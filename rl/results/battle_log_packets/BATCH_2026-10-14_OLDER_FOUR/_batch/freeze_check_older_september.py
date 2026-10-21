import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

specs = {
    '20260926_211809000_iOS': {
        'seconds': [0,8,13,20,24,27,34,36.5,38,43.4],
        'paths': ['evidence/native_' + f'{s:06.3f}'.replace('.', 'p') + 's.jpg' for s in [0,8,13,20,24,27,34,36.5,38,43.4]],
        'opponent': 'XaBy8', 'duration': 43.463333,
        'critical': {'beginning':'evidence/native_00p000s.jpg', 'second_point':'evidence/native_20p000s.jpg', 'concession':'evidence/native_38p000s.jpg', 'victory':'evidence/native_43p400s.jpg'},
        'missing': ['Opening/setup', 'Earlier turns/development', 'First owner point'],
        'score': {'owner':2,'opponent':0},
    },
    '20260926_212155000_iOS': {
        'seconds': [0,6,48,72,101.5,113,124.5,131.5,133,165,175,177,186,198,199.5,201,203.5,204,205.55],
        'paths': ['evidence/t' + f'{s:07.2f}' + '.jpg' for s in [0,6,48,72,101.5,113,124.5,131.5,133,165,175,177,186,198,199.5,201,203.5,204,205.55]],
        'opponent':'StefaGo', 'duration':205.771927,
        'critical': {'beginning':'evidence/t0000.00.jpg','initial_turn2_banner':'evidence/t0006.00.jpg', 'last_score':'evidence/t0198.00.jpg', 'concession':'evidence/t0199.50.jpg', 'concession_retained':'evidence/t0201.00.jpg', 'victory':'evidence/t0203.50.jpg', 'victory_tap_to_proceed':'evidence/t0204.00.jpg','pale_tail':'evidence/t0205.55.jpg'},
        'missing': ['Opening hand/setup','Initial owner Basic placement sequence','Earlier already-discarded Poké Ball play','Beginning of initial owner turn'],
        'score': {'owner':2,'opponent':1},
    }
}

for name, spec in specs.items():
    packet = BATCH / name
    out = packet / 'independent_sol'
    initial = json.loads((out/'INTEGRITY_INITIAL.json').read_text())
    final = json.loads((out/'INTEGRITY_FINAL.json').read_text())
    unchanged = (initial['files_checked'] == final['files_checked'] and
                 initial['frozen_manifest_sha256'] == final['frozen_manifest_sha256'] and
                 initial['evidence_manifest_sha256'] == final['evidence_manifest_sha256'] and
                 initial['source_sha256'] == final['source_sha256'])
    assert unchanged and initial['all_frozen_entries_match'] and final['all_frozen_entries_match']
    lookup = {entry['path']:entry for entry in final['files_checked']}
    inspected = []
    for sec, path in zip(spec['seconds'],spec['paths']):
        e = lookup[path]
        inspected.append({'path':path,'source_elapsed_seconds':sec,'sha256':e['sha256'],'bytes':e['bytes'], 'dimensions':[1170,2532]})
    result = {
        'schema_version':1, 'reviewer':'/root/check_older_september',
        'reviewer_role':'separate Sol bounded independent acceptance reviewer',
        'model_configuration':'inherited parent configuration; no override',
        'checked_utc':datetime.now(timezone.utc).isoformat(),
        'decision':'accepted_available_footage_packet', 'material_repairs_required':[],
        'source_basename':name+'.MP4', 'source_path':final['source_path'],
        'source_sha256_initial':initial['source_sha256'], 'source_sha256_final':final['source_sha256'],
        'source_bytes':final['source_bytes'], 'source_duration_seconds':spec['duration'],
        'initial_integrity_receipt':'INTEGRITY_INITIAL.json','final_integrity_receipt':'INTEGRITY_FINAL.json',
        'frozen_primary_manifest_sha256_initial':initial['frozen_manifest_sha256'],
        'frozen_primary_manifest_sha256_final':final['frozen_manifest_sha256'],
        'evidence_manifest_sha256_initial':initial['evidence_manifest_sha256'],
        'evidence_manifest_sha256_final':final['evidence_manifest_sha256'],
        'all_frozen_entries_match':True, 'frozen_entries_checked':len(final['files_checked']),
        'primary_packet_unchanged_between_checks':unchanged,
        'inspected_source_bound_native_evidence':inspected,
        'critical_evidence':spec['critical'],
        'available_footage_review_accepted':True, 'available_footage_review_complete':True,
        'available_footage_interval_seconds':[0,spec['duration']],
        'independent_check_scope':'Bounded selected beginning, ordinary actions, consequential states and terminal evidence; not a second full visual pass',
        'battle_complete':False, 'recommended_machine_status':'partial',
        'recommended_index_status':'Needs full battle review', 'archive_eligible':False,
        'missing_pre_source_phases':spec['missing'],
        'entirely_absent_completed_turns_established':False if spec['opponent']=='StefaGo' else None,
        'owner':'Dacz8976','opponent':spec['opponent'], 'owner_result':'win',
        'result_method':'explicit_opponent_concession', 'victory_splash_verified':True,
        'last_visible_score':spec['score'], 'actual_queue':'unknown',
        'auto_control_established':False, 'auto_enabled':None,
        'mode_limit':'Bounded evidence lacks an established Auto control; absence does not independently prove PvP or ranked',
        'external_route':'Owner-default Ladder candidate, live source-filename duplicate verification pending with lead',
        'live_external_duplicates_checked':False, 'shared_registration_written':False,
        'media_moved':False,'external_log_written':False,'mirror_written':False,
        'primary_files_edited':False, 'notes':'CHECK_NOTES.md',
    }
    target=out/'CHECK_RESULT.json'
    assert not target.exists()
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    own_files=[]
    for filename in ('CHECK_RESULT.json','CHECK_NOTES.md','INTEGRITY_INITIAL.json','INTEGRITY_FINAL.json'):
        p=out/filename
        own_files.append({'path':filename,'sha256':sha(p),'bytes':p.stat().st_size})
    freeze=out/'CHECK_RECEIPT_HASHES.json'
    assert not freeze.exists()
    freeze.write_text(json.dumps({'frozen_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/check_older_september','source_sha256':final['source_sha256'],'self_excluded':True,'files':own_files},indent=2)+'\n',encoding='utf-8')
    print(name, 'acceptance receipt frozen:', sha(freeze))
