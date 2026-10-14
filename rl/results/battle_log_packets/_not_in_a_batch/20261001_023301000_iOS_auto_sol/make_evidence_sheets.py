from pathlib import Path
from PIL import Image, ImageDraw
p = Path(__file__).parent / 'target'
groups = {
    'opening_and_turn4': [21,22,35,37,41.5,44.5,47,48,50,51],
    'midgame': [58,60,69,71,96.5,98,100.5,105],
    'closing_transactions': [129,132,135,136,141.5,144,147,151,154,156,161,163,175.5],
}
for name, times in groups.items():
    w, h, cols = 468, 1013, 3
    rows = (len(times) + cols - 1) // cols
    sheet = Image.new('RGB', (w*cols, (h+24)*rows), 'white')
    draw = ImageDraw.Draw(sheet)
    for slot,t in enumerate(times):
        x,y=(slot%cols)*w,(slot//cols)*(h+24)
        draw.text((x+4,y+4),f'{t:.2f}s',fill='black')
        with Image.open(p/f't{t:07.2f}.jpg') as im:
            sheet.paste(im.resize((w,h)),(x,y+24))
    sheet.save(p/f'{name}.jpg',quality=92)
