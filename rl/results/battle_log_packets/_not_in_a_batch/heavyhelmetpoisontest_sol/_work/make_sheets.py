from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
frames = sorted(root.glob('frame_*.jpg'))
for chunk_start in range(0, len(frames), 20):
    sheet = Image.new('RGB', (4 * 292, 5 * 658), 'white')
    draw = ImageDraw.Draw(sheet)
    for offset, path in enumerate(frames[chunk_start:chunk_start + 20]):
        frame = Image.open(path)
        frame.thumbnail((286, 620))
        x = (offset % 4) * 292
        y = (offset // 4) * 658
        sheet.paste(frame, (x, y + 25))
        sec = (chunk_start + offset) / 2
        draw.text((x + 4, y + 4), f'{sec:05.1f}s  {path.stem}', fill='black')
    sheet.save(root / f'sheet_{chunk_start // 20:02d}.jpg', quality=85)
print(len(frames), 'frames,', len(list(root.glob('sheet_*.jpg'))), 'sheets')
