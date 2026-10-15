import json,copy
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
p=Path(__file__).parent
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
video=src['video_basename']; sha=src['sha256']; game='20261010_014541000_iOS_game1'
sources=[{'video_basename':video,'sha256':sha,'source_json':'SOURCE.json'}]
def write(name,obj):
    (p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):
    # Evidence IDs identify an actual retained seek, not a fabricated frame.
    f=p/'turn_evidence'/f't{t:07.2f}.jpg'
    if not f.exists():
        vals=[float(x.stem[1:]) for x in (p/'turn_evidence').glob('t*.jpg') if not x.stem.endswith(('_bottom','_top'))]
        t=min(vals,key=lambda x:abs(x-t))
    return 'f_'+f'{t:07.2f}'
def cardnames(names,t):
    return [{'position':i+1,'name':n,'variant':None,'basis':'Visible source hand or individual draw reveal, not deck inference','evidence_ids':[eid(t)],'limit_reason':None} for i,n in enumerate(names)]
def hand(names,t,basis='Visible unzoomed fan'):
    return {'cards_left_to_right':cardnames(names,t),'count':len(names),'basis':basis,'evidence_ids':[eid(t)],'status':'observed','limit_reason':None}
def hidden_hand(count,t):
    return {'cards_left_to_right':[{'position':i+1,'name':None,'variant':None,'basis':'Visible card back','evidence_ids':[eid(t)],'limit_reason':'Opponent card identity hidden'} for i in range(count)],'count':count,'basis':'Visible fan; identities hidden','evidence_ids':[eid(t)],'status':'observed_count_hidden_identities','limit_reason':'Opponent card identities hidden'}
def mon(name,hp,mx,en=0,pos=None,tool='none',conditions=None,effects=None):
    return {'name':name,'variant':{'Horsea':'50 HP / Hook 30',"Team Rocket's Koffing":'60 HP / Reverse Thrust 10','Kingdra ex':'170 HP / Stormy Prison 90',"Team Rocket's Weezing ex":'140 HP / Boiler Smog / Confusion Gas 60','Feebas':'30 HP / Splash 10','Carvanha':'50 HP / Sharp Fang 20','Mega Sharpedo ex':'190 printed HP / Turbo Shark 70','Suicune ex':'140 HP / Legendary Pulse / Crystal Waltz 20x','Milotic':'120 HP / Healing Ripples'}.get(name),
    'bench_position':pos,'hp_now':hp,'hp_max':mx,'hp_max_basis':'Visible printed HP and established Tool modifier','damage':mx-hp,'attached_energy':{'total':en,'by_type':{'Water':en} if en else {}},'tool':tool,'special_conditions':conditions or [],'active_effects':effects or [],'evidence_ids':[],'status':'observed','limit_reason':None}
H=lambda en=0,pos=None:mon('Horsea',50,50,en,pos)
K=lambda hp=50,pos=1,tool='Small Balloon':mon("Team Rocket's Koffing",hp,60,0,pos,tool)
G=lambda hp,en:mon('Kingdra ex',hp,170,en)
W=lambda hp,en=1:mon("Team Rocket's Weezing ex",hp,140,en,None,'Small Balloon')
F=lambda pos=None,en=0:mon('Feebas',30,30,en,pos)
C=lambda pos=None:mon('Carvanha',50,50,0,pos)
S=lambda hp,en=1,cape=False,pos=None,conds=None,lock=False:mon('Mega Sharpedo ex',hp,220 if cape else 190,en,pos,'Elegant Cape' if cape else 'none',conds,[{'name':'Cannot retreat','source':'Kingdra ex Stormy Prison','affected_pokemon':'Mega Sharpedo ex','expiry':'End of opponent next turn'}] if lock else [])
U=lambda en=1,pos=1:mon('Suicune ex',140,140,en,pos)
M=lambda en=1,pos=2:mon('Milotic',120,120,en,pos)
def zone(this,next_visible=True):
    return {'this_turn':{'type':'Water' if this else None,'count':1 if this else 0,'available':bool(this)},'next':{'type':'Water' if next_visible else None,'count':1 if next_visible else None,'available':None},'basis':'Visible current circle and next Water icon; next icon is type preview, not a claim of current usable Energy','evidence_ids':[],'limit_reason':'Future availability is not established by a next-type preview'}
def board(turn,phase,oa,ob,pa,pb,op,pp,stadium,oz,pz,t):
    b={'turn_number_displayed':turn,'phase':phase,'stadium':stadium,'owner':{'active':copy.deepcopy(oa),'bench_in_position_order':copy.deepcopy(ob),'energy_zone':zone(oz),'points':op,'board_effects':[],'evidence_ids':[eid(t)],'status':'observed','limit_reason':None},'opponent':{'active':copy.deepcopy(pa),'bench_in_position_order':copy.deepcopy(pb),'energy_zone':zone(pz),'points':pp,'board_effects':[],'evidence_ids':[eid(t)],'status':'observed','limit_reason':None},'shared_effects':[],'evidence_ids':[eid(t)]}
    for who in ['owner','opponent']:
        b[who]['energy_zone']['evidence_ids']=[eid(t)]
        for m in [b[who]['active']]+b[who]['bench_in_position_order']:
            if m: m['evidence_ids']=[eid(t)]
    return b
# At turn boundaries, unused current Energy can remain in its circle until transition.
# The next-icon count is one visible preview symbol, never a hidden generated-energy inference.
start=[
 board(1,'After normal draw, before first play',H(),[K(60)],F(),[],0,0,'none',False,False,56),
 board(2,'After opponent normal draw',H(),[K(60)],F(),[],0,0,'Hiking Trail',False,True,74),
 board(3,'After normal draw',K(50,None),[H(pos=1)],F(en=1),[C(2)],0,0,'Soothing Shore',True,False,126.5),
 board(4,'After opponent normal draw',G(170,1),[K(),H(pos=2)],C(),[F(2,1)],0,0,'Soothing Shore',False,True,172),
 board(5,'After normal draw',G(100,1),[K(),H(pos=2)],S(190),[U(1),F(2,1)],0,0,'Soothing Shore',True,False,206.5),
 board(6,'After opponent normal draw',G(120,2),[K(),H(pos=2)],S(100,lock=True),[U(1),F(2,1)],0,0,'Soothing Shore',False,True,225),
 board(7,'After normal draw',G(50,2),[K(),H(pos=2)],S(180),[U(2),M(2)],0,0,'Soothing Shore',True,False,260),
 board(8,'After opponent normal draw',G(70,2),[K(),H(1,2)],S(90,lock=True),[U(2),M(2)],0,0,'Soothing Shore',False,True,294),
 board(9,'After normal draw',H(1),[K()],S(140,cape=True),[U(4),M(2)],0,2,'Soothing Shore',True,False,351),
 board(10,'After opponent normal draw and checkup',W(140),[H(pos=1)],S(110,cape=True,conds=['Poisoned']),[U(4),M(2)],0,2,'Soothing Shore',False,True,396),
 board(11,'After normal draw',W(80),[H(pos=1)],U(4,None),[S(130,1,True,1),M(3)],0,2,'Soothing Shore',True,False,434),
 board(12,'After opponent normal draw',W(100),[H(1,1),K(60,3,'Elegant Cape')],U(4,None),[S(130,1,True,1),M(3)],0,2,'Soothing Shore',False,True,456)
]
end=[
 board(1,'After End Turn and Hiking Trail draw',H(),[K(60)],F(),[],0,0,'Hiking Trail',False,False,70),
 board(2,'After Splash resolves',K(50,None),[H(pos=1)],F(en=1),[C(2)],0,0,'Soothing Shore',False,False,122),
 board(3,'After manual End Turn',G(170,1),[K(),H(pos=2)],C(),[F(2,1)],0,0,'Soothing Shore',False,False,166),
 board(4,'After Turbo Shark and extra Energy resolve',G(100,1),[K(),H(pos=2)],S(190),[U(1),F(2,1)],0,0,'Soothing Shore',False,False,203),
 board(5,'After Stormy Prison and Soothing Shore',G(120,2),[K(),H(pos=2)],S(100,lock=True),[U(1),F(2,1)],0,0,'Soothing Shore',False,False,219),
 board(6,'After attack, extra Energy and Soothing Shore',G(50,2),[K(),H(pos=2)],S(180),[U(2),M(2)],0,0,'Soothing Shore',False,False,256),
 board(7,'After Stormy Prison and Soothing Shore',G(70,2),[K(),H(1,2)],S(90,lock=True),[U(2),M(2)],0,0,'Soothing Shore',False,False,289),
 board(8,'After Kingdra knockout, replacement and Shore',H(1),[K()],S(140,cape=True),[U(4),M(2)],0,2,'Soothing Shore',False,False,346),
 board(9,'After End Turn, Shore, Poison/Burn damage and Burn recovery',W(140),[H(pos=1)],S(110,cape=True,conds=['Poisoned']),[U(4),M(2)],0,2,'Soothing Shore',False,False,393),
 board(10,'After Crystal Waltz, Legendary Pulse and Shore',W(80),[H(pos=1)],U(4,None),[S(130,1,True,1),M(3)],0,2,'Soothing Shore',False,False,429),
 board(11,'After manual End Turn and Shore',W(100),[H(1,1),K(60,3,'Elegant Cape')],U(4,None),[S(130,1,True,1),M(3)],0,2,'Soothing Shore',False,False,451),
 board(12,'Terminal knockout frame; winning point display follows',W(0),[H(1,1),K(60,3,'Elegant Cape')],U(4,None),[S(170,1,True,1),M(4),F(3)],0,3,'Soothing Shore',False,False,486)
]
def play(order,kind,name,t,target,result,en=None,nested=None,limit=None):
    return {'order':order,'kind':kind,'card_name':name,'target':target,'energy':en,'result':result,'prompt_text':None,'response':None,'nested_events_in_order':nested or [],'hand_count_after':None,'source_video':video,'timestamp_seconds':t,'evidence_ids':[eid(t)],'basis':'Observed source animation and resulting state','limit_reason':limit}
def energy(dest): return {'type':'Water','count':1,'destination':dest,'retreat_payment_by_type':None}
plays=[
 [play(1,'card_play','Small Balloon',58,'Team Rocket\'s Koffing','Tool attaches; visible retreat reduction'),play(2,'card_play','Hiking Trail',65,'Stadium','Stadium becomes Hiking Trail'),play(3,'end_turn',None,67,None,'Manual turn end')],
 [play(1,'card_play','Soothing Shore',79,'Stadium','Replaces Hiking Trail'),play(2,'card_play','Poké Ball',85,None,'Search adds a hidden Basic; Carvanha subsequently revealed'),play(3,'card_play','Carvanha',92,'Bench position 2','Carvanha benched'),play(4,'card_play','Sabrina',106,'Owner Active','Owner chooses Koffing to replace Horsea'),play(5,'energy_attachment',None,114,'Feebas','One Water attached',energy('Feebas')),play(6,'attack','Feebas',120,"Team Rocket's Koffing",'Splash 10; Koffing 60→50')],
 [play(1,'card_play','Poké Ball',128.5,None,'Search finds Horsea'),play(2,'card_play','Horsea',137,'Bench position 2','Second Horsea benched'),play(3,'card_play','Rare Candy',143,'Original Horsea, Bench position 1','Evolves original Horsea directly into Kingdra ex; consumes Rare Candy and Kingdra ex'),play(4,'card_play','Sabrina',153,'Opponent Feebas','Feebas moves to Bench position 2; Carvanha becomes Active'),play(5,'retreat',None,161,"Team Rocket's Koffing → Kingdra ex",'Free retreat with Small Balloon; no Energy discarded',{'type':None,'count':0,'destination':'Kingdra ex','retreat_payment_by_type':{}}),play(6,'energy_attachment',None,164,'Kingdra ex','First Water attached',energy('Kingdra ex')),play(7,'end_turn',None,166,None,'Manual turn end; Kingdra has only one Water')],
 [play(1,'card_play','Suicune ex',176,'Bench position 1','Suicune ex benched'),play(2,'card_play','Mega Sharpedo ex',180,'Carvanha Active','Carvanha evolves directly into Mega Sharpedo ex'),play(3,'energy_attachment',None,185,'Mega Sharpedo ex','One Water attached',energy('Mega Sharpedo ex')),play(4,'attack','Mega Sharpedo ex',192,'Kingdra ex','Turbo Shark 70; Kingdra 170→100',nested=[{'order':1,'event':'Take a Water Energy from Energy Zone and attach to benched Suicune ex','timestamp_seconds':196,'evidence_ids':[eid(195)]}])],
 [play(1,'energy_attachment',None,208.5,'Kingdra ex','Second Water attached',energy('Kingdra ex')),play(2,'attack','Kingdra ex',211.5,'Mega Sharpedo ex','Stormy Prison 90; Sharpedo 190→100; cannot retreat during next opponent turn')],
 [play(1,'card_play','Milotic',230,'Benched Feebas position 2','Feebas evolves into Milotic; Healing Ripples offered/used',nested=[{'order':1,'event':'Healing Ripples heals Mega Sharpedo ex by60,100→160','timestamp_seconds':237,'evidence_ids':[eid(237)]}]),play(2,'energy_attachment',None,240,'Suicune ex','Suicune Water1→2',energy('Suicune ex')),play(3,'attack','Mega Sharpedo ex',246,'Kingdra ex','Turbo Shark70; Kingdra120→50',nested=[{'order':1,'event':'Extra Water attached to benched Milotic,1→2','timestamp_seconds':249,'evidence_ids':[eid(249)]}])],
 [play(1,'card_play',"Professor's Research",262,None,'Draws Elegant Cape then Soothing Shore'),play(2,'energy_attachment',None,267,'Benched Horsea position2','First Water attached',energy('Horsea')),play(3,'attack','Kingdra ex',282,'Mega Sharpedo ex','Stormy Prison90; Sharpedo180→90; next-turn retreat blocked')],
 [play(1,'card_play','Elegant Cape',306,'Mega Sharpedo ex','Stage1 Tool raises effective maximum HP190→220 and current HP90→120'),play(2,'energy_attachment',None,315,'Suicune ex','Suicune Water2→3',energy('Suicune ex')),play(3,'attack','Mega Sharpedo ex',324,'Kingdra ex','Turbo Shark70 KOs Kingdra70HP; opponent earns2points',nested=[{'order':1,'event':'Extra Water attached to benched Suicune ex,3→4','timestamp_seconds':339,'evidence_ids':[eid(339)]},{'order':2,'event':'Owner selects Horsea as replacement Active','timestamp_seconds':342,'evidence_ids':[eid(342)]}])],
 [play(1,'card_play',"Team Rocket's Weezing ex",353,"Team Rocket's Koffing, Bench position1",'Evolution carries10damage: Weezing130/140',nested=[{'order':1,'event':'Boiler Smog prompt accepted Yes; opposing Mega Sharpedo ex becomes Poisoned and Burned','timestamp_seconds':357,'evidence_ids':[eid(357),eid(360)]}]),play(2,'retreat',None,371,'Horsea → Team Rocket\'s Weezing ex','Horsea retreats; one Water discarded; Weezing becomes Active',{'type':'Water','count':1,'destination':"Team Rocket's Weezing ex",'retreat_payment_by_type':{'Water':1}}),play(3,'energy_attachment',None,378,"Team Rocket's Weezing ex",'First Water attached',energy("Team Rocket's Weezing ex")),play(4,'end_turn',None,380,None,'Manual end; no Weezing attack')],
 [play(1,'energy_attachment',None,402,'Milotic','Milotic Water2→3',energy('Milotic')),play(2,'retreat',None,414,'Mega Sharpedo ex → Suicune ex','Free retreat; one attached Water retained; Sharpedo leaves Active and Poison clears',{'type':None,'count':0,'destination':'Suicune ex','retreat_payment_by_type':{}}),play(3,'attack','Suicune ex',423,"Team Rocket's Weezing ex",'Crystal Waltz60 from three total Benched Pokémon; Weezing140→80')],
 [play(1,'card_play',"Team Rocket's Koffing",436,'Bench position3','Second Koffing benched at60HP'),play(2,'card_play','Elegant Cape',439,"Team Rocket's Koffing, Bench position3",'Tool attaches to Basic Koffing; displayed60HP unchanged; its Stage1 HP benefit does not apply'),play(3,'energy_attachment',None,444,'Horsea, Bench position1','First Water attached after prior retreat discarded its previous Energy',energy('Horsea')),play(4,'end_turn',None,448,None,'Manual end; no attack')],
 [play(1,'energy_attachment',None,460,'Milotic','Milotic Water3→4',energy('Milotic')),play(2,'card_play','Feebas',471,'Bench position3','Second Feebas benched'),play(3,'card_play','Irida',473.3,'All own Pokémon with Water attached','Heals40 from each eligible Pokémon; only damaged Sharpedo visibly changes130→170'),play(4,'attack','Suicune ex',483,"Team Rocket's Weezing ex",'Crystal Waltz100 from five total Benched Pokémon; Weezing100→0; terminal win for opponent')]
]
hands_start={1:['Sabrina','Small Balloon','Kingdra ex','Hiking Trail'],3:['Sabrina','Kingdra ex','Poké Ball','Rare Candy'],5:['Kingdra ex'],7:['Kingdra ex',"Professor's Research"],9:['Kingdra ex','Elegant Cape','Soothing Shore',"Team Rocket's Weezing ex"],11:['Kingdra ex','Elegant Cape','Soothing Shore',"Team Rocket's Koffing"]}
hands_end={1:['Sabrina','Kingdra ex'],3:[],5:['Kingdra ex'],7:['Kingdra ex','Elegant Cape','Soothing Shore'],9:['Kingdra ex','Elegant Cape','Soothing Shore'],11:['Kingdra ex','Soothing Shore']}
starthandtime={1:56,3:126.5,5:206.5,7:260,9:351,11:434}
endhandtime={1:67,3:165,5:209,7:277,9:380,11:447}
oppcount={1:4,3:2,5:1,7:1,9:1,11:3}
opstartcount={2:5,4:3,6:2,8:2,10:2,12:4}
drawend={1:55,3:125.5,5:205.5,7:259,9:350,11:433}
first={1:58,2:79,3:128.5,4:176,5:208.5,6:230,7:262,8:306,9:353,10:396,11:436,12:460}
resolved={1:72,2:123,3:167,4:204,5:220,6:256,7:290,8:348,9:394,10:431,11:452,12:501}
normal={1:('Hiking Trail',54),3:('Rare Candy',124),5:('Kingdra ex',205),7:("Professor's Research",258),9:("Team Rocket's Weezing ex",350),11:("Team Rocket's Koffing",433)}
def draw(kind,cause,names,ts,order=None):
    return {'kind':kind,'caused_by':cause,'linked_play_order':order,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':video,'timestamp_seconds':t,'evidence_ids':[eid(t)],'basis':'Visible card reveal' if n else 'Hidden opponent draw','limit_reason':None if n else 'Card face hidden'} for i,(n,t) in enumerate(zip(names,ts))],'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':[],'source_video':video,'timestamp_seconds':ts[0],'evidence_ids':[eid(t) for t in ts],'limit_reason':None}
automatic={
1:[{'event':'Hiking Trail draws Poké Ball, filling hand2→3','time':70}],
2:[],3:[],4:[],
5:[{'event':'Soothing Shore heals Kingdra20,100→120','time':219}],
6:[{'event':'Soothing Shore heals Sharpedo20,160→180','time':254}],
7:[{'event':'Soothing Shore heals Kingdra20,50→70','time':289}],
8:[{'event':'Kingdra knockout earns opponent2points; Horsea chosen Active','time':336},{'event':'Soothing Shore heals Sharpedo20,120→140','time':346}],
9:[{'event':'Soothing Shore heals Weezing130→140, capped','time':384},{'event':'Poison10 and Burn20 deal30total to Sharpedo140→110','time':387},{'event':'Burn-recovery coin Heads; Burn clears, Poison remains','time':393}],
10:[{'event':'Suicune Legendary Pulse draws one hidden card at end of its turn','time':426},{'event':'Soothing Shore heals benched Sharpedo110→130; free retreat retained its Water','time':429}],
11:[{'event':'Soothing Shore heals Weezing80→100','time':451}],
12:[{'event':'Weezing knockout ends battle; capped winning display reaches3points','time':489},{'event':'Defeat vs Max Ketchum result shown','time':501}]
}
turns=[]
for n in range(1,13):
    own=n%2==1; st=starthandtime.get(n,74 if n==2 else {4:172,6:225,8:294,10:396,12:456}.get(n)); draws=[]
    if own:
        nm,t=normal[n]; draws.append(draw('normal_draw','Turn draw',[nm],[t]))
        if n==1: draws.append(draw('automatic_draw','Hiking Trail',['Poké Ball'],[70]))
        if n==3: draws.append(draw('search','Poké Ball',['Horsea'],[131.5],1))
        if n==7: draws.append(draw('supporter_draw',"Professor's Research",['Elegant Cape','Soothing Shore'],[264,265],1))
    else:
        draws.append(draw('normal_draw','Opponent turn draw',[None],[{2:73,4:168,6:222,8:291,10:395,12:453}[n]]))
        if n==2: draws.append(draw('search','Poké Ball',[None],[88],2)); draws[-1]['limit_reason']='Search result face hidden; subsequent Carvanha play is public, but is not falsely treated as a direct search reveal'
        if n==10: draws.append(draw('automatic_draw','Legendary Pulse',[None],[426]))
    turns.append({'turn_number':n,'who_played':'owner' if own else 'opponent','source_video':video,
      'timing':{'turn_start_seconds':{1:52,2:72,3:123,4:167,5:204,6:220,7:256,8:290,9:348,10:394,11:431,12:452}[n],'draw_animation_end_seconds':drawend.get(n),'first_voluntary_move_seconds':first[n],'before_end_action_seconds':endhandtime.get(n,plays[n-1][-1]['timestamp_seconds']),'end_after_resolution_seconds':resolved[n],'basis':'Source-local approximate timing from bounded seeks; draw-end uncertainty approximately0.5s'},
      'hand_at_start':hand(hands_start[n],st) if own else hidden_hand(opstartcount[n],st),
      'owner_hand_start':hand(hands_start[n],st) if own else {'cards_left_to_right':None,'count':None,'basis':'Owner is not acting this turn','evidence_ids':[eid(st)],'status':'not_applicable','limit_reason':'Required named start hand is captured on owner turns'},
      'opponent_hand_at_owner_turn_start':{'count':oppcount.get(n),'supported_range':None,'count_method':'Individually count visible card backs in native top crop','basis':'Directly observed fan' if own else 'Not an owner turn','evidence_ids':[eid(st)] if own else [],'limit_reason':None if own else 'Not applicable'},
      'draws_and_searches':draws,'plays_in_order':plays[n-1],'automatic_events_in_order':automatic[n],
      'board_at_start':start[n-1],'board_after':end[n-1],
      'owner_hand_end':hand(hands_end[n],endhandtime[n],'Before attack or manual end action; end draw accounted separately') if own else {'cards_left_to_right':None,'count':None,'basis':'Not an owner turn','evidence_ids':[],'status':'not_applicable','limit_reason':'See next owner hand observation'},
      'discard_snapshot_ids':[f'discard_not_shown_t{n}'],'turn_evidence_ids':[eid(st),eid(endhandtime.get(n,plays[n-1][-1]['timestamp_seconds'])),eid(end[n-1]['evidence_ids'][0].split('_',1)[1] and float(end[n-1]['evidence_ids'][0][2:]))],
      'limits':['No opened discard pile in this turn; public play history is distinct from a viewed pile','Opponent next Energy count/availability is not established by type preview','Hidden opponent card identities remain unknown']})
# End-of-turn hand is after all automatic additions, not only the before-action frame.
turns[0]['owner_hand_end']=hand(['Sabrina','Kingdra ex','Poké Ball'],70,'Observed after Hiking Trail automatic draw; before-end hand was2')
write('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':sources,'turns':turns,'limits':['Source-local times approximate; requested seek times differ from measured frame PTS','No opened discard piles','Exact deck20 unverified; no list or QR filmed in this source']})
frames=[]
selected=set(starthandtime.values())
native=p/'turn_evidence'
for f in sorted(native.glob('t*.jpg')):
    if f.stem.endswith(('_bottom','_top')): continue
    t=float(f.stem[1:]); ownturn=next((n for n,v in drawend.items() if abs(t-v-1)<.06 or abs(t-v-3)<.06 or abs(t-v-6)<.06),None)
    role='draw_candidate' if ownturn else 'native_action_or_board_evidence'
    if t in selected: role='selected_owner_start_hand'
    if t in endhandtime.values():role='before_end_action_hand'
    if t==39:role='opening_five_before_active'
    if t in [489,501,504]:role='terminal_result'
    # Crops are original pixels, independently retained, never enlarged overview frames.
    im=Image.open(f); im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_bottom.jpg'),quality=94); im.crop((0,0,1170,780)).save(f.with_name(f.stem+'_top.jpg'),quality=94)
    tn=ownturn or next((n for n,v in starthandtime.items() if t==v),None)
    frames.append({'evidence_id':eid(t),'role':role,'turn_number':tn,'who_played':'owner' if tn else None,'source_video':video,'source_sha256':sha,'draw_animation_end_seconds':drawend.get(tn),'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':t-drawend[tn] if tn in drawend else None,'full_frame_path':str(f.relative_to(p)).replace('\\','/'),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':str(f.with_name(f.stem+'_bottom.jpg').relative_to(p)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':str(f.with_name(f.stem+'_top.jpg').relative_to(p)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,780]},'selected_for_start_hand':t in selected,'before_first_play':t in selected,'unzoomed':True if t in selected else None,'hand_spread':True if t in selected else None,'observation':'Retained source-native frame; selected hand/board facts in TURN_LEDGER','suitability_or_limit':'Only selected pre-play hands establish turn-start fan; later candidates may show card play/zoom'})
write('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':sources,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':.2,'fixed_grid_is_turn_start_evidence':False},'frames':frames,'discard_snapshots':[{'snapshot_id':f'discard_not_shown_t{n}','turn_number':n,'pile_owner':'both','source_video':video,'timestamp_seconds':None,'cards_in_view':None,'scroll_coverage':'not shown','full_pile_established':False,'evidence_ids':[],'limit_reason':'Neither player\'s opened discard pile is shown anywhere in reviewed source'} for n in range(1,13)],'scheduled_capture_limits':['Later +3/+6 candidates commonly show actions; clearest pre-play candidate or denser earlier frame selected','Actual frame PTS was not measured; requested seek timestamp retained']})
opening=['Horsea',"Team Rocket's Koffing",'Sabrina','Small Balloon','Kingdra ex']
limits=['The named live snapshot has23decks but lacks this Kingdra/Team Rocket\'s Weezing deck; exact20-card game version unverified','No opened discard piles appear','Opponent draws/search faces hidden','Source-local draw-end estimates approximately0.5s; actual extracted-frame PTS not measured']
write('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'review_date':datetime.now(timezone.utc).isoformat(),'sources':sources,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':'Filmed selection: New deck13; visible Kingdra ex / Team Rocket\'s Weezing ex core','opening':{'source_video':video,'timestamp_seconds':39,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':cardnames(opening,39),'selected_active':{'name':'Horsea','opening_position':1,'source_video':video,'timestamp_seconds':43,'evidence_ids':[eid(39)]},'benched_during_setup':[{'name':"Team Rocket's Koffing",'opening_position':2,'bench_position':1,'timestamp_seconds':47}],'redraw_or_replacement':[],'before_active_placement':True,'status':'observed','evidence_ids':[eid(39)],'limit_reason':'Kingdra ex name partly clipped in opening frame; native55 subsequently confirms same retained card'},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'first_pass_complete_pending_independent_acceptance','outcome':{'owner':'loss','opponent':'Max Ketchum','method':'Knockouts; final Suicune ex attack','owner_points':0,'opponent_points_displayed':3,'terminal_turn':12,'evidence_ids':[eid(486),eid(489),eid(501)]},'limits':limits,'lead_checked':False})
write('DECK_USED.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':sources,'deck_name_in_log':None,'filmed_deck_label':'New deck13','source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','captured_at':'2026-10-10T03:20:04.384Z','log_list_version':'Shared LIVE_DECK_SNAPSHOT.json,23decks','expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':None,'energy_configuration_from_log':None,'energy_configuration_filmed':'Water only in inspected this/next Energy Zone previews','actual_card_count':None,'capture_source_text_or_image':'../LIVE_DECK_SNAPSHOT.json','game_version_binding_basis':'No matching named live deck; no QR or full list filmed in this source. Later015452QR can be candidate only, not proof of earlier game version.','conflicts_with_filmed_cards':None,'exact_list_status':'unverified_game_version_no_matching_current_live_deck','visible_cards_minimum_counts':{'Horsea':2,"Team Rocket's Koffing":2,'Kingdra ex':2,"Team Rocket's Weezing ex":1,'Sabrina':1,'Small Balloon':1,'Hiking Trail':1,'Poké Ball':1,'Rare Candy':1,"Professor's Research":1,'Elegant Cape':1,'Soothing Shore':1},'limits':limits})
summary={'reviewer':'/root/pause_014541','review_model':'gpt-6.1-sol','reasoning_effort':'high','game_id':game,'source_video':video,'source_sha256':sha,'source_duration_seconds':src['duration_seconds'],'creation_time_utc':src['creation_time_utc'],'creation_time_local':'2026-10-09T20:45:41-05:00','match_date_local':'2026-10-09','review_scope':'Entire supplied source, setup through terminal result; all12recorded turns','game_count':1,'turn_count':12,'mode':'human battle; no Auto control visible in inspected source','specific_queue':None,'opponent':'Max Ketchum','owner_result':'loss','owner_points':0,'opponent_points_displayed':3,'concession':False,'result_evidence':[{'seconds':324,'event':'Mega Sharpedo ex Turbo Shark70 KOs Kingdra ex'},{'seconds':336,'event':'Opponent2point award'},{'seconds':483,'event':'Suicune ex Crystal Waltz100 against Weezing ex100HP'},{'seconds':486,'event':'Weezing displayed0HP'},{'seconds':489,'event':'Opponent terminal3point display'},{'seconds':501,'event':'Defeat vs Max Ketchum'}],'deck_core':['Horsea','Kingdra ex',"Team Rocket's Koffing","Team Rocket's Weezing ex"],'opponent_core':['Feebas','Milotic','Carvanha','Mega Sharpedo ex','Suicune ex'],'deck_qr_in_source':False,'exact_deck20_verified':False,'first_pass_status':'complete_pending_independent_lead_acceptance','capture_status':'complete_with_recording_limits','external_writes_performed':False,'archive_moves_performed':False,'packet_files':['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']}
write('SUMMARY.json',summary)
write('UNCERTAINTIES.json',{'source_video':video,'source_sha256':sha,'recording_limits':[{'issue':'Exact20-card game deck version','evidence':'No matching current23deck live snapshot; filmed New deck13 selection only; later QR does not establish earlier continuity','status':'unresolved_version_binding'},{'issue':'Opened discard snapshots','evidence':'Neither pile opened in full source','status':'unavailable_from_recording'},{'issue':'Hidden opponent cards and exact print identifiers','evidence':'Card backs and small game views','status':'kept_unknown'},{'issue':'Specific queue type','evidence':'Human matchmaking seen, no specific ranked/private label retained','status':'unknown'}],'resolved_native_followups':[{'issue':'Turn12 healing card exact name','times':[473.3],'resolution':'Irida clearly named;40healing130→170'},{'issue':'Sharpedo retreat and Shore eligibility','times':[180,414,417,429],'resolution':'Visible printed retreat row has no cost; free retreat keeps one Water, matching Shore healing'}],'bounded_followup_checks':[]})
table=[]
for tr in turns:
    n=tr['turn_number']; act='; '.join(f"{x['order']}. {x['card_name'] or x['kind']}: {x['result']}" for x in tr['plays_in_order'])
    table.append(f"| {n} | {tr['who_played']} | {tr['timing']['turn_start_seconds']}–{resolved[n]} | {act} |")
review=f'''# Full recording review: {video}

Reviewer: /root/pause_014541, GPT-6.1 Sol, high. This is the complete first visual pass, pending independent lead acceptance. Source SHA-256: `{sha}`. Frozen identity in SOURCE.json. Recording duration504.478333seconds. Creation metadata2026-10-10T01:45:41Z, equivalent to October9,2026,20:45:41CDT. Match date is October9local.

One human battle is recorded against Max Ketchum. The opening shows online opponent search, and no Auto control appears in the reviewed gameplay. The specific queue type is not established. Dustin loses by knockouts: Mega Sharpedo ex KOs Kingdra ex on turn8 for two points; Suicune ex KOs Team Rocket's Weezing ex on turn12 to reach the capped three-point win display. The501second result reads Defeat vs Max Ketchum. No concession is shown.

## Setup and deck

0–36seconds covers filmed deck selection, opponent search, loading and coin/setup animation. The selected slot24 is New deck13. At39seconds the five opening cards, left to right, are Horsea, Team Rocket's Koffing, Sabrina, Small Balloon, Kingdra ex. Horsea is selected Active; Koffing goes to Bench position1. The Kingdra name is partly clipped in the opening fan but native55seconds confirms the retained card as Kingdra ex. Opponent opens Feebas30HP. No filmed QR/full deck list appears before or after this battle. The shared live23deck snapshot lacks a matching Kingdra/Weezing deck. The later015452QR is a candidate list, not proof of this earlier game's exact20-card version. DECK_USED.json keeps that limit explicit.

## Every recorded turn

This table is the readable counterpart of TURN_LEDGER.json. Rows contain ordered voluntary actions, and the JSON separately retains automatic effects, named draws/searches, hand counts, both boards and Energy Zones.

| Turn | Player | Source seconds | Ordered meaningful actions |
|---|---|---|---|
'''+ '\n'.join(table)+'''

## Draw and hand reconciliation

Owner turn1 draws Hiking Trail, begins with four cards after setup, plays Small Balloon then Hiking Trail, ends manually with two, and Hiking Trail draws Poké Ball to finish at three. Turn3 draws Rare Candy; Poké Ball finds a second Horsea, which is benched; Rare Candy plus Kingdra ex evolve the original Horsea; Sabrina is played, leaving zero cards. Turn5 draws the second Kingdra ex and keeps it, ending with one card. Turn7 draws Professor's Research, plays it, then reveals Elegant Cape followed by Soothing Shore; hand ends at three. Turn9 draws Team Rocket's Weezing ex and evolves Koffing; the three other cards stay in hand. Turn11 draws a second Koffing, benches it and attaches Elegant Cape, leaving Kingdra ex and Soothing Shore, two cards.

Directly counted opponent fan sizes at the six owner-turn starts are4,2,1,1,1,3. Native top crops retain each count. Opponent search/draw faces stay unknown. Turn2 Poké Ball's search result is face-down; Carvanha is subsequently publicly benched and is not falsely represented as a direct search reveal.

## Reconciled changes and decisions

Small Balloon attaches to Koffing on turn1 and enables its free retreat on turn3. Kingdra gets its first Water on turn3 and second on turn5. Its Stormy Prison attacks on turns5and7 each deal90 and apply the visible next-turn retreat block. Soothing Shore heals the owner's Kingdra by20 at each of those turn ends. Milotic's evolution Healing Ripples heals opposing Sharpedo60 on turn6, followed by Shore20. Elegant Cape attaches to Mega Sharpedo ex on turn8, increasing effective maximum190→220 and current90→120; Turbo Shark then KOs Kingdra70HP. Owner chooses the energized second Horsea as replacement.

Turn9 Weezing evolution carries Koffing's10damage and the owner accepts Boiler Smog Yes, poisoning and burning Sharpedo. Horsea pays one Water to retreat. A Water attaches to Weezing; the owner manually ends without an attack. Shore heals Weezing130→140. Poison10andBurn20 lower Sharpedo140→110, and the visible Burn-recovery coin clears Burn; Poison remains until Sharpedo retreats for free on turn10, retaining its Water. Suicune Crystal Waltz deals60 with three total Benched Pokémon. Legendary Pulse draws one opponent card; Shore heals Sharpedo on the Bench. Turn11 Cape attaches to Basic Koffing and its60HP does not increase, consistent with the visible Tool text requiring Stage1. The owner attaches Water to Horsea and manually ends, healing Weezing80→100. Turn12 adds Feebas to the opponent Bench, plays Irida to heal eligible Water-attached Pokémon40, visibly Sharpedo130→170, and Crystal Waltz deals100 with five total Benched Pokémon, exactly KOs Weezing100HP. Owner points remain zero.

The Cape inspection on turn7 is a card view, not a played Tool; it stays in hand. No unsuccessful search or declined warning is observed. Boiler Smog is an accepted prompt. Weezing does not attack in this source; its card displays two Darkness requirements, while filmed Energy Zone previews are Water.

## Evidence and recording limits

TURN_EVIDENCE.json binds native1170×2532frames to the source filename/hash, preserves requested source-local seek times, bottom-fifth crops[0,2025,1170,2532] and top crops[0,0,1170,780]. Owner draws have approximately+1,+3,+6second candidates plus before-ending hands; later candidates that already show actions are not used as pre-play evidence. Clear selections are56,126.5,206.5,260,351and434seconds. Actual extracted-frame PTS was not measured. Draw-end estimates have roughly0.5second precision. The native images, dense2second52–112pass, dense3second114–486pass and targeted1second255–274pass are retained. VIEWED_EVIDENCE_MANIFEST.json lists inspected image sheets and direct native views.

Neither discard pile is opened at any point. Discard snapshots are therefore unavailable, and public play/retreat history is not misrepresented as a full discard pile. Hidden opponent card identities, unseen deck slots and exact print identifiers remain unknown. Exact20-card deck binding is unverified. Targeted native checks resolved the turn12 healing card as Irida and confirmed Sharpedo free retreat retaining its Water. Full first-pass coverage is complete; acceptance and registration remain the lead's responsibility.
'''
    
(p/'REVIEW.md').write_text(review,encoding='utf-8')
(p/'COVERAGE.md').write_text('''# Coverage

Full first-pass review of one recorded battle, all12turns, setup through terminal result. Pending independent lead acceptance.

| Phase | Source-local coverage | Evidence |
|---|---|---|
| Deck choice/search/loading/setup |0–52|overview early sheet; native39and55|
| Turns1–2 |52–123|dense01 sheets1–4, native hand/board/action captures|
| Turns3–4 |123–204|dense_seeks sheets138,165,192,219; native126.5,166,172,185,195,203|
| Turns5–6 |204–256|dense_seeks sheets219,246,273; native206.5,208.5,211.5,219,230,237,240,245,254|
| Turns7–8 |256–348|dense07 sheets1–3, dense_seeks sheets273,300,327,354; native draw candidates, Research reveals, knockout and replacement|
| Turns9–10 |348–431|dense_seeks sheets354,381,408,435; native351,353,356,357,374,380,393,396,414,417,423,429|
| Turns11–12 |431–489|dense_seeks sheets435,462,last; native434,436,439,443,447,451,473.3,483,486,489|
| Terminal result/tail |489–504.478333|native489,495,501,504; tail overview|

No skipped turn or additional game. No Auto option seen. No deck QR or opened discard pile in this source. The exact deck version and hidden information are recording limits, not guessed facts. Dense reduced sheets provide action-location coverage; native draws and crops provide the required hand evidence. Actual frame PTS was not measured; seek timestamps are explicitly distinguished.
''',encoding='utf-8')
viewed=['overview/early.jpg','overview/second.jpg','overview/third.jpg','dense01/first.jpg']+[f'dense01/sheet_{n:02}.jpg' for n in range(2,5)]+[f'seekoverview/sheet{n}.jpg' for n in range(1,4)]+[f'dense_seeks/sheet_{n}.jpg' for n in [138,165,192,219,246,273,300,327,354,381,408,435,462]]+['dense_seeks/last.jpg','dense07/sheet_01.jpg','dense07/sheet_02.jpg','turn_evidence/hands_check.jpg','turn_evidence/fans_check.jpg']+[f'turn_evidence/{s}_{n}.jpg' for s in ['candidates','details','boundaries'] for n in [1,2]]+[f'turn_evidence/t{t:07.2f}.jpg' for t in [39,55,495,350,263,483]]
write('VIEWED_EVIDENCE_MANIFEST.json',{'reviewer':'/root/pause_014541','source_video':video,'source_sha256':sha,'viewed_image_paths':viewed,'notes':'Sheet constituents were visually inspected; retained native candidates additionally viewed in candidates/boundaries/detail sheets. Frames not in this list are retained evidence, not a claim of separate direct full-size viewing.'})
print('Packet written:12turns,',len(frames),'native frames')
