from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageChops,ImageStat
out=Path(__file__).parent
p=out.parent.parent/'20260908_190933000'
read=lambda q:json.loads(q.read_text(encoding='utf-8-sig'))
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
ref=read(p/'SOURCE_REFERENCE.json'); frozen=read(Path(ref['frozen_binding_path'])); verification=read(p/'SOURCE_VERIFICATION.json')
ev=read(p/'TURN_EVIDENCE.json'); ledger=read(p/'TURN_LEDGER.json'); hand=read(p/'HAND_SUPPLEMENT.json')
errors=[]; images=[]; crops=[]
for f in ev['frames']:
 q=Path(f['full_frame_path']); im=Image.open(q).convert('RGB')
 if im.size!=(1170,2532): errors.append('Native dimensions '+str(q))
 if f['source_sha256']!=ref['sha256']:errors.append('Frame source SHA '+str(q))
 images.append({'path':str(q),'sha256':sha(q),'dimensions':im.size,'requested_seconds':f['requested_source_seconds']})
 for key in ['bottom_crop','top_crop']:
  c=f[key]; path=Path(c['path']); bounds=c['pixel_bounds_x0_y0_x1_y1']; ci=Image.open(path).convert('RGB'); expected=im.crop(bounds)
  rms=ImageStat.Stat(ImageChops.difference(expected,ci)).rms
  if ci.size!=expected.size or max(rms)>15: errors.append('Crop binding '+str(path))
  crops.append({'path':str(path),'sha256':sha(path),'parent_sha256':sha(q),'bounds':bounds,'dimensions':ci.size,'jpeg_reencoding_rms':rms})
def refs(x):
 s=set()
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['evidence_ids','turn_evidence_ids']:s.update(v or [])
   else:s.update(refs(v))
 elif isinstance(x,list):
  for v in x:s.update(refs(v))
 return s
ids={f['evidence_id'] for f in ev['frames']}
field_checks=[]
for r in ledger['turns']:
 nested=refs({k:v for k,v in r.items() if k!='turn_evidence_ids'})
 missing=nested-set(r.get('turn_evidence_ids') or [])
 unknown=nested-ids
 if missing or unknown:errors.append({'turn':r['turn_number'],'missing_union':sorted(missing),'unresolved':sorted(unknown)})
 assigned=[x['snapshot_id'] for x in ev['discard_snapshots'] if x['turn_number']==r['turn_number']]
 if set(assigned)!=set(r.get('discard_snapshot_ids') or []):errors.append('Discard row binding '+str(r['turn_number']))
 field_checks.append({'turn':r['turn_number'],'ending_hand':r.get('owner_hand_end'),'nested_reference_count':len(nested),'discard_ids':assigned})
files=[]
for q in sorted(p.glob('*')):
 if q.is_file() and q.suffix in ['.json','.md']:
  if q.suffix=='.json':read(q)
  else:q.read_text(encoding='utf-8-sig')
  files.append({'path':str(q),'sha256':sha(q),'read_encoding':'utf-8-sig'})
additional=[]
for folder in [p/'independent_added_evidence',out/'added_t8']:
 for q in sorted(folder.glob('*.jpg')):
  additional.append({'path':str(q),'sha256':sha(q),'dimensions':Image.open(q).size,'source_sha256':ref['sha256'],'actual_pts_if_measured':None})
checked=[17.5,44.5,45,50.5,51.5,56.5,68,87,114.5,115.5,117.5,120.5,136.5,137.5,138.5,139.5,143.5,167,212,214,218.5,219.5,234,241,287,290,300,302.5,308,354,357,358,363,374,385,392,397.5,403.5,409,412.5]
repair=[{'turn':2,'issue':'Opponent Poke Ball search omitted from numbered actions and draws/searches.','required':'Add concealed search after first shiny Electrike bench and before regular Electrike bench. Search card identity remains unknown; do not infer exact find from later bench. Keep inherited old narrative separately.','evidence':['cue_audit/grid_03.jpg samples100.5-103.5','independent_added_evidence/t0100.50.jpg concealed reveal','t0102.50 preceding second bench','t0108.50 second Electrike and readable Poke Ball opposing pile top','native114.5 resulting board']},{'turn':8,'issue':'Inherited action order contradicts fresh source sequence.','required':'New numbered sequence Poncho, Electrode evolution, new Voltorb bench, fresh Mega evolution, retreat to Electrode, manual Lightning to Active Electrode, Random Spark. Preserve old ordering and timestamps as inherited conflict.','evidence':['added_t8/t0314.50.jpg Poncho revealed before evolution','t0317.50 Electrode evolving after Poncho already attached','t0333.50 Voltorb slot3 while slot2 still Electrike','t0335.50 Mega evolution slot2','t0339.50 current Lightning remains available; Electrode has zero attached','t0343.50 Electrode promoted Active with zero attached','native354 Active Electrode now one Lightning, damagedMega still two on bench','grid10/11 attack350.5-353.5'] }]
limits=['Unplayed opponent hand and normal/search draw identities concealed by backs; Poké Ball exact find unknown.','No opened discard panel detected in all413 inspected locator samples; visible tops only, hidden full pile content/order unestablished.','All413 retained1fps samples inspected for bounded cues, not every recorded instant; unsampled subsecond events and input transitions can be missed.','Native requested source offsets and locator midpoint labels are source-local approximations; decoded PTS and exact input instant unmeasured.','First T1 Research first card50.5 flips back;51.5 partially recognizable Poké Ball behind Small Balloon. Exact first-card label/order remains inherited accepted prose with partial native support.','Historical exact20-card log snapshot unavailable; do not substitute current deck.','No Auto option visible in inspected native controls or413 locator samples, absence limited to inspected views. Any visible Auto even OFF would classify computer and exclude ladder.','Final409 clear board has empty owner Active and surviving MegaAltaria on bench1;412.5 blurred point overlay does not establish promotion.','Rapid turn1 44.5 and turn3 114.5 untouched hands serve actual starts;45 and117.5 afterplay states do not replace starts. Offset1/3/6 views after first play are qualified rather than reconstructed untouched hands.']
result={'verdict':'needs_repair','reviewer':'Sol, different producer independent source-field check','source':ref['source'],'source_sha256':ref['sha256'],'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_binding':{'frozen':frozen,'current_verification':verification,'original_video_rehashed_by_checker':False},'required_repairs':repair,'other_binding_errors':errors,'checked_native_seconds':checked,'added_native_seconds':[100.5,102.5,108.5,314.5,317.5,333.5,335.5,339.5,343.5],'checked_fields':['Opening5 positional order and Igglybuff slot2','All5 owner untouched starts and ending names/counts; named normals, Research, Copycat four refills, Ball finds','All10 both boards HP, typed Energy, tools, conditions/effect icons, TrainingArea and current/next Zones','Opponent fan counts, periodic visible pile tops, warning302.5 and OK resolution','Numbered plays and bounded no-effect/decline/prompts via413sample screen'],'canonical_field_checks':field_checks,'limits':limits,'submitted_packet_files':files,'metrics':{'original_video_sha_reads':0,'cached_original_extraction_invocations_by_checker':1,'new_native_frames_extracted_by_checker':6,'lead_added_native_frames_inspected':3,'existing_decisive_native_submissions':40,'total_native_submissions':49,'locator_samples_screened':413,'locator_grids_screened':12,'packet_edits':0,'shared_log_edits':0,'outcome_audit':False}}
(out/'SOURCE_CHECKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'BINDING_CHECK.json').write_text(json.dumps({'source_sha256':ref['sha256'],'native_frames':images,'crops':crops,'additional_frames':additional,'packet_files':files,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
(out/'METRICS.json').write_text(json.dumps(result['metrics'],indent=2),encoding='utf-8')
text='# Independent field check: 20260908_190933000\n\nVerdict: needs_repair.\n\nTwo bounded repairs remain. Turn2 omits the opponent Poké Ball search between the shiny Electrike bench and regular Electrike bench. Native100.5 shows the concealed reveal,102.5 still has only one benched Electrike, and108.5 adds the regular Electrike and readable Poké Ball opposing pile top. The exact searched card is unknown.\n\nTurn8 must use the fresh sequence: Protective Poncho, Electrode evolution, new Voltorb bench, fresh Mega Manectric evolution, retreat to Electrode, manual Lightning to Active Electrode, Random Spark. Native314.5/317.5/333.5/335.5/339.5/343.5 directly establish the successive identities/states. At339.5 current Lightning is still available and Electrode has none;343.5 promoted Electrode still has none;354 has one attached. Thus attachment follows retreat. Earlier reduced-grid impression that the Zone was empty at339.5 was incorrect and is superseded by the native frame. Keep inherited old narrative/order/timestamps separate.\n\nThe opening five, Igglybuff selection, all five owner start/end hands, named normal draws, both Research draws and four Copycat refill cards, search results, ten board rows, HP, typed Energy, Small Balloon, Poncho, Training Area, Zones and fans agree with checked native views. Canonical end and nested/pile bindings were checked mechanically; any binding issues are listed in SOURCE_CHECKS.json. At302.5 the Supporter warning shows OK and subsequent attack resolves while Sabrina stays unused. Final409 has owner Active empty after KO; the surviving Altaria remains bench1, and412.5 is a blurred overlay.\n\nOwner ending hands: T1 Copycat/Eevee/Small Balloon (3), native68; T3 Sabrina/Swablu/Training Area/Field Blower (4),143.5; T5 Sabrina/Training Area/Field Blower/Mega Altaria ex/Eevee (5),234; T7 Sabrina/Training Area/Field Blower/Espeon (4),300; T9 Training Area/Field Blower/Espeon (3),385. The following opponent rows carry these unchanged visible owner hands.\n\nSource frozen/current SHA receipts agree. All53 existing native frames and106 crops were hashed, dimensions and crop coordinate/reencoding binding checked. Forty decisive natives plus nine specifically authorized additional natives were inspected. All413 samples in12 retained locator grids were screened for cues. One six-frame cached-source extraction was authorized specifically for the T8 order gap; no new SHA read, general source replay, packet edits, log changes or outcome audit occurred.\n\n'+ '\n'.join('- '+s for s in limits)+'\n'
(out/'INDEPENDENT_CHECK.md').write_text(text,encoding='utf-8')
binding=[]
for q in sorted(out.glob('*')):
 if q.suffix in ['.json','.md'] and q.name!='REPORT_BINDING.json':
  q.read_text(encoding='utf-8-sig');binding.append({'path':str(q),'sha256':sha(q),'encoding':'utf-8-sig'})
(out/'REPORT_BINDING.json').write_text(json.dumps(binding,indent=2),encoding='utf-8')
print(json.dumps({'verdict':'needs_repair','binding_errors':errors,'native_count':len(images),'crop_count':len(crops),'additional':len(additional),'frozen_sha':frozen.get('sha256')}))
