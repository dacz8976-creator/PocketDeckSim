from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent
fs=sorted((p/'turn_evidence').glob('t*.jpg'))
for f in fs:
 with Image.open(f) as im:
  im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_bottom.jpg'),quality=95)
  im.crop((0,0,1170,800)).save(f.with_name(f.stem+'_top.jpg'),quality=95)
out=p/'hand_sheets';out.mkdir(exist_ok=True)
for k in range(0,len(fs),8):
 s=Image.new('RGB',(1170,8*340),'white');d=ImageDraw.Draw(s)
 for i,f in enumerate(fs[k:k+8]):
  d.text((4,i*340+3),f.stem[1:]+'s',fill='black')
  with Image.open(f) as im:s.paste(im.crop((0,1900,1170,2532)).resize((585,316)),(0,i*340+24));s.paste(im.crop((0,0,1170,632)).resize((585,316)),(585,i*340+24))
 s.save(out/f'sheet_{k//8+1:02}.jpg',quality=95)
print(len(fs))
