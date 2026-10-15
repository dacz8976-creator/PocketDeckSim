from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_213822000_iOS_rule_sol')
files=sorted((p/'native').glob('*.jpg'))
for s in range(0,len(files),9):
 out=Image.new('RGB',(1050,2340),'white'); d=ImageDraw.Draw(out)
 for i,f in enumerate(files[s:s+9]):
  x=(i%3)*350;y=(i//3)*780
  d.text((x+5,y+4),f.stem,fill='black')
  im=Image.open(f);im.thumbnail((350,756));out.paste(im,(x,y+24))
 out.save(p/f'native_sheet_{s//9+1:02}.jpg',quality=90)
