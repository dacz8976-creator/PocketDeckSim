from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
for key,ts in [('e12',[414,415,418,435]),('e14',[475,480,490,494,496,497,500])]:
 im=Image.new('RGB',(1170,len(ts)*550),'white');d=ImageDraw.Draw(im)
 for i,t in enumerate(ts):
  a=Image.open(p/'turn_evidence'/f't{t:07.2f}.jpg');im.paste(a.crop((0,110,1170,635)),(0,i*550+25));d.text((5,i*550+5),str(t),fill='black')
 im.save(p/(key+'.jpg'))
