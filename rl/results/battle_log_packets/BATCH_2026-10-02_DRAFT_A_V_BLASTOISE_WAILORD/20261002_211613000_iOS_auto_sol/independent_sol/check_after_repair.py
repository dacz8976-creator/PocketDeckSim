import json, hashlib, copy
from pathlib import Path
from datetime import datetime, timezone
p=Path(__file__).resolve().parent.parent
out=Path(__file__).resolve().parent
def read(f): return json.loads(f.read_text(encoding='utf-8-sig'))
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
initial=read(out/'CHECK_RESULT.json')
initial_sha=sha(out/'CHECK_RESULT.json')
s=read(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')
original=read(p/'worker_submission/SUBMISSION.json')
receipt=read(p/'REPAIR_RECEIPT.json')
assert not initial['accepted'] and len(initial['findings'])==1
assert initial_sha==receipt['independent_rejection_sha256']
assert sha(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')=='023e53edd194e05a78dc2fcb98f5959e31dac7fbcbde2a363231b531c8e85cfc'
assert sha(p/'worker_submission/SUBMISSION.json')==initial['checked_submission_manifest_sha256']
assert sha(p/'SUBMISSION.json')==initial['checked_submission_manifest_sha256']
assert original['files']==initial['checked_submission_files']
assert all(sha(p/'worker_submission'/f)==h for f,h in original['files'].items())
current={f:sha(p/f) for f in s['files']}
assert current==s['files'] and len(current)==20
changed=[f for f,h in original['files'].items() if current[f]!=h]
assert set(changed)==set(receipt['changed_files'])=={'TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','TURN_TABLE.md'}
assert set(current)-set(original['files'])=={'REPAIR_RECEIPT.json'}
ledger=read(p/'TURN_LEDGER.json'); oldledger=read(p/'worker_submission/TURN_LEDGER.json')
assert ledger['turns'][:7]==oldledger['turns'][:7] and ledger['turns'][8:]==oldledger['turns'][8:]
t8=ledger['turns'][7]
assert t8['timing']['end_after_resolution_seconds']==164.0
assert t8['board_after']['timestamp_seconds']==162.5
assert t8['board_after']['opponent']['board_effects'][0]['name']=='Binding Snow'
assert t8['board_after']['opponent']['board_effects'][0]['evidence_ids']==['F0162.50']
assert t8['post_expiry_confirmation']['actual_frame_seconds_if_measured']==164.002
assert t8['post_expiry_confirmation']['turn_number_displayed']==9
assert t8['post_expiry_confirmation']['binding_snow_icon_present'] is False
assert t8['automatic_events_in_order'][0]['evidence_ids']==['F0164.00','F0167.20']
frames={f['evidence_id']:f for f in read(p/'TURN_EVIDENCE.json')['frames']}
assert 'board_after_resolution' not in frames['F0162.50']['role']
assert 'board_after_actions_before_expiry' in frames['F0162.50']['role']
assert 'previous_turn_post_expiry_confirmation' in frames['F0164.00']['role']
def refs(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k.endswith('evidence_ids'):
                assert all(i in frames for i in x),(k,x)
            if k=='evidence_id': assert x in frames,x
            refs(x)
    elif isinstance(v,list):
        for x in v: refs(x)
for f in ['TURN_LEDGER.json','PAUSE_GAME.json','GUIDE_UPDATE_SUPPLEMENT.json','SEEN_CARD_INVENTORY.json']: refs(read(p/f))
result=copy.deepcopy(initial)
result.update({
 'reviewed_utc':datetime.now(timezone.utc).isoformat(),
 'accepted':True,'full_review_coverage_checked':True,'pause_contract_checked':True,'guide_update_checked':True,
 'checked_submission_manifest':str(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'),
 'checked_submission_manifest_sha256':sha(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'),
 'checked_submission_files':current,
 'findings':[], 'exact_corrections_required':[], 'remaining_coverage_gaps':[], 'unverified_material_claims':[],
 'review_scope':'Full original independent review carried forward after preservation and unchanged-file hash verification, plus independent bounded four-file comparison and retained T8 frame reinspection. No source reread or extraction.',
 'initial_rejection_preserved':{'path':str(out/'CHECK_RESULT.json'),'sha256':initial_sha,'accepted':False},
 'preserved_worker_submission_manifest':str(p/'worker_submission/SUBMISSION.json'),
 'preserved_worker_submission_manifest_sha256':sha(p/'worker_submission/SUBMISSION.json'),
 'repair_receipt_checked':str(p/'REPAIR_RECEIPT.json'),
 'repair_receipt_sha256':sha(p/'REPAIR_RECEIPT.json'),
 'independently_reinspected_after_repair_image_paths':[str(p/'turn_evidence/t0162.50.jpg'),str(p/'turn_evidence/t0164.00.jpg')],
 'resolved_findings':[{'id':'T8_POST_RESOLUTION_EFFECT_BOUNDARY','resolved':True,'basis':'Native 162.502 still shows the prohibition icon and opponent-turn background. Native 164.002 shows Current turn 9 and no icon. The repaired T8 row truthfully retains the pre-expiry board at 162.5, sets the resolved ending time to 164.0, and separately records the native next-turn confirmation. Automatic expiry and frame roles now use the correct boundary evidence; REVIEW and TURN_TABLE describe the distinction. Logical expiry remains end T8.','changed_files':changed,'guide_and_inventory_semantics_unchanged':True,'effective_manifest_binds_all_20_files':True}],
})
result['verification']['submission_file_count']=20
result['verification']['original_19_files_preserved_and_hash_checked']=True
result['verification']['bounded_changed_file_count']=4
result['verification']['additional_native_extractions']=0
result['category_findings']['boards']='All six independently reviewed owner-start boards, both physical board histories, HP, Tools, typed Energy and same-recording genealogy remain valid. Binding Snow applies to the opponent Active position, including replacement Baxcalibur, through opponent turns 6, 8 and 10. T8 now distinguishes the pre-expiry 162.5 snapshot from the native 164.002 next-turn confirmation.'
(out/'CHECK_RESULT_AFTER_REPAIR.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=f'''# Independent review after the bounded T8 repair

Accepted: **true** for the effective 20-file submission. Full review coverage, the Pause capture contract and all four guide additions are verified, using the prior independent full review plus the bounded repair check.

Reviewer: /root/ind_drafta_auto5; gpt-6.1-sol, high. Effective manifest: SUBMISSION_AFTER_INDEPENDENT_REPAIR.json. SHA-256: {sha(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')}. All 20 hashes match. The original 19 files and original manifest are preserved in worker_submission and match the initial rejected receipt. The initial CHECK_RESULT.json remains unchanged with accepted false.

I independently compared every changed field and prose difference in TURN_LEDGER.json, TURN_EVIDENCE.json, REVIEW.md and TURN_TABLE.md, checked REPAIR_RECEIPT.json, and reinspected the two retained native frames. At 162.502, the restriction icon is present. At 164.002, displayed turn 9 and no restriction icon confirm end-T8 expiry. The repair keeps the 162.5 board snapshot as pre-expiry, uses 164.0 as the resolved ending time, and records a separate post-expiry confirmation. Frame roles, expiry event evidence and narrative now agree.

The guide and 19-copy seen inventory need no semantic change. All four guide/inventory files are unchanged and bound by the effective 20-file manifest. No coverage gaps or unverified material claims remain. Source limits from the initial review still apply, including hidden opponent information, unopened discard piles, covered stacks, exact collector IDs and invisible input telemetry. Computer Auto On and Advanced category remain local-only, excluded from human Pause Games and Ladder logs.

No source reread, extraction, producer edit, index change or archival move was performed during this check. The initial rejection is preserved separately from this acceptance.
'''
(out/'CHECK_RESULT_AFTER_REPAIR.md').write_text(md,encoding='utf-8')
assert sha(out/'CHECK_RESULT.json')==initial_sha
print(json.dumps({'accepted':result['accepted'],'manifest_sha256':result['checked_submission_manifest_sha256'],'checked_files':len(current),'changed_files_checked':changed,'initial_rejection_unchanged':True,'receipt':str(out/'CHECK_RESULT_AFTER_REPAIR.json')}))
