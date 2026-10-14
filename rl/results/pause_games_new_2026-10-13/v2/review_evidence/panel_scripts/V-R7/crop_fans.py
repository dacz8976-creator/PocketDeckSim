import sys, os
from PIL import Image
src = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\fans.png"
out = r"C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\panel14\V-R7"
im = Image.open(src)
print(im.size, im.mode)
W, H = im.size
rows = 7
rh = H / rows
labels = ["0046.70", "0073.50", "0114.50", "0157.80", "0208.00", "0282.50", "0343.50"]
for i, lab in enumerate(labels):
    top = int(i * rh)
    # the fan is in the middle of each row: x 250..900, y top+100..top+rh
    box = (250, top + 90, 950, int(top + rh))
    c = im.crop(box)
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    c.save(os.path.join(out, f"fan_{lab}.png"))
print("done")
