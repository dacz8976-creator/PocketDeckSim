from pathlib import Path
from PIL import Image,ImageDraw
from observations import STARTS,ENDS
p=Path(__file__).parent
for kind,ts in [('start',STARTS),('end',ENDS)]:
 s=Image.new('RGB',(300*7,510*3),'white');d=ImageDraw.Draw(s)
 for i,t in enumerate(ts):
  q=p/'turn_evidence'/f't{t:07.2f}.jpg'
  with Image.open(q) as im:
   own=im.crop((930,2070,1170,2330));opp=im.crop((60,250,300,470));s.paste(opp,(i%7*300,i//7*510+35));s.paste(own,(i%7*300,i//7*510+255))
  d.text((i%7*300,i//7*510),f'T{i+1} {t}',fill='black')
 s.save(p/f'zones_{kind}_audit.jpg')
