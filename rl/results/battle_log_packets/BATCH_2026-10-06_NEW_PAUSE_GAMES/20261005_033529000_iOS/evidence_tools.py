import argparse, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parent
SRC=P.parents[2]/'20261005_033529000_iOS.MP4'
FF=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
a=argparse.ArgumentParser();a.add_argument('--times',nargs='*',type=float);a.add_argument('--sheet',nargs='*',type=float);a.add_argument('--label',default='detail');v=a.parse_args()
for t in v.times or []:
    f=P/'turn_evidence'/f't{t:07.2f}.jpg'
    if not f.exists(): subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','2','-y',str(f)],check=True)
if v.sheet:
    out=P/'native_sheets';out.mkdir(exist_ok=True)
    for k in range(0,len(v.sheet),9):
        im=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(im)
        for i,t in enumerate(v.sheet[k:k+9]):
            f=P/'turn_evidence'/f't{t:07.2f}.jpg'
            with Image.open(f) as x: im.paste(x.resize((390,844)),((i%3)*390,(i//3)*870+26))
            d.text(((i%3)*390+4,(i//3)*870+5),str(t)+'s',fill='black')
        im.save(out/f'{v.label}_{k//9:02d}.jpg')
