"""Root accepts verified local reviews and archives only their local staging copies."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'Review_Log'))
from review_log import WriteLock, load_events, latest_for, read_index, index_row

BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'
INBOX = ROOT / 'Offline_Inbox'
ARCHIVE = ROOT / 'Offline_Reviewed'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


sources = load(BATCH / 'SOURCE_INVENTORY.json')
p = argparse.ArgumentParser()
p.add_argument('video', choices=[s['video_basename'] for s in sources])
a = p.parse_args()
source = next(s for s in sources if s['video_basename'] == a.video)
packet = Path(source['packet']).resolve()
assert packet.is_relative_to(BATCH.resolve())
assert load(packet / 'SOURCE.json') == source
summary = load(packet / 'SUMMARY.json')
decision = load(packet / 'ROOT_DECISION.json')
manifest_path = packet / 'REVIEW_PACKET_HASHES.json'
manifest = load(manifest_path)
assert manifest['source_sha256'] == source['sha256']
raw_files = manifest['files']
if isinstance(raw_files, list):
    assert len({f['path'] for f in raw_files}) == len(raw_files), 'Duplicate frozen evidence path'
    frozen_files = {f['path']: f['sha256'] for f in raw_files}
else:
    assert isinstance(raw_files, dict)
    frozen_files = raw_files
check_path = packet / 'independent_sol/CHECK_RESULT.json'
check = load(check_path)
assert check['accepted'] and check['frozen_files_match'] and check['primary_unchanged']
assert check['source_filename'] == summary['source_filename'] == source['video_basename'] == decision['source_filename']
assert check['source_sha256'] == summary['source_sha256'] == source['sha256'] == decision['source_sha256']
assert check['frozen_manifest_sha256'] == digest(manifest_path)
assert summary['battle_complete'] and summary['match_count'] == 1
assert decision['battle_complete'] and decision['root_read_full_timeline_and_coverage']
assert decision['auto_option_seen'] is False
assert summary['exact_three_item_note_prefix'] == decision.get('primary_note_prefix', decision['note_prefix'])
assert summary['outcome'] == decision['result']
for rel, sha in frozen_files.items():
    target = (packet / rel).resolve()
    assert target.is_relative_to(packet) and digest(target) == sha, rel
assert len(decision['observations']) >= 3 and all(o['directly_viewed_by_root'] for o in decision['observations'])
for observation in decision['observations']:
    observation['sha256'] = digest(packet / observation['path'])
now = datetime.now(timezone.utc).isoformat()
save_new(packet / 'SOURCE_CHECKS.json', {'lead': '/root', 'checked_utc': now, 'source_filename': a.video,
     'source_sha256': source['sha256'], 'observations': decision['observations'],
     'full_timeline_coverage_read_by_root': True, 'independent_source_check': str(check_path)})
save_new(packet / 'LEAD_ACCEPTANCE.json', {'accepted': True, 'decision': 'accepted_full_battle_review', 'lead': '/root',
     'accepted_utc': now, 'source_video': a.video, 'source_sha256': source['sha256'],
     'source_game_count': 1, 'all_source_games_accepted': True, 'battle_complete': True, 'archive_eligible': True,
     'scope': decision['scope'], 'independent_acceptance': str(check_path), 'independent_acceptance_sha256': digest(check_path),
     'independent_model_configuration': 'gpt-6.1-sol/high fresh compact source check',
     'accepted_input_sha256': frozen_files, 'frozen_manifest_sha256': digest(manifest_path),
     'root_decision': 'ROOT_DECISION.json', 'root_checks': 'SOURCE_CHECKS.json', 'clarifications': decision.get('clarifications', []),
     'canonical_cloud_copy_verified': False, 'offline_local_source_accepted': True})
if (packet / 'LEAD_CLARIFICATION.md').exists():
    save_new(packet / 'ACCEPTED_ADDENDUM_HASHES.json', {'LEAD_CLARIFICATION.md': digest(packet / 'LEAD_CLARIFICATION.md'),
         'ROOT_DECISION.json': digest(packet / 'ROOT_DECISION.json'), 'SOURCE_CHECKS.json': digest(packet / 'SOURCE_CHECKS.json')})
entry = {'source_filename': a.video, 'source_sha256': source['sha256'], 'section': decision['section'],
     'deck_name': decision.get('deck_name'), 'energy': decision.get('energy'), 'opponent': decision['opponent'],
     'opponent_deck': decision['opponent_deck'], 'result': decision['result'], 'note': decision['note'],
     'note_prefix': decision['note_prefix'], 'match_creation_utc': source['source_creation_utc'],
     'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1', 'status': 'ready_for_live_save'}
save_new(packet / 'LADDER_ENTRY.json', entry)
local = (INBOX / a.video).resolve()
destination = (ARCHIVE / a.video).resolve()
assert local.parent == INBOX.resolve() and destination.parent == ARCHIVE.resolve()
assert not destination.exists() and local.is_file()
cmd = [sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record', '--video', a.video,
       '--source-path', str(local), '--reviewer', summary['reviewer'], '--status', 'full_battle_review_complete',
       '--scope', decision['scope'], '--notes', decision['registration_notes'], '--recording-time', source['source_creation_utc']]
for name in ['SOURCE.json', 'COPY_RECEIPT.json', 'REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json',
             'REVIEW_PACKET_HASHES.json', 'ROOT_DECISION.json', 'SOURCE_CHECKS.json', 'LEAD_ACCEPTANCE.json',
             'LADDER_ENTRY.json', 'independent_sol/CHECK_RESULT.json']:
    cmd.extend(['--evidence', str(packet / name)])
if (packet / 'LEAD_CLARIFICATION.md').exists():
    cmd.extend(['--evidence', str(packet / 'LEAD_CLARIFICATION.md')])
    cmd.extend(['--evidence', str(packet / 'ACCEPTED_ADDENDUM_HASHES.json')])
r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=90)
save_new(packet / 'REGISTRATION_RESULT.json', {'registered_utc': datetime.now(timezone.utc).isoformat(),
     'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
assert r.returncode == 0, r.stderr
event = load(Path(r.stdout.strip()))
assert event['video_sha256'] == source['sha256']
with WriteLock(ROOT / 'Review_Log'):
    latest = latest_for(load_events(ROOT), a.video)
    assert latest['event_id'] == event['event_id'] and latest['status'] == 'full_battle_review_complete'
    fields, rows = read_index(ROOT)
    row = index_row(rows, a.video)
    assert row['Status'] == 'Reviewed'
    before = digest(local)
    assert before == source['sha256'] and local.stat().st_size == source['bytes']
    local.rename(destination)
    after = digest(destination)
    assert after == before and destination.stat().st_size == source['bytes']
    receipt_path = packet / ('MOVE_RECEIPT.' + a.video + '.json')
    moved = datetime.now(timezone.utc).isoformat()
    save_new(receipt_path, {'schema': 'battle-offline-media-move-receipt/v1', 'filename': a.video, 'from': str(local),
         'to': str(destination), 'bytes': source['bytes'], 'sha256_before': before, 'sha256_after': after,
         'identity_match': True, 'moved_utc': moved, 'review_event_id': event['event_id'],
         'review_status': event['status'], 'evidence_packet': str(packet), 'downloads_original_preserved': True,
         'canonical_cloud_placeholder_preserved': True, 'cloud_sync_and_canonical_reconciliation_pending': True})
    row['Location'] = destination.relative_to(ROOT).as_posix()
    import csv
    temp_index = ROOT / ('.BATTLE_REVIEW_INDEX.' + event['event_id'] + '.offline.tmp')
    with temp_index.open('x', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp_index, ROOT / 'BATTLE_REVIEW_INDEX.csv')
    map_path = ROOT / 'MEDIA_LOCATIONS.json'
    locations = load(map_path)
    assert not any(m['filename'] == a.video for m in locations['moved'])
    locations['moved'].append({'filename': a.video, 'old_path': str(local), 'current_path': str(destination),
         'bytes': source['bytes'], 'sha256': after, 'download_original': source['download_original'],
         'canonical_cloud_placeholder': source['canonical_cloud_placeholder'], 'canonical_cloud_copy_verified': False,
         'cloud_reconciliation_pending': True, 'review_status': 'Reviewed',
         'review_evidence': [str(packet / n) for n in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json', 'independent_sol/CHECK_RESULT.json']],
         'location_history': [{'from': str(local), 'to': str(destination), 'utc': moved,
              'reason': 'Accepted source-bound local review; owner deferred cloud reconciliation', 'receipt': str(receipt_path)}]})
    locations['index_video_count'] = len(rows)
    locations['awaiting_review_or_confirmation'] = sum(r['Status'] != 'Reviewed' for r in rows)
    locations['updated_utc'] = moved
    map_temp = ROOT / ('.MEDIA_LOCATIONS.' + event['event_id'] + '.offline.tmp')
    save_new(map_temp, locations)
    os.replace(map_temp, map_path)
save_new(packet / 'CLOUD_RECONCILIATION_PENDING.json', {'source_filename': a.video, 'source_sha256': source['sha256'],
     'local_archive': str(destination), 'downloads_original': source['download_original'],
     'canonical_cloud_placeholder': source['canonical_cloud_placeholder'], 'canonical_cloud_copy_verified': False,
     'owner_deferred_cloud_work': True, 'source_contents_deleted': False, 'offline_local_review_complete': True,
     'remaining': ['Verify cloud source identity when OneDrive returns', 'Reconcile canonical cloud placement without duplicate games',
                   'Copy written review/evidence to Boss Folder when appropriate', 'Release archived cache only after in-sync verification']})
print(json.dumps({'video': a.video, 'accepted': True, 'registered': True, 'offline_archive': str(destination),
                  'source_sha256': after, 'cloud_reconciliation_pending': True}), flush=True)
