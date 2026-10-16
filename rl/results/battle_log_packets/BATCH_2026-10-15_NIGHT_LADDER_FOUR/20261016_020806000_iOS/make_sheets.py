from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).parent/'action'
fs=sorted(p.glob('overview_*.jpg'))
for k in range(0,len(fs)//12*12,12):
    dest=p/f'early{k//12+1:02d}.jpg'
    if dest.exists(): continue
    s=Image.new('RGB',(1800,3006),'white'); d=ImageDraw.Draw(s)
    for i,f in enumerate(fs[k:k+12]):
        x,y=i%4*450,i//4*1002
        d.text((x+4,y+4),str((i+k+.5)*5),fill='black')
        s.paste(Image.open(f),(x,y+28))
    s.save(dest,quality=88)
