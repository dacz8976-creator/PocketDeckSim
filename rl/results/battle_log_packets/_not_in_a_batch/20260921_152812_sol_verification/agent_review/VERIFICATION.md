# Independent verification: 20260921_152812000_iOS.MP4

Reviewer: Codex independent subagent `/root/astra_review_152812`. Review date: 2026-09-21. Gemini 3.8 Flash supplied the first-pass draft. The prior battle's packet was used only as a formatting reference.

## Method and source

The local video SHA-256 is `5FEF7F20302FADC695346ED277CEF892E523CCC73DFF67F2907F4448EE10CDB0`, matching the Gemini submission. Decoder metadata confirms 304.803333 seconds, HEVC, 1170 x 2532, and 18,011 video frames. The review used timestamped source frames covering setup, every turn, named-card plays, all attacks and KOs, energy transitions, evolution, searches, and the terminal sequence. Disputed windows were expanded with before/after frames. This is selective source verification of an end-to-end outline, not a frame-by-frame transcript or knowledge of hidden state.

Gemini's RESPONSE.md ends mid-sentence during Turn 8. Its candidate COVERAGE.md spans all twelve turns, but structural completeness does not establish correctness. The corrected packet is separately authored and remains a draft pending lead acceptance. Originals are unchanged.

## Corrections and evidence

| Claim in Gemini | Corrected observation | Source frames, video time |
|---|---|---|
| Opponent named AI Opponent; Solo established | Visible label is `Opponent`. AI status and Solo/PvP are not independently established. Auto is off; owner's manual-control statement agrees. | 00:15.000, 00:19.000, 00:55.600 |
| T3 Lightning attaches to Dratini at 00:55.600 | Dratini has no Energy. The small Lightning icon is the next-Energy preview in the Energy Zone. First Dragonite receives its first Energy, Water, at 01:08.400. | 00:55.600, 01:06.000, 01:08.400, 01:09.000 |
| T5 attaches Water, taking Dragonite to three Energy | The new Energy is Lightning. Dragonite then has one Water and one Lightning, two total. | 02:02.000, 02:09.000 |
| T7 attaches Water at 03:04.600, and ends with four Energy | Water is still in the Energy Zone at 03:04.600 and through 03:14.000. Irida heals first, Rare Candy evolves the other Dratini, then Water attaches around 03:15.000. Dragonite ends with two Water plus one Lightning, three total. | 03:04.600, 03:08.000, 03:14.000, 03:15.000, 03:18.000 |
| T7 passes despite having four Energy | It has only three. The claimed surprising four-Energy pass is unsupported and removed. | 03:18.000 |
| T8 second Dragonite promotes at 04:06.400 | At 04:06.400 the first Dragonite has disappeared and the second remains Benched. Second point appears next; promotion is visible at 04:11.500 and complete by 04:13.000. | 04:06.400, 04:08.400, 04:10.500, 04:11.500, 04:13.000 |
| T11 attaches Lightning | It attaches Water. The two attached Energy are Water; Lightning is the next-Energy preview. | 04:41.800, 04:42.400, 04:44.000 |
| T12 generated Water unused; Gold Breaker has three Water | Fourth Water is attached to Benched Gold Breaker Silvally at 04:49.500, complete by 04:50.500. It promotes with four Water. | 04:49.000, 04:49.500, 04:50.500, 04:52.400, 04:55.000 |
| Victory banner at the final timestamp | Last inspected frame, 05:04.750, shows `+1 point!` and player points 1, 2, 3. No literal Victory/results screen is recorded. The final KO, empty opponent board and third point establish the player's 3-0 win. | 04:58.800, 05:00.000, 05:02.400, 05:04.750 |

## Confirmed high-impact facts

- Player goes second, starts Type: Null Active against Oricorio, and uses manual control.
- Both Rare Candy evolutions are Dratini to Dragonite, with the 160 HP Draco Meteor printing visibly identifiable.
- The player's first Silvally is the 110 HP Brave Buddies printing, boosted to 140 HP by Elegant Cape. The second is the 110 HP Gold Breaker printing, also boosted to 140 HP.
- Brave Buddies is used on Turns 4, 6, 8 and 10 after a Supporter. It deals 100 each time. Oricorio is KO'd on Turn 4, the first Dragonite on Turn 8, and the second Dragonite loses 100 on Turn 10.
- Irida heals the first Dragonite from 60 to 100 HP on Turn 7.
- Gold Breaker is used on Turn 12 for 60, KO'ing the second Dragonite. No opponent attack or player damage is observed.
- Team Rocket's Thieving Machine at 03:32.500 retrieves Poke Ball by 03:35.800. The player uses that Poke Ball and receives a no-target message, then plays Copycat and uses another Poke Ball with the same no-target result.
- Player Poke Ball failures are visible at 02:21.600, 03:40.200 and 03:55.200. Gladion's no-target result is visible at 04:29.600.
- The long Turn 6 pause includes inspection of the opponent's discard pile at 02:27-02:44, followed by the normal attachment and attack. It is not an unreviewed turn.
- Hiking Trail visibly activates at 04:14.000 and draws Sightseer, shown at 04:16.000. This is an end-of-turn Stadium draw, not a played Supporter.

## Remaining limits

The opponent's Turn 7 Poke Ball is visibly played, but no obtained card identity or explicit no-target result is publicly revealed in the inspected sequence. Hidden hands and complete deck contents remain unknown. Match mode and opponent AI status remain unknown. The last results screen is outside the recording, but the decisive terminal sequence is present. These limits are carried into UNCERTAINTIES.json.

Recommendation: accept the corrected twelve-turn account after lead reconciliation. Do not accept the original Gemini energy ledger or its literal Victory-screen claim. No registry edit or source-video move was performed by this reviewer.
