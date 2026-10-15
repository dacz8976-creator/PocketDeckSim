from pathlib import Path
import json, hashlib, copy
from datetime import datetime, timezone
from PIL import Image
P=Path(__file__).parent; W=P.parents[2]
OLD=Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\video-review-coordinator-2026-09-09\previously-finished-audit\battle-023151')
G='20260909_023151000'; V=G+'_iOS.MP4'; SHA='3df25a8532bd7df253638e23c3a6cfd711e4b7607992463ca5663e8abbff367a'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[dict(video_basename=V,sha256=SHA,source_json='SOURCE_REFERENCE.json')]
limits=['Hidden opponent normal/Research/Legendary Pulse draws and concealed search identities remain null; subsequent bench cards do not identify a concealed search result.', 'Exact historical 20-card deck snapshot unavailable; nearby QR is separate unbound evidence and no full deck is reconstructed.', 'All344 reduced1fps samples were inspected through18 grids once. This bounds sampled cues, not every instant, input or subsecond event.', 'Requested native seek times and inherited nominal native times are source-local. Actual frame PTS and exact input times unmeasured; inherited anchors have their retained tolerance.', 'No opened full discard panel detected in bounded timeline screening. Periodic visible tops and overlapping cards are recorded; hidden contents/order and discarded Energy totals not reconstructed.', 'No Auto control observed in sampled controls. This is not proof of every-instant absence; any visible Auto option, even OFF, means computer battle under owner rule.']
frames=[]; reg={}; manifest=read(OLD/'evidence/MANIFEST.json'); oldmap={Path(x['file']).stem:x for x in manifest['items']}
def add(key,role='native field evidence',turn=None,obs=None,selected=False,pre=None,unzoomed=None):
 new=isinstance(key,(int,float)); id=('t'+f'{key:07.2f}') if new else 'r_'+key
 if id in reg:
  if selected: reg[id].update(selected_for_start_hand=True,before_first_play=pre,unzoomed=unzoomed,observation=obs)
  return id
 if new: q=P/'nativeframes'/f'{id}.jpg'; ts=key; tol=None
 else:
  q=OLD/'evidence'/(key+'.jpg'); item=oldmap[key]; ts=item['nominal_time_seconds']; tol=item.get('time_tolerance_seconds'); assert digest(q)==item['sha256'],q
 im=Image.open(q); assert im.size==(1170,2532)
 d=P/'hand_crops';d.mkdir(exist_ok=True);cs={};h=digest(q)
 for name,b in [('bottom',[0,2025,1170,2532]),('top',[0,0,1170,500])]:
  c=d/(id+'_'+name+'.png');im.crop(b).save(c)
  cs[name+'_crop']=dict(path=str(c),pixel_bounds_x0_y0_x1_y1=b,sha256=digest(c),parent_sha256=h,lossless=True)
 f=dict(evidence_id=id,role=role,turn_number=turn,source_video=V,source_sha256=SHA,requested_source_seconds=ts,actual_frame_seconds_if_measured=None,timestamp_basis='requested native seek; actual PTS unmeasured' if new else 'inherited nominal anchor; retained approximately +/-1second tolerance, actual PTS unmeasured',time_tolerance_seconds=tol,full_frame_path=str(q),full_frame_sha256=h,native_dimensions=dict(width=1170,height=2532),reused_from_accepted_packet=not new,selected_for_start_hand=selected,before_first_play=pre,unzoomed=unzoomed,observation=obs,suitability_or_limit='Phase-qualified native identity and field evidence; draw-timed later views can already be after play.',**cs)
 frames.append(f);reg[id]=f;return id
def refs(*keys):return [add(k) for k in keys]
def cue(t):
 id=f'cue_{int(t):03d}'
 if id not in reg:
  q=P/'locator_scan/frames'/f'{int(t)+1:06d}.jpg'
  assert q.exists(),q
  f=dict(evidence_id=id,role='reduced timeline cue only',source_video=V,source_sha256=SHA,requested_source_seconds=t,actual_frame_seconds_if_measured=None,timestamp_basis='root nominal1fps sample label, actual PTS unmeasured',full_frame_path=str(q),full_frame_sha256=digest(q),native_dimensions=dict(width=234,height=506),observation='Transition/order/prompt locator only; native anchors prove identities.',suitability_or_limit='One sampled view each second cannot establish exact subsecond input.')
  reg[id]=f;frames.append(f)
 return id
def ev(keys,t=None):return refs(*keys)+([] if t is None else [cue(t)])
CAPE='Elegant Cape'; BALL='Poké Ball'; HEL='Heliolisk'; HEP='Helioptile'; ELE='Electrike'; MEGA='Mega Manectric ex'; PACK="Clemont's Backpack"; AREA='Training Area'; RES="Professor's Research"; ENT='Entei ex'; TOR='Torkoal'; TO='Torchic'; COM='Combusken'; BLA='Mega Blaziken ex'
startcards={1:[CAPE,BALL,HEL,PACK,MEGA],3:[CAPE,HEL,PACK,MEGA,ELE],5:[PACK,MEGA,AREA],7:[BALL],9:[HEP,RES]}
endcards={1:[CAPE,HEL,PACK,MEGA],2:[CAPE,HEL,PACK,MEGA],3:[PACK,MEGA],4:[PACK,MEGA],5:[],6:[],7:[HEP],8:[HEP],9:[HEP,RES]}
st={1:46.8,3:114.6,5:181.2,7:234.2,9:329.4};drawend={1:46.7,3:114.4,5:181.2,7:234.2,9:329.4}
before={1:59.5,3:128.5,5:197.5,7:241.5,9:332};be={1:59.5,2:111.2,3:128.5,4:'t5-owner-banner',5:'t5-first-spread-settled',6:230.5,7:'t8-entei-promoted',8:325.5,9:'terminal-settled-three-two'}
fanstart={1:4,2:5,3:4,4:5,5:4,6:5,7:4,8:5,9:4};fanend={1:4,2:4,3:4,4:4,5:4,6:4,7:4,8:4,9:4}
firstinterval={1:[47,48],2:[81,83],3:[115,116],4:[150,152],5:[181.5,182.5],6:[219,221],7:[234.5,236],8:[287,289],9:[330,331]}
def hand(cards,keys,basis='direct native complete lower hand',count=None,lim=None):
 return dict(cards_left_to_right=cards,count=len(cards) if cards is not None else count,basis=basis,evidence_ids=refs(*keys),status='observed' if cards is not None else 'hidden',limit_reason=lim)
starts={t:hand(c,[st[t]],lim='Unzoomed complete hand with automatic draw reveal remnant above hand; before Energy generation.' if t==3 else None) for t,c in startcards.items()}
for t in st:add(st[t],role='owner postdraw start before first voluntary play',turn=t,obs='Complete unzoomed lower hand; T3 automatic draw remnant separately qualified.',selected=True,pre=True,unzoomed=True)
def mon(name,hp,mx,n=0,typ=None,pos=None,tool=None,effects=None,variant=None):
 return dict(name=name,variant=variant,bench_position=pos,hp_now=hp,hp_max=mx,hp_max_basis='visible printed HP plus visible Cape bonus if Mega; Basic Cape does not increase HP',damage=mx-hp,attached_energy=dict(total=n,by_type={} if not n else {typ:n}),tool=tool,special_conditions=[],active_effects=effects or [],status='observed_at_native_anchors',limit_reason='Sampled board evidence only; hidden transient effects not reconstructed',evidence_ids=[])
def e(hp=60,n=0,pos=None,tool=None):return mon(ELE,hp,60,n,'Lightning',pos,tool,variant='Quick Attack; two distinct copies')
def hel(hp=80,n=0,pos=None):return mon(HEL,hp,80,n,'Lightning',pos)
def meg(n=1,pos=1):return mon(MEGA,210,210,n,'Lightning',pos,CAPE)
def torch(hp=60,n=0,pos=None):return mon(TO,hp,60,n,'Fire',pos)
def ent(hp=140,n=0,pos=1):return mon(ENT,hp,140,n,'Fire',pos)
def tork(hp=100):return mon(TOR,hp,100,0,'Fire',2)
def comb(hp=80):return mon(COM,hp,80,2,'Fire')
# State tuple: owner Active, owner Bench, opponent Active, opponent Bench, owner points, opponent points.
states={0:[e(),[],torch(),[],0,0],1:[e(),[mon(HEP,60,60,0,'Lightning',3,variant='Jumping Kick')],torch(),[],0,0],2:[e(40),[mon(HEP,60,60,0,'Lightning',3,variant='Jumping Kick')],torch(60,1),[ent(),tork()],0,0],3:[e(40),[e(60,1,1,CAPE),hel(80,0,3)],torch(60,1),[ent(),tork()],0,0],4:[hel(),[e(60,1,1,CAPE)],comb(),[ent(),tork()],0,1],5:[hel(80,1),[meg()],comb(10),[ent(110),tork(70)],0,1],6:[hel(20,1),[meg()],comb(10),[ent(110,1),tork(70),torch(60,0,3)],0,1],7:[hel(20,1),[meg(2)],ent(100,1,None),[tork(60),torch(50,0,3)],1,1],8:[meg(2,None),[],ent(100,2,None),[tork(60),mon(BLA,200,210,0,'Fire',3)],1,2],9:[meg(2,None),[],None,[tork(60),mon(BLA,200,210,0,'Fire',3)],3,2]}
def zone(typ,count,keys,basis):return dict(this_turn=dict(type=typ if count else None,count=count,available=bool(count)),next=dict(type=typ,count=1,available=False),basis=basis,evidence_ids=refs(*keys),limit_reason='Next count1 from one visible next icon; not future random stream')
def board(t,phase,state,key,current_owner=0,current_opp=0,stadium=None,lim=None):
 a,b,c,d,op,pp=copy.deepcopy(state);ids=refs(key)
 if stadium:
  for m in [a,c]:
   if m and m['name'] in (HEL,COM,MEGA):m['active_effects'].append('Training Area: Stage1 Active attacks +10')
 for m in [a,c]+b+d:
  if m:m['evidence_ids']=ids
 def side(active,bench,typ,count,points):return dict(active=active,bench_in_position_order=bench,energy_zone=zone(typ,count,[key],'native visible current/next icons at named phase'),points=points,board_effects=[],evidence_ids=ids,status='observed_with_phase_qualifications',limit_reason=lim)
 return dict(turn_number_displayed=t,phase=phase,stadium=stadium,owner=side(a,b,'Lightning',current_owner,op),opponent=side(c,d,'Fire',current_opp,pp),shared_effects=[] if stadium is None else ['Training Area remains in play; printed Stage1 Active attack bonus +10'],evidence_ids=ids,limit_reason=lim)
def play(order,kind,name,target,result,interval,keys,hc=None,energy=None,prompt=None,response=None,lim=None,nested=None):
 return dict(order=order,kind=kind,card_name=name,target=target,energy=energy,result=result,prompt_text=prompt,response=response,nested_events_in_order=nested or [],hand_count_after=hc,hand_count_basis='visible native boundaries; intermediate costs/additions arithmetic inference when separately noted',source_video=V,timestamp_seconds=None,source_interval_seconds=interval,timestamp_basis='bounded approximate locator interval; exact input and actual PTS unmeasured',evidence_ids=ev(keys,interval[0]),basis='native identities/endpoints with sampled transition order',limit_reason=lim,inherited_action_fields_preserved=dict(old_prose_assertion_preserved_in='REVIEW_SUPPLEMENT.json',old_packet_changed=False))
def energy(typ,target):return dict(type=typ,count=1,destination=target,retreat_payment_by_type=None)
plays={
1:[play(1,'Item',BALL,'owner deck','Find Helioptile; count5→4 on cost then5 after find',[47,51],[47.7,49.7,51.5],5),play(2,'bench',HEP,'Bench3','Helioptile60HP0Lightning benched',[53,54],[52.7,59.5],4),play(3,'end_turn',None,None,'No Energy attached on first turn; end at unchanged board',[59,60],[59.5],4)],
2:[play(1,'Supporter',RES,'opponent hand','Two hidden draws; normal-draw fan5→4 cost→6 after draw',[81,85],['t2-research-in-discard'],6),play(2,'Item',BALL,'opponent deck','Concealed search; result identity unknown',[91,97],[95,'t2-pokeball-entei-result'],6,lim='Six after find inferred from cost5 and subsequent five after bench; no separate public find/name observed.'),play(3,'bench',ENT,'Bench1','Entei ex140HP0Fire publicly benched; not proof of search identity',[98,100],['t2-pokeball-entei-result',111.2],5),play(4,'bench',TOR,'Bench2','Torkoal100HP0Fire benched',[103,104],['t2-torkoal-benched'],4),play(5,'manual_energy',None,'opponent Active Torchic','Fire0→1',[104,106],[111.2],4,energy('Fire','opponent Active Torchic')),play(6,'attack','Peck','owner Active Electrike','20 damage; Electrike60→40',[108,111.2],[110,111.2],4)],
3:[play(1,'bench',ELE,'Bench1','Second healthy Electrike60HP0Lightning',[115,117],[114.6,117,128.5],4),play(2,'evolve',HEL,'Bench3 Helioptile','Heliolisk80HP0Lightning',[119,120],[120,128.5],3),play(3,'manual_energy',None,'owner Bench1 Electrike','Lightning0→1',[122,124],[128.5],3,energy('Lightning','owner Bench1 Electrike')),play(4,'Tool',CAPE,'owner Bench1 Electrike','Tool attached; Basic remains60HP',[125,127],[128.5],2),play(5,'end_turn',None,None,'No attack; handBackpack/Mega retained',[128.5,130],[128.5],2)],
4:[play(1,'evolve',COM,'opponent Active Torchic','Combusken80HP with inheritedFire1',[150,152],['t4-combusken-two-fire'],4),play(2,'manual_energy',None,'opponent Active Combusken','Fire1→2',[154,157],['t4-combusken-two-fire'],4,energy('Fire','opponent Active Combusken')),play(3,'attack','High Jump Kick','owner Active original Electrike','50 damage;40→0 knockout, opponent point1',[167,173],['t5-owner-banner'],4)],
5:[play(1,'Stadium',AREA,'shared Stadium slot','Training Area in play',[181.5,184],[181.2,182,184],2),play(2,'evolve',MEGA,'owner Bench1 Electrike','Mega printed180+Cape30=210HP; inheritsLightning1',[187,189],[187,'t5-heliolisk-one-mega-one-energy'],1),play(3,'Item',PACK,'owner Pokemon attacks this turn','Heliolisk attacks +20 to all opponent Pokemon this turn',[191,193],['t5-heliolisk-one-mega-one-energy','t5-first-spread-settled'],0),play(4,'manual_energy',None,'owner Active Heliolisk','Lightning0→1',[194,195],['t5-heliolisk-one-mega-one-energy'],0,energy('Lightning','owner Active Heliolisk')),play(5,'attack','Electrispark','opponent Active and Bench','Displayed70 Active: Combusken80→10; Bench30 each: Entei140→110,Torkoal100→70',[198,203],[197.5,'t5-first-spread-settled'],0)],
6:[play(1,'bench',TO,'opponent Bench3','Second Torchic60HP0Fire',[219,221],['t6-entei-one-fire-settled',230.5],4),play(2,'manual_energy',None,'opponent Bench1 Entei ex','Fire0→1',[221,223],['t6-entei-one-fire-settled'],4,energy('Fire','opponent Bench1 Entei ex')),play(3,'attack','High Jump Kick','owner Active Heliolisk','60 with Training Area; Heliolisk80→20',[228,230.5],['t6-heliolisk-twenty',230.5],4)],
7:[play(1,'Item',BALL,'owner deck','Find Jumping Kick Helioptile; remains in hand',[234.5,238],[235,237,'t7-helioptile-search-result',240],1),play(2,'manual_energy',None,'owner Bench1 Mega Manectric ex','Lightning1→2',[239,241],[240,'t7-mega-two-lightning'],1,energy('Lightning','owner Bench1 Mega Manectric ex')),play(3,'attack','Electrispark','opponent Active and Bench','Displayed50 knocks Combusken10→0; Bench10 Entei110→100,Torkoal70→60,Torchic60→50',[241,250],[241.5,'t8-entei-promoted'],1)],
8:[play(1,'Item','Rare Candy','opponent Bench3 damaged Torchic','Rare Candy precedes direct Stage2 evolution',[287,289],['t8-rare-candy-play'],4),play(2,'evolve',BLA,'opponent Bench3 Torchic','Mega Blaziken ex200/210 from inherited10damage; Fire0',[296,299],['t8-mega-blaziken-printed-210','t8-mega-blaziken-200-remaining'],3),play(3,'manual_energy',None,'opponent Active Entei ex','Fire1→2',[303,305],['t8-entei-two-fire'],3,energy('Fire','opponent Active Entei ex')),play(4,'attack','Blazing Beatdown','owner Active Heliolisk','60 knocks20→0; opponent point2',[310,317],['t8-legendary-pulse',325.5],3)],
9:[play(1,'attack','Lightning Accelerator','opponent Active Entei ex','120 using existingLightning2; Entei100→0 and owner settled3–2',[330,342],[330,331.5,332,335,'t9-unused-action-warning','terminal-settled-three-two'],2,prompt='End your turn? Energy can be attached; A Supporter card can be used',response='OK acceptance inferred from following attack; unused Energy/Supporter declined',lim='Warning text direct; exact button input not captured. Research is normal draw retained, not a Supporter play.',nested=[dict(event='Unused Energy/Supporter warning',source_interval_seconds=[332,333],evidence_ids=refs(332,'t9-unused-action-warning')),dict(event='Attack proceeds without attachment or Research play',source_interval_seconds=[333,335],evidence_ids=refs(335,'terminal-settled-three-two'))])]
}
def draw(kind,by,names,t,keys,beforec,afterc,linked=None,hidden=False,lim=None):
 return dict(kind=kind,caused_by=by,linked_play_order=linked,cards_in_reveal_order=[dict(name=n,reveal_position=i+1,source_video=V,timestamp_seconds=t,evidence_ids=ev(keys,t),basis='hidden card back' if n is None else 'direct native owner reveal/hand identity',limit_reason='concealed identity' if n is None else None) for i,n in enumerate(names)],hand_count_before=beforec,hand_count_after=afterc,returned_or_discarded_cards=None,source_video=V,timestamp_seconds=t,timestamp_basis='approximate source animation interval; PTS unmeasured',evidence_ids=ev(keys,t),limit_reason=lim or ('Hidden opponent draw identities' if hidden else None))
norm={1:MEGA,3:ELE,5:AREA,7:BALL,9:RES};draws={t:[] for t in range(1,10)}
for t in st:draws[t]=[draw('normal','turn start',[norm[t]],drawend[t],[st[t]],len(startcards[t])-1,len(startcards[t]))]
for t,tm in [(2,62),(4,131),(6,205),(8,274)]:draws[t]=[draw('normal','turn start',[None],tm,[be[t-1]],fanend[t-1],fanstart[t],hidden=True)]
draws[1].append(draw('search',BALL,[HEP],50,[51.5,52.7],4,5,1))
draws[2].append(draw('Supporter draw',RES,[None,None],84,['t2-research-in-discard'],4,6,1,True))
draws[2].append(draw('search',BALL,[None],96,[95,'t2-pokeball-entei-result'],5,6,2,True,'Search result concealed. Added-card count6 inferred; native99fivebacks follows Entei bench. Later Entei is not proof of find.'))
draws[7].append(draw('search',BALL,[HEP],238,['t7-helioptile-search-result',240],0,1,1))
draws[8].append(draw('Ability draw','Legendary Pulse',[None],324,['t8-legendary-pulse',325.5],3,4,hidden=True))
rows=[];piles=[]
for t in range(1,10):
 owner=t%2==1;bs=st[t] if owner else be[t-1]
 os=copy.deepcopy(starts[t]) if owner else hand(endcards[t-1],[bs],'direct native owner carried hand at preceding boundary')
 hs=copy.deepcopy(os) if owner else hand(None,[bs],'Post-normal-draw fan count from sampled fan transitions; native preceding and later counts corroborate',fanstart[t],'Card backs conceal identities; boundary native is preceding normal draw')
 beforegen=t in (1,3,5)
 cur=0 if not owner or beforegen else 1
 bstart=board(t,'owner complete postdraw hand before generation/first play' if owner and beforegen else 'owner postdraw/generated Energy before first play' if owner else 'preceding resolved boundary before opponent normal draw and generation',states[t-1],bs,cur,0,AREA if t>=6 else None)
 if t==5:bstart['stadium']=None;bstart['shared_effects']=[]
 if owner and t>1 and beforegen:bstart['owner']['energy_zone']['derived_after_generation']=dict(type='Lightning',count=1,basis='subsequent generation/attachment sequence; distinct from preceding observed empty current',evidence_ids=ev([bs],int(drawend[t])+1))
 if not owner:bstart['opponent']['energy_zone']['derived_after_generation']=dict(type='Fire',count=1,basis='following turn generation and Fire attachment; distinct from preceding boundary empty current',evidence_ids=ev([bs],{2:63,4:132,6:206,8:275}[t]))
 aft=board(t,'resolved endpoint, including required promotion/automatic draw; same board shown at following boundary if banner overlays',states[t],be[t],1 if t==9 else 0,0,AREA if t>=5 else None, 'Entei remaining100 carried from spread/native endpoints; promoted large card temporarily hides numeric overlay.' if t==7 else None)
 if t==5:aft['shared_effects'].append('Clemont Backpack attack bonus applied during attack; expires at turn boundary, not retained for T7')
 auto=[]
 if t==4:auto=[dict(event='Original Electrike KO; opponent point1; owner promotes Heliolisk',source_interval_seconds=[169,178],evidence_ids=refs(177.5,'t5-owner-banner'))]
 if t==7:auto=[dict(event='CombuskenKO; ownerpoint1; after long choice opponent promotesEntei',source_interval_seconds=[246,272],evidence_ids=ev(['t8-entei-promoted'],250))]
 if t==8:auto=[dict(event='HelioliskKO; opponentpoint2; owner promotesMega',source_interval_seconds=[313,322],evidence_ids=refs('t8-legendary-pulse',325.5)),dict(event='Entei Legendary Pulse hidden draw, fan3→4',source_interval_seconds=[323,325.5],evidence_ids=refs('t8-legendary-pulse',325.5))]
 if t==9:auto=[dict(event='EnteiKO two-point award; settledowner3/opponent2 thenwhiteending',source_interval_seconds=[336,343],evidence_ids=refs('terminal-settled-three-two'))]
 ownend=hand(endcards[t],[be[t]],lim='T9 postattack two-card hand corroborated by335 and terminal342' if t==9 else None)
 row=dict(turn_number=t,who_played='owner' if owner else 'opponent',source_video=V,timing=dict(draw_animation_end_seconds=drawend.get(t),first_voluntary_move_seconds=None,first_voluntary_move_interval_seconds=firstinterval[t],before_end_action_seconds=before.get(t),end_after_resolution_seconds=reg[add(be[t])]['requested_source_seconds'],timing_basis='Source-local approximate animation/nominal anchor times; not exact input/PTS'),hand_at_start=hs,owner_hand_start=os,opponent_hand_at_owner_turn_start=dict(count=fanstart[t] if owner else fanend[t-1],supported_range=None,count_method='Visible card backs at owner start or preceding boundary',basis='native top fan; opponent normal-draw fan is separately tracked',evidence_ids=refs(bs),limit_reason='identities concealed'),draws_and_searches=draws[t],plays_in_order=plays[t],automatic_events_in_order=auto,board_at_start=bstart,board_after=aft,owner_hand_end=ownend,opponent_hand_end=dict(count=fanend[t],cards_left_to_right=None,basis='visible native fan after resolution',evidence_ids=refs(be[t]),limit_reason='identities concealed'),discard_snapshot_ids=[],turn_evidence_ids=[],limits=limits)
 # Visible tops only. No claim of opened/full pile, hidden count, energy or chronology.
 tops={1:(['Poké Ball'],[]),2:(['Poké Ball'],['Poké Ball',RES]),3:(['Poké Ball'],['Poké Ball']),4:([ELE],['Poké Ball']),5:([PACK],['Poké Ball']),6:([PACK],['Poké Ball']),7:([BALL],[COM,TO]),8:([HEL],['Rare Candy',COM,TO]),9:([HEL],[ENT,'Rare Candy'])}[t]
 for side,names in zip(['owner','opponent'],tops):
  if not names:continue
  pid=f'pile_{t}_{side}';piles.append(dict(snapshot_id=pid,turn_number=t,pile_owner=side,source_video=V,timestamp_seconds=reg[add(be[t])]['requested_source_seconds'],cards_in_view=names,discarded_energy_by_type=None,scroll_coverage='closed pile visible top/overlap only',full_pile_established=False,evidence_ids=refs(be[t]),limit_reason='Visible top/overlap names only; hidden contents, total count, chronological order and Energy totals unknown'))
  row['discard_snapshot_ids'].append(pid)
 rows.append(row)
 if t==5:row['intermediate_board_effects']=[dict(effect="Clemont's Backpack: attacks by Heliolisk this turn deal20 more to opponent Active and Bench",applies_to='owner Heliolisk',source_interval_seconds=[193,203],evidence_ids=refs('t5-heliolisk-one-mega-one-energy',197.5,'t5-first-spread-settled'),basis='printed Item and visible boosted attack/spread; end-of-turn expiry distinguished from ongoing Stadium')]
def nested_ids(x):
 out=set()
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='evidence_ids' and isinstance(v,list):out.update(v)
   elif k!='turn_evidence_ids':out.update(nested_ids(v))
 elif isinstance(x,list):
  for v in x:out.update(nested_ids(v))
 return out
for r in rows:r['turn_evidence_ids']=sorted(nested_ids(r)|set(eid for p in piles if p['snapshot_id'] in r['discard_snapshot_ids'] for eid in p['evidence_ids']))
candidates={1:[(47.7,'Poké Ball already lifted/played; remainingfour'),(49.7,'Ball search pending; lowerhandfour'),(52.7,'Find Helioptile joinedhandfive; after first play')],3:[(115,'Five cardsstillpresent, Energygeneration beforebench'),(117,'Electrike alreadybenched; four'),(120,'Heliolisk evolutionafterplay; three')],5:[(182,'TrainingArea alreadyleft hand; two'),(184,'Stadium broadcastafterplay; two'),(187,'Mega selected/played; one')],7:[(235,'Ball leavinghand; firstplay'),(237,'Search pending; handempty'),(240,'Helioptile addedone; EnergyattachmentafterBall')],9:[(330,'Two cardhandduringattackselection'),(332,'Warningoverlay; bothcardsremain'),(335,'Attackdamage; bothcardsremain')]}
handrows=[]
for t in st:
 cs=[]
 for tm,obs in candidates[t]:
  eid=add(tm,'draw-timed candidate',t,obs);reg[eid].update(draw_animation_end_seconds=drawend[t],offset_after_draw_seconds=round(tm-drawend[t],2))
  cs.append(dict(evidence_id=eid,requested_source_seconds=tm,offset_after_draw_seconds=round(tm-drawend[t],2),observation=obs))
 handrows.append(dict(turn_number=t,draw_animation_end_seconds=drawend[t],timing_basis='Approximate inspected card-join endpoint, actual PTSunmeasured',selected_start_evidence_ids=starts[t]['evidence_ids'],start_hand=starts[t],before_end_evidence_ids=refs(before[t]),before_end_hand=hand(endcards[t],[before[t]]),candidates=cs,named_draws_and_searches=draws[t],capture_status='complete_with_recording_limits'))
for q in sorted((P/'nativeframes').glob('*.jpg')):add(float(q.stem[1:]),obs='Decisive native/crop inspected directly; unused alternatives retained with phase-dependent suitability.')
opening=dict(source_video=V,timestamp_seconds=23.5,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=[dict(position=i+1,name=n,basis='native five-card setup before placement',evidence_ids=refs(23.5),limit_reason=None) for i,n in enumerate([CAPE,BALL,HEL,ELE,PACK])],selected_active=dict(name=ELE,opening_position=4,source_video=V,timestamp_seconds=None,source_interval_seconds=[24,30],evidence_ids=refs(23.5,46.8)),redraw_or_replacement=False,before_active_placement=True,status='observed',evidence_ids=refs(23.5),limit_reason=None)
save('SOURCE_REFERENCE.json',dict(source=V,source_sha256=SHA,source_bytes=642076032,current_path=str(W/'Reviewed'/V),frozen_accepted_source_json=str(OLD/'SOURCE.json'),frozen_source_json_sha256=digest(OLD/'SOURCE.json'),current_verification_receipt='ROOT_SOURCE_VERIFICATION.json',identity_basis='Root successful attempt3 hash matches frozen source. Primary reuses receipt and root locator, no duplicate hash/locator decode.',old_packet=str(OLD),old_review_sha256=digest(OLD/'REVIEW.md'),timestamp_basis='New requested seeks/old nominal anchors; actualPTS unmeasured'))
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,setup=opening,turns=rows,limits=limits,independent_acceptance_status='pending'))
save('HAND_SUPPLEMENT.json',dict(game_id=G,source=V,source_sha256=SHA,opening_hand=dict(cards_left_to_right=[CAPE,BALL,HEL,ELE,PACK],count=5,before_active_placement=True,evidence_ids=refs(23.5)),owner_turns=handrows,limits=limits,independent_acceptance_status='pending'))
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,fixed_grid_is_turn_start_evidence=False),frames=frames,discard_snapshots=piles,scheduled_capture_limits=limits))
pg=read(W/'Review_Log/templates/pause_games/PAUSE_GAME.template.json');pg.update(is_template=False,game_id=G,review_date='2026-10-02',sources=sources,destination=None,deck_name='Mega Manectric ex / Heliolisk',capture_status='complete_with_recording_limits',battle_review_status='Accepted outcome preserved; fresh field packet pending different-producer check',outcome=dict(owner_result='win',score='3-2',basis='inherited accepted REVIEW.md; no broad new outcome audit',accepted_packet=str(OLD)),opening=opening,limits=limits,lead_checked=False,packet_files=dict(prose='REVIEW_SUPPLEMENT.md',coverage='COVERAGE.md',deck='DECK_USED.json',turns='TURN_LEDGER.json',evidence='TURN_EVIDENCE.json'));save('PAUSE_GAME.json',pg)
save('DECK_USED.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=sources,deck_name_in_log=None,expected_card_count=20,cards_in_log_order=None,counts_by_name_and_variant=None,actual_card_count=None,exact_list_status='historical_list_unavailable',capture_status='complete_with_recording_limits',visible_core=[ELE,HEP,HEL,MEGA,CAPE,PACK,AREA,BALL,RES],visible_minimum_copies={ELE:2,HEP:2,HEL:1,MEGA:1,CAPE:1,PACK:1,AREA:1,BALL:1,RES:1},copy_count_limit='Two Electrike simultaneously in play proves2; second Helioptile in hand while first evolved line remains in play proves2. Other listed counts are conservative minimum observations, not exact deckcounts.',nearby_QR_binding='separate unbound owner-supplied evidence; not used for exact historicaldeck',limits=limits))
mode=dict(source=V,source_sha256=SHA,visible_opponent='Alai',opponent_name_evidence_ids=refs(59.5,325.5),both_clocks_visible=True,auto_option_observed=False,auto_enabled=None,input_authorship=None,classification='ladder candidate under owner default, pending independent acceptance',owner_rule='Any visible Auto option, even OFF, is computer battle and excluded ladder.',screening='All344 reducedsamples plus decisive retained/newnative controls inspected; noAutoobserved inthese samples, not every-instant absenceproof.');save('MODE_CHECK.json',mode)
conflict=dict(turn_number=2,field='PokéBall searchresult identity/publicreveal',accepted_quote='then plays Poké Ball and publicly finds Entei ex.',accepted_quote_path=str(OLD/'REVIEW.md'),source_native_result_name=None,evidence_ids=refs(95,'t2-pokeball-entei-result'),fresh_finding='Native95concealedfan and native99publicEntei bench animation do not show distinct publicsearchreveal. Searchidentityremainsunknown.',old_packet_changed=False)
save('UNCERTAINTIES.json',dict(source=V,source_sha256=SHA,limits=limits,provenance_conflicts=[conflict],inherited_turn_parser_limit='INHERITED_TURNS empty despite nine prose turns; new ledger covers actual9recordedturns.',timestamp_conflicts='Inherited nominal anchors retained separately; sourceintervals do not silently convert oldtimes into exactmeasuredPTS.'))
save('REVIEW_SUPPLEMENT.json',dict(source=V,source_sha256=SHA,capture_status='complete_with_recording_limits',opening=opening,hands=handrows,turns=rows,mode=mode,provenance_conflicts=[conflict],limits=limits,inherited_prose_verbatim=(OLD/'REVIEW.md').read_text(encoding='utf-8-sig'),old_packet_modified=False))
md=['# Mega Manectric ex / Heliolisk source supplement','','Source: '+V+'; SHA256 '+SHA+'. Nine recorded turns and five owner postdraw hands are complete with stated recording limits. Different-producer independent acceptance is pending. Acceptedwin3–2vsAlai remains unchanged.','','Opening before placement: Elegant Cape, Poké Ball, Heliolisk, Electrike, Clemont\'s Backpack. Slot4 Electrike is selected as Active; owner goes first. Setup-time Ball inspection is separate from Turn1 play.','','|Turn|Player|Start hand after draw|Draw/search|Numbered plays|Owner ending hand|','|---|---|---|---|---|---|']
for r in rows:
 hs=r['hand_at_start'];h=', '.join(hs['cards_left_to_right']) if hs['cards_left_to_right'] is not None else f"hidden fan{hs['count']}"
 dr='; '.join(d['kind']+': '+', '.join(c['name'] or 'hidden' for c in d['cards_in_reveal_order']) for d in r['draws_and_searches'])
 acts='; '.join(f"{a['order']}. {a['card_name'] or a['kind']}: {a['result']} [~{a['source_interval_seconds'][0]}–{a['source_interval_seconds'][1]}s]" for a in r['plays_in_order'])
 md.append(f"|{r['turn_number']}|{r['who_played']}|{h}|{dr}|{acts}|"+(', '.join(r['owner_hand_end']['cards_left_to_right']) or 'empty')+'|')
def side(s):
 def m(p):
  if p is None:return 'empty'
  en=p['attached_energy'];typ='L' if 'Lightning' in en['by_type'] else 'F' if 'Fire' in en['by_type'] else 'Energy'
  return f"{p['name']} HP{p['hp_now']}/{p['hp_max']} {typ}{en['total']}"+(' Tool:'+p['tool'] if p['tool'] else '')
 return 'Active '+m(s['active'])+'; '+('; '.join('Bench'+str(x['bench_position'])+' '+m(x) for x in s['bench_in_position_order']) or 'Bench empty')
md+=['','|Turn|Owner board after resolution|Opponent board after resolution|Fan start→end|Stadium / Zones at endpoint|Native endpoint|','|---|---|---|---|---|---|']
for r in rows:
 t=r['turn_number'];b=r['board_after'];md.append(f"|{t}|{side(b['owner'])}|{side(b['opponent'])}|{fanstart[t]}→{fanend[t]}|"+(AREA if t>=5 else 'none')+('; ownercurrentL1, opponentcurrent0' if t==9 else '; bothcurrent0')+'; nextownerL/opponentF|'+str(be[t])+'|')
md+=['','All inspected board anchors show no Special Conditions; only owner Elegant Cape is attached. Training Area appears in Turn5 and remains. Clemont\'s Backpack is an Item, adds20 to Heliolisk damage against all opponent Pokemon that turn, and is absent from Turn7 damage. Printed Stage1 attack plus10 is reflected in recorded attacks. This is sampled field coverage, not an all-instant rules audit.','','Draw-join ends and start candidates: '+ '; '.join(f'T{t} end~{drawend[t]}, untouchedstart{st[t]}' for t in st)+'. T3 lowerhand is unzoomed with automatic reveal remnant above it. Draw offsets are retained with phase labels; rapid first plays mean several +1/+3/+6 views are already after play.','','Turn9 warning directly says Energy can be attached and a Supporter can be used. Professor\'s Research remains in the two-card hand and current Lightning1 is left unused. OK acceptance is inferred from the following attack; exact input is not captured. Helioptile remains unplayed on Turns7–9; no invented separate decline button/action.','','The prior Turn2 assertion “then plays Poké Ball and publicly finds Entei ex.” is retained verbatim in the JSON accepted prose. Native95 shows concealed search; retained native99 shows Entei subsequently being benched with five backs. No distinct public search reveal is shown, so fresh search identity is null and count6 after search is inference. Later bench Entei is not proof of search identity.','','Periodic discard records show only closed pile tops/overlapping visible cards: Ball, originalElectrike, Backpack/Heliolisk on owner side; Research/Ball, Combusken/Torchic, Rare Candy and finalEntei on opponent side. Full pile contents and discardedEnergy totals are unknown.','','Recording limits:']+['- '+x for x in limits]+['','Original accepted prose is preserved separately; old packets, source locations, shared logs/index/history/artifact/simulator were not changed.']
(P/'REVIEW_SUPPLEMENT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
(P/'COVERAGE.md').write_text('All344 retained reduced1fps samples screened once through18 contact grids. Forty newnative frames and decisive retained1170×2532 anchors inspected directly; lossless top/hand crops preserve pixel dimensions. Nine turnrows, five ownerhands, all visible normaldraws/searches, numbered plays, bothboards/Zones/fans, warningresponse and periodic closedpile views serialized.\n\n'+'\n'.join('- '+x for x in limits)+'\n',encoding='utf-8')
save('CUE_AUDIT.json',dict(source=V,source_sha256=SHA,root_preprocessing_receipt='LOCATOR_PREPROCESSING.json',samples=344,samples_inspected=344,grids_inspected=18,all_samples_screened_once=True,auto_option_observed=False,opened_discard_panels_detected=False,source_interval_seconds=[0,343],basis='Direct visual inspection of all18retained grids; reducedcues locate transitions and nativecaptures establishidentity',limits=limits))
save('METRICS.json',dict(new_native_frames=40,new_native_cap=60,new_native_directly_inspected=40,new_native_extraction_invocations=4,new_native_seek_decodes=40,primary_source_hash_reads=0,primary_locator_decode_passes=0,root_hash_receipt_reused=True,root_total_hash_attempts=3,root_successful_hash_reads=1,root_locator_decode_passes=1,reduced_locator_samples=344,reduced_locator_samples_inspected=344,locator_grids_inspected=18,retained_native_inspected_minimum=20,turn_rows=9,owner_hand_rows=5,old_packet_writes=0,shared_log_index_writes=0,actual_frame_pts_measured=False,status='ready_for_different_producer_independent_check'))
met=read(P/'METRICS.json');native=[f for f in frames if f['role']!='reduced timeline cue only'];met.update(retained_native_registered=sum(f['reused_from_accepted_packet'] for f in native),native_registered=len(native),lossless_registered_crops=len(native)*2,new_native_bytes=sum(q.stat().st_size for q in (P/'nativeframes').glob('*.jpg')),registered_crop_bytes=sum(Path(f[k]['path']).stat().st_size for f in native for k in ('bottom_crop','top_crop')),wall_time_seconds=None,wall_time_limit='Not measured across resumed primary work; root hash walltime is separately recorded in receipt.',token_usage=None,dollar_usage=None,usage_limit='Exact token/dollar allowance unavailable.');save('METRICS.json',met)
ass=read(P/'ASSIGNMENT.json');ass.update(status='ready_for_independent_check',capture_status='complete_with_recording_limits',new_native_frames=40,new_native_cap=60,native_seek_decodes=40,primary_hash_reads=0,root_hash_receipt_reused=True,primary_locator_decode_passes=0);save('ASSIGNMENT.json',ass)
errors=[]
for r in rows:
 if nested_ids(r)-set(r['turn_evidence_ids']):errors.append('missing nested rowrefs '+str(r['turn_number']))
 if set(r['turn_evidence_ids'])-set(reg):errors.append('unresolved rowrefs '+str(r['turn_number']))
 for pid in r['discard_snapshot_ids']:
  if not any(x['snapshot_id']==pid for x in piles):errors.append('unresolved pile '+pid)
for f in frames:
 if digest(Path(f['full_frame_path']))!=f['full_frame_sha256']:errors.append('frame hash '+f['evidence_id'])
 if f['role']=='reduced timeline cue only':continue
 for k in ['bottom_crop','top_crop']:
  c=f[k];im=Image.open(f['full_frame_path']);ci=Image.open(c['path'])
  if im.crop(c['pixel_bounds_x0_y0_x1_y1']).tobytes()!=ci.tobytes():errors.append('crop pixels '+f['evidence_id'])
save('PACKET_VALIDATION.json',dict(status='pass' if not errors else 'fail',errors=errors,turn_rows=9,owner_hand_rows=5,frames=len(frames),native_frames=sum(x['role']!='reduced timeline cue only' for x in frames),json_read_encoding='utf-8-sig',scope='Structure/evidence unions/imageSHA/losslesscrop binding, independent factual acceptance pending'))
assert not errors,errors
files=[]
for q in sorted(P.glob('*.json')):
 if q.name in {'SUBMISSION.json','WORKING_OBSERVATIONS.json','CHECKPOINT.json','STRUCTURE_CHECK.json'}:continue
 read(q);files.append(dict(path=str(q),sha256=digest(q),read_encoding='utf-8-sig'))
for q in [P/'REVIEW_SUPPLEMENT.md',P/'COVERAGE.md']:q.read_text(encoding='utf-8-sig');files.append(dict(path=str(q),sha256=digest(q),read_encoding='utf-8-sig'))
save('SUBMISSION.json',dict(source=V,source_sha256=SHA,capture_status='complete_with_recording_limits',independent_acceptance_status='pending',producer='Sol primary source packet',frozen_utc=datetime.now(timezone.utc).isoformat(),submitted_files=files,new_native_frames=40,old_packet_modified=False))
print(json.dumps(dict(errors=errors,rows=9,owner_hands=5,frames=len(frames),new_native=40)))
