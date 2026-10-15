from PIL import Image, ImageDraw
from pathlib import Path
root=Path(__file__).parent
frames=sorted((root/'dense').glob('sec_*.jpg'))
for start in range(0,len(frames),30):
    sheet=Image.new('RGB',(1404,2680),'#ddd')
    draw=ImageDraw.Draw(sheet)
    for j,p in enumerate(frames[start:start+30]):
        im=Image.open(p); im.thumbnail((234,506))
        x=(j%6)*234; y=(j//6)*536
        sheet.paste(im,(x,y+30)); draw.text((x+5,y+5),f'{p.stem} ~{0.5+start+j:.1f}s',fill='black')
    sheet.save(root/f'dense_sheet_{start//30+1:02d}.jpg',quality=95)
