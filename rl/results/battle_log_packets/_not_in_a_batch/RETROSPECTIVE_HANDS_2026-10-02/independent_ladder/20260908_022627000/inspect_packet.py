from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
G=P.parents[1]/'20260908_022627000'
def read(n):return json.loads((G/n).read_text(encoding='utf-8-sig'))
S=read('SUBMISSION_AFTER_ASTRA_REPAIR.json');mods=S['astra_reference_repair']['modified_file_sha256'];check=[]
for f in S['files']:
 p=Path(f['path']);expected=mods.get(p.name,f['sha256']);actual=hashlib.sha256(p.read_bytes()).hexdigest();check.append({'file':p.name,'expected':expected,'actual':actual,'match':expected==actual})
(P/'FROZEN_FILE_CHECKS.json').write_text(json.dumps(check,indent=2)+'\n')
print('Frozen files:',all(x['match'] for x in check))
L=read('TURN_LEDGER.json');E=read('TURN_EVIDENCE.json');H=read('HAND_SUPPLEMENT.json')
print('Ledger keys',list(L));print('Hand keys',list(H));print('Evidence keys',list(E));print('Frame example',json.dumps(E['frames'][0]))
def board(b):
 o={}
 for side in ['owner','opponent']:
  q=b[side];cards=[]
  for p in [q['active']]+q['bench_in_position_order']:
   if p:cards.append({k:p.get(k) for k in ['name','bench_position','hp_now','hp_max','attached_energy','tool','special_conditions','active_effects','evidence_ids','status','limit_reason']})
  o[side]={'cards':cards,'zone':q['energy_zone'],'points':q['points']}
 o['stadium']=b.get('stadium');o['evidence_ids']=b.get('evidence_ids');return o
for r in L['turns']:
 print('\nTURN',r['turn_number'],r['who_played'],'TIMING',r['timing'])
 for k in ['owner_hand_start','owner_hand_end','opponent_hand_at_owner_turn_start','draws_and_searches','plays_in_order','automatic_events_in_order','discard_snapshot_ids','limits']:
  print(k,json.dumps(r[k],ensure_ascii=False))
 for k in ['board_at_start','board_after']:print(k,json.dumps(board(r[k]),ensure_ascii=False))
print('HAND_SUPPLEMENT',json.dumps(H,ensure_ascii=False))
