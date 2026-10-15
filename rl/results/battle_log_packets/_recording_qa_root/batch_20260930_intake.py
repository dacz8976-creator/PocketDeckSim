import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBE = Path(r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe')
BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-09-30'
BATCH.mkdir(exist_ok=True)
rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
snapshot = BATCH / 'INDEX_BEFORE.json'
if not snapshot.exists():
    snapshot.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
manifest_path = BATCH / 'INTAKE.json'
existing_manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig')) if manifest_path.exists() else {'sources': []}
known = {item['video']: item for item in existing_manifest['sources']}
entries = list(known.values())
for video in sorted(ROOT.glob('20260930_*.MP4')):
    if known.get(video.name, {}).get('sha256'):
        continue
    before = video.stat()
    if before.st_file_attributes & (0x400000 | 0x1000):
        item = {'video': video.name, 'bytes': before.st_size, 'sha256': None, 'status': 'pending_local_download', 'file_attributes': before.st_file_attributes, 'ladder_eligible': False}
        known[video.name] = item
        print(json.dumps(item), flush=True)
        continue
    try:
        probe = json.loads(subprocess.check_output([str(PROBE), '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'json', str(video)], timeout=45))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        item = {'video': video.name, 'bytes': before.st_size, 'sha256': None, 'status': 'pending_readable_source', 'error': str(error), 'ladder_eligible': False}
        known[video.name] = item
        print(json.dumps(item), flush=True)
        continue
    reviewer = 'sol_auto_' + video.stem.split('_')[1]
    command = [sys.executable, str(ROOT / 'Review_Log' / 'review_log.py'), '--root', str(ROOT), 'record', '--video', video.name, '--reviewer', reviewer, '--status', 'in_progress', '--scope', 'Full September 30 autopilot computer battle review, setup through terminal result', '--notes', 'Owner explicitly identified all September 30 uploads as autopilot battles against the computer. Excluded from Ladder Log. Lead alone finalizes and moves source.']
    events = [json.loads(p.read_text(encoding='utf-8')) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
    prior = sorted((e for e in events if e.get('video_basename') == video.name), key=lambda e: e['logged_at_utc'])
    if prior:
        if prior[-1]['status'] != 'in_progress' or prior[-1]['reviewer'] != reviewer:
            raise RuntimeError(f'Existing unrelated assignment: {video.name}')
        event = prior[-1]
    else:
        subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
        events = [json.loads(p.read_text(encoding='utf-8')) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
        event = sorted((e for e in events if e.get('video_basename') == video.name), key=lambda e: e['logged_at_utc'])[-1]
    after = video.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f'Source changed: {video.name}')
    packet = ROOT / 'Recording_QA' / (video.stem + '_auto_sol')
    packet.mkdir(exist_ok=True)
    source = {'video_basename': video.name, 'sha256': event['video_sha256'], 'bytes': before.st_size, 'duration_seconds': float(probe['format']['duration']), 'streams': probe['streams'], 'source_path_at_review': str(video), 'recording_relationships': [], 'recording_date_basis': '20260930 source filename and owner testimony; no independent clock verification', 'owner_testimony': 'All new September 30 uploads were autopilot battles against the computer.', 'mode': 'autopilot_vs_computer', 'ladder_eligible': False, 'ladder_action': 'excluded_by_owner_instruction; no Ladder Log write', 'reviewer': reviewer, 'review_model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'identity_verified_event_id': event['event_id'], 'intake_utc': datetime.now(timezone.utc).isoformat()}
    (packet / 'SOURCE.json').write_text(json.dumps(source, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    item = {'video': video.name, 'packet': str(packet), 'reviewer': reviewer, 'duration_seconds': source['duration_seconds'], 'bytes': source['bytes'], 'sha256': source['sha256'], 'ladder_eligible': False}
    known[video.name] = item
    print(json.dumps(item), flush=True)
entries = [known[name] for name in sorted(known)]
manifest_path.write_text(json.dumps({'owner_instruction': 'Review today\'s uploads with separate Sol agents, consult Astra only for difficult or unclear parts; autopilot computer battles, never Ladder Log.', 'sources': entries}, indent=2) + '\n', encoding='utf-8')
