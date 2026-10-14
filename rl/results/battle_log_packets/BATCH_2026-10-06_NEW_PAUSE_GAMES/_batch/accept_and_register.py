"""Lead-only completion, gated on a frozen independent acceptance receipt."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
b=Path(__file__).resolve().parent;root=b.parent.parent
ap=argparse.ArgumentParser();ap.add_argument('packet');a=ap.parse_args()
p=(b/a.packet).resolve();assert p.parent==b and p.is_dir()
if (p/'RELATED_GAME_PACKETS.json').exists():
    import runpy
    runpy.run_path(str(b/'accept_multi_game_source.py'),run_name='__main__')
    sys.exit(0)
def read(name):return json.loads((p/name).read_text(encoding='utf-8-sig'))
source=read('SOURCE.json');game=read('PAUSE_GAME.json');assignment=read('ASSIGNMENT.json')
assert not (p/'LEAD_ACCEPTANCE.json').exists(),'Existing lead disposition: inspect before updating'
receipt_path=p/'independent_sol/CORRECTION_RECHECK.json'
if not receipt_path.exists():receipt_path=p/'independent_sol/CHECK_RESULT.json'
independent=json.loads(receipt_path.read_text(encoding='utf-8'))
independent_accepted=independent.get('accepted') is True or ('accepted' not in independent and independent.get('status') in ('accepted','accepted_with_recording_limits'))
assert independent_accepted and not any(independent.get(k) for k in ('required_repairs','required_repairs_remaining','remaining_repairs')), 'Independent acceptance required'
assert independent['source_sha256']==source['sha256']
for name,digest in {**independent.get('checked_input_sha256',{}), **independent.get('supplemental_checked_input_sha256',{})}.items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,'Accepted input changed: '+name
verification=subprocess.run([sys.executable,str(b/'validate_packet.py'),str(p)],capture_output=True,text=True,encoding='utf-8',check=True)
structure=json.loads(verification.stdout)
(p/'ROOT_STRUCTURE_CHECK.json').write_text(json.dumps(structure,indent=2)+'\n',encoding='utf-8')
assert game['capture_status'] in ('complete','complete_with_recording_limits')
assert structure['turn_rows']>=0
if structure['turn_rows']==0:
    summary=read('SUMMARY.json')
    one_setup_game=summary.get('game_count')==1 or summary.get('recording_type')=='complete_setup_only_match_with_terminal_result'
    assert summary.get('turn_count')==0 and one_setup_game,'Zero-row packet requires an explicitly reviewed setup-only game'
    assert independent.get('zero_turn_terminal_verified') is True,'Independent setup-only terminal verification required'
shutil.copy2(p/'PAUSE_GAME.json',p/'PAUSE_GAME.before_lead_acceptance.json')
game['lead_checked']=True;game['battle_review_status']='full_battle_review_complete'
game['lead_acceptance']='LEAD_ACCEPTANCE.json'
(p/'PAUSE_GAME.json').write_text(json.dumps(game,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
acceptance={'accepted':True,'decision':'accepted_full_battle_review','lead':'/root','accepted_utc':datetime.now(timezone.utc).isoformat(),
    'source_video':source['video_basename'],'source_sha256':source['sha256'],'scope':'Whole supplied continuous battle: setup, all turns, terminal sequence and source ending',
    'capture_status':game['capture_status'],'turn_rows':structure['turn_rows'],'independent_acceptance':str(receipt_path),
    'basis':'Whole-source Sol review and coverage; separately commissioned bounded Sol checks of opening, ordinary turns/first moves, draws/searches, hands, both boards/Energy Zones, fans, decisive outcome; all frozen repairs independently verified. Root reconciled reports and inspected consequential boundary frames. Structure checked separately.',
    'source_limits':game.get('limits',[]),'outcome':game.get('outcome'),
    'external_status':'Prepared for Pause Games; no new live deck or game save claimed. Missing matching current live list is preserved, filmed QR definitions prepared separately.',
    'archive_authorization':'Completed local review may be safely archived after verified CLI registration; original bytes/name preserved.'}
(p/'LEAD_ACCEPTANCE.json').write_text(json.dumps(acceptance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
evidence=['REVIEW.md','COVERAGE.md','LEAD_ACCEPTANCE.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json',str(receipt_path.relative_to(p))]
cmd=[sys.executable,str(root/'Review_Log/review_log.py'),'--root',str(root),'record','--video',source['video_basename'],'--reviewer',assignment['reviewer'],
    '--status','full_battle_review_complete','--scope',f"Whole continuous battle, {structure['turn_rows']} turns, source ending, required Pause Games capture supplement; independently checked and root accepted"]
for file in evidence:cmd+=['--evidence',str(p/file)]
cmd+=['--notes','Root is sole shared writer. Whole-source Sol account and independent Sol acceptance preserved in packet. Explicit hidden/unrecorded information and missing current live deck version remain source limits; new filmed QR definitions prepared, external saving pending. No Ladder entry.']
result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
(p/'REGISTRATION_RESULT.json').write_text(json.dumps({'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'recorded_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n',encoding='utf-8')
assert result.returncode==0,result.stderr
print('Accepted and registered '+source['video_basename'])
