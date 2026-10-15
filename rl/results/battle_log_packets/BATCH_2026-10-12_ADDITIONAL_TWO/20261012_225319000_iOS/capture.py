import subprocess,sys,json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
v=p.parents[2]/'20261012_225319000_iOS.MP4'
ff=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
out=p/'turn_evidence';out.mkdir(exist_ok=True)
times=[float(x) for x in sys.argv[1:]]
paths=[]
for t in times:
 f=out/f't{t:07.2f}.jpg'
 if not f.exists(): subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(v),'-frames:v','1','-q:v','2',str(f)],check=True)
 im=Image.open(f);im.crop((0,2025,1170,2532)).save(out/f'{f.stem}_bottom.jpg',quality=94);im.crop((0,0,1170,700)).save(out/f'{f.stem}_top.jpg',quality=94)
 paths.append(f)
for start in range(0,len(paths),8):
 sheet=Image.new('RGB',(390*4,844*2+50),'white');d=ImageDraw.Draw(sheet)
 for slot,f in enumerate(paths[start:start+8]):
  x=(slot%4)*390;y=(slot//4)*869;d.text((x+4,y+3),f.stem,fill='black');im=Image.open(f);im.thumbnail((390,844));sheet.paste(im,(x,y+25))
 sheet.save(out/f'grid_{times[0]:07.2f}_{start//8}.jpg',quality=90)
print('Captured',times)
