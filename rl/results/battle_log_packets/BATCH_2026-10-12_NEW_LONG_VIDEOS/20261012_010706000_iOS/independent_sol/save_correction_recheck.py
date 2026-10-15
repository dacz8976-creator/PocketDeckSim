from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
p=Path(__file__).resolve().parent.parent;o=p/'independent_sol'
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
inspection=json.loads((o/'FINAL_FILE_INSPECTION.json').read_text(encoding='utf-8'))
hashes={n:h(p/n) for n in names}
assert hashes=={n:inspection['files'][n]['sha256'] for n in names},'Primary file changed after inspection; reread required'
assert all(inspection['files'][n]['em_dash_count']==0 for n in names)
assert inspection['row_count']==21 and not inspection['missing_frame_paths'] and not inspection['diagnostics']
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'));deck=json.loads((p/'DECK_USED.json').read_text(encoding='utf-8'))
r15=ledger['turns'][14]
assert r15['timing']['start_seconds']==558
assert r15['owner_hand_start']['status']=='complete_with_recording_limits'
assert r15['owner_hand_start']['cards_left_to_right'][3]['evidence_ids']==['F560_50']
assert deck['exact_list_status']=='live_log_list_missing' and deck['cards_in_log_order'] is None
assert len(deck['filmed_deck_snapshot']['cards_in_qr_order'])==20
checked=['turn_evidence/t0558.00.jpg','turn_evidence/t0559.50.jpg','turn_evidence/t0560.50.jpg','turn_evidence/t0051.80.jpg','turn_evidence/t0139.00.jpg','turn_evidence/t0718.00.jpg','turn_evidence/t0719.00.jpg','turn_evidence/t0719.50.jpg']
checkpoint=json.loads((o/'CHECK_RESULT.json').read_text(encoding='utf-8'))
result={
'schema':'independent_bounded_source_correction_recheck_v1','reviewer':'/root/check_010706','model':'Sol','reviewed_utc':datetime.now(timezone.utc).isoformat(),
'source_video':checkpoint['source_video'],'source_sha256':checkpoint['source_sha256'],'duration_seconds':checkpoint['duration_seconds'],
'accepted':True,'status':'independent_acceptance_after_source_bound_corrections','required_repairs':[],
'accepted_input_sha256':hashes,
'earlier_rejected_checkpoint':{'path':'independent_sol/CHECK_RESULT.json','sha256':h(o/'CHECK_RESULT.json'),'preserved_unchanged':True},
'correction_checks':[
 {'id':'turn15_start_hand_observation','resolved':True,'finding':'Native558 shows owner turn15 banner. Native559.5 has prior3fan, native560.5 names Poké Ball. Ledger now labels four-card start inferred from those observations and complete_with_recording_limits. Evidence559.5 is prior_hand_before_normal_draw, selected=false; no full unzoomed four-cardfan claim remains.'},
 {'id':'named_draw_individual_binding','resolved':True,'finding':'Research first second card now bound to51.8 Poké Ball named immediateplay/sequence; Research second second card bound to139 Glimmora completed drawsequence. Copycat individual718Ilima,719normalLuckyIcePop and719.5goldLuckyIcePop visibly agree, then completed721fan has3. Limits preserve sequence versus precise new-card fan observations.'},
 {'id':'readable_prose_spacing','resolved':True,'finding':'Turn prose/action labels and missing spaces cleaned; hand fan, Pause Games and second point readable. All eight final files contain zero em dashes.'},
 {'id':'deck_provenance','resolved':True,'finding':'DECK_USED retains20filmedQRsemantic slots with duplicates, Darkness and direct0→2s New deck16 continuity, while live snapshot fields remain null and exact_list_status=live_log_list_missing. No unsupported dated live20deck snapshot accepted.'}
],
'scope':checkpoint['scope'],
'confirmed_result':checkpoint['confirmed_result'],
'evidence_manifest':{'earlier_bounded_source_check_notes':'independent_sol/SOURCE_CHECK_NOTES.md','earlier_checked_frame_hashes':'independent_sol/CHECKED_FRAME_HASHES.json','final_file_inspection':'independent_sol/FINAL_FILE_INSPECTION.json','correction_navigation_sheet':'independent_sol/CORRECTION_SOURCE_SHEET.jpg','correction_native_frames_sha256':{f:h(p/f) for f in checked},'source_reextract':checkpoint['evidence_manifest']['reextract']},
'limits':['This accepted bounded independent check supplements the primary whole-source review; it is not a second full-source pass.','Three source re-extractions exactly match same-time retained JPEG hashes; no additional source decode was performed for this correction pass.','Full post-draw fans remain unavailable on documented fast/zoomed turns, including15; named cards/counts can be supported by direct reveals plus marked inference.','Hidden opponent card identities, large overlapping fan ranges, unopened discard views, exact unmeasured PTS and unavailable dated live deck snapshot remain explicit.','Independent raw QR decode was not rerun successfully in the selected runtime; retained source-bound decoder/count provenance and native QR context are qualified accordingly.','Lead acceptance, append-only registration, collision-safe archival, external logging and live-artifact verification remain root responsibilities. No primary files, shared logs, sources or external artifacts were changed by this checker.']}
(o/'CORRECTION_RECHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Accepted correction recheck saved with frozen hashes of all eight unchanged final files.')
