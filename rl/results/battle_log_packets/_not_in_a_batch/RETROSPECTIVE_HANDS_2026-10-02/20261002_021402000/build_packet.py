import json, re, copy, datetime, hashlib
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
OLD = ROOT / 'Recording_QA/20261002_021402000_iOS_competitive_sol'
SOURCE = json.loads((OLD/'SOURCE.json').read_text(encoding='utf-8-sig'))
INH = json.loads((P/'INHERITED_TURNS.json').read_text(encoding='utf-8-sig'))
SOURCE_ID = {'video_basename': SOURCE['video_basename'], 'sha256': SOURCE['sha256'], 'source_json': str(OLD/'SOURCE.json')}

def save(name, data):
    (P/name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def frame_id(t): return 'f'+f'{t:07.2f}'
def frame_path(t):
    new = P/'turn_evidence'/f't{t:07.2f}.jpg'
    return new if new.exists() else OLD/'native'/f't{t:07.2f}.jpg'

def cards(names, evid):
    return [{'position': i+1, 'name': n, 'variant': None, 'basis': 'direct_native_frame_observation' if n else 'unreadable', 'evidence_ids': evid, 'limit_reason': None if n else 'Card face cannot be read from inspected native evidence.'} for i,n in enumerate(names)]

def hand(names, times):
    return {'cards_left_to_right': cards(names, [frame_id(t) for t in times]), 'count': len(names), 'basis': 'direct_native_frame_observation', 'evidence_ids': [frame_id(t) for t in times], 'status': 'observed', 'limit_reason': None}

def inherited_reference(row):
    return {'status':'inherited_accepted_review_not_new_visual_observation', 'accepted_review': INH['accepted_review'], 'accepted_review_sha256': INH['accepted_review_sha256'], 'accepted_source_line': row['accepted_source_line'], 'verbatim_accepted_row': row['verbatim_accepted_row']}

def board_ref(row):
    return {'status': 'inherited_reference_only', 'owner': {'status': 'inherited_accepted_review_not_new_visual_observation', 'energy_zone': {'this_turn': None, 'next': None, 'status': 'outside_requested_hand_supplement', 'limit_reason': 'No fresh board or Energy Zone review authorized.'}}, 'opponent': {'status': 'inherited_accepted_review_not_new_visual_observation', 'energy_zone': {'this_turn': None, 'next': None, 'status': 'outside_requested_hand_supplement', 'limit_reason': 'No fresh board or Energy Zone review authorized.'}}, 'accepted_board_reference': inherited_reference(row), 'limit_reason': 'Accepted prose and native references govern board facts; no new start/end board reconstruction in this bounded request.'}

def unavailable_hand(reason):
    return {'cards_left_to_right': None, 'count': None, 'basis': None, 'evidence_ids': None, 'status': 'outside_requested_scope', 'limit_reason':reason}

def base_ledger():
    rows=[]
    for row in INH['rows']:
        cells=[x.strip() for x in row['verbatim_accepted_row'].strip('|').split('|')]
        n=row['turn_number']; own=n%2==1
        sentences=re.split(r'(?<=\.)\s+', cells[1])
        acts=[]
        for k, sentence in enumerate(sentences,1):
            acts.append({'order': k, 'kind': 'inherited_narrative_unit', 'description': sentence, 'basis': 'inherited_accepted_review_not_new_visual_observation', 'accepted_source_line':row['accepted_source_line'], 'source_video':SOURCE['video_basename'], 'timestamp_seconds':None, 'limit_reason':'Narrative sentence order preserved. Compound actions within a sentence are not silently split or independently verified.'})
        rows.append({'turn_number':n,'who_played':'owner' if own else 'opponent','source_video':SOURCE['video_basename'],'timing':{'accepted_window':cells[0],'draw_animation_end_seconds':None,'first_voluntary_move_seconds':None,'before_end_action_seconds':None,'end_after_resolution_seconds':None},'hand_at_start': unavailable_hand('Not a requested owner turn.' if own else 'Opponent card identities are hidden; no hand identities inferred.'),'owner_hand_start':unavailable_hand('Not requested beyond first six owner turns.'),'opponent_hand_at_owner_turn_start':{'count':None,'supported_range':None,'basis':None,'evidence_ids':None,'limit_reason':'Outside requested target owner hands.'},'draws_and_searches':None,'draws_searches_accepted_account_reference':inherited_reference(row),'plays_in_order':acts,'numbering_basis':'Inherited sentence order, not newly inspected exact subaction order. Target owner turns replace this with accepted voluntary-action sequence where possible.','automatic_events_in_order':None,'board_at_start':board_ref(row),'board_after':board_ref(row),'owner_hand_end':unavailable_hand('Outside requested target owner hands.'),'discard_snapshot_ids':None,'turn_evidence_ids':None,'accepted_reference':inherited_reference(row),'limits':'Accepted battle account preserved. Newly observed hand fields are populated only for turns 1,3,5,7,9,11.'})
    return {'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':SOURCE['video_basename'],'sources':[SOURCE_ID],'turns':rows,'limits':'Fourteen accepted game turns are included as inherited context. This is not a fresh all-turn capture. Owner turn13 is explicitly outside the bounded supplement.'}

TARGETS = {
 1: {'start':['Poké Ball','Pokémon Center Lady','Heavy Helmet','Irida','Wailord'], 'start_t':37.5, 'draw':'Wailord','draw_evid':[36,37,37.5], 'end':['Pokémon Center Lady','Irida','Wailord'],'end_t':50.5,'draw_bound':[37,37.5],'first_bound':[37.5,39.5],'candidates':[37.5,39.5,42.5], 'fan':3,'range':None,'plays':[('card_play','Heavy Helmet','Active Wailmer','Attached'),('card_play','Poké Ball',None,'Obtains second Wailmer'),('card_play','Wailmer','Bench','Benched'),('end_turn',None,None,'No Energy attachment or attack')]},
 3: {'start':['Pokémon Center Lady','Irida','Wailord','Cyrus'],'start_t':72.3,'draw':'Cyrus','draw_evid':[71,72,72.3],'end':['Pokémon Center Lady','Irida','Cyrus'],'end_t':77,'draw_bound':[71,72.3],'first_bound':[72.3,74],'candidates':[72,74,77], 'fan':5,'range':None,'plays':[('evolution','Wailord','Active Wailmer','Non-ex Wailord 200 HP'),('energy_attachment',None,'Active Wailord','First Water'),('end_turn',None,None,'No attack with one Energy')]},
 5: {'start':['Pokémon Center Lady','Irida','Cyrus','Wailord ex'],'start_t':100.8,'draw':'Wailord ex','draw_evid':[99.6,100,100.8],'end':['Pokémon Center Lady','Irida','Cyrus'],'end_t':108,'draw_bound':[100,100.8],'first_bound':[100.8,101.2],'candidates':[102,105,108],'fan':None,'range':[7,8],'plays':[('evolution','Wailord ex','Benched Wailmer','Wailord ex 250 HP'),('energy_attachment',None,'Active non-ex Wailord','Second Water'),('end_turn',None,None,'No attack')]},
 7: {'start':['Pokémon Center Lady','Irida','Cyrus',"Professor's Research"],'start_t':132,'draw':"Professor's Research",'draw_evid':[131,132],'end':['Pokémon Center Lady','Irida','Cyrus','Copycat'],'end_t':146,'draw_bound':[131,132],'first_bound':[132,134],'candidates':[132,134,137],'fan':None,'range':[7,8],'plays':[('card_play',"Professor's Research",None,'Draws two cards'),('card_play','Indeedee ex','Bench','First Indeedee ex benched'),('energy_attachment',None,'Active non-ex Wailord','Third Water'),('end_turn',None,None,'No attack')]},
 9: {'start':['Pokémon Center Lady','Irida','Cyrus','Copycat','Lucky Ice Pop'],'start_t':205,'draw':'Lucky Ice Pop','draw_evid':[203,204,205],'end':['Soothing Shore','Lucky Ice Pop'],'end_t':275,'draw_bound':[203,204],'first_bound':[205,206],'candidates':[205,207,210],'fan':5,'range':None,'plays':[('ability','Indeedee ex','Active Wailord ex','First Watch Over heals 140 to 160'),('card_play','Lucky Ice Pop','Active Wailord ex','Heals to 180; heads returns Pop'),('card_play','Lucky Ice Pop','Active Wailord ex','Heals to 200; tails discards Pop'),('card_play','Copycat',None,'Remaining hand shuffled; draws to opponent count'),('card_play','Soothing Shore','Stadium','Replaces Peculiar Plaza'),('card_play','Indeedee ex','Bench','Second Indeedee ex benched'),('ability','Indeedee ex','Active Wailord ex','Second Watch Over heals to 220'),('card_play','Heavy Helmet','Active Wailord ex','Attached'),('energy_attachment',None,'Active Wailord ex','Water attached'),('end_turn',None,None,'Shore heals to 240; no attack')]},
 11: {'start':['Soothing Shore','Lucky Ice Pop',"Professor's Research"],'start_t':316.5,'draw':"Professor's Research",'draw_evid':[313,314.5,316.5],'end':['Soothing Shore','Cyrus'],'end_t':362,'draw_bound':[313,314.5],'first_bound':[316.5,319.5],'candidates':[314.5,316.5,319.5],'fan':4,'range':None,'plays':[('ability','Indeedee ex','Active Wailord ex','First Watch Over heals 150 to 170'),('ability','Indeedee ex','Active Wailord ex','Second Watch Over heals 170 to 190'),('card_play',"Professor's Research",None,'Draws Poké Ball and Cyrus; original prose did not assert reveal order'),('card_play','Poké Ball',None,'No Basic target; on-screen no-target message'),('energy_attachment',None,'Benched non-ex Wailord','Fourth Water; ex remains Active with one'),('card_play','Lucky Ice Pop','Active Wailord ex','Heals to 210; tails discards Pop'),('end_turn',None,None,'Shore heals to 230; no attack')]}
}

def draw_group(kind,names,times,order=None,returned=None,limit=None):
    return {'kind':kind,'caused_by':"Professor's Research" if kind=='research' else 'Copycat' if kind=='copycat' else 'Poké Ball' if kind=='search' else 'normal turn draw','linked_play_order':order,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':SOURCE['video_basename'],'timestamp_seconds':t,'evidence_ids':[frame_id(t)],'basis':'direct_native_observation','limit_reason':None} for i,(n,t) in enumerate(zip(names,times))],'returned_or_discarded_cards':returned,'source_video':SOURCE['video_basename'],'timestamp_seconds':times[0],'evidence_ids':[frame_id(t) for t in times],'limit_reason':limit}

def build():
    ledger=base_ledger(); supp=[]; frames={}
    def add_frame(t,role,n=None,selected=False,pre=None,note=None):
        f=frame_path(t)
        if not f.exists(): raise ValueError(f'Missing frame {t}: {f}')
        im=Image.open(f); assert im.size==(1170,2532)
        pref='ref_' if f.parent==OLD/'native' else ''
        bottom=P/'turn_evidence'/f'{pref}t{t:07.2f}_bottom.jpg';top=P/'turn_evidence'/f'{pref}t{t:07.2f}_top.jpg'
        im.crop((0,2025,1170,2532)).save(bottom,quality=95)
        im.crop((0,0,1170,550)).save(top,quality=95)
        d=TARGETS.get(n)
        mid=sum(d['draw_bound'])/2 if d else None
        frames[frame_id(t)]={'evidence_id':frame_id(t),'role':role,'turn_number':n,'who_played':'owner' if n else 'setup','source_video':SOURCE['video_basename'],'source_sha256':SOURCE['sha256'],'draw_animation_end_seconds':mid,'draw_end_precision':'bounded estimate; exact animation-end frame not measured' if d else None,'draw_end_supported_interval_seconds':d['draw_bound'] if d else None,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':round(t-mid,2) if d else None,'full_frame_path':str(f),'full_frame_storage':'reference_to_accepted_native' if pref else 'new_native_extraction','native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':str(bottom),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':str(top),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,550]},'selected_for_start_hand':selected,'before_first_play':pre,'unzoomed':pre if selected else None,'hand_spread':True if selected else None,'observation':note,'suitability_or_limit':'Draw-end offsets approximate; many later candidates follow the rapid first play. No later candidate is substituted for the chosen pre-play fan.'}
    add_frame(18,'opening_five',selected=True,pre=True,note='All five original cards before Active placement.')
    add_frame(19,'opening_active_selection',pre=True,note='Wailmer, original slot4, is selected for Active placement.')
    for n,d in TARGETS.items():
        row=ledger['turns'][n-1]
        start=hand(d['start'],[d['start_t']]);end=hand(d['end'],[d['end_t']])
        row['owner_hand_start']=start;row['hand_at_start']=copy.deepcopy(start);row['owner_hand_end']=end
        row['timing'].update({'draw_animation_end_seconds':sum(d['draw_bound'])/2,'draw_end_supported_interval_seconds':d['draw_bound'],'first_voluntary_move_seconds':None,'first_move_supported_interval_seconds':d['first_bound'],'before_end_action_seconds':d['end_t'],'timing_basis':'Bounded native candidate inspection; exact video frame PTS and exact first-action onset were not measured.'})
        row['opponent_hand_at_owner_turn_start']={'count':d['fan'],'supported_range':d['range'],'count_method':'Visible separate card-back faces and bottom boundaries in native top crop','basis':'direct_visual_count' if d['fan'] is not None else 'direct_visual_supported_range','evidence_ids':[frame_id(d['start_t'])],'limit_reason':None if d['fan'] is not None else 'Tight overlapping card backs obscure one boundary; no bookkeeping substituted for visual count.'}
        acts=[]
        for k,(kind,card,target,result) in enumerate(d['plays'],1):
            acts.append({'order':k,'kind':kind,'card_name':card,'target':target,'result':result,'basis':'inherited_accepted_review_not_new_visual_observation','source_video':SOURCE['video_basename'],'timestamp_seconds':None,'evidence_ids':None,'accepted_source_line':row['accepted_reference']['accepted_source_line'],'prompt_text':None,'response':None,'limit_reason':'Accepted sequence transcribed. This supplement does not freshly re-review accepted plays or declare unseen prompts declined.'})
        row['plays_in_order']=acts;row['numbering_basis']='Numbered voluntary sequence as far as accepted prose explicitly supports; End Turn is inherited from its pass/no-attack account. Automatic healing stays in the original result prose.'
        row['draws_and_searches']=[draw_group('normal',[d['draw']],[d['draw_evid'][-1]],limit='Draw identity directly observed during reveal or subsequent fan; animation-end time bounded separately.')]
        if n==1: row['draws_and_searches'].append(draw_group('search',['Wailmer'],[48],2,limit='Found Wailmer visibly in hand at48, then benched by50.5; exact search-reveal instant not measured.'))
        if n==7: row['draws_and_searches'].append(draw_group('research',['Indeedee ex','Copycat'],[137,139],1,limit='Indeedee revealed first at137; Copycat is the second new card visibly retained at139. Timestamp139 is its fan evidence after bench placement, not a claimed exact reveal onset.'))
        if n==9:
            g=draw_group('copycat',['Heavy Helmet','Indeedee ex','Soothing Shore','Lucky Ice Pop','Soothing Shore'],[249,249.5,249.5,250,252],4,returned=['Pokémon Center Lady','Irida','Cyrus'],limit='All five names and duplicate Shores directly preserved together at252. Reveal positions follow append order; times are retained reveal/fan anchors rather than exact onset. Earlier accepted native249 is a reveal anchor with approximate original seek provenance.')
            g['hand_count_before']=3;g['hand_count_after']=5;g['all_five_in_one_fan_evidence_ids']=[frame_id(252)];row['draws_and_searches'].append(g)
        if n==11:
            row['draws_and_searches'].append(draw_group('research',['Cyrus','Poké Ball'],[330,331],3,limit='Observed reveal order Cyrus then Poké Ball supplements the accepted unordered pair.'))
            row['draws_and_searches'].append({'kind':'search','caused_by':'Poké Ball','linked_play_order':4,'cards_in_reveal_order':[],'basis':'inherited_no_target_message_with_native336_reference','hand_count_after':3,'evidence_ids':[frame_id(336)],'limit_reason':'Known unsuccessful search; empty revealed-card array means no card obtained, not uninspected.'})
        add_frame(d['start_t'],'chosen_preplay_hand',n,True,True,note=', '.join(d['start']))
        for t in d['candidates']:
            if t != d['start_t']: add_frame(t,'draw_timed_candidate',n,False,t<d['first_bound'][0],note='Later candidate used for timing/hand reconciliation; suitability differs after first play.')
        add_frame(d['end_t'],'before_ending_action_hand',n,False,False,note=f"{len(d['end'])} cards: "+', '.join(d['end']))
        for t in d['draw_evid']:
            if frame_id(t) not in frames: add_frame(t,'normal_draw_reveal_or_boundary',n,note=d['draw'])
        extras={1:[48],7:[137,139],9:[211,232,236,241,246,247.5,248,249,249.5,250,251,252,254,263,265,268,272],11:[330,331,336,350]}.get(n,[])
        for t in extras:
            if frame_id(t) not in frames: add_frame(t,'draw_search_or_hand_reconciliation',n,note='Native reveal/fan reference; accepted plays remain inherited.')
        row['discard_snapshot_ids']=None
        row['discard_limits']='No opened discard-pile window is visible in the inspected hand/reveal evidence. No claim that every intervening second was freshly checked for pile views.'
        row['turn_evidence_ids']=[k for k,f in frames.items() if f['turn_number']==n]
        row['limits']='Target hand identities and counts are fresh native observations. Boards, points and voluntary plays remain inherited. Exact action onset and exact video-frame PTS were not measured; hidden opponent identities and discard contents remain unknown.'
        counts={1:'5 - Helmet1 - Poké Ball1 + found Wailmer1 - benched Wailmer1 =3.',3:'4 - evolution Wailord1 =3.',5:'4 - evolution Wailord ex1 =3.',7:'4 - Research1 + Research draws2 - benched Indeedee1 =4.',9:'5 - Pop1 + returned Pop1 - reused Pop1 - Copycat1 - three shuffled cards3 + five Copycat draws5 - Shore1 - Indeedee1 - Helmet1 =2.',11:'3 - Research1 + Research draws2 - no-target Poké Ball1 - Pop1 =2.'}[n]
        supp.append({'turn_number':n,'owner_turn_ordinal':(n+1)//2,'owner_hand_start':start,'owner_hand_end':end,'normal_draw':d['draw'],'draws_and_searches':row['draws_and_searches'],'first_voluntary_play':acts[0],'first_move_supported_interval_seconds':d['first_bound'],'opponent_hand_at_owner_turn_start':row['opponent_hand_at_owner_turn_start'],'hand_count_reconciliation':{'expression':counts,'basis':'inference_using_direct_counts_and_inherited_accepted_transactions','consistent':True},'evidence_ids':row['turn_evidence_ids'],'scope':'Only missing first-six-owner-turn hand fields, no fresh board/result/accepted-play review.'})
    # Every retained new full frame is source bound, including unsuitable candidates.
    for f in sorted((P/'turn_evidence').glob('t????.??.jpg')):
        t=float(f.stem[1:])
        if frame_id(t) not in frames:
            n=next((n for n,d in TARGETS.items() if d['draw_bound'][0]-2<=t<=d['end_t']+2),None)
            add_frame(t,'bounded_timing_candidate_not_selected',n,note='Retained for draw/first-action boundary; not chosen as pre-play fan.')
    save('TURN_LEDGER.json',ledger)
    save('HAND_SUPPLEMENT.json',{'is_template':False,'schema':'retrospective-hand-supplement-v1','game_id':SOURCE['video_basename'],'sources':[SOURCE_ID],'target_turn_numbers':[1,3,5,7,9,11],'capture_status':'complete_with_recording_limits','capture_scope':'Opening and six specified owner hands only. This is not a fresh full-battle capture.','target_rows':supp,'late_owner_hand_status':'Turn13 not requested and not freshly transcribed.'})
    opening=hand(['Poké Ball','Pokémon Center Lady','Heavy Helmet','Wailmer','Irida'],[18])
    opening.update({'source_video':SOURCE['video_basename'],'timestamp_seconds':18,'expected_card_slots':5,'recorded_card_count':5,'selected_active':{'name':'Wailmer','opening_position':4,'source_video':SOURCE['video_basename'],'timestamp_seconds':19,'evidence_ids':[frame_id(19)],'basis':'direct_selection_frame; placement inherited accepted setup'},'before_active_placement':True,'redraw_or_replacement':None,'redraw_limit_reason':'No redraw established; not inferred.','status':'observed'})
    save('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':SOURCE['video_basename'],'review_date':'2026-10-02','sources':[SOURCE_ID],'deck_name':'Wailord / Indeedee wall','destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','mode_flag':"Dustin's own play",'mode_basis':'inherited accepted review, online versus with no Auto activation visible','went_first':True,'opening':opening,'packet_files':{'prose':'REVIEW_SUPPLEMENT.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json','hands':'HAND_SUPPLEMENT.json'},'capture_status':'complete_with_recording_limits','capture_scope':'Only opening and first six owner hands (game turns1,3,5,7,9,11); all fourteen ledger turns carry inherited accepted context.','battle_review_status':'Reviewed, unchanged','outcome':{'result':'loss','owner_points':0,'opponent_points':3,'basis':'inherited accepted review, not freshly re-reviewed'},'limits':['Draw-end timestamps are bounded estimates and actual video-frame PTS unmeasured. Rapid first plays make later candidates unsuitable for start hands; selected dense pre-play frames are used.','Opponent fan at turns5/7 remains range7-8 because of overlapping backs.','Opened discard piles absent from retained target evidence; no new whole-turn pile audit.','All boards and accepted actions are inherited; ownerturn13 outside target.','DECK_USED is the supplied current live20-slot snapshot with historical version limits preserved.'],'lead_checked':False})
    save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':SOURCE['video_basename'],'sources':[SOURCE_ID],'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'top_crop':'fan, clock and visible Energy Zone at [0,0,1170,550]','fixed_grid_is_turn_start_evidence':False},'frames':list(frames.values()),'discard_snapshots':None,'discard_limit':'No opened pile seen in inspected native target/reveal frames. Not a claim of a fresh exhaustive discard audit.','scheduled_capture_limits':'Offsets tied to bounded draw-end windows. Exact +1/+3/+6 timing is not claimed for every candidate. Nearest retained candidates and denser pre-play captures preserve all target hands; several later scheduled candidates are after play.48 new-full-frame cap respected.'})
    save('UNCERTAINTIES.json',{'scope':'Target hand supplement only','capture_status':'complete_with_recording_limits','unresolved_hand_identities':[],'astra_question':None,'limits':[{'field':'opponent_hand_count','turns':[5,7],'supported_range':[7,8],'reason':'One tightly overlapping card-back boundary cannot be cleanly separated.'},{'field':'timing','reason':'Actual frame PTS not measured. Draw-end and first-move timings bounded rather than frame-exact; late scheduled candidates may follow play.'},{'field':'discard_piles','reason':'No opened pile in retained hand evidence; intervening full turns not newly audited for discard windows.'},{'field':'boards_actions_outcome','reason':'Inherited by exact accepted-row provenance, not freshly re-reviewed.'},{'field':'ownerturn13','reason':'Explicitly outside requested first-six-owner-turn scope.'},{'field':'deck_game_version','reason':'Supplied current20-slot log snapshot preserved; unseen historical version not proven.'}]})
    a=json.loads((P/'ASSIGNMENT.json').read_text(encoding='utf-8-sig'));a.update({'status':'submitted_for_independent_sol_check','capture_status':'complete_with_recording_limits','completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_full_frames':48,'independent_acceptance':'pending'});save('ASSIGNMENT.json',a)
    all_files=[f for f in (P/'turn_evidence').glob('*.jpg')];new=[f for f in all_files if re.fullmatch(r't\d{4}\.\d{2}\.jpg',f.name)];crops=[f for f in all_files if f.name.endswith(('_bottom.jpg','_top.jpg'))]
    unique_refs={f['full_frame_path'] for f in frames.values() if f['full_frame_storage']=='reference_to_accepted_native'}
    started=datetime.datetime.fromisoformat(a['started_at_utc'].replace('Z','+00:00'));finished=datetime.datetime.fromisoformat(a['completed_at_utc'])
    save('METRICS.json',{'new_extracted_full_frames':len(new),'new_full_frame_cap':48,'new_full_frame_bytes':sum(f.stat().st_size for f in new),'retained_crop_count':len(crops),'retained_crop_bytes':sum(f.stat().st_size for f in crops),'referenced_existing_native_frames':len(unique_refs),'source_full_hash_reads_completed':1,'source_hash_match':True,'default_source_read_denied_attempts':1,'default_extraction_denied_attempts':1,'new_extraction_passes_completed':3,'source_read_notes':'One escalated SHA256 read hydrated the archived online-only source.38+8+2 targeted extractions used the hydrated file; no source copies or moves.','started_at_utc':a['started_at_utc'],'submitted_at_utc':a['completed_at_utc'],'wall_seconds':(finished-started).total_seconds(),'hydration_wait_seconds_estimate':390,'source_decoding_threads':2,'token_usage':None,'dollar_usage':None,'usage_limit_reason':'Not measured or available in this worker.'})

if __name__ == '__main__':
    build()
