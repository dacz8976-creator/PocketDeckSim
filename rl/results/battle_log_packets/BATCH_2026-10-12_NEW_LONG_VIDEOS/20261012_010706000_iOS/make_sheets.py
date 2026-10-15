from pathlib import Path
from PIL import Image, ImageDraw
import sys
folder=Path(__file__).parent / sys.argv[1]
paths=sorted(folder.glob('t*.jpg'))
for i in range(0,len(paths),9):
    sheet=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(sheet)
    for j,p in enumerate(paths[i:i+9]):
        im=Image.open(p);im.thumbnail((390,844));x=(j%3)*390;y=(j//3)*870
        d.text((x+3,y+3),p.stem,fill='black');sheet.paste(im,(x,y+26))
    sheet.save(folder/f'sheet_{i//9+1:02}.jpg',quality=90)
