# Score of Review G, game g2 (Dustin v Point n Click, 6 global turns, 3-0)

Frames opened: 20 (t=1, 22, 23, 71, 74, 76, 191, 219, 220, 221, 222, 223, 224, 226, 228, 232, 233, 234, 235, 236). Every frame is in `frames/`.

Result: **2 major, 0 minor, 3 missed, 3 where G is right and C is wrong or silent, 0 unsettled.**

Review G agrees with Review C on almost every fact: who went first (opponent), the opening hand, both Energy Zones, every turn's plays, all five attacks and their damage, every HP change, the Special Condition, the Knock Out, the 3-0 score and the end by points. It also matches C on the order of the two opponent Metal Energy attachments and the Starting Plains HP changes, which `ref/compare.json` and `ref/CHECK_NOTES.md` had already settled in C's favour over a third review.

## 1. Review G errors

| Turn | Item | What G says | The truth | Frames | Grade | How settled |
|---|---|---|---|---|---|---|
| Global 6 | Retreat of Mega Sharpedo ex | "discarding 1 Water Energy (t=221-222)". The final board then lists Mega Sharpedo ex "0 Energy". | No Energy was discarded. Mega Sharpedo ex has 1 Water at t=219 (Active) and still has 1 Water on the Bench at t=226, 228, 235 and 236. Mega Gyarados ex goes from 3 Water (t=219) to 4 Water after the attach at t=226, so nothing was moved off Sharpedo. | t_0219, t_0221, t_0222, t_0224, t_0226, t_0228, t_0235 | major (an Energy event that did not happen; the end-board Energy count follows from it) | CHECK_NOTES (item "Retreat and attachment") and confirmed in the frames |
| Global 6 | Cards discarded by Mega Blaster | At t=233 "the third discarded card visible on top of the discard pile is Steel Apron". The sheet notes and UNCERTAINTIES.md repeat it: "Steel Apron is clearly visible as the last of the 3 discarded cards". | The identities of the 3 discarded cards are not readable. The top of the opponent's discard before the attack is Pokémon Center Lady (t=232). At t=233 the cards are mid-flight. At t=234 the top card is a different, unreadable card with a flare. Steel Apron is on top only at t=235, after Mega Mawile ex is Knocked Out, because its attached Tool goes to the discard with it. It was in play all game, so it was not a deck discard. | t_0232, t_0233, t_0234, t_0235 | major (a wrong card name for a recorded event) | CHECK_NOTES (item "Mega Blaster deck discard": identities not readable) and confirmed in the frames |

Not counted as errors:
- G's description of Steel Apron leaves out "recovers from all Special Conditions" (it says "immune to Special Conditions"). This is wording only; the card is correct.
- Timestamps: no G timestamp is more than 3 s from the frames (for example the attack banners at t=182-183 against C's t=184, and the Starting Plains HP drop at t=178).
- The coin flip result "Tails" at t=22-23 is not contradicted. The coin shows its Pokémon-logo side (t=22) and the banner "Going second" is at t=23. C is silent.
- G's opponent hand sizes (5 at t=71, 2 at t=191) match the card fans on screen.

## 2. Disagreements G v C settled in G's favour (g_right_over_c = 3)

| Item | C | G | Frames or source | Verdict |
|---|---|---|---|---|
| Result screen rank points | "924 pts shown faded", no final value | 924 -> 925, +1 | compare.json (frames t=250 to 251) | G right |
| Opponent Mega Mawile ex `points_taken` (OPPONENT_FINAL.json) | 3 | 0 (both G sheets) | compare.json: the opponent's point markers stay empty, so 0 is correct (not in the brief's field list) | G right |
| `special_conditions` on the opponent sheet | `[]` | `["Confused"]` | t=74 and t=76: Team Rocket's Master Plan, "Carvanha is now Confused". Review C itself records this. If the field means conditions on the opponent's own Pokémon, `[]` is right and this item would not count; see the note under table 3. | G right on the facts |

## 3. Opponent-sheet checks against `ref/OPPONENT_FINAL.json` (12 fields each)

The 12 fields are: went_first, global_turns, final_score, end, opponent_energy_zone, opponent Pokémon names, opponent attacks (name and damage), opponent Trainer names, special_conditions, healed, bench_damage, card of the game.

**`gemini/OPPONENT_field.json` (cheaper pass): 11 of 12 correct against the settled truth (10 of 12 agree with the ref file as written).**

| Field | G field sheet | Ref | Result |
|---|---|---|---|
| went_first | opponent | opponent | match |
| global_turns | 6 | 6 | match |
| final_score | 3-0 | 3-0 | match |
| end | points | points | match |
| opponent_energy_zone | Metal | Metal | match |
| Pokémon names | Mega Mawile ex | Mega Mawile ex | match |
| attacks | Heat-Up Crunch 60 (turn 5) | Heat-Up Crunch (no damage given; 60 per REVIEW_FINAL) | match |
| Trainer names | **Team Rocket's Hijinks**, Steel Apron, Lucky Ice Pop x2, Starting Plains, Pokémon Center Lady | **Team Rocket's Master Plan**, Steel Apron, Lucky Ice Pop x2, Starting Plains, Pokémon Center Lady | **MISMATCH**: the card title at t=74 reads "Team Rocket's Master Plan". G wrong (frames, and compare.json agrees). |
| special_conditions | ["Confused"] | [] | differs from ref, G right (see table 2) |
| healed | true | true | match |
| bench_damage | false | false | match |
| card of the game | Mega Mawile ex | Mega Mawile ex | match |

Extra points, not in the 12 fields: the sheet fills in set number "B2b 051/071", while G's own UNCERTAINTIES.md says set numbers could not be read. Set numbers are ignored in the check. `points_taken` is 0, which is correct.

**`gemini/OPPONENT_review.json` (from the full review): 12 of 12 correct against the settled truth (11 of 12 agree with the ref file as written).**

| Field | G review sheet | Ref | Result |
|---|---|---|---|
| went_first, global_turns, final_score, end | opponent, 6, 3-0, points | same | match |
| opponent_energy_zone | Metal | Metal | match |
| Pokémon names | Mega Mawile ex | Mega Mawile ex | match |
| attacks | Heat-Up Crunch (no damage) | Heat-Up Crunch | match |
| Trainer names | Team Rocket's Master Plan, Steel Apron, Lucky Ice Pop x2, Starting Plains, Pokémon Center Lady | same | match |
| special_conditions | ["Confused"] | [] | differs from ref, G right (see table 2) |
| healed | true | true | match |
| bench_damage | false | false | match |
| card of the game | Mega Mawile ex | Mega Mawile ex | match |

Note on special_conditions: the brief does not define whether this field means conditions the opponent's cards caused or conditions on the opponent's own Pokémon. The frames show the opponent's Supporter Confused Dustin's Carvanha and Mawile was not Confused (heads at t=80). I treated G as right. If the field means the second reading, both G sheets lose one field each (field sheet 10 of 12, review sheet 11 of 12) and g_right_over_c is 2.

The notes field of OPPONENT_review.json repeats the Steel Apron discard error from table 1. Notes are ignored in the field check, and the error is counted once.

## 4. Facts in Review C (confirmed by the frames) that G is missing (missed = 3)

1. The opponent is Lv. 60 (matchmaking card, t=10).
2. Both players start with a 5-card hand, and Dustin's deck shows 15 at setup (t=30). (G gives the opponent's hand size only after the turn-1 draw.)
3. Mega Mawile ex is Metal type (type icon on the card). G only says the opponent's Energy Zone is Metal.

Everything else in C is present in G, including the opponent's name, both Cards of the Game and the full turn log.

Not missed: Lisia and the second Mega Sharpedo ex stay in hand all game. G's start-of-turn hands show both through turn 6.

## 5. Claims in G that the frames contradict while C is silent

None. G's extra details were checked and are correct, or are not contradicted:
- Deck preview at t=1: Feebas, Milotic ex, Carvanha with Sharp Fang, Carvanha with Aqua Jet, two Mega Sharpedo ex, Magikarp, Mega Gyarados ex, Poké Ball, 20/20, Water Energy (all visible in t_0001).
- Starter Carvanha has Sharp Fang 30 (t=71); the benched Carvanha has Aqua Jet 10 (t=219); Magikarp has Expert Splasher (t=191).
- Rank 924 -> 925.

## 6. G's own uncertainty items

| Item | Real gap? |
|---|---|
| 1. The 3 cards discarded by Mega Blaster | Partly real. The two other cards really are unreadable, but G wrongly said the third was Steel Apron (see error 2). |
| 2. The opponent's remaining hand and deck are never shown | Real, but only a limit of the video. It is not a gap in the record. |
| 3. Set numbers too small to read | Real and true. The field sheet nonetheless prints a set number. |

G did not flag the retreat Energy as uncertain. It stated the false discard with confidence.

## 7. Could a player rely on Review G for this game?

Mostly yes. G got the whole play sequence right: the opening hand, the Master Plan Confusion, the Wallace evolution into Mega Sharpedo ex, every Energy attachment and its target, both Lucky Ice Pop coin flips, the Stadium swap with its HP shifts, all five attack damages (70, 60, 60, 130 and the turn-5 hit), the 3-0 score and the points ending. It beat C on the rank points. Its two real errors both come in the last minute of the game. It invented an Energy discard on Mega Sharpedo ex's retreat, which would make a reader think the retreat cost was paid from the Water on Sharpedo when it was not. It also named a card (Steel Apron) as one of the three cards milled by Mega Blaster, which would make a reader think the opponent holds two Steel Aprons. Neither changes who won or how, but each makes a card-level record wrong. A player should trust G for the game flow and damage race, and should not take its Energy counts after a retreat, or card names read from fast animations, without a check. The opponent sheet from the full review is clean; the cheaper sheet misnames the turn-1 Supporter, so it needs a check against the frame.
