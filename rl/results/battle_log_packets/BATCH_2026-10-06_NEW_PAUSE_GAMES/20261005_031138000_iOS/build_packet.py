import json
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
from PIL import Image

P = Path(__file__).resolve().parent
B = P.parent
V = '20261005_031138000_iOS.MP4'
SHA = json.loads((P/'SOURCE.json').read_text(encoding='utf-8'))['sha256']
NOW = datetime.now(timezone.utc).isoformat()
G = 'pause-20261005-031138'
SRC = [{'video_basename': V, 'sha256': SHA, 'source_json': 'SOURCE.json'}]
def eid(t): return f'f{t:07.2f}'
def ev(t): return [eid(t)]
def save(name, data): (P/name).write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
def card(name,i,t): return {'position':i,'name':name,'variant':None,'basis':'observed card artwork/name in source, not inferred from deck','evidence_ids':ev(t),'limit_reason':'Exact printing not required to establish hand name'}
def hand(names,t):
    return {'cards_left_to_right':[card(n,i+1,t) for i,n in enumerate(names)],'count':len(names),'basis':'native hand fan, with draw reveal evidence for newly added card','evidence_ids':ev(t),'status':'observed','limit_reason':None}
def hidden_hand(n,t):
    return {'cards_left_to_right':[{'position':i+1,'name':None,'variant':None,'basis':'card back','evidence_ids':ev(t),'limit_reason':'Opponent hand identities hidden'} for i in range(n)],'count':n,'basis':'counted visible card backs','evidence_ids':ev(t),'status':'hidden_identities','limit_reason':'Opponent hand is not revealed'}
def na_hand(): return {'cards_left_to_right':None,'count':None,'basis':'not applicable to opponent turn','evidence_ids':[],'status':'not_applicable','limit_reason':'Named owner start/end hand supplement applies to owner turns'}
def mon(name,hp,mx,e=0,et='Psychic',pos=None,conf=False,variant=None):
    return {'name':name,'variant':variant or 'visible attack/HP variant; exact printing unspecified','bench_position':pos,'hp_now':hp,'hp_max':mx,'hp_max_basis':'printed HP visible, no HP modifier shown','damage':mx-hp,'attached_energy':{'total':e,'by_type':({et:e} if e else {})},'tool':'none','special_conditions':['Confused'] if conf else [],'active_effects':[],'evidence_ids':[],'status':'observed','limit_reason':None}
def zone(typ,n,t):
    return {'this_turn':{'type':typ if n else 'none','count':n,'available':bool(n)},'next':{'type':typ,'count':1,'available':False,'basis':'small preview icon, not current-turn availability'},'basis':'visible large current circle and small preview icon','evidence_ids':ev(t),'limit_reason':None}
def board(t,own,ob,opp,pb,oe=0,pe=0,pts=0,display=None):
    own=deepcopy(own);opp=deepcopy(opp);ob=deepcopy(ob);pb=deepcopy(pb)
    for m in [own,opp,*ob,*pb]: m['evidence_ids']=ev(t)
    return {'turn_number_displayed':display,'turn_number_display_limit_reason':None if display is not None else 'No numeric turn banner in this retained board frame; row number is bound to chronological turn transitions','phase':'resolved boundary board','stadium':'none','owner':{'active':own,'bench_in_position_order':ob,'energy_zone':zone('Psychic',oe,t),'points':pts,'board_effects':[],'evidence_ids':ev(t),'status':'observed','limit_reason':None},'opponent':{'active':opp,'bench_in_position_order':pb,'energy_zone':zone('Lightning',pe,t),'points':0,'board_effects':[],'evidence_ids':ev(t),'status':'observed','limit_reason':None},'shared_effects':[],'evidence_ids':ev(t)}
def play(order,kind,name,t,target,result,energy=None,nested=None,prompt=None,response=None,hcount=None):
    return {'order':order,'kind':kind,'card_name':name,'target':target,'energy':energy or {'type':'none','count':0,'destination':'none','retreat_payment_by_type':{}},'result':result,'prompt_text':prompt,'response':response,'nested_events_in_order':nested or [],'hand_count_after':hcount,'source_video':V,'timestamp_seconds':t,'evidence_ids':ev(t),'basis':'observed action and resolved state','limit_reason':None}
def draw(kind,names,t,linked=None,caused='normal turn draw',before=None,after=None):
    return {'kind':kind,'caused_by':caused,'linked_play_order':linked,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':V,'timestamp_seconds':tt,'evidence_ids':ev(tt),'basis':'visible named reveal' if n else 'hidden opponent draw','limit_reason':None if n else 'Opponent draws are face down'} for i,(n,tt) in enumerate(zip(names,t if isinstance(t,list) else [t]*len(names)))],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':[],'source_video':V,'timestamp_seconds':t[0] if isinstance(t,list) else t,'evidence_ids':[eid(tt) for tt in (t if isinstance(t,list) else [t])],'limit_reason':None if all(names) else 'Opponent normal draw identity hidden'}

# Cards on the board are differentiated by position and damage, not by inferred hidden membership.
S=mon('Spritzee',60,60,variant='Sweet Scent, 60 HP')
K=mon('Tapu Koko ex',130,130,et='Lightning',variant='Plasma Hurricane 20 / Mach Bolt 90, 130 HP')
F=mon('Froakie',60,60,et='Water',pos=3,variant='Flop 10, 60 HP')
H0=mon('Hatenna',60,60,pos=1,variant='Stampede 10, 60 HP')
H1=mon('Hatenna',60,60,pos=2,variant='Stampede 10, 60 HP')
GR=mon('Greninja',120,120,et='Water',pos=3,variant='Water Shuriken / Mist Slash 60, 120 HP')
Z=mon('Zeraora',90,90,et='Lightning',pos=2,variant='Thunderclap Flash / Lightning Claw 50, 90 HP')
T=mon('Togepi',50,50,pos=3,variant='Pound 20, 50 HP')

H2end=['Hatterene',"Professor's Research",'Aromatisse','Togetic']
H4end=['Hatterene','Togetic','Togekiss','Hatterene']
H6end=['Hatterene','Togetic','Togekiss']
b1s=board(44,S,[],K,[])
b1e=board(50,S,[],K,[F])
s2=deepcopy(S);s2['attached_energy']={'total':1,'by_type':{'Psychic':1}}
b2s=board(52.5,S,[],K,[F],oe=1)
b2s['owner']['energy_zone']['evidence_ids']=ev(55)
b2s['owner']['energy_zone']['limit_reason']='Energy generation finishes just after selected hand; verified before any Energy attachment'
b2e=board(78,s2,[H0,H1],K,[F],display=3)
k2=deepcopy(K);k2['attached_energy']={'total':2,'by_type':{'Lightning':2}}
h1hurt=deepcopy(H1);h1hurt.update(hp_now=40,damage=20)
s3=deepcopy(s2);s3.update(hp_now=40,damage=20)
b3s=board(83,s2,[H0,H1],K,[F],pe=1)
b3e=board(112,s3,[H0,h1hurt],k2,[GR])
a=mon('Aromatisse',70,90,1,variant='Confounding Cologne 40, 90 HP')
hr=mon('Hattrem',80,80,1,pos=1,variant='Disarming Voice 20, 80 HP')
kconf=deepcopy(k2);kconf.update(hp_now=90,damage=40,special_conditions=['Confused'])
b4s=board(116.5,s3,[H0,h1hurt],k2,[GR],oe=1)
b4s['owner']['energy_zone']['evidence_ids']=ev(120)
b4s['owner']['energy_zone']['limit_reason']='Energy generation finishes immediately after selected hand; verified before any Energy attachment'
b4e=board(140,a,[hr,h1hurt],kconf,[GR])
k3=deepcopy(kconf);k3['attached_energy']={'total':3,'by_type':{'Lightning':3}}
hrhurt=deepcopy(hr);hrhurt.update(hp_now=60,damage=20)
b5s=board(146,a,[hr,h1hurt],kconf,[GR],pe=1)
b5e=board(178,a,[hrhurt,h1hurt],k3,[Z,GR])
b6s=board(180.5,a,[hrhurt,h1hurt],k3,[Z,GR],oe=1)
b6s['owner']['energy_zone']['evidence_ids']=ev(181.5)
b6s['owner']['energy_zone']['limit_reason']='Current Psychic generation completes just after selected pre-play hand; observed before any energy attachment'
hat=mon('Hatterene',130,150,2,variant='Mental Crush 70+70 if Confused, 150 HP')
abench=deepcopy(a);abench['bench_position']=1;abench['attached_energy']={'total':0,'by_type':{}}
zactive=deepcopy(Z);zactive['bench_position']=None
b6e=board(206,hat,[abench,h1hurt,T],zactive,[GR],pts=2)
b7s=board(212,hat,[abench,h1hurt,T],zactive,[GR],pts=2,pe=1)
b7e=board(214,hat,[abench,h1hurt,T],zactive,[GR],pts=2,pe=1)
turns=[]
def row(n,who,start,end,hstart,hend,draws,plays,bs,be,fan=None,drawend=None,first=None,before=None,auto=None):
    d={'turn_number':n,'who_played':who,'source_video':V,'timing':{'start_seconds':start,'end_seconds':end,'draw_animation_end_seconds':drawend,'first_voluntary_move_seconds':first,'before_end_action_seconds':before,'end_after_resolution_seconds':end,'timing_precision':'approximately 0.1 to 0.5 seconds, visually located; requested seek times are not measured decoded PTS'},'hand_at_start':hstart,'owner_hand_start':hstart if who=='owner' else na_hand(),'opponent_hand_at_owner_turn_start':{'count':fan,'supported_range':None,'count_method':'count distinct card-back panels/edges in native top crop','basis':'direct visual count' if fan is not None else 'not applicable to opponent turn','evidence_ids':bs['evidence_ids'] if fan is not None else [],'limit_reason':None if fan is not None else 'This field is required only at owner turn starts'},'draws_and_searches':draws,'plays_in_order':plays,'automatic_events_in_order':auto or [],'board_at_start':bs,'board_after':be,'owner_hand_end':hend if who=='owner' else na_hand(),'discard_snapshot_ids':[],'turn_evidence_ids':list(dict.fromkeys(bs['evidence_ids']+be['evidence_ids']+[x for p in plays for x in p['evidence_ids']]+[x for p in draws for x in p['evidence_ids']])),'limits':['Neither player opens a discard-pile view in this turn. Opponent unrevealed cards remain hidden.']}
    if who=='owner':
        d['owner_hand_count_reconciliation']={2:'4 after setup + normal draw1 - Hatenna1 - Poke Ball1 + search1 - Research1 + Research2 - Hatenna1 =4',4:'4 + normal draw1 - Aromatisse1 - Research1 + Research2 - Hattrem1 =4',6:'4 + normal draw1 - Togepi1 - Hatterene1 =3; retreat and energy attachment do not remove hand cards'}[n]
    turns.append(d)

row(1,'opponent',44,50,hidden_hand(5,46),None,[draw('normal_draw',[None],45,before=4,after=5)], [play(1,'card_play','Froakie',48,'opponent Bench position 3','Froakie benched at 60 HP, no Energy',hcount=4),play(2,'end_turn',None,50,'turn boundary','Ends first turn without attachment or attack')],b1s,b1e,first=48,before=49)
row(2,'owner',50,78,hand(['Poke Ball','Hatenna','Hatterene',"Professor's Research","Professor's Research"],52.5),hand(H2end,76),[draw('normal_draw',["Professor's Research"],52,before=4,after=5),draw('search',['Hatenna'],60,2,'Poke Ball',3,4),draw('supporter_draw',['Aromatisse','Togetic'],[66,67],3,"Professor's Research",3,5)], [play(1,'card_play','Hatenna',53,'owner Bench position 2','Opening Hatenna placed on middle Bench',hcount=4),play(2,'card_play','Poke Ball',57.5,'owner deck/hand','Search reveals Hatenna',nested=['Poke Ball played','Hatenna revealed at60 and added to hand'],hcount=4),play(3,'card_play',"Professor's Research",64,'owner hand','Two draws: Aromatisse, then Togetic',nested=['Full-art Research played','Aromatisse revealed first','Togetic revealed second'],hcount=5),play(4,'card_play','Hatenna',72,'owner Bench position 1','Searched Hatenna benched on left',hcount=4),play(5,'energy_attachment',None,75,'Spritzee Active','1 Psychic attached',energy={'type':'Psychic','count':1,'destination':'Spritzee Active','retreat_payment_by_type':{}}),play(6,'end_turn',None,77,'End Turn','End Turn selected while an attack is available',prompt='An attack can be used',response='End Turn requested'),play(7,'prompt_response',None,77.5,'End your turn?','OK accepted; declines using the available attack',prompt='An attack can be used',response='OK; end without attack')],b2s,b2e,fan=4,drawend=52.3,first=53,before=76)
row(3,'opponent',78,112,hidden_hand(5,83),None,[draw('normal_draw',[None],80,before=4,after=5)], [play(1,'energy_attachment',None,84,'Tapu Koko ex Active','1 Lightning attached',energy={'type':'Lightning','count':1,'destination':'Tapu Koko ex Active','retreat_payment_by_type':{}}),play(2,'card_play','Rare Candy',89,'Froakie Bench position 3','Froakie evolves directly into Greninja',nested=['Rare Candy consumed','Greninja revealed and placed on Froakie; no Frogadier played'],hcount=3),play(3,'ability','Greninja',95,'owner Hatenna Bench position 2','Water Shuriken deals20; 60->40 HP'),play(4,'attack','Tapu Koko ex',109,'Spritzee Active','Plasma Hurricane20; Spritzee60->40; Koko gains a second Lightning',nested=['Plasma Hurricane20 damage','Lightning taken from Energy Zone and attached to Koko'])],b3s,b3e,first=84,before=107)
row(4,'owner',112,142,hand(H2end+['Togekiss'],116.5),hand(H4end,134.5),[draw('normal_draw',['Togekiss'],115,before=4,after=5),draw('supporter_draw',['Hatterene','Hattrem'],[124,126],2,"Professor's Research",3,5)], [play(1,'card_play','Aromatisse',118,'Spritzee Active','Evolves40/60 Spritzee into70/90 Aromatisse; damage20 and1Psychic retained',hcount=4),play(2,'card_play',"Professor's Research",121.5,'owner hand','Draws Hatterene then Hattrem',nested=['Research consumed','Hatterene first','Hattrem second'],hcount=5),play(3,'card_play','Hattrem',128,'Hatenna Bench position 1','Left Hatenna evolves to80HP Hattrem',hcount=4),play(4,'energy_attachment',None,132,'Hattrem Bench position 1','1 Psychic attached',energy={'type':'Psychic','count':1,'destination':'Hattrem Bench position 1','retreat_payment_by_type':{}}),play(5,'attack','Aromatisse',135,'Tapu Koko ex Active','Confounding Cologne40; Koko130->90HP and Confused',nested=['40damage','Confused applied'])],b4s,b4e,fan=3,drawend=115.7,first=118,before=134.5,auto=[{'kind':'condition_application','name':'Confused','target':'Tapu Koko ex','timestamp_seconds':140,'evidence_ids':ev(140)}])
row(5,'opponent',142,178,hidden_hand(4,146),None,[draw('normal_draw',[None],144,before=3,after=4)], [play(1,'card_play','Zeraora',148,'opponent Bench position2','Zeraora90HP benched,0Energy',hcount=3),play(2,'energy_attachment',None,150,'Tapu Koko ex Active','Third Lightning attached',energy={'type':'Lightning','count':1,'destination':'Tapu Koko ex Active','retreat_payment_by_type':{}}),play(3,'card_play','Electric Generator',152.5,'benched Lightning Pokemon if heads','Tail at156.2s; no Energy attached; no-effect play retained',nested=['Electric Generator item shown','Coin flip','Tail visible','Card discarded; Zeraora remains0Energy'],hcount=2),play(4,'ability','Greninja',161,'owner Hattrem Bench position1','Water Shuriken20;80->60HP'),play(5,'attack','Tapu Koko ex',173,'Aromatisse Active','Attack attempted while Confused; tails, attack did nothing',nested=['Confusion coin flip','Tail','The attack did nothing message; no damage'],hcount=2)],b5s,b5e,first=148,before=171,auto=[{'kind':'confusion_check','coin':'tails','result':'attack failed, no damage or extra Energy','timestamp_seconds':176,'evidence_ids':ev(176),'limit_reason':'Attempted attack name is not revealed before the failed confusion check; do not guess Mach Bolt or Plasma Hurricane'}])
turns[-1]['plays_in_order'][-1]['attack_name']=None
turns[-1]['plays_in_order'][-1]['limit_reason']='Failed Confusion check prevents the attack name animation; selected attack identity unknown'
row(6,'owner',178,207,hand(H4end+['Togepi'],180.5),hand(H6end,195.5),[draw('normal_draw',['Togepi'],180,before=4,after=5)], [play(1,'card_play','Togepi',181.2,'owner Bench position3','Pound20 Togepi50HP benched',hcount=4),play(2,'card_play','Hatterene',186,'Hattrem Bench position1','60/80 Hattrem evolves to130/150 Hatterene,20damage and1Psychic retained',hcount=3),play(3,'retreat',None,191,'Aromatisse Active -> Hatterene','Aromatisse pays1Psychic; Hatterene promoted, Aromatisse moves to Bench1',energy={'type':'Psychic','count':1,'destination':'discard payment','retreat_payment_by_type':{'Psychic':1}},nested=['Retreat selected','1Psychic removed from Aromatisse','Hatterene selected as replacement']),play(4,'energy_attachment',None,193.5,'Hatterene Active','Second Psychic attached',energy={'type':'Psychic','count':1,'destination':'Hatterene Active','retreat_payment_by_type':{}}),play(5,'attack','Hatterene',196,'Tapu Koko ex Active','Mental Crush140 total against Confused Koko; Koko knocked out; +2points',nested=['Mental Crush70+70 against Confused','Koko90HP depleted','Koko knocked out','Owner+2points','Opponent promotes Zeraora'])],b6s,b6e,fan=2,drawend=180.5,first=181.2,before=195.5,auto=[{'kind':'knockout','pokemon':'Tapu Koko ex','points_awarded':2,'owner_points_after':2,'opponent_points_after':0,'timestamp_seconds':203,'evidence_ids':ev(204)},{'kind':'forced_replacement','pokemon':'Zeraora','timestamp_seconds':206,'evidence_ids':ev(206)}])
row(7,'opponent',207,214,hidden_hand(3,212),None,[draw('normal_draw',[None],210,before=2,after=3)], [play(1,'concede',None,213,'battle','Opponent conceded; owner victory')],b7s,b7e,first=213,before=212)
ledger={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':SRC,'reviewer':'Sol / root/pause_031138','turns':turns,'limits':['Requested seek time is not a measured decoded frame PTS.','The selected opponent attack at the failed confusion check is hidden.','Opponent hand identities not publicly revealed remain unknown.','Discard-pile UI never opened.']}
save('TURN_LEDGER.json',ledger)

rolemap={29:('opening',None,None,None,True),52.5:('selected_owner_start_hand',2,'owner',52.3,True),53:('draw_candidate_approximately_plus1',2,'owner',52.3,False),55:('draw_candidate_approximately_plus3',2,'owner',52.3,False),58:('draw_candidate_approximately_plus6',2,'owner',52.3,False),76:('before_end_hand',2,'owner',52.3,False),116.5:('draw_candidate_plus1_selected',4,'owner',115.7,True),118.5:('draw_candidate_plus3',4,'owner',115.7,False),121.5:('draw_candidate_plus6',4,'owner',115.7,False),134.5:('last_pre_attack_hand',4,'owner',115.7,False),180.5:('selected_owner_start_hand_dense_early',6,'owner',180.5,True),181.5:('draw_candidate_plus1',6,'owner',180.5,False),183.5:('draw_candidate_plus3',6,'owner',180.5,False),186.5:('draw_candidate_plus6',6,'owner',180.5,False),195.5:('before_attack_hand',6,'owner',180.5,False)}
frames=[]
for f in sorted((P/'turn_evidence').glob('t*.jpg')):
    t=float(f.stem[1:]); im=Image.open(f)
    bp=f.with_name(f.stem+'_bottom.png');tp=f.with_name(f.stem+'_top.png')
    if not bp.exists(): im.crop((0,2025,1170,2532)).save(bp)
    if not tp.exists(): im.crop((0,130,1170,660)).save(tp)
    role,n,who,de,sel=rolemap.get(t,('focused_action_or_board',None,None,None,False))
    if n is None and 44 <= t < 214:
        n=1 if t<50 else 2 if t<78 else 3 if t<112 else 4 if t<142 else 5 if t<178 else 6 if t<207 else 7
        who='owner' if n in [2,4,6] else 'opponent'
    unzoomed=t in [29,52.5,116.5,180.5,76,134.5,195.5]
    unsuitable = 'Action/card zoom has already started; retained candidate is not used as the start hand' if de and not sel and role.startswith('draw_candidate') else None
    if t==134.5: unsuitable='Clear unzoomed final four-card hand immediately before Aromatisse attack at135.'
    frames.append({'evidence_id':eid(t),'role':role,'turn_number':n,'who_played':who,'source_video':V,'source_sha256':SHA,'draw_animation_end_seconds':de,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'actual_frame_limit_reason':'FFmpeg seek timestamp retained; decoded PTS not measured','offset_after_draw_seconds':round(t-de,2) if de is not None else None,'full_frame_path':str(f.relative_to(P)),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':str(bp.relative_to(P)),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':str(tp.relative_to(P)),'pixel_bounds_x0_y0_x1_y1':[0,130,1170,660]},'selected_for_start_hand':sel and role!='opening','before_first_play':sel,'unzoomed':unzoomed,'hand_spread':unzoomed,'observation':'See ledger and prose for source-bound observation','suitability_or_limit':unsuitable})
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':SRC,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'top_crop_pixel_bounds':[0,130,1170,660],'fixed_grid_is_turn_start_evidence':False,'discard_target_every_owner_turns':[2,3]},'frames':frames,'discard_snapshots':[],'scheduled_capture_limits':['No opened discard-pile views anywhere in the inspected source; public top discard cards and play-derived history only.','Turn2 first play begins less than1second after draw completes; dense52.5s frame selected.','Turn6 first play begins0.7seconds after draw completes; dense180.5s frame selected.','Turn4/6 end by attack, so last pre-attack hand replaces pre-End-Turn view.','Draw-end times are visually estimated; approximately+1/+3/+6 candidates retained.']})

qr=json.loads((P/'QR_DECODE.json').read_text(encoding='utf-8'))
new=json.loads((B/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8'))
entry=next(d for d in new['decks'] if d.get('source_video')==V)
entry=deepcopy(entry)
normalized_names={30:'Poke Ball',40:"Professor's Research"}
for c in entry['card_slots']:
    if c.get('entity_id') in normalized_names: c['name']=normalized_names[c['entity_id']]
qr=deepcopy(qr)
for c in qr['cards']:
    if c.get('entity_id') in normalized_names:
        c['name']=normalized_names[c['entity_id']]
        c['name_candidates']=[c['name']]
save('QR_NAME_NORMALIZATION.json',{'original_receipt':'QR_DECODE.json','original_receipt_unchanged':True,'normalization_basis':'Original correct UTF-8 source labels were initially read with the Windows default codec by the authored-copy script, creating mojibake in an intermediate DECK_USED. Fixed explicit UTF-8 reads; ASCII card aliases used consistently for authored packet, backed by semantic trainer IDs and visible cards','corrected_names_by_trainer_entity_id':normalized_names,'scope':'DECK_USED copy only; preserves entity IDs, counts, functional IDs, payload and all receipt hashes'})
save('DECK_USED.json',{'is_template':False,'schema':'pause-games/deck-snapshot-v1','game_id':G,'deck_name_in_log':entry['deck_name'],'filmed_deck_label':'New deck 6','source_url':new['destination'],'snapshot_retrieval_utc':new['prepared_utc'],'exact_list_status':'exact20_filmed_QR_and_prepared_new_log_entry_live_save_awaits_lead','log_list_version':'new entry prepared by lead in NEW_DECK_ENTRIES.json; initial LIVE_DECK_SNAPSHOT.json lacks this new Psychic deck','cards_in_log_order':entry['cards_in_log_order'] if 'cards_in_log_order' in entry else entry['card_slots'],'counts_by_name_and_variant':qr['cards'],'actual_card_count':20,'energy_configuration':['Psychic'],'captured_source_text_or_image':'../NEW_DECK_ENTRIES.json plus QR_DECODE.json and turn_evidence/t0002.00.jpg','filmed_QR_receipt':'QR_DECODE.json','game_version_binding_basis':'Source-continuous QR at2s -> selected New deck6 at5s -> battle opening29s; no deck edit shown. Opening and all reveals match semantic QR entities. Slot label alone is not a unique identity.','limits':['Exact artwork/rarity/printing is not encoded by QR.','Lead must update live-log retrieval/receipt after saving the prepared new entry; this packet does not claim it is already saved.','Pinned catalog is community-derived; resolved semantic identities and roundtrip are preserved.']})
opening=['Spritzee','Poke Ball','Hatenna','Hatterene',"Professor's Research"]
save('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'review_date':NOW,'sources':SRC,'destination':new['destination'],'deck_name':entry['deck_name'],'opening':{'source_video':V,'timestamp_seconds':29,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[card(n,i+1,29) for i,n in enumerate(opening)],'selected_active':{'name':'Spritzee','opening_position':1,'source_video':V,'timestamp_seconds':36,'evidence_ids':ev(29)+ev(44)},'redraw_or_replacement':'none','before_active_placement':True,'status':'observed_complete','evidence_ids':ev(29),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'worker_full_battle_review_complete_pending_independent_lead_acceptance','outcome':{'owner':'Dacz8976','opponent':'\u4e5d\u5154','result':'win','method':'opponent concession','owner_points':2,'opponent_points':0,'turns_played':7,'damage_done_displayed':180,'evidence_ids':ev(214)+ev(225)},'classification':'human opponent, Deluxe Pack: Mega Emblem Event; no Auto control shown','local_match_date':'2026-10-04','recording_metadata':'RECORDING_METADATA.json','limits':['Opened discard piles not recorded.','Opponent hidden hand/deck unknown.','Failed confusion attack identity not shown.','Exact QR printings unavailable.','Prepared new external deck entry awaits lead live-save verification.'],'lead_checked':False})
save('SUMMARY.json',{'source_video':V,'source_sha256':SHA,'reviewer':'Sol / root/pause_031138','review_utc':NOW,'scope':'entire226.181667s source: QR/intake, setup, all7turns, terminal concession and result screen through source end','status':'worker_full_battle_review_complete_pending_independent_lead_acceptance','capture_status':'complete_with_recording_limits','reviewed_intervals_seconds':[[0,226.181667]],'uninspected_intervals_seconds':[],'classification':'human event battle; no Auto visible','owner':'Dacz8976','opponent':'\u4e5d\u5154','local_date':'2026-10-04','owner_deck':entry['deck_name'],'visible_opponent_core':['Tapu Koko ex','Froakie -> Greninja','Zeraora','Rare Candy','Electric Generator'],'outcome':'win by opponent concession','owner_points':2,'opponent_points':0,'turns':7,'owner_turns':[2,4,6],'fullreview_accepted_by_lead':False,'recommended_independent_checks':[29,52.5,57.5,60,64,66,67,116.5,124,126,156.2,180.5,191,193.5,195.5,196,204,206,214,225]})
save('UNCERTAINTIES.json',{'source_video':V,'source_sha256':SHA,'unreviewed_intervals':[],'uncertainties':[{'id':'hidden_opponent','status':'recording_limit','reason':'Unrevealed opposing hand/deck identities hidden; only public cards transcribed'},{'id':'failed_attack_name','status':'recording_limit','time_seconds':173,'reason':'Confusion check fails before attack-name animation; attempted attack name unknown'},{'id':'discard_views','status':'not_shown','reason':'No opened discard-pile UI across entire inspected footage. Public plays are a separate history.'},{'id':'printing','status':'source_limit','reason':'QR resolves semantic entities, not artwork/rarity/printing'},{'id':'external_snapshot','status':'lead_write_pending','reason':'Prepared new deck entry copied locally; root must verify live save and then update deck receipt'},{'id':'frame_pts','status':'measurement_limit','reason':'Requested FFmpeg seek times known; exact decoded frame PTS not measured'}]})
print('Wrote seven-row packet; native frames:',len(frames))

