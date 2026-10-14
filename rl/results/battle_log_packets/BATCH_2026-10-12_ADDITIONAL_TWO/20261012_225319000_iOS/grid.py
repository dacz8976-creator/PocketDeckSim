from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent/'turn_evidence';a,b=map(float,sys.argv[1:3]);paths=[x for x in sorted(p.glob('t*.jpg')) if '_' not in x.stem and a<=float(x.stem[1:])<=b]
for start in range(0,len(paths),8):
 s=Image.new('RGB',(1560,1738),'white');d=ImageDraw.Draw(s)
 for i,f in enumerate(paths[start:start+8]):
  x=i%4*390;y=i//4*869;d.text((x+4,y+4),f.stem,fill='black');im=Image.open(f);im.thumbnail((390,844));s.paste(im,(x,y+25))
 fn=p/f'focus_{a:04.0f}_{start//8:02d}.jpg';s.save(fn,quality=90);print(fn)
