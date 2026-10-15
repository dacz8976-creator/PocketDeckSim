"""Make a single reviewable, unsent import from completed source-bound packets."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent

def read(name):
    return json.loads((B/name).read_text(encoding='utf-8-sig'))

def digest(name):
    return hashlib.sha256((B/name).read_bytes()).hexdigest()

completion = read('BATCH_COMPLETION_CHECK.json')
assert completion['all_requested_local_reviews_complete'] is True
assert completion['source_count'] == 17 and completion['game_count'] == 18
queue = read('PREPARED_GAME_QUEUE.json')
assert not queue['review_pending_sources']
decks = read('PAUSE_DECKS_IMPORT.json')['documents'] + read('PAUSE_EDITED_DECK_IMPORT.json')['documents']
assert len(decks) == 14 and len({d['document_id'] for d in decks}) == 14
deck_by_id = {d['document_id']: d for d in decks}
for deck in decks:
    assert sum(card['n'] for card in deck['fields']['cards']) == 20

games = []
for row in queue['accepted_game_entries']:
    deck_id = row['prepared_deck_id'] or row['qualified_candidate_QR_deck_id']
    assert deck_id in deck_by_id and row['date'] and row['went'] in ('first','second')
    core = row['visible_opponent_core']
    opponent_cards = ', '.join(core) if isinstance(core,list) else str(core or '')
    assert len(opponent_cards) <= 200 and len(row['note']) <= 1500
    games.append({
        'source_video': row['source_video'],
        'source_sha256': row['source_sha256'],
        'game_number_in_source': row['game_number_in_source'],
        'game_id': row['game_id'],
        'exact_game_deck_binding': row['exact_game_deck_binding'],
        'deck_choice_basis': row['deck_selection_note'],
        'fields': {'deck':deck_id, 'deckName':deck_by_id[deck_id]['fields']['name'],
                   'date':row['date'], 'result':row['artifact_result_choice'],
                   'first':row['went'], 'opp':opponent_cards, 'ratings':{}, 'note':row['note']},
        'external_saved':False})
assert len(games) == 18
baseline = read('EXTERNAL_BASELINE.json')
win_count = sum(g['fields']['result'] in ('win','concession') for g in games)
loss_count = len(games)-win_count
doc = {
    'prepared_utc':datetime.now(timezone.utc).isoformat(),
    'existing_artifact':queue['destination'],
    'external_saved':False,
    'operation':'Prepared only. Preserve every existing deck and game; create only missing definitions, then save only source/game identities absent on fresh readback.',
    'required_before_external_write':['Explicit owner authorization to send the prepared request to Claude.',
        'Fresh live duplicate checks by deck document ID/code and source filename plus game number/game ID.',
        'Reload and verify saved deck definitions, each game and totals.'],
    'deck_documents':decks,
    'game_documents':games,
    'prepared_counts':{'sources':17,'games':18,'decks':14,'filmed_QR_decks':13,'filmed_edit_decks':1,'wins':win_count,'losses':loss_count},
    'earlier_live_baseline':baseline,
    'expected_totals_if_baseline_unchanged':{'games':baseline['game_count']+18,'wins':baseline['wins']+win_count,'losses':baseline['losses']+loss_count},
    'source_files_sha256':{n:digest(n) for n in ['BATCH_COMPLETION_CHECK.json','PREPARED_GAME_QUEUE.json','NEW_DECK_ENTRIES.json','EDITED_DECK_ENTRY.json','PAUSE_DECKS_IMPORT.json','PAUSE_EDITED_DECK_IMPORT.json']}}
(B/'PAUSE_GAMES_BATCH_IMPORT.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bindings = {'prepared_utc':doc['prepared_utc'],'source_acceptance_verified':True,
    'definitions_unchanged':True,'external_saved':False,
    'definitions_sha256':{n:digest(n) for n in ['NEW_DECK_ENTRIES.json','EDITED_DECK_ENTRY.json']},
    'source_acceptance':[{'source_video':r['source_video'],'source_sha256':r['source_sha256'],'game_number_in_source':r['game_number_in_source'],'game_id':r['game_id'],'definition_id':r['prepared_deck_id'],'exact_game_deck_binding':r['exact_game_deck_binding'],'qualified_candidate_definition_id':r['qualified_candidate_QR_deck_id']} for r in queue['accepted_game_entries']]}
(B/'ACCEPTED_DECK_BINDINGS.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(doc['prepared_counts']))
