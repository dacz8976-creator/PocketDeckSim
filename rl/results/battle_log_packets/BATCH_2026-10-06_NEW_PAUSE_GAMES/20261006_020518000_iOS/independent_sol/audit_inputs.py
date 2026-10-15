import json, hashlib, datetime
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent.parent
O=P/'independent_sol'
def read(n): return json.loads((P/n).read_text(encoding='utf-8'))
L=read('TURN_LEDGER.json'); E=read('TURN_EVIDENCE.json')
files=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files}
issues=[]; frames={f['evidence_id']:f for f in E['frames']}; image_hashes={}
for f in E['frames']:
    if f['source_sha256']!=read('SOURCE.json')['sha256']: issues.append('Frame source SHA mismatch '+f['evidence_id'])
    full=P/f['full_frame_path']
    with Image.open(full) as im:
        if im.size!=(1170,2532): issues.append('Native dimensions '+f['evidence_id'])
        image_hashes[f['full_frame_path']]=hashlib.sha256(full.read_bytes()).hexdigest()
        for k in ['bottom_crop','top_crop']:
            c=f[k]; path=P/c['path']; bounds=c['pixel_bounds_x0_y0_x1_y1']
            if k=='bottom_crop' and bounds!=[0,2025,1170,2532]: issues.append('Bottom fifth '+f['evidence_id'])
            with Image.open(path) as crop:
                if crop.size!=(bounds[2]-bounds[0],bounds[3]-bounds[1]): issues.append('Crop dimensions '+f['evidence_id'])
                if crop.convert('RGB').tobytes()!=im.crop(bounds).convert('RGB').tobytes(): issues.append('Crop pixels '+f['evidence_id']+k)
            image_hashes[c['path']]=hashlib.sha256(path.read_bytes()).hexdigest()
def walk(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k.endswith('evidence_ids') and isinstance(x,list):
                for i in x:
                    if i not in frames: issues.append('Missing evidence '+str(i))
            walk(x)
    elif isinstance(v,list):
        for x in v:walk(x)
for n in ['TURN_LEDGER.json','PAUSE_GAME.json','DECK_USED.json']:walk(read(n))
assert [t['turn_number'] for t in L['turns']]==list(range(1,18))
report={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_input_sha256':hashes,'frame_count':len(frames),'image_count':len(image_hashes),'image_sha256':image_hashes,'issues':issues,'integrity_pass':not issues,'semantic_acceptance':False}
(O/'INPUT_INTEGRITY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for t in L['turns']:
 print('TURN',t['turn_number'],t['who_played'],'start/end',t['owner_hand_start']['count'],t['owner_hand_end']['count'])
 print('plays',[(a['order'],a['kind'],a['card_name'],a['timestamp_seconds']) for a in t['plays_in_order']])
 if t['who_played']=='owner':
  print('start',t['owner_hand_start']['cards_left_to_right'],'end',t['owner_hand_end']['cards_left_to_right'])
  print('candidates',[(i,frames[i].get('before_first_play'),frames[i].get('unzoomed'),frames[i].get('suitability_or_limit')) for i in t['capture_candidates']])
print('INTEGRITY',len(frames),len(image_hashes),issues)
