"""Bind and claim the two new owner-requested October 15 ladder sources."""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_LADDER_TWO'
SELECTED = ['20261015_201201000_iOS.MP4', '20261015_201850000_iOS.MP4']
PROBE = Path('C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe')

def save(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

BATCH.mkdir(exist_ok=True)
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
save(BATCH / 'INDEX_BEFORE.json', rows)
save(BATCH / 'OWNER_CONTEXT.json', {
    'requested_utc': datetime.now(timezone.utc).isoformat(), 'selected_sources': SELECTED,
    'scope': 'Two newly downloaded ladder recordings only. Full review, independent check, lead acceptance, live save/readback, archive and storage verification.',
    'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1',
    'auto_rule': 'Any visible Auto option, including OFF, identifies computer play and excludes external human logs.',
    'shared_writer': '/root', 'pause_games_supplement': False})
inventory = []
for name in SELECTED:
    path = ROOT / name
    before = path.stat()
    assert not any(r['Video'] == name for r in rows), name
    assert not (ROOT / 'Reviewed' / name).exists(), name
    packet = BATCH / path.stem
    packet.mkdir(exist_ok=True)
    meta = metadata(path)
    save(packet / 'LOCAL_METADATA.json', meta)
    assert meta['allocated_bytes'] == before.st_size and not meta['online_only'], meta
    probe = subprocess.run([str(PROBE), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, timeout=25, check=True)
    data = json.loads(probe.stdout)
    save(packet / 'PROBE.json', data)
    worker = '/root/ladder_' + name[9:15]
    result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record', '--video', name,
        '--reviewer', worker, '--status', 'in_progress', '--scope', 'Entire new ladder recording: setup, every turn and terminal result.',
        '--notes', 'Owner requested these two new sources on October 15. No older backlog. Root is sole shared writer.'], capture_output=True, text=True, encoding='utf-8', timeout=60)
    save(packet / 'ASSIGNMENT_REGISTRATION.json', {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    assert result.returncode == 0, result.stderr
    event = json.loads(Path(result.stdout.strip()).read_text(encoding='utf-8-sig'))
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    source = {'video_basename': name, 'sha256': event['video_sha256'], 'bytes': after.st_size,
        'duration_seconds': float(data['format']['duration']), 'streams': data['streams'],
        'source_path_at_review': str(path), 'bound_utc': event['logged_at_utc'],
        'identity_provenance': event['identity_provenance'], 'recording_relationships': [],
        'source_creation_utc': data['format'].get('tags', {}).get('creation_time'), 'packet': str(packet)}
    save(packet / 'SOURCE.json', source)
    save(packet / 'ASSIGNMENT.json', {'reviewer': worker, 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
        'source_sha256': source['sha256'], 'assignment_event': event['event_id'], 'scope': 'Full battle; ordinary ladder protocol.',
        'shared_write_authority': False, 'external_write_authority': False})
    inventory.append(source)
    print(json.dumps({k: source[k] for k in ['video_basename','sha256','bytes','duration_seconds','source_creation_utc','packet']}), flush=True)
save(BATCH / 'SOURCE_INVENTORY.json', inventory)
