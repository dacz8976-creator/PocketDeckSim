from pathlib import Path
from PIL import Image
import json,datetime,hashlib
P=Path(__file__).resolve().parent;B=P.parents[2];OLD=P.parents[1]/'20260907_232617_v5_review/final_packet'
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
ev=read('TURN_EVIDENCE.json');hand=read('HAND_SUPPLEMENT.json');pg=read('PAUSE_GAME.json');ledger=read('TURN_LEDGER.json')
sha=pg['sources'][0]['sha256'];video=pg['sources'][0]['video_basename']
def eid(t):return 'f'+f'{t:.3f}'
def add(t,role,n=None):
 path=OLD/'frames'/f'{t:07.3f}.jpg';im=Image.open(path);w,h=im.size;id=eid(t)
 if any(x['evidence_id']==id for x in ev['frames']):return id
 bottom=P/'turn_evidence'/f'{id}_bottom.png';top=P/'turn_evidence'/f'{id}_top.png';im.crop((0,int(h*.8),w,h)).save(bottom);im.crop((0,0,w,720)).save(top)
 ev['frames'].append({'evidence_id':id,'role':[role],'turn_number':n,'source_video':video,'source_sha256':sha,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'full_frame_path':str(path),'full_frame_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_dimensions':{'width':w,'height':h},'bottom_crop':{'path':str(bottom),'pixel_bounds_x0_y0_x1_y1':[0,int(h*.8),w,h]},'top_crop':{'path':str(top),'pixel_bounds_x0_y0_x1_y1':[0,0,w,720]},'new_extraction':False});return id
add(111,'owner_opened_discard',3)
for t in [40,47,52,100,104,134,138,162,170,210,215,237,240,260,265,317,320,355,360,407,410,440]:add(t,'Energy_Zone_boundary_observation')
ids=['n13.000','n137.300']
assert all(any(x['evidence_id']==i for x in ev['frames']) for i in ids)
opening=['Professor\'s Research','Professor\'s Research',"Team Rocket's Goo-zooka",'Lisia','Eevee']
pg['opening'].update({'timestamp_seconds':13,'cards_left_to_right':[{'position':i+1,'name':name,'basis':'direct_native_preplacement_fan','evidence_ids':['n13.000','n13.500'],'limit_reason':None} for i,name in enumerate(opening)],'before_active_placement':True,'status':'observed','evidence_ids':['n13.000','n13.500','f15.000'],'limit_reason':None,'redraw_or_replacement':{'observed':False,'basis':'Setup cards dealt12s, intact13s; Eevee selected15s; no redraw visible in inspected setup window'}})
pg['opening']['selected_active']['opening_position']=5
for h in hand['turns']:
 if h['turn_number']==4:
  h['selected_frame_seconds']=137.3;h['draw_animation_end_seconds']=137.3;h['draw_end_supported_interval_seconds']=[137,137.3];h['draw_end_basis']='Upper bound: card center at137s, in fan by137.3s; approximate, not measured PTS';h['hand_at_start']['evidence_ids']=['n137.300'];h['hand_at_start']['limit_reason']=None;h['target_status']='observed'
  for c in h['hand_at_start']['cards_left_to_right']:c.update({'basis':'direct_native_untouched_postdraw_fan','evidence_ids':['n137.300'],'limit_reason':None})
  h['candidate_evidence_ids'].insert(0,'n137.300');h['opponent_fan']['evidence_ids']=['n137.300']
hand['capture_status']='complete_with_recording_limits';hand['status']='submitted_for_independent_check';hand['target_turn_numbers']=[2,4,6,8,10];hand['target_rows']=hand['turns']
limits=['Exact historical20-card deck list unavailable from captured log/pre-season history','Hidden opponent draw/search identities remain unknown','Old/new frame names record requested source seeks; exact decoded PTS not measured','Normal draw completion is bounded by inspected frames; timing estimates not exact','T10 retained+3 candidate unavailable;360s and365s show unchanged preplay hand','One opened owner discard view at111s: Lisia, no discarded Energy; no opponent opened inventory found in retained381-frame overview; sampling does not certify absence between frames','Terminal blur conceals Energy Zone detail; final board/points inherit accepted full review']
hand['limits']=limits;pg['limits']=limits;pg['capture_status']='complete_with_recording_limits';ledger['limits']=limits
zoneStarts={1:40,2:52,3:104,4:137.3,5:170,6:215,7:240,8:265,9:320,10:360,11:410}
zoneEnds={1:47,2:100,3:134,4:162,5:210,6:237,7:260,8:317,9:355,10:407,11:440}
def zone(side,cur,t,terminal=False):
 return {'this_turn':{'type':None if terminal or not cur else ('Lightning' if side=='owner' else 'Fighting'),'count':None if terminal else cur,'available':None if terminal else bool(cur)},'next':{'type':None if terminal else ('Lightning' if side=='owner' else 'Fighting'),'count':None if terminal else 1,'available':None},'basis':'Direct native token/preview inspection; small preview is next Energy, not an attachment','evidence_ids':[('n' if t==137.3 else 'f')+f'{t:.3f}'],'limit_reason':'Terminal award blur obscures token detail' if terminal else 'Preview availability is future, not usable this turn; source UI uses icons rather than permanent text lines','source_seconds_requested':t}
for row in ledger['turns']:
 n=row['turn_number']
 if n%2==0:
  h=next(x for x in hand['turns'] if x['turn_number']==n);row['hand_at_start']=h['hand_at_start'];row['owner_hand_start']=h['hand_at_start'];row['owner_hand_end']=h['owner_hand_end'];row['opponent_hand_at_owner_turn_start']=h['opponent_fan'];row['timing']['draw_animation_end_seconds']=h['draw_animation_end_seconds'];row['timing']['draw_end_supported_interval_seconds']=h['draw_end_supported_interval_seconds']
  if n==4:row['turn_evidence_ids'].insert(0,'n137.300')
 for key in ['board_at_start','board_after']:
  b=row[key];isstart=key=='board_at_start';ztime=zoneStarts[n] if isstart else zoneEnds[n]
  for side in ['owner','opponent']:
   cur=1 if isstart and ((side=='owner' and n%2==0 and n!=4) or (side=='opponent' and n%2==1 and n!=1)) else 0
   b[side]['energy_zone']=zone(side,cur,ztime,n==11 and not isstart)
   # Tool/condition absence is bounded to inspected native board views plus inherited complete action account.
   for poke in [b[side]['active'],*b[side]['bench_in_position_order']]:
    if poke is None:continue
    poke['tool']=None;poke['tool_status']='none_visible_in_inspected_board_views';poke['tool_limit']='No attachment in inherited complete action account; selected native views show no Tool'
    poke['special_conditions']=[];poke['conditions_limit']='No condition applied in inherited account; inspected native board views show ability/effect badges, not Special Conditions'
    poke['condition_basis']='accepted action account plus selected native board inspection'
  # Bench position correction from native215/236/265/360 views, without changing accepted card/HP/Energy claims.
  phase_after=n if not isstart else n-1
  bench=b['owner']['bench_in_position_order']
  if phase_after>=5:
   for poke in bench:
    poke['bench_position']=1 if poke['name']=='Eevee' else (3 if poke['name']=="Team Rocket's Raticate ex" else (2 if poke['attached_energy']['total'] else 3))
   bench.sort(key=lambda p:p['bench_position'])
  if phase_after==7:b['opponent']['active']['active_effects']=['Coordinated Unit','Goo-zooka retreat increase last observed235s; expiration not directly displayed']
 row['limits']=['Boards/actions/results inherited from exact accepted prose section; hands/fans/Zone tokens newly observed','Opponent identities hidden','Energy Zone token snapshots sometimes occur just after turn banner; explicit source times supplied','No hidden Tool/effect/card identity inferred']
 row['discard_snapshot_ids']=['owner-discard-111'] if n==3 else None
 if n==3:row['source_observed_inspections']=[{'kind':'opened_owner_discard','timestamp_seconds':111,'result':'Lisia shown; no discarded Energy','evidence_ids':['f111.000']}]
ev['discard_snapshots']=[{'snapshot_id':'owner-discard-111','turn_number':3,'pile_owner':'owner','source_video':video,'timestamp_seconds':111,'cards_in_view':[{'name':'Lisia','count':1}],'discarded_energy':[],'energy_display':'No discarded Energy','scroll_coverage':'Single visible card and empty remainder; no scrolling observed','full_pile_established':True,'evidence_ids':['f111.000'],'basis':'Direct native open Your discard pile view','limit_reason':None},{'snapshot_id':'opponent-discard-views','turn_number':None,'pile_owner':'opponent','source_video':video,'timestamp_seconds':None,'cards_in_view':None,'scroll_coverage':None,'full_pile_established':False,'evidence_ids':None,'limit_reason':'No opened opponent pile found in inspected381 retained-frame locators; between-frame absence not certified'},{'snapshot_id':'later-owner-discard-views','turn_number':None,'pile_owner':'owner','source_video':video,'timestamp_seconds':None,'cards_in_view':None,'scroll_coverage':None,'full_pile_established':False,'evidence_ids':None,'limit_reason':'No further opened owner inventory found in retained evidence after111s. Top discard card alone is not a complete pile.'}]
ev['scheduled_capture_limits']=limits[2:6];ev['retained_frame_overview_scan']={'files':381,'method':'Five locator sheets scanned for opened discard screens only; native111s inspected for content; locator views do not supply hand identities','locator_files':[str(P/f'discard_locator_{n}.jpg') for n in [0,80,160,240,320]]}
for fr in ev['frames']:
 if fr['evidence_id']=='n137.300':fr.update({'selected_for_start_hand':True,'before_first_play':True,'unzoomed':True,'hand_spread':True,'suitability_or_limit':None,'turn_number':4,'draw_animation_end_seconds':137.3,'draw_end_estimate_basis':'Upper bound interval137–137.3s'})
 if fr['evidence_id']=='f138.000':fr.update({'selected_for_start_hand':False,'before_first_play':False,'suitability_or_limit':'Research already selected/lifted; replaced by native137.3s untouched fan'})
save('TURN_EVIDENCE.json',ev);save('HAND_SUPPLEMENT.json',hand);save('PAUSE_GAME.json',pg);save('TURN_LEDGER.json',ledger)
save('UNCERTAINTIES.json',{'capture_status':'complete_with_recording_limits','limits':limits,'consequential_questions':[],'native_inspected_setup_window':[11.5,14],'native_inspected_turn4_window':[137.3,137.9],'no_guessing':'No unknown cards inferred from deck/count/later action; no opponent AI inference','independent_acceptance':'pending Sol checks'})
ref=read('SOURCE_REFERENCE.json');ref['source_identity_basis']='Frozen accepted binding plus one authorized original SHA256 verification (SOURCE_ACCESS.json); exact match';ref['native_frame_dimensions_verified']={'count':381,'dimensions':[1170,2532],'verification':'PIL metadata read of all retained native frames'};save('SOURCE_REFERENCE.json',ref)
for f in (OLD/'frames').glob('*.jpg'):
 with Image.open(f) as im:assert im.size==(1170,2532)
assignment=read('ASSIGNMENT.json');assignment.update({'status':'submitted_for_independent_check','capture_status':'complete_with_recording_limits','completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_frames_extracted':10,'main_status_preserved':'Reviewed'});save('ASSIGNMENT.json',assignment)
receipt=read('SOURCE_ACCESS.json');receipt.update({'status':'hash_verified_and_bounded_extraction_complete','new_frames':10,'extraction_requested_times':[11.5,12,12.5,13,13.5,14,137.3,137.5,137.7,137.9],'original_hash_passes':1,'original_hydration_sessions':1,'source_preserved':True,'lead_storage_release_pending':True});save('SOURCE_ACCESS.json',receipt)
text=(P/'REVIEW_SUPPLEMENT.md').read_text();text=text[:text.index('Opening:')]+'''Opening at13s before placement, left to right: Professor's Research (full art), Professor's Research (standard), Team Rocket's Goo-zooka, Lisia, Eevee. Eevee in slot5 is selected Active by15s. Native137.3s recovers the untouched T4 postdraw hand before Research selection. Five of five owner starts and ending hands have readable names/counts; every owner normal draw and all Research, Lisia and Copycat results are named. Poke Ball on T8 has a known empty search result.

Numbered plays preserve accepted order and include failed attachment drags(T2), forced Oricorio selection(T5), Raticate ability acceptance(T8), Sabrina inspection without play(T8), no-target Poke Ball(T8), and canceled Energy warning(T10). Both boards, points, Stadium and Energy Zones are structured per row. Native215/236/265/360 evidence supplies Bench positions: after Sabrina, energized Rattata occupies middle slot2; new Eevee occupies left slot1; the other Rattata/Raticate occupies right slot3. HP/Energy/card/outcome claims retain accepted provenance.

One opened owner discard at111s directly shows Lisia and No discarded Energy. All381 retained frames were scanned in locator sheets for other opened pile views; none were found. This does not certify absence between sampled frames. Full native evidence is retained by reference, with native bottom-fifth and top crops. Exact historical20-card list remains unavailable from live Ladder Log capture and pre-season history; no current list is substituted.

Capture status: complete with recording/evidence limits, submitted for independent Sol checks. Exact decoded PTS and draw end moments are not measured; timing uses requested source seconds and bounded intervals. T10+3 candidate was not retained;360s and365s both show the unchanged hand before386s warning. Terminal blur conceals token detail. Hidden opponent card identities and game mode remain explicit.

The original was hydrated once, SHA256 matched once, and ten bounded native frames were extracted. Accepted packet, source bytes, review index/events, external log and simulator remain unchanged. Lead still needs to restore online-only storage after independent acceptance.
''';(P/'REVIEW_SUPPLEMENT.md').write_text(text)
# Remove only redundant newly produced initial crops; originals/reused frame files stay untouched.
used={Path(f[k]['path']).resolve() for f in ev['frames'] for k in ['bottom_crop','top_crop']}
for path in (P/'turn_evidence').glob('*.png'):
 if path.resolve() not in used:path.unlink()
metrics={'reviewer':'/root/sol_retro_ladder_232617','model':'Sol inherited parent settings','new_native_frames':10,'new_native_frame_bytes':sum(p.stat().st_size for p in (P/'new_frames').glob('*.jpg')),'reused_native_frames_referenced':sum(not f['new_extraction'] for f in ev['frames']),'native_frame_dimensions':[1170,2532],'crop_count':len(list((P/'turn_evidence').glob('*.png'))),'crop_bytes':sum(p.stat().st_size for p in (P/'turn_evidence').glob('*.png')),'image_tool_submissions':59,'image_submission_count_basis':'Manual count of images emitted for visual inspection in this worker turn; includes locators and repeated views','original_hydrations':1,'original_hash_passes':1,'original_video_decode_extractions':10,'target_owner_hands':5,'observed_owner_hands':5,'opening_slots_observed':5,'structured_turn_rows':11,'named_owner_normal_draws':5,'named_effect_draw_search_cards':10,'no_effect_searches':1,'token_usage':None,'cost_usage':None,'usage_limit':'Not measured; exact tokens/dollars unavailable','elapsed_seconds':(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(assignment['assigned_at'])).total_seconds(),'storage_release_pending':True}
save('METRICS.json',metrics)
print(json.dumps(metrics))
