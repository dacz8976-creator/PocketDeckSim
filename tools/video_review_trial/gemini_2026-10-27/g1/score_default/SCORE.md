# Score: Review G (med run) vs Review C, game g1 (Dustin vs Ryze)

Totals: **7 major, 2 minor, 1 missed, 1 fact where G is right and C is wrong, 0 unsettled.**
Review sheet (OPPONENT_review.json): **12 of 12 fields matched.** There is no field sheet in this run (`"field_sheet": null`).
Frames opened: 28 of the 120 allowed (t_0000, 0001, 0002, 0029, 0045, 0053, 0085, 0094, 0115, 0119, 0121, 0127, 0132, 0136, 0148, 0150, 0186, 0191, 0193, 0216, 0222, 0226, 0281, 0284, 0296, 0324, 0337, 0346).

## Facts where G and C agree (frames or earlier checks back them)
Who went first (Ryze), 12 turns, final score 3-2 on points, Energy Zones (Ryze Fighting, Dustin Water), the opening Carvanha Active with no Bench, Ryze's two Buneary, every attack and damage number (70, 70, 30, 10, 70, 70 for Dustin = 320; Rapid Smashers 90 with 1 heads and 1 tails, Quick Straight 50 three times), all four Knock Outs and point awards, the Confusion and its cure by retreat, Soothing Shore heals, the two Stadium swaps, the Card of the Game on both sides, and rank 970 to 971. G's coin order (tails first, heads second) is right: the tally reads 0 heads / 1 tail at t_0148 and 1 / 1 at t_0150. G's slot number 25 and the deck name are right (t_0002).

## Review G errors

| Turn | Item | G says | Truth | Frames | Grade | Settled by |
|---|---|---|---|---|---|---|
| Opening (repeated in T2, T4, T6 hand lists and the T6 Copycat shuffle) | Name of the Supporter in the opening hand | Colress | Cabbie. The hand card reads "Cabbie" at t_0029 and stays in Dustin's hand through t_0186. G wrote Colress in five places; counted once. | t_0029, t_0053, t_0085, t_0121 | major | frames (C also says Cabbie) |
| T4 (Dustin) | Where Turbo Shark's Energy went | 1 Water to Benched Carvanha at t=120-121 (so Carvanha 1 Water, Feebas 1) | To Benched Feebas. Feebas shows 1 Water at t_0115 and t_0119 and 2 at t_0121. Carvanha has none. | t_0115, t_0119, t_0121 | major | frames (C says Feebas x2) |
| T6 (Dustin) | Retreat cost | Mega Sharpedo ex retreats "discarding 1 Water Energy" | No Energy discarded. Mega Sharpedo ex has its 1 Water on the Bench at t_0191. (Its retreat cost shows empty at t_0186.) | t_0186, t_0191, t_0193 | major | frames; CHECK_NOTES (reviewer S, item 8) agrees |
| T6 (Dustin) | Target of the turn's Water Energy | Water to Benched Mega Sharpedo ex at t=192 | Water to the new Active Carvanha, which has 0 Energy at t_0191 and is attached at t_0193 (the glow on Carvanha). Sharpedo has 1 Water throughout. Carvanha's Sharp Fang then needs it. | t_0191, t_0193 | major | frames (C says Carvanha) |
| T7 (Ryze) | Retreat of Mega Lopunny ex | Discarded 1 Fighting Energy, leaving 1 | Nothing discarded (X Speed made the retreat free). Mega Lopunny ex has 2 Fighting before at t_0216 and 2 on the Bench at t_0226; Hitmonchan ex has 1 after its attach. | t_0216, t_0222, t_0226 | major | frames (C says both stay attached) |
| T9 (Ryze) | Target of the Fighting Energy | Benched Mega Lopunny ex (now 2) | Active Hitmonchan ex. At t_0281 Hitmonchan has 1 and Lopunny has 2; at t_0284 Hitmonchan has 2 and Lopunny still 2. | t_0281, t_0284 | major | frames (C says Hitmonchan) |
| T11 (Ryze) | Target of the Fighting Energy | Active Hitmonchan ex (now 2) | Benched Mega Lopunny ex. At t_0324 Lopunny has 2 and Hitmonchan 2; at t_0337 Lopunny has 3 and Hitmonchan still 2. (Final board: Lopunny 3 Fighting, G says 2.) | t_0324, t_0337 | major | frames (C says Lopunny bench) |
| T5 (Ryze) | When Ryze attached the Fighting Energy | After Copycat, at t=139 | Before Copycat. 1 Fighting at t_0127, 2 at t_0132, Copycat played at about 134-136 (t_0136 shows the hand being shuffled away). The event and target (Mega Lopunny ex) are right; the order and time are off by 7 s or more. | t_0127, t_0132, t_0136 | minor | frames; CHECK_NOTES (reviewer S, item 1) agrees |
| T1, T3, T5 (Ryze) | Ryze's hand sizes | Hand 5 after the T1 draw, 6 after the T3 draw, 6 after the T5 draw, and 5 cards shuffled by Copycat | One lower each time: 4 cards at t_0045, 5 at t_0085 (4 again at t_0094 after the evolve), and 4 cards shuffled by Copycat at t_0136. G's "draws 3" afterwards is right. | t_0045, t_0085, t_0094, t_0132, t_0136 | minor | frames (C silent on counts; C says the shuffled hand was 4) |

Board-state lines that follow from the errors above are not counted again: Feebas shown with 1 Water in the T4 to T8 board lines (truth 2), Hitmonchan shown with 1 Fighting at the end of T9 (truth 2), Mega Lopunny shown with 1 and then 2 Fighting in the T7 to T12 board lines (truth 2, 2, 3 from T9 on), and Carvanha shown with 1 Water in the T4/T5 lines (truth 0 until T6).

## Where G is right and C is wrong
1. **T3 (Ryze): order of evolution and Energy.** G: Buneary evolves into Mega Lopunny ex (t=90-92), then the Fighting Energy is attached (t=93). C had the Energy first. Settled in `ref/compare.json` (frames t_0087, 0089, 0092, 0094): evolution first, Energy after. I looked at t_0094 as well: Mega Lopunny ex 190 with 1 Fighting. (C's OPPONENT_FINAL.json repeats the wrong order, "attached to Buneary, then evolved".)

## Facts C records, confirmed by the frames, that G is missing
1. **T8 (Dustin): the second Soothing Shore.** C records that the drawn Soothing Shore was held, not played, because a Stadium with that name was already in play. G lists it in the hand and never says what happened to it. The card is still in Dustin's hand at t_0281. This is a small detail; the board record is not affected.

(Not counted: Ryze's player name, left out on purpose; the notes that Quick Straight got no Arena of Antiquity bonus on T9 and T11; the "Victory!" screen at 353 s.)

## Claims in G that the frames contradict while C is silent
Only the hand sizes (minor, in the table above). G's "Wallace" among the cards in the t=1 deck-list preview is not visible in t_0001 (the screen shows Feebas, Milotic ex, 2 Carvanha, 2 Mega Sharpedo ex, Magikarp, Mega Gyarados ex and the top of Poké Ball); Wallace is in the deck, so I did not count it.

## G's uncertainty items
1. Serena's fetched card is face-down. Not a gap in G: no frame shows it, and C says the same.
2. Set numbers unreadable (all turns). Not a gap: C also says set numbers are not shown.
3. Only the top of the deck list is visible at t=1. True of the video (t_0001 shows 9 of 20 cards). Not a gap in G, but its note names "Colress" as a confirmed card, which is wrong (it is Cabbie).

G listed no uncertainty about Energy targets or retreat costs, which is where all of its major errors are.

## Opponent sheets

Field sheet: none in this run (`"field_sheet": null`).

### OPPONENT_review.json vs ref/OPPONENT_FINAL.json (12 fields checked, 12 matched)

| Field | G | C | Match |
|---|---|---|---|
| went_first | opponent | opponent | yes |
| global_turns | 12 | 12 | yes |
| final_score | 3-2 | 3-2 | yes |
| end | points | points | yes |
| opponent_energy_zone | Fighting | Fighting | yes |
| opponent Pokémon names | Buneary, Mega Lopunny ex, Hitmonchan ex | same | yes |
| opponent attacks | Rapid Smashers, Quick Straight | Rapid Smashers 90, Quick Straight 50 (x3) | yes on names; G records no damage numbers and lists Quick Straight once, so damage cannot be checked, but nothing contradicts |
| opponent Trainer names | Serena, Copycat, X Speed, Professor's Research, Arena of Antiquity | same | yes |
| special_conditions | Confused | Confused | yes |
| healed | false | false | yes |
| bench_damage | false | false | yes |
| card of the game | Hitmonchan ex | Hitmonchan ex | yes |

Outside the 12 fields: G's `opponent_energy_attached` list has the T9 target (Mega Lopunny ex, truth Hitmonchan ex) and the T11 target (Hitmonchan ex, truth Mega Lopunny ex) wrong. Those are the same two errors already counted in the table above, so they are not counted again. C's list also has one wrong target (T3 "Buneary", settled against C by compare.json).

## Can a player rely on Review G for this game?
For the big picture, yes: who went first, the turn count, every attack and damage number, all four Knock Outs, the points, the 3-2 result, the coin flips, the Stadiums and heals, and the opponent's cards are right, and the opponent sheet matches on all 12 fields. For the details of Energy, no. G got three of Ryze's five Energy attachments or retreats wrong (T7 discard, T9 and T11 targets), invented an Energy discard on Dustin's T6 retreat, put two of Dustin's Energy on the wrong Pokémon (T4, T6), and named the wrong Supporter (Colress for Cabbie) in several hand lists. Anyone checking who had how much Energy where, such as which Pokémon could attack on a given turn, would be misled from T4 onward, and the end-of-game board (Lopunny 2 Fighting instead of 3, Feebas 1 Water instead of 2) is wrong too. Ryze's hand sizes are also one too high. It is a usable story of the game but not a reliable Energy ledger; for that, use Review C and the frames.
