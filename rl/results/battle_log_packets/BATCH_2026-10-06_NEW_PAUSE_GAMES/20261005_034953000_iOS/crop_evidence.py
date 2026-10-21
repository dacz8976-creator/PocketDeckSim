from pathlib import Path
from PIL import Image
import json
p=Path(__file__).parent
s=json.loads((p/'SOURCE.json').read_text(encoding='utf-8'))
frames=[]
for q in sorted(q for q in (p/'turn_evidence').glob('t*.jpg') if '_' not in q.stem):
    t=float(q.stem[1:]);im=Image.open(q);w,h=im.size
    bottom=q.with_name(q.stem+'_bottom.jpg');top=q.with_name(q.stem+'_top.jpg')
    b=[0,int(h*.8),w,h];a=[0,0,w,750]
    im.crop(b).save(bottom,quality=95);im.crop(a).save(top,quality=95)
    frames.append(dict(evidence_id='f'+q.stem[1:].replace('.','_'),source_video=s['video_basename'],source_sha256=s['sha256'],seek_timestamp_seconds=t,actual_frame_timestamp_seconds=None,timestamp_basis='native FFmpeg input seek; decoded frame PTS not separately measured',full_frame_path=str(q.relative_to(p)),native_dimensions=[w,h],bottom_crop=dict(path=str(bottom.relative_to(p)),pixel_bounds_x0_y0_x1_y1=b),top_crop=dict(path=str(top.relative_to(p)),pixel_bounds_x0_y0_x1_y1=a)))
(p/'FRAME_INDEX.json').write_text(json.dumps(frames,indent=2),encoding='utf-8')
print(len(frames))
