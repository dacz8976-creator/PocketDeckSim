import hashlib
import json
from pathlib import Path

p = Path(__file__).resolve().parent.parent
out = p / 'independent_sol'
audit = json.loads((out / 'STRUCTURAL_AUDIT.json').read_text(encoding='utf-8'))
manifest = p / 'SUBMISSION.json'
sha = lambda q: hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(manifest) == audit['checked_submission_manifest_sha256']
for name, digest in audit['checked_submission_files'].items():
    assert sha(p / name) == digest, name

full = ['0000.00','0015.00','0097.70','0100.00','0105.00','0224.70','0234.00','0243.50','0274.50','0275.70','0227.70','0314.70','0319.40','0320.40','0059.50','0196.30','0294.00','0297.00','0352.00','0371.00','0176.00','0177.00','0062.00','0077.50','0191.60','0261.00','0305.00','0310.70']
bottom = ['0013.90','0029.70','0056.70','0097.70','0131.70','0190.70','0224.70','0270.70','0310.70','0345.70','0099.70','0102.70','0226.70','0229.70','0031.20','0062.00','0149.00','0196.30','0278.80','0323.60','0105.00','0157.00']
top = ['0029.70','0131.70','0307.50','0345.70']
images = [p / 'locator_scan' / f'grid_{s:03}_{min(s+19,370):03}.jpg' for s in range(0,371,20)]
images += [p / 'turn_evidence' / f't{t}.jpg' for t in full]
images += [p / 'turn_evidence' / f't{t}_bottom.png' for t in bottom]
images += [p / 'turn_evidence' / f't{t}_top.png' for t in top]
images += [p.parent / 'opponent_deck' / 'OWNER_ADVANCED_CATEGORY.jpg']
assert len(images) == len(set(images)) == 74
assert all(q.is_file() for q in images)

findings = {
 'source_identity_and_frozen_submission': 'All 15 current submitted file hashes match the frozen SUBMISSION.json map and its assigned SHA256. All 354 evidence hashes match. The 118 native full frames are 1170 x 2532; 236 lossless crops have consistent source-frame hashes and pixel bounds, measured PTS and decode records. No second full-source decode or source hash was performed.',
 'full_coverage_and_turn_structure': 'Read full prose, coverage, summary and all 18 turn rows. Inspected all 19 retained source-local one-second locator grids through the result. Nine owner turn rows retain draw-end +1/+3/+6 candidates and a before-ending view. Evidence references resolve; numbered voluntary moves and nested automatic effects are reconciled. The chosen owner preplay views precede voluntary plays.',
 'opening_and_selected_active': 'Native 13.9-second bottom view shows Mega Sharpedo ex, Lucky Ice Pop, Irida, Alolan Ninetales ex and Carvanha. Native 15-second board shows Carvanha selected Active at 50 HP and the other four retained. No redraw is observed.',
 'owner_hands_and_ordinary_turns': 'Visually checked all nine selected owner preplay hands and ending counts: 5, 5, 5, 3, 3, 3, 4, 5, 5 for turns 2 through 18. Independently selected ordinary turns 6 and 12 beyond producer flags. T6 first benches Vulpix, attaches Water, attacks and accelerates Water; six starting cards reconcile to five ending cards. T12 first plays Poke Ball, reveals Lapras, evolves the benched Vulpix and attaches Water; four starting cards reconcile to Copycat, Misty and Lapras at the end.',
 'draws_searches_order_and_duplicates': 'Sampled normal draws across all owner turn starts. T12 Poke Ball visibly reveals Lapras; T16 Poke Ball reveals Carvanha. T14 Research reveals regular Research at 274.5 seconds then regular Sharpedo at 275.7. T16 Research reveals Misty at 319.4 then Cyrus at 320.4. The later hand preserves two Misty, matching the exact 20-slot snapshot. Copycat is held and never played. Concealed opponent draw and search identities remain null; a known opponent deck does not establish held or drawn cards.',
 'opponent_fans': 'Early, middle and late fans independently checked on native views, including T2=3, T6=2, T8=1, T12=1, T16=3 and T18=3. The clean 307.5-second top view supports T16 before the owner draw because the selected view has a notification and no opponent transaction intervenes. All nine reported start counts 3,3,2,1,1,1,2,3,3 are consistent with visible cards.',
 'boards_hp_energy_and_energy_zones': 'Both boards and phase-specific Energy Zones checked on ordinary T6/T12 and consequential transitions. T6 Sharpedo 190 HP/2 Water and Vulpix 60 HP/2 Water reconcile with Baxcalibur 140 to 70 HP. T12 evolved benched Ninetales has 2 Water and the Active attack takes Blastoise 170 to 90 HP. Generated owner current Water before normal attachment becomes empty afterward; upcoming Water is separately described. Opponent idle current is empty with Water preview. Intermediate effect animation is not treated as an equivalent endpoint phase.',
 'retreats_effects_conditions_heals_and_kos': 'Sharpedo printed free retreat is visible at 59.5 seconds; its T10 retreat retains all 3 Water at 196.3. T9 Baxcalibur pays 3 Water to retreat; normal attachment at 176 seconds precedes Poke Ball at 177. T15 X Speed reduces Blastoise retreat cost by one; retreat pays 2 Water and retains 1. Binding Snow blocks normal Energy Zone attachment to the Active; permitted bench attachments occur. Lucky Ice Pop, Irida, Healing Shore, Turbo Shark acceleration, Meowth/Baxcalibur transitions and Ninetales KO/replacement are consistent with the ledger. No extra Triple Bombardment bench damage is invented.',
 'binding_snow_scope_and_expiry': 'Narrow cross-packet recheck explicitly confirms correct player-level Active-position scope. Native printed attack text at 261.00 seconds restricts the opponent taking Energy from the Energy Zone to attach to their Active during their next turn. It is represented solely in opponent.board_effects, never as a Pokemon condition. It is present after T10/T12/T14/T16 and at T11/T13/T15/T17 start, then absent after each affected opponent turn and at T12/T14/T16/T18 owner start. T15 after has an empty board_effects list with Arctibax Active, Wailord benched and Blastoise benched. Native T13 KO replacement view retains the restriction during that opponent turn; T15 retreat/end and T16 owner-start views support the changed Active and expiry. No restriction is carried onto benched Wailord or into owner T16.',
 'no_effect_actions_and_declines': 'Early Turbo Shark has no eligible Water bench, with the visible no-effect message preserved. T17 shows an empty-deck draw failure and no attack from zero-Energy Arctibax. No explicit optional decline is visible. Held Misty, Copycat, Elegant Cape and regular Sharpedo are not labeled as declined or played.',
 'discards_and_recording_limits': 'No discard pile is opened or scrolled in the inspected full locator coverage. Native exposed top cards agree with the partial observations, including Meowth, Irida, Poke Ball, Ninetales, Research and Cyrus. The packet does not convert those top views into a full discard inventory.',
 'decisive_action_and_result': 'T18 Cyrus brings the damaged Mega Blastoise ex at 70 HP Active; Binding Snow deals 80 and KOs it for the winning three-point award. Native result frame requested at 371 seconds has measured PTS 371.01 and shows Victory, owner 3 to opponent 2, went second, turn 18, 610 damage, Alolan Ninetales ex card of the game.',
 'author_mode_category_and_routing': 'Native setup visibly shows AI, the fixed Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega), Draft A: Shark Tempo and green checked Auto On. No mode change is observed. Advanced category comes from the separate owner screenshot, not a recorded difficulty selector. ROUTING.json supersedes tentative intake destination fields: LOCAL batch/index only, excluded from human Pause Games and ladder. Its deck snapshot URL remains valid provenance. No external game entry is required.'
}
result = {
 'reviewer': '/root/ind_drafta_205731',
 'model': 'gpt-6.1-sol',
 'effort': 'high',
 'source_video': '20261002_205731000_iOS.MP4',
 'source_sha256': 'f1ce8e51bc351fc008563c73a72aa7915f0389707375437068c998afd0190199',
 'accepted': True,
 'acceptance_status': 'complete_with_recording_limits',
 'full_review_coverage_checked': True,
 'pause_contract_checked': True,
 'checked_submission_manifest': str(manifest),
 'checked_submission_manifest_sha256': audit['checked_submission_manifest_sha256'],
 'checked_submission_files': audit['checked_submission_files'],
 'independently_inspected_image_paths': [str(q) for q in images],
 'findings': findings,
 'exact_corrections_required': [],
 'remaining_coverage_gaps': [],
 'unverified_material_claims': [],
 'recording_limits': [
  'Opponent concealed card identities are unavailable, even with the supplied fixed deck list.',
  'No periodic opened or scrolled discard views were recorded; exposed top cards are partial observations only.',
  'Some action boundaries are approximate source-local times from a one-second locator; bounded retained native frames establish the material transitions.',
  'No input telemetry establishes a human input or direct intervention; visible Auto On and AI establish the computer Auto classification.',
  'Advanced is established by the separate owner screenshot. No separate difficulty selector is shown in the battle recording.',
  'Visible art distinguishes some owner copies, but collector printing detail is not established.'
 ],
 'named_observed_result': {'result':'Victory','owner_deck':'Draft A: Shark Tempo','opponent':'Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)','points':{'owner':3,'opponent':2},'turn':18,'damage':610,'went':'second','card_of_game':'Alolan Ninetales ex','evidence':'turn_evidence/t0371.00.jpg','measured_pts_seconds':371.01},
 'author_mode_classification': {'opponent_type':'computer_AI','auto_option_visible':True,'observed_auto_enabled':True,'observed_auto_changes':False,'human_input_telemetry':'unavailable','category':'Advanced','category_basis':'separate owner screenshot','actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX','human_pause_games_eligible':False,'ranked_ladder_eligible':False},
 'checked_routing_addendum': {'path':str(p / 'ROUTING.json'),'sha256':sha(p / 'ROUTING.json'),'included_in_frozen_submission_files':False},
 'independent_structural_audit': str(out / 'STRUCTURAL_AUDIT.json'),
 'independent_new_native_captures':0,
 'astra_escalation_required':False
}
(out / 'CHECK_RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
lines = ['# Independent acceptance: 20261002_205731000_iOS.MP4', '', '**Accepted: complete_with_recording_limits.** Full review coverage and the requested capture contract were independently checked. No correction, remaining coverage gap, unverified material claim or Astra escalation is required.', '', 'Reviewer: /root/ind_drafta_205731. Model: gpt-6.1-sol. Effort: high.', '', f"Source SHA256: `{result['source_sha256']}`", f"Frozen submission SHA256: `{result['checked_submission_manifest_sha256']}`", '', 'All 15 frozen file hashes and all 354 native/crop evidence hashes pass. Inspected 74 existing images, including all 19 locator grids. No new source decode or capture was required.', '', 'Observed result: Draft A: Shark Tempo wins against the fixed Mega Blastoise ex & Wailord ex computer deck. Victory screen confirms 3 to 2, turn 18, 610 damage, went second and Alolan Ninetales ex card of the game. Auto On is visibly enabled. Advanced category is separately supported by the owner screenshot.', '', 'Routing: LOCAL batch and BATTLE_REVIEW_INDEX only under the owner addendum. This computer game is excluded from human Pause Games and ladder. The frozen intake destination is superseded; the deck snapshot URL remains provenance.', '', f"Routing addendum SHA256: `{result['checked_routing_addendum']['sha256']}`", '', '## Checklist findings', '']
for category, finding in findings.items():
    lines.extend([f'### {category.replace("_", " ")}', '', finding, ''])
lines.extend(['## Recording limits', ''])
lines.extend(f'- {limit}' for limit in result['recording_limits'])
lines.extend(['', '## Frozen files checked', ''])
lines.extend(f'- `{name}`: `{digest}`' for name,digest in audit['checked_submission_files'].items())
lines.extend(['', '## Independently inspected images', ''])
lines.extend(f'- `{q}`' for q in images)
lines.extend(['', 'Exact corrections required: none.', 'Remaining coverage gaps: none.', 'Unverified material claims: none.', ''])
(out / 'CHECK_RESULT.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'accepted':result['accepted'],'status':result['acceptance_status'],'checked_files':len(result['checked_submission_files']),'inspected_images':len(images),'json':str(out/'CHECK_RESULT.json'),'markdown':str(out/'CHECK_RESULT.md')},indent=2))
