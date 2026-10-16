from pathlib import Path
import subprocess,sys
from PIL import Image,ImageDraw
P=Path(__file__).parent
FF=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
SRC=P.parents[2]/'20261015_015320000_iOS.MP4'
E=P/'evidence'; E.mkdir(exist_ok=True)
times=[float(x) for x in sys.argv[1].split(',')]
for t in times:
    out=E/f't{t:07.2f}.jpg'
    if not out.exists():
        subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','3','-threads','2',str(out)],check=True)
cols=6; w=240; h=540
sheet=Image.new('RGB',(cols*w,((len(times)+cols-1)//cols)*h),'white')
d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    im=Image.open(E/f't{t:07.2f}.jpg'); im.thumbnail((w,h-24))
    x=i%cols*w;y=i//cols*h
    sheet.paste(im,(x,y+24)); d.text((x+6,y+4),f'{t:.2f}s',fill='black')
out=P/f'sheet_{times[0]:07.2f}_{times[-1]:07.2f}.jpg';sheet.save(out,quality=88)
print(out)
