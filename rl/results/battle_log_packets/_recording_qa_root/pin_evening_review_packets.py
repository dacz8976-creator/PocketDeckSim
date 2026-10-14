"""Keep the eleven finished reports and their extracted evidence available locally."""
import json
import os
from pathlib import Path
import subprocess
from free_reviewed_video_space import metadata

root = Path(__file__).resolve().parent.parent
qa = (root / 'Recording_QA').resolve()
batch = qa / 'BATCH_2026-09-30_EVENING'
intake = json.loads((batch / 'INTAKE.json').read_text(encoding='utf-8-sig'))
attrib = str(Path(os.environ['SystemRoot']) / 'System32/attrib.exe')
entries = []
for item in intake['sources']:
    name = item['video']
    packet = (qa / (Path(name).stem + '_auto_sol')).resolve()
    assert packet.parent == qa and (packet / f'MOVE_RECEIPT.{name}.json').is_file()
    files = [p for p in packet.rglob('*') if p.is_file()]
    assert not any(p.suffix.lower() in ['.mp4','.mov','.mkv','.avi','.m4v'] for p in files), 'Source video found in report packet'
    subprocess.run([attrib,'+P','-U',str(packet / '*'),'/S','/D'],check=True)
    subprocess.run([attrib,'+P','-U',str(packet)],check=True)
    checks = []
    for doc in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
        state = metadata(packet / doc)
        assert state['pinned'] and state['allocated_bytes'] > 0 and not state['online_only'], doc
        checks.append({'file':doc,**state})
    images = [p for p in files if p.suffix.lower() in ['.jpg','.png']]
    assert images
    frame = images[0]
    state = metadata(frame)
    assert state['pinned'] and state['allocated_bytes'] > 0 and not state['online_only']
    entries.append({'video':name,'files_requested_local':len(files),'retained_images':len(images),'documents_verified':checks,'sample_frame_verified':{'file':str(frame.relative_to(packet)),**state}})
result = {'packets':len(entries),'scope':'Exact eleven accepted report packets, including retained extracted images; no original video target','entries':entries}
(batch / 'LOCAL_REPORT_STORAGE.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
for filename in ['BATTLE_TRANSCRIPTS_2026-09-30_EVENING.md','READ_ME_REVIEW_STATUS.md']:
    target = root / filename
    assert target.is_file()
    subprocess.run([attrib,'+P','-U',str(target)],check=True)
assert not any(p.suffix.lower() in ['.mp4','.mov','.mkv','.avi','.m4v'] for p in batch.rglob('*') if p.is_file())
subprocess.run([attrib,'+P','-U',str(batch / '*'),'/S','/D'],check=True)
subprocess.run([attrib,'+P','-U',str(batch)],check=True)
print(json.dumps({'packets':len(entries),'documents_verified':sum(len(e['documents_verified']) for e in entries),'retained_images_requested_local':sum(e['retained_images'] for e in entries)}))
