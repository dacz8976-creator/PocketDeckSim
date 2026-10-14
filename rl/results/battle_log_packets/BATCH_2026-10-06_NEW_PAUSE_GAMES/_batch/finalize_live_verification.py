"""Reconcile source-bound live readback into local receipts and index notes."""
import csv
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

B=Path(__file__).resolve().parent
ROOT=B.parent.parent
sys.path.insert(0,str(ROOT))
from Review_Log.review_log import WriteLock, read_index, index_row

def read(name):
    return json.loads((B/name).read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

decks=read('LIVE_DECK_READBACK.json')
games=read('LIVE_GAME_READBACK.json')
summary=read('LIVE_SUMMARY_READBACK.json')
bundle=read('PAUSE_GAMES_BATCH_IMPORT.json')
notes=read('FINAL_GAME_NOTES.json')
completion=read('BATCH_COMPLETION_CHECK.json')
assert completion['all_requested_local_reviews_complete']
assert decks['reloaded'] and games['reloaded'] and summary['reloaded']
assert len(decks['decks'])==23 and len(decks['checks'])==14
assert all(c[k] for c in decks['checks'] for k in ('found','name','energy','note','cards','code','source'))
assert all(c['total']==20 for c in decks['checks'])
assert len(decks['existing_deck_checks'])==9
assert all(c[k] for c in decks['existing_deck_checks'] for k in ('found','cards','energy'))
assert len(games['games'])==28 and len(games['checks'])==18
assert all(v is True for c in games['checks'] for k,v in c.items() if k!='id')
assert all(c['count']==1 for c in games['existing_game_source_checks'])
assert games['existing_game_results']=={'games':10,'wins':6,'losses':4,'concessions':3}
assert summary['totals']=='28\ngames\n14-14\nwins-losses\n8\nwon by concession'
assert sum(g['qualified'] for g in games['games'])==4
assert len({g['id'] for g in games['games']})==28
assert all(sha(B/name)==digest for name,digest in bundle['source_files_sha256'].items())
for prefix,expected in [('Butterfree / Accelgor',2),('Skarmory ex / Aegislash / Orthworm',1),('Scolipede / Mega Sableye ex',1)]:
    row=next(r for r in summary['rows'] if r['name']==prefix)
    assert f'{expected} with exact deck list unverified' in row['text']
verified=datetime.now(timezone.utc).isoformat()
receipt={'verified_utc':verified,'external_saved_verified':True,'artifact_url':bundle['existing_artifact'],
    'inserted_decks':14,'inserted_games':18,'sources':17,'new_wins':8,'new_losses':10,'new_concession_wins':5,
    'final_decks':23,'final_games':28,'final_wins':14,'final_losses':14,'final_concession_wins':8,
    'exact_game_deck_bindings':14,'qualified_game_deck_bindings':4,'new_ratings_empty':True,
    'reloaded_and_verified':True,'old_deck_lists_and_energy_match_intake_snapshot':True,
    'old_game_source_identities_and_result_totals_match_baseline':True,
    'earlier_whole_database_preservation_report':'CLAUDE_IMPORT_AUDIT.txt: Claude reported all original document fields identical before and after both updates; root independently checked rendered earlier deck lists and game identities/totals.',
    'verified_new_rendered_fields':['game ID uniqueness','deck name','date','result','turn order','opponent visible core','final note','empty ratings','qualified marker'],
    'verified_deck_rendered_fields':['document ID','name','Energy','note','card quantities/names/kinds/version IDs','QR code string','source provenance'],
    'review_sources_unchanged':True,'archive_identity_verified':'BATCH_COMPLETION_CHECK.json',
    'filmed_edit':{'deck_id':'filmed-edit-2c58f9b081c7','energy':'Water','code':'','basis':'continuous filmed edit, final saved list and accepted game 2'},
    'limits':['Four exact 20-card game lists remain unverified and are visibly labeled; candidate-deck Summary records include those games with explicit counts.',
              'QR codes identify playable versions and Energy; filmed artwork and rarity remain unspecified.',
              'Numeric owner ratings were not supplied. Hidden cards and buffered or unrecorded action order remain subject to packet limits.'],
    'proof_screenshot':'PAUSE_GAMES_SAVED.jpg',
    'readback_files':['LIVE_DECK_READBACK.json','LIVE_GAME_READBACK.json','LIVE_SUMMARY_READBACK.json','CLAUDE_IMPORT_AUDIT.txt'],
    'file_hashes':{name:sha(B/name) for name in ['PAUSE_GAMES_BATCH_IMPORT.json','FINAL_GAME_NOTES.json','LIVE_DECK_READBACK.json','LIVE_GAME_READBACK.json','LIVE_SUMMARY_READBACK.json','CLAUDE_IMPORT_AUDIT.txt','PAUSE_GAMES_SAVED.jpg']},
    'game_receipts':[]}
queue=read('PREPARED_GAME_QUEUE.json')
for game in queue['accepted_game_entries']:
    packet=Path(game['packet'])
    per_game={'verified_utc':verified,'external_saved_verified':True,'artifact_url':bundle['existing_artifact'],
        'game_id':game['game_id'],'source_video':game['source_video'],'source_sha256':game['source_sha256'],
        'game_number_in_source':game['game_number_in_source'],'exact_game_deck_binding':game['exact_game_deck_binding'],
        'deck_id':game['prepared_deck_id'] or game['qualified_candidate_QR_deck_id'],
        'rendered_fields_match':True,'ratings_empty':True,'final_note_source':str(B/'FINAL_GAME_NOTES.json'),
        'batch_verification':str(B/'LIVE_SAVE_VERIFICATION.json')}
    path=packet/'EXTERNAL_LOG_VERIFICATION.json'
    path.write_text(json.dumps(per_game,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    receipt['game_receipts'].append(str(path))
(B/'LIVE_SAVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes_receipt=read('FINAL_NOTES_REQUEST_RECEIPT.json')
if 'sent_utc' in notes_receipt:
    notes_receipt['recorded_utc']=notes_receipt.pop('sent_utc')
    (B/'FINAL_NOTES_REQUEST_RECEIPT.json').write_text(json.dumps(notes_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

index_path=ROOT/'BATTLE_REVIEW_INDEX.csv'
with WriteLock(ROOT/'Review_Log'):
    before_bytes=index_path.read_bytes()
    fields,rows=read_index(ROOT)
    before_rows=[r.copy() for r in rows]
    sources=read('OWNER_CONTEXT.json')['selected_sources']
    selected=set(sources)
    assert len(selected)==17
    index_updates=[]
    for source in sources:
        row=index_row(rows,source)
        assert row and row['Status']=='Reviewed' and row['Location']=='Reviewed/'+source
        original=row.copy()
        current=f"Current external status: saved and reloaded in Pause Games at {bundle['existing_artifact']}; verified {verified}. "
        row['Notes']=current+'Earlier registration note: '+row['Notes']
        refs=[str(B/source.removesuffix('.MP4')/'EXTERNAL_LOG_VERIFICATION.json'),str(B/'LIVE_SAVE_VERIFICATION.json')]
        if source=='20261006_012927000_iOS.MP4':
            refs.append(str(B/source.removesuffix('.MP4')/'game_02'/'EXTERNAL_LOG_VERIFICATION.json'))
        row['Review evidence']+=' | '+' | '.join(refs)
        index_updates.append({'source_video':source,'before':original,'after':row.copy()})
    assert [r for r in rows if r['Video'] not in selected]==[r for r in before_rows if r['Video'] not in selected]
    assert all(all(u['before'][k]==u['after'][k] for k in fields if k not in ('Notes','Review evidence')) for u in index_updates)
    backup=B/'INDEX_BEFORE_EXTERNAL_SAVE.csv'
    assert not backup.exists(), 'External index reconciliation is a one-time operation.'
    backup.write_bytes(before_bytes)
    staged=ROOT/('.BATTLE_REVIEW_INDEX.external-'+uuid.uuid4().hex+'.tmp')
    with staged.open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    staged.replace(index_path)
    fields_after,rows_after=read_index(ROOT)
    assert fields_after==fields and rows_after==rows
    (B/'INDEX_EXTERNAL_UPDATE_RECEIPT.json').write_text(json.dumps({'verified_utc':verified,'index_before_sha256':hashlib.sha256(before_bytes).hexdigest(),
        'index_after_sha256':sha(index_path),'changed_sources':17,'changed_columns':['Notes','Review evidence'],
        'status_scope_location_and_unrelated_rows_preserved':True,'review_events_and_frozen_packets_unchanged':True,
        'updates':index_updates},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'live_verified':True,'decks':23,'games':28,'wins':14,'losses':14,'concessions':8,'index_sources_reconciled':17}))
