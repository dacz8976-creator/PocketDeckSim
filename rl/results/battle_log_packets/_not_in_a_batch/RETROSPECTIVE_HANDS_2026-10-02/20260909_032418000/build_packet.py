from pathlib import Path
import json, hashlib, re, copy
from PIL import Image
from datetime import datetime,timezone
P=Path(__file__).parent
W=P.parents[2]
OLD=Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\competitive-deck-study-2026-09-08\ongoing-campaign-2026-09-08\native-random-rotom')
V='20260909_032418000_iOS.MP4'; G='20260909_032418000'
SHA='750514530d208e76a8fbd8fc968aa6900ef08b0a0c84d5c00ce48c656f1f9672'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def hash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[dict(video_basename=V,sha256=SHA,source_json='SOURCE_REFERENCE.json')]
limits=['Opponent unplayed cards and normal/Research refill identities remain concealed by card backs.','Exact historical 20-card deck log snapshot is unavailable; visible cards are minimum observations, not a reconstructed deck.','All 345 reduced 1fps samples were screened once; this does not observe every instant, input or subsecond event.','Requested seek times and approximate midpoint locator labels are source-local. Actual decoded frame PTS and exact input times were not measured.','Opened owner discard panels are recorded at189.5 and255.0. No opened opponent pile was detected in the bounded screen; pile tops are not full pile contents.','T9 sole Lucky Ice Pop start is directly visible before play with reveal/inspection overlay; inspected close anchors do not show a clean unselected unzoomed interval.']
frames=[]; registry={}; oldbytime={}
for p in sorted((OLD/'frames').rglob('*.jpg')):
 m=re.search(r'_t([\d_]+)\.jpg$',p.name)
 if m:
  try:t=float(m.group(1).replace('_','.'))
  except:continue
  if t not in oldbytime or 'timeline' in str(p):oldbytime[t]=p
def fid(t,old=False):
 p=P/'nativeframes'/f't{t:07.2f}.jpg'
 return ('t' if not old and p.exists() else 'r')+f'{t:07.2f}'
def add(t,old=False,role='field evidence',turn=None,obs=None,selected=False,pre=None,unzoomed=None):
 id=fid(t,old)
 if id in registry:
  f=registry[id]
  if selected:f.update(selected_for_start_hand=True,before_first_play=pre,unzoomed=unzoomed,observation=obs)
  return id
 p=(P/'nativeframes'/f't{t:07.2f}.jpg') if id.startswith('t') else oldbytime[t]
 im=Image.open(p); assert im.size==(1170,2532),(p,im.size)
 dest=P/'hand_crops';dest.mkdir(exist_ok=True)
 cs={}
 for name,bounds in [('bottom',[0,2025,1170,2532]),('top',[0,0,1170,500])]:
  q=dest/(id+'_'+name+'.png');im.crop(bounds).save(q)
  cs[name+'_crop']=dict(path=str(q),pixel_bounds_x0_y0_x1_y1=bounds,sha256=hash(q),parent_sha256=hash(p),lossless=True)
 f=dict(evidence_id=id,role=role,turn_number=turn,who_played=None,source_video=V,source_sha256=SHA,requested_source_seconds=t,actual_frame_seconds_if_measured=None,timestamp_basis='requested seek; actual PTS unmeasured',full_frame_path=str(p),full_frame_sha256=hash(p),native_dimensions=dict(width=1170,height=2532),selected_for_start_hand=selected,before_first_play=pre,unzoomed=unzoomed,hand_spread=None,observation=obs,suitability_or_limit='Native identities/field evidence; the role and phase govern suitability, not a fixed grid.',reused_from_accepted_packet=id.startswith('r'),**cs)
 registry[id]=f;frames.append(f);return id
def refs(*ts):return [add(t) for t in ts]
def cue(t):
 # midpoint labels are approximate; native anchors prove names and typed fields.
 i=int(t)+1;id=f'cue_{i:05d}'
 if id not in registry:
  p=P/'cue_audit'/'sample_frames'/f'{i:05d}.jpg'
  f=dict(evidence_id=id,role='reduced timeline cue only',source_video=V,source_sha256=SHA,requested_source_seconds=i-.5,actual_frame_seconds_if_measured=None,full_frame_path=str(p),full_frame_sha256=hash(p),native_dimensions=dict(width=234,height=506),selected_for_start_hand=False,observation='Action/prompt/transition locator; not native identity proof.',suitability_or_limit='1fps midpoint approximate; exact input/order within a sampled interval unmeasured.')
  registry[id]=f;frames.append(f)
 return id
def evidence(ts,ct=None):return refs(*ts)+([] if ct is None else [cue(ct)])
GOO="Team Rocket's Goo-zooka";HAM='Hitting Hammer'; BALL='Poké Ball'; GOLD='Gholdengo'; ROT='Rotom ex'; TAP='Tapu Koko ex';RES="Professor's Research"
def hand(cards,ts,basis='direct native visible hand',status='observed',lim=None,count=None):return dict(cards_left_to_right=cards,count=len(cards) if cards is not None else count,basis=basis,evidence_ids=refs(*ts),status=status,limit_reason=lim)
startcards={1:[GOO,HAM,GOLD,BALL,HAM],3:[GOO,HAM,GOLD,HAM,'Red Card'],5:['Order Pad'],7:[GOO],9:['Lucky Ice Pop']}
st={1:38.5,3:79.5,5:166,7:234,9:284.4};end={1:48,3:133,5:205,7:240,9:305}
drawend={1:38.4,3:79.3,5:165.5,7:233.5,9:284.4}
first={1:40.5,2:54.5,3:80.5,4:141.5,5:168.5,6:220.5,7:236.5,8:247.5,9:284.75,10:322.5}
endcards={1:[GOO,HAM,GOLD,HAM],3:[],5:[],7:[],9:[]}
starts={t:hand(c,[st[t]],lim=limits[-1] if t==9 else None) for t,c in startcards.items()}
for t in startcards:add(st[t],role='owner postdraw start',turn=t,obs='Sole Lucky Ice Pop visible with fading reveal overlay, not yet played.' if t==9 else 'Owner complete hand before first play.',selected=True,pre=True,unzoomed=t!=9)
def play(order,kind,name,target,result,t,ts,hc=None,prompt=None,response=None,nested=None,energy=None,basis=None,lim=None):
 return dict(order=order,kind=kind,card_name=name,target=target,result=result,prompt_text=prompt,response=response,nested_events_in_order=nested,energy=energy,hand_count_after=hc,hand_count_basis='visible boundaries plus counted transitions; intermediate arithmetic inference',source_video=V,timestamp_seconds=t,timestamp_basis='approximate locator interval, separate from native seek times and unmeasured PTS',evidence_ids=evidence(ts,t),basis=basis or 'native identity/board anchors with reduced timeline transition cues',limit_reason=lim,inherited_action_fields_preserved=dict(old_numbered_action_present=False,accepted_provenance=None))
def attach(o,dest,t,ts,hc=None):return play(o,'manual Energy attachment',None,dest,'one Lightning attached',t,ts,hc,energy=dict(type='Lightning',count=1,destination=dest,retreat_payment_by_type=None))
def event(text,t,ts):return dict(event=text,timestamp_seconds=t,evidence_ids=evidence(ts,t),basis='native endpoints and locator cue; exact input unmeasured')
plays={
1:[play(1,'Item',BALL,'owner deck','Search finds Gimmighoul',40.5,[39,41,44],5),play(2,'bench','Gimmighoul','owner Bench position3','Gimmighoul60HP benched',45.5,[44,48],4),play(3,'end turn',None,None,'Owner ends without attachment or attack',48.5,[48],4)],
2:[play(1,'Tool','Poison Barb','opponent Active Tapu Koko ex','Tool attached',54.5,[55,69],5),play(2,'Item',BALL,'opponent deck','One searched Basic revealed as alternate-art Tapu Koko ex',58.5,[60,65,69],5),play(3,'bench',TAP,'opponent Bench position2','alternate-art Tapu Koko ex130 benched',66.5,[65,69],3),attach(4,'opponent Active Tapu Koko ex',68.5,[69],3),play(5,'attack','Plasma Hurricane','owner Active Rotom ex','20 damage; Rotom120→100; opponent Active Lightning1→2 by after-resolution',71.5,[70,75,79.5],3)],
3:[play(1,'evolution',GOLD,'owner Gimmighoul Bench3','Gholdengo100HP replaces Gimmighoul',80.5,[79.5,82],4),play(2,'Item','Red Card','opponent hand','Three cards shuffled; three card backs returned, no net fan count change',86.5,[85,90],3),play(3,'Item',HAM,'opponent Active Tapu Koko ex','Two Heads; one Lightning discarded,2→1',93.5,[95,100.5,102.5],2,nested=[event('Two Heads initial result',99.5,[100]),event('Luxury Coin prompt appears',100.5,[100.5]),event('Prompt resolves without reroll; decline inferred from unchanged successful result and no Ability animation',102.5,[102.5])],prompt='Use the effect of Luxury Coin?',response='No/decline inferred from resolution; exact click not captured'),play(4,'Item',HAM,'opponent Active Tapu Koko ex','Initial two Tails rerolled via Luxury Coin to one Head/one Tail; no Energy discarded',104.5,[104,110,111.5,114,120],1,nested=[event('Two Tails initial result',110.5,[110,111.5]),event('Luxury Coin used, followed by new coin flips',113.5,[114]),event('One Head and one Tail final result; no Energy change',119.5,[120])],prompt='Use the effect of Luxury Coin?',response='Yes/use supported by Ability animation and reroll'),attach(5,'owner Active Rotom ex',121.5,[125,133],1),play(6,'Item',GOO,'opponent Active Tapu Koko ex','Retreat Cost+1 effect; hand empty',130.5,[130,133],0),play(7,'end turn',None,None,'Owner ends without attack',133.5,[133],0)],
4:[attach(1,'opponent Bench2 alternate-art Tapu Koko ex',141.5,[140,142],4),play(2,'Supporter',RES,'opponent deck','Two hidden cards drawn',145.5,[145,150],5),play(3,'Tool','Poison Barb','opponent Bench2 alternate-art Tapu Koko ex','Tool attached',151.5,[155,160],4),play(4,'attack','Plasma Hurricane','owner Active Rotom ex','20 damage; Rotom100→80; opponent Active Lightning1→2',157.5,[155,160,166],4)],
5:[play(1,'Item','Order Pad','owner deck','Initial Tails; Luxury Coin reroll Tails; no Item found, hand empty',168.5,[166,168,171,172,173.5,176,180],0,prompt='Use the effect of Luxury Coin?',response='Yes/use supported by Ability animation and reroll',nested=[event('Initial Tails',172.5,[172,173.5]),event('Luxury Coin used',175.5,[176]),event('Reroll Tails, no search find',179.5,[180])]),attach(2,'owner Bench3 Gholdengo',190.5,[185,190,205],0),play(3,'retreat',ROT,'Gholdengo promoted from Bench3','Rotom pays one Lightning, becomes Bench3 with0; Gholdengo100L1 becomes Active',195.5,[190,205],0,energy=dict(type=None,count=None,destination=None,retreat_payment_by_type={'Lightning':1}),nested=[event('Retreat payment selected',197.5,[190,205]),event('Gholdengo selected and promoted',203.5,[205])]),play(4,'end turn',None,None,'Owner ends without attack',205.5,[205],0)],
6:[attach(1,'opponent Bench2 alternate-art Tapu Koko ex',220.5,[220,225],5),play(2,'attack','Plasma Hurricane','owner Active Gholdengo','20 damage; Gholdengo100→80; opponent Active Lightning2→3',225.5,[225,230,234],5)],
7:[play(1,'Item',GOO,'opponent Active Tapu Koko ex','Retreat Cost+1 effect; hand empty',236.5,[234,236,239,240],0),attach(2,'owner Bench3 Rotom ex',237.5,[239,240],0),play(3,'end turn',None,None,'Owner ends without attack',240.5,[240],0)],
8:[attach(1,'opponent Bench2 alternate-art Tapu Koko ex',247.5,[245,250,255],6),play(2,'attack','Mach Bolt','owner Active Gholdengo','Gholdengo80HP knocked out; Rotom80L1 promoted afterward',266.5,[260,270,275,280],6)],
9:[play(1,'Item','Lucky Ice Pop','owner Active Rotom ex','Heal80→100; Heads returns this card to hand',284.75,[284.4,284.7,284.75,287,290.4],1,nested=[event('20 heal',287.5,[287.4]),event('Heads then return to hand',291.5,[290,294])]),play(2,'Item','Lucky Ice Pop','owner Active Rotom ex','Same returned card replayed; heal100→120; Tails, card discarded',294.5,[294,296,300,302,305],0,nested=[event('20 heal',296.5,[296]),event('Tails and discard',300.5,[300,302])]),attach(3,'owner Active Rotom ex',302.5,[302,305],0),play(4,'attack','Junk Spark','opponent Active Tapu Koko ex','110 damage; Tapu130→20; Poison Barb poisons Rotom; boundary poison10 leaves Rotom110',306.5,[305,310,314,320],0)],
10:[play(1,'Supporter','Giovanni','opponent side','Attacks+10 effect displayed',322.5,[320,326],6),attach(2,'opponent Bench2 alternate-art Tapu Koko ex',326.5,[326,337.5],6),play(3,'attack','Mach Bolt','owner Active Rotom ex','100 damage leaves Rotom10; poison10 knocks it out; owner board empty',331.5,[330,334,336,337.5],6)]}
def draw(kind,name,t,ts,before,after,order=None,lim=None,count=1):
 return dict(kind=kind,caused_by=RES if kind=='Research' else BALL if kind=='search' else 'Red Card' if kind=='refill' else None,linked_play_order=order,cards_in_reveal_order=[dict(name=name,reveal_position=i+1,source_video=V,timestamp_seconds=t,evidence_ids=evidence(ts,t),basis='native reveal/hand identity' if name else 'concealed card back',limit_reason=lim) for i in range(count)],hand_count_before=before,hand_count_after=after,hand_count_basis='counted visible boundary plus transitions; intermediate counts may be arithmetic',returned_or_discarded_cards=None,source_video=V,timestamp_seconds=t,evidence_ids=evidence(ts,t),limit_reason=lim)
draws={1:[draw('normal',HAM,38,[38,38.5],4,5),draw('search','Gimmighoul',43.5,[44],4,5,1)],2:[draw('normal',None,51.5,[50,55],5,6,lim='hidden draw'),draw('search',TAP,64.5,[65],4,5,2)],3:[draw('normal','Red Card',79,[79.5],4,5),draw('refill',None,89.5,[90],3,3,2,'Opponent three hidden cards shuffled and replaced; no visible identity',3)],4:[draw('normal',None,137.5,[140,142],3,4,lim='hidden draw'),draw('Research',None,147.5,[145,150],3,5,2,'two concealed opponent draws',2)],5:[draw('normal','Order Pad',165.5,[166],0,1)],6:[draw('normal',None,212.5,[215,220],4,5,lim='hidden draw')],7:[draw('normal',GOO,233.5,[234],0,1)],8:[draw('normal',None,243.5,[245,250],5,6,lim='hidden draw')],9:[draw('normal','Lucky Ice Pop',284.4,[284.4,284.45,284.7],0,1)],10:[draw('normal',None,316.5,[320],6,7,lim='hidden draw')]}
def pokemon(name,hp,maxhp,l,pos=None,tool=None,effects=None,conditions=None,variant=None,ids=None):
 return dict(name=name,variant=variant,bench_position=pos,hp_now=hp,hp_max=maxhp,hp_max_basis='printed native card',damage=maxhp-hp,attached_energy=dict(total=l,by_type={'Lightning':l} if l else {}),tool=tool,special_conditions=conditions or [],active_effects=effects or [],evidence_ids=ids,status='observed',limit_reason=None)
def board(t,phase,state,ts,generated=False):
 # state RotomHP,L,GholdHP,L,ownerActive,TapuActiveHP,L,benchL,toolActive,toolBench,Goo,poison,oppPoints
 rh,rl,gh,gl,act,th,tl,bl,ta,tb,goo,poison,pts=state; ids=refs(*ts)
 rot=pokemon(ROT,rh,120,rl,conditions=['Poisoned'] if poison else [],ids=ids) if rh is not None else None
 gold=pokemon(GOLD,gh,100,gl,ids=ids) if gh is not None else None
 if act=='R':active=rot;benches=[{**gold,'bench_position':3}] if gold else []
 elif act=='G':active=gold;benches=[{**rot,'bench_position':3}] if rot else []
 else:active=None;benches=[]
 if gh==60 and t<=3 and act=='R':benches=[pokemon('Gimmighoul',60,60,0,3,ids=ids)]
 oppactive=pokemon(TAP,th,130,tl,tool='Poison Barb' if ta else None,effects=['Retreat Cost +1 from Team Rocket\'s Goo-zooka'] if goo else [],variant='regular art',ids=ids)
 oppbench=[pokemon(TAP,130,130,bl,2,tool='Poison Barb' if tb else None,variant='alternate art',ids=ids)] if bl is not None else []
 def zone(owner):
  ownturn=t%2==1 if owner else t%2==0
  available=bool(generated and ownturn and t!=1)
  return dict(this_turn=dict(type='Lightning' if available else None,count=1 if available else 0,available=available),next=dict(type='Lightning',count=1,available=False),basis='native large current icon versus small next icon at the specified phase',evidence_ids=ids,limit_reason=None,derived_after_turn_generation=dict(type='Lightning',count=1,available=True,basis='derived from next Lightning plus observed generation; separate from preceding-boundary current0') if phase=='preceding boundary before current-turn generation' else None)
 return dict(turn_number_displayed=t,phase=phase,stadium=None,stadium_basis='no Stadium visible in inspected board anchors',owner=dict(active=active,bench_in_position_order=benches,energy_zone=zone(True),points=0,board_effects=[],evidence_ids=ids,status='observed',limit_reason=None),opponent=dict(active=oppactive,bench_in_position_order=oppbench,energy_zone=zone(False),points=pts,board_effects=[],evidence_ids=ids,status='observed',limit_reason=None),shared_effects=[],evidence_ids=ids)
# End states from native field observations, not simulator reconstruction.
states={0:(120,0,None,0,'R',130,0,None,0,0,0,0,0),1:(120,0,60,0,'R',130,0,None,0,0,0,0,0),2:(100,0,60,0,'R',130,2,0,1,0,0,0,0),3:(100,1,100,0,'R',130,1,0,1,0,1,0,0),4:(80,1,100,0,'R',130,2,1,1,1,0,0,0),5:(80,0,100,1,'G',130,2,1,1,1,0,0,0),6:(80,0,80,1,'G',130,3,2,1,1,0,0,0),7:(80,1,80,1,'G',130,3,2,1,1,1,0,0),8:(80,1,None,0,'R',130,3,3,1,1,0,0,1),9:(110,2,None,0,'R',20,3,3,1,1,0,1,1),10:(None,0,None,0,None,20,3,4,1,1,0,0,1)}
bst={1:38.5,2:48,3:79.5,4:133,5:166,6:205,7:234,8:240,9:284.4,10:314};be={1:48,2:75,3:133,4:160,5:205,6:230,7:240,8:280,9:314,10:337.5}
fanstart={1:4,2:5,3:3,4:4,5:4,6:5,7:5,8:6,9:6,10:7};fanend={1:4,2:3,3:3,4:4,5:4,6:5,7:5,8:6,9:6,10:6}
draws[2][0]['hand_count_before']=4;draws[2][0]['hand_count_after']=5
draws[2][1]['hand_count_before']=3;draws[2][1]['hand_count_after']=4
plays[2][0]['hand_count_after']=4;plays[2][1]['hand_count_after']=4
plays[9][0]['nested_events_in_order'][1]=event('HEADS text directly visible; return to hand inferred from same-card replay',292,[292,294])
plays[9][0]['result']='Heal80→100; HEADS text directly visible at292; return to hand inferred from same-card replay'
plays[9][1]['timestamp_seconds']=None
plays[9][1]['source_interval_seconds']=[292,294.5]
plays[9][1]['timestamp_basis']='Replay committed after first Heads result and by native294; later locator card animation is not an exact input timestamp'
plays[9][1]['nested_events_in_order'][1]['basis']='Tails result supported by coin face, sampled result cue and following discard; exact input unmeasured'
rows=[]
for t in range(1,11):
 owner=t%2==1; prior=states[t-1]; start=list(prior)
 if owner and t in (3,5,7,9):pass
 actorhand=copy.deepcopy(starts[t]) if owner else hand(None,[50 if t==2 else 140 if t==4 else 215 if t==6 else 245 if t==8 else 320],basis='visible opponent fan after normal draw; concealed identities',status='hidden',lim='card backs conceal identities',count=fanstart[t])
 ownstart=copy.deepcopy(starts[t]) if owner else hand(endcards[t-1],[bst[t]],basis='native owner hand carried into opponent turn')
 ownend=hand(endcards[t if owner else t-1],[be[t]],basis='native end/boundary hand, empty arrays mean visible zero')
 row=dict(turn_number=t,who_played='owner' if owner else 'opponent',source_video=V,timing=dict(draw_animation_end_seconds=drawend.get(t),first_voluntary_move_seconds=first[t],before_end_action_seconds=end.get(t,266 if t==8 else 330 if t==10 else be[t]-5),end_after_resolution_seconds=be[t],timing_basis='approximate source-local intervals, no actual PTS/input timing measured'),hand_at_start=actorhand,owner_hand_start=ownstart,opponent_hand_at_owner_turn_start=dict(count=fanstart[t] if owner else fanend[t-1],supported_range=None,count_method='visible card backs, identity concealed',basis='native fan at owner start or preceding boundary',evidence_ids=refs(bst[t]),limit_reason=None),draws_and_searches=draws[t],plays_in_order=plays[t],automatic_events_in_order=[],board_at_start=board(t,'owner postdraw before first play' if owner else 'preceding boundary before current-turn generation',start,[bst[t]],generated=owner),board_after=board(t,'after recorded resolution; T10 pre-final-point-award' if t==10 else 'after recorded resolution',states[t],[be[t]]),owner_hand_end=ownend,discard_snapshot_ids=['pile_5_owner'] if t==5 else ['pile_8_owner'] if t==8 else [],turn_evidence_ids=[],limits=copy.deepcopy(limits))
 if t in (2,4,6):row['automatic_events_in_order'].append(event('Plasma Hurricane adds one Lightning to opponent Active, shown by native endpoint',be[t],[be[t]]))
 if t==4:row['automatic_events_in_order'].append(event('Goo-zooka first effect no longer shown at following owner start',166,[166]))
 if t==8:row['automatic_events_in_order']=[event('Gholdengo knockout and one-point display',273.5,[275]),event('Rotom selected/promoted',277.5,[280])]
 if t==9:row['automatic_events_in_order']=[event('Poison Barb poisons attacking Rotom',311.5,[310,314]),event('Poison10 after owner turn leaves Rotom110',313.5,[314,320])]
 if t==10:row['automatic_events_in_order']=[event('Mach Bolt100 leaves Rotom10',333.5,[334]),event('Poison10 knocks out Rotom, owner board empty',335.5,[336,337.5])]
 if t==10:row['intermediate_board_effects']=[dict(effect='Attacks +10 from Giovanni',applies_to='opponent Active and Bench',evidence_ids=refs(326),basis='visible +10 icons on both opponent Pokemon at326; later endpoint icons are absent')]
 row['opponent_hand_end']=dict(count=fanend[t],cards_left_to_right=None,basis='visible native fan, identities concealed',evidence_ids=refs(be[t]),limit_reason='Unplayed identities hidden by backs')
 rows.append(row)
def nested_ids(x):
 out=set()
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='evidence_ids' and isinstance(v,list):out.update(v)
   elif k!='turn_evidence_ids':out.update(nested_ids(v))
 elif isinstance(x,list):
  for v in x:out.update(nested_ids(v))
 return out
for r in rows:r['turn_evidence_ids']=sorted(nested_ids(r))
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,turns=rows,limits=limits,independent_acceptance_status='pending'))
handrows=[]
candidates={1:[(39,'Poké Ball inspected/selected; all five cards still present, not a clean untouched view'),(41,'Poké Ball already played, four cards'),(44,'Search result Gimmighoul added, five cards after search')],3:[(79.5,'Unzoomed five-card untouched postdraw hand'),(82,'Gholdengo evolution reveal; after play, four cards'),(85,'Red Card preview after evolution; four cards')],5:[(166,'Untouched sole Order Pad'),(168,'Order Pad selected/played'),(171,'Order Pad coin animation, hand empty')],7:[(234,'Sole Goo-zooka unzoomed before play'),(236,'Goo-zooka inspection overlay before it leaves hand'),(239,'Goo-zooka resolved and Rotom Energy attachment animation; hand empty')],9:[(285.4,'Lucky Ice Pop already played; card play animation'),(287.4,'Heal resolution; hand empty'),(290.4,'Coin animation; hand empty')]}
for t in startcards:
 cs=[]
 for tt,obs in candidates[t]:
  id=add(tt,role='draw-timed candidate',turn=t,obs=obs)
  f=registry[id];f.update(draw_animation_end_seconds=drawend[t],offset_after_draw_seconds=round(tt-drawend[t],2),observation=obs)
  cs.append(dict(evidence_id=id,requested_source_seconds=tt,offset_after_draw_seconds=round(tt-drawend[t],2),observation=obs))
 handrows.append(dict(turn_number=t,draw_animation_end_seconds=drawend[t],timing_basis='approximate inspected animation endpoint; actual PTS unmeasured',selected_start_evidence_ids=starts[t]['evidence_ids'],before_end_evidence_ids=refs(end[t]),start_hand=starts[t],before_end_hand=rows[t-1]['owner_hand_end'],candidates=cs,named_draws_and_searches=draws[t],capture_status='complete_with_recording_limits'))
save('HAND_SUPPLEMENT.json',dict(game_id=G,source=V,source_sha256=SHA,opening_hand=dict(cards_left_to_right=[GOO,ROT,HAM,GOLD,BALL],count=5,evidence_ids=refs(22,23),before_active_placement=True),owner_turns=handrows,limits=limits,independent_acceptance_status='pending'))
piles=[dict(snapshot_id='pile_5_owner',turn_number=5,pile_owner='owner',source_video=V,timestamp_seconds=189.5,cards_in_view=['Order Pad',HAM,'Red Card',GOO+' (gold variant)',HAM,BALL],discarded_energy_by_type={},scroll_coverage='one fully visible six-card panel; no scroll performed',full_pile_established=False,evidence_ids=refs(189.5),limit_reason='Visible panel contents only; full pile/order not claimed'),dict(snapshot_id='pile_8_owner',turn_number=8,pile_owner='owner',source_video=V,timestamp_seconds=255,cards_in_view=[GOO+' (regular variant)',GOO+' (gold variant)',HAM,BALL,'Order Pad',HAM,'Red Card'],discarded_energy_by_type={'Lightning':1},scroll_coverage='one fully visible seven-card panel; no scroll performed',full_pile_established=False,evidence_ids=refs(254.5,255),limit_reason='Visible panel contents only; full pile/order not claimed')]
for p in (P/'nativeframes').glob('*.jpg'):add(float(p.stem[1:]),obs=registry.get(p.stem,{}).get('observation','Retained decisive native capture inspected directly.'))
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,fixed_grid_is_turn_start_evidence=False),frames=frames,discard_snapshots=piles,scheduled_capture_limits=limits))
pg=read(W/'Review_Log/templates/pause_games/PAUSE_GAME.template.json');pg.update(is_template=False,game_id=G,review_date='2026-10-02',sources=sources,destination=None,deck_name='Rotom ex / Gholdengo',capture_status='complete_with_recording_limits',battle_review_status='old accepted outcome preserved; fresh field packet pending independent check',outcome=dict(owner_result='loss',score='0-3',basis='inherited accepted REVIEW.md, no new outcome audit',accepted_packet=str(OLD)),limits=limits,lead_checked=False)
pg['opening']=dict(source_video=V,timestamp_seconds=23,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=[dict(position=i+1,name=n,basis='direct native five-card setup before Active placement',evidence_ids=refs(22,23),limit_reason=None) for i,n in enumerate([GOO,ROT,HAM,GOLD,BALL])],selected_active=dict(name=ROT,opening_position=2,source_video=V,timestamp_seconds=24,evidence_ids=refs(23,24)),redraw_or_replacement=False,before_active_placement=True,status='observed',evidence_ids=refs(22,23),limit_reason=None)
pg['packet_files']=dict(prose='REVIEW_SUPPLEMENT.md',coverage='COVERAGE.md',deck='DECK_USED.json',turns='TURN_LEDGER.json',evidence='TURN_EVIDENCE.json');save('PAUSE_GAME.json',pg)
save('DECK_USED.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,deck_name_in_log=None,expected_card_count=20,cards_in_log_order=None,counts_by_name_and_variant=None,actual_card_count=None,exact_list_status='historical_list_unavailable',capture_status='complete_with_recording_limits',visible_core=[ROT,'Gimmighoul',GOLD,GOO,HAM,BALL,'Red Card','Order Pad','Lucky Ice Pop'],visible_minimum_copies={ROT:1,'Gimmighoul':1,GOLD:1,GOO:2,HAM:2,BALL:1,'Red Card':1,'Order Pad':1,'Lucky Ice Pop':1},limits=limits))
sr=read(P/'SOURCE_REFERENCE.json');sr['identity_basis']='One successful fresh exact-source SHA256 verification by primary Sol, matching frozen accepted source; one earlier cloud-timeout attempt retained separately. See SOURCE_VERIFICATION.json.';save('SOURCE_REFERENCE.json',sr)
save('MODE_CHECK.json',dict(source=V,source_sha256=SHA,visible_opponent='ゆうちゃん',opponent_name_evidence_ids=refs(35,38.5,326),old_placeholder='Opponent',old_files_changed=False,both_clocks_visible=True,auto_option_observed=False,auto_enabled=None,input_authorship=None,classification='ladder candidate under owner default, subject to independent check',owner_rule='Any visible Auto option, even OFF, is computer battle and excluded ladder.',screening='All345 reduced samples and retained native field anchors; no Auto control observed in these samples. This is not every-instant absence proof.'))
save('UNCERTAINTIES.json',dict(source=V,source_sha256=SHA,limits=limits,old_numbered_rows=0,new_recorded_turn_rows=10,owner_normal_draws={1:HAM,3:'Red Card',5:'Order Pad',7:GOO,9:'Lucky Ice Pop'},discards='No hidden full pile reconstruction; two owner panels recorded.',timestamp_conflicts='Old prose kept separately; new source intervals not presented as measured exact input PTS.'))
save('REVIEW_SUPPLEMENT.json',dict(source=V,source_sha256=SHA,capture_status='complete_with_recording_limits',opening=pg['opening'],hands=handrows,turns=rows,mode=read(P/'MODE_CHECK.json'),limits=limits,inherited_prose_verbatim=(OLD/'REVIEW.md').read_text(encoding='utf-8-sig'),old_packet_modified=False))
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,fixed_grid_is_turn_start_evidence=False),frames=frames,discard_snapshots=piles,scheduled_capture_limits=limits))
md=['# Rotom ex / Gholdengo source supplement', '', 'Source: '+V+'; SHA256 '+SHA+'. Fresh source fields are complete with the stated recording limits. Independent acceptance is pending. The accepted outcome remains loss0–3. The visible opponent is ゆうちゃん, replacing the old generic placeholder only in this separate supplement. No Auto option was observed in the bounded inspected controls.', '', 'Opening before placement at23.0: '+', '.join([GOO,ROT,HAM,GOLD,BALL])+'. Rotom ex from slot2 was selected as Active; owner goes first.', '', '| Turn | Player | Start hand | Draw/search | Numbered actions | Owner ending hand |', '|---|---|---|---|---|---|']
for r in rows:
 cs=r['hand_at_start']['cards_left_to_right']; h=', '.join(cs) if cs else 'hidden '+str(r['hand_at_start']['count']) if cs is None else 'empty'
 acts='; '.join(f"{p['order']}. {p['card_name'] or p['kind']}: {p['result']} [~{p['timestamp_seconds']}s]" for p in r['plays_in_order'])
 dr='; '.join(f"{d['kind']}: "+', '.join(c['name'] or 'hidden' for c in d['cards_in_reveal_order']) for d in r['draws_and_searches'])
 md.append(f"|{r['turn_number']}|{r['who_played']}|{h}|{dr}|{acts}|"+(', '.join(r['owner_hand_end']['cards_left_to_right']) or 'empty')+'|')
md+=['','The following fields are the resolved native endpoint states. L means attached Lightning. All inspected endpoints show no Stadium, current Energy Zone empty and next Lightning on both sides. Owner postdraw starts after turn1 show current Lightning1; opponent rows keep the observed preceding boundary separate from generated Lightning1.','','|Turn|Owner board after resolution|Opponent board after resolution|Opponent fan start → end|Native endpoint|','|---|---|---|---|---|']
def concise_side(side):
 def cp(p):
  if p is None:return 'empty'
  x=f"{p['name']} HP{p['hp_now']}/{p['hp_max']} L{p['attached_energy']['total']}"
  if p['tool']:x+=' Tool:'+p['tool']
  if p['special_conditions']:x+=' '+', '.join(p['special_conditions'])
  if p['active_effects']:x+=' '+', '.join(p['active_effects'])
  return x
 return 'Active '+cp(side['active'])+'; '+('; '.join('Bench'+str(p['bench_position'])+' '+cp(p) for p in side['bench_in_position_order']) or 'Bench empty')
for r in rows:
 t=r['turn_number'];md.append(f"|{t}|{concise_side(r['board_after']['owner'])}|{concise_side(r['board_after']['opponent'])}|{fanstart[t]} → {fanend[t]}|{be[t]}s|")
md+=['','Board fields include both sides, HP, typed Lightning counts, Tool attachments, Goo-zooka effects, Poison, Stadium absence at the inspected anchors, and current/next Zones. Opponent start rows retain preceding-boundary current0 separately from derived generation1. T10 final board is before the final point award and does not replace the accepted outcome record.','','The Luxury Coin No response after Hammer1 is inferred from successful resolution without reroll. Hammer2 and Order Pad use are supported by Ability animations and rerolls. Order Pad ends with no find. Red Card replaces three hidden cards with three hidden cards; the unchanged count does not mean no action. Lucky Ice Pop is the same card returned once, then replayed and discarded.','','Owner discard189.5: Order Pad, Hitting Hammer, Red Card, gold Goo-zooka, Hitting Hammer, Poké Ball; no discarded Energy. Owner discard255.0: regular Goo-zooka, gold Goo-zooka, Hitting Hammer, Poké Ball, Order Pad, Hitting Hammer, Red Card; Lightning1. These are panel layout order, not chronological pile order.','','Recording limits:']+['- '+x for x in limits]+['','Original accepted prose is preserved verbatim in REVIEW_SUPPLEMENT.json. Old packet, shared logs, index, history and source locations were not changed.']
(P/'REVIEW_SUPPLEMENT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
(P/'COVERAGE.md').write_text('All345 retained1fps reduced samples inspected once through39 contact sheets, plus decisive native identities/fields. Ten recorded turns, five owner normal draws, owner start/end hands, both boards/Zones, visible prompts/no-effect actions and two owner discard panels are serialized.\n\n'+ '\n'.join('- '+x for x in limits)+'\n',encoding='utf-8')
save('METRICS.json',dict(new_native_frames=39,new_native_cap=40,new_native_directly_inspected=39,retained_native_inspected_minimum=64,new_native_extraction_invocations=6,new_native_seek_decodes=39,successful_fresh_hash_reads=1,fresh_hash_attempts=2,reduced_locator_passes=1,reduced_locator_samples=345,reduced_locator_samples_inspected=345,locator_grids_inspected=39,turn_rows=10,owner_hand_rows=5,old_packet_writes=0,shared_log_index_writes=0,actual_frame_pts_measured=False,status='ready_for_different_producer_independent_check'))
ass=read(P/'ASSIGNMENT.json');ass['initial_original_reads_snapshot']=ass.pop('original_reads',0);ass.update(capture_status='complete_with_recording_limits',status='ready_for_independent_check',successful_source_hash_reads=1,hash_attempts=2,native_seek_decodes=39,reduced_locator_decode_passes=1);save('ASSIGNMENT.json',ass)
sv=read(P/'SOURCE_VERIFICATION.json');sv['original_decodes_basis']='Hash-stage historical count only; subsequent39 native seek decodes and one reduced locator pass recorded in METRICS.json';save('SOURCE_VERIFICATION.json',sv)
# Native image/crop bindings and complete nested evidence unions validated before freeze.
errors=[]
for r in rows:
 if nested_ids(r)-set(r['turn_evidence_ids']):errors.append('row refs '+str(r['turn_number']))
 if set(r['turn_evidence_ids'])-set(registry):errors.append('unresolved refs '+str(r['turn_number']))
for f in frames:
 if f['role']=='reduced timeline cue only':continue
 for c in ('bottom_crop','top_crop'):
  cp=f[c]; orig=Image.open(f['full_frame_path']); crop=Image.open(cp['path']);
  if orig.crop(cp['pixel_bounds_x0_y0_x1_y1']).tobytes()!=crop.tobytes():errors.append('crop '+f['evidence_id'])
save('PACKET_VALIDATION.json',dict(status='pass' if not errors else 'fail',errors=errors,turn_rows=10,owner_hand_rows=5,frames=len(frames),native_frames=sum(f['role']!='reduced timeline cue only' for f in frames),json_read_encoding='utf-8-sig',scope='structural/reference/hash/pixel binding; independent factual acceptance pending'))
assert not errors,errors
files=[]
for p in sorted(P.glob('*.json')):
 if p.name in {'SUBMISSION.json','WORKING_OBSERVATIONS.json','CHECKPOINT.json','STRUCTURE_CHECK.json'}:continue
 read(p);files.append(dict(path=str(p),sha256=hash(p),read_encoding='utf-8-sig'))
for p in (P/'REVIEW_SUPPLEMENT.md',P/'COVERAGE.md'):files.append(dict(path=str(p),sha256=hash(p),read_encoding='utf-8-sig'))
save('SUBMISSION.json',dict(source=V,source_sha256=SHA,capture_status='complete_with_recording_limits',independent_acceptance_status='pending',producer='Sol primary source packet',frozen_utc=datetime.now(timezone.utc).isoformat(),submitted_files=files,new_native_frames=39,old_packet_modified=False))
print(json.dumps(dict(errors=errors,rows=10,owner_hands=5,frames=len(frames),native=sum(f['role']!='reduced timeline cue only' for f in frames),new_native=39)))
