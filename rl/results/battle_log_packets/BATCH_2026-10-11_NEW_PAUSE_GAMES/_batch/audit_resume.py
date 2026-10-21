"""Audit resumed review and incrementally mirror evidence without reading archived videos."""
import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
sys.path.insert(0, str(ROOT / 'Recording_QA'))
from free_reviewed_video_space import metadata

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def preserve(path):
    if path.exists():
        backup = BATCH / 'BEFORE_RESUME_FINALIZATION' / path.relative_to(BATCH)
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(path, backup)

context = read(BATCH / 'OWNER_CONTEXT.json')
live = read(BATCH / 'RESUME_LIVE_VERIFICATION.json')
assert live['game_count'] == 37 + live['new_game_count'] and live['baseline_games_preserved']
assert live['new_game_count'] == 2 and live['pending_sources_not_logged']
rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
maps = read(ROOT / 'MEDIA_LOCATIONS.json')['moved']
completed = []
pending = []
for name in context['selected_sources']:
    packet = BATCH / Path(name).stem
    if not (packet / 'LEAD_ACCEPTANCE.json').exists():
        path = ROOT / name
        assert path.is_file() and not (ROOT / 'Reviewed' / name).exists()
        assert not (packet / 'SOURCE.json').exists()
        assert not any(row['Video'] == name for row in rows)
        pending.append({'source_video': name, 'state': 'source_unavailable_pending_review',
                        'metadata': metadata(path.resolve()), 'source_sha256': None,
                        'visual_review_started': False, 'external_logged': False, 'archived': False,
                        'blocker': 'Desktop cloud reads and bounded hydration timed out. Direct web download awaits owner OneDrive sign-in.'})
        continue
    source = read(packet / 'SOURCE.json')
    acceptance = read(packet / 'LEAD_ACCEPTANCE.json')
    move = read(packet / ('MOVE_RECEIPT.' + name + '.json'))
    registration = read(packet / 'REGISTRATION_RESULT.json')
    external = read(packet / 'EXTERNAL_LOG_RECEIPT.json')
    independent = read(packet / 'independent_sol' / 'CHECK_RESULT.json')
    assert independent['accepted'] and not independent.get('required_repairs')
    assert independent['source_sha256'] == source['sha256']
    for filename, digest in independent['accepted_input_sha256'].items():
        original = packet / ('PAUSE_GAME.before_lead_acceptance.json' if filename == 'PAUSE_GAME.json' else filename)
        assert sha(original) == digest, 'Accepted review changed: ' + name + '/' + filename
    row = next(row for row in rows if row['Video'] == name)
    mapped = next(entry for entry in maps if entry['filename'] == name)
    archived = ROOT / row['Location']
    assert acceptance['accepted'] and registration['exit_code'] == 0
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
    assert archived.is_file() and archived.stat().st_size == source['bytes']
    assert row['Status'] == 'Reviewed' and row['Location'] == 'Reviewed/' + name
    assert mapped['sha256'] == source['sha256'] and Path(mapped['current_path']) == archived
    assert not (ROOT / name).exists()
    assert external['saved'] and external['fresh_reload_verified']
    assert external['fresh_page_entry'] == external['rendered_entry']
    storage = metadata(archived.resolve())
    save(packet / 'FINAL_STORAGE_VERIFICATION.json', {'verified_utc': datetime.now(timezone.utc).isoformat(),
         'source_video': name, 'source_sha256': source['sha256'], 'metadata': storage,
         'archived_video_contents_read': False, 'files_deleted': 0})
    completed.append({'source_video': name, 'source_sha256': source['sha256'],
                      'capture_status': acceptance['capture_status'],
                      'archive_identity_verified': True, 'storage': storage})
    preserve(packet / 'FINAL_STATUS.json')
    save(packet / 'FINAL_STATUS.json', {'local_review': 'accepted_registered_archived',
         'external_log': 'saved_and_fresh_reload_verified', 'capture_status': acceptance['capture_status'],
         'storage': storage, 'video_contents_read_for_storage_audit': False,
         'receipt': 'EXTERNAL_LOG_RECEIPT.json', 'move_receipt': 'MOVE_RECEIPT.' + name + '.json'})
assert len(completed) == 3 and not pending
before = {row['Video']: row for row in read(BATCH / 'INDEX_BEFORE.json')}
current = {row['Video']: row for row in rows}
preserved = all(current.get(name) == original for name, original in before.items())
assert preserved, 'Unrelated index changed'
status = {'audited_utc': datetime.now(timezone.utc).isoformat(), 'requested_sources': 3,
          'completed_reviews': len(completed), 'accepted_registered_archived': len(completed), 'live_games_added_in_batch': 3,
          'live_games_added_this_resume': 2, 'completed_sources': completed, 'pending_sources': pending,
          'current_index_and_location_map_verified': True, 'unrelated_index_rows_preserved': preserved,
          'prior_live_games_preserved': True,
          'live_totals': live['totals'],
          'archived_videos_rehashed_for_this_audit': False, 'files_deleted': 0}
preserve(BATCH / 'FINAL_LOCAL_AUDIT.json')
save(BATCH / 'FINAL_LOCAL_AUDIT.json', status)
preserve(BATCH / 'README.md')
last_summary = read(BATCH / '20261012_003458000_iOS' / 'SUMMARY.json')
last_outcome = last_summary['outcome']
last_result = (last_outcome.get('owner_result', last_outcome.get('owner', 'see packet'))
               if isinstance(last_outcome, dict) else last_outcome)
last_opponent = last_summary.get('opponent_name', last_summary.get('opponent', 'see packet'))
last_turns = last_summary.get('turn_count', 'see packet')
totals = live['totals']
local_storage = [entry for entry in completed if not entry['storage']['online_only']]
storage_note = ('All three archived originals are verified in sync and online-only, with zero allocated local video bytes.'
                if not local_storage else 'Online-only release is pending for ' + ', '.join(entry['source_video'] for entry in local_storage)
                + ' while OneDrive finishes sync. Their ' + str(sum(entry['storage']['allocated_bytes'] for entry in local_storage))
                + ' local video bytes remain preserved. The other archived originals are verified online-only.')
(BATCH / 'README.md').write_text(f'''# October 11 Pause Games batch

All three new recordings are fully reviewed, independently accepted, logged and archived. Both outstanding videos downloaded successfully during this retry.

| Source | Status | Result |
| --- | --- | --- |
| [20261012_004128000_iOS.MP4](20261012_004128000_iOS/REVIEW.md) | Complete; live entry and archive verified | Kingdra ex / Team Rocket's Weezing ex, win 1-0 over ユオカ, went second, four turns |
| [20261012_004435000_iOS.MP4](20261012_004435000_iOS/REVIEW.md) | Complete; live entry and archive verified | Kingdra ex / Team Rocket's Weezing ex, win by concession over Chuaryzard, went second, ten turns |
| [20261012_003458000_iOS.MP4](20261012_003458000_iOS/REVIEW.md) | Complete; live entry and archive verified | Kingdra ex / Team Rocket's Weezing ex, {last_result} against {last_opponent}, {last_turns} turns; see packet for terminal evidence |

All games include the required opening, draw-relative native hand evidence, named draws and searches, numbered actions, both boards and Energy Zones, fan counts, exact filmed-QR/live 20-card deck match, and one ledger row per recorded turn. Hidden opponent cards and unopened discard piles remain explicit recording limits. The 003458 opening and first turn have qualified zoom/clipping views, and that source ends during its result transition after the explicit concession. The Chuaryzard game's concession appears at 451-452 seconds; Victory at 462 seconds confirms ten turns, 90 damage and zero earned points on both sides. No Ladder entry was made.

[Pause Games](https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd) was saved and freshly reloaded. It shows {totals['games']} games, {totals['wins']} wins, {totals['losses']} losses and {totals['concession_wins']} concession wins. All 37 entries preceding this retry were preserved; all three batch sources appear exactly once. The live deck record is preserved in RESUME_LIVE_VERIFICATION.json.

The completed originals are in Reviewed with matching pre/post-move SHA-256. Index and media-location records agree. {storage_note} FINAL_LOCAL_AUDIT.json records the latest OneDrive sync and allocated-byte state without reading archived video contents. No files were deleted.

The early desktop reads and bounded cloud hydration timed out. Later retries succeeded after local space became available. Complete source hashes and stable metadata were verified before review. Browser sign-in was no longer needed. Older paused reviews were not reopened.

See FINAL_LOCAL_AUDIT.json, RESUME_LIVE_VERIFICATION.json and each completed game's independent_sol/CHECK_RESULT.json, EXTERNAL_LOG_RECEIPT.json and move receipt. Previous batch-level outputs are retained in BEFORE_RESUME_FINALIZATION and the original FINAL_LIVE_VERIFICATION.json.
''', encoding='utf-8')

destination = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / BATCH.name
assert destination.is_dir(), 'Expected existing verified mirror'
old_receipt = read(destination / 'BOSS_FOLDER_COPY_RECEIPT.json')
known = {entry['path'].replace('\\', '/'): entry['sha256'] for entry in old_receipt['files']}
resume_receipt = destination / 'BOSS_FOLDER_RESUME_COPY_RECEIPT.json'
if resume_receipt.exists():
    known.update({entry['path'].replace('\\', '/'): entry['sha256'] for entry in read(resume_receipt)['files']})
files = [path for path in BATCH.rglob('*') if path.is_file() and '__pycache__' not in path.parts
         and path.name != 'BOSS_FOLDER_RESUME_COPY_RECEIPT.json']
assert not any(path.suffix.lower() in ('.mp4', '.mov', '.m4v', '.mkv', '.avi') for path in files), 'Original video unexpectedly inside evidence packet'
plan = []
for path in files:
    rel = path.relative_to(BATCH)
    copied = destination / rel
    digest = sha(path)
    if copied.exists() and sha(copied) != digest:
        assert rel.as_posix() in known and sha(copied) == known[rel.as_posix()], 'Unexpected mirror collision: ' + str(rel)
    plan.append((path, copied, rel, digest))
manifest = []
for path, copied, rel, digest in plan:
    copied.parent.mkdir(parents=True, exist_ok=True)
    if not copied.exists() or sha(copied) != digest:
        shutil.copy2(path, copied)
    assert sha(copied) == digest
    manifest.append({'path': rel.as_posix(), 'sha256': digest, 'bytes': path.stat().st_size})
receipt = {'destination': str(destination), 'files_verified': len(manifest), 'source_videos_copied': 0,
           'verified_utc': datetime.now(timezone.utc).isoformat(), 'files': manifest,
           'method': 'Incremental copy with prior receipt collision guards; unrelated destination files retained.'}
save(BATCH / 'BOSS_FOLDER_RESUME_COPY_RECEIPT.json', receipt)
shutil.copy2(BATCH / 'BOSS_FOLDER_RESUME_COPY_RECEIPT.json', destination / 'BOSS_FOLDER_RESUME_COPY_RECEIPT.json')
print(json.dumps({'completed': len(completed), 'pending': len(pending), 'live_games': totals['games'],
                  'mirror_files_verified': len(manifest), 'unrelated_index_rows_preserved': preserved}))
