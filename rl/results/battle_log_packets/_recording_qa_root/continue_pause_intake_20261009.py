"""Continue serialized intake and recover a registered source after interruption."""
import csv
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone
import intake_pause_batch_20261006 as prior

root = Path(__file__).resolve().parent.parent
prior.BATCH = root / 'Recording_QA/BATCH_2026-10-09_NEW_PAUSE_GAMES'
names = json.loads((prior.BATCH/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
for name in names:
    packet = prior.BATCH / Path(name).stem
    if (packet/'SOURCE.json').exists():
        continue
    deadline = time.monotonic()+180
    while (root/'Review_Log/.write.lock').exists() and time.monotonic()<deadline:
        time.sleep(1)
    if (root/'Review_Log/.write.lock').exists():
        print('Active shared review write: deferred '+name,flush=True)
        break
    events = [json.loads(p.read_text(encoding='utf-8-sig')) for p in (root/'Review_Log/events').glob('*.json')]
    existing = [e for e in events if e.get('video_basename')==name]
    if not existing:
        prior.intake(name)
        continue
    e = max(existing,key=lambda e:e['logged_at_utc'])
    if e['reviewer'] != '/root/pause_'+Path(name).stem or e['status'] != 'in_progress':
        print('Other assignment: deferred '+name,flush=True)
        continue
    source = root/name
    before=source.stat()
    probe=json.loads(subprocess.check_output([prior.PROBE,'-v','error','-show_entries','format=duration:stream=width,height,codec_name,start_time','-of','json',str(source)],timeout=60))
    after=source.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    assert after.st_size==e['video_bytes']
    prior.save(packet/'SOURCE.json',{'video_basename':name,'sha256':e['video_sha256'],'bytes':e['video_bytes'],
        'duration_seconds':float(probe['format']['duration']),'streams':probe['streams'],'source_path_at_review':str(source),
        'recording_relationships':[],'source_identity_basis':'Recovered exact successful CLI registration event after parent interruption; size stable during probe',
        'identity_verified_event_id':e['event_id'],'intake_utc':datetime.now(timezone.utc).isoformat(),
        'requested_log':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','classification':'awaiting_visual_verification'})
    for template in (root/'Review_Log/templates/pause_games').glob('*.template.json'):
        target=packet/template.name.replace('.template','')
        if not target.exists(): shutil.copy2(template,target)
    shutil.copy2(root/'Review_Log/templates/pause_games/ASSIGNMENT.md',packet/'ASSIGNMENT.md')
    prior.save(packet/'ASSIGNMENT.json',{'reviewer':e['reviewer'],'review_model':'gpt-6.1-sol','reasoning_effort':'high',
        'scope':'Entire source, all games and turns, mandatory Pause Games supplement','source_sha256':e['video_sha256'],
        'deck_snapshot':str(prior.BATCH/'LIVE_DECK_SNAPSHOT.json'),'lead_only_shared_writes':True})
    print(json.dumps({'source':name,'recovered':True,'duration_seconds':float(probe['format']['duration'])}),flush=True)
