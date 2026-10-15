import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
q=Path(__file__).resolve().parent
p=q.parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
read=lambda f:json.loads(Path(f).read_text(encoding='utf-8-sig'))
submission=read(p/'SUBMISSION.json')
expected='9489c54b6a89b2387ab1a988555385358a6ab5f4d097ce70562577a44637bd5b'
assert sha(p/'SUBMISSION.json')==expected
checked={name:sha(p/name) for name in submission['files']}
assert checked==submission['files']
e=read(p/'TURN_EVIDENCE.json')
crop_count=0
for f in e['frames']:
    fp=Path(f['full_frame_path'])
    assert sha(fp)==f['full_frame_sha256']
    with Image.open(fp) as im:
        assert im.size==(1170,2532)
        for key in ('bottom_crop','top_crop'):
            c=f[key]
            assert sha(c['path'])==c['sha256']
            with Image.open(c['path']) as ci:
                assert ci.size==im.crop(c['pixel_bounds_x0_y0_x1_y1']).size
                assert ImageChops.difference(im.crop(c['pixel_bounds_x0_y0_x1_y1']).convert('RGB'),ci.convert('RGB')).getbbox() is None
            crop_count+=1
for c in e.get('additional_detail_crops',[]):
    assert sha(c['path'])==c['sha256']
    parent=next(f for f in e['frames'] if f['evidence_id']==c['parent_evidence_id'])
    with Image.open(parent['full_frame_path']) as im,Image.open(c['path']) as ci:
        assert ImageChops.difference(im.crop(c['pixel_bounds_x0_y0_x1_y1']).convert('RGB'),ci.convert('RGB')).getbbox() is None
inspected=read(q/'INSPECTED_IMAGES.json')
assert all(Path(f).is_file() for f in inspected)
corrections=[
{
'id':'R1','category':'Binding Snow expiry and endpoint phase','files':['TURN_LEDGER.json'],
'guard_sha256':checked['TURN_LEDGER.json'],
'location':'turns[7].board_after.opponent.board_effects and turns[7].board_after displayed-turn/phase fields',
'finding':'T8 board_after retains a restriction at F0124.50, but that native has already entered displayed Current turn 9 and the blocked icon is absent. The field falsely extends the T7 restriction past expiry.',
'evidence_ids':['F0123.50','F0124.50','F0128.20','F0187.50'],
'exact_repair':'Set T8 board_after.opponent.board_effects to []. Record the visible turn 9 banner and describe this endpoint as the T8-to-T9 handoff. Retain the player-level restriction at T8 start and through retreat; do not attach it to Squirtle or Wailmer. T6/T10/T12 late opponent-turn anchors still show the blocked icon and may retain a restriction applying to that current opponent turn, with expiry explicit at the following owner start.',
'question_for_astra':None
},
{
'id':'R2','category':'Cape HP provenance and animation boundary','files':['TURN_LEDGER.json','REVIEW.md'],
'guard_sha256':{name:checked[name] for name in ['TURN_LEDGER.json','REVIEW.md']},
'location':'turns[2].board_after.owner.active HP provenance and T3 tool/effective-HP wording',
'finding':'F0049.40 displays170 during Cape HP-count animation. The T3 resolved endpoint records180 with name_hp_position provenance only F0049.40; the stock animation disclaimer does not identify the different HP observation. F0052.00 independently confirms the settled180, one Water and Cape.',
'evidence_ids':['F0048.90','F0049.40','F0052.00','F0054.00'],
'exact_repair':'Keep resolved hp_now/hp_max180 and damage0, but bind settled180 to F0052.00 as continuous carry-forward/composite HP provenance. Explicitly retain F0049.40 as the before-end hand/HP animation showing170, and distinguish this from settled180. Add the two-anchor explanation to the T3 prose/tool result. No game fact, hand, deck or original image needs changing.',
'question_for_astra':None
}]
findings={
'integrity_and_source_binding':{'status':'pass','submission_sha256':expected,'core_files':len(checked),'native_frames':len(e['frames']),'lossless_top_bottom_crops':crop_count,'additional_lossless_detail_crops':len(e.get('additional_detail_crops',[])),'source_scope':'Existing frozen source identity/PTS manifests checked; root supplied source SHA. No full-source rehash or full decode was repeated.'},
'full_coverage':{'status':'pass','observations':['All eleven locator grids inspected from setup through206.641667s, with native checks across all thirteen rows. No cut or additional game turn identified.','Complete numbered actions and nested automatic events match the covered sequence. Timestamp fields explicitly use retained animation/result anchors rather than asserting touch onset.']},
'opening_and_authorship':{'status':'pass','observations':['Native15.00 opening before Active: Lucky Ice Pop, Mega Sharpedo ex, Alolan Vulpix, Irida, Alolan Ninetales ex. Vulpix becomes Active; opponent Squirtle. Owner goes first.','Setup0.50 shows fixed AI opponent, Draft A Shark Tempo and Auto On. Retained gameplay controls remain checked; no mode change observed. Advanced Step-Up category is owner screenshot evidence, separately from Auto.']},
'owner_hands_and_capture_roles':{'status':'pass','observations':['Inspected every selected native owner preplay lower crop:23.00,31.20,62.20,90.20,128.20,155.20,180.20. Starting counts5,6,4,4,5,6,6. Ending native lower crops23.20,49.40,71.20,101.50,137.40,158.30,186.20 reconcile to5,3,3,4,5,5,5.','Scheduled+1/+3/+6 candidates are saved with approximate draw-end timing and honest later-candidate limits. Chosen preplay frames remain before voluntary card removal. Fast actions make later candidates postplay; these candidates do not replace selected start hands.','Independently selected ordinary T3 first evolution and ending, T9 Research/bench sequence and ending, and T11 first Vulpix bench/Water attachment and ending. Unplayed Irida/Lucky Ice Pop/Copycat/Cyrus held rather than invented declines.']},
'draws_and_searches':{'status':'pass','observations':['All seven owner normal-draw identities matched native hand differences. Owner Poke Ball F66.50 publicly reveals Carvanha.','T7 Research reveals Copycat F94.60 then Research F96.00; T9 Research reveals Cyrus F133.00 then second Mega Sharpedo ex F134.20. Reveal order is distinct from subsequent fan order. Copycat never played.','Opponent Poke Ball search result remains concealed; later Wailmer bench does not establish the concealed search identity.']},
'opponent_fans':{'status':'pass','observations':['Direct independent native top-crop counts at all owner starts are4,5,4,4,4,5,5. Early T1/T3, middle T7/T9 and late T11/T13 counted from physical edges. Transaction arithmetic is separate inference.']},
'boards_hp_energy_and_effects':{'status':'repair_required','observations':['Ordinary T9 native128.20 shows owner Ninetales180/Cape/Water2, Sharpedo190/Water1, opponent Wailmer100/Water1 and Squirtle70/Water0. Owner current Water is generated and next preview Water; opponent current slot empty and preview Water. Native137.40 after attachment shows consumed owner current slot, Lapras110/Water1 and remaining five-card hand.','Misty0 heads1 tails gives no Energy; normal Water follows. Cape settled maximum180 is confirmed, but R2 must correct its precise boundary provenance.','T8 Squirtle has Water1 before retreat; Wailmer receives normal Water on bench. F123.50 shows Squirtle Water0 on bench, Wailmer Active Water1, restriction still present. F124.50 already owner turn9 and restriction absent, requiring R1.','Binding Snow text F187.50 makes a player-level restriction on taking Energy from Energy Zone to whichever Active during the next opponent turn. The opponent retains it through promotion and retreat, then it expires at the next owner turn. Pokemon conditions are not fabricated.','Soothing Shore native detail gives automatic20 end-turn heal of that player Water Active. Wartortle10->30 confirmed84.90/86.00 and Wailmer20->40 confirmed150.00. Owner Active stays undamaged; no heal on the opposing damaged Active at owner end.']},
'discard_observations':{'status':'pass_with_recording_limits','observations':['Neither pile is opened anywhere in locator coverage. Periodic native top-only views T5/T9/T13 agree with saved Poké Ball/Research and opponent Poké Ball/Wailmer observations. These remain partial, with inferred history separate.']},
'deck_snapshot':{'status':'pass','observations':['Exact dated owner log snapshot has20 slots including two Misty and Water configuration; packet equals the supplied version. Filmed cards do not conflict. Set/rarity IDs are not inferred from concealed cards or board art.']},
'knockouts_and_result':{'status':'pass','observations':['Ninetales Binding Snow attacks five times. Wartortle KO T7, Wailmer KO T11, Squirtle KO T13 each give one point; no opponent damage/points. Native112.50/169.80 establish promotions,192.40 empty opponent Active after terminal KO,194.80 three points for Dacz8976,203.00 Victory versus fixed Blastoise/Wailord computer deck. T13 endpoint explicitly separates physical board and third-point evidence.']},
'routing':{'status':'pass_with_root_override','observations':['Per-packet ROUTING.json and root LOG_ROUTING.json supersede tentative external destination in original first pass. Local batch/index only; computer Advanced Auto On excludes both human Pause and ladder. Deck-source URL remains valid provenance.']}
}
result={
'reviewer':'/root/ind_drafta_205230','model':'gpt-6.1-sol','reasoning_effort':'high',
'game_id':submission['game_id'],'source_video':submission['source_video'],'source_sha256':submission['source_sha256'],
'accepted':False,'full_review_coverage_checked':True,'pause_contract_checked':True,
'checked_submission_manifest':str(p/'SUBMISSION.json'),'checked_submission_manifest_sha256':expected,
'checked_submission_files':checked,'independently_inspected_image_paths':inspected,
'findings_by_checklist_category':findings,'exact_corrections_required':corrections,
'remaining_coverage_gaps':[],'unverified_material_claims':['Two endpoint/provenance contradictions require the bounded corrections R1/R2; no outcome ambiguity remains.'],
'recording_limits':read(p/'UNCERTAINTIES.json')['recording_limits'],
'observed_result':{'owner':'Dacz8976','outcome':'win','points_owner_opponent':[3,0],'terminal_turn':13,'opponent':'Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)','evidence_ids':['F0192.40','F0194.80','F0203.00']},
'author_mode_classification':{'battle':'computer_battle','category':'Advanced Step-Up Battle','category_basis':'Owner ADVANCED_CATEGORY_CONFIRMATION.json, not source setup label','auto_enabled':True,'owner_actions':'game Auto','opponent_actions':'computer AI','mode_changes':[],'pause_eligible':False,'ladder_eligible':False,'routing':'local batch/index only per root routing receipts'},
'independent_native_extractions':[],'native_cap_used':113,'native_cap_remaining':47,
'checked_utc':datetime.now(timezone.utc).isoformat()
}
(q/'CHECK_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Independent check: third Auto game','', 'Accepted: **false**, pending two precise repairs. Full coverage and Pause contract inspected. No producer file modified.','',f"Source: {submission['source_video']}. Manifest SHA256: {expected}.",'',f'Integrity: all15 core files,113 native frames,226 lossless hand/top crops and1 lossless Stadium detail match. Independently inspected{len(inspected)} images including all11 locator grids. No extra source capture needed.','', 'Observed result: Dacz8976 wins3-0 on turn13 versus the fixed Mega Blastoise/Wailord computer deck. Advanced Step-Up Battle, Auto On, local batch/index only, excluded from human Pause and ladder.','']
for c in corrections:
    lines.extend([f"## {c['id']}: {c['category']}",'',c['finding'],'',c['exact_repair'],'', 'Evidence: '+', '.join(c['evidence_ids'])+'.',''])
for category,info in findings.items():
    lines.extend([f'## {category} ({info["status"]})',''])
    lines.extend(['- '+s for s in info.get('observations',[])])
    lines.append('')
lines.extend(['## Limits','']+['- '+s for s in result['recording_limits']]+['','No remaining coverage gap or consequential rule question. Preserve the frozen first pass and SUBMISSION before guarded repairs. Effective replacement manifest and changed files require this independent checker confirmation.',''])
(q/'CHECK_RESULT.md').write_text('\n'.join(lines),encoding='utf-8')
receipt={'game_id':submission['game_id'],'checked_original_submission_manifest_sha256':expected,'files':{f:sha(q/f) for f in ['CHECK_RESULT.json','CHECK_RESULT.md','INSPECTED_IMAGES.json']},'producer_unchanged_verified':checked==submission['files'],'independent_native_extractions':[]}
(q/'FINDINGS_FREEZE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))

