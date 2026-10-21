# Setup tester: kingambit_amendment1_run

Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on the same deals for every version. It does not say who wins.
**Plan config follows SPEC_AMENDMENT_1 (Dustin, Oct 15):** Regigigas leads; Pawniard is held until the bench trigger (first_ko; default first_ko = our first turn after one of ours was knocked out, a spot free); Grimer and Muk are benched; Glimmora gets a turn; Energy goes to the Pawniard line up to [DD], then the Active Glimmora, then Regigigas while Muk is in play. The lines that lead are P1-P5; the old G and K lines stay below "descriptive (speed is not the goal)". The no-knock-out runs have no knock-out to trigger first_ko, so they bench Pawniard at once (T-now), and say so.
**Copycat is the N/M rule** (play it when fewer than N still-needed plan cards are in hand and the opponent's hand is at least M larger than ours without it). **N and M are still to be asked of Dustin, once.** The headline uses N=2, M=1; the N x M grid is in the choices section.
**PROPOSED, not yet confirmed by Dustin:** the plan lines, the lead and promotion orders, the Copycat N and M, and the assumed strongest Pokémon of C-fixed. Nothing here is to be reported to him as settled until he confirms or rewrites each.

## base (card-list id 73dfed58d1d6)

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
| P1 Regigigas leads (the Active at the start of the game; exact above) | 29.0% (28.6-29.4) | 29.2% (28.8-29.6) | 29.1% (28.8-29.4) |

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 48.3% / 75.4% [37-61] | 35.1% / 71.8% [22-48] | 41.7% / 73.6% [30-54] |
| P2 both Glimmora had their turn | 3.9% / 52.5% [1-9] | 2.7% / 55.5% [0-6] | 3.3% / 54.0% [1-8] |
| P2 the first Glimmora placed had its turn | 39.0% / 71.9% [27-52] | 26.8% / 69.6% [13-41] | 32.9% / 70.8% [21-46] |
| P2 the second Glimmora placed had its turn | 13.2% / 56.0% [5-23] | 11.0% / 57.6% [5-18] | 12.1% / 56.8% [5-20] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 35.2% / 68.0% [30-40] | 36.2% / 69.8% [30-42] | 35.7% / 68.9% [30-41] |
| P3, cause: the opening (still the starting Active) | 22.8% / 61.0% [22-24] | 20.2% / 62.8% [18-22] | 21.5% / 61.9% [20-23] |
| P3, cause: promoted, nothing else left | 12.4% / 56.4% [7-18] | 16.0% / 60.5% [10-23] | 14.2% / 58.5% [8-20] |
| P4 ready at the winning moment: Knocks out their strongest | 18.4% / 43.7% [6-31] | 12.0% / 40.0% [3-22] | 15.2% / 41.8% [4-26] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 2.9% / 28.2% [0-9] | 1.5% / 29.6% [0-5] | 2.2% / 28.9% [0-7] |
| P4 not ready, ready 1 turn late | 5.9% / 41.9% [0-16] | 4.9% / 46.8% [0-13] | 5.4% / 44.4% [0-14] |
| P4 not ready, ready 2 or more turns late | 0.9% / 37.0% [0-3] | 1.1% / 43.0% [0-3] | 1.0% / 40.0% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 7.5% / 43.5% [0-18] | 7.8% / 49.8% [0-20] | 7.7% / 46.7% [0-19] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 31.2% / 56.5% [10-56] | 32.3% / 60.3% [14-55] | 31.8% / 58.4% [12-55] |
| P5 plan reached in time: Knocks out their strongest | 25.2% / 61.3% [11-41] | 17.9% / 59.9% [7-31] | 21.6% / 60.6% [9-36] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.1% / 39.2% [0-10] | 1.9% / 43.8% [0-6] | 2.5% / 41.5% [0-8] |

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 51.0% / 74.1% [34-67] | 30.3% / 84.8% [0-53] | 40.7% / 79.5% [25-57] |
| P2 both Glimmora had their turn | 5.2% / 48.1% [1-12] | 0.6% / 80.1% [0-1] | 2.9% / 64.1% [1-7] |
| P2 the first Glimmora placed had its turn | 39.3% / 70.0% [23-57] | 27.9% / 84.3% [0-53] | 33.6% / 77.1% [20-48] |
| P2 the second Glimmora placed had its turn | 16.9% / 52.2% [7-29] | 3.0% / 80.6% [0-7] | 10.0% / 66.4% [4-20] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 34.7% / 64.4% [28-41] | 40.9% / 88.7% [26-50] | 37.8% / 76.5% [30-44] |
| P3, cause: the opening (still the starting Active) | 22.6% / 56.9% [21-24] | 22.4% / 84.8% [21-23] | 22.5% / 70.8% [22-23] |
| P3, cause: promoted, nothing else left | 12.1% / 51.2% [5-19] | 18.4% / 83.9% [3-28] | 15.2% / 67.6% [7-22] |
| P4 ready at the winning moment: Knocks out their strongest | 20.0% / 42.1% [4-37] | 7.5% / 58.8% [0-23] | 13.8% / 50.4% [4-26] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.2% / 26.2% [0-13] | 0.0% / 51.2% [0-0] | 2.1% / 38.7% [0-8] |
| P4 not ready, ready 1 turn late | 8.3% / 38.4% [0-23] | 0.0% / 72.5% [0-0] | 4.2% / 55.4% [0-13] |
| P4 not ready, ready 2 or more turns late | 1.3% / 31.3% [0-4] | 0.0% / 72.5% [0-0] | 0.6% / 51.9% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 10.5% / 40.5% [0-24] | 0.0% / 72.5% [0-0] | 5.2% / 56.5% [0-14] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 29.8% / 51.9% [8-59] | 19.9% / 71.2% [1-45] | 24.9% / 61.5% [10-45] |
| P5 plan reached in time: Knocks out their strongest | 29.6% / 59.7% [11-50] | 7.5% / 80.0% [0-23] | 18.6% / 69.9% [7-34] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.5% / 34.5% [0-14] | 0.0% / 72.5% [0-0] | 2.2% / 53.5% [0-9] |

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 45.7% / 51.8% [42-50] | 30.8% / 39.1% [26-36] | 38.3% / 45.4% [34-43] |
| P2 both Glimmora had their turn | 3.5% / 14.8% [2-6] | 1.9% / 14.2% [1-3] | 2.7% / 14.5% [1-4] |
| P2 the first Glimmora placed had its turn | 38.0% / 45.4% [35-41] | 23.8% / 33.3% [19-28] | 30.9% / 39.4% [27-34] |
| P2 the second Glimmora placed had its turn | 11.2% / 21.1% [7-16] | 9.0% / 20.0% [6-13] | 10.1% / 20.6% [7-14] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 42.7% / 49.8% [40-46] | 45.4% / 52.0% [43-48] | 44.0% / 50.9% [41-47] |
| P3, cause: the opening (still the starting Active) | 22.7% / 31.7% [22-24] | 20.9% / 30.7% [20-22] | 21.8% / 31.2% [21-23] |
| P3, cause: promoted, nothing else left | 19.9% / 29.7% [17-23] | 24.5% / 33.7% [22-27] | 22.2% / 31.7% [20-25] |
| P4 ready at the winning moment: Knocks out their strongest | 12.5% / 18.5% [7-18] | 8.7% / 15.8% [5-12] | 10.6% / 17.1% [6-15] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.3% / 6.2% [0-1] | 0.7% / 7.8% [0-2] | 0.5% / 7.0% [0-1] |
| P4 not ready, ready 1 turn late | 2.4% / 10.1% [1-4] | 2.4% / 11.9% [1-4] | 2.4% / 11.0% [1-4] |
| P4 not ready, ready 2 or more turns late | 1.0% / 8.7% [0-2] | 1.3% / 10.8% [0-2] | 1.2% / 9.7% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 6.5% / 14.2% [3-10] | 8.0% / 17.4% [4-12] | 7.2% / 15.8% [4-11] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.9% / 75.8% [59-81] | 70.2% / 77.3% [60-80] | 70.1% / 76.6% [59-80] |
| P5 plan reached in time: Knocks out their strongest | 15.9% / 23.6% [9-23] | 12.4% / 21.8% [7-18] | 14.1% / 22.7% [8-21] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.4% / 8.1% [0-1] | 0.7% / 10.2% [0-2] | 0.6% / 9.2% [0-1] |

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 both Glimmora had their turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the first Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the second Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 58.2% [57-59, Wilson] | 47.0% [46-48, Wilson] | 52.6% [52-53, Wilson] |
| P3, cause: the opening (still the starting Active) | 20.3% [20-21, Wilson] | 13.2% [13-14, Wilson] | 16.8% [16-17, Wilson] |
| P3, cause: promoted, nothing else left | 37.9% [37-39, Wilson] | 33.7% [33-35, Wilson] | 35.8% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 17.6% [17-18, Wilson] | 6.3% [6-7, Wilson] | 12.0% [12-12, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 17.6% [17-18, Wilson] | 6.3% [6-7, Wilson] | 12.0% [12-12, Wilson] |
| P4 not ready, ready 1 turn late | 1.0% [1-1, Wilson] | 0.3% [0-0, Wilson] | 0.7% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 20.3% [19-21, Wilson] | 15.1% [14-16, Wilson] | 17.7% [17-18, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 61.1% [60-62, Wilson] | 78.3% [77-79, Wilson] | 69.7% [69-70, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 18.6% [18-19, Wilson] | 6.6% [6-7, Wilson] | 12.6% [12-13, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 18.6% [18-19, Wilson] | 6.6% [6-7, Wilson] | 12.6% [12-13, Wilson] |

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 31.9% [31-33, Wilson] | 0.0% [0-0, Wilson] | 15.9% [15-16, Wilson] |
| P2 both Glimmora had their turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the first Glimmora placed had its turn | 31.9% [31-33, Wilson] | 0.0% [0-0, Wilson] | 15.9% [15-16, Wilson] |
| P2 the second Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 58.8% [58-60, Wilson] | 58.2% [57-59, Wilson] | 58.5% [58-59, Wilson] |
| P3, cause: the opening (still the starting Active) | 22.2% [21-23, Wilson] | 21.0% [20-22, Wilson] | 21.6% [21-22, Wilson] |
| P3, cause: promoted, nothing else left | 36.5% [36-37, Wilson] | 37.2% [36-38, Wilson] | 36.9% [36-38, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 30.1% [29-31, Wilson] | 17.7% [17-18, Wilson] | 23.9% [23-24, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 1.4% [1-2, Wilson] | 1.2% [1-1, Wilson] | 1.3% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 19.5% [19-20, Wilson] | 21.1% [20-22, Wilson] | 20.3% [20-21, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 49.0% [48-50, Wilson] | 60.1% [59-61, Wilson] | 54.5% [54-55, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 31.5% [31-32, Wilson] | 18.9% [18-20, Wilson] | 25.2% [25-26, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 78.8% [78-80, Wilson] | 51.6% [51-53, Wilson] | 65.2% [65-66, Wilson] |
| P2 both Glimmora had their turn | 15.6% [15-16, Wilson] | 9.3% [9-10, Wilson] | 12.4% [12-13, Wilson] |
| P2 the first Glimmora placed had its turn | 51.1% [50-52, Wilson] | 22.1% [21-23, Wilson] | 36.6% [36-37, Wilson] |
| P2 the second Glimmora placed had its turn | 43.3% [42-44, Wilson] | 38.9% [38-40, Wilson] | 41.1% [40-42, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 37.8% [37-39, Wilson] | 43.5% [43-44, Wilson] | 40.7% [40-41, Wilson] |
| P3, cause: the opening (still the starting Active) | 22.2% [21-23, Wilson] | 21.0% [20-22, Wilson] | 21.6% [21-22, Wilson] |
| P3, cause: promoted, nothing else left | 15.6% [15-16, Wilson] | 22.5% [22-23, Wilson] | 19.1% [19-20, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 both Glimmora had their turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the first Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the second Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 58.2% [57-59, Wilson] | 47.0% [46-48, Wilson] | 52.6% [52-53, Wilson] |
| P3, cause: the opening (still the starting Active) | 20.3% [20-21, Wilson] | 13.2% [13-14, Wilson] | 16.8% [16-17, Wilson] |
| P3, cause: promoted, nothing else left | 37.9% [37-39, Wilson] | 33.7% [33-35, Wilson] | 35.8% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 3.9% [4-4, Wilson] | 1.4% [1-2, Wilson] | 2.7% [2-3, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 92.7% [92-93, Wilson] | 97.7% [97-98, Wilson] | 95.2% [95-95, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.4% [3-4, Wilson] | 0.8% [1-1, Wilson] | 2.1% [2-2, Wilson] |

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 28.9% (28.5-29.3) | 29.1% (28.7-29.5) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 55.3% (54.9-55.7) | 55.1% (54.7-55.5) | 55.2% (54.9-55.5) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 68.2% (67.8-68.6) | 67.9% (67.4-68.3) | 68.0% (67.7-68.3) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 77.3% (76.9-77.6) | 77.2% (76.8-77.5) | 77.2% (77.0-77.5) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 85.0% (84.7-85.3) | 84.9% (84.5-85.2) | 84.9% (84.7-85.1) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 91.0% (90.8-91.3) | 91.1% (90.8-91.3) | 91.1% (90.9-91.2) |
| K2 Kingambit in play, own turn 2 | 10.8% (10.5-11.0) | 10.5% (10.2-10.7) | 10.6% (10.4-10.8) |
| K2 Kingambit in play, own turn 3 | 20.7% (20.3-21.1) | 20.7% (20.3-21.0) | 20.7% (20.4-20.9) |
| K2 Kingambit in play, own turn 4 | 33.7% (33.3-34.1) | 33.9% (33.4-34.3) | 33.8% (33.5-34.1) |
| K2 Kingambit in play, own turn 5 | 49.6% (49.2-50.1) | 49.7% (49.3-50.2) | 49.7% (49.4-50.0) |
| K2 Kingambit in play, own turn 6 | 66.2% (65.7-66.6) | 66.5% (66.1-66.9) | 66.3% (66.0-66.6) |
| K6 Muk and Regigigas both in play, own turn 3 | 23.9% (23.5-24.3) | 24.0% (23.6-24.4) | 23.9% (23.7-24.2) |
| K6 Muk and Regigigas both in play, own turn 4 | 32.0% (31.5-32.4) | 32.4% (32.0-32.8) | 32.2% (31.9-32.4) |
| K6 Muk and Regigigas both in play, own turn 5 | 38.9% (38.5-39.3) | 39.0% (38.6-39.4) | 38.9% (38.6-39.2) |
| G3 Pawniard in play, own turn 1 | 55.3% (54.9-55.7) | 55.1% (54.7-55.5) | 55.2% (54.9-55.5) |
| G3 Pawniard in play, own turn 2 | 57.4% (57.0-57.8) | 57.4% (57.0-57.8) | 57.4% (57.1-57.7) |
| G3 Pawniard in play, own turn 3 | 56.6% (56.1-57.0) | 56.5% (56.0-56.9) | 56.5% (56.2-56.8) |
| G3 Pawniard in play, own turn 4 | 51.3% (50.9-51.7) | 51.0% (50.6-51.4) | 51.1% (50.8-51.5) |
| G3 Pawniard in play, own turn 5 | 41.4% (41.0-41.8) | 41.3% (40.9-41.8) | 41.4% (41.1-41.7) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 10.8% (10.5-11.0) | 10.5% (10.2-10.7) | 10.6% (10.4-10.8) |
| G3 Kingambit in play, own turn 3 | 20.7% (20.3-21.1) | 20.7% (20.3-21.0) | 20.7% (20.4-20.9) |
| G3 Kingambit in play, own turn 4 | 33.7% (33.3-34.1) | 33.9% (33.4-34.3) | 33.8% (33.5-34.1) |
| G3 Kingambit in play, own turn 5 | 49.6% (49.2-50.1) | 49.7% (49.3-50.2) | 49.7% (49.4-50.0) |
| G3 Alolan Grimer in play, own turn 1 | 51.9% (51.5-52.4) | 52.3% (51.9-52.7) | 52.1% (51.8-52.4) |
| G3 Alolan Grimer in play, own turn 2 | 34.6% (34.2-35.0) | 34.5% (34.1-34.9) | 34.5% (34.2-34.8) |
| G3 Alolan Grimer in play, own turn 3 | 27.4% (27.0-27.8) | 27.5% (27.1-27.9) | 27.5% (27.2-27.8) |
| G3 Alolan Grimer in play, own turn 4 | 20.2% (19.8-20.5) | 19.9% (19.6-20.3) | 20.0% (19.8-20.3) |
| G3 Alolan Grimer in play, own turn 5 | 12.9% (12.7-13.2) | 13.1% (12.8-13.4) | 13.0% (12.8-13.2) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 26.1% (25.8-26.5) | 26.5% (26.1-26.9) | 26.3% (26.0-26.6) |
| G3 Alolan Muk in play, own turn 3 | 38.4% (38.0-38.8) | 38.5% (38.1-39.0) | 38.5% (38.2-38.8) |
| G3 Alolan Muk in play, own turn 4 | 48.8% (48.4-49.3) | 49.2% (48.8-49.6) | 49.0% (48.7-49.3) |
| G3 Alolan Muk in play, own turn 5 | 57.7% (57.3-58.2) | 57.8% (57.3-58.2) | 57.8% (57.4-58.1) |
| G3 Glimmet in play, own turn 1 | 81.0% (80.6-81.3) | 81.1% (80.8-81.5) | 81.1% (80.8-81.3) |
| G3 Glimmet in play, own turn 2 | 48.2% (47.8-48.6) | 48.3% (47.9-48.8) | 48.3% (48.0-48.6) |
| G3 Glimmet in play, own turn 3 | 39.0% (38.6-39.4) | 39.0% (38.5-39.4) | 39.0% (38.7-39.3) |
| G3 Glimmet in play, own turn 4 | 29.0% (28.6-29.4) | 28.8% (28.4-29.2) | 28.9% (28.6-29.2) |
| G3 Glimmet in play, own turn 5 | 19.2% (18.9-19.6) | 19.3% (19.0-19.7) | 19.3% (19.0-19.5) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 61.6% (61.2-62.0) | 62.0% (61.6-62.4) | 61.8% (61.5-62.1) |
| G3 Glimmora in play, own turn 3 | 77.1% (76.7-77.5) | 77.4% (77.0-77.7) | 77.2% (77.0-77.5) |
| G3 Glimmora in play, own turn 4 | 87.2% (86.9-87.5) | 87.3% (87.0-87.6) | 87.2% (87.0-87.4) |
| G3 Glimmora in play, own turn 5 | 93.5% (93.3-93.7) | 93.6% (93.4-93.8) | 93.6% (93.4-93.7) |
| G3 Regigigas in play, own turn 1 | 54.2% (53.8-54.7) | 54.2% (53.7-54.6) | 54.2% (53.9-54.5) |
| G3 Regigigas in play, own turn 2 | 64.6% (64.1-65.0) | 64.5% (64.1-64.9) | 64.5% (64.2-64.8) |
| G3 Regigigas in play, own turn 3 | 70.3% (69.9-70.7) | 70.4% (70.0-70.8) | 70.4% (70.1-70.6) |
| G3 Regigigas in play, own turn 4 | 74.0% (73.6-74.4) | 74.2% (73.8-74.5) | 74.1% (73.8-74.4) |
| G3 Regigigas in play, own turn 5 | 76.2% (75.8-76.5) | 76.2% (75.9-76.6) | 76.2% (75.9-76.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 77.7% (77.3-78.0) | 78.0% (77.6-78.3) | 77.8% (77.6-78.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 89.8% (89.5-90.1) | 90.0% (89.7-90.2) | 89.9% (89.7-90.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 95.9% (95.7-96.1) | 96.0% (95.8-96.1) | 95.9% (95.8-96.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.6% (98.5-98.7) | 98.7% (98.6-98.8) | 98.6% (98.6-98.7) |
| G4.s2 a Stage 2 in play, own turn 2 | 10.8% (10.5-11.0) | 10.5% (10.2-10.7) | 10.6% (10.4-10.8) |
| G4.s2 a Stage 2 in play, own turn 3 | 20.7% (20.3-21.1) | 20.7% (20.3-21.0) | 20.7% (20.4-20.9) |
| G4.s2 a Stage 2 in play, own turn 4 | 33.7% (33.3-34.1) | 33.9% (33.4-34.3) | 33.8% (33.5-34.1) |
| G4.s2 a Stage 2 in play, own turn 5 | 49.6% (49.2-50.1) | 49.7% (49.3-50.2) | 49.7% (49.4-50.0) |
| G5.any3 an empty own turn among turns 1-3 | 27.1% (26.7-27.5) | 27.0% (26.7-27.4) | 27.1% (26.8-27.3) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.5% (10.2-10.7) | 5.2% (5.1-5.4) |
| G6 Kingambit with [DD] attached, own turn 3 | 20.7% (20.3-21.1) | 20.7% (20.3-21.0) | 20.7% (20.4-20.9) |
| G6 Kingambit with [DD] attached, own turn 4 | 33.7% (33.3-34.1) | 33.9% (33.4-34.3) | 33.8% (33.5-34.1) |
| G6 Kingambit with [DD] attached, own turn 5 | 49.6% (49.2-50.1) | 49.7% (49.3-50.2) | 49.7% (49.4-50.0) |
| G5 mean empty own turns in turns 1-5 | 0.800 | 0.803 | 0.801 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.1% / 10.5% [1-3] | 1.1% / 5.2% [1-1] |
| K3.by3 | 3.5% / 12.1% [2-5] | 2.9% / 11.2% [2-4] | 3.2% / 11.7% [2-4] |
| K3.by4 | 4.2% / 12.8% [3-6] | 5.6% / 14.0% [4-7] | 4.9% / 13.4% [4-6] |
| K3.by5 | 7.7% / 16.4% [5-11] | 6.3% / 21.2% [5-8] | 7.0% / 18.8% [5-10] |
| K3.by6 | 8.2% / 24.6% [5-12] | 11.2% / 34.0% [6-18] | 9.7% / 29.3% [6-13] |
| K3.by7 | 15.5% / 39.7% [7-25] | 13.2% / 56.4% [7-21] | 14.3% / 48.0% [8-23] |
| K3.by8 | 18.2% / 64.1% [9-29] | 13.2% / 60.3% [7-21] | 15.7% / 62.2% [8-25] |
| K3.never | 35.9% / 81.8% [16-58] | 39.7% / 86.8% [19-61] | 37.8% / 84.3% [17-59] |
| K3.k0 | 4.5% / 50.4% [3-6] | 3.3% / 50.4% [2-5] | 3.9% / 50.4% [2-5] |
| K3.k1 | 0.0% / 45.9% [0-0] | 0.0% / 47.1% [0-0] | 0.0% / 46.5% [0-0] |
| K3.k2 | 8.5% / 54.4% [2-18] | 6.9% / 54.0% [2-14] | 7.7% / 54.2% [2-16] |
| K3.k3p | 5.2% / 51.0% [0-13] | 3.0% / 50.1% [0-7] | 4.1% / 50.6% [0-10] |
| K4 | 13.7% / 61.9% [4-25] | 9.9% / 58.7% [3-18] | 11.8% / 60.3% [3-21] |
| K5 | 6.7% / 61.5% [5-9] | 9.5% / 58.5% [7-12] | 8.1% / 60.0% [6-10] |

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.7% [2-3] | 1.4% [0-2] |
| K3.by3 | 3.1% / 14.4% [2-4] | 3.7% [2-5] | 3.4% / 9.0% [2-4] |
| K3.by4 | 3.6% / 14.9% [2-5] | 5.9% [4-7] | 4.8% / 10.4% [3-6] |
| K3.by5 | 7.5% / 18.8% [4-12] | 7.0% / 33.6% [7-7] | 7.3% / 26.2% [6-10] |
| K3.by6 | 7.9% / 19.2% [5-13] | 7.2% / 33.8% [7-8] | 7.6% / 26.5% [6-10] |
| K3.by7 | 18.2% / 40.4% [7-32] | 14.7% / 72.2% [7-31] | 16.4% / 56.3% [8-27] |
| K3.by8 | 18.2% / 59.3% [7-32] | 14.7% / 81.7% [7-31] | 16.5% / 70.5% [8-28] |
| K3.never | 40.7% / 81.8% [16-67] | 18.3% / 85.3% [1-41] | 29.5% / 83.5% [14-50] |
| K3.k0 | 3.9% / 44.9% [2-6] | 4.4% / 71.3% [2-7] | 4.1% / 58.1% [3-5] |
| K3.k1 | 0.0% / 41.0% [0-0] | 0.0% / 66.9% [0-0] | 0.0% / 54.0% [0-0] |
| K3.k2 | 10.7% / 51.7% [1-24] | 2.9% / 69.8% [0-5] | 6.8% / 60.8% [2-15] |
| K3.k3p | 3.6% / 44.7% [0-11] | 7.5% / 74.4% [0-23] | 5.6% / 59.6% [0-13] |
| K4 | 14.3% / 56.9% [2-29] | 10.3% / 81.0% [0-27] | 12.3% / 68.9% [3-23] |
| K5 | 6.9% / 53.5% [4-10] | 9.6% / 82.3% [6-12] | 8.3% / 67.9% [6-10] |

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [2-3] | 1.2% [1-1] |
| K3.by3 | 3.6% [3-4] | 3.1% [3-4] | 3.4% [3-4] |
| K3.by4 | 4.6% [4-5] | 4.8% [4-5] | 4.7% [4-5] |
| K3.by5 | 7.0% [6-8] | 8.1% [7-10] | 7.5% [7-9] |
| K3.by6 | 11.5% [9-15] | 10.5% / 14.4% [8-13] | 11.0% / 13.0% [9-13] |
| K3.by7 | 14.6% / 18.8% [11-18] | 12.1% / 21.0% [10-15] | 13.4% / 19.9% [11-16] |
| K3.by8 | 16.5% / 26.0% [13-21] | 13.2% / 23.4% [10-16] | 14.8% / 24.7% [12-18] |
| K3.never | 74.0% / 83.5% [66-81] | 76.6% / 86.8% [70-83] | 75.3% / 85.2% [68-81] |
| K3.k0 | 4.9% / 14.4% [4-6] | 3.3% / 13.6% [3-4] | 4.1% / 14.0% [4-5] |
| K3.k1 | 0.0% / 9.5% [0-0] | 0.0% / 10.3% [0-0] | 0.0% / 9.9% [0-0] |
| K3.k2 | 6.2% / 15.7% [4-9] | 5.1% / 15.4% [4-7] | 5.7% / 15.6% [4-8] |
| K3.k3p | 5.4% / 14.9% [3-9] | 4.7% / 15.0% [3-7] | 5.0% / 14.9% [3-8] |
| K4 | 11.6% / 21.8% [8-16] | 9.8% / 20.6% [7-13] | 10.7% / 21.2% [8-14] |
| K5 | 8.0% / 21.2% [7-9] | 12.0% / 23.3% [11-13] | 10.0% / 22.3% [9-11] |

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 3.6% [3-4, Wilson] | 1.8% [2-2, Wilson] |
| K3.by4 | 4.5% [4-5, Wilson] | 7.6% [7-8, Wilson] | 6.1% [6-6, Wilson] |
| K3.by5 | 16.4% [16-17, Wilson] | 8.3% [8-9, Wilson] | 12.4% [12-13, Wilson] |
| K3.by6 | 18.9% [18-20, Wilson] | 8.3% [8-9, Wilson] | 13.6% [13-14, Wilson] |
| K3.by7 | 18.9% [18-20, Wilson] | 8.3% [8-9, Wilson] | 13.6% [13-14, Wilson] |
| K3.by8 | 18.9% [18-20, Wilson] | 8.3% [8-9, Wilson] | 13.6% [13-14, Wilson] |
| K3.never | 81.1% [80-82, Wilson] | 91.7% [91-92, Wilson] | 86.4% [86-87, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.5% [4-5, Wilson] | 3.6% [3-4, Wilson] | 4.0% [4-4, Wilson] |
| K3.k3p | 14.4% [14-15, Wilson] | 4.7% [4-5, Wilson] | 9.6% [9-10, Wilson] |
| K4 | 18.9% [18-20, Wilson] | 8.3% [8-9, Wilson] | 13.6% [13-14, Wilson] |
| K5 | 19.2% [18-20, Wilson] | 24.8% [24-26, Wilson] | 22.0% [21-23, Wilson] |

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.8% [2-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.3% [4-5, Wilson] | 2.8% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.by4 | 4.3% [4-5, Wilson] | 7.0% [6-7, Wilson] | 5.6% [5-6, Wilson] |
| K3.by5 | 8.3% [8-9, Wilson] | 19.4% [19-20, Wilson] | 13.9% [13-14, Wilson] |
| K3.by6 | 31.4% [31-32, Wilson] | 21.9% [21-23, Wilson] | 26.6% [26-27, Wilson] |
| K3.by7 | 34.6% [34-36, Wilson] | 21.9% [21-23, Wilson] | 28.2% [28-29, Wilson] |
| K3.by8 | 34.6% [34-36, Wilson] | 21.9% [21-23, Wilson] | 28.2% [28-29, Wilson] |
| K3.never | 65.4% [64-66, Wilson] | 78.2% [77-79, Wilson] | 71.8% [71-72, Wilson] |
| K3.k0 | 4.3% [4-5, Wilson] | 2.8% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.0% [4-4, Wilson] | 4.2% [4-5, Wilson] | 4.1% [4-4, Wilson] |
| K3.k3p | 26.2% [25-27, Wilson] | 14.9% [14-16, Wilson] | 20.6% [20-21, Wilson] |
| K4 | 30.3% [29-31, Wilson] | 19.1% [18-20, Wilson] | 24.7% [24-25, Wilson] |
| K5 | 14.1% [13-15, Wilson] | 20.1% [19-21, Wilson] | 17.1% [17-18, Wilson] |

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.8% [2-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.3% [4-5, Wilson] | 2.8% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.by4 | 4.3% [4-5, Wilson] | 2.8% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.by5 | 4.3% [4-5, Wilson] | 8.1% [8-9, Wilson] | 6.2% [6-7, Wilson] |
| K3.by6 | 9.0% [8-10, Wilson] | 8.6% [8-9, Wilson] | 8.8% [8-9, Wilson] |
| K3.by7 | 9.3% [9-10, Wilson] | 30.7% [30-32, Wilson] | 20.0% [19-21, Wilson] |
| K3.by8 | 40.9% [40-42, Wilson] | 31.0% [30-32, Wilson] | 36.0% [35-37, Wilson] |
| K3.never | 59.1% [58-60, Wilson] | 69.0% [68-70, Wilson] | 64.0% [63-65, Wilson] |
| K3.k0 | 4.3% [4-5, Wilson] | 2.8% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 5.0% [5-5, Wilson] | 5.8% [5-6, Wilson] | 5.4% [5-6, Wilson] |
| K3.k3p | 31.7% [31-33, Wilson] | 22.4% [22-23, Wilson] | 27.0% [26-28, Wilson] |
| K4 | 36.6% [36-38, Wilson] | 28.2% [27-29, Wilson] | 32.4% [32-33, Wilson] |
| K5 | 8.7% [8-9, Wilson] | 12.2% [12-13, Wilson] | 10.4% [10-11, Wilson] |

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 3.6% [3-4, Wilson] | 1.8% [2-2, Wilson] |
| K3.by4 | 4.5% [4-5, Wilson] | 6.8% [6-7, Wilson] | 5.6% [5-6, Wilson] |
| K3.by5 | 13.3% [13-14, Wilson] | 7.7% [7-8, Wilson] | 10.5% [10-11, Wilson] |
| K3.by6 | 16.7% [16-17, Wilson] | 7.7% [7-8, Wilson] | 12.2% [12-13, Wilson] |
| K3.by7 | 16.7% [16-17, Wilson] | 7.7% [7-8, Wilson] | 12.2% [12-13, Wilson] |
| K3.by8 | 16.7% [16-17, Wilson] | 7.7% [7-8, Wilson] | 12.2% [12-13, Wilson] |
| K3.never | 83.3% [83-84, Wilson] | 92.3% [92-93, Wilson] | 87.8% [87-88, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.5% [4-5, Wilson] | 3.6% [3-4, Wilson] | 4.0% [4-4, Wilson] |
| K3.k3p | 12.2% [12-13, Wilson] | 4.0% [4-4, Wilson] | 8.1% [8-9, Wilson] |
| K4 | 16.7% [16-17, Wilson] | 7.7% [7-8, Wilson] | 12.2% [12-13, Wilson] |
| K5 | 19.2% [18-20, Wilson] | 24.8% [24-26, Wilson] | 22.0% [21-23, Wilson] |

**Plain summary, base.**

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## deck01 (card-list id 35d98d0dcaf2)

Changes: decks/dustin/01-muk-glimmora-kingambit-regigigas.txt

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

Plan lines under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 50.1% / 76.3% [38-63] | 36.4% / 72.8% [23-50] | 43.3% / 74.5% [31-56] |
| P2 both Glimmora had their turn | 4.3% / 53.1% [1-10] | 3.0% / 56.5% [0-7] | 3.6% / 54.8% [1-8] |
| P2 the first Glimmora placed had its turn | 40.2% / 72.3% [28-52] | 27.5% / 70.5% [13-43] | 33.9% / 71.4% [22-47] |
| P2 the second Glimmora placed had its turn | 14.2% / 57.1% [5-25] | 11.9% / 58.8% [5-19] | 13.1% / 57.9% [5-22] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 34.0% / 66.6% [30-38] | 34.7% / 69.7% [29-40] | 34.4% / 68.1% [29-39] |
| P3, cause: the opening (still the starting Active) | 23.1% / 60.8% [22-25] | 20.1% / 63.4% [17-23] | 21.6% / 62.1% [20-24] |
| P3, cause: promoted, nothing else left | 10.9% / 55.3% [6-16] | 14.6% / 60.5% [9-21] | 12.7% / 57.9% [7-18] |
| P4 ready at the winning moment: Knocks out their strongest | 20.2% / 45.4% [7-34] | 13.9% / 42.0% [4-25] | 17.1% / 43.7% [5-29] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 3.3% / 28.6% [0-10] | 2.1% / 30.2% [0-6] | 2.7% / 29.4% [0-8] |
| P4 not ready, ready 1 turn late | 6.2% / 41.4% [0-17] | 5.7% / 46.4% [0-15] | 5.9% / 43.9% [0-16] |
| P4 not ready, ready 2 or more turns late | 0.8% / 36.0% [0-2] | 1.1% / 41.7% [0-3] | 0.9% / 38.9% [0-3] |
| P4 the moment came and Kingambit was never ready in the deal | 7.2% / 42.4% [0-17] | 7.2% / 47.9% [0-19] | 7.2% / 45.1% [0-18] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 30.5% / 55.8% [10-55] | 31.4% / 59.5% [13-54] | 30.9% / 57.6% [12-54] |
| P5 plan reached in time: Knocks out their strongest | 27.1% / 62.4% [12-44] | 20.7% / 61.4% [8-35] | 23.9% / 61.9% [10-40] |
| P5 plan reached in time: Wins outright (a lower bound) | 3.3% / 38.6% [0-10] | 2.4% / 43.0% [0-7] | 2.8% / 40.8% [0-9] |

Flagged differences from the base under C-his (pooled; bootstrap range over the recorded games, undecided counted as no): P2.any: +1.6 points (+0.5 to +2.7); P3.promo: -1.5 points (-2.4 to -0.6); P4.ko: +1.9 points (+0.6 to +3.2); P5.ko: +2.3 points (+1.0 to +3.8).

Plan lines under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent's board): 210-HP Mega ex, 3 points in 2 game(s), 190-HP Mega ex, 3 points in 2 game(s), 180-HP Mega ex, 3 points in 2 game(s), 140-HP ex, 2 points in 2 game(s), 130-HP ex, 2 points in 1 game(s), 120-HP ex, 2 points in 1 game(s), 100-HP non-ex, 1 point in 1 game(s), 70-HP non-ex, 1 point in 1 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 52.6% / 75.3% [35-69] | 31.1% / 86.0% [0-53] | 41.9% / 80.6% [26-58] |
| P2 both Glimmora had their turn | 5.3% / 48.6% [1-12] | 0.7% / 80.6% [0-2] | 3.0% / 64.6% [1-7] |
| P2 the first Glimmora placed had its turn | 39.9% / 70.6% [24-58] | 28.2% / 85.1% [0-52] | 34.1% / 77.8% [20-48] |
| P2 the second Glimmora placed had its turn | 18.1% / 53.3% [7-31] | 3.5% / 81.5% [0-9] | 10.8% / 67.4% [4-22] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 33.2% / 63.0% [27-39] | 40.1% / 89.0% [27-49] | 36.6% / 76.0% [30-42] |
| P3, cause: the opening (still the starting Active) | 22.8% / 56.7% [21-24] | 22.5% / 85.0% [20-24] | 22.6% / 70.9% [21-24] |
| P3, cause: promoted, nothing else left | 10.4% / 50.4% [5-17] | 17.6% / 84.6% [3-26] | 14.0% / 67.5% [7-20] |
| P4 ready at the winning moment: Knocks out their strongest | 21.8% / 43.9% [5-40] | 8.2% / 60.3% [0-24] | 15.0% / 52.1% [4-28] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 5.0% / 27.1% [0-15] | 0.0% / 52.1% [0-0] | 2.5% / 39.6% [0-10] |
| P4 not ready, ready 1 turn late | 8.8% / 38.2% [0-25] | 0.0% / 72.4% [0-0] | 4.4% / 55.3% [0-14] |
| P4 not ready, ready 2 or more turns late | 1.1% / 30.5% [0-3] | 0.0% / 72.4% [0-0] | 0.5% / 51.4% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 10.1% / 39.5% [0-24] | 0.0% / 72.4% [0-0] | 5.1% / 56.0% [0-13] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 28.8% / 50.8% [7-57] | 19.4% / 71.6% [1-42] | 24.1% / 61.2% [9-44] |
| P5 plan reached in time: Knocks out their strongest | 31.7% / 61.1% [12-52] | 8.2% / 80.6% [0-24] | 19.9% / 70.8% [8-37] |
| P5 plan reached in time: Wins outright (a lower bound) | 5.1% / 34.5% [0-16] | 0.0% / 72.4% [0-0] | 2.6% / 53.5% [0-10] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap range over the recorded games, undecided counted as no): P2.any: +1.2 points (+0.1 to +2.4); P3.promo: -1.2 points (-2.4 to -0.4); P4.ko: +1.2 points (+0.3 to +2.5); P5.ko: +1.3 points (+0.4 to +2.6).

Plan lines under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon (FLAGGED: the logs do not show the opponent's HP, so this is the biggest Pokémon in the panel list of that game): 210-HP Mega ex, 3 points in 16 game(s), 190-HP Mega ex, 3 points in 16 game(s), 170-HP Mega ex, 3 points in 8 game(s), 150-HP ex, 2 points in 8 game(s), 140-HP ex, 2 points in 16 game(s).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 46.4% / 52.3% [42-51] | 31.2% / 39.6% [26-36] | 38.8% / 46.0% [35-43] |
| P2 both Glimmora had their turn | 3.4% / 14.9% [2-6] | 1.9% / 14.2% [1-3] | 2.7% / 14.6% [1-4] |
| P2 the first Glimmora placed had its turn | 38.6% / 46.0% [35-42] | 22.9% / 32.8% [19-27] | 30.7% / 39.4% [27-34] |
| P2 the second Glimmora placed had its turn | 11.2% / 21.2% [7-16] | 10.2% / 21.1% [7-14] | 10.7% / 21.2% [7-15] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 41.2% / 48.4% [38-44] | 43.6% / 50.2% [41-47] | 42.4% / 49.3% [40-45] |
| P3, cause: the opening (still the starting Active) | 23.4% / 32.2% [22-24] | 21.0% / 30.6% [20-22] | 22.2% / 31.4% [21-23] |
| P3, cause: promoted, nothing else left | 17.8% / 27.9% [15-21] | 22.6% / 32.1% [20-25] | 20.2% / 30.0% [17-23] |
| P4 ready at the winning moment: Knocks out their strongest | 13.7% / 19.7% [8-20] | 10.8% / 17.9% [6-16] | 12.2% / 18.8% [7-18] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.4% / 6.4% [0-1] | 0.7% / 7.8% [0-2] | 0.5% / 7.1% [0-1] |
| P4 not ready, ready 1 turn late | 2.6% / 10.1% [1-4] | 2.6% / 11.5% [1-4] | 2.6% / 10.8% [1-4] |
| P4 not ready, ready 2 or more turns late | 0.9% / 8.4% [0-1] | 1.2% / 10.0% [0-2] | 1.0% / 9.2% [0-2] |
| P4 the moment came and Kingambit was never ready in the deal | 5.6% / 13.1% [3-9] | 6.8% / 15.6% [3-11] | 6.2% / 14.4% [3-10] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 69.8% / 75.8% [58-81] | 69.8% / 76.8% [60-80] | 69.8% / 76.3% [59-80] |
| P5 plan reached in time: Knocks out their strongest | 17.1% / 24.6% [10-25] | 14.6% / 23.5% [9-21] | 15.8% / 24.1% [9-23] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.5% / 8.0% [0-1] | 0.8% / 9.6% [0-2] | 0.6% / 8.8% [0-2] |

Flagged differences from the base under C-bot (pooled; bootstrap range over the recorded games, undecided counted as no): P3: -1.7 points (-2.6 to -0.7); P3.promo: -2.1 points (-2.8 to -1.3); P4.ko: +1.6 points (+0.8 to +2.5); P4.never: -1.1 points (-1.8 to -0.5); P5.ko: +1.7 points (+0.8 to +2.7).

Plan lines under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 180-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 180, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 both Glimmora had their turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the first Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the second Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 57.6% [57-59, Wilson] | 46.6% [46-48, Wilson] | 52.1% [51-53, Wilson] |
| P3, cause: the opening (still the starting Active) | 20.7% [20-22, Wilson] | 12.6% [12-13, Wilson] | 16.7% [16-17, Wilson] |
| P3, cause: promoted, nothing else left | 36.8% [36-38, Wilson] | 34.0% [33-35, Wilson] | 35.4% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 23.5% [23-24, Wilson] | 9.0% [8-10, Wilson] | 16.2% [16-17, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 23.5% [23-24, Wilson] | 9.0% [8-10, Wilson] | 16.2% [16-17, Wilson] |
| P4 not ready, ready 1 turn late | 1.3% [1-2, Wilson] | 0.5% [0-1, Wilson] | 0.9% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 17.9% [17-19, Wilson] | 14.8% [14-15, Wilson] | 16.4% [16-17, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 57.2% [56-58, Wilson] | 75.8% [75-77, Wilson] | 66.5% [66-67, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 24.8% [24-26, Wilson] | 9.4% [9-10, Wilson] | 17.1% [17-18, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 24.8% [24-26, Wilson] | 9.4% [9-10, Wilson] | 17.1% [17-18, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; bootstrap range over the recorded games, undecided counted as no): P4.ko: +4.3 points (+3.6 to +4.9); P4.win: +4.3 points (+3.6 to +4.9); P4.never: -1.3 points (-2.0 to -0.6); P4.nomoment: -3.2 points (-3.9 to -2.4); P5.ko: +4.5 points (+3.9 to +5.2); P5.win: +4.5 points (+3.9 to +5.2).

Plan lines under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 150-HP ex, 2 points (the Blade needs 60 + 40k >= 150, k = 3).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 32.6% [32-34, Wilson] | 0.0% [0-0, Wilson] | 16.3% [16-17, Wilson] |
| P2 both Glimmora had their turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the first Glimmora placed had its turn | 32.6% [32-34, Wilson] | 0.0% [0-0, Wilson] | 16.3% [16-17, Wilson] |
| P2 the second Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 56.9% [56-58, Wilson] | 58.7% [58-60, Wilson] | 57.8% [57-58, Wilson] |
| P3, cause: the opening (still the starting Active) | 22.7% [22-24, Wilson] | 21.1% [20-22, Wilson] | 21.9% [21-22, Wilson] |
| P3, cause: promoted, nothing else left | 34.2% [33-35, Wilson] | 37.5% [37-38, Wilson] | 35.9% [35-37, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 35.5% [35-36, Wilson] | 23.5% [23-24, Wilson] | 29.5% [29-30, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 1.0% [1-1, Wilson] | 1.6% [1-2, Wilson] | 1.3% [1-1, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 17.4% [17-18, Wilson] | 18.5% [18-19, Wilson] | 17.9% [17-18, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 46.0% [45-47, Wilson] | 56.5% [56-57, Wilson] | 51.3% [51-52, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 36.6% [36-38, Wilson] | 25.1% [24-26, Wilson] | 30.8% [30-31, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; bootstrap range over the recorded games, undecided counted as no): P3.promo: -1.0 points (-1.9 to -0.1); P4.ko: +5.7 points (+4.9 to +6.4); P4.never: -2.4 points (-3.1 to -1.6); P4.nomoment: -3.3 points (-4.0 to -2.5); P5.ko: +5.6 points (+4.8 to +6.4).

Plan lines under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 220-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 220, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 82.5% [82-83, Wilson] | 55.0% [54-56, Wilson] | 68.8% [68-69, Wilson] |
| P2 both Glimmora had their turn | 16.4% [16-17, Wilson] | 10.3% [10-11, Wilson] | 13.3% [13-14, Wilson] |
| P2 the first Glimmora placed had its turn | 52.1% [51-53, Wilson] | 21.0% [20-22, Wilson] | 36.5% [36-37, Wilson] |
| P2 the second Glimmora placed had its turn | 46.9% [46-48, Wilson] | 44.3% [43-45, Wilson] | 45.6% [45-46, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 34.5% [34-35, Wilson] | 39.9% [39-41, Wilson] | 37.2% [37-38, Wilson] |
| P3, cause: the opening (still the starting Active) | 22.7% [22-24, Wilson] | 21.1% [20-22, Wilson] | 21.9% [21-22, Wilson] |
| P3, cause: promoted, nothing else left | 11.8% [11-12, Wilson] | 18.8% [18-20, Wilson] | 15.3% [15-16, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] | 100.0% [100-100, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; bootstrap range over the recorded games, undecided counted as no): P2.any: +3.5 points (+2.7 to +4.4); P2.g2: +4.5 points (+3.5 to +5.4); P3: -3.5 points (-4.4 to -2.5); P3.promo: -3.8 points (-4.5 to -3.1).

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

Strongest Pokémon assumed for this pace: a 190-HP Mega ex, 3 points (the Blade needs 60 + 40k >= 190, k = 4).

P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero (their Pokémon's points at least 3). Any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not modelled, so "wins outright" is a lower bound.

| Measure | going first | going second | pooled |
|---|---|---|---|
| P2 at least one Glimmora had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 both Glimmora had their turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the first Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P2 the second Glimmora placed had its turn | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P3 plan broken in front: Muk or Pawniard Active at any point | 57.6% [57-59, Wilson] | 46.6% [46-48, Wilson] | 52.1% [51-53, Wilson] |
| P3, cause: the opening (still the starting Active) | 20.7% [20-22, Wilson] | 12.6% [12-13, Wilson] | 16.7% [16-17, Wilson] |
| P3, cause: promoted, nothing else left | 36.8% [36-38, Wilson] | 34.0% [33-35, Wilson] | 35.4% [35-36, Wilson] |
| P4 ready at the winning moment: Knocks out their strongest | 4.5% [4-5, Wilson] | 1.3% [1-2, Wilson] | 2.9% [3-3, Wilson] |
| P4 ready at the winning moment: Wins outright (a lower bound) | 4.5% [4-5, Wilson] | 1.3% [1-2, Wilson] | 2.9% [3-3, Wilson] |
| P4 not ready, ready 1 turn late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 not ready, ready 2 or more turns late | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| P4 the moment came and Kingambit was never ready in the deal | 5.2% [5-6, Wilson] | 1.7% [2-2, Wilson] | 3.5% [3-4, Wilson] |
| P4 the winning moment never came in the deal (the Blade never reaches their strongest) | 90.3% [90-91, Wilson] | 96.9% [97-97, Wilson] | 93.6% [93-94, Wilson] |
| P5 plan reached in time: Knocks out their strongest | 4.5% [4-5, Wilson] | 1.3% [1-2, Wilson] | 2.9% [3-3, Wilson] |
| P5 plan reached in time: Wins outright (a lower bound) | 4.5% [4-5, Wilson] | 1.3% [1-2, Wilson] | 2.9% [3-3, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; bootstrap range over the recorded games, undecided counted as no): P4.nomoment: -1.6 points (-2.0 to -1.2).

#### descriptive (speed is not the goal)

The old G and K lines, kept for reference. Kingambit's speed is not the yardstick for this deck.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 29.2% (28.8-29.6) | 28.8% (28.4-29.2) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 56.2% (55.7-56.6) | 55.7% (55.3-56.2) | 55.9% (55.6-56.3) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 70.2% (69.8-70.6) | 70.0% (69.6-70.4) | 70.1% (69.8-70.4) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 79.7% (79.3-80.0) | 79.5% (79.2-79.9) | 79.6% (79.3-79.8) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 86.9% (86.6-87.2) | 87.0% (86.7-87.3) | 87.0% (86.8-87.2) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 92.4% (92.2-92.6) | 92.4% (92.2-92.6) | 92.4% (92.2-92.6) |
| K2 Kingambit in play, own turn 2 | 11.7% (11.4-11.9) | 11.4% (11.1-11.7) | 11.5% (11.3-11.7) |
| K2 Kingambit in play, own turn 3 | 23.9% (23.5-24.2) | 23.5% (23.1-23.9) | 23.7% (23.4-24.0) |
| K2 Kingambit in play, own turn 4 | 39.5% (39.1-40.0) | 39.1% (38.7-39.5) | 39.3% (39.0-39.6) |
| K2 Kingambit in play, own turn 5 | 56.6% (56.1-57.0) | 56.3% (55.9-56.8) | 56.4% (56.1-56.7) |
| K2 Kingambit in play, own turn 6 | 72.7% (72.3-73.1) | 72.5% (72.1-72.9) | 72.6% (72.3-72.9) |
| K6 Muk and Regigigas both in play, own turn 3 | 26.6% (26.2-27.0) | 26.6% (26.2-27.0) | 26.6% (26.3-26.9) |
| K6 Muk and Regigigas both in play, own turn 4 | 35.1% (34.7-35.5) | 35.0% (34.6-35.5) | 35.1% (34.8-35.4) |
| K6 Muk and Regigigas both in play, own turn 5 | 41.3% (40.9-41.8) | 41.3% (40.9-41.8) | 41.3% (41.0-41.6) |
| G3 Pawniard in play, own turn 1 | 56.2% (55.7-56.6) | 55.7% (55.3-56.2) | 55.9% (55.6-56.3) |
| G3 Pawniard in play, own turn 2 | 58.6% (58.2-59.0) | 58.6% (58.2-59.0) | 58.6% (58.3-58.9) |
| G3 Pawniard in play, own turn 3 | 55.8% (55.3-56.2) | 56.0% (55.6-56.4) | 55.9% (55.6-56.2) |
| G3 Pawniard in play, own turn 4 | 47.4% (47.0-47.8) | 47.9% (47.5-48.3) | 47.6% (47.3-48.0) |
| G3 Pawniard in play, own turn 5 | 35.8% (35.4-36.3) | 36.1% (35.7-36.5) | 36.0% (35.7-36.3) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 11.7% (11.4-11.9) | 11.4% (11.1-11.7) | 11.5% (11.3-11.7) |
| G3 Kingambit in play, own turn 3 | 23.9% (23.5-24.2) | 23.5% (23.1-23.9) | 23.7% (23.4-24.0) |
| G3 Kingambit in play, own turn 4 | 39.5% (39.1-40.0) | 39.1% (38.7-39.5) | 39.3% (39.0-39.6) |
| G3 Kingambit in play, own turn 5 | 56.6% (56.1-57.0) | 56.3% (55.9-56.8) | 56.4% (56.1-56.7) |
| G3 Alolan Grimer in play, own turn 1 | 52.6% (52.2-53.1) | 52.7% (52.2-53.1) | 52.7% (52.3-53.0) |
| G3 Alolan Grimer in play, own turn 2 | 33.7% (33.3-34.1) | 33.8% (33.4-34.2) | 33.7% (33.4-34.0) |
| G3 Alolan Grimer in play, own turn 3 | 24.8% (24.4-25.2) | 25.1% (24.7-25.5) | 24.9% (24.7-25.2) |
| G3 Alolan Grimer in play, own turn 4 | 16.5% (16.2-16.8) | 17.0% (16.6-17.3) | 16.7% (16.5-17.0) |
| G3 Alolan Grimer in play, own turn 5 | 9.9% (9.7-10.2) | 10.2% (9.9-10.5) | 10.1% (9.9-10.2) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 28.0% (27.6-28.3) | 28.0% (27.6-28.4) | 28.0% (27.7-28.2) |
| G3 Alolan Muk in play, own turn 3 | 41.6% (41.2-42.1) | 41.7% (41.2-42.1) | 41.7% (41.3-42.0) |
| G3 Alolan Muk in play, own turn 4 | 52.7% (52.3-53.1) | 52.6% (52.2-53.0) | 52.6% (52.3-53.0) |
| G3 Alolan Muk in play, own turn 5 | 60.8% (60.3-61.2) | 60.8% (60.4-61.2) | 60.8% (60.5-61.1) |
| G3 Glimmet in play, own turn 1 | 81.4% (81.1-81.7) | 81.5% (81.2-81.9) | 81.5% (81.2-81.7) |
| G3 Glimmet in play, own turn 2 | 47.8% (47.4-48.3) | 48.0% (47.6-48.5) | 47.9% (47.6-48.2) |
| G3 Glimmet in play, own turn 3 | 35.6% (35.2-36.1) | 35.5% (35.1-35.9) | 35.6% (35.3-35.9) |
| G3 Glimmet in play, own turn 4 | 24.3% (23.9-24.7) | 24.0% (23.6-24.4) | 24.1% (23.9-24.4) |
| G3 Glimmet in play, own turn 5 | 14.6% (14.3-14.9) | 14.8% (14.5-15.1) | 14.7% (14.5-14.9) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 64.6% (64.2-65.0) | 64.4% (64.0-64.8) | 64.5% (64.2-64.8) |
| G3 Glimmora in play, own turn 3 | 80.5% (80.2-80.9) | 80.6% (80.3-81.0) | 80.6% (80.3-80.8) |
| G3 Glimmora in play, own turn 4 | 90.0% (89.7-90.2) | 89.9% (89.6-90.1) | 89.9% (89.7-90.1) |
| G3 Glimmora in play, own turn 5 | 95.3% (95.1-95.5) | 95.2% (95.0-95.4) | 95.2% (95.1-95.4) |
| G3 Regigigas in play, own turn 1 | 54.7% (54.3-55.2) | 54.4% (54.0-54.8) | 54.6% (54.3-54.9) |
| G3 Regigigas in play, own turn 2 | 66.3% (65.8-66.7) | 65.8% (65.4-66.2) | 66.0% (65.7-66.3) |
| G3 Regigigas in play, own turn 3 | 72.2% (71.8-72.6) | 71.9% (71.5-72.3) | 72.1% (71.8-72.3) |
| G3 Regigigas in play, own turn 4 | 75.4% (75.0-75.8) | 75.2% (74.8-75.6) | 75.3% (75.0-75.6) |
| G3 Regigigas in play, own turn 5 | 77.1% (76.8-77.5) | 76.8% (76.5-77.2) | 77.0% (76.7-77.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 79.9% (79.6-80.3) | 79.7% (79.3-80.1) | 79.8% (79.6-80.1) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 91.3% (91.1-91.6) | 91.4% (91.2-91.7) | 91.4% (91.2-91.5) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 96.6% (96.4-96.7) | 96.7% (96.5-96.8) | 96.6% (96.5-96.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.9% (98.8-99.0) | 98.9% (98.8-99.0) | 98.9% (98.8-98.9) |
| G4.s2 a Stage 2 in play, own turn 2 | 11.7% (11.4-11.9) | 11.4% (11.1-11.7) | 11.5% (11.3-11.7) |
| G4.s2 a Stage 2 in play, own turn 3 | 23.9% (23.5-24.2) | 23.5% (23.1-23.9) | 23.7% (23.4-24.0) |
| G4.s2 a Stage 2 in play, own turn 4 | 39.5% (39.1-40.0) | 39.1% (38.7-39.5) | 39.3% (39.0-39.6) |
| G4.s2 a Stage 2 in play, own turn 5 | 56.6% (56.1-57.0) | 56.3% (55.9-56.8) | 56.4% (56.1-56.7) |
| G5.any3 an empty own turn among turns 1-3 | 23.0% (22.6-23.4) | 23.1% (22.7-23.5) | 23.1% (22.8-23.3) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 11.4% (11.1-11.7) | 5.7% (5.6-5.8) |
| G6 Kingambit with [DD] attached, own turn 3 | 23.9% (23.5-24.2) | 23.5% (23.1-23.9) | 23.7% (23.4-24.0) |
| G6 Kingambit with [DD] attached, own turn 4 | 39.5% (39.1-40.0) | 39.1% (38.7-39.5) | 39.3% (39.0-39.6) |
| G6 Kingambit with [DD] attached, own turn 5 | 56.6% (56.1-57.0) | 56.3% (55.9-56.8) | 56.4% (56.1-56.7) |
| G5 mean empty own turns in turns 1-5 | 0.776 | 0.777 | 0.777 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.1% / 10.4% [1-3] | 1.0% / 5.2% [1-1] |
| K3.by3 | 3.7% / 12.3% [2-5] | 2.8% / 11.2% [2-4] | 3.3% / 11.8% [2-4] |
| K3.by4 | 4.5% / 13.1% [3-6] | 5.8% / 14.1% [4-8] | 5.1% / 13.6% [4-6] |
| K3.by5 | 8.0% / 16.6% [5-12] | 6.5% / 21.6% [5-8] | 7.2% / 19.1% [5-10] |
| K3.by6 | 8.5% / 24.8% [6-12] | 12.2% / 35.1% [6-20] | 10.4% / 30.0% [7-14] |
| K3.by7 | 17.0% / 41.1% [8-28] | 14.2% / 57.8% [7-23] | 15.6% / 49.4% [8-25] |
| K3.by8 | 20.2% / 66.0% [9-33] | 14.2% / 61.4% [7-23] | 17.2% / 63.7% [8-28] |
| K3.never | 34.0% / 79.8% [15-56] | 38.6% / 85.8% [18-60] | 36.3% / 82.8% [16-58] |
| K3.k0 | 4.9% / 50.7% [3-7] | 3.3% / 50.5% [2-5] | 4.1% / 50.6% [3-6] |
| K3.k1 | 0.0% / 45.8% [0-0] | 0.0% / 47.2% [0-0] | 0.0% / 46.5% [0-0] |
| K3.k2 | 9.0% / 54.9% [2-19] | 7.3% / 54.5% [2-15] | 8.2% / 54.7% [2-17] |
| K3.k3p | 6.2% / 52.0% [0-16] | 3.6% / 50.8% [0-9] | 4.9% / 51.4% [0-12] |
| K4 | 15.2% / 63.6% [4-28] | 10.9% / 59.8% [3-20] | 13.1% / 61.7% [3-24] |
| K5 | 6.9% / 62.1% [5-9] | 9.2% / 59.2% [7-12] | 8.1% / 60.6% [6-10] |

Flagged differences from the base under C-his (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by7: +1.3 points (+0.1 to +2.6); K3.by8: +1.5 points (+0.3 to +2.8); K3.never: -1.5 points (-2.7 to -0.4); K4: +1.3 points (+0.1 to +2.7).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.9% [3-3] | 1.4% [0-2] |
| K3.by3 | 3.4% / 14.7% [2-5] | 3.9% [3-5] | 3.6% / 9.3% [3-5] |
| K3.by4 | 3.9% / 15.2% [2-6] | 6.1% [4-7] | 5.0% / 10.7% [3-6] |
| K3.by5 | 7.7% / 19.0% [4-12] | 7.5% / 33.6% [7-8] | 7.6% / 26.3% [6-10] |
| K3.by6 | 8.2% / 19.5% [5-13] | 7.7% / 33.9% [7-9] | 8.0% / 26.7% [6-10] |
| K3.by7 | 19.6% / 41.8% [7-35] | 16.2% / 73.2% [7-35] | 17.9% / 57.5% [8-30] |
| K3.by8 | 19.6% / 60.8% [7-35] | 16.2% / 82.3% [7-35] | 17.9% / 71.5% [8-30] |
| K3.never | 39.2% / 80.4% [15-66] | 17.7% / 83.8% [1-38] | 28.5% / 82.1% [14-48] |
| K3.k0 | 4.4% / 45.5% [2-7] | 4.6% / 70.6% [3-7] | 4.5% / 58.1% [3-6] |
| K3.k1 | 0.0% / 41.2% [0-0] | 0.0% / 66.0% [0-0] | 0.0% / 53.6% [0-0] |
| K3.k2 | 10.8% / 51.9% [1-25] | 3.2% / 69.2% [0-5] | 7.0% / 60.5% [2-15] |
| K3.k3p | 4.5% / 45.7% [0-14] | 8.5% / 74.5% [0-26] | 6.5% / 60.1% [0-15] |
| K4 | 15.3% / 58.4% [1-31] | 11.7% / 81.6% [0-31] | 13.5% / 70.0% [3-26] |
| K5 | 7.4% / 54.5% [5-10] | 8.8% / 82.8% [6-11] | 8.1% / 68.7% [6-10] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by7: +1.5 points (+0.3 to +2.9); K3.by8: +1.5 points (+0.3 to +2.8).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% [2-3] | 1.2% [1-1] |
| K3.by3 | 3.9% [3-4] | 3.2% [3-4] | 3.5% [3-4] |
| K3.by4 | 4.9% [4-6] | 5.2% [4-6] | 5.1% [5-6] |
| K3.by5 | 7.3% [6-9] | 9.2% [7-12] | 8.2% [7-10] |
| K3.by6 | 12.4% [9-16] | 11.8% / 15.6% [9-14] | 12.1% / 14.0% [9-15] |
| K3.by7 | 15.4% / 19.5% [11-19] | 13.8% / 22.5% [11-18] | 14.6% / 21.0% [11-18] |
| K3.by8 | 17.4% / 26.7% [13-22] | 14.8% / 24.8% [11-18] | 16.1% / 25.8% [12-20] |
| K3.never | 73.3% / 82.6% [65-80] | 75.2% / 85.2% [68-81] | 74.2% / 83.9% [67-81] |
| K3.k0 | 5.2% / 14.5% [4-6] | 3.5% / 13.5% [3-4] | 4.3% / 14.0% [4-5] |
| K3.k1 | 0.0% / 9.3% [0-0] | 0.0% / 10.0% [0-0] | 0.0% / 9.7% [0-0] |
| K3.k2 | 6.7% / 16.0% [3-11] | 5.8% / 15.8% [4-8] | 6.2% / 15.9% [4-9] |
| K3.k3p | 5.5% / 14.9% [3-9] | 5.5% / 15.6% [3-9] | 5.5% / 15.2% [3-9] |
| K4 | 12.2% / 22.4% [8-17] | 11.3% / 21.9% [8-15] | 11.8% / 22.1% [8-16] |
| K5 | 8.2% / 21.6% [7-9] | 11.0% / 22.3% [10-12] | 9.6% / 22.0% [9-10] |

Flagged differences from the base under C-bot (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by6: +1.1 points (+0.2 to +2.0); K3.by7: +1.2 points (+0.2 to +2.3); K3.by8: +1.3 points (+0.2 to +2.4); K3.never: -1.0 points (-2.0 to -0.1); K4: +1.0 points (+0.2 to +2.0).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 3.7% [3-4, Wilson] | 1.9% [2-2, Wilson] |
| K3.by4 | 4.3% [4-5, Wilson] | 8.9% [8-9, Wilson] | 6.6% [6-7, Wilson] |
| K3.by5 | 20.6% [20-21, Wilson] | 10.0% [9-11, Wilson] | 15.3% [15-16, Wilson] |
| K3.by6 | 23.9% [23-25, Wilson] | 10.0% [9-11, Wilson] | 16.9% [16-17, Wilson] |
| K3.by7 | 23.9% [23-25, Wilson] | 10.0% [9-11, Wilson] | 16.9% [16-17, Wilson] |
| K3.by8 | 23.9% [23-25, Wilson] | 10.0% [9-11, Wilson] | 16.9% [16-17, Wilson] |
| K3.never | 76.1% [75-77, Wilson] | 90.0% [89-91, Wilson] | 83.1% [83-84, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.3% [4-5, Wilson] | 3.7% [3-4, Wilson] | 4.0% [4-4, Wilson] |
| K3.k3p | 19.6% [19-20, Wilson] | 6.2% [6-7, Wilson] | 12.9% [12-13, Wilson] |
| K4 | 23.9% [23-25, Wilson] | 10.0% [9-11, Wilson] | 16.9% [16-17, Wilson] |
| K5 | 17.7% [17-18, Wilson] | 23.5% [23-24, Wilson] | 20.6% [20-21, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by5: +2.9 points (+2.3 to +3.6); K3.by6: +3.3 points (+2.7 to +4.0); K3.by7: +3.3 points (+2.7 to +4.0); K3.by8: +3.3 points (+2.7 to +4.0); K3.never: -3.3 points (-4.0 to -2.7); K3.k3p: +3.4 points (+2.8 to +3.9); K4: +3.3 points (+2.7 to +4.0); K5: -1.4 points (-2.2 to -0.6).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.8% [3-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.6% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by4 | 4.6% [4-5, Wilson] | 7.5% [7-8, Wilson] | 6.0% [6-6, Wilson] |
| K3.by5 | 8.4% [8-9, Wilson] | 23.7% [23-25, Wilson] | 16.1% [16-17, Wilson] |
| K3.by6 | 36.6% [36-38, Wilson] | 27.1% [26-28, Wilson] | 31.9% [31-33, Wilson] |
| K3.by7 | 39.8% [39-41, Wilson] | 27.1% [26-28, Wilson] | 33.5% [33-34, Wilson] |
| K3.by8 | 39.8% [39-41, Wilson] | 27.1% [26-28, Wilson] | 33.5% [33-34, Wilson] |
| K3.never | 60.2% [59-61, Wilson] | 72.9% [72-74, Wilson] | 66.5% [66-67, Wilson] |
| K3.k0 | 4.6% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 3.9% [3-4, Wilson] | 4.7% [4-5, Wilson] | 4.3% [4-5, Wilson] |
| K3.k3p | 31.4% [30-32, Wilson] | 19.6% [19-20, Wilson] | 25.5% [25-26, Wilson] |
| K4 | 35.2% [34-36, Wilson] | 24.3% [23-25, Wilson] | 29.8% [29-30, Wilson] |
| K5 | 13.1% [12-14, Wilson] | 17.8% [17-19, Wilson] | 15.4% [15-16, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by5: +2.2 points (+1.5 to +2.9); K3.by6: +5.2 points (+4.4 to +6.1); K3.by7: +5.2 points (+4.4 to +6.1); K3.by8: +5.2 points (+4.4 to +6.1); K3.never: -5.2 points (-6.1 to -4.4); K3.k3p: +4.9 points (+4.2 to +5.7); K4: +5.1 points (+4.3 to +5.9); K5: -1.7 points (-2.4 to -1.0).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.8% [3-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.6% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by4 | 4.6% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.by5 | 4.6% [4-5, Wilson] | 6.9% [6-7, Wilson] | 5.7% [5-6, Wilson] |
| K3.by6 | 8.5% [8-9, Wilson] | 7.3% [7-8, Wilson] | 7.9% [8-8, Wilson] |
| K3.by7 | 8.7% [8-9, Wilson] | 34.6% [34-36, Wilson] | 21.6% [21-22, Wilson] |
| K3.by8 | 44.8% [44-46, Wilson] | 34.8% [34-36, Wilson] | 39.8% [39-40, Wilson] |
| K3.never | 55.2% [54-56, Wilson] | 65.2% [64-66, Wilson] | 60.2% [60-61, Wilson] |
| K3.k0 | 4.6% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.7% [3-4, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.1% [4-4, Wilson] | 4.5% [4-5, Wilson] | 4.3% [4-5, Wilson] |
| K3.k3p | 36.1% [35-37, Wilson] | 27.5% [27-28, Wilson] | 31.8% [31-32, Wilson] |
| K4 | 40.2% [39-41, Wilson] | 32.0% [31-33, Wilson] | 36.1% [35-37, Wilson] |
| K5 | 9.0% [8-10, Wilson] | 11.2% [11-12, Wilson] | 10.1% [10-10, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by7: +1.7 points (+1.0 to +2.4); K3.by8: +3.9 points (+3.0 to +4.7); K3.never: -3.9 points (-4.7 to -3.0); K3.k2: -1.1 points (-1.5 to -0.7); K3.k3p: +4.8 points (+4.0 to +5.6); K4: +3.7 points (+2.8 to +4.6).

Clock measures under C-fixed reference (fast pace, 190-HP Mega ex) (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.by3 | 0.0% [0-0, Wilson] | 3.7% [3-4, Wilson] | 1.9% [2-2, Wilson] |
| K3.by4 | 4.3% [4-5, Wilson] | 7.5% [7-8, Wilson] | 5.9% [6-6, Wilson] |
| K3.by5 | 16.7% [16-17, Wilson] | 8.9% [8-9, Wilson] | 12.8% [12-13, Wilson] |
| K3.by6 | 21.2% [20-22, Wilson] | 8.9% [8-9, Wilson] | 15.0% [15-16, Wilson] |
| K3.by7 | 21.2% [20-22, Wilson] | 8.9% [8-9, Wilson] | 15.0% [15-16, Wilson] |
| K3.by8 | 21.2% [20-22, Wilson] | 8.9% [8-9, Wilson] | 15.0% [15-16, Wilson] |
| K3.never | 78.8% [78-80, Wilson] | 91.1% [91-92, Wilson] | 85.0% [84-85, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k2 | 4.3% [4-5, Wilson] | 3.7% [3-4, Wilson] | 4.0% [4-4, Wilson] |
| K3.k3p | 16.9% [16-18, Wilson] | 5.1% [5-6, Wilson] | 11.0% [11-11, Wilson] |
| K4 | 21.2% [20-22, Wilson] | 8.9% [8-9, Wilson] | 15.0% [15-16, Wilson] |
| K5 | 17.7% [17-18, Wilson] | 23.5% [23-24, Wilson] | 20.6% [20-21, Wilson] |

Flagged differences from the base under C-fixed reference (fast pace, 190-HP Mega ex) (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by5: +2.3 points (+1.7 to +2.9); K3.by6: +2.9 points (+2.2 to +3.5); K3.by7: +2.9 points (+2.2 to +3.5); K3.by8: +2.9 points (+2.2 to +3.5); K3.never: -2.9 points (-3.5 to -2.2); K3.k3p: +2.9 points (+2.4 to +3.4); K4: +2.9 points (+2.2 to +3.5); K5: -1.4 points (-2.2 to -0.6).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard line in play (end of own turn t), own turn 2 | +2.1 (+1.5 to +2.6) FLAG | +2.2 (+1.6 to +2.7) FLAG | +2.1 (+1.7 to +2.5) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | +2.4 (+1.9 to +2.9) FLAG | +2.4 (+1.8 to +2.9) FLAG | +2.4 (+2.0 to +2.7) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | +1.9 (+1.5 to +2.4) FLAG | +2.1 (+1.7 to +2.6) FLAG | +2.0 (+1.7 to +2.3) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 5 | +1.4 (+1.0 to +1.7) FLAG | +1.3 (+1.0 to +1.7) FLAG | +1.3 (+1.1 to +1.6) FLAG |
| K2 Kingambit in play, own turn 3 | +3.2 (+2.7 to +3.7) FLAG | +2.8 (+2.3 to +3.3) FLAG | +3.0 (+2.6 to +3.4) FLAG |
| K2 Kingambit in play, own turn 4 | +5.8 (+5.3 to +6.4) FLAG | +5.2 (+4.7 to +5.8) FLAG | +5.5 (+5.1 to +5.9) FLAG |
| K2 Kingambit in play, own turn 5 | +6.9 (+6.3 to +7.5) FLAG | +6.6 (+6.0 to +7.2) FLAG | +6.7 (+6.3 to +7.2) FLAG |
| K2 Kingambit in play, own turn 6 | +6.5 (+6.0 to +7.1) FLAG | +6.0 (+5.4 to +6.5) FLAG | +6.2 (+5.9 to +6.6) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +2.7 (+2.2 to +3.3) FLAG | +2.6 (+2.1 to +3.1) FLAG | +2.7 (+2.3 to +3.1) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +3.1 (+2.5 to +3.7) FLAG | +2.7 (+2.1 to +3.3) FLAG | +2.9 (+2.5 to +3.3) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.4 (+1.8 to +3.0) FLAG | +2.3 (+1.7 to +2.9) FLAG | +2.4 (+2.0 to +2.8) FLAG |
| G3 Pawniard in play, own turn 2 | +1.2 (+0.6 to +1.8) FLAG | +1.2 (+0.6 to +1.8) FLAG | +1.2 (+0.8 to +1.6) FLAG |
| G3 Pawniard in play, own turn 4 | -3.9 (-4.5 to -3.3) FLAG | -3.1 (-3.7 to -2.5) FLAG | -3.5 (-3.9 to -3.1) FLAG |
| G3 Pawniard in play, own turn 5 | -5.6 (-6.2 to -5.0) FLAG | -5.3 (-5.9 to -4.7) FLAG | -5.4 (-5.8 to -5.0) FLAG |
| G3 Kingambit in play, own turn 3 | +3.2 (+2.7 to +3.7) FLAG | +2.8 (+2.3 to +3.3) FLAG | +3.0 (+2.6 to +3.4) FLAG |
| G3 Kingambit in play, own turn 4 | +5.8 (+5.3 to +6.4) FLAG | +5.2 (+4.7 to +5.8) FLAG | +5.5 (+5.1 to +5.9) FLAG |
| G3 Kingambit in play, own turn 5 | +6.9 (+6.3 to +7.5) FLAG | +6.6 (+6.0 to +7.2) FLAG | +6.7 (+6.3 to +7.2) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -2.6 (-3.2 to -2.1) FLAG | -2.4 (-3.0 to -1.9) FLAG | -2.5 (-2.9 to -2.2) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -3.7 (-4.1 to -3.2) FLAG | -2.9 (-3.4 to -2.5) FLAG | -3.3 (-3.6 to -3.0) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -3.0 (-3.4 to -2.6) FLAG | -2.9 (-3.3 to -2.5) FLAG | -3.0 (-3.3 to -2.7) FLAG |
| G3 Alolan Muk in play, own turn 2 | +1.8 (+1.3 to +2.4) FLAG | +1.5 (+0.9 to +2.0) FLAG | +1.6 (+1.3 to +2.0) FLAG |
| G3 Alolan Muk in play, own turn 3 | +3.3 (+2.7 to +3.9) FLAG | +3.1 (+2.5 to +3.7) FLAG | +3.2 (+2.8 to +3.6) FLAG |
| G3 Alolan Muk in play, own turn 4 | +3.9 (+3.2 to +4.5) FLAG | +3.4 (+2.8 to +4.0) FLAG | +3.6 (+3.2 to +4.1) FLAG |
| G3 Alolan Muk in play, own turn 5 | +3.0 (+2.4 to +3.6) FLAG | +3.0 (+2.4 to +3.7) FLAG | +3.0 (+2.6 to +3.5) FLAG |
| G3 Glimmet in play, own turn 3 | -3.4 (-4.0 to -2.8) FLAG | -3.5 (-4.1 to -2.9) FLAG | -3.4 (-3.9 to -3.0) FLAG |
| G3 Glimmet in play, own turn 4 | -4.7 (-5.3 to -4.2) FLAG | -4.8 (-5.4 to -4.3) FLAG | -4.8 (-5.2 to -4.4) FLAG |
| G3 Glimmet in play, own turn 5 | -4.7 (-5.1 to -4.2) FLAG | -4.6 (-5.0 to -4.1) FLAG | -4.6 (-4.9 to -4.3) FLAG |
| G3 Glimmora in play, own turn 2 | +3.0 (+2.4 to +3.6) FLAG | +2.4 (+1.8 to +3.1) FLAG | +2.7 (+2.3 to +3.2) FLAG |
| G3 Glimmora in play, own turn 3 | +3.4 (+2.9 to +4.0) FLAG | +3.3 (+2.8 to +3.8) FLAG | +3.4 (+3.0 to +3.7) FLAG |
| G3 Glimmora in play, own turn 4 | +2.8 (+2.4 to +3.2) FLAG | +2.6 (+2.2 to +3.0) FLAG | +2.7 (+2.4 to +3.0) FLAG |
| G3 Glimmora in play, own turn 5 | +1.8 (+1.5 to +2.1) FLAG | +1.6 (+1.3 to +1.8) FLAG | +1.7 (+1.5 to +1.9) FLAG |
| G3 Regigigas in play, own turn 2 | +1.7 (+1.1 to +2.3) FLAG | +1.3 (+0.7 to +1.9) FLAG | +1.5 (+1.1 to +1.9) FLAG |
| G3 Regigigas in play, own turn 3 | +1.9 (+1.3 to +2.4) FLAG | +1.5 (+1.0 to +2.1) FLAG | +1.7 (+1.3 to +2.1) FLAG |
| G3 Regigigas in play, own turn 4 | +1.4 (+0.9 to +1.9) FLAG | +1.0 (+0.5 to +1.6) FLAG | +1.2 (+0.8 to +1.6) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | +2.3 (+1.8 to +2.8) FLAG | +1.7 (+1.2 to +2.3) FLAG | +2.0 (+1.6 to +2.4) FLAG |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | +1.5 (+1.1 to +1.9) FLAG | +1.5 (+1.1 to +1.8) FLAG | +1.5 (+1.2 to +1.7) FLAG |
| G4.s2 a Stage 2 in play, own turn 3 | +3.2 (+2.7 to +3.7) FLAG | +2.8 (+2.3 to +3.3) FLAG | +3.0 (+2.6 to +3.4) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +5.8 (+5.3 to +6.4) FLAG | +5.2 (+4.7 to +5.8) FLAG | +5.5 (+5.1 to +5.9) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +6.9 (+6.3 to +7.5) FLAG | +6.6 (+6.0 to +7.2) FLAG | +6.7 (+6.3 to +7.2) FLAG |
| G5.any3 an empty own turn among turns 1-3 | -4.1 (-4.6 to -3.6) FLAG | -3.9 (-4.5 to -3.4) FLAG | -4.0 (-4.4 to -3.6) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +3.2 (+2.7 to +3.7) FLAG | +2.8 (+2.3 to +3.3) FLAG | +3.0 (+2.6 to +3.4) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +5.8 (+5.3 to +6.4) FLAG | +5.2 (+4.7 to +5.8) FLAG | +5.5 (+5.1 to +5.9) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +6.9 (+6.3 to +7.5) FLAG | +6.6 (+6.0 to +7.2) FLAG | +6.7 (+6.3 to +7.2) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.025 (-0.033 to -0.017) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, deck01.**

Gains (flagged, pooled): K1 Pawniard line in play (end of own turn t), own turn 2 +2.1 points; K1 Pawniard line in play (end of own turn t), own turn 3 +2.4 points; K1 Pawniard line in play (end of own turn t), own turn 4 +2.0 points; K1 Pawniard line in play (end of own turn t), own turn 5 +1.3 points; K2 Kingambit in play, own turn 3 +3.0 points; K2 Kingambit in play, own turn 4 +5.5 points; K2 Kingambit in play, own turn 5 +6.7 points; K2 Kingambit in play, own turn 6 +6.2 points; K6 Muk and Regigigas both in play, own turn 3 +2.7 points; K6 Muk and Regigigas both in play, own turn 4 +2.9 points.
Gives up (flagged, pooled): G3 Pawniard in play, own turn 4 -3.5 points; G3 Pawniard in play, own turn 5 -5.4 points; G3 Alolan Grimer in play, own turn 3 -2.5 points; G3 Alolan Grimer in play, own turn 4 -3.3 points; G3 Alolan Grimer in play, own turn 5 -3.0 points; G3 Glimmet in play, own turn 3 -3.4 points; G3 Glimmet in play, own turn 4 -4.8 points; G3 Glimmet in play, own turn 5 -4.6 points.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow, C-fixed reference (fast pace, 190-HP Mega ex) (Copycat draws the opponent's hand: the recorded one under C-his, otherwise 4).

**Not modelled** (stated in every summary): Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, retreats, and disruption (SPEC "It cannot represent").

## Against lib/consistency.py on deck 01 (SPEC test 6)

Kingambit in play by own turn t, going first, deck 01, no clock. Gaps are explained by named differences in the script; a gap is not a failure.

| Own turn | this tester | lib/consistency.py solitaire | gap | named difference |
|---|---|---|---|---|
| 2 | 11.8% | 8.1% | +3.6 | +1.7 points of the +3.6 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +1.9 is Copycat and Supporter policy: the script plays Copycat by the N/M rule (fewer than N still-needed plan cards in hand and the opponent's hand at least M larger than ours), the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -0.6 from it); it also holds Pawniard only by the T-now trigger here and puts Energy on the Pawniard line first |
| 3 | 24.3% | 15.0% | +9.3 | +4.8 points of the +9.3 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +4.6 is Copycat and Supporter policy: the script plays Copycat by the N/M rule (fewer than N still-needed plan cards in hand and the opponent's hand at least M larger than ours), the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -2.0 from it); it also holds Pawniard only by the T-now trigger here and puts Energy on the Pawniard line first |
| 4 | 40.0% | 23.4% | +16.6 | +9.4 points of the +16.6 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +7.2 is Copycat and Supporter policy: the script plays Copycat by the N/M rule (fewer than N still-needed plan cards in hand and the opponent's hand at least M larger than ours), the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -3.5 from it); it also holds Pawniard only by the T-now trigger here and puts Energy on the Pawniard line first |
| 5 | 57.0% | 33.7% | +23.3 | +14.2 points of the +23.3 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +9.1 is Copycat and Supporter policy: the script plays Copycat by the N/M rule (fewer than N still-needed plan cards in hand and the opponent's hand at least M larger than ours), the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -5.2 from it); it also holds Pawniard only by the T-now trigger here and puts Energy on the Pawniard line first |

## Against the bots (SPEC test 7)

Deck 01, C-bot clock, 20,000 deals: the share of deals whose first Overlord's Blade is on own turn t, beside the first Overlord's Blade turn in the 64 recorded games (km3 and kx3 against km3 on the 8 panel lists, replay_b). A gap is printed, not a failure: the tester plays a fixed script and the bots do not.

| First Blade on own turn | this tester | the 64 bot games |
|---|---|---|
| 2 | 1.2% | 0 of 64 (0%) |
| 3 | 2.4% | 0 of 64 (0%) |
| 4 | 1.5% | 1 of 64 (2%) |
| 5 | 3.2% | 3 of 64 (5%) |
| 6 | 3.9% | 8 of 64 (12%) |
| 7 | 2.5% | 6 of 64 (9%) |
| 8 | 1.6% | 0 of 64 (0%) |
| 9 | 0.0% | 3 of 64 (5%) |
| 11 | 0.0% | 1 of 64 (2%) |
| never in the horizon | 83.8% | 42 of 64 (66%) |

## How much each open choice matters (on the base list)

Each alternative is run once on the base list on the same deals, against the default config (T-first-KO, Copycat N=2 M=1). Pooled, paired differences in percentage points; a "*" marks a range (+-1.96 sd/sqrt(n) for the setup measures, as in the paired tables) that excludes 0 with a difference of at least 1 point. The Copycat grid is N in {1, 2, 3} by M in {0, 1, 2}; its headline N=2 M=1 equals the default (all zeros). Dustin has not answered N and M yet.

Setup measures with no knock-outs (these runs bench Pawniard at once under T-first-KO and T-late, so the bench-trigger rows differ only on T-pieces here):

| Alternative | P1 | K1.t1 | K1.t3 | K2.t3 | K2.t5 | G5.any3 | G6.t3 |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| T-late: Pawniard benched one own turn after T-first-KO | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | -39.1* | -49.8* | -7.8* | -20.9* | +0.6 | -7.8* |
| lead order: Pawniard first | -0.1 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Poke Ball over names, not cards | +0.0 | +1.2* | +0.8 | +0.2 | -0.1 | +0.1 | +0.2 |
| Copycat N=1 M=0 | +0.0 | -1.2* | -2.4* | -2.4* | -4.5* | +3.3* | -2.4* |
| Copycat N=1 M=1 | +0.0 | -1.2* | -2.5* | -2.4* | -4.6* | +3.4* | -2.4* |
| Copycat N=1 M=2 | +0.0 | -1.3* | -2.9* | -2.6* | -5.4* | +3.9* | -2.6* |
| Copycat N=2 M=0 | +0.0 | +0.1 | +0.7 | +0.3 | +0.9 | -1.1* | +0.3 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | +0.0 | -0.7 | -1.7* | -1.1* | -2.7* | +2.3* | -1.1* |
| Copycat N=3 M=0 | +0.0 | +1.4* | +2.8* | +0.9 | +1.9* | -4.0* | +0.9 |
| Copycat N=3 M=1 | +0.0 | +1.0 | +1.2* | +0.4 | +0.8 | -1.3* | +0.4 |
| Copycat N=3 M=2 | +0.0 | -0.5 | -1.4* | -1.0* | -2.4* | +2.0* | -1.0* |

Plan lines under C-his, difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +1.9* | -0.7 | +3.2* | +0.0 | +0.4 | +0.0 | -2.2* |
| T-late: Pawniard benched one own turn after T-first-KO | +5.6* | -0.9 | -5.5* | +0.0 | -7.4* | -0.0 | +4.1* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +3.4* | -0.8 | -2.5* | -0.6 | -5.0* | -0.5 | +3.1* |
| lead order: Pawniard first | +0.1 | +11.9* | -3.0* | -0.5 | -4.2* | -0.5 | -0.3 |
| Poke Ball over names, not cards | -0.1 | -0.0 | -0.2 | -0.0 | -0.1 | +0.0 | +0.0 |
| Copycat N=1 M=0 | -0.3 | +1.1* | -1.3* | -0.4 | -1.5* | -0.2 | +1.4* |
| Copycat N=1 M=1 | -0.3 | +1.2* | -1.4* | -0.4 | -1.7* | -0.2 | +1.4* |
| Copycat N=1 M=2 | -0.3 | +1.3* | -1.6* | -0.4 | -2.0* | -0.2 | +1.5* |
| Copycat N=2 M=0 | +0.0 | -0.1 | +0.1 | -0.0 | +0.2 | +0.0 | -0.1 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | +0.0 | +0.3 | -0.6 | -0.1 | -0.8 | -0.1 | +0.6 |
| Copycat N=3 M=0 | +0.3 | -0.8 | +0.1 | +0.0 | +0.4 | +0.1 | -0.7 |
| Copycat N=3 M=1 | +0.2 | -0.7 | +0.3 | +0.1 | +0.4 | +0.1 | -0.5 |
| Copycat N=3 M=2 | +0.2 | -0.1 | -0.4 | -0.0 | -0.6 | -0.0 | +0.3 |

Plan lines under C-his, seat-matched, difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +2.7* | -1.4* | +2.7* | +0.0 | +0.2 | +0.0 | -2.3* |
| T-late: Pawniard benched one own turn after T-first-KO | +6.9* | -1.7* | -5.9* | +0.0 | -7.3* | +0.0 | +4.8* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +3.9* | -1.2* | -2.3* | -0.5 | -4.1* | -0.4 | +3.3* |
| lead order: Pawniard first | +0.2 | +11.5* | -2.8* | -0.4 | -3.6* | -0.4 | -0.5 |
| Poke Ball over names, not cards | -0.1 | -0.3 | -0.2 | +0.0 | -0.1 | +0.0 | +0.2 |
| Copycat N=1 M=0 | -0.1 | +1.2* | -0.9 | -0.3 | -0.9 | -0.2 | +1.1* |
| Copycat N=1 M=1 | -0.1 | +1.3* | -1.0* | -0.3 | -1.1* | -0.2 | +1.1* |
| Copycat N=1 M=2 | -0.1 | +1.3* | -1.2* | -0.3 | -1.3* | -0.2 | +1.3* |
| Copycat N=2 M=0 | +0.0 | -0.2 | +0.1 | -0.0 | +0.2 | +0.0 | -0.3 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | +0.0 | +0.3 | -0.5 | -0.1 | -0.7 | -0.0 | +0.5 |
| Copycat N=3 M=0 | +0.2 | -0.9 | +0.0 | +0.0 | +0.2 | +0.1 | -0.7 |
| Copycat N=3 M=1 | +0.1 | -0.6 | +0.2 | +0.1 | +0.4 | +0.1 | -0.5 |
| Copycat N=3 M=2 | +0.2 | -0.0 | -0.3 | -0.0 | -0.4 | -0.0 | +0.2 |

Plan lines under C-bot, difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +2.3* | -1.4* | +0.1 | +0.0 | +0.2 | +0.0 | -5.8* |
| T-late: Pawniard benched one own turn after T-first-KO | +4.6* | +3.7* | -5.5* | -0.0 | -2.7* | -0.0 | +6.3* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +3.0* | -0.7 | -3.1* | -0.1 | -3.2* | -0.2 | +0.2 |
| lead order: Pawniard first | +1.4* | +10.5* | -2.2* | -0.1 | -2.8* | -0.1 | -1.9* |
| Poke Ball over names, not cards | -0.1 | +0.1 | -0.3 | -0.0 | -0.2 | -0.0 | +0.3 |
| Copycat N=1 M=0 | -0.1 | +1.6* | -1.0 | -0.0 | -0.9 | -0.0 | +0.8 |
| Copycat N=1 M=1 | -0.1 | +1.6* | -1.0* | -0.0 | -1.0 | -0.0 | +0.8 |
| Copycat N=1 M=2 | -0.2 | +1.7* | -1.3* | -0.1 | -1.2* | -0.1 | +0.9 |
| Copycat N=2 M=0 | +0.0 | -0.2 | +0.2 | +0.0 | +0.2 | +0.0 | -0.1 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | -0.1 | +1.1* | -0.7 | -0.0 | -0.7 | -0.0 | +0.6 |
| Copycat N=3 M=0 | +0.2 | -0.4 | -0.1 | -0.0 | +0.2 | +0.0 | +0.1 |
| Copycat N=3 M=1 | +0.1 | -0.2 | -0.1 | -0.0 | +0.0 | -0.0 | -0.0 |
| Copycat N=3 M=2 | -0.1 | +1.0* | -0.7 | -0.0 | -0.6 | -0.0 | +0.5 |

Plan lines under C-fixed fast, difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +0.0 | +2.4* | +0.7 | +0.7 | +0.7 | +0.7 | -3.5* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.0 | -5.9* | -0.9 | -0.9 | -0.9 | -0.9 | +8.2* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | -8.6* | -4.6* | -4.6* | -4.7* | -4.7* | +2.6* |
| lead order: Pawniard first | +0.0 | +8.4* | -2.4* | -2.4* | -2.4* | -2.4* | +2.8* |
| Poke Ball over names, not cards | +0.0 | -0.2 | -0.1 | -0.1 | +0.0 | +0.0 | -0.1 |
| Copycat N=1 M=0 | +0.0 | +0.2 | -2.3* | -2.3* | -2.4* | -2.4* | +1.6* |
| Copycat N=1 M=1 | +0.0 | +0.2 | -2.3* | -2.3* | -2.4* | -2.4* | +1.6* |
| Copycat N=1 M=2 | +0.0 | +0.1 | -2.6* | -2.6* | -2.8* | -2.8* | +1.8* |
| Copycat N=2 M=0 | +0.0 | +0.1 | +0.3 | +0.3 | +0.4 | +0.4 | -0.3 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | +0.0 | +0.1 | -1.3* | -1.3* | -1.4* | -1.4* | +1.0 |
| Copycat N=3 M=0 | +0.0 | -0.1 | +0.8 | +0.8 | +1.0 | +1.0 | -0.2 |
| Copycat N=3 M=1 | +0.0 | -0.4 | +0.4 | +0.4 | +0.5 | +0.5 | +0.0 |
| Copycat N=3 M=2 | +0.0 | +0.0 | -1.2* | -1.2* | -1.2* | -1.2* | +0.9 |

Plan lines under C-fixed medium, difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +0.0 | -2.1* | +0.7 | +0.0 | +0.8 | +0.0 | -4.1* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.0 | +1.7* | -1.4* | +0.0 | -1.3* | +0.0 | +14.2* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | -5.2* | -7.2* | +0.0 | -7.2* | +0.0 | +4.8* |
| lead order: Pawniard first | +0.0 | +7.8* | -4.5* | +0.0 | -4.7* | +0.0 | +1.2* |
| Poke Ball over names, not cards | +0.0 | -0.4 | -0.2 | +0.0 | -0.2 | +0.0 | +0.2 |
| Copycat N=1 M=0 | +0.0 | +0.9 | -3.4* | +0.0 | -3.5* | +0.0 | +3.2* |
| Copycat N=1 M=1 | +0.0 | +0.9 | -3.5* | +0.0 | -3.6* | +0.0 | +3.2* |
| Copycat N=1 M=2 | +0.0 | +0.8 | -4.2* | +0.0 | -4.3* | +0.0 | +3.9* |
| Copycat N=2 M=0 | +0.0 | -0.0 | +0.8 | +0.0 | +0.8 | +0.0 | -0.6 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | +0.0 | +0.3 | -2.4* | +0.0 | -2.5* | +0.0 | +2.2* |
| Copycat N=3 M=0 | +0.0 | +0.0 | +1.2* | +0.0 | +1.4* | +0.0 | +0.0 |
| Copycat N=3 M=1 | +0.0 | -0.2 | +0.3 | +0.0 | +0.5 | +0.0 | +0.1 |
| Copycat N=3 M=2 | +0.0 | +0.3 | -2.3* | +0.0 | -2.3* | +0.0 | +2.1* |

Plan lines under C-fixed slow, difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +14.4* | +0.7 | +0.0 | +0.0 | +0.0 | +0.0 | -3.0* |
| T-late: Pawniard benched one own turn after T-first-KO | +4.2* | +5.1* | +0.0 | +0.0 | +0.0 | +0.0 | +3.5* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +11.7* | +5.2* | +0.0 | +0.0 | +0.0 | +0.0 | +6.5* |
| lead order: Pawniard first | +9.6* | +11.3* | +0.0 | +0.0 | +0.0 | +0.0 | +2.6* |
| Poke Ball over names, not cards | -0.1 | -0.1 | +0.0 | +0.0 | +0.0 | +0.0 | -0.1 |
| Copycat N=1 M=0 | -0.6 | +2.6* | +0.0 | +0.0 | +0.0 | +0.0 | +2.7* |
| Copycat N=1 M=1 | -0.6 | +2.7* | +0.0 | +0.0 | +0.0 | +0.0 | +2.8* |
| Copycat N=1 M=2 | -0.8 | +3.1* | +0.0 | +0.0 | +0.0 | +0.0 | +3.1* |
| Copycat N=2 M=0 | +0.2 | -0.5 | +0.0 | +0.0 | +0.0 | +0.0 | -0.5 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | -0.5 | +1.7* | +0.0 | +0.0 | +0.0 | +0.0 | +1.6* |
| Copycat N=3 M=0 | +0.4 | -0.7 | +0.0 | +0.0 | +0.0 | +0.0 | -0.8 |
| Copycat N=3 M=1 | +0.1 | -0.4 | +0.0 | +0.0 | +0.0 | +0.0 | -0.3 |
| Copycat N=3 M=2 | -0.6 | +1.6* | +0.0 | +0.0 | +0.0 | +0.0 | +1.5* |

Plan lines under C-fixed reference (fast pace, 190-HP Mega ex), difference from the default (pooled points, undecided as no):

| Alternative | P2.both | P3 | P4.ko | P4.win | P5.ko | P5.win | K3.never |
|---|---|---|---|---|---|---|---|
| T-now: Pawniard benched as soon as drawn (the old default) | +0.0 | +2.4* | -0.1 | -0.1 | -0.1 | -0.1 | -3.6* |
| T-late: Pawniard benched one own turn after T-first-KO | +0.0 | -5.9* | +0.4 | +0.4 | +0.4 | +0.4 | +6.8* |
| T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand | +0.0 | -8.6* | -0.6 | -0.6 | -0.6 | -0.6 | +2.0* |
| lead order: Pawniard first | +0.0 | +8.4* | -0.3 | -0.3 | -0.3 | -0.3 | +2.5* |
| Poke Ball over names, not cards | +0.0 | -0.2 | +0.0 | +0.0 | +0.0 | +0.0 | -0.0 |
| Copycat N=1 M=0 | +0.0 | +0.2 | -0.5 | -0.5 | -0.5 | -0.5 | +1.4* |
| Copycat N=1 M=1 | +0.0 | +0.2 | -0.5 | -0.5 | -0.5 | -0.5 | +1.4* |
| Copycat N=1 M=2 | +0.0 | +0.1 | -0.6 | -0.6 | -0.6 | -0.6 | +1.5* |
| Copycat N=2 M=0 | +0.0 | +0.1 | +0.1 | +0.1 | +0.1 | +0.1 | -0.2 |
| Copycat N=2 M=1 (the headline) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat N=2 M=2 | +0.0 | +0.1 | -0.3 | -0.3 | -0.3 | -0.3 | +0.8 |
| Copycat N=3 M=0 | +0.0 | -0.1 | +0.3 | +0.3 | +0.3 | +0.3 | -0.2 |
| Copycat N=3 M=1 | +0.0 | -0.4 | +0.1 | +0.1 | +0.1 | +0.1 | -0.1 |
| Copycat N=3 M=2 | +0.0 | +0.0 | -0.3 | -0.3 | -0.3 | -0.3 | +0.7 |

## The run record

- **code sha256**: 6fc5b64c8588bade8fb7f9a305ee72107fceeeb561656a7afb9e6733db3fa7b3
- **engine commit**: pinned rules-switch-2 engine, main 70319c3d (engine unchanged since c045ede); no engine program is run
- **seeds**: 24,700,000,000 + deal index i (deal i is the same in every version and under every clock); 100,000 deals with no knock-outs, 20,000 deals per clock
- **clock sources**: C-his: rl/results/pause_games_new_2026-10-13/v2/positions_all.json (12 Kingambit games); C-bot: rl/results/kx3_on_rules2_2026-10/replay_b/games.jsonl (64 deck-01 rows); C-fixed: fast, medium, slow (SPEC)
- **base list**: rl/results/pause_games_new_2026-10-13/decks/KW261012_203719000.txt (card-list id 73dfed58d1d6)
- **plan config**: /home/dacz8976/credit_work/tools/rl/setup_tester/plans/kingambit.json
- **plan overrides**: none
- **wall time**: 754 s, 1 process(es) (comparisons and the choice runs included)
- **speed**: 5,687 deals per second per process (480,000 deals in 84 s of version time)

