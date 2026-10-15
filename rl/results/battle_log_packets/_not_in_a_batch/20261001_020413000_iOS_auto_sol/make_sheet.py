from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent/'overview'/'sample_frames'
nums=[int(x) for x in sys.argv[1:]]
w=390
h=844
out=Image.new('RGB',(w*3,(h+24)*((len(nums)+2)//3)),'white')
d=ImageDraw.Draw(out)
for k,n in enumerate(nums):
 if not (p/f'{n:05d}.jpg').exists(): continue
 im=Image.open(p/f'{n:05d}.jpg')
 x=k%3*w;y=k//3*(h+24)
 d.text((x+3,y+3),f'{(n-.5)*3:.1f}s sample {n}',fill='black')
 out.paste(im,(x,y+24))
out.save(Path(__file__).parent/f'progress_{nums[0]:03d}.jpg',quality=90)
