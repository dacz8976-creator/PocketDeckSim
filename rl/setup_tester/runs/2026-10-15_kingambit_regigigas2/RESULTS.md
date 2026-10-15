# Setup tester: kingambit_regigigas2

Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on the same deals for every version. It does not say who wins.
**Plan config follows SPEC_AMENDMENT_1 (Dustin, Oct 15) and the coordinator's rulings R1-R3 (Oct 15):** Regigigas leads; Pawniard is held until the bench trigger (first_ko; default first_ko = our first turn after one of ours was knocked out, a spot free); Grimer and Muk are benched, and an Active Alolan Grimer is never evolved into Muk (R2); a Glimmora has had its turn when it attacked at least once (R1); Energy goes to Kingambit up to [DD], then an Active Glimmora that has not attacked yet and has no [D], then the Pawniard line up to [DD], then Regigigas while Muk is in play (R1; the other order runs as a choices row). The lines that lead are P1-P5, P3 by cause (R2); the old G and K lines stay below "descriptive (speed is not the goal)". The slow pace is knockouts on their turns 3, 5 and 7 against a 180-HP Mega ex; the 220-HP Mega is a reference row with 10 own turns (R3). The no-knock-out runs have no knock-out to trigger first_ko, so Pawniard is benched at once (trigger "at_once") and no Bench slot is reserved; the old T-now reserved one.
**Copycat is played by his valuation, approximated** (Dustin, Oct 15: "an updated approximate valuation of card values, based on what I have in play, what cards are left in the deck, how many cards I have, they have, and whether a shuffle and new hand is likely to be more valuable to winning than keeping my current hand"): it is played when the expected value of a fresh hand beats the current hand's value under the value table below. A fresh hand is the opponent's hand count of cards from deck plus hand reshuffled, estimated from 16 sampled hands per decision drawn from the tester's own seed block. The value table is written from the plan's own needs, with no tuned constants; Dustin can correct a value.
**His rule, approximated, as a check:** the fallback rule runs on the base and on every version. The two disagree at base: 118,722 of 279,664 Copycat decisions (42.5%).
**WARNING, the Copycat rule changes a verdict:** -1 Poké Ball A2b 111 +1 Regigigas B3 134: fast P2.g1 - only under the fallback rule, ref190 P2.g1 - only under the fallback rule; -1 Rare Candy A3 144 +1 Regigigas B3 134: fast P4.late1 - only under the valuation, his P2.g1 + only under the fallback rule, his_seat P4.nomoment - only under the fallback rule, medium P4.nomoment - only under the fallback rule, slow P2.both - only under the valuation; -1 Ilima A3 149 +1 Regigigas B3 134: fast P2.both - only under the valuation, fast P4.ko + only under the valuation, fast P4.win + only under the valuation, his_seat P4.nomoment - only under the fallback rule, medium P2.any - only under the fallback rule, medium P4.ko + only under the fallback rule, medium P4.never - only under the valuation, medium P4.nomoment - only under the fallback rule, ref190 P2.both - only under the valuation, ref190 P4.nomoment - only under the valuation; -1 Professor's Research A4b 373 +1 Regigigas B3 134: fast P4.never + only under the valuation, slow P4.late1 + only under the valuation; -1 Heavy Helmet B1 219 +1 Regigigas B3 134: fast P2.any + only under the fallback rule, fast P2.both - only under the valuation, his_seat P4.nomoment - only under the fallback rule, medium P4.never - only under the valuation, medium P4.nomoment - only under the fallback rule, ref190 P4.nomoment - only under the valuation; -1 Copycat B1 225 +1 Regigigas B3 134: bot P2.g1 - only under the valuation, bot P4.ko - only under the valuation, bot P4.never + only under the valuation, bot P4.nomoment - only under the fallback rule, bot P5.ko - only under the valuation, fast P2.any - only under the valuation, fast P2.g1 + only under the fallback rule, fast P2.g1 - only under the valuation, fast P4.ko - only under the valuation, fast P4.never + only under the fallback rule, fast P4.nomoment + only under the valuation, fast P4.nomoment - only under the fallback rule, fast P4.win - only under the valuation, fast P5.ko - only under the valuation, fast P5.win - only under the valuation, his P2.g1 - only under the valuation, his P4.nomoment - only under the fallback rule, his_seat P4.nomoment - only under the fallback rule, medium P4.never + only under the fallback rule, medium P4.nomoment + only under the valuation, ref190 P2.any - only under the valuation, ref190 P2.g1 + only under the fallback rule, ref190 P2.g1 - only under the valuation, ref190 P4.never - only under the valuation, ref190 P4.nomoment + only under the valuation, ref220 P2.any - only under the valuation, ref220 P2.g1 - only under the valuation, ref220 P4.nomoment + only under the valuation, slow P2.g1 - only under the valuation, slow P4.ko - only under the valuation, slow P4.win - only under the valuation, slow P5.ko - only under the valuation, slow P5.win - only under the valuation; -1 Lucky Ice Pop B2 145 +1 Regigigas B3 134: fast P4.ko + only under the valuation, fast P4.win + only under the valuation, his_seat P4.nomoment - only under the fallback rule, medium P2.any - only under the fallback rule, medium P4.never - only under the valuation, medium P4.nomoment - only under the fallback rule, ref190 P4.nomoment - only under the valuation; -1 Mesagoza B2a 093 +1 Regigigas B3 134: fast P4.never + only under the valuation, medium P4.late1 - only under the valuation, ref190 P4.ko - only under the valuation, ref190 P4.win - only under the valuation, ref190 P5.ko - only under the valuation, ref190 P5.win - only under the valuation, slow P4.late1 + only under the valuation. The laptop shows Dustin one such hand.
**PROPOSED, not yet confirmed by Dustin:** the plan lines, the lead and promotion orders, the Copycat value table, and the assumed strongest Pokémon of C-fixed. Nothing here is to be reported to him as settled until he confirms or rewrites each.

## Copycat value table (his rule, approximated)

Each card in a hand is worth the value of the first row whose conditions all hold (the last row of a card always holds). A card not listed is worth 1. Conditions are read at the moment of the decision, for the hand being valued: pawniard_due = a Pawniard-line Pokémon is in play or the bench trigger is open; kingambit_held / kingambit_needed = Kingambit in that hand / none in play; no_pawniard_line_in_play; pawniard_in_play; bisharp_line_missing = no Bisharp or Kingambit in play; glimmora_lines_lt2 = fewer than two Glimmet lines in play; glimmet_waits = a Glimmet in play; muk_needed = no Muk in play; grimer_in_play; regigigas_missing; kingambit_in_deck; bench_room; no_stadium. Ilima, Lucky Ice Pop and Heavy Helmet act on damage, which the tester does not model, so they are worth the default.

| Card | rows: when (all of these) = value |
|---|---|
| Rare Candy | pawniard_due and kingambit_held and kingambit_needed = 8; otherwise = 1 |
| Kingambit | kingambit_needed and pawniard_due = 8; kingambit_needed = 5; otherwise = 1 |
| Pawniard | no_pawniard_line_in_play and pawniard_due = 8; no_pawniard_line_in_play = 4; otherwise = 1 |
| Bisharp | pawniard_in_play and bisharp_line_missing = 6; bisharp_line_missing = 3; otherwise = 1 |
| Glimmet | glimmora_lines_lt2 = 6; otherwise = 1 |
| Glimmora | glimmet_waits = 8; glimmora_lines_lt2 = 3; otherwise = 1 |
| Alolan Grimer | muk_needed = 4; otherwise = 1 |
| Alolan Muk | grimer_in_play and muk_needed = 6; muk_needed = 3; otherwise = 1 |
| Regigigas | regigigas_missing = 4; otherwise = 1 |
| Juliana | kingambit_needed and kingambit_in_deck = 6; otherwise = 1 |
| Poké Ball | bench_room = 3; otherwise = 1 |
| Pokémon Communication | kingambit_needed = 3; otherwise = 1 |
| Mesagoza | no_stadium = 4; otherwise = 0 |
| Professor's Research | otherwise = 3 |
| Lisia | bench_room = 3; otherwise = 1 |
| Sightseer | otherwise = 2 |
| Ilima | otherwise = 1 |
| Lucky Ice Pop | otherwise = 1 |
| Heavy Helmet | otherwise = 1 |

**The fallback rule (his rule, approximated)**: no must-keep card in hand (Kingambit, Rare Candy): Copycat on a gap of 2 or more between the opponent's hand and ours without the Copycat; a must-keep card in hand: only on a gap of 5 or more (his 2 v 8). It runs on the base and on every version beside the valuation; the two disagree at the rates below.

## base (card-list id 73dfed58d1d6)

Copycat decisions with a Copycat in hand: 279,664; the valuation and the fallback rule disagree at 118,722 of 279,664 Copycat decisions (42.5%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.2371.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03373; in 8 cards: 0.05246.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 28.8% (28.4-29.2) | 28.6% (28.2-29.0) | 28.7% (28.4-29.0) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 88.3% / 96.1% [77-95] | 78.2% / 90.6% [63-90] | 83.3% / 93.4% [70-93] |
| P2 both Glimmora had their turn | 38.5% / 70.1% [28-48] | 32.9% / 70.0% [22-46] | 35.7% / 70.1% [26-45] |
| P2 the first Glimmora placed had its turn | 84.7% / 91.4% [74-93] | 70.7% / 80.5% [55-85] | 77.7% / 85.9% [65-89] |
| P2 the second Glimmora placed had its turn | 42.1% / 69.5% [31-52] | 40.5% / 70.2% [29-53] | 41.3% / 69.9% [31-51] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 5.8% / 51.9% [1-12] | 6.4% / 55.3% [3-11] | 6.1% / 53.6% [2-11] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 27.3% / 65.0% [21-34] | 32.9% / 70.2% [26-40] | 30.1% / 67.6% [23-37] |
| P4 ready at the winning moment: Knocks out their strongest | 13.9% / 39.2% [3-27] | 10.2% / 38.7% [2-20] | 12.1% / 38.9% [2-23] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.7% / 28.0% [0-8] | 1.7% / 30.1% [0-5] | 2.2% / 29.1% [0-7] |
| P4 not ready, ready 1 turn late | 4.4% / 46.6% [0-11] | 3.7% / 50.0% [0-9] | 4.1% / 48.3% [0-10] |
| P4 not ready, ready 2 or more turns late | 1.4% / 43.6% [0-4] | 1.4% / 47.7% [0-4] | 1.4% / 45.6% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 7.8% / 50.0% [0-19] | 7.9% / 54.3% [0-19] | 7.9% / 52.2% [0-19] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.3% / 55.6% [9-55] | 30.4% / 58.8% [12-53] | 30.3% / 57.2% [11-54] |
| P5 plan reached in time: Knocks out their strongest | 19.6% / 61.9% [7-35] | 15.3% / 61.7% [5-27] | 17.5% / 61.8% [6-31] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.1% / 45.3% [0-9] | 2.1% / 48.4% [0-6] | 2.6% / 46.9% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 50.5% of 2749 [25-72] | 44.0% of 2329 [23-67] | 47.5% of 5078 [25-70] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 9.8% of 2749 [0-37] | 7.5% of 2329 [0-35] | 8.7% of 5078 [0-36] |
| P4 not ready, ready 1 turn late | 16.0% of 2749 [0-54] | 16.0% of 2329 [0-50] | 16.0% of 5078 [0-52] |
| P4 not ready, ready 2 or more turns late | 5.0% of 2749 [0-18] | 5.9% of 2329 [0-21] | 5.4% of 5078 [0-20] |
| P4 the moment came and Kingambit was never ready in the deal | 28.5% of 2749 [0-50] | 34.1% of 2329 [0-60] | 31.1% of 5078 [0-55] |

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.9% / 96.1% [71-96] | 88.2% / 94.6% [78-96] | 87.5% / 95.4% [79-94] |
| P2 both Glimmora had their turn | 39.0% / 66.5% [26-50] | 31.6% / 81.2% [22-45] | 35.3% / 73.8% [27-45] |
| P2 the first Glimmora placed had its turn | 83.0% / 91.3% [68-93] | 84.2% / 86.1% [73-94] | 83.6% / 88.7% [75-91] |
| P2 the second Glimmora placed had its turn | 42.9% / 66.6% [29-55] | 35.5% / 75.6% [27-51] | 39.2% / 71.1% [30-50] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.7% / 44.5% [1-5] | 12.6% / 78.7% [0-29] | 7.6% / 61.6% [1-16] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 27.1% / 61.2% [20-36] | 35.5% / 88.4% [18-45] | 31.3% / 74.8% [23-39] |
| P4 ready at the winning moment: Knocks out their strongest | 17.0% / 39.3% [2-34] | 4.0% / 56.2% [0-12] | 10.5% / 47.7% [2-21] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.3% / 26.6% [0-13] | 0.0% / 52.2% [0-0] | 2.2% / 39.4% [0-8] |
| P4 not ready, ready 1 turn late | 5.9% / 41.8% [0-15] | 0.0% / 77.2% [0-0] | 3.0% / 59.5% [0-9] |
| P4 not ready, ready 2 or more turns late | 1.8% / 37.6% [0-6] | 0.0% / 77.2% [0-0] | 0.9% / 57.4% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 11.1% / 47.0% [0-25] | 0.0% / 77.2% [0-0] | 5.6% / 62.1% [0-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.3% / 50.6% [6-58] | 18.8% / 71.0% [0-43] | 23.5% / 60.8% [8-44] |
| P5 plan reached in time: Knocks out their strongest | 24.7% / 60.6% [7-43] | 4.0% / 81.2% [0-12] | 14.4% / 70.9% [5-29] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.8% / 40.6% [0-15] | 0.0% / 77.2% [0-0] | 2.4% / 58.9% [0-9] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 47.5% of 3583 [15-67] | 100.0% of 404 [100-100] | 52.8% of 3987 [28-76] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.1% of 3583 [0-44] | 0.0% of 404 [0-0] | 10.9% of 3987 [0-37] |
| P4 not ready, ready 1 turn late | 16.5% of 3583 [0-64] | 0.0% of 404 [0-0] | 14.8% of 3987 [0-44] |
| P4 not ready, ready 2 or more turns late | 5.0% of 3583 [0-21] | 0.0% of 404 [0-0] | 4.5% of 3987 [0-15] |
| P4 the moment came and Kingambit was never ready in the deal | 31.0% of 3583 [0-55] | 0.0% of 404 [0-0] | 27.9% of 3987 [0-49] |

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.4% / 92.1% [89-94] | 82.7% / 84.0% [79-86] | 87.0% / 88.1% [84-90] |
| P2 both Glimmora had their turn | 42.2% / 47.7% [37-47] | 31.7% / 38.5% [27-36] | 37.0% / 43.1% [32-41] |
| P2 the first Glimmora placed had its turn | 84.9% / 85.1% [81-89] | 72.7% / 72.8% [67-78] | 78.8% / 78.9% [74-83] |
| P2 the second Glimmora placed had its turn | 48.6% / 52.6% [45-53] | 41.8% / 46.3% [38-46] | 45.2% / 49.5% [41-49] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 16.1% / 26.6% [12-20] | 15.6% / 26.6% [13-18] | 15.8% / 26.6% [13-19] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.1% / 44.5% [33-40] | 42.9% / 50.6% [40-46] | 39.5% / 47.5% [36-43] |
| P4 ready at the winning moment: Knocks out their strongest | 7.7% / 13.8% [4-12] | 6.6% / 13.9% [4-10] | 7.2% / 13.9% [4-11] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.3% / 6.4% [0-1] | 0.7% / 7.9% [0-2] | 0.5% / 7.2% [0-1] |
| P4 not ready, ready 1 turn late | 4.5% / 12.6% [2-7] | 3.7% / 13.5% [2-6] | 4.1% / 13.0% [2-6] |
| P4 not ready, ready 2 or more turns late | 1.5% / 9.6% [1-3] | 1.8% / 11.5% [1-3] | 1.6% / 10.6% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 8.6% / 16.6% [4-14] | 8.8% / 18.6% [4-14] | 8.7% / 17.6% [4-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.6% / 75.7% [58-80] | 69.2% / 76.5% [59-79] | 69.4% / 76.1% [59-80] |
| P5 plan reached in time: Knocks out their strongest | 13.7% / 21.8% [8-21] | 12.1% / 21.9% [7-18] | 12.9% / 21.9% [8-19] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.4% / 8.5% [0-1] | 0.7% / 10.5% [0-2] | 0.5% / 9.5% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 34.6% of 2229 [22-49] | 31.6% of 2098 [23-42] | 33.2% of 4327 [23-45] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.3% of 2229 [0-5] | 3.1% of 2098 [0-11] | 2.2% of 4327 [0-7] |
| P4 not ready, ready 1 turn late | 20.2% of 2229 [12-29] | 17.7% of 2098 [12-24] | 19.0% of 4327 [12-26] |
| P4 not ready, ready 2 or more turns late | 6.8% of 2229 [3-12] | 8.4% of 2098 [4-14] | 7.6% of 4327 [3-12] |
| P4 the moment came and Kingambit was never ready in the deal | 38.4% of 2229 [26-52] | 42.2% of 2098 [30-54] | 40.2% of 4327 [28-53] |

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.8% [81-83, Wilson] | 53.0% [52-54, Wilson] | 67.4% [67-68, Wilson] |
| P2 both Glimmora had their turn | 28.1% [27-29, Wilson] | 8.4% [8-9, Wilson] | 18.3% [18-19, Wilson] |
| P2 the first Glimmora placed had its turn | 76.7% [76-78, Wilson] | 33.2% [32-34, Wilson] | 55.0% [54-56, Wilson] |
| P2 the second Glimmora placed had its turn | 33.2% [32-34, Wilson] | 28.2% [27-29, Wilson] | 30.7% [30-31, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 21.7% [21-23, Wilson] | 19.0% [18-20, Wilson] | 20.3% [20-21, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 57.4% [56-58, Wilson] | 54.6% [54-56, Wilson] | 56.0% [55-57, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 16.2% [15-17, Wilson] | 5.3% [5-6, Wilson] | 10.7% [10-11, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 16.2% [15-17, Wilson] | 5.3% [5-6, Wilson] | 10.7% [10-11, Wilson] |
| P4 not ready, ready 1 turn late | 2.1% [2-2, Wilson] | 0.6% [0-1, Wilson] | 1.4% [1-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.6% [24-25, Wilson] | 17.8% [17-19, Wilson] | 21.2% [21-22, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 57.1% [56-58, Wilson] | 76.3% [75-77, Wilson] | 66.7% [66-67, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 18.3% [18-19, Wilson] | 5.9% [5-6, Wilson] | 12.1% [12-13, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 18.3% [18-19, Wilson] | 5.9% [5-6, Wilson] | 12.1% [12-13, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 37.7% of 4290 [36-39, Wilson] | 22.4% of 2368 [21-24, Wilson] | 32.2% of 6658 [31-33, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 37.7% of 4290 [36-39, Wilson] | 22.4% of 2368 [21-24, Wilson] | 32.2% of 6658 [31-33, Wilson] |
| P4 not ready, ready 1 turn late | 4.9% of 4290 [4-6, Wilson] | 2.6% of 2368 [2-3, Wilson] | 4.1% of 6658 [4-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4290 [0-0, Wilson] | 0.0% of 2368 [0-0, Wilson] | 0.0% of 6658 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 57.4% of 4290 [56-59, Wilson] | 75.0% of 2368 [73-77, Wilson] | 63.7% of 6658 [63-65, Wilson] |

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.5% [90-91, Wilson] | 81.6% [81-82, Wilson] | 86.0% [86-87, Wilson] |
| P2 both Glimmora had their turn | 39.7% [39-41, Wilson] | 28.3% [27-29, Wilson] | 34.0% [33-35, Wilson] |
| P2 the first Glimmora placed had its turn | 87.2% [87-88, Wilson] | 77.2% [76-78, Wilson] | 82.2% [82-83, Wilson] |
| P2 the second Glimmora placed had its turn | 43.0% [42-44, Wilson] | 32.7% [32-34, Wilson] | 37.9% [37-39, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 25.1% [24-26, Wilson] | 22.9% [22-24, Wilson] | 23.9% [23-25, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 55.1% [54-56, Wilson] | 58.4% [57-59, Wilson] | 56.7% [56-57, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 27.1% [26-28, Wilson] | 16.3% [16-17, Wilson] | 21.7% [21-22, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.7% [2-3, Wilson] | 2.1% [2-2, Wilson] | 2.4% [2-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.8% [24-26, Wilson] | 25.0% [24-26, Wilson] | 24.9% [24-25, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 45.4% [44-46, Wilson] | 56.5% [56-57, Wilson] | 51.0% [50-52, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 29.8% [29-31, Wilson] | 18.4% [18-19, Wilson] | 24.1% [24-25, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 49.7% of 5458 [48-51, Wilson] | 37.6% of 4348 [36-39, Wilson] | 44.4% of 9806 [43-45, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5458 [0-0, Wilson] | 0.0% of 4348 [0-0, Wilson] | 0.0% of 9806 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 4.9% of 5458 [4-6, Wilson] | 4.8% of 4348 [4-6, Wilson] | 4.9% of 9806 [4-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5458 [0-0, Wilson] | 0.0% of 4348 [0-0, Wilson] | 0.0% of 9806 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 45.3% of 5458 [44-47, Wilson] | 57.6% of 4348 [56-59, Wilson] | 50.8% of 9806 [50-52, Wilson] |

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.6% [95-96, Wilson] | 89.9% [89-90, Wilson] | 92.8% [92-93, Wilson] |
| P2 both Glimmora had their turn | 70.3% [69-71, Wilson] | 54.2% [53-55, Wilson] | 62.3% [62-63, Wilson] |
| P2 the first Glimmora placed had its turn | 90.2% [90-91, Wilson] | 81.6% [81-82, Wilson] | 85.9% [85-86, Wilson] |
| P2 the second Glimmora placed had its turn | 75.7% [75-77, Wilson] | 62.5% [62-63, Wilson] | 69.1% [68-70, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 5.3% [5-6, Wilson] | 8.2% [8-9, Wilson] | 6.7% [6-7, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.0% [30-32, Wilson] | 40.6% [40-42, Wilson] | 35.8% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 49.2% [48-50, Wilson] | 39.8% [39-41, Wilson] | 44.5% [44-45, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 49.2% [48-50, Wilson] | 39.8% [39-41, Wilson] | 44.5% [44-45, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 4.2% [4-5, Wilson] | 2.1% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 15.1% [14-16, Wilson] | 12.8% [12-13, Wilson] | 14.0% [13-14, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 35.7% [35-37, Wilson] | 43.2% [42-44, Wilson] | 39.4% [39-40, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 49.2% [48-50, Wilson] | 44.0% [43-45, Wilson] | 46.6% [46-47, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 49.2% [48-50, Wilson] | 44.0% [43-45, Wilson] | 46.6% [46-47, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 76.5% of 6433 [75-78, Wilson] | 70.1% of 5678 [69-71, Wilson] | 73.5% of 12111 [73-74, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 76.5% of 6433 [75-78, Wilson] | 70.1% of 5678 [69-71, Wilson] | 73.5% of 12111 [73-74, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 6433 [0-0, Wilson] | 7.3% of 5678 [7-8, Wilson] | 3.4% of 12111 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 6433 [0-0, Wilson] | 0.0% of 5678 [0-0, Wilson] | 0.0% of 12111 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 23.5% of 6433 [22-25, Wilson] | 22.6% of 5678 [22-24, Wilson] | 23.1% of 12111 [22-24, Wilson] |

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.0% [81-83, Wilson] | 53.0% [52-54, Wilson] | 67.5% [67-68, Wilson] |
| P2 both Glimmora had their turn | 28.4% [28-29, Wilson] | 8.4% [8-9, Wilson] | 18.4% [18-19, Wilson] |
| P2 the first Glimmora placed had its turn | 76.7% [76-78, Wilson] | 33.2% [32-34, Wilson] | 55.0% [54-56, Wilson] |
| P2 the second Glimmora placed had its turn | 33.6% [33-35, Wilson] | 28.3% [27-29, Wilson] | 30.9% [30-32, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 24.0% [23-25, Wilson] | 19.6% [19-20, Wilson] | 21.8% [21-22, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 57.4% [56-58, Wilson] | 54.6% [54-56, Wilson] | 56.0% [55-57, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 3.6% [3-4, Wilson] | 0.9% [1-1, Wilson] | 2.2% [2-2, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.6% [3-4, Wilson] | 0.9% [1-1, Wilson] | 2.2% [2-2, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 4.4% [4-5, Wilson] | 1.7% [1-2, Wilson] | 3.1% [3-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 92.0% [91-93, Wilson] | 97.4% [97-98, Wilson] | 94.7% [94-95, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 3.6% [3-4, Wilson] | 0.9% [1-1, Wilson] | 2.2% [2-2, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.6% [3-4, Wilson] | 0.9% [1-1, Wilson] | 2.2% [2-2, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 44.9% of 799 [42-48, Wilson] | 34.2% of 263 [29-40, Wilson] | 42.3% of 1062 [39-45, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 44.9% of 799 [42-48, Wilson] | 34.2% of 263 [29-40, Wilson] | 42.3% of 1062 [39-45, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 799 [0-0, Wilson] | 0.0% of 263 [0-1, Wilson] | 0.0% of 1062 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 799 [0-0, Wilson] | 0.0% of 263 [0-1, Wilson] | 0.0% of 1062 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 55.1% of 799 [52-58, Wilson] | 65.8% of 263 [60-71, Wilson] | 57.7% of 1062 [55-61, Wilson] |

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.6% [95-96, Wilson] | 89.9% [89-90, Wilson] | 92.8% [92-93, Wilson] |
| P2 both Glimmora had their turn | 72.0% [71-73, Wilson] | 56.6% [56-58, Wilson] | 64.3% [64-65, Wilson] |
| P2 the first Glimmora placed had its turn | 90.2% [90-91, Wilson] | 81.6% [81-82, Wilson] | 85.9% [85-86, Wilson] |
| P2 the second Glimmora placed had its turn | 77.4% [77-78, Wilson] | 64.9% [64-66, Wilson] | 71.1% [70-72, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 38.5% [38-39, Wilson] | 31.4% [31-32, Wilson] | 35.0% [34-36, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 44.1% [43-45, Wilson] | 49.9% [49-51, Wilson] | 47.0% [46-48, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 5.9% [5-6, Wilson] | 7.2% [7-8, Wilson] | 6.5% [6-7, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 5.9% [5-6, Wilson] | 7.2% [7-8, Wilson] | 6.5% [6-7, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.2% [0-0, Wilson] | 0.1% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 13.5% [13-14, Wilson] | 9.9% [9-11, Wilson] | 11.7% [11-12, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 80.6% [80-81, Wilson] | 82.7% [82-83, Wilson] | 81.7% [81-82, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 5.9% [5-6, Wilson] | 7.4% [7-8, Wilson] | 6.6% [6-7, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.9% [5-6, Wilson] | 7.4% [7-8, Wilson] | 6.6% [6-7, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 30.4% of 1938 [28-33, Wilson] | 41.6% of 1730 [39-44, Wilson] | 35.7% of 3668 [34-37, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 30.4% of 1938 [28-33, Wilson] | 41.6% of 1730 [39-44, Wilson] | 35.7% of 3668 [34-37, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1938 [0-0, Wilson] | 1.2% of 1730 [1-2, Wilson] | 0.5% of 3668 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1938 [0-0, Wilson] | 0.0% of 1730 [0-0, Wilson] | 0.0% of 3668 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 69.6% of 1938 [67-72, Wilson] | 57.3% of 1730 [55-60, Wilson] | 63.8% of 3668 [62-65, Wilson] |

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 29.2% (28.8-29.6) | 28.8% (28.4-29.2) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 55.9% (55.5-56.4) | 55.6% (55.2-56.0) | 55.8% (55.5-56.1) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 67.9% (67.5-68.3) | 67.8% (67.4-68.2) | 67.9% (67.6-68.2) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 74.5% (74.1-74.9) | 74.5% (74.2-74.9) | 74.5% (74.2-74.8) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 78.6% (78.2-78.9) | 78.6% (78.3-79.0) | 78.6% (78.4-78.9) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 80.8% (80.5-81.2) | 80.8% (80.4-81.1) | 80.8% (80.5-81.0) |
| K2 Kingambit in play, own turn 2 | 10.7% (10.5-11.0) | 10.8% (10.5-11.0) | 10.7% (10.5-10.9) |
| K2 Kingambit in play, own turn 3 | 21.1% (20.7-21.4) | 21.1% (20.8-21.5) | 21.1% (20.8-21.3) |
| K2 Kingambit in play, own turn 4 | 33.0% (32.6-33.4) | 33.1% (32.7-33.5) | 33.1% (32.8-33.4) |
| K2 Kingambit in play, own turn 5 | 46.4% (46.0-46.9) | 46.4% (46.0-46.9) | 46.4% (46.1-46.7) |
| K2 Kingambit in play, own turn 6 | 59.4% (59.0-59.9) | 59.1% (58.7-59.6) | 59.3% (59.0-59.6) |
| K6 Muk and Regigigas both in play, own turn 3 | 22.2% (21.8-22.6) | 22.3% (21.9-22.6) | 22.2% (22.0-22.5) |
| K6 Muk and Regigigas both in play, own turn 4 | 30.4% (30.0-30.8) | 30.5% (30.1-30.9) | 30.4% (30.2-30.7) |
| K6 Muk and Regigigas both in play, own turn 5 | 36.9% (36.5-37.4) | 37.0% (36.6-37.4) | 37.0% (36.7-37.3) |
| G3 Pawniard in play, own turn 1 | 55.9% (55.5-56.4) | 55.6% (55.2-56.0) | 55.8% (55.5-56.1) |
| G3 Pawniard in play, own turn 2 | 57.2% (56.8-57.6) | 57.1% (56.6-57.5) | 57.1% (56.8-57.4) |
| G3 Pawniard in play, own turn 3 | 53.4% (53.0-53.9) | 53.4% (53.0-53.9) | 53.4% (53.1-53.7) |
| G3 Pawniard in play, own turn 4 | 45.6% (45.1-46.0) | 45.5% (45.1-45.9) | 45.5% (45.2-45.9) |
| G3 Pawniard in play, own turn 5 | 34.4% (34.0-34.8) | 34.4% (33.9-34.8) | 34.4% (34.1-34.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 10.7% (10.5-11.0) | 10.8% (10.5-11.0) | 10.7% (10.5-10.9) |
| G3 Kingambit in play, own turn 3 | 21.1% (20.7-21.4) | 21.1% (20.8-21.5) | 21.1% (20.8-21.3) |
| G3 Kingambit in play, own turn 4 | 33.0% (32.6-33.4) | 33.1% (32.7-33.5) | 33.1% (32.8-33.4) |
| G3 Kingambit in play, own turn 5 | 46.4% (46.0-46.9) | 46.4% (46.0-46.9) | 46.4% (46.1-46.7) |
| G3 Alolan Grimer in play, own turn 1 | 54.6% (54.2-55.0) | 54.7% (54.3-55.2) | 54.7% (54.4-55.0) |
| G3 Alolan Grimer in play, own turn 2 | 46.3% (45.8-46.7) | 46.6% (46.1-47.0) | 46.4% (46.1-46.7) |
| G3 Alolan Grimer in play, own turn 3 | 39.9% (39.5-40.4) | 40.0% (39.6-40.5) | 40.0% (39.7-40.3) |
| G3 Alolan Grimer in play, own turn 4 | 33.0% (32.6-33.4) | 33.2% (32.8-33.6) | 33.1% (32.8-33.4) |
| G3 Alolan Grimer in play, own turn 5 | 26.7% (26.3-27.1) | 27.0% (26.7-27.4) | 26.9% (26.6-27.1) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 18.9% (18.5-19.2) | 18.9% (18.6-19.3) | 18.9% (18.7-19.1) |
| G3 Alolan Muk in play, own turn 3 | 31.1% (30.7-31.5) | 31.4% (31.0-31.8) | 31.2% (30.9-31.5) |
| G3 Alolan Muk in play, own turn 4 | 41.2% (40.7-41.6) | 41.3% (40.9-41.8) | 41.3% (41.0-41.6) |
| G3 Alolan Muk in play, own turn 5 | 49.3% (48.8-49.7) | 49.2% (48.8-49.7) | 49.2% (48.9-49.6) |
| G3 Glimmet in play, own turn 1 | 82.1% (81.8-82.4) | 82.4% (82.1-82.8) | 82.3% (82.0-82.5) |
| G3 Glimmet in play, own turn 2 | 52.8% (52.4-53.2) | 52.4% (52.0-52.9) | 52.6% (52.3-52.9) |
| G3 Glimmet in play, own turn 3 | 42.2% (41.7-42.6) | 41.9% (41.5-42.3) | 42.0% (41.7-42.3) |
| G3 Glimmet in play, own turn 4 | 30.9% (30.5-31.4) | 30.9% (30.5-31.3) | 30.9% (30.6-31.2) |
| G3 Glimmet in play, own turn 5 | 20.1% (19.8-20.5) | 19.8% (19.5-20.2) | 20.0% (19.7-20.2) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 63.2% (62.7-63.6) | 63.3% (62.9-63.8) | 63.2% (62.9-63.5) |
| G3 Glimmora in play, own turn 3 | 79.7% (79.4-80.1) | 79.9% (79.6-80.3) | 79.8% (79.6-80.1) |
| G3 Glimmora in play, own turn 4 | 89.4% (89.2-89.7) | 89.4% (89.2-89.7) | 89.4% (89.2-89.6) |
| G3 Glimmora in play, own turn 5 | 95.1% (94.9-95.3) | 95.1% (94.9-95.3) | 95.1% (95.0-95.2) |
| G3 Regigigas in play, own turn 1 | 55.4% (55.0-55.8) | 55.2% (54.8-55.7) | 55.3% (55.0-55.6) |
| G3 Regigigas in play, own turn 2 | 67.7% (67.2-68.1) | 67.1% (66.7-67.5) | 67.4% (67.1-67.7) |
| G3 Regigigas in play, own turn 3 | 74.4% (74.1-74.8) | 74.2% (73.8-74.5) | 74.3% (74.0-74.6) |
| G3 Regigigas in play, own turn 4 | 78.2% (77.9-78.6) | 78.1% (77.8-78.5) | 78.2% (77.9-78.4) |
| G3 Regigigas in play, own turn 5 | 80.3% (80.0-80.7) | 80.2% (79.8-80.5) | 80.2% (80.0-80.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 75.5% (75.1-75.9) | 75.7% (75.3-76.0) | 75.6% (75.3-75.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 89.6% (89.4-89.9) | 89.8% (89.5-90.0) | 89.7% (89.5-89.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 95.9% (95.8-96.1) | 95.9% (95.7-96.0) | 95.9% (95.8-96.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.6% (98.5-98.7) | 98.6% (98.5-98.7) | 98.6% (98.5-98.7) |
| G4.s2 a Stage 2 in play, own turn 2 | 10.7% (10.5-11.0) | 10.8% (10.5-11.0) | 10.7% (10.5-10.9) |
| G4.s2 a Stage 2 in play, own turn 3 | 21.1% (20.7-21.4) | 21.1% (20.8-21.5) | 21.1% (20.8-21.3) |
| G4.s2 a Stage 2 in play, own turn 4 | 33.0% (32.6-33.4) | 33.1% (32.7-33.5) | 33.1% (32.8-33.4) |
| G4.s2 a Stage 2 in play, own turn 5 | 46.4% (46.0-46.9) | 46.4% (46.0-46.9) | 46.4% (46.1-46.7) |
| G5.any3 an empty own turn among turns 1-3 | 23.1% (22.8-23.5) | 22.5% (22.1-22.9) | 22.8% (22.6-23.1) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.8% (10.5-11.0) | 5.4% (5.2-5.5) |
| G6 Kingambit with [DD] attached, own turn 3 | 17.6% (17.2-17.9) | 21.1% (20.8-21.5) | 19.3% (19.1-19.6) |
| G6 Kingambit with [DD] attached, own turn 4 | 33.0% (32.6-33.4) | 33.1% (32.7-33.5) | 33.1% (32.8-33.4) |
| G6 Kingambit with [DD] attached, own turn 5 | 46.4% (46.0-46.9) | 46.4% (46.0-46.9) | 46.4% (46.1-46.7) |
| G5 mean empty own turns in turns 1-5 | 0.762 | 0.755 | 0.758 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.3% / 10.7% [2-3] | 1.1% / 5.3% [1-2] |
| K3.by3 | 3.5% / 12.2% [2-5] | 2.9% / 11.3% [2-4] | 3.2% / 11.7% [2-4] |
| K3.by4 | 4.3% / 12.9% [3-6] | 4.9% / 13.3% [4-6] | 4.6% / 13.1% [3-6] |
| K3.by5 | 6.5% / 15.2% [5-9] | 5.7% / 21.1% [4-7] | 6.1% / 18.1% [4-8] |
| K3.by6 | 7.0% / 23.5% [5-9] | 10.6% / 33.9% [6-17] | 8.8% / 28.7% [6-12] |
| K3.by7 | 14.2% / 38.5% [7-24] | 12.3% / 57.2% [6-20] | 13.3% / 47.9% [7-22] |
| K3.by8 | 17.0% / 63.6% [7-28] | 12.4% / 61.5% [6-20] | 14.7% / 62.6% [7-24] |
| K3.never | 36.4% / 83.0% [16-59] | 38.5% / 87.6% [17-61] | 37.4% / 85.3% [17-60] |
| K3.k0 | 4.6% / 51.3% [3-6] | 3.2% / 52.4% [2-5] | 3.9% / 51.8% [2-6] |
| K3.k1 | 0.0% / 46.6% [0-0] | 0.0% / 49.1% [0-0] | 0.0% / 47.9% [0-0] |
| K3.k2 | 7.4% / 54.0% [1-17] | 6.2% / 55.4% [2-13] | 6.8% / 54.7% [1-15] |
| K3.k3p | 5.0% / 51.6% [0-12] | 2.9% / 52.0% [0-7] | 3.9% / 51.8% [0-10] |
| K4 | 12.4% / 61.4% [2-24] | 9.1% / 60.0% [3-17] | 10.8% / 60.7% [3-20] |
| K5 | 7.2% / 61.9% [5-9] | 9.1% / 59.8% [7-12] | 8.1% / 60.9% [6-10] |

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.1% [3-3] | 1.6% [0-2] |
| K3.by3 | 3.3% / 14.6% [2-5] | 4.1% [3-5] | 3.7% / 9.3% [3-5] |
| K3.by4 | 3.9% / 15.2% [2-6] | 5.6% [4-7] | 4.7% / 10.4% [3-6] |
| K3.by5 | 6.2% / 17.5% [4-9] | 6.5% / 33.8% [5-7] | 6.3% / 25.7% [5-8] |
| K3.by6 | 6.7% / 18.0% [4-9] | 7.0% / 34.4% [5-9] | 6.9% / 26.2% [5-8] |
| K3.by7 | 16.7% / 38.9% [6-31] | 14.3% / 72.7% [5-31] | 15.5% / 55.8% [7-26] |
| K3.by8 | 16.7% / 58.7% [6-31] | 14.3% / 83.0% [5-31] | 15.5% / 70.8% [7-26] |
| K3.never | 41.3% / 83.3% [15-69] | 17.0% / 85.7% [0-38] | 29.2% / 84.5% [13-50] |
| K3.k0 | 4.2% / 46.2% [2-6] | 4.7% / 73.3% [3-7] | 4.4% / 59.7% [3-6] |
| K3.k1 | 0.0% / 42.0% [0-0] | 0.0% / 68.6% [0-0] | 0.0% / 55.3% [0-0] |
| K3.k2 | 9.0% / 51.0% [1-22] | 2.4% / 71.0% [0-4] | 5.7% / 61.0% [1-13] |
| K3.k3p | 3.5% / 45.5% [0-11] | 7.3% / 75.9% [0-22] | 5.4% / 60.7% [0-13] |
| K4 | 12.5% / 56.2% [1-27] | 9.7% / 82.2% [0-27] | 11.1% / 69.2% [2-22] |
| K5 | 7.5% / 54.4% [5-10] | 8.6% / 83.2% [5-11] | 8.0% / 68.8% [6-10] |

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.6% [2-3] | 1.3% [1-1] |
| K3.by3 | 3.7% [3-4] | 3.2% [3-4] | 3.4% [3-4] |
| K3.by4 | 4.6% [4-5] | 4.6% [4-5] | 4.6% [4-5] |
| K3.by5 | 5.9% [5-7] | 7.0% [6-8] | 6.5% [6-7] |
| K3.by6 | 8.0% [7-9] | 9.3% / 13.2% [8-11] | 8.7% / 10.6% [7-10] |
| K3.by7 | 10.5% / 14.8% [8-13] | 11.1% / 20.5% [9-14] | 10.8% / 17.6% [9-13] |
| K3.by8 | 12.5% / 22.9% [10-16] | 12.1% / 23.0% [9-15] | 12.3% / 22.9% [10-15] |
| K3.never | 77.1% / 87.5% [69-84] | 77.0% / 87.9% [70-83] | 77.1% / 87.7% [69-83] |
| K3.k0 | 4.8% / 15.2% [4-6] | 3.5% / 14.3% [3-4] | 4.2% / 14.8% [4-5] |
| K3.k1 | 0.0% / 10.4% [0-0] | 0.0% / 10.8% [0-0] | 0.0% / 10.6% [0-0] |
| K3.k2 | 2.8% / 13.2% [2-4] | 4.0% / 14.8% [3-5] | 3.4% / 14.0% [2-5] |
| K3.k3p | 4.8% / 15.2% [2-8] | 4.7% / 15.5% [3-7] | 4.8% / 15.4% [3-8] |
| K4 | 7.6% / 18.8% [5-11] | 8.7% / 20.1% [6-11] | 8.2% / 19.4% [6-11] |
| K5 | 8.5% / 22.0% [8-9] | 10.7% / 22.3% [10-12] | 9.6% / 22.1% [9-10] |

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.4% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by4 | 2.3% [2-3, Wilson] | 5.6% [5-6, Wilson] | 4.0% [4-4, Wilson] |
| K3.by5 | 12.4% [12-13, Wilson] | 6.5% [6-7, Wilson] | 9.5% [9-10, Wilson] |
| K3.by6 | 15.9% [15-17, Wilson] | 6.5% [6-7, Wilson] | 11.2% [11-12, Wilson] |
| K3.by7 | 15.9% [15-17, Wilson] | 6.5% [6-7, Wilson] | 11.2% [11-12, Wilson] |
| K3.by8 | 15.9% [15-17, Wilson] | 6.5% [6-7, Wilson] | 11.2% [11-12, Wilson] |
| K3.never | 84.1% [83-85, Wilson] | 93.5% [93-94, Wilson] | 88.8% [88-89, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.3% [2-3, Wilson] | 2.4% [2-3, Wilson] | 2.4% [2-3, Wilson] |
| K3.k3p | 13.6% [13-14, Wilson] | 4.1% [4-4, Wilson] | 8.8% [8-9, Wilson] |
| K4 | 15.9% [15-17, Wilson] | 6.5% [6-7, Wilson] | 11.2% [11-12, Wilson] |
| K5 | 19.0% [18-20, Wilson] | 24.5% [24-25, Wilson] | 21.7% [21-22, Wilson] |

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 3.0% [3-3, Wilson] | 1.5% [1-2, Wilson] |
| K3.by3 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by4 | 4.4% [4-5, Wilson] | 5.8% [5-6, Wilson] | 5.1% [5-5, Wilson] |
| K3.by5 | 6.1% [6-7, Wilson] | 16.0% [15-17, Wilson] | 11.0% [11-11, Wilson] |
| K3.by6 | 24.7% [24-26, Wilson] | 19.6% [19-20, Wilson] | 22.1% [22-23, Wilson] |
| K3.by7 | 29.8% [29-31, Wilson] | 19.6% [19-20, Wilson] | 24.7% [24-25, Wilson] |
| K3.by8 | 29.8% [29-31, Wilson] | 19.6% [19-20, Wilson] | 24.7% [24-25, Wilson] |
| K3.never | 70.2% [69-71, Wilson] | 80.4% [80-81, Wilson] | 75.3% [75-76, Wilson] |
| K3.k0 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.7% [1-2, Wilson] | 2.7% [2-3, Wilson] | 2.2% [2-2, Wilson] |
| K3.k3p | 23.7% [23-25, Wilson] | 13.8% [13-14, Wilson] | 18.7% [18-19, Wilson] |
| K4 | 25.4% [25-26, Wilson] | 16.5% [16-17, Wilson] | 20.9% [20-22, Wilson] |
| K5 | 13.7% [13-14, Wilson] | 18.9% [18-20, Wilson] | 16.3% [16-17, Wilson] |

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 3.0% [3-3, Wilson] | 1.5% [1-2, Wilson] |
| K3.by3 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by4 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by5 | 4.4% [4-5, Wilson] | 8.0% [7-9, Wilson] | 6.2% [6-7, Wilson] |
| K3.by6 | 8.0% [7-9, Wilson] | 8.3% [8-9, Wilson] | 8.1% [8-9, Wilson] |
| K3.by7 | 8.1% [8-9, Wilson] | 40.7% [40-42, Wilson] | 24.4% [24-25, Wilson] |
| K3.by8 | 51.2% [50-52, Wilson] | 40.9% [40-42, Wilson] | 46.1% [45-47, Wilson] |
| K3.never | 48.8% [48-50, Wilson] | 59.1% [58-60, Wilson] | 53.9% [53-55, Wilson] |
| K3.k0 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.7% [3-4, Wilson] | 5.3% [5-6, Wilson] | 4.5% [4-5, Wilson] |
| K3.k3p | 43.1% [42-44, Wilson] | 32.6% [32-34, Wilson] | 37.9% [37-39, Wilson] |
| K4 | 46.8% [46-48, Wilson] | 37.9% [37-39, Wilson] | 42.4% [42-43, Wilson] |
| K5 | 9.1% [9-10, Wilson] | 10.8% [10-11, Wilson] | 10.0% [10-10, Wilson] |

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.4% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by4 | 2.3% [2-3, Wilson] | 5.5% [5-6, Wilson] | 3.9% [4-4, Wilson] |
| K3.by5 | 11.6% [11-12, Wilson] | 6.4% [6-7, Wilson] | 9.0% [9-9, Wilson] |
| K3.by6 | 15.2% [14-16, Wilson] | 6.4% [6-7, Wilson] | 10.8% [10-11, Wilson] |
| K3.by7 | 15.2% [14-16, Wilson] | 6.4% [6-7, Wilson] | 10.8% [10-11, Wilson] |
| K3.by8 | 15.2% [14-16, Wilson] | 6.4% [6-7, Wilson] | 10.8% [10-11, Wilson] |
| K3.never | 84.8% [84-86, Wilson] | 93.6% [93-94, Wilson] | 89.2% [89-90, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.3% [2-3, Wilson] | 2.4% [2-3, Wilson] | 2.4% [2-3, Wilson] |
| K3.k3p | 12.8% [12-14, Wilson] | 4.0% [4-4, Wilson] | 8.4% [8-9, Wilson] |
| K4 | 15.2% [14-16, Wilson] | 6.4% [6-7, Wilson] | 10.8% [10-11, Wilson] |
| K5 | 19.0% [18-20, Wilson] | 24.5% [24-25, Wilson] | 21.7% [21-22, Wilson] |

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 3.0% [3-3, Wilson] | 1.5% [1-2, Wilson] |
| K3.by3 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by4 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by5 | 4.4% [4-5, Wilson] | 8.0% [7-9, Wilson] | 6.2% [6-7, Wilson] |
| K3.by6 | 8.0% [7-9, Wilson] | 8.3% [8-9, Wilson] | 8.1% [8-9, Wilson] |
| K3.by7 | 8.1% [8-9, Wilson] | 32.1% [31-33, Wilson] | 20.1% [20-21, Wilson] |
| K3.by8 | 41.9% [41-43, Wilson] | 32.3% [31-33, Wilson] | 37.1% [36-38, Wilson] |
| K3.by9 | 42.0% [41-43, Wilson] | 39.5% [39-40, Wilson] | 40.7% [40-41, Wilson] |
| K3.by10 | 47.9% [47-49, Wilson] | 39.7% [39-41, Wilson] | 43.8% [43-44, Wilson] |
| K3.never | 52.1% [51-53, Wilson] | 60.3% [59-61, Wilson] | 56.2% [56-57, Wilson] |
| K3.k0 | 4.4% [4-5, Wilson] | 3.0% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.7% [3-4, Wilson] | 5.3% [5-6, Wilson] | 4.5% [4-5, Wilson] |
| K3.k3p | 39.8% [39-41, Wilson] | 31.3% [30-32, Wilson] | 35.6% [35-36, Wilson] |
| K4 | 43.5% [43-44, Wilson] | 36.6% [36-38, Wilson] | 40.1% [39-41, Wilson] |
| K5 | 9.2% [9-10, Wilson] | 11.0% [10-12, Wilson] | 10.1% [10-11, Wilson] |

**Plain summary, base.**

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Poké Ball A2b 111 +1 Regigigas B3 134 (card-list id 4e00417356c7)

Changes: ['-1 Poké Ball A2b 111', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 280,600; the valuation and the fallback rule disagree at 115,509 of 280,600 Copycat decisions (41.2%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.2408, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 29/34/39/44/49%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 49.1% (48.6-49.5) | 48.5% (48.1-48.9) | 48.8% (48.5-49.1) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 83.5% / 94.1% [71-92] | 74.0% / 88.4% [59-86] | 78.8% / 91.2% [65-89] |
| P2 both Glimmora had their turn | 25.9% / 64.4% [19-33] | 22.4% / 64.4% [15-32] | 24.2% / 64.4% [17-31] |
| P2 the first Glimmora placed had its turn | 81.1% / 90.1% [69-89] | 69.1% / 80.6% [54-83] | 75.1% / 85.3% [62-86] |
| P2 the second Glimmora placed had its turn | 28.4% / 64.1% [20-36] | 27.4% / 64.3% [19-36] | 27.9% / 64.2% [20-35] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9] | 8.7% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.3% / 49.5% [1-4] | 3.7% / 54.4% [2-6] | 3.0% / 52.0% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.5% / 59.2% [14-21] | 22.3% / 64.7% [18-27] | 19.9% / 62.0% [16-24] |
| P4 ready at the winning moment: Knocks out their strongest | 11.7% / 37.1% [2-22] | 8.4% / 36.2% [2-16] | 10.0% / 36.7% [2-19] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.3% / 27.7% [0-7] | 1.5% / 29.3% [0-5] | 1.9% / 28.5% [0-6] |
| P4 not ready, ready 1 turn late | 4.0% / 46.5% [0-10] | 3.2% / 49.2% [0-7] | 3.6% / 47.8% [0-9] |
| P4 not ready, ready 2 or more turns late | 1.6% / 44.1% [0-5] | 1.7% / 47.7% [0-5] | 1.6% / 45.9% [0-5] |
| P4 the moment came and Kingambit was never ready in the deal | 9.5% / 52.0% [0-22] | 9.5% / 55.5% [0-23] | 9.5% / 53.8% [0-23] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.7% / 56.1% [9-56] | 31.3% / 59.1% [12-54] | 31.0% / 57.6% [11-55] |
| P5 plan reached in time: Knocks out their strongest | 17.3% / 59.8% [6-32] | 13.2% / 59.2% [4-23] | 15.2% / 59.5% [5-28] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.6% / 45.1% [0-8] | 1.9% / 47.9% [0-6] | 2.2% / 46.5% [0-7] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 43.8% of 2681 [25-65] | 36.8% of 2270 [21-57] | 40.6% of 4951 [23-61] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 8.6% of 2681 [0-35] | 6.6% of 2270 [0-32] | 7.7% of 4951 [0-34] |
| P4 not ready, ready 1 turn late | 14.8% of 2681 [0-50] | 13.9% of 2270 [0-44] | 14.4% of 4951 [0-47] |
| P4 not ready, ready 2 or more turns late | 5.9% of 2681 [0-22] | 7.4% of 2270 [0-27] | 6.6% of 4951 [0-24] |
| P4 the moment came and Kingambit was never ready in the deal | 35.5% of 2681 [0-59] | 41.8% of 2270 [0-67] | 38.4% of 4951 [0-62] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -4.5 points (-5.4 to -3.7); P2.both: -11.6 points (-15.0 to -8.2); P2.g1: -2.6 points (-4.0 to -1.3); P2.g2: -13.4 points (-16.8 to -9.8); P3.pawn_lead: -4.2 points (-4.4 to -3.9); P3.pawn_promo: -3.0 points (-7.5 to -0.4); P3.grimer_muk: -10.2 points (-13.3 to -7.5); P4.ko: -2.0 points (-4.5 to -0.1); P5.ko: -2.2 points (-4.6 to -0.4).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.0% / 93.7% [65-93] | 82.9% / 92.7% [72-91] | 82.5% / 93.2% [73-90] |
| P2 both Glimmora had their turn | 25.2% / 58.8% [16-33] | 21.9% / 79.6% [13-38] | 23.6% / 69.2% [16-32] |
| P2 the first Glimmora placed had its turn | 79.3% / 89.8% [63-90] | 80.3% / 85.0% [69-91] | 79.8% / 87.4% [70-88] |
| P2 the second Glimmora placed had its turn | 27.9% / 58.9% [18-37] | 24.6% / 75.6% [15-42] | 26.2% / 67.3% [18-35] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9] | 8.7% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.9% / 44.4% [1-3] | 4.9% / 77.8% [0-8] | 3.4% / 61.1% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.4% / 54.7% [14-22] | 23.5% / 85.1% [14-30] | 20.4% / 69.9% [15-25] |
| P4 ready at the winning moment: Knocks out their strongest | 14.8% / 37.1% [2-29] | 3.6% / 53.7% [0-11] | 9.2% / 45.4% [2-19] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.6% / 25.9% [0-11] | 0.0% / 50.1% [0-0] | 1.8% / 38.0% [0-7] |
| P4 not ready, ready 1 turn late | 5.6% / 41.6% [0-14] | 0.0% / 75.6% [0-0] | 2.8% / 58.6% [0-8] |
| P4 not ready, ready 2 or more turns late | 2.0% / 38.0% [0-7] | 0.0% / 75.6% [0-0] | 1.0% / 56.8% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 12.6% / 48.6% [0-30] | 0.0% / 75.6% [0-0] | 6.3% / 62.1% [0-16] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.9% / 51.2% [6-58] | 20.7% / 70.8% [0-49] | 24.8% / 61.0% [8-46] |
| P5 plan reached in time: Knocks out their strongest | 22.5% / 58.5% [7-39] | 3.6% / 79.3% [0-11] | 13.1% / 68.9% [5-26] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.2% / 40.2% [0-13] | 0.0% / 75.6% [0-0] | 2.1% / 57.9% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 42.1% of 3512 [17-60] | 100.0% of 362 [100-100] | 47.5% of 3874 [25-70] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.3% of 3512 [0-40] | 0.0% of 362 [0-0] | 9.3% of 3874 [0-34] |
| P4 not ready, ready 1 turn late | 16.1% of 3512 [0-59] | 0.0% of 362 [0-0] | 14.6% of 3874 [0-41] |
| P4 not ready, ready 2 or more turns late | 5.8% of 3512 [0-24] | 0.0% of 362 [0-0] | 5.3% of 3874 [0-18] |
| P4 the moment came and Kingambit was never ready in the deal | 36.0% of 3512 [0-61] | 0.0% of 362 [0-0] | 32.6% of 3874 [0-55] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.1 points (-5.9 to -4.2); P2.both: -11.7 points (-15.2 to -9.0); P2.g1: -3.8 points (-4.7 to -3.0); P2.g2: -13.0 points (-16.4 to -10.5); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -4.2 points (-10.9 to -0.4); P3.grimer_muk: -10.9 points (-14.4 to -7.2); P4.ko: -1.3 points (-2.9 to -0.1); P5.ko: -1.3 points (-2.8 to -0.3).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.1% / 87.5% [83-89] | 76.5% / 78.6% [72-81] | 81.3% / 83.0% [78-85] |
| P2 both Glimmora had their turn | 28.1% / 35.5% [25-31] | 22.5% / 30.6% [19-26] | 25.3% / 33.0% [22-28] |
| P2 the first Glimmora placed had its turn | 81.3% / 81.8% [77-86] | 69.7% / 70.3% [64-75] | 75.5% / 76.0% [71-80] |
| P2 the second Glimmora placed had its turn | 32.8% / 39.4% [30-35] | 29.4% / 36.1% [26-32] | 31.1% / 37.7% [28-34] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9] | 8.7% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 4.2% / 15.1% [3-5] | 6.2% / 17.7% [5-7] | 5.2% / 16.4% [4-6] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 20.1% / 29.5% [19-21] | 26.6% / 36.2% [25-28] | 23.4% / 32.8% [22-25] |
| P4 ready at the winning moment: Knocks out their strongest | 6.2% / 12.3% [3-10] | 5.4% / 12.5% [3-8] | 5.8% / 12.4% [3-9] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.3% / 6.3% [0-1] | 0.5% / 7.5% [0-1] | 0.4% / 6.9% [0-1] |
| P4 not ready, ready 1 turn late | 4.0% / 12.6% [2-6] | 3.3% / 13.2% [2-5] | 3.7% / 12.9% [2-6] |
| P4 not ready, ready 2 or more turns late | 1.8% / 10.4% [1-3] | 2.1% / 12.0% [1-4] | 1.9% / 11.2% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 9.6% / 18.2% [5-15] | 9.6% / 19.5% [5-15] | 9.6% / 18.8% [5-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.8% / 75.9% [58-81] | 69.7% / 76.8% [59-80] | 69.8% / 76.3% [59-80] |
| P5 plan reached in time: Knocks out their strongest | 12.0% / 20.6% [7-18] | 10.8% / 20.7% [6-16] | 11.4% / 20.6% [7-17] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.3% / 8.9% [0-1] | 0.5% / 10.4% [0-1] | 0.4% / 9.7% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 28.8% of 2158 [19-41] | 26.6% of 2037 [19-36] | 27.7% of 4195 [20-38] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.3% of 2158 [0-5] | 2.2% of 2037 [0-7] | 1.7% of 4195 [0-5] |
| P4 not ready, ready 1 turn late | 18.5% of 2158 [12-26] | 16.3% of 2037 [11-22] | 17.4% of 4195 [12-24] |
| P4 not ready, ready 2 or more turns late | 8.2% of 2158 [4-13] | 10.2% of 2037 [4-16] | 9.2% of 4195 [4-14] |
| P4 the moment came and Kingambit was never ready in the deal | 44.5% of 2158 [31-57] | 46.9% of 2037 [34-59] | 45.7% of 4195 [33-58] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.7 points (-6.8 to -4.7); P2.both: -11.7 points (-13.4 to -10.0); P2.g1: -3.3 points (-4.2 to -2.4); P2.g2: -14.1 points (-15.6 to -12.6); P3.pawn_lead: -4.2 points (-4.5 to -3.8); P3.pawn_promo: -10.6 points (-13.2 to -8.1); P3.grimer_muk: -16.1 points (-18.4 to -13.9); P4.ko: -1.4 points (-2.2 to -0.7); P5.ko: -1.5 points (-2.4 to -0.8).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 76.0% [75-77, Wilson] | 48.0% [47-49, Wilson] | 62.0% [61-63, Wilson] |
| P2 both Glimmora had their turn | 20.7% [20-21, Wilson] | 6.8% [6-7, Wilson] | 13.7% [13-14, Wilson] |
| P2 the first Glimmora placed had its turn | 72.5% [72-73, Wilson] | 36.0% [35-37, Wilson] | 54.3% [54-55, Wilson] |
| P2 the second Glimmora placed had its turn | 24.2% [23-25, Wilson] | 18.8% [18-20, Wilson] | 21.5% [21-22, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 11.5% [11-12, Wilson] | 12.9% [12-14, Wilson] | 12.2% [12-13, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.3% [35-37, Wilson] | 39.3% [38-40, Wilson] | 37.8% [37-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 12.2% [12-13, Wilson] | 4.0% [4-4, Wilson] | 8.1% [8-8, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.2% [12-13, Wilson] | 4.0% [4-4, Wilson] | 8.1% [8-8, Wilson] |
| P4 not ready, ready 1 turn late | 1.7% [1-2, Wilson] | 0.5% [0-1, Wilson] | 1.1% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.8% [24-26, Wilson] | 17.1% [16-18, Wilson] | 20.9% [20-21, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 61.3% [60-62, Wilson] | 78.5% [78-79, Wilson] | 69.9% [69-71, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 13.9% [13-15, Wilson] | 4.4% [4-5, Wilson] | 9.2% [9-10, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 13.9% [13-15, Wilson] | 4.4% [4-5, Wilson] | 9.2% [9-10, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 31.6% of 3871 [30-33, Wilson] | 18.4% of 2149 [17-20, Wilson] | 26.9% of 6020 [26-28, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 31.6% of 3871 [30-33, Wilson] | 18.4% of 2149 [17-20, Wilson] | 26.9% of 6020 [26-28, Wilson] |
| P4 not ready, ready 1 turn late | 4.4% of 3871 [4-5, Wilson] | 2.2% of 2149 [2-3, Wilson] | 3.6% of 6020 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 3871 [0-0, Wilson] | 0.0% of 2149 [0-0, Wilson] | 0.0% of 6020 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 64.0% of 3871 [62-66, Wilson] | 79.4% of 2149 [78-81, Wilson] | 69.5% of 6020 [68-71, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.4 points (-5.9 to -4.9); P2.both: -4.5 points (-5.0 to -4.1); P2.g2: -9.2 points (-9.8 to -8.7); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -8.1 points (-8.6 to -7.6); P3.grimer_muk: -18.2 points (-18.8 to -17.6); P4.ko: -2.6 points (-3.0 to -2.3); P4.win: -2.6 points (-3.0 to -2.3); P4.nomoment: +3.2 points (+2.8 to +3.6); P5.ko: -2.9 points (-3.3 to -2.6); P5.win: -2.9 points (-3.3 to -2.6).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.1% [84-86, Wilson] | 75.6% [75-76, Wilson] | 80.3% [80-81, Wilson] |
| P2 both Glimmora had their turn | 29.3% [28-30, Wilson] | 19.9% [19-21, Wilson] | 24.6% [24-25, Wilson] |
| P2 the first Glimmora placed had its turn | 82.8% [82-84, Wilson] | 72.4% [72-73, Wilson] | 77.6% [77-78, Wilson] |
| P2 the second Glimmora placed had its turn | 31.5% [31-32, Wilson] | 23.1% [22-24, Wilson] | 27.3% [27-28, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 8.9% [8-9, Wilson] | 12.3% [12-13, Wilson] | 10.6% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 29.9% [29-31, Wilson] | 37.4% [36-38, Wilson] | 33.6% [33-34, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 21.0% [20-22, Wilson] | 12.0% [11-13, Wilson] | 16.5% [16-17, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.8% [3-3, Wilson] | 1.8% [2-2, Wilson] | 2.3% [2-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.6% [24-25, Wilson] | 25.2% [24-26, Wilson] | 24.9% [24-25, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 51.6% [51-53, Wilson] | 60.9% [60-62, Wilson] | 56.3% [56-57, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 23.8% [23-25, Wilson] | 13.8% [13-15, Wilson] | 18.8% [18-19, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 43.4% of 4835 [42-45, Wilson] | 30.8% of 3907 [29-32, Wilson] | 37.8% of 8742 [37-39, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 4835 [0-0, Wilson] | 0.0% of 3907 [0-0, Wilson] | 0.0% of 8742 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 5.8% of 4835 [5-7, Wilson] | 4.7% of 3907 [4-5, Wilson] | 5.3% of 8742 [5-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4835 [0-0, Wilson] | 0.0% of 3907 [0-0, Wilson] | 0.0% of 8742 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 50.8% of 4835 [49-52, Wilson] | 64.6% of 3907 [63-66, Wilson] | 56.9% of 8742 [56-58, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.7 points (-6.1 to -5.3); P2.both: -9.4 points (-10.0 to -8.8); P2.g1: -4.5 points (-5.0 to -4.1); P2.g2: -10.5 points (-11.2 to -9.9); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -13.3 points (-13.9 to -12.8); P3.grimer_muk: -23.1 points (-23.8 to -22.5); P4.ko: -5.2 points (-5.7 to -4.8); P4.nomoment: +5.3 points (+4.9 to +5.8); P5.ko: -5.3 points (-5.8 to -4.8).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 92.2% [92-93, Wilson] | 85.0% [84-86, Wilson] | 88.6% [88-89, Wilson] |
| P2 both Glimmora had their turn | 48.8% [48-50, Wilson] | 38.2% [37-39, Wilson] | 43.5% [43-44, Wilson] |
| P2 the first Glimmora placed had its turn | 88.2% [88-89, Wilson] | 79.4% [79-80, Wilson] | 83.8% [83-84, Wilson] |
| P2 the second Glimmora placed had its turn | 52.8% [52-54, Wilson] | 43.8% [43-45, Wilson] | 48.3% [48-49, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.8% [3-3, Wilson] | 4.6% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.4% [17-18, Wilson] | 24.9% [24-26, Wilson] | 21.1% [21-22, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 44.0% [43-45, Wilson] | 34.0% [33-35, Wilson] | 39.0% [38-40, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 44.0% [43-45, Wilson] | 34.0% [33-35, Wilson] | 39.0% [38-40, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 5.2% [5-6, Wilson] | 2.6% [2-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 12.7% [12-13, Wilson] | 11.3% [11-12, Wilson] | 12.0% [12-12, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 43.3% [42-44, Wilson] | 49.5% [49-50, Wilson] | 46.4% [46-47, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 44.0% [43-45, Wilson] | 39.2% [38-40, Wilson] | 41.6% [41-42, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 44.0% [43-45, Wilson] | 39.2% [38-40, Wilson] | 41.6% [41-42, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 77.6% of 5666 [76-79, Wilson] | 67.3% of 5048 [66-69, Wilson] | 72.7% of 10714 [72-74, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 77.6% of 5666 [76-79, Wilson] | 67.3% of 5048 [66-69, Wilson] | 72.7% of 10714 [72-74, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5666 [0-0, Wilson] | 10.3% of 5048 [10-11, Wilson] | 4.9% of 10714 [4-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5666 [0-0, Wilson] | 0.0% of 5048 [0-0, Wilson] | 0.0% of 10714 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 22.4% of 5666 [21-24, Wilson] | 22.3% of 5048 [21-24, Wilson] | 22.4% of 10714 [22-23, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: -4.1 points (-4.5 to -3.8); P2.both: -18.8 points (-19.5 to -18.1); P2.g1: -2.1 points (-2.5 to -1.8); P2.g2: -20.8 points (-21.5 to -20.1); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -3.0 points (-3.3 to -2.7); P3.grimer_muk: -14.7 points (-15.2 to -14.1); P4.ko: -5.5 points (-6.1 to -5.0); P4.win: -5.5 points (-6.1 to -5.0); P4.never: -2.0 points (-2.4 to -1.5); P4.nomoment: +7.0 points (+6.5 to +7.4); P5.ko: -5.0 points (-5.5 to -4.5); P5.win: -5.0 points (-5.5 to -4.5).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 76.2% [75-77, Wilson] | 48.1% [47-49, Wilson] | 62.2% [61-63, Wilson] |
| P2 both Glimmora had their turn | 21.0% [20-22, Wilson] | 6.8% [6-7, Wilson] | 13.9% [13-14, Wilson] |
| P2 the first Glimmora placed had its turn | 72.5% [72-73, Wilson] | 36.0% [35-37, Wilson] | 54.3% [54-55, Wilson] |
| P2 the second Glimmora placed had its turn | 24.7% [24-26, Wilson] | 18.9% [18-20, Wilson] | 21.8% [21-22, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 12.4% [12-13, Wilson] | 13.2% [13-14, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.3% [35-37, Wilson] | 39.3% [38-40, Wilson] | 37.8% [37-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.2% [3-4, Wilson] | 1.4% [1-2, Wilson] | 2.3% [2-2, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 93.4% [93-94, Wilson] | 97.8% [98-98, Wilson] | 95.6% [95-96, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 52.0% of 659 [48-56, Wilson] | 35.5% of 217 [29-42, Wilson] | 47.9% of 876 [45-51, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 52.0% of 659 [48-56, Wilson] | 35.5% of 217 [29-42, Wilson] | 47.9% of 876 [45-51, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 659 [0-1, Wilson] | 0.0% of 217 [0-2, Wilson] | 0.0% of 876 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 659 [0-1, Wilson] | 0.0% of 217 [0-2, Wilson] | 0.0% of 876 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 48.0% of 659 [44-52, Wilson] | 64.5% of 217 [58-71, Wilson] | 52.1% of 876 [49-55, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.3 points (-5.8 to -4.8); P2.both: -4.5 points (-5.0 to -4.1); P2.g2: -9.2 points (-9.7 to -8.6); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -9.0 points (-9.5 to -8.5); P3.grimer_muk: -18.2 points (-18.8 to -17.6).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 92.5% [92-93, Wilson] | 85.2% [85-86, Wilson] | 88.9% [88-89, Wilson] |
| P2 both Glimmora had their turn | 59.1% [58-60, Wilson] | 44.9% [44-46, Wilson] | 52.0% [51-53, Wilson] |
| P2 the first Glimmora placed had its turn | 88.2% [88-89, Wilson] | 79.4% [79-80, Wilson] | 83.8% [83-84, Wilson] |
| P2 the second Glimmora placed had its turn | 63.4% [62-64, Wilson] | 50.7% [50-52, Wilson] | 57.0% [56-58, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.6% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 4.4% [4-5, Wilson] | 7.0% [6-7, Wilson] | 5.7% [5-6, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.7% [17-18, Wilson] | 25.7% [25-27, Wilson] | 21.7% [21-22, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 16.1% [15-17, Wilson] | 12.7% [12-13, Wilson] | 14.4% [14-15, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 16.1% [15-17, Wilson] | 12.7% [12-13, Wilson] | 14.4% [14-15, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.3% [0-0, Wilson] | 0.2% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.5% [2-3, Wilson] | 2.4% [2-3, Wilson] | 2.4% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 81.3% [81-82, Wilson] | 84.6% [84-85, Wilson] | 83.0% [82-83, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 16.1% [15-17, Wilson] | 13.1% [12-14, Wilson] | 14.6% [14-15, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 16.1% [15-17, Wilson] | 13.1% [12-14, Wilson] | 14.6% [14-15, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 86.4% of 1867 [85-88, Wilson] | 82.6% of 1542 [81-84, Wilson] | 84.7% of 3409 [83-86, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 86.4% of 1867 [85-88, Wilson] | 82.6% of 1542 [81-84, Wilson] | 84.7% of 3409 [83-86, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1867 [0-0, Wilson] | 2.2% of 1542 [2-3, Wilson] | 1.0% of 3409 [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1867 [0-0, Wilson] | 0.0% of 1542 [0-0, Wilson] | 0.0% of 3409 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 13.6% of 1867 [12-15, Wilson] | 15.2% of 1542 [14-17, Wilson] | 14.3% of 3409 [13-16, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: -3.9 points (-4.3 to -3.5); P2.both: -12.3 points (-13.0 to -11.7); P2.g1: -2.1 points (-2.5 to -1.8); P2.g2: -14.1 points (-14.7 to -13.4); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -29.3 points (-30.0 to -28.6); P3.grimer_muk: -25.3 points (-26.0 to -24.6); P4.ko: +7.9 points (+7.4 to +8.3); P4.win: +7.9 points (+7.4 to +8.3); P4.never: -9.2 points (-9.7 to -8.8); P4.nomoment: +1.3 points (+1.0 to +1.6); P5.ko: +8.0 points (+7.5 to +8.4); P5.win: +8.0 points (+7.5 to +8.4).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.4% (27.1-27.8) | 27.1% (26.7-27.5) | 27.3% (27.0-27.5) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 46.5% (46.1-47.0) | 46.3% (45.8-46.7) | 46.4% (46.1-46.7) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 56.9% (56.5-57.3) | 56.9% (56.5-57.4) | 56.9% (56.6-57.2) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 62.6% (62.2-63.1) | 62.7% (62.3-63.1) | 62.7% (62.4-63.0) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 65.9% (65.5-66.3) | 66.1% (65.7-66.5) | 66.0% (65.7-66.3) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 67.7% (67.3-68.1) | 67.8% (67.4-68.2) | 67.7% (67.5-68.0) |
| K2 Kingambit in play, own turn 2 | 8.6% (8.4-8.8) | 8.6% (8.3-8.8) | 8.6% (8.4-8.8) |
| K2 Kingambit in play, own turn 3 | 16.1% (15.8-16.5) | 16.4% (16.1-16.8) | 16.3% (16.1-16.5) |
| K2 Kingambit in play, own turn 4 | 25.0% (24.7-25.4) | 25.3% (25.0-25.7) | 25.2% (24.9-25.5) |
| K2 Kingambit in play, own turn 5 | 35.1% (34.6-35.5) | 35.3% (34.9-35.8) | 35.2% (34.9-35.5) |
| K2 Kingambit in play, own turn 6 | 45.3% (44.8-45.7) | 45.2% (44.8-45.7) | 45.2% (44.9-45.6) |
| K6 Muk and Regigigas both in play, own turn 3 | 22.6% (22.2-23.0) | 22.5% (22.1-22.9) | 22.5% (22.3-22.8) |
| K6 Muk and Regigigas both in play, own turn 4 | 30.3% (29.9-30.7) | 30.1% (29.7-30.5) | 30.2% (29.9-30.5) |
| K6 Muk and Regigigas both in play, own turn 5 | 36.6% (36.2-37.0) | 36.2% (35.8-36.7) | 36.4% (36.1-36.7) |
| G3 Pawniard in play, own turn 1 | 46.5% (46.1-47.0) | 46.3% (45.8-46.7) | 46.4% (46.1-46.7) |
| G3 Pawniard in play, own turn 2 | 48.3% (47.9-48.7) | 48.4% (47.9-48.8) | 48.3% (48.0-48.6) |
| G3 Pawniard in play, own turn 3 | 46.5% (46.1-46.9) | 46.3% (45.9-46.7) | 46.4% (46.1-46.7) |
| G3 Pawniard in play, own turn 4 | 40.9% (40.4-41.3) | 40.8% (40.3-41.2) | 40.8% (40.5-41.1) |
| G3 Pawniard in play, own turn 5 | 32.7% (32.2-33.1) | 32.4% (32.0-32.9) | 32.5% (32.3-32.8) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 8.6% (8.4-8.8) | 8.6% (8.3-8.8) | 8.6% (8.4-8.8) |
| G3 Kingambit in play, own turn 3 | 16.1% (15.8-16.5) | 16.4% (16.1-16.8) | 16.3% (16.1-16.5) |
| G3 Kingambit in play, own turn 4 | 25.0% (24.7-25.4) | 25.3% (25.0-25.7) | 25.2% (24.9-25.5) |
| G3 Kingambit in play, own turn 5 | 35.1% (34.6-35.5) | 35.3% (34.9-35.8) | 35.2% (34.9-35.5) |
| G3 Alolan Grimer in play, own turn 1 | 45.3% (44.8-45.7) | 45.5% (45.0-45.9) | 45.4% (45.1-45.7) |
| G3 Alolan Grimer in play, own turn 2 | 38.4% (37.9-38.8) | 38.5% (38.0-38.9) | 38.4% (38.1-38.7) |
| G3 Alolan Grimer in play, own turn 3 | 33.4% (33.0-33.8) | 33.3% (32.9-33.7) | 33.4% (33.1-33.7) |
| G3 Alolan Grimer in play, own turn 4 | 27.9% (27.5-28.3) | 27.9% (27.5-28.3) | 27.9% (27.6-28.2) |
| G3 Alolan Grimer in play, own turn 5 | 22.6% (22.3-23.0) | 22.7% (22.4-23.1) | 22.7% (22.4-22.9) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 16.1% (15.8-16.4) | 16.0% (15.7-16.4) | 16.1% (15.8-16.3) |
| G3 Alolan Muk in play, own turn 3 | 26.0% (25.6-26.3) | 25.9% (25.5-26.3) | 25.9% (25.7-26.2) |
| G3 Alolan Muk in play, own turn 4 | 34.1% (33.6-34.5) | 33.9% (33.5-34.3) | 34.0% (33.7-34.3) |
| G3 Alolan Muk in play, own turn 5 | 40.7% (40.3-41.1) | 40.4% (39.9-40.8) | 40.5% (40.2-40.8) |
| G3 Glimmet in play, own turn 1 | 72.8% (72.4-73.2) | 72.8% (72.4-73.1) | 72.8% (72.5-73.1) |
| G3 Glimmet in play, own turn 2 | 44.5% (44.1-44.9) | 44.2% (43.8-44.7) | 44.4% (44.1-44.7) |
| G3 Glimmet in play, own turn 3 | 35.2% (34.8-35.7) | 34.8% (34.4-35.3) | 35.0% (34.7-35.3) |
| G3 Glimmet in play, own turn 4 | 26.2% (25.8-26.6) | 26.0% (25.6-26.4) | 26.1% (25.8-26.4) |
| G3 Glimmet in play, own turn 5 | 17.6% (17.2-17.9) | 17.5% (17.2-17.9) | 17.5% (17.3-17.8) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 54.7% (54.3-55.2) | 54.8% (54.3-55.2) | 54.8% (54.4-55.1) |
| G3 Glimmora in play, own turn 3 | 70.6% (70.2-71.0) | 70.7% (70.3-71.1) | 70.7% (70.4-70.9) |
| G3 Glimmora in play, own turn 4 | 80.5% (80.1-80.8) | 80.5% (80.1-80.8) | 80.5% (80.2-80.7) |
| G3 Glimmora in play, own turn 5 | 86.7% (86.4-87.0) | 86.7% (86.4-87.0) | 86.7% (86.5-86.9) |
| G3 Regigigas in play, own turn 1 | 72.8% (72.5-73.2) | 72.7% (72.3-73.0) | 72.8% (72.5-73.0) |
| G3 Regigigas in play, own turn 2 | 83.7% (83.4-84.0) | 83.5% (83.1-83.8) | 83.6% (83.4-83.8) |
| G3 Regigigas in play, own turn 3 | 89.1% (88.8-89.4) | 88.9% (88.6-89.1) | 89.0% (88.8-89.2) |
| G3 Regigigas in play, own turn 4 | 91.8% (91.6-92.1) | 91.8% (91.5-92.0) | 91.8% (91.6-92.0) |
| G3 Regigigas in play, own turn 5 | 93.2% (92.9-93.4) | 93.1% (92.9-93.3) | 93.1% (93.0-93.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 67.6% (67.2-68.0) | 67.5% (67.1-67.9) | 67.5% (67.2-67.8) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 83.4% (83.1-83.7) | 83.6% (83.3-83.9) | 83.5% (83.3-83.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 91.8% (91.6-92.0) | 91.6% (91.4-91.9) | 91.7% (91.5-91.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 96.1% (95.9-96.3) | 96.0% (95.9-96.2) | 96.1% (95.9-96.2) |
| G4.s2 a Stage 2 in play, own turn 2 | 8.6% (8.4-8.8) | 8.6% (8.3-8.8) | 8.6% (8.4-8.8) |
| G4.s2 a Stage 2 in play, own turn 3 | 16.1% (15.8-16.5) | 16.4% (16.1-16.8) | 16.3% (16.1-16.5) |
| G4.s2 a Stage 2 in play, own turn 4 | 25.0% (24.7-25.4) | 25.3% (25.0-25.7) | 25.2% (24.9-25.5) |
| G4.s2 a Stage 2 in play, own turn 5 | 35.1% (34.6-35.5) | 35.3% (34.9-35.8) | 35.2% (34.9-35.5) |
| G5.any3 an empty own turn among turns 1-3 | 27.6% (27.2-28.0) | 27.0% (26.6-27.4) | 27.3% (27.0-27.6) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 8.6% (8.3-8.8) | 4.3% (4.2-4.4) |
| G6 Kingambit with [DD] attached, own turn 3 | 14.2% (13.9-14.5) | 16.4% (16.1-16.8) | 15.3% (15.1-15.5) |
| G6 Kingambit with [DD] attached, own turn 4 | 25.0% (24.7-25.4) | 25.3% (25.0-25.7) | 25.2% (24.9-25.5) |
| G6 Kingambit with [DD] attached, own turn 5 | 35.1% (34.6-35.5) | 35.3% (34.9-35.8) | 35.2% (34.9-35.5) |
| G5 mean empty own turns in turns 1-5 | 0.773 | 0.765 | 0.769 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.7% / 10.1% [1-2] | 0.8% / 5.0% [1-1] |
| K3.by3 | 2.3% / 11.0% [2-3] | 2.0% / 10.4% [1-3] | 2.2% / 10.7% [1-3] |
| K3.by4 | 2.8% / 11.4% [2-4] | 3.8% / 12.2% [3-5] | 3.3% / 11.8% [3-4] |
| K3.by5 | 4.6% / 13.2% [3-6] | 4.4% / 19.8% [3-6] | 4.5% / 16.5% [3-6] |
| K3.by6 | 4.9% / 21.6% [3-7] | 7.9% / 31.4% [4-13] | 6.4% / 26.5% [4-9] |
| K3.by7 | 10.4% / 35.0% [4-18] | 8.2% / 53.5% [4-13] | 9.3% / 44.3% [5-16] |
| K3.by8 | 10.5% / 58.1% [5-18] | 8.2% / 59.0% [4-13] | 9.3% / 58.5% [5-16] |
| K3.never | 41.9% / 89.5% [17-66] | 41.0% / 91.8% [18-63] | 41.5% / 90.7% [18-65] |
| K3.k0 | 3.0% / 50.6% [2-4] | 2.2% / 53.0% [1-3] | 2.6% / 51.8% [2-4] |
| K3.k1 | 0.0% / 47.6% [0-0] | 0.0% / 50.8% [0-0] | 0.0% / 49.2% [0-0] |
| K3.k2 | 5.9% / 53.5% [1-13] | 5.0% / 55.8% [2-10] | 5.4% / 54.6% [1-12] |
| K3.k3p | 1.6% / 49.3% [0-5] | 1.0% / 51.8% [0-2] | 1.3% / 50.5% [0-4] |
| K4 | 7.5% / 56.7% [1-16] | 5.9% / 57.9% [2-11] | 6.7% / 57.3% [2-13] |
| K5 | 4.9% / 60.2% [4-6] | 6.4% / 57.8% [5-8] | 5.6% / 59.0% [4-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.0 points (-1.5 to -0.6); K3.by4: -1.3 points (-1.9 to -0.8); K3.by5: -1.6 points (-2.2 to -1.1); K3.by6: -2.4 points (-3.4 to -1.5); K3.by7: -4.0 points (-6.4 to -1.9); K3.by8: -5.4 points (-9.9 to -1.9); K3.never: +4.0 points (+0.9 to +7.9); K3.k0: -1.3 points (-2.1 to -0.7); K3.k2: -1.4 points (-3.3 to -0.1); K4: -4.0 points (-8.7 to -0.4); K5: -2.5 points (-3.2 to -1.8).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [2-3] | 1.2% [0-2] |
| K3.by3 | 2.1% / 13.4% [1-3] | 2.8% [2-4] | 2.5% / 8.1% [2-3] |
| K3.by4 | 2.4% / 13.7% [1-4] | 4.0% [3-5] | 3.2% / 8.9% [2-4] |
| K3.by5 | 4.4% / 15.7% [3-7] | 4.7% / 32.5% [4-5] | 4.5% / 24.1% [3-6] |
| K3.by6 | 4.7% / 16.0% [3-7] | 5.1% / 32.9% [4-6] | 4.9% / 24.4% [4-6] |
| K3.by7 | 12.8% / 35.2% [4-24] | 5.9% / 65.5% [4-9] | 9.3% / 50.3% [5-17] |
| K3.by8 | 12.8% / 55.5% [4-24] | 5.9% / 80.7% [4-9] | 9.4% / 68.1% [5-17] |
| K3.never | 44.5% / 87.2% [16-73] | 19.3% / 94.1% [0-45] | 31.9% / 90.6% [14-54] |
| K3.k0 | 2.6% / 45.3% [1-4] | 3.2% / 78.0% [2-5] | 2.9% / 61.7% [2-4] |
| K3.k1 | 0.0% / 42.7% [0-0] | 0.0% / 74.8% [0-0] | 0.0% / 58.8% [0-0] |
| K3.k2 | 7.7% / 50.4% [1-19] | 1.9% / 76.7% [0-3] | 4.8% / 63.5% [1-11] |
| K3.k3p | 2.5% / 45.2% [0-8] | 0.8% / 75.6% [0-3] | 1.7% / 60.4% [0-5] |
| K4 | 10.2% / 54.1% [1-22] | 2.7% / 80.0% [0-6] | 6.4% / 67.0% [2-14] |
| K5 | 5.1% / 52.8% [3-7] | 6.0% / 80.9% [4-7] | 5.5% / 66.8% [4-7] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.2 points (-1.6 to -0.8); K3.by4: -1.5 points (-2.0 to -1.1); K3.by5: -1.8 points (-2.2 to -1.4); K3.by6: -2.0 points (-2.5 to -1.5); K3.by7: -6.2 points (-12.2 to -1.9); K3.by8: -6.2 points (-12.2 to -1.8); K3.never: +2.7 points (+0.4 to +5.5); K3.k0: -1.5 points (-2.1 to -1.0); K4: -4.7 points (-11.0 to -0.3); K5: -2.5 points (-3.2 to -1.7).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.9% [2-2] | 1.0% [1-1] |
| K3.by3 | 2.4% [2-3] | 2.3% [2-3] | 2.4% [2-3] |
| K3.by4 | 2.9% [2-3] | 3.5% [3-4] | 3.2% [3-4] |
| K3.by5 | 3.9% [3-4] | 5.3% [4-6] | 4.6% [4-5] |
| K3.by6 | 5.7% [5-7] | 6.4% / 10.4% [5-7] | 6.0% / 8.0% [5-7] |
| K3.by7 | 6.7% / 11.1% [5-8] | 7.2% / 16.9% [6-9] | 6.9% / 14.0% [6-8] |
| K3.by8 | 7.3% / 18.0% [6-9] | 7.5% / 18.8% [6-9] | 7.4% / 18.4% [6-9] |
| K3.never | 82.0% / 92.7% [74-89] | 81.2% / 92.5% [74-87] | 81.6% / 92.6% [74-88] |
| K3.k0 | 3.1% / 13.8% [3-4] | 2.5% / 13.8% [2-3] | 2.8% / 13.8% [2-3] |
| K3.k1 | 0.0% / 10.7% [0-0] | 0.0% / 11.3% [0-0] | 0.0% / 11.0% [0-0] |
| K3.k2 | 2.4% / 13.1% [1-3] | 3.1% / 14.4% [2-4] | 2.7% / 13.7% [2-4] |
| K3.k3p | 1.8% / 12.6% [1-3] | 1.9% / 13.3% [1-3] | 1.9% / 12.9% [1-3] |
| K4 | 4.2% / 15.4% [3-6] | 5.0% / 16.7% [4-7] | 4.6% / 16.1% [3-6] |
| K5 | 5.7% / 19.2% [5-6] | 7.4% / 19.1% [7-8] | 6.6% / 19.2% [6-7] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.1 points (-1.3 to -0.9); K3.by4: -1.3 points (-1.6 to -1.1); K3.by5: -1.9 points (-2.2 to -1.6); K3.by6: -2.7 points (-3.3 to -2.1); K3.by7: -3.9 points (-5.2 to -2.8); K3.by8: -4.9 points (-6.8 to -3.3); K3.never: +4.5 points (+3.0 to +6.3); K3.k0: -1.3 points (-1.6 to -1.1); K3.k3p: -2.9 points (-4.8 to -1.4); K4: -3.6 points (-5.5 to -2.0); K5: -3.0 points (-3.4 to -2.6).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.2% [2-2, Wilson] | 1.1% [1-1, Wilson] |
| K3.by4 | 1.8% [2-2, Wilson] | 4.1% [4-4, Wilson] | 3.0% [3-3, Wilson] |
| K3.by5 | 6.7% [6-7, Wilson] | 4.5% [4-5, Wilson] | 5.6% [5-6, Wilson] |
| K3.by6 | 8.9% [8-9, Wilson] | 4.5% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.by7 | 8.9% [8-9, Wilson] | 4.5% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.by8 | 8.9% [8-9, Wilson] | 4.5% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.never | 91.1% [91-92, Wilson] | 95.5% [95-96, Wilson] | 93.3% [93-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.8% [2-2, Wilson] | 2.2% [2-2, Wilson] | 2.0% [2-2, Wilson] |
| K3.k3p | 7.1% [7-8, Wilson] | 2.3% [2-3, Wilson] | 4.7% [4-5, Wilson] |
| K4 | 8.9% [8-9, Wilson] | 4.5% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K5 | 12.3% [12-13, Wilson] | 17.1% [16-18, Wilson] | 14.7% [14-15, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.0 points (-1.3 to -0.8); K3.by5: -3.8 points (-4.2 to -3.5); K3.by6: -4.5 points (-4.9 to -4.1); K3.by7: -4.5 points (-4.9 to -4.1); K3.by8: -4.5 points (-4.9 to -4.1); K3.never: +4.5 points (+4.1 to +4.9); K3.k3p: -4.1 points (-4.5 to -3.8); K4: -4.5 points (-4.9 to -4.1); K5: -7.0 points (-7.5 to -6.6).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 2.8% [3-3, Wilson] | 4.8% [4-5, Wilson] | 3.8% [4-4, Wilson] |
| K3.by5 | 4.3% [4-5, Wilson] | 9.3% [9-10, Wilson] | 6.8% [6-7, Wilson] |
| K3.by6 | 10.6% [10-11, Wilson] | 11.6% [11-12, Wilson] | 11.1% [11-12, Wilson] |
| K3.by7 | 15.7% [15-16, Wilson] | 11.6% [11-12, Wilson] | 13.7% [13-14, Wilson] |
| K3.by8 | 15.7% [15-16, Wilson] | 11.6% [11-12, Wilson] | 13.7% [13-14, Wilson] |
| K3.never | 84.3% [84-85, Wilson] | 88.4% [88-89, Wilson] | 86.3% [86-87, Wilson] |
| K3.k0 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-2, Wilson] | 2.4% [2-3, Wilson] | 1.9% [2-2, Wilson] |
| K3.k3p | 11.4% [11-12, Wilson] | 6.9% [6-7, Wilson] | 9.2% [9-10, Wilson] |
| K4 | 12.9% [12-14, Wilson] | 9.3% [9-10, Wilson] | 11.1% [11-12, Wilson] |
| K5 | 8.5% [8-9, Wilson] | 12.4% [12-13, Wilson] | 10.5% [10-11, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.3 to -1.0); K3.by4: -1.3 points (-1.5 to -1.1); K3.by5: -4.2 points (-4.6 to -3.8); K3.by6: -11.0 points (-11.6 to -10.5); K3.by7: -11.0 points (-11.5 to -10.5); K3.by8: -11.0 points (-11.5 to -10.5); K3.never: +11.0 points (+10.5 to +11.5); K3.k0: -1.1 points (-1.3 to -1.0); K3.k3p: -9.6 points (-10.1 to -9.1); K4: -9.9 points (-10.4 to -9.4); K5: -5.8 points (-6.2 to -5.4).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 2.8% [3-3, Wilson] | 5.2% [5-6, Wilson] | 4.0% [4-4, Wilson] |
| K3.by6 | 4.9% [5-5, Wilson] | 5.3% [5-6, Wilson] | 5.1% [5-5, Wilson] |
| K3.by7 | 5.0% [5-5, Wilson] | 28.9% [28-30, Wilson] | 17.0% [16-17, Wilson] |
| K3.by8 | 38.3% [37-39, Wilson] | 29.0% [28-30, Wilson] | 33.7% [33-34, Wilson] |
| K3.never | 61.7% [61-63, Wilson] | 71.0% [70-72, Wilson] | 66.3% [66-67, Wilson] |
| K3.k0 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.2% [2-3, Wilson] | 3.0% [3-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k3p | 33.3% [32-34, Wilson] | 23.7% [23-25, Wilson] | 28.5% [28-29, Wilson] |
| K4 | 35.5% [35-36, Wilson] | 26.7% [26-28, Wilson] | 31.1% [30-32, Wilson] |
| K5 | 6.1% [6-7, Wilson] | 7.4% [7-8, Wilson] | 6.7% [6-7, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.3 to -1.0); K3.by4: -1.1 points (-1.3 to -1.0); K3.by5: -2.2 points (-2.5 to -1.9); K3.by6: -3.0 points (-3.3 to -2.7); K3.by7: -7.4 points (-7.9 to -7.0); K3.by8: -12.4 points (-13.0 to -11.8); K3.never: +12.4 points (+11.8 to +13.0); K3.k0: -1.1 points (-1.3 to -1.0); K3.k2: -1.9 points (-2.2 to -1.6); K3.k3p: -9.4 points (-10.0 to -8.8); K4: -11.3 points (-11.9 to -10.7); K5: -3.2 points (-3.5 to -2.9).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.2% [2-2, Wilson] | 1.1% [1-1, Wilson] |
| K3.by4 | 1.8% [2-2, Wilson] | 3.7% [3-4, Wilson] | 2.8% [3-3, Wilson] |
| K3.by5 | 5.1% [5-6, Wilson] | 4.1% [4-5, Wilson] | 4.6% [4-5, Wilson] |
| K3.by6 | 7.5% [7-8, Wilson] | 4.1% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K3.by7 | 7.5% [7-8, Wilson] | 4.1% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K3.by8 | 7.5% [7-8, Wilson] | 4.1% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K3.never | 92.5% [92-93, Wilson] | 95.9% [95-96, Wilson] | 94.2% [94-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.8% [2-2, Wilson] | 2.2% [2-2, Wilson] | 2.0% [2-2, Wilson] |
| K3.k3p | 5.7% [5-6, Wilson] | 2.0% [2-2, Wilson] | 3.8% [4-4, Wilson] |
| K4 | 7.5% [7-8, Wilson] | 4.1% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K5 | 12.3% [12-13, Wilson] | 17.1% [16-18, Wilson] | 14.7% [14-15, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.1 points (-1.4 to -0.9); K3.by5: -4.3 points (-4.7 to -4.0); K3.by6: -4.9 points (-5.3 to -4.5); K3.by7: -4.9 points (-5.3 to -4.5); K3.by8: -4.9 points (-5.3 to -4.5); K3.never: +4.9 points (+4.5 to +5.3); K3.k3p: -4.6 points (-4.9 to -4.2); K4: -4.9 points (-5.3 to -4.5); K5: -7.0 points (-7.5 to -6.6).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 2.8% [3-3, Wilson] | 5.2% [5-6, Wilson] | 4.0% [4-4, Wilson] |
| K3.by6 | 4.9% [5-5, Wilson] | 5.3% [5-6, Wilson] | 5.1% [5-5, Wilson] |
| K3.by7 | 5.0% [5-5, Wilson] | 7.9% [7-8, Wilson] | 6.5% [6-7, Wilson] |
| K3.by8 | 6.7% [6-7, Wilson] | 8.0% [7-9, Wilson] | 7.3% [7-8, Wilson] |
| K3.by9 | 6.7% [6-7, Wilson] | 19.9% [19-21, Wilson] | 13.3% [13-14, Wilson] |
| K3.by10 | 22.4% [22-23, Wilson] | 20.0% [19-21, Wilson] | 21.2% [21-22, Wilson] |
| K3.never | 77.6% [77-78, Wilson] | 80.0% [79-81, Wilson] | 78.8% [78-79, Wilson] |
| K3.k0 | 2.8% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.2% [2-3, Wilson] | 3.0% [3-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k3p | 17.4% [17-18, Wilson] | 14.6% [14-15, Wilson] | 16.0% [16-17, Wilson] |
| K4 | 19.6% [19-20, Wilson] | 17.6% [17-18, Wilson] | 18.6% [18-19, Wilson] |
| K5 | 6.2% [6-7, Wilson] | 7.5% [7-8, Wilson] | 6.9% [7-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.3 to -1.0); K3.by4: -1.1 points (-1.3 to -1.0); K3.by5: -2.2 points (-2.5 to -1.9); K3.by6: -3.0 points (-3.3 to -2.7); K3.by7: -13.6 points (-14.1 to -13.1); K3.by8: -29.7 points (-30.4 to -29.1); K3.by9: -27.4 points (-28.1 to -26.7); K3.by10: -22.6 points (-23.2 to -21.9); K3.never: +22.6 points (+21.9 to +23.2); K3.k0: -1.1 points (-1.3 to -1.0); K3.k2: -1.9 points (-2.2 to -1.6); K3.k3p: -19.6 points (-20.2 to -18.9); K4: -21.4 points (-22.1 to -20.8); K5: -3.2 points (-3.5 to -2.9).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.3 (+19.9 to +20.7) FLAG | +19.9 (+19.5 to +20.2) FLAG | +20.1 (+19.8 to +20.3) FLAG |
| K1 Pawniard in play at setup | -1.8 (-1.9 to -1.6) FLAG | -1.7 (-1.9 to -1.6) FLAG | -1.7 (-1.8 to -1.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -9.4 (-9.7 to -9.1) FLAG | -9.3 (-9.6 to -9.0) FLAG | -9.4 (-9.6 to -9.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -11.0 (-11.4 to -10.7) FLAG | -10.9 (-11.2 to -10.5) FLAG | -11.0 (-11.2 to -10.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -11.9 (-12.2 to -11.5) FLAG | -11.8 (-12.2 to -11.5) FLAG | -11.8 (-12.1 to -11.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -12.7 (-13.0 to -12.3) FLAG | -12.5 (-12.9 to -12.2) FLAG | -12.6 (-12.9 to -12.4) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -13.1 (-13.5 to -12.7) FLAG | -13.0 (-13.3 to -12.6) FLAG | -13.0 (-13.3 to -12.8) FLAG |
| K2 Kingambit in play, own turn 2 | -2.1 (-2.3 to -2.0) FLAG | -2.2 (-2.4 to -2.0) FLAG | -2.2 (-2.3 to -2.0) FLAG |
| K2 Kingambit in play, own turn 3 | -4.9 (-5.2 to -4.7) FLAG | -4.7 (-4.9 to -4.4) FLAG | -4.8 (-5.0 to -4.6) FLAG |
| K2 Kingambit in play, own turn 4 | -8.0 (-8.3 to -7.7) FLAG | -7.8 (-8.1 to -7.5) FLAG | -7.9 (-8.1 to -7.7) FLAG |
| K2 Kingambit in play, own turn 5 | -11.4 (-11.7 to -11.0) FLAG | -11.1 (-11.4 to -10.7) FLAG | -11.2 (-11.5 to -11.0) FLAG |
| K2 Kingambit in play, own turn 6 | -14.2 (-14.6 to -13.8) FLAG | -13.9 (-14.3 to -13.5) FLAG | -14.0 (-14.3 to -13.8) FLAG |
| G3 Pawniard in play, own turn 1 | -9.4 (-9.7 to -9.1) FLAG | -9.3 (-9.6 to -9.0) FLAG | -9.4 (-9.6 to -9.1) FLAG |
| G3 Pawniard in play, own turn 2 | -8.9 (-9.3 to -8.6) FLAG | -8.7 (-9.0 to -8.3) FLAG | -8.8 (-9.0 to -8.6) FLAG |
| G3 Pawniard in play, own turn 3 | -6.9 (-7.3 to -6.6) FLAG | -7.1 (-7.5 to -6.8) FLAG | -7.0 (-7.3 to -6.8) FLAG |
| G3 Pawniard in play, own turn 4 | -4.7 (-5.1 to -4.4) FLAG | -4.7 (-5.1 to -4.4) FLAG | -4.7 (-5.0 to -4.5) FLAG |
| G3 Pawniard in play, own turn 5 | -1.7 (-2.1 to -1.4) FLAG | -1.9 (-2.2 to -1.6) FLAG | -1.8 (-2.1 to -1.6) FLAG |
| G3 Kingambit in play, own turn 2 | -2.1 (-2.3 to -2.0) FLAG | -2.2 (-2.4 to -2.0) FLAG | -2.2 (-2.3 to -2.0) FLAG |
| G3 Kingambit in play, own turn 3 | -4.9 (-5.2 to -4.7) FLAG | -4.7 (-4.9 to -4.4) FLAG | -4.8 (-5.0 to -4.6) FLAG |
| G3 Kingambit in play, own turn 4 | -8.0 (-8.3 to -7.7) FLAG | -7.8 (-8.1 to -7.5) FLAG | -7.9 (-8.1 to -7.7) FLAG |
| G3 Kingambit in play, own turn 5 | -11.4 (-11.7 to -11.0) FLAG | -11.1 (-11.4 to -10.7) FLAG | -11.2 (-11.5 to -11.0) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -9.3 (-9.7 to -9.0) FLAG | -9.3 (-9.6 to -9.0) FLAG | -9.3 (-9.5 to -9.1) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -7.9 (-8.2 to -7.6) FLAG | -8.1 (-8.4 to -7.8) FLAG | -8.0 (-8.2 to -7.8) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -6.5 (-6.8 to -6.2) FLAG | -6.7 (-7.1 to -6.4) FLAG | -6.6 (-6.8 to -6.4) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -5.1 (-5.5 to -4.8) FLAG | -5.4 (-5.7 to -5.0) FLAG | -5.2 (-5.5 to -5.0) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -4.0 (-4.3 to -3.7) FLAG | -4.3 (-4.6 to -4.0) FLAG | -4.2 (-4.4 to -4.0) FLAG |
| G3 Alolan Muk in play, own turn 2 | -2.8 (-3.0 to -2.5) FLAG | -2.9 (-3.1 to -2.6) FLAG | -2.8 (-3.0 to -2.6) FLAG |
| G3 Alolan Muk in play, own turn 3 | -5.1 (-5.4 to -4.8) FLAG | -5.4 (-5.8 to -5.1) FLAG | -5.3 (-5.5 to -5.0) FLAG |
| G3 Alolan Muk in play, own turn 4 | -7.1 (-7.5 to -6.7) FLAG | -7.4 (-7.8 to -7.1) FLAG | -7.3 (-7.5 to -7.0) FLAG |
| G3 Alolan Muk in play, own turn 5 | -8.5 (-8.9 to -8.1) FLAG | -8.9 (-9.3 to -8.5) FLAG | -8.7 (-9.0 to -8.4) FLAG |
| G3 Glimmet in play, own turn 1 | -9.3 (-9.6 to -9.0) FLAG | -9.7 (-10.0 to -9.4) FLAG | -9.5 (-9.7 to -9.3) FLAG |
| G3 Glimmet in play, own turn 2 | -8.3 (-8.7 to -7.9) FLAG | -8.2 (-8.6 to -7.8) FLAG | -8.2 (-8.5 to -8.0) FLAG |
| G3 Glimmet in play, own turn 3 | -6.9 (-7.3 to -6.5) FLAG | -7.1 (-7.5 to -6.7) FLAG | -7.0 (-7.3 to -6.7) FLAG |
| G3 Glimmet in play, own turn 4 | -4.7 (-5.1 to -4.4) FLAG | -4.9 (-5.3 to -4.6) FLAG | -4.8 (-5.1 to -4.6) FLAG |
| G3 Glimmet in play, own turn 5 | -2.6 (-2.9 to -2.3) FLAG | -2.3 (-2.6 to -2.0) FLAG | -2.4 (-2.7 to -2.2) FLAG |
| G3 Glimmora in play, own turn 2 | -8.4 (-8.7 to -8.1) FLAG | -8.6 (-8.9 to -8.2) FLAG | -8.5 (-8.7 to -8.3) FLAG |
| G3 Glimmora in play, own turn 3 | -9.1 (-9.4 to -8.8) FLAG | -9.2 (-9.5 to -8.9) FLAG | -9.2 (-9.4 to -8.9) FLAG |
| G3 Glimmora in play, own turn 4 | -8.9 (-9.2 to -8.7) FLAG | -9.0 (-9.3 to -8.7) FLAG | -9.0 (-9.2 to -8.8) FLAG |
| G3 Glimmora in play, own turn 5 | -8.4 (-8.6 to -8.1) FLAG | -8.4 (-8.7 to -8.2) FLAG | -8.4 (-8.6 to -8.2) FLAG |
| G3 Regigigas in play, own turn 1 | +17.5 (+17.1 to +17.8) FLAG | +17.4 (+17.1 to +17.8) FLAG | +17.4 (+17.2 to +17.7) FLAG |
| G3 Regigigas in play, own turn 2 | +16.1 (+15.7 to +16.4) FLAG | +16.4 (+16.0 to +16.7) FLAG | +16.2 (+16.0 to +16.5) FLAG |
| G3 Regigigas in play, own turn 3 | +14.7 (+14.3 to +15.0) FLAG | +14.7 (+14.4 to +15.0) FLAG | +14.7 (+14.4 to +14.9) FLAG |
| G3 Regigigas in play, own turn 4 | +13.6 (+13.3 to +14.0) FLAG | +13.7 (+13.3 to +14.0) FLAG | +13.6 (+13.4 to +13.9) FLAG |
| G3 Regigigas in play, own turn 5 | +12.8 (+12.5 to +13.2) FLAG | +12.9 (+12.6 to +13.2) FLAG | +12.9 (+12.7 to +13.1) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -8.0 (-8.3 to -7.6) FLAG | -8.2 (-8.5 to -7.8) FLAG | -8.1 (-8.3 to -7.8) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -6.3 (-6.5 to -6.0) FLAG | -6.2 (-6.5 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -4.2 (-4.4 to -3.9) FLAG | -4.2 (-4.4 to -4.0) FLAG | -4.2 (-4.3 to -4.0) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -2.5 (-2.7 to -2.4) FLAG | -2.6 (-2.7 to -2.4) FLAG | -2.5 (-2.7 to -2.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | -2.1 (-2.3 to -2.0) FLAG | -2.2 (-2.4 to -2.0) FLAG | -2.2 (-2.3 to -2.0) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -4.9 (-5.2 to -4.7) FLAG | -4.7 (-4.9 to -4.4) FLAG | -4.8 (-5.0 to -4.6) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -8.0 (-8.3 to -7.7) FLAG | -7.8 (-8.1 to -7.5) FLAG | -7.9 (-8.1 to -7.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -11.4 (-11.7 to -11.0) FLAG | -11.1 (-11.4 to -10.7) FLAG | -11.2 (-11.5 to -11.0) FLAG |
| G5.any3 an empty own turn among turns 1-3 | +4.4 (+4.2 to +4.7) FLAG | +4.5 (+4.2 to +4.8) FLAG | +4.5 (+4.3 to +4.6) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | -2.2 (-2.4 to -2.0) FLAG | -1.1 (-1.2 to -1.0) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -3.4 (-3.6 to -3.1) FLAG | -4.7 (-4.9 to -4.4) FLAG | -4.0 (-4.2 to -3.8) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -8.0 (-8.3 to -7.7) FLAG | -7.8 (-8.1 to -7.5) FLAG | -7.9 (-8.1 to -7.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -11.4 (-11.7 to -11.0) FLAG | -11.1 (-11.4 to -10.7) FLAG | -11.2 (-11.5 to -11.0) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.010 (+0.006 to +0.015) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Poké Ball A2b 111 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.1 points
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn -4.5 points (-5.4 to -3.7); P2 both Glimmora had their turn -11.6 points (-15.0 to -8.2); P2 the first Glimmora placed had its turn -2.6 points (-4.0 to -1.3); P2 the second Glimmora placed had its turn -13.4 points (-16.8 to -9.8); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.4 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -3.0 points (-7.5 to -0.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -10.2 points (-13.3 to -7.5); P4 ready at the winning moment: Knocks out their strongest -2.0 points (-4.5 to -0.1); P5 plan reached in time: Knocks out their strongest -2.2 points (-4.6 to -0.4)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -5.1 points (-5.9 to -4.2); P2 both Glimmora had their turn -11.7 points (-15.2 to -9.0); P2 the first Glimmora placed had its turn -3.8 points (-4.7 to -3.0); P2 the second Glimmora placed had its turn -13.0 points (-16.4 to -10.5); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.2 points (-10.9 to -0.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -10.9 points (-14.4 to -7.2); P4 ready at the winning moment: Knocks out their strongest -1.3 points (-2.9 to -0.1); P5 plan reached in time: Knocks out their strongest -1.3 points (-2.8 to -0.3)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -5.7 points (-6.8 to -4.7); P2 both Glimmora had their turn -11.7 points (-13.4 to -10.0); P2 the first Glimmora placed had its turn -3.3 points (-4.2 to -2.4); P2 the second Glimmora placed had its turn -14.1 points (-15.6 to -12.6); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -10.6 points (-13.2 to -8.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -16.1 points (-18.4 to -13.9); P4 ready at the winning moment: Knocks out their strongest -1.4 points (-2.2 to -0.7); P5 plan reached in time: Knocks out their strongest -1.5 points (-2.4 to -0.8)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn -5.4 points (-5.9 to -4.9); P2 both Glimmora had their turn -4.5 points (-5.0 to -4.1); P2 the second Glimmora placed had its turn -9.2 points (-9.8 to -8.7); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -8.1 points (-8.6 to -7.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -18.2 points (-18.8 to -17.6); P4 ready at the winning moment: Knocks out their strongest -2.6 points (-3.0 to -2.3); P4 ready at the winning moment: Wins outright (a lower bound) -2.6 points (-3.0 to -2.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.2 points (+2.8 to +3.6); P5 plan reached in time: Knocks out their strongest -2.9 points (-3.3 to -2.6); P5 plan reached in time: Wins outright (a lower bound) -2.9 points (-3.3 to -2.6)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn -5.7 points (-6.1 to -5.3); P2 both Glimmora had their turn -9.4 points (-10.0 to -8.8); P2 the first Glimmora placed had its turn -4.5 points (-5.0 to -4.1); P2 the second Glimmora placed had its turn -10.5 points (-11.2 to -9.9); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.3 points (-13.9 to -12.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -23.1 points (-23.8 to -22.5); P4 ready at the winning moment: Knocks out their strongest -5.2 points (-5.7 to -4.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +5.3 points (+4.9 to +5.8); P5 plan reached in time: Knocks out their strongest -5.3 points (-5.8 to -4.8)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn -4.1 points (-4.5 to -3.8); P2 both Glimmora had their turn -18.8 points (-19.5 to -18.1); P2 the first Glimmora placed had its turn -2.1 points (-2.5 to -1.8); P2 the second Glimmora placed had its turn -20.8 points (-21.5 to -20.1); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -3.0 points (-3.3 to -2.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.7 points (-15.2 to -14.1); P4 ready at the winning moment: Knocks out their strongest -5.5 points (-6.1 to -5.0); P4 ready at the winning moment: Wins outright (a lower bound) -5.5 points (-6.1 to -5.0); P4 the moment came and Kingambit was never ready in the deal -2.0 points (-2.4 to -1.5); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +7.0 points (+6.5 to +7.4); P5 plan reached in time: Knocks out their strongest -5.0 points (-5.5 to -4.5); P5 plan reached in time: Wins outright (a lower bound) -5.0 points (-5.5 to -4.5)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn -5.3 points (-5.8 to -4.8); P2 both Glimmora had their turn -4.5 points (-5.0 to -4.1); P2 the second Glimmora placed had its turn -9.2 points (-9.7 to -8.6); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -9.0 points (-9.5 to -8.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -18.2 points (-18.8 to -17.6)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn -3.9 points (-4.3 to -3.5); P2 both Glimmora had their turn -12.3 points (-13.0 to -11.7); P2 the first Glimmora placed had its turn -2.1 points (-2.5 to -1.8); P2 the second Glimmora placed had its turn -14.1 points (-14.7 to -13.4); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -29.3 points (-30.0 to -28.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -25.3 points (-26.0 to -24.6); P4 ready at the winning moment: Knocks out their strongest +7.9 points (+7.4 to +8.3); P4 ready at the winning moment: Wins outright (a lower bound) +7.9 points (+7.4 to +8.3); P4 the moment came and Kingambit was never ready in the deal -9.2 points (-9.7 to -8.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +1.3 points (+1.0 to +1.6); P5 plan reached in time: Knocks out their strongest +8.0 points (+7.5 to +8.4); P5 plan reached in time: Wins outright (a lower bound) +8.0 points (+7.5 to +8.4)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): G3 Regigigas in play, own turn 1 +17.4 points; G3 Regigigas in play, own turn 2 +16.2 points; G3 Regigigas in play, own turn 3 +14.7 points; G3 Regigigas in play, own turn 4 +13.6 points; G3 Regigigas in play, own turn 5 +12.9 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.7 points; K1 Pawniard line in play (end of own turn t), own turn 1 -9.4 points; K1 Pawniard line in play (end of own turn t), own turn 2 -11.0 points; K1 Pawniard line in play (end of own turn t), own turn 3 -11.8 points; K1 Pawniard line in play (end of own turn t), own turn 4 -12.6 points; K1 Pawniard line in play (end of own turn t), own turn 5 -13.0 points; K2 Kingambit in play, own turn 2 -2.2 points; K2 Kingambit in play, own turn 3 -4.8 points; K2 Kingambit in play, own turn 4 -7.9 points; K2 Kingambit in play, own turn 5 -11.2 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 -1.0; K3.by4 -1.3; K3.by5 -1.6; K3.by6 -2.4; K3.by7 -4.0; K3.by8 -5.4; K3.never +4.0; K3.k0 -1.3; K3.k2 -1.4; K4 -4.0; K5 -2.5; C-his, seat-matched: K3.by3 -1.2; K3.by4 -1.5; K3.by5 -1.8; K3.by6 -2.0; K3.by7 -6.2; K3.by8 -6.2; K3.never +2.7; K3.k0 -1.5; K4 -4.7; K5 -2.5; C-bot: K3.by3 -1.1; K3.by4 -1.3; K3.by5 -1.9; K3.by6 -2.7; K3.by7 -3.9; K3.by8 -4.9; K3.never +4.5; K3.k0 -1.3; K3.k3p -2.9; K4 -3.6; K5 -3.0; C-fixed fast: K3.by4 -1.0; K3.by5 -3.8; K3.by6 -4.5; K3.by7 -4.5; K3.by8 -4.5; K3.never +4.5; K3.k3p -4.1; K4 -4.5; K5 -7.0; C-fixed medium: K3.by3 -1.1; K3.by4 -1.3; K3.by5 -4.2; K3.by6 -11.0; K3.by7 -11.0; K3.by8 -11.0; K3.never +11.0; K3.k0 -1.1; K3.k3p -9.6; K4 -9.9; K5 -5.8; C-fixed slow: K3.by3 -1.1; K3.by4 -1.1; K3.by5 -2.2; K3.by6 -3.0; K3.by7 -7.4; K3.by8 -12.4; K3.never +12.4; K3.k0 -1.1; K3.k2 -1.9; K3.k3p -9.4; K4 -11.3; K5 -3.2; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.1; K3.by5 -4.3; K3.by6 -4.9; K3.by7 -4.9; K3.by8 -4.9; K3.never +4.9; K3.k3p -4.6; K4 -4.9; K5 -7.0; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.1; K3.by4 -1.1; K3.by5 -2.2; K3.by6 -3.0; K3.by7 -13.6; K3.by8 -29.7; K3.by9 -27.4; K3.by10 -22.6; K3.never +22.6; K3.k0 -1.1; K3.k2 -1.9; K3.k3p -19.6; K4 -21.4; K5 -3.2.
Not valued here (changed cards the script never plays: they count as blanks): none.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Rare Candy A3 144 +1 Regigigas B3 134 (card-list id 47e622b7f280)

Changes: ['-1 Rare Candy A3 144', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 303,414; the valuation and the fallback rule disagree at 99,271 of 303,414 Copycat decisions (32.7%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 48.9% (48.5-49.4) | 48.8% (48.4-49.2) | 48.9% (48.6-49.2) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 88.0% / 96.9% [75-96] | 79.6% / 92.7% [64-91] | 83.8% / 94.8% [70-93] |
| P2 both Glimmora had their turn | 33.2% / 70.2% [23-44] | 28.4% / 69.6% [19-38] | 30.8% / 69.9% [22-40] |
| P2 the first Glimmora placed had its turn | 85.4% / 93.1% [73-94] | 73.6% / 84.2% [58-87] | 79.5% / 88.6% [66-90] |
| P2 the second Glimmora placed had its turn | 35.8% / 69.8% [25-46] | 34.4% / 70.0% [24-45] | 35.1% / 69.9% [25-45] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9] | 8.8% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.1% / 51.0% [0-2] | 2.1% / 57.8% [1-3] | 1.6% / 54.4% [1-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 15.8% / 59.1% [13-19] | 19.7% / 65.7% [16-24] | 17.8% / 62.4% [15-22] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% / 25.6% [0-0] | 0.0% / 28.7% [0-0] | 0.0% / 27.1% [0-0] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% / 25.6% [0-0] | 0.0% / 28.7% [0-0] | 0.0% / 27.1% [0-0] |
| P4 not ready, ready 1 turn late | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| P4 not ready, ready 2 or more turns late | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| P4 the moment came and Kingambit was never ready in the deal | 20.4% / 70.8% [0-44] | 15.6% / 72.3% [0-38] | 18.0% / 71.5% [0-41] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.2% / 54.8% [8-54] | 27.7% / 56.4% [9-52] | 28.5% / 55.6% [9-52] |
| P5 plan reached in time: Knocks out their strongest | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 2035 [0-0] | 0.0% of 1557 [0-0] | 0.0% of 3592 [0-0] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 2035 [0-0] | 0.0% of 1557 [0-0] | 0.0% of 3592 [0-0] |
| P4 not ready, ready 1 turn late | 0.0% of 2035 [0-0] | 0.0% of 1557 [0-0] | 0.0% of 3592 [0-0] |
| P4 not ready, ready 2 or more turns late | 0.0% of 2035 [0-0] | 0.0% of 1557 [0-0] | 0.0% of 3592 [0-0] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 2035 [100-100] | 100.0% of 1557 [100-100] | 100.0% of 3592 [100-100] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.g2: -6.2 points (-11.2 to -1.0); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -4.4 points (-9.3 to -1.2); P3.grimer_muk: -12.3 points (-15.8 to -8.9); P4.ko: -12.1 points (-23.5 to -2.5); P4.nomoment: -1.9 points (-3.2 to -0.8); P5.ko: -17.5 points (-31.1 to -6.0).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.2% / 96.9% [68-96] | 88.3% / 95.8% [78-96] | 87.3% / 96.4% [77-94] |
| P2 both Glimmora had their turn | 32.7% / 65.4% [21-44] | 31.3% / 86.5% [19-55] | 32.0% / 75.9% [22-44] |
| P2 the first Glimmora placed had its turn | 83.4% / 93.1% [66-94] | 85.1% / 88.3% [74-94] | 84.2% / 90.7% [75-92] |
| P2 the second Glimmora placed had its turn | 35.4% / 65.5% [22-48] | 34.6% / 82.6% [20-59] | 35.0% / 74.1% [24-48] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9] | 8.8% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.0% / 45.5% [0-2] | 2.4% / 83.8% [0-5] | 1.7% / 64.6% [0-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 15.7% / 54.2% [13-20] | 20.0% / 87.2% [11-26] | 17.9% / 70.7% [14-22] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% / 22.5% [0-0] | 0.0% / 51.9% [0-0] | 0.0% / 37.2% [0-0] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% / 22.5% [0-0] | 0.0% / 51.9% [0-0] | 0.0% / 37.2% [0-0] |
| P4 not ready, ready 1 turn late | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| P4 not ready, ready 2 or more turns late | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| P4 the moment came and Kingambit was never ready in the deal | 28.0% / 72.9% [0-59] | 0.0% / 83.3% [0-0] | 14.0% / 78.1% [0-33] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 27.1% / 49.6% [5-56] | 16.7% / 68.6% [0-44] | 21.9% / 59.1% [6-43] |
| P5 plan reached in time: Knocks out their strongest | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 2799 [0-0] | the moment never came | 0.0% of 2799 [0-0] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 2799 [0-0] | the moment never came | 0.0% of 2799 [0-0] |
| P4 not ready, ready 1 turn late | 0.0% of 2799 [0-0] | the moment never came | 0.0% of 2799 [0-0] |
| P4 not ready, ready 2 or more turns late | 0.0% of 2799 [0-0] | the moment never came | 0.0% of 2799 [0-0] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 2799 [100-100] | the moment never came | 100.0% of 2799 [100-100] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P3.pawn_lead: -4.1 points (-4.6 to -3.8); P3.pawn_promo: -6.0 points (-13.7 to -0.9); P3.grimer_muk: -13.5 points (-17.8 to -9.0); P4.ko: -10.5 points (-21.5 to -2.5); P5.ko: -14.4 points (-29.4 to -4.9).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.5% / 91.5% [87-93] | 83.1% / 84.7% [79-87] | 86.8% / 88.1% [83-90] |
| P2 both Glimmora had their turn | 40.6% / 47.1% [36-45] | 32.3% / 39.9% [28-37] | 36.4% / 43.5% [32-41] |
| P2 the first Glimmora placed had its turn | 85.1% / 85.3% [80-90] | 74.7% / 75.0% [69-80] | 79.9% / 80.2% [75-85] |
| P2 the second Glimmora placed had its turn | 46.0% / 51.9% [42-50] | 40.7% / 46.9% [37-44] | 43.3% / 49.4% [39-47] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9] | 8.8% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.5% / 13.5% [1-2] | 2.8% / 15.9% [2-3] | 2.1% / 14.7% [2-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.2% / 27.3% [16-19] | 23.4% / 34.0% [22-25] | 20.3% / 30.6% [19-22] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% / 6.3% [0-0] | 0.0% / 7.5% [0-0] | 0.0% / 6.9% [0-0] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% / 6.3% [0-0] | 0.0% / 7.5% [0-0] | 0.0% / 6.9% [0-0] |
| P4 not ready, ready 1 turn late | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| P4 not ready, ready 2 or more turns late | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| P4 the moment came and Kingambit was never ready in the deal | 18.9% / 31.0% [10-29] | 19.0% / 32.3% [10-28] | 18.9% / 31.7% [10-28] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.0% / 75.3% [57-80] | 67.7% / 75.1% [56-78] | 68.3% / 75.2% [57-79] |
| P5 plan reached in time: Knocks out their strongest | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 1892 [0-0] | 0.0% of 1897 [0-0] | 0.0% of 3789 [0-0] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 1892 [0-0] | 0.0% of 1897 [0-0] | 0.0% of 3789 [0-0] |
| P4 not ready, ready 1 turn late | 0.0% of 1892 [0-0] | 0.0% of 1897 [0-0] | 0.0% of 3789 [0-0] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1892 [0-0] | 0.0% of 1897 [0-0] | 0.0% of 3789 [0-0] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 1892 [100-100] | 100.0% of 1897 [100-100] | 100.0% of 3789 [100-100] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -13.7 points (-16.8 to -10.7); P3.grimer_muk: -19.2 points (-21.8 to -16.6); P4.ko: -7.2 points (-11.1 to -3.9); P4.late1: -4.1 points (-6.4 to -2.1); P4.late2p: -1.6 points (-2.9 to -0.6); P4.never: +10.2 points (+5.2 to +15.5); P4.nomoment: -1.1 points (-1.7 to -0.4); P5.ko: -12.9 points (-19.2 to -7.5).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.9% [82-84, Wilson] | 58.6% [58-60, Wilson] | 70.8% [70-71, Wilson] |
| P2 both Glimmora had their turn | 32.4% [31-33, Wilson] | 11.7% [11-12, Wilson] | 22.0% [21-23, Wilson] |
| P2 the first Glimmora placed had its turn | 78.4% [78-79, Wilson] | 42.5% [42-44, Wilson] | 60.5% [60-61, Wilson] |
| P2 the second Glimmora placed had its turn | 36.8% [36-38, Wilson] | 27.8% [27-29, Wilson] | 32.3% [32-33, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 7.1% [7-8, Wilson] | 10.4% [10-11, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.5% [36-37, Wilson] | 38.9% [38-40, Wilson] | 37.7% [37-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 45.1% [44-46, Wilson] | 28.7% [28-30, Wilson] | 36.9% [36-38, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 54.9% [54-56, Wilson] | 71.3% [70-72, Wilson] | 63.1% [62-64, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 4511 [0-0, Wilson] | 0.0% of 2869 [0-0, Wilson] | 0.0% of 7380 [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 4511 [0-0, Wilson] | 0.0% of 2869 [0-0, Wilson] | 0.0% of 7380 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 4511 [0-0, Wilson] | 0.0% of 2869 [0-0, Wilson] | 0.0% of 7380 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4511 [0-0, Wilson] | 0.0% of 2869 [0-0, Wilson] | 0.0% of 7380 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 4511 [100-100, Wilson] | 100.0% of 2869 [100-100, Wilson] | 100.0% of 7380 [100-100, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: +3.3 points (+2.8 to +3.8); P2.both: +3.8 points (+3.3 to +4.3); P2.g1: +5.5 points (+5.0 to +6.0); P2.g2: +1.6 points (+1.0 to +2.2); P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -11.6 points (-12.2 to -11.0); P3.grimer_muk: -18.3 points (-19.0 to -17.7); P4.ko: -10.7 points (-11.2 to -10.3); P4.win: -10.7 points (-11.2 to -10.3); P4.late1: -1.4 points (-1.5 to -1.2); P4.never: +15.7 points (+15.1 to +16.3); P4.nomoment: -3.6 points (-4.1 to -3.2); P5.ko: -12.1 points (-12.5 to -11.6); P5.win: -12.1 points (-12.5 to -11.6).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.2% [91-92, Wilson] | 82.8% [82-83, Wilson] | 87.0% [87-87, Wilson] |
| P2 both Glimmora had their turn | 47.7% [47-49, Wilson] | 32.6% [32-34, Wilson] | 40.2% [39-41, Wilson] |
| P2 the first Glimmora placed had its turn | 88.5% [88-89, Wilson] | 78.8% [78-80, Wilson] | 83.6% [83-84, Wilson] |
| P2 the second Glimmora placed had its turn | 50.4% [49-51, Wilson] | 36.6% [36-38, Wilson] | 43.5% [43-44, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 3.9% [3-4, Wilson] | 7.4% [7-8, Wilson] | 5.6% [5-6, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 33.6% [33-35, Wilson] | 37.2% [36-38, Wilson] | 35.4% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 53.2% [52-54, Wilson] | 45.9% [45-47, Wilson] | 49.5% [49-50, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 46.8% [46-48, Wilson] | 54.1% [53-55, Wilson] | 50.5% [50-51, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 5323 [0-0, Wilson] | 0.0% of 4586 [0-0, Wilson] | 0.0% of 9909 [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5323 [0-0, Wilson] | 0.0% of 4586 [0-0, Wilson] | 0.0% of 9909 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5323 [0-0, Wilson] | 0.0% of 4586 [0-0, Wilson] | 0.0% of 9909 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5323 [0-0, Wilson] | 0.0% of 4586 [0-0, Wilson] | 0.0% of 9909 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 5323 [100-100, Wilson] | 100.0% of 4586 [100-100, Wilson] | 100.0% of 9909 [100-100, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.both: +6.2 points (+5.6 to +6.8); P2.g1: +1.5 points (+1.1 to +1.8); P2.g2: +5.7 points (+5.0 to +6.3); P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -18.3 points (-18.9 to -17.7); P3.grimer_muk: -21.3 points (-22.0 to -20.7); P4.ko: -21.7 points (-22.3 to -21.2); P4.late1: -2.4 points (-2.6 to -2.2); P4.never: +24.6 points (+24.0 to +25.3); P5.ko: -24.1 points (-24.7 to -23.5).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 96.3% [96-97, Wilson] | 90.7% [90-91, Wilson] | 93.5% [93-94, Wilson] |
| P2 both Glimmora had their turn | 66.8% [66-68, Wilson] | 55.4% [54-56, Wilson] | 61.1% [60-62, Wilson] |
| P2 the first Glimmora placed had its turn | 92.8% [92-93, Wilson] | 85.2% [84-86, Wilson] | 89.0% [89-89, Wilson] |
| P2 the second Glimmora placed had its turn | 70.3% [69-71, Wilson] | 60.9% [60-62, Wilson] | 65.6% [65-66, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 0.8% [1-1, Wilson] | 1.8% [2-2, Wilson] | 1.3% [1-1, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 15.6% [15-16, Wilson] | 21.5% [21-22, Wilson] | 18.6% [18-19, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 59.8% [59-61, Wilson] | 55.2% [54-56, Wilson] | 57.5% [57-58, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 40.2% [39-41, Wilson] | 44.8% [44-46, Wilson] | 42.5% [42-43, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 5980 [0-0, Wilson] | 0.0% of 5516 [0-0, Wilson] | 0.0% of 11496 [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5980 [0-0, Wilson] | 0.0% of 5516 [0-0, Wilson] | 0.0% of 11496 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5980 [0-0, Wilson] | 0.0% of 5516 [0-0, Wilson] | 0.0% of 11496 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5980 [0-0, Wilson] | 0.0% of 5516 [0-0, Wilson] | 0.0% of 11496 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 5980 [100-100, Wilson] | 100.0% of 5516 [100-100, Wilson] | 100.0% of 11496 [100-100, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.both: -1.1 points (-1.8 to -0.5); P2.g1: +3.1 points (+2.7 to +3.4); P2.g2: -3.5 points (-4.2 to -2.8); P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -5.4 points (-5.8 to -5.1); P3.grimer_muk: -17.2 points (-17.8 to -16.6); P4.ko: -44.5 points (-45.2 to -43.8); P4.win: -44.5 points (-45.2 to -43.8); P4.late1: -2.1 points (-2.3 to -1.9); P4.never: +43.5 points (+42.8 to +44.2); P4.nomoment: +3.1 points (+2.6 to +3.5); P5.ko: -46.6 points (-47.3 to -45.9); P5.win: -46.6 points (-47.3 to -45.9).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.9% [82-84, Wilson] | 58.6% [58-60, Wilson] | 70.8% [70-71, Wilson] |
| P2 both Glimmora had their turn | 32.4% [31-33, Wilson] | 11.7% [11-12, Wilson] | 22.0% [21-23, Wilson] |
| P2 the first Glimmora placed had its turn | 78.4% [78-79, Wilson] | 42.5% [42-44, Wilson] | 60.5% [60-61, Wilson] |
| P2 the second Glimmora placed had its turn | 36.8% [36-38, Wilson] | 27.8% [27-29, Wilson] | 32.3% [32-33, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 7.1% [7-8, Wilson] | 10.4% [10-11, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.5% [36-37, Wilson] | 38.9% [38-40, Wilson] | 37.7% [37-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 9.1% [9-10, Wilson] | 3.9% [4-4, Wilson] | 6.5% [6-7, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.9% [90-91, Wilson] | 96.1% [96-96, Wilson] | 93.5% [93-94, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 911 [0-0, Wilson] | 0.0% of 387 [0-1, Wilson] | 0.0% of 1298 [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 911 [0-0, Wilson] | 0.0% of 387 [0-1, Wilson] | 0.0% of 1298 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 911 [0-0, Wilson] | 0.0% of 387 [0-1, Wilson] | 0.0% of 1298 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 911 [0-0, Wilson] | 0.0% of 387 [0-1, Wilson] | 0.0% of 1298 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 911 [100-100, Wilson] | 100.0% of 387 [99-100, Wilson] | 100.0% of 1298 [100-100, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +3.2 points (+2.7 to +3.7); P2.both: +3.6 points (+3.1 to +4.1); P2.g1: +5.5 points (+5.0 to +6.0); P2.g2: +1.4 points (+0.8 to +1.9); P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -13.1 points (-13.6 to -12.5); P3.grimer_muk: -18.3 points (-19.0 to -17.7); P4.ko: -2.2 points (-2.5 to -2.0); P4.win: -2.2 points (-2.5 to -2.0); P4.never: +3.4 points (+3.1 to +3.7); P4.nomoment: -1.2 points (-1.4 to -0.9); P5.ko: -2.2 points (-2.5 to -2.0); P5.win: -2.2 points (-2.5 to -2.0).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 96.3% [96-97, Wilson] | 90.7% [90-91, Wilson] | 93.5% [93-94, Wilson] |
| P2 both Glimmora had their turn | 67.1% [66-68, Wilson] | 55.4% [54-56, Wilson] | 61.3% [61-62, Wilson] |
| P2 the first Glimmora placed had its turn | 92.8% [92-93, Wilson] | 85.2% [84-86, Wilson] | 89.0% [89-89, Wilson] |
| P2 the second Glimmora placed had its turn | 70.6% [70-71, Wilson] | 60.9% [60-62, Wilson] | 65.8% [65-66, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 0.8% [1-1, Wilson] | 1.9% [2-2, Wilson] | 1.4% [1-2, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.2% [30-32, Wilson] | 34.7% [34-36, Wilson] | 32.9% [32-34, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 20.4% [20-21, Wilson] | 18.8% [18-20, Wilson] | 19.6% [19-20, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 79.5% [79-80, Wilson] | 81.2% [80-82, Wilson] | 80.4% [80-81, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 0.0% of 2045 [0-0, Wilson] | 0.0% of 1877 [0-0, Wilson] | 0.0% of 3922 [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 2045 [0-0, Wilson] | 0.0% of 1877 [0-0, Wilson] | 0.0% of 3922 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 2045 [0-0, Wilson] | 0.0% of 1877 [0-0, Wilson] | 0.0% of 3922 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 2045 [0-0, Wilson] | 0.0% of 1877 [0-0, Wilson] | 0.0% of 3922 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 100.0% of 2045 [100-100, Wilson] | 100.0% of 1877 [100-100, Wilson] | 100.0% of 3922 [100-100, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.both: -3.0 points (-3.6 to -2.4); P2.g1: +3.1 points (+2.7 to +3.4); P2.g2: -5.4 points (-6.0 to -4.7); P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -33.6 points (-34.3 to -32.9); P3.grimer_muk: -14.1 points (-14.6 to -13.5); P4.ko: -6.5 points (-6.9 to -6.2); P4.win: -6.5 points (-6.9 to -6.2); P4.never: +7.9 points (+7.5 to +8.3); P4.nomoment: -1.3 points (-1.5 to -1.0); P5.ko: -6.6 points (-7.0 to -6.3); P5.win: -6.6 points (-7.0 to -6.3).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.5% (27.1-27.9) | 27.2% (26.8-27.6) | 27.4% (27.1-27.6) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 52.1% (51.6-52.5) | 51.9% (51.5-52.4) | 52.0% (51.7-52.3) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 62.3% (61.9-62.7) | 62.1% (61.7-62.6) | 62.2% (61.9-62.5) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 66.7% (66.3-67.1) | 66.6% (66.2-67.0) | 66.6% (66.4-66.9) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 68.7% (68.2-69.1) | 68.6% (68.2-69.0) | 68.6% (68.3-68.9) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 69.4% (69.0-69.8) | 69.4% (69.0-69.8) | 69.4% (69.1-69.7) |
| K2 Kingambit in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| K2 Kingambit in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| K2 Kingambit in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| K2 Kingambit in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| K2 Kingambit in play, own turn 6 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| K6 Muk and Regigigas both in play, own turn 3 | 26.1% (25.7-26.4) | 26.3% (25.9-26.7) | 26.2% (25.9-26.4) |
| K6 Muk and Regigigas both in play, own turn 4 | 33.5% (33.1-33.9) | 33.6% (33.2-34.0) | 33.5% (33.3-33.8) |
| K6 Muk and Regigigas both in play, own turn 5 | 39.0% (38.6-39.5) | 39.1% (38.7-39.6) | 39.1% (38.8-39.4) |
| G3 Pawniard in play, own turn 1 | 52.1% (51.6-52.5) | 51.9% (51.5-52.4) | 52.0% (51.7-52.3) |
| G3 Pawniard in play, own turn 2 | 62.3% (61.9-62.7) | 62.1% (61.7-62.6) | 62.2% (61.9-62.5) |
| G3 Pawniard in play, own turn 3 | 66.7% (66.3-67.1) | 66.6% (66.2-67.0) | 66.6% (66.4-66.9) |
| G3 Pawniard in play, own turn 4 | 68.7% (68.2-69.1) | 68.6% (68.2-69.0) | 68.6% (68.3-68.9) |
| G3 Pawniard in play, own turn 5 | 69.4% (69.0-69.8) | 69.4% (69.0-69.8) | 69.4% (69.1-69.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Grimer in play, own turn 1 | 49.7% (49.2-50.1) | 50.3% (49.8-50.7) | 50.0% (49.7-50.3) |
| G3 Alolan Grimer in play, own turn 2 | 38.7% (38.3-39.1) | 39.2% (38.8-39.6) | 38.9% (38.6-39.2) |
| G3 Alolan Grimer in play, own turn 3 | 31.9% (31.4-32.3) | 32.1% (31.7-32.5) | 32.0% (31.7-32.3) |
| G3 Alolan Grimer in play, own turn 4 | 25.5% (25.1-25.9) | 25.8% (25.4-26.2) | 25.7% (25.4-25.9) |
| G3 Alolan Grimer in play, own turn 5 | 20.1% (19.8-20.5) | 20.6% (20.2-20.9) | 20.3% (20.1-20.6) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 19.0% (18.6-19.3) | 19.1% (18.8-19.5) | 19.1% (18.8-19.3) |
| G3 Alolan Muk in play, own turn 3 | 29.3% (28.9-29.7) | 29.6% (29.2-30.0) | 29.4% (29.1-29.7) |
| G3 Alolan Muk in play, own turn 4 | 37.2% (36.7-37.6) | 37.3% (36.9-37.8) | 37.3% (37.0-37.6) |
| G3 Alolan Muk in play, own turn 5 | 43.1% (42.7-43.6) | 43.2% (42.8-43.7) | 43.2% (42.9-43.5) |
| G3 Glimmet in play, own turn 1 | 78.3% (77.9-78.6) | 78.5% (78.1-78.8) | 78.4% (78.1-78.6) |
| G3 Glimmet in play, own turn 2 | 44.9% (44.4-45.3) | 44.8% (44.3-45.2) | 44.8% (44.5-45.1) |
| G3 Glimmet in play, own turn 3 | 32.7% (32.3-33.1) | 32.4% (32.0-32.8) | 32.5% (32.3-32.8) |
| G3 Glimmet in play, own turn 4 | 22.4% (22.1-22.8) | 22.1% (21.8-22.5) | 22.3% (22.0-22.5) |
| G3 Glimmet in play, own turn 5 | 13.9% (13.6-14.2) | 13.6% (13.3-13.9) | 13.8% (13.5-14.0) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 60.4% (60.0-60.8) | 60.5% (60.1-60.9) | 60.4% (60.1-60.7) |
| G3 Glimmora in play, own turn 3 | 75.6% (75.3-76.0) | 75.9% (75.6-76.3) | 75.8% (75.5-76.1) |
| G3 Glimmora in play, own turn 4 | 84.1% (83.8-84.4) | 84.2% (83.9-84.5) | 84.1% (83.9-84.4) |
| G3 Glimmora in play, own turn 5 | 88.8% (88.5-89.1) | 89.0% (88.7-89.3) | 88.9% (88.7-89.1) |
| G3 Regigigas in play, own turn 1 | 78.3% (77.9-78.6) | 78.5% (78.2-78.9) | 78.4% (78.1-78.7) |
| G3 Regigigas in play, own turn 2 | 87.9% (87.6-88.2) | 87.9% (87.6-88.2) | 87.9% (87.7-88.1) |
| G3 Regigigas in play, own turn 3 | 91.7% (91.4-91.9) | 91.5% (91.3-91.8) | 91.6% (91.4-91.8) |
| G3 Regigigas in play, own turn 4 | 93.2% (93.0-93.4) | 93.2% (93.0-93.4) | 93.2% (93.1-93.4) |
| G3 Regigigas in play, own turn 5 | 93.8% (93.6-94.0) | 93.8% (93.6-94.0) | 93.8% (93.7-94.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 69.1% (68.7-69.5) | 69.3% (68.8-69.7) | 69.2% (68.9-69.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 83.7% (83.4-84.0) | 84.0% (83.7-84.3) | 83.8% (83.6-84.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 91.1% (90.8-91.3) | 91.2% (90.9-91.4) | 91.1% (90.9-91.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 94.9% (94.7-95.1) | 95.0% (94.8-95.2) | 95.0% (94.8-95.1) |
| G4.s2 a Stage 2 in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G4.s2 a Stage 2 in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G4.s2 a Stage 2 in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G4.s2 a Stage 2 in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G5.any3 an empty own turn among turns 1-3 | 25.3% (24.9-25.6) | 24.7% (24.4-25.1) | 25.0% (24.7-25.3) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G6 Kingambit with [DD] attached, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G6 Kingambit with [DD] attached, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G6 Kingambit with [DD] attached, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G5 mean empty own turns in turns 1-5 | 0.843 | 0.843 | 0.843 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 0.0% / 8.4% [0-0] | 0.0% / 4.2% [0-0] |
| K3.by3 | 0.0% / 8.6% [0-0] | 0.0% / 8.4% [0-0] | 0.0% / 8.5% [0-0] |
| K3.by4 | 0.0% / 8.6% [0-0] | 0.0% / 8.4% [0-0] | 0.0% / 8.5% [0-0] |
| K3.by5 | 0.0% / 8.6% [0-0] | 0.0% / 16.3% [0-0] | 0.0% / 12.5% [0-0] |
| K3.by6 | 0.0% / 17.2% [0-0] | 0.0% / 24.7% [0-0] | 0.0% / 20.9% [0-0] |
| K3.by7 | 0.0% / 25.5% [0-0] | 0.0% / 48.9% [0-0] | 0.0% / 37.2% [0-0] |
| K3.by8 | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| K3.never | 49.6% / 100.0% [17-75] | 43.3% / 100.0% [18-68] | 46.4% / 100.0% [18-72] |
| K3.k0 | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| K3.k1 | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| K3.k2 | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| K3.k3p | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| K4 | 0.0% / 50.4% [0-0] | 0.0% / 56.7% [0-0] | 0.0% / 53.6% [0-0] |
| K5 | 8.2% / 62.8% [6-9] | 9.0% / 61.3% [7-11] | 8.6% / 62.0% [7-10] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by2: -1.1 points (-1.5 to -0.7); K3.by3: -3.2 points (-4.4 to -2.1); K3.by4: -4.6 points (-5.7 to -3.4); K3.by5: -6.1 points (-7.8 to -4.4); K3.by6: -8.8 points (-12.1 to -5.9); K3.by7: -13.3 points (-21.7 to -6.7); K3.by8: -14.7 points (-24.0 to -7.1); K3.never: +9.0 points (+1.0 to +19.1); K3.k0: -3.9 points (-5.5 to -2.4); K3.k2: -6.8 points (-14.9 to -1.5); K4: -10.8 points (-20.6 to -2.5).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 0.0% [0-0] | 0.0% [0-0] |
| K3.by3 | 0.0% / 11.3% [0-0] | 0.0% [0-0] | 0.0% / 5.7% [0-0] |
| K3.by4 | 0.0% / 11.3% [0-0] | 0.0% [0-0] | 0.0% / 5.7% [0-0] |
| K3.by5 | 0.0% / 11.3% [0-0] | 0.0% / 31.4% [0-0] | 0.0% / 21.4% [0-0] |
| K3.by6 | 0.0% / 11.3% [0-0] | 0.0% / 31.4% [0-0] | 0.0% / 21.4% [0-0] |
| K3.by7 | 0.0% / 22.9% [0-0] | 0.0% / 64.9% [0-0] | 0.0% / 43.9% [0-0] |
| K3.by8 | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| K3.never | 55.1% / 100.0% [20-87] | 16.7% / 100.0% [0-44] | 35.9% / 100.0% [14-65] |
| K3.k0 | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| K3.k1 | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| K3.k2 | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| K3.k3p | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| K4 | 0.0% / 44.9% [0-0] | 0.0% / 83.3% [0-0] | 0.0% / 64.1% [0-0] |
| K5 | 8.1% / 55.5% [6-10] | 9.5% / 85.4% [8-11] | 8.8% / 70.5% [7-10] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -3.7 points (-4.6 to -2.6); K3.by4: -4.7 points (-5.9 to -3.3); K3.by5: -6.3 points (-7.5 to -5.1); K3.by6: -6.9 points (-8.2 to -5.5); K3.by7: -15.5 points (-26.3 to -6.8); K3.by8: -15.5 points (-26.3 to -6.8); K3.k0: -4.4 points (-5.8 to -3.0); K3.k2: -5.7 points (-13.5 to -1.5); K4: -11.1 points (-22.5 to -2.0).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 0.0% [0-0] | 0.0% [0-0] |
| K3.by3 | 0.0% [0-0] | 0.0% [0-0] | 0.0% [0-0] |
| K3.by4 | 0.0% [0-0] | 0.0% [0-0] | 0.0% [0-0] |
| K3.by5 | 0.0% [0-0] | 0.0% [0-0] | 0.0% [0-0] |
| K3.by6 | 0.0% [0-0] | 0.0% / 4.3% [0-0] | 0.0% / 2.2% [0-0] |
| K3.by7 | 0.0% / 4.7% [0-0] | 0.0% / 11.0% [0-0] | 0.0% / 7.9% [0-0] |
| K3.by8 | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| K3.never | 87.9% / 100.0% [79-95] | 86.6% / 100.0% [79-94] | 87.3% / 100.0% [79-94] |
| K3.k0 | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| K3.k1 | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| K3.k2 | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| K3.k3p | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| K4 | 0.0% / 12.1% [0-0] | 0.0% / 13.4% [0-0] | 0.0% / 12.7% [0-0] |
| K5 | 9.4% / 22.7% [9-10] | 10.2% / 22.4% [9-11] | 9.8% / 22.6% [9-10] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by2: -1.3 points (-1.5 to -1.1); K3.by3: -3.4 points (-3.9 to -3.0); K3.by4: -4.6 points (-5.0 to -4.1); K3.by5: -6.5 points (-7.2 to -5.8); K3.by6: -8.7 points (-10.1 to -7.4); K3.by7: -10.8 points (-13.0 to -8.8); K3.by8: -12.3 points (-15.2 to -9.7); K3.never: +10.2 points (+7.6 to +13.0); K3.k0: -4.2 points (-4.8 to -3.6); K3.k2: -3.4 points (-4.6 to -2.4); K3.k3p: -4.8 points (-7.5 to -2.5); K4: -8.2 points (-11.0 to -5.6).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by5 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by6 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by7 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by8 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.never | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k3p | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K5 | 15.6% [15-16, Wilson] | 19.2% [18-20, Wilson] | 17.4% [17-18, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.2 points (-1.4 to -1.1); K3.by4: -4.0 points (-4.2 to -3.7); K3.by5: -9.5 points (-9.9 to -9.0); K3.by6: -11.2 points (-11.6 to -10.7); K3.by7: -11.2 points (-11.6 to -10.7); K3.by8: -11.2 points (-11.6 to -10.7); K3.never: +11.2 points (+10.7 to +11.6); K3.k2: -2.4 points (-2.6 to -2.2); K3.k3p: -8.8 points (-9.2 to -8.4); K4: -11.2 points (-11.6 to -10.7); K5: -4.3 points (-4.8 to -3.8).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by5 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by6 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by7 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by8 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.never | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k3p | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K5 | 12.4% [12-13, Wilson] | 16.3% [16-17, Wilson] | 14.3% [14-15, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by2: -1.5 points (-1.7 to -1.4); K3.by3: -3.7 points (-4.0 to -3.5); K3.by4: -5.1 points (-5.4 to -4.8); K3.by5: -11.0 points (-11.4 to -10.6); K3.by6: -22.1 points (-22.7 to -21.6); K3.by7: -24.7 points (-25.3 to -24.1); K3.by8: -24.7 points (-25.3 to -24.1); K3.never: +24.7 points (+24.1 to +25.3); K3.k0: -3.7 points (-4.0 to -3.5); K3.k2: -2.2 points (-2.4 to -2.0); K3.k3p: -18.7 points (-19.3 to -18.2); K4: -20.9 points (-21.5 to -20.4); K5: -1.9 points (-2.4 to -1.5).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by5 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by6 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by7 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by8 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.never | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k3p | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K5 | 9.1% [9-10, Wilson] | 10.2% [10-11, Wilson] | 9.7% [9-10, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by2: -1.5 points (-1.7 to -1.4); K3.by3: -3.7 points (-4.0 to -3.5); K3.by4: -3.7 points (-4.0 to -3.5); K3.by5: -6.2 points (-6.5 to -5.9); K3.by6: -8.1 points (-8.5 to -7.8); K3.by7: -24.4 points (-25.0 to -23.8); K3.by8: -46.1 points (-46.8 to -45.4); K3.never: +46.1 points (+45.4 to +46.8); K3.k0: -3.7 points (-4.0 to -3.5); K3.k2: -4.5 points (-4.8 to -4.2); K3.k3p: -37.9 points (-38.5 to -37.2); K4: -42.4 points (-43.0 to -41.7).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by5 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by6 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by7 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by8 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.never | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k3p | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K5 | 15.6% [15-16, Wilson] | 19.2% [18-20, Wilson] | 17.4% [17-18, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.2 points (-1.4 to -1.1); K3.by4: -3.9 points (-4.2 to -3.6); K3.by5: -9.0 points (-9.4 to -8.6); K3.by6: -10.8 points (-11.2 to -10.3); K3.by7: -10.8 points (-11.2 to -10.3); K3.by8: -10.8 points (-11.2 to -10.3); K3.never: +10.8 points (+10.3 to +11.2); K3.k2: -2.4 points (-2.6 to -2.2); K3.k3p: -8.4 points (-8.8 to -8.0); K4: -10.8 points (-11.2 to -10.3); K5: -4.3 points (-4.8 to -3.8).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by5 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by6 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by7 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by8 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by9 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by10 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.never | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k3p | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K4 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K5 | 9.4% [9-10, Wilson] | 10.6% [10-11, Wilson] | 10.0% [10-10, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by2: -1.5 points (-1.7 to -1.4); K3.by3: -3.7 points (-4.0 to -3.5); K3.by4: -3.7 points (-4.0 to -3.5); K3.by5: -6.2 points (-6.5 to -5.9); K3.by6: -8.1 points (-8.5 to -7.8); K3.by7: -20.1 points (-20.6 to -19.5); K3.by8: -37.1 points (-37.8 to -36.4); K3.by9: -40.7 points (-41.4 to -40.0); K3.by10: -43.8 points (-44.5 to -43.1); K3.never: +43.8 points (+43.1 to +44.5); K3.k0: -3.7 points (-4.0 to -3.5); K3.k2: -4.5 points (-4.8 to -4.2); K3.k3p: -35.6 points (-36.2 to -34.9); K4: -40.1 points (-40.7 to -39.4).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.1 (+19.8 to +20.5) FLAG | +20.2 (+19.8 to +20.5) FLAG | +20.2 (+19.9 to +20.4) FLAG |
| K1 Pawniard in play at setup | -1.7 (-1.8 to -1.5) FLAG | -1.6 (-1.8 to -1.5) FLAG | -1.6 (-1.8 to -1.5) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -3.9 (-4.1 to -3.6) FLAG | -3.7 (-4.0 to -3.4) FLAG | -3.8 (-4.0 to -3.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -5.7 (-6.0 to -5.3) FLAG | -5.7 (-6.0 to -5.4) FLAG | -5.7 (-5.9 to -5.4) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -7.8 (-8.1 to -7.5) FLAG | -7.9 (-8.3 to -7.6) FLAG | -7.9 (-8.1 to -7.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -9.9 (-10.3 to -9.6) FLAG | -10.0 (-10.4 to -9.7) FLAG | -10.0 (-10.2 to -9.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -11.4 (-11.7 to -11.0) FLAG | -11.4 (-11.7 to -11.0) FLAG | -11.4 (-11.6 to -11.1) FLAG |
| K2 Kingambit in play, own turn 2 | -10.7 (-11.0 to -10.5) FLAG | -10.8 (-11.0 to -10.5) FLAG | -10.7 (-10.9 to -10.5) FLAG |
| K2 Kingambit in play, own turn 3 | -21.1 (-21.4 to -20.7) FLAG | -21.1 (-21.5 to -20.8) FLAG | -21.1 (-21.3 to -20.8) FLAG |
| K2 Kingambit in play, own turn 4 | -33.0 (-33.4 to -32.6) FLAG | -33.1 (-33.5 to -32.7) FLAG | -33.1 (-33.4 to -32.8) FLAG |
| K2 Kingambit in play, own turn 5 | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.7 to -46.1) FLAG |
| K2 Kingambit in play, own turn 6 | -59.4 (-59.9 to -59.0) FLAG | -59.1 (-59.6 to -58.7) FLAG | -59.3 (-59.6 to -59.0) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +3.9 (+3.5 to +4.2) FLAG | +4.0 (+3.7 to +4.4) FLAG | +3.9 (+3.7 to +4.2) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +3.1 (+2.7 to +3.5) FLAG | +3.1 (+2.7 to +3.5) FLAG | +3.1 (+2.8 to +3.4) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.1 (+1.7 to +2.5) FLAG | +2.1 (+1.7 to +2.5) FLAG | +2.1 (+1.8 to +2.4) FLAG |
| G3 Pawniard in play, own turn 1 | -3.9 (-4.1 to -3.6) FLAG | -3.7 (-4.0 to -3.4) FLAG | -3.8 (-4.0 to -3.6) FLAG |
| G3 Pawniard in play, own turn 2 | +5.1 (+4.7 to +5.5) FLAG | +5.1 (+4.7 to +5.5) FLAG | +5.1 (+4.8 to +5.4) FLAG |
| G3 Pawniard in play, own turn 3 | +13.2 (+12.8 to +13.7) FLAG | +13.2 (+12.7 to +13.7) FLAG | +13.2 (+12.9 to +13.6) FLAG |
| G3 Pawniard in play, own turn 4 | +23.1 (+22.6 to +23.6) FLAG | +23.1 (+22.6 to +23.6) FLAG | +23.1 (+22.7 to +23.4) FLAG |
| G3 Pawniard in play, own turn 5 | +35.1 (+34.5 to +35.6) FLAG | +35.1 (+34.5 to +35.6) FLAG | +35.1 (+34.7 to +35.4) FLAG |
| G3 Kingambit in play, own turn 2 | -10.7 (-11.0 to -10.5) FLAG | -10.8 (-11.0 to -10.5) FLAG | -10.7 (-10.9 to -10.5) FLAG |
| G3 Kingambit in play, own turn 3 | -21.1 (-21.4 to -20.7) FLAG | -21.1 (-21.5 to -20.8) FLAG | -21.1 (-21.3 to -20.8) FLAG |
| G3 Kingambit in play, own turn 4 | -33.0 (-33.4 to -32.6) FLAG | -33.1 (-33.5 to -32.7) FLAG | -33.1 (-33.4 to -32.8) FLAG |
| G3 Kingambit in play, own turn 5 | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.7 to -46.1) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -4.9 (-5.2 to -4.7) FLAG | -4.5 (-4.8 to -4.2) FLAG | -4.7 (-4.9 to -4.5) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -7.6 (-7.9 to -7.2) FLAG | -7.4 (-7.7 to -7.1) FLAG | -7.5 (-7.7 to -7.2) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -8.1 (-8.4 to -7.7) FLAG | -8.0 (-8.3 to -7.6) FLAG | -8.0 (-8.2 to -7.8) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -7.5 (-7.9 to -7.2) FLAG | -7.4 (-7.7 to -7.1) FLAG | -7.5 (-7.7 to -7.2) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -6.5 (-6.8 to -6.2) FLAG | -6.5 (-6.8 to -6.2) FLAG | -6.5 (-6.7 to -6.3) FLAG |
| G3 Alolan Muk in play, own turn 3 | -1.8 (-2.1 to -1.5) FLAG | -1.8 (-2.1 to -1.5) FLAG | -1.8 (-2.0 to -1.6) FLAG |
| G3 Alolan Muk in play, own turn 4 | -4.0 (-4.4 to -3.6) FLAG | -4.0 (-4.4 to -3.6) FLAG | -4.0 (-4.3 to -3.7) FLAG |
| G3 Alolan Muk in play, own turn 5 | -6.1 (-6.5 to -5.7) FLAG | -6.0 (-6.4 to -5.6) FLAG | -6.1 (-6.3 to -5.8) FLAG |
| G3 Glimmet in play, own turn 1 | -3.8 (-4.1 to -3.6) FLAG | -4.0 (-4.2 to -3.7) FLAG | -3.9 (-4.1 to -3.7) FLAG |
| G3 Glimmet in play, own turn 2 | -7.9 (-8.3 to -7.6) FLAG | -7.7 (-8.0 to -7.3) FLAG | -7.8 (-8.0 to -7.6) FLAG |
| G3 Glimmet in play, own turn 3 | -9.5 (-9.8 to -9.1) FLAG | -9.5 (-9.9 to -9.2) FLAG | -9.5 (-9.8 to -9.2) FLAG |
| G3 Glimmet in play, own turn 4 | -8.5 (-8.9 to -8.2) FLAG | -8.8 (-9.1 to -8.4) FLAG | -8.6 (-8.9 to -8.4) FLAG |
| G3 Glimmet in play, own turn 5 | -6.3 (-6.6 to -6.0) FLAG | -6.2 (-6.5 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| G3 Glimmora in play, own turn 2 | -2.8 (-3.0 to -2.5) FLAG | -2.8 (-3.1 to -2.6) FLAG | -2.8 (-3.0 to -2.6) FLAG |
| G3 Glimmora in play, own turn 3 | -4.1 (-4.3 to -3.8) FLAG | -4.0 (-4.2 to -3.7) FLAG | -4.0 (-4.2 to -3.8) FLAG |
| G3 Glimmora in play, own turn 4 | -5.3 (-5.6 to -5.1) FLAG | -5.2 (-5.5 to -5.0) FLAG | -5.3 (-5.5 to -5.1) FLAG |
| G3 Glimmora in play, own turn 5 | -6.3 (-6.5 to -6.0) FLAG | -6.2 (-6.4 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| G3 Regigigas in play, own turn 1 | +22.9 (+22.5 to +23.3) FLAG | +23.3 (+22.9 to +23.7) FLAG | +23.1 (+22.8 to +23.4) FLAG |
| G3 Regigigas in play, own turn 2 | +20.2 (+19.9 to +20.6) FLAG | +20.8 (+20.4 to +21.2) FLAG | +20.5 (+20.3 to +20.8) FLAG |
| G3 Regigigas in play, own turn 3 | +17.2 (+16.9 to +17.6) FLAG | +17.4 (+17.0 to +17.7) FLAG | +17.3 (+17.1 to +17.6) FLAG |
| G3 Regigigas in play, own turn 4 | +15.0 (+14.7 to +15.3) FLAG | +15.1 (+14.7 to +15.4) FLAG | +15.0 (+14.8 to +15.3) FLAG |
| G3 Regigigas in play, own turn 5 | +13.5 (+13.2 to +13.8) FLAG | +13.6 (+13.3 to +14.0) FLAG | +13.6 (+13.3 to +13.8) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -6.4 (-6.7 to -6.1) FLAG | -6.4 (-6.7 to -6.1) FLAG | -6.4 (-6.6 to -6.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -5.9 (-6.2 to -5.7) FLAG | -5.8 (-6.1 to -5.5) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -4.9 (-5.1 to -4.7) FLAG | -4.7 (-4.9 to -4.5) FLAG | -4.8 (-5.0 to -4.6) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -3.7 (-3.9 to -3.5) FLAG | -3.6 (-3.8 to -3.4) FLAG | -3.6 (-3.8 to -3.5) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | -10.7 (-11.0 to -10.5) FLAG | -10.8 (-11.0 to -10.5) FLAG | -10.7 (-10.9 to -10.5) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -21.1 (-21.4 to -20.7) FLAG | -21.1 (-21.5 to -20.8) FLAG | -21.1 (-21.3 to -20.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -33.0 (-33.4 to -32.6) FLAG | -33.1 (-33.5 to -32.7) FLAG | -33.1 (-33.4 to -32.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.7 to -46.1) FLAG |
| G5.any3 an empty own turn among turns 1-3 | +2.1 (+1.8 to +2.4) FLAG | +2.3 (+2.0 to +2.5) FLAG | +2.2 (+2.0 to +2.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | -10.8 (-11.0 to -10.5) FLAG | -5.4 (-5.5 to -5.2) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -17.6 (-17.9 to -17.2) FLAG | -21.1 (-21.5 to -20.8) FLAG | -19.3 (-19.6 to -19.1) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -33.0 (-33.4 to -32.6) FLAG | -33.1 (-33.5 to -32.7) FLAG | -33.1 (-33.4 to -32.8) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.9 to -46.0) FLAG | -46.4 (-46.7 to -46.1) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.085 (+0.080 to +0.089) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Rare Candy A3 144 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.2 points
- C-his (per-game bootstrap): P2 the second Glimmora placed had its turn -6.2 points (-11.2 to -1.0); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.4 points (-9.3 to -1.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -12.3 points (-15.8 to -8.9); P4 ready at the winning moment: Knocks out their strongest -12.1 points (-23.5 to -2.5); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.9 points (-3.2 to -0.8); P5 plan reached in time: Knocks out their strongest -17.5 points (-31.1 to -6.0)
- C-his, seat-matched (per-game bootstrap): P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.6 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -6.0 points (-13.7 to -0.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -13.5 points (-17.8 to -9.0); P4 ready at the winning moment: Knocks out their strongest -10.5 points (-21.5 to -2.5); P5 plan reached in time: Knocks out their strongest -14.4 points (-29.4 to -4.9)
- C-bot (per-game bootstrap): P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.7 points (-16.8 to -10.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -19.2 points (-21.8 to -16.6); P4 ready at the winning moment: Knocks out their strongest -7.2 points (-11.1 to -3.9); P4 not ready, ready 1 turn late -4.1 points (-6.4 to -2.1); P4 not ready, ready 2 or more turns late -1.6 points (-2.9 to -0.6); P4 the moment came and Kingambit was never ready in the deal +10.2 points (+5.2 to +15.5); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.1 points (-1.7 to -0.4); P5 plan reached in time: Knocks out their strongest -12.9 points (-19.2 to -7.5)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn +3.3 points (+2.8 to +3.8); P2 both Glimmora had their turn +3.8 points (+3.3 to +4.3); P2 the first Glimmora placed had its turn +5.5 points (+5.0 to +6.0); P2 the second Glimmora placed had its turn +1.6 points (+1.0 to +2.2); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -11.6 points (-12.2 to -11.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -18.3 points (-19.0 to -17.7); P4 ready at the winning moment: Knocks out their strongest -10.7 points (-11.2 to -10.3); P4 ready at the winning moment: Wins outright (a lower bound) -10.7 points (-11.2 to -10.3); P4 not ready, ready 1 turn late -1.4 points (-1.5 to -1.2); P4 the moment came and Kingambit was never ready in the deal +15.7 points (+15.1 to +16.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -3.6 points (-4.1 to -3.2); P5 plan reached in time: Knocks out their strongest -12.1 points (-12.5 to -11.6); P5 plan reached in time: Wins outright (a lower bound) -12.1 points (-12.5 to -11.6)
- C-fixed medium (paired test): P2 both Glimmora had their turn +6.2 points (+5.6 to +6.8); P2 the first Glimmora placed had its turn +1.5 points (+1.1 to +1.8); P2 the second Glimmora placed had its turn +5.7 points (+5.0 to +6.3); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -18.3 points (-18.9 to -17.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -21.3 points (-22.0 to -20.7); P4 ready at the winning moment: Knocks out their strongest -21.7 points (-22.3 to -21.2); P4 not ready, ready 1 turn late -2.4 points (-2.6 to -2.2); P4 the moment came and Kingambit was never ready in the deal +24.6 points (+24.0 to +25.3); P5 plan reached in time: Knocks out their strongest -24.1 points (-24.7 to -23.5)
- C-fixed slow (paired test): P2 both Glimmora had their turn -1.1 points (-1.8 to -0.5); P2 the first Glimmora placed had its turn +3.1 points (+2.7 to +3.4); P2 the second Glimmora placed had its turn -3.5 points (-4.2 to -2.8); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -5.4 points (-5.8 to -5.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -17.2 points (-17.8 to -16.6); P4 ready at the winning moment: Knocks out their strongest -44.5 points (-45.2 to -43.8); P4 ready at the winning moment: Wins outright (a lower bound) -44.5 points (-45.2 to -43.8); P4 not ready, ready 1 turn late -2.1 points (-2.3 to -1.9); P4 the moment came and Kingambit was never ready in the deal +43.5 points (+42.8 to +44.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.1 points (+2.6 to +3.5); P5 plan reached in time: Knocks out their strongest -46.6 points (-47.3 to -45.9); P5 plan reached in time: Wins outright (a lower bound) -46.6 points (-47.3 to -45.9)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +3.2 points (+2.7 to +3.7); P2 both Glimmora had their turn +3.6 points (+3.1 to +4.1); P2 the first Glimmora placed had its turn +5.5 points (+5.0 to +6.0); P2 the second Glimmora placed had its turn +1.4 points (+0.8 to +1.9); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.1 points (-13.6 to -12.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -18.3 points (-19.0 to -17.7); P4 ready at the winning moment: Knocks out their strongest -2.2 points (-2.5 to -2.0); P4 ready at the winning moment: Wins outright (a lower bound) -2.2 points (-2.5 to -2.0); P4 the moment came and Kingambit was never ready in the deal +3.4 points (+3.1 to +3.7); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.2 points (-1.4 to -0.9); P5 plan reached in time: Knocks out their strongest -2.2 points (-2.5 to -2.0); P5 plan reached in time: Wins outright (a lower bound) -2.2 points (-2.5 to -2.0)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 both Glimmora had their turn -3.0 points (-3.6 to -2.4); P2 the first Glimmora placed had its turn +3.1 points (+2.7 to +3.4); P2 the second Glimmora placed had its turn -5.4 points (-6.0 to -4.7); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -33.6 points (-34.3 to -32.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.1 points (-14.6 to -13.5); P4 ready at the winning moment: Knocks out their strongest -6.5 points (-6.9 to -6.2); P4 ready at the winning moment: Wins outright (a lower bound) -6.5 points (-6.9 to -6.2); P4 the moment came and Kingambit was never ready in the deal +7.9 points (+7.5 to +8.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.3 points (-1.5 to -1.0); P5 plan reached in time: Knocks out their strongest -6.6 points (-7.0 to -6.3); P5 plan reached in time: Wins outright (a lower bound) -6.6 points (-7.0 to -6.3)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K6 Muk and Regigigas both in play, own turn 3 +3.9 points; K6 Muk and Regigigas both in play, own turn 4 +3.1 points; K6 Muk and Regigigas both in play, own turn 5 +2.1 points; G3 Pawniard in play, own turn 2 +5.1 points; G3 Pawniard in play, own turn 3 +13.2 points; G3 Pawniard in play, own turn 4 +23.1 points; G3 Pawniard in play, own turn 5 +35.1 points; G3 Regigigas in play, own turn 1 +23.1 points; G3 Regigigas in play, own turn 2 +20.5 points; G3 Regigigas in play, own turn 3 +17.3 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.6 points; K1 Pawniard line in play (end of own turn t), own turn 1 -3.8 points; K1 Pawniard line in play (end of own turn t), own turn 2 -5.7 points; K1 Pawniard line in play (end of own turn t), own turn 3 -7.9 points; K1 Pawniard line in play (end of own turn t), own turn 4 -10.0 points; K1 Pawniard line in play (end of own turn t), own turn 5 -11.4 points; K2 Kingambit in play, own turn 2 -10.7 points; K2 Kingambit in play, own turn 3 -21.1 points; K2 Kingambit in play, own turn 4 -33.1 points; K2 Kingambit in play, own turn 5 -46.4 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by2 -1.1; K3.by3 -3.2; K3.by4 -4.6; K3.by5 -6.1; K3.by6 -8.8; K3.by7 -13.3; K3.by8 -14.7; K3.never +9.0; K3.k0 -3.9; K3.k2 -6.8; K4 -10.8; C-his, seat-matched: K3.by3 -3.7; K3.by4 -4.7; K3.by5 -6.3; K3.by6 -6.9; K3.by7 -15.5; K3.by8 -15.5; K3.k0 -4.4; K3.k2 -5.7; K4 -11.1; C-bot: K3.by2 -1.3; K3.by3 -3.4; K3.by4 -4.6; K3.by5 -6.5; K3.by6 -8.7; K3.by7 -10.8; K3.by8 -12.3; K3.never +10.2; K3.k0 -4.2; K3.k2 -3.4; K3.k3p -4.8; K4 -8.2; C-fixed fast: K3.by3 -1.2; K3.by4 -4.0; K3.by5 -9.5; K3.by6 -11.2; K3.by7 -11.2; K3.by8 -11.2; K3.never +11.2; K3.k2 -2.4; K3.k3p -8.8; K4 -11.2; K5 -4.3; C-fixed medium: K3.by2 -1.5; K3.by3 -3.7; K3.by4 -5.1; K3.by5 -11.0; K3.by6 -22.1; K3.by7 -24.7; K3.by8 -24.7; K3.never +24.7; K3.k0 -3.7; K3.k2 -2.2; K3.k3p -18.7; K4 -20.9; K5 -1.9; C-fixed slow: K3.by2 -1.5; K3.by3 -3.7; K3.by4 -3.7; K3.by5 -6.2; K3.by6 -8.1; K3.by7 -24.4; K3.by8 -46.1; K3.never +46.1; K3.k0 -3.7; K3.k2 -4.5; K3.k3p -37.9; K4 -42.4; C-fixed reference (fast pace, 190-HP Mega ex): K3.by3 -1.2; K3.by4 -3.9; K3.by5 -9.0; K3.by6 -10.8; K3.by7 -10.8; K3.by8 -10.8; K3.never +10.8; K3.k2 -2.4; K3.k3p -8.4; K4 -10.8; K5 -4.3; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by2 -1.5; K3.by3 -3.7; K3.by4 -3.7; K3.by5 -6.2; K3.by6 -8.1; K3.by7 -20.1; K3.by8 -37.1; K3.by9 -40.7; K3.by10 -43.8; K3.never +43.8; K3.k0 -3.7; K3.k2 -4.5; K3.k3p -35.6; K4 -40.1.
Not valued here (changed cards the script never plays: they count as blanks): none.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Ilima A3 149 +1 Regigigas B3 134 (card-list id 54be04900624)

Changes: ['-1 Ilima A3 149', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 285,446; the valuation and the fallback rule disagree at 113,410 of 285,446 Copycat decisions (39.7%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 49.0% (48.5-49.4) | 48.8% (48.4-49.3) | 48.9% (48.6-49.2) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.9% / 96.2% [75-95] | 78.1% / 91.6% [63-90] | 82.5% / 93.9% [69-92] |
| P2 both Glimmora had their turn | 28.9% / 66.3% [21-37] | 25.7% / 67.5% [17-35] | 27.3% / 66.9% [19-35] |
| P2 the first Glimmora placed had its turn | 84.5% / 92.5% [72-93] | 72.6% / 83.3% [57-86] | 78.6% / 87.9% [65-89] |
| P2 the second Glimmora placed had its turn | 31.2% / 66.0% [22-40] | 31.2% / 67.7% [22-41] | 31.2% / 66.8% [23-39] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9] | 8.7% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.3% / 49.4% [1-2] | 2.4% / 56.1% [1-4] | 1.9% / 52.8% [1-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 14.9% / 58.5% [13-17] | 18.5% / 65.1% [15-22] | 16.7% / 61.8% [14-20] |
| P4 ready at the winning moment: Knocks out their strongest | 13.8% / 39.4% [3-27] | 10.2% / 38.8% [2-20] | 12.0% / 39.1% [2-23] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.9% / 28.4% [0-9] | 1.9% / 30.5% [0-6] | 2.4% / 29.5% [0-7] |
| P4 not ready, ready 1 turn late | 4.9% / 47.2% [0-13] | 4.1% / 51.0% [0-10] | 4.5% / 49.1% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.5% / 43.8% [0-5] | 1.6% / 48.5% [0-5] | 1.5% / 46.1% [0-5] |
| P4 the moment came and Kingambit was never ready in the deal | 8.2% / 50.5% [0-20] | 9.2% / 56.0% [0-22] | 8.7% / 53.3% [0-21] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.3% / 54.8% [8-54] | 28.1% / 56.7% [9-52] | 28.7% / 55.8% [8-53] |
| P5 plan reached in time: Knocks out their strongest | 20.2% / 62.5% [7-36] | 15.9% / 62.8% [5-29] | 18.0% / 62.6% [6-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.2% / 45.5% [0-10] | 2.4% / 49.3% [0-7] | 2.8% / 47.4% [0-9] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 48.8% of 2841 [23-73] | 40.7% of 2501 [21-64] | 45.0% of 5342 [23-69] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.1% of 2841 [0-39] | 7.6% of 2501 [0-34] | 8.9% of 5342 [0-37] |
| P4 not ready, ready 1 turn late | 17.1% of 2841 [0-56] | 16.5% of 2501 [0-50] | 16.8% of 5342 [0-53] |
| P4 not ready, ready 2 or more turns late | 5.2% of 2841 [0-18] | 6.2% of 2501 [0-22] | 5.7% of 5342 [0-20] |
| P4 the moment came and Kingambit was never ready in the deal | 28.9% of 2841 [0-52] | 36.6% of 2501 [0-64] | 32.5% of 5342 [0-58] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: -8.5 points (-11.8 to -5.4); P2.g2: -10.1 points (-13.3 to -7.0); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -4.2 points (-9.0 to -1.1); P3.grimer_muk: -13.4 points (-17.4 to -9.7); P4.nomoment: -1.7 points (-3.1 to -0.6).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.2% / 95.9% [67-95] | 87.4% / 95.6% [77-95] | 86.3% / 95.8% [76-94] |
| P2 both Glimmora had their turn | 28.4% / 61.0% [19-38] | 26.3% / 82.9% [17-44] | 27.4% / 71.9% [19-37] |
| P2 the first Glimmora placed had its turn | 82.5% / 92.2% [66-93] | 84.4% / 87.8% [73-94] | 83.4% / 90.0% [74-91] |
| P2 the second Glimmora placed had its turn | 31.1% / 61.2% [20-42] | 29.3% / 79.2% [18-49] | 30.2% / 70.2% [21-40] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9] | 8.7% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.0% / 44.1% [0-2] | 3.1% / 81.0% [0-5] | 2.0% / 62.5% [0-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 15.1% / 53.7% [13-19] | 19.6% / 87.3% [12-25] | 17.4% / 70.5% [13-21] |
| P4 ready at the winning moment: Knocks out their strongest | 17.4% / 39.7% [2-34] | 4.1% / 55.8% [0-12] | 10.7% / 47.8% [2-22] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.6% / 26.9% [0-14] | 0.0% / 51.7% [0-0] | 2.3% / 39.3% [0-9] |
| P4 not ready, ready 1 turn late | 6.5% / 42.0% [0-17] | 0.0% / 79.1% [0-0] | 3.2% / 60.6% [0-10] |
| P4 not ready, ready 2 or more turns late | 1.9% / 37.4% [0-6] | 0.0% / 79.1% [0-0] | 0.9% / 58.3% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 11.3% / 46.8% [0-27] | 0.0% / 79.1% [0-0] | 5.6% / 63.0% [0-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 27.5% / 49.8% [5-57] | 16.8% / 68.5% [0-45] | 22.1% / 59.2% [6-43] |
| P5 plan reached in time: Knocks out their strongest | 25.7% / 61.3% [8-45] | 4.1% / 83.2% [0-12] | 14.9% / 72.2% [5-30] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.1% / 40.6% [0-16] | 0.0% / 79.1% [0-0] | 2.5% / 59.9% [0-10] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 46.9% of 3700 [15-67] | 100.0% of 406 [100-100] | 52.2% of 4106 [27-76] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.3% of 3700 [0-45] | 0.0% of 406 [0-0] | 11.1% of 4106 [0-38] |
| P4 not ready, ready 1 turn late | 17.5% of 3700 [0-64] | 0.0% of 406 [0-0] | 15.8% of 4106 [0-45] |
| P4 not ready, ready 2 or more turns late | 5.1% of 3700 [0-20] | 0.0% of 406 [0-0] | 4.6% of 4106 [0-15] |
| P4 the moment came and Kingambit was never ready in the deal | 30.5% of 3700 [0-56] | 0.0% of 406 [0-0] | 27.4% of 4106 [0-50] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -1.3 points (-2.6 to -0.6); P2.both: -7.9 points (-11.5 to -5.0); P2.g2: -9.0 points (-12.6 to -6.1); P3.pawn_lead: -4.1 points (-4.4 to -3.9); P3.pawn_promo: -5.6 points (-13.0 to -0.9); P3.grimer_muk: -14.0 points (-18.6 to -9.1).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.5% / 90.6% [86-92] | 81.7% / 83.4% [77-86] | 85.6% / 87.0% [82-89] |
| P2 both Glimmora had their turn | 31.1% / 38.2% [28-35] | 25.4% / 33.7% [22-29] | 28.3% / 35.9% [25-32] |
| P2 the first Glimmora placed had its turn | 84.4% / 84.7% [79-89] | 73.7% / 74.1% [68-79] | 79.1% / 79.4% [74-84] |
| P2 the second Glimmora placed had its turn | 36.2% / 42.6% [33-39] | 33.4% / 40.2% [30-36] | 34.8% / 41.4% [32-38] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9] | 8.7% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.2% / 13.6% [2-3] | 3.7% / 16.1% [3-4] | 2.9% / 14.8% [2-4] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 16.2% / 26.3% [15-17] | 21.7% / 32.3% [20-23] | 19.0% / 29.3% [18-20] |
| P4 ready at the winning moment: Knocks out their strongest | 7.4% / 13.7% [4-12] | 6.7% / 14.1% [4-10] | 7.1% / 13.9% [4-11] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.3% / 6.5% [0-1] | 0.7% / 8.1% [0-2] | 0.5% / 7.3% [0-1] |
| P4 not ready, ready 1 turn late | 5.2% / 13.3% [3-8] | 4.1% / 14.0% [2-6] | 4.7% / 13.7% [2-7] |
| P4 not ready, ready 2 or more turns late | 1.8% / 9.9% [1-3] | 2.1% / 12.0% [1-4] | 2.0% / 11.0% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 8.4% / 16.5% [4-14] | 9.4% / 19.3% [5-15] | 8.9% / 17.9% [4-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.0% / 75.3% [57-80] | 67.8% / 75.2% [57-78] | 68.4% / 75.2% [57-79] |
| P5 plan reached in time: Knocks out their strongest | 14.5% / 22.6% [8-22] | 12.9% / 22.8% [8-19] | 13.7% / 22.7% [8-20] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.5% / 8.6% [0-1] | 0.7% / 10.6% [0-2] | 0.6% / 9.6% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 32.5% of 2286 [21-46] | 30.1% of 2230 [21-41] | 31.3% of 4516 [21-43] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.3% of 2286 [0-5] | 2.9% of 2230 [0-10] | 2.1% of 4516 [0-6] |
| P4 not ready, ready 1 turn late | 22.7% of 2286 [15-32] | 18.5% of 2230 [13-25] | 20.6% of 4516 [14-28] |
| P4 not ready, ready 2 or more turns late | 8.0% of 2286 [4-13] | 9.3% of 2230 [4-15] | 8.7% of 4516 [4-13] |
| P4 the moment came and Kingambit was never ready in the deal | 36.7% of 2286 [24-51] | 42.2% of 2230 [29-55] | 39.4% of 4516 [26-53] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -1.4 points (-2.4 to -0.5); P2.both: -8.7 points (-10.5 to -7.0); P2.g2: -10.4 points (-12.0 to -8.8); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -12.9 points (-15.8 to -10.0); P3.grimer_muk: -20.5 points (-23.0 to -18.0); P4.nomoment: -1.0 points (-1.6 to -0.4).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.4% [81-82, Wilson] | 55.9% [55-57, Wilson] | 68.6% [68-69, Wilson] |
| P2 both Glimmora had their turn | 24.9% [24-26, Wilson] | 9.4% [9-10, Wilson] | 17.1% [17-18, Wilson] |
| P2 the first Glimmora placed had its turn | 77.4% [77-78, Wilson] | 41.3% [40-42, Wilson] | 59.4% [59-60, Wilson] |
| P2 the second Glimmora placed had its turn | 28.8% [28-30, Wilson] | 24.0% [23-25, Wilson] | 26.4% [26-27, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 8.5% [8-9, Wilson] | 11.3% [11-12, Wilson] | 9.9% [10-10, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.6% [31-33, Wilson] | 36.9% [36-38, Wilson] | 34.3% [34-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 17.1% [16-18, Wilson] | 6.4% [6-7, Wilson] | 11.8% [11-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 17.1% [16-18, Wilson] | 6.4% [6-7, Wilson] | 11.8% [11-12, Wilson] |
| P4 not ready, ready 1 turn late | 2.8% [2-3, Wilson] | 1.1% [1-1, Wilson] | 1.9% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 25.1% [24-26, Wilson] | 20.6% [20-21, Wilson] | 22.8% [22-23, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 55.1% [54-56, Wilson] | 71.9% [71-73, Wilson] | 63.5% [63-64, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 19.8% [19-21, Wilson] | 7.5% [7-8, Wilson] | 13.7% [13-14, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 19.8% [19-21, Wilson] | 7.5% [7-8, Wilson] | 13.7% [13-14, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 38.1% of 4488 [37-39, Wilson] | 22.8% of 2810 [21-24, Wilson] | 32.2% of 7298 [31-33, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 38.1% of 4488 [37-39, Wilson] | 22.8% of 2810 [21-24, Wilson] | 32.2% of 7298 [31-33, Wilson] |
| P4 not ready, ready 1 turn late | 6.1% of 4488 [5-7, Wilson] | 3.9% of 2810 [3-5, Wilson] | 5.3% of 7298 [5-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4488 [0-0, Wilson] | 0.0% of 2810 [0-0, Wilson] | 0.0% of 7298 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 55.8% of 4488 [54-57, Wilson] | 73.2% of 2810 [72-75, Wilson] | 62.5% of 7298 [61-64, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.2 points (+0.7 to +1.7); P2.both: -1.2 points (-1.6 to -0.7); P2.g1: +4.4 points (+3.9 to +4.9); P2.g2: -4.3 points (-4.8 to -3.8); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -10.4 points (-11.0 to -9.9); P3.grimer_muk: -21.7 points (-22.4 to -21.1); P4.ko: +1.0 points (+0.7 to +1.4); P4.win: +1.0 points (+0.7 to +1.4); P4.never: +1.6 points (+1.1 to +2.1); P4.nomoment: -3.2 points (-3.7 to -2.7); P5.ko: +1.6 points (+1.2 to +2.0); P5.win: +1.6 points (+1.2 to +2.0).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.6% [89-90, Wilson] | 80.8% [80-82, Wilson] | 85.2% [85-86, Wilson] |
| P2 both Glimmora had their turn | 32.2% [31-33, Wilson] | 25.3% [24-26, Wilson] | 28.8% [28-29, Wilson] |
| P2 the first Glimmora placed had its turn | 87.5% [87-88, Wilson] | 77.4% [77-78, Wilson] | 82.4% [82-83, Wilson] |
| P2 the second Glimmora placed had its turn | 34.3% [33-35, Wilson] | 28.7% [28-30, Wilson] | 31.5% [31-32, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 6.2% [6-7, Wilson] | 9.1% [9-10, Wilson] | 7.7% [7-8, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 24.1% [23-25, Wilson] | 32.3% [31-33, Wilson] | 28.2% [28-29, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 27.8% [27-29, Wilson] | 17.3% [17-18, Wilson] | 22.6% [22-23, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 3.5% [3-4, Wilson] | 3.1% [3-3, Wilson] | 3.3% [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 21.9% [21-23, Wilson] | 25.5% [25-26, Wilson] | 23.7% [23-24, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 46.8% [46-48, Wilson] | 54.1% [53-55, Wilson] | 50.4% [50-51, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 31.4% [30-32, Wilson] | 20.4% [20-21, Wilson] | 25.9% [25-26, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 52.2% of 5322 [51-54, Wilson] | 37.7% of 4590 [36-39, Wilson] | 45.5% of 9912 [45-46, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5322 [0-0, Wilson] | 0.0% of 4590 [0-0, Wilson] | 0.0% of 9912 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 6.7% of 5322 [6-7, Wilson] | 6.7% of 4590 [6-7, Wilson] | 6.7% of 9912 [6-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5322 [0-0, Wilson] | 0.0% of 4590 [0-0, Wilson] | 0.0% of 9912 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 41.1% of 5322 [40-42, Wilson] | 55.6% of 4590 [54-57, Wilson] | 47.8% of 9912 [47-49, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.both: -5.2 points (-5.8 to -4.6); P2.g2: -6.3 points (-6.9 to -5.7); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -16.3 points (-16.9 to -15.7); P3.grimer_muk: -28.6 points (-29.3 to -27.9); P4.never: -1.2 points (-1.7 to -0.7); P5.ko: +1.7 points (+1.3 to +2.2).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.2% [95-96, Wilson] | 89.7% [89-90, Wilson] | 92.5% [92-93, Wilson] |
| P2 both Glimmora had their turn | 53.0% [52-54, Wilson] | 45.1% [44-46, Wilson] | 49.1% [48-50, Wilson] |
| P2 the first Glimmora placed had its turn | 91.9% [91-92, Wilson] | 84.0% [83-85, Wilson] | 87.9% [87-88, Wilson] |
| P2 the second Glimmora placed had its turn | 56.4% [55-57, Wilson] | 50.8% [50-52, Wilson] | 53.6% [53-54, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.4% [1-2, Wilson] | 2.6% [2-3, Wilson] | 2.0% [2-2, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 13.8% [13-14, Wilson] | 18.9% [18-20, Wilson] | 16.3% [16-17, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 50.2% [49-51, Wilson] | 42.7% [42-44, Wilson] | 46.4% [46-47, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 50.2% [49-51, Wilson] | 42.7% [42-44, Wilson] | 46.4% [46-47, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 4.5% [4-5, Wilson] | 2.2% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 9.5% [9-10, Wilson] | 8.6% [8-9, Wilson] | 9.0% [9-9, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 40.4% [39-41, Wilson] | 44.2% [43-45, Wilson] | 42.3% [42-43, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 50.2% [49-51, Wilson] | 47.2% [46-48, Wilson] | 48.7% [48-49, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 50.2% [49-51, Wilson] | 47.2% [46-48, Wilson] | 48.7% [48-49, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 84.1% of 5962 [83-85, Wilson] | 76.5% of 5577 [75-78, Wilson] | 80.4% of 11539 [80-81, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 84.1% of 5962 [83-85, Wilson] | 76.5% of 5577 [75-78, Wilson] | 80.4% of 11539 [80-81, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5962 [0-0, Wilson] | 8.1% of 5577 [7-9, Wilson] | 3.9% of 11539 [4-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5962 [0-0, Wilson] | 0.0% of 5577 [0-0, Wilson] | 0.0% of 11539 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 15.9% of 5962 [15-17, Wilson] | 15.4% of 5577 [14-16, Wilson] | 15.7% of 11539 [15-16, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.both: -13.2 points (-13.9 to -12.5); P2.g1: +2.0 points (+1.7 to +2.4); P2.g2: -15.5 points (-16.2 to -14.8); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -4.7 points (-5.1 to -4.4); P3.grimer_muk: -19.4 points (-20.0 to -18.9); P4.ko: +1.9 points (+1.4 to +2.4); P4.win: +1.9 points (+1.4 to +2.4); P4.never: -4.9 points (-5.3 to -4.6); P4.nomoment: +2.9 points (+2.4 to +3.3); P5.ko: +2.1 points (+1.6 to +2.6); P5.win: +2.1 points (+1.6 to +2.6).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.6% [81-82, Wilson] | 56.0% [55-57, Wilson] | 68.8% [68-69, Wilson] |
| P2 both Glimmora had their turn | 25.3% [24-26, Wilson] | 9.4% [9-10, Wilson] | 17.4% [17-18, Wilson] |
| P2 the first Glimmora placed had its turn | 77.4% [77-78, Wilson] | 41.3% [40-42, Wilson] | 59.4% [59-60, Wilson] |
| P2 the second Glimmora placed had its turn | 29.5% [29-30, Wilson] | 24.1% [23-25, Wilson] | 26.8% [26-27, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 9.4% [9-10, Wilson] | 11.7% [11-12, Wilson] | 10.5% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.6% [31-33, Wilson] | 36.9% [36-38, Wilson] | 34.3% [34-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 6.0% [6-6, Wilson] | 1.8% [2-2, Wilson] | 3.9% [4-4, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.0% [6-6, Wilson] | 1.8% [2-2, Wilson] | 3.9% [4-4, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.3% [3-4, Wilson] | 1.8% [2-2, Wilson] | 2.5% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.8% [90-91, Wilson] | 96.4% [96-97, Wilson] | 93.6% [93-94, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 6.0% [6-6, Wilson] | 1.8% [2-2, Wilson] | 3.9% [4-4, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.0% [6-6, Wilson] | 1.8% [2-2, Wilson] | 3.9% [4-4, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 64.6% of 922 [62-68, Wilson] | 50.7% of 363 [46-56, Wilson] | 60.7% of 1285 [58-63, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 64.6% of 922 [62-68, Wilson] | 50.7% of 363 [46-56, Wilson] | 60.7% of 1285 [58-63, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 922 [0-0, Wilson] | 0.0% of 363 [0-1, Wilson] | 0.0% of 1285 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 922 [0-0, Wilson] | 0.0% of 363 [0-1, Wilson] | 0.0% of 1285 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 35.4% of 922 [32-38, Wilson] | 49.3% of 363 [44-54, Wilson] | 39.3% of 1285 [37-42, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.3 points (+0.8 to +1.8); P2.both: -1.1 points (-1.5 to -0.6); P2.g1: +4.4 points (+3.9 to +4.9); P2.g2: -4.2 points (-4.7 to -3.6); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -11.3 points (-11.9 to -10.7); P3.grimer_muk: -21.7 points (-22.4 to -21.1); P4.ko: +1.7 points (+1.4 to +1.9); P4.win: +1.7 points (+1.4 to +1.9); P4.nomoment: -1.1 points (-1.4 to -0.9); P5.ko: +1.7 points (+1.4 to +1.9); P5.win: +1.7 points (+1.4 to +1.9).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.5% [95-96, Wilson] | 90.1% [89-91, Wilson] | 92.8% [92-93, Wilson] |
| P2 both Glimmora had their turn | 65.1% [64-66, Wilson] | 54.3% [53-55, Wilson] | 59.7% [59-60, Wilson] |
| P2 the first Glimmora placed had its turn | 91.9% [91-92, Wilson] | 84.0% [83-85, Wilson] | 87.9% [87-88, Wilson] |
| P2 the second Glimmora placed had its turn | 68.7% [68-70, Wilson] | 60.4% [59-61, Wilson] | 64.5% [64-65, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.8% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.2% [2-3, Wilson] | 4.1% [4-4, Wilson] | 3.1% [3-3, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 13.9% [13-15, Wilson] | 19.4% [19-20, Wilson] | 16.6% [16-17, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 18.2% [17-19, Wilson] | 16.8% [16-18, Wilson] | 17.5% [17-18, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 18.2% [17-19, Wilson] | 16.8% [16-18, Wilson] | 17.5% [17-18, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.1% [0-0, Wilson] | 0.1% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.4% [2-3, Wilson] | 2.3% [2-3, Wilson] | 2.4% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 79.4% [79-80, Wilson] | 80.8% [80-82, Wilson] | 80.1% [80-81, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 18.2% [17-19, Wilson] | 16.9% [16-18, Wilson] | 17.6% [17-18, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 18.2% [17-19, Wilson] | 16.9% [16-18, Wilson] | 17.6% [17-18, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 88.3% of 2063 [87-90, Wilson] | 87.5% of 1923 [86-89, Wilson] | 87.9% of 3986 [87-89, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 88.3% of 2063 [87-90, Wilson] | 87.5% of 1923 [86-89, Wilson] | 87.9% of 3986 [87-89, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 2063 [0-0, Wilson] | 0.6% of 1923 [0-1, Wilson] | 0.3% of 3986 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 2063 [0-0, Wilson] | 0.0% of 1923 [0-0, Wilson] | 0.0% of 3986 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 11.7% of 2063 [10-13, Wilson] | 11.9% of 1923 [11-13, Wilson] | 11.8% of 3986 [11-13, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.both: -4.6 points (-5.2 to -4.0); P2.g1: +2.0 points (+1.7 to +2.4); P2.g2: -6.6 points (-7.2 to -6.0); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -31.8 points (-32.5 to -31.1); P3.grimer_muk: -30.3 points (-31.0 to -29.7); P4.ko: +11.0 points (+10.5 to +11.4); P4.win: +11.0 points (+10.5 to +11.4); P4.never: -9.3 points (-9.8 to -8.9); P4.nomoment: -1.6 points (-1.8 to -1.3); P5.ko: +10.9 points (+10.5 to +11.4); P5.win: +10.9 points (+10.5 to +11.4).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.5% (27.1-27.9) | 27.0% (26.6-27.4) | 27.3% (27.0-27.6) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 52.1% (51.7-52.5) | 51.6% (51.2-52.1) | 51.9% (51.5-52.2) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 61.9% (61.5-62.4) | 61.5% (61.1-61.9) | 61.7% (61.4-62.0) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 66.3% (65.9-66.7) | 66.0% (65.6-66.4) | 66.1% (65.8-66.4) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 68.5% (68.1-68.9) | 68.1% (67.7-68.5) | 68.3% (68.0-68.6) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 69.4% (69.0-69.8) | 69.0% (68.6-69.4) | 69.2% (68.9-69.5) |
| K2 Kingambit in play, own turn 2 | 10.0% (9.7-10.2) | 10.0% (9.7-10.2) | 10.0% (9.8-10.2) |
| K2 Kingambit in play, own turn 3 | 19.3% (19.0-19.7) | 19.1% (18.8-19.5) | 19.2% (19.0-19.5) |
| K2 Kingambit in play, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| K2 Kingambit in play, own turn 5 | 41.0% (40.5-41.4) | 40.7% (40.3-41.1) | 40.8% (40.5-41.1) |
| K2 Kingambit in play, own turn 6 | 51.7% (51.3-52.1) | 51.1% (50.7-51.5) | 51.4% (51.1-51.7) |
| K6 Muk and Regigigas both in play, own turn 3 | 25.9% (25.5-26.3) | 26.3% (25.9-26.7) | 26.1% (25.8-26.3) |
| K6 Muk and Regigigas both in play, own turn 4 | 33.3% (32.9-33.8) | 33.6% (33.2-34.0) | 33.5% (33.2-33.7) |
| K6 Muk and Regigigas both in play, own turn 5 | 39.1% (38.7-39.5) | 39.1% (38.7-39.6) | 39.1% (38.8-39.4) |
| G3 Pawniard in play, own turn 1 | 52.1% (51.7-52.5) | 51.6% (51.2-52.1) | 51.9% (51.5-52.2) |
| G3 Pawniard in play, own turn 2 | 52.0% (51.5-52.4) | 51.5% (51.1-52.0) | 51.8% (51.4-52.1) |
| G3 Pawniard in play, own turn 3 | 46.9% (46.5-47.4) | 46.9% (46.4-47.3) | 46.9% (46.6-47.2) |
| G3 Pawniard in play, own turn 4 | 38.9% (38.4-39.3) | 38.5% (38.1-38.9) | 38.7% (38.4-39.0) |
| G3 Pawniard in play, own turn 5 | 28.5% (28.1-28.9) | 28.3% (27.9-28.7) | 28.4% (28.1-28.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 10.0% (9.7-10.2) | 10.0% (9.7-10.2) | 10.0% (9.8-10.2) |
| G3 Kingambit in play, own turn 3 | 19.3% (19.0-19.7) | 19.1% (18.8-19.5) | 19.2% (19.0-19.5) |
| G3 Kingambit in play, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| G3 Kingambit in play, own turn 5 | 41.0% (40.5-41.4) | 40.7% (40.3-41.1) | 40.8% (40.5-41.1) |
| G3 Alolan Grimer in play, own turn 1 | 49.8% (49.3-50.2) | 49.9% (49.5-50.3) | 49.8% (49.5-50.2) |
| G3 Alolan Grimer in play, own turn 2 | 38.7% (38.3-39.1) | 39.0% (38.6-39.4) | 38.8% (38.5-39.2) |
| G3 Alolan Grimer in play, own turn 3 | 32.0% (31.6-32.4) | 31.8% (31.4-32.2) | 31.9% (31.6-32.2) |
| G3 Alolan Grimer in play, own turn 4 | 25.6% (25.2-26.0) | 25.6% (25.2-26.0) | 25.6% (25.3-25.9) |
| G3 Alolan Grimer in play, own turn 5 | 20.1% (19.8-20.5) | 20.2% (19.8-20.5) | 20.2% (19.9-20.4) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 18.9% (18.6-19.2) | 19.0% (18.6-19.3) | 18.9% (18.7-19.2) |
| G3 Alolan Muk in play, own turn 3 | 29.1% (28.7-29.5) | 29.5% (29.1-29.9) | 29.3% (29.0-29.6) |
| G3 Alolan Muk in play, own turn 4 | 37.1% (36.6-37.5) | 37.2% (36.8-37.7) | 37.1% (36.8-37.4) |
| G3 Alolan Muk in play, own turn 5 | 43.2% (42.8-43.7) | 43.2% (42.8-43.7) | 43.2% (42.9-43.5) |
| G3 Glimmet in play, own turn 1 | 78.2% (77.9-78.6) | 78.4% (78.0-78.7) | 78.3% (78.0-78.6) |
| G3 Glimmet in play, own turn 2 | 45.1% (44.6-45.5) | 45.0% (44.6-45.4) | 45.0% (44.7-45.3) |
| G3 Glimmet in play, own turn 3 | 32.9% (32.4-33.3) | 32.6% (32.2-33.0) | 32.7% (32.4-33.0) |
| G3 Glimmet in play, own turn 4 | 22.1% (21.8-22.5) | 22.2% (21.9-22.6) | 22.2% (21.9-22.4) |
| G3 Glimmet in play, own turn 5 | 13.4% (13.1-13.7) | 13.4% (13.1-13.7) | 13.4% (13.2-13.6) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 60.1% (59.7-60.6) | 60.0% (59.6-60.4) | 60.1% (59.8-60.4) |
| G3 Glimmora in play, own turn 3 | 75.7% (75.3-76.1) | 75.9% (75.5-76.2) | 75.8% (75.5-76.0) |
| G3 Glimmora in play, own turn 4 | 84.4% (84.1-84.8) | 84.5% (84.1-84.8) | 84.4% (84.2-84.7) |
| G3 Glimmora in play, own turn 5 | 89.1% (88.9-89.4) | 89.4% (89.1-89.6) | 89.2% (89.1-89.4) |
| G3 Regigigas in play, own turn 1 | 78.4% (78.1-78.8) | 78.5% (78.2-78.9) | 78.5% (78.2-78.7) |
| G3 Regigigas in play, own turn 2 | 87.8% (87.6-88.1) | 87.8% (87.6-88.1) | 87.8% (87.6-88.0) |
| G3 Regigigas in play, own turn 3 | 91.6% (91.4-91.9) | 91.6% (91.4-91.9) | 91.6% (91.5-91.8) |
| G3 Regigigas in play, own turn 4 | 93.2% (93.0-93.4) | 93.3% (93.1-93.5) | 93.2% (93.1-93.4) |
| G3 Regigigas in play, own turn 5 | 93.8% (93.6-94.0) | 93.9% (93.7-94.1) | 93.8% (93.7-94.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 73.6% (73.3-74.0) | 73.4% (73.0-73.8) | 73.5% (73.2-73.8) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 88.0% (87.7-88.3) | 88.0% (87.7-88.2) | 88.0% (87.8-88.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 94.6% (94.4-94.8) | 94.5% (94.3-94.7) | 94.5% (94.4-94.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 97.7% (97.6-97.8) | 97.6% (97.5-97.8) | 97.7% (97.6-97.8) |
| G4.s2 a Stage 2 in play, own turn 2 | 10.0% (9.7-10.2) | 10.0% (9.7-10.2) | 10.0% (9.8-10.2) |
| G4.s2 a Stage 2 in play, own turn 3 | 19.3% (19.0-19.7) | 19.1% (18.8-19.5) | 19.2% (19.0-19.5) |
| G4.s2 a Stage 2 in play, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| G4.s2 a Stage 2 in play, own turn 5 | 41.0% (40.5-41.4) | 40.7% (40.3-41.1) | 40.8% (40.5-41.1) |
| G5.any3 an empty own turn among turns 1-3 | 23.4% (23.0-23.8) | 23.0% (22.7-23.4) | 23.2% (23.0-23.5) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.0% (9.7-10.2) | 5.0% (4.8-5.1) |
| G6 Kingambit with [DD] attached, own turn 3 | 16.9% (16.6-17.3) | 19.1% (18.8-19.5) | 18.0% (17.8-18.3) |
| G6 Kingambit with [DD] attached, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| G6 Kingambit with [DD] attached, own turn 5 | 41.0% (40.5-41.4) | 40.7% (40.3-41.1) | 40.8% (40.5-41.1) |
| G5 mean empty own turns in turns 1-5 | 0.761 | 0.758 | 0.759 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.7% / 10.1% [1-2] | 0.9% / 5.0% [1-1] |
| K3.by3 | 2.5% / 11.1% [2-3] | 2.2% / 10.6% [1-3] | 2.3% / 10.8% [1-3] |
| K3.by4 | 2.9% / 11.5% [2-4] | 3.8% / 12.1% [3-5] | 3.3% / 11.8% [2-4] |
| K3.by5 | 4.6% / 13.3% [3-7] | 4.3% / 20.3% [3-6] | 4.4% / 16.8% [3-6] |
| K3.by6 | 4.8% / 21.7% [3-7] | 8.9% / 33.0% [4-16] | 6.9% / 27.4% [4-10] |
| K3.by7 | 11.8% / 36.7% [4-22] | 9.1% / 56.1% [4-16] | 10.4% / 46.4% [4-19] |
| K3.by8 | 11.9% / 60.2% [4-22] | 9.1% / 62.1% [4-16] | 10.5% / 61.2% [4-19] |
| K3.never | 39.8% / 88.1% [16-64] | 37.9% / 90.9% [16-61] | 38.8% / 89.5% [16-63] |
| K3.k0 | 3.1% / 51.5% [2-4] | 2.5% / 55.5% [1-3] | 2.8% / 53.5% [2-4] |
| K3.k1 | 0.0% / 48.4% [0-0] | 0.0% / 53.1% [0-0] | 0.0% / 50.7% [0-0] |
| K3.k2 | 6.6% / 54.9% [0-16] | 5.3% / 58.4% [1-12] | 5.9% / 56.6% [1-14] |
| K3.k3p | 2.2% / 50.5% [0-7] | 1.3% / 54.4% [0-4] | 1.7% / 52.5% [0-5] |
| K4 | 8.8% / 58.9% [1-19] | 6.6% / 61.0% [1-14] | 7.7% / 59.9% [1-17] |
| K5 | 4.8% / 61.2% [4-6] | 5.9% / 59.4% [4-8] | 5.3% / 60.3% [4-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by4: -1.3 points (-1.7 to -0.9); K3.by5: -1.7 points (-2.0 to -1.2); K3.by6: -1.9 points (-2.4 to -1.5); K3.by7: -2.8 points (-4.8 to -1.5); K3.by8: -4.2 points (-9.0 to -1.5); K3.k0: -1.1 points (-1.7 to -0.6); K4: -3.1 points (-7.7 to -0.5); K5: -2.8 points (-3.6 to -2.0).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [2-3] | 1.2% [0-2] |
| K3.by3 | 2.2% / 13.5% [1-3] | 3.0% [2-4] | 2.6% / 8.3% [2-3] |
| K3.by4 | 2.6% / 13.9% [1-4] | 3.9% [3-5] | 3.2% / 8.9% [2-4] |
| K3.by5 | 4.3% / 15.6% [3-6] | 4.2% / 34.5% [4-5] | 4.3% / 25.1% [3-5] |
| K3.by6 | 4.5% / 15.8% [3-7] | 4.5% / 34.8% [4-5] | 4.5% / 25.3% [3-6] |
| K3.by7 | 14.6% / 36.9% [4-29] | 5.0% / 67.2% [4-7] | 9.8% / 52.1% [4-19] |
| K3.by8 | 14.6% / 57.8% [4-29] | 5.0% / 84.2% [4-7] | 9.8% / 71.0% [4-19] |
| K3.never | 42.2% / 85.4% [15-71] | 15.8% / 95.0% [0-42] | 29.0% / 90.2% [12-52] |
| K3.k0 | 2.8% / 46.0% [1-4] | 3.3% / 82.5% [2-5] | 3.1% / 64.2% [2-4] |
| K3.k1 | 0.0% / 43.2% [0-0] | 0.0% / 79.1% [0-0] | 0.0% / 61.2% [0-0] |
| K3.k2 | 8.2% / 51.4% [0-21] | 1.1% / 80.3% [0-2] | 4.7% / 65.8% [1-13] |
| K3.k3p | 3.5% / 46.7% [0-11] | 0.6% / 79.7% [0-2] | 2.0% / 63.2% [0-7] |
| K4 | 11.7% / 56.3% [0-26] | 1.7% / 83.6% [0-4] | 6.7% / 69.9% [1-16] |
| K5 | 4.9% / 53.4% [3-6] | 5.5% / 84.3% [3-7] | 5.2% / 68.8% [4-6] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.0 points (-1.4 to -0.7); K3.by4: -1.5 points (-1.9 to -1.0); K3.by5: -2.1 points (-2.4 to -1.7); K3.by6: -2.4 points (-3.0 to -1.8); K3.by7: -5.7 points (-12.6 to -1.8); K3.by8: -5.7 points (-12.6 to -1.7); K3.k0: -1.4 points (-1.9 to -0.9); K3.k2: -1.0 points (-1.7 to -0.3); K4: -4.4 points (-11.5 to -0.3); K5: -2.8 points (-3.4 to -2.1).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.0% [2-2] | 1.0% [1-1] |
| K3.by3 | 2.5% [2-3] | 2.5% [2-3] | 2.5% [2-3] |
| K3.by4 | 3.1% [3-4] | 3.5% [3-4] | 3.3% [3-4] |
| K3.by5 | 4.0% [3-5] | 5.0% [4-6] | 4.5% [4-5] |
| K3.by6 | 5.2% [4-6] | 6.0% / 10.0% [5-7] | 5.6% / 7.6% [5-7] |
| K3.by7 | 6.4% / 10.9% [5-8] | 6.8% / 16.9% [5-9] | 6.6% / 13.9% [5-8] |
| K3.by8 | 7.1% / 18.3% [5-9] | 7.3% / 19.3% [6-9] | 7.2% / 18.8% [6-9] |
| K3.never | 81.7% / 92.9% [73-89] | 80.7% / 92.7% [73-87] | 81.2% / 92.8% [73-88] |
| K3.k0 | 3.3% / 14.5% [3-4] | 2.7% / 14.7% [2-3] | 3.0% / 14.6% [3-4] |
| K3.k1 | 0.0% / 11.2% [0-0] | 0.0% / 12.0% [0-0] | 0.0% / 11.6% [0-0] |
| K3.k2 | 1.7% / 12.9% [1-3] | 2.2% / 14.2% [1-3] | 1.9% / 13.5% [1-3] |
| K3.k3p | 2.1% / 13.3% [1-4] | 2.4% / 14.3% [1-4] | 2.2% / 13.8% [1-4] |
| K4 | 3.8% / 15.5% [2-6] | 4.6% / 17.1% [3-7] | 4.2% / 16.3% [2-6] |
| K5 | 5.4% / 19.3% [5-6] | 6.5% / 18.9% [6-7] | 6.0% / 19.1% [5-6] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by4: -1.3 points (-1.5 to -1.1); K3.by5: -2.0 points (-2.3 to -1.7); K3.by6: -3.1 points (-3.7 to -2.5); K3.by7: -4.2 points (-5.5 to -3.1); K3.by8: -5.1 points (-7.3 to -3.5); K3.never: +4.2 points (+2.4 to +6.1); K3.k0: -1.1 points (-1.4 to -0.9); K3.k2: -1.4 points (-1.8 to -1.1); K3.k3p: -2.6 points (-4.6 to -1.0); K4: -4.0 points (-5.9 to -2.4); K5: -3.6 points (-4.1 to -3.2).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by4 | 1.4% [1-2, Wilson] | 4.2% [4-5, Wilson] | 2.8% [3-3, Wilson] |
| K3.by5 | 6.8% [6-7, Wilson] | 5.2% [5-6, Wilson] | 6.0% [6-6, Wilson] |
| K3.by6 | 10.5% [10-11, Wilson] | 5.2% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K3.by7 | 10.5% [10-11, Wilson] | 5.2% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K3.by8 | 10.5% [10-11, Wilson] | 5.2% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K3.never | 89.5% [89-90, Wilson] | 94.8% [94-95, Wilson] | 92.1% [92-92, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-2, Wilson] | 1.9% [2-2, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 9.1% [9-10, Wilson] | 3.4% [3-4, Wilson] | 6.2% [6-7, Wilson] |
| K4 | 10.5% [10-11, Wilson] | 5.2% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K5 | 10.1% [9-11, Wilson] | 15.3% [15-16, Wilson] | 12.7% [12-13, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.2 points (-1.5 to -0.9); K3.by5: -3.4 points (-3.8 to -3.1); K3.by6: -3.3 points (-3.7 to -2.9); K3.by7: -3.3 points (-3.7 to -2.9); K3.by8: -3.3 points (-3.7 to -2.9); K3.never: +3.3 points (+2.9 to +3.7); K3.k3p: -2.6 points (-2.9 to -2.2); K4: -3.3 points (-3.7 to -2.9); K5: -9.1 points (-9.5 to -8.6).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.by4 | 3.1% [3-3, Wilson] | 3.6% [3-4, Wilson] | 3.4% [3-4, Wilson] |
| K3.by5 | 4.0% [4-4, Wilson] | 9.1% [9-10, Wilson] | 6.5% [6-7, Wilson] |
| K3.by6 | 10.4% [10-11, Wilson] | 13.1% [12-14, Wilson] | 11.7% [11-12, Wilson] |
| K3.by7 | 18.5% [18-19, Wilson] | 13.1% [12-14, Wilson] | 15.8% [15-16, Wilson] |
| K3.by8 | 18.5% [18-19, Wilson] | 13.1% [12-14, Wilson] | 15.8% [15-16, Wilson] |
| K3.never | 81.5% [81-82, Wilson] | 86.9% [86-88, Wilson] | 84.2% [84-85, Wilson] |
| K3.k0 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.9% [1-1, Wilson] | 1.3% [1-2, Wilson] | 1.1% [1-1, Wilson] |
| K3.k3p | 14.5% [14-15, Wilson] | 9.4% [9-10, Wilson] | 12.0% [12-12, Wilson] |
| K4 | 15.4% [15-16, Wilson] | 10.8% [10-11, Wilson] | 13.1% [13-14, Wilson] |
| K5 | 7.0% [6-7, Wilson] | 10.1% [10-11, Wilson] | 8.5% [8-9, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.0 points (-1.2 to -0.9); K3.by4: -1.7 points (-2.0 to -1.5); K3.by5: -4.5 points (-4.9 to -4.1); K3.by6: -10.4 points (-10.9 to -9.9); K3.by7: -8.9 points (-9.4 to -8.4); K3.by8: -8.9 points (-9.4 to -8.4); K3.never: +8.9 points (+8.4 to +9.4); K3.k0: -1.0 points (-1.2 to -0.9); K3.k2: -1.1 points (-1.3 to -0.9); K3.k3p: -6.8 points (-7.3 to -6.3); K4: -7.9 points (-8.4 to -7.4); K5: -7.7 points (-8.2 to -7.3).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.by4 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.by5 | 3.1% [3-3, Wilson] | 4.3% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| K3.by6 | 4.3% [4-5, Wilson] | 4.4% [4-5, Wilson] | 4.3% [4-5, Wilson] |
| K3.by7 | 4.3% [4-5, Wilson] | 35.8% [35-37, Wilson] | 20.1% [20-21, Wilson] |
| K3.by8 | 44.9% [44-46, Wilson] | 35.9% [35-37, Wilson] | 40.4% [40-41, Wilson] |
| K3.never | 55.1% [54-56, Wilson] | 64.2% [63-65, Wilson] | 59.6% [59-60, Wilson] |
| K3.k0 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.2% [1-1, Wilson] | 2.1% [2-2, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 40.6% [40-42, Wilson] | 31.5% [31-32, Wilson] | 36.0% [35-37, Wilson] |
| K4 | 41.9% [41-43, Wilson] | 33.5% [33-34, Wilson] | 37.7% [37-38, Wilson] |
| K5 | 5.8% [5-6, Wilson] | 6.7% [6-7, Wilson] | 6.2% [6-7, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.0 points (-1.2 to -0.9); K3.by4: -1.0 points (-1.2 to -0.9); K3.by5: -2.5 points (-2.8 to -2.2); K3.by6: -3.8 points (-4.1 to -3.5); K3.by7: -4.3 points (-4.8 to -3.9); K3.by8: -5.7 points (-6.3 to -5.1); K3.never: +5.7 points (+5.1 to +6.3); K3.k0: -1.0 points (-1.2 to -0.9); K3.k2: -2.8 points (-3.1 to -2.6); K3.k3p: -1.8 points (-2.4 to -1.3); K4: -4.7 points (-5.2 to -4.1); K5: -3.7 points (-4.0 to -3.4).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by4 | 1.4% [1-2, Wilson] | 3.7% [3-4, Wilson] | 2.5% [2-3, Wilson] |
| K3.by5 | 4.5% [4-5, Wilson] | 4.8% [4-5, Wilson] | 4.6% [4-5, Wilson] |
| K3.by6 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.by7 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.by8 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.never | 91.4% [91-92, Wilson] | 95.2% [95-96, Wilson] | 93.3% [93-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-2, Wilson] | 1.9% [2-2, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 7.2% [7-8, Wilson] | 3.0% [3-3, Wilson] | 5.1% [5-5, Wilson] |
| K4 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K5 | 10.1% [9-11, Wilson] | 15.3% [15-16, Wilson] | 12.7% [12-13, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.4 points (-1.6 to -1.1); K3.by5: -4.3 points (-4.7 to -3.9); K3.by6: -4.1 points (-4.5 to -3.6); K3.by7: -4.1 points (-4.5 to -3.6); K3.by8: -4.1 points (-4.5 to -3.6); K3.never: +4.1 points (+3.6 to +4.5); K3.k3p: -3.3 points (-3.7 to -3.0); K4: -4.1 points (-4.5 to -3.6); K5: -9.1 points (-9.5 to -8.6).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.by4 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.by5 | 3.1% [3-3, Wilson] | 4.3% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| K3.by6 | 4.3% [4-5, Wilson] | 4.4% [4-5, Wilson] | 4.3% [4-5, Wilson] |
| K3.by7 | 4.3% [4-5, Wilson] | 5.9% [5-6, Wilson] | 5.1% [5-5, Wilson] |
| K3.by8 | 5.1% [5-6, Wilson] | 5.9% [5-6, Wilson] | 5.5% [5-6, Wilson] |
| K3.by9 | 5.1% [5-6, Wilson] | 22.1% [21-23, Wilson] | 13.6% [13-14, Wilson] |
| K3.by10 | 23.2% [22-24, Wilson] | 22.1% [21-23, Wilson] | 22.7% [22-23, Wilson] |
| K3.never | 76.8% [76-78, Wilson] | 77.9% [77-79, Wilson] | 77.3% [77-78, Wilson] |
| K3.k0 | 3.1% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.2% [1-1, Wilson] | 2.1% [2-2, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 18.9% [18-20, Wilson] | 17.7% [17-19, Wilson] | 18.3% [18-19, Wilson] |
| K4 | 20.1% [19-21, Wilson] | 19.8% [19-21, Wilson] | 20.0% [19-21, Wilson] |
| K5 | 5.9% [5-6, Wilson] | 6.7% [6-7, Wilson] | 6.3% [6-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.0 points (-1.2 to -0.9); K3.by4: -1.0 points (-1.2 to -0.9); K3.by5: -2.5 points (-2.8 to -2.2); K3.by6: -3.8 points (-4.1 to -3.5); K3.by7: -15.0 points (-15.5 to -14.4); K3.by8: -31.6 points (-32.2 to -30.9); K3.by9: -27.1 points (-27.8 to -26.4); K3.by10: -21.1 points (-21.8 to -20.5); K3.never: +21.1 points (+20.5 to +21.8); K3.k0: -1.0 points (-1.2 to -0.9); K3.k2: -2.8 points (-3.1 to -2.6); K3.k3p: -17.3 points (-17.9 to -16.6); K4: -20.1 points (-20.7 to -19.5); K5: -3.8 points (-4.1 to -3.5).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.2 (+19.8 to +20.6) FLAG | +20.2 (+19.9 to +20.6) FLAG | +20.2 (+19.9 to +20.5) FLAG |
| K1 Pawniard in play at setup | -1.7 (-1.8 to -1.5) FLAG | -1.8 (-1.9 to -1.6) FLAG | -1.7 (-1.8 to -1.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -3.9 (-4.1 to -3.6) FLAG | -4.0 (-4.3 to -3.7) FLAG | -3.9 (-4.1 to -3.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -6.0 (-6.3 to -5.7) FLAG | -6.3 (-6.6 to -6.0) FLAG | -6.2 (-6.4 to -5.9) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -8.2 (-8.6 to -7.9) FLAG | -8.5 (-8.9 to -8.2) FLAG | -8.4 (-8.6 to -8.2) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -10.1 (-10.4 to -9.7) FLAG | -10.5 (-10.9 to -10.2) FLAG | -10.3 (-10.5 to -10.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -11.4 (-11.7 to -11.0) FLAG | -11.8 (-12.1 to -11.5) FLAG | -11.6 (-11.8 to -11.3) FLAG |
| K2 Kingambit in play, own turn 3 | -1.7 (-2.0 to -1.5) FLAG | -2.0 (-2.2 to -1.8) FLAG | -1.9 (-2.0 to -1.7) FLAG |
| K2 Kingambit in play, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.6 (-3.8 to -3.3) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| K2 Kingambit in play, own turn 5 | -5.5 (-5.8 to -5.1) FLAG | -5.7 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.4) FLAG |
| K2 Kingambit in play, own turn 6 | -7.7 (-8.1 to -7.4) FLAG | -8.0 (-8.4 to -7.7) FLAG | -7.9 (-8.1 to -7.6) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +3.7 (+3.4 to +4.0) FLAG | +4.0 (+3.7 to +4.4) FLAG | +3.9 (+3.6 to +4.1) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +3.0 (+2.6 to +3.3) FLAG | +3.1 (+2.7 to +3.4) FLAG | +3.0 (+2.7 to +3.3) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.2 (+1.8 to +2.6) FLAG | +2.1 (+1.7 to +2.6) FLAG | +2.2 (+1.9 to +2.4) FLAG |
| G3 Pawniard in play, own turn 1 | -3.9 (-4.1 to -3.6) FLAG | -4.0 (-4.3 to -3.7) FLAG | -3.9 (-4.1 to -3.7) FLAG |
| G3 Pawniard in play, own turn 2 | -5.3 (-5.6 to -4.9) FLAG | -5.5 (-5.8 to -5.2) FLAG | -5.4 (-5.6 to -5.2) FLAG |
| G3 Pawniard in play, own turn 3 | -6.5 (-6.8 to -6.2) FLAG | -6.5 (-6.9 to -6.2) FLAG | -6.5 (-6.8 to -6.3) FLAG |
| G3 Pawniard in play, own turn 4 | -6.7 (-7.1 to -6.4) FLAG | -7.0 (-7.3 to -6.6) FLAG | -6.9 (-7.1 to -6.6) FLAG |
| G3 Pawniard in play, own turn 5 | -5.9 (-6.2 to -5.6) FLAG | -6.1 (-6.4 to -5.7) FLAG | -6.0 (-6.2 to -5.8) FLAG |
| G3 Kingambit in play, own turn 3 | -1.7 (-2.0 to -1.5) FLAG | -2.0 (-2.2 to -1.8) FLAG | -1.9 (-2.0 to -1.7) FLAG |
| G3 Kingambit in play, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.6 (-3.8 to -3.3) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G3 Kingambit in play, own turn 5 | -5.5 (-5.8 to -5.1) FLAG | -5.7 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.4) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -4.8 (-5.1 to -4.5) FLAG | -4.8 (-5.1 to -4.5) FLAG | -4.8 (-5.0 to -4.6) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -7.5 (-7.9 to -7.2) FLAG | -7.6 (-7.9 to -7.3) FLAG | -7.6 (-7.8 to -7.3) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -7.9 (-8.2 to -7.6) FLAG | -8.2 (-8.6 to -7.9) FLAG | -8.1 (-8.3 to -7.8) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -7.4 (-7.7 to -7.1) FLAG | -7.6 (-7.9 to -7.3) FLAG | -7.5 (-7.7 to -7.3) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -6.6 (-6.9 to -6.3) FLAG | -6.9 (-7.1 to -6.6) FLAG | -6.7 (-6.9 to -6.5) FLAG |
| G3 Alolan Muk in play, own turn 3 | -1.9 (-2.2 to -1.6) FLAG | -1.8 (-2.2 to -1.5) FLAG | -1.9 (-2.1 to -1.7) FLAG |
| G3 Alolan Muk in play, own turn 4 | -4.1 (-4.5 to -3.8) FLAG | -4.1 (-4.5 to -3.8) FLAG | -4.1 (-4.4 to -3.9) FLAG |
| G3 Alolan Muk in play, own turn 5 | -6.0 (-6.4 to -5.7) FLAG | -6.0 (-6.4 to -5.6) FLAG | -6.0 (-6.3 to -5.7) FLAG |
| G3 Glimmet in play, own turn 1 | -3.9 (-4.1 to -3.6) FLAG | -4.0 (-4.3 to -3.8) FLAG | -4.0 (-4.1 to -3.8) FLAG |
| G3 Glimmet in play, own turn 2 | -7.7 (-8.1 to -7.4) FLAG | -7.4 (-7.8 to -7.1) FLAG | -7.6 (-7.8 to -7.3) FLAG |
| G3 Glimmet in play, own turn 3 | -9.3 (-9.7 to -9.0) FLAG | -9.3 (-9.7 to -9.0) FLAG | -9.3 (-9.6 to -9.1) FLAG |
| G3 Glimmet in play, own turn 4 | -8.8 (-9.1 to -8.5) FLAG | -8.7 (-9.0 to -8.3) FLAG | -8.7 (-9.0 to -8.5) FLAG |
| G3 Glimmet in play, own turn 5 | -6.7 (-7.0 to -6.5) FLAG | -6.4 (-6.7 to -6.1) FLAG | -6.6 (-6.8 to -6.4) FLAG |
| G3 Glimmora in play, own turn 2 | -3.0 (-3.3 to -2.8) FLAG | -3.3 (-3.6 to -3.1) FLAG | -3.2 (-3.4 to -3.0) FLAG |
| G3 Glimmora in play, own turn 3 | -4.0 (-4.3 to -3.7) FLAG | -4.1 (-4.3 to -3.8) FLAG | -4.0 (-4.2 to -3.8) FLAG |
| G3 Glimmora in play, own turn 4 | -5.0 (-5.2 to -4.7) FLAG | -5.0 (-5.2 to -4.7) FLAG | -5.0 (-5.2 to -4.8) FLAG |
| G3 Glimmora in play, own turn 5 | -5.9 (-6.2 to -5.7) FLAG | -5.8 (-6.0 to -5.6) FLAG | -5.9 (-6.0 to -5.7) FLAG |
| G3 Regigigas in play, own turn 1 | +23.1 (+22.7 to +23.5) FLAG | +23.3 (+22.9 to +23.7) FLAG | +23.2 (+22.9 to +23.5) FLAG |
| G3 Regigigas in play, own turn 2 | +20.2 (+19.8 to +20.6) FLAG | +20.7 (+20.4 to +21.1) FLAG | +20.5 (+20.2 to +20.7) FLAG |
| G3 Regigigas in play, own turn 3 | +17.2 (+16.8 to +17.5) FLAG | +17.5 (+17.1 to +17.8) FLAG | +17.3 (+17.1 to +17.6) FLAG |
| G3 Regigigas in play, own turn 4 | +15.0 (+14.6 to +15.3) FLAG | +15.1 (+14.8 to +15.5) FLAG | +15.1 (+14.8 to +15.3) FLAG |
| G3 Regigigas in play, own turn 5 | +13.5 (+13.2 to +13.9) FLAG | +13.7 (+13.4 to +14.0) FLAG | +13.6 (+13.4 to +13.8) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -1.9 (-2.1 to -1.6) FLAG | -2.3 (-2.5 to -2.0) FLAG | -2.1 (-2.3 to -1.9) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -1.6 (-1.8 to -1.4) FLAG | -1.8 (-2.0 to -1.6) FLAG | -1.7 (-1.9 to -1.6) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -1.3 (-1.5 to -1.2) FLAG | -1.4 (-1.6 to -1.2) FLAG | -1.4 (-1.5 to -1.3) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -1.7 (-2.0 to -1.5) FLAG | -2.0 (-2.2 to -1.8) FLAG | -1.9 (-2.0 to -1.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.6 (-3.8 to -3.3) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -5.5 (-5.8 to -5.1) FLAG | -5.7 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -0.6 (-0.8 to -0.4) | -2.0 (-2.2 to -1.8) FLAG | -1.3 (-1.5 to -1.1) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.6 (-3.8 to -3.3) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -5.5 (-5.8 to -5.1) FLAG | -5.7 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.4) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.001 (-0.003 to +0.005) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Ilima A3 149 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.2 points
- C-his (per-game bootstrap): P2 both Glimmora had their turn -8.5 points (-11.8 to -5.4); P2 the second Glimmora placed had its turn -10.1 points (-13.3 to -7.0); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.2 points (-9.0 to -1.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -13.4 points (-17.4 to -9.7); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.7 points (-3.1 to -0.6)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -1.3 points (-2.6 to -0.6); P2 both Glimmora had their turn -7.9 points (-11.5 to -5.0); P2 the second Glimmora placed had its turn -9.0 points (-12.6 to -6.1); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -5.6 points (-13.0 to -0.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.0 points (-18.6 to -9.1)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -1.4 points (-2.4 to -0.5); P2 both Glimmora had their turn -8.7 points (-10.5 to -7.0); P2 the second Glimmora placed had its turn -10.4 points (-12.0 to -8.8); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -12.9 points (-15.8 to -10.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -20.5 points (-23.0 to -18.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.0 points (-1.6 to -0.4)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn +1.2 points (+0.7 to +1.7); P2 both Glimmora had their turn -1.2 points (-1.6 to -0.7); P2 the first Glimmora placed had its turn +4.4 points (+3.9 to +4.9); P2 the second Glimmora placed had its turn -4.3 points (-4.8 to -3.8); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -10.4 points (-11.0 to -9.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -21.7 points (-22.4 to -21.1); P4 ready at the winning moment: Knocks out their strongest +1.0 points (+0.7 to +1.4); P4 ready at the winning moment: Wins outright (a lower bound) +1.0 points (+0.7 to +1.4); P4 the moment came and Kingambit was never ready in the deal +1.6 points (+1.1 to +2.1); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -3.2 points (-3.7 to -2.7); P5 plan reached in time: Knocks out their strongest +1.6 points (+1.2 to +2.0); P5 plan reached in time: Wins outright (a lower bound) +1.6 points (+1.2 to +2.0)
- C-fixed medium (paired test): P2 both Glimmora had their turn -5.2 points (-5.8 to -4.6); P2 the second Glimmora placed had its turn -6.3 points (-6.9 to -5.7); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -16.3 points (-16.9 to -15.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -28.6 points (-29.3 to -27.9); P4 the moment came and Kingambit was never ready in the deal -1.2 points (-1.7 to -0.7); P5 plan reached in time: Knocks out their strongest +1.7 points (+1.3 to +2.2)
- C-fixed slow (paired test): P2 both Glimmora had their turn -13.2 points (-13.9 to -12.5); P2 the first Glimmora placed had its turn +2.0 points (+1.7 to +2.4); P2 the second Glimmora placed had its turn -15.5 points (-16.2 to -14.8); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.7 points (-5.1 to -4.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -19.4 points (-20.0 to -18.9); P4 ready at the winning moment: Knocks out their strongest +1.9 points (+1.4 to +2.4); P4 ready at the winning moment: Wins outright (a lower bound) +1.9 points (+1.4 to +2.4); P4 the moment came and Kingambit was never ready in the deal -4.9 points (-5.3 to -4.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +2.9 points (+2.4 to +3.3); P5 plan reached in time: Knocks out their strongest +2.1 points (+1.6 to +2.6); P5 plan reached in time: Wins outright (a lower bound) +2.1 points (+1.6 to +2.6)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +1.3 points (+0.8 to +1.8); P2 both Glimmora had their turn -1.1 points (-1.5 to -0.6); P2 the first Glimmora placed had its turn +4.4 points (+3.9 to +4.9); P2 the second Glimmora placed had its turn -4.2 points (-4.7 to -3.6); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -11.3 points (-11.9 to -10.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -21.7 points (-22.4 to -21.1); P4 ready at the winning moment: Knocks out their strongest +1.7 points (+1.4 to +1.9); P4 ready at the winning moment: Wins outright (a lower bound) +1.7 points (+1.4 to +1.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.1 points (-1.4 to -0.9); P5 plan reached in time: Knocks out their strongest +1.7 points (+1.4 to +1.9); P5 plan reached in time: Wins outright (a lower bound) +1.7 points (+1.4 to +1.9)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 both Glimmora had their turn -4.6 points (-5.2 to -4.0); P2 the first Glimmora placed had its turn +2.0 points (+1.7 to +2.4); P2 the second Glimmora placed had its turn -6.6 points (-7.2 to -6.0); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -31.8 points (-32.5 to -31.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -30.3 points (-31.0 to -29.7); P4 ready at the winning moment: Knocks out their strongest +11.0 points (+10.5 to +11.4); P4 ready at the winning moment: Wins outright (a lower bound) +11.0 points (+10.5 to +11.4); P4 the moment came and Kingambit was never ready in the deal -9.3 points (-9.8 to -8.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.6 points (-1.8 to -1.3); P5 plan reached in time: Knocks out their strongest +10.9 points (+10.5 to +11.4); P5 plan reached in time: Wins outright (a lower bound) +10.9 points (+10.5 to +11.4)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K6 Muk and Regigigas both in play, own turn 3 +3.9 points; K6 Muk and Regigigas both in play, own turn 4 +3.0 points; K6 Muk and Regigigas both in play, own turn 5 +2.2 points; G3 Regigigas in play, own turn 1 +23.2 points; G3 Regigigas in play, own turn 2 +20.5 points; G3 Regigigas in play, own turn 3 +17.3 points; G3 Regigigas in play, own turn 4 +15.1 points; G3 Regigigas in play, own turn 5 +13.6 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.7 points; K1 Pawniard line in play (end of own turn t), own turn 1 -3.9 points; K1 Pawniard line in play (end of own turn t), own turn 2 -6.2 points; K1 Pawniard line in play (end of own turn t), own turn 3 -8.4 points; K1 Pawniard line in play (end of own turn t), own turn 4 -10.3 points; K1 Pawniard line in play (end of own turn t), own turn 5 -11.6 points; K2 Kingambit in play, own turn 3 -1.9 points; K2 Kingambit in play, own turn 4 -3.5 points; K2 Kingambit in play, own turn 5 -5.6 points; K2 Kingambit in play, own turn 6 -7.9 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by4 -1.3; K3.by5 -1.7; K3.by6 -1.9; K3.by7 -2.8; K3.by8 -4.2; K3.k0 -1.1; K4 -3.1; K5 -2.8; C-his, seat-matched: K3.by3 -1.0; K3.by4 -1.5; K3.by5 -2.1; K3.by6 -2.4; K3.by7 -5.7; K3.by8 -5.7; K3.k0 -1.4; K3.k2 -1.0; K4 -4.4; K5 -2.8; C-bot: K3.by4 -1.3; K3.by5 -2.0; K3.by6 -3.1; K3.by7 -4.2; K3.by8 -5.1; K3.never +4.2; K3.k0 -1.1; K3.k2 -1.4; K3.k3p -2.6; K4 -4.0; K5 -3.6; C-fixed fast: K3.by4 -1.2; K3.by5 -3.4; K3.by6 -3.3; K3.by7 -3.3; K3.by8 -3.3; K3.never +3.3; K3.k3p -2.6; K4 -3.3; K5 -9.1; C-fixed medium: K3.by3 -1.0; K3.by4 -1.7; K3.by5 -4.5; K3.by6 -10.4; K3.by7 -8.9; K3.by8 -8.9; K3.never +8.9; K3.k0 -1.0; K3.k2 -1.1; K3.k3p -6.8; K4 -7.9; K5 -7.7; C-fixed slow: K3.by3 -1.0; K3.by4 -1.0; K3.by5 -2.5; K3.by6 -3.8; K3.by7 -4.3; K3.by8 -5.7; K3.never +5.7; K3.k0 -1.0; K3.k2 -2.8; K3.k3p -1.8; K4 -4.7; K5 -3.7; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.4; K3.by5 -4.3; K3.by6 -4.1; K3.by7 -4.1; K3.by8 -4.1; K3.never +4.1; K3.k3p -3.3; K4 -4.1; K5 -9.1; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.0; K3.by4 -1.0; K3.by5 -2.5; K3.by6 -3.8; K3.by7 -15.0; K3.by8 -31.6; K3.by9 -27.1; K3.by10 -21.1; K3.never +21.1; K3.k0 -1.0; K3.k2 -2.8; K3.k3p -17.3; K4 -20.1; K5 -3.8.
Not valued here (changed cards the script never plays: they count as blanks): Ilima.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Professor's Research A4b 373 +1 Regigigas B3 134 (card-list id baab9147364c)

Changes: ["-1 Professor's Research A4b 373", '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 236,952; the valuation and the fallback rule disagree at 106,515 of 236,952 Copycat decisions (45.0%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 48.8% (48.4-49.3) | 48.8% (48.3-49.2) | 48.8% (48.5-49.1) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.5% / 93.8% [71-91] | 73.5% / 88.7% [59-85] | 78.0% / 91.3% [65-88] |
| P2 both Glimmora had their turn | 23.8% / 63.5% [17-31] | 20.3% / 64.0% [13-29] | 22.1% / 63.7% [16-29] |
| P2 the first Glimmora placed had its turn | 79.3% / 88.2% [68-88] | 67.7% / 79.2% [53-81] | 73.5% / 83.7% [60-84] |
| P2 the second Glimmora placed had its turn | 27.1% / 63.1% [19-35] | 26.1% / 63.8% [18-35] | 26.6% / 63.4% [19-34] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10] | 8.5% [8-9] | 8.8% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.0% / 49.7% [1-3] | 3.7% / 55.0% [2-6] | 2.9% / 52.4% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.5% / 59.3% [14-21] | 22.0% / 64.7% [18-27] | 19.7% / 62.0% [16-24] |
| P4 ready at the winning moment: Knocks out their strongest | 10.2% / 35.6% [2-20] | 7.0% / 34.7% [2-13] | 8.6% / 35.2% [2-16] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.9% / 27.4% [0-6] | 1.3% / 29.0% [0-4] | 1.6% / 28.2% [0-5] |
| P4 not ready, ready 1 turn late | 3.6% / 47.1% [0-9] | 2.9% / 50.2% [0-7] | 3.3% / 48.7% [0-8] |
| P4 not ready, ready 2 or more turns late | 1.5% / 45.0% [0-4] | 1.4% / 48.7% [0-4] | 1.4% / 46.9% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 10.8% / 54.4% [0-25] | 10.8% / 58.0% [0-27] | 10.8% / 56.2% [0-26] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.4% / 55.9% [9-55] | 30.6% / 58.3% [11-54] | 30.5% / 57.1% [10-54] |
| P5 plan reached in time: Knocks out their strongest | 15.2% / 58.8% [5-28] | 11.4% / 58.6% [4-20] | 13.3% / 58.7% [4-24] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.4% / 45.9% [0-7] | 1.7% / 48.9% [0-5] | 2.0% / 47.4% [0-6] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 39.0% of 2608 [22-57] | 31.6% of 2214 [18-52] | 35.6% of 4822 [20-54] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 7.4% of 2608 [0-31] | 5.7% of 2214 [0-31] | 6.6% of 4822 [0-31] |
| P4 not ready, ready 1 turn late | 13.9% of 2608 [0-49] | 13.2% of 2214 [0-46] | 13.6% of 4822 [0-48] |
| P4 not ready, ready 2 or more turns late | 5.6% of 2608 [0-22] | 6.5% of 2214 [0-26] | 6.0% of 4822 [0-24] |
| P4 the moment came and Kingambit was never ready in the deal | 41.6% of 2608 [0-65] | 48.7% of 2214 [0-72] | 44.8% of 4822 [0-68] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.3 points (-6.3 to -4.3); P2.both: -13.7 points (-17.5 to -10.1); P2.g1: -4.2 points (-5.7 to -2.7); P2.g2: -14.7 points (-18.3 to -11.0); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -3.2 points (-7.6 to -0.6); P3.grimer_muk: -10.4 points (-13.4 to -7.6); P4.ko: -3.5 points (-7.1 to -0.6); P5.ko: -4.2 points (-7.7 to -1.1).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 80.5% / 93.1% [64-91] | 81.3% / 92.5% [69-90] | 80.9% / 92.8% [71-89] |
| P2 both Glimmora had their turn | 22.7% / 57.5% [15-30] | 20.4% / 79.5% [12-35] | 21.6% / 68.5% [15-29] |
| P2 the first Glimmora placed had its turn | 77.2% / 87.8% [61-89] | 78.1% / 83.0% [66-89] | 77.7% / 85.4% [69-86] |
| P2 the second Glimmora placed had its turn | 26.1% / 57.5% [17-35] | 23.7% / 75.1% [15-40] | 24.9% / 66.3% [17-33] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10] | 8.5% [8-9] | 8.8% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.8% / 44.6% [1-3] | 4.7% / 77.9% [0-8] | 3.2% / 61.3% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.3% / 54.8% [13-22] | 22.9% / 84.5% [13-29] | 20.1% / 69.7% [15-24] |
| P4 ready at the winning moment: Knocks out their strongest | 12.6% / 34.9% [2-25] | 3.1% / 52.4% [0-9] | 7.8% / 43.6% [2-16] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.1% / 25.4% [0-9] | 0.0% / 49.3% [0-0] | 1.6% / 37.4% [0-6] |
| P4 not ready, ready 1 turn late | 4.7% / 41.8% [0-11] | 0.0% / 75.7% [0-0] | 2.4% / 58.8% [0-7] |
| P4 not ready, ready 2 or more turns late | 1.9% / 39.0% [0-6] | 0.0% / 75.7% [0-0] | 1.0% / 57.4% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 14.6% / 51.7% [0-34] | 0.0% / 75.7% [0-0] | 7.3% / 63.7% [0-19] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.0% / 51.3% [7-58] | 21.2% / 70.5% [1-52] | 25.1% / 60.9% [8-46] |
| P5 plan reached in time: Knocks out their strongest | 19.3% / 56.4% [6-34] | 3.1% / 78.8% [0-9] | 11.2% / 67.6% [4-22] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.6% / 40.7% [0-11] | 0.0% / 75.7% [0-0] | 1.8% / 58.2% [0-7] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 37.2% of 3392 [17-53] | 100.0% of 306 [100-100] | 42.4% of 3698 [21-64] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 9.2% of 3392 [0-38] | 0.0% of 306 [0-0] | 8.4% of 3698 [0-32] |
| P4 not ready, ready 1 turn late | 14.0% of 3392 [0-57] | 0.0% of 306 [0-0] | 12.8% of 3698 [0-40] |
| P4 not ready, ready 2 or more turns late | 5.7% of 3392 [0-26] | 0.0% of 306 [0-0] | 5.3% of 3698 [0-19] |
| P4 the moment came and Kingambit was never ready in the deal | 43.1% of 3392 [0-68] | 0.0% of 306 [0-0] | 39.5% of 3698 [0-63] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -6.6 points (-7.5 to -5.6); P2.both: -13.7 points (-17.6 to -10.9); P2.g1: -6.0 points (-6.8 to -5.1); P2.g2: -14.3 points (-18.2 to -11.6); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -4.4 points (-10.8 to -0.4); P3.grimer_muk: -11.2 points (-14.7 to -7.5); P4.ko: -2.7 points (-5.7 to -0.6); P5.ko: -3.2 points (-6.5 to -0.9).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 84.5% / 86.2% [81-88] | 75.6% / 77.9% [72-80] | 80.1% / 82.1% [76-84] |
| P2 both Glimmora had their turn | 25.9% / 33.7% [23-29] | 20.8% / 29.2% [18-24] | 23.3% / 31.4% [20-26] |
| P2 the first Glimmora placed had its turn | 79.4% / 79.9% [75-84] | 68.1% / 68.7% [63-74] | 73.8% / 74.3% [69-78] |
| P2 the second Glimmora placed had its turn | 31.0% / 37.8% [28-34] | 28.3% / 35.1% [25-31] | 29.6% / 36.5% [27-32] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [8-10] | 8.5% [8-9] | 8.8% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 3.7% / 14.7% [3-4] | 6.0% / 17.8% [5-7] | 4.9% / 16.3% [4-6] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 20.3% / 29.7% [19-22] | 26.1% / 35.7% [24-28] | 23.2% / 32.7% [22-25] |
| P4 ready at the winning moment: Knocks out their strongest | 5.3% / 11.5% [3-8] | 4.5% / 11.6% [3-7] | 4.9% / 11.5% [3-8] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.1% / 6.3% [0-0] | 0.4% / 7.5% [0-1] | 0.3% / 6.9% [0-1] |
| P4 not ready, ready 1 turn late | 3.7% / 12.6% [2-6] | 2.9% / 13.2% [2-5] | 3.3% / 12.9% [2-5] |
| P4 not ready, ready 2 or more turns late | 1.6% / 10.6% [1-3] | 1.7% / 12.0% [0-3] | 1.7% / 11.3% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 10.8% / 19.7% [5-17] | 11.3% / 21.5% [6-17] | 11.0% / 20.6% [6-17] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.6% / 75.8% [58-81] | 69.3% / 76.3% [59-79] | 69.5% / 76.0% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 10.6% / 19.6% [6-16] | 9.2% / 19.4% [5-14] | 9.9% / 19.5% [6-15] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.3% / 9.2% [0-1] | 0.5% / 10.7% [0-1] | 0.4% / 10.0% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 24.8% of 2142 [17-36] | 22.1% of 2050 [16-30] | 23.5% of 4192 [16-33] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.7% of 2142 [0-2] | 2.0% of 2050 [0-7] | 1.3% of 4192 [0-4] |
| P4 not ready, ready 1 turn late | 17.2% of 2142 [12-24] | 14.3% of 2050 [10-20] | 15.8% of 4192 [11-22] |
| P4 not ready, ready 2 or more turns late | 7.6% of 2142 [4-12] | 8.4% of 2050 [3-15] | 8.0% of 4192 [4-13] |
| P4 the moment came and Kingambit was never ready in the deal | 50.3% of 2142 [38-62] | 55.1% of 2050 [43-66] | 52.6% of 4192 [40-64] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -7.0 points (-8.2 to -5.8); P2.both: -13.7 points (-15.7 to -11.7); P2.g1: -5.0 points (-6.0 to -4.0); P2.g2: -15.6 points (-17.1 to -14.0); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -11.0 points (-13.7 to -8.4); P3.grimer_muk: -16.3 points (-18.5 to -14.1); P4.ko: -2.2 points (-3.6 to -1.1); P4.never: +2.3 points (+1.2 to +3.6); P5.ko: -3.0 points (-4.5 to -1.7).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 73.8% [73-75, Wilson] | 49.3% [48-50, Wilson] | 61.6% [61-62, Wilson] |
| P2 both Glimmora had their turn | 17.9% [17-19, Wilson] | 6.2% [6-7, Wilson] | 12.1% [12-13, Wilson] |
| P2 the first Glimmora placed had its turn | 69.7% [69-71, Wilson] | 36.7% [36-38, Wilson] | 53.2% [52-54, Wilson] |
| P2 the second Glimmora placed had its turn | 22.1% [21-23, Wilson] | 18.9% [18-20, Wilson] | 20.5% [20-21, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10, Wilson] | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 10.7% [10-11, Wilson] | 13.3% [13-14, Wilson] | 12.0% [12-12, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 35.4% [34-36, Wilson] | 38.0% [37-39, Wilson] | 36.7% [36-37, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 8.8% [8-9, Wilson] | 3.2% [3-4, Wilson] | 6.0% [6-6, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 8.8% [8-9, Wilson] | 3.2% [3-4, Wilson] | 6.0% [6-6, Wilson] |
| P4 not ready, ready 1 turn late | 1.4% [1-2, Wilson] | 0.4% [0-0, Wilson] | 0.9% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 26.8% [26-28, Wilson] | 18.9% [18-20, Wilson] | 22.8% [22-23, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 63.0% [62-64, Wilson] | 77.5% [77-78, Wilson] | 70.3% [70-71, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 10.2% [10-11, Wilson] | 3.6% [3-4, Wilson] | 6.9% [7-7, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 10.2% [10-11, Wilson] | 3.6% [3-4, Wilson] | 6.9% [7-7, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 23.8% of 3698 [22-25, Wilson] | 14.4% of 2247 [13-16, Wilson] | 20.3% of 5945 [19-21, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 23.8% of 3698 [22-25, Wilson] | 14.4% of 2247 [13-16, Wilson] | 20.3% of 5945 [19-21, Wilson] |
| P4 not ready, ready 1 turn late | 3.7% of 3698 [3-4, Wilson] | 1.6% of 2247 [1-2, Wilson] | 2.9% of 5945 [3-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 3698 [0-0, Wilson] | 0.0% of 2247 [0-0, Wilson] | 0.0% of 5945 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 72.5% of 3698 [71-74, Wilson] | 84.0% of 2247 [82-85, Wilson] | 76.8% of 5945 [76-78, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.8 points (-6.4 to -5.3); P2.both: -6.2 points (-6.7 to -5.7); P2.g1: -1.8 points (-2.3 to -1.3); P2.g2: -10.2 points (-10.8 to -9.6); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -8.3 points (-8.9 to -7.8); P3.grimer_muk: -19.3 points (-19.9 to -18.6); P4.ko: -4.7 points (-5.1 to -4.3); P4.win: -4.7 points (-5.1 to -4.3); P4.never: +1.6 points (+1.1 to +2.2); P4.nomoment: +3.6 points (+3.1 to +4.0); P5.ko: -5.2 points (-5.6 to -4.8); P5.win: -5.2 points (-5.6 to -4.8).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 83.0% [82-84, Wilson] | 73.3% [72-74, Wilson] | 78.2% [78-79, Wilson] |
| P2 both Glimmora had their turn | 26.1% [25-27, Wilson] | 18.2% [17-19, Wilson] | 22.1% [22-23, Wilson] |
| P2 the first Glimmora placed had its turn | 80.2% [79-81, Wilson] | 70.2% [69-71, Wilson] | 75.2% [75-76, Wilson] |
| P2 the second Glimmora placed had its turn | 28.8% [28-30, Wilson] | 21.4% [21-22, Wilson] | 25.1% [24-26, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10, Wilson] | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 8.0% [7-9, Wilson] | 12.0% [11-13, Wilson] | 10.0% [10-10, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 30.3% [29-31, Wilson] | 36.6% [36-38, Wilson] | 33.4% [33-34, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 16.8% [16-18, Wilson] | 9.6% [9-10, Wilson] | 13.2% [13-14, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.2% [2-3, Wilson] | 1.4% [1-2, Wilson] | 1.8% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 26.9% [26-28, Wilson] | 27.1% [26-28, Wilson] | 27.0% [26-28, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 54.0% [53-55, Wilson] | 61.9% [61-63, Wilson] | 57.9% [57-59, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 19.1% [18-20, Wilson] | 11.1% [10-12, Wilson] | 15.1% [15-16, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 36.6% of 4600 [35-38, Wilson] | 25.2% of 3815 [24-27, Wilson] | 31.4% of 8415 [30-32, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 4600 [0-0, Wilson] | 0.0% of 3815 [0-0, Wilson] | 0.0% of 8415 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 4.8% of 4600 [4-5, Wilson] | 3.8% of 3815 [3-4, Wilson] | 4.4% of 8415 [4-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4600 [0-0, Wilson] | 0.0% of 3815 [0-0, Wilson] | 0.0% of 8415 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 58.6% of 4600 [57-60, Wilson] | 71.0% of 3815 [70-72, Wilson] | 64.2% of 8415 [63-65, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: -7.9 points (-8.3 to -7.4); P2.both: -11.8 points (-12.5 to -11.2); P2.g1: -7.0 points (-7.4 to -6.5); P2.g2: -12.8 points (-13.4 to -12.1); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -13.9 points (-14.5 to -13.3); P3.grimer_muk: -23.3 points (-24.0 to -22.6); P4.ko: -8.5 points (-9.0 to -8.0); P4.never: +2.1 points (+1.5 to +2.7); P4.nomoment: +7.0 points (+6.5 to +7.4); P5.ko: -9.1 points (-9.6 to -8.6).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.7% [90-91, Wilson] | 83.4% [83-84, Wilson] | 87.0% [87-88, Wilson] |
| P2 both Glimmora had their turn | 45.2% [44-46, Wilson] | 36.6% [36-38, Wilson] | 40.9% [40-42, Wilson] |
| P2 the first Glimmora placed had its turn | 85.8% [85-87, Wilson] | 77.3% [76-78, Wilson] | 81.6% [81-82, Wilson] |
| P2 the second Glimmora placed had its turn | 50.1% [49-51, Wilson] | 42.8% [42-44, Wilson] | 46.4% [46-47, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10, Wilson] | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.8% [2-3, Wilson] | 4.6% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.6% [17-18, Wilson] | 24.4% [24-25, Wilson] | 21.0% [20-22, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 38.1% [37-39, Wilson] | 28.6% [28-29, Wilson] | 33.3% [33-34, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 38.1% [37-39, Wilson] | 28.6% [28-29, Wilson] | 33.3% [33-34, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 6.5% [6-7, Wilson] | 3.3% [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 16.8% [16-17, Wilson] | 14.1% [13-15, Wilson] | 15.4% [15-16, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 45.2% [44-46, Wilson] | 50.8% [50-52, Wilson] | 48.0% [47-49, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 38.1% [37-39, Wilson] | 35.1% [34-36, Wilson] | 36.6% [36-37, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 38.1% [37-39, Wilson] | 35.1% [34-36, Wilson] | 36.6% [36-37, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 69.5% of 5484 [68-71, Wilson] | 58.0% of 4921 [57-59, Wilson] | 64.1% of 10405 [63-65, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 69.5% of 5484 [68-71, Wilson] | 58.0% of 4921 [57-59, Wilson] | 64.1% of 10405 [63-65, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5484 [0-0, Wilson] | 13.2% of 4921 [12-14, Wilson] | 6.3% of 10405 [6-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5484 [0-0, Wilson] | 0.0% of 4921 [0-0, Wilson] | 0.0% of 10405 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 30.5% of 5484 [29-32, Wilson] | 28.7% of 4921 [27-30, Wilson] | 29.7% of 10405 [29-31, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.7 points (-6.1 to -5.3); P2.both: -21.3 points (-22.0 to -20.6); P2.g1: -4.4 points (-4.8 to -4.0); P2.g2: -22.7 points (-23.4 to -22.0); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -3.0 points (-3.4 to -2.7); P3.grimer_muk: -14.8 points (-15.3 to -14.2); P4.ko: -11.2 points (-11.8 to -10.6); P4.win: -11.2 points (-11.8 to -10.6); P4.late1: +1.2 points (+0.9 to +1.5); P4.never: +1.5 points (+1.0 to +2.0); P4.nomoment: +8.5 points (+8.1 to +9.0); P5.ko: -10.0 points (-10.6 to -9.4); P5.win: -10.0 points (-10.6 to -9.4).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 73.9% [73-75, Wilson] | 49.3% [48-50, Wilson] | 61.6% [61-62, Wilson] |
| P2 both Glimmora had their turn | 18.2% [17-19, Wilson] | 6.2% [6-7, Wilson] | 12.2% [12-13, Wilson] |
| P2 the first Glimmora placed had its turn | 69.7% [69-71, Wilson] | 36.7% [36-38, Wilson] | 53.2% [52-54, Wilson] |
| P2 the second Glimmora placed had its turn | 22.4% [22-23, Wilson] | 18.9% [18-20, Wilson] | 20.7% [20-21, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10, Wilson] | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 11.5% [11-12, Wilson] | 13.5% [13-14, Wilson] | 12.5% [12-13, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 35.4% [34-36, Wilson] | 38.0% [37-39, Wilson] | 36.7% [36-37, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 2.6% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.6% [1-2, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.6% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.6% [1-2, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.0% [3-3, Wilson] | 1.4% [1-2, Wilson] | 2.2% [2-2, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 94.4% [94-95, Wilson] | 98.1% [98-98, Wilson] | 96.2% [96-96, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 2.6% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.6% [1-2, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.6% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.6% [1-2, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 47.0% of 562 [43-51, Wilson] | 30.1% of 193 [24-37, Wilson] | 42.6% of 755 [39-46, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 47.0% of 562 [43-51, Wilson] | 30.1% of 193 [24-37, Wilson] | 42.6% of 755 [39-46, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 562 [0-1, Wilson] | 0.0% of 193 [0-2, Wilson] | 0.0% of 755 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 562 [0-1, Wilson] | 0.0% of 193 [0-2, Wilson] | 0.0% of 755 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 53.0% of 562 [49-57, Wilson] | 69.9% of 193 [63-76, Wilson] | 57.4% of 755 [54-61, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.9 points (-6.4 to -5.3); P2.both: -6.2 points (-6.7 to -5.7); P2.g1: -1.8 points (-2.3 to -1.3); P2.g2: -10.2 points (-10.8 to -9.7); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -9.3 points (-9.9 to -8.8); P3.grimer_muk: -19.3 points (-19.9 to -18.6); P4.nomoment: +1.5 points (+1.3 to +1.8).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.9% [90-91, Wilson] | 83.6% [83-84, Wilson] | 87.2% [87-88, Wilson] |
| P2 both Glimmora had their turn | 53.8% [53-55, Wilson] | 41.6% [41-43, Wilson] | 47.7% [47-48, Wilson] |
| P2 the first Glimmora placed had its turn | 85.8% [85-87, Wilson] | 77.3% [76-78, Wilson] | 81.6% [81-82, Wilson] |
| P2 the second Glimmora placed had its turn | 58.8% [58-60, Wilson] | 47.9% [47-49, Wilson] | 53.4% [53-54, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 9.1% [9-10, Wilson] | 8.5% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 4.6% [4-5, Wilson] | 6.6% [6-7, Wilson] | 5.6% [5-6, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 18.7% [18-20, Wilson] | 26.0% [25-27, Wilson] | 22.4% [22-23, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 14.4% [14-15, Wilson] | 11.6% [11-12, Wilson] | 13.0% [13-13, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 14.4% [14-15, Wilson] | 11.6% [11-12, Wilson] | 13.0% [13-13, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.7% [1-1, Wilson] | 0.3% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.9% [3-3, Wilson] | 2.4% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 82.8% [82-83, Wilson] | 85.3% [85-86, Wilson] | 84.0% [84-85, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 14.4% [14-15, Wilson] | 12.3% [12-13, Wilson] | 13.3% [13-14, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 14.4% [14-15, Wilson] | 12.3% [12-13, Wilson] | 13.3% [13-14, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 83.4% of 1724 [82-85, Wilson] | 79.2% of 1468 [77-81, Wilson] | 81.4% of 3192 [80-83, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 83.4% of 1724 [82-85, Wilson] | 79.2% of 1468 [77-81, Wilson] | 81.4% of 3192 [80-83, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1724 [0-0, Wilson] | 4.5% of 1468 [4-6, Wilson] | 2.1% of 3192 [2-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1724 [0-0, Wilson] | 0.0% of 1468 [0-0, Wilson] | 0.0% of 3192 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 16.6% of 1724 [15-18, Wilson] | 16.3% of 1468 [15-18, Wilson] | 16.5% of 3192 [15-18, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.5 points (-5.9 to -5.1); P2.both: -16.6 points (-17.2 to -15.9); P2.g1: -4.4 points (-4.8 to -4.0); P2.g2: -17.8 points (-18.4 to -17.1); P3.pawn_lead: -4.0 points (-4.3 to -3.7); P3.pawn_promo: -29.4 points (-30.1 to -28.7); P3.grimer_muk: -24.6 points (-25.3 to -24.0); P4.ko: +6.5 points (+6.0 to +6.9); P4.win: +6.5 points (+6.0 to +6.9); P4.never: -9.1 points (-9.5 to -8.6); P4.nomoment: +2.4 points (+2.1 to +2.7); P5.ko: +6.7 points (+6.2 to +7.1); P5.win: +6.7 points (+6.2 to +7.1).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.6% (27.2-28.0) | 27.2% (26.8-27.6) | 27.4% (27.1-27.7) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 50.4% (49.9-50.8) | 50.3% (49.9-50.8) | 50.4% (50.0-50.7) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 58.8% (58.4-59.3) | 58.9% (58.5-59.4) | 58.9% (58.6-59.2) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 63.7% (63.3-64.1) | 63.7% (63.3-64.1) | 63.7% (63.4-64.0) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 66.7% (66.3-67.1) | 66.6% (66.2-67.0) | 66.7% (66.4-67.0) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 68.3% (67.9-68.8) | 68.2% (67.8-68.6) | 68.3% (68.0-68.6) |
| K2 Kingambit in play, own turn 2 | 7.7% (7.5-8.0) | 7.7% (7.4-7.9) | 7.7% (7.5-7.9) |
| K2 Kingambit in play, own turn 3 | 13.5% (13.2-13.8) | 13.5% (13.2-13.8) | 13.5% (13.3-13.7) |
| K2 Kingambit in play, own turn 4 | 21.1% (20.7-21.4) | 21.1% (20.7-21.4) | 21.1% (20.8-21.3) |
| K2 Kingambit in play, own turn 5 | 30.1% (29.7-30.5) | 29.7% (29.3-30.1) | 29.9% (29.6-30.2) |
| K2 Kingambit in play, own turn 6 | 39.7% (39.3-40.1) | 39.0% (38.6-39.4) | 39.3% (39.0-39.6) |
| K6 Muk and Regigigas both in play, own turn 3 | 21.2% (20.9-21.6) | 20.9% (20.5-21.2) | 21.0% (20.8-21.3) |
| K6 Muk and Regigigas both in play, own turn 4 | 28.1% (27.7-28.5) | 27.7% (27.3-28.1) | 27.9% (27.6-28.2) |
| K6 Muk and Regigigas both in play, own turn 5 | 34.3% (33.9-34.7) | 33.9% (33.5-34.3) | 34.1% (33.8-34.4) |
| G3 Pawniard in play, own turn 1 | 50.4% (49.9-50.8) | 50.3% (49.9-50.8) | 50.4% (50.0-50.7) |
| G3 Pawniard in play, own turn 2 | 51.1% (50.6-51.5) | 51.3% (50.8-51.7) | 51.2% (50.9-51.5) |
| G3 Pawniard in play, own turn 3 | 50.2% (49.7-50.6) | 50.2% (49.8-50.6) | 50.2% (49.9-50.5) |
| G3 Pawniard in play, own turn 4 | 45.6% (45.2-46.1) | 45.6% (45.1-46.0) | 45.6% (45.3-45.9) |
| G3 Pawniard in play, own turn 5 | 38.3% (37.8-38.7) | 38.5% (38.1-39.0) | 38.4% (38.1-38.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 7.7% (7.5-8.0) | 7.7% (7.4-7.9) | 7.7% (7.5-7.9) |
| G3 Kingambit in play, own turn 3 | 13.5% (13.2-13.8) | 13.5% (13.2-13.8) | 13.5% (13.3-13.7) |
| G3 Kingambit in play, own turn 4 | 21.1% (20.7-21.4) | 21.1% (20.7-21.4) | 21.1% (20.8-21.3) |
| G3 Kingambit in play, own turn 5 | 30.1% (29.7-30.5) | 29.7% (29.3-30.1) | 29.9% (29.6-30.2) |
| G3 Alolan Grimer in play, own turn 1 | 48.1% (47.7-48.6) | 47.9% (47.5-48.3) | 48.0% (47.7-48.3) |
| G3 Alolan Grimer in play, own turn 2 | 39.0% (38.6-39.5) | 39.2% (38.8-39.7) | 39.1% (38.8-39.4) |
| G3 Alolan Grimer in play, own turn 3 | 35.1% (34.7-35.5) | 35.2% (34.8-35.6) | 35.1% (34.8-35.4) |
| G3 Alolan Grimer in play, own turn 4 | 30.2% (29.8-30.6) | 30.4% (30.0-30.8) | 30.3% (30.0-30.6) |
| G3 Alolan Grimer in play, own turn 5 | 24.9% (24.5-25.3) | 25.1% (24.7-25.4) | 25.0% (24.7-25.2) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 16.3% (16.0-16.6) | 15.9% (15.6-16.2) | 16.1% (15.9-16.3) |
| G3 Alolan Muk in play, own turn 3 | 24.2% (23.8-24.6) | 24.0% (23.6-24.3) | 24.1% (23.8-24.4) |
| G3 Alolan Muk in play, own turn 4 | 31.5% (31.1-31.9) | 31.1% (30.7-31.6) | 31.3% (31.0-31.6) |
| G3 Alolan Muk in play, own turn 5 | 38.1% (37.6-38.5) | 37.7% (37.2-38.1) | 37.9% (37.6-38.2) |
| G3 Glimmet in play, own turn 1 | 76.5% (76.2-76.9) | 76.6% (76.2-76.9) | 76.5% (76.3-76.8) |
| G3 Glimmet in play, own turn 2 | 45.6% (45.1-46.0) | 45.7% (45.3-46.2) | 45.6% (45.3-46.0) |
| G3 Glimmet in play, own turn 3 | 38.3% (37.9-38.8) | 38.2% (37.8-38.6) | 38.3% (38.0-38.6) |
| G3 Glimmet in play, own turn 4 | 29.9% (29.5-30.3) | 30.1% (29.7-30.5) | 30.0% (29.7-30.3) |
| G3 Glimmet in play, own turn 5 | 21.4% (21.0-21.7) | 21.5% (21.1-21.9) | 21.4% (21.2-21.7) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 54.5% (54.1-55.0) | 54.7% (54.3-55.1) | 54.6% (54.3-54.9) |
| G3 Glimmora in play, own turn 3 | 68.1% (67.7-68.5) | 68.3% (67.9-68.7) | 68.2% (67.9-68.5) |
| G3 Glimmora in play, own turn 4 | 78.1% (77.7-78.4) | 77.9% (77.6-78.3) | 78.0% (77.7-78.3) |
| G3 Glimmora in play, own turn 5 | 84.8% (84.4-85.1) | 84.7% (84.4-85.0) | 84.7% (84.5-85.0) |
| G3 Regigigas in play, own turn 1 | 76.6% (76.2-76.9) | 76.8% (76.5-77.2) | 76.7% (76.4-77.0) |
| G3 Regigigas in play, own turn 2 | 85.3% (84.9-85.6) | 85.2% (84.8-85.5) | 85.2% (85.0-85.4) |
| G3 Regigigas in play, own turn 3 | 89.6% (89.3-89.8) | 89.6% (89.3-89.9) | 89.6% (89.4-89.8) |
| G3 Regigigas in play, own turn 4 | 92.0% (91.8-92.3) | 92.0% (91.8-92.2) | 92.0% (91.8-92.2) |
| G3 Regigigas in play, own turn 5 | 93.2% (93.0-93.5) | 93.2% (93.0-93.5) | 93.2% (93.1-93.4) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 67.2% (66.8-67.6) | 67.1% (66.6-67.5) | 67.1% (66.8-67.4) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 81.1% (80.8-81.5) | 81.1% (80.8-81.4) | 81.1% (80.9-81.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 89.8% (89.5-90.1) | 89.7% (89.4-89.9) | 89.7% (89.5-89.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 94.7% (94.5-94.9) | 94.8% (94.6-95.0) | 94.8% (94.6-94.9) |
| G4.s2 a Stage 2 in play, own turn 2 | 7.7% (7.5-8.0) | 7.7% (7.4-7.9) | 7.7% (7.5-7.9) |
| G4.s2 a Stage 2 in play, own turn 3 | 13.5% (13.2-13.8) | 13.5% (13.2-13.8) | 13.5% (13.3-13.7) |
| G4.s2 a Stage 2 in play, own turn 4 | 21.1% (20.7-21.4) | 21.1% (20.7-21.4) | 21.1% (20.8-21.3) |
| G4.s2 a Stage 2 in play, own turn 5 | 30.1% (29.7-30.5) | 29.7% (29.3-30.1) | 29.9% (29.6-30.2) |
| G5.any3 an empty own turn among turns 1-3 | 34.7% (34.3-35.1) | 34.3% (33.9-34.7) | 34.5% (34.2-34.8) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 7.7% (7.4-7.9) | 3.8% (3.7-4.0) |
| G6 Kingambit with [DD] attached, own turn 3 | 12.2% (11.9-12.5) | 13.5% (13.2-13.8) | 12.8% (12.6-13.0) |
| G6 Kingambit with [DD] attached, own turn 4 | 21.1% (20.7-21.4) | 21.1% (20.7-21.4) | 21.1% (20.8-21.3) |
| G6 Kingambit with [DD] attached, own turn 5 | 30.1% (29.7-30.5) | 29.7% (29.3-30.1) | 29.9% (29.6-30.2) |
| G5 mean empty own turns in turns 1-5 | 0.913 | 0.912 | 0.912 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.3% / 9.7% [1-2] | 0.7% / 4.8% [0-1] |
| K3.by3 | 1.9% / 10.5% [1-3] | 1.6% / 9.9% [1-2] | 1.7% / 10.2% [1-2] |
| K3.by4 | 2.4% / 11.0% [2-3] | 3.1% / 11.4% [2-4] | 2.7% / 11.2% [2-3] |
| K3.by5 | 3.8% / 12.5% [3-5] | 3.6% / 19.2% [3-5] | 3.7% / 15.9% [3-5] |
| K3.by6 | 4.1% / 20.9% [3-6] | 6.5% / 30.2% [3-10] | 5.3% / 25.5% [3-7] |
| K3.by7 | 8.7% / 33.6% [4-16] | 6.7% / 52.9% [3-11] | 7.7% / 43.2% [4-13] |
| K3.by8 | 8.8% / 57.0% [4-16] | 6.7% / 58.3% [3-11] | 7.8% / 57.6% [4-13] |
| K3.never | 43.0% / 91.2% [17-68] | 41.7% / 93.3% [18-64] | 42.4% / 92.2% [18-66] |
| K3.k0 | 2.6% / 50.8% [2-4] | 1.8% / 53.4% [1-3] | 2.2% / 52.1% [1-3] |
| K3.k1 | 0.0% / 48.1% [0-0] | 0.0% / 51.6% [0-0] | 0.0% / 49.9% [0-0] |
| K3.k2 | 5.0% / 53.1% [1-12] | 3.9% / 55.6% [1-8] | 4.5% / 54.3% [1-10] |
| K3.k3p | 1.2% / 49.4% [0-4] | 1.0% / 52.6% [0-3] | 1.1% / 51.0% [0-3] |
| K4 | 6.2% / 55.8% [1-13] | 4.9% / 57.5% [1-9] | 5.6% / 56.7% [1-11] |
| K5 | 5.8% / 60.5% [4-7] | 6.8% / 58.2% [5-9] | 6.3% / 59.3% [5-8] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.5 points (-2.1 to -0.9); K3.by4: -1.9 points (-2.5 to -1.3); K3.by5: -2.4 points (-3.0 to -1.7); K3.by6: -3.5 points (-5.1 to -2.4); K3.by7: -5.6 points (-8.9 to -2.8); K3.by8: -6.9 points (-12.1 to -2.8); K3.never: +4.9 points (+0.8 to +9.8); K3.k0: -1.7 points (-2.6 to -1.0); K3.k2: -2.4 points (-5.2 to -0.5); K4: -5.2 points (-10.5 to -0.9); K5: -1.8 points (-2.4 to -1.3).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.8% [1-2] | 0.9% [0-1] |
| K3.by3 | 1.8% / 13.1% [1-3] | 2.2% [1-3] | 2.0% / 7.6% [1-3] |
| K3.by4 | 2.1% / 13.4% [1-3] | 3.0% [2-4] | 2.5% / 8.2% [2-3] |
| K3.by5 | 3.7% / 15.0% [2-5] | 3.6% / 32.2% [3-4] | 3.7% / 23.6% [3-5] |
| K3.by6 | 4.0% / 15.3% [3-6] | 3.9% / 32.5% [3-5] | 4.0% / 23.9% [3-5] |
| K3.by7 | 10.8% / 33.3% [4-20] | 4.7% / 65.4% [3-7] | 7.8% / 49.3% [4-14] |
| K3.by8 | 10.8% / 53.8% [4-20] | 4.7% / 80.0% [3-7] | 7.8% / 66.9% [4-14] |
| K3.never | 46.2% / 89.2% [17-75] | 20.0% / 95.3% [1-48] | 33.1% / 92.2% [14-56] |
| K3.k0 | 2.3% / 45.3% [1-3] | 2.5% / 77.7% [1-4] | 2.4% / 61.5% [2-3] |
| K3.k1 | 0.0% / 43.0% [0-0] | 0.0% / 75.2% [0-0] | 0.0% / 59.1% [0-0] |
| K3.k2 | 6.3% / 49.4% [1-15] | 1.4% / 76.7% [0-3] | 3.9% / 63.0% [1-9] |
| K3.k3p | 2.2% / 45.2% [0-7] | 0.8% / 76.1% [0-3] | 1.5% / 60.6% [0-4] |
| K4 | 8.5% / 52.6% [1-18] | 2.3% / 79.5% [0-5] | 5.4% / 66.0% [1-12] |
| K5 | 6.0% / 53.0% [4-8] | 6.7% / 80.6% [5-8] | 6.3% / 66.8% [5-8] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.7 points (-2.1 to -1.2); K3.by4: -2.2 points (-2.7 to -1.5); K3.by5: -2.7 points (-3.1 to -2.1); K3.by6: -2.9 points (-3.4 to -2.3); K3.by7: -7.8 points (-14.5 to -2.8); K3.by8: -7.8 points (-14.5 to -2.8); K3.never: +3.9 points (+0.4 to +8.2); K3.k0: -2.1 points (-2.7 to -1.4); K3.k2: -1.8 points (-4.1 to -0.5); K4: -5.7 points (-12.2 to -0.7); K5: -1.7 points (-2.3 to -1.0).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.4% [1-2] | 0.7% [1-1] |
| K3.by3 | 2.0% [2-2] | 1.8% [1-2] | 1.9% [2-2] |
| K3.by4 | 2.5% [2-3] | 2.8% [2-3] | 2.6% [2-3] |
| K3.by5 | 3.5% [3-4] | 4.3% [4-5] | 3.9% [3-4] |
| K3.by6 | 4.8% [4-6] | 5.3% / 9.3% [4-6] | 5.0% / 7.0% [4-6] |
| K3.by7 | 5.6% / 10.0% [5-7] | 5.9% / 15.8% [5-7] | 5.7% / 12.9% [5-7] |
| K3.by8 | 6.2% / 17.1% [5-8] | 6.2% / 17.9% [5-8] | 6.2% / 17.5% [5-8] |
| K3.never | 82.9% / 93.8% [75-90] | 82.1% / 93.8% [74-88] | 82.5% / 93.8% [75-89] |
| K3.k0 | 2.6% / 13.6% [2-3] | 1.9% / 13.6% [2-2] | 2.3% / 13.6% [2-3] |
| K3.k1 | 0.0% / 10.9% [0-0] | 0.0% / 11.7% [0-0] | 0.0% / 11.3% [0-0] |
| K3.k2 | 2.0% / 12.9% [1-3] | 2.6% / 14.3% [2-4] | 2.3% / 13.6% [2-3] |
| K3.k3p | 1.6% / 12.5% [1-3] | 1.7% / 13.3% [1-3] | 1.6% / 12.9% [1-3] |
| K4 | 3.5% / 14.9% [2-5] | 4.3% / 16.2% [3-6] | 3.9% / 15.6% [3-5] |
| K5 | 6.8% / 19.9% [6-7] | 8.0% / 19.7% [7-9] | 7.4% / 19.8% [7-8] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.6 points (-1.8 to -1.3); K3.by4: -2.0 points (-2.3 to -1.7); K3.by5: -2.6 points (-3.0 to -2.2); K3.by6: -3.7 points (-4.4 to -3.0); K3.by7: -5.1 points (-6.6 to -3.8); K3.by8: -6.1 points (-8.3 to -4.4); K3.never: +5.4 points (+3.7 to +7.4); K3.k0: -1.9 points (-2.2 to -1.5); K3.k2: -1.1 points (-1.5 to -0.7); K3.k3p: -3.2 points (-5.2 to -1.5); K4: -4.2 points (-6.3 to -2.5); K5: -2.2 points (-2.6 to -1.8).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 1.8% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by4 | 1.7% [1-2, Wilson] | 3.2% [3-4, Wilson] | 2.5% [2-3, Wilson] |
| K3.by5 | 5.2% [5-6, Wilson] | 3.6% [3-4, Wilson] | 4.4% [4-5, Wilson] |
| K3.by6 | 6.8% [6-7, Wilson] | 3.6% [3-4, Wilson] | 5.2% [5-6, Wilson] |
| K3.by7 | 6.8% [6-7, Wilson] | 3.6% [3-4, Wilson] | 5.2% [5-6, Wilson] |
| K3.by8 | 6.8% [6-7, Wilson] | 3.6% [3-4, Wilson] | 5.2% [5-6, Wilson] |
| K3.never | 93.2% [93-94, Wilson] | 96.4% [96-97, Wilson] | 94.8% [94-95, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.7% [1-2, Wilson] | 1.8% [2-2, Wilson] | 1.8% [2-2, Wilson] |
| K3.k3p | 5.1% [5-6, Wilson] | 1.8% [2-2, Wilson] | 3.4% [3-4, Wilson] |
| K4 | 6.8% [6-7, Wilson] | 3.6% [3-4, Wilson] | 5.2% [5-6, Wilson] |
| K5 | 13.6% [13-14, Wilson] | 18.0% [17-19, Wilson] | 15.8% [15-16, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.5 points (-1.8 to -1.2); K3.by5: -5.1 points (-5.5 to -4.7); K3.by6: -6.0 points (-6.4 to -5.6); K3.by7: -6.0 points (-6.4 to -5.6); K3.by8: -6.0 points (-6.4 to -5.6); K3.never: +6.0 points (+5.6 to +6.4); K3.k3p: -5.4 points (-5.8 to -5.0); K4: -6.0 points (-6.4 to -5.6); K5: -6.0 points (-6.4 to -5.5).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.7% [1-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by3 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.by4 | 2.4% [2-3, Wilson] | 3.6% [3-4, Wilson] | 3.0% [3-3, Wilson] |
| K3.by5 | 3.7% [3-4, Wilson] | 7.3% [7-8, Wilson] | 5.5% [5-6, Wilson] |
| K3.by6 | 8.9% [8-10, Wilson] | 8.7% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| K3.by7 | 13.0% [12-14, Wilson] | 8.7% [8-9, Wilson] | 10.9% [10-11, Wilson] |
| K3.by8 | 13.0% [12-14, Wilson] | 8.7% [8-9, Wilson] | 10.9% [10-11, Wilson] |
| K3.never | 87.0% [86-88, Wilson] | 91.3% [91-92, Wilson] | 89.1% [89-90, Wilson] |
| K3.k0 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.2% [1-1, Wilson] | 1.9% [2-2, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 9.3% [9-10, Wilson] | 5.1% [5-6, Wilson] | 7.2% [7-8, Wilson] |
| K4 | 10.6% [10-11, Wilson] | 7.0% [6-7, Wilson] | 8.8% [8-9, Wilson] |
| K5 | 10.0% [9-11, Wilson] | 13.4% [13-14, Wilson] | 11.7% [11-12, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.6 points (-1.8 to -1.4); K3.by4: -2.1 points (-2.3 to -1.8); K3.by5: -5.5 points (-5.9 to -5.1); K3.by6: -13.3 points (-13.9 to -12.8); K3.by7: -13.8 points (-14.3 to -13.3); K3.by8: -13.8 points (-14.3 to -13.3); K3.never: +13.8 points (+13.3 to +14.3); K3.k0: -1.6 points (-1.8 to -1.4); K3.k3p: -11.5 points (-12.0 to -11.0); K4: -12.2 points (-12.7 to -11.6); K5: -4.5 points (-4.9 to -4.1).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.7% [1-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by3 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.by4 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.by5 | 2.4% [2-3, Wilson] | 4.4% [4-5, Wilson] | 3.4% [3-4, Wilson] |
| K3.by6 | 4.5% [4-5, Wilson] | 4.6% [4-5, Wilson] | 4.5% [4-5, Wilson] |
| K3.by7 | 4.6% [4-5, Wilson] | 23.9% [23-25, Wilson] | 14.2% [14-15, Wilson] |
| K3.by8 | 32.5% [32-33, Wilson] | 24.0% [23-25, Wilson] | 28.3% [28-29, Wilson] |
| K3.never | 67.5% [67-68, Wilson] | 76.0% [75-77, Wilson] | 71.7% [71-72, Wilson] |
| K3.k0 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.1% [2-2, Wilson] | 2.9% [3-3, Wilson] | 2.5% [2-3, Wilson] |
| K3.k3p | 27.9% [27-29, Wilson] | 19.4% [19-20, Wilson] | 23.7% [23-24, Wilson] |
| K4 | 30.1% [29-31, Wilson] | 22.3% [21-23, Wilson] | 26.2% [26-27, Wilson] |
| K5 | 7.1% [7-8, Wilson] | 7.8% [7-8, Wilson] | 7.5% [7-8, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.6 points (-1.8 to -1.4); K3.by4: -1.6 points (-1.8 to -1.4); K3.by5: -2.8 points (-3.0 to -2.5); K3.by6: -3.6 points (-3.9 to -3.3); K3.by7: -10.2 points (-10.7 to -9.7); K3.by8: -17.8 points (-18.4 to -17.2); K3.never: +17.8 points (+17.2 to +18.4); K3.k0: -1.6 points (-1.8 to -1.4); K3.k2: -2.0 points (-2.3 to -1.7); K3.k3p: -14.2 points (-14.8 to -13.6); K4: -16.2 points (-16.8 to -15.6); K5: -2.5 points (-2.8 to -2.2).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 1.8% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by4 | 1.7% [1-2, Wilson] | 3.0% [3-3, Wilson] | 2.4% [2-3, Wilson] |
| K3.by5 | 4.1% [4-5, Wilson] | 3.4% [3-4, Wilson] | 3.8% [4-4, Wilson] |
| K3.by6 | 5.9% [5-6, Wilson] | 3.4% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.by7 | 5.9% [5-6, Wilson] | 3.4% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.by8 | 5.9% [5-6, Wilson] | 3.4% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.never | 94.1% [94-95, Wilson] | 96.6% [96-97, Wilson] | 95.3% [95-96, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.7% [1-2, Wilson] | 1.8% [2-2, Wilson] | 1.8% [2-2, Wilson] |
| K3.k3p | 4.2% [4-5, Wilson] | 1.6% [1-2, Wilson] | 2.9% [3-3, Wilson] |
| K4 | 5.9% [5-6, Wilson] | 3.4% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K5 | 13.6% [13-14, Wilson] | 18.0% [17-19, Wilson] | 15.8% [15-16, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.5 points (-1.8 to -1.3); K3.by5: -5.2 points (-5.6 to -4.8); K3.by6: -6.1 points (-6.5 to -5.7); K3.by7: -6.1 points (-6.5 to -5.7); K3.by8: -6.1 points (-6.5 to -5.7); K3.never: +6.1 points (+5.7 to +6.5); K3.k3p: -5.5 points (-5.9 to -5.2); K4: -6.1 points (-6.5 to -5.7); K5: -6.0 points (-6.4 to -5.5).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.7% [1-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by3 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.by4 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.by5 | 2.4% [2-3, Wilson] | 4.4% [4-5, Wilson] | 3.4% [3-4, Wilson] |
| K3.by6 | 4.5% [4-5, Wilson] | 4.6% [4-5, Wilson] | 4.5% [4-5, Wilson] |
| K3.by7 | 4.6% [4-5, Wilson] | 6.6% [6-7, Wilson] | 5.6% [5-6, Wilson] |
| K3.by8 | 6.4% [6-7, Wilson] | 6.7% [6-7, Wilson] | 6.5% [6-7, Wilson] |
| K3.by9 | 6.4% [6-7, Wilson] | 17.1% [16-18, Wilson] | 11.8% [11-12, Wilson] |
| K3.by10 | 19.8% [19-21, Wilson] | 17.2% [16-18, Wilson] | 18.5% [18-19, Wilson] |
| K3.never | 80.2% [79-81, Wilson] | 82.8% [82-84, Wilson] | 81.5% [81-82, Wilson] |
| K3.k0 | 2.4% [2-3, Wilson] | 1.7% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.1% [2-2, Wilson] | 2.9% [3-3, Wilson] | 2.5% [2-3, Wilson] |
| K3.k3p | 15.3% [15-16, Wilson] | 12.6% [12-13, Wilson] | 13.9% [13-14, Wilson] |
| K4 | 17.4% [17-18, Wilson] | 15.4% [15-16, Wilson] | 16.4% [16-17, Wilson] |
| K5 | 7.2% [7-8, Wilson] | 8.2% [8-9, Wilson] | 7.7% [7-8, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.6 points (-1.8 to -1.4); K3.by4: -1.6 points (-1.8 to -1.4); K3.by5: -2.8 points (-3.0 to -2.5); K3.by6: -3.6 points (-3.9 to -3.3); K3.by7: -14.5 points (-15.0 to -13.9); K3.by8: -30.6 points (-31.2 to -29.9); K3.by9: -29.0 points (-29.6 to -28.3); K3.by10: -25.3 points (-25.9 to -24.6); K3.never: +25.3 points (+24.6 to +25.9); K3.k0: -1.6 points (-1.8 to -1.4); K3.k2: -2.0 points (-2.3 to -1.7); K3.k3p: -21.6 points (-22.3 to -21.0); K4: -23.6 points (-24.3 to -23.0); K5: -2.4 points (-2.7 to -2.1).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.0 (+19.7 to +20.4) FLAG | +20.2 (+19.8 to +20.5) FLAG | +20.1 (+19.8 to +20.4) FLAG |
| K1 Pawniard in play at setup | -1.6 (-1.8 to -1.5) FLAG | -1.6 (-1.8 to -1.5) FLAG | -1.6 (-1.7 to -1.5) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -5.6 (-5.9 to -5.3) FLAG | -5.3 (-5.6 to -5.0) FLAG | -5.4 (-5.6 to -5.2) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -9.1 (-9.5 to -8.8) FLAG | -8.9 (-9.2 to -8.6) FLAG | -9.0 (-9.2 to -8.8) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -10.8 (-11.2 to -10.5) FLAG | -10.9 (-11.2 to -10.5) FLAG | -10.8 (-11.1 to -10.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -11.9 (-12.2 to -11.5) FLAG | -12.0 (-12.4 to -11.6) FLAG | -11.9 (-12.2 to -11.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -12.5 (-12.8 to -12.1) FLAG | -12.6 (-12.9 to -12.2) FLAG | -12.5 (-12.8 to -12.3) FLAG |
| K2 Kingambit in play, own turn 2 | -3.0 (-3.2 to -2.8) FLAG | -3.1 (-3.3 to -2.9) FLAG | -3.0 (-3.2 to -2.9) FLAG |
| K2 Kingambit in play, own turn 3 | -7.6 (-7.8 to -7.3) FLAG | -7.6 (-7.9 to -7.3) FLAG | -7.6 (-7.8 to -7.4) FLAG |
| K2 Kingambit in play, own turn 4 | -11.9 (-12.3 to -11.6) FLAG | -12.1 (-12.4 to -11.7) FLAG | -12.0 (-12.2 to -11.8) FLAG |
| K2 Kingambit in play, own turn 5 | -16.3 (-16.7 to -16.0) FLAG | -16.7 (-17.1 to -16.4) FLAG | -16.5 (-16.8 to -16.3) FLAG |
| K2 Kingambit in play, own turn 6 | -19.7 (-20.1 to -19.3) FLAG | -20.1 (-20.5 to -19.7) FLAG | -19.9 (-20.2 to -19.7) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | -1.0 (-1.3 to -0.6) | -1.4 (-1.7 to -1.0) FLAG | -1.2 (-1.4 to -0.9) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | -2.3 (-2.7 to -1.9) FLAG | -2.8 (-3.2 to -2.4) FLAG | -2.5 (-2.8 to -2.3) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | -2.6 (-3.0 to -2.2) FLAG | -3.1 (-3.5 to -2.7) FLAG | -2.9 (-3.2 to -2.6) FLAG |
| G3 Pawniard in play, own turn 1 | -5.6 (-5.9 to -5.3) FLAG | -5.3 (-5.6 to -5.0) FLAG | -5.4 (-5.6 to -5.2) FLAG |
| G3 Pawniard in play, own turn 2 | -6.1 (-6.5 to -5.8) FLAG | -5.8 (-6.2 to -5.4) FLAG | -6.0 (-6.2 to -5.7) FLAG |
| G3 Pawniard in play, own turn 3 | -3.3 (-3.6 to -2.9) FLAG | -3.2 (-3.6 to -2.8) FLAG | -3.2 (-3.5 to -3.0) FLAG |
| G3 Pawniard in play, own turn 5 | +3.9 (+3.5 to +4.3) FLAG | +4.2 (+3.8 to +4.6) FLAG | +4.0 (+3.7 to +4.3) FLAG |
| G3 Kingambit in play, own turn 2 | -3.0 (-3.2 to -2.8) FLAG | -3.1 (-3.3 to -2.9) FLAG | -3.0 (-3.2 to -2.9) FLAG |
| G3 Kingambit in play, own turn 3 | -7.6 (-7.8 to -7.3) FLAG | -7.6 (-7.9 to -7.3) FLAG | -7.6 (-7.8 to -7.4) FLAG |
| G3 Kingambit in play, own turn 4 | -11.9 (-12.3 to -11.6) FLAG | -12.1 (-12.4 to -11.7) FLAG | -12.0 (-12.2 to -11.8) FLAG |
| G3 Kingambit in play, own turn 5 | -16.3 (-16.7 to -16.0) FLAG | -16.7 (-17.1 to -16.4) FLAG | -16.5 (-16.8 to -16.3) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -6.5 (-6.8 to -6.2) FLAG | -6.8 (-7.2 to -6.5) FLAG | -6.7 (-6.9 to -6.4) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -7.2 (-7.6 to -6.9) FLAG | -7.3 (-7.7 to -7.0) FLAG | -7.3 (-7.5 to -7.0) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -4.8 (-5.2 to -4.5) FLAG | -4.8 (-5.2 to -4.5) FLAG | -4.8 (-5.1 to -4.6) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -2.8 (-3.2 to -2.5) FLAG | -2.8 (-3.1 to -2.4) FLAG | -2.8 (-3.0 to -2.6) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -1.8 (-2.1 to -1.5) FLAG | -2.0 (-2.3 to -1.6) FLAG | -1.9 (-2.1 to -1.7) FLAG |
| G3 Alolan Muk in play, own turn 2 | -2.6 (-2.9 to -2.3) FLAG | -3.0 (-3.3 to -2.8) FLAG | -2.8 (-3.0 to -2.6) FLAG |
| G3 Alolan Muk in play, own turn 3 | -6.8 (-7.2 to -6.5) FLAG | -7.4 (-7.7 to -7.0) FLAG | -7.1 (-7.4 to -6.9) FLAG |
| G3 Alolan Muk in play, own turn 4 | -9.7 (-10.1 to -9.3) FLAG | -10.2 (-10.6 to -9.8) FLAG | -9.9 (-10.2 to -9.7) FLAG |
| G3 Alolan Muk in play, own turn 5 | -11.2 (-11.6 to -10.8) FLAG | -11.6 (-12.0 to -11.2) FLAG | -11.4 (-11.7 to -11.1) FLAG |
| G3 Glimmet in play, own turn 1 | -5.6 (-5.8 to -5.3) FLAG | -5.9 (-6.2 to -5.6) FLAG | -5.7 (-5.9 to -5.5) FLAG |
| G3 Glimmet in play, own turn 2 | -7.2 (-7.6 to -6.8) FLAG | -6.7 (-7.1 to -6.3) FLAG | -7.0 (-7.2 to -6.7) FLAG |
| G3 Glimmet in play, own turn 3 | -3.8 (-4.2 to -3.4) FLAG | -3.7 (-4.1 to -3.3) FLAG | -3.8 (-4.1 to -3.5) FLAG |
| G3 Glimmet in play, own turn 4 | -1.0 (-1.4 to -0.6) FLAG | -0.8 (-1.2 to -0.4) | -0.9 (-1.2 to -0.6) |
| G3 Glimmet in play, own turn 5 | +1.2 (+0.9 to +1.6) FLAG | +1.7 (+1.3 to +2.0) FLAG | +1.5 (+1.2 to +1.7) FLAG |
| G3 Glimmora in play, own turn 2 | -8.6 (-8.9 to -8.3) FLAG | -8.6 (-9.0 to -8.3) FLAG | -8.6 (-8.9 to -8.4) FLAG |
| G3 Glimmora in play, own turn 3 | -11.6 (-11.9 to -11.2) FLAG | -11.6 (-12.0 to -11.3) FLAG | -11.6 (-11.8 to -11.4) FLAG |
| G3 Glimmora in play, own turn 4 | -11.4 (-11.7 to -11.0) FLAG | -11.5 (-11.8 to -11.2) FLAG | -11.4 (-11.7 to -11.2) FLAG |
| G3 Glimmora in play, own turn 5 | -10.3 (-10.6 to -10.0) FLAG | -10.4 (-10.7 to -10.1) FLAG | -10.4 (-10.6 to -10.2) FLAG |
| G3 Regigigas in play, own turn 1 | +21.2 (+20.8 to +21.6) FLAG | +21.6 (+21.2 to +22.0) FLAG | +21.4 (+21.1 to +21.7) FLAG |
| G3 Regigigas in play, own turn 2 | +17.6 (+17.2 to +18.0) FLAG | +18.1 (+17.7 to +18.4) FLAG | +17.8 (+17.6 to +18.1) FLAG |
| G3 Regigigas in play, own turn 3 | +15.1 (+14.8 to +15.5) FLAG | +15.5 (+15.1 to +15.8) FLAG | +15.3 (+15.0 to +15.5) FLAG |
| G3 Regigigas in play, own turn 4 | +13.8 (+13.5 to +14.1) FLAG | +13.9 (+13.5 to +14.2) FLAG | +13.8 (+13.6 to +14.1) FLAG |
| G3 Regigigas in play, own turn 5 | +12.9 (+12.6 to +13.3) FLAG | +13.1 (+12.7 to +13.4) FLAG | +13.0 (+12.8 to +13.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -8.3 (-8.7 to -8.0) FLAG | -8.6 (-8.9 to -8.3) FLAG | -8.5 (-8.7 to -8.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -8.5 (-8.8 to -8.2) FLAG | -8.7 (-9.0 to -8.4) FLAG | -8.6 (-8.8 to -8.4) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -6.2 (-6.4 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG | -6.2 (-6.3 to -6.0) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -3.9 (-4.1 to -3.7) FLAG | -3.8 (-3.9 to -3.6) FLAG | -3.8 (-3.9 to -3.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | -3.0 (-3.2 to -2.8) FLAG | -3.1 (-3.3 to -2.9) FLAG | -3.0 (-3.2 to -2.9) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -7.6 (-7.8 to -7.3) FLAG | -7.6 (-7.9 to -7.3) FLAG | -7.6 (-7.8 to -7.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -11.9 (-12.3 to -11.6) FLAG | -12.1 (-12.4 to -11.7) FLAG | -12.0 (-12.2 to -11.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -16.3 (-16.7 to -16.0) FLAG | -16.7 (-17.1 to -16.4) FLAG | -16.5 (-16.8 to -16.3) FLAG |
| G5.any3 an empty own turn among turns 1-3 | +11.6 (+11.2 to +11.9) FLAG | +11.8 (+11.5 to +12.2) FLAG | +11.7 (+11.4 to +11.9) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | -3.1 (-3.3 to -2.9) FLAG | -1.5 (-1.6 to -1.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -5.4 (-5.6 to -5.1) FLAG | -7.6 (-7.9 to -7.3) FLAG | -6.5 (-6.7 to -6.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -11.9 (-12.3 to -11.6) FLAG | -12.1 (-12.4 to -11.7) FLAG | -12.0 (-12.2 to -11.8) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -16.3 (-16.7 to -16.0) FLAG | -16.7 (-17.1 to -16.4) FLAG | -16.5 (-16.8 to -16.3) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.154 (+0.148 to +0.159) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Professor's Research A4b 373 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.1 points
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn -5.3 points (-6.3 to -4.3); P2 both Glimmora had their turn -13.7 points (-17.5 to -10.1); P2 the first Glimmora placed had its turn -4.2 points (-5.7 to -2.7); P2 the second Glimmora placed had its turn -14.7 points (-18.3 to -11.0); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -3.2 points (-7.6 to -0.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -10.4 points (-13.4 to -7.6); P4 ready at the winning moment: Knocks out their strongest -3.5 points (-7.1 to -0.6); P5 plan reached in time: Knocks out their strongest -4.2 points (-7.7 to -1.1)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -6.6 points (-7.5 to -5.6); P2 both Glimmora had their turn -13.7 points (-17.6 to -10.9); P2 the first Glimmora placed had its turn -6.0 points (-6.8 to -5.1); P2 the second Glimmora placed had its turn -14.3 points (-18.2 to -11.6); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.4 points (-10.8 to -0.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -11.2 points (-14.7 to -7.5); P4 ready at the winning moment: Knocks out their strongest -2.7 points (-5.7 to -0.6); P5 plan reached in time: Knocks out their strongest -3.2 points (-6.5 to -0.9)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -7.0 points (-8.2 to -5.8); P2 both Glimmora had their turn -13.7 points (-15.7 to -11.7); P2 the first Glimmora placed had its turn -5.0 points (-6.0 to -4.0); P2 the second Glimmora placed had its turn -15.6 points (-17.1 to -14.0); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -11.0 points (-13.7 to -8.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -16.3 points (-18.5 to -14.1); P4 ready at the winning moment: Knocks out their strongest -2.2 points (-3.6 to -1.1); P4 the moment came and Kingambit was never ready in the deal +2.3 points (+1.2 to +3.6); P5 plan reached in time: Knocks out their strongest -3.0 points (-4.5 to -1.7)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn -5.8 points (-6.4 to -5.3); P2 both Glimmora had their turn -6.2 points (-6.7 to -5.7); P2 the first Glimmora placed had its turn -1.8 points (-2.3 to -1.3); P2 the second Glimmora placed had its turn -10.2 points (-10.8 to -9.6); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -8.3 points (-8.9 to -7.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -19.3 points (-19.9 to -18.6); P4 ready at the winning moment: Knocks out their strongest -4.7 points (-5.1 to -4.3); P4 ready at the winning moment: Wins outright (a lower bound) -4.7 points (-5.1 to -4.3); P4 the moment came and Kingambit was never ready in the deal +1.6 points (+1.1 to +2.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.6 points (+3.1 to +4.0); P5 plan reached in time: Knocks out their strongest -5.2 points (-5.6 to -4.8); P5 plan reached in time: Wins outright (a lower bound) -5.2 points (-5.6 to -4.8)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn -7.9 points (-8.3 to -7.4); P2 both Glimmora had their turn -11.8 points (-12.5 to -11.2); P2 the first Glimmora placed had its turn -7.0 points (-7.4 to -6.5); P2 the second Glimmora placed had its turn -12.8 points (-13.4 to -12.1); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.9 points (-14.5 to -13.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -23.3 points (-24.0 to -22.6); P4 ready at the winning moment: Knocks out their strongest -8.5 points (-9.0 to -8.0); P4 the moment came and Kingambit was never ready in the deal +2.1 points (+1.5 to +2.7); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +7.0 points (+6.5 to +7.4); P5 plan reached in time: Knocks out their strongest -9.1 points (-9.6 to -8.6)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn -5.7 points (-6.1 to -5.3); P2 both Glimmora had their turn -21.3 points (-22.0 to -20.6); P2 the first Glimmora placed had its turn -4.4 points (-4.8 to -4.0); P2 the second Glimmora placed had its turn -22.7 points (-23.4 to -22.0); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -3.0 points (-3.4 to -2.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.8 points (-15.3 to -14.2); P4 ready at the winning moment: Knocks out their strongest -11.2 points (-11.8 to -10.6); P4 ready at the winning moment: Wins outright (a lower bound) -11.2 points (-11.8 to -10.6); P4 not ready, ready 1 turn late +1.2 points (+0.9 to +1.5); P4 the moment came and Kingambit was never ready in the deal +1.5 points (+1.0 to +2.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +8.5 points (+8.1 to +9.0); P5 plan reached in time: Knocks out their strongest -10.0 points (-10.6 to -9.4); P5 plan reached in time: Wins outright (a lower bound) -10.0 points (-10.6 to -9.4)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn -5.9 points (-6.4 to -5.3); P2 both Glimmora had their turn -6.2 points (-6.7 to -5.7); P2 the first Glimmora placed had its turn -1.8 points (-2.3 to -1.3); P2 the second Glimmora placed had its turn -10.2 points (-10.8 to -9.7); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -9.3 points (-9.9 to -8.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -19.3 points (-19.9 to -18.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +1.5 points (+1.3 to +1.8)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn -5.5 points (-5.9 to -5.1); P2 both Glimmora had their turn -16.6 points (-17.2 to -15.9); P2 the first Glimmora placed had its turn -4.4 points (-4.8 to -4.0); P2 the second Glimmora placed had its turn -17.8 points (-18.4 to -17.1); P3 plan broken in front, cause: Pawniard forced to lead -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -29.4 points (-30.1 to -28.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -24.6 points (-25.3 to -24.0); P4 ready at the winning moment: Knocks out their strongest +6.5 points (+6.0 to +6.9); P4 ready at the winning moment: Wins outright (a lower bound) +6.5 points (+6.0 to +6.9); P4 the moment came and Kingambit was never ready in the deal -9.1 points (-9.5 to -8.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +2.4 points (+2.1 to +2.7); P5 plan reached in time: Knocks out their strongest +6.7 points (+6.2 to +7.1); P5 plan reached in time: Wins outright (a lower bound) +6.7 points (+6.2 to +7.1)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): G3 Pawniard in play, own turn 5 +4.0 points; G3 Glimmet in play, own turn 5 +1.5 points; G3 Regigigas in play, own turn 1 +21.4 points; G3 Regigigas in play, own turn 2 +17.8 points; G3 Regigigas in play, own turn 3 +15.3 points; G3 Regigigas in play, own turn 4 +13.8 points; G3 Regigigas in play, own turn 5 +13.0 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.6 points; K1 Pawniard line in play (end of own turn t), own turn 1 -5.4 points; K1 Pawniard line in play (end of own turn t), own turn 2 -9.0 points; K1 Pawniard line in play (end of own turn t), own turn 3 -10.8 points; K1 Pawniard line in play (end of own turn t), own turn 4 -11.9 points; K1 Pawniard line in play (end of own turn t), own turn 5 -12.5 points; K2 Kingambit in play, own turn 2 -3.0 points; K2 Kingambit in play, own turn 3 -7.6 points; K2 Kingambit in play, own turn 4 -12.0 points; K2 Kingambit in play, own turn 5 -16.5 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 -1.5; K3.by4 -1.9; K3.by5 -2.4; K3.by6 -3.5; K3.by7 -5.6; K3.by8 -6.9; K3.never +4.9; K3.k0 -1.7; K3.k2 -2.4; K4 -5.2; K5 -1.8; C-his, seat-matched: K3.by3 -1.7; K3.by4 -2.2; K3.by5 -2.7; K3.by6 -2.9; K3.by7 -7.8; K3.by8 -7.8; K3.never +3.9; K3.k0 -2.1; K3.k2 -1.8; K4 -5.7; K5 -1.7; C-bot: K3.by3 -1.6; K3.by4 -2.0; K3.by5 -2.6; K3.by6 -3.7; K3.by7 -5.1; K3.by8 -6.1; K3.never +5.4; K3.k0 -1.9; K3.k2 -1.1; K3.k3p -3.2; K4 -4.2; K5 -2.2; C-fixed fast: K3.by4 -1.5; K3.by5 -5.1; K3.by6 -6.0; K3.by7 -6.0; K3.by8 -6.0; K3.never +6.0; K3.k3p -5.4; K4 -6.0; K5 -6.0; C-fixed medium: K3.by3 -1.6; K3.by4 -2.1; K3.by5 -5.5; K3.by6 -13.3; K3.by7 -13.8; K3.by8 -13.8; K3.never +13.8; K3.k0 -1.6; K3.k3p -11.5; K4 -12.2; K5 -4.5; C-fixed slow: K3.by3 -1.6; K3.by4 -1.6; K3.by5 -2.8; K3.by6 -3.6; K3.by7 -10.2; K3.by8 -17.8; K3.never +17.8; K3.k0 -1.6; K3.k2 -2.0; K3.k3p -14.2; K4 -16.2; K5 -2.5; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.5; K3.by5 -5.2; K3.by6 -6.1; K3.by7 -6.1; K3.by8 -6.1; K3.never +6.1; K3.k3p -5.5; K4 -6.1; K5 -6.0; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.6; K3.by4 -1.6; K3.by5 -2.8; K3.by6 -3.6; K3.by7 -14.5; K3.by8 -30.6; K3.by9 -29.0; K3.by10 -25.3; K3.never +25.3; K3.k0 -1.6; K3.k2 -2.0; K3.k3p -21.6; K4 -23.6; K5 -2.4.
Not valued here (changed cards the script never plays: they count as blanks): none.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Heavy Helmet B1 219 +1 Regigigas B3 134 (card-list id 48e17562f3c0)

Changes: ['-1 Heavy Helmet B1 219', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 284,825; the valuation and the fallback rule disagree at 113,076 of 284,825 Copycat decisions (39.7%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 48.9% (48.5-49.4) | 48.7% (48.2-49.1) | 48.8% (48.5-49.1) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 87.0% / 96.4% [74-95] | 78.2% / 91.8% [63-90] | 82.6% / 94.1% [68-92] |
| P2 both Glimmora had their turn | 28.5% / 66.1% [20-36] | 25.2% / 67.3% [17-34] | 26.8% / 66.7% [19-34] |
| P2 the first Glimmora placed had its turn | 84.5% / 92.5% [72-93] | 72.6% / 83.5% [57-86] | 78.5% / 88.0% [65-89] |
| P2 the second Glimmora placed had its turn | 31.0% / 66.0% [22-40] | 30.7% / 67.5% [21-40] | 30.9% / 66.7% [22-39] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9] | 8.5% [8-9] | 8.6% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.1% / 49.3% [1-2] | 2.1% / 55.9% [1-3] | 1.6% / 52.6% [1-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 14.7% / 58.0% [13-17] | 19.1% / 65.1% [15-23] | 16.9% / 61.6% [14-20] |
| P4 ready at the winning moment: Knocks out their strongest | 14.2% / 39.7% [3-27] | 10.4% / 39.1% [2-20] | 12.3% / 39.4% [3-23] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.1% / 28.6% [0-9] | 2.1% / 30.8% [0-6] | 2.6% / 29.7% [0-8] |
| P4 not ready, ready 1 turn late | 4.9% / 47.4% [0-13] | 4.1% / 51.0% [0-10] | 4.5% / 49.2% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.3% / 43.9% [0-4] | 1.6% / 48.5% [0-5] | 1.4% / 46.2% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 8.1% / 50.6% [0-20] | 9.2% / 56.1% [0-22] | 8.6% / 53.3% [0-21] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.1% / 54.6% [8-54] | 27.8% / 56.5% [9-52] | 28.4% / 55.5% [8-52] |
| P5 plan reached in time: Knocks out their strongest | 20.3% / 62.9% [7-37] | 16.1% / 63.0% [5-29] | 18.2% / 62.9% [6-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.4% / 46.0% [0-10] | 2.6% / 49.5% [0-8] | 3.0% / 47.7% [0-9] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 49.8% of 2839 [23-73] | 41.3% of 2527 [22-64] | 45.8% of 5366 [24-69] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.8% of 2839 [0-41] | 8.2% of 2527 [0-37] | 9.6% of 5366 [0-39] |
| P4 not ready, ready 1 turn late | 17.2% of 2839 [0-57] | 16.1% of 2527 [0-50] | 16.7% of 5366 [0-54] |
| P4 not ready, ready 2 or more turns late | 4.6% of 2839 [0-17] | 6.2% of 2527 [0-22] | 5.4% of 5366 [0-19] |
| P4 the moment came and Kingambit was never ready in the deal | 28.4% of 2839 [0-52] | 36.4% of 2527 [0-63] | 32.1% of 5366 [0-57] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: -8.9 points (-12.3 to -5.7); P2.g2: -10.4 points (-13.8 to -7.2); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -4.4 points (-9.4 to -1.2); P3.grimer_muk: -13.2 points (-17.2 to -9.6); P4.nomoment: -1.9 points (-3.4 to -0.8).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.2% / 96.0% [68-95] | 87.6% / 95.9% [77-95] | 86.4% / 96.0% [76-94] |
| P2 both Glimmora had their turn | 28.1% / 60.8% [18-37] | 25.6% / 83.0% [16-44] | 26.9% / 71.9% [19-36] |
| P2 the first Glimmora placed had its turn | 82.7% / 92.4% [66-94] | 84.6% / 88.1% [73-94] | 83.6% / 90.3% [74-91] |
| P2 the second Glimmora placed had its turn | 30.6% / 60.8% [20-41] | 28.6% / 79.0% [17-48] | 29.6% / 69.9% [21-40] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9] | 8.5% [8-9] | 8.6% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.1% / 44.2% [0-2] | 2.8% / 80.8% [0-5] | 2.0% / 62.5% [1-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 14.6% / 53.2% [12-18] | 19.5% / 87.4% [11-26] | 17.1% / 70.3% [13-21] |
| P4 ready at the winning moment: Knocks out their strongest | 17.3% / 39.7% [2-34] | 4.2% / 56.1% [0-12] | 10.7% / 47.9% [3-22] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.6% / 27.0% [0-14] | 0.0% / 51.9% [0-0] | 2.3% / 39.5% [0-9] |
| P4 not ready, ready 1 turn late | 6.4% / 42.0% [0-16] | 0.0% / 79.2% [0-0] | 3.2% / 60.6% [0-10] |
| P4 not ready, ready 2 or more turns late | 1.8% / 37.4% [0-6] | 0.0% / 79.2% [0-0] | 0.9% / 58.3% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 11.4% / 47.0% [0-27] | 0.0% / 79.2% [0-0] | 5.7% / 63.1% [0-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 27.5% / 49.9% [5-57] | 16.7% / 68.6% [0-44] | 22.1% / 59.3% [7-43] |
| P5 plan reached in time: Knocks out their strongest | 25.5% / 61.1% [8-45] | 4.2% / 83.3% [0-12] | 14.8% / 72.2% [5-30] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.0% / 40.6% [0-15] | 0.0% / 79.2% [0-0] | 2.5% / 59.9% [0-10] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 46.8% of 3690 [15-68] | 100.0% of 416 [100-100] | 52.2% of 4106 [27-77] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.5% of 3690 [0-47] | 0.0% of 416 [0-0] | 11.2% of 4106 [0-39] |
| P4 not ready, ready 1 turn late | 17.3% of 3690 [0-65] | 0.0% of 416 [0-0] | 15.5% of 4106 [0-46] |
| P4 not ready, ready 2 or more turns late | 5.0% of 3690 [0-20] | 0.0% of 416 [0-0] | 4.5% of 4106 [0-14] |
| P4 the moment came and Kingambit was never ready in the deal | 31.0% of 3690 [0-57] | 0.0% of 416 [0-0] | 27.8% of 4106 [0-51] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -1.1 points (-2.4 to -0.4); P2.both: -8.4 points (-12.0 to -5.6); P2.g2: -9.6 points (-13.2 to -6.7); P3.pawn_lead: -4.2 points (-4.6 to -3.8); P3.pawn_promo: -5.7 points (-13.1 to -0.8); P3.grimer_muk: -14.3 points (-19.0 to -9.4).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.4% / 90.6% [86-92] | 81.4% / 83.1% [77-86] | 85.4% / 86.9% [82-89] |
| P2 both Glimmora had their turn | 30.1% / 37.5% [27-33] | 25.1% / 33.4% [22-28] | 27.6% / 35.5% [24-31] |
| P2 the first Glimmora placed had its turn | 84.7% / 85.0% [80-89] | 73.6% / 73.9% [68-79] | 79.2% / 79.5% [74-84] |
| P2 the second Glimmora placed had its turn | 34.8% / 41.5% [32-38] | 32.9% / 39.8% [30-36] | 33.8% / 40.6% [31-36] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9] | 8.5% [8-9] | 8.6% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.2% / 13.6% [2-3] | 3.8% / 16.2% [3-5] | 3.0% / 14.9% [2-4] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 15.9% / 26.0% [15-17] | 21.6% / 32.2% [20-23] | 18.8% / 29.1% [17-20] |
| P4 ready at the winning moment: Knocks out their strongest | 7.6% / 13.9% [4-12] | 6.7% / 14.1% [4-10] | 7.1% / 14.0% [4-11] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.2% / 6.5% [0-1] | 0.5% / 7.9% [0-2] | 0.4% / 7.2% [0-1] |
| P4 not ready, ready 1 turn late | 5.3% / 13.4% [3-8] | 4.3% / 14.1% [2-7] | 4.8% / 13.7% [2-7] |
| P4 not ready, ready 2 or more turns late | 1.9% / 10.0% [1-3] | 2.1% / 11.8% [1-4] | 2.0% / 10.9% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 8.2% / 16.4% [4-13] | 9.4% / 19.1% [5-15] | 8.8% / 17.7% [4-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.0% / 75.3% [57-80] | 67.7% / 75.1% [56-78] | 68.3% / 75.2% [57-79] |
| P5 plan reached in time: Knocks out their strongest | 14.7% / 22.8% [8-22] | 13.2% / 22.9% [8-20] | 13.9% / 22.9% [8-21] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.4% / 8.6% [0-1] | 0.6% / 10.4% [0-2] | 0.5% / 9.5% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 33.0% of 2288 [21-47] | 29.8% of 2255 [21-40] | 31.5% of 4543 [21-43] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.1% of 2288 [0-4] | 2.4% of 2255 [0-8] | 1.7% of 4543 [0-5] |
| P4 not ready, ready 1 turn late | 23.0% of 2288 [15-32] | 19.2% of 2255 [14-25] | 21.1% of 4543 [14-28] |
| P4 not ready, ready 2 or more turns late | 8.1% of 2288 [4-13] | 9.3% of 2255 [4-14] | 8.7% of 4543 [4-13] |
| P4 the moment came and Kingambit was never ready in the deal | 35.9% of 2288 [23-50] | 41.6% of 2255 [29-54] | 38.7% of 4543 [26-52] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -1.6 points (-2.7 to -0.6); P2.both: -9.4 points (-11.3 to -7.6); P2.g2: -11.4 points (-13.0 to -9.7); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -12.9 points (-15.7 to -10.0); P3.grimer_muk: -20.7 points (-23.1 to -18.2); P4.nomoment: -1.1 points (-1.7 to -0.4).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.4% [81-82, Wilson] | 55.4% [54-56, Wilson] | 68.4% [68-69, Wilson] |
| P2 both Glimmora had their turn | 24.8% [24-26, Wilson] | 9.6% [9-10, Wilson] | 17.2% [17-18, Wilson] |
| P2 the first Glimmora placed had its turn | 77.2% [76-78, Wilson] | 41.3% [40-42, Wilson] | 59.3% [59-60, Wilson] |
| P2 the second Glimmora placed had its turn | 29.0% [28-30, Wilson] | 23.7% [23-25, Wilson] | 26.4% [26-27, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9, Wilson] | 8.5% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 8.6% [8-9, Wilson] | 11.3% [11-12, Wilson] | 10.0% [10-10, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 30.9% [30-32, Wilson] | 37.0% [36-38, Wilson] | 33.9% [33-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 16.8% [16-18, Wilson] | 6.3% [6-7, Wilson] | 11.5% [11-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 16.8% [16-18, Wilson] | 6.3% [6-7, Wilson] | 11.5% [11-12, Wilson] |
| P4 not ready, ready 1 turn late | 2.8% [3-3, Wilson] | 1.1% [1-1, Wilson] | 2.0% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 25.0% [24-26, Wilson] | 20.0% [19-21, Wilson] | 22.5% [22-23, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 55.4% [54-56, Wilson] | 72.6% [72-73, Wilson] | 64.0% [63-65, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 19.6% [19-20, Wilson] | 7.4% [7-8, Wilson] | 13.5% [13-14, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 19.6% [19-20, Wilson] | 7.4% [7-8, Wilson] | 13.5% [13-14, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 37.6% of 4457 [36-39, Wilson] | 22.8% of 2744 [21-24, Wilson] | 32.0% of 7201 [31-33, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 37.6% of 4457 [36-39, Wilson] | 22.8% of 2744 [21-24, Wilson] | 32.0% of 7201 [31-33, Wilson] |
| P4 not ready, ready 1 turn late | 6.4% of 4457 [6-7, Wilson] | 4.2% of 2744 [3-5, Wilson] | 5.5% of 7201 [5-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4457 [0-0, Wilson] | 0.0% of 2744 [0-0, Wilson] | 0.0% of 7201 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 56.0% of 4457 [55-57, Wilson] | 73.0% of 2744 [71-75, Wilson] | 62.5% of 7201 [61-64, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.both: -1.0 points (-1.5 to -0.6); P2.g1: +4.3 points (+3.8 to +4.8); P2.g2: -4.3 points (-4.9 to -3.8); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -10.4 points (-10.9 to -9.8); P3.grimer_muk: -22.1 points (-22.7 to -21.4); P4.never: +1.3 points (+0.8 to +1.8); P4.nomoment: -2.7 points (-3.2 to -2.3); P5.ko: +1.4 points (+1.0 to +1.8); P5.win: +1.4 points (+1.0 to +1.8).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.5% [89-90, Wilson] | 80.5% [80-81, Wilson] | 85.0% [85-86, Wilson] |
| P2 both Glimmora had their turn | 31.6% [31-32, Wilson] | 24.7% [24-26, Wilson] | 28.1% [27-29, Wilson] |
| P2 the first Glimmora placed had its turn | 87.4% [87-88, Wilson] | 77.3% [77-78, Wilson] | 82.3% [82-83, Wilson] |
| P2 the second Glimmora placed had its turn | 33.7% [33-35, Wilson] | 27.9% [27-29, Wilson] | 30.8% [30-31, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9, Wilson] | 8.5% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 5.8% [5-6, Wilson] | 9.0% [8-10, Wilson] | 7.4% [7-8, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 23.6% [23-24, Wilson] | 32.6% [32-34, Wilson] | 28.1% [27-29, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 28.4% [27-29, Wilson] | 17.4% [17-18, Wilson] | 22.9% [22-23, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 3.2% [3-4, Wilson] | 2.6% [2-3, Wilson] | 2.9% [3-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 21.7% [21-22, Wilson] | 25.1% [24-26, Wilson] | 23.4% [23-24, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 46.8% [46-48, Wilson] | 54.9% [54-56, Wilson] | 50.8% [50-52, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 31.6% [31-32, Wilson] | 20.0% [19-21, Wilson] | 25.8% [25-26, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 53.3% of 5323 [52-55, Wilson] | 38.5% of 4512 [37-40, Wilson] | 46.5% of 9835 [46-47, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5323 [0-0, Wilson] | 0.0% of 4512 [0-0, Wilson] | 0.0% of 9835 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 6.0% of 5323 [5-7, Wilson] | 5.8% of 4512 [5-7, Wilson] | 5.9% of 9835 [5-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5323 [0-0, Wilson] | 0.0% of 4512 [0-0, Wilson] | 0.0% of 9835 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 40.7% of 5323 [39-42, Wilson] | 55.7% of 4512 [54-57, Wilson] | 47.6% of 9835 [47-49, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: -1.0 points (-1.4 to -0.7); P2.both: -5.9 points (-6.4 to -5.3); P2.g2: -7.1 points (-7.7 to -6.5); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -16.5 points (-17.1 to -15.9); P3.grimer_muk: -28.6 points (-29.3 to -27.9); P4.ko: +1.1 points (+0.7 to +1.6); P4.never: -1.5 points (-2.0 to -1.0); P5.ko: +1.6 points (+1.2 to +2.1).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.5% [95-96, Wilson] | 89.5% [89-90, Wilson] | 92.5% [92-93, Wilson] |
| P2 both Glimmora had their turn | 52.3% [51-53, Wilson] | 44.6% [44-46, Wilson] | 48.4% [48-49, Wilson] |
| P2 the first Glimmora placed had its turn | 91.9% [91-92, Wilson] | 83.8% [83-84, Wilson] | 87.8% [87-88, Wilson] |
| P2 the second Glimmora placed had its turn | 55.9% [55-57, Wilson] | 50.4% [49-51, Wilson] | 53.1% [52-54, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9, Wilson] | 8.5% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.2% [1-1, Wilson] | 2.7% [2-3, Wilson] | 2.0% [2-2, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 13.6% [13-14, Wilson] | 18.8% [18-20, Wilson] | 16.2% [16-17, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 50.5% [49-51, Wilson] | 42.3% [41-43, Wilson] | 46.4% [46-47, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 50.5% [49-51, Wilson] | 42.3% [41-43, Wilson] | 46.4% [46-47, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 4.4% [4-5, Wilson] | 2.2% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 9.2% [9-10, Wilson] | 8.4% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 40.3% [39-41, Wilson] | 44.9% [44-46, Wilson] | 42.6% [42-43, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 50.5% [49-51, Wilson] | 46.8% [46-48, Wilson] | 48.6% [48-49, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 50.5% [49-51, Wilson] | 46.8% [46-48, Wilson] | 48.6% [48-49, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 84.5% of 5969 [84-85, Wilson] | 76.8% of 5512 [76-78, Wilson] | 80.8% of 11481 [80-82, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 84.5% of 5969 [84-85, Wilson] | 76.8% of 5512 [76-78, Wilson] | 80.8% of 11481 [80-82, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5969 [0-0, Wilson] | 8.1% of 5512 [7-9, Wilson] | 3.9% of 11481 [4-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5969 [0-0, Wilson] | 0.0% of 5512 [0-0, Wilson] | 0.0% of 11481 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 15.5% of 5969 [15-16, Wilson] | 15.2% of 5512 [14-16, Wilson] | 15.3% of 11481 [15-16, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.both: -13.8 points (-14.5 to -13.1); P2.g1: +1.9 points (+1.6 to +2.2); P2.g2: -16.0 points (-16.7 to -15.3); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -4.8 points (-5.1 to -4.4); P3.grimer_muk: -19.6 points (-20.2 to -19.0); P4.ko: +1.9 points (+1.4 to +2.4); P4.win: +1.9 points (+1.4 to +2.4); P4.never: -5.2 points (-5.6 to -4.8); P4.nomoment: +3.1 points (+2.7 to +3.6); P5.ko: +2.0 points (+1.5 to +2.5); P5.win: +2.0 points (+1.5 to +2.5).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.6% [81-82, Wilson] | 55.6% [55-57, Wilson] | 68.6% [68-69, Wilson] |
| P2 both Glimmora had their turn | 25.3% [24-26, Wilson] | 9.6% [9-10, Wilson] | 17.5% [17-18, Wilson] |
| P2 the first Glimmora placed had its turn | 77.2% [76-78, Wilson] | 41.3% [40-42, Wilson] | 59.3% [59-60, Wilson] |
| P2 the second Glimmora placed had its turn | 29.6% [29-31, Wilson] | 23.9% [23-25, Wilson] | 26.8% [26-27, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9, Wilson] | 8.5% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 9.5% [9-10, Wilson] | 11.7% [11-12, Wilson] | 10.6% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 30.9% [30-32, Wilson] | 37.0% [36-38, Wilson] | 33.9% [33-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 6.1% [6-7, Wilson] | 1.9% [2-2, Wilson] | 4.0% [4-4, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.1% [6-7, Wilson] | 1.9% [2-2, Wilson] | 4.0% [4-4, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.2% [3-4, Wilson] | 1.9% [2-2, Wilson] | 2.6% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.7% [90-91, Wilson] | 96.2% [96-97, Wilson] | 93.5% [93-94, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 6.1% [6-7, Wilson] | 1.9% [2-2, Wilson] | 4.0% [4-4, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.1% [6-7, Wilson] | 1.9% [2-2, Wilson] | 4.0% [4-4, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 65.3% of 929 [62-68, Wilson] | 49.9% of 377 [45-55, Wilson] | 60.9% of 1306 [58-63, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 65.3% of 929 [62-68, Wilson] | 49.9% of 377 [45-55, Wilson] | 60.9% of 1306 [58-63, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 929 [0-0, Wilson] | 0.0% of 377 [0-1, Wilson] | 0.0% of 1306 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 929 [0-0, Wilson] | 0.0% of 377 [0-1, Wilson] | 0.0% of 1306 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 34.7% of 929 [32-38, Wilson] | 50.1% of 377 [45-55, Wilson] | 39.1% of 1306 [37-42, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.1 points (+0.6 to +1.5); P2.g1: +4.3 points (+3.8 to +4.8); P2.g2: -4.2 points (-4.7 to -3.6); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -11.2 points (-11.8 to -10.7); P3.grimer_muk: -22.1 points (-22.7 to -21.4); P4.ko: +1.7 points (+1.5 to +2.0); P4.win: +1.7 points (+1.5 to +2.0); P4.nomoment: -1.2 points (-1.5 to -1.0); P5.ko: +1.7 points (+1.5 to +2.0); P5.win: +1.7 points (+1.5 to +2.0).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.7% [95-96, Wilson] | 89.9% [89-91, Wilson] | 92.8% [92-93, Wilson] |
| P2 both Glimmora had their turn | 65.0% [64-66, Wilson] | 53.5% [53-54, Wilson] | 59.2% [59-60, Wilson] |
| P2 the first Glimmora placed had its turn | 91.9% [91-92, Wilson] | 83.8% [83-84, Wilson] | 87.8% [87-88, Wilson] |
| P2 the second Glimmora placed had its turn | 68.8% [68-70, Wilson] | 59.7% [59-61, Wilson] | 64.2% [64-65, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.7% [8-9, Wilson] | 8.5% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.0% [2-2, Wilson] | 4.2% [4-5, Wilson] | 3.1% [3-3, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 13.8% [13-14, Wilson] | 19.2% [18-20, Wilson] | 16.5% [16-17, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 18.2% [18-19, Wilson] | 16.1% [15-17, Wilson] | 17.2% [17-18, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 18.2% [18-19, Wilson] | 16.1% [15-17, Wilson] | 17.2% [17-18, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.1% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.3% [2-3, Wilson] | 2.4% [2-3, Wilson] | 2.4% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 79.4% [79-80, Wilson] | 81.4% [81-82, Wilson] | 80.4% [80-81, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 18.2% [18-19, Wilson] | 16.2% [16-17, Wilson] | 17.2% [17-18, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 18.2% [18-19, Wilson] | 16.2% [16-17, Wilson] | 17.2% [17-18, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 88.8% of 2056 [87-90, Wilson] | 86.6% of 1864 [85-88, Wilson] | 87.7% of 3920 [87-89, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 88.8% of 2056 [87-90, Wilson] | 86.6% of 1864 [85-88, Wilson] | 87.7% of 3920 [87-89, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 2056 [0-0, Wilson] | 0.5% of 1864 [0-1, Wilson] | 0.2% of 3920 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 2056 [0-0, Wilson] | 0.0% of 1864 [0-0, Wilson] | 0.0% of 3920 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 11.2% of 2056 [10-13, Wilson] | 12.9% of 1864 [11-15, Wilson] | 12.0% of 3920 [11-13, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.both: -5.0 points (-5.7 to -4.4); P2.g1: +1.9 points (+1.6 to +2.2); P2.g2: -6.9 points (-7.5 to -6.3); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -31.9 points (-32.5 to -31.2); P3.grimer_muk: -30.5 points (-31.2 to -29.8); P4.ko: +10.7 points (+10.2 to +11.1); P4.win: +10.7 points (+10.2 to +11.1); P4.never: -9.3 points (-9.7 to -8.9); P4.nomoment: -1.3 points (-1.5 to -1.0); P5.ko: +10.6 points (+10.2 to +11.0); P5.win: +10.6 points (+10.2 to +11.0).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.5% (27.1-27.9) | 27.0% (26.7-27.4) | 27.3% (27.0-27.5) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 52.0% (51.5-52.4) | 51.8% (51.3-52.2) | 51.9% (51.6-52.2) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 61.9% (61.5-62.3) | 61.7% (61.3-62.1) | 61.8% (61.5-62.1) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 66.3% (65.9-66.7) | 66.3% (65.9-66.7) | 66.3% (66.0-66.6) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 68.4% (68.0-68.8) | 68.4% (68.0-68.8) | 68.4% (68.1-68.7) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 69.4% (69.0-69.8) | 69.2% (68.8-69.6) | 69.3% (69.0-69.6) |
| K2 Kingambit in play, own turn 2 | 10.0% (9.7-10.2) | 10.0% (9.7-10.3) | 10.0% (9.8-10.2) |
| K2 Kingambit in play, own turn 3 | 19.2% (18.8-19.5) | 19.2% (18.8-19.5) | 19.2% (18.9-19.4) |
| K2 Kingambit in play, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| K2 Kingambit in play, own turn 5 | 41.0% (40.6-41.4) | 40.7% (40.3-41.2) | 40.9% (40.6-41.2) |
| K2 Kingambit in play, own turn 6 | 51.6% (51.1-52.0) | 51.3% (50.8-51.7) | 51.4% (51.1-51.7) |
| K6 Muk and Regigigas both in play, own turn 3 | 25.9% (25.5-26.3) | 26.0% (25.6-26.4) | 26.0% (25.7-26.2) |
| K6 Muk and Regigigas both in play, own turn 4 | 33.4% (33.0-33.8) | 33.3% (32.9-33.7) | 33.4% (33.1-33.6) |
| K6 Muk and Regigigas both in play, own turn 5 | 39.1% (38.7-39.5) | 39.0% (38.5-39.4) | 39.0% (38.7-39.4) |
| G3 Pawniard in play, own turn 1 | 52.0% (51.5-52.4) | 51.8% (51.3-52.2) | 51.9% (51.6-52.2) |
| G3 Pawniard in play, own turn 2 | 51.9% (51.5-52.3) | 51.7% (51.3-52.2) | 51.8% (51.5-52.1) |
| G3 Pawniard in play, own turn 3 | 47.1% (46.7-47.6) | 47.1% (46.7-47.6) | 47.1% (46.8-47.4) |
| G3 Pawniard in play, own turn 4 | 38.8% (38.4-39.3) | 38.7% (38.3-39.2) | 38.8% (38.5-39.1) |
| G3 Pawniard in play, own turn 5 | 28.4% (28.0-28.8) | 28.5% (28.1-28.9) | 28.4% (28.2-28.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 10.0% (9.7-10.2) | 10.0% (9.7-10.3) | 10.0% (9.8-10.2) |
| G3 Kingambit in play, own turn 3 | 19.2% (18.8-19.5) | 19.2% (18.8-19.5) | 19.2% (18.9-19.4) |
| G3 Kingambit in play, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| G3 Kingambit in play, own turn 5 | 41.0% (40.6-41.4) | 40.7% (40.3-41.2) | 40.9% (40.6-41.2) |
| G3 Alolan Grimer in play, own turn 1 | 49.6% (49.1-50.0) | 49.8% (49.4-50.3) | 49.7% (49.4-50.0) |
| G3 Alolan Grimer in play, own turn 2 | 38.9% (38.5-39.4) | 39.0% (38.6-39.4) | 39.0% (38.7-39.3) |
| G3 Alolan Grimer in play, own turn 3 | 32.0% (31.6-32.4) | 31.9% (31.5-32.4) | 32.0% (31.7-32.3) |
| G3 Alolan Grimer in play, own turn 4 | 25.5% (25.1-25.9) | 25.7% (25.4-26.1) | 25.6% (25.3-25.9) |
| G3 Alolan Grimer in play, own turn 5 | 20.0% (19.6-20.4) | 20.3% (19.9-20.6) | 20.1% (19.9-20.4) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 18.8% (18.4-19.1) | 18.8% (18.5-19.2) | 18.8% (18.6-19.0) |
| G3 Alolan Muk in play, own turn 3 | 29.1% (28.7-29.5) | 29.4% (29.0-29.8) | 29.2% (29.0-29.5) |
| G3 Alolan Muk in play, own turn 4 | 37.1% (36.7-37.6) | 37.1% (36.6-37.5) | 37.1% (36.8-37.4) |
| G3 Alolan Muk in play, own turn 5 | 43.3% (42.9-43.7) | 43.1% (42.7-43.6) | 43.2% (42.9-43.5) |
| G3 Glimmet in play, own turn 1 | 78.0% (77.6-78.3) | 78.2% (77.8-78.6) | 78.1% (77.8-78.3) |
| G3 Glimmet in play, own turn 2 | 45.2% (44.7-45.6) | 45.1% (44.6-45.5) | 45.1% (44.8-45.4) |
| G3 Glimmet in play, own turn 3 | 32.7% (32.3-33.1) | 32.6% (32.2-33.0) | 32.6% (32.3-32.9) |
| G3 Glimmet in play, own turn 4 | 22.1% (21.7-22.5) | 22.3% (22.0-22.7) | 22.2% (21.9-22.5) |
| G3 Glimmet in play, own turn 5 | 13.5% (13.2-13.8) | 13.3% (13.0-13.6) | 13.4% (13.2-13.6) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 59.8% (59.3-60.2) | 60.1% (59.7-60.5) | 59.9% (59.6-60.2) |
| G3 Glimmora in play, own turn 3 | 75.5% (75.1-75.9) | 75.9% (75.5-76.2) | 75.7% (75.4-75.9) |
| G3 Glimmora in play, own turn 4 | 84.1% (83.8-84.5) | 84.3% (84.0-84.7) | 84.2% (84.0-84.5) |
| G3 Glimmora in play, own turn 5 | 88.8% (88.5-89.1) | 89.2% (88.9-89.5) | 89.0% (88.8-89.2) |
| G3 Regigigas in play, own turn 1 | 78.6% (78.2-78.9) | 78.3% (77.9-78.7) | 78.5% (78.2-78.7) |
| G3 Regigigas in play, own turn 2 | 87.9% (87.6-88.2) | 87.6% (87.4-87.9) | 87.8% (87.6-88.0) |
| G3 Regigigas in play, own turn 3 | 91.6% (91.3-91.8) | 91.5% (91.2-91.7) | 91.5% (91.4-91.7) |
| G3 Regigigas in play, own turn 4 | 93.2% (93.0-93.4) | 93.2% (92.9-93.4) | 93.2% (93.0-93.3) |
| G3 Regigigas in play, own turn 5 | 93.8% (93.6-94.0) | 93.8% (93.6-94.0) | 93.8% (93.6-93.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 73.3% (72.9-73.7) | 73.4% (73.0-73.8) | 73.3% (73.1-73.6) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 87.7% (87.4-88.0) | 87.9% (87.6-88.2) | 87.8% (87.6-88.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 94.4% (94.2-94.6) | 94.4% (94.2-94.6) | 94.4% (94.3-94.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 97.5% (97.4-97.7) | 97.5% (97.4-97.6) | 97.5% (97.4-97.6) |
| G4.s2 a Stage 2 in play, own turn 2 | 10.0% (9.7-10.2) | 10.0% (9.7-10.3) | 10.0% (9.8-10.2) |
| G4.s2 a Stage 2 in play, own turn 3 | 19.2% (18.8-19.5) | 19.2% (18.8-19.5) | 19.2% (18.9-19.4) |
| G4.s2 a Stage 2 in play, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| G4.s2 a Stage 2 in play, own turn 5 | 41.0% (40.6-41.4) | 40.7% (40.3-41.2) | 40.9% (40.6-41.2) |
| G5.any3 an empty own turn among turns 1-3 | 23.5% (23.1-23.9) | 22.8% (22.5-23.2) | 23.2% (22.9-23.4) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.0% (9.7-10.3) | 5.0% (4.9-5.1) |
| G6 Kingambit with [DD] attached, own turn 3 | 16.8% (16.5-17.1) | 19.2% (18.8-19.5) | 18.0% (17.7-18.2) |
| G6 Kingambit with [DD] attached, own turn 4 | 29.6% (29.2-30.0) | 29.6% (29.2-30.0) | 29.6% (29.3-29.9) |
| G6 Kingambit with [DD] attached, own turn 5 | 41.0% (40.6-41.4) | 40.7% (40.3-41.2) | 40.9% (40.6-41.2) |
| G5 mean empty own turns in turns 1-5 | 0.762 | 0.757 | 0.759 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.7% / 10.1% [1-2] | 0.9% / 5.0% [1-1] |
| K3.by3 | 2.4% / 11.0% [2-3] | 2.1% / 10.4% [1-3] | 2.2% / 10.7% [1-3] |
| K3.by4 | 2.9% / 11.5% [2-4] | 3.8% / 12.1% [3-5] | 3.3% / 11.8% [2-4] |
| K3.by5 | 4.6% / 13.2% [3-7] | 4.1% / 20.1% [3-6] | 4.3% / 16.7% [3-6] |
| K3.by6 | 4.8% / 21.8% [3-7] | 8.8% / 32.9% [4-16] | 6.8% / 27.3% [4-10] |
| K3.by7 | 11.9% / 36.9% [4-22] | 8.9% / 55.9% [4-16] | 10.4% / 46.4% [4-19] |
| K3.by8 | 12.0% / 60.4% [4-22] | 8.9% / 62.0% [4-16] | 10.5% / 61.2% [4-19] |
| K3.never | 39.6% / 88.0% [16-64] | 38.0% / 91.0% [15-61] | 38.8% / 89.5% [16-62] |
| K3.k0 | 3.1% / 51.5% [2-4] | 2.3% / 55.4% [1-3] | 2.7% / 53.5% [2-4] |
| K3.k1 | 0.0% / 48.4% [0-0] | 0.0% / 53.0% [0-0] | 0.0% / 50.7% [0-0] |
| K3.k2 | 6.5% / 54.9% [0-16] | 5.2% / 58.3% [1-12] | 5.9% / 56.6% [1-14] |
| K3.k3p | 2.3% / 50.7% [0-7] | 1.4% / 54.4% [0-4] | 1.8% / 52.6% [0-5] |
| K4 | 8.8% / 59.0% [1-19] | 6.6% / 61.1% [1-14] | 7.7% / 60.0% [1-17] |
| K5 | 4.7% / 61.4% [3-6] | 5.7% / 59.5% [4-7] | 5.2% / 60.5% [4-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by4: -1.3 points (-1.7 to -0.8); K3.by5: -1.8 points (-2.3 to -1.2); K3.by6: -2.0 points (-2.6 to -1.4); K3.by7: -2.9 points (-5.2 to -1.4); K3.by8: -4.2 points (-9.3 to -1.4); K3.k0: -1.2 points (-1.9 to -0.7); K4: -3.0 points (-7.8 to -0.4); K5: -2.9 points (-3.9 to -2.1).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [2-3] | 1.2% [0-2] |
| K3.by3 | 2.2% / 13.5% [1-3] | 3.0% [2-4] | 2.6% / 8.3% [2-3] |
| K3.by4 | 2.6% / 13.9% [1-4] | 4.1% [3-5] | 3.4% / 9.0% [2-4] |
| K3.by5 | 4.4% / 15.7% [3-7] | 4.4% / 34.5% [3-5] | 4.4% / 25.1% [3-6] |
| K3.by6 | 4.6% / 15.9% [3-7] | 4.5% / 34.6% [4-5] | 4.6% / 25.3% [4-6] |
| K3.by7 | 14.4% / 36.9% [4-28] | 5.1% / 66.8% [4-6] | 9.8% / 51.8% [5-18] |
| K3.by8 | 14.5% / 57.6% [4-28] | 5.1% / 84.1% [4-6] | 9.8% / 70.9% [5-18] |
| K3.never | 42.4% / 85.5% [15-71] | 15.9% / 94.9% [0-42] | 29.1% / 90.2% [12-52] |
| K3.k0 | 2.8% / 46.0% [1-4] | 3.5% / 82.5% [2-5] | 3.1% / 64.3% [2-4] |
| K3.k1 | 0.0% / 43.2% [0-0] | 0.0% / 79.1% [0-0] | 0.0% / 61.1% [0-0] |
| K3.k2 | 8.3% / 51.4% [0-21] | 1.1% / 80.2% [0-2] | 4.7% / 65.8% [1-12] |
| K3.k3p | 3.4% / 46.5% [0-10] | 0.5% / 79.6% [0-2] | 1.9% / 63.0% [0-6] |
| K4 | 11.6% / 56.1% [1-26] | 1.6% / 83.7% [0-3] | 6.6% / 69.9% [1-16] |
| K5 | 5.0% / 53.3% [3-7] | 5.2% / 84.4% [3-6] | 5.1% / 68.8% [4-6] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.1 points (-1.5 to -0.7); K3.by4: -1.4 points (-1.7 to -1.0); K3.by5: -2.0 points (-2.6 to -1.4); K3.by6: -2.3 points (-3.3 to -1.5); K3.by7: -5.8 points (-13.4 to -1.6); K3.by8: -5.8 points (-13.4 to -1.6); K3.k0: -1.3 points (-1.8 to -0.8); K3.k2: -1.0 points (-1.8 to -0.3); K4: -4.5 points (-12.0 to -0.3); K5: -2.9 points (-3.7 to -2.1).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.9% [2-2] | 1.0% [1-1] |
| K3.by3 | 2.6% [2-3] | 2.3% [2-3] | 2.4% [2-3] |
| K3.by4 | 3.2% [3-4] | 3.2% [3-4] | 3.2% [3-4] |
| K3.by5 | 4.1% [3-5] | 4.9% [4-6] | 4.5% [4-5] |
| K3.by6 | 5.4% [4-7] | 6.0% / 10.1% [5-7] | 5.7% / 7.7% [5-7] |
| K3.by7 | 6.5% / 11.0% [5-8] | 6.6% / 16.8% [5-8] | 6.5% / 13.9% [5-8] |
| K3.by8 | 7.2% / 18.4% [5-9] | 7.0% / 19.0% [5-9] | 7.1% / 18.7% [5-9] |
| K3.never | 81.6% / 92.8% [73-89] | 81.0% / 93.0% [73-88] | 81.3% / 92.9% [73-88] |
| K3.k0 | 3.4% / 14.6% [3-4] | 2.4% / 14.4% [2-3] | 2.9% / 14.5% [2-3] |
| K3.k1 | 0.0% / 11.2% [0-0] | 0.0% / 12.0% [0-0] | 0.0% / 11.6% [0-0] |
| K3.k2 | 1.8% / 12.9% [1-3] | 2.4% / 14.4% [1-4] | 2.1% / 13.7% [1-3] |
| K3.k3p | 2.0% / 13.2% [1-4] | 2.2% / 14.2% [1-4] | 2.1% / 13.7% [1-4] |
| K4 | 3.8% / 15.5% [2-6] | 4.6% / 17.1% [3-7] | 4.2% / 16.3% [3-6] |
| K5 | 5.3% / 19.2% [5-6] | 6.7% / 19.2% [6-7] | 6.0% / 19.2% [5-6] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.0 points (-1.2 to -0.8); K3.by4: -1.4 points (-1.6 to -1.1); K3.by5: -2.0 points (-2.3 to -1.7); K3.by6: -3.0 points (-3.6 to -2.4); K3.by7: -4.3 points (-5.6 to -3.1); K3.by8: -5.2 points (-7.3 to -3.6); K3.never: +4.2 points (+2.5 to +6.2); K3.k0: -1.2 points (-1.5 to -1.0); K3.k2: -1.3 points (-1.6 to -1.0); K3.k3p: -2.7 points (-4.7 to -1.2); K4: -4.0 points (-5.9 to -2.4); K5: -3.6 points (-4.0 to -3.2).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.0% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by4 | 1.4% [1-2, Wilson] | 4.3% [4-5, Wilson] | 2.9% [3-3, Wilson] |
| K3.by5 | 6.5% [6-7, Wilson] | 5.3% [5-6, Wilson] | 5.9% [6-6, Wilson] |
| K3.by6 | 10.4% [10-11, Wilson] | 5.3% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K3.by7 | 10.4% [10-11, Wilson] | 5.3% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K3.by8 | 10.4% [10-11, Wilson] | 5.3% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K3.never | 89.6% [89-90, Wilson] | 94.7% [94-95, Wilson] | 92.1% [92-92, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-2, Wilson] | 2.0% [2-2, Wilson] | 1.7% [2-2, Wilson] |
| K3.k3p | 9.0% [8-10, Wilson] | 3.3% [3-4, Wilson] | 6.2% [6-7, Wilson] |
| K4 | 10.4% [10-11, Wilson] | 5.3% [5-6, Wilson] | 7.9% [8-8, Wilson] |
| K5 | 10.0% [9-11, Wilson] | 15.2% [14-16, Wilson] | 12.6% [12-13, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.1 points (-1.4 to -0.8); K3.by5: -3.6 points (-4.0 to -3.2); K3.by6: -3.3 points (-3.7 to -2.9); K3.by7: -3.3 points (-3.7 to -2.9); K3.by8: -3.3 points (-3.7 to -2.9); K3.never: +3.3 points (+2.9 to +3.7); K3.k3p: -2.6 points (-3.0 to -2.3); K4: -3.3 points (-3.7 to -2.9); K5: -9.1 points (-9.6 to -8.7).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 3.0% [3-3, Wilson] | 3.9% [4-4, Wilson] | 3.4% [3-4, Wilson] |
| K3.by5 | 3.7% [3-4, Wilson] | 9.4% [9-10, Wilson] | 6.5% [6-7, Wilson] |
| K3.by6 | 10.0% [9-11, Wilson] | 13.2% [13-14, Wilson] | 11.6% [11-12, Wilson] |
| K3.by7 | 18.2% [17-19, Wilson] | 13.2% [13-14, Wilson] | 15.7% [15-16, Wilson] |
| K3.by8 | 18.2% [17-19, Wilson] | 13.2% [13-14, Wilson] | 15.7% [15-16, Wilson] |
| K3.never | 81.8% [81-83, Wilson] | 86.8% [86-87, Wilson] | 84.3% [84-85, Wilson] |
| K3.k0 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.7% [1-1, Wilson] | 1.6% [1-2, Wilson] | 1.1% [1-1, Wilson] |
| K3.k3p | 14.5% [14-15, Wilson] | 9.3% [9-10, Wilson] | 11.9% [11-12, Wilson] |
| K4 | 15.3% [15-16, Wilson] | 10.9% [10-12, Wilson] | 13.1% [13-14, Wilson] |
| K5 | 6.9% [6-7, Wilson] | 9.6% [9-10, Wilson] | 8.2% [8-9, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.2 to -0.9); K3.by4: -1.7 points (-1.9 to -1.4); K3.by5: -4.5 points (-4.9 to -4.1); K3.by6: -10.5 points (-11.0 to -10.0); K3.by7: -8.9 points (-9.5 to -8.4); K3.by8: -8.9 points (-9.5 to -8.4); K3.never: +8.9 points (+8.4 to +9.5); K3.k0: -1.1 points (-1.2 to -0.9); K3.k2: -1.1 points (-1.3 to -0.9); K3.k3p: -6.8 points (-7.3 to -6.3); K4: -7.9 points (-8.4 to -7.4); K5: -8.0 points (-8.4 to -7.6).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 3.0% [3-3, Wilson] | 4.5% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| K3.by6 | 4.0% [4-4, Wilson] | 4.6% [4-5, Wilson] | 4.3% [4-5, Wilson] |
| K3.by7 | 4.0% [4-4, Wilson] | 35.4% [34-36, Wilson] | 19.7% [19-20, Wilson] |
| K3.by8 | 45.2% [44-46, Wilson] | 35.4% [34-36, Wilson] | 40.3% [40-41, Wilson] |
| K3.never | 54.8% [54-56, Wilson] | 64.6% [64-66, Wilson] | 59.7% [59-60, Wilson] |
| K3.k0 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.1% [1-1, Wilson] | 2.2% [2-3, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 41.2% [40-42, Wilson] | 30.8% [30-32, Wilson] | 36.0% [35-37, Wilson] |
| K4 | 42.2% [41-43, Wilson] | 33.0% [32-34, Wilson] | 37.6% [37-38, Wilson] |
| K5 | 5.8% [5-6, Wilson] | 6.5% [6-7, Wilson] | 6.2% [6-6, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.2 to -0.9); K3.by4: -1.1 points (-1.2 to -0.9); K3.by5: -2.5 points (-2.7 to -2.2); K3.by6: -3.9 points (-4.2 to -3.6); K3.by7: -4.7 points (-5.2 to -4.3); K3.by8: -5.8 points (-6.4 to -5.2); K3.never: +5.8 points (+5.2 to +6.4); K3.k0: -1.1 points (-1.2 to -0.9); K3.k2: -2.9 points (-3.1 to -2.6); K3.k3p: -1.9 points (-2.4 to -1.3); K4: -4.7 points (-5.3 to -4.2); K5: -3.8 points (-4.1 to -3.5).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.0% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by4 | 1.4% [1-2, Wilson] | 3.7% [3-4, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 4.3% [4-5, Wilson] | 4.8% [4-5, Wilson] | 4.6% [4-5, Wilson] |
| K3.by6 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.by7 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.by8 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K3.never | 91.4% [91-92, Wilson] | 95.2% [95-96, Wilson] | 93.3% [93-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-2, Wilson] | 2.0% [2-2, Wilson] | 1.7% [2-2, Wilson] |
| K3.k3p | 7.2% [7-8, Wilson] | 2.8% [3-3, Wilson] | 5.0% [5-5, Wilson] |
| K4 | 8.6% [8-9, Wilson] | 4.8% [4-5, Wilson] | 6.7% [6-7, Wilson] |
| K5 | 10.0% [9-11, Wilson] | 15.2% [14-16, Wilson] | 12.6% [12-13, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.3 points (-1.6 to -1.1); K3.by5: -4.4 points (-4.8 to -4.0); K3.by6: -4.0 points (-4.5 to -3.6); K3.by7: -4.0 points (-4.5 to -3.6); K3.by8: -4.0 points (-4.5 to -3.6); K3.never: +4.0 points (+3.6 to +4.5); K3.k3p: -3.4 points (-3.7 to -3.0); K4: -4.0 points (-4.5 to -3.6); K5: -9.1 points (-9.6 to -8.7).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.3% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| K3.by3 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 3.0% [3-3, Wilson] | 4.5% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| K3.by6 | 4.0% [4-4, Wilson] | 4.6% [4-5, Wilson] | 4.3% [4-5, Wilson] |
| K3.by7 | 4.0% [4-4, Wilson] | 6.1% [6-7, Wilson] | 5.0% [5-5, Wilson] |
| K3.by8 | 4.9% [4-5, Wilson] | 6.1% [6-7, Wilson] | 5.5% [5-6, Wilson] |
| K3.by9 | 4.9% [4-5, Wilson] | 21.7% [21-23, Wilson] | 13.3% [13-14, Wilson] |
| K3.by10 | 22.9% [22-24, Wilson] | 21.7% [21-23, Wilson] | 22.3% [22-23, Wilson] |
| K3.never | 77.1% [76-78, Wilson] | 78.3% [77-79, Wilson] | 77.7% [77-78, Wilson] |
| K3.k0 | 3.0% [3-3, Wilson] | 2.3% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.1% [1-1, Wilson] | 2.2% [2-3, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 18.9% [18-20, Wilson] | 17.2% [16-18, Wilson] | 18.0% [17-19, Wilson] |
| K4 | 19.9% [19-21, Wilson] | 19.4% [19-20, Wilson] | 19.7% [19-20, Wilson] |
| K5 | 5.9% [5-6, Wilson] | 6.5% [6-7, Wilson] | 6.2% [6-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.2 to -0.9); K3.by4: -1.1 points (-1.2 to -0.9); K3.by5: -2.5 points (-2.7 to -2.2); K3.by6: -3.9 points (-4.2 to -3.6); K3.by7: -15.0 points (-15.6 to -14.5); K3.by8: -31.6 points (-32.3 to -30.9); K3.by9: -27.4 points (-28.1 to -26.7); K3.by10: -21.5 points (-22.1 to -20.8); K3.never: +21.5 points (+20.8 to +22.1); K3.k0: -1.1 points (-1.2 to -0.9); K3.k2: -2.9 points (-3.1 to -2.6); K3.k3p: -17.5 points (-18.2 to -16.9); K4: -20.4 points (-21.0 to -19.7); K5: -3.9 points (-4.2 to -3.6).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.1 (+19.8 to +20.5) FLAG | +20.0 (+19.7 to +20.4) FLAG | +20.1 (+19.8 to +20.3) FLAG |
| K1 Pawniard in play at setup | -1.7 (-1.9 to -1.6) FLAG | -1.8 (-1.9 to -1.6) FLAG | -1.7 (-1.8 to -1.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -4.0 (-4.3 to -3.7) FLAG | -3.9 (-4.1 to -3.6) FLAG | -3.9 (-4.1 to -3.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -6.0 (-6.4 to -5.7) FLAG | -6.1 (-6.4 to -5.8) FLAG | -6.1 (-6.3 to -5.9) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -8.2 (-8.5 to -7.9) FLAG | -8.2 (-8.6 to -7.9) FLAG | -8.2 (-8.4 to -8.0) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -10.2 (-10.5 to -9.8) FLAG | -10.3 (-10.6 to -9.9) FLAG | -10.2 (-10.5 to -10.0) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -11.4 (-11.7 to -11.1) FLAG | -11.6 (-11.9 to -11.2) FLAG | -11.5 (-11.7 to -11.2) FLAG |
| K2 Kingambit in play, own turn 3 | -1.9 (-2.1 to -1.6) FLAG | -2.0 (-2.2 to -1.7) FLAG | -1.9 (-2.1 to -1.8) FLAG |
| K2 Kingambit in play, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.5 (-3.8 to -3.2) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| K2 Kingambit in play, own turn 5 | -5.4 (-5.8 to -5.1) FLAG | -5.7 (-6.0 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| K2 Kingambit in play, own turn 6 | -7.9 (-8.2 to -7.5) FLAG | -7.9 (-8.2 to -7.5) FLAG | -7.9 (-8.1 to -7.6) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +3.7 (+3.4 to +4.0) FLAG | +3.8 (+3.4 to +4.1) FLAG | +3.7 (+3.5 to +4.0) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +3.0 (+2.6 to +3.4) FLAG | +2.8 (+2.4 to +3.2) FLAG | +2.9 (+2.6 to +3.2) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.2 (+1.8 to +2.6) FLAG | +2.0 (+1.6 to +2.4) FLAG | +2.1 (+1.8 to +2.4) FLAG |
| G3 Pawniard in play, own turn 1 | -4.0 (-4.3 to -3.7) FLAG | -3.9 (-4.1 to -3.6) FLAG | -3.9 (-4.1 to -3.7) FLAG |
| G3 Pawniard in play, own turn 2 | -5.3 (-5.6 to -5.0) FLAG | -5.3 (-5.7 to -5.0) FLAG | -5.3 (-5.5 to -5.1) FLAG |
| G3 Pawniard in play, own turn 3 | -6.3 (-6.6 to -6.0) FLAG | -6.3 (-6.6 to -6.0) FLAG | -6.3 (-6.5 to -6.1) FLAG |
| G3 Pawniard in play, own turn 4 | -6.7 (-7.1 to -6.4) FLAG | -6.8 (-7.1 to -6.4) FLAG | -6.8 (-7.0 to -6.5) FLAG |
| G3 Pawniard in play, own turn 5 | -6.0 (-6.3 to -5.7) FLAG | -5.9 (-6.2 to -5.6) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| G3 Kingambit in play, own turn 3 | -1.9 (-2.1 to -1.6) FLAG | -2.0 (-2.2 to -1.7) FLAG | -1.9 (-2.1 to -1.8) FLAG |
| G3 Kingambit in play, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.5 (-3.8 to -3.2) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G3 Kingambit in play, own turn 5 | -5.4 (-5.8 to -5.1) FLAG | -5.7 (-6.0 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -5.0 (-5.3 to -4.7) FLAG | -4.9 (-5.2 to -4.6) FLAG | -5.0 (-5.2 to -4.8) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -7.3 (-7.7 to -7.0) FLAG | -7.6 (-7.9 to -7.3) FLAG | -7.5 (-7.7 to -7.2) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -7.9 (-8.3 to -7.6) FLAG | -8.1 (-8.4 to -7.8) FLAG | -8.0 (-8.2 to -7.8) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -7.5 (-7.8 to -7.2) FLAG | -7.5 (-7.8 to -7.2) FLAG | -7.5 (-7.7 to -7.3) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -6.7 (-7.0 to -6.4) FLAG | -6.8 (-7.0 to -6.5) FLAG | -6.7 (-6.9 to -6.5) FLAG |
| G3 Alolan Muk in play, own turn 3 | -1.9 (-2.2 to -1.6) FLAG | -2.0 (-2.3 to -1.7) FLAG | -2.0 (-2.2 to -1.7) FLAG |
| G3 Alolan Muk in play, own turn 4 | -4.0 (-4.4 to -3.7) FLAG | -4.3 (-4.6 to -3.9) FLAG | -4.2 (-4.4 to -3.9) FLAG |
| G3 Alolan Muk in play, own turn 5 | -6.0 (-6.3 to -5.6) FLAG | -6.1 (-6.5 to -5.7) FLAG | -6.0 (-6.3 to -5.8) FLAG |
| G3 Glimmet in play, own turn 1 | -4.1 (-4.4 to -3.9) FLAG | -4.2 (-4.5 to -4.0) FLAG | -4.2 (-4.4 to -4.0) FLAG |
| G3 Glimmet in play, own turn 2 | -7.6 (-8.0 to -7.3) FLAG | -7.4 (-7.7 to -7.0) FLAG | -7.5 (-7.7 to -7.3) FLAG |
| G3 Glimmet in play, own turn 3 | -9.5 (-9.9 to -9.1) FLAG | -9.3 (-9.7 to -9.0) FLAG | -9.4 (-9.7 to -9.2) FLAG |
| G3 Glimmet in play, own turn 4 | -8.9 (-9.2 to -8.5) FLAG | -8.6 (-8.9 to -8.2) FLAG | -8.7 (-9.0 to -8.5) FLAG |
| G3 Glimmet in play, own turn 5 | -6.7 (-7.0 to -6.4) FLAG | -6.5 (-6.8 to -6.2) FLAG | -6.6 (-6.8 to -6.4) FLAG |
| G3 Glimmora in play, own turn 2 | -3.4 (-3.7 to -3.1) FLAG | -3.2 (-3.5 to -3.0) FLAG | -3.3 (-3.5 to -3.1) FLAG |
| G3 Glimmora in play, own turn 3 | -4.2 (-4.5 to -4.0) FLAG | -4.1 (-4.3 to -3.8) FLAG | -4.1 (-4.3 to -4.0) FLAG |
| G3 Glimmora in play, own turn 4 | -5.3 (-5.5 to -5.0) FLAG | -5.1 (-5.3 to -4.8) FLAG | -5.2 (-5.4 to -5.0) FLAG |
| G3 Glimmora in play, own turn 5 | -6.3 (-6.5 to -6.0) FLAG | -5.9 (-6.2 to -5.7) FLAG | -6.1 (-6.3 to -5.9) FLAG |
| G3 Regigigas in play, own turn 1 | +23.2 (+22.8 to +23.6) FLAG | +23.1 (+22.7 to +23.5) FLAG | +23.1 (+22.9 to +23.4) FLAG |
| G3 Regigigas in play, own turn 2 | +20.3 (+19.9 to +20.7) FLAG | +20.5 (+20.2 to +20.9) FLAG | +20.4 (+20.1 to +20.7) FLAG |
| G3 Regigigas in play, own turn 3 | +17.1 (+16.8 to +17.5) FLAG | +17.3 (+17.0 to +17.7) FLAG | +17.2 (+17.0 to +17.5) FLAG |
| G3 Regigigas in play, own turn 4 | +15.0 (+14.6 to +15.3) FLAG | +15.0 (+14.7 to +15.4) FLAG | +15.0 (+14.8 to +15.2) FLAG |
| G3 Regigigas in play, own turn 5 | +13.5 (+13.2 to +13.8) FLAG | +13.6 (+13.3 to +13.9) FLAG | +13.6 (+13.3 to +13.8) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -2.2 (-2.5 to -2.0) FLAG | -2.2 (-2.5 to -2.0) FLAG | -2.2 (-2.4 to -2.0) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -1.9 (-2.2 to -1.7) FLAG | -1.9 (-2.1 to -1.6) FLAG | -1.9 (-2.1 to -1.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -1.6 (-1.7 to -1.4) FLAG | -1.4 (-1.6 to -1.3) FLAG | -1.5 (-1.6 to -1.4) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -1.1 (-1.2 to -0.9) FLAG | -1.1 (-1.2 to -1.0) FLAG | -1.1 (-1.2 to -1.0) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -1.9 (-2.1 to -1.6) FLAG | -2.0 (-2.2 to -1.7) FLAG | -1.9 (-2.1 to -1.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.5 (-3.8 to -3.2) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -5.4 (-5.8 to -5.1) FLAG | -5.7 (-6.0 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -0.8 (-1.0 to -0.6) | -2.0 (-2.2 to -1.7) FLAG | -1.4 (-1.5 to -1.2) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -3.4 (-3.7 to -3.1) FLAG | -3.5 (-3.8 to -3.2) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -5.4 (-5.8 to -5.1) FLAG | -5.7 (-6.0 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.001 (-0.003 to +0.005) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Heavy Helmet B1 219 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.1 points
- C-his (per-game bootstrap): P2 both Glimmora had their turn -8.9 points (-12.3 to -5.7); P2 the second Glimmora placed had its turn -10.4 points (-13.8 to -7.2); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.4 points (-9.4 to -1.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -13.2 points (-17.2 to -9.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.9 points (-3.4 to -0.8)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -1.1 points (-2.4 to -0.4); P2 both Glimmora had their turn -8.4 points (-12.0 to -5.6); P2 the second Glimmora placed had its turn -9.6 points (-13.2 to -6.7); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -5.7 points (-13.1 to -0.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.3 points (-19.0 to -9.4)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -1.6 points (-2.7 to -0.6); P2 both Glimmora had their turn -9.4 points (-11.3 to -7.6); P2 the second Glimmora placed had its turn -11.4 points (-13.0 to -9.7); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -12.9 points (-15.7 to -10.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -20.7 points (-23.1 to -18.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.1 points (-1.7 to -0.4)
- C-fixed fast (paired test): P2 both Glimmora had their turn -1.0 points (-1.5 to -0.6); P2 the first Glimmora placed had its turn +4.3 points (+3.8 to +4.8); P2 the second Glimmora placed had its turn -4.3 points (-4.9 to -3.8); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -10.4 points (-10.9 to -9.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -22.1 points (-22.7 to -21.4); P4 the moment came and Kingambit was never ready in the deal +1.3 points (+0.8 to +1.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.7 points (-3.2 to -2.3); P5 plan reached in time: Knocks out their strongest +1.4 points (+1.0 to +1.8); P5 plan reached in time: Wins outright (a lower bound) +1.4 points (+1.0 to +1.8)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn -1.0 points (-1.4 to -0.7); P2 both Glimmora had their turn -5.9 points (-6.4 to -5.3); P2 the second Glimmora placed had its turn -7.1 points (-7.7 to -6.5); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -16.5 points (-17.1 to -15.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -28.6 points (-29.3 to -27.9); P4 ready at the winning moment: Knocks out their strongest +1.1 points (+0.7 to +1.6); P4 the moment came and Kingambit was never ready in the deal -1.5 points (-2.0 to -1.0); P5 plan reached in time: Knocks out their strongest +1.6 points (+1.2 to +2.1)
- C-fixed slow (paired test): P2 both Glimmora had their turn -13.8 points (-14.5 to -13.1); P2 the first Glimmora placed had its turn +1.9 points (+1.6 to +2.2); P2 the second Glimmora placed had its turn -16.0 points (-16.7 to -15.3); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.8 points (-5.1 to -4.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -19.6 points (-20.2 to -19.0); P4 ready at the winning moment: Knocks out their strongest +1.9 points (+1.4 to +2.4); P4 ready at the winning moment: Wins outright (a lower bound) +1.9 points (+1.4 to +2.4); P4 the moment came and Kingambit was never ready in the deal -5.2 points (-5.6 to -4.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.1 points (+2.7 to +3.6); P5 plan reached in time: Knocks out their strongest +2.0 points (+1.5 to +2.5); P5 plan reached in time: Wins outright (a lower bound) +2.0 points (+1.5 to +2.5)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +1.1 points (+0.6 to +1.5); P2 the first Glimmora placed had its turn +4.3 points (+3.8 to +4.8); P2 the second Glimmora placed had its turn -4.2 points (-4.7 to -3.6); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -11.2 points (-11.8 to -10.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -22.1 points (-22.7 to -21.4); P4 ready at the winning moment: Knocks out their strongest +1.7 points (+1.5 to +2.0); P4 ready at the winning moment: Wins outright (a lower bound) +1.7 points (+1.5 to +2.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.2 points (-1.5 to -1.0); P5 plan reached in time: Knocks out their strongest +1.7 points (+1.5 to +2.0); P5 plan reached in time: Wins outright (a lower bound) +1.7 points (+1.5 to +2.0)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 both Glimmora had their turn -5.0 points (-5.7 to -4.4); P2 the first Glimmora placed had its turn +1.9 points (+1.6 to +2.2); P2 the second Glimmora placed had its turn -6.9 points (-7.5 to -6.3); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -31.9 points (-32.5 to -31.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -30.5 points (-31.2 to -29.8); P4 ready at the winning moment: Knocks out their strongest +10.7 points (+10.2 to +11.1); P4 ready at the winning moment: Wins outright (a lower bound) +10.7 points (+10.2 to +11.1); P4 the moment came and Kingambit was never ready in the deal -9.3 points (-9.7 to -8.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.3 points (-1.5 to -1.0); P5 plan reached in time: Knocks out their strongest +10.6 points (+10.2 to +11.0); P5 plan reached in time: Wins outright (a lower bound) +10.6 points (+10.2 to +11.0)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K6 Muk and Regigigas both in play, own turn 3 +3.7 points; K6 Muk and Regigigas both in play, own turn 4 +2.9 points; K6 Muk and Regigigas both in play, own turn 5 +2.1 points; G3 Regigigas in play, own turn 1 +23.1 points; G3 Regigigas in play, own turn 2 +20.4 points; G3 Regigigas in play, own turn 3 +17.2 points; G3 Regigigas in play, own turn 4 +15.0 points; G3 Regigigas in play, own turn 5 +13.6 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.7 points; K1 Pawniard line in play (end of own turn t), own turn 1 -3.9 points; K1 Pawniard line in play (end of own turn t), own turn 2 -6.1 points; K1 Pawniard line in play (end of own turn t), own turn 3 -8.2 points; K1 Pawniard line in play (end of own turn t), own turn 4 -10.2 points; K1 Pawniard line in play (end of own turn t), own turn 5 -11.5 points; K2 Kingambit in play, own turn 3 -1.9 points; K2 Kingambit in play, own turn 4 -3.5 points; K2 Kingambit in play, own turn 5 -5.6 points; K2 Kingambit in play, own turn 6 -7.9 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by4 -1.3; K3.by5 -1.8; K3.by6 -2.0; K3.by7 -2.9; K3.by8 -4.2; K3.k0 -1.2; K4 -3.0; K5 -2.9; C-his, seat-matched: K3.by3 -1.1; K3.by4 -1.4; K3.by5 -2.0; K3.by6 -2.3; K3.by7 -5.8; K3.by8 -5.8; K3.k0 -1.3; K3.k2 -1.0; K4 -4.5; K5 -2.9; C-bot: K3.by3 -1.0; K3.by4 -1.4; K3.by5 -2.0; K3.by6 -3.0; K3.by7 -4.3; K3.by8 -5.2; K3.never +4.2; K3.k0 -1.2; K3.k2 -1.3; K3.k3p -2.7; K4 -4.0; K5 -3.6; C-fixed fast: K3.by4 -1.1; K3.by5 -3.6; K3.by6 -3.3; K3.by7 -3.3; K3.by8 -3.3; K3.never +3.3; K3.k3p -2.6; K4 -3.3; K5 -9.1; C-fixed medium: K3.by3 -1.1; K3.by4 -1.7; K3.by5 -4.5; K3.by6 -10.5; K3.by7 -8.9; K3.by8 -8.9; K3.never +8.9; K3.k0 -1.1; K3.k2 -1.1; K3.k3p -6.8; K4 -7.9; K5 -8.0; C-fixed slow: K3.by3 -1.1; K3.by4 -1.1; K3.by5 -2.5; K3.by6 -3.9; K3.by7 -4.7; K3.by8 -5.8; K3.never +5.8; K3.k0 -1.1; K3.k2 -2.9; K3.k3p -1.9; K4 -4.7; K5 -3.8; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.3; K3.by5 -4.4; K3.by6 -4.0; K3.by7 -4.0; K3.by8 -4.0; K3.never +4.0; K3.k3p -3.4; K4 -4.0; K5 -9.1; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.1; K3.by4 -1.1; K3.by5 -2.5; K3.by6 -3.9; K3.by7 -15.0; K3.by8 -31.6; K3.by9 -27.4; K3.by10 -21.5; K3.never +21.5; K3.k0 -1.1; K3.k2 -2.9; K3.k3p -17.5; K4 -20.4; K5 -3.9.
Not valued here (changed cards the script never plays: they count as blanks): Heavy Helmet.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Copycat B1 225 +1 Regigigas B3 134 (card-list id a35b56716749)

Changes: ['-1 Copycat B1 225', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 0; the valuation and the fallback rule disagree at no Copycat decision.

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 48.9% (48.4-49.3) | 48.6% (48.2-49.1) | 48.8% (48.4-49.1) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 83.5% / 94.7% [71-91] | 74.2% / 89.7% [59-86] | 78.9% / 92.2% [65-88] |
| P2 both Glimmora had their turn | 23.8% / 63.9% [17-30] | 20.7% / 64.9% [13-29] | 22.2% / 64.4% [16-28] |
| P2 the first Glimmora placed had its turn | 80.3% / 89.4% [69-89] | 68.7% / 80.4% [53-82] | 74.5% / 84.9% [61-85] |
| P2 the second Glimmora placed had its turn | 27.0% / 63.7% [19-34] | 26.2% / 64.7% [18-35] | 26.6% / 64.2% [19-34] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9] | 8.7% [8-9] | 8.6% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.1% / 50.1% [1-3] | 3.6% / 55.3% [2-6] | 2.9% / 52.7% [1-4] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.3% / 59.1% [14-20] | 22.0% / 65.3% [17-27] | 19.7% / 62.2% [16-24] |
| P4 ready at the winning moment: Knocks out their strongest | 12.6% / 38.0% [3-24] | 8.7% / 36.8% [2-17] | 10.7% / 37.4% [2-20] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.3% / 27.7% [0-7] | 1.3% / 29.4% [0-4] | 1.8% / 28.5% [0-5] |
| P4 not ready, ready 1 turn late | 4.5% / 47.1% [0-11] | 3.3% / 50.6% [0-7] | 3.9% / 48.8% [0-9] |
| P4 not ready, ready 2 or more turns late | 1.4% / 44.0% [0-4] | 1.3% / 48.6% [0-4] | 1.4% / 46.3% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 9.1% / 51.7% [0-21] | 9.7% / 57.0% [0-24] | 9.4% / 54.4% [0-22] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.8% / 55.2% [9-55] | 29.7% / 57.7% [11-53] | 29.7% / 56.5% [10-53] |
| P5 plan reached in time: Knocks out their strongest | 18.6% / 61.1% [7-33] | 13.3% / 60.6% [5-23] | 15.9% / 60.9% [6-28] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.7% / 45.2% [0-8] | 1.8% / 49.1% [0-5] | 2.2% / 47.2% [0-7] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 45.6% of 2770 [25-65] | 37.8% of 2303 [23-58] | 42.1% of 5073 [25-61] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 8.2% of 2770 [0-32] | 5.8% of 2303 [0-29] | 7.1% of 5073 [0-31] |
| P4 not ready, ready 1 turn late | 16.4% of 2770 [0-53] | 14.3% of 2303 [0-47] | 15.4% of 5073 [0-51] |
| P4 not ready, ready 2 or more turns late | 5.1% of 2770 [0-18] | 5.7% of 2303 [0-22] | 5.4% of 5073 [0-20] |
| P4 the moment came and Kingambit was never ready in the deal | 33.0% of 2770 [0-54] | 42.2% of 2303 [0-65] | 37.1% of 5073 [0-59] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -4.4 points (-5.4 to -3.3); P2.both: -13.5 points (-18.0 to -9.4); P2.g1: -3.2 points (-4.8 to -1.1); P2.g2: -14.7 points (-19.0 to -10.6); P3.pawn_lead: -4.2 points (-4.5 to -3.9); P3.pawn_promo: -3.2 points (-7.7 to -0.5); P3.grimer_muk: -10.4 points (-13.8 to -7.5).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.7% / 94.0% [65-92] | 83.7% / 94.1% [74-91] | 82.7% / 94.0% [73-90] |
| P2 both Glimmora had their turn | 22.3% / 57.8% [15-29] | 22.0% / 81.9% [14-39] | 22.1% / 69.9% [15-30] |
| P2 the first Glimmora placed had its turn | 78.3% / 88.8% [62-90] | 80.6% / 85.3% [70-89] | 79.4% / 87.0% [70-87] |
| P2 the second Glimmora placed had its turn | 25.7% / 58.0% [17-34] | 25.1% / 77.5% [15-43] | 25.4% / 67.7% [18-34] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9] | 8.7% [8-9] | 8.6% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.9% / 44.6% [1-3] | 4.4% / 80.1% [0-8] | 3.2% / 62.4% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.4% / 54.4% [13-22] | 22.4% / 86.5% [13-29] | 19.9% / 70.4% [15-24] |
| P4 ready at the winning moment: Knocks out their strongest | 15.2% / 37.5% [2-30] | 4.0% / 54.5% [0-12] | 9.6% / 46.0% [2-19] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.6% / 25.9% [0-11] | 0.0% / 50.6% [0-0] | 1.8% / 38.2% [0-7] |
| P4 not ready, ready 1 turn late | 5.9% / 41.8% [0-14] | 0.0% / 77.6% [0-0] | 2.9% / 59.7% [0-8] |
| P4 not ready, ready 2 or more turns late | 2.0% / 37.9% [0-6] | 0.0% / 77.6% [0-0] | 1.0% / 57.7% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 12.8% / 48.7% [0-30] | 0.0% / 77.6% [0-0] | 6.4% / 63.1% [0-16] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.3% / 50.6% [6-57] | 18.5% / 69.0% [0-48] | 23.4% / 59.8% [7-45] |
| P5 plan reached in time: Knocks out their strongest | 23.0% / 59.0% [7-40] | 4.0% / 81.5% [0-12] | 13.5% / 70.2% [5-27] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.2% / 40.1% [0-13] | 0.0% / 77.6% [0-0] | 2.1% / 58.8% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 42.4% of 3579 [16-60] | 100.0% of 396 [100-100] | 48.2% of 3975 [26-70] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 9.9% of 3579 [0-40] | 0.0% of 396 [0-0] | 9.0% of 3975 [0-33] |
| P4 not ready, ready 1 turn late | 16.4% of 3579 [0-61] | 0.0% of 396 [0-0] | 14.7% of 3975 [0-43] |
| P4 not ready, ready 2 or more turns late | 5.6% of 3579 [0-23] | 0.0% of 396 [0-0] | 5.0% of 3975 [0-17] |
| P4 the moment came and Kingambit was never ready in the deal | 35.6% of 3579 [0-58] | 0.0% of 396 [0-0] | 32.1% of 3975 [0-53] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -4.8 points (-5.8 to -4.0); P2.both: -13.1 points (-17.9 to -9.8); P2.g1: -4.2 points (-5.5 to -3.3); P2.g2: -13.8 points (-18.4 to -10.6); P3.pawn_lead: -4.2 points (-4.7 to -3.9); P3.pawn_promo: -4.5 points (-10.8 to -0.3); P3.grimer_muk: -11.5 points (-15.6 to -7.1).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.0% / 86.6% [82-88] | 76.5% / 78.7% [72-81] | 80.8% / 82.6% [77-84] |
| P2 both Glimmora had their turn | 25.3% / 33.4% [22-28] | 20.2% / 29.1% [17-23] | 22.8% / 31.2% [20-26] |
| P2 the first Glimmora placed had its turn | 79.7% / 80.1% [75-84] | 68.9% / 69.5% [64-74] | 74.3% / 74.8% [69-79] |
| P2 the second Glimmora placed had its turn | 30.7% / 37.6% [28-33] | 27.8% / 35.0% [25-31] | 29.2% / 36.3% [27-32] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9] | 8.7% [8-9] | 8.6% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 3.9% / 15.0% [3-5] | 6.2% / 17.8% [5-7] | 5.1% / 16.4% [4-6] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 19.8% / 29.4% [18-21] | 26.8% / 36.2% [25-29] | 23.3% / 32.8% [22-25] |
| P4 ready at the winning moment: Knocks out their strongest | 6.5% / 12.7% [3-10] | 5.8% / 12.8% [3-9] | 6.1% / 12.8% [3-9] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.2% / 6.4% [0-1] | 0.6% / 7.7% [0-2] | 0.4% / 7.0% [0-1] |
| P4 not ready, ready 1 turn late | 4.3% / 12.7% [2-7] | 3.4% / 13.4% [2-5] | 3.9% / 13.1% [2-6] |
| P4 not ready, ready 2 or more turns late | 1.7% / 10.1% [1-3] | 1.8% / 11.8% [1-3] | 1.7% / 10.9% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 9.7% / 18.1% [5-15] | 10.2% / 20.2% [5-16] | 9.9% / 19.1% [5-16] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.4% / 75.6% [58-80] | 68.9% / 75.9% [58-79] | 69.1% / 75.8% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 12.5% / 20.9% [7-19] | 11.0% / 20.9% [6-16] | 11.7% / 20.9% [7-17] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.3% / 8.7% [0-1] | 0.6% / 10.6% [0-2] | 0.4% / 9.6% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 29.5% of 2215 [20-41] | 27.2% of 2117 [20-36] | 28.3% of 4332 [20-39] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.9% of 2215 [0-3] | 2.8% of 2117 [0-9] | 1.8% of 4332 [0-6] |
| P4 not ready, ready 1 turn late | 19.4% of 2215 [13-27] | 16.2% of 2117 [11-21] | 17.8% of 4332 [12-24] |
| P4 not ready, ready 2 or more turns late | 7.5% of 2215 [3-12] | 8.4% of 2117 [3-14] | 7.9% of 4332 [3-12] |
| P4 the moment came and Kingambit was never ready in the deal | 43.7% of 2215 [30-56] | 48.2% of 2117 [35-60] | 45.9% of 4332 [33-58] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -6.3 points (-7.4 to -5.2); P2.both: -14.2 points (-16.1 to -12.3); P2.g1: -4.5 points (-5.5 to -3.5); P2.g2: -16.0 points (-17.6 to -14.3); P3.pawn_lead: -4.2 points (-4.6 to -3.9); P3.pawn_promo: -10.8 points (-13.4 to -8.2); P3.grimer_muk: -16.2 points (-18.4 to -14.0); P4.ko: -1.0 points (-1.9 to -0.3); P4.never: +1.2 points (+0.5 to +2.0); P5.ko: -1.2 points (-2.0 to -0.6).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 73.8% [73-75, Wilson] | 49.6% [49-51, Wilson] | 61.7% [61-62, Wilson] |
| P2 both Glimmora had their turn | 17.0% [16-18, Wilson] | 5.8% [5-6, Wilson] | 11.4% [11-12, Wilson] |
| P2 the first Glimmora placed had its turn | 70.0% [69-71, Wilson] | 36.9% [36-38, Wilson] | 53.5% [53-54, Wilson] |
| P2 the second Glimmora placed had its turn | 20.8% [20-22, Wilson] | 18.5% [18-19, Wilson] | 19.6% [19-20, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 12.2% [12-13, Wilson] | 14.3% [14-15, Wilson] | 13.2% [13-14, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.8% [36-38, Wilson] | 40.7% [40-42, Wilson] | 38.8% [38-39, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 11.6% [11-12, Wilson] | 3.8% [3-4, Wilson] | 7.7% [7-8, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 11.6% [11-12, Wilson] | 3.8% [3-4, Wilson] | 7.7% [7-8, Wilson] |
| P4 not ready, ready 1 turn late | 1.4% [1-2, Wilson] | 0.3% [0-0, Wilson] | 0.9% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.1% [23-25, Wilson] | 18.2% [17-19, Wilson] | 21.2% [21-22, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 62.8% [62-64, Wilson] | 77.7% [77-79, Wilson] | 70.3% [70-71, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 13.0% [12-14, Wilson] | 4.1% [4-4, Wilson] | 8.6% [8-9, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 13.0% [12-14, Wilson] | 4.1% [4-4, Wilson] | 8.6% [8-9, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 31.2% of 3717 [30-33, Wilson] | 16.8% of 2230 [15-18, Wilson] | 25.8% of 5947 [25-27, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 31.2% of 3717 [30-33, Wilson] | 16.8% of 2230 [15-18, Wilson] | 25.8% of 5947 [25-27, Wilson] |
| P4 not ready, ready 1 turn late | 3.9% of 3717 [3-5, Wilson] | 1.5% of 2230 [1-2, Wilson] | 3.0% of 5947 [3-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 3717 [0-0, Wilson] | 0.0% of 2230 [0-0, Wilson] | 0.0% of 5947 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 65.0% of 3717 [63-66, Wilson] | 81.7% of 2230 [80-83, Wilson] | 71.2% of 5947 [70-72, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.7 points (-6.3 to -5.1); P2.both: -6.8 points (-7.3 to -6.3); P2.g1: -1.5 points (-2.0 to -0.9); P2.g2: -11.1 points (-11.6 to -10.5); P3.pawn_lead: -4.2 points (-4.6 to -3.9); P3.pawn_promo: -7.1 points (-7.6 to -6.5); P3.grimer_muk: -17.2 points (-17.9 to -16.6); P4.ko: -3.1 points (-3.5 to -2.7); P4.win: -3.1 points (-3.5 to -2.7); P4.nomoment: +3.6 points (+3.1 to +4.0); P5.ko: -3.5 points (-4.0 to -3.1); P5.win: -3.5 points (-4.0 to -3.1).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 83.7% [83-84, Wilson] | 74.1% [73-75, Wilson] | 78.9% [78-79, Wilson] |
| P2 both Glimmora had their turn | 25.0% [24-26, Wilson] | 17.4% [17-18, Wilson] | 21.2% [21-22, Wilson] |
| P2 the first Glimmora placed had its turn | 80.9% [80-82, Wilson] | 71.0% [70-72, Wilson] | 75.9% [75-77, Wilson] |
| P2 the second Glimmora placed had its turn | 27.8% [27-29, Wilson] | 20.5% [20-21, Wilson] | 24.2% [24-25, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 8.7% [8-9, Wilson] | 12.5% [12-13, Wilson] | 10.6% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 29.8% [29-31, Wilson] | 38.1% [37-39, Wilson] | 34.0% [33-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 21.4% [21-22, Wilson] | 11.3% [11-12, Wilson] | 16.4% [16-17, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.3% [2-3, Wilson] | 1.3% [1-2, Wilson] | 1.8% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 23.6% [23-24, Wilson] | 25.5% [25-26, Wilson] | 24.6% [24-25, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 52.7% [52-54, Wilson] | 61.8% [61-63, Wilson] | 57.2% [57-58, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 23.7% [23-25, Wilson] | 12.6% [12-13, Wilson] | 18.2% [18-19, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 45.2% of 4733 [44-47, Wilson] | 29.7% of 3817 [28-31, Wilson] | 38.3% of 8550 [37-39, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 4733 [0-0, Wilson] | 0.0% of 3817 [0-0, Wilson] | 0.0% of 8550 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 4.9% of 4733 [4-6, Wilson] | 3.4% of 3817 [3-4, Wilson] | 4.2% of 8550 [4-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4733 [0-0, Wilson] | 0.0% of 3817 [0-0, Wilson] | 0.0% of 8550 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 49.9% of 4733 [48-51, Wilson] | 66.9% of 3817 [65-68, Wilson] | 57.5% of 8550 [56-59, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: -7.1 points (-7.6 to -6.6); P2.both: -12.8 points (-13.4 to -12.2); P2.g1: -6.2 points (-6.7 to -5.7); P2.g2: -13.7 points (-14.3 to -13.0); P3.pawn_lead: -4.2 points (-4.6 to -3.9); P3.pawn_promo: -13.4 points (-14.0 to -12.8); P3.grimer_muk: -22.8 points (-23.4 to -22.1); P4.ko: -5.4 points (-5.9 to -4.9); P4.nomoment: +6.3 points (+5.8 to +6.8); P5.ko: -6.0 points (-6.5 to -5.4).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.5% [91-92, Wilson] | 84.7% [84-85, Wilson] | 88.1% [88-89, Wilson] |
| P2 both Glimmora had their turn | 45.2% [44-46, Wilson] | 36.6% [36-38, Wilson] | 40.9% [40-42, Wilson] |
| P2 the first Glimmora placed had its turn | 86.7% [86-87, Wilson] | 78.2% [77-79, Wilson] | 82.5% [82-83, Wilson] |
| P2 the second Glimmora placed had its turn | 50.0% [49-51, Wilson] | 43.1% [42-44, Wilson] | 46.5% [46-47, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.9% [3-3, Wilson] | 5.2% [5-6, Wilson] | 4.1% [4-4, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 16.9% [16-18, Wilson] | 24.2% [23-25, Wilson] | 20.5% [20-21, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 44.0% [43-45, Wilson] | 32.7% [32-34, Wilson] | 38.3% [38-39, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 44.0% [43-45, Wilson] | 32.7% [32-34, Wilson] | 38.3% [38-39, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 6.4% [6-7, Wilson] | 3.2% [3-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 12.0% [11-13, Wilson] | 11.1% [10-12, Wilson] | 11.6% [11-12, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 44.0% [43-45, Wilson] | 49.8% [49-51, Wilson] | 46.9% [46-48, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 44.0% [43-45, Wilson] | 39.1% [38-40, Wilson] | 41.5% [41-42, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 44.0% [43-45, Wilson] | 39.1% [38-40, Wilson] | 41.5% [41-42, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 78.5% of 5599 [77-80, Wilson] | 65.1% of 5017 [64-66, Wilson] | 72.2% of 10616 [71-73, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 78.5% of 5599 [77-80, Wilson] | 65.1% of 5017 [64-66, Wilson] | 72.2% of 10616 [71-73, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5599 [0-0, Wilson] | 12.8% of 5017 [12-14, Wilson] | 6.0% of 10616 [6-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5599 [0-0, Wilson] | 0.0% of 5017 [0-0, Wilson] | 0.0% of 10616 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 21.5% of 5599 [20-23, Wilson] | 22.1% of 5017 [21-23, Wilson] | 21.8% of 10616 [21-23, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: -4.6 points (-5.0 to -4.2); P2.both: -21.4 points (-22.1 to -20.7); P2.g1: -3.4 points (-3.8 to -3.0); P2.g2: -22.6 points (-23.3 to -21.8); P3.pawn_lead: -4.2 points (-4.6 to -3.9); P3.pawn_promo: -2.7 points (-3.0 to -2.3); P3.grimer_muk: -15.2 points (-15.8 to -14.7); P4.ko: -6.2 points (-6.8 to -5.6); P4.win: -6.2 points (-6.8 to -5.6); P4.late1: +1.1 points (+0.9 to +1.4); P4.never: -2.4 points (-2.9 to -2.0); P4.nomoment: +7.5 points (+7.0 to +7.9); P5.ko: -5.1 points (-5.6 to -4.5); P5.win: -5.1 points (-5.6 to -4.5).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 74.0% [73-75, Wilson] | 49.6% [49-51, Wilson] | 61.8% [61-62, Wilson] |
| P2 both Glimmora had their turn | 17.2% [16-18, Wilson] | 5.8% [5-6, Wilson] | 11.5% [11-12, Wilson] |
| P2 the first Glimmora placed had its turn | 70.0% [69-71, Wilson] | 36.9% [36-38, Wilson] | 53.5% [53-54, Wilson] |
| P2 the second Glimmora placed had its turn | 21.1% [20-22, Wilson] | 18.5% [18-19, Wilson] | 19.8% [19-20, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 13.2% [13-14, Wilson] | 14.6% [14-15, Wilson] | 13.9% [13-14, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.8% [36-38, Wilson] | 40.7% [40-42, Wilson] | 38.8% [38-39, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 2.9% [3-3, Wilson] | 0.6% [0-1, Wilson] | 1.7% [2-2, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.9% [3-3, Wilson] | 0.6% [0-1, Wilson] | 1.7% [2-2, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.7% [2-3, Wilson] | 1.2% [1-1, Wilson] | 1.9% [2-2, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 94.4% [94-95, Wilson] | 98.2% [98-98, Wilson] | 96.3% [96-97, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 2.9% [3-3, Wilson] | 0.6% [0-1, Wilson] | 1.7% [2-2, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.9% [3-3, Wilson] | 0.6% [0-1, Wilson] | 1.7% [2-2, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 51.5% of 557 [47-56, Wilson] | 33.3% of 180 [27-41, Wilson] | 47.1% of 737 [44-51, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 51.5% of 557 [47-56, Wilson] | 33.3% of 180 [27-41, Wilson] | 47.1% of 737 [44-51, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 557 [0-1, Wilson] | 0.0% of 180 [0-2, Wilson] | 0.0% of 737 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 557 [0-1, Wilson] | 0.0% of 180 [0-2, Wilson] | 0.0% of 737 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 48.5% of 557 [44-53, Wilson] | 66.7% of 180 [59-73, Wilson] | 52.9% of 737 [49-56, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.7 points (-6.3 to -5.1); P2.both: -6.9 points (-7.4 to -6.4); P2.g1: -1.5 points (-2.0 to -0.9); P2.g2: -11.1 points (-11.7 to -10.5); P3.pawn_lead: -4.2 points (-4.6 to -3.9); P3.pawn_promo: -7.9 points (-8.5 to -7.3); P3.grimer_muk: -17.2 points (-17.9 to -16.6); P4.never: -1.1 points (-1.4 to -0.9); P4.nomoment: +1.6 points (+1.4 to +1.9).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.8% [91-92, Wilson] | 84.9% [84-86, Wilson] | 88.3% [88-89, Wilson] |
| P2 both Glimmora had their turn | 55.5% [55-56, Wilson] | 42.8% [42-44, Wilson] | 49.1% [48-50, Wilson] |
| P2 the first Glimmora placed had its turn | 86.7% [86-87, Wilson] | 78.2% [77-79, Wilson] | 82.5% [82-83, Wilson] |
| P2 the second Glimmora placed had its turn | 60.5% [60-61, Wilson] | 49.4% [48-50, Wilson] | 55.0% [54-56, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 4.8% [4-5, Wilson] | 7.9% [7-8, Wilson] | 6.3% [6-7, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.3% [17-18, Wilson] | 25.1% [24-26, Wilson] | 21.2% [21-22, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 15.3% [15-16, Wilson] | 12.6% [12-13, Wilson] | 14.0% [14-14, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 15.3% [15-16, Wilson] | 12.6% [12-13, Wilson] | 14.0% [14-14, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.3% [0-0, Wilson] | 0.1% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.5% [2-3, Wilson] | 2.1% [2-2, Wilson] | 2.3% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 82.2% [81-83, Wilson] | 85.0% [84-86, Wilson] | 83.6% [83-84, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 15.3% [15-16, Wilson] | 12.9% [12-14, Wilson] | 14.1% [14-15, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 15.3% [15-16, Wilson] | 12.9% [12-14, Wilson] | 14.1% [14-15, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 86.2% of 1780 [84-88, Wilson] | 84.0% of 1503 [82-86, Wilson] | 85.2% of 3283 [84-86, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 86.2% of 1780 [84-88, Wilson] | 84.0% of 1503 [82-86, Wilson] | 85.2% of 3283 [84-86, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1780 [0-0, Wilson] | 1.7% of 1503 [1-3, Wilson] | 0.8% of 3283 [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1780 [0-0, Wilson] | 0.0% of 1503 [0-0, Wilson] | 0.0% of 3283 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 13.8% of 1780 [12-16, Wilson] | 14.3% of 1503 [13-16, Wilson] | 14.0% of 3283 [13-15, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: -4.4 points (-4.8 to -4.0); P2.both: -15.1 points (-15.8 to -14.5); P2.g1: -3.4 points (-3.8 to -3.0); P2.g2: -16.2 points (-16.8 to -15.5); P3.pawn_lead: -4.2 points (-4.6 to -3.9); P3.pawn_promo: -28.7 points (-29.3 to -28.0); P3.grimer_muk: -25.8 points (-26.5 to -25.1); P4.ko: +7.4 points (+7.0 to +7.9); P4.win: +7.4 points (+7.0 to +7.9); P4.never: -9.4 points (-9.8 to -9.0); P4.nomoment: +1.9 points (+1.6 to +2.2); P5.ko: +7.5 points (+7.0 to +7.9); P5.win: +7.5 points (+7.0 to +7.9).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.5% (27.1-27.9) | 27.1% (26.7-27.5) | 27.3% (27.0-27.6) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 49.5% (49.1-50.0) | 49.3% (48.9-49.7) | 49.4% (49.1-49.7) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 58.0% (57.5-58.4) | 57.9% (57.5-58.4) | 57.9% (57.6-58.3) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 63.1% (62.7-63.5) | 63.1% (62.7-63.6) | 63.1% (62.8-63.4) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 66.3% (65.9-66.7) | 66.4% (66.0-66.8) | 66.4% (66.1-66.7) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 67.9% (67.5-68.3) | 67.9% (67.5-68.3) | 67.9% (67.6-68.2) |
| K2 Kingambit in play, own turn 2 | 8.2% (8.0-8.5) | 8.4% (8.1-8.6) | 8.3% (8.1-8.5) |
| K2 Kingambit in play, own turn 3 | 14.8% (14.5-15.1) | 14.9% (14.6-15.3) | 14.9% (14.7-15.1) |
| K2 Kingambit in play, own turn 4 | 23.3% (23.0-23.7) | 23.4% (23.0-23.8) | 23.4% (23.1-23.6) |
| K2 Kingambit in play, own turn 5 | 33.4% (33.0-33.8) | 33.3% (32.9-33.8) | 33.4% (33.1-33.7) |
| K2 Kingambit in play, own turn 6 | 44.0% (43.5-44.4) | 43.7% (43.2-44.1) | 43.8% (43.5-44.1) |
| K6 Muk and Regigigas both in play, own turn 3 | 21.3% (21.0-21.7) | 21.5% (21.1-21.8) | 21.4% (21.1-21.7) |
| K6 Muk and Regigigas both in play, own turn 4 | 28.8% (28.4-29.2) | 29.1% (28.7-29.5) | 29.0% (28.7-29.2) |
| K6 Muk and Regigigas both in play, own turn 5 | 35.4% (35.0-35.8) | 35.8% (35.4-36.2) | 35.6% (35.3-35.9) |
| G3 Pawniard in play, own turn 1 | 49.5% (49.1-50.0) | 49.3% (48.9-49.7) | 49.4% (49.1-49.7) |
| G3 Pawniard in play, own turn 2 | 49.7% (49.3-50.2) | 49.5% (49.1-50.0) | 49.6% (49.3-50.0) |
| G3 Pawniard in play, own turn 3 | 48.3% (47.9-48.7) | 48.2% (47.7-48.6) | 48.2% (47.9-48.6) |
| G3 Pawniard in play, own turn 4 | 43.0% (42.5-43.4) | 43.0% (42.6-43.5) | 43.0% (42.7-43.3) |
| G3 Pawniard in play, own turn 5 | 34.4% (34.0-34.8) | 34.6% (34.1-35.0) | 34.5% (34.2-34.8) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 8.2% (8.0-8.5) | 8.4% (8.1-8.6) | 8.3% (8.1-8.5) |
| G3 Kingambit in play, own turn 3 | 14.8% (14.5-15.1) | 14.9% (14.6-15.3) | 14.9% (14.7-15.1) |
| G3 Kingambit in play, own turn 4 | 23.3% (23.0-23.7) | 23.4% (23.0-23.8) | 23.4% (23.1-23.6) |
| G3 Kingambit in play, own turn 5 | 33.4% (33.0-33.8) | 33.3% (32.9-33.8) | 33.4% (33.1-33.7) |
| G3 Alolan Grimer in play, own turn 1 | 48.2% (47.7-48.6) | 48.4% (47.9-48.8) | 48.3% (48.0-48.6) |
| G3 Alolan Grimer in play, own turn 2 | 39.6% (39.1-40.0) | 39.9% (39.4-40.3) | 39.7% (39.4-40.0) |
| G3 Alolan Grimer in play, own turn 3 | 35.8% (35.4-36.2) | 35.9% (35.5-36.3) | 35.9% (35.6-36.1) |
| G3 Alolan Grimer in play, own turn 4 | 30.5% (30.1-30.9) | 30.5% (30.1-30.9) | 30.5% (30.2-30.8) |
| G3 Alolan Grimer in play, own turn 5 | 24.8% (24.5-25.2) | 24.6% (24.3-25.0) | 24.7% (24.5-25.0) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 16.2% (15.8-16.5) | 16.3% (16.0-16.6) | 16.2% (16.0-16.5) |
| G3 Alolan Muk in play, own turn 3 | 24.5% (24.1-24.8) | 24.8% (24.4-25.1) | 24.6% (24.3-24.9) |
| G3 Alolan Muk in play, own turn 4 | 32.3% (31.9-32.7) | 32.7% (32.3-33.1) | 32.5% (32.2-32.8) |
| G3 Alolan Muk in play, own turn 5 | 39.2% (38.8-39.6) | 39.7% (39.2-40.1) | 39.4% (39.1-39.7) |
| G3 Glimmet in play, own turn 1 | 75.9% (75.5-76.3) | 75.9% (75.5-76.3) | 75.9% (75.7-76.2) |
| G3 Glimmet in play, own turn 2 | 46.0% (45.6-46.5) | 45.7% (45.3-46.1) | 45.9% (45.6-46.2) |
| G3 Glimmet in play, own turn 3 | 38.7% (38.3-39.1) | 38.3% (37.9-38.7) | 38.5% (38.2-38.8) |
| G3 Glimmet in play, own turn 4 | 29.8% (29.4-30.2) | 29.9% (29.5-30.3) | 29.9% (29.6-30.1) |
| G3 Glimmet in play, own turn 5 | 20.6% (20.3-21.0) | 20.6% (20.3-21.0) | 20.6% (20.4-20.9) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 54.6% (54.1-55.0) | 54.8% (54.4-55.3) | 54.7% (54.4-55.0) |
| G3 Glimmora in play, own turn 3 | 68.7% (68.3-69.1) | 69.2% (68.7-69.6) | 68.9% (68.6-69.2) |
| G3 Glimmora in play, own turn 4 | 78.9% (78.6-79.3) | 79.1% (78.8-79.5) | 79.0% (78.8-79.3) |
| G3 Glimmora in play, own turn 5 | 85.9% (85.6-86.2) | 86.0% (85.7-86.3) | 86.0% (85.7-86.2) |
| G3 Regigigas in play, own turn 1 | 76.3% (75.9-76.6) | 76.2% (75.8-76.6) | 76.2% (76.0-76.5) |
| G3 Regigigas in play, own turn 2 | 84.7% (84.3-85.0) | 84.6% (84.3-84.9) | 84.6% (84.4-84.8) |
| G3 Regigigas in play, own turn 3 | 89.3% (89.0-89.6) | 89.2% (89.0-89.5) | 89.3% (89.1-89.5) |
| G3 Regigigas in play, own turn 4 | 91.9% (91.6-92.1) | 91.9% (91.7-92.2) | 91.9% (91.7-92.1) |
| G3 Regigigas in play, own turn 5 | 93.2% (93.0-93.4) | 93.2% (93.0-93.4) | 93.2% (93.0-93.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 67.8% (67.4-68.2) | 67.9% (67.5-68.3) | 67.8% (67.6-68.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 82.5% (82.1-82.8) | 82.7% (82.4-83.1) | 82.6% (82.4-82.8) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 91.3% (91.0-91.5) | 91.4% (91.1-91.6) | 91.3% (91.1-91.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 96.1% (95.9-96.2) | 96.2% (96.1-96.4) | 96.2% (96.0-96.3) |
| G4.s2 a Stage 2 in play, own turn 2 | 8.2% (8.0-8.5) | 8.4% (8.1-8.6) | 8.3% (8.1-8.5) |
| G4.s2 a Stage 2 in play, own turn 3 | 14.8% (14.5-15.1) | 14.9% (14.6-15.3) | 14.9% (14.7-15.1) |
| G4.s2 a Stage 2 in play, own turn 4 | 23.3% (23.0-23.7) | 23.4% (23.0-23.8) | 23.4% (23.1-23.6) |
| G4.s2 a Stage 2 in play, own turn 5 | 33.4% (33.0-33.8) | 33.3% (32.9-33.8) | 33.4% (33.1-33.7) |
| G5.any3 an empty own turn among turns 1-3 | 32.9% (32.5-33.3) | 32.3% (31.9-32.7) | 32.6% (32.3-32.9) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 8.4% (8.1-8.6) | 4.2% (4.1-4.3) |
| G6 Kingambit with [DD] attached, own turn 3 | 13.2% (13.0-13.5) | 14.9% (14.6-15.3) | 14.1% (13.9-14.3) |
| G6 Kingambit with [DD] attached, own turn 4 | 23.3% (23.0-23.7) | 23.4% (23.0-23.8) | 23.4% (23.1-23.6) |
| G6 Kingambit with [DD] attached, own turn 5 | 33.4% (33.0-33.8) | 33.3% (32.9-33.8) | 33.4% (33.1-33.7) |
| G5 mean empty own turns in turns 1-5 | 0.868 | 0.854 | 0.861 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.6% / 10.0% [1-2] | 0.8% / 5.0% [1-1] |
| K3.by3 | 1.9% / 10.5% [1-3] | 1.9% / 10.3% [1-3] | 1.9% / 10.4% [1-3] |
| K3.by4 | 2.2% / 10.9% [1-3] | 3.8% / 12.2% [3-5] | 3.0% / 11.5% [2-4] |
| K3.by5 | 4.2% / 12.8% [3-6] | 4.3% / 20.2% [3-6] | 4.2% / 16.5% [3-6] |
| K3.by6 | 4.5% / 21.4% [3-7] | 8.0% / 31.9% [4-13] | 6.2% / 26.7% [4-9] |
| K3.by7 | 10.4% / 35.5% [4-19] | 8.2% / 54.4% [4-13] | 9.3% / 45.0% [4-16] |
| K3.by8 | 10.7% / 59.0% [4-19] | 8.3% / 60.0% [4-13] | 9.5% / 59.5% [4-16] |
| K3.never | 41.0% / 89.3% [16-65] | 40.0% / 91.7% [17-62] | 40.5% / 90.5% [17-64] |
| K3.k0 | 2.5% / 50.9% [2-4] | 2.2% / 53.9% [1-3] | 2.3% / 52.4% [1-3] |
| K3.k1 | 0.0% / 48.4% [0-0] | 0.0% / 51.7% [0-0] | 0.0% / 50.0% [0-0] |
| K3.k2 | 6.3% / 54.7% [1-14] | 4.9% / 56.6% [1-10] | 5.6% / 55.6% [1-12] |
| K3.k3p | 1.8% / 50.2% [0-5] | 1.2% / 52.9% [0-3] | 1.5% / 51.5% [0-4] |
| K4 | 8.1% / 57.8% [1-17] | 6.1% / 59.0% [2-11] | 7.1% / 58.4% [2-14] |
| K5 | 5.2% / 60.9% [4-6] | 6.4% / 58.6% [5-8] | 5.8% / 59.8% [4-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.3 points (-1.9 to -0.8); K3.by4: -1.6 points (-2.3 to -0.9); K3.by5: -1.8 points (-2.4 to -1.3); K3.by6: -2.6 points (-3.7 to -1.7); K3.by7: -3.9 points (-6.2 to -2.0); K3.by8: -5.2 points (-9.8 to -2.0); K3.k0: -1.6 points (-2.3 to -1.0); K3.k2: -1.2 points (-2.8 to -0.2); K4: -3.6 points (-8.2 to -0.3); K5: -2.4 points (-3.1 to -1.7).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.2% [2-2] | 1.1% [0-2] |
| K3.by3 | 1.7% / 13.0% [1-3] | 2.7% [2-3] | 2.2% / 7.8% [1-3] |
| K3.by4 | 2.0% / 13.3% [1-3] | 3.6% [3-4] | 2.8% / 8.5% [2-4] |
| K3.by5 | 4.2% / 15.5% [2-7] | 4.1% / 33.8% [4-4] | 4.1% / 24.6% [3-5] |
| K3.by6 | 4.5% / 15.8% [3-7] | 4.4% / 34.1% [4-5] | 4.5% / 25.0% [3-6] |
| K3.by7 | 12.6% / 35.1% [4-24] | 5.5% / 67.4% [4-9] | 9.1% / 51.2% [4-16] |
| K3.by8 | 12.6% / 55.5% [4-24] | 5.5% / 82.8% [4-9] | 9.1% / 69.2% [4-16] |
| K3.never | 44.5% / 87.4% [16-73] | 17.2% / 94.5% [0-45] | 30.9% / 90.9% [13-54] |
| K3.k0 | 2.3% / 45.2% [1-4] | 2.9% / 80.2% [2-4] | 2.6% / 62.7% [2-3] |
| K3.k1 | 0.0% / 42.9% [0-0] | 0.0% / 77.2% [0-0] | 0.0% / 60.1% [0-0] |
| K3.k2 | 7.8% / 50.8% [1-19] | 1.5% / 78.7% [0-2] | 4.7% / 64.7% [1-11] |
| K3.k3p | 2.5% / 45.5% [0-8] | 1.1% / 78.3% [0-3] | 1.8% / 61.9% [0-5] |
| K4 | 10.3% / 54.3% [1-22] | 2.6% / 82.1% [0-6] | 6.5% / 68.2% [2-14] |
| K5 | 5.3% / 52.8% [3-7] | 6.2% / 83.0% [5-7] | 5.8% / 67.9% [5-7] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.5 points (-2.1 to -0.9); K3.by4: -1.9 points (-2.6 to -1.3); K3.by5: -2.2 points (-2.8 to -1.6); K3.by6: -2.4 points (-3.1 to -1.7); K3.by7: -6.5 points (-12.6 to -2.2); K3.by8: -6.5 points (-12.6 to -2.2); K3.k0: -1.8 points (-2.6 to -1.1); K3.k2: -1.0 points (-2.3 to -0.2); K4: -4.6 points (-10.9 to -0.3); K5: -2.3 points (-3.0 to -1.5).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.9% [2-2] | 0.9% [1-1] |
| K3.by3 | 2.1% [2-2] | 2.2% [2-3] | 2.2% [2-2] |
| K3.by4 | 2.7% [2-3] | 3.2% [3-4] | 3.0% [3-3] |
| K3.by5 | 3.7% [3-4] | 5.0% [4-6] | 4.3% [4-5] |
| K3.by6 | 5.2% [4-6] | 6.2% / 10.2% [5-7] | 5.7% / 7.7% [5-7] |
| K3.by7 | 6.4% / 10.9% [5-8] | 6.9% / 16.6% [6-9] | 6.7% / 13.7% [5-8] |
| K3.by8 | 7.0% / 18.0% [5-9] | 7.4% / 18.7% [6-9] | 7.2% / 18.3% [6-9] |
| K3.never | 82.0% / 93.0% [74-89] | 81.3% / 92.6% [74-87] | 81.7% / 92.8% [74-88] |
| K3.k0 | 2.8% / 13.8% [2-3] | 2.4% / 13.7% [2-3] | 2.6% / 13.7% [2-3] |
| K3.k1 | 0.0% / 10.9% [0-0] | 0.0% / 11.3% [0-0] | 0.0% / 11.1% [0-0] |
| K3.k2 | 2.3% / 13.2% [1-3] | 2.8% / 14.1% [2-4] | 2.6% / 13.7% [2-4] |
| K3.k3p | 1.9% / 12.8% [1-3] | 2.2% / 13.5% [1-4] | 2.1% / 13.2% [1-3] |
| K4 | 4.2% / 15.6% [3-6] | 5.0% / 16.7% [4-7] | 4.6% / 16.2% [3-6] |
| K5 | 5.9% / 19.3% [5-6] | 7.5% / 19.2% [7-8] | 6.7% / 19.3% [6-7] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.3 points (-1.5 to -1.0); K3.by4: -1.6 points (-1.9 to -1.3); K3.by5: -2.2 points (-2.5 to -1.8); K3.by6: -3.0 points (-3.7 to -2.4); K3.by7: -4.2 points (-5.5 to -3.0); K3.by8: -5.1 points (-7.1 to -3.5); K3.never: +4.6 points (+3.0 to +6.6); K3.k0: -1.6 points (-1.9 to -1.2); K3.k3p: -2.7 points (-4.6 to -1.3); K4: -3.5 points (-5.4 to -2.0); K5: -2.9 points (-3.3 to -2.5).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.0% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by4 | 2.0% [2-2, Wilson] | 4.0% [4-4, Wilson] | 3.0% [3-3, Wilson] |
| K3.by5 | 6.9% [6-7, Wilson] | 4.4% [4-5, Wilson] | 5.6% [5-6, Wilson] |
| K3.by6 | 8.7% [8-9, Wilson] | 4.4% [4-5, Wilson] | 6.5% [6-7, Wilson] |
| K3.by7 | 8.7% [8-9, Wilson] | 4.4% [4-5, Wilson] | 6.5% [6-7, Wilson] |
| K3.by8 | 8.7% [8-9, Wilson] | 4.4% [4-5, Wilson] | 6.5% [6-7, Wilson] |
| K3.never | 91.3% [91-92, Wilson] | 95.6% [95-96, Wilson] | 93.5% [93-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.0% [2-2, Wilson] | 2.0% [2-2, Wilson] | 2.0% [2-2, Wilson] |
| K3.k3p | 6.8% [6-7, Wilson] | 2.4% [2-3, Wilson] | 4.6% [4-5, Wilson] |
| K4 | 8.7% [8-9, Wilson] | 4.4% [4-5, Wilson] | 6.5% [6-7, Wilson] |
| K5 | 13.1% [12-14, Wilson] | 18.6% [18-19, Wilson] | 15.8% [15-16, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by5: -3.8 points (-4.3 to -3.4); K3.by6: -4.6 points (-5.1 to -4.2); K3.by7: -4.6 points (-5.1 to -4.2); K3.by8: -4.6 points (-5.1 to -4.2); K3.never: +4.6 points (+4.2 to +5.1); K3.k3p: -4.2 points (-4.6 to -3.9); K4: -4.6 points (-5.1 to -4.2); K5: -5.9 points (-6.4 to -5.4).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| K3.by3 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.by4 | 2.5% [2-3, Wilson] | 4.3% [4-5, Wilson] | 3.4% [3-4, Wilson] |
| K3.by5 | 3.8% [3-4, Wilson] | 9.3% [9-10, Wilson] | 6.6% [6-7, Wilson] |
| K3.by6 | 10.9% [10-12, Wilson] | 11.1% [10-12, Wilson] | 11.0% [11-11, Wilson] |
| K3.by7 | 15.7% [15-16, Wilson] | 11.1% [10-12, Wilson] | 13.4% [13-14, Wilson] |
| K3.by8 | 15.7% [15-16, Wilson] | 11.1% [10-12, Wilson] | 13.4% [13-14, Wilson] |
| K3.never | 84.3% [84-85, Wilson] | 88.9% [88-90, Wilson] | 86.6% [86-87, Wilson] |
| K3.k0 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-2, Wilson] | 2.1% [2-2, Wilson] | 1.8% [2-2, Wilson] |
| K3.k3p | 11.8% [11-12, Wilson] | 6.7% [6-7, Wilson] | 9.3% [9-10, Wilson] |
| K4 | 13.2% [13-14, Wilson] | 8.8% [8-9, Wilson] | 11.0% [11-11, Wilson] |
| K5 | 8.8% [8-9, Wilson] | 12.9% [12-14, Wilson] | 10.8% [10-11, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.4 points (-1.6 to -1.2); K3.by4: -1.7 points (-1.9 to -1.4); K3.by5: -4.4 points (-4.8 to -4.0); K3.by6: -11.2 points (-11.7 to -10.6); K3.by7: -11.3 points (-11.9 to -10.8); K3.by8: -11.3 points (-11.9 to -10.8); K3.never: +11.3 points (+10.8 to +11.9); K3.k0: -1.4 points (-1.6 to -1.2); K3.k3p: -9.5 points (-10.0 to -9.0); K4: -9.9 points (-10.5 to -9.4); K5: -5.4 points (-5.9 to -5.0).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| K3.by3 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.by4 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.by5 | 2.5% [2-3, Wilson] | 5.8% [5-6, Wilson] | 4.1% [4-4, Wilson] |
| K3.by6 | 4.8% [4-5, Wilson] | 6.0% [6-6, Wilson] | 5.4% [5-6, Wilson] |
| K3.by7 | 4.9% [5-5, Wilson] | 28.0% [27-29, Wilson] | 16.5% [16-17, Wilson] |
| K3.by8 | 38.6% [38-40, Wilson] | 28.1% [27-29, Wilson] | 33.4% [33-34, Wilson] |
| K3.never | 61.4% [60-62, Wilson] | 71.9% [71-73, Wilson] | 66.6% [66-67, Wilson] |
| K3.k0 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.5% [2-3, Wilson] | 3.8% [3-4, Wilson] | 3.1% [3-3, Wilson] |
| K3.k3p | 33.7% [33-35, Wilson] | 22.1% [21-23, Wilson] | 27.9% [27-29, Wilson] |
| K4 | 36.2% [35-37, Wilson] | 25.9% [25-27, Wilson] | 31.0% [30-32, Wilson] |
| K5 | 6.3% [6-7, Wilson] | 7.5% [7-8, Wilson] | 6.9% [7-7, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.4 points (-1.6 to -1.2); K3.by4: -1.4 points (-1.6 to -1.2); K3.by5: -2.1 points (-2.4 to -1.8); K3.by6: -2.7 points (-3.1 to -2.4); K3.by7: -7.9 points (-8.5 to -7.4); K3.by8: -12.7 points (-13.4 to -12.1); K3.never: +12.7 points (+12.1 to +13.4); K3.k0: -1.4 points (-1.6 to -1.2); K3.k2: -1.4 points (-1.7 to -1.1); K3.k3p: -10.0 points (-10.6 to -9.3); K4: -11.3 points (-12.0 to -10.7); K5: -3.1 points (-3.4 to -2.8).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.0% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by4 | 2.0% [2-2, Wilson] | 3.8% [3-4, Wilson] | 2.9% [3-3, Wilson] |
| K3.by5 | 5.5% [5-6, Wilson] | 4.2% [4-5, Wilson] | 4.8% [5-5, Wilson] |
| K3.by6 | 7.5% [7-8, Wilson] | 4.2% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K3.by7 | 7.5% [7-8, Wilson] | 4.2% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K3.by8 | 7.5% [7-8, Wilson] | 4.2% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K3.never | 92.5% [92-93, Wilson] | 95.8% [95-96, Wilson] | 94.2% [94-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.0% [2-2, Wilson] | 2.0% [2-2, Wilson] | 2.0% [2-2, Wilson] |
| K3.k3p | 5.5% [5-6, Wilson] | 2.2% [2-2, Wilson] | 3.8% [4-4, Wilson] |
| K4 | 7.5% [7-8, Wilson] | 4.2% [4-5, Wilson] | 5.8% [6-6, Wilson] |
| K5 | 13.1% [12-14, Wilson] | 18.6% [18-19, Wilson] | 15.8% [15-16, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.0 points (-1.3 to -0.7); K3.by5: -4.2 points (-4.6 to -3.7); K3.by6: -4.9 points (-5.4 to -4.5); K3.by7: -4.9 points (-5.4 to -4.5); K3.by8: -4.9 points (-5.4 to -4.5); K3.never: +4.9 points (+4.5 to +5.4); K3.k3p: -4.5 points (-4.9 to -4.2); K4: -4.9 points (-5.4 to -4.5); K5: -5.9 points (-6.4 to -5.4).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| K3.by3 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.by4 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.by5 | 2.5% [2-3, Wilson] | 5.8% [5-6, Wilson] | 4.1% [4-4, Wilson] |
| K3.by6 | 4.8% [4-5, Wilson] | 6.0% [6-6, Wilson] | 5.4% [5-6, Wilson] |
| K3.by7 | 4.9% [5-5, Wilson] | 8.7% [8-9, Wilson] | 6.8% [6-7, Wilson] |
| K3.by8 | 6.8% [6-7, Wilson] | 8.8% [8-9, Wilson] | 7.8% [7-8, Wilson] |
| K3.by9 | 6.9% [6-7, Wilson] | 20.3% [20-21, Wilson] | 13.6% [13-14, Wilson] |
| K3.by10 | 21.7% [21-23, Wilson] | 20.3% [20-21, Wilson] | 21.0% [20-22, Wilson] |
| K3.never | 78.3% [77-79, Wilson] | 79.7% [79-80, Wilson] | 79.0% [78-80, Wilson] |
| K3.k0 | 2.5% [2-3, Wilson] | 2.2% [2-3, Wilson] | 2.3% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.5% [2-3, Wilson] | 3.8% [3-4, Wilson] | 3.1% [3-3, Wilson] |
| K3.k3p | 16.8% [16-18, Wilson] | 14.4% [14-15, Wilson] | 15.6% [15-16, Wilson] |
| K4 | 19.3% [19-20, Wilson] | 18.1% [17-19, Wilson] | 18.7% [18-19, Wilson] |
| K5 | 6.3% [6-7, Wilson] | 7.6% [7-8, Wilson] | 7.0% [7-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.4 points (-1.6 to -1.2); K3.by4: -1.4 points (-1.6 to -1.2); K3.by5: -2.1 points (-2.4 to -1.8); K3.by6: -2.7 points (-3.1 to -2.4); K3.by7: -13.3 points (-13.8 to -12.7); K3.by8: -29.3 points (-30.0 to -28.6); K3.by9: -27.1 points (-27.8 to -26.4); K3.by10: -22.8 points (-23.4 to -22.1); K3.never: +22.8 points (+22.1 to +23.4); K3.k0: -1.4 points (-1.6 to -1.2); K3.k2: -1.4 points (-1.7 to -1.1); K3.k3p: -20.0 points (-20.6 to -19.4); K4: -21.4 points (-22.0 to -20.7); K5: -3.1 points (-3.4 to -2.8).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.1 (+19.7 to +20.4) FLAG | +20.0 (+19.7 to +20.4) FLAG | +20.1 (+19.8 to +20.3) FLAG |
| K1 Pawniard in play at setup | -1.7 (-1.9 to -1.6) FLAG | -1.7 (-1.9 to -1.6) FLAG | -1.7 (-1.8 to -1.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -6.4 (-6.7 to -6.1) FLAG | -6.3 (-6.6 to -6.0) FLAG | -6.4 (-6.6 to -6.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -10.0 (-10.3 to -9.6) FLAG | -9.9 (-10.2 to -9.6) FLAG | -9.9 (-10.2 to -9.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -11.4 (-11.7 to -11.0) FLAG | -11.4 (-11.8 to -11.1) FLAG | -11.4 (-11.6 to -11.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -12.3 (-12.6 to -11.9) FLAG | -12.2 (-12.6 to -11.9) FLAG | -12.2 (-12.5 to -12.0) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -12.9 (-13.3 to -12.6) FLAG | -12.9 (-13.2 to -12.5) FLAG | -12.9 (-13.2 to -12.7) FLAG |
| K2 Kingambit in play, own turn 2 | -2.5 (-2.7 to -2.3) FLAG | -2.4 (-2.6 to -2.2) FLAG | -2.4 (-2.6 to -2.3) FLAG |
| K2 Kingambit in play, own turn 3 | -6.3 (-6.5 to -6.0) FLAG | -6.2 (-6.4 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| K2 Kingambit in play, own turn 4 | -9.7 (-10.0 to -9.3) FLAG | -9.7 (-10.1 to -9.4) FLAG | -9.7 (-9.9 to -9.5) FLAG |
| K2 Kingambit in play, own turn 5 | -13.0 (-13.4 to -12.6) FLAG | -13.1 (-13.5 to -12.7) FLAG | -13.0 (-13.3 to -12.8) FLAG |
| K2 Kingambit in play, own turn 6 | -15.5 (-15.9 to -15.1) FLAG | -15.5 (-15.9 to -15.0) FLAG | -15.5 (-15.8 to -15.2) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | -1.6 (-2.0 to -1.2) FLAG | -1.4 (-1.8 to -1.0) FLAG | -1.5 (-1.8 to -1.2) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | -1.5 (-2.0 to -1.1) FLAG | -1.2 (-1.6 to -0.8) FLAG | -1.4 (-1.7 to -1.1) FLAG |
| G3 Pawniard in play, own turn 1 | -6.4 (-6.7 to -6.1) FLAG | -6.3 (-6.6 to -6.0) FLAG | -6.4 (-6.6 to -6.1) FLAG |
| G3 Pawniard in play, own turn 2 | -7.5 (-7.8 to -7.1) FLAG | -7.5 (-7.9 to -7.2) FLAG | -7.5 (-7.7 to -7.2) FLAG |
| G3 Pawniard in play, own turn 3 | -5.1 (-5.5 to -4.7) FLAG | -5.2 (-5.6 to -4.9) FLAG | -5.2 (-5.5 to -4.9) FLAG |
| G3 Pawniard in play, own turn 4 | -2.6 (-3.0 to -2.2) FLAG | -2.5 (-2.9 to -2.1) FLAG | -2.5 (-2.8 to -2.3) FLAG |
| G3 Kingambit in play, own turn 2 | -2.5 (-2.7 to -2.3) FLAG | -2.4 (-2.6 to -2.2) FLAG | -2.4 (-2.6 to -2.3) FLAG |
| G3 Kingambit in play, own turn 3 | -6.3 (-6.5 to -6.0) FLAG | -6.2 (-6.4 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| G3 Kingambit in play, own turn 4 | -9.7 (-10.0 to -9.3) FLAG | -9.7 (-10.1 to -9.4) FLAG | -9.7 (-9.9 to -9.5) FLAG |
| G3 Kingambit in play, own turn 5 | -13.0 (-13.4 to -12.6) FLAG | -13.1 (-13.5 to -12.7) FLAG | -13.0 (-13.3 to -12.8) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -6.4 (-6.7 to -6.1) FLAG | -6.4 (-6.7 to -6.1) FLAG | -6.4 (-6.6 to -6.2) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -6.7 (-7.0 to -6.3) FLAG | -6.7 (-7.1 to -6.4) FLAG | -6.7 (-7.0 to -6.4) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -4.1 (-4.5 to -3.8) FLAG | -4.1 (-4.5 to -3.8) FLAG | -4.1 (-4.4 to -3.9) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -2.6 (-2.9 to -2.2) FLAG | -2.8 (-3.1 to -2.4) FLAG | -2.7 (-2.9 to -2.4) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -1.8 (-2.2 to -1.5) FLAG | -2.4 (-2.7 to -2.1) FLAG | -2.1 (-2.4 to -1.9) FLAG |
| G3 Alolan Muk in play, own turn 2 | -2.7 (-3.0 to -2.4) FLAG | -2.6 (-2.9 to -2.3) FLAG | -2.7 (-2.9 to -2.5) FLAG |
| G3 Alolan Muk in play, own turn 3 | -6.6 (-7.0 to -6.3) FLAG | -6.6 (-7.0 to -6.2) FLAG | -6.6 (-6.9 to -6.4) FLAG |
| G3 Alolan Muk in play, own turn 4 | -8.9 (-9.3 to -8.5) FLAG | -8.7 (-9.1 to -8.3) FLAG | -8.8 (-9.0 to -8.5) FLAG |
| G3 Alolan Muk in play, own turn 5 | -10.1 (-10.5 to -9.6) FLAG | -9.6 (-10.0 to -9.2) FLAG | -9.8 (-10.1 to -9.5) FLAG |
| G3 Glimmet in play, own turn 1 | -6.2 (-6.5 to -5.9) FLAG | -6.5 (-6.8 to -6.2) FLAG | -6.3 (-6.5 to -6.2) FLAG |
| G3 Glimmet in play, own turn 2 | -6.8 (-7.2 to -6.4) FLAG | -6.7 (-7.1 to -6.4) FLAG | -6.8 (-7.0 to -6.5) FLAG |
| G3 Glimmet in play, own turn 3 | -3.5 (-3.9 to -3.1) FLAG | -3.6 (-4.0 to -3.2) FLAG | -3.5 (-3.8 to -3.2) FLAG |
| G3 Glimmet in play, own turn 4 | -1.1 (-1.5 to -0.7) FLAG | -1.0 (-1.4 to -0.6) FLAG | -1.1 (-1.3 to -0.8) FLAG |
| G3 Glimmora in play, own turn 2 | -8.6 (-8.9 to -8.3) FLAG | -8.5 (-8.8 to -8.2) FLAG | -8.5 (-8.8 to -8.3) FLAG |
| G3 Glimmora in play, own turn 3 | -11.0 (-11.3 to -10.7) FLAG | -10.8 (-11.1 to -10.4) FLAG | -10.9 (-11.1 to -10.6) FLAG |
| G3 Glimmora in play, own turn 4 | -10.5 (-10.8 to -10.2) FLAG | -10.3 (-10.6 to -10.0) FLAG | -10.4 (-10.6 to -10.2) FLAG |
| G3 Glimmora in play, own turn 5 | -9.2 (-9.5 to -8.9) FLAG | -9.1 (-9.4 to -8.8) FLAG | -9.1 (-9.3 to -9.0) FLAG |
| G3 Regigigas in play, own turn 1 | +20.9 (+20.5 to +21.3) FLAG | +21.0 (+20.6 to +21.4) FLAG | +20.9 (+20.7 to +21.2) FLAG |
| G3 Regigigas in play, own turn 2 | +17.0 (+16.6 to +17.4) FLAG | +17.5 (+17.1 to +17.8) FLAG | +17.2 (+17.0 to +17.5) FLAG |
| G3 Regigigas in play, own turn 3 | +14.9 (+14.5 to +15.2) FLAG | +15.1 (+14.7 to +15.4) FLAG | +15.0 (+14.7 to +15.2) FLAG |
| G3 Regigigas in play, own turn 4 | +13.6 (+13.3 to +14.0) FLAG | +13.8 (+13.5 to +14.1) FLAG | +13.7 (+13.5 to +14.0) FLAG |
| G3 Regigigas in play, own turn 5 | +12.9 (+12.6 to +13.2) FLAG | +13.0 (+12.7 to +13.3) FLAG | +12.9 (+12.7 to +13.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -7.7 (-8.1 to -7.4) FLAG | -7.8 (-8.1 to -7.4) FLAG | -7.7 (-8.0 to -7.5) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -7.2 (-7.5 to -6.9) FLAG | -7.0 (-7.3 to -6.7) FLAG | -7.1 (-7.3 to -6.9) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -4.7 (-4.9 to -4.5) FLAG | -4.5 (-4.7 to -4.2) FLAG | -4.6 (-4.7 to -4.4) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -2.5 (-2.7 to -2.4) FLAG | -2.4 (-2.5 to -2.2) FLAG | -2.5 (-2.6 to -2.3) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | -2.5 (-2.7 to -2.3) FLAG | -2.4 (-2.6 to -2.2) FLAG | -2.4 (-2.6 to -2.3) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -6.3 (-6.5 to -6.0) FLAG | -6.2 (-6.4 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -9.7 (-10.0 to -9.3) FLAG | -9.7 (-10.1 to -9.4) FLAG | -9.7 (-9.9 to -9.5) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -13.0 (-13.4 to -12.6) FLAG | -13.1 (-13.5 to -12.7) FLAG | -13.0 (-13.3 to -12.8) FLAG |
| G5.any3 an empty own turn among turns 1-3 | +9.7 (+9.4 to +10.1) FLAG | +9.8 (+9.5 to +10.2) FLAG | +9.8 (+9.6 to +10.0) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | -2.4 (-2.6 to -2.2) FLAG | -1.2 (-1.3 to -1.1) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -4.3 (-4.6 to -4.1) FLAG | -6.2 (-6.4 to -5.9) FLAG | -5.2 (-5.4 to -5.1) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -9.7 (-10.0 to -9.3) FLAG | -9.7 (-10.1 to -9.4) FLAG | -9.7 (-9.9 to -9.5) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -13.0 (-13.4 to -12.6) FLAG | -13.1 (-13.5 to -12.7) FLAG | -13.0 (-13.3 to -12.8) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.103 (+0.097 to +0.108) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Copycat B1 225 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.1 points
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn -4.4 points (-5.4 to -3.3); P2 both Glimmora had their turn -13.5 points (-18.0 to -9.4); P2 the first Glimmora placed had its turn -3.2 points (-4.8 to -1.1); P2 the second Glimmora placed had its turn -14.7 points (-19.0 to -10.6); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.5 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -3.2 points (-7.7 to -0.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -10.4 points (-13.8 to -7.5)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -4.8 points (-5.8 to -4.0); P2 both Glimmora had their turn -13.1 points (-17.9 to -9.8); P2 the first Glimmora placed had its turn -4.2 points (-5.5 to -3.3); P2 the second Glimmora placed had its turn -13.8 points (-18.4 to -10.6); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.7 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.5 points (-10.8 to -0.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -11.5 points (-15.6 to -7.1)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -6.3 points (-7.4 to -5.2); P2 both Glimmora had their turn -14.2 points (-16.1 to -12.3); P2 the first Glimmora placed had its turn -4.5 points (-5.5 to -3.5); P2 the second Glimmora placed had its turn -16.0 points (-17.6 to -14.3); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -10.8 points (-13.4 to -8.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -16.2 points (-18.4 to -14.0); P4 ready at the winning moment: Knocks out their strongest -1.0 points (-1.9 to -0.3); P4 the moment came and Kingambit was never ready in the deal +1.2 points (+0.5 to +2.0); P5 plan reached in time: Knocks out their strongest -1.2 points (-2.0 to -0.6)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn -5.7 points (-6.3 to -5.1); P2 both Glimmora had their turn -6.8 points (-7.3 to -6.3); P2 the first Glimmora placed had its turn -1.5 points (-2.0 to -0.9); P2 the second Glimmora placed had its turn -11.1 points (-11.6 to -10.5); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -7.1 points (-7.6 to -6.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -17.2 points (-17.9 to -16.6); P4 ready at the winning moment: Knocks out their strongest -3.1 points (-3.5 to -2.7); P4 ready at the winning moment: Wins outright (a lower bound) -3.1 points (-3.5 to -2.7); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.6 points (+3.1 to +4.0); P5 plan reached in time: Knocks out their strongest -3.5 points (-4.0 to -3.1); P5 plan reached in time: Wins outright (a lower bound) -3.5 points (-4.0 to -3.1)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn -7.1 points (-7.6 to -6.6); P2 both Glimmora had their turn -12.8 points (-13.4 to -12.2); P2 the first Glimmora placed had its turn -6.2 points (-6.7 to -5.7); P2 the second Glimmora placed had its turn -13.7 points (-14.3 to -13.0); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.4 points (-14.0 to -12.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -22.8 points (-23.4 to -22.1); P4 ready at the winning moment: Knocks out their strongest -5.4 points (-5.9 to -4.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +6.3 points (+5.8 to +6.8); P5 plan reached in time: Knocks out their strongest -6.0 points (-6.5 to -5.4)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn -4.6 points (-5.0 to -4.2); P2 both Glimmora had their turn -21.4 points (-22.1 to -20.7); P2 the first Glimmora placed had its turn -3.4 points (-3.8 to -3.0); P2 the second Glimmora placed had its turn -22.6 points (-23.3 to -21.8); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -2.7 points (-3.0 to -2.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -15.2 points (-15.8 to -14.7); P4 ready at the winning moment: Knocks out their strongest -6.2 points (-6.8 to -5.6); P4 ready at the winning moment: Wins outright (a lower bound) -6.2 points (-6.8 to -5.6); P4 not ready, ready 1 turn late +1.1 points (+0.9 to +1.4); P4 the moment came and Kingambit was never ready in the deal -2.4 points (-2.9 to -2.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +7.5 points (+7.0 to +7.9); P5 plan reached in time: Knocks out their strongest -5.1 points (-5.6 to -4.5); P5 plan reached in time: Wins outright (a lower bound) -5.1 points (-5.6 to -4.5)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn -5.7 points (-6.3 to -5.1); P2 both Glimmora had their turn -6.9 points (-7.4 to -6.4); P2 the first Glimmora placed had its turn -1.5 points (-2.0 to -0.9); P2 the second Glimmora placed had its turn -11.1 points (-11.7 to -10.5); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -7.9 points (-8.5 to -7.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -17.2 points (-17.9 to -16.6); P4 the moment came and Kingambit was never ready in the deal -1.1 points (-1.4 to -0.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +1.6 points (+1.4 to +1.9)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn -4.4 points (-4.8 to -4.0); P2 both Glimmora had their turn -15.1 points (-15.8 to -14.5); P2 the first Glimmora placed had its turn -3.4 points (-3.8 to -3.0); P2 the second Glimmora placed had its turn -16.2 points (-16.8 to -15.5); P3 plan broken in front, cause: Pawniard forced to lead -4.2 points (-4.6 to -3.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -28.7 points (-29.3 to -28.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -25.8 points (-26.5 to -25.1); P4 ready at the winning moment: Knocks out their strongest +7.4 points (+7.0 to +7.9); P4 ready at the winning moment: Wins outright (a lower bound) +7.4 points (+7.0 to +7.9); P4 the moment came and Kingambit was never ready in the deal -9.4 points (-9.8 to -9.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +1.9 points (+1.6 to +2.2); P5 plan reached in time: Knocks out their strongest +7.5 points (+7.0 to +7.9); P5 plan reached in time: Wins outright (a lower bound) +7.5 points (+7.0 to +7.9)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): G3 Regigigas in play, own turn 1 +20.9 points; G3 Regigigas in play, own turn 2 +17.2 points; G3 Regigigas in play, own turn 3 +15.0 points; G3 Regigigas in play, own turn 4 +13.7 points; G3 Regigigas in play, own turn 5 +12.9 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.7 points; K1 Pawniard line in play (end of own turn t), own turn 1 -6.4 points; K1 Pawniard line in play (end of own turn t), own turn 2 -9.9 points; K1 Pawniard line in play (end of own turn t), own turn 3 -11.4 points; K1 Pawniard line in play (end of own turn t), own turn 4 -12.2 points; K1 Pawniard line in play (end of own turn t), own turn 5 -12.9 points; K2 Kingambit in play, own turn 2 -2.4 points; K2 Kingambit in play, own turn 3 -6.2 points; K2 Kingambit in play, own turn 4 -9.7 points; K2 Kingambit in play, own turn 5 -13.0 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 -1.3; K3.by4 -1.6; K3.by5 -1.8; K3.by6 -2.6; K3.by7 -3.9; K3.by8 -5.2; K3.k0 -1.6; K3.k2 -1.2; K4 -3.6; K5 -2.4; C-his, seat-matched: K3.by3 -1.5; K3.by4 -1.9; K3.by5 -2.2; K3.by6 -2.4; K3.by7 -6.5; K3.by8 -6.5; K3.k0 -1.8; K3.k2 -1.0; K4 -4.6; K5 -2.3; C-bot: K3.by3 -1.3; K3.by4 -1.6; K3.by5 -2.2; K3.by6 -3.0; K3.by7 -4.2; K3.by8 -5.1; K3.never +4.6; K3.k0 -1.6; K3.k3p -2.7; K4 -3.5; K5 -2.9; C-fixed fast: K3.by5 -3.8; K3.by6 -4.6; K3.by7 -4.6; K3.by8 -4.6; K3.never +4.6; K3.k3p -4.2; K4 -4.6; K5 -5.9; C-fixed medium: K3.by3 -1.4; K3.by4 -1.7; K3.by5 -4.4; K3.by6 -11.2; K3.by7 -11.3; K3.by8 -11.3; K3.never +11.3; K3.k0 -1.4; K3.k3p -9.5; K4 -9.9; K5 -5.4; C-fixed slow: K3.by3 -1.4; K3.by4 -1.4; K3.by5 -2.1; K3.by6 -2.7; K3.by7 -7.9; K3.by8 -12.7; K3.never +12.7; K3.k0 -1.4; K3.k2 -1.4; K3.k3p -10.0; K4 -11.3; K5 -3.1; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.0; K3.by5 -4.2; K3.by6 -4.9; K3.by7 -4.9; K3.by8 -4.9; K3.never +4.9; K3.k3p -4.5; K4 -4.9; K5 -5.9; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.4; K3.by4 -1.4; K3.by5 -2.1; K3.by6 -2.7; K3.by7 -13.3; K3.by8 -29.3; K3.by9 -27.1; K3.by10 -22.8; K3.never +22.8; K3.k0 -1.4; K3.k2 -1.4; K3.k3p -20.0; K4 -21.4; K5 -3.1.
Not valued here (changed cards the script never plays: they count as blanks): none.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Lucky Ice Pop B2 145 +1 Regigigas B3 134 (card-list id 59407df8dd79)

Changes: ['-1 Lucky Ice Pop B2 145', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 285,562; the valuation and the fallback rule disagree at 112,615 of 285,562 Copycat decisions (39.4%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 48.7% (48.3-49.2) | 48.8% (48.3-49.2) | 48.7% (48.4-49.1) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.7% / 96.2% [74-95] | 78.5% / 92.1% [63-90] | 82.6% / 94.1% [69-92] |
| P2 both Glimmora had their turn | 28.0% / 65.9% [20-36] | 25.2% / 67.4% [17-34] | 26.6% / 66.7% [19-34] |
| P2 the first Glimmora placed had its turn | 84.4% / 92.4% [72-93] | 72.9% / 83.8% [57-86] | 78.7% / 88.1% [65-89] |
| P2 the second Glimmora placed had its turn | 30.3% / 65.3% [21-38] | 30.8% / 67.8% [22-40] | 30.6% / 66.6% [22-39] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10] | 8.5% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.0% / 49.3% [0-2] | 2.2% / 56.3% [1-4] | 1.6% / 52.8% [1-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 15.0% / 58.2% [13-18] | 19.1% / 65.3% [15-23] | 17.0% / 61.7% [14-20] |
| P4 ready at the winning moment: Knocks out their strongest | 13.8% / 39.3% [3-27] | 10.4% / 39.1% [2-20] | 12.1% / 39.2% [3-23] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.9% / 28.4% [0-9] | 2.2% / 30.8% [0-7] | 2.5% / 29.6% [0-8] |
| P4 not ready, ready 1 turn late | 4.8% / 47.4% [0-12] | 4.2% / 51.1% [0-10] | 4.5% / 49.2% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.5% / 44.0% [0-5] | 1.5% / 48.4% [0-5] | 1.5% / 46.2% [0-5] |
| P4 the moment came and Kingambit was never ready in the deal | 8.2% / 50.7% [0-20] | 9.2% / 56.1% [0-22] | 8.7% / 53.4% [0-21] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.2% / 54.8% [8-54] | 27.8% / 56.5% [9-52] | 28.5% / 55.6% [8-52] |
| P5 plan reached in time: Knocks out their strongest | 20.1% / 62.6% [7-36] | 16.1% / 63.0% [5-29] | 18.1% / 62.8% [6-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.3% / 45.8% [0-10] | 2.6% / 49.5% [0-8] | 2.9% / 47.6% [0-9] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 48.7% of 2828 [23-72] | 41.1% of 2532 [21-65] | 45.1% of 5360 [22-69] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.1% of 2828 [0-40] | 8.5% of 2532 [0-38] | 9.4% of 5360 [0-39] |
| P4 not ready, ready 1 turn late | 17.1% of 2828 [0-56] | 16.6% of 2532 [0-52] | 16.9% of 5360 [0-54] |
| P4 not ready, ready 2 or more turns late | 5.3% of 2828 [0-19] | 5.9% of 2532 [0-21] | 5.6% of 5360 [0-20] |
| P4 the moment came and Kingambit was never ready in the deal | 28.9% of 2828 [0-52] | 36.4% of 2532 [0-64] | 32.4% of 5360 [0-58] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: -9.1 points (-12.7 to -5.9); P2.g2: -10.7 points (-14.1 to -7.5); P3.pawn_lead: -4.1 points (-4.5 to -3.8); P3.pawn_promo: -4.4 points (-9.2 to -1.3); P3.grimer_muk: -13.1 points (-17.2 to -9.4); P4.nomoment: -1.8 points (-3.2 to -0.7).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.2% / 95.9% [68-95] | 87.3% / 95.6% [77-95] | 86.3% / 95.8% [76-93] |
| P2 both Glimmora had their turn | 27.8% / 60.8% [18-37] | 26.6% / 83.1% [17-45] | 27.2% / 72.0% [19-37] |
| P2 the first Glimmora placed had its turn | 82.8% / 92.3% [66-93] | 84.4% / 88.1% [73-94] | 83.6% / 90.2% [74-91] |
| P2 the second Glimmora placed had its turn | 30.2% / 60.6% [20-41] | 29.5% / 79.2% [18-49] | 29.8% / 69.9% [21-40] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10] | 8.5% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 0.9% / 44.1% [0-2] | 2.9% / 80.9% [0-5] | 1.9% / 62.5% [0-3] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 14.9% / 53.4% [12-18] | 19.6% / 87.1% [11-27] | 17.2% / 70.2% [13-21] |
| P4 ready at the winning moment: Knocks out their strongest | 17.1% / 39.6% [2-34] | 4.1% / 55.9% [0-12] | 10.6% / 47.7% [2-22] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.5% / 27.0% [0-14] | 0.0% / 51.8% [0-0] | 2.2% / 39.4% [0-9] |
| P4 not ready, ready 1 turn late | 6.4% / 42.1% [0-16] | 0.0% / 79.1% [0-0] | 3.2% / 60.6% [0-10] |
| P4 not ready, ready 2 or more turns late | 1.9% / 37.6% [0-6] | 0.0% / 79.1% [0-0] | 1.0% / 58.4% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 11.5% / 47.2% [0-27] | 0.0% / 79.1% [0-0] | 5.7% / 63.1% [0-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 27.4% / 49.9% [5-57] | 16.9% / 68.7% [0-44] | 22.1% / 59.3% [7-43] |
| P5 plan reached in time: Knocks out their strongest | 25.4% / 61.1% [8-45] | 4.1% / 83.2% [0-12] | 14.8% / 72.2% [5-30] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.0% / 40.7% [0-15] | 0.0% / 79.1% [0-0] | 2.5% / 59.9% [0-10] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 46.3% of 3692 [14-67] | 100.0% of 407 [100-100] | 51.6% of 4099 [27-75] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.2% of 3692 [0-45] | 0.0% of 407 [0-0] | 11.0% of 4099 [0-38] |
| P4 not ready, ready 1 turn late | 17.4% of 3692 [0-65] | 0.0% of 407 [0-0] | 15.7% of 4099 [0-46] |
| P4 not ready, ready 2 or more turns late | 5.2% of 3692 [0-21] | 0.0% of 407 [0-0] | 4.7% of 4099 [0-15] |
| P4 the moment came and Kingambit was never ready in the deal | 31.1% of 3692 [0-56] | 0.0% of 407 [0-0] | 28.0% of 4099 [0-50] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -1.3 points (-2.2 to -0.8); P2.both: -8.1 points (-12.2 to -4.7); P2.g2: -9.4 points (-13.5 to -6.2); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -5.7 points (-13.1 to -0.9); P3.grimer_muk: -14.1 points (-19.0 to -9.3).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.0% / 90.2% [85-92] | 82.0% / 83.7% [78-86] | 85.5% / 87.0% [82-89] |
| P2 both Glimmora had their turn | 30.5% / 37.9% [27-34] | 25.5% / 33.7% [22-29] | 28.0% / 35.8% [25-31] |
| P2 the first Glimmora placed had its turn | 84.1% / 84.4% [79-89] | 74.2% / 74.7% [69-80] | 79.1% / 79.5% [74-84] |
| P2 the second Glimmora placed had its turn | 35.4% / 42.2% [32-38] | 33.2% / 40.0% [30-36] | 34.3% / 41.1% [31-37] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10] | 8.5% [8-9] | 8.7% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.0% / 13.5% [1-3] | 3.7% / 16.2% [3-5] | 2.9% / 14.8% [2-4] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 16.1% / 26.2% [15-17] | 21.4% / 31.9% [20-23] | 18.7% / 29.1% [17-20] |
| P4 ready at the winning moment: Knocks out their strongest | 7.4% / 13.7% [4-12] | 6.6% / 14.0% [4-10] | 7.0% / 13.9% [4-11] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.3% / 6.6% [0-1] | 0.6% / 8.1% [0-2] | 0.5% / 7.3% [0-1] |
| P4 not ready, ready 1 turn late | 5.5% / 13.6% [3-9] | 4.3% / 14.1% [2-7] | 4.9% / 13.9% [3-8] |
| P4 not ready, ready 2 or more turns late | 1.7% / 9.8% [1-3] | 2.2% / 12.0% [1-4] | 1.9% / 10.9% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 8.3% / 16.5% [4-14] | 9.3% / 19.1% [4-15] | 8.8% / 17.8% [4-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 68.9% / 75.2% [57-80] | 67.8% / 75.2% [57-78] | 68.4% / 75.2% [57-79] |
| P5 plan reached in time: Knocks out their strongest | 14.6% / 22.7% [8-22] | 13.1% / 22.9% [8-19] | 13.8% / 22.8% [8-21] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.5% / 8.6% [0-1] | 0.7% / 10.4% [0-2] | 0.6% / 9.5% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 32.3% of 2293 [21-46] | 29.5% of 2240 [21-40] | 30.9% of 4533 [21-43] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.4% of 2293 [0-5] | 2.9% of 2240 [0-10] | 2.1% of 4533 [0-6] |
| P4 not ready, ready 1 turn late | 24.0% of 2293 [16-33] | 19.2% of 2240 [13-25] | 21.6% of 4533 [15-29] |
| P4 not ready, ready 2 or more turns late | 7.4% of 2293 [3-12] | 9.8% of 2240 [4-16] | 8.6% of 4533 [4-13] |
| P4 the moment came and Kingambit was never ready in the deal | 36.3% of 2293 [23-50] | 41.5% of 2240 [28-54] | 38.9% of 4533 [25-52] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -1.6 points (-2.6 to -0.6); P2.both: -9.0 points (-10.9 to -7.2); P2.g2: -10.9 points (-12.6 to -9.2); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -13.0 points (-15.9 to -10.1); P3.grimer_muk: -20.7 points (-23.3 to -18.2); P4.nomoment: -1.1 points (-1.6 to -0.5).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.0% [80-82, Wilson] | 56.3% [55-57, Wilson] | 68.6% [68-69, Wilson] |
| P2 both Glimmora had their turn | 25.1% [24-26, Wilson] | 9.5% [9-10, Wilson] | 17.3% [17-18, Wilson] |
| P2 the first Glimmora placed had its turn | 77.2% [76-78, Wilson] | 41.6% [41-43, Wilson] | 59.4% [59-60, Wilson] |
| P2 the second Glimmora placed had its turn | 28.9% [28-30, Wilson] | 24.2% [23-25, Wilson] | 26.6% [26-27, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10, Wilson] | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 7.8% [7-8, Wilson] | 11.8% [11-12, Wilson] | 9.8% [9-10, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.5% [31-32, Wilson] | 37.6% [37-39, Wilson] | 34.6% [34-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 17.0% [16-18, Wilson] | 6.6% [6-7, Wilson] | 11.8% [11-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 17.0% [16-18, Wilson] | 6.6% [6-7, Wilson] | 11.8% [11-12, Wilson] |
| P4 not ready, ready 1 turn late | 2.9% [3-3, Wilson] | 1.0% [1-1, Wilson] | 1.9% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.9% [24-26, Wilson] | 21.0% [20-22, Wilson] | 23.0% [22-24, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 55.2% [54-56, Wilson] | 71.4% [70-72, Wilson] | 63.3% [63-64, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 19.9% [19-21, Wilson] | 7.6% [7-8, Wilson] | 13.7% [13-14, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 19.9% [19-21, Wilson] | 7.6% [7-8, Wilson] | 13.7% [13-14, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 38.0% of 4479 [37-39, Wilson] | 22.9% of 2863 [21-24, Wilson] | 32.1% of 7342 [31-33, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 38.0% of 4479 [37-39, Wilson] | 22.9% of 2863 [21-24, Wilson] | 32.1% of 7342 [31-33, Wilson] |
| P4 not ready, ready 1 turn late | 6.4% of 4479 [6-7, Wilson] | 3.6% of 2863 [3-4, Wilson] | 5.3% of 7342 [5-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4479 [0-0, Wilson] | 0.0% of 2863 [0-0, Wilson] | 0.0% of 7342 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 55.6% of 4479 [54-57, Wilson] | 73.5% of 2863 [72-75, Wilson] | 62.6% of 7342 [61-64, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.2 points (+0.8 to +1.7); P2.g1: +4.4 points (+3.9 to +4.9); P2.g2: -4.1 points (-4.7 to -3.6); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -10.5 points (-11.1 to -10.0); P3.grimer_muk: -21.4 points (-22.1 to -20.7); P4.ko: +1.1 points (+0.7 to +1.4); P4.win: +1.1 points (+0.7 to +1.4); P4.never: +1.8 points (+1.3 to +2.3); P4.nomoment: -3.4 points (-3.9 to -3.0); P5.ko: +1.6 points (+1.3 to +2.0); P5.win: +1.6 points (+1.3 to +2.0).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.2% [89-90, Wilson] | 81.0% [80-82, Wilson] | 85.1% [85-86, Wilson] |
| P2 both Glimmora had their turn | 31.5% [31-32, Wilson] | 25.3% [24-26, Wilson] | 28.4% [28-29, Wilson] |
| P2 the first Glimmora placed had its turn | 87.2% [86-88, Wilson] | 77.5% [77-78, Wilson] | 82.3% [82-83, Wilson] |
| P2 the second Glimmora placed had its turn | 33.5% [33-34, Wilson] | 28.8% [28-30, Wilson] | 31.2% [31-32, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10, Wilson] | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 5.6% [5-6, Wilson] | 8.9% [8-10, Wilson] | 7.3% [7-8, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 23.8% [23-25, Wilson] | 32.5% [32-33, Wilson] | 28.2% [28-29, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 28.2% [27-29, Wilson] | 17.3% [17-18, Wilson] | 22.8% [22-23, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 3.1% [3-3, Wilson] | 2.9% [3-3, Wilson] | 3.0% [3-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 21.8% [21-23, Wilson] | 25.6% [25-27, Wilson] | 23.7% [23-24, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 46.9% [46-48, Wilson] | 54.1% [53-55, Wilson] | 50.5% [50-51, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 31.3% [30-32, Wilson] | 20.2% [19-21, Wilson] | 25.8% [25-26, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 53.1% of 5309 [52-54, Wilson] | 37.7% of 4589 [36-39, Wilson] | 46.0% of 9898 [45-47, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5309 [0-0, Wilson] | 0.0% of 4589 [0-0, Wilson] | 0.0% of 9898 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 5.9% of 5309 [5-7, Wilson] | 6.4% of 4589 [6-7, Wilson] | 6.1% of 9898 [6-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5309 [0-0, Wilson] | 0.0% of 4589 [0-0, Wilson] | 0.0% of 9898 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 41.0% of 5309 [40-42, Wilson] | 55.9% of 4589 [54-57, Wilson] | 47.9% of 9898 [47-49, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.both: -5.5 points (-6.1 to -5.0); P2.g2: -6.7 points (-7.3 to -6.1); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -16.7 points (-17.3 to -16.1); P3.grimer_muk: -28.5 points (-29.2 to -27.9); P4.ko: +1.0 points (+0.6 to +1.5); P4.never: -1.2 points (-1.7 to -0.7); P5.ko: +1.7 points (+1.2 to +2.1).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.2% [95-96, Wilson] | 89.8% [89-90, Wilson] | 92.5% [92-93, Wilson] |
| P2 both Glimmora had their turn | 52.4% [51-53, Wilson] | 45.3% [44-46, Wilson] | 48.8% [48-50, Wilson] |
| P2 the first Glimmora placed had its turn | 91.5% [91-92, Wilson] | 84.1% [83-85, Wilson] | 87.8% [87-88, Wilson] |
| P2 the second Glimmora placed had its turn | 56.1% [55-57, Wilson] | 51.0% [50-52, Wilson] | 53.5% [53-54, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10, Wilson] | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.0% [1-1, Wilson] | 2.9% [3-3, Wilson] | 1.9% [2-2, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 13.9% [13-15, Wilson] | 18.6% [18-19, Wilson] | 16.3% [16-17, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 50.7% [50-52, Wilson] | 43.0% [42-44, Wilson] | 46.8% [46-48, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 50.7% [50-52, Wilson] | 43.0% [42-44, Wilson] | 46.8% [46-48, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 4.4% [4-5, Wilson] | 2.2% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 9.0% [8-10, Wilson] | 8.3% [8-9, Wilson] | 8.6% [8-9, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 40.3% [39-41, Wilson] | 44.4% [43-45, Wilson] | 42.3% [42-43, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 50.7% [50-52, Wilson] | 47.4% [46-48, Wilson] | 49.0% [48-50, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 50.7% [50-52, Wilson] | 47.4% [46-48, Wilson] | 49.0% [48-50, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 84.9% of 5972 [84-86, Wilson] | 77.2% of 5565 [76-78, Wilson] | 81.2% of 11537 [80-82, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 84.9% of 5972 [84-86, Wilson] | 77.2% of 5565 [76-78, Wilson] | 81.2% of 11537 [80-82, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5972 [0-0, Wilson] | 7.9% of 5565 [7-9, Wilson] | 3.8% of 11537 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5972 [0-0, Wilson] | 0.0% of 5565 [0-0, Wilson] | 0.0% of 11537 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 15.1% of 5972 [14-16, Wilson] | 14.9% of 5565 [14-16, Wilson] | 15.0% of 11537 [14-16, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.both: -13.4 points (-14.1 to -12.8); P2.g1: +1.9 points (+1.5 to +2.2); P2.g2: -15.6 points (-16.2 to -14.9); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -4.8 points (-5.1 to -4.5); P3.grimer_muk: -19.5 points (-20.1 to -18.9); P4.ko: +2.3 points (+1.8 to +2.9); P4.win: +2.3 points (+1.8 to +2.9); P4.never: -5.3 points (-5.7 to -4.9); P4.nomoment: +2.9 points (+2.4 to +3.3); P5.ko: +2.5 points (+1.9 to +3.0); P5.win: +2.5 points (+1.9 to +3.0).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.2% [80-82, Wilson] | 56.4% [55-57, Wilson] | 68.8% [68-69, Wilson] |
| P2 both Glimmora had their turn | 25.6% [25-26, Wilson] | 9.5% [9-10, Wilson] | 17.5% [17-18, Wilson] |
| P2 the first Glimmora placed had its turn | 77.2% [76-78, Wilson] | 41.6% [41-43, Wilson] | 59.4% [59-60, Wilson] |
| P2 the second Glimmora placed had its turn | 29.6% [29-31, Wilson] | 24.3% [23-25, Wilson] | 27.0% [26-28, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10, Wilson] | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 8.7% [8-9, Wilson] | 12.1% [12-13, Wilson] | 10.4% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.5% [31-32, Wilson] | 37.6% [37-39, Wilson] | 34.6% [34-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 6.1% [6-7, Wilson] | 1.8% [2-2, Wilson] | 4.0% [4-4, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.1% [6-7, Wilson] | 1.8% [2-2, Wilson] | 4.0% [4-4, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.4% [3-4, Wilson] | 1.9% [2-2, Wilson] | 2.7% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.5% [90-91, Wilson] | 96.2% [96-97, Wilson] | 93.4% [93-94, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 6.1% [6-7, Wilson] | 1.8% [2-2, Wilson] | 4.0% [4-4, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.1% [6-7, Wilson] | 1.8% [2-2, Wilson] | 4.0% [4-4, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 64.2% of 948 [61-67, Wilson] | 48.8% of 375 [44-54, Wilson] | 59.9% of 1323 [57-62, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 64.2% of 948 [61-67, Wilson] | 48.8% of 375 [44-54, Wilson] | 59.9% of 1323 [57-62, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 948 [0-0, Wilson] | 0.0% of 375 [0-1, Wilson] | 0.0% of 1323 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 948 [0-0, Wilson] | 0.0% of 375 [0-1, Wilson] | 0.0% of 1323 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 35.8% of 948 [33-39, Wilson] | 51.2% of 375 [46-56, Wilson] | 40.1% of 1323 [38-43, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.3 points (+0.8 to +1.8); P2.g1: +4.4 points (+3.9 to +4.9); P2.g2: -4.0 points (-4.5 to -3.4); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -11.4 points (-12.0 to -10.8); P3.grimer_muk: -21.4 points (-22.1 to -20.7); P4.ko: +1.7 points (+1.5 to +1.9); P4.win: +1.7 points (+1.5 to +1.9); P4.nomoment: -1.3 points (-1.6 to -1.1); P5.ko: +1.7 points (+1.5 to +1.9); P5.win: +1.7 points (+1.5 to +1.9).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.5% [95-96, Wilson] | 90.2% [90-91, Wilson] | 92.8% [92-93, Wilson] |
| P2 both Glimmora had their turn | 64.7% [64-66, Wilson] | 54.2% [53-55, Wilson] | 59.5% [59-60, Wilson] |
| P2 the first Glimmora placed had its turn | 91.5% [91-92, Wilson] | 84.1% [83-85, Wilson] | 87.8% [87-88, Wilson] |
| P2 the second Glimmora placed had its turn | 68.7% [68-70, Wilson] | 60.3% [59-61, Wilson] | 64.5% [64-65, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.9% [8-10, Wilson] | 8.5% [8-9, Wilson] | 8.7% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.9% [2-2, Wilson] | 4.3% [4-5, Wilson] | 3.1% [3-3, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 14.1% [13-15, Wilson] | 19.1% [18-20, Wilson] | 16.6% [16-17, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 18.0% [17-19, Wilson] | 16.3% [16-17, Wilson] | 17.2% [17-18, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 18.0% [17-19, Wilson] | 16.3% [16-17, Wilson] | 17.2% [17-18, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.1% [0-0, Wilson] | 0.1% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.5% [2-3, Wilson] | 2.4% [2-3, Wilson] | 2.4% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 79.5% [79-80, Wilson] | 81.2% [80-82, Wilson] | 80.4% [80-81, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 18.0% [17-19, Wilson] | 16.4% [16-17, Wilson] | 17.2% [17-18, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 18.0% [17-19, Wilson] | 16.4% [16-17, Wilson] | 17.2% [17-18, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 88.0% of 2049 [87-89, Wilson] | 86.8% of 1880 [85-88, Wilson] | 87.4% of 3929 [86-88, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 88.0% of 2049 [87-89, Wilson] | 86.8% of 1880 [85-88, Wilson] | 87.4% of 3929 [86-88, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 2049 [0-0, Wilson] | 0.6% of 1880 [0-1, Wilson] | 0.3% of 3929 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 2049 [0-0, Wilson] | 0.0% of 1880 [0-0, Wilson] | 0.0% of 3929 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 12.0% of 2049 [11-13, Wilson] | 12.7% of 1880 [11-14, Wilson] | 12.3% of 3929 [11-13, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.both: -4.8 points (-5.4 to -4.2); P2.g1: +1.9 points (+1.5 to +2.2); P2.g2: -6.6 points (-7.2 to -6.0); P3.pawn_lead: -4.1 points (-4.4 to -3.8); P3.pawn_promo: -31.8 points (-32.5 to -31.2); P3.grimer_muk: -30.4 points (-31.1 to -29.8); P4.ko: +10.6 points (+10.2 to +11.1); P4.win: +10.6 points (+10.2 to +11.1); P4.never: -9.3 points (-9.7 to -8.9); P4.nomoment: -1.3 points (-1.6 to -1.1); P5.ko: +10.6 points (+10.1 to +11.0); P5.win: +10.6 points (+10.1 to +11.0).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.5% (27.1-27.9) | 27.2% (26.8-27.6) | 27.3% (27.0-27.6) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 51.9% (51.5-52.4) | 51.9% (51.5-52.4) | 51.9% (51.6-52.2) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 61.8% (61.4-62.2) | 61.8% (61.4-62.2) | 61.8% (61.5-62.1) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 66.2% (65.8-66.6) | 66.2% (65.8-66.6) | 66.2% (65.9-66.5) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 68.4% (68.0-68.8) | 68.3% (67.9-68.7) | 68.3% (68.0-68.6) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 69.3% (68.9-69.7) | 69.1% (68.7-69.5) | 69.2% (68.9-69.5) |
| K2 Kingambit in play, own turn 2 | 9.9% (9.6-10.1) | 10.0% (9.8-10.3) | 9.9% (9.8-10.1) |
| K2 Kingambit in play, own turn 3 | 19.2% (18.8-19.5) | 19.1% (18.7-19.4) | 19.1% (18.9-19.4) |
| K2 Kingambit in play, own turn 4 | 29.5% (29.1-29.9) | 29.5% (29.1-29.9) | 29.5% (29.2-29.8) |
| K2 Kingambit in play, own turn 5 | 41.1% (40.7-41.5) | 40.7% (40.2-41.1) | 40.9% (40.6-41.2) |
| K2 Kingambit in play, own turn 6 | 51.7% (51.2-52.1) | 51.2% (50.7-51.6) | 51.4% (51.1-51.7) |
| K6 Muk and Regigigas both in play, own turn 3 | 26.1% (25.7-26.4) | 26.3% (25.9-26.7) | 26.2% (25.9-26.5) |
| K6 Muk and Regigigas both in play, own turn 4 | 33.6% (33.2-34.0) | 33.6% (33.2-34.0) | 33.6% (33.3-33.9) |
| K6 Muk and Regigigas both in play, own turn 5 | 39.1% (38.6-39.5) | 39.2% (38.8-39.6) | 39.1% (38.8-39.4) |
| G3 Pawniard in play, own turn 1 | 51.9% (51.5-52.4) | 51.9% (51.5-52.4) | 51.9% (51.6-52.2) |
| G3 Pawniard in play, own turn 2 | 51.9% (51.5-52.4) | 51.8% (51.4-52.2) | 51.9% (51.6-52.2) |
| G3 Pawniard in play, own turn 3 | 47.0% (46.6-47.5) | 47.1% (46.7-47.6) | 47.1% (46.8-47.4) |
| G3 Pawniard in play, own turn 4 | 38.9% (38.4-39.3) | 38.8% (38.3-39.2) | 38.8% (38.5-39.1) |
| G3 Pawniard in play, own turn 5 | 28.2% (27.8-28.6) | 28.5% (28.1-28.9) | 28.3% (28.1-28.6) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 9.9% (9.6-10.1) | 10.0% (9.8-10.3) | 9.9% (9.8-10.1) |
| G3 Kingambit in play, own turn 3 | 19.2% (18.8-19.5) | 19.1% (18.7-19.4) | 19.1% (18.9-19.4) |
| G3 Kingambit in play, own turn 4 | 29.5% (29.1-29.9) | 29.5% (29.1-29.9) | 29.5% (29.2-29.8) |
| G3 Kingambit in play, own turn 5 | 41.1% (40.7-41.5) | 40.7% (40.2-41.1) | 40.9% (40.6-41.2) |
| G3 Alolan Grimer in play, own turn 1 | 49.7% (49.2-50.1) | 49.9% (49.5-50.4) | 49.8% (49.5-50.1) |
| G3 Alolan Grimer in play, own turn 2 | 39.0% (38.6-39.4) | 39.1% (38.6-39.5) | 39.0% (38.7-39.3) |
| G3 Alolan Grimer in play, own turn 3 | 32.0% (31.6-32.4) | 32.0% (31.6-32.4) | 32.0% (31.7-32.3) |
| G3 Alolan Grimer in play, own turn 4 | 25.4% (25.1-25.8) | 25.8% (25.4-26.1) | 25.6% (25.3-25.9) |
| G3 Alolan Grimer in play, own turn 5 | 20.1% (19.8-20.5) | 20.3% (19.9-20.6) | 20.2% (20.0-20.5) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 18.9% (18.5-19.2) | 19.0% (18.7-19.4) | 18.9% (18.7-19.2) |
| G3 Alolan Muk in play, own turn 3 | 29.4% (29.0-29.8) | 29.5% (29.1-29.9) | 29.4% (29.2-29.7) |
| G3 Alolan Muk in play, own turn 4 | 37.4% (37.0-37.8) | 37.2% (36.8-37.7) | 37.3% (37.0-37.6) |
| G3 Alolan Muk in play, own turn 5 | 43.4% (42.9-43.8) | 43.3% (42.9-43.7) | 43.3% (43.0-43.6) |
| G3 Glimmet in play, own turn 1 | 78.2% (77.8-78.5) | 78.3% (77.9-78.6) | 78.2% (78.0-78.5) |
| G3 Glimmet in play, own turn 2 | 45.3% (44.9-45.7) | 45.1% (44.6-45.5) | 45.2% (44.9-45.5) |
| G3 Glimmet in play, own turn 3 | 32.9% (32.5-33.3) | 32.5% (32.1-33.0) | 32.7% (32.4-33.0) |
| G3 Glimmet in play, own turn 4 | 22.3% (21.9-22.6) | 22.1% (21.8-22.5) | 22.2% (22.0-22.5) |
| G3 Glimmet in play, own turn 5 | 13.5% (13.2-13.8) | 13.2% (13.0-13.5) | 13.4% (13.2-13.6) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 60.0% (59.6-60.4) | 60.1% (59.6-60.5) | 60.0% (59.7-60.3) |
| G3 Glimmora in play, own turn 3 | 75.7% (75.3-76.1) | 75.9% (75.5-76.3) | 75.8% (75.5-76.1) |
| G3 Glimmora in play, own turn 4 | 84.3% (84.0-84.6) | 84.5% (84.2-84.8) | 84.4% (84.2-84.6) |
| G3 Glimmora in play, own turn 5 | 89.0% (88.7-89.3) | 89.3% (89.0-89.5) | 89.1% (88.9-89.3) |
| G3 Regigigas in play, own turn 1 | 78.4% (78.0-78.7) | 78.5% (78.1-78.8) | 78.4% (78.2-78.7) |
| G3 Regigigas in play, own turn 2 | 87.7% (87.4-88.0) | 87.9% (87.7-88.2) | 87.8% (87.6-88.0) |
| G3 Regigigas in play, own turn 3 | 91.5% (91.2-91.7) | 91.7% (91.4-91.9) | 91.6% (91.4-91.7) |
| G3 Regigigas in play, own turn 4 | 93.1% (92.8-93.3) | 93.3% (93.1-93.5) | 93.2% (93.0-93.3) |
| G3 Regigigas in play, own turn 5 | 93.6% (93.4-93.8) | 93.8% (93.6-94.1) | 93.7% (93.6-93.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 73.4% (73.0-73.8) | 73.5% (73.2-73.9) | 73.5% (73.2-73.8) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 88.0% (87.7-88.3) | 88.0% (87.7-88.2) | 88.0% (87.8-88.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 94.6% (94.4-94.8) | 94.5% (94.3-94.7) | 94.5% (94.4-94.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 97.6% (97.5-97.7) | 97.5% (97.4-97.7) | 97.6% (97.5-97.7) |
| G4.s2 a Stage 2 in play, own turn 2 | 9.9% (9.6-10.1) | 10.0% (9.8-10.3) | 9.9% (9.8-10.1) |
| G4.s2 a Stage 2 in play, own turn 3 | 19.2% (18.8-19.5) | 19.1% (18.7-19.4) | 19.1% (18.9-19.4) |
| G4.s2 a Stage 2 in play, own turn 4 | 29.5% (29.1-29.9) | 29.5% (29.1-29.9) | 29.5% (29.2-29.8) |
| G4.s2 a Stage 2 in play, own turn 5 | 41.1% (40.7-41.5) | 40.7% (40.2-41.1) | 40.9% (40.6-41.2) |
| G5.any3 an empty own turn among turns 1-3 | 23.3% (22.9-23.7) | 22.8% (22.4-23.2) | 23.1% (22.8-23.3) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.0% (9.8-10.3) | 5.0% (4.9-5.1) |
| G6 Kingambit with [DD] attached, own turn 3 | 16.7% (16.4-17.0) | 19.1% (18.7-19.4) | 17.9% (17.6-18.1) |
| G6 Kingambit with [DD] attached, own turn 4 | 29.5% (29.1-29.9) | 29.5% (29.1-29.9) | 29.5% (29.2-29.8) |
| G6 Kingambit with [DD] attached, own turn 5 | 41.1% (40.7-41.5) | 40.7% (40.2-41.1) | 40.9% (40.6-41.2) |
| G5 mean empty own turns in turns 1-5 | 0.759 | 0.754 | 0.756 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.7% / 10.1% [1-2] | 0.8% / 5.0% [1-1] |
| K3.by3 | 2.5% / 11.2% [2-3] | 2.1% / 10.4% [1-3] | 2.3% / 10.8% [2-3] |
| K3.by4 | 2.9% / 11.6% [2-4] | 3.6% / 11.9% [2-5] | 3.2% / 11.8% [2-4] |
| K3.by5 | 4.4% / 13.0% [3-6] | 3.9% / 19.9% [3-5] | 4.2% / 16.5% [3-6] |
| K3.by6 | 4.6% / 21.6% [3-7] | 8.8% / 32.9% [4-15] | 6.7% / 27.2% [4-10] |
| K3.by7 | 11.7% / 36.7% [4-22] | 8.9% / 56.1% [4-16] | 10.3% / 46.4% [4-19] |
| K3.by8 | 11.7% / 60.2% [4-22] | 8.9% / 62.1% [4-16] | 10.3% / 61.1% [4-19] |
| K3.never | 39.8% / 88.3% [16-64] | 37.9% / 91.1% [15-61] | 38.9% / 89.7% [16-63] |
| K3.k0 | 3.1% / 51.6% [2-4] | 2.3% / 55.5% [1-3] | 2.7% / 53.5% [2-4] |
| K3.k1 | 0.0% / 48.5% [0-0] | 0.0% / 53.2% [0-0] | 0.0% / 50.8% [0-0] |
| K3.k2 | 6.4% / 54.9% [0-16] | 5.1% / 58.3% [1-12] | 5.8% / 56.6% [1-14] |
| K3.k3p | 2.2% / 50.7% [0-7] | 1.5% / 54.6% [0-4] | 1.9% / 52.7% [0-5] |
| K4 | 8.6% / 58.9% [1-19] | 6.6% / 61.1% [1-14] | 7.6% / 60.0% [1-17] |
| K5 | 4.9% / 61.4% [4-6] | 5.8% / 59.7% [4-7] | 5.4% / 60.5% [4-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by4: -1.3 points (-1.8 to -1.0); K3.by5: -1.9 points (-2.4 to -1.4); K3.by6: -2.1 points (-2.7 to -1.6); K3.by7: -3.0 points (-5.1 to -1.6); K3.by8: -4.4 points (-9.3 to -1.7); K3.k0: -1.2 points (-2.0 to -0.6); K3.k2: -1.1 points (-1.7 to -0.5); K4: -3.1 points (-7.9 to -0.5); K5: -2.8 points (-3.6 to -2.0).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.3% [2-3] | 1.1% [0-2] |
| K3.by3 | 2.4% / 13.7% [1-3] | 2.8% [2-4] | 2.6% / 8.2% [2-3] |
| K3.by4 | 2.7% / 14.0% [1-4] | 3.9% [3-5] | 3.3% / 8.9% [2-4] |
| K3.by5 | 4.4% / 15.7% [2-7] | 4.2% / 34.4% [4-5] | 4.3% / 25.0% [3-6] |
| K3.by6 | 4.6% / 15.9% [3-7] | 4.5% / 34.7% [4-5] | 4.6% / 25.3% [4-6] |
| K3.by7 | 14.4% / 36.8% [4-28] | 5.0% / 66.9% [4-6] | 9.7% / 51.9% [4-18] |
| K3.by8 | 14.4% / 57.7% [4-28] | 5.0% / 84.1% [4-6] | 9.7% / 70.9% [4-18] |
| K3.never | 42.3% / 85.6% [15-71] | 15.9% / 95.0% [0-42] | 29.1% / 90.3% [12-52] |
| K3.k0 | 2.9% / 46.2% [1-4] | 3.3% / 82.4% [2-5] | 3.1% / 64.3% [2-4] |
| K3.k1 | 0.0% / 43.3% [0-0] | 0.0% / 79.1% [0-0] | 0.0% / 61.2% [0-0] |
| K3.k2 | 8.2% / 51.5% [0-21] | 1.2% / 80.3% [0-2] | 4.7% / 65.9% [1-12] |
| K3.k3p | 3.3% / 46.6% [0-10] | 0.5% / 79.6% [0-1] | 1.9% / 63.1% [0-6] |
| K4 | 11.5% / 56.1% [0-26] | 1.6% / 83.5% [0-3] | 6.6% / 69.8% [1-15] |
| K5 | 5.0% / 53.5% [3-7] | 5.4% / 84.2% [4-6] | 5.2% / 68.8% [4-6] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.1 points (-1.4 to -0.7); K3.by4: -1.4 points (-1.8 to -1.0); K3.by5: -2.0 points (-2.5 to -1.6); K3.by6: -2.3 points (-3.0 to -1.7); K3.by7: -5.9 points (-13.1 to -1.8); K3.by8: -5.9 points (-13.1 to -1.8); K3.k0: -1.4 points (-1.9 to -0.9); K4: -4.5 points (-11.9 to -0.4); K5: -2.8 points (-3.5 to -2.0).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.8% [1-2] | 0.9% [1-1] |
| K3.by3 | 2.6% [2-3] | 2.2% [2-2] | 2.4% [2-3] |
| K3.by4 | 3.1% [3-4] | 3.2% [3-4] | 3.2% [3-4] |
| K3.by5 | 4.1% [3-5] | 4.7% [4-6] | 4.4% [4-5] |
| K3.by6 | 5.3% [4-6] | 5.8% / 9.9% [5-7] | 5.5% / 7.6% [5-7] |
| K3.by7 | 6.5% / 11.0% [5-8] | 6.5% / 16.8% [5-8] | 6.5% / 13.9% [5-8] |
| K3.by8 | 7.2% / 18.5% [5-9] | 7.0% / 19.1% [5-9] | 7.1% / 18.8% [5-9] |
| K3.never | 81.5% / 92.8% [73-88] | 80.9% / 93.0% [73-87] | 81.2% / 92.9% [73-88] |
| K3.k0 | 3.5% / 14.8% [3-4] | 2.4% / 14.6% [2-3] | 3.0% / 14.7% [3-3] |
| K3.k1 | 0.0% / 11.3% [0-0] | 0.0% / 12.1% [0-0] | 0.0% / 11.7% [0-0] |
| K3.k2 | 1.6% / 12.9% [1-3] | 2.3% / 14.4% [1-3] | 1.9% / 13.6% [1-3] |
| K3.k3p | 2.1% / 13.4% [1-4] | 2.3% / 14.4% [1-4] | 2.2% / 13.9% [1-4] |
| K4 | 3.7% / 15.5% [2-6] | 4.5% / 17.1% [3-7] | 4.1% / 16.3% [2-6] |
| K5 | 5.4% / 19.4% [5-6] | 6.7% / 19.3% [6-7] | 6.0% / 19.3% [5-7] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.0 points (-1.2 to -0.9); K3.by4: -1.4 points (-1.6 to -1.2); K3.by5: -2.1 points (-2.4 to -1.8); K3.by6: -3.2 points (-3.7 to -2.6); K3.by7: -4.3 points (-5.6 to -3.2); K3.by8: -5.2 points (-7.3 to -3.7); K3.never: +4.1 points (+2.5 to +6.0); K3.k0: -1.2 points (-1.5 to -1.0); K3.k2: -1.5 points (-1.8 to -1.1); K3.k3p: -2.6 points (-4.6 to -1.1); K4: -4.0 points (-5.9 to -2.5); K5: -3.6 points (-4.0 to -3.2).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by4 | 1.0% [1-1, Wilson] | 4.4% [4-5, Wilson] | 2.7% [2-3, Wilson] |
| K3.by5 | 6.2% [6-7, Wilson] | 5.5% [5-6, Wilson] | 5.8% [6-6, Wilson] |
| K3.by6 | 10.0% [9-11, Wilson] | 5.5% [5-6, Wilson] | 7.7% [7-8, Wilson] |
| K3.by7 | 10.0% [9-11, Wilson] | 5.5% [5-6, Wilson] | 7.7% [7-8, Wilson] |
| K3.by8 | 10.0% [9-11, Wilson] | 5.5% [5-6, Wilson] | 7.7% [7-8, Wilson] |
| K3.never | 90.0% [89-91, Wilson] | 94.5% [94-95, Wilson] | 92.3% [92-93, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.0% [1-1, Wilson] | 1.9% [2-2, Wilson] | 1.4% [1-2, Wilson] |
| K3.k3p | 9.0% [8-10, Wilson] | 3.6% [3-4, Wilson] | 6.3% [6-7, Wilson] |
| K4 | 10.0% [9-11, Wilson] | 5.5% [5-6, Wilson] | 7.7% [7-8, Wilson] |
| K5 | 9.9% [9-10, Wilson] | 15.6% [15-16, Wilson] | 12.7% [12-13, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.3 points (-1.6 to -1.0); K3.by5: -3.6 points (-4.0 to -3.2); K3.by6: -3.4 points (-3.9 to -3.0); K3.by7: -3.4 points (-3.9 to -3.0); K3.by8: -3.4 points (-3.9 to -3.0); K3.never: +3.4 points (+3.0 to +3.9); K3.k3p: -2.5 points (-2.9 to -2.1); K4: -3.4 points (-3.9 to -3.0); K5: -9.0 points (-9.5 to -8.5).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| K3.by3 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 3.1% [3-3, Wilson] | 3.8% [3-4, Wilson] | 3.4% [3-4, Wilson] |
| K3.by5 | 3.7% [3-4, Wilson] | 9.0% [8-10, Wilson] | 6.3% [6-7, Wilson] |
| K3.by6 | 9.9% [9-11, Wilson] | 13.1% [12-14, Wilson] | 11.5% [11-12, Wilson] |
| K3.by7 | 17.8% [17-19, Wilson] | 13.1% [12-14, Wilson] | 15.5% [15-16, Wilson] |
| K3.by8 | 17.8% [17-19, Wilson] | 13.1% [12-14, Wilson] | 15.5% [15-16, Wilson] |
| K3.never | 82.2% [81-83, Wilson] | 86.9% [86-88, Wilson] | 84.5% [84-85, Wilson] |
| K3.k0 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.6% [0-1, Wilson] | 1.5% [1-2, Wilson] | 1.1% [1-1, Wilson] |
| K3.k3p | 14.1% [13-15, Wilson] | 9.4% [9-10, Wilson] | 11.8% [11-12, Wilson] |
| K4 | 14.8% [14-15, Wilson] | 10.9% [10-12, Wilson] | 12.8% [12-13, Wilson] |
| K5 | 7.1% [7-8, Wilson] | 9.7% [9-10, Wilson] | 8.4% [8-9, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.3 to -0.9); K3.by4: -1.7 points (-1.9 to -1.4); K3.by5: -4.7 points (-5.1 to -4.3); K3.by6: -10.6 points (-11.1 to -10.1); K3.by7: -9.2 points (-9.7 to -8.7); K3.by8: -9.2 points (-9.7 to -8.7); K3.never: +9.2 points (+8.7 to +9.7); K3.k0: -1.1 points (-1.3 to -0.9); K3.k2: -1.1 points (-1.3 to -0.9); K3.k3p: -7.0 points (-7.5 to -6.5); K4: -8.1 points (-8.6 to -7.6); K5: -7.8 points (-8.3 to -7.4).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| K3.by3 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 3.1% [3-3, Wilson] | 4.3% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| K3.by6 | 3.9% [4-4, Wilson] | 4.4% [4-5, Wilson] | 4.2% [4-4, Wilson] |
| K3.by7 | 4.0% [4-4, Wilson] | 35.8% [35-37, Wilson] | 19.9% [19-20, Wilson] |
| K3.by8 | 44.8% [44-46, Wilson] | 35.8% [35-37, Wilson] | 40.3% [40-41, Wilson] |
| K3.never | 55.2% [54-56, Wilson] | 64.2% [63-65, Wilson] | 59.7% [59-60, Wilson] |
| K3.k0 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.9% [1-1, Wilson] | 2.2% [2-3, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 40.9% [40-42, Wilson] | 31.4% [30-32, Wilson] | 36.1% [35-37, Wilson] |
| K4 | 41.8% [41-43, Wilson] | 33.6% [33-35, Wilson] | 37.7% [37-38, Wilson] |
| K5 | 6.0% [6-6, Wilson] | 6.7% [6-7, Wilson] | 6.3% [6-7, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.3 to -0.9); K3.by4: -1.1 points (-1.3 to -0.9); K3.by5: -2.5 points (-2.7 to -2.2); K3.by6: -4.0 points (-4.3 to -3.7); K3.by7: -4.5 points (-5.0 to -4.1); K3.by8: -5.8 points (-6.3 to -5.2); K3.never: +5.8 points (+5.2 to +6.3); K3.k0: -1.1 points (-1.3 to -0.9); K3.k2: -2.9 points (-3.2 to -2.7); K3.k3p: -1.8 points (-2.3 to -1.2); K4: -4.7 points (-5.3 to -4.1); K5: -3.6 points (-3.9 to -3.3).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by4 | 1.0% [1-1, Wilson] | 3.9% [3-4, Wilson] | 2.4% [2-3, Wilson] |
| K3.by5 | 4.0% [4-4, Wilson] | 5.0% [5-5, Wilson] | 4.5% [4-5, Wilson] |
| K3.by6 | 8.2% [8-9, Wilson] | 5.0% [5-5, Wilson] | 6.6% [6-7, Wilson] |
| K3.by7 | 8.2% [8-9, Wilson] | 5.0% [5-5, Wilson] | 6.6% [6-7, Wilson] |
| K3.by8 | 8.2% [8-9, Wilson] | 5.0% [5-5, Wilson] | 6.6% [6-7, Wilson] |
| K3.never | 91.8% [91-92, Wilson] | 95.0% [95-95, Wilson] | 93.4% [93-94, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.0% [1-1, Wilson] | 1.9% [2-2, Wilson] | 1.4% [1-2, Wilson] |
| K3.k3p | 7.2% [7-8, Wilson] | 3.2% [3-4, Wilson] | 5.2% [5-6, Wilson] |
| K4 | 8.2% [8-9, Wilson] | 5.0% [5-5, Wilson] | 6.6% [6-7, Wilson] |
| K5 | 9.9% [9-10, Wilson] | 15.6% [15-16, Wilson] | 12.7% [12-13, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.5 points (-1.7 to -1.2); K3.by5: -4.4 points (-4.8 to -4.0); K3.by6: -4.2 points (-4.6 to -3.7); K3.by7: -4.2 points (-4.6 to -3.7); K3.by8: -4.2 points (-4.6 to -3.7); K3.never: +4.2 points (+3.7 to +4.6); K3.k3p: -3.2 points (-3.6 to -2.8); K4: -4.2 points (-4.6 to -3.7); K5: -9.0 points (-9.5 to -8.5).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| K3.by3 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by4 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.by5 | 3.1% [3-3, Wilson] | 4.3% [4-5, Wilson] | 3.7% [3-4, Wilson] |
| K3.by6 | 3.9% [4-4, Wilson] | 4.4% [4-5, Wilson] | 4.2% [4-4, Wilson] |
| K3.by7 | 4.0% [4-4, Wilson] | 5.9% [5-6, Wilson] | 4.9% [5-5, Wilson] |
| K3.by8 | 4.9% [5-5, Wilson] | 6.0% [6-6, Wilson] | 5.4% [5-6, Wilson] |
| K3.by9 | 4.9% [5-5, Wilson] | 21.9% [21-23, Wilson] | 13.4% [13-14, Wilson] |
| K3.by10 | 22.7% [22-24, Wilson] | 21.9% [21-23, Wilson] | 22.3% [22-23, Wilson] |
| K3.never | 77.3% [76-78, Wilson] | 78.1% [77-79, Wilson] | 77.7% [77-78, Wilson] |
| K3.k0 | 3.1% [3-3, Wilson] | 2.2% [2-3, Wilson] | 2.6% [2-3, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 0.9% [1-1, Wilson] | 2.2% [2-3, Wilson] | 1.6% [1-2, Wilson] |
| K3.k3p | 18.8% [18-20, Wilson] | 17.4% [17-18, Wilson] | 18.1% [18-19, Wilson] |
| K4 | 19.7% [19-20, Wilson] | 19.6% [19-20, Wilson] | 19.7% [19-20, Wilson] |
| K5 | 6.0% [6-6, Wilson] | 6.8% [6-7, Wilson] | 6.4% [6-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.1 points (-1.3 to -0.9); K3.by4: -1.1 points (-1.3 to -0.9); K3.by5: -2.5 points (-2.7 to -2.2); K3.by6: -4.0 points (-4.3 to -3.7); K3.by7: -15.1 points (-15.7 to -14.6); K3.by8: -31.6 points (-32.3 to -31.0); K3.by9: -27.3 points (-28.0 to -26.7); K3.by10: -21.5 points (-22.1 to -20.8); K3.never: +21.5 points (+20.8 to +22.1); K3.k0: -1.1 points (-1.3 to -0.9); K3.k2: -2.9 points (-3.2 to -2.7); K3.k3p: -17.5 points (-18.1 to -16.8); K4: -20.4 points (-21.1 to -19.8); K5: -3.8 points (-4.1 to -3.5).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +19.9 (+19.6 to +20.3) FLAG | +20.1 (+19.8 to +20.5) FLAG | +20.0 (+19.8 to +20.3) FLAG |
| K1 Pawniard in play at setup | -1.7 (-1.9 to -1.6) FLAG | -1.6 (-1.8 to -1.5) FLAG | -1.7 (-1.8 to -1.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -4.0 (-4.3 to -3.7) FLAG | -3.7 (-4.0 to -3.4) FLAG | -3.8 (-4.0 to -3.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -6.1 (-6.4 to -5.8) FLAG | -6.0 (-6.3 to -5.7) FLAG | -6.1 (-6.3 to -5.8) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -8.3 (-8.6 to -8.0) FLAG | -8.3 (-8.7 to -8.0) FLAG | -8.3 (-8.6 to -8.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -10.2 (-10.5 to -9.9) FLAG | -10.4 (-10.7 to -10.0) FLAG | -10.3 (-10.5 to -10.0) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -11.5 (-11.9 to -11.2) FLAG | -11.6 (-12.0 to -11.3) FLAG | -11.6 (-11.8 to -11.3) FLAG |
| K2 Kingambit in play, own turn 3 | -1.9 (-2.1 to -1.7) FLAG | -2.0 (-2.3 to -1.8) FLAG | -2.0 (-2.1 to -1.8) FLAG |
| K2 Kingambit in play, own turn 4 | -3.5 (-3.8 to -3.2) FLAG | -3.6 (-3.9 to -3.3) FLAG | -3.5 (-3.8 to -3.3) FLAG |
| K2 Kingambit in play, own turn 5 | -5.3 (-5.7 to -5.0) FLAG | -5.8 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| K2 Kingambit in play, own turn 6 | -7.8 (-8.1 to -7.4) FLAG | -7.9 (-8.3 to -7.6) FLAG | -7.9 (-8.1 to -7.6) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +3.9 (+3.5 to +4.2) FLAG | +4.1 (+3.7 to +4.4) FLAG | +4.0 (+3.7 to +4.2) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +3.2 (+2.8 to +3.6) FLAG | +3.1 (+2.7 to +3.5) FLAG | +3.1 (+2.9 to +3.4) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.1 (+1.7 to +2.5) FLAG | +2.2 (+1.8 to +2.6) FLAG | +2.2 (+1.9 to +2.5) FLAG |
| G3 Pawniard in play, own turn 1 | -4.0 (-4.3 to -3.7) FLAG | -3.7 (-4.0 to -3.4) FLAG | -3.8 (-4.0 to -3.6) FLAG |
| G3 Pawniard in play, own turn 2 | -5.3 (-5.6 to -5.0) FLAG | -5.3 (-5.6 to -5.0) FLAG | -5.3 (-5.5 to -5.1) FLAG |
| G3 Pawniard in play, own turn 3 | -6.4 (-6.7 to -6.1) FLAG | -6.3 (-6.6 to -6.0) FLAG | -6.4 (-6.6 to -6.1) FLAG |
| G3 Pawniard in play, own turn 4 | -6.7 (-7.1 to -6.4) FLAG | -6.8 (-7.1 to -6.4) FLAG | -6.7 (-7.0 to -6.5) FLAG |
| G3 Pawniard in play, own turn 5 | -6.2 (-6.5 to -5.8) FLAG | -5.9 (-6.2 to -5.6) FLAG | -6.0 (-6.2 to -5.8) FLAG |
| G3 Kingambit in play, own turn 3 | -1.9 (-2.1 to -1.7) FLAG | -2.0 (-2.3 to -1.8) FLAG | -2.0 (-2.1 to -1.8) FLAG |
| G3 Kingambit in play, own turn 4 | -3.5 (-3.8 to -3.2) FLAG | -3.6 (-3.9 to -3.3) FLAG | -3.5 (-3.8 to -3.3) FLAG |
| G3 Kingambit in play, own turn 5 | -5.3 (-5.7 to -5.0) FLAG | -5.8 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -4.9 (-5.2 to -4.6) FLAG | -4.8 (-5.1 to -4.5) FLAG | -4.9 (-5.1 to -4.7) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -7.2 (-7.6 to -6.9) FLAG | -7.5 (-7.8 to -7.2) FLAG | -7.4 (-7.6 to -7.1) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -8.0 (-8.3 to -7.6) FLAG | -8.1 (-8.4 to -7.8) FLAG | -8.0 (-8.2 to -7.8) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -7.6 (-7.9 to -7.3) FLAG | -7.5 (-7.8 to -7.2) FLAG | -7.5 (-7.8 to -7.3) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -6.5 (-6.8 to -6.3) FLAG | -6.8 (-7.0 to -6.5) FLAG | -6.6 (-6.9 to -6.4) FLAG |
| G3 Alolan Muk in play, own turn 3 | -1.7 (-2.0 to -1.4) FLAG | -1.8 (-2.1 to -1.5) FLAG | -1.8 (-2.0 to -1.5) FLAG |
| G3 Alolan Muk in play, own turn 4 | -3.8 (-4.1 to -3.4) FLAG | -4.1 (-4.5 to -3.7) FLAG | -3.9 (-4.2 to -3.7) FLAG |
| G3 Alolan Muk in play, own turn 5 | -5.9 (-6.3 to -5.5) FLAG | -5.9 (-6.3 to -5.5) FLAG | -5.9 (-6.2 to -5.6) FLAG |
| G3 Glimmet in play, own turn 1 | -4.0 (-4.2 to -3.7) FLAG | -4.2 (-4.4 to -3.9) FLAG | -4.1 (-4.2 to -3.9) FLAG |
| G3 Glimmet in play, own turn 2 | -7.5 (-7.8 to -7.2) FLAG | -7.4 (-7.7 to -7.0) FLAG | -7.4 (-7.7 to -7.2) FLAG |
| G3 Glimmet in play, own turn 3 | -9.3 (-9.6 to -8.9) FLAG | -9.4 (-9.7 to -9.0) FLAG | -9.3 (-9.6 to -9.1) FLAG |
| G3 Glimmet in play, own turn 4 | -8.7 (-9.0 to -8.3) FLAG | -8.8 (-9.1 to -8.4) FLAG | -8.7 (-9.0 to -8.5) FLAG |
| G3 Glimmet in play, own turn 5 | -6.7 (-7.0 to -6.4) FLAG | -6.6 (-6.9 to -6.3) FLAG | -6.6 (-6.8 to -6.4) FLAG |
| G3 Glimmora in play, own turn 2 | -3.1 (-3.4 to -2.9) FLAG | -3.3 (-3.5 to -3.0) FLAG | -3.2 (-3.4 to -3.0) FLAG |
| G3 Glimmora in play, own turn 3 | -4.0 (-4.3 to -3.7) FLAG | -4.0 (-4.3 to -3.8) FLAG | -4.0 (-4.2 to -3.8) FLAG |
| G3 Glimmora in play, own turn 4 | -5.1 (-5.4 to -4.9) FLAG | -4.9 (-5.2 to -4.7) FLAG | -5.0 (-5.2 to -4.9) FLAG |
| G3 Glimmora in play, own turn 5 | -6.1 (-6.3 to -5.8) FLAG | -5.9 (-6.1 to -5.6) FLAG | -6.0 (-6.1 to -5.8) FLAG |
| G3 Regigigas in play, own turn 1 | +23.0 (+22.6 to +23.4) FLAG | +23.3 (+22.9 to +23.7) FLAG | +23.1 (+22.8 to +23.4) FLAG |
| G3 Regigigas in play, own turn 2 | +20.0 (+19.6 to +20.4) FLAG | +20.8 (+20.5 to +21.2) FLAG | +20.4 (+20.2 to +20.7) FLAG |
| G3 Regigigas in play, own turn 3 | +17.0 (+16.7 to +17.4) FLAG | +17.5 (+17.1 to +17.9) FLAG | +17.3 (+17.0 to +17.5) FLAG |
| G3 Regigigas in play, own turn 4 | +14.8 (+14.5 to +15.2) FLAG | +15.1 (+14.8 to +15.5) FLAG | +15.0 (+14.8 to +15.2) FLAG |
| G3 Regigigas in play, own turn 5 | +13.3 (+13.0 to +13.7) FLAG | +13.7 (+13.3 to +14.0) FLAG | +13.5 (+13.3 to +13.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -2.1 (-2.4 to -1.8) FLAG | -2.1 (-2.4 to -1.8) FLAG | -2.1 (-2.3 to -1.9) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -1.7 (-1.9 to -1.4) FLAG | -1.8 (-2.0 to -1.6) FLAG | -1.7 (-1.9 to -1.6) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -1.4 (-1.5 to -1.2) FLAG | -1.3 (-1.5 to -1.2) FLAG | -1.4 (-1.5 to -1.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -1.0 (-1.1 to -0.9) FLAG | -1.1 (-1.2 to -0.9) FLAG | -1.0 (-1.1 to -1.0) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -1.9 (-2.1 to -1.7) FLAG | -2.0 (-2.3 to -1.8) FLAG | -2.0 (-2.1 to -1.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -3.5 (-3.8 to -3.2) FLAG | -3.6 (-3.9 to -3.3) FLAG | -3.5 (-3.8 to -3.3) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -5.3 (-5.7 to -5.0) FLAG | -5.8 (-6.1 to -5.4) FLAG | -5.6 (-5.8 to -5.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -0.9 (-1.1 to -0.6) | -2.0 (-2.3 to -1.8) FLAG | -1.5 (-1.6 to -1.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -3.5 (-3.8 to -3.2) FLAG | -3.6 (-3.9 to -3.3) FLAG | -3.5 (-3.7 to -3.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -5.3 (-5.7 to -5.0) FLAG | -5.8 (-6.1 to -5.4) FLAG | -5.5 (-5.8 to -5.3) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.002 (-0.006 to +0.002) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Lucky Ice Pop B2 145 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.0 points
- C-his (per-game bootstrap): P2 both Glimmora had their turn -9.1 points (-12.7 to -5.9); P2 the second Glimmora placed had its turn -10.7 points (-14.1 to -7.5); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.5 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.4 points (-9.2 to -1.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -13.1 points (-17.2 to -9.4); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.8 points (-3.2 to -0.7)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -1.3 points (-2.2 to -0.8); P2 both Glimmora had their turn -8.1 points (-12.2 to -4.7); P2 the second Glimmora placed had its turn -9.4 points (-13.5 to -6.2); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -5.7 points (-13.1 to -0.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.1 points (-19.0 to -9.3)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -1.6 points (-2.6 to -0.6); P2 both Glimmora had their turn -9.0 points (-10.9 to -7.2); P2 the second Glimmora placed had its turn -10.9 points (-12.6 to -9.2); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.0 points (-15.9 to -10.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -20.7 points (-23.3 to -18.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.1 points (-1.6 to -0.5)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn +1.2 points (+0.8 to +1.7); P2 the first Glimmora placed had its turn +4.4 points (+3.9 to +4.9); P2 the second Glimmora placed had its turn -4.1 points (-4.7 to -3.6); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -10.5 points (-11.1 to -10.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -21.4 points (-22.1 to -20.7); P4 ready at the winning moment: Knocks out their strongest +1.1 points (+0.7 to +1.4); P4 ready at the winning moment: Wins outright (a lower bound) +1.1 points (+0.7 to +1.4); P4 the moment came and Kingambit was never ready in the deal +1.8 points (+1.3 to +2.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -3.4 points (-3.9 to -3.0); P5 plan reached in time: Knocks out their strongest +1.6 points (+1.3 to +2.0); P5 plan reached in time: Wins outright (a lower bound) +1.6 points (+1.3 to +2.0)
- C-fixed medium (paired test): P2 both Glimmora had their turn -5.5 points (-6.1 to -5.0); P2 the second Glimmora placed had its turn -6.7 points (-7.3 to -6.1); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -16.7 points (-17.3 to -16.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -28.5 points (-29.2 to -27.9); P4 ready at the winning moment: Knocks out their strongest +1.0 points (+0.6 to +1.5); P4 the moment came and Kingambit was never ready in the deal -1.2 points (-1.7 to -0.7); P5 plan reached in time: Knocks out their strongest +1.7 points (+1.2 to +2.1)
- C-fixed slow (paired test): P2 both Glimmora had their turn -13.4 points (-14.1 to -12.8); P2 the first Glimmora placed had its turn +1.9 points (+1.5 to +2.2); P2 the second Glimmora placed had its turn -15.6 points (-16.2 to -14.9); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.8 points (-5.1 to -4.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -19.5 points (-20.1 to -18.9); P4 ready at the winning moment: Knocks out their strongest +2.3 points (+1.8 to +2.9); P4 ready at the winning moment: Wins outright (a lower bound) +2.3 points (+1.8 to +2.9); P4 the moment came and Kingambit was never ready in the deal -5.3 points (-5.7 to -4.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +2.9 points (+2.4 to +3.3); P5 plan reached in time: Knocks out their strongest +2.5 points (+1.9 to +3.0); P5 plan reached in time: Wins outright (a lower bound) +2.5 points (+1.9 to +3.0)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +1.3 points (+0.8 to +1.8); P2 the first Glimmora placed had its turn +4.4 points (+3.9 to +4.9); P2 the second Glimmora placed had its turn -4.0 points (-4.5 to -3.4); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -11.4 points (-12.0 to -10.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -21.4 points (-22.1 to -20.7); P4 ready at the winning moment: Knocks out their strongest +1.7 points (+1.5 to +1.9); P4 ready at the winning moment: Wins outright (a lower bound) +1.7 points (+1.5 to +1.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.3 points (-1.6 to -1.1); P5 plan reached in time: Knocks out their strongest +1.7 points (+1.5 to +1.9); P5 plan reached in time: Wins outright (a lower bound) +1.7 points (+1.5 to +1.9)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 both Glimmora had their turn -4.8 points (-5.4 to -4.2); P2 the first Glimmora placed had its turn +1.9 points (+1.5 to +2.2); P2 the second Glimmora placed had its turn -6.6 points (-7.2 to -6.0); P3 plan broken in front, cause: Pawniard forced to lead -4.1 points (-4.4 to -3.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -31.8 points (-32.5 to -31.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -30.4 points (-31.1 to -29.8); P4 ready at the winning moment: Knocks out their strongest +10.6 points (+10.2 to +11.1); P4 ready at the winning moment: Wins outright (a lower bound) +10.6 points (+10.2 to +11.1); P4 the moment came and Kingambit was never ready in the deal -9.3 points (-9.7 to -8.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.3 points (-1.6 to -1.1); P5 plan reached in time: Knocks out their strongest +10.6 points (+10.1 to +11.0); P5 plan reached in time: Wins outright (a lower bound) +10.6 points (+10.1 to +11.0)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K6 Muk and Regigigas both in play, own turn 3 +4.0 points; K6 Muk and Regigigas both in play, own turn 4 +3.1 points; K6 Muk and Regigigas both in play, own turn 5 +2.2 points; G3 Regigigas in play, own turn 1 +23.1 points; G3 Regigigas in play, own turn 2 +20.4 points; G3 Regigigas in play, own turn 3 +17.3 points; G3 Regigigas in play, own turn 4 +15.0 points; G3 Regigigas in play, own turn 5 +13.5 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.7 points; K1 Pawniard line in play (end of own turn t), own turn 1 -3.8 points; K1 Pawniard line in play (end of own turn t), own turn 2 -6.1 points; K1 Pawniard line in play (end of own turn t), own turn 3 -8.3 points; K1 Pawniard line in play (end of own turn t), own turn 4 -10.3 points; K1 Pawniard line in play (end of own turn t), own turn 5 -11.6 points; K2 Kingambit in play, own turn 3 -2.0 points; K2 Kingambit in play, own turn 4 -3.5 points; K2 Kingambit in play, own turn 5 -5.6 points; K2 Kingambit in play, own turn 6 -7.9 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by4 -1.3; K3.by5 -1.9; K3.by6 -2.1; K3.by7 -3.0; K3.by8 -4.4; K3.k0 -1.2; K3.k2 -1.1; K4 -3.1; K5 -2.8; C-his, seat-matched: K3.by3 -1.1; K3.by4 -1.4; K3.by5 -2.0; K3.by6 -2.3; K3.by7 -5.9; K3.by8 -5.9; K3.k0 -1.4; K4 -4.5; K5 -2.8; C-bot: K3.by3 -1.0; K3.by4 -1.4; K3.by5 -2.1; K3.by6 -3.2; K3.by7 -4.3; K3.by8 -5.2; K3.never +4.1; K3.k0 -1.2; K3.k2 -1.5; K3.k3p -2.6; K4 -4.0; K5 -3.6; C-fixed fast: K3.by4 -1.3; K3.by5 -3.6; K3.by6 -3.4; K3.by7 -3.4; K3.by8 -3.4; K3.never +3.4; K3.k3p -2.5; K4 -3.4; K5 -9.0; C-fixed medium: K3.by3 -1.1; K3.by4 -1.7; K3.by5 -4.7; K3.by6 -10.6; K3.by7 -9.2; K3.by8 -9.2; K3.never +9.2; K3.k0 -1.1; K3.k2 -1.1; K3.k3p -7.0; K4 -8.1; K5 -7.8; C-fixed slow: K3.by3 -1.1; K3.by4 -1.1; K3.by5 -2.5; K3.by6 -4.0; K3.by7 -4.5; K3.by8 -5.8; K3.never +5.8; K3.k0 -1.1; K3.k2 -2.9; K3.k3p -1.8; K4 -4.7; K5 -3.6; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.5; K3.by5 -4.4; K3.by6 -4.2; K3.by7 -4.2; K3.by8 -4.2; K3.never +4.2; K3.k3p -3.2; K4 -4.2; K5 -9.0; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.1; K3.by4 -1.1; K3.by5 -2.5; K3.by6 -4.0; K3.by7 -15.1; K3.by8 -31.6; K3.by9 -27.3; K3.by10 -21.5; K3.never +21.5; K3.k0 -1.1; K3.k2 -2.9; K3.k3p -17.5; K4 -20.4; K5 -3.8.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## -1 Mesagoza B2a 093 +1 Regigigas B3 134 (card-list id 66aad19597ac)

Changes: ['-1 Mesagoza B2a 093', '+1 Regigigas B3 134']

Copycat decisions with a Copycat in hand: 255,169; the valuation and the fallback rule disagree at 123,774 of 255,169 Copycat decisions (48.5%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.12913. Basics in the opening hand: 1: 0.517, 2: 0.352, 3 or more: 0.131.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.08609, Glimmet 0.19565, Pawniard 0.08609, Regigigas 0.19565.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.10956, Glimmet 0.31394, Pawniard 0.08609, Regigigas 0.49041 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2715, Kingambit 0.2408, Alolan Grimer 0.2715, Alolan Muk 0.2408, Glimmet 0.4904, Glimmora 0.4346, Regigigas 0.4904, Poké Ball 0.4346, Rare Candy 0.2408.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03238; in 8 cards: 0.05085.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 32/37/42/47/51%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 32/37/42/47/51%; Alolan Muk: 29/34/39/44/49%; Glimmet: 56/62/68/73/78%; Glimmora: 51/58/64/70/76%; Regigigas: 56/62/68/73/78%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 48.9% (48.5-49.4) | 48.9% (48.4-49.3) | 48.9% (48.6-49.2) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.3% / 93.7% [70-91] | 73.3% / 88.9% [58-85] | 77.8% / 91.3% [64-88] |
| P2 both Glimmora had their turn | 21.5% / 62.1% [15-28] | 18.8% / 63.5% [12-27] | 20.2% / 62.8% [14-26] |
| P2 the first Glimmora placed had its turn | 79.0% / 87.9% [68-88] | 67.8% / 79.6% [53-81] | 73.4% / 83.8% [60-84] |
| P2 the second Glimmora placed had its turn | 24.8% / 61.6% [18-32] | 24.4% / 63.1% [17-33] | 24.6% / 62.4% [17-32] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9] | 8.4% [8-9] | 8.4% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.2% / 49.9% [1-4] | 3.7% / 55.0% [2-6] | 3.0% / 52.4% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.6% / 59.5% [14-21] | 21.6% / 64.6% [17-27] | 19.6% / 62.1% [16-24] |
| P4 ready at the winning moment: Knocks out their strongest | 10.1% / 35.5% [2-19] | 6.9% / 34.6% [2-13] | 8.5% / 35.1% [2-16] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.7% / 27.1% [0-5] | 1.0% / 28.7% [0-3] | 1.3% / 27.9% [0-4] |
| P4 not ready, ready 1 turn late | 3.6% / 47.4% [0-8] | 2.7% / 50.8% [0-6] | 3.2% / 49.1% [0-7] |
| P4 not ready, ready 2 or more turns late | 1.2% / 45.0% [0-4] | 1.0% / 49.1% [0-3] | 1.1% / 47.0% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 10.8% / 54.7% [0-25] | 10.8% / 58.9% [0-27] | 10.8% / 56.8% [0-26] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.5% / 56.0% [9-55] | 30.4% / 58.1% [11-54] | 30.5% / 57.0% [10-54] |
| P5 plan reached in time: Knocks out their strongest | 14.8% / 58.7% [5-26] | 10.7% / 58.7% [4-19] | 12.8% / 58.7% [5-22] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.3% / 46.2% [0-7] | 1.4% / 49.5% [0-4] | 1.9% / 47.8% [0-6] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 39.2% of 2565 [24-55] | 32.2% of 2152 [18-53] | 36.0% of 4717 [22-53] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.5% of 2565 [0-27] | 4.5% of 2152 [0-25] | 5.6% of 4717 [0-26] |
| P4 not ready, ready 1 turn late | 14.0% of 2565 [0-48] | 12.7% of 2152 [0-47] | 13.4% of 4717 [0-47] |
| P4 not ready, ready 2 or more turns late | 4.6% of 2565 [0-19] | 4.7% of 2152 [0-21] | 4.6% of 4717 [0-20] |
| P4 the moment came and Kingambit was never ready in the deal | 42.2% of 2565 [0-63] | 50.4% of 2152 [0-72] | 45.9% of 4717 [0-68] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.4 points (-6.5 to -4.4); P2.both: -15.6 points (-19.4 to -11.9); P2.g1: -4.3 points (-5.9 to -2.7); P2.g2: -16.7 points (-20.4 to -12.8); P3.pawn_lead: -4.4 points (-4.8 to -4.1); P3.pawn_promo: -3.1 points (-7.2 to -0.6); P3.grimer_muk: -10.5 points (-13.1 to -8.0); P4.ko: -3.6 points (-7.3 to -0.2); P5.ko: -4.8 points (-9.0 to -0.9).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.0% / 93.5% [65-92] | 81.1% / 92.6% [71-89] | 81.0% / 93.1% [72-88] |
| P2 both Glimmora had their turn | 21.5% / 57.0% [14-28] | 17.9% / 80.1% [12-31] | 19.7% / 68.6% [14-27] |
| P2 the first Glimmora placed had its turn | 77.6% / 88.2% [62-89] | 77.9% / 83.2% [67-88] | 77.8% / 85.7% [69-85] |
| P2 the second Glimmora placed had its turn | 24.9% / 56.8% [16-33] | 21.1% / 75.0% [13-36] | 23.0% / 65.9% [16-31] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9] | 8.4% [8-9] | 8.4% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 1.8% / 44.6% [0-3] | 4.9% / 78.0% [0-9] | 3.3% / 61.3% [1-5] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 17.6% / 55.2% [13-23] | 23.2% / 85.0% [12-29] | 20.4% / 70.1% [15-25] |
| P4 ready at the winning moment: Knocks out their strongest | 12.2% / 34.5% [2-24] | 3.3% / 52.4% [0-10] | 7.7% / 43.4% [2-16] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.0% / 25.3% [0-9] | 0.0% / 49.0% [0-0] | 1.5% / 37.2% [0-6] |
| P4 not ready, ready 1 turn late | 4.7% / 42.2% [0-11] | 0.0% / 75.9% [0-0] | 2.4% / 59.0% [0-7] |
| P4 not ready, ready 2 or more turns late | 1.7% / 39.2% [0-6] | 0.0% / 75.9% [0-0] | 0.9% / 57.5% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 15.2% / 52.6% [0-35] | 0.0% / 75.9% [0-0] | 7.6% / 64.2% [0-19] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.8% / 51.1% [6-58] | 20.8% / 69.9% [0-53] | 24.8% / 60.5% [8-46] |
| P5 plan reached in time: Knocks out their strongest | 18.6% / 56.1% [6-32] | 3.3% / 79.2% [0-10] | 11.0% / 67.6% [4-22] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.7% / 41.1% [0-11] | 0.0% / 75.9% [0-0] | 1.8% / 58.5% [0-7] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 36.1% of 3378 [19-49] | 100.0% of 330 [100-100] | 41.7% of 3708 [22-64] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 8.9% of 3378 [0-37] | 0.0% of 330 [0-0] | 8.1% of 3708 [0-29] |
| P4 not ready, ready 1 turn late | 14.0% of 3378 [0-57] | 0.0% of 330 [0-0] | 12.8% of 3708 [0-40] |
| P4 not ready, ready 2 or more turns late | 5.1% of 3378 [0-24] | 0.0% of 330 [0-0] | 4.6% of 3708 [0-17] |
| P4 the moment came and Kingambit was never ready in the deal | 44.9% of 3378 [0-67] | 0.0% of 330 [0-0] | 40.9% of 3708 [0-63] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -6.5 points (-7.3 to -5.5); P2.both: -15.5 points (-19.4 to -12.4); P2.g1: -5.8 points (-6.6 to -4.8); P2.g2: -16.2 points (-20.0 to -13.2); P3.pawn_lead: -4.4 points (-4.9 to -4.0); P3.pawn_promo: -4.3 points (-10.3 to -0.5); P3.grimer_muk: -10.9 points (-13.7 to -7.7); P4.ko: -2.8 points (-6.3 to -0.4); P5.ko: -3.4 points (-7.4 to -0.8).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 83.9% / 85.4% [80-87] | 75.1% / 77.6% [71-79] | 79.5% / 81.5% [76-83] |
| P2 both Glimmora had their turn | 24.9% / 33.2% [22-28] | 19.0% / 28.2% [16-22] | 21.9% / 30.7% [19-25] |
| P2 the first Glimmora placed had its turn | 78.9% / 79.3% [74-83] | 68.2% / 68.9% [63-74] | 73.6% / 74.1% [69-78] |
| P2 the second Glimmora placed had its turn | 29.9% / 36.7% [27-32] | 25.8% / 33.1% [23-28] | 27.8% / 34.9% [25-30] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9] | 8.4% [8-9] | 8.4% [8-9] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 4.8% / 15.9% [4-6] | 6.7% / 18.3% [5-8] | 5.7% / 17.1% [5-7] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 20.8% / 30.4% [19-22] | 26.7% / 36.2% [25-29] | 23.8% / 33.3% [22-25] |
| P4 ready at the winning moment: Knocks out their strongest | 5.4% / 11.6% [3-8] | 4.6% / 11.6% [3-7] | 5.0% / 11.6% [3-8] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.2% / 6.3% [0-1] | 0.4% / 7.4% [0-1] | 0.3% / 6.9% [0-1] |
| P4 not ready, ready 1 turn late | 3.2% / 12.2% [2-5] | 2.5% / 13.0% [1-4] | 2.9% / 12.6% [1-4] |
| P4 not ready, ready 2 or more turns late | 1.6% / 10.6% [1-3] | 1.8% / 12.3% [1-3] | 1.7% / 11.4% [1-3] |
| P4 the moment came and Kingambit was never ready in the deal | 11.2% / 20.2% [6-17] | 11.6% / 22.0% [6-18] | 11.4% / 21.1% [6-18] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.6% / 75.7% [58-80] | 69.0% / 76.1% [58-79] | 69.3% / 75.9% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 10.2% / 19.3% [6-15] | 8.9% / 19.4% [5-14] | 9.6% / 19.3% [5-14] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.3% / 9.3% [0-1] | 0.4% / 10.8% [0-1] | 0.4% / 10.1% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 25.4% of 2140 [18-35] | 22.4% of 2051 [17-29] | 23.9% of 4191 [17-32] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.1% of 2140 [0-4] | 1.9% of 2051 [0-6] | 1.5% of 4191 [0-4] |
| P4 not ready, ready 1 turn late | 15.0% of 2140 [10-22] | 12.3% of 2051 [8-17] | 13.7% of 4191 [10-19] |
| P4 not ready, ready 2 or more turns late | 7.5% of 2140 [3-12] | 8.9% of 2051 [3-15] | 8.2% of 4191 [4-13] |
| P4 the moment came and Kingambit was never ready in the deal | 52.1% of 2140 [39-64] | 56.4% of 2051 [44-67] | 54.2% of 4191 [42-65] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -7.6 points (-8.9 to -6.3); P2.both: -15.0 points (-17.1 to -13.0); P2.g1: -5.2 points (-6.1 to -4.3); P2.g2: -17.4 points (-19.0 to -15.7); P3.pawn_lead: -4.4 points (-4.7 to -4.1); P3.pawn_promo: -10.1 points (-12.6 to -7.9); P3.grimer_muk: -15.7 points (-17.8 to -13.8); P4.ko: -2.2 points (-3.6 to -1.0); P4.late1: -1.2 points (-2.1 to -0.4); P4.never: +2.7 points (+1.4 to +4.1); P5.ko: -3.3 points (-5.0 to -2.0).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 74.3% [73-75, Wilson] | 50.1% [49-51, Wilson] | 62.2% [62-63, Wilson] |
| P2 both Glimmora had their turn | 16.7% [16-17, Wilson] | 6.1% [6-7, Wilson] | 11.4% [11-12, Wilson] |
| P2 the first Glimmora placed had its turn | 70.6% [70-71, Wilson] | 37.3% [36-38, Wilson] | 53.9% [53-55, Wilson] |
| P2 the second Glimmora placed had its turn | 20.4% [20-21, Wilson] | 18.9% [18-20, Wilson] | 19.7% [19-20, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 11.5% [11-12, Wilson] | 12.8% [12-14, Wilson] | 12.2% [12-13, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 35.9% [35-37, Wilson] | 38.3% [37-39, Wilson] | 37.1% [36-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 9.0% [8-10, Wilson] | 3.3% [3-4, Wilson] | 6.1% [6-6, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 9.0% [8-10, Wilson] | 3.3% [3-4, Wilson] | 6.1% [6-6, Wilson] |
| P4 not ready, ready 1 turn late | 0.9% [1-1, Wilson] | 0.3% [0-0, Wilson] | 0.6% [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 27.2% [26-28, Wilson] | 19.3% [19-20, Wilson] | 23.3% [23-24, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 62.9% [62-64, Wilson] | 77.2% [76-78, Wilson] | 70.0% [69-71, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 9.8% [9-10, Wilson] | 3.6% [3-4, Wilson] | 6.7% [6-7, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 9.8% [9-10, Wilson] | 3.6% [3-4, Wilson] | 6.7% [6-7, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 24.2% of 3710 [23-26, Wilson] | 14.4% of 2285 [13-16, Wilson] | 20.4% of 5995 [19-21, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 24.2% of 3710 [23-26, Wilson] | 14.4% of 2285 [13-16, Wilson] | 20.4% of 5995 [19-21, Wilson] |
| P4 not ready, ready 1 turn late | 2.4% of 3710 [2-3, Wilson] | 1.2% of 2285 [1-2, Wilson] | 1.9% of 5995 [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 3710 [0-0, Wilson] | 0.0% of 2285 [0-0, Wilson] | 0.0% of 5995 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 73.5% of 3710 [72-75, Wilson] | 84.4% of 2285 [83-86, Wilson] | 77.6% of 5995 [77-79, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.2 points (-5.7 to -4.7); P2.both: -6.9 points (-7.4 to -6.4); P2.g1: -1.1 points (-1.6 to -0.5); P2.g2: -11.0 points (-11.6 to -10.4); P3.pawn_lead: -4.4 points (-4.7 to -4.1); P3.pawn_promo: -8.2 points (-8.7 to -7.6); P3.grimer_muk: -18.9 points (-19.5 to -18.2); P4.ko: -4.6 points (-5.0 to -4.2); P4.win: -4.6 points (-5.0 to -4.2); P4.never: +2.1 points (+1.6 to +2.6); P4.nomoment: +3.3 points (+2.8 to +3.8); P5.ko: -5.4 points (-5.8 to -5.0); P5.win: -5.4 points (-5.8 to -5.0).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.8% [82-84, Wilson] | 74.0% [73-75, Wilson] | 78.4% [78-79, Wilson] |
| P2 both Glimmora had their turn | 24.2% [23-25, Wilson] | 16.7% [16-17, Wilson] | 20.4% [20-21, Wilson] |
| P2 the first Glimmora placed had its turn | 80.2% [79-81, Wilson] | 70.8% [70-72, Wilson] | 75.5% [75-76, Wilson] |
| P2 the second Glimmora placed had its turn | 26.8% [26-28, Wilson] | 19.8% [19-21, Wilson] | 23.3% [23-24, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 9.2% [9-10, Wilson] | 11.9% [11-13, Wilson] | 10.6% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.6% [31-33, Wilson] | 36.8% [36-38, Wilson] | 34.2% [34-35, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 14.6% [14-15, Wilson] | 8.4% [8-9, Wilson] | 11.5% [11-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 1.8% [2-2, Wilson] | 1.0% [1-1, Wilson] | 1.4% [1-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 29.1% [28-30, Wilson] | 28.1% [27-29, Wilson] | 28.6% [28-29, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 54.6% [54-56, Wilson] | 62.5% [62-63, Wilson] | 58.5% [58-59, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 16.3% [16-17, Wilson] | 9.4% [9-10, Wilson] | 12.8% [12-13, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 32.1% of 4542 [31-33, Wilson] | 22.3% of 3754 [21-24, Wilson] | 27.7% of 8296 [27-29, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 4542 [0-0, Wilson] | 0.0% of 3754 [0-0, Wilson] | 0.0% of 8296 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 3.9% of 4542 [3-4, Wilson] | 2.7% of 3754 [2-3, Wilson] | 3.3% of 8296 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4542 [0-0, Wilson] | 0.0% of 3754 [0-0, Wilson] | 0.0% of 8296 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 64.1% of 4542 [63-65, Wilson] | 75.0% of 3754 [74-76, Wilson] | 69.0% of 8296 [68-70, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: -7.7 points (-8.1 to -7.2); P2.both: -13.5 points (-14.2 to -12.9); P2.g1: -6.7 points (-7.1 to -6.2); P2.g2: -14.5 points (-15.2 to -13.9); P3.pawn_lead: -4.4 points (-4.7 to -4.1); P3.pawn_promo: -13.4 points (-14.0 to -12.8); P3.grimer_muk: -22.5 points (-23.2 to -21.9); P4.ko: -10.3 points (-10.8 to -9.8); P4.late1: -1.0 points (-1.2 to -0.8); P4.never: +3.7 points (+3.2 to +4.3); P4.nomoment: +7.5 points (+7.1 to +8.0); P5.ko: -11.3 points (-11.8 to -10.8).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.3% [90-91, Wilson] | 83.2% [82-84, Wilson] | 86.7% [86-87, Wilson] |
| P2 both Glimmora had their turn | 41.1% [40-42, Wilson] | 32.1% [31-33, Wilson] | 36.6% [36-37, Wilson] |
| P2 the first Glimmora placed had its turn | 85.5% [85-86, Wilson] | 77.5% [77-78, Wilson] | 81.5% [81-82, Wilson] |
| P2 the second Glimmora placed had its turn | 46.0% [45-47, Wilson] | 37.9% [37-39, Wilson] | 41.9% [41-43, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 3.0% [3-3, Wilson] | 4.8% [4-5, Wilson] | 4.0% [4-4, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 18.1% [17-19, Wilson] | 24.5% [24-25, Wilson] | 21.3% [21-22, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 35.8% [35-37, Wilson] | 25.5% [25-26, Wilson] | 30.7% [30-31, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 35.8% [35-37, Wilson] | 25.5% [25-26, Wilson] | 30.7% [30-31, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 7.2% [7-8, Wilson] | 3.6% [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 18.1% [17-19, Wilson] | 15.5% [15-16, Wilson] | 16.8% [16-17, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 46.0% [45-47, Wilson] | 51.8% [51-53, Wilson] | 48.9% [48-50, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 35.8% [35-37, Wilson] | 32.7% [32-34, Wilson] | 34.3% [34-35, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 35.8% [35-37, Wilson] | 32.7% [32-34, Wilson] | 34.3% [34-35, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 66.4% of 5397 [65-68, Wilson] | 53.0% of 4821 [52-54, Wilson] | 60.1% of 10218 [59-61, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 66.4% of 5397 [65-68, Wilson] | 53.0% of 4821 [52-54, Wilson] | 60.1% of 10218 [59-61, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5397 [0-0, Wilson] | 14.9% of 4821 [14-16, Wilson] | 7.0% of 10218 [7-8, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5397 [0-0, Wilson] | 0.0% of 4821 [0-0, Wilson] | 0.0% of 10218 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 33.6% of 5397 [32-35, Wilson] | 32.1% of 4821 [31-33, Wilson] | 32.9% of 10218 [32-34, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: -6.0 points (-6.4 to -5.6); P2.both: -25.6 points (-26.3 to -24.9); P2.g1: -4.5 points (-4.9 to -4.0); P2.g2: -27.2 points (-27.9 to -26.5); P3.pawn_lead: -4.4 points (-4.7 to -4.1); P3.pawn_promo: -2.8 points (-3.1 to -2.4); P3.grimer_muk: -14.5 points (-15.1 to -13.9); P4.ko: -13.8 points (-14.4 to -13.2); P4.win: -13.8 points (-14.4 to -13.2); P4.late1: +1.5 points (+1.2 to +1.8); P4.never: +2.8 points (+2.3 to +3.4); P4.nomoment: +9.5 points (+9.0 to +9.9); P5.ko: -12.3 points (-12.9 to -11.7); P5.win: -12.3 points (-12.9 to -11.7).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 74.4% [74-75, Wilson] | 50.1% [49-51, Wilson] | 62.3% [62-63, Wilson] |
| P2 both Glimmora had their turn | 16.8% [16-18, Wilson] | 6.1% [6-7, Wilson] | 11.5% [11-12, Wilson] |
| P2 the first Glimmora placed had its turn | 70.6% [70-71, Wilson] | 37.3% [36-38, Wilson] | 53.9% [53-55, Wilson] |
| P2 the second Glimmora placed had its turn | 20.6% [20-21, Wilson] | 19.0% [18-20, Wilson] | 19.8% [19-20, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 12.4% [12-13, Wilson] | 13.0% [12-14, Wilson] | 12.7% [12-13, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 35.9% [35-37, Wilson] | 38.3% [37-39, Wilson] | 37.1% [36-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 1.6% [1-2, Wilson] | 0.5% [0-1, Wilson] | 1.1% [1-1, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.6% [1-2, Wilson] | 0.5% [0-1, Wilson] | 1.1% [1-1, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.9% [3-3, Wilson] | 1.4% [1-2, Wilson] | 2.1% [2-2, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 95.5% [95-96, Wilson] | 98.1% [98-98, Wilson] | 96.8% [97-97, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 1.6% [1-2, Wilson] | 0.5% [0-1, Wilson] | 1.1% [1-1, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 1.6% [1-2, Wilson] | 0.5% [0-1, Wilson] | 1.1% [1-1, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 36.1% of 454 [32-41, Wilson] | 26.3% of 186 [21-33, Wilson] | 33.3% of 640 [30-37, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 36.1% of 454 [32-41, Wilson] | 26.3% of 186 [21-33, Wilson] | 33.3% of 640 [30-37, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 454 [0-1, Wilson] | 0.0% of 186 [0-2, Wilson] | 0.0% of 640 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 454 [0-1, Wilson] | 0.0% of 186 [0-2, Wilson] | 0.0% of 640 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 63.9% of 454 [59-68, Wilson] | 73.7% of 186 [67-79, Wilson] | 66.7% of 640 [63-70, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.2 points (-5.8 to -4.7); P2.both: -7.0 points (-7.4 to -6.5); P2.g1: -1.1 points (-1.6 to -0.5); P2.g2: -11.2 points (-11.7 to -10.6); P3.pawn_lead: -4.4 points (-4.7 to -4.1); P3.pawn_promo: -9.1 points (-9.7 to -8.6); P3.grimer_muk: -18.9 points (-19.5 to -18.2); P4.ko: -1.2 points (-1.4 to -1.0); P4.win: -1.2 points (-1.4 to -1.0); P4.nomoment: +2.1 points (+1.8 to +2.4); P5.ko: -1.2 points (-1.4 to -1.0); P5.win: -1.2 points (-1.4 to -1.0).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.5% [90-91, Wilson] | 83.4% [83-84, Wilson] | 86.9% [86-87, Wilson] |
| P2 both Glimmora had their turn | 48.2% [47-49, Wilson] | 35.8% [35-37, Wilson] | 42.0% [41-43, Wilson] |
| P2 the first Glimmora placed had its turn | 85.5% [85-86, Wilson] | 77.5% [77-78, Wilson] | 81.5% [81-82, Wilson] |
| P2 the second Glimmora placed had its turn | 53.2% [52-54, Wilson] | 41.7% [41-43, Wilson] | 47.5% [47-48, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] | 8.4% [8-9, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 6.0% [6-7, Wilson] | 8.4% [8-9, Wilson] | 7.2% [7-8, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 19.1% [18-20, Wilson] | 26.3% [25-27, Wilson] | 22.7% [22-23, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 12.7% [12-13, Wilson] | 9.7% [9-10, Wilson] | 11.2% [11-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.7% [12-13, Wilson] | 9.7% [9-10, Wilson] | 11.2% [11-12, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.8% [1-1, Wilson] | 0.4% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.4% [2-3, Wilson] | 1.8% [2-2, Wilson] | 2.1% [2-2, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 84.9% [84-86, Wilson] | 87.8% [87-88, Wilson] | 86.3% [86-87, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 12.7% [12-13, Wilson] | 10.5% [10-11, Wilson] | 11.6% [11-12, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 12.7% [12-13, Wilson] | 10.5% [10-11, Wilson] | 11.6% [11-12, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 84.0% of 1508 [82-86, Wilson] | 78.9% of 1225 [76-81, Wilson] | 81.7% of 2733 [80-83, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 84.0% of 1508 [82-86, Wilson] | 78.9% of 1225 [76-81, Wilson] | 81.7% of 2733 [80-83, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1508 [0-0, Wilson] | 6.5% of 1225 [5-8, Wilson] | 2.9% of 2733 [2-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1508 [0-0, Wilson] | 0.0% of 1225 [0-0, Wilson] | 0.0% of 2733 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 16.0% of 1508 [14-18, Wilson] | 14.6% of 1225 [13-17, Wilson] | 15.4% of 2733 [14-17, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.8 points (-6.2 to -5.4); P2.both: -22.3 points (-23.0 to -21.6); P2.g1: -4.5 points (-4.9 to -4.0); P2.g2: -23.6 points (-24.4 to -22.9); P3.pawn_lead: -4.4 points (-4.7 to -4.1); P3.pawn_promo: -27.8 points (-28.4 to -27.1); P3.grimer_muk: -24.3 points (-25.0 to -23.6); P4.ko: +4.6 points (+4.2 to +5.0); P4.win: +4.6 points (+4.2 to +5.0); P4.never: -9.6 points (-10.0 to -9.2); P4.nomoment: +4.7 points (+4.3 to +5.0); P5.ko: +4.9 points (+4.5 to +5.3); P5.win: +4.9 points (+4.5 to +5.3).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 27.5% (27.1-27.9) | 27.1% (26.7-27.5) | 27.3% (27.0-27.6) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 50.5% (50.0-50.9) | 50.2% (49.7-50.6) | 50.3% (50.0-50.6) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 59.5% (59.0-59.9) | 59.3% (58.8-59.7) | 59.4% (59.0-59.7) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 63.8% (63.4-64.3) | 63.7% (63.3-64.1) | 63.8% (63.5-64.1) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 66.4% (66.0-66.8) | 66.2% (65.8-66.6) | 66.3% (66.0-66.6) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 67.8% (67.4-68.2) | 67.7% (67.3-68.1) | 67.8% (67.5-68.0) |
| K2 Kingambit in play, own turn 2 | 8.5% (8.2-8.7) | 8.6% (8.4-8.9) | 8.5% (8.4-8.7) |
| K2 Kingambit in play, own turn 3 | 15.1% (14.8-15.4) | 15.2% (14.9-15.6) | 15.2% (14.9-15.4) |
| K2 Kingambit in play, own turn 4 | 22.0% (21.7-22.4) | 22.2% (21.8-22.5) | 22.1% (21.8-22.3) |
| K2 Kingambit in play, own turn 5 | 30.0% (29.6-30.4) | 29.7% (29.3-30.1) | 29.9% (29.6-30.1) |
| K2 Kingambit in play, own turn 6 | 38.4% (38.0-38.8) | 38.2% (37.8-38.6) | 38.3% (38.0-38.6) |
| K6 Muk and Regigigas both in play, own turn 3 | 21.4% (21.1-21.8) | 21.3% (20.9-21.7) | 21.4% (21.1-21.6) |
| K6 Muk and Regigigas both in play, own turn 4 | 27.3% (26.9-27.7) | 27.1% (26.7-27.5) | 27.2% (26.9-27.5) |
| K6 Muk and Regigigas both in play, own turn 5 | 32.2% (31.8-32.7) | 32.1% (31.7-32.6) | 32.2% (31.9-32.5) |
| G3 Pawniard in play, own turn 1 | 50.5% (50.0-50.9) | 50.2% (49.7-50.6) | 50.3% (50.0-50.6) |
| G3 Pawniard in play, own turn 2 | 51.0% (50.6-51.4) | 50.7% (50.2-51.1) | 50.8% (50.5-51.1) |
| G3 Pawniard in play, own turn 3 | 48.7% (48.3-49.2) | 48.5% (48.0-48.9) | 48.6% (48.3-48.9) |
| G3 Pawniard in play, own turn 4 | 44.4% (43.9-44.8) | 44.1% (43.6-44.5) | 44.2% (43.9-44.5) |
| G3 Pawniard in play, own turn 5 | 37.8% (37.4-38.3) | 37.9% (37.5-38.4) | 37.9% (37.6-38.2) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 8.5% (8.2-8.7) | 8.6% (8.4-8.9) | 8.5% (8.4-8.7) |
| G3 Kingambit in play, own turn 3 | 15.1% (14.8-15.4) | 15.2% (14.9-15.6) | 15.2% (14.9-15.4) |
| G3 Kingambit in play, own turn 4 | 22.0% (21.7-22.4) | 22.2% (21.8-22.5) | 22.1% (21.8-22.3) |
| G3 Kingambit in play, own turn 5 | 30.0% (29.6-30.4) | 29.7% (29.3-30.1) | 29.9% (29.6-30.1) |
| G3 Alolan Grimer in play, own turn 1 | 48.4% (48.0-48.9) | 48.6% (48.1-49.0) | 48.5% (48.2-48.8) |
| G3 Alolan Grimer in play, own turn 2 | 39.6% (39.2-40.0) | 40.0% (39.5-40.4) | 39.8% (39.5-40.1) |
| G3 Alolan Grimer in play, own turn 3 | 35.5% (35.1-35.9) | 35.8% (35.4-36.2) | 35.6% (35.4-35.9) |
| G3 Alolan Grimer in play, own turn 4 | 31.5% (31.1-31.9) | 32.0% (31.6-32.4) | 31.7% (31.5-32.0) |
| G3 Alolan Grimer in play, own turn 5 | 27.5% (27.1-27.9) | 27.9% (27.5-28.3) | 27.7% (27.4-28.0) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 16.5% (16.2-16.8) | 16.3% (16.0-16.7) | 16.4% (16.2-16.6) |
| G3 Alolan Muk in play, own turn 3 | 24.5% (24.1-24.8) | 24.4% (24.0-24.8) | 24.4% (24.2-24.7) |
| G3 Alolan Muk in play, own turn 4 | 30.6% (30.2-31.0) | 30.5% (30.1-30.9) | 30.5% (30.2-30.8) |
| G3 Alolan Muk in play, own turn 5 | 35.9% (35.5-36.3) | 35.8% (35.4-36.2) | 35.8% (35.5-36.1) |
| G3 Glimmet in play, own turn 1 | 76.7% (76.3-77.1) | 76.6% (76.2-77.0) | 76.6% (76.4-76.9) |
| G3 Glimmet in play, own turn 2 | 47.0% (46.6-47.4) | 46.8% (46.4-47.3) | 46.9% (46.6-47.2) |
| G3 Glimmet in play, own turn 3 | 38.5% (38.0-38.9) | 38.6% (38.2-39.0) | 38.5% (38.2-38.8) |
| G3 Glimmet in play, own turn 4 | 31.6% (31.2-32.1) | 31.8% (31.4-32.2) | 31.7% (31.5-32.0) |
| G3 Glimmet in play, own turn 5 | 24.7% (24.3-25.1) | 24.9% (24.5-25.3) | 24.8% (24.5-25.1) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 55.1% (54.6-55.5) | 55.0% (54.6-55.4) | 55.0% (54.7-55.3) |
| G3 Glimmora in play, own turn 3 | 69.1% (68.7-69.5) | 69.1% (68.7-69.5) | 69.1% (68.8-69.4) |
| G3 Glimmora in play, own turn 4 | 77.9% (77.6-78.3) | 77.9% (77.5-78.2) | 77.9% (77.6-78.2) |
| G3 Glimmora in play, own turn 5 | 84.1% (83.8-84.4) | 84.1% (83.8-84.5) | 84.1% (83.9-84.3) |
| G3 Regigigas in play, own turn 1 | 77.1% (76.7-77.4) | 76.8% (76.4-77.2) | 76.9% (76.7-77.2) |
| G3 Regigigas in play, own turn 2 | 85.9% (85.6-86.2) | 85.7% (85.4-86.0) | 85.8% (85.6-86.0) |
| G3 Regigigas in play, own turn 3 | 89.9% (89.7-90.2) | 89.8% (89.5-90.1) | 89.9% (89.7-90.1) |
| G3 Regigigas in play, own turn 4 | 92.1% (91.9-92.3) | 92.1% (91.8-92.3) | 92.1% (91.9-92.2) |
| G3 Regigigas in play, own turn 5 | 93.2% (93.0-93.5) | 93.1% (92.9-93.4) | 93.2% (93.0-93.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 68.3% (67.9-68.7) | 68.3% (67.9-68.7) | 68.3% (68.0-68.6) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 82.5% (82.1-82.8) | 82.4% (82.1-82.7) | 82.4% (82.2-82.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 90.0% (89.8-90.3) | 90.1% (89.8-90.3) | 90.1% (89.9-90.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 94.6% (94.4-94.8) | 94.7% (94.5-94.9) | 94.6% (94.5-94.8) |
| G4.s2 a Stage 2 in play, own turn 2 | 8.5% (8.2-8.7) | 8.6% (8.4-8.9) | 8.5% (8.4-8.7) |
| G4.s2 a Stage 2 in play, own turn 3 | 15.1% (14.8-15.4) | 15.2% (14.9-15.6) | 15.2% (14.9-15.4) |
| G4.s2 a Stage 2 in play, own turn 4 | 22.0% (21.7-22.4) | 22.2% (21.8-22.5) | 22.1% (21.8-22.3) |
| G4.s2 a Stage 2 in play, own turn 5 | 30.0% (29.6-30.4) | 29.7% (29.3-30.1) | 29.9% (29.6-30.1) |
| G5.any3 an empty own turn among turns 1-3 | 49.6% (49.2-50.1) | 49.0% (48.6-49.5) | 49.3% (49.0-49.6) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 8.6% (8.4-8.9) | 4.3% (4.2-4.4) |
| G6 Kingambit with [DD] attached, own turn 3 | 13.5% (13.2-13.8) | 15.2% (14.9-15.6) | 14.4% (14.2-14.6) |
| G6 Kingambit with [DD] attached, own turn 4 | 22.0% (21.7-22.4) | 22.2% (21.8-22.5) | 22.1% (21.8-22.3) |
| G6 Kingambit with [DD] attached, own turn 5 | 30.0% (29.6-30.4) | 29.7% (29.3-30.1) | 29.9% (29.6-30.1) |
| G5 mean empty own turns in turns 1-5 | 1.619 | 1.608 | 1.614 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.5% / 9.8% [1-2] | 0.7% / 4.9% [0-1] |
| K3.by3 | 1.9% / 10.5% [1-3] | 1.7% / 10.1% [1-2] | 1.8% / 10.3% [1-2] |
| K3.by4 | 2.3% / 10.9% [1-3] | 3.2% / 11.6% [2-4] | 2.7% / 11.2% [2-3] |
| K3.by5 | 3.9% / 12.6% [3-6] | 3.6% / 19.4% [3-5] | 3.8% / 16.0% [3-5] |
| K3.by6 | 4.2% / 21.0% [3-6] | 6.4% / 30.2% [3-10] | 5.3% / 25.6% [3-7] |
| K3.by7 | 8.7% / 33.5% [4-15] | 6.7% / 53.2% [4-11] | 7.7% / 43.4% [4-13] |
| K3.by8 | 8.9% / 57.0% [4-15] | 6.7% / 58.4% [4-11] | 7.8% / 57.7% [4-13] |
| K3.never | 43.0% / 91.1% [17-68] | 41.6% / 93.3% [18-64] | 42.3% / 92.2% [18-66] |
| K3.k0 | 2.5% / 50.6% [2-4] | 1.8% / 53.5% [1-2] | 2.2% / 52.1% [1-3] |
| K3.k1 | 0.0% / 48.1% [0-0] | 0.0% / 51.7% [0-0] | 0.0% / 49.9% [0-0] |
| K3.k2 | 5.0% / 53.2% [1-11] | 4.0% / 55.7% [1-8] | 4.5% / 54.4% [1-10] |
| K3.k3p | 1.4% / 49.5% [0-4] | 0.9% / 52.6% [0-2] | 1.1% / 51.1% [0-3] |
| K4 | 6.4% / 55.9% [1-13] | 4.9% / 57.6% [1-9] | 5.7% / 56.7% [1-11] |
| K5 | 5.2% / 60.0% [4-6] | 6.6% / 58.1% [5-8] | 5.9% / 59.1% [4-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.4 points (-1.9 to -0.9); K3.by4: -1.8 points (-2.5 to -1.3); K3.by5: -2.3 points (-3.0 to -1.7); K3.by6: -3.5 points (-4.9 to -2.3); K3.by7: -5.6 points (-9.2 to -2.7); K3.by8: -6.9 points (-11.9 to -2.7); K3.never: +4.8 points (+0.5 to +9.9); K3.k0: -1.8 points (-2.7 to -1.0); K3.k2: -2.3 points (-5.3 to -0.5); K4: -5.1 points (-10.2 to -0.7); K5: -2.3 points (-3.0 to -1.6).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.0% [2-2] | 1.0% [0-1] |
| K3.by3 | 1.8% / 13.1% [1-3] | 2.4% [2-3] | 2.1% / 7.7% [1-3] |
| K3.by4 | 2.1% / 13.4% [1-3] | 3.4% [2-4] | 2.7% / 8.4% [2-3] |
| K3.by5 | 3.6% / 14.9% [2-5] | 4.0% / 33.0% [4-4] | 3.8% / 23.9% [3-5] |
| K3.by6 | 3.9% / 15.2% [3-5] | 4.3% / 33.3% [4-5] | 4.1% / 24.2% [3-5] |
| K3.by7 | 10.4% / 32.9% [4-20] | 5.5% / 66.6% [4-9] | 8.0% / 49.7% [4-14] |
| K3.by8 | 10.4% / 53.5% [4-20] | 5.5% / 80.4% [4-9] | 8.0% / 66.9% [4-14] |
| K3.never | 46.5% / 89.6% [17-76] | 19.6% / 94.5% [0-49] | 33.1% / 92.0% [14-56] |
| K3.k0 | 2.3% / 45.3% [1-3] | 2.7% / 77.5% [2-4] | 2.5% / 61.4% [2-3] |
| K3.k1 | 0.0% / 43.1% [0-0] | 0.0% / 74.8% [0-0] | 0.0% / 58.9% [0-0] |
| K3.k2 | 6.0% / 49.1% [1-15] | 1.6% / 76.4% [0-3] | 3.8% / 62.8% [1-9] |
| K3.k3p | 2.1% / 45.2% [0-7] | 1.2% / 76.1% [0-4] | 1.7% / 60.6% [0-4] |
| K4 | 8.2% / 52.2% [1-18] | 2.9% / 79.8% [0-7] | 5.5% / 66.0% [1-12] |
| K5 | 5.3% / 52.7% [3-7] | 6.2% / 80.8% [5-7] | 5.8% / 66.8% [5-7] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.6 points (-2.1 to -1.1); K3.by4: -2.0 points (-2.6 to -1.4); K3.by5: -2.6 points (-3.1 to -2.0); K3.by6: -2.8 points (-3.4 to -2.1); K3.by7: -7.6 points (-13.8 to -2.7); K3.by8: -7.6 points (-13.8 to -2.7); K3.k0: -2.0 points (-2.7 to -1.3); K3.k2: -1.9 points (-4.4 to -0.5); K4: -5.6 points (-11.8 to -0.6); K5: -2.2 points (-3.0 to -1.4).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 1.7% [1-2] | 0.8% [1-1] |
| K3.by3 | 2.1% [2-2] | 2.0% [2-2] | 2.0% [2-2] |
| K3.by4 | 2.4% [2-3] | 3.0% [3-3] | 2.7% [2-3] |
| K3.by5 | 3.4% [3-4] | 4.7% [4-6] | 4.0% [4-5] |
| K3.by6 | 4.9% [4-6] | 5.6% / 9.6% [5-7] | 5.2% / 7.3% [4-6] |
| K3.by7 | 5.8% / 10.3% [5-7] | 6.2% / 16.2% [5-8] | 6.0% / 13.2% [5-7] |
| K3.by8 | 6.4% / 17.3% [5-8] | 6.5% / 18.0% [5-8] | 6.4% / 17.6% [5-8] |
| K3.never | 82.7% / 93.6% [74-89] | 82.0% / 93.5% [74-88] | 82.3% / 93.6% [75-89] |
| K3.k0 | 2.6% / 13.5% [2-3] | 2.1% / 13.6% [2-2] | 2.3% / 13.5% [2-3] |
| K3.k1 | 0.0% / 10.9% [0-0] | 0.0% / 11.5% [0-0] | 0.0% / 11.2% [0-0] |
| K3.k2 | 2.2% / 13.1% [1-3] | 2.7% / 14.2% [2-4] | 2.5% / 13.7% [2-3] |
| K3.k3p | 1.6% / 12.5% [1-3] | 1.7% / 13.2% [1-3] | 1.7% / 12.9% [1-3] |
| K4 | 3.8% / 15.1% [3-5] | 4.4% / 16.3% [3-6] | 4.1% / 15.7% [3-5] |
| K5 | 6.2% / 19.6% [6-7] | 7.6% / 19.5% [7-8] | 6.9% / 19.6% [6-7] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: -1.4 points (-1.7 to -1.2); K3.by4: -1.9 points (-2.2 to -1.6); K3.by5: -2.5 points (-2.8 to -2.1); K3.by6: -3.5 points (-4.1 to -2.8); K3.by7: -4.8 points (-6.2 to -3.6); K3.by8: -5.9 points (-7.9 to -4.2); K3.never: +5.3 points (+3.6 to +7.2); K3.k0: -1.8 points (-2.2 to -1.5); K3.k3p: -3.1 points (-5.0 to -1.5); K4: -4.0 points (-6.0 to -2.4); K5: -2.7 points (-3.0 to -2.3).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.0% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by4 | 1.5% [1-2, Wilson] | 3.5% [3-4, Wilson] | 2.5% [2-3, Wilson] |
| K3.by5 | 5.6% [5-6, Wilson] | 3.9% [4-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.by6 | 6.7% [6-7, Wilson] | 3.9% [4-4, Wilson] | 5.3% [5-6, Wilson] |
| K3.by7 | 6.7% [6-7, Wilson] | 3.9% [4-4, Wilson] | 5.3% [5-6, Wilson] |
| K3.by8 | 6.7% [6-7, Wilson] | 3.9% [4-4, Wilson] | 5.3% [5-6, Wilson] |
| K3.never | 93.3% [93-94, Wilson] | 96.1% [96-96, Wilson] | 94.7% [94-95, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.5% [1-2, Wilson] | 2.0% [2-2, Wilson] | 1.7% [2-2, Wilson] |
| K3.k3p | 5.2% [5-6, Wilson] | 1.9% [2-2, Wilson] | 3.5% [3-4, Wilson] |
| K4 | 6.7% [6-7, Wilson] | 3.9% [4-4, Wilson] | 5.3% [5-6, Wilson] |
| K5 | 13.1% [12-14, Wilson] | 17.2% [16-18, Wilson] | 15.1% [15-16, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.4 points (-1.7 to -1.2); K3.by5: -4.7 points (-5.1 to -4.3); K3.by6: -5.9 points (-6.3 to -5.5); K3.by7: -5.9 points (-6.3 to -5.5); K3.by8: -5.9 points (-6.3 to -5.5); K3.never: +5.9 points (+5.5 to +6.3); K3.k3p: -5.3 points (-5.6 to -4.9); K4: -5.9 points (-6.3 to -5.5); K5: -6.6 points (-7.0 to -6.1).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by3 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.by4 | 2.5% [2-3, Wilson] | 4.0% [4-4, Wilson] | 3.2% [3-3, Wilson] |
| K3.by5 | 3.7% [3-4, Wilson] | 8.0% [7-9, Wilson] | 5.9% [6-6, Wilson] |
| K3.by6 | 9.6% [9-10, Wilson] | 8.9% [8-9, Wilson] | 9.2% [9-10, Wilson] |
| K3.by7 | 11.7% [11-12, Wilson] | 8.9% [8-9, Wilson] | 10.3% [10-11, Wilson] |
| K3.by8 | 11.7% [11-12, Wilson] | 8.9% [8-9, Wilson] | 10.3% [10-11, Wilson] |
| K3.never | 88.3% [88-89, Wilson] | 91.1% [91-92, Wilson] | 89.7% [89-90, Wilson] |
| K3.k0 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.3% [1-2, Wilson] | 2.0% [2-2, Wilson] | 1.7% [1-2, Wilson] |
| K3.k3p | 8.0% [7-9, Wilson] | 4.9% [5-5, Wilson] | 6.5% [6-7, Wilson] |
| K4 | 9.2% [9-10, Wilson] | 7.0% [6-7, Wilson] | 8.1% [8-8, Wilson] |
| K5 | 9.4% [9-10, Wilson] | 12.9% [12-14, Wilson] | 11.1% [11-12, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.5 points (-1.7 to -1.3); K3.by4: -1.9 points (-2.1 to -1.6); K3.by5: -5.2 points (-5.5 to -4.8); K3.by6: -12.9 points (-13.5 to -12.4); K3.by7: -14.4 points (-14.9 to -13.8); K3.by8: -14.4 points (-14.9 to -13.8); K3.never: +14.4 points (+13.8 to +14.9); K3.k0: -1.5 points (-1.7 to -1.3); K3.k3p: -12.3 points (-12.8 to -11.8); K4: -12.8 points (-13.4 to -12.3); K5: -5.1 points (-5.5 to -4.7).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by3 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.by4 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.by5 | 2.5% [2-3, Wilson] | 4.8% [4-5, Wilson] | 3.6% [3-4, Wilson] |
| K3.by6 | 4.7% [4-5, Wilson] | 5.0% [5-5, Wilson] | 4.8% [5-5, Wilson] |
| K3.by7 | 4.7% [4-5, Wilson] | 22.3% [22-23, Wilson] | 13.5% [13-14, Wilson] |
| K3.by8 | 30.4% [30-31, Wilson] | 22.5% [22-23, Wilson] | 26.4% [26-27, Wilson] |
| K3.never | 69.6% [69-70, Wilson] | 77.5% [77-78, Wilson] | 73.6% [73-74, Wilson] |
| K3.k0 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.3% [2-3, Wilson] | 3.0% [3-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.k3p | 25.7% [25-27, Wilson] | 17.5% [17-18, Wilson] | 21.6% [21-22, Wilson] |
| K4 | 27.9% [27-29, Wilson] | 20.5% [20-21, Wilson] | 24.2% [24-25, Wilson] |
| K5 | 6.4% [6-7, Wilson] | 7.5% [7-8, Wilson] | 6.9% [7-7, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.5 points (-1.7 to -1.3); K3.by4: -1.5 points (-1.7 to -1.3); K3.by5: -2.5 points (-2.8 to -2.3); K3.by6: -3.3 points (-3.7 to -3.0); K3.by7: -10.9 points (-11.4 to -10.4); K3.by8: -19.6 points (-20.3 to -19.0); K3.never: +19.6 points (+19.0 to +20.3); K3.k0: -1.5 points (-1.7 to -1.3); K3.k2: -1.8 points (-2.1 to -1.6); K3.k3p: -16.3 points (-16.9 to -15.7); K4: -18.1 points (-18.8 to -17.5); K5: -3.0 points (-3.3 to -2.7).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 2.0% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by4 | 1.5% [1-2, Wilson] | 3.3% [3-4, Wilson] | 2.4% [2-3, Wilson] |
| K3.by5 | 4.7% [4-5, Wilson] | 3.6% [3-4, Wilson] | 4.1% [4-4, Wilson] |
| K3.by6 | 5.8% [5-6, Wilson] | 3.6% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.by7 | 5.8% [5-6, Wilson] | 3.6% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.by8 | 5.8% [5-6, Wilson] | 3.6% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K3.never | 94.2% [94-95, Wilson] | 96.4% [96-97, Wilson] | 95.3% [95-96, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.5% [1-2, Wilson] | 2.0% [2-2, Wilson] | 1.7% [2-2, Wilson] |
| K3.k3p | 4.3% [4-5, Wilson] | 1.7% [1-2, Wilson] | 3.0% [3-3, Wilson] |
| K4 | 5.8% [5-6, Wilson] | 3.6% [3-4, Wilson] | 4.7% [4-5, Wilson] |
| K5 | 13.1% [12-14, Wilson] | 17.2% [16-18, Wilson] | 15.1% [15-16, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: -1.5 points (-1.8 to -1.2); K3.by5: -4.8 points (-5.2 to -4.4); K3.by6: -6.0 points (-6.5 to -5.6); K3.by7: -6.0 points (-6.5 to -5.6); K3.by8: -6.0 points (-6.5 to -5.6); K3.never: +6.0 points (+5.6 to +6.5); K3.k3p: -5.4 points (-5.8 to -5.1); K4: -6.0 points (-6.5 to -5.6); K5: -6.6 points (-7.0 to -6.1).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 1.0% [1-1, Wilson] |
| K3.by3 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.by4 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.by5 | 2.5% [2-3, Wilson] | 4.8% [4-5, Wilson] | 3.6% [3-4, Wilson] |
| K3.by6 | 4.7% [4-5, Wilson] | 5.0% [5-5, Wilson] | 4.8% [5-5, Wilson] |
| K3.by7 | 4.7% [4-5, Wilson] | 8.8% [8-9, Wilson] | 6.7% [6-7, Wilson] |
| K3.by8 | 7.9% [7-8, Wilson] | 8.9% [8-9, Wilson] | 8.4% [8-9, Wilson] |
| K3.by9 | 7.9% [7-8, Wilson] | 16.9% [16-18, Wilson] | 12.4% [12-13, Wilson] |
| K3.by10 | 19.5% [19-20, Wilson] | 16.9% [16-18, Wilson] | 18.2% [18-19, Wilson] |
| K3.never | 80.5% [80-81, Wilson] | 83.1% [82-84, Wilson] | 81.8% [81-82, Wilson] |
| K3.k0 | 2.5% [2-3, Wilson] | 1.9% [2-2, Wilson] | 2.2% [2-2, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.3% [2-3, Wilson] | 3.0% [3-3, Wilson] | 2.7% [2-3, Wilson] |
| K3.k3p | 14.8% [14-15, Wilson] | 11.9% [11-13, Wilson] | 13.3% [13-14, Wilson] |
| K4 | 17.0% [16-18, Wilson] | 15.0% [14-16, Wilson] | 16.0% [16-17, Wilson] |
| K5 | 6.4% [6-7, Wilson] | 7.8% [7-8, Wilson] | 7.1% [7-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: -1.5 points (-1.7 to -1.3); K3.by4: -1.5 points (-1.7 to -1.3); K3.by5: -2.5 points (-2.8 to -2.3); K3.by6: -3.3 points (-3.7 to -3.0); K3.by7: -13.3 points (-13.9 to -12.8); K3.by8: -28.7 points (-29.4 to -28.0); K3.by9: -28.3 points (-29.0 to -27.6); K3.by10: -25.6 points (-26.2 to -24.9); K3.never: +25.6 points (+24.9 to +26.2); K3.k0: -1.5 points (-1.7 to -1.3); K3.k2: -1.8 points (-2.1 to -1.6); K3.k3p: -22.2 points (-22.9 to -21.6); K4: -24.1 points (-24.7 to -23.4); K5: -3.0 points (-3.3 to -2.7).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | +20.1 (+19.8 to +20.5) FLAG | +20.2 (+19.9 to +20.6) FLAG | +20.2 (+19.9 to +20.4) FLAG |
| K1 Pawniard in play at setup | -1.7 (-1.8 to -1.5) FLAG | -1.7 (-1.9 to -1.6) FLAG | -1.7 (-1.8 to -1.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 1 | -5.5 (-5.8 to -5.2) FLAG | -5.5 (-5.8 to -5.2) FLAG | -5.5 (-5.7 to -5.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -8.5 (-8.8 to -8.2) FLAG | -8.6 (-8.9 to -8.2) FLAG | -8.5 (-8.8 to -8.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -10.7 (-11.0 to -10.3) FLAG | -10.8 (-11.2 to -10.5) FLAG | -10.7 (-11.0 to -10.5) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -12.2 (-12.5 to -11.8) FLAG | -12.4 (-12.8 to -12.1) FLAG | -12.3 (-12.6 to -12.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -13.0 (-13.4 to -12.6) FLAG | -13.1 (-13.4 to -12.7) FLAG | -13.0 (-13.3 to -12.8) FLAG |
| K2 Kingambit in play, own turn 2 | -2.3 (-2.4 to -2.1) FLAG | -2.1 (-2.3 to -2.0) FLAG | -2.2 (-2.3 to -2.1) FLAG |
| K2 Kingambit in play, own turn 3 | -6.0 (-6.2 to -5.7) FLAG | -5.9 (-6.1 to -5.6) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| K2 Kingambit in play, own turn 4 | -11.0 (-11.3 to -10.7) FLAG | -11.0 (-11.3 to -10.6) FLAG | -11.0 (-11.2 to -10.7) FLAG |
| K2 Kingambit in play, own turn 5 | -16.5 (-16.8 to -16.1) FLAG | -16.7 (-17.1 to -16.3) FLAG | -16.6 (-16.8 to -16.3) FLAG |
| K2 Kingambit in play, own turn 6 | -21.0 (-21.4 to -20.6) FLAG | -20.9 (-21.3 to -20.5) FLAG | -21.0 (-21.3 to -20.7) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | -3.1 (-3.5 to -2.7) FLAG | -3.4 (-3.8 to -3.0) FLAG | -3.3 (-3.5 to -3.0) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | -4.7 (-5.1 to -4.2) FLAG | -4.8 (-5.3 to -4.4) FLAG | -4.8 (-5.1 to -4.5) FLAG |
| G3 Pawniard in play, own turn 1 | -5.5 (-5.8 to -5.2) FLAG | -5.5 (-5.8 to -5.2) FLAG | -5.5 (-5.7 to -5.3) FLAG |
| G3 Pawniard in play, own turn 2 | -6.2 (-6.6 to -5.9) FLAG | -6.4 (-6.7 to -6.1) FLAG | -6.3 (-6.5 to -6.1) FLAG |
| G3 Pawniard in play, own turn 3 | -4.7 (-5.1 to -4.3) FLAG | -5.0 (-5.3 to -4.6) FLAG | -4.8 (-5.1 to -4.6) FLAG |
| G3 Pawniard in play, own turn 4 | -1.2 (-1.6 to -0.8) FLAG | -1.4 (-1.8 to -1.1) FLAG | -1.3 (-1.6 to -1.1) FLAG |
| G3 Pawniard in play, own turn 5 | +3.5 (+3.1 to +3.8) FLAG | +3.6 (+3.2 to +4.0) FLAG | +3.5 (+3.3 to +3.8) FLAG |
| G3 Kingambit in play, own turn 2 | -2.3 (-2.4 to -2.1) FLAG | -2.1 (-2.3 to -2.0) FLAG | -2.2 (-2.3 to -2.1) FLAG |
| G3 Kingambit in play, own turn 3 | -6.0 (-6.2 to -5.7) FLAG | -5.9 (-6.1 to -5.6) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| G3 Kingambit in play, own turn 4 | -11.0 (-11.3 to -10.7) FLAG | -11.0 (-11.3 to -10.6) FLAG | -11.0 (-11.2 to -10.7) FLAG |
| G3 Kingambit in play, own turn 5 | -16.5 (-16.8 to -16.1) FLAG | -16.7 (-17.1 to -16.3) FLAG | -16.6 (-16.8 to -16.3) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -6.2 (-6.5 to -5.9) FLAG | -6.2 (-6.5 to -5.9) FLAG | -6.2 (-6.4 to -6.0) FLAG |
| G3 Alolan Grimer in play, own turn 2 | -6.6 (-7.0 to -6.3) FLAG | -6.6 (-6.9 to -6.3) FLAG | -6.6 (-6.9 to -6.4) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -4.4 (-4.8 to -4.1) FLAG | -4.3 (-4.6 to -3.9) FLAG | -4.3 (-4.6 to -4.1) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -1.5 (-1.9 to -1.2) FLAG | -1.3 (-1.6 to -0.9) FLAG | -1.4 (-1.6 to -1.1) FLAG |
| G3 Alolan Muk in play, own turn 2 | -2.4 (-2.6 to -2.1) FLAG | -2.6 (-2.8 to -2.3) FLAG | -2.5 (-2.7 to -2.3) FLAG |
| G3 Alolan Muk in play, own turn 3 | -6.6 (-6.9 to -6.3) FLAG | -7.0 (-7.3 to -6.6) FLAG | -6.8 (-7.0 to -6.5) FLAG |
| G3 Alolan Muk in play, own turn 4 | -10.6 (-10.9 to -10.2) FLAG | -10.9 (-11.3 to -10.5) FLAG | -10.7 (-11.0 to -10.5) FLAG |
| G3 Alolan Muk in play, own turn 5 | -13.4 (-13.8 to -13.0) FLAG | -13.4 (-13.9 to -13.0) FLAG | -13.4 (-13.7 to -13.1) FLAG |
| G3 Glimmet in play, own turn 1 | -5.4 (-5.7 to -5.2) FLAG | -5.8 (-6.1 to -5.6) FLAG | -5.6 (-5.8 to -5.4) FLAG |
| G3 Glimmet in play, own turn 2 | -5.8 (-6.2 to -5.4) FLAG | -5.6 (-6.0 to -5.3) FLAG | -5.7 (-6.0 to -5.4) FLAG |
| G3 Glimmet in play, own turn 3 | -3.7 (-4.1 to -3.3) FLAG | -3.3 (-3.7 to -2.9) FLAG | -3.5 (-3.8 to -3.2) FLAG |
| G3 Glimmet in play, own turn 5 | +4.5 (+4.2 to +4.9) FLAG | +5.1 (+4.7 to +5.4) FLAG | +4.8 (+4.5 to +5.1) FLAG |
| G3 Glimmora in play, own turn 2 | -8.1 (-8.4 to -7.8) FLAG | -8.3 (-8.6 to -8.0) FLAG | -8.2 (-8.4 to -8.0) FLAG |
| G3 Glimmora in play, own turn 3 | -10.6 (-10.9 to -10.3) FLAG | -10.8 (-11.1 to -10.5) FLAG | -10.7 (-10.9 to -10.5) FLAG |
| G3 Glimmora in play, own turn 4 | -11.5 (-11.8 to -11.2) FLAG | -11.6 (-11.9 to -11.3) FLAG | -11.5 (-11.7 to -11.3) FLAG |
| G3 Glimmora in play, own turn 5 | -11.0 (-11.3 to -10.7) FLAG | -11.0 (-11.3 to -10.7) FLAG | -11.0 (-11.2 to -10.8) FLAG |
| G3 Regigigas in play, own turn 1 | +21.7 (+21.3 to +22.1) FLAG | +21.6 (+21.2 to +22.0) FLAG | +21.6 (+21.4 to +21.9) FLAG |
| G3 Regigigas in play, own turn 2 | +18.3 (+17.9 to +18.6) FLAG | +18.6 (+18.2 to +19.0) FLAG | +18.4 (+18.2 to +18.7) FLAG |
| G3 Regigigas in play, own turn 3 | +15.5 (+15.2 to +15.8) FLAG | +15.7 (+15.3 to +16.0) FLAG | +15.6 (+15.3 to +15.8) FLAG |
| G3 Regigigas in play, own turn 4 | +13.9 (+13.5 to +14.2) FLAG | +13.9 (+13.6 to +14.3) FLAG | +13.9 (+13.7 to +14.1) FLAG |
| G3 Regigigas in play, own turn 5 | +12.9 (+12.6 to +13.3) FLAG | +13.0 (+12.6 to +13.3) FLAG | +13.0 (+12.7 to +13.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -7.2 (-7.5 to -6.9) FLAG | -7.4 (-7.7 to -7.0) FLAG | -7.3 (-7.5 to -7.1) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -7.2 (-7.5 to -6.9) FLAG | -7.4 (-7.6 to -7.1) FLAG | -7.3 (-7.5 to -7.1) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -5.9 (-6.1 to -5.7) FLAG | -5.8 (-6.0 to -5.6) FLAG | -5.9 (-6.0 to -5.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | -4.0 (-4.2 to -3.8) FLAG | -3.9 (-4.1 to -3.7) FLAG | -4.0 (-4.1 to -3.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | -2.3 (-2.4 to -2.1) FLAG | -2.1 (-2.3 to -2.0) FLAG | -2.2 (-2.3 to -2.1) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | -6.0 (-6.2 to -5.7) FLAG | -5.9 (-6.1 to -5.6) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | -11.0 (-11.3 to -10.7) FLAG | -11.0 (-11.3 to -10.6) FLAG | -11.0 (-11.2 to -10.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | -16.5 (-16.8 to -16.1) FLAG | -16.7 (-17.1 to -16.3) FLAG | -16.6 (-16.8 to -16.3) FLAG |
| G5.any3 an empty own turn among turns 1-3 | +26.5 (+26.1 to +26.9) FLAG | +26.5 (+26.1 to +26.9) FLAG | +26.5 (+26.2 to +26.8) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | -2.1 (-2.3 to -2.0) FLAG | -1.1 (-1.2 to -1.0) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | -4.0 (-4.3 to -3.8) FLAG | -5.9 (-6.1 to -5.6) FLAG | -5.0 (-5.1 to -4.8) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | -11.0 (-11.3 to -10.7) FLAG | -11.0 (-11.3 to -10.6) FLAG | -11.0 (-11.2 to -10.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | -16.5 (-16.8 to -16.1) FLAG | -16.7 (-17.1 to -16.3) FLAG | -16.6 (-16.8 to -16.3) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.855 (+0.849 to +0.862) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, -1 Mesagoza B2a 093 +1 Regigigas B3 134.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): +20.2 points
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn -5.4 points (-6.5 to -4.4); P2 both Glimmora had their turn -15.6 points (-19.4 to -11.9); P2 the first Glimmora placed had its turn -4.3 points (-5.9 to -2.7); P2 the second Glimmora placed had its turn -16.7 points (-20.4 to -12.8); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.8 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -3.1 points (-7.2 to -0.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -10.5 points (-13.1 to -8.0); P4 ready at the winning moment: Knocks out their strongest -3.6 points (-7.3 to -0.2); P5 plan reached in time: Knocks out their strongest -4.8 points (-9.0 to -0.9)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -6.5 points (-7.3 to -5.5); P2 both Glimmora had their turn -15.5 points (-19.4 to -12.4); P2 the first Glimmora placed had its turn -5.8 points (-6.6 to -4.8); P2 the second Glimmora placed had its turn -16.2 points (-20.0 to -13.2); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.9 to -4.0); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -4.3 points (-10.3 to -0.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -10.9 points (-13.7 to -7.7); P4 ready at the winning moment: Knocks out their strongest -2.8 points (-6.3 to -0.4); P5 plan reached in time: Knocks out their strongest -3.4 points (-7.4 to -0.8)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -7.6 points (-8.9 to -6.3); P2 both Glimmora had their turn -15.0 points (-17.1 to -13.0); P2 the first Glimmora placed had its turn -5.2 points (-6.1 to -4.3); P2 the second Glimmora placed had its turn -17.4 points (-19.0 to -15.7); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.7 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -10.1 points (-12.6 to -7.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -15.7 points (-17.8 to -13.8); P4 ready at the winning moment: Knocks out their strongest -2.2 points (-3.6 to -1.0); P4 not ready, ready 1 turn late -1.2 points (-2.1 to -0.4); P4 the moment came and Kingambit was never ready in the deal +2.7 points (+1.4 to +4.1); P5 plan reached in time: Knocks out their strongest -3.3 points (-5.0 to -2.0)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn -5.2 points (-5.7 to -4.7); P2 both Glimmora had their turn -6.9 points (-7.4 to -6.4); P2 the first Glimmora placed had its turn -1.1 points (-1.6 to -0.5); P2 the second Glimmora placed had its turn -11.0 points (-11.6 to -10.4); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.7 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -8.2 points (-8.7 to -7.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -18.9 points (-19.5 to -18.2); P4 ready at the winning moment: Knocks out their strongest -4.6 points (-5.0 to -4.2); P4 ready at the winning moment: Wins outright (a lower bound) -4.6 points (-5.0 to -4.2); P4 the moment came and Kingambit was never ready in the deal +2.1 points (+1.6 to +2.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.3 points (+2.8 to +3.8); P5 plan reached in time: Knocks out their strongest -5.4 points (-5.8 to -5.0); P5 plan reached in time: Wins outright (a lower bound) -5.4 points (-5.8 to -5.0)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn -7.7 points (-8.1 to -7.2); P2 both Glimmora had their turn -13.5 points (-14.2 to -12.9); P2 the first Glimmora placed had its turn -6.7 points (-7.1 to -6.2); P2 the second Glimmora placed had its turn -14.5 points (-15.2 to -13.9); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.7 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -13.4 points (-14.0 to -12.8); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -22.5 points (-23.2 to -21.9); P4 ready at the winning moment: Knocks out their strongest -10.3 points (-10.8 to -9.8); P4 not ready, ready 1 turn late -1.0 points (-1.2 to -0.8); P4 the moment came and Kingambit was never ready in the deal +3.7 points (+3.2 to +4.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +7.5 points (+7.1 to +8.0); P5 plan reached in time: Knocks out their strongest -11.3 points (-11.8 to -10.8)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn -6.0 points (-6.4 to -5.6); P2 both Glimmora had their turn -25.6 points (-26.3 to -24.9); P2 the first Glimmora placed had its turn -4.5 points (-4.9 to -4.0); P2 the second Glimmora placed had its turn -27.2 points (-27.9 to -26.5); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.7 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -2.8 points (-3.1 to -2.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -14.5 points (-15.1 to -13.9); P4 ready at the winning moment: Knocks out their strongest -13.8 points (-14.4 to -13.2); P4 ready at the winning moment: Wins outright (a lower bound) -13.8 points (-14.4 to -13.2); P4 not ready, ready 1 turn late +1.5 points (+1.2 to +1.8); P4 the moment came and Kingambit was never ready in the deal +2.8 points (+2.3 to +3.4); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +9.5 points (+9.0 to +9.9); P5 plan reached in time: Knocks out their strongest -12.3 points (-12.9 to -11.7); P5 plan reached in time: Wins outright (a lower bound) -12.3 points (-12.9 to -11.7)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn -5.2 points (-5.8 to -4.7); P2 both Glimmora had their turn -7.0 points (-7.4 to -6.5); P2 the first Glimmora placed had its turn -1.1 points (-1.6 to -0.5); P2 the second Glimmora placed had its turn -11.2 points (-11.7 to -10.6); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.7 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -9.1 points (-9.7 to -8.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -18.9 points (-19.5 to -18.2); P4 ready at the winning moment: Knocks out their strongest -1.2 points (-1.4 to -1.0); P4 ready at the winning moment: Wins outright (a lower bound) -1.2 points (-1.4 to -1.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +2.1 points (+1.8 to +2.4); P5 plan reached in time: Knocks out their strongest -1.2 points (-1.4 to -1.0); P5 plan reached in time: Wins outright (a lower bound) -1.2 points (-1.4 to -1.0)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn -5.8 points (-6.2 to -5.4); P2 both Glimmora had their turn -22.3 points (-23.0 to -21.6); P2 the first Glimmora placed had its turn -4.5 points (-4.9 to -4.0); P2 the second Glimmora placed had its turn -23.6 points (-24.4 to -22.9); P3 plan broken in front, cause: Pawniard forced to lead -4.4 points (-4.7 to -4.1); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) -27.8 points (-28.4 to -27.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -24.3 points (-25.0 to -23.6); P4 ready at the winning moment: Knocks out their strongest +4.6 points (+4.2 to +5.0); P4 ready at the winning moment: Wins outright (a lower bound) +4.6 points (+4.2 to +5.0); P4 the moment came and Kingambit was never ready in the deal -9.6 points (-10.0 to -9.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +4.7 points (+4.3 to +5.0); P5 plan reached in time: Knocks out their strongest +4.9 points (+4.5 to +5.3); P5 plan reached in time: Wins outright (a lower bound) +4.9 points (+4.5 to +5.3)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): G3 Pawniard in play, own turn 5 +3.5 points; G3 Glimmet in play, own turn 5 +4.8 points; G3 Regigigas in play, own turn 1 +21.6 points; G3 Regigigas in play, own turn 2 +18.4 points; G3 Regigigas in play, own turn 3 +15.6 points; G3 Regigigas in play, own turn 4 +13.9 points; G3 Regigigas in play, own turn 5 +13.0 points.
Gives up (flagged, pooled): K1 Pawniard in play at setup -1.7 points; K1 Pawniard line in play (end of own turn t), own turn 1 -5.5 points; K1 Pawniard line in play (end of own turn t), own turn 2 -8.5 points; K1 Pawniard line in play (end of own turn t), own turn 3 -10.7 points; K1 Pawniard line in play (end of own turn t), own turn 4 -12.3 points; K1 Pawniard line in play (end of own turn t), own turn 5 -13.0 points; K2 Kingambit in play, own turn 2 -2.2 points; K2 Kingambit in play, own turn 3 -5.9 points; K2 Kingambit in play, own turn 4 -11.0 points; K2 Kingambit in play, own turn 5 -16.6 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 -1.4; K3.by4 -1.8; K3.by5 -2.3; K3.by6 -3.5; K3.by7 -5.6; K3.by8 -6.9; K3.never +4.8; K3.k0 -1.8; K3.k2 -2.3; K4 -5.1; K5 -2.3; C-his, seat-matched: K3.by3 -1.6; K3.by4 -2.0; K3.by5 -2.6; K3.by6 -2.8; K3.by7 -7.6; K3.by8 -7.6; K3.k0 -2.0; K3.k2 -1.9; K4 -5.6; K5 -2.2; C-bot: K3.by3 -1.4; K3.by4 -1.9; K3.by5 -2.5; K3.by6 -3.5; K3.by7 -4.8; K3.by8 -5.9; K3.never +5.3; K3.k0 -1.8; K3.k3p -3.1; K4 -4.0; K5 -2.7; C-fixed fast: K3.by4 -1.4; K3.by5 -4.7; K3.by6 -5.9; K3.by7 -5.9; K3.by8 -5.9; K3.never +5.9; K3.k3p -5.3; K4 -5.9; K5 -6.6; C-fixed medium: K3.by3 -1.5; K3.by4 -1.9; K3.by5 -5.2; K3.by6 -12.9; K3.by7 -14.4; K3.by8 -14.4; K3.never +14.4; K3.k0 -1.5; K3.k3p -12.3; K4 -12.8; K5 -5.1; C-fixed slow: K3.by3 -1.5; K3.by4 -1.5; K3.by5 -2.5; K3.by6 -3.3; K3.by7 -10.9; K3.by8 -19.6; K3.never +19.6; K3.k0 -1.5; K3.k2 -1.8; K3.k3p -16.3; K4 -18.1; K5 -3.0; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 -1.5; K3.by5 -4.8; K3.by6 -6.0; K3.by7 -6.0; K3.by8 -6.0; K3.never +6.0; K3.k3p -5.4; K4 -6.0; K5 -6.6; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 -1.5; K3.by4 -1.5; K3.by5 -2.5; K3.by6 -3.3; K3.by7 -13.3; K3.by8 -28.7; K3.by9 -28.3; K3.by10 -25.6; K3.never +25.6; K3.k0 -1.5; K3.k2 -1.8; K3.k3p -22.2; K4 -24.1; K5 -3.0.
Not valued here (changed cards the script never plays: they count as blanks): none.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## How much each open choice matters (on the base list)

Each alternative is run once on the base list on the same deals, against the default config (T-first-KO, Copycat by his valuation, approximated, the Pawniard line after an Active Glimmora's Energy, the promotion order of the plan file). Pooled differences in percentage points, with "*" for a range that excludes 0 and a difference of at least 1 point. Ranges: the per-game bootstrap over the recorded games under C-his and C-bot (a bootstrap over the recorded games, 1,000 resamples), the paired test on the same deals under C-fixed and for the setup measures. These runs are on the base only; nothing here is a version.

Setup measures with no knock-outs (Pawniard is benched at once under T-first-KO and T-late there, so the bench-trigger rows differ only on T-now and T-pieces):

| Alternative | P1 | K1.t1 | K1.t3 | K2.t3 | K2.t5 | G5.any3 | G6.t3 |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +0.0 | +0.3 | +5.0* | +0.5 | +4.9* | +0.7 | +0.4 |
| T-late: Pawniard benched one own turn after T-first-KO | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | -39.7* | -47.2* | -8.0* | -18.0* | -0.2 | -7.2* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | -5.3* | +0.0 | +0.0 | +0.0 | +0.1 | -0.2 | +0.4 |
| Poke Ball over names, not cards | +0.0 | +1.3* | +0.8 | +0.2 | +0.1 | +0.2 | +0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | +0.0 | -1.9* | -3.8* | -2.8* | -4.7* | +7.5* | -2.4* |
| Copycat never played | +0.0 | -2.6* | -4.4* | -4.8* | -8.2* | +9.8* | -4.2* |
| Energy order: the Pawniard line before an Active Glimmora | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +1.8* |
| promotion order: Regigigas first | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | +0.0 | -2.1* | -3.2* | -4.4* | -8.0* | +6.1* | -3.9* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +0.0 | +2.2* | +3.5* | +8.6* | +12.6* | -3.2* | +7.5* |

Plan lines under C-his, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.7 | -2.6 | +0.0 | +2.5* | -1.9* | +6.4* | +0.1 | +4.8* | +0.0 | -2.5* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.3 | +2.1* | +0.0 | -2.1* | +0.5 | -2.1* | +0.0 | -2.5* | +0.0 | +3.1* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -1.0 | -0.6 | +0.0 | -1.6* | +0.9 | -0.4 | -0.5 | -2.2 | -0.4 | +2.4* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.9 | +1.0 | +16.8* | -1.3* | -4.9* | -2.6* | -0.4 | -3.7* | -0.5 | -0.7 |
| Poke Ball over names, not cards | -0.7 | -0.2 | +0.0 | -0.1 | +0.4 | -0.1 | -0.1 | -0.1 | -0.1 | +0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -2.9* | -5.0* | +0.0 | +1.0* | +2.4* | -0.9 | -0.3 | -1.2 | -0.3 | +1.8* |
| Copycat never played | -3.5* | -6.9* | +0.0 | +1.3* | +3.6* | -1.6 | -0.6 | -2.2* | -0.6 | +2.5* |
| Energy order: the Pawniard line before an Active Glimmora | -15.7* | -17.5* | +0.0 | -0.2 | +0.0 | +3.3 | +0.0 | +4.6* | +0.0 | -0.5 |
| promotion order: Regigigas first | -7.1* | -13.3* | +0.0 | +0.2 | +0.1 | +1.2 | -0.1 | +1.9 | -0.1 | -0.0 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | +0.0 | -0.0 | +0.0 | +0.0 | +0.0 | -0.0 | +0.0 | -0.0 | +0.0 | +0.0 |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | -0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |

Plan lines under C-his, seat-matched, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.8 | -2.1 | +0.0 | +2.5* | -2.3* | +5.9* | +0.1 | +4.4* | +0.0 | -2.6* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.4 | +2.4* | +0.0 | -3.2* | +0.5 | -2.7* | -0.0 | -2.7* | +0.0 | +3.6* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.9 | -0.5 | +0.0 | -2.0 | +0.6 | -0.2 | -0.4 | -1.3 | -0.3 | +2.2* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.4 | +0.4 | +16.8* | -1.7* | -5.1* | -2.1* | -0.4 | -3.1* | -0.5 | -0.6 |
| Poke Ball over names, not cards | -0.8 | -0.3 | +0.0 | +0.0 | +0.0 | +0.1 | -0.0 | +0.0 | -0.0 | +0.1 |
| Copycat: the fallback rule (his 2 v 8), approximated | -2.8* | -5.2* | +0.0 | +0.7 | +2.4* | -0.7 | -0.4 | -0.8 | -0.3 | +1.8* |
| Copycat never played | -3.4* | -6.8* | +0.0 | +0.7 | +3.5* | -1.3* | -0.6 | -1.5* | -0.5 | +2.6* |
| Energy order: the Pawniard line before an Active Glimmora | -19.3* | -21.1* | +0.0 | -0.2 | +0.0 | +3.4 | +0.0 | +4.3* | +0.0 | -0.5 |
| promotion order: Regigigas first | -7.9* | -13.2* | +0.0 | +0.2 | +0.1 | +1.1 | -0.1 | +1.7 | -0.1 | +0.1 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | +0.0 | -0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |

Plan lines under C-bot, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.4 | +6.7* | +0.0 | +4.4* | -3.9* | +3.4* | -0.0 | +1.6* | +0.0 | -7.5* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.4 | +6.1* | +0.0 | -7.0* | +5.7* | -1.9* | -0.0 | -1.7* | -0.0 | +4.3* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.6 | +3.0* | +0.0 | -3.0* | +1.3* | -1.0 | -0.1 | -2.5* | -0.1 | -1.5* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.5 | +3.5* | +16.8* | -3.3* | -6.4* | -1.4* | -0.1 | -2.5* | -0.1 | -2.6* |
| Poke Ball over names, not cards | -0.7 | +0.1 | +0.0 | -0.0 | +0.4 | -0.2 | -0.0 | -0.1 | +0.0 | +0.0 |
| Copycat: the fallback rule (his 2 v 8), approximated | -3.8* | -5.7* | +0.0 | +0.4 | +2.9* | -0.5 | -0.1 | -1.2* | -0.1 | +0.4 |
| Copycat never played | -4.4* | -7.1* | +0.0 | +0.0 | +4.4* | -0.9 | -0.1 | -1.8* | -0.1 | +0.8 |
| Energy order: the Pawniard line before an Active Glimmora | -19.3* | -20.6* | +0.0 | -1.8* | +0.0 | +3.2* | +0.0 | +1.5* | +0.0 | -1.5* |
| promotion order: Regigigas first | -2.6* | -9.0* | +0.0 | -0.3 | +0.3 | +1.2* | -0.0 | +0.2 | -0.0 | -0.4 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -3.3* | -5.5* | +0.0 | -0.7 | +4.0* | -1.0* | -0.1 | -1.9* | -0.1 | +1.0* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +2.3* | +3.9* | +0.0 | +2.8* | -5.3* | +1.5* | +0.2 | +2.2* | +0.2 | -2.1* |

Plan lines under C-fixed fast, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.1 | -0.6 | +0.0 | +3.9* | -0.9 | +1.2* | +1.2* | +0.9 | +0.9 | -5.3* |
| T-late: Pawniard benched one own turn after T-first-KO | +1.4* | +2.2* | +0.0 | -11.4* | +2.4* | -3.7* | -3.7* | -3.2* | -3.2* | +6.5* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.4 | +0.7 | +0.0 | -12.1* | +0.2 | -4.5* | -4.5* | -4.9* | -4.9* | +1.6* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +2.9* | +2.6* | +16.8* | -4.9* | -5.4* | -2.3* | -2.3* | -2.5* | -2.5* | +2.5* |
| Poke Ball over names, not cards | -1.7* | +0.1 | +0.0 | -0.0 | +0.3 | -0.1 | -0.1 | -0.0 | -0.0 | -0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -5.7* | -4.2* | +0.0 | +1.1* | -0.7 | -2.3* | -2.3* | -2.8* | -2.8* | +1.6* |
| Copycat never played | -6.6* | -5.7* | +0.0 | +1.1* | -0.1 | -3.8* | -3.8* | -4.4* | -4.4* | +2.8* |
| Energy order: the Pawniard line before an Active Glimmora | -27.0* | -11.4* | +0.0 | -4.3* | +0.0 | +1.8* | +1.8* | +1.4* | +1.4* | -2.5* |
| promotion order: Regigigas first | -1.2* | -2.0* | +0.0 | -0.9 | +0.8 | -0.1 | -0.1 | -0.1 | -0.1 | -0.5 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.7* | -4.0* | +0.0 | +0.6 | -0.1 | -3.5* | -3.5* | -4.0* | -4.0* | +2.5* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +4.2* | +3.6* | +0.0 | +1.8* | -1.8* | +7.4* | +7.4* | +7.9* | +7.9* | -6.0* |

Plan lines under C-fixed medium, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +0.7 | +4.7* | +0.0 | -4.2* | -3.2* | +2.6* | +0.0 | +1.9* | +0.0 | -7.8* |
| T-late: Pawniard benched one own turn after T-first-KO | +1.3* | +7.3* | +0.0 | -11.7* | +6.9* | -7.9* | +0.0 | -6.0* | +0.0 | +11.3* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.5 | +2.5* | +0.0 | -11.2* | +0.6 | -6.9* | +0.0 | -7.1* | +0.0 | +2.5* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +1.2* | +3.7* | +16.8* | -5.0* | -6.0* | -4.3* | +0.0 | -4.7* | +0.0 | +0.4 |
| Poke Ball over names, not cards | -1.1* | -0.2 | +0.0 | -0.1 | -0.2 | +0.0 | +0.0 | +0.0 | +0.0 | -0.1 |
| Copycat: the fallback rule (his 2 v 8), approximated | -4.8* | -7.2* | +0.0 | +0.5 | +0.1 | -3.8* | +0.0 | -4.5* | +0.0 | +3.2* |
| Copycat never played | -5.6* | -8.9* | +0.0 | -0.1 | +0.9 | -5.8* | +0.0 | -6.7* | +0.0 | +5.0* |
| Energy order: the Pawniard line before an Active Glimmora | -29.8* | -22.1* | +0.0 | -10.4* | +0.0 | +2.8* | +0.0 | +2.0* | +0.0 | -3.6* |
| promotion order: Regigigas first | -2.7* | -6.6* | +0.0 | -3.2* | +1.3* | -0.2 | +0.0 | -0.2 | +0.0 | -1.4* |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.1* | -6.4* | +0.0 | -0.6 | +1.0* | -5.6* | +0.0 | -6.4* | +0.0 | +4.9* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +3.4* | +4.6* | +0.0 | +4.5* | -4.1* | +11.0* | +0.0 | +11.0* | +0.0 | -9.9* |

Plan lines under C-fixed slow, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +1.6* | +2.1* | +0.0 | +2.7* | -1.5* | +1.1* | +1.1* | +0.8 | +0.8 | -3.2* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.6 | +0.7 | +0.0 | -2.0* | +3.6* | +0.3 | +0.3 | +0.4 | +0.4 | +2.2* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.4 | -0.8 | +0.0 | +0.9 | +6.0* | -5.9* | -5.9* | -5.2* | -5.2* | +8.7* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.9 | +3.4* | +16.8* | -1.4* | -5.7* | -8.3* | -8.3* | -8.7* | -8.7* | +4.4* |
| Poke Ball over names, not cards | -0.3 | -0.4 | +0.0 | -0.2 | +0.4 | -0.1 | -0.1 | +0.1 | +0.1 | +0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -3.5* | -9.2* | +0.0 | +2.8* | +4.3* | -6.0* | -6.0* | -5.9* | -5.9* | +4.3* |
| Copycat never played | -4.0* | -11.9* | +0.0 | +3.7* | +6.8* | -8.7* | -8.7* | -8.2* | -8.2* | +6.8* |
| Energy order: the Pawniard line before an Active Glimmora | -7.7* | -38.2* | +0.0 | -0.7 | +0.0 | +0.0 | +0.0 | +0.1 | +0.1 | -0.4 |
| promotion order: Regigigas first | +0.7 | -8.1* | +0.0 | +0.4 | +0.3 | -1.4* | -1.4* | -1.5* | -1.5* | +1.2* |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -3.0* | -9.2* | +0.0 | +2.4* | +6.4* | -8.1* | -8.1* | -7.5* | -7.5* | +7.3* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +2.1* | +9.0* | +0.0 | -1.7* | -7.4* | +7.5* | +7.5* | +6.4* | +6.4* | -10.0* |

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex), difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.1 | -0.5 | +0.0 | +7.1* | -0.9 | -0.1 | -0.1 | -0.1 | -0.1 | -4.7* |
| T-late: Pawniard benched one own turn after T-first-KO | +1.3* | +2.1* | +0.0 | -12.8* | +2.4* | +0.4 | +0.4 | +0.4 | +0.4 | +6.1* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.5 | +0.7 | +0.0 | -12.1* | +0.2 | -0.8 | -0.8 | -0.8 | -0.8 | +1.7* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +2.9* | +2.6* | +16.8* | -5.3* | -5.4* | -0.4 | -0.4 | -0.4 | -0.4 | +2.3* |
| Poke Ball over names, not cards | -1.7* | +0.1 | +0.0 | +0.1 | +0.3 | +0.0 | +0.0 | +0.0 | +0.0 | -0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -5.7* | -4.2* | +0.0 | +0.9 | -0.7 | -0.6 | -0.6 | -0.6 | -0.6 | +1.5* |
| Copycat never played | -6.6* | -5.7* | +0.0 | +0.8 | -0.1 | -1.1* | -1.1* | -1.1* | -1.1* | +2.6* |
| Energy order: the Pawniard line before an Active Glimmora | -26.7* | -11.4* | +0.0 | -0.5 | +0.0 | +0.1 | +0.1 | +0.1 | +0.1 | -1.5* |
| promotion order: Regigigas first | -0.8 | -2.0* | +0.0 | +0.4 | +0.8 | +0.1 | +0.1 | +0.1 | +0.1 | -0.3 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.7* | -4.1* | +0.0 | +0.2 | -0.1 | -0.9 | -0.9 | -0.9 | -0.9 | +2.4* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +4.3* | +3.6* | +0.0 | +2.4* | -1.8* | +1.2* | +1.2* | +1.2* | +1.2* | -5.8* |

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns), difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +1.6* | +2.1* | +0.0 | +4.2* | -0.7 | -0.2 | -0.2 | -0.2 | -0.2 | -3.0* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.6 | +1.7* | +0.0 | -3.1* | +2.8* | +0.6 | +0.6 | +0.6 | +0.6 | +2.6* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.4 | -1.0 | +0.0 | -6.3* | +4.3* | +1.1* | +1.1* | +1.0 | +1.0 | +4.9* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.9 | +3.1* | +16.8* | -6.8* | -3.9* | -1.2* | -1.2* | -1.2* | -1.2* | +3.9* |
| Poke Ball over names, not cards | -0.3 | -0.1 | +0.0 | -0.4 | +0.2 | +0.2 | +0.2 | +0.2 | +0.2 | +0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -3.5* | -8.9* | +0.0 | -2.4* | +2.3* | -0.3 | -0.3 | -0.3 | -0.3 | +3.9* |
| Copycat never played | -4.0* | -11.6* | +0.0 | -4.0* | +3.7* | -0.1 | -0.1 | -0.1 | -0.1 | +5.7* |
| Energy order: the Pawniard line before an Active Glimmora | -7.1* | -38.8* | +0.0 | -0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| promotion order: Regigigas first | +0.7 | -4.1* | +0.0 | +0.8 | +0.9 | +0.4 | +0.4 | +0.4 | +0.4 | -1.1* |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -3.0* | -9.1* | +0.0 | -4.1* | +3.7* | +0.1 | +0.1 | +0.1 | +0.1 | +5.7* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +2.1* | +8.9* | +0.0 | +6.2* | -4.4* | -0.8 | -0.8 | -0.9 | -0.9 | -7.1* |

## The run record

- **code sha256**: 9d6774d1005749390161601f6f24903d595500db611f8ad667aadcfc5d0bfcb0
- **engine commit**: pinned rules-switch-2 engine, main 70319c3d (engine unchanged since c045ede); no engine program is run
- **rulings**: R1: glimmora_turn=attacked_once; R2: never_evolve_active_grimer; P3_by_cause; R3: slow=180hp_k3_turns_3_5_7; 220hp_reference_horizon_10; by: coordinator, Oct 15
- **seeds**: 24,700,000,000 + deal index i (deal i is the same in every version and under every clock); 100,000 deals with no knock-outs, 20,000 deals per clock
- **clock sources**: C-his: rl/results/pause_games_new_2026-10-13/v2/positions_all.json (12 Kingambit games); C-bot: rl/results/kx3_on_rules2_2026-10/replay_b/games.jsonl (64 deck-01 rows); C-fixed: fast, medium, slow, and the 190- and 220-HP references (SPEC, R3)
- **base list**: decks/dustin/01-kingambit-as-played.txt (card-list id 73dfed58d1d6)
- **plan config**: rl/setup_tester/plans/kingambit.json
- **plan overrides**: none
- **wall time**: 661 s, 9 process(es) (every version under both Copycat rules, and the choice runs, included)
- **speed**: 1,337 deals per second per process (4,680,000 deals in 3501 s of version time)

