from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent/'seek_overview'; fs=sorted(p.glob('t*.jpg'))
for i in range(0,len(fs)-11,12):
 target=p/f'sheet_{i//12+1:02d}.jpg'
 if target.exists(): continue
 s=Image.new('RGB',(1560,2604),'white'); d=ImageDraw.Draw(s)
 for k,f in enumerate(fs[i:i+12]):
  x=k%4*390; y=k//4*868; d.text((x+4,y+4),f.stem,fill='black')
  with Image.open(f) as im:s.paste(im,(x,y+24))
 s.save(target,quality=88)
