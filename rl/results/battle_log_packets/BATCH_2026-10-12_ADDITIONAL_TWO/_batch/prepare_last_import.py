"""Prepare supported UI fields only after full acceptance and verified archival."""
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
packet = BATCH / '20261012_230258000_iOS'
def read(name):
    return json.loads((packet / name).read_text(encoding='utf-8-sig'))
source = read('SOURCE.json')
summary = read('SUMMARY.json')
game = read('PAUSE_GAME.json')
lead = read('LEAD_ACCEPTANCE.json')
move = read('MOVE_RECEIPT.' + source['video_basename'] + '.json')
assert lead['accepted'] and lead['all_source_games_accepted'] and lead['turn_rows'] == 14
assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
assert summary['opponent'] == 'Giorno'
note = (f"Source: {source['video_basename']}. Game 1 of 1; game ID: {game['game_id']}. Opponent: Giorno. "
        "Owner loss by points: Starmie ex Hydro Splash 90 knocks out Alolan Muk at 548 s; opponent third point 553 s, Defeat 558 s, final statistics 564 s confirm went first, 14 turns, points 2-3 and 160 damage. "
        "The empty-deck notice at 495 s did not end the battle. Muk's suppression enables Regigigas's Giga Turbo; its generated Energy to Muk is Colorless. "
        "Exact 20-card Darkness list matches the filmed QR and live deck snapshot. "
        "Full independently checked review and opening, hand, draw, turn and board evidence: "
        "Recording_QA/BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/ "
        "(REVIEW.md, TURN_LEDGER.json, TURN_EVIDENCE.json, DECK_USED.json, PAUSE_GAME.json). "
        "All times are source-local; exact frame PTS, specific queue, artwork and rarity are unverified. "
        "Hidden opponent cards and unopened discard piles remain unknown. Owner ratings were not supplied.")
assert len(note) <= 1500
prepared = {'prepared_utc': datetime.now(timezone.utc).isoformat(),
            'artifact_url': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
            'source': source['video_basename'], 'source_sha256': source['sha256'],
            'game_id': game['game_id'], 'external_saved': False,
            'requires_before_save': 'Fresh duplicate check by source filename and game identity; verify loss, went first and blank ratings.',
            'fields': {'date': '2026-10-12', 'deck': 'filmed-qr-d8a7167db33b',
                       'deckName': 'Glimmora / Alolan Muk / Kingambit / Regigigas',
                       'result': 'loss', 'first': 'first',
                       'opp': 'Froakie, Greninja, Staryu, Starmie ex', 'ratings': {}, 'note': note}}
target = BATCH / 'PAUSE_GAME_IMPORT_230258.prepared.json'
assert not target.exists()
target.write_text(json.dumps(prepared, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Accepted last-game UI fields prepared.')
