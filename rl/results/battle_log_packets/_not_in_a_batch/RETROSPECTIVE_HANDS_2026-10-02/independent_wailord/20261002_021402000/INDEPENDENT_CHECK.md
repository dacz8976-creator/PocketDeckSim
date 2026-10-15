# Independent hand supplement check

Reviewer: sol_verify_wailord_021402. October 2, 2026.

Status: **needs_repair**, limited to one Research evidence-provenance claim. No unresolved identity needs Astra. The opening, six requested owner starting hands, six ending hands and card counts pass the retained-image check.

## Required repair

In HAND_SUPPLEMENT.json `target_rows[3].draws_and_searches[1]` and TURN_LEDGER.json `turns[6].draws_and_searches[1]`, the turn7 Research event says: `Indeedee revealed first at137`.

Native `turn_evidence/t0137.00.jpg` actually shows **Copycat enlarged as the current reveal**, with **Indeedee ex already appended in the hand** below it. The submitted two-card identity list, Indeedee ex then Copycat, is supported. The first reveal itself is not shown at137.00. Preserve the pair and order, but qualify the first-card reveal order as inferred from append state. Keep137.00 as direct Indeedee hand evidence and use the same frame as direct Copycat reveal evidence;139.00 shows Copycat retained after Indeedee leaves the hand.

Correct both event `limit_reason` fields and any first-card direct-reveal basis. Add an explicit order basis so a downstream reader cannot mistake fan append position for an independently observed first reveal. In REVIEW_SUPPLEMENT.md, the current sentence that Indeedee is directly visible at137 is true, but add that Copycat is the enlarged reveal in that frame. TURN_EVIDENCE's generic137 observation can be made precise without new extraction.

Suggested corrected wording: "At137.00, Indeedee ex is already appended in hand and Copycat is the enlarged Research reveal. Indeedee-then-Copycat order is inferred from this append state. Copycat remains in hand at139.00 after Indeedee placement. Exact Indeedee reveal onset was not measured."

## Supported visual findings

Opening18.00 before placement: Poké Ball, Pokémon Center Lady, Heavy Helmet, Wailmer, Irida.19.00 shows original slot4 Wailmer selected and going first.

| Owner game turn | Start hand, direct left-to-right | End hand, direct left-to-right |
| --- | --- | --- |
| 1 | Poké Ball; Pokémon Center Lady; Heavy Helmet; Irida; Wailord at37.50 | Pokémon Center Lady; Irida; Wailord at50.50 |
| 3 | Pokémon Center Lady; Irida; Wailord; Cyrus at72.30 | Pokémon Center Lady; Irida; Cyrus at77.00 |
| 5 | Pokémon Center Lady; Irida; Cyrus; Wailord ex at100.80 | Pokémon Center Lady; Irida; Cyrus at108.00 |
| 7 | Pokémon Center Lady; Irida; Cyrus; Professor's Research at132.00 | Pokémon Center Lady; Irida; Cyrus; Copycat at146.00 |
| 9 | Pokémon Center Lady; Irida; Cyrus; Copycat; Lucky Ice Pop at205.00 | Soothing Shore; Lucky Ice Pop at275.00 |
| 11 | Soothing Shore; Lucky Ice Pop; Professor's Research at316.50 | Soothing Shore; Cyrus at362.00 |

100.80 retains all four cards in an unzoomed hand with the Bench Wailmer still present.101.20 already shows the Wailord ex evolution. Thus the brief100.80 preplay fan is valid; later offset candidates cannot substitute for it.

Poké Ball's Wailmer is directly visible in the48.00 fan. Search attribution and bench transaction are inherited from the accepted account; exact reveal onset is not independently observed.

Copycat:252.00 directly displays Heavy Helmet, Indeedee ex, Soothing Shore, Lucky Ice Pop, Soothing Shore, including both Shores.249.50 shows the first Shore enlarged while Helmet and Indeedee are already in the fan;250.00 shows Lucky Ice Pop enlarged. This supports the submitted append order. Exact individual reveal onsets, particularly the first two cards, remain bounded rather than measured.

Turn11 Research reveals Cyrus enlarged at330.00 then Poké Ball enlarged at331.00.362.00 directly shows remaining Shore and Cyrus. The failed Poké Ball search remains inherited accepted evidence; no new outcome/board/accepted-action pass was performed.

Opponent fan crops support3,5,7-8,7-8,5,4 for turns1,3,5,7,9,11. The middle two are retained as overlap ranges. Hidden cards are unknown.

## Identity, crop and scope checks

SOURCE_REFERENCE, frozen SOURCE, original before/after move receipt and shared completion event agree on filename,795,968,694 bytes and SHA256 `5b9bcc18507ea541f35741ed451edb58c743300be366db7f8d4fc88856b36759`. Current file metadata matches byte size. The independent checker did not reread the original; the worker's current hash verification is a recorded statement corroborated against frozen receipts.

All64 registered full frames are1170 x2532. All128 registered crops match the stated native bounds: bottom [0,2025,1170,2532], top [0,0,1170,550]. Comparing each crop against its parent at those bounds gives maximum mean absolute RGB pixel difference1.1574/255, consistent with JPEG recompression. No reduced overview was used as identity evidence. The display tool reduced some full frames to946 x2048 for presentation; retained files and native crops were checked at their saved dimensions.

Accepted REVIEW.md hash matches `c6e361d1f95db21cf3b2d500d8d6d3f7db0b0d059aae500a22a677b466abe044`. All14 inherited turn rows match their cited accepted line verbatim. TURN_LEDGER includes all14 turns, marks only the six target owner hands observed, marks owner13 outside requested scope, and labels boards/actions as inherited reference. Exact decoded PTS is unmeasured and remains an explicit limit. Intervening discard windows and the historical full deck version were not newly established.

Metrics:30 visual image submissions,64 full-image and128 crop provenance checks;0 original content reads,0 new extractions,0 new evidence image bytes. Wall time and token/dollar usage were not instrumented. Saved SOURCE_CHECKS.json contains the per-image audit and exact repair request. Submitted supplement, old accepted packet, sources and shared records were not changed.

## Focused repair acceptance

October2,2026: **accepted_with_recording_limits**. The lead preserved the initial five-file worker submission and repaired only the turn7 Research provenance fields and corresponding note. HAND_SUPPLEMENT and TURN_LEDGER now agree: Indeedee identity is direct in the137.00 fan, its first-card order is inferred from append state, and Copycat is the enlarged137.00 reveal plus retained139.00 fan. TURN_EVIDENCE, prose and UNCERTAINTIES state the same boundary. No remaining repair is required.

The original SOURCE_CHECKS.json remains needs_repair as the historical first-check result. SOURCE_CHECKS_REPAIR_ACCEPTANCE.json records the final verdict, all five repaired-file hashes, preserved-submission hashes and exact changed fields. All64 retained full-image hashes are unchanged. This recheck used0 new image submissions,0 new extractions and0 original reads; earlier30 visual submissions remain the evidence basis. All earlier timing, opponent-fan, inherited-scope and historical-version limits remain.
