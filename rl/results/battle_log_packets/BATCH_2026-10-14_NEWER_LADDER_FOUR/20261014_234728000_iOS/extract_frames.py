from pathlib import Path
import subprocess, sys
from PIL import Image, ImageOps, ImageDraw
P=Path(__file__).parent
S=P.parents[2]/'20261014_234728000_iOS.MP4'
F=Path('C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe')
E=P/'evidence';E.mkdir(exist_ok=True)
times=[float(x) for x in sys.argv[1].split(',')]
for t in times:
    f=E/f'f_{t:07.2f}.jpg'
    if not f.exists():
        subprocess.run([str(F),'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(S),'-frames:v','1','-q:v','2','-y',str(f)],check=True)
    print(t,flush=True)
for j in range(0,len(times),16):
    chunk=times[j:j+16];out=Image.new('RGB',(280*4,640*4),'#eeeeee')
    d=ImageDraw.Draw(out)
    for i,t in enumerate(chunk):
        im=Image.open(E/f'f_{t:07.2f}.jpg');im.thumbnail((280,605))
        x=(i%4)*280;y=(i//4)*640
        out.paste(im,(x,y+25));d.text((x+8,y+5),f'{t:.2f}s',fill='black')
    out.save(E/f'sheet_{times[0]:07.2f}_{j//16}.jpg',quality=90)
