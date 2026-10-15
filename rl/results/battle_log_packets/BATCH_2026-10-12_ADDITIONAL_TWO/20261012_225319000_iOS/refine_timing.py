from pathlib import Path
import json,shutil
p=Path(__file__).parent
old=json.loads((p/'REVIEW_PACKET_HASHES.json').read_text());d=p/'submitted_v1_before_timing_refinement';d.mkdir(exist_ok=True)
for n in list(old['files'])+['REVIEW_PACKET_HASHES.json']:shutil.copy2(p/n,d/n)
def save(n,x):(p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=json.loads((p/'TURN_LEDGER.json').read_text());r=l['turns'][5]
r['timing']['before_end_action_seconds']=339.5
r['board_after']['turn_number_displayed']=7;r['board_after']['phase']='Resolved T6 state at transition into opponent turn7 banner; Energy generation for T7 has not yet occurred'
for field in ['owner_hand_before_end_action','owner_hand_end']:
 r[field]['evidence_ids']=['f0339.50'];r[field]['basis']='Native339.5 flat hand after retreat resolved, immediately before End Turn'
 for c in r[field]['cards_left_to_right']:c['evidence_ids']=['f0339.50']
r['turn_evidence_ids']=sorted(set(r['turn_evidence_ids']+['f0339.50']))
save('TURN_LEDGER.json',l)
e=json.loads((p/'TURN_EVIDENCE.json').read_text())
for f in e['frames']:
 if f['requested_source_seconds']==339.5:f.update(role='before_end_hand',turn_number=6,who_played='owner',unzoomed=True,hand_spread=True,suitability_or_limit='Clear hand and resolved retreat immediately before End Turn')
 if f['requested_source_seconds']==338:f['role']='retreat evidence';f['suitability_or_limit']='Retreat in progress; final before-End hand uses339.5'
save('TURN_EVIDENCE.json',e)
f=p/'REVIEW.md';x=f.read_text().replace('Before-end hand views 116, 244, 338, 410','Before-end hand views 116, 244, 339.5, 410');x+='\nFinal timing refinement: native 339.5 supplies the clear T6 hand immediately before End Turn. The board at 340 is labeled as the resolved T6 state at the transition into the turn 7 banner. The prior submitted bytes and manifest are preserved in submitted_v1_before_timing_refinement.\n';f.write_text(x,encoding='utf-8')
print('Refined T6 end timing and preserved prior frozen bytes.')
