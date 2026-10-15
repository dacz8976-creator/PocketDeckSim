from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent/'locator_scan'
ps=sorted((p/'frames').glob('*.jpg'))
for start in range(0,len(ps)-19,20):
    out=p/f'preview_{start:03d}.jpg'
    if out.exists(): continue
    im=Image.new('RGB',(1170,2104),'white'); d=ImageDraw.Draw(im)
    for i,f in enumerate(ps[start:start+20]):
        x=i%5*234;y=i//5*526
        d.text((x+3,y+3),str(start+i)+'s',fill='black')
        with Image.open(f) as pic: im.paste(pic,(x,y+20))
    im.save(out,quality=90)
