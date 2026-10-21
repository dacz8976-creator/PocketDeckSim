from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
fs=sorted(p.glob('t6_*.jpg'))
for start in range(0,len(fs),8):
 s=Image.new('RGB',(1560,1738),'white');d=ImageDraw.Draw(s)
 for i,f in enumerate(fs[start:start+8]):
  n=int(f.stem.split('_')[1]);t=332+(n-1)/4
  x=i%4*390;y=i//4*869;d.text((x+4,y+4),f'{f.name}, approx {t}',fill='black');im=Image.open(f);im.thumbnail((390,844));s.paste(im,(x,y+25))
 s.save(p/f't6_sheet_{start//8}.jpg',quality=90)
