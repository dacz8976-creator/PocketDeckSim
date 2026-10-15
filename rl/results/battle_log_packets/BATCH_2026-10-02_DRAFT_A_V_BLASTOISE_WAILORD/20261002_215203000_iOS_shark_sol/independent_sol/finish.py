import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent.parent; out=p/'independent_sol'
H=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
hashcheck=json.loads((out/'HASH_CHECK.json').read_text())
s=json.loads((p/'SUBMISSION.json').read_text())
assert H(p/'SUBMISSION.json')==hashcheck['submission_sha256']
assert {k:H(p/k) for k in s['files']}==hashcheck['checked_submission_files']
e=json.loads((p/'EXTRACTION_MANIFEST.json').read_text())
groups=[('T2',[43.5,45.5,48.5,56.9]),('T4',[70.2,71,73,76,96.5]),('T6',[128.5,130.5,133.5,140.5]),('T8',[164.8,165.5,167.5,170.5,171.5]),('T10',[193.8,195.5,197.5,200.5,206.5]),('T12',[226.2,227.5,229.5,232.5])]
times=[43.5,70.2,127.5,128.5,164.8,193.8,226.2,247,14,22,42,69.5,80.5,81.5,82.5,83.5,126,163.5,193.5,194.2,194.6,197.5,198.5,203,225.5,.5,52,139.5,148.5,182,183.5,184.5,207.5,222.5,223.5,232.5,239,35,36.5,37,59.5,114.5,135.5,146.5,167.5,176.5,211.5,33.5,45,61,74,78,156,157,160.5,200.5,202,38.5,40,76]
full=[str(p/'turn_evidence'/f't{t:07.2f}.jpg') for t in times]
grids=[str(p/'locator_scan'/f'grid_{a:03d}_{min(a+19,247):03d}.jpg') for a in range(0,248,20)]
sheets=[]; crops=[]
for label,ts in groups:
 for c in ['bottom_crop','top_crop']:
  sheets += [str(out/f'{label}_{c}_{i}.png') for i in range((len(ts)+2)//3)]
  crops += [next(r for r in e if r['requested_source_seconds']==t)[c]['path'] for t in ts]
extra=json.loads((out/'EXTRACTION_MANIFEST.json').read_text())
for r in extra:
 assert H(r['full_frame_path'])==r['full_frame_sha256']
 for c in ['bottom_crop','top_crop']: assert H(r[c]['path'])==r[c]['sha256']
extra_paths=[r['full_frame_path'] for r in extra]
paths=list(dict.fromkeys(grids+full+sheets+extra_paths))
assert all(Path(x).exists() for x in paths+crops)
corrections=[
 {'field':'TURN_LEDGER.json: turns[0].plays_in_order[0].hand_count_after','submitted':3,'required':5,'reason':'3 is after supporter consumption before its two draws; completed Research has5, then Frigibax placement leaves4. The separately submitted draws_and_searches already records3 to5.','evidence_ids':['F0035.00','F0036.50','F0037.00','F0038.50','F0040.00']},
 {'field':'TURN_LEDGER.json: turns[0].plays_in_order[0].evidence_ids and corresponding TURN_EVIDENCE/coverage identity links','required':'Add independent_sol:F0035.50 as exact native Research face identity evidence; retain draw endpoints and do not relabel F0035.00 as the face.','actual_source_seconds':35.5067,'reason':'Existing35.0067 frame is preface fan;35.5067 clearly shows Professor\'s Research. Nominal35 locator is not the exact35.0067 native instant.'},
 {'field':'TURN_LEDGER.json: turns[6].plays_in_order[2].evidence_ids and corresponding TURN_EVIDENCE/coverage identity links','required':'Add independent_sol:F0157.50 as exact native Poke Ball face evidence; retain concealed search endpoint160.5 and unchanged hidden result name.','actual_source_seconds':157.505,'reason':'156.00 and157.00 native anchors precede face reveal;157.505 clearly shows Poke Ball. Later160.5 topdiscard supports continuity but is not the enlarged play-face instant.'}
]
limits=[
 'Concealed opponent draw/search identities remain unknown; complete opponent deck snapshot does not identify hidden held copies.',
 'Neither discard pile is opened. Only public top cards and source-witnessed transactions support partial discard histories; exact full counts remain null.',
 'Covered evolution lower faces are not directly readable. Witnessed same-source evolution genealogy is separate from direct face observation.',
 'Locator grids are one-fps nominal indices. They establish full-span review but may omit subsecond UI or input; selected native frames have separately measured source PTS.',
 'Exact physical collector numbers are not transcribed. Observed alternate artwork and physical-copy lower bounds are separate from the supplied20-slot printing snapshot.',
 'Auto OFF and manual choice prompts support user control on each owner turn, but touch telemetry is absent.',
 'Composite resolved/terminal board states have multiple measured anchors and no single exact source time; no missing interval is reconstructed.'
]
findings={
 'source_and_frozen_submission':'Source identity bound to established verified SHA/size/duration; no movie rehash or full decode. All19frozen core hashes match. All137native plus274crop hashes/dimensions and referenced evidence IDs verified.',
 'full_span_coverage':'Every cell of all13grids inspected from setup through Victory and recording end.12turns/6owner rows match the timeline; no visible cut used to invent events.',
 'opening_setup_result':'14.0opening Misty/IcePop/Carvanha/Lapras/whiteNinetales; Lapras selected Active22 and Carvanha right Bench. Visible AutoOFF establishes computer classification. Terminal Victory3-0,second,12turns,nominaldamage380.',
 'draw_timed_hands':'All6owner selected preplay states, +1/+3/+6 candidates and before-end hands/topfans inspected via24native-pixel lossless contact sheets plus full boards. Fast substitutions70.2/164.8/193.8/226.2 precede the first voluntary action;194.2Research preview is not consumption.',
 'research_ball_copycat':'All named normal owner draws and consequential Copycat/Research/Ball transactions/reveal order checked. Copycat returns2 then draws whiteNinetales,fierySharpedo,Cyrus,Cape. T10 Research drawsPop thenBall; Ball searches stampedVulpix. T9 Research182plus concealed183.5/184.5 are correct. T1 completed-count error and two play-face links need correction.',
 'numbered_plays_and_choices':'Ordered voluntary/nested events checked. OrdinaryT2 andT8 first actions/end hands reconciled, as well as remaining owner turns. No shown no-effect play, warning or visible decline omitted. Owner retreat/attack target selections occur on own turns; no owner choice on opponent turns; opponent Wailmer KO promotion is computer-owned.',
 'boards_hp_energy_tools_conditions':'All6fresh starts show both Active/Bench left-to-right with HP/current/max/individualWater/Tool and empty slots; current versus preview/consumed slots distinguished. Lapras retreat pays2of3 retaining1; Sharpedo free retreat retains1; Cape220; TurboShark70 and nestedWater toNinetales;T10normalWater goesLaprasrightto2 while Vulpixcenter0;T12attack-only unusedcurrentWater1.',
 'stadium_points':'BindingSnow blocks opponent Active-position Energy Zone placement duringT9/T11 and expires at turn end. Shore is opponent Stadium onT11, with zero actual healing because damaged Wailord20 has0Energy and energized Blastoise is full. MeowthKO1 plusWailordKO2 gives3-0; terminal no replacement.',
 'latest_guide_evolution_inventory_actors':'Four latest guide additions integrated:6freshboards with source genealogy/covered-face distinction; owner/opponent choice ownership; source-seen inventoryminimum16physicalcopies with witnessedSharpedo/Ninetales/Vulpix/Research duplicate proofs rather than20-deck assumptions; perownerturn user and AutoOFF spans. Exact20deck snapshot remains separate.',
 'routing':'Computer comparison restricted to local batch/index. No external game logs, shared events, producer-file edits or media moves performed.'
}
r={'accepted':False,'status':'requires_bounded_repair','reviewer':'ind_drafta_manual2','model':'gpt-6.1-sol','effort':'high','checked_at_utc':datetime.now(timezone.utc).isoformat(),'source_video':'20261002_215203000_iOS.MP4','source_sha256':'d0e031e9a27c358ad0e1590621014f2758bf80138b83c0776f9961ca34c88b7c','full_review_coverage_checked':True,'pause_contract_checked':True,'guide_update_checked':True,'checked_submission_manifest':'SUBMISSION.json','checked_submission_manifest_sha256':hashcheck['submission_sha256'],'checked_submission_files':hashcheck['checked_submission_files'],'remaining_coverage_gaps':['Effective packet must link the independently confirmed Research35.5067 and Ball157.505 native play faces.'],'unverified_material_claims':['T1 numbered Research completed-action hand_count_after3 contradicts resolved draw transaction5.'],'recording_limits':limits,'independently_inspected_image_paths':paths,'actual_independently_inspected_image_paths':paths,'original_crop_paths_inspected_in_lossless_native_pixel_sheets':crops,'inspection_counts':{'locator_grids':len(grids),'existing_native_full_frames':len(full),'native_pixel_contact_sheets':len(sheets),'original_crops_in_sheets':len(crops),'independent_new_native_frames':len(extra)},'independent_extra_extraction_manifest':'independent_sol/EXTRACTION_MANIFEST.json','independent_extra_extraction_manifest_sha256':H(out/'EXTRACTION_MANIFEST.json'),'independent_new_native_evidence':extra,'findings_by_checklist_category':findings,'exact_corrections_required':corrections,'observed_result':{'outcome':'win','owner_points':3,'opponent_points':0,'went':'second','game_turns':12,'nominal_damage':380},'classification':{'game_mode':'computer','visible_auto_status':'OFF throughout inspected spans','owner_turn_decision_maker':'user','excluded_from_ladder':True,'excluded_from_human_pause_games':True},'material_additional_findings':[]}
(out/'CHECK_RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
md='# Independent acceptance: repair required\n\nFrozen original SUBMISSION SHA: '+hashcheck['submission_sha256']+'\n\nReviewed all19frozen files, every full-span grid, all6owner fresh boards and scheduled/native hand/top-fan candidates, all reveal transactions, boards/Energy/HP/evolution histories, inventoryminimumcopies and perturnactors. Hashes and411retainedframe/crop files agree. Confirmed computer battle, AutoOFF/user choices, win3-0,second,12turns,380nominaldamage.\n\nRequired corrections:\n\n1. T1 Research completed-action hand_count_after must be5, not3.3is the post-consumption/pre-draw phase; after the two concealed draws it is5, then Frigibax leaves4. The existing draw transaction already records3to5.\n2. Add exact Research native play-face anchor independent_sol:F0035.50 (measured35.5067). ExistingF35is before the face; nominal locator35does not equal native35.0067.\n3. Add exact T7Ball play-face anchor independent_sol:F0157.50 (measured157.505). ExistingF156/F157 precede face, while later publictopdiscard gives continuity. Keep hidden searched identity unknown.\n\nThe separate extraction contains4frames:34.0067and156.505did not show the faces,35.5067and157.505do. All retained with measured PTS, source SHA, native dimensions and lossless crops. No original producer file changed. Root can preserve this rejection and create one effective repaired manifest; final acceptance remains pending that verification.\n\nAll other checked material claims agree, including Lapras retreat2retains1,T10Water toLapras,T12unusedWater1,Shorezerohealing,BindingSnowexpiry,no owneropturnchoices,exact20deck separation and source-seenminimum16copies. Honest hidden-info/unopened-pile/subsecond/touch/covered-face limits are retained in JSON. Actual inspected paths and checklist findings are listed there.\n'
(out/'CHECK_RESULT.md').write_text(md,encoding='utf-8')
print(json.dumps({'accepted':False,'frozen_files':len(r['checked_submission_files']),'counts':r['inspection_counts'],'result_sha256':H(out/'CHECK_RESULT.json')}))
