from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).resolve().parent
ts=[t for t in range(422,623,2) if (p/'native'/f't{t:07.2f}.jpg').exists()]
for k in range(0,len(ts),20):
    im=Image.new('RGB',(1500,2020),'white');d=ImageDraw.Draw(im)
    for i,t in enumerate(ts[k:k+20]):
        x=i%5*300;y=i//5*505;d.text((x,y),str(t),fill='black')
        a=Image.open(p/'native'/f't{t:07.2f}.jpg');a.thumbnail((300,480));im.paste(a,(x,y+20))
    im.save(p/f'edit_locator_{k//20+1}.jpg')
