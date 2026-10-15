from pathlib import Path
from datetime import datetime, timezone
import json, copy, hashlib
from PIL import Image

P=Path(__file__).resolve().parent
SRC=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
VIDEO=SRC['video_basename']; SHA=SRC['sha256']; GAME='20261006_012140000_iOS-game-1'
NOW=datetime.now(timezone.utc).isoformat()
def write(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t): return 'F'+f'{t:07.2f}'.replace('.','')
def refs(*ts): return [eid(t) for t in ts]
SOURCES=[{'video_basename':VIDEO,'sha256':SHA,'source_json':'SOURCE.json'}]
LIMITS=[
 'No game-bound QR, exact deck editor list, or exact 20-card log snapshot appears in this source. A matching prior filmed QR is only a candidate because the intervening gap and deck edits are unrecorded.',
 'Opponent hand identities and ordinary draws remain hidden. Fan counts are visible card-back counts, not inferred card identities.',
 'Neither full discard pile is opened or scrolled. Top previews are partial views only.',
 'Native frame filenames are requested seek times. Individual decoded frame PTS was not measured; action input times are bounded intervals and are separate from card previews/reveals/resolution.',
 'The transient waiting-for-opponent messages do not establish why the opponent was unavailable.'
]
def common(): return {'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':GAME,'sources':SOURCES}
def hand(cards,t,status='observed',reason=None):
 return {'cards_left_to_right':cards,'count':len(cards) if cards is not None else None,'basis':'Native visible fan; names read from filmed cards' if cards is not None else 'Opponent card backs only','evidence_ids':refs(t),'status':status,'limit_reason':reason}
def hiddenhand(count,t):
 h=hand(None,t,'hidden_identities','Opponent cards face away from camera; identities cannot be read.');h['count']=count;return h
def pokemon(name,hp,maxhp,energy=None,pos=None,poison=False):
 return {'name':name,'variant':{'Venipede':'60 HP / Ram 20','Whirlipede':'90 HP / Poison Sting 20','Scolipede':'140 HP / Venoshock 70+','Mega Sableye ex':'170 HP / Cursed Jewel 80','Dialga ex':'150 HP / Metallic Turbo 30 / Heavy Impact 100','Honedge':'60 HP / Pierce 20','Tinkatink':'60 HP / Corkscrew Punch 20','Alolan Diglett':'60 HP / Happened to Headbutt 40'}[name],
 'printing':None,'printing_limit':'Exact set/artwork identifier is not established by this source.',
 'bench_position':pos,'hp_now':hp,'hp_max':maxhp,'hp_max_basis':'Printed card HP and subsequent intact-board views','damage':maxhp-hp,
 'attached_energy':{'total':sum((energy or {}).values()),'by_type':energy or {}},'tool':None,'tool_basis':'No attached Tool visible','special_conditions':['Poisoned'] if poison else [],'active_effects':[],
 'evidence_ids':[],'status':'observed','limit_reason':None}
def empty(pos):
 return {'name':None,'variant':None,'bench_position':pos,'hp_now':None,'hp_max':None,'hp_max_basis':'Empty bench slot','damage':None,'attached_energy':{'total':0,'by_type':{}},'tool':None,'special_conditions':[],'active_effects':[],'evidence_ids':[],'status':'empty','limit_reason':'Visible empty bench outline; no Pokemon occupies this position.'}
def zone(typ,available,t):
 return {'this_turn':{'type':typ if available else None,'count':1 if available else 0,'available':available},'next':{'type':typ,'count':None,'available':None},'basis':'Large current Energy icon is distinct from the small next-type preview. Next preview supplies type only, not currently usable Energy or a proven future generation count.','evidence_ids':refs(t),'limit_reason':'Next Energy is a preview; its count/availability cannot be taken as current Energy.'}
def player(active,bench,typ,available,points,t):
 a=copy.deepcopy(active);b=[copy.deepcopy(x) for x in bench]
 for x in [a]+b: x['evidence_ids']=refs(t)
 return {'active':a,'bench_in_position_order':b,'energy_zone':zone(typ,available,t),'points':points,'board_effects':[],'evidence_ids':refs(t),'status':'observed','limit_reason':None}
V=pokemon('Venipede',60,60); VD=pokemon('Venipede',60,60,{'Darkness':1})
W=pokemon('Whirlipede',90,90,{'Darkness':1}); WH=pokemon('Whirlipede',60,90,{'Darkness':1})
S=pokemon('Scolipede',130,140,{'Darkness':1,'Colorless':1})
M2=pokemon('Mega Sableye ex',170,170,{},2);M3=pokemon('Mega Sableye ex',170,170,{},3)
MD2=pokemon('Mega Sableye ex',170,170,{'Darkness':1},2);MD3=pokemon('Mega Sableye ex',170,170,{'Darkness':1},3)
H=pokemon('Honedge',60,60,{},1); T=pokemon('Tinkatink',60,60,{},2);TM=pokemon('Tinkatink',60,60,{'Metal':1},2)
D=pokemon('Alolan Diglett',60,60,{},3);DM=pokemon('Alolan Diglett',60,60,{'Metal':2},3);DA=pokemon('Alolan Diglett',60,60,{'Metal':2})
def B(t,display,phase,own,ob,opp,pb,oa=False,pa=False,points=0):
 return {'turn_number_displayed':display,'phase':phase,'stadium':None,'stadium_basis':'No Stadium is visible or played in the recorded game','owner':player(own,ob,'Darkness',oa,points,t),'opponent':player(opp,pb,'Metal',pa,0,t),'shared_effects':[],'evidence_ids':refs(t)}
E=lambda:[empty(1),empty(2),empty(3)]
boards={
1:(B(38,1,'after opponent normal draw, before first play',V,E(),pokemon('Dialga ex',150,150),E()),B(56,1,'after opponent last play, before turn transition',V,E(),pokemon('Dialga ex',150,150),[H,T,empty(3)])),
2:(B(60,2,'intact owner starting hand, before first play',V,E(),pokemon('Dialga ex',150,150),[H,T,empty(3)],True),B(89,2,'Ram damage resolved before next turn',VD,[empty(1),M2,M3],pokemon('Dialga ex',130,150),[H,T,empty(3)])),
3:(B(92,3,'after opponent normal draw, before first play',VD,[empty(1),M2,M3],pokemon('Dialga ex',130,150),[H,T,empty(3)],False,True),B(101,3,'after Metal attachment, before next turn',VD,[empty(1),M2,M3],pokemon('Dialga ex',130,150,{'Metal':1}),[H,T,D])),
4:(B(107.5,4,'intact owner starting hand, before first play',VD,[empty(1),M2,M3],pokemon('Dialga ex',130,150,{'Metal':1}),[H,T,D],True),B(123,5,'turn 4 attack and checkup resolved; turn 5 displayed',W,[empty(1),MD2,M3],pokemon('Dialga ex',100,150,{'Metal':1},poison=True),[H,T,D])),
5:(B(126,5,'after opponent draw, before Energy attachment',W,[empty(1),MD2,M3],pokemon('Dialga ex',100,150,{'Metal':1},poison=True),[H,T,D],False,True),B(145,6,'turn 5 attack/effect/checkup resolved; turn 6 displayed',WH,[empty(1),MD2,M3],pokemon('Dialga ex',90,150,{'Metal':2},poison=True),[H,T,DM])),
6:(B(149,6,'intact owner starting hand, before first play',WH,[empty(1),MD2,M3],pokemon('Dialga ex',90,150,{'Metal':2},poison=True),[H,T,DM],True),B(182,6,'KO, point award and opponent promotion resolved',S,[empty(1),MD2,MD3],DA,[H,T,empty(3)],points=2)),
7:(B(186,7,'after opponent draw, before Metal attachment',S,[empty(1),MD2,MD3],DA,[H,T,empty(3)],False,True,2),B(202,7,'last intact board before concession',S,[empty(1),MD2,MD3],DA,[H,TM,empty(3)],points=2))}

def play(order,kind,name,target,interval,reveal,result,count,ts,energy=None,nested=None):
 return {'order':order,'kind':kind,'card_name':name,'target':target,'energy':{'type':energy[0] if energy else None,'count':energy[1] if energy else None,'destination':target if energy else None,'retreat_payment_by_type':None},'result':result,'prompt_text':None,'response':None,'nested_events_in_order':nested or [],'hand_count_after':count,'source_video':VIDEO,'timestamp_seconds':reveal,'input_consumption_seconds':None,'input_consumption_interval_seconds':interval,'input_limit_reason':'Exact touch/input is not separately established; interval bounds retained from adjacent native before/after states. Preview/reveal/resolution are not substituted for the input.','preview_or_reveal_seconds':reveal,'evidence_ids':refs(*ts),'basis':'Visible card/board changes in source order','limit_reason':None}
def event(name,t,ts,details):return {'event':name,'source_video':VIDEO,'timestamp_seconds':t,'evidence_ids':refs(*ts),'details':details}
def draw(kind,cause,names,times,before,after,playorder=None,limit=None):
 return {'kind':kind,'caused_by':cause,'linked_play_order':playorder,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':VIDEO,'timestamp_seconds':times[i],'evidence_ids':refs(times[i]),'basis':'Named native card reveal' if n else 'Facedown opponent draw','limit_reason':None if n else 'Opponent identity hidden'} for i,n in enumerate(names)],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':[],'source_video':VIDEO,'timestamp_seconds':times[0],'evidence_ids':refs(*times),'limit_reason':limit}
START={1:hiddenhand(5,38),2:hand(['Scolipede','Poke Ball',"Professor's Research",'Whirlipede','Whirlipede'],60),3:hiddenhand(4,92),4:hand(['Scolipede','Whirlipede','Whirlipede','Wally','Cyrus'],107.5),5:hiddenhand(4,126),6:hand(['Scolipede','Whirlipede','Wally','Cyrus','Lucky Ice Pop'],149),7:hiddenhand(5,186)}
END={1:hand(['Scolipede','Poke Ball',"Professor's Research",'Whirlipede'],56),2:hand(['Scolipede','Whirlipede','Whirlipede','Wally'],84),3:hand(['Scolipede','Whirlipede','Whirlipede','Wally'],101),4:hand(['Scolipede','Whirlipede','Wally','Cyrus'],114),5:hand(['Scolipede','Whirlipede','Wally','Cyrus'],145),6:hand(['Whirlipede','Cyrus','Lucky Ice Pop'],168),7:hand(['Whirlipede','Cyrus','Lucky Ice Pop'],202)}
PLAYS={
1:[play(1,'bench','Honedge','opponent bench 1',[42,44],44,'Honedge 60 HP occupies left bench',4,[42,43,44]),play(2,'trainer','Poke Ball','opponent deck',[47,48],48,'Search adds an unidentified Basic. Later Tinkatink placement does not prove which card was searched.',4,[47,48,50]),play(3,'bench','Tinkatink','opponent bench 2',[50,51],51,'Tinkatink revealed as played at 51 and occupies center bench by 54',3,[50,51,52,53,54])],
2:[play(1,'trainer','Poke Ball','owner deck',[60.5,61],62,'Finds Mega Sableye ex; named reveal at 64',5,[60,60.5,61,62,64,65]),play(2,'bench','Mega Sableye ex','owner bench 2',[65,66],66,'First Mega Sableye ex benched in center',4,[65,65.5,66]),play(3,'supporter',"Professor's Research",'owner hand',[71,72],72,'Draws Mega Sableye ex then Wally',5,[70,71,72,75,76,78]),play(4,'energy_attachment',None,'owner Active Venipede',[79,80],80,'One Darkness attached to Active',5,[79,80],('Darkness',1)),play(5,'bench','Mega Sableye ex','owner bench 3',[80,81],81,'Second Mega Sableye ex benched on right',4,[80,81,82,83]),play(6,'attack','Ram','opponent Active Dialga ex',[85,86],86,'20 damage; Dialga ex 150 to 130; attack ends turn',4,[84,85,86,87,89])],
3:[play(1,'bench','Alolan Diglett','opponent bench 3',[96,98],98,'Alolan Diglett 60 HP occupies right bench',3,[96,98]),play(2,'energy_attachment',None,'opponent Active Dialga ex',[99,100],100,'One Metal attached; no attack before next turn',3,[99,100,101],('Metal',1))],
4:[play(1,'evolution','Whirlipede','owner Active Venipede',[107.5,108.5],108.5,'Venipede evolves to Whirlipede at full 90 HP; attached Darkness retained',4,[107.5,108.5,110]),play(2,'energy_attachment',None,'owner bench 2 Mega Sableye ex',[111,113.5],113.5,'One Darkness attached to center Mega Sableye ex',4,[112,113.5,114],('Darkness',1)),play(3,'attack','Poison Sting','opponent Active Dialga ex',[115,116],116,'20 damage: 130 to 110. Poison applied; subsequent checkup reduces to 100',4,[114,115,116,118,120,121,122])],
5:[play(1,'energy_attachment',None,'opponent Active Dialga ex',[131,133],133,'Second Metal attached to Dialga ex',4,[131,132,133],('Metal',1)),play(2,'attack','Metallic Turbo','owner Active Whirlipede',[137,139],138,'30 damage; Whirlipede 90 to 60. Effect subsequently adds two Metal to Alolan Diglett',4,[137,138,139,140,141,142,143],nested=[event('attack damage',141,[140,141],'Whirlipede 90 to 60'),event('generated Energy attachment',143,[142,143],'Two additional Metal generated and attached to opponent bench 3 Alolan Diglett. Dialga retains its two attached Metal. This is distinct from the earlier normal one-Energy attachment and the small next-Energy preview.')])],
6:[play(1,'item','Lucky Ice Pop','owner Active Whirlipede',[149,150],151,'Heals 20 HP, 60 to 80; coin Heads returns same Item to hand',5,[149,150,151,153,154,157.5,158],nested=[event('heal',154,[153,154],'Whirlipede 60 to 80'),event('coin result',157.5,[157.5],'Heads'),event('return same Item',158,[158],'Lucky Ice Pop returns to owner hand; not a new deck draw')]),play(2,'evolution','Scolipede','owner Active Whirlipede',[158,160],160,'Evolves to 140-max Scolipede with 10 damage retained: current HP 130',4,[158,160,162]),play(3,'supporter','Wally','owner Active Scolipede',[162,163],164,'Adds one Colorless to Stage 2 Scolipede, which retains its prior Darkness',3,[162,163,164,165,166],('Colorless',1),[event('generated Colorless attachment',166,[165,166],'This filmed Wally takes Colorless Energy and attaches it to Stage 2; it does not perform an evolution.')]),play(4,'energy_attachment',None,'owner bench 3 Mega Sableye ex',[166,168],167,'Normal available Darkness attaches to right Mega Sableye ex after Wally',3,[166,167,168],('Darkness',1)),play(5,'attack','Venoshock','opponent Active Dialga ex',[169,170],171,'120 attack damage to Poisoned Dialga ex; KO, two points and Alolan Diglett promotion follow separately',3,[168,169,170,171,172,172.5,173,173.5,174,174.5,175,178,182])],
7:[play(1,'energy_attachment',None,'opponent bench 2 Tinkatink',[189,191],191,'One Metal attached to Tinkatink; no attack occurs before concession',5,[189,190,191,192],('Metal',1)),play(2,'concession',None,'match',[203,204],204,'Your opponent conceded; owner wins',5,[203,204,205,206])]
}
AUTO={1:[],2:[],3:[],4:[event('Poison checkup',122,[121,122,123],'Dialga ex 110 to 100 after Poison Sting; distinct from 20 attack damage.')],5:[event('Poison checkup',144,[143,144,145],'Dialga ex 100 to 90 at turn-end checkup.')],6:[event('damage animation',172,[172,172.5],'Venoshock shows 120; HP countdown still in progress (20 visible at 172.5)'),event('zero HP',173.5,[173,173.5],'HP 20 remains visible at 173; first retained zero-HP frame is 173.5 with Dialga ex still occupying Active. Zero transition is bounded 173-173.5.'),event('removal animation',174,[174,174.5],'Dialga card glows/removes at 174; vacant outline still covered by removal cloud at 174.5'),event('first clear empty Active',175,[175],'Clear empty opponent Active; Dialga ex in discard preview; points not yet awarded'),event('two-point award',178,[176,177,178],'Owner points become 2; opponent remains 0'),event('promotion',182,[181,182],'Alolan Diglett moves from bench 3 to Active, retaining 60 HP and two Metal')],7:[event('Victory results',214,[214,214.8],'Went second; Turns played 7; points 2-0; damage done 160; Scolipede card of the game')]}
DRAWS={
1:[draw('normal_draw','start of turn',[None],[38],4,5,limit='Opponent normal draw is facedown.'),draw('search','Poke Ball',[None],[50],3,4,2,'Searched card remains facedown. Tinkatink is later revealed as a bench play, which cannot distinguish a searched card from a previously held card.')],
2:[draw('normal_draw','start of turn',['Whirlipede'],[59],4,5),draw('search','Poke Ball',['Mega Sableye ex'],[64],4,5,1),draw('supporter_draw',"Professor's Research",['Mega Sableye ex','Wally'],[75,76],3,5,3)],
3:[draw('normal_draw','start of turn',[None],[92],3,4,limit='Opponent normal draw is facedown.')],4:[draw('normal_draw','start of turn',['Cyrus'],[106],4,5)],5:[draw('normal_draw','start of turn',[None],[126],3,4,limit='Opponent normal draw is facedown.')],6:[draw('normal_draw','start of turn',['Lucky Ice Pop'],[147],4,5)],7:[draw('normal_draw','start of turn',[None],[186],4,5,limit='Opponent normal draw is facedown.')]
}
TIMES={1:(None,43,56,56),2:(59.5,60.5,84,89),3:(None,97,101,103),4:(107.5,108,114,123),5:(None,132,137,145),6:(148,150,168,182),7:(None,190,202,206)}
ledger=common();ledger['turns']=[]
for n in range(1,8):
 owner=n%2==0;t=TIMES[n];row={
 'turn_number':n,'who_played':'owner' if owner else 'opponent','source_video':VIDEO,
 'timing':dict(zip(['draw_animation_end_seconds','first_voluntary_move_seconds','before_end_action_seconds','end_after_resolution_seconds'],t)),
 'timing_limits':{'draw_animation_end_interval_seconds':{2:[59,59.5],4:[106.5,107.5],6:[147,148]}.get(n),'draw_end_basis':'Completion localized to inspected before/after native frames' if owner else 'Opponent card identities hidden; exact draw-end frame not separately pinned','input_times':'See per-play input_consumption_interval_seconds; headline times are localization anchors, not exact input measurements.'},
 'hand_at_start':START[n], 'owner_hand_start':START[n] if owner else END[n-1] if n>1 else hand(['Scolipede','Poke Ball',"Professor's Research",'Whirlipede'],38),
 'opponent_hand_at_owner_turn_start':{'count':{2:3,4:3,6:4}.get(n),'supported_range':None,'count_method':'Count visible card backs in native opponent fan','basis':'Distinct visible card backs at owner starting-hand frame' if owner else 'Not an owner turn; see opponent hand_at_start instead','evidence_ids':refs({2:60,4:107.5,6:149}.get(n,t[2])),'limit_reason':None if owner else 'Field applies to owner turn starts only.'},
 'draws_and_searches':DRAWS[n],'plays_in_order':PLAYS[n],'automatic_events_in_order':AUTO[n],
 'board_at_start':boards[n][0],'board_after':boards[n][1],'owner_hand_end':END[n],
 'opponent_hand_end':hiddenhand({1:3,2:3,3:3,4:3,5:4,6:4,7:5}[n],t[3]),
 'discard_snapshot_ids':['D2_OWNER','D2_OPP'] if n==2 else ['D4_OWNER','D4_OPP'] if n==4 else ['D6_OWNER','D6_OPP'] if n==6 else [],
 'turn_evidence_ids':sorted(set(sum((x['evidence_ids'] for x in PLAYS[n]),[])+boards[n][0]['evidence_ids']+boards[n][1]['evidence_ids'])),
 'visible_declines_or_no_effect_actions':[],'decline_basis':'No warning decline or voluntarily played no-effect card is visible in this turn. Card inspection and Research card reveals are not additional card plays.',
 'end_turn_input':{'timestamp_seconds':None,'interval_seconds':{1:[56,57],3:[101,104],5:[137,139]}.get(n),'limit_reason':'Opponent End Turn tap is not separately visible; transition establishes ending without attack for turns 1/3, and attack ends turn 5.'} if not owner and n<7 else {'timestamp_seconds':None,'interval_seconds':None,'limit_reason':'Owner attack ends the turn; turn 7 ends by concession.'},
 'limits':['No hidden opponent card identity is inferred from deck membership.','Board snapshots are before first play and after final resolution; displayed turn may already advance after checkup.']}
 ledger['turns'].append(row)
ledger['limits']=LIMITS
write('TURN_LEDGER.json',ledger)

pause=common();pause.update({'review_date':'2026-10-06','destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':'Scolipede / Mega Sableye ex (filmed deck label New deck 6; exact list unbound)',
 'opening':{'source_video':VIDEO,'timestamp_seconds':23.5,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[{'position':i+1,'name':name,'basis':'Native pre-placement fan, card titles/printed identity','evidence_ids':refs(23,23.5),'limit_reason':None} for i,name in enumerate(['Scolipede','Poke Ball',"Professor's Research",'Whirlipede','Venipede'])],'selected_active':{'name':'Venipede','opening_position':5,'source_video':VIDEO,'timestamp_seconds':24,'evidence_ids':refs(23.5,24,24.5,25)},'redraw_or_replacement':'None observed','before_active_placement':True,'status':'observed_complete','evidence_ids':refs(23,23.5,24,25),'limit_reason':None},
 'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},
 'capture_status':'complete_with_recording_limits','battle_review_status':'whole_source_first_pass_complete_awaiting_independent_acceptance','outcome':{'owner':'Dacz8976','opponent':'おせち','result':'win','method':'opponent concession','points_owner':2,'points_opponent':0,'turns_played':7,'owner_went':'second','damage_done_owner_results':160,'concession_seconds':204,'victory_seconds':214,'evidence_ids':refs(204,205,214,214.8)},'classification':'human event battle; Deluxe Pack: Mega Emblem Event','classification_basis':'Event lobby at source start, matchmaking and named opponent; no battle Auto control is visible anywhere in the source.','match_date_local':'2026-10-05','date_basis':'Recording UTC creation 2026-10-06T01:21:40Z converts to America/Chicago 2026-10-05 20:21:40; displayed phone clock agrees. Filename date is not assumed local.','limits':LIMITS,'lead_checked':False})
write('PAUSE_GAME.json',pause)
candidate_decks=json.loads((P.parent/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8-sig'))
candidate=next(d for d in candidate_decks['decks'] if d['id']=='filmed-qr-d0b1bba631c1')
write('QUALIFIED_DECK_CANDIDATE.json',{'game_id':GAME,'qualification':'Matching visible core only; not an exact game-bound list. Unrecorded inter-source gap and possible edits prevent exact binding.','candidate':candidate})
deck=common();deck.update({'deck_name_in_log':None,'source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','captured_at':NOW,'log_list_version':'batch LIVE_DECK_SNAPSHOT.json frozen before this review','expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':None,'energy_configuration_from_log':None,'actual_card_count':None,'capture_source_text_or_image':'../LIVE_DECK_SNAPSHOT.json; ../NEW_DECK_ENTRIES.json; QUALIFIED_DECK_CANDIDATE.json','game_version_binding_basis':'Live frozen log has no exact Scolipede / Mega Sableye list. Source has deck-slot label New deck 6 and visible matching core, but no deck QR or full list. Candidate QR belongs to 20261005_183108000_iOS.MP4, a separate source with an unrecorded gap.','conflicts_with_filmed_cards':[],'exact_list_status':'unavailable_game_bound_log_list','qualified_candidate_id':candidate['id'],'qualified_candidate_file':'QUALIFIED_DECK_CANDIDATE.json','qualified_candidate_card_count':20,'filmed_deck_label':'New deck 6','visible_named_cards':['Venipede','Whirlipede','Scolipede','Mega Sableye ex','Poke Ball',"Professor's Research",'Wally','Cyrus','Lucky Ice Pop'],'visible_energy_type':'Darkness','limits':LIMITS[:1]+['Candidate membership does not prove that unseen Poison Barb, Deceptive Needle or Copycat was in this battle deck. Exact artwork/set identifiers are not claimed.']})
write('DECK_USED.json',deck)

ev=common();ev['default_capture_policy']={'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'top_crop':'Opponent fan, clock and Energy Zone; [0,0,1170,620]','fixed_grid_is_turn_start_evidence':False,'discard_target_every_owner_turns':[2,3]}
ev['frames']=[];cropdir=P/'turn_evidence'/'crops';cropdir.mkdir(exist_ok=True)
QUAL={
 23.5:('opening',None,True,True,True,True,'All five opening cards intact before Active placement.'),
 60:('selected_start_hand',2,True,True,True,True,'Denser pre-play start frame shows all five after Whirlipede normal draw.'),
 60.5:('scheduled_plus_1',2,False,True,False,False,'Poke Ball selected/preview state; cards still present but not a clean unzoomed hand.'),
 62.5:('scheduled_plus_3',2,False,False,True,True,'Poke Ball already consumed; resolving search with four-card fan, not intact starting hand.'),
 65.5:('scheduled_plus_6',2,False,False,True,True,'Search completed and Mega Sableye ex bench action underway; four-card post-play fan, no intact start hand.'),
 84:('before_end_action',2,False,False,True,True,'Four-card ending hand before Ram attack.'),
 107.5:('selected_start_hand',4,True,True,True,True,'Five intact starting cards including Cyrus before evolution.'),
 108.5:('scheduled_plus_1',4,False,False,False,False,'Evolution consumes Whirlipede and resolves; unsuitable for intact start hand.'),
 110.5:('scheduled_plus_3',4,False,False,True,True,'Post-evolution four-card fan, not starting five.'),
 113.5:('scheduled_plus_6',4,False,False,False,True,'Energy attachment in progress with board zoom/highlight; hand is post-evolution four.'),
 114:('before_end_action',4,False,False,True,True,'Four-card ending hand before Poison Sting.'),
 149:('scheduled_plus_1_and_selected_start_hand',6,True,True,True,True,'Five intact starting cards including Lucky Ice Pop; opponent has four backs.'),
 151:('scheduled_plus_3',6,False,False,False,False,'Lucky Ice Pop consumed and resolving; no intact starting fan.'),
 154:('scheduled_plus_6',6,False,False,True,True,'Heal resolution after Item play; no intact starting hand.'),
 168:('before_end_action',6,False,False,True,True,'Three-card ending hand Whirlipede, Cyrus, Lucky Ice Pop before Venoshock.')}
for path in sorted((P/'turn_evidence').glob('t*.jpg')):
 t=float(path.stem[1:]);im=Image.open(path)
 if im.size!=(1170,2532):raise ValueError(path)
 bn=path.stem+'_bottom.jpg';tn=path.stem+'_top.jpg'
 im.crop((0,2025,1170,2532)).save(cropdir/bn,quality=95,subsampling=0)
 im.crop((0,0,1170,620)).save(cropdir/tn,quality=95,subsampling=0)
 turn=1 if 35<=t<57 else 2 if 57<=t<90 else 3 if 90<=t<104 else 4 if 104<=t<122 else 5 if 122<=t<145 else 6 if 145<=t<183 else 7 if 183<=t<=207 else None
 q=QUAL.get(t);n=q[1] if q else turn;drawend={2:59.5,4:107.5,6:148}.get(n)
 ev['frames'].append({'evidence_id':eid(t),'role':q[0] if q else 'supporting_native_state','turn_number':n,'who_played':('owner' if n%2==0 else 'opponent') if n else None,'source_video':VIDEO,'source_sha256':SHA,'draw_animation_end_seconds':drawend if q and n else None,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'actual_frame_limit_reason':'Requested FFmpeg seek time; decoded PTS not separately measured.','offset_after_draw_seconds':round(t-drawend,2) if q and n else None,'full_frame_path':str(path.relative_to(P)).replace('\\','/'),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':'turn_evidence/crops/'+bn,'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':'turn_evidence/crops/'+tn,'pixel_bounds_x0_y0_x1_y1':[0,0,1170,620]},'selected_for_start_hand':q[2] if q else False,'before_first_play':q[3] if q else None,'unzoomed':q[4] if q else None,'hand_spread':q[5] if q else None,'observation':q[6] if q else 'Retained source-local native state used to bracket recorded actions, board changes, or full-source phase coverage.','suitability_or_limit':q[6] if q else 'Supporting frame, not selected as an intact turn-start hand; clean-hand qualification is not asserted.'})
ev['discard_snapshots']=[]
for n,t,owncard,oppcard in [(2,84,"Professor's Research",'Poke Ball'),(4,114,"Professor's Research",'Poke Ball'),(6,182,'Wally','Dialga ex')]:
 for owner,card in [('OWNER',owncard),('OPP',oppcard)]:
  ev['discard_snapshots'].append({'snapshot_id':f'D{n}_{owner}','turn_number':n,'pile_owner':'owner' if owner=='OWNER' else 'opponent','source_video':VIDEO,'timestamp_seconds':t,'cards_in_view':[card],'scroll_coverage':'Top battlefield preview only; pile was never opened or scrolled','full_pile_established':False,'evidence_ids':refs(t),'limit_reason':'Only top card can be read. Unseen underlying pile contents are not reconstructed from play chronology.'})
ev['scheduled_capture_limits']=['Turn 2 and 4 +1/+3/+6 captures occur during or after first play. Each is individually qualified; denser earlier intact views supply the start hand.','Turn 6 +1 is clean pre-play; +3/+6 occur after Item consumption.','No full discard pile view appears anywhere in this source. Periodic top previews retained instead.','All hand/full/top files use original source dimensions before crops. Overview contact sheets are navigation only.']
write('TURN_EVIDENCE.json',ev)

summary={'schema':'battle-review/summary-v1','game_id':GAME,'source_video':VIDEO,'source_sha256':SHA,'reviewed_utc':NOW,'first_pass_status':'complete_awaiting_independent_acceptance','lead_accepted':False,'game_count':1,'reviewed_source_interval_seconds':[0,SRC['duration_seconds']],'source_ending_reviewed':True,'classification':'human event battle','event':'Deluxe Pack: Mega Emblem Event','battle_auto_visible':False,'deck_editor_auto_build_visible':False,'external_eligibility':'human Pause Games candidate; external writing requires lead acceptance/registration','owner':'Dacz8976','opponent':'おせち','match_date_local':'2026-10-05','match_date_basis':'UTC recording creation 2026-10-06T01:21:40Z converted to America/Chicago; phone clock 20:21-20:25 agrees. Filename date was not assumed local.','owner_deck_core':'Venipede / Whirlipede / Scolipede; two Mega Sableye ex','opponent_deck_core':'Dialga ex / Honedge / Tinkatink / Alolan Diglett','outcome':'owner_win','result_basis':'Your opponent conceded at 204-206, Victory results at 214-214.8','points':{'owner':2,'opponent':0},'turns':7,'went':'second','owner_damage_done_results':160,'exact_deck_list_status':'qualified_candidate_only','qr_in_this_source':False,'interludes':[{'seconds':[0,20],'kind':'event lobby and matchmaking/loading'},{'seconds':[93,96],'kind':'waiting for opponent to return message'},{'seconds':[193,203],'kind':'waiting for opponent before concession'},{'seconds':[207,SRC['duration_seconds']],'kind':'terminal transition and Victory results'}],'independent_check_targets':[{'seconds':[23,25],'reason':'Opening five and selected Active'},{'seconds':[59,66],'reason':'Ordinary first owner move: exact intact hand, Poke Ball input versus reveal/search/bench timing'},{'seconds':[90,104],'reason':'One full ordinary opponent turn, hidden draw/fan count, Diglett bench and Metal attachment'},{'seconds':[147,183],'reason':'Lucky Ice Pop heal/Heads return, evolution, Wally before normal Darkness, KO lifecycle and promotion'},{'seconds':[203,215],'reason':'Concession and final Victory'}],'limitations':LIMITS,'archive_authorized_by_worker':False,'external_written_by_worker':False}
write('SUMMARY.json',summary)
uncertainties={'game_id':GAME,'source_video':VIDEO,'source_sha256':SHA,'items':[{'id':'U_DECK_BINDING','severity':'recording_limit','claim':'Exact 20-card battle deck','status':'unresolved_by_source','detail':LIMITS[0],'impact':'No game-bound exact list asserted; qualified candidate retained separately.'},{'id':'U_HIDDEN','severity':'recording_limit','claim':'Opponent draw/hand identities','status':'hidden','detail':LIMITS[1],'impact':'Unknown identities remain null; visible fan counts retained.'},{'id':'U_DISCARD','severity':'recording_limit','claim':'Entire discard contents','status':'partial_view_only','detail':LIMITS[2],'impact':'No invented pile history or full-scroll claim.'},{'id':'U_TIME','severity':'measurement_limit','claim':'Exact input and decoded PTS','status':'bounded_or_unmeasured','detail':LIMITS[3],'impact':'Frame seek timestamps are source-local requests; inputs use intervals.'},{'id':'U_CONNECTION','severity':'recording_limit','claim':'Waiting-message cause','status':'unknown','detail':LIMITS[4],'impact':'Concession text, not presumed disconnect, establishes outcome.'}],'astra_required':False,'reason':'No consequential unresolved identity/outcome/order ambiguity; recording limits are explicit.'}
write('UNCERTAINTIES.json',uncertainties)

review='''# Whole-source review: 20261006_012140000_iOS.MP4

First pass complete, awaiting independent acceptance. One continuous human event battle is recorded, with setup and terminal results. Owner Dacz8976 goes second against おせち and wins by opponent concession on turn 7. The recorded final points are 2-0 and damage done is 160. No battle Auto control or QR is visible in the reviewed source. This worker has not logged, accepted, registered, or moved the source.

Source identity: 383,198,779 bytes; SHA-256 2fbf36e1f6d45a8e7fc6b1d273b0dc64c106ce1df14ac0447617e413ad79cf4e; native 1170x2532; duration 215.053333 seconds. All times below are source-local. Native filename times are requested seek timestamps, with decoded PTS unmeasured. Input consumption is bounded separately from card previews and resolution in TURN_LEDGER.json.

The UTC creation timestamp 2026-10-06T01:21:40Z converts to October 5, 2026 at 20:21:40 America/Chicago. The filmed phone clock agrees. The filename date is not used as a local match-date assumption.

At 0-20 seconds, the lobby reads Deluxe Pack: Mega Emblem Event, wins 8, and deck slot New deck 6. Matchmaking finds the named opponent. At 20 seconds the owner goes second. Before placement at 23-23.5 seconds, the five-card opening is Scolipede, Poke Ball, Professor's Research, Whirlipede, Venipede, left to right. Venipede is selected from slot 5 and placed Active at 24-25 seconds. No redraw is shown. Opponent starts Dialga ex. Both benches are empty initially.

| Turn | Source interval | Recorded sequence and resolution |
| --- | --- | --- |
| 1, opponent | 35-57 | Hidden normal draw gives five backs. Bench Honedge left, play Poke Ball and search, then reveal/bench Tinkatink center. Ends with three backs. Dialga ex remains 150 HP, no attached Energy. No attack or Energy attachment. |
| 2, owner | 57-90 | Draw Whirlipede at 59. Intact five-card hand retained at 60. Play Poke Ball (consumed 60.5-61), reveal Mega Sableye ex at 64, bench it center at 65-66. Play Research (consumed 71-72), draw Mega Sableye ex then Wally at 75/76. Attach Darkness to Venipede at 79-80, bench second Mega right at 80-83, then Ram for 20; Dialga ex reaches 130 HP by 89. Owner ending hand is Scolipede, Whirlipede, Whirlipede, Wally. |
| 3, opponent | 90-104 | Hidden normal draw gives four backs. A waiting-for-opponent-to-return message appears at 93-96. Bench Alolan Diglett right at 97-98, attach one Metal to Dialga ex at 99-100. Three backs remain. Ends without attack. |
| 4, owner | 104-123 | Draw Cyrus at 106. Intact five-card fan at 107.5. Evolve Venipede to Whirlipede at 108-110, attach Darkness to center Mega at 111-114, then Poison Sting. Dialga ex 130 to 110 by attack; Poison appears, and distinct checkup damage at 121-122 reduces it to 100. Owner hand ends Scolipede, Whirlipede, Wally, Cyrus. |
| 5, opponent | 122-145 | Hidden normal draw gives four backs. Attach second Metal to Dialga ex at 131-133. Metallic Turbo at 138-141 deals 30 to Whirlipede, 90 to 60. Its later effect generates and attaches two Metal to right-bench Alolan Diglett at 142-143. Dialga retains its own two Metal. Poison checkup at 144 takes Dialga from 100 to 90. |
| 6, owner | 145-183 | Draw Lucky Ice Pop at 147, intact five-card fan at 149. Lucky Ice Pop is consumed between 149-150, with resolving card reveal at 151; heal Whirlipede 60 to 80 at 153-154, coin Heads at 157.5 and return same Item to hand at 158. Evolve to Scolipede at 159-162; 10 damage remains, current HP 130 of 140. Consume Wally at 162-163; filmed Wally adds Colorless to Stage 2 Scolipede at 165-166. Then attach normal Darkness to right Mega at 167-168. Venoshock at 169-173 deals 120 to Poisoned Dialga ex. Ending hand is Whirlipede, Cyrus, Lucky Ice Pop. |
| 7, opponent | 183-207 | Hidden normal draw gives five backs. Attach Metal to center Tinkatink at 189-191. No attack is shown. Waiting message persists; explicit Your opponent conceded at 204-206 establishes terminal outcome. |

Turn 6 KO phases are recorded separately: damage animation at 172 and intermediate HP 20 at 172.5; Dialga remains at intermediate 20 HP at 173, then still on Active at 0 HP at 173.5; removal animation at 174-174.5 (cloud still covers the vacant outline at 174.5); first clear empty Active at 175 with Dialga in the discard preview; two-point award by 178; Alolan Diglett promotion at 181-182 with 60 HP and its two Metal intact. The right opponent bench is now empty. This is not a single instant KO event.

At the final intact board, owner Active Scolipede is 130/140 with Darkness and Colorless. Owner bench 1 is empty; bench 2 and 3 are both Mega Sableye ex at 170 HP with one Darkness each. Opponent Active Alolan Diglett is 60 HP with two Metal; Honedge left is 60 with no Energy, Tinkatink center is 60 with one Metal, right bench empty. No Tool or Stadium is visible or played. Dialga was Poisoned until removed; no other condition is visible. Both zones' large current Energy and small next-type preview are separately recorded in the ledger. The later Metallic Turbo and Wally generations are nested effects, not evidence that the next preview was already available.

At 214-214.8, Victory results show went second, turns played 7, points 2-0, damage done 160, and Scolipede as card of the game. The source ends on this result panel at 215.053333. No additional game, result, QR, or deck-editor interlude appears.

Capture supplement: opening is native before Active placement. Owner turns 2/4/6 each retain draw-timed +1/+3/+6 candidates and a before-attack ending hand. Each candidate has individual qualifications in TURN_EVIDENCE.json. Turn 2 and 4 scheduled candidates overlap or follow the first play, so denser earlier intact frames at 60 and 107.5 are selected; turn 6 +1 at 149 is intact. Full native images, bottom fifth and top crops have declared pixel bounds. Contact sheets serve navigation only. Both boards, exact ending owner hand sizes, opponent fan counts, named draw order, nested effects, and one row per all seven turns are in TURN_LEDGER.json.

The full discard piles are never opened or scrolled. Periodic top previews are retained: owner Research at turn 2 and 4, Wally at turn 6; opponent Poke Ball then Dialga ex. These previews do not establish underlying contents. Lucky Ice Pop returns on Heads and is not a discarded or newly drawn card.

The frozen live log does not contain an exact bound Scolipede / Mega Sableye list. A separate filmed QR from 20261005_183108000_iOS.MP4 yields a matching 20-card candidate, retained verbatim in QUALIFIED_DECK_CANDIDATE.json. The unrecorded gap and possible deck edits prevent a game-bound exact claim. DECK_USED.json deliberately leaves the exact game list null and states this limit. Hidden opponent identities, exact decoded PTS and exact touches likewise remain unknown or bounded. No Astra judgment is needed for these explicit source limits.
'''
(P/'REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Whole-source coverage

Fresh first pass over the complete 0-215.053333-second source, supplemented by dense native seeks at all turns, draws, plays, resolution changes, and terminal evidence. Reduced four-second contact sheets were navigation only; opening and owner-turn hand evidence uses native separately qualified frames and crops.

| Interval (seconds) | Coverage |
| --- | --- |
| 0-20 | Event lobby, New deck 6, searching/found opponent, loading, going-second notice. |
| 20-35 | All five opening cards before Active placement, Venipede placement, Dialga ex setup, empty benches. |
| 35-57 | Full opponent turn 1, hidden draw, Honedge, Poke Ball, Tinkatink, no attack. |
| 57-90 | Full owner turn 2, Whirlipede draw, exact hand candidates, search, both Research cards in reveal order, both Mega benches, Darkness, Ram. |
| 90-104 | Full ordinary opponent turn 3, waiting message, Diglett bench, Metal attachment, no attack. |
| 104-123 | Full owner turn 4, Cyrus draw, hand candidates, evolution, center Mega Energy, Poison Sting and separate Poison checkup. |
| 122-145 | Full opponent turn 5, draw, Metal, Metallic Turbo damage and later two-Metal generation, Poison checkup. |
| 145-183 | Full owner turn 6, Lucky Ice Pop draw/play/heal/Heads/return, evolution, Wally, normal Energy destination, Venoshock, HP zero/removal/empty/points/promotion separately. |
| 183-207 | Full opponent turn 7, hidden draw, Tinkatink Energy, waiting and explicit concession. |
| 207-215.053333 | Terminal transition and Victory details; actual recording end. |

- One game; no unreviewed game or intervening separate battle.
- No visible battle Auto control, including OFF; source classified human event battle.
- No QR found anywhere in the reviewed source. Deck editor Auto-build is not present.
- Every recorded game turn has a structured row with both start/end boards and explicit empty bench slots.
- Owner starting fan counts: 5/5/5 on turns 2/4/6. Ending hand counts: 4/4/3.
- Opponent fan at owner starts: 3/3/4. Opponent hidden draw names remain null.
- Opening native 23.5; selected owner starts 60, 107.5, 149; before-ending-action native 84, 114, 168. Requested +1/+3/+6 candidates all retained and individually qualified.
- Native full frames retained; bottom bounds [0,2025,1170,2532], top bounds [0,0,1170,620]. Native frame PTS was not separately measured.
- Full discard-pile scroll coverage is unavailable because neither pile is opened. Periodic partial top previews are identified.
- Exact battle-bound 20-card deck snapshot is unavailable. Qualified matching candidate is retained without claiming it is this source's exact list.
- Source gaps: no recording discontinuity is visibly identified; waiting/network UI is not filled with guessed actions. Source begins before setup and ends after result.
- Independent acceptance, CLI registration, source archival and external artifact entry remain the lead's steps. This packet is a stable first-pass submission, not lead acceptance.
'''
(P/'COVERAGE.md').write_text(coverage,encoding='utf-8')
print(json.dumps({'packet':str(P),'turns':7,'native_frames':len(ev['frames']),'source_unchanged':SHA,'status':'written'},indent=2))
