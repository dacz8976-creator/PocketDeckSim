from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys,json
p=Path(__file__).resolve().parent
ff='C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
src=p.parents[2]/'20261013_014423000_iOS.MP4'
out=p/'turn_evidence';out.mkdir(exist_ok=True)
times=[float(x) for x in sys.argv[1:]]
for t in times:
 f=out/f't{t:07.2f}.jpg'
 if not f.exists():subprocess.run([ff,'-v','error','-threads','1','-ss',str(t),'-i',str(src),'-frames:v','1','-q:v','2',str(f)],check=True)
 with Image.open(f) as im:
  im.crop((0,2025,1170,2532)).save(out/f'{f.stem}_bottom.jpg',quality=95)
  im.crop((0,0,1170,880)).save(out/f'{f.stem}_top.jpg',quality=95)
for k in range(0,len(times),12):
 s=Image.new('RGB',(1170,2616),'white');d=ImageDraw.Draw(s)
 for j,t in enumerate(times[k:k+12]):
  x=j%4*292;y=j//4*872
  with Image.open(out/f't{t:07.2f}.jpg') as im:s.paste(im.resize((292,632)),(x,y+24))
  d.text((x+4,y+4),str(t),fill='black')
 s.save(p/f'selected_{times[k]:07.2f}.jpg',quality=93)
print('extracted',times)
