import sys
from PIL import Image
QA = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\turn_evidence" + "\\"


def is_red(p):
    r, g, b = p[:3]
    return r > 110 and g < 60 and b < 60


for name in sys.argv[1:]:
    im = Image.open(QA + name).convert('RGB')
    out = []
    for y in (300, 330, 360):
        xs = []
        prev = False
        run_start = None
        for x in range(280, 900):
            red = is_red(im.getpixel((x, y)))
            if red and not prev:
                run_start = x
            if not red and prev:
                xs.append((run_start, x - 1))
            prev = red
        out.append((y, [a for a, b in xs if b - a >= 2]))
    print(name)
    for y, xs in out:
        print('   y=%d red runs at x=%s (n=%d)' % (y, xs, len(xs)))
