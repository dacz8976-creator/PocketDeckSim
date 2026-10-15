from PIL import Image,ImageDraw
from pathlib import Path
import re,json,sys
p=Path(__file__).parent
pts=[float(x) for x in re.findall(r'\bn:\s*\d+.*?pts_time:([0-9.]+)',(p/'dense_decode.log').read_text(errors='replace'))]
fs=sorted((p/'frames').glob('dense_*.jpg'))
rows=[{'file':f'frames/{f.name}','source_seconds':t} for f,t in zip(fs,pts)]
(p/'DENSE_FRAME_INDEX.json').write_text(json.dumps(rows,indent=2))
# Retained original frames are the evidence. Inspection strips crop the readable popup/board and hand, without resizing inside each crop.
# Four sampled dense frames per row, each full width 1170 divided into center+hand at 360 px preview.
lo=float(sys.argv[1]);hi=float(sys.argv[2]);tag=sys.argv[3]
r=[x for x in rows if lo<=x['source_seconds']<=hi]
for start in range(0,len(r),16):
 s=Image.new('RGB',(4*290,4*535),'white');d=ImageDraw.Draw(s)
 for j,xr in enumerate(r[start:start+16]):
  im=Image.open(p/xr['file']);im.thumbnail((290,505));x=(j%4)*290;y=(j//4)*535
  s.paste(im,(x,y+25));d.text((x+2,y+3),f"{xr['source_seconds']:.3f}s {Path(xr['file']).stem}",fill='black')
 s.save(p/f"dense_{tag}_{start//16+1:02}.jpg")
print(len(r))
