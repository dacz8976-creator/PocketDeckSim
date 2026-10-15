"""Author source-bound review data; never modifies source or shared records."""
import json, re, copy, hashlib
from pathlib import Path
from PIL import Image

P=Path(__file__).resolve().parent
S=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
V=S['video_basename']; H=S['sha256']; G=P.name
def save(name,value):
    (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t): return 'f_'+f'{t:07.2f}'.replace('.','_')
def refs(*times): return [eid(t) for t in times]
sources=[{'video_basename':V,'sha256':H,'source_json':'SOURCE.json'}]
base={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources}
D='Doublade'; A='Aegislash (Cursed Metal / Slicing Blade)'; AS='Aegislash (Superb Shield)'
L='Lucky Ice Pop'; R='Rare Candy'; PR='Professor’s Research'; PB='Poké Ball'; M='Metal Core Barrier (gold artwork)'; MN='Metal Core Barrier (ordinary artwork)'; HO='Honedge'; O='Orthworm'
SG='Skarmory ex (green artwork)'; SS='Skarmory ex (silver artwork)'; ML='Mega Lucario ex (red/blue attack artwork)'; ML2='Mega Lucario ex (alternate artwork)'; HI='Hitmonlee'; RI='Riolu'; MA='Marshadow'
opening=[D,SG,A,L,SS]
hand0=[D,A,L]; h1=hand0+[R]; h3=h1+[HO]; h5=h1+[PR]; e5=[A,L,R,PR]; h7=e5+[M]; e7=[L,R,M,MN,HO]; h9=e7+[AS]; e9=[R,MN,AS]
native={}
for path in (P/'turn_evidence').glob('t*.jpg'):
    if not re.fullmatch(r't\d+\.\d+',path.stem): continue
    t=float(path.stem[1:]); native[t]=path
frames=[]
for t,path in sorted(native.items()):
    with Image.open(path) as im:
        bottom=path.with_name(path.stem+'_hand.png'); top=path.with_name(path.stem+'_top.png')
        if not bottom.exists(): im.crop((0,2025,1170,2532)).save(bottom)
        if not top.exists(): im.crop((0,0,1170,520)).save(top)
    frames.append({'evidence_id':eid(t),'source_video':V,'source_sha256':H,'timestamp_seconds':t,
        'requested_seek_seconds':t,'actual_frame_pts_seconds':None,'pts_limit':'Requested source-local seek; exact decoded PTS was not measured.',
        'native_dimensions':[1170,2532],'full_frame_path':str(path.relative_to(P)).replace('\\','/'),
        'bottom_crop':{'path':str(bottom.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},
        'top_crop':{'path':str(top.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,520]},
        'role':'Native event/context frame; hand selection suitability separately recorded below.'})
qrpath=P/'qr_intake/t0001.00.png'
with Image.open(qrpath) as im:
    im.crop((0,2025,1170,2532)).save(P/'qr_intake/t0001.00_hand.png'); im.crop((0,0,1170,520)).save(P/'qr_intake/t0001.00_top.png')
frames.append({'evidence_id':'qr_0001_00','source_video':V,'source_sha256':H,'timestamp_seconds':1.0,'requested_seek_seconds':1.0,'actual_frame_pts_seconds':None,'native_dimensions':[1170,2532],'full_frame_path':'qr_intake/t0001.00.png','bottom_crop':{'path':'qr_intake/t0001.00_hand.png','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':'qr_intake/t0001.00_top.png','pixel_bounds_x0_y0_x1_y1':[0,0,1170,520]},'role':'Retained native filmed QR, decode receipt in qr_intake.'})

captures=[]
for n,draw,selected,before,candidates,reasons,input_bounds in [
 (1,42.8,42.8,43.5,[44,46,49],['Next-turn banner already displayed','Opponent turn has begun','Opponent turn has begun'],[43.5,44]),
 (3,81.5,81.5,88,[82.5,84.5,87.5],['Honedge has left the hand','Honedge already benched','After bench play and Energy attachment'],[81.5,82]),
 (5,131.5,131.5,152,[132.5,134.5,137.5],['Aegislash inspection zoom obstructs intact fan','After Doublade evolution input','After Research play; reveal animation'],[132,132.5]),
 (7,232.8,232.8,257,[233.8,235.8,238.8],['Aegislash has left hand for evolution','Evolution/Ability resolution after first play','After evolution, before further play'],[233.2,233.5]),
 (9,310.8,310.8,344.2,[311.8,313.8,316.8],['Honedge inspection zoom obstructs full fan','Honedge already played to bench','Lucky Ice Pop has left hand'],[311.2,311.8])]:
    captures.append({'turn_number':n,'draw_animation_end_seconds':draw,'draw_end_basis':'End of draw travel into visible owner fan, bounded by reveal and following native frames; approximate source seek.',
        'scheduled_candidates':[{'offset_seconds':round(t-draw,2),'requested_seconds':t,'evidence_ids':refs(t),'suitable_for_intact_start_hand':False,'rejection_reason':reason} for t,reason in zip(candidates,reasons)],
        'selected_start_hand':{'timestamp_seconds':selected,'evidence_ids':refs(selected),'intact_before_first_input':True,'unzoomed':True,'inspection_basis':'Full native frame inspected. All listed starting cards remain in the fan; no played card is absent. Later input frames checked separately.'},
        'first_input_bounds_seconds':input_bounds,'first_card_consuming_input_bounds_seconds':{1:None,3:[81.5,82],5:[133,134],7:[233.2,234],9:[312,312.5]}[n],
        'before_end_action':{'timestamp_seconds':before,'evidence_ids':refs(before),'unzoomed':True,'purpose':'Complete remaining fan before End Turn or attack. Turn 5 uses last stable full board before attack menu; turn 9 has Energy attachment highlight but all three cards visible.'}})

def hand(cards,t,basis='Visible native owner fan and preceding reveal order'):
    return {'cards_left_to_right':[{'position':i+1,'name':x,'basis':basis,'evidence_ids':refs(t),'limit_reason':None} for i,x in enumerate(cards)],'count':len(cards),'basis':basis,'evidence_ids':refs(t),'status':'observed','limit_reason':None}
def hidden_hand(count,t):
    return {'cards_left_to_right':[{'position':i+1,'name':None,'basis':'Visible card back','evidence_ids':refs(t),'limit_reason':'Opponent face is hidden'} for i in range(count)],'count':count,'basis':'Visible opponent fan; no identities inferred','evidence_ids':refs(t),'status':'complete_with_hidden_identities','limit_reason':'Card backs do not establish names'}
def pokemon(name,hp,maxhp,energy=0,etype='Metal',tool=None,effects=None):
    if name is None:return {'name':None,'status':'visibly_empty','hp_now':None,'hp_max':None,'damage':None,'attached_energy':{'total':0,'by_type':{}},'tool':None,'special_conditions':[],'active_effects':[],'limit_reason':'Empty slot, not a hidden Pokémon'}
    return {'name':name.split(' (')[0],'variant':name.split(' (')[1][:-1] if ' (' in name else 'Filmed variant; exact printing not catalog-matched','hp_now':hp,'hp_max':maxhp,'hp_max_basis':'Visible printed HP; no HP modifier observed','damage':maxhp-hp,'attached_energy':{'total':energy,'by_type':{etype:energy} if energy else {}},'tool':tool,'special_conditions':[],'active_effects':effects or [],'status':'observed','limit_reason':'Art description identifies visible instance, not rarity/catalog printing.'}
def own(name,hp,maxhp,e=0,tool=None,effects=None):return pokemon(name,hp,maxhp,e,'Metal',tool,effects)
def opp(name,hp,maxhp,e=0):return pokemon(name,hp,maxhp,e,'Fighting')
empty=lambda: pokemon(None,None,None)
state={'owner':{'active':own(SG,140,140),'bench':[empty(),own(SS,140,140),empty()],'points':0},'opponent':{'active':opp(HI,80,80),'bench':[empty(),empty(),empty()],'points':0},'stadium':None}
states=[copy.deepcopy(state)]
def snapshot(t,n,phase,who,available=False,first=False,display=None):
    b={'turn_number_displayed':display,'turn_number_basis': 'Visible banner at this frame' if display else 'Sequence established by adjacent turn banners; this frame does not show a turn label.','phase':phase,'stadium':copy.deepcopy(state['stadium']),'shared_effects':[],'evidence_ids':refs(t)}
    if state['stadium']:b['shared_effects']=['Arena of Antiquity: Fighting Pokémon attacks +20 damage to opponent’s Active Pokémon ex; visible Stadium text.']
    for actor,typ in [('owner','Metal'),('opponent','Fighting')]:
        a=copy.deepcopy(state[actor]); a['bench_in_position_order']=a.pop('bench')
        for i,p in enumerate(a['bench_in_position_order']):p['bench_position']=['left','center','right'][i];p['evidence_ids']=refs(t)
        a['active']['bench_position']=None;a['active']['evidence_ids']=refs(t)
        a['energy_zone']={'this_turn':{'type':typ if available and who==actor and not first else None,'count':1 if available and who==actor and not first else 0,'available':bool(available and who==actor and not first)},'next':{'type':typ,'count':1,'available':False},'basis':'Visible Energy Zone and attachment transitions; next type icon retains Metal/Fighting. Current large sphere empties after attachment or outside acting turn.','evidence_ids':refs(t),'limit_reason':'No hidden Energy generation asserted.'}
        a['board_effects']=['Cursed Metal: owner Psychic/Metal attacks +30 to opponent’s Active Pokémon'] if any(p.get('name')=='Aegislash' and p.get('variant','').startswith('Cursed') for p in [a['active']]+a['bench_in_position_order']) else []
        a['status']='observed';a['limit_reason']=None;a['evidence_ids']=refs(t);b[actor]=a
    return b
def draw(kind,names,times,before,after,caused='Turn start',order=None,hidden=False,returned=None):
    return {'kind':kind,'caused_by':caused,'linked_play_order':order,'cards_in_reveal_order':[{'name':name,'reveal_position':i+1,'source_video':V,'timestamp_seconds':times[min(i,len(times)-1)],'evidence_ids':refs(times[min(i,len(times)-1)]),'basis':'Face revealed during draw/search' if name else 'Card back draw animation/count only','limit_reason':'Hidden opponent card identity' if name is None else None} for i,name in enumerate(names)],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':returned or [],'source_video':V,'timestamp_seconds':times[0],'evidence_ids':refs(*times),'limit_reason':'Hidden identities retained as null' if hidden else None}
def play(order,kind,card,t,result,target=None,count=None,energy=None,prompt=None,response=None,nested=None,bounds=None):
    return {'order':order,'kind':kind,'card_name':card,'target':target,'energy':energy,'result':result,'prompt_text':prompt,'response':response,'nested_events_in_order':nested or [],'hand_count_after':count,'source_video':V,'timestamp_seconds':t,'input_bounds_seconds':bounds,'evidence_ids':refs(t),'basis':'Visible play/reveal and resolution, not inferred from deck composition','limit_reason':'Opponent touch itself is hidden; timestamp is first visible action/reveal' if kind.startswith('opponent') else 'Timestamp is approximate requested seek; input may precede reveal.'}
def energy(actor,target):return {'type':'Metal' if actor=='owner' else 'Fighting','count':1,'destination':target,'retreat_payment_by_type':{}}
def event(t,detail):return {'timestamp_seconds':t,'source_video':V,'detail':detail,'evidence_ids':refs(t)}
turns=[]
starttimes=[42.8,46,81.5,93,131.5,163,232.8,277,310.8,355]
endtimes=[44,78,89.4,128,158,229,273,309,350,379]
drawends=[42.8,46,81.5,93,131.5,162,232.8,277,310.8,355]
owners_start=[h1,h1,h3,h1,h5,e5,h7,e7,h9,e9]
owners_end=[h1,h1,h1,h1,e5,e5,e7,e7,e9,e9]
fanstart=[4,5,4,5,4,5,3,4,4,5]
first=[43.7,55,82,99,132.5,173,233.5,278,311.8,357]
before=[43.5,75,88,124,152,225,257,293,344.2,369]

for n in range(1,11):
    actor='owner' if n%2 else 'opponent'; st=starttimes[n-1]; en=endtimes[n-1]
    # Start snapshot before any voluntary action; every owner's normal draw is included in the hand.
    bstart=snapshot(st,n,'After normal draw, before first voluntary input',actor,True,n==1)
    draws=[]; plays=[]; auto=[]
    if n==1:
        draws=[draw('normal_draw',[R],[42],3,4)]
        plays=[play(1,'end_turn',None,43.5,'End Turn selected; no card, attack, Supporter or Energy attachment performed',count=4,bounds=[43.5,44])]
    elif n==2:
        draws=[draw('normal_draw',[None],[46],4,5,hidden=True),draw('supporter_draw',[None,None],[57,58],4,6,PR,1,True),draw('search',[None],[63],5,6,PB,2,True)]
        plays=[play(1,'opponent_supporter',PR,55,'Two hidden cards drawn',count=6),play(2,'opponent_item',PB,61,'One hidden Basic Pokémon search result enters fan; identity is not revealed',count=6),play(3,'opponent_bench',RI,67,'Riolu 60 HP enters left bench',target='left bench',count=5),play(4,'opponent_stadium','Arena of Antiquity',69,'Stadium installed and remains in play',count=4),play(5,'opponent_energy',None,74,'Hitmonlee now has one Fighting Energy',target='Active Hitmonlee',count=4,energy=energy(actor,'Active Hitmonlee')),play(6,'opponent_attack','Stretch Kick',76,'30 damage to silver Skarmory ex on center bench: 140 → 110',target='owner center bench',count=4)]
        state['owner']['bench'][1]['hp_now']=110;state['owner']['bench'][1]['damage']=30
        state['opponent']['bench'][0]=opp(RI,60,60);state['opponent']['active']=opp(HI,80,80,1)
        state['stadium']={'name':'Arena of Antiquity','played_by':'opponent','timestamp_seconds':69,'evidence_ids':refs(69,71,272)}
    elif n==3:
        draws=[draw('normal_draw',[HO],[81],4,5)]
        plays=[play(1,'bench',HO,82,'Honedge placed on left bench, 60 HP',target='left bench',count=4,bounds=[81.5,82]),play(2,'energy',None,87,'Metal attached to green Active Skarmory ex, total one',target='Active green Skarmory ex',count=4,energy=energy(actor,'Active green Skarmory ex')),play(3,'end_turn',None,89,'End Turn selected without attacking or Supporter play',count=4)]
        state['owner']['bench'][0]=own(HO,60,60);state['owner']['active']=own(SG,140,140,1)
    elif n==4:
        draws=[draw('normal_draw',[None],[93],4,5,hidden=True),draw('supporter_draw',[None,None],[115,116],2,4,PR,4,True)]
        plays=[play(1,'opponent_bench',MA,100,'Marshadow 80 HP enters center bench',target='center bench',count=4),play(2,'opponent_evolution',ML,105,'Riolu on left bench evolves directly to Stage 1 Mega Lucario ex, 190 HP',target='left Riolu',count=3),play(3,'opponent_energy',None,109,'One Fighting attached to left Mega Lucario ex',target='left Mega Lucario ex',count=3,energy=energy(actor,'left Mega Lucario ex')),play(4,'opponent_supporter',PR,112,'Two hidden draws',count=4),play(5,'opponent_attack','Stretch Kick',125,'30 damage to left Honedge: 60 → 30',target='owner left Honedge',count=4)]
        state['opponent']['bench'][0]=opp(ML,190,190,1);state['opponent']['bench'][1]=opp(MA,80,80)
        state['owner']['bench'][0]=own(HO,30,60)
    elif n==5:
        draws=[draw('normal_draw',[PR],[130.5],4,5),draw('supporter_draw',[PB,PR],[139,140],3,5,PR,4),draw('search',[O],[145],4,5,PB,5)]
        plays=[play(1,'inspection',A,132.5,'Card inspection only, no card consumed, no effect',count=5),play(2,'inspection',D,133,'Card inspection only, prior to evolution input',count=5),play(3,'evolution',D,134,'Left Honedge evolves to Doublade. Existing 30 damage retained: 60/90 HP',target='left Honedge',count=4,bounds=[133,134]),play(4,'supporter',PR,137,'Draw Poké Ball then Professor’s Research',count=5,bounds=[135.5,136]),play(5,'item',PB,143,'Search reveals Orthworm and adds it to hand',count=5,bounds=[141,142]),play(6,'bench',O,149,'Orthworm placed on right bench, 100 HP',target='right bench',count=4),play(7,'energy',None,152,'Second Metal attached to green Active Skarmory ex',target='green Active Skarmory ex',count=4,energy=energy(actor,'green Active Skarmory ex')),play(8,'attack','Steel Wing',155,'70 damage to Active Hitmonlee: 80 → 10. Skarmory gains -20 damage from attacks during opponent’s next turn',target='opponent Active Hitmonlee',count=4,bounds=[153,154.2])]
        state['owner']['bench'][0]=own(D,60,90);state['owner']['bench'][2]=own(O,100,100);state['owner']['active']=own(SG,140,140,2,effects=['Steel Wing: -20 damage from attacks during opponent turn 6'])
        state['opponent']['active']=opp(HI,10,80,1)
    elif n==6:
        draws=[draw('normal_draw',[None],[162],4,5,hidden=True),draw('shuffle_and_draw',[None]*4,[208,209,210,210],0,4,'Copycat',5,True,returned=[{'name':None,'count':3,'destination':'deck','basis':'Remaining fan after playing Copycat is shuffled; identities hidden'}])]
        plays=[play(1,'opponent_item',L,173,'Heal Hitmonlee 10 → 30; Heads at 180 returns this Lucky Ice Pop to hand',target='opponent Active Hitmonlee',count=5,nested=[event(175,'Heal 20'),event(180,'Heads'),event(181,'Lucky Ice Pop returns to fan')]),play(2,'opponent_energy',None,182,'Second Fighting attached to left Mega Lucario ex, between first and second Ice Pop uses',target='left Mega Lucario ex',count=5,energy=energy(actor,'left Mega Lucario ex'),bounds=[181,183]),play(3,'opponent_item',L,184,'Heal Hitmonlee 30 → 50; Heads at 191 returns same item',target='opponent Active Hitmonlee',count=5,nested=[event(186,'Heal 20'),event(191,'Heads'),event(192,'Lucky Ice Pop returns')]),play(4,'opponent_item',L,194,'Heal Hitmonlee 50 → 70; Tails at 200 discards item',target='opponent Active Hitmonlee',count=4,nested=[event(195,'Heal 20'),event(200,'Tails'),event(201,'Lucky Ice Pop top of discard')]),play(5,'opponent_supporter','Copycat',204,'Remaining three hidden cards shuffled into deck, then four hidden cards drawn, matching owner hand count four',count=4),play(6,'opponent_bench',RI,216,'Second Riolu placed on right bench, 60 HP',target='right bench',count=3),play(7,'opponent_attack','Stretch Kick',226,'30 damage to left Doublade: 60 → 30',target='owner left Doublade',count=3)]
        auto=[event(171,'Owner taps own deck during opponent wait; tooltip shows nine cards. No draw, card play or pile viewer occurs.'),event(229,'Settled Doublade HP is 30/90; preceding red 60 flash at 228 is prior HP, not terminal HP.')]
        state['opponent']['active']=opp(HI,70,80,1);state['opponent']['bench'][0]=opp(ML,190,190,2);state['opponent']['bench'][2]=opp(RI,60,60)
        state['owner']['bench'][0]=own(D,30,90);state['owner']['active']['active_effects']=[]
    elif n==7:
        draws=[draw('normal_draw',[M],[232],4,5),draw('supporter_draw',[PB,MN],[247,248],3,5,PR,3),draw('search',[HO],[253],4,5,PB,4)]
        plays=[play(1,'evolution',A,234,'Left Doublade evolves to Cursed Metal Aegislash: 80/140 HP, retaining 60 damage; Ability +30 Psychic/Metal attack damage to opponent Active',target='left Doublade',count=4,bounds=[233.2,234]),play(2,'energy',None,241,'Metal attached to center silver Skarmory ex. Hover at 240 passes over Orthworm but confirmed attachment is silver Skarmory',target='center silver Skarmory ex',count=4,energy=energy(actor,'center silver Skarmory ex')),play(3,'supporter',PR,244,'Draw Poké Ball, then ordinary-art Metal Core Barrier',count=5),play(4,'item',PB,251,'Search reveals Honedge and adds it to hand',count=5),play(5,'attack','Steel Wing',260,'100 damage to Hitmonlee (70 + Cursed Metal 30), 70 → 0; owner earns one point. Green Skarmory gains -20 damage during opponent turn 8',target='opponent Active Hitmonlee',count=5,bounds=[258,259])]
        auto=[event(236,'Cursed Metal Ability automatically resolves; not a separate voluntary play'),event(264,'Hitmonlee removed to discard'),event(268,'Owner awarded +1 point'),event(271,'Owner inspects Arena of Antiquity while waiting for replacement; no play or Stadium change'),event(273,'Opponent mandatory replacement promotes left Mega Lucario ex to Active, outside an extra turn')]
        state['owner']['bench'][0]=own(A,80,140);state['owner']['bench'][1]=own(SS,110,140,1);state['owner']['active']=own(SG,140,140,2,effects=['Steel Wing: -20 damage during opponent turn 8']);state['owner']['points']=1
        state['opponent']['active']=opp(ML,190,190,2);state['opponent']['bench'][0]=empty()
    elif n==8:
        draws=[draw('normal_draw',[None],[277],3,4,hidden=True)]
        plays=[play(1,'opponent_energy',None,279,'Third Fighting attached to Active Mega Lucario ex',target='Active Mega Lucario ex',count=4,energy=energy(actor,'Active Mega Lucario ex')),play(2,'opponent_attack','Fighting Pulse',295,'140 damage at 296 knocks out green Active Skarmory ex (140 → 0); opponent awarded two points',target='owner green Active Skarmory ex',count=4)]
        auto=[event(298,'Green Skarmory ex removed to discard with its two Metal Energy'),event(302,'Opponent awarded +2 points, score owner 1 to opponent 2'),event(305,'Owner forced replacement selects silver Skarmory ex'),event(307,'Silver Skarmory ex becomes Active at 110 HP and one Metal; this is replacement, not a new owner turn')]
        state['opponent']['active']=opp(ML,190,190,3);state['opponent']['points']=2
        state['owner']['active']=own(SS,110,140,1);state['owner']['bench'][1]=empty()
    elif n==9:
        draws=[draw('normal_draw',[AS],[310],5,6)]
        plays=[play(1,'inspection',HO,311.8,'Honedge inspection zoom only, no card consumed',count=6,bounds=[311.2,311.8]),play(2,'bench',HO,312.5,'Honedge placed on center bench, 60 HP',target='center bench',count=5,bounds=[312,312.5]),play(3,'item',L,317,'Heal silver Active Skarmory ex 110 → 130; Heads at 324 returns Lucky Ice Pop',target='silver Active Skarmory ex',count=5,nested=[event(319,'Heal 20'),event(324,'Heads'),event(325,'Lucky Ice Pop returns')]),play(4,'item',L,326,'Replay same Lucky Ice Pop; heal 130 → 140 (10 actually healed); Tails at 332 discards item',target='silver Active Skarmory ex',count=4,nested=[event(329,'Full HP 140'),event(332,'Tails'),event(333,'Lucky Ice Pop discarded')]),play(5,'tool',M,337,'Gold-art Metal Core Barrier attached to silver Active Skarmory ex; -50 attack damage and discard at end opponent next turn',target='silver Active Skarmory ex',count=3,prompt='Please choose a Pokémon to attach a Pokémon Tool to.',response='Silver Active Skarmory ex selected at 338; tool attached by 340',nested=[event(340,'Tool attached')]),play(6,'energy',None,344,'Second Metal attached to silver Active Skarmory ex',target='silver Active Skarmory ex',count=3,energy=energy(actor,'silver Active Skarmory ex')),play(7,'attack','Steel Wing',347,'100 damage to Mega Lucario ex: 190 → 90; silver Skarmory gains -20 attack damage during opponent turn 10',target='opponent Active Mega Lucario ex',count=3,bounds=[345,346])]
        state['owner']['active']=own(SS,140,140,2,tool={'name':'Metal Core Barrier','variant':'gold artwork','effect':'-50 attack damage; discard at end of opponent next turn (turn 10)','evidence_ids':refs(340)},effects=['Steel Wing: -20 attack damage during opponent turn 10'])
        state['owner']['bench'][1]=own(HO,60,60);state['opponent']['active']=opp(ML,90,190,3)
    elif n==10:
        draws=[draw('normal_draw',[None],[355],4,5,hidden=True)]
        plays=[play(1,'opponent_supporter','Cyrus',357,'Cyrus selects damaged owner bench Aegislash (80/140 HP), switches it into Active; silver Skarmory moves to left bench with Tool and two Metal retained',target='owner left Aegislash',count=4,nested=[event(360,'Aegislash now Active; silver Skarmory on left bench')]),play(2,'opponent_evolution',ML2,363,'Right Riolu evolves directly to Stage 1 Mega Lucario ex alternate art, 190 HP',target='right Riolu',count=3),play(3,'opponent_energy',None,368,'One Fighting attached to right alternate-art Mega Lucario ex',target='right Mega Lucario ex',count=3,energy=energy(actor,'right Mega Lucario ex'),bounds=[367,368]),play(4,'opponent_attack','Fighting Pulse',370,'140 damage at 372 to Aegislash (80 → 0), removal at 374; opponent third point, final score 1–3',target='owner Active Aegislash',count=3)]
        auto=[event(360,'Cyrus switch resolves; no voluntary owner retreat, no Energy payment'),event(374,'Aegislash removed to discard; Cursed Metal board effect ends'),event(378,'Opponent third point awarded'),event(379,'Terminal board, no replacement turn follows')]
        silver=copy.deepcopy(state['owner']['active']);silver['previous_active_effects']=silver['active_effects'];silver['active_effects']=[];silver['effects_status']='Steel Wing applied while Active on turn 9; continuation after Cyrus switch is not established by this film and not asserted';state['owner']['bench'][0]=silver;state['owner']['active']=empty();state['opponent']['bench'][2]=opp(ML2,190,190,1);state['opponent']['points']=3
    bend=snapshot(en,n,'Resolved turn including mandatory replacement, or terminal state',actor,False)
    if n==1:
        bend['turn_number_displayed']=2;bend['turn_number_basis']='Actual Current turn: 2 banner at 44';bend['phase']='Transition to opponent turn 2 after owner End Turn; before opponent normal draw or voluntary play'
    if n==8:
        bend['phase']='Mandatory replacement settled; owner turn 9 has begun at 308, capture 309 precedes normal draw reveal at 310'
        bend['owner']['energy_zone']['this_turn']={'type':None,'count':None,'available':None};bend['owner']['energy_zone']['limit_reason']='Boundary is already turn 9; current large Energy sphere generation not yet established in this frame. Next Metal icon visible.'
    # Attack-created protection remains on its Pokémon until its stated expiry; terminal tool expiry is not filmed.
    row={'turn_number':n,'who_played':actor,'source_video':V,'timing':{'draw_animation_end_seconds':drawends[n-1],'first_voluntary_move_seconds':first[n-1],'before_end_action_seconds':before[n-1],'end_after_resolution_seconds':en},
        'hand_at_start':hand(owners_start[n-1],st) if actor=='owner' else hidden_hand(fanstart[n-1],st),
        'owner_hand_start':hand(owners_start[n-1],st),'opponent_hand_at_owner_turn_start':{'count':fanstart[n-1] if actor=='owner' else None,'supported_range':[fanstart[n-1],fanstart[n-1]] if actor=='owner' else None,'count_method':'Count visible individual card backs in retained native top crop','basis':'Native top fan inspected' if actor=='owner' else 'Not an owner turn; acting fan is in hand_at_start','evidence_ids':refs(st),'limit_reason':'Faces hidden'},
        'draws_and_searches':draws,'plays_in_order':plays,'automatic_events_in_order':auto,'board_at_start':bstart,'board_after':bend,'owner_hand_end':hand(owners_end[n-1],en),
        'discard_snapshot_ids':[f'discard_t{n:02}'],'turn_evidence_ids':refs(st,en,*[p['timestamp_seconds'] for p in plays]),'limits':['Opponent hidden draws/search identities remain unknown.','Requested timestamps are not measured PTS.','No full discard fan opened in this turn.']}
    banner_t=[40,44,79,90,129,160,230,274,308,351][n-1]
    row['turn_banner']={'turn_number_displayed':n,'timestamp_seconds':banner_t,'evidence_ids':refs(banner_t),'basis':'Actual Current turn label inspected. Row number denotes acting turn, not an invented concluding-turn label.'}
    row['hand_reconciliation']={'owner_start_after_normal_draw':len(owners_start[n-1]),'owner_end':len(owners_end[n-1]),'opponent_start_after_normal_draw':fanstart[n-1], 'opponent_end':{1:4,2:4,3:4,4:4,5:4,6:3,7:3,8:4,9:4,10:3}[n],'notes':{1:'3 + Rare Candy = 4; End Turn consumes no cards',3:'4 + Honedge - Honedge bench = 4',5:'4 + Research - Doublade - Research + 2 - Poké Ball + Orthworm - Orthworm = 4',7:'4 + Barrier - Aegislash - Research + 2 - Poké Ball + Honedge = 5',9:'5 + Shield Aegislash - Honedge - final discarded Ice Pop - attached Barrier = 3',6:'5, first Ice Pop returns, Energy consumes no hand card, second Ice Pop returns, third discards (4), Copycat play leaves 3 to shuffle, draws 4, Riolu bench leaves 3',10:'4 + hidden normal draw - Cyrus - Mega Lucario evolution = 3'}.get(n,'Opponent normal draw, public plays and hidden card counts reconcile; names remain hidden')}
    turns.append(row);states.append(copy.deepcopy(state))

discards=[]
for n,t,owner_top,opp_top in [(1,43.5,None,None),(2,78,None,PB),(3,89.4,None,PB),(4,128,None,PR),(5,158,PB,PR),(6,228,PB,'Copycat'),(7,273,PB,HI),(8,307,SG,HI),(9,350,L,HI),(10,379,A,'Cyrus')]:
    discards.append({'snapshot_id':f'discard_t{n:02}','turn_number':n,'source_video':V,'timestamp_seconds':t,'evidence_ids':refs(t),'view':'Main-board top-of-discard previews only','owner_top_visible':owner_top,'opponent_top_visible':opp_top,'full_pile_contents':None,'limit_reason':'No discard pile viewer opened. Top preview cannot establish the complete discard list or order.'})
save('TURN_LEDGER.json',{**base,'turns':turns,'discard_snapshots':discards,'limits':['All ten actual turns included. Mandatory replacement events stay in preceding turn.','Inspection actions are numbered, identified as no-effect actions; passive Ability resolves separately.','No Supporter-warning decline or retreat occurred visibly.','Discard preview is recorded separately from a full-pile inspection.']})
save('TURN_EVIDENCE.json',{**base,'source_sha256':H,'timestamp_basis':'Source-local requested fast-seek timestamps, exact decoded frame PTS not measured','frames':frames,'owner_turn_capture_sets':captures,'opening_evidence_ids':refs(26,28,34),'discard_snapshots':discards,'limits':['Contact sheets are navigation aids only; all decisive cards and selected owner fans were checked against retained native frames.','Bottom fifth is exactly [0,2025,1170,2532], top crop [0,0,1170,520]. Native full frame is authoritative for cards extending above bottom fifth.']})

q=json.loads((P/'qr_intake/QR_DECODE_0001.00.json').read_text(encoding='utf-8'))
(P/'QR_DECODE_RECEIPT.json').write_bytes((P/'qr_intake/QR_DECODE_0001.00.json').read_bytes())
snapshot_bytes=(P.parent/'LIVE_DECK_SNAPSHOT.json').read_bytes()
(P/'LIVE_DECK_SNAPSHOT_AT_INTAKE.json').write_bytes(snapshot_bytes)
log_snapshot=json.loads(snapshot_bytes.decode('utf-8-sig'))
counts=[]; slots=[]
for card in q['cards']:
    c={k:card[k] for k in ('entity_kind','entity_id','name','count','functional_ids')};c['variant']='Cursed Metal / Slicing Blade' if c['entity_id']==12540 else 'Superb Shield' if c['entity_id']==14860 else 'Semantic entity; QR does not identify printing';counts.append(c)
    for i in range(c['count']):slots.append({'position':len(slots)+1,'name':c['name'],'entity_id':c['entity_id'],'variant':c['variant'],'basis':'Retained filmed QR decode with catalog resolution, source hash bound'})
save('DECK_USED.json',{**base,'deck_name_in_log':None,'filmed_deck_label':'New deck 6','source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','captured_at':None,'log_list_version':None,'expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':counts,'energy_configuration_from_log':None,'actual_card_count':20,'capture_source_text_or_image':'qr_intake/QR_DECODE_0001.00.json; native editor at 3 seconds','game_version_binding_basis':'Uninterrupted filmed QR at 1s → New deck 6 editor at 3s → New deck 6 selected at event screen 4s → opponent search 5s → game. No deck edit/selection change observed.','conflicts_with_filmed_cards':[],'exact_list_status':'filmed_qr_exact_semantic_20_bound_to_game; matching_live_log_version_missing','filmed_semantic_slots_in_qr_order':slots,'filmed_energy_configuration':['Metal'],'log_snapshot_status':'Initial nine-deck batch snapshot has no matching version. Source-qualified deck entry is prepared locally only.','exact_20_log_snapshot_available':False,'limits':['The 20 slots above are filmed QR order, not Pause Games live-log order.','QR does not determine artwork, rarity, exact printing or hidden hand order.','Both Aegislash functional versions are distinct. Green/silver Skarmory and gold/ordinary Barrier artwork are visually distinguished in hand evidence only.','Required matching dated live-log list/version remains unavailable; no external log entry made by worker.']})
deck_doc=json.loads((P/'DECK_USED.json').read_text(encoding='utf-8'))
deck_doc['initial_log_snapshot']={'retained_path':'LIVE_DECK_SNAPSHOT_AT_INTAKE.json','sha256':hashlib.sha256(snapshot_bytes).hexdigest(),'retrieved_utc':log_snapshot.get('retrieved_utc'),'deck_names_checked':[d['deck_name_in_log'] for d in log_snapshot['decks']],'matching_decks_with_Skarmory_ex':[d['deck_name_in_log'] for d in log_snapshot['decks'] if any(c['name']=='Skarmory ex' for c in d['cards_in_log_order'])],'basis':'Parsed every captured live-deck card list; none contains the filmed Skarmory ex core, so none can be this exact semantic 20.'}
save('DECK_USED.json',deck_doc)
save('PAUSE_GAME.json',{**base,'review_date':'2026-10-06','destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':'New deck 6 (filmed label)','owner':'Dacz8976','opponent':'ゆぬ','mode':'Deluxe Pack: Mega Emblem Event','computer_battle':False,'computer_basis':'Human opponent search and event lobby visible; no Auto control visible anywhere reviewed.','opening':{'source_video':V,'timestamp_seconds':26,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[{'position':i+1,'name':x,'basis':'Visible original opening fan, before placement','evidence_ids':refs(26,28),'limit_reason':'Artwork description is not exact printing'} for i,x in enumerate(opening)],'selected_active':{'name':SG,'opening_position':2,'source_video':V,'timestamp_seconds':31,'selection_bounds_seconds':[28,34],'evidence_ids':refs(28,34)},'selected_bench':[{'name':SS,'opening_position':5,'position':'center','timestamp_seconds':34,'evidence_ids':refs(34)}],'redraw_or_replacement':'No opening redraw observed','before_active_placement':True,'status':'observed','evidence_ids':refs(26,28,34),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'worker_complete_pending_independent_acceptance','outcome':{'result':'loss','owner_points':1,'opponent_points':3,'turns':10,'damage_done':270,'evidence_ids':refs(379,390,395),'basis':'Final board plus Defeat results screen shows 1–3, Turns 10, Damage done 270'},'limits':['Exact matching live Pause Games list/version unavailable.','Opponent hidden hand identities and full discard views not filmed.','Exact PTS not measured.','No external action, registration, acceptance or archival performed.'],'lead_checked':False})
save('SUMMARY.json',{'schema':'battle-video-review-summary-v1','is_template':False,'game_id':G,'source_video':V,'source_sha256':H,'duration_seconds':S['duration_seconds'],'review_status':'worker_complete_pending_independent_acceptance','coverage_status':'entire_supplied_source_reviewed','owner':'Dacz8976','opponent':'ゆぬ','match_date_local':'2026-10-04','match_datetime_local':'2026-10-04T22:35:29-05:00','datetime_basis':'Metadata creation_time UTC converted to America/Chicago; phone clock reads 10:35–10:41','visible_deck_label':'New deck 6','visible_deck_core':['Skarmory ex','Honedge','Doublade','Aegislash Cursed Metal','Aegislash Superb Shield','Orthworm'],'mode':'Deluxe Pack: Mega Emblem Event','mode_basis':'Event selection screen at 4s; opponent search at 5s; uninterrupted sequence','computer_battle':False,'auto_control_visible':False,'auto_enabled':None,'owner_choices_basis':'Owner-side touch selection, zooms, plays and End Turn visibly enacted; no Auto option shown','outcome':'loss','owner_points':1,'opponent_points':3,'actual_turns':10,'damage_done':270,'result_evidence_seconds':[379,390,395],'deck_list_status':'20 semantic cards decoded from filmed QR and game-bound; required matching live-log list/version missing','external_action_taken':False,'lead_accepted':False,'recommended_independent_checks':[{'seconds':[26,28,34],'reason':'Original five and setup binding'},{'seconds':[42.8,43.5,44],'reason':'Intact T1 hand and End Turn input'},{'seconds':[81.5,82,87],'reason':'Ordinary owner T3 first move and Metal attachment'},{'seconds':[173,181,182,183,184,194,204,208,210,216,226],'reason':'Opponent T6 repeated Ice Pop, interleaved Energy attachment, Copycat count and attack'},{'seconds':[232.8,233.5,234,241,247,248,253,260],'reason':'T7 intact hand, evolution, silver attachment and named reveal order'},{'seconds':[310.8,311.8,312.5,324,332,337,340,344.2,348],'reason':'T9 no-effect inspection, intact six and Tool/hand arithmetic'},{'seconds':[357,360,363,368,372,390],'reason':'Cyrus switch, second Mega Lucario, terminal KO/results'}]})
save('UNCERTAINTIES.json',{'is_template':False,'source_video':V,'source_sha256':H,'uncertainties':[{'id':'u_log_version','status':'unresolved_external_source_limit','detail':'Required dated exact matching live Pause Games list/version not present in initial nine-deck snapshot. Filmed QR has all 20 semantic slots and is bound to game. Prepared entry local only.'},{'id':'u_hidden_opponent','status':'recording_limit','detail':'Opponent normal draws, Research cards, Poké Ball search result and Copycat cards are hidden. Counts observed; identities null.'},{'id':'u_printing','status':'recording_limit','detail':'QR functional card entity does not prove printing/artwork/rarity. Visible art labels only identify instances.'},{'id':'u_pts','status':'measurement_limit','detail':'Fast-seek requested timestamps are source-local approximation; exact decoded PTS not measured. First-input windows bounded with native neighboring frames.'},{'id':'u_discard','status':'recording_limit','detail':'No full discard viewer shown. Main board only reveals top card at periodic turns.'},{'id':'u_terminal_tool','status':'recording_limit','detail':'Game ends immediately after third point; Metal Core Barrier end-of-next-opponent-turn discard is not separately shown. Tool remains on benched silver Skarmory in terminal board.'}], 'resolved_questions':[{'detail':'Cyrus, not Sabrina, is the final Supporter','evidence_ids':refs(357,360)},{'detail':'Turn 6 second Fighting attachment occurs at 182 between first and second Ice Pop uses','evidence_ids':refs(181,182,183)},{'detail':'Turn 7 Metal attaches to silver Skarmory, not hovered Orthworm','evidence_ids':refs(240,241,242)},{'detail':'No Auto control visible; event matchmaking, not computer classification','evidence_ids':refs(4,5)},{'detail':'Defeat 1–3 after ten turns, damage done 270','evidence_ids':refs(390,395)}]})

review='''# Source-bound review: 20261005_033529000_iOS.MP4

Worker complete, awaiting independent acceptance. Dacz8976 loses to ゆぬ, 1–3 after ten actual turns. The result screen at 390–395 seconds shows Defeat, Turns 10 and Damage done 270. This is a Deluxe Pack: Mega Emblem Event match, established by the selection screen and opponent search at 4–5 seconds. No Auto control appears in the reviewed source. No external entry, registration or archival was performed.

The source is 400.856667 seconds, native 1170 × 2532 HEVC. SHA-256: e272b0c74f6a863c68811a235d7b9611b14994611365e58694028f323afaea3d. Metadata creation time converts to October 4, 2026, 22:35:29 America/Chicago; the filename's October 5 is the UTC date. Every evidence time is local to this source, a requested seek, not measured frame PTS.

The film opens on a readable QR for New deck 6. The QR, deck editor, event selection with New deck 6 selected, matchmaking and battle follow without a filmed deck change. The retained decode identifies 20 semantic cards: two Skarmory ex, two Honedge, one Doublade, one Cursed Metal Aegislash, one Superb Shield Aegislash, one Orthworm; two Poké Ball, two Rare Candy, two Lucky Ice Pop, one Steel Apron, two Metal Core Barrier, two Professor’s Research and one Copycat. Metal is the configured Energy. QR artwork and rarity remain unproven. The initial nine-deck live snapshot has no matching version; the source-qualified list is local only. DECK_USED.json explicitly does not call QR order live-log order.

The original five at 26 seconds, left to right, are Doublade, green-art Skarmory ex, Cursed Metal Aegislash, Lucky Ice Pop and silver-art Skarmory ex. Green Skarmory is chosen Active and silver is placed on center bench. No redraw is observed. The opponent starts with Hitmonlee Active and an empty bench. Owner goes first.

| Turn | Source window | Actions and resulting state |
|---|---|---|
| 1, owner | 40–44 | Rare Candy drawn; intact four-card fan at 42.8. Owner selects End Turn between 43.5 and 44. No card, Energy or attack is used. |
| 2, opponent | 44–78 | Hidden normal draw; Research draws two hidden cards; Poké Ball finds one hidden Basic. Riolu goes left bench, Arena of Antiquity installed, Fighting attached to Hitmonlee. Stretch Kick deals 30 to silver Skarmory on center bench, leaving 110/140 HP. |
| 3, owner | 79–90 | Honedge drawn and benched left; first consuming input bounded 81.5–82. Metal attached to green Active Skarmory. End Turn, no attack. Owner retains four cards. |
| 4, opponent | 90–129 | Hidden draw; Marshadow benched center; left Riolu evolves directly to Stage 1 Mega Lucario ex. Fighting attached there, Research draws two hidden cards. Stretch Kick hits Honedge for 30, leaving 30/60 HP. |
| 5, owner | 129–160 | Research drawn. Aegislash and Doublade inspections consume no card. Honedge evolves to Doublade, retaining 30 damage (60/90). Research reveals Poké Ball then Research. Poké Ball reveals Orthworm, which is benched right. Second Metal attaches to green Skarmory. Steel Wing deals 70, leaving Hitmonlee 10/80, and gives Skarmory -20 attack damage for turn 6. |
| 6, opponent | 160–230 | Hidden draw. Lucky Ice Pop heals Hitmonlee to 30; Heads returns it. At 182, a second Fighting is attached to left Mega Lucario, before the next Ice Pop. Second Ice Pop heals to 50, Heads returns it. Third heals to 70, Tails discards it. Copycat shuffles remaining three hidden cards and draws four, matching owner hand four. Second Riolu benched right. Stretch Kick deals 30 to Doublade, leaving 30/90. |
| 7, owner | 230–274 | Gold-art Metal Core Barrier drawn. Doublade evolves to Cursed Metal Aegislash, retaining 60 damage (80/140). Cursed Metal activates automatically, +30 Psychic/Metal attack damage to opponent Active. Metal attaches to center silver Skarmory, despite an earlier hover over Orthworm. Research reveals Poké Ball then ordinary-art Metal Core Barrier. Poké Ball reveals Honedge. Steel Wing deals 100 and knocks out Hitmonlee, awarding owner one point. Opponent mandatory replacement promotes left Mega Lucario. Owner inspects Arena while waiting, without changing it. |
| 8, opponent | 274–308 | Hidden draw. Third Fighting attaches to Active Mega Lucario. Fighting Pulse deals 140 to green Skarmory, knocking it out and awarding opponent two points. Owner mandatory replacement promotes silver Skarmory (110 HP, one Metal). |
| 9, owner | 308–351 | Superb Shield Aegislash drawn. Honedge inspected, then benched center. Lucky Ice Pop heals silver Skarmory 110 → 130; Heads returns it. Replay heals only 10 to reach 140; Tails discards it. Gold Metal Core Barrier attaches to silver Active, then second Metal. Steel Wing deals 100 to Mega Lucario, leaving it 90/190. Owner retains Rare Candy, ordinary Barrier and Superb Shield Aegislash. |
| 10, opponent | 351–379 | Hidden draw. Cyrus selects damaged Cursed Metal Aegislash and switches it Active, silver Skarmory to left bench with Tool and two Metal retained. Right Riolu evolves to second Mega Lucario ex, alternate art, and receives one Fighting. Active Mega Lucario's Fighting Pulse deals 140 to Aegislash, knocks it out, and awards third point. No extra replacement turn follows. |

Arena remains throughout. Its Fighting +20 applies against the opponent's Active Pokémon ex, not bench Stretch Kick targets. Turn 8's observed 140 is consistent with Fighting Pulse 90 + extra-Energy 50 + Arena 20 - Steel Wing 20. Turn 10 also visibly deals 140, to non-ex Aegislash, which has neither the Skarmory Tool nor the Skarmory Steel Wing protection. These calculations explain filmed damage; observed damage and resulting HP remain the authoritative record.

Owner attachments are all Metal: green Skarmory on turns 3 and 5, silver Skarmory on turns 7 and 9. Opponent attachments are Fighting: Hitmonlee turn 2, first Mega Lucario turns 4, 6 and 8, second Mega Lucario turn 10. No retreat or Energy-payment prompt occurs. No Special Condition is shown. The Cursed Metal Ability stops when Aegislash is knocked out. Metal Core Barrier's scheduled discard after opponent turn 10 is not separately filmed because the match ends; it remains attached to benched silver Skarmory in the terminal board.

Selected owner starting fans were individually inspected at native size: 42.8 (four), 81.5 (five), 131.5 (five), 232.8 (five), 310.8 (six). The +1/+3/+6 candidates are retained but rejected where next-turn transition, inspection zoom or a card already played makes them unsuitable. Each selected full frame keeps every starting card before the first input. The before-end frames preserve four, four, four, five and three cards respectively. T5 and T9 first voluntary inspections are separately numbered and do not consume cards.

No full discard viewer was opened. Periodic snapshots retain only main-board top previews, explicitly limited in TURN_LEDGER.json and TURN_EVIDENCE.json. Opponent fan counts at owner starts are 4, 4, 4, 3 and 4; hidden draw/search identities remain null. Structured rows preserve both boards, exact bench positions, HP/max/damage, typed Energy, Tool and effects, Stadium, points, Energy Zones, ordered reveals, all voluntary actions and replacement events.

Independent checks: original five/setup 26–34; ordinary owner move and intact starting hand 81.5–87; opponent turn 6 at 173–226, particularly 181–184 Energy between Ice Pops and 204–216 Copycat; turn 7 at 232.8–241 for Aegislash input and actual silver attachment; final Cyrus and knockout 357–390. Exact live-log list/version, hidden opponent faces, complete discard contents and measured PTS remain unavailable, not guessed.
'''
(P/'REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Coverage record

Source: 20261005_033529000_iOS.MP4, 0.000–400.856667 seconds, SHA-256 e272b0c74f6a863c68811a235d7b9611b14994611365e58694028f323afaea3d.

The complete supplied recording was traversed from setup through the post-match opponent card at the ending. Four-second overview images located state changes; native five-second context and dense one-second/fractional event windows were then inspected. Overview grids were not used as substitutes for draw-timed or selected hand captures. Retained native full frames and native crops support the actions and boundaries. This is a frame-based full-source inspection, not a claim of uninterrupted real-time playback or measured per-frame PTS.

| Covered source interval | Review and evidence |
|---|---|
| 0–40 | QR, New deck 6 editor and selection, event matchmaking, opening five, first-player notice and setup; qr_intake and native 3, 4, 5, 26, 28, 34, 38, 40. |
| 40–90 | Turns 1–3; dense 40–49, 47–78, fractional 79–89.4; T1 and T3 draw candidates and intact/pre-end captures. |
| 90–160 | Turns 4–5; dense 91–159 and fractional owner draw/evolution/Research windows. |
| 160–230 | Turn 6 entirety including idle interval, three Ice Pops, interleaved Fighting attachment, Copycat shuffle/draw, second Riolu and attack; native 160–228. |
| 230–274 | Turn 7 draw to first input, evolution/Ability, silver Energy, all Research/search reveals, attack, point and mandatory replacement; dense 229–274. |
| 274–308 | Turn 8 Energy/idle/attack and owner mandatory replacement; dense 274–307. |
| 308–351 | Turn 9 draw and no-effect zoom, bench, repeated Ice Pop, Tool prompt/target, Energy, attack; dense fractional 307–350. |
| 351–380 | Turn 10 draw, Cyrus switch, second Mega Lucario evolution/Energy, attack, KO and point; native 350–379. |
| 380–400.856667 | Defeat, result summary and opponent card ending; context 380, 385, 390, 395, 400, overview through 398. |

Ten actual turn rows are present. No uncovered game interval or missing turn was identified. Shorter than one-second inputs are bounded with fractional frames for owner intact-hand decisions. Requested seeks are not exact PTS. The packet records missing live-log version and unfilmed opponent/card/discard information as limits. Source bytes were not modified. Worker completion does not establish lead acceptance or external registration.
'''
(P/'COVERAGE.md').write_text(coverage,encoding='utf-8')
print(json.dumps({'authored':G,'turns':len(turns),'native_frames':len(frames),'owner_capture_sets':len(captures)},ensure_ascii=False))
