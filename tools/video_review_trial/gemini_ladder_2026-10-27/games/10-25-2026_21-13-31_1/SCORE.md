# Score: ScreenRecording_10-25-2026 21-13-31_1 (Review G = Gemini, Review X = Codex)

About 62 distinct frames were opened (limit 120). Frame numbers below are seconds (t_SSSS.jpg).

How energy was read from the frames: each Energy on a Pokemon shows as one Water icon at the bottom-left of its card; the Energy Zone orb at the top-left (opponent) stays big and bright until that turn's Energy is used, then goes flat. Mega Sharpedo ex has retreat cost 0 (retreat field is empty on the card); its Energy count does not drop when it retreats.

Everything else both reviews agree on and the frames did not contradict is taken as right: opponent went first, Dustin's opening hand, both Energy Zones Water, T1 Poke Ball + Magikarp, T2 Lisia/Feebas/Carvanha/Sharp Fang 30, T3 Wallace -> Mega Sharpedo ex, Gyarados, Elegant Cape, Turbo Shark 70 KO (opp point 1), T4 Milotic ex/Wallace/Soothing Shore, T5 Wild Swing 60, T6 Irida/Water Pulse 80 + Asleep, T7 tails, T8 Turbo Shark 70 KO on Gyarados (Dustin point 1), T9/T10/T11 Turbo Shark 70 each, T12 Water Pulse 80 + Asleep (heads), T13 Diving Icicles 130 on benched 90-HP Mega Sharpedo ex, KO, "+3 points!" (frame 424) with the track at 1-2-3 (423-425), Defeat (426), Card of the Game Milotic ex (431) and Mega Sharpedo ex (432). Damage numbers 30+80+70+70+80 = 330 match G's results line.

## Disagreement table

| # | Turn | Item | G says | X says | Frames | Verdict |
|---|------|------|--------|--------|--------|---------|
| 1 | T5 (opp) | Extra Energy during the "Waiting for opponent" pause, and an unrevealed Item on the discard | 1 Water attached to benched Mega Sharpedo ex at t=169-174; an Item appears on the discard pile at t=175 | Only one attach this turn (Gyarados, ~165); no Item | 154 (MS 1 icon), 159 (bench MS 1 icon), 165, 174, 178 (still 1 icon); discard top is Wallace at 154-175, then Mantyke at 176-178; orb used at 164 only | X right |
| 2 | T5 (opp) | Mega Sharpedo ex retreat cost | Retreat "discards its 1 Water Energy" | No discard stated | 154 (active MS 1 icon) vs 159 (bench MS 1 icon): nothing discarded | X right |
| 3 | T7 (opp) | Poke Ball played | Plays Poke Ball at t=219 | Not mentioned (omitted from REVIEW and OPPONENT.json) | 219 (item flash, discard top Mantyke) vs 228 (discard top Poke Ball) | G right |
| 4 | T8 (Dustin) | Where Turbo Shark's Energy goes | To benched Milotic ex (3 Water) | To benched Magikarp | 273 (prompt: Magikarp and Milotic highlighted), 274 (Magikarp gets an icon, Milotic stays at 2), 275, 287 (Magikarp 1, Milotic 2) | X right |
| 5 | T9 (opp) | Manual Energy attach target | Chien-Pao ex (t=298), Turbo Shark also to Chien-Pao | Active Mega Sharpedo ex; Turbo Shark to Chien-Pao | 296 (CP 0, MS 2), 299 (CP 1, MS 2), 306 (CP 2, MS 2) | G right |
| 6 | T10 (Dustin) | Copycat play time | Played t=318 after Aqua Charge (312-314) | Played t=309, before Aqua Charge | 310 (Copycat still in hand), 314 (Aqua Charge banner, Copycat still in hand), 319 (Copycat gone, deck count 6) | G right |
| 7 | T12 (Dustin) | Mega Sharpedo ex retreat | Discards 1 Water, 1 left | Retreats with 70 HP, no discard stated | 350 (MS 2 icons) vs 406/408 (bench MS 2 icons) | X right |
| 8 | T13 (opp) | Manual Energy attach | None; Chien-Pao already has 4 | Water attaches to Chien-Pao ex "bringing it to 4" | 404, 406, 408 (CP already 4 icons, orb unused), 412, 415 (CP 4), 425 (orb still unused) | G right |
| 9 | T13 (opp) | Mega Sharpedo ex retreat and final board | Retreats discarding 1 Water, ends with 1 Water | No discard stated | 412, 415, 425 (bench MS shows 2 icons) | X right |
| 10 | T8-T12 | Board-state Energy counts on Dustin's side | Milotic 3 (T8), 4 (T10), 5 (T12); Mega Gyarados 2 (T10), 3 (T12); Magikarp 0 | Milotic "4 Water" at T12 | 275/287 (Milotic 2, Magikarp 1), 319 (Milotic 3), 347/350 (Mega Gyarados 3, Milotic 3), 406/425 (Milotic 4, Mega Gyarados 4) | X right (where X states a count) |

Verdict counts: G right 4, X right 6, both wrong 0, unsettled 0.

## Claims only one review makes that the frames contradict

- G only: the T5 lag-pause Energy attach and "unrevealed Item on the discard" (row 1); the three Mega Sharpedo ex retreat discards (rows 2, 7, 9); Dustin-side Energy counts built on the wrong T8 target (row 10).
- X only: the T13 manual attach to Chien-Pao ex (row 8) and its T9 mirror (Mega Sharpedo ex getting the T9 Energy, row 5); Copycat at t=309 (row 6).
- X omission (not a contradiction): the T7 Poke Ball play (row 3).

## Errors and grades

Review G (Gemini): 2 major, 4 minor.
- MAJOR T5: phantom Energy attach to benched Mega Sharpedo ex (t=169-174) and an Item said to appear at t=175. Frames show Mega Sharpedo ex at 1 Energy before and after, and no new card on the discard.
- MAJOR T8: Turbo Shark Energy attached to Milotic ex. It went to Magikarp.
- minor T5: retreat said to discard 1 Water from Mega Sharpedo ex (cost is 0).
- minor T12: Dustin's Mega Sharpedo ex retreat said to leave it with 1 Water (still 2).
- minor T13: opponent's Mega Sharpedo ex said to retreat leaving 1 Water, final board shows 1 (really 2).
- minor T8-T12 board-state lines: Milotic and Mega Gyarados Energy counts off by one, Magikarp 0 at T8 (a consequence of the T8 error); the events themselves are right.

Review X (Codex): 3 major, 1 minor.
- MAJOR T7: opponent's Poke Ball play missing (REVIEW and OPPONENT.json both omit it).
- MAJOR T9: the opponent's manual Energy attach is put on Mega Sharpedo ex; it went to Chien-Pao ex (REVIEW and OPPONENT.json).
- MAJOR T13: a manual Water attach to Chien-Pao ex that did not happen (Chien-Pao ex already had 4 at the start of the turn; the turn's Energy was never used). Follows from the T9 mistake.
- minor T10: Copycat time given as 309 (really about 316-319, after Aqua Charge).

Not counted: X's "results at 430" was corrected by its own VERIFICATION to 431-434 (frames confirm 431-434). Style and extra detail (G's hand-by-hand lists) are not scored. T12 Copycat times (G 367, X 363) were not settled; frame 364 shows it still in hand, G fits better but the difference is borderline, not counted.

## Opponent sheets (12 fields)

Truth for the checked fields: opponent first; 13 turns; track ends 1-3 with "+3 points!" after the opponent had 1 (1+3 = 4 earned, 3 shown); end by points; Energy Zone Water; Pokemon Carvanha, Magikarp, Mega Sharpedo ex, Gyarados, Mantyke, Chien-Pao ex; attacks Turbo Shark, Wild Swing, Diving Icicles; Trainers Poke Ball (T1, T7), Wallace, Elegant Cape; no special conditions from the opponent; healed true (Soothing Shore heals opponent Pokemon); bench damage true (Diving Icicles); Card of the Game Mega Sharpedo ex.

| Field | gemini | gemini_cheap | codex |
|-------|--------|--------------|-------|
| went_first | opponent: right | right | right |
| global_turns | 13: right | right | right |
| final_score | 1-4: right (earned total) | 1-4: right | 1-3: right (displayed track) |
| end | points: right | right | right |
| energy zone | Water: right | right | right |
| Pokemon names | all six: right | missing Mantyke: WRONG | all six: right |
| attack names | right | right | right |
| Trainer names | Poke Ball, Wallace, Elegant Cape: right | right | right (set of names; it lacks the second Poke Ball entry) |
| special_conditions | none: right | right | right |
| healed | true: right | right | right |
| bench_damage | true: right | right | right |
| card of the game | Mega Sharpedo ex: right | right | right |
| **right / checked** | **12 / 12** | **11 / 12** | **12 / 12** |

final_score convention: the frames show a capped 3-slot track and the +3 banner after 1 point; neither 3 nor 4 is contradicted, so both were accepted.

Other sheet slips outside the 12 fields (not counted): gemini has the extra T5 attach to Mega Sharpedo ex; gemini_cheap puts the T7 attach on Magikarp (it was Mega Sharpedo ex) and lacks Mantyke; codex puts the T9 manual attach on Mega Sharpedo ex, invents a T13 attach and lacks the T7 Poke Ball entry.

## Which record to rely on

For this game the two records agree on every attack, damage number, Knock Out, point, the score, who went first and how it ended, so either gives the same story of the result. For the details, G is the more complete and mostly the more accurate guide to what the opponent did (it has the T7 Poke Ball and the correct T9 and T13 Energy, plus Dustin's hands and draws, which the frames bear out) with 2 major errors against X's 3. But G made two bookkeeping mistakes a player would care about: it invented an Energy attach and Item in the T5 lag pause, and it sent Turbo Shark's T8 Energy to Milotic ex instead of Magikarp, which then threw off Dustin's Energy counts for several turns; it also wrongly has Mega Sharpedo ex paying a retreat cost (it pays none). X got those right but missed the T7 Poke Ball and put the opponent's T9 and T13 Energy on the wrong Pokemon. Best use: take G's turn-by-turn, then correct the T5 lag attach, the T8 Turbo Shark target and the Mega Sharpedo ex retreat cost from X.
