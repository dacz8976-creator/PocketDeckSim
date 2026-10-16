from PIL import Image, ImageDraw
from pathlib import Path
p=Path(__file__).parent/'evidence'/'turnscan'
fs=sorted(p.glob('overview_*.jpg'))
for start in range(0,len(fs)//12*12,12):
    dest=p/f'progress_{start//12+1:02d}.jpg'
    if dest.exists(): continue
    w,h=Image.open(fs[start]).size
    out=Image.new('RGB',(w*4,(h+28)*3),'white');d=ImageDraw.Draw(out)
    for j,f in enumerate(fs[start:start+12]):
        x,y=j%4*w,j//4*(h+28)
        out.paste(Image.open(f),(x,y+28))
        d.text((x+4,y+4),f'{(start+j+.5)*5:.1f}s',fill='black')
    out.save(dest,quality=90)
