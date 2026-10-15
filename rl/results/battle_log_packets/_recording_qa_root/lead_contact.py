"""Create a bounded contact sheet from retained exact-time native evidence."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

p = argparse.ArgumentParser()
p.add_argument('packet')
p.add_argument('times', nargs='+', type=float)
p.add_argument('--folder', default='native')
p.add_argument('--name', default='LEAD_CONTACT.jpg')
p.add_argument('--width', type=int, default=440)
a = p.parse_args()
packet = Path(a.packet)
images = []
for t in a.times:
    path = packet / a.folder / f't{t:07.2f}.jpg'
    if not path.is_file():
        matches = list(packet.rglob(path.name))
        assert len(matches) == 1, f'Missing or ambiguous exact-time evidence: {path.name}'
        path = matches[0]
    with Image.open(path) as im:
        images.append(im.resize((a.width, round(im.height * a.width / im.width))))
h = max(im.height for im in images)
cols = min(4, len(images))
rows = (len(images) + cols - 1) // cols
sheet = Image.new('RGB', (cols * a.width, rows * (h + 28)), 'white')
draw = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(zip(a.times, images)):
    x, y = (i % cols) * a.width, (i // cols) * (h + 28)
    draw.text((x + 8, y + 6), f'Exact source {t:.2f}s', fill='black')
    sheet.paste(im, (x, y + 28))
sheet.save(packet / a.name, quality=92)
print(packet / a.name)
