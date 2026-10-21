"""Source intake for the owner's eleven September 30 evening Auto AI uploads."""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-09-30_EVENING'
PROBE = Path(r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video')
    args = parser.parse_args()
    BATCH.mkdir(exist_ok=True)
    snapshot = BATCH / 'INDEX_BEFORE.json'
    if not snapshot.exists():
        rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
        snapshot.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    manifest_path = BATCH / 'INTAKE.json'
    manifest = read(manifest_path) if manifest_path.exists() else {
        'expected_recordings': 11,
        'owner_instruction': 'Just uploaded 11 new videos for review. Not ladder log games, just auto ai games. Same process as before.',
        'recording_date_note': 'Source names use 20261001; upload and owner request occur September 30 America/Chicago. Source filename clock basis is unverified.',
        'ladder_eligible': False,
        'sources': [],
    }
    known = {item['video']: item for item in manifest['sources']}
    baseline_names = {item['Video'] for item in read(snapshot)}
    videos = sorted(p for p in ROOT.glob('*.MP4') if p.name.startswith(('20260930_', '20261001_')) and p.name not in baseline_names)
    for video in videos:
        known.setdefault(video.name, {'video': video.name, 'bytes': video.stat().st_size, 'status': 'awaiting_source_intake', 'ladder_eligible': False})
    if args.video:
        if Path(args.video).name != args.video or args.video not in known:
            raise SystemExit('Exact discovered evening source basename required')
        video = ROOT / args.video
        before = video.stat()
        probe = json.loads(subprocess.check_output([str(PROBE), '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'json', str(video)], timeout=45))
        reviewer = 'sol_auto_evening_' + video.stem.split('_')[1]
        events = [read(p) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
        prior = sorted((e for e in events if e.get('video_basename') == video.name), key=lambda e: e['logged_at_utc'])
        if prior:
            event = prior[-1]
            if event['status'] != 'in_progress' or event['reviewer'] != reviewer:
                raise RuntimeError(f'Existing unrelated assignment: {video.name}')
        else:
            command = [sys.executable, str(ROOT / 'Review_Log' / 'review_log.py'), '--root', str(ROOT), 'record', '--video', video.name, '--reviewer', reviewer, '--status', 'in_progress', '--scope', 'Full owner-requested Auto AI battle review, setup through terminal result', '--notes', 'Owner identified eleven evening uploads as Auto AI games. Excluded from Ladder Log. Lead alone finalizes and moves originals.']
            subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            events = [read(p) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
            event = sorted((e for e in events if e.get('video_basename') == video.name), key=lambda e: e['logged_at_utc'])[-1]
        after = video.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f'Source changed during intake: {video.name}')
        packet = ROOT / 'Recording_QA' / (video.stem + '_auto_sol')
        packet.mkdir(exist_ok=True)
        source = {'video_basename': video.name, 'sha256': event['video_sha256'], 'bytes': before.st_size, 'duration_seconds': float(probe['format']['duration']), 'streams': probe['streams'], 'source_path_at_review': str(video), 'recording_relationships': [], 'recording_date_basis': manifest['recording_date_note'], 'owner_testimony': manifest['owner_instruction'], 'mode': 'autopilot_vs_computer', 'ladder_eligible': False, 'ladder_action': 'excluded_by_owner_instruction; no Ladder Log write', 'reviewer': reviewer, 'review_model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'identity_verified_event_id': event['event_id'], 'intake_utc': datetime.now(timezone.utc).isoformat()}
        copy_receipt = BATCH / ('SOURCE_COPY.' + video.name + '.json')
        if copy_receipt.exists():
            copied = read(copy_receipt)
            if copied['staged_copy_sha256'] != source['sha256'] or copied['bytes'] != source['bytes']:
                raise RuntimeError('Staged copy disagrees with review-source identity')
            source['recording_relationships'] = [{'type': 'unchanged_review_copy', 'original_path': copied['original_path'], 'source_copy_receipt': str(copy_receipt), 'original_preserved': True, 'independent_gameplay_observations': 1}]
        (packet / 'SOURCE.json').write_text(json.dumps(source, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        known[video.name] = {'video': video.name, 'packet': str(packet), 'reviewer': reviewer, 'duration_seconds': source['duration_seconds'], 'bytes': source['bytes'], 'sha256': source['sha256'], 'status': 'assigned_full_review', 'ladder_eligible': False}
        print(json.dumps(known[video.name]), flush=True)
    manifest['sources'] = [known[name] for name in sorted(known)]
    manifest['discovered_recordings'] = len(known)
    manifest['updated_utc'] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if not args.video:
        print(json.dumps({'discovered': len(known), 'expected': manifest['expected_recordings'], 'sources': manifest['sources']}))

if __name__ == '__main__':
    main()
