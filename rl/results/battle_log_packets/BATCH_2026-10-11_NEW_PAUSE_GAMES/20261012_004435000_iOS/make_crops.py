from PIL import Image
from pathlib import Path
import json,shutil
p=Path(__file__).parent/'turn_evidence'
rows=[]
selected={27,43,129,134,135,136,138,139,141,185,187.5,188.3,189,191,194,213,223,267,272.5,274.5,275,277,280,289,294,299,342,351,351.4,352,354,357,402,419,445,447,448,449,450,451,452,454}
for f in sorted(p.glob('t*.jpg')):
 if '_bottom' in f.stem or '_top' in f.stem: continue
 if float(f.stem[1:]) not in selected: continue
 with Image.open(f) as im:
  w,h=im.size
  bottom=[0,int(h*.8),w,h]; top=[0,0,w,650]
  bp=f.with_name(f.stem+'_bottom.jpg');tp=f.with_name(f.stem+'_top.jpg')
  assert shutil.disk_usage(p).free>100*1024*1024,'Free-space gate'
  if not bp.exists():im.crop(bottom).save(bp,quality=88)
  if not tp.exists():im.crop(top).save(tp,quality=88)
 rows.append({'file':f.name,'requested_seconds':float(f.stem[1:]),'native_dimensions':[w,h],'bottom':{'path':bp.name,'bounds':bottom},'top':{'path':tp.name,'bounds':top}})
(p.parent/'NATIVE_CROPS_MANIFEST.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('native crop pairs',len(rows))
