import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageStat

ROOT = Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs')
P = ROOT/'Recording_QA/RETROSPECTIVE_HANDS_2026-10-02/20260929_002539000'
OUT = P.parent/'independent_ladder/20260929_002539000'
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
submission=read(P/'SUBMISSION.json')
fail=[]; payload=[]; evidence=[]
for f in submission['files']:
 actual=sha(f['path']); payload.append(dict(f,actual_sha256=actual,match=actual==f['sha256']))
 if actual!=f['sha256']:fail.append('Payload hash: '+f['path'])
frames=read(P/'TURN_EVIDENCE.json')['frames']
ids={f['evidence_id'] for f in frames}
for f in frames:
 full=Path(f['full_frame_path']); im=Image.open(full).convert('RGB')
 rec={'evidence_id':f['evidence_id'],'path':str(full),'sha256':sha(full),'dimensions':list(im.size),'crops':[]}
 if im.size!=(1170,2532):fail.append('Dimensions '+f['evidence_id'])
 if f['source_sha256']!=submission['source_sha256']:fail.append('Source SHA '+f['evidence_id'])
 for kind in ['top_crop','bottom_crop']:
  c=f[kind]; bounds=c['pixel_bounds_x0_y0_x1_y1']; crop=Image.open(c['path']).convert('RGB'); expected=im.crop(bounds)
  mae=sum(ImageStat.Stat(ImageChops.difference(crop,expected)).mean)/3 if crop.size==expected.size else None
  rec['crops'].append({'kind':kind,'path':c['path'],'sha256':sha(c['path']),'bounds':bounds,'dimensions':list(crop.size),'pixel_mae_vs_native_crop':mae,'binding':'JPEG recompression of unscaled native region'})
  if mae is None or mae>12:fail.append('Crop binding '+f['evidence_id']+' '+kind)
 if f.get('decode_log'):
  text=Path(f['decode_log']).read_text(encoding='utf-8-sig')
  pts=[float(x) for x in re.findall(r'pts_time:([0-9.]+)',text)]
  actual=f['actual_frame_seconds_if_measured']
  rec['pts_log_match']=bool(pts and abs(pts[0]-actual)<0.0001)
  if not rec['pts_log_match']:fail.append('PTS '+f['evidence_id'])
 evidence.append(rec)
def refs(obj):
 result=set()
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k.endswith('evidence_ids') and isinstance(v,list):result.update(v)
   else:result.update(refs(v))
 elif isinstance(obj,list):
  for v in obj:result.update(refs(v))
 return result
ledger=read(P/'TURN_LEDGER.json'); hands=read(P/'HAND_SUPPLEMENT.json'); te=read(P/'TURN_EVIDENCE.json')
piles={x['snapshot_id'] for x in te['discard_snapshots']}
for name in ['TURN_LEDGER.json','HAND_SUPPLEMENT.json','MODE_CHECK.json','DECK_USED.json']:
 missing=refs(read(P/name))-ids
 if missing:fail.append(name+' unresolved '+str(sorted(missing)))
for row in ledger['turns']:
 nested=refs({k:v for k,v in row.items() if k!='turn_evidence_ids'})
 if not nested.issubset(set(row['turn_evidence_ids'])):fail.append('Nested refs omitted T'+str(row['turn_number']))
 if set(row['discard_snapshot_ids'])-piles:fail.append('Pile ids T'+str(row['turn_number']))
for hand in hands['target_rows']:
 row=ledger['turns'][hand['turn_number']-1]
 if hand['hand_at_start']!=row['owner_hand_start']:fail.append('Start hand sync T'+str(hand['turn_number']))
 if hand['end_hand_after_automatic_draw']!=row['owner_hand_end']:fail.append('End hand sync T'+str(hand['turn_number']))
 for key in ['hand_at_start','before_end_hand','end_hand_after_automatic_draw']:
  if len(hand[key]['cards_left_to_right'])!=hand[key]['count']:fail.append('Hand count '+key)
source=read(P/'SOURCE_REFERENCE.json'); receipt=read(P/'ROOT_SOURCE_VERIFICATION.json'); old=read(source['old_accepted_source_json'])
source_match=source['sha256']==receipt['actual_sha256']==receipt['expected_sha256']==old['source_sha256']==submission['source_sha256']
if not source_match:fail.append('Source receipt mismatch')
locator=read(P/'LOCATOR_PREPROCESSING.json'); locator_bad=[]
for f in locator['sample_files']:
 if sha(f['path'])!=f['sha256']:locator_bad.append(f['path'])
if locator_bad:fail.append('Locator SHA mismatch')
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'json_read_encoding':'utf-8-sig','submission_path':str(P/'SUBMISSION.json'),'submission_sha256':sha(P/'SUBMISSION.json'),'payload_files':payload,'frame_and_crop_hash_binding':evidence,'source_receipt_match':source_match,'source_movie_reads':0,'new_extractions':0,'frames':len(frames),'crops':len(frames)*2,'locator_files_hashed':len(locator['sample_files']),'locator_hash_failures':locator_bad,'turn_rows':len(ledger['turns']),'owner_hands':len(hands['target_rows']),'discard_snapshots':len(piles),'failures':fail,'binding_check_pass':not fail,'additional_receipt_hashes':{str(p):sha(p) for p in [P/'ROOT_SOURCE_VERIFICATION.json',P/'LOCATOR_PREPROCESSING.json',Path(source['old_accepted_source_json']),Path(source['old_accepted_prose'])]}}
(OUT/'FILE_AND_EVIDENCE_BINDING.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['payload_files','frames','crops','turn_rows','owner_hands','discard_snapshots','binding_check_pass','failures']},ensure_ascii=False))
