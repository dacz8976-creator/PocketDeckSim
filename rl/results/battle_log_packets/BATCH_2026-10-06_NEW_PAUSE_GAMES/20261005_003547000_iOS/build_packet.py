import json, copy, shutil
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone

P=Path(__file__).resolve().parent
SRC=json.loads((P/'SOURCE.json').read_text())
VIDEO=SRC['video_basename']; SHA=SRC['sha256']; GAME='20261005_003547000_iOS_game1'
BIND=[{'video_basename':VIDEO,'sha256':SHA,'source_json':'SOURCE.json'}]
NOW=datetime.now(timezone.utc).isoformat()
frames={float(f.stem[1:]):f for folder in ['coarse','detail','focus','final_focus','turn_evidence'] for f in (P/folder).glob('t*.jpg')}
E=P/'turn_evidence'; E.mkdir(exist_ok=True)
evidence={}

def frame(t,role='event',turn=None,obs=None,draw=None,offset=None,selected=False,before=None,unzoomed=None,limit=None):
    key=f'f{t:07.2f}'
    if key in evidence:
        r=evidence[key]
        if role not in r['roles']: r['roles'].append(role)
        if selected: r['selected_for_start_hand']=True
        if draw is not None: r.update(draw_animation_end_seconds=draw,offset_after_draw_seconds=offset)
        if before is not None: r['before_first_play']=before
        if unzoomed is not None: r['unzoomed']=unzoomed
        if limit: r['suitability_or_limit']=limit
        return key
    f=frames[t]; dest=E/f.name
    if f.resolve()!=dest.resolve(): shutil.move(str(f),str(dest)); frames[t]=dest
    im=Image.open(dest);w,h=im.size
    bottom=E/f'{dest.stem}_bottom.png';top=E/f'{dest.stem}_top.png'
    if not bottom.exists(): im.crop((0,int(h*.8),w,h)).save(bottom)
    if not top.exists(): im.crop((0,0,w,700)).save(top)
    evidence[key]={'evidence_id':key,'role':role,'roles':[role],'turn_number':turn,'who_played':('owner' if turn and turn%2 else 'opponent' if turn else None),'source_video':VIDEO,'source_sha256':SHA,'draw_animation_end_seconds':draw,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':offset,'full_frame_path':str(dest.relative_to(P)).replace('\\','/'),'native_dimensions':{'width':w,'height':h},'bottom_crop':{'path':str(bottom.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,int(h*.8),w,h]},'top_crop':{'path':str(top.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,0,w,700]},'selected_for_start_hand':selected,'before_first_play':before,'unzoomed':unzoomed,'hand_spread':unzoomed,'observation':obs,'suitability_or_limit':limit}
    return key

def cards(names,ids): return [{'position':i+1,'name':n,'variant':None,'basis':'visible named hand slots, not deck inference','evidence_ids':ids,'limit_reason':None} for i,n in enumerate(names)]
def hand(names,ids,reason=None): return {'cards_left_to_right':cards(names,ids) if names is not None else None,'count':len(names) if names is not None else None,'basis':'direct visible hand' if names is not None else 'opponent faces hidden','evidence_ids':ids,'status':'observed' if names is not None else 'complete_with_recording_limits','limit_reason':reason}
def mon(name,hp,mx,en=0,typ=None,tool='none',pos=None,ident=None):
    return {'pokemon_id':ident,'name':name,'variant':{'Wailmer':'Wave Splash 60, printed HP100','Wailord':'Whale Pump 60+, printed HP200','Carvanha':'Sharp Fang30, printed HP50','Mega Sharpedo ex':'Turbo Shark70, printed HP190','Suicune ex':'Legendary Pulse / Crystal Waltz, printed HP140','Oricorio':'Psychic / Supernatural Feather50, HP80','Pumpkaboo':'Ram20, HP60','Gourgeist':'Soul Shot70, HP110','Greavard':'Soul Shot30, HP70','Houndstone':'Last Respects50+, printed HP130'}[name],'bench_position':pos,'hp_now':hp,'hp_max':mx,'hp_max_basis':'visible printed HP plus filmed Stage1 +30 Tool effect' if tool!='none' and name=='Houndstone' else 'visible printed HP','damage':mx-hp,'attached_energy':{'total':en,'by_type':({typ:en} if en else {})},'tool':tool,'special_conditions':[],'active_effects':([{'name':'Stage 1 +30 HP','source':tool,'expiry':'while Tool attached'}] if tool!='none' and name=='Houndstone' else []),'evidence_ids':[],'status':'observed','limit_reason':None}
def zone(typ,available): return {'this_turn':{'type':typ if available else None,'count':1 if available else 0,'available':available},'next':{'type':typ,'count':1,'available':None},'basis':'large this-turn Energy socket and smaller next-Energy icon visible; one icon is not two available attachments','evidence_ids':[],'limit_reason':'Next Energy is a preview, not a currently attachable Energy.'}
def side(active,bench,typ,available,points):
    bb=copy.deepcopy(bench)
    while len(bb)<3: bb.append({'name':None,'status':'known_empty_slot','bench_position':None})
    for i,m in enumerate(bb): m['bench_position']=i+1
    return {'active':copy.deepcopy(active),'bench_in_position_order':bb,'energy_zone':zone(typ,available),'points':points,'board_effects':[],'evidence_ids':[],'status':'observed','limit_reason':None}

w=lambda hp,en=0:mon('Wailmer',hp,100,en,'Water',ident='owner_wailmer1')
W=lambda hp,en=0:mon('Wailord',hp,200,en,'Water',ident='owner_wailmer1')
c=lambda en=0:mon('Carvanha',50,50,en,'Water',ident='owner_carvanha1')
C=lambda hp=190,en=0:mon('Mega Sharpedo ex',hp,190,en,'Water',ident='owner_carvanha1')
c2=lambda en=0:mon('Carvanha',50,50,en,'Water',ident='owner_carvanha2')
C2=lambda hp=190,en=0:mon('Mega Sharpedo ex',hp,190,en,'Water',ident='owner_carvanha2')
w2=lambda:mon('Wailmer',100,100,ident='owner_wailmer2')
W2=lambda en=0:mon('Wailord',200,200,en,'Water',ident='owner_wailmer2')
s=lambda en=0:mon('Suicune ex',140,140,en,'Water',ident='owner_suicune1')
o=lambda en=0:mon('Oricorio',80,80,en,'Psychic',ident='opponent_oricorio1')
p=lambda:mon('Pumpkaboo',60,60,ident='opponent_pumpkaboo1')
g=lambda hp=110,en=1:mon('Gourgeist',hp,110,en,'Psychic',ident='opponent_pumpkaboo1')
d=lambda en=0,tool='none':mon('Greavard',70,70,en,'Psychic',tool,ident='opponent_greavard1')
D=lambda hp=160,en=2:mon('Houndstone',hp,160,en,'Psychic','Elegant Cape',ident='opponent_greavard1')

# Final states after every turn, including resolving discards, Stadium draws/heals, KO and replacement.
states=[(w(100),[],o(),[None,p()],'none',0),
 (w(100),[c()],o(),[None,p()],'Soothing Shore',0),
 (w(50),[c()],o(1),[None,p()],'Peculiar Plaza',0),
 (W(190,1),[C()],o(1),[None,p()],'Peculiar Plaza',0),
 (W(120,1),[C()],g(),[None,o()],'Hiking Trail',0),
 (W(160,2),[C(),w2(),s()],g(),[None,o()],'Hiking Trail',0),
 (W(90,2),[C(),w2(),s()],g(),[d(1,'Elegant Cape'),o()],'Hiking Trail',0),
 (W(110,3),[C(),W2(),s()],g(),[d(1,'Elegant Cape'),o()],'Soothing Shore',0),
 (W(40,3),[C(),W2(),s()],g(),[D(),o()],'Soothing Shore',0),
 (W(100,4),[C(),W2(),s()],g(10),[D(),o()],'Soothing Shore',0),
 (C(),[None,W2(),s()],D(),[g(10,0),o()],'Soothing Shore',1),
 (C(190,1),[c2(),W2(1),s()],D(90),[g(10,0),o()],'Soothing Shore',1),
 (C(60,1),[c2(),W2(1),s()],D(120,3),[g(10,0),o()],'Soothing Shore',1),
 (C2(190,1),[C(80,1),W2(1),s(1)],D(50,3),[g(10,0),o()],'Soothing Shore',1),
 (None,[C2(190,1),W2(1),s(1)],D(50,3),[g(10,0),o()],'Soothing Shore',3)]

def board(index,turn,phase,eid,acting=None,available=False):
    a,b,oa,ob,stad,opppts=states[index]
    # Null is a filmed empty bench slot; retain its position rather than compressing it.
    ownside=side(a,[x if x is not None else {'name':None,'status':'known_empty_slot','bench_position':None} for x in b],'Water',available and acting=='owner',0)
    oppside=side(oa,[x if x is not None else {'name':None,'status':'known_empty_slot','bench_position':None} for x in ob],'Psychic',available and acting=='opponent',opppts)
    effects=[]
    if stad=='Peculiar Plaza': effects=[{'name':'Psychic retreat cost -2','source':'Peculiar Plaza','affected_player':'both','expiry':'until Stadium replaced'}]
    elif stad=='Hiking Trail': effects=[{'name':'End-turn draw until hand has3','source':'Hiking Trail','affected_player':'acting player','expiry':'until Stadium replaced'}]
    elif stad=='Soothing Shore': effects=[{'name':'End-turn heal20 for Water Pokemon with Water attached','source':'Soothing Shore','affected_player':'acting player','expiry':'until Stadium replaced'}]
    for sd in [ownside,oppside]:
        sd['evidence_ids']=[eid];sd['energy_zone']['evidence_ids']=[eid]
        for m in [sd['active']]+sd['bench_in_position_order']:
            if m is not None: m['evidence_ids']=[eid]
    return {'turn_number_displayed':turn,'phase':phase,'stadium':stad,'owner':ownside,'opponent':oppside,'shared_effects':effects,'evidence_ids':[eid]}

startnames={1:["Professor's Research",'Copycat','Poké Ball','Mega Sharpedo ex','Lucky Ice Pop'],3:['Copycat','Mega Sharpedo ex','Lucky Ice Pop','Wallace','Wailord'],5:['Copycat','Mega Sharpedo ex','Lucky Ice Pop','Wailord'],7:['Wailord','Mega Sharpedo ex','Carvanha',"Professor's Research"],9:['Mega Sharpedo ex','Carvanha','Irida','Suicune ex'],11:['Mega Sharpedo ex','Carvanha','Suicune ex'],13:['Mega Sharpedo ex','Suicune ex']}
endnames={1:['Copycat','Mega Sharpedo ex','Lucky Ice Pop','Wallace'],3:['Copycat','Mega Sharpedo ex','Lucky Ice Pop'],5:['Wailord','Mega Sharpedo ex','Carvanha'],7:['Mega Sharpedo ex','Carvanha','Irida'],9:['Mega Sharpedo ex','Carvanha','Suicune ex'],11:['Mega Sharpedo ex','Suicune ex'],13:['Suicune ex']}
fan={1:3,3:2,5:3,7:3,9:2,11:3,13:3}
# start, draw-end (None when failure), selected preplay, first move, before-end, resolved, anchor failure
timings={1:(64,67,68,71,89,92,None),2:(92,None,94,106,118,128,None),3:(128,131,132,138,175,178,None),4:(178,None,180,182,213,224,None),5:(224,227,227.5,230,283,289,None),6:(289,None,296,300,325,335,None),7:(335,337.5,337.5,338,355,360,None),8:(360,None,362,366,375,385,None),9:(385,387.5,388,392,405,415,None),10:(415,None,415,417,439,454,None),11:(454,None,455.5,456,465,476,456),12:(477,None,480,483,497,502,None),13:(503,None,503,506,515,528,503),14:(528,None,531,533,539,551,530)}

# kind, name, target, timestamp, result; exact event times are seeks/approximate observation anchors.
acts={
1:[('card_play','Poké Ball','deck',71,'Search reveals Carvanha at72.'),('card_play','Carvanha','Bench1',75,'Bench Carvanha50.'),('card_play',"Professor's Research",'deck',79,'Draw Wallace at83, then Soothing Shore at85.'),('card_play','Soothing Shore','Stadium',87,'Play Stadium; no Water Energy is attached, so no heal occurs.'),('end_turn',None,None,90,'End Turn; no available Energy on first turn.')],
2:[('energy_attachment',None,'Oricorio Active',106,'Attach1 Psychic.'),('card_play','Peculiar Plaza','Stadium',112,'Replace Soothing Shore; Psychic retreat cost2 less.'),('attack','Oricorio','Wailmer Active',120,'Supernatural Feather50; Wailmer100→50. Discard1 hand card after attack; top preview at128 is Klefki, confirmed in rotated native crop.')],
3:[('card_play','Wallace','Carvanha Bench1',139,'Random deck evolution is Mega Sharpedo ex at142; hand copy of Mega Sharpedo remains.'),('card_play','Lucky Ice Pop','Wailmer Active',153,'Heal20:50→70. Heads at158; card returns to hand.'),('evolution','Wailord','Wailmer Active',161,'Evolve manually from hand; damage30 carries over,170 HP.'),('card_play','Lucky Ice Pop','Wailord Active',166,'Heal20:170→190. Heads at172; same card returns to hand.'),('energy_attachment',None,'Wailord Active',174,'Attach1 Water, total1.'),('end_turn',None,None,177,'End Turn with three cards.')],
4:[('card_play',"Professor's Research",'deck',182,'Opponent draws2 hidden cards.'),('evolution','Gourgeist','Pumpkaboo Bench2',191,'Evolve into Gourgeist110.'),('card_play','Hiking Trail','Stadium',198,'Replace Peculiar Plaza.'),('energy_attachment',None,'Gourgeist Bench2',204,'Attach1 Psychic.'),('retreat',None,'Oricorio→Gourgeist',212,'Pay1 Psychic from Oricorio; Gourgeist moves Active, Oricorio takes vacated Bench2.'),('attack','Gourgeist','Wailord Active',214,'Soul Shot70:190→120; discard1 hand card. Hiking Trail replenishes opponent hand to3.')],
5:[('card_play','Lucky Ice Pop','Wailord Active',230,'Heal20:120→140. Heads at236; returns.'),('card_play','Lucky Ice Pop','Wailord Active',241,'Heal20:140→160. Tails at244; card discarded.'),('card_play','Copycat','hand/deck',250,'Shuffle remaining Mega Sharpedo ex and Wailord into deck; draw3 matching opponent fan: Wailord252, Suicune ex256, Poké Ball258.'),('card_play','Poké Ball','deck',260,'Find Wailmer262.'),('card_play','Wailmer','Bench2',265,'Bench Wailmer100.'),('card_play','Suicune ex','Bench3',269,'Bench Suicune ex140. Legendary Pulse does not activate from Bench.'),('energy_attachment',None,'Wailord Active',274,'Attach1 Water, total2.'),('end_turn',None,None,283,'End with Wailord1 card before automatic Hiking Trail. Draw Mega Sharpedo ex285/286 and Carvanha287; ending hand3.')],
6:[('card_play','Poké Ball','deck',300,'Opponent random Basic search; found identity hidden.'),('card_play','Poké Ball','deck',306,'Second opponent random Basic search; identity hidden.'),('card_play','Greavard','Bench1',313,'Bench Greavard70, Oricorio remains Bench2.'),('energy_attachment',None,'Greavard Bench1',316,'Attach1 Psychic.'),('card_play','Elegant Cape','Greavard Bench1',319,'Attach Tool; Basic HP remains70, Stage1 gains30 when evolved.'),('attack','Gourgeist','Wailord Active',326,'Soul Shot70:160→90; discard1 hand card. Hiking Trail replenishes to3.')],
7:[('evolution','Wailord','Wailmer Bench2',339,'Evolve second Wailmer into Wailord200.'),('card_play',"Professor's Research",'deck',342,'Draw Soothing Shore344 then Irida346. Irida remains in hand.'),('card_play','Soothing Shore','Stadium',350,'Replace Hiking Trail.'),('energy_attachment',None,'Wailord Active',352,'Attach1 Water, total3.'),('end_turn',None,None,355,'End Turn; Soothing Shore heals20:90→110 at357. Hand3.')],
8:[('evolution','Houndstone','Greavard Bench1',366,'Evolve Houndstone printed130; Elegant Cape raises effective maximum/current HP to160.'),('energy_attachment',None,'Houndstone Bench1',374,'Attach1 Psychic, total2.'),('attack','Gourgeist','Wailord Active',376,'Soul Shot70:110→40; discard1 hand card. No Stadium refill, since Hiking Trail was replaced.')],
9:[('energy_attachment',None,'Wailord Active',394,'Attach1 Water, total4.'),('card_play','Irida','Water board',400,'Heal40 from damaged Water Pokemon: Wailord40→80; undamaged Bench does not gain excess HP.'),('attack','Wailord','Gourgeist Active',407,'Whale Pump100:110→10; ending Shore heals20:80→100.')],
10:[('energy_attachment',None,'Gourgeist Active',417,'Attach1 Psychic, total2.'),('retreat',None,'Gourgeist→Houndstone',433,'Pay2 Psychic from Gourgeist; Houndstone moves Active. Gourgeist Bench1 now has0.'),('attack','Houndstone','Wailord Active',440,'Last Respects130 knocks out100-HP Wailord at444; opponent gains1 point. Owner replacement prompt selects Mega Sharpedo ex at451.')],
11:[('card_play','Carvanha','Bench1',456.5,'Bench second Carvanha50.'),('energy_attachment',None,'Mega Sharpedo ex Active',460,'Attach1 Water.'),('attack','Mega Sharpedo ex','Houndstone Active',467,'Turbo Shark70:160→90; nested Energy destination prompt at472-475 selects Wailord Bench2, attach1 Water resolved at476. Carvanha remains at0 Energy.')],
12:[('card_play','Pokémon Center Lady','Houndstone Active',483,'Heal30:90→120; no condition removed because none was present.'),('energy_attachment',None,'Houndstone Active',492,'Attach1 Psychic, total3.'),('attack','Houndstone','Mega Sharpedo ex Active',498,'Last Respects130:190→60; no knockout.')],
13:[('evolution','Mega Sharpedo ex','Carvanha Bench1',506,'Evolve second Carvanha; it has0 Water.'),('retreat',None,'damaged Mega Sharpedo→fresh Mega Sharpedo',509,'Free retreat; pay0 Energy. Damaged Sharpedo60 with1 Water moves Bench1; fresh Active has0 Water.'),('energy_attachment',None,'fresh Mega Sharpedo ex Active',515,'Normal turn Water attachment, total1. Destination selected at514 and resolved by515.'),('attack','Mega Sharpedo ex','Houndstone Active',518,'Turbo Shark70:120→50. Attack effect attaches1 Water to Suicune ex Bench3 at523. Damaged Sharpedo keeps its1 Water; Soothing Shore heals that Benched Sharpedo60→80.')],
14:[('card_play','Cyrus','damaged Mega Sharpedo ex Bench1',533,'Force damaged80-HP Mega Sharpedo Active; fresh190-HP Sharpedo takes vacated Bench1.'),('attack','Houndstone','Mega Sharpedo ex Active',541,'Last Respects130 knocks out80-HP Mega Sharpedo; +3 points banner548, displayed total caps at3; Defeat550.')]
}

draws={1:[('normal_draw',None,None,66,['Lucky Ice Pop'],[66]),('search','Poké Ball',1,72,['Carvanha'],[72]),('supporter_draw',"Professor's Research",3,83,['Wallace','Soothing Shore'],[83,85])],3:[('normal_draw',None,None,130,['Wailord'],[130]),('deck_evolution','Wallace',1,142,['Mega Sharpedo ex'],[142])],5:[('normal_draw',None,None,226,['Wailord'],[226]),('supporter_draw','Copycat',3,252,['Wailord','Suicune ex','Poké Ball'],[252,256,258]),('search','Poké Ball',4,262,['Wailmer'],[262]),('automatic_draw','Hiking Trail',None,285,['Mega Sharpedo ex','Carvanha'],[285,287])],7:[('normal_draw',None,None,336,['Professor\'s Research'],[336]),('supporter_draw',"Professor's Research",2,344,['Soothing Shore','Irida'],[344,346])],9:[('normal_draw',None,None,386,['Suicune ex'],[386])],11:[('normal_draw_failed',None,None,455.5,[],[])],13:[('normal_draw_failed',None,None,504,[],[])]}
action_hand_counts={1:[5,4,5,4,4],3:[4,4,3,3,3,3],5:[4,3,3,3,2,1,1,3],7:[3,4,3,3,3],9:[4,3,3],11:[2,2,2],13:[1,1,1,1]}
draw_hand_counts={1:[(4,5),(4,5),(3,5)],3:[(4,5),(4,4)],5:[(3,4),(2,3),(2,3),(1,3)],7:[(3,4),(2,4)],9:[(3,4)],11:[(3,3)],13:[(2,2)]}

turns=[]
for n in range(1,15):
    owner=n%2==1; who='owner' if owner else 'opponent'; start,de,selected,first,pre,end,failure=timings[n]
    chosen=frame(selected,'selected_preplay_hand' if owner else 'opponent_turn_boundary',n,'Named hand and both boards before first play.' if owner else 'Opponent hand identities hidden.',selected=owner,before=(selected<first),unzoomed=True)
    after=frame(end,'after_resolution_board',n,'Both boards after ending action and all recorded effects resolve.')
    preid=frame(pre,'before_end_hand_or_attack_substitution',n,'Last clear hand before End Turn or attack; end-state board is captured separately.')
    candidates=[]
    if owner and de is not None:
        # Stored approximate offsets measured against the first settled draw frame.
        tt={1:[68,70,73],3:[132,134,137],5:[228,230,233],7:[338.5,340.5,343.5],9:[389,391,393]}[n]
        for t in tt:
            candidates.append(frame(t,'draw_relative_candidate',n,draw=de,offset=t-de,before=t<first,unzoomed=(t not in [134,228,230,338.5,340.5,343.5]),limit=('Already playing or inspecting a card; dense settled frame selected instead.' if t>=first or t in [134,228] else 'Clear candidate before first voluntary play.')))
    elif owner:
        for t in ({11:[457,459,462],13:[504,506,509]}[n]):
            candidates.append(frame(t,'failed_draw_relative_candidate',n,obs='No normal card draw exists: deck-empty message anchors these diagnostic candidates.',before=t<first,unzoomed=False,limit='Not a valid normal-draw offset; draw timestamp remains null. Pre-play hand retained before first play.'))
    plays=[]
    for order,(kind,name,target,t,result) in enumerate(acts[n],1):
        eid=frame(t,'numbered_action',n,result)
        rec={'order':order,'kind':kind,'card_name':name,'target':target,'energy':None,'result':result,'prompt_text':None,'response':None,'nested_events_in_order':[],'hand_count_after':None,'source_video':VIDEO,'timestamp_seconds':t,'evidence_ids':[eid],'basis':'filmed action/state change','limit_reason':None}
        if owner: rec['hand_count_after']=action_hand_counts[n][order-1]
        if kind=='energy_attachment': rec['energy']={'type':'Water' if owner else 'Psychic','count':1,'destination':target,'retreat_payment_by_type':None}
        if kind=='retreat': rec['energy']={'type':None,'count':None,'destination':None,'retreat_payment_by_type':{'Psychic':1 if n==4 else 2} if n in [4,10] else {}}
        if n in [11,13] and kind=='attack':
            t2=476 if n==11 else 523
            rec['nested_events_in_order']=[{'order':1,'kind':'energy_destination_prompt','choice':'Wailord Bench2' if n==11 else 'Suicune ex Bench3','energy_type':'Water','count':1,'timestamp_seconds':t2,'evidence_ids':[frame(t2,'attack_nested_energy',n)]}]
        if n==10 and kind=='attack': rec['nested_events_in_order']=[{'order':1,'kind':'knockout','target':'Wailord','points':1,'timestamp_seconds':444,'evidence_ids':[frame(444,'knockout',n)]},{'order':2,'kind':'replacement_choice','choice':'Mega Sharpedo ex','timestamp_seconds':451,'evidence_ids':[frame(451,'replacement',n)]}]
        plays.append(rec)
    dd=[]
    for kind,caused,order,t,names,ts in draws.get(n,[]):
        ids=[frame(x,'draw_or_search_reveal',n) for x in ts]
        dd.append({'kind':kind,'caused_by':caused,'linked_play_order':order,'cards_in_reveal_order':[{'name':name,'reveal_position':i+1,'source_video':VIDEO,'timestamp_seconds':ts[i],'evidence_ids':[ids[i]],'basis':'visible named reveal','limit_reason':None} for i,name in enumerate(names)],'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':(['Mega Sharpedo ex','Wailord'] if caused=='Copycat' else None),'source_video':VIDEO,'timestamp_seconds':t,'evidence_ids':ids if ids else [frame(t,'failed_draw_message',n)],'limit_reason':'Deck empty; normal draw yields zero cards.' if kind=='normal_draw_failed' else None})
    if not owner:
        dd.append({'kind':'normal_draw' if n!=14 else 'normal_draw_failed','caused_by':None,'linked_play_order':None,'cards_in_reveal_order':None if n!=14 else [],'card_count':1 if n!=14 else 0,'source_video':VIDEO,'timestamp_seconds':start,'evidence_ids':[chosen],'limit_reason':'Opponent card faces remain hidden.' if n!=14 else 'No cards left in deck message at530.'})
        for pl in plays:
            if pl['card_name'] in ['Poké Ball',"Professor's Research"]:
                dd.append({'kind':'search' if pl['card_name']=='Poké Ball' else 'supporter_draw','caused_by':pl['card_name'],'linked_play_order':pl['order'],'cards_in_reveal_order':None,'card_count':1 if pl['card_name']=='Poké Ball' else 2,'source_video':VIDEO,'timestamp_seconds':pl['timestamp_seconds'],'evidence_ids':pl['evidence_ids'],'limit_reason':'Opponent found/drawn cards are not revealed face-up.'})
    else:
        for drawrow,counts in zip(dd,draw_hand_counts[n]):
            drawrow['hand_count_before'],drawrow['hand_count_after']=counts
            drawrow['hand_count_basis']='Visible hand plus public card transactions; counts after search/Supporter include resolved draws. Wallace evolution goes directly to Bench and adds no hand card.'
    bs=board(n-1,n,'post-draw/pre-first-play (failure message when deck empty)',chosen,who,n!=1)
    ba=board(n,n,'after attack/discard/KO/replacement and Stadium resolution',after,who,n==14)
    # T14 Cyrus places healthy Sharpedo into Bench1 before damaged Sharpedo knockout.
    if n==14:
        ba['owner']['active']=None
        terminalids=[frame(544,'terminal_board_after_knockout',n),frame(548,'terminal_points_banner',n),result_id if 'result_id' in globals() else frame(557,'result_screen',n)]
        ba['evidence_ids']+=terminalids
        for sd in [ba['owner'],ba['opponent']]:
            sd['evidence_ids']+=terminalids
            sd['energy_zone']['evidence_ids']=[terminalids[0]]
            for m in [sd['active']]+sd['bench_in_position_order']:
                if m is not None: m['evidence_ids']=[terminalids[0]]
    row={'turn_number':n,'who_played':who,'source_video':VIDEO,'timing':{'turn_start_seconds':start,'draw_animation_end_seconds':de,'draw_end_basis':'first observed settled draw frame, approximate within0.5 seconds' if de else 'no owner normal draw was possible' if owner else 'opponent hidden draw not timed as owner hand capture','normal_draw_failure_anchor_seconds':failure,'first_voluntary_move_seconds':first,'before_end_action_seconds':pre,'end_after_resolution_seconds':end},'hand_at_start':hand(startnames[n],[chosen]) if owner else hand(None,[chosen],'Opponent card faces are hidden throughout normal draws.'),'owner_hand_start':hand(startnames[n],[chosen]) if owner else hand(None,[], 'Owner pre-turn identities are carried by previous owner-turn ending record; no opponent-turn hand-by-name requirement.'),'opponent_hand_at_owner_turn_start':{'count':fan.get(n),'supported_range':None,'count_method':'Count separate visible card backs and fan edges in retained native top crop','basis':'direct visual count' if owner else 'not applicable: opponent turn','evidence_ids':[chosen] if owner else [],'limit_reason':None if owner else 'Only required at owner-turn start.'},'draws_and_searches':dd,'plays_in_order':plays,'automatic_events_in_order':[],'board_at_start':bs,'board_after':ba,'owner_hand_end':hand(endnames[n],[after]) if owner else hand(None,[],'Not an owner turn; previous/next owner hand records retain named identities.'),'owner_hand_before_end_action':hand(['Wailord'],[preid]) if n==5 else hand(endnames[n],[preid]) if owner else None,'discard_snapshot_ids':[],'turn_evidence_ids':[chosen,preid,after]+candidates,'limits':['Action timestamps are source-local seek anchors, not measured exact transition frames.']}
    if n==5: row['automatic_events_in_order']=[{'order':1,'source':'Hiking Trail','event':'Draw until hand3: Mega Sharpedo ex then Carvanha','timestamp_seconds':285,'evidence_ids':[frame(285,'automatic_draw',n),frame(287,'automatic_draw',n)]}]
    if n in [7,9,13]: row['automatic_events_in_order']=[{'order':1,'source':'Soothing Shore','event':'Heal20 from Water Pokemon with Water attached at end of owner turn','target':'Wailord Active' if n!=13 else 'damaged Mega Sharpedo ex Bench1','timestamp_seconds':357 if n==7 else 411 if n==9 else 526,'evidence_ids':[frame(357 if n==7 else 411 if n==9 else 526,'stadium_heal',n)]}]
    if n in [2,4,6,8]: row['automatic_events_in_order'].append({'order':1,'source':'attack requirement','event':'Discard1 opponent hand card after attack selection. New top pile preview is '+{2:'Klefki',4:'Houndstone',6:'Pumpkaboo',8:'Gourgeist'}[n]+'.','evidence_ids':[after],'identity_limit':'These four filmed Psychic Pokemon discards are consistent with Last Respects130; no opened full pile scroll was recorded.'})
    turns.append(row)

opening_id=frame(32,'five_card_opening',obs='Five original hand slots before Active placement, with Wailmer atposition2.',unzoomed=True)
active_id=frame(36,'opening_active_selection',obs='Wailmer selected as Active.')
result_id=frame(557,'result_screen',obs='Defeat versus Garfield.tv; went first;14 turns; owner0/opponent3; damage240.')
qr=json.loads((P/'QR_DECODE.json').read_text())
filmed=[]
for card in qr['cards']:
    filmed.extend([{'name':card['name'],'semantic_entity_id':card['entity_id'],'functional_ids':card['functional_ids'],'printing_limit':card['printing_limit']}] * card['count'])
deck={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':GAME,'sources':BIND,'deck_name_in_log':None,'filmed_deck_name':'New deck 6','descriptive_filmed_deck_name':'Wailord / Mega Sharpedo ex / Suicune ex','source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','captured_at':json.loads((P.parent/'LIVE_DECK_SNAPSHOT.json').read_text())['retrieved_utc'],'log_list_version':None,'expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':None,'energy_configuration_from_log':None,'actual_card_count':None,'capture_source_text_or_image':'../LIVE_DECK_SNAPSHOT.json','game_version_binding_basis':'Filmed New deck6 QR at6 seconds, followed by selection of same deck at8-10 seconds and gameplay matching core. QR confirms20 semantic card slots and Water, not exact art printings. None of nine named live-log lists matches this QR.','conflicts_with_filmed_cards':['Draft A Shark Tempo has Alolan Vulpix/Ninetales/Lapras in place of Wailmer/Wailord/Suicune and different Trainers; Wailord Indeedee wall contains Indeedee and different Trainers. Neither is this deck.'],'exact_list_status':'filmed_exact_semantic_QR_verified_but_matching_live_log_list_unavailable','filmed_cards_20_slots':filmed,'filmed_counts':[{k:c[k] for k in ['name','count','entity_kind','entity_id','functional_ids']} for c in qr['cards']],'filmed_energy_configuration':['Water'],'filmed_QR_receipt':'QR_DECODE.json','filmed_QR_native_image':'QR_NATIVE_t6.png','limits':['Requested exact dated log snapshot could not be bound because all nine current log lists differ from the film. Do not substitute another deck list or infer hidden cards from this QR.']}
limits=['Neither player opens a full discard pile. Only changing top-card pile previews and visible attack discards are filmed; periodic full-pile snapshots are unavailable.','Opponent normal draws and both Poké Ball finds are concealed. No hidden identities inferred.','Owner first plays on turns5 and7 occur during or before scheduled+1 candidate; dense settled pre-play frames227.5 and337.5 preserve the starting hand.','Turns11 and13 have deck-empty normal-draw failures, so draw-animation end is null and diagnostic candidates use the failure message anchor instead.','The exact filmed QR deck is absent from all nine current Pause Games log lists. DECK_USED retains the conflict and filmed20-slot semantic list separately.','All source-local timestamps are requested seeks. Exact decoded presentation timestamps were not measured.','No visible supporter-warning decline or zero-effect voluntary card play occurs. Card inspection zooms are not counted as plays.']
pause={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':GAME,'review_date':NOW,'sources':BIND,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','classification':'human_event_battle','mode':'Deluxe Pack: Mega Emblem Event','auto_control_visible':False,'match_date':'2026-10-04','match_date_basis':'RECORDING_METADATA.json embedded UTC2026-10-05T00:35:47Z converts to America/Chicago October4 19:35:47','deck_name':'New deck 6 (Wailord / Mega Sharpedo ex / Suicune ex)','opening':{'source_video':VIDEO,'timestamp_seconds':32,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':cards(["Professor's Research",'Wailmer','Copycat','Poké Ball','Mega Sharpedo ex'],[opening_id]),'selected_active':{'name':'Wailmer','opening_position':2,'source_video':VIDEO,'timestamp_seconds':36,'evidence_ids':[active_id]},'redraw_or_replacement':None,'redraw_or_replacement_limit':'No setup redraw shown.','before_active_placement':True,'status':'observed','evidence_ids':[opening_id,active_id],'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'full_source_review_submitted_for_independent_acceptance','outcome':{'owner':'loss','opponent':'Garfield.tv','owner_points':0,'opponent_points':3,'turns_played':14,'damage_done':240,'evidence_ids':[result_id]},'limits':limits,'lead_checked':False}
discards=[]
for n in [3,7,9,13]:
    for player in ['owner','opponent']:
        previewname=({3:'Soothing Shore',7:'Poké Ball',9:"Professor's Research",13:'Wailord'} if player=='owner' else {3:'Klefki',7:'Pumpkaboo',9:'Gourgeist',13:'Pokémon Center Lady'})[n]
        sid=f'discard_{player}_turn{n}_partial'
        discards.append({'snapshot_id':sid,'turn_number':n,'pile_owner':player,'source_video':VIDEO,'timestamp_seconds':timings[n][2],'cards_in_view':[{'name':previewname,'basis':'only filmed top pile preview'}],'scroll_coverage':'No opened discard pile or scroll shown.','full_pile_established':False,'evidence_ids':[frame(timings[n][2],'periodic_discard_availability_check',n)],'limit_reason':'Only top preview available; contents beneath it are not identified.'})
        turns[n-1]['discard_snapshot_ids'].append(sid)
for n,name in [(2,'Klefki'),(4,'Houndstone'),(6,'Pumpkaboo'),(8,'Gourgeist')]:
    sid=f'discard_opponent_turn{n}_attack_preview'
    discards.append({'snapshot_id':sid,'turn_number':n,'pile_owner':'opponent','source_video':VIDEO,'timestamp_seconds':timings[n][5],'cards_in_view':[{'name':name,'basis':'new filmed top discard preview after attack'}],'scroll_coverage':'Top preview only','full_pile_established':False,'evidence_ids':[frame(timings[n][5],'attack_discard_preview',n)],'limit_reason':'Contents beneath the newly discarded card are not opened.'})
    turns[n-1]['discard_snapshot_ids'].append(sid)
for file,obj in [('DECK_USED.json',deck),('PAUSE_GAME.json',pause),('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':GAME,'sources':BIND,'turns':turns,'limits':limits}),('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':GAME,'sources':BIND,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':.2,'top_crop_bounds':[0,0,1170,700],'fixed_grid_is_turn_start_evidence':False},'frames':list(evidence.values()),'discard_snapshots':discards,'scheduled_capture_limits':limits}),('SUMMARY.json',{'source_video':VIDEO,'source_sha256':SHA,'reviewer':'/root/pause_003547','model':'Sol','review_date':NOW,'game_count':1,'turn_count':14,'classification':'human_event_battle','mode':'Deluxe Pack: Mega Emblem Event','opponent':'Garfield.tv','match_date':'2026-10-04','deck_core':['Wailmer','Wailord','Carvanha','Mega Sharpedo ex','Suicune ex'],'outcome':'loss','owner_points':0,'opponent_points':3,'source_coverage_seconds':[0,558.038333],'continuity':'No observed cuts; continuous setup-through-result footage.','packet_status':'submitted_for_independent_acceptance','capture_status':'complete_with_recording_limits','critical_ambiguity':'No matching live-log deck list, despite fully decoded filmed QR.','result_evidence':[result_id]}),('UNCERTAINTIES.json',{'source_video':VIDEO,'source_sha256':SHA,'items':[{'type':'recording_or_destination_limit','description':x} for x in limits],'unreviewed_intervals':[],'consequential_question_for_independent_review':'Verify attack-retreat-Energy transitions and terminal Cyrus/Last Respects130. Deck log binding requires a separate exact filmed-version list, not substituting an existing live deck.'})]:
    (P/file).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lines=['# Full recording review:20261005_003547000_iOS.MP4','',f'Reviewer: /root/pause_003547. Reviewed {NOW}. Source SHA-256: `{SHA}`. Frozen source identity is in SOURCE.json. Embedded metadata gives the local match date October4,2026 at7:35:47p.m. Central; filename clock is UTC.','', 'One continuous human Deluxe Pack: Mega Emblem Event match, Dacz8976 versus Garfield.tv. The owner went first. No Auto control is visible. Setup, all14 turns, terminal knockout, Defeat banner and result screen are reviewed. Result: owner0 points, opponent3; damage done240. The +3 Mega knockout is awarded after opponent already has1; the displayed win total caps at3.','', 'The filmed deck is New deck6: Wailord, Mega Sharpedo ex and Suicune ex, Water. QR_NATIVE_t6.png and QR_DECODE.json confirm20 semantic slots. None of nine current log lists matches it; DECK_USED.json preserves the exact filmed list without substituting Draft A or the Indeedee wall list. No cards are identified from deck membership.','', '## Setup and coverage','', '0–10s: deck selection/editor, QR6s, same New deck6 selected for battle. 12–30s: matchmaking, Garfield.tv reveal, battle transition. 32s: five original cards left-to-right are Professor’s Research, Wailmer, Copycat, Poké Ball, Mega Sharpedo ex. Wailmer is selected Active36s. 38–58s: owner waits for opponent setup. 60–62s: Oricorio Active and Pumpkaboo Bench2 are revealed. Owner board is Wailmer100, empty Bench. 64s: owner turn1.','', '## Turn table','', '|Turn|Player|Source seconds|Named starting hand or hidden status|Ending owner hand|','|---|---|---|---|---|']
for row in turns:
    n=row['turn_number'];start,end=timings[n][0],timings[n][5]
    lines.append(f'|{n}|{row["who_played"]}|{start}–{end}|'+(', '.join(startnames[n]) if n%2 else 'Opponent identities hidden')+'|'+(', '.join(endnames[n])+f' ({len(endnames[n])})' if n%2 else 'See adjacent owner turns')+'|')
lines+=['','The ledger preserves both complete boards and Energy Zones before and after each turn, including empty Bench1 after first Wailord knockout. Each turn below corresponds to the identically numbered TURN_LEDGER.json row. Native frames and unscaled bottom-fifth/top crops are indexed in TURN_EVIDENCE.json.','']
for n in range(1,15):
    lines.append(f'## Turn{n}: '+('owner' if n%2 else 'opponent'))
    if n%2: lines.append(f'\nPre-play hand frame {timings[n][2]}s; opponent fan visually counted {fan[n]}. Normal draw: '+('no card because deck empty.' if n in [11,13] else draws[n][0][4][0]+'.'))
    lines.append('')
    for i,(kind,name,target,t,result) in enumerate(acts[n],1): lines.append(f'{i}. {t}s: '+(name+'; ' if name else '')+result)
    lines.append('')
lines+=['## Consequential observations','', 'Wallace turn3 evolves the benched Carvanha directly from the deck. The existing Mega Sharpedo hand card stays in hand. The two turn3 Lucky Ice Pop flips are both heads; turn5 repeats the same card with heads, then tails. Copycat turn5 shuffles the remaining two cards before drawing exactly three named cards. Hiking Trail then fills the one-card ending hand with Mega Sharpedo ex and Carvanha. Suicune stays Benched throughout and its Active-only Legendary Pulse does not supply these draws.','', 'The first Wailord reaches four Water Energy and uses Whale Pump100 once on turn9. Houndstone, with Elegant Cape, has160 effective maximum HP. Its filmed Last Respects130 knocks out Wailord on turn10, damages the first Mega Sharpedo to60 on turn12, and knocks that same damaged Pokémon out after Cyrus on turn14. Free retreat on turn13 preserves the damaged Pokémon’s Energy; Soothing Shore heals it to80. Turn11 Turbo Shark attaches1 Water to Wailord Bench2, leaving Carvanha at0. On turn13 the fresh evolved Sharpedo becomes Active with0 Water, receives the normal Water attachment at514-515s, and Turbo Shark then attaches1 Water to Suicune Bench3 at523s. Both Sharpedo retain exactly1 Water. Those steps leave it as a visible Cyrus target. No win/loss-based claim about strategic quality is made.','', '## Capture limits','']+['- '+x for x in limits]+['','Full source review is submitted; independent acceptance and external registration remain with the lead. Original source and SOURCE.json were preserved. No external logs, shared index/events, simulator files or archive locations were changed.']
(P/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
cov=['# Coverage','',f'Source: {VIDEO}; SHA-256 `{SHA}`. One game, all14 turns.','', '- [x]0–32s: deck/QR, matchmaking and initial deal','- [x]32–64s: original five cards, selected Active, opponent setup reveal']
for n in range(1,15): cov.append(f'- [x]Turn{n}, {timings[n][0]}–{timings[n][5]}s: actions, draws/searches, full board transitions, result of ending action')
cov+=['- [x]541–551s: terminal Cyrus target, Last Respects130, Mega knockout, +3 banner, Defeat','- [x]552–558.038333s: result transition and explicit14-turn0–3 result','', 'Review method: two-second native source sequence with targeted0.5/1-second rechecks at draws, searches, coin outcomes, evolution/retreat/Energy interactions and terminal sequence. Selected draw-relative frames are separate from overview sampling. No unreviewed intervals. Discard UI and current-log deck mismatch are explicit capture limits. Lead acceptance is still pending.']
(P/'COVERAGE.md').write_text('\n'.join(cov)+'\n',encoding='utf-8')
(P/'CHECKPOINT.md').write_text('Full-source review and structured packet submitted for independent acceptance. All14 turns and ending covered. Files: REVIEW.md, COVERAGE.md, SUMMARY.json, UNCERTAINTIES.json, PAUSE_GAME.json, DECK_USED.json, TURN_LEDGER.json, TURN_EVIDENCE.json, retained turn_evidence and QR PNG/receipt. Exact live-log deck mismatch unresolved; original remains unmoved.\n',encoding='utf-8')
print(json.dumps({'turns':len(turns),'evidence_frames':len(evidence),'capture_status':pause['capture_status'],'packet':str(P)}))
