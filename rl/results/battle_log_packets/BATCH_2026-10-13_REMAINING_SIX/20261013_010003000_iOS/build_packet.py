import json,copy,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
p=Path(__file__).resolve().parent
s=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'));v=s['video_basename'];sha=s['sha256'];gid=p.name+'_game_1'
sources=[dict(video_basename=v,sha256=sha,source_json='SOURCE.json')]
def save(n,x): (p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def eid(t):return 'f'+f'{t:07.2f}'.replace('.','_')
def refs(*ts):return [eid(t) for t in ts]
def hand(names,t,basis='Native visible card names and positions'):
 return dict(cards_left_to_right=[dict(position=i+1,name=n,variant=None,basis=basis,evidence_ids=refs(t),limit_reason=None) for i,n in enumerate(names)],count=len(names),basis=basis,evidence_ids=refs(t),status='observed',limit_reason=None)
def mon(n,h,m,e={},tool='none',poison=False,pos=None,supp=False):
 return dict(name=n,variant='Mechanically established from filmed HP, attacks and ability; artwork/rarity not exhaustively identified',bench_position=pos,hp_now=h,hp_max=m,hp_max_basis='Printed filmed HP; no maximum-HP modifier observed',damage=m-h,attached_energy=dict(total=sum(e.values()),by_type=e),tool=tool,special_conditions=['Poisoned'] if poison else [],active_effects=['Basic ability suppressed by Alolan Muk Power of Alchemy'] if supp and n!='Alolan Muk' and n!='Dragonair' else (['Seal of Antiquity prevents attack while required Regis are absent'] if n=='Regigigas' else []),status='observed',limit_reason=None,evidence_ids=[])
def zone(typ,available,nexttyp):return dict(this_turn=dict(type=typ,count=1 if available else 0,available=available),next=dict(type=nexttyp,count=None,available=None),basis='Visible current orb and small next-type preview',evidence_ids=[],limit_reason='Next preview establishes type only, not future Energy count or availability')
R=lambda en=0,tool='none',h=150,supp=False:mon('Regigigas',h,150,{'Darkness':en} if en else {},tool,supp=supp)
G=lambda h=60,en=0:mon('Glimmet',h,60,{'Darkness':en} if en else {})
M=lambda h=90:mon('Glimmora',h,90,{'Darkness':1})
D=lambda h=60,en={},pois=False:mon('Dratini',h,60,en,poison=pois)
A=lambda h=40,en={}:mon('Dragonair',h,80,en)
P=lambda h=100,en={},pois=False:mon('Drampa',h,100,en,poison=pois)
def state(oa,ob,pa,pb,op=0,pp=0,stad='none',sup=False):
 for i,m in enumerate(ob):m['bench_position']=i+1
 for i,m in enumerate(pb):m['bench_position']=i+1
 return dict(turn_number_displayed=None,phase=None,stadium=stad,owner=dict(active=oa,bench_in_position_order=ob,energy_zone=zone('Darkness',False,'Darkness'),points=op,board_effects=['Alolan Muk: Basic Pokémon in play have no Abilities'] if sup else [],status='observed',evidence_ids=[]),opponent=dict(active=pa,bench_in_position_order=pb,energy_zone=zone(None,False,None),points=pp,board_effects=['Alolan Muk: Basic Pokémon in play have no Abilities'] if sup else [],status='observed',evidence_ids=[]),shared_effects=['Power of Alchemy suppresses Basic abilities; Stage1 Dragonair is unaffected'] if sup else [],evidence_ids=[])
L={'Lightning':1};WL={'Water':1,'Lightning':1}
states=[
 state(G(),[R()],D(),[]),
 state(G(),[R()],D(),[],stad='Mesagoza'),
 state(G(40),[R()],D(en=L),[P()],stad='Mesagoza'),
 state(M(),[R()],D(20,L,True),[P()],stad='Mesagoza'),
 state(M(),[R()],P(en=L),[A()]),
 state(M(),[G(),R(1)],P(60,L,True),[A()]),
 state(M(20),[G(),R(1)],P(50,WL,True),[A(),P()]),
 state(M(20),[G(),R(2,'Heavy Helmet'),mon('Alolan Grimer',70,70)],P(10,WL,True),[A(),P()]),
 state(R(2,'Heavy Helmet'),[G(),mon('Alolan Grimer',70,70)],P(),[A(en=L)],op=1),
 state(R(3,'Heavy Helmet',supp=True),[mon('Glimmet',60,60,supp=True),mon('Alolan Muk',110,110,{'Colorless':1})],A(en=L),[],op=2,sup=True),
 state(R(3,'Heavy Helmet',130,True),[mon('Glimmet',60,60,supp=True),mon('Alolan Muk',110,110,{'Colorless':1})],A(en=WL),[mon('Dratini',60,60,supp=True,pos=3)],op=2,sup=True),
 state(R(3,'Heavy Helmet',supp=True),[mon('Glimmet',60,60,supp=True),mon('Alolan Muk',110,110,{'Colorless':1})],A(en=WL),[mon('Dratini',60,60,supp=True,pos=3)],op=2,sup=True)
]
# Preserve physical Bench positions, including vacated center and right-side slots.
for k in [8,9,10,11]:states[k]['owner']['bench_in_position_order'][-1]['bench_position']=3
for k in [10,11]:states[k]['opponent']['bench_in_position_order'][0]['bench_position']=3
starts=[40,64,109,142,210,233,278,306,374,410,432]
ends=[64,109,142,210,233,278,306,374,410,432,454]
anchors=[44,66,112,144,213,234,281,311,377,412,437]
endanchors=[64,108,144,209,234,278,306,374,409,431,453]
drawends={1:43,3:111,5:212.5,7:280.5,9:377.4,11:435.4}
selected={1:44,3:112,5:212.6,7:280.6,9:378.4,11:436.4}
candidate={1:[44,46,49],3:[112,114,117],5:[213.5,215.5,218.5],7:[281.5,283.5,286.5],9:[378.4,380.4,383.4],11:[436.4,438.4,441.4]}
first={1:47,3:113.5,5:212.85,7:281.1,9:379.1,11:440}
before={1:63,3:134,5:224,7:298,9:391,11:449}
sn={1:['Mesagoza','Rare Candy','Glimmora',"Professor's Research"],3:['Rare Candy','Glimmora','Lucky Ice Pop','Alolan Muk','Heavy Helmet'],5:['Rare Candy','Alolan Muk','Heavy Helmet','Lucky Ice Pop','Poké Ball'],7:['Rare Candy','Alolan Muk','Heavy Helmet','Lucky Ice Pop','Poké Ball'],9:['Rare Candy','Alolan Muk','Lucky Ice Pop',"Professor's Research"],11:['Rare Candy','Lucky Ice Pop','Ilima','Kingambit','Lucky Ice Pop']}
en={1:['Rare Candy','Glimmora','Lucky Ice Pop','Alolan Muk'],3:['Rare Candy','Alolan Muk','Heavy Helmet','Lucky Ice Pop'],5:['Rare Candy','Alolan Muk','Heavy Helmet','Lucky Ice Pop'],7:['Rare Candy','Alolan Muk','Lucky Ice Pop'],9:['Rare Candy','Lucky Ice Pop','Ilima','Kingambit'],11:['Rare Candy','Lucky Ice Pop','Ilima','Kingambit','Lucky Ice Pop']}
fans={1:4,3:4,5:4,7:5,9:3,11:3}
actions={
1:[('card_play','Mesagoza',47,'Stadium','Placed Mesagoza'),('stadium_effect','Mesagoza',52,'owner deck','Accepted use prompt; tails at56, no card found'),('card_play',"Professor's Research",58,'owner hand','Draws Lucky Ice Pop then Alolan Muk'),('end_turn',None,63,None,'Ended turn; no Energy available going first')],
2:[('bench','Drampa',73,'opponent Bench1','Benched Drampa100'),('stadium_effect','Mesagoza',83,'opponent deck','Tails; no card found'),('energy_attachment',None,91,'Dratini','One Lightning attached'),('attack','Dratini',99,'Glimmet','Slam: one heads, one tails;20 damage')],
3:[('evolution','Glimmora',114,'Active Glimmet','Evolved with20 damage carried;70/90 HP'),('stadium_effect','Mesagoza',118,'owner deck','Tails, no card found'),('energy_attachment',None,124,'Glimmora','One Darkness attached'),('card_play','Lucky Ice Pop',126,'Glimmora','Healed20 to90; heads132 returns item to hand'),('attack','Glimmora',136,'Dratini','Venomous Hit30 and Poison')],
4:[('evolution','Dragonair',150,'Dratini','Evolved;40 damage remains,40/80 HP; poison removed'),('card_play',"Professor's Research",169,'opponent hand','Two hidden draws'),('stadium_effect','Mesagoza',176,'opponent deck','Tails180; no card found'),('card_play','Field Blower',183,'Mesagoza','Stadium removed'),('energy_attachment',None,193,'Dragonair','One Water attached; now Water+Lightning'),('retreat','Dragonair',197,'Drampa','Paid one Water and one Lightning; Drampa promoted with no Energy'),('ability','Dragonair',201,'Drampa','Dragon’s Blessing recovers discarded Lightning to Active Drampa'),('end_turn',None,209,None,'Ended without attack; Drampa has one Energy')],
5:[('card_play','Poké Ball',214,'owner deck','Found Glimmet'),('bench','Glimmet',220,'owner Bench1','Benched Glimmet60'),('energy_attachment',None,223,'Regigigas','One Darkness attached'),('attack','Glimmora',226,'Drampa','Venomous Hit30 and Poison')],
6:[('energy_attachment',None,242,'Drampa','One Water attached; now Water+Lightning'),('card_play',"Professor's Research",249,'opponent hand','Two hidden draws'),('card_play','Poké Ball',255,'opponent deck','One Basic added; search identity hidden, later Drampa bench observation separate'),('bench','Drampa',261,'opponent Bench2','Second Drampa100 benched'),('ability','Dragonair',266,'Drampa','Dragon’s Blessing recovers one Water from discard; Drampa2Water+Lightning'),('attack','Drampa',273,'Glimmora','Power Blast70; Glimmora90 to20; random Water discarded')],
7:[('card_play','Poké Ball',283,'owner deck','Found Alolan Grimer'),('bench','Alolan Grimer',289,'owner Bench3','Benched70 HP'),('card_play','Heavy Helmet',292,'Regigigas','Tool attached to Regigigas, not Glimmora'),('energy_attachment',None,297,'Regigigas','Second Darkness attached'),('attack','Glimmora',300,'Drampa','Venomous Hit30; Drampa50 to20; Poison retained')],
8:[('card_play','Copycat',321,'opponent hand','Shuffled hand and drew three hidden cards to match owner three-card hand'),('ability','Dragonair',339,'Drampa','Recovers Water from discard, Drampa2Water+Lightning'),('energy_attachment',None,342,'Dragonair','One Lightning attached to Benched Dragonair'),('attack','Drampa',350,'Glimmora','Power Blast70 knocks out20HP Glimmora; Water discarded')],
9:[('evolution','Alolan Muk',380,'Alolan Grimer','Evolved to110 HP; Power of Alchemy suppresses Basic abilities'),('energy_attachment',None,383,'Regigigas','Third Darkness attached'),('card_play',"Professor's Research",384,'owner hand','Draws Ilima then Kingambit'),('attack','Regigigas',394,'Drampa','Giga Turbo100 KOs second Drampa; nested one Colorless Energy from Energy Zone attached to Bench Alolan Muk')],
10:[('energy_attachment',None,413,'Dragonair','One Water attached; now Water+Lightning'),('bench','Dratini',417,'opponent Bench3','Benched Dratini60'),('attack','Dragonair',429,'Regigigas','Draconic Whip40 reduced by Heavy Helmet to20; Regigigas150 to130')],
11:[('card_play','Lucky Ice Pop',441,'Regigigas','Healed20 from130 to150; heads448 returns item to hand')]
}
draws={1:[('normal_draw',None,None,[("Professor's Research",42)]),('supporter_draw',"Professor's Research",3,[('Lucky Ice Pop',61),('Alolan Muk',62)])],3:[('normal_draw',None,None,[('Heavy Helmet',111)])],5:[('normal_draw',None,None,[('Poké Ball',212)]),('search','Poké Ball',1,[('Glimmet',216)])],7:[('normal_draw',None,None,[('Poké Ball',280)]),('search','Poké Ball',1,[('Alolan Grimer',285)])],9:[('normal_draw',None,None,[("Professor's Research",376)]),('supporter_draw',"Professor's Research",3,[('Ilima',387.5),('Kingambit',388.5)])],11:[('normal_draw',None,None,[('Lucky Ice Pop',434)])]}
nativefiles=[f for f in (p/'turn_evidence').glob('t*.jpg') if '_' not in f.stem]
nearest=lambda t:min([float(f.stem[1:]) for f in nativefiles],key=lambda x:abs(x-t))
turns=[]
for i in range(11):
 n=i+1;owner=n%2==1;start=copy.deepcopy(states[i]);after=copy.deepcopy(states[i+1]);start['turn_number_displayed']=n;after['turn_number_displayed']=n;start['phase']='after normal draw before first voluntary action';after['phase']='After ending action, effects, replacements and checkup resolve'
 for b,t in [(start,anchors[i]),(after,endanchors[i])]:
  b['evidence_ids']=refs(t)
  for pl in ['owner','opponent']:
   b[pl]['evidence_ids']=refs(t);b[pl]['energy_zone']['evidence_ids']=refs(t)
   for m in [b[pl]['active']]+b[pl]['bench_in_position_order']:m['evidence_ids']=refs(t)
 start['owner']['energy_zone']=zone('Darkness',owner and n>1,'Darkness');start['owner']['energy_zone']['evidence_ids']=refs(anchors[i])
 start['opponent']['energy_zone']=zone('Lightning' if n in [2,8] else 'Water' if n in [4,6,10] else None,not owner,'Water' if n in [2,4,8,10] else 'Lightning' if n==6 else None);start['opponent']['energy_zone']['evidence_ids']=refs(anchors[i])
 after['owner']['energy_zone']['evidence_ids']=refs(endanchors[i]);after['opponent']['energy_zone']['evidence_ids']=refs(endanchors[i]);after['opponent']['energy_zone']['next']['type']='Water' if n<=5 or n>=8 else 'Lightning'
 hs=hand(sn[n],selected[n]) if owner else dict(cards_left_to_right=None,count=None,status='hidden',basis='Opponent card backs; identities hidden',evidence_ids=refs(anchors[i]),limit_reason='Opponent hand cannot be named from backs')
 oh=hs if owner else hand(en[n-1],anchors[i],basis='Owner hand remained visible from preceding turn')
 plays=[]
 for j,(kind,name,t,target,result) in enumerate(actions[n]):
  energy=None
  if kind=='energy_attachment':energy=dict(type='Darkness' if owner else ('Lightning' if n in [2,8] else 'Water'),count=1,destination=target,retreat_payment_by_type=None)
  if kind=='retreat':energy=dict(type=None,count=2,destination=None,retreat_payment_by_type={'Water':1,'Lightning':1})
  plays.append(dict(order=j+1,kind=kind,card_name=name,target=target,energy=energy,result=result,prompt_text='Use the effect of Mesagoza?' if kind=='stadium_effect' and owner else None,response='Yes' if kind=='stadium_effect' and owner else None,nested_events_in_order=[result] if kind in ['attack','card_play','ability','stadium_effect'] else [],hand_count_after=None,source_video=v,source_sha256=sha,timestamp_seconds=t,evidence_ids=refs(nearest(t)),basis='Observed source action and result',limit_reason='Timestamp is an inspected event anchor, not measured animation boundary'))
 ds=[]
 for kind,cause,order,cards in draws.get(n,[]):
  ds.append(dict(kind=kind,caused_by=cause,linked_play_order=order,cards_in_reveal_order=[dict(name=name,reveal_position=k+1,source_video=v,source_sha256=sha,timestamp_seconds=t,evidence_ids=refs(nearest(t)),basis='Visible individual reveal and hand addition',limit_reason=None) for k,(name,t) in enumerate(cards)],hand_count_before=None,hand_count_after=None,returned_or_discarded_cards=[],source_video=v,timestamp_seconds=cards[0][1],evidence_ids=refs(nearest(cards[0][1])),limit_reason=None))
 if not owner:
  ds=[dict(kind='normal_draw',caused_by=None,linked_play_order=None,cards_in_reveal_order=[dict(name=None,reveal_position=1,source_video=v,source_sha256=sha,timestamp_seconds=starts[i],evidence_ids=refs(anchors[i]),basis='Hidden opponent normal draw',limit_reason='Card back only')],evidence_ids=refs(anchors[i]),limit_reason='Opponent drawn identities hidden')]
  for j,a in enumerate(actions[n]):
   if a[1] in ["Professor's Research",'Copycat','Poké Ball']:
    cnt=2 if a[1]=="Professor's Research" else 3 if a[1]=='Copycat' else 1
    ds.append(dict(kind='search' if a[1]=='Poké Ball' else 'supporter_draw',caused_by=a[1],linked_play_order=j+1,cards_in_reveal_order=[dict(name=None,reveal_position=k+1,source_video=v,source_sha256=sha,timestamp_seconds=a[2],evidence_ids=refs(nearest(a[2])),basis='Hidden opponent additions',limit_reason='No face-up reveal establishes identity') for k in range(cnt)],evidence_ids=refs(nearest(a[2])),limit_reason='Reveal order/identities hidden'))
 auto=[]
 if n in [3,5,6,7]:auto=[dict(event='Poison checkup',result={3:'Dratini30 to20',5:'Drampa70 to60',6:'Drampa60 to50',7:'Drampa20 to10'}[n],evidence_ids=refs(endanchors[i]))]
 if n==8:auto=[dict(event='Shattering Crystal heads',result='Owner Glimmora KO awards opponent0 points',evidence_ids=refs(358)),dict(event='Owner replacement',result='Regigigas promoted after Glimmora KO',evidence_ids=refs(364)),dict(event='Poison checkup',result='First Drampa10 to0; owner gains1 point',evidence_ids=refs(369)),dict(event='Opponent replacement',result='Second Drampa100 promoted',evidence_ids=refs(374))]
 if n==9:auto=[dict(event='Knockout',result='Second Drampa KO; owner gains second point',evidence_ids=refs(402)),dict(event='Opponent replacement',result='Dragonair40 promoted',evidence_ids=refs(409))]
 if n==11:auto=[dict(event='Opponent concession',result='Your opponent conceded452; Victory456; final2-0',evidence_ids=refs(452,456,472))]
 he=hand(en[n] if owner else en[n-1],endanchors[i])
 if n==11:he=hand(en[n],453)
 turns.append(dict(turn_number=n,who_played='owner' if owner else 'opponent',source_video=v,source_sha256=sha,timing=dict(start_seconds=starts[i],draw_animation_end_seconds=drawends.get(n),first_voluntary_move_seconds=first.get(n,actions[n][0][2]),before_end_action_seconds=before.get(n,actions[n][-1][2]),end_after_resolution_seconds=ends[i]),hand_at_start=hs,owner_hand_start=oh,opponent_hand_at_owner_turn_start=dict(count=fans.get(n),supported_range=None,count_method='Count separate visible card-back edges in native top crop',basis='Observed fan count' if owner else 'Not owner turn',evidence_ids=refs(selected[n]) if owner else [],limit_reason=None if owner else 'Not applicable'),draws_and_searches=ds,plays_in_order=plays,automatic_events_in_order=auto,board_at_start=start,board_after=after,owner_hand_end=he,owner_hand_before_end_action=hand(en[n],before[n]) if owner else None,discard_snapshot_ids=[],turn_evidence_ids=refs(anchors[i],endanchors[i]),limits=['No opened discard pile shown. Opponent hidden identities remain unknown. Next Energy preview does not prove future count.']))
turns[0]['owner_hand_end']['reconciliation']='4 post-draw - Mesagoza - Research +2 =4'
for n,txt in {3:'5 - evolution - Ice Pop + Ice Pop return =4',5:'5 - Poké Ball + Glimmet search - bench =4',7:'5 - Poké Ball + Grimer search - bench - Helmet =3',9:'4 - Muk evolution - Research +2 =4',11:'5 - Ice Pop + heads return =5'}.items():turns[n-1]['owner_hand_end']['reconciliation']=txt
for n in [3,5,7,9,11]:turns[n-1]['owner_hand_end']['reconciliation_basis']='Counted native hand plus observed additions/removals; arithmetic separate from card identity'
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=sources,source_video=v,source_sha256=sha,turns=turns,limits=['All eleven recorded turns covered; source-local anchor times approximate. No hidden-card reconstruction.']))
opening=['Regigigas','Mesagoza','Rare Candy','Glimmet','Glimmora']
limits=['No opened discard pile, no complete discard scroll for either player.','Opponent drawn/searched card identities stay hidden except publicly played cards.','Exact artwork/rarity unverified; filmed QR establishes semantic entities only.','Fresh live Pause Games deck snapshot pending root retrieval; filmed exact20 is separate.','Some draw candidates occur after an immediate first play; denser pre-play anchors retained.','Turn11 ends by opponent concession; before-end hand uses post-heal/pre-concession view, not End Turn.']
save('PAUSE_GAME.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,review_date='2026-10-13',sources=sources,source_video=v,source_sha256=sha,destination='https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',deck_name='New deck16: Glimmora / Alolan Muk / Regigigas',opening=dict(source_video=v,timestamp_seconds=27,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=hand(opening,27)['cards_left_to_right'],selected_active=dict(name='Glimmet',opening_position=4,source_video=v,timestamp_seconds=30,evidence_ids=refs(30)),redraw_or_replacement='No redraw shown',before_active_placement=True,status='observed',evidence_ids=refs(27),limit_reason=None),packet_files=dict(prose='REVIEW.md',coverage='COVERAGE.md',deck='DECK_USED.json',turns='TURN_LEDGER.json',evidence='TURN_EVIDENCE.json'),capture_status='complete_with_recording_limits',battle_review_status='full_source_review_submitted_for_independent_acceptance',outcome=dict(result='win',method='opponent_concession',opponent='gimt',points_owner=2,points_opponent=0,turn_count=11,evidence_ids=refs(452,456,472)),limits=limits,lead_checked=False))
q=json.loads((p/'QR_DECODE.json').read_text(encoding='utf-8'))
save('DECK_USED.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=sources,source_video=v,source_sha256=sha,deck_name_in_log=None,source_url='https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',captured_at=None,log_list_version=None,expected_card_count=20,cards_in_log_order=None,counts_by_name_and_variant=None,energy_configuration_from_log=None,actual_card_count=None,capture_source_text_or_image=None,game_version_binding_basis='Filmed New deck16 QR at3s proceeds directly to this one match; no intervening deck change shown. Fresh live log retrieval remains pending.',conflicts_with_filmed_cards=[],exact_list_status='fresh_live_snapshot_unavailable_pending_root',filmed_qr_exact20=dict(payload=q['payload'],card_slot_count=20,cards_in_qr_order=q['slots'],counts_by_name_and_variant=[dict(name=c['name'],variant='semantic entity; exact printing unknown',count=c['count']) for c in q['cards']],energy_configuration=q['energy'],receipt='QR_DECODE.json',native_frame='turn_evidence/t0003.00.jpg'),limits=['Historical accepted47-game27-deck readback is not a current retrieval. Root will append fresh saved-list supplement; this frozen filmed source is not described as copied from live log.']))
# Crops are saved only for opening, draw-relative, start-hand/fan and ending-hand evidence.
cropids={27}
for n in drawends:cropids.update(candidate[n]);cropids.update([selected[n],before[n],endanchors[n-1]])
cropids.update([anchors[i] for i in range(11)])
frames=[]
for f in sorted(nativefiles):
 t=float(f.stem[1:]);n=next((i+1 for i in range(11) if starts[i]<=t<ends[i]),None)
 role='opening_hand' if t==27 else 'source_action_board_or_result'
 offset=None;de=None
 for nn,ts in candidate.items():
  if t in ts:role='draw_timed_candidate';n=nn;de=drawends[nn];offset=t-de
 if n in before and t==before[n]:role='before_end_hand'
 bc={};tc={}
 if t in cropids:
  with Image.open(f) as im:
   bottom=f.with_name(f.stem+'_bottom.jpg');top=f.with_name(f.stem+'_top.jpg');im.crop((0,2025,1170,2532)).save(bottom,quality=95);im.crop((0,0,1170,730)).save(top,quality=95)
  bc=dict(path=str(bottom.relative_to(p)),pixel_bounds_x0_y0_x1_y1=[0,2025,1170,2532]);tc=dict(path=str(top.relative_to(p)),pixel_bounds_x0_y0_x1_y1=[0,0,1170,730])
 beforefirst=(n in first and t<first[n]) if n else None
 frames.append(dict(evidence_id=eid(t),role=role,turn_number=n,who_played=('owner' if n%2 else 'opponent') if n else None,source_video=v,source_sha256=sha,draw_animation_end_seconds=de,requested_source_seconds=t,actual_frame_seconds_if_measured=None,offset_after_draw_seconds=offset,full_frame_path=str(f.relative_to(p)),native_dimensions=dict(width=1170,height=2532),bottom_crop=bc,top_crop=tc,selected_for_start_hand=t in selected.values(),before_first_play=beforefirst,unzoomed=t in selected.values() or t in before.values(),hand_spread=t in selected.values(),observation='See linked turn ledger and prose for named observations',suitability_or_limit='Later candidate already contains play/zoom; not substituted for first hand' if offset is not None and not beforefirst else None,image_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
overview=[]
for f in sorted((p/'overview/sample_frames').glob('*.jpg')):overview.append(dict(evidence_id='o'+f.stem,source_video=v,source_sha256=sha,requested_source_seconds=(int(f.stem)-.5)*6,path=str(f.relative_to(p)),dimensions=dict(width=390,height=844),role='coarse action locator only'))
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=sources,source_video=v,source_sha256=sha,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,bottom_crop_height_fraction=.2,top_crop='Actual bounds [0,0,1170,730]',fixed_grid_is_turn_start_evidence=False,discard_target_every_owner_turns=[2,3]),frames=frames,overview_frames=overview,discard_snapshots=[dict(snapshot_id='discard-not-shown-'+str(pl),turn_number=None,pile_owner=pl,source_video=v,source_sha256=sha,timestamp_seconds=None,cards_in_view=None,scroll_coverage='No opened discard view anywhere in supplied source',full_pile_established=False,evidence_ids=[],limit_reason='Source never opens pile; visible discard top cards and public plays are not a complete pile snapshot') for pl in ['owner','opponent']],scheduled_capture_limits=limits))
time=json.loads((p/'SOURCE_TIME.json').read_text(encoding='utf-8'))
save('SUMMARY.json',dict(source_video=v,source_sha256=sha,game_id=gid,classification='human_battle',auto_option_visible=False,queue='B4b emblem event progress shown after match; exact matchmaking queue text not separately visible',opponent='gimt',owner='Dacz8976',result='win',method='opponent_concession',turn_count=11,source_game_count=1,match_date=time['match_date_local'],match_date_basis='SOURCE_TIME.json UTC creation metadata converted to Chicago; filmed20:00 clock corroborates',owner_points=2,opponent_points=0,damage_done=190,result_evidence=[dict(source_seconds=452,text='Your opponent conceded',evidence_id=eid(452)),dict(source_seconds=456,text='Victory!',evidence_id=eid(456)),dict(source_seconds=472,text='vs.gimt Victory; turns11; points2-0; damage190',evidence_id=eid(472))],capture_status='complete_with_recording_limits',review_status='submitted_for_independent_acceptance',deck_status='filmed_exact20_resolved; fresh live retrieval pending',visible_core=['Glimmora','Glimmet','Alolan Muk','Alolan Grimer','Regigigas'],full_filmed_deck_receipt='QR_DECODE.json'))
save('UNCERTAINTIES.json',dict(source_video=v,source_sha256=sha,game_id=gid,limits=limits,unresolved=[dict(topic='Fresh live deck snapshot',status='pending_root_retrieval',reason='Browser approval outstanding; no current retrieved list fabricated'),dict(topic='Opponent hidden hand',status='recording_limit',reason='Card backs do not show identities or exact order'),dict(topic='Exact artwork and rarity',status='recording_limit',reason='QR identifies semantic playable entity, not printing'),dict(topic='Next Energy count',status='recording_limit',reason='Preview type is not future count')],unreviewed_intervals=[]))
lines=['# Full source review: '+v,'','Reviewer: /root/remaining_010003, gpt-6.1-sol, high. Reviewed October13,2026. Submitted for independent acceptance.','',f'Source SHA256: {sha}. Duration479.441667s,886389142 bytes, native1170x2532. One uninterrupted recorded match, setup through results. Match date October12,2026,20:00 Chicago per SOURCE_TIME.json and filmed phone clock.','', 'Owner Dacz8976 wins by gimt concession at452s. Native472s results explicitly show11 turns,2-0 points and190 damage done. No visible Auto option. B4b emblem progress appears after results; exact matchmaking queue text was not displayed.','', 'At0-3s New deck16 and its exact20-card Darkness QR are filmed, followed by direct matchmaking. QR_DECODE.json retains the byte payload and semantic mapping. DECK_USED.json keeps this separate from the pending fresh live Pause Games list.','', 'At27s all five opening cards appear left to right: Regigigas, Mesagoza, Rare Candy, Glimmet, Glimmora. Glimmet is selected Active at30s; Regigigas goes to center Bench at32s. No redraw shown. Opponent starts Dratini60. Native setup anchors: [27s](turn_evidence/t0027.00.jpg), [30s](turn_evidence/t0030.00.jpg), [32s](turn_evidence/t0032.00.jpg).','', '| Turn | Player | Source interval | Account and evidence |','|---|---|---|---|']
for tr in turns:
 n=tr['turn_number'];a=tr['timing']['start_seconds'];b=tr['timing']['end_after_resolution_seconds'];txt='; '.join(f"{pl['order']}. {pl['card_name'] or pl['kind']} at{pl['timestamp_seconds']}s: {pl['result']}" for pl in tr['plays_in_order'])
 if tr['automatic_events_in_order']:txt+='; Automatic: '+'; '.join(e['result'] for e in tr['automatic_events_in_order'])
 if n%2:txt+=f". Ending hand {tr['owner_hand_end']['count']}: {', '.join(en[n])}. {tr['owner_hand_end']['reconciliation']}."
 txt+=f' Ledger TURN_LEDGER.json row{n}; [native start](turn_evidence/t{anchors[n-1]:07.2f}.jpg), [native ending](turn_evidence/t{endanchors[n-1]:07.2f}.jpg).'
 lines.append(f'| {n} | {tr["who_played"]} | {a}-{b}s | {txt} |')
lines+=['','The owner prepares Regigigas while Glimmora applies poison. The lucky Shattering Crystal heads at358s denies the opponent a point, and poison subsequently earns the first owner point. Alolan Muk on turn9 suppresses Basic abilities, removing Regigigas’ Seal of Antiquity attack restriction. Dragonair is Stage1 and retains Dragon’s Blessing. The filmed Dragonair ability retrieves Energy from discard to Active while Benched; it does not generate an Energy-Zone attachment. Regigigas Giga Turbo supplies one Colorless Energy to Bench Alolan Muk after its attack.','', 'Heavy Helmet is attached to Regigigas, not Glimmora. It reduces the turn10 Draconic Whip40 to20. Atturn11 Lucky Ice Pop restores that20 and flips heads. The owner opens Regigigas’ attack menu at450s, but the opponent concedes before another attack resolves. Inspection is not an attack. No unselected option is labelled a decline.','', 'Owner post-draw hands and native bottom-fifth/top crops are linked in TURN_LEDGER.json and TURN_EVIDENCE.json. Draw-end offsets are approximate observed animation boundaries. Turns5 and7 have immediate first plays; denser pre-play frames are retained and later scheduled candidates are labelled unsuitable. Opponent fans at owner-turn starts count4,4,4,5,3,3 backs; hidden identities remain unknown.','', 'No discard pile is opened anywhere in the source. Both players’ public discard-top observations and narrated actions do not establish complete piles. No absent discard snapshots are fabricated. Maximum HP is taken from filmed card text and carries no inferred modifier. Next Energy preview gives type only, not future count.','', 'Results continue456-479.441667s through Victory, card-of-game Regigigas and emblem progress. Fresh live log binding remains pending root retrieval, so this is a complete local full-source review with recording limits and a filmed exact20, awaiting independent acceptance and live supplement.']
(p/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(p/'COVERAGE.md').write_text('# Source coverage\n\n'+v+'\nSHA256 '+sha+'\n\n- 0-21s: deck screen, QR, matchmaking, versus identity.\n- 21-40s: opening five, Active/Bench setup, opponent Active.\n'+''.join(f'- Turn{n}: {starts[n-1]}-{ends[n-1]}s, full action/board/hand account in TURN_LEDGER.json row{n}; native start{anchors[n-1]}s and ending{endanchors[n-1]}s.\n' for n in range(1,12))+'- 454-479.441667s: Victory and full results; no second game or split clip.\n\nMethod: six-second coarse locating across entire source, then bounded native action/board/reveal captures and denser immediate-play windows. The overview is not substituted for native owner hand evidence. Eleven ledger rows match the filmed result screen. No unreviewed source interval remains. No source edit, external write, shared registration, move or lead acceptance was performed by this worker.\n',encoding='utf-8')
print('Wrote all eight review components; independent acceptance remains required.')
# Historical exact list is a dated log snapshot, explicitly not a fresh readback.
cat=json.loads((p.parent/'HISTORICAL_DECK_CATALOG.json').read_text(encoding='utf-8'))
hist=next(d for d in cat['decks'] if d['code']==q['payload'])
save('HISTORICAL_DECK_MATCH.json',dict(source_video=v,source_sha256=sha,artifact_url=cat['artifact_url'],retrieved_utc=cat['retrieved_utc'],historical=True,fresh_live_readback=False,raw_deck=hist,source_catalog='../HISTORICAL_DECK_CATALOG.json',source_catalog_sha256=hashlib.sha256((p.parent/'HISTORICAL_DECK_CATALOG.json').read_bytes()).hexdigest(),payload_exact_match=True,limits=['Historical raw source text preserves original corrupted characters. Authored semantic names below are resolved from byte-matching filmed QR.']))
deck=json.loads((p/'DECK_USED.json').read_text(encoding='utf-8'))
slots=[];counts=[]
for count,name,variant in hist['rows']:
 if name.startswith('Pok'):name='Poké Ball'
 if name.startswith('Professor'):name="Professor's Research"
 slots.extend([dict(name=name,variant=variant,variant_basis='historical log label; filmed artwork/rarity unverified') for _ in range(int(count))]);counts.append(dict(name=name,variant=variant,count=int(count)))
assert len(slots)==sum(c['count'] for c in counts)==20
deck.update(deck_name_in_log=hist['name'],captured_at=cat['retrieved_utc'],log_list_version='Historical accepted27-deck catalog; current access blocked',cards_in_log_order=slots,counts_by_name_and_variant=counts,energy_configuration_from_log=['Darkness'],actual_card_count=20,capture_source_text_or_image='HISTORICAL_DECK_MATCH.json',exact_list_status='historical_exact20_verified_not_fresh',historical=True,fresh_live_readback=False)
save('DECK_USED.json',deck)
