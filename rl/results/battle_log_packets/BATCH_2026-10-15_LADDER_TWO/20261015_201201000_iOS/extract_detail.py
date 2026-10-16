import subprocess
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent
src=P.parents[2]/'20261015_201201000_iOS.MP4'
out=P/'detail';out.mkdir(exist_ok=True)
frames=[]
for t in range(0,383,4):
    f=out/f't{t:03}.jpg'
    if not f.exists():
        subprocess.run(['C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe','-hide_banner','-loglevel','error','-threads','1','-ss',str(min(t,382.2)),'-i',str(src),'-frames:v','1','-vf','scale=390:-1','-q:v','3','-threads','1',str(f)],check=True)
    frames.append((t,f))
for start in range(0,len(frames),6):
    sheet=Image.new('RGB',(1170,1752),'white');d=ImageDraw.Draw(sheet)
    for j,(t,f) in enumerate(frames[start:start+6]):
        x=j%3*390;y=j//3*876
        d.text((x+4,y+3),f'{t}s',fill='black')
        with Image.open(f) as im:sheet.paste(im,(x,y+24))
    sheet.save(out/f'sheet_{start//6+1:02}.jpg',quality=90)
print('done',flush=True)
