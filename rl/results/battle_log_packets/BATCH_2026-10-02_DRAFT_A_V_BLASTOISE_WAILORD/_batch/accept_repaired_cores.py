import json
from datetime import datetime,timezone
from validate_packet import BATCH,read,sha,validate

cases=[
 ('20261002_205230000_iOS_auto_sol',{'result':'win','owner_points':3,'opponent_points':0,'turns':16,'damage_done':580,'went':'second'},['turn_evidence/t0014.60.jpg','turn_evidence/t0277.50.jpg'],
 'Root directly inspected the five-card opening before Active placement with Auto enabled, terminal Victory/result table and the bounded repair evidence. Independent original full-coverage receipt plus distinct Sol repair recheck establishes all turns, player-level Binding Snow expiry, preplay boundary and named Carvanha reveal. Original submitted files and original rejection receipt remain preserved.'),
 ('20261002_210612000_iOS_auto_sol',{'result':'win','owner_points':3,'opponent_points':0,'turns':13,'damage_done':None,'went':'first'},['turn_evidence/t0015.00.jpg','turn_evidence/t0203.00.jpg','turn_evidence/t0049.40.jpg','turn_evidence/t0052.00.jpg','turn_evidence/t0124.50.jpg'],
 'Root directly inspected the five-card opening, terminal Victory, Cape HP count-up49.4 then settled180 at52.0, and turn9 handoff124.5 with expired restriction absent. Original independent full coverage plus distinct Sol bounded repair check establishes all13turns and3-0. Source ends before the detailed results table; damage total is not asserted. Original submitted files and original rejection receipt remain preserved.')]
for name,outcome,evidence,statement in cases:
 p=BATCH/name
 s=read(p/'SOURCE.json');a=read(p/'ASSIGNMENT.json')
 cpath=p/'independent_repair_sol/CHECK_RESULT.json';c=read(cpath)
 assert c['accepted'] and c['full_review_coverage_checked'] and c['pause_contract_checked']
 assert not c['remaining_coverage_gaps'] and not c['unverified_material_claims']
 assert c['source_sha256']==s['sha256'] and c['reviewer']!=a['reviewer']
 manifest='SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'
 v=validate(p,manifest)
 assert c['checked_submission_manifest_sha256']==v['submission_manifest_sha256']
 assert c['checked_submission_files']==read(p/manifest)['files']
 for item in evidence:assert (p/item).exists(),item
 lead={'accepted':True,'accepted_utc':datetime.now(timezone.utc).isoformat(),'accepted_by':'/root','source_video':s['video_basename'],'source_sha256':s['sha256'],'full_reviewer':a['reviewer'],'full_review_model':'gpt-6.1-sol','full_review_effort':'high','independent_reviewer':c['reviewer'],'independent_model':c['model'],'independent_effort':c.get('effort',c.get('reasoning_effort')),'independent_check':'independent_repair_sol/CHECK_RESULT.json','independent_check_sha256':sha(cpath),'submission_manifest':manifest,'submission_manifest_sha256':v['submission_manifest_sha256'],'coverage_checked':True,'pause_contract_checked':True,'completion_status':'full_battle_review_complete','capture_status':'complete_with_recording_limits','remaining_coverage_gaps':[],'unverified_material_claims':[],'ranked_ladder_eligible':False,'human_pause_games_eligible':False,'requested_log':None,'actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX','scope':f"Entire source-bound computer battle: setup, all{outcome['turns']} turns and terminal result, complete draw-timed Pause capture supplement and independently bounded preserved repairs; local only.",'outcome':outcome,'lead_evidence':evidence+['independent_repair_sol/CHECK_RESULT.json','ROUTING.json'],'lead_visual_check':statement,'limits':c['recording_limits'],'producer_files_preserved':True,'movie_archive_pending_at_acceptance':True}
 assert not(p/'LEAD_ACCEPTANCE.json').exists()
 (p/'LEAD_ACCEPTANCE.json').write_text(json.dumps(lead,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Root core accepted: '+s['video_basename']+'; guide acceptance separately required before archive.')
