from PIL import Image, ImageDraw
from pathlib import Path

root = Path(__file__).parent
paths = sorted(root.glob('coarse_*.jpg'))
for start in range(0, len(paths), 8):
    batch = paths[start:start+8]
    out = Image.new('RGB', (1600, 1830), '#222222')
    draw = ImageDraw.Draw(out)
    for i, path in enumerate(batch):
        im = Image.open(path)
        im.thumbnail((390, 845))
        x = (i%4)*400+(400-im.width)//2
        y = (i//4)*915+25
        out.paste(im, (x,y))
        draw.text((x,y+848), f't={int(path.stem[-3:])-1}s', fill='white')
    out.save(root/f'contact_{start//8:02d}.jpg', quality=85)

for prefix, offset in [('A', 27), ('B', 39), ('C', 34)]:
    paths = sorted(root.glob(f'dense_{prefix}_*.jpg'))
    for start in range(0, len(paths), 10):
        batch = paths[start:start+10]
        out = Image.new('RGB', (1650, 1490), '#222222')
        draw = ImageDraw.Draw(out)
        for i, path in enumerate(batch):
            im = Image.open(path)
            im.thumbnail((324, 700))
            x = (i%5)*330+(330-im.width)//2
            y = (i//5)*745+25
            out.paste(im, (x,y))
            t = offset+(int(path.stem[-3:])-1)/5
            draw.text((x,y+703), f't={t:.1f}s', fill='white')
        out.save(root/f'contact_dense_{prefix}_{start//10:02d}.jpg', quality=85)
