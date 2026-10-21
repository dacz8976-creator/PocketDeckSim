import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
p=Path(__file__).parent
for name in ('SOURCE.json','SUMMARY.json','UNCERTAINTIES.json'):
    json.loads((p/name).read_text(encoding='utf-8-sig'))
s=json.loads((p/'SUMMARY.json').read_text(encoding='utf-8-sig'))
assert s['source_sha256']==json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))['sha256']
assert s['first_main_attack']['owner_turn']==3 and s['first_main_attack']['global_turn']==5
for ref in s['key_evidence_paths']:
    assert (p/ref).is_file(),ref
files={}
for f in sorted(p.rglob('*')):
    if f.is_file() and f.name!='REVIEW_PACKET_HASHES.json':
        files[f.relative_to(p).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
manifest={'source_filename':s['source_filename'],'source_sha256':s['source_sha256'],'frozen_utc':datetime.now(timezone.utc).isoformat(),'reviewer':s['reviewer'],'files':files}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for rel,sha in files.items(): assert hashlib.sha256((p/rel).read_bytes()).hexdigest()==sha
print(json.dumps({'frozen_files':len(files),'key_evidence_files':len(s['key_evidence_paths']),'manifest':str(p/'REVIEW_PACKET_HASHES.json')}))
