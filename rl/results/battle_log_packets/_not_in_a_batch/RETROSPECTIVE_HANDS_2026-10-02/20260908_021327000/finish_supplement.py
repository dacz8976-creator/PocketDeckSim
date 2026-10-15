import json, pathlib, copy, re, datetime
from PIL import Image

P=pathlib.Path(__file__).resolve().parent
def read(n):
    raw=(P/n).read_bytes()
    try: s=raw.decode('utf-8-sig')
    except UnicodeDecodeError: s=raw.decode('cp1252')
    return json.loads(s)
def write(n,v): (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def repair(v):
    if isinstance(v,str):
        if any(x in v for x in ['Ã','â']):
            try: return v.encode('cp1252').decode('utf-8')
            except (UnicodeError,LookupError): pass
        return v
    if isinstance(v,list): return [repair(x) for x in v]
    if isinstance(v,dict): return {k:repair(x) for k,x in v.items()}
    return v
for f in P.glob('*.json'):
    if f.name!='ROOT_SOURCE_VERIFICATION.json': write(f.name,repair(read(f.name)))
e=read('TURN_EVIDENCE.json'); l=read('TURN_LEDGER.json'); h=read('HAND_SUPPLEMENT.json'); g=read('PAUSE_GAME.json'); u=read('UNCERTAINTIES.json'); a=read('ASSIGNMENT.json')
for t,turn,role,obs in [(169.5,6,'research_draw','Research reveal 1: Sightseer; Flute is the prior remaining hand.'),(170.5,6,'research_draw',"Research reveal 2: Team Rocket's Drowzee; Sightseer is already in hand."),(190,6,'board_after','Jigglypuff promotion animation, card identity and printed HP60 visible; no later turn7 card or Energy play yet.'),(353,10,'board_after','Boost Dash damage resolved: Mewtwo HP40, owner Raticate HP150, before opponent turn11 draw.')]:
    base=copy.deepcopy(e['frames'][-1]); base.update(evidence_id=f'f{t:07.2f}',role=role,turn_number=turn,who_played='owner',draw_animation_end_seconds=None,offset_after_draw_seconds=None,requested_source_seconds=t,selected_for_start_hand=False,before_first_play=False,observation=obs,suitability_or_limit='Targeted native observation; seek time is source-local, PTS not independently measured.')
    fn=P/'turn_evidence'/f't{t:07.2f}.jpg'; im=Image.open(fn)
    base['full_frame_path']=str(fn); base['native_dimensions']={'width':im.width,'height':im.height}
    for kind,bounds in [('bottom',(0,2025,1170,2532)),('top',(0,0,1170,582))]:
        out=fn.with_name(fn.stem+'_'+kind+'.jpg'); im.crop(bounds).save(out,quality=95)
        base[kind+'_crop']={'path':str(out),'pixel_bounds_x0_y0_x1_y1':list(bounds)}
    e['frames'].append(base)
r=l['turns'][5]['draws_and_searches'][1]
r.update(timestamp_seconds=169.5,evidence_ids=['f0169.50','f0170.50'],hand_count_before=1,hand_count_after=3,limit_reason=None)
for i,t in enumerate([169.5,170.5]):
    r['cards_in_reveal_order'][i].update(reveal_position=i+1,timestamp_seconds=t,evidence_ids=[f'f{t:07.2f}'],basis='direct_native_reveal',limit_reason=None)
l['turns'][5]['plays_in_order'][1].update(evidence_ids=['f0169.50','f0170.50'],hand_count_after=3)
def change_ref(obj,old,new):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k=='evidence_ids': obj[k]=[new if x==old else x for x in v]
            else: change_ref(v,old,new)
    elif isinstance(obj,list):
        for x in obj: change_ref(x,old,new)
for idx,t,old in [(5,190,'f0188.00'),(9,353,'f0379.00')]:
    row=l['turns'][idx]; board=row['board_after']; change_ref(board,old,f'f{t:07.2f}')
    board['requested_source_seconds']=t; row['timing']['end_after_resolution_seconds']=t
    row['turn_evidence_ids'].append(f'f{t:07.2f}')
    board['basis']='Direct native boundary state, with accepted printed maxima; explicit conflicts remain separately retained.'
    for side in ['owner','opponent']:
        z=board[side]['energy_zone']; z.update(evidence_ids=[f'f{t:07.2f}'],limit_reason=None,status='observed')
        z['this_turn']={'type':None,'count':0,'available':False}; z['next']={'type':'Psychic','count':1,'available':None}
    if idx==5:
        board['opponent']['active']['limit_reason']='Promotion animation visible; identity and HP60 clear. No turn7 action has occurred in this view.'
        row['automatic_events_in_order'][0].update(effect='Jigglypuff knockout; owner point1; remaining Jigglypuff promoted',basis='Native188/190, with accepted transition account')
# Turn7 now starts from the actual preceding promotion rather than the vacant pre-promotion view.
change_ref(l['turns'][6]['board_at_start'],'f0188.00','f0190.00'); l['turns'][6]['board_at_start']['requested_source_seconds']=190
l['energy_zone_audit'].setdefault('inspected_requested_source_seconds',[])[:] += [190,353]
limits=['Turn12 draw +6 candidate would be after concession; no ongoing owner turn exists then.','Draw animation endpoints and source-local seeks are approximate visual timing; PTS was not independently measured.','No opened discard panel was observed in 410 reduced samples at 1 fps or retained native checkpoints. Full piles and scroll coverage remain null; brief openings between samples can be missed.','Opponent Energy Zones at98s and379s are obscured by waiting overlays; exact current and next fields at those views remain null. Owner154s and404s current sockets are empty during generation, with later candidates showing the orb.','Hidden opponent card identities and the exact historical20-card log snapshot are unavailable.','Game mode remains uncertain: no Auto control observed in sampled or retained unobscured views; card zooms and overlays obscure some UI.','Turn12 warning response is not established before opponent concession.']
for obj in [e,l,h,g,u]:
    if 'capture_status' in obj: obj['capture_status']='complete_with_recording_limits'
    obj['independent_acceptance_status']='pending'
    if 'limits' in obj: obj['limits']=limits
e['scheduled_capture_limits']=[x for x in e['scheduled_capture_limits'] if '108' not in str(x)]
for s in e['discard_snapshots']:
    s['limit_reason']=limits[2]; s['scan_reference']='cue_audit/CUE_AUDIT.json'
u['review_gaps']=[]; u['recording_limits']=limits; u['pending_acceptance']=['Bounded Astra reconciliation of consequential conflicts','Independent Sol acceptance']
g['mode']['basis']='No Auto control observed in retained native full frames or 410 reduced1fps locator samples. End Turn and card inspections are visible. Some UI is covered by card zooms or overlays. Hidden mode remains uncertain; owner rule would classify any visible Auto control, even OFF, as computer and exclude ladder.'
a.update(new_native_fullframe_cap=108,status='submitted_for_independent_acceptance',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()); a['cap_approval_history'] += [104,108]
for n,v in [('TURN_EVIDENCE.json',e),('TURN_LEDGER.json',l),('HAND_SUPPLEMENT.json',h),('PAUSE_GAME.json',g),('UNCERTAINTIES.json',u),('ASSIGNMENT.json',a)]: write(n,v)
audit={'source':g['sources'][0]['video_basename'],'sha256':g['sources'][0]['sha256'],'status':'reviewed_sampled_locator_scan','sample_count':410,'sampling_rate_fps':1,'source_interval_seconds':[0,410.492],'reviewed_grids':[f'grid_{n:02d}.jpg' for n in range(1,13)],'dimensions':[234,506],'native_evidence':False,'timestamp_precision':'Approximate midpoint labels from fps1 locator extraction; independently measured PTS unavailable.','opened_discard_panels_observed':False,'full_pile_established':False,'visible_declines_observed':False,'auto_control_observed':False,'native_followups':[169.5,170.5,190,353],'material_cues':[{'seconds':[108.5,160.5],'kind':'Thieving Incisors choice','result':'Energy transfer subsequently observed; no declined choice seen.','native_refs':['f0108.00','f0110.00','f0159.00','f0169.50']},{'seconds':[117.5,121.5],'kind':'Researcher coin search','result':'No found cards, tails; accepted action retained.','native_refs':['f0121.00']},{'seconds':[221.5,224.5],'kind':'Sightseer deck panel','result':'Deck inspection, not discard panel; Hypno selected.','native_refs':['f0224.00']},{'seconds':[268.5,269.5],'kind':'Hypno confusion prevented','native_refs':['f0269.00']},{'seconds':[293.5,295.5],'kind':'Confusion attack did nothing, turn9','native_refs':['f0298.00'],'basis':'Accepted action corroborated by sampled locator; exact attack name inherited.'},{'seconds':[323.5,328.5],'kind':'Both Poké Ball no eligible target warnings','native_refs':['f0323.00','f0328.00']},{'seconds':[391.5,396.5],'kind':'Confusion attack did nothing, turn11','native_refs':['f0391.00','f0396.00']},{'seconds':[406,406],'kind':'End turn Energy warning','native_refs':['f0406.00'],'basis':'Native captured warning falls between reduced sample views; response not established.'}],'limitations':'This examines 410 sampled views, not every instant. Native406 warning missed by adjacent reduced samples demonstrates brief-prompt limitation. No new result review. No opened discard panel found, so no full pile contents inferred.'}
write('cue_audit/CUE_AUDIT.json',audit)
# Refresh the human supplement without changing inherited quoted claims.
text=(P/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8'); text=repair(text)
text=text.replace('Status: incomplete_review, submitted for independent acceptance.','Status: complete_with_recording_limits. Source inspection is complete; independent acceptance is pending.')
text=text.replace('f0154.00, f0179.00, f0188.00; TURN_LEDGER turn6','f0154.00, f0169.50, f0170.50, f0179.00, f0190.00; TURN_LEDGER turn6').replace('f0188.00, f0209.00; TURN_LEDGER turn7','f0190.00, f0209.00; TURN_LEDGER turn7').replace('f0303.00, f0345.00, f0379.00; TURN_LEDGER turn10','f0303.00, f0345.00, f0353.00; TURN_LEDGER turn10')
text=text.split('## Limits and unfinished acceptance')[0]+'## Recording limits and pending acceptance\n\n'+''.join('- '+x+'\n' for x in limits)+'\nThe systematic locator audit reviewed 410 reduced views at1fps across0 to410.492s. All12 grids were inspected for discard panels, warnings, visible declines and Auto controls. No opened discard panel or Auto control was found. Named draw order at169.5/170.5 and boundary states at190/353 were then retained as native evidence. Native406 contains a brief warning missed by adjacent locator samples, so sampling is explicitly limited. See cue_audit/CUE_AUDIT.json.\n\nTurn6 Research draws Sightseer first at169.5s, then Team Rocket\'s Drowzee at170.5s. The before-end hand is unchanged. Both Energy Zones were independently inspected in existing boundary native frames; obscured and generation-pending views retain precise limits.\n\nAstra reconciliation and independent Sol acceptance remain pending. Existing accepted battle result and files remain unchanged.\n'
(P/'REVIEW_SUPPLEMENT.md').write_text(text,encoding='utf-8')
metrics=read('METRICS.json'); natives=list((P/'turn_evidence').glob('t????.??.jpg')); crops=list((P/'turn_evidence').glob('t????.??_*jpg')); allimgs=list((P/'turn_evidence').glob('*.jpg'))
metrics.update(wall_seconds=round((datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(a['started_utc'].replace('Z','+00:00'))).total_seconds(),2),retained_native_fullframe_count=len(natives),retained_crop_count=len(crops),locator_or_comparison_count=len(allimgs)-len(natives)-len(crops),retained_image_bytes=sum(x.stat().st_size for x in allimgs),new_extraction_count=len(natives),worker_original_seek_read_invocations=8,worker_original_sequential_locator_reads=1,approved_final_cap=108,capture_status='complete_with_recording_limits',remaining_work=['Bounded Astra reconciliation','Independent Sol acceptance'],usage_reason='Not measured',cue_locator_sample_count=410,cue_locator_grid_count=12,cue_locator_image_bytes=sum(x.stat().st_size for x in (P/'cue_audit').rglob('*.jpg')))
write('METRICS.json',metrics)
print('Packaged',len(natives),'native frames;',len(crops),'crops;',metrics['locator_or_comparison_count'],'comparisons. Source work complete; acceptance pending.')
