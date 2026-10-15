"""Source-bound authored observations for Auto1/Auto3/Auto4; core files remain frozen."""
import json, hashlib, sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fid(t):return f'F{t:07.2f}'
# Tuple per observed Pokemon: physical instance, top name, current/max HP, Water count.
# Positions are explicit arrays: Active, then screen-left/middle/right Bench slots.
C='Carvanha'; V='Alolan Vulpix'; N='Alolan Ninetales ex'; M='Mega Sharpedo ex'; L='Lapras'
S='Squirtle'; W='Wailmer'; WX='Wailord ex'; F='Frigibax'; A='Arctibax'; X='Baxcalibur'; T='Wartortle'; MB='Mega Blastoise ex'
def c(i,n,h,m,e):return (i,n,h,m,e)
data={
'205230':{
 'expected_effective':'6a3dd52586d7c5d38b4a3fae3c9e76029d1c75107ee6dfd780ac134795157a9c',
 'rows':[
 (2,37.5,0,[c('owner_carvanha1',C,50,50,0),None,None,None],[c('opponent_squirtle1',S,70,70,0),c('opponent_wailmer1',W,100,100,0),c('opponent_frigibax1',F,60,60,0),None]),
 (4,62,0,[c('owner_carvanha1',C,50,50,1),None,c('owner_lapras1',L,110,110,0),c('owner_vulpix1',V,60,60,0)],[c('opponent_squirtle1',S,40,70,0),c('opponent_wailmer1',WX,250,250,1),c('opponent_frigibax1',F,60,60,0),None]),
 (6,95.3,1,[c('owner_carvanha1',M,190,190,1),None,c('owner_lapras1',L,110,110,0),c('owner_vulpix1',N,150,150,2)],[c('opponent_frigibax1',A,90,90,0),c('opponent_wailmer1',WX,250,250,2),c('opponent_squirtle2',S,70,70,0),None]),
 (8,121,1,[c('owner_vulpix1',N,150,150,2),c('owner_vulpix2',V,60,60,1),c('owner_lapras1',L,110,110,0),c('owner_carvanha1',M,190,190,1)],[c('opponent_frigibax1',X,60,140,0),c('opponent_wailmer1',WX,250,250,3),c('opponent_squirtle2',S,70,70,0),None]),
 (10,149,2,[c('owner_vulpix1',N,150,150,2),c('owner_vulpix2',V,60,60,1),c('owner_lapras1',L,110,110,1),c('owner_carvanha1',M,190,190,1)],[c('opponent_wailmer1',WX,250,250,3),None,c('opponent_squirtle2',T,90,90,1),None]),
 (12,178,2,[c('owner_vulpix1',N,150,150,2),c('owner_vulpix2',V,60,60,1),c('owner_lapras1',L,110,110,2),c('owner_carvanha1',M,190,190,1)],[c('opponent_wailmer1',WX,190,250,3),None,c('opponent_squirtle2',MB,230,230,2),None]),
 (14,199,2,[c('owner_vulpix1',N,150,150,2),c('owner_vulpix2',V,60,60,1),c('owner_lapras1',L,110,110,3),c('owner_carvanha1',M,190,190,1)],[c('opponent_wailmer1',WX,130,250,3),None,c('opponent_squirtle2',MB,230,230,3),None]),
 (16,236,2,[c('owner_vulpix1',N,20,150,2),c('owner_vulpix2',N,150,150,2),c('owner_lapras1',L,110,110,3),c('owner_carvanha1',M,190,190,1)],[c('opponent_squirtle2',MB,230,230,3),None,c('opponent_wailmer1',WX,70,250,1),None])],
 'histories':{
  'owner_carvanha1':[(C,37.5),(M,65.5)],'owner_vulpix1':[(V,62),(N,70.5)],'owner_vulpix2':[(V,121),(N,203.5)],
  'opponent_wailmer1':[(W,37.5),(WX,55.5)],'opponent_frigibax1':[(F,37.5),(A,89.5),(X,113)],
  'opponent_squirtle2':[(S,95.3),(T,141.5),(MB,167.5)]},
 'extra_inspected':[55.5,65.5,70.5,89.5,113,141.5,167.5,203.5,42,254.5],
 'independent_inspected':['independent_sol:F0152.50'],
 'owner_discard_tops':{2:None,4:"Professor's Research",6:"Professor's Research",8:"Professor's Research",10:"Professor's Research",12:'Poké Ball',14:'Poké Ball',16:'Poké Ball'},
 'opponent_discard_tops':{2:'Poké Ball',4:'Poké Ball',6:S,8:S,10:X,12:X,14:X,16:'X Speed'},
 'duplicate_expected':{'Cyrus':1,'Copycat':1,'Misty':2,C:2,N:2,"Professor's Research":1,L:1,V:2,M:2,'Elegant Cape':1,'Poké Ball':1},
 'stadium_first_turn':8, 'cape':False,
 'special_extra_occurrences':[("Cyrus",254.5,'visible owner discard top after final play')],
 'whole_timeline_limit':'Full 16-turn source-bound core provides action coverage. This supplement freshly inspects every owner start and relevant evolution/reveal anchors; it does not claim a second full frame-by-frame pass.'},
'210612':{
 'expected_effective':'87bc59a20d7950bc2d72befd75510f5725cf19ba669641028da35ef41be405c5',
 'rows':[
 (1,23,0,[c('O-V1',V,60,60,0),None,None,None],[c('P-S1',S,70,70,0),None,None,None]),
 (3,31.2,0,[c('O-V1',V,60,60,0),None,None,None],[c('P-S1',S,70,70,1),None,None,None]),
 (5,62.2,0,[c('O-V1',N,180,180,1),None,None,None],[c('P-S1',T,90,90,2),None,None,None]),
 (7,90.2,0,[c('O-V1',N,180,180,2),None,None,c('O-C1',C,50,50,0)],[c('P-S1',T,30,90,2),None,c('P-S2',S,70,70,1),None]),
 (9,128.2,1,[c('O-V1',N,180,180,2),None,None,c('O-C1',M,190,190,1)],[c('P-W',W,100,100,1),None,c('P-S2',S,70,70,0),None]),
 (11,155.2,1,[c('O-V1',N,180,180,2),None,c('O-L',L,110,110,1),c('O-C1',M,190,190,1)],[c('P-W',W,40,100,1),None,c('P-S2',S,70,70,1),None]),
 (13,180.2,2,[c('O-V1',N,180,180,2),c('O-V2',V,60,60,1),c('O-L',L,110,110,1),c('O-C1',M,190,190,1)],[c('P-S2',S,70,70,1),None,c('P-F',F,60,60,1),None])],
 'histories':{'O-V1':[(V,23),(N,36)],'O-C1':[(C,90.2),(M,99.5)],'O-V2':[(V,180.2),(N,183.8)],'P-S1':[(S,23),(T,54)]},
 'extra_inspected':[0.5,36,54,99.5,183.8,96.2,134,194.8], 'independent_inspected':[],
 'owner_discard_tops':{1:None,3:None,5:'Misty',7:'Poké Ball',9:"Professor's Research",11:"Professor's Research",13:"Professor's Research"},
 'opponent_discard_tops':{1:None,3:None,5:None,7:None,9:'Poké Ball',11:'Poké Ball',13:W},
 'duplicate_expected':{'Lucky Ice Pop':1,M:2,V:2,'Irida':1,N:2,'Elegant Cape':1,'Misty':1,'Poké Ball':1,"Professor's Research":2,'Copycat':1,L:1,'Cyrus':1,C:1},
 'stadium_first_turn':5,'cape':True,'special_extra_occurrences':[],
 'whole_timeline_limit':'Full 13-turn source-bound core provides action coverage. This supplement freshly inspects every owner start and relevant evolution/reveal anchors; it does not claim a second full frame-by-frame pass.'}
}

data['210952']={
 'effective_name':'SUBMISSION.json','expected_effective':'ae9dbf637c49ecf5f5825338f55efe50aae03c41d905d34256c090677476b955',
 'rows':[
 (2,31.4,0,[c('O-L',L,110,110,0),None,None,None],[c('C-W1',W,100,100,0),None,None,c('C-B',F,60,60,0)]),
 (4,63.3,0,[c('O-L',L,110,110,1),None,None,c('O-N1',V,60,60,0)],[c('C-W1',W,100,100,1),c('C-S',S,70,70,0),None,c('C-B',A,90,90,0)]),
 (6,88.4,0,[c('O-L',L,50,110,2),None,None,c('O-N1',N,150,150,0)],[c('C-W1',W,100,100,3),c('C-S',T,90,90,0),None,c('C-B',X,140,140,0)]),
 (8,141.4,0,[c('O-L',L,110,110,3),None,None,c('O-N1',N,150,150,0)],[c('C-B',X,140,140,1),c('C-S',T,90,90,1),None,c('C-W1',W,50,100,1)]),
 (10,165.4,0,[c('O-L',L,110,110,3),None,c('O-S1',C,50,50,0),c('O-N1',N,150,150,1)],[c('C-B',X,90,140,2),c('C-S',T,90,90,2),c('C-W2',W,100,100,0),c('C-W1',W,70,100,1)]),
 (12,195.4,0,[c('O-L',L,110,110,3),None,c('O-S1',M,190,190,0),c('O-N1',N,150,150,2)],[c('C-W2',W,100,100,0),c('C-S',T,90,90,3),c('C-B',X,20,140,0),c('C-W1',W,90,100,1)]),
 (14,221.4,0,[c('O-L',L,110,110,3),None,c('O-S1',M,190,190,1),c('O-N1',N,150,150,2)],[c('C-W2',W,50,100,1),c('C-S',MB,230,230,3),c('C-B',X,20,140,0),c('C-W1',W,100,100,2)]),
 (16,261.4,1,[c('O-N1',N,150,150,2),c('O-S2',C,50,50,1),c('O-S1',M,190,190,1),None],[c('C-S',MB,230,230,5),None,c('C-B',X,20,140,0),c('C-W1',W,100,100,2)]),
 (18,290.4,1,[c('O-N1',N,20,150,2),c('O-S2',M,190,190,1),c('O-S1',M,190,190,1),c('O-N2',V,60,60,1)],[c('C-S',MB,170,230,5),c('C-B2',F,60,60,0),c('C-B',X,20,140,0),c('C-W1',W,100,100,3)])],
 'histories':{'O-N1':[(V,63.3),(N,65.3)],'O-N2':[(V,290.4),(N,293.4)],'O-S1':[(C,165.4),(M,167.4)],'O-S2':[(C,261.4),(M,266.4)],'C-S':[(S,63.3),(T,74.2),(MB,208.3)],'C-B':[(F,31.4),(A,48.3),(X,74.2)],'C-W1':[(W,31.4),(WX,333.4)],'C-B2':[(F,290.4),(A,327.4)]},
 'extra_inspected':[48.3,65.3,72.2,74.2,167.4,208.3,266.4,293.4,327.4,333.4,251.4,254.3,255.4,256.4,95.2,101.3,106.4,109.3,110.6,343.4,33.4,90.4,96.4,303.4,313.4,339.4],
 'independent_inspected':[],
 'owner_discard_tops':{2:None,4:'Poké Ball',6:'Poké Ball',8:'Lucky Ice Pop',10:'Lucky Ice Pop',12:'Lucky Ice Pop',14:'Lucky Ice Pop',16:L,18:L},
 'opponent_discard_tops':{2:"Professor's Research",4:'Poké Ball',6:'Poké Ball',8:'X Speed',10:'X Speed',12:'Poké Ball',14:'Poké Ball',16:W,18:W},
 'duplicate_expected':{'Irida':1,L:1,'Copycat':1,M:2,"Professor's Research":2,N:2,'Poké Ball':1,V:2,'Lucky Ice Pop':1,'Misty':2,C:2,'Elegant Cape':1,'Cyrus':1},
 'stadium_first_turn':4,'cape':False,'special_extra_occurrences':[],
 'whole_timeline_limit':'Full 19-turn source-bound core supplies action coverage. Fresh native reads cover all nine owner starts, evolution anchors, both Research printings, Lucky Ice Pop resolution, T15 replacement and final bench knockout. This is not a redundant full-video pass.'}

for short,d in data.items():
 if len(sys.argv)>1 and short!=sys.argv[1]:continue
 P=B/f'20261002_{short}000_iOS_auto_sol'
 target_names=['GUIDE_UPDATE_SUPPLEMENT.json','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md','GUIDE_UPDATE_SUBMISSION.json']
 assert not any((P/n).exists() for n in target_names),short
 effective_name=d.get('effective_name','SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')
 assert sha(P/effective_name)==d['expected_effective']
 core=load(P/effective_name)
 frozen={n:sha(P/n) for n in core['files']}
 assert all(v==core['files'][n] for n,v in frozen.items())
 frozen['SUBMISSION.json']=sha(P/'SUBMISSION.json');frozen[effective_name]=sha(P/effective_name)
 ledger=load(P/'TURN_LEDGER.json'); turns={t['turn_number']:t for t in ledger['turns']}
 ev=load(P/'TURN_EVIDENCE.json'); frames={f['evidence_id']:f for f in ev['frames']}
 inspected=[fid(t) for _,t,*_ in d['rows']]+[fid(t) for t in d['extra_inspected']]+d['independent_inspected']
 inspected=list(dict.fromkeys(inspected))
 for id in inspected:
  f=frames[id];assert sha(Path(f['full_frame_path']))==f['full_frame_sha256'],id
 def stamp(id):return frames[id]['actual_frame_seconds_if_measured']
 def bind(ids):return [{'evidence_id':i,'source_seconds':stamp(i)} for i in ids]
 observations=[]; inventory=defaultdict(list); snapshots=[]
 def occurrence(name,context,ids,count=1,status='fresh_native_observation',**kwargs):
  inventory[name].append({'context':context,'count_here':count,'evidence':bind(ids),'status':status,**kwargs})
 for turn,t,points,owner,opponent in d['rows']:
  id=fid(t);o={'turn_number':turn,'source_video':core['source_video'],'source_seconds':stamp(id),'phase':'after draw and before first play','evidence_ids':[id],
      'stadium':{'name':'Soothing Shore' if turn>=d['stadium_first_turn'] else None,'played_by':'opponent' if turn>=d['stadium_first_turn'] else None,'basis':'freshly visible shared Stadium or empty Stadium area','evidence_ids':[id]},
      'points':{'owner':points,'opponent':1 if short=='210952' and turn>=16 else 0,'basis':'freshly counted visible point markers','evidence_ids':[id]},
      'discard_views':{'owner':{'opened':False,'visible_top':d['owner_discard_tops'][turn],'total_count':None},'opponent':{'opened':False,'visible_top':d['opponent_discard_tops'][turn],'total_count':None},'limit':'Only exposed top cards, not opened piles. No visible numeric total; lower stack and duplicate census unavailable.','evidence_ids':[id]}}
  for side,observed_cards in [('owner',owner),('opponent',opponent)]:
   out=[]
   core_side=turns[turn]['board_at_start'][side]
   core_positions={0:core_side['active'],**{c['bench_position']:c for c in core_side['bench_in_position_order']}}
   for pos,v in enumerate(observed_cards):
    if v is None:
     out.append({'position':'Active' if pos==0 else pos,'name':None,'status':'observed_empty','evidence_ids':[id]});continue
    instance,name,hp,maxhp,water=v
    prior=core_positions[pos]
    assert (prior['name'],prior['hp_now'],prior['hp_max'],prior['attached_energy']['total'])==(name,hp,maxhp,water),(short,turn,side,pos)
    hist=d['histories'].get(instance,[(name,t)])
    known=[(n,s) for n,s in hist if s<=t]
    assert known[-1][0]==name,(short,turn,instance)
    under=known[:-1]
    tool='Elegant Cape' if d['cape'] and side=='owner' and instance=='O-V1' and name==N else None
    card={'position':'Active' if pos==0 else pos,'physical_instance':instance,'name':name,'hp_now':hp,'hp_max':maxhp,
      'printed_hp':150 if tool else maxhp,'damage':maxhp-hp,'attached_energy':{'total':water,'by_type':{'Water':water} if water else {},'basis':'fresh count of attached Water icons on this individual Pokemon; not a side total','evidence_ids':[id]},
      'tool':{'name':tool,'status':'visible attached Cape icon' if tool else 'no Tool icon visible','evidence_ids':[id]},
      'special_conditions':[],'special_conditions_basis':'No Special Condition marker visible on this card at the sampled boundary.',
      'evolution_stack':{'top_card':name,'under_top_bottom_to_top':[n for n,s in under],
       'under_top_directly_readable_now':[] if not under else None,
       'basis':'Basic top, no lower evolution cards' if not under else 'same-recording observed earlier top cards and evolution transition/endpoint anchors; lower cards are hidden in this current view',
       'history':[{'top_card':n,'evidence_id':fid(s),'source_seconds':stamp(fid(s))} for n,s in known],
       'limit':None if not under else 'This names the witnessed evolution history, not a new direct read of the hidden lower faces. Set/rarity IDs remain unverified.'},
      'attribute_provenance':{'name_current_hp_position':[id],'energy':[id],'tool':[id],
       'maximum_hp':{'evidence_ids':list(dict.fromkeys([id]+[fid(s) for n,s in known])),
        'basis':'Printed 150 HP plus visible Cape modifier; settled effective full HP 180 is visible in this game.' if tool else 'Printed/full-health maximum established in this same recording; current damage is distinguished from maximum.'}},
      'status':'fresh_native_boundary_read_with_separately_labeled_history','evidence_ids':[id]}
    out.append(card)
    if side=='owner':
     occurrence(name,'board top '+str(card['position']),[id],physical_instance=instance)
     for lower,_ in under:occurrence(lower,'hidden lower evolution card retained in witnessed physical stack',[id]+[fid(s) for n,s in known],status='same_recording_evolution_history',physical_instance=instance)
     if tool:occurrence(tool,'attached Tool icon',[id],physical_instance=instance+'_cape')
   o[side]={'active':out[0],'bench_left_to_right':out[1:]}
  # Freshly read hands above match source-ledger names, but duplicate accounting is independent.
  hand=[x['name'] if isinstance(x,dict) else x for x in turns[turn]['owner_hand_start']['cards_left_to_right']]
  o['owner_hand_for_copy_reconciliation']={'cards_left_to_right':hand,'evidence_ids':[id],'basis':'Freshly read hand names at this same native start view'}
  for name,count in Counter(hand).items():occurrence(name,'owner hand',[id],count=count)
  top=d['owner_discard_tops'][turn]
  if top:occurrence(top,'visible owner discard top only',[id])
  direct=Counter(hand);history_count=Counter(hand)
  for card in [o['owner']['active']]+o['owner']['bench_left_to_right']:
   if not card['name']:continue
   direct[card['name']]+=1;history_count[card['name']]+=1
   for name in card['evolution_stack']['under_top_bottom_to_top']:history_count[name]+=1
   if card['tool']['name']:direct[card['tool']['name']]+=1;history_count[card['tool']['name']]+=1
  if top:direct[top]+=1;history_count[top]+=1
  snapshots.append((id,direct,history_count))
  tm=turns[turn]['timing']
  period=tm.get('turn_interval_seconds',[tm.get('turn_start_seconds_approx',tm.get('turn_start_seconds')),tm.get('end_after_resolution_seconds')])
  o['decision_actor']={'actor':'game Auto','auto_control_present':False if short=='210612' and turn==1 else True,
   'auto_enabled_at_this_start':None if short=='210612' and turn==1 else True,
   'native_control_evidence_ids':[fid(.5),fid(31.2)] if short=='210612' and turn==1 else [id],
   'turn_interval_seconds_approx':period,'classification_basis':'setup Auto On and first subsequent checked in-game control; consistent with source-bound full sequence' if short=='210612' and turn==1 else 'checked Auto control freshly visible at this owner-start frame; full source review records no mode change',
   'observed_control_span_seconds':[.5,31.2] if short=='210612' and turn==1 else [stamp(id),stamp(id)],
   'span_limit':'Control observations are sampled anchors, not continuous input telemetry. No direct input/override can be inferred between frames. T1 start image does not expose the in-game button.' if short=='210612' and turn==1 else 'Start anchor is a point observation. Attribution to the whole turn additionally uses the existing covered sequence with no observed toggle; invisible human input is not certified absent.',
   'mode_changes_or_overrides_observed':[]}
  observations.append(o)

 # Whole-timeline occurrence routing, preserving provenance for records not freshly reread.
 source_occurrences=[]
 for turnrow in ledger['turns']:
  if 'owner' not in turnrow['who_played']:continue
  for tr in turnrow['draws_and_searches']:
   for card in tr['cards_in_reveal_order']:
    if not card.get('name'):continue
    ids=card.get('evidence_ids') or tr['evidence_ids']
    occurrence(card['name'],f"T{turnrow['turn_number']} {tr['kind']} transaction",ids,
      status='source_bound_core_transaction_reconciled_to_fresh_hand_or_board',
      limit='Core transaction timing/reveal order is retained; this occurrence is not asserted as a fresh inspection of every cited reveal frame.')
  for play in turnrow['plays_in_order']:
   name=play.get('card_name')
   if name in d['duplicate_expected'] and play['kind'] not in ('attack','retreat'):
    occurrence(name,f"T{turnrow['turn_number']} {play['kind']} play",play['evidence_ids'],
      status='fresh_anchor' if all(i in inspected for i in play['evidence_ids']) else 'source_bound_core_play_reconciled_to_fresh_hand_or_board',
      limit='Playing or moving a previously seen physical card does not add a copy.')
 for name,t,context in d['special_extra_occurrences']:occurrence(name,context,[fid(t)])
 # Full evolution history includes the final owner turn after its start.
 evolution_history=[]
 for instance,h in d['histories'].items():
  evolution_history.append({'physical_instance':instance,'top_cards_in_order':[{'name':n,'evidence':bind([fid(t)])} for n,t in h],
    'basis':'Freshly inspected same-source prior top card plus evolution animation or endpoint; route reconciled to the full turn ledger.',
    'limit':'An endpoint can establish the new top while lower faces stay hidden. No deck-list-only stack inference.'})
  if instance.startswith('owner') or instance.startswith('O-'):
   for name,t in h:occurrence(name,'physical evolution history',[fid(t)],physical_instance=instance)
 cards=[]
 for name,expected in d['duplicate_expected'].items():
  direct_max=max(s[1][name] for s in snapshots)
  supported_max=max(s[2][name] for s in snapshots)
  research_printing_proof=short=='210952' and name=="Professor's Research"
  if research_printing_proof:supported_max=2
  assert supported_max==expected,(short,name,supported_max,expected)
  sims=[{'evidence':bind([id]),'directly_visible_named_faces_or_tool_icons':direct[name],
         'count_including_retained_witnessed_evolution_stack':hist[name],
         'basis':'Same-frame hand/board/Tool/discard top plus explicitly separated hidden lower evolution cards.'} for id,direct,hist in snapshots if hist[name]>=2]
  cards.append({'name':name,'minimum_distinct_copies_supported':supported_max,
   'maximum_simultaneously_visible_faces_or_tool_icons':direct_max,
   'copy_count_basis':'Two distinct native art printings played: full-art Research at F0033.40 and standard Research at F0090.40; the first remains in discard history. No recycling action in between.' if research_printing_proof else ('Simultaneous visible copies' if direct_max==supported_max else 'Visible copy plus another retained in an independently witnessed evolution stack; hidden lower face not directly visible now'),
   'additional_physical_copy_evidence':bind([fid(33.4),fid(90.4)]) if research_printing_proof else [],
   'simultaneous_duplicate_evidence':sims,'occurrences':inventory[name],
   'printing_limit':'Identity is name/mechanical form; exact set, rarity and cosmetic printings are not exhaustively identified.'})
 assert set(inventory)==set(d['duplicate_expected']),(short,set(inventory)-set(d['duplicate_expected']))
 now=datetime.now(timezone.utc).isoformat()
 common={'source_video':core['source_video'],'source_sha256':core['source_sha256'],'reviewer':'/root/astra_drafta_bounded_repairs','model':'gpt-6-astra','reasoning_effort':'high','created_utc':now}
 inv={**common,'schema':'seen-card-inventory/v1','is_template':False,'owner':'Dacz8976','cards':cards,
   'total_minimum_distinct_owner_deck_cards_seen':sum(x['minimum_distinct_copies_supported'] for x in cards),
   'exact_whole_deck_visually_recovered':False,
   'exact_deck_limit':'Fewer than 20 distinct owner cards are exposed; no complete opened deck/discard census or verified empty-deck closure. DECK_USED.json is the separate supplied 20-card snapshot and is not used to inflate seen counts.',
   'repeated_sighting_policy':'Counts are simultaneous physical lower bounds, not sums of hand draws or repeated sightings. Evolving preserves the lower card; Tools count separately once. Moving or discarding a seen card adds no copy.',
   'copycat_and_recycling_check':'Core full timeline records no Copycat play and no Lucky Ice Pop play or recycle in either of these two games. Auto3 holds one Lucky Ice Pop through every owner start; Auto1 never exposes Lucky Ice Pop. No redraw is counted as a new physical card.',
   'opponent_supplied_shared_cards':[{'name':'Soothing Shore','owner':'opponent','counted_in_owner_inventory':False,'evidence_ids':[fid(d['rows'][-1][1])]}],
   'opened_discard_views':[],'opened_discard_limit':'Neither pile is opened in the reviewed source. Exposed top cards are partial observations only.',
   'energy_limit':'Generated Energy is not a physical deck-card slot and is recorded per Pokemon in the supplement.',
   'scope':d['whole_timeline_limit']}
 choices=[]
 for tr in ledger['turns']:
  if 'owner' in tr['who_played']:continue
  timing=tr['timing'];interval=timing.get('turn_interval_seconds',[timing.get('turn_start_seconds_approx',timing.get('turn_start_seconds')),timing.get('end_after_resolution_seconds')])
  choices.append({'turn_number':tr['turn_number'],'source_interval_seconds_approx':interval,
   'owner_choice_events':[],'owner_knockout_promotion':False,'owner_forced_switch_prompt':False,
   'basis':'Source-bound full reviewed action/automatic-event ledger contains no owner knockout, opponent switch-forcing action or owner choice prompt in this opponent turn; fresh adjacent owner-start board reads agree.',
   'evidence_ids':tr['turn_evidence_ids'],'options_shown':None,'selection':None,'decision_actor':None,
   'limit':'No such decision observed, so no option list is invented. This supplement uses existing whole-turn coverage plus fresh boundary checks, not a repeated full video inspection.'})
 supp={**common,'schema':'guide-update-supplement/v1','is_template':False,
   'scope':'Only this game in the owner-authorized eight-game Draft A computer comparison. Frozen effective core is preserved.',
   'status':'authored_pending_independent_review','original_submission_manifest':{'path':'SUBMISSION.json','sha256':sha(P/'SUBMISSION.json')},
   'effective_core_manifest':{'path':effective_name,'sha256':sha(P/effective_name)},
   'fresh_owner_turn_boards':observations,'physical_evolution_histories':evolution_history,'owner_choices_during_opponent_turns':choices,
   'seen_card_inventory':'SEEN_CARD_INVENTORY.json','routing':{'computer':True,'online_game_entry_requested':False,'destination':'local batch and BATTLE_REVIEW_INDEX only'},
   'source_evidence':[{k:f[k] for k in ('evidence_id','source_video','source_sha256','actual_frame_seconds_if_measured','full_frame_path','full_frame_sha256','native_dimensions')} for id in inspected for f in [frames[id]]],
   'metrics':{'model':'gpt-6-astra','reasoning_effort':'high','fresh_or_same_session_native_images_inspected':len(inspected),'inspected_image_ids':inspected,'new_native_extractions':0,'tokens':None,'dollar_cost':None,'elapsed_seconds':None,'measurement_limit':'Token cost and precise elapsed time were not measured. Some listed images were inspected in the immediately preceding narrow repair and reused without another decode.'},
   'limits':['Lower evolution faces are hidden at current boundaries; named stacks are tied to freshly inspected prior top/evolution anchors.','No opened pile census or opponent discard total is available.','Auto attribution uses visible checked controls and source coverage, not direct input telemetry.','All hidden opponent hand identities remain unknown.',d['whole_timeline_limit']],
   'independent_acceptance':None,'self_acceptance':False}
 if short=='210952':
  inv['copycat_and_recycling_check']='Copycat stays in hand and is never played. One Lucky Ice Pop is seen at T4/T6 starts, then used twice in T6. Heads at F0101.30 returns the same card; its second use reaches Lapras 90 HP at F0106.40, Tails at F0109.30 discards it, and F0110.60 shows it atop the owner discard. Count is one physical card, not two plays.'
  inv['recycling_events']=[{'physical_instance':'owner_lucky_ice_pop_1','name':'Lucky Ice Pop','minimum_copies':1,'turn':6,'events':[
   {'event':'initial held card','evidence':bind([fid(63.3),fid(88.4)])},
   {'event':'first use, heal Lapras from 50 to 70; Heads returns this card','evidence':bind([fid(95.2),fid(101.3)]),'limit':'F0095.20 is the pre-heal play anchor, F0101.30 the Heads result. Exact completed healing frame is retained in full source chronology, not claimed visible in the pre-heal frame.'},
   {'event':'reused same returned card, second heal reaches 90; Tails sends to discard','evidence':bind([fid(106.4),fid(109.3),fid(110.6)])}],
   'no_new_copy_reason':'Only one Ice Pop in the starting hand; printed Heads return text and same-turn sequence reconcile both plays without a new draw. A second copy is not exposed.'}]
  for ch in choices:
   if ch['turn_number']==15:
    opts=[{'bench_position':1,'physical_instance':'O-S2','name':C,'hp_now':50,'water':1}, {'bench_position':2,'physical_instance':'O-S1','name':M,'hp_now':190,'water':1}, {'bench_position':3,'physical_instance':'O-N1','name':N,'hp_now':150,'water':2}]
    evt={'kind':'forced Active replacement after Lapras knockout','decision_actor':'game Auto','source_seconds_bracket':[stamp(fid(254.3)),stamp(fid(256.4))],
     'visible_candidates_left_to_right':opts,'options_shown':'Three remaining Bench Pokemon visible on board; no separate menu or written selection prompt visible in inspected anchors.',
     'selection':{'physical_instance':'O-N1','name':N,'from_bench_position':3,'to':'Active','first_selected_animation_evidence':fid(255.4),'settled_evidence':fid(256.4)},
     'control_evidence':bind([fid(254.3),fid(256.4)]),'evidence':bind([fid(251.4),fid(254.3),fid(255.4),fid(256.4),fid(261.4)]),
     'basis':'Opponent gains its first point, Lapras is in discard and Active empty; right Bench Ninetales enlarges, then occupies Active. Checked Auto is visible immediately around promotion.',
     'limit':'Candidate Energy/HP use last settled board and next start because animation temporarily hides numerical overlays. No exact touch or human input is visible. Options are visible board candidates, not a fabricated dialog.'}
    ch.update(owner_choice_events=[evt],owner_knockout_promotion=True,options_shown=evt['options_shown'],selection=evt['selection'],decision_actor='game Auto',basis=evt['basis'],evidence_ids=[fid(x) for x in [251.4,254.3,255.4,256.4,261.4]],limit=evt['limit'])
   if ch['turn_number']==19:
    ch.update(basis='Final attack knocks out the old Ninetales on the Bench and reaches the win threshold. Owner Active Sharpedo remains at 60 HP; no owner promotion follows a Bench knockout or the terminal result.',evidence_ids=[fid(327.4),fid(339.4),fid(343.4)],limit='Game ends. No owner selection prompt or replacement is observed; no options invented.')
  supp['critical_physical_instance_reconciliation']=[
   {'physical_instance':'O-N1','history':'Original right Vulpix evolves to the dark-background Ninetales, is Auto-promoted after Lapras KO, takes 130 to 20 HP, retreats to middle Bench by paying both Water, receives Turbo Shark Water, heals to 40 under Shore, then is knocked out by final 50 Bench damage. It is distinct from the new right Ninetales.', 'evidence':bind([fid(63.3),fid(65.3),fid(256.4),fid(290.4),fid(303.4),fid(327.4),fid(339.4),fid(343.4)])},
   {'physical_instance':'O-N2','history':'Second Vulpix remains right at T18 start, evolves into light/rainbow Ninetales at 293.4, has two Water and full 150 HP before final attack, survives final Bench damage at 100 HP. Its lower Vulpix is established by same-recording history, not a visible lower face.', 'evidence':bind([fid(290.4),fid(293.4),fid(327.4),fid(339.4)])},
   {'physical_instance':'O-S1','history':'First Carvanha in middle Bench evolves into full-art Sharpedo; replaces the retreating old Ninetales, attacks Baxcalibur and remains Active at 60 HP after final attack. Left regular-art Sharpedo O-S2 remains 190 HP.', 'evidence':bind([fid(165.4),fid(167.4),fid(261.4),fid(266.4),fid(303.4),fid(339.4)])}]
  supp['metrics']['measurement_limit']='Token cost and precise elapsed time not measured. All listed native images were freshly viewed for this supplement; source movie was not reread or rehashed.'
 save(P/'GUIDE_UPDATE_SUPPLEMENT.json',supp);save(P/'SEEN_CARD_INVENTORY.json',inv)
 lines=[f'# Guide update: {core["source_video"]}','',f'Author: gpt-6-astra, high effort. Status: awaiting separate independent review.','',
  'Fresh native reads cover every owner turn start. Bench positions are screen left, middle and right. Each row below gives current/max HP and attached Water; every unlisted slot is explicitly empty in the JSON. Tools, evolution history and evidence are recorded per Pokemon.','',
  '| Turn | Source PTS | Owner Active; Bench 1 / 2 / 3 | Opponent Active; Bench 1 / 2 / 3 | Points |','|---|---:|---|---|---|']
 def boardtext(side):
  def ctxt(c):return 'empty' if not c['name'] else f"{c['name']} {c['hp_now']}/{c['hp_max']} HP, W{c['attached_energy']['total']}"+(' + Cape' if c['tool']['name'] else '')
  return ctxt(side['active'])+'; '+ ' / '.join(ctxt(c) for c in side['bench_left_to_right'])
 for o in observations:lines.append(f"| {o['turn_number']} | {o['source_seconds']} | {boardtext(o['owner'])} | {boardtext(o['opponent'])} | {o['points']['owner']}-{o['points']['opponent']} |")
 lines += ['',f'Soothing Shore is first present at the owner-start snapshot for turn {d["stadium_first_turn"]}, remains in later snapshots, and belongs to the opponent. It is excluded from the owner inventory.','',
  'Every owner turn is attributed to game Auto with the visible control anchor and limits listed in JSON. No toggle or override is observed in the reviewed sequence. '+('The turn 1 start image lacks the in-game button; its attribution uses setup Auto On and the subsequent checked control, explicitly marked as an inference.' if short=='210612' else 'Each owner-start image visibly shows checked Auto.'),'',
  ('On opponent turn 15, Auto promotes the original right Ninetales after Lapras is knocked out. At 254.3 seconds the visible Bench candidates are Carvanha left, Sharpedo middle and Ninetales right. Ninetales enlarges at 255.4 and occupies Active at 256.4. No separate option dialog or human touch is visible. The final turn knocks out that same old Ninetales on the Bench while Active Sharpedo survives at 60 HP; the game ends without another owner choice. All other opponent turns have explicit no-observed-choice records.' if short=='210952' else 'No owner choice during an opponent turn is recorded: no owner Pokemon is knocked out and no opponent forced-switch prompt appears in the full turn account. Per-opponent-turn records retain their source evidence and distinguish absence of an observed event from an invented option list.'),'',
  'Lower evolution faces are not freshly readable in current views. The JSON links each known lower card to its earlier visible top and evolution anchor in this recording. No stack is inferred from the supplied deck list. Neither discard pile is opened; only exposed top cards are named, and discard totals remain unknown.','',
  f'The companion inventory supports at least {inv["total_minimum_distinct_owner_deck_cards_seen"]} distinct owner cards. It does not visually recover the exact 20-card deck. Repeated hand/board sightings are not added together. See SEEN_CARD_INVENTORY.md and its JSON for copy evidence.','',
  'No original movie, frozen core file, external log or shared index was changed. No new frames were extracted. Independent acceptance is pending.','']
 (P/'GUIDE_UPDATE_SUPPLEMENT.md').write_text('\n'.join(lines),encoding='utf-8')
 ilines=[f'# Seen owner cards: {core["source_video"]}','',f'{inv["total_minimum_distinct_owner_deck_cards_seen"]} distinct physical cards are supported as a lower bound. The exact whole deck is not visually recovered. Counts below use simultaneous locations, including separately identified retained evolution cards, rather than adding repeated sightings.','',
  '| Card | Minimum copies | Maximum directly visible together | Copy evidence |','|---|---:|---:|---|']
 for x in cards:
  evidence_ids=[e['evidence'][0]['evidence_id'] for e in x['simultaneous_duplicate_evidence']]
  if not evidence_ids:evidence_ids=[x['occurrences'][0]['evidence'][0]['evidence_id']]
  ilines.append(f"| {x['name']} | {x['minimum_distinct_copies_supported']} | {x['maximum_simultaneously_visible_faces_or_tool_icons']} | {', '.join(evidence_ids)}; {x['copy_count_basis']} |")
 ilines += ['',inv['copycat_and_recycling_check'],'',
  'The JSON routes all owner draw/search/play records from the full reviewed timeline into named occurrences and adds fresh hand/board/Tool/discard-top observations. Each occurrence identifies whether it was freshly read or retained from the source-bound core. Same physical evolution chains retain their basic cards; hidden lower faces are not labeled directly visible.','',
  'Soothing Shore was supplied by the opponent and is excluded. Generated Water is excluded from the deck-card count. No opened discard pile is available, and unseen cards are not added from DECK_USED.json. Exact printings and unseen copy counts remain uncertain.','']
 (P/'SEEN_CARD_INVENTORY.md').write_text('\n'.join(ilines),encoding='utf-8')
 assert all(sha(P/n)==v for n,v in frozen.items()),'core changed'
 for n in ['GUIDE_UPDATE_SUPPLEMENT.json','SEEN_CARD_INVENTORY.json']:load(P/n)
 submission={**common,'schema':'guide-update-submission/v1','status':'pending_independent_review','self_accepted':False,
  'original_submission':{'path':'SUBMISSION.json','sha256':sha(P/'SUBMISSION.json')},
  'effective_core_manifest':{'path':effective_name,'sha256':sha(P/effective_name)},
  'effective_core_files_sha256':core['files'],
  'files':{n:sha(P/n) for n in target_names if n!='GUIDE_UPDATE_SUBMISSION.json'},
  'source_binding':'Frozen source identity reused; original movie not rehashed.',
  'immutable_extraction_manifests':{str(p.relative_to(P)):sha(p) for p in [P/'EXTRACTION_MANIFEST.json']+list(P.glob('independent_*/EXTRACTION_MANIFEST.json'))},
  'validation':{'all_core_hashes_unchanged':True,'all_owner_turns_have_fresh_board_records':len(observations),'all_referenced_inspected_frames_hash_verified':True,'new_frames':0,'copy_lower_bounds_reconciled':True}}
 save(P/'GUIDE_UPDATE_SUBMISSION.json',submission)
 print(json.dumps({'packet':P.name,'owner_turns':len(observations),'minimum_distinct_owner_cards':inv['total_minimum_distinct_owner_deck_cards_seen'],'submission_sha256':sha(P/'GUIDE_UPDATE_SUBMISSION.json')},indent=2))
