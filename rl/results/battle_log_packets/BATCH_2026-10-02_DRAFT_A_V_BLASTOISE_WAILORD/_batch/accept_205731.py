import json
from datetime import datetime, timezone
from pathlib import Path
from validate_packet import read, sha, validate

packet=Path(__file__).resolve().parent/'20261002_205731000_iOS_auto_sol'
source=read(packet/'SOURCE.json');assignment=read(packet/'ASSIGNMENT.json')
check_path=packet/'independent_sol/CHECK_RESULT.json';check=read(check_path)
assert check['accepted'] and check['full_review_coverage_checked'] and check['pause_contract_checked']
assert not check['remaining_coverage_gaps'] and not check['unverified_material_claims']
assert check['source_sha256']==source['sha256']
structural=validate(packet)
assert check['checked_submission_manifest_sha256']==structural['submission_manifest_sha256']
assert check['checked_submission_files']==read(packet/'SUBMISSION.json')['files']
assert not(packet/'LEAD_ACCEPTANCE.json').exists()
lead={
    'accepted':True,'accepted_utc':datetime.now(timezone.utc).isoformat(),
    'accepted_by':'/root','source_video':source['video_basename'],'source_sha256':source['sha256'],
    'full_reviewer':assignment['reviewer'],'full_review_model':'gpt-6.1-sol','full_review_effort':'high',
    'independent_reviewer':check['reviewer'],'independent_model':check['model'],'independent_effort':check['effort'],
    'independent_check':'independent_sol/CHECK_RESULT.json','independent_check_sha256':sha(check_path),
    'submission_manifest':'SUBMISSION.json','submission_manifest_sha256':structural['submission_manifest_sha256'],
    'coverage_checked':True,'pause_contract_checked':True,
    'completion_status':'full_battle_review_complete','capture_status':'complete_with_recording_limits',
    'remaining_coverage_gaps':[],'unverified_material_claims':[],
    'ranked_ladder_eligible':False,'human_pause_games_eligible':False,'requested_log':None,
    'actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX','routing_basis':'ROUTING.json',
    'scope':'Complete source-bound computer battle from setup through Victory, all18game turns and full draw-timed hand/board capture supplement; local review only.',
    'outcome':{'result':'win','owner_points':3,'opponent_points':2,'turns':18,'damage_done':610,'went':'second'},
    'lead_evidence':['turn_evidence/t0013.90.jpg','turn_evidence/t0371.00.jpg','independent_sol/CHECK_RESULT.json','independent_sol/CHECK_RESULT.md','ROUTING.json'],
    'lead_visual_check':'Root visually checked the five-card opening, empty Active slot and Auto On; terminal Victory, computer deck title, went second,18turns,3-2points,610damage. Distinct independent Sol inspected ordinaryT6/T12 firstmoves, endinghands, draw/search order, fans, Energy and decisiveCyrus/KO; root reconciled those findings with frozen files.',
    'binding_snow_confirmation':'Independent source check explicitly confirms player/Active-position restriction, retained through opponent nextturn and cleared at each opponentturnend; no perPokemon persistence.',
    'limits':check.get('recording_limits',check.get('limits',[])),
    'producer_files_preserved':True,'movie_archive_pending_at_acceptance':True
}
(packet/'LEAD_ACCEPTANCE.json').write_text(json.dumps(lead,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Root accepted205731 with independent source evidence and local-only routing.')
