from pathlib import Path
import json
from PIL import Image
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
L=read('TURN_LEDGER.json');E=read('TURN_EVIDENCE.json');H=read('HAND_SUPPLEMENT.json');M=read('METRICS.json');S=read('SOURCE_REFERENCE.json')
ids={f['evidence_id'] for f in E['frames']};sn={v['snapshot_id'] for v in E['discard_snapshots']}
assert len(ids)==53 and len(E['frames'])==53
assert len(list((P/'turn_evidence').glob('*.jpg')))==50
assert [r['turn_number'] for r in L['turns']]==list(range(1,11))
assert H['target_turn_numbers']==[1,3,5,7,9] and len(H['rows'])==5
def walk(d):
 if isinstance(d,dict):
  for k,v in d.items():
   if k in ['evidence_ids','turn_evidence_ids','selected_start_evidence_ids','before_end_evidence_ids','native_evidence_ids'] and isinstance(v,list):assert set(v)<=ids,(k,set(v)-ids)
   if k=='discard_snapshot_ids' and isinstance(v,list):assert set(v)<=sn
   walk(v)
 elif isinstance(d,list):
  for v in d:walk(v)
for name in ['TURN_LEDGER.json','TURN_EVIDENCE.json','HAND_SUPPLEMENT.json','PAUSE_GAME.json','REVIEW_SUPPLEMENT.json']:
 d=read(name);walk(d);assert 'not_reviewed' not in json.dumps(d)
for f in E['frames']:
 assert f['source_sha256']==S['sha256']
 assert Image.open(f['full_frame_path']).size==(1170,2532)
 assert Image.open(f['bottom_crop']['path']).size==(1170,507)
 assert Image.open(f['top_crop']['path']).size==(1170,582)
for r in L['turns']:
 for k in ['owner_hand_start','owner_hand_end']:
  h=r[k];assert h['count']==len(h['cards_left_to_right'])
 for k in ['board_at_start','board_after']:
  for side in ['owner','opponent']:
   b=r[k][side]
   for p in ([b['active']] if b['active'] else [])+b['bench_in_position_order']:
    assert p['hp_max']-p['hp_now']==p['damage'] and 0<=p['hp_now']<=p['hp_max']
    assert p['attached_energy']['total']==sum(p['attached_energy']['by_type'].values())
assert M['new_native_full_frames']==M['approved_native_cap']==50
report={'status':'passed_structural_consistency','independent_source_acceptance':'pending','checks':['All JSON parse','10 ordered turn rows and5 owner targets','All referenced evidence IDs resolve','50 new native frames within approved50 cap plus3 SHA-bound reused frames','Native dimensions and106 crop dimensions checked','Owner duplicate-preserving hand counts consistent','Recorded HP/damage and Energy type sums consistent'],'not_checked':'This structural check is not independent visual source acceptance.'}
(P/'PACKET_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(P/'FROZEN_FOR_INDEPENDENT_REVIEW.json').write_text(json.dumps({'worker_status':'submitted_and_frozen','capture_status':'complete_with_recording_limits','independent_acceptance_status':'pending','old_packet_unchanged':True,'scope':'No further worker edits after submission; independent reviewers may repair documented fields under lead authorization.'},indent=2)+'\n',encoding='utf-8')
print('Packet structure, evidence links, native dimensions and field arithmetic passed; independent source acceptance pending.')
