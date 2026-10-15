from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent/'turn_evidence'
for f in sorted(p.glob('t*.jpg')):
 if '_bottom' in f.stem or '_top' in f.stem: continue
 with Image.open(f) as im:
  im.crop((0,2025,1170,2532)).save(p/(f.stem+'_bottom.jpg'),quality=95)
  im.crop((0,0,1170,1050)).save(p/(f.stem+'_top.jpg'),quality=95)
if len(sys.argv)>1:
 ts=[float(x) for x in sys.argv[1:]]
 s=Image.new('RGB',(780*4,(338+24)*((len(ts)+3)//4)),'white'); d=ImageDraw.Draw(s)
 for k,t in enumerate(ts):
  x=k%4*780;y=k//4*362;d.text((x+4,y+4),str(t),fill='black')
  with Image.open(p/f't{t:07.2f}_bottom.jpg') as im:s.paste(im.resize((780,338)),(x,y+24))
 s.save(p/'hands_contact.jpg',quality=95)
