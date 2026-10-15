import sys
from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).parent
times=[float(v) for v in sys.argv[2:]]
s=Image.new('RGB',(1170,870*((len(times)+2)//3)),'white')
d=ImageDraw.Draw(s)
for i,t in enumerate(times):
    x,y=i%3*390,i//3*870
    d.text((x+4,y+5),f'Native {t:.2f}s',fill='black')
    im=Image.open(p/'native'/f't{t:07.2f}.jpg')
    im.thumbnail((390,844))
    s.paste(im,(x,y+26))
s.save(p/sys.argv[1],quality=90)
