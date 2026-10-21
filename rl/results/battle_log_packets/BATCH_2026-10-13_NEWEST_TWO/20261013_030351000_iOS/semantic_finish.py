import json
from pathlib import Path
p=Path(__file__).resolve().parent
f=p/'TURN_LEDGER.json';d=json.loads(f.read_text(encoding='utf-8'));ts=d['turns']
for t in ts:
 t['point_change']=dict(owner_delta=2 if t['turn_number']==15 else 0,opponent_delta=1 if t['turn_number'] in [5,13,16] else 0,owner_total_after=t['board_after']['owner']['points'],opponent_total_after=t['board_after']['opponent']['points'])
 for a in t['plays_in_order']:
  if a['kind']!='attack':continue
  if a['card_name']=='Igglybuff':
   a['attack_name']='Sleepy Lullaby';a['attack_cost']={'Fighting':1};a['energy_attached_before']={'Fighting':1};a['energy_consumed_by_attack']=0
  elif a['card_name']=='Haxorus':
   a['attack_name']='Frenzied Blade';a['attack_cost']={'Fighting':1,'Metal':1,'Colorless':1};a['energy_attached_before']={'Fighting':1,'Metal':2};a['energy_consumed_by_attack']=0
   a['literal_attack_text']="This attack does 20 more damage for each Benched Pok\u00e9mon (both yours and your opponent\u2019s)."
   a['printed_damage']='50+';a['text_evidence_ids']=['f0127.00'];a['damage_dealt']=150
  else:
   a['attack_name']='World Wrecker';a['attack_cost']={'Fighting':3};a['energy_attached_before']={'Fighting':7};a['energy_consumed_by_attack']=0;a['damage_dealt']=110;a['text_evidence_ids']=['f0609.00']
 # First move must be play, not card inspection.
 if t['turn_number']==7:t['timing']['first_voluntary_move_seconds']=252
 if t['turn_number']==9:t['timing']['first_voluntary_move_seconds']=323
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=p/'TURN_EVIDENCE.json';d=json.loads(f.read_text(encoding='utf-8'))
for x in d['frames']:
 if x['turn_number'] in [7,9]:
  first=252 if x['turn_number']==7 else 323
  x['before_first_play']=x['requested_source_seconds']<first
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=p/'REVIEW.md';s=f.read_text(encoding='utf-8')
s=s.replace('T15 has both Haxorus', '[Haxorus\u2019 literal attack text](turn_evidence/t0127.00.jpg) is \u201cThis attack does 20 more damage for each Benched Pok\u00e9mon (both yours and your opponent\u2019s).\u201d Its printed damage is 50+ and its attack cost is Fighting, Metal and Colorless.\n\nT15 has both Haxorus')
for a,b in [('T3 uses the normal','[T3 preplay](turn_evidence/t0117.50.jpg) and [settled placement](turn_evidence/t0121.00.jpg): T3 uses the normal'),('T5 attaches generated','[T5 two-Metal sleeping Active](turn_evidence/t0204.00.jpg): T5 attaches generated'),('T6 Sabrina gives','[Sabrina choice](turn_evidence/t0231.00.jpg): T6 Sabrina gives'),('T9\u2019s two Lucky','[T9 after the defensive switch](turn_evidence/t0350.00.jpg): T9\u2019s two Lucky'),('T11 visibly accepts','[T11 Supporter warning](turn_evidence/t0430.00.jpg): T11 visibly accepts'),('T13 Research finds','[T13 sleeping Druddigon before end](turn_evidence/t0496.00.jpg): T13 Research finds'),('T15 has both Haxorus','[T15 before attack, score 0-2](turn_evidence/t0568.00.jpg) and [two-point award](turn_evidence/t0576.00.jpg): T15 has both Haxorus')]:s=s.replace(a,b)
f.write_text(s,encoding='utf-8')
print('Semantic finish: explicit attack costs, score deltas and decision anchors')
