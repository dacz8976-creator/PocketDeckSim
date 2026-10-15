from pathlib import Path
from PIL import Image, ImageDraw

packet = Path(__file__).parent
files = sorted(packet.glob('overview_*.jpg'))
for start in range(0, len(files), 10):
    batch = files[start:start + 10]
    canvas = Image.new('RGB', (468 * 5, 1040 * 2), 'white')
    draw = ImageDraw.Draw(canvas)
    for j, f in enumerate(batch):
        n = int(f.stem.split('_')[1])
        x, y = (j % 5) * 468, (j // 5) * 1040
        with Image.open(f) as im:
            canvas.paste(im, (x, y + 27))
        draw.text((x + 6, y + 5), f'{(n-1)*4:03d}s  {f.name}', fill='black')
    canvas.save(packet / f'sheet_{start//10:02d}.jpg', quality=85)

files = sorted((f for f in packet.glob('detail_*.jpg') if f.stem.split('_')[1].isdigit()), key=lambda f: (int(f.stem.split('_')[1]), int(f.stem.split('_')[2])))
for start in range(0, len(files), 12):
    batch = files[start:start + 12]
    canvas = Image.new('RGB', (468 * 4, 1040 * 3), 'white')
    draw = ImageDraw.Draw(canvas)
    for j, f in enumerate(batch):
        _, segment, num = f.stem.split('_')
        sec = int(segment) + int(num) - 1
        x, y = (j % 4) * 468, (j // 4) * 1040
        with Image.open(f) as im:
            canvas.paste(im, (x, y + 27))
        draw.text((x + 6, y + 5), f'{sec:03d}s  {f.name}', fill='black')
    canvas.save(packet / f'detail_sheet_{start//12:02d}.jpg', quality=85)

files = sorted((f for f in packet.glob('gap_*.jpg') if f.stem.split('_')[1].isdigit()), key=lambda f: (int(f.stem.split('_')[1]), int(f.stem.split('_')[2])))
for start in range(0, len(files), 12):
    batch = files[start:start + 12]
    canvas = Image.new('RGB', (468 * 4, 1040 * 3), 'white')
    draw = ImageDraw.Draw(canvas)
    for j, f in enumerate(batch):
        _, segment, num = f.stem.split('_')
        sec = int(segment) + int(num) - 1
        x, y = (j % 4) * 468, (j // 4) * 1040
        with Image.open(f) as im:
            canvas.paste(im, (x, y + 27))
        draw.text((x + 6, y + 5), f'{sec:03d}s  {f.name}', fill='black')
    canvas.save(packet / f'gap_sheet_{start//12:02d}.jpg', quality=85)
