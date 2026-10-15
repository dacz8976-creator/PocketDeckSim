import json,copy,re
from pathlib import Path
from PIL import Image
P=Path(__file__).parent
S=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
V=S['video_basename'];H=S['sha256'];G='20261012_010706000_iOS_game1'
def save(n,d): (P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return 'F'+f'{t:.2f}'.replace('.','_')
def cards(names,t,basis='observed visible hand'):
 return [{'position':i+1,'name':n,'variant':None,'basis':basis,'evidence_ids':[eid(t)],'limit_reason':None} for i,n in enumerate(names)]
LP='Lucky Ice Pop';PR="Professor's Research";GB='Glimmora';PB='Poké Ball'
hands={1:([LP,'Kingambit',PR,PR],[LP,'Kingambit',PR],44.25,63),3:([LP,'Kingambit',PR,GB],[LP,'Kingambit',GB],128.4,147),5:([LP,'Kingambit',GB,'Rare Candy'],[LP,GB],190,198),7:([LP,GB,'Ilima'],[LP,GB,'Ilima'],260,264),9:([LP,GB,'Ilima','Mesagoza'],[LP,GB,'Ilima'],353.5,369),11:([LP,GB,'Ilima','Heavy Helmet'],[LP,GB,'Ilima'],474,484),13:([LP,GB,'Ilima','Glimmet'],[LP,GB,'Ilima'],532,538),15:([LP,GB,'Ilima',PB],[LP,'Ilima'],562,572),17:([LP,'Ilima',LP],[LP,'Ilima',LP],632,636),19:([LP,'Ilima',LP,'Copycat'],['Ilima',LP,LP],710,724),21:(['Ilima',LP,LP],['Ilima',LP,LP],797,802)}
# These moments bind the capture schedule to the normal draw sequence, not a fixed overview grid.
drawends={1:44,3:128,5:190,7:260,9:353,11:474,13:532,15:562,17:632,19:710,21:None}
bounds=[(1,41,66),(2,66,124),(3,124,163),(4,163,188),(5,188,206),(6,206,257),(7,257,271),(8,271,351),(9,351,376),(10,376,471),(11,471,488),(12,488,531),(13,531,540),(14,540,563),(15,563,580),(16,580,630),(17,630,645),(18,645,708),(19,708,730),(20,730,796),(21,796,810)]
# Each action below is a source observation. Automatic resolutions are kept separately.
acts={
1:[(44.5,'card_play',PR,None,'Draw Alolan Grimer then Poké Ball.'),(52,'card_play',PB,None,'Search reveals Regigigas.'),(57,'card_play','Alolan Grimer','Bench right','Bench at70HP.'),(61,'card_play','Regigigas','Bench middle','Bench at150HP; Seal of Antiquity cannot function without its named Regis.'),(64,'attack_attempt',None,'Glimmet','Visible Cannot attack / Can\'t attack banner; no attack or damage.'),(65,'end_turn',None,None,'End turn with three cards; no Energy on first turn.')],
2:[(90,'card_play',PR,None,'Opponent Research shown in discard; two hidden draws.'),(94,'energy_attachment',None,'Ralts','Attach1Psychic.'),(100,'card_play',PB,None,'Hidden Basic search.'),(115,'card_play','Mega Diancie ex','Bench left','Bench170HP.'),(123,'end_turn',None,None,'No attack shown.')],
3:[(128.6,'evolution',GB,'Active Glimmet','Evolve to90HP.'),(132,'card_play',PR,None,'Draw Alolan Muk then Glimmora.'),(140,'evolution','Alolan Muk','Bench Alolan Grimer','Evolve to110HP; Power of Alchemy suppresses Basic abilities on both boards.'),(145,'energy_attachment',None,'Active Glimmora','Attach1Darkness.'),(148,'attack','Venomous Hit','Ralts','50damage including Darkness weakness; poison. Ralts60->10 then poison KO.')],
4:[(169,'energy_attachment',None,'Mega Diancie ex','Attach1Psychic; no attack.'),(187,'end_turn',None,None,'Pass.')],
5:[(191,'card_play','Rare Candy','Pawniard','Select Kingambit and evolve directly;50HP Pawniard becomes140HP Kingambit.'),(196,'energy_attachment',None,'Regigigas','Attach1Darkness, first.'),(200,'attack','Venomous Hit','Mega Diancie ex','30damage and poison:170->140->130.')],
6:[(220,'card_play',PB,None,'Opponent hidden Basic search.'),(227,'card_play','Indeedee ex','Bench left','Bench130HP. Ability unavailable while Muk suppresses Basics.'),(230,'energy_attachment',None,'Mega Diancie ex','SecondPsychic.'),(254,'end_turn',None,None,'No attack; poison130->120 at checkup.')],
7:[(261,'energy_attachment',None,'Regigigas','SecondDarkness.'),(264,'attack','Venomous Hit','Mega Diancie ex','30damage and poison:120->90->80.')],
8:[(277,'energy_attachment',None,'Mega Diancie ex','ThirdPsychic.'),(292,'card_play',LP,'Mega Diancie ex','Heal20:80->100; heads returns Pop.'),(303,'card_play',LP,'Mega Diancie ex','Heal20:100->120; tails discards Pop.'),(326,'card_play','Giant Cape','Mega Diancie ex','Effective max170->190 and current120->140, not healing.'),(334,'attack','Brilliant Storm','Glimmora','100damage, knockout.')],
9:[(354,'card_play','Mesagoza',None,'Place Stadium.'),(360,'ability','Mesagoza',None,'Activate Stadium: tails; no search/card found.'),(367,'energy_attachment',None,'Regigigas','ThirdDarkness.'),(369,'attack','Giga Turbo','Mega Diancie ex','100damage:130->30; nested attach1Colorless fromEnergyZone to AlolanMuk. Poison30->20.')],
10:[(392,'energy_attachment',None,'Mega Diancie ex','FourthPsychic.'),(428,'card_play','Peculiar Plaza',None,'Replace Mesagoza; Psychic retreat costs2less.'),(434,'card_play','Potion','Mega Diancie ex','Heal20:20->40.'),(439,'card_play','Sabrina','Owner Active','Owner chooses AlolanMuk to replace Regigigas at445–447; forced switch no payment.'),(464,'retreat',None,'Mega Diancie ex -> Indeedee ex','Retreat without Energy payment under Plaza; poison clears.'),(470,'end_turn',None,None,'No attack.')],
11:[(477,'card_play','Heavy Helmet','Kingambit','Attach tool on Bench.'),(484,'energy_attachment',None,'Kingambit','FirstDarkness.'),(487,'end_turn',None,None,'Pass; Muk has only1Colorless, cannot attack.')],
12:[(500,'energy_attachment',None,'Mega Diancie ex','FifthPsychic.'),(516,'card_play','Ralts','Bench right','Bench60HP.'),(530,'end_turn',None,None,'No attack; Basic abilities remain suppressed.')],
13:[(533,'card_play','Glimmet','Bench middle','Bench60HP.'),(537,'energy_attachment',None,'Alolan Muk','FirstDarkness, total2Energy including Colorless.'),(539,'end_turn',None,None,'Pass; no attack.')],
14:[(555,'evolution','Kirlia','Ralts','Evolve80HP.'),(557,'energy_attachment',None,'Kirlia','FirstPsychic.'),(560,'card_play',PB,None,'Opponent PokéBall shown, searched identity hidden.'),(562,'end_turn',None,None,'Pass.')],
15:[(563,'card_play',PB,None,'Owner PokéBall no Basic found; hand stays3 after removing Ball. No Basic remaining in filmed deck after both Glimmet, Pawniard, Grimer and Regigigas in play.'),(567,'evolution',GB,'Bench Glimmet','Evolve90HP.'),(571,'energy_attachment',None,'Alolan Muk','SecondDarkness, total3 including Colorless.'),(574,'attack','Sludge Bomb','Indeedee ex','90damage including weakness:130->40.')],
16:[(588,'evolution','Mega Gardevoir ex','Kirlia','Evolve210HP.'),(593,'energy_attachment',None,'Mega Gardevoir ex','SecondPsychic.'),(595,'retreat',None,'Indeedee ex -> Mega Gardevoir ex','Plaza reduces retreat to0; no Energy paid.'),(606,'attack','Fantasia Force','Alolan Muk','110damage, knockout; nested take3Psychic fromEnergyZone and attach to Indeedee ex at614–617.')],
17:[(633,'energy_attachment',None,'Glimmora','FirstDarkness.'),(637,'attack','Venomous Hit','Mega Gardevoir ex','50damage including weakness:210->160; poison ->150.')],
18:[(652,'ability','Watch Over','Mega Gardevoir ex','Indeedee heals20:150->170 after Muk gone.'),(666,'energy_attachment',None,'Mega Gardevoir ex','ThirdPsychic.'),(706,'end_turn',None,None,'No attack; poison170->160.')],
19:[(711,'card_play','Copycat',None,'Shuffle LuckyIcePop/Ilima/LuckyIcePop remaining3; draw3 matching opponent fan3. New hand Ilima, LuckyIcePop, LuckyIcePop at721.'),(723,'energy_attachment',None,'Kingambit','SecondDarkness.'),(726,'attack','Venomous Hit','Mega Gardevoir ex','50damage:160->110; poison->100. LuckyIcePop viewed720; not consumed or confirmed no-effect play.')],
20:[(739,'card_play','Indeedee ex','Bench middle','Second Indeedee,130HP.'),(747,'ability','Watch Over','Mega Gardevoir ex','First Indeedee heal20:100->120.'),(752,'ability','Watch Over','Mega Gardevoir ex','Second Indeedee heal20:120->140.'),(766,'energy_attachment',None,'Mega Diancie ex','SixthPsychic.'),(771,'attack','Fantasia Force','Glimmora','110damage, knockout; nested attach3Psychic fromEnergyZone to new Indeedee ex. ShatteringCrystal tails gives opponent secondpoint.')],
21:[(801,'attack',"Overlord's Blade",'Mega Gardevoir ex','Knockout from130HP; 180base after three owner KOs, +20weakness=200 inferred from filmed card text. Award3Mega points; score ends3-2.')]
}
auto={3:['Poison checkup10 KOs Ralts; owner firstpoint. Opponent promotes MegaDiancie.'],5:['Poison10 ->130HP.'],6:['Poison10 ->120HP.'],7:['Poison10 ->80HP.'],8:['Glimmora ShatteringCrystal heads338–344: no opponent point. Owner promotesRegigigas346–350. Poison10 ->Diancie130HP.'],9:['GigaTurbo nestedColorless toMuk; poison10 ->Diancie20.'],10:['Sabrina forced owner choiceMuk. Retreat clearsDianciepoison.'],16:['Muk KO, opponent firstpoint620. PowerAlchemy ends. Owner promotesGlimmora624–628.'],17:['Poison10 ->MegaGardevoir150.'],18:['Poison10 ->MegaGardevoir160.'],19:['Poison10 ->MegaGardevoir100.'],20:['ShatteringCrystal tails783; opponent secondpoint787. Owner selectsKingambit793. Poison10 ->MegaGardevoir130.'],21:['MegaGardevoir KO805. Three-point award808; victory812–819.']}
draws={1:[('normal_draw',[PR],44,None),('supporter_draw',['Alolan Grimer',PB],48,1),('search',['Regigigas'],55,2)],3:[('normal_draw',[GB],128,None),('supporter_draw',['Alolan Muk',GB],136,2)],5:[('normal_draw',['Rare Candy'],190,None)],7:[('normal_draw',['Ilima'],260,None)],9:[('normal_draw',['Mesagoza'],353,None),('stadium_search',[],364,2)],11:[('normal_draw',['Heavy Helmet'],474,None)],13:[('normal_draw',['Glimmet'],532,None)],15:[('normal_draw',[PB],562,None),('search',[],565,1)],17:[('normal_draw',[LP],632,None)],19:[('normal_draw',['Copycat'],710,None),('supporter_draw',['Ilima',LP,LP],721,1)],21:[]}
source=[{'video_basename':V,'sha256':H,'source_json':'SOURCE.json'}]
opening_names=[LP,'Kingambit','Glimmet','Pawniard',PR]
limits=['Opponent draws/search identities hidden unless later publicly played; handfan overlap gives ranges for large fans.','Neither opened discard pile appears in the recording. Play-derived histories are inference, not pile snapshots.','Several first moves occur immediately after a zoomed normal draw. Candidate+1/+3/+6 can already be post-play; actual pre-play evidence and limits are individually identified.','Exact filmed QR semantic list verified; dated readable PauseGames live-log deck snapshot is absent. QR does not resolve artwork/printing aliases.','Native seek requested times are retained; exact decoded PTS was not measured. Turn transition timings are bounded to nearby source frames, not frame-accurate.']
# Retain every native action/candidate image and catalog it. Hand crops are original-resolution.
paths={}
for folder in ['dense_native','coarse_native','turn_evidence']:
 for f in (P/folder).glob('t*.jpg'):
  if not re.fullmatch(r't\d+\.\d+',f.stem):continue
  t=float(f.stem[1:]);paths[t]=f
crop_times={25}
for n,(sh,eh,st,et) in hands.items():crop_times.update([st,et])
for n,d in drawends.items():
 if d is not None:crop_times.update([d+1,d+3,d+6])
frames=[]
for t,f in sorted(paths.items()):
 im=Image.open(f);w,h=im.size;fr={'evidence_id':eid(t),'role':'native_action_or_continuity','source_video':V,'source_sha256':H,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'full_frame_path':f.relative_to(P).as_posix(),'native_dimensions':{'width':w,'height':h}}
 if t in crop_times:
  out=P/'turn_evidence';bot=out/f'{f.stem}_bottom.jpg';top=out/f'{f.stem}_top.jpg';im.crop((0,2025,w,h)).save(bot,quality=95);im.crop((0,0,w,650)).save(top,quality=95)
  fr.update(bottom_crop={'path':bot.relative_to(P).as_posix(),'pixel_bounds_x0_y0_x1_y1':[0,2025,w,h]},top_crop={'path':top.relative_to(P).as_posix(),'pixel_bounds_x0_y0_x1_y1':[0,0,w,650]})
 for n,d in drawends.items():
  if d is not None and t-d in [1,3,6]:fr.update(role='draw_timed_candidate',turn_number=n,who_played='owner',draw_animation_end_seconds=d,offset_after_draw_seconds=t-d,selected_for_start_hand=False,suitability_or_limit='Inspect alongside first-move timing; later candidates may show post-play hand.')
 for n,(sh,eh,st,et) in hands.items():
  if t==st:fr.update(role='selected_start_hand',turn_number=n,who_played='owner',selected_for_start_hand=True,before_first_play=True,unzoomed=n not in [5,7,9,15],hand_spread=n not in [5,7,9,15],suitability_or_limit='Draw/reveal and continuity establish names; zoom or fast move limits full post-draw fan.' if n in [5,7,9,15] else 'Selected native start hand before first voluntary move.')
  if t==et:fr.update(role='before_end_hand',turn_number=n,who_played='owner')
 if t==25:fr.update(role='opening_hand')
 frames.append(fr)
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':source,'frames':frames,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'native_resolution_required':True,'bottom_crop_height_fraction':.2,'fixed_grid_is_turn_start_evidence':False},'discard_snapshots':[{'snapshot_id':'not_shown_owner','pile_owner':'owner','cards_in_view':None,'full_pile_established':False,'limit_reason':'No opened owner discard pile anywhere in0–820.845s.'},{'snapshot_id':'not_shown_opponent','pile_owner':'opponent','cards_in_view':None,'full_pile_established':False,'limit_reason':'No opened opponent discard pile anywhere in0–820.845s.'}],'scheduled_capture_limits':limits})
save('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'review_date':'2026-10-12','sources':source,'destination':S['requested_log'],'deck_name':'Glimmora / Alolan Muk / Kingambit / Regigigas','queue':'Deluxe Pack: Mega Emblem Event','match_date_local':'2026-10-11','match_date_basis':'SOURCE_TIME.json UTCcreation_time convertedAmerica/Chicago','opening':{'source_video':V,'timestamp_seconds':25,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':cards(opening_names,25),'selected_active':{'name':'Glimmet','opening_position':3,'source_video':V,'timestamp_seconds':26,'evidence_ids':[eid(26)]},'redraw_or_replacement':'none observed','before_active_placement':True,'status':'complete','evidence_ids':[eid(25)],'limit_reason':None,'bench_setup':{'name':'Pawniard','timestamp_seconds':32}},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'review_ready_pending_independent_acceptance','outcome':{'owner':'win','method':'points','points':[3,2],'turns':21,'damage_done_displayed':600,'evidence_ids':[eid(819)]},'limits':limits,'lead_checked':False})
# Exact QR stays explicitly distinct from unavailable live-log fields.
qr=json.loads((P/'QR_DECODE.json').read_text(encoding='utf-8'))
prepared=json.loads((P.parent/'PREPARED_FILMED_DECK.json').read_text(encoding='utf-8'))['deck']
save('DECK_USED.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':source,'deck_name_in_log':None,'source_url':S['requested_log'],'captured_at':None,'expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':None,'energy_configuration_from_log':None,'actual_card_count':None,'capture_source_text_or_image':None,'exact_list_status':'live_log_list_missing','game_version_binding_basis':'QR at 0 s closes directly into New deck 16 in the Event queue at 2 s. No intervening deck edit is shown; all filmed owner cards agree with the semantic QR list.','conflicts_with_filmed_cards':[],'filmed_deck_snapshot':{'status':'verified_filmed_QR','card_slot_count':20,'cards_in_qr_order':[{'name':e['name'],'semantic_entity_id':e['entity_id']} for e in qr['resolved_entities'] for _ in range(e['count'])] if 'resolved_entities' in qr else prepared['cards_in_log_order'],'counts_by_semantic_name':[{k:v for k,v in c.items() if k in ['name','count']} for c in prepared['counts_by_name_and_variant']],'energy':'Darkness','provenance':'QR_DECODE.json binds the current filmed code. Semantic names are established; exact printing aliases are not.'},'limits':['Live-log deck not available in the fresh owner log; no verified dated twenty-slot live snapshot.','QR aliases do not prove exact printed artwork or rarity.']})

# Board snapshots are reconciled against native boundary frames and public changes.
def mon(name,hp,maximum,energy=None,tool='none',cond=None,pos=None):
 e=energy or {};return {'name':name,'variant':'Visible functional card text; artwork not fully classified','bench_position':pos,'hp_now':hp,'hp_max':maximum,'hp_max_basis':'Filmed card HP and visible Giant Cape +20 when present','damage':maximum-hp,'attached_energy':{'total':sum(e.values()),'by_type':e},'tool':tool,'special_conditions':cond or [],'active_effects':[],'evidence_ids':[],'status':'observed_and_reconciled','limit_reason':None}
gl=mon('Glimmet',60,60);pa=mon('Pawniard',50,50);ra=mon('Ralts',60,60)
state={'owner':{'active':gl,'bench':[pa,None,None],'points':0},'opponent':{'active':ra,'bench':[None,None,None],'points':0},'stadium':'none'}
states=[]
for n,start,end in bounds:
 st=copy.deepcopy(state);o=state['owner'];q=state['opponent']
 if n==1:o['bench'][1]=mon('Regigigas',150,150);o['bench'][2]=mon('Alolan Grimer',70,70)
 if n==2:q['active']['attached_energy']={'total':1,'by_type':{'Psychic':1}};q['bench'][0]=mon('Mega Diancie ex',170,170)
 if n==3:o['active']=mon(GB,90,90,{'Darkness':1});o['bench'][2]=mon('Alolan Muk',110,110);o['points']=1;q['active']=q['bench'][0];q['bench'][0]=None
 if n==4:q['active']['attached_energy']={'total':1,'by_type':{'Psychic':1}}
 if n==5:o['bench'][0]=mon('Kingambit',140,140);o['bench'][1]['attached_energy']={'total':1,'by_type':{'Darkness':1}};q['active']=mon('Mega Diancie ex',130,170,{'Psychic':1},cond=['Poisoned'])
 if n==6:q['active']=mon('Mega Diancie ex',120,170,{'Psychic':2},cond=['Poisoned']);q['bench'][0]=mon('Indeedee ex',130,130)
 if n==7:o['bench'][1]['attached_energy']={'total':2,'by_type':{'Darkness':2}};q['active']=mon('Mega Diancie ex',80,170,{'Psychic':2},cond=['Poisoned'])
 if n==8:o['active']=o['bench'][1];o['bench'][1]=None;q['active']=mon('Mega Diancie ex',130,190,{'Psychic':3},'Giant Cape',['Poisoned'])
 if n==9:o['active']['attached_energy']={'total':3,'by_type':{'Darkness':3}};o['bench'][2]['attached_energy']={'total':1,'by_type':{'Colorless':1}};q['active']=mon('Mega Diancie ex',20,190,{'Psychic':3},'Giant Cape',['Poisoned']);state['stadium']='Mesagoza'
 if n==10:o['bench'][2]=o['active'];o['active']=mon('Alolan Muk',110,110,{'Colorless':1});q['bench'][0]=mon('Mega Diancie ex',40,190,{'Psychic':4},'Giant Cape');q['active']=mon('Indeedee ex',130,130);state['stadium']='Peculiar Plaza'
 if n==11:o['bench'][0]=mon('Kingambit',140,140,{'Darkness':1},'Heavy Helmet')
 if n==12:q['bench'][2]=mon('Ralts',60,60,{'Psychic':1})
 if n==13:o['bench'][1]=mon('Glimmet',60,60);o['active']['attached_energy']={'total':2,'by_type':{'Darkness':1,'Colorless':1}}
 if n==14:q['bench'][2]=mon('Kirlia',80,80,{'Psychic':2})
 if n==15:o['bench'][1]=mon(GB,90,90);o['active']['attached_energy']={'total':3,'by_type':{'Darkness':2,'Colorless':1}};q['active']=mon('Indeedee ex',40,130)
 if n==16:o['active']=o['bench'][1];o['bench'][1]=None;q['active']=mon('Mega Gardevoir ex',210,210,{'Psychic':2});q['bench'][2]=mon('Indeedee ex',40,130,{'Psychic':3});q['bench'][0]['attached_energy']={'total':5,'by_type':{'Psychic':5}};q['points']=1
 if n==17:o['active']['attached_energy']={'total':1,'by_type':{'Darkness':1}};q['active']=mon('Mega Gardevoir ex',150,210,{'Psychic':2},cond=['Poisoned'])
 if n==18:q['active']=mon('Mega Gardevoir ex',160,210,{'Psychic':3},cond=['Poisoned'])
 if n==19:o['active']['attached_energy']={'total':2,'by_type':{'Darkness':2}};q['active']=mon('Mega Gardevoir ex',100,210,{'Psychic':3},cond=['Poisoned'])
 if n==20:q['bench'][1]=mon('Indeedee ex',130,130,{'Psychic':3});q['bench'][0]['attached_energy']={'total':6,'by_type':{'Psychic':6}};q['active']=mon('Mega Gardevoir ex',130,210,{'Psychic':3},cond=['Poisoned']);o['active']=o['bench'][0];o['bench'][0]=None;q['points']=2
 if n==21:q['active']=None;o['points']=3
 states.append((st,copy.deepcopy(state)))

def clean(s):
 s=re.sub(r'(?<=[a-z])(?=[A-Z])',' ',s);s=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',s);s=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',s)
 for a,b in [('Psychic.', ' Psychic.'),('Colorless.', ' Colorless.'),('->',' -> '),('Mega Diancie','Mega Diancie'),('cannot function','cannot function')]:s=s.replace(a,b)
 s=re.sub(r'([,:;])(?=\S)',r'\1 ',s)
 s=s.replace('secondpoint','second point').replace('handfan','hand fan').replace('PauseGames','Pause Games')
 return re.sub(r' {2,}',' ',s)
# Correct the source-specific timing and attachments after closer native inspection.
acts[1][0]=(45,'card_play',PR,None,'Draw Alolan Grimer then Poké Ball; the second card is immediately played and is never held in a lasting fanned hand.')
acts[1][1]=(51.8,'card_play',PB,None,'Search reveals Regigigas at 53.8-55 s.')
acts[2][0]=(90,'card_play',PR,None,'Opponent Research is visibly played, with two hidden draws.')
acts[12][0]=(518,'energy_attachment',None,'Ralts','First Psychic after benching Ralts.')
acts[12][1],acts[12][0]=acts[12][0],acts[12][1]
acts[12]=[(516,'card_play','Ralts','Bench right','Bench at 60 HP.'),(518,'energy_attachment',None,'Ralts','First Psychic.'),(530,'end_turn',None,None,'No attack; Basic abilities remain suppressed.')]
acts[14][1]=(557,'energy_attachment',None,'Kirlia','Second Psychic.')
acts[14]=acts[14][:2]+[(557.5,'end_turn',None,None,'No attack. Owner turn 15 banner appears at 558 s. No opponent Poké Ball is played here; the Ball at 560 s belongs to the owner on turn 15.')]
acts[16][1]=(593,'energy_attachment',None,'Mega Diancie ex','Fifth Psychic; Mega Gardevoir carries its two inherited Psychic.')
acts[19][1]=(723,'energy_attachment',None,'Glimmora','Second Darkness to the Active Glimmora. Kingambit receives its second Darkness on turn 21.')
acts[21]=[(799,'energy_attachment',None,'Kingambit','Second Darkness.'),acts[21][0]]
hands[1]=(hands[1][0],hands[1][1],44.5,63)
hands[5]=(hands[5][0],hands[5][1],190,196)
hands[15]=(hands[15][0],hands[15][1],559.5,572);drawends[15]=560
draws[15][0]=('normal_draw',[PB],560.5,None);draws[15][1]=('search',[],563,1)
acts[15][0]=(561.5,'card_play',PB,None,'No Basic found. The Ball is revealed around 560 s and immediately played. The prior three-card fan plus this named draw establishes four before the play, without a complete unzoomed four-card fan.')
bounds=[(n,558 if n==15 else s,558 if n==14 else e) for n,s,e in bounds]
for n,(st,en) in enumerate(states,1):
 if n==21:en['owner']['active']['attached_energy']={'total':2,'by_type':{'Darkness':2}}

boardtimes={1:(41,68),2:(68,124),3:(124,168),4:(168,188),5:(188,208),6:(208,256),7:(256,272),8:(272,352),9:(352,376),10:(376,476),11:(476,488),12:(488,532),13:(532,540),14:(540,558),15:(558,580),16:(580,628),17:(628,644),18:(644,712),19:(712,732),20:(732,798),21:(798,810)}
def board(s,n,phase,t,acting):
 b={'turn_number_displayed':n,'phase':phase,'stadium':s['stadium'],'shared_effects':[],'evidence_ids':[eid(t)]}
 muk=any(x and x['name']=='Alolan Muk' for x in [s['owner']['active']]+s['owner']['bench'])
 for player in ['owner','opponent']:
  d=s[player];typ='Darkness' if player=='owner' else 'Psychic';bench=[]
  for i,x in enumerate(d['bench']):
   if x:x=copy.deepcopy(x);x['bench_position']=i+1;bench.append(x)
  active=copy.deepcopy(d['active']);mons=([active] if active else [])+bench
  for x in mons:
   x['evidence_ids']=[eid(t)]
   if muk and x['name'] in ['Regigigas','Ralts','Mega Diancie ex','Indeedee ex','Glimmet','Pawniard']:
    x['active_effects']=[{'name':'Power of Alchemy','source':'Owner Alolan Muk','restriction':'Basic Pokemon have no Abilities','expiry':'While Alolan Muk remains in play'}]
   elif x['name']=='Regigigas':x['active_effects']=[{'name':'Seal of Antiquity','restriction':'Cannot attack without the named Regis on the Bench','expiry':'Until condition changes or ability is suppressed','basis':'Filmed card text and no named Regis on this board'}]
   if x['tool']=='Heavy Helmet':x['active_effects'].append({'name':'Heavy Helmet','restriction':'Takes 20 less attack damage if retreat cost is at least 3','expiry':'While tool remains attached','basis':'Filmed tool text'})
  available=player==acting and phase=='start' and not(n==1 and player=='owner')
  b[player]={'active':active,'bench_in_position_order':bench,'bench_slot_names':[x['name'] if x else None for x in d['bench']], 'points':d['points'],'board_effects':[],'energy_zone':{'this_turn':{'type':typ if available else None,'count':1 if available else 0,'available':available},'next':{'type':typ if player=='owner' else None,'count':1 if player=='owner' else None,'available':True if player=='owner' else None},'basis':'Visible owner Darkness next icon; opponent future Energy is hidden. This-turn availability follows active turn and visible use.','evidence_ids':[eid(t)],'limit_reason':'Opponent next Energy identity/count is hidden.'},'evidence_ids':[eid(t)],'status':'observed_and_reconciled','limit_reason':None}
 if phase=='end' and n==21:b['owner']['energy_zone']['this_turn']={'type':None,'count':0,'available':False}
 if s['stadium']=='Peculiar Plaza':b['shared_effects']=[{'name':'Peculiar Plaza','restriction':'Retreat cost of Psychic Pokemon is 2 less','expiry':'While Stadium remains in play'}]
 return b

fan={1:(4,None),3:(5,None),5:(6,None),7:(None,[7,8]),9:(None,[7,8]),11:(5,None),13:(2,None),15:(2,None),17:(2,None),19:(3,None),21:(3,None)}
turnrows=[]
for i,(n,start,end) in enumerate(bounds):
 who='owner' if n%2 else 'opponent';st,en=states[i];bs,be=boardtimes[n]
 row={'turn_number':n,'who_played':who,'source_video':V,'timing':{'start_seconds':start,'draw_animation_end_seconds':drawends.get(n),'draw_end_basis':'Native reveal sequence, approximately within 0.5 s' if n in drawends and drawends[n] else 'No normal draw on turn 21 because deck is empty' if n==21 else 'Opponent draw hidden','first_voluntary_move_seconds':acts[n][0][0],'before_end_action_seconds':hands[n][3] if n in hands else None,'end_after_resolution_seconds':end},'plays_in_order':[],'automatic_events_in_order':[clean(x) for x in auto.get(n,[])],'board_at_start':board(st,n,'start',bs,who),'board_after':board(en,n,'end',be,who),'discard_snapshot_ids':['not_shown_owner','not_shown_opponent'],'turn_evidence_ids':[eid(bs),eid(be)],'limits':['Board boundary native views can fall just after the next turn animation or draw; their public HP/Energy/points are unchanged. Exact turn-transition PTS is not claimed.']}
 for order,(t,kind,card,target,result) in enumerate(acts[n],1):
  nearest=min(paths,key=lambda v:abs(v-t));energy=None
  if kind=='energy_attachment':energy={'type':'Darkness' if who=='owner' else 'Psychic','count':1,'destination':target,'retreat_payment_by_type':None}
  if kind=='retreat':energy={'type':None,'count':0,'destination':None,'retreat_payment_by_type':{}}
  row['plays_in_order'].append({'order':order,'kind':kind,'card_name':card,'target':target,'energy':energy,'result':clean(result),'prompt_text':"Can't attack" if kind=='attack_attempt' else None,'response':None,'nested_events_in_order':None,'hand_count_after':None,'source_video':V,'timestamp_seconds':t,'evidence_ids':[eid(nearest)],'basis':'Observed play/transition; public attack arithmetic is identified as inference where needed.','limit_reason':None})
 row['draws_and_searches']=[]
 if who=='owner':
  sh,eh,ht,et=hands[n];lim='Card zoom or immediate play prevents an unzoomed complete post-draw fan; identities/count reconcile from prior hand and filmed reveal.' if n in [3,5,7,9,13,15] else None
  hand={'cards_left_to_right':cards(sh,ht,'Observed hand or prior visible hand plus individually revealed new card' if lim else 'Observed visible hand'),'count':len(sh),'basis':'Visible fan and named draw, duplicates preserved','evidence_ids':[eid(ht)],'status':'complete_with_recording_limits' if lim else 'observed','limit_reason':lim}
  row['hand_at_start']=copy.deepcopy(hand);row['owner_hand_start']=hand
  if n==15:
   row['hand_at_start']['basis']=row['owner_hand_start']['basis']='Inference from observed prior three-card fan at 559.5 s plus individually revealed Poké Ball at 560.5 s'
   for obj in [row['hand_at_start'],row['owner_hand_start']]:
    obj['evidence_ids']=[eid(559.5),eid(560.5)];obj['cards_left_to_right'][-1]['evidence_ids']=[eid(560.5)];obj['cards_left_to_right'][-1]['basis']='Named normal draw before immediate play; full fan position is inferred appended slot'
  row['owner_hand_end']={'cards_left_to_right':cards(eh,et),'count':len(eh),'basis':'Directly counted visible pre-end hand; attack does not consume hand cards','evidence_ids':[eid(et)],'status':'observed','limit_reason':None}
  c,r=fan[n];row['opponent_hand_at_owner_turn_start']={'count':c,'supported_range':r,'count_method':'Count visible backs in native top crop','basis':'Observed fan','evidence_ids':[eid(ht)],'limit_reason':'Large overlapping fan prevents exact separation.' if r else None}
  for kind,names,t,order in draws.get(n,[]):
   nearest=min(paths,key=lambda v:abs(v-t));row['draws_and_searches'].append({'kind':kind,'caused_by':None if kind=='normal_draw' else row['plays_in_order'][order-1]['card_name'],'linked_play_order':order,'cards_in_reveal_order':[{'name':name,'reveal_position':j+1,'source_video':V,'timestamp_seconds':t,'evidence_ids':[eid(nearest)],'basis':'Filmed individual reveal or later completed same draw sequence','limit_reason':None} for j,name in enumerate(names)],'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':[LP,'Ilima',LP] if n==19 and kind=='supporter_draw' else None,'source_video':V,'timestamp_seconds':t,'evidence_ids':[eid(nearest)],'limit_reason':'Tails, no card found.' if kind=='stadium_search' else 'No Basic found; no card enters hand.' if n==15 and kind=='search' else None})
  if n==21:row['limits'].append('No normal draw: empty deck after Copycat redrew all three shuffled cards. Candidate frames use turn-transition offsets, not invented draw offsets.')
  if lim:row['limits'].append(lim)
 else:
  row['hand_at_start']={'cards_left_to_right':None,'count':None,'basis':'Hidden opponent hand backs','evidence_ids':[eid(bs)],'status':'hidden','limit_reason':'Identities hidden; only revealed plays transcribed.'};row['owner_hand_start']={'cards_left_to_right':None,'count':None,'status':'not_applicable','evidence_ids':[],'limit_reason':'Opponent turn'};row['owner_hand_end']={'cards_left_to_right':None,'count':None,'status':'not_applicable','evidence_ids':[],'limit_reason':'Opponent turn'}
  row['opponent_hand_at_owner_turn_start']={'count':None,'supported_range':None,'evidence_ids':[],'limit_reason':'Opponent turn'}
  row['draws_and_searches']=[{'kind':'normal_draw','cards_in_reveal_order':[{'name':None,'limit_reason':'Opponent card back only'}],'source_video':V,'timestamp_seconds':start,'evidence_ids':[eid(bs)],'limit_reason':'Hidden identity'}]
  for play in row['plays_in_order']:
   if play['card_name'] in [PR,PB]:row['draws_and_searches'].append({'kind':'supporter_draw' if play['card_name']==PR else 'search','linked_play_order':play['order'],'cards_in_reveal_order':[{'name':None,'limit_reason':'Hidden opponent reveal' } for _ in range(2 if play['card_name']==PR else 1)],'source_video':V,'timestamp_seconds':play['timestamp_seconds'],'evidence_ids':play['evidence_ids'],'limit_reason':'Searched/drawn identity not exposed.'})
 row['limits'].append('Opened discard snapshots not shown in this turn or elsewhere in the recording.')
 turnrows.append(row)
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':source,'turns':turnrows,'limits':limits,'basis':'Whole-source native frame review and bounded dense action sequences. Boundary HP/Energy uses observed public state and visible transitions; hidden identities remain null.'})
for row in turnrows:
 for group in row['draws_and_searches']:
  if row['turn_number']==1 and group['kind']=='supporter_draw':
   for c,t in zip(group['cards_in_reveal_order'],[48,51.8]):c['timestamp_seconds']=t;c['evidence_ids']=[eid(t)];c['basis']='Named reveal and immediate play within the same Research draw sequence'
  if row['turn_number']==1 and group['kind']=='search':
   group['timestamp_seconds']=53.8;group['cards_in_reveal_order'][0].update(timestamp_seconds=53.8,evidence_ids=[eid(53.8)])
  if row['turn_number']==3 and group['kind']=='supporter_draw':
   for c,t in zip(group['cards_in_reveal_order'],[137,139]):c['timestamp_seconds']=t;c['evidence_ids']=[eid(t)]
  if row['turn_number']==19 and group['kind']=='supporter_draw':
   for c,t in zip(group['cards_in_reveal_order'],[718,719,719.5]):c['timestamp_seconds']=t;c['evidence_ids']=[eid(t)];c['basis']='Individually revealed card in the Copycat draw sequence; final three-card fan verifies identities/order'
 for key in ['board_at_start','board_after']:
  row[key]['turn_number_displayed']=None;row[key]['turn_number_basis']='Ledger turn inferred from adjacent visible turn banners, not a persistent on-board display';row[key]['evidence_source_seconds']=boardtimes[row['turn_number']][0 if key=='board_at_start' else 1]
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':source,'turns':turnrows,'limits':[clean(x) for x in limits],'basis':'Whole-source native frame review and bounded dense action sequences. Boundary HP/Energy uses observed public state and visible transitions; hidden identities remain null.'})

# Refresh selected frame/candidate metadata after precise draw-window reconciliation.
ev=json.loads((P/'TURN_EVIDENCE.json').read_text(encoding='utf-8'));frmap={f['requested_source_seconds']:f for f in ev['frames']}
for f in ev['frames']:
 if f.get('selected_for_start_hand') and f['requested_source_seconds'] not in [v[2] for v in hands.values()]:
  f.update(selected_for_start_hand=False,before_first_play=None,role='native_action_or_continuity',suitability_or_limit='Retained continuity frame; not the selected start hand.')
for n,(sh,eh,ht,et) in hands.items():
 capture_schedule=([ht,et]+[drawends[n]+x for x in [1,3,6]] if drawends[n] is not None else [ht,et,797,799,802])
 if n==15:capture_schedule.append(560.5)
 for t in capture_schedule:
  if t not in frmap:continue
  f=frmap[t];im=Image.open(P/f['full_frame_path']);w,h=im.size
  bot=P/'turn_evidence'/f'capture_{t:.2f}_bottom.jpg';top=P/'turn_evidence'/f'capture_{t:.2f}_top.jpg';im.crop((0,2025,w,h)).save(bot,quality=95);im.crop((0,0,w,650)).save(top,quality=95)
  f['bottom_crop']={'path':bot.relative_to(P).as_posix(),'pixel_bounds_x0_y0_x1_y1':[0,2025,w,h]};f['top_crop']={'path':top.relative_to(P).as_posix(),'pixel_bounds_x0_y0_x1_y1':[0,0,w,650]}
  if t==ht:f.update(role='prior_hand_before_normal_draw' if n==15 else 'selected_start_hand',turn_number=n,who_played='owner',selected_for_start_hand=n!=15,before_first_play=True,unzoomed=n not in [3,5,7,9,13],hand_spread=n not in [3,5,7,9,13],suitability_or_limit='Prior three-card fan only. Poké Ball is individually revealed at 560.5 s and immediately played; no full unzoomed four-card fan is established.' if n==15 else 'Zoom/instant play limits a full post-draw fan; use named draw plus prior hand continuity.' if n in [3,5,7,9,13] else 'Clear post-draw pre-play native hand.')
  elif t==et:f.update(role='before_end_hand',turn_number=n,who_played='owner')
  else:f.update(role='draw_timed_candidate' if n!=21 else 'turn_transition_candidate_no_draw',turn_number=n,who_played='owner',draw_animation_end_seconds=drawends[n],offset_after_draw_seconds=t-drawends[n] if drawends[n] is not None else None,selected_for_start_hand=False,before_first_play=t<acts[n][0][0],unzoomed=None,hand_spread=None,suitability_or_limit='Post-play candidate cannot replace the selected first hand.' if t>=acts[n][0][0] else 'Pre-play candidate; named reveal and fan reviewed.')
save('TURN_EVIDENCE.json',ev)

review=['# Complete recording review: 20261012_010706000_iOS.MP4','', 'Reviewer: /root/long_010706, Sol. Review date: October 12, 2026. Status: review ready, pending independent acceptance.','', 'One human battle from the Deluxe Pack: Mega Emblem Event is shown. The event menu at 2 s uses New deck 16; the current deck QR is shown at 0 s and closes directly into matchmaking. No deck edit, recording cut, second battle, or Auto option is shown. The opponent is たまご and the owner is Dacz8976. SOURCE_TIME.json establishes October 11, 2026, at about 8:07 PM Chicago time.','', 'The owner wins by points, 3-2, on turn 21. The results at 819 s show Went first, 21 turns played, and 600 damage done. Kingambit knocks out Mega Gardevoir ex to end the battle. This is a normal knockout victory, not a concession.','', '## Opening and source coverage','', 'At 25 s, the original five cards are Lucky Ice Pop, Kingambit, Glimmet, Pawniard, and Professor\'s Research, left to right. Glimmet becomes Active at 26 s and Pawniard occupies the left Bench slot at 32 s. The opponent starts Ralts. No setup redraw is shown.','', 'The entire 0-820.845 s source was inspected with native 4-second continuity frames, an initial boundary overview, and denser native seeks at draws, first moves, searches, knockouts, and terminal play. The QR/menu/matchmaking, setup, all 21 turns, and results transition are covered. TURN_EVIDENCE.json catalogs the retained original 1170 x 2532 images. The overview sheets are reduced browsing aids and are never substituted for native hand captures.','', '## Turn account','', '| Turn | Player | Source seconds | Meaningful actions and result | Owner ending hand |','|---|---|---:|---|---:|']
for row in turnrows:
 n=row['turn_number'];summary='; '.join(f"{a['order']}. {a['card_name'] or a['kind']}: {a['result']}" for a in row['plays_in_order']);review.append(f"| {n} | {row['who_played']} | {row['timing']['start_seconds']}-{row['timing']['end_after_resolution_seconds']} | {summary} | {row['owner_hand_end']['count'] if row['who_played']=='owner' else '-'} |")
review += ['', 'Each table row corresponds to the same numbered TURN_LEDGER.json row, with native frame IDs, ordered plays, named owner draws, both boards, Energy Zones, and explicit limits.','', '## Reconciled decisive sequences','', 'Turn 3 Venomous Hit deals 50 to Ralts because of weakness. The following poison checkup knocks it out and gives the owner the first point. After three turns of development, Mega Diancie ex has three Psychic Energy and uses Brilliant Storm for 100 on turn 8. Glimmora is knocked out; Shattering Crystal flips heads at 342 s, so the opponent gains no point. Giant Cape had just raised Diancie\'s effective maximum HP to 190 and its current HP by 20. This increase is not healing.','', 'Regigigas uses Giga Turbo on turn 9 for 100 and adds one Colorless Energy to the Benched Alolan Muk. The stadium activation beforehand is tails and finds no card. On turn 10, Peculiar Plaza replaces Mesagoza; Potion heals Diancie by 20, Sabrina forces the owner to choose Muk, and Diancie retreats to Indeedee without Energy payment under Plaza. Alolan Muk suppresses Basic abilities until it is knocked out on turn 16.','', 'The owner\'s turn 15 Poké Ball finds no Basic. Glimmora evolves on the Bench and Muk attacks Indeedee for 90 including weakness. On turn 16, Mega Gardevoir ex retreats into the Active position, knocks Muk out with Fantasia Force, and attaches its additional three Psychic Energy to Indeedee. The opponent gains its first point.','', 'On turn 19, the owner normally draws Copycat, plays it, shuffles the remaining three cards, and draws exactly Ilima, Lucky Ice Pop, and Lucky Ice Pop. The opponent has three cards. Lucky Ice Pop is inspected afterward, but neither Pop is consumed and the hand remains three; it is not recorded as a confirmed no-effect play. The normal draw and all three Copycat draws are separate ledger entries.','', 'Mega Gardevoir knocks the second Glimmora out on turn 20. Shattering Crystal is tails at 783 s and the opponent gains its second point. The owner promotes Kingambit, attaches its second Darkness on turn 21, and attacks. Three owner Pokemon have been knocked out, including the first Glimmora whose point was denied. Overlord\'s Blade therefore has 180 base damage plus 20 weakness, inferred from the filmed text and public knockout history. Mega Gardevoir is knocked out from 130 HP. Its three-point award ends the game at the displayed 3-2 score.','', 'The displayed 600 attack damage reconciles with 50 + 30 + 30 + 100 + 90 + 50 + 50 + 200. Poison checkups are documented separately.','', '## Capture and information limits','']+[f'- {x}' for x in limits]+['','Opponent hand ranges on owner turns 7 and 9 preserve overlap uncertainty. Other selected native fans provide direct counts. No hidden opponent card is inferred merely from later deck type. No explicit Supporter-warning decline is shown. The first-turn Cannot attack message is recorded as a no-effect attempted action.','', 'The exact current filmed QR semantic list is saved in DECK_USED.json and QR_DECODE.json. The live Pause Games log did not contain a readable current definition for this list. This is a live-log snapshot limit, not a guessed twenty-card list. External logging, independent acceptance, registration, and archival remain lead responsibilities.']
(P/'REVIEW.md').write_text('\n'.join(review)+'\n',encoding='utf-8')
(P/'COVERAGE.md').write_text('# Whole-source coverage\n\n- 0-3 s: current deck QR and Event menu, New deck 16.\n- 3-24 s: matchmaking, opponent profile, coin flip and first-player assignment.\n- 24-41 s: opening five, Active and Bench placement, opponent Ralts.\n- 41-810 s: all 21 recorded turns, with native continuity and denser action checks. One ledger row per turn.\n- 810-820.845 s: victory animation, complete owner results at 819 s, then opponent card-of-game transition.\n\nAll turns and the terminal result are covered. No second battle or cut was observed. The turn ledger and prose agree on point changes, ending hand counts and public board transitions. Selected draw candidates have native bottom-fifth and top-screen crops. Fast-play/zoom limitations, hidden opponent cards, overlapping fans, and absent opened discard piles are preserved.\n\nStatus: full available recording reviewed, pending independent lead acceptance. A deterministic validator only checks integrity and does not establish visual acceptance.\n',encoding='utf-8')
save('SUMMARY.json',{'video_basename':V,'source_sha256':H,'game_id':G,'source_game_count':1,'reviewer':'/root/long_010706','model':'Sol','review_date':'2026-10-12','whole_source_reviewed':True,'reviewed_interval_seconds':[0,820.845],'turn_count':21,'classification':'human_event','auto_visible':False,'queue':'Deluxe Pack: Mega Emblem Event','owner':'Dacz8976','opponent':'たまご','match_date_local':'2026-10-11','deck_core':['Glimmora','Alolan Muk','Kingambit','Regigigas'],'opponent_core':['Mega Gardevoir ex','Mega Diancie ex','Indeedee ex'],'outcome':'win','result_method':'points','points_owner':3,'points_opponent':2,'damage_done_displayed':600,'result_evidence':[eid(808),eid(819)],'qr_present':True,'qr_seconds':0,'capture_status':'complete_with_recording_limits','review_status':'review_ready_pending_independent_acceptance','external_log_written':False,'source_moved':False,'limits':limits})
save('UNCERTAINTIES.json',{'video_basename':V,'source_sha256':H,'game_id':G,'unreviewed_intervals':[],'uncertainties':[{'type':'recording_or_provenance_limit','description':clean(x),'consequence':'Do not claim complete hidden-hand replay or a dated live-log deck snapshot.'} for x in limits],'material_outcome_uncertainty':False,'lead_acceptance_pending':True})
# Keep QR names semantic. Community printing aliases are not evidence of exact artwork.
dd=json.loads((P/'DECK_USED.json').read_text(encoding='utf-8'))
dd['filmed_deck_snapshot']['cards_in_qr_order']=[{'name':x['name'],'semantic_entity_id':x['entity_id']} for x in qr['cards'] for _ in range(x['count'])]
dd['filmed_deck_snapshot']['counts_by_semantic_name']=[{'name':x['name'],'count':x['count'],'semantic_entity_id':x['entity_id']} for x in qr['cards']]
save('DECK_USED.json',dd)
for file in ['PAUSE_GAME.json','SUMMARY.json','TURN_EVIDENCE.json']:
 data=json.loads((P/file).read_text(encoding='utf-8'))
 if 'limits' in data:data['limits']=[clean(x) for x in data['limits']]
 if 'scheduled_capture_limits' in data:data['scheduled_capture_limits']=[clean(x) for x in data['scheduled_capture_limits']]
 save(file,data)
text=(P/'REVIEW.md').read_text(encoding='utf-8').replace('secondpoint','second point').replace('handfan','hand fan').replace('PauseGames','Pause Games').replace('Candidate+1/+3/+6','Candidates at +1/+3/+6 seconds')
text=text.replace('energy_attachment','Energy attachment').replace('attack_attempt','Attack attempt').replace('end_turn','End Turn')
text=re.sub(r'([,:;])(?=\S)',r'\1 ',text);text=re.sub(r' {2,}',' ',text);text=text.replace('.;', ';')
(P/'REVIEW.md').write_text(text,encoding='utf-8')
