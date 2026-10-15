import json,sys,subprocess,re
from pathlib import Path
from PIL import Image
B=Path(__file__).parent
receipt=json.loads((B/'SOURCE_VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert receipt['status']=='verified_sha256_match'
out=B/'turn_evidence';out.mkdir(exist_ok=True)
logdir=B/'decode_logs';logdir.mkdir(exist_ok=True)
manifest=json.loads((B/'EXTRACTION_MANIFEST.json').read_text()) if (B/'EXTRACTION_MANIFEST.json').exists() else []
times=[float(x) for x in sys.argv[1:]]
cap=json.loads((B/'EXTRACTION_PLAN.json').read_text())['new_native_cap']
assert len(manifest)+sum(not (out/f't{t:07.2f}.jpg').exists() for t in times)<=cap
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
for t in times:
 p=out/f't{t:07.2f}.jpg'
 if p.exists():continue
 proc=subprocess.run([ff,'-hide_banner','-loglevel','info','-threads','2','-copyts','-ss',str(t),'-i',receipt['current_path'],'-vf','showinfo','-frames:v','1','-q:v','2','-y',str(p)],capture_output=True,text=True,check=True)
 (logdir/f't{t:07.2f}.txt').write_text(proc.stderr,encoding='utf-8')
 matches=re.findall(r'\bn:\s*0\s+pts:\s*(-?\d+)\s+pts_time:([\d.-]+)',proc.stderr)
 decoded=float(matches[0][1]) if matches else None
 with Image.open(p) as im:
  w,h=im.size;bottom=[0,int(h*.8),w,h];top=[0,0,w,550]
  im.crop(bottom).save(out/f'b{t:07.2f}.jpg',quality=95)
  im.crop(top).save(out/f'p{t:07.2f}.jpg',quality=95)
 manifest.append(dict(evidence_id=f'F{t:07.2f}',source_video=receipt['source'],source_sha256=receipt['actual_sha256'],requested_source_seconds=t,actual_frame_seconds_if_measured=decoded,timestamp_basis='FFmpeg -copyts showinfo first selected decoded framePTS; source stream start recorded in decode log',full_frame_path=str(p.resolve()),native_dimensions=dict(width=w,height=h),bottom_crop=dict(path=str((out/f'b{t:07.2f}.jpg').resolve()),pixel_bounds_x0_y0_x1_y1=bottom),top_crop=dict(path=str((out/f'p{t:07.2f}.jpg').resolve()),pixel_bounds_x0_y0_x1_y1=top),decode_log=str((logdir/f't{t:07.2f}.txt').resolve())))
 (B/'EXTRACTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(t,decoded,flush=True)
