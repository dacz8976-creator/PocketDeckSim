from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent
mode=sys.argv[1];times=[float(t) for t in sys.argv[2:]]
ims=[]
for t in times:
    f=p/'turn_evidence'/f't{t:07.2f}.jpg'
    if not f.exists():f=p/'dense_native'/f't{t:07.2f}.jpg'
    if not f.exists():continue
    im=Image.open(f)
    if mode=='hand':im=im.crop((0,2050,1170,2532));im.thumbnail((585,241))
    elif mode=='center':im=im.crop((80,520,1090,1710));im.thumbnail((505,595))
    else:im.thumbnail((390,844))
    ims.append((t,im))
for i in range(0,len(ims),9):
    w,h=ims[0][1].size;s=Image.new('RGB',(w*3,(h+26)*3),'white');d=ImageDraw.Draw(s)
    for j,(t,im) in enumerate(ims[i:i+9]):
        x=j%3*w;y=j//3*(h+26);s.paste(im,(x,y+26));d.text((x+3,y+3),str(t),fill='black')
    s.save(p/f'{mode}_{i//9+1:02}.jpg',quality=92)
