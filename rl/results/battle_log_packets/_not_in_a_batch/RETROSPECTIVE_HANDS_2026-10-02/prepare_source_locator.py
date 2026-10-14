"""Cached-source preprocessing only, not visual review or factual acceptance."""
import json,subprocess,hashlib,argparse
from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone

B=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('stem',choices=['20260929_020916000','20260929_002539000','20260928_200654000','20260909_023151000'])
args=parser.parse_args()
P=B/args.stem
receipt=json.loads((P/'ROOT_SOURCE_VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert receipt['status']=='verified_sha256_match'
out=P/'locator_scan'
assert not out.exists(), 'Do not repeat decode automatically'
frames=out/'frames';frames.mkdir(parents=True)
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','2','-i',receipt['current_path'],
 '-vf','fps=1,scale=234:506','-q:v','3',str(frames/'%06d.jpg')],check=True)
paths=sorted(frames.glob('*.jpg'))
grids=[]
for start in range(0,len(paths),20):
    grid=Image.new('RGB',(234*5,526*4),'white');draw=ImageDraw.Draw(grid)
    for slot,path in enumerate(paths[start:start+20]):
        x=(slot%5)*234;y=(slot//5)*526
        draw.text((x+4,y+3),f'nominal {start+slot}s',fill='black')
        with Image.open(path) as im:grid.paste(im,(x,y+20))
    gp=out/f'grid_{start:03d}_{min(start+19,len(paths)-1):03d}.jpg'
    grid.save(gp,quality=90);grids.append(str(gp))
data={'schema':'source-panel-locator-preprocessing-v1','created_utc':datetime.now(timezone.utc).isoformat(),
 'source':receipt['source'],'source_sha256':receipt['actual_sha256'],'source_receipt':str(P/'ROOT_SOURCE_VERIFICATION.json'),
 'sampling_rate_fps':1,'dimensions':[234,506],'samples':len(paths),'grids':grids,'decode_passes':1,
 'status':'preprocessed_not_visually_reviewed','source_video_cache_read':True,'duplicate_sha_reads':0,
 'timestamp_basis':'Nominal fps=1 output indices; actual source PTS unmeasured. Reduced locator images cannot substitute for native hand/card transcription.',
 'sample_files':[{'path':str(p),'nominal_source_second':i,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in enumerate(paths)]}
(P/'LOCATOR_PREPROCESSING.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in data.items() if k not in ['sample_files','grids']}))
