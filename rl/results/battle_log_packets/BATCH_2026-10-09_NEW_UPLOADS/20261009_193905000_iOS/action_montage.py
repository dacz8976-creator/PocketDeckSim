from PIL import Image,ImageDraw
from pathlib import Path
import re,json
p=Path(__file__).parent
lines=(p/'frame_decode.log').read_text(errors='replace')
pts=[float(x) for x in re.findall(r'\bn:\s*\d+.*?pts_time:([0-9.]+)',lines)]
fs=sorted((p/'frames').glob('action_*.jpg'))
rows=[{'file':f'frames/{f.name}','source_seconds':t} for f,t in zip(fs,pts)]
(p/'FRAME_INDEX.json').write_text(json.dumps(rows,indent=2))
for start in range(0,len(rows),12):
 s=Image.new('RGB',(4*360,3*810),'white');d=ImageDraw.Draw(s)
 for j,r in enumerate(rows[start:start+12]):
  im=Image.open(p/r['file']);im.thumbnail((360,780));x=(j%4)*360;y=(j//4)*810
  s.paste(im,(x,y+25));d.text((x+4,y+4),f"{r['source_seconds']:.3f}s {Path(r['file']).stem}",fill='black')
 s.save(p/f"actions_{start//12+1:02}.jpg")
