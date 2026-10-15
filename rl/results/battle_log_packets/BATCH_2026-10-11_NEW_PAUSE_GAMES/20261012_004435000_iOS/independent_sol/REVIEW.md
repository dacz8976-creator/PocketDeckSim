# Independent bounded verification

Reviewer: /root/verify_pause_004435, gpt-6.1-sol, inherited high effort. Source: 20261012_004435000_iOS.MP4, SHA-256 7326d0f49952bda981acb67765fb118375963a485c52161e693cb7cf85be37fe, 463.93 seconds, 1170 x 2532. Source identity is the frozen CLI intake binding; the source was not rehashed or moved.

Status: accepted with recording limits. The final eight packet inputs are sealed in CHECK_RESULT.json; no required repairs remain.

This is a separate bounded source verification, not a second full-battle review. It reuses native and reduced frames retained by the worker. No new video extraction, shared index/event writes, source moves or external log changes were performed. Native frames were distinguished from the reduced four-second overview.

VIEWED_EVIDENCE.json binds the independently viewed frame files, crop views and the reduced boundary contact sheet to their retained-image SHA-256 values. The final read-only crop-manifest check found 42 native 1170 x 2532 frames and 84 correctly sized crops; bottom bounds are [0, 2025, 1170, 2532]. That verifies native geometry and file presence, separately from semantic visual checks.

## Independently inspected source evidence

- Native 0 seconds shows the filmed deck QR. A separate rescan in QR_DECODE.json resolves 20 semantic slots and Water Energy, roundtrips the payload, and exactly matches both the worker decode and the fresh LIVE_DECK_SNAPSHOT_RESUME.json. Exact printing remains a live-log label rather than QR proof.
- Native 10 seconds identifies Chuaryzard, level 47. Native 27 seconds gives all five opening cards left to right: Kingdra ex, Hiking Trail, Team Rocket's Weezing ex, Team Rocket's Koffing, Rare Candy. Owner goes second; Koffing is selected as Active. No Auto control appears in inspected gameplay views.
- Ordinary owner turn 2: Seadra is the normal draw. Native 136 seconds gives the five-card pre-play hand. Native 138 through 141 seconds establishes the first voluntary move as Water attached to Active Koffing, then the turn ends without an attack. Ending hand remains five.
- Owner turn 4: native 188.3 seconds recovers the clear six-card pre-play hand before Horsea placement. Native 188/189 placement and 190/192 later views cannot substitute for that pre-play hand. The opponent's bench is Eevee ex and Feebas, not Froakie or Vaporeon.
- Turn 5: native 243 seconds names Irida and visibly states a 40-damage heal for Pokemon with Water attached. Native 246 shows Mega Gyarados ex restored from 180 to its 210 HP cap, an actual heal of 30. Poison and Burn persist; a single condition icon alternating on screen is not proof of a cure.
- Owner turn 6: native 273 seconds shows normal Poké Ball draw; 274.5 gives the four-card pre-play hand; 275 is Poké Ball play; 278 reveals searched Team Rocket's Koffing; 281 is its bench placement; 289 shows Seadra and two Water. The voluntary ending hand is Kingdra ex and Rare Candy, then Hiking Trail adds Horsea at 293 seconds.
- Owner turn 8: native 351.4 gives Kingdra ex, Rare Candy, Horsea, Copycat before the first play. Copycat's three reveal cards are Professor's Research at 374 seconds, Kingdra ex at 375, Small Balloon at 376; 377 shows their final order in hand. The pre-Copycat remaining Rare Candy is shuffled back.
- Native 376/378 shows Small Balloon applies to a Basic Pokemon. It is attached to Stage 1 Weezing ex; native 392 still shows retreat cost two. Native 394 shows the second Water attachment; native 398 shows Kingdra Active and the owner Energy Zone empty. The paid retreat cost is two Water, with Weezing left without Energy.
- Native 410 shows Kingdra poisoned by Poison Barb after Stormy Prison. Native 414 shows the Hiking Trail Rare Candy added to the hand and the poison check. Native 419 shows Kingdra at 160 HP, Mega Gyarados ex at 40, and the retreat-block effect during turn 9.
- Native 424/425 shows Milotic ex already has its second Water while Mega Gyarados ex still has three and the large opponent Energy Zone Water remains available. Native 426 shows that normal Water being attached to Mega. Aqua Charge therefore precedes the normal attachment on turn 9.
- Reduced 428 seconds shows opponent Professor's Research; the identities of its two drawn cards are hidden. Reduced 440 seconds shows Mega Blaster has left Kingdra at 20 HP. Native 445/446 establish turn 10 and Kingdra at 10 after poison, Mega at 30, Mega with four Water and Milotic ex with two Water. Native 447 shows the normal Team Rocket's Weezing ex draw; 448/449 gives all four hand names left to right: Professor's Research, Kingdra ex, Rare Candy, Team Rocket's Weezing ex. Native 451/452 shows the explicit concession message, so the final packet's 451-second notice is valid; the board-only 448 frame is not concession evidence. Native 449/452 shows a generated owner Water available in the Energy Zone. Native 462 confirms Victory, went second, 10 turns, zero points for both players, and 90 owner attack damage.

## Reconciliation to check against final inputs

Owner hand counts: turn 2 ends 5; turn 4 ends 3; turn 6 ends 2 at voluntary end and 3 after Hiking Trail; turn 8 ends 2 before attack and 3 after Hiking Trail; turn 10 has 4 before concession. Owner-start opponent fans are 4, 2, 3, 3, 5. The turn 9 post-normal-draw fan at native 419 is four.

Native 450 and 450.5 shows a Professor's Research inspection while the same four cards, including Research, remain in the hand. Native 452 returns the same four at concession. A resolved owner Research play or two new owner draws is not established.

Terminal HP arithmetic: Mega Gyarados ex 140 to 50 from Stormy Prison, then poison to 40 at turn 8 end and 30 at turn 9 end. Kingdra ex 170 to 160 from poison at turn 8 end, then Mega Blaster 140 to 20 and poison to 10 at turn 9 end. The terminal event is a concession, with no knockout and no points awarded.

## Final packet reconciliation and repairs

The final prose and ledger cover one match and exactly ten turns. Every owner turn has retained draw-relative +1/+3/+6 candidates, a named preplay hand and native crops, and ending hand evidence. Dense 188.3, 274.5 and 351.4 frames recover hands before immediate plays. The final +6 turn 10 candidate is after concession and is correctly unsuitable. Native 294's added crop pair confirms the post-Hiking turn 6 ending hand. Opening, all five owner normal draws, Poké Ball's find, all three Copycat reveals and both automatic Hiking Trail draws reconcile to the hand counts above.

Initial final-draft opponent fans 5/3 at owner turns 2/4 were corrected after independent top-crop inspection to 4/2. Owner-start fans now read 4/2/3/3/5 in prose, coverage, ledger and evidence. Acting-opponent start fans are 5/4/2/4/4 at their specifically labeled captures; turns 3/5 are before their normal draws, so counts differ from later after-draw fans. Hidden identities remain null.

The first three after-board snapshots were changed from pre-End/pre-timeout views to resolved boundaries: native 134, 141, 186, displaying turns 2, 3, 4. Clear earlier board frames supplement the normal-draw zoom at 134. Later after-board phases distinguish logical resolved turn from the next displayed turn and Energy generation. Both boards, effective HP, attached Water, Tools, conditions, Stadium, points and both Energy Zone lines reconcile. Stormy Prison is active through opponent turn 9 and expired by turn 10.

Copycat's draw-entry count now starts at zero after its played card leaves the hand and Rare Candy is shuffled back, while the separate pre-Supporter count remains two. Its three reveals and resulting hand are directly evidenced. The owner's turn 10 Research inspection is not promoted to a resolved play or two draws.

The final structural validator passes ten rows with no issues. Separate semantic checks confirm HP/Energy arithmetic, opening/hand counts, contiguous numbered action order, source-bound evidence and the complete candidate/crop contract. A pass does not reveal the two hidden mill identities or opponent hidden cards. No full discard-pile view is available; retained board-side tops remain partial observations.

Independent acceptance covers the completed local packet. The parent remains responsible for lead registration, archival, external saved-entry verification and later storage release. Changing any of the eight sealed inputs requires revalidation of the affected claims and a new seal.
