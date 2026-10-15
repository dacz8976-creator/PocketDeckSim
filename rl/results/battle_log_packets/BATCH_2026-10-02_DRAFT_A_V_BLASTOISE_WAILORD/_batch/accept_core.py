import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import BATCH,read,sha,local,validate

parser=argparse.ArgumentParser();parser.add_argument('packet');parser.add_argument('check');parser.add_argument('--manifest',default='SUBMISSION.json');args=parser.parse_args()
p=Path(args.packet).resolve();assert p.parent==BATCH
s=read(p/'SOURCE.json');a=read(p/'ASSIGNMENT.json');v=read(p/'LEAD_VISUAL_CHECK.json');g=read(p/'GUIDE_UPDATE_ACCEPTANCE.json')
cp=local(p,args.check);c=read(cp)
assert v['source_video']==s['video_basename'] and v['source_sha256']==s['sha256']
assert c['accepted'] and c['full_review_coverage_checked'] and c['pause_contract_checked']
assert c['source_video']==s['video_basename'] and c['source_sha256']==s['sha256']
assert c['reviewer']!=a['reviewer'] and not c['remaining_coverage_gaps'] and not c['unverified_material_claims']
assert g['accepted'] and g['guide_update_checked'] and g['source_sha256']==s['sha256']
structural=validate(p,args.manifest)
assert c['checked_submission_manifest_sha256']==structural['submission_manifest_sha256']
assert c['checked_submission_files']==read(p/args.manifest)['files']
for e in v['evidence']:local(p,e)
lead={'accepted':True,'accepted_utc':datetime.now(timezone.utc).isoformat(),'accepted_by':'/root','source_video':s['video_basename'],'source_sha256':s['sha256'],'full_reviewer':a['reviewer'],'full_review_model':'gpt-6.1-sol','full_review_effort':'high','independent_reviewer':c['reviewer'],'independent_model':c['model'],'independent_effort':c.get('effort',c.get('reasoning_effort')),'independent_check':args.check,'independent_check_sha256':sha(cp),'submission_manifest':args.manifest,'submission_manifest_sha256':structural['submission_manifest_sha256'],'coverage_checked':True,'pause_contract_checked':True,'completion_status':'full_battle_review_complete','capture_status':'complete_with_recording_limits','remaining_coverage_gaps':[],'unverified_material_claims':[],'ranked_ladder_eligible':False,'human_pause_games_eligible':False,'requested_log':None,'actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX','scope':v['scope'],'outcome':v['outcome'],'lead_evidence':v['evidence']+[args.check,'ROUTING.json','GUIDE_UPDATE_ACCEPTANCE.json'],'lead_visual_check':v['observations'],'limits':c.get('recording_limits',c.get('limits',[])),'producer_files_preserved':True,'movie_archive_pending_at_acceptance':True}
assert not(p/'LEAD_ACCEPTANCE.json').exists()
(p/'LEAD_ACCEPTANCE.json').write_text(json.dumps(lead,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Root accepted full source and latest guide: '+s['video_basename'])
