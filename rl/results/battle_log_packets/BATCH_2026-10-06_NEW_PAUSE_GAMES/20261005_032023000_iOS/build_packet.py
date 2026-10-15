import json,copy,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
p=Path(__file__).parent
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
metadata=json.loads((p/'RECORDING_METADATA.json').read_text(encoding='utf-8-sig'))
video=src['video_basename'];sha=src['sha256'];gid='20261005_032023000_iOS_game1'
sources=[{'video_basename':video,'sha256':sha,'source_json':'SOURCE.json'}]
now=datetime.now(timezone.utc).isoformat()
def write(name,obj):
    (p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t): return f'f{t:07.2f}'
def ev(*times): return [eid(t) for t in times]
def card(name,variant=None): return {'name':name,'variant':variant}
TR="Team Rocket's Tinkatink"; TRT="Team Rocket's Tinkaton"; SUP='Aegislash [Superb Shield]';CUR='Aegislash [Cursed Metal]';POP='Lucky Ice Pop';CORE='Metal Core Barrier';RES="Professor's Research"
def hand(names,t,basis='direct native fan, left to right'):
    return {'cards_left_to_right':[{'position':i+1,'name':n.split(' [')[0],'variant':n.split(' [')[1][:-1] if ' [' in n else None,'basis':'visible card name/artwork and preceding named reveal','evidence_ids':ev(t),'limit_reason':None} for i,n in enumerate(names)],'count':len(names),'basis':basis,'evidence_ids':ev(t),'status':'observed','limit_reason':None}
start_hands={2:[CORE,POP,POP,RES,SUP],4:[CORE,POP,POP,SUP,'Honedge'],6:[CORE,POP,SUP,POP,'Poke Ball'],8:[CORE,POP,SUP,POP,TRT],10:[CORE,POP,SUP,POP,TRT,CUR],12:[SUP,TRT,CUR,RES]}
end_hands={2:[CORE,POP,POP,SUP],4:[CORE,POP,SUP,POP],6:[CORE,POP,SUP,POP],8:[CORE,POP,SUP,POP,TRT],10:[SUP,TRT,CUR],12:[TRT,CUR,'Tinkaton ex']}
selected={2:66.6,4:116.0,6:184.2,8:242.8,10:295.8,12:397.5}
draw_end={2:66.6,4:115.8,6:183.2,8:241.8,10:294.8,12:397.2}
candidates={2:[67.6,69.6,72.6],4:[116.8,118.8,121.8],6:[184.2,186.2,189.2],8:[242.8,244.8,247.8],10:[295.8,297.8,300.8],12:[398.2,400.2,403.2]}
first_input={2:67,4:116.5,6:186,8:248.5,10:308,12:397.8}
before_end={2:89,4:133,6:203,8:251,10:352,12:439}
start_frame={1:46,2:66.6,3:96,4:116,5:140,6:184.2,7:212,8:242.8,9:260,10:295.8,11:360,12:397.5,13:448}
end_frame={1:63,2:92,3:112,4:136,5:179,6:207,7:237,8:256,9:291,10:355,11:393,12:443,13:467}
banner={1:46,2:64,3:93,4:113,5:137,6:180,7:208,8:239,9:257,10:292,11:356,12:394,13:445}
turn_limits=["Opponent identities remain hidden unless played or publicly shown. Remote card input timestamps are not visible; listed reveal/resolution timestamps are not inputs.","The recording never opens a full discard pile. Top previews are limited observations.","Seek seconds are requested source-local positions; exact decoded PTS was not measured.","Random attack resolutions show aggregate damage at once; the order of individual random target selections is not exposed."]
frames={}
def addframe(t,role,turn=None,obs='',selected_hand=False,pre=None,zoom=None,spread=None,limit=None):
    k=eid(t)
    if k not in frames:
        f=p/'turn_evidence'/f't{t:07.2f}.jpg'
        assert f.exists(),f
        im=Image.open(f);assert im.size==(1170,2532),im.size
        b=p/'turn_evidence'/f't{t:07.2f}_bottom.png';top=p/'turn_evidence'/f't{t:07.2f}_top.png'
        im.crop((0,2025,1170,2532)).save(b);im.crop((0,0,1170,770)).save(top)
        frames[k]={'evidence_id':k,'role':[role],'turn_number':turn,'who_played':('owner' if turn and turn%2==0 else 'opponent') if turn else None,'source_video':video,'source_sha256':sha,'draw_animation_end_seconds':draw_end.get(turn),'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':round(t-draw_end[turn],2) if turn in draw_end else None,'full_frame_path':f'turn_evidence/{f.name}','native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':f'turn_evidence/{b.name}','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':f'turn_evidence/{top.name}','pixel_bounds_x0_y0_x1_y1':[0,0,1170,770]},'selected_for_start_hand':selected_hand,'before_first_play':pre,'unzoomed':zoom,'hand_spread':spread,'observation':obs,'suitability_or_limit':limit}
    else:
        frames[k]['role'].append(role)
        if obs: frames[k]['observation']+='; '+obs
        if selected_hand: frames[k]['selected_for_start_hand']=True
        if pre is not None: frames[k]['before_first_play']=pre
        if zoom is not None: frames[k]['unzoomed']=zoom
        if spread is not None: frames[k]['hand_spread']=spread
        if limit is not None: frames[k]['suitability_or_limit']=limit
    return k
for n in range(1,14):
    addframe(banner[n],'readable_current_turn_label',n,f'Current turn: {n}; this is a start transition, not the preceding concluded turn.')
    addframe(start_frame[n],'starting_board',n,'Both boards and Energy Zones at this turn boundary.')
    addframe(end_frame[n],'resolved_board',n,'Turn consequences resolved; terminal points may use a separate frame.')
for n in selected:
    addframe(selected[n],'selected_preplay_owner_hand',n,'Intact named owner hand after normal draw and before first voluntary play.',True,True,True,True)
    for t in candidates[n]:
        suitable=t<first_input[n]
        zoomed=t in [121.8,398.2]
        addframe(t,'draw_relative_candidate',n,'Inspected approximately +1/+3/+6-second candidate.',t==selected[n],suitable,not zoomed,not zoomed,'Suitable intact preplay hand.' if suitable else 'After first voluntary play; cannot replace the preplay hand. '+('Card zoom is visible.' if zoomed else 'Hand count or card positions already changed.'))
    addframe(before_end[n],'before_attack_hand_substitution',n,'Last clear hand before the attack ends the turn. Attack substitutes for End Turn.',False,False,n not in [6,8,12],True,'After all card plays; use for ending hand/count only.')
addframe(28,'opening_five',obs='Before Active placement: Metal Core Barrier, Lucky Ice Pop, Team Rocket\'s Tinkatink, Lucky Ice Pop, Professor\'s Research.',zoom=True,spread=True)
addframe(30,'selected_active_setup',obs="Team Rocket's Tinkatink chosen as Active; four hand cards remain.")
addframe(2.5,'deck_label_continuity',obs='Filmed deck editor reads New deck 6 immediately after QR closing.')
addframe(4,'deck_selection_continuity',obs='Selected New deck 6 slot with Honedge, before matchmaking.')
addframe(6,'human_matchmaking',obs='Searching for opponent.')
addframe(12,'opponent_identity',obs='Opponent 犬いぬ, level60 matchmaking profile.')
addframe(476,'result',obs='Defeat vs 犬いぬ; went second; turns played13; owner0 points, opponent3; damage done180.')
addframe(480,'source_ending',obs='Postgame thanks overlay; recording ends after completed result.')
def pokemon(name,hp,maximum,energy=0,etype='Metal',tool='none',variant=None,effects=None,t=0,pos=None):
    return {'name':name,'variant':variant,'bench_position':pos,'hp_now':hp,'hp_max':maximum,'hp_max_basis':'visible printed HP and visible Giant Cape +20 where applicable','damage':maximum-hp,'attached_energy':{'total':energy,'by_type':{etype:energy} if energy else {}},'tool':tool,'special_conditions':[],'active_effects':effects or [],'evidence_ids':ev(t),'status':'observed','limit_reason':None}
def empty(pos,t): return {'bench_position':pos,'name':None,'status':'visibly_empty','limit_reason':None,'evidence_ids':ev(t)}
def zone(etype,available,t):return {'this_turn':{'type':etype if available else 'none','count':1 if available else 0,'available':available},'next':{'type':etype,'count':1,'available':True},'basis':'visible large current icon or empty well and smaller next icon','evidence_ids':ev(t),'limit_reason':None}
def side(active,bench,etype,available,points,t,effects=None):
    return {'active':active,'bench_in_position_order':[b if b is not None else empty(i+1,t) for i,b in enumerate(bench)],'energy_zone':zone(etype,available,t),'points':points,'board_effects':effects or [],'evidence_ids':ev(t),'status':'observed','limit_reason':None}
def board(n,phase,t,own,opp,display=None):return {'turn_number_displayed':display,'turn_number_displayed_evidence_ids':ev(banner[n]) if display else [],'turn_number_limit_reason':None if display else 'No readable Current turn label in the resolved-board frame. The concluded turn is recorded in phase.','phase':phase,'stadium':'none','owner':own,'opponent':opp,'shared_effects':[],'evidence_ids':ev(t,banner[n]) if display else ev(t)}
# Each state is the post-resolution board; next starts copy it with fresh current Energy.
def P(name,hp,maxhp,energy,t,tool='none',variant=None,effects=None,pos=None):return pokemon(name,hp,maxhp,energy,'Metal' if name in [TR,'Honedge','Aegislash'] else 'Water',tool,variant,effects,t,pos)
def state(n,t,oa,ob,pa,pb,pts=0,oe=False,pe=False,oeffects=None,peffects=None):
    return board(n,f'concluded turn {n}, after resolution',t,side(oa,ob,'Metal',oe,0,t,oeffects),side(pa,pb,'Water',pe,pts,t,peffects))
ends={}
ends[1]=state(1,63,P(TR,60,60,0,63),[None]*3,P('Finizen',80,80,0,63,'Giant Cape','Razor Fin'),[P('Manaphy',50,50,0,63,pos=1),None,P('Wiglett',60,60,0,63,pos=3)])
ends[2]=state(2,92,P(TR,60,60,1,92),[P('Honedge',60,60,0,92,pos=1),P(TR,60,60,0,92,pos=2),None],P('Finizen',60,80,0,92,'Giant Cape','Razor Fin'),[P('Manaphy',50,50,0,92,pos=1),None,P('Wiglett',60,60,0,92,pos=3)])
ends[3]=state(3,112,P(TR,40,60,1,112),[P('Honedge',60,60,0,112,pos=1),P(TR,60,60,0,112,pos=2),None],P('Finizen',60,80,1,112,'Giant Cape','Razor Fin'),[P('Manaphy',50,50,0,112,pos=1),None,P('Wugtrio ex',140,140,0,112,variant='Pop Out Throughout',pos=3)])
ends[4]=state(4,136,P(TR,60,60,1,136),[P('Honedge',60,60,1,136,pos=1),P(TR,60,60,0,136,pos=2),P('Honedge',60,60,0,136,pos=3)],P('Finizen',40,80,1,136,'Giant Cape','Razor Fin'),[P('Manaphy',50,50,0,136,pos=1),None,P('Wugtrio ex',140,140,0,136,variant='Pop Out Throughout',pos=3)])
ends[5]=copy.deepcopy(ends[4]);ends[5]['phase']='concluded turn 5, after Razor Fin';ends[5]['owner']['active']['hp_now']=40;ends[5]['owner']['active']['damage']=20;ends[5]['opponent']['active']['hp_now']=80;ends[5]['opponent']['active']['damage']=0;ends[5]['opponent']['bench_in_position_order'][2]['attached_energy']={'total':1,'by_type':{'Water':1}}
ends[6]=copy.deepcopy(ends[5]);ends[6]['phase']='concluded turn 6, after Lunge Out';ends[6]['owner']['active']['hp_now']=60;ends[6]['owner']['active']['damage']=0;ends[6]['owner']['bench_in_position_order'][0]['attached_energy']={'total':2,'by_type':{'Metal':2}};ends[6]['opponent']['active']['hp_now']=60;ends[6]['opponent']['active']['damage']=20
ends[7]=state(7,237,P(TR,60,60,1,237),[P('Honedge',60,60,2,237,pos=1),P(TR,60,60,0,237,pos=2),P('Honedge',60,60,0,237,pos=3)],P('Manaphy',50,50,1,237,variant='Oceanic Gift'),[P('Finizen',60,80,2,237,'Giant Cape','Razor Fin',pos=1),None,P('Wugtrio ex',140,140,2,237,variant='Pop Out Throughout',pos=3)])
ends[8]=copy.deepcopy(ends[7]);ends[8]['phase']='concluded turn 8, after Lunge Out';ends[8]['owner']['bench_in_position_order'][1]['attached_energy']={'total':1,'by_type':{'Metal':1}};ends[8]['opponent']['active']['hp_now']=30;ends[8]['opponent']['active']['damage']=20
ends[9]=state(9,291,P(TR,60,60,1,291),[P('Honedge',10,60,2,291,pos=1),P(TR,60,60,1,291,pos=2),None],P('Wugtrio ex',140,140,3,291,variant='Pop Out Throughout'),[P('Finizen',60,80,2,291,'Giant Cape','Razor Fin',pos=1),None,P('Manaphy',30,50,0,291,variant='Oceanic Gift',pos=3)],1)
barrier={'name':'Metal Core Barrier','source':'attached Tool','affected_pokemon':'owner Active Honedge','restriction_or_mark':'Metal-type holder takes -50 damage from opponent attacks','expires':'end of opponent turn 11; removal visibly resolves389-391s','evidence_ids':ev(350.5,387,389,390,391)}
ends[10]=state(10,355,P('Honedge',60,60,2,355,CORE,effects=[barrier]),[P(TR,60,60,0,355,pos=1),P(TR,60,60,2,355,pos=2),None],P('Wugtrio ex',120,140,3,355,variant='Pop Out Throughout'),[P('Finizen',60,80,2,355,'Giant Cape','Razor Fin',pos=1),None,P('Manaphy',30,50,0,355,variant='Oceanic Gift',pos=3)],1)
flower={'name':'Flower Shield','source':'opponent benched Comfey','affected_player':'opponent','restriction_or_mark':'Conditional protection from Special Conditions if Psychic Energy attached; no Psychic Energy visible on board','status':'conditional; no active protected Pokemon established','expires':None,'evidence_ids':ev(363,365)}
ends[11]=state(11,393,P('Honedge',60,60,2,393),[P(TR,10,60,0,393,pos=1),P(TR,10,60,2,393,pos=2),None],P('Wugtrio ex',120,140,3,393,variant='Pop Out Throughout'),[P('Finizen',60,80,2,393,'Giant Cape','Razor Fin',pos=1),P('Comfey',70,70,0,393,variant='Flower Shield',pos=2),P('Manaphy',30,50,1,393,variant='Oceanic Gift',pos=3)],1,peffects=[flower])
shield={'name':'Superb Shield','source':'owner Aegislash attack','affected_pokemon':'owner Active Aegislash','restriction_or_mark':'takes -80 damage from attacks by opponent Pokemon ex during next opponent turn','expires':'after opponent turn13','evidence_ids':ev(443,445,462)}
ends[12]=state(12,443,P('Aegislash',140,140,3,443,variant='Superb Shield',effects=[shield]),[P(TR,10,60,0,443,pos=1),P(TR,10,60,2,443,pos=2),None],P('Wugtrio ex',40,140,3,443,variant='Pop Out Throughout'),[P('Finizen',60,80,2,443,'Giant Cape','Razor Fin',pos=1),P('Comfey',70,70,0,443,variant='Flower Shield',pos=2),P('Manaphy',30,50,1,443,variant='Oceanic Gift',pos=3)],1,peffects=[flower])
ends[13]=state(13,465,P('Aegislash',140,140,3,465,variant='Superb Shield',effects=[shield]),[None]*3,P('Wugtrio ex',40,140,3,465,variant='Pop Out Throughout'),[P('Palafin',130,130,3,465,'Giant Cape','Jet Punch',pos=1),P('Comfey',70,70,0,465,variant='Flower Shield',pos=2),P('Manaphy',30,50,1,465,variant='Oceanic Gift',pos=3)],3,peffects=[flower])
ends[13]['phase']='concluded turn13, terminal post-removal board465s; three opponent points separately467s'
ends[13]['evidence_ids']=ev(465,467,476)
initial=state(1,46,P(TR,60,60,0,46),[None]*3,P('Finizen',60,60,0,46,variant='Razor Fin'),[None,None,P('Wiglett',60,60,0,46,pos=3)])
def rebind(obj,t):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k=='evidence_ids':obj[k]=ev(t)
            else:rebind(v,t)
    elif isinstance(obj,list):
        for v in obj:rebind(v,t)
for n,b in ends.items():
    if n in [5,6,8]:rebind(b,end_frame[n]);b['evidence_ids']=ev(end_frame[n])
actions={}
def action(kind,name,t,result,target=None,hc=None,energy=None,nested=None,reveal=None,remote=False):
    times=[t] if t is not None else []
    if reveal is not None:times.append(reveal)
    for sec in times:addframe(sec,'action_or_reveal',obs=result)
    return {'kind':kind,'card_name':name,'target':target,'energy':energy,'result':result,'prompt_text':None,'response':None,'nested_events_in_order':nested or [],'hand_count_after':hc,'source_video':video,'timestamp_seconds':None if remote else t,'input_timestamp_seconds':None if remote else t,'reveal_or_resolution_seconds':reveal if reveal is not None else t,'evidence_ids':ev(*times),'basis':'visible remote reveal/resolution; input hidden' if remote else 'visible owner selection/input, with separate resolution when retained','limit_reason':'Remote input is not filmed.' if remote else None}
def energy(typ,dest,t,remote=False):return action('energy_attachment',None,t,f'One {typ} Energy attached to {dest}.',dest,energy={'type':typ,'count':1,'destination':dest,'retreat_payment_by_type':{}},remote=remote)
def pop(t,reveal,hp,coin,coin_t,hc,remote=False):
    addframe(coin_t,'coin_result',obs=f'Lucky Ice Pop {coin}.')
    return action('card_play',POP,t,f'Active healed {hp}; {coin}; '+('card returns to hand' if coin=='heads' else 'card discarded'),target='acting Active',hc=hc,reveal=reveal,remote=remote,nested=[{'order':1,'event':'heal','detail':hp,'evidence_ids':ev(reveal)},{'order':2,'event':'coin','result':coin,'evidence_ids':ev(coin_t)}])
actions[1]=[action('card_play','Poke Ball',49,'Search resolves as an unrevealed card back at51s; a Manaphy is then benched. Do not assert searched identity solely from subsequent bench.',reveal=51,remote=True),action('bench','Manaphy',54,'Manaphy50 placed in opponent Bench1.','opponent Bench1',remote=True),action('tool_attachment','Giant Cape',59,'Finizen maximum/current HP rises60->80.','opponent Active Finizen',reveal=63,remote=True),action('end_turn',None,64,'Opponent ends without an attack or Energy attachment; owner turn2 begins.',remote=True)]
actions[2]=[action('card_play',RES,67,'Research draws Poke Ball then Honedge.',hc=6,reveal=68),action('card_play','Poke Ball',73,'Search finds Team Rocket\'s Tinkatink.',hc=6,reveal=74),action('bench',TR,77,'Second TR Tinkatink placed on Bench2.','owner Bench2',5,reveal=78),energy('Metal','owner Active TR Tinkatink',79),action('bench','Honedge',82,'Honedge placed on Bench1.','owner Bench1',4,reveal=83),action('attack','Lunge Out',89,'20 damage to Finizen80->60; turn ends.','opponent Active Finizen',4,reveal=91)]
actions[3]=[action('evolution','Wugtrio ex',103,'Wiglett evolves into Wugtrio ex140 on Bench3.','opponent Bench3',remote=True),energy('Water','opponent Active Finizen',105,True),action('attack','Razor Fin',110,'20 damage to owner TR Tinkatink60->40.','owner Active TR Tinkatink',reveal=111,remote=True)]
actions[4]=[action('bench','Honedge',116.8,'Second Honedge placed on Bench3.','owner Bench3',4,reveal=117),pop(121,125,'40->60','heads',128,4),energy('Metal','owner Bench1 Honedge',130),action('attack','Lunge Out',133,'20 damage to Finizen60->40.','opponent Active Finizen',4,reveal=135)]
actions[5]=[energy('Water','opponent Bench3 Wugtrio ex',152.5,True),pop(155,159,'40->60','heads',162,3,True),pop(165,168,'60->80','tails',172,2,True),action('attack','Razor Fin',177,'20 damage to owner TR Tinkatink60->40.','owner Active TR Tinkatink',reveal=179,remote=True)]
actions[6]=[action('card_play','Poke Ball',186,'No-effect play; banner: There are no cards in the deck that can be the target of the effect. No searched card.',hc=4,reveal=187),pop(191,194,'40->60','heads',197,4),energy('Metal','owner Bench1 Honedge',199),action('attack','Lunge Out',203,'20 damage to Finizen80->60.','opponent Active Finizen',4,reveal=207)]
actions[6][0]['nested_events_in_order']=[{'order':1,'event':'no_target_banner','text':'There are no cards in the deck that can be the target of the effect','evidence_ids':ev(189)}]
actions[7]=[action('card_play','X Speed',221,'Retreat Cost is1 less for this turn; message223s.',remote=True),action('retreat',None,228,'Finizen retreats for0 after X Speed; Manaphy promoted; Finizen retains one Water.','opponent Manaphy',energy={'type':None,'count':0,'destination':None,'retreat_payment_by_type':{}},remote=True),energy('Water','opponent Active Manaphy',230,True),action('attack','Oceanic Gift',235,'Adds one Water each to benched Finizen1->2 and Wugtrio ex1->2. No damage.',reveal=237,remote=True)]
actions[8]=[energy('Metal','owner Bench2 TR Tinkatink',249),action('attack','Lunge Out',251,'20 damage to Manaphy50->30.','opponent Active Manaphy',5,reveal=256)]
actions[9]=[action('retreat',None,275,'Manaphy retreats, pays one Water1->0; Wugtrio ex promoted.','opponent Wugtrio ex',energy={'type':'Water','count':1,'destination':None,'retreat_payment_by_type':{'Water':1}},remote=True),energy('Water','opponent Active Wugtrio ex',278,True),action('attack','Pop Out Throughout',283,'Aggregate resolution:50 to owner Bench1 Honedge60->10,100 to Bench3 Honedge60->0. Bench3 removed287s; +1 point290s. Individual random selection order is not shown.',reveal=285,remote=True)]
actions[10]=[action('retreat',None,308,'TR Tinkatink pays one Metal1->0; Bench1 Honedge10HP promoted. Retreated TR occupies Bench1.','owner Honedge',energy={'type':'Metal','count':1,'destination':None,'retreat_payment_by_type':{'Metal':1}},reveal=312),pop(314,317,'10->30','tails',320.3,5),pop(322,327,'30->50','heads',331,5),pop(332,336,'50->60','tails',339.7,4),action('tool_attachment',CORE,343,'Metal Core Barrier attached to Active Honedge.','owner Active Honedge',3,reveal=348),energy('Metal','owner Bench2 TR Tinkatink',351),action('attack','Pierce',353,'20 damage to Wugtrio ex140->120.','opponent Active Wugtrio ex',3,reveal=355)]
actions[11]=[action('bench','Comfey',363,'Comfey70 with Flower Shield placed on Bench2. Conditional ability banner; no Psychic attached.','opponent Bench2',remote=True),energy('Water','opponent Bench3 Manaphy',383,True),action('attack','Pop Out Throughout',386,'Aggregate resolution:50 to each benched TR Tinkatink60->10;0 to Honedge because Metal Core Barrier. Individual selection order not exposed.',reveal=387,remote=True)]
actions[12]=[action('card_play',RES,398,'Research draws Rare Candy then Tinkaton ex.',hc=5,reveal=399),action('card_play','Rare Candy',411,'Rare Candy eventually evolves Active Honedge into Aegislash [Superb Shield].',target='owner Active Honedge',hc=3,reveal=435,nested=[{'order':1,'event':'evolution_selection','card':'Aegislash [Superb Shield]','evidence_ids':ev(415,417)},{'order':2,'event':'selection_inspection','card':TRT,'evidence_ids':ev(423,425)},{'order':3,'event':'invalid_selection','card':'Tinkaton ex','message':'Unable to evolve','evidence_ids':ev(427,429)},{'order':4,'event':'choose_evolution','card':'Aegislash [Superb Shield]','target':'Honedge','evidence_ids':ev(431,433,435)}]),energy('Metal','owner Active Aegislash',437),action('attack','Superb Shield',439,'80 damage to Wugtrio ex120->40; owner Aegislash gets next-opponent-turn -80 versus ex attacks.','opponent Active Wugtrio ex',3,reveal=443)]
actions[13]=[action('evolution','Palafin',451,'Bench1 Finizen evolves to Palafin; damage clears, effective maximum130 with retained Giant Cape.','opponent Bench1',reveal=453,remote=True),energy('Water','opponent Bench1 Palafin',455,True),action('attack','Pop Out Throughout',460,'Aggregate resolution:50 to each10HP benched TR Tinkatink, both0HP at463s and removed464-465s;0 to Aegislash under Superb Shield. +2 points467-468s reaches3; Defeat471s.',reveal=462,remote=True)]
draws={}
def draw(kind,n,names,times,play=None,before=None,after=None,limit=None):
    for t in times:addframe(t,'draw_or_search_reveal',n,'Named reveal or explicitly hidden card-back draw.')
    return {'kind':kind,'caused_by':None if play is None else actions[n][play-1]['card_name'],'linked_play_order':play,'cards_in_reveal_order':[{'name':name.split(' [')[0] if name else None,'variant':name.split(' [')[1][:-1] if name and ' [' in name else None,'reveal_position':i+1,'source_video':video,'timestamp_seconds':times[i],'evidence_ids':ev(times[i]),'basis':'native reveal' if name else 'card back only; identity hidden','limit_reason':None if name else limit or 'Opponent card identity is hidden.'} for i,name in enumerate(names)],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':[],'source_video':video,'timestamp_seconds':times[0],'evidence_ids':ev(*times),'limit_reason':limit}
for n,name,time in [(2,SUP,66),(4,'Honedge',115),(6,'Poke Ball',182),(8,TRT,241),(10,CUR,294),(12,RES,396)]:draws[n]=[draw('normal_draw',n,[name],[time],before=len(start_hands[n])-1,after=len(start_hands[n]))]
draws[2]+=[draw('supporter_draw',2,['Poke Ball','Honedge'],[71,72],1,4,6),draw('search',2,[TR],[76],2,5,6)]
draws[6]+=[draw('search_no_target',6,[],[189],1,4,4,'Visible no-target banner; no card found.')]
draws[6][-1]['cards_in_reveal_order']=[]
draws[12]+=[draw('supporter_draw',12,['Rare Candy','Tinkaton ex'],[401,402],1,3,5)]
oppdrawtimes={1:46,3:96,5:140,7:212,9:260,11:360,13:448}
for n,t in oppdrawtimes.items():draws[n]=[draw('normal_draw_hidden',n,[None],[t],limit='Opponent normal turn addition is not identity-revealed; timestamp is settled post-draw fan boundary, not a measured animation end.')]
draws[1].append(draw('search_hidden',1,[None],[51],1,limit='Poke Ball search shown as a card back. Subsequent Manaphy bench does not alone prove search identity.'))
turns=[]
fan={2:2,4:2,6:2,8:2,10:3,12:3}
for n in range(1,14):
    t=start_frame[n]
    st=copy.deepcopy(initial if n==1 else ends[n-1]);rebind(st,t)
    st['phase']=f'turn {n} start, after normal draw' if n%2==0 else f'turn {n} start, settled board/fan boundary'
    st['turn_number_displayed']=n;st['turn_number_displayed_evidence_ids']=ev(banner[n]);st['turn_number_limit_reason']=None;st['evidence_ids']=ev(t,banner[n])
    st['owner']['energy_zone']=zone('Metal',n%2==0,t);st['opponent']['energy_zone']=zone('Water',n%2==1 and n>1,t)
    en=copy.deepcopy(ends[n]);en['turn_number_displayed']=None;en['turn_number_displayed_evidence_ids']=[];en['turn_number_limit_reason']='No readable Current turn label in resolved board frame; phase names concluded turn.'
    for i,a in enumerate(actions[n]):a['order']=i+1
    h=hand(start_hands[n],selected[n]) if n in selected else {'cards_left_to_right':None,'count':None,'basis':'opponent fan only; hidden identities','evidence_ids':ev(t),'status':'hidden','limit_reason':'Opponent identities and exact start fan count are not needed to infer hidden cards; no unsupported exact count supplied.'}
    ah=hand(start_hands[n],selected[n]) if n in selected else {'cards_left_to_right':None,'count':None,'basis':None,'evidence_ids':[],'status':'not_applicable','limit_reason':'Opponent acts on odd turns.'}
    eh=hand(end_hands[n],before_end[n],'direct last pre-attack fan plus action arithmetic') if n in selected else {'cards_left_to_right':None,'count':None,'basis':None,'evidence_ids':[],'status':'not_applicable','limit_reason':'Owner hand end capture is required on owner turns; odd turn owner hand unchanged.'}
    auto=[]
    if n==9:auto=[{'order':1,'event':'knockout_removal','target':'owner Bench3 Honedge','evidence_ids':ev(286,287)},{'order':2,'event':'award_point','opponent_points':1,'evidence_ids':ev(290)}]
    if n==11:auto=[{'order':1,'event':'Metal Core Barrier discards at opponent-turn end','evidence_ids':ev(389,390,391)}]
    if n==13:auto=[{'order':1,'event':'two Bench TR Tinkatink knockouts/removal','evidence_ids':ev(463,464,465)},{'order':2,'event':'award2points and terminal result','opponent_points':3,'evidence_ids':ev(467,468,471,476)}]
    turns.append({'turn_number':n,'who_played':'owner' if n%2==0 else 'opponent','source_video':video,'timing':{'start_transition_seconds':banner[n],'draw_animation_end_seconds':draw_end.get(n),'draw_end_precision':'approximately0.2-0.6s from native samples; not measured PTS' if n%2==0 else 'opponent draw remains hidden','first_voluntary_move_seconds':first_input.get(n),'first_remote_reveal_seconds':actions[n][0]['reveal_or_resolution_seconds'] if n%2 else None,'before_end_action_seconds':before_end.get(n),'end_after_resolution_seconds':end_frame[n]},'hand_at_start':h,'owner_hand_start':ah,'opponent_hand_at_owner_turn_start':{'count':fan.get(n),'supported_range':None,'count_method':'count exposed card backs in retained native top crop','basis':'direct visual count' if n%2==0 else 'not_applicable','evidence_ids':ev(selected[n]) if n%2==0 else [],'limit_reason':None if n%2==0 else 'Not an owner-turn start.'},'draws_and_searches':draws[n],'plays_in_order':actions[n],'automatic_events_in_order':auto,'board_at_start':st,'board_after':en,'owner_hand_end':eh,'discard_snapshot_ids':[],'turn_evidence_ids':ev(banner[n],t,end_frame[n])+ (ev(*candidates[n],selected[n],before_end[n]) if n in selected else []),'limits':turn_limits})
for n,row in enumerate(turns,1):
    if n in [5,6,8]:row['board_after']['evidence_ids']=ev(end_frame[n])
    # The end current zones have both been consumed. Energy generation refreshes on subsequent start.
    row['board_after']['owner']['energy_zone']=zone('Metal',False,end_frame[n]);row['board_after']['opponent']['energy_zone']=zone('Water',False,end_frame[n])
    row['board_after']['owner']['evidence_ids']=ev(end_frame[n]);row['board_after']['opponent']['evidence_ids']=ev(end_frame[n])
    if n==13:row['board_after']['evidence_ids']=ev(465,467,476)
# Retain evidence used by all nested claims and source states.
def allrefs(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k.endswith('evidence_ids') and isinstance(v,list):
                for item in v:
                    if isinstance(item,str) and item.startswith('f'):yield item
            else:yield from allrefs(v)
    elif isinstance(x,list):
        for v in x:yield from allrefs(v)
for k in sorted(set(allrefs(turns))):
    if k not in frames:addframe(float(k[1:]),'supporting_native_observation',obs='Retained supporting native source observation cited by ledger.')
discards=[]
for n,t,owner,name in [(2,66.6,'opponent','Poke Ball'),(6,189,'owner','Poke Ball'),(5,176,'opponent',POP),(10,296,'owner','Honedge'),(10,340,'owner',POP),(11,393,'owner',CORE),(12,403,'owner',RES),(12,443,'owner','Rare Candy'),(7,237,'opponent','X Speed')]:
    addframe(t,'limited_discard_top_preview',n,'Only discard top preview visible; pile not opened.')
    discards.append({'snapshot_id':f'discard_{owner}_{t:07.2f}','turn_number':n,'pile_owner':owner,'source_video':video,'timestamp_seconds':t,'cards_in_view':[{'name':name,'count':1}],'scroll_coverage':'top preview only; no pile screen/scroll','full_pile_established':False,'evidence_ids':ev(t),'limit_reason':'The footage never opens this full discard pile.'})
deckdata=json.loads((p.parent/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8-sig'))
deck=next(d for d in deckdata['decks'] if d['source_video']==video)
write('DECK_USED.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':sources,'deck_name_in_log':None,'prepared_deck_name':deck['deck_name'],'filmed_deck_label':'New deck6','source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','captured_at':deckdata['prepared_utc'],'log_list_version':None,'expected_card_count':20,'cards_in_log_order':None,'cards_in_filmed_QR_order':deck['card_slots'],'counts_by_name_and_variant':deck['cards_in_display_order'],'energy_configuration_from_log':None,'energy_configuration_from_filmed_QR':['Metal'],'actual_card_count':20,'capture_source_text_or_image':['../NEW_DECK_ENTRIES.json','qr_intake/QR_DECODE_0001.00.json','qr_intake/t0001.00.png','turn_evidence/t0002.50.jpg','turn_evidence/t0004.00.jpg'],'game_version_binding_basis':'Same source closes filmed QR into New deck6 editor2.5s, selects New deck6 at4s, and proceeds directly to matchmaking6s and this game. No intervening deck edit is shown. Exact QR20 slots verified locally; prepared entry is not a claim of live saving.','conflicts_with_filmed_cards':[],'exact_list_status':'filmed_QR_exact20_verified; live_log_snapshot_unavailable_for_this_new_variant','deck_entity_id':deck['id'],'QR_payload':deck['deck_code'],'limits':['Frozen nine live lists did not contain this filmed variant; root prepared this new entry separately. External saved/reloaded deck snapshot is not yet supplied to worker.','QR identifies semantic card entities, not artwork/rarity.','Keep separate from032857 revision: this list has one Tinkaton ex and one Team Rocket\'s Tinkaton.']})
write('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':sources,'turns':turns,'limits':turn_limits})
write('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':sources,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'fixed_grid_is_turn_start_evidence':False},'frames':list(frames.values()),'discard_snapshots':discards,'scheduled_capture_limits':['Every owner turn retains three draw-relative candidates and chosen intact hand, including denser preplay captures where first input precedes+1s.','Candidates at turns2,4,6,12 after first play are explicitly unsuitable for the intact starting hand.','Attacks end owner turns; pre-attack hands substitute for End Turn.','Native bottom fifth truncates upper card names on this layout; full frames retain names. Crops preserve native pixels and are not enlarged overviews.','No full discard pile view is filmed.']})
limits=turn_limits+['Exact human queue/ranked mode is not shown. Human matchmaking is established; no Auto control/option appears in inspected source.','Exact new-variant live Pause Games list not supplied; separate exact20 filmed QR retained.','Original five-card opening and all owner hand identities/draws are captured.']
write('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'review_date':now,'sources':sources,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':deck['deck_name'],'filmed_deck_label':'New deck6','opening':{'source_video':video,'timestamp_seconds':28,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':hand([CORE,POP,TR,POP,RES],28)['cards_left_to_right'],'selected_active':{'name':TR,'opening_position':3,'source_video':video,'timestamp_seconds':30,'evidence_ids':ev(30)},'redraw_or_replacement':'none shown','before_active_placement':True,'status':'observed_complete','evidence_ids':ev(28,30),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'first_pass_full_battle_review_complete_pending_independent_acceptance','outcome':{'owner':'loss','owner_points':0,'opponent_points':3,'turns_played':13,'opponent':'犬いぬ','evidence_ids':ev(463,465,467,471,476)},'limits':limits,'lead_checked':False})
write('SUMMARY.json',{'game_id':gid,'source_video':video,'source_sha256':sha,'reviewer':'/root/pause_032023','model':'gpt-6.1-sol','reasoning_effort':'high','reviewed_utc':now,'scope':'Complete first pass of whole480.65-second recording; one game, setup through result and postgame overlay.','review_status':'first_pass_full_battle_review_complete_pending_independent_acceptance','capture_status':'complete_with_recording_limits','match_date_local':metadata['match_date_local'],'recording_time_local':metadata['recording_time_america_chicago'],'classification':'human_matchmaking','queue':None,'auto_control_observed':False,'owner':'Dacz8976','opponent':'犬いぬ','went':'second','outcome':'loss','points':{'owner':0,'opponent':3},'turns':13,'damage_done_result_screen':180,'visible_opponent_core':['Finizen / Palafin [Jet Punch]','Wiglett / Wugtrio ex [Pop Out Throughout]','Manaphy [Oceanic Gift]','Comfey [Flower Shield]'],'deck':deck['deck_name'],'external_eligible':True,'external_write_performed':False,'source_move_performed':False,'independent_check_timestamps_seconds':[28,66.6,67,71,72,73,76,103,105,110,189,285,308,320.3,331,339.7,387,389,401,402,427,429,435,437,462,463,465,467,476],'limits':limits})
write('UNCERTAINTIES.json',{'source_video':video,'source_sha256':sha,'items':[{'id':'U1','severity':'recording_limit','topic':'Opponent hand identities','interval_seconds':[44,469],'finding':'Hidden card backs do not establish names. Normal/search identities remain null unless revealed.'},{'id':'U2','severity':'recording_limit','topic':'Random selection order','interval_seconds':[283,287],'finding':'Aggregate50 and100 shown on two Honedge; individual three target-selection order hidden.'},{'id':'U3','severity':'recording_limit','topic':'Random selection order','interval_seconds':[386,387],'finding':'Aggregate0 to Active and50 to each Bench shown simultaneously; do not invent individual ordering.'},{'id':'U4','severity':'recording_limit','topic':'Discard views','interval_seconds':[0,480.65],'finding':'No full pile opened; top previews and play-derived events only.'},{'id':'U5','severity':'provenance_limit','topic':'Exact live list','finding':'Exact20 local filmed QR is available; new deck prepared but external saved/reloaded list is not supplied to worker.'},{'id':'U6','severity':'recording_limit','topic':'Queue','finding':'Human opponent found and postgame thanks option; exact ranked/private/casual queue label not shown.'},{'id':'U7','severity':'recording_limit','topic':'Random final selection order','interval_seconds':[460,465],'finding':'0 Active and50 to each Bench resolve together. Both Bench are0 at463; removal at464-465; three points separate467.'}],'consequential_ambiguities_needing_astra':[]})
text='''# Complete first-pass review: 20261005_032023000_iOS.MP4

Reviewer: /root/pause_032023, gpt-6.1-sol, high. Whole source:0.00-480.65 seconds. Source SHA-256:6fadd948b5526f22007c2ca2b11516c27801c2fbf2af57c290b214f9327f36a9. First pass awaits independent lead acceptance. No shared index/event writes, external writes or media moves were performed.

One human matchmaking game. Owner Dacz8976 went second against 犬いぬ. No Auto option/control is shown. Exact queue is unestablished. Embedded UTC creation time resolves to October4,2026,22:20:23 America/Chicago. The filename clock is not treated as the local match date.

Outcome: owner loss0-3 on turn13. Wugtrio ex knocks out both10HP benched Team Rocket's Tinkatink; native462 shows0 damage to protected Aegislash and50 to each Bench,463 shows both Bench0HP,465 shows both removed,467-468 awards two points to reach3,471 shows Defeat,476 confirms13 turns,0-3 and180 damage done. No concession or connection-error reason is inferred.

## Setup and filmed deck

The retained native QR at1s decodes20 cards with Metal Energy. At2.5s the editor reads New deck6;4s selects New deck6,6s searches for an opponent,12s shows the opponent profile,24s resolves going second. This source preserves the version with one Tinkaton ex and one Team Rocket's Tinkaton. It differs from the032857 revision with two Team Rocket's Tinkaton and no Tinkaton ex. QR evidence and prepared batch definition are exact local deck provenance, but do not claim the new entry has been saved live. DECK_USED.json preserves that distinction.

At28s, before Active placement, opening left to right is Metal Core Barrier, Lucky Ice Pop, Team Rocket's Tinkatink, Lucky Ice Pop, Professor's Research. Team Rocket's Tinkatink, third slot, is chosen as Active by30s. No setup Bench or redraw is shown. The opponent begins with Active Finizen and Wiglett in Bench3. Manaphy is benched later in turn1.

## Every recorded turn

The exact numbered voluntary actions and both boards are in TURN_LEDGER.json. Opponent card inputs are offscreen, so their times below describe observable reveals/resolutions rather than falsely asserting input times.

| Turn | Player | Source seconds | Full account | Owner hand end |
|---|---|---|---|---|
|1|Opponent|46-64|Poke Ball reveal49; search is an unrevealed back51. Manaphy50 to Bench1 by54. Giant Cape on Finizen59-63 raises effective HP60->80. Ends without Energy or attack.|4 unchanged|
|2|Owner|64-93|Normal draw Aegislash with Superb Shield65.5-66.6. Play1 Research67, revealing Poke Ball71 then Honedge72. Play2 Poke Ball73, reveals TR Tinkatink76. Play3 benches TR Tinkatink77-78 in Bench2. Play4 Metal to Active79-81. Play5 benches Honedge82-84 in Bench1. Play6 Lunge Out89-91 for20, Finizen80->60.|4|
|3|Opponent|93-113|Wiglett evolves to Wugtrio ex103-105. Water to Finizen105-108. Razor Fin110-111 for20, owner Active60->40.|4 unchanged|
|4|Owner|113-137|Normal Honedge115. First play benches it116.8-117 in Bench3. Lucky Ice Pop121-128 heals40->60; heads returns it. Metal to Bench1 Honedge130-131. Lunge Out133-135 for20, Finizen60->40.|4|
|5|Opponent|137-180|Water to Bench3 Wugtrio ex by152.5. Lucky Ice Pop155-162 heals Finizen40->60, heads returns. Second play165-172 heals60->80, tails discards. Razor Fin177-179 for20, owner Active60->40.|4 unchanged|
|6|Owner|180-208|Normal Poke Ball182-183.2. Play1 Poke Ball186-189 fails visibly: no cards in deck can be target. Play2 Lucky Ice Pop191-197 heals40->60; heads returns. Play3 Metal to Bench1 Honedge199-201, now2. Play4 Lunge Out203-207 for20, Finizen80->60.|4|
|7|Opponent|208-239|X Speed221-223 reduces retreat cost. Finizen retreats for0 at228; Manaphy becomes Active, Finizen retains1 Water. Water to Manaphy230-231. Oceanic Gift235-237 gives one Water each to Bench Finizen and Wugtrio ex, both now2.|4 unchanged|
|8|Owner|239-257|Normal TR Tinkaton241-241.8. Metal to Bench2 TR Tinkatink249-250. Lunge Out251-256 for20, Manaphy50->30.|5|
|9|Opponent|257-292|Manaphy retreats275-276, paying its1 Water, Wugtrio ex promoted. Water attachment278-280 makes3. Pop Out Throughout283-285 resolves50 to Bench1 Honedge and100 to Bench3 Honedge. Left Honedge60->10, right60->0. Right removed287, +1 point290. Individual random choice order hidden.|5 unchanged|
|10|Owner|292-356|Normal Cursed Metal Aegislash294-294.8. Retreat308-312 pays Active TR's1 Metal, promotes10HP Honedge with2 Metal; TR moves to Bench1. Three Lucky Ice Pop plays314-320.3(tails,10->30),322-331(heads,30->50),332-339.7(tails,50->60). Metal Core Barrier343-348 to Honedge. Metal351-352 to Bench2 TR, now2. Pierce353-355 for20, Wugtrio140->120.|3|
|11|Opponent|356-394|Bench Comfey70 at363; conditional Flower Shield banner, no Psychic Energy visible. Water to Manaphy383. Pop Out Throughout386-387 resolves0 to Honedge under Barrier and50 to each TR Bench, both60->10. Barrier discard resolves389-391. Individual random order hidden.|3 unchanged|
|12|Owner|394-445|Normal Research396-397.5. Research input398; reveals Rare Candy401 then Tinkaton ex402. Rare Candy input411; inspects Superb Shield Aegislash415, TR Tinkaton423-425, then Tinkaton ex427 with Unable to evolve429. Returns to Aegislash and evolves Active Honedge433-435, HP140. Metal437 to Active, now3. Superb Shield439-443 deals80, Wugtrio120->40, grants next-turn -80 against ex attacks.|3|
|13|Opponent|445-471|Bench Finizen evolves into Palafin451-453, full effective HP130 including Cape. Water455 makes3. Pop Out Throughout460-462 resolves0 to Aegislash under Superb Shield and50 to each10HP TR Bench. Both0HP463, both removed464-465. +2 points467-468 reaches3; Defeat471.|3 unchanged|

## Capture and count reconciliation

Opening five retained at28. Every owner turn has native draw-relative candidates and an inspected intact preplay view. Scheduled candidates after an immediate first play are marked unsuitable, with denser preplay captures at turns2,4 and12. Ending hand views are last pre-attack substitutions, with resolved boards retained separately. Opponent fan counts at the six owner starts are2,2,2,2,3,3.

Owner arithmetic: turn2 begins5, Research-1+2=6, Poke Ball-1+1=6, two benches-2=4. Turn4 begins5, benches-1=4, returned Ice Pop net0, ends4. Turn6 begins5, failed Ball-1=4, returned Ice Pop net0, ends4. Turn8 begins5 and only Energy/attack, ends5. Turn10 begins6, retreat net0, tails/head/tails Ice Pop net-2=4, Barrier-1=3. Turn12 begins4, Research-1+2=5, Rare Candy plus evolved Aegislash consume2, ends3. These counts agree with the direct fans. Exact hand names are visually evidenced, not deduced from the QR.

Damage/points reconcile: owner Lunge Out four times20 plus Pierce20 plus Superb Shield80 totals180, matching result. Opponent scores1 from right Honedge turn9, then2 from the two TR Tinkatink turn13. Active damage reduction does not protect those Bench.

## Limits and independent checks

No full discard pile is opened. Retained top previews are labeled as top-only; a play-derived history does not replace them. Hidden opponent normal/search cards remain unnamed, including turn1 Poke Ball's returned card back. Random target-selection order is unexposed, although resolved targets/damage are clear. Exact queue label and live saved20-card new-variant log snapshot remain unavailable to worker. Seek times are source-local requested seconds, not measured frame PTS.

Suggested independent checks: opening28-30; ordinary owner first decision66.6-77 and Research reveal order71-72; ordinary opponent development103-112; failed Poke Ball186-189; turn9 KO285-291; turn10 coins320.3/331/339.7 and ending hand351; Barrier387-391; Research401-402 and invalid Tinkaton ex427-429; final evolution435, Energy437, attack443; terminal462-476. No consequential ambiguity remains requiring Astra after bounded inspection.
'''
(p/'REVIEW.md').write_text(text,encoding='utf-8')
coverage='# Source coverage and completion checklist\n\nWhole source0-480.65s inspected: setup/QR/deck continuity0-6, matchmaking6-24, opening/setup24-46, all13 turns46-471, result/postgame471-480.65. Four-second locating frames were followed by denser native seeks around every action, reveal, coin, retreat, evolution and terminal consequence. Sparse locating sheets are not treated as turn-hand evidence.\n\n'
for row in turns:coverage+=f"- [x] Turn{row['turn_number']} {row['who_played']}: displayed label{banner[row['turn_number']]}s, starting board{start_frame[row['turn_number']]}s, resolved board{end_frame[row['turn_number']]}s; all numbered actions and observed effects reconciled.\n"
coverage+='\n- [x] All5 opening cards and selected Active.\n- [x] All6 normal owner draws; Research2-card order on both uses; successful Poke Ball reveal and failed Ball no-effect play.\n- [x] All6 owner hands retain3 draw-relative candidates, selected preplay native frame, before-attack hand and native crops.\n- [x] Both boards, positions, HP/max/damage, typed Energy, Tools, conditions, effects, points and both Energy Zones.\n- [x] Opponent native top fan counts2,2,2,2,3,3.\n- [x] Terminal pre-removal0HP, post-removal board and separately awarded points.\n- [x] Exact20 filmed QR version; missing live new-variant saved snapshot is explicit.\n- [x] Full discard pile views absent throughout; top-only previews retained.\n- [x] UTF-8 JSON/file references/crop bounds/hand arithmetic structural receipt.\n- [ ] Independent lead acceptance and shared/external registration: lead-only, not worker work.\n\nFirst-pass review complete, capture complete_with_recording_limits; independent acceptance pending.\n'
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
# Structural checks do not assert independent factual acceptance.
assert len(turns)==13 and [r['turn_number'] for r in turns]==list(range(1,14))
assert len(deck['card_slots'])==20 and sum(x['count'] for x in deck['cards_in_display_order'])==20
assert [turns[n-1]['owner_hand_end']['count'] for n in selected]==[4,4,4,5,3,3]
for k in allrefs(turns):assert k in frames,k
for f in frames.values():
    for path in [f['full_frame_path'],f['bottom_crop']['path'],f['top_crop']['path']]:assert (p/path).exists(),path
write('CONSISTENCY_RECEIPT.json',{'checked_utc':now,'source_video':video,'source_sha256':sha,'checks':{'turn_rows':13,'owner_turn_rows':6,'opening_slots':5,'owner_hand_end_counts':[4,4,4,5,3,3],'draw_relative_candidates':18,'native_frame_entries':len(frames),'all_references_exist':True,'native_dimensions':[1170,2532],'bottom_bounds':[0,2025,1170,2532],'top_bounds':[0,0,1170,770],'QR_slots':20,'QR_count_sum':20,'owner_damage_sum':180,'point_progression':[0,1,3],'parsed_unicode_preserved':True},'independent_acceptance':False,'limit':'Structural/self consistency only; lead must independently inspect evidence.'})
print(json.dumps({'packet':str(p),'turns':13,'frames':len(frames),'status':'first_pass_complete_pending_independent_acceptance'},ensure_ascii=True))
