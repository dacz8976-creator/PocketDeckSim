"""Register root decisions only after independent source acceptance."""
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('packet',choices=['20261014_214436000_iOS','20261014_215114000_iOS','20261014_225451000_iOS','20261014_225802000_iOS','20261014_230328000_iOS','20261014_231006000_iOS','20261014_232438000_iOS','20261014_233402000_iOS','20261014_234511000_iOS','20261014_234728000_iOS','20261015_015320000_iOS','20261015_020931000_iOS','20261015_021533000_iOS','20261015_022206000_iOS'])
p.add_argument('--batch',choices=['BATCH_2026-10-14_EVENING_LADDER','BATCH_2026-10-14_LATE_LADDER_TWO','BATCH_2026-10-14_NEWER_LADDER_FOUR','BATCH_2026-10-14_NIGHT_LADDER_FOUR'],default='BATCH_2026-10-14_EVENING_LADDER')
a=p.parse_args()
BATCH=ROOT/'Recording_QA'/a.batch
if a.batch=='BATCH_2026-10-14_NIGHT_LADDER_FOUR':
    assert a.packet+'.MP4' in json.loads((BATCH/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
packet=BATCH/a.packet
def load(name):
    return json.loads((packet/name).read_text(encoding='utf-8-sig'))
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save_new(name,value):
    with (packet/name).open('x',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
source=load('SOURCE.json')
summary=load('SUMMARY.json')
manifest=load('REVIEW_PACKET_HASHES.json')
check=load('independent_sol/CHECK_RESULT.json')
decision=load('ROOT_DECISION.json')
assert check['accepted'] is True and decision['accepted'] is True
assert check['source_filename']==summary['source_filename']==decision['source_filename']==source['video_basename']
assert check['source_sha256']==summary['source_sha256']==decision['source_sha256']==source['sha256']
assert check['frozen_manifest_sha256']==digest(packet/'REVIEW_PACKET_HASHES.json')
assert check['frozen_files_match'] and check['primary_unchanged']
assert summary['battle_complete'] and summary['match_count']==1
assert decision['auto_option_seen'] is False
assert decision['note_prefix']==summary['exact_three_item_note_prefix']
assert decision['full_timeline_and_coverage_read'] is True
for rel,sha in manifest['files'].items():
    path=(packet/rel).resolve()
    assert path.is_relative_to(packet.resolve()) and digest(path)==sha,rel
supplemental_files={}
if (packet/'SUPPLEMENT_HASHES.json').exists():
    supplement=load('SUPPLEMENT_HASHES.json')
    assert supplement['original_manifest_sha256']==digest(packet/'REVIEW_PACKET_HASHES.json')
    for rel,sha in supplement['files'].items():
        path=(packet/rel).resolve()
        assert path.is_relative_to(packet.resolve()) and digest(path)==sha,rel
    supplemental_files={**supplement['files'],'SUPPLEMENT_HASHES.json':digest(packet/'SUPPLEMENT_HASHES.json')}
now=datetime.now(timezone.utc).isoformat()
observations=decision['direct_source_observations']
assert observations and all(o['directly_viewed_by_root'] is True for o in observations)
for o in observations:o['sha256']=digest(packet/o['path'])
save_new('SOURCE_CHECKS.json',{'lead':'/root','checked_utc':now,'source_filename':source['video_basename'],'source_sha256':source['sha256'],'observations':observations,'coverage_reconciliation':'Root read full timeline and turn/phase coverage; separate Sol reviewer checked decisive sequences and ordinary turns against retained source evidence.'})
save_new('LEAD_ACCEPTANCE.json',{'accepted':True,'decision':'accepted_full_battle_review','lead':'/root','accepted_utc':now,'source_video':source['video_basename'],'source_sha256':source['sha256'],'source_game_count':1,'all_source_games_accepted':True,'battle_complete':True,'archive_eligible':True,'scope':decision['scope'],'independent_acceptance':str(packet/'independent_sol/CHECK_RESULT.json'),'independent_acceptance_sha256':digest(packet/'independent_sol/CHECK_RESULT.json'),'accepted_input_sha256':manifest['files'],'supplemental_input_sha256':supplemental_files,'frozen_manifest_sha256':digest(packet/'REVIEW_PACKET_HASHES.json'),'root_checks':'SOURCE_CHECKS.json','clarifications':decision.get('clarifications',[])})
save_new('LADDER_ENTRY.json',{'source_filename':source['video_basename'],'source_sha256':source['sha256'],'section':decision['section'],'opponent':decision['opponent'],'opponent_deck':decision['opponent_deck'],'result':decision['result'],'note':decision['note'],'note_prefix':decision['note_prefix'],'match_creation_utc':source['source_creation_utc'],'artifact':'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1','status':'ready_for_live_save'})
cmd=[sys.executable,'-X','utf8',str(ROOT/'Review_Log/review_log.py'),'record','--video',source['video_basename'],'--reviewer',load('ASSIGNMENT.json')['reviewer'],'--status','full_battle_review_complete','--scope',decision['scope'],'--notes',decision['registration_notes'],'--recording-time',source['source_creation_utc']]
evidence=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','REVIEW_PACKET_HASHES.json','ROOT_DECISION.json','SOURCE_CHECKS.json','LEAD_ACCEPTANCE.json','LADDER_ENTRY.json','independent_sol/CHECK_RESULT.json']
if (packet/'LEAD_CLARIFICATION.md').exists():evidence.append('LEAD_CLARIFICATION.md')
if supplemental_files:evidence.extend(supplemental_files)
if (packet/'UNCERTAINTIES.md').exists():evidence.append('UNCERTAINTIES.md')
for name in evidence:cmd.extend(['--evidence',str(packet/name)])
r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
save_new('REGISTRATION_RESULT.json',{'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'registered_utc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'packet':a.packet,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},ensure_ascii=False),flush=True)
raise SystemExit(r.returncode)
