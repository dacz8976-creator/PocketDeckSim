from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent/'locator_scan'
paths=sorted((P/'frames').glob('*.jpg'))
for start in range(0,len(paths)-19,20):
 gp=P/f'grid_{start:03d}_{start+19:03d}.jpg'
 if gp.exists():continue
 grid=Image.new('RGB',(1170,2104),'white');draw=ImageDraw.Draw(grid)
 for slot,path in enumerate(paths[start:start+20]):
  x=slot%5*234;y=slot//5*526;draw.text((x+3,y+3),f'nominal {start+slot}s',fill='black')
  with Image.open(path)as im:grid.paste(im,(x,y+20))
 grid.save(gp,quality=90)
print(len(paths),'decoded frames available; no additional movie decode')
