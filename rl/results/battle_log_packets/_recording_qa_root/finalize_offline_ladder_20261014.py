"""Final local evidence reconciliation; cloud work stays explicitly deferred."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv'], 'No video reread during final checkpoint'
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


inventory = load(BATCH / 'SOURCE_INVENTORY.json')
live = load(BATCH / 'LIVE_SAVE_VERIFICATION.json')
assert live['verified_after_reload'] and live['all_four_unique_and_exact'] and live['baseline_62_rows_preserved']
assert live['total_game_rows'] == 66
assert live['current_season'] == {'wins': 2, 'losses': 8, 'games': 10}
assert live['historical_season'] == {'wins': 27, 'losses': 29, 'games': 56}
assert (BATCH / 'LADDER_LOG_FINAL_VERIFIED.png').exists()
index = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
index_map = {r['Video']: r for r in index}
before = load(BATCH / 'INDEX_BEFORE.json')
assert all(index_map[r['Video']] == r for r in before)
locations = load(ROOT / 'MEDIA_LOCATIONS.json')['moved']
evidence_manifest = {}
reconciled = []
for source in inventory:
    name = source['video_basename']
    packet = Path(source['packet'])
    assert load(packet / 'SOURCE.json') == source
    lead = load(packet / 'LEAD_ACCEPTANCE.json')
    check = load(packet / 'independent_sol/CHECK_RESULT.json')
    assert lead['accepted'] and check['accepted']
    assert check['frozen_files_match'] and check['primary_unchanged']
    assert lead['source_sha256'] == check['source_sha256'] == source['sha256']
    frozen = load(packet / 'REVIEW_PACKET_HASHES.json')['files']
    frozen = {f['path']: f['sha256'] for f in frozen} if isinstance(frozen, list) else frozen
    assert all(digest(packet / rel) == sha for rel, sha in frozen.items())
    copy = load(packet / 'COPY_RECEIPT.json')
    move = load(packet / ('MOVE_RECEIPT.' + name + '.json'))
    assert copy['identity_match'] and copy['sha256_original'] == copy['sha256_local_copy'] == source['sha256']
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
    archived = ROOT / 'Offline_Reviewed' / name
    assert archived.is_file() and archived.stat().st_size == source['bytes']
    assert not (ROOT / 'Offline_Inbox' / name).exists()
    original = Path(source['download_original'])
    assert original.is_file() and original.stat().st_size == source['bytes']
    assert Path(source['canonical_cloud_placeholder']).is_file()
    assert index_map[name]['Status'] == 'Reviewed' and index_map[name]['Location'] == 'Offline_Reviewed/' + name
    mapped = next(m for m in locations if m['filename'] == name)
    assert Path(mapped['current_path']).resolve() == archived.resolve() and mapped['sha256'] == source['sha256']
    assert mapped['cloud_reconciliation_pending'] and not mapped['canonical_cloud_copy_verified']
    registered = load(packet / 'REGISTRATION_RESULT.json')
    event = load(Path(registered['stdout'].strip()))
    assert registered['exit_code'] == 0 and event['event_id'] == move['review_event_id']
    assert event['status'] == 'full_battle_review_complete' and event['video_sha256'] == source['sha256']
    assert event['identity_provenance'] == 'verified_by_cli_sha256' and not event['canonical_cloud_copy_verified']
    entry = load(packet / 'LADDER_ENTRY.json')
    row = live['entries'][name]
    assert row['cells'][:3] == ['L', entry['opponent_deck'], entry['note']]
    save(packet / 'LADDER_READBACK.json', {'source_filename': name, 'source_sha256': source['sha256'],
         'artifact': entry['artifact'], 'verified_after_reload': True, 'verified_utc': live['verified_utc'],
         'entry': row, 'current_season': live['current_season'], 'historical_season': live['historical_season']})
    save(packet / 'EXTERNAL_SAVE_STATUS.json', {'source_filename': name, 'saved': True, 'fresh_reload_verified': True,
         'verified_utc': live['verified_utc'], 'artifact': entry['artifact']})
    reconciled.append({'filename': name, 'source_sha256': source['sha256'], 'archived_local': str(archived),
         'downloads_original_preserved': True, 'canonical_cloud_placeholder_preserved': True,
         'full_review_accepted_registered': True, 'ladder_saved_once_reload_verified': True,
         'canonical_cloud_copy_verified': False, 'cloud_reconciliation_pending': True,
         'frozen_primary_files_verified': len(frozen), 'note_prefix': entry['note_prefix']})

save(BATCH / 'FINAL_RECONCILIATION.json', {'checked_utc': datetime.now(timezone.utc).isoformat(),
     'reviewed_games': 4, 'saved_games': 4, 'local_archive_complete': True, 'baseline_62_saved_rows_preserved': True,
     'unrelated_index_rows_preserved': len(before), 'current_season': live['current_season'],
     'historical_season': live['historical_season'], 'sources': reconciled,
     'original_video_contents_read_at_final_checkpoint': False, 'videos_deleted': 0,
     'canonical_cloud_work_owner_deferred': True, 'boss_mirror_owner_deferred': True})
with (BATCH / 'README.md').open('a', encoding='utf-8') as f:
    f.write('\n## Completed local result\n\nAll four games have completed full reviews, separate independent source acceptance, root reconciliation, immutable completion registration, and verified local archive moves. All four are saved exactly once under Deck 12 and verified after an explicit artifact reload. The current season is 2 wins, 8 losses, and 10 games (20%); the 56 historical games and all 62 prior saved rows remain unchanged.\n\n')
    f.write('Local accepted videos are in Battle Logs/Offline_Reviewed. Each Downloads original and the existing canonical cloud placeholder is preserved. CLOUD_RECONCILIATION_PENDING.json records the deferred synchronization and identity/placement work. The immutable first-pass reports remain intact; nonmaterial season/Card of the Game and Poké Ball citation corrections are explicit root addenda. The online log is complete and must not be duplicated when OneDrive returns.\n')
# A single hash manifest makes the locally saved written/evidence package reviewable.
# Videos live separately and are bound by verified copy/move receipts above.
for path in sorted(BATCH.rglob('*')):
    if path.is_file() and path.name not in ['LOCAL_EVIDENCE_HASHES.json', 'BATCH_STATUS.json', 'CLOUD_RECONCILIATION_PENDING.json']:
        assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv']
        evidence_manifest[path.relative_to(BATCH).as_posix()] = digest(path)
save(BATCH / 'LOCAL_EVIDENCE_HASHES.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
     'source_folder': str(BATCH), 'files': evidence_manifest, 'file_count': len(evidence_manifest),
     'videos_included': False, 'cloud_mirror_verified': False})
print(json.dumps({'local_reviews_registered_archived': 4, 'ladder_entries_saved_reload_verified': 4,
     'current_season': live['current_season'], 'written_and_evidence_files_hashed': len(evidence_manifest),
     'cloud_work_deferred': True}), flush=True)
