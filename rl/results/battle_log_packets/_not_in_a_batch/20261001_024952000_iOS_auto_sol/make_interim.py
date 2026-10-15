from pathlib import Path
from PIL import Image,ImageDraw
out=Path(__file__).parent/'overview';paths=sorted((out/'sample_frames').glob('*.jpg'))
for start in range(0,len(paths)-8,9):
 target=out/f'sheet_{start//9+1:02d}.jpg'
 if target.exists(): continue
 sheet=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(sheet)
 for slot,p in enumerate(paths[start:start+9]):
  x=slot%3*390;y=slot//3*870;d.text((x+4,y+5),f'{(start+slot+.5)*3:.2f}s',fill='black')
  with Image.open(p) as im:sheet.paste(im,(x,y+26))
 sheet.save(target,quality=88)
