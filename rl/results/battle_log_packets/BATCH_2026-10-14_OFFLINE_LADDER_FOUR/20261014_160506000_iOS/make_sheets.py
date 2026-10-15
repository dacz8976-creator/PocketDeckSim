from pathlib import Path
from PIL import Image, ImageDraw
import sys
p=Path(__file__).parent/(sys.argv[1] if len(sys.argv)>1 else 'native')
fs=sorted(p.glob('t*.jpg'))
w,h=520,1125
for j in range(0,len(fs),6):
    s=Image.new('RGB',(w*3,(h+25)*2),'white')
    d=ImageDraw.Draw(s)
    for i,f in enumerate(fs[j:j+6]):
        x,y=i%3*w,i//3*(h+25)
        d.text((x+4,y+3),f.stem,fill='black')
        s.paste(Image.open(f).resize((w,h)),(x,y+25))
    s.save(p/f'sheet_{j//6+1:02}.jpg',quality=88)
