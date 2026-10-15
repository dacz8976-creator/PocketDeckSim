from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent
f=sorted((p/'native').glob('*.jpg'))
for k in range(0,len(f),9):
 s=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(s)
 for n,x in enumerate(f[k:k+9]):
  im=Image.open(x);im.thumbnail((390,844));cx=n%3*390;cy=n//3*870;d.text((cx+5,cy+5),x.stem,fill='black');s.paste(im,(cx,cy+26))
 s.save(p/f'sheet_{k//9+1:02d}.jpg')
