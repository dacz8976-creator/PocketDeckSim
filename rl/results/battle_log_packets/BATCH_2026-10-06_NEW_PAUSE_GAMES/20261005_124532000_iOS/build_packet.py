"""Author this source-bound packet from the worker's inspected observations."""
from pathlib import Path
from PIL import Image
import json, hashlib, copy
from datetime import datetime, timezone
P=Path(__file__).parent
S=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
V=S['video_basename']; SHA=S['sha256']; G='20261005_124532000_iOS'; NOW=datetime.now(timezone.utc).isoformat()
SRC=[dict(video_basename=V,sha256=SHA,source_json='SOURCE.json')]
def save(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frames={}; crops=P/'turn_evidence'; crops.mkdir(exist_ok=True)
def eid(t): return 'f'+f'{t:07.2f}'.replace('.','p')
def frame(t,role='action_or_board',turn=None,**kw):
    key=eid(t)
    if key in frames:
        if role not in frames[key]['roles']: frames[key]['roles'].append(role)
        frames[key].update(kw);return key
    f=None
    for folder in ['final_gap','final_capture','fractions','detail','native']:
        candidate=P/folder/f't{t:07.2f}.jpg'
        if candidate.exists(): f=candidate;break
    if t==1: f=P/'qr_intake/t0001.00.png'
    assert f and f.is_file(),(t,f)
    with Image.open(f) as im:
        assert im.size==(1170,2532)
        bottom=(0,2025,1170,2532); top=(0,0,1170,700)
        im.crop(bottom).save(crops/(key+'_hand.jpg'),quality=95)
        im.crop(top).save(crops/(key+'_top.jpg'),quality=95)
    frames[key]=dict(evidence_id=key,role=role,roles=[role],turn_number=turn,
        source_video=V,source_sha256=SHA,requested_source_seconds=t,actual_frame_seconds_if_measured=None,
        timestamp_basis='Requested source-local fast seek; exact decoded PTS not measured',
        full_frame_path=str(f.relative_to(P)).replace('\\','/'),native_dimensions={'width':1170,'height':2532},
        bottom_crop={'path':'turn_evidence/'+key+'_hand.jpg','pixel_bounds_x0_y0_x1_y1':list(bottom)},
        top_crop={'path':'turn_evidence/'+key+'_top.jpg','pixel_bounds_x0_y0_x1_y1':list(top)},
        selected_for_start_hand=False,before_first_play=None,unzoomed=None,hand_spread=None,
        observation='Retained source-bound frame inspected in ordered contact sheets or native view.',suitability_or_limit='Action/board evidence; no default hand suitability claim.')
    frames[key].update(kw)
    return key
def refs(*times): return [frame(t) for t in times]
def cards(names,t,basis='Observed source hand in left-to-right order'):
    return [dict(position=i+1,name=n,variant=None,basis=basis,evidence_ids=refs(t),limit_reason=None) for i,n in enumerate(names)]
def hand(names,t,basis=None):
    return dict(cards_left_to_right=cards(names,t,basis or 'Observed fan; nearby draw/reveal frames support named continuity'),count=len(names),basis=basis or 'Counted visible fan',evidence_ids=refs(t),status='observed',limit_reason=None)
def hiddenhand(count,t):
    return dict(cards_left_to_right=[dict(position=i+1,name=None,variant=None,basis='Exposed card back',evidence_ids=refs(t),limit_reason='Opponent card identity concealed') for i in range(count)],count=count,basis='Counted exposed card backs',evidence_ids=refs(t),status='observed_hidden_identities',limit_reason='Opponent hand is not exposed')
def mon(name,hp,maxhp,energy=0,etype='Darkness',tool='none',cond=None,effects=None,pos=None,t=53.2,variant=None):
    return dict(name=name,variant=variant,bench_position=pos,hp_now=hp,hp_max=maxhp,hp_max_basis='Visible card/HP display; no maximum HP modifier shown',damage=maxhp-hp,
        attached_energy=dict(total=energy,by_type={etype:energy} if energy else {}),tool=tool,
        tool_basis='Visible attached icon or observed absence',special_conditions=cond or [],active_effects=effects or [],evidence_ids=refs(t),status='observed',limit_reason=None)
def empty(pos,t): return dict(bench_position=pos,name='none',status='visibly_empty',basis='Empty positional Bench rectangle',evidence_ids=refs(t))
def zone(etype,current,t):
    return dict(this_turn=dict(type=etype if current else 'none',count=1 if current else 0,available=bool(current),status='observed_present' if current else 'observed_absent'),
        next=dict(type=etype,count=1,available=False,status='visible_next_preview'),basis='Large current circle and small next preview read independently at the selected frame',evidence_ids=refs(t),limit_reason=None)
def board(t,owner_active,owner_bench,opp_active,opp_bench,op=0,pp=0,stadium='Rainbow Cave',oc=False,pc=False,phase='turn boundary',display=None):
    return dict(turn_number_displayed=display,turn_number_displayed_limit_reason=None if display else 'No readable Current turn label in this selected frame; ledger turn comes from retained transition label',phase=phase,
        timestamp_seconds=t,stadium=stadium,stadium_basis='Visible Stadium or observed empty Stadium slot',
        owner=dict(active=owner_active,bench_in_position_order=owner_bench,energy_zone=zone('Darkness',oc,t),points=op,board_effects=[],evidence_ids=refs(t),status='observed',limit_reason=None),
        opponent=dict(active=opp_active,bench_in_position_order=opp_bench,energy_zone=zone('Fire',pc,t),points=pp,board_effects=[],evidence_ids=refs(t),status='observed',limit_reason=None),shared_effects=[],evidence_ids=refs(t))
def nido(t,pos=None,en=0,tool='none'): return mon('Nidoran male',60,60,en,tool=tool,pos=pos,t=t,variant='Peck 20 / HP60 semantic entity1690')
def dark(t,pos=None,en=0,tool='none'): return mon('Darkrai ex',140,140,en,tool=tool,pos=pos,t=t,variant='Nightmare Aura / Dark Prism80 semantic entity3910')
def entei(t,hp=140,pos=None,en=0,poison=False): return mon('Entei ex',hp,140,en,'Fire',cond=['Poisoned'] if poison else [],pos=pos,t=t,variant='Legendary Pulse / Blazing Beatdown60+')
def charm(t,pos=3,en=0,evolved=False): return mon('Charmeleon' if evolved else 'Charmander',80 if evolved else 70,80 if evolved else 70,en,'Fire',pos=pos,t=t,variant='Ignition / Slash40' if evolved else 'Flame Tail30 / HP70')
def bench_empty(t): return [empty(i,t) for i in range(1,4)]
def oppbench(t,stage=0,energy=0,second_entei=False):
    return [entei(t,pos=1) if second_entei else empty(1,t),charm(t,pos=2) if stage>=1 else empty(2,t),charm(t,pos=3,en=energy,evolved=stage>=1)]
def draw(kind,names,times,play=None,before=None,after=None,cause=None,hidden=False):
    cs=[]
    for i,(name,t) in enumerate(zip(names,times)):
        cs.append(dict(name=name,reveal_position=i+1,source_video=V,timestamp_seconds=t,evidence_ids=refs(t),basis='Visible reveal' if name else 'Hidden opponent addition',limit_reason='Concealed opponent card identity' if name is None else None))
    return dict(kind=kind,caused_by=cause,linked_play_order=play,cards_in_reveal_order=cs,hand_count_before=before,hand_count_after=after,returned_or_discarded_cards=[],source_video=V,timestamp_seconds=times[0],evidence_ids=refs(*times),limit_reason='Opponent card fronts not exposed' if hidden else None)
def play(kind,name,target,t,result,ev=None,energy=None,nested=None,hand_after=None,reveal=None,prompt=None,response=None):
    return dict(order=None,kind=kind,card_name=name,target=target,energy=energy or dict(type='none',count=0,destination='none',retreat_payment_by_type={}),result=result,prompt_text=prompt,response=response,
        nested_events_in_order=nested or [],hand_count_after=hand_after,source_video=V,timestamp_seconds=t,
        input_or_selection_timestamp_seconds=t,card_reveal_timestamp_seconds=reveal,
        timing_limit='Visual input/selection localized by source frames; touch telemetry unavailable. Opponent timestamps locate revealed resolution, not hidden touch.',
        evidence_ids=refs(*(ev or [t])),basis='Observed source action and consequences',limit_reason=None)
def auto(name,t,result,ev=None): return dict(name=name,timestamp_seconds=t,result=result,evidence_ids=refs(*(ev or [t])),basis='Observed automatic effect')
T=[]
def row(num,who,start,end,hs,plays,draws,bs,ba,he=None,fan=None,autos=None,first=None,drawend=None,beforeend=None,transition=None):
    for i,x in enumerate(plays):x['order']=i+1
    r=dict(turn_number=num,who_played=who,source_video=V,source_sha256=SHA,
        timing=dict(turn_start_seconds=start,turn_end_seconds=end,draw_animation_end_seconds=drawend,first_voluntary_move_seconds=first,before_end_action_seconds=beforeend,end_after_resolution_seconds=ba['timestamp_seconds']),
        hand_at_start=hs,owner_hand_start=copy.deepcopy(hs) if who=='owner' else dict(status='not_applicable',count=None,cards_left_to_right=None,basis='Opponent turn',evidence_ids=[],limit_reason='Owner hand naming is captured on owner turns'),
        opponent_hand_at_owner_turn_start=dict(count=fan,supported_range=None,count_method='Count distinct exposed card backs in retained native top crop',basis='Observed card backs' if fan is not None else 'Not an owner turn',evidence_ids=hs['evidence_ids'] if fan is not None else [],limit_reason=None if fan is not None else 'Not applicable to opponent turn'),
        draws_and_searches=draws,plays_in_order=plays,automatic_events_in_order=autos or [],board_at_start=bs,board_after=ba,
        owner_hand_end=he or dict(status='not_applicable',count=None,cards_left_to_right=None,basis='Opponent turn',evidence_ids=[],limit_reason='Owner ending hand captured only for owner turns'),
        discard_snapshot_ids=[],turn_evidence_ids=list(dict.fromkeys(hs['evidence_ids']+bs['evidence_ids']+ba['evidence_ids']+(refs(transition) if transition else []))),
        limits=['Opponent private inputs and hidden identities unavailable; action ordering uses public resolutions.'] if who=='opponent' else [])
    if transition:r['turn_label_evidence_ids']=refs(transition)
    T.append(r);return r
luck='Lucky Ice Pop'; king='Nidoking'; cy='Cyrus'; wall='Wally'; research="Professor's Research"
# Turn1: full intact hand at53.2, first normal draw at52.0.
t=53.2
bs=board(t,nido(t),[nido(t,pos=1),empty(2,t),empty(3,t)],entei(t),oppbench(t),stadium='none')
t=62
ba=board(t,nido(t,tool='Poison Barb'),[nido(t,pos=1),empty(2,t),empty(3,t)],entei(t),oppbench(t),stadium='none',phase='After End Turn input; next turn transition follows')
r=row(1,'owner',50,63,hand(['Poison Barb',luck,king,cy],53.2),[
    play('card_play','Poison Barb','owner Active Nidoran male',53.6,'Tool attaches; no HP change',ev=[53.6,54,55,58],hand_after=3,reveal=54,nested=[dict(order=1,event='Tool target selection',target='Active Nidoran male',timestamp_seconds=55,evidence_ids=refs(55))]),
    play('end_turn',None,None,62,'End Turn accepted; no warning dialog observed',ev=[61,62,63],hand_after=3)
], [draw('normal_draw',[cy],[52],before=3,after=4)],bs,ba,hand([luck,king,cy],61),3,first=53.6,drawend=53.0,beforeend=61,transition=50)
# Turn2 opponent.
t=65;bs=board(t,nido(t,tool='Poison Barb'),[nido(t,pos=1),empty(2,t),empty(3,t)],entei(t),oppbench(t),stadium='none',pc=True)
t=87;ba=board(t,nido(t,tool='Poison Barb'),[nido(t,pos=1),empty(2,t),empty(3,t)],entei(t,en=1),oppbench(t),phase='After opponent end effects; transition displays turn3',display=3)
row(2,'opponent',63,87,hiddenhand(4,65),[
    play('card_play','Rainbow Cave','shared Stadium',70,'Stadium installed',ev=[67,70,72],reveal=70),
    play('stadium_activation','Rainbow Cave','opponent Energy Zone',76,'Current Fire discarded; next Fire produced. Same-type replacement still recorded.',ev=[75,76,77,78],nested=[dict(order=1,event='discard current Fire',timestamp_seconds=76,evidence_ids=refs(76)),dict(order=2,event='next Fire generated',timestamp_seconds=78,evidence_ids=refs(78))]),
    play('energy_attachment',None,'opponent Active Entei ex',79,'One Fire attached; Entei total1',ev=[79,81],energy=dict(type='Fire',count=1,destination='Active Entei ex',retreat_payment_by_type={})),
    play('end_turn',None,None,83,'Turn ends without attack',ev=[83,84])
], [draw('normal_draw',[None],[65],before=3,after=4,hidden=True),draw('ability_draw',[None],[85],cause='Legendary Pulse',before=3,after=4,hidden=True)],bs,ba,autos=[auto('Legendary Pulse',84,'Active Entei draws1 hidden card',[84,85])],first=70,transition=63)
# Turn3 owner.
t=89.2;bs=board(t,nido(t,tool='Poison Barb'),[nido(t,pos=1),empty(2,t),empty(3,t)],entei(t,en=1),oppbench(t))
t=115;ba=board(t,nido(t,tool='Poison Barb'),[nido(t,pos=1,en=1),dark(t,pos=2),empty(3,t)],entei(t,en=1),oppbench(t),phase='After owner end input; transition explicitly shows turn4',display=4)
row(3,'owner',87,115,hand([luck,king,cy,research],89.2),[
    play('card_play',research,None,89.6,'Draw Wally, then Poke Ball',ev=[89.4,89.6,90,91,93,94],hand_after=5,reveal=91),
    play('card_play','Poke Ball',None,96,'Find Darkrai ex',ev=[95,96,97,99],hand_after=5,reveal=97),
    play('bench_pokemon','Darkrai ex','owner Bench2',103,'Darkrai ex benched at140HP',ev=[101,102,103,104,106],hand_after=4,reveal=105),
    play('energy_attachment',None,'owner Bench1 Nidoran male',109,'One Darkness attached; Bench Nidoran total1',ev=[108,109,110,112],energy=dict(type='Darkness',count=1,destination='Bench1 Nidoran male',retreat_payment_by_type={}),hand_after=4),
    play('end_turn',None,None,114,'End Turn accepted; no additional prompt observed',ev=[114,115],hand_after=4)
], [draw('normal_draw',[research],[88],before=3,after=4),draw('supporter_draw',[wall,'Poke Ball'],[93,94],play=1,before=3,after=5,cause=research),draw('search',['Darkrai ex'],[99],play=2,before=4,after=5,cause='Poke Ball')],bs,ba,hand([luck,king,cy,wall],114),4,
    autos=[auto('Energy generation',89.6,'One Darkness generated after the selected89.2 empty-current frame',[89.2,89.6,91])],first=89.6,drawend=89.2,beforeend=114,transition=87)
# Turn4 opponent, including all public sequences and first KO.
t=118;bs=board(t,nido(t,tool='Poison Barb'),[nido(t,pos=1,en=1),dark(t,pos=2),empty(3,t)],entei(t,en=1),oppbench(t),pc=True)
t=184;ba=board(t,nido(t,en=1),[empty(1,t),dark(t,pos=2),empty(3,t)],entei(t,hp=130,en=2,poison=True),oppbench(t,stage=1,energy=1),pp=1,phase='After KO, replacement, Legendary Pulse and Poison checkup; before turn5')
row(4,'opponent',115,185,hiddenhand(5,118),[
    play('stadium_activation','Rainbow Cave','opponent Energy Zone',123,'Current Fire discarded and next Fire produced',ev=[121,123,124,125]),
    play('card_play','May',None,131,'Add two hidden Pokemon, then choose two hidden Pokemon to shuffle from hand into deck; net hand 5 to 4 including the played Supporter',ev=[130,131,131.5,132.5,133,134,135,140,140.5],reveal=131.5,nested=[dict(order=1,event='Two random Pokemon added from deck',identities='hidden',timestamp_seconds=134,evidence_ids=refs(133,134)),dict(order=2,event='Two Pokemon selected for shuffle back',identities='hidden',timestamp_seconds=140,evidence_ids=refs(135,140,140.5),limit='Opponent private choice prompt is not visible; both identities unknown')]),
    play('evolution','Charmeleon','opponent Bench3 Charmander',143,'Evolves to80HP Ignition/Slash40 Charmeleon',ev=[142,143,144]),
    play('ability','Ignition','opponent Active Entei ex',146,'Fire from Energy Zone attaches to Active Entei; Entei1 to2. Next Fire generated afterward.',ev=[145,146,147,148],energy=dict(type='Fire',count=1,destination='Active Entei ex',retreat_payment_by_type={})),
    play('card_play',"Team Rocket's Thieving Machine",'owner discard Poke Ball',150,'Recovers owner-discarded Poke Ball into opponent hand',ev=[150,151,153],reveal=150),
    play('card_play','Poke Ball',None,155,'Search adds1 hidden Basic Pokemon',ev=[154,155,156,157],reveal=155),
    play('bench_pokemon','Charmander','opponent Bench2',162,'Second Charmander benched70HP',ev=[161,162,163],reveal=162),
    play('energy_attachment',None,'opponent Bench3 Charmeleon',164,'One Fire attached to Charmeleon; total1, current Zone empty',ev=[163,164,165,166],energy=dict(type='Fire',count=1,destination='Bench3 Charmeleon',retreat_payment_by_type={})),
    play('attack','Blazing Beatdown','owner Active Nidoran male',167,'60 damage knocks out60HP Nidoran; attack ends turn',ev=[167,168,169,170],reveal=167)
], [draw('normal_draw',[None],[118],before=4,after=5,hidden=True),draw('supporter_pokemon_draw',[None,None],[133,134],play=2,cause='May',before=4,after=6,hidden=True),draw('recovery',['Poke Ball'],[151],play=5,cause="Team Rocket's Thieving Machine"),draw('search',[None],[157],play=6,cause='Poke Ball',hidden=True),draw('ability_draw',[None],[182],cause='Legendary Pulse',before=2,after=3,hidden=True)],bs,ba,
    autos=[auto('Poison Barb',171,'Entei becomes Poisoned after attack; resolves before removal',[170,171,172,173]),auto('KO/removal/point',175,'Nidoran and Poison Barb removed; opponent gains first point',[174,177,178]),auto('Owner replacement choice',179,'Owner promotes Bench1 Nidoran with1 Darkness, no retreat payment',[178,179,180]),auto('Legendary Pulse',181,'Entei draws1 hidden card',[181,182]),auto('Poison checkup',183,'Entei140 to130 after10 Poison damage',[183,184])],first=123,transition=115)
# Turn5 owner.
t=187.95;bs=board(t,nido(t,en=1),[empty(1,t),dark(t,pos=2),empty(3,t)],entei(t,hp=130,en=2,poison=True),oppbench(t,stage=1,energy=1),pp=1,oc=True)
t=221;ba=board(t,nido(t,en=1),[empty(1,t),dark(t,pos=2,en=1,tool='Deceptive Needle'),empty(3,t)],entei(t,hp=80,en=2,poison=True),oppbench(t,stage=1,energy=1),pp=1,phase='After attack and10 Poison checkup; before turn6')
row(5,'owner',185,222,hand([luck,king,cy,wall,research],187.95,'Five intact slots; leftmost Lucky Ice Pop near edge supported by186/187 continuity, not deck inference'),[
    play('card_play',research,None,188,'Draw second Nidoking, then Deceptive Needle',ev=[187.95,188,188.1,189,191,192],hand_after=6,reveal=189),
    play('card_play','Deceptive Needle','owner Bench2 Darkrai ex',202,'Tool attached to benched Darkrai; no immediate damage',ev=[201,202,203,204,205,207],hand_after=5,reveal=204,nested=[dict(order=1,event='Choose Pokemon Tool target',prompt='Please choose a Pokemon to attach the Pokemon Tool to',response='Darkrai ex Bench2',timestamp_seconds=202,evidence_ids=refs(202,204,205))]),
    play('energy_attachment',None,'owner Bench2 Darkrai ex',208,'One Darkness attached; Nightmare Aura20 lowers Entei130 to110',ev=[208,209,210,211,213,214],energy=dict(type='Darkness',count=1,destination='Bench2 Darkrai ex',retreat_payment_by_type={}),hand_after=5),
    play('attack','Peck','opponent Active Entei ex',216,'Nidoran Peck20 lowers Entei110 to90; attack ends turn',ev=[215,216,217,219,220],hand_after=5,reveal=217)
], [draw('normal_draw',[research],[187],before=4,after=5),draw('supporter_draw',[king,'Deceptive Needle'],[191,192],play=1,before=4,after=6,cause=research)],bs,ba,hand([luck,king,cy,wall,king],215),3,
    autos=[auto('Energy generation',187.9,'Darkness present in selected187.95 frame; empty at187.7',[187.7,187.95]),auto('Nightmare Aura',211,'20 damage Entei130 to110',[211,213,214]),auto('Deceptive Needle eligibility',219,'No Needle damage while Darkrai remains Benched',[219]),auto('Poison checkup',221,'10 Poison damage Entei90 to80',[220,221])],first=188,drawend=187.6,beforeend=215,transition=185)
# Turn6 opponent.
t=225;bs=board(t,nido(t,en=1),[empty(1,t),dark(t,pos=2,en=1,tool='Deceptive Needle'),empty(3,t)],entei(t,hp=80,en=2,poison=True),oppbench(t,stage=1,energy=1),pp=1,pc=True)
t=267;ba=board(t,dark(t,en=1,tool='Deceptive Needle'),bench_empty(t),entei(t,hp=110,en=2),oppbench(t,stage=1,energy=2,second_entei=True),pp=2,phase='After second KO, Darkrai replacement and Legendary Pulse; turn7 transition',display=7)
row(6,'opponent',222,267,hiddenhand(4,225),[
    play('card_play','Poke Ball',None,227,'Search adds one hidden Basic Pokemon; hand 4 to 3 to 4',ev=[227,227.5,228,229,230,231],reveal=227.5),
    play('bench_pokemon','Entei ex','opponent Bench1',236,'Second Entei ex benched140HP',ev=[235,236,237,238],reveal=236),
    play('card_play','Pokemon Center Lady','opponent Active Entei ex',241,'Heals30 HP80 to110 and removes Poison',ev=[240,241,242,243,244,245,246],reveal=241),
    play('energy_attachment',None,'opponent Bench3 Charmeleon',248,'One Fire attached; Charmeleon1 to2, current Zone empty afterward',ev=[247,247.5,248,249,250],energy=dict(type='Fire',count=1,destination='Bench3 Charmeleon',retreat_payment_by_type={})),
    play('attack','Blazing Beatdown','owner Active Nidoran male',251,'60 damage knocks out second Nidoran; attack ends turn',ev=[251,252,253,254,255],reveal=251)
], [draw('normal_draw',[None],[224],before=3,after=4,hidden=True),draw('search',[None],[229],play=1,cause='Poke Ball',before=3,after=4,hidden=True),draw('ability_draw',[None],[266],cause='Legendary Pulse',before=2,after=3,hidden=True)],bs,ba,
    autos=[auto('Second Nidoran KO',255,'Removed with1 Darkness; opponent second point awarded',[254,255,258,259]),auto('Owner replacement choice',261,'Choose sole remaining Darkrai ex; free forced replacement, not retreat',[260,261,262,263]),auto('Legendary Pulse',265,'Entei draws1 hidden card',[265,266])],first=227,transition=222)
# Turn7 owner.
t=269.7;bs=board(t,dark(t,en=1,tool='Deceptive Needle'),bench_empty(t),entei(t,hp=110,en=2),oppbench(t,stage=1,energy=2,second_entei=True),pp=2)
t=285
nih=mon('Nihilego',70,70,pos=3,t=t,variant='More Poison / New Wave30',effects=[dict(name='More Poison',source='Nihilego',affected_player='opponent',affected_pokemon='Active',restriction_or_mark='Poison damage +10',expiry='While ability applies')])
ba=board(t,dark(t,en=2,tool='Deceptive Needle'),[empty(1,t),empty(2,t),nih],entei(t,hp=80,en=2),oppbench(t,stage=1,energy=2,second_entei=True),pp=2,phase='After End Turn and Deceptive Needle10; before turn8')
row(7,'owner',267,286,hand([luck,king,cy,wall,king,'Nihilego'],269.7),[
    play('bench_pokemon','Nihilego','owner Bench3',270.5,'Benched70HP; More Poison applies, without creating Poison',ev=[270.2,270.5,270.7,271,272,273,274],hand_after=5,reveal=272),
    play('energy_attachment',None,'owner Active Darkrai ex',275,'Second Darkness attaches; Nightmare Aura20 lowers Entei110 to90',ev=[275,276,277,278,279,280],energy=dict(type='Darkness',count=1,destination='Active Darkrai ex',retreat_payment_by_type={}),hand_after=5),
    play('end_turn',None,None,281,'End Turn accepted without attack or Supporter; no warning prompt observed',ev=[281,282,283,285,286],hand_after=5)
], [draw('normal_draw',['Nihilego'],[269],before=5,after=6)],bs,ba,hand([luck,king,cy,wall,king],281),3,
    autos=[auto('Energy generation',270.2,'Current absent at269.7; generated during270.2 flash and present afterward',[269.7,270.2,270.7]),auto('More Poison',273,'Opponent board receives Poison damage modifier; Entei is not Poisoned',[273,274]),auto('Nightmare Aura',278,'20 damage Entei110 to90',[278,279,280]),auto('Deceptive Needle',282,'Active Darkrai end effect10 lowers Entei90 to80',[282,283,285])],first=270.5,drawend=269.6,beforeend=281,transition=267)
# Turn8 opponent terminal sequence.
t=288
nih=mon('Nihilego',70,70,pos=3,t=t,variant='More Poison / New Wave30',effects=[dict(name='More Poison',source='Nihilego',affected_player='opponent',affected_pokemon='Active',restriction_or_mark='Poison damage +10',expiry='While ability applies')])
bs=board(t,dark(t,en=2,tool='Deceptive Needle'),[empty(1,t),empty(2,t),nih],entei(t,hp=80,en=2),oppbench(t,stage=1,energy=2,second_entei=True),pp=2,pc=True)
t=324
nih=mon('Nihilego',70,70,pos=3,t=t,variant='More Poison / New Wave30')
char=mon('Charizard ex',180,180,2,'Fire',t=t,variant='Slash60 / Crimson Storm200 / HP180')
vacant=dict(name='none',status='visibly_empty_after_KO_removal',basis='Darkrai removed; no replacement occurs before terminal result',evidence_ids=refs(323,324))
ba=board(t,vacant,[empty(1,t),empty(2,t),nih],char,[entei(t,pos=1),charm(t,pos=2),entei(t,hp=80,pos=3)],pp=2,phase='Terminal post-removal board, before awarded points animation. Opponent2 here; later327/339.7 confirms3.')
row(8,'opponent',286,329,hiddenhand(4,288),[
    play('card_play',research,None,292,'Opponent draws2 hidden cards',ev=[291,292,293,294,295],reveal=292),
    play('evolution','Charizard ex','opponent Bench3 Charmeleon',299,'Evolves into180HP Slash60/Crimson Storm200 Charizard with2 Fire',ev=[298,299,300,301,302],reveal=299),
    play('retreat',None,'opponent Entei ex to Bench3; Charizard ex to Active',305,'Entei retreats, pays2 Fire, Charizard becomes Active',ev=[304,305,306,307,308,309,310],energy=dict(type='Fire',count=0,destination='none',retreat_payment_by_type={'Fire':2})),
    play('card_play','Flame Patch','opponent Active Charizard ex',312,'Attach1 Fire from discard; Charizard2 to3 Fire',ev=[311,312,313,314],reveal=312,energy=dict(type='Fire',count=1,destination='Active Charizard ex',retreat_payment_by_type={})),
    play('energy_attachment',None,'opponent Active Charizard ex',315,'Normal zone Fire attachment; Charizard3 to4 Fire',ev=[314,315,316,317,318],energy=dict(type='Fire',count=1,destination='Active Charizard ex',retreat_payment_by_type={})),
    play('attack','Crimson Storm','owner Active Darkrai ex',319,'200 damage knocks out140HP Darkrai; Charizard discards2 Fire. Opponent earns2 points and wins.',ev=[319,320,321,322,323,324,327,328,339.7],reveal=319)
], [draw('normal_draw',[None],[288],before=3,after=4,hidden=True),draw('supporter_draw',[None,None],[294,295],play=1,cause=research,before=3,after=5,hidden=True)],bs,ba,
    autos=[auto('Crimson Storm Energy discard',322,'Charizard4 Fire to2; separate from retreat payment',[321,322,323]),auto('Darkrai KO/removal',323,'Darkrai and Needle removed; Active empty before result',[321,322,323,324]),auto('Awarded terminal points',327,'Opponent2 to3 displayed cap after +2 award',[325,326,327,339.7]),auto('Defeat',328,'Defeat; results339.7 report8 turns, owner0/opponent3 and70 damage done',[328,329,339.7])],first=292,transition=286)

# Draw-relative hand evidence is deliberately not a fixed grid.
T[3]['draws_and_searches'][1]['returned_or_discarded_cards']=[dict(name=None,action='shuffle to deck',timestamp_seconds=t,evidence_ids=refs(t),limit_reason='Opponent Pokemon identity concealed') for t in [135,140]]
for r,boundary in [(T[6],'board_after'),(T[7],'board_at_start'),(T[7],'board_after')]:
    b=r[boundary]
    b['opponent']['board_effects']=[dict(name='More Poison',source='owner Bench3 Nihilego',affected_pokemon='opponent Pokemon',restriction_or_mark='Poison damage +10; this does not inflict Poison',expiry='While the ability applies',evidence_ids=b['evidence_ids'])]
T[4]['hand_at_start']['evidence_ids']+=refs(186,187,187.7)
T[4]['hand_at_start']['cards_left_to_right'][0]['evidence_ids']+=refs(186,187,187.7)
T[4]['owner_hand_start']=copy.deepcopy(T[4]['hand_at_start'])
captures=[(1,53.0,53.2,61,[53.8,55.8,58.8]),(3,89.2,89.2,114,[90.2,92.2,95.2]),(5,187.6,187.95,215,[188.8,190.8,193.8]),(7,269.6,269.7,281,[270.6,272.6,275.6])]
capture_rows=[]
for num,end,selected,before,candidates in captures:
    for t in candidates:
        frame(t,'draw_end_candidate',num,draw_animation_end_seconds=end,offset_after_draw_seconds=round(t-end,2),selected_for_start_hand=False,before_first_play=False,unzoomed=t in [55.8,58.8,90.2,92.2,95.2,190.8,193.8,275.6],hand_spread=True,
            observation='Scheduled candidate inspected; the first play has already begun or resolved.',suitability_or_limit='Unsuitable intact preplay hand: immediate first play occurred before this candidate.')
    frame(selected,'selected_intact_preplay_hand',num,draw_animation_end_seconds=end,offset_after_draw_seconds=round(selected-end,2),selected_for_start_hand=True,before_first_play=True,unzoomed=True,hand_spread=True,
        observation='Full original fan intact after normal draw and before card commit. Turn5 Research is highlighted after preview closes; the leftmost slot is partly off-screen and supported by nearby continuity.',suitability_or_limit='Selected native intact preplay frame; exact subsecond PTS unmeasured.')
    frame(before,'before_end_hand',num,selected_for_start_hand=False,unzoomed=True,hand_spread=True,observation='Last clear hand before End Turn or pre-attack substitution.',suitability_or_limit='Turn5 uses pre-Peck frame because attack ends turn.' if num==5 else 'Before End Turn input')
    capture_rows.append(dict(turn_number=num,draw_animation_end_seconds=end,draw_end_timing_basis='Localized at native reveal/return inspection; precision approximately0.2seconds',candidate_evidence_ids=refs(*candidates),selected_preplay_evidence_ids=refs(selected),before_end_evidence_ids=refs(before),dense_preplay_window_inspected_seconds=[selected-.6,selected+.6],limit='Timing based on requested seeks, not measured PTS'))

# Opening, selection continuity and terminal evidence.
for t,role in [(1,'filmed_QR'),(3,'deck_editor'),(4,'deck_save'),(5,'event_selected_deck'),(6,'event_Battle'),(8,'human_matchmaking'),(14,'Nick_profile'),(26,'going_first'),(29,'opening_five'),(30,'Active_selection'),(31,'placed_Active'),(32,'setup_bench'),(38,'setup_complete'),(48,'revealed_setup'),(50,'turn1_label'),(339.7,'results')]: frame(t,role)
opening=['Nidoran male','Poison Barb','Nidoran male',luck,king]
limits=[
    'No full discard pile is opened in the source. Visible top previews and observed transactions are retained separately.',
    'Hidden opponent card identities and private prompt choices remain unknown; public actions are recorded in visible resolution order.',
    'Scheduled +1/+3/+6 hand candidates are post-play in all four owner turns; denser native seeks recover intact preplay fans.',
    'Turn5 selected five-slot fan has a partly off-screen leftmost Lucky Ice Pop. Its identity is supported by filmed continuity from the preceding hand; no deck-membership inference is used.',
    'QR establishes twenty semantic card slots and Darkness, with artwork/rarity unspecified. The initial dated live log snapshot lacks this Nidoking revision; a prepared deck entry is not a saved live snapshot.',
    'Input/reveal times are visually localized source-local requests, not measured PTS or exact touch telemetry.',
    'Terminal board324 is post-removal with opponent2 visible points. The separate327 and339.7 frames establish awarded terminal3 points; Darkrai0HP is a separate321/322 pre-removal state.'
]
pause=dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,review_date=NOW,sources=SRC,destination='https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',deck_name='Nidoking / Darkrai ex / Nihilego (one Darkrai, Cyrus revision)',
    opening=dict(source_video=V,timestamp_seconds=29,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=cards(opening,29),selected_active=dict(name='Nidoran male',opening_position=3,source_video=V,timestamp_seconds=30,evidence_ids=refs(30,31)),setup_bench=dict(name='Nidoran male',opening_position=1,bench_position=1,evidence_ids=refs(32,38)),redraw_or_replacement='none observed',before_active_placement=True,status='observed',evidence_ids=refs(29,30,31),limit_reason=None),
    packet_files=dict(prose='REVIEW.md',coverage='COVERAGE.md',deck='DECK_USED.json',turns='TURN_LEDGER.json',evidence='TURN_EVIDENCE.json'),capture_status='complete_with_recording_limits',battle_review_status='full_source_first_pass_complete_pending_independent_acceptance',outcome='loss',opponent='Nick',mode='Deluxe Pack: Mega Emblem Event',classification='human_event_battle',auto_control_observed=False,turn_count=8,final_points=dict(owner=0,opponent=3),limits=limits,lead_checked=False)
save('PAUSE_GAME.json',pause)
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=SRC,turns=T,limits=limits))

q=json.loads((P/'qr_intake/QR_DECODE_0001.00.json').read_text(encoding='utf-8'))
save('QR_DECODE.json',q)
entries=json.loads((P.parent/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8-sig'))
matched=[x for x in entries['decks'] if x.get('source_video')==V]
prepared=matched[0] if matched else None
deckslots=[]
for kind,ids in [('pokemon',q['decoded']['pokemonIds']),('trainer',q['decoded']['trainerIds'])]:
    for entity in ids:
        card=next(c for c in q['cards'] if c['entity_kind']==kind and c['entity_id']==entity)
        deckslots.append(dict(name=card['name'],entity_kind=kind,entity_id=entity,functional_id=card['functional_ids'][0],variant_basis='QR semantic entity',printing=None,printing_limit='QR does not identify artwork or rarity'))
deck=dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=SRC,deck_name_in_log=None,source_url='https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',captured_at='2026-10-06T17:07:52.454484+00:00',log_list_version=None,expected_card_count=20,cards_in_log_order=None,counts_by_name_and_variant=None,energy_configuration_from_log=None,actual_card_count=None,
    capture_source_text_or_image='../LIVE_DECK_SNAPSHOT.json',game_version_binding_basis='Filmed native QR1 -> deck editor3 -> save4 -> slot11 New deck6 selected in event5/6 -> matchmaking8 -> game setup. No intervening deck edit observed.',
    conflicts_with_filmed_cards='Initial nine-deck live snapshot has no corresponding Nidoking list; no matching live game-version snapshot can be claimed.',exact_list_status='filmed_QR_verified_live_log_version_missing',
    filmed_deck_label='New deck 6',filmed_slot=11,filmed_qr_receipt='qr_intake/QR_DECODE_0001.00.json',filmed_cards_in_order=deckslots,filmed_counts=q['cards'],filmed_actual_card_count=20,filmed_energy_configuration=['Darkness'],
    prepared_external_deck_id=prepared.get('id') if prepared else None,prepared_external_deck_name=prepared.get('deck_name') if prepared else None,external_saved=False,
    nearby_version_comparison=dict(source_video='20261005_123812000_iOS.MP4',difference='This filmed QR has Darkrai ex1 and Cyrus1; prior123812 QR had Darkrai ex2 and Cyrus0. Same New deck6 label is not a shared semantic deck identity.',basis='Frozen per-source QR entity/count comparison supplied at assignment and checked in this QR'),
    evidence_ids=refs(1,3,4,5,6,8),limits=['A prepared new deck entry is not saved live evidence. Exact filmed twenty-card semantic list retained; exact dated live-log snapshot for this revision pending root external workflow.','QR printing and rarity are unspecified.','Deck composition is not used to infer concealed hands.'])
save('DECK_USED.json',deck)
save('FILMED_DECK_SNAPSHOT.json',dict(source_video=V,source_sha256=SHA,card_slot_count=20,cards=deckslots,energy=['Darkness'],QR_receipt='qr_intake/QR_DECODE_0001.00.json',game_binding_evidence_ids=refs(1,3,4,5,6,8),external_saved=False))

discard=[]
for num,who,t,names in [(3,'owner',104,['Poke Ball']),(5,'owner',194,[research]),(7,'owner',270,['Nidoran male']),(4,'opponent',159,['Poke Ball']),(6,'opponent',249,['Pokemon Center Lady']),(8,'opponent',318,['Flame Patch'])]:
    did=f'discard_preview_{num}_{who}'
    discard.append(dict(snapshot_id=did,turn_number=num,pile_owner=who,source_video=V,timestamp_seconds=t,cards_in_view=names,scroll_coverage='Single visible top preview only; pile not opened',full_pile_established=False,evidence_ids=refs(t),limit_reason='No full-pile opening or scroll in recorded source'))
    T[num-1]['discard_snapshot_ids'].append(did)
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=SRC,turns=T,limits=limits))
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=G,sources=SRC,source_sha256=SHA,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,bottom_crop_height_fraction=.2,top_crop='Native top700px covering exposed fan, clock and both Energy circles',fixed_grid_is_turn_start_evidence=False),owner_turn_captures=capture_rows,frames=list(frames.values()),discard_snapshots=discard,scheduled_capture_limits=limits))

summary=dict(schema='whole-source-review-summary-v1',source_video=V,source_sha256=SHA,reviewer='/root/pause_124532',review_model='gpt-6.1-sol',reasoning_effort='high',reviewed_at_utc=NOW,scope='Whole source0 to339.899138seconds; one complete human event match',classification='human_event_battle',auto_control_observed=False,queue='Deluxe Pack: Mega Emblem Event',opponent='Nick',owner_name='Dacz8976',match_date_local='2026-10-05',recording_local='2026-10-05T07:45:32-05:00',owner_went_first=True,outcome='loss',turn_count=8,final_points=dict(owner=0,opponent=3),deck_core=['Nidoran male','Nidoking','Darkrai ex','Nihilego'],deck_version='One Darkrai ex plus Cyrus revision',capture_status='complete_with_recording_limits',review_status='first_pass_complete_pending_independent_acceptance',full_source_review_complete=True,battle_completion_established=True,independent_acceptance=False,
    outcome_evidence_ids=refs(319,320,321,323,327,328,339.7),limits=limits,
    suggested_independent_checks=[dict(seconds=[29,30,31,32],target='Original five and Active/Bench mapping'),dict(seconds=[53.2,53.6,55,58,61,63],target='Ordinary first owner decision and turn1'),dict(seconds=[88,89.2,89.6,93,94,96,99,103,109,114],target='Turn3 normal draw, Research order, Poke Ball search, intact hand and ending arithmetic'),dict(seconds=[123,143,146,148,150,155,162,164,167,171,177,179,181,184],target='Opponent turn4 beyond unusual ending: Rainbow Energy cycle, Ignition, item theft/search, attachment, KO and Poison order'),dict(seconds=[187.95,188,191,192,202,208,215,221],target='Turn5 intact preplay, Research order and5-card ending'),dict(seconds=[269.7,270.5,275,281,282,285],target='Turn7 early empty Energy, first play, Needle resolution'),dict(seconds=[299,305,312,315,319,321,323,327,339.7],target='Turn8 Energy accounting, pre-removal KO vs post-removal board and final result')])
save('SUMMARY.json',summary)
save('UNCERTAINTIES.json',dict(source_video=V,source_sha256=SHA,status='complete_with_recording_limits',unreviewed_intervals=[],consequential_unresolved_ambiguities=[],recording_limits=[dict(id=f'limit{i+1}',description=x) for i,x in enumerate(limits)],strategic_judgments='No strategic quality claim made; source review and public state only'))

lines=['# Whole-source review: '+V,'','Reviewer: /root/pause_124532, GPT-6.1 Sol high. Completed first pass '+NOW+'. Independent acceptance remains with the lead.','','Source: SOURCE.json, SHA-256 '+SHA+', 622584338 bytes, 339.899138 seconds, native1170x2532. Recording local October5,2026 at07:45:32 America/Chicago, from embedded UTC metadata.','','Human match against Nick in Deluxe Pack: Mega Emblem Event. No Auto control is visible. Owner Dacz8976 goes first and loses after8 turns, final displayed score0 to3. Charizard ex Crimson Storm deals200 to Darkrai ex on turn8. The results show70 damage done. This does not establish ranked mode.','','Deck continuity: retained QR at1s, revised deck editor at3s, save transition4s, slot11 New deck6 selected at5/6s, matchmaking8s and opening29s form an uninterrupted chain. This deck has one Darkrai ex and one Cyrus, unlike the prior source two-Darkrai revision. Exact filmed20 semantic cards and Darkness are retained. The initial dated live log snapshot lacks this deck version; prepared external deck data is not a saved log snapshot.','','Opening29s, before Active placement: Nidoran male, Poison Barb, Nidoran male, Lucky Ice Pop, Nidoking. The third opening slot becomes Active at30/31s; the first becomes Bench1 by32/38s. No redraw observed.','','Each row below links to the corresponding numbered TURN_LEDGER.json row. Action input/selection and reveal are separate where footage supplies them; timing precision is visual and source-local, not exact touch telemetry.','','| Turn | Player | Source seconds | Numbered actions and resolution | Ending owner hand |','|---|---|---|---|---|']
for r in T:
    acts='; '.join(str(x['order'])+'. '+(x['card_name'] or x['kind'])+' '+str(x['timestamp_seconds'])+'s: '+x['result'] for x in r['plays_in_order'])
    end=str(r['owner_hand_end']['count']) if r['who_played']=='owner' else 'n/a'
    lines.append(f"| {r['turn_number']} | {r['who_played']} | {r['timing']['turn_start_seconds']}-{r['timing']['turn_end_seconds']} | {acts} | {end} |")
lines += ['','Automatic effects and public ordering: turn2 Legendary Pulse adds one concealed card after the end action. Turn4 attack damages Nidoran60 to0, Poison Barb applies Poison, the KO removes Nidoran/Tool and awards one point, the owner chooses the other Nidoran without retreat cost, Legendary Pulse adds one hidden card, then Poison deals10, Entei140 to130. Turn5 Aura20, Peck20 and Poison10 produce130 ->110 ->90 ->80. Benched Needle produces no damage. Turn6 Center Lady heals80 ->110 and clears Poison before the attack; the second Nidoran KO awards point2, and the owner selects Darkrai as the forced replacement. Turn7 Aura20 and active Needle10 produce110 ->90 ->80; Nihilego adds More Poison but does not itself make Entei Poisoned. Turn8 Entei pays2 Fire to retreat; Flame Patch adds1 Fire to Charizard, ordinary Zone attachment adds another, Charizard reaches4 Fire then Crimson Storm discards2, leaving2. Darkrai is0HP at321/322s and removed at323/324s. Post-removal324 still shows opponent2 points; separate327/results339.7 establishes the terminal3-point display.','','Hand reconciliation: owner end counts are3,4,5,5 on turns1,3,5,7. Turn1: setup3 +Cyrus -Barb =3. Turn3: start4 -Research +Wally +Poke Ball -Poke Ball +Darkrai -bench Darkrai =4. Turn5: start5 -Research +Nidoking +Needle -Needle =5. Turn7: start6 -bench Nihilego =5. Ending identities are in the ledger, including both separate Nidoking copies. Opponent fan counts at owner starts are3,4,4,4; these are native exposed-back counts, not deck arithmetic.','','Draw record: Cyrus52s; Research88s; Research reveals Wally93s then Poke Ball94s; search reveals Darkrai99s. Research187s; second Research reveals Nidoking191s then Needle192s. Nihilego269s. Opponent normal draws, Research cards and Legendary Pulse cards stay concealed. No Copycat is played. Rainbow Cave cycles generated Energy, it does not draw a card.','','Hand capture: turn1 selected53.2s; turn3 selected89.2s; turn5 selected187.95s; turn7 selected269.7s. Each has retained native full frame and full-width bottom fifth/top crop. Scheduled +1/+3/+6 candidates are already after the immediate first play and are labeled unsuitable. Subsecond source inspection recovered the intact preplay hand. Turn5 leftmost Lucky Ice Pop is partly off-screen after the fan expands, supported by nearby observed continuity. The Research preview has closed at187.95 and all five slots remain before commit188.0. Before-end evidence:61,114,215 (pre-Peck substitution),281s.','','Energy at selected frame: turn3 at89.2 and turn7 at269.7 have EMPTY large current circles, recorded absent even though Darkness generates moments later. Turn5 at187.95 has a present Darkness sphere. Turn1 current is absent as the first turn. Next previews remain independently read Darkness for owner and Fire for opponent. No future Energy is inferred from deck type.','','Both start and end boards, ordered Bench rectangles including visibly empty positions, HP, maximum HP, typed attached Energy, Tool absence/presence, conditions, effects, Stadium and points appear in each ledger row. Current turn labels are cited separately; selected frames without labels use null plus reason instead of borrowing the ledger number.','','Discard views: neither complete pile is opened. Six retained top previews are explicitly limited. Thieving Machine publicly recovers the owner Poke Ball, and the removed Tool/KO states are evidenced; these transactions do not prove the whole hidden pile.','','Inspection coverage: whole0-339.899s with the continuous ordered native locating pass, denser1-second action windows, subsecond draw/preplay checks, and native checks of selected hands/mechanics. Coarse overview is only the locator; dense source-bound native events and boundaries supply the complete account. No source cut or unreviewed game turn remains.','','Recording limits:'] + ['- '+x for x in limits] + ['','Independent targets are in SUMMARY.json, including the ordinary turn1 first move and the full opponent turn4. No external game write, index edit, lead acceptance or media movement performed by this worker.']
(P/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
coverage=['# Source coverage','','Whole source '+V+' / '+SHA,'','| Interval seconds | Inspected scope | Status |','|---|---|---|','|0-8|QR, revised deck editor, save, event selection and matchmaking|covered|','|8-29|Nick identity, loading, going-first coin and deal|covered|','|29-50|Original five, Active/Bench placement, opponent setup and reveal|covered|']
for r in T:coverage.append(f"|{r['timing']['turn_start_seconds']}-{r['timing']['turn_end_seconds']}|Turn{r['turn_number']}: {r['who_played']}, every meaningful public action and automatic effect|covered|")
coverage += ['|329-339.899138|Loading then Defeat result panel; no second match|covered|','','All8 actual turns reviewed. No uncovered source interval or linked continuation is required. Public actions are reconciled with changing hands, HP, Energy, Tools, conditions, board occupancy and points. Hidden opponent inputs are an inspected recording limit. No full discard opening exists.','','Evidence methods: native fast seeks with2 decoder threads, ordered contact sheets from retained native frames, targeted1-second action inspections and dense0.05-0.3second preplay checks. A partial reduced overview decoder was stopped for performance; it was not treated as full coverage or native hand evidence. All useful full frames remain in this packet.','','Source access is frozen by SOURCE.json and intake identity event. Worker wrote only this packet. Independent acceptance and registration are pending root review.']
(P/'COVERAGE.md').write_text('\n'.join(coverage)+'\n',encoding='utf-8')
save('WORKER_CHECKS.json',dict(source_video=V,source_sha256=SHA,performed_at_utc=NOW,turn_count_matches_result=8,actual_owner_turn_numbers=[1,3,5,7],all_opening_slots=5,owner_ending_hand_counts=[3,4,5,5],all_normal_owner_draws_named=True,all_owner_Research_search_reveals_named=True,terminal_pre_removal_and_awarded_points_separated=True,selected_energy_absence_preserved=True,tools_stadium_absence_explicit=True,full_discard_limit_explicit=True,deck_revision_separate=True,external_written=False,source_moved=False,independent_acceptance=False,limit='Worker consistency checks do not substitute for independent visual acceptance'))
print(json.dumps({'turns':len(T),'frames':len(frames),'outcome':'loss','capture_status':pause['capture_status']},indent=2))
