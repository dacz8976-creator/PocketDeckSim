import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
p=Path(__file__).resolve().parent.parent; o=p/'independent_sol'
sys.path.insert(0,str(p.parents[1]/'BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/qr_runtime'))
import zxingcpp
q=json.loads((p/'QR_DECODE.json').read_text(encoding='utf-8'))
payload=zxingcpp.read_barcodes(Image.open(p/'turn_evidence/t0000.00.jpg'))[0].text
cat=json.loads((p.parent/'LIVE_DECK_CATALOG.json').read_text(encoding='utf-8'))
d=json.loads((p/'DECK_USED.json').read_text(encoding='utf-8'))
assert payload==q['payload']==d['filmed_qr_exact20']['payload']
assert len(q['decoded']['trainerIds'])+len(q['decoded']['pokemonIds'])==20
assert len(d['filmed_qr_exact20']['cards_in_qr_order'])==20
assert sum(x['count'] for x in d['filmed_qr_exact20']['counts_by_name_and_variant'])==20
assert not any(x['code']==payload for x in cat['decks'])
qr={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'source_video':q['source_video'],'source_sha256':q['source_sha256'],'native_frame_sha256':hashlib.sha256((p/'turn_evidence/t0000.00.jpg').read_bytes()).hexdigest(),'payload':payload,'decoded_byte_exactly':True,'semantic_slots':20,'energy':q['decoded']['energy'],'initial_catalog_decks':len(cat['decks']),'absent_in_initial_catalog':True,'semantic_mapping_provenance':'QR_DECODE retained entity mapping; independently verified native QR byte equality, ids/slot/count arithmetic. Exact printing/artwork/rarity unverified.'}
(o/'QR_CHECK.json').write_text(json.dumps(qr,ensure_ascii=False,indent=2),encoding='utf-8')
l=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
for t in l['turns']:
 print('\nTurn',t['turn_number'])
 for key in ['board_at_start','board_after']:
  b=t[key]; parts=[]
  for who in ['owner','opponent']:
   side=b[who]
   cards=([side['active']] if side['active'] else [])+side['bench_in_position_order']
   for c in cards:
    assert c['hp_max']-c['hp_now']==c['damage'], (t['turn_number'],key,c)
    assert sum(c['attached_energy']['by_type'].values())==c['attached_energy']['total'], (t['turn_number'],key,c)
   parts.append(who+':'+str(side['points'])+' '+str([(c['instance_id'],c['hp_now'],c['hp_max'],c['attached_energy']['by_type'],c['special_conditions']) for c in cards])+' EZ:'+str(side['energy_zone']))
  print(key,*parts)
for t in l['turns']:
 if t['who_played']=='owner':
  print('HAND',t['turn_number'],t['owner_hand_start']['count'],t['owner_hand_end']['count'],t.get('hand_reconciliation'))
