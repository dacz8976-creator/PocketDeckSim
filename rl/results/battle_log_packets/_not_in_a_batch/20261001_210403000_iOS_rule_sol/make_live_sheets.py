from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol/overview')
paths=sorted((p/'sample_frames').glob('*.jpg'))
for start in range(0,(len(paths)//9)*9,9):
 target=p/f'live_{start//9+1:02d}.jpg'
 if target.exists(): continue
 h=Image.open(paths[start]).height
 im=Image.new('RGB',(1170,(h+26)*3),'white'); d=ImageDraw.Draw(im)
 for j,f in enumerate(paths[start:start+9]):
  x=j%3*390;y=j//3*(h+26);d.text((x+4,y+5),f'{(start+j+.5)*3:.2f}s',fill='black');im.paste(Image.open(f),(x,y+26))
 im.save(target,quality=88)
 print(target)
