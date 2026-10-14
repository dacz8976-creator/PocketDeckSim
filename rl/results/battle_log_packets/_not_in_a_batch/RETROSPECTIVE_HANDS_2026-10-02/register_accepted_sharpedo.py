import argparse, csv, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

BATCH=Path(__file__).resolve().parent
ROOT=BATCH.parents[1]
p=argparse.ArgumentParser()
p.add_argument('stems',nargs='+')
a=p.parse_args()
allowed={'20261002_115323000','20261002_143837000'}
if any(stem not in allowed for stem in a.stems):
    raise SystemExit('Only the two independently accepted initial packets are authorized here.')
for stem in a.stems:
    folder=BATCH/stem
    checks=BATCH/'independent_sharpedo'/stem
    checkpath=checks/('SOURCE_CHECKS_ENDPOINT_REPAIR_ACCEPTANCE.json' if stem.endswith('115323000') else 'SOURCE_CHECKS.json')
    check=json.loads(checkpath.read_text(encoding='utf-8-sig'))
    verdict=check.get('verdict',check.get('final_verdict'))
    if verdict not in ['accepted','accepted_with_recording_limits']:
        raise SystemExit(f'{stem}: independent acceptance missing: {verdict}')
    structure=json.loads((folder/'STRUCTURE_CHECK.json').read_text(encoding='utf-8-sig'))
    if not structure['structure_passed']:
        raise SystemExit(f'{stem}: structural check failed')
    hand=json.loads((folder/'HAND_SUPPLEMENT.json').read_text(encoding='utf-8-sig'))
    name=stem+'_iOS.MP4'
    source_hash=hand.get('source_sha256',hand.get('sha256'))
    if not source_hash:
        source_hash=json.loads((checks/'SOURCE_CHECKS.json').read_text())['source_binding']['sha256']
    current_index=list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
    row=next(r for r in current_index if r['Video']==name)
    if row['Status']!='Reviewed':
        raise SystemExit(f'{name}: preserve/coordinate changed shared status first')
    turns=[r['turn_number'] for r in hand['turns']]
    acceptance={'schema':'retrospective-hand-lead-acceptance-v1','source':name,'source_sha256':source_hash,'accepted_at_utc':datetime.now(timezone.utc).isoformat(),'lead':'Codex retrospective lead','worker_model':'gpt-6.1-sol','worker_effort':'high','independent_model':'gpt-6.1-sol','independent_effort':'high','verdict':'accepted_with_recording_limits','target_turns':turns,'original_full_battle_status':'Reviewed; preserved','scope':'Owner-authorized targeted starting-hand additions only; accepted outcome, boards, points and unrelated turns unchanged','independent_check':str(checkpath),'structure_check':str(folder/'STRUCTURE_CHECK.json'),'capture_status':hand['capture_status'],'source_read_basis':'Worker verified current archived source SHA after OneDrive delivery; independent verifier reused retained native evidence','shared_registration':'pending','limits':'Exact frame PTS unmeasured; scheduled candidates after first play are unsuitable; qualified ending views preserved','accepted_packet_hashes':{n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ['HAND_SUPPLEMENT.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']}}
    acceptancepath=folder/'LEAD_ACCEPTANCE.json'
    if acceptancepath.exists() and json.loads(acceptancepath.read_text()).get('shared_registration')=='complete':
        print(f'{name}: already registered, skipped')
        continue
    acceptancepath.write_text(json.dumps(acceptance,indent=2),encoding='utf-8')
    oldrefs=[]
    for raw in row['Review evidence'].split('|'):
        old=raw.strip()
        if old.startswith('/mnt/c/'):
            old='C:/'+old[7:]
        if Path(old).is_file():
            oldrefs.append(Path(old))
    refs=oldrefs+[folder/'REVIEW_SUPPLEMENT.md',folder/'HAND_SUPPLEMENT.json',folder/'TURN_EVIDENCE.json',folder/'DECK_USED.json',acceptancepath,checkpath,checks/'INDEPENDENT_CHECK.md']
    refs=list(dict.fromkeys(str(r.resolve()) for r in refs))
    scope='Retains accepted full-battle review; independently accepted retrospective starting-hand supplement for owner turn(s) '+','.join(map(str,turns))
    notes=row['Notes']+' | Targeted hand supplement only, following corrected October 2 guide; new preplay identities directly observed; explicit capture limits and original worker attribution preserved. No duplicate external game or result changes.'
    command=[sys.executable,str(ROOT/'Review_Log/review_log.py'),'--root',str(ROOT),'record','--video',name,'--reviewer','Codex retrospective lead with Sol high workers and independent Sol high checks','--status','full_battle_review_complete','--scope',scope,'--notes',notes]
    for ref in refs:
        command += ['--evidence',ref]
    run=subprocess.run(command,capture_output=True,text=True)
    if run.returncode:
        (folder/'REGISTRATION_ERROR.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
        raise SystemExit(f'{name}: registration failed; acceptance saved and original Reviewed status retained. '+run.stderr.strip())
    events=[]
    for path in (ROOT/'Review_Log/events').glob('*.json'):
        event=json.loads(path.read_text(encoding='utf-8-sig'))
        if event.get('video_basename')==name:
            events.append((event['logged_at_utc'],path,event))
    _,eventpath,event=max(events,key=lambda item:item[0])
    if event['video_sha256'].lower()!=source_hash.lower():
        raise SystemExit(f'{name}: shared event source hash differs from packet!')
    acceptance['shared_registration']='complete'
    acceptance['shared_event']=str(eventpath)
    acceptance['cli_verified_sha256']=event['video_sha256']
    acceptancepath.write_text(json.dumps(acceptance,indent=2),encoding='utf-8')
    print(json.dumps({'source':name,'target_turns':turns,'registered_event':str(eventpath),'source_sha256_verified':True,'original_location':'Reviewed'}))
