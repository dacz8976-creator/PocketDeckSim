"""Produce a single reduced event locator per packet; no factual acceptance."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageDraw

B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('packet');a=p.parse_args();P=Path(a.packet).resolve();assert P.parent==B
s=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'));out=P/'locator_scan';assert not out.exists() or not list(out.rglob('*.jpg')),'Do not repeat the source locator decode.'
frames=out/'frames';frames.mkdir(parents=True,exist_ok=True);ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','2','-i',s['source_path_at_review'],'-vf','fps=1,scale=234:506','-q:v','3',str(frames/'%06d.jpg')],check=True)
paths=sorted(frames.glob('*.jpg'));grids=[]
for start in range(0,len(paths),20):
 grid=Image.new('RGB',(1170,2104),'white');draw=ImageDraw.Draw(grid)
 for slot,path in enumerate(paths[start:start+20]):
  x=slot%5*234;y=slot//5*526;draw.text((x+3,y+3),f'nominal {start+slot}s',fill='black')
  with Image.open(path)as im:grid.paste(im,(x,y+20))
 gp=out/f'grid_{start:03d}_{min(start+19,len(paths)-1):03d}.jpg';grid.save(gp,quality=90);grids.append(str(gp))
data={'source':s['video_basename'],'source_sha256':s['sha256'],'created_utc':datetime.now(timezone.utc).isoformat(),'decode_passes':1,'sampling_rate_fps':1,'dimensions':[234,506],'samples':len(paths),'grids':grids,'status':'preprocessed_not_visually_reviewed','timestamp_basis':'Nominal fps=1 indices; not measured source PTS. Reduced locators cannot replace native hand/identity evidence and may miss subsecond inputs.','sample_files':[{'path':str(p),'nominal_source_second':i,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for i,p in enumerate(paths)]}
(P/'LOCATOR_PREPROCESSING.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps({'source':s['video_basename'],'samples':len(paths),'grids':len(grids),'decode_passes':1}))
