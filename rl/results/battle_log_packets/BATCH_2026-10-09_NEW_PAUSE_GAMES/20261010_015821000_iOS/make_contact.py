from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
paths=sorted((p/'turn_evidence').glob('t*.jpg'))
for i in range(0,len(paths),9):
 out=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(out)
 for j,f in enumerate(paths[i:i+9]):
  x=j%3*390;y=j//3*870
  d.text((x+4,y+2),f.stem,fill='black')
  with Image.open(f) as im:im.thumbnail((390,844));out.paste(im,(x,y+26))
 out.save(p/f'contact_{i//9+1:02}.jpg',quality=88)
