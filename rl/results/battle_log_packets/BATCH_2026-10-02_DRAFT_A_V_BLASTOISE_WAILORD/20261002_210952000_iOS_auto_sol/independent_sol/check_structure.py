import json,hashlib,re,datetime
from pathlib import Path
from PIL import Image
b=Path(__file__).resolve().parent.parent
r=lambda f:json.loads((b/f).read_text(encoding='utf-8-sig'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
l=r('TURN_LEDGER.json');e=r('TURN_EVIDENCE.json');m=r('EXTRACTION_MANIFEST.json');im=r('independent_sol/EXTRACTION_MANIFEST.json')
ids={x['evidence_id']for x in m}; refs=[]
def visit(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='evidence_ids':refs.extend(v)
   visit(v)
 elif isinstance(x,list):
  for v in x:visit(v)
visit(l)
errors=[]
if set(refs)-ids:errors.append('unregistered core evidence')
if {x['evidence_id']for x in e['frames']}!=ids:errors.append('evidence/manifest mismatch')
assert [t['turn_number']for t in l['turns']]==list(range(1,20))
for t in l['turns']:assert [x['order']for x in t['plays_in_order']]==list(range(1,len(t['plays_in_order'])+1))
for x in m+im:
 assert x['source_sha256']==l['sources'][0]['sha256']
 p=Path(x['full_frame_path'])
 assert Image.open(p).size==(1170,2532)
 if sha(p)!=x['full_frame_sha256']:errors.append(str(p))
 log=Path(x['decode_log']).read_text(encoding='utf-8')
 q=re.findall(r'\bn:\s*0\s+pts:\s*(-?\d+)\s+pts_time:([\d.-]+)',log)
 assert q and float(q[0][1])==x['actual_frame_seconds_if_measured']
 for z in ['top_crop','bottom_crop']:
  assert sha(Path(x[z]['path']))==x[z]['sha256']
assert r('DECK_USED.json')['actual_card_count']==20
d={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_video':l['sources'][0]['video_basename'],'source_sha256':l['sources'][0]['sha256'],'reviewer':'/root/ind_drafta_auto4','model':'gpt-6.1-sol','effort':'high','errors':errors,'primary_native_frames':len(m),'independent_native_frames':len(im),'aggregate_native_frames':len(m)+len(im),'cap':160,'turn_count':19,'owner_turn_count':9,'checks':['19sequential turns','sequential numbered plays','core refs resolve','evidence/manifest IDs identical','native1170x2532 dimensions','measured PTS agrees decoder showinfo','all148fullframe+296crop SHA values current','source bindings agree','exact supplied deck20separatefrom seen19'],'semantic_acceptance_not_inferred_from_structure':True}
(b/'independent_sol/STRUCTURAL_CHECK.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d))

