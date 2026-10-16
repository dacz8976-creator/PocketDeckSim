from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent/'evidence'
times=[2,3,4,16,20,34,38,42,47,51,54,56,58,62,66,72,77,81,84,87,89,92,96,101,104,107,113,117,122,126,128,132,136,138,142,148,152,156,158,162,168,172,174,178,182,184,186,188,192,196,198,204,208,212,216,218,222,224,226,228,232,234,236,238,242,244,246,248,252,258,264,268,272,278,284,290,296,302,308,314,320,326,332,338,342,344,346,348,352,354,356,358,362,364,366,368,372,374,376,378,382,392,402,412,422,424,426,452,454,456,458,462,464,466,467,468,469,471.8]
for start in range(0,len(times),9):
 fs=[p/f't{t:07.2f}.jpg' for t in times[start:start+9]]
 if not all(f.exists() for f in fs): continue
 out=Image.new('RGB',(1500,3360),'white');d=ImageDraw.Draw(out)
 for j,f in enumerate(fs):
  im=Image.open(f);im.thumbnail((500,1082));x=j%3*500;y=j//3*1120
  out.paste(im,(x,y+30));d.text((x+10,y+5),f.name,fill='black')
 out.save(p/f'supplement_{start//9+1:02d}.jpg',quality=91)
print(sum(f.exists() for f in [p/f't{t:07.2f}.jpg' for t in times]))
