from pathlib import Path
from PIL import Image, ImageDraw
import subprocess
p=Path(__file__).parent
root=p.parents[2]
video=root/'20261012_004435000_iOS.MP4'
out=p/'overview_seek'; out.mkdir(exist_ok=True)
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
for t in range(0,464,4):
 f=out/f't{t:03d}.jpg'
 if not f.exists() or f.stat().st_size==0: subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=390:-1','-q:v','3','-y',str(f)],check=True)
paths=sorted(out.glob('t*.jpg'))
for start in range(0,len(paths),9):
 sheet=Image.new('RGB',(1170,2610),'white'); draw=ImageDraw.Draw(sheet)
 for slot,f in enumerate(paths[start:start+9]):
  x=(slot%3)*390;y=(slot//3)*870
  draw.text((x+4,y+4),f.stem+' sec',fill='black')
  with Image.open(f) as im: sheet.paste(im,(x,y+24))
 sheet.save(out/f'sheet_{start//9+1:02d}.jpg',quality=90)
print('done',len(paths))
