from pathlib import Path
import json,hashlib,datetime
from PIL import Image
p=Path(__file__).parent
s=json.loads((p/'SUMMARY.json').read_text(encoding='utf-8'))
assert len(s['exact_three_item_note_prefix'].split(' | '))==3
assert s['battle_complete'] and s['match_count']==1 and s['owner_turns']==5
for f in p.glob('*.json'):
 json.loads(f.read_text(encoding='utf-8-sig'))
for f in (p/'evidence/native').glob('t*.jpg'):
 with Image.open(f) as im: assert im.size==(1170,2532),(f,im.size)
text=(p/'REVIEW.md').read_text(encoding='utf-8')
for prohibited in ['Turtonator','Armarouge','Mega Gengar','May,']:
 assert prohibited not in text
names=['SOURCE.json','PROBE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','EVIDENCE_MAP.json','build_sheets.py','build_native_sheets.py','verify_evidence.py','write_primary.py']
files=[p/n for n in names]+[f for f in (p/'evidence').rglob('*') if f.is_file()]
entries=[]
for f in sorted(files):
 b=f.read_bytes();entries.append({'path':f.relative_to(p).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'source_filename':s['source_filename'],'source_sha256':s['source_sha256'],'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':s['reviewer'],'scope':'Primary SOURCE/PROBE/ASSIGNMENT, full review/coverage/summary/uncertainties, evidence map and all retained primary evidence; excludes this manifest, independent_sol, lead/external/completion/archive files and lead registration metadata. No primary changes after freeze.','files':entries}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
assert all(hashlib.sha256((p/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in entries)
print(json.dumps({'frozen_files':len(entries),'native_frames':len(list((p/'evidence/native').glob('t*.jpg'))),'evidence_files':len(files)-len(names),'total_bytes':sum(e['bytes'] for e in entries),'manifest_sha256':hashlib.sha256((p/'REVIEW_PACKET_HASHES.json').read_bytes()).hexdigest()},indent=2))
