"""Deterministic local checks only. Visual acceptance is a separate Sol review."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

p=argparse.ArgumentParser()
p.add_argument('stem')
a=p.parse_args()
BATCH=Path(__file__).resolve().parent
folder=BATCH/a.stem
assert folder.parent==BATCH and folder.is_dir()
required=['ASSIGNMENT.json','SOURCE_REFERENCE.json','HAND_SUPPLEMENT.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']
missing=[name for name in required if not (folder/name).is_file()]
json_files={}
for path in folder.glob('*.json'):
    json_files[path.name]=json.loads(path.read_text(encoding='utf-8-sig'))
images=[]
for path in sorted((folder/'turn_evidence').glob('*')):
    if path.suffix.lower() not in ['.jpg','.jpeg','.png']:
        continue
    with Image.open(path) as image:
        dimensions=image.size
    images.append({'path':str(path),'dimensions':dimensions,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
baseline=json.loads((BATCH/'PRESERVATION_BASELINE.json').read_text(encoding='utf-8'))
changed=[]
for record in baseline:
    if record['source'] != a.stem+'_iOS.MP4':
        continue
    path=Path(record['path'])
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
        changed.append(str(path))
hand=json_files.get('HAND_SUPPLEMENT.json',{})
turns=next((hand[key] for key in ['turns','target_rows','target_turns','rows'] if isinstance(hand.get(key),(list,dict))),[])
if isinstance(turns,dict):
    turns=list(turns.values())
numbers=[turn.get('turn_number') for turn in turns if isinstance(turn,dict)]
inventory=json.loads((BATCH/'INVENTORY.json').read_text(encoding='utf-8-sig'))
expected=None
for entry in inventory if isinstance(inventory,list) else inventory.get('recordings',inventory.get('games',[])):
    if entry.get('source',entry.get('video_basename'))==a.stem+'_iOS.MP4':
        expected=entry.get('target_turns',entry.get('target_owner_turns'))
if expected is None:
    expected=hand.get('target_turn_numbers')
if expected is None:
    expected={'20261002_132311000':[5,11],'20261002_115323000':[13],'20261002_143837000':[5,7]}.get(a.stem)
target_mismatch=expected is not None and sorted(numbers)!=sorted(expected)
report={'source':a.stem+'_iOS.MP4','missing_required_files':missing,'json_parsed':sorted(json_files),'target_turn_numbers':numbers,'expected_target_turn_numbers':expected,'target_mismatch':target_mismatch,'duplicate_target_turn_numbers':len(numbers)!=len(set(numbers)),'accepted_packet_files_changed':changed,'retained_images':images,'retained_image_bytes':sum(i['bytes'] for i in images),'structure_passed':not missing and not changed and not target_mismatch and len(numbers)==len(set(numbers)),'visual_acceptance':'Not established by this structural check; separate independent Sol inspection required'}
target=folder/'STRUCTURE_CHECK.json'
target.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['retained_images','json_parsed']}))
