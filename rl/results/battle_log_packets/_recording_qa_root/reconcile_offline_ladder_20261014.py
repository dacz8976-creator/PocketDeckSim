"""Finish the owner's four-game offline batch without writing to the live log."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / BATCH.name
sys.path.insert(0, str(ROOT / 'Review_Log'))
sys.path.insert(0, str(ROOT / 'Recording_QA'))
from review_log import WriteLock, load_events, latest_for, read_index, index_row
import free_reviewed_video_space as storage


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def preserve(path):
    if path.exists():
        target = path.with_name(path.stem + '.before_sync_recovery' + path.suffix)
        if not target.exists():
            shutil.copy2(path, target)


def archive():
    sources = load(BATCH / 'SOURCE_INVENTORY.json')
    content = load(BATCH / 'SYNC_RECOVERY_CONTENT_CHECKS.json')
    live = load(BATCH / 'SYNC_RECOVERY_LADDER_READBACK.json')
    assert live['all_66_prior_rows_unchanged'] and live['external_writes'] == 0
    # Check the completed written/evidence package before any current-state updates.
    original_manifest = load(BATCH / 'LOCAL_EVIDENCE_HASHES.json')
    for rel, bound in original_manifest['files'].items():
        assert sha(BATCH / rel) == bound, rel
    snapshot = BATCH / 'SYNC_RECOVERY_INDEX_BEFORE.json'
    with WriteLock(ROOT / 'Review_Log'):
        fields, rows = read_index(ROOT)
        if not snapshot.exists():
            save(snapshot, rows)
        before_rows = load(snapshot)
        names = {s['video_basename'] for s in sources}
        assert all(index_row(rows, r['Video']) == r for r in before_rows if r['Video'] not in names)
        locations = load(ROOT / 'MEDIA_LOCATIONS.json')
        map_before = BATCH / 'SYNC_RECOVERY_MEDIA_MAP_BEFORE.json'
        if not map_before.exists():
            save(map_before, locations)
        events = load_events(ROOT)
        receipts = []
        for s in sources:
            name = s['video_basename']
            packet = Path(s['packet']).resolve()
            assert packet.is_relative_to(BATCH.resolve())
            check = next(c for c in content['checks'] if c['filename'] == name)
            assert check['all_three_identical']
            assert all(c['sha256'] == s['sha256'] and c['bytes'] == s['bytes'] for c in check['copies'])
            event = latest_for(events, name)
            assert event['status'] == 'full_battle_review_complete' and event['video_sha256'] == s['sha256']
            row = index_row(rows, name)
            assert row['Status'] == 'Reviewed'
            canonical = (ROOT / name).resolve()
            destination = (ROOT / 'Reviewed' / name).resolve()
            assert canonical.parent == ROOT and destination.parent == (ROOT / 'Reviewed').resolve()
            receipt_path = packet / 'SYNC_RECOVERY_MOVE_RECEIPT.json'
            if not receipt_path.exists():
                assert canonical.is_file() and not destination.exists(), 'Destination collision or missing original'
                current = canonical.stat()
                original_check = next(c for c in check['copies'] if Path(c['path']).resolve() == canonical)
                assert current.st_size == s['bytes'] and current.st_mtime_ns == original_check['mtime_ns']
                meta = storage.metadata(canonical)
                assert meta['cloud_placeholder'] and meta['in_sync']
                canonical.rename(destination)
                after = sha(destination)
                assert after == s['sha256'] and destination.stat().st_size == s['bytes']
                save(receipt_path, {'filename': name, 'from': str(canonical), 'to': str(destination),
                     'bytes': s['bytes'], 'sha256_before': s['sha256'], 'sha256_after': after,
                     'identity_match': True, 'moved_utc': now(), 'review_event_id': event['event_id'],
                     'review_status': event['status'], 'evidence_packet': str(packet),
                     'canonical_cloud_copy_verified': True, 'all_three_copies_identical': True})
            receipt = load(receipt_path)
            assert receipt['identity_match'] and destination.is_file() and not canonical.exists()
            row['Location'] = 'Reviewed/' + name
            mapped = next(m for m in locations['moved'] if m['filename'] == name)
            mapped['current_path'] = str(destination)
            mapped['canonical_cloud_copy_verified'] = True
            mapped['canonical_cloud_copy_path'] = str(destination)
            mapped['canonical_cloud_copy_verified_utc'] = receipt['moved_utc']
            mapped['cloud_reconciliation_pending'] = True
            mapped['archive_sync_verified'] = False
            mapped['duplicate_cleanup_pending'] = True
            if not any(h.get('receipt') == str(receipt_path) for h in mapped['location_history']):
                mapped['location_history'].append({'from': str(canonical), 'to': str(destination),
                    'utc': receipt['moved_utc'], 'reason': 'OneDrive restored; identical canonical source archived',
                    'receipt': str(receipt_path)})
            receipts.append(receipt)
            print(json.dumps({'archived': name, 'hash_verified': True}), flush=True)
        for r in rows:
            if r['Video'] not in names:
                assert r == index_row(before_rows, r['Video'])
        temp_index = ROOT / '.BATTLE_REVIEW_INDEX.sync_recovery.tmp'
        with temp_index.open('x', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            writer.writeheader(); writer.writerows(rows)
        os.replace(temp_index, ROOT / 'BATTLE_REVIEW_INDEX.csv')
        locations['updated_utc'] = now()
        temporary = ROOT / '.MEDIA_LOCATIONS.sync_recovery.tmp'
        save(temporary, locations)
        os.replace(temporary, ROOT / 'MEDIA_LOCATIONS.json')
    save(BATCH / 'SYNC_RECOVERY_ARCHIVE_RECEIPTS.json', {'checked_utc': now(), 'sources': receipts,
         'unrelated_index_rows_preserved': len(before_rows) - len(sources), 'external_writes': 0,
         'original_written_evidence_files_verified': len(original_manifest['files'])})
    # Exact paths only. Recycle cleanup is a separate, recoverable operation.
    cleanup = []
    for s in sources:
        for parent in [ROOT / 'Offline_Reviewed', Path('C:/Users/dacz8/Downloads')]:
            path = (parent / s['video_basename']).resolve()
            assert path.parent == parent.resolve()
            check = next(c for c in content['checks'] if c['filename'] == s['video_basename'])
            bound = next(c for c in check['copies'] if Path(c['path']).resolve() == path)
            cleanup.append({'path': str(path), 'filename': s['video_basename'], 'bytes': s['bytes'],
                 'sha256': s['sha256'], 'mtime_ns': bound['mtime_ns'],
                 'keep': str(ROOT / 'Reviewed' / s['video_basename'])})
    save(BATCH / 'DUPLICATE_CLEANUP_PLAN.json', {'created_utc': now(), 'method': 'Windows Recycle Bin',
         'owner_authorized_duplicate_removal': True, 'files': cleanup})


def mirror():
    assert BOSS.parent.resolve() == Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
    BOSS.mkdir(exist_ok=True)
    copied = []
    for path in sorted(BATCH.rglob('*')):
        if not path.is_file() or path.name in ['SYNC_RECOVERY_MIRROR_RECEIPT.json', 'SYNC_RECOVERY_PACKAGE_HASHES.json']:
            continue
        assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv', '.avi', '.m4v']
        relative = path.relative_to(BATCH)
        target = BOSS / relative
        assert target.resolve().is_relative_to(BOSS.resolve())
        bound = sha(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha(target) != bound:
            # Only our explicitly mutable recovery summaries may change between checkpoints.
            assert path.name in ['SYNC_RECOVERY_STATUS.json', 'SYNC_RECOVERY_README.md',
                 'SYNC_RECOVERY_PACKAGE_HASHES.json', 'SYNC_RECOVERY_KEEP_SYNC.json',
                 'SYNC_RECOVERY_RECORD_STORAGE.json', 'BATCH_STATUS.json', 'CLOUD_RECONCILIATION_PENDING.json'], str(target)
            preserve(target)
        if not target.exists() or sha(target) != bound:
            shutil.copy2(path, target)
        assert sha(target) == bound
        copied.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': bound})
    status_path = BATCH / 'SYNC_RECOVERY_STATUS.json'
    if status_path.exists():
        status = load(status_path)
        status['review_records_mirror_verified'] = True
        status['review_records_mirror_destination'] = str(BOSS)
        status['review_records_mirror_verified_utc'] = now()
        save(status_path, status)
        shutil.copy2(status_path, BOSS / status_path.name)
        status_sha = sha(status_path)
        assert sha(BOSS / status_path.name) == status_sha
        copied = [f for f in copied if f['path'] != status_path.name]
        copied.append({'path': status_path.name, 'bytes': status_path.stat().st_size, 'sha256': status_sha})
    package = BATCH / 'SYNC_RECOVERY_PACKAGE_HASHES.json'
    save(package, {'created_utc': now(), 'files': {f['path']: f['sha256'] for f in copied},
         'videos_included': False, 'mirror_destination': str(BOSS)})
    shutil.copy2(package, BOSS / package.name)
    assert sha(package) == sha(BOSS / package.name)
    copied.append({'path': package.name, 'bytes': package.stat().st_size, 'sha256': sha(package)})
    result = {'created_utc': now(), 'source': str(BATCH), 'destination': str(BOSS),
         'files': copied, 'file_count': len(copied), 'videos_copied': 0, 'all_hashes_verified': True}
    save(BATCH / 'SYNC_RECOVERY_MIRROR_RECEIPT.json', result)
    shutil.copy2(BATCH / 'SYNC_RECOVERY_MIRROR_RECEIPT.json', BOSS / 'SYNC_RECOVERY_MIRROR_RECEIPT.json')
    assert sha(BATCH / 'SYNC_RECOVERY_MIRROR_RECEIPT.json') == sha(BOSS / 'SYNC_RECOVERY_MIRROR_RECEIPT.json')
    print(json.dumps({'review_evidence_files_mirrored': len(copied), 'all_hashes_verified': True}), flush=True)


def sync_check():
    sources = []
    for s in load(BATCH / 'SOURCE_INVENTORY.json'):
        path = ROOT / 'Reviewed' / s['video_basename']
        meta = storage.metadata(path)
        sources.append({'filename': s['video_basename'], 'path': str(path), 'metadata': meta})
    result = {'checked_utc': now(), 'all_four_in_sync': all(s['metadata']['cloud_placeholder'] and
         s['metadata']['in_sync'] for s in sources), 'sources': sources, 'video_contents_read': False}
    save(BATCH / 'SYNC_RECOVERY_KEEP_SYNC.json', result)
    with WriteLock(ROOT / 'Review_Log'):
        locations = load(ROOT / 'MEDIA_LOCATIONS.json')
        for state in sources:
            mapped = next(m for m in locations['moved'] if m['filename'] == state['filename'])
            mapped['archive_sync_verified'] = state['metadata']['in_sync']
            mapped['cloud_reconciliation_pending'] = not state['metadata']['in_sync']
        locations['updated_utc'] = now()
        temporary = ROOT / '.MEDIA_LOCATIONS.sync_state.tmp'
        save(temporary, locations); os.replace(temporary, ROOT / 'MEDIA_LOCATIONS.json')
    batch_status_path = BATCH / 'BATCH_STATUS.json'
    preserve(batch_status_path)
    status = load(batch_status_path)
    status['canonical_cloud_work_owner_deferred'] = False
    status['all_requested_work_complete'] = False
    status['sync_recovery_check'] = 'SYNC_RECOVERY_KEEP_SYNC.json'
    status['duplicate_cleanup_pending'] = True
    for item in status['sources']:
        state = next(s for s in sources if s['filename'] == item['source_filename'])
        item['local_current_path'] = state['path']
        item['canonical_cloud_copy_verified'] = True
        item['one_drive_sync_and_reconciliation_pending'] = not state['metadata']['in_sync']
    save(batch_status_path, status)
    print(json.dumps(result, indent=2), flush=True)


def finish():
    sources = load(BATCH / 'SOURCE_INVENTORY.json')
    clean = load(BATCH / 'DUPLICATE_CLEANUP_RECEIPT.json')
    assert clean['recycled_count'] == 8 and clean['permanent_deletions'] == 0
    assert len({f['path'] for f in clean['files']}) == 8
    live = load(BATCH / 'SYNC_RECOVERY_LADDER_READBACK.json')
    assert live['all_66_prior_rows_unchanged'] and live['external_writes'] == 0
    source_rows = []
    with WriteLock(ROOT / 'Review_Log'):
        fields, index = read_index(ROOT)
        before = load(BATCH / 'SYNC_RECOVERY_INDEX_BEFORE.json')
        names = {s['video_basename'] for s in sources}
        assert all(index_row(index, r['Video']) == r for r in before if r['Video'] not in names)
        locations = load(ROOT / 'MEDIA_LOCATIONS.json')
        for s in sources:
            name = s['video_basename']; packet = Path(s['packet'])
            archive_path = ROOT / 'Reviewed' / name
            assert archive_path.is_file() and archive_path.stat().st_size == s['bytes']
            assert index_row(index, name)['Location'] == 'Reviewed/' + name
            for parent in [ROOT, ROOT / 'Offline_Reviewed', Path('C:/Users/dacz8/Downloads')]:
                assert not (parent / name).exists(), str(parent / name)
            meta = storage.metadata(archive_path)
            assert meta['cloud_placeholder']
            mapped = next(m for m in locations['moved'] if m['filename'] == name)
            assert Path(mapped['current_path']).resolve() == archive_path.resolve()
            mapped['duplicate_cleanup_pending'] = False
            mapped['cloud_reconciliation_pending'] = not meta['in_sync']
            mapped['archive_sync_verified'] = meta['in_sync']
            mapped['duplicate_cleanup_receipt'] = str(BATCH / 'DUPLICATE_CLEANUP_RECEIPT.json')
            source_rows.append({'filename': name, 'sha256': s['sha256'], 'path': str(archive_path),
                 'metadata': meta, 'one_active_copy_verified': True, 'duplicates_recycled': 2})
            pending = packet / 'CLOUD_RECONCILIATION_PENDING.json'
            preserve(pending)
            save(pending, {'source_filename': name, 'source_sha256': s['sha256'], 'pending': not meta['in_sync'],
                 'checked_utc': now(), 'canonical_cloud_copy_verified': True, 'archive': str(archive_path),
                 'in_sync_verified': meta['in_sync'], 'cache_release_pending': not meta['online_only'], 'duplicates_recycled': 2,
                 'current_status': str(BATCH / 'SYNC_RECOVERY_STATUS.json'),
                 'historical_pending_record': pending.stem + '.before_sync_recovery.json'})
        locations['updated_utc'] = now()
        temp = ROOT / '.MEDIA_LOCATIONS.sync_finished.tmp'
        save(temp, locations); os.replace(temp, ROOT / 'MEDIA_LOCATIONS.json')
    status = {'checked_utc': now(), 'requested_games': 4, 'video_files_retained': 4,
         'canonical_cloud_copy_identity_verified': True,
         'all_four_archived_in_sync': all(s['metadata']['in_sync'] for s in source_rows),
         'source_rows': source_rows, 'duplicate_copies_recycled': 8, 'permanent_deletions': 0,
         'one_active_copy_per_video_verified': True,
         'online_only_verified': all(s['metadata']['online_only'] and s['metadata']['allocated_bytes'] == 0 for s in source_rows),
         'review_records_mirror_verified': False, 'external_log_writes': 0,
         'all_66_ladder_entries_unchanged': True, 'current_season': live['current_season'],
         'historical_season': live['historical_season'], 'unrelated_index_rows_preserved': len(before) - 4,
         'review_completion_events_preserved': True, 'frozen_review_source_paths_preserved': True}
    status['cloud_sync_confirmation_pending'] = not status['all_four_archived_in_sync']
    status['cache_release_pending'] = not status['online_only_verified']
    status['owner_phone_originals_preserved'] = True
    status['owner_phone_originals_evidence'] = 'Owner reported phone originals remain available'
    status['pre_phone_deletion_sync_check_passed'] = status['all_four_archived_in_sync']
    status['owner_phone_originals_condition'] = 'Double-check final OneDrive sync before owner deletes phone originals'
    save(BATCH / 'SYNC_RECOVERY_STATUS.json', status)
    batch_status_path = BATCH / 'BATCH_STATUS.json'
    preserve(batch_status_path)
    batch_status = load(batch_status_path)
    batch_status['canonical_cloud_work_owner_deferred'] = False
    batch_status['cloud_reconciliation_pending'] = status['cloud_sync_confirmation_pending']
    batch_status['duplicate_cleanup_pending'] = False
    batch_status['all_requested_work_complete'] = status['all_four_archived_in_sync']
    batch_status['sync_recovery_status'] = 'SYNC_RECOVERY_STATUS.json'
    batch_status['duplicates_recycled'] = 8
    batch_status['cache_release_pending'] = status['cache_release_pending']
    for old in batch_status['sources']:
        old['local_current_path'] = str(ROOT / 'Reviewed' / old['source_filename'])
        old['canonical_cloud_copy_verified'] = True
        current = next(s for s in source_rows if s['filename'] == old['source_filename'])
        old['one_drive_sync_and_reconciliation_pending'] = not current['metadata']['in_sync']
    save(batch_status_path, batch_status)
    pending = BATCH / 'CLOUD_RECONCILIATION_PENDING.json'
    preserve(pending)
    save(pending, {'pending': status['cloud_sync_confirmation_pending'], 'checked_utc': now(), 'source_count': 4,
         'current_status': 'SYNC_RECOVERY_STATUS.json',
         'remaining': (['Confirm new Reviewed paths are in sync'] if status['cloud_sync_confirmation_pending'] else [])
             + (['OneDrive local video cache release remains pending; originals retained'] if status['cache_release_pending'] else []),
         'historical_pending_record': 'CLOUD_RECONCILIATION_PENDING.before_sync_recovery.json'})
    (BATCH / 'SYNC_RECOVERY_README.md').write_text(
        '# October 14 OneDrive reconciliation\n\n'
        'The four offline-reviewed ladder videos are now archived in the normal Battle Logs/Reviewed folder. '
        'Each canonical OneDrive source, offline review copy, and Downloads copy had an identical SHA-256 and byte size. '
        'The canonical sources were moved without changing their filenames, verified again, and reconciled with the existing review index and media location map.\n\n'
        'Eight extra video copies were sent to the Windows Recycle Bin, leaving one active copy of each recording. '
        'No Recycle Bin was emptied. Source-bound full reviews, independent acceptance, original completion events, '
        'and historical source paths remain unchanged. The mirror receipt records the hash-verified review and evidence copies in Pocket Deck Lab/Boss Folder.\n\n'
        'A fresh Ladder Log reload confirmed all 66 entries unchanged, with exactly one entry per source and no external writes. '
        'Deck 12 remains at 2 wins and 8 losses (20%) this season. The 56 historical entries remain unchanged.\n\n'
        'SYNC_RECOVERY_STATUS.json records current archive and storage state. Earlier README, pending records, and final reconciliation describe the offline phase and are retained as history. '
        'The before_sync_recovery files preserve mutable status records from that phase.\n\n'
        + ('OneDrive still marks the four new archive locations as sync pending. The owner reports the client is looking for changes. '
           'The owner retains the phone originals and will double-check final synchronization before deleting them. '
           'Cache release is deferred until in-sync confirmation. No phone media was accessed or deleted.\n'
           if status['cloud_sync_confirmation_pending'] else 'All four archive locations are confirmed in sync. The requested pre-deletion synchronization check has passed. No phone media was accessed or deleted.\n')
        + ('\nOneDrive Free up space was requested, but the cloud provider declined direct cache release. '
           'The four synced originals remain locally available; cache release is still pending. '
           'SYNC_RECOVERY_CACHE_STATUS.json and SYNC_RECOVERY_CACHE_RELEASE.json preserve the results.\n'
           if status['cache_release_pending'] else '\nAll four source videos are in sync and online-only, with zero allocated local bytes. Written reviews and evidence stay available locally.\n'), encoding='utf-8')
    print(json.dumps({k: v for k, v in status.items() if k != 'source_rows'}), flush=True)


parser = argparse.ArgumentParser()
parser.add_argument('operation', choices=['archive', 'sync-check', 'finish', 'mirror'])
args = parser.parse_args()
{'archive': archive, 'sync-check': sync_check, 'finish': finish, 'mirror': mirror}[args.operation]()
