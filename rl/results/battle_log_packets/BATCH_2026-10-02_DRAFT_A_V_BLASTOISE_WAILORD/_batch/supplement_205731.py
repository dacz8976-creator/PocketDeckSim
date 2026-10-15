"""Save new guide observations without changing an accepted first pass."""
import copy
import hashlib
import json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

B=Path(__file__).resolve().parent
P=B/'20261002_205731000_iOS_auto_sol'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (P/'GUIDE_UPDATE_SUBMISSION.json').exists()
sub=read(P/'SUBMISSION.json')
for n,s in sub['files'].items():assert sha(P/n)==s,n
ledger=read(P/'TURN_LEDGER.json');game=read(P/'PAUSE_GAME.json')
native={f['evidence_id']:f for f in read(P/'EXTRACTION_MANIFEST.json')}
stamp=datetime.now(timezone.utc).isoformat()
common={'source_video':sub['source_video'],'source_sha256':sub['source_sha256'],'reviewer':'/root supplemental author','created_utc':stamp,'guide_receipt':'../GUIDE_UPDATE_RECEIPT.json','independent_acceptance_pending':True,'original_submission_manifest':'SUBMISSION.json','original_submission_sha256':sha(P/'SUBMISSION.json')}
chains={'O1':['Carvanha','Mega Sharpedo ex'],'O2':['Alolan Vulpix','Alolan Ninetales ex'],'O3':['Alolan Vulpix','Alolan Ninetales ex'],'O4':['Lapras'],'O5':['Carvanha'],'P1':['Meowth'],'P2':['Frigibax','Arctibax','Baxcalibur'],'P3':['Squirtle','Wartortle','Mega Blastoise ex'],'P4':['Wailmer','Wailord ex'],'P5':['Frigibax','Arctibax']}
chain_evidence={'O1':['F0029.70','F0056.70','F0059.50','F0097.70'],'O2':['F0100.00','F0131.70','F0149.00','F0190.70'],'O3':['F0190.70','F0196.30','F0224.70','F0234.00'],'P2':['F0029.70','F0056.70','F0086.00','F0097.70'],'P3':['F0029.70','F0117.00','F0131.70','F0164.00','F0190.70'],'P4':['F0097.70','F0117.00','F0131.70'],'P5':['F0190.70','F0211.00','F0224.70']}
rows=[]
for r in ledger['turns']:
 if not r['who_played'].startswith('owner'):continue
 board=copy.deepcopy(r['board_at_start'])
 ids=board['evidence_ids'];anchor=native[ids[0]]
 for who in ['owner','opponent']:
  for mon in [board[who]['active']]+board[who]['bench_in_position_order']:
   if mon.get('empty'):continue
   inst=mon['instance_id'];chain=chains[inst]
   below=list(reversed(chain[:chain.index(mon['name'])]))
   earlier=[e for e in chain_evidence.get(inst,[]) if native[e]['actual_frame_seconds_if_measured']<=anchor['actual_frame_seconds_if_measured']]
   mon['fresh_observation']={'evidence_ids':ids,'basis':'Root directly re-inspected this native owner-start board: top-card name, current HP, screen position and exposed attached icons. Maximum HP follows the printed same-recording face; underside identities are recorded history, separately below.','tool_visibility':'No attached Tool badge visible; no Tool attached in covered history.'}
   mon['evolution_stack_below_top_nearest_first']=below
   mon['evolution_stack_basis']='Witnessed same-recording evolution chain; cards below top were not opened at this start frame' if below else 'Basic Pokemon; no prior evolution in recorded history'
   mon['evolution_stack_evidence_ids']=earlier or ids
   mon['evolution_stack_current_view_limit']='Underside card faces not separately exposed; set/rarity variants unverified' if below else None
   mon.pop('field_basis',None)
   mon['limit_reason']='Fresh current board observation plus individually established printed maximum and witnessed evolution history; no inherited estimate from an older review.'
   if inst=='O3' and r['turn_number']==12:
    mon['fresh_observation']['energy_limit']='One Water is partly overlapped by adjacent card; typed total1 follows witnessed T10 attachment and no removal, rather than pretending this frame alone exposes every icon.'
 row={'turn_number':r['turn_number'],'source_video':sub['source_video'],'actual_frame_seconds':anchor['actual_frame_seconds_if_measured'],'requested_seconds':anchor['requested_source_seconds'],'evidence_ids':ids,'fresh_board_observation':board,'decision_maker':{'value':'game Auto','auto_control_present':True,'auto_enabled':True,'evidence_ids':ids,'basis':'Checked Auto control visible in each selected native owner-start frame; primary complete coverage records no toggle or manual override.','observed_override':False,'limit':'No input telemetry; start/covered UI and automated sequence support attribution, not a claim that each invisible tap was witnessed.'},'opponent_opened_discard_count':None,'opponent_discard_count_limit':'No opened pile; visible top cards do not reveal a numeric total.'}
 rows.append(row)
choices=[{'turn_number':13,'kind':'mandatory promotion after owner Active knockout','trigger':'Triple Bombardment KOs O2 pink-art Alolan Ninetales ex','decision_maker':'game Auto','offered_choice_ui':False,'options_on_choice_screen':None,'options_limit':'No separate manual selection prompt appears in retained locator sequence; do not invent buttons/options. Two eligible bench Pokemon are visibly present before knockout.','eligible_candidates_from_visible_board':[{'instance_id':'O3','name':'Alolan Ninetales ex','bench_position':2,'hp_now':150,'water':2},{'instance_id':'O1','name':'Mega Sharpedo ex','bench_position':3,'hp_now':90,'water':3}],'selected_instance':'O3','selected_name':'Alolan Ninetales ex','selection_source_seconds_range':[258,261],'evidence_ids':['F0247.00','F0261.00','F0270.70'],'locator_evidence':['locator_scan/grid_240_259.jpg','locator_scan/grid_260_279.jpg'],'basis':'Native247 shows both eligible bench cards; nominal258-259 shows Ninetales promotion animation, native261 selected Active; no choice UI shown.','time_limit':'Onset bracket from reduced locator, not exact user input PTS; native261 is measured outcome anchor.'}]
supp=dict(common);supp.update({'capture_status':'complete_with_recording_limits','owner_turns':rows,'owner_choices_during_opponent_turns':choices,'other_forced_switches':'No opponent Sabrina/forced-switch action in this recorded fixed-deck battle. Opponent promotions caused by owner KOs are computer choices, separate from owner selections.','inventory_reference':'SEEN_CARD_INVENTORY.json','recording_limits':['Neither player opens a discard pile; pile total counts and full census unavailable.','Evolution stacks are tied to visible same-recording history, not opened underside faces.','Auto action authorship is based on visible checked control and covered sequence, not input telemetry.']})
save(P/'GUIDE_UPDATE_SUPPLEMENT.json',supp)

occ=defaultdict(list);sim=defaultdict(list)
def norm(n):return n.split(' [')[0] if n else None
def add(name,context,ids,turn=None,seconds=None,instance=None):
 name=norm(name)
 if not name:return
 occ[name].append({'context':context,'turn_number':turn,'source_seconds':seconds if seconds is not None else (native[ids[0]]['actual_frame_seconds_if_measured'] if ids else None),'evidence_ids':ids,'instance_id':instance})
for c in game['opening']['cards_left_to_right']:add(c['name'],'five-card opening',c['evidence_ids'],seconds=game['opening']['timestamp_seconds'])
for r in ledger['turns']:
 for phase in ['owner_hand_start','owner_hand_end']:
  h=r[phase]
  if not r['who_played'].startswith('owner'):continue
  names=[norm(c['name'] if isinstance(c,dict) else c) for c in h['cards_left_to_right']]
  for name in names:add(name,phase,h['evidence_ids'],r['turn_number'])
  for name,num in Counter(names).items():
   if num>1:sim[name].append({'count':num,'context':phase,'turn_number':r['turn_number'],'evidence_ids':h['evidence_ids']})
 if r['who_played'].startswith('owner'):
  for d in r['draws_and_searches']:
   for c in d['cards_in_reveal_order']:add(c['name'],d['kind'],c['evidence_ids'],r['turn_number'],c['timestamp_seconds'])
  for a in r['plays_in_order']:
   if a['kind'] in ['item','supporter','bench','evolution','tool','stadium']:add(a['card_name'],'owner '+a['kind'],a['evidence_ids'],r['turn_number'],a['timestamp_seconds'])
 for boundary in ['board_at_start','board_after']:
  owner=r[boundary]['owner']
  for m in [owner['active']]+owner['bench_in_position_order']:
   if not m.get('empty'):add(m['name'],boundary,m.get('evidence_ids',r[boundary]['evidence_ids']),r['turn_number'],instance=m['instance_id'])
minimum={'Carvanha':2,'Mega Sharpedo ex':2,'Alolan Vulpix':2,'Alolan Ninetales ex':2,'Lapras':1,'Misty':2,"Professor's Research":2,'Poké Ball':2,'Copycat':1,'Cyrus':1,'Irida':1,'Elegant Cape':1,'Lucky Ice Pop':1}
proof={'Carvanha':(['F0031.20','F0345.70'],'O1 Carvanha observed before evolution, plus distinct O5 Carvanha visible alongside O1 Sharpedo; its Carvanha remains under evolved O1.'),'Mega Sharpedo ex':(['F0310.70','F0314.70'],'Illustrated Sharpedo in play and regular-art second Sharpedo in hand simultaneously.'),'Alolan Vulpix':(['F0131.70','F0190.70','F0224.70'],'O2 Vulpix evolves T8; distinct O3 Vulpix subsequently in hand/bench while O2 Ninetales remains in play.'),'Alolan Ninetales ex':(['F0056.70','F0247.00'],'Two differently illustrated Ninetales together in hand at T4; later both physically in play.'),'Misty':(['F0345.70'],'Two Misty cards simultaneously in owner hand.'),"Professor's Research":(['F0270.70','F0274.50','F0310.70'],'Illustrated Research played/discarded T14 and regular Research revealed by it; regular Research in hand alongside illustrated discard top at T16.'),'Poké Ball':(['F0224.70','F0234.00','F0310.70','F0314.70'],'First Ball played T12, discarded; second normal draw T16 and played then. No owner shuffle/recycling of discarded Items occurs between. This is a witnessed transaction distinct-copy bound, not a two-face simultaneous fan claim.')}
cards=[]
for name in sorted(occ):
 assert name in minimum,name
 ids,basis=proof.get(name,(occ[name][0]['evidence_ids'],'At least one public face in recording; repeated sightings are not extra copies.'))
 cards.append({'name':name,'minimum_distinct_copies_seen':minimum[name],'copy_count_evidence_ids':ids,'copy_count_basis':basis,'simultaneous_hand_duplicate_observations':sim.get(name,[]),'occurrences':occ[name],'variant_limit':'Mechanical identity and visible art only; physical set/rarity not verified.'})
inventory=dict(common);inventory.update({'status':'source_bound_inventory_pending_independent_supplement_check','cards':cards,'observed_distinct_card_slot_lower_bound':sum(minimum.values()),'visual_inventory_matches_twenty_card_mechanical_list':True,'exact_printing_inventory_verified':False,'count_basis':'All20 mechanical slots supported by simultaneous faces or tracked distinct instances/consumption. Supplied deck counts were not used to fill unseen copies.','owner_stadium_cards_seen':[],'shared_stadium':{'name':'Soothing Shore','played_by':'computer opponent','included_in_owner_inventory':False,'evidence_ids':['F0056.70']},'discard_limit':'Opened discard census absent; public plays and visible top cards are source-bound supplemental sightings only.','not_seen_names_from_supplied_deck':[]})
save(P/'SEEN_CARD_INVENTORY.json',inventory)
lines=['# Seen owner cards','',f"Source: {sub['source_video']}",'','Minimum20 distinct mechanical card slots are supported. This is separate from exact set/rarity verification. No opened discard census was recorded. Soothing Shore belongs to the computer and is excluded from this owner inventory.','','| Card | Minimum copies | Evidence and counting basis |','|---|---:|---|']
for c in cards:lines.append(f"| {c['name']} | {c['minimum_distinct_copies_seen']} | {', '.join(c['copy_count_evidence_ids'])}: {c['copy_count_basis']} |")
(P/'SEEN_CARD_INVENTORY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
lines=['# October 2 evening guide supplement','',f"Source: {sub['source_video']}",'','The accepted first pass remains unchanged. Root freshly inspected every owner-start native board listed below. Printed maxima and evolution stacks retain same-recording provenance; hidden underside faces and unopened discard counts remain limited. Auto is checked at each start, with no covered override. Independent supplemental acceptance is pending.','','| Owner turn | Native requested time | Both-board frame | Decision maker |','|---|---:|---|---|']
for r in rows:lines.append(f"| {r['turn_number']} | {r['requested_seconds']:.2f}s | {r['evidence_ids'][0]} | game Auto |")
lines+=['','T13: two eligible bench cards are visible before knockout, Ninetales150HP/2Water and Sharpedo90HP/3Water. Auto promotes Ninetales around258-261s. No separate selection prompt is shown. See native247/261 and saved locator grids240-279.','','[Seen-card inventory](SEEN_CARD_INVENTORY.md) records supported copy counts, including two differently illustrated Ninetales in one fan and two Misty in the final start hand. Poke Ball uses a distinct-consumption bound, rather than a simultaneous duplicate claim.']
(P/'GUIDE_UPDATE_SUPPLEMENT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
names=['GUIDE_UPDATE_SUPPLEMENT.json','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md']
manifest=dict(common);manifest['files']={n:sha(P/n) for n in names};manifest['required_additions_authored']=True
save(P/'GUIDE_UPDATE_SUBMISSION.json',manifest)
for n,s in sub['files'].items():assert sha(P/n)==s,n
print(json.dumps({'supplement_manifest_sha256':sha(P/'GUIDE_UPDATE_SUBMISSION.json'),'fresh_owner_start_boards':len(rows),'seen_identities':len(cards),'minimum_slots':20,'core_unchanged':True}))
