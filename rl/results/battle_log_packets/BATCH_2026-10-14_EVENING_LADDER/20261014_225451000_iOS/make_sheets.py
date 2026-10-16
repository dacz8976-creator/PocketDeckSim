from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).parent
files=sorted((p/'details').glob('t*.jpg'))
for start in range(0,len(files),12):
    sheet=Image.new('RGB',(1440,3*806),'white')
    d=ImageDraw.Draw(sheet)
    for j,f in enumerate(files[start:start+12]):
        x,y=j%4*360,j//4*806
        d.text((x+4,y+4),f.stem,fill='black')
        with Image.open(f) as im: sheet.paste(im.resize((360,779)),(x,y+27))
    sheet.save(p/f'detail_sheet_{start//12+1:02d}.jpg',quality=91)
