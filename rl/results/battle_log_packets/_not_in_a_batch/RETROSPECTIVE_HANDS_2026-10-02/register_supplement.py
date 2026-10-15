"""Lead-only acceptance of separate supplements; preserves prior full review evidence."""
import argparse, csv, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

BATCH=Path(__file__).resolve().parent
ROOT=BATCH.parents[1]
p=argparse.ArgumentParser()
p.add_argument('stem')
p.add_argument('--check',required=True)
p.add_argument('--check-note',required=True)
p.add_argument('--retained-evidence-only',action='store_true')
a=p.parse_args()
name=a.stem+'_iOS.MP4'
inventory=json.loads((BATCH/'INVENTORY.json').read_text(encoding='utf-8-sig'))
entry=next((e for e in inventory['recordings'] if e['source']==name),None)
if entry is None:
    raise SystemExit('Source is outside the corrected owner-authorized batch.')
folder=BATCH/a.stem
checkpath=Path(a.check).resolve()
notepath=Path(a.check_note).resolve()
if not checkpath.is_relative_to(BATCH) or not notepath.is_relative_to(BATCH):
    raise SystemExit('Independent check must be inside this batch.')
check=json.loads(checkpath.read_text(encoding='utf-8-sig'))
verdict=check.get('verdict',check.get('final_verdict'))
if verdict is None and check.get('independent_acceptance') is True:
    verdict=check.get('status')
if verdict not in ['accepted','accepted_with_recording_limits']:
    raise SystemExit('Independent source acceptance is missing: '+str(verdict))
structure=json.loads((folder/'STRUCTURE_CHECK.json').read_text(encoding='utf-8-sig'))
if not structure['structure_passed']:
    raise SystemExit('Structural check failed.')
source=json.loads((folder/'SOURCE_REFERENCE.json').read_text(encoding='utf-8-sig'))
source_hash=source.get('sha256') or source.get('source_sha256')
for key in ['source_identity','source']:
    nested=source.get(key)
    if not source_hash and isinstance(nested,dict):
        source_hash=nested.get('sha256')
if not source_hash or len(source_hash)!=64:
    raise SystemExit('Frozen source SHA is missing.')
hand=json.loads((folder/'HAND_SUPPLEMENT.json').read_text(encoding='utf-8-sig'))
turns=structure['target_turn_numbers']
row=next(r for r in csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')) if r['Video']==name)
if row['Status']!='Reviewed':
    raise SystemExit('Shared status changed; coordinate before registering.')
acceptancepath=folder/'LEAD_ACCEPTANCE.json'
if acceptancepath.exists() and json.loads(acceptancepath.read_text()).get('shared_registration')=='complete':
    print(name+': already registered, skipped')
    raise SystemExit(0)
submitted=['REVIEW_SUPPLEMENT.md','HAND_SUPPLEMENT.json','TURN_EVIDENCE.json','UNCERTAINTIES.json','DECK_USED.json']
submitted += [n for n in ['PAUSE_GAME.json','TURN_LEDGER.json'] if (folder/n).is_file()]
missing=[n for n in submitted if not (folder/n).is_file()]
if missing:
    raise SystemExit('Missing submitted file(s): '+', '.join(missing))
scope=('Targeted uncertain owner hands only' if entry['group']=='sharpedo' else
       'Opening and first six owner hands; accepted remaining turns inherited' if entry['group']=='wailord' else
       'Setup and recorded-turn field additions; accepted battle outcome preserved')
acceptance={'schema':'retrospective-hand-lead-acceptance-v1','source':name,'source_sha256':source_hash,
 'accepted_at_utc':datetime.now(timezone.utc).isoformat(),'lead':'Codex retrospective lead',
 'worker_model':'gpt-6.1-sol','worker_effort':'high','independent_model':'gpt-6.1-sol','independent_effort':'high',
 'verdict':verdict,'target_turns':turns,'original_full_battle_status':'Reviewed; preserved','scope':scope,
 'independent_check':str(checkpath),'structure_check':str(folder/'STRUCTURE_CHECK.json'),
 'capture_status':hand.get('capture_status'),'source_read_basis':source.get('identity_verification_status',source.get('identity_provenance',source.get('current_hash_verification',source.get('source_identity_basis',source.get('verification_receipt'))))),
 'shared_registration':'pending','accepted_packet_hashes':{n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in submitted},
 'retained_evidence_only':a.retained_evidence_only}
acceptancepath.write_text(json.dumps(acceptance,indent=2),encoding='utf-8')
oldrefs=[]
for raw in row['Review evidence'].split('|'):
    old=raw.strip()
    if old.startswith('/mnt/c/'):
        old='C:/'+old[7:]
    if Path(old).is_file():
        oldrefs.append(Path(old))
if not oldrefs:
    raise SystemExit('No prior full-review evidence found; do not replace references.')
refs=oldrefs+[folder/n for n in submitted]+[folder/'SOURCE_REFERENCE.json',acceptancepath,checkpath,notepath]
classificationpath=folder/'CLASSIFICATION_RECEIPT.json'
if classificationpath.is_file():
    classification=json.loads(classificationpath.read_text(encoding='utf-8-sig'))
    acceptance['classification']=classification['classification']
    acceptance['excluded_from_ladder']=classification['excluded_from_ladder']
    refs.append(classificationpath)
    acceptancepath.write_text(json.dumps(acceptance,indent=2),encoding='utf-8')
for path in sorted((BATCH/'astra_checks'/a.stem).glob('*')):
    if path.is_file() and path.suffix.lower() in ['.json','.md']:
        refs.append(path)
refs=list(dict.fromkeys(str(r.resolve()) for r in refs))
notes=row['Notes']+' | Independently accepted separate retrospective field supplement, following corrected October 2 owner guide. Original accepted packet and outcome preserved. No duplicate external game or result changes.'
if acceptance.get('excluded_from_ladder'):
    notes+=' Confirmed computer battle under owner clarified visible-Auto-option rule; excluded from ladder, outcome retained separately in COMPUTER_BATTLE_HISTORY.md.'
if a.retained_evidence_only:
    notes += ' Uses source-bound retained evidence and saved source SHA; original video was not freshly read or rehashed for this supplement.'
command=[sys.executable,str(ROOT/'Review_Log/review_log.py'),'--root',str(ROOT),'record','--video',name,
 '--reviewer','Codex retrospective lead with Sol high workers and independent Sol high checks',
 '--status','full_battle_review_complete','--scope','Retains accepted full-battle review; '+scope,'--notes',notes]
if a.retained_evidence_only:
    command += ['--imported-saved-record','--known-sha256',source_hash]
for ref in refs:
    command += ['--evidence',ref]
run=subprocess.run(command,capture_output=True,text=True)
if run.returncode:
    (folder/'REGISTRATION_ERROR.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
    raise SystemExit('Registration failed: '+run.stderr.strip())
events=[]
for path in (ROOT/'Review_Log/events').glob('*.json'):
    event=json.loads(path.read_text(encoding='utf-8-sig'))
    if event.get('video_basename')==name:
        events.append((event['logged_at_utc'],path,event))
_,eventpath,event=max(events,key=lambda item:item[0])
if event['video_sha256'].lower()!=source_hash.lower():
    raise SystemExit('Registration source SHA differs!')
acceptance.update(shared_registration='complete',shared_event=str(eventpath),registration_identity_provenance=event['identity_provenance'])
acceptancepath.write_text(json.dumps(acceptance,indent=2),encoding='utf-8')
print(json.dumps({'source':name,'target_turns':turns,'registered_event':str(eventpath),'identity_provenance':event['identity_provenance'],'old_full_review_preserved':True}))
