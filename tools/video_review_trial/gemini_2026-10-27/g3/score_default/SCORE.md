# Score: Review G (med run) vs Review C, game Dustin vs Zavs65

Frames opened: 50 of the 120 allowed. All frame paths below are under `frames/`. No `OPPONENT_field.json` exists in this run, so there is no field-sheet table.

## Totals
- major: 4
- minor: 3
- missed: 1
- g_right_over_c: 3
- unsettled: 0
- review sheet: 12 of 12 fields matched

## What matches (checked, no error)
Opponent went first; Energy Zones (Dustin Water, opponent Lightning); opening hand; setup (Magikarp v Furfrou, no benches); every attack and damage (Expert Splasher 0, Double Headbutt 30 and 30, Turbo Shark 50 and 70, Zzzap 70 x3, Volt Bolt 140); every Knock Out and point (Magikarp T3, Feebas T5, score 0-2); all evolutions, HP values, Soothing Shore and Irida healing, Sylveon Soothing Ribbon heals, Dustin's Energy attachments, Dustin's empty deck at T14, the concession at t=499, and the result screen (Defeat, 15 turns, damage 120, cards of the game, 970 pts). Two of the three timing gaps of 3 s were not counted, because 3 s or less is not an error: T3 Lightning to Furfrou (G 0126, truth about 0129) and T9 Lightning to Shinx (G 0359, truth about 0362).

## Review G errors

| Turn | Item | G says | Truth | Frames | Grade | Settled by |
|---|---|---|---|---|---|---|
| 7 (opp) | Order and time of the Lightning attach | Attach to benched Oricorio at 0285, then Furfrou retreats (0288-0291) | Retreat first. At 0285 and 0287 the Zone Lightning is still unattached and Oricorio is benched with 1 Lightning. By 0289 Oricorio is being promoted. The Zone Lightning is attached to the now-Active Oricorio at about 0291, which gives 2. Same Pokemon and same final count, but wrong order and 6 s early. | t_0285, t_0287, t_0289, t_0291, t_0299 | minor | frames (C right) |
| 8 (Dustin) | Retreat Energy cost | The retreat discards 1 Water from the rainbow Sharpedo (2 to 1) | Mega Sharpedo ex has no retreat cost (the retreat box is empty on the card at 0341). Nothing is discarded. At 0343 and 0348 both Sharpedo show 2 Water. | t_0337, t_0341, t_0343, t_0348 | major | frames (C right) |
| 10 (Dustin) | Retreat Energy cost | The retreat discards 1 Water from the regular Sharpedo (3 to 2) | No discard. The retreated 150 HP Sharpedo keeps 3 Water (0390). Active 190 has 2 Water, bench 170 has 3 Water (0398). | t_0384, t_0390, t_0398 | major | frames (C right) |
| 12 (Dustin) | Retreat Energy cost | The retreat discards 1 Water from the rainbow Sharpedo (now 2, then 1) | No discard. After the Water attach, the rainbow Sharpedo has 3 Water. After the retreat, Active 220 has 3 Water and bench 180 has 3 Water (0448). | t_0434, t_0446, t_0448 | major | frames (C right) |
| 13 (opp) | Order, target state and time of the third Lightning on Luxray | Retreat Oricorio (0461-0463), then Zone Lightning to Active Luxray at 0464 | Rare Candy makes a benched Luxray with 2 (0457, Zone Lightning still unattached, Oricorio Active). At 0459 the benched Luxray has 3, the Zone is empty and Oricorio is still Active. The retreat comes after (0462). The attach was to the benched Luxray at about 0458. Same final count of 3. | t_0457, t_0459, t_0462, t_0465 | minor | frames and compare.json (both reviews wrong; C also had the wrong order) |
| 15 (opp) | Zone Lightning attach | Zone Lightning attached to Active Luxray at 0492 (Luxray 1), then Volkner adds 2 (Luxray 3 at the end) | No attach happened. Luxray has 0 Energy at 0494 with the Zone Lightning unattached, 2 Lightning at 0498 after Volkner, and the Zone Lightning is still unattached when Dustin concedes. Luxray ends with 2, not 3. | t_0494, t_0496, t_0498, t_0499 | major | frames and compare.json (C right) |
| Opening | Deck list claim | A deck-editor preview at t=1s shows nine named cards (Feebas, Milotic ex, two Carvanha, two Mega Sharpedo ex, Magikarp, Mega Gyarados ex, Poke Ball) | t=0 is the 2D code share screen over a blurred editor. t=1 is the home screen with the "New deck 17" tile in slot 25 (Feebas and two small highlight cards). No card list is shown. G's own UNCERTAINTIES file says the list cannot be confirmed. The deck name and slot are right. | t_0000, t_0001 | minor | frames (C: not readable) |

Board-state lines in T8, T10, T12, T14 and T15 carry the wrong Energy counts that follow from the three retreat errors and the T15 error (final board: G Active 2 / bench 2 Water and Luxray 3; truth 3 / 4 and Luxray 2). They are not counted again.

## Disagreements where G is right and C is wrong or silent (g_right_over_c = 3)
1. T3 opponent: G records Professor's Research (about 0123), drawing 2. At 0119 the hand is 3 cards, the hand is 4 at 0120, a card is played at 0123, the glow at 0124 is the Supporter, and the hand is 5 at 0126-0127. C leaves out the turn 3 Supporter.
2. T7 opponent: G names the Tool Giant Cape. The played card at 0297 reads "...nt Cape" with the text "gets +20 HP", and Oricorio goes from 70 to 90. C says the name is unreadable.
3. T11 opponent: Zone Lightning to Shinx. G says about 0404. The Zone Lightning is still unattached at 0398, fading at 0402, and Shinx shows 2 at 0405. C says about 0396, which is too early.

Extra detail in G that agrees with the frames and compare.json (not a disagreement): the two Carvanha versions (Sharp Fang benched T4, Aqua Jet benched T6), the T14 "attack, not Energy" choice, and the deck name and slot.

## Facts C records that G is missing (missed = 1)
- T8, T10 and T12: Dustin skipped the attack because the Turbo Shark preview shows 0 damage against Oricorio's Safeguard (shown at 0338 and 0437 per C; confirmed here by the "An attack can be used" warning at t_0390 with Oricorio Active and Safeguard on the card). G only says "ends his turn without attacking".

## G's uncertainty items
- Card set numbers unreadable: true and harmless (set numbers are ignored). Not a real gap for the record.
- Deck list and duplicate counts unconfirmed: a real gap, and it undercuts the deck list G gave in REVIEW.md.
- Opponent's hidden hand and deck: never shown on screen, so not a gap in the record.
- None of G's real errors (the three retreat discards, the T15 attach, the T7 and T13 ordering) were flagged as uncertain.

## Opponent sheets
### gemini/OPPONENT_field.json
Not present in this run (field_sheet = null).

### gemini/OPPONENT_review.json vs ref/OPPONENT_FINAL.json

| Field | G sheet | C sheet | Truth | Match |
|---|---|---|---|---|
| went_first | opponent | opponent | opponent | yes |
| global_turns | 15 | 15 | 15 | yes |
| final_score | 0-2 | 0-2 | 0-2 | yes |
| end | concede_dustin | concede_dustin | concession by Dustin | yes |
| opponent_energy_zone | Lightning | Lightning | Lightning | yes |
| Pokemon names | Furfrou, Eevee, Oricorio, Sylveon, Shinx, Luxray | same set | same set | yes |
| attacks (name and damage) | Double Headbutt, Zzzap, Volt Bolt (names only; neither sheet lists damage) | same | same (30, 50 + 20, 120 + 20) | yes |
| trainers | Poke Ball, Professor's Research (T1 and T3), Protective Poncho, Giant Cape, Copycat, Rare Candy, Volkner | same, but "unreadable Tool (+20 HP)" for Giant Cape and no T3 Professor's Research | G's list is right (Giant Cape read at t_0297; T3 Professor's Research from t_0123-0127) | yes (G right over C) |
| special_conditions | none | none | none seen | yes |
| healed | true | true | true (Sylveon) | yes |
| bench_damage | false | false | false | yes |
| card of the game | Oricorio | Oricorio | Oricorio | yes |

Fields checked 12, matched 12.

## Could a player rely on Review G for this game?
Mostly yes for what happened and who won: every attack, damage number, Knock Out, point, evolution, heal, the 0-2 score, the concession and the result screen are right, and in three places it is more complete than the careful review (the turn 3 Professor's Research, Giant Cape, the Carvanha versions, and the Shinx attach time). It cannot be trusted for Energy bookkeeping on Dustin's side. It invents an Energy discard on every retreat of Mega Sharpedo ex (which has no retreat cost), so its board states from turn 8 on show 1 to 2 fewer Water than the frames, and in turn 15 it adds an opponent attach that never happened (Luxray 3 instead of 2). Two opponent Energy attaches (T7, T13) are placed on the wrong side of a retreat, and the deck list it cites is not on screen. It also does not explain why Dustin skipped attacking in turns 8, 10 and 12 (Safeguard). Someone using it to decide whether Dustin could have attacked, or to count Energy, would be misled; for the story of the game it is dependable.
