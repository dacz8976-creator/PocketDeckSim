"""Final metadata audit and durable packet mirror. Never read archived video bytes."""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
PACKET = BATCH / '20261012_004128000_iOS'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

context = read(BATCH / 'OWNER_CONTEXT.json')
source = read(PACKET / 'SOURCE.json')
acceptance = read(PACKET / 'LEAD_ACCEPTANCE.json')
move = read(PACKET / ('MOVE_RECEIPT.' + source['video_basename'] + '.json'))
registration = read(PACKET / 'REGISTRATION_RESULT.json')
external = read(PACKET / 'EXTERNAL_LOG_RECEIPT.json')
live = read(BATCH / 'FINAL_LIVE_VERIFICATION.json')
rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
row = next(r for r in rows if r['Video'] == source['video_basename'])
mapped = next(r for r in read(ROOT / 'MEDIA_LOCATIONS.json')['moved'] if r['filename'] == source['video_basename'])
archived = ROOT / row['Location']
assert acceptance['accepted'] and registration['exit_code'] == 0
assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
assert archived.is_file() and archived.stat().st_size == source['bytes']
assert row['Status'] == 'Reviewed' and row['Location'] == 'Reviewed/' + source['video_basename']
assert mapped['sha256'] == source['sha256'] and Path(mapped['current_path']) == archived
assert not (ROOT / source['video_basename']).exists()
assert external['saved'] and external['fresh_reload_verified'] and external['fresh_page_entry'] == external['rendered_entry']
assert live['game_count'] == 37 and live['baseline_games_preserved'] and live['new_game_count'] == 1 and live['pending_sources_not_logged']
pending = []
for name in context['selected_sources']:
    if name == source['video_basename']:
        continue
    p = ROOT / name
    assert p.is_file() and not (ROOT / 'Reviewed' / name).exists()
    assert not (BATCH / p.stem / 'SOURCE.json').exists()
    assert not any(r['Video'] == name for r in rows)
    pending.append({'source_video': name, 'state': 'source_unavailable_pending_review',
                    'bytes_from_metadata_only': p.stat().st_size, 'source_sha256': None,
                    'visual_review_started': False, 'external_logged': False, 'archived': False,
                    'blocker': 'OneDrive read failures, including low-system-resource error; full and small-range hydration retries failed.'})
before = {r['Video']: r for r in read(BATCH / 'INDEX_BEFORE.json')}
current = {r['Video']: r for r in rows}
preserved = all(current.get(name) == original for name, original in before.items())
storage_path = ROOT / 'Recording_QA/CLOUD_STORAGE/20261012T014200149026Z.apply.json'
storage = read(storage_path)
shutil.copy2(storage_path, PACKET / 'STORAGE_RECEIPT.json')
status = {'audited_utc': datetime.now(timezone.utc).isoformat(), 'requested_sources': 3,
          'completed_reviews': 1, 'accepted_registered_archived': 1, 'live_games_added': 1,
          'source_name': source['video_basename'], 'source_sha256': source['sha256'],
          'archive_identity_verified': True, 'current_index_and_location_map_verified': True,
          'unrelated_index_rows_preserved': preserved, 'prior_live_games_preserved': True,
          'live_totals': {'games': 37, 'wins': 20, 'losses': 17, 'concession_wins': 11},
          'capture_status': acceptance['capture_status'], 'pending_sources': pending,
          'storage': {'online_only': False, 'allocated_video_bytes': storage['allocated_bytes_after'],
                      'pending_reason': storage['entries'][0]['pending_reason'], 'files_deleted': 0},
          'archived_video_rehashed_for_this_audit': False}
save(BATCH / 'FINAL_LOCAL_AUDIT.json', status)
save(PACKET / 'FINAL_STATUS.json', {'local_review': 'accepted_registered_archived',
     'external_log': 'saved_and_fresh_reload_verified', 'capture_status': acceptance['capture_status'],
     'storage': status['storage'], 'receipt': 'EXTERNAL_LOG_RECEIPT.json', 'move_receipt': 'MOVE_RECEIPT.' + source['video_basename'] + '.json'})
report = '''# October 11 Pause Games batch

One of three new recordings is fully reviewed, independently accepted, logged and archived. Two remain blocked by OneDrive source availability.

| Source | Status | Result |
| --- | --- | --- |
| 20261012_004128000_iOS.MP4 | Complete; live entry and archive verified | Kingdra ex / Team Rocket's Weezing ex, win 1-0 over ユオカ, went second, four turns |
| 20261012_003458000_iOS.MP4 | Pending; source bytes unavailable | Unreviewed, unlogged, original retained |
| 20261012_004435000_iOS.MP4 | Pending; source bytes unavailable | Unreviewed, unlogged, original retained |

The completed game has the five-card opening, draw-relative native hand evidence, named draws, numbered actions, both boards and Energy Zones, opponent fan counts, exact filmed-QR/live 20-card deck match, and one ledger row per turn. Hidden opponent cards and unopened discard piles remain explicit recording limits. No Ladder Log entry was made.

[Pause Games](https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd) was reloaded after saving. It shows 37 games, 20 wins, 17 losses and 11 concession wins. All 36 prior entries were preserved, and this source appears exactly once. Kingdra's deck record is 5-2. The new win was a knockout of the opponent's last Pokemon, not a concession.

The completed original is in Reviewed with matching pre/post-move SHA-256. Index and media-location records agree. OneDrive has not confirmed the archived original is in sync, so its 245,906,067 local bytes remain preserved and online-only release is pending.

The two other sources could not be read after pinning, repeated hashing attempts, bounded Cloud Files hydration, and a small-range hydration retry. Windows reported a cloud-provider low-resource error. No source identity or battle outcome is claimed for them. They need to become locally readable before review can continue; retry only these source filenames, without reopening older backlog footage.

See FINAL_LOCAL_AUDIT.json, FINAL_LIVE_VERIFICATION.json, the accepted game's independent_sol/CHECK_RESULT.json and EXTERNAL_LOG_RECEIPT.json for verification. This report describes partial batch completion, not completion of all three uploads.
'''
(BATCH / 'README.md').write_text(report, encoding='utf-8')
destination = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / BATCH.name
assert not destination.exists(), 'Mirror destination already exists; inspect before replacing.'
shutil.copytree(BATCH, destination)
files = [p for p in BATCH.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
manifest = []
for p in files:
    rel = p.relative_to(BATCH)
    copied = destination / rel
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    assert hashlib.sha256(copied.read_bytes()).hexdigest() == digest
    manifest.append({'path': str(rel), 'sha256': digest, 'bytes': p.stat().st_size})
receipt = {'destination': str(destination), 'files_verified': len(manifest), 'source_videos_copied': 0,
           'verified_utc': datetime.now(timezone.utc).isoformat(), 'files': manifest}
save(BATCH / 'BOSS_FOLDER_COPY_RECEIPT.json', receipt)
shutil.copy2(BATCH / 'BOSS_FOLDER_COPY_RECEIPT.json', destination / 'BOSS_FOLDER_COPY_RECEIPT.json')
print(json.dumps({'completed': 1, 'pending': 2, 'live_games': 37, 'unrelated_index_rows_preserved': preserved,
                  'mirror_files_verified': len(manifest), 'storage_release_pending': True}))
