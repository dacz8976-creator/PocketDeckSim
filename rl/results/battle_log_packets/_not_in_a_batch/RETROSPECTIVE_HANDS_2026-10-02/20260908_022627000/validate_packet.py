import json
from pathlib import Path
from PIL import Image
B=Path(__file__).parent
files=['ASSIGNMENT.json','PAUSE_GAME.json','TURN_LEDGER.json','HAND_SUPPLEMENT.json','SOURCE_REFERENCE.json','TURN_EVIDENCE.json','UNCERTAINTIES.json','DECK_USED.json','METRICS.json','MODE_QUESTION.json','ASTRA_QUESTIONS.json']
p={n:json.loads((B/n).read_text(encoding='utf-8-sig')) for n in files}
rows=p['TURN_LEDGER.json']['turns'];assert [x['turn_number'] for x in rows]==list(range(1,19))
h=p['HAND_SUPPLEMENT.json'];assert h['target_turn_numbers']==list(range(1,18,2));assert len(h['target_rows'])==9
e=p['TURN_EVIDENCE.json'];ids={x['evidence_id'] for x in e['frames']};assert len(ids)==124
for f in e['frames']:
 assert Path(f['full_frame_path']).exists()
 with Image.open(f['full_frame_path']) as im:assert im.size==(1170,2532)
 for k,dim in [('bottom_crop',(1170,507)),('top_crop',(1170,550))]:
  with Image.open(f[k]['path']) as im:assert im.size==dim
 assert f['source_sha256']==p['SOURCE_REFERENCE.json']['sha256']
 if f['evidence_id'].startswith('F'):assert f['actual_frame_seconds_if_measured'] is not None
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['evidence_ids','turn_evidence_ids'] and v is not None:
    assert set(v)<=ids,(k,set(v)-ids)
   walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
for x in p.values():walk(x)
for row in rows:
 if row['turn_number']%2:
  for k in ['owner_hand_start','owner_hand_end']:
   hs=row[k];assert hs['count']==len(hs['cards_left_to_right']);assert all(x['name'] for x in hs['cards_left_to_right'])
  assert row['opponent_hand_at_owner_turn_start']['count'] is not None
 for k in ['board_at_start','board_after']:
  for s in ['owner','opponent']:
   bd=row[k][s];assert bd['energy_zone']['next']['count']==1
   for pk in [bd['active']]+bd['bench_in_position_order']:
    if pk:assert pk['hp_now']<=pk['hp_max'];assert pk['attached_energy']['total']==sum(pk['attached_energy']['by_type'].values())
assert p['METRICS.json']['new_native_frames']==72
assert p['SOURCE_REFERENCE.json']['verification_status']=='verified_sha256_match'
assert p['DECK_USED.json']['cards_in_log_order'] is None
assert all(x['capture_status']=='complete_with_recording_limits' for x in [p['PAUSE_GAME.json'],h,p['TURN_LEDGER.json']])
out={'status':'passed_packet_structure_and_evidence_paths','turn_rows':18,'owner_targets':9,'native_references':124,'new_native_frames':72,'native_dimensions':[1170,2532],'all_referenced_ids_and_paths_exist':True,'independent_source_acceptance':'pending; structural validation is not independent source acceptance'}
(B/'PACKET_VALIDATION.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
