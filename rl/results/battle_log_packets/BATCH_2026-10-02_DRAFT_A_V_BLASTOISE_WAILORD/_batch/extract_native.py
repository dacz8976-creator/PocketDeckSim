"""One shared source-bound native extractor with measured PTS and lossless crops."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from PIL import Image

B = Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('packet');parser.add_argument('times',nargs='+',type=float);parser.add_argument('--independent-folder');args=parser.parse_args()
base=Path(args.packet).resolve();assert base.parent==B and base.is_dir()
source=json.loads((base/'SOURCE.json').read_text(encoding='utf-8-sig'))
P=base
if args.independent_folder:
 assert re.fullmatch(r'independent_[A-Za-z0-9_-]+',args.independent_folder),'Expected a unique independent evidence folder name.'
 P=base/args.independent_folder;P.mkdir(exist_ok=True)
out=P/'turn_evidence';out.mkdir(exist_ok=True);logs=P/'decode_logs';logs.mkdir(exist_ok=True)
manifest_path=P/'EXTRACTION_MANIFEST.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))if manifest_path.exists()else[]
plan=base/'EXTRACTION_PLAN.json';cap=json.loads(plan.read_text(encoding='utf-8'))['cap'] if plan.exists() else 160
assert all(abs(t-round(t,2))<1e-8 for t in args.times), 'Requested timestamps must use at most two decimal places to preserve unique filenames.'
new=set(args.times)-{r['requested_source_seconds']for r in manifest}
other_manifests=[base/'EXTRACTION_MANIFEST.json',*base.glob('independent_*/EXTRACTION_MANIFEST.json')]
other_count=sum(len(json.loads(mp.read_text(encoding='utf-8-sig')))for mp in other_manifests if mp!=manifest_path and mp.exists())
assert other_count+len(manifest)+len(new)<=cap,'Native extraction cap reached; notify root with remaining required captures.'
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for t in sorted(new):
 assert 0<=t<source['duration_seconds']
 path=out/f't{t:07.2f}.jpg';assert not path.exists(),'Unregistered existing image: reconcile before overwriting.'
 proc=subprocess.run([ff,'-hide_banner','-loglevel','info','-threads','2','-copyts','-ss',str(t),'-i',source['source_path_at_review'],'-vf','showinfo','-frames:v','1','-q:v','2','-y',str(path)],check=True,capture_output=True,text=True)
 log=logs/f't{t:07.2f}.txt';log.write_text(proc.stderr,encoding='utf-8')
 match=re.findall(r'\bn:\s*0\s+pts:\s*(-?\d+)\s+pts_time:([\d.-]+)',proc.stderr);pts=float(match[0][1])if match else None
 with Image.open(path)as im:
  w,h=im.size;bounds={'bottom':[0,int(h*.8),w,h],'top':[0,0,w,min(550,h)]}
  crops={}
  for role,bound in bounds.items():
   cp=out/f't{t:07.2f}_{role}.png';im.crop(bound).save(cp)
   crops[role+'_crop']={'path':str(cp),'pixel_bounds_x0_y0_x1_y1':bound,'sha256':sha(cp),'parent_sha256':sha(path),'lossless':True}
 evidence_id=(args.independent_folder+':' if args.independent_folder else '')+f'F{t:07.2f}'
 manifest.append({'evidence_id':evidence_id,'source_video':source['video_basename'],'source_sha256':source['sha256'],'requested_source_seconds':t,'actual_frame_seconds_if_measured':pts,'timestamp_basis':'FFmpeg -copyts showinfo first selected decoded frame PTS; source start recorded in decode log','full_frame_path':str(path),'full_frame_sha256':sha(path),'native_dimensions':{'width':w,'height':h},'decode_log':str(log),**crops})
 manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(json.dumps({'requested':t,'actual_pts':pts,'native_frames_total':len(manifest)}),flush=True)
