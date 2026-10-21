"""Return only the two Camera Roll sources hydrated during this intake to cloud storage."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from free_reviewed_video_space import metadata

root = Path(__file__).resolve().parent.parent
camera = Path(r'C:\Users\dacz8\OneDrive\Pictures\Camera Roll 1\2026\09').resolve()
batch = root / 'Recording_QA/BATCH_2026-09-30_EVENING'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
entries = []
for name in ['20261001_024952000_iOS.MP4','20261001_030109000_iOS.MP4']:
    packet = root / 'Recording_QA' / (Path(name).stem + '_auto_sol')
    source = read(packet / 'SOURCE.json')
    accepted = read(packet / 'LEAD_ACCEPTANCE.json')
    receipt = read(packet / f'MOVE_RECEIPT.{name}.json')
    assert accepted['accepted'] and not accepted['ladder_eligible'] and receipt['identity_match']
    assert source['sha256'] == accepted['source_sha256'] == receipt['sha256_after']
    target = (camera / name).resolve()
    assert target.parent == camera and target.is_file()
    before = metadata(target)
    assert before['logical_bytes'] == source['bytes']
    entry = {'video':name,'path':str(target),'before':before,'requested_online_only':False,'files_deleted':0}
    if not before['online_only']:
        if before['pinned']:
            entry['pending_reason'] = 'Existing Camera Roll pin preserved'
        elif not before['in_sync']:
            entry['pending_reason'] = 'Camera Roll sync pending; local data retained'
        else:
            digest = hashlib.sha256()
            with target.open('rb') as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b''):
                    digest.update(block)
            assert digest.hexdigest() == source['sha256'], 'Camera copy differs; preserve it'
            entry['matching_current_source_sha256'] = digest.hexdigest()
            current = metadata(target)
            assert current['in_sync'] and not current['pinned']
            attrib = str(Path(os.environ['SystemRoot']) / 'System32/attrib.exe')
            if current['unpinned']:
                subprocess.run([attrib,'-U','-P',str(target)],check=True)
                time.sleep(1)
            subprocess.run([attrib,'+U','-P',str(target)],check=True)
            entry['requested_online_only'] = True
    entries.append(entry)
deadline = time.monotonic()+5
while True:
    for entry in entries:
        entry['after'] = metadata(Path(entry['path']))
        assert entry['after']['logical_bytes'] == entry['before']['logical_bytes']
    if all(e['after']['online_only'] for e in entries) or time.monotonic() >= deadline:
        break
    time.sleep(1)
result = {'scope':'Two Camera Roll sources hydrated during intake; neither is an additional gameplay observation','entries':entries,'files_deleted':0,'archived_originals_rehashed':False}
(batch / 'CAMERA_CACHE_STORAGE.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'camera_sources':len(entries),'online_only':sum(e['after']['online_only'] for e in entries),'files_deleted':0}))
