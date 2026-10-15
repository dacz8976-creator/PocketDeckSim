from pathlib import Path
from PIL import Image
import json,hashlib
packet=Path(__file__).parent
old=Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\competitive-deck-study-2026-09-08\ongoing-campaign-2026-09-08\native-random-rotom')
frames=list(old.rglob('*.jpg'))
out=packet/'readability_crops';out.mkdir(exist_ok=True)
bindings=[]
for t in [75,145,160,220,230,250]:
 candidates=[p for p in frames if p.name.endswith(f'_t{t}.jpg') and 'timeline' in str(p)]
 if not candidates:continue
 p=candidates[0]
 with Image.open(p) as im:
  bounds=[0,500,1170,1120]
  dest=out/f'opponent_t{t}.png';im.crop(bounds).save(dest)
 bindings.append({'path':str(dest),'parent':str(p),'parent_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bounds':bounds,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(out/'BINDING.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8')
print([x['path'] for x in bindings])
