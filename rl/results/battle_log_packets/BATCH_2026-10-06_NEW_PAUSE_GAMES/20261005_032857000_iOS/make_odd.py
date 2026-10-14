from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
for b,start in enumerate(range(43,300,24)):
 files=[p/'dense'/f't{t:07.2f}.jpg' for t in range(start,min(start+24,300),2)]
 if not all(f.exists() for f in files):continue
 s=Image.new('RGB',(1440,2440),'white');d=ImageDraw.Draw(s)
 for i,f in enumerate(files):
  im=Image.open(f);im.thumbnail((360,779));x=i%4*360;y=i//4*812;s.paste(im,(x,y+28));d.text((x+5,y+4),f.stem,fill='black')
 s.save(p/f'odd_{b:02d}.jpg',quality=92)
