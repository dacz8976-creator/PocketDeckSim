import json, hashlib, copy
from pathlib import Path
from datetime import datetime, timezone
P=Path(__file__).parent; B=P.parent
V='20261002_205230000_iOS.MP4'; SHA='5e1e5a7a8d7c8a2e9d1e8f69f978d49f2f772fbba3a7fd2c884ae997a3fa1d8c'; G='20261002_205230000_iOS_game1'
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
def write(n,x): (P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def md(n,x): (P/n).write_text(x+'\n',encoding='utf-8')
def fid(t): return f'F{t:07.2f}'
S=[dict(video_basename=V,sha256=SHA,source_json='SOURCE.json')]
manifest=read('EXTRACTION_MANIFEST.json'); bytime={f['requested_source_seconds']:f for f in manifest}
C='Cyrus'; Y='Copycat'; M='Misty'; N='Alolan Ninetales ex'; Q='Mega Sharpedo ex'; U='Alolan Vulpix'; L='Lapras'; R="Professor's Research"; PB='Poké Ball'; CA='Carvanha'; EC='Elegant Cape'
hands={2:[C,Y,M,N,R],4:[C,Y,M,N,Q],6:[C,Y,M,U],8:[C,Y,M,Q],10:[C,Y,M,Q,PB],12:[C,Y,M,Q,CA,EC],14:[C,Y,M,Q,CA,EC,N],16:[C,Y,M,Q,CA,EC,M]}
ends={2:[C,Y,M,N],4:[C,Y,M],6:[C,Y,M],8:[C,Y,M,Q],10:[C,Y,M,Q,CA],12:[C,Y,M,Q,CA,EC],14:[C,Y,M,Q,CA,EC],16:[Y,M,Q,CA,EC,M]}
drawends={2:36.5,4:61,6:95,8:120,10:148,12:177,14:198,16:235}
selected={2:37.5,4:62,6:95.3,8:121,10:149,12:178,14:199,16:236}
before={2:46.5,4:72,6:102,8:123,10:156,12:180,14:204,16:243.5}
endframe={1:34.8,2:49.5,3:57.3,4:84.5,5:91.5,6:105.5,7:116.5,8:137.5,9:144,10:159.5,11:173.5,12:184.5,13:193.5,14:208.5,15:231.5,16:254.5}
startframe={1:22,2:37.5,3:51.8,4:62,5:86.5,6:95.3,7:110,8:121,9:139.5,10:149,11:165,12:178,13:189.5,14:199,15:213.5,16:236}
fans={2:3,4:3,6:2,8:1,10:1,12:1,14:2,16:2}
timings={1:(20,32.8),2:(33,50),3:(50.5,58),4:(58.5,85),5:(85,92.5),6:(92.5,107.5),7:(107.5,117.5),8:(117.5,137),9:(137,145.5),10:(145.5,162),11:(162,174.5),12:(174.5,186.5),13:(186.5,195.5),14:(195.5,210.5),15:(210.5,232.5),16:(232.5,254.5)}
def hand(cards,ev,observed=True):
 return dict(cards_left_to_right=cards,count=len(cards) if cards is not None else None,basis='Visible named hand crop' if observed else 'Carry-forward of visible hand; no owner hand transaction on this opponent turn',evidence_ids=[fid(ev)],status='observed' if observed else 'carried_forward',limit_reason=None if observed else 'This boundary is reconstructed from adjacent named owner-hand observations, not a newly exposed hand.')
def mon(name,hp,maxhp,e,pos=None,effects=None,instance=None):
 return dict(name=name,variant=None,physical_instance=instance or name,bench_position=pos,hp_now=hp,hp_max=maxhp,hp_max_basis='Visible printed card and unchanged effective maximum; no Tool played',damage=maxhp-hp,attached_energy=dict(total=e,by_type={'Water':e}),tool=None,special_conditions=[],active_effects=effects or [],evidence_ids=[],status='observed_and_carried_forward',limit_reason='Printing identity is not established from the log. Attributes reconcile native endpoints and observed actions; a single boundary frame may obscure a label.')
def empty(pos): return dict(name=None,bench_position=pos,status='observed_empty',limit_reason=None)
def zone(count,own,turn,end):
 return dict(this_turn=dict(type='Water' if count else None,count=count,available=bool(count)),next=dict(type='Water',count=1,available=False),basis='Visible Water preview/current orb at retained boundary; active player consumes generated Water by observed attachment. Empty orb has no current Energy type.',evidence_ids=[fid(endframe[turn] if end else startframe[turn])],limit_reason='Opponent preview is small; native upper crops support Water. Non-active current slot is carried from its preceding consumed endpoint. Preview is not available Energy.')
owner={'active':mon(CA,50,50,0,instance='owner_carvanha1'),'bench':[empty(1),empty(2),empty(3)],'points':0}
opp={'active':mon('Squirtle',70,70,0,instance='opponent_squirtle1'),'bench':[empty(1),empty(2),empty(3)],'points':0}
stadium=None
def board(t,end=False):
 ev=fid(endframe[t] if end else startframe[t]); result=dict(turn_number_displayed=t,phase='after attack/effects/checkup/replacement resolved' if end else 'after normal draw, before first play (state reconstructed where animation obscures)',stadium=stadium,shared_effects=[],evidence_ids=[ev])
 for key,state in [('owner',owner),('opponent',opp)]:
  x=copy.deepcopy(state); x['bench_in_position_order']=x.pop('bench'); x['energy_zone']=zone(0 if end or (key=='opponent' and t==1) or (key=='owner' and t%2==1) or (key=='opponent' and t%2==0) else 1,key,t,end); x['board_effects']=[]; x['evidence_ids']=[ev]; x['status']='observed_and_carried_forward'; x['limit_reason']='HP, Energy, positions and effects reconcile physical instances through this turn. Endpoint images during banners may not independently expose all attributes.'
  for m in [x['active']]+x['bench_in_position_order']:
   if m: m['evidence_ids']=[ev]
  result[key]=x
 return result
def play(kind,name,target,result,t,ev,energy=None,nested=None):
 return dict(order=None,kind=kind,card_name=name,target=target,energy=energy or dict(type=None,count=None,destination=None,retreat_payment_by_type=None),result=result,prompt_text=None,response=None,nested_events_in_order=nested or [],hand_count_after=None,source_video=V,timestamp_seconds=t,evidence_ids=[fid(ev)],basis='Native anchor plus ordered one-fps event locator; action time approximate to about one second',limit_reason='Action onset timestamp is approximate; retained decoded frame PTS is exact for its frame.')
def attach(name,t,ev,result='Water attached'):
 return play('energy_attachment',None,name,result,t,ev,dict(type='Water',count=1,destination=name,retreat_payment_by_type=None))
def evolve(a,b,t,ev): return play('evolution',b,a,f'{a} evolves to {b}; damage and attached Energy carried',t,ev)
def draw(name,t,ev,kind='normal_draw',cause='start of turn',order=None,countbefore=None,countafter=None):
 return dict(kind=kind,caused_by=cause,linked_play_order=order,cards_in_reveal_order=[dict(name=name,reveal_position=1,source_video=V,timestamp_seconds=t,evidence_ids=[fid(ev)],basis='Visible draw/reveal and named hand' if name else 'Visible concealed draw animation',limit_reason=None if name else 'Identity remains concealed; fixed deck is not evidence of hand identity.')],hand_count_before=countbefore,hand_count_after=countafter,returned_or_discarded_cards=[],source_video=V,timestamp_seconds=t,evidence_ids=[fid(ev)],limit_reason='Event timestamp approximate; decoded evidence timestamp is separate.')
actions={
1:[play('item',PB,None,'Successful search animation; found card concealed',23.5,26.5),play('bench','Wailmer','opponent bench 1','Bench Wailmer 100 HP',26.5,26.5),play('item',PB,None,'Second successful search animation; found card concealed',28.5,31.5),play('bench','Frigibax','opponent bench 2','Bench Frigibax 60 HP',32,34.8),play('end_turn',None,None,'No attack',32.8,34.8)],
2:[play('supporter',R,None,'Draw Lapras then Alolan Vulpix',38.5,41),play('bench',U,'owner bench 3','Bench first Vulpix',43.5,43.5),play('bench',L,'owner bench 2','Bench Lapras',44.5,44.5),attach('owner Active Carvanha',45.5,45.5),play('attack','Sharp Fang','opponent Active Squirtle','30 damage: 70 to 40 HP',47.5,49.5)],
3:[evolve('opponent bench 1 Wailmer','Wailord ex',54.5,55.5),attach('opponent bench 1 Wailord ex',56.5,56.5),play('end_turn',None,None,'No attack',57.5,57.3)],
4:[evolve('owner Active Carvanha',Q,65,65.5),evolve('owner bench 3 Alolan Vulpix',N,68.5,70.5),attach('owner bench 3 first Alolan Ninetales ex',71.5,71.5),play('attack','Turbo Shark','opponent Active Squirtle','70 damage; KO; owner gains 1 point; Frigibax promoted',73.5,76.5,nested=[dict(order=1,kind='energy_target_prompt',target='owner bench 3 first Alolan Ninetales ex',timestamp_seconds=76.5,evidence_ids=[fid(76.5)],result='Extra Water from Energy Zone attached to Ninetales: 1 to 2 Water'),dict(order=2,kind='knockout_and_promotion',result='Squirtle KO; +1 point; Frigibax becomes Active',evidence_ids=[fid(84.5)])])],
5:[evolve('opponent Active Frigibax','Arctibax',88.5,89.5),attach('opponent bench 1 Wailord ex',89.5,89.5),play('bench','Squirtle','opponent bench 2','Second Squirtle benched',91,91.5),play('end_turn',None,None,'No attack',92,91.5)],
6:[play('bench',U,'owner bench 1','Second Vulpix benched',96,96),attach('owner bench 1 second Alolan Vulpix',98,98),play('retreat',Q,'first Alolan Ninetales ex becomes Active','Free retreat; Mega retains its 1 Water and moves to bench 3',99.5,99.5,dict(type=None,count=0,destination=None,retreat_payment_by_type={})),play('attack','Binding Snow','opponent Active Arctibax','80 damage: 90 to 10; blocks opponent Energy Zone attachment to its Active next turn',103.5,105.5)],
7:[attach('opponent bench 1 Wailord ex',111,113),evolve('opponent Active Arctibax','Baxcalibur',112.5,113),play('stadium','Soothing Shore','Stadium','Stadium placed; Baxcalibur has 60/140 HP from carried 80 damage',114.5,116.5),play('end_turn',None,None,'No attack or visible Ice Maker activation',117,116.5)],
8:[attach('owner bench 2 Lapras',122.5,122.5),play('attack','Binding Snow','opponent Active Baxcalibur','80 damage; KO; +1 point (owner 2); Wailord ex promoted; attachment block renewed',124.5,134)],
9:[evolve('opponent bench 2 Squirtle','Wartortle',140.5,141.5),attach('opponent bench 2 Wartortle',143.5,144),play('end_turn',None,None,'No attack; Wailord has 3 Water and cannot receive Energy Zone attachment to Active this turn',145,144)],
10:[play('item',PB,None,'Search reveals Carvanha',150.5,152),attach('owner bench 2 Lapras',155,155),play('attack','Binding Snow','opponent Active Wailord ex','80 damage: 250 to 170; attachment block renewed',157.5,159.5)],
11:[evolve('opponent bench 2 Wartortle','Mega Blastoise ex',166,167.5),attach('opponent bench 2 Mega Blastoise ex',168,167.5),play('end_turn',None,None,'No attack; Soothing Shore then heals Wailord 170 to 190',170,173.5)],
12:[attach('owner bench 2 Lapras',179.5,179.5),play('attack','Binding Snow','opponent Active Wailord ex','80 damage: 190 to 110; attachment block renewed',182.5,184.5)],
13:[attach('opponent bench 2 Mega Blastoise ex',189,189.5),play('end_turn',None,None,'No attack; Soothing Shore then heals Wailord 110 to 130',191,193.5)],
14:[evolve('owner bench 1 second Alolan Vulpix',N,201.5,203.5),attach('owner bench 1 second Alolan Ninetales ex',203.5,203.5),play('attack','Binding Snow','opponent Active Wailord ex','80 damage: 130 to 50; attachment block renewed',206.5,208.5)],
15:[play('item','X Speed','opponent Active Wailord ex','Retreat cost reduced by 1',213.5,214.5),play('retreat','Wailord ex','Mega Blastoise ex becomes Active','Printed retreat 4, reduced to 3; pays 3 Water, Wailord 3 to 0 Water and moves bench 2',218.5,220.5,dict(type='Water',count=3,destination='discard',retreat_payment_by_type={'Water':3})),attach('opponent bench 2 Wailord ex',222,222.5,'After retreat, generated Water attaches to Wailord: 0 to 1'),play('attack','Triple Bombardment','owner Active first Alolan Ninetales ex','130 damage: 150 to 20; no extra Bench damage; Soothing Shore subsequently heals Wailord 50 to 70',224.5,231.5)],
16:[play('supporter',C,'damaged opponent bench Wailord ex','Forces Wailord 70 HP / 1 Water Active; Mega Blastoise ex moves bench 2',237.5,240),attach('owner bench 3 Mega Sharpedo ex',242.5,243.5),play('attack','Binding Snow','opponent Active Wailord ex','80 damage; Wailord KO awards 2 points, reaches displayed 3; Victory',245,254.5)]}
normalnames={2:R,4:Q,6:U,8:Q,10:PB,12:EC,14:N,16:M}
reveals={2:[draw(L,41,41,'supporter_draw',R,1,4,5),draw(U,42,42,'supporter_draw',R,1,5,6)],10:[draw(CA,152.5,154,'search',PB,1,4,5)]}
def ene(m,n): m['attached_energy']={'total':n,'by_type':{'Water':n}}
def hp(m,n): m['hp_now']=n; m['damage']=m['hp_max']-n
rows=[]; prevhand=[C,Y,M,N]
for t in range(1,17):
 # Binding Snow prohibits attachment to the computer Active for its next turn; old block expires when that turn ends.
 if t%2==0 and opp['active']: opp['active']['active_effects']=[]
 st=board(t); acts=actions[t]
 if t==1: opp['bench']=[mon('Wailmer',100,100,0,1,instance='opponent_wailmer1'),mon('Frigibax',60,60,0,2,instance='opponent_frigibax1'),empty(3)]
 elif t==2: owner['bench']=[empty(1),mon(L,110,110,0,2,instance='owner_lapras1'),mon(U,60,60,0,3,instance='owner_vulpix1')]; ene(owner['active'],1); hp(opp['active'],40)
 elif t==3: opp['bench'][0]=mon('Wailord ex',250,250,1,1,instance='opponent_wailmer1')
 elif t==4: owner['active']=mon(Q,190,190,1,instance='owner_carvanha1'); owner['bench'][2]=mon(N,150,150,2,3,instance='owner_vulpix1'); owner['points']=1; opp['active']=opp['bench'][1]; opp['active']['bench_position']=None; opp['bench'][1]=empty(2)
 elif t==5: opp['active']=mon('Arctibax',90,90,0,instance='opponent_frigibax1'); ene(opp['bench'][0],2); opp['bench'][1]=mon('Squirtle',70,70,0,2,instance='opponent_squirtle2')
 elif t==6: owner['bench'][0]=mon(U,60,60,1,1,instance='owner_vulpix2'); owner['active'],owner['bench'][2]=owner['bench'][2],owner['active']; owner['active']['bench_position']=None; owner['bench'][2]['bench_position']=3; hp(opp['active'],10)
 elif t==7: ene(opp['bench'][0],3); opp['active']=mon('Baxcalibur',60,140,0,instance='opponent_frigibax1'); stadium='Soothing Shore'
 elif t==8: ene(owner['bench'][1],1); owner['points']=2; opp['active']=opp['bench'][0]; opp['active']['bench_position']=None; opp['bench'][0]=empty(1)
 elif t==9: opp['bench'][1]=mon('Wartortle',90,90,1,2,effects=['Shell Shield: prevent attack damage while on Bench'],instance='opponent_squirtle2')
 elif t==10: ene(owner['bench'][1],2); hp(opp['active'],170)
 elif t==11: opp['bench'][1]=mon('Mega Blastoise ex',230,230,2,2,instance='opponent_squirtle2'); hp(opp['active'],190)
 elif t==12: ene(owner['bench'][1],3); hp(opp['active'],110)
 elif t==13: ene(opp['bench'][1],3); hp(opp['active'],130)
 elif t==14: owner['bench'][0]=mon(N,150,150,2,1,instance='owner_vulpix2'); hp(opp['active'],50)
 elif t==15: opp['active'],opp['bench'][1]=opp['bench'][1],opp['active']; opp['active']['bench_position']=None; opp['bench'][1]['bench_position']=2; ene(opp['bench'][1],1); hp(opp['bench'][1],70); hp(owner['active'],20)
 elif t==16: opp['active'],opp['bench'][1]=opp['bench'][1],opp['active']; opp['active']['bench_position']=None; opp['bench'][1]['bench_position']=2; ene(owner['bench'][2],2); opp['active']=None; owner['points']=3
 if t in [6,8,10,12,14] and opp['active']: opp['active']['active_effects']=['Binding Snow: cannot attach Energy from Energy Zone to Active during next opponent turn']
 if t%2==1 and opp['active']: opp['active']['active_effects']=[]
 aft=board(t,True)
 for i,a in enumerate(acts,1): a['order']=i
 if t%2==0:
  counts={2:[4,5,4,4,4],4:[4,3,3,3],6:[3,3,3,3],8:[4,4],10:[4,5,5],12:[6,6],14:[6,6,6],16:[6,6,6]}
  for a,cnt in zip(acts,counts[t]): a['hand_count_after']=cnt
  if t==2: acts[0]['hand_count_after']=6; acts[1]['hand_count_after']=5
  if t==10: acts[0]['hand_count_after']=5
  ds=[draw(normalnames[t],drawends[t]-1,selected[t],countbefore=len(hands[t])-1,countafter=len(hands[t]))]+reveals.get(t,[])
  oh=hand(hands[t],selected[t]); fan=dict(count=fans[t],supported_range=None,count_method='Count visible card backs in native upper fan crop',basis='Direct native fan count',evidence_ids=[fid(selected[t])],limit_reason='Identity of every back remains concealed.')
  prevhand=ends[t]; he=hand(prevhand,before[t]); hs=oh
 else:
  ds=[draw(None,timings[t][0]+1,startframe[t])]
  if t==1:
   ds += [draw(None,24,26.5,'search',PB,1),draw(None,29,31.5,'search',PB,3)]
  oh=hand(prevhand,startframe[t],False); hs=dict(cards_left_to_right=None,count=None,basis='Concealed opponent hand',evidence_ids=[fid(startframe[t])],status='hidden',limit_reason='Do not assign identities from fixed opponent deck.'); fan=None; he=hand(prevhand,endframe[t],False)
 auto=[]
 if t==9: auto.append(dict(order=1,kind='ability',name='Shell Shield',result='Wartortle prevents attack damage while on Bench; no voluntary activation observed',evidence_ids=[fid(141.5)]))
 if t in [11,13,15]: auto.append(dict(order=1,kind='stadium_checkup',name='Soothing Shore',result={11:'Wailord 170 to 190',13:'Wailord 110 to 130',15:'Wailord 50 to 70'}[t],evidence_ids=[fid(endframe[t])]))
 rows.append(dict(turn_number=t,who_played='owner (Auto)' if t%2==0 else 'computer opponent',source_video=V,timing=dict(turn_start_seconds_approx=timings[t][0],draw_animation_end_seconds=drawends.get(t),first_voluntary_move_seconds=acts[0]['timestamp_seconds'],before_end_action_seconds=before.get(t,acts[-1]['timestamp_seconds']),end_after_resolution_seconds=timings[t][1],timestamp_limit='Event boundaries approximate to about one second. Measured selected-frame PTS in evidence manifest is distinct.'),hand_at_start=hs,owner_hand_start=oh,opponent_hand_at_owner_turn_start=fan,draws_and_searches=ds,plays_in_order=acts,automatic_events_in_order=auto,board_at_start=st,board_after=aft,owner_hand_end=he,discard_snapshot_ids=[f'D{t}_{side}' for side in ['owner','opponent']] if t in [4,8,12,16] else [],turn_evidence_ids=sorted(set([fid(startframe[t]),fid(endframe[t])]+[x for a in acts for x in a['evidence_ids']]+([fid(before[t])] if t in before else []))),limits=['No opened discard pile; opponent draw/search identities concealed.','Some board attributes carried through observed actions when animation obscures a boundary.','No visible no-effect attempt or offered/declined Supporter warning; held cards are not recorded as declines.']))
write('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=S,turns=rows,limits=['All 16 turns recorded. Opponent identities hidden except publicly played cards. Action timestamps approximate; native PTS measured.']))
deck=read('DECK_USED.json'); snap=json.loads((B/'OWNER_DECK_SNAPSHOT.json').read_text()); deck.update(is_template=False,game_id=G,sources=S,deck_name_in_log=snap['deck_name_in_log'],captured_at=snap['retrieved_utc'],log_list_version=snap['log_list_version'],cards_in_log_order=snap['cards_in_log_order'],counts_by_name_and_variant=snap['counts_by_name_and_variant'],energy_configuration_from_log=snap['energy_configuration'],actual_card_count=20,capture_source_text_or_image=str(B/'OWNER_DECK_SNAPSHOT.json'),game_version_binding_basis=snap['game_version_binding_basis'],conflicts_with_filmed_cards=[],exact_list_status=snap['exact_list_status'],limits=snap['limits']+['Exact snapshot establishes deck composition, never concealed hands.'])
write('DECK_USED.json',deck)
frames=[]
for f in manifest:
 x=copy.deepcopy(f); tm=x['requested_source_seconds']; t=next((n for n,(a,b) in timings.items() if a<=tm<=b),None); roles=[]
 if tm==14.6: roles=['five_card_opening_before_active_placement']
 if tm==2: roles=['setup_opponent_deck_and_Auto_On']
 if tm==277.5: roles=['terminal_result_summary']
 if t and t%2==0:
  if tm in [drawends[t]+o for o in [1,3,6]]: roles.append('draw_timed_candidate')
  if tm==selected[t]: roles+=['selected_start_hand','opponent_fan_count']
  if tm==before[t]: roles.append('before_attack_hand')
 if t and tm==endframe[t]: roles.append('board_after_resolution')
 if not roles: roles=['event_or_boundary_anchor']
 pre=t in selected and tm==selected[t]; candidate='draw_timed_candidate' in roles
 x.update(role=roles,turn_number=t,who_played=('owner (Auto)' if t%2==0 else 'computer opponent') if t else 'setup or terminal',draw_animation_end_seconds=drawends.get(t),offset_after_draw_seconds=round(tm-drawends[t],2) if t in drawends else None,selected_for_start_hand=bool(pre),before_first_play=bool(pre),unzoomed=True if pre or tm==14.6 else None,hand_spread=True if pre or tm==14.6 else None,observation='All owner hand names read left to right; opponent fan directly counted' if pre else ('Five opening cards exposed before placement' if tm==14.6 else 'Retained event/candidate anchor; use linked ledger for observation'),suitability_or_limit=('Chosen preplay hand; T6 uses dense +0.30 s capture because Auto plays before +1.' if pre else 'Scheduled candidate may already contain a play or resolution and cannot replace the chosen preplay view.' if candidate else 'No blanket claim that every retained full frame was separately inspected.'))
 frames.append(x)
discard=[]
for t in [4,8,12,16]:
 for side in ['owner','opponent']:
  discard.append(dict(snapshot_id=f'D{t}_{side}',turn_number=t,pile_owner=side,source_video=V,timestamp_seconds=None,cards_in_view=None,scroll_coverage=None,full_pile_established=False,evidence_ids=[fid(endframe[t])],limit_reason='No opened discard pile is filmed in the entire recording. Periodic requested full pile snapshot unavailable.'))
for side,t,tm,card in [('owner',2,46.5,R),('opponent',1,31.5,PB),('opponent',4,84.5,'Squirtle'),('opponent',9,144,'Baxcalibur'),('owner',10,159.5,PB),('opponent',15,221.5,'X Speed'),('owner',16,243.5,C),('opponent',16,254.5,'Wailord ex')]:
 discard.append(dict(snapshot_id=f'PARTIAL_{side}_{t}',turn_number=t,pile_owner=side,source_video=V,timestamp_seconds=tm,cards_in_view=[card],scroll_coverage='Visible top card only; unopened pile',full_pile_established=False,evidence_ids=[fid(tm)],limit_reason='Visible top card is partial evidence and cannot establish pile contents or duplicate count.'))
te=read('TURN_EVIDENCE.json'); te.update(is_template=False,game_id=G,sources=S,frames=frames,discard_snapshots=discard,scheduled_capture_limits=['All eight owner turns have +1/+3/+6 candidates and before-attack views. Auto plays before +1 on T6: additional +0.30 s view used. Candidate suitability follows action timing; later candidates may be postplay.','Opening fan is still moving but all five card names are exposed before Carvanha placement.','Native full frames 1170x2532; lower crops 1170x507 and upper crops 1170x550 retain measured pixel bounds.','No opened pile snapshots were recorded.'])
write('TURN_EVIDENCE.json',te)
pg=read('PAUSE_GAME.json'); pg.update(is_template=False,game_id=G,review_date='2026-10-02',sources=S,deck_name='Draft A: Shark Tempo',capture_status='complete_with_recording_limits',battle_review_status='complete_first_pass_pending_independent_acceptance',outcome=dict(result='win',points_owner=3,points_opponent=0,total_turns=16,damage_dealt=580,evidence_ids=[fid(254.5),fid(277.5)]),limits=['Concealed opponent draws/searches and unopened discard piles remain unavailable.','Advanced category comes from owner screenshot receipt; opening recording has no category/difficulty label.'],lead_checked=False)
pg['opening']=dict(source_video=V,timestamp_seconds=14.6,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=[dict(position=i,name=n,basis='Visible exposed opening fan before Active placement',evidence_ids=[fid(14.6)],limit_reason=None) for i,n in enumerate([C,Y,M,CA,N],1)],selected_active=dict(name=CA,opening_position=4,source_video=V,timestamp_seconds=15,evidence_ids=[fid(15),fid(17.9)]),redraw_or_replacement='None observed',before_active_placement=True,status='observed',evidence_ids=[fid(14.6)],limit_reason='Opening cards moving; names readable; no inferred missing slot.')
write('PAUSE_GAME.json',pg)
category=json.loads((B/'ADVANCED_CATEGORY_CONFIRMATION.json').read_text())
summary=dict(game_id=G,source_video=V,source_sha256=SHA,reviewer='/root/drafta_auto_205230',model='gpt-6.1-sol',reasoning_effort='high',classification='computer_battle',ranked_ladder_eligible=False,match_date='2026-10-02',match_date_basis='Owner testimony and filename',owner='Dacz8976',opponent='AI',opponent_deck='Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)',difficulty='Advanced',difficulty_basis=str(B/'ADVANCED_CATEGORY_CONFIRMATION.json'),difficulty_evidence=category,separate_difficulty_selector=False,opening_difficulty_label_visible=False,auto=dict(control_present=True,opening_enabled=True,changes_observed=[],authorship='Owner-side game actions attributed to enabled Auto; separate from computer-opponent classification.',evidence_ids=[fid(2),fid(243.5)],limit='No hidden input can be excluded between retained frames; no observed Auto toggle or manual takeover.'),deck_name='Draft A: Shark Tempo',result='win',owner_points=3,opponent_points=0,turns=16,damage_dealt=580,card_of_game=N,result_evidence_ids=[fid(254.5),fid(277.5)],battle_review_status='complete_first_pass_pending_independent_acceptance',capture_status='complete_with_recording_limits',coverage=dict(start_seconds=0,end_seconds=278.235,uninspected_intervals=[],method='Every retained one-fps locator grid inspected from setup to terminal screen, plus targeted native frames/crops; does not certify every video instant.'),decisive_sequence='Turbo Shark charged first Ninetales to 2 Water; free pivot enabled repeated Binding Snow. Computer built Mega Blastoise on Bench, retreated Wailord with X Speed and hit for 130. Cyrus returned damaged Wailord for the winning 80-damage KO.',unsupported_claims_avoided=['No concealed opponent card identities reconstructed from deck list','No pile census inferred from partial top cards','No held Misty/Copycat/Cape recorded as declined prompts'])
write('SUMMARY.json',summary)
write('UNCERTAINTIES.json',dict(game_id=G,source_video=V,source_sha256=SHA,consequential_unresolved=[],recording_limits=[dict(topic='Opponent hands',status='hidden',detail='Every normal draw and both T1 searches remain unnamed. Only publicly played cards establish identities.'),dict(topic='Discard piles',status='not_shown',detail='Neither pile is opened anywhere. Eight periodic unavailable snapshots and eight partial top-card observations retained.'),dict(topic='Timing',status='approximate_event_boundary',detail='Action and draw-end values approximately one second; decoded native frame PTS measured separately.'),dict(topic='Auto authorship',status='enabled_observed',detail='No toggle or takeover seen. Retained sampling cannot exclude every unseen input.'),dict(topic='Difficulty',status='owner_screenshot_confirmed',detail='Advanced Step-Up Battle category via batch receipt. Category absent on this recording setup screen; no separate selector.'),dict(topic='Physical printings',status='not_established',detail='Deck snapshot variant labels belong to log; filmed artwork may differ.'),dict(topic='Board boundaries',status='carried_forward_attributes',detail='Both boards tracked by physical instance from native endpoints and actions. Some labels obscured by animations; attribute provenance is combined, not all directly visible at each boundary.'),dict(topic='Sampling',status='full_source_locator_coverage',detail='All one-fps locator grids inspected; native details checked selectively. Not a frame-by-frame review.' )]))
lines=['# Turn table',f'Source: {V}. All action times are approximate; native evidence PTS is measured in TURN_EVIDENCE.json.','| Turn | Player | Draw/search | Ordered actions and resolution | Owner hand start → end | Evidence |','|---|---|---|---|---|---|']
for row in rows:
 t=row['turn_number']; ds='; '.join((d['kind']+': '+', '.join(c['name'] or 'concealed' for c in d['cards_in_reveal_order'])) for d in row['draws_and_searches']); acts='; '.join(f"{a['order']}. {a['card_name'] or a['kind']} ({a['timestamp_seconds']}s): {a['result']}" for a in row['plays_in_order']); h=f"{row['owner_hand_start']['count']} → {row['owner_hand_end']['count']}"; lines.append(f"| {t} | {row['who_played']} | {ds} | {acts} | {h} | {', '.join(row['turn_evidence_ids'])} |")
md('TURN_TABLE.md','\n\n'.join(lines[:2])+'\n\n'+'\n'.join(lines[2:]))
md('REVIEW.md',f'''# First-pass battle review

{V}, source SHA256 {SHA}. Reviewer /root/drafta_auto_205230, gpt-6.1-sol, high effort. Full supplied source 0–278.235 s reviewed using all retained one-fps locator grids and targeted native evidence. First pass complete; independent acceptance pending. Capture supplement complete with recording limits.

Dacz8976 wins 3–0 in 16 turns. The terminal result screen at F0277.50 reports 580 damage and Alolan Ninetales ex as card of game. Final Cyrus pulls Wailord ex at 70 HP into the Active position; Binding Snow deals 80, takes the final two points and displays Victory (F0240.00, F0243.50, F0254.50).

This is an Auto-controlled computer battle, excluded from ladder. Setup F0002.00 identifies the fixed Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega), selected Draft A: Shark Tempo and Auto On. Auto remains visibly enabled with no observed changes. Enabled control supports action authorship; computer classification is separately established by AI/setup and owner testimony. Advanced is the Step-Up Battle category verified by the owner's screenshot in ../ADVANCED_CATEGORY_CONFIRMATION.json. This recording's opening does not display a difficulty/category label; there is no separate selector according to the owner.

Opening F0014.60 exposes Cyrus, Copycat, Misty, Carvanha, Alolan Ninetales ex in that order before placement. Auto selects Carvanha, opening position 4, as Active (F0015.00, F0017.90). No redraw is observed. Owner goes second. The exact original 20-card Draft A list with two Misty is preserved in DECK_USED.json with live-log provenance; no filmed conflict is found. The list never establishes a concealed hand.

The early line is Carvanha into Mega Sharpedo ex, while Research draws Lapras then Alolan Vulpix (F0041.00, F0042.00). T2 benches Vulpix before Lapras, attaches Water to Carvanha and deals 30 to Squirtle. T4 evolves Sharpedo and first Ninetales, attaches the ordinary Water to Ninetales, then Turbo Shark deals 70 and attaches one additional Water to the same Ninetales through its nested target choice (F0071.50, F0076.50). Squirtle is knocked out for the first point. Ninetales has two Water, Sharpedo retains one.

T6 first benches the second Vulpix, attaches to it, then retreats Sharpedo for zero Energy payment to Ninetales (F0095.30, F0098.00, F0099.50). Sharpedo retains its Water. Binding Snow deals 80 and blocks Energy Zone attachment to the opponent Active during its next turn. The opponent evolves the damaged Arctibax into Baxcalibur with its damage retained, attaches to Wailord, then places Soothing Shore. T8 Ninetales knocks out Baxcalibur for the second point. Wailord is promoted with three Water.

T10, T12 and T14 repeat Binding Snow, reducing Wailord from 250 to 170, then from 190 to 110, then from 130 to 50. Soothing Shore heals it by 20 at the end of opponent turns 11 and 13. It does not heal the opponent at the end of owner attacks. Wailord cannot receive the fourth Energy from the Energy Zone while Active on the intervening blocked turns, so it does not attack. The computer builds the Squirtle → Wartortle → Mega Blastoise ex line on its Bench. Wartortle's Shell Shield is automatic; no voluntary activation is recorded. Mega receives three Water by T13.

T15 the computer plays X Speed, reducing Wailord's printed retreat cost of four to three. It pays all three existing Water, promotes Mega Blastoise, then attaches that turn's generated Water to the now-benched Wailord (F0214.50, F0218.00, F0220.50, F0222.50). Wailord ends with one Water, not zero or three. Triple Bombardment deals 130 to first Ninetales, leaving 20/150 HP; no Bench damage is observed. Soothing Shore heals Wailord from 50 to 70. T16 Cyrus returns that damaged Wailord to Active; Auto also attaches Water to benched Mega Sharpedo, increasing it to two, before the winning Binding Snow. Lapras remains at three Water, second Ninetales at two.

All owner normal draws are named: T2 Research; T4 Mega Sharpedo ex; T6 Alolan Vulpix; T8 second Mega Sharpedo ex; T10 Poké Ball; T12 Elegant Cape; T14 second Alolan Ninetales ex; T16 second Misty. Research reveals Lapras then Vulpix; T10 Poké Ball finds Carvanha. Final hand is Copycat, Misty, Mega Sharpedo ex, Carvanha, Elegant Cape, Misty. Held Misty, Copycat and Cape are not interpreted as offered or declined prompts. No visible no-effect play or Supporter warning response appears.

The successful pressure comes from using Turbo Shark to prepare Ninetales and repeating the Energy attachment restriction, while saving Cyrus for the damaged two-point target. Cape is drawn but held; it never modifies Ninetales's maximum HP. Additional protective or resource plays could be considered when comparing Auto with manual games, but this one win does not establish an optimal policy or broad matchup rate.

TURN_TABLE.md and TURN_LEDGER.json give exactly one row for each of the 16 turns, numbered actions, hand transactions, both start/end boards, physical instances, Water destinations, effects, HP, points and phase-specific Energy Zones. Native start hands and opponent upper-fan counts are retained for all eight owner turns. T6 uses an extra +0.30 s preplay frame because Auto acts before +1. All +1/+3/+6 candidates and pre-attack substitutes are retained, with later postplay candidates explicitly limited.

Neither discard pile is opened. Periodic full-pile snapshots are unavailable; visible top cards are marked partial and never treated as a complete census. Every concealed opponent draw/search identity stays null. Coverage and uncertain timing/provenance are recorded in COVERAGE.md and UNCERTAINTIES.json. Original SOURCE and ASSIGNMENT are preserved. No external log, original movie, shared index, deck or simulator was changed by this worker.
''')
md('COVERAGE.md','''# Source coverage

Entire source 20261002_205230000_iOS.MP4, 0–278.235 s: setup, 16 turns, final attack, Victory and results screen. No source interval was skipped in locator inspection. Every retained one-fps locator image was inspected in 14 chronological grids: nominal samples 0–19, 20–39, 40–59, 60–79, 80–99, 100–119, 120–139, 140–159, 160–179, 180–199, 200–219, 220–239, 240–259, 260–277. Preview grids of the same retained samples were used for the first eleven ranges; standard final three grids were used. The nominal locator time is distinct from measured decoded native PTS.

Setup 0–19; T1 20–32.8; T2 33–50; T3 50.5–58; T4 58.5–85; T5 85–92.5; T6 92.5–107.5; T7 107.5–117.5; T8 117.5–137; T9 137–145.5; T10 145.5–162; T11 162–174.5; T12 174.5–186.5; T13 186.5–195.5; T14 195.5–210.5; T15 210.5–232.5; T16 232.5–254.5; terminal 254.5–278.235. Turn boundaries are approximate and adjoining banner/animation ranges overlap within that precision. These are event windows, not gaps in source inspection.

Targeted native inspection checks exposed opening, draw/end hands, upper opponent fans, both Research reveals, search identity, attachment destinations, retreat payments, evolutions, damage, healing, Cyrus target and ending. All native capture metadata, exact selected PTS, dimensions, crops and file SHA values are retained in EXTRACTION_MANIFEST.json / TURN_EVIDENCE.json. Retained extra anchors are not all claimed independently inspected. Broad coverage uses one-fps locator inspection; it cannot prove every video instant or exclude hidden/manual input between frames.

Initial restricted-shell read failed due to access denial. Narrow approved read access then decoded successfully. This is an access failure, not a corrupt-media diagnosis. The original source was never rehashed by this reviewer. Source hash comes from frozen SOURCE.json.

Recording limits: no opened discard piles; hidden opponent draw/search identities; category absent from game setup screen but confirmed by owner screenshot receipt. Some start/end board values carry through adjacent native endpoints and known actions while animations obscure labels. No unreviewed interval is being relabeled as a recording limit.
''')
now=datetime.now(timezone.utc)
write('METRICS.json',dict(source_video=V,reviewer='/root/drafta_auto_205230',model='gpt-6.1-sol',reasoning_effort='high',locator_frames=278,locator_grids_inspected=14,locator_images_inspected=278,native_captures=len(manifest),native_crops_retained=2*len(manifest),native_images_inspected_count=None,native_inspection_limit='Distinct inspection-call total was not instrumented; no invented count. Required hands, fans and consequential anchors inspected; retained unused captures are not claimed inspected.',assigned_utc=read('ASSIGNMENT.json')['assigned_utc'],finished_utc=now.isoformat(),elapsed_seconds=(now-datetime.fromisoformat(read('ASSIGNMENT.json')['assigned_utc'])).total_seconds(),elapsed_basis='Wall time since assignment, includes wait/access/extraction time',token_usage=None,dollar_cost=None,usage_limit='No actual usage/cost measurement available',native_capture_cap=160,bounded_decoder_threads=2))
# Local validation before immutable submission freeze.
assert len(rows)==16 and [x['turn_number'] for x in rows]==list(range(1,17))
assert len(deck['cards_in_log_order'])==20 and sum(x['count'] for x in deck['counts_by_name_and_variant'])==20
assert len(manifest)<=160
for t in range(2,17,2):
 assert all(drawends[t]+o in bytime for o in [1,3,6]) and before[t] in bytime and selected[t] in bytime
for row in rows:
 for ev in row['turn_evidence_ids']: assert ev in {f['evidence_id'] for f in manifest},ev
for n in ['PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']: assert read(n)['is_template'] is False
files=['SOURCE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','TURN_TABLE.md','METRICS.json','EXTRACTION_MANIFEST.json']
write('SUBMISSION.json',dict(source_video=V,source_sha256=SHA,reviewer='/root/drafta_auto_205230',model='gpt-6.1-sol',reasoning_effort='high',complete_first_pass=True,submitted_utc=now.isoformat(),files={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files},capture_status='complete_with_recording_limits',independent_acceptance='pending',validation='16 sequential rows; exact 20-card snapshot; all eight owner timed candidates, selected preplay and before-attack evidence present; all row evidence IDs resolve; no template flags remain.'))
print('Frozen first-pass packet:',len(rows),'turns;',len(manifest),'native captures;',len(files),'core files')
