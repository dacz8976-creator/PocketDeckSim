from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent/'evidence'
times=[86,114,137,171,183,203,213,233,235,325,327,329,357,359,361,363,379,381,453,455,457,459,461,463,465.1,465.2,465.3,465.4,465.5,465.6,465.7]
for start in range(0,len(times),9):
 fs=[p/f't{t:07.2f}.jpg' for t in times[start:start+9]]
 if not all(f.exists() for f in fs): continue
 out=Image.new('RGB',(1500,3360),'white');d=ImageDraw.Draw(out)
 for j,f in enumerate(fs):
  im=Image.open(f);im.thumbnail((500,1082));x=j%3*500;y=j//3*1120
  out.paste(im,(x,y+30));d.text((x+10,y+5),f.name,fill='black')
 out.save(p/f'critical_{start//9+1:02d}.jpg',quality=91)
print(sum(f.exists() for f in [p/f't{t:07.2f}.jpg' for t in times]))
