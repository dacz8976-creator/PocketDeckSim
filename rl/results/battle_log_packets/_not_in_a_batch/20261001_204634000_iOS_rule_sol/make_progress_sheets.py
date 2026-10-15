from pathlib import Path
from PIL import Image, ImageDraw
p = Path(__file__).parent / 'overview'
fs = sorted((p / 'sample_frames').glob('*.jpg'))
for start in range(0, len(fs) - 8, 9):
    target = p / f'progress_{start // 9 + 1:02d}.jpg'
    if target.exists():
        continue
    h = Image.open(fs[start]).height
    sheet = Image.new('RGB', (1170, (h+26)*3), 'white')
    draw = ImageDraw.Draw(sheet)
    for j, f in enumerate(fs[start:start+9]):
        x, y = j%3*390, j//3*(h+26)
        draw.text((x+4,y+5), f'{(start+j+0.5)*3:.2f}s', fill='black')
        sheet.paste(Image.open(f), (x,y+26))
    sheet.save(target, quality=88)
    print(target)
