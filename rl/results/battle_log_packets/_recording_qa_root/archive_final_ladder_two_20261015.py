"""Collision-safe archive of one accepted new October 15 source, with receipts."""
import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_FINAL_LADDER_TWO'
NAMES = ['20261016_030833000_iOS.MP4', '20261016_031512000_iOS.MP4']

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('video', choices=NAMES)
args = parser.parse_args()
packet = BATCH / Path(args.video).stem
source = (ROOT / args.video).resolve()
destination = (ROOT / 'Reviewed' / args.video).resolve()
assert source.parent == ROOT.resolve() and destination.parent == (ROOT / 'Reviewed').resolve()
assert source.is_file() and not destination.exists()
binding = load(packet / 'SOURCE.json')
acceptance = load(packet / 'LEAD_ACCEPTANCE.json')
registration = load(packet / 'REGISTRATION_RESULT.json')
assert acceptance['accepted'] and acceptance['archive_eligible'] and acceptance['all_source_games_accepted']
assert registration['exit_code'] == 0
before = digest(source)
assert before == binding['sha256'] and source.stat().st_size == binding['bytes']
events = [load(path) for path in (ROOT / 'Review_Log/events').glob('*.json')]
latest = max((event for event in events if event.get('video_basename') == args.video), key=lambda event: event['logged_at_utc'])
assert latest['status'] == 'full_battle_review_complete' and latest['video_sha256'] == before
lock = ROOT / 'Review_Log/.write.lock'
lock.mkdir()
owner = lock / 'owner.json'
try:
    save(owner, {'pid': os.getpid(), 'purpose': 'Accepted October 15 source archive'})
    index_path = ROOT / 'BATTLE_REVIEW_INDEX.csv'
    with index_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    matching = [row for row in rows if row['Video'] == args.video]
    assert len(matching) == 1 and matching[0]['Status'] == 'Reviewed'
    map_path = ROOT / 'MEDIA_LOCATIONS.json'
    mapping = load(map_path)
    assert not any(entry['filename'] == args.video for entry in mapping['moved'])
    os.rename(source, destination)
    after = digest(destination)
    assert before == after and destination.stat().st_size == binding['bytes']
    now = datetime.now(timezone.utc).isoformat()
    receipt_path = packet / ('MOVE_RECEIPT.' + args.video + '.json')
    receipt = {'schema': 'battle-media-move-receipt/v1', 'filename': args.video, 'from': str(source), 'to': str(destination),
        'bytes': binding['bytes'], 'sha256_before': before, 'sha256_after': after, 'identity_match': True, 'moved_utc': now,
        'review_event_id': latest['event_id'], 'review_status': latest['status'], 'evidence_packet': str(packet)}
    save(receipt_path, receipt)
    matching[0]['Location'] = 'Reviewed/' + args.video
    with index_path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    mapping['moved'].append({'filename': args.video, 'old_path': str(source), 'current_path': str(destination),
        'bytes': binding['bytes'], 'sha256': after, 'review_evidence': [str(packet / name) for name in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json']],
        'location_history': [{'from': str(source), 'to': str(destination), 'utc': now, 'reason': 'Complete source review independently and lead accepted', 'receipt': str(receipt_path)}],
        'review_status': 'Reviewed'})
    mapping['index_video_count'] = len(rows)
    mapping['awaiting_review_or_confirmation'] = sum(row['Status'] != 'Reviewed' for row in rows)
    mapping['updated_utc'] = now
    map_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n', encoding='utf-8-sig')
    print(json.dumps({'archived': args.video, 'verified_sha256': after, 'bytes': binding['bytes']}))
finally:
    if owner.exists():
        owner.chmod(0o666)
        owner.unlink()
    if not list(lock.iterdir()):
        lock.chmod(0o777)
        lock.rmdir()
