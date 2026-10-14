from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
for k,(a,b) in enumerate([(31,88),(89,138),(139,181),(182,213),(214,267),(268,328),(329,355),(356,386),(387,419),(420,460)]):
 paths=[x for x in (p/'turn_evidence').glob('t*.png') if '_' not in x.stem and a<=float(x.stem[1:])<=b];paths.sort()
 for z in range(0,len(paths),16):
  sheet=Image.new('RGB',(1400,4*781),'white');d=ImageDraw.Draw(sheet)
  for j,fn in enumerate(paths[z:z+16]):
   im=Image.open(fn);im.thumbnail((350,755));x=j%4*350;y=j//4*781;sheet.paste(im,(x,y+26));d.text((x+4,y+4),fn.stem,fill='black')
  sheet.save(p/f'phase{k+1}_{z//16}.jpg',quality=90)
