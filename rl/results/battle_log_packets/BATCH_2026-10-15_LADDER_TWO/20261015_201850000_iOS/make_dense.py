from pathlib import Path
from PIL import Image,ImageDraw
import subprocess
p=Path(__file__).parent
out=p/'dense';out.mkdir(exist_ok=True)
for i in range(161):
 t=min((i+.5)*5,801.5);dest=out/f't{t:06.1f}.jpg'
 if not dest.exists():
  if i%3==1:
   src=p/'overview'/f'overview_{i//3+1:04d}.jpg'
   if src.exists():
    with Image.open(src) as im:im.resize((390,844)).save(dest,quality=90)
   else:continue
  else:
   subprocess.run(['C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe','-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i','20261015_201850000_iOS.MP4','-frames:v','1','-an','-vf','scale=390:-1','-q:v','3','-threads','1',str(dest)],check=True)
 if i%6==5 or i==160:
  start=i//6*6;files=[out/f't{min((j+.5)*5,801.5):06.1f}.jpg' for j in range(start,i+1)]
  sheet=Image.new('RGB',(1170,1748),'white');d=ImageDraw.Draw(sheet)
  for j,f in enumerate(files):
   if not f.exists():continue
   x=j%3*390;y=j//3*874;d.text((x+4,y+5),f'{min((start+j+.5)*5,801.5):.1f}s',fill='black')
   with Image.open(f) as im:sheet.paste(im,(x,y+30))
  sheet.save(out/f'sheet_{i//6+1:02d}.jpg',quality=90)
  print(out/f'sheet_{i//6+1:02d}.jpg',flush=True)
