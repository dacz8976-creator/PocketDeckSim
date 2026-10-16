"""Bind only newly requested evening sources; bounded cloud reads."""
import argparse, csv, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
PROBE = 'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe'
p = argparse.ArgumentParser()
p.add_argument('video')
p.add_argument('--batch',choices=['BATCH_2026-10-14_EVENING_LADDER','BATCH_2026-10-14_LATE_LADDER_TWO','BATCH_2026-10-14_NEWER_LADDER_FOUR','BATCH_2026-10-14_NIGHT_LADDER_FOUR'],default='BATCH_2026-10-14_EVENING_LADDER')
a = p.parse_args()
BATCH=ROOT/'Recording_QA'/a.batch
assert Path(a.video).name == a.video
if a.batch=='BATCH_2026-10-14_NIGHT_LADDER_FOUR':
    context=json.loads((BATCH/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))
    assert a.video in context['selected_sources'] and a.video.startswith('20261015_')
else:
    assert a.video.startswith('20261014_')
source = ROOT / a.video
packet = BATCH / source.stem
packet.mkdir(parents=True, exist_ok=True)
def save(name, data):
    (packet / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
rows = list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
assert not any(r['Video'] == a.video for r in rows), 'Existing shared review record'
assert not (ROOT/'Reviewed'/a.video).exists(), 'Archive collision'
before = source.stat()
state = metadata(source)
save('INTAKE_METADATA.json', {'utc':datetime.now(timezone.utc).isoformat(), 'source':a.video, 'metadata':state})
print(json.dumps({'source':a.video,'metadata':state}), flush=True)
code = 'import sys;from pathlib import Path;f=Path(sys.argv[1]).open("rb");print(f.read(32).hex(),flush=True)'
try:
    read = subprocess.run([sys.executable,'-c',code,str(source)],capture_output=True,text=True,timeout=30)
except subprocess.TimeoutExpired:
    save('AVAILABILITY.json', {'readable':False,'reason':'32-byte read timed out after 30 seconds','utc':datetime.now(timezone.utc).isoformat()})
    print('SOURCE_READ_TIMEOUT', flush=True)
    sys.exit(2)
if read.returncode:
    save('AVAILABILITY.json', {'readable':False,'stderr':read.stderr,'utc':datetime.now(timezone.utc).isoformat()})
    print(read.stderr, flush=True)
    sys.exit(2)
probe = subprocess.run([PROBE,'-v','error','-show_format','-show_streams','-of','json',str(source)],capture_output=True,text=True,timeout=40)
assert probe.returncode == 0, probe.stderr
probe_data = json.loads(probe.stdout)
save('PROBE.json',probe_data)
time.sleep(2)
middle = source.stat()
assert (before.st_size,before.st_mtime_ns)==(middle.st_size,middle.st_mtime_ns), 'Upload still writing'
worker = ('/root/night_' if a.batch=='BATCH_2026-10-14_NIGHT_LADDER_FOUR' else '/root/evening_')+a.video[9:15]
registration = subprocess.run([sys.executable,'-X','utf8',str(ROOT/'Review_Log/review_log.py'),'record','--video',a.video,'--reviewer',worker,'--status','in_progress','--scope','Whole newly requested evening ladder recording, setup through result; every recorded turn, order, first main-attacker attack own turn and opponent points.','--notes','October 14 evening owner request. Root sole shared writer. Older backlog excluded.'],capture_output=True,text=True,encoding='utf-8',timeout=90)
save('ASSIGNMENT_REGISTRATION.json',{'exit_code':registration.returncode,'stdout':registration.stdout,'stderr':registration.stderr})
assert registration.returncode == 0, registration.stderr
event=json.loads(Path(registration.stdout.strip()).read_text(encoding='utf-8-sig'))
after=source.stat()
assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns), 'Source changed'
binding={'video_basename':a.video,'sha256':event['video_sha256'],'bytes':after.st_size,'duration_seconds':float(probe_data['format']['duration']),'streams':probe_data['streams'],'source_path_at_review':str(source),'bound_utc':event['logged_at_utc'],'identity_provenance':event['identity_provenance'],'recording_relationships':[],'source_creation_utc':probe_data['format'].get('tags',{}).get('creation_time'),'packet':str(packet)}
save('SOURCE.json',binding)
save('ASSIGNMENT.json',{'reviewer':worker,'model':'gpt-6.1-sol','reasoning_effort':'high','source_sha256':binding['sha256'],'assignment_event':event['event_id'],'scope':'Entire recording; ladder review, no Pause Games supplement','shared_write_authority':False,'external_write_authority':False})
save('AVAILABILITY.json',{'readable':True,'sha256_bound':True,'stable_size_mtime':True,'utc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({k:binding[k] for k in ['video_basename','sha256','bytes','duration_seconds','source_creation_utc','packet']}),flush=True)
