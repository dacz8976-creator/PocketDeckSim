from pathlib import Path
from PIL import Image, ImageDraw
import sys
p=Path(__file__).parent
times=sys.argv[2:]
files=[p/'turn_evidence'/f't{float(t):07.2f}.jpg' for t in times]
w=390; h=844
out=Image.new('RGB',(w*3,(h+26)*((len(files)+2)//3)),'white'); d=ImageDraw.Draw(out)
for i,f in enumerate(files):
    im=Image.open(f); im.thumbnail((w,h)); x=(i%3)*w; y=(i//3)*(h+26)
    out.paste(im,(x,y+26)); d.text((x+4,y+4),f.stem,fill='black')
out.save(p/sys.argv[1],quality=90)
