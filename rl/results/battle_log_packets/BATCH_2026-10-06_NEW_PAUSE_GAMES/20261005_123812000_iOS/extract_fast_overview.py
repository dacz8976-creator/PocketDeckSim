from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
P=Path(r'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/20261005_123812000_iOS'); F=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
paths=[]
for t in range(0,337,3):
 p=P/'overview'/f'fast_{t:04}.jpg'
 if not p.exists(): subprocess.run([F,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i','20261005_123812000_iOS.MP4','-frames:v','1','-vf','scale=390:-1','-q:v','3','-y',str(p)],check=True)
 paths.append((t,p))
for i in range(0,len(paths),12):
 sheet=Image.new('RGB',(1560,2610),'white'); d=ImageDraw.Draw(sheet)
 for j,(t,p) in enumerate(paths[i:i+12]):
  x=j%4*390;y=j//4*870;d.text((x+4,y+2),str(t)+'s',fill='black');sheet.paste(Image.open(p),(x,y+26))
 sheet.save(P/'overview'/f'fast_sheet_{i//12+1:02}.jpg',quality=90)
