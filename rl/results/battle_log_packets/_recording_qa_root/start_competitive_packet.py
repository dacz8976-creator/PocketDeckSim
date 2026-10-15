"""Register exactly one source-bound competitive first-pass assignment."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from intake_competitive_20261002 import ROOT,BATCH,VIDEOS,packet_for,read,save,DESTINATION

SELECTED=VIDEOS[2:]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('video',choices=SELECTED)
    args=parser.parse_args()
    packet=packet_for(args.video)
    source=read(packet/'SOURCE.json')
    assert source['video_basename']==args.video
    reviewer='sol_competitive_20261002_'+args.video.split('_')[1]
    events=[read(path) for path in (ROOT/'Review_Log'/'events').glob('*.json')]
    prior=sorted((event for event in events if event.get('video_basename')==args.video),key=lambda event:event['logged_at_utc'])
    if prior:
        event=prior[-1]
        assert event['status']=='in_progress' and event['reviewer']==reviewer
    else:
        command=[sys.executable,str(ROOT/'Review_Log'/'review_log.py'),'--root',str(ROOT),'record','--video',args.video,'--reviewer',reviewer,'--status','in_progress','--scope','Entire owner-requested competitive battle: setup, every supplied turn and terminal result','--evidence',str(packet/'SOURCE.json'),'--notes','Owner requested competitive results in '+DESTINATION+'. Excluded from ranked Ladder Log. Lead alone accepts, logs externally and archives originals.']
        subprocess.run(command,check=True,capture_output=True,text=True,encoding='utf-8')
        events=[read(path) for path in (ROOT/'Review_Log'/'events').glob('*.json')]
        event=sorted((event for event in events if event.get('video_basename')==args.video),key=lambda event:event['logged_at_utc'])[-1]
    assert event['video_sha256']==source['sha256'] and event['video_bytes']==source['bytes']
    assignment={'video_basename':args.video,'source_sha256':source['sha256'],'reviewer':reviewer,'review_model':'gpt-6.1-sol','reasoning_effort':'high','recording_intent':'competitive_pause_games','requested_log':DESTINATION,'ranked_ladder_eligible':False,'identity_verified_event_id':event['event_id'],'assigned_utc':datetime.now(timezone.utc).isoformat(),'match_date_local':'2026-10-01','date_basis':'Owner says newly uploaded today; local upload date October 1 and recording phone clocks align with October 2 filename timestamps interpreted as UTC. Exact filename timezone is inferred, not printed.'}
    target=packet/'ASSIGNMENT.json'
    if target.exists():
        assert read(target)['source_sha256']==assignment['source_sha256']
    else:
        save(target,assignment)
    print(json.dumps(assignment),flush=True)

if __name__=='__main__':main()
