from PIL import Image,ImageDraw
from pathlib import Path
import sys
p=Path(__file__).parent
files=[p/'turn_evidence'/('t%07.2f.jpg'%float(t)) for t in sys.argv[1:]]
w=390;h=870;o=Image.new('RGB',(w*4,h*((len(files)+3)//4)),'white');d=ImageDraw.Draw(o)
for i,f in enumerate(files):
 x=(i%4)*w;y=(i//4)*h;d.text((x+3,y+3),f.stem,fill='black');im=Image.open(f);im.thumbnail((w,h-26));o.paste(im,(x,y+26))
o.save(p/'montage.jpg')
