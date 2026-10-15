from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
groups={'energy12':[418,419,420,422,426,429,430,431,433,434,435,438,439,440,441,442], 'first14':[475,476,477,478,479,480,481,482]}
for name,times in groups.items():
 for k in range(0,len(times),8):
  sheet=Image.new('RGB',(4*390,2*870),'white'); d=ImageDraw.Draw(sheet)
  for i,t in enumerate(times[k:k+8]):
   f=p/'turn_evidence'/f't{t:07.2f}.jpg'
   if f.exists():
    im=Image.open(f); im.thumbnail((390,844)); x=(i%4)*390;y=(i//4)*870;sheet.paste(im,(x,y+26));d.text((x+5,y+5),str(t),fill='black')
  sheet.save(p/f'{name}_{k//8}.jpg')
