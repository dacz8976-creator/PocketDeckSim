import os, sys
from PIL import Image
d = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\overview\sample_frames"
names = sys.argv[1].split(",")
ys = [int(y) for y in sys.argv[2].split(",")]
def isred(p):
    r, g, b = p[:3]
    return r > 90 and g < 75 and b < 75 and r > 1.8 * g
for n in names:
    im = Image.open(os.path.join(d, f"{n}.jpg")).convert("RGB")
    W, H = im.size
    for y in ys:
        runs, x = [], 90
        while x < 320:
            if isred(im.getpixel((x, y))):
                x0 = x
                while x < 320 and isred(im.getpixel((x, y))):
                    x += 1
                runs.append((x0, x - 1))
            x += 1
        merged = []
        for r in runs:
            if merged and r[0] - merged[-1][1] <= 2:
                merged[-1] = (merged[-1][0], r[1])
            else:
                merged.append(r)
        print(f"{n} y={y} runs({len(merged)}): {merged}")
