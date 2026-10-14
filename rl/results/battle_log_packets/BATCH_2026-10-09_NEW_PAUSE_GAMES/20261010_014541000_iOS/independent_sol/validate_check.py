from pathlib import Path
import json,hashlib
from PIL import Image
p=Path(__file__).parent.parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8'))
ev=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
ids={f['evidence_id'] for f in ev['frames']}
errors=[]
def inspect(x,file):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ['source_sha256','sha256'] and v is not None and v!=source['sha256']: errors.append([file,'hash',v])
            if k=='source_video' and v!=source['video_basename']: errors.append([file,'source',v])
            if k in ['evidence_ids','turn_evidence_ids']:
                for r in v:
                    if r not in ids: errors.append([file,'missing evidence',r])
            inspect(v,file)
    elif isinstance(x,list):
        for v in x:inspect(v,file)
for n in names:
    if n.endswith('.json'):inspect(json.loads((p/n).read_text(encoding='utf-8')),n)
for f in ev['frames']:
    for k in ['full_frame_path']:
        path=p/f[k]
        if not path.exists():errors.append([f['evidence_id'],'missing path',f[k]])
        elif Image.open(path).size!=(1170,2532):errors.append([f['evidence_id'],'not native',f[k]])
    for k in ['bottom_crop','top_crop']:
        path=p/f[k]['path']
        bounds=f[k]['pixel_bounds_x0_y0_x1_y1']
        if not path.exists():errors.append([f['evidence_id'],'missing crop',str(path)])
        elif Image.open(path).size!=(bounds[2]-bounds[0],bounds[3]-bounds[1]):errors.append([f['evidence_id'],'crop bounds mismatch',str(path)])
l=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
assert [t['turn_number'] for t in l['turns']]==list(range(1,13))
print(json.dumps({'errors':errors,'frames':len(ev['frames']),'turns':len(l['turns']),'source_sha256':source['sha256'],'checked_input_sha256':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}},indent=2))
