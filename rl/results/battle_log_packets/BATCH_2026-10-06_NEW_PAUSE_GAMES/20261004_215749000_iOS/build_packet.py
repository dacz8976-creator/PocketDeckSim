from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import json
from PIL import Image

P=Path(__file__).resolve().parent
source=json.loads((P/'SOURCE.json').read_text(encoding='utf-8'))
V=source['video_basename']; SHA=source['sha256']; G='20261004_215749000_iOS_game1'
src=[{'video_basename':V,'sha256':SHA,'source_json':'SOURCE.json'}]
reviewer='/root/pause_20261004_215749000_iOS'
def write(name,data):
    (P/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def eid(t): return 'f'+f'{t:07.2f}'
def hand(names,t,basis='Directly visible left-to-right hand'):
    return {'cards_left_to_right':[{'position':i+1,'name':n,'basis':'observation','evidence_ids':[eid(t)]} for i,n in enumerate(names)] if names is not None else None,'count':len(names) if names is not None else None,'basis':basis,'evidence_ids':[eid(t)],'status':'observed' if names is not None else 'hidden_opponent_hand','limit_reason':None if names is not None else 'Opponent card faces remain hidden.'}
def mon(name,hp,mx,en=0,typ=None,tool=None,pos=None,variant=None):
    return {'name':name,'variant':variant,'bench_position':pos,'hp_now':hp,'hp_max':mx,'hp_max_basis':'Visible printed HP and observed unchanged maximum','damage':mx-hp,'attached_energy':{'total':en,'by_type':({typ:en} if en else {})},'tool':tool,'special_conditions':[],'active_effects':[],'evidence_ids':[],'status':'observed','limit_reason':'Exact artwork/rarity is not identified unless card face establishes it.'}
def zone(typ,available):
    return {'this_turn':{'type':typ if available else None,'count':1 if available else 0,'available':available},'next':{'type':typ,'count':1,'available':None},'basis':'Visible large current Energy orb or empty current slot, plus smaller next Energy icon','evidence_ids':[],'limit_reason':'The smaller next icon establishes type, not an additional currently spendable Energy.'}
def board(t,turn,oa,ob,pa,pb,oe=False,pe=False,stadium=None,points=0):
    r={'turn_number_displayed':turn,'phase':'stable board boundary','stadium':stadium,'owner':{'active':oa,'bench_in_position_order':ob,'energy_zone':zone('Fire',oe),'points':points,'board_effects':[],'evidence_ids':[eid(t)],'status':'observed','limit_reason':None},'opponent':{'active':pa,'bench_in_position_order':pb,'energy_zone':zone('Metal',pe),'points':0,'board_effects':[],'evidence_ids':[eid(t)],'status':'observed','limit_reason':None},'shared_effects':([{'name':'Hiking Trail','observed_text':'At the end of each player\u2019s turn, that player draws a card if they have 3 or fewer cards in their hand.'}] if stadium else []),'evidence_ids':[eid(t)]}
    for who in ('owner','opponent'):
        r[who]['energy_zone']['evidence_ids']=[eid(t)]
        for m in [r[who]['active']]+[x for x in r[who]['bench_in_position_order'] if x]:
            if m: m['evidence_ids']=[eid(t)]
    return r
torch=lambda hp=60,tool=None:mon('Torchic',hp,60,tool=tool,variant='Peck 20, 60 HP; QR entity consistent with B1 033')
comb=lambda hp=80,en=0,tool=None,pos=None:mon('Combusken',hp,80,en,'Fire',tool,pos,variant='High Jump Kick 50, 80 HP; B1 034 semantic QR entity')
cast=lambda en=0,pos=None:mon('Castform Sunny Form',70,70,en,'Fire',pos=pos,variant='Sunny Scorching 30, 70 HP; B3 024 semantic QR entity')
tink=lambda hp=60:mon('Tinkatink',hp,60,1 if hp!=60 else 0,'Metal',variant='Corkscrew Punch 20, 60 HP')
rook=lambda pos=3:mon('Rookidee',60,60,pos=pos,variant='Pluck 10, 60 HP')
melt=lambda pos=2,en=0:mon('Meltan',60,60,en,'Metal',pos=pos,variant='Amass, 60 HP')
def blanks(*mons):
    a=[None,None,None]
    for m in mons:a[m['bench_position']-1]=m
    return a
def play(order,kind,name,t,result,target=None,count=None,typ=None,nested=None,prompt=None,response=None):
    return {'order':order,'kind':kind,'card_name':name,'target':target,'energy':{'type':typ,'count':count,'destination':target,'retreat_payment_by_type':{'Fire':1} if kind=='retreat' else None},'result':result,'prompt_text':prompt,'response':response,'nested_events_in_order':nested or [],'hand_count_after':None,'source_video':V,'timestamp_seconds':t,'evidence_ids':[eid(t)],'basis':'observation','limit_reason':None}
def draw(kind,names,t,caused=None,order=None,before=None,after=None):
    return {'kind':kind,'caused_by':caused,'linked_play_order':order,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':V,'timestamp_seconds':t+i,'evidence_ids':[eid(t+i)],'basis':'observation' if n else 'hidden card back','limit_reason':None if n else 'Opponent card face not revealed.'} for i,n in enumerate(names)],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':None,'source_video':V,'timestamp_seconds':t,'evidence_ids':[eid(t)],'limit_reason':None}

b1s=board(55,1,torch(),blanks(),mon('Tinkatink',60,60,variant='Corkscrew Punch 20'),blanks(rook()))
b1e=board(74,1,torch(tool='Rocky Helmet'),blanks(cast(pos=3)),mon('Tinkatink',60,60,variant='Corkscrew Punch 20'),blanks(rook()))
b2s=board(80,2,torch(tool='Rocky Helmet'),blanks(cast(pos=3)),mon('Tinkatink',60,60,variant='Corkscrew Punch 20'),blanks(rook()),pe=True)
b2e=board(104,2,torch(40,'Rocky Helmet'),blanks(cast(pos=3)),tink(40),blanks(rook()))
b3s=board(106,3,torch(40,'Rocky Helmet'),blanks(cast(pos=3)),tink(40),blanks(rook()),oe=True)
t= torch();t['bench_position']=2
b3e=board(131,3,comb(60,1,'Rocky Helmet'),blanks(t,cast(pos=3)),tink(40),blanks(rook()))
b4s=board(133,4,comb(60,1,'Rocky Helmet'),blanks(deepcopy(t),cast(pos=3)),tink(40),blanks(rook()),pe=True)
b4e=board(163,4,comb(40,1,'Rocky Helmet'),blanks(deepcopy(t),cast(pos=3)),tink(40),blanks(melt(en=1),rook()))
b5s=board(170,5,comb(40,1,'Rocky Helmet'),blanks(deepcopy(t),cast(pos=3)),tink(40),blanks(melt(en=1),rook()),oe=True)
b5e=board(225,5,cast(1),blanks(comb(80,1,pos=2),comb(40,0,'Rocky Helmet',3)),melt(pos=None,en=1),blanks(rook()),stadium='Hiking Trail',points=1)
b6s=board(226,6,cast(1),blanks(comb(80,1,pos=2),comb(40,0,'Rocky Helmet',3)),melt(pos=None,en=1),blanks(rook()),pe=True,stadium='Hiking Trail',points=1)
b6e=board(244,6,cast(1),blanks(comb(80,1,pos=2),comb(40,0,'Rocky Helmet',3)),melt(pos=None,en=1),blanks(rook()),pe=True,stadium='Hiking Trail',points=1)

commonlimits=['No opened discard-pile view occurs anywhere in the supplied source. Public play history is not a full discard snapshot.','Opponent identities behind card backs remain unknown.','Approximate draw-animation ends and action onset times are bounded to the retained frames, generally within about one second.','No hidden choices or actions are inferred from deck membership.']
turns=[]
def row(n,who,start,end,drawend,first,pre,hs,he,ds,ps,bs,be,auto=None):
    h=hand(hs,start) if who=='owner' else hand(None,start)
    oh=hand(hs,start,'Owner hand visible during opponent turn' if who=='opponent' else 'Direct visible hand after normal draw')
    # Opponent rows retain the owner's visible hand separately, rather than mislabeling it as the acting player's hand.
    if who=='opponent':oh=hand(hs,start,'Owner visible hand at this opponent boundary')
    z={'turn_number':n,'who_played':who,'source_video':V,'timing':{'start_seconds':start,'end_seconds':end,'draw_animation_end_seconds':drawend,'first_voluntary_move_seconds':first,'before_end_action_seconds':pre,'end_after_resolution_seconds':end},'hand_at_start':h,'owner_hand_start':oh,'opponent_hand_at_owner_turn_start':{'count':3 if who=='owner' else None,'supported_range':None,'count_method':'Count exposed left edges and card backs in native top crop','basis':'observation' if who=='owner' else 'Not applicable to opponent turn','evidence_ids':[eid(start)] if who=='owner' else [],'limit_reason':None if who=='owner' else 'Required fan count applies at owner-turn start.'},'draws_and_searches':ds,'plays_in_order':ps,'automatic_events_in_order':auto or [],'board_at_start':bs,'board_after':be,'owner_hand_end':hand(he,end),'discard_snapshot_ids':['not_shown_owner_'+str(n),'not_shown_opponent_'+str(n)],'turn_evidence_ids':list(dict.fromkeys([eid(start),eid(end),eid(pre)]+[q for x in ps+ds for q in x['evidence_ids']])),'limits':commonlimits.copy()}
    turns.append(z);return z

r=row(1,'owner',55,74,55,56,72,['Combusken','Copycat','Flame Patch','Rocky Helmet','Poké Ball'],['Combusken','Copycat','Flame Patch'],[draw('normal',['Poké Ball'],54,before=4,after=5),draw('search',['Castform Sunny Form'],60,'Poké Ball',1,4,5)],[play(1,'Item','Poké Ball',56,'Search reveals Castform Sunny Form; owner hand returns to five after the search.'),play(2,'bench Basic','Castform Sunny Form',62,'Placed in rightmost Bench slot (3).',target='owner Bench 3'),play(3,'Tool','Rocky Helmet',66,'Attached to Active Torchic.',target='owner Active Torchic'),play(4,'end turn',None,74,'Ends without using Copycat; no first-turn Energy attachment.',prompt='End your turn? A Supporter card can be used',response='OK accepted; warning was visibly dismissed to end turn')],b1s,b1e)
r['plays_in_order'][0]['hand_count_after']=5;r['plays_in_order'][1]['hand_count_after']=4;r['plays_in_order'][2]['hand_count_after']=3;r['plays_in_order'][3]['hand_count_after']=3
red=draw('forced replacement',['Flame Patch',"Professor's Research","Professor's Research"],91,'opponent Red Card',2,3,3)
red['returned_or_discarded_cards']=[{'name':n,'destination':'shuffled into owner deck','basis':'owner hand visible before Red Card'} for n in ['Combusken','Copycat','Flame Patch']]
r=row(2,'opponent',80,104,None,81,98,['Combusken','Copycat','Flame Patch'],['Flame Patch',"Professor's Research","Professor's Research"],[draw('normal',[None],80),red],[play(1,'Energy attachment',None,82,'Tinkatink receives one Metal Energy.',target='opponent Active Tinkatink',count=1,typ='Metal'),play(2,'Item','Red Card',89,'Owner shuffles the three-card hand into the deck and receives three new cards.',target='owner hand'),play(3,'attack','Tinkatink: Corkscrew Punch',99,'20 damage to Torchic: 60 to 40. Rocky Helmet returns 20 damage: Tinkatink 60 to 40.',target='owner Active Torchic')],b2s,b2e,[{'order':1,'name':'Rocky Helmet retaliation','timestamp_seconds':101,'result':'20 damage to attacking Tinkatink','evidence_ids':[eid(101)]}])
r['draws_and_searches'][1]['cards_in_reveal_order'][1]['timestamp_seconds']=93;r['draws_and_searches'][1]['cards_in_reveal_order'][1]['evidence_ids']=[eid(93)]
r['draws_and_searches'][1]['cards_in_reveal_order'][2]['timestamp_seconds']=94;r['draws_and_searches'][1]['cards_in_reveal_order'][2]['evidence_ids']=[eid(94)]
row(3,'owner',106,131,106,107,130,['Flame Patch',"Professor's Research","Professor's Research",'Combusken'],['Flame Patch',"Professor's Research",'Field Blower'],[draw('normal',['Combusken'],105,before=3,after=4),draw('Supporter draw',['Torchic','Field Blower'],118,"Professor's Research",2,2,4)],[play(1,'evolution','Combusken',107,'Evolves damaged Torchic; retains 20 damage and Rocky Helmet. HP changes 40/60 to 60/80.',target='owner Active Torchic'),play(2,'Supporter',"Professor's Research",114,'Draws Torchic then Field Blower.'),play(3,'bench Basic','Torchic',125,'Placed in center Bench slot (2).',target='owner Bench 2'),play(4,'Energy attachment',None,129,'Attaches this turn\u2019s Fire to Active Combusken.',target='owner Active Combusken',count=1,typ='Fire'),play(5,'end turn',None,132,'Ends with no attack; Combusken has only one of the two Energy required by High Jump Kick.')],b3s,b3e)
turns[-1]['draws_and_searches'][1]['cards_in_reveal_order'][1]['timestamp_seconds']=120;turns[-1]['draws_and_searches'][1]['cards_in_reveal_order'][1]['evidence_ids']=[eid(120)]
row(4,'opponent',133,163,None,140,157,['Flame Patch',"Professor's Research",'Field Blower'],['Flame Patch',"Professor's Research",'Field Blower'],[draw('normal',[None],134),draw('Supporter draw',[None,None],142,"Professor's Research",1)],[play(1,'Supporter',"Professor's Research",142,'Draws two hidden cards.'),play(2,'bench Basic','Meltan',144,'Placed in center Bench slot (2).',target='opponent Bench 2'),play(3,'Energy attachment',None,149,'Attaches one Metal to benched Meltan.',target='opponent Bench 2 Meltan',count=1,typ='Metal'),play(4,'Item','Potion',154,'Heals Tinkatink by 20: 40 to 60.',target='opponent Active Tinkatink'),play(5,'attack','Tinkatink: Corkscrew Punch',161,'20 damage to Combusken: 60 to 40. Rocky Helmet returns 20 damage to Tinkatink: 60 to 40.',target='owner Active Combusken')],b4s,b4e,[{'order':1,'name':'Rocky Helmet retaliation','timestamp_seconds':163,'result':'Tinkatink returns to 40/60 HP','evidence_ids':[eid(163)]}])
row(5,'owner',170,225,169,173,206,['Flame Patch',"Professor's Research",'Field Blower','Copycat'],['Field Blower','Copycat','Mega Blaziken ex'],[draw('normal',['Copycat'],169,before=3,after=4),draw('Supporter draw',['Combusken','Hiking Trail'],177,"Professor's Research",1,3,5),draw('Stadium end-turn draw',['Mega Blaziken ex'],225,'Hiking Trail',None,2,3)],[play(1,'Supporter',"Professor's Research",172,'Draws Combusken then Hiking Trail.'),play(2,'evolution','Combusken',179,'Evolves the center benched Torchic. New Combusken is 80/80.',target='owner Bench 2 Torchic'),play(3,'Stadium','Hiking Trail',190,'Places Hiking Trail in the Stadium slot.'),play(4,'retreat','Combusken',195,'Pays one Fire from the damaged Active Combusken; promotes Castform Sunny Form. Old Active moves to rightmost Bench slot3.',target='owner Bench 3 Castform Sunny Form',count=1,typ='Fire'),play(5,'Energy attachment',None,200,'Attaches the turn\u2019s Fire Energy to the undamaged center benched Combusken. Native200s shows the attachment flash on that Bench card.',target='owner Bench 2 Combusken',count=1,typ='Fire'),play(6,'Item','Flame Patch',201,'Attaches the Fire discarded for retreat to Active Castform Sunny Form; only the Active is a legal target shown by the card text. Castform gains its first Fire by206s.',target='owner Active Castform Sunny Form',count=1,typ='Fire'),play(7,'attack','Castform Sunny Form: Sunny Scorching',208,'Deals 50 including +20 Fire weakness to 40-HP Tinkatink; Tinkatink is knocked out. Owner gains one point. Stadium would cause Burn, but no enduring condition remains on the knocked-out target.',target='opponent Active Tinkatink')],b5s,b5e,[{'order':1,'name':'Knockout and point','timestamp_seconds':211,'result':'Tinkatink knocked out; owner points 0 to1','evidence_ids':[eid(211),eid(216)]},{'order':2,'name':'Hiking Trail','timestamp_seconds':225,'result':'Owner has two cards, draws Mega Blaziken ex at end of turn to finish with three. This is a Stadium end-turn draw, not a normal turn draw or a KO-triggered draw.','evidence_ids':[eid(225)]},{'order':3,'name':'Opponent replacement','timestamp_seconds':225,'result':'Meltan is promoted from center Bench to Active. Its one Metal Energy is retained.','evidence_ids':[eid(225)]}])
turns[-1]['plays_in_order'][0]['hand_count_after']=5;turns[-1]['plays_in_order'][1]['hand_count_after']=4;turns[-1]['plays_in_order'][2]['hand_count_after']=3;turns[-1]['plays_in_order'][3]['hand_count_after']=3;turns[-1]['plays_in_order'][4]['hand_count_after']=3;turns[-1]['plays_in_order'][5]['hand_count_after']=2;turns[-1]['plays_in_order'][6]['hand_count_after']=2
row(6,'opponent',226,244,None,232,243,['Field Blower','Copycat','Mega Blaziken ex'],['Field Blower','Copycat','Mega Blaziken ex'],[draw('normal',[None],226),draw('Supporter draw',[None,None],233,"Professor's Research",1)],[play(1,'Supporter',"Professor's Research",232,'Draws two hidden cards.'),play(2,'concede',None,244,'Your opponent conceded. Owner wins; board points are1-0 before results. No opponent Energy attachment or attack occurs after Research.')],b6s,b6e)

for rr,(a,b) in zip(turns,[(52,75),(75,103),(103,133),(133,165),(165,226),(226,245)]):
    rr['timing']['start_seconds']=a;rr['timing']['end_seconds']=b
    rr['timing']['end_after_resolution_seconds']=b
turns[3]['plays_in_order']=[turns[3]['plays_in_order'][0],turns[3]['plays_in_order'][1],turns[3]['plays_in_order'][3],turns[3]['plays_in_order'][2],turns[3]['plays_in_order'][4]]
for i,q in enumerate(turns[3]['plays_in_order']):q['order']=i+1
turns[3]['plays_in_order'][2]['timestamp_seconds']=152;turns[3]['plays_in_order'][2]['evidence_ids']=[eid(150),eid(152),eid(154)]
turns[3]['plays_in_order'][3]['timestamp_seconds']=156;turns[3]['plays_in_order'][3]['evidence_ids']=[eid(155),eid(156),eid(157)]
turns[3]['turn_evidence_ids']+= [eid(150),eid(152),eid(154),eid(155),eid(156),eid(157)]
turns[1]['draws_and_searches'][1]['cards_in_reveal_order'][1]['timestamp_seconds']=93;turns[1]['draws_and_searches'][1]['cards_in_reveal_order'][1]['evidence_ids']=[eid(92),eid(93)]
turns[1]['draws_and_searches'][1]['cards_in_reveal_order'][2]['timestamp_seconds']=93;turns[1]['draws_and_searches'][1]['cards_in_reveal_order'][2]['evidence_ids']=[eid(93),eid(94)]
turns[1]['draws_and_searches'][1]['cards_in_reveal_order'][1]['basis']='Visible ordinary-art Research already joining hand behind the next full-art Research reveal; retained93s contains both.'
turns[1]['draws_and_searches'][1]['cards_in_reveal_order'][2]['basis']='Visible full-art Research reveal follows the ordinary-art Research.'
turns[0]['board_after']['evidence_ids']=[eid(80)]
turns[0]['board_after']['phase']='Resolved owner turn1 board, before opponent actions'
turns[2]['board_after']['phase']='Owner turn3 resolved board; no attack or end effect changes it'
turns[4]['owner_hand_end']['basis']='Visible225-226s hand after Hiking Trail end-turn draw, not pre-attack two-card hand'
turns[4]['plays_in_order'][5]['evidence_ids']=[eid(201),eid(204),eid(206)]
turns[4]['plays_in_order'][4]['evidence_ids']=[eid(199),eid(200)]
turns[4]['turn_evidence_ids']+= [eid(200),eid(201),eid(204),eid(206)]
write('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':src,'turns':turns,'limits':commonlimits,'reviewer':reviewer})

snapshot=json.loads((P.parent/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8'))
deck=deepcopy(next(d for d in snapshot['decks'] if d['deck_name_in_log']=='Mega Blaziken tournament list'))
qr=json.loads((P/'QR_DECODE.json').read_text(encoding='utf-8'))
deck.update({'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':src,'source_url':snapshot['source_url'],'captured_at':snapshot['retrieved_utc'],'expected_card_count':20,'capture_source_text_or_image':deck['captured_source_text'],'energy_configuration_from_log':deck['energy_configuration'],'game_version_binding_basis':'Filmed New deck1 QR at1.0s and immediately subsequent gameplay. Visible Torchic/Combusken/Castform actions agree with the filmed QR. Current log list is a different evolution line.','conflicts_with_filmed_cards':[{'live_log':{'name':'Rare Candy','count':2},'filmed_QR':{'name':'Combusken','count':2},'evidence':'QR_DECODE.json; native/t0001.00.jpg; native/t0105.00.jpg; native/t0177.00.jpg'}],'exact_list_status':'exact_live_log_20_slot_snapshot_saved_but_game_version_conflict','filmed_deck_label':'New deck1','filmed_QR_20_card_counts':qr['cards'],'filmed_QR_energy':qr['decoded']['energy'],'filmed_QR_receipt':'QR_DECODE.json','limits':['Exact live log snapshot is retained as retrieved, not silently amended.','The current named Mega Blaziken list cannot be claimed as the exact filmed game list: two Rare Candy are replaced by two Combusken in the QR.','QR resolves functional card entities, not artwork, rarity or exact printing.','Deck membership does not establish hidden hands or draws.']})
write('DECK_USED.json',deck)
opening=['Combusken','Copycat','Torchic','Flame Patch','Rocky Helmet']
write('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'review_date':datetime.now(timezone.utc).isoformat(),'sources':src,'destination':snapshot['source_url'],'deck_name':'Mega Blaziken tournament list (current log snapshot conflicts with filmed New deck1 QR)','opening':{'source_video':V,'timestamp_seconds':30,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[{'position':i+1,'name':n,'basis':'observation','evidence_ids':[eid(30)],'limit_reason':None} for i,n in enumerate(opening)],'selected_active':{'name':'Torchic','opening_position':3,'source_video':V,'timestamp_seconds':31,'evidence_ids':[eid(30),eid(31)]},'redraw_or_replacement':False,'before_active_placement':True,'status':'complete','evidence_ids':[eid(30),eid(31)],'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'full_source_review_submitted_for_independent_acceptance','classification':'human opponent matchmaking; no visible Auto control','owner':'Dacz8976','opponent':'Sherwin','outcome':{'owner_result':'win','basis':'Opponent conceded244s; Victory vs. Sherwin256s','points_at_concession':{'owner':1,'opponent':0},'evidence_ids':[eid(244),eid(256)]},'limits':commonlimits+deck['limits'],'lead_checked':False})

c=P/'crops';c.mkdir(exist_ok=True)
frames=[]
owner_ranges={1:(53,74,55),3:(102,132,106),5:(167,225,169)}
candidate={(1,56):1,(1,58):3,(1,61):6,(3,107):1,(3,109):3,(3,112):6,(5,170):1,(5,172):3,(5,175):6}
selected={(1,55),(3,106),(5,170)}
preend={(1,72),(3,130),(5,206)}
for f in sorted((P/'native').glob('t*.jpg')):
    tt=float(f.stem[1:]); turn=1 if 49<=tt<75 else 2 if 75<=tt<103 else 3 if 103<=tt<133 else 4 if 133<=tt<165 else 5 if 165<=tt<225.5 else 6 if 225.5<=tt<246 else None
    if tt==104:turn=2 # resolved previous turn before owner draw
    if tt==106:turn=3
    with Image.open(f) as im:
        if im.size!=(1170,2532):raise ValueError((f,im.size))
        bp=c/(f.stem+'_bottom.png');tp=c/(f.stem+'_top.png')
        if not bp.exists():im.crop((0,2025,1170,2532)).save(bp)
        if not tp.exists():im.crop((0,0,1170,650)).save(tp)
    dr=owner_ranges.get(turn,(None,None,None))[2]
    key=(turn,tt); role='native_action_or_boundary'
    if key in candidate:role='draw_offset_candidate'
    if key in selected:role='selected_owner_start_hand'
    if key in preend:role='before_end_action_hand'
    if tt==30:role='opening_five_before_active'
    before=(turn==1 and tt<=55) or (turn==3 and tt<=106) or (turn==5 and tt<=171)
    limit=None
    if key in candidate and not before:limit='A voluntary play has begun or occurred by this scheduled candidate; retained, but not used to establish the pre-play hand.'
    if key==(5,172):limit='Research is being selected/zoomed; unzoomed170s chosen.'
    frames.append({'evidence_id':eid(tt),'role':role,'turn_number':turn,'who_played':'owner' if turn in (1,3,5) else 'opponent' if turn else None,'source_video':V,'source_sha256':SHA,'draw_animation_end_seconds':dr,'requested_source_seconds':tt,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':candidate.get(key),'full_frame_path':str(f.relative_to(P)),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':str(bp.relative_to(P)),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':str(tp.relative_to(P)),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,650]},'selected_for_start_hand':key in selected,'before_first_play':before if turn in (1,3,5) else None,'unzoomed':key in selected or key in preend or tt==30,'hand_spread':key in selected or key in preend or tt==30,'observation':'Source-native retained evidence; see linked turn row for transcription.','suitability_or_limit':limit})
discards=[{'snapshot_id':'not_shown_'+who+'_'+str(n),'turn_number':n,'pile_owner':who,'source_video':V,'timestamp_seconds':None,'cards_in_view':None,'scroll_coverage':None,'full_pile_established':False,'evidence_ids':[],'limit_reason':'No opened discard-pile view in this recorded turn or anywhere in the full source. The edge of the played/discarded pile does not establish full contents.'} for n in range(1,7) for who in ('owner','opponent')]
write('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':src,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'top_crop':'Native0,0,1170,650 covering fan, clock and both current/next Energy symbols','fixed_grid_is_turn_start_evidence':False,'discard_target_every_owner_turns':[2,3]},'frames':frames,'discard_snapshots':discards,'scheduled_capture_limits':['Owner plays rapidly after draws in turns1 and3; +1/+3/+6 candidates contain completed/begun plays. Dense source-local55s and106s pre-play frames are selected instead.','Owner turn5 +1 at170s is selected; +3 at172s already has a Research zoom; +6 at175s follows Research.','All exact seeks are requested source-local timestamps; actual decoder frame PTS has not been separately measured.','Source is continuous, one match. Low-battery overlay222-224s limits the Stadium draw reveal, but the added Mega Blaziken ex is legible in225-226s hand; no identity is filled from the deck list.']})

write('SUMMARY.json',{'video_basename':V,'source_sha256':SHA,'reviewer':reviewer,'review_model':'gpt-6.1-sol','reasoning_effort':'high','review_status':'full_source_review_submitted_for_independent_acceptance','capture_status':'complete_with_recording_limits','game_count':1,'recorded_turn_count':6,'classification':'human','auto_control_observed':False,'queue_label':'Online opponent matchmaking; precise ranked/private queue label not established','match_date_local':'2026-10-04','match_date_basis':'RECORDING_METADATA.json embedded UTC creation time converted to America/Chicago','owner':'Dacz8976','opponent':'Sherwin','visible_deck_core':['Torchic','Combusken','Castform Sunny Form','Mega Blaziken ex drawn at end turn5'],'owner_result':'win','outcome_evidence':[{'seconds':244,'text':'Your opponent conceded'},{'seconds':256,'text':'vs. Sherwin Victory!'}],'points_at_concession':{'owner':1,'opponent':0},'continuity':'One source, continuous setup through victory; no observed recording cut','QR_times':[1],'deck_version_conflict':'Live Mega Blaziken list has Rare Candy2; filmed QR instead has Combusken2. Both20-slot snapshots retained.','external_writes_performed':False,'source_moved':False,'independent_acceptance_pending':True})
write('UNCERTAINTIES.json',{'source_video':V,'source_sha256':SHA,'items':[{'id':'deck_version','status':'resolved_conflict_preserved','time_seconds':1,'finding':'Filmed QR is exact functional20-slot Fire list; current named log list differs by Combusken2/RareCandy2. Neither source is overwritten.','evidence':['QR_DECODE.json','DECK_USED.json',eid(105),eid(177)]},{'id':'discard_views','status':'recording_limit','finding':'Neither discard pile is opened; complete snapshot unavailable.','evidence':['COVERAGE.md']},{'id':'opponent_hidden','status':'recording_limit','finding':'Opponent normal and Research draws remain unknown card identities.','evidence':[eid(142),eid(232)]},{'id':'queue','status':'recording_limit','finding':'Human online matchmaking visible. Exact queue/ranked mode label not established. No Auto observed.'},{'id':'draw_offsets','status':'bounded_timing','finding':'Owner draw ends approximated55/106/169 seconds; play starts rapidly on turns1 and3. Retained scheduled offsets and dense selected pre-play frames expose this timing rather than substituting post-play hands.'},{'id':'end_turn_draw','status':'observed_with_reveal_overlay_limit','time_seconds':225,'finding':'Low battery popup obscures part of Hiking Trail draw animation. Owner hand changes FieldBlower/Copycat to those cards plus visibly named MegaBlazikenex by225-226s. Trail printed end-turn text and final hand support its source.'}]})
print('Wrote structured packet; turns=',len(turns),'native evidence frames=',len(frames))
known={f['evidence_id'] for f in frames}
missing=[]
def check(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ('evidence_ids','turn_evidence_ids') and isinstance(v,list):
                missing.extend(z for z in v if z not in known)
            else:check(v)
    elif isinstance(x,list):
        for y in x:check(y)
check(turns)
if missing:raise ValueError('Unresolved evidence references: '+str(sorted(set(missing))))
for f in frames:
    for path in [f['full_frame_path'],f['bottom_crop']['path'],f['top_crop']['path']]:
        if not (P/path).exists():raise ValueError(path)
assert len(turns)==6 and sum(q['who_played']=='owner' for q in turns)==3
assert len(deck['cards_in_log_order'])==20 and sum(q['count'] for q in qr['cards'])==20
assert all(not json.loads((P/n).read_text(encoding='utf-8')).get('is_template',False) for n in ['PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json'])
print('Evidence references and native paths verified; both saved lists have20 slots.')
