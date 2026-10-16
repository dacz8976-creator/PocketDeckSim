from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).parent
mp=P/'REVIEW_PACKET_HASHES.json'
m=json.loads(mp.read_text())
sfile=P/'SUMMARY.json'
s=json.loads(sfile.read_text(encoding='utf-8'))
s['source_filename']=s['video_basename']
sfile.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
entries=m['files']
for e in entries:
    if e['path']=='SUMMARY.json':
        e['sha256']=hashlib.sha256(sfile.read_bytes()).hexdigest()
        e['bytes']=sfile.stat().st_size
m['file_details']=entries
m['files']={e['path']:e['sha256'] for e in entries}
m['frozen_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
m['schema_normalization']='Lead-requested source_filename alias and mapping schema; no semantic review changes.'
mp.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
bad=[path for path,expected in m['files'].items() if hashlib.sha256((P/path).read_bytes()).hexdigest()!=expected]
assert not bad,bad
print(json.dumps({'frozen_files':len(m['files']),'hashes_verified':True,'source_filename':s['source_filename'],'manifest_sha256':hashlib.sha256(mp.read_bytes()).hexdigest()}))
