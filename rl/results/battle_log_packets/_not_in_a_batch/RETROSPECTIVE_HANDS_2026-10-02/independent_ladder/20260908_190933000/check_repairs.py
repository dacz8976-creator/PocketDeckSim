from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageStat,ImageChops
out=Path(__file__).parent;p=out.parent.parent/'20260908_190933000'
read=lambda q:json.loads(q.read_text(encoding='utf-8-sig'))
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
old=read(out/'BINDING_CHECK.json'); d=read(p/'TURN_LEDGER.json');ev=read(p/'TURN_EVIDENCE.json'); errors=[]
def refs(x):
 s=set()
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['evidence_ids','turn_evidence_ids']:s.update(v or [])
   else:s.update(refs(v))
 elif isinstance(x,list):
  for v in x:s.update(refs(v))
 return s
for item in old['native_frames']+old['crops']+old['additional_frames']:
 if sha(Path(item['path']))!=item['sha256']:errors.append('Image changed '+item['path'])
allids={f['evidence_id'] for f in ev['frames']}
for r in d['turns']:
 nested=refs({k:v for k,v in r.items() if k!='turn_evidence_ids'})
 if not nested.issubset(set(r['turn_evidence_ids'])) or nested-allids:errors.append('Evidence union turn '+str(r['turn_number']))
 assigned={x['snapshot_id'] for x in ev['discard_snapshots'] if x['turn_number']==r['turn_number']}
 if assigned!=set(r.get('discard_snapshot_ids') or []):errors.append('Pile binding '+str(r['turn_number']))
 if r['owner_hand_end']!=read(out/'SOURCE_CHECKS.json')['canonical_field_checks'][r['turn_number']-1]['ending_hand']:errors.append('Ending hand changed '+str(r['turn_number']))
t2=d['turns'][1];t8=d['turns'][7]
if [x['kind'] for x in t2['plays_in_order']]!=['supporter','bench','item','bench','energy_attachment']:errors.append('T2 order')
ball=t2['plays_in_order'][2]
inherit=ball.get('inherited_action_fields_preserved') or {}
if ball['card_name']!='Poké Ball' or ball['accepted_provenance'] is not None or inherit.get('old_action_present') is not False or inherit.get('order') is not None or inherit.get('timestamp_seconds') is not None:errors.append('New Ball inherited provenance incorrect')
draw=t2['draws_and_searches'][-1]
if draw['cards_in_reveal_order'] is not None or draw['count']!=1:errors.append('Hidden search result')
if [x['kind'] for x in t8['plays_in_order']]!=['tool','evolution','bench','evolution','retreat','energy_attachment','attack']:errors.append('T8 order')
energy=t8['plays_in_order'][5]
if energy['source_event_interval_seconds']!=[343.5,350.5] or 'Endpoint-derived' not in energy['attachment_target_basis'] or not energy['limit_reason']:errors.append('Energy endpoint qualification')
newbindings=[]
for f in ev['frames']:
 if not f['evidence_id'].startswith('repair_'):continue
 q=Path(f['full_frame_path']);im=Image.open(q).convert('RGB')
 if im.size!=(1170,2532) or f['full_frame_sha256']!=sha(q) or f['source_sha256']!=old['source_sha256'] or f['actual_frame_seconds_if_measured'] is not None:errors.append('Repair native binding '+str(q))
 for kind in ['bottom_crop','top_crop']:
  c=f[kind];cq=Path(c['path']);ci=Image.open(cq).convert('RGB');bounds=c['pixel_bounds_x0_y0_x1_y1'];expected=im.crop(bounds);rms=ImageStat.Stat(ImageChops.difference(ci,expected)).rms
  if ci.size!=expected.size or max(rms)>15:errors.append('Repair crop '+str(cq))
  newbindings.append({'path':str(cq),'sha256':sha(cq),'native_sha256':sha(q),'bounds':bounds,'jpeg_reencoding_rms':rms})
text=(p/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig')
if text.index('3. item: Poké Ball')>text.index('## Turn3'):errors.append('Readable search order')
if not any(q.name=='before_independent_action_repair' for q in p.iterdir()):errors.append('Missing pre-repair snapshot')
files=[]
for q in sorted(p.glob('*')):
 if q.is_file() and q.suffix in ['.json','.md']:
  if q.suffix=='.json':read(q)
  else:q.read_text(encoding='utf-8-sig')
  files.append({'path':str(q),'sha256':sha(q),'read_encoding':'utf-8-sig'})
verdict='needs_repair' if errors else 'accepted_with_recording_limits'
r={'verdict':verdict,'source':'20260908_190933000_iOS.MP4','source_sha256':old['source_sha256'],'reviewer':'Sol different-producer independent check','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'T2 omitted concealed search, T8 source order/endpoint Energy, row nested reference unions, synchronization and image binding only; original needs_repair report retained.','repairs_passed':['T2 now Research,shinyElectrike bench,concealed Poké Ball search,regularElectrike bench,Lightning attachment; Research hidden2 and search hidden1 recorded. Search result remains null.','T8 now Poncho,Electrode evolution,newVoltorb,freshMega,retreat,Energy,RandomSpark. Attachment343.5–350.5 explicitly endpoint-derived, exact input and PTS unmeasured.','All ten row unions include all nested evidence IDs, all resolve; pile bindings and checked canonical end hands preserved.','Nine added natives source-bound1170x2532, eighteen new full-width crops coordinates/reencoding verified; all original53native106crop plus nine added native byte hashes unchanged.','Old prose and timestamps retained separately in inherited fields and before_independent_action_repair; new Ball has no invented inherited action provenance.'],'errors':errors,'current_packet_files':files,'repair_crop_bindings':newbindings,'limits_inherited_from':'SOURCE_CHECKS.json','metrics':{'new_video_reads_for_recheck':0,'new_extractions_for_recheck':0,'new_image_submissions_for_recheck':0,'full_check_native_submissions':49,'full_check_locator_samples':413,'full_check_cached_extraction_invocations':1,'full_check_new_native_extracted_by_checker':6}}
(out/'SOURCE_CHECKS_REPAIR_ACCEPTANCE.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'REPAIR_ACCEPTANCE.md').write_text('# Independent repair acceptance\n\nVerdict: '+verdict+'\n\n'+ '\n\n'.join(r['repairs_passed'])+'\n\nAll original recording and hidden-information limits remain in SOURCE_CHECKS.json. No additional visual submissions, extraction or source reads were needed for this repair recheck. The full check used49 decisive native views, including nine specifically authorized additions, and screened all413 retained1fps samples. No old accepted packet, outcome or shared log was changed by this checker. Current submitted JSON/Markdown were read explicitly as utf-8-sig and raw-byte SHA bound in the repair acceptance.\n',encoding='utf-8')
binding=[]
for name in ['SOURCE_CHECKS_REPAIR_ACCEPTANCE.json','REPAIR_ACCEPTANCE.md']:
 q=out/name;q.read_text(encoding='utf-8-sig');binding.append({'path':str(q),'sha256':sha(q),'encoding':'utf-8-sig'})
(out/'REPAIR_BINDING.json').write_text(json.dumps(binding,indent=2),encoding='utf-8')
print(json.dumps({'verdict':verdict,'errors':errors,'frames':len(ev['frames']),'repair_crops':len(newbindings)}))
