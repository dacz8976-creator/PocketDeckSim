from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent/'overview'
fs=sorted((p/'sample_frames').glob('*.jpg'))
for j in range((len(fs)+8)//9):
    subset=fs[j*9:(j+1)*9]
    w=390; h=Image.open(subset[0]).height
    im=Image.new('RGB',(3*w,3*(h+26)),'white'); d=ImageDraw.Draw(im)
    for k,f in enumerate(subset):
        x=(k%3)*w; y=(k//3)*(h+26)
        d.text((x+4,y+5),f'{(j*9+k+0.5)*3:.2f}s',fill='black')
        im.paste(Image.open(f),(x,y+26))
    im.save(p/f'sheet_{j+1:02d}.jpg',quality=88)
