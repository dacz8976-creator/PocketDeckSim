from pathlib import Path
import subprocess, sys
from PIL import Image, ImageDraw
P=Path(__file__).parent
V=P.parents[2]/'20261014_142546000_iOS.MP4'
FF='C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
if sys.argv[1]=='native':
    d=P/'native'; d.mkdir(exist_ok=True)
    for t in map(float,sys.argv[2:]):
        out=d/f't{t:06.1f}.jpg'
        subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(V),'-frames:v','1','-q:v','2','-y',str(out)],check=True)
        print(out.name,flush=True)
elif sys.argv[1] in ('nsheets','subset'):
    fs=sorted((P/'native').glob('t*.jpg')) if sys.argv[1]=='nsheets' else [P/'native'/f't{float(t):06.1f}.jpg' for t in sys.argv[2:]]
    for start in range(0,len(fs),6):
        sheet=Image.new('RGB',(1170,1750),'white'); dr=ImageDraw.Draw(sheet)
        for i,f in enumerate(fs[start:start+6]):
            x=(i%3)*390; y=(i//3)*875
            dr.text((x+5,y+5),f.stem,fill='black')
            im=Image.open(f); im.thumbnail((390,844))
            sheet.paste(im,(x,y+30))
        sheet.save(P/'native'/f'{sys.argv[1]}_{start//6+1:02d}.jpg',quality=90)
else:
    fs=sorted((P/'coarse').glob('f*.jpg'))
    for start in range(0,len(fs),12):
        sheet=Image.new('RGB',(1200,2046),'white'); dr=ImageDraw.Draw(sheet)
        for i,f in enumerate(fs[start:start+12]):
            x=(i%4)*300; y=(i//4)*682
            # fps filter chooses approximately interval-center source frames.
            dr.text((x+5,y+5),f'~{(start+i)*10+5}s',fill='black')
            sheet.paste(Image.open(f),(x,y+30))
        sheet.save(P/'coarse'/f'contact_{start//12+1:02d}.jpg',quality=85)
