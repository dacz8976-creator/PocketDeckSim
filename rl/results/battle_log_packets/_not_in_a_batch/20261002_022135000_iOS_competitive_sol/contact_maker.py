from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent/'overview'
first,last=map(int,sys.argv[1:3])
for start in range(first-1,last,9):
    paths=[p/'sample_frames'/f'{i:05}.jpg' for i in range(start+1,min(start+10,last+1))]
    if not all(x.exists() for x in paths): continue
    with Image.open(paths[0]) as im: w,h=im.size
    sh=Image.new('RGB',(w*3,(h+26)*3),'white');d=ImageDraw.Draw(sh)
    for n,path in enumerate(paths):
        x=n%3*w;y=n//3*(h+26);d.text((x+4,y+5),f'{(start+n+0.5)*4:.2f}s',fill='black')
        with Image.open(path) as im: sh.paste(im,(x,y+26))
    out=p/f'sheet_{start//9+1:02}.jpg';sh.save(out,quality=88);print(out)
