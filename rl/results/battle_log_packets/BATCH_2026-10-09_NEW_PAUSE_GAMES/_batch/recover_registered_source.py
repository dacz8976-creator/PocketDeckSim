"""Recover packet metadata from a successful event without a shared-state write."""
import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('event',type=Path);a=ap.parse_args()
batch=Path(__file__).resolve().parent;root=batch.parent.parent
e=json.loads(a.event.read_text(encoding='utf-8-sig'))
name=e['video_basename'];source=root/name;packet=batch/Path(name).stem
assert name in json.loads((batch/'OWNER_CONTEXT.json').read_text())['selected_sources']
assert e['reviewer']=='/root/pause_'+Path(name).stem and e['status']=='in_progress'
assert e['identity_provenance']=='verified_by_cli_sha256' and e['video_sha256']
assert not (packet/'SOURCE.json').exists()
before=source.stat()
probe=json.loads(subprocess.check_output([r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe','-v','error',
    '-show_entries','format=duration:format_tags=creation_time:stream=width,height,codec_name,start_time',
    '-of','json',str(source)],timeout=40))
after=source.stat()
assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
assert after.st_size==e['video_bytes']
def save(name,value): (packet/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
save('SOURCE.json',{'video_basename':name,'sha256':e['video_sha256'],'bytes':e['video_bytes'],
    'duration_seconds':float(probe['format']['duration']),'streams':probe['streams'],
    'creation_time_utc':probe['format'].get('tags',{}).get('creation_time'),'source_path_at_review':str(source),
    'recording_relationships':[],'source_identity_basis':'Successful source-hashed CLI event; recovered after parent interruption; stable size/mtime during probe',
    'identity_verified_event_id':e['event_id'],'intake_utc':datetime.now(timezone.utc).isoformat(),
    'requested_log':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','classification':'awaiting_visual_verification'})
for t in (root/'Review_Log/templates/pause_games').glob('*.template.json'):
    target=packet/t.name.replace('.template','')
    if not target.exists():shutil.copy2(t,target)
shutil.copy2(root/'Review_Log/templates/pause_games/ASSIGNMENT.md',packet/'ASSIGNMENT.md')
save('ASSIGNMENT.json',{'reviewer':e['reviewer'],'review_model':'gpt-6.1-sol','reasoning_effort':'high',
    'scope':'Entire source, all recorded games and turns; mandatory Pause Games supplement','source_sha256':e['video_sha256'],
    'deck_snapshot':str(batch/'LIVE_DECK_SNAPSHOT.json'),'lead_only_shared_writes':True})
print(json.dumps({'source':name,'packet_recovered':True,'duration_seconds':float(probe['format']['duration'])}))
