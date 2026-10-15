import os, sys
from PIL import Image
d = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\turn_evidence"
names = sys.argv[1].split(",")
ys = [int(y) for y in sys.argv[2].split(",")]
def isred(p):
    r, g, b = p[:3]
    return r > 100 and g < 70 and b < 70 and r > 2 * g
def isdark(p):
    r, g, b = p[:3]
    return r < 80 and g < 60 and b < 60
for n in names:
    im = Image.open(os.path.join(d, f"t{n}_top.png")).convert("RGB")
    W, H = im.size
    for y in ys:
        runs = []
        x = 0
        while x < W:
            if isred(im.getpixel((x, y))):
                x0 = x
                while x < W and isred(im.getpixel((x, y))):
                    x += 1
                runs.append((x0, x - 1))
            x += 1
        # merge runs closer than 4 px
        merged = []
        for r in runs:
            if merged and r[0] - merged[-1][1] <= 4:
                merged[-1] = (merged[-1][0], r[1])
            else:
                merged.append(r)
        merged = [r for r in merged if r[1] - r[0] >= 2]
        # dark (black band) extent
        darkxs = [x for x in range(W) if isdark(im.getpixel((x, y)))]
        print(f"{n} y={y} size={W}x{H} red runs ({len(merged)}): {[(a, b) for a, b in merged]} | dark span {min(darkxs) if darkxs else None}-{max(darkxs) if darkxs else None} n={len(darkxs)}")
