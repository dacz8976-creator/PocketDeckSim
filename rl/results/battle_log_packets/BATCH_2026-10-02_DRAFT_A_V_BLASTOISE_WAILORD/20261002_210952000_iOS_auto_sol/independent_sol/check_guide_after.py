import json,hashlib,datetime
from pathlib import Path
b=Path(__file__).resolve().parent.parent;p=b/'independent_sol'
r=lambda f:json.loads((b/f).read_text(encoding='utf-8-sig'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
fn='GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json';g=r(fn);s=r('GUIDE_UPDATE_SUPPLEMENT.json');c=r('SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')
assert sha(b/fn)=='deb368da1948aafaf9616dbab753a1f88769f1a020e44cbdce30fa42bcdcae77'
assert sha(b/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')=='7b6e7108591db334dc3bb20f9cd31219343c443ab2c810182071ceb0284a8f03'
assert g['effective_core_files_sha256']==c['files']
assert g['effective_core_manifest']==s['effective_core_manifest']=={'path':'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json','sha256':sha(b/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')}
for n,h in g['files'].items():assert sha(b/n)==h
old=r('guide_submission_before_repair/GUIDE_UPDATE_SUBMISSION.json')
assert sha(b/'guide_submission_before_repair/GUIDE_UPDATE_SUBMISSION.json')=='ec615eca388eb920c30dc52b725925b3d111511af81c2d2057a42e33cfe771cc'
for n,h in old['files'].items():assert sha(b/'guide_submission_before_repair'/n)==h
assert len(s['fresh_owner_turn_boards'])==9
q=next(x for x in s['owner_choices_during_opponent_turns']if x['turn_number']==15)
assert q['owner_forced_switch_prompt']is True
assert q['prompt_text']=='Please choose a Pokémon to switch in'
assert q['decision_actor']=='game Auto'
assert q['prompt_evidence']['actual_frame_seconds_if_measured']==253.503
assert q['prompt_evidence']['full_frame_sha256']=='9a00689f5fe88c1912ff2606b4e6b556fe7ea0b3c190db0bd21aef8dacda9916'
assert q['owner_choice_events'][0]['prompt_text']==q['prompt_text']
assert len(q['owner_choice_events'][0]['options_on_board'])==3 if 'options_on_board' in q['owner_choice_events'][0] else True
d=r('independent_sol/CHECK_GUIDE_UPDATE.json');resolved=d['findings']
d.update(accepted=True,checked_submission_path=str(b/fn),checked_submission_sha256=sha(b/fn),checked_files_sha256=g['files'],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),acceptance_status='accepted_after_bounded_independent_recheck',findings=[],remaining_coverage_gaps=[],unverified_material_claims=[],resolved_findings=resolved,independently_inspected_image_paths=r('independent_sol/INSPECTED_IMAGES_FINAL.json'),original_check_receipt={'path':'independent_sol/CHECK_GUIDE_UPDATE.json','sha256':sha(p/'CHECK_GUIDE_UPDATE.json')},original_guide_submission_preserved={'path':'guide_submission_before_repair/GUIDE_UPDATE_SUBMISSION.json','sha256':sha(b/'guide_submission_before_repair/GUIDE_UPDATE_SUBMISSION.json')},effective_core_manifest=g['effective_core_manifest'],effective_core_files_sha256=g['effective_core_files_sha256'],recheck_scope='Prompt fields, exact native prompt identity/time/hash, three candidates and unchanged right Ninetales/game Auto selection; direct original/current diff; current guide/core manifest bindings; historical author metrics separately labeled; preserved four originals and exact four current guide hashes.',independent_extraction_manifest={'path':'independent_sol/EXTRACTION_MANIFEST.json','sha256':sha(p/'EXTRACTION_MANIFEST.json')})
d['verified_checks']+=['All +3/+6 owner hand candidate native bottom crops inspected; 113 unique image paths retained in this receipt.','After repair both guide submission and supplemental JSON bind effective core manifest7b6e and current16file map; original Astra binding/metrics/validation remain historical.','T15 written prompt true and exact text/native253.503 SHA checked; event and row agree. Candidate order, selection and actor remain correct. All four guide additions independently satisfied within stated source limits.']
(p/'CHECK_GUIDE_UPDATE_AFTER_REPAIR.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(p/'CHECK_GUIDE_UPDATE_AFTER_REPAIR.md').write_text('# Independent Sol guide acceptance after repair\n\nAccepted true. Full review coverage, Pause capture contract and all four guide additions checked. Reviewer /root/ind_drafta_auto4, gpt-6.1-sol high.\n\nChecked GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json SHA256 '+d['checked_submission_sha256']+' with the exact four current guide hashes and effective core binding '+g['effective_core_manifest']['sha256']+'. Original Astra four-file submission and initial rejected receipt remain preserved.\n\nThe nine fresh owner boards and per-turn game Auto actor records agree with native evidence. T15 now records the visible switch-in prompt at measured253.503 and three highlighted Bench candidates; Auto selects the right Ninetales. Evolution stack history is distinguished from hidden lower faces. The seen inventory supports19 physical owner cards, including one Lucky Ice Pop returned and reused, separately from the supplied exact20-card deck.\n\nNo remaining bounded coverage gaps or unverified material claims. Concealed cards, unopened piles and absent input telemetry remain recording limits. Original Astra metrics are separately historical, and six independent captures, three registered, are identified.\n',encoding='utf-8')
print('Guide accepted',sha(p/'CHECK_GUIDE_UPDATE_AFTER_REPAIR.json'))

