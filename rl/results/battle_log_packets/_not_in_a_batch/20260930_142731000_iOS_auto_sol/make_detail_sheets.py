from PIL import Image, ImageDraw
from pathlib import Path
root=Path(__file__).parent
times=[4.5,20,23,29,35.2,37,37.6,50,65,68,76.5,80,88,91.3,104,107.5,110,114,116,129.5,135]
for base in range(0,len(times),6):
    canvas=Image.new('RGB',(1170,1740),'white')
    draw=ImageDraw.Draw(canvas)
    for slot,t in enumerate(times[base:base+6]):
        path=root/'keyframes'/f't{t:07.2f}.jpg'
        with Image.open(path) as im:
            im.thumbnail((390,844))
            x=(slot%3)*390;y=(slot//3)*870
            draw.text((x+4,y+4),f'{t:.2f}s',fill='black')
            canvas.paste(im,(x,y+26))
    canvas.save(root/f'detail_sheet_{base//6+1:02d}.jpg',quality=90)
