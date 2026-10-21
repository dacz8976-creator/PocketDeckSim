"""Resume-safe source binding for one of the four explicit night uploads."""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_FINAL_LADDER_TWO'
NAMES = ['20261016_030833000_iOS.MP4', '20261016_031512000_iOS.MP4']
PROBE = 'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe'

def save(path, data):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

parser = argparse.ArgumentParser()
parser.add_argument('video', choices=NAMES)
args = parser.parse_args()
name = args.video
assert json.loads((BATCH / 'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources'] == NAMES
packet = BATCH / Path(name).stem
packet.mkdir(exist_ok=True)
assert not (packet / 'SOURCE.json').exists(), 'Already bound; use existing assignment'
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
assert not any(row['Video'] == name for row in rows), 'Prior shared review record must be reconciled'
assert not (ROOT / 'Reviewed' / name).exists()
path = ROOT / name
before = path.stat()
meta = metadata(path)
assert meta['allocated_bytes'] == before.st_size and not meta['online_only'], meta
save(packet / 'LOCAL_METADATA.json', meta)
probe = subprocess.run([PROBE, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, timeout=30, check=True)
data = json.loads(probe.stdout)
save(packet / 'PROBE.json', data)
reviewer = '/root/ladder_' + name[9:15]
result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record', '--video', name,
    '--reviewer', reviewer, '--status', 'in_progress', '--scope', 'Entire new night ladder recording: setup, every turn and terminal result.',
    '--notes', 'Owner requested these four exact sources with upload-progress screenshot. Root sole shared writer; no older backlog.'], capture_output=True, text=True, encoding='utf-8', timeout=60)
save(packet / 'ASSIGNMENT_REGISTRATION.json', {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
assert result.returncode == 0, result.stderr
event = json.loads(Path(result.stdout.strip()).read_text(encoding='utf-8-sig'))
after = path.stat()
assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
source = {'video_basename': name, 'sha256': event['video_sha256'], 'bytes': after.st_size,
    'duration_seconds': float(data['format']['duration']), 'streams': data['streams'], 'source_path_at_review': str(path),
    'bound_utc': event['logged_at_utc'], 'identity_provenance': event['identity_provenance'], 'recording_relationships': [],
    'source_creation_utc': data['format'].get('tags', {}).get('creation_time'), 'packet': str(packet)}
save(packet / 'SOURCE.json', source)
save(packet / 'ASSIGNMENT.json', {'reviewer': reviewer, 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
    'source_sha256': source['sha256'], 'assignment_event': event['event_id'], 'scope': 'Full source; ordinary ladder protocol, no PauseGames supplement.',
    'shared_write_authority': False, 'external_write_authority': False})
print(json.dumps({key: source[key] for key in ['video_basename', 'sha256', 'bytes', 'duration_seconds', 'source_creation_utc', 'packet']}), flush=True)
