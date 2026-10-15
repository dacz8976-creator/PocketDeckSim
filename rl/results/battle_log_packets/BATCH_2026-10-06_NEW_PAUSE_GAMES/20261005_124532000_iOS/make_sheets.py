from pathlib import Path
from PIL import Image, ImageDraw
import sys
p=Path(__file__).parent
folder=p/(sys.argv[1] if len(sys.argv)>1 else 'native')
files=sorted(folder.glob('t*.jpg'))
for n in range(0,len(files),9):
    w,h=390,844
    canvas=Image.new('RGB',(w*3,(h+26)*3),'white')
    d=ImageDraw.Draw(canvas)
    for i,f in enumerate(files[n:n+9]):
        x,y=i%3*w,i//3*(h+26)
        d.text((x+4,y+5),f.name,fill='black')
        with Image.open(f) as im:canvas.paste(im.resize((w,h)),(x,y+26))
    canvas.save(folder/f'sheet_{n//9+1:02d}.jpg',quality=90)
