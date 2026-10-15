from PIL import Image
from pathlib import Path
import json
B=Path(__file__).parent
m=json.loads((B/'REUSED_MANIFEST.json').read_text())
for t,box,label in [(500,(170,310,1170,1190),'opponent_board'),(500,(410,1600,780,2090),'comfey'),(193,(160,320,1170,1200),'opponent_board'),(64,(0,0,1170,560),'fan'),(672,(0,0,1170,600),'fan')]:
 p=next(x['full_frame_path'] for x in m if x['requested_source_seconds']==t)
 Image.open(p).crop(box).save(B/f'inspect_{t}_{label}.jpg')
plan=json.loads((B/'EXTRACTION_PLAN.json').read_text())
plan['new_native_cap']=50
plan['additional_gap_checkpoint']['status']='approved_by_lead_2026-10-02'
for s in plan['additional_gap_checkpoint']['requested_seconds']:
 plan['rows'].append(dict(turn_number=15 if s<600 and s>580 else 17 if s>670 else 9 if s==348 else 1 if s==40 else 5,requested_source_seconds=float(s),purpose=plan['additional_gap_checkpoint']['justification'],status='planned_pending_identity_verification',actual_frame_seconds_if_measured=None))
plan['planned_new_native_count']=50
(B/'EXTRACTION_PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
