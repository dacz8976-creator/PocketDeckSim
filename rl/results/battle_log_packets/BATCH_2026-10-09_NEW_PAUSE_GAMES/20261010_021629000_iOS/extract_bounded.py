from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys,json
p=Path(__file__).parent
v=p.parents[2]/'20261010_021629000_iOS.MP4'
f=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
out=p/sys.argv[1];out.mkdir(exist_ok=True)
times=[float(x) for x in sys.argv[2:]]
for t in times:
 target=out/f't{t:07.2f}.jpg'
 if not target.exists():
  subprocess.run([f,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(v),'-frames:v','1','-vf','scale=390:-1','-q:v','3','-y',str(target)],check=True)
for n in range(0,len(times),9):
 sheet=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(sheet)
 for j,t in enumerate(times[n:n+9]):
  im=Image.open(out/f't{t:07.2f}.jpg');x=j%3*390;y=j//3*870
  sheet.paste(im,(x,y+26));d.text((x+5,y+5),str(t),fill='black')
 sheet.save(out/f'sheet_{n//9+1:02}.jpg',quality=92)
print('finished',len(times),'frames')
