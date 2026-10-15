import subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS');f=p/'dense';f.mkdir(exist_ok=True)
ff=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
for t in range(26,801,2):
 dest=f/f't{t:07.2f}.jpg';old=p/'overview'/dest.name
 if old.exists():continue
 if not dest.exists():subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(min(t,800.5)),'-i','20261012_203719000_iOS.MP4','-frames:v','1','-q:v','3','-y',str(dest)],check=True)
 if t%50==0:print(t,flush=True)
paths=sorted(list(f.glob('t*.jpg'))+list((p/'overview').glob('t*.jpg')))
paths=[q for q in paths if float(q.stem[1:])>=26]
for st in range(0,len(paths),18):
 sheet=Image.new('RGB',(390*6,870*3),'white');d=ImageDraw.Draw(sheet)
 for i,path in enumerate(paths[st:st+18]):
  x=i%6*390;y=i//6*870;d.text((x,y),path.stem,fill='black')
  with Image.open(path) as im:sheet.paste(im.resize((390,844)),(x,y+26))
 sheet.save(f/f'sheet{st//18:02}.jpg')
