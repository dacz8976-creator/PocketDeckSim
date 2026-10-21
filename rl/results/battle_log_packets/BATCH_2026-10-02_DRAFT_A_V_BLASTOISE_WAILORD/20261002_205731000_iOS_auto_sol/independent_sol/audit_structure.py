import json, hashlib
from pathlib import Path
from PIL import Image

p=Path(__file__).resolve().parent.parent
def read(n): return json.loads((p/n).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
s=read('SUBMISSION.json'); ledger=read('TURN_LEDGER.json'); ev=read('TURN_EVIDENCE.json'); manifest=read('EXTRACTION_MANIFEST.json')
errors=[]
checked={n:sha(p/n) for n in s['files']}
for n,h in checked.items():
    if h!=s['files'][n]: errors.append('Frozen hash mismatch '+n)
ids={x['evidence_id'] for x in manifest}
for f in manifest:
    for path,expected in [(f['full_frame_path'],f['full_frame_sha256']),(f['bottom_crop']['path'],f['bottom_crop']['sha256']),(f['top_crop']['path'],f['top_crop']['sha256'])]:
        if sha(path)!=expected: errors.append('Evidence hash mismatch '+path)
    with Image.open(f['full_frame_path']) as img:
        if img.size!=(1170,2532): errors.append('Native dimension mismatch '+f['evidence_id'])
    if f['actual_frame_seconds_if_measured'] is None: errors.append('Missing measured PTS '+f['evidence_id'])
    if not Path(f['decode_log']).exists(): errors.append('Missing decode log '+f['evidence_id'])
    for key in ['bottom_crop','top_crop']:
        c=f[key]; x0,y0,x1,y1=c['pixel_bounds_x0_y0_x1_y1']
        with Image.open(c['path']) as img:
            if img.size!=(x1-x0,y1-y0): errors.append('Crop bounds mismatch '+c['path'])
        if c['parent_sha256']!=f['full_frame_sha256']: errors.append('Crop parent mismatch '+f['evidence_id'])
def trace(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k.endswith('evidence_ids') and isinstance(v,list):
                for i in v:
                    if i not in ids: errors.append('Unresolved evidence ID '+str(i))
            trace(v)
    elif isinstance(x,list):
        for v in x: trace(v)
trace(ledger); trace(read('PAUSE_GAME.json')); trace(ev)
assert [t['turn_number'] for t in ledger['turns']]==list(range(1,19))
owners=[t for t in ledger['turns'] if t['who_played']=='owner']
timing=[]
for t in owners:
    frames=[f for f in ev['frames'] if f['turn_number']==t['turn_number']]
    offsets={f['offset_after_draw_seconds'] for f in frames}
    for offset in [1,3,6]:
        if offset not in offsets: errors.append('Missing offset '+str(t['turn_number'])+' '+str(offset))
    selected=[f for f in frames if f['selected_for_start_hand']]
    if len(selected)!=1 or not selected[0]['before_first_play']: errors.append('Start choice invalid '+str(t['turn_number']))
    if not any(f['role']=='before_ending_attack' for f in frames): errors.append('Missing before-ending frame '+str(t['turn_number']))
    if len(t['hand_at_start']['cards_left_to_right'])!=t['hand_at_start']['count']: errors.append('Start count mismatch')
    if len(t['owner_hand_end']['cards_left_to_right'])!=t['owner_hand_end']['count']: errors.append('End count mismatch')
    if [x['order'] for x in t['plays_in_order']]!=list(range(1,len(t['plays_in_order'])+1)): errors.append('Action order nonsequential')
    timing.append({'turn':t['turn_number'],'selected':selected[0]['evidence_id'],'draw_end':t['timing']['draw_animation_end_seconds'],'selected_pts':selected[0]['actual_frame_seconds_if_measured'],'end_hand_count':t['owner_hand_end']['count']})
for t in ledger['turns']:
    if t['who_played']=='opponent':
        for d in t['draws_and_searches']:
            for card in d['cards_in_reveal_order']:
                if card['name'] is not None: errors.append('Concealed opponent draw named T'+str(t['turn_number']))
deck=read('DECK_USED.json')
assert len(deck['cards_in_log_order'])==20
assert sum(c['name']=='Misty' for c in deck['cards_in_log_order'])==2
out={'checked_submission_manifest_sha256':sha(p/'SUBMISSION.json'),'checked_submission_files':checked,'evidence_files_hashed':len(manifest)*3,'native_count':len(manifest),'crop_count':len(manifest)*2,'turn_count':len(ledger['turns']),'owner_turn_count':len(owners),'owner_timing':timing,'errors':errors}
(p/'independent_sol'/'STRUCTURAL_AUDIT.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checked_submission_files'},indent=2))
