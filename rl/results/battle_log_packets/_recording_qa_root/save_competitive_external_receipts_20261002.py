"""Record the five-source UI verification actually observed after reload."""
from datetime import datetime, timezone
from intake_competitive_20261002 import BATCH, DESTINATION, packet_for, read, save
from start_competitive_packet import SELECTED

ax = (BATCH / 'PAUSE_GAMES_5_RELOADED.txt').read_text(encoding='utf-8')
totals = {'games': 5, 'wins': 2, 'losses': 3, 'concession_wins': 2}
occurrences = {name: ax.count(name) for name in SELECTED}
assert all(count == 1 for count in occurrences.values())
assert (BATCH / 'PAUSE_GAMES_5_VERIFIED.png').is_file()
timestamp = datetime.now(timezone.utc).isoformat()
name = '20261002_022135000_iOS.MP4'
packet = packet_for(name)
save(packet / 'EXTERNAL_LOG_RECEIPT.json', {
    'source_video': name, 'source_sha256': read(packet / 'SOURCE.json')['sha256'],
    'destination': DESTINATION, 'artifact_title': 'Pause Games',
    'date': '2026-10-01', 'deck': 'Wailord / Indeedee wall',
    'result': 'loss', 'turn_order': 'first',
    'opponent': 'だんくしゅー: Mega Altaria ex x2 / Greninja x2 / Swablu / Chingling',
    'numeric_ratings': None, 'verified_after_reload': True,
    'filename_occurrences_after_reload': occurrences[name],
    'games_before': 4, 'games_after_save': 5, 'batch_games_verified': 5,
    'batch_totals_verified': totals, 'verified_at': timestamp,
    'verification': 'After reload, all five source filenames occurred once, with correct date, deck, result, turn order, opponent, evidence and owner feedback. Summary showed 5 games, 2-3 wins-losses, 2 concession wins; ratings blank.',
    'proof_screenshot': '../BATCH_2026-10-02_COMPETITIVE/PAUSE_GAMES_5_VERIFIED.png'
})
save(BATCH / 'EXTERNAL_BATCH_VERIFICATION.json', {
    'destination': DESTINATION, 'artifact_title': 'Pause Games',
    'verified_after_reload': True, 'totals': totals,
    'source_filenames': list(SELECTED), 'filename_occurrences': occurrences,
    'numeric_ratings': None, 'verified_at': timestamp,
    'proof_screenshot': 'PAUSE_GAMES_5_VERIFIED.png',
    'log_audit': 'PAUSE_GAMES_5_RELOADED.txt',
    'summary_audit': 'PAUSE_GAMES_5_SUMMARY_RELOADED.txt'
})
context = read(BATCH / 'OWNER_CONTEXT.json')
context['fifth_intake_status'] = 'Full review accepted, registered and archived; external entry and five-game totals verified after reload'
context['all_five_external_entries_verified_after_reload'] = True
save(BATCH / 'OWNER_CONTEXT.json', context)
print(totals)
