# Setup tester: journal_fixture

Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on the same deals for every version. It does not say who wins.
**Plan config follows SPEC_AMENDMENT_1 (Dustin, Oct 15) and the coordinator's rulings R1-R3 (Oct 15):** Regigigas leads; Pawniard is held until the bench trigger (first_ko; default first_ko = our first turn after one of ours was knocked out, a spot free); Grimer and Muk are benched, and an Active Alolan Grimer is never evolved into Muk (R2); a Glimmora has had its turn when it attacked at least once (R1); Energy goes to Kingambit up to [DD], then an Active Glimmora with no [D], then the Pawniard line up to [DD], then Regigigas while Muk is in play (R1; the other order runs as a choices row). The lines that lead are P1-P5, P3 by cause (R2); the old G and K lines stay below "descriptive (speed is not the goal)". The slow pace is knockouts on their turns 3, 5 and 7 against a 180-HP Mega ex; the 220-HP Mega is a reference row with 10 own turns (R3). The no-knock-out runs have no knock-out to trigger first_ko, so Pawniard is benched at once (trigger "at_once") and no Bench slot is reserved; the old T-now reserved one.
**Copycat is played by his valuation, approximated** (Dustin, Oct 15: "an updated approximate valuation of card values, based on what I have in play, what cards are left in the deck, how many cards I have, they have, and whether a shuffle and new hand is likely to be more valuable to winning than keeping my current hand"): it is played when the expected value of a fresh hand beats the current hand's value under the value table below. A fresh hand is the opponent's hand count of cards from deck plus hand reshuffled, estimated from 16 sampled hands per decision drawn from the tester's own seed block. The value table is written from the plan's own needs, with no tuned constants; Dustin can correct a value.
**His rule, approximated, as a check:** the fallback rule runs on the base and on every version. The two disagree at base: 4,695 of 10,597 Copycat decisions (44.3%).
**WARNING, the Copycat rule changes a verdict:** deck01: bot P2.both + only under the valuation, bot P2.g2 + only under the valuation, bot P4.ko + only under the valuation, bot P5.ko + only under the valuation, fast P2.both + only under the valuation, fast P2.g1 + only under the valuation, his P2.any + only under the valuation, his P2.both + only under the valuation, his P2.g1 + only under the valuation, his P2.g2 + only under the valuation, his P4.nomoment - only under the valuation, his_seat P2.both + only under the valuation, his_seat P2.g2 + only under the valuation, his_seat P3.grimer_muk - only under the valuation, medium P2.any + only under the valuation, medium P2.both + only under the valuation, medium P2.g2 + only under the valuation, medium P3.pawn_promo + only under the valuation, medium P4.ko + only under the valuation, medium P5.ko + only under the valuation, ref190 P2.both + only under the valuation, ref190 P2.g1 + only under the valuation, ref190 P3.pawn_promo + only under the fallback rule, ref190 P4.nomoment - only under the valuation, ref220 P2.any + only under the valuation, ref220 P2.both + only under the valuation, ref220 P2.g1 + only under the valuation, ref220 P2.g2 + only under the valuation, ref220 P3.grimer_muk - only under the valuation, ref220 P3.pawn_promo + only under the valuation, ref220 P4.never + only under the valuation, ref220 P4.nomoment - only under the valuation, slow P2.any + only under the valuation, slow P2.both + only under the valuation, slow P2.g1 + only under the valuation, slow P2.g2 + only under the valuation, slow P3.grimer_muk - only under the valuation, slow P3.pawn_promo - only under the valuation, slow P4.ko + only under the valuation, slow P4.late1 - only under the valuation, slow P4.nomoment - only under the valuation, slow P4.win + only under the valuation, slow P5.ko + only under the valuation, slow P5.win + only under the valuation; B: bot P2.both + only under the valuation, bot P2.g1 + only under the valuation, bot P2.g2 + only under the valuation, bot P4.late2p - only under the valuation, fast P2.any + only under the valuation, fast P2.both + only under the valuation, fast P2.both - only under the fallback rule, fast P2.g1 + only under the valuation, fast P2.g2 + only under the valuation, fast P4.nomoment - only under the valuation, his P2.any + only under the valuation, his P2.both - only under the fallback rule, his P2.g1 + only under the valuation, his P2.g2 - only under the fallback rule, his P4.nomoment - only under the valuation, his_seat P2.any + only under the valuation, his_seat P2.both + only under the valuation, his_seat P2.g1 + only under the valuation, his_seat P2.g2 + only under the valuation, his_seat P4.nomoment - only under the valuation, medium P2.any + only under the valuation, medium P2.both + only under the valuation, medium P2.both - only under the fallback rule, medium P2.g1 + only under the valuation, medium P2.g2 - only under the fallback rule, medium P4.nomoment - only under the valuation, ref190 P2.any + only under the valuation, ref190 P2.both + only under the valuation, ref190 P2.g1 + only under the valuation, ref190 P2.g2 + only under the valuation, ref190 P4.nomoment - only under the valuation, ref220 P2.any + only under the valuation, ref220 P2.both + only under the valuation, ref220 P2.g1 + only under the valuation, ref220 P2.g2 + only under the valuation, ref220 P4.nomoment - only under the valuation, slow P2.any + only under the valuation, slow P2.both + only under the valuation, slow P2.g1 + only under the valuation, slow P2.g2 + only under the valuation, slow P3.pawn_promo - only under the valuation, slow P4.late1 - only under the valuation, slow P4.nomoment - only under the valuation; C: bot P2.any + only under the valuation, bot P2.both + only under the valuation, bot P2.both - only under the fallback rule, bot P2.g1 + only under the valuation, bot P2.g2 + only under the valuation, bot P2.g2 - only under the fallback rule, bot P3.pawn_promo + only under the valuation, bot P4.late2p - only under the valuation, fast P2.any + only under the valuation, fast P2.both + only under the valuation, fast P2.g1 + only under the valuation, fast P2.g2 + only under the valuation, fast P4.nomoment - only under the valuation, his P2.any + only under the valuation, his P2.both + only under the valuation, his P2.both - only under the fallback rule, his P2.g1 + only under the valuation, his P2.g2 - only under the fallback rule, his P4.nomoment - only under the valuation, his_seat P2.any + only under the valuation, his_seat P2.both + only under the valuation, his_seat P2.g1 + only under the valuation, his_seat P2.g2 + only under the valuation, his_seat P4.nomoment - only under the valuation, medium P2.any + only under the valuation, medium P2.both + only under the valuation, medium P2.both - only under the fallback rule, medium P2.g1 + only under the valuation, medium P2.g2 - only under the fallback rule, medium P3.pawn_promo + only under the valuation, medium P4.nomoment - only under the valuation, ref190 P2.any + only under the valuation, ref190 P2.both + only under the valuation, ref190 P2.g1 + only under the valuation, ref190 P2.g2 + only under the valuation, ref190 P4.nomoment - only under the valuation, ref220 P2.any + only under the valuation, ref220 P2.both + only under the valuation, ref220 P2.g1 + only under the valuation, ref220 P2.g2 + only under the valuation, ref220 P4.ko - only under the valuation, ref220 P4.nomoment - only under the valuation, ref220 P4.win - only under the valuation, ref220 P5.ko - only under the valuation, ref220 P5.win - only under the valuation, slow P2.any + only under the valuation, slow P2.both + only under the valuation, slow P2.g1 + only under the valuation, slow P2.g2 + only under the valuation, slow P3.pawn_promo - only under the valuation, slow P4.late1 - only under the valuation, slow P4.nomoment - only under the valuation. The laptop shows Dustin one such hand.
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

Copycat decisions with a Copycat in hand: 10,597; the valuation and the fallback rule disagree at 4,695 of 10,597 Copycat decisions (44.3%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.2371.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03373; in 8 cards: 0.05246.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 2,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 30.1% (27.3-33.0) | 28.2% (25.5-31.1) | 29.1% (27.2-31.2) |

Plan lines under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.6% / 93.8% [74-95] | 81.6% / 92.0% [66-93] | 83.6% / 92.9% [70-93] |
| P2 both Glimmora had their turn | 39.0% / 72.0% [29-48] | 36.2% / 71.6% [22-53] | 37.6% / 71.8% [27-49] |
| P2 the first Glimmora placed had its turn | 82.8% / 90.0% [71-92] | 75.0% / 83.6% [58-89] | 78.9% / 86.8% [65-91] |
| P2 the second Glimmora placed had its turn | 41.8% / 70.2% [31-52] | 42.8% / 71.4% [28-59] | 42.3% / 70.8% [30-54] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [12-16] | 10.0% [9-11] | 11.9% [11-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 7.4% / 54.4% [2-15] | 7.4% / 52.2% [3-12] | 7.4% / 53.3% [3-13] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 24.6% / 64.4% [18-32] | 34.6% / 68.8% [27-43] | 29.6% / 66.6% [23-37] |
| P4 ready at the winning moment: Knocks out their strongest | 13.6% / 40.6% [3-27] | 10.4% / 36.0% [2-21] | 12.0% / 38.3% [2-24] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.0% / 29.0% [0-6] | 1.4% / 27.0% [0-4] | 1.7% / 28.0% [0-5] |
| P4 not ready, ready 1 turn late | 4.6% / 48.4% [0-12] | 3.8% / 46.2% [0-9] | 4.2% / 47.3% [0-10] |
| P4 not ready, ready 2 or more turns late | 1.4% / 45.2% [0-4] | 1.4% / 43.8% [0-4] | 1.4% / 44.5% [0-4] |
| P4 the moment came and Kingambit was never ready in the deal | 8.6% / 52.4% [0-20] | 9.0% / 51.4% [0-22] | 8.8% / 51.9% [0-21] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.0% / 55.0% [9-53] | 33.0% / 58.6% [12-57] | 30.5% / 56.8% [10-54] |
| P5 plan reached in time: Knocks out their strongest | 19.6% / 63.4% [6-35] | 15.6% / 58.0% [5-28] | 17.6% / 60.7% [6-31] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.2% / 46.0% [0-7] | 1.8% / 44.2% [0-6] | 2.0% / 45.1% [0-6] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 48.2% of 141 [26-69] | 42.3% of 123 [16-66] | 45.5% of 264 [23-67] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 7.1% of 141 [0-31] | 5.7% of 123 [0-29] | 6.4% of 264 [0-31] |
| P4 not ready, ready 1 turn late | 16.3% of 141 [0-54] | 15.4% of 123 [0-48] | 15.9% of 264 [0-51] |
| P4 not ready, ready 2 or more turns late | 5.0% of 141 [0-18] | 5.7% of 123 [0-22] | 5.3% of 264 [0-18] |
| P4 the moment came and Kingambit was never ready in the deal | 30.5% of 141 [0-56] | 36.6% of 123 [0-66] | 33.3% of 264 [0-60] |

Plan lines under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.8% / 95.8% [72-96] | 89.4% / 94.4% [81-97] | 88.1% / 95.1% [80-94] |
| P2 both Glimmora had their turn | 39.2% / 69.6% [25-53] | 32.6% / 80.4% [23-43] | 35.9% / 75.0% [27-45] |
| P2 the first Glimmora placed had its turn | 83.6% / 92.0% [70-94] | 84.6% / 85.8% [76-96] | 84.1% / 88.9% [76-92] |
| P2 the second Glimmora placed had its turn | 42.4% / 67.2% [27-56] | 37.4% / 75.8% [28-52] | 39.9% / 71.5% [30-50] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-16] | 10.0% [9-11] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 2.4% / 46.2% [1-4] | 11.6% / 76.6% [0-25] | 7.0% / 61.4% [1-14] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 25.4% / 61.8% [17-34] | 35.6% / 87.2% [19-46] | 30.5% / 74.5% [21-38] |
| P4 ready at the winning moment: Knocks out their strongest | 18.8% / 42.8% [3-35] | 4.8% / 59.4% [0-17] | 11.8% / 51.1% [3-24] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 5.0% / 29.0% [0-15] | 0.0% / 54.6% [0-0] | 2.5% / 41.8% [0-9] |
| P4 not ready, ready 1 turn late | 6.2% / 43.8% [0-16] | 0.0% / 75.0% [0-0] | 3.1% / 59.4% [0-9] |
| P4 not ready, ready 2 or more turns late | 1.8% / 39.4% [0-6] | 0.0% / 75.0% [0-0] | 0.9% / 57.2% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 9.8% / 47.4% [0-22] | 0.0% / 75.0% [0-0] | 4.9% / 61.2% [0-12] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 25.8% / 49.8% [7-54] | 20.2% / 74.8% [1-47] | 23.0% / 62.3% [7-42] |
| P5 plan reached in time: Knocks out their strongest | 26.8% / 64.4% [8-46] | 4.8% / 79.8% [0-17] | 15.8% / 72.1% [5-32] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.4% / 43.0% [0-17] | 0.0% / 75.0% [0-0] | 2.7% / 59.0% [0-10] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 51.4% of 183 [21-69] | 100.0% of 24 [100-100] | 57.0% of 207 [34-79] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 13.7% of 183 [0-47] | 0.0% of 24 [0-0] | 12.1% of 207 [0-40] |
| P4 not ready, ready 1 turn late | 16.9% of 183 [0-60] | 0.0% of 24 [0-0] | 15.0% of 207 [0-43] |
| P4 not ready, ready 2 or more turns late | 4.9% of 183 [0-19] | 0.0% of 24 [0-0] | 4.3% of 207 [0-13] |
| P4 the moment came and Kingambit was never ready in the deal | 26.8% of 183 [0-48] | 0.0% of 24 [0-0] | 23.7% of 207 [0-42] |

Plan lines under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.8% / 92.2% [88-95] | 85.6% / 86.6% [82-89] | 88.7% / 89.4% [85-92] |
| P2 both Glimmora had their turn | 39.2% / 45.6% [33-46] | 31.8% / 37.2% [26-38] | 35.5% / 41.4% [30-41] |
| P2 the first Glimmora placed had its turn | 86.2% / 86.4% [81-91] | 74.8% / 75.0% [68-81] | 80.5% / 80.7% [75-85] |
| P2 the second Glimmora placed had its turn | 44.8% / 49.2% [39-50] | 42.6% / 46.6% [37-48] | 43.7% / 47.9% [39-48] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17] | 10.0% [8-12] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 16.2% / 28.0% [11-22] | 14.4% / 24.2% [11-18] | 15.3% / 26.1% [11-20] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 35.0% / 44.8% [30-40] | 47.0% / 53.6% [42-52] | 41.0% / 49.2% [37-45] |
| P4 ready at the winning moment: Knocks out their strongest | 7.4% / 14.0% [3-12] | 5.6% / 12.8% [2-9] | 6.5% / 13.4% [3-10] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.6% / 7.2% [0-2] | 0.2% / 7.4% [0-1] | 0.4% / 7.3% [0-1] |
| P4 not ready, ready 1 turn late | 5.0% / 13.6% [2-9] | 5.0% / 14.0% [2-8] | 5.0% / 13.8% [2-8] |
| P4 not ready, ready 2 or more turns late | 1.8% / 10.4% [0-4] | 2.2% / 11.2% [1-4] | 2.0% / 10.8% [1-4] |
| P4 the moment came and Kingambit was never ready in the deal | 10.0% / 18.6% [5-16] | 6.6% / 15.6% [3-11] | 8.3% / 17.1% [4-13] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 67.2% / 73.8% [54-79] | 71.6% / 78.8% [60-82] | 69.4% / 76.3% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 14.2% / 22.8% [7-22] | 12.8% / 21.8% [7-20] | 13.5% / 22.3% [7-20] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.6% / 9.2% [0-2] | 0.2% / 9.2% [0-1] | 0.4% / 9.2% [0-1] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 30.6% of 121 [17-46] | 28.9% of 97 [18-40] | 29.8% of 218 [20-41] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.5% of 121 [0-9] | 1.0% of 97 [0-4] | 1.8% of 218 [0-6] |
| P4 not ready, ready 1 turn late | 20.7% of 121 [10-32] | 25.8% of 97 [15-38] | 22.9% of 218 [14-31] |
| P4 not ready, ready 2 or more turns late | 7.4% of 121 [2-14] | 11.3% of 97 [4-20] | 9.2% of 218 [4-16] |
| P4 the moment came and Kingambit was never ready in the deal | 41.3% of 121 [25-57] | 34.0% of 97 [20-48] | 38.1% of 218 [25-51] |

Plan lines under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 80.0% [76-83, Wilson] | 52.2% [48-57, Wilson] | 66.1% [63-69, Wilson] |
| P2 both Glimmora had their turn | 27.4% [24-31, Wilson] | 7.4% [5-10, Wilson] | 17.4% [15-20, Wilson] |
| P2 the first Glimmora placed had its turn | 74.6% [71-78, Wilson] | 31.2% [27-35, Wilson] | 52.9% [50-56, Wilson] |
| P2 the second Glimmora placed had its turn | 32.8% [29-37, Wilson] | 28.4% [25-33, Wilson] | 30.6% [28-34, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 17.6% [15-21, Wilson] | 18.8% [16-22, Wilson] | 18.2% [16-21, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 55.6% [51-60, Wilson] | 54.4% [50-59, Wilson] | 55.0% [52-58, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 16.4% [13-20, Wilson] | 4.0% [3-6, Wilson] | 10.2% [8-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 16.4% [13-20, Wilson] | 4.0% [3-6, Wilson] | 10.2% [8-12, Wilson] |
| P4 not ready, ready 1 turn late | 1.8% [1-3, Wilson] | 0.4% [0-1, Wilson] | 1.1% [1-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 21.6% [18-25, Wilson] | 16.4% [13-20, Wilson] | 19.0% [17-22, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 60.2% [56-64, Wilson] | 79.2% [75-83, Wilson] | 69.7% [67-72, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 18.2% [15-22, Wilson] | 4.4% [3-7, Wilson] | 11.3% [9-13, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 18.2% [15-22, Wilson] | 4.4% [3-7, Wilson] | 11.3% [9-13, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 41.2% of 199 [35-48, Wilson] | 19.2% of 104 [13-28, Wilson] | 33.7% of 303 [29-39, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 41.2% of 199 [35-48, Wilson] | 19.2% of 104 [13-28, Wilson] | 33.7% of 303 [29-39, Wilson] |
| P4 not ready, ready 1 turn late | 4.5% of 199 [2-8, Wilson] | 1.9% of 104 [1-7, Wilson] | 3.6% of 303 [2-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 199 [0-2, Wilson] | 0.0% of 104 [0-4, Wilson] | 0.0% of 303 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 54.3% of 199 [47-61, Wilson] | 78.8% of 104 [70-86, Wilson] | 62.7% of 303 [57-68, Wilson] |

Plan lines under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.2% [86-92, Wilson] | 82.2% [79-85, Wilson] | 85.7% [83-88, Wilson] |
| P2 both Glimmora had their turn | 38.8% [35-43, Wilson] | 27.6% [24-32, Wilson] | 33.2% [30-36, Wilson] |
| P2 the first Glimmora placed had its turn | 85.4% [82-88, Wilson] | 78.2% [74-82, Wilson] | 81.8% [79-84, Wilson] |
| P2 the second Glimmora placed had its turn | 42.6% [38-47, Wilson] | 31.6% [28-36, Wilson] | 37.1% [34-40, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 22.0% [19-26, Wilson] | 22.4% [19-26, Wilson] | 22.2% [20-25, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 50.8% [46-55, Wilson] | 56.8% [52-61, Wilson] | 53.8% [51-57, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 24.8% [21-29, Wilson] | 15.8% [13-19, Wilson] | 20.3% [18-23, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.6% [2-4, Wilson] | 1.6% [1-3, Wilson] | 2.1% [1-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 22.6% [19-26, Wilson] | 21.8% [18-26, Wilson] | 22.2% [20-25, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 50.0% [46-54, Wilson] | 60.8% [56-65, Wilson] | 55.4% [52-58, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 27.4% [24-31, Wilson] | 17.4% [14-21, Wilson] | 22.4% [20-25, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 49.6% of 250 [43-56, Wilson] | 40.3% of 196 [34-47, Wilson] | 45.5% of 446 [41-50, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 250 [0-2, Wilson] | 0.0% of 196 [0-2, Wilson] | 0.0% of 446 [0-1, Wilson] |
| P4 not ready, ready 1 turn late | 5.2% of 250 [3-9, Wilson] | 4.1% of 196 [2-8, Wilson] | 4.7% of 446 [3-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 250 [0-2, Wilson] | 0.0% of 196 [0-2, Wilson] | 0.0% of 446 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 45.2% of 250 [39-51, Wilson] | 55.6% of 196 [49-62, Wilson] | 49.8% of 446 [45-54, Wilson] |

Plan lines under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 94.8% [92-96, Wilson] | 90.2% [87-93, Wilson] | 92.5% [91-94, Wilson] |
| P2 both Glimmora had their turn | 68.2% [64-72, Wilson] | 55.6% [51-60, Wilson] | 61.9% [59-65, Wilson] |
| P2 the first Glimmora placed had its turn | 89.8% [87-92, Wilson] | 81.6% [78-85, Wilson] | 85.7% [83-88, Wilson] |
| P2 the second Glimmora placed had its turn | 73.2% [69-77, Wilson] | 64.2% [60-68, Wilson] | 68.7% [66-71, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 5.4% [4-8, Wilson] | 9.2% [7-12, Wilson] | 7.3% [6-9, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 28.4% [25-33, Wilson] | 39.6% [35-44, Wilson] | 34.0% [31-37, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 48.4% [44-53, Wilson] | 38.8% [35-43, Wilson] | 43.6% [41-47, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 48.4% [44-53, Wilson] | 38.8% [35-43, Wilson] | 43.6% [41-47, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 3.6% [2-6, Wilson] | 1.8% [1-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 13.4% [11-17, Wilson] | 10.8% [8-14, Wilson] | 12.1% [10-14, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 38.2% [34-43, Wilson] | 46.8% [42-51, Wilson] | 42.5% [39-46, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 48.4% [44-53, Wilson] | 42.4% [38-47, Wilson] | 45.4% [42-48, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 48.4% [44-53, Wilson] | 42.4% [38-47, Wilson] | 45.4% [42-48, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 78.3% of 309 [73-83, Wilson] | 72.9% of 266 [67-78, Wilson] | 75.8% of 575 [72-79, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 78.3% of 309 [73-83, Wilson] | 72.9% of 266 [67-78, Wilson] | 75.8% of 575 [72-79, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 309 [0-1, Wilson] | 6.8% of 266 [4-10, Wilson] | 3.1% of 575 [2-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 309 [0-1, Wilson] | 0.0% of 266 [0-1, Wilson] | 0.0% of 575 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 21.7% of 309 [17-27, Wilson] | 20.3% of 266 [16-26, Wilson] | 21.0% of 575 [18-25, Wilson] |

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 80.0% [76-83, Wilson] | 52.2% [48-57, Wilson] | 66.1% [63-69, Wilson] |
| P2 both Glimmora had their turn | 28.2% [24-32, Wilson] | 7.4% [5-10, Wilson] | 17.8% [16-20, Wilson] |
| P2 the first Glimmora placed had its turn | 74.6% [71-78, Wilson] | 31.2% [27-35, Wilson] | 52.9% [50-56, Wilson] |
| P2 the second Glimmora placed had its turn | 33.6% [30-38, Wilson] | 28.4% [25-33, Wilson] | 31.0% [28-34, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 19.4% [16-23, Wilson] | 19.2% [16-23, Wilson] | 19.3% [17-22, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 55.6% [51-60, Wilson] | 54.4% [50-59, Wilson] | 55.0% [52-58, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.0% [3-6, Wilson] | 0.4% [0-1, Wilson] | 2.2% [1-3, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.0% [3-6, Wilson] | 0.4% [0-1, Wilson] | 2.2% [1-3, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.8% [2-6, Wilson] | 1.4% [1-3, Wilson] | 2.6% [2-4, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 92.2% [90-94, Wilson] | 98.2% [97-99, Wilson] | 95.2% [94-96, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.0% [3-6, Wilson] | 0.4% [0-1, Wilson] | 2.2% [1-3, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.0% [3-6, Wilson] | 0.4% [0-1, Wilson] | 2.2% [1-3, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 51.3% of 39 [36-66, Wilson] | 22.2% of 9 [6-55, Wilson] | 45.8% of 48 [33-60, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 51.3% of 39 [36-66, Wilson] | 22.2% of 9 [6-55, Wilson] | 45.8% of 48 [33-60, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 39 [0-9, Wilson] | 0.0% of 9 [0-30, Wilson] | 0.0% of 48 [0-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 39 [0-9, Wilson] | 0.0% of 9 [0-30, Wilson] | 0.0% of 48 [0-7, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 48.7% of 39 [34-64, Wilson] | 77.8% of 9 [45-94, Wilson] | 54.2% of 48 [40-67, Wilson] |

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 94.8% [92-96, Wilson] | 90.2% [87-93, Wilson] | 92.5% [91-94, Wilson] |
| P2 both Glimmora had their turn | 69.8% [66-74, Wilson] | 57.2% [53-61, Wilson] | 63.5% [60-66, Wilson] |
| P2 the first Glimmora placed had its turn | 89.8% [87-92, Wilson] | 81.6% [78-85, Wilson] | 85.7% [83-88, Wilson] |
| P2 the second Glimmora placed had its turn | 74.8% [71-78, Wilson] | 65.8% [62-70, Wilson] | 70.3% [67-73, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 37.4% [33-42, Wilson] | 33.2% [29-37, Wilson] | 35.3% [32-38, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 38.8% [35-43, Wilson] | 48.4% [44-53, Wilson] | 43.6% [41-47, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 6.0% [4-8, Wilson] | 6.2% [4-9, Wilson] | 6.1% [5-8, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.0% [4-8, Wilson] | 6.2% [4-9, Wilson] | 6.1% [5-8, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 10.8% [8-14, Wilson] | 9.0% [7-12, Wilson] | 9.9% [8-12, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 83.2% [80-86, Wilson] | 84.8% [81-88, Wilson] | 84.0% [82-86, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 6.0% [4-8, Wilson] | 6.2% [4-9, Wilson] | 6.1% [5-8, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.0% [4-8, Wilson] | 6.2% [4-9, Wilson] | 6.1% [5-8, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 35.7% of 84 [26-46, Wilson] | 40.8% of 76 [30-52, Wilson] | 38.1% of 160 [31-46, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 35.7% of 84 [26-46, Wilson] | 40.8% of 76 [30-52, Wilson] | 38.1% of 160 [31-46, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 84 [0-4, Wilson] | 0.0% of 76 [0-5, Wilson] | 0.0% of 160 [0-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 84 [0-4, Wilson] | 0.0% of 76 [0-5, Wilson] | 0.0% of 160 [0-2, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 64.3% of 84 [54-74, Wilson] | 59.2% of 76 [48-70, Wilson] | 61.9% of 160 [54-69, Wilson] |

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 31.7% (28.9-34.6) | 24.2% (21.6-27.0) | 27.9% (26.0-30.0) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 57.8% (54.7-60.8) | 54.2% (51.1-57.3) | 56.0% (53.8-58.2) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 70.1% (67.2-72.9) | 66.5% (63.5-69.4) | 68.3% (66.2-70.3) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 76.4% (73.7-78.9) | 73.8% (71.0-76.4) | 75.1% (73.2-76.9) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 79.7% (77.1-82.1) | 78.2% (75.5-80.6) | 79.0% (77.1-80.7) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 82.4% (79.9-84.6) | 80.3% (77.7-82.6) | 81.3% (79.6-83.0) |
| K2 Kingambit in play, own turn 2 | 12.1% (10.2-14.3) | 10.9% (9.1-13.0) | 11.5% (10.2-13.0) |
| K2 Kingambit in play, own turn 3 | 23.0% (20.5-25.7) | 20.2% (17.8-22.8) | 21.6% (19.9-23.5) |
| K2 Kingambit in play, own turn 4 | 34.5% (31.6-37.5) | 33.9% (31.0-36.9) | 34.2% (32.2-36.3) |
| K2 Kingambit in play, own turn 5 | 46.5% (43.4-49.6) | 49.4% (46.3-52.5) | 48.0% (45.8-50.1) |
| K2 Kingambit in play, own turn 6 | 60.3% (57.2-63.3) | 60.8% (57.7-63.8) | 60.5% (58.4-62.7) |
| K6 Muk and Regigigas both in play, own turn 3 | 21.8% (19.4-24.5) | 22.7% (20.2-25.4) | 22.2% (20.5-24.1) |
| K6 Muk and Regigigas both in play, own turn 4 | 29.5% (26.8-32.4) | 30.9% (28.1-33.8) | 30.2% (28.2-32.2) |
| K6 Muk and Regigigas both in play, own turn 5 | 36.0% (33.1-39.0) | 37.1% (34.2-40.1) | 36.5% (34.5-38.7) |
| G3 Pawniard in play, own turn 1 | 57.8% (54.7-60.8) | 54.2% (51.1-57.3) | 56.0% (53.8-58.2) |
| G3 Pawniard in play, own turn 2 | 58.0% (54.9-61.0) | 55.6% (52.5-58.7) | 56.8% (54.6-59.0) |
| G3 Pawniard in play, own turn 3 | 53.4% (50.3-56.5) | 53.6% (50.5-56.7) | 53.5% (51.3-55.7) |
| G3 Pawniard in play, own turn 4 | 45.2% (42.1-48.3) | 44.3% (41.2-47.4) | 44.8% (42.6-46.9) |
| G3 Pawniard in play, own turn 5 | 35.9% (33.0-38.9) | 30.9% (28.1-33.8) | 33.4% (31.4-35.5) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 2 | 12.1% (10.2-14.3) | 10.9% (9.1-13.0) | 11.5% (10.2-13.0) |
| G3 Kingambit in play, own turn 3 | 23.0% (20.5-25.7) | 20.2% (17.8-22.8) | 21.6% (19.9-23.5) |
| G3 Kingambit in play, own turn 4 | 34.5% (31.6-37.5) | 33.9% (31.0-36.9) | 34.2% (32.2-36.3) |
| G3 Kingambit in play, own turn 5 | 46.5% (43.4-49.6) | 49.4% (46.3-52.5) | 48.0% (45.8-50.1) |
| G3 Alolan Grimer in play, own turn 1 | 55.6% (52.5-58.7) | 55.4% (52.3-58.5) | 55.5% (53.3-57.7) |
| G3 Alolan Grimer in play, own turn 2 | 45.6% (42.5-48.7) | 46.0% (42.9-49.1) | 45.8% (43.6-48.0) |
| G3 Alolan Grimer in play, own turn 3 | 39.2% (36.2-42.3) | 38.2% (35.2-41.3) | 38.7% (36.6-40.9) |
| G3 Alolan Grimer in play, own turn 4 | 32.8% (30.0-35.8) | 31.6% (28.8-34.5) | 32.2% (30.2-34.3) |
| G3 Alolan Grimer in play, own turn 5 | 26.0% (23.4-28.8) | 26.1% (23.5-28.9) | 26.1% (24.2-28.0) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Alolan Muk in play, own turn 2 | 20.3% (17.9-22.9) | 20.5% (18.1-23.1) | 20.4% (18.7-22.2) |
| G3 Alolan Muk in play, own turn 3 | 31.5% (28.7-34.4) | 33.8% (30.9-36.8) | 32.6% (30.6-34.7) |
| G3 Alolan Muk in play, own turn 4 | 40.6% (37.6-43.7) | 43.1% (40.1-46.2) | 41.9% (39.7-44.0) |
| G3 Alolan Muk in play, own turn 5 | 48.8% (45.7-51.9) | 50.4% (47.3-53.5) | 49.6% (47.4-51.8) |
| G3 Glimmet in play, own turn 1 | 81.2% (78.7-83.5) | 85.3% (83.0-87.4) | 83.2% (81.5-84.8) |
| G3 Glimmet in play, own turn 2 | 51.7% (48.6-54.8) | 54.0% (50.9-57.1) | 52.9% (50.7-55.0) |
| G3 Glimmet in play, own turn 3 | 43.0% (40.0-46.1) | 41.6% (38.6-44.7) | 42.3% (40.2-44.5) |
| G3 Glimmet in play, own turn 4 | 31.2% (28.4-34.1) | 30.5% (27.7-33.4) | 30.9% (28.9-32.9) |
| G3 Glimmet in play, own turn 5 | 20.5% (18.1-23.1) | 17.3% (15.1-19.8) | 18.9% (17.2-20.7) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Glimmora in play, own turn 2 | 63.0% (60.0-65.9) | 65.9% (62.9-68.8) | 64.5% (62.3-66.5) |
| G3 Glimmora in play, own turn 3 | 78.4% (75.7-80.8) | 81.7% (79.2-84.0) | 80.0% (78.2-81.7) |
| G3 Glimmora in play, own turn 4 | 89.0% (86.9-90.8) | 90.5% (88.5-92.2) | 89.8% (88.3-91.0) |
| G3 Glimmora in play, own turn 5 | 94.9% (93.4-96.1) | 95.4% (93.9-96.5) | 95.2% (94.1-96.0) |
| G3 Regigigas in play, own turn 1 | 57.1% (54.0-60.1) | 51.7% (48.6-54.8) | 54.4% (52.2-56.6) |
| G3 Regigigas in play, own turn 2 | 68.4% (65.5-71.2) | 64.0% (61.0-66.9) | 66.2% (64.1-68.2) |
| G3 Regigigas in play, own turn 3 | 74.2% (71.4-76.8) | 71.0% (68.1-73.7) | 72.6% (70.6-74.5) |
| G3 Regigigas in play, own turn 4 | 78.2% (75.5-80.6) | 75.4% (72.6-78.0) | 76.8% (74.9-78.6) |
| G3 Regigigas in play, own turn 5 | 79.6% (77.0-82.0) | 78.4% (75.7-80.8) | 79.0% (77.2-80.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 77.0% (74.3-79.5) | 78.2% (75.5-80.6) | 77.6% (75.7-79.4) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 90.4% (88.4-92.1) | 91.2% (89.3-92.8) | 90.8% (89.5-92.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 96.3% (94.9-97.3) | 96.7% (95.4-97.6) | 96.5% (95.6-97.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.4% (97.4-99.0) | 99.0% (98.2-99.5) | 98.7% (98.1-99.1) |
| G4.s2 a Stage 2 in play, own turn 2 | 12.1% (10.2-14.3) | 10.9% (9.1-13.0) | 11.5% (10.2-13.0) |
| G4.s2 a Stage 2 in play, own turn 3 | 23.0% (20.5-25.7) | 20.2% (17.8-22.8) | 21.6% (19.9-23.5) |
| G4.s2 a Stage 2 in play, own turn 4 | 34.5% (31.6-37.5) | 33.9% (31.0-36.9) | 34.2% (32.2-36.3) |
| G4.s2 a Stage 2 in play, own turn 5 | 46.5% (43.4-49.6) | 49.4% (46.3-52.5) | 48.0% (45.8-50.1) |
| G5.any3 an empty own turn among turns 1-3 | 21.8% (19.4-24.5) | 22.4% (19.9-25.1) | 22.1% (20.3-24.0) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.4) | 10.9% (9.1-13.0) | 5.5% (4.5-6.5) |
| G6 Kingambit with [DD] attached, own turn 3 | 19.3% (17.0-21.9) | 20.2% (17.8-22.8) | 19.8% (18.1-21.6) |
| G6 Kingambit with [DD] attached, own turn 4 | 34.5% (31.6-37.5) | 33.9% (31.0-36.9) | 34.2% (32.2-36.3) |
| G6 Kingambit with [DD] attached, own turn 5 | 46.5% (43.4-49.6) | 49.4% (46.3-52.5) | 48.0% (45.8-50.1) |
| G5 mean empty own turns in turns 1-5 | 0.778 | 0.734 | 0.756 |

Clock measures under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.6% / 9.8% [1-4] | 1.3% / 4.9% [1-2] |
| K3.by3 | 3.2% / 13.4% [2-5] | 3.0% / 10.2% [2-4] | 3.1% / 11.8% [2-4] |
| K3.by4 | 4.0% / 14.2% [2-6] | 4.8% / 12.0% [4-6] | 4.4% / 13.1% [3-6] |
| K3.by5 | 6.6% / 16.8% [4-9] | 5.4% / 19.2% [4-7] | 6.0% / 18.0% [5-8] |
| K3.by6 | 7.2% / 25.0% [5-10] | 10.2% / 33.2% [5-18] | 8.7% / 29.1% [5-13] |
| K3.by7 | 15.6% / 42.2% [6-28] | 12.2% / 53.2% [5-20] | 13.9% / 47.7% [6-24] |
| K3.by8 | 18.8% / 67.2% [7-32] | 12.2% / 58.0% [5-20] | 15.5% / 62.6% [7-26] |
| K3.never | 32.8% / 81.2% [14-55] | 42.0% / 87.8% [19-64] | 37.4% / 84.5% [17-60] |
| K3.k0 | 4.4% / 52.8% [3-6] | 3.0% / 48.8% [2-4] | 3.7% / 50.8% [2-5] |
| K3.k1 | 0.0% / 48.4% [0-0] | 0.0% / 45.8% [0-0] | 0.0% / 47.1% [0-0] |
| K3.k2 | 9.2% / 57.6% [1-21] | 6.6% / 52.4% [1-14] | 7.9% / 55.0% [2-17] |
| K3.k3p | 5.2% / 53.6% [0-13] | 2.6% / 48.4% [0-6] | 3.9% / 51.0% [0-10] |
| K4 | 14.4% / 65.6% [2-28] | 9.2% / 56.4% [2-17] | 11.8% / 61.0% [2-22] |
| K5 | 7.6% / 62.8% [5-10] | 7.0% / 54.8% [5-9] | 7.3% / 58.8% [5-9] |

Clock measures under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.2% [2-4] | 1.6% [0-3] |
| K3.by3 | 3.2% / 14.8% [1-5] | 3.8% [3-4] | 3.5% / 9.3% [2-4] |
| K3.by4 | 3.8% / 15.4% [2-6] | 6.0% [3-8] | 4.9% / 10.7% [3-6] |
| K3.by5 | 6.0% / 17.6% [3-9] | 7.2% / 30.2% [7-8] | 6.6% / 23.9% [5-8] |
| K3.by6 | 6.6% / 18.2% [4-10] | 7.4% / 30.4% [7-8] | 7.0% / 24.3% [6-8] |
| K3.by7 | 16.0% / 38.6% [6-29] | 13.8% / 70.6% [7-26] | 14.9% / 54.6% [7-24] |
| K3.by8 | 16.0% / 60.2% [6-29] | 13.8% / 81.2% [7-26] | 14.9% / 70.7% [7-24] |
| K3.never | 39.8% / 84.0% [14-68] | 18.8% / 86.2% [1-44] | 29.3% / 85.1% [12-50] |
| K3.k0 | 4.0% / 48.2% [2-6] | 4.8% / 72.2% [3-7] | 4.4% / 60.2% [3-6] |
| K3.k1 | 0.0% / 44.2% [0-0] | 0.0% / 67.4% [0-0] | 0.0% / 55.8% [0-0] |
| K3.k2 | 8.4% / 52.6% [1-20] | 2.6% / 70.0% [0-4] | 5.5% / 61.3% [2-13] |
| K3.k3p | 3.6% / 47.8% [0-11] | 6.4% / 73.8% [0-18] | 5.0% / 60.8% [0-11] |
| K4 | 12.0% / 58.6% [1-25] | 9.0% / 80.2% [0-22] | 10.5% / 69.4% [2-20] |
| K5 | 8.2% / 58.2% [5-11] | 6.0% / 81.0% [4-8] | 7.1% / 69.6% [5-9] |

Clock measures under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [1-4] | 1.2% [1-2] |
| K3.by3 | 4.4% [3-6] | 2.6% [1-4] | 3.5% [2-5] |
| K3.by4 | 5.0% [3-7] | 4.2% [3-6] | 4.6% [3-6] |
| K3.by5 | 7.2% [5-10] | 6.2% [4-9] | 6.7% [5-9] |
| K3.by6 | 10.0% [7-13] | 7.8% / 12.0% [5-11] | 8.9% / 11.0% [7-11] |
| K3.by7 | 11.4% / 15.0% [8-15] | 9.8% / 17.6% [7-14] | 10.6% / 16.3% [8-13] |
| K3.by8 | 13.6% / 24.8% [10-18] | 10.8% / 20.8% [7-15] | 12.2% / 22.8% [9-16] |
| K3.never | 75.2% / 86.4% [65-83] | 79.2% / 89.2% [71-86] | 77.2% / 87.8% [69-84] |
| K3.k0 | 5.8% / 17.0% [4-8] | 2.6% / 12.6% [1-4] | 4.2% / 14.8% [3-5] |
| K3.k1 | 0.0% / 11.2% [0-0] | 0.0% / 10.0% [0-0] | 0.0% / 10.6% [0-0] |
| K3.k2 | 3.4% / 14.6% [1-6] | 3.4% / 13.4% [2-5] | 3.4% / 14.0% [2-5] |
| K3.k3p | 4.4% / 15.6% [2-8] | 4.8% / 14.8% [2-9] | 4.6% / 15.2% [2-8] |
| K4 | 7.8% / 20.6% [5-12] | 8.2% / 18.8% [5-12] | 8.0% / 19.7% [5-11] |
| K5 | 8.8% / 23.8% [6-11] | 8.6% / 19.4% [6-11] | 8.7% / 21.6% [7-11] |

Clock measures under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 3.2% [2-5, Wilson] | 1.6% [1-3, Wilson] |
| K3.by4 | 2.8% [2-5, Wilson] | 5.8% [4-8, Wilson] | 4.3% [3-6, Wilson] |
| K3.by5 | 10.4% [8-13, Wilson] | 6.2% [4-9, Wilson] | 8.3% [7-10, Wilson] |
| K3.by6 | 14.2% [11-18, Wilson] | 6.2% [4-9, Wilson] | 10.2% [8-12, Wilson] |
| K3.by7 | 14.2% [11-18, Wilson] | 6.2% [4-9, Wilson] | 10.2% [8-12, Wilson] |
| K3.by8 | 14.2% [11-18, Wilson] | 6.2% [4-9, Wilson] | 10.2% [8-12, Wilson] |
| K3.never | 85.8% [82-89, Wilson] | 93.8% [91-96, Wilson] | 89.8% [88-92, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.8% [2-5, Wilson] | 3.2% [2-5, Wilson] | 3.0% [2-4, Wilson] |
| K3.k3p | 11.4% [9-14, Wilson] | 3.0% [2-5, Wilson] | 7.2% [6-9, Wilson] |
| K4 | 14.2% [11-18, Wilson] | 6.2% [4-9, Wilson] | 10.2% [8-12, Wilson] |
| K5 | 18.0% [15-22, Wilson] | 21.8% [18-26, Wilson] | 19.9% [18-22, Wilson] |

Clock measures under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 3.4% [2-5, Wilson] | 1.7% [1-3, Wilson] |
| K3.by3 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.by4 | 4.8% [3-7, Wilson] | 7.2% [5-10, Wilson] | 6.0% [5-8, Wilson] |
| K3.by5 | 6.4% [5-9, Wilson] | 17.6% [15-21, Wilson] | 12.0% [10-14, Wilson] |
| K3.by6 | 23.2% [20-27, Wilson] | 20.8% [17-25, Wilson] | 22.0% [20-25, Wilson] |
| K3.by7 | 27.4% [24-31, Wilson] | 20.8% [17-25, Wilson] | 24.1% [22-27, Wilson] |
| K3.by8 | 27.4% [24-31, Wilson] | 20.8% [17-25, Wilson] | 24.1% [22-27, Wilson] |
| K3.never | 72.6% [69-76, Wilson] | 79.2% [75-83, Wilson] | 75.9% [73-78, Wilson] |
| K3.k0 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.6% [1-3, Wilson] | 3.8% [2-6, Wilson] | 2.7% [2-4, Wilson] |
| K3.k3p | 21.0% [18-25, Wilson] | 13.6% [11-17, Wilson] | 17.3% [15-20, Wilson] |
| K4 | 22.6% [19-26, Wilson] | 17.4% [14-21, Wilson] | 20.0% [18-23, Wilson] |
| K5 | 13.4% [11-17, Wilson] | 15.6% [13-19, Wilson] | 14.5% [12-17, Wilson] |

Clock measures under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 3.4% [2-5, Wilson] | 1.7% [1-3, Wilson] |
| K3.by3 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.by4 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.by5 | 4.8% [3-7, Wilson] | 8.8% [7-12, Wilson] | 6.8% [5-9, Wilson] |
| K3.by6 | 7.8% [6-10, Wilson] | 8.8% [7-12, Wilson] | 8.3% [7-10, Wilson] |
| K3.by7 | 8.2% [6-11, Wilson] | 40.6% [36-45, Wilson] | 24.4% [22-27, Wilson] |
| K3.by8 | 50.2% [46-55, Wilson] | 41.0% [37-45, Wilson] | 45.6% [43-49, Wilson] |
| K3.never | 49.8% [45-54, Wilson] | 59.0% [55-63, Wilson] | 54.4% [51-57, Wilson] |
| K3.k0 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.4% [2-5, Wilson] | 5.4% [4-8, Wilson] | 4.4% [3-6, Wilson] |
| K3.k3p | 42.0% [38-46, Wilson] | 32.2% [28-36, Wilson] | 37.1% [34-40, Wilson] |
| K4 | 45.4% [41-50, Wilson] | 37.6% [33-42, Wilson] | 41.5% [38-45, Wilson] |
| K5 | 10.0% [8-13, Wilson] | 8.4% [6-11, Wilson] | 9.2% [8-11, Wilson] |

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 3.2% [2-5, Wilson] | 1.6% [1-3, Wilson] |
| K3.by4 | 2.8% [2-5, Wilson] | 5.6% [4-8, Wilson] | 4.2% [3-6, Wilson] |
| K3.by5 | 9.2% [7-12, Wilson] | 6.0% [4-8, Wilson] | 7.6% [6-9, Wilson] |
| K3.by6 | 13.2% [11-16, Wilson] | 6.0% [4-8, Wilson] | 9.6% [8-12, Wilson] |
| K3.by7 | 13.2% [11-16, Wilson] | 6.0% [4-8, Wilson] | 9.6% [8-12, Wilson] |
| K3.by8 | 13.2% [11-16, Wilson] | 6.0% [4-8, Wilson] | 9.6% [8-12, Wilson] |
| K3.never | 86.8% [84-89, Wilson] | 94.0% [92-96, Wilson] | 90.4% [88-92, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.8% [2-5, Wilson] | 3.2% [2-5, Wilson] | 3.0% [2-4, Wilson] |
| K3.k3p | 10.4% [8-13, Wilson] | 2.8% [2-5, Wilson] | 6.6% [5-8, Wilson] |
| K4 | 13.2% [11-16, Wilson] | 6.0% [4-8, Wilson] | 9.6% [8-12, Wilson] |
| K5 | 18.0% [15-22, Wilson] | 21.8% [18-26, Wilson] | 19.9% [18-22, Wilson] |

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 3.4% [2-5, Wilson] | 1.7% [1-3, Wilson] |
| K3.by3 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.by4 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.by5 | 4.8% [3-7, Wilson] | 8.8% [7-12, Wilson] | 6.8% [5-9, Wilson] |
| K3.by6 | 7.8% [6-10, Wilson] | 8.8% [7-12, Wilson] | 8.3% [7-10, Wilson] |
| K3.by7 | 8.2% [6-11, Wilson] | 33.6% [30-38, Wilson] | 20.9% [18-24, Wilson] |
| K3.by8 | 41.0% [37-45, Wilson] | 34.0% [30-38, Wilson] | 37.5% [35-41, Wilson] |
| K3.by9 | 41.0% [37-45, Wilson] | 40.2% [36-45, Wilson] | 40.6% [38-44, Wilson] |
| K3.by10 | 47.0% [43-51, Wilson] | 40.2% [36-45, Wilson] | 43.6% [41-47, Wilson] |
| K3.never | 53.0% [49-57, Wilson] | 59.8% [55-64, Wilson] | 56.4% [53-59, Wilson] |
| K3.k0 | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] | 4.1% [3-6, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.4% [2-5, Wilson] | 5.4% [4-8, Wilson] | 4.4% [3-6, Wilson] |
| K3.k3p | 38.8% [35-43, Wilson] | 31.4% [27-36, Wilson] | 35.1% [32-38, Wilson] |
| K4 | 42.2% [38-47, Wilson] | 36.8% [33-41, Wilson] | 39.5% [37-43, Wilson] |
| K5 | 10.0% [8-13, Wilson] | 8.4% [6-11, Wilson] | 9.2% [8-11, Wilson] |

**Plain summary, base.**

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## deck01 (card-list id 35d98d0dcaf2)

Changes: decks/dustin/01-muk-glimmora-kingambit-regigigas.txt

Copycat decisions with a Copycat in hand: 21,906; the valuation and the fallback rule disagree at 8,733 of 21,906 Copycat decisions (39.9%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.2371.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03373; in 8 cards: 0.05246.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 2,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 30.1% (27.3-33.0) | 28.2% (25.5-31.1) | 29.1% (27.2-31.2) |

Plan lines under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.8% / 96.4% [79-98] | 83.8% / 93.6% [68-95] | 86.8% / 95.0% [74-96] |
| P2 both Glimmora had their turn | 43.0% / 74.4% [31-54] | 44.0% / 73.0% [29-60] | 43.5% / 73.7% [31-55] |
| P2 the first Glimmora placed had its turn | 87.6% / 93.8% [76-97] | 76.6% / 84.8% [60-90] | 82.1% / 89.3% [69-93] |
| P2 the second Glimmora placed had its turn | 45.2% / 74.0% [32-57] | 51.2% / 75.0% [36-66] | 48.2% / 74.5% [35-60] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [12-16] | 10.0% [9-11] | 11.9% [11-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 6.6% / 53.6% [1-15] | 6.8% / 53.6% [2-12] | 6.7% / 53.6% [2-13] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 23.8% / 64.4% [17-31] | 31.8% / 68.8% [24-42] | 27.8% / 66.6% [21-36] |
| P4 ready at the winning moment: Knocks out their strongest | 14.2% / 41.4% [3-29] | 12.6% / 38.8% [2-26] | 13.4% / 40.1% [3-27] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.8% / 30.0% [0-9] | 2.4% / 28.6% [0-7] | 2.6% / 29.3% [0-8] |
| P4 not ready, ready 1 turn late | 4.4% / 49.0% [0-13] | 3.8% / 47.2% [0-10] | 4.1% / 48.1% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.2% / 45.8% [0-4] | 0.8% / 44.2% [0-3] | 1.0% / 45.0% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 9.2% / 53.8% [0-22] | 8.4% / 51.8% [0-22] | 8.8% / 52.8% [0-22] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 26.4% / 53.6% [7-51] | 31.0% / 57.2% [10-55] | 28.7% / 55.4% [9-52] |
| P5 plan reached in time: Knocks out their strongest | 19.8% / 64.4% [4-36] | 17.2% / 60.6% [5-31] | 18.5% / 62.5% [5-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.8% / 47.4% [0-9] | 2.4% / 45.8% [0-7] | 2.6% / 46.6% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 49.0% of 145 [21-74] | 49.2% of 128 [17-77] | 49.1% of 273 [21-76] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 9.7% of 145 [0-42] | 9.4% of 128 [0-45] | 9.5% of 273 [0-42] |
| P4 not ready, ready 1 turn late | 15.2% of 145 [0-61] | 14.8% of 128 [0-53] | 15.0% of 273 [0-57] |
| P4 not ready, ready 2 or more turns late | 4.1% of 145 [0-16] | 3.1% of 128 [0-11] | 3.7% of 273 [0-14] |
| P4 the moment came and Kingambit was never ready in the deal | 31.7% of 145 [0-60] | 32.8% of 128 [0-67] | 32.2% of 273 [0-63] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +3.2 points (+1.8 to +4.4); P2.both: +5.9 points (+2.9 to +9.6); P2.g1: +3.2 points (+1.6 to +4.7); P2.g2: +5.9 points (+2.8 to +9.8); P4.nomoment: -1.8 points (-3.7 to -0.2).

Plan lines under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 89.6% / 97.4% [75-98] | 91.6% / 96.0% [85-96] | 90.6% / 96.7% [82-96] |
| P2 both Glimmora had their turn | 44.2% / 72.0% [28-59] | 37.8% / 80.4% [32-46] | 41.0% / 76.2% [32-51] |
| P2 the first Glimmora placed had its turn | 86.2% / 93.6% [72-95] | 88.2% / 89.6% [81-95] | 87.2% / 91.6% [79-93] |
| P2 the second Glimmora placed had its turn | 47.6% / 71.8% [29-64] | 41.2% / 77.8% [34-52] | 44.4% / 74.8% [35-56] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-16] | 10.0% [9-11] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 2.0% / 46.4% [0-5] | 13.4% / 79.4% [0-31] | 7.7% / 62.9% [1-17] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 24.2% / 61.6% [16-34] | 32.4% / 89.2% [18-42] | 28.3% / 75.4% [20-36] |
| P4 ready at the winning moment: Knocks out their strongest | 19.4% / 43.4% [2-38] | 3.6% / 61.2% [0-13] | 11.5% / 52.3% [3-24] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 5.8% / 29.8% [0-18] | 0.0% / 57.6% [0-0] | 2.9% / 43.7% [0-11] |
| P4 not ready, ready 1 turn late | 6.6% / 44.6% [0-20] | 0.0% / 79.6% [0-0] | 3.3% / 62.1% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.8% / 39.8% [0-6] | 0.0% / 79.6% [0-0] | 0.9% / 59.7% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 10.4% / 48.4% [0-24] | 0.0% / 79.6% [0-0] | 5.2% / 64.0% [0-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 23.8% / 47.8% [5-51] | 16.8% / 74.4% [0-40] | 20.3% / 61.1% [6-39] |
| P5 plan reached in time: Knocks out their strongest | 27.8% / 65.8% [7-48] | 3.6% / 83.2% [0-13] | 15.7% / 74.5% [5-33] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.0% / 44.0% [0-18] | 0.0% / 79.6% [0-0] | 3.0% / 61.8% [0-11] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 50.8% of 191 [13-73] | 100.0% of 18 [100-100] | 55.0% of 209 [26-80] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 15.2% of 191 [0-51] | 0.0% of 18 [0-0] | 13.9% of 209 [0-44] |
| P4 not ready, ready 1 turn late | 17.3% of 191 [0-68] | 0.0% of 18 [0-0] | 15.8% of 209 [0-49] |
| P4 not ready, ready 2 or more turns late | 4.7% of 191 [0-19] | 0.0% of 18 [0-0] | 4.3% of 209 [0-14] |
| P4 the moment came and Kingambit was never ready in the deal | 27.2% of 191 [0-52] | 0.0% of 18 [0-0] | 24.9% of 209 [0-45] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +2.5 points (+0.9 to +4.0); P2.both: +5.1 points (+2.9 to +7.6); P2.g1: +3.1 points (+0.7 to +5.3); P2.g2: +4.5 points (+2.0 to +7.4); P3.grimer_muk: -2.2 points (-3.6 to -0.4); P4.nomoment: -2.7 points (-4.9 to -0.8).

Plan lines under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 93.4% / 94.0% [90-96] | 85.2% / 86.0% [81-89] | 89.3% / 90.0% [86-92] |
| P2 both Glimmora had their turn | 46.6% / 51.2% [40-53] | 38.4% / 43.2% [32-45] | 42.5% / 47.2% [37-49] |
| P2 the first Glimmora placed had its turn | 88.6% / 88.8% [84-93] | 75.4% [68-82] | 82.0% / 82.1% [77-87] |
| P2 the second Glimmora placed had its turn | 51.4% / 54.8% [45-58] | 48.2% / 51.6% [43-54] | 49.8% / 53.2% [45-55] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17] | 10.0% [8-12] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 16.4% / 27.8% [11-22] | 17.6% / 27.4% [13-23] | 17.0% / 27.6% [13-22] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 31.2% / 41.8% [26-36] | 38.8% / 46.4% [34-44] | 35.0% / 44.1% [31-39] |
| P4 ready at the winning moment: Knocks out their strongest | 9.0% / 15.6% [4-15] | 8.4% / 15.8% [4-14] | 8.7% / 15.7% [4-14] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.8% / 7.4% [0-2] | 0.6% / 8.0% [0-2] | 0.7% / 7.7% [0-2] |
| P4 not ready, ready 1 turn late | 5.4% / 14.2% [2-9] | 4.6% / 12.8% [2-8] | 5.0% / 13.5% [2-8] |
| P4 not ready, ready 2 or more turns late | 1.4% / 10.2% [0-3] | 1.0% / 9.2% [0-2] | 1.2% / 9.7% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 9.2% / 18.0% [4-16] | 6.4% / 14.6% [2-11] | 7.8% / 16.3% [3-13] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 66.2% / 72.8% [53-78] | 71.4% / 78.8% [60-82] | 68.8% / 75.8% [57-79] |
| P5 plan reached in time: Knocks out their strongest | 15.8% / 24.6% [8-25] | 14.0% / 22.2% [8-21] | 14.9% / 23.4% [8-23] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.8% / 9.6% [0-2] | 0.6% / 8.8% [0-2] | 0.7% / 9.2% [0-2] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 36.0% of 125 [21-53] | 41.2% of 102 [28-56] | 38.3% of 227 [25-53] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.2% of 125 [0-12] | 2.9% of 102 [0-9] | 3.1% of 227 [0-10] |
| P4 not ready, ready 1 turn late | 21.6% of 125 [12-32] | 22.5% of 102 [11-35] | 22.0% of 227 [13-31] |
| P4 not ready, ready 2 or more turns late | 5.6% of 125 [1-12] | 4.9% of 102 [1-10] | 5.3% of 227 [2-10] |
| P4 the moment came and Kingambit was never ready in the deal | 36.8% of 125 [20-52] | 31.4% of 102 [17-47] | 34.4% of 227 [20-48] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: +7.0 points (+4.5 to +9.7); P2.g2: +6.1 points (+3.4 to +9.0); P3.grimer_muk: -6.0 points (-8.4 to -3.5); P4.ko: +2.2 points (+0.9 to +3.8); P5.ko: +1.4 points (+0.2 to +2.8).

Plan lines under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.2% [83-89, Wilson] | 59.0% [55-63, Wilson] | 72.6% [70-75, Wilson] |
| P2 both Glimmora had their turn | 36.4% [32-41, Wilson] | 9.8% [7-13, Wilson] | 23.1% [21-26, Wilson] |
| P2 the first Glimmora placed had its turn | 81.0% [77-84, Wilson] | 34.4% [30-39, Wilson] | 57.7% [55-61, Wilson] |
| P2 the second Glimmora placed had its turn | 41.6% [37-46, Wilson] | 34.4% [30-39, Wilson] | 38.0% [35-41, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 21.8% [18-26, Wilson] | 16.8% [14-20, Wilson] | 19.3% [17-22, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 51.4% [47-56, Wilson] | 56.4% [52-61, Wilson] | 53.9% [51-57, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 22.4% [19-26, Wilson] | 8.0% [6-11, Wilson] | 15.2% [13-18, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 22.4% [19-26, Wilson] | 8.0% [6-11, Wilson] | 15.2% [13-18, Wilson] |
| P4 not ready, ready 1 turn late | 2.6% [2-4, Wilson] | 1.2% [1-3, Wilson] | 1.9% [1-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 22.2% [19-26, Wilson] | 18.0% [15-22, Wilson] | 20.1% [18-23, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 52.8% [48-57, Wilson] | 72.8% [69-77, Wilson] | 62.8% [60-66, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 25.0% [21-29, Wilson] | 9.2% [7-12, Wilson] | 17.1% [15-20, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 25.0% [21-29, Wilson] | 9.2% [7-12, Wilson] | 17.1% [15-20, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 47.5% of 236 [41-54, Wilson] | 29.4% of 136 [22-38, Wilson] | 40.9% of 372 [36-46, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 47.5% of 236 [41-54, Wilson] | 29.4% of 136 [22-38, Wilson] | 40.9% of 372 [36-46, Wilson] |
| P4 not ready, ready 1 turn late | 5.5% of 236 [3-9, Wilson] | 4.4% of 136 [2-9, Wilson] | 5.1% of 372 [3-8, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 236 [0-2, Wilson] | 0.0% of 136 [0-3, Wilson] | 0.0% of 372 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 47.0% of 236 [41-53, Wilson] | 66.2% of 136 [58-74, Wilson] | 54.0% of 372 [49-59, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: +6.5 points (+4.3 to +8.7); P2.both: +5.7 points (+3.4 to +8.0); P2.g1: +4.8 points (+2.7 to +6.9); P2.g2: +7.4 points (+4.7 to +10.1); P4.ko: +5.0 points (+3.0 to +7.0); P4.win: +5.0 points (+3.0 to +7.0); P4.nomoment: -6.9 points (-9.1 to -4.7); P5.ko: +5.8 points (+3.7 to +7.9); P5.win: +5.8 points (+3.7 to +7.9).

Plan lines under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 93.8% [91-96, Wilson] | 85.6% [82-88, Wilson] | 89.7% [88-91, Wilson] |
| P2 both Glimmora had their turn | 47.4% [43-52, Wilson] | 34.8% [31-39, Wilson] | 41.1% [38-44, Wilson] |
| P2 the first Glimmora placed had its turn | 90.6% [88-93, Wilson] | 82.0% [78-85, Wilson] | 86.3% [84-88, Wilson] |
| P2 the second Glimmora placed had its turn | 50.6% [46-55, Wilson] | 38.4% [34-43, Wilson] | 44.5% [41-48, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 28.6% [25-33, Wilson] | 22.4% [19-26, Wilson] | 25.5% [23-28, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 47.8% [43-52, Wilson] | 56.4% [52-61, Wilson] | 52.1% [49-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 31.8% [28-36, Wilson] | 23.4% [20-27, Wilson] | 27.6% [25-30, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.6% [2-4, Wilson] | 2.4% [1-4, Wilson] | 2.5% [2-4, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 23.8% [20-28, Wilson] | 21.6% [18-25, Wilson] | 22.7% [20-25, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 41.8% [38-46, Wilson] | 52.6% [48-57, Wilson] | 47.2% [44-50, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 34.4% [30-39, Wilson] | 25.8% [22-30, Wilson] | 30.1% [27-33, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 54.6% of 291 [49-60, Wilson] | 49.4% of 237 [43-56, Wilson] | 52.3% of 528 [48-57, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 291 [0-1, Wilson] | 0.0% of 237 [0-2, Wilson] | 0.0% of 528 [0-1, Wilson] |
| P4 not ready, ready 1 turn late | 4.5% of 291 [3-7, Wilson] | 5.1% of 237 [3-9, Wilson] | 4.7% of 528 [3-7, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 291 [0-1, Wilson] | 0.0% of 237 [0-2, Wilson] | 0.0% of 528 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 40.9% of 291 [35-47, Wilson] | 45.6% of 237 [39-52, Wilson] | 43.0% of 528 [39-47, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: +4.0 points (+2.2 to +5.8); P2.both: +7.9 points (+4.9 to +10.9); P2.g1: +4.5 points (+2.4 to +6.6); P2.g2: +7.4 points (+4.3 to +10.5); P3.pawn_promo: +3.3 points (+0.6 to +6.0); P4.ko: +7.3 points (+4.9 to +9.7); P4.nomoment: -8.2 points (-10.4 to -6.0); P5.ko: +7.7 points (+5.2 to +10.2).

Plan lines under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 97.6% [96-99, Wilson] | 92.2% [90-94, Wilson] | 94.9% [93-96, Wilson] |
| P2 both Glimmora had their turn | 75.0% [71-79, Wilson] | 65.4% [61-69, Wilson] | 70.2% [67-73, Wilson] |
| P2 the first Glimmora placed had its turn | 93.2% [91-95, Wilson] | 84.4% [81-87, Wilson] | 88.8% [87-91, Wilson] |
| P2 the second Glimmora placed had its turn | 79.4% [76-83, Wilson] | 73.2% [69-77, Wilson] | 76.3% [74-79, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 3.6% [2-6, Wilson] | 5.8% [4-8, Wilson] | 4.7% [4-6, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 24.6% [21-29, Wilson] | 31.4% [27-36, Wilson] | 28.0% [25-31, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 52.6% [48-57, Wilson] | 48.6% [44-53, Wilson] | 50.6% [48-54, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 52.6% [48-57, Wilson] | 48.6% [44-53, Wilson] | 50.6% [48-54, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 1.6% [1-3, Wilson] | 0.8% [0-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 12.4% [10-16, Wilson] | 8.8% [7-12, Wilson] | 10.6% [9-13, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 35.0% [31-39, Wilson] | 41.0% [37-45, Wilson] | 38.0% [35-41, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 52.6% [48-57, Wilson] | 50.2% [46-55, Wilson] | 51.4% [48-54, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 52.6% [48-57, Wilson] | 50.2% [46-55, Wilson] | 51.4% [48-54, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 80.9% of 325 [76-85, Wilson] | 82.4% of 295 [78-86, Wilson] | 81.6% of 620 [78-84, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 80.9% of 325 [76-85, Wilson] | 82.4% of 295 [78-86, Wilson] | 81.6% of 620 [78-84, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 325 [0-1, Wilson] | 2.7% of 295 [1-5, Wilson] | 1.3% of 620 [1-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 325 [0-1, Wilson] | 0.0% of 295 [0-1, Wilson] | 0.0% of 620 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 19.1% of 325 [15-24, Wilson] | 14.9% of 295 [11-19, Wilson] | 17.1% of 620 [14-20, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: +2.4 points (+0.9 to +3.9); P2.both: +8.3 points (+5.5 to +11.1); P2.g1: +3.1 points (+1.2 to +5.0); P2.g2: +7.6 points (+4.9 to +10.3); P3.pawn_promo: -2.6 points (-4.2 to -1.0); P3.grimer_muk: -6.0 points (-8.3 to -3.7); P4.ko: +7.0 points (+4.7 to +9.3); P4.win: +7.0 points (+4.7 to +9.3); P4.late1: -1.0 points (-2.0 to -0.0); P4.nomoment: -4.5 points (-6.4 to -2.6); P5.ko: +6.0 points (+3.8 to +8.2); P5.win: +6.0 points (+3.8 to +8.2).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 86.4% [83-89, Wilson] | 59.0% [55-63, Wilson] | 72.7% [70-75, Wilson] |
| P2 both Glimmora had their turn | 37.0% [33-41, Wilson] | 9.8% [7-13, Wilson] | 23.4% [21-26, Wilson] |
| P2 the first Glimmora placed had its turn | 81.0% [77-84, Wilson] | 34.4% [30-39, Wilson] | 57.7% [55-61, Wilson] |
| P2 the second Glimmora placed had its turn | 42.4% [38-47, Wilson] | 34.4% [30-39, Wilson] | 38.4% [35-41, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 25.8% [22-30, Wilson] | 17.2% [14-21, Wilson] | 21.5% [19-24, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 51.4% [47-56, Wilson] | 56.4% [52-61, Wilson] | 53.9% [51-57, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 3.6% [2-6, Wilson] | 1.6% [1-3, Wilson] | 2.6% [2-4, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.6% [2-6, Wilson] | 1.6% [1-3, Wilson] | 2.6% [2-4, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 5.8% [4-8, Wilson] | 1.4% [1-3, Wilson] | 3.6% [3-5, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.6% [88-93, Wilson] | 97.0% [95-98, Wilson] | 93.8% [92-95, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 3.6% [2-6, Wilson] | 1.6% [1-3, Wilson] | 2.6% [2-4, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.6% [2-6, Wilson] | 1.6% [1-3, Wilson] | 2.6% [2-4, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 38.3% of 47 [26-53, Wilson] | 53.3% of 15 [30-75, Wilson] | 41.9% of 62 [30-54, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 38.3% of 47 [26-53, Wilson] | 53.3% of 15 [30-75, Wilson] | 41.9% of 62 [30-54, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 47 [0-8, Wilson] | 0.0% of 15 [0-20, Wilson] | 0.0% of 62 [0-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 47 [0-8, Wilson] | 0.0% of 15 [0-20, Wilson] | 0.0% of 62 [0-6, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 61.7% of 47 [47-74, Wilson] | 46.7% of 15 [25-70, Wilson] | 58.1% of 62 [46-70, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +6.6 points (+4.4 to +8.8); P2.both: +5.6 points (+3.3 to +7.9); P2.g1: +4.8 points (+2.7 to +6.9); P2.g2: +7.4 points (+4.7 to +10.1); P4.nomoment: -1.4 points (-2.6 to -0.2).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 97.6% [96-99, Wilson] | 92.2% [90-94, Wilson] | 94.9% [93-96, Wilson] |
| P2 both Glimmora had their turn | 76.4% [72-80, Wilson] | 67.0% [63-71, Wilson] | 71.7% [69-74, Wilson] |
| P2 the first Glimmora placed had its turn | 93.2% [91-95, Wilson] | 84.4% [81-87, Wilson] | 88.8% [87-91, Wilson] |
| P2 the second Glimmora placed had its turn | 80.8% [77-84, Wilson] | 74.8% [71-78, Wilson] | 77.8% [75-80, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 41.4% [37-46, Wilson] | 38.2% [34-43, Wilson] | 39.8% [37-43, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 37.6% [33-42, Wilson] | 45.2% [41-50, Wilson] | 41.4% [38-44, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.6% [3-7, Wilson] | 5.6% [4-8, Wilson] | 5.1% [4-7, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.6% [3-7, Wilson] | 5.6% [4-8, Wilson] | 5.1% [4-7, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 13.2% [11-16, Wilson] | 13.8% [11-17, Wilson] | 13.5% [12-16, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 82.2% [79-85, Wilson] | 80.6% [77-84, Wilson] | 81.4% [79-84, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.6% [3-7, Wilson] | 5.6% [4-8, Wilson] | 5.1% [4-7, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.6% [3-7, Wilson] | 5.6% [4-8, Wilson] | 5.1% [4-7, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 25.8% of 89 [18-36, Wilson] | 28.9% of 97 [21-39, Wilson] | 27.4% of 186 [22-34, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 25.8% of 89 [18-36, Wilson] | 28.9% of 97 [21-39, Wilson] | 27.4% of 186 [22-34, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 89 [0-4, Wilson] | 0.0% of 97 [0-4, Wilson] | 0.0% of 186 [0-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 89 [0-4, Wilson] | 0.0% of 97 [0-4, Wilson] | 0.0% of 186 [0-2, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 74.2% of 89 [64-82, Wilson] | 71.1% of 97 [61-79, Wilson] | 72.6% of 186 [66-78, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: +2.4 points (+0.9 to +3.9); P2.both: +8.2 points (+5.4 to +11.0); P2.g1: +3.1 points (+1.2 to +5.0); P2.g2: +7.5 points (+4.8 to +10.2); P3.pawn_promo: +4.5 points (+2.1 to +6.9); P3.grimer_muk: -2.2 points (-4.4 to -0.0); P4.never: +3.6 points (+2.1 to +5.1); P4.nomoment: -2.6 points (-4.0 to -1.2).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 31.7% (28.9-34.6) | 24.2% (21.6-27.0) | 27.9% (26.0-30.0) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 58.7% (55.6-61.7) | 55.7% (52.6-58.8) | 57.2% (55.0-59.4) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 71.4% (68.5-74.1) | 70.1% (67.2-72.9) | 70.8% (68.7-72.7) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 78.6% (76.0-81.0) | 77.0% (74.3-79.5) | 77.8% (75.9-79.6) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 81.9% (79.4-84.2) | 79.7% (77.1-82.1) | 80.8% (79.0-82.5) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 83.5% (81.1-85.7) | 80.8% (78.2-83.1) | 82.2% (80.4-83.8) |
| K2 Kingambit in play, own turn 2 | 14.0% (12.0-16.3) | 12.0% (10.1-14.2) | 13.0% (11.6-14.5) |
| K2 Kingambit in play, own turn 3 | 26.1% (23.5-28.9) | 23.7% (21.2-26.4) | 24.9% (23.1-26.8) |
| K2 Kingambit in play, own turn 4 | 39.3% (36.3-42.4) | 40.2% (37.2-43.3) | 39.8% (37.6-41.9) |
| K2 Kingambit in play, own turn 5 | 53.0% (49.9-56.1) | 54.7% (51.6-57.8) | 53.9% (51.7-56.0) |
| K2 Kingambit in play, own turn 6 | 65.5% (62.5-68.4) | 67.1% (64.1-69.9) | 66.3% (64.2-68.3) |
| K6 Muk and Regigigas both in play, own turn 3 | 24.2% (21.6-27.0) | 25.0% (22.4-27.8) | 24.6% (22.8-26.5) |
| K6 Muk and Regigigas both in play, own turn 4 | 33.0% (30.2-36.0) | 33.9% (31.0-36.9) | 33.5% (31.4-35.5) |
| K6 Muk and Regigigas both in play, own turn 5 | 38.9% (35.9-42.0) | 38.9% (35.9-42.0) | 38.9% (36.8-41.1) |
| G3 Pawniard in play, own turn 1 | 58.7% (55.6-61.7) | 55.7% (52.6-58.8) | 57.2% (55.0-59.4) |
| G3 Pawniard in play, own turn 2 | 57.4% (54.3-60.4) | 58.1% (55.0-61.1) | 57.8% (55.6-59.9) |
| G3 Pawniard in play, own turn 3 | 52.5% (49.4-55.6) | 53.3% (50.2-56.4) | 52.9% (50.7-55.1) |
| G3 Pawniard in play, own turn 4 | 42.6% (39.6-45.7) | 39.5% (36.5-42.6) | 41.0% (38.9-43.2) |
| G3 Pawniard in play, own turn 5 | 30.5% (27.7-33.4) | 26.1% (23.5-28.9) | 28.3% (26.4-30.3) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 2 | 14.0% (12.0-16.3) | 12.0% (10.1-14.2) | 13.0% (11.6-14.5) |
| G3 Kingambit in play, own turn 3 | 26.1% (23.5-28.9) | 23.7% (21.2-26.4) | 24.9% (23.1-26.8) |
| G3 Kingambit in play, own turn 4 | 39.3% (36.3-42.4) | 40.2% (37.2-43.3) | 39.8% (37.6-41.9) |
| G3 Kingambit in play, own turn 5 | 53.0% (49.9-56.1) | 54.7% (51.6-57.8) | 53.9% (51.7-56.0) |
| G3 Alolan Grimer in play, own turn 1 | 56.3% (53.2-59.3) | 56.2% (53.1-59.2) | 56.2% (54.1-58.4) |
| G3 Alolan Grimer in play, own turn 2 | 46.9% (43.8-50.0) | 46.0% (42.9-49.1) | 46.5% (44.3-48.6) |
| G3 Alolan Grimer in play, own turn 3 | 37.5% (34.6-40.5) | 36.5% (33.6-39.5) | 37.0% (34.9-39.1) |
| G3 Alolan Grimer in play, own turn 4 | 29.2% (26.5-32.1) | 28.0% (25.3-30.9) | 28.6% (26.7-30.6) |
| G3 Alolan Grimer in play, own turn 5 | 22.3% (19.8-25.0) | 24.2% (21.6-27.0) | 23.2% (21.5-25.2) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Alolan Muk in play, own turn 2 | 20.2% (17.8-22.8) | 21.3% (18.9-23.9) | 20.8% (19.0-22.6) |
| G3 Alolan Muk in play, own turn 3 | 33.8% (30.9-36.8) | 36.3% (33.4-39.3) | 35.0% (33.0-37.2) |
| G3 Alolan Muk in play, own turn 4 | 44.7% (41.6-47.8) | 47.2% (44.1-50.3) | 46.0% (43.8-48.1) |
| G3 Alolan Muk in play, own turn 5 | 52.4% (49.3-55.5) | 52.7% (49.6-55.8) | 52.5% (50.4-54.7) |
| G3 Glimmet in play, own turn 1 | 83.1% (80.7-85.3) | 86.8% (84.6-88.8) | 85.0% (83.3-86.5) |
| G3 Glimmet in play, own turn 2 | 51.1% (48.0-54.2) | 52.2% (49.1-55.3) | 51.6% (49.5-53.8) |
| G3 Glimmet in play, own turn 3 | 38.3% (35.3-41.4) | 35.5% (32.6-38.5) | 36.9% (34.8-39.0) |
| G3 Glimmet in play, own turn 4 | 23.8% (21.3-26.5) | 23.6% (21.1-26.3) | 23.7% (21.9-25.6) |
| G3 Glimmet in play, own turn 5 | 13.7% (11.7-16.0) | 11.1% (9.3-13.2) | 12.4% (11.0-13.9) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Glimmora in play, own turn 2 | 67.6% (64.6-70.4) | 71.0% (68.1-73.7) | 69.3% (67.2-71.3) |
| G3 Glimmora in play, own turn 3 | 83.4% (81.0-85.6) | 86.9% (84.7-88.9) | 85.2% (83.5-86.6) |
| G3 Glimmora in play, own turn 4 | 92.7% (90.9-94.2) | 93.8% (92.1-95.1) | 93.2% (92.1-94.3) |
| G3 Glimmora in play, own turn 5 | 97.0% (95.7-97.9) | 96.9% (95.6-97.8) | 97.0% (96.1-97.6) |
| G3 Regigigas in play, own turn 1 | 57.4% (54.3-60.4) | 53.5% (50.4-56.6) | 55.5% (53.3-57.6) |
| G3 Regigigas in play, own turn 2 | 70.8% (67.9-73.5) | 68.0% (65.0-70.8) | 69.4% (67.3-71.4) |
| G3 Regigigas in play, own turn 3 | 77.1% (74.4-79.6) | 74.3% (71.5-76.9) | 75.7% (73.8-77.5) |
| G3 Regigigas in play, own turn 4 | 80.2% (77.6-82.6) | 77.1% (74.4-79.6) | 78.7% (76.8-80.4) |
| G3 Regigigas in play, own turn 5 | 80.9% (78.3-83.2) | 79.2% (76.6-81.6) | 80.0% (78.2-81.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 80.9% (78.3-83.2) | 81.9% (79.4-84.2) | 81.4% (79.6-83.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 92.9% (91.1-94.3) | 94.0% (92.4-95.3) | 93.5% (92.3-94.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 97.2% (96.0-98.1) | 98.3% (97.3-98.9) | 97.8% (97.0-98.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 99.1% (98.3-99.5) | 99.2% (98.4-99.6) | 99.2% (98.6-99.5) |
| G4.s2 a Stage 2 in play, own turn 2 | 14.0% (12.0-16.3) | 12.0% (10.1-14.2) | 13.0% (11.6-14.5) |
| G4.s2 a Stage 2 in play, own turn 3 | 26.1% (23.5-28.9) | 23.7% (21.2-26.4) | 24.9% (23.1-26.8) |
| G4.s2 a Stage 2 in play, own turn 4 | 39.3% (36.3-42.4) | 40.2% (37.2-43.3) | 39.8% (37.6-41.9) |
| G4.s2 a Stage 2 in play, own turn 5 | 53.0% (49.9-56.1) | 54.7% (51.6-57.8) | 53.9% (51.7-56.0) |
| G5.any3 an empty own turn among turns 1-3 | 16.9% (14.7-19.3) | 15.8% (13.7-18.2) | 16.4% (14.8-18.0) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.4) | 12.0% (10.1-14.2) | 6.0% (5.0-7.1) |
| G6 Kingambit with [DD] attached, own turn 3 | 22.2% (19.7-24.9) | 23.7% (21.2-26.4) | 22.9% (21.2-24.8) |
| G6 Kingambit with [DD] attached, own turn 4 | 39.3% (36.3-42.4) | 40.2% (37.2-43.3) | 39.8% (37.6-41.9) |
| G6 Kingambit with [DD] attached, own turn 5 | 53.0% (49.9-56.1) | 54.7% (51.6-57.8) | 53.9% (51.7-56.0) |
| G5 mean empty own turns in turns 1-5 | 0.714 | 0.719 | 0.717 |

Clock measures under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.8% / 10.0% [1-5] | 1.4% / 5.0% [1-2] |
| K3.by3 | 4.0% / 14.2% [2-6] | 3.4% / 10.6% [1-5] | 3.7% / 12.4% [2-5] |
| K3.by4 | 5.2% / 15.4% [3-7] | 4.6% / 11.8% [3-7] | 4.9% / 13.6% [3-7] |
| K3.by5 | 7.6% / 17.8% [5-11] | 5.4% / 19.4% [3-8] | 6.5% / 18.6% [5-8] |
| K3.by6 | 8.0% / 25.4% [5-11] | 12.2% / 35.2% [4-22] | 10.1% / 30.3% [6-15] |
| K3.by7 | 17.4% / 43.4% [7-31] | 14.2% / 55.4% [6-24] | 15.8% / 49.4% [7-27] |
| K3.by8 | 21.0% / 69.0% [8-36] | 14.2% / 60.4% [6-24] | 17.6% / 64.7% [7-30] |
| K3.never | 31.0% / 79.0% [13-53] | 39.6% / 85.8% [17-62] | 35.3% / 82.4% [15-58] |
| K3.k0 | 5.4% / 53.4% [3-8] | 3.4% / 49.6% [1-5] | 4.4% / 51.5% [3-6] |
| K3.k1 | 0.0% / 48.0% [0-0] | 0.0% / 46.2% [0-0] | 0.0% / 47.1% [0-0] |
| K3.k2 | 9.4% / 57.4% [1-22] | 7.0% / 53.2% [1-17] | 8.2% / 55.3% [1-19] |
| K3.k3p | 6.2% / 54.2% [0-16] | 3.8% / 50.0% [0-9] | 5.0% / 52.1% [0-12] |
| K4 | 15.6% / 67.2% [2-31] | 10.8% / 58.6% [2-22] | 13.2% / 62.9% [2-26] |
| K5 | 6.6% / 63.6% [4-9] | 7.0% / 56.0% [4-10] | 6.8% / 59.8% [4-9] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by8: +2.1 points (+0.3 to +4.2); K3.never: -2.1 points (-4.2 to -0.2).

Clock measures under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.0% [2-5] | 1.5% [0-3] |
| K3.by3 | 3.8% / 15.4% [2-6] | 3.8% [3-5] | 3.8% / 9.6% [3-5] |
| K3.by4 | 4.0% / 15.6% [2-6] | 6.0% [3-8] | 5.0% / 10.8% [3-6] |
| K3.by5 | 6.6% / 18.2% [4-11] | 6.6% / 30.0% [5-8] | 6.6% / 24.1% [5-9] |
| K3.by6 | 6.8% / 18.4% [4-11] | 7.0% / 30.4% [6-8] | 6.9% / 24.4% [5-9] |
| K3.by7 | 18.0% / 40.8% [6-33] | 16.6% / 74.0% [7-34] | 17.3% / 57.4% [7-28] |
| K3.by8 | 18.0% / 62.6% [6-33] | 16.6% / 84.4% [7-34] | 17.3% / 73.5% [7-28] |
| K3.never | 37.4% / 82.0% [13-65] | 15.6% / 83.4% [0-37] | 26.5% / 82.7% [11-47] |
| K3.k0 | 4.0% / 48.6% [2-6] | 5.2% / 73.0% [3-7] | 4.6% / 60.8% [3-6] |
| K3.k1 | 0.0% / 44.6% [0-0] | 0.0% / 67.8% [0-0] | 0.0% / 56.2% [0-0] |
| K3.k2 | 9.4% / 54.0% [0-24] | 1.8% / 69.6% [0-3] | 5.6% / 61.8% [1-14] |
| K3.k3p | 4.6% / 49.2% [0-14] | 9.6% / 77.4% [0-27] | 7.1% / 63.3% [0-16] |
| K4 | 14.0% / 61.2% [0-29] | 11.4% / 83.8% [0-30] | 12.7% / 72.5% [2-25] |
| K5 | 8.0% / 59.6% [5-11] | 5.2% / 84.2% [4-7] | 6.6% / 71.9% [5-9] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by7: +2.4 points (+0.2 to +5.0); K3.by8: +2.4 points (+0.2 to +5.0); K3.never: -2.8 points (-5.0 to -0.9).

Clock measures under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [1-4] | 1.2% [1-2] |
| K3.by3 | 4.6% [3-6] | 2.4% [1-4] | 3.5% [3-4] |
| K3.by4 | 5.2% [4-7] | 4.6% [3-6] | 4.9% [4-6] |
| K3.by5 | 7.4% [5-10] | 6.8% [5-9] | 7.1% [5-9] |
| K3.by6 | 11.0% [8-14] | 9.2% / 13.4% [6-12] | 10.1% / 12.2% [8-13] |
| K3.by7 | 12.8% / 16.8% [9-16] | 11.6% / 19.0% [8-16] | 12.2% / 17.9% [10-15] |
| K3.by8 | 15.0% / 25.6% [11-19] | 12.8% / 22.0% [9-17] | 13.9% / 23.8% [11-17] |
| K3.never | 74.4% / 85.0% [64-82] | 78.0% / 87.2% [70-85] | 76.2% / 86.1% [68-83] |
| K3.k0 | 6.2% / 16.8% [4-8] | 2.8% / 12.0% [1-4] | 4.5% / 14.4% [3-6] |
| K3.k1 | 0.0% / 10.6% [0-0] | 0.0% / 9.2% [0-0] | 0.0% / 9.9% [0-0] |
| K3.k2 | 3.6% / 14.2% [2-6] | 3.0% / 12.2% [1-5] | 3.3% / 13.2% [2-5] |
| K3.k3p | 5.2% / 15.8% [2-9] | 7.0% / 16.2% [4-11] | 6.1% / 16.0% [3-10] |
| K4 | 8.8% / 20.8% [5-13] | 10.0% / 20.0% [6-14] | 9.4% / 20.4% [6-13] |
| K5 | 7.2% / 21.8% [5-10] | 8.2% / 19.4% [6-11] | 7.7% / 20.6% [6-9] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.k3p: +1.5 points (+0.4 to +2.9).

Clock measures under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 2.2% [1-4, Wilson] | 1.1% [1-2, Wilson] |
| K3.by4 | 2.6% [2-4, Wilson] | 5.8% [4-8, Wilson] | 4.2% [3-6, Wilson] |
| K3.by5 | 17.2% [14-21, Wilson] | 7.4% [5-10, Wilson] | 12.3% [10-14, Wilson] |
| K3.by6 | 20.6% [17-24, Wilson] | 7.4% [5-10, Wilson] | 14.0% [12-16, Wilson] |
| K3.by7 | 20.6% [17-24, Wilson] | 7.4% [5-10, Wilson] | 14.0% [12-16, Wilson] |
| K3.by8 | 20.6% [17-24, Wilson] | 7.4% [5-10, Wilson] | 14.0% [12-16, Wilson] |
| K3.never | 79.4% [76-83, Wilson] | 92.6% [90-95, Wilson] | 86.0% [84-88, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.6% [2-4, Wilson] | 2.2% [1-4, Wilson] | 2.4% [2-4, Wilson] |
| K3.k3p | 18.0% [15-22, Wilson] | 5.2% [4-8, Wilson] | 11.6% [10-14, Wilson] |
| K4 | 20.6% [17-24, Wilson] | 7.4% [5-10, Wilson] | 14.0% [12-16, Wilson] |
| K5 | 16.6% [14-20, Wilson] | 19.2% [16-23, Wilson] | 17.9% [16-20, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by5: +4.0 points (+2.1 to +5.9); K3.by6: +3.8 points (+1.8 to +5.8); K3.by7: +3.8 points (+1.8 to +5.8); K3.by8: +3.8 points (+1.8 to +5.8); K3.never: -3.8 points (-5.8 to -1.8); K3.k3p: +4.4 points (+2.6 to +6.2); K4: +3.8 points (+1.8 to +5.8); K5: -2.0 points (-3.8 to -0.2).

Clock measures under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 3.2% [2-5, Wilson] | 1.6% [1-3, Wilson] |
| K3.by3 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.by4 | 5.4% [4-8, Wilson] | 7.0% [5-10, Wilson] | 6.2% [5-8, Wilson] |
| K3.by5 | 7.0% [5-10, Wilson] | 21.4% [18-25, Wilson] | 14.2% [12-17, Wilson] |
| K3.by6 | 30.8% [27-35, Wilson] | 26.2% [23-30, Wilson] | 28.5% [26-31, Wilson] |
| K3.by7 | 35.0% [31-39, Wilson] | 26.2% [23-30, Wilson] | 30.6% [28-34, Wilson] |
| K3.by8 | 35.0% [31-39, Wilson] | 26.2% [23-30, Wilson] | 30.6% [28-34, Wilson] |
| K3.never | 65.0% [61-69, Wilson] | 73.8% [70-77, Wilson] | 69.4% [66-72, Wilson] |
| K3.k0 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.6% [1-3, Wilson] | 3.8% [2-6, Wilson] | 2.7% [2-4, Wilson] |
| K3.k3p | 28.0% [24-32, Wilson] | 19.2% [16-23, Wilson] | 23.6% [21-26, Wilson] |
| K4 | 29.6% [26-34, Wilson] | 23.0% [20-27, Wilson] | 26.3% [24-29, Wilson] |
| K5 | 11.4% [9-14, Wilson] | 12.0% [9-15, Wilson] | 11.7% [10-14, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by5: +2.2 points (+0.2 to +4.2); K3.by6: +6.5 points (+3.8 to +9.2); K3.by7: +6.5 points (+3.8 to +9.2); K3.by8: +6.5 points (+3.8 to +9.2); K3.never: -6.5 points (-9.2 to -3.8); K3.k3p: +6.3 points (+3.9 to +8.7); K4: +6.3 points (+3.7 to +8.9); K5: -2.8 points (-4.7 to -0.9).

Clock measures under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 3.2% [2-5, Wilson] | 1.6% [1-3, Wilson] |
| K3.by3 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.by4 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.by5 | 5.4% [4-8, Wilson] | 7.0% [5-10, Wilson] | 6.2% [5-8, Wilson] |
| K3.by6 | 8.2% [6-11, Wilson] | 7.0% [5-10, Wilson] | 7.6% [6-9, Wilson] |
| K3.by7 | 8.4% [6-11, Wilson] | 50.2% [46-55, Wilson] | 29.3% [27-32, Wilson] |
| K3.by8 | 55.8% [51-60, Wilson] | 50.2% [46-55, Wilson] | 53.0% [50-56, Wilson] |
| K3.never | 44.2% [40-49, Wilson] | 49.8% [45-54, Wilson] | 47.0% [44-50, Wilson] |
| K3.k0 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.0% [2-5, Wilson] | 3.8% [2-6, Wilson] | 3.4% [2-5, Wilson] |
| K3.k3p | 47.4% [43-52, Wilson] | 43.2% [39-48, Wilson] | 45.3% [42-48, Wilson] |
| K4 | 50.4% [46-55, Wilson] | 47.0% [43-51, Wilson] | 48.7% [46-52, Wilson] |
| K5 | 8.6% [6-11, Wilson] | 7.6% [6-10, Wilson] | 8.1% [7-10, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by7: +4.9 points (+2.6 to +7.2); K3.by8: +7.4 points (+4.7 to +10.1); K3.never: -7.4 points (-10.1 to -4.7); K3.k3p: +8.2 points (+5.6 to +10.8); K4: +7.2 points (+4.6 to +9.8).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 2.2% [1-4, Wilson] | 1.1% [1-2, Wilson] |
| K3.by4 | 2.6% [2-4, Wilson] | 5.6% [4-8, Wilson] | 4.1% [3-6, Wilson] |
| K3.by5 | 16.4% [13-20, Wilson] | 7.2% [5-10, Wilson] | 11.8% [10-14, Wilson] |
| K3.by6 | 20.0% [17-24, Wilson] | 7.2% [5-10, Wilson] | 13.6% [12-16, Wilson] |
| K3.by7 | 20.0% [17-24, Wilson] | 7.2% [5-10, Wilson] | 13.6% [12-16, Wilson] |
| K3.by8 | 20.0% [17-24, Wilson] | 7.2% [5-10, Wilson] | 13.6% [12-16, Wilson] |
| K3.never | 80.0% [76-83, Wilson] | 92.8% [90-95, Wilson] | 86.4% [84-88, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.6% [2-4, Wilson] | 2.2% [1-4, Wilson] | 2.4% [2-4, Wilson] |
| K3.k3p | 17.4% [14-21, Wilson] | 5.0% [3-7, Wilson] | 11.2% [9-13, Wilson] |
| K4 | 20.0% [17-24, Wilson] | 7.2% [5-10, Wilson] | 13.6% [12-16, Wilson] |
| K5 | 16.6% [14-20, Wilson] | 19.2% [16-23, Wilson] | 17.9% [16-20, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by5: +4.2 points (+2.3 to +6.1); K3.by6: +4.0 points (+2.0 to +6.0); K3.by7: +4.0 points (+2.0 to +6.0); K3.by8: +4.0 points (+2.0 to +6.0); K3.never: -4.0 points (-6.0 to -2.0); K3.k3p: +4.6 points (+2.8 to +6.4); K4: +4.0 points (+2.0 to +6.0); K5: -2.0 points (-3.8 to -0.2).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 3.2% [2-5, Wilson] | 1.6% [1-3, Wilson] |
| K3.by3 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.by4 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.by5 | 5.4% [4-8, Wilson] | 7.0% [5-10, Wilson] | 6.2% [5-8, Wilson] |
| K3.by6 | 8.2% [6-11, Wilson] | 7.0% [5-10, Wilson] | 7.6% [6-9, Wilson] |
| K3.by7 | 8.4% [6-11, Wilson] | 40.2% [36-45, Wilson] | 24.3% [22-27, Wilson] |
| K3.by8 | 46.6% [42-51, Wilson] | 40.2% [36-45, Wilson] | 43.4% [40-46, Wilson] |
| K3.by9 | 46.6% [42-51, Wilson] | 45.8% [41-50, Wilson] | 46.2% [43-49, Wilson] |
| K3.by10 | 51.2% [47-56, Wilson] | 45.8% [41-50, Wilson] | 48.5% [45-52, Wilson] |
| K3.never | 48.8% [44-53, Wilson] | 54.2% [50-59, Wilson] | 51.5% [48-55, Wilson] |
| K3.k0 | 5.4% [4-8, Wilson] | 3.2% [2-5, Wilson] | 4.3% [3-6, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.0% [2-5, Wilson] | 3.8% [2-6, Wilson] | 3.4% [2-5, Wilson] |
| K3.k3p | 42.8% [39-47, Wilson] | 38.8% [35-43, Wilson] | 40.8% [38-44, Wilson] |
| K4 | 45.8% [41-50, Wilson] | 42.6% [38-47, Wilson] | 44.2% [41-47, Wilson] |
| K5 | 8.6% [6-11, Wilson] | 7.8% [6-10, Wilson] | 8.2% [7-10, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by7: +3.4 points (+1.2 to +5.6); K3.by8: +5.9 points (+3.3 to +8.5); K3.by9: +5.6 points (+3.1 to +8.1); K3.by10: +4.9 points (+2.5 to +7.3); K3.never: -4.9 points (-7.3 to -2.5); K3.k3p: +5.7 points (+3.4 to +8.0); K4: +4.7 points (+2.4 to +7.0).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard line in play (end of own turn t), own turn 1 | +0.9 (-0.3 to +2.1) | +1.5 (+0.1 to +2.9) FLAG | +1.2 (+0.3 to +2.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | +1.3 (-0.3 to +2.9) | +3.6 (+2.0 to +5.2) FLAG | +2.5 (+1.3 to +3.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | +2.2 (+0.5 to +3.9) FLAG | +3.2 (+1.6 to +4.8) FLAG | +2.7 (+1.5 to +3.9) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | +2.2 (+0.6 to +3.8) FLAG | +1.5 (+0.0 to +3.0) FLAG | +1.8 (+0.8 to +2.9) FLAG |
| K2 Kingambit in play, own turn 2 | +1.9 (+0.3 to +3.5) FLAG | +1.1 (-0.5 to +2.7) | +1.5 (+0.4 to +2.6) FLAG |
| K2 Kingambit in play, own turn 3 | +3.1 (+1.0 to +5.2) FLAG | +3.5 (+1.3 to +5.7) FLAG | +3.3 (+1.8 to +4.8) FLAG |
| K2 Kingambit in play, own turn 4 | +4.8 (+2.2 to +7.4) FLAG | +6.3 (+3.6 to +9.0) FLAG | +5.5 (+3.7 to +7.4) FLAG |
| K2 Kingambit in play, own turn 5 | +6.5 (+3.7 to +9.3) FLAG | +5.3 (+2.4 to +8.2) FLAG | +5.9 (+3.9 to +7.9) FLAG |
| K2 Kingambit in play, own turn 6 | +5.2 (+2.6 to +7.8) FLAG | +6.3 (+3.6 to +9.0) FLAG | +5.8 (+3.9 to +7.6) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +2.4 (+0.5 to +4.3) FLAG | +2.3 (+0.3 to +4.3) FLAG | +2.4 (+1.0 to +3.7) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +3.5 (+1.4 to +5.6) FLAG | +3.0 (+0.9 to +5.1) FLAG | +3.2 (+1.8 to +4.7) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.9 (+1.0 to +4.8) FLAG | +1.8 (-0.1 to +3.7) | +2.4 (+1.0 to +3.7) FLAG |
| G3 Pawniard in play, own turn 1 | +0.9 (-0.3 to +2.1) | +1.5 (+0.1 to +2.9) FLAG | +1.2 (+0.3 to +2.1) FLAG |
| G3 Pawniard in play, own turn 2 | -0.6 (-2.8 to +1.6) | +2.5 (+0.3 to +4.7) FLAG | +0.9 (-0.6 to +2.5) |
| G3 Pawniard in play, own turn 4 | -2.6 (-5.4 to +0.2) | -4.8 (-7.6 to -2.0) FLAG | -3.7 (-5.7 to -1.7) FLAG |
| G3 Pawniard in play, own turn 5 | -5.4 (-8.1 to -2.7) FLAG | -4.8 (-7.7 to -1.9) FLAG | -5.1 (-7.1 to -3.1) FLAG |
| G3 Kingambit in play, own turn 2 | +1.9 (+0.3 to +3.5) FLAG | +1.1 (-0.5 to +2.7) | +1.5 (+0.4 to +2.6) FLAG |
| G3 Kingambit in play, own turn 3 | +3.1 (+1.0 to +5.2) FLAG | +3.5 (+1.3 to +5.7) FLAG | +3.3 (+1.8 to +4.8) FLAG |
| G3 Kingambit in play, own turn 4 | +4.8 (+2.2 to +7.4) FLAG | +6.3 (+3.6 to +9.0) FLAG | +5.5 (+3.7 to +7.4) FLAG |
| G3 Kingambit in play, own turn 5 | +6.5 (+3.7 to +9.3) FLAG | +5.3 (+2.4 to +8.2) FLAG | +5.9 (+3.9 to +7.9) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -1.7 (-4.0 to +0.6) | -1.7 (-4.0 to +0.6) | -1.7 (-3.3 to -0.1) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -3.6 (-5.8 to -1.4) FLAG | -3.6 (-5.6 to -1.6) FLAG | -3.6 (-5.1 to -2.1) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -3.7 (-5.6 to -1.8) FLAG | -1.9 (-3.5 to -0.3) FLAG | -2.8 (-4.0 to -1.6) FLAG |
| G3 Alolan Muk in play, own turn 3 | +2.3 (+0.3 to +4.3) FLAG | +2.5 (+0.3 to +4.7) FLAG | +2.4 (+0.9 to +3.9) FLAG |
| G3 Alolan Muk in play, own turn 4 | +4.1 (+1.9 to +6.3) FLAG | +4.1 (+2.0 to +6.2) FLAG | +4.1 (+2.6 to +5.6) FLAG |
| G3 Alolan Muk in play, own turn 5 | +3.6 (+1.6 to +5.6) FLAG | +2.3 (+0.4 to +4.2) FLAG | +2.9 (+1.6 to +4.3) FLAG |
| G3 Glimmet in play, own turn 1 | +1.9 (+0.6 to +3.2) FLAG | +1.5 (+0.5 to +2.5) FLAG | +1.7 (+0.9 to +2.5) FLAG |
| G3 Glimmet in play, own turn 3 | -4.7 (-7.7 to -1.7) FLAG | -6.1 (-9.0 to -3.2) FLAG | -5.4 (-7.5 to -3.3) FLAG |
| G3 Glimmet in play, own turn 4 | -7.4 (-10.2 to -4.6) FLAG | -6.9 (-9.8 to -4.0) FLAG | -7.1 (-9.2 to -5.1) FLAG |
| G3 Glimmet in play, own turn 5 | -6.8 (-9.2 to -4.4) FLAG | -6.2 (-8.6 to -3.8) FLAG | -6.5 (-8.2 to -4.8) FLAG |
| G3 Glimmora in play, own turn 2 | +4.6 (+2.4 to +6.8) FLAG | +5.1 (+3.0 to +7.2) FLAG | +4.9 (+3.3 to +6.4) FLAG |
| G3 Glimmora in play, own turn 3 | +5.0 (+2.8 to +7.2) FLAG | +5.2 (+3.1 to +7.3) FLAG | +5.1 (+3.6 to +6.6) FLAG |
| G3 Glimmora in play, own turn 4 | +3.7 (+1.8 to +5.6) FLAG | +3.3 (+1.6 to +5.0) FLAG | +3.5 (+2.2 to +4.8) FLAG |
| G3 Glimmora in play, own turn 5 | +2.1 (+0.8 to +3.4) FLAG | +1.5 (+0.2 to +2.8) FLAG | +1.8 (+0.9 to +2.7) FLAG |
| G3 Regigigas in play, own turn 1 | +0.3 (-1.1 to +1.7) | +1.8 (+0.7 to +2.9) FLAG | +1.1 (+0.2 to +1.9) FLAG |
| G3 Regigigas in play, own turn 2 | +2.4 (+0.8 to +4.0) FLAG | +4.0 (+2.3 to +5.7) FLAG | +3.2 (+2.0 to +4.4) FLAG |
| G3 Regigigas in play, own turn 3 | +2.9 (+1.4 to +4.4) FLAG | +3.3 (+1.7 to +4.9) FLAG | +3.1 (+2.0 to +4.2) FLAG |
| G3 Regigigas in play, own turn 4 | +2.0 (+0.6 to +3.4) FLAG | +1.7 (+0.2 to +3.2) FLAG | +1.8 (+0.8 to +2.9) FLAG |
| G3 Regigigas in play, own turn 5 | +1.3 (-0.1 to +2.7) | +0.8 (-0.6 to +2.2) | +1.1 (+0.1 to +2.0) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | +3.9 (+1.8 to +6.0) FLAG | +3.7 (+1.7 to +5.7) FLAG | +3.8 (+2.4 to +5.2) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | +2.5 (+0.8 to +4.2) FLAG | +2.8 (+1.1 to +4.5) FLAG | +2.6 (+1.4 to +3.9) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | +0.9 (-0.4 to +2.2) | +1.6 (+0.5 to +2.7) FLAG | +1.2 (+0.4 to +2.1) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | +1.9 (+0.3 to +3.5) FLAG | +1.1 (-0.5 to +2.7) | +1.5 (+0.4 to +2.6) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | +3.1 (+1.0 to +5.2) FLAG | +3.5 (+1.3 to +5.7) FLAG | +3.3 (+1.8 to +4.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +4.8 (+2.2 to +7.4) FLAG | +6.3 (+3.6 to +9.0) FLAG | +5.5 (+3.7 to +7.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +6.5 (+3.7 to +9.3) FLAG | +5.3 (+2.4 to +8.2) FLAG | +5.9 (+3.9 to +7.9) FLAG |
| G5.any3 an empty own turn among turns 1-3 | -4.9 (-7.6 to -2.2) FLAG | -6.6 (-9.2 to -4.0) FLAG | -5.8 (-7.6 to -3.9) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +2.9 (+1.0 to +4.8) FLAG | +3.5 (+1.3 to +5.7) FLAG | +3.2 (+1.7 to +4.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +4.8 (+2.2 to +7.4) FLAG | +6.3 (+3.6 to +9.0) FLAG | +5.5 (+3.7 to +7.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +6.5 (+3.7 to +9.3) FLAG | +5.3 (+2.4 to +8.2) FLAG | +5.9 (+3.9 to +7.9) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.040 (-0.078 to -0.001) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, deck01.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): none flagged
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn +3.2 points (+1.8 to +4.4); P2 both Glimmora had their turn +5.9 points (+2.9 to +9.6); P2 the first Glimmora placed had its turn +3.2 points (+1.6 to +4.7); P2 the second Glimmora placed had its turn +5.9 points (+2.8 to +9.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.8 points (-3.7 to -0.2)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn +2.5 points (+0.9 to +4.0); P2 both Glimmora had their turn +5.1 points (+2.9 to +7.6); P2 the first Glimmora placed had its turn +3.1 points (+0.7 to +5.3); P2 the second Glimmora placed had its turn +4.5 points (+2.0 to +7.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.2 points (-3.6 to -0.4); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.7 points (-4.9 to -0.8)
- C-bot (per-game bootstrap): P2 both Glimmora had their turn +7.0 points (+4.5 to +9.7); P2 the second Glimmora placed had its turn +6.1 points (+3.4 to +9.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -6.0 points (-8.4 to -3.5); P4 ready at the winning moment: Knocks out their strongest +2.2 points (+0.9 to +3.8); P5 plan reached in time: Knocks out their strongest +1.4 points (+0.2 to +2.8)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn +6.5 points (+4.3 to +8.7); P2 both Glimmora had their turn +5.7 points (+3.4 to +8.0); P2 the first Glimmora placed had its turn +4.8 points (+2.7 to +6.9); P2 the second Glimmora placed had its turn +7.4 points (+4.7 to +10.1); P4 ready at the winning moment: Knocks out their strongest +5.0 points (+3.0 to +7.0); P4 ready at the winning moment: Wins outright (a lower bound) +5.0 points (+3.0 to +7.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -6.9 points (-9.1 to -4.7); P5 plan reached in time: Knocks out their strongest +5.8 points (+3.7 to +7.9); P5 plan reached in time: Wins outright (a lower bound) +5.8 points (+3.7 to +7.9)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn +4.0 points (+2.2 to +5.8); P2 both Glimmora had their turn +7.9 points (+4.9 to +10.9); P2 the first Glimmora placed had its turn +4.5 points (+2.4 to +6.6); P2 the second Glimmora placed had its turn +7.4 points (+4.3 to +10.5); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +3.3 points (+0.6 to +6.0); P4 ready at the winning moment: Knocks out their strongest +7.3 points (+4.9 to +9.7); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -8.2 points (-10.4 to -6.0); P5 plan reached in time: Knocks out their strongest +7.7 points (+5.2 to +10.2)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn +2.4 points (+0.9 to +3.9); P2 both Glimmora had their turn +8.3 points (+5.5 to +11.1); P2 the first Glimmora placed had its turn +3.1 points (+1.2 to +5.0); P2 the second Glimmora placed had its turn +7.6 points (+4.9 to +10.3); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left -2.6 points (-4.2 to -1.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -6.0 points (-8.3 to -3.7); P4 ready at the winning moment: Knocks out their strongest +7.0 points (+4.7 to +9.3); P4 ready at the winning moment: Wins outright (a lower bound) +7.0 points (+4.7 to +9.3); P4 not ready, ready 1 turn late -1.0 points (-2.0 to -0.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -4.5 points (-6.4 to -2.6); P5 plan reached in time: Knocks out their strongest +6.0 points (+3.8 to +8.2); P5 plan reached in time: Wins outright (a lower bound) +6.0 points (+3.8 to +8.2)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +6.6 points (+4.4 to +8.8); P2 both Glimmora had their turn +5.6 points (+3.3 to +7.9); P2 the first Glimmora placed had its turn +4.8 points (+2.7 to +6.9); P2 the second Glimmora placed had its turn +7.4 points (+4.7 to +10.1); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.4 points (-2.6 to -0.2)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn +2.4 points (+0.9 to +3.9); P2 both Glimmora had their turn +8.2 points (+5.4 to +11.0); P2 the first Glimmora placed had its turn +3.1 points (+1.2 to +5.0); P2 the second Glimmora placed had its turn +7.5 points (+4.8 to +10.2); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +4.5 points (+2.1 to +6.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.2 points (-4.4 to -0.0); P4 the moment came and Kingambit was never ready in the deal +3.6 points (+2.1 to +5.1); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.6 points (-4.0 to -1.2)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K1 Pawniard line in play (end of own turn t), own turn 1 +1.2 points; K1 Pawniard line in play (end of own turn t), own turn 2 +2.5 points; K1 Pawniard line in play (end of own turn t), own turn 3 +2.7 points; K1 Pawniard line in play (end of own turn t), own turn 4 +1.8 points; K2 Kingambit in play, own turn 2 +1.5 points; K2 Kingambit in play, own turn 3 +3.3 points; K2 Kingambit in play, own turn 4 +5.5 points; K2 Kingambit in play, own turn 5 +5.9 points; K2 Kingambit in play, own turn 6 +5.8 points; K6 Muk and Regigigas both in play, own turn 3 +2.4 points.
Gives up (flagged, pooled): none flagged.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by8 +2.1; K3.never -2.1; C-his, seat-matched: K3.by7 +2.4; K3.by8 +2.4; K3.never -2.8; C-bot: K3.k3p +1.5; C-fixed fast: K3.by5 +4.0; K3.by6 +3.8; K3.by7 +3.8; K3.by8 +3.8; K3.never -3.8; K3.k3p +4.4; K4 +3.8; K5 -2.0; C-fixed medium: K3.by5 +2.2; K3.by6 +6.5; K3.by7 +6.5; K3.by8 +6.5; K3.never -6.5; K3.k3p +6.3; K4 +6.3; K5 -2.8; C-fixed slow: K3.by7 +4.9; K3.by8 +7.4; K3.never -7.4; K3.k3p +8.2; K4 +7.2; C-fixed reference (fast pace, 190-HP Mega ex): K3.by5 +4.2; K3.by6 +4.0; K3.by7 +4.0; K3.by8 +4.0; K3.never -4.0; K3.k3p +4.6; K4 +4.0; K5 -2.0; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by7 +3.4; K3.by8 +5.9; K3.by9 +5.6; K3.by10 +4.9; K3.never -4.9; K3.k3p +5.7; K4 +4.7.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## B (card-list id 78b2ba4b7e24)

Changes: ['-2 Lucky Ice Pop B2 145', '+1 Rare Candy A3 144', '+1 Copycat B1 225']

Copycat decisions with a Copycat in hand: 21,744; the valuation and the fallback rule disagree at 9,460 of 21,744 Copycat decisions (43.5%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.4289.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.05955; in 8 cards: 0.08964.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 51/58/64/70/76%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 2,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 30.1% (27.3-33.0) | 28.2% (25.5-31.1) | 29.1% (27.2-31.2) |

Plan lines under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 88.8% / 95.8% [78-97] | 83.4% / 93.2% [68-94] | 86.1% / 94.5% [73-95] |
| P2 both Glimmora had their turn | 42.2% / 73.6% [30-55] | 38.2% / 71.0% [24-54] | 40.2% / 72.3% [28-52] |
| P2 the first Glimmora placed had its turn | 85.8% / 92.4% [76-95] | 76.8% / 85.0% [60-91] | 81.3% / 88.7% [69-93] |
| P2 the second Glimmora placed had its turn | 45.2% / 73.0% [32-58] | 44.8% / 71.4% [31-60] | 45.0% / 72.2% [32-57] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [12-16] | 10.0% [9-11] | 11.9% [11-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 6.6% / 53.4% [1-15] | 7.6% / 52.0% [2-15] | 7.1% / 52.7% [2-15] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 21.6% / 62.0% [16-28] | 29.6% / 67.0% [23-37] | 25.6% / 64.5% [20-32] |
| P4 ready at the winning moment: Knocks out their strongest | 17.4% / 44.6% [4-34] | 16.2% / 42.4% [4-32] | 16.8% / 43.5% [3-33] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.0% / 30.2% [0-9] | 1.8% / 28.0% [0-6] | 2.4% / 29.1% [0-7] |
| P4 not ready, ready 1 turn late | 5.2% / 49.0% [0-14] | 5.0% / 45.6% [0-12] | 5.1% / 47.3% [0-13] |
| P4 not ready, ready 2 or more turns late | 0.8% / 44.6% [0-2] | 1.4% / 42.0% [0-4] | 1.1% / 43.3% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 6.4% / 50.2% [0-15] | 5.4% / 46.0% [0-14] | 5.9% / 48.1% [0-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 26.4% / 53.6% [7-51] | 31.4% / 57.6% [10-56] | 28.9% / 55.6% [9-52] |
| P5 plan reached in time: Knocks out their strongest | 23.4% / 67.2% [7-41] | 22.6% / 63.2% [8-40] | 23.0% / 65.2% [8-40] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.0% / 46.8% [0-9] | 2.2% / 42.8% [0-7] | 2.6% / 44.8% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 58.4% of 149 [28-81] | 57.9% of 140 [27-83] | 58.1% of 289 [29-82] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 10.1% of 149 [0-41] | 6.4% of 140 [0-29] | 8.3% of 289 [0-36] |
| P4 not ready, ready 1 turn late | 17.4% of 149 [0-62] | 17.9% of 140 [0-49] | 17.6% of 289 [0-54] |
| P4 not ready, ready 2 or more turns late | 2.7% of 149 [0-10] | 5.0% of 140 [0-16] | 3.8% of 289 [0-12] |
| P4 the moment came and Kingambit was never ready in the deal | 21.5% of 149 [0-40] | 19.3% of 140 [0-45] | 20.4% of 289 [0-42] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +2.5 points (+1.4 to +3.6); P2.g1: +2.4 points (+1.4 to +3.3); P3.grimer_muk: -4.0 points (-7.2 to -0.9); P4.ko: +4.8 points (+0.9 to +9.3); P4.nomoment: -1.6 points (-2.7 to -0.6); P5.ko: +5.4 points (+1.5 to +10.0).

Plan lines under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 88.6% / 96.6% [74-98] | 91.0% / 95.4% [82-97] | 89.8% / 96.0% [81-96] |
| P2 both Glimmora had their turn | 45.2% / 71.6% [27-63] | 35.8% / 80.6% [26-45] | 40.5% / 76.1% [31-52] |
| P2 the first Glimmora placed had its turn | 86.2% / 94.0% [72-96] | 87.2% / 88.2% [79-97] | 86.7% / 91.1% [78-93] |
| P2 the second Glimmora placed had its turn | 47.6% / 70.6% [28-66] | 39.6% / 76.2% [30-53] | 43.6% / 73.4% [33-56] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-16] | 10.0% [9-11] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 1.4% / 44.4% [0-3] | 14.0% / 77.6% [0-33] | 7.7% / 61.0% [0-18] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 20.8% / 58.8% [15-27] | 32.4% / 88.6% [19-42] | 26.6% / 73.7% [18-34] |
| P4 ready at the winning moment: Knocks out their strongest | 22.0% / 46.2% [3-42] | 6.0% / 63.0% [0-21] | 14.0% / 54.6% [4-28] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.0% / 30.2% [0-18] | 0.0% / 57.0% [0-0] | 3.0% / 43.6% [0-11] |
| P4 not ready, ready 1 turn late | 7.2% / 44.6% [0-20] | 0.0% / 76.6% [0-0] | 3.6% / 60.6% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.2% / 38.6% [0-4] | 0.0% / 76.6% [0-0] | 0.6% / 57.6% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 8.0% / 45.4% [0-17] | 0.0% / 76.6% [0-0] | 4.0% / 61.0% [0-10] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 24.2% / 48.4% [5-52] | 17.4% / 74.4% [1-41] | 20.8% / 61.4% [7-39] |
| P5 plan reached in time: Knocks out their strongest | 30.4% / 67.8% [9-52] | 6.0% / 82.6% [0-21] | 18.2% / 75.2% [6-36] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.2% / 43.6% [0-19] | 0.0% / 76.6% [0-0] | 3.1% / 60.1% [0-12] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 57.3% of 192 [20-76] | 100.0% of 30 [100-100] | 63.1% of 222 [35-84] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 15.6% of 192 [0-52] | 0.0% of 30 [0-0] | 13.5% of 222 [0-43] |
| P4 not ready, ready 1 turn late | 18.8% of 192 [0-69] | 0.0% of 30 [0-0] | 16.2% of 222 [0-48] |
| P4 not ready, ready 2 or more turns late | 3.1% of 192 [0-12] | 0.0% of 30 [0-0] | 2.7% of 222 [0-8] |
| P4 the moment came and Kingambit was never ready in the deal | 20.8% of 192 [0-38] | 0.0% of 30 [0-0] | 18.0% of 222 [0-33] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +1.7 points (+1.0 to +2.5); P2.both: +4.6 points (+1.9 to +8.4); P2.g1: +2.6 points (+1.4 to +3.8); P2.g2: +3.7 points (+1.1 to +7.4); P3.grimer_muk: -3.9 points (-6.3 to -1.8); P4.ko: +2.2 points (+0.5 to +4.5); P4.nomoment: -2.2 points (-4.0 to -0.6); P5.ko: +2.4 points (+0.8 to +4.6).

Plan lines under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 92.8% / 93.0% [89-96] | 86.6% / 87.4% [82-91] | 89.7% / 90.2% [87-92] |
| P2 both Glimmora had their turn | 43.8% / 49.4% [37-51] | 36.0% / 40.4% [30-43] | 39.9% / 44.9% [35-46] |
| P2 the first Glimmora placed had its turn | 88.6% [84-93] | 76.6% / 76.8% [70-83] | 82.6% / 82.7% [78-87] |
| P2 the second Glimmora placed had its turn | 48.0% / 52.2% [42-54] | 46.0% / 49.2% [41-52] | 47.0% / 50.7% [42-52] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17] | 10.0% [8-12] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 19.4% / 30.8% [13-26] | 16.2% / 26.0% [12-21] | 17.8% / 28.4% [13-23] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 28.4% / 38.6% [24-33] | 41.8% / 49.0% [37-47] | 35.1% / 43.8% [31-39] |
| P4 ready at the winning moment: Knocks out their strongest | 11.0% / 17.6% [5-19] | 9.0% / 16.0% [4-14] | 10.0% / 16.8% [5-16] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.2% / 7.8% [0-4] | 0.4% / 7.4% [0-1] | 0.8% / 7.6% [0-2] |
| P4 not ready, ready 1 turn late | 5.2% / 13.2% [2-9] | 5.4% / 13.4% [3-9] | 5.3% / 13.3% [2-8] |
| P4 not ready, ready 2 or more turns late | 1.0% / 9.0% [0-2] | 0.4% / 8.4% [0-1] | 0.7% / 8.7% [0-1] |
| P4 the moment came and Kingambit was never ready in the deal | 8.0% / 16.0% [3-14] | 6.0% / 14.0% [2-11] | 7.0% / 15.0% [3-12] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 66.8% / 73.4% [54-78] | 71.2% / 78.2% [60-82] | 69.0% / 75.8% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 17.2% / 25.2% [9-26] | 14.8% / 22.8% [8-22] | 16.0% / 24.0% [9-24] |
| P5 plan reached in time: Wins outright (a lower bound) | 1.2% / 9.2% [0-4] | 0.6% / 8.6% [0-2] | 0.9% / 8.9% [0-3] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 43.7% of 126 [24-66] | 43.3% of 104 [32-54] | 43.5% of 230 [29-59] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.8% of 126 [0-17] | 1.9% of 104 [0-8] | 3.5% of 230 [0-11] |
| P4 not ready, ready 1 turn late | 20.6% of 126 [8-33] | 26.0% of 104 [17-37] | 23.0% of 230 [13-32] |
| P4 not ready, ready 2 or more turns late | 4.0% of 126 [1-8] | 1.9% of 104 [0-5] | 3.0% of 230 [0-6] |
| P4 the moment came and Kingambit was never ready in the deal | 31.7% of 126 [16-47] | 28.8% of 104 [15-42] | 30.4% of 230 [16-44] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.both: +4.4 points (+2.4 to +6.4); P2.g1: +2.1 points (+0.9 to +3.5); P2.g2: +3.3 points (+1.3 to +5.3); P3.pawn_promo: +2.5 points (+0.5 to +4.5); P3.grimer_muk: -5.9 points (-7.7 to -4.1); P4.ko: +3.5 points (+1.6 to +5.8); P4.late2p: -1.3 points (-2.3 to -0.5); P4.never: -1.3 points (-2.7 to -0.1); P5.ko: +2.5 points (+1.1 to +4.3).

Plan lines under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.0% [82-88, Wilson] | 56.8% [52-61, Wilson] | 70.9% [68-74, Wilson] |
| P2 both Glimmora had their turn | 30.8% [27-35, Wilson] | 8.2% [6-11, Wilson] | 19.5% [17-22, Wilson] |
| P2 the first Glimmora placed had its turn | 80.6% [77-84, Wilson] | 33.6% [30-38, Wilson] | 57.1% [54-60, Wilson] |
| P2 the second Glimmora placed had its turn | 35.2% [31-39, Wilson] | 31.4% [27-36, Wilson] | 33.3% [30-36, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 20.6% [17-24, Wilson] | 18.2% [15-22, Wilson] | 19.4% [17-22, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 48.6% [44-53, Wilson] | 54.0% [50-58, Wilson] | 51.3% [48-54, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 30.2% [26-34, Wilson] | 11.6% [9-15, Wilson] | 20.9% [18-24, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 30.2% [26-34, Wilson] | 11.6% [9-15, Wilson] | 20.9% [18-24, Wilson] |
| P4 not ready, ready 1 turn late | 1.2% [1-3, Wilson] | 0.6% [0-2, Wilson] | 0.9% [0-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 15.2% [12-19, Wilson] | 13.2% [11-16, Wilson] | 14.2% [12-17, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 53.4% [49-58, Wilson] | 74.6% [71-78, Wilson] | 64.0% [61-67, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 31.4% [27-36, Wilson] | 12.2% [10-15, Wilson] | 21.8% [19-24, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 31.4% [27-36, Wilson] | 12.2% [10-15, Wilson] | 21.8% [19-24, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 64.8% of 233 [58-71, Wilson] | 45.7% of 127 [37-54, Wilson] | 58.1% of 360 [53-63, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 64.8% of 233 [58-71, Wilson] | 45.7% of 127 [37-54, Wilson] | 58.1% of 360 [53-63, Wilson] |
| P4 not ready, ready 1 turn late | 2.6% of 233 [1-6, Wilson] | 2.4% of 127 [1-7, Wilson] | 2.5% of 360 [1-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 233 [0-2, Wilson] | 0.0% of 127 [0-3, Wilson] | 0.0% of 360 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 32.6% of 233 [27-39, Wilson] | 52.0% of 127 [43-60, Wilson] | 39.4% of 360 [35-45, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: +4.8 points (+3.0 to +6.6); P2.both: +2.1 points (+0.2 to +4.0); P2.g1: +4.2 points (+2.6 to +5.8); P2.g2: +2.7 points (+0.5 to +4.9); P3.grimer_muk: -3.7 points (-5.4 to -2.0); P4.ko: +10.7 points (+8.7 to +12.7); P4.win: +10.7 points (+8.7 to +12.7); P4.never: -4.8 points (-6.8 to -2.8); P4.nomoment: -5.7 points (-7.3 to -4.1); P5.ko: +10.5 points (+8.6 to +12.4); P5.win: +10.5 points (+8.6 to +12.4).

Plan lines under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 92.0% [89-94, Wilson] | 84.4% [81-87, Wilson] | 88.2% [86-90, Wilson] |
| P2 both Glimmora had their turn | 40.8% [37-45, Wilson] | 33.4% [29-38, Wilson] | 37.1% [34-40, Wilson] |
| P2 the first Glimmora placed had its turn | 90.2% [87-93, Wilson] | 82.0% [78-85, Wilson] | 86.1% [84-88, Wilson] |
| P2 the second Glimmora placed had its turn | 42.6% [38-47, Wilson] | 35.8% [32-40, Wilson] | 39.2% [36-42, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 27.8% [24-32, Wilson] | 24.2% [21-28, Wilson] | 26.0% [23-29, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 42.6% [38-47, Wilson] | 53.4% [49-58, Wilson] | 48.0% [45-51, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 40.4% [36-45, Wilson] | 26.4% [23-30, Wilson] | 33.4% [31-36, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 1.8% [1-3, Wilson] | 1.4% [1-3, Wilson] | 1.6% [1-3, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 14.8% [12-18, Wilson] | 18.4% [15-22, Wilson] | 16.6% [14-19, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 43.0% [39-47, Wilson] | 53.8% [49-58, Wilson] | 48.4% [45-51, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 42.2% [38-47, Wilson] | 27.8% [24-32, Wilson] | 35.0% [32-38, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 70.9% of 285 [65-76, Wilson] | 57.1% of 231 [51-63, Wilson] | 64.7% of 516 [61-69, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 285 [0-1, Wilson] | 0.0% of 231 [0-2, Wilson] | 0.0% of 516 [0-1, Wilson] |
| P4 not ready, ready 1 turn late | 3.2% of 285 [2-6, Wilson] | 3.0% of 231 [1-6, Wilson] | 3.1% of 516 [2-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 285 [0-1, Wilson] | 0.0% of 231 [0-2, Wilson] | 0.0% of 516 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 26.0% of 285 [21-31, Wilson] | 39.8% of 231 [34-46, Wilson] | 32.2% of 516 [28-36, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: +2.5 points (+1.1 to +3.9); P2.both: +3.9 points (+1.3 to +6.5); P2.g1: +4.3 points (+2.7 to +5.9); P3.pawn_promo: +3.8 points (+1.6 to +6.0); P3.grimer_muk: -5.8 points (-8.0 to -3.6); P4.ko: +13.1 points (+10.8 to +15.4); P4.never: -5.6 points (-7.8 to -3.4); P4.nomoment: -7.0 points (-8.7 to -5.3); P5.ko: +12.6 points (+10.3 to +14.9).

Plan lines under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 96.6% [95-98, Wilson] | 91.8% [89-94, Wilson] | 94.2% [93-95, Wilson] |
| P2 both Glimmora had their turn | 75.4% [71-79, Wilson] | 65.6% [61-70, Wilson] | 70.5% [68-73, Wilson] |
| P2 the first Glimmora placed had its turn | 92.8% [90-95, Wilson] | 84.4% [81-87, Wilson] | 88.6% [86-90, Wilson] |
| P2 the second Glimmora placed had its turn | 79.2% [75-83, Wilson] | 73.0% [69-77, Wilson] | 76.1% [73-79, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 2.6% [2-4, Wilson] | 7.0% [5-10, Wilson] | 4.8% [4-6, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 20.4% [17-24, Wilson] | 31.2% [27-35, Wilson] | 25.8% [23-29, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 54.8% [50-59, Wilson] | 49.6% [45-54, Wilson] | 52.2% [49-55, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 54.8% [50-59, Wilson] | 49.6% [45-54, Wilson] | 52.2% [49-55, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.4% [0-1, Wilson] | 0.2% [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 11.6% [9-15, Wilson] | 8.6% [6-11, Wilson] | 10.1% [8-12, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 33.6% [30-38, Wilson] | 41.4% [37-46, Wilson] | 37.5% [35-41, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 54.8% [50-59, Wilson] | 50.0% [46-54, Wilson] | 52.4% [49-55, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 54.8% [50-59, Wilson] | 50.0% [46-54, Wilson] | 52.4% [49-55, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 82.5% of 332 [78-86, Wilson] | 84.6% of 293 [80-88, Wilson] | 83.5% of 625 [80-86, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 82.5% of 332 [78-86, Wilson] | 84.6% of 293 [80-88, Wilson] | 83.5% of 625 [80-86, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 332 [0-1, Wilson] | 0.7% of 293 [0-2, Wilson] | 0.3% of 625 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 332 [0-1, Wilson] | 0.0% of 293 [0-1, Wilson] | 0.0% of 625 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 17.5% of 332 [14-22, Wilson] | 14.7% of 293 [11-19, Wilson] | 16.2% of 625 [13-19, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.7 points (+0.6 to +2.8); P2.both: +8.6 points (+6.4 to +10.8); P2.g1: +2.9 points (+1.5 to +4.3); P2.g2: +7.4 points (+5.3 to +9.5); P3.pawn_promo: -2.5 points (-3.8 to -1.2); P3.grimer_muk: -8.2 points (-10.1 to -6.3); P4.ko: +8.6 points (+6.8 to +10.4); P4.win: +8.6 points (+6.8 to +10.4); P4.late1: -1.6 points (-2.4 to -0.8); P4.never: -2.0 points (-3.2 to -0.8); P4.nomoment: -5.0 points (-6.4 to -3.6); P5.ko: +7.0 points (+5.3 to +8.7); P5.win: +7.0 points (+5.3 to +8.7).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 85.6% [82-88, Wilson] | 56.8% [52-61, Wilson] | 71.2% [68-74, Wilson] |
| P2 both Glimmora had their turn | 31.6% [28-36, Wilson] | 8.2% [6-11, Wilson] | 19.9% [18-22, Wilson] |
| P2 the first Glimmora placed had its turn | 80.6% [77-84, Wilson] | 33.6% [30-38, Wilson] | 57.1% [54-60, Wilson] |
| P2 the second Glimmora placed had its turn | 36.6% [32-41, Wilson] | 31.4% [27-36, Wilson] | 34.0% [31-37, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 25.2% [22-29, Wilson] | 18.8% [16-22, Wilson] | 22.0% [20-25, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 48.6% [44-53, Wilson] | 54.0% [50-58, Wilson] | 51.3% [48-54, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.4% [3-7, Wilson] | 1.2% [1-3, Wilson] | 2.8% [2-4, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.4% [3-7, Wilson] | 1.2% [1-3, Wilson] | 2.8% [2-4, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 5.2% [4-8, Wilson] | 1.6% [1-3, Wilson] | 3.4% [2-5, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.4% [88-93, Wilson] | 97.2% [95-98, Wilson] | 93.8% [92-95, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.4% [3-7, Wilson] | 1.2% [1-3, Wilson] | 2.8% [2-4, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.4% [3-7, Wilson] | 1.2% [1-3, Wilson] | 2.8% [2-4, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 45.8% of 48 [33-60, Wilson] | 42.9% of 14 [21-67, Wilson] | 45.2% of 62 [33-57, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 45.8% of 48 [33-60, Wilson] | 42.9% of 14 [21-67, Wilson] | 45.2% of 62 [33-57, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 48 [0-7, Wilson] | 0.0% of 14 [0-22, Wilson] | 0.0% of 62 [0-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 48 [0-7, Wilson] | 0.0% of 14 [0-22, Wilson] | 0.0% of 62 [0-6, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 54.2% of 48 [40-67, Wilson] | 57.1% of 14 [33-79, Wilson] | 54.8% of 62 [43-67, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +5.1 points (+3.3 to +6.9); P2.both: +2.1 points (+0.2 to +4.0); P2.g1: +4.2 points (+2.6 to +5.8); P2.g2: +3.0 points (+0.8 to +5.2); P3.pawn_promo: +2.7 points (+0.7 to +4.7); P3.grimer_muk: -3.7 points (-5.4 to -2.0); P4.nomoment: -1.4 points (-2.2 to -0.6).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 96.6% [95-98, Wilson] | 91.8% [89-94, Wilson] | 94.2% [93-95, Wilson] |
| P2 both Glimmora had their turn | 77.2% [73-81, Wilson] | 67.8% [64-72, Wilson] | 72.5% [70-75, Wilson] |
| P2 the first Glimmora placed had its turn | 92.8% [90-95, Wilson] | 84.4% [81-87, Wilson] | 88.6% [86-90, Wilson] |
| P2 the second Glimmora placed had its turn | 81.0% [77-84, Wilson] | 75.2% [71-79, Wilson] | 78.1% [75-81, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 44.2% [40-49, Wilson] | 38.0% [34-42, Wilson] | 41.1% [38-44, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 34.0% [30-38, Wilson] | 43.8% [40-48, Wilson] | 38.9% [36-42, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.2% [3-6, Wilson] | 6.2% [4-9, Wilson] | 5.2% [4-7, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.2% [3-6, Wilson] | 6.2% [4-9, Wilson] | 5.2% [4-7, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 14.0% [11-17, Wilson] | 12.6% [10-16, Wilson] | 13.3% [11-16, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 81.8% [78-85, Wilson] | 81.2% [78-84, Wilson] | 81.5% [79-84, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.2% [3-6, Wilson] | 6.2% [4-9, Wilson] | 5.2% [4-7, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.2% [3-6, Wilson] | 6.2% [4-9, Wilson] | 5.2% [4-7, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 23.1% of 91 [16-33, Wilson] | 33.0% of 94 [24-43, Wilson] | 28.1% of 185 [22-35, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 23.1% of 91 [16-33, Wilson] | 33.0% of 94 [24-43, Wilson] | 28.1% of 185 [22-35, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 91 [0-4, Wilson] | 0.0% of 94 [0-4, Wilson] | 0.0% of 185 [0-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 91 [0-4, Wilson] | 0.0% of 94 [0-4, Wilson] | 0.0% of 185 [0-2, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 76.9% of 91 [67-84, Wilson] | 67.0% of 94 [57-76, Wilson] | 71.9% of 185 [65-78, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: +1.7 points (+0.6 to +2.8); P2.both: +9.0 points (+6.9 to +11.1); P2.g1: +2.9 points (+1.5 to +4.3); P2.g2: +7.8 points (+5.7 to +9.9); P3.pawn_promo: +5.8 points (+3.9 to +7.7); P3.grimer_muk: -4.7 points (-6.5 to -2.9); P4.never: +3.4 points (+2.2 to +4.6); P4.nomoment: -2.5 points (-3.5 to -1.5).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 31.7% (28.9-34.6) | 24.2% (21.6-27.0) | 27.9% (26.0-30.0) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 59.8% (56.7-62.8) | 56.3% (53.2-59.3) | 58.0% (55.9-60.2) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 73.0% (70.2-75.7) | 69.3% (66.4-72.1) | 71.2% (69.1-73.1) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 78.4% (75.7-80.8) | 76.5% (73.8-79.0) | 77.5% (75.6-79.2) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 81.7% (79.2-84.0) | 80.8% (78.2-83.1) | 81.2% (79.5-82.9) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 83.6% (81.2-85.8) | 81.9% (79.4-84.2) | 82.8% (81.0-84.3) |
| K2 Kingambit in play, own turn 2 | 22.2% (19.7-24.9) | 19.8% (17.4-22.4) | 21.0% (19.3-22.8) |
| K2 Kingambit in play, own turn 3 | 39.5% (36.5-42.6) | 37.2% (34.3-40.2) | 38.4% (36.2-40.5) |
| K2 Kingambit in play, own turn 4 | 55.7% (52.6-58.8) | 55.9% (52.8-58.9) | 55.8% (53.6-58.0) |
| K2 Kingambit in play, own turn 5 | 69.0% (66.1-71.8) | 68.3% (65.4-71.1) | 68.7% (66.6-70.6) |
| K2 Kingambit in play, own turn 6 | 77.7% (75.0-80.2) | 75.7% (72.9-78.3) | 76.7% (74.8-78.5) |
| K6 Muk and Regigigas both in play, own turn 3 | 24.6% (22.0-27.4) | 26.2% (23.6-29.0) | 25.4% (23.5-27.4) |
| K6 Muk and Regigigas both in play, own turn 4 | 34.3% (31.4-37.3) | 33.9% (31.0-36.9) | 34.1% (32.1-36.2) |
| K6 Muk and Regigigas both in play, own turn 5 | 39.5% (36.5-42.6) | 39.4% (36.4-42.5) | 39.5% (37.3-41.6) |
| G3 Pawniard in play, own turn 1 | 59.8% (56.7-62.8) | 56.3% (53.2-59.3) | 58.0% (55.9-60.2) |
| G3 Pawniard in play, own turn 2 | 50.8% (47.7-53.9) | 49.5% (46.4-52.6) | 50.1% (48.0-52.3) |
| G3 Pawniard in play, own turn 3 | 38.9% (35.9-42.0) | 39.3% (36.3-42.4) | 39.1% (37.0-41.3) |
| G3 Pawniard in play, own turn 4 | 26.0% (23.4-28.8) | 24.9% (22.3-27.7) | 25.4% (23.6-27.4) |
| G3 Pawniard in play, own turn 5 | 14.6% (12.5-16.9) | 13.6% (11.6-15.9) | 14.1% (12.6-15.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 2 | 22.2% (19.7-24.9) | 19.8% (17.4-22.4) | 21.0% (19.3-22.8) |
| G3 Kingambit in play, own turn 3 | 39.5% (36.5-42.6) | 37.2% (34.3-40.2) | 38.4% (36.2-40.5) |
| G3 Kingambit in play, own turn 4 | 55.7% (52.6-58.8) | 55.9% (52.8-58.9) | 55.8% (53.6-58.0) |
| G3 Kingambit in play, own turn 5 | 69.0% (66.1-71.8) | 68.3% (65.4-71.1) | 68.7% (66.6-70.6) |
| G3 Alolan Grimer in play, own turn 1 | 56.2% (53.1-59.2) | 56.3% (53.2-59.3) | 56.2% (54.1-58.4) |
| G3 Alolan Grimer in play, own turn 2 | 45.1% (42.0-48.2) | 46.1% (43.0-49.2) | 45.6% (43.4-47.8) |
| G3 Alolan Grimer in play, own turn 3 | 37.0% (34.1-40.0) | 36.0% (33.1-39.0) | 36.5% (34.4-38.6) |
| G3 Alolan Grimer in play, own turn 4 | 27.7% (25.0-30.6) | 28.6% (25.9-31.5) | 28.1% (26.2-30.2) |
| G3 Alolan Grimer in play, own turn 5 | 21.8% (19.4-24.5) | 22.7% (20.2-25.4) | 22.2% (20.5-24.1) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Alolan Muk in play, own turn 2 | 22.3% (19.8-25.0) | 22.3% (19.8-25.0) | 22.3% (20.5-24.2) |
| G3 Alolan Muk in play, own turn 3 | 35.2% (32.3-38.2) | 37.4% (34.5-40.4) | 36.3% (34.2-38.4) |
| G3 Alolan Muk in play, own turn 4 | 47.2% (44.1-50.3) | 46.9% (43.8-50.0) | 47.0% (44.9-49.2) |
| G3 Alolan Muk in play, own turn 5 | 53.9% (50.8-57.0) | 53.8% (50.7-56.9) | 53.9% (51.7-56.0) |
| G3 Glimmet in play, own turn 1 | 82.4% (79.9-84.6) | 86.5% (84.2-88.5) | 84.5% (82.8-86.0) |
| G3 Glimmet in play, own turn 2 | 52.0% (48.9-55.1) | 54.6% (51.5-57.7) | 53.3% (51.1-55.5) |
| G3 Glimmet in play, own turn 3 | 37.6% (34.7-40.6) | 36.8% (33.9-39.8) | 37.2% (35.1-39.3) |
| G3 Glimmet in play, own turn 4 | 22.7% (20.2-25.4) | 22.4% (19.9-25.1) | 22.6% (20.8-24.4) |
| G3 Glimmet in play, own turn 5 | 13.7% (11.7-16.0) | 11.0% (9.2-13.1) | 12.3% (11.0-13.9) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Glimmora in play, own turn 2 | 66.6% (63.6-69.5) | 69.6% (66.7-72.4) | 68.1% (66.0-70.1) |
| G3 Glimmora in play, own turn 3 | 84.6% (82.2-86.7) | 85.8% (83.5-87.8) | 85.2% (83.6-86.7) |
| G3 Glimmora in play, own turn 4 | 93.5% (91.8-94.9) | 94.1% (92.5-95.4) | 93.8% (92.7-94.8) |
| G3 Glimmora in play, own turn 5 | 97.1% (95.9-98.0) | 97.6% (96.5-98.4) | 97.3% (96.6-98.0) |
| G3 Regigigas in play, own turn 1 | 58.4% (55.3-61.4) | 53.0% (49.9-56.1) | 55.7% (53.5-57.9) |
| G3 Regigigas in play, own turn 2 | 70.4% (67.5-73.1) | 67.3% (64.3-70.1) | 68.8% (66.8-70.8) |
| G3 Regigigas in play, own turn 3 | 76.5% (73.8-79.0) | 74.6% (71.8-77.2) | 75.5% (73.6-77.4) |
| G3 Regigigas in play, own turn 4 | 79.5% (76.9-81.9) | 77.6% (74.9-80.1) | 78.5% (76.7-80.3) |
| G3 Regigigas in play, own turn 5 | 80.2% (77.6-82.6) | 79.0% (76.4-81.4) | 79.6% (77.8-81.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 83.3% (80.9-85.5) | 82.6% (80.1-84.8) | 83.0% (81.2-84.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 95.0% (93.5-96.2) | 94.8% (93.2-96.0) | 94.9% (93.8-95.8) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 98.0% (96.9-98.7) | 98.8% (97.9-99.3) | 98.4% (97.8-98.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 99.6% (99.0-99.8) | 99.7% (99.1-99.9) | 99.7% (99.3-99.8) |
| G4.s2 a Stage 2 in play, own turn 2 | 22.2% (19.7-24.9) | 19.8% (17.4-22.4) | 21.0% (19.3-22.8) |
| G4.s2 a Stage 2 in play, own turn 3 | 39.5% (36.5-42.6) | 37.2% (34.3-40.2) | 38.4% (36.2-40.5) |
| G4.s2 a Stage 2 in play, own turn 4 | 55.7% (52.6-58.8) | 55.9% (52.8-58.9) | 55.8% (53.6-58.0) |
| G4.s2 a Stage 2 in play, own turn 5 | 69.0% (66.1-71.8) | 68.3% (65.4-71.1) | 68.7% (66.6-70.6) |
| G5.any3 an empty own turn among turns 1-3 | 14.4% (12.4-16.7) | 14.3% (12.3-16.6) | 14.3% (12.9-16.0) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.4) | 19.8% (17.4-22.4) | 9.9% (8.7-11.3) |
| G6 Kingambit with [DD] attached, own turn 3 | 32.5% (29.7-35.5) | 37.2% (34.3-40.2) | 34.9% (32.8-37.0) |
| G6 Kingambit with [DD] attached, own turn 4 | 55.7% (52.6-58.8) | 55.9% (52.8-58.9) | 55.8% (53.6-58.0) |
| G6 Kingambit with [DD] attached, own turn 5 | 69.0% (66.1-71.8) | 68.3% (65.4-71.1) | 68.7% (66.6-70.6) |
| G5 mean empty own turns in turns 1-5 | 0.716 | 0.717 | 0.717 |

Clock measures under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.8% / 11.0% [2-6] | 1.9% / 5.5% [1-3] |
| K3.by3 | 4.8% / 15.0% [2-7] | 4.2% / 11.4% [2-6] | 4.5% / 13.2% [3-7] |
| K3.by4 | 5.8% / 16.0% [3-9] | 6.8% / 14.0% [5-9] | 6.3% / 15.0% [4-8] |
| K3.by5 | 9.0% / 19.2% [6-12] | 7.2% / 20.6% [5-9] | 8.1% / 19.9% [6-10] |
| K3.by6 | 9.2% / 26.6% [6-13] | 14.6% / 37.0% [6-26] | 11.9% / 31.8% [7-18] |
| K3.by7 | 20.2% / 46.2% [8-36] | 18.0% / 58.4% [7-31] | 19.1% / 52.3% [8-33] |
| K3.by8 | 24.0% / 71.6% [10-41] | 18.0% / 61.6% [7-31] | 21.0% / 66.6% [9-35] |
| K3.never | 28.4% / 76.0% [11-51] | 38.4% / 82.0% [17-61] | 33.4% / 79.0% [13-56] |
| K3.k0 | 6.4% / 54.0% [4-9] | 4.4% / 48.0% [3-6] | 5.4% / 51.0% [3-8] |
| K3.k1 | 0.0% / 47.6% [0-0] | 0.0% / 43.6% [0-0] | 0.0% / 45.6% [0-0] |
| K3.k2 | 10.8% / 58.4% [1-25] | 8.8% / 52.4% [1-20] | 9.8% / 55.4% [2-23] |
| K3.k3p | 6.8% / 54.4% [0-17] | 4.8% / 48.4% [0-12] | 5.8% / 51.4% [0-14] |
| K4 | 17.6% / 69.2% [3-34] | 13.6% / 59.6% [3-26] | 15.6% / 64.4% [3-30] |
| K5 | 5.4% / 63.4% [3-8] | 5.2% / 55.0% [3-8] | 5.3% / 59.2% [3-8] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.4 points (+0.5 to +2.4); K3.by4: +1.9 points (+0.8 to +3.1); K3.by5: +2.1 points (+0.7 to +3.5); K3.by6: +3.2 points (+1.2 to +5.3); K3.by7: +5.2 points (+2.0 to +9.0); K3.by8: +5.5 points (+2.0 to +9.6); K3.never: -4.0 points (-8.0 to -1.1); K3.k0: +1.7 points (+0.8 to +2.7); K4: +3.8 points (+0.5 to +7.6); K5: -2.0 points (-3.0 to -1.1).

Clock measures under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 4.4% [3-5] | 2.2% [0-3] |
| K3.by3 | 5.2% / 16.8% [2-8] | 5.6% [5-6] | 5.4% / 11.2% [4-7] |
| K3.by4 | 6.0% / 17.6% [2-10] | 7.4% [6-8] | 6.7% / 12.5% [5-9] |
| K3.by5 | 8.8% / 20.4% [5-12] | 8.8% / 32.2% [8-10] | 8.8% / 26.3% [7-11] |
| K3.by6 | 8.8% / 20.4% [5-12] | 9.2% / 32.6% [8-11] | 9.0% / 26.5% [7-11] |
| K3.by7 | 22.4% / 44.6% [8-40] | 18.6% / 75.4% [8-38] | 20.5% / 60.0% [9-34] |
| K3.by8 | 22.4% / 65.6% [8-40] | 18.6% / 84.0% [8-38] | 20.5% / 74.8% [9-34] |
| K3.never | 34.4% / 77.6% [12-63] | 16.0% / 81.4% [1-38] | 25.2% / 79.5% [10-45] |
| K3.k0 | 6.2% / 49.4% [3-10] | 6.4% / 71.8% [5-8] | 6.3% / 60.6% [4-8] |
| K3.k1 | 0.0% / 43.2% [0-0] | 0.0% / 65.4% [0-0] | 0.0% / 54.3% [0-0] |
| K3.k2 | 10.4% / 53.6% [0-26] | 2.8% / 68.2% [0-5] | 6.6% / 60.9% [1-16] |
| K3.k3p | 5.8% / 49.0% [0-18] | 9.4% / 74.8% [0-27] | 7.6% / 61.9% [0-17] |
| K4 | 16.2% / 63.6% [0-34] | 12.2% / 83.2% [0-32] | 14.2% / 73.4% [2-28] |
| K5 | 5.4% / 58.4% [3-8] | 3.8% / 83.2% [3-5] | 4.6% / 70.8% [3-6] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.9); K3.by4: +1.8 points (+0.8 to +2.9); K3.by5: +2.2 points (+1.2 to +3.3); K3.by6: +2.0 points (+1.1 to +3.0); K3.by7: +5.6 points (+1.8 to +10.3); K3.by8: +5.6 points (+1.8 to +10.3); K3.never: -4.1 points (-7.9 to -1.0); K3.k0: +1.9 points (+1.0 to +3.0); K5: -2.5 points (-3.6 to -1.5).

Clock measures under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.6% [2-5] | 1.8% [1-3] |
| K3.by3 | 6.2% [4-9] | 3.8% [2-5] | 5.0% [4-6] |
| K3.by4 | 7.2% [5-10] | 5.4% [4-7] | 6.3% [5-8] |
| K3.by5 | 9.4% [6-12] | 8.2% [6-11] | 8.8% [7-11] |
| K3.by6 | 12.4% [9-16] | 10.0% / 14.2% [7-13] | 11.2% / 13.3% [9-14] |
| K3.by7 | 14.8% / 18.2% [11-19] | 11.8% / 19.2% [9-16] | 13.3% / 18.7% [10-17] |
| K3.by8 | 17.2% / 27.8% [13-22] | 13.0% / 22.0% [9-17] | 15.1% / 24.9% [12-19] |
| K3.never | 72.2% / 82.8% [63-80] | 78.0% / 87.0% [70-85] | 75.1% / 84.9% [67-82] |
| K3.k0 | 8.0% / 18.6% [5-11] | 3.8% / 12.8% [2-5] | 5.9% / 15.7% [4-8] |
| K3.k1 | 0.0% / 10.6% [0-0] | 0.0% / 9.0% [0-0] | 0.0% / 9.8% [0-0] |
| K3.k2 | 3.0% / 13.6% [1-6] | 3.6% / 12.6% [2-6] | 3.3% / 13.1% [2-6] |
| K3.k3p | 6.2% / 16.8% [3-11] | 5.6% / 14.6% [3-9] | 5.9% / 15.7% [3-10] |
| K4 | 9.2% / 21.8% [5-14] | 9.2% / 19.0% [6-13] | 9.2% / 20.4% [6-13] |
| K5 | 5.2% / 21.0% [3-7] | 6.6% / 17.4% [4-9] | 5.9% / 19.2% [4-7] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.5 points (+0.7 to +2.4); K3.by4: +1.7 points (+0.7 to +2.8); K3.by5: +2.1 points (+1.0 to +3.2); K3.by6: +2.3 points (+1.0 to +3.5); K3.by7: +2.7 points (+1.2 to +4.2); K3.by8: +2.9 points (+1.4 to +4.5); K3.never: -2.1 points (-3.5 to -0.6); K3.k0: +1.7 points (+0.9 to +2.7); K3.k3p: +1.3 points (+0.6 to +2.2); K5: -2.8 points (-3.9 to -1.7).

Clock measures under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 5.0% [3-7, Wilson] | 2.5% [2-4, Wilson] |
| K3.by4 | 2.6% [2-4, Wilson] | 11.4% [9-14, Wilson] | 7.0% [6-9, Wilson] |
| K3.by5 | 21.0% [18-25, Wilson] | 12.6% [10-16, Wilson] | 16.8% [15-19, Wilson] |
| K3.by6 | 25.0% [21-29, Wilson] | 12.6% [10-16, Wilson] | 18.8% [16-21, Wilson] |
| K3.by7 | 25.0% [21-29, Wilson] | 12.6% [10-16, Wilson] | 18.8% [16-21, Wilson] |
| K3.by8 | 25.0% [21-29, Wilson] | 12.6% [10-16, Wilson] | 18.8% [16-21, Wilson] |
| K3.never | 75.0% [71-79, Wilson] | 87.4% [84-90, Wilson] | 81.2% [79-84, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.6% [2-4, Wilson] | 5.0% [3-7, Wilson] | 3.8% [3-5, Wilson] |
| K3.k3p | 22.4% [19-26, Wilson] | 7.6% [6-10, Wilson] | 15.0% [13-17, Wilson] |
| K4 | 25.0% [21-29, Wilson] | 12.6% [10-16, Wilson] | 18.8% [16-21, Wilson] |
| K5 | 10.8% [8-14, Wilson] | 14.2% [11-18, Wilson] | 12.5% [11-15, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: +2.7 points (+1.6 to +3.8); K3.by5: +8.5 points (+6.6 to +10.4); K3.by6: +8.6 points (+6.7 to +10.5); K3.by7: +8.6 points (+6.7 to +10.5); K3.by8: +8.6 points (+6.7 to +10.5); K3.never: -8.6 points (-10.5 to -6.7); K3.k3p: +7.8 points (+6.0 to +9.6); K4: +8.6 points (+6.7 to +10.5); K5: -7.4 points (-9.1 to -5.7).

Clock measures under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 5.0% [3-7, Wilson] | 2.5% [2-4, Wilson] |
| K3.by3 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by4 | 7.0% [5-10, Wilson] | 8.8% [7-12, Wilson] | 7.9% [6-10, Wilson] |
| K3.by5 | 8.4% [6-11, Wilson] | 27.4% [24-31, Wilson] | 17.9% [16-20, Wilson] |
| K3.by6 | 38.6% [34-43, Wilson] | 31.4% [27-36, Wilson] | 35.0% [32-38, Wilson] |
| K3.by7 | 43.0% [39-47, Wilson] | 31.4% [27-36, Wilson] | 37.2% [34-40, Wilson] |
| K3.by8 | 43.0% [39-47, Wilson] | 31.4% [27-36, Wilson] | 37.2% [34-40, Wilson] |
| K3.never | 57.0% [53-61, Wilson] | 68.6% [64-73, Wilson] | 62.8% [60-66, Wilson] |
| K3.k0 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.4% [1-3, Wilson] | 3.8% [2-6, Wilson] | 2.6% [2-4, Wilson] |
| K3.k3p | 34.6% [31-39, Wilson] | 22.6% [19-26, Wilson] | 28.6% [26-31, Wilson] |
| K4 | 36.0% [32-40, Wilson] | 26.4% [23-30, Wilson] | 31.2% [28-34, Wilson] |
| K5 | 7.6% [6-10, Wilson] | 9.2% [7-12, Wilson] | 8.4% [7-10, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.8); K3.by4: +1.9 points (+0.8 to +3.0); K3.by5: +5.9 points (+4.1 to +7.7); K3.by6: +13.0 points (+10.6 to +15.4); K3.by7: +13.1 points (+10.7 to +15.5); K3.by8: +13.1 points (+10.7 to +15.5); K3.never: -13.1 points (-15.5 to -10.7); K3.k0: +1.9 points (+1.0 to +2.8); K3.k3p: +11.3 points (+9.1 to +13.5); K4: +11.2 points (+8.9 to +13.5); K5: -6.1 points (-7.7 to -4.5).

Clock measures under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 5.0% [3-7, Wilson] | 2.5% [2-4, Wilson] |
| K3.by3 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by4 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by5 | 7.0% [5-10, Wilson] | 9.8% [7-13, Wilson] | 8.4% [7-10, Wilson] |
| K3.by6 | 9.0% [7-12, Wilson] | 9.8% [7-13, Wilson] | 9.4% [8-11, Wilson] |
| K3.by7 | 9.0% [7-12, Wilson] | 54.2% [50-59, Wilson] | 31.6% [29-35, Wilson] |
| K3.by8 | 61.8% [57-66, Wilson] | 54.2% [50-59, Wilson] | 58.0% [55-61, Wilson] |
| K3.never | 38.2% [34-43, Wilson] | 45.8% [41-50, Wilson] | 42.0% [39-45, Wilson] |
| K3.k0 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.0% [1-4, Wilson] | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] |
| K3.k3p | 52.8% [48-57, Wilson] | 44.4% [40-49, Wilson] | 48.6% [46-52, Wilson] |
| K4 | 54.8% [50-59, Wilson] | 49.2% [45-54, Wilson] | 52.0% [49-55, Wilson] |
| K5 | 6.8% [5-9, Wilson] | 5.6% [4-8, Wilson] | 6.2% [5-8, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.8); K3.by4: +1.9 points (+1.0 to +2.8); K3.by5: +1.6 points (+0.3 to +2.9); K3.by7: +7.2 points (+5.2 to +9.2); K3.by8: +12.4 points (+10.2 to +14.6); K3.never: -12.4 points (-14.6 to -10.2); K3.k0: +1.9 points (+1.0 to +2.8); K3.k3p: +11.5 points (+9.4 to +13.6); K4: +10.5 points (+8.4 to +12.6); K5: -3.0 points (-4.1 to -1.9).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 5.0% [3-7, Wilson] | 2.5% [2-4, Wilson] |
| K3.by4 | 2.6% [2-4, Wilson] | 10.8% [8-14, Wilson] | 6.7% [5-8, Wilson] |
| K3.by5 | 19.6% [16-23, Wilson] | 12.0% [9-15, Wilson] | 15.8% [14-18, Wilson] |
| K3.by6 | 24.0% [20-28, Wilson] | 12.0% [9-15, Wilson] | 18.0% [16-21, Wilson] |
| K3.by7 | 24.0% [20-28, Wilson] | 12.0% [9-15, Wilson] | 18.0% [16-21, Wilson] |
| K3.by8 | 24.0% [20-28, Wilson] | 12.0% [9-15, Wilson] | 18.0% [16-21, Wilson] |
| K3.never | 76.0% [72-80, Wilson] | 88.0% [85-91, Wilson] | 82.0% [79-84, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.6% [2-4, Wilson] | 5.0% [3-7, Wilson] | 3.8% [3-5, Wilson] |
| K3.k3p | 21.4% [18-25, Wilson] | 7.0% [5-10, Wilson] | 14.2% [12-17, Wilson] |
| K4 | 24.0% [20-28, Wilson] | 12.0% [9-15, Wilson] | 18.0% [16-21, Wilson] |
| K5 | 10.8% [8-14, Wilson] | 14.2% [11-18, Wilson] | 12.5% [11-15, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: +2.5 points (+1.4 to +3.6); K3.by5: +8.2 points (+6.3 to +10.1); K3.by6: +8.4 points (+6.5 to +10.3); K3.by7: +8.4 points (+6.5 to +10.3); K3.by8: +8.4 points (+6.5 to +10.3); K3.never: -8.4 points (-10.3 to -6.5); K3.k3p: +7.6 points (+5.8 to +9.4); K4: +8.4 points (+6.5 to +10.3); K5: -7.4 points (-9.1 to -5.7).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 5.0% [3-7, Wilson] | 2.5% [2-4, Wilson] |
| K3.by3 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by4 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by5 | 7.0% [5-10, Wilson] | 9.8% [7-13, Wilson] | 8.4% [7-10, Wilson] |
| K3.by6 | 9.0% [7-12, Wilson] | 9.8% [7-13, Wilson] | 9.4% [8-11, Wilson] |
| K3.by7 | 9.0% [7-12, Wilson] | 42.2% [38-47, Wilson] | 25.6% [23-28, Wilson] |
| K3.by8 | 51.2% [47-56, Wilson] | 42.2% [38-47, Wilson] | 46.7% [44-50, Wilson] |
| K3.by9 | 51.2% [47-56, Wilson] | 48.4% [44-53, Wilson] | 49.8% [47-53, Wilson] |
| K3.by10 | 55.4% [51-60, Wilson] | 48.4% [44-53, Wilson] | 51.9% [49-55, Wilson] |
| K3.never | 44.6% [40-49, Wilson] | 51.6% [47-56, Wilson] | 48.1% [45-51, Wilson] |
| K3.k0 | 7.0% [5-10, Wilson] | 5.0% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.0% [1-4, Wilson] | 4.8% [3-7, Wilson] | 3.4% [2-5, Wilson] |
| K3.k3p | 46.4% [42-51, Wilson] | 38.6% [34-43, Wilson] | 42.5% [39-46, Wilson] |
| K4 | 48.4% [44-53, Wilson] | 43.4% [39-48, Wilson] | 45.9% [43-49, Wilson] |
| K5 | 6.8% [5-9, Wilson] | 5.6% [4-8, Wilson] | 6.2% [5-8, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.8); K3.by4: +1.9 points (+1.0 to +2.8); K3.by5: +1.6 points (+0.3 to +2.9); K3.by7: +4.7 points (+2.9 to +6.5); K3.by8: +9.2 points (+7.1 to +11.3); K3.by9: +9.2 points (+7.2 to +11.2); K3.by10: +8.3 points (+6.4 to +10.2); K3.never: -8.3 points (-10.2 to -6.4); K3.k0: +1.9 points (+1.0 to +2.8); K3.k3p: +7.4 points (+5.6 to +9.2); K4: +6.4 points (+4.7 to +8.1); K5: -3.0 points (-4.1 to -1.9).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard line in play (end of own turn t), own turn 1 | +2.0 (+1.1 to +2.9) FLAG | +2.1 (+1.2 to +3.0) FLAG | +2.1 (+1.4 to +2.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | +2.9 (+1.8 to +4.0) FLAG | +2.8 (+1.6 to +4.0) FLAG | +2.9 (+2.1 to +3.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | +2.0 (+1.0 to +3.0) FLAG | +2.7 (+1.5 to +3.9) FLAG | +2.4 (+1.6 to +3.1) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | +2.0 (+1.1 to +2.9) FLAG | +2.6 (+1.5 to +3.7) FLAG | +2.3 (+1.6 to +3.0) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | +1.2 (+0.5 to +1.9) FLAG | +1.6 (+0.7 to +2.5) FLAG | +1.4 (+0.8 to +2.0) FLAG |
| K2 Kingambit in play, own turn 2 | +10.1 (+8.2 to +12.0) FLAG | +8.9 (+7.1 to +10.7) FLAG | +9.5 (+8.2 to +10.8) FLAG |
| K2 Kingambit in play, own turn 3 | +16.5 (+14.1 to +18.9) FLAG | +17.0 (+14.6 to +19.4) FLAG | +16.8 (+15.1 to +18.4) FLAG |
| K2 Kingambit in play, own turn 4 | +21.2 (+18.6 to +23.8) FLAG | +22.0 (+19.3 to +24.7) FLAG | +21.6 (+19.7 to +23.5) FLAG |
| K2 Kingambit in play, own turn 5 | +22.5 (+19.9 to +25.1) FLAG | +18.9 (+16.3 to +21.5) FLAG | +20.7 (+18.8 to +22.6) FLAG |
| K2 Kingambit in play, own turn 6 | +17.4 (+15.0 to +19.8) FLAG | +14.9 (+12.5 to +17.3) FLAG | +16.2 (+14.4 to +17.9) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +2.8 (+1.5 to +4.1) FLAG | +3.5 (+2.1 to +4.9) FLAG | +3.1 (+2.2 to +4.1) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +4.8 (+3.2 to +6.4) FLAG | +3.0 (+1.5 to +4.5) FLAG | +3.9 (+2.8 to +5.0) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +3.5 (+2.0 to +5.0) FLAG | +2.3 (+0.9 to +3.7) FLAG | +2.9 (+1.9 to +3.9) FLAG |
| G3 Pawniard in play, own turn 1 | +2.0 (+1.1 to +2.9) FLAG | +2.1 (+1.2 to +3.0) FLAG | +2.1 (+1.4 to +2.7) FLAG |
| G3 Pawniard in play, own turn 2 | -7.2 (-9.4 to -5.0) FLAG | -6.1 (-8.2 to -4.0) FLAG | -6.7 (-8.2 to -5.1) FLAG |
| G3 Pawniard in play, own turn 3 | -14.5 (-17.0 to -12.0) FLAG | -14.3 (-16.9 to -11.7) FLAG | -14.4 (-16.2 to -12.6) FLAG |
| G3 Pawniard in play, own turn 4 | -19.2 (-21.8 to -16.6) FLAG | -19.4 (-22.2 to -16.6) FLAG | -19.3 (-21.2 to -17.4) FLAG |
| G3 Pawniard in play, own turn 5 | -21.3 (-23.9 to -18.7) FLAG | -17.3 (-19.9 to -14.7) FLAG | -19.3 (-21.1 to -17.5) FLAG |
| G3 Kingambit in play, own turn 2 | +10.1 (+8.2 to +12.0) FLAG | +8.9 (+7.1 to +10.7) FLAG | +9.5 (+8.2 to +10.8) FLAG |
| G3 Kingambit in play, own turn 3 | +16.5 (+14.1 to +18.9) FLAG | +17.0 (+14.6 to +19.4) FLAG | +16.8 (+15.1 to +18.4) FLAG |
| G3 Kingambit in play, own turn 4 | +21.2 (+18.6 to +23.8) FLAG | +22.0 (+19.3 to +24.7) FLAG | +21.6 (+19.7 to +23.5) FLAG |
| G3 Kingambit in play, own turn 5 | +22.5 (+19.9 to +25.1) FLAG | +18.9 (+16.3 to +21.5) FLAG | +20.7 (+18.8 to +22.6) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -2.2 (-3.7 to -0.7) FLAG | -2.2 (-3.7 to -0.7) FLAG | -2.2 (-3.3 to -1.1) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -5.1 (-6.8 to -3.4) FLAG | -3.0 (-4.5 to -1.5) FLAG | -4.0 (-5.2 to -2.9) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -4.2 (-5.7 to -2.7) FLAG | -3.4 (-4.6 to -2.2) FLAG | -3.8 (-4.8 to -2.8) FLAG |
| G3 Alolan Muk in play, own turn 2 | +2.0 (+1.0 to +3.0) FLAG | +1.8 (+0.8 to +2.8) FLAG | +1.9 (+1.2 to +2.6) FLAG |
| G3 Alolan Muk in play, own turn 3 | +3.7 (+2.3 to +5.1) FLAG | +3.6 (+2.2 to +5.0) FLAG | +3.6 (+2.7 to +4.6) FLAG |
| G3 Alolan Muk in play, own turn 4 | +6.6 (+4.9 to +8.3) FLAG | +3.8 (+2.3 to +5.3) FLAG | +5.2 (+4.1 to +6.3) FLAG |
| G3 Alolan Muk in play, own turn 5 | +5.1 (+3.5 to +6.7) FLAG | +3.4 (+2.0 to +4.8) FLAG | +4.2 (+3.2 to +5.3) FLAG |
| G3 Glimmet in play, own turn 1 | +1.2 (+0.4 to +2.0) FLAG | +1.2 (+0.5 to +1.9) FLAG | +1.2 (+0.6 to +1.8) FLAG |
| G3 Glimmet in play, own turn 3 | -5.4 (-7.6 to -3.2) FLAG | -4.8 (-6.9 to -2.7) FLAG | -5.1 (-6.6 to -3.6) FLAG |
| G3 Glimmet in play, own turn 4 | -8.5 (-10.8 to -6.2) FLAG | -8.1 (-10.3 to -5.9) FLAG | -8.3 (-9.9 to -6.7) FLAG |
| G3 Glimmet in play, own turn 5 | -6.8 (-8.7 to -4.9) FLAG | -6.3 (-8.2 to -4.4) FLAG | -6.6 (-7.9 to -5.2) FLAG |
| G3 Glimmora in play, own turn 2 | +3.6 (+2.2 to +5.0) FLAG | +3.7 (+2.1 to +5.3) FLAG | +3.6 (+2.6 to +4.7) FLAG |
| G3 Glimmora in play, own turn 3 | +6.2 (+4.6 to +7.8) FLAG | +4.1 (+2.7 to +5.5) FLAG | +5.1 (+4.1 to +6.2) FLAG |
| G3 Glimmora in play, own turn 4 | +4.5 (+3.1 to +5.9) FLAG | +3.6 (+2.3 to +4.9) FLAG | +4.0 (+3.1 to +5.0) FLAG |
| G3 Glimmora in play, own turn 5 | +2.2 (+1.2 to +3.2) FLAG | +2.2 (+1.2 to +3.2) FLAG | +2.2 (+1.5 to +2.9) FLAG |
| G3 Regigigas in play, own turn 1 | +1.3 (+0.5 to +2.1) FLAG | +1.3 (+0.5 to +2.1) FLAG | +1.3 (+0.8 to +1.8) FLAG |
| G3 Regigigas in play, own turn 2 | +2.0 (+1.1 to +2.9) FLAG | +3.3 (+2.1 to +4.5) FLAG | +2.6 (+1.9 to +3.4) FLAG |
| G3 Regigigas in play, own turn 3 | +2.3 (+1.1 to +3.5) FLAG | +3.6 (+2.2 to +5.0) FLAG | +2.9 (+2.0 to +3.9) FLAG |
| G3 Regigigas in play, own turn 4 | +1.3 (+0.2 to +2.4) FLAG | +2.2 (+0.9 to +3.5) FLAG | +1.8 (+0.9 to +2.6) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | +6.3 (+4.7 to +7.9) FLAG | +4.4 (+2.9 to +5.9) FLAG | +5.3 (+4.2 to +6.5) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | +4.6 (+3.3 to +5.9) FLAG | +3.6 (+2.4 to +4.8) FLAG | +4.1 (+3.2 to +5.0) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | +1.7 (+0.9 to +2.5) FLAG | +2.1 (+1.1 to +3.1) FLAG | +1.9 (+1.3 to +2.5) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | +1.2 (+0.5 to +1.9) FLAG | +0.7 (+0.2 to +1.2) | +0.9 (+0.5 to +1.4) |
| G4.s2 a Stage 2 in play, own turn 2 | +10.1 (+8.2 to +12.0) FLAG | +8.9 (+7.1 to +10.7) FLAG | +9.5 (+8.2 to +10.8) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | +16.5 (+14.1 to +18.9) FLAG | +17.0 (+14.6 to +19.4) FLAG | +16.8 (+15.1 to +18.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +21.2 (+18.6 to +23.8) FLAG | +22.0 (+19.3 to +24.7) FLAG | +21.6 (+19.7 to +23.5) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +22.5 (+19.9 to +25.1) FLAG | +18.9 (+16.3 to +21.5) FLAG | +20.7 (+18.8 to +22.6) FLAG |
| G5.any3 an empty own turn among turns 1-3 | -7.4 (-9.2 to -5.6) FLAG | -8.1 (-10.0 to -6.2) FLAG | -7.8 (-9.1 to -6.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | +8.9 (+7.1 to +10.7) FLAG | +4.5 (+3.5 to +5.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +13.2 (+11.0 to +15.4) FLAG | +17.0 (+14.6 to +19.4) FLAG | +15.1 (+13.5 to +16.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +21.2 (+18.6 to +23.8) FLAG | +22.0 (+19.3 to +24.7) FLAG | +21.6 (+19.7 to +23.5) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +22.5 (+19.9 to +25.1) FLAG | +18.9 (+16.3 to +21.5) FLAG | +20.7 (+18.8 to +22.6) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.040 (-0.071 to -0.008) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, B.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): none flagged
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn +2.5 points (+1.4 to +3.6); P2 the first Glimmora placed had its turn +2.4 points (+1.4 to +3.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -4.0 points (-7.2 to -0.9); P4 ready at the winning moment: Knocks out their strongest +4.8 points (+0.9 to +9.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.6 points (-2.7 to -0.6); P5 plan reached in time: Knocks out their strongest +5.4 points (+1.5 to +10.0)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn +1.7 points (+1.0 to +2.5); P2 both Glimmora had their turn +4.6 points (+1.9 to +8.4); P2 the first Glimmora placed had its turn +2.6 points (+1.4 to +3.8); P2 the second Glimmora placed had its turn +3.7 points (+1.1 to +7.4); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.9 points (-6.3 to -1.8); P4 ready at the winning moment: Knocks out their strongest +2.2 points (+0.5 to +4.5); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.2 points (-4.0 to -0.6); P5 plan reached in time: Knocks out their strongest +2.4 points (+0.8 to +4.6)
- C-bot (per-game bootstrap): P2 both Glimmora had their turn +4.4 points (+2.4 to +6.4); P2 the first Glimmora placed had its turn +2.1 points (+0.9 to +3.5); P2 the second Glimmora placed had its turn +3.3 points (+1.3 to +5.3); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +2.5 points (+0.5 to +4.5); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -5.9 points (-7.7 to -4.1); P4 ready at the winning moment: Knocks out their strongest +3.5 points (+1.6 to +5.8); P4 not ready, ready 2 or more turns late -1.3 points (-2.3 to -0.5); P4 the moment came and Kingambit was never ready in the deal -1.3 points (-2.7 to -0.1); P5 plan reached in time: Knocks out their strongest +2.5 points (+1.1 to +4.3)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn +4.8 points (+3.0 to +6.6); P2 both Glimmora had their turn +2.1 points (+0.2 to +4.0); P2 the first Glimmora placed had its turn +4.2 points (+2.6 to +5.8); P2 the second Glimmora placed had its turn +2.7 points (+0.5 to +4.9); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.7 points (-5.4 to -2.0); P4 ready at the winning moment: Knocks out their strongest +10.7 points (+8.7 to +12.7); P4 ready at the winning moment: Wins outright (a lower bound) +10.7 points (+8.7 to +12.7); P4 the moment came and Kingambit was never ready in the deal -4.8 points (-6.8 to -2.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -5.7 points (-7.3 to -4.1); P5 plan reached in time: Knocks out their strongest +10.5 points (+8.6 to +12.4); P5 plan reached in time: Wins outright (a lower bound) +10.5 points (+8.6 to +12.4)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn +2.5 points (+1.1 to +3.9); P2 both Glimmora had their turn +3.9 points (+1.3 to +6.5); P2 the first Glimmora placed had its turn +4.3 points (+2.7 to +5.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +3.8 points (+1.6 to +6.0); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -5.8 points (-8.0 to -3.6); P4 ready at the winning moment: Knocks out their strongest +13.1 points (+10.8 to +15.4); P4 the moment came and Kingambit was never ready in the deal -5.6 points (-7.8 to -3.4); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -7.0 points (-8.7 to -5.3); P5 plan reached in time: Knocks out their strongest +12.6 points (+10.3 to +14.9)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn +1.7 points (+0.6 to +2.8); P2 both Glimmora had their turn +8.6 points (+6.4 to +10.8); P2 the first Glimmora placed had its turn +2.9 points (+1.5 to +4.3); P2 the second Glimmora placed had its turn +7.4 points (+5.3 to +9.5); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left -2.5 points (-3.8 to -1.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -8.2 points (-10.1 to -6.3); P4 ready at the winning moment: Knocks out their strongest +8.6 points (+6.8 to +10.4); P4 ready at the winning moment: Wins outright (a lower bound) +8.6 points (+6.8 to +10.4); P4 not ready, ready 1 turn late -1.6 points (-2.4 to -0.8); P4 the moment came and Kingambit was never ready in the deal -2.0 points (-3.2 to -0.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -5.0 points (-6.4 to -3.6); P5 plan reached in time: Knocks out their strongest +7.0 points (+5.3 to +8.7); P5 plan reached in time: Wins outright (a lower bound) +7.0 points (+5.3 to +8.7)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +5.1 points (+3.3 to +6.9); P2 both Glimmora had their turn +2.1 points (+0.2 to +4.0); P2 the first Glimmora placed had its turn +4.2 points (+2.6 to +5.8); P2 the second Glimmora placed had its turn +3.0 points (+0.8 to +5.2); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +2.7 points (+0.7 to +4.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -3.7 points (-5.4 to -2.0); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.4 points (-2.2 to -0.6)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn +1.7 points (+0.6 to +2.8); P2 both Glimmora had their turn +9.0 points (+6.9 to +11.1); P2 the first Glimmora placed had its turn +2.9 points (+1.5 to +4.3); P2 the second Glimmora placed had its turn +7.8 points (+5.7 to +9.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +5.8 points (+3.9 to +7.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -4.7 points (-6.5 to -2.9); P4 the moment came and Kingambit was never ready in the deal +3.4 points (+2.2 to +4.6); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.5 points (-3.5 to -1.5)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K1 Pawniard line in play (end of own turn t), own turn 1 +2.1 points; K1 Pawniard line in play (end of own turn t), own turn 2 +2.9 points; K1 Pawniard line in play (end of own turn t), own turn 3 +2.4 points; K1 Pawniard line in play (end of own turn t), own turn 4 +2.3 points; K1 Pawniard line in play (end of own turn t), own turn 5 +1.4 points; K2 Kingambit in play, own turn 2 +9.5 points; K2 Kingambit in play, own turn 3 +16.8 points; K2 Kingambit in play, own turn 4 +21.6 points; K2 Kingambit in play, own turn 5 +20.7 points; K2 Kingambit in play, own turn 6 +16.2 points.
Gives up (flagged, pooled): none flagged.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 +1.4; K3.by4 +1.9; K3.by5 +2.1; K3.by6 +3.2; K3.by7 +5.2; K3.by8 +5.5; K3.never -4.0; K3.k0 +1.7; K4 +3.8; K5 -2.0; C-his, seat-matched: K3.by3 +1.9; K3.by4 +1.8; K3.by5 +2.2; K3.by6 +2.0; K3.by7 +5.6; K3.by8 +5.6; K3.never -4.1; K3.k0 +1.9; K5 -2.5; C-bot: K3.by3 +1.5; K3.by4 +1.7; K3.by5 +2.1; K3.by6 +2.3; K3.by7 +2.7; K3.by8 +2.9; K3.never -2.1; K3.k0 +1.7; K3.k3p +1.3; K5 -2.8; C-fixed fast: K3.by4 +2.7; K3.by5 +8.5; K3.by6 +8.6; K3.by7 +8.6; K3.by8 +8.6; K3.never -8.6; K3.k3p +7.8; K4 +8.6; K5 -7.4; C-fixed medium: K3.by3 +1.9; K3.by4 +1.9; K3.by5 +5.9; K3.by6 +13.0; K3.by7 +13.1; K3.by8 +13.1; K3.never -13.1; K3.k0 +1.9; K3.k3p +11.3; K4 +11.2; K5 -6.1; C-fixed slow: K3.by3 +1.9; K3.by4 +1.9; K3.by5 +1.6; K3.by7 +7.2; K3.by8 +12.4; K3.never -12.4; K3.k0 +1.9; K3.k3p +11.5; K4 +10.5; K5 -3.0; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 +2.5; K3.by5 +8.2; K3.by6 +8.4; K3.by7 +8.4; K3.by8 +8.4; K3.never -8.4; K3.k3p +7.6; K4 +8.4; K5 -7.4; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 +1.9; K3.by4 +1.9; K3.by5 +1.6; K3.by7 +4.7; K3.by8 +9.2; K3.by9 +9.2; K3.by10 +8.3; K3.never -8.3; K3.k0 +1.9; K3.k3p +7.4; K4 +6.4; K5 -3.0.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## C (card-list id 74075f8030e0)

Changes: ['-2 Lucky Ice Pop B2 145', '+1 Rare Candy A3 144', '+1 Copycat B1 225', '-1 Ilima A3 149', '+1 Red A2b 071']

Copycat decisions with a Copycat in hand: 21,874; the valuation and the fallback rule disagree at 9,384 of 21,874 Copycat decisions (42.9%).

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- Chance each Pokémon is the starting Active (lead order Regigigas, Glimmet, Alolan Grimer, Pawniard): Alolan Grimer 0.15613, Glimmet 0.42835, Pawniard 0.12678, Regigigas 0.28874 (P1 is the Regigigas figure).
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.4289.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.05955; in 8 cards: 0.08964.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 51/58/64/70/76%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

### Plan lines: does the deck line up with Dustin's plan?

Simulated, no knock-outs; 2,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P1 Regigigas leads (the Active at the start of the game; exact above) | 30.1% (27.3-33.0) | 28.2% (25.5-31.1) | 29.1% (27.2-31.2) |

Plan lines under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 87.8% / 95.4% [77-96] | 84.2% / 93.8% [68-95] | 86.0% / 94.6% [73-96] |
| P2 both Glimmora had their turn | 41.4% / 73.6% [29-53] | 41.2% / 73.8% [25-59] | 41.3% / 73.7% [28-54] |
| P2 the first Glimmora placed had its turn | 85.6% / 92.4% [75-95] | 77.6% / 85.8% [60-92] | 81.6% / 89.1% [68-94] |
| P2 the second Glimmora placed had its turn | 43.6% / 72.8% [31-56] | 47.8% / 75.2% [31-64] | 45.7% / 74.0% [32-58] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [12-16] | 10.0% [9-11] | 11.9% [11-13] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 7.2% / 54.2% [1-16] | 6.6% / 51.8% [2-13] | 6.9% / 53.0% [2-14] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 22.2% / 62.6% [16-28] | 31.4% / 68.2% [24-40] | 26.8% / 65.4% [21-33] |
| P4 ready at the winning moment: Knocks out their strongest | 17.4% / 44.6% [4-34] | 16.0% / 42.4% [3-32] | 16.7% / 43.5% [3-33] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.4% / 29.6% [0-8] | 2.8% / 29.2% [0-9] | 2.6% / 29.4% [0-8] |
| P4 not ready, ready 1 turn late | 5.0% / 48.8% [0-14] | 4.2% / 46.2% [0-10] | 4.6% / 47.5% [0-12] |
| P4 not ready, ready 2 or more turns late | 0.8% / 44.6% [0-2] | 1.0% / 43.0% [0-3] | 0.9% / 43.8% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 6.4% / 50.2% [0-15] | 6.0% / 48.0% [0-16] | 6.2% / 49.1% [0-15] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 26.6% / 53.8% [8-52] | 30.8% / 57.2% [10-56] | 28.7% / 55.5% [9-52] |
| P5 plan reached in time: Knocks out their strongest | 23.2% / 67.0% [7-40] | 21.2% / 63.2% [7-37] | 22.2% / 65.1% [7-38] |
| P5 plan reached in time: Wins outright (a lower bound) | 2.4% / 46.2% [0-8] | 2.8% / 44.8% [0-9] | 2.6% / 45.5% [0-8] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 58.8% of 148 [32-79] | 58.8% of 136 [27-83] | 58.8% of 284 [31-81] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 8.1% of 148 [0-34] | 10.3% of 136 [0-44] | 9.2% of 284 [0-40] |
| P4 not ready, ready 1 turn late | 16.9% of 148 [0-57] | 15.4% of 136 [0-51] | 16.2% of 284 [0-54] |
| P4 not ready, ready 2 or more turns late | 2.7% of 148 [0-9] | 3.7% of 136 [0-13] | 3.2% of 284 [0-11] |
| P4 the moment came and Kingambit was never ready in the deal | 21.6% of 148 [0-40] | 22.1% of 136 [0-47] | 21.8% of 284 [0-43] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +2.4 points (+1.1 to +3.6); P2.both: +3.7 points (+0.3 to +7.8); P2.g1: +2.7 points (+1.8 to +3.6); P3.grimer_muk: -2.8 points (-5.0 to -0.9); P4.ko: +4.7 points (+0.9 to +8.9); P4.nomoment: -1.8 points (-2.7 to -0.9); P5.ko: +4.6 points (+1.2 to +8.8).

Plan lines under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 88.4% / 97.0% [74-98] | 92.0% / 96.0% [85-97] | 90.2% / 96.5% [81-96] |
| P2 both Glimmora had their turn | 45.4% / 72.6% [28-61] | 35.4% / 81.0% [24-46] | 40.4% / 76.8% [30-52] |
| P2 the first Glimmora placed had its turn | 86.2% / 94.6% [72-95] | 87.4% / 88.4% [80-97] | 86.8% / 91.5% [78-93] |
| P2 the second Glimmora placed had its turn | 47.6% / 71.2% [29-65] | 40.0% / 78.0% [29-54] | 43.8% / 74.6% [33-56] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-16] | 10.0% [9-11] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 1.4% / 44.4% [0-3] | 13.0% / 77.4% [0-31] | 7.2% / 60.9% [1-16] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 22.6% / 60.2% [16-30] | 33.2% / 89.2% [18-42] | 27.9% / 74.7% [19-35] |
| P4 ready at the winning moment: Knocks out their strongest | 23.4% / 47.6% [4-44] | 6.4% / 63.2% [0-23] | 14.9% / 55.4% [4-29] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 6.8% / 31.0% [0-21] | 0.0% / 56.8% [0-0] | 3.4% / 43.9% [0-13] |
| P4 not ready, ready 1 turn late | 7.2% / 44.4% [0-20] | 0.0% / 75.8% [0-0] | 3.6% / 60.1% [0-11] |
| P4 not ready, ready 2 or more turns late | 1.0% / 38.2% [0-3] | 0.0% / 75.8% [0-0] | 0.5% / 57.0% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 8.0% / 45.2% [0-18] | 0.0% / 75.8% [0-0] | 4.0% / 60.5% [0-10] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 23.2% / 47.4% [5-51] | 17.8% / 74.6% [0-42] | 20.5% / 61.0% [6-39] |
| P5 plan reached in time: Knocks out their strongest | 31.6% / 68.8% [9-54] | 6.4% / 82.2% [0-23] | 19.0% / 75.5% [7-37] |
| P5 plan reached in time: Wins outright (a lower bound) | 6.8% / 44.0% [0-21] | 0.0% / 75.8% [0-0] | 3.4% / 59.9% [0-13] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 59.1% of 198 [23-78] | 100.0% of 32 [100-100] | 64.8% of 230 [38-85] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 17.2% of 198 [0-54] | 0.0% of 32 [0-0] | 14.8% of 230 [0-46] |
| P4 not ready, ready 1 turn late | 18.2% of 198 [0-68] | 0.0% of 32 [0-0] | 15.7% of 230 [0-48] |
| P4 not ready, ready 2 or more turns late | 2.5% of 198 [0-9] | 0.0% of 32 [0-0] | 2.2% of 230 [0-7] |
| P4 the moment came and Kingambit was never ready in the deal | 20.2% of 198 [0-38] | 0.0% of 32 [0-0] | 17.4% of 230 [0-32] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +2.1 points (+0.9 to +3.1); P2.both: +4.5 points (+2.1 to +8.2); P2.g1: +2.7 points (+1.4 to +4.0); P2.g2: +3.9 points (+1.6 to +7.3); P3.grimer_muk: -2.6 points (-3.9 to -1.5); P4.ko: +3.1 points (+0.8 to +6.1); P4.nomoment: -2.5 points (-4.5 to -0.9); P5.ko: +3.2 points (+1.0 to +6.0).

Plan lines under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 93.2% / 93.6% [89-96] | 86.8% / 87.8% [82-91] | 90.0% / 90.7% [87-93] |
| P2 both Glimmora had their turn | 43.2% / 48.6% [37-49] | 34.6% / 39.0% [28-41] | 38.9% / 43.8% [34-44] |
| P2 the first Glimmora placed had its turn | 88.0% / 88.2% [83-92] | 77.4% [70-84] | 82.7% / 82.8% [78-88] |
| P2 the second Glimmora placed had its turn | 48.4% / 52.2% [43-54] | 44.0% / 47.0% [39-49] | 46.2% / 49.6% [42-51] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17] | 10.0% [8-12] | 11.9% [10-14] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 20.0% / 31.8% [13-27] | 17.0% / 26.4% [12-22] | 18.5% / 29.1% [14-24] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 29.0% / 39.4% [24-34] | 39.8% / 47.4% [35-45] | 34.4% / 43.4% [31-38] |
| P4 ready at the winning moment: Knocks out their strongest | 9.6% / 16.2% [4-16] | 10.4% / 17.6% [5-17] | 10.0% / 16.9% [5-16] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 1.0% / 7.6% [0-3] | 0.6% / 7.8% [0-2] | 0.8% / 7.7% [0-2] |
| P4 not ready, ready 1 turn late | 6.0% / 14.6% [2-10] | 4.8% / 13.0% [2-8] | 5.4% / 13.8% [2-9] |
| P4 not ready, ready 2 or more turns late | 0.8% / 9.4% [0-2] | 0.8% / 9.0% [0-2] | 0.8% / 9.2% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 8.4% / 17.0% [3-14] | 4.4% / 12.6% [1-8] | 6.4% / 14.8% [3-11] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 66.6% / 73.2% [54-79] | 71.4% / 78.6% [60-82] | 69.0% / 75.9% [58-80] |
| P5 plan reached in time: Knocks out their strongest | 16.4% / 25.0% [9-26] | 16.0% / 24.2% [9-25] | 16.2% / 24.6% [9-24] |
| P5 plan reached in time: Wins outright (a lower bound) | 1.0% / 9.6% [0-3] | 0.6% / 8.8% [0-2] | 0.8% / 9.2% [0-2] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 38.7% of 124 [20-60] | 51.0% of 102 [35-68] | 44.2% of 226 [28-62] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.0% of 124 [0-15] | 2.9% of 102 [0-9] | 3.5% of 226 [0-11] |
| P4 not ready, ready 1 turn late | 24.2% of 124 [11-38] | 23.5% of 102 [10-37] | 23.9% of 226 [11-36] |
| P4 not ready, ready 2 or more turns late | 3.2% of 124 [0-7] | 3.9% of 102 [1-8] | 3.5% of 226 [1-6] |
| P4 the moment came and Kingambit was never ready in the deal | 33.9% of 124 [18-49] | 21.6% of 102 [8-36] | 28.3% of 226 [15-42] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): P2.any: +1.3 points (+0.4 to +2.3); P2.both: +3.4 points (+1.2 to +5.7); P2.g1: +2.2 points (+1.1 to +3.5); P2.g2: +2.5 points (+0.3 to +4.9); P3.pawn_promo: +3.2 points (+1.2 to +5.2); P3.grimer_muk: -6.6 points (-8.8 to -4.4); P4.ko: +3.5 points (+1.3 to +6.1); P4.late2p: -1.2 points (-2.3 to -0.2); P4.never: -1.9 points (-3.7 to -0.5); P5.ko: +2.7 points (+1.1 to +4.8).

Plan lines under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 84.6% [81-87, Wilson] | 55.0% [51-59, Wilson] | 69.8% [67-73, Wilson] |
| P2 both Glimmora had their turn | 31.8% [28-36, Wilson] | 9.4% [7-12, Wilson] | 20.6% [18-23, Wilson] |
| P2 the first Glimmora placed had its turn | 79.6% [76-83, Wilson] | 32.8% [29-37, Wilson] | 56.2% [53-59, Wilson] |
| P2 the second Glimmora placed had its turn | 36.8% [33-41, Wilson] | 31.6% [28-36, Wilson] | 34.2% [31-37, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 21.4% [18-25, Wilson] | 17.2% [14-21, Wilson] | 19.3% [17-22, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 49.2% [45-54, Wilson] | 55.4% [51-60, Wilson] | 52.3% [49-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 28.0% [24-32, Wilson] | 9.4% [7-12, Wilson] | 18.7% [16-21, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 28.0% [24-32, Wilson] | 9.4% [7-12, Wilson] | 18.7% [16-21, Wilson] |
| P4 not ready, ready 1 turn late | 1.6% [1-3, Wilson] | 0.6% [0-2, Wilson] | 1.1% [1-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 17.4% [14-21, Wilson] | 14.0% [11-17, Wilson] | 15.7% [14-18, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 53.0% [49-57, Wilson] | 76.0% [72-80, Wilson] | 64.5% [61-67, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 29.6% [26-34, Wilson] | 10.0% [8-13, Wilson] | 19.8% [17-22, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 29.6% [26-34, Wilson] | 10.0% [8-13, Wilson] | 19.8% [17-22, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 59.6% of 235 [53-66, Wilson] | 39.2% of 120 [31-48, Wilson] | 52.7% of 355 [47-58, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 59.6% of 235 [53-66, Wilson] | 39.2% of 120 [31-48, Wilson] | 52.7% of 355 [47-58, Wilson] |
| P4 not ready, ready 1 turn late | 3.4% of 235 [2-7, Wilson] | 2.5% of 120 [1-7, Wilson] | 3.1% of 355 [2-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 235 [0-2, Wilson] | 0.0% of 120 [0-3, Wilson] | 0.0% of 355 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 37.0% of 235 [31-43, Wilson] | 58.3% of 120 [49-67, Wilson] | 44.2% of 355 [39-49, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): P2.any: +3.7 points (+2.1 to +5.3); P2.both: +3.2 points (+1.3 to +5.1); P2.g1: +3.3 points (+1.8 to +4.8); P2.g2: +3.6 points (+1.5 to +5.7); P3.grimer_muk: -2.7 points (-4.6 to -0.8); P4.ko: +8.5 points (+6.6 to +10.4); P4.win: +8.5 points (+6.6 to +10.4); P4.never: -3.3 points (-5.4 to -1.2); P4.nomoment: -5.2 points (-6.7 to -3.7); P5.ko: +8.5 points (+6.6 to +10.4); P5.win: +8.5 points (+6.6 to +10.4).

Plan lines under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: P4.win (first, second); P5.win (first, second).

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 91.6% [89-94, Wilson] | 86.0% [83-89, Wilson] | 88.8% [87-91, Wilson] |
| P2 both Glimmora had their turn | 40.8% [37-45, Wilson] | 31.8% [28-36, Wilson] | 36.3% [33-39, Wilson] |
| P2 the first Glimmora placed had its turn | 89.4% [86-92, Wilson] | 83.0% [79-86, Wilson] | 86.2% [84-88, Wilson] |
| P2 the second Glimmora placed had its turn | 43.0% [39-47, Wilson] | 34.8% [31-39, Wilson] | 38.9% [36-42, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 28.2% [24-32, Wilson] | 23.2% [20-27, Wilson] | 25.7% [23-28, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 44.4% [40-49, Wilson] | 54.8% [50-59, Wilson] | 49.6% [47-53, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 38.0% [34-42, Wilson] | 29.4% [26-34, Wilson] | 33.7% [31-37, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 2.0% [1-4, Wilson] | 1.0% [0-2, Wilson] | 1.5% [1-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 16.6% [14-20, Wilson] | 17.0% [14-21, Wilson] | 16.8% [15-19, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 43.4% [39-48, Wilson] | 52.6% [48-57, Wilson] | 48.0% [45-51, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 40.0% [36-44, Wilson] | 30.4% [27-35, Wilson] | 35.2% [32-38, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 67.1% of 283 [61-72, Wilson] | 62.0% of 237 [56-68, Wilson] | 64.8% of 520 [61-69, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% of 283 [0-1, Wilson] | 0.0% of 237 [0-2, Wilson] | 0.0% of 520 [0-1, Wilson] |
| P4 not ready, ready 1 turn late | 3.5% of 283 [2-6, Wilson] | 2.1% of 237 [1-5, Wilson] | 2.9% of 520 [2-5, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 283 [0-1, Wilson] | 0.0% of 237 [0-2, Wilson] | 0.0% of 520 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 29.3% of 283 [24-35, Wilson] | 35.9% of 237 [30-42, Wilson] | 32.3% of 520 [28-36, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): P2.any: +3.1 points (+1.7 to +4.5); P2.both: +3.1 points (+0.6 to +5.6); P2.g1: +4.4 points (+2.9 to +5.9); P3.pawn_promo: +3.5 points (+1.4 to +5.6); P3.grimer_muk: -4.2 points (-6.4 to -2.0); P4.ko: +13.4 points (+11.2 to +15.6); P4.never: -5.4 points (-7.6 to -3.2); P4.nomoment: -7.4 points (-9.1 to -5.7); P5.ko: +12.8 points (+10.6 to +15.0).

Plan lines under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 97.0% [95-98, Wilson] | 93.0% [90-95, Wilson] | 95.0% [93-96, Wilson] |
| P2 both Glimmora had their turn | 75.2% [71-79, Wilson] | 65.4% [61-69, Wilson] | 70.3% [67-73, Wilson] |
| P2 the first Glimmora placed had its turn | 92.8% [90-95, Wilson] | 85.6% [82-88, Wilson] | 89.2% [87-91, Wilson] |
| P2 the second Glimmora placed had its turn | 79.4% [76-83, Wilson] | 72.8% [69-77, Wilson] | 76.1% [73-79, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 2.6% [2-4, Wilson] | 6.6% [5-9, Wilson] | 4.6% [3-6, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 21.2% [18-25, Wilson] | 30.0% [26-34, Wilson] | 25.6% [23-28, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 55.6% [51-60, Wilson] | 50.8% [46-55, Wilson] | 53.2% [50-56, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 55.6% [51-60, Wilson] | 50.8% [46-55, Wilson] | 53.2% [50-56, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.4% [0-1, Wilson] | 0.2% [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 10.4% [8-13, Wilson] | 8.6% [6-11, Wilson] | 9.5% [8-11, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 34.0% [30-38, Wilson] | 40.2% [36-45, Wilson] | 37.1% [34-40, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 55.6% [51-60, Wilson] | 51.2% [47-56, Wilson] | 53.4% [50-56, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 55.6% [51-60, Wilson] | 51.2% [47-56, Wilson] | 53.4% [50-56, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 84.2% of 330 [80-88, Wilson] | 84.9% of 299 [80-89, Wilson] | 84.6% of 629 [82-87, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 84.2% of 330 [80-88, Wilson] | 84.9% of 299 [80-89, Wilson] | 84.6% of 629 [82-87, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 330 [0-1, Wilson] | 0.7% of 299 [0-2, Wilson] | 0.3% of 629 [0-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 330 [0-1, Wilson] | 0.0% of 299 [0-1, Wilson] | 0.0% of 629 [0-1, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 15.8% of 330 [12-20, Wilson] | 14.4% of 299 [11-19, Wilson] | 15.1% of 629 [13-18, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): P2.any: +2.5 points (+1.3 to +3.7); P2.both: +8.4 points (+6.2 to +10.6); P2.g1: +3.5 points (+2.1 to +4.9); P2.g2: +7.4 points (+5.3 to +9.5); P3.pawn_promo: -2.7 points (-4.1 to -1.3); P3.grimer_muk: -8.4 points (-10.4 to -6.4); P4.ko: +9.6 points (+7.7 to +11.5); P4.win: +9.6 points (+7.7 to +11.5); P4.late1: -1.6 points (-2.5 to -0.7); P4.never: -2.6 points (-3.8 to -1.4); P4.nomoment: -5.4 points (-6.8 to -4.0); P5.ko: +8.0 points (+6.3 to +9.7); P5.win: +8.0 points (+6.3 to +9.7).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 84.8% [81-88, Wilson] | 55.0% [51-59, Wilson] | 69.9% [67-73, Wilson] |
| P2 both Glimmora had their turn | 32.6% [29-37, Wilson] | 9.4% [7-12, Wilson] | 21.0% [19-24, Wilson] |
| P2 the first Glimmora placed had its turn | 79.6% [76-83, Wilson] | 32.8% [29-37, Wilson] | 56.2% [53-59, Wilson] |
| P2 the second Glimmora placed had its turn | 37.8% [34-42, Wilson] | 31.6% [28-36, Wilson] | 34.7% [32-38, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 25.2% [22-29, Wilson] | 18.0% [15-22, Wilson] | 21.6% [19-24, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 49.2% [45-54, Wilson] | 55.4% [51-60, Wilson] | 52.3% [49-55, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.4% [3-7, Wilson] | 1.0% [0-2, Wilson] | 2.7% [2-4, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.4% [3-7, Wilson] | 1.0% [0-2, Wilson] | 2.7% [2-4, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 5.4% [4-8, Wilson] | 1.6% [1-3, Wilson] | 3.5% [3-5, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.2% [87-93, Wilson] | 97.4% [96-98, Wilson] | 93.8% [92-95, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.4% [3-7, Wilson] | 1.0% [0-2, Wilson] | 2.7% [2-4, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.4% [3-7, Wilson] | 1.0% [0-2, Wilson] | 2.7% [2-4, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 44.9% of 49 [32-59, Wilson] | 38.5% of 13 [18-64, Wilson] | 43.5% of 62 [32-56, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 44.9% of 49 [32-59, Wilson] | 38.5% of 13 [18-64, Wilson] | 43.5% of 62 [32-56, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 49 [0-7, Wilson] | 0.0% of 13 [0-23, Wilson] | 0.0% of 62 [0-6, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 49 [0-7, Wilson] | 0.0% of 13 [0-23, Wilson] | 0.0% of 62 [0-6, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 55.1% of 49 [41-68, Wilson] | 61.5% of 13 [36-82, Wilson] | 56.5% of 62 [44-68, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): P2.any: +3.8 points (+2.2 to +5.4); P2.both: +3.2 points (+1.3 to +5.1); P2.g1: +3.3 points (+1.8 to +4.8); P2.g2: +3.7 points (+1.6 to +5.8); P3.pawn_promo: +2.3 points (+0.3 to +4.3); P3.grimer_muk: -2.7 points (-4.6 to -0.8); P4.nomoment: -1.4 points (-2.3 to -0.5).

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at the moment or later, before the opponent's third point.

Zero by construction at this pace: none.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 97.0% [95-98, Wilson] | 93.0% [90-95, Wilson] | 95.0% [93-96, Wilson] |
| P2 both Glimmora had their turn | 77.0% [73-80, Wilson] | 67.2% [63-71, Wilson] | 72.1% [69-75, Wilson] |
| P2 the first Glimmora placed had its turn | 92.8% [90-95, Wilson] | 85.6% [82-88, Wilson] | 89.2% [87-91, Wilson] |
| P2 the second Glimmora placed had its turn | 81.2% [78-84, Wilson] | 74.6% [71-78, Wilson] | 77.9% [75-80, Wilson] |
| P3 plan broken in front, cause: Pawniard forced to lead | 13.8% [11-17, Wilson] | 10.0% [8-13, Wilson] | 11.9% [10-14, Wilson] |
| P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left | 43.4% [39-48, Wilson] | 39.6% [35-44, Wilson] | 41.5% [38-45, Wilson] |
| P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) | 35.2% [31-39, Wilson] | 43.8% [40-48, Wilson] | 39.5% [37-43, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.2% [3-6, Wilson] | 5.2% [4-8, Wilson] | 4.7% [4-6, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.2% [3-6, Wilson] | 5.2% [4-8, Wilson] | 4.7% [4-6, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 14.0% [11-17, Wilson] | 13.8% [11-17, Wilson] | 13.9% [12-16, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 81.8% [78-85, Wilson] | 81.0% [77-84, Wilson] | 81.4% [79-84, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.2% [3-6, Wilson] | 5.2% [4-8, Wilson] | 4.7% [4-6, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.2% [3-6, Wilson] | 5.2% [4-8, Wilson] | 4.7% [4-6, Wilson] |

P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left out):

| P4 line, given the moment came | going first | going second | pooled |
|---|---|---|---|
| P4 ready at the winning moment: Knocks out their strongest | 23.1% of 91 [16-33, Wilson] | 27.4% of 95 [19-37, Wilson] | 25.3% of 186 [20-32, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 23.1% of 91 [16-33, Wilson] | 27.4% of 95 [19-37, Wilson] | 25.3% of 186 [20-32, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% of 91 [0-4, Wilson] | 0.0% of 95 [0-4, Wilson] | 0.0% of 186 [0-2, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% of 91 [0-4, Wilson] | 0.0% of 95 [0-4, Wilson] | 0.0% of 186 [0-2, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 76.9% of 91 [67-84, Wilson] | 72.6% of 95 [63-81, Wilson] | 74.7% of 186 [68-80, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): P2.any: +2.5 points (+1.3 to +3.7); P2.both: +8.6 points (+6.4 to +10.8); P2.g1: +3.5 points (+2.1 to +4.9); P2.g2: +7.6 points (+5.5 to +9.7); P3.pawn_promo: +6.2 points (+4.2 to +8.2); P3.grimer_muk: -4.1 points (-5.9 to -2.3); P4.ko: -1.4 points (-2.5 to -0.3); P4.win: -1.4 points (-2.5 to -0.3); P4.never: +4.0 points (+2.7 to +5.3); P4.nomoment: -2.6 points (-3.7 to -1.5); P5.ko: -1.4 points (-2.5 to -0.3); P5.win: -1.4 points (-2.5 to -0.3).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 31.7% (28.9-34.6) | 24.2% (21.6-27.0) | 27.9% (26.0-30.0) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 58.9% (55.8-61.9) | 56.5% (53.4-59.5) | 57.7% (55.5-59.8) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 71.9% (69.0-74.6) | 69.7% (66.8-72.5) | 70.8% (68.8-72.8) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 77.7% (75.0-80.2) | 76.1% (73.4-78.6) | 76.9% (75.0-78.7) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 80.5% (77.9-82.8) | 80.1% (77.5-82.5) | 80.3% (78.5-82.0) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 82.1% (79.6-84.4) | 81.5% (79.0-83.8) | 81.8% (80.0-83.4) |
| K2 Kingambit in play, own turn 2 | 22.0% (19.5-24.7) | 19.5% (17.2-22.1) | 20.8% (19.0-22.6) |
| K2 Kingambit in play, own turn 3 | 38.0% (35.0-41.0) | 38.1% (35.1-41.2) | 38.0% (35.9-40.2) |
| K2 Kingambit in play, own turn 4 | 54.9% (51.8-58.0) | 57.1% (54.0-60.1) | 56.0% (53.8-58.2) |
| K2 Kingambit in play, own turn 5 | 68.6% (65.7-71.4) | 71.3% (68.4-74.0) | 70.0% (67.9-71.9) |
| K2 Kingambit in play, own turn 6 | 76.7% (74.0-79.2) | 78.5% (75.8-80.9) | 77.6% (75.7-79.4) |
| K6 Muk and Regigigas both in play, own turn 3 | 25.9% (23.3-28.7) | 26.1% (23.5-28.9) | 26.0% (24.1-28.0) |
| K6 Muk and Regigigas both in play, own turn 4 | 35.0% (32.1-38.0) | 34.1% (31.2-37.1) | 34.5% (32.5-36.7) |
| K6 Muk and Regigigas both in play, own turn 5 | 40.5% (37.5-43.6) | 39.5% (36.5-42.6) | 40.0% (37.9-42.2) |
| G3 Pawniard in play, own turn 1 | 58.9% (55.8-61.9) | 56.5% (53.4-59.5) | 57.7% (55.5-59.8) |
| G3 Pawniard in play, own turn 2 | 49.9% (46.8-53.0) | 50.2% (47.1-53.3) | 50.0% (47.9-52.2) |
| G3 Pawniard in play, own turn 3 | 39.7% (36.7-42.8) | 38.0% (35.0-41.0) | 38.9% (36.7-41.0) |
| G3 Pawniard in play, own turn 4 | 25.6% (23.0-28.4) | 23.0% (20.5-25.7) | 24.3% (22.5-26.2) |
| G3 Pawniard in play, own turn 5 | 13.5% (11.5-15.8) | 10.2% (8.5-12.2) | 11.8% (10.5-13.3) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Kingambit in play, own turn 2 | 22.0% (19.5-24.7) | 19.5% (17.2-22.1) | 20.8% (19.0-22.6) |
| G3 Kingambit in play, own turn 3 | 38.0% (35.0-41.0) | 38.1% (35.1-41.2) | 38.0% (35.9-40.2) |
| G3 Kingambit in play, own turn 4 | 54.9% (51.8-58.0) | 57.1% (54.0-60.1) | 56.0% (53.8-58.2) |
| G3 Kingambit in play, own turn 5 | 68.6% (65.7-71.4) | 71.3% (68.4-74.0) | 70.0% (67.9-71.9) |
| G3 Alolan Grimer in play, own turn 1 | 55.6% (52.5-58.7) | 56.2% (53.1-59.2) | 55.9% (53.7-58.1) |
| G3 Alolan Grimer in play, own turn 2 | 45.9% (42.8-49.0) | 45.8% (42.7-48.9) | 45.9% (43.7-48.0) |
| G3 Alolan Grimer in play, own turn 3 | 36.1% (33.2-39.1) | 36.1% (33.2-39.1) | 36.1% (34.0-38.2) |
| G3 Alolan Grimer in play, own turn 4 | 26.9% (24.2-29.7) | 28.4% (25.7-31.3) | 27.6% (25.7-29.7) |
| G3 Alolan Grimer in play, own turn 5 | 21.4% (19.0-24.0) | 22.8% (20.3-25.5) | 22.1% (20.3-24.0) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Alolan Muk in play, own turn 2 | 21.3% (18.9-23.9) | 22.3% (19.8-25.0) | 21.8% (20.0-23.7) |
| G3 Alolan Muk in play, own turn 3 | 36.1% (33.2-39.1) | 37.5% (34.6-40.5) | 36.8% (34.7-38.9) |
| G3 Alolan Muk in play, own turn 4 | 47.5% (44.4-50.6) | 47.2% (44.1-50.3) | 47.4% (45.2-49.5) |
| G3 Alolan Muk in play, own turn 5 | 54.0% (50.9-57.1) | 53.9% (50.8-57.0) | 54.0% (51.8-56.1) |
| G3 Glimmet in play, own turn 1 | 82.2% (79.7-84.4) | 86.2% (83.9-88.2) | 84.2% (82.5-85.7) |
| G3 Glimmet in play, own turn 2 | 51.2% (48.1-54.3) | 53.9% (50.8-57.0) | 52.5% (50.4-54.7) |
| G3 Glimmet in play, own turn 3 | 38.9% (35.9-42.0) | 36.5% (33.6-39.5) | 37.7% (35.6-39.8) |
| G3 Glimmet in play, own turn 4 | 23.1% (20.6-25.8) | 20.9% (18.5-23.5) | 22.0% (20.2-23.9) |
| G3 Glimmet in play, own turn 5 | 14.2% (12.2-16.5) | 11.3% (9.5-13.4) | 12.8% (11.4-14.3) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.4) | 0.0% (0.0-0.4) | 0.0% (0.0-0.2) |
| G3 Glimmora in play, own turn 2 | 66.6% (63.6-69.5) | 69.4% (66.5-72.2) | 68.0% (65.9-70.0) |
| G3 Glimmora in play, own turn 3 | 84.3% (81.9-86.4) | 86.8% (84.6-88.8) | 85.5% (83.9-87.0) |
| G3 Glimmora in play, own turn 4 | 93.5% (91.8-94.9) | 94.4% (92.8-95.7) | 94.0% (92.8-94.9) |
| G3 Glimmora in play, own turn 5 | 96.7% (95.4-97.6) | 97.5% (96.3-98.3) | 97.1% (96.3-97.7) |
| G3 Regigigas in play, own turn 1 | 57.9% (54.8-60.9) | 53.0% (49.9-56.1) | 55.5% (53.3-57.6) |
| G3 Regigigas in play, own turn 2 | 71.3% (68.4-74.0) | 67.7% (64.7-70.5) | 69.5% (67.4-71.5) |
| G3 Regigigas in play, own turn 3 | 77.5% (74.8-80.0) | 74.2% (71.4-76.8) | 75.8% (73.9-77.7) |
| G3 Regigigas in play, own turn 4 | 80.0% (77.4-82.4) | 77.5% (74.8-80.0) | 78.8% (76.9-80.5) |
| G3 Regigigas in play, own turn 5 | 80.8% (78.2-83.1) | 79.2% (76.6-81.6) | 80.0% (78.2-81.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 83.0% (80.5-85.2) | 83.7% (81.3-85.9) | 83.3% (81.7-84.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 95.7% (94.3-96.8) | 95.3% (93.8-96.4) | 95.5% (94.5-96.3) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 98.1% (97.1-98.8) | 98.3% (97.3-98.9) | 98.2% (97.5-98.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 99.0% (98.2-99.5) | 99.5% (98.8-99.8) | 99.2% (98.8-99.5) |
| G4.s2 a Stage 2 in play, own turn 2 | 22.0% (19.5-24.7) | 19.5% (17.2-22.1) | 20.8% (19.0-22.6) |
| G4.s2 a Stage 2 in play, own turn 3 | 38.0% (35.0-41.0) | 38.1% (35.1-41.2) | 38.0% (35.9-40.2) |
| G4.s2 a Stage 2 in play, own turn 4 | 54.9% (51.8-58.0) | 57.1% (54.0-60.1) | 56.0% (53.8-58.2) |
| G4.s2 a Stage 2 in play, own turn 5 | 68.6% (65.7-71.4) | 71.3% (68.4-74.0) | 70.0% (67.9-71.9) |
| G5.any3 an empty own turn among turns 1-3 | 15.0% (12.9-17.3) | 13.7% (11.7-16.0) | 14.3% (12.9-16.0) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.4) | 19.5% (17.2-22.1) | 9.8% (8.5-11.1) |
| G6 Kingambit with [DD] attached, own turn 3 | 32.6% (29.8-35.6) | 38.1% (35.1-41.2) | 35.4% (33.3-37.5) |
| G6 Kingambit with [DD] attached, own turn 4 | 54.9% (51.8-58.0) | 57.1% (54.0-60.1) | 56.0% (53.8-58.2) |
| G6 Kingambit with [DD] attached, own turn 5 | 68.6% (65.7-71.4) | 71.3% (68.4-74.0) | 70.0% (67.9-71.9) |
| G5 mean empty own turns in turns 1-5 | 0.710 | 0.695 | 0.703 |

Clock measures under C-his (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.6% / 10.8% [2-6] | 1.8% / 5.4% [1-3] |
| K3.by3 | 5.0% / 15.2% [3-7] | 4.4% / 11.6% [2-7] | 4.7% / 13.4% [3-7] |
| K3.by4 | 6.0% / 16.2% [4-9] | 6.6% / 13.8% [5-9] | 6.3% / 15.0% [5-8] |
| K3.by5 | 9.2% / 19.4% [7-12] | 7.2% / 20.8% [5-9] | 8.2% / 20.1% [6-10] |
| K3.by6 | 9.6% / 27.0% [7-12] | 15.2% / 37.2% [7-27] | 12.4% / 32.1% [8-19] |
| K3.by7 | 20.0% / 46.2% [9-36] | 17.8% / 58.4% [8-30] | 18.9% / 52.3% [9-33] |
| K3.by8 | 23.8% / 71.6% [10-40] | 17.8% / 62.4% [8-30] | 20.8% / 67.0% [9-35] |
| K3.never | 28.4% / 76.2% [11-52] | 37.6% / 82.2% [16-60] | 33.0% / 79.2% [13-56] |
| K3.k0 | 6.4% / 54.2% [4-9] | 4.6% / 49.2% [2-7] | 5.5% / 51.7% [3-8] |
| K3.k1 | 0.0% / 47.8% [0-0] | 0.0% / 44.6% [0-0] | 0.0% / 46.2% [0-0] |
| K3.k2 | 11.2% / 59.0% [2-26] | 9.0% / 53.6% [2-21] | 10.1% / 56.3% [2-23] |
| K3.k3p | 6.2% / 54.0% [0-15] | 4.2% / 48.8% [0-10] | 5.2% / 51.4% [0-13] |
| K4 | 17.4% / 69.2% [3-34] | 13.2% / 60.4% [3-26] | 15.3% / 64.8% [3-30] |
| K5 | 5.0% / 63.0% [3-7] | 4.8% / 55.2% [2-7] | 4.9% / 59.1% [3-7] |

Flagged differences from the base under C-his (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.6 points (+0.8 to +2.6); K3.by4: +1.9 points (+1.0 to +3.0); K3.by5: +2.2 points (+1.0 to +3.4); K3.by6: +3.7 points (+1.7 to +6.1); K3.by7: +5.0 points (+2.0 to +9.0); K3.by8: +5.3 points (+2.1 to +9.5); K3.never: -4.4 points (-8.6 to -1.4); K3.k0: +1.8 points (+0.9 to +3.0); K4: +3.5 points (+0.4 to +7.3); K5: -2.4 points (-3.4 to -1.5).

Clock measures under C-his, seat-matched (1,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 4.6% [2-7] | 2.3% [0-4] |
| K3.by3 | 5.6% / 17.2% [2-9] | 5.8% [4-8] | 5.7% / 11.5% [4-8] |
| K3.by4 | 6.4% / 18.0% [3-10] | 7.0% [4-9] | 6.7% / 12.5% [4-9] |
| K3.by5 | 9.0% / 20.6% [5-13] | 8.4% / 31.6% [8-9] | 8.7% / 26.1% [7-11] |
| K3.by6 | 9.2% / 20.8% [5-13] | 9.0% / 32.2% [8-10] | 9.1% / 26.5% [7-11] |
| K3.by7 | 23.2% / 45.0% [8-42] | 17.8% / 74.2% [8-35] | 20.5% / 59.6% [9-33] |
| K3.by8 | 23.2% / 66.4% [8-42] | 17.8% / 83.6% [8-35] | 20.5% / 75.0% [9-33] |
| K3.never | 33.6% / 76.8% [11-62] | 16.4% / 82.2% [0-38] | 25.0% / 79.5% [10-45] |
| K3.k0 | 6.6% / 49.8% [3-10] | 6.2% / 72.0% [4-9] | 6.4% / 60.9% [4-9] |
| K3.k1 | 0.0% / 43.2% [0-0] | 0.0% / 65.8% [0-0] | 0.0% / 54.5% [0-0] |
| K3.k2 | 10.4% / 53.6% [0-26] | 2.8% / 68.6% [0-6] | 6.6% / 61.1% [1-16] |
| K3.k3p | 6.2% / 49.4% [0-19] | 8.8% / 74.6% [0-25] | 7.5% / 62.0% [0-17] |
| K4 | 16.6% / 64.0% [1-34] | 11.6% / 83.0% [0-31] | 14.1% / 73.5% [2-28] |
| K5 | 4.8% / 58.6% [2-7] | 3.8% / 82.8% [2-5] | 4.3% / 70.7% [3-6] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +2.2 points (+1.1 to +3.4); K3.by4: +1.8 points (+0.6 to +3.2); K3.by5: +2.1 points (+0.7 to +3.7); K3.by6: +2.1 points (+0.7 to +3.5); K3.by7: +5.6 points (+2.1 to +9.9); K3.by8: +5.6 points (+2.1 to +9.9); K3.never: -4.3 points (-8.3 to -1.3); K3.k0: +2.0 points (+1.0 to +3.3); K5: -2.8 points (-3.8 to -1.9).

Clock measures under C-bot (1,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 3.2% [2-5] | 1.6% [1-2] |
| K3.by3 | 6.4% [4-9] | 3.4% [2-5] | 4.9% [4-6] |
| K3.by4 | 7.4% [5-10] | 5.2% [3-7] | 6.3% [5-8] |
| K3.by5 | 9.4% [6-12] | 8.0% [5-11] | 8.7% [7-11] |
| K3.by6 | 12.6% [9-16] | 10.2% / 14.2% [7-14] | 11.4% / 13.4% [9-15] |
| K3.by7 | 14.4% / 17.8% [11-18] | 12.6% / 19.8% [8-18] | 13.5% / 18.8% [10-17] |
| K3.by8 | 16.8% / 28.0% [13-21] | 13.8% / 22.8% [9-19] | 15.3% / 25.4% [12-20] |
| K3.never | 72.0% / 83.2% [62-80] | 77.2% / 86.2% [69-85] | 74.6% / 84.7% [66-82] |
| K3.k0 | 8.0% / 19.2% [5-11] | 3.4% / 12.4% [2-5] | 5.7% / 15.8% [4-7] |
| K3.k1 | 0.0% / 11.2% [0-0] | 0.0% / 9.0% [0-0] | 0.0% / 10.1% [0-0] |
| K3.k2 | 3.2% / 14.4% [1-6] | 3.6% / 12.6% [2-6] | 3.4% / 13.5% [2-6] |
| K3.k3p | 5.6% / 16.8% [2-10] | 6.8% / 15.8% [3-11] | 6.2% / 16.3% [3-10] |
| K4 | 8.8% / 21.8% [5-13] | 10.4% / 20.2% [6-15] | 9.6% / 21.0% [6-14] |
| K5 | 5.2% / 20.8% [4-7] | 6.8% / 18.0% [4-9] | 6.0% / 19.4% [4-8] |

Flagged differences from the base under C-bot (pooled; bootstrap over the recorded games, undecided counted as no): K3.by3: +1.4 points (+0.6 to +2.2); K3.by4: +1.7 points (+0.7 to +2.8); K3.by5: +2.0 points (+1.0 to +3.1); K3.by6: +2.5 points (+1.2 to +3.8); K3.by7: +2.9 points (+1.5 to +4.3); K3.by8: +3.1 points (+1.6 to +4.5); K3.never: -2.6 points (-3.8 to -1.2); K3.k0: +1.5 points (+0.7 to +2.4); K3.k3p: +1.6 points (+0.7 to +2.7); K4: +1.6 points (+0.3 to +3.1); K5: -2.7 points (-3.8 to -1.6).

Clock measures under C-fixed fast (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 4.4% [3-7, Wilson] | 2.2% [1-3, Wilson] |
| K3.by4 | 3.2% [2-5, Wilson] | 9.8% [7-13, Wilson] | 6.5% [5-8, Wilson] |
| K3.by5 | 20.0% [17-24, Wilson] | 10.8% [8-14, Wilson] | 15.4% [13-18, Wilson] |
| K3.by6 | 23.8% [20-28, Wilson] | 10.8% [8-14, Wilson] | 17.3% [15-20, Wilson] |
| K3.by7 | 23.8% [20-28, Wilson] | 10.8% [8-14, Wilson] | 17.3% [15-20, Wilson] |
| K3.by8 | 23.8% [20-28, Wilson] | 10.8% [8-14, Wilson] | 17.3% [15-20, Wilson] |
| K3.never | 76.2% [72-80, Wilson] | 89.2% [86-92, Wilson] | 82.7% [80-85, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.2% [2-5, Wilson] | 4.4% [3-7, Wilson] | 3.8% [3-5, Wilson] |
| K3.k3p | 20.6% [17-24, Wilson] | 6.4% [5-9, Wilson] | 13.5% [12-16, Wilson] |
| K4 | 23.8% [20-28, Wilson] | 10.8% [8-14, Wilson] | 17.3% [15-20, Wilson] |
| K5 | 12.2% [10-15, Wilson] | 15.2% [12-19, Wilson] | 13.7% [12-16, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; paired test on the same deals, undecided counted as no): K3.by4: +2.2 points (+1.1 to +3.3); K3.by5: +7.1 points (+5.3 to +8.9); K3.by6: +7.1 points (+5.3 to +8.9); K3.by7: +7.1 points (+5.3 to +8.9); K3.by8: +7.1 points (+5.3 to +8.9); K3.never: -7.1 points (-8.9 to -5.3); K3.k3p: +6.3 points (+4.6 to +8.0); K4: +7.1 points (+5.3 to +8.9); K5: -6.2 points (-7.8 to -4.6).

Clock measures under C-fixed medium (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 4.8% [3-7, Wilson] | 2.4% [2-4, Wilson] |
| K3.by3 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by4 | 7.2% [5-10, Wilson] | 8.2% [6-11, Wilson] | 7.7% [6-10, Wilson] |
| K3.by5 | 9.2% [7-12, Wilson] | 28.6% [25-33, Wilson] | 18.9% [17-21, Wilson] |
| K3.by6 | 36.8% [33-41, Wilson] | 32.8% [29-37, Wilson] | 34.8% [32-38, Wilson] |
| K3.by7 | 41.2% [37-46, Wilson] | 32.8% [29-37, Wilson] | 37.0% [34-40, Wilson] |
| K3.by8 | 41.2% [37-46, Wilson] | 32.8% [29-37, Wilson] | 37.0% [34-40, Wilson] |
| K3.never | 58.8% [54-63, Wilson] | 67.2% [63-71, Wilson] | 63.0% [60-66, Wilson] |
| K3.k0 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 2.0% [1-4, Wilson] | 3.4% [2-5, Wilson] | 2.7% [2-4, Wilson] |
| K3.k3p | 32.0% [28-36, Wilson] | 24.6% [21-29, Wilson] | 28.3% [26-31, Wilson] |
| K4 | 34.0% [30-38, Wilson] | 28.0% [24-32, Wilson] | 31.0% [28-34, Wilson] |
| K5 | 8.0% [6-11, Wilson] | 7.8% [6-10, Wilson] | 7.9% [6-10, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.8); K3.by4: +1.7 points (+0.7 to +2.7); K3.by5: +6.9 points (+5.1 to +8.7); K3.by6: +12.8 points (+10.5 to +15.1); K3.by7: +12.9 points (+10.6 to +15.2); K3.by8: +12.9 points (+10.6 to +15.2); K3.never: -12.9 points (-15.2 to -10.6); K3.k0: +1.9 points (+1.0 to +2.8); K3.k3p: +11.0 points (+8.9 to +13.1); K4: +11.0 points (+8.8 to +13.2); K5: -6.6 points (-8.3 to -4.9).

Clock measures under C-fixed slow (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 4.8% [3-7, Wilson] | 2.4% [2-4, Wilson] |
| K3.by3 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by4 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by5 | 7.2% [5-10, Wilson] | 9.2% [7-12, Wilson] | 8.2% [7-10, Wilson] |
| K3.by6 | 8.4% [6-11, Wilson] | 9.2% [7-12, Wilson] | 8.8% [7-11, Wilson] |
| K3.by7 | 8.4% [6-11, Wilson] | 55.6% [51-60, Wilson] | 32.0% [29-35, Wilson] |
| K3.by8 | 62.0% [58-66, Wilson] | 55.6% [51-60, Wilson] | 58.8% [56-62, Wilson] |
| K3.never | 38.0% [34-42, Wilson] | 44.4% [40-49, Wilson] | 41.2% [38-44, Wilson] |
| K3.k0 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.2% [1-3, Wilson] | 4.4% [3-7, Wilson] | 2.8% [2-4, Wilson] |
| K3.k3p | 53.6% [49-58, Wilson] | 46.4% [42-51, Wilson] | 50.0% [47-53, Wilson] |
| K4 | 54.8% [50-59, Wilson] | 50.8% [46-55, Wilson] | 52.8% [50-56, Wilson] |
| K5 | 6.8% [5-9, Wilson] | 5.4% [4-8, Wilson] | 6.1% [5-8, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.8); K3.by4: +1.9 points (+1.0 to +2.8); K3.by5: +1.4 points (+0.1 to +2.7); K3.by7: +7.6 points (+5.6 to +9.6); K3.by8: +13.2 points (+10.9 to +15.5); K3.never: -13.2 points (-15.5 to -10.9); K3.k0: +1.9 points (+1.0 to +2.8); K3.k2: -1.6 points (-2.7 to -0.5); K3.k3p: +12.9 points (+10.7 to +15.1); K4: +11.3 points (+9.1 to +13.5); K5: -3.1 points (-4.2 to -2.0).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-1, Wilson] | 4.4% [3-7, Wilson] | 2.2% [1-3, Wilson] |
| K3.by4 | 3.2% [2-5, Wilson] | 9.6% [7-12, Wilson] | 6.4% [5-8, Wilson] |
| K3.by5 | 18.4% [15-22, Wilson] | 10.6% [8-14, Wilson] | 14.5% [12-17, Wilson] |
| K3.by6 | 22.8% [19-27, Wilson] | 10.6% [8-14, Wilson] | 16.7% [15-19, Wilson] |
| K3.by7 | 22.8% [19-27, Wilson] | 10.6% [8-14, Wilson] | 16.7% [15-19, Wilson] |
| K3.by8 | 22.8% [19-27, Wilson] | 10.6% [8-14, Wilson] | 16.7% [15-19, Wilson] |
| K3.never | 77.2% [73-81, Wilson] | 89.4% [86-92, Wilson] | 83.3% [81-85, Wilson] |
| K3.k0 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.2% [2-5, Wilson] | 4.4% [3-7, Wilson] | 3.8% [3-5, Wilson] |
| K3.k3p | 19.6% [16-23, Wilson] | 6.2% [4-9, Wilson] | 12.9% [11-15, Wilson] |
| K4 | 22.8% [19-27, Wilson] | 10.6% [8-14, Wilson] | 16.7% [15-19, Wilson] |
| K5 | 12.2% [10-15, Wilson] | 15.2% [12-19, Wilson] | 13.7% [12-16, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; paired test on the same deals, undecided counted as no): K3.by4: +2.2 points (+1.1 to +3.3); K3.by5: +6.9 points (+5.2 to +8.6); K3.by6: +7.1 points (+5.3 to +8.9); K3.by7: +7.1 points (+5.3 to +8.9); K3.by8: +7.1 points (+5.3 to +8.9); K3.never: -7.1 points (-8.9 to -5.3); K3.k3p: +6.3 points (+4.6 to +8.0); K4: +7.1 points (+5.3 to +8.9); K5: -6.2 points (-7.8 to -4.6).

Clock measures under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (1,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can still happen after it.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-1, Wilson] | 4.8% [3-7, Wilson] | 2.4% [2-4, Wilson] |
| K3.by3 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by4 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.by5 | 7.2% [5-10, Wilson] | 9.2% [7-12, Wilson] | 8.2% [7-10, Wilson] |
| K3.by6 | 8.4% [6-11, Wilson] | 9.2% [7-12, Wilson] | 8.8% [7-11, Wilson] |
| K3.by7 | 8.4% [6-11, Wilson] | 44.0% [40-48, Wilson] | 26.2% [24-29, Wilson] |
| K3.by8 | 50.4% [46-55, Wilson] | 44.0% [40-48, Wilson] | 47.2% [44-50, Wilson] |
| K3.by9 | 50.4% [46-55, Wilson] | 49.2% [45-54, Wilson] | 49.8% [47-53, Wilson] |
| K3.by10 | 54.6% [50-59, Wilson] | 49.2% [45-54, Wilson] | 51.9% [49-55, Wilson] |
| K3.never | 45.4% [41-50, Wilson] | 50.8% [46-55, Wilson] | 48.1% [45-51, Wilson] |
| K3.k0 | 7.2% [5-10, Wilson] | 4.8% [3-7, Wilson] | 6.0% [5-8, Wilson] |
| K3.k1 | 0.0% [0-1, Wilson] | 0.0% [0-1, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 1.2% [1-3, Wilson] | 4.4% [3-7, Wilson] | 2.8% [2-4, Wilson] |
| K3.k3p | 46.2% [42-51, Wilson] | 40.0% [36-44, Wilson] | 43.1% [40-46, Wilson] |
| K4 | 47.4% [43-52, Wilson] | 44.4% [40-49, Wilson] | 45.9% [43-49, Wilson] |
| K5 | 6.8% [5-9, Wilson] | 5.4% [4-8, Wilson] | 6.1% [5-8, Wilson] |

Flagged differences from the base under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (pooled; paired test on the same deals, undecided counted as no): K3.by3: +1.9 points (+1.0 to +2.8); K3.by4: +1.9 points (+1.0 to +2.8); K3.by5: +1.4 points (+0.1 to +2.7); K3.by7: +5.3 points (+3.4 to +7.2); K3.by8: +9.7 points (+7.5 to +11.9); K3.by9: +9.2 points (+7.1 to +11.3); K3.by10: +8.3 points (+6.3 to +10.3); K3.never: -8.3 points (-10.3 to -6.3); K3.k0: +1.9 points (+1.0 to +2.8); K3.k2: -1.6 points (-2.7 to -0.5); K3.k3p: +8.0 points (+6.2 to +9.8); K4: +6.4 points (+4.6 to +8.2); K5: -3.1 points (-4.2 to -2.0).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard line in play (end of own turn t), own turn 1 | +1.1 (+0.4 to +1.8) FLAG | +2.3 (+1.3 to +3.3) FLAG | +1.7 (+1.1 to +2.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 2 | +1.8 (+0.8 to +2.8) FLAG | +3.2 (+1.9 to +4.5) FLAG | +2.5 (+1.7 to +3.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | +1.3 (+0.3 to +2.3) FLAG | +2.3 (+1.1 to +3.5) FLAG | +1.8 (+1.0 to +2.6) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | +0.8 (-0.1 to +1.7) | +1.9 (+0.8 to +3.0) FLAG | +1.4 (+0.7 to +2.0) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | -0.3 (-1.1 to +0.5) | +1.2 (+0.3 to +2.1) FLAG | +0.4 (-0.2 to +1.1) |
| K2 Kingambit in play, own turn 2 | +9.9 (+8.0 to +11.8) FLAG | +8.6 (+6.8 to +10.4) FLAG | +9.2 (+7.9 to +10.6) FLAG |
| K2 Kingambit in play, own turn 3 | +15.0 (+12.7 to +17.3) FLAG | +17.9 (+15.4 to +20.4) FLAG | +16.4 (+14.8 to +18.1) FLAG |
| K2 Kingambit in play, own turn 4 | +20.4 (+17.8 to +23.0) FLAG | +23.2 (+20.4 to +26.0) FLAG | +21.8 (+19.9 to +23.7) FLAG |
| K2 Kingambit in play, own turn 5 | +22.1 (+19.4 to +24.8) FLAG | +21.9 (+19.2 to +24.6) FLAG | +22.0 (+20.1 to +23.9) FLAG |
| K2 Kingambit in play, own turn 6 | +16.4 (+14.0 to +18.8) FLAG | +17.7 (+15.2 to +20.2) FLAG | +17.1 (+15.3 to +18.8) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +4.1 (+2.8 to +5.4) FLAG | +3.4 (+2.1 to +4.7) FLAG | +3.8 (+2.8 to +4.7) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +5.5 (+3.9 to +7.1) FLAG | +3.2 (+1.8 to +4.6) FLAG | +4.3 (+3.3 to +5.4) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +4.5 (+3.0 to +6.0) FLAG | +2.4 (+1.0 to +3.8) FLAG | +3.5 (+2.4 to +4.5) FLAG |
| G3 Pawniard in play, own turn 1 | +1.1 (+0.4 to +1.8) FLAG | +2.3 (+1.3 to +3.3) FLAG | +1.7 (+1.1 to +2.3) FLAG |
| G3 Pawniard in play, own turn 2 | -8.1 (-10.2 to -6.0) FLAG | -5.4 (-7.6 to -3.2) FLAG | -6.8 (-8.3 to -5.2) FLAG |
| G3 Pawniard in play, own turn 3 | -13.7 (-16.2 to -11.2) FLAG | -15.6 (-18.3 to -12.9) FLAG | -14.6 (-16.5 to -12.8) FLAG |
| G3 Pawniard in play, own turn 4 | -19.6 (-22.2 to -17.0) FLAG | -21.3 (-24.2 to -18.4) FLAG | -20.4 (-22.4 to -18.5) FLAG |
| G3 Pawniard in play, own turn 5 | -22.4 (-25.1 to -19.7) FLAG | -20.7 (-23.3 to -18.1) FLAG | -21.6 (-23.4 to -19.7) FLAG |
| G3 Kingambit in play, own turn 2 | +9.9 (+8.0 to +11.8) FLAG | +8.6 (+6.8 to +10.4) FLAG | +9.2 (+7.9 to +10.6) FLAG |
| G3 Kingambit in play, own turn 3 | +15.0 (+12.7 to +17.3) FLAG | +17.9 (+15.4 to +20.4) FLAG | +16.4 (+14.8 to +18.1) FLAG |
| G3 Kingambit in play, own turn 4 | +20.4 (+17.8 to +23.0) FLAG | +23.2 (+20.4 to +26.0) FLAG | +21.8 (+19.9 to +23.7) FLAG |
| G3 Kingambit in play, own turn 5 | +22.1 (+19.4 to +24.8) FLAG | +21.9 (+19.2 to +24.6) FLAG | +22.0 (+20.1 to +23.9) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -3.1 (-4.7 to -1.5) FLAG | -2.1 (-3.7 to -0.5) FLAG | -2.6 (-3.7 to -1.5) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -5.9 (-7.7 to -4.1) FLAG | -3.2 (-4.6 to -1.8) FLAG | -4.5 (-5.7 to -3.4) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -4.6 (-6.1 to -3.1) FLAG | -3.3 (-4.6 to -2.0) FLAG | -4.0 (-5.0 to -2.9) FLAG |
| G3 Alolan Muk in play, own turn 2 | +1.0 (+0.1 to +1.9) FLAG | +1.8 (+0.8 to +2.8) FLAG | +1.4 (+0.7 to +2.1) FLAG |
| G3 Alolan Muk in play, own turn 3 | +4.6 (+3.2 to +6.0) FLAG | +3.7 (+2.3 to +5.1) FLAG | +4.2 (+3.2 to +5.1) FLAG |
| G3 Alolan Muk in play, own turn 4 | +6.9 (+5.2 to +8.6) FLAG | +4.1 (+2.6 to +5.6) FLAG | +5.5 (+4.4 to +6.6) FLAG |
| G3 Alolan Muk in play, own turn 5 | +5.2 (+3.6 to +6.8) FLAG | +3.5 (+2.0 to +5.0) FLAG | +4.3 (+3.3 to +5.4) FLAG |
| G3 Glimmet in play, own turn 1 | +1.0 (+0.0 to +2.0) FLAG | +0.9 (+0.3 to +1.5) | +0.9 (+0.4 to +1.5) |
| G3 Glimmet in play, own turn 3 | -4.1 (-6.3 to -1.9) FLAG | -5.1 (-7.2 to -3.0) FLAG | -4.6 (-6.1 to -3.1) FLAG |
| G3 Glimmet in play, own turn 4 | -8.1 (-10.3 to -5.9) FLAG | -9.6 (-11.8 to -7.4) FLAG | -8.8 (-10.4 to -7.3) FLAG |
| G3 Glimmet in play, own turn 5 | -6.3 (-8.1 to -4.5) FLAG | -6.0 (-7.9 to -4.1) FLAG | -6.2 (-7.5 to -4.8) FLAG |
| G3 Glimmora in play, own turn 2 | +3.6 (+2.1 to +5.1) FLAG | +3.5 (+2.1 to +4.9) FLAG | +3.5 (+2.5 to +4.6) FLAG |
| G3 Glimmora in play, own turn 3 | +5.9 (+4.2 to +7.6) FLAG | +5.1 (+3.6 to +6.6) FLAG | +5.5 (+4.4 to +6.6) FLAG |
| G3 Glimmora in play, own turn 4 | +4.5 (+3.0 to +6.0) FLAG | +3.9 (+2.5 to +5.3) FLAG | +4.2 (+3.2 to +5.2) FLAG |
| G3 Glimmora in play, own turn 5 | +1.8 (+0.8 to +2.8) FLAG | +2.1 (+1.1 to +3.1) FLAG | +1.9 (+1.2 to +2.7) FLAG |
| G3 Regigigas in play, own turn 1 | +0.8 (+0.1 to +1.5) | +1.3 (+0.5 to +2.1) FLAG | +1.1 (+0.5 to +1.6) FLAG |
| G3 Regigigas in play, own turn 2 | +2.9 (+1.7 to +4.1) FLAG | +3.7 (+2.4 to +5.0) FLAG | +3.3 (+2.4 to +4.2) FLAG |
| G3 Regigigas in play, own turn 3 | +3.3 (+1.9 to +4.7) FLAG | +3.2 (+1.9 to +4.5) FLAG | +3.2 (+2.3 to +4.2) FLAG |
| G3 Regigigas in play, own turn 4 | +1.8 (+0.6 to +3.0) FLAG | +2.1 (+1.0 to +3.2) FLAG | +1.9 (+1.1 to +2.8) FLAG |
| G3 Regigigas in play, own turn 5 | +1.2 (+0.1 to +2.3) FLAG | +0.8 (-0.2 to +1.8) | +1.0 (+0.3 to +1.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | +6.0 (+4.4 to +7.6) FLAG | +5.5 (+4.0 to +7.0) FLAG | +5.8 (+4.6 to +6.9) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | +5.3 (+3.9 to +6.7) FLAG | +4.1 (+2.7 to +5.5) FLAG | +4.7 (+3.7 to +5.7) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | +1.8 (+0.8 to +2.8) FLAG | +1.6 (+0.6 to +2.6) FLAG | +1.7 (+1.0 to +2.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 2 | +9.9 (+8.0 to +11.8) FLAG | +8.6 (+6.8 to +10.4) FLAG | +9.2 (+7.9 to +10.6) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | +15.0 (+12.7 to +17.3) FLAG | +17.9 (+15.4 to +20.4) FLAG | +16.4 (+14.8 to +18.1) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +20.4 (+17.8 to +23.0) FLAG | +23.2 (+20.4 to +26.0) FLAG | +21.8 (+19.9 to +23.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +22.1 (+19.4 to +24.8) FLAG | +21.9 (+19.2 to +24.6) FLAG | +22.0 (+20.1 to +23.9) FLAG |
| G5.any3 an empty own turn among turns 1-3 | -6.8 (-8.7 to -4.9) FLAG | -8.7 (-10.7 to -6.7) FLAG | -7.8 (-9.1 to -6.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 2 | +0.0 (+0.0 to +0.0) | +8.6 (+6.8 to +10.4) FLAG | +4.3 (+3.4 to +5.2) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +13.3 (+11.1 to +15.5) FLAG | +17.9 (+15.4 to +20.4) FLAG | +15.6 (+13.9 to +17.3) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +20.4 (+17.8 to +23.0) FLAG | +23.2 (+20.4 to +26.0) FLAG | +21.8 (+19.9 to +23.7) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +22.1 (+19.4 to +24.8) FLAG | +21.9 (+19.2 to +24.6) FLAG | +22.0 (+20.1 to +23.9) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.053 (-0.084 to -0.023) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, C.**

Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; undecided counted as no):

- P1 setup (paired test on the same deals): none flagged
- C-his (per-game bootstrap): P2 at least one Glimmora had its turn +2.4 points (+1.1 to +3.6); P2 both Glimmora had their turn +3.7 points (+0.3 to +7.8); P2 the first Glimmora placed had its turn +2.7 points (+1.8 to +3.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.8 points (-5.0 to -0.9); P4 ready at the winning moment: Knocks out their strongest +4.7 points (+0.9 to +8.9); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.8 points (-2.7 to -0.9); P5 plan reached in time: Knocks out their strongest +4.6 points (+1.2 to +8.8)
- C-his, seat-matched (per-game bootstrap): P2 at least one Glimmora had its turn +2.1 points (+0.9 to +3.1); P2 both Glimmora had their turn +4.5 points (+2.1 to +8.2); P2 the first Glimmora placed had its turn +2.7 points (+1.4 to +4.0); P2 the second Glimmora placed had its turn +3.9 points (+1.6 to +7.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.6 points (-3.9 to -1.5); P4 ready at the winning moment: Knocks out their strongest +3.1 points (+0.8 to +6.1); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.5 points (-4.5 to -0.9); P5 plan reached in time: Knocks out their strongest +3.2 points (+1.0 to +6.0)
- C-bot (per-game bootstrap): P2 at least one Glimmora had its turn +1.3 points (+0.4 to +2.3); P2 both Glimmora had their turn +3.4 points (+1.2 to +5.7); P2 the first Glimmora placed had its turn +2.2 points (+1.1 to +3.5); P2 the second Glimmora placed had its turn +2.5 points (+0.3 to +4.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +3.2 points (+1.2 to +5.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -6.6 points (-8.8 to -4.4); P4 ready at the winning moment: Knocks out their strongest +3.5 points (+1.3 to +6.1); P4 not ready, ready 2 or more turns late -1.2 points (-2.3 to -0.2); P4 the moment came and Kingambit was never ready in the deal -1.9 points (-3.7 to -0.5); P5 plan reached in time: Knocks out their strongest +2.7 points (+1.1 to +4.8)
- C-fixed fast (paired test): P2 at least one Glimmora had its turn +3.7 points (+2.1 to +5.3); P2 both Glimmora had their turn +3.2 points (+1.3 to +5.1); P2 the first Glimmora placed had its turn +3.3 points (+1.8 to +4.8); P2 the second Glimmora placed had its turn +3.6 points (+1.5 to +5.7); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.7 points (-4.6 to -0.8); P4 ready at the winning moment: Knocks out their strongest +8.5 points (+6.6 to +10.4); P4 ready at the winning moment: Wins outright (a lower bound) +8.5 points (+6.6 to +10.4); P4 the moment came and Kingambit was never ready in the deal -3.3 points (-5.4 to -1.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -5.2 points (-6.7 to -3.7); P5 plan reached in time: Knocks out their strongest +8.5 points (+6.6 to +10.4); P5 plan reached in time: Wins outright (a lower bound) +8.5 points (+6.6 to +10.4)
- C-fixed medium (paired test): P2 at least one Glimmora had its turn +3.1 points (+1.7 to +4.5); P2 both Glimmora had their turn +3.1 points (+0.6 to +5.6); P2 the first Glimmora placed had its turn +4.4 points (+2.9 to +5.9); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +3.5 points (+1.4 to +5.6); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -4.2 points (-6.4 to -2.0); P4 ready at the winning moment: Knocks out their strongest +13.4 points (+11.2 to +15.6); P4 the moment came and Kingambit was never ready in the deal -5.4 points (-7.6 to -3.2); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -7.4 points (-9.1 to -5.7); P5 plan reached in time: Knocks out their strongest +12.8 points (+10.6 to +15.0)
- C-fixed slow (paired test): P2 at least one Glimmora had its turn +2.5 points (+1.3 to +3.7); P2 both Glimmora had their turn +8.4 points (+6.2 to +10.6); P2 the first Glimmora placed had its turn +3.5 points (+2.1 to +4.9); P2 the second Glimmora placed had its turn +7.4 points (+5.3 to +9.5); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left -2.7 points (-4.1 to -1.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -8.4 points (-10.4 to -6.4); P4 ready at the winning moment: Knocks out their strongest +9.6 points (+7.7 to +11.5); P4 ready at the winning moment: Wins outright (a lower bound) +9.6 points (+7.7 to +11.5); P4 not ready, ready 1 turn late -1.6 points (-2.5 to -0.7); P4 the moment came and Kingambit was never ready in the deal -2.6 points (-3.8 to -1.4); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -5.4 points (-6.8 to -4.0); P5 plan reached in time: Knocks out their strongest +8.0 points (+6.3 to +9.7); P5 plan reached in time: Wins outright (a lower bound) +8.0 points (+6.3 to +9.7)
- C-fixed reference (fast pace, 190-HP Mega ex) (paired test): P2 at least one Glimmora had its turn +3.8 points (+2.2 to +5.4); P2 both Glimmora had their turn +3.2 points (+1.3 to +5.1); P2 the first Glimmora placed had its turn +3.3 points (+1.8 to +4.8); P2 the second Glimmora placed had its turn +3.7 points (+1.6 to +5.8); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +2.3 points (+0.3 to +4.3); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -2.7 points (-4.6 to -0.8); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -1.4 points (-2.3 to -0.5)
- C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (paired test): P2 at least one Glimmora had its turn +2.5 points (+1.3 to +3.7); P2 both Glimmora had their turn +8.6 points (+6.4 to +10.8); P2 the first Glimmora placed had its turn +3.5 points (+2.1 to +4.9); P2 the second Glimmora placed had its turn +7.6 points (+5.5 to +9.7); P3 plan broken in front, cause: a Pawniard-line Pokémon promoted, nothing else left +6.2 points (+4.2 to +8.2); P3 plan broken in front, cause: Alolan Grimer or Muk in front (lead or promotion) -4.1 points (-5.9 to -2.3); P4 ready at the winning moment: Knocks out their strongest -1.4 points (-2.5 to -0.3); P4 ready at the winning moment: Wins outright (a lower bound) -1.4 points (-2.5 to -0.3); P4 the moment came and Kingambit was never ready in the deal +4.0 points (+2.7 to +5.3); P4 the winning moment never came in the deal (the Blade never reaches their strongest) -2.6 points (-3.7 to -1.5); P5 plan reached in time: Knocks out their strongest -1.4 points (-2.5 to -0.3); P5 plan reached in time: Wins outright (a lower bound) -1.4 points (-2.5 to -0.3)

**descriptive (no knockouts)**: the old G and K lines; Kingambit's speed is not the aim for this deck. G3 falls that come only from evolving are left out.

Gains (flagged, pooled): K1 Pawniard line in play (end of own turn t), own turn 1 +1.7 points; K1 Pawniard line in play (end of own turn t), own turn 2 +2.5 points; K1 Pawniard line in play (end of own turn t), own turn 3 +1.8 points; K1 Pawniard line in play (end of own turn t), own turn 4 +1.4 points; K2 Kingambit in play, own turn 2 +9.2 points; K2 Kingambit in play, own turn 3 +16.4 points; K2 Kingambit in play, own turn 4 +21.8 points; K2 Kingambit in play, own turn 5 +22.0 points; K2 Kingambit in play, own turn 6 +17.1 points; K6 Muk and Regigigas both in play, own turn 3 +3.8 points.
Gives up (flagged, pooled): none flagged.
K3-K5 under the clocks (flagged, pooled): C-his: K3.by3 +1.6; K3.by4 +1.9; K3.by5 +2.2; K3.by6 +3.7; K3.by7 +5.0; K3.by8 +5.3; K3.never -4.4; K3.k0 +1.8; K4 +3.5; K5 -2.4; C-his, seat-matched: K3.by3 +2.2; K3.by4 +1.8; K3.by5 +2.1; K3.by6 +2.1; K3.by7 +5.6; K3.by8 +5.6; K3.never -4.3; K3.k0 +2.0; K5 -2.8; C-bot: K3.by3 +1.4; K3.by4 +1.7; K3.by5 +2.0; K3.by6 +2.5; K3.by7 +2.9; K3.by8 +3.1; K3.never -2.6; K3.k0 +1.5; K3.k3p +1.6; K4 +1.6; K5 -2.7; C-fixed fast: K3.by4 +2.2; K3.by5 +7.1; K3.by6 +7.1; K3.by7 +7.1; K3.by8 +7.1; K3.never -7.1; K3.k3p +6.3; K4 +7.1; K5 -6.2; C-fixed medium: K3.by3 +1.9; K3.by4 +1.7; K3.by5 +6.9; K3.by6 +12.8; K3.by7 +12.9; K3.by8 +12.9; K3.never -12.9; K3.k0 +1.9; K3.k3p +11.0; K4 +11.0; K5 -6.6; C-fixed slow: K3.by3 +1.9; K3.by4 +1.9; K3.by5 +1.4; K3.by7 +7.6; K3.by8 +13.2; K3.never -13.2; K3.k0 +1.9; K3.k2 -1.6; K3.k3p +12.9; K4 +11.3; K5 -3.1; C-fixed reference (fast pace, 190-HP Mega ex): K3.by4 +2.2; K3.by5 +6.9; K3.by6 +7.1; K3.by7 +7.1; K3.by8 +7.1; K3.never -7.1; K3.k3p +6.3; K4 +7.1; K5 -6.2; C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns): K3.by3 +1.9; K3.by4 +1.9; K3.by5 +1.4; K3.by7 +5.3; K3.by8 +9.7; K3.by9 +9.2; K3.by10 +8.3; K3.never -8.3; K3.k0 +1.9; K3.k2 -1.6; K3.k3p +8.0; K4 +6.4; K5 -3.1.
Not valued here (changed cards the script never plays: they count as blanks): Ilima, Lucky Ice Pop, Red.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex), C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## How much each open choice matters (on the base list)

Each alternative is run once on the base list on the same deals, against the default config (T-first-KO, Copycat by his valuation, approximated, the Pawniard line after an Active Glimmora's Energy, the promotion order of the plan file). Pooled differences in percentage points, with "*" for a range that excludes 0 and a difference of at least 1 point. Ranges: the per-game bootstrap over the recorded games under C-his and C-bot (a bootstrap over the recorded games, 1,000 resamples), the paired test on the same deals under C-fixed and for the setup measures. These runs are on the base only; nothing here is a version.

Setup measures with no knock-outs (Pawniard is benched at once under T-first-KO and T-late there, so the bench-trigger rows differ only on T-now and T-pieces):

| Alternative | P1 | K1.t1 | K1.t3 | K2.t3 | K2.t5 | G5.any3 | G6.t3 |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +0.0 | +0.2 | +5.4* | +0.5 | +5.1* | +0.6 | +0.4 |
| T-late: Pawniard benched one own turn after T-first-KO | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | -40.5* | -47.4* | -7.7* | -18.1* | -0.4 | -7.1* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | -5.5* | +0.0 | +0.0 | +0.1 | +0.0 | -0.2 | +0.4 |
| Poke Ball over names, not cards | +0.0 | +1.8* | +0.7 | -0.4 | -0.6 | -1.1* | -0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | +0.0 | -1.6* | -3.8* | -2.2* | -5.1* | +7.4* | -2.1* |
| Copycat never played | +0.0 | -2.6* | -4.8* | -4.6* | -8.8* | +10.6* | -4.1* |
| Energy order: the Pawniard line before an Active Glimmora | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +1.8* |
| promotion order: Regigigas first | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | +0.0 | -2.1* | -3.6* | -4.5* | -9.2* | +6.0* | -4.0* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +0.0 | +2.4* | +3.8* | +9.7* | +12.8* | -3.1* | +8.5* |

Plan lines under C-his, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.7 | -2.5 | +0.0 | +2.7* | -1.8 | +6.7* | +0.2 | +5.4* | +0.1 | -2.4* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.4 | +1.4* | +0.0 | -3.0* | +0.0 | -2.4 | -0.1 | -2.9 | +0.0 | +3.6* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.4 | -1.2 | +0.0 | -2.5* | +1.6 | +0.2 | -0.3 | -1.6 | -0.3 | +3.4* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +1.0* | +0.6 | +17.1* | -2.1* | -4.2* | -2.3* | -0.2 | -4.1* | -0.3 | -0.4 |
| Poke Ball over names, not cards | -0.6 | -0.7 | +0.0 | -0.4 | -0.9 | +0.5 | -0.2 | +0.7 | -0.3 | -0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -2.8* | -5.4* | +0.0 | +0.6 | +2.7* | -0.8 | +0.0 | -1.1 | +0.1 | +2.3* |
| Copycat never played | -3.5* | -7.0* | +0.0 | +0.6 | +3.8* | -1.5 | -0.2 | -2.4* | -0.1 | +3.4* |
| Energy order: the Pawniard line before an Active Glimmora | -13.8* | -18.0* | +0.0 | -0.1 | +0.0 | +2.6 | +0.0 | +4.4 | +0.0 | -0.1 |
| promotion order: Regigigas first | -6.2* | -13.9* | +0.0 | +0.0 | +0.1 | +1.1 | -0.1 | +1.7 | -0.1 | +0.3 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |

Plan lines under C-his, seat-matched, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.7 | -2.9 | +0.0 | +4.0* | -3.1* | +5.1 | +0.0 | +3.8 | +0.0 | -3.6* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.2 | +1.7 | +0.0 | -3.1* | +0.7 | -3.3 | +0.1 | -3.0 | +0.1 | +3.4* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.4 | -1.7 | +0.0 | -0.3 | +0.9 | -0.5 | -0.5 | -1.5 | -0.2 | +1.5 |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.7 | +0.1 | +17.1* | -1.8* | -4.4* | -3.2* | -0.8 | -4.3* | -0.8 | -0.1 |
| Poke Ball over names, not cards | -1.0 | -1.1 | +0.0 | +1.0 | +0.0 | +0.3 | +0.1 | +0.6 | +0.1 | -1.3* |
| Copycat: the fallback rule (his 2 v 8), approximated | -3.7* | -4.9* | +0.0 | +0.8 | +3.4* | -1.8* | -0.7 | -1.2 | -0.3 | +2.1* |
| Copycat never played | -4.6* | -6.7* | +0.0 | +0.8 | +4.0* | -2.3* | -0.9 | -2.0* | -0.5 | +2.9* |
| Energy order: the Pawniard line before an Active Glimmora | -18.4* | -22.5* | +0.0 | -0.1 | +0.0 | +3.2 | +0.0 | +4.1 | +0.0 | -0.8 |
| promotion order: Regigigas first | -7.0* | -14.2* | +0.0 | +0.5 | +0.2 | +1.2 | +0.0 | +1.9 | +0.0 | -0.3 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |

Plan lines under C-bot, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | -0.7 | +8.7* | +0.0 | +6.2* | -4.4* | +4.4* | +0.0 | +2.1* | +0.0 | -7.9* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.3 | +7.0* | +0.0 | -7.6* | +6.2* | -2.1* | +0.0 | -2.2* | +0.0 | +4.9* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | -0.5 | +4.3* | +0.0 | -2.7 | +1.1 | -0.8 | -0.1 | -3.3* | -0.1 | -2.0 |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +0.1 | +3.8* | +17.1* | -3.8* | -6.6* | -1.0* | -0.1 | -2.3* | -0.1 | -2.9* |
| Poke Ball over names, not cards | -1.5* | -0.4 | +0.0 | +0.7 | -0.4 | -0.4 | +0.2 | -0.5 | +0.2 | +0.5 |
| Copycat: the fallback rule (his 2 v 8), approximated | -5.1* | -5.3* | +0.0 | +0.7 | +3.0* | -1.1* | -0.1 | -1.7* | +0.0 | +0.9 |
| Copycat never played | -6.2* | -7.1* | +0.0 | +0.1 | +4.3* | -1.6* | -0.2 | -2.3* | +0.0 | +1.3 |
| Energy order: the Pawniard line before an Active Glimmora | -17.8* | -20.0* | +0.0 | -1.9* | +0.0 | +4.0* | +0.0 | +1.4* | +0.0 | -1.2* |
| promotion order: Regigigas first | -2.2* | -7.5* | +0.0 | -0.8 | +0.5 | +1.5* | +0.0 | +0.5 | +0.0 | -0.3 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.5* | -5.4* | +0.0 | -0.4 | +3.9* | -1.7* | -0.1 | -2.6* | -0.1 | +1.8* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +1.6* | +4.1* | +0.0 | +3.7* | -5.1* | +1.8* | +0.0 | +1.8* | +0.3 | -1.6* |

Plan lines under C-fixed fast, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +0.8 | +0.1 | +0.0 | +6.4* | +0.3 | +1.2* | +1.2* | +1.2* | +1.2* | -6.0* |
| T-late: Pawniard benched one own turn after T-first-KO | +1.1* | +2.0* | +0.0 | -11.3* | +1.6* | -3.2* | -3.2* | -3.4* | -3.4* | +6.7* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | +0.4 | +0.0 | -9.6* | -0.4 | -4.8* | -4.8* | -5.1* | -5.1* | +0.5 |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +2.7* | +2.6* | +17.1* | -4.6* | -5.7* | -2.0* | -2.0* | -2.2* | -2.2* | +1.7* |
| Poke Ball over names, not cards | -0.7 | +0.7 | +0.0 | +0.2 | +0.7 | +0.0 | +0.0 | +0.1 | +0.1 | -0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -6.1* | -4.0* | +0.0 | +1.4 | -0.3 | -2.4* | -2.4* | -3.0* | -3.0* | +1.4* |
| Copycat never played | -7.2* | -5.8* | +0.0 | +1.4 | +0.3 | -3.9* | -3.9* | -4.8* | -4.8* | +3.0* |
| Energy order: the Pawniard line before an Active Glimmora | -28.1* | -11.1* | +0.0 | -2.8* | +0.0 | +1.2* | +1.2* | +1.2* | +1.2* | -2.2* |
| promotion order: Regigigas first | -1.3* | -1.8* | +0.0 | -0.5 | +0.4 | -0.3 | -0.3 | -0.2 | -0.2 | -0.8 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.8* | -4.5* | +0.0 | -0.1 | +0.6 | -3.5* | -3.5* | -4.4* | -4.4* | +3.2* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +4.6* | +4.4* | +0.0 | +1.3 | -2.5* | +7.4* | +7.4* | +8.1* | +8.1* | -7.3* |

Plan lines under C-fixed medium, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +1.5 | +5.0* | +0.0 | -1.9 | -3.4* | +3.7* | +0.0 | +2.8* | +0.0 | -9.4* |
| T-late: Pawniard benched one own turn after T-first-KO | +1.6* | +6.4* | +0.0 | -12.2* | +7.2* | -5.9* | +0.0 | -4.8* | +0.0 | +11.9* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.5 | +2.3* | +0.0 | -11.3* | +1.7* | -4.8* | +0.0 | -5.5* | +0.0 | +1.8 |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +1.4* | +4.5* | +17.1* | -4.9* | -5.6* | -4.2* | +0.0 | -4.6* | +0.0 | -0.6 |
| Poke Ball over names, not cards | -0.1 | +1.0 | +0.0 | -0.2 | -0.7 | +0.0 | +0.0 | +0.0 | +0.0 | -0.9 |
| Copycat: the fallback rule (his 2 v 8), approximated | -5.7* | -6.9* | +0.0 | +0.9 | +0.3 | -3.0* | +0.0 | -3.4* | +0.0 | +3.7* |
| Copycat never played | -6.5* | -9.1* | +0.0 | +0.8 | +1.0 | -4.8* | +0.0 | -5.3* | +0.0 | +5.2* |
| Energy order: the Pawniard line before an Active Glimmora | -29.1* | -22.3* | +0.0 | -8.7* | +0.0 | +2.0* | +0.0 | +1.3* | +0.0 | -3.2* |
| promotion order: Regigigas first | -2.6* | -6.6* | +0.0 | -3.6* | +1.6* | -0.6 | +0.0 | -0.4 | +0.0 | -1.6* |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.6* | -5.7* | +0.0 | -0.4 | +1.9 | -4.5* | +0.0 | -4.9* | +0.0 | +5.5* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +4.2* | +4.8* | +0.0 | +4.9* | -4.4* | +11.6* | +0.0 | +11.3* | +0.0 | -10.3* |

Plan lines under C-fixed slow, difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +1.6* | +1.7 | +0.0 | +2.8* | -1.1 | +1.4* | +1.4* | +1.1* | +1.1* | -4.7* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.7 | +1.3* | +0.0 | -1.7* | +3.8* | +0.1 | +0.1 | +0.1 | +0.1 | +2.4* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.7 | -0.4 | +0.0 | +0.2 | +7.9* | -5.8* | -5.8* | -4.8* | -4.8* | +8.1* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +1.0* | +4.0* | +17.1* | -1.9* | -4.8* | -8.2* | -8.2* | -8.5* | -8.5* | +3.6* |
| Poke Ball over names, not cards | +0.0 | +0.2 | +0.0 | -0.3 | -0.4 | +0.2 | +0.2 | +0.3 | +0.3 | -0.1 |
| Copycat: the fallback rule (his 2 v 8), approximated | -4.9* | -10.0* | +0.0 | +1.9* | +4.6* | -5.8* | -5.8* | -6.6* | -6.6* | +4.5* |
| Copycat never played | -5.7* | -13.0* | +0.0 | +3.1* | +6.8* | -8.9* | -8.9* | -9.2* | -9.2* | +6.9* |
| Energy order: the Pawniard line before an Active Glimmora | -7.8* | -38.8* | +0.0 | -0.9 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | -0.3 |
| promotion order: Regigigas first | +0.3 | -6.8* | +0.0 | +0.3 | +0.1 | -1.1* | -1.1* | -1.1* | -1.1* | +0.5 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -3.8* | -9.0* | +0.0 | +1.8* | +7.6* | -7.5* | -7.5* | -7.3* | -7.3* | +6.9* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +2.4* | +9.0* | +0.0 | -2.8* | -5.6* | +8.3* | +8.3* | +7.4* | +7.4* | -9.7* |

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex), difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +0.8 | -0.1 | +0.0 | +8.6* | +0.3 | -0.2 | -0.2 | -0.2 | -0.2 | -5.4* |
| T-late: Pawniard benched one own turn after T-first-KO | +1.1* | +1.6* | +0.0 | -12.4* | +1.6* | -0.3 | -0.3 | -0.3 | -0.3 | +6.1* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | +0.3 | +0.0 | -9.6* | -0.4 | -1.2* | -1.2* | -1.2* | -1.2* | +0.6 |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +2.7* | +2.6* | +17.1* | -4.6* | -5.7* | -0.2 | -0.2 | -0.2 | -0.2 | +1.6* |
| Poke Ball over names, not cards | -0.7 | +0.7 | +0.0 | +0.3 | +0.7 | +0.0 | +0.0 | +0.0 | +0.0 | -0.4 |
| Copycat: the fallback rule (his 2 v 8), approximated | -6.1* | -4.1* | +0.0 | +1.6 | -0.3 | -1.0* | -1.0* | -1.0* | -1.0* | +1.3* |
| Copycat never played | -7.2* | -6.1* | +0.0 | +1.3 | +0.3 | -1.5* | -1.5* | -1.5* | -1.5* | +2.6* |
| Energy order: the Pawniard line before an Active Glimmora | -28.0* | -11.1* | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | -1.3* |
| promotion order: Regigigas first | -0.8 | -1.8* | +0.0 | +0.6 | +0.4 | +0.0 | +0.0 | +0.0 | +0.0 | -0.3 |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -4.8* | -4.5* | +0.0 | -0.2 | +0.6 | -1.5* | -1.5* | -1.5* | -1.5* | +3.0* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +4.7* | +4.3* | +0.0 | +2.7* | -2.5* | +1.3* | +1.3* | +1.3* | +1.3* | -7.3* |

Plan lines under C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns), difference from the default (pooled points, undecided as no):

| Alternative | P2.any | P2.both | P3.pawn_lead | P3.pawn_promo | P3.grimer_muk | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default) | +1.6* | +1.7 | +0.0 | +5.3* | +0.1 | -0.3 | -0.3 | -0.3 | -0.3 | -4.1* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.7 | +2.0* | +0.0 | -3.2* | +3.1* | +0.8 | +0.8 | +0.8 | +0.8 | +2.6* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.7 | -0.3 | +0.0 | -7.7* | +6.3* | +1.2* | +1.2* | +1.2* | +1.2* | +5.5* |
| lead order: Pawniard first (P1 is still "Regigigas leads") | +1.0* | +3.8* | +17.1* | -7.7* | -2.8* | -0.9 | -0.9 | -0.9 | -0.9 | +2.8* |
| Poke Ball over names, not cards | +0.0 | +1.0 | +0.0 | -0.4 | -0.6 | +0.4 | +0.4 | +0.4 | +0.4 | +0.2 |
| Copycat: the fallback rule (his 2 v 8), approximated | -4.9* | -9.7* | +0.0 | -3.0* | +3.5* | -1.3* | -1.3* | -1.3* | -1.3* | +5.6* |
| Copycat never played | -5.7* | -12.8* | +0.0 | -5.0* | +4.7* | -1.2* | -1.2* | -1.2* | -1.2* | +7.6* |
| Energy order: the Pawniard line before an Active Glimmora | -7.4* | -39.2* | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| promotion order: Regigigas first | +0.3 | -2.9* | +0.0 | +0.9 | +1.2* | +0.4 | +0.4 | +0.4 | +0.4 | -1.1* |
| opponent's hand 2 (Copycat's draw under every clock but C-his) | -3.8* | -8.7* | +0.0 | -4.8* | +5.7* | -0.2 | -0.2 | -0.1 | -0.1 | +6.9* |
| opponent's hand 6 (Copycat's draw under every clock but C-his) | +2.4* | +8.7* | +0.0 | +5.6* | -2.5* | -0.7 | -0.7 | -0.7 | -0.7 | -6.7* |

## The run record

- **code sha256**: 2c8b531f85b489fbf77954473fff8378c0040af6cfcc6d97d063b0b0a6ab0bbc
- **engine commit**: pinned rules-switch-2 engine, main 70319c3d (engine unchanged since c045ede); no engine program is run
- **rulings**: R1: glimmora_turn=attacked_once; R2: never_evolve_active_grimer; P3_by_cause; R3: slow=180hp_k3_turns_3_5_7; 220hp_reference_horizon_10; by: coordinator, Oct 15
- **seeds**: 24,700,000,000 + deal index i (deal i is the same in every version and under every clock); 2,000 deals with no knock-outs, 1,000 deals per clock
- **clock sources**: C-his: rl/results/pause_games_new_2026-10-13/v2/positions_all.json (12 Kingambit games); C-bot: rl/results/kx3_on_rules2_2026-10/replay_b/games.jsonl (64 deck-01 rows); C-fixed: fast, medium, slow, and the 190- and 220-HP references (SPEC, R3)
- **base list**: decks/dustin/01-kingambit-as-played.txt (card-list id 73dfed58d1d6)
- **plan config**: rl/setup_tester/plans/kingambit.json
- **plan overrides**: none
- **wall time**: 94 s, 1 process(es) (every version under both Copycat rules, and the choice runs, included)
- **speed**: 1,728 deals per second per process (80,000 deals in 46 s of version time)

