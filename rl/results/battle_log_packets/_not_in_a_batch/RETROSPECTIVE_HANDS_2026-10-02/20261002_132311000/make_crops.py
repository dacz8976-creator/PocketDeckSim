from pathlib import Path
from PIL import Image
import json

packet=Path(__file__).resolve().parent
old=packet.parents[1]/'20261002_132311000_iOS_shark_sol'
paths=[old/'native/t0190.00.jpg',old/'native/t0161.00.jpg',old/'native_extra/t0177.00.jpg', old/'native_extra/t0189.00.jpg',old/'native/t0356.00.jpg',old/'native/t0366.00.jpg',old/'native/t0372.00.jpg',old/'native/t0378.00.jpg']
paths += sorted((packet/'turn_evidence').glob('t*.jpg'))
out=packet/'turn_evidence'
out.mkdir(exist_ok=True)
inventory=[]
for p in paths:
    with Image.open(p) as im:
        w,h=im.size
        for role,box in [('bottom',(0,int(h*.8),w,h)),('top',(0,0,w,490))]:
            dest=out/f'{p.stem}_{role}.png'
            im.crop(box).save(dest)
            inventory.append({'source_frame':str(p),'role':role,'path':str(dest),'bounds':list(box),'native_dimensions':[w,h]})
(packet/'CROP_INVENTORY.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
print(json.dumps({'crop_count':len(inventory),'native_frame_count':len(paths),'crop_bytes':sum(Path(x['path']).stat().st_size for x in inventory)}))
