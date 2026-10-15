from pathlib import Path
import json, hashlib
from PIL import Image, ImageChops, ImageStat
packet=Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\RETROSPECTIVE_HANDS_2026-10-02\20260908_190031000')
out=Path(__file__).parent
binding=[]
for p in sorted(packet.glob('*.json')):
    json.loads(p.read_text(encoding='utf-8-sig'))
    binding.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'read_encoding':'utf-8-sig'})
ev=json.loads((packet/'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
errors=[]; means=[]; image_binding=[]
for f in ev['frames']:
    p=Path(f['full_frame_path'])
    with Image.open(p) as im:
        if im.size != (1170,2532): errors.append(str(p)+' wrong dimensions')
        image_binding.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'evidence_id':f['evidence_id']})
        for kind in ['bottom_crop','top_crop']:
            c=f[kind]; cp=Path(c['path']); bounds=c['pixel_bounds_x0_y0_x1_y1']
            with Image.open(cp) as crop:
                expected=im.crop(bounds)
                if crop.size!=expected.size: errors.append(str(cp)+' wrong crop bounds');continue
                mean=sum(ImageStat.Stat(ImageChops.difference(expected.convert('RGB'),crop.convert('RGB'))).mean)/3
                means.append(mean)
                if mean>3: errors.append(str(cp)+' excessive JPEG difference '+str(mean))
            image_binding.append({'path':str(cp),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'evidence_id':f['evidence_id'],'bounds':bounds})
result={'packet_files':binding,'image_files':image_binding,'native_count':len(ev['frames']),'crop_count':len(means),'crop_mean_abs_difference_max':max(means),'errors':errors}
(out/'BINDING_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['packet_files','image_files']}))
