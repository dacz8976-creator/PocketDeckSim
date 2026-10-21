"""Bound and register the owner-requested October 1 rules recordings."""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-10-01_RULES'
VIDEOS = ['20261001_203626000_iOS.MP4', '20261001_204634000_iOS.MP4', '20261001_205658000_iOS.MP4', '20261001_210403000_iOS.MP4', '20261001_213034000_iOS.MP4', '20261001_213822000_iOS.MP4', '20261001_214736000_iOS.MP4']
PROBE = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe'
OWNER = 'Can we process the newly uploaded videos? All not ladders and rules testing'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', choices=VIDEOS)
    args = parser.parse_args()
    BATCH.mkdir(exist_ok=True)
    snapshot = BATCH / 'INDEX_BEFORE.json'
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    if not snapshot.exists():
        save(snapshot, rows)
    baseline = {row['Video'] for row in read(snapshot)}
    assert not baseline.intersection(VIDEOS), 'Requested source already indexed before this batch'
    manifest_path = BATCH / 'INTAKE.json'
    manifest = read(manifest_path) if manifest_path.exists() else {'owner_instruction': OWNER, 'ladder_eligible': False, 'expected_recordings': len(VIDEOS), 'sources': []}
    manifest['expected_recordings'] = len(VIDEOS)
    known = {item['video']: item for item in manifest['sources']}
    for name in VIDEOS:
        packet = ROOT / 'Recording_QA' / (Path(name).stem + '_rule_sol')
        if name not in known and (packet / 'SOURCE.json').exists():
            source = read(packet / 'SOURCE.json')
            known[name] = {'video': name, 'packet': str(packet), 'reviewer': source['reviewer'], 'sha256': source['sha256'], 'bytes': source['bytes'], 'duration_seconds': source['duration_seconds']}
    manifest['sources'] = list(known.values())
    save(manifest_path, manifest)
    for name in ([args.video] if args.video else VIDEOS):
        video = ROOT / name
        before = video.stat()
        probe = json.loads(subprocess.check_output([PROBE, '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'json', str(video)], timeout=300))
        reviewer = 'sol_rules_20261001_' + video.stem.split('_')[1]
        events = [read(path) for path in (ROOT / 'Review_Log' / 'events').glob('*.json')]
        prior = sorted((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])
        if prior:
            event = prior[-1]
            assert event['status'] == 'in_progress' and event['reviewer'] == reviewer, 'Existing different assignment'
        else:
            command = [sys.executable, str(ROOT / 'Review_Log' / 'review_log.py'), '--root', str(ROOT), 'record', '--video', name, '--reviewer', reviewer, '--status', 'in_progress', '--scope', 'Entire owner-requested rules-testing recording, including every supplied match and consequential interaction', '--notes', OWNER + '. Excluded from Ladder Log. Lead alone accepts, registers completion and moves originals.']
            subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            events = [read(path) for path in (ROOT / 'Review_Log' / 'events').glob('*.json')]
            event = sorted((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])[-1]
        after = video.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Source changed during intake'
        packet = ROOT / 'Recording_QA' / (video.stem + '_rule_sol')
        packet.mkdir(exist_ok=True)
        source = {'video_basename': name, 'sha256': event['video_sha256'], 'bytes': before.st_size, 'duration_seconds': float(probe['format']['duration']), 'streams': probe['streams'], 'source_path_at_review': str(video), 'recording_relationships': [], 'recording_date_basis': 'Filename 20261001; exact clock and timezone basis unverified', 'owner_testimony': OWNER, 'recording_intent': 'rules_testing', 'mode': 'verify_from_footage', 'ladder_eligible': False, 'reviewer': reviewer, 'review_model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'identity_verified_event_id': event['event_id'], 'intake_utc': datetime.now(timezone.utc).isoformat()}
        source_path = packet / 'SOURCE.json'
        if source_path.exists():
            old = read(source_path)
            assert old['sha256'] == source['sha256'] and old['bytes'] == source['bytes']
        else:
            save(source_path, source)
        manifest['sources'] = [item for item in manifest['sources'] if item['video'] != name]
        manifest['sources'].append({'video': name, 'packet': str(packet), 'reviewer': reviewer, 'sha256': source['sha256'], 'bytes': source['bytes'], 'duration_seconds': source['duration_seconds']})
        save(manifest_path, manifest)
        print(json.dumps(manifest['sources'][-1]), flush=True)
    save(manifest_path, manifest)

if __name__ == '__main__':
    main()
