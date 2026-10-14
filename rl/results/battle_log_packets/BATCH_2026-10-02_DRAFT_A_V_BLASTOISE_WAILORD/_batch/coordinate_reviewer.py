"""Reassign an unstarted packet to an available existing Sol worker."""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parser=argparse.ArgumentParser();parser.add_argument('packet');parser.add_argument('reviewer');args=parser.parse_args()
packet=Path(args.packet).resolve()
assert packet.parent==BATCH and not(packet/'SUBMISSION.json').exists()
assert not(packet/'LOCATOR_PREPROCESSING.json').exists(), 'Coordinate an active first pass explicitly before reassigning'
source=read(packet/'SOURCE.json');assignment=read(packet/'ASSIGNMENT.json')
rows=list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
row=next(r for r in rows if r['Video']==source['video_basename'])
assert row['Status']=='In progress'
history=packet/'assignment_history';history.mkdir(exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
save(history/(stamp+'.before.json'),assignment)
update={'coordinated_utc':datetime.now(timezone.utc).isoformat(), 'source_video':source['video_basename'],
        'source_sha256':source['sha256'], 'prior_planned_reviewer':assignment['reviewer'],
        'actual_reviewer':args.reviewer,'model':'gpt-6.1-sol','effort':'high',
        'reason':'Use an available existing Sol context for the bounded batch after its prior independent task is complete. No other worker has begun this source.',
        'identity_basis':'Previously verified SOURCE.json and intake event; assignment update does not claim a new media hash.',
        'actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX', 'external_game_entry_requested':False}
save(history/(stamp+'.coordination.json'),update)
command=[sys.executable,str(ROOT/'Review_Log/review_log.py'),'--root',str(ROOT),'record','--video',source['video_basename'],
         '--reviewer',args.reviewer,'--status','in_progress','--scope','Coordinated whole computer battle review under full capture protocol; local batch and index only',
         '--evidence',str(history/(stamp+'.coordination.json')),'--evidence',str(packet/'SOURCE.json'),
         '--imported-saved-record','--known-sha256',source['sha256'],'--correct','--notes',update['reason']+' Original verified source identity remains preserved. No external game entry.']
subprocess.run(command,check=True)
assignment.update({'reviewer':args.reviewer,'requested_log':None,'actual_destination':update['actual_destination'],
                   'assignment_update':str(history/(stamp+'.coordination.json')),'original_planned_reviewer':update['prior_planned_reviewer']})
save(packet/'ASSIGNMENT.json',assignment)
print(json.dumps(update,ensure_ascii=False))
