import argparse, subprocess,json
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('times',nargs='+',type=float);p.add_argument('--sheet',default='target');a=p.parse_args()
root=Path(__file__).resolve().parent; out=root/'turn_evidence';out.mkdir(exist_ok=True)
video=root.parents[2]/'20261010_012303000_iOS.MP4'
for t in a.times:
 target=out/f't{t:07.2f}.jpg'
 if not target.exists():subprocess.run([r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe','-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2','-y',str(target)],check=True)
 with Image.open(target) as im:
  im.crop((0,2025,1170,2532)).save(out/f't{t:07.2f}_bottom.jpg',quality=95)
  im.crop((0,0,1170,620)).save(out/f't{t:07.2f}_top.jpg',quality=95)
for start in range(0,len(a.times),9):
 sheet=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(sheet)
 for j,t in enumerate(a.times[start:start+9]):
  x=j%3*390;y=j//3*870;d.text((x+5,y+5),str(t),fill='black')
  with Image.open(out/f't{t:07.2f}.jpg') as im:sheet.paste(im.resize((390,844)),(x,y+25))
 sheet.save(root/f'{a.sheet}_{start//9+1:02d}.jpg',quality=90)
print('Captured',len(a.times),'frames')
