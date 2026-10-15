"""Reconcile only the newest pair, append live provenance, and mirror evidence."""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
NAMES = ['20261013_022530000_iOS', '20261013_030351000_iOS']
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

assert not (BATCH / 'BATCH_COMPLETION_CHECK.json').exists()
now = datetime.now(timezone.utc).isoformat()
before = {r['Video']: r for r in read(BATCH / 'INDEX_BEFORE.json')}
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    current = {r['Video']: r for r in csv.DictReader(f)}
selected = {n + '.MP4' for n in NAMES}
assert all(current.get(n) == r for n, r in before.items() if n not in selected)
assert not (set(current) - set(before) - selected)
locations = read(ROOT / 'MEDIA_LOCATIONS.json')['moved']
live = read(BATCH / 'LIVE_SAVE_VERIFICATION.json')
assert live['reloaded'] and live['prior_45_games_unchanged'] and live['prior_26_decks_unchanged']
assert (live['total_games'], live['wins'], live['losses'], live['concession_wins'], live['deck_count']) == (47, 26, 21, 16, 27)
storage = read(BATCH / 'FINAL_STORAGE_CHECK.json')
assert {e['video'] for e in storage['entries']} == selected
assert all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in storage['entries'])
prepared = read(BATCH / 'PREPARED_FILMED_DECK.json')['deck']
deck_matches = [d for d in live['all_decks'] if d['code'] == prepared['deck_code']]
assert len(deck_matches) == 1 and deck_matches[0]['name'] == prepared['name']
expected_rows = [[str(c['n']), c['name'], c['id']] for c in prepared['cards']]
assert deck_matches[0]['rows'] == expected_rows
assert sum(int(r[0]) for r in expected_rows) == 20
accepted = []
for i, name in enumerate(NAMES):
    packet = BATCH / name
    source = read(packet / 'SOURCE.json')
    summary = read(packet / 'SUMMARY.json')
    turn_count = summary.get('turn_count', summary.get('turns_played'))
    outcome = summary.get('result', summary.get('outcome'))
    game = read(packet / 'PAUSE_GAME.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    move = read(packet / ('MOVE_RECEIPT.' + name + '.MP4.json'))
    assert lead['accepted'] and lead['all_source_games_accepted'] and lead['source_game_count'] == 1
    assert lead['source_sha256'] == source['sha256']
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
    registration = read(packet / 'REGISTRATION_RESULT.json')
    assert registration['exit_code'] == 0
    event_path = Path(registration['stdout'].strip()).resolve()
    assert event_path.parent == (ROOT / 'Review_Log/events').resolve() and move['review_event_id'] in event_path.name
    event = read(event_path)
    assert event['status'] == 'full_battle_review_complete' and event['video_basename'] == source['video_basename'] and event['video_sha256'] == source['sha256']
    assert current[name + '.MP4']['Status'] == 'Reviewed' and current[name + '.MP4']['Location'].replace('\\', '/') == 'Reviewed/' + name + '.MP4'
    assert not (ROOT / (name + '.MP4')).exists()
    assert (ROOT / 'Reviewed' / (name + '.MP4')).stat().st_size == source['bytes']
    entries = [e for e in locations if e['filename'] == name + '.MP4']
    assert len(entries) == 1 and entries[0]['sha256'] == source['sha256']
    turns = read(packet / 'TURN_LEDGER.json')['turns']
    assert len(turns) == turn_count == lead['turn_rows'] == [12, 16][i]
    assert [r['turn_number'] for r in turns] == list(range(1, len(turns) + 1))
    for filename, expected in lead['accepted_input_sha256'].items():
        bound = 'PAUSE_GAME.before_lead_acceptance.json' if filename == 'PAUSE_GAME.json' else filename
        assert digest(packet / bound) == expected, (name, filename)
    old_game = read(packet / 'PAUSE_GAME.before_lead_acceptance.json')
    for key in set(game) | set(old_game):
        if key not in ['lead_checked', 'battle_review_status', 'lead_acceptance']:
            assert game.get(key) == old_game.get(key)
    rows = [r for r in live['all_game_texts'] if source['video_basename'] in r]
    assert len(rows) == 1 and ['Win by concession', 'Loss'][i] in rows[0]
    assert summary['classification'] == 'human' and outcome == ['win', 'loss'][i]
    save(packet / 'EXTERNAL_SAVE_STATUS.json', {'verified_utc': now, 'source': source['video_basename'], 'source_sha256': source['sha256'], 'game_id': game['game_id'], 'external_saved': True, 'fresh_reload_verified': True, 'artifact_url': live['artifact_url'], 'saved_row': rows[0], 'verification_receipt': '../LIVE_SAVE_VERIFICATION.json', 'ratings': 'Unassigned.'})
    save(packet / 'DECK_LOG_SNAPSHOT.json', {'retrieved_utc': live['verified_utc'], 'game_id': game['game_id'], 'source_video': source['video_basename'], 'source_sha256': source['sha256'], 'slot_count': 20, 'deck_id': prepared['id'], 'deck_label': prepared['name'], 'energy': prepared['energy'], 'qr_payload': prepared['deck_code'], 'cards': prepared['cards'], 'actual_live_rows': deck_matches[0]['rows'], 'artifact_url': live['artifact_url'], 'live_readback_receipt': '../LIVE_SAVE_VERIFICATION.json', 'supplement': 'Append-only saved-list readback. Initial absence and accepted DECK_USED remain preserved. Artwork and rarity unverified.'})
    accepted.append({'source': source['video_basename'], 'sha256': source['sha256'], 'game_id': game['game_id'], 'opponent': summary['opponent'], 'result': outcome, 'turns': len(turns), 'registration_event': move['review_event_id'], 'archive_hash_verified': True, 'external_saved': True, 'storage_online_only': True, 'packet': str(packet)})
completion = {'checked_utc': now, 'all_requested_reviews_complete': True, 'sources': accepted, 'counts': {'sources': 2, 'games': 2, 'wins': 1, 'losses': 1, 'opponent_concessions': 1, 'turns': 28}, 'all_source_games_covered': True, 'unrelated_index_rows_unchanged': True, 'external_saved': True, 'fresh_live_counts': {'games': 47, 'wins': 26, 'losses': 21, 'concession_wins': 16, 'decks': 27}, 'storage_online_only_count': 2, 'storage_allocated_bytes': 0, 'source_contents_not_read_for_final_reconciliation': True, 'accepted_packet_semantics_unchanged': True}
save(BATCH / 'BATCH_COMPLETION_CHECK.json', completion)
roles = read(BATCH / 'REVIEW_ROLES.json')
roles['updated_utc'] = now
for r in roles['sources']: r['current_status'] = 'accepted_registered_archived_live_verified_and_online_only'
save(BATCH / 'REVIEW_ROLES.json', roles)
shutil.copy2(BATCH / 'README.md', BATCH / 'README.md.before_completion')
(BATCH / 'README.md').write_text('# Newest two recordings completed\n\nBoth recordings received full-source reviews, separate independent acceptance, root checks and registration. Original source hashes match before and after archival into Reviewed. Both originals are in sync, online only and use zero local allocated bytes.\n\n| Recording | Opponent | Result | Turns |\n|---|---|---|---:|\n| [20261013_022530000_iOS.MP4](20261013_022530000_iOS/REVIEW.md) | sadao | Opponent-concession win, 2-1 | 12 |\n| [20261013_030351000_iOS.MP4](20261013_030351000_iOS/REVIEW.md) | ヒロ | Points loss, 2-3 | 16 |\n\nThe same filmed Haxorus / Dragonair / Druddigon deck has 20 cards and Fighting/Metal Energy. The missing deck and both games are saved in Pause Games and verified after reload. The saved log has 47 games, 26 wins, 21 losses, 16 opponent-concession wins and 27 decks. All 45 previous game entries and all 26 previous deck lists remain unchanged.\n\nSource metadata confirms October 12 Chicago evening; original October 13 UTC filenames are preserved. Iris supplied an extra point on the Igglybuff knockout in the loss. The win ended by explicit concession against Mega Scizor ex. Native hand, draw and board evidence and one row per turn are retained. Hidden cards, missing discard views, unresolved reveal timing and exact artwork remain explicit limits.\n\nOnly the frozen newest pair was processed. Other root uploads and the older paused backlog were not reviewed. Written reviews and images are mirrored to Pocket Deck Lab/Boss Folder/BATCH_2026-10-13_NEWEST_TWO with matching copy hashes. See BATCH_COMPLETION_CHECK.json, LIVE_SAVE_VERIFICATION.json, FINAL_STORAGE_CHECK.json and MIRROR_RECEIPT.json.\n', encoding='utf-8')
destination = BOSS / BATCH.name
assert destination.parent == BOSS and not destination.exists()
files = [p for p in BATCH.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
assert not any(p.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi'] for p in files)
shutil.copytree(BATCH, destination, ignore=shutil.ignore_patterns('__pycache__'))
copies = []
for path in sorted(files):
    relative = path.relative_to(BATCH)
    expected = digest(path)
    assert digest(destination / relative) == expected
    copies.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': expected})
receipt = {'copied_utc': datetime.now(timezone.utc).isoformat(), 'source': str(BATCH), 'destination': str(destination), 'file_count': len(copies), 'all_copy_hashes_match': True, 'videos_copied': 0, 'files': copies}
save(BATCH / 'MIRROR_RECEIPT.json', receipt)
shutil.copy2(BATCH / 'MIRROR_RECEIPT.json', destination / 'MIRROR_RECEIPT.json')
assert digest(BATCH / 'MIRROR_RECEIPT.json') == digest(destination / 'MIRROR_RECEIPT.json')
print(json.dumps({'pair_complete': True, 'live_games': 47, 'mirrored_files': len(copies), 'copy_hashes_match': True}))
