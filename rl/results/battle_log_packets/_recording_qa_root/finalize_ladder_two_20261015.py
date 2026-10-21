"""Reconcile accepted October 15 reviews, live readback, archive and storage."""
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_LADDER_TWO'
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / BATCH.name
NAMES = ['20261015_201201000_iOS.MP4', '20261015_201850000_iOS.MP4']

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def digest(path):
    assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv']
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--mirror', action='store_true')
args = parser.parse_args()
if args.mirror:
    assert load(BATCH / 'BATCH_STATUS.json')['review_and_ladder_logging_complete']
    BOSS.mkdir(parents=True, exist_ok=True)
    copied = []
    for path in sorted(BATCH.rglob('*')):
        if not path.is_file() or path.name == 'MIRROR_RECEIPT.json':
            continue
        assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv']
        rel = path.relative_to(BATCH)
        target = BOSS / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        sha = digest(path)
        if target.exists():
            assert digest(target) == sha, target
        else:
            shutil.copy2(path, target)
        assert digest(target) == sha
        copied.append({'path': rel.as_posix(), 'sha256': sha, 'bytes': path.stat().st_size})
    receipt = {'source': str(BATCH), 'destination': str(BOSS), 'created_utc': datetime.now(timezone.utc).isoformat(),
        'all_hashes_verified': True, 'videos_copied': 0, 'file_count': len(copied), 'files': copied}
    save(BATCH / 'MIRROR_RECEIPT.json', receipt)
    shutil.copy2(BATCH / 'MIRROR_RECEIPT.json', BOSS / 'MIRROR_RECEIPT.json')
    assert digest(BATCH / 'MIRROR_RECEIPT.json') == digest(BOSS / 'MIRROR_RECEIPT.json')
    print(json.dumps({'mirrored_files': len(copied), 'all_hashes_verified': True}))
    raise SystemExit(0)

live = load(BATCH / 'LIVE_SAVE_VERIFICATION.json')
assert live['fresh_reload_verified'] and live['all_exact_rows_verified'] and live['verified_entry_count'] == 2
assert live['prior_source_notes_preserved_exactly_once'] == 24
assert (BATCH / 'LADDER_SAVED_PROOF.png').is_file()
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
current = {row['Video']: row for row in rows}
baseline = load(BATCH / 'INDEX_BEFORE.json')
unrelated = [row for row in baseline if row['Video'] not in NAMES]
assert all(current[row['Video']] == row for row in unrelated)
mapping = load(ROOT / 'MEDIA_LOCATIONS.json')['moved']
states = []
for name in NAMES:
    packet = BATCH / Path(name).stem
    source = load(packet / 'SOURCE.json')
    assert load(packet / 'LEAD_ACCEPTANCE.json')['accepted']
    assert load(packet / 'independent_sol/CHECK_RESULT.json')['accepted']
    assert load(packet / 'REGISTRATION_RESULT.json')['exit_code'] == 0
    for rel, sha in load(packet / 'REVIEW_PACKET_HASHES.json')['files'].items():
        assert digest(packet / rel) == sha, rel
    receipt = load(packet / ('MOVE_RECEIPT.' + name + '.json'))
    assert receipt['identity_match'] and receipt['sha256_before'] == receipt['sha256_after'] == source['sha256']
    archived = ROOT / 'Reviewed' / name
    assert archived.is_file() and not (ROOT / name).exists() and archived.stat().st_size == source['bytes']
    assert current[name]['Status'] == 'Reviewed' and current[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
    location = next(entry for entry in mapping if entry['filename'] == name)
    assert Path(location['current_path']).resolve() == archived.resolve() and location['sha256'] == source['sha256']
    entry = load(packet / 'LADDER_ENTRY.json')
    cloud = metadata(archived)
    states.append({'source': name, 'source_sha256': source['sha256'], 'result': entry['result'], 'opponent': entry['opponent'],
        'review_complete': True, 'independently_accepted': True, 'registered': True, 'archived': True,
        'external_saved': True, 'fresh_reload_verified': True, 'cloud_metadata': cloud,
        'storage_complete': cloud['in_sync'] and cloud['online_only'] and cloud['allocated_bytes'] == 0})
now = datetime.now(timezone.utc).isoformat()
pending = [row['source'] for row in states if not row['storage_complete']]
save(BATCH / 'FINAL_STORAGE_CHECK.json', {'checked_utc': now, 'states': states, 'original_media_read': False, 'files_deleted': 0})
save(BATCH / 'BATCH_STATUS.json', {'checked_utc': now, 'requested_games': 2, 'review_and_ladder_logging_complete': True,
    'archive_complete': True, 'sources': states, 'live_verified_current_season': live['verified_totals'],
    'unrelated_index_rows_preserved': len(unrelated), 'storage_pending': pending, 'external_pending': [], 'review_pending': []})
report = '# October 15 ladder results\n\n'
report += 'Both new recordings have complete source-bound reviews, separate independent acceptance, lead acceptance, immutable completion registration and hash-verified archive moves. Both results are saved exactly once under Deck 01 in the live Ladder Log and verified after reload. All 24 prior current-season entries remain unchanged.\n\n'
for row in states:
    report += f"- `{row['source']}`: {row['result']} versus {row['opponent']}.\n"
report += '\nVerified season total: 26 games, 9 wins and 17 losses. Deck 01 is 1 win and 1 loss. The first loss is an explicit owner concession at an actual 1-2 score; the win ends 3-2. Full lists and hidden cards remain unknown.\n\n'
report += 'Original recordings are preserved in Reviewed. Frozen SOURCE paths retain the review-time location; move receipts and MEDIA_LOCATIONS.json resolve the current paths. No videos were deleted.\n\n'
report += ('OneDrive local cache release remains pending for: ' + ', '.join(pending) + '.\n' if pending else 'Both recordings are verified in sync and online-only with zero allocated local bytes.\n')
with (BATCH / 'README.md').open('x', encoding='utf-8') as f:
    f.write(report)
print(json.dumps({'reviewed_logged_archived': 2, 'current_season': live['verified_totals'], 'storage_pending': pending,
    'unrelated_index_rows_preserved': len(unrelated)}))
