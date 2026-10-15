# Independent check: third Auto game

Accepted: **false**, pending two precise repairs. Full coverage and Pause contract inspected. No producer file modified.

Source: 20261002_210612000_iOS.MP4. Manifest SHA256: 9489c54b6a89b2387ab1a988555385358a6ab5f4d097ce70562577a44637bd5b.

Integrity: all15 core files,113 native frames,226 lossless hand/top crops and1 lossless Stadium detail match. Independently inspected65 images including all11 locator grids. No extra source capture needed.

Observed result: Dacz8976 wins3-0 on turn13 versus the fixed Mega Blastoise/Wailord computer deck. Advanced Step-Up Battle, Auto On, local batch/index only, excluded from human Pause and ladder.

## R1: Binding Snow expiry and endpoint phase

T8 board_after retains a restriction at F0124.50, but that native has already entered displayed Current turn 9 and the blocked icon is absent. The field falsely extends the T7 restriction past expiry.

Set T8 board_after.opponent.board_effects to []. Record the visible turn 9 banner and describe this endpoint as the T8-to-T9 handoff. Retain the player-level restriction at T8 start and through retreat; do not attach it to Squirtle or Wailmer. T6/T10/T12 late opponent-turn anchors still show the blocked icon and may retain a restriction applying to that current opponent turn, with expiry explicit at the following owner start.

Evidence: F0123.50, F0124.50, F0128.20, F0187.50.

## R2: Cape HP provenance and animation boundary

F0049.40 displays170 during Cape HP-count animation. The T3 resolved endpoint records180 with name_hp_position provenance only F0049.40; the stock animation disclaimer does not identify the different HP observation. F0052.00 independently confirms the settled180, one Water and Cape.

Keep resolved hp_now/hp_max180 and damage0, but bind settled180 to F0052.00 as continuous carry-forward/composite HP provenance. Explicitly retain F0049.40 as the before-end hand/HP animation showing170, and distinguish this from settled180. Add the two-anchor explanation to the T3 prose/tool result. No game fact, hand, deck or original image needs changing.

Evidence: F0048.90, F0049.40, F0052.00, F0054.00.

## integrity_and_source_binding (pass)


## full_coverage (pass)

- All eleven locator grids inspected from setup through206.641667s, with native checks across all thirteen rows. No cut or additional game turn identified.
- Complete numbered actions and nested automatic events match the covered sequence. Timestamp fields explicitly use retained animation/result anchors rather than asserting touch onset.

## opening_and_authorship (pass)

- Native15.00 opening before Active: Lucky Ice Pop, Mega Sharpedo ex, Alolan Vulpix, Irida, Alolan Ninetales ex. Vulpix becomes Active; opponent Squirtle. Owner goes first.
- Setup0.50 shows fixed AI opponent, Draft A Shark Tempo and Auto On. Retained gameplay controls remain checked; no mode change observed. Advanced Step-Up category is owner screenshot evidence, separately from Auto.

## owner_hands_and_capture_roles (pass)

- Inspected every selected native owner preplay lower crop:23.00,31.20,62.20,90.20,128.20,155.20,180.20. Starting counts5,6,4,4,5,6,6. Ending native lower crops23.20,49.40,71.20,101.50,137.40,158.30,186.20 reconcile to5,3,3,4,5,5,5.
- Scheduled+1/+3/+6 candidates are saved with approximate draw-end timing and honest later-candidate limits. Chosen preplay frames remain before voluntary card removal. Fast actions make later candidates postplay; these candidates do not replace selected start hands.
- Independently selected ordinary T3 first evolution and ending, T9 Research/bench sequence and ending, and T11 first Vulpix bench/Water attachment and ending. Unplayed Irida/Lucky Ice Pop/Copycat/Cyrus held rather than invented declines.

## draws_and_searches (pass)

- All seven owner normal-draw identities matched native hand differences. Owner Poke Ball F66.50 publicly reveals Carvanha.
- T7 Research reveals Copycat F94.60 then Research F96.00; T9 Research reveals Cyrus F133.00 then second Mega Sharpedo ex F134.20. Reveal order is distinct from subsequent fan order. Copycat never played.
- Opponent Poke Ball search result remains concealed; later Wailmer bench does not establish the concealed search identity.

## opponent_fans (pass)

- Direct independent native top-crop counts at all owner starts are4,5,4,4,4,5,5. Early T1/T3, middle T7/T9 and late T11/T13 counted from physical edges. Transaction arithmetic is separate inference.

## boards_hp_energy_and_effects (repair_required)

- Ordinary T9 native128.20 shows owner Ninetales180/Cape/Water2, Sharpedo190/Water1, opponent Wailmer100/Water1 and Squirtle70/Water0. Owner current Water is generated and next preview Water; opponent current slot empty and preview Water. Native137.40 after attachment shows consumed owner current slot, Lapras110/Water1 and remaining five-card hand.
- Misty0 heads1 tails gives no Energy; normal Water follows. Cape settled maximum180 is confirmed, but R2 must correct its precise boundary provenance.
- T8 Squirtle has Water1 before retreat; Wailmer receives normal Water on bench. F123.50 shows Squirtle Water0 on bench, Wailmer Active Water1, restriction still present. F124.50 already owner turn9 and restriction absent, requiring R1.
- Binding Snow text F187.50 makes a player-level restriction on taking Energy from Energy Zone to whichever Active during the next opponent turn. The opponent retains it through promotion and retreat, then it expires at the next owner turn. Pokemon conditions are not fabricated.
- Soothing Shore native detail gives automatic20 end-turn heal of that player Water Active. Wartortle10->30 confirmed84.90/86.00 and Wailmer20->40 confirmed150.00. Owner Active stays undamaged; no heal on the opposing damaged Active at owner end.

## discard_observations (pass_with_recording_limits)

- Neither pile is opened anywhere in locator coverage. Periodic native top-only views T5/T9/T13 agree with saved Poké Ball/Research and opponent Poké Ball/Wailmer observations. These remain partial, with inferred history separate.

## deck_snapshot (pass)

- Exact dated owner log snapshot has20 slots including two Misty and Water configuration; packet equals the supplied version. Filmed cards do not conflict. Set/rarity IDs are not inferred from concealed cards or board art.

## knockouts_and_result (pass)

- Ninetales Binding Snow attacks five times. Wartortle KO T7, Wailmer KO T11, Squirtle KO T13 each give one point; no opponent damage/points. Native112.50/169.80 establish promotions,192.40 empty opponent Active after terminal KO,194.80 three points for Dacz8976,203.00 Victory versus fixed Blastoise/Wailord computer deck. T13 endpoint explicitly separates physical board and third-point evidence.

## routing (pass_with_root_override)

- Per-packet ROUTING.json and root LOG_ROUTING.json supersede tentative external destination in original first pass. Local batch/index only; computer Advanced Auto On excludes both human Pause and ladder. Deck-source URL remains valid provenance.

## Limits

- Opponent concealed normal draws and concealed search result remain unknown. Complete opponent deck membership does not identify a held card.
- Neither player opens a discard pile. Saved discard observations show only visible pile tops; they are not a full census.
- Requested seeks and measured decoded PTS are distinct. Draw-end estimates locate visible integration into hand; offsets are approximate.
- Physical art varies from log labels. Mechanical versions are visible; exact set/rarity numbers are not read from board images.
- Beginning screen omits category label. Advanced is established by owner category screenshot receipt, not inferred from opponent deck name.

No remaining coverage gap or consequential rule question. Preserve the frozen first pass and SUBMISSION before guarded repairs. Effective replacement manifest and changed files require this independent checker confirmation.
