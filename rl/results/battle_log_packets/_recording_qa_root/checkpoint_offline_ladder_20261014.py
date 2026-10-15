"""Save honest local batch state without reading or changing cloud originals."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


inventory = load(BATCH / 'SOURCE_INVENTORY.json')
rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
before = load(BATCH / 'INDEX_BEFORE.json')
current = {r['Video']: r for r in rows}
names = {s['video_basename'] for s in inventory}
assert all(current[r['Video']] == r for r in before if r['Video'] not in names)
status = []
for source in inventory:
    packet = Path(source['packet'])
    name = source['video_basename']
    accepted = (packet / 'LEAD_ACCEPTANCE.json').exists() and load(packet / 'LEAD_ACCEPTANCE.json')['accepted']
    registered = (packet / 'REGISTRATION_RESULT.json').exists() and load(packet / 'REGISTRATION_RESULT.json')['exit_code'] == 0
    archived = (packet / ('MOVE_RECEIPT.' + name + '.json')).exists()
    live = (packet / 'LADDER_READBACK.json').exists() and load(packet / 'LADDER_READBACK.json')['verified_after_reload']
    status.append({'source_filename': name, 'source_sha256': source['sha256'], 'bytes': source['bytes'],
                   'duration_seconds': source['duration_seconds'], 'source_original': source['download_original'],
                   'local_current_path': str(ROOT / current[name]['Location']),
                   'full_review_accepted': bool(accepted), 'completion_registered': bool(registered),
                   'local_archived': bool(archived), 'ladder_saved_reload_verified': bool(live),
                   'review_index_status': current[name]['Status'], 'canonical_cloud_copy_verified': False,
                   'one_drive_sync_and_reconciliation_pending': True})
complete = all(s['full_review_accepted'] and s['completion_registered'] and s['local_archived'] and s['ladder_saved_reload_verified'] for s in status)
now = datetime.now(timezone.utc).isoformat()
save(BATCH / 'BATCH_STATUS.json', {'checked_utc': now, 'requested_games': len(status), 'sources': status,
      'local_review_archive_and_ladder_complete': complete, 'all_requested_work_complete': complete,
      'canonical_cloud_work_owner_deferred': True, 'cloud_contents_read': False, 'downloads_originals_preserved': True,
      'reviewed_games': sum(s['full_review_accepted'] for s in status), 'saved_games': sum(s['ladder_saved_reload_verified'] for s in status),
      'unrelated_index_rows_preserved': len(before), 'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1'})
save(BATCH / 'CLOUD_RECONCILIATION_PENDING.json', {'checked_utc': now, 'owner_deferred': True,
      'sources': [{'filename': s['source_filename'], 'source_sha256': s['source_sha256'],
                   'local_current_path': s['local_current_path'], 'downloads_original': s['source_original'],
                   'canonical_cloud_placeholder': str(ROOT / s['source_filename']),
                   'canonical_cloud_copy_verified': False} for s in status],
      'no_cloud_or_local_original_deleted': True, 'future_work': [
          'When OneDrive returns, verify canonical cloud bytes against each local source hash',
          'Reconcile source placement without overwriting conflicts or creating duplicate Ladder entries',
          'Mirror accepted written reviews and retained evidence to Boss Folder',
          'Release video cache only after archive identity and cloud synchronization are verified']})
print(json.dumps({'accepted_games': sum(s['full_review_accepted'] for s in status),
                  'saved_games': sum(s['ladder_saved_reload_verified'] for s in status),
                  'local_work_complete': complete, 'cloud_work_deferred': True}), flush=True)
