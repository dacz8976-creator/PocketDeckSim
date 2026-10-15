"""Prepare the authorized existing-task import only after both final acceptances."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
NAMES = ['20261013_022530000_iOS', '20261013_030351000_iOS']
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

prepared = read(BATCH / 'PREPARED_FILMED_DECK.json')
deck = prepared['deck']
assert sum(c['n'] for c in deck['cards']) == 20
baseline = read(BATCH / 'LIVE_BASELINE.json')
assert baseline['game_count'] == 45 and baseline['deck_count'] == 26
fields = {'name': deck['name'], 'energy': deck['energy'], 'group': 'filmed', 'status': 'active', 'tag': 'Filmed QR', 'order': 201,
          'note': 'Same native QR in both October 12 Chicago evening games. Exact semantic 20-card list and Fighting/Metal Energy verified; filmed artwork and rarity unverified.',
          'code': deck['deck_code'], 'source': 'Two source-bound native QR captures at 0 seconds; provenance in PREPARED_FILMED_DECK.json.', 'cards': deck['cards']}
games = []
cores = ['Mega Scizor ex, Orthworm, Scyther, Revavroom', 'Darkrai, Igglybuff, Koraidon ex']
evidence = ['Explicit opponent concession at 544 seconds, Victory at 550, final result at 559: 12 turns, 2-1, 480 damage, went first.',
            'Cyrus brings the damaged Haxorus Active, Koraidon ex gathers Fighting Energy with Legendary Drive, and World Wrecker knocks it out. Defeat at 625-626: 16 turns, 2-3, 230 damage, went first. The Igglybuff knockout earned one point plus the additional Iris point, taking the owner from 0 to 2.']
for index, name in enumerate(NAMES):
    packet = BATCH / name
    source = read(packet / 'SOURCE.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    game = read(packet / 'PAUSE_GAME.json')
    summary = read(packet / 'SUMMARY.json')
    turns = summary.get('turn_count', summary.get('turns_played'))
    outcome = summary.get('result', summary.get('outcome'))
    move = read(packet / ('MOVE_RECEIPT.' + source['video_basename'] + '.json'))
    assert lead['accepted'] and lead['source_sha256'] == source['sha256']
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
    assert summary['classification'] == 'human' and turns == [12, 16][index]
    assert outcome == ['win', 'loss'][index]
    result = ['concession', 'loss'][index]
    note = (f"Source: {source['video_basename']}; game 1; opponent: {summary['opponent']}. "
            f"Owner {outcome}; {evidence[index]} Full review: {turns} turns. "
            f"Review and capture limits: Recording_QA/{BATCH.name}/{name}/REVIEW.md; PAUSE_GAME.json and TURN_LEDGER.json beside it. "
            "Native QR verifies exact 20-card Haxorus / Dragonair / Druddigon deck and Fighting/Metal Energy. "
            "Date is October 12 in Chicago, confirmed by recording creation metadata; filename retains UTC date. "
            "Hidden cards, unopened discard contents and any unresolved arrival order remain explicit in the packet. Ratings unassigned.")
    games.append({'source_video': source['video_basename'], 'source_sha256': source['sha256'], 'game_number_in_source': 1,
                  'game_id': game['game_id'], 'exact_game_deck_binding': True,
                  'deck_choice_basis': 'Identical native filmed QR at 0 seconds in both clips; semantic 20-card list and Fighting/Metal Energy independently checked.',
                  'result_evidence': evidence[index], 'fields': {'deck': deck['id'], 'deckName': deck['name'], 'date': '2026-10-12',
                  'result': result, 'first': 'first', 'opp': cores[index], 'ratings': {}, 'note': note}})
doc = {'prepared_utc': datetime.now(timezone.utc).isoformat(), 'existing_artifact': prepared['destination'],
       'existing_authoring_task': 'https://claude.ai/cowork/cse_01RtxfTEtHtFkw97BA1cpD4b', 'external_saved': False, 'sent_to_claude': False,
       'authority': 'Continuing the same review and import workflow to the same destination approved by the owner with Yes please finish; latest request retries these two newly uploaded sources.',
       'deck_documents': [{'document_id': deck['id'], 'fields': fields}], 'game_documents': games}
target = BATCH / 'PAUSE_GAMES_BATCH_IMPORT.json'
assert not target.exists(), 'Inspect existing prepared import before replacing it'
target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
message = """Continue updating Dustin's existing Pause Games artifact only: https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd.

Both newest videos have finished full-source reviews, separate independent checks, lead acceptance, registration and hash-preserving archival. Add the missing filmed Haxorus / Dragonair / Druddigon deck and the two accepted games below: one opponent-concession win and one points loss.

Use the existing artifact data collections and supported fields. Preserve the existing HTML, layout, sharing, all decks and all games. Check current data before writing. Reuse a deck only if its QR code is identical. Skip a game already saved by its exact source filename plus game number or game ID. Add only missing entries, with the exact fields below. Ratings stay empty. Existing supported provenance fields may carry the source filename, hash, game number, game ID, deck-list match and binding basis, as in your preceding import. Notes include the outcome evidence and local packet references.

Fresh public baseline: 26 decks and 45 games, 25 wins, 20 losses, 15 opponent-concession wins. Neither source filename nor this QR appeared. If unchanged, expected new totals are 27 decks and 47 games, 26 wins, 21 losses, 16 opponent-concession wins. Report actual saved IDs and totals; do not overwrite old entries to force totals. Read back every new field and compare all old data with your immediately preceding read. Keep the Ladder Log unchanged.

Native QR proves 20 semantic card slots and Fighting/Metal Energy. Card references identify representative playable versions, not filmed artwork or rarity. The opponent fields contain only visible deck cores. The win is an explicit concession at 2-1, not an assumed third point. Iris in the loss grants an additional point for Haxorus's knockout; it is not a damage bonus. Container and stream creation times establish October 12 Chicago evening for both games, despite October 13 UTC filenames.

Reviewed import JSON:

"""
message += json.dumps({'deck_documents': doc['deck_documents'], 'game_documents': games}, ensure_ascii=False, indent=2) + '\n'
(BATCH / 'CLAUDE_IMPORT_REQUEST.txt').write_text(message, encoding='utf-8')
print('Prepared exact authorized import; no external write yet.')
