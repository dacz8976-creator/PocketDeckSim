"""Source-bound intake of two recordings from one owner-declared computer test."""
import csv,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from batch_rules_20261001 import ROOT,PROBE,read,save

VIDEOS=['20261002_161001000_iOS.MP4','20261002_161342000_iOS.MP4']
BATCH=ROOT/'Recording_QA'/'BATCH_2026-10-02_CAREFREE_SNIPES'
REVIEWER='sol_rules_20261002_carefree_steps'
OWNER='Two recordings of one computer battle; recording cut out. Rules test of coin-flip damage prevention against targeted attacks. Exclude Pause Games and Ladder Log.'

def main():
    BATCH.mkdir(exist_ok=True)
    if not (BATCH/'INDEX_BEFORE.json').exists():save(BATCH/'INDEX_BEFORE.json',list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline=''))))
    for name in VIDEOS:
        video=ROOT/name;before=video.stat()
        subprocess.run(['attrib','+P','-U',str(video)],check=True,capture_output=True,text=True)
        probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_entries','format=duration:stream=width,height,codec_name','-of','json',str(video)],timeout=300))
        events=[read(p) for p in (ROOT/'Review_Log'/'events').glob('*.json')]
        prior=sorted((e for e in events if e.get('video_basename')==name),key=lambda e:e['logged_at_utc'])
        if prior:
            event=prior[-1];assert event['status']=='in_progress' and event['reviewer']==REVIEWER
        else:
            subprocess.run([sys.executable,str(ROOT/'Review_Log'/'review_log.py'),'--root',str(ROOT),'record','--video',name,'--reviewer',REVIEWER,'--status','in_progress','--scope','Entire available recording, one of two parts of a single computer rules test','--notes',OWNER],check=True,capture_output=True,text=True,encoding='utf-8')
            events=[read(p) for p in (ROOT/'Review_Log'/'events').glob('*.json')];event=max((e for e in events if e.get('video_basename')==name),key=lambda e:e['logged_at_utc'])
        after=video.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        packet=ROOT/'Recording_QA'/(video.stem+'_rule_sol');packet.mkdir(exist_ok=True)
        source={'video_basename':name,'sha256':event['video_sha256'],'bytes':before.st_size,'duration_seconds':float(probe['format']['duration']),'streams':probe['streams'],'source_path_at_review':str(video),'recording_relationships':[{'other_source':other,'basis':'Owner says two parts of one battle; visual continuity must be checked','visual_continuity_verified':False} for other in VIDEOS if other!=name],'recording_date_basis':'October 2 filename and owner upload; exact filename timezone unverified','owner_testimony':OWNER,'recording_intent':'rules_testing','mode':'computer battle per owner, verify from footage','ladder_eligible':False,'pause_games_eligible':False,'reviewer':REVIEWER,'review_model':'gpt-6.1-sol','reasoning_effort':'high','identity_verified_event_id':event['event_id'],'intake_utc':datetime.now(timezone.utc).isoformat()}
        if (packet/'SOURCE.json').exists():assert read(packet/'SOURCE.json')['sha256']==source['sha256']
        else:save(packet/'SOURCE.json',source)
        assignment={**source,'worker_task':'One fresh Sol high worker reviews both source-bound recordings as one battle; no guessing across the recording interruption','expected_recordings':2,'expected_battles':1,'requested_log':None,'simulator_scope':'Compare filmed behavior with the user quoted engine prediction; no source edits or training'}
        if not (packet/'ASSIGNMENT.json').exists():save(packet/'ASSIGNMENT.json',assignment)
        print(name+' verified '+source['sha256']+'; '+str(source['duration_seconds'])+' seconds',flush=True)
    save(BATCH/'INTAKE.json',{'sources':[read(ROOT/'Recording_QA'/(Path(n).stem+'_rule_sol')/'SOURCE.json') for n in VIDEOS],'owner_instruction':OWNER,'recordings':2,'battles':1,'pause_games_eligible':False,'ladder_eligible':False})

if __name__=='__main__':main()
