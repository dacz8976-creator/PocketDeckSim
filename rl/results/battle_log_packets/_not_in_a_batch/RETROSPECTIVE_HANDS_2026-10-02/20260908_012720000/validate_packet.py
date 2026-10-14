import json
from pathlib import Path
B=Path(__file__).resolve().parent
def read(n):return json.loads((B/n).read_text(encoding='utf-8-sig'))
e=read('TURN_EVIDENCE.json');rows=read('TURN_LEDGER.json')['turns'];hands=read('HAND_SUPPLEMENT.json');src=read('SOURCE_REFERENCE.json')
known={r['evidence_id'] for group in ['native_frames','reused_native_frames','prose_anchors','discard_snapshots'] for r in e[group]}
errors=[]
def scan(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k.endswith('evidence_ids') or k=='discard_snapshot_ids':
    for x in v or []:
     if x not in known:errors.append('Unbound evidence ID: '+x)
   else:scan(v)
 elif isinstance(obj,list):
  for v in obj:scan(v)
scan(rows)
for group in ['native_frames','reused_native_frames']:
 for f in e[group]:
  for p in [f['full_frame_path'],f['bottom_crop']['path'],f['top_crop']['path']]:
   if not Path(p).exists():errors.append('Missing evidence '+p)
for p in B.glob('*.json'):
 try:read(p.name)
 except Exception as exc:errors.append(p.name+': '+str(exc))
assert [r['turn_number'] for r in rows]==list(range(1,13))
assert [r['turn_number'] for r in hands['target_rows']]==[2,4,6,8,10,12]
assert len(e['native_frames'])==86
assert src['verification_status']=='verified_sha256_match'
assert src['classification']=='computer_battle' and src['excluded_from_ladder'] is True
assert all(r['owner_hand_start']['count']==len(r['owner_hand_start']['cards_left_to_right']) for r in rows)
assert all(r['owner_hand_end']['count']==len(r['owner_hand_end']['cards_left_to_right']) for r in rows)
result={'schema':'worker-packet-validation-v1','status':'passed' if not errors else 'failed','scope':'JSON parsing,12 sequential turns,6 target rows,86 native frames, all referenced frame paths and evidence IDs, completed source receipt, owner hand counts, computer classification','errors':errors,'factual_acceptance':'Independent checker pending; source work complete with explicit recording/sampling limits'}
(B/'WORKER_VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
