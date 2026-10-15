from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent
f=sorted((p/'dense').glob('*.jpg'))
for k in range(0,len(f),12):
 s=Image.new('RGB',(1560,2295),'white');d=ImageDraw.Draw(s)
 for n,x in enumerate(f[k:k+12]):
  im=Image.open(x);im=im.crop((0,320,1170,2532));im.thumbnail((390,738));cx=n%4*390;cy=n//4*765;d.text((cx+5,cy+5),x.stem,fill='black');s.paste(im,(cx,cy+26))
 s.save(p/f'dense_sheet_{k//12+1:02d}.jpg')
