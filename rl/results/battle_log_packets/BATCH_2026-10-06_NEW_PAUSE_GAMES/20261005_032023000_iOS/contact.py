from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent
times=[float(t) for t in sys.argv[2:]]
paths=[p/'turn_evidence'/f't{t:07.2f}.jpg' for t in times]
for start in range(0,len(paths),9):
    imgs=[Image.open(f).convert('RGB') for f in paths[start:start+9]]
    w=390;h=844
    out=Image.new('RGB',(w*3,(h+26)*3),'white');d=ImageDraw.Draw(out)
    for i,im in enumerate(imgs):
        x=(i%3)*w;y=(i//3)*(h+26)
        out.paste(im.resize((w,h)),(x,y+26));d.text((x+5,y+5),paths[start+i].stem,fill='black')
    out.save(p/f'{sys.argv[1]}_{start//9+1}.jpg',quality=90)
