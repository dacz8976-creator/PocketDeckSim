from pathlib import Path
import json
p=Path(__file__).parent
l=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
e=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
ids={x['evidence_id'] for x in e['frames']+e['overview_frames']};bad=[]
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='evidence_ids' and isinstance(v,list):bad.extend(i for i in v if i not in ids)
   else:walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(l)
missing_paths=[z for x in e['frames'] for z in [x['full_frame_path'],x['bottom_crop']['path'],x['top_crop']['path']] if not (p/z).exists()]
result={'turns':len(l['turns']),'turn_numbers':[x['turn_number'] for x in l['turns']],'native_frames':len(e['frames']),'overview_frames':len(e['overview_frames']),'missing_evidence_ids':sorted(set(bad)),'missing_paths':missing_paths,'scheduled_capture_unavailable':sum('requested_seconds' in x for x in e['scheduled_capture_limits']),'owner_end_counts':[(x['turn_number'],x['owner_hand_end']['count']) for x in l['turns'] if x['who_played']=='owner']}
print(result)
(p/'PACKET_STRUCTURE_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
