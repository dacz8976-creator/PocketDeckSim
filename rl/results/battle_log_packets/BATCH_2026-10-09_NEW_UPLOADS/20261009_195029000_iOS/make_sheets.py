from PIL import Image, ImageDraw
from pathlib import Path

root = Path(__file__).parent
src = root / "frames_1s"
out = root / "sheets"
out.mkdir(exist_ok=True)
files = sorted(src.glob("f_*.jpg"))
for start in range(0, len(files), 20):
    batch = files[start:start + 20]
    sheet = Image.new("RGB", (1200, 3340), "white")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(batch):
        im = Image.open(path).convert("RGB")
        im.thumbnail((285, 620))
        x, y = (i % 4) * 300, (i // 4) * 668
        sheet.paste(im, (x, y + 20))
        draw.text((x + 4, y + 2), f"{int(path.stem[2:]) - 1:03d}s", fill="black")
    sheet.save(out / f"sheet_{start:03d}.jpg", quality=88)
