from pathlib import Path
import hashlib,json,datetime
p=Path(__file__).parent
for f in ['SOURCE.json','SUMMARY.json','UNCERTAINTIES.json']:
 json.loads((p/f).read_text(encoding='utf-8-sig'))
s=json.loads((p/'SUMMARY.json').read_text())
assert s['source_sha256']=='60f6a6c04e3f6e8c989b867b9dd41c536d4d0ac853b40603575a4ce3829faeee'
for f in s['key_evidence_paths']: assert (p/f).is_file(),f
files=[p/f for f in ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']]+sorted((p/'evidence').glob('*'))
hashes={f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.is_file()}
out={'source_filename':s['source_filename'],'source_sha256':s['source_sha256'],'reviewer':s['reviewer'],'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':hashes}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files_hashed':len(hashes),'native_frames':len(list((p/'evidence').glob('t*.jpg'))),'manifest_sha256':hashlib.sha256((p/'REVIEW_PACKET_HASHES.json').read_bytes()).hexdigest()}))
