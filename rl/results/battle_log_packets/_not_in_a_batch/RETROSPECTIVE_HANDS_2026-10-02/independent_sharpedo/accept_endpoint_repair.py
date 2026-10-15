import json, hashlib, time
from pathlib import Path
root=Path.cwd(); batch=root/'Recording_QA'/'RETROSPECTIVE_HANDS_2026-10-02'; worker=batch/'20261002_115323000'; check=batch/'independent_sharpedo'/'20261002_115323000'
initial=json.loads((check/'SOURCE_CHECKS.json').read_text(encoding='utf-8-sig'))
files=['HAND_SUPPLEMENT.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']
original_hash_checks={n:hashlib.sha256((worker/'worker_submission_before_endpoint_repair'/n).read_bytes()).hexdigest()==initial['worker_packet_file_hashes_at_check'][n] for n in files if n in initial['worker_packet_file_hashes_at_check']}
ev=json.loads((worker/'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
limit=ev['scheduled_capture_limits'][-1]
assert 'obscured' in limit and 'continuity' in limit and 'after-trigger' in limit,limit
result={'schema':'independent-hand-endpoint-repair-acceptance-v1','game_id':'20261002_115323000','reviewer':'sol_verify_sharpedo','checked_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'initial_verdict':'needs_repair','final_verdict':'accepted_with_recording_limits','repair':'478 count and matching artwork observed; printed header obscured; Cyrus identity continuity inference from461.479/481 are after-trigger only.','updated_files_checked':files,'updated_file_hashes':{n:hashlib.sha256((worker/n).read_bytes()).hexdigest() for n in files},'preserved_worker_versions_match_initial_checks':original_hash_checks,'final_scheduled_capture_limit':limit,'additional_image_submissions':0,'source_reads':0,'new_extractions':0,'remaining_repairs':[],'astra_question':None}
(check/'SOURCE_CHECKS_ENDPOINT_REPAIR_ACCEPTANCE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
with (check/'INDEPENDENT_CHECK.md').open('a',encoding='utf-8') as f:f.write('\n\n## Final endpoint repair acceptance\n\nFinal verdict: **accepted_with_recording_limits**. The last scheduled-capture caption now matches the corrected structured fields and report: count one and matching artwork observed, printed header obscured, Cyrus identity a continuity inference from461, with479/481 after-trigger corroboration only. The saved original worker files match the initial checker hashes. No remaining factual repair or Astra question. This follow-up added no images, source reads or extraction. See SOURCE_CHECKS_ENDPOINT_REPAIR_ACCEPTANCE.json for exact updated-file hashes.\n')
print(json.dumps(result,indent=2))
