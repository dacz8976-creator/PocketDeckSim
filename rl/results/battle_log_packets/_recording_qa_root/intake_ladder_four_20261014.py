"""Bind and claim only the four owner-requested October 14 ladder uploads."""
import csv
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from hydrate_competitive_source import hydrate

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_NEW_LADDER_FOUR'
PROBE = Path('C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe')
SELECTED = ['20261014_142546000_iOS.MP4', '20261014_143111000_iOS.MP4',
            '20261014_144627000_iOS.MP4', '20261014_145449000_iOS.MP4']

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

BATCH.mkdir(exist_ok=True)
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
if not (BATCH / 'INDEX_BEFORE.json').exists():
    save(BATCH / 'INDEX_BEFORE.json', rows)
save(BATCH / 'OWNER_CONTEXT.json', {
    'requested_utc': datetime.now(timezone.utc).isoformat(), 'selected_sources': SELECTED,
    'scope': 'Four new ladder uploads only. Full source review, separate source checks, lead acceptance, existing Ladder Log save and readback, archive and OneDrive storage.',
    'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1',
    'season': 'Keep previous games as history; October 14 games identifiable by saved match date and time.',
    'note_contract': 'First or second | main attacker and first attack own turn (T1 is first own turn) | opponent points at that attack. Include source filename and outcome evidence in available record fields.',
    'deck_routing': 'brew 07, brew 08, deck 12, deck 13 exist. draft A and draft D use Add a deck not listed.',
    'auto_rule': 'Any visible Auto option even OFF means computer; exclude both external human logs.',
    'shared_writes': 'Root only: index/events, artifact, moves, media map and Boss mirror.'})
sources = []
parser = argparse.ArgumentParser()
parser.add_argument('--video', choices=SELECTED)
args = parser.parse_args()
for name in ([args.video] if args.video else SELECTED):
    path = ROOT / name
    before = path.stat()
    assert not (ROOT / 'Reviewed' / name).exists(), name
    p = BATCH / path.stem
    if (p / 'SOURCE.json').exists():
        bound = json.loads((p / 'SOURCE.json').read_text(encoding='utf-8-sig'))
        assert before.st_size == bound['bytes']
        sources.append(bound)
        continue
    prior = next((r for r in rows if r['Video'] == name), None)
    assert prior is None, prior
    p.mkdir(exist_ok=True)
    print('Ensuring complete local source: ' + name, flush=True)
    try:
        hydrate(path)
    except Exception as error:
        save(p / ('HYDRATION_ERROR.' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '.json'), {'utc': datetime.now(timezone.utc).isoformat(), 'error': str(error), 'contents_modified': False})
        raise
    save(p / 'HYDRATION.json', {'result': 'S_OK', 'utc': datetime.now(timezone.utc).isoformat(), 'contents_modified': False})
    probe_result = subprocess.run([str(PROBE), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True)
    if probe_result.returncode:
        save(p / 'PROBE_ERROR.json', {'exit_code': probe_result.returncode, 'stderr': probe_result.stderr})
        raise RuntimeError(probe_result.stderr)
    probe = json.loads(probe_result.stdout)
    save(p / 'PROBE.json', probe)
    worker = '/root/ladder_' + name[9:15]
    result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record', '--video', name,
        '--reviewer', worker, '--status', 'in_progress', '--scope', 'Whole new ladder recording: setup, every turn, terminal result; first/second, first main-attacker attack own turn and opponent points.',
        '--notes', 'Owner explicitly requested October 14 new ladder batch. No older backlog included. Root is sole shared writer.'], capture_output=True, text=True, encoding='utf-8')
    save(p / 'ASSIGNMENT_REGISTRATION.json', {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    assert result.returncode == 0, result.stderr
    event = json.loads(Path(result.stdout.strip()).read_text(encoding='utf-8-sig'))
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    binding = {'video_basename': name, 'sha256': event['video_sha256'], 'bytes': after.st_size,
        'duration_seconds': float(probe['format']['duration']), 'streams': probe['streams'],
        'source_path_at_review': str(path), 'bound_utc': event['logged_at_utc'],
        'identity_provenance': event['identity_provenance'], 'recording_relationships': [],
        'source_creation_utc': probe['format'].get('tags', {}).get('creation_time'), 'packet': str(p)}
    save(p / 'SOURCE.json', binding)
    save(p / 'ASSIGNMENT.json', {'reviewer': worker, 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
        'source_sha256': binding['sha256'], 'assignment_event': event['event_id'],
        'scope': 'Entire recording; ordinary ladder full review. No Pause Games supplement.',
        'shared_write_authority': False, 'external_write_authority': False})
    sources.append(binding)
    print(json.dumps({k:binding[k] for k in ['video_basename','sha256','bytes','duration_seconds','source_creation_utc','packet']}), flush=True)
save(BATCH / 'SOURCE_INVENTORY.json', [json.loads((BATCH / Path(name).stem / 'SOURCE.json').read_text(encoding='utf-8-sig')) for name in SELECTED if (BATCH / Path(name).stem / 'SOURCE.json').exists()])
