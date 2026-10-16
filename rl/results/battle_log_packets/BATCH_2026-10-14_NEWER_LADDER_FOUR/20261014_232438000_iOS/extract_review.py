from pathlib import Path
import subprocess, sys
from PIL import Image, ImageOps, ImageDraw
P=Path(__file__).parent
S=P.parents[2]/'20261014_232438000_iOS.MP4'
FF=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
E=P/'evidence'; E.mkdir(exist_ok=True)
def capture(t):
    f=E/f't{t:07.2f}.jpg'
    if not f.exists(): subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(S),'-frames:v','1','-q:v','2',str(f)],check=True)
    return f
def sheet(times,name,w=293,cols=4):
    h=round(w*2532/1170); rows=(len(times)+cols-1)//cols
    out=Image.new('RGB',(cols*w,rows*(h+25)),'#202020'); d=ImageDraw.Draw(out)
    for i,t in enumerate(times):
        f=capture(t); im=Image.open(f); im.thumbnail((w,h)); x=(i%cols)*w; y=(i//cols)*(h+25)
        out.paste(im,(x,y+25)); d.text((x+5,y+4),f'{t:.2f}s',fill='white')
    out.save(P/name)
if sys.argv[1]=='overview':
    for n,start in enumerate(range(0,354,64)): sheet(list(range(start,min(start+64,355),4)),f'overview_{n}.jpg')
else:
    times=[float(x) for x in sys.argv[2:]]
    sheet(times,sys.argv[1],390,3)
