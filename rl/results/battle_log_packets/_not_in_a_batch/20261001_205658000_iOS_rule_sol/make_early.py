from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).parent/'overview'
fs=sorted((p/'sample_frames').glob('*.jpg'))
for k in range(len(fs)//9):
 target=p/f'early_{k+1:02d}.jpg'
 if target.exists(): continue
 sheet=Image.new('RGB',(1170,2610),'white'); d=ImageDraw.Draw(sheet)
 for j,f in enumerate(fs[k*9:k*9+9]):
  x=j%3*390; y=j//3*870
  d.text((x+4,y+5),f'{(k*9+j+.5)*3:.2f}s',fill='black')
  with Image.open(f) as im: sheet.paste(im,(x,y+26))
 sheet.save(target,quality=88)
