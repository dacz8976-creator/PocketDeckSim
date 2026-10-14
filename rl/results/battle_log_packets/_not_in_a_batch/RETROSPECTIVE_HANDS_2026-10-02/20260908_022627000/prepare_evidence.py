import json,csv,re
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
old=Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\wsl-review-campaign-2026-09-22\battle-20260908-022627')
sha='5689a2c45eda9b0629d7a2616852beef6fedb8396bdfe34c080b4c136e4e364e'
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
ass=json.loads((B/'ASSIGNMENT.json').read_text());ass['registered_utc']='2026-10-02T21:34:28+00:00';save('ASSIGNMENT.json',ass)
with (old/'evidence/EVIDENCE_MANIFEST.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
native=[];dimensions={}
out=B/'reused_crops';out.mkdir(exist_ok=True)
for r in rows:
 p=old/'evidence'/r['evidence_filename']
 with Image.open(p) as im:
  w,h=im.size;key=f'{w}x{h}';dimensions[key]=dimensions.get(key,0)+1
  if (w,h)==(1170,2532):
   t=float(r['source_timestamp_seconds']);eid=f'R{t:07.2f}';bottom=[0,2025,w,h];top=[0,0,w,550]
   im.crop(bottom).save(out/(eid+'_hand.jpg'),quality=95);im.crop(top).save(out/(eid+'_top.jpg'),quality=95)
   native.append(dict(evidence_id=eid,source_video='20260908_022627000_iOS.MP4',source_sha256=sha,requested_source_seconds=t,actual_frame_seconds_if_measured=None,timestamp_basis=r['sampling_method']+'; prior manifest source timestamp, decodedPTS not supplied',full_frame_path=str(p),native_dimensions=dict(width=w,height=h),bottom_crop=dict(path=str(out/(eid+'_hand.jpg')),pixel_bounds_x0_y0_x1_y1=bottom),top_crop=dict(path=str(out/(eid+'_top.jpg')),pixel_bounds_x0_y0_x1_y1=top),source_binding=str(old/'evidence/PREPROCESS_LOG.md'),manifest=str(old/'evidence/EVIDENCE_MANIFEST.csv')))
save('REUSED_MANIFEST.json',native)
save('EVIDENCE_INVENTORY.json',dict(source_sha256=sha,prior_source_binding=str(old/'evidence/PREPROCESS_LOG.md'),manifest=str(old/'evidence/EVIDENCE_MANIFEST.csv'),manifest_entries=len(rows),dimensions=dimensions,native_entries=len(native),excluded_folder='evidence/discarded_invalid_pts_shift_20260922T1529Z',exclusion_reason='Detected invalid shiftedPTS; explicitly excluded from old manifest and current claims',metadata_probe='PIL image header dimensions; all retained manifest files opened for dimension probe',native_timestamp_limit='Actual decoded framePTS not independently supplied; exact requested source timestamps retained separately'))
grid=B/'locator_grids';grid.mkdir(exist_ok=True)
overview=[r for r in rows if r['evidence_filename'].startswith('overview/')]
for start in range(0,len(overview),20):
 sheet=Image.new('RGB',(936,2650),'white');d=ImageDraw.Draw(sheet)
 for j,r in enumerate(overview[start:start+20]):
  x=j%4*234;y=j//4*530;d.text((x+4,y+3),r['source_timestamp_seconds']+'s',fill='black')
  with Image.open(old/'evidence'/r['evidence_filename']) as im:sheet.paste(im.resize((234,506)),(x,y+24))
 sheet.save(grid/f'grid_{start:03d}_{min(start+19,len(overview)-1):03d}.jpg',quality=90)
save('LOCATOR_SCAN.json',dict(source_sha256=sha,kind='reused_prior_manifest_bound_complete1fps_timeline',source_duration_seconds=721.046825,nominal_source_interval_seconds=[0,720],sampling_rate_fps=1,retained_samples=len(overview),grid_count=len(list(grid.glob('grid_*.jpg'))),inspection_status='pending_visual_inspection',original_video_reads=0,card_identity_use=False,source_provenance=str(old/'evidence/PREPROCESS_LOG.md'),timestamp_limit='Prior source-relative manifest/overlay validated in preprocessing; current worker does not measure actual framePTS',limits=['One-second sampling can miss subsecond panels or inputs; no every-instant absence claim.','Reduced locator images not used for hand card identity.']))
lines=(old/'REVIEW.md').read_text(encoding='utf-8').splitlines();turns=[]
for i,line in enumerate(lines):
 if re.match(r'\| \d+ —',line):
  parts=line.split('|');t=int(re.match(r'\s*(\d+)',parts[1]).group(1));turns.append(dict(turn_number=t,accepted_source_line=i+1,verbatim_accepted_section=line,basis='inherited_accepted_review_not_new_visual_observation',actions=parts[3].strip(),exit_state=parts[4].strip()))
save('INHERITED_TURNS.json',dict(source='20260908_022627000_iOS.MP4',accepted_review=str(old/'REVIEW.md'),rows=turns,accepted_status='Reviewed; latest completion event supersedes stale prosepending status'))
save('SOURCE_REFERENCE.json',dict(schema='retrospective-source-reference-v1',source_video='20260908_022627000_iOS.MP4',sha256=sha,bytes=1351891106,duration_seconds=721.046825,native_dimensions=[1170,2532],current_path=r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Reviewed\20260908_022627000_iOS.MP4',prior_source_json=str(old/'SOURCE.json'),prior_manifest=str(old/'evidence/EVIDENCE_MANIFEST.csv'),prior_preprocess_source_binding=str(old/'evidence/PREPROCESS_LOG.md'),main_review_status='Reviewed',latest_completion_event='Review_Log/events/2026-09-22T171311.332302_0000_b3d74b7e-650d-47de-8784-0d479ea13715.json',verified_post_move_receipt=str(old/'MOVE_RECEIPT.20260908_022627000_iOS.MP4.json'),current_original_hash_reads=0,accepted_outcome='Owner loss; visible0-3; opponent cumulative awards4 (+1,+1,+2); no result splash recorded'))
print('Native',len(native),'overview',len(overview),'manifest',len(rows),'dimensions',dimensions,'turns',len(turns))
