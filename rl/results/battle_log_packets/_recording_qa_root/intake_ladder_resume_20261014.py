"""Resume three now-readable sources and bind two newly authorized uploads."""
import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT/'Recording_QA/BATCH_2026-10-14_NEW_LADDER_FOUR'
NEW = ROOT/'Recording_QA/BATCH_2026-10-14_ADDITIONAL_TWO'
RESUME = ROOT/'Recording_QA/BATCH_2026-10-14_LADDER_RESUME_FIVE'
SELECTED = ['20261014_143111000_iOS.MP4','20261014_144627000_iOS.MP4','20261014_145449000_iOS.MP4',
            '20261014_153139000_iOS.MP4','20261014_153908000_iOS.MP4']
PROBE = 'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe'

def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for folder in [NEW,RESUME]:
    folder.mkdir(exist_ok=True)
    if not (folder/'REVIEW_ASSIGNMENT.md').exists():
        shutil.copy2(OLD/'REVIEW_ASSIGNMENT.md',folder/'REVIEW_ASSIGNMENT.md')
with (ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
if not (RESUME/'OWNER_CONTEXT.json').exists():
    save(RESUME/'OWNER_CONTEXT.json',{'requested_utc':datetime.now(timezone.utc).isoformat(),
        'owner_request':'They should be available to you now. Also added two more.',
        'selected_sources':SELECTED,'previous_completed_source':'20261014_142546000_iOS.MP4',
        'scope':'Finish three original pending ladder games and two additional ladder uploads. Preserve previous accepted first game and season history.',
        'artifact':'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1',
        'note_contract':'First/second | main attacker first attack own turn | opponent points before that attack. Supporting earlier attacks remain separate.',
        'shared_writes':'Root alone writes events/index/artifact/archive/location map/Boss mirror.'})
    save(RESUME/'INDEX_BEFORE.json',rows)
if not (NEW/'OWNER_CONTEXT.json').exists():
    save(NEW/'OWNER_CONTEXT.json',{'requested_utc':datetime.now(timezone.utc).isoformat(),
        'selected_sources':SELECTED[3:],'routing':'New ladder uploads, same owner contracts as original October14 batch.',
        'artifact':'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1'})
inventory=[]
for i,name in enumerate(SELECTED):
    batch=OLD if i<3 else NEW
    packet=batch/Path(name).stem
    packet.mkdir(exist_ok=True)
    if (packet/'SOURCE.json').exists():
        inventory.append(json.loads((packet/'SOURCE.json').read_text(encoding='utf-8-sig')))
        continue
    prior=next((r for r in rows if r['Video']==name),None)
    assert prior is None, prior
    path=ROOT/name
    assert path.is_file() and not (ROOT/'Reviewed'/name).exists()
    before=path.stat()
    cloud=metadata(path)
    assert cloud['allocated_bytes']==before.st_size and not cloud['online_only']
    save(packet/'AVAILABILITY_RECOVERED.json',{'utc':datetime.now(timezone.utc).isoformat(),'cloud_metadata':cloud,
        'prior_cloud_errors_preserved':True,'owner_reports_now_available':True})
    probe=json.loads(subprocess.run([PROBE,'-v','error','-show_format','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True,timeout=45).stdout)
    save(packet/'PROBE.json',probe)
    worker='/root/ladder_'+name[9:15]
    r=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'Review_Log/review_log.py'),'record','--video',name,
        '--reviewer',worker,'--status','in_progress','--scope','Whole ladder source: setup, every turn, ending; order, main first attack own turn and opponent points.',
        '--notes','Owner resumed now-readable files and added two uploads. No older backlog; root sole shared writer.'],capture_output=True,text=True,encoding='utf-8',timeout=90)
    save(packet/'ASSIGNMENT_REGISTRATION.json',{'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    assert r.returncode==0,r.stderr
    event=json.loads(Path(r.stdout.strip()).read_text(encoding='utf-8-sig'))
    after=path.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    binding={'video_basename':name,'sha256':event['video_sha256'],'bytes':after.st_size,
        'duration_seconds':float(probe['format']['duration']),'streams':probe['streams'],
        'source_path_at_review':str(path),'bound_utc':event['logged_at_utc'],
        'identity_provenance':event['identity_provenance'],'recording_relationships':[],
        'source_creation_utc':probe['format'].get('tags',{}).get('creation_time'),'packet':str(packet)}
    save(packet/'SOURCE.json',binding)
    save(packet/'ASSIGNMENT.json',{'reviewer':worker,'model':'gpt-6.1-sol','reasoning_effort':'high',
        'source_sha256':binding['sha256'],'assignment_event':event['event_id'],
        'scope':'Entire source ordinary ladder full review. No Pause Games supplement.',
        'shared_write_authority':False,'external_write_authority':False})
    inventory.append(binding)
    print(json.dumps({k:binding[k] for k in ['video_basename','sha256','bytes','duration_seconds','source_creation_utc','packet']}),flush=True)
    save(RESUME/'SOURCE_INVENTORY.json',inventory)
save(NEW/'SOURCE_INVENTORY.json',inventory[3:])
