import os
from PIL import Image
d = r"C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-13_REMAINING_SIX\20261013_015659000_iOS\overview\sample_frames"
out = r"C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\panel14\V-R7"
names = ["00049.jpg", "00050.jpg", "00051.jpg", "00052.jpg"]
ims = [Image.open(os.path.join(d, n)) for n in names]
w = sum(i.width for i in ims)
h = max(i.height for i in ims)
s = Image.new("RGB", (w, h), "white")
x = 0
for i in ims:
    s.paste(i, (x, 0))
    x += i.width
s.save(os.path.join(out, "ov_49_52.png"))
print(s.size)
