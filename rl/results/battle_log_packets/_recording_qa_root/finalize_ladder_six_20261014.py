"""Reconcile this owner's six-game batch using saved UI and archive receipts.

Never reads original media. Frozen review evidence stays unchanged.
"""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / 'Recording_QA'
OLD = QA / 'BATCH_2026-10-14_NEW_LADDER_FOUR'
NEW = QA / 'BATCH_2026-10-14_ADDITIONAL_TWO'
RUN = QA / 'BATCH_2026-10-14_LADDER_RESUME_FIVE'
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder')
NAMES = ['20261014_142546000_iOS.MP4', '20261014_143111000_iOS.MP4',
         '20261014_144627000_iOS.MP4', '20261014_145449000_iOS.MP4',
         '20261014_153139000_iOS.MP4', '20261014_153908000_iOS.MP4']


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv'], path
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def preserve(path):
    if path.exists():
        backup = path.with_name(path.stem + '.before_resume' + path.suffix)
        if not backup.exists():
            shutil.copy2(path, backup)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


live = load(RUN / 'LIVE_SAVE_VERIFICATION.json')
assert live['verified_after_reload'] and live['all_six_unique_and_exact']
assert live['baseline_57_rows_preserved'] and live['total_game_rows'] == 62
assert live['current_season'] == {'wins': 2, 'losses': 4, 'games': 6}
assert live['historical_season'] == {'wins': 27, 'losses': 29, 'games': 56}
assert (RUN / 'LADDER_LOG_FINAL_VERIFIED.png').exists()
cloud_receipts = sorted((QA / 'CLOUD_STORAGE').glob('*.json'))
cloud = next(load(p) for p in reversed(cloud_receipts)
             if {e['video'] for e in load(p).get('entries', [])} == set(NAMES))
metadata = {e['video']: e['after'] for e in cloud['entries']}
locations = load(ROOT / 'MEDIA_LOCATIONS.json')['moved']
index = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
index_map = {r['Video']: r for r in index}
before_index = load(RUN / 'INDEX_BEFORE.json')
unchanged = [r for r in before_index if r['Video'] not in NAMES]
assert all(index_map[r['Video']] == r for r in unchanged)
events = [load(p) for p in (ROOT / 'Review_Log/events').glob('*.json')]
status_rows = []
now = datetime.now(timezone.utc).isoformat()
for name in NAMES:
    batch = NEW if name in NAMES[-2:] else OLD
    packet = batch / Path(name).stem
    source = load(packet / 'SOURCE.json')
    lead = load(packet / 'LEAD_ACCEPTANCE.json')
    check = load(packet / 'independent_sol/CHECK_RESULT.json')
    entry = load(packet / 'LADDER_ENTRY.json')
    frozen = load(packet / 'REVIEW_PACKET_HASHES.json')['files']
    assert lead['accepted'] and check['accepted']
    assert all(digest(packet / rel) == sha for rel, sha in frozen.items())
    receipt = load(packet / ('MOVE_RECEIPT.' + name + '.json'))
    assert receipt['identity_match'] and receipt['sha256_before'] == receipt['sha256_after'] == source['sha256']
    assert receipt['bytes'] == source['bytes']
    current = ROOT / 'Reviewed' / name
    assert current.exists() and not (ROOT / name).exists()
    assert current.stat().st_size == source['bytes']
    assert index_map[name]['Status'] == 'Reviewed'
    assert index_map[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
    mapped = next(m for m in locations if m['filename'] == name)
    assert mapped['sha256'] == source['sha256'] and Path(mapped['current_path']).resolve() == current.resolve()
    event = max((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])
    assert event['status'] == 'full_battle_review_complete' and event['video_sha256'] == source['sha256']
    assert event['event_id'] == receipt['review_event_id']
    row = live['entries'][name]
    assert row['cells'][:3] == ['W' if entry['result'] == 'win' else 'L', entry['opponent_deck'], entry['note']]
    if name != NAMES[0]:
        save(packet / 'LADDER_READBACK.json', {'artifact': entry['artifact'],
             'verified_after_reload': True, 'verified_utc': live['verified_utc'],
             'source_filename': name, 'entry': row, 'current_season': live['current_season'],
             'verification_file': str(RUN / 'LIVE_SAVE_VERIFICATION.json')})
        save(packet / 'EXTERNAL_SAVE_STATUS.json', {'saved': True, 'fresh_reload_verified': True,
             'verified_utc': live['verified_utc'], 'source_filename': name,
             'source_sha256': source['sha256'], 'artifact': entry['artifact']})
    cloud_state = metadata[name]
    storage_done = cloud_state['in_sync'] and cloud_state['online_only'] and cloud_state['allocated_bytes'] == 0
    status_rows.append({'source': name, 'source_sha256': source['sha256'],
         'current_path': str(current), 'result': entry['result'], 'section': 'Deck 12',
         'opponent': entry['opponent'], 'note_prefix': entry['note_prefix'],
         'review_complete': True, 'independently_accepted': True, 'registered': True,
         'archived': True, 'external_saved': True, 'fresh_reload_verified': True,
         'media_contents_read_during_reconciliation': False,
         'frozen_file_count': len(frozen), 'cloud_metadata': cloud_state,
         'storage_complete': bool(storage_done)})

for batch, selected in [(OLD, status_rows[:4]), (NEW, status_rows[4:]), (RUN, status_rows[1:])]:
    preserve(batch / 'BATCH_STATUS.json')
    preserve(batch / 'README.md')
    pending = [r['source'] for r in selected if not r['storage_complete']]
    save(batch / 'BATCH_STATUS.json', {'checked_utc': now, 'requested_games': len(selected),
         'review_and_ladder_logging_complete': True, 'archive_and_mirror_complete': True,
         'all_requested_work_complete': not pending, 'sources': selected,
         'live_verified_current_season': live['current_season'],
         'historical_season_unchanged': live['historical_season'],
         'reviewed_games': len(selected), 'saved_games': len(selected), 'remaining_games': 0,
         'storage_pending': pending, 'storage_metadata_utc': cloud['created_at_utc'],
         'unrelated_index_rows_preserved': len(unchanged),
         'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1'})
    text = '# October 14 ladder batch\n\n'
    text += f'All {len(selected)} games in this packet have full reviews, separate source checks, root acceptance, immutable completion registration, and collision-safe archive receipts. All are saved once under Deck 12 in the existing Ladder Log and verified after reload. The six-game combined current season is 2 wins and 4 losses; all 56 historical games remain unchanged.\n\n'
    text += 'Notes begin with order, Whimsicott ex first attack on owner-turn numbering, and opponent points before that attack. The concession game explicitly says no attack and N/A; the Chacho game qualifies the first attack attempt as missed due to confusion. Hidden deck cards remain unknown. No Auto option was observed.\n\n'
    text += 'Original sources are in Reviewed with unchanged identities. Source paths in frozen evidence intentionally retain their review-time location; MEDIA_LOCATIONS.json and move receipts resolve the archive path. Reports, retained evidence and receipts are copied with hash verification to Pocket Deck Lab/Boss Folder. No original media is copied or deleted.\n\n'
    if pending:
        text += f'OneDrive Free up space has been requested. Local cache release remains pending for {len(pending)} source(s); BATCH_STATUS.json records metadata and exact filenames. No original contents were read during this storage check.\n\n'
    else:
        text += 'All source videos are verified in-sync and online-only with zero allocated bytes.\n\n'
    text += 'Earlier interrupted status and mirror receipts remain preserved in before_resume files. The initial Ghezzuka checker rejection and frozen primary account remain intact; LEAD_CLARIFICATION.md and final independent acceptance record the factual corrections.\n'
    (batch / 'README.md').write_text(text, encoding='utf-8')

reconciliation = {'checked_utc': now, 'accepted_games': 6, 'saved_games': 6,
                  'all_six_unique_and_exact': True, 'baseline_57_rows_preserved': True,
                  'current_season': live['current_season'], 'historical_season': live['historical_season'],
                  'unrelated_index_rows_preserved': len(unchanged), 'source_rows': status_rows,
                  'original_media_read': False, 'videos_deleted': 0}
save(RUN / 'FINAL_RECONCILIATION.json', reconciliation)

for batch in [OLD, NEW, RUN]:
    destination = BOSS / batch.name
    destination.mkdir(parents=True, exist_ok=True)
    preserve(batch / 'MIRROR_RECEIPT.json')
    preserve(destination / 'MIRROR_RECEIPT.json')
    copied = []
    for path in sorted(batch.rglob('*')):
        if not path.is_file() or path.name == 'MIRROR_RECEIPT.json':
            continue
        assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv'], path
        rel = path.relative_to(batch)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        sha = digest(path)
        if target.exists() and digest(target) != sha:
            assert path.name in ['BATCH_STATUS.json', 'README.md'], f'Unexpected mirror conflict {target}'
            preserve(target)
        if not target.exists() or digest(target) != sha:
            shutil.copy2(path, target)
        assert digest(target) == sha
        copied.append({'path': rel.as_posix(), 'bytes': path.stat().st_size, 'sha256': sha})
    mirror = {'created_utc': datetime.now(timezone.utc).isoformat(), 'source': str(batch),
              'destination': str(destination), 'videos_copied': 0, 'all_hashes_verified': True,
              'file_count': len(copied), 'files': copied}
    save(batch / 'MIRROR_RECEIPT.json', mirror)
    shutil.copy2(batch / 'MIRROR_RECEIPT.json', destination / 'MIRROR_RECEIPT.json')
    assert digest(batch / 'MIRROR_RECEIPT.json') == digest(destination / 'MIRROR_RECEIPT.json')
    print(json.dumps({'batch': batch.name, 'files_mirrored': len(copied), 'verified': True}), flush=True)
print(json.dumps({'reviewed_logged_archived': 6, 'current_season': live['current_season'],
      'storage_pending': [r['source'] for r in status_rows if not r['storage_complete']]}), flush=True)
