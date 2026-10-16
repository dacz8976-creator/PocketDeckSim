from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent/'evidence'
files=sorted(p.glob('t*.jpg'))
for k in range(0,len(files),12):
    fs=files[k:k+12]
    if len(fs)<12 and not (p/'t0377.00.jpg').exists(): continue
    dest=p/f'detail_sheet_{k//12+1:02d}.jpg'
    if dest.exists(): continue
    sheet=Image.new('RGB',(1168,1980),'white');d=ImageDraw.Draw(sheet)
    for i,f in enumerate(fs):
        x=i%4*292;y=i//4*660
        d.text((x+4,y+2),f'{float(f.stem[1:]):.2f}s | {f.name}',fill='black')
        with Image.open(f) as im: sheet.paste(im.resize((292,632)),(x,y+28))
    sheet.save(dest,quality=89)
    print(dest)
