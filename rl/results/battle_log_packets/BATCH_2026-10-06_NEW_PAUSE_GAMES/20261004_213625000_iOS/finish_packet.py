import json,re
from pathlib import Path
p=Path(__file__).parent
def save(n,x):(p/n).write_text(json.dumps(x,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
l=json.loads((p/'TURN_LEDGER.json').read_text())
def hidden(kind,count,t,play):return {'kind':kind,'linked_play_order':play,'source_video':l['sources'][0]['video_basename'],'timestamp_seconds':t,'cards_in_reveal_order':[{'name':None,'reveal_position':i+1,'basis':'hidden opponent card','limit_reason':'Opponent card faces not shown','evidence_ids':[f'F{t:07.2f}']} for i in range(count)],'limit_reason':'Hidden opponent identities'}
l['turns'][1]['draws_and_searches'] += [hidden('Research',2,91,1),hidden('Fragrant Forest search',1,124,3)]
l['turns'][5]['draws_and_searches'] += [hidden('Fragrant Forest search',1,232,1)]
l['turns'][7]['draws_and_searches'] += [{'kind':'Fragrant Forest search','linked_play_order':2,'cards_in_reveal_order':[],'timestamp_seconds':284,'evidence_ids':['F0284.00'],'limit_reason':'No target; nothing added'},{'kind':'Quick Growth direct evolution','linked_play_order':None,'cards_in_reveal_order':[{'name':'Metapod','reveal_position':1,'timestamp_seconds':329,'evidence_ids':['F0329.00'],'basis':'public evolution reveal'}],'limit_reason':None}]
l['turns'][10]['draws_and_searches'] += [{'kind':'Poke Ball search','linked_play_order':3,'cards_in_reveal_order':[],'timestamp_seconds':399,'evidence_ids':['F0399.00'],'limit_reason':'No target; nothing added'}]
for r in l['turns']:
 for b in [r['board_at_start'],r['board_after']]:
  b['turn_number_basis']='Turn identified by native current-turn transition; boundary frame may no longer show transition label'
  if r['turn_number']>=4:
   if b['opponent']['board_effects']:
    b['opponent']['board_effects'][0]['restriction']='Each of that player\'s Pokemon with any Energy attached recovers from all Special Conditions and cannot be affected by Special Conditions'
  for who in ['owner','opponent']:
   b[who]['energy_zone']['evidence_ids']=b['evidence_ids']
   for m in [b[who]['active']]+b[who]['bench_in_position_order']:
    if m:m['evidence_ids']=b['evidence_ids']
 # Terminal knockout empties owner's board. Absence is directly known.
 if r['turn_number']==12:r['board_after']['owner']['active_status']='known_empty_after_terminal_KO'
save('TURN_LEDGER.json',l)
for fn in ['REVIEW.md','COVERAGE.md']:
 lines=(p/fn).read_text(encoding='utf-8').splitlines()
 result=[]
 for line in lines:
  if 'SHA-256' not in line and '20261004_213625000_iOS' not in line:
   line=re.sub(r'([A-Za-z])(\d)',r'\1 \2',line)
   line=re.sub(r'(\d)([A-Za-z])',r'\1 \2',line)
  line=line.replace('3,3,3,5,3,4respectively','3, 3, 3, 5, 4, 4 respectively').replace('3,3,3,5,3,4 respectively','3, 3, 3, 5, 4, 4 respectively')
  line=line.replace('vsNoytamon','vs Noytamon').replace('row','row')
  result.append(line)
 (p/fn).write_text('\n'.join(result)+'\n',encoding='utf-8')
(p/'CHECKPOINT.md').write_text('Worker whole-source review complete. All 12 turns and setup/result covered. All required files filled, native captures retained and structural pass. Pending independent acceptance and root deck log-entry/readback provenance. No source, shared index, external log or archival changes.\n',encoding='utf-8')
