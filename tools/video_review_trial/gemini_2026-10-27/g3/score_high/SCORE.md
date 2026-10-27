# Score of Review G (Gemini) for g3: Dustin (Dacz8976) vs Zavs65, ranked, 15 turns

Method: Review G was compared with Review C (corrected) fact by fact. Every disagreement was settled in the frames, using `ref/compare.json` and `ref/CHECK_NOTES.md` where they already covered it. About 62 frames were opened, all in `frames/`.

Totals: **major 0, minor 0, missed 2, G right over C 6, unsettled 0.**

## 1. Review G errors (graded)

| Turn | Item | G says | Truth | Frames | Grade | Settled by |
|---|---|---|---|---|---|---|
| none | No Review G error was found. Every disagreement with C was settled for G, or was a timestamp within 3 s. | | | | | |

Checked and found correct in G (the facts are in G, in C, and in the frames):
- First player, Energy Zone types, opening hand and the 15 turns.
- Every attack and its damage: Expert Splasher 0 (both coins tails), Double Headbutt 30 twice, Turbo Shark 50 then 70, Zzzap 70 three times, Volt Bolt 140.
- Both Knock Outs (Magikarp, Feebas), the points (0-2), the concession at about 499 s and the result screen (Defeat, damage 120, turns 15, went second).
- The Mega Sharpedo ex versions (2-star and 4-diamond) and their HP at each step, including the Soothing Shore and Irida heals: 140 mid-animation at 0433, 220/180 at 0448, 100/200 at 0488.
- The retreats in turns 8, 10 and 12.
- Hand arithmetic for both Copycat plays, which matches G's draw counts: Dustin drew 5 on opponent hand 5, and 6 on opponent hand 6.
- Timestamps: the largest offsets against the frames are about 2-3 s (turn 5 Lightning to Oricorio: G 198-199, beam seen at 0195, attached by 0197), so no timing error is graded.

## 2. Disagreements G vs C, all settled in G's favour

| Turn | Item | G | C | Truth | Frames | Verdict | Settled by |
|---|---|---|---|---|---|---|---|
| 1 | Opponent Poké Balls | two Poké Balls (t=37 and t=42) | one (0037) | Two. The first full-screen card is at 0037 (timer 19:51). At 0040 the first Poké Ball is already in the discard and the hand has 5 cards. A second full-screen Poké Ball is at 0042 (19:46). | t_0037, t_0040, t_0041, t_0042, t_0044 | G right | frames |
| 3 | Opponent Professor's Research | played at t=123, draws 2 | not listed | Played. At 0122 the opponent hand is 4. At 0124 a white Supporter flash shows with 3 cards in hand. At 0127 the hand is 5 and Professor's Research is on the discard. This also explains Dustin's Copycat drawing 5 in turn 4. | t_0122, t_0124, t_0127 | G right | frames |
| 7 | Tool put on Oricorio | Giant Cape | "name unreadable", +20 HP | Giant Cape. The reveal reads "...nt Cape", "The Pokémon this card is attached to gets +20 HP", and Oricorio goes 70 to 90. | t_0297, t_0299, t_0301 | G right | frames |
| 11 | Lightning to Shinx | attached at t=404 | 0396 | About 0402-0404. At 0399 the Zone Lightning is still unattached and Shinx has 1. At 0403 it is in flight. At 0405 Shinx has 2 and the Zone is empty. C's 0396 is when the Energy was generated. | t_0399, t_0403, t_0405 | G right | frames |
| 13 | Lightning for Luxray's third Energy | attached to the benched Luxray (3 Lightning) at t=458, then Oricorio retreats at t=461-462 | attached to the Active Luxray at about 0463 after the retreat (C and CHECK_NOTES) | The benched Luxray got it between 0458 and 0460. At 0458 the Zone Lightning is unattached and the benched Luxray has 2. At 0460 the benched Luxray has 3, the Zone is empty and Oricorio is still Active. At 0463 Luxray is Active with 3 and Oricorio is benched with 1. | t_0458, t_0460, t_0463 | G right; C wrong; `compare.json` already settled that the Energy went to the benched Luxray before the retreat | compare.json and frames |
| 15 | Zone Lightning at the concession | attached to the Active Luxray (now 3) at t=499-500 | still unattached at 0498, Luxray ends with 2 | Volkner's beam reaches Luxray at 0497 and Luxray has 2 at 0498. At 0498 the Zone Lightning is still large and unattached. At 0499 the Zone is empty. At 0500-0501 the Luxray Energy row is blurred but reads as three icons. The Zone Energy can only leave by being attached. C's 0498 reading is true for that second, but the Energy was attached right after. | t_0497, t_0498, t_0499, t_0500, t_0501 | G right. The target (Luxray) is read from the blurred 0500-0501 frames, so confidence is moderate. | frames |

Extra G detail confirmed by the frames where C is silent:
- The two Carvanha are different cards: Sharp Fang (benched turn 4, t_0195) and Aqua Jet (benched turn 6, t_0299).
- Deck name "New deck 17" and slot 25 are readable at t_0001. The 2D pattern code screen is at t_0000.
- Sylveon heals 30 in turn 7 and 20 in turn 9, capped by Furfrou's max HP of 70.

## 3. Missed facts (in C, confirmed by the frames, absent from G)

| # | Fact | Frames |
|---|---|---|
| 1 | Why Dustin did not attack in turns 8, 10 and 12: the Turbo Shark preview shows 0 damage against Oricorio (Safeguard stops damage from ex attackers). G only says "ends turn without attacking". The "An attack can be used" warning is at 0390. | t_0338 (per C), t_0343, t_0390 |
| 2 | Final result card: "Defeat..." with "pts lost 0" (Master Ball 970). G has the 970 pts and the stats but not "pts lost 0". | t_0509 |

## 4. Claims in G contradicted by the frames while C is silent

None. One UI wording slip is not graded because it does not change the game record: G says a "deck list" is previewed at t=1, but the frame is the Ranked Match screen with the deck tile.

## 5. G's uncertainty items

| Item | Real gap? |
|---|---|
| The opponent's 4 unplayed hand cards and 2 deck cards were never revealed | No. It is hidden information, not a gap in the record. The 4 cards in hand match the card backs at 0498-0500. The deck count is not shown on screen. |
| Set numbers not legible, `set_number` is null | No. The frames show only the Dex line (t_0508), so null is correct and cosmetic. |

G flagged no uncertainty about anything it actually got wrong. It got nothing wrong.

## 6. Opponent sheets against `ref/OPPONENT_FINAL.json`

Fields checked (12): went_first, global_turns, final_score, end, opponent_energy_zone, Pokémon name set, attacks (names; the sheets carry no damage), Trainer names, special_conditions, healed, bench_damage, card of the game.

### 6a. `gemini/OPPONENT_field.json` (quick pass): 11 of 12 match

| Field | Field sheet | Reference | Match |
|---|---|---|---|
| went_first | opponent | opponent | yes |
| global_turns | 15 | 15 | yes |
| final_score | 0-2 | 0-2 | yes |
| end | concede_dustin | concede_dustin | yes |
| opponent_energy_zone | Lightning | Lightning | yes |
| Pokémon names | Furfrou, Eevee, Oricorio, Sylveon, Shinx, Luxray | same six | yes |
| attacks | Double Headbutt, Zzzap, Volt Bolt | same | yes |
| **Trainer names** | Poké Ball, Protective Poncho, Rare Candy | Poké Ball, Professor's Research, Protective Poncho, a Tool, Copycat, Rare Candy, Volkner | **no**. Missing Professor's Research, Copycat, Volkner and the Tool (Giant Cape). The sheet's note admits three reveals rendered as white flashes. Frames: t_0122/t_0127 (Prof. Research), t_0297 (Giant Cape), t_0310 (Copycat on discard), t_0498 (Volkner on discard). |
| special_conditions | none | none | yes |
| healed | true | true | yes |
| bench_damage | false | false | yes |
| card of the game | Oricorio | Oricorio | yes |

Not a checked field: its Energy list is short. It has one turn-15 Lightning entry, while Volkner added 2 and the Zone Energy 1.

### 6b. `gemini/OPPONENT_review.json`: 12 of 12 match

| Field | Review sheet | Reference | Match |
|---|---|---|---|
| went_first | opponent | opponent | yes |
| global_turns | 15 | 15 | yes |
| final_score | 0-2 | 0-2 | yes |
| end | concede_dustin | concede_dustin | yes |
| opponent_energy_zone | Lightning | Lightning | yes |
| Pokémon names | same six | same six | yes |
| attacks | Double Headbutt, Zzzap, Volt Bolt | same | yes |
| Trainer names | Poké Ball, Professor's Research, Protective Poncho, Giant Cape, Copycat, Rare Candy, Volkner | same, with the Tool "unreadable" | yes. The reference's unreadable Tool is Giant Cape (t_0297). The sheet is more complete than the reference: it has the second Poké Ball and Professor's Research on turns 1 and 3, both confirmed. |
| special_conditions | none | none | yes |
| healed | true | true | yes |
| bench_damage | false | false | yes |
| card of the game | Oricorio | Oricorio | yes |

## 7. Can a player rely on Review G for this game?

Yes. Review G is an accurate, complete turn-by-turn record: no major or minor error against the frames. It is more complete than the corrected Review C. G caught the second Poké Ball (turn 1), Professor's Research (turn 3), the name Giant Cape (turn 7), and the true timing and targets of the turn 11, 13 and 15 Energy attachments, where C was wrong. Its damage, HP, Knock Out, point and score lines all check out, and so do its Soothing Shore, Irida and Sylveon heal numbers. What it lacks is two small items: the stated reason for not attacking in turns 8, 10 and 12 (Safeguard preview showing 0), and the "pts lost 0" line on the last screen. The only soft spot is the turn 15 Energy target: the Zone Energy is gone by 0499, but the Luxray count is read from blurred frames. Of the two sheets, the review sheet is fully correct, and the quick field sheet is unreliable for the opponent Trainer list (it drops three Supporters and a Tool).
