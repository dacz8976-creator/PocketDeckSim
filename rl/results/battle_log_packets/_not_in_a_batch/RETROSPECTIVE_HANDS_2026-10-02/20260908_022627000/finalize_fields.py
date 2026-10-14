import json,datetime
from pathlib import Path
B=Path(__file__).parent
def read(n):return json.loads((B/n).read_text(encoding='utf-8-sig'))
def save(n,x):(B/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
e=read('TURN_EVIDENCE.json')
tops={3:("Team Rocket's Researcher","Professor's Research"),5:('Poké Ball',"Professor's Research"),7:('Copycat',"Professor's Research"),9:("Team Rocket's Goo-zooka","Professor's Research"),11:("Team Rocket's Goo-zooka",'Poké Ball'),13:("Team Rocket's Hypno",'Rare Candy'),15:("Team Rocket's Hypno",'Rare Candy'),17:("Team Rocket's Hypno",'Lucky Ice Pop')}
for d in e['discard_snapshots']:
 n=d['turn_number'];s=d['pile_owner']
 if n in tops:
  d['cards_in_view']=[{'name':tops[n][0 if s=='owner' else 1],'position':'displayed top face of closed discard pile','evidence_ids':d['evidence_ids'],'basis':'native displayed title/art; one visible face does not establish underlying pile'}]
  d['limit_reason']='Only displayed top face is named. Underlying closed pile contents are hidden; no opened/scrollable full-pile enumeration.'
 else:d['limit_reason']='No discarded top face established at this opening anchor; whole-pile inventory is not claimed.'
save('TURN_EVIDENCE.json',e)
m=read('METRICS.json');m['source_work_wall_seconds']=round((datetime.datetime.fromisoformat(m['source_work_finished_utc'])-datetime.datetime.fromisoformat(m['registered_utc'])).total_seconds(),2);m['source_work_wall_basis']='Registration to completed packet UTC; includes initial cloud delivery wait and source verification.';save('METRICS.json',m)
l=read('TURN_LEDGER.json')
for row in l['turns']:
 for d in row['draws_and_searches']:
  if d['kind']=='failed_normal':d['evidence_ids']={13:['F0501.00'],15:['F0590.00'],17:['R0672.00']}[row['turn_number']]
save('TURN_LEDGER.json',l)
h=read('HAND_SUPPLEMENT.json')
for row in h['target_rows']:row['normal_draw']=l['turns'][row['turn_number']-1]['draws_and_searches'][0]
save('HAND_SUPPLEMENT.json',h)
md=(B/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8');md=md.replace('Boundary snapshots precede next-turn generation; generation and attachment are separately recorded.','Start snapshots include normal generation after the draw or failed draw; end snapshots precede next-turn generation. Generation and attachment are separately recorded.');(B/'REVIEW_SUPPLEMENT.md').write_text(md,encoding='utf-8')
