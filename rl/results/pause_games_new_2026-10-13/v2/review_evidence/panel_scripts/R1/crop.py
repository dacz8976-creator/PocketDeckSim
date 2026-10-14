import sys
try:
    from PIL import Image
except ImportError:
    print("no PIL"); sys.exit(0)
src = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS/turn_evidence/"
out = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R1/"
for t in sys.argv[1:]:
    im = Image.open(src + "capture_%s_top.jpg" % t)
    c = im.crop((280, 100, 900, 430)).resize((1240, 660))
    c.save(out + "fan_%s.png" % t)
    print("saved", t, im.size)
