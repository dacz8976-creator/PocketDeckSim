from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
times=[26,34,45,54,74,77,83,94,107,110,138,143,159,161,170,194,198,204,219,222,235,237,239,242,245,246,252,254,256,258]
for j in range(0,len(times),6):
    im=Image.new('RGB',(1170,3*(1266+26)),'white'); d=ImageDraw.Draw(im)
    for k,t in enumerate(times[j:j+6]):
        f=p/'native'/f't{t:07.2f}.jpg'
        if not f.exists(): continue
        x=(k%2)*585; y=(k//2)*1292
        d.text((x+4,y+4),f'{t:.2f}s',fill='black')
        im.paste(Image.open(f).resize((585,1266)),(x,y+26))
    im.save(p/'native'/f'contact_{j//6+1:02d}.jpg',quality=90)
