# Setup tester: kingambit_A_A1_A2

Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on the same deals for every version. It does not say who wins.
**Plan config follows SPEC_AMENDMENT_1 (Dustin, Oct 15) and the coordinator's rulings R1-R3 (Oct 15):** Regigigas leads; Pawniard is held until the bench trigger (first_ko; default first_ko = our first turn after one of ours was knocked out, a spot free); Grimer and Muk are benched, and an Active Alolan Grimer is never evolved into Muk (R2); a Glimmora has had its turn when it attacked at least once (R1); Energy goes to Kingambit up to [DD], then an Active Glimmora that has not attacked yet and has no [D], then the Pawniard line up to [DD], then Regigigas while Muk is in play (R1; the other order runs as a choices row). The lines that lead are P1-P5, P3 by cause (R2); the old G and K lines stay below "descriptive (speed is not the goal)". The slow pace is knockouts on their turns 3, 5 and 7 against a 180-HP Mega ex; the 220-HP Mega is a reference row with 10 own turns (R3). The no-knock-out runs have no knock-out to trigger first_ko, so Pawniard is benched at once (trigger "at_once") and no Bench slot is reserved; the old T-now reserved one.
**Copycat is played by his valuation, approximated** (Dustin, Oct 15: "an updated approximate valuation of card values, based on what I have in play, what cards are left in the deck, how many cards I have, they have, and whether a shuffle and new hand is likely to be more valuable to winning than keeping my current hand"): it is played when the expected value of a fresh hand beats the current hand's value under the value table below. A fresh hand is the opponent's hand count of cards from deck plus hand reshuffled, estimated from 16 sampled hands per decision drawn from the tester's own seed block. The value table is written from the plan's own needs, with no tuned constants; Dustin can correct a value.
**His rule, approximated, as a check:** the fallback rule runs on the base and on every version. The two disagree at base: 118,722 of 279,664 Copycat decisions (42.5%).
**WARNING, the Copycat rule changes a verdict:** A1: fast P3.grimer_muk - only under the valuation, his P3.grimer_muk - only under the valuation, medium P3.pawn_promo + only under the valuation, ref190 P3.grimer_muk - only under the valuation, ref190 P3.pawn_promo + only under the valuation, ref220 P2.both - only under the fallback rule, ref220 P2.g2 - only under the fallback rule, ref220 P4.never + only under the valuation, slow P2.both - only under the fallback rule, slow P2.g2 - only under the fallback rule; A2: his_seat P4.ko + only under the fallback rule, medium P4.late1 - only under the valuation, ref190 P4.never - only under the valuation, ref220 P3.pawn_promo + only under the fallback rule, slow P4.never - only under the fallback rule. The laptop shows Dustin one such hand.
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

## A1 (card-list id 6f3bbf39374e)

Changes: ['-1 Lucky Ice Pop B2 145', '+1 Rare Candy A3 144']

Copycat decisions with a Copycat in hand: 274,455; the valuation and the fallback rule disagree at 125,610 of 274,455 Copycat decisions (45.8%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.4289.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.05955; in 8 cards: 0.08964.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 51/58/64/70/76%.
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
| P2 at least one Glimmora had its turn | 87.9% / 95.9% [77-95] | 77.8% / 90.4% [63-90] | 82.9% / 93.1% [70-93] |
| P2 both Glimmora had their turn | 37.0% / 69.0% [27-46] | 31.5% / 69.0% [21-45] | 34.3% / 69.0% [25-44] |
| P2 the first Glimmora placed had its turn | 84.5% / 91.2% [74-93] | 70.4% / 80.4% [54-85] | 77.5% / 85.8% [64-89] |
| P2 the second Glimmora placed had its turn | 40.4% / 68.2% [30-51] | 38.9% / 69.0% [28-52] | 39.7% / 68.6% [29-50] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 6.1% / 51.1% [2-13] | 6.5% / 54.2% [2-11] | 6.3% / 52.7% [2-12] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 25.9% / 63.5% [21-31] | 31.6% / 69.4% [25-38] | 28.7% / 66.5% [23-35] |
| P4 ready at the winning moment: Knocks out their strongest | 16.5% / 41.8% [4-32] | 13.1% / 41.5% [3-25] | 14.8% / 41.6% [3-28] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.9% / 28.2% [0-9] | 2.0% / 30.3% [0-6] | 2.4% / 29.3% [0-7] |
| P4 not ready, ready 1 turn late | 4.9% / 46.0% [0-13] | 4.5% / 49.1% [0-11] | 4.7% / 47.6% [0-12] |
| P4 not ready, ready 2 or more turns late | 1.1% / 42.2% [0-3] | 1.3% / 45.9% [0-4] | 1.2% / 44.0% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 6.1% / 47.2% [0-14] | 6.1% / 50.6% [0-16] | 6.1% / 49.0% [0-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.3% / 55.6% [9-55] | 30.4% / 58.8% [12-53] | 30.4% / 57.2% [11-54] |
| P5 plan reached in time: Knocks out their strongest | 22.5% / 63.6% [8-39] | 18.9% / 63.5% [6-33] | 20.7% / 63.5% [7-36] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.1% / 44.2% [0-9] | 2.2% / 46.8% [0-7] | 2.7% / 45.5% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 57.6% of 2859 [30-78] | 52.4% of 2501 [29-76] | 55.2% of 5360 [29-78] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.1% of 2859 [0-37] | 7.9% of 2501 [0-35] | 9.1% of 5360 [0-36] |
| P4 not ready, ready 1 turn late | 17.1% of 2859 [0-55] | 18.1% of 2501 [0-52] | 17.6% of 5360 [0-53] |
| P4 not ready, ready 2 or more turns late | 3.9% of 2859 [0-13] | 5.2% of 2501 [0-16] | 4.5% of 5360 [0-14] |
| P4 the moment came and Kingambit was never ready in the deal | 21.4% of 2859 [0-37] | 24.3% of 2501 [0-47] | 22.8% of 5360 [0-42] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: -1.4 points (-2.6 to -0.4); P2.g2: -1.6 points (-3.0 to -0.5); P3.grimer_muk: -1.4 points (-2.5 to -0.3); P4.ko: +2.7 points (+0.8 to +5.4); P5.ko: +3.2 points (+1.2 to +5.6).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.5% / 95.8% [71-96] | 87.9% / 94.6% [77-96] | 87.2% / 95.2% [78-94] |
| P2 both Glimmora had their turn | 37.9% / 65.4% [25-49] | 29.5% / 80.0% [20-42] | 33.7% / 72.7% [26-44] |
| P2 the first Glimmora placed had its turn | 82.8% / 91.1% [68-93] | 84.0% / 86.1% [73-94] | 83.4% / 88.6% [75-91] |
| P2 the second Glimmora placed had its turn | 41.6% / 65.3% [28-54] | 33.4% / 74.5% [24-48] | 37.5% / 69.9% [29-48] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 2.7% / 43.4% [1-5] | 13.7% / 77.2% [0-32] | 8.2% / 60.3% [1-17] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 25.6% / 59.6% [20-33] | 34.4% / 88.4% [18-44] | 30.0% / 74.0% [22-37] |
| P4 ready at the winning moment: Knocks out their strongest | 19.8% / 42.1% [3-39] | 5.7% / 57.8% [0-17] | 12.8% / 50.0% [3-25] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.6% / 26.9% [0-14] | 0.0% / 52.1% [0-0] | 2.3% / 39.5% [0-9] |
| P4 not ready, ready 1 turn late | 6.6% / 41.5% [0-17] | 0.0% / 75.5% [0-0] | 3.3% / 58.5% [0-10] |
| P4 not ready, ready 2 or more turns late | 1.4% / 36.3% [0-5] | 0.0% / 75.5% [0-0] | 0.7% / 55.9% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 8.9% / 43.8% [0-20] | 0.0% / 75.5% [0-0] | 4.4% / 59.7% [0-11] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.3% / 50.6% [6-58] | 18.8% / 70.9% [0-43] | 23.6% / 60.8% [8-44] |
| P5 plan reached in time: Knocks out their strongest | 27.9% / 62.8% [8-49] | 5.7% / 81.2% [0-17] | 16.8% / 72.0% [6-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.8% / 39.7% [0-15] | 0.0% / 75.5% [0-0] | 2.4% / 57.6% [0-9] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 53.9% of 3676 [17-75] | 100.0% of 569 [100-100] | 60.1% of 4245 [34-81] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 12.5% of 3676 [0-45] | 0.0% of 569 [0-0] | 10.8% of 4245 [0-38] |
| P4 not ready, ready 1 turn late | 18.0% of 3676 [0-68] | 0.0% of 569 [0-0] | 15.6% of 4245 [0-47] |
| P4 not ready, ready 2 or more turns late | 3.9% of 3676 [0-15] | 0.0% of 569 [0-0] | 3.4% of 4245 [0-11] |
| P4 the moment came and Kingambit was never ready in the deal | 24.1% of 3676 [0-43] | 0.0% of 569 [0-0] | 20.9% of 4245 [0-38] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: -1.6 points (-2.5 to -0.7); P2.g2: -1.7 points (-2.7 to -0.7); P3.grimer_muk: -1.4 points (-2.7 to -0.2); P4.ko: +2.2 points (+0.6 to +4.4); P5.ko: +2.4 points (+0.8 to +4.5).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.0% / 91.8% [88-93] | 82.3% / 83.7% [79-86] | 86.7% / 87.8% [84-90] |
| P2 both Glimmora had their turn | 39.4% / 45.2% [35-44] | 29.8% / 36.8% [25-34] | 34.6% / 41.0% [30-39] |
| P2 the first Glimmora placed had its turn | 84.7% / 84.8% [81-88] | 72.5% / 72.7% [67-78] | 78.6% / 78.8% [74-83] |
| P2 the second Glimmora placed had its turn | 45.8% / 50.0% [42-50] | 39.6% / 44.4% [36-44] | 42.7% / 47.2% [39-47] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 18.6% / 28.8% [14-23] | 17.7% / 28.5% [14-21] | 18.2% / 28.6% [14-22] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 33.1% / 41.6% [30-36] | 40.0% / 47.9% [37-43] | 36.5% / 44.7% [34-40] |
| P4 ready at the winning moment: Knocks out their strongest | 9.6% / 15.7% [5-15] | 8.6% / 15.8% [5-13] | 9.1% / 15.7% [5-14] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.4% / 6.5% [0-1] | 0.7% / 7.9% [0-2] | 0.5% / 7.2% [0-1] |
| P4 not ready, ready 1 turn late | 5.0% / 12.7% [2-8] | 4.1% / 13.2% [2-6] | 4.6% / 13.0% [2-7] |
| P4 not ready, ready 2 or more turns late | 1.0% / 8.6% [0-2] | 1.3% / 10.5% [1-2] | 1.2% / 9.6% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 7.2% / 14.8% [3-12] | 7.6% / 16.8% [4-12] | 7.4% / 15.8% [4-12] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.6% / 75.7% [58-80] | 69.2% / 76.5% [59-79] | 69.4% / 76.1% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 15.6% / 23.2% [9-23] | 14.0% / 23.1% [8-20] | 14.8% / 23.2% [9-22] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.5% / 8.1% [0-1] | 0.8% / 9.9% [0-2] | 0.6% / 9.0% [0-2] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 42.0% of 2276 [28-58] | 39.7% of 2159 [29-52] | 40.9% of 4435 [29-55] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.7% of 2276 [0-6] | 3.1% of 2159 [0-11] | 2.4% of 4435 [0-7] |
| P4 not ready, ready 1 turn late | 22.2% of 2276 [12-32] | 18.9% of 2159 [12-26] | 20.6% of 4435 [12-29] |
| P4 not ready, ready 2 or more turns late | 4.3% of 2276 [2-8] | 6.2% of 2159 [3-10] | 5.2% of 4435 [2-8] |
| P4 the moment came and Kingambit was never ready in the deal | 31.5% of 2276 [20-44] | 35.2% of 2159 [24-47] | 33.3% of 4435 [22-45] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: -2.4 points (-2.9 to -1.9); P2.g2: -2.5 points (-3.0 to -2.0); P3.pawn_promo: +2.3 points (+1.7 to +3.0); P3.grimer_muk: -3.0 points (-3.5 to -2.4); P4.ko: +1.9 points (+1.0 to +2.9); P4.never: -1.3 points (-2.1 to -0.7); P5.ko: +1.9 points (+1.0 to +2.7).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.2% [80-82, Wilson] | 51.9% [51-53, Wilson] | 66.5% [66-67, Wilson] |
| P2 both Glimmora had their turn | 25.6% [25-26, Wilson] | 7.5% [7-8, Wilson] | 16.6% [16-17, Wilson] |
| P2 the first Glimmora placed had its turn | 76.5% [76-77, Wilson] | 32.9% [32-34, Wilson] | 54.7% [54-55, Wilson] |
| P2 the second Glimmora placed had its turn | 30.3% [29-31, Wilson] | 26.6% [26-27, Wilson] | 28.4% [28-29, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 22.4% [22-23, Wilson] | 19.3% [19-20, Wilson] | 20.8% [20-21, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 55.3% [54-56, Wilson] | 53.7% [53-55, Wilson] | 54.5% [54-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 21.4% [21-22, Wilson] | 7.9% [7-8, Wilson] | 14.7% [14-15, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 21.4% [21-22, Wilson] | 7.9% [7-8, Wilson] | 14.7% [14-15, Wilson] |
| P4 not ready, ready 1 turn late | 1.8% [2-2, Wilson] | 0.7% [1-1, Wilson] | 1.2% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 19.7% [19-20, Wilson] | 14.9% [14-16, Wilson] | 17.3% [17-18, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 57.1% [56-58, Wilson] | 76.5% [76-77, Wilson] | 66.8% [66-67, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 23.2% [22-24, Wilson] | 8.6% [8-9, Wilson] | 15.9% [15-16, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 23.2% [22-24, Wilson] | 8.6% [8-9, Wilson] | 15.9% [15-16, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 49.9% of 4289 [48-51, Wilson] | 33.6% of 2346 [32-36, Wilson] | 44.2% of 6635 [43-45, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 49.9% of 4289 [48-51, Wilson] | 33.6% of 2346 [32-36, Wilson] | 44.2% of 6635 [43-45, Wilson] |
| P4 not ready, ready 1 turn late | 4.2% of 4289 [4-5, Wilson] | 2.8% of 2346 [2-4, Wilson] | 3.7% of 6635 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4289 [0-0, Wilson] | 0.0% of 2346 [0-0, Wilson] | 0.0% of 6635 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 45.8% of 4289 [44-47, Wilson] | 63.6% of 2346 [62-65, Wilson] | 52.1% of 6635 [51-53, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.both: -1.7 points (-1.9 to -1.5); P2.g2: -2.3 points (-2.5 to -2.1); P3.grimer_muk: -1.5 points (-1.6 to -1.3); P4.ko: +3.9 points (+3.6 to +4.2); P4.win: +3.9 points (+3.6 to +4.2); P4.never: -3.9 points (-4.2 to -3.6); P5.ko: +3.8 points (+3.5 to +4.1); P5.win: +3.8 points (+3.5 to +4.1).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 90.0% [89-91, Wilson] | 81.0% [80-82, Wilson] | 85.5% [85-86, Wilson] |
| P2 both Glimmora had their turn | 35.4% [34-36, Wilson] | 25.4% [25-26, Wilson] | 30.4% [30-31, Wilson] |
| P2 the first Glimmora placed had its turn | 87.0% [86-88, Wilson] | 76.9% [76-78, Wilson] | 82.0% [81-82, Wilson] |
| P2 the second Glimmora placed had its turn | 38.3% [37-39, Wilson] | 29.4% [29-30, Wilson] | 33.9% [33-35, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 26.9% [26-28, Wilson] | 23.5% [23-24, Wilson] | 25.2% [25-26, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 51.8% [51-53, Wilson] | 56.2% [55-57, Wilson] | 54.0% [53-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 33.9% [33-35, Wilson] | 21.8% [21-23, Wilson] | 27.9% [27-28, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 1.9% [2-2, Wilson] | 1.9% [2-2, Wilson] | 1.9% [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 18.9% [18-20, Wilson] | 19.7% [19-21, Wilson] | 19.3% [19-20, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 45.3% [44-46, Wilson] | 56.5% [56-57, Wilson] | 50.9% [50-52, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 35.8% [35-37, Wilson] | 23.7% [23-25, Wilson] | 29.8% [29-30, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 62.0% of 5467 [61-63, Wilson] | 50.2% of 4347 [49-52, Wilson] | 56.8% of 9814 [56-58, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 5467 [0-0, Wilson] | 0.0% of 4347 [0-0, Wilson] | 0.0% of 9814 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 3.4% of 5467 [3-4, Wilson] | 4.4% of 4347 [4-5, Wilson] | 3.9% of 9814 [4-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5467 [0-0, Wilson] | 0.0% of 4347 [0-0, Wilson] | 0.0% of 9814 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 34.6% of 5467 [33-36, Wilson] | 45.4% of 4347 [44-47, Wilson] | 39.4% of 9814 [38-40, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.both: -3.6 points (-3.9 to -3.3); P2.g2: -4.0 points (-4.3 to -3.7); P3.pawn_promo: +1.3 points (+1.0 to +1.5); P3.grimer_muk: -2.7 points (-3.0 to -2.5); P4.ko: +6.1 points (+5.8 to +6.4); P4.never: -5.6 points (-5.9 to -5.2); P5.ko: +5.6 points (+5.3 to +5.9).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.4% [95-96, Wilson] | 89.5% [89-90, Wilson] | 92.4% [92-93, Wilson] |
| P2 both Glimmora had their turn | 69.5% [69-70, Wilson] | 53.1% [52-54, Wilson] | 61.3% [61-62, Wilson] |
| P2 the first Glimmora placed had its turn | 90.0% [89-91, Wilson] | 81.3% [81-82, Wilson] | 85.6% [85-86, Wilson] |
| P2 the second Glimmora placed had its turn | 74.9% [74-76, Wilson] | 61.3% [60-62, Wilson] | 68.1% [67-69, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 6.0% [6-6, Wilson] | 9.0% [8-10, Wilson] | 7.5% [7-8, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 26.5% [26-27, Wilson] | 35.7% [35-37, Wilson] | 31.1% [30-32, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 51.4% [50-52, Wilson] | 43.2% [42-44, Wilson] | 47.3% [47-48, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 51.4% [50-52, Wilson] | 43.2% [42-44, Wilson] | 47.3% [47-48, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 2.2% [2-3, Wilson] | 1.1% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 13.1% [12-14, Wilson] | 11.6% [11-12, Wilson] | 12.3% [12-13, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 35.5% [35-36, Wilson] | 43.0% [42-44, Wilson] | 39.3% [39-40, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 51.4% [50-52, Wilson] | 45.4% [44-46, Wilson] | 48.4% [48-49, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 51.4% [50-52, Wilson] | 45.4% [44-46, Wilson] | 48.4% [48-49, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 79.7% of 6446 [79-81, Wilson] | 75.8% of 5700 [75-77, Wilson] | 77.9% of 12146 [77-79, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 79.7% of 6446 [79-81, Wilson] | 75.8% of 5700 [75-77, Wilson] | 77.9% of 12146 [77-79, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 6446 [0-0, Wilson] | 3.9% of 5700 [3-4, Wilson] | 1.8% of 12146 [2-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 6446 [0-0, Wilson] | 0.0% of 5700 [0-0, Wilson] | 0.0% of 12146 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 20.3% of 6446 [19-21, Wilson] | 20.4% of 5700 [19-21, Wilson] | 20.3% of 12146 [20-21, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P3.grimer_muk: -4.7 points (-5.0 to -4.4); P4.ko: +2.8 points (+2.5 to +3.0); P4.win: +2.8 points (+2.5 to +3.0); P4.never: -1.6 points (-1.9 to -1.4); P5.ko: +1.8 points (+1.6 to +2.0); P5.win: +1.8 points (+1.6 to +2.0).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 81.4% [81-82, Wilson] | 52.0% [51-53, Wilson] | 66.7% [66-67, Wilson] |
| P2 both Glimmora had their turn | 25.9% [25-27, Wilson] | 7.5% [7-8, Wilson] | 16.7% [16-17, Wilson] |
| P2 the first Glimmora placed had its turn | 76.5% [76-77, Wilson] | 32.9% [32-34, Wilson] | 54.7% [54-55, Wilson] |
| P2 the second Glimmora placed had its turn | 30.8% [30-32, Wilson] | 26.7% [26-28, Wilson] | 28.8% [28-29, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 25.7% [25-27, Wilson] | 20.2% [19-21, Wilson] | 22.9% [22-24, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 55.3% [54-56, Wilson] | 53.7% [53-55, Wilson] | 54.5% [54-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 3.6% [3-4, Wilson] | 1.1% [1-1, Wilson] | 2.4% [2-3, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.6% [3-4, Wilson] | 1.1% [1-1, Wilson] | 2.4% [2-3, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 4.4% [4-5, Wilson] | 1.5% [1-2, Wilson] | 3.0% [3-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 91.9% [91-92, Wilson] | 97.4% [97-98, Wilson] | 94.7% [94-95, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 3.6% [3-4, Wilson] | 1.1% [1-1, Wilson] | 2.4% [2-3, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.6% [3-4, Wilson] | 1.1% [1-1, Wilson] | 2.4% [2-3, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 45.1% of 809 [42-49, Wilson] | 42.3% of 260 [36-48, Wilson] | 44.4% of 1069 [41-47, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 45.1% of 809 [42-49, Wilson] | 42.3% of 260 [36-48, Wilson] | 44.4% of 1069 [41-47, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 809 [0-0, Wilson] | 0.0% of 260 [0-1, Wilson] | 0.0% of 1069 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 809 [0-0, Wilson] | 0.0% of 260 [0-1, Wilson] | 0.0% of 1069 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 54.9% of 809 [51-58, Wilson] | 57.7% of 260 [52-64, Wilson] | 55.6% of 1069 [53-59, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.both: -1.7 points (-1.9 to -1.5); P2.g2: -2.2 points (-2.4 to -2.0); P3.pawn_promo: +1.1 points (+0.9 to +1.3); P3.grimer_muk: -1.5 points (-1.6 to -1.3).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 95.5% [95-96, Wilson] | 89.5% [89-90, Wilson] | 92.5% [92-93, Wilson] |
| P2 both Glimmora had their turn | 71.4% [70-72, Wilson] | 56.0% [55-57, Wilson] | 63.7% [63-64, Wilson] |
| P2 the first Glimmora placed had its turn | 90.0% [89-91, Wilson] | 81.3% [81-82, Wilson] | 85.6% [85-86, Wilson] |
| P2 the second Glimmora placed had its turn | 76.8% [76-78, Wilson] | 64.2% [63-65, Wilson] | 70.5% [70-71, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 42.7% [42-44, Wilson] | 35.6% [35-37, Wilson] | 39.1% [38-40, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 40.6% [40-42, Wilson] | 46.2% [45-47, Wilson] | 43.4% [43-44, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 5.0% [5-5, Wilson] | 6.3% [6-7, Wilson] | 5.7% [5-6, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 5.0% [5-5, Wilson] | 6.3% [6-7, Wilson] | 5.7% [5-6, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 14.4% [14-15, Wilson] | 11.0% [10-12, Wilson] | 12.7% [12-13, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 80.5% [80-81, Wilson] | 82.6% [82-83, Wilson] | 81.6% [81-82, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 5.0% [5-5, Wilson] | 6.4% [6-7, Wilson] | 5.7% [5-6, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.0% [5-5, Wilson] | 6.4% [6-7, Wilson] | 5.7% [5-6, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 25.9% of 1949 [24-28, Wilson] | 36.4% of 1740 [34-39, Wilson] | 30.9% of 3689 [29-32, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 25.9% of 1949 [24-28, Wilson] | 36.4% of 1740 [34-39, Wilson] | 30.9% of 3689 [29-32, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1949 [0-0, Wilson] | 0.2% of 1740 [0-1, Wilson] | 0.1% of 3689 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1949 [0-0, Wilson] | 0.0% of 1740 [0-0, Wilson] | 0.0% of 3689 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 74.1% of 1949 [72-76, Wilson] | 63.4% of 1740 [61-66, Wilson] | 69.0% of 3689 [68-71, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P3.pawn_promo: +4.2 points (+3.9 to +4.5); P3.grimer_muk: -3.6 points (-3.9 to -3.3); P4.never: +1.0 points (+0.9 to +1.2).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 29.2% (28.8-29.6) | 28.8% (28.4-29.2) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 55.9% (55.4-56.3) | 55.5% (55.1-56.0) | 55.7% (55.4-56.0) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 67.6% (67.2-68.0) | 67.4% (67.0-67.8) | 67.5% (67.2-67.8) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 74.1% (73.7-74.4) | 74.1% (73.7-74.5) | 74.1% (73.8-74.3) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 78.2% (77.8-78.6) | 78.3% (78.0-78.7) | 78.3% (78.0-78.5) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 80.6% (80.2-80.9) | 80.6% (80.3-81.0) | 80.6% (80.3-80.8) |
| K2 Kingambit in play, own turn 2 | 18.0% (17.7-18.4) | 17.9% (17.6-18.3) | 18.0% (17.7-18.2) |
| K2 Kingambit in play, own turn 3 | 32.7% (32.3-33.1) | 32.6% (32.1-33.0) | 32.6% (32.3-32.9) |
| K2 Kingambit in play, own turn 4 | 47.3% (46.9-47.7) | 47.5% (47.0-47.9) | 47.4% (47.1-47.7) |
| K2 Kingambit in play, own turn 5 | 61.1% (60.7-61.5) | 61.1% (60.6-61.5) | 61.1% (60.8-61.4) |
| K2 Kingambit in play, own turn 6 | 71.5% (71.1-71.9) | 71.4% (71.0-71.8) | 71.4% (71.1-71.7) |
| K6 Muk and Regigigas both in play, own turn 3 | 22.1% (21.8-22.5) | 22.3% (21.9-22.6) | 22.2% (21.9-22.5) |
| K6 Muk and Regigigas both in play, own turn 4 | 30.4% (30.0-30.8) | 30.5% (30.1-30.9) | 30.5% (30.2-30.7) |
| K6 Muk and Regigigas both in play, own turn 5 | 37.0% (36.6-37.4) | 37.0% (36.6-37.5) | 37.0% (36.7-37.3) |
| G3 Pawniard in play, own turn 1 | 55.9% (55.4-56.3) | 55.5% (55.1-56.0) | 55.7% (55.4-56.0) |
| G3 Pawniard in play, own turn 2 | 49.5% (49.1-50.0) | 49.5% (49.1-49.9) | 49.5% (49.2-49.8) |
| G3 Pawniard in play, own turn 3 | 41.4% (40.9-41.8) | 41.5% (41.1-42.0) | 41.5% (41.1-41.8) |
| G3 Pawniard in play, own turn 4 | 30.9% (30.5-31.3) | 30.9% (30.5-31.3) | 30.9% (30.6-31.2) |
| G3 Pawniard in play, own turn 5 | 19.5% (19.1-19.8) | 19.5% (19.2-19.9) | 19.5% (19.3-19.8) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 18.0% (17.7-18.4) | 17.9% (17.6-18.3) | 18.0% (17.7-18.2) |
| G3 Kingambit in play, own turn 3 | 32.7% (32.3-33.1) | 32.6% (32.1-33.0) | 32.6% (32.3-32.9) |
| G3 Kingambit in play, own turn 4 | 47.3% (46.9-47.7) | 47.5% (47.0-47.9) | 47.4% (47.1-47.7) |
| G3 Kingambit in play, own turn 5 | 61.1% (60.7-61.5) | 61.1% (60.6-61.5) | 61.1% (60.8-61.4) |
| G3 Alolan Grimer in play, own turn 1 | 54.5% (54.1-55.0) | 54.6% (54.2-55.1) | 54.6% (54.3-54.9) |
| G3 Alolan Grimer in play, own turn 2 | 46.2% (45.7-46.6) | 46.5% (46.1-47.0) | 46.3% (46.0-46.7) |
| G3 Alolan Grimer in play, own turn 3 | 39.9% (39.5-40.3) | 39.9% (39.5-40.4) | 39.9% (39.6-40.2) |
| G3 Alolan Grimer in play, own turn 4 | 32.9% (32.5-33.3) | 33.2% (32.8-33.6) | 33.0% (32.8-33.3) |
| G3 Alolan Grimer in play, own turn 5 | 26.6% (26.2-27.0) | 26.9% (26.5-27.3) | 26.8% (26.5-27.0) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 18.8% (18.5-19.2) | 18.9% (18.5-19.2) | 18.8% (18.6-19.1) |
| G3 Alolan Muk in play, own turn 3 | 31.0% (30.6-31.5) | 31.4% (31.0-31.8) | 31.2% (30.9-31.5) |
| G3 Alolan Muk in play, own turn 4 | 41.2% (40.8-41.7) | 41.4% (41.0-41.8) | 41.3% (41.0-41.6) |
| G3 Alolan Muk in play, own turn 5 | 49.3% (48.9-49.8) | 49.3% (48.9-49.7) | 49.3% (49.0-49.6) |
| G3 Glimmet in play, own turn 1 | 82.0% (81.6-82.3) | 82.3% (82.0-82.6) | 82.1% (81.9-82.4) |
| G3 Glimmet in play, own turn 2 | 52.9% (52.5-53.4) | 52.6% (52.1-53.0) | 52.8% (52.4-53.1) |
| G3 Glimmet in play, own turn 3 | 42.2% (41.8-42.7) | 42.0% (41.5-42.4) | 42.1% (41.8-42.4) |
| G3 Glimmet in play, own turn 4 | 30.8% (30.4-31.2) | 30.8% (30.4-31.2) | 30.8% (30.5-31.1) |
| G3 Glimmet in play, own turn 5 | 19.9% (19.5-20.2) | 19.6% (19.2-19.9) | 19.7% (19.5-20.0) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 62.9% (62.5-63.3) | 63.1% (62.7-63.6) | 63.0% (62.7-63.3) |
| G3 Glimmora in play, own turn 3 | 79.7% (79.3-80.0) | 79.9% (79.6-80.3) | 79.8% (79.6-80.1) |
| G3 Glimmora in play, own turn 4 | 89.6% (89.3-89.8) | 89.6% (89.3-89.9) | 89.6% (89.4-89.8) |
| G3 Glimmora in play, own turn 5 | 95.2% (95.0-95.4) | 95.3% (95.1-95.5) | 95.3% (95.1-95.4) |
| G3 Regigigas in play, own turn 1 | 55.3% (54.9-55.7) | 55.1% (54.7-55.6) | 55.2% (54.9-55.5) |
| G3 Regigigas in play, own turn 2 | 67.6% (67.2-68.0) | 67.1% (66.6-67.5) | 67.3% (67.0-67.6) |
| G3 Regigigas in play, own turn 3 | 74.5% (74.1-74.9) | 74.2% (73.9-74.6) | 74.4% (74.1-74.6) |
| G3 Regigigas in play, own turn 4 | 78.3% (77.9-78.7) | 78.2% (77.8-78.6) | 78.2% (78.0-78.5) |
| G3 Regigigas in play, own turn 5 | 80.4% (80.1-80.7) | 80.3% (79.9-80.6) | 80.3% (80.1-80.6) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 78.2% (77.8-78.5) | 78.2% (77.9-78.6) | 78.2% (77.9-78.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 91.4% (91.2-91.7) | 91.5% (91.2-91.7) | 91.4% (91.3-91.6) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 96.9% (96.7-97.0) | 96.8% (96.6-96.9) | 96.8% (96.7-96.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 99.0% (98.9-99.1) | 99.0% (98.9-99.1) | 99.0% (98.9-99.0) |
| G4.s2 a Stage 2 in play, own turn 2 | 18.0% (17.7-18.4) | 17.9% (17.6-18.3) | 18.0% (17.7-18.2) |
| G4.s2 a Stage 2 in play, own turn 3 | 32.7% (32.3-33.1) | 32.6% (32.1-33.0) | 32.6% (32.3-32.9) |
| G4.s2 a Stage 2 in play, own turn 4 | 47.3% (46.9-47.7) | 47.5% (47.0-47.9) | 47.4% (47.1-47.7) |
| G4.s2 a Stage 2 in play, own turn 5 | 61.1% (60.7-61.5) | 61.1% (60.6-61.5) | 61.1% (60.8-61.4) |
| G5.any3 an empty own turn among turns 1-3 | 22.4% (22.0-22.7) | 21.7% (21.4-22.1) | 22.0% (21.8-22.3) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 17.9% (17.6-18.3) | 9.0% (8.8-9.1) |
| G6 Kingambit with [DD] attached, own turn 3 | 27.7% (27.3-28.1) | 32.6% (32.1-33.0) | 30.1% (29.8-30.4) |
| G6 Kingambit with [DD] attached, own turn 4 | 47.3% (46.9-47.7) | 47.5% (47.0-47.9) | 47.4% (47.1-47.7) |
| G6 Kingambit with [DD] attached, own turn 5 | 61.1% (60.6-61.5) | 61.1% (60.6-61.5) | 61.1% (60.8-61.4) |
| G5 mean empty own turns in turns 1-5 | 0.750 | 0.744 | 0.747 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.6% / 12.0% [2-5] | 1.8% / 6.0% [1-2] |
| K3.by3 | 5.4% / 14.1% [4-7] | 4.4% / 12.7% [3-6] | 4.9% / 13.4% [3-6] |
| K3.by4 | 6.2% / 14.9% [4-8] | 7.2% / 15.6% [5-9] | 6.7% / 15.2% [5-8] |
| K3.by5 | 9.3% / 17.9% [7-12] | 8.0% / 23.3% [6-10] | 8.7% / 20.6% [6-11] |
| K3.by6 | 9.8% / 25.9% [7-13] | 14.4% / 37.3% [8-24] | 12.1% / 31.6% [8-17] |
| K3.by7 | 18.2% / 42.0% [9-30] | 16.4% / 60.3% [9-27] | 17.3% / 51.2% [9-28] |
| K3.by8 | 21.4% / 66.7% [10-35] | 16.4% / 63.8% [9-27] | 18.9% / 65.2% [10-31] |
| K3.never | 33.3% / 78.6% [15-56] | 36.2% / 83.6% [17-58] | 34.8% / 81.1% [15-57] |
| K3.k0 | 6.5% / 51.8% [4-9] | 4.8% / 52.1% [3-7] | 5.6% / 52.0% [4-8] |
| K3.k1 | 0.0% / 45.3% [0-0] | 0.0% / 47.4% [0-0] | 0.0% / 46.3% [0-0] |
| K3.k2 | 9.2% / 54.5% [1-20] | 8.2% / 55.6% [2-17] | 8.7% / 55.0% [2-19] |
| K3.k3p | 5.8% / 51.1% [0-14] | 3.5% / 50.8% [0-8] | 4.6% / 50.9% [0-11] |
| K4 | 14.9% / 63.8% [3-28] | 11.7% / 61.6% [3-22] | 13.3% / 62.7% [3-25] |
| K5 | 4.9% / 61.1% [3-6] | 7.3% / 58.9% [5-10] | 6.1% / 60.0% [4-8] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.7 points (+1.1 to +2.3); K3.by4: +2.1 points (+1.6 to +2.6); K3.by5: +2.6 points (+1.9 to +3.3); K3.by6: +3.3 points (+2.2 to +4.6); K3.by7: +4.0 points (+2.3 to +6.3); K3.by8: +4.2 points (+2.4 to +6.5); K3.never: -2.7 points (-5.3 to -0.7); K3.k0: +1.7 points (+1.1 to +2.2); K3.k2: +1.9 points (+0.3 to +4.0); K4: +2.5 points (+0.6 to +4.9); K5: -2.0 points (-2.4 to -1.6).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 4.9% [4-6] | 2.5% [0-4] |
| K3.by3 | 5.0% / 16.3% [3-7] | 6.1% [4-8] | 5.5% / 11.2% [4-7] |
| K3.by4 | 5.7% / 17.0% [3-9] | 7.8% [6-9] | 6.8% / 12.4% [5-8] |
| K3.by5 | 8.9% / 20.2% [6-12] | 8.9% / 35.5% [8-10] | 8.9% / 27.9% [7-11] |
| K3.by6 | 9.4% / 20.7% [6-13] | 9.6% / 36.2% [8-12] | 9.5% / 28.4% [8-11] |
| K3.by7 | 21.2% / 43.0% [9-38] | 18.0% / 75.0% [8-37] | 19.6% / 59.0% [9-32] |
| K3.by8 | 21.2% / 62.0% [9-38] | 18.0% / 83.5% [8-37] | 19.6% / 72.7% [9-32] |
| K3.never | 38.0% / 78.8% [13-66] | 16.5% / 82.0% [0-37] | 27.3% / 80.4% [13-47] |
| K3.k0 | 6.0% / 46.7% [3-9] | 6.5% / 72.0% [4-9] | 6.2% / 59.4% [4-8] |
| K3.k1 | 0.0% / 40.8% [0-0] | 0.0% / 65.5% [0-0] | 0.0% / 53.1% [0-0] |
| K3.k2 | 11.2% / 52.0% [1-27] | 3.1% / 68.5% [0-5] | 7.1% / 60.3% [2-16] |
| K3.k3p | 4.0% / 44.8% [0-12] | 8.4% / 73.9% [0-26] | 6.2% / 59.4% [0-14] |
| K4 | 15.2% / 58.8% [1-32] | 11.5% / 82.3% [0-31] | 13.4% / 70.6% [3-27] |
| K5 | 5.2% / 53.3% [3-7] | 6.5% / 82.6% [4-8] | 5.8% / 68.0% [4-7] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.9 points (+1.3 to +2.4); K3.by4: +2.0 points (+1.4 to +2.5); K3.by5: +2.5 points (+2.0 to +3.2); K3.by6: +2.6 points (+2.0 to +3.3); K3.by7: +4.1 points (+2.5 to +6.1); K3.by8: +4.1 points (+2.5 to +6.1); K3.never: -1.9 points (-4.0 to -0.5); K3.k0: +1.8 points (+1.3 to +2.3); K3.k2: +1.5 points (+0.4 to +3.2); K4: +2.3 points (+0.7 to +4.2); K5: -2.2 points (-2.7 to -1.7).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 4.0% [3-5] | 2.0% [2-2] |
| K3.by3 | 5.8% [5-7] | 4.7% [4-5] | 5.2% [5-6] |
| K3.by4 | 6.6% [6-7] | 6.6% [6-7] | 6.6% [6-7] |
| K3.by5 | 8.5% [7-10] | 9.6% [8-11] | 9.1% [8-10] |
| K3.by6 | 11.2% [10-13] | 12.6% / 16.3% [10-15] | 11.9% / 13.8% [10-14] |
| K3.by7 | 14.2% / 18.4% [12-17] | 14.6% / 23.6% [12-18] | 14.4% / 21.0% [12-17] |
| K3.by8 | 16.4% / 26.3% [13-20] | 15.7% / 26.0% [13-19] | 16.1% / 26.1% [13-19] |
| K3.never | 73.7% / 83.6% [66-80] | 74.0% / 84.3% [67-80] | 73.9% / 84.0% [66-80] |
| K3.k0 | 6.9% / 16.8% [6-8] | 5.1% / 15.3% [4-6] | 6.0% / 16.1% [5-7] |
| K3.k1 | 0.0% / 9.9% [0-0] | 0.0% / 10.2% [0-0] | 0.0% / 10.1% [0-0] |
| K3.k2 | 3.7% / 13.6% [2-5] | 5.0% / 15.3% [4-7] | 4.4% / 14.4% [3-6] |
| K3.k3p | 5.8% / 15.7% [3-9] | 5.7% / 15.9% [3-9] | 5.7% / 15.8% [3-9] |
| K4 | 9.4% / 20.4% [6-13] | 10.7% / 21.7% [8-14] | 10.1% / 21.1% [7-13] |
| K5 | 5.7% / 19.6% [5-6] | 8.5% / 20.4% [8-10] | 7.1% / 20.0% [6-8] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.8 points (+1.5 to +2.0); K3.by4: +2.0 points (+1.7 to +2.3); K3.by5: +2.6 points (+2.3 to +2.9); K3.by6: +3.2 points (+2.7 to +3.7); K3.by7: +3.6 points (+3.0 to +4.2); K3.by8: +3.7 points (+3.1 to +4.4); K3.never: -3.2 points (-3.9 to -2.6); K3.k0: +1.8 points (+1.5 to +2.1); K4: +1.9 points (+1.3 to +2.5); K5: -2.5 points (-2.8 to -2.2).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 3.6% [3-4, Wilson] | 1.8% [2-2, Wilson] |
| K3.by4 | 3.4% [3-4, Wilson] | 8.6% [8-9, Wilson] | 6.0% [6-6, Wilson] |
| K3.by5 | 17.7% [17-18, Wilson] | 9.7% [9-10, Wilson] | 13.7% [13-14, Wilson] |
| K3.by6 | 21.1% [20-22, Wilson] | 9.7% [9-10, Wilson] | 15.4% [15-16, Wilson] |
| K3.by7 | 21.1% [20-22, Wilson] | 9.7% [9-10, Wilson] | 15.4% [15-16, Wilson] |
| K3.by8 | 21.1% [20-22, Wilson] | 9.7% [9-10, Wilson] | 15.4% [15-16, Wilson] |
| K3.never | 78.9% [78-80, Wilson] | 90.3% [90-91, Wilson] | 84.6% [84-85, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.4% [3-4, Wilson] | 3.6% [3-4, Wilson] | 3.5% [3-4, Wilson] |
| K3.k3p | 17.7% [17-18, Wilson] | 6.0% [6-7, Wilson] | 11.9% [11-12, Wilson] |
| K4 | 21.1% [20-22, Wilson] | 9.7% [9-10, Wilson] | 15.4% [15-16, Wilson] |
| K5 | 13.4% [13-14, Wilson] | 21.2% [20-22, Wilson] | 17.3% [17-18, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: +2.0 points (+1.8 to +2.2); K3.by5: +4.2 points (+3.9 to +4.5); K3.by6: +4.2 points (+3.9 to +4.5); K3.by7: +4.2 points (+3.9 to +4.5); K3.by8: +4.2 points (+3.9 to +4.5); K3.never: -4.2 points (-4.5 to -3.9); K3.k2: +1.1 points (+1.0 to +1.3); K3.k3p: +3.1 points (+2.8 to +3.3); K4: +4.2 points (+3.9 to +4.5); K5: -4.4 points (-4.7 to -4.1).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 4.9% [4-5, Wilson] | 2.4% [2-3, Wilson] |
| K3.by3 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.by4 | 6.9% [6-7, Wilson] | 8.5% [8-9, Wilson] | 7.7% [7-8, Wilson] |
| K3.by5 | 9.1% [9-10, Wilson] | 23.1% [22-24, Wilson] | 16.1% [16-17, Wilson] |
| K3.by6 | 33.5% [33-34, Wilson] | 26.8% [26-28, Wilson] | 30.2% [30-31, Wilson] |
| K3.by7 | 38.1% [37-39, Wilson] | 26.8% [26-28, Wilson] | 32.5% [32-33, Wilson] |
| K3.by8 | 38.1% [37-39, Wilson] | 26.8% [26-28, Wilson] | 32.5% [32-33, Wilson] |
| K3.never | 61.9% [61-63, Wilson] | 73.2% [72-74, Wilson] | 67.5% [67-68, Wilson] |
| K3.k0 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.2% [2-2, Wilson] | 3.6% [3-4, Wilson] | 2.9% [3-3, Wilson] |
| K3.k3p | 29.0% [28-30, Wilson] | 18.3% [18-19, Wilson] | 23.7% [23-24, Wilson] |
| K4 | 31.2% [30-32, Wilson] | 22.0% [21-23, Wilson] | 26.6% [26-27, Wilson] |
| K5 | 8.6% [8-9, Wilson] | 13.2% [13-14, Wilson] | 10.9% [10-11, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: +2.2 points (+2.0 to +2.4); K3.by4: +2.6 points (+2.4 to +2.8); K3.by5: +5.1 points (+4.7 to +5.4); K3.by6: +8.0 points (+7.6 to +8.4); K3.by7: +7.8 points (+7.4 to +8.2); K3.by8: +7.8 points (+7.4 to +8.2); K3.never: -7.8 points (-8.2 to -7.4); K3.k0: +2.2 points (+2.0 to +2.4); K3.k3p: +4.9 points (+4.6 to +5.2); K4: +5.6 points (+5.3 to +5.9); K5: -5.4 points (-5.7 to -5.0).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 4.9% [4-5, Wilson] | 2.4% [2-3, Wilson] |
| K3.by3 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.by4 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.by5 | 6.9% [6-7, Wilson] | 11.5% [11-12, Wilson] | 9.2% [9-10, Wilson] |
| K3.by6 | 11.5% [11-12, Wilson] | 11.8% [11-12, Wilson] | 11.6% [11-12, Wilson] |
| K3.by7 | 11.6% [11-12, Wilson] | 49.8% [49-51, Wilson] | 30.7% [30-31, Wilson] |
| K3.by8 | 59.5% [59-60, Wilson] | 49.9% [49-51, Wilson] | 54.7% [54-55, Wilson] |
| K3.never | 40.5% [40-41, Wilson] | 50.1% [49-51, Wilson] | 45.3% [45-46, Wilson] |
| K3.k0 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.7% [4-5, Wilson] | 6.9% [6-7, Wilson] | 5.8% [5-6, Wilson] |
| K3.k3p | 47.8% [47-49, Wilson] | 38.1% [37-39, Wilson] | 43.0% [42-44, Wilson] |
| K4 | 52.6% [52-54, Wilson] | 45.0% [44-46, Wilson] | 48.8% [48-49, Wilson] |
| K5 | 6.3% [6-7, Wilson] | 8.4% [8-9, Wilson] | 7.3% [7-8, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: +2.2 points (+2.0 to +2.4); K3.by4: +2.2 points (+2.0 to +2.4); K3.by5: +3.0 points (+2.8 to +3.2); K3.by6: +3.5 points (+3.2 to +3.8); K3.by7: +6.3 points (+6.0 to +6.6); K3.by8: +8.6 points (+8.2 to +9.0); K3.never: -8.6 points (-9.0 to -8.2); K3.k0: +2.2 points (+2.0 to +2.4); K3.k2: +1.3 points (+1.1 to +1.5); K3.k3p: +5.1 points (+4.8 to +5.4); K4: +6.4 points (+6.1 to +6.8); K5: -2.6 points (-2.8 to -2.4).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 3.6% [3-4, Wilson] | 1.8% [2-2, Wilson] |
| K3.by4 | 3.4% [3-4, Wilson] | 8.4% [8-9, Wilson] | 5.9% [6-6, Wilson] |
| K3.by5 | 16.4% [16-17, Wilson] | 9.5% [9-10, Wilson] | 12.9% [12-13, Wilson] |
| K3.by6 | 20.0% [19-21, Wilson] | 9.5% [9-10, Wilson] | 14.8% [14-15, Wilson] |
| K3.by7 | 20.0% [19-21, Wilson] | 9.5% [9-10, Wilson] | 14.8% [14-15, Wilson] |
| K3.by8 | 20.0% [19-21, Wilson] | 9.5% [9-10, Wilson] | 14.8% [14-15, Wilson] |
| K3.never | 80.0% [79-81, Wilson] | 90.5% [90-91, Wilson] | 85.2% [85-86, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.4% [3-4, Wilson] | 3.6% [3-4, Wilson] | 3.5% [3-4, Wilson] |
| K3.k3p | 16.6% [16-17, Wilson] | 5.8% [5-6, Wilson] | 11.2% [11-12, Wilson] |
| K4 | 20.0% [19-21, Wilson] | 9.5% [9-10, Wilson] | 14.8% [14-15, Wilson] |
| K5 | 13.4% [13-14, Wilson] | 21.2% [20-22, Wilson] | 17.3% [17-18, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: +2.0 points (+1.8 to +2.2); K3.by5: +4.0 points (+3.7 to +4.2); K3.by6: +4.0 points (+3.7 to +4.3); K3.by7: +4.0 points (+3.7 to +4.3); K3.by8: +4.0 points (+3.7 to +4.3); K3.never: -4.0 points (-4.3 to -3.7); K3.k2: +1.1 points (+1.0 to +1.3); K3.k3p: +2.8 points (+2.6 to +3.1); K4: +4.0 points (+3.7 to +4.3); K5: -4.4 points (-4.7 to -4.1).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 4.9% [4-5, Wilson] | 2.4% [2-3, Wilson] |
| K3.by3 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.by4 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.by5 | 6.9% [6-7, Wilson] | 11.5% [11-12, Wilson] | 9.2% [9-10, Wilson] |
| K3.by6 | 11.5% [11-12, Wilson] | 11.8% [11-12, Wilson] | 11.6% [11-12, Wilson] |
| K3.by7 | 11.6% [11-12, Wilson] | 39.4% [38-40, Wilson] | 25.5% [25-26, Wilson] |
| K3.by8 | 49.2% [48-50, Wilson] | 39.5% [39-40, Wilson] | 44.3% [44-45, Wilson] |
| K3.by9 | 49.2% [48-50, Wilson] | 45.8% [45-47, Wilson] | 47.5% [47-48, Wilson] |
| K3.by10 | 54.3% [53-55, Wilson] | 45.9% [45-47, Wilson] | 50.1% [49-51, Wilson] |
| K3.never | 45.7% [45-47, Wilson] | 54.1% [53-55, Wilson] | 49.9% [49-51, Wilson] |
| K3.k0 | 6.9% [6-7, Wilson] | 4.9% [4-5, Wilson] | 5.9% [6-6, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.7% [4-5, Wilson] | 6.9% [6-7, Wilson] | 5.8% [5-6, Wilson] |
| K3.k3p | 42.6% [42-44, Wilson] | 34.1% [33-35, Wilson] | 38.4% [38-39, Wilson] |
| K4 | 47.4% [46-48, Wilson] | 41.0% [40-42, Wilson] | 44.2% [43-45, Wilson] |
| K5 | 6.3% [6-7, Wilson] | 8.4% [8-9, Wilson] | 7.4% [7-8, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: +2.2 points (+2.0 to +2.4); K3.by4: +2.2 points (+2.0 to +2.4); K3.by5: +3.0 points (+2.8 to +3.2); K3.by6: +3.5 points (+3.2 to +3.8); K3.by7: +5.4 points (+5.1 to +5.7); K3.by8: +7.3 points (+6.9 to +7.6); K3.by9: +6.8 points (+6.4 to +7.2); K3.by10: +6.3 points (+5.9 to +6.6); K3.never: -6.3 points (-6.6 to -5.9); K3.k0: +2.2 points (+2.0 to +2.4); K3.k2: +1.3 points (+1.1 to +1.5); K3.k3p: +2.8 points (+2.5 to +3.1); K4: +4.1 points (+3.8 to +4.4); K5: -2.7 points (-3.0 to -2.5).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K2 Kingambit in play, own turn 2 | +7.3 (+7.1 to +7.5) FLAG | +7.2 (+6.9 to +7.4) FLAG | +7.2 (+7.1 to +7.4) FLAG |
| K2 Kingambit in play, own turn 3 | +11.6 (+11.4 to +11.9) FLAG | +11.4 (+11.2 to +11.7) FLAG | +11.5 (+11.3 to +11.7) FLAG |
| K2 Kingambit in play, own turn 4 | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.1 to +14.5) FLAG |
| K2 Kingambit in play, own turn 5 | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.4 to +14.9) FLAG |
| K2 Kingambit in play, own turn 6 | +12.0 (+11.7 to +12.3) FLAG | +12.2 (+11.9 to +12.5) FLAG | +12.1 (+11.9 to +12.3) FLAG |
| G3 Pawniard in play, own turn 2 | -7.7 (-7.9 to -7.4) FLAG | -7.6 (-7.8 to -7.3) FLAG | -7.6 (-7.8 to -7.4) FLAG |
| G3 Pawniard in play, own turn 3 | -12.1 (-12.4 to -11.8) FLAG | -11.9 (-12.2 to -11.6) FLAG | -12.0 (-12.2 to -11.8) FLAG |
| G3 Pawniard in play, own turn 4 | -14.7 (-15.0 to -14.4) FLAG | -14.6 (-15.0 to -14.3) FLAG | -14.7 (-14.9 to -14.4) FLAG |
| G3 Pawniard in play, own turn 5 | -14.9 (-15.2 to -14.6) FLAG | -14.8 (-15.1 to -14.5) FLAG | -14.9 (-15.1 to -14.6) FLAG |
| G3 Kingambit in play, own turn 2 | +7.3 (+7.1 to +7.5) FLAG | +7.2 (+6.9 to +7.4) FLAG | +7.2 (+7.1 to +7.4) FLAG |
| G3 Kingambit in play, own turn 3 | +11.6 (+11.4 to +11.9) FLAG | +11.4 (+11.2 to +11.7) FLAG | +11.5 (+11.3 to +11.7) FLAG |
| G3 Kingambit in play, own turn 4 | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.1 to +14.5) FLAG |
| G3 Kingambit in play, own turn 5 | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.4 to +14.9) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | +2.7 (+2.5 to +2.8) FLAG | +2.6 (+2.4 to +2.7) FLAG | +2.6 (+2.5 to +2.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | +1.8 (+1.7 to +1.9) FLAG | +1.7 (+1.6 to +1.8) FLAG | +1.7 (+1.6 to +1.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | +7.3 (+7.1 to +7.5) FLAG | +7.2 (+6.9 to +7.4) FLAG | +7.2 (+7.1 to +7.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | +11.6 (+11.4 to +11.9) FLAG | +11.4 (+11.2 to +11.7) FLAG | +11.5 (+11.3 to +11.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.1 to +14.5) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.4 to +14.9) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | +7.2 (+6.9 to +7.4) FLAG | +3.6 (+3.5 to +3.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +10.1 (+9.8 to +10.4) FLAG | +11.4 (+11.2 to +11.7) FLAG | +10.8 (+10.6 to +11.0) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.0 to +14.6) FLAG | +14.3 (+14.1 to +14.5) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.3 to +15.0) FLAG | +14.6 (+14.4 to +14.9) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.012 (-0.014 to -0.010) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, A1.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): none flagged
- C-his (per-game bootstrap): P2 both Glimmora had their turn -1.4 points (-2.6 to -0.4); P2 the second Glimmora placed had its turn -1.6 points (-3.0 to -0.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -1.4 points (-2.5 to -0.3); P4 ready at the winning moment: Knocks out their strongest +2.7 points (+0.8 to +5.4); P5 plan reached in time: Knocks out their strongest +3.2 points (+1.2 to +5.6)
- C-his, seat-matched (per-game bootstrap): P2 both Glimmora had their turn -1.6 points (-2.5 to -0.7); P2 the second Glimmora placed had its turn -1.7 points (-2.7 to -0.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -1.4 points (-2.7 to -0.2); P4 ready at the winning moment: Knocks out their strongest +2.2 points (+0.6 to +4.4); P5 plan reached in time: Knocks out their strongest +2.4 points (+0.8 to +4.5)
- C-bot (per-game bootstrap): P2 both Glimmora had their turn -2.4 points (-2.9 to -1.9); P2 the second Glimmora placed had its turn -2.5 points (-3.0 to -2.0); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +2.3 points (+1.7 to +3.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.0 points (-3.5 to -2.4); P4 ready at the winning moment: Knocks out their strongest +1.9 points (+1.0 to +2.9); P4 the moment came and Kingambit was never ready in the deal -1.3 points (-2.1 to -0.7); P5 plan reached in time: Knocks out their strongest +1.9 points (+1.0 to +2.7)
- C-fixed fast (paired test): P2 both Glimmora had their turn -1.7 points (-1.9 to -1.5); P2 the second Glimmora placed had its turn -2.3 points (-2.5 to -2.1); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -1.5 points (-1.6 to -1.3); P4 ready at the winning moment: Knocks out their strongest +3.9 points (+3.6 to +4.2); P4 ready at the winning moment: Wins outright (a lower bound) +3.9 points (+3.6 to +4.2); P4 the moment came and Kingambit was never ready in the deal -3.9 points (-4.2 to -3.6); P5 plan reached in time: Knocks out their strongest +3.8 points (+3.5 to +4.1); P5 plan reached in time: Wins outright (a lower bound) +3.8 points (+3.5 to +4.1)
- C-fixed medium (paired test): P2 both Glimmora had their turn -3.6 points (-3.9 to -3.3); P2 the second Glimmora placed had its turn -4.0 points (-4.3 to -3.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +1.3 points (+1.0 to +1.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.7 points (-3.0 to -2.5); P4 ready at the winning moment: Knocks out their strongest +6.1 points (+5.8 to +6.4); P4 the moment came and Kingambit was never ready in the deal -5.6 points (-5.9 to -5.2); P5 plan reached in time: Knocks out their strongest +5.6 points (+5.3 to +5.9)
- C-fixed slow (paired test): P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -4.7 points (-5.0 to -4.4); P4 ready at the winning moment: Knocks out their strongest +2.8 points (+2.5 to +3.0); P4 ready at the winning moment: Wins outright (a lower bound) +2.8 points (+2.5 to +3.0); P4 the moment came and Kingambit was never ready in the deal -1.6 points (-1.9 to -1.4); P5 plan reached in time: Knocks out their strongest +1.8 points (+1.6 to +2.0); P5 plan reached in time: Wins outright (a lower bound) +1.8 points (+1.6 to +2.0)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 both Glimmora had their turn -1.7 points (-1.9 to -1.5); P2 the second Glimmora placed had its turn -2.2 points (-2.4 to -2.0); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +1.1 points (+0.9 to +1.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -1.5 points (-1.6 to -1.3)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +4.2 points (+3.9 to +4.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.6 points (-3.9 to -3.3); P4 the moment came and Kingambit was never ready in the deal +1.0 points (+0.9 to +1.2)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K2 Kingambit in play, own turn 2 +7.2 points; K2 Kingambit in play, own turn 3 +11.5 points; K2 Kingambit in play, own turn 4 +14.3 points; K2 Kingambit in play, own turn 5 +14.6 points; K2 Kingambit in play, own turn 6 +12.1 points; G3 Kingambit in play, own turn 2 +7.2 points; G3 Kingambit in play, own turn 3 +11.5 points; G3 Kingambit in play, own turn 4 +14.3 points; G3 Kingambit in play, own turn 5 +14.6 points; G4.s1 a Stage 1 or Stage 2 in play, own turn 2 +2.6 points.
Gives up (flagged, pooled): none flagged.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 +1.7; K3.by4 +2.1; K3.by5 +2.6; K3.by6 +3.3; K3.by7 +4.0; K3.by8 +4.2; K3.never -2.7; K3.k0 +1.7; K3.k2 +1.9; K4 +2.5; K5 -2.0; C-his, seat-matched: K3.by3 +1.9; K3.by4 +2.0; K3.by5 +2.5; K3.by6 +2.6; K3.by7 +4.1; K3.by8 +4.1; K3.never -1.9; K3.k0 +1.8; K3.k2 +1.5; K4 +2.3; K5 -2.2; C-bot: K3.by3 +1.8; K3.by4 +2.0; K3.by5 +2.6; K3.by6 +3.2; K3.by7 +3.6; K3.by8 +3.7; K3.never -3.2; K3.k0 +1.8; K4 +1.9; K5 -2.5; C-fixed fast: K3.by4 +2.0; K3.by5 +4.2; K3.by6 +4.2; K3.by7 +4.2; K3.by8 +4.2; K3.never -4.2; K3.k2 +1.1; K3.k3p +3.1; K4 +4.2; K5 -4.4; C-fixed medium: K3.by3 +2.2; K3.by4 +2.6; K3.by5 +5.1; K3.by6 +8.0; K3.by7 +7.8; K3.by8 +7.8; K3.never -7.8; K3.k0 +2.2; K3.k3p +4.9; K4 +5.6; K5 -5.4; C-fixed slow: K3.by3 +2.2; K3.by4 +2.2; K3.by5 +3.0; K3.by6 +3.5; K3.by7 +6.3; K3.by8 +8.6; K3.never -8.6; K3.k0 +2.2; K3.k2 +1.3; K3.k3p +5.1; K4 +6.4; K5 -2.6; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 +2.0; K3.by5 +4.0; K3.by6 +4.0; K3.by7 +4.0; K3.by8 +4.0; K3.never -4.0; K3.k2 +1.1; K3.k3p +2.8; K4 +4.0; K5 -4.4; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 +2.2; K3.by4 +2.2; K3.by5 +3.0; K3.by6 +3.5; K3.by7 +5.4; K3.by8 +7.3; K3.by9 +6.8; K3.by10 +6.3; K3.never -6.3; K3.k0 +2.2; K3.k2 +1.3; K3.k3p +2.8; K4 +4.1; K5 -2.7.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## A2 (card-list id ba59eb4ecb12)

Changes: ['-1 Lucky Ice Pop B2 145', "-1 Professor's Research A4b 373", '+1 Rare Candy A3 144', '+1 Juliana B3a 071']

Copycat decisions with a Copycat in hand: 244,926; the valuation and the fallback rule disagree at 111,431 of 244,926 Copycat decisions (45.5%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Juliana 0.2371, Poké Ball 0.4289, Rare Candy 0.4289.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.05955; in 8 cards: 0.08964.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Juliana: 29/34/39/44/49%; Poké Ball: 51/58/64/70/76%; Rare Candy: 51/58/64/70/76%.
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
| P2 at least one Glimmora had its turn | 84.0% / 93.5% [73-92] | 72.5% / 86.6% [57-85] | 78.2% / 90.1% [66-88] |
| P2 both Glimmora had their turn | 29.8% / 64.9% [22-37] | 25.5% / 64.3% [16-38] | 27.7% / 64.6% [20-36] |
| P2 the first Glimmora placed had its turn | 80.0% / 87.3% [70-88] | 65.1% / 75.4% [49-80] | 72.6% / 81.4% [60-84] |
| P2 the second Glimmora placed had its turn | 33.8% / 64.0% [25-42] | 32.9% / 64.1% [23-45] | 33.3% / 64.0% [24-42] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 6.8% / 49.9% [2-13] | 7.2% / 51.5% [3-12] | 7.0% / 50.7% [3-12] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 28.8% / 64.4% [23-35] | 33.3% / 68.1% [26-40] | 31.1% / 66.3% [25-37] |
| P4 ready at the winning moment: Knocks out their strongest | 15.6% / 40.6% [4-29] | 12.0% / 39.2% [3-23] | 13.8% / 39.9% [3-26] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.2% / 27.3% [0-7] | 1.6% / 28.8% [0-5] | 1.9% / 28.1% [0-6] |
| P4 not ready, ready 1 turn late | 4.8% / 44.5% [0-12] | 4.2% / 46.5% [0-10] | 4.5% / 45.5% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.0% / 40.7% [0-3] | 1.1% / 43.4% [0-3] | 1.1% / 42.0% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 6.5% / 46.2% [0-15] | 6.0% / 48.3% [0-15] | 6.2% / 47.2% [0-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 32.4% / 57.5% [11-57] | 34.5% / 61.7% [16-57] | 33.4% / 59.6% [14-56] |
| P5 plan reached in time: Knocks out their strongest | 21.4% / 61.1% [8-37] | 17.2% / 59.5% [6-30] | 19.3% / 60.3% [7-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.3% / 42.0% [0-7] | 1.9% / 44.2% [0-6] | 2.1% / 43.1% [0-6] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 55.8% of 2791 [33-75] | 51.7% of 2324 [31-73] | 53.9% of 5115 [32-74] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 8.0% of 2791 [0-32] | 7.1% of 2324 [0-33] | 7.6% of 5115 [0-32] |
| P4 not ready, ready 1 turn late | 17.2% of 2791 [0-51] | 18.0% of 2324 [0-50] | 17.6% of 5115 [0-51] |
| P4 not ready, ready 2 or more turns late | 3.7% of 2791 [0-12] | 4.6% of 2324 [0-14] | 4.1% of 5115 [0-13] |
| P4 the moment came and Kingambit was never ready in the deal | 23.3% of 2791 [0-40] | 25.8% of 2324 [0-48] | 24.4% of 5115 [0-43] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.0 points (-6.8 to -3.5); P2.both: -8.1 points (-10.1 to -5.9); P2.g1: -5.1 points (-6.3 to -3.9); P2.g2: -8.0 points (-10.0 to -5.8); P4.ko: +1.7 points (+0.0 to +3.6); P4.nomoment: +3.1 points (+1.7 to +4.6).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.6% / 93.2% [68-93] | 82.4% / 91.2% [70-92] | 82.5% / 92.2% [74-90] |
| P2 both Glimmora had their turn | 30.0% / 60.6% [20-39] | 23.4% / 75.5% [14-35] | 26.7% / 68.1% [20-34] |
| P2 the first Glimmora placed had its turn | 78.2% / 87.1% [64-89] | 78.6% / 81.3% [66-90] | 78.4% / 84.2% [70-86] |
| P2 the second Glimmora placed had its turn | 34.4% / 60.5% [23-44] | 27.2% / 69.9% [18-41] | 30.8% / 65.2% [23-40] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 3.8% / 43.1% [1-7] | 13.6% / 71.9% [0-29] | 8.7% / 57.5% [2-16] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 28.3% / 60.5% [21-36] | 37.1% / 85.7% [20-47] | 32.7% / 73.1% [24-40] |
| P4 ready at the winning moment: Knocks out their strongest | 18.3% / 40.2% [4-36] | 5.8% / 54.9% [0-17] | 12.1% / 47.6% [4-24] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.7% / 25.6% [0-11] | 0.0% / 49.1% [0-0] | 1.9% / 37.4% [0-7] |
| P4 not ready, ready 1 turn late | 6.2% / 40.3% [0-15] | 0.0% / 70.0% [0-0] | 3.1% / 55.1% [0-9] |
| P4 not ready, ready 2 or more turns late | 1.4% / 35.5% [0-4] | 0.0% / 70.0% [0-0] | 0.7% / 52.7% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 9.3% / 43.4% [0-21] | 0.0% / 70.0% [0-0] | 4.6% / 56.7% [0-12] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.7% / 52.6% [8-60] | 24.3% / 73.4% [2-51] | 27.5% / 63.0% [11-48] |
| P5 plan reached in time: Knocks out their strongest | 25.9% / 60.0% [8-45] | 5.8% / 75.7% [0-17] | 15.8% / 67.9% [6-31] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.0% / 38.1% [0-12] | 0.0% / 70.0% [0-0] | 2.0% / 54.0% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 52.2% of 3516 [23-71] | 100.0% of 577 [100-100] | 58.9% of 4093 [35-80] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.6% of 3516 [0-41] | 0.0% of 577 [0-0] | 9.1% of 4093 [0-33] |
| P4 not ready, ready 1 turn late | 17.6% of 3516 [0-63] | 0.0% of 577 [0-0] | 15.1% of 4093 [0-44] |
| P4 not ready, ready 2 or more turns late | 3.9% of 3516 [0-14] | 0.0% of 577 [0-0] | 3.3% of 4093 [0-10] |
| P4 the moment came and Kingambit was never ready in the deal | 26.4% of 3516 [0-47] | 0.0% of 577 [0-0] | 22.7% of 4093 [0-40] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.0 points (-6.4 to -3.6); P2.both: -8.6 points (-10.7 to -6.6); P2.g1: -5.2 points (-6.3 to -4.0); P2.g2: -8.4 points (-10.4 to -6.5); P3.pawn_promo: +1.1 points (+0.3 to +2.0); P3.grimer_muk: +1.4 points (+0.6 to +2.3); P4.nomoment: +4.0 points (+1.6 to +5.9).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.7% / 87.8% [84-89] | 75.9% / 77.5% [72-80] | 81.3% / 82.7% [78-85] |
| P2 both Glimmora had their turn | 32.0% / 38.5% [28-36] | 23.7% / 31.1% [20-28] | 27.9% / 34.8% [24-32] |
| P2 the first Glimmora placed had its turn | 80.2% / 80.4% [76-84] | 66.8% / 67.1% [62-72] | 73.5% / 73.8% [69-78] |
| P2 the second Glimmora placed had its turn | 38.5% / 43.3% [35-42] | 32.8% / 37.9% [29-37] | 35.6% / 40.6% [32-39] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14] | 12.6% [12-13] | 12.8% [12-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 18.2% / 27.8% [14-22] | 17.2% / 26.8% [14-20] | 17.7% / 27.3% [14-21] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 36.9% / 44.5% [34-40] | 42.7% / 49.6% [40-46] | 39.8% / 47.1% [37-43] |
| P4 ready at the winning moment: Knocks out their strongest | 9.1% / 15.1% [5-14] | 7.9% / 14.6% [4-12] | 8.5% / 14.9% [5-13] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.3% / 6.2% [0-1] | 0.6% / 7.2% [0-2] | 0.4% / 6.7% [0-1] |
| P4 not ready, ready 1 turn late | 4.2% / 11.7% [2-7] | 3.1% / 11.8% [2-5] | 3.6% / 11.8% [2-6] |
| P4 not ready, ready 2 or more turns late | 1.0% / 8.5% [0-2] | 1.2% / 9.9% [0-2] | 1.1% / 9.2% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 7.5% / 15.1% [4-12] | 7.8% / 16.4% [4-12] | 7.7% / 15.8% [4-12] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 70.6% / 76.6% [60-81] | 71.3% / 78.0% [61-81] | 71.0% / 77.3% [60-81] |
| P5 plan reached in time: Knocks out their strongest | 14.3% / 21.8% [8-21] | 12.2% / 20.9% [7-18] | 13.3% / 21.4% [8-20] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.3% / 7.9% [0-1] | 0.6% / 9.3% [0-2] | 0.5% / 8.6% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 41.8% of 2184 [30-55] | 39.6% of 2000 [30-51] | 40.8% of 4184 [30-53] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.2% of 2184 [0-5] | 2.8% of 2000 [0-10] | 1.9% of 4184 [0-6] |
| P4 not ready, ready 1 turn late | 19.2% of 2184 [12-27] | 15.5% of 2000 [10-21] | 17.4% of 4184 [11-24] |
| P4 not ready, ready 2 or more turns late | 4.4% of 2184 [2-8] | 6.0% of 2000 [3-10] | 5.2% of 4184 [2-8] |
| P4 the moment came and Kingambit was never ready in the deal | 34.6% of 2184 [22-47] | 38.9% of 2000 [27-50] | 36.6% of 4184 [25-48] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: -5.8 points (-6.3 to -5.2); P2.both: -9.1 points (-10.1 to -8.0); P2.g1: -5.3 points (-5.8 to -4.8); P2.g2: -9.6 points (-10.5 to -8.7); P3.pawn_promo: +1.9 points (+1.3 to +2.4); P4.ko: +1.4 points (+0.6 to +2.1); P4.never: -1.0 points (-1.8 to -0.5); P4.nomoment: +1.5 points (+0.9 to +2.2).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 73.7% [73-75, Wilson] | 43.4% [42-44, Wilson] | 58.6% [58-59, Wilson] |
| P2 both Glimmora had their turn | 18.1% [17-19, Wilson] | 4.7% [4-5, Wilson] | 11.4% [11-12, Wilson] |
| P2 the first Glimmora placed had its turn | 69.2% [68-70, Wilson] | 27.6% [27-28, Wilson] | 48.4% [48-49, Wilson] |
| P2 the second Glimmora placed had its turn | 22.7% [22-24, Wilson] | 20.6% [20-21, Wilson] | 21.6% [21-22, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 21.6% [21-22, Wilson] | 18.1% [17-19, Wilson] | 19.9% [19-20, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 54.8% [54-56, Wilson] | 50.6% [50-52, Wilson] | 52.7% [52-53, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 16.2% [15-17, Wilson] | 5.7% [5-6, Wilson] | 10.9% [11-11, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 16.2% [15-17, Wilson] | 5.7% [5-6, Wilson] | 10.9% [11-11, Wilson] |
| P4 not ready, ready 1 turn late | 1.2% [1-1, Wilson] | 0.3% [0-0, Wilson] | 0.8% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 16.4% [16-17, Wilson] | 11.1% [10-12, Wilson] | 13.7% [13-14, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 66.2% [65-67, Wilson] | 82.8% [82-84, Wilson] | 74.5% [74-75, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 17.4% [17-18, Wilson] | 6.1% [6-7, Wilson] | 11.7% [11-12, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 17.4% [17-18, Wilson] | 6.1% [6-7, Wilson] | 11.7% [11-12, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 47.9% of 3378 [46-50, Wilson] | 33.4% of 1717 [31-36, Wilson] | 43.0% of 5095 [42-44, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 47.9% of 3378 [46-50, Wilson] | 33.4% of 1717 [31-36, Wilson] | 43.0% of 5095 [42-44, Wilson] |
| P4 not ready, ready 1 turn late | 3.7% of 3378 [3-4, Wilson] | 2.0% of 1717 [1-3, Wilson] | 3.1% of 5095 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 3378 [0-0, Wilson] | 0.0% of 1717 [0-0, Wilson] | 0.0% of 5095 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 48.4% of 3378 [47-50, Wilson] | 64.6% of 1717 [62-67, Wilson] | 53.9% of 5095 [53-55, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: -8.8 points (-9.2 to -8.4); P2.both: -6.8 points (-7.2 to -6.4); P2.g1: -6.6 points (-7.0 to -6.2); P2.g2: -9.1 points (-9.6 to -8.6); P3.grimer_muk: -3.3 points (-3.7 to -2.8); P4.never: -7.5 points (-7.9 to -7.0); P4.nomoment: +7.8 points (+7.4 to +8.2).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 84.3% [84-85, Wilson] | 73.7% [73-75, Wilson] | 79.0% [78-80, Wilson] |
| P2 both Glimmora had their turn | 27.3% [26-28, Wilson] | 18.6% [18-19, Wilson] | 22.9% [22-24, Wilson] |
| P2 the first Glimmora placed had its turn | 81.0% [80-82, Wilson] | 70.0% [69-71, Wilson] | 75.5% [75-76, Wilson] |
| P2 the second Glimmora placed had its turn | 30.6% [30-32, Wilson] | 22.2% [21-23, Wilson] | 26.4% [26-27, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 24.7% [24-26, Wilson] | 22.1% [21-23, Wilson] | 23.4% [23-24, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 53.1% [52-54, Wilson] | 55.5% [54-56, Wilson] | 54.3% [54-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 27.4% [26-28, Wilson] | 16.0% [15-17, Wilson] | 21.7% [21-22, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 1.4% [1-2, Wilson] | 1.1% [1-1, Wilson] | 1.3% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 17.7% [17-18, Wilson] | 17.3% [17-18, Wilson] | 17.5% [17-18, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 53.5% [53-55, Wilson] | 65.6% [65-67, Wilson] | 59.6% [59-60, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 28.8% [28-30, Wilson] | 17.1% [16-18, Wilson] | 23.0% [22-24, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 58.9% of 4647 [57-60, Wilson] | 46.4% of 3442 [45-48, Wilson] | 53.6% of 8089 [52-55, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 4647 [0-0, Wilson] | 0.0% of 3442 [0-0, Wilson] | 0.0% of 8089 [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 3.1% of 4647 [3-4, Wilson] | 3.3% of 3442 [3-4, Wilson] | 3.2% of 8089 [3-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 4647 [0-0, Wilson] | 0.0% of 3442 [0-0, Wilson] | 0.0% of 8089 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 38.0% of 4647 [37-39, Wilson] | 50.3% of 3442 [49-52, Wilson] | 43.2% of 8089 [42-44, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: -7.0 points (-7.4 to -6.7); P2.both: -11.0 points (-11.6 to -10.5); P2.g1: -6.7 points (-7.0 to -6.3); P2.g2: -11.4 points (-12.0 to -10.9); P3.grimer_muk: -2.4 points (-3.0 to -1.9); P4.late1: -1.1 points (-1.3 to -0.9); P4.never: -7.4 points (-7.9 to -6.9); P4.nomoment: +8.6 points (+8.2 to +9.0); P5.ko: -1.2 points (-1.7 to -0.7).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.5% [91-92, Wilson] | 83.1% [82-84, Wilson] | 87.3% [87-88, Wilson] |
| P2 both Glimmora had their turn | 56.3% [55-57, Wilson] | 41.2% [40-42, Wilson] | 48.7% [48-49, Wilson] |
| P2 the first Glimmora placed had its turn | 84.8% [84-86, Wilson] | 75.1% [74-76, Wilson] | 80.0% [79-81, Wilson] |
| P2 the second Glimmora placed had its turn | 63.0% [62-64, Wilson] | 49.2% [48-50, Wilson] | 56.1% [55-57, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 9.3% [9-10, Wilson] | 12.2% [12-13, Wilson] | 10.7% [10-11, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.1% [30-32, Wilson] | 39.6% [39-41, Wilson] | 35.4% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 43.6% [43-45, Wilson] | 34.2% [33-35, Wilson] | 38.9% [38-40, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 43.6% [43-45, Wilson] | 34.2% [33-35, Wilson] | 38.9% [38-40, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 2.5% [2-3, Wilson] | 1.2% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 14.4% [14-15, Wilson] | 12.2% [12-13, Wilson] | 13.3% [13-14, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 42.0% [41-43, Wilson] | 51.2% [50-52, Wilson] | 46.6% [46-47, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 43.6% [43-45, Wilson] | 36.7% [36-38, Wilson] | 40.1% [39-41, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 43.6% [43-45, Wilson] | 36.7% [36-38, Wilson] | 40.1% [39-41, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 75.2% of 5797 [74-76, Wilson] | 70.0% of 4881 [69-71, Wilson] | 72.8% of 10678 [72-74, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 75.2% of 5797 [74-76, Wilson] | 70.0% of 4881 [69-71, Wilson] | 72.8% of 10678 [72-74, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 5797 [0-0, Wilson] | 5.1% of 4881 [5-6, Wilson] | 2.3% of 10678 [2-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 5797 [0-0, Wilson] | 0.0% of 4881 [0-0, Wilson] | 0.0% of 10678 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 24.8% of 5797 [24-26, Wilson] | 24.9% of 4881 [24-26, Wilson] | 24.9% of 10678 [24-26, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.4 points (-5.8 to -5.1); P2.both: -13.5 points (-14.1 to -13.0); P2.g1: -6.0 points (-6.3 to -5.6); P2.g2: -13.0 points (-13.6 to -12.4); P3.pawn_promo: +4.0 points (+3.6 to +4.4); P4.ko: -5.6 points (-6.1 to -5.1); P4.win: -5.6 points (-6.1 to -5.1); P4.nomoment: +7.2 points (+6.8 to +7.6); P5.ko: -6.5 points (-6.9 to -6.0); P5.win: -6.5 points (-6.9 to -6.0).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 73.9% [73-75, Wilson] | 43.6% [43-45, Wilson] | 58.7% [58-59, Wilson] |
| P2 both Glimmora had their turn | 18.4% [18-19, Wilson] | 4.7% [4-5, Wilson] | 11.6% [11-12, Wilson] |
| P2 the first Glimmora placed had its turn | 69.2% [68-70, Wilson] | 27.6% [27-28, Wilson] | 48.4% [48-49, Wilson] |
| P2 the second Glimmora placed had its turn | 23.1% [22-24, Wilson] | 20.7% [20-22, Wilson] | 21.9% [21-22, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 24.6% [24-25, Wilson] | 18.7% [18-20, Wilson] | 21.7% [21-22, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 54.8% [54-56, Wilson] | 50.6% [50-52, Wilson] | 52.7% [52-53, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 2.4% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.5% [1-2, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.4% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.5% [1-2, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 2.9% [3-3, Wilson] | 0.8% [1-1, Wilson] | 1.8% [2-2, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 94.7% [94-95, Wilson] | 98.6% [98-99, Wilson] | 96.7% [96-97, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 2.4% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.5% [1-2, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.4% [2-3, Wilson] | 0.6% [0-1, Wilson] | 1.5% [1-2, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 45.2% of 527 [41-49, Wilson] | 44.1% of 143 [36-52, Wilson] | 44.9% of 670 [41-49, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 45.2% of 527 [41-49, Wilson] | 44.1% of 143 [36-52, Wilson] | 44.9% of 670 [41-49, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 527 [0-1, Wilson] | 0.0% of 143 [0-3, Wilson] | 0.0% of 670 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 527 [0-1, Wilson] | 0.0% of 143 [0-3, Wilson] | 0.0% of 670 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 54.8% of 527 [51-59, Wilson] | 55.9% of 143 [48-64, Wilson] | 55.1% of 670 [51-59, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: -8.8 points (-9.2 to -8.4); P2.both: -6.9 points (-7.3 to -6.5); P2.g1: -6.6 points (-7.0 to -6.2); P2.g2: -9.1 points (-9.5 to -8.6); P3.grimer_muk: -3.3 points (-3.7 to -2.8); P4.never: -1.2 points (-1.4 to -1.0); P4.nomoment: +2.0 points (+1.7 to +2.2).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.6% [91-92, Wilson] | 83.2% [82-84, Wilson] | 87.4% [87-88, Wilson] |
| P2 both Glimmora had their turn | 58.7% [58-60, Wilson] | 43.7% [43-45, Wilson] | 51.2% [51-52, Wilson] |
| P2 the first Glimmora placed had its turn | 84.8% [84-86, Wilson] | 75.1% [74-76, Wilson] | 80.0% [79-81, Wilson] |
| P2 the second Glimmora placed had its turn | 65.5% [65-66, Wilson] | 51.8% [51-53, Wilson] | 58.6% [58-59, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.0% [12-14, Wilson] | 12.6% [12-13, Wilson] | 12.8% [12-13, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) | 39.4% [38-40, Wilson] | 32.5% [32-33, Wilson] | 35.9% [35-37, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 42.8% [42-44, Wilson] | 47.1% [46-48, Wilson] | 44.9% [44-46, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.7% [4-5, Wilson] | 5.6% [5-6, Wilson] | 5.1% [5-5, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.7% [4-5, Wilson] | 5.6% [5-6, Wilson] | 5.1% [5-5, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.1% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 12.1% [11-13, Wilson] | 8.1% [8-9, Wilson] | 10.1% [10-11, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 83.3% [83-84, Wilson] | 86.3% [86-87, Wilson] | 84.8% [84-85, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.7% [4-5, Wilson] | 5.6% [5-6, Wilson] | 5.2% [5-5, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.7% [4-5, Wilson] | 5.6% [5-6, Wilson] | 5.2% [5-5, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 28.0% of 1674 [26-30, Wilson] | 40.5% of 1372 [38-43, Wilson] | 33.7% of 3046 [32-35, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 28.0% of 1674 [26-30, Wilson] | 40.5% of 1372 [38-43, Wilson] | 33.7% of 3046 [32-35, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 1674 [0-0, Wilson] | 0.4% of 1372 [0-1, Wilson] | 0.2% of 3046 [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 1674 [0-0, Wilson] | 0.0% of 1372 [0-0, Wilson] | 0.0% of 3046 [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 72.0% of 1674 [70-74, Wilson] | 59.1% of 1372 [56-62, Wilson] | 66.2% of 3046 [64-68, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: -5.4 points (-5.7 to -5.1); P2.both: -13.1 points (-13.6 to -12.5); P2.g1: -6.0 points (-6.3 to -5.6); P2.g2: -12.5 points (-13.1 to -12.0); P3.grimer_muk: -2.1 points (-2.6 to -1.6); P4.ko: -1.4 points (-1.7 to -1.2); P4.win: -1.4 points (-1.7 to -1.2); P4.never: -1.6 points (-1.9 to -1.3); P4.nomoment: +3.1 points (+2.8 to +3.4); P5.ko: -1.5 points (-1.8 to -1.2); P5.win: -1.5 points (-1.8 to -1.2).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 29.2% (28.8-29.6) | 28.8% (28.4-29.2) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 52.5% (52.1-52.9) | 52.2% (51.7-52.6) | 52.3% (52.0-52.6) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 63.1% (62.7-63.6) | 62.8% (62.4-63.2) | 63.0% (62.7-63.3) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 70.2% (69.8-70.6) | 70.0% (69.6-70.4) | 70.1% (69.8-70.4) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 75.0% (74.6-75.4) | 75.0% (74.6-75.4) | 75.0% (74.7-75.3) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 78.4% (78.0-78.7) | 78.4% (78.1-78.8) | 78.4% (78.1-78.6) |
| K2 Kingambit in play, own turn 2 | 20.6% (20.3-21.0) | 20.5% (20.2-20.9) | 20.6% (20.3-20.8) |
| K2 Kingambit in play, own turn 3 | 34.1% (33.7-34.5) | 33.9% (33.4-34.3) | 34.0% (33.7-34.3) |
| K2 Kingambit in play, own turn 4 | 47.6% (47.2-48.1) | 47.4% (46.9-47.8) | 47.5% (47.2-47.8) |
| K2 Kingambit in play, own turn 5 | 60.0% (59.6-60.4) | 59.7% (59.2-60.1) | 59.8% (59.5-60.1) |
| K2 Kingambit in play, own turn 6 | 69.7% (69.3-70.1) | 69.5% (69.1-69.9) | 69.6% (69.3-69.9) |
| K6 Muk and Regigigas both in play, own turn 3 | 17.4% (17.0-17.7) | 17.4% (17.0-17.7) | 17.4% (17.1-17.6) |
| K6 Muk and Regigigas both in play, own turn 4 | 25.0% (24.6-25.3) | 25.0% (24.6-25.3) | 25.0% (24.7-25.2) |
| K6 Muk and Regigigas both in play, own turn 5 | 32.2% (31.7-32.6) | 32.1% (31.7-32.5) | 32.1% (31.8-32.4) |
| G3 Pawniard in play, own turn 1 | 52.5% (52.1-52.9) | 52.2% (51.7-52.6) | 52.3% (52.0-52.6) |
| G3 Pawniard in play, own turn 2 | 42.5% (42.1-42.9) | 42.3% (41.8-42.7) | 42.4% (42.1-42.7) |
| G3 Pawniard in play, own turn 3 | 36.1% (35.7-36.5) | 36.1% (35.7-36.5) | 36.1% (35.8-36.4) |
| G3 Pawniard in play, own turn 4 | 27.4% (27.0-27.8) | 27.6% (27.3-28.0) | 27.5% (27.2-27.8) |
| G3 Pawniard in play, own turn 5 | 18.4% (18.0-18.7) | 18.7% (18.4-19.1) | 18.6% (18.3-18.8) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 20.6% (20.3-21.0) | 20.5% (20.2-20.9) | 20.6% (20.3-20.8) |
| G3 Kingambit in play, own turn 3 | 34.1% (33.7-34.5) | 33.9% (33.4-34.3) | 34.0% (33.7-34.3) |
| G3 Kingambit in play, own turn 4 | 47.6% (47.2-48.1) | 47.4% (46.9-47.8) | 47.5% (47.2-47.8) |
| G3 Kingambit in play, own turn 5 | 60.0% (59.6-60.4) | 59.7% (59.2-60.1) | 59.8% (59.5-60.1) |
| G3 Alolan Grimer in play, own turn 1 | 51.3% (50.8-51.7) | 51.4% (50.9-51.8) | 51.3% (51.0-51.6) |
| G3 Alolan Grimer in play, own turn 2 | 46.1% (45.6-46.5) | 46.2% (45.8-46.6) | 46.1% (45.8-46.4) |
| G3 Alolan Grimer in play, own turn 3 | 42.3% (41.9-42.7) | 42.5% (42.0-42.9) | 42.4% (42.1-42.7) |
| G3 Alolan Grimer in play, own turn 4 | 37.3% (36.9-37.7) | 37.7% (37.2-38.1) | 37.5% (37.2-37.8) |
| G3 Alolan Grimer in play, own turn 5 | 31.3% (30.9-31.7) | 31.6% (31.2-32.0) | 31.4% (31.1-31.7) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 15.2% (14.9-15.6) | 15.2% (14.9-15.5) | 15.2% (15.0-15.4) |
| G3 Alolan Muk in play, own turn 3 | 25.3% (24.9-25.7) | 25.3% (24.9-25.7) | 25.3% (25.0-25.6) |
| G3 Alolan Muk in play, own turn 4 | 34.7% (34.2-35.1) | 34.6% (34.2-35.0) | 34.6% (34.3-34.9) |
| G3 Alolan Muk in play, own turn 5 | 43.4% (42.9-43.8) | 43.3% (42.9-43.8) | 43.3% (43.0-43.7) |
| G3 Glimmet in play, own turn 1 | 78.8% (78.4-79.1) | 78.9% (78.6-79.3) | 78.9% (78.6-79.1) |
| G3 Glimmet in play, own turn 2 | 52.6% (52.1-53.0) | 52.5% (52.1-52.9) | 52.5% (52.2-52.8) |
| G3 Glimmet in play, own turn 3 | 46.3% (45.9-46.8) | 45.9% (45.5-46.4) | 46.1% (45.8-46.4) |
| G3 Glimmet in play, own turn 4 | 37.6% (37.1-38.0) | 37.4% (37.0-37.8) | 37.5% (37.2-37.8) |
| G3 Glimmet in play, own turn 5 | 27.6% (27.2-28.0) | 27.5% (27.1-27.8) | 27.5% (27.3-27.8) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 56.0% (55.6-56.4) | 56.1% (55.7-56.6) | 56.1% (55.8-56.4) |
| G3 Glimmora in play, own turn 3 | 72.1% (71.7-72.5) | 72.4% (72.0-72.8) | 72.2% (72.0-72.5) |
| G3 Glimmora in play, own turn 4 | 83.5% (83.2-83.8) | 83.4% (83.1-83.8) | 83.5% (83.2-83.7) |
| G3 Glimmora in play, own turn 5 | 91.1% (90.9-91.4) | 91.1% (90.9-91.4) | 91.1% (91.0-91.3) |
| G3 Regigigas in play, own turn 1 | 52.0% (51.6-52.4) | 51.7% (51.2-52.1) | 51.8% (51.5-52.2) |
| G3 Regigigas in play, own turn 2 | 63.3% (62.9-63.7) | 62.9% (62.4-63.3) | 63.1% (62.8-63.4) |
| G3 Regigigas in play, own turn 3 | 70.7% (70.3-71.1) | 70.5% (70.1-70.9) | 70.6% (70.3-70.9) |
| G3 Regigigas in play, own turn 4 | 75.8% (75.4-76.1) | 75.4% (75.1-75.8) | 75.6% (75.3-75.9) |
| G3 Regigigas in play, own turn 5 | 79.0% (78.6-79.3) | 78.7% (78.3-79.1) | 78.8% (78.6-79.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 73.9% (73.5-74.3) | 74.0% (73.7-74.4) | 74.0% (73.7-74.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 88.1% (87.8-88.4) | 88.0% (87.7-88.3) | 88.0% (87.8-88.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 94.9% (94.7-95.1) | 94.8% (94.6-95.0) | 94.9% (94.7-95.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.1% (97.9-98.2) | 98.0% (97.9-98.2) | 98.0% (98.0-98.1) |
| G4.s2 a Stage 2 in play, own turn 2 | 20.6% (20.3-21.0) | 20.5% (20.2-20.9) | 20.6% (20.3-20.8) |
| G4.s2 a Stage 2 in play, own turn 3 | 34.1% (33.7-34.5) | 33.9% (33.4-34.3) | 34.0% (33.7-34.3) |
| G4.s2 a Stage 2 in play, own turn 4 | 47.6% (47.2-48.1) | 47.4% (46.9-47.8) | 47.5% (47.2-47.8) |
| G4.s2 a Stage 2 in play, own turn 5 | 60.0% (59.6-60.4) | 59.7% (59.2-60.1) | 59.8% (59.5-60.1) |
| G5.any3 an empty own turn among turns 1-3 | 27.9% (27.5-28.3) | 27.5% (27.1-27.8) | 27.7% (27.4-27.9) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 20.5% (20.2-20.9) | 10.3% (10.1-10.4) |
| G6 Kingambit with [DD] attached, own turn 3 | 29.9% (29.5-30.3) | 33.9% (33.4-34.3) | 31.9% (31.6-32.2) |
| G6 Kingambit with [DD] attached, own turn 4 | 47.6% (47.2-48.1) | 47.4% (46.9-47.8) | 47.5% (47.2-47.8) |
| G6 Kingambit with [DD] attached, own turn 5 | 60.0% (59.6-60.4) | 59.7% (59.2-60.1) | 59.8% (59.5-60.1) |
| G5 mean empty own turns in turns 1-5 | 0.810 | 0.805 | 0.807 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 4.5% / 12.9% [3-6] | 2.3% / 6.5% [1-3] |
| K3.by3 | 6.1% / 14.7% [4-8] | 5.3% / 13.7% [3-7] | 5.7% / 14.2% [4-8] |
| K3.by4 | 6.8% / 15.4% [5-9] | 8.7% / 17.1% [7-11] | 7.7% / 16.2% [6-9] |
| K3.by5 | 10.6% / 19.3% [8-14] | 9.8% / 24.2% [7-12] | 10.2% / 21.7% [8-13] |
| K3.by6 | 11.3% / 26.9% [8-15] | 15.7% / 37.5% [10-24] | 13.5% / 32.2% [10-18] |
| K3.by7 | 18.9% / 42.0% [10-30] | 17.1% / 58.4% [10-26] | 18.0% / 50.2% [11-28] |
| K3.by8 | 21.6% / 65.1% [12-34] | 17.3% / 61.5% [10-26] | 19.4% / 63.3% [11-30] |
| K3.never | 34.9% / 78.4% [16-57] | 38.5% / 82.7% [19-59] | 36.7% / 80.6% [18-58] |
| K3.k0 | 7.0% / 50.5% [5-9] | 5.6% / 49.9% [3-8] | 6.3% / 50.2% [4-8] |
| K3.k1 | 0.0% / 43.5% [0-0] | 0.0% / 44.2% [0-0] | 0.0% / 43.9% [0-0] |
| K3.k2 | 9.9% / 53.5% [2-20] | 8.9% / 53.2% [3-17] | 9.4% / 53.3% [3-19] |
| K3.k3p | 4.7% / 48.2% [0-11] | 2.7% / 47.0% [0-7] | 3.7% / 47.6% [0-9] |
| K4 | 14.6% / 61.9% [4-27] | 11.6% / 58.8% [4-21] | 13.1% / 60.4% [4-24] |
| K5 | 4.3% / 59.1% [3-6] | 6.6% / 56.0% [4-9] | 5.4% / 57.5% [4-8] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by2: +1.1 points (+0.7 to +1.5); K3.by3: +2.5 points (+1.6 to +3.3); K3.by4: +3.1 points (+2.4 to +3.9); K3.by5: +4.1 points (+3.1 to +5.2); K3.by6: +4.7 points (+3.4 to +5.8); K3.by7: +4.7 points (+3.3 to +6.3); K3.by8: +4.8 points (+3.3 to +6.3); K3.k0: +2.4 points (+1.5 to +3.2); K3.k2: +2.6 points (+1.3 to +4.1); K4: +2.4 points (+1.1 to +3.9); K5: -2.7 points (-3.3 to -2.1).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 6.1% [5-7] | 3.0% [0-5] |
| K3.by3 | 5.6% / 16.9% [3-8] | 7.2% [5-9] | 6.4% / 12.1% [5-8] |
| K3.by4 | 6.1% / 17.4% [3-9] | 9.6% [8-11] | 7.8% / 13.5% [5-9] |
| K3.by5 | 10.2% / 21.5% [7-14] | 11.1% / 34.4% [10-12] | 10.6% / 27.9% [9-13] |
| K3.by6 | 10.9% / 22.2% [7-15] | 12.2% / 35.5% [10-16] | 11.6% / 28.9% [9-14] |
| K3.by7 | 21.5% / 43.3% [10-37] | 18.8% / 71.8% [10-36] | 20.2% / 57.6% [11-32] |
| K3.by8 | 21.6% / 60.9% [10-37] | 18.8% / 79.4% [10-36] | 20.2% / 70.1% [11-32] |
| K3.never | 39.1% / 78.5% [15-65] | 20.6% / 81.2% [2-41] | 29.9% / 79.8% [14-49] |
| K3.k0 | 6.3% / 45.7% [3-9] | 7.7% / 68.2% [5-10] | 7.0% / 56.9% [5-9] |
| K3.k1 | 0.0% / 39.4% [0-0] | 0.0% / 60.5% [0-0] | 0.0% / 50.0% [0-0] |
| K3.k2 | 11.9% / 51.3% [2-27] | 4.6% / 65.1% [0-8] | 8.2% / 58.2% [3-17] |
| K3.k3p | 3.3% / 42.7% [0-10] | 6.6% / 67.1% [0-20] | 5.0% / 54.9% [0-12] |
| K4 | 15.2% / 57.5% [2-31] | 11.2% / 77.6% [0-28] | 13.2% / 67.6% [4-25] |
| K5 | 4.6% / 51.5% [3-7] | 5.3% / 77.1% [3-7] | 4.9% / 64.3% [3-6] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +2.8 points (+1.9 to +3.4); K3.by4: +3.1 points (+1.9 to +4.2); K3.by5: +4.3 points (+3.1 to +5.3); K3.by6: +4.7 points (+3.2 to +5.9); K3.by7: +4.6 points (+3.4 to +6.0); K3.by8: +4.6 points (+3.4 to +6.0); K3.k0: +2.5 points (+1.7 to +3.1); K3.k2: +2.5 points (+1.2 to +4.0); K4: +2.1 points (+1.0 to +3.6); K5: -3.1 points (-3.7 to -2.4).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 4.9% [4-6] | 2.5% [2-3] |
| K3.by3 | 6.6% [6-7] | 5.7% [5-6] | 6.1% [5-7] |
| K3.by4 | 7.4% [6-8] | 8.0% [7-9] | 7.7% [7-8] |
| K3.by5 | 9.5% [8-11] | 11.5% [10-13] | 10.5% [9-12] |
| K3.by6 | 12.9% [11-15] | 14.7% / 18.3% [13-17] | 13.8% / 15.6% [12-16] |
| K3.by7 | 16.1% / 20.0% [13-19] | 16.5% / 24.7% [14-20] | 16.3% / 22.4% [14-19] |
| K3.by8 | 18.0% / 27.3% [15-21] | 17.4% / 26.6% [15-20] | 17.7% / 27.0% [15-21] |
| K3.never | 72.7% / 82.0% [66-79] | 73.4% / 82.6% [67-79] | 73.0% / 82.3% [66-79] |
| K3.k0 | 7.5% / 16.8% [6-8] | 6.0% / 15.2% [5-7] | 6.7% / 16.0% [6-8] |
| K3.k1 | 0.0% / 9.3% [0-0] | 0.0% / 9.2% [0-0] | 0.0% / 9.3% [0-0] |
| K3.k2 | 5.5% / 14.9% [4-7] | 6.8% / 16.0% [5-9] | 6.2% / 15.4% [5-8] |
| K3.k3p | 4.9% / 14.2% [2-8] | 4.7% / 13.9% [2-7] | 4.8% / 14.1% [3-7] |
| K4 | 10.5% / 20.9% [7-14] | 11.5% / 21.5% [9-14] | 11.0% / 21.2% [8-14] |
| K5 | 5.1% / 18.4% [4-6] | 7.8% / 18.7% [7-9] | 6.4% / 18.6% [6-7] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by2: +1.2 points (+1.0 to +1.4); K3.by3: +2.7 points (+2.3 to +3.0); K3.by4: +3.1 points (+2.7 to +3.5); K3.by5: +4.0 points (+3.5 to +4.5); K3.by6: +5.1 points (+4.4 to +5.8); K3.by7: +5.4 points (+4.8 to +6.1); K3.by8: +5.4 points (+4.7 to +6.1); K3.never: -4.0 points (-5.0 to -3.0); K3.k0: +2.6 points (+2.2 to +2.9); K3.k2: +2.8 points (+2.2 to +3.4); K4: +2.8 points (+2.2 to +3.4); K5: -3.2 points (-3.5 to -2.8).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 4.5% [4-5, Wilson] | 2.3% [2-2, Wilson] |
| K3.by4 | 5.3% [5-6, Wilson] | 8.4% [8-9, Wilson] | 6.8% [6-7, Wilson] |
| K3.by5 | 16.6% [16-17, Wilson] | 9.0% [8-10, Wilson] | 12.8% [12-13, Wilson] |
| K3.by6 | 18.8% [18-20, Wilson] | 9.0% [8-10, Wilson] | 13.9% [13-14, Wilson] |
| K3.by7 | 18.8% [18-20, Wilson] | 9.0% [8-10, Wilson] | 13.9% [13-14, Wilson] |
| K3.by8 | 18.8% [18-20, Wilson] | 9.0% [8-10, Wilson] | 13.9% [13-14, Wilson] |
| K3.never | 81.2% [80-82, Wilson] | 91.0% [90-92, Wilson] | 86.1% [86-87, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 5.3% [5-6, Wilson] | 4.5% [4-5, Wilson] | 4.9% [5-5, Wilson] |
| K3.k3p | 13.5% [13-14, Wilson] | 4.5% [4-5, Wilson] | 9.0% [9-9, Wilson] |
| K4 | 18.8% [18-20, Wilson] | 9.0% [8-10, Wilson] | 13.9% [13-14, Wilson] |
| K5 | 12.2% [12-13, Wilson] | 20.1% [19-21, Wilson] | 16.2% [16-17, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.1 points (+0.9 to +1.2); K3.by4: +2.9 points (+2.6 to +3.2); K3.by5: +3.3 points (+2.9 to +3.7); K3.by6: +2.7 points (+2.3 to +3.1); K3.by7: +2.7 points (+2.3 to +3.1); K3.by8: +2.7 points (+2.3 to +3.1); K3.never: -2.7 points (-3.1 to -2.3); K3.k2: +2.5 points (+2.3 to +2.8); K4: +2.7 points (+2.3 to +3.1); K5: -5.6 points (-6.0 to -5.2).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 6.1% [6-7, Wilson] | 3.1% [3-3, Wilson] |
| K3.by3 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.by4 | 7.8% [7-8, Wilson] | 11.4% [11-12, Wilson] | 9.6% [9-10, Wilson] |
| K3.by5 | 11.8% [11-12, Wilson] | 22.6% [22-23, Wilson] | 17.2% [17-18, Wilson] |
| K3.by6 | 32.0% [31-33, Wilson] | 24.8% [24-26, Wilson] | 28.4% [28-29, Wilson] |
| K3.by7 | 35.3% [34-36, Wilson] | 24.8% [24-26, Wilson] | 30.0% [29-31, Wilson] |
| K3.by8 | 35.3% [34-36, Wilson] | 24.8% [24-26, Wilson] | 30.0% [29-31, Wilson] |
| K3.never | 64.7% [64-66, Wilson] | 75.2% [74-76, Wilson] | 70.0% [69-71, Wilson] |
| K3.k0 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.0% [4-4, Wilson] | 5.3% [5-6, Wilson] | 4.7% [4-5, Wilson] |
| K3.k3p | 23.5% [23-24, Wilson] | 13.4% [13-14, Wilson] | 18.4% [18-19, Wilson] |
| K4 | 27.5% [27-28, Wilson] | 18.7% [18-19, Wilson] | 23.1% [23-24, Wilson] |
| K5 | 7.9% [7-8, Wilson] | 11.9% [11-13, Wilson] | 9.9% [9-10, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by2: +1.5 points (+1.3 to +1.7); K3.by3: +3.2 points (+3.0 to +3.5); K3.by4: +4.5 points (+4.2 to +4.8); K3.by5: +6.2 points (+5.7 to +6.7); K3.by6: +6.2 points (+5.7 to +6.8); K3.by7: +5.4 points (+4.8 to +5.9); K3.by8: +5.4 points (+4.8 to +5.9); K3.never: -5.4 points (-5.9 to -4.8); K3.k0: +3.2 points (+3.0 to +3.5); K3.k2: +2.4 points (+2.2 to +2.7); K4: +2.1 points (+1.6 to +2.6); K5: -6.4 points (-6.8 to -6.0).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 6.1% [6-7, Wilson] | 3.1% [3-3, Wilson] |
| K3.by3 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.by4 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.by5 | 7.8% [7-8, Wilson] | 15.6% [15-16, Wilson] | 11.7% [11-12, Wilson] |
| K3.by6 | 15.4% [15-16, Wilson] | 15.9% [15-17, Wilson] | 15.7% [15-16, Wilson] |
| K3.by7 | 15.6% [15-16, Wilson] | 45.2% [44-46, Wilson] | 30.4% [30-31, Wilson] |
| K3.by8 | 55.6% [55-57, Wilson] | 45.3% [44-46, Wilson] | 50.5% [50-51, Wilson] |
| K3.never | 44.4% [43-45, Wilson] | 54.7% [54-56, Wilson] | 49.5% [49-50, Wilson] |
| K3.k0 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 7.8% [7-8, Wilson] | 9.8% [9-10, Wilson] | 8.8% [8-9, Wilson] |
| K3.k3p | 40.0% [39-41, Wilson] | 29.4% [29-30, Wilson] | 34.7% [34-35, Wilson] |
| K4 | 47.8% [47-49, Wilson] | 39.2% [38-40, Wilson] | 43.5% [43-44, Wilson] |
| K5 | 5.5% [5-6, Wilson] | 7.3% [7-8, Wilson] | 6.4% [6-7, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by2: +1.5 points (+1.3 to +1.7); K3.by3: +3.2 points (+3.0 to +3.5); K3.by4: +3.2 points (+3.0 to +3.5); K3.by5: +5.5 points (+5.2 to +5.9); K3.by6: +7.5 points (+7.1 to +8.0); K3.by7: +6.0 points (+5.5 to +6.5); K3.by8: +4.4 points (+3.8 to +5.0); K3.never: -4.4 points (-5.0 to -3.8); K3.k0: +3.2 points (+3.0 to +3.5); K3.k2: +4.3 points (+4.0 to +4.7); K3.k3p: -3.2 points (-3.7 to -2.7); K4: +1.1 points (+0.6 to +1.7); K5: -3.6 points (-3.9 to -3.3).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 4.5% [4-5, Wilson] | 2.3% [2-2, Wilson] |
| K3.by4 | 5.3% [5-6, Wilson] | 8.1% [8-9, Wilson] | 6.7% [6-7, Wilson] |
| K3.by5 | 15.7% [15-16, Wilson] | 8.8% [8-9, Wilson] | 12.2% [12-13, Wilson] |
| K3.by6 | 18.1% [17-19, Wilson] | 8.8% [8-9, Wilson] | 13.4% [13-14, Wilson] |
| K3.by7 | 18.1% [17-19, Wilson] | 8.8% [8-9, Wilson] | 13.4% [13-14, Wilson] |
| K3.by8 | 18.1% [17-19, Wilson] | 8.8% [8-9, Wilson] | 13.4% [13-14, Wilson] |
| K3.never | 81.9% [81-83, Wilson] | 91.2% [91-92, Wilson] | 86.6% [86-87, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 5.3% [5-6, Wilson] | 4.5% [4-5, Wilson] | 4.9% [5-5, Wilson] |
| K3.k3p | 12.8% [12-13, Wilson] | 4.2% [4-5, Wilson] | 8.5% [8-9, Wilson] |
| K4 | 18.1% [17-19, Wilson] | 8.8% [8-9, Wilson] | 13.4% [13-14, Wilson] |
| K5 | 12.2% [12-13, Wilson] | 20.1% [19-21, Wilson] | 16.2% [16-17, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.1 points (+0.9 to +1.2); K3.by4: +2.8 points (+2.5 to +3.1); K3.by5: +3.3 points (+2.8 to +3.7); K3.by6: +2.7 points (+2.2 to +3.1); K3.by7: +2.7 points (+2.2 to +3.1); K3.by8: +2.7 points (+2.2 to +3.1); K3.never: -2.7 points (-3.1 to -2.2); K3.k2: +2.5 points (+2.3 to +2.8); K4: +2.7 points (+2.2 to +3.1); K5: -5.6 points (-6.0 to -5.2).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 6.1% [6-7, Wilson] | 3.1% [3-3, Wilson] |
| K3.by3 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.by4 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.by5 | 7.8% [7-8, Wilson] | 15.6% [15-16, Wilson] | 11.7% [11-12, Wilson] |
| K3.by6 | 15.4% [15-16, Wilson] | 15.9% [15-17, Wilson] | 15.7% [15-16, Wilson] |
| K3.by7 | 15.6% [15-16, Wilson] | 37.1% [36-38, Wilson] | 26.4% [26-27, Wilson] |
| K3.by8 | 46.5% [46-48, Wilson] | 37.2% [36-38, Wilson] | 41.9% [41-43, Wilson] |
| K3.by9 | 46.6% [46-48, Wilson] | 42.8% [42-44, Wilson] | 44.7% [44-45, Wilson] |
| K3.by10 | 51.3% [50-52, Wilson] | 42.9% [42-44, Wilson] | 47.1% [46-48, Wilson] |
| K3.never | 48.7% [48-50, Wilson] | 57.1% [56-58, Wilson] | 52.9% [52-54, Wilson] |
| K3.k0 | 7.8% [7-8, Wilson] | 6.1% [6-7, Wilson] | 7.0% [7-7, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 7.8% [7-8, Wilson] | 9.8% [9-10, Wilson] | 8.8% [8-9, Wilson] |
| K3.k3p | 35.7% [35-37, Wilson] | 26.9% [26-28, Wilson] | 31.3% [31-32, Wilson] |
| K4 | 43.5% [43-45, Wilson] | 36.8% [36-38, Wilson] | 40.1% [39-41, Wilson] |
| K5 | 5.5% [5-6, Wilson] | 7.4% [7-8, Wilson] | 6.4% [6-7, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by2: +1.5 points (+1.3 to +1.7); K3.by3: +3.2 points (+3.0 to +3.5); K3.by4: +3.2 points (+3.0 to +3.5); K3.by5: +5.5 points (+5.2 to +5.9); K3.by6: +7.5 points (+7.1 to +8.0); K3.by7: +6.3 points (+5.8 to +6.8); K3.by8: +4.8 points (+4.2 to +5.4); K3.by9: +4.0 points (+3.4 to +4.6); K3.by10: +3.3 points (+2.7 to +3.9); K3.never: -3.3 points (-3.9 to -2.7); K3.k0: +3.2 points (+3.0 to +3.5); K3.k2: +4.3 points (+4.0 to +4.7); K3.k3p: -4.2 points (-4.7 to -3.8); K5: -3.7 points (-4.0 to -3.4).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard line in play (end of own turn t), own turn 1 | -3.4 (-3.6 to -3.3) FLAG | -3.4 (-3.6 to -3.3) FLAG | -3.4 (-3.6 to -3.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | -4.8 (-5.0 to -4.6) FLAG | -5.0 (-5.2 to -4.8) FLAG | -4.9 (-5.1 to -4.8) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | -4.3 (-4.5 to -4.1) FLAG | -4.6 (-4.8 to -4.4) FLAG | -4.4 (-4.6 to -4.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | -3.6 (-3.8 to -3.4) FLAG | -3.6 (-3.9 to -3.4) FLAG | -3.6 (-3.8 to -3.4) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -2.4 (-2.7 to -2.2) FLAG | -2.4 (-2.6 to -2.1) FLAG | -2.4 (-2.6 to -2.2) FLAG |
| K2 Kingambit in play, own turn 2 | +9.9 (+9.6 to +10.2) FLAG | +9.8 (+9.5 to +10.1) FLAG | +9.8 (+9.6 to +10.1) FLAG |
| K2 Kingambit in play, own turn 3 | +13.0 (+12.7 to +13.4) FLAG | +12.7 (+12.4 to +13.1) FLAG | +12.9 (+12.6 to +13.2) FLAG |
| K2 Kingambit in play, own turn 4 | +14.6 (+14.2 to +15.0) FLAG | +14.2 (+13.8 to +14.6) FLAG | +14.4 (+14.1 to +14.7) FLAG |
| K2 Kingambit in play, own turn 5 | +13.6 (+13.1 to +14.0) FLAG | +13.3 (+12.8 to +13.7) FLAG | +13.4 (+13.1 to +13.7) FLAG |
| K2 Kingambit in play, own turn 6 | +10.3 (+9.9 to +10.7) FLAG | +10.4 (+10.0 to +10.7) FLAG | +10.3 (+10.0 to +10.6) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | -4.8 (-5.0 to -4.6) FLAG | -4.9 (-5.1 to -4.7) FLAG | -4.9 (-5.0 to -4.7) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | -5.4 (-5.7 to -5.2) FLAG | -5.5 (-5.8 to -5.3) FLAG | -5.5 (-5.7 to -5.3) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | -4.8 (-5.0 to -4.5) FLAG | -4.9 (-5.1 to -4.6) FLAG | -4.8 (-5.0 to -4.6) FLAG |
| G3 Pawniard in play, own turn 1 | -3.4 (-3.6 to -3.3) FLAG | -3.4 (-3.6 to -3.3) FLAG | -3.4 (-3.6 to -3.3) FLAG |
| G3 Pawniard in play, own turn 2 | -14.7 (-15.1 to -14.4) FLAG | -14.8 (-15.1 to -14.4) FLAG | -14.8 (-15.0 to -14.5) FLAG |
| G3 Pawniard in play, own turn 3 | -17.4 (-17.8 to -17.0) FLAG | -17.3 (-17.7 to -16.9) FLAG | -17.3 (-17.6 to -17.1) FLAG |
| G3 Pawniard in play, own turn 4 | -18.2 (-18.6 to -17.8) FLAG | -17.9 (-18.3 to -17.4) FLAG | -18.0 (-18.3 to -17.7) FLAG |
| G3 Pawniard in play, own turn 5 | -16.0 (-16.4 to -15.6) FLAG | -15.6 (-16.0 to -15.2) FLAG | -15.8 (-16.1 to -15.5) FLAG |
| G3 Kingambit in play, own turn 2 | +9.9 (+9.6 to +10.2) FLAG | +9.8 (+9.5 to +10.1) FLAG | +9.8 (+9.6 to +10.1) FLAG |
| G3 Kingambit in play, own turn 3 | +13.0 (+12.7 to +13.4) FLAG | +12.7 (+12.4 to +13.1) FLAG | +12.9 (+12.6 to +13.2) FLAG |
| G3 Kingambit in play, own turn 4 | +14.6 (+14.2 to +15.0) FLAG | +14.2 (+13.8 to +14.6) FLAG | +14.4 (+14.1 to +14.7) FLAG |
| G3 Kingambit in play, own turn 5 | +13.6 (+13.1 to +14.0) FLAG | +13.3 (+12.8 to +13.7) FLAG | +13.4 (+13.1 to +13.7) FLAG |
| G3 Alolan Grimer in play, own turn 1 | -3.3 (-3.5 to -3.2) FLAG | -3.4 (-3.5 to -3.2) FLAG | -3.3 (-3.5 to -3.2) FLAG |
| G3 Alolan Grimer in play, own turn 3 | +2.4 (+2.1 to +2.7) FLAG | +2.4 (+2.2 to +2.7) FLAG | +2.4 (+2.2 to +2.6) FLAG |
| G3 Alolan Grimer in play, own turn 4 | +4.3 (+4.0 to +4.5) FLAG | +4.4 (+4.2 to +4.7) FLAG | +4.4 (+4.2 to +4.5) FLAG |
| G3 Alolan Grimer in play, own turn 5 | +4.6 (+4.3 to +4.8) FLAG | +4.5 (+4.3 to +4.8) FLAG | +4.6 (+4.4 to +4.7) FLAG |
| G3 Alolan Muk in play, own turn 2 | -3.6 (-3.8 to -3.5) FLAG | -3.7 (-3.9 to -3.5) FLAG | -3.7 (-3.8 to -3.5) FLAG |
| G3 Alolan Muk in play, own turn 3 | -5.8 (-6.0 to -5.5) FLAG | -6.0 (-6.3 to -5.8) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| G3 Alolan Muk in play, own turn 4 | -6.5 (-6.8 to -6.2) FLAG | -6.8 (-7.0 to -6.5) FLAG | -6.6 (-6.8 to -6.4) FLAG |
| G3 Alolan Muk in play, own turn 5 | -5.9 (-6.1 to -5.6) FLAG | -5.9 (-6.2 to -5.6) FLAG | -5.9 (-6.1 to -5.7) FLAG |
| G3 Glimmet in play, own turn 1 | -3.3 (-3.5 to -3.2) FLAG | -3.5 (-3.7 to -3.3) FLAG | -3.4 (-3.5 to -3.3) FLAG |
| G3 Glimmet in play, own turn 3 | +4.1 (+3.8 to +4.5) FLAG | +4.0 (+3.7 to +4.4) FLAG | +4.1 (+3.8 to +4.3) FLAG |
| G3 Glimmet in play, own turn 4 | +6.6 (+6.3 to +6.9) FLAG | +6.5 (+6.1 to +6.8) FLAG | +6.5 (+6.3 to +6.8) FLAG |
| G3 Glimmet in play, own turn 5 | +7.5 (+7.2 to +7.8) FLAG | +7.6 (+7.3 to +7.9) FLAG | +7.6 (+7.3 to +7.8) FLAG |
| G3 Glimmora in play, own turn 2 | -7.1 (-7.4 to -6.9) FLAG | -7.2 (-7.5 to -7.0) FLAG | -7.2 (-7.4 to -7.0) FLAG |
| G3 Glimmora in play, own turn 3 | -7.6 (-7.9 to -7.3) FLAG | -7.5 (-7.8 to -7.3) FLAG | -7.6 (-7.7 to -7.4) FLAG |
| G3 Glimmora in play, own turn 4 | -5.9 (-6.2 to -5.7) FLAG | -6.0 (-6.2 to -5.8) FLAG | -6.0 (-6.1 to -5.8) FLAG |
| G3 Glimmora in play, own turn 5 | -3.9 (-4.1 to -3.8) FLAG | -4.0 (-4.2 to -3.8) FLAG | -4.0 (-4.1 to -3.8) FLAG |
| G3 Regigigas in play, own turn 1 | -3.4 (-3.6 to -3.2) FLAG | -3.5 (-3.7 to -3.4) FLAG | -3.5 (-3.6 to -3.3) FLAG |
| G3 Regigigas in play, own turn 2 | -4.3 (-4.6 to -4.1) FLAG | -4.2 (-4.5 to -4.0) FLAG | -4.3 (-4.4 to -4.1) FLAG |
| G3 Regigigas in play, own turn 3 | -3.8 (-4.0 to -3.5) FLAG | -3.7 (-3.9 to -3.4) FLAG | -3.7 (-3.9 to -3.6) FLAG |
| G3 Regigigas in play, own turn 4 | -2.5 (-2.7 to -2.2) FLAG | -2.7 (-2.9 to -2.5) FLAG | -2.6 (-2.7 to -2.4) FLAG |
| G3 Regigigas in play, own turn 5 | -1.3 (-1.6 to -1.1) FLAG | -1.5 (-1.7 to -1.2) FLAG | -1.4 (-1.6 to -1.3) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | -1.6 (-1.9 to -1.3) FLAG | -1.6 (-1.9 to -1.3) FLAG | -1.6 (-1.8 to -1.4) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | -1.6 (-1.8 to -1.3) FLAG | -1.8 (-2.0 to -1.6) FLAG | -1.7 (-1.8 to -1.5) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | -1.1 (-1.2 to -0.9) FLAG | -1.0 (-1.2 to -0.9) FLAG | -1.0 (-1.2 to -0.9) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | +9.9 (+9.6 to +10.2) FLAG | +9.8 (+9.5 to +10.1) FLAG | +9.8 (+9.6 to +10.1) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | +13.0 (+12.7 to +13.4) FLAG | +12.7 (+12.4 to +13.1) FLAG | +12.9 (+12.6 to +13.2) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +14.6 (+14.2 to +15.0) FLAG | +14.2 (+13.8 to +14.6) FLAG | +14.4 (+14.1 to +14.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +13.6 (+13.1 to +14.0) FLAG | +13.3 (+12.8 to +13.7) FLAG | +13.4 (+13.1 to +13.7) FLAG |
| G5.any3 an empty own turn among turns 1-3 | +4.7 (+4.4 to +5.0) FLAG | +5.0 (+4.7 to +5.3) FLAG | +4.8 (+4.6 to +5.1) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | +9.8 (+9.5 to +10.1) FLAG | +4.9 (+4.7 to +5.0) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +12.3 (+12.0 to +12.7) FLAG | +12.7 (+12.4 to +13.1) FLAG | +12.5 (+12.3 to +12.8) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +14.6 (+14.2 to +15.0) FLAG | +14.2 (+13.8 to +14.6) FLAG | +14.4 (+14.1 to +14.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +13.6 (+13.1 to +14.0) FLAG | +13.3 (+12.8 to +13.7) FLAG | +13.4 (+13.1 to +13.7) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled +0.049 (+0.044 to +0.053) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, A2.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): none flagged
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn -5.0 points (-6.8 to -3.5); P2 both Glimmora had their turn -8.1 points (-10.1 to -5.9); P2 the first Glimmora placed had its turn -5.1 points (-6.3 to -3.9); P2 the second Glimmora placed had its turn -8.0 points (-10.0 to -5.8); P4 ready at the winning moment: Knocks out their strongest +1.7 points (+0.0 to +3.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.1 points (+1.7 to +4.6)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn -5.0 points (-6.4 to -3.6); P2 both Glimmora had their turn -8.6 points (-10.7 to -6.6); P2 the first Glimmora placed had its turn -5.2 points (-6.3 to -4.0); P2 the second Glimmora placed had its turn -8.4 points (-10.4 to -6.5); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +1.1 points (+0.3 to +2.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) +1.4 points (+0.6 to +2.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +4.0 points (+1.6 to +5.9)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn -5.8 points (-6.3 to -5.2); P2 both Glimmora had their turn -9.1 points (-10.1 to -8.0); P2 the first Glimmora placed had its turn -5.3 points (-5.8 to -4.8); P2 the second Glimmora placed had its turn -9.6 points (-10.5 to -8.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +1.9 points (+1.3 to +2.4); P4 ready at the winning moment: Knocks out their strongest +1.4 points (+0.6 to +2.1); P4 the moment came and Kingambit was never ready in the deal -1.0 points (-1.8 to -0.5); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +1.5 points (+0.9 to +2.2)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn -8.8 points (-9.2 to -8.4); P2 both Glimmora had their turn -6.8 points (-7.2 to -6.4); P2 the first Glimmora placed had its turn -6.6 points (-7.0 to -6.2); P2 the second Glimmora placed had its turn -9.1 points (-9.6 to -8.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.3 points (-3.7 to -2.8); P4 the moment came and Kingambit was never ready in the deal -7.5 points (-7.9 to -7.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +7.8 points (+7.4 to +8.2)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn -7.0 points (-7.4 to -6.7); P2 both Glimmora had their turn -11.0 points (-11.6 to -10.5); P2 the first Glimmora placed had its turn -6.7 points (-7.0 to -6.3); P2 the second Glimmora placed had its turn -11.4 points (-12.0 to -10.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.4 points (-3.0 to -1.9); P4 not ready, ready 1 turn late -1.1 points (-1.3 to -0.9); P4 the moment came and Kingambit was never ready in the deal -7.4 points (-7.9 to -6.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +8.6 points (+8.2 to +9.0); P5 plan reached in time: Knocks out their strongest -1.2 points (-1.7 to -0.7)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn -5.4 points (-5.8 to -5.1); P2 both Glimmora had their turn -13.5 points (-14.1 to -13.0); P2 the first Glimmora placed had its turn -6.0 points (-6.3 to -5.6); P2 the second Glimmora placed had its turn -13.0 points (-13.6 to -12.4); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted by the order list (Bisharp and an unready Kingambit come before Grimer and Muk; Pawniard last) +4.0 points (+3.6 to +4.4); P4 ready at the winning moment: Knocks out their strongest -5.6 points (-6.1 to -5.1); P4 ready at the winning moment: Wins outright (a lower bound) -5.6 points (-6.1 to -5.1); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +7.2 points (+6.8 to +7.6); P5 plan reached in time: Knocks out their strongest -6.5 points (-6.9 to -6.0); P5 plan reached in time: Wins outright (a lower bound) -6.5 points (-6.9 to -6.0)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn -8.8 points (-9.2 to -8.4); P2 both Glimmora had their turn -6.9 points (-7.3 to -6.5); P2 the first Glimmora placed had its turn -6.6 points (-7.0 to -6.2); P2 the second Glimmora placed had its turn -9.1 points (-9.5 to -8.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.3 points (-3.7 to -2.8); P4 the moment came and Kingambit was never ready in the deal -1.2 points (-1.4 to -1.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +2.0 points (+1.7 to +2.2)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn -5.4 points (-5.7 to -5.1); P2 both Glimmora had their turn -13.1 points (-13.6 to -12.5); P2 the first Glimmora placed had its turn -6.0 points (-6.3 to -5.6); P2 the second Glimmora placed had its turn -12.5 points (-13.1 to -12.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.1 points (-2.6 to -1.6); P4 ready at the winning moment: Knocks out their strongest -1.4 points (-1.7 to -1.2); P4 ready at the winning moment: Wins outright (a lower bound) -1.4 points (-1.7 to -1.2); P4 the moment came and Kingambit was never ready in the deal -1.6 points (-1.9 to -1.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) +3.1 points (+2.8 to +3.4); P5 plan reached in time: Knocks out their strongest -1.5 points (-1.8 to -1.2); P5 plan reached in time: Wins outright (a lower bound) -1.5 points (-1.8 to -1.2)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K2 Kingambit in play, own turn 2 +9.8 points; K2 Kingambit in play, own turn 3 +12.9 points; K2 Kingambit in play, own turn 4 +14.4 points; K2 Kingambit in play, own turn 5 +13.4 points; K2 Kingambit in play, own turn 6 +10.3 points; G3 Kingambit in play, own turn 2 +9.8 points; G3 Kingambit in play, own turn 3 +12.9 points; G3 Kingambit in play, own turn 4 +14.4 points; G3 Kingambit in play, own turn 5 +13.4 points; G3 Alolan Grimer in play, own turn 3 +2.4 points.
Gives up (flagged, pooled): K1 Pawniard line in play (end of own turn t), own turn 1 -3.4 points; K1 Pawniard line in play (end of own turn t), own turn 2 -4.9 points; K1 Pawniard line in play (end of own turn t), own turn 3 -4.4 points; K1 Pawniard line in play (end of own turn t), own turn 4 -3.6 points; K1 Pawniard line in play (end of own turn t), own turn 5 -2.4 points; K6 Muk and Regigigas both in play, own turn 3 -4.9 points; K6 Muk and Regigigas both in play, own turn 4 -5.5 points; K6 Muk and Regigigas both in play, own turn 5 -4.8 points; G3 Alolan Muk in play, own turn 2 -3.7 points; G3 Alolan Muk in play, own turn 3 -5.9 points.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by2 +1.1; K3.by3 +2.5; K3.by4 +3.1; K3.by5 +4.1; K3.by6 +4.7; K3.by7 +4.7; K3.by8 +4.8; K3.k0 +2.4; K3.k2 +2.6; K4 +2.4; K5 -2.7; C-his, seat-matched: K3.by3 +2.8; K3.by4 +3.1; K3.by5 +4.3; K3.by6 +4.7; K3.by7 +4.6; K3.by8 +4.6; K3.k0 +2.5; K3.k2 +2.5; K4 +2.1; K5 -3.1; C-bot: K3.by2 +1.2; K3.by3 +2.7; K3.by4 +3.1; K3.by5 +4.0; K3.by6 +5.1; K3.by7 +5.4; K3.by8 +5.4; K3.never -4.0; K3.k0 +2.6; K3.k2 +2.8; K4 +2.8; K5 -3.2; C-fixed fast: K3.by3 +1.1; K3.by4 +2.9; K3.by5 +3.3; K3.by6 +2.7; K3.by7 +2.7; K3.by8 +2.7; K3.never -2.7; K3.k2 +2.5; K4 +2.7; K5 -5.6; C-fixed medium: K3.by2 +1.5; K3.by3 +3.2; K3.by4 +4.5; K3.by5 +6.2; K3.by6 +6.2; K3.by7 +5.4; K3.by8 +5.4; K3.never -5.4; K3.k0 +3.2; K3.k2 +2.4; K4 +2.1; K5 -6.4; C-fixed slow: K3.by2 +1.5; K3.by3 +3.2; K3.by4 +3.2; K3.by5 +5.5; K3.by6 +7.5; K3.by7 +6.0; K3.by8 +4.4; K3.never -4.4; K3.k0 +3.2; K3.k2 +4.3; K3.k3p -3.2; K4 +1.1; K5 -3.6; C-fixed reference (fast pace, 190-HP Mega ex): K3.by3 +1.1; K3.by4 +2.8; K3.by5 +3.3; K3.by6 +2.7; K3.by7 +2.7; K3.by8 +2.7; K3.never -2.7; K3.k2 +2.5; K4 +2.7; K5 -5.6; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by2 +1.5; K3.by3 +3.2; K3.by4 +3.2; K3.by5 +5.5; K3.by6 +7.5; K3.by7 +6.3; K3.by8 +4.8; K3.by9 +4.0; K3.by10 +3.3; K3.never -3.3; K3.k0 +3.2; K3.k2 +4.3; K3.k3p -4.2; K5 -3.7.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
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
- **wall time**: 539 s, 8 process(es) (every version under both Copycat rules, and the choice runs, included)
- **speed**: 2,065 deals per second per process (1,560,000 deals in 756 s of version time)

