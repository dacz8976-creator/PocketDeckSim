from PIL import Image,ImageDraw
from pathlib import Path
import sys
p=Path(__file__).parent
paths=[p/'turn_evidence'/f't{float(x):07.2f}.jpg' for x in sys.argv[1:]] if len(sys.argv)>1 else sorted((p/'turn_evidence').glob('t*.jpg'))
for k in range(0,len(paths),12):
    chunk=paths[k:k+12];s=Image.new('RGB',(1200,2010),'white');d=ImageDraw.Draw(s)
    for j,q in enumerate(chunk):
        if not q.exists():continue
        im=Image.open(q);im.thumbnail((300,645));x=j%4*300;y=j//4*670
        s.paste(im,(x,y+25));d.text((x+5,y+4),q.stem,fill='black')
    target=p/f'contact_{k//12+1:02d}.jpg';s.save(target,quality=90);print(target)
