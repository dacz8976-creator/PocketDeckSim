from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).parent/'overview'
fs=sorted((p/'sample_frames').glob('*.jpg'))
h=Image.open(fs[0]).height
for k in range(0,len(fs)-8,9):
    s=Image.new('RGB',(960,(h+26)*3),'white'); d=ImageDraw.Draw(s)
    for i,f in enumerate(fs[k:k+9]):
        x=i%3*320;y=i//3*(h+26)
        s.paste(Image.open(f),(x,y+26));d.text((x,y),str((k+i+0.5)*3)+'s',fill='black')
    s.save(p/f'progress_{k//9+1:02d}.jpg')
