import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
evidence=root/'evidence'
# These are this worker's reduced navigation thumbnails only. Retain the
# labelled contact sheets and all native source screenshots.
for p in evidence.iterdir():
    if p.is_file() and (p.name.startswith('overview_') or p.name=='test120.jpg' or
        (p.name.startswith(('coarse_','detail_')) and '_sheet_' not in p.name)):
        assert p.resolve().parent==evidence.resolve()
        p.unlink()
for name in ['SOURCE.json','PROBE.json','SUMMARY.json','UNCERTAINTIES.json','ASSIGNMENT.json']:
    json.loads((root/name).read_text(encoding='utf-8-sig'))
files={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(root.rglob('*')) if p.is_file() and p.name!='REVIEW_PACKET_HASHES.json'}
manifest={'source_filename':'20261014_145449000_iOS.MP4',
    'source_sha256':'14396f74a5949fe27458a2758b2eee4fad952737ca96f20839be4a1e1d0458cf',
    'reviewer':'/root/ladder_145449','frozen_utc':datetime.now(timezone.utc).isoformat(),
    'files':files}
(root/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in files.items())
print(json.dumps({'frozen_files':len(files),'native_frames':len(list(evidence.glob('native_*.jpg'))),'hashes_verified':True}))
