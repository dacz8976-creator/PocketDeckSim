import subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS')
f=p/'overview';f.mkdir(exist_ok=True)
ff=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
for t in range(0,801,8):
 dest=f/f't{t:07.2f}.jpg'
 if not dest.exists():subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(min(t,800.5)),'-i','20261012_203719000_iOS.MP4','-frames:v','1','-q:v','3','-y',str(dest)],check=True)
paths=sorted(f.glob('t*.jpg'))
for st in range(0,len(paths),12):
 sheet=Image.new('RGB',(390*4,844*3+26*3),'white');d=ImageDraw.Draw(sheet)
 for i,path in enumerate(paths[st:st+12]):
  x=i%4*390;y=i//4*870
  d.text((x,y),path.stem,fill='black')
  with Image.open(path) as im:sheet.paste(im.resize((390,844)),(x,y+26))
 sheet.save(f/f'sheet{st//12:02}.jpg')
 print(st,flush=True)
