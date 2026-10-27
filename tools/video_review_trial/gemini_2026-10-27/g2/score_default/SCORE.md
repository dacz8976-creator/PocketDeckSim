# Score: Review G (G2 med run) vs Review C and the frames

Game: Dustin (Dacz8976) vs "Point n Click", 6 global turns, about 251 s. Both reviews agree on who went first (opponent), Energy Zones (Water / Metal), the Master Plan Confusion, every damage number (70, 60, 60, 130), every heal, the Knock Out, the 3-0 score and the end by points. About 21 frames opened (limit 120). `ref/compare.json` and `ref/CHECK_NOTES.md` were used where they already settled a fact.

Totals: major 4, minor 1, missed 3, G right over C 2 (one in the review, one on the opponent sheet), unsettled 0.

## 1. Every Review G error

| Turn | Item | G says | Truth | Frames | Grade | Settled by |
|---|---|---|---|---|---|---|
| Opening (t=25-26) | Opening hand | Cabbie, Poke Ball, Carvanha, Wallace, **Mega Gyarados ex** | The fifth card is **Mega Sharpedo ex** (190 HP, Turbo Shark 70), not Mega Gyarados ex. Review C is right. | t_0026, t_0030 (hand fan shows Cabbie, Poke Ball, Wallace, Mega Sharpedo ex; Carvanha Sharp Fang 30 is Active) | major | frames; CHECK_NOTES "confirmed, no change" |
| Global 2 and 4 (t=86, t=162) | Hand-at-start lists | Turn 2: "Cabbie, Poke Ball, Wallace, Mega Gyarados ex, Lisia". Turn 4: "Cabbie, Mega Gyarados ex, Lisia, Carvanha". | The card in hand all game is the second Mega Sharpedo ex (Mega Gyarados ex comes later from the deck). This follows from the opening-hand error; counted once as a minor so the root error is not charged twice. | t_0122 (hand: Cabbie, Mega Sharpedo ex, Lisia), t_0190 (hand: Mega Sharpedo ex, Lisia) | minor | frames; compare.json only_C ("second Mega Sharpedo ex stays in hand") |
| Global 6 (t=213-218) | Wallace played; where Gyarados came from | Wallace is listed in hand but never played. Magikarp evolves into Mega Gyarados ex "from his hand". Hand = Mega Gyarados ex, Lisia, Wallace. | Hand at t=210 is Mega Sharpedo ex, Lisia, Wallace. Dustin **plays Wallace** (t=213, card text "Put a random ... Pokemon from your deck that evolves from that Pokemon onto that Pokemon"), and Magikarp evolves into Mega Gyarados ex 210 HP from the deck (t=217). Mega Sharpedo ex stays in hand. Review C is right. | t_0210, t_0213, t_0217 | major | frames; CHECK_NOTES confirms Wallace played, Magikarp becomes Mega Gyarados ex |
| Global 6 (t=220-225) | Retreat Energy | The retreat "discards its 1 W Energy (remaining 0)". Final board: Mega Sharpedo ex "0 Energy". | No Energy is discarded. Benched Mega Sharpedo ex still shows 1 Water at t=228 and t=232, and Mega Gyarados ex ends with 4 Water. Review C is right. | t_0220 (retreat button), t_0222, t_0224, t_0228, t_0232 | major | frames; CHECK_NOTES Global 6 retreat line |
| Global 6 (t=232-233) | Cards milled by Mega Blaster | "Rocky Helmet (t=232s) and Metal Core Barrier (t=233s)" read as landing in the discard; the third is "hidden". Repeated in UNCERTAINTIES 1 and in the opponent sheet's notes. | The names are not readable. At t=232 the top of the opponent's discard is still Pokemon Center Lady. At t=233 only face-down card backs fly to the pile. At t=234-235 the visible top is the Knocked Out Mawile's Steel Apron. Nothing shows Rocky Helmet or Metal Core Barrier. Review C ("identities not readable") is right. | t_0232, t_0233, t_0234, t_0235 | major | frames; CHECK_NOTES Global 6 discard line |

Not errors (checked): Slot 25, "New deck 17", 924 pts at the start (t_0001, t_0002); Mega Mawile ex first seen t=65; Starting Plains and Soothing Shore HP swings; Soothing Shore's end-of-turn effect (the card text on t_0217 matches what G says); Turbo Shark at t=182 vs C's t=184 (within 3 s); Energy at t=157-158 and t=199-200; Mega Blaster 130 = 140 minus Steel Apron 10; points 3-0 at t=238; Carvanha Sharp Fang vs Aqua Jet are two different printings (compare.json only_X).

## 2. Facts where G is right and C is wrong or silent

- **Rank points (settled by compare.json, verdict "X right" = G).** The rank panel ends at 925 pts, +1. G wrote 924 to 925. C wrote only "924 faded". The last extracted frame (t_0250) is still the faded 924, so G's 925 rests on compare.json's half-second frame. Counted as 1 G-right-over-C.
- Opponent sheet `special_conditions`: G has ["Confused"], the reference has []. Confused did appear from the opponent's card (Team Rocket's Master Plan, "Carvanha is now Confused", t_0076). Counted as 1 G-right-over-C (below).
- Facts G has that C does not (not disagreements): the two Carvanha printings, Magikarp's Expert Splasher, hand sizes, and the Soothing Shore end-of-turn trigger.

## 3. Facts Review C records, confirmed by frames, that G is missing (3)

1. The opponent's name and level: "Point n Click", Lv. 60 (t_0010 per compare.json, visible on t_0076, t_0190, t_0250 "vs. Point n Click"). G never names the opponent.
2. Steel Apron's full text: it also "recovers from all Special Conditions and can't be affected by any Special Conditions". G records only the -10 damage.
3. Dustin's deck count of 15 at setup (t_0030), which G does not record.

Already counted as errors, so not repeated: the Wallace play and the second Mega Sharpedo ex staying in hand.

## 4. Claims in G that the frames contradict while C is silent

None. The one contradicted claim (the milled card names) is also addressed by C.

## 5. G's uncertainty items

| G item | Real gap? |
|---|---|
| 1. Third card milled by Mega Blaster | Partly real. The gap is real, but G also asserted two card names that the frames do not show, and its explanation (Steel Apron / second copy) was a guess. The honest answer was "not readable". |
| 2. Final rank points after the count finishes | Not a gap. G reported 924 to 925 and the frames and compare.json agree. |

G did not flag the real weak spots: the opening-hand card, the Wallace play, or the retreat Energy.

## 6. Opponent sheets

`OPPONENT_field.json` does not exist in this run (`field_sheet: null`). Only `gemini/OPPONENT_review.json` was checked against `ref/OPPONENT_FINAL.json`. Result: 11 of 12 fields match the reference, and the 12th mismatch is one where G is right and the reference is wrong.

| Field | G sheet | Reference | Match | Settled |
|---|---|---|---|---|
| went_first | opponent | opponent | yes | |
| global_turns | 6 | 6 | yes | |
| final_score | 3-0 | 3-0 | yes | |
| end | points | points | yes | |
| opponent_energy_zone | Metal | Metal | yes | |
| opponent Pokemon names | Mega Mawile ex | Mega Mawile ex | yes | |
| opponent attacks | Heat-Up Crunch (60) | Heat-Up Crunch (60) | yes | |
| opponent Trainers | Team Rocket's Master Plan, Steel Apron, Lucky Ice Pop x2, Starting Plains, Pokemon Center Lady | same six | yes | |
| special_conditions | ["Confused"] | [] | **no** | Frames t_0076 and the definition (conditions from the opponent's cards or attacks) give Confused. G right, reference wrong. |
| healed | true | true | yes | |
| bench_damage | false | false | yes | |
| card of the game | Mega Mawile ex | Mega Mawile ex | yes | |

Off the checked list: the reference has `points_taken: 3` for Mawile, while G has 0. compare.json says G is right (the opponent never took points). The sheet's `notes` field repeats the unreadable "Rocky Helmet and Metal Core Barrier" claim; notes are not scored, but it is the same error as in section 1.

## 7. Could a player rely on Review G for this game?

For the shape of the game, yes. Who went first, the Master Plan Confusion, all four damage numbers (70, 60, 60, 130), the heals, the Steel Apron reduction, the Plains/Shore HP swings, the Knock Out, the 3-0 score and the ending are all correct and mostly well timed. For a close read of the cards, no. G swapped Mega Sharpedo ex for Mega Gyarados ex in the opening hand, so it also shows the wrong hand all game and says Magikarp evolved from hand. It missed that Dustin played Wallace on the last turn. It invented a retreat Energy discard, which leaves Mega Sharpedo ex with 0 Energy on the final board instead of 1. It named two milled cards the frames do not show and presented them as read. A player reviewing his decisions would get wrong answers on what was in hand and which Supporter was used on the winning turn, and would wrongly believe the retreat cost him an Energy.
