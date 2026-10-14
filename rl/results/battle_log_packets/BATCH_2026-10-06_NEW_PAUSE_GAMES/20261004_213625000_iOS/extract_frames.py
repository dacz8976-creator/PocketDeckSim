import subprocess,sys,json
from pathlib import Path
from PIL import Image,ImageDraw
from concurrent.futures import ThreadPoolExecutor
p=Path(__file__).parent; v=p.parents[2]/'20261004_213625000_iOS.MP4'; out=p/'turn_evidence';out.mkdir(exist_ok=True)
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
times=[float(x) for x in sys.argv[1:]]
def f(t):
 fn=out/f't{t:07.2f}.png'
 if not fn.exists():subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(v),'-frames:v','1','-y',str(fn)],check=True)
 im=Image.open(fn);w,h=im.size; im.crop((0,int(h*.8),w,h)).save(out/f't{t:07.2f}_bottom.png'); im.crop((0,0,w,int(h*.24))).save(out/f't{t:07.2f}_top.png');return fn
with ThreadPoolExecutor(max_workers=2) as pool:paths=list(pool.map(f,times))
for start in range(0,len(paths),12):
 s=Image.new('RGB',(1200,4*675),'white');d=ImageDraw.Draw(s)
 for j,fn in enumerate(paths[start:start+12]):
  im=Image.open(fn);im.thumbnail((300,649));x=(j%4)*300;y=(j//4)*675;s.paste(im,(x,y+26));d.text((x+3,y+3),fn.stem,fill='black')
 name=p/f'overview_{times[0]:.2f}_{start//12}.jpg';s.save(name,quality=85);print(name)
