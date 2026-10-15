import json
from pathlib import Path
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def read(n):return json.loads((B/n).read_text(encoding='utf-8-sig'))
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def fid(t):return f'F{t:07.2f}'
limit='One-second locator sampling screened the complete recorded interval; subsecond panels/prompts between samples cannot be excluded. No opened discard panel or visible decline dialog appears in the283 inspected samples. Full hidden pile contents remain unknown; no every-instant absence claim.'
scan=read('LOCATOR_SCAN.json');scan.update(inspection_status='complete_interval_samples_visually_inspected',samples_inspected=283,grids_inspected=15,nominal_inspected_interval_seconds=[0,282],complete_recording_duration_seconds=282.628,opened_discard_panel_located=False,visible_decline_dialog_located=False,yes_no_end_turn_warning_located=False,limits=[limit,'Reduced locators were used for panel/prompt location only; card identities remain grounded in native evidence.'],additional_native_targets=[116,175.5,199,246.5,263.5,276.5],additional_native_cap_approved=86);save('LOCATOR_SCAN.json',scan)
led=read('TURN_LEDGER.json');led['capture_status']='complete_with_recording_limits';led['independent_acceptance_status']='pending';led['limits']=[limit,'Historical exact20-card deck unavailable; hidden opponent faces unknown; requested frame seek time distinct from unmeasured actualPTS.']
for row in led['turns']:
 row['limits']=[limit]
 row['prompt_and_decline_audit']=dict(locator_scan='LOCATOR_SCAN.json',visible_declines=None,visible_declines_limit='None located in inspected samples; shorter unsampled events cannot be excluded.',end_turn_warning=None,end_turn_warning_limit='No warning dialog located in sampled views; no inference of a response to an unobserved prompt.')
 for a in row['plays_in_order']:
  if a['limit_reason'] and 'Exact prompt' in a['limit_reason']:a['limit_reason']='Input authorship/decision response not exposed; exact UI text only recorded where native evidence supports it.'
  if row['turn_number']==7 and a['card_name']=="Team Rocket's Master Plan":a['result']='Ogerpon Confusion attempt blocked; Heads avoids self-Confusion. Subsequent normal Darkness attachment goes to new Bench Magmar.'
  if row['turn_number']==7 and a['kind']=='no_effect':a.update(prompt_text="Teal Mask Ogerpon ex didn't become Confused",response='Automatic prevention notification; no choice/decline prompt')
  if row['turn_number']==10 and a['card_name']=="Team Rocket's Goo-zooka":a.update(prompt_text='Retreat Cost is 1 more',response='Automatic effect notification',evidence_ids=[fid(218.5)])
  if row['turn_number']==12 and a['card_name']=='X Speed':a.update(prompt_text='Retreat Cost is 1 less',response='Automatic effect notification',evidence_ids=[fid(259.5)])
  if row['turn_number']==4 and a['kind']=='bench':a.update(timestamp_seconds=None,timestamp_interval_seconds=[90,93.5],evidence_ids=[fid(90.6),fid(93.5)],basis='Native search/bench transition; accepted prose confirms bench action, but exact placement time unmeasured')
  if row['turn_number']==10 and a['card_name']=="Team Rocket's Goo-zooka":a.update(timestamp_seconds=214.6,evidence_ids=[fid(214.5),fid(218.5)],basis='Accepted prose time214.6; native214.5/218.5 show consumption and effect, requested seek time not measuredPTS')
 if row['turn_number']==10:row['timing']['first_voluntary_move_seconds']=214.6;row['timing']['first_voluntary_move_basis']='Inherited accepted Goo-zooka action anchor; native consumption bracket212.5-214.5; actualPTS unmeasured'
 for boundary in ['board_at_start','board_after']:
  own=row[boundary]['owner'];cards=([own['active']] if own['active'] else [])+own['bench_in_position_order'];oger=any(p['name']=='Teal Mask Ogerpon ex' for p in cards)
  if oger:
   own['board_effects'].append('Soothing Wind: each owner Pokémon with any attached Energy recovers from all Special Conditions and cannot be affected by them (native printed text F0012.00).')
   for p in cards:
    if p['attached_energy']['total']:p['active_effects']=list(dict.fromkeys(p['active_effects']+['Protected from all Special Conditions by owner Ogerpon Soothing Wind']))
 row['turn_evidence_ids']=list(dict.fromkeys(row['turn_evidence_ids']))
def event(t,text,time):
 row=led['turns'][t-1];row['automatic_events_in_order'].append(dict(kind='notification',text=text,source_video=row['source_video'],requested_source_seconds=time,actual_frame_seconds_if_measured=None,evidence_ids=[fid(time)],basis='native full-frame observation'));row['turn_evidence_ids'].append(fid(time))
event(5,'Master Plan gold Poké Ball coin face visible; subsequent Active Magmar is not Confused. Native still precedes settled Heads lettering; locator~116s locates Heads animation.',116)
event(8,"Whimsicott ex didn't become Poisoned",175.5)
event(9,"Teal Mask Ogerpon ex didn't become Confused",199)
event(11,'Whimsicott ex is now Confused',246.5)
event(12,'Whimsicott ex recovered from being Confused',263.5)
event(12,'Victory!',276.5)
led['turns'][6]['automatic_events_in_order']=[x.replace('Heads permits extra Darkness attachment to newly benched Magmar','Heads avoids self-Confusion; normal generated Darkness attaches to newly benched Magmar') if isinstance(x,str) else x for x in led['turns'][6]['automatic_events_in_order']]
for row in led['turns']:
 row['automatic_events_in_order']=list({json.dumps(x,sort_keys=True):x for x in row['automatic_events_in_order']}.values())
 row['turn_evidence_ids']=list(dict.fromkeys(row['turn_evidence_ids']))
 for boundary in ['board_at_start','board_after']:row[boundary]['owner']['board_effects']=list(dict.fromkeys(row[boundary]['owner']['board_effects']))
save('TURN_LEDGER.json',led)
for name in ['PAUSE_GAME.json','HAND_SUPPLEMENT.json']:
 obj=read(name);obj.update(capture_status='complete_with_recording_limits',independent_acceptance_status='pending',source_audit='LOCATOR_SCAN.json')
 if name=='PAUSE_GAME.json':obj['limits']=led['limits'];obj['outcome'].update(native_result_evidence_ids=[fid(272),fid(276.5)],preserved_accepted_outcome=True);obj['opening']['setup_prompt']=dict(text='Waiting for opponent to set up...',evidence_ids=[fid(12)],response='Automatic wait notification; no manual-input authorship established')
 else:
  for r in obj['target_rows']:r['limits']=[limit]
 save(name,obj)
e=read('TURN_EVIDENCE.json');e['native_frames']=read('EXTRACTION_MANIFEST.json');e['locator_scan']='LOCATOR_SCAN.json';e['source_audit_status']='complete_with_recording_limits'
for f in e['native_frames']:
 t=f['requested_source_seconds'];f['roles']=['native full-frame source anchor; full-width hand and top crops retained']
 if t in [10,12,20]:f['roles'].append('setup/opening')
 if t in [4.4,10,41,212.5,259.5]:f['roles'].append('mode/control evidence')
 if t in [116,148.8,151,175.5,199,246.5,259.5,263.5]:f['roles'].append('effect/condition/coin notification')
 if t in [272,276.5]:f['roles'].append('terminal points/result')
 for r in led['turns']:
  if f['evidence_id'] in (r['owner_hand_start'].get('evidence_ids') or []):f['roles'].append(f"turn{r['turn_number']} selected starting-hand identity")
  if f['evidence_id'] in (r['owner_hand_end'].get('evidence_ids') or []):f['roles'].append(f"turn{r['turn_number']} ending-hand identity")
  for s in r['timing'].get('draw_capture_candidates',[]):
   if s['evidence_id']==f['evidence_id']:f['roles'].append(f"turn{r['turn_number']} draw-offset candidate; before_first_play={s['before_first_play']}")
for d in e['discard_snapshots']:
 d.update(status='inspected_closed_pile_with_recording_limits',limit_reason='No opened pile in systematic1fps samples. Closed pile/top face inspected at native boundary; full contents cannot be identified from a closed pile. Shorter opened views between samples cannot be excluded.',full_contents=None)
e['periodic_native_discard_views']=[dict(requested_source_seconds=t,evidence_ids=[fid(t)],owner_visible_top_card=name,opponent_visible_top_card=None,opponent_limit='Face present but title not independently transcribed from this angled closed-pile view; full pile unknown',full_opened_panel=False) for t,name in [(175.5,'Poké Ball'),(199,'Poké Ball'),(246.5,'Copycat'),(263.5,'X Speed'),(270,'X Speed')]]
save('TURN_EVIDENCE.json',e)
u=read('UNCERTAINTIES.json');u['items']=[i for i in u['items'] if i['field'] not in ['prompt_and_declines','discard_full_contents']];u['items'][:0]=[dict(field='prompt_and_decline_sampling',status='recording_sampling_limit',reason=limit),dict(field='discard_full_contents',status='unexposed_in_inspected_views',reason='Periodic closed-pile views retained; no opened pile in283 one-second locator samples. Full pile contents unknown; short unsampled opening cannot be excluded.')];save('UNCERTAINTIES.json',u)
ass=read('ASSIGNMENT.json');ass.update(capture_status='complete_with_recording_limits',status='worker_complete_independent_acceptance_pending',completed_utc=datetime.now(timezone.utc).isoformat(),approved_new_native_frame_cap=86,retained_new_native_frames=86,remaining_capture_fields=[],independent_acceptance_status='pending');save('ASSIGNMENT.json',ass)
obs=read('OBSERVATIONS.json');obs.update(status='complete_with_recording_limits',turns={str(r['turn_number']):r for r in led['turns']},limits=led['limits'],independent_acceptance_status='pending');save('OBSERVATIONS.json',obs)
met=read('METRICS.json');met.update(worker_status='source_work_complete_independent_acceptance_pending',finished_utc=ass['completed_utc'],new_native_frames=86,new_native_crops=172,approved_native_frame_cap=86,locator_decode_passes=1,reduced_locator_samples=283,locator_grids=15,locator_rate_fps=1,locator_source_interval_seconds=[0,282.628],native_evidence_storage_bytes=sum(p.stat().st_size for p in (B/'turn_evidence').glob('*') if p.is_file()),locator_storage_bytes=sum(p.stat().st_size for p in (B/'locator_scan').glob('*') if p.is_file()));save('METRICS.json',met)
met.update(worker_cached_source_frame_seek_calls=86,worker_cached_source_locator_decode_passes=1,wall_seconds=(datetime.fromisoformat(ass['completed_utc'])-datetime.fromisoformat(ass['registered_utc'].replace('Z','+00:00'))).total_seconds());save('METRICS.json',met)
mode=read('MODE_QUESTION.json');mode.update(status='resolved_by_bounded_astra_check',mode_flag=led['mode_observation'],classification=led['classification'],excluded_from_ladder=True,astra_mode_check=led['astra_mode_check']);save('MODE_QUESTION.json',mode)
cp=read('LOCATOR_CHECKPOINT.json');cp.update(status='approved_targets_extracted_and_inspected',retained_full_native_frames=86);save('LOCATOR_CHECKPOINT.json',cp)
cp=read('CHECKPOINT.json');cp.update(status='source_work_complete_after_locator_audit_and_approved_cap86',retained_new_native_frames=86,remaining_material_inspection=[],source_audit='LOCATOR_SCAN.json');save('CHECKPOINT.json',cp)
p=B/'REVIEW_SUPPLEMENT.md';text=p.read_text(encoding='utf-8');text=text.replace('Native80-frame evidence','Native86-frame evidence').replace('Head s','Heads').replace('Confusion blocked; coin Heads gives attachment permission','Confusion blocked; Heads avoids self-Confusion. Normal generated Darkness attached later').replace('Capture status is incomplete_review pending independent field checking and the bounded prompt/discard gaps. Exact prompts/visible declines and full opened discard-pile scrolls are not exhaustively established by retained80 frames. This is incomplete capture, not a claim that footage hid or omitted those views.','Capture status is complete_with_recording_limits; independent acceptance is pending separately. The full recording was screened using283 one-second reduced locator samples across15 grids. No opened discard panel, Yes/No end-turn warning, or visible decline dialog was located in those samples. Shorter events between samples cannot be excluded. Full unopened pile contents remain unknown. Native references preserve located effect and condition messages.')
paragraph='Additional native notifications: F0175.50 shows Whimsicott did not become Poisoned while Ogerpon is Benched; F0199.00 shows Ogerpon did not become Confused during its knockout; F0246.50 applies Confusion to Whimsicott; F0263.50 clears it after retreat; F0276.50 shows Victory. F0116.00 preserves the Master Plan coin face; it does not grant Energy attachment permission. The printed Soothing Wind text in F0012.00 protects each owner Pokémon with attached Energy while Ogerpon is in play. Periodic closed-pile views are listed in TURN_EVIDENCE.json.'
text=text.replace(paragraph+'\n','');text+='\n'+paragraph+'\n'
p.write_text(text,encoding='utf-8')
print('Source audit complete;86native;283locator samples; independent acceptance pending')
