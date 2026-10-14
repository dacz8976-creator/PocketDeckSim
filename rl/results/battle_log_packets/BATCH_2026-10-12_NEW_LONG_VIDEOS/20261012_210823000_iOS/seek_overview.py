from pathlib import Path
from PIL import Image, ImageDraw
import subprocess
p=Path(__file__).parent
out=p/'seek_overview'; out.mkdir(exist_ok=True)
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
video=p.parents[2]/'20261012_210823000_iOS.MP4'
times=list(range(0,440,3))
for t in times:
 f=out/f't{t:07.2f}.jpg'
 subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=390:-1','-q:v','3','-y',str(f)],check=True)
for i in range(0,len(times),12):
 sheet=Image.new('RGB',(390*4,(844+24)*3),'white'); d=ImageDraw.Draw(sheet)
 for k,t in enumerate(times[i:i+12]):
  x=k%4*390; y=k//4*868; d.text((x+4,y+4),f'{t}s',fill='black')
  with Image.open(out/f't{t:07.2f}.jpg') as im: sheet.paste(im,(x,y+24))
 sheet.save(out/f'sheet_{i//12+1:02d}.jpg',quality=88)
 print(i//12+1,flush=True)
