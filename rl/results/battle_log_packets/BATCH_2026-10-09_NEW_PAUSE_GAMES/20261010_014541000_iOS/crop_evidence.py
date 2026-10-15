from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent/'turn_evidence'
for f in p.glob('t*.jpg'):
    im=Image.open(f)
    im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_bottom.jpg'),quality=94)
    im.crop((0,0,1170,780)).save(f.with_name(f.stem+'_top.jpg'),quality=94)
sets={
 'candidates':[56.7,58.7,61.7,126.5,128.5,131.5,206.5,208.5,211.5,260,262,265,351,353,356,434,436,439],
 'details':[230,232,237,240,303,306,310,396,402,408,472,474,476],
 'boundaries':[74,78,114,122,172,185,195,203,245,254,324,342,346,417,423,429,451,486]
}
for name,ts in sets.items():
    for start in range(0,len(ts),9):
        s=Image.new('RGB',(1755,3900),'white'); d=ImageDraw.Draw(s)
        for i,t in enumerate(ts[start:start+9]):
            f=p/f't{t:07.2f}.jpg'
            s.paste(Image.open(f).resize((585,1266)),(i%3*585,i//3*1300+26)); d.text((i%3*585+5,i//3*1300+5),str(t),fill='black')
        s.save(p/f'{name}_{start//9+1}.jpg',quality=90)
