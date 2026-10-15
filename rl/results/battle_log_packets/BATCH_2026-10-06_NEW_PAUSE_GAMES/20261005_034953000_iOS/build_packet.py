from pathlib import Path
from copy import deepcopy
import json, datetime
p=Path(__file__).parent
S=json.loads((p/'SOURCE.json').read_text(encoding='utf-8')); video=S['video_basename'];sha=S['sha256'];gid=p.name
src=[dict(video_basename=video,sha256=sha,source_json='SOURCE.json')]
def save(n,d): (p/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fid(t):return 'f'+f'{t:07.2f}'.replace('.','_')
def refs(*ts):return [fid(t) for t in ts]
versions={'Aegislash Cursed Metal':'B2 120; Cursed Metal / Slicing Blade 70, HP140','Aegislash Superb Shield':'B1 172; Superb Shield 80, HP140','Honedge Pierce':'B1 170; Pierce20, HP60','Honedge Cut Up':'B2 118; Cut Up20, HP70','Doublade Dual Blades':'B1 171; Dual Blades40x, HP90','Doublade Slash':'B2 119; Slash40, HP90','Magnemite':'A2a 053; Tackle20, HP60','Magneton':'A2a 054; Rolling Attack30, HP90','Meltan':'A1 181; Amass, HP60','Melmetal ex':'B1 174; Headbutt80 / Metal Arms100+, HP170','Axew':'Sharp Fang40, HP70; exact printing not established','Fraxure':'Dragon Claw60, HP90; exact printing not established','Haxorus':'Frenzied Blade50+, HP150; exact printing not established','Munchlax':'Hungry Draw10, HP50; exact printing not established','Happiny':'Chubby Cheer10, HP30; exact printing not established'}
def cname(k):return k.split(' ')[0] if k.startswith(('Aegislash ','Honedge ','Doublade ')) else k
def card(k,i,t):return dict(position=i,name=cname(k),variant=versions.get(k),basis='Visible native hand/reveal and continuity; not inferred from deck membership',evidence_ids=refs(t),limit_reason=None)
def hand(ks,t,basis='direct visible native fan'):
    return dict(cards_left_to_right=[card(k,i+1,t) for i,k in enumerate(ks)],count=len(ks),basis=basis,evidence_ids=refs(t),status='observed',limit_reason=None)
def mon(k,hp,en=None,tool='none',t=0):
    maxima={'Magnemite':60,'Magneton':90,'Honedge Pierce':60,'Honedge Cut Up':70,'Meltan':60,'Melmetal ex':170,'Doublade Dual Blades':90,'Aegislash Cursed Metal':140,'Axew':70,'Fraxure':90,'Haxorus':150,'Munchlax':50,'Happiny':30}
    energy=en or {};fx=[]
    if tool=='Steel Apron':fx=[dict(name='Steel Apron',restriction='Take -10 attack damage; cannot be affected by Special Conditions',expiry='while attached')]
    return dict(name=cname(k),variant=versions[k],bench_position=None,hp_now=hp,hp_max=maxima[k],hp_max_basis='visible card HP; no max-HP Tool in this game',damage=maxima[k]-hp,attached_energy=dict(total=sum(energy.values()),by_type=energy),tool=tool,special_conditions=[],active_effects=fx,evidence_ids=refs(t),status='observed',limit_reason=None)
def empty(i,t):return dict(bench_position=i,name=None,status='visibly_empty',hp_now=None,hp_max=None,damage=None,attached_energy=None,tool='none',special_conditions=[],active_effects=[],evidence_ids=refs(t),limit_reason='Empty positional Bench slot, not an unknown Pokemon')
def bench(ms,t):
    out=[]
    for i,m in enumerate(ms,1):
        if m is None:out.append(empty(i,t))
        else:q=deepcopy(m);q['bench_position']=i;q['evidence_ids']=refs(t);out.append(q)
    return out
def state(oa,ob,pa,pb,pts=(0,0),stad='Rainbow Cave',t=0):return dict(owner=dict(active=oa,bench_in_position_order=bench(ob,t),points=pts[0]),opponent=dict(active=pa,bench_in_position_order=bench(pb,t),points=pts[1]),stadium=stad)
m=lambda k,h,e=None,tool='none',t=0:mon(k,h,e,tool,t)
# Resolved boundary states, independently transcribed from visible boards.
states=[state(m('Magnemite',60),[None]*3,m('Axew',70),[None]*3,stad='none')]
states.append(state(m('Magnemite',60),[None]*3,m('Axew',70),[None,m('Munchlax',50),m('Axew',70)],t=79))
states.append(state(m('Magnemite',60,{'Metal':1}),[m('Honedge Pierce',60),m('Meltan',60),None],m('Axew',50),[None,m('Munchlax',50),m('Axew',70)],t=93))
states.append(state(m('Magnemite',60,{'Metal':1}),[m('Honedge Pierce',60),m('Meltan',60),None],m('Axew',50),[None,m('Munchlax',50),m('Fraxure',90,{'Metal':1})],t=109))
states.append(state(m('Magnemite',60,{'Metal':1}),[m('Honedge Pierce',60),m('Melmetal ex',170,{'Metal':1},'Steel Apron'),None],m('Axew',30),[None,m('Munchlax',50),m('Fraxure',90,{'Metal':1})],t=133))
states.append(state(m('Magnemite',60,{'Metal':1}),[m('Honedge Pierce',60),m('Melmetal ex',170,{'Metal':1},'Steel Apron'),None],m('Fraxure',50),[None,m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],t=146))
states.append(state(m('Magneton',90,{'Metal':1}),[m('Honedge Pierce',60),m('Melmetal ex',170,{'Metal':2},'Steel Apron'),None],m('Fraxure',50),[None,m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],t=163))
states.append(state(m('Magneton',90,{'Metal':1}),[m('Honedge Pierce',60),m('Melmetal ex',170,{'Metal':2},'Steel Apron'),None],m('Haxorus',110,{'Metal':1}),[None,m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],t=179))
states.append(state(m('Magneton',90,{'Metal':2}),[m('Honedge Pierce',60),m('Melmetal ex',170,{'Metal':2},'Steel Apron'),None],m('Haxorus',80,{'Metal':1}),[None,m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],t=202))
states.append(state(m('Magneton',90,{'Metal':2}),[m('Honedge Pierce',60),m('Melmetal ex',170,{'Metal':2},'Steel Apron'),None],m('Haxorus',80,{'Metal':2}),[m('Happiny',30),m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],t=219))
states.append(state(m('Magneton',90,{'Metal':2}),[m('Doublade Dual Blades',90),m('Melmetal ex',170,{'Metal':3},'Steel Apron'),None],m('Haxorus',50,{'Metal':2}),[m('Happiny',30),m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],t=235))
states.append(state(m('Melmetal ex',170,{'Metal':3},'Steel Apron'),[m('Doublade Dual Blades',90),None,None],m('Haxorus',50,{'Fighting':1,'Metal':2}),[m('Happiny',30),m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],pts=(0,1),t=261))
states.append(state(m('Melmetal ex',170,{'Metal':4},'Steel Apron'),[m('Aegislash Cursed Metal',140),None,None],m('Happiny',30),[None,m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':1})],pts=(1,1),t=295))
states.append(state(m('Melmetal ex',170,{'Metal':4},'Steel Apron'),[m('Aegislash Cursed Metal',140),None,None],m('Happiny',30),[m('Happiny',30),m('Munchlax',50),m('Haxorus',150,{'Fighting':1,'Metal':2})],pts=(1,1),t=329))
states.append(state(m('Melmetal ex',170,{'Metal':4},'Steel Apron'),[m('Aegislash Cursed Metal',140),None,m('Honedge Cut Up',70,{'Metal':1},'Steel Apron')],m('Haxorus',150,{'Fighting':1,'Metal':2}),[m('Happiny',30),m('Munchlax',50),None],pts=(2,1),t=371))
states.append(state(m('Melmetal ex',10,{'Metal':4},'Steel Apron'),[m('Aegislash Cursed Metal',140),None,m('Honedge Cut Up',70,{'Metal':1},'Steel Apron')],m('Haxorus',150,{'Fighting':1,'Metal':2}),[m('Happiny',30),m('Munchlax',50),m('Munchlax',50)],pts=(2,1),t=384))
states.append(deepcopy(states[-1]))
ranges=[(47,79),(80,93),(94,109),(110,133),(134,146),(147,163),(164,179),(180,202),(203,219),(220,235),(236,261),(262,295),(296,329),(330,371),(372,384),(385,394)]
starts=[49,83,96,114,136,149.5,166,184.5,206,223,238,268,299,333,374,388]
ends=[79,93,109,133,146,163,179,202,219,235,261,295,329,371,384,393]
draws={2:('Meltan',82),4:('Steel Apron',113),6:('Magneton',149),8:('Steel Apron',183),10:('Doublade Dual Blades',222),12:('Doublade Slash',267),14:('Honedge Cut Up',332),16:('Melmetal ex',387)}
drawends={2:83,4:113.8,6:149.5,8:184,10:223,12:267.5,14:333,16:388.3}
selected={2:83,4:114,6:149.5,8:184.5,10:223,12:268,14:333,16:388}
candidates={2:[84,86,89],4:[114.6,116.6,119.6],6:[150.5,152.5,155.5],8:[185,187,190],10:[224,226,229],12:[268.5,270.5,273.5],14:[334,336,339],16:[389,391,394]}
beforeend={2:88,4:128,6:161,8:195,10:230,12:273,14:357,16:389}
hands={2:['Aegislash Cursed Metal','Honedge Pierce','Aegislash Superb Shield','Melmetal ex','Meltan'],4:['Aegislash Cursed Metal','Aegislash Superb Shield','Melmetal ex','Steel Apron'],6:['Aegislash Cursed Metal','Aegislash Superb Shield','Magneton'],8:['Aegislash Cursed Metal','Aegislash Superb Shield','Steel Apron'],10:['Aegislash Cursed Metal','Aegislash Superb Shield','Steel Apron','Doublade Dual Blades'],12:['Aegislash Cursed Metal','Aegislash Superb Shield','Steel Apron','Doublade Slash'],14:['Aegislash Superb Shield','Steel Apron','Doublade Slash','Honedge Cut Up'],16:['Aegislash Superb Shield','Doublade Slash','Melmetal ex']}
endhands={2:['Aegislash Cursed Metal','Aegislash Superb Shield','Melmetal ex'],4:['Aegislash Cursed Metal','Aegislash Superb Shield'],6:['Aegislash Cursed Metal','Aegislash Superb Shield'],8:hands[8],10:['Aegislash Cursed Metal','Aegislash Superb Shield','Steel Apron'],12:['Aegislash Superb Shield','Steel Apron','Doublade Slash'],14:['Aegislash Superb Shield','Doublade Slash'],16:hands[16]}
fans={2:3,4:4,6:3,8:3,10:3,12:4,14:4,16:4}
def play(kind,k,target,result,t,hc=None,energy=None,nested=None,prompt=None,response=None):return dict(order=None,kind=kind,card_name=cname(k) if k else None,card_variant=versions.get(k),target=target,energy=energy,result=result,prompt_text=prompt,response=response,nested_events_in_order=nested or [],hand_count_after=hc,source_video=video,timestamp_seconds=t,timestamp_basis='first retained observation of input/selection or animation; resolution timestamp listed separately where present',evidence_ids=refs(t),basis='source observation',limit_reason=None)
def energy(target,t,hc=None,typ='Metal'):return play('energy_attachment',None,target,'Attach one '+typ+' Energy from Energy Zone',t,hc,dict(type=typ,count=1,destination=target,retreat_payment_by_type=None))
def evolve(k,target,t,hc=None):return play('card_play',k,target,'Evolve target; existing damage and attachments retained',t,hc)
def attack(k,target,name,dmg,t,hc=None):return play('attack',k,target,f'{name}: displayed {dmg} damage; ends turn',t,hc,nested=[dict(kind='damage_resolution',damage=dmg)])
def end(t,hc=None):return play('end_turn',None,None,'Turn ends without attack',t,hc)
def stadium(t):return play('stadium_activation','Rainbow Cave','Energy Zone','Rainbow Cave visibly activates; selected type not exposed as a readable choice. Subsequent attached Energy is Metal.',t,nested=[dict(kind='energy_choice',selected_type=None,limit_reason='Selection dialog/choice identity is not exposed from the opponent perspective')])
P={
1:[play('card_play','Poke Ball','deck','One concealed Basic search',53),play('card_play','Poke Ball','deck','Second concealed Basic search',59),play('card_play','Axew','opponent Bench right','Place Axew70',65),play('card_play','Munchlax','opponent Bench middle','Place Munchlax50',67),play('card_play',"Professor's Research",'deck','Draw two concealed cards',69),play('card_play','Rainbow Cave','Stadium','Put Rainbow Cave in play',77),end(79)],
2:[play('card_play','Meltan','owner Bench middle','Place Meltan60',83.8,4),play('card_play','Honedge Pierce','owner Bench left','Place Honedge60',86,3),energy('owner Active Magnemite',87,3),attack('Magnemite','opponent Active Axew','Tackle',20,91,3)],
3:[evolve('Fraxure','opponent Bench right Axew',99),energy('opponent Bench right Fraxure',100),play('card_play',"Professor's Research",'deck','Draw two concealed cards',102),end(109)],
4:[evolve('Melmetal ex','owner Bench middle Meltan',116,3),play('card_play','Steel Apron','owner Bench middle Melmetal ex','Attach Tool',122,2),energy('owner Bench middle Melmetal ex',126,2),attack('Magnemite','opponent Active Axew','Tackle',20,131,2)],
5:[evolve('Fraxure','opponent Active Axew',139),evolve('Haxorus','opponent Bench right Fraxure',142),energy('opponent Bench right Haxorus',144,typ='Fighting'),end(146)],
6:[evolve('Magneton','owner Active Magnemite',150.5,2),energy('owner Bench middle Melmetal ex',160,2),end(162,2)],
7:[evolve('Haxorus','opponent Active Fraxure',168),stadium(173),energy('opponent Active Haxorus',175),end(179)],
8:[energy('owner Active Magneton',196,3),attack('Magneton','opponent Active Haxorus','Rolling Attack',30,199,3)],
9:[play('card_play','Happiny','opponent Bench left','Place Happiny30',209),stadium(213),energy('opponent Active Haxorus',215),end(219)],
10:[evolve('Doublade Dual Blades','owner Bench left Honedge Pierce',223.5,3),energy('owner Bench middle Melmetal ex',228,3),attack('Magneton','opponent Active Haxorus','Rolling Attack',30,233,3)],
11:[energy('opponent Active Haxorus',243,typ='Fighting'),attack('Haxorus','owner Active Magneton','Frenzied Blade',150,246),play('prompt_response','Melmetal ex','owner Active','Owner promotes Melmetal ex after Magneton KO; no retreat payment',261,prompt='Please choose a Pokemon to switch in',response='Melmetal ex')],
12:[evolve('Aegislash Cursed Metal','owner Bench left Doublade Dual Blades',271,3),energy('owner Active Melmetal ex',274,3),attack('Melmetal ex','opponent Active Haxorus','Metal Arms',180,281,3)],
13:[energy('opponent Bench right Haxorus',302),play('card_play','Happiny','opponent Bench left','Place second Happiny30',305),attack('Happiny','owner Active Melmetal ex','Chubby Cheer',0,326)],
14:[play('card_play','Honedge Cut Up','owner Bench right','Place Honedge70',333.5,3),play('card_play','Steel Apron','owner Bench right Honedge Cut Up','Attach Tool',353,2),energy('owner Bench right Honedge Cut Up',355,2),attack('Melmetal ex','opponent Active Happiny','Metal Arms',180,359,2)],
15:[play('card_play','Munchlax','opponent Bench right','Place second Munchlax50',377),attack('Haxorus','owner Active Melmetal ex','Frenzied Blade',160,381)],
16:[]}
for ps in P.values():
    for i,pl in enumerate(ps,1):pl['order']=i
P[12][0].update(resolution_seconds=272,evidence_ids=refs(270.5,271,272),timestamp_basis='Input card movement observed at271s; evolved board and effect resolution at272s')
# Boundaries distinguish the visible Current turn label from the turn concluded.
def board(n,s,phase,t,acting,owner_current,op_current,opnext):
    b=deepcopy(s);b.update(turn_number_displayed=None,turn_number_displayed_limit='No readable Current turn label in this selected board frame; phase identifies reviewed turn separately',phase=phase,source_seconds=t,evidence_ids=refs(t),shared_effects=[])
    for who,cur,nxt in [('owner',owner_current,'Metal'),('opponent',op_current,opnext)]:
        q=b[who];q.update(status='observed',limit_reason=None,evidence_ids=refs(t),board_effects=[])
        q['energy_zone']=dict(this_turn=dict(type='Metal' if who=='owner' and cur else (cur if isinstance(cur,str) else 'none'),count=1 if cur else 0,available=bool(cur)),next=dict(type=nxt,count=1,available=False),basis='visible large current orb and small next-energy icon; next count is one preview icon',evidence_ids=refs(t),limit_reason='An empty off-turn current orb does not establish whether unused Energy was discarded or retained in hidden state.')
        for pk in [q['active']]+q['bench_in_position_order']:
            if pk:pk['evidence_ids']=refs(t)
    if any(pk.get('name')=='Aegislash' for pk in b['owner']['bench_in_position_order']):
        b['owner']['board_effects'].append(dict(name='Cursed Metal',source='owner Bench left Aegislash',affected='Metal and Psychic Pokemon attacks versus opponent Active',modifier='+30 damage',expiry='while Aegislash remains in play'))
    if (n==13 and phase.startswith('after')) or n in (14,15):
        b['opponent']['board_effects'].append(dict(name='Chubby Cheer',source='opponent Happiny attack turn13',modifier='+20 damage to opponent Active during opponent next turn',expiry='after opponent turn15',evidence_ids=refs(329)))
    if n==15 and phase.startswith('after'):b['opponent']['board_effects']=[]
    return b
nexttypes={1:'Metal',2:'Metal',3:'Fighting',4:'Fighting',5:'Metal',6:'Metal',7:'Metal',8:'Metal',9:'Fighting',10:'Fighting',11:'Metal',12:'Metal',13:'Metal',14:'Metal',15:'Metal',16:'Metal'}
opcurrent={1:None,3:'Metal',5:'Fighting',7:'Metal',9:'Metal',11:'Fighting',13:'Metal',15:'Metal'}
turns=[]
for n,(st,et) in enumerate(ranges,1):
    owner=n%2==0;t=starts[n-1];eh=hand(endhands[n],beforeend[n]) if owner else hand(endhands.get(n-1,['Aegislash Cursed Metal','Honedge Pierce','Aegislash Superb Shield','Melmetal ex']),ends[n-1],basis='owner fan observed during opponent turn; not acting-player hand')
    hs=hand(hands[n],selected[n]) if owner else dict(cards_left_to_right=None,count=None,basis='opponent card identities concealed',evidence_ids=refs(t),status='hidden',limit_reason='Opponent cards are face down; count at owner starts is separately measured')
    if owner:
        k,rt=draws[n];ds=[dict(kind='normal_draw',caused_by='turn_start',linked_play_order=None,cards_in_reveal_order=[dict(name=cname(k),variant=versions.get(k),reveal_position=1,source_video=video,timestamp_seconds=rt,evidence_ids=refs(rt),basis='visible card reveal',limit_reason=None)],hand_count_before=len(hands[n])-1,hand_count_after=len(hands[n]),returned_or_discarded_cards=[],source_video=video,timestamp_seconds=rt,evidence_ids=refs(rt),limit_reason=None)]
    else:
        ds=[dict(kind='normal_draw',caused_by='turn_start',linked_play_order=None,cards_in_reveal_order=[dict(name=None,reveal_position=1,source_video=video,timestamp_seconds=t,evidence_ids=refs(t),basis='concealed opponent normal draw',limit_reason='Card face hidden')],source_video=video,timestamp_seconds=t,evidence_ids=refs(t),limit_reason='Opponent draw identity hidden')]
        if n==1:
            for kind,num,rt,cnt in [('search',1,55,1),('search',2,61,1),('supporter_draw',5,71,2)]:ds.append(dict(kind=kind,caused_by=P[n][num-1]['card_name'],linked_play_order=num,cards_in_reveal_order=[dict(name=None,reveal_position=i+1,source_video=video,timestamp_seconds=rt,evidence_ids=refs(rt),basis='concealed search/draw',limit_reason='Face not exposed') for i in range(cnt)],source_video=video,timestamp_seconds=rt,evidence_ids=refs(rt),limit_reason='Opponent search/draw cards hidden; later plays do not establish which search returned which card'))
        if n==3:ds.append(dict(kind='supporter_draw',caused_by="Professor's Research",linked_play_order=3,cards_in_reveal_order=[dict(name=None,reveal_position=i+1,source_video=video,timestamp_seconds=104,evidence_ids=refs(104),basis='concealed draw',limit_reason='Face hidden') for i in range(2)],source_video=video,timestamp_seconds=104,evidence_ids=refs(104),limit_reason='Opponent identities hidden'))
    bs=board(n,states[n-1],f'start of reviewed turn {n} after normal draw',t,'owner' if owner else 'opponent',owner,opcurrent.get(n),nexttypes[n])
    ba=board(n,states[n],f'after reviewed turn {n} ending action and resolution',ends[n-1],'owner' if owner else 'opponent',n==16,'Metal' if n==15 else None,nexttypes[n])
    auto=[]
    if n==11:auto=[dict(order=1,kind='KO',pokemon='owner Magneton',damage=150,pre_removal_evidence_ids=refs(247,249)),dict(order=2,kind='point_award',player='opponent',points_after=1,evidence_ids=refs(252)),dict(order=3,kind='promotion',player='owner',pokemon='Melmetal ex',evidence_ids=refs(261))]
    if n==12:auto=[dict(order=1,kind='Cursed Metal damage modifier',amount=30,evidence_ids=refs(274)),dict(order=2,kind='KO',pokemon='opponent Haxorus',damage=180,pre_removal_evidence_ids=refs(283,284)),dict(order=3,kind='point_award',player='owner',points_after=1,evidence_ids=refs(288)),dict(order=4,kind='promotion',player='opponent',pokemon='Happiny',evidence_ids=refs(294,295))]
    if n==13:auto=[dict(order=1,kind='Steel Apron reduction',damage_before=10,damage_after=0,evidence_ids=refs(327)),dict(order=2,kind='Chubby Cheer delayed buff',player='opponent',amount=20,expiry='after opponent turn15',evidence_ids=refs(329))]
    if n==14:auto=[dict(order=1,kind='KO',pokemon='opponent Active Happiny',damage=180,pre_removal_evidence_ids=refs(361,363)),dict(order=2,kind='point_award',player='owner',points_after=2,evidence_ids=refs(366)),dict(order=3,kind='promotion',player='opponent',pokemon='Haxorus from right Bench',evidence_ids=refs(371))]
    if n==15:auto=[dict(order=1,kind='damage_modifiers',base_formula='50 + 20 x 5 total Benched Pokemon = 150',chubby_cheer=20,steel_apron=-10,damage_final=160,evidence_ids=refs(382,384)),dict(order=2,kind='Chubby Cheer expires',evidence_ids=refs(384))]
    if n==16:auto=[dict(order=1,kind='opponent_concession',message='Your opponent conceded',evidence_ids=refs(390,391)),dict(order=2,kind='Victory',evidence_ids=refs(395,409))]
    turn=dict(turn_number=n,who_played='owner' if owner else 'opponent',source_video=video,timing=dict(start_seconds=st,end_seconds=et,draw_animation_end_seconds=drawends.get(n),first_voluntary_move_seconds=P[n][0]['timestamp_seconds'] if P[n] else None,before_end_action_seconds=beforeend.get(n,et),end_after_resolution_seconds=et,timestamp_limit='Native seeks bracket animation stages; timestamps are source-local seeks, not measured PTS'),hand_at_start=hs,owner_hand_start=hs if owner else None,opponent_hand_at_owner_turn_start=dict(count=fans[n],supported_range=None,count_method='Count exposed card-back panels in native top crop, not printed symbols within each sleeve',basis='direct visual count',evidence_ids=refs(selected[n]),limit_reason=None) if owner else None,draws_and_searches=ds,plays_in_order=P[n],automatic_events_in_order=auto,board_at_start=bs,board_after=ba,owner_hand_end=eh,discard_snapshot_ids=[],turn_evidence_ids=refs(t,ends[n-1]),limits=['Opponent concealed hand identities unavailable','Opened discard pile is never shown; top preview is not full pile'])
    if owner:turn['owner_hand_reconciliation']=dict(start=len(hands[n]),card_additions_after_start=0,card_removals=len(hands[n])-len(endhands[n]),end=len(endhands[n]),basis='normal draw included in start; direct fan corroborates played card removals; Energy attachments do not remove hand cards')
    if n==8:turn['inspection_observations']=[dict(kind='card_inspection',card_name='Melmetal ex',timestamp_seconds=187,evidence_ids=refs(186,187,188),effect='Central card zoom only; no hand card removal or game-state play')]
    turns.append(turn)
save('TURN_LEDGER.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=src,turns=turns,limits=['Full source reviewed; all owner draws named; opponent draws/searches hidden','No opened discard piles','Input times are retained observation seeks, with reveal/resolution retained separately']))
Q=json.loads((p/'qr_intake/QR_DECODE_0005.00.json').read_text(encoding='utf-8'))
qrslots=[]
for c in Q['cards']:
    for _ in range(c['count']):qrslots.append(dict(name=c['name'],entity_id=c['entity_id'],variant=' / '.join(c['printing_aliases']),variant_basis='QR semantic identity, exact artwork/printing unspecified'))
save('DECK_USED.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=src,deck_name_in_log='Aegislash / Melmetal ex / Magnezone',filmed_deck_label='New deck 6',source_url=S['requested_log'],captured_at=Q['decoded_at_utc'],log_list_version='prepared filmed-qr-afe59c84d238; not verified saved live',expected_card_count=20,cards_in_log_order=None,counts_by_name_and_variant=None,energy_configuration_from_log=None,actual_card_count=20,capture_source_text_or_image=['../LIVE_DECK_SNAPSHOT.json','../NEW_DECK_ENTRIES.json','qr_intake/QR_DECODE_0005.00.json','qr_intake/t0005.00.png'],game_version_binding_basis='Source starts on New deck 6 event selection; opens its QR then closes QR and directly taps Battle at7s; no deck editing or selection change before matchmaking/setup. Visible game cards agree with QR, including distinct B1/B2 line.',conflicts_with_filmed_cards=[],exact_list_status='filmed_QR_exact_semantic_list_verified_live_log_snapshot_missing',filmed_QR=dict(cards_in_QR_entity_order=qrslots,counts_by_name_and_entity_id=[dict(name=c['name'],entity_id=c['entity_id'],variant_aliases=c['printing_aliases'],count=c['count']) for c in Q['cards']],energy_configuration=['Metal'],payload=Q['payload'],receipt='qr_intake/QR_DECODE_0005.00.json',total=20),limits=['The initial nine live deck snapshots do not contain this newly filmed deck. Prepared entry exists but worker does not claim live saving.','QR resolves playable identities and count, not artwork/rarity or exact printings.','Current live list must be verified by lead after external deck saving.']))
opening=['Aegislash Cursed Metal','Honedge Pierce','Magnemite','Aegislash Superb Shield','Melmetal ex']
limits=['Opponent identities remain hidden for normal and Research draws and both Poke Ball searches.','No player opens a discard pile anywhere in this source; visible top cards are partial previews.','Source-local timestamp estimates use native FFmpeg seeks; no separate frame PTS measurement.','Initial live deck snapshot has no matching new metal list; exact QR semantic list preserved, live saving pending lead.','Later +1/+3/+6 owner candidates can already show immediate plays; selected earlier intact frames are retained.','Rainbow Cave activation choice is not exposed from opponent perspective; subsequent attachments are observed Metal.']
save('PAUSE_GAME.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,review_date='2026-10-06',sources=src,destination=S['requested_log'],deck_name='Aegislash / Melmetal ex / Magnezone',filmed_deck_label='New deck 6',opening=dict(source_video=video,timestamp_seconds=35,expected_card_slots=5,recorded_card_count=5,cards_left_to_right=[card(k,i+1,35) for i,k in enumerate(opening)],selected_active=dict(name='Magnemite',opening_position=3,source_video=video,timestamp_seconds=40,evidence_ids=refs(40,42)),redraw_or_replacement='none shown',before_active_placement=True,status='observed',evidence_ids=refs(31,35,40,42),limit_reason='Names/versions supported by native fan artwork and later direct card inspection; exact printing/artwork rarity not assumed from QR'),packet_files=dict(prose='REVIEW.md',coverage='COVERAGE.md',deck='DECK_USED.json',turns='TURN_LEDGER.json',evidence='TURN_EVIDENCE.json'),capture_status='complete_with_recording_limits',battle_review_status='full_source_first_pass_complete_pending_independent_acceptance',outcome=dict(result='win',opponent='MIYA',owner='Dacz8976',method='explicit opponent concession',owner_points=2,opponent_points=1,turns=16,evidence_ids=refs(390,391,395,409)),limits=limits,lead_checked=False))
frames=json.loads((p/'FRAME_INDEX.json').read_text(encoding='utf-8'));fm={f['evidence_id']:f for f in frames}
for f in frames:f.update(role='source_phase_or_action_evidence',selected_for_start_hand=False,before_first_play=None,unzoomed=None,hand_spread=None)
for n in selected:
    sel=fm[fid(selected[n])];sel.update(role='selected_intact_preplay_hand',turn_number=n,who_played='owner',selected_for_start_hand=True,before_first_play=True,unzoomed=True,hand_spread=True,draw_animation_end_seconds=drawends[n],observation='Directly inspected native frame. All hand cards retained before first card leaves the hand.',suitability_or_limit='Intact fan; newly drawn card may still be highlighted. T2 uses 83s to keep all five positions inside frame.')
    for ct in candidates[n]:
        f=fm[fid(ct)];suitable=(n==4 and ct==114.6) or (n==8 and ct in (185,190)) or (n==12 and ct==268.5) or (n==16 and ct==389)
        before_play=suitable or (n==8 and ct==187) or (n==12 and ct==270.5)
        note='Candidate remains before first play and no central card zoom' if suitable else ('Concession/result overlay after owner turn began; unsuitable for hand start' if n==16 else 'Already after an immediate play; does not replace earlier selected intact hand')
        if n==8 and ct==187:note='Before first game-state play, but central Melmetal inspection zoom; unsuitable for intact hand start'
        if n==12 and ct==270.5:note='Before evolution input, Aegislash selected/highlighted; all four retained but right card clipped in expanded fan; earlier268s frame selected'
        f.update(role='draw_relative_candidate',turn_number=n,who_played='owner',draw_animation_end_seconds=drawends[n],offset_after_draw_seconds=round(ct-drawends[n],2),before_first_play=before_play,unzoomed=(False if n==8 and ct==187 else True if suitable or (n==12 and ct==270.5) else None),hand_spread=suitable,suitability_or_limit=note)
    fm[fid(beforeend[n])].update(role='before_ending_action_hand',turn_number=n,who_played='owner',observation='Direct ending fan/count before attack or End Turn; turn16 before opponent concession',suitability_or_limit='Pre-attack/End Turn hand substitution; resolved board is separately retained')
save('TURN_EVIDENCE.json',dict(is_template=False,schema='pause-games/turn-capture-v1',game_id=gid,sources=src,source_sha256=sha,default_capture_policy=dict(owner_turn_offsets_after_draw_seconds=[1,3,6],before_end_action_required=True,native_resolution_required=True,bottom_crop_height_fraction=.2,top_crop='native full width, y0..750 covers fan, clocks and Energy Zone',fixed_grid_is_turn_start_evidence=False,discard_target_every_owner_turns=[2,3]),frames=frames,discard_snapshots=[dict(snapshot_id='discard_not_opened_'+w,pile_owner=w,turn_number=None,source_video=video,timestamp_seconds=None,cards_in_view=None,scroll_coverage='not opened anywhere in reviewed source',full_pile_established=False,evidence_ids=[],limit_reason='Full pile view is absent; top discard previews are not full contents') for w in ['owner','opponent']],partial_discard_previews=[dict(pile_owner='owner',timestamp_seconds=266,cards_in_view=['Magneton top preview'],full_pile_established=False,evidence_ids=refs(266)),dict(pile_owner='opponent',timestamp_seconds=334,cards_in_view=['Haxorus top preview'],full_pile_established=False,evidence_ids=refs(334)),dict(pile_owner='opponent',timestamp_seconds=388,cards_in_view=['Happiny top preview'],full_pile_established=False,evidence_ids=refs(388))],scheduled_capture_limits=limits,draw_timing_status='observed native seeks with approximately +1/+3/+6; not frame-perfect PTS'))
save('SUMMARY.json',dict(source_video=video,source_sha256=sha,reviewer='/root/pause_034953',model='Sol',review_date='2026-10-06',review_scope='Entire source 0..410.035s; setup, all 16 turns, terminal concession and results',review_status='full_source_first_pass_complete_pending_independent_acceptance',capture_status='complete_with_recording_limits',classification='human_event_battle',auto_control_visible=False,mode='Deluxe Pack: Mega Emblem Event',mode_evidence_ids=refs(0,7),opponent='MIYA',owner='Dacz8976',local_match_date='2026-10-04',local_match_date_basis='RECORDING_METADATA.json embedded UTC creation time converts to America/Chicago',outcome='win',result_evidence_ids=refs(390,391,395,409),method='opponent conceded',points=dict(owner=2,opponent=1),turns=16,damage_done=460,deck_label='New deck 6',deck_name='Aegislash / Melmetal ex / Magnezone',external_eligibility='human Pause Games eligible; lead only registers/saves',independent_targets=[dict(seconds=[31,35,40],purpose='Original opening five and selected Active'),dict(seconds=[82,83,83.8,86,87,91,93],purpose='Ordinary owner first move, draw, fan and Tackle ending hand'),dict(seconds=[95,99,100,102,104,109],purpose='Ordinary opponent turn3 action order and concealed Research draw'),dict(seconds=[222,223,223.5,228,233,235],purpose='Immediate evolution after owner turn10 draw and exact version'),dict(seconds=[267,268,272,274,281,283,284,288,294],purpose='Owner turn12 draw, Cursed Metal, Metal Arms180 and point/promotion'),dict(seconds=[377,381,382,384,387,388,390,409],purpose='Final opponent turn, 160 damage, last draw, explicit concession and results')],limits=limits))
save('UNCERTAINTIES.json',dict(source_video=video,source_sha256=sha,status='bounded recording_limits',items=[dict(id='U1',category='hidden_information',timestamps=[55,61,71,104],description='Opponent search and draw identities concealed. Visible later cards do not prove search-to-card mapping.',disposition='retain unknown'),dict(id='U2',category='absent_view',timestamps=[0,410.035],description='No opened discard piles in full recording; partial top previews only.',disposition='source limit'),dict(id='U3',category='deck_snapshot',timestamps=[5],description='QR20 is verified and bound continuously to game; matching newly prepared deck not in frozen initial live snapshot.',disposition='lead external deck-save check pending'),dict(id='U4',category='opponent_choice',timestamps=[173,213],description='Rainbow Cave activation is visible; exact type-choice UI is hidden. Metal attachments are directly observed afterward.',disposition='no guessed selection'),dict(id='U5',category='timing',timestamps=[83,113.8,149.5,184,223,267.5,333,388.3],description='Animation-end estimates are bracketed native seeks, not measured PTS. Scheduled candidates carry suitability limits.',disposition='explicit timing bound')],consequential_ambiguities_requiring_astra=[]))
rows=[]
for t in turns:
    n=t['turn_number'];desc='; '.join(f"{pl['order']}. {pl['card_name'] or pl['kind']} -> {pl['target'] or 'turn'}: {pl['result']} ({pl['timestamp_seconds']}s)" for pl in t['plays_in_order']) or 'No owner play before explicit opponent concession.'
    rows.append(f"| {n} | {t['who_played']} | {ranges[n-1][0]}-{ranges[n-1][1]} | {desc} | {len(endhands[n]) if n%2==0 else 'owner fan preserved'} |")
text='''# 20261005_034953000_iOS.MP4 full-source first pass

Reviewer: /root/pause_034953, Sol. Review date: October 6, 2026. Independent acceptance remains with lead.

The owner Dacz8976 wins against MIYA by an explicit opponent concession. The result screen reports 16 turns, owner 2 points, opponent 1 point and 460 damage done. The filmed queue is Deluxe Pack: Mega Emblem Event. No Auto option is visible. The local match date is October 4, 2026, established by embedded creation time in RECORDING_METADATA.json, rather than the UTC-looking filename.

## Source and deck continuity

Frozen SOURCE.json binds 759,507,732 bytes, 410.035 seconds and SHA-256 85f9e3803543f512323259794b7166808e5bfd2ff5a3854d8ce1a40686075180. Retained native images use 1170 x 2532. Times are source-local requested FFmpeg seeks, not separately measured frame PTS.

The source opens on event selection with New deck 6, shows its QR at 5 seconds, closes it and immediately enters Battle at 7 seconds. Matchmaking and setup continue without a deck-edit or selection change. The QR receipt is reused unchanged. It binds 20 semantic card slots and Metal Energy. The exact new list is absent from the initial nine live snapshots; the batch prepared entry filmed-qr-afe59c84d238 exists but this worker does not claim it was saved externally. DECK_USED.json preserves that distinction.

The list preserves Honedge B1 170 Pierce, HP60 and B2 118 Cut Up, HP70, Doublade B1 171 Dual Blades and B2 119 Slash, and Aegislash B1 172 Superb Shield and B2 120 Cursed Metal. Different variants remain distinct. The game visibly uses both Honedge versions, both Doublade versions and the Cursed Metal Aegislash; Superb Shield stays in hand. QR aliases do not establish exact artwork or rarity.

## Opening and all turns

Opening at 35 seconds, before Active placement: Aegislash Cursed Metal, Honedge Pierce, Magnemite, Aegislash Superb Shield, Melmetal ex, left to right. Magnemite, slot 3, is placed Active at 40 seconds. No setup Bench cards are placed. Owner goes second. Native source evidence, bottom-fifth crops and top fan crops are indexed in TURN_EVIDENCE.json.

| Turn | Player | Source seconds | Numbered meaningful actions | Owner end hand |
|---|---|---|---|---|
'''+ '\n'.join(rows)+'''

Each table row corresponds to one TURN_LEDGER.json row, including opponent turns. Opponent normal draws are concealed. Turn1 has two Poke Ball searches, then Axew and Munchlax placements, Research and Rainbow Cave. Research draws on turns1 and3 are individually represented as concealed cards. Owner uses no search or draw Supporter; every owner normal draw is named.

## Native hands and arithmetic

Selected intact preplay hands were directly inspected at 83, 114, 149.5, 184.5, 223, 268, 333 and 388 seconds for owner turns2 through16. Each retained full-resolution image has a full-width bottom fifth, y2025..2532, and top crop, y0..750. Draw-relative candidates at about +1/+3/+6 seconds are individually labeled; immediate plays make most later candidates unsuitable. A highlighted card still in an intact fan is distinguished from a card already leaving the hand, a central card zoom and a board after evolution. The pre-ending hand substitute and the resolved board are separate evidence.

Owner start/end counts: turn2 5/3, turn4 4/2, turn6 3/2, turn8 3/3, turn10 4/3, turn12 4/3, turn14 4/2, turn16 3/3. All draws occur before these start counts. Attachments and attacks do not remove cards from hand. Visually counted opponent fans at owner starts are 3,4,3,3,3,4,4,4. Sleeve artwork contains repeated symbols; counts use the card-back panels, not those symbols.

Owner draws in order: Meltan (82s), Steel Apron (113s), Magneton (149s), Steel Apron (183s), Doublade Dual Blades (222s), Doublade Slash (267s), Honedge Cut Up (332s), Melmetal ex (387s). Reveal and selection/play stages have separate retained timestamps. Owner normal draw animations end approximately 83,113.8,149.5,184,223,267.5,333,388.3 seconds.

## Board and damage reconciliation

Magnemite takes no damage before evolving. Owner Tackle20 twice changes opponent Active Axew70 to50 to30; its evolution retains40 damage, first Fraxure50/90 and then Haxorus110/150. Rolling Attack30 twice changes Haxorus110 to80 to50. Opponent turn11 attaches Fighting to the Active Haxorus's two Metal, then Frenzied Blade displays150 and KOs Magneton90. Point award is independently visible at252 seconds; the removed Magneton is not claimed as post-removal Active. Owner promotes Melmetal ex from middle Bench.

Turn12 draws the Slash Doublade, evolves the existing Dual Blades Doublade into Cursed Metal Aegislash, then adds the fourth Metal to Melmetal ex. Metal Arms with Steel Apron is150, plus Cursed Metal30, displays180 against Haxorus50 at283 seconds. Haxorus is removed before the one-point award at288 seconds. Opponent promotes Happiny from the left Bench. Turn13 adds Metal to the second Haxorus and benches a second Happiny. Chubby Cheer10 is reduced to0 by Steel Apron, with the +20 next-opponent-turn effect visibly applied at329 seconds.

Turn14 places the Cut Up Honedge right, equips the second Steel Apron and attaches Metal to it. Metal Arms again displays180 and KOs the Active Happiny30 at361 seconds. The point award brings owner to2 at366 seconds, and the remaining Haxorus150 moves from right Bench to Active. Turn15 benches the second Munchlax; no Energy attachment is observed and Metal remains visibly unused in the opponent zone. Five total Benched Pokemon make Frenzied Blade150; Chubby Cheer adds20 and Steel Apron reduces10, yielding the displayed160. Melmetal ex170 becomes10 HP. The owner draws Melmetal ex on turn16 and makes no voluntary play before the opponent-conceded message at390-392 seconds.

Owner damage done reconciles exactly: 20+20+30+30+180+180 =460, matching the result screen. Points finish2-1 by concession, not a third scored knockout. No coin flips, retreats, switches with payment, visible declined warnings, Special Conditions or healing are shown. The actual promotion prompts are retained separately from retreat actions. All boards include ordered three Bench positions, typed Energy, HP/max/damage, Tools, effects, points, Stadium and Energy Zone previews. Empty positions explicitly mean visibly empty. Current turn display is kept null in selected boundary frames without a readable label; transition evidence establishes the row numbers separately.

## Limits and independent checks

Opponent normal draws, both Poke Ball finds and all four Research cards remain concealed. Rainbow Cave activations at173 and213 seconds are visible, but the opponent's exact choice UI is not shown; subsequent Metal attachments are observed. No player opens a full discard pile. Top discard previews are partial only. The exact QR list is available; live saving of its newly prepared deck is pending lead verification. Timing is source-seek based, with late scheduled candidates unsuitable after immediate plays or concession. These are source/retrieval limits, not uninspected turns.

Recommended independent source checks: opening31-42; ordinary owner first move82-93; ordinary opponent turn3 95-109; immediate owner turn10 draw/evolution222-235; consequential turn12 draw/evolution/damage/points267-294; final opponent turn and concession377-409. SUMMARY.json carries bounded targets. Structural receipt confirms only file/reference/count consistency. This packet does not claim acceptance, registration, external saving or archive movement.
'''
(p/'REVIEW.md').write_text(text,encoding='utf-8')
cov='''# Full-source coverage

All available phases were visually reviewed using native source seeks, coarse location images and denser action/reveal windows. Sparse overviews alone are not the completion basis. The native extraction/crop index preserves the evidence; normal animation and waiting intervals do not imply extra actions.

| Interval | Reviewed scope | Coverage |
|---|---|---|
| 0-7 | Event selection, named deck, QR and Battle continuity | Complete |
| 8-24 | Searching, MIYA matchmaking/loading | Complete |
| 25-44 | Coin, second-player order, original opening5, Magnemite placement and setup | Complete |
| 45-46 | Both Active cards revealed, battle begins | Complete |
'''
cov+='\n'.join(f'| {a}-{b} | Turn {i}: {"owner" if i%2==0 else "opponent"}, all recorded meaningful actions, hand/draw and resolved boards | Complete |' for i,(a,b) in enumerate(ranges,1))
cov+='''
| 395-410.035 | Victory animation and results versus MIYA, turn/point/damage totals | Complete |

Original source remains in its assigned location. No unseen battle continuation is required: explicit concession, Victory and results are all recorded. Entire source coverage and capture quality are distinct: concealed opponent cards, absent full-discard views, opponent Stadium choice and initial live deck-snapshot gap remain explicit. Selected native hand frames were directly inspected before suitability flags were set. Independent acceptance is pending lead.
'''
(p/'COVERAGE.md').write_text(cov,encoding='utf-8')
print('Built 16-turn source-bound packet; independent acceptance not claimed.')
