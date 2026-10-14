"""Intake only the owner's October 4-6 uploads. Lead is the shared writer."""
import argparse
import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES'
PROBE = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe'

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def initialize():
    BATCH.mkdir(exist_ok=True)
    selected = sorted(p.name for p in ROOT.glob('2026100[456]_*.MP4'))
    context = BATCH / 'OWNER_CONTEXT.json'
    if not context.exists():
        save(context, {'requested_utc': datetime.now(timezone.utc).isoformat(), 'selected_sources': selected,
            'owner_request': 'New uploads are believed to be Pause Games; first use of a deck may show its QR. Sol agents with Astra for difficult or unclear spots.',
            'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
            'protocol': str(ROOT / 'PAUSE_GAMES_REVIEW_PROTOCOL.md'),
            'scope': 'Only these new uploads. Full source coverage, independent acceptance, external logging when human and outcome established, safe archive.',
            'classification_rule': 'Visible Auto option even OFF means computer, excluded from both external human logs.',
            'lead_only_shared_writes': True})
        save(BATCH / 'INDEX_BEFORE.json', list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
    return json.loads(context.read_text(encoding='utf-8'))['selected_sources']

def intake(name):
    packet = BATCH / Path(name).stem
    packet.mkdir(exist_ok=True)
    binding = packet / 'SOURCE.json'
    if binding.exists():
        print(name + ': already bound', flush=True)
        return
    video = ROOT / name
    assert video.is_file() and not (ROOT / 'Reviewed' / name).exists()
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    assert not any(r['Video'] == name for r in rows), 'Existing assignment: coordinate before intake'
    subprocess.run(['attrib', '+P', '-U', str(video)], check=True, capture_output=True)
    before = video.stat()
    reviewer = '/root/pause_' + Path(name).stem
    print('Binding ' + name, flush=True)
    result = subprocess.run([sys.executable, str(ROOT / 'Review_Log/review_log.py'), '--root', str(ROOT), 'record',
        '--video', name, '--reviewer', reviewer, '--status', 'in_progress',
        '--scope', 'Whole newly uploaded Pause Games recording: setup, all turns, ending, hand capture and deck QR where shown',
        '--evidence', str(BATCH / 'OWNER_CONTEXT.json'), '--notes', 'Owner requested this new upload. Sol first pass and independent checks; Astra targeted ambiguity. Root is sole shared writer.'], capture_output=True, text=True)
    if result.returncode:
        history=packet/'source_access_history'
        history.mkdir(exist_ok=True)
        receipt={'source': name, 'attempt_utc': datetime.now(timezone.utc).isoformat(), 'exit_code': result.returncode, 'stderr': result.stderr, 'stdout': result.stdout}
        save(history/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'),receipt)
        save(packet / 'SOURCE_ACCESS_WAIT.json', receipt)
        print(name + ': source access incomplete: ' + result.stderr[-400:], flush=True)
        return
    events = [json.loads(p.read_text(encoding='utf-8-sig')) for p in (ROOT / 'Review_Log/events').glob('*.json')]
    event = max((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])
    probe = json.loads(subprocess.check_output([PROBE, '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name,start_time', '-of', 'json', str(video)], timeout=300))
    after = video.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Upload changed during intake'
    save(binding, {'video_basename': name, 'sha256': event['video_sha256'], 'bytes': event['video_bytes'], 'duration_seconds': float(probe['format']['duration']),
        'streams': probe['streams'], 'source_path_at_review': str(video), 'recording_relationships': [],
        'source_identity_basis': 'CLI SHA-256 and stable size/mtime during intake', 'identity_verified_event_id': event['event_id'],
        'intake_utc': datetime.now(timezone.utc).isoformat(), 'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
        'classification': 'awaiting_visual_verification', 'match_date_from_filename': name[:8], 'filename_clock_timezone': None})
    for template in (ROOT / 'Review_Log/templates/pause_games').glob('*.template.json'):
        target = packet / template.name.replace('.template', '')
        if not target.exists():
            shutil.copy2(template, target)
    shutil.copy2(ROOT / 'Review_Log/templates/pause_games/ASSIGNMENT.md', packet / 'ASSIGNMENT.md')
    save(packet / 'ASSIGNMENT.json', {'reviewer': reviewer, 'review_model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'assigned_utc': datetime.now(timezone.utc).isoformat(),
        'video_basename': name, 'source_sha256': event['video_sha256'], 'packet': str(packet), 'protocol': str(ROOT / 'PAUSE_GAMES_REVIEW_PROTOCOL.md'),
        'scope': 'Whole supplied source and all games/related segments. Mandatory future Pause Games supplement.', 'lead_only_shared_writes': True,
        'deck_snapshot': str(BATCH / 'LIVE_DECK_SNAPSHOT.json'), 'deck_snapshot_status': 'Lead retrieving live list; report QR sightings immediately.'})
    print(json.dumps({'source': name, 'duration_seconds': float(probe['format']['duration']), 'packet': str(packet), 'registered': True}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--video')
    parser.add_argument('--initialize-only', action='store_true')
    args = parser.parse_args()
    selected = initialize()
    if not args.initialize_only:
        for name in ([args.video] if args.video else selected):
            assert name in selected
            intake(name)
