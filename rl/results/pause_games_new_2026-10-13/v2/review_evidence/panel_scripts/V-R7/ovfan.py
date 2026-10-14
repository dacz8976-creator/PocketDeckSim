import os, sys
from PIL import Image
d = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\overview\sample_frames"
out = r"C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\panel14\V-R7"
nums = sys.argv[1].split(",")
tag = sys.argv[2]
crops = []
for n in nums:
    im = Image.open(os.path.join(d, f"{n}.jpg"))
    c = im.crop((90, 20, 330, 140)).resize((240 * 4, 120 * 4), Image.LANCZOS)
    crops.append(c)
s = Image.new("RGB", (crops[0].width, sum(c.height for c in crops) + 10 * len(crops)), "white")
y = 0
for c in crops:
    s.paste(c, (0, y))
    y += c.height + 10
s.save(os.path.join(out, f"ovfan_{tag}.png"))
print(s.size)
