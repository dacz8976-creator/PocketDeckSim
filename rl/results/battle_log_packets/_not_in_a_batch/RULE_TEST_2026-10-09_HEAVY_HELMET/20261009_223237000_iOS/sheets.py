from PIL import Image, ImageDraw
from pathlib import Path
root=Path(__file__).parent
frames=sorted((root/'frames').glob('overview_*.jpg'))
for start in range(0,len(frames),20):
    sheet=Image.new('RGB',(1170,2144),'#ddd')
    draw=ImageDraw.Draw(sheet)
    for j,p in enumerate(frames[start:start+20]):
        im=Image.open(p); im.thumbnail((234,506))
        x=(j%5)*234; y=(j//5)*536
        sheet.paste(im,(x,y+30)); draw.text((x+5,y+5),f'{p.stem} ~{2.5+(start+j)*5:.1f}s',fill='black')
    sheet.save(root/f'sheet_{start//20+1:02d}.jpg',quality=95)
