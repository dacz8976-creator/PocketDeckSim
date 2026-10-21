import sys
from PIL import Image
QA = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\turn_evidence" + "\\"


def is_red(p):
    r, g, b = p[:3]
    return r > 110 and g < 60 and b < 60


def runs(im, y):
    xs, prev, st = [], False, None
    for x in range(250, 950):
        red = is_red(im.getpixel((x, y)))
        if red and not prev:
            st = x
        if not red and prev:
            if x - 1 - st >= 2:
                xs.append(st)
        prev = red
    return xs


for name in sys.argv[1:]:
    im = Image.open(QA + name).convert('RGB')
    best = None
    for y in range(340, 381, 5):
        r = runs(im, y)
        print('%s y=%d n=%d %s' % (name, y, len(r), r))
