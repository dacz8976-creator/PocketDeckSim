import json, copy
from pathlib import Path
from PIL import Image

P = Path(__file__).parent
SRC = '20261010_020908000_iOS.MP4'
SHA = '6771089aca9afe1e952e047017c07b74964a184011832179c27fe7b7f839bffc'
GAME = '20261010_020908000_iOS_game1'
SOURCES = [dict(video_basename=SRC, sha256=SHA, source_json='SOURCE.json')]
K = "Team Rocket's Koffing"
W = "Team Rocket's Weezing ex"
M = "Team Rocket's Magmar"
def eid(t): return 'F'+f'{t:07.2f}'
def save(name,data): (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cards(names,t): return [dict(position=i+1,name=n,variant=None,basis='visible native hand/reveal',evidence_ids=[eid(t)],limit_reason=None) for i,n in enumerate(names)]
def hand(names,t): return dict(cards_left_to_right=cards(names,t),count=len(names),basis='visually counted native hand',evidence_ids=[eid(t)],status='observed',limit_reason=None)
def hidden(t,count=None): return dict(cards_left_to_right=None,count=count,basis='card-back fan only',evidence_ids=[eid(t)],status='hidden',limit_reason='Opponent card identities are face down.')
def pokemon(name,hp,maxhp,energy=0,etype='Water',tool='none',conditions=None,pos=None,effects=None):
 return dict(name=name,variant={'Horsea':'Hook 30 / 50 HP','Seadra':'Water Arrow 50 / 70 HP','Kingdra ex':'Stormy Prison 90 / 170 HP','Nihilego':'More Poison / New Wave / 70 HP',K:'Reverse Thrust 10 / 60 HP',W:'Boiler Smog / Confusion Gas 60 / 140 HP',M:'Derisive Roasting 10+ / 70 HP'}.get(name),bench_position=pos,hp_now=hp,hp_max=maxhp,hp_max_basis='visible printed HP; no applicable HP modifier shown',damage=maxhp-hp,attached_energy=dict(total=energy,by_type={etype:energy} if energy else {}),tool=tool,special_conditions=conditions or [],active_effects=effects or [],evidence_ids=[],status='observed',limit_reason=None)
def zone(typ,count):
 return dict(this_turn=dict(type=typ,count=count,available=bool(count)),next=dict(type=typ,count=None,available=None),basis='Visible large current orb and small next orb; future count is not displayed.',evidence_ids=[],limit_reason='Next type visible; next count/availability not displayed.')
def board(turn,t,oa,ob,pa,pb,stadium='none',points=0,oz=0,pz=0):
 z=dict(turn_number_displayed=turn,phase='resolved board boundary',stadium=stadium,owner=dict(active=copy.deepcopy(oa),bench_in_position_order=copy.deepcopy(ob),energy_zone=zone('Water',oz),points=points,board_effects=[],evidence_ids=[eid(t)],status='observed',limit_reason=None),opponent=dict(active=copy.deepcopy(pa),bench_in_position_order=copy.deepcopy(pb),energy_zone=zone('Darkness',pz),points=0,board_effects=[],evidence_ids=[eid(t)],status='observed',limit_reason=None),shared_effects=[],evidence_ids=[eid(t)])
 for side in ['owner','opponent']:
  for p in [z[side]['active']]+z[side]['bench_in_position_order']: p['evidence_ids']=[eid(t)]
  z[side]['energy_zone']['evidence_ids']=[eid(t)]
 z['opponent']['board_effects']=[dict(name='More Poison',source='Nihilego',affected_player='owner',restriction_or_mark='Owner Active takes10 additional damage from Poisoned while ability is in effect.',expiry='while Nihilego remains in play',basis='visible printed ability')]
 return z
def act(order,kind,name,t,target,result,energy=None,prompt=None,response=None,nested=None,limit=None):
 return dict(order=order,kind=kind,card_name=name,target=target,energy=energy,result=result,prompt_text=prompt,response=response,nested_events_in_order=nested or [],hand_count_after=None,source_video=SRC,timestamp_seconds=t,evidence_ids=[eid(t)],basis='source observation',limit_reason=limit)
def draw(kind,names,t,play=None,cause=None,before=None,after=None):
 return dict(kind=kind,caused_by=cause,linked_play_order=play,cards_in_reveal_order=[dict(name=n,reveal_position=i+1,source_video=SRC,timestamp_seconds=t,evidence_ids=[eid(t)],basis='visible reveal/hand',limit_reason=None if n else 'Opponent reveal remains face down.') for i,n in enumerate(names)],hand_count_before=before,hand_count_after=after,returned_or_discarded_cards=[],source_video=SRC,timestamp_seconds=t,evidence_ids=[eid(t)],limit_reason=None)

# Native source crops. These are retained source pixels, not enlarged overview images.
for f in (P/'turn_evidence').glob('t*.jpg'):
 if '_' in f.stem: continue
 im=Image.open(f)
 assert im.size==(1170,2532)
 im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_bottom.jpg'))
 im.crop((0,150,1170,760)).save(f.with_name(f.stem+'_top.jpg'))

opening=[W,K,K,'Soothing Shore','Horsea']
h2=[W,K,K,'Soothing Shore','Poke Ball'];h4=[W,'Seadra'];h6=['Poke Ball','Hiking Trail','Rare Candy','Kingdra ex']
b1s=board(1,47,pokemon('Horsea',50,50),[],pokemon('Nihilego',70,70,etype='Darkness'),[pokemon(M,70,70,etype='Darkness',pos=3)])
b1e=board(1,70,pokemon('Horsea',40,50),[],pokemon('Nihilego',70,70,etype='Darkness',tool='Deceptive Needle'),[pokemon(M,70,70,etype='Darkness',pos=3)])
b2s=copy.deepcopy(b1e);b2s['turn_number_displayed']=2;b2s['owner']['energy_zone']=zone('Water',1);b2s['evidence_ids']=[eid(73.4)]
ob=[pokemon(K,60,60,pos=1),pokemon(K,60,60,pos=2),pokemon('Horsea',50,50,pos=3)]
b2e=board(2,104,pokemon('Horsea',50,50,1),ob,pokemon('Nihilego',40,70,etype='Darkness',tool='Deceptive Needle'),[pokemon(M,70,70,etype='Darkness',pos=3)],'Soothing Shore')
b3s=copy.deepcopy(b2e);b3s['turn_number_displayed']=3;b3s['opponent']['energy_zone']=zone('Darkness',1)
pb=[pokemon(K,60,60,etype='Darkness',pos=2),pokemon(M,70,70,1,'Darkness',pos=3)]
b3e=board(3,168,pokemon('Horsea',40,50,1),ob,pokemon('Nihilego',40,70,etype='Darkness',tool='Deceptive Needle'),pb,'Hiking Trail')
b4s=copy.deepcopy(b3e);b4s['turn_number_displayed']=4;b4s['owner']['energy_zone']=zone('Water',1)
ob4=[pokemon(W,140,140,pos=1),pokemon(K,60,60,pos=2),pokemon('Horsea',50,50,pos=3)]
b4e=board(4,214,pokemon('Seadra',60,70,2),ob4,pokemon('Nihilego',10,70,etype='Darkness',tool='Deceptive Needle',conditions=['Poisoned']),pb,'Hiking Trail')
b5s=copy.deepcopy(b4e);b5s['turn_number_displayed']=5;b5s['opponent']['energy_zone']=zone('Darkness',1)
pb5=[pokemon(K,60,60,etype='Darkness',pos=2),pokemon('Nihilego',10,70,etype='Darkness',tool='Deceptive Needle',pos=3)]
b5e=board(5,251,pokemon('Seadra',60,70,2,conditions=['Confused']),ob4,pokemon(M,70,70,1,'Darkness'),pb5,'Hiking Trail',pz=1)
b6s=copy.deepcopy(b5e);b6s['turn_number_displayed']=6;b6s['owner']['energy_zone']=zone('Water',1)
ob6=[pokemon(W,140,140,pos=1),pokemon(K,60,60,pos=2),pokemon('Horsea',50,50,1,pos=3)]
b6e=board(6,300,pokemon('Kingdra ex',160,170,2),ob6,pokemon('Nihilego',10,70,etype='Darkness',tool='Deceptive Needle'),[pokemon(K,60,60,etype='Darkness',pos=2)],'Hiking Trail',1)
b7s=copy.deepcopy(b6e);b7s['turn_number_displayed']=7;b7s['opponent']['energy_zone']=zone('Darkness',1)
b7e=board(7,376,pokemon('Kingdra ex',160,170,2),ob6,pokemon('Nihilego',10,70,etype='Darkness',tool='Deceptive Needle'),[pokemon(K,60,60,1,'Darkness',tool='Elegant Cape',pos=2)],'Hiking Trail',1)

specs=[
 (1,'opponent',50,70,None,None,b1s,b1e,[act(1,'card_play',"Professor's Research",56,None,'Draws two hidden cards.'),act(2,'card_play','Deceptive Needle',66,'Nihilego','Tool attached.'),act(3,'end_turn',None,69,None,'Ends turn without an attack.')],[draw('normal_draw',[None],50),draw('supporter_draw',[None,None],58,1,"Professor's Research")],[dict(event='Deceptive Needle',timestamp_seconds=70,result='Horsea 50 to 40 HP; 10 damage.')]),
 (2,'owner',71,106,73.4,h2,b2s,b2e,[act(1,'card_play',K,75,'Bench position 1','Benched.'),act(2,'card_play',K,80,'Bench position 2','Benched.'),act(3,'card_play','Poke Ball',82,None,'Finds Horsea.',nested=['Horsea revealed and added to hand']),act(4,'card_play','Horsea',86,'Bench position 3','Benched.'),act(5,'card_play','Soothing Shore',90,'Stadium','Soothing Shore enters play.'),act(6,'energy_attachment',None,93,'Active Horsea','1 Water attached.',energy=dict(type='Water',count=1,destination='Active Horsea',retreat_payment_by_type=None)),act(7,'attack','Horsea',98,'Nihilego','Hook deals 30, Nihilego 70 to 40.')],[draw('normal_draw',['Poke Ball'],73,None,None,4,5),draw('search',['Horsea'],84,3,'Poke Ball',2,3)],[dict(event='Soothing Shore',timestamp_seconds=102,result='Heals owner Active Horsea 40 to 50, capped at maximum; printed stadium heals 20 to Water-attached Pokemon.')]),
 (3,'opponent',106,169,None,None,b3s,b3e,[act(1,'card_play','Poke Ball',112,None,'Search finds Team Rocket\'s Koffing.'),act(2,'card_play',K,138,'Bench position 2','Benched.'),act(3,'energy_attachment',None,152,M,'1 Darkness attached to benched Magmar.',energy=dict(type='Darkness',count=1,destination='Bench Team Rocket\'s Magmar',retreat_payment_by_type=None),limit='Attachment is bracketed by pre/post board states around 148-152s; action timestamp approximate.'),act(4,'card_play','Hiking Trail',154,'Stadium','Replaces Soothing Shore.'),act(5,'end_turn',None,162,None,'Ends without attack.')],[draw('normal_draw',[None],108),draw('search',[K],126,1,'Poke Ball')],[dict(event='Hiking Trail',timestamp_seconds=162,result='Opponent fan remains three; no hidden card names established.'),dict(event='Deceptive Needle',timestamp_seconds=167,result='Horsea 50 to 40 HP.')]),
 (4,'owner',169,214,173.8,h4,b4s,b4e,[act(1,'evolution','Seadra',178,'Active Horsea','Evolves; inherited 10 damage gives 60/70 HP.'),act(2,'evolution',W,182,'Bench position 1 Koffing','Evolves into Weezing ex, 140 HP.'),act(3,'prompt_response',None,187,'Boiler Smog','Accepts effect.',prompt='Use the effect of Boiler Smog!',response='Yes',nested=['Nihilego becomes Poisoned and Burned']),act(4,'energy_attachment',None,195,'Active Seadra','Second Water attached.',energy=dict(type='Water',count=1,destination='Active Seadra',retreat_payment_by_type=None)),act(5,'end_turn',None,197,None,'Ends with no attack and no hand cards before automatic draw.')],[draw('normal_draw',['Seadra'],172.7,None,None,1,2),draw('stadium_draw',['Poke Ball','Hiking Trail','Rare Candy'],202,None,'Hiking Trail',0,3)],[dict(event='Hiking Trail',timestamp_seconds=198,result='Draws to three: Poke Ball, Hiking Trail, Rare Candy, separately revealed in that order.'),dict(event='Pokemon Checkup',timestamp_seconds=204,result='Poison and Burn total 30 damage, Nihilego 40 to 10 HP.'),dict(event='Burn coin',timestamp_seconds=210,result='Heads; Nihilego recovers from Burned, remains Poisoned.')]),
 (5,'opponent',214,252,None,None,b5s,b5e,[act(1,'card_play','Leaf',216,'opponent retreat','Leaf used before retreat.'),act(2,'retreat',None,218,'Nihilego to benched Magmar','Nihilego retreats with zero attached Energy and zero Energy payment; poison clears on bench.',energy=dict(type=None,count=0,destination=None,retreat_payment_by_type={})),act(3,'card_play',"Team Rocket's Master Plan",225,'both Actives','Seadra Confused; tails also makes Magmar Confused.'),act(4,'card_play','Lum Berry',237,'Active Magmar','Tool attached.'),act(5,'attack',M,240,'Seadra','Derisive Roasting attempted; confusion coin tails; The attack did nothing.')],[draw('normal_draw',[None],216),draw('stadium_draw',[None],250,None,'Hiking Trail')],[dict(event='Lum Berry',timestamp_seconds=245,result='Clears Magmar Confusion and is discarded; Seadra remains Confused.'),dict(event='Hiking Trail',timestamp_seconds=249,result='Opponent fan refills from two to three, identity hidden; owner HP stays60.')]),
 (6,'owner',252,302,254.6,h6,b6s,b6e,[act(1,'card_play','Poke Ball',255.6,None,'No effect: There are no cards in the deck that can be the target of the effect.'),act(2,'evolution','Kingdra ex',262,'Active Seadra','Evolves, inherited 10 damage gives160/170 HP; Confusion clears.'),act(3,'energy_attachment',None,269,'Bench position3 Horsea','1 Water attached to Horsea; Kingdra retains2 Water.',energy=dict(type='Water',count=1,destination='Bench position3 Horsea',retreat_payment_by_type=None)),act(4,'attack','Kingdra ex',274,'Active Magmar','Stormy Prison deals110 (90 printed plus20 Water weakness); Magmar knocked out; owner gains point1.',nested=['Retreat-block text displayed on Magmar before KO','Opponent promotes Nihilego at298'])],[draw('normal_draw',['Kingdra ex'],254.2,None,None,3,4),draw('stadium_draw',['Copycat'],302,None,'Hiking Trail',2,3)],[dict(event='KO',timestamp_seconds=282,result='Magmar and its Darkness Energy discarded; points1-0.'),dict(event='Replacement',timestamp_seconds=298,result='Nihilego promoted from bench3,10HP; Koffing remainsbench2.'),dict(event='Hiking Trail',timestamp_seconds=300,result='Owner draws Copycat from2 to3 cards.')]),
 (7,'opponent',302,378,None,None,b7s,b7e,[act(1,'card_play','Poke Ball',304,None,'No effect: There are no cards in the deck that can be the target of the effect.'),act(2,'card_play','Elegant Cape',309.5,'Bench position2 Koffing','Tool attached; Basic Koffing remains60HP. Printed tool gives Stage1 +30HP.'),act(3,'energy_attachment',None,315,'Bench position2 Koffing','1 Darkness attached.',energy=dict(type='Darkness',count=1,destination='Bench position2 Koffing',retreat_payment_by_type=None))],[draw('normal_draw',[None],302)],[dict(event='Connection timeout',timestamp_seconds=378,result='Error: Your opponent did not return within the allowed time.'),dict(event='Victory',timestamp_seconds=382,result='Dacz8976 Victory displayed; points before timeout1-0.')])]
rows=[]
for num,who,start,end,de,names,bs,be,plays,draws,auto in specs:
 sh=hand(names,de) if names else hidden(start)
 ending={2:[W],4:['Poke Ball','Hiking Trail','Rare Candy'],6:['Hiking Trail','Rare Candy','Copycat']}.get(num)
 hs=copy.deepcopy(sh) if who=='owner' else dict(cards_left_to_right=None,count=None,basis=None,evidence_ids=[],status='not_applicable',limit_reason='Opponent turn; owner hand captured at adjacent boundaries.')
 if who=='owner':
  st={2:73.4,4:174.8,6:255}[num];sh=hand(names,st);hs=copy.deepcopy(sh)
 fan={2:4,4:3,6:3}.get(num)
 rows.append(dict(turn_number=num,who_played=who,source_video=SRC,timing=dict(start_seconds=start,draw_animation_end_seconds=de,first_voluntary_move_seconds=plays[0]['timestamp_seconds'],before_end_action_seconds={2:96,4:196,6:272}.get(num),end_after_resolution_seconds=end),hand_at_start=sh,owner_hand_start=hs,opponent_hand_at_owner_turn_start=dict(count=fan,supported_range=None,count_method='Count distinct visible card backs in native top crop',basis='direct fan observation' if fan else 'not applicable on opponent turn',evidence_ids=[eid({2:73.4,4:174.8,6:255}.get(num,start))],limit_reason=None if fan else 'Opponent turn'),draws_and_searches=draws,plays_in_order=plays,automatic_events_in_order=auto,board_at_start=bs,board_after=be,owner_hand_end=hand(ending,{2:104,4:214,6:302}[num]) if ending else hs,owner_before_end_hand_count={2:1,4:0,6:2}.get(num),discard_snapshot_ids=[],turn_evidence_ids=sorted(set([eid(start),eid(end)]+[eid(x['timestamp_seconds']) for x in plays])),limits=['Opponent hidden draws retain unknown identities.','No opened discard pile in this turn.']+(['Terminal timeout occurs within turn7; no normal end-of-turn resolution.'] if num==7 else [])))

limits=['No opened discard pile appears anywhere in this source; visible top discard cards and play history do not establish a full pile.','Opponent hand identities and hidden draw/search results remain unknown except publicly revealed Koffing.','Draw-end times are visual approximations; frame requested seek times are preserved, actual decoder frame PTS was not separately measured.','Opponent connection intent and actual disconnect cause are not established.','QR and live log use semantic card variants; artwork/rarity exact printings are not established.']
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=GAME,sources=SOURCES,turns=rows,limits=limits))
save('PAUSE_GAME.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=GAME,review_date='2026-10-10',reviewer='/root/pause_020908',model='gpt-6.1-sol',sources=SOURCES,destination='https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',deck_name="Kingdra ex / Team Rocket's Weezing ex",recording_match_date_local='2026-10-09',recording_start_local='21:09:08 America/Chicago',date_basis='../RECORDING_DATE_VERIFICATION.json and filmed iPhone21:09 clock; lead supplied verified metadata',classification='human_battle',classification_basis='Matching screen versus Lv30 Desk and seven manually controlled turns; no Auto control visible anywhere.',opponent='Desk',owner='Dacz8976',opening=dict(source_video=SRC,timestamp_seconds=27,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=cards(opening,27),selected_active=dict(name='Horsea',opening_position=5,source_video=SRC,timestamp_seconds=29,evidence_ids=[eid(29)]),redraw_or_replacement=[],before_active_placement=True,status='observed',evidence_ids=[eid(27)],limit_reason=None),packet_files=dict(prose='REVIEW.md',coverage='COVERAGE.md',deck='DECK_USED.json',turns='TURN_LEDGER.json',evidence='TURN_EVIDENCE.json'),capture_status='complete_with_recording_limits',battle_review_status='worker_full_battle_review_complete_awaiting_lead_acceptance',outcome=dict(owner_result='win',basis='Opponent connection-timeout notice followed by Victory',final_points_before_timeout=dict(owner=1,opponent=0),evidence_ids=[eid(378),eid(382)]),limits=limits,lead_checked=False))

live=json.loads((P.parent/'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8'))
deck=next(d for d in live['decks'] if d['id']=='filmed-qr-b649812c0d42')
assert sum(int(r[0]) for r in deck['rows'])==20
(P/'LIVE_DECK_SOURCE.txt').write_text(deck['text'],encoding='utf-8')
save('DECK_USED.json',dict(is_template=False,schema='pause-games/deck-used-v1',game_id=GAME,deck_name=deck['name'],deck_id=deck['id'],source_url=live['source_url'],retrieved_at_utc=live['retrieved_at_utc'],retrieval_local_date='2026-10-09',captured_source_text='LIVE_DECK_SOURCE.txt',shared_snapshot='../LIVE_NEW_DECKS_VERIFIED.json',exact_list_status='verified_20_semantic_cards_live_log_matches_filmed_QR',card_slot_count=20,cards_in_log_order=[dict(name=r[1],variant=r[2]) for r in deck['rows'] for _ in range(int(r[0]))],counts_by_name_and_variant=[dict(name=r[1],variant=r[2],count=int(r[0])) for r in deck['rows']],energy_configuration='Water only',filmed_deck_label='New deck13',film_qr='qr_intake/QR_DECODE_0001.00.json',film_continuity=dict(evidence_ids=[eid(2),eid(3),eid(4),eid(5),eid(27)],observation='Source starts with QR, closes to same New deck13 and visible20/20 list, then matchmaking without a visible deck change. Gameplay Horsea/Koffing/Weezing/Kingdra core and filmed cards agree.',qr_code_matches_live=deck['code']==json.loads((P/'qr_intake/QR_DECODE_0001.00.json').read_text(encoding='utf-8'))['payload']),limits=[limits[-1]]))

selected={73.4:2,174.8:4,255:6}
candidate={2:dict(draw_end=73.4,times=[74.4,76.4,79.4],pre=94,chosen=73.4),4:dict(draw_end=173.8,times=[174.8,176.8,179.8],pre=196,chosen=174.8),6:dict(draw_end=254.6,times=[255.6,257.6,260.6],pre=270,chosen=255)}
frames=[]
for f in sorted((P/'turn_evidence').glob('t*.jpg')):
 if '_' in f.stem: continue
 t=float(f.stem[1:]);turn=next((n for n,_,st,en,_,_,_,_,_,_,_ in specs if st<=t<=en),None)
 c=candidate.get(turn);is_c=c and t in c['times'];pre=c and t==c['pre'];sel=t in selected
 role='opening' if t==27 else 'selected_start_hand' if sel else 'draw_relative_candidate' if is_c else 'before_end_hand' if pre else 'targeted_source_frame'
 suitability='Selected dense pre-play hand; scheduled candidates occur after first play.' if sel and turn in [2,6] else 'Clear selected pre-play hand.' if sel else 'Already contains a voluntary play or card zoom; unsuitable as start hand.' if is_c and (turn in [2,6] or (turn==4 and t==179.8)) else 'Candidate inspected; native hand retained.' if is_c else 'Source frame retained for boundary/action/ending verification.'
 frames.append(dict(evidence_id=eid(t),role=role,turn_number=turn,who_played='owner' if turn in [2,4,6] else 'opponent' if turn else 'setup',source_video=SRC,source_sha256=SHA,draw_animation_end_seconds=c['draw_end'] if c else None,requested_source_seconds=t,actual_frame_seconds_if_measured=None,offset_after_draw_seconds=round(t-c['draw_end'],2) if is_c else None,full_frame_path='turn_evidence/'+f.name,native_dimensions=dict(width=1170,height=2532),bottom_crop=dict(path='turn_evidence/'+f.stem+'_bottom.jpg',pixel_bounds_x0_y0_x1_y1=[0,2025,1170,2532]),top_crop=dict(path='turn_evidence/'+f.stem+'_top.jpg',pixel_bounds_x0_y0_x1_y1=[0,150,1170,760]),selected_for_start_hand=sel,before_first_play=True if sel else False if is_c and (turn in [2,6] or t==179.8) else None,unzoomed=True if sel else None,hand_spread=True if sel else None,observation=suitability,suitability_or_limit=suitability))
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=GAME,sources=SOURCES,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,bottom_crop_height_fraction=.2,top_crop='[0,150,1170,760]',fixed_grid_is_turn_start_evidence=False),frames=frames,owner_turn_capture_schedule=candidate,discard_snapshots=[dict(snapshot_id='DISCARD_NOT_SHOWN',turn_number=None,pile_owner='both',source_video=SRC,timestamp_seconds=None,cards_in_view=None,scroll_coverage=None,full_pile_established=False,evidence_ids=[],limit_reason=limits[0])],scheduled_capture_limits=limits))
save('SUMMARY.json',dict(source_video=SRC,sha256=SHA,reviewer='/root/pause_020908',model='gpt-6.1-sol',scope='Entire supplied source: deck QR/continuity, setup, displayed turns1-7, timeout/Victory and recording end',worker_status='full_review_complete_awaiting_independent_acceptance',classification='human_battle',opponent='Desk',owner_result='win',terminal_reason_observed='Your opponent did not return within the allowed time.',terminal_seconds=378,victory_seconds=382,points_before_terminal='1-0',deck_name=deck['name'],capture_status='complete_with_recording_limits',owner_turns=[2,4,6],turn_count=7,limits=limits,external_writes=False,source_moved=False))
save('UNCERTAINTIES.json',dict(source_video=SRC,sha256=SHA,unreviewed_intervals=[],limits=[dict(id='L'+str(i+1),description=s,inspection_status='inspected source limitation') for i,s in enumerate(limits)],consequential_unresolved_claims=[]))

prose='''# Whole-source review: 20261010_020908000_iOS.MP4

Reviewer: /root/pause_020908, gpt-6.1-sol. Review UTC date: October10,2026. Match date: October9,2026,21:09:08 America/Chicago (lead-verified file metadata and filmed clock). Frozen source SHA-256: 6771089aca9afe1e952e047017c07b74964a184011832179c27fe7b7f839bffc. Duration388.888333 seconds. Native dimensions1170x2532.

One human battle against Desk (Lv30), owner Dacz8976. No Auto control appears. Owner wins after the filmed opponent connection-timeout notice, not a three-point finish. At378 seconds the Error states, "Your opponent did not return within the allowed time." Victory appears at382 seconds. The last gameplay board is1-0. The footage does not establish why the opponent disconnected or any intention to quit.

## Setup and source continuity

0-5s: native QR and New deck13, visible20/20 deck, then matchmaking with no visible intervening deck change. The filmed QR matches the dated live Pause Games deck ID filmed-qr-b649812c0d42. DECK_USED.json saves20 slots and duplicate counts. Exact artwork/rarity is not encoded by that QR.

At27s before Active placement the five cards left to right are Team Rocket's Weezing ex, Team Rocket's Koffing, Team Rocket's Koffing, Soothing Shore, Horsea. Horsea, original slot5, becomes Active at29s. Owner elects no starting Bench cards and goes second. Opponent reveals Nihilego70HP Active and Team Rocket's Magmar70HP at right Bench slot3. Setup ends around47s. No redraw occurs.

## All seven recorded turns

|Turn|Player|Source interval|Observed actions and resulting state|
|---|---|---|---|
|1|Desk|50-70s|Hidden normal draw; Professor's Research draws two hidden cards; Deceptive Needle on Nihilego; ends without attack. Needle10 damage makes Horsea40/50.|
|2|Owner|71-106s|Normal draw Poke Ball. Bench both Koffing in left/middle slots, Poke Ball finds Horsea, bench Horsea right, play Soothing Shore, attach Water Active Horsea, Hook30 into Nihilego. Shore heals Horsea to50. End hand one Weezing.|
|3|Desk|106-169s|Hidden normal draw, Poke Ball finds Koffing, bench Koffing middle, Darkness to right benched Magmar, Hiking Trail replaces Shore, ends without attack. Needle10 makes Horsea40.|
|4|Owner|169-214s|Normal draw Seadra; evolve Active Horsea to Seadra60/70, evolve left Koffing to Weezing140, accept Boiler Smog Yes to Poison/Burn Nihilego, attach second Water Seadra, End Turn with zero cards and no attack. Hiking Trail reveals Poke Ball, Hiking Trail, Rare Candy in order. Poison/Burn30 lowers Nihilego40 to10; Burn heads clears Burn, Poison remains.|
|5|Desk|214-252s|Leaf, retreat zero-Energy Nihilego into Magmar (Poison clears), Team Rocket's Master Plan confuses Seadra and tails confuses Magmar too, Lum Berry on Magmar, attempt Derisive Roasting. Confusion tails: The attack did nothing. Lum Berry clears Magmar Confusion and is discarded. Hiking Trail refills opponent fan to3 hidden cards. Seadra stays60/70 and Confused.|
|6|Owner|252-302s|Normal draw Kingdra ex, first play Poke Ball finds no eligible target, evolve Active Seadra to Kingdra160/170 and clear Confusion, Water to bench Horsea, Stormy Prison110 including Water weakness knocks out Magmar. Owner point1; opponent promotes Nihilego10. Hiking Trail adds Copycat. Owner ending hand Hiking Trail/Rare Candy/Copycat,3 cards.|
|7|Desk|302-378s|Hidden normal draw; Poke Ball no target, Elegant Cape on benched Koffing (Basic remains60HP), Darkness to Koffing. Waiting for opponent to return appears. No attack or normal turn-end resolution before connection timeout.|

Each table row corresponds to TURN_LEDGER.json turn_number. The ledger numbers every voluntary action and separates automatic effects, condition checks and Stadium draws. Boiler Smog prompt187s is explicitly accepted. No unoffered option is labeled declined. No owner Research or Copycat is played in this game; Copycat is a named automatic Stadium draw at the end of turn6.

## Native hand and board evidence

All retained native frames have full frame, bottom-fifth crop [0,2025,1170,2532] and top crop [0,150,1170,760]. TURN_EVIDENCE.json stores source seek times, draw approximations and candidate suitability. Selected pre-play owner hands are73.4s (turn2),174.8s (turn4),255s (turn6). Turn2 and6 first plays occur too quickly for the scheduled+1/+3/+6 frames, so dense pre-play frames are selected and scheduled post-play candidates retained with explicit labels. Turn4+1/+3 candidates retain both hand cards; +6 is after evolution. Before-ending views96s/196s/272s have respective hand sizes1/0/2. Automatic Hiking Trail draws change the final resolved hand counts to1/3/3.

Opponent fans directly count4/3/3 card backs at owner turns2/4/6. These are visual fan counts, separate from transaction arithmetic. Owner Energy is Water; opponent Darkness icons are observed. Both current and small next orb types are captured; future counts are not shown. All board starts/ends, Bench slots, printed/current HP, damage, typed Energy, Tools, conditions, Stadium and points are in the ledger.

## Recording limits and review scope

Neither discard pile is opened. The visible top discard card and play history cannot establish complete pile contents. No hidden hand identities are inferred from the deck. Opponent hidden draws remain unknown. Requested seeks are local source times; exact decoded frame PTS is unmeasured. Notifications briefly cover the top clock/fan around177-184s and370s; neighboring clear frames supply the visible board. The late waiting sequence is inspected through its timeout, then Victory and source end388s (loading screen). No second match appears.

The whole-source review is complete at worker level. The Pause Games supplement is complete with recording limits. Independent lead acceptance, external logging and source archival remain lead responsibilities. No shared index, event, external artifact or simulator was modified by this worker.
'''
(P/'REVIEW.md').write_text(prose,encoding='utf-8')
(P/'COVERAGE.md').write_text('''# Coverage checklist

- [x]0-5: native QR, deck list and matchmaking continuity.
- [x]5-27: matchmaking, opponent identity and opening deal.
- [x]27-47: five opening slots, Horsea Active, no Bench, second player, opponent setup.
- [x]50-70: opponent turn1, Research, Needle and damage.
- [x]71-106: owner turn2, every numbered play, search, hand and healing.
- [x]106-169: opponent turn3, search, Bench, Energy, Stadium and Needle.
- [x]169-214: owner turn4, evolutions, Yes prompt, Water, end draw and checkups.
- [x]214-252: opponent turn5, Leaf retreat, Master Plan, Berry, failed attack and end draw.
- [x]252-302: owner turn6, no-effect Poke Ball, evolution, Energy destination, weakness KO, replacement, draw.
- [x]302-378: opponent turn7, no-effect Ball, Elegant Cape, Energy and complete waiting sequence.
- [x]378-388.888333: timeout notice, Victory, source-end loading screen.
- [x]One ledger row per displayed turn1-7; setup separate.
- [x]Native draw-relative candidates and dense pre-play selected hands.
- [x]Opening/first move/draw order/end hand/terminal claims have retained source evidence for independent acceptance.
- [x]Both discards explicitly unavailable because neither pile is opened.
- [ ]Independent lead acceptance and external entry/archive (lead responsibility).

No unreviewed source interval remains. Coarse contact sheets locate phases; native frames supply hand/draw/decision evidence. Dense action inspections and their source timestamps are recorded in VIEWED_MANIFEST.json and TURN_EVIDENCE.json. Unknown information remains qualified.
''',encoding='utf-8')
save('VIEWED_MANIFEST.json',dict(reviewer='/root/pause_020908',source_video=SRC,sha256=SHA,method='Visual inspection of complete four-second contact overview plus targeted native full frames and native hand crops. Extracted images are not all automatically claimed viewed.',whole_source_overview_viewed=['overview/initial.jpg','coarse2.jpg']+['overview/sheet_'+f'{i:02}'+'.jpg' for i in range(3,12)],targeted_contact_sheets_viewed=['native1.jpg']+['detail_'+f'{i:02}'+'.jpg' for i in range(1,6)]+['start_01.jpg','start_02.jpg','early_01.jpg','middle_01.jpg','middle_02.jpg']+['late_'+f'{i:02}'+'.jpg' for i in range(1,5)]+['reconcile_01.jpg','reconcile_02.jpg','opp_01.jpg','opp_02.jpg','opp_03.jpg','last_01.jpg','last_02.jpg'],native_individual_views=['qr_intake/t0001.00.jpg','turn_evidence/t0027.00_bottom.jpg','turn_evidence/t0175.00.jpg','turn_evidence/t0226.00.jpg','turn_evidence/t0234.00.jpg','turn_evidence/t0255.20.jpg','turn_evidence/t0202.00.jpg','turn_evidence/t0312.50.jpg','turn_evidence/t0176.00.jpg','turn_evidence/t0309.00.jpg','turn_evidence/t0255.60.jpg','turn_evidence/t0174.80.jpg','turn_evidence/t0074.20.jpg'],inspection_limits=['Some contact sheets were created before all later seeks existed; blank slots were not considered inspected. Later sheets and individual views supplied those reviewed events.','Overview native seeks are approximate midpoint timestamps; overview is navigation, not native hand evidence.']))
print('Packet written: 7 turns,',len(frames),'native full frames with crops, live20-card deck.')
