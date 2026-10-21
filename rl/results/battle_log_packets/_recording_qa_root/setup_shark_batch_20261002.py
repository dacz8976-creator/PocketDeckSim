"""Bind and assign only the five requested Shark Tempo recordings."""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from intake_competitive_20261002 import ROOT, PROBE, FFMPEG, DESTINATION, read, save

BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-10-02_SHARK_TEMPO'
SELECTED = ['20261002_114458000_iOS.MP4', '20261002_115323000_iOS.MP4', '20261002_132311000_iOS.MP4', '20261002_143309000_iOS.MP4', '20261002_143837000_iOS.MP4']
DECK = 'Draft A: Shark Tempo'
FEEDBACK = 'It was fun and competitive. Could maybe combine with Wailord or the Soothing Shore Stadium.'

def packet_for(name):
    return ROOT / 'Recording_QA' / (Path(name).stem + '_shark_sol')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', choices=SELECTED)
    args = parser.parse_args()
    BATCH.mkdir(exist_ok=True)
    baseline = BATCH / 'INDEX_BEFORE.json'
    if not baseline.exists():
        save(baseline, list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
    context = BATCH / 'OWNER_CONTEXT.json'
    if not context.exists():
        save(context, {'requested_destination': DESTINATION, 'deck': DECK, 'source_filenames': SELECTED, 'owner_feedback': FEEDBACK, 'numeric_ratings': None, 'proposals_tested': False, 'ranked_ladder_eligible': False, 'date_local': '2026-10-02'})
    for name in [args.video] if args.video else SELECTED:
        video = ROOT / name
        packet = packet_for(name)
        packet.mkdir(exist_ok=True)
        source = packet / 'SOURCE.json'
        if not source.exists():
            assert video.is_file() and not (ROOT / 'Reviewed' / name).exists()
            subprocess.run(['attrib', '+P', '-U', str(video)], check=True, capture_output=True)
            before = video.stat()
            print('Binding ' + name, flush=True)
            digest = hashlib.sha256()
            with video.open('rb') as handle:
                while chunk := handle.read(8 * 1024 * 1024):
                    digest.update(chunk)
            probe = json.loads(subprocess.check_output([PROBE, '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'json', str(video)], timeout=300))
            after = video.stat()
            assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Upload changed during intake'
            save(source, {'video_basename': name, 'sha256': digest.hexdigest(), 'bytes': before.st_size, 'duration_seconds': float(probe['format']['duration']), 'streams': probe['streams'], 'source_path_at_review': str(video), 'recording_relationships': [], 'requested_log': DESTINATION, 'owner_deck': DECK, 'owner_testimony': 'Five new games with the deck labelled Draft A: Shark Tempo in Pause Games.', 'match_date_local': '2026-10-02', 'recording_date_basis': 'October 2 filename and new local upload date; exact filename timezone unverified', 'intake_utc': datetime.now(timezone.utc).isoformat()})
        binding = read(source)
        reviewer = 'sol_shark_20261002_' + name.split('_')[1]
        events = [read(p) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
        prior = sorted((e for e in events if e.get('video_basename', e.get('video')) == name), key=lambda e: e.get('logged_at_utc', e.get('timestamp_utc')))
        if not prior:
            subprocess.run([sys.executable, str(ROOT / 'Review_Log' / 'review_log.py'), '--root', str(ROOT), 'record', '--video', name, '--reviewer', reviewer, '--status', 'in_progress', '--scope', 'Entire owner-requested Shark Tempo battle: setup, every supplied turn and terminal outcome', '--evidence', str(source), '--notes', 'Owner requests Draft A: Shark Tempo in Pause Games. Fun and competitive is owner testimony; Wailord/Soothing Shore are proposed ideas, not already-tested variants. Ranked Ladder Log excluded.'], check=True, capture_output=True)
            events = [read(p) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
            prior = sorted((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])
        event = prior[-1]
        assert event['status'] == 'in_progress' and event['reviewer'] == reviewer
        assert event['video_sha256'] == binding['sha256'] and event['video_bytes'] == binding['bytes']
        assignment = packet / 'ASSIGNMENT.json'
        if not assignment.exists():
            save(assignment, {'video_basename': name, 'source_sha256': binding['sha256'], 'reviewer': reviewer, 'review_model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'requested_log': DESTINATION, 'owner_deck': DECK, 'ranked_ladder_eligible': False, 'match_date_local': '2026-10-02', 'identity_verified_event_id': event['event_id'], 'assigned_utc': datetime.now(timezone.utc).isoformat(), 'owner_feedback': FEEDBACK})
        print(json.dumps({'video': name, 'packet': str(packet), 'sha256': binding['sha256'], 'duration': binding['duration_seconds'], 'bytes': binding['bytes']}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
