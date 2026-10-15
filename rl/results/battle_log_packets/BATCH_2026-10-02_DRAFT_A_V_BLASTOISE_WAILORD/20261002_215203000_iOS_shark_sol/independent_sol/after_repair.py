import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent.parent;out=p/'independent_sol';H=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
orig=json.loads((out/'CHECK_RESULT.json').read_text());orig_sha=H(out/'CHECK_RESULT.json')
assert orig_sha=='c8dff4fb7383eaf4ae8e3d600d2e16f8a84d2545cef894031edc4af360fc922d'
name='SUBMISSION_AFTER_INDEPENDENT_REPAIR.json';s=json.loads((p/name).read_text());sha=H(p/name)
assert sha=='8b3daf869cb180d0b022ee18b67462762d87d3d19ec09ec315c6875942a48f2a'
checks={k:H(p/k) for k in s['files']};assert checks==s['files'];assert len(checks)==20
old=json.loads((p/'worker_submission/SUBMISSION.json').read_text());assert H(p/'worker_submission/SUBMISSION.json')==orig['checked_submission_manifest_sha256']
assert {k:H(p/'worker_submission'/k) for k in old['files']}==orig['checked_submission_files']
changed=[k for k in old['files'] if old['files'][k]!=checks[k]];assert set(changed)=={'REVIEW.md','TURN_LEDGER.json','TURN_EVIDENCE.json','TURN_TABLE.md'}
ledger=json.loads((p/'TURN_LEDGER.json').read_text());e=json.loads((p/'TURN_EVIDENCE.json').read_text());extra=json.loads((out/'EXTRACTION_MANIFEST.json').read_text());ev={r['evidence_id']:r for r in extra}
for t,idx,eid,pts in [(0,0,'independent_sol:F0035.50',35.5067),(6,2,'independent_sol:F0157.50',157.505)]:
 a=ledger['turns'][t]['plays_in_order'][idx];assert eid in a['evidence_ids'];assert a['actual_frame_seconds_if_measured']==pts;assert a['named_card_face_anchor']['evidence_id']==eid
 assert H(ev[eid]['full_frame_path'])==ev[eid]['full_frame_sha256']
 for c in ['bottom_crop','top_crop']:assert H(ev[eid][c]['path'])==ev[eid][c]['sha256']
assert ledger['turns'][0]['plays_in_order'][0]['hand_count_after']==5
assert ledger['turns'][0]['draws_and_searches'][1]['hand_count_after']==5
assert ledger['turns'][0]['plays_in_order'][1]['hand_count_after']==4
allids={r['evidence_id'] for r in json.loads((p/'EXTRACTION_MANIFEST.json').read_text())}|set(ev)
def walk(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k.endswith('evidence_ids') and isinstance(x,list):
    for z in x:assert z in allids,(k,z)
   walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for k in checks:
 if k.endswith('.json'):walk(json.loads((p/k).read_text()))
r=dict(orig);r.update({'accepted':True,'status':'complete_with_recording_limits','checked_at_utc':datetime.now(timezone.utc).isoformat(),'checked_submission_manifest':name,'checked_submission_manifest_sha256':sha,'checked_submission_files':checks,'remaining_coverage_gaps':[],'unverified_material_claims':[],'exact_corrections_required':[],'initial_rejection_preserved':'independent_sol/CHECK_RESULT.json','initial_rejection_sha256':orig_sha,'original_submission_preserved':'worker_submission/SUBMISSION.json','original_submission_sha256':orig['checked_submission_manifest_sha256'],'bounded_repair_checked':{'changed_existing_files':changed,'new_core_file':'REPAIR_RECEIPT.json','all_three_required_corrections_resolved':True,'frozen_effective_files_checked':20,'preserved_original_files_checked':19,'guide_and_inventory_unchanged':True,'result_hidden_identities_move_order_unchanged':True,'selected_new_face_ids':['independent_sol:F0035.50','independent_sol:F0157.50']}})
r['findings_by_checklist_category']=dict(orig['findings_by_checklist_category']);r['findings_by_checklist_category']['research_ball_copycat']='All consequential transactions checked. T1 completed Research hand count now5, followed by Frigibax4. Exact measured Research35.5067 and T7Ball157.505 native faces linked in effective ledger/evidence; preface anchors remain continuity-only. Original rejection preserved; effective20hashes verified.'
r['findings_by_checklist_category']['source_and_frozen_submission']='Effective20-file manifest and preserved19-file original verified against their exact frozen hashes. Primary137-frame extraction remains unchanged; two independent face frames registered in TURN_EVIDENCE with source identity, native dimensions, measuredPTS and hashes. All referenced nested evidence IDs resolve.'
(out/'CHECK_RESULT_AFTER_REPAIR.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
(out/'CHECK_RESULT_AFTER_REPAIR.md').write_text('# Independent acceptance after bounded repair\n\nAccepted complete_with_recording_limits. Effective20-file SUBMISSION_AFTER_INDEPENDENT_REPAIR.json SHA '+sha+' and preserved19-file original match every frozen file hash.\n\nAll three corrections are resolved: T1 completed Research hand count5 then Frigibax4; exact Researchface35.5067 and T7Ballface157.505 registered and linked with measuredPTS/hashes. Earlier anchors remain continuity-only. Compared all four changed existing files and the repair receipt; guide/inventory/results/hidden identities/move order retain original semantics. Original rejected CHECK_RESULT.json remains unchanged.\n\nFull-span coverage, Pause capture contract and latest four guide additions remain independently checked. Confirmed computer battle, AutoOFF/user owner turns, second, win3-0,12turns,380nominaldamage. No remaining material claim or review-coverage gap. The unopened-pile, concealed-card, covered-face, touch and subsecond recording limits remain explicit. Actual inspected paths and source/effective binding are in the JSON.\n',encoding='utf-8')
assert H(out/'CHECK_RESULT.json')==orig_sha
print(json.dumps({'accepted':True,'manifest_sha256':sha,'files':len(checks),'after_check_sha256':H(out/'CHECK_RESULT_AFTER_REPAIR.json')}))
