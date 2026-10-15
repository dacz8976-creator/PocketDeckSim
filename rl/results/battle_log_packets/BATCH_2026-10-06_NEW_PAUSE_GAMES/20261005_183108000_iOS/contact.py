from PIL import Image, ImageDraw
from pathlib import Path
import sys
p=Path(__file__).parent / 'turn_evidence'
lo,hi=map(float,sys.argv[1:3])
fs=[f for f in sorted(p.glob('t*.jpg')) if lo<=float(f.stem[1:])<=hi]
for j in range(0,len(fs),9):
    s=Image.new('RGB',(1170,2625),'white'); d=ImageDraw.Draw(s)
    for i,f in enumerate(fs[j:j+9]):
        x=(i%3)*390;y=(i//3)*875
        d.text((x+5,y+3),f.stem,fill='black')
        with Image.open(f) as im:s.paste(im.resize((390,844)),(x,y+25))
    s.save(p/f'c_{int(lo)}_{j//9:02d}.jpg')
    print(p/f'c_{int(lo)}_{j//9:02d}.jpg')
