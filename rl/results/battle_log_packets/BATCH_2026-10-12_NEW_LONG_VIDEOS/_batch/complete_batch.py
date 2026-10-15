"""Lead reconciliation and an unsent, reviewable import for four accepted sources."""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
NAMES = ['20261012_010706000_iOS', '20261012_203719000_iOS',
         '20261012_210041000_iOS', '20261012_210823000_iOS']
CORE = {
    NAMES[0]: ['Mega Gardevoir ex', 'Mega Diancie ex', 'Indeedee ex'],
    NAMES[1]: ['Drampa', 'Dragonair', 'Mega Rayquaza ex'],
    NAMES[2]: ['Mega Lucario ex', 'Hitmonchan ex', 'Riolu', 'Tyrogue'],
    NAMES[3]: ['Mega Pidgeot ex', 'Meowth', 'Alolan Meowth'],
}
ENDING = {
    NAMES[0]: 'Kingambit knocks out Mega Gardevoir ex; Victory 3-2 around 808 s, detailed result 819 s (21 turns, 600 damage).',
    NAMES[1]: 'Your opponent conceded at 790 s; Victory/result 799-800.5 s (21 turns, 150 damage). Last board 1-2.',
    NAMES[2]: 'Concede menu 432.6 s, confirmation 433.2-433.5 s, then Defeat 434 s/result 440-443 s. Last board 0-2; final numeric statistics unavailable.',
    NAMES[3]: 'Your opponent conceded at 430-431 s; Victory versus Hons at 439 s. Last board 0-1; detailed result statistics not opened. Empty deck is explicitly shown at 428 s.',
}

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(name, value):
    (BATCH / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

now = datetime.now(timezone.utc).isoformat()
selected = {name + '.MP4' for name in NAMES}
before = {row['Video']: row for row in read(BATCH / 'INDEX_BEFORE.json')}
current = {row['Video']: row for row in csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))}
unrelated_changes = [name for name, row in before.items() if name not in selected and current.get(name) != row]
assert not unrelated_changes, unrelated_changes
assert not (set(current) - set(before) - selected), 'Unexpected unrelated index additions'
locations = read(ROOT / 'MEDIA_LOCATIONS.json')['moved']
deck = read(BATCH / 'PREPARED_FILMED_DECK.json')['deck']
assert sum(card['n'] for card in deck['cards']) == 20
assert len(deck['sources']) == 4
baseline = read(BATCH / 'LIVE_BASELINE.json')
assert baseline['new_sources_absent'] is True
storage = read(BATCH / 'FINAL_STORAGE_CHECK.json')
assert {entry['video'] for entry in storage['entries']} == selected
online_only_count = sum(entry['after']['online_only'] and entry['after']['in_sync'] and entry['after']['allocated_bytes'] == 0 for entry in storage['entries'])
games, accepted = [], []
for name in NAMES:
    packet = BATCH / name
    source = read(packet / 'SOURCE.json')
    summary = read(packet / 'SUMMARY.json')
    game = read(packet / 'PAUSE_GAME.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    move = read(packet / ('MOVE_RECEIPT.' + name + '.MP4.json'))
    ledger = read(packet / 'TURN_LEDGER.json')['turns']
    assert lead['accepted'] is True and lead['all_source_games_accepted'] is True
    assert lead['source_sha256'] == source['sha256']
    assert move['identity_match'] is True
    assert move['sha256_before'] == move['sha256_after'] == source['sha256']
    assert current[name + '.MP4']['Status'] == 'Reviewed'
    assert current[name + '.MP4']['Location'].replace('\\', '/') == 'Reviewed/' + name + '.MP4'
    assert (ROOT / 'Reviewed' / (name + '.MP4')).stat().st_size == source['bytes']
    assert not (ROOT / (name + '.MP4')).exists()
    matching = [row for row in locations if row['filename'] == name + '.MP4']
    assert len(matching) == 1 and matching[0]['sha256'] == source['sha256']
    assert len(ledger) == lead['turn_rows'] == summary['turn_count']
    assert [row['turn_number'] for row in ledger] == list(range(1, len(ledger) + 1))
    frozen = lead['accepted_input_sha256']
    for filename, expected in frozen.items():
        actual_file = 'PAUSE_GAME.before_lead_acceptance.json' if filename == 'PAUSE_GAME.json' else filename
        assert digest(packet / actual_file) == expected, (name, filename)
    assert game['lead_checked'] is True
    assert summary.get('auto_visible', summary.get('auto_control_visible')) is False
    outcome = game['outcome']
    if isinstance(outcome, dict):
        owner_result = outcome.get('owner', outcome.get('owner_result'))
        cause = outcome.get('method', outcome.get('cause'))
    else:
        owner_result = {'owner_win': 'win', 'owner_loss': 'loss'}.get(outcome, outcome)
        cause = game.get('terminal_cause')
    assert owner_result in ['win', 'loss']
    cause = cause or summary.get('result_method', summary.get('outcome_cause', summary.get('terminal_cause')))
    # Source-bound classification: only the two explicit opponent-concession games use that UI choice.
    artifact_result = 'concession' if name in [NAMES[1], NAMES[3]] else owner_result
    went_first = summary.get('went_first')
    if went_first is None:
        went_first = ledger[0]['who_played'] == 'owner'
    local_date = read(packet / 'SOURCE_TIME.json')['local_match_date']
    opponent = summary['opponent']
    note = (f"Source: {name}.MP4; game 1; opponent: {opponent}. "
            f"Deluxe Pack: Mega Emblem Event. Owner {owner_result}; ending: {cause or 'cause not established'}. "
            f"Result evidence: {ENDING[name]} "
            f"Full review: {len(ledger)} turns. Evidence and capture limits: "
            f"Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/{name}/REVIEW.md; "
            "PAUSE_GAME.json and TURN_LEDGER.json beside it. Exact 20-card filmed QR verified. "
            "Hidden opponent cards remain unknown; discard piles were not opened. "
            "Native hand/draw crops retained. Ratings unassigned.")
    assert len(note) <= 1500
    games.append({'source_video': name + '.MP4', 'source_sha256': source['sha256'],
        'game_number_in_source': 1, 'game_id': game['game_id'],
        'exact_game_deck_binding': True,
        'deck_choice_basis': 'Identical source-native QR at 0 seconds, exact semantic 20-card list and Darkness Energy.',
        'result_evidence': ENDING[name],
        'fields': {'deck': deck['id'], 'deckName': deck['name'], 'date': local_date,
                   'result': artifact_result, 'first': 'first' if went_first else 'second',
                   'opp': ', '.join(CORE[name]), 'ratings': {}, 'note': note},
        'external_saved': False})
    accepted.append({'source_video': name + '.MP4', 'sha256': source['sha256'],
        'game_id': game['game_id'], 'turns': len(ledger), 'owner_result': owner_result,
        'terminal_cause': cause, 'opponent': opponent, 'local_match_date': local_date,
        'went': 'first' if went_first else 'second', 'local_review_complete': True,
        'registered_event_id': move['review_event_id'], 'archive_hash_verified': True,
        'packet': str(packet), 'external_saved': False})

counts = {'sources': 4, 'games': 4, 'decks': 1,
          'wins': sum(row['owner_result'] == 'win' for row in accepted),
          'losses': sum(row['owner_result'] == 'loss' for row in accepted),
          'opponent_concessions': sum(row['fields']['result'] == 'concession' for row in games),
          'turns': sum(row['turns'] for row in accepted)}
assert counts['wins'] == 3 and counts['losses'] == 1 and counts['opponent_concessions'] == 2
prepared_deck = read(BATCH / 'PREPARED_FILMED_DECK.json')
prepared_deck['deck']['game_binding_status'] = 'All four full-source reviews independently and lead accepted; exact filmed deck continuity confirmed.'
prepared_deck['deck']['accepted_game_ids'] = [row['game_id'] for row in accepted]
save('PREPARED_FILMED_DECK.json', prepared_deck)
completion = {'checked_utc': now, 'all_requested_local_reviews_complete': True,
    'source_count': 4, 'game_count': 4, 'accepted_sources': accepted,
    'counts': counts, 'unrelated_index_rows_unchanged': True,
    'source_contents_not_read_for_final_reconciliation': True,
    'external_saved': False, 'external_pending_reason': 'The new deck is absent and the artifact has no Add Deck control. Sending the prepared import to its existing Claude task requires explicit owner authorization.',
    'storage_state': 'Use the dated metadata-only CLOUD_STORAGE receipt; archive integrity does not prove online-only release.'}
completion['storage_online_only_count'] = online_only_count
completion['storage_allocated_bytes'] = sum(entry['after']['allocated_bytes'] for entry in storage['entries'])
completion['storage_receipt'] = 'FINAL_STORAGE_CHECK.json'
save('BATCH_COMPLETION_CHECK.json', completion)
old_availability = BATCH / 'FINAL_AVAILABILITY.json'
if old_availability.exists():
    preserved = BATCH / 'INITIAL_FAILED_AVAILABILITY.json'
    assert not preserved.exists(), 'Inspect existing preserved availability history'
    shutil.copy2(old_availability, preserved)
save('FINAL_AVAILABILITY.json', {'checked_utc': now, 'all_four_sources_successfully_read_and_reviewed': True,
    'all_four_archived_with_verified_source_identity': True,
    'identity_basis': 'Stable downloaded-source bindings, completion events and matching pre/post move SHA-256 receipts. Final metadata checks do not read or rehydrate video contents.',
    'sources': accepted, 'storage_online_only_count': online_only_count,
    'storage_receipt': 'FINAL_STORAGE_CHECK.json', 'earlier_download_wait': 'INITIAL_FAILED_AVAILABILITY.json'})
deck_document = {'document_id': deck['id'], 'fields': {'name': deck['name'],
    'energy': deck['energy'], 'group': 'filmed', 'status': 'active', 'tag': 'Filmed QR', 'order': 200,
    'note': 'Identical QR in all four October 12 uploads. Semantic card identities verified; filmed artwork and rarity unverified.',
    'code': deck['deck_code'], 'source': 'Four source-bound QR captures at 0 seconds; provenance in PREPARED_FILMED_DECK.json.',
    'cards': deck['cards']}}
save('PAUSE_GAMES_BATCH_IMPORT.json', {'prepared_utc': now,
    'existing_artifact': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
    'existing_authoring_task': 'https://claude.ai/cowork/cse_01RtxfTEtHtFkw97BA1cpD4b',
    'external_saved': False, 'sent_to_claude': False,
    'operation': 'Preserve existing entries; add only the missing filmed deck and four accepted source/game entries after fresh duplicate checks.',
    'required_before_external_write': ['Explicit owner authorization to send this prepared import to the existing Claude task.',
        'Fresh duplicate checks by exact deck QR and source filename plus game identity.',
        'Reload and verify exact new deck, all four entries and totals; compare prior 39 games and 25 decks against LIVE_BASELINE.json.'],
    'deck_documents': [deck_document], 'game_documents': games, 'prepared_counts': counts,
    'live_baseline_counts': {'games': baseline['game_count'], 'decks': baseline['deck_count']},
    'expected_counts_if_baseline_unchanged': {'games': baseline['game_count'] + 4, 'decks': baseline['deck_count'] + 1,
        'wins': baseline['summary_counts']['wins'] + counts['wins'],
        'losses': baseline['summary_counts']['losses'] + counts['losses'],
        'concession_wins': baseline['summary_counts']['concession_wins'] + counts['opponent_concessions']},
    'accepted_packet_refs': [str(BATCH / name / 'LEAD_ACCEPTANCE.json') for name in NAMES]})
table = ['| Video | Opponent | Result | Turns | Review |', '|---|---|---|---:|---|']
for row in accepted:
    stem = Path(row['source_video']).stem
    label = 'Win' if row['owner_result'] == 'win' else 'Loss'
    table.append(f"| {row['source_video']} | {row['opponent']} | {label} | {row['turns']} | [Full review]({stem}/REVIEW.md) |")
text = ('# October 12 video batch\n\nAll four requested recordings have complete, independently checked local reviews, completion events and hash-preserving archival to Reviewed.\n\n'
        + '\n'.join(table) + '\n\n'
        + f"Batch results: {counts['wins']} wins, {counts['losses']} loss. Two wins have explicit opponent concessions. The Hons win has last observed points 0-1, separate from the unopened detailed result statistics. All four filmed QR codes identify the same 20-card Darkness deck.\n\n"
        + 'The added loss has a retained owner-concession confirmation and Defeat sequence. Native opening hands, draw-relative crops and one structured row per turn are retained. Hidden cards, overlapping fans and unopened discard piles remain explicit limits.\n\n'
        + 'Pause Games import is prepared in PAUSE_GAMES_BATCH_IMPORT.json and has not been sent or saved online. The artifact lacks an Add Deck control, so importing this new deck needs a message to its existing Claude task and explicit owner authorization. These human event games do not enter the Ladder Log.\n\n'
        + f'Storage release is verified for {online_only_count} of four archived originals. See FINAL_STORAGE_CHECK.json for in-sync flags, online-only state and allocated bytes. No video was deleted. Written packets and retained evidence are mirrored into Pocket Deck Lab/Boss Folder/BATCH_2026-10-12_NEW_LONG_VIDEOS.\n')
(BATCH / 'README.md').write_text(text, encoding='utf-8')
subprocess.run([sys.executable, '-X', 'utf8', str(BATCH / 'prepare_message.py')], check=True)
destination = BOSS / BATCH.name
assert destination.parent == BOSS and not destination.exists(), 'Inspect existing mirror instead of overwriting it'
assert not any(path.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi'] for path in BATCH.rglob('*') if path.is_file()), 'Keep original videos outside the written-evidence mirror'
shutil.copytree(BATCH, destination, ignore=shutil.ignore_patterns('__pycache__'))
files = []
for path in sorted(BATCH.rglob('*')):
    if path.is_file():
        relative = path.relative_to(BATCH)
        if '__pycache__' in relative.parts:
            continue
        expected = digest(path)
        assert digest(destination / relative) == expected
        files.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': expected})
receipt = {'copied_utc': datetime.now(timezone.utc).isoformat(), 'source': str(BATCH),
    'destination': str(destination), 'file_count': len(files), 'all_copy_hashes_match': True,
    'videos_copied': 0, 'files': files}
save('MIRROR_RECEIPT.json', receipt)
shutil.copy2(BATCH / 'MIRROR_RECEIPT.json', destination / 'MIRROR_RECEIPT.json')
print(json.dumps({'counts': counts, 'local_complete': True, 'mirror_hashes_match': True, 'external_saved': False}))
