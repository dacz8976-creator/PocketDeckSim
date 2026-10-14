from PIL import Image, ImageDraw
from pathlib import Path
p = Path(__file__).parent / 'evidence'
ts = [20,23,24,26,29,30,32,36,46.7,65,65.5,168.5]
out=p/'sheets'
out.mkdir(exist_ok=True)
for start in range(0,len(ts),6):
    s=Image.new('RGB',(1170,1740),'white')
    d=ImageDraw.Draw(s)
    for i,t in enumerate(ts[start:start+6]):
        im=Image.open(p/f't{t:07.2f}.jpg').resize((390,844))
        x=i%3*390
        y=i//3*870
        s.paste(im,(x,y+26))
        d.text((x+4,y+4),str(t)+'s',fill='black')
    s.save(out/f'rapid_{start//6+1:02d}.jpg',quality=90)

