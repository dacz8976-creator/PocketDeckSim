from pathlib import Path
from PIL import Image,ImageDraw
import sys
root=Path(__file__).parent
ts=[float(x) for x in sys.argv[1:]]
w=585;h=950
im=Image.new('RGB',(w*3,(h+25)*((len(ts)+2)//3)),'white')
d=ImageDraw.Draw(im)
for n,t in enumerate(ts):
 f=root/'native'/f't{t:07.2f}.jpg'
 if not f.exists():continue
 src=Image.open(f).crop((0,260,1170,2160)).resize((w,h))
 x=n%3*w;y=n//3*(h+25)
 d.text((x+3,y+3),f'{t:.2f}s',fill='black')
 im.paste(src,(x,y+25))
im.save(root/f'natives_{ts[0]:07.2f}.jpg',quality=92)
