"""One ordinary read of a missing source range; no file writes or review claims."""
import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--child', action='store_true')
parser.add_argument('--offset', type=int)
parser.add_argument('--video', choices=['20261013_022530000_iOS.MP4', '20261013_030351000_iOS.MP4'], default='20261013_022530000_iOS.MP4')
args = parser.parse_args()
path = ROOT / args.video
if args.child:
    assert args.offset is not None and 0 <= args.offset < path.stat().st_size
    with path.open('rb') as stream:
        stream.seek(args.offset)
        data = stream.read(min(1024 * 1024, path.stat().st_size - args.offset))
        print('Read bytes: ' + str(len(data)), flush=True)
else:
    spec = importlib.util.spec_from_file_location('range_meta', ROOT / 'Recording_QA/BATCH_2026-10-12_ADDITIONAL_TWO/check_download_ranges.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    before = mod.ranges(path)
    if not before['missing_ranges']:
        print('Source is fully available.')
        sys.exit(0)
    offset = before['missing_ranges'][0]['offset']
    record = {'created_utc': datetime.now(timezone.utc).isoformat(), 'source': path.name,
              'operation': 'One normal read of at most 1 MiB at the first missing offset',
              'requested_offset': offset, 'source_contents_modified': False, 'before': before}
    try:
        result = subprocess.run([sys.executable, '-X', 'utf8', __file__, '--child', '--video', path.name, '--offset', str(offset)], capture_output=True, text=True, timeout=180)
        record.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired:
        record.update(exit_code=None, timeout_seconds=180, note='Only the task-owned read probe was stopped.')
    record['after'] = mod.ranges(path)
    out = BATCH / path.stem / 'source_access_history' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.read_probe.json')
    out.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record), flush=True)
