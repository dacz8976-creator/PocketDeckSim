import sys
from PIL import Image
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/20261013_015659000_iOS/turn_evidence/"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R7/"
for name in sys.argv[1:]:
    im = Image.open(QA + name)
    print(name, im.size)
    box = (280, 100, 900, 420)
    c = im.crop(box)
    c = c.resize((c.width * 2, c.height * 2))
    c.save(OUT + "crop_fan_" + name.replace('.png', '').replace('.jpg', '') + ".png")
    box2 = (0, 560, 220, 760)
    c2 = im.crop(box2).resize((440, 400))
    c2.save(OUT + "crop_disc_" + name.replace('.png', '').replace('.jpg', '') + ".png")
