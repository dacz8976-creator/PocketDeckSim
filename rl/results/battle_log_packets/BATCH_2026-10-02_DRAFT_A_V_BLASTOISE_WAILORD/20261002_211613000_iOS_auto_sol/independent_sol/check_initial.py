import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

p=Path(__file__).resolve().parent.parent
def read(n): return json.loads((p/n).read_text(encoding='utf-8-sig'))
def sha(f): return hashlib.sha256(Path(f).read_bytes()).hexdigest()
s=read('SUBMISSION.json'); ledger=read('TURN_LEDGER.json'); ev=read('TURN_EVIDENCE.json'); ex=read('EXTRACTION_MANIFEST.json')
current={n:sha(p/n) for n in s['files']}
assert current==s['files'] and len(current)==19
assert sha(p/'SUBMISSION.json')=='f517ef25c730bae74c7b80c8fae098b354a5633983351a45d11d44edcda0344c'
assert [t['turn_number'] for t in ledger['turns']]==list(range(1,12))
assert len(ex)==110
ids={f['evidence_id'] for f in ex}
assert len(ids)==110
for f in ex:
    assert f['source_sha256']==s['source_sha256'] and f['source_video']==s['source_video']
    assert f['actual_frame_seconds_if_measured'] is not None
    im=Image.open(f['full_frame_path']); assert im.size==(1170,2532)
    assert sha(f['full_frame_path'])==f['full_frame_sha256']
    for c in ['bottom_crop','top_crop']:
        crop=f[c]; assert sha(crop['path'])==crop['sha256']
        bounds=crop['pixel_bounds_x0_y0_x1_y1']; assert Image.open(crop['path']).size==(bounds[2]-bounds[0],bounds[3]-bounds[1])
        assert crop['parent_sha256']==f['full_frame_sha256']
    assert f['bottom_crop']['pixel_bounds_x0_y0_x1_y1']==[0,2025,1170,2532]
def refs(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k.endswith('evidence_ids'):
                for i in x: assert i in ids,(k,i)
            refs(x)
    elif isinstance(v,list):
        for x in v: refs(x)
for n in ['TURN_LEDGER.json','PAUSE_GAME.json','SEEN_CARD_INVENTORY.json','GUIDE_UPDATE_SUPPLEMENT.json']: refs(read(n))
frames={f['evidence_id']:f for f in ev['frames']}
hand_contract=[]
for t in ledger['turns']:
    if t['who_played']!='owner': continue
    de=t['timing']['draw_animation_end_seconds']; nums=[]
    for off in [1,3,6]:
        key=f'F{de+off:07.2f}'; f=frames[key]
        assert 'scheduled_draw_candidate' in f['role']
        assert f['turn_number']==t['turn_number']
        assert abs(f['offset_after_draw_seconds']-off)<0.0001
        nums.append(key)
    before=f"F{t['timing']['before_end_action_seconds']:07.2f}"
    assert 'before_ending_action_hand' in frames[before]['role']
    assert len(t['owner_hand_start']['cards_left_to_right'])==t['owner_hand_start']['count']
    assert len(t['owner_hand_end']['cards_left_to_right'])==t['owner_hand_end']['count']
    hand_contract.append({'turn':t['turn_number'],'draw_end':de,'candidate_ids':nums,'before_end_id':before,'ending_hand_count':t['owner_hand_end']['count']})

full_times=['0014.20','0015.30','0024.80','0045.80','0093.20','0137.80','0167.20','0208.80','0049.50','0104.50','0108.30','0109.00','0110.20','0111.50','0141.10','0142.20','0142.80','0171.00','0172.30','0176.00','0139.80','0169.20','0158.50','0211.50','0230.80','0000.00','0074.50','0121.50','0133.50','0156.50','0162.50','0058.50','0063.50','0066.50','0068.00','0164.00']
bottom_times=['0025.80','0027.80','0030.80','0047.80','0050.80','0056.50','0095.20','0098.20','0118.00','0139.80','0142.80','0145.00','0169.20','0172.20','0183.00','0210.80','0213.80','0211.50']
top_times=['0024.80','0045.80','0093.20','0137.80','0167.20','0208.80']
inspected=[str(x) for x in sorted((p/'locator_scan').glob('grid_*.jpg'))]+[str(p/'turn_evidence'/f't{t}.jpg') for t in full_times]+[str(p/'turn_evidence'/f't{t}_bottom.png') for t in bottom_times]+[str(p/'turn_evidence'/f't{t}_top.png') for t in top_times]+[str(p.parent/'opponent_deck'/'OWNER_ADVANCED_CATEGORY.jpg')]
finding={
 'id':'T8_POST_RESOLUTION_EFFECT_BOUNDARY','category':'board_after_and_effect_expiry','severity':'bounded_material_timing_correction',
 'observed':'Native F0162.50 still has opponent-turn red background and the Binding Snow prohibition icon. Native F0164.00 displays Current turn 9 and no prohibition icon. The physical Pokemon, HP and Energy endpoints agree.',
 'exact_affected_fields':['TURN_LEDGER.json#/turns/7/timing/end_after_resolution_seconds','TURN_LEDGER.json#/turns/7/board_after/timestamp_seconds','TURN_LEDGER.json#/turns/7/board_after/phase','TURN_LEDGER.json#/turns/7/board_after/opponent/board_effects','TURN_LEDGER.json#/turns/7/board_after/evidence_ids and nested current-board evidence_ids','TURN_LEDGER.json#/turns/7/automatic_events_in_order/0/evidence_ids','TURN_EVIDENCE.json frame F0162.50 role board_after_resolution and frame F0164.00 roles if the endpoint is moved','REVIEW.md T8 Resolved ending boards at 162.5 and automatic expiry evidence'],
 'required_correction':'Preserve the frozen original. In a separate canonical repair, use existing F0164.00 for the resolved post-T8 expiry endpoint and set displayed turn to 9, or keep 162.5 as a pre-boundary snapshot with visible restriction and cite F0164.00 separately as post-expiry confirmation. Do not describe 162.5 as directly showing the cleared effect. Keep logical expiry end T8.',
 'guide_update_needs_semantic_change':False,'seen_inventory_needs_change':False,
 'guide_note':'Six guide owner-start boards, per-turn Auto actors, absent owner opponent-turn choices and seen-card inventory are valid. Manifest/provenance binding must identify repaired effective core if canonical repairs are added.',
 'evidence_ids':['F0162.50','F0164.00','F0167.20']}
limits=read('PAUSE_GAME.json')['limits']+['One-fps timeline review does not certify every subsecond input. No raw video rehash or full re-decode performed in independent review.','Exact 20-card snapshot checked against saved batch owner snapshot, without revisiting the external site. Source SHA is supplied frozen identity; evidence is consistently bound to it.']
result={
 'reviewer':'/root/ind_drafta_auto5','model':'gpt-6.1-sol','review_model':'gpt-6.1-sol','reasoning_effort':'high','reviewed_utc':datetime.now(timezone.utc).isoformat(),
 'source_video':s['source_video'],'source_sha256':s['source_sha256'],'source_duration_seconds':231.373333,
 'accepted':False,'full_review_coverage_checked':True,'pause_contract_checked':True,'guide_update_checked':True,
 'checked_submission_manifest':str(p/'SUBMISSION.json'),'checked_submission_manifest_sha256':sha(p/'SUBMISSION.json'),'checked_submission_files':current,
 'independently_inspected_image_paths':inspected,'findings':[finding],'exact_corrections_required':[finding['required_correction']],
 'remaining_coverage_gaps':[],'unverified_material_claims':['T8 cleared-effect endpoint at 162.5 contradicts the cited native frame; pending canonical boundary/provenance repair.'],
 'recording_limits':limits,
 'observed_result':{'owner_result':'win','owner_points':3,'opponent_points':0,'turns':11,'went_first':'owner','damage_done':390,'card_of_game':'Alolan Ninetales ex','evidence_ids':['F0230.80']},
 'mode_classification':{'battle_type':'computer','category':'Advanced','category_basis':'Separate owner category screenshot, independently inspected','owner_decision_actor_by_turn':{str(t):'game Auto' for t in [1,3,5,7,9,11]},'auto_enabled':True,'manual_override':'none visible; invisible input unverified','routing':'local only; exclude human Pause Games and Ladder'},
 'verification':{'submission_file_count':19,'hash_matches':True,'native_full_and_crop_hashes_checked':330,'native_frame_count':110,'native_dimensions':[1170,2532],'nested_evidence_refs_checked':True,'turn_rows':11,'owner_rows':6,'locator_grids_inspected':12,'additional_native_extractions':0,'timed_hand_contract':hand_contract},
 'category_findings':{
 'opening':'All five opening cards and Carvanha selected Active are directly supported at14.2/15.3.',
 'hands':'All six starts and draw-end +1/+3/+6 candidates inspected. T1 fast End Turn substitution24.8 is valid; later candidates are appropriately marked post-play/turn. Ending hands5,4,3,5,6,7 reconcile.',
 'draws_searches':'All owner Research/Search/Copycat individual reveal native anchors checked. Copycat Misty108.3, illustrated Research109, regular Research110.2,Vulpix111.5; T7 Cyrus142.2 then Ice Pop142.8; T9 Ball171 then Ninetales172.3; Ball searches Vulpix49.5 and Carvanha176 are valid. Reveals and fan order distinguished.',
 'ordinary_turns':'Independently chose T7/T9 first Research plays and ending-hand reconciliations. T11 attachment goes to right Bench Sharpedo1 to2 while Active Cape Ninetales staysWater2.',
 'boards':'All six owner-start boards freshly inspected with positions, HP, Tools, typed Energy and same-recording evolution genealogy. Both-side boundary fields structurally checked. Binding Snow is player Active-position restriction including replacement Baxcalibur, ends T6/8/10. T8 endpoint repair required.',
 'fans_discards':'All six native top fans independently counted3,5,4,4,4,2. Neither pile opened; top-card observations remain partial and public-event history separate.',
 'guide':'Six fresh start-board records and Auto actors supported. No owner choices during opponent turns appear; owner takes no damage. Inventory19 minimum physical owner copies is supported, repeated Irida/Ice Pop sightings do not add copies, second Sharpedo unseen.',
 'mode_result':'SetupAutoOn and nativeVictory11turns3to0/390damage confirmed. Advanced is separate menu category. Local-only computer routing is correct.'}}
(Path(__file__).parent/'CHECK_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=f'''# Independent review of {s['source_video']}

Accepted: **false pending one bounded timing repair**. Whole review, Pause capture contract and four guide additions were checked. No unreviewed interval remains.

Reviewer: /root/ind_drafta_auto5; gpt-6.1-sol, high. Frozen SUBMISSION SHA-256: {sha(p/'SUBMISSION.json')}. All 19 submitted file hashes match. All 110 native frames and 220 crop hashes/dimensions were checked, with zero new extraction.

Native F0162.50 still shows the Binding Snow restriction and opponent-turn background. F0164.00 displays turn 9 with the restriction absent. T8 board_after currently claims the post-expiry state directly at 162.5. Correct its endpoint/provenance and the matching evidence roles/prose in a separate canonical repair. Logical expiry remains end T8. Exact pointers and remedy are in CHECK_RESULT.json.

The guide's six fresh owner-start boards, per-owner-turn Auto actor, absent owner choices during opponent turns, and 19-copy seen inventory need no semantic correction. Any repaired canonical core needs the appropriate effective-manifest binding.

Confirmed: opening five and Carvanha Active; all six owner hand capture contracts; every named owner Copycat/Research/Search reveal native timestamp; ordinary T7/T9 first moves and hand arithmetic; opponent fans 3,5,4,4,4,2; physical board Energy and HP; T11 Water to Bench Sharpedo; Victory 3-0 in 11 turns, 390 damage. The T3 nested damage/KO then Turbo Water attachment was checked and is supported, with no repair needed.

Recording limits: hidden opponent draws/searches, unopened discard piles, covered evolution stacks known through witnessed same-source history, no exact filmed collector-number recovery, no invisible input telemetry. Exact supplied 20-card list is separate from the visually supported19; second Sharpedo unseen. Computer AutoOn, Advanced category from separate screenshot, local-only routing; exclude both human external logs.

No producer files, source movie, archive, shared index or external log were changed. Receipt preserves this original decision for an after-repair independent check.
'''
(Path(__file__).parent/'CHECK_RESULT.md').write_text(md,encoding='utf-8')
print(json.dumps({'receipt':str(Path(__file__).parent/'CHECK_RESULT.json'),'accepted':False,'checked_files':19,'checked_hashes':330,'images_independently_inspected':len(inspected),'findings':1}))
