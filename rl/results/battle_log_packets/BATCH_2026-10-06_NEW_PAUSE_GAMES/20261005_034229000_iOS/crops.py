from pathlib import Path
from PIL import Image
p=Path(__file__).parent/'turn_evidence'
for f in sorted(p.glob('t*.jpg')):
    if '_' in f.stem: continue
    im=Image.open(f)
    im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_bottom.jpg'),quality=95)
    im.crop((0,0,1170,730)).save(f.with_name(f.stem+'_top.jpg'),quality=95)
