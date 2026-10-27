# Score: Review G (Gemini) for g1, Dustin (Dacz8976) vs Ryze

Method: I compared `gemini/REVIEW.md` with `ref/REVIEW_FINAL.md` turn by turn, using `ref/compare.json` and `ref/CHECK_NOTES.md` where they already settled a fact, and I opened full-resolution frames for everything else. I opened 27 frames: t_0002, 0043, 0050, 0095, 0148, 0149, 0165, 0167, 0186, 0222, 0225, 0241, 0270, 0277, 0321, 0323, 0326, 0328, 0358, 0359, 0361, and a few repeats of these.

Result: **major 0, minor 2, missed 3, G right over C 2, unsettled 0.** Opponent sheets: field sheet 12/12, review sheet 11/12.

Everything else in Review G agrees with Review C turn by turn: who went first (Ryze), the opening hand, Energy Zones (Water / Fighting), every card played, every attack and damage number, every HP change, all four Knock Outs, the points (1-0, 1-1, 1-2, 3-2), the Confusion and its removal, the 12 turns, and the end by points. The result screen at t=358-361 confirms: Went second, 12 turns, points 3-2, damage 320, card of the game Mega Sharpedo ex (Dustin) and Hitmonchan ex (Ryze), and 970 to 971 pts.

## 1. Review G errors

| Turn | Item | G says | Truth | Frames | Grade | Settled by |
|---|---|---|---|---|---|---|
| Global 7 (Ryze) | Order and target of the Fighting Energy attach | Energy attached to the **Benched** Hitmonchan ex at t=218-219, then Mega Lopunny ex retreats at t=220-223 and Hitmonchan ex is promoted | X Speed, then the retreat, then Hitmonchan ex is Active with no Energy and the Energy still in the Zone (t=222), and only then the Energy is attached to the **Active** Hitmonchan ex (about t=222-225; on at t=225). Same Pokémon, same Energy, same turn; the attach is after the retreat, not before | t_0212, t_0214, t_0222, t_0225 (compare.json); I re-checked t_0222 and t_0225 | minor (borderline) | compare.json (C right) |
| Global 11 (Ryze) | Time of the third Fighting Energy on the Benched Mega Lopunny ex | t=321-322 | At t=321 the Zone is empty (turn just began, hand 4). At t=323 the Energy is in the Zone. At t=326 Lopunny still shows 2 Energy. At t=328 it shows 3 and the Zone is empty. Attach is at about t=326-328, so G is 5-6 s early. Event, target and count (3 F) are right | t_0321, t_0323, t_0326, t_0328 | minor (timestamp off by more than 3 s) | frames |

Grading note on the Global 7 item. The brief lists "a wrong Energy target" as major. Here the card that received the Energy (Hitmonchan ex), the Energy type, the turn and the final board are all right; what is wrong is the order (before the retreat instead of after) and so the label "Benched". I graded it minor. If you count order of play inside a turn as part of "what happened", it becomes major, and the totals would be major 1, minor 1.

### Where G is right and Review C is wrong (counted as G right over C)

| Turn | Item | G | C | Truth | Frames | Settled by |
|---|---|---|---|---|---|---|
| Global 3 (Ryze) | Order of Buneary evolving and the Fighting Energy | Evolves into Mega Lopunny ex (t=89-92), then Energy attached to Mega Lopunny ex (t=93-94) | Energy attached to Buneary at about 86-89, then evolves | Evolve first, Energy after. At 87 and 89 Buneary has no Energy and the Energy is in the Zone; at 92 Mega Lopunny ex is in play with the Energy still in the Zone; at 94 the Zone is empty and Lopunny has 1 F | t_0087, t_0089, t_0092, t_0094 | compare.json (X right, and G says the same as X) |
| Global 6 (Dustin) | Cards shuffled by Copycat | "his 2 remaining cards (Cabbie, Mega Gyarados ex)", then draws 3 to match Ryze's 3-card hand | "Dustin's 3-card hand was shuffled away" | Copycat itself was already played, so 2 cards were shuffled (hand shows Cabbie and Mega Gyarados ex at t=165 and t=167); Ryze has 3 cards, so he draws 3 | t_0165, t_0167 | frames |

Also checked in G and found right: the 0 retreat cost on Mega Sharpedo ex (retreat button shows no Energy cost, t_0186); the coin flips, Tails first (t=148) then Heads (t=149), 90 damage (t_0148, t_0149); Ryze's hand sizes at T1 (4, t_0050), T3 (4, t_0095), T7 (2, t_0222), T9 (4, t_0270), T11 (4, t_0321); Season, deck tile and 970 pts at t=2 (t_0002; the tile shows "25" and "New deck 17"); the result screens (t_0358, t_0359, t_0361).

## 2. Facts Review C records, confirmed by frames, that Review G is missing (3)

1. Opponent's on-screen name **Ryze** (t_0043, t_0358: "vs. Ryze"). G's header never names the opponent.
2. The ranked-screen label **Season B4b SP** (t_0002). Not in G's header.
3. Global 8: the second Soothing Shore Dustin drew was not played because "A Stadium with the same name can't be played" while his own Soothing Shore is in play (card text at t_0241). G only says he drew it.

Small things left out and not counted: the card text of Arena of Antiquity (not readable at the frames I opened) and C's remarks that Arena never added damage (Feebas is not an ex, and it was gone by turn 11). G does record that Arena replaced Soothing Shore and was replaced in turn.

## 3. Claims in G that the frames contradict while Review C is silent

None found. G's hand-size remarks and its turn-boundary times match the frames I checked (see above). The Global 11 timestamp is the only G-only claim that was off.

## 4. G's uncertainty items

| Item in UNCERTAINTIES.md | Real gap? |
|---|---|
| Card fetched by Serena (turn 1) is not shown | No. It is hidden information; C also says Ryze's hand and deck are not shown. |
| Cards shuffled and drawn by Ryze's Copycat and Professor's Research | No. The new cards are hidden; the frames show only the hand size (3 after Copycat, 4 after Research). |
| Set numbers not legible | No, but note `gemini/OPPONENT_field.json` gives set numbers "B1a 076/069" and "B1a 084/069" that neither the frames I opened nor Review C can confirm, and which contradict G's own uncertainty note. Set numbers are not scored. |

G did not flag the two real mistakes (Global 7 order, Global 11 time).

## 5. Opponent sheets against `ref/OPPONENT_FINAL.json`

I counted 12 fields: went_first; global_turns; final_score; end; opponent_energy_zone; set of Pokémon names; each opponent attack (name and damage, counted as one field); Trainer names; special_conditions; healed; bench_damage; card of the game.

### `gemini/OPPONENT_field.json` (cheaper pass): 12/12

| Field | Sheet | Reference | Match |
|---|---|---|---|
| went_first | opponent | opponent | yes |
| global_turns | 12 | 12 | yes |
| final_score | 3-2 | 3-2 | yes |
| end | points | points | yes |
| opponent_energy_zone | Fighting | Fighting | yes |
| Pokémon names | Buneary x2, Mega Lopunny ex, Hitmonchan ex | same | yes |
| attacks | Rapid Smashers 90 (T5); Quick Straight 50 (T7, T9, T11) | same | yes |
| Trainers | Serena, Copycat, X Speed, Professor's Research, Arena of Antiquity | same | yes |
| special_conditions | Confused | Confused | yes |
| healed | false | false | yes |
| bench_damage | false | false | yes |
| card of the game | Hitmonchan ex | Hitmonchan ex | yes |

Outside the 12 fields (not counted): this sheet's `opponent_energy_attached` puts the turn 9 Energy on Mega Lopunny ex (truth: Active Hitmonchan ex, t=280-284) and leaves out the turn 11 attach to the Benched Mega Lopunny ex. The notes field also talks about a "Lucario card sleeve"; notes are ignored.

### `gemini/OPPONENT_review.json`: 11/12

| Field | Sheet | Reference | Match |
|---|---|---|---|
| went_first | opponent | opponent | yes |
| global_turns | 12 | 12 | yes |
| final_score | 3-2 | 3-2 | yes |
| end | points | points | yes |
| opponent_energy_zone | Fighting | Fighting | yes |
| Pokémon names | Buneary x2, Mega Lopunny ex, Hitmonchan ex | same | yes |
| attacks | Rapid Smashers, Quick Straight (names only, no damage numbers, one use each) | Rapid Smashers 90; Quick Straight 50 x3 | **no**: damage missing (names right, nothing contradicted) |
| Trainers | same five | same five | yes |
| special_conditions | Confused | Confused | yes |
| healed | false | false | yes |
| bench_damage | false | false | yes |
| card of the game | Hitmonchan ex | Hitmonchan ex | yes |

Its `opponent_energy_attached` list (turns 3, 5, 7, 9, 11, with the right targets) is correct and, for turn 3, better than the reference (the reference says "Buneary, then evolved"; per compare.json the Energy went on Mega Lopunny ex). Not counted.

## 6. Could a player rely on Review G for this game?

Yes. Review G gets the record of what happened right: both players' setups, all 12 turns, every card played, every attack and damage number, the coin flips, the Confusion, the four Knock Outs, the point race and the 3-2 finish are the same as the frame-checked reference. Its two mistakes are small: in Ryze's turn 7 it puts the Energy attach before the retreat instead of after (same Pokémon, same Energy, same board at the end of the turn), and in turn 11 it dates the Energy attach about 5 s early. It also gets two ordering details right that the reference got wrong (turn 3 evolve-then-attach, and the 2-card Copycat shuffle in turn 6). It leaves out only small context: the opponent's name, the season label, and why the second Soothing Shore went unplayed. Its own uncertainty list is honest (hidden cards and set numbers), though the field sheet's set numbers should not be trusted. The review-pass opponent sheet is complete except that it carries no damage numbers; the field sheet matches the reference on every checked field.
