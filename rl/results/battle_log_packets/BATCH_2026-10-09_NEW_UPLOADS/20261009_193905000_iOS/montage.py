from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent
fs=list((p/'frames').glob('coarse_*.jpg'))
for start in range(0,len(fs),12):
 s=Image.new('RGB',(4*300,3*675),'white'); d=ImageDraw.Draw(s)
 for j,f in enumerate(fs[start:start+12]):
  im=Image.open(f); im.thumbnail((300,650)); x=(j%4)*300;y=(j//4)*675
  s.paste(im,(x,y+25));d.text((x+4,y+4),f'{(start+j)*5+2.5:.1f}s',fill='black')
 s.save(p/f'overview_{start//12+1}.jpg')
