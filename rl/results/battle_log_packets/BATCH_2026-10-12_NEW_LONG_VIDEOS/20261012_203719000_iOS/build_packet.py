import json,copy,shutil
from pathlib import Path
from PIL import Image
from observations import *
from zone_observations import OWNER_START,OPPONENT_START,OWNER_END,OPPONENT_END,LIMITS
p=Path(__file__).parent;tpl=Path('Review_Log/templates/pause_games')
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8'));video=src['video_basename'];sha=src['sha256'];gid='20261012_203719000_iOS-game-1'
sources=[dict(video_basename=video,sha256=sha,source_json='SOURCE.json')]
def save(n,o):(p/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def template(n):return json.loads((tpl/n).read_text(encoding='utf-8'))
def eid(t):return 'f'+f'{t:.2f}'.replace('.','_')
def retain(t):
 name=f't{t:07.2f}.jpg';dest=p/'turn_evidence'/name
 if not dest.exists():
  for folder in ['dense','overview','intake']:
   q=p/folder/name
   if q.exists():shutil.copy2(q,dest);break
 if not dest.exists():raise RuntimeError(name)
 return dest
def mon(name,hp,mx,e=0,ty='Darkness',tool='none',poison=False):
 return dict(name=name,variant={'Glimmora':'Shattering Crystal / Venomous Hit','Drampa':'Power Blast 70','Kingambit':"Overlord's Blade",'Alolan Muk':'Power of Alchemy','Dragonair':"Dragon's Blessing",'Mega Rayquaza ex':'Mega Burst 50x'}.get(name),bench_position=None,hp_now=hp,hp_max=mx,hp_max_basis='Visible card and HP display',damage=mx-hp,attached_energy=dict(total=e,by_type={} if e==0 else ({ty:e} if isinstance(ty,str) else ty)),tool=tool,special_conditions=['Poisoned'] if poison else [],active_effects=[],evidence_ids=[],status='observed',limit_reason=None)
def owner(n):
 R=lambda h,e:mon('Regigigas',h,150,e);M=lambda e:mon('Alolan Muk',110,110,e);G=lambda h,e:mon('Glimmora',h,90,e);K=lambda e:mon('Kingambit',140,140,e,tool='Heavy Helmet' if n>=11 else 'none');P=lambda e:mon('Pawniard',50,50,e);g=lambda:mon('Glimmet',60,60)
 if n==0:return R(150,0),[None,None,P(0)]
 if n<=2:return R(150,0),[mon('Alolan Grimer',70,70),None,P(0)]
 if n<=4:return R(80 if n==4 else 150,1),[M(0),g(),P(0)]
 if n<=6:return R(10 if n==6 else 80,1),[M(0),G(90,0),P(1)]
 if n==7:return G(90,1),[M(0),R(150,0),K(1)]
 if n<=11:return R(10 if n>=10 else 80,0),[M(2 if n==11 else (1 if n>=9 else 0)),G(90,1),K(1)]
 if n==12:return G(90,1),[M(2),None,K(1)]
 if n<=14:return G(20 if n==14 else 90,1),[M(2),g(),K(2)]
 if n<=17:return G({15:80,16:10,17:70}[n],1),[M(3),G(90,1 if n==17 else 0),K(2)]
 if n<=19:return G(90,1),[M(3),None,K(3 if n==19 else 2)]
 return K(3),[M(3),None,None]
def opponent(n):
 D=lambda hp,e,ty,po=False:mon('Drampa',hp,100,e,ty,poison=po)
 q=mon('Mega Rayquaza ex',180,180,(0 if n<6 else 1)+(0 if n<4 else (1 if n<12 else 2)),{'Fire':0 if n<6 else 1,'Lightning':0 if n<4 else (1 if n<12 else 2)},tool='Rocky Helmet' if n>=18 else 'none')
 d=lambda evo=False,f=0,l=0:mon('Dragonair' if evo else 'Dratini',80 if evo else 60,80 if evo else 60,f+l,{'Fire':f,'Lightning':l})
 bd=D(100,0 if n<8 else (1 if n<10 else 2),'Fire')
 if n<2:return D(100,0,'Lightning'),[None,q,None]
 if n<=6:return D(100,1,'Lightning'),[bd,q,d(n>=4)]
 if n<=14:return D({7:60,8:90,9:80,10:90,11:80,12:70,13:30,14:40}[n],1,'Lightning',True),[bd,q,d(True,1 if n>=14 else 0)]
 if n==15:return D(100,2,'Fire'),[None,q,d(True,1)]
 if n<=19:return D({16:100,17:60,18:50,19:10}[n],1,'Fire',n>=17),[d(n>=18,1),q,d(True,1)]
 q['attached_energy']={'total':0,'by_type':{}}
 return q,[d(True,1,1),D(10,0,'Fire'),d(True,1)]
def board(n,turn,phase,t):
 oa,ob=owner(n);pa,pb=opponent(n)
 for bs in [ob,pb]:
  for i,m in enumerate(bs,1):
   if m:m['bench_position']=i
 for m in [oa,pa]+[x for x in ob+pb if x]:m['evidence_ids']=[eid(t)]
 boundary='start' if phase=='start' else 'end'
 def zone(player):
  values=(OWNER_START if player=='owner' else OPPONENT_START) if boundary=='start' else (OWNER_END if player=='owner' else OPPONENT_END)
  current,preview=values[turn-1]
  limit=LIMITS.get((boundary,turn,player))
  if current=='U' and not limit:limit='A message or animation covers the generated slot in this exact boundary frame. Current type, count and availability remain unknown.'
  if preview is None:limit=(limit+' ' if limit else '')+'The small next marker is absent or obscured in this frame; its type/count are not inferred.'
  z=dict(this_turn=dict(type=current if current not in ['E','U'] else None,count=0 if current=='E' else (None if current=='U' else 1),available=False if current=='E' else (None if current=='U' else True),visibility='observed_empty' if current=='E' else ('obscured' if current=='U' else 'visible_generated_token')),next=dict(type=preview,count=1 if preview else None,available=None,visibility='visible_preview_icon' if preview else 'absent_or_obscured'),basis='Direct visual audit of this exact native boundary frame, without turn/game-rule defaults',source_video=video,observed_at_source_seconds=t,evidence_ids=[eid(t)],limit_reason=limit,preview_availability_limit='A visible preview icon establishes its displayed type/count, not future availability.')
  if player=='owner' and boundary=='start' and turn in [3,13]:
   dt=107.5 if turn==3 else 468;z['later_within_turn_observation']=dict(source_video=video,observed_at_source_seconds=dt,this_turn={'type':'Darkness','count':1,'available':True},next={'type':None if turn==3 else 'Darkness','count':None if turn==3 else 1,'available':None,'visibility':'absent_or_obscured' if turn==3 else 'visible_preview_icon'},limit_reason='At 107.5 s, the current Darkness token is visible but the small next marker is absent or obscured. No next type, count or availability is inferred.' if turn==3 else None,evidence_ids=[eid(dt)],basis='Visible generated token after the first card selection has begun; not substituted for the earlier preplay boundary.')
  return z
 oz=zone('owner');pz=zone('opponent')
 effect=[] if n<3 else [dict(name='Power of Alchemy',source='owner Alolan Muk',affected='Basic Pokémon on both boards',restriction='Basic Pokémon have no Abilities',expiry='While Muk ability remains active')]
 return dict(turn_number_displayed=turn,phase=phase,stadium='none' if n<2 else ('Rainbow Cave' if n<3 or n>=16 else 'Mesagoza'),owner=dict(active=oa,bench_in_position_order=ob,energy_zone=oz,points=1 if n>=15 else 0,board_effects=effect,evidence_ids=[eid(t)],status='observed',limit_reason=None),opponent=dict(active=pa,bench_in_position_order=pb,energy_zone=pz,points=2 if n>=18 else (1 if n>=12 else 0),board_effects=effect,evidence_ids=[eid(t)],status='observed',limit_reason=None),shared_effects=effect,evidence_ids=[eid(t)])
def hand(names,t):return dict(cards_left_to_right=[dict(position=i,name=name,variant=None,basis='Visible hand and revealed card continuity',evidence_ids=[eid(t)],limit_reason=None) for i,name in enumerate(names,1)],count=len(names),basis='Observed fan, reconciled with individually named additions and removals',evidence_ids=[eid(t)],status='observed',limit_reason=None)
ledger=dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=sources,turns=[],limits=['All requested seek times are source-local, actual frame PTS not measured. Event times and turn boundaries approximate to inspected windows. Hidden opponent identities remain null.'])
allframes=list((p/'turn_evidence').glob('t*.jpg'))+list((p/'dense').glob('t*.jpg'))+list((p/'overview').glob('t*.jpg'))
alltimes=[float(q.stem[1:]) for q in allframes if '_bottom' not in q.stem and '_top' not in q.stem]
for n in range(1,22):
 who='owner' if n%2 else 'opponent';t=STARTS[n-1];end=ENDS[n-1];retain(t);retain(end)
 row=copy.deepcopy(template('TURN_LEDGER.template.json')['turns'][0]);row.update(turn_number=n,who_played=who,source_video=video)
 row['timing']=dict(start_seconds=BOUNDS[n-1],end_seconds=BOUNDS[n],draw_animation_end_seconds=DRAW_END.get(n),draw_end_precision_seconds=0.5 if n in DRAW_END else None,first_voluntary_move_seconds=A[n][0][0],before_end_action_seconds=PRE.get(n),end_after_resolution_seconds=end)
 hidden=dict(cards_left_to_right=None,count=None,basis='Opponent backs / non-acting player',evidence_ids=[eid(t)],status='hidden',limit_reason='Opponent faces hidden; non-acting owner start record not applicable.')
 row['hand_at_start']=hand(HANDS[n],t) if n%2 else copy.deepcopy(hidden);row['owner_hand_start']=hand(HANDS[n],t) if n%2 else copy.deepcopy(hidden)
 fc,fr=FANS.get(n,(None,None));row['opponent_hand_at_owner_turn_start']=dict(count=fc,supported_range=fr,count_method='Distinct visible card-back edges in native top crop',basis='observation',evidence_ids=[eid(t)] if n%2 else [],limit_reason='One overlapping edge uncertain; keep range.' if fr else ('Not owner turn.' if not n%2 else None))
 row['draws_and_searches']=[]
 for kind,c,order,names,dt in DRAWS.get(n,[]):
  if n==3 and order is not None:order={2:1,5:4,7:6}[order]
  retain(dt);row['draws_and_searches'].append(dict(kind=kind,caused_by=c,linked_play_order=order,cards_in_reveal_order=[dict(name=name,reveal_position=i,source_video=video,timestamp_seconds=dt,evidence_ids=[eid(dt)],basis='Visible individual reveals and subsequent hand',limit_reason=None) for i,name in enumerate(names,1)],hand_count_before=None,hand_count_after=None,returned_or_discarded_cards=['Kingambit','Glimmora'] if c=='Copycat' else [],source_video=video,timestamp_seconds=dt,evidence_ids=[eid(dt)],limit_reason=None))
 if not n%2:row['draws_and_searches'].append(dict(kind='normal_draw',caused_by=None,linked_play_order=None,cards_in_reveal_order=[dict(name=None,reveal_position=1,source_video=video,timestamp_seconds=t,evidence_ids=[eid(t)],basis='Hidden opponent back',limit_reason='Face not revealed by normal draw.')],timestamp_seconds=t,evidence_ids=[eid(t)],limit_reason='Opponent identity hidden.'))
 if n in [17,19,21]:
  no_draw_time={17:628,19:722,21:788}[n];retain(no_draw_time);row['draws_and_searches']=[dict(kind='normal_draw_no_effect',cards_in_reveal_order=[],timestamp_seconds=no_draw_time,evidence_ids=[eid(no_draw_time)],limit_reason='Explicit No cards left in deck; unable to draw cards. No draw animation end exists.')]
 row['plays_in_order']=[]
 for i,(at,k,c,target,result) in enumerate(A[n],1):
  nearest=min(alltimes,key=lambda x:abs(x-at));retain(nearest)
  item=copy.deepcopy(template('TURN_LEDGER.template.json')['turns'][0]['plays_in_order'][0]);item.update(order=i,kind=k,card_name=c,target=target,result=result,source_video=video,timestamp_seconds=at,evidence_ids=[eid(nearest)],basis='Observed source sequence',nested_events_in_order=[result],limit_reason=None)
  if n==19 and i==1:
   retain(732);item['evidence_ids']=[eid(722),eid(732)];item['result_observed_at_source_seconds']=732;item['basis']='Attachment action at about 723 s, with preplay board at 722 s and resulting board at 732 s clearly showing three Darkness on Kingambit. The 732 s observation is later than the attachment, not its exact resolution timestamp.'
  if k=='energy_attachment':item['energy']=dict(type='Darkness' if n%2 else ('Lightning' if 'Lightning' in result else 'Fire'),count=1,destination=target,retreat_payment_by_type=None)
  if k=='retreat':item['energy']['retreat_payment_by_type']={'Fire':1};item['limit_reason']='Visible Fire removed. Effective cost explanation not established from zoom.'
  row['plays_in_order'].append(item)
 row['automatic_events_in_order']=[x[4] for x in A[n] if any(k in x[4] for k in ['checkup','Shattering','Power of Alchemy'])]
 row['board_at_start']=board(n-1,n,'start',t);row['board_after']=board(n,n,'after effects, checkups and replacements',end)
 row['owner_hand_end']=hand(END_HANDS[n],PRE[n]) if n%2 else copy.deepcopy(hidden);row['discard_snapshot_ids']=[];row['turn_evidence_ids']=[eid(t),eid(end)]+([eid(PRE[n])] if n%2 else []);row['limits']=['No opened discard-pile view in this turn or elsewhere in the recording.']
 if n%2:row['hand_reconciliation']=dict(start_count=len(HANDS[n]),end_count=len(END_HANDS[n]),basis='Named draws/searches, Trainer removals, evolutions and returned Items in numbered plays.')
 if n==13:row['timing']['draw_end_precision_seconds']=0.1;row['limits'].append('First Glimmet selection begins about 467.1 s, lift at 467.2 s. The clean 466.9 s hand precedes it; 468 s is already after that decision.')
 ledger['turns'].append(row)
save('TURN_LEDGER.json',ledger)
lines=['# Full battle review: '+video,'','Reviewer: /root/long_203719. Review date: October 12, 2026. Entire source reviewed from 0 to 800.786667 seconds. Submitted for independent acceptance. No external writes or source moves performed.','','One human battle against KCXPF in Deluxe Pack: Mega Emblem Event, explicitly visible at 2 seconds. Dacz8976 went first. No Auto control is visible. Native QR at 0 seconds precedes New deck 16 selection and this battle. The owner wins by explicit opponent concession at 790 seconds. Final points are owner 1, opponent 2. The result screen reports 21 turns and 150 damage done.','','Opening five cards, left to right: Copycat, Regigigas, Kingambit, Professor\'s Research, Pawniard. Regigigas is chosen Active, Pawniard right bench. Evidence: native 28 to 34 seconds.','','| Turn | Player | Source interval (s) | Numbered actions and resolution |','|---|---|---|---|']
for row in ledger['turns']:
 n=row['turn_number'];desc=' '.join(f"{a['order']}. {a['card_name'] or a['kind'].replace('_',' ')}"+(f" to {a['target']}" if a['target'] else '')+f": {a['result']}" for a in row['plays_in_order']);lines.append(f"| {n} | {row['who_played']} | {BOUNDS[n-1]} to {BOUNDS[n]} | {desc} |")
lines+=['','The ledger preserves owner hand names, named draws/searches, numbered plays, both boards and zones, HP, Energy, Tools, conditions, points and turn evidence. For quick first moves, the selected earlier hand view is separate from later +1/+3/+6 candidates. Turns 17, 19 and 21 explicitly cannot draw because the owner deck is empty.','','Hand and Zone evidence repaired after independent checking: turn 13 uses the clean three-card fan at 466.9 s, before Glimmet selection about 467.1 s; 468 s is a later candidate after the first decision. Turn 3 uses the five-card hand at 107.2 s and records its then-empty current Zone, rather than claiming one ready Energy. The generated Darkness is separately visible at 107.5 s while Poké Ball selection has begun. The attachment to Regigigas remains near 150 s. All boundary Zones were audited from their own native frame: an empty current slot has null type, count 0 and false availability; glow/zoom/message-obscured values remain null. Preview icons do not prove future availability. Turn 17 uses the earlier clean two-Ice-Pop hand at 628 s; turns 19 and 21 use clear empty-hand views at 722 and 786 s.','','Key sequence: Ilima saves the damaged Regigigas on turn 7; Cyrus forces it back on turn 8. Its knockout gives the opponent point 1 on turn 12. Three successful Lucky Ice Pop returns heal Glimmora from 20 to 80 on turn 15, then poison knocks out the first opposing Drampa for the owner\'s only point. The first Glimmora knockout awards opponent point 2 on turn 18 after Shattering Crystal fails. The second Glimmora is knocked out for 200 on turn 20, but Shattering Crystal prevents a point. Kingambit is promoted and shows Overlord\'s Blade 180 before the opponent concedes. Kingambit does not attack.','','Recording limits: hidden opponent faces remain unknown, several fan counts preserve ranges, and neither discard pile is opened. Turn 14 has an explicit no-target message with an uncertain trigger label. The turn 20 retreat records visible Fire removal without asserting an unfilmed effective-cost explanation. The exact filmed QR list is separately verified by the lead; a live Pause Games deck list was unavailable. See UNCERTAINTIES.json.','','Packet references: SOURCE.json, SOURCE_TIME.json, PAUSE_GAME.json, DECK_USED.json, TURN_LEDGER.json, TURN_EVIDENCE.json and native turn_evidence frames/crops.']
(p/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
cov=['# Entire source coverage','',f'Source: {video}. SHA-256: {sha}. Duration: 800.786667 seconds.','','Native seeks span the whole battle at two-second intervals, supplemented around draws, first moves, searches, attachments, coins, replacements and the terminal sequence. Overview and targeted frames cover pregame and results.','','- 0 to 4 s: deck QR, event queue and New deck 16 selection.','- 4 to 26 s: matchmaking, opponent identity, coin and order.','- 26 to 44 s: original five cards, Active/bench setup, Ready animation.']
for n in range(1,22):cov.append(f'- Turn {n}: {BOUNDS[n-1]} to {BOUNDS[n]} seconds, {"owner" if n%2 else "opponent"}. Full meaningful actions and resolution checked in ledger row {n}.')
cov+=['- 791 to 800.786667 s: card-of-game animation and complete result screen.','- Targeted independent repairs: native 466.7 to 467.5 s for turn 13 hand/first move, native 107.5 to 107.8 s for turn 3 first card selection, and visual audit of all 42 start/end boundary Zone pairs.','','Exactly one game. No cuts, split continuation or other match found. No unreviewed game phase remains. Hidden facts and missing views remain explicit limits. Independent acceptance is still the lead\'s task.']
(p/'COVERAGE.md').write_text('\n'.join(cov)+'\n',encoding='utf-8')
ev=template('TURN_EVIDENCE.template.json');ev.update(is_template=False,game_id=gid,sources=sources,frames=[],discard_snapshots=[],scheduled_capture_limits=[])
roles={28:('opening_five',None),2:('queue',None),790:('concession',21),800.5:('result',21),800.7:('source_end',None)}
for n in range(1,22):
 roles[STARTS[n-1]]=('selected_start_hand' if n%2 else 'start_board',n);roles[ENDS[n-1]]=('end_board',n)
 if n%2:roles[PRE[n]]=('before_end_hand',n);retain(PRE[n])
 for ct in CAND.get(n,[]):roles[ct]=('draw_relative_candidate',n);retain(ct)
for q in sorted((p/'turn_evidence').glob('t*.jpg')):
 if '_bottom' in q.stem or '_top' in q.stem:continue
 t=float(q.stem[1:]);role,n=roles.get(t,('action_or_refinement',None));bottom=q.with_name(q.stem+'_bottom.jpg');top=q.with_name(q.stem+'_top.jpg')
 with Image.open(q) as im:
  assert im.size==(1170,2532)
  im.crop((0,2025,1170,2532)).save(bottom,quality=94);im.crop((0,100,1170,800)).save(top,quality=94)
 first=A[n][0][0] if n else None;selected=role=='selected_start_hand'
 ev['frames'].append(dict(evidence_id=eid(t),role=role,turn_number=n,who_played=('owner' if n%2 else 'opponent') if n else None,source_video=video,source_sha256=sha,draw_animation_end_seconds=DRAW_END.get(n),requested_source_seconds=t,actual_frame_seconds_if_measured=None,offset_after_draw_seconds=round(t-DRAW_END[n],2) if n in DRAW_END else None,full_frame_path=q.relative_to(p).as_posix(),native_dimensions={'width':1170,'height':2532},bottom_crop=dict(path=bottom.relative_to(p).as_posix(),pixel_bounds_x0_y0_x1_y1=[0,2025,1170,2532]),top_crop=dict(path=top.relative_to(p).as_posix(),pixel_bounds_x0_y0_x1_y1=[0,100,1170,800]),selected_for_start_hand=selected,before_first_play=t<first if first is not None else None,unzoomed=selected,hand_spread=selected,observation='Native source frame retained.',suitability_or_limit='Candidate falls after first play; chosen earlier frame is separate.' if role=='draw_relative_candidate' and t>=first else None))
 if t==466.9:ev['frames'][-1]['observation']='Clean three-card hand left to right: Glimmet, Glimmora, Lucky Ice Pop, before Glimmet selection. Current owner Zone visibly empty during generation.'
 if t==468:ev['frames'][-1].update(selected_for_start_hand=False,before_first_play=False,unzoomed=False,hand_spread=False,observation='Glimmet already selected and moving over middle Bench. Only Glimmora and Lucky Ice Pop remain in bottom fan.',suitability_or_limit='Unsuitable for original three-card preplay hand. Superseded by native 466.9 s.')
 if t==107.2:ev['frames'][-1]['observation']='Five-card hand before Poké Ball selection. Owner current Zone empty and next marker absent during generation; no availability claimed from this frame.'
for n in [1,5,9,13,17,21]:
 for player in ['owner','opponent']:ev['discard_snapshots'].append(dict(snapshot_id=f'discard-{n}-{player}-unavailable',turn_number=n,pile_owner=player,source_video=video,timestamp_seconds=STARTS[n-1],cards_in_view=None,scroll_coverage=None,full_pile_established=False,evidence_ids=[eid(STARTS[n-1])],limit_reason='No opened discard pile anywhere in the complete source. Top visible card or public play history is not a full pile.'))
ev['scheduled_capture_limits']=[dict(turn_number=n,reason='Explicit empty-deck message, no normal draw animation. No fabricated draw-end offsets. Turn-start and before-end views retained.') for n in [17,19,21]]
save('TURN_EVIDENCE.json',ev)
pg=template('PAUSE_GAME.template.json');pg.update(is_template=False,game_id=gid,review_date='2026-10-12',sources=sources,deck_name='New deck 16',capture_status='complete_with_recording_limits',battle_review_status='review_ready_for_independent_acceptance',outcome=dict(owner='win',cause='opponent conceded',owner_points=1,opponent_points=2,turns_played=21,evidence_ids=[eid(790),eid(800.5)]),limits=['Live Pause Games deck list missing; filmed QR list separately verified.','Discard piles never opened.','Some opponent fan overlap counts remain ranges.','Source seek times approximate, actual PTS not measured.'])
pg['opening']=dict(source_video=video,timestamp_seconds=28,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=[dict(position=i,name=name,basis='Observed before Active placement',evidence_ids=[eid(28)],limit_reason=None) for i,name in enumerate(['Copycat','Regigigas','Kingambit',"Professor's Research",'Pawniard'],1)],selected_active=dict(name='Regigigas',opening_position=2,source_video=video,timestamp_seconds=29,evidence_ids=[eid(28),eid(30)]),redraw_or_replacement='none observed',before_active_placement=True,status='observed',evidence_ids=[eid(28)],limit_reason=None)
pg['classification']=dict(opponent_type='human',auto_visible=False,queue='Deluxe Pack: Mega Emblem Event',queue_evidence=eid(2),number_of_games=1);save('PAUSE_GAME.json',pg)
deck=template('DECK_USED.template.json');prepared=json.loads((p.parent/'PREPARED_FILMED_DECK.json').read_text(encoding='utf-8'));deck.update(is_template=False,game_id=gid,sources=sources,deck_name_in_log=None,exact_list_status='missing_live_log_snapshot',limits=['The named new deck was not present as an exact 20-card list in the live Pause Games log checked by the lead. Do not label the QR list as copied from that log.'],filmed_deck_snapshot=dict(provenance='Native filmed QR at 0 s, decoded by lead',deck_label_on_film='New deck 16',qr_decode_file='QR_DECODE.json',prepared_definition='../PREPARED_FILMED_DECK.json',deck=prepared['deck'],game_version_binding_basis='QR immediately precedes event selection and this uninterrupted single battle; played core agrees.'))
save('DECK_USED.json',deck)
summary=dict(source_video=video,sha256=sha,game_id=gid,reviewer='/root/long_203719',review_status='repaired_review_ready_for_fresh_independent_check',review_scope='Entire source 0 to 800.786667 s; setup, all 21 turns, ending and results',review_method='Native 2-second full-battle seeks, 8-second overview, targeted subsecond draw/first-move/action refinements, direct audit of every boundary Zone',opponent='KCXPF',owner='Dacz8976',classification='human_event_battle',queue='Deluxe Pack: Mega Emblem Event',auto_visible=False,outcome='win',outcome_cause='opponent conceded',score={'owner':1,'opponent':2},turn_count=21,went_first=True,damage_done_result_screen=150,qr_sightings=[0],source_time_file='SOURCE_TIME.json',capture_status='complete_with_recording_limits',deck_visible_core=['Regigigas','Alolan Grimer','Alolan Muk','Pawniard','Kingambit','Glimmet','Glimmora'],external_write_performed=False,lead_acceptance=False,independent_repairs=dict(prior_files='before_independent_repairs_20261012T233338Z',turn_13_selected_frame='f466_90',turn_3_boundary_energy='Visibly empty at107.2, later generated Darkness at107.5 during first selection',all_boundary_zones_audited=True))
summary['second_independent_repairs']=dict(prior_files='before_second_independent_repairs_20261012T235813Z',turn_3_later_next='Null at 107.5 s; small marker absent or obscured',turn_9_start_next='Null at 358 s; small marker absent or obscured',turn_19_attachment_proof=['f722_00','f732_00'],supported_hands_actions_outcome_unchanged=True)
save('SUMMARY.json',summary)
u=[('hidden_faces','Opponent normal draws and most searched/drawn faces hidden. No identities reconstructed.'),('discard_views','No opened discard view for either player in the complete source.'),('external_snapshot','Exact live-log list absent. Verified filmed QR list has separate provenance.'),('fan_overlap','Turns 7, 9, 11, 13 opponent fan edge overlap preserves 3 to 4 range.'),('turn14_no_target','No eligible target message at 488 to 491 s clearly observed. Trigger label uncertain; kept unknown.'),('retreat_cost','Turn 20 Drampa displayed Fire disappears; effective cost explanation not established by zoom.'),('timestamp_precision','Seek times are requested local positions, actual frame PTS not measured; draw ends approximate within inspected windows.'),('turn6_coin','Mesagoza use and no added Pokémon recorded, exact coin face uncertain.'),('boundary_energy_visibility','Zones use directly audited frame values. Early hand views may precede generation; empty slots are type null/count0/availablefalse. White glow or message-obscured current/preview values remain null. Preview availability is unknown; no game-rule default is used.')]
save('UNCERTAINTIES.json',dict(review_complete=True,unreviewed_intervals=[],uncertainties=[dict(id='U'+str(i),kind=k,finding=v) for i,(k,v) in enumerate(u,1)]))
print('Eight files written. Turns:',len(ledger['turns']),'native evidence frames:',len(ev['frames']))
