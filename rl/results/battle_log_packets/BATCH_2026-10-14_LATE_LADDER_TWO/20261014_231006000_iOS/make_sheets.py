from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent/'evidence'
files=sorted(p.glob('t*.jpg'))
for start in range(0,len(files),9):
 fs=files[start:start+9]
 out=Image.new('RGB',(1500,3360),'white');d=ImageDraw.Draw(out)
 for j,f in enumerate(fs):
  im=Image.open(f);im.thumbnail((500,1082));x=j%3*500;y=j//3*1120
  out.paste(im,(x,y+30));d.text((x+10,y+5),f.name,fill='black')
 out.save(p/f'detail_{start//9+1:02d}.jpg',quality=91)
print(len(files))
