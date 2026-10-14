import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).parent
def load(n):return json.loads((p/n).read_text())
def save(n,x):(p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return f'f{t:07.2f}'
def readable(x):
 x=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',x);x=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',x);x=re.sub(r'\bT (?=\d)','T',x)
 return x
ledger=load('TURN_LEDGER.json')
ledger['turns'][0]['draws_and_searches'].insert(0,{'kind':'normal_draw','caused_by':None,'linked_play_order':None,'cards_in_reveal_order':[{'name':None,'reveal_position':1,'source_video':ledger['turns'][0]['source_video'],'timestamp_seconds':46,'evidence_ids':[eid(46)],'basis':'Opponent normal card-back draw in opening turn','limit_reason':'Hidden opponent identity'}],'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':None,'source_video':ledger['turns'][0]['source_video'],'timestamp_seconds':46,'evidence_ids':[eid(46)],'limit_reason':'Exact animation end within42-46 was not separately measured'})
for row in ledger['turns']:
 for a in row['plays_in_order']:a['result']=readable(a['result']);a['hand_count_after']=None
 if row['who_played']=='owner':
  n=row['turn_number'];tm={2:85.5,4:201.5,6:323.5,8:401.8}[n]
  row['automatic_events_in_order'].insert(0,{'event':'Normal Darkness Energy generated','timestamp_seconds':tm,'result':'One current Darkness token available; small preview Darkness remains','evidence_ids':[eid(tm)]})
  if n in [4,6,8]:row['board_at_start']['phase']='clear preplay hand after draw, just before normal Energy generation'
 if row['turn_number']==6:
  row['timing']['before_end_action_seconds']=338;row['timing']['end_after_resolution_seconds']=340
  row['owner_hand_before_end_action']['evidence_ids']=[eid(338)];row['owner_hand_before_end_action']['basis']='Last clear named hand before retreat promotion and immediate End Turn; subsequent339 is Grimer promotion zoom'
  row['owner_hand_end']['evidence_ids']=[eid(340)];row['owner_hand_end']['basis']='Resolved flat hand at340 immediately before opponent banner'
  for c in row['owner_hand_end']['cards_left_to_right']:c['evidence_ids']=[eid(340)]
  for c in row['owner_hand_before_end_action']['cards_left_to_right']:c['evidence_ids']=[eid(338)]
save('TURN_LEDGER.json',ledger)
pg=load('PAUSE_GAME.json');pg['opening']['selected_active']['evidence_ids']=[eid(36)];save('PAUSE_GAME.json',pg)
review=(p/'REVIEW.md').read_text()
review=review.replace('October12,2026','October 12, 2026').replace('nine recorded turns','nine recorded turns').replace('| None to 82 |','| 42 to 82 (draw end unavailable) |')
review=review.replace('Pawniard has zero attached Energy after T4 retreat; retreats with zero Energy payment and promotes Grimer','Pawniard pays the Darkness just attached this turn and promotes Grimer').replace('End without attack or Energy attachment; Darkness left unused','End without attack; current Energy Zone empty')
review=review.replace('T6 Pawniard had spent its sole Darkness in the T4 retreat, so the observed T6 retreat has zero payment. The normal Darkness onT6 is left unused and carries toT8, where it is attached to Grimer.','T6 Pawniard receives one Darkness at 335-336 seconds, then pays that Energy to retreat at 337-339. Its current Energy Zone is empty afterward. T8 generates a fresh Darkness and attaches it to Grimer.')
review=review.replace('T6 retreat payment was checked against Energy state: zero afterT4 payment, not a second Darkness payment.','A rejected draft incorrectly claimed T6 used no Energy and left the token unused. Native335-337 shows the new attachment to Pawniard, and339-340 shows the retreat payment and empty current zone. The earlier eight draft files are preserved in draft_before_t6_correction, and the independent checker also preserves the rejected bytes. Both reviewers corrected this claim before freeze.')
review=review.replace('339,410','338,410').replace('before-end hand views116','before-end hand views116')
# Improve generated prose spacing without changing source filenames, identifiers or hash strings.
out=[]
for line in review.splitlines():
 if not ('20261012_225319000_iOS.MP4' in line or 'SHA-256' in line):line=readable(line)
 line=line.replace('atT','at T').replace('onT','on T').replace('source0-','source 0-').replace('bound byQR','bound by QR')
 out.append(line)
review='\n'.join(out)+'\n'
# Rebuild only T6 table from the corrected ledger so ordering includes the attachment.
lines=review.splitlines()
for i,line in enumerate(lines):
 if line.startswith('| 6 |'):
  aa=ledger['turns'][5]['plays_in_order'];text='; '.join(f"{a['order']}. {a['card_name'] or a['kind']} ({a['timestamp_seconds']}s): {a['result']}" for a in aa)
  lines[i]=f'| 6 | owner | 323 to 340 | {text}. Owner ending hand 2. Ledger row 6. |'
(p/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
coverage=(p/'COVERAGE.md').read_text().replace('duration438','duration 438')
coverage=re.sub(r'\bTurn(?=\d)','Turn ',coverage).replace('source0-','source 0-')
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
e=load('TURN_EVIDENCE.json')
for f in e['frames']:
 tm=f['requested_source_seconds']
 info={86:(True,True,'Selected clear preplay hand'),88:(False,False,'Poké Ball played and zoomed, not start hand'),91:(False,True,'Poké Ball search has already resolved, not start hand'),202:(True,False,'Heavy Helmet inspection zoom before first voluntary play204'),204:(False,False,'Heavy Helmet play zoom has started'),207:(False,False,'Mesagoza use prompt after Helmet play'),324:(True,True,'Normal Energy generation overlay dims view before Mesagoza action'),326:(False,True,'Mesagoza effect already activated, not start hand'),329:(False,False,'Mesagoza coin animation after first action'),402:(False,True,'Poké Ball play has started, hand already loses Ball'),404:(False,True,'Poké Ball search resolving after first play'),407:(False,True,'Glimmet searched already; not original postdraw hand')}.get(tm)
 if info:f['before_first_play'],f['unzoomed'],f['suitability_or_limit']=info;f['hand_spread']=info[1]
 if f['requested_source_seconds']==338:f['role']='before_end_hand';f['who_played']='owner';f['turn_number']=6;f['suitability_or_limit']='Last clear hand before retreat promotion and immediate End Turn'
 if f['requested_source_seconds']==339:f['role']='retreat promotion evidence';f['suitability_or_limit']='Grimer zoom covers board, hand crop remains separately readable'
save('TURN_EVIDENCE.json',e)
print('T6 and pre-generation start boundaries corrected; rejected draft preserved. Ready for validation and independent check.')
