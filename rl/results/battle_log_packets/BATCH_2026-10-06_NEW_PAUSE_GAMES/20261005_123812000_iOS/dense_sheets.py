from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/20261005_123812000_iOS');
for tag,ts in [('t2',[64,65,66,67,68,69,70,71,72,73,74,76,77,78,79,80.5,81,82,83,85,86,88,89,90.5,94,95,96,97,98,99,102,104,105,106,107]),('t6',[211,212,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,241,242,243,244]),('t7',[245,246,247,248,249,249.25,249.5,249.75,250,250.25,250.5,250.75,251,251.5,252,253,253.5,254,255,256,256.5,257,258,259,260,261,261.5,262,263,264,265,266,267,268,269,270,271,272,272.5,273,274,275,276,277,278,279,281])]:
 for k in range(0,len(ts),12):
  s=Image.new('RGB',(1560,2610),'white');d=ImageDraw.Draw(s)
  for i,t in enumerate(ts[k:k+12]):
   f=p/'turn_evidence'/f't{t:07.2f}.jpg'
   if not f.exists():continue
   im=Image.open(f);im.thumbnail((390,844));x=i%4*390;y=i//4*870;d.text((x+5,y+3),str(t),fill='black');s.paste(im,(x,y+25))
  s.save(p/'overview'/f'{tag}_dense_{k//12+1}.jpg',quality=90)
