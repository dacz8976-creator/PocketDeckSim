from pathlib import Path
from PIL import Image,ImageDraw
import re,json
p=Path(__file__).resolve().parent
log=(p/'keyframes.log').read_text(errors='replace');ts=[float(x) for x in re.findall(r'pts_time:([\d.]+)',log)]
fs=sorted(p.glob('k*.jpg'));items=[dict(path=f.name,actual_seconds=t) for f,t in zip(fs,ts)]
(p/'keyframe_map.json').write_text(json.dumps(items,indent=2))
out=p/'key_sheets';out.mkdir(exist_ok=True)
for k in range(0,len(items),12):
 s=Image.new('RGB',(1560,2610),'white');d=ImageDraw.Draw(s)
 for i,it in enumerate(items[k:k+12]):
  x=i%4*390;y=i//4*870
  with Image.open(p/it['path']) as im:s.paste(im,(x,y+26))
  d.text((x+3,y+5),str(it['actual_seconds'])+'s',fill='black')
 s.save(out/f'sheet_{k//12+1:02}.jpg',quality=88)
print(len(items))
