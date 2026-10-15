import copy, json
from pathlib import Path
from PIL import Image

p=Path(__file__).parent
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
video=source['video_basename']; sha=source['sha256']; game='20261010_015821000_iOS-game1'
sources=[{'video_basename':video,'sha256':sha,'source_json':'SOURCE.json'}]
base={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':sources}
def save(name,obj): (p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t): return 'F'+f'{t:07.2f}'.replace('.','_')
def refs(*ts): return [eid(t) for t in ts]
def hand(names,t,limit=None):
    return {'cards_left_to_right':[{'position':i+1,'name':n,'variant':None,'basis':'Native visible hand plus named reveal continuity','evidence_ids':refs(t),'limit_reason':None} for i,n in enumerate(names)],'count':len(names),'basis':'Visible card slots; names cross-checked with reveals','evidence_ids':refs(t),'status':'observed','limit_reason':limit}
R='Professor’s Research'; W='Team Rocket’s Weezing ex'; K='Team Rocket’s Koffing'; H='Horsea'; C='Rare Candy'; S='Soothing Shore'; T='Hiking Trail'; P='Poké Ball'
limits=['Opponent hand identities and hidden normal/Research/Poké Ball/Legendary Pulse draws are unavailable. A later Basic play does not identify an earlier search result.',
        'No discard-pile window or scrolling was opened. Public top cards and known transactions do not establish either complete discard pile.',
        'Normal draw-end anchors are visually estimated source seconds. Actual decoded frame PTS was not measured; requested seek times remain separate.',
        'The +1/+3/+6 candidates sometimes follow the first voluntary play. Dense earlier native frames supply the owner start hand; no future hand is substituted.',
        'Notifications temporarily cover upper-screen information around112–118,149–156 and175–176 seconds. Clear adjacent frames establish the cited board and actions.',
        'Filmed QR and log establish semantic deck composition; exact artwork/rarity of every hidden card is not established. No hidden identities were supplied from the deck.']

# Every retained native image stays source-bound. Generated crops are lossless and unscaled.
frames=[]; cropdir=p/'turn_evidence'/'crops'; cropdir.mkdir(exist_ok=True)
candidate={43:(1,42,1),45:(1,42,3),48:(1,42,6),94:(3,93,1),96:(3,93,3),99:(3,93,6),197:(5,196,1),199:(5,196,3),202:(5,196,6)}
selected={42.5:1,93.3:3,196:5}; preend={57:1,139:3,220:5}
for path in sorted((p/'turn_evidence').glob('t*.jpg')):
    t=float(path.stem[1:]); ident=eid(t); turn=1 if 39<=t<58 else 2 if 58<=t<90 else 3 if 90<=t<164 else 4 if 164<=t<193 else 5 if 193<=t<227 else 6 if 227<=t<=243 else None
    with Image.open(path) as im:
        assert im.size==(1170,2532)
        im.crop((0,2025,1170,2532)).save(cropdir/(ident+'_bottom.png'))
        im.crop((0,0,1170,720)).save(cropdir/(ident+'_top.png'))
    cand=candidate.get(t); sel=t in selected
    role='scheduled_draw_candidate' if cand else 'selected_start_hand' if sel else 'before_end_action' if t in preend else 'opening' if 26.5<=t<=27 else 'event_or_board'
    frames.append({'evidence_id':ident,'role':role,'turn_number':turn,'who_played':'owner' if turn in (1,3,5) else 'opponent' if turn else None,'source_video':video,'source_sha256':sha,
        'draw_animation_end_seconds':cand[1] if cand else {42.5:42,93.3:93,196:196}.get(t),'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':cand[2] if cand else None,
        'full_frame_path':path.relative_to(p).as_posix(),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':(cropdir/(ident+'_bottom.png')).relative_to(p).as_posix(),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},
        'top_crop':{'path':(cropdir/(ident+'_top.png')).relative_to(p).as_posix(),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,720]},'selected_for_start_hand':sel,
        'before_first_play':True if sel else False if cand else None,'unzoomed':True if sel else None,'hand_spread':True if sel else None,
        'observation':'Complete readable owner hand before first committed play' if sel else 'Native draw-offset candidate; first play already begins or resolves' if cand else 'Native event, board or pre-ending view',
        'suitability_or_limit':'Horsea is lifted in the fan but not yet benched; all six slots readable' if t==93.3 else 'Use dense preplay selected frame instead of this later action/draw frame' if cand else 'Do not infer hidden cards or exact frame PTS'})
discards=[{'snapshot_id':'D'+str(n),'turn_number':n,'pile_owner':'both','source_video':video,'timestamp_seconds':t,'cards_in_view':None,'scroll_coverage':'none: pile was never opened','full_pile_established':False,'evidence_ids':refs(t),'limit_reason':'Periodic owner-turn check: only public top discard images, not a full pile view'} for n,t in [(1,57),(3,162),(5,226)]]
evidence=base|{'source_sha256':sha,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'top_crop':'Native opponent fan, clock and Energy Zone; bounds recorded','fixed_grid_is_turn_start_evidence':False,'discard_target_every_owner_turns':[2,3]},'frames':frames,'discard_snapshots':discards,'scheduled_capture_limits':limits}
save('TURN_EVIDENCE.json',evidence)

def pokemon(name,hp,maxhp,energy=0,tool='none',position=None,effects=None):
    return {'name':name,'variant':None,'bench_position':position,'hp_now':hp,'hp_max':maxhp,'hp_max_basis':'Visible HP/card; +20 Giant Cape when attached' if tool=='Giant Cape' else 'Visible HP/card','damage':maxhp-hp,'attached_energy':{'total':energy,'by_type':{'Water':energy} if energy else {}},'tool':tool,'special_conditions':[],'active_effects':effects or [],'evidence_ids':[],'status':'observed','limit_reason':'Exact printing not established'}
def zone(count,first=False):
    return {'this_turn':{'type':'Water' if count else None,'count':count,'available':bool(count)},'next':{'type':'Water','count':1,'available':False},'basis':'Visible large current Energy if available and small next Water icon; first player turn1 has none' if first else 'Visible current/next Energy icons','evidence_ids':[],'limit_reason':'No hidden future sequence inferred'}
def board(n,t,oa,ob,pa,pb,stadium='none',points=0,ownerzone=0,oppzone=0):
    b={'turn_number_displayed':n,'phase':'after resolution' if t in (57,89,162,192,226,242) else 'start after normal draw','stadium':stadium,'owner':{'active':oa,'bench_in_position_order':ob,'energy_zone':zone(ownerzone,n==1),'points':points,'board_effects':[],'evidence_ids':refs(t),'status':'observed','limit_reason':None},'opponent':{'active':pa,'bench_in_position_order':pb,'energy_zone':zone(oppzone),'points':0,'board_effects':[],'evidence_ids':refs(t),'status':'observed','limit_reason':None},'shared_effects':[],'evidence_ids':refs(t)}
    for side in ['owner','opponent']:
        b[side]['energy_zone']['evidence_ids']=refs(t)
        for mon in [b[side]['active']]+b[side]['bench_in_position_order']:mon['evidence_ids']=refs(t)
    if stadium!='none': b['shared_effects']=[{'name':stadium,'source':stadium,'affected_player':'both','restriction_or_mark':'At end turn draw to3' if stadium==T else 'At end turn heal20 from own Pokémon with at least6 Energy','expiry':'until replaced','evidence_ids':refs(t)}]
    return b
start1=board(1,42.5,pokemon(K,60,60),[],pokemon('Frigibax',60,60),[])
end1=board(1,57,pokemon(K,60,60,tool='Small Balloon'),[],pokemon('Frigibax',60,60),[])
start2=board(2,61,pokemon(K,60,60,tool='Small Balloon'),[],pokemon('Frigibax',60,60),[],oppzone=1)
end2=board(2,89,pokemon(K,60,60,tool='Small Balloon'),[],pokemon('Suicune ex',140,140),[pokemon('Frigibax',60,60,position='center')])
start3=board(3,93.3,pokemon(K,60,60,tool='Small Balloon'),[],pokemon('Suicune ex',140,140),[pokemon('Frigibax',60,60,position='center')],ownerzone=1)
end3=board(3,162,pokemon(H,50,50,1),[pokemon(W,140,140,tool='Small Balloon',position='center')],pokemon('Suicune ex',140,140),[],T,1)
start4=board(4,166,pokemon(H,50,50,1),[pokemon(W,140,140,tool='Small Balloon',position='center')],pokemon('Suicune ex',140,140),[],T,1,oppzone=1)
end4=board(4,192,pokemon(H,50,50,1),[pokemon(W,140,140,tool='Small Balloon',position='center')],pokemon('Suicune ex',160,160,1,'Giant Cape'),[pokemon('Frigibax',60,60,position='center')],S,1)
start5=board(5,196,pokemon(H,50,50,1),[pokemon(W,140,140,tool='Small Balloon',position='center')],pokemon('Suicune ex',160,160,1,'Giant Cape'),[pokemon('Frigibax',60,60,position='center')],S,1,ownerzone=1)
lock=[{'name':'Cannot retreat','source':'Kingdra ex: Stormy Prison','affected_player':'opponent','affected_pokemon':'Suicune ex','restriction_or_mark':'Defending Pokémon cannot retreat during opponent next turn','expiry':'end of opponent turn6','evidence_ids':refs(226)}]
end5=board(5,226,pokemon('Kingdra ex',170,170,2),[pokemon(W,140,140,tool='Small Balloon',position='center'),pokemon(H,50,50,position='right')],pokemon('Suicune ex',70,160,1,'Giant Cape',effects=lock),[pokemon('Frigibax',60,60,position='center')],S,1)
start6=copy.deepcopy(end5);start6['turn_number_displayed']=6;start6['phase']='start after normal draw';start6['opponent']['energy_zone']=zone(1);start6['evidence_ids']=refs(231)
end6=board(6,242,pokemon('Kingdra ex',170,170,2),[pokemon(W,140,140,tool='Small Balloon',position='center'),pokemon(H,50,50,position='right')],pokemon('Suicune ex',70,160,1,'Giant Cape',effects=lock),[pokemon('Baxcalibur',140,140,position='center')],S,1,oppzone=1)

def play(order,kind,card,target,t,result,hc=None,energy=None,nested=None,prompt=None,response=None):
    return {'order':order,'kind':kind,'card_name':card,'target':target,'energy':energy or {'type':None,'count':None,'destination':None,'retreat_payment_by_type':None},'result':result,'prompt_text':prompt,'response':response,'nested_events_in_order':nested or [],'hand_count_after':hc,'source_video':video,'timestamp_seconds':t,'evidence_ids':refs(t),'basis':'Visible action and resulting board/hand','limit_reason':None}
def draw(kind,cause,t,names,before,after,linked=None):
    return {'kind':kind,'caused_by':cause,'linked_play_order':linked,'cards_in_reveal_order':[{'name':name,'reveal_position':i+1,'source_video':video,'timestamp_seconds':tm,'evidence_ids':refs(tm),'basis':'Named visible reveal' if name else 'Hidden opponent draw/card back only','limit_reason':None if name else 'Identity hidden'} for i,(name,tm) in enumerate(names)],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':[],'source_video':video,'timestamp_seconds':t,'evidence_ids':refs(t),'limit_reason':None if all(x[0] for x in names) else 'Opponent identities not exposed; counts can be public transaction inference'}
def auto(name,t,result):return {'name':name,'source_video':video,'timestamp_seconds':t,'result':result,'evidence_ids':refs(t)}
starts={1:hand([R,C,W,'Small Balloon',S],42.5),2:hand([C,W,S,'Sabrina',T],61),3:hand([C,W,S,'Sabrina',T,H],93.3,'Draw-end estimate93; Horsea lifted before bench placement'),4:hand([C,S,'Kingdra ex'],166),5:hand([C,S,'Kingdra ex',P],196),6:hand([S],231)}
ends={1:hand([C,W,S,'Sabrina',T],57),2:hand([C,W,S,'Sabrina',T],89),3:hand([C,S,'Kingdra ex'],162),4:hand([C,S,'Kingdra ex'],192),5:hand([S],226),6:hand([S],242)}
rows=[]
def row(n,a,b,drawend,first,pre,end,draws,plays,automatic,oppfan=None,arith=None):
    owner=n%2==1
    acting=starts[n] if owner else {'cards_left_to_right':None,'count':None,'supported_count_inference':arith,'basis':'Hidden opponent fan; public transactions separately inferred','evidence_ids':refs(drawend),'status':'hidden','limit_reason':'No identities revealed'}
    row={'turn_number':n,'who_played':'owner' if owner else 'opponent','source_video':video,'timing':{'draw_animation_end_seconds':drawend,'first_voluntary_move_seconds':first,'before_end_action_seconds':pre,'end_after_resolution_seconds':end},'hand_at_start':acting,'owner_hand_start':starts[n],
         'opponent_hand_at_owner_turn_start':{'count':oppfan,'supported_range':[oppfan,oppfan] if owner else None,'count_method':'Visible separate card backs in native fan','basis':'Direct visual count; arithmetic corroboration kept separate' if owner else 'Not an owner turn start','evidence_ids':refs({1:42.5,3:93.3,5:196}.get(n,drawend)),'limit_reason':None if owner else 'Field applies at owner turn starts only','public_transaction_inference':arith},
         'draws_and_searches':draws,'plays_in_order':plays,'automatic_events_in_order':automatic,'board_at_start':a,'board_after':b,'owner_hand_end':ends[n],'discard_snapshot_ids':['D'+str(n)] if owner else [],'turn_evidence_ids':refs(drawend,pre,end),'limits':['Opponent hidden cards stay unnamed','No opened full discard pile']}
    rows.append(row)
row(1,start1,end1,42,44,57,57,[draw('normal_draw','turn start',41,[(S,41)],4,5),draw('supporter_draw',R,47,[('Sabrina',47),(T,48)],4,6,1)],
    [play(1,'card_play',R,'owner hand',44,'Draw Sabrina then Hiking Trail',6),play(2,'card_play','Small Balloon','owner Active Koffing',51,'Attach Tool; no Energy change',5),play(3,'end_turn',None,'turn',58,'End without attack or Energy generation',5)],[],4,'4 from opening5 minus Active')
row(2,start2,end2,61,66,88,89,[draw('normal_draw','turn start',61,[(None,61)],4,5),draw('search',P,68,[(None,68)],4,5,1),draw('supporter_draw',R,72,[(None,72),(None,76)],4,6,2),draw('ability_draw','Legendary Pulse',88,[(None,88)],5,6)],
    [play(1,'card_play',P,'opponent deck',66,'Find hidden Basic; identity cannot be bound to later Suicune',None),play(2,'card_play',R,'opponent hand',70,'Draw2 hidden cards',None),play(3,'card_play','Suicune ex','opponent center Bench',78,'Bench140HP Basic',None),play(4,'energy_attachment',None,'opponent Active Frigibax',82,'Attach1 Water',None,{'type':'Water','count':1,'destination':'Active Frigibax','retreat_payment_by_type':None}),play(5,'retreat',None,'Frigibax to Bench, Suicune ex Active',84,'Pay1 Water from Frigibax; both end with0 Energy',None,{'type':'Water','count':1,'destination':None,'retreat_payment_by_type':{'Water':1}}),play(6,'end_turn',None,'turn',88,'End without attack; Legendary Pulse draws1')],
    [auto('Legendary Pulse',88,'Active Suicune ex draws1 hidden card at end turn')],None,'Start5 after normal draw; end6 from public transactions')
row(3,start3,end3,93,94,139,162,[draw('normal_draw','turn start',92,[(H,92)],5,6),draw('stadium_draw',T,146,[('Kingdra ex',148)],2,3)],
    [play(1,'card_play',H,'owner center Bench',94,'Bench50HP Horsea',5),play(2,'card_play','Sabrina','opponent Active Suicune ex',109,'Opponent chooses Frigibax as new Active',4,nested=[{'sequence':1,'event':'Opponent selects sole benched Frigibax; Suicune moves center Bench','timestamp_seconds':112,'evidence_ids':refs(112)}]),
     play(3,'retreat',None,'Koffing to center Bench; Horsea Active',114,'Small Balloon reduces basic retreat cost to0; no Energy discarded',4,{'type':None,'count':0,'destination':None,'retreat_payment_by_type':{}}),
     play(4,'card_play',W,'owner benched Koffing',120,'Evolve to140HP Weezing ex; inherit Small Balloon',3,nested=[{'sequence':1,'event':'Optional Boiler Smog accepted; exact prompt wording not retained','timestamp_seconds':128,'evidence_ids':refs(128)},{'sequence':2,'event':'Opponent Active Frigibax becomes Poisoned and Burned','timestamp_seconds':132,'evidence_ids':refs(132,134)}],response='Use Boiler Smog'),
     play(5,'card_play',T,'Stadium',136,'Hiking Trail enters; no immediate draw',2),play(6,'energy_attachment',None,'owner Active Horsea',139,'Attach1 Water from current Energy Zone',2,{'type':'Water','count':1,'destination':'Active Horsea','retreat_payment_by_type':None}),play(7,'attack','Hook','opponent Active Frigibax',141,'30damage:60→30; attack ends turn',2)],
    [auto('Hiking Trail',146,'Hand2→3, draw Kingdra ex'),auto('Poison checkup',149,'Frigibax30→20HP'),auto('Burn checkup',150,'Frigibax20→0HP; coin face not needed to establish KO'),auto('KO and point',158,'Frigibax removed; owner points0→1'),auto('Promotion',162,'Opponent promotes Suicune ex,140HP0Energy')],6,'6 from public draws/plays on turn2')
row(4,start4,end4,166,170,191,192,[draw('normal_draw','turn start',166,[(None,166)],6,7),draw('ability_draw','Legendary Pulse',191,[(None,191)],4,5)],
    [play(1,'card_play','Frigibax','opponent center Bench',170,'Bench60HP Basic'),play(2,'energy_attachment',None,'opponent Active Suicune ex',171,'Attach1 Water',None,{'type':'Water','count':1,'destination':'Active Suicune ex','retreat_payment_by_type':None}),play(3,'card_play',S,'Stadium',178,'Replace Hiking Trail; owner Hiking Trail discarded'),play(4,'card_play','Giant Cape','opponent Active Suicune ex',185,'Attach+20HP cape; Suicune140/140→160/160'),play(5,'end_turn',None,'turn',191,'No attack; Suicune has1Water; Legendary Pulse draws1')],
    [auto('Soothing Shore',191,'No Pokémon has6 Energy, so no visible healing'),auto('Legendary Pulse',191,'Draw1 hidden card')],None,'Start7 after normal draw; end5 by public transactions')
row(5,start5,end5,196,197,220,226,[draw('normal_draw','turn start',195,[(P,195)],3,4),draw('search',P,199,[(H,200)],3,4,1)],
    [play(1,'card_play',P,'owner deck',197,'Find shiny Horsea, revealed200s',4),play(2,'card_play',C,'owner Active Horsea',204,'Evolve directly to Kingdra ex using card from hand; skip Seadra; inherit1Water',2,nested=[{'sequence':1,'event':'Select Active Horsea as Rare Candy target','timestamp_seconds':206,'evidence_ids':refs(206)},{'sequence':2,'event':'Select Kingdra ex from hand','timestamp_seconds':211,'evidence_ids':refs(211)},{'sequence':3,'event':'Kingdra ex resolves170HP with inherited1Water','timestamp_seconds':213,'evidence_ids':refs(213)}]),play(3,'card_play',H,'owner right Bench',216,'Bench second50HP Horsea',1),play(4,'energy_attachment',None,'owner Active Kingdra ex',220,'Attach second Water; total2',1,{'type':'Water','count':1,'destination':'Active Kingdra ex','retreat_payment_by_type':None}),play(5,'attack','Stormy Prison','opponent Active Suicune ex',222,'90damage:160→70HP; cannot retreat during opponent next turn',1)],
    [auto('Soothing Shore',226,'Neither side has6Energy; no healing')],5,'5 from public draws/plays on turn4')
row(6,start6,end6,231,233,241,242,[draw('normal_draw','turn start',231,[(None,231)],5,6)],
    [play(1,'card_play',C,'opponent benched Frigibax',233,'Rare Candy evolves directly to Baxcalibur140HP; skip middle stage; no Energy added',None,nested=[{'sequence':1,'event':'Baxcalibur appears center Bench','timestamp_seconds':236,'evidence_ids':refs(236)}]),play(2,'concession',None,'game',242,'Opponent concedes; owner Victory')],[],None,'Start6 after normal draw; expected4 after Candy and Baxcalibur; exact fan count not separately asserted')
save('TURN_LEDGER.json',base|{'turns':rows,'limits':limits,'copycat_observation':'No Copycat play in this battle','unproductive_actions_observation':'No visible canceled card play or declined effect; quick card inspections and accepted Boiler Smog are retained. End turns without attack are explicitly numbered.'})

live=json.loads((p.parent/'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8-sig')); deck=live['decks'][1]
slots=[]; counts=[]
for count,name,variant in deck['rows']:
    counts.append({'count':int(count),'name':name,'variant_in_log':variant})
    slots.extend([{'name':name,'variant_in_log':variant,'printing_basis':'Live log representative identifier; exact filmed printing may differ'} for _ in range(int(count))])
save('DECK_USED.json',base|{'deck_name_in_log':deck['name'],'deck_id_in_log':deck['id'],'source_url':live['source_url'],'captured_at':live['retrieved_at_utc'],'log_list_version':'LIVE_NEW_DECKS_VERIFIED.json '+live['retrieved_at_utc'],'expected_card_count':20,'cards_in_log_order':slots,'counts_by_name_and_variant':counts,'energy_configuration_from_log':'Water energy','actual_card_count':20,'capture_source_text_or_image':'../LIVE_NEW_DECKS_VERIFIED.json','captured_log_text':deck['text'],'game_version_binding_basis':{'source_qr':'qr_intake/QR_DECODE_0001.00.json','qr_payload_matches_live_code':True,'continuous_footage':'0–3s QR/deck screen then event entry with New deck13 selected,6–17s matchmaking/opponent,26–39s setup and uninterrupted turns through concession/result. No intervening deck edit/selection is visible. Filmed opening/play cards are compatible with this semantic list.','evidence_ids':refs(0,3,6,14,17,26.5,42.5,120,196,242,253)},'conflicts_with_filmed_cards':[],'exact_list_status':'verified_20_card_semantic_list_and_game_binding','limits':['Representative live-log printing identifiers are preserved verbatim; semantic match does not verify all artwork/rarity','Opening and draws are from footage, not inferred from this list']})
opening=[R,C,K,W,'Small Balloon']
save('PAUSE_GAME.json',base|{'review_date':'2026-10-09','match_date':'2026-10-09','date_basis':'Parent verified filename creationUTC conversion to America/Chicago; batch RECORDING_DATE_VERIFICATION','destination':live['source_url'],'deck_name':deck['name'],'opening':{'source_video':video,'timestamp_seconds':26.5,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[{'position':i+1,'name':name,'basis':'Native pre-Active opening fan','evidence_ids':refs(26.5,26.8,27),'limit_reason':None} for i,name in enumerate(opening)],'selected_active':{'name':K,'opening_position':3,'source_video':video,'timestamp_seconds':28,'evidence_ids':refs(27,28)},'redraw_or_replacement':'None shown','before_active_placement':True,'status':'observed_complete_five','evidence_ids':refs(26.5,26.8,27),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'reviewer_complete_pending_independent_acceptance','outcome':{'result':'win','reason':'opponent conceded','opponent':'よこっぴ','owner':'Dacz8976','mode':'Deluxe Pack: Mega Emblem Event','battle_type':'human','visible_auto':'No Auto control or option observed','went_first':True,'turns_played':6,'points_owner':1,'points_opponent':0,'damage_done':120,'evidence_ids':refs(3,242,253)},'limits':limits,'lead_checked':False})
save('SUMMARY.json',{'is_template':False,'source_video':video,'source_sha256':sha,'source_json':'SOURCE.json','review_status':'reviewer_complete_pending_independent_acceptance','game_count':1,'recording_coverage_seconds':[0,254.015],'games':[{'game_id':game,'match_date':'2026-10-09','owner':'Dacz8976','opponent':'よこっぴ','mode':'Deluxe Pack: Mega Emblem Event','battle_type':'human','auto_control_observed':False,'owner_deck':deck['name'],'opponent_visible_core':['Frigibax','Suicune ex','Baxcalibur'],'outcome':'win','finish':'opponent concession','turns_played':6,'owner_points':1,'opponent_points':0,'damage_done':120,'ending_evidence':{'concession_seconds':242,'victory_result_seconds':253,'evidence_ids':refs(242,253)},'external_log_eligibility':'Human-only Pause Games candidate; root controls deduplication, entry and reload verification','ladder_entry':'Do not claim ranked; visible event mode'}],'capture_status':'complete_with_recording_limits','independent_acceptance':'pending','packet_only':True,'limits':limits})
save('UNCERTAINTIES.json',{'is_template':False,'source_video':video,'source_sha256':sha,'items':[{'id':'U'+str(i+1),'scope':'recording or evidence','description':v,'impact':'Does not prevent observed outcome or6turn public-action reconstruction'} for i,v in enumerate(limits)]+[{'id':'U7','scope':'burn coin','description':'Burn check coin face not confidently resolved from selected native frames; Frigibax reaches0HP and KO/point are explicit','impact':'No guess of heads/tails'},{'id':'U8','scope':'cape name','description':'Name on played Tool partly covered by glare; recognizable Giant Cape artwork and legible+20HP text corroborate140→160 maximum HP','impact':'Printing unknown; exact tool effect and target clear'}]})
save('VIEWED_EVIDENCE_MANIFEST.json',{'is_template':False,'source_video':video,'source_sha256':sha,'method':'All6 five-second overview sheets inspected for phases and gaps; native event evidence inspected directly or in chronological contact sheets. Native draw-start hands and named reveals were individually checked. Not a claim of every source frame being watched.','overview_sheets_viewed':['overview/'+x.name for x in sorted((p/'overview').glob('*sheet*'))],'contact_sheets_viewed':['contact_'+f'{i:02}'+'.jpg' for i in range(1,15)],'direct_native_examples_evidence_ids':refs(26.5,26.8,27,42.5,47,48,82,84,93.3,120,128,136,139,185,186,196,220,221,226,236,242,253),'top_fan_crops_individually_viewed':['fan_42.5.jpg','fan_93.3.jpg','fan_196.jpg'],'limits':['Some redundant extracted native frames were retained without separate direct view; evidence registry is capture inventory, not an assertion all were separately viewed']})

review='''# 20261010_015821000_iOS.MP4 review

One complete human Deluxe Pack: Mega Emblem Event game is recorded. Dacz8976 went first against よこっぴ and won when the opponent conceded. The banner at242s explicitly says “Your opponent conceded”;253s shows Victory,6turns,1–0points and120damage done. No Auto control or option is visible. This is an event game; ranked mode is not established.

Source identity is frozen in SOURCE.json: SHA2568d64e896d3125e504b7186754cbf2c21c0b5fcbc61f65524f6de27a2effd2a38,254.015seconds,1170×2532. Match date is October9,2026 in Chicago from the parent’s creationUTC verification, rather than the filename’s UTC date.

## Opening and deck binding

At26.5–27s the original five cards, before Active selection, are Professor’s Research, Rare Candy, Team Rocket’s Koffing, Team Rocket’s Weezing ex and Small Balloon, left to right. Koffing is selected as Active at27–28s; no redraw is shown and both initial benches are empty. Opponent starts Frigibax60HP. Water is the visible next Energy type for both.

The source QR at0–1s matches the dated live Pause Games list saved in ../LIVE_NEW_DECKS_VERIFIED.json: Kingdra ex / Team Rocket's Weezing ex,20cards and Water Energy. Continuous footage moves from that deck screen to the event with New deck13 selected, then matchmaking, setup and this battle. No intervening deck edit or different selection is visible. DECK_USED.json preserves all20log-order slots including duplicates and all log identifiers. QR/live semantic identity does not establish every hidden card's artwork or rarity. Hand identities below come from filmed hands and reveals.

## Turn coverage

| Turn | Source seconds | Normal draw and start hand | Numbered voluntary actions | Resolution |
|---|---|---|---|---|
|1owner|39–58|Soothing Shore;5cards: Research, Candy, Weezing, Balloon, Shore|1Research;2Balloon on Active Koffing;3End Turn|Research reveals Sabrina then Hiking Trail. Hand5at end. Koffing60HP0Energy with Balloon; Frigibax60HP0Energy. No attack or first-turn Energy.|
|2opponent|58–90|Hidden normal draw; public count inference5|1Poké Ball;2Research;3bench Suicune ex;4Water to Active Frigibax;5retreat Frigibax, pay1Water and promote Suicune;6end|Hidden Basic find and2Research draws stay unnamed. Legendary Pulse draws1hidden card. Suicune140HP0Energy Active; Frigibax60HP0Energy center Bench. Owner unchanged.|
|3owner|90–164|Horsea;6cards: Candy, Weezing, Shore, Sabrina, Hiking Trail, Horsea|1bench Horsea;2Sabrina;3free Koffing retreat to Horsea;4evolve benched Koffing to Weezing and accept Boiler Smog;5Hiking Trail;6Water to Active Horsea;7Hook|Sabrina brings Frigibax Active. Balloon makes Koffing retreat free. Boiler Smog poisons/burns Frigibax. Hook30 leaves30HP; Hiking Trail draws Kingdra ex from hand2→3; poison10 and burn20 produceKO and ownerpoint1. Opponent promotes Suicune.|
|4opponent|164–193|Hidden normal draw; public count inference7|1bench another Frigibax;2Water to Suicune;3Soothing Shore replaces Hiking Trail;4Giant Cape on Suicune;5end|Suicune becomes160/160HP with1Water and Cape. No attack. Legendary Pulse draws1hidden card; no qualifying6Energy Pokémon or healing. Owner hand3.|
|5owner|193–227|Poké Ball;4cards: Candy, Shore, Kingdra, Poké Ball|1Poké Ball finds Horsea;2Rare Candy evolves Active Horsea directly to Kingdra ex;3bench second Horsea right;4Water to Kingdra;5Stormy Prison|Kingdra170HP inherits1Water then gainssecond.90damage leaves caped Suicune70/160HP; visible cannot-retreat effect applies during opponent next turn. Owner hand1Shore; points1–0.|
|6opponent|227–243|Hidden normal draw; public count inference6|1Rare Candy evolves benched Frigibax directly to Baxcalibur;2concede|Baxcalibur140HP0Energy. No Ice Maker, Energy attachment or attack observed. Current Water remains available. Concession242s followed by Victory253s.|

The120result damage agrees with Hook30 plus Stormy Prison90; the30checkup damage is kept separately. There is no Copycat play. No visible canceled card play or declined prompt is established. Accepted Boiler Smog and turns ending without attack are explicit rather than omitted.

## Pause Games captures

Native preplay hand frames42.5,93.3 and196s establish owner starts5,6 and4cards. Direct native top-fan counts are4,6 and5opponent cards at those starts, with public transaction arithmetic separately corroborating them. Draw-end anchors are approximately42,93 and196s. Retained +1/+3/+6 candidates are43/45/48,94/96/99 and197/199/202s. Those candidates already show a play or its resolution, so dense earlier readable frames are selected instead. The93.3s Horsea is lifted in the fan but not yet benched. Before-ending hand frames57,139 and220s show5,2 and1cards; turn3 resolves to3after Hiking Trail's Kingdra draw.

TURN_EVIDENCE.json retains native full frames plus lossless bottom-fifth crops [0,2025,1170,2532] and top crops [0,0,1170,720]. Requested seek timestamps are not presented as measured frame PTS. TURN_LEDGER.json has one actual row for each of6turns, named owner reveals/searches, sequential voluntary actions, automatic events, both boards, HP, tools, Water counts, Energy Zones, Stadium/effects and points.

No discard-pile viewer was opened. Periodic checks on owner turns1,3and5 therefore record a full-pile limitation. Public top discard cards and known spent cards are not treated as a complete pile. Opponent hidden draws/search identities, unresolved burn coin face, glared Cape name printing and temporary notification occlusions remain explicit in UNCERTAINTIES.json.

Review is complete with recording limits and awaits independent acceptance. No external entry, shared index mutation, archive move or simulator change was performed by this reviewer.
'''
(p/'REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Source coverage

Source:20261010_015821000_iOS.MP4. One recorded game, no source gap or second game found. Frozen identity and254.015s duration are in SOURCE.json.

| Interval | Covered content | Evidence |
|---|---|---|
|0–6s|DeckQR, deckscreen, selectedevent deck and mode|Native0,3,6; retained QR decode; overview1|
|6–26s|Matchmaking, opponent, first-player choice and initialdraw|Native10,14,17,20,23,26; overview1–2|
|26–39s|Originalfive beforeActive, selection, opponent setup and waiting|Native26.5,26.8,27,28,29; openingreview|
|39–58s|Turn1normaldraw,Research2reveals,Balloon,ending|Native40–58event captures; selectedhand42.5|
|58–90s|Turn2hiddendraw,search,Research,bench,Waterandpaidretreat,abilitydraw|Native60–90captures;82/84Energy/retreatchecks|
|90–164s|Turn3drawandall7plays,abilityconditions,attack,Stadiumdraw,checkupKO,promotion|Native90.5–164dense captures;hand93.3;Weezing120/128;ending139,162|
|164–193s|Turn4draw,bench,attachment,Stadiumreplacement,Tool,endability|Native164–193captures;Cape185/186|
|193–227s|Turn5namednormaldraw,search,skip-stageevolution,bench,Energy,attack/effect|Native193–227dense captures;hand196;beforeattack220;resolved226|
|227–243s|Turn6draw,Candyevolution,concession|Native228–243;Baxcalibur236;concession242|
|243–254.015s|Victoryanimationandresultcard,sourceending|Native244,245,250,253;finaloverview|

Allsix5second overview sheets were inspected to locate phases. Chronological native-event contact sheets1–14 and directly viewed native frames cover every setup, turn, meaningful action and ending. This is not a claim that every frame was individually watched. Fixed overview images do not replace the native opening, draw-timed hands or event evidence. VIEWED_EVIDENCE_MANIFEST.json distinguishes inspected views from the capture inventory.

No missing outcome, unrecorded earlier turn or extra game is inferred. Recording limitations concern hidden opponent identities, unavailable full discards, notifications, exact printing and estimated seek anchors. Structural validation is separate from independent visual acceptance.
'''
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
print('Built6turn packet,',len(frames),'native frames,',len(slots),'deck slots')
