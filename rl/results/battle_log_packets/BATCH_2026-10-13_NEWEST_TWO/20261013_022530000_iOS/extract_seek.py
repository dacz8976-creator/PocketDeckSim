import subprocess,sys,json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
v=str(p.parents[2]/'20261013_022530000_iOS.MP4')
mode=sys.argv[1]; times=[float(x) for x in sys.argv[2:]]
folder=p/('overview' if mode=='grid' else 'turn_evidence');folder.mkdir(exist_ok=True)
for t in times:
 f=folder/f't{t:07.2f}.jpg'
 if not f.exists():
  cmd=[ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',v,'-frames:v','1']
  if mode=='grid':cmd+=['-vf','scale=390:-1']
  subprocess.run(cmd+['-q:v','2','-y',str(f)],check=True)
 if mode!='grid':
  im=Image.open(f); w,h=im.size
  im.crop((0,int(h*.8),w,h)).save(folder/(f.stem+'_bottom.jpg'),quality=95)
  im.crop((0,0,w,int(h*.31))).save(folder/(f.stem+'_top.jpg'),quality=95)
if mode=='grid':
 for start in range(0,len(times),12):
  ts=times[start:start+12];sheet=Image.new('RGB',(390*4,870*3),'white');d=ImageDraw.Draw(sheet)
  for i,t in enumerate(ts):
   im=Image.open(folder/f't{t:07.2f}.jpg');x=i%4*390;y=i//4*870;sheet.paste(im,(x,y+24));d.text((x+4,y+3),str(t),fill='black')
  sheet.save(folder/f'grid_{times[0]:07.2f}_{start//12:02}.jpg',quality=90)
print('Done',mode,len(times))

