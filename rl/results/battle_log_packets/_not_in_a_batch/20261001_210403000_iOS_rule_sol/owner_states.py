from PIL import Image,ImageDraw
from pathlib import Path
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol/native')
times=[250,253,299,305,329,361,377,415,425,440,450,455]
im=Image.new('RGB',(1800,4*770),'white');d=ImageDraw.Draw(im)
for j,t in enumerate(times):
 f=p/f't{t:07.2f}.jpg'
 if f.exists():
  src=Image.open(f).crop((130,1180,1010,2250));src.thumbnail((600,740));x=j%3*600;y=j//3*770;im.paste(src,(x,y+30));d.text((x+5,y+5),str(t),fill='black')
im.save(p/'owner_states.jpg',quality=93)
