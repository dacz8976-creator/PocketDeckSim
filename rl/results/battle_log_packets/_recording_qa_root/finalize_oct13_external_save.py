"""Reconcile the six verified UI saves without rereading archived videos."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / 'Recording_QA/BATCH_2026-10-13_REMAINING_SIX'
RUN = B / 'LIVE_UPDATE_20261013'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--mirror', action='store_true')
args = parser.parse_args()
r = read(RUN / 'LIVE_SAVE_VERIFICATION.json')
assert r['external_saved'] and r['reloaded'] and r['new_sources_exactly_once']
assert r['all_new_visible_game_fields_match'] and r['prior_47_visible_game_fields_unchanged']
assert r['target_deck_exact_20_verified_before_and_after_reload']
assert r['counts'] == {'games': 53, 'wins': 29, 'losses': 24, 'concession_wins': 17, 'decks': 27}
games = {g['source_video']: g for g in r['new_games']}
context = read(B / 'OWNER_CONTEXT.json')
assert set(games) == set(context['selected_sources']) and len(games) == 6
changed = ['BATCH_COMPLETION_CHECK.json', 'README.md', 'REVIEW_ROLES.json']

if not args.mirror:
    for name, game in games.items():
        packet = B / Path(name).stem
        source = read(packet / 'SOURCE.json')
        lead = read(packet / 'LEAD_ACCEPTANCE.json')
        assert lead['accepted'] and source['sha256'] == game['source_sha256'] == lead['source_sha256']
        for filename, expected in lead['accepted_input_sha256'].items():
            bound = 'PAUSE_GAME.before_lead_acceptance.json' if filename == 'PAUSE_GAME.json' else filename
            assert sha(packet / bound) == expected, (name, filename)
        status_path = packet / 'EXTERNAL_SAVE_STATUS.json'
        before_path = packet / 'EXTERNAL_SAVE_STATUS.before_live_save_20261013.json'
        if not before_path.exists():
            shutil.copy2(status_path, before_path)
        else:
            current_status = read(status_path)
            assert current_status['external_saved'] and current_status['source_sha256'] == source['sha256']
        status = {'checked_utc': r['verified_utc'], 'source_video': name, 'source_sha256': source['sha256'],
                  'game_id': game['game_id'], 'external_saved': True, 'fresh_reload_verified': True,
                  'artifact_url': r['artifact_url'], 'live_receipt': '../LIVE_SAVE_VERIFICATION.json',
                  'saved_document_id': None, 'document_id_limit': game['document_id_limit'],
                  'status': 'Saved using the existing artifact entry form; source, date, result, turn order, opponent core and full note verified after reload.'}
        save(status_path, status)
        snapshot = dict(r['target_deck_snapshot'])
        snapshot.update({'source_video': name, 'source_sha256': source['sha256'], 'game_id': game['game_id'],
                         'evidence': '../LIVE_UPDATE_20261013/DECK_LIST_BEFORE.txt',
                         'verified_after_reload': True, 'after_reload_evidence': '../LIVE_UPDATE_20261013/DECK_LIST_AFTER_RELOAD.txt',
                         'preserved_game_deck_snapshot': 'DECK_USED.json'})
        fresh_snapshot_path = packet / 'DECK_LOG_SNAPSHOT.live_20261013.json'
        if fresh_snapshot_path.exists():
            assert read(fresh_snapshot_path) == snapshot
        else:
            save(fresh_snapshot_path, snapshot)
    shutil.copy2(RUN / 'LIVE_SAVE_VERIFICATION.json', B / 'LIVE_SAVE_VERIFICATION.json')
    check_path = B / 'BATCH_COMPLETION_CHECK.json'
    before_check = B / 'BATCH_COMPLETION_CHECK.before_live_save_20261013.json'
    assert not before_check.exists()
    shutil.copy2(check_path, before_check)
    check = read(check_path)
    assert check['all_requested_local_reviews_complete'] and check['storage_complete']
    check.update({'entire_requested_work_complete': True, 'external_saved': True,
                  'external_verified_utc': r['verified_utc'], 'external_verification': 'LIVE_SAVE_VERIFICATION.json',
                  'fresh_live_counts': r['counts'], 'external_blocker': None,
                  'prior_external_blocker_receipt': 'EXTERNAL_ACCESS_BLOCK.json'})
    for item in check['sources']:
        item['external_saved'] = True
    save(check_path, check)
    roles = read(B / 'REVIEW_ROLES.json')
    roles['external_verified_utc'] = r['verified_utc']
    for item in roles['sources']:
        item['status'] = 'accepted_registered_archived_external_saved_online_only'
    save(B / 'REVIEW_ROLES.json', roles)
    text = (B / 'README.md').read_text(encoding='utf-8')
    old = "Pause Games entries are prepared in PAUSE_GAMES_BATCH_IMPORT.json and CLAUDE_IMPORT_REQUEST.txt. They have not been saved or verified live: Computer Use stopped because it could not verify the current Chrome URL for policy enforcement. Historical exact deck snapshots retain their actual retrieval date and are not represented as fresh readbacks."
    assert old in text
    new = "All six games are saved in the existing Pause Games artifact and verified after a fresh reload. Each source appears exactly once with its accepted date, result, turn order, opponent core, source hash and review reference. The prior 47 visible game entries are unchanged. Current totals: 53 games, 29 wins, 24 losses and 17 opponent-concession wins. The 27-deck catalog is preserved, and the used deck's exact 20-card list and QR match before and after reload. Ratings remain unassigned. See LIVE_SAVE_VERIFICATION.json and each game's appended DECK_LOG_SNAPSHOT.live_20261013.json. Internal database IDs are not exposed by the rendered UI; source/game IDs remain in the saved notes. The earlier prepared import and browser-block receipt are retained as history."
    (B / 'README.md').write_text(text.replace(old, new), encoding='utf-8')
    save(B / 'EXTERNAL_SAVE_CHANGED_FILES.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
                                                'changed_existing_files': changed + [Path(name).stem + '/EXTERNAL_SAVE_STATUS.json' for name in games],
                                                'accepted_review_semantics_unchanged': True,
                                                'archived_video_contents_read': False})
    print(json.dumps({'entire_requested_work_complete': True, 'saved_games': 6, 'live_counts': r['counts'],
                      'accepted_review_hashes_match': True, 'archived_video_contents_read': False}))
else:
    receipt_path = B / 'MIRROR_RECEIPT.json'
    receipt = read(receipt_path)
    D = Path(receipt['destination']).resolve()
    boss = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
    assert D.parent == boss and D.name == B.name and D.is_dir()
    entries = {e['path']: e for e in receipt['files']}
    all_paths = {p.relative_to(B).as_posix() for p in B.rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts and p.name != 'MIRROR_RECEIPT.json'}
    assert set(entries) <= all_paths
    changes = read(B / 'EXTERNAL_SAVE_CHANGED_FILES.json')['changed_existing_files']
    copy_paths = sorted((all_paths - set(entries)) | set(changes))
    assert not any(Path(name).suffix.lower() in ['.mp4', '.mov', '.mkv', '.avi', '.m4v'] for name in copy_paths)
    for name in copy_paths:
        source = B / name
        destination = D / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        digest = sha(source)
        assert sha(destination) == digest, name
        entries[name] = {'path': name, 'bytes': source.stat().st_size, 'sha256': digest}
    assert set(entries) == all_paths
    receipt.update({'updated_utc': datetime.now(timezone.utc).isoformat(), 'file_count': len(entries),
                    'files': sorted(entries.values(), key=lambda e: e['path']),
                    'external_save_incremental_update': {'copied_and_hash_verified': copy_paths,
                                                         'archived_video_contents_read': False}})
    save(receipt_path, receipt)
    shutil.copy2(receipt_path, D / receipt_path.name)
    assert sha(receipt_path) == sha(D / receipt_path.name)
    print(json.dumps({'mirrored_files': len(entries), 'updated_copies_verified': len(copy_paths), 'videos_copied': 0}))
