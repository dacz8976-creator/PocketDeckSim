from pathlib import Path
from PIL import Image,ImageDraw
p=Path('Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS');f=p/'dense';paths=sorted(list(f.glob('t*.jpg'))+list((p/'overview').glob('t*.jpg')),key=lambda q:q.name);paths=[q for q in paths if float(q.stem[1:])>=26]
for st in range(0,len(paths),12):
 s=Image.new('RGB',(1560,2610),'white');d=ImageDraw.Draw(s)
 for i,path in enumerate(paths[st:st+12]):
  x=i%4*390;y=i//4*870;d.text((x,y),path.stem,fill='black')
  with Image.open(path) as im:s.paste(im.resize((390,844)),(x,y+26))
 s.save(f/f'v{st//12:02}.jpg')

