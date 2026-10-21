"""Prepare accepted source-bound entries; does not send them or claim a fresh baseline."""
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
names = read(B / 'OWNER_CONTEXT.json')['selected_sources']
notes = read(B / 'IMPORT_SOURCE_NOTES.json')
historical = read(B / 'HISTORICAL_DECK_CATALOG.json')
games = []
decks = {}
for name in names:
    p = B / Path(name).stem
    source = read(p / 'SOURCE.json')
    lead = read(p / 'LEAD_ACCEPTANCE.json')
    summary = read(p / 'SUMMARY.json')
    game = read(p / 'PAUSE_GAME.json')
    binding = read(p / 'DECK_USED.json')
    qr = read(p / 'QR_DECODE.json')
    assert lead['accepted'] and lead['source_sha256'] == source['sha256']
    assert summary['classification'] in ['human', 'human_battle', 'human_event_battle'] and summary['auto_option_visible'] is False
    move = read(p / ('MOVE_RECEIPT.' + name + '.json'))
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
    code = qr['payload']
    assert qr['card_slot_count'] == 20 and qr['source_sha256'] == source['sha256']
    found = [d for d in historical['decks'] if d['code'] == code]
    assert len(found) == 1, 'Resolve exact filmed deck before import'
    deck = found[0]
    expanded = binding['cards_in_log_order']
    actual_count = binding.get('actual_card_count', len(expanded))
    assert binding['is_template'] is False and len(expanded) == actual_count == 20
    assert sum(int(c[0]) for c in deck['rows']) == 20
    decks[code] = {'name': deck['name'], 'qr_payload': code, 'historical_rows': deck['rows'], 'historical_retrieved_utc': historical['retrieved_utc'], 'slot_count': 20, 'fresh_live_readback': False, 'resolution_required': 'Freshly read the destination deck with this exact QR, verify all20 slots, then use its actual document ID. Do not create a duplicate deck.'}
    n = notes[name]
    result = summary.get('result', summary.get('outcome'))
    assert result == n['result'] and n['result_method'] in ['opponent_concession','owner_concession','opponent_return_timeout','points']
    assert n['first'] in ['first','second']
    log_result = 'concession' if n['result_method'] == 'opponent_concession' else result
    turns = summary.get('turn_count', summary.get('turns_played'))
    narrative = (f"Source: {name}; game1; game ID: {game['game_id']}; opponent: {summary['opponent']}. "
                 f"Owner {result}; ending: {n['result_method']}. Result evidence: {n['result_evidence']} "
                 f"Full source review: {turns} recorded turns, separately accepted. "
                 f"Review/capture evidence: Recording_QA/{B.name}/{Path(name).stem}/REVIEW.md, PAUSE_GAME.json, TURN_LEDGER.json and TURN_EVIDENCE.json. "
                 "Own native QR matches the exact20-card dated historical log snapshot; verify the current saved list before import. "
                 "Source metadata corroborated by phone clock establishes October12 Chicago evening; October13 UTC source name is preserved. "
                 "Hidden opponent cards, unopened discard content, unsupported future Energy counts and printing remain explicit. Ratings unassigned.")
    games.append({'source_video':name,'source_sha256':source['sha256'],'game_number_in_source':1,'game_id':game['game_id'],'exact_game_deck_binding':True,'result_method':n['result_method'],'result_evidence':n['result_evidence'],'deck_selector':{'qr_payload':code,'name':deck['name']},'fields':{'deckName':deck['name'],'date':summary['match_date'],'result':log_result,'first':n['first'],'opp':n['visible_opponent_core'],'ratings':{},'note':narrative}})
doc = {'prepared_utc':datetime.now(timezone.utc).isoformat(),'existing_artifact':historical['artifact_url'],'existing_authoring_task':'https://claude.ai/cowork/cse_01RtxfTEtHtFkw97BA1cpD4b','external_saved':False,'sent_to_claude':False,'fresh_baseline':None,'authority':'Owner asks to finish exactly these six remaining sources, continuing previously approved existing Pause Games destination and workflow.','external_blocker_receipt':'EXTERNAL_ACCESS_BLOCK.json','deck_documents':[],'required_deck_resolution':list(decks.values()),'game_documents':games}
target = B / 'PAUSE_GAMES_BATCH_IMPORT.json'
assert not target.exists(), 'Inspect existing prepared import before replacement'
target.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
message = '''Continue the authorized update to Dustin's existing Pause Games artifact only: https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd.

These six recordings received complete source reviews, separate independent checks, root acceptance, registration and source-hash-preserving archival. Save only the missing accepted games below. Check the destination's current data first. Detect duplicates by exact source filename plus game number, or game ID. Preserve every prior deck, game, rating, note, layout and sharing setting. Use existing data collections and supported fields.

For each deck_selector, resolve the existing actual deck document ID through its exact QR payload and verify its current20-card rows against the dated historical rows below. Set the game's deck field to that resolved ID. A matching visible core alone does not establish the deck. Do not make duplicate decks. If a current list differs, report the difference and preserve the source-bound filmed list; do not silently overwrite existing lists.

Opponent timeout wins are ordinary wins, not opponent concessions. Only an explicit opponent-concession win uses result=concession. An owner concession is a loss and does not increment opponent-concession wins. Notes retain each precise ending and any preterminal versus final displayed point distinction. Opponent field is visible core; actual opponent name is in the note. Ratings remain empty. Source/hash/game identity may also use existing supported provenance fields.

Read back every saved game field and the resolved deck list after reload. Report actual saved IDs and current totals, and confirm all prior data is unchanged. There is no freshly verified baseline for this batch; do not force an expected total. The Ladder Log remains unchanged. Historical deck snapshots below retain their original retrieval time and are not fresh readbacks.

Accepted import JSON:

'''
message += json.dumps({'required_deck_resolution':doc['required_deck_resolution'],'game_documents':games},ensure_ascii=False,indent=2)+'\n'
(B / 'CLAUDE_IMPORT_REQUEST.txt').write_text(message,encoding='utf-8')
print('Prepared all six accepted imports; no external save or send claimed.')
