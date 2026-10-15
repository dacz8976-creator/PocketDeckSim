from pathlib import Path
import sys
from PIL import Image, ImageDraw

base = Path(__file__).parent
prefix = sys.argv[1] if len(sys.argv) > 1 else 'coarse'
offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
interval = int(sys.argv[3]) if len(sys.argv) > 3 else 8
files = sorted(base.glob(f'{prefix}_*.jpg'))
for page in range((len(files) + 7) // 8):
    subset = files[page * 8:(page + 1) * 8]
    board = Image.new('RGB', (1640, 1780), '#eeeeee')
    draw = ImageDraw.Draw(board)
    for slot, path in enumerate(subset):
        image = Image.open(path).convert('RGB')
        image.thumbnail((390, 845))
        x = (slot % 4) * 410 + 10
        y = (slot // 4) * 890 + 24
        board.paste(image, (x, y))
        t = offset + (int(path.stem.split('_')[1]) - 1) * interval
        draw.text((x, y - 18), f'{t // 60:02d}:{t % 60:02d} {path.name}', fill='black')
    board.save(base / f'{prefix}_sheet_{page + 1:02d}.jpg', quality=87)
