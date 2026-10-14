"""Root-only acceptance of source-checked decisions for this exact resumed batch."""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
RUN=ROOT/'Recording_QA/BATCH_2026-10-14_LADDER_RESUME_FIVE'

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def save_new(path,value):
    assert not path.exists(),str(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

inventory=load(RUN/'SOURCE_INVENTORY.json')
p=argparse.ArgumentParser()
p.add_argument('video',choices=[s['video_basename'] for s in inventory])
a=p.parse_args()
source=next(s for s in inventory if s['video_basename']==a.video)
packet=Path(source['packet']).resolve()
assert packet.is_relative_to((ROOT/'Recording_QA').resolve())
assert load(packet/'SOURCE.json')==source
summary=load(packet/'SUMMARY.json')
decision=load(packet/'ROOT_DECISION.json')
manifest_path=packet/'REVIEW_PACKET_HASHES.json'
manifest=load(manifest_path)
check_path=packet/'independent_sol/CHECK_RESULT.json'
check=load(check_path)
assert check['accepted'] and check['frozen_files_match'] and check['primary_unchanged']
assert check['source_filename']==summary['source_filename']==source['video_basename']==decision['source_filename']
assert check['source_sha256']==summary['source_sha256']==source['sha256']==decision['source_sha256']
assert check['frozen_manifest_sha256']==digest(manifest_path)
assert summary['battle_complete'] and summary['match_count']==1
assert decision['battle_complete'] and decision['root_read_full_timeline_and_coverage']
assert decision['auto_option_seen'] is False
assert summary['exact_three_item_note_prefix']==decision.get('primary_note_prefix',decision['note_prefix'])
assert summary['outcome']==decision['result']
for rel,sha in manifest['files'].items():
    target=(packet/rel).resolve()
    assert target.is_relative_to(packet) and digest(target)==sha,rel
assert len(decision['observations'])>=3 and all(o['directly_viewed_by_root'] for o in decision['observations'])
for observation in decision['observations']:
    observation['sha256']=digest(packet/observation['path'])
now=datetime.now(timezone.utc).isoformat()
save_new(packet/'SOURCE_CHECKS.json',{'lead':'/root','checked_utc':now,'source_filename':a.video,
    'source_sha256':source['sha256'],'observations':decision['observations'],
    'full_timeline_coverage_read_by_root':True,'independent_source_check':str(check_path)})
save_new(packet/'LEAD_ACCEPTANCE.json',{'accepted':True,'decision':'accepted_full_battle_review','lead':'/root',
    'accepted_utc':now,'source_video':a.video,'source_sha256':source['sha256'],
    'source_game_count':1,'all_source_games_accepted':True,'battle_complete':True,'archive_eligible':True,
    'scope':decision['scope'],'independent_acceptance':str(check_path),
    'independent_acceptance_sha256':digest(check_path),'independent_model_configuration':'gpt-6.1-sol/high fresh compact source check',
    'accepted_input_sha256':manifest['files'],'frozen_manifest_sha256':digest(manifest_path),
    'root_decision':'ROOT_DECISION.json','root_checks':'SOURCE_CHECKS.json','clarifications':decision.get('clarifications',[])})
if (packet/'LEAD_CLARIFICATION.md').exists():
    save_new(packet/'ACCEPTED_ADDENDUM_HASHES.json',{'LEAD_CLARIFICATION.md':digest(packet/'LEAD_CLARIFICATION.md'),
        'ROOT_DECISION.json':digest(packet/'ROOT_DECISION.json'), 'SOURCE_CHECKS.json':digest(packet/'SOURCE_CHECKS.json')})
entry={'source_filename':a.video,'source_sha256':source['sha256'],'section':decision['section'],
       'deck_name':decision.get('deck_name'),'energy':decision.get('energy'),'opponent':decision['opponent'],
       'opponent_deck':decision['opponent_deck'],'result':decision['result'],'note':decision['note'],
       'note_prefix':decision['note_prefix'],'match_creation_utc':source['source_creation_utc'],
       'artifact':'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1','status':'ready_for_live_save'}
save_new(packet/'LADDER_ENTRY.json',entry)
cmd=[sys.executable,'-X','utf8',str(ROOT/'Review_Log/review_log.py'),'record','--video',a.video,
     '--reviewer',summary['reviewer'],'--status','full_battle_review_complete','--scope',decision['scope'],
     '--notes',decision['registration_notes'],'--recording-time',source['source_creation_utc']]
for name in ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','REVIEW_PACKET_HASHES.json',
             'ROOT_DECISION.json','SOURCE_CHECKS.json','LEAD_ACCEPTANCE.json','LADDER_ENTRY.json','independent_sol/CHECK_RESULT.json']:
    cmd.extend(['--evidence',str(packet/name)])
if (packet/'LEAD_CLARIFICATION.md').exists():
    cmd.extend(['--evidence',str(packet/'LEAD_CLARIFICATION.md')])
    cmd.extend(['--evidence',str(packet/'ACCEPTED_ADDENDUM_HASHES.json')])
r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
save_new(packet/'REGISTRATION_RESULT.json',{'registered_utc':datetime.now(timezone.utc).isoformat(),
    'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps({'video':a.video,'registered':r.returncode==0,'stdout':r.stdout,'stderr':r.stderr}),flush=True)
raise SystemExit(r.returncode)
