from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol/native')
times=[44.5,81,83,87,102,107,109,110,122,124,129,132,146,153,156,202,249,252,282,285,294,297,300,305,311,314,315,316,330,340,342,348,350,354,355,376,378,380,384,386,387,396,402,406,410,411,412,414,416,419,420,422,423,426,432,434,439,442,444,447,449,455]
for start in range(0,len(times),9):
 group=times[start:start+9]
 im=Image.new('RGB',(1170,2628),'white');d=ImageDraw.Draw(im)
 for j,t in enumerate(group):
  f=p/f't{t:07.2f}.jpg'
  if not f.exists():continue
  src=Image.open(f);src.thumbnail((390,844));x=j%3*390;y=j//3*876;d.text((x+5,y+5),f'EXACT {t:.2f}s',fill='black');im.paste(src,(x,y+30))
 im.save(p/f'checks_{start//9+1:02d}.jpg',quality=90)
for t in [44.5,81,83,285,330,378]:
 f=p/f't{t:07.2f}.jpg'
 if f.exists(): Image.open(f).crop((60,650,1130,2250)).save(p/f'card_{t:07.2f}.jpg',quality=94)
