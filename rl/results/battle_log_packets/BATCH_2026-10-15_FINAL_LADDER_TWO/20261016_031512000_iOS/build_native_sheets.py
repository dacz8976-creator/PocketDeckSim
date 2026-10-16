from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent/'evidence'/'native'
files=sorted(f for f in p.glob('t*.jpg') if float(f.stem[1:])%3==1.5)
for k in range(0,len(files),8):
 s=files[k:k+8]
 if len(s)<8:continue
 dest=p.parent/f'native_sheet_{k//8+1:02d}.jpg'
 if dest.exists():continue
 out=Image.new('RGB',(1880,2098),'white');d=ImageDraw.Draw(out)
 for j,f in enumerate(s):
  x=j%4*470;y=j//4*1049
  d.text((x+4,y+4),f'{float(f.stem[1:]):.1f}s',fill='black')
  with Image.open(f) as im:out.paste(im.resize((470,1017)),(x,y+32))
 out.save(dest,quality=92); print(dest)
