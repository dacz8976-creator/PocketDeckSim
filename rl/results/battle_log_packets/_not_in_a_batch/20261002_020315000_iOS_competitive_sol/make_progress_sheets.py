from PIL import Image, ImageDraw
from pathlib import Path
p = Path(__file__).parent / 'overview'
paths = sorted((p / 'sample_frames').glob('*.jpg'))
for start in range(0, len(paths)-8, 9):
    target = p / f'progress_{start//9+1:02d}.jpg'
    if target.exists():
        continue
    s = Image.new('RGB', (1170,2610), 'white')
    d = ImageDraw.Draw(s)
    for i,f in enumerate(paths[start:start+9]):
        x,y=(i%3)*390,(i//3)*870
        d.text((x+4,y+4),f'{(start+i+.5)*3:.2f}s',fill='black')
        s.paste(Image.open(f),(x,y+26))
    s.save(target)
    print(target)
