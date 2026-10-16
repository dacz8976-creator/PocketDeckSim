import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).parent
primary=[p/n for n in ['SOURCE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']]
for f in primary:
    if f.suffix=='.json':
        json.loads(f.read_text(encoding='utf-8-sig'))
frames=sorted(p.rglob('*.jpg'))
entries=[]
for f in primary+frames:
    entries.append({'path':f.relative_to(p).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
r={'schema_version':1,'frozen_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/offline_ladder_160506','source_filename':'20261014_160506000_iOS.MP4','source_sha256':'65a94f2a9cfcfc69d5bcbb9f11e2a5d1fd045daeb7c6fea703f20454e174239b','scope':'Completed primary JSON/prose and all retained native/overview/evidence/viewing-aid JPG files; excludes helper scripts and this manifest','primary_file_count':len(primary),'retained_jpg_count':len(frames),'files':entries}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'primary_files':len(primary),'retained_jpgs':len(frames),'hashed_files':len(entries)}))
