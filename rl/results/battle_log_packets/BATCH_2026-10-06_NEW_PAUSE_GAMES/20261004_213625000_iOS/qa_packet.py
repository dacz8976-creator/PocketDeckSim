import json,hashlib
from pathlib import Path
p=Path(__file__).parent
e=json.loads((p/'TURN_EVIDENCE.json').read_text());l=json.loads((p/'TURN_LEDGER.json').read_text())
ids={f['evidence_id'] for f in e['frames']};missing=[];bad=[]
def walk(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='evidence_ids' and isinstance(x,list):
    missing.extend(i for i in x if i not in ids)
   else:walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for n in ['TURN_LEDGER.json','PAUSE_GAME.json','SUMMARY.json']:
 text=(p/n).read_text(encoding='utf-8');walk(json.loads(text))
 if any(s in text for s in ['Pok\u00c3','Professor\u00e2','not_reviewed','not_captured']):bad.append(n)
paths=[]
for f in e['frames']:
 for k in ['full_frame','bottom_fifth','top_crop']:
  path=p/f[k];paths.append(path)
  if not path.is_file():missing.append(f[k])
for c in e['owner_turn_captures']:
 for key in ['chosen_pre_play_evidence_id','before_end_evidence_id','end_after_resolution_evidence_id']:
  if c[key] not in ids:missing.append(c[key])
 for candidate in c['candidate_frames']:
  if candidate['evidence_id'] not in ids:missing.append(candidate['evidence_id'])
q=json.loads((p/'QR_DECODE_RECEIPT.json').read_text());qr_ok=hashlib.sha256(Path(q['retained_image']).read_bytes()).hexdigest()==q['retained_image_sha256']
result={'pointer_integrity_pass':not missing,'missing':sorted(set(missing)),'encoding_pass':not bad,'encoding_issues':bad,'qr_native_image_hash_matches':qr_ok,'native_full_frames':len(e['frames']),'native_evidence_bytes':sum(f.stat().st_size for f in paths),'turn_rows':len(l['turns']),'owner_turn_rows':sum(t['who_played']=='owner' for t in l['turns']),'visual_acceptance':False,'status':'ready_for_independent_review'}
(p/'WORKER_QA.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
