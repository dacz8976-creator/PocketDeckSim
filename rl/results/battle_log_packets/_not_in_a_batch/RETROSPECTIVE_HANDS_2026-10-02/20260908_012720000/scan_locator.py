import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
out=B/'locator_scan';out.mkdir(exist_ok=True)
receipt=json.loads((B/'ROOT_SOURCE_VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert receipt['status']=='verified_sha256_match'
cmd=[r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe','-hide_banner','-loglevel','error','-i',receipt['current_path'],'-vf','fps=1,scale=234:506','-q:v','6',str(out/'sample_%04d.jpg')]
subprocess.run(cmd,check=True)
frames=sorted(out.glob('sample_*.jpg'))
for start in range(0,len(frames),20):
 sheet=Image.new('RGB',(936,2650),'white');d=ImageDraw.Draw(sheet)
 for j,p in enumerate(frames[start:start+20]):
  x=(j%4)*234;y=(j//4)*530
  d.text((x+4,y+3),f'~{start+j}s / sample{start+j+1}',fill='black')
  sheet.paste(Image.open(p),(x,y+24))
 sheet.save(out/f'grid_{start:03d}_{min(start+19,len(frames)-1):03d}.jpg',quality=90)
(B/'LOCATOR_SCAN.json').write_text(json.dumps(dict(schema='source-panel-locator-v1',source=receipt['current_path'],source_sha256=receipt.get('actual_sha256'),sampling_rate_fps=1,sampling_interval_seconds=1,source_duration_seconds=282.628,retained_reduced_samples=len(frames),dimensions=[234,506],grids=[str(p) for p in sorted(out.glob('grid_*.jpg'))],purpose='Locate panels/prompts only; no card identity transcription',timestamp_basis='Nominal one-second sample ordinals from ffmpeg fps filter; actual decoded PTS not measured; target event native extraction requires separate requested time',inspection_status='awaiting_visual_inspection',limits=['One-second sampling can miss shorter events; no every-instant claim.','Reduced locators cannot establish card identities.']),indent=2),encoding='utf-8')
print('Reduced locator scan:',len(frames),'samples;',len(list(out.glob('grid_*.jpg'))),'grids')
