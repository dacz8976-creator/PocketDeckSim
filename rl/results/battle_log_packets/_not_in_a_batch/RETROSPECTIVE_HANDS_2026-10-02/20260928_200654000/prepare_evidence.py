import json,re,datetime
from pathlib import Path
from PIL import Image
B=Path(__file__).parent;old=B.parents[1]/'20260928_200654000_iOS_sol'
receipt=json.loads((B/'ROOT_SOURCE_VERIFICATION.json').read_text())
assert receipt['status']=='verified_sha256_match'
source=json.loads((old/'SOURCE.json').read_text())
assert source['source_sha256']==receipt['actual_sha256']
a=json.loads((B/'ASSIGNMENT.json').read_text());a['registered_utc']='2026-10-02T22:18:38+00:00';a['timestamp_note']='Initial future timestamp corrected to actual clock before first visual inspection.';(B/'ASSIGNMENT.json').write_text(json.dumps(a,indent=2))
c=B/'reused_crops';c.mkdir(exist_ok=True)
inventory=[];native=[]
for p in sorted(old.rglob('*.jpg')):
 with Image.open(p) as im:
  w,h=im.size
  m=re.search(r't(\d+(?:\.\d+)?)',p.stem)
  t=float(m[1]) if m else None
  inventory.append(dict(path=str(p.resolve()),dimensions=[w,h],bytes=p.stat().st_size,requested_source_seconds=t))
  if (w,h)!=(1170,2532):continue
  eid='R_'+p.parent.name+'_'+p.stem
  im.crop((0,2025,1170,2532)).save(c/(eid+'_hand.jpg'),quality=95)
  im.crop((0,0,1170,550)).save(c/(eid+'_top.jpg'),quality=95)
  native.append(dict(evidence_id=eid,source_video=receipt['source'],source_sha256=receipt['actual_sha256'],full_frame_path=str(p.resolve()),requested_source_seconds=t,actual_frame_seconds_if_measured=None,timestamp_basis='Prior source-relative filename time; decodedPTS not provided. Bound by exact old SOURCE SHA and current matching root receipt.',native_dimensions={'width':w,'height':h},bottom_crop={'path':str((c/(eid+'_hand.jpg')).resolve()),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},top_crop={'path':str((c/(eid+'_top.jpg')).resolve()),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,550]},source_binding=str((old/'SOURCE.json').resolve())))
(B/'REUSED_MANIFEST.json').write_text(json.dumps(native,indent=2))
(B/'EVIDENCE_INVENTORY.json').write_text(json.dumps({'old_packet':str(old.resolve()),'native_frames':len(native),'images':inventory},indent=2))
lines=(old/'REVIEW.md').read_text(encoding='utf-8').splitlines();rows=[]
for i,line in enumerate(lines,1):
 m=re.match(r'\| (\d+) (?:opponent|owner)',line)
 if m:rows.append({'turn_number':int(m[1]),'accepted_source_line':i,'verbatim_accepted_row':line,'basis':'inherited_accepted_review_not_new_visual_observation'})
(B/'INHERITED_TURNS.json').write_text(json.dumps({'source':receipt['source'],'accepted_review':str((old/'REVIEW.md').resolve()),'rows':rows},indent=2))
(B/'SOURCE_REFERENCE.json').write_text(json.dumps({'source_video':receipt['source'],'sha256':receipt['actual_sha256'],'bytes':receipt['actual_bytes'],'duration_seconds':source['duration_seconds'],'native_dimensions':source['video_dimensions'],'current_path':receipt['current_path'],'verification_status':receipt['status'],'source_verification_receipt':str((B/'ROOT_SOURCE_VERIFICATION.json').resolve()),'old_packet':str(old.resolve()),'old_source_json':str((old/'SOURCE.json').resolve()),'accepted_outcome':'owner loss2-3 inherited; no new outcome review','main_review_status':'Reviewed','worker_identity_hash_reads':0},indent=2))
print('native',len(native),'oldtotal',len(inventory),'turnrows',len(rows))
print('native time/path',[(x['requested_source_seconds'],Path(x['full_frame_path']).parent.name) for x in native])
