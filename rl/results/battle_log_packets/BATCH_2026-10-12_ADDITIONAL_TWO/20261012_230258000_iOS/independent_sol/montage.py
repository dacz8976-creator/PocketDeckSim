from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).resolve().parent
times=[float(s) for s in sys.argv[2:]]
kind=sys.argv[1]
for k in range(0,len(times),12):
    ts=times[k:k+12]
    cw,ch=(585,330) if kind=='hand' else (390,870)
    out=Image.new('RGB',(cw*4,ch*3),'white');d=ImageDraw.Draw(out)
    for j,t in enumerate(ts):
        f=p.parent/'turn_evidence'/f't{t:07.2f}.jpg'
        if not f.exists():f=p.parent/'overview'/f't{t:07.2f}.jpg'
        im=Image.open(f)
        if kind=='hand': im=im.crop((0,int(im.height*.79),im.width,im.height))
        im.thumbnail((cw,ch-25))
        x=j%4*cw;y=j//4*ch
        out.paste(im,(x,y+25));d.text((x+3,y+4),str(t),fill='black')
    out.save(p/f'{kind}_{times[0]:07.2f}_{k//12:02}.jpg',quality=95)
