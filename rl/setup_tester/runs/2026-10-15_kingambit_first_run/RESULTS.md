# Setup tester: kingambit_first_run

Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on the same deals for every version. It does not say who wins.
**PROPOSED, not yet confirmed by Dustin:** the plan lines K1-K6, the lead order, the promote order, the Copycat rule, the Blade target and what "a fast deck" means (C-fixed fast). None of this is to be reported to him as settled until he confirms or rewrites each.

## base (card-list id 73dfed58d1d6)

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.2371.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03373; in 8 cards: 0.05246.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 28.9% (28.5-29.3) | 29.1% (28.7-29.5) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 55.0% (54.6-55.5) | 54.9% (54.5-55.3) | 55.0% (54.7-55.3) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 66.8% (66.4-67.2) | 66.6% (66.1-67.0) | 66.7% (66.4-67.0) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 75.7% (75.3-76.0) | 75.6% (75.2-76.0) | 75.6% (75.4-75.9) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 83.6% (83.3-83.9) | 83.6% (83.2-83.9) | 83.6% (83.4-83.8) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 90.1% (89.8-90.3) | 90.1% (89.9-90.4) | 90.1% (89.9-90.3) |
| K2 Kingambit in play, own turn 2 | 10.4% (10.1-10.7) | 10.2% (9.9-10.4) | 10.3% (10.1-10.5) |
| K2 Kingambit in play, own turn 3 | 19.8% (19.4-20.1) | 19.7% (19.4-20.1) | 19.7% (19.5-20.0) |
| K2 Kingambit in play, own turn 4 | 32.0% (31.6-32.4) | 32.2% (31.8-32.6) | 32.1% (31.8-32.4) |
| K2 Kingambit in play, own turn 5 | 47.4% (47.0-47.9) | 47.6% (47.1-48.0) | 47.5% (47.2-47.8) |
| K2 Kingambit in play, own turn 6 | 63.8% (63.4-64.2) | 64.1% (63.6-64.5) | 63.9% (63.6-64.2) |
| K6 Muk and Regigigas both in play, own turn 3 | 22.6% (22.3-23.0) | 22.7% (22.3-23.1) | 22.7% (22.4-22.9) |
| K6 Muk and Regigigas both in play, own turn 4 | 30.8% (30.4-31.2) | 31.3% (30.9-31.7) | 31.0% (30.8-31.3) |
| K6 Muk and Regigigas both in play, own turn 5 | 38.0% (37.5-38.4) | 38.2% (37.8-38.7) | 38.1% (37.8-38.4) |
| G3 Pawniard in play, own turn 1 | 55.0% (54.6-55.5) | 54.9% (54.5-55.3) | 55.0% (54.7-55.3) |
| G3 Pawniard in play, own turn 2 | 56.4% (55.9-56.8) | 56.4% (56.0-56.8) | 56.4% (56.1-56.7) |
| G3 Pawniard in play, own turn 3 | 55.9% (55.5-56.4) | 55.9% (55.5-56.3) | 55.9% (55.6-56.2) |
| G3 Pawniard in play, own turn 4 | 51.6% (51.2-52.1) | 51.4% (50.9-51.8) | 51.5% (51.2-51.8) |
| G3 Pawniard in play, own turn 5 | 42.6% (42.2-43.1) | 42.5% (42.1-43.0) | 42.6% (42.3-42.9) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 10.4% (10.1-10.7) | 10.2% (9.9-10.4) | 10.3% (10.1-10.5) |
| G3 Kingambit in play, own turn 3 | 19.8% (19.4-20.1) | 19.7% (19.4-20.1) | 19.7% (19.5-20.0) |
| G3 Kingambit in play, own turn 4 | 32.0% (31.6-32.4) | 32.2% (31.8-32.6) | 32.1% (31.8-32.4) |
| G3 Kingambit in play, own turn 5 | 47.4% (47.0-47.9) | 47.6% (47.1-48.0) | 47.5% (47.2-47.8) |
| G3 Alolan Grimer in play, own turn 1 | 51.8% (51.4-52.3) | 52.1% (51.7-52.6) | 52.0% (51.7-52.3) |
| G3 Alolan Grimer in play, own turn 2 | 35.5% (35.1-35.9) | 35.4% (35.0-35.8) | 35.5% (35.2-35.8) |
| G3 Alolan Grimer in play, own turn 3 | 29.0% (28.6-29.4) | 29.1% (28.7-29.5) | 29.1% (28.8-29.4) |
| G3 Alolan Grimer in play, own turn 4 | 21.6% (21.3-22.0) | 21.4% (21.0-21.7) | 21.5% (21.2-21.8) |
| G3 Alolan Grimer in play, own turn 5 | 14.2% (13.9-14.5) | 14.2% (13.9-14.5) | 14.2% (14.0-14.4) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 24.9% (24.5-25.3) | 25.2% (24.8-25.6) | 25.0% (24.8-25.3) |
| G3 Alolan Muk in play, own turn 3 | 36.7% (36.2-37.1) | 36.8% (36.4-37.2) | 36.7% (36.4-37.0) |
| G3 Alolan Muk in play, own turn 4 | 47.3% (46.9-47.8) | 47.7% (47.3-48.2) | 47.5% (47.2-47.8) |
| G3 Alolan Muk in play, own turn 5 | 56.5% (56.1-57.0) | 56.7% (56.3-57.2) | 56.6% (56.3-56.9) |
| G3 Glimmet in play, own turn 1 | 80.9% (80.6-81.3) | 81.1% (80.8-81.4) | 81.0% (80.8-81.2) |
| G3 Glimmet in play, own turn 2 | 49.2% (48.8-49.7) | 49.2% (48.7-49.6) | 49.2% (48.9-49.5) |
| G3 Glimmet in play, own turn 3 | 40.9% (40.4-41.3) | 40.8% (40.4-41.2) | 40.8% (40.5-41.1) |
| G3 Glimmet in play, own turn 4 | 30.9% (30.5-31.3) | 30.9% (30.5-31.3) | 30.9% (30.6-31.2) |
| G3 Glimmet in play, own turn 5 | 20.7% (20.3-21.1) | 20.9% (20.5-21.2) | 20.8% (20.5-21.0) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 59.7% (59.3-60.1) | 60.2% (59.7-60.6) | 59.9% (59.6-60.2) |
| G3 Glimmora in play, own turn 3 | 75.4% (75.1-75.8) | 75.7% (75.3-76.1) | 75.6% (75.3-75.8) |
| G3 Glimmora in play, own turn 4 | 86.2% (85.9-86.5) | 86.2% (85.9-86.5) | 86.2% (86.0-86.4) |
| G3 Glimmora in play, own turn 5 | 93.0% (92.8-93.3) | 93.1% (92.9-93.3) | 93.1% (92.9-93.2) |
| G3 Regigigas in play, own turn 1 | 54.0% (53.6-54.5) | 54.0% (53.6-54.4) | 54.0% (53.7-54.3) |
| G3 Regigigas in play, own turn 2 | 63.6% (63.2-64.0) | 63.6% (63.1-64.0) | 63.6% (63.3-63.9) |
| G3 Regigigas in play, own turn 3 | 69.5% (69.1-69.9) | 69.7% (69.3-70.1) | 69.6% (69.3-69.9) |
| G3 Regigigas in play, own turn 4 | 73.5% (73.1-73.9) | 73.7% (73.3-74.1) | 73.6% (73.3-73.9) |
| G3 Regigigas in play, own turn 5 | 75.9% (75.5-76.2) | 75.9% (75.6-76.3) | 75.9% (75.6-76.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 75.9% (75.5-76.3) | 76.3% (75.9-76.7) | 76.1% (75.8-76.4) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 88.7% (88.4-89.0) | 88.9% (88.6-89.2) | 88.8% (88.6-89.0) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 95.4% (95.2-95.6) | 95.5% (95.3-95.7) | 95.5% (95.3-95.6) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.4% (98.3-98.5) | 98.5% (98.4-98.6) | 98.5% (98.4-98.6) |
| G4.s2 a Stage 2 in play, own turn 2 | 10.4% (10.1-10.7) | 10.2% (9.9-10.4) | 10.3% (10.1-10.5) |
| G4.s2 a Stage 2 in play, own turn 3 | 19.8% (19.4-20.1) | 19.7% (19.4-20.1) | 19.7% (19.5-20.0) |
| G4.s2 a Stage 2 in play, own turn 4 | 32.0% (31.6-32.4) | 32.2% (31.8-32.6) | 32.1% (31.8-32.4) |
| G4.s2 a Stage 2 in play, own turn 5 | 47.4% (47.0-47.9) | 47.6% (47.1-48.0) | 47.5% (47.2-47.8) |
| G5.any3 an empty own turn among turns 1-3 | 28.8% (28.4-29.2) | 28.8% (28.4-29.2) | 28.8% (28.5-29.1) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.2% (9.9-10.4) | 5.1% (4.9-5.2) |
| G6 Kingambit with [DD] attached, own turn 3 | 19.8% (19.4-20.1) | 19.7% (19.4-20.1) | 19.7% (19.5-20.0) |
| G6 Kingambit with [DD] attached, own turn 4 | 32.0% (31.6-32.4) | 32.2% (31.8-32.6) | 32.1% (31.8-32.4) |
| G6 Kingambit with [DD] attached, own turn 5 | 47.4% (47.0-47.9) | 47.6% (47.1-48.0) | 47.5% (47.2-47.8) |
| G5 mean empty own turns in turns 1-5 | 0.809 | 0.811 | 0.810 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.4% / 10.8% [2-3] | 1.2% / 5.4% [1-1] |
| K3.by3 | 3.6% / 12.3% [3-4] | 3.6% / 12.0% [3-4] | 3.6% / 12.1% [3-4] |
| K3.by4 | 4.5% / 13.2% [4-6] | 10.2% / 18.6% [6-14] | 7.3% / 15.8% [5-10] |
| K3.by5 | 16.2% / 24.9% [9-24] | 12.9% / 27.0% [8-18] | 14.5% / 25.9% [9-20] |
| K3.by6 | 20.0% / 34.3% [12-29] | 17.4% / 39.5% [11-25] | 18.7% / 36.9% [12-26] |
| K3.by7 | 25.8% / 48.0% [15-36] | 18.9% / 59.9% [11-28] | 22.4% / 54.0% [13-32] |
| K3.by8 | 27.3% / 67.4% [16-40] | 24.6% / 69.0% [14-37] | 26.0% / 68.2% [16-36] |
| K3.never | 32.6% / 72.7% [13-54] | 31.0% / 75.4% [13-49] | 31.8% / 74.0% [14-51] |
| K3.k0 | 4.3% / 44.4% [3-6] | 3.1% / 47.5% [2-4] | 3.7% / 45.9% [2-5] |
| K3.k1 | 0.8% / 40.8% [0-1] | 1.3% / 45.6% [1-2] | 1.0% / 43.2% [1-2] |
| K3.k2 | 19.5% / 59.5% [9-30] | 18.0% / 62.4% [8-29] | 18.7% / 60.9% [10-28] |
| K3.k3p | 2.7% / 42.7% [0-7] | 2.2% / 46.5% [0-5] | 2.4% / 44.6% [0-6] |
| K4 | 22.2% / 64.6% [10-35] | 20.2% / 66.5% [10-33] | 21.2% / 65.6% [11-32] |
| K5 | 7.5% / 61.9% [5-10] | 11.4% / 60.5% [8-15] | 9.4% / 61.2% [7-12] |

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.7% [3-3] | 1.4% [0-2] |
| K3.by3 | 3.3% / 14.6% [2-4] | 4.2% [4-4] | 3.7% / 9.4% [3-4] |
| K3.by4 | 4.0% / 15.3% [3-5] | 10.3% [5-20] | 7.2% / 12.8% [4-12] |
| K3.by5 | 15.9% / 27.2% [8-24] | 19.0% / 42.8% [7-31] | 17.4% / 35.0% [10-24] |
| K3.by6 | 16.3% / 27.6% [8-25] | 19.2% / 43.0% [7-31] | 17.7% / 35.3% [11-25] |
| K3.by7 | 24.8% / 47.1% [12-38] | 24.8% / 79.8% [7-48] | 24.8% / 63.5% [14-37] |
| K3.by8 | 24.9% / 61.0% [12-38] | 24.8% / 86.8% [7-48] | 24.8% / 73.9% [14-37] |
| K3.never | 39.0% / 75.1% [15-66] | 13.2% / 75.2% [0-31] | 26.1% / 75.2% [12-46] |
| K3.k0 | 3.7% / 39.8% [2-6] | 4.3% / 66.4% [3-6] | 4.0% / 53.1% [3-5] |
| K3.k1 | 0.8% / 37.0% [0-1] | 0.8% / 62.9% [1-1] | 0.8% / 49.9% [1-1] |
| K3.k2 | 18.4% / 54.5% [6-31] | 14.0% / 76.1% [0-26] | 16.2% / 65.3% [8-25] |
| K3.k3p | 2.0% / 38.1% [0-6] | 5.6% / 67.6% [0-17] | 3.8% / 52.9% [0-9] |
| K4 | 20.3% / 58.0% [7-34] | 19.6% / 85.8% [0-43] | 20.0% / 71.9% [9-33] |
| K5 | 7.9% / 54.3% [5-11] | 10.8% / 83.9% [7-13] | 9.3% / 69.1% [7-12] |

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.7% [2-3] | 1.3% [1-1] |
| K3.by3 | 3.8% [3-4] | 4.2% [4-5] | 4.0% [4-4] |
| K3.by4 | 5.5% [5-6] | 8.8% [7-11] | 7.1% [6-8] |
| K3.by5 | 12.8% [10-16] | 18.3% [15-21] | 15.5% [14-18] |
| K3.by6 | 27.5% [23-32] | 27.6% / 31.0% [24-31] | 27.5% / 29.2% [24-31] |
| K3.by7 | 40.3% / 43.4% [36-45] | 29.2% / 37.2% [25-33] | 34.8% / 40.3% [31-39] |
| K3.by8 | 42.2% / 49.3% [37-47] | 31.6% / 40.6% [28-36] | 36.9% / 45.0% [33-41] |
| K3.never | 50.7% / 57.8% [44-57] | 59.4% / 68.4% [52-65] | 55.0% / 63.1% [49-61] |
| K3.k0 | 4.8% / 11.9% [4-6] | 3.3% / 12.3% [3-4] | 4.1% / 12.1% [3-5] |
| K3.k1 | 0.7% / 7.8% [0-1] | 1.4% / 10.4% [1-2] | 1.0% / 9.1% [1-1] |
| K3.k2 | 34.2% / 41.4% [30-39] | 24.5% / 33.5% [21-28] | 29.4% / 37.4% [26-33] |
| K3.k3p | 2.5% / 9.6% [1-4] | 2.4% / 11.4% [1-4] | 2.4% / 10.5% [1-4] |
| K4 | 36.7% / 44.6% [32-41] | 26.9% / 36.5% [23-31] | 31.8% / 40.5% [28-36] |
| K5 | 9.0% / 22.1% [8-10] | 14.2% / 25.7% [13-16] | 11.6% / 23.9% [10-13] |

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by3 | 1.4% [1-2, Wilson] | 9.0% [8-10, Wilson] | 5.2% [5-6, Wilson] |
| K3.by4 | 17.3% [17-18, Wilson] | 11.8% [11-12, Wilson] | 14.6% [14-15, Wilson] |
| K3.by5 | 23.2% [22-24, Wilson] | 12.4% [12-13, Wilson] | 17.8% [17-18, Wilson] |
| K3.by6 | 25.3% [24-26, Wilson] | 12.4% [12-13, Wilson] | 18.8% [18-19, Wilson] |
| K3.by7 | 25.3% [24-26, Wilson] | 12.4% [12-13, Wilson] | 18.8% [18-19, Wilson] |
| K3.by8 | 25.3% [24-26, Wilson] | 12.4% [12-13, Wilson] | 18.8% [18-19, Wilson] |
| K3.never | 74.7% [74-76, Wilson] | 87.6% [87-88, Wilson] | 81.2% [81-82, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 1.4% [1-2, Wilson] | 1.9% [2-2, Wilson] | 1.6% [1-2, Wilson] |
| K3.k2 | 15.9% [15-17, Wilson] | 7.2% [7-8, Wilson] | 11.5% [11-12, Wilson] |
| K3.k3p | 8.0% [7-9, Wilson] | 3.4% [3-4, Wilson] | 5.7% [5-6, Wilson] |
| K4 | 23.9% [23-25, Wilson] | 10.5% [10-11, Wilson] | 17.2% [17-18, Wilson] |
| K5 | 22.5% [22-23, Wilson] | 30.8% [30-32, Wilson] | 26.6% [26-27, Wilson] |

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.7% [2-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.3% [4-5, Wilson] | 3.8% [3-4, Wilson] | 4.0% [4-4, Wilson] |
| K3.by4 | 5.0% [5-5, Wilson] | 19.4% [19-20, Wilson] | 12.2% [12-13, Wilson] |
| K3.by5 | 31.7% [31-33, Wilson] | 25.4% [25-26, Wilson] | 28.5% [28-29, Wilson] |
| K3.by6 | 40.6% [40-42, Wilson] | 27.6% [27-28, Wilson] | 34.1% [33-35, Wilson] |
| K3.by7 | 43.8% [43-45, Wilson] | 27.6% [27-28, Wilson] | 35.7% [35-36, Wilson] |
| K3.by8 | 43.8% [43-45, Wilson] | 27.6% [27-28, Wilson] | 35.7% [35-36, Wilson] |
| K3.never | 56.2% [55-57, Wilson] | 72.5% [72-73, Wilson] | 64.3% [64-65, Wilson] |
| K3.k0 | 4.3% [4-5, Wilson] | 2.7% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.k1 | 0.7% [1-1, Wilson] | 1.1% [1-1, Wilson] | 0.9% [1-1, Wilson] |
| K3.k2 | 26.7% [26-28, Wilson] | 15.6% [15-16, Wilson] | 21.2% [21-22, Wilson] |
| K3.k3p | 12.2% [12-13, Wilson] | 8.1% [8-9, Wilson] | 10.1% [10-11, Wilson] |
| K4 | 38.9% [38-40, Wilson] | 23.7% [23-25, Wilson] | 31.3% [31-32, Wilson] |
| K5 | 15.4% [15-16, Wilson] | 23.1% [22-24, Wilson] | 19.3% [19-20, Wilson] |

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.7% [2-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.3% [4-5, Wilson] | 3.8% [3-4, Wilson] | 4.0% [4-4, Wilson] |
| K3.by4 | 5.0% [5-5, Wilson] | 4.2% [4-5, Wilson] | 4.6% [4-5, Wilson] |
| K3.by5 | 5.2% [5-6, Wilson] | 29.7% [29-31, Wilson] | 17.4% [17-18, Wilson] |
| K3.by6 | 45.0% [44-46, Wilson] | 30.3% [29-31, Wilson] | 37.6% [37-38, Wilson] |
| K3.by7 | 45.4% [44-46, Wilson] | 45.6% [45-47, Wilson] | 45.5% [45-46, Wilson] |
| K3.by8 | 63.3% [62-64, Wilson] | 46.0% [45-47, Wilson] | 54.7% [54-55, Wilson] |
| K3.never | 36.7% [36-38, Wilson] | 54.0% [53-55, Wilson] | 45.3% [45-46, Wilson] |
| K3.k0 | 4.3% [4-5, Wilson] | 2.7% [2-3, Wilson] | 3.5% [3-4, Wilson] |
| K3.k1 | 0.9% [1-1, Wilson] | 1.5% [1-2, Wilson] | 1.2% [1-1, Wilson] |
| K3.k2 | 40.2% [39-41, Wilson] | 26.1% [25-27, Wilson] | 33.1% [32-34, Wilson] |
| K3.k3p | 18.0% [17-19, Wilson] | 15.7% [15-16, Wilson] | 16.9% [16-17, Wilson] |
| K4 | 58.2% [57-59, Wilson] | 41.8% [41-43, Wilson] | 50.0% [49-51, Wilson] |
| K5 | 9.5% [9-10, Wilson] | 14.5% [14-15, Wilson] | 12.0% [12-12, Wilson] |

## deck01 (card-list id 35d98d0dcaf2)

Changes: decks/dustin/01-muk-glimmora-kingambit-regigigas.txt

Exact, no simulation (SPEC "Exact part"):

- P0 (no Basic in the first 5 cards): 0.19369. Basics in the opening hand: 1: 0.634, 2: 0.293, 3 or more: 0.073.
- Chance of being the only Basic (forced Active): Alolan Grimer 0.12678, Glimmet 0.28291, Pawniard 0.12678, Regigigas 0.12678.
- In the opening hand: Pawniard 0.2887, Kingambit 0.2371, Alolan Grimer 0.2887, Alolan Muk 0.2371, Glimmet 0.5248, Glimmora 0.4289, Regigigas 0.2887, Poké Ball 0.4289, Rare Candy 0.2371.
- Pawniard, Kingambit and Rare Candy all seen in 7 cards: 0.03373; in 8 cards: 0.05246.
- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): Pawniard: 34/38/43/48/53%; Kingambit: 29/34/39/44/49%; Alolan Grimer: 34/38/43/48/53%; Alolan Muk: 29/34/39/44/49%; Glimmet: 59/65/70/75/80%; Glimmora: 51/58/64/70/76%; Regigigas: 34/38/43/48/53%; Poké Ball: 51/58/64/70/76%; Rare Candy: 29/34/39/44/49%.
- Energy by own turn N: N-1 going first, N going second. Kingambit's earliest attack: own turn 2 going second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.

Simulated, no knock-outs; 100,000 deals (deal i uses seed 24,700,000,000 + i; even i going first). Wilson 95% ranges.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard in play at setup | 29.2% (28.8-29.6) | 28.8% (28.4-29.2) | 29.0% (28.7-29.3) |
| K1 Pawniard line in play (end of own turn t), own turn 1 | 55.7% (55.3-56.1) | 55.4% (54.9-55.8) | 55.5% (55.2-55.8) |
| K1 Pawniard line in play (end of own turn t), own turn 2 | 67.9% (67.5-68.3) | 67.7% (67.3-68.1) | 67.8% (67.5-68.1) |
| K1 Pawniard line in play (end of own turn t), own turn 3 | 77.0% (76.6-77.3) | 76.6% (76.3-77.0) | 76.8% (76.5-77.1) |
| K1 Pawniard line in play (end of own turn t), own turn 4 | 84.6% (84.3-85.0) | 84.5% (84.2-84.8) | 84.6% (84.3-84.8) |
| K1 Pawniard line in play (end of own turn t), own turn 5 | 90.8% (90.5-91.0) | 90.7% (90.4-91.0) | 90.7% (90.6-90.9) |
| K2 Kingambit in play, own turn 2 | 11.1% (10.8-11.4) | 10.9% (10.6-11.2) | 11.0% (10.8-11.2) |
| K2 Kingambit in play, own turn 3 | 22.0% (21.7-22.4) | 21.7% (21.4-22.1) | 21.9% (21.6-22.1) |
| K2 Kingambit in play, own turn 4 | 36.1% (35.6-36.5) | 35.5% (35.1-35.9) | 35.8% (35.5-36.1) |
| K2 Kingambit in play, own turn 5 | 52.0% (51.6-52.4) | 51.7% (51.2-52.1) | 51.8% (51.5-52.1) |
| K2 Kingambit in play, own turn 6 | 68.2% (67.8-68.6) | 67.8% (67.4-68.2) | 68.0% (67.7-68.3) |
| K6 Muk and Regigigas both in play, own turn 3 | 24.5% (24.2-24.9) | 24.4% (24.0-24.8) | 24.5% (24.2-24.7) |
| K6 Muk and Regigigas both in play, own turn 4 | 33.2% (32.8-33.6) | 33.1% (32.7-33.5) | 33.2% (32.9-33.5) |
| K6 Muk and Regigigas both in play, own turn 5 | 39.9% (39.5-40.3) | 40.0% (39.5-40.4) | 39.9% (39.6-40.2) |
| G3 Pawniard in play, own turn 1 | 55.7% (55.3-56.1) | 55.4% (54.9-55.8) | 55.5% (55.2-55.8) |
| G3 Pawniard in play, own turn 2 | 56.8% (56.4-57.2) | 56.8% (56.3-57.2) | 56.8% (56.5-57.1) |
| G3 Pawniard in play, own turn 3 | 54.9% (54.5-55.4) | 54.9% (54.5-55.4) | 54.9% (54.6-55.2) |
| G3 Pawniard in play, own turn 4 | 48.6% (48.2-49.0) | 49.0% (48.5-49.4) | 48.8% (48.5-49.1) |
| G3 Pawniard in play, own turn 5 | 38.8% (38.4-39.2) | 39.0% (38.6-39.5) | 38.9% (38.6-39.2) |
| G3 Bisharp in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 2 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 3 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 4 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Bisharp in play, own turn 5 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Kingambit in play, own turn 2 | 11.1% (10.8-11.4) | 10.9% (10.6-11.2) | 11.0% (10.8-11.2) |
| G3 Kingambit in play, own turn 3 | 22.0% (21.7-22.4) | 21.7% (21.4-22.1) | 21.9% (21.6-22.1) |
| G3 Kingambit in play, own turn 4 | 36.1% (35.6-36.5) | 35.5% (35.1-35.9) | 35.8% (35.5-36.1) |
| G3 Kingambit in play, own turn 5 | 52.0% (51.6-52.4) | 51.7% (51.2-52.1) | 51.8% (51.5-52.1) |
| G3 Alolan Grimer in play, own turn 1 | 52.5% (52.1-52.9) | 52.5% (52.1-53.0) | 52.5% (52.2-52.8) |
| G3 Alolan Grimer in play, own turn 2 | 35.4% (35.0-35.8) | 35.5% (35.1-35.9) | 35.4% (35.2-35.7) |
| G3 Alolan Grimer in play, own turn 3 | 27.7% (27.3-28.1) | 27.9% (27.5-28.3) | 27.8% (27.5-28.1) |
| G3 Alolan Grimer in play, own turn 4 | 19.4% (19.1-19.8) | 19.8% (19.4-20.1) | 19.6% (19.4-19.9) |
| G3 Alolan Grimer in play, own turn 5 | 12.2% (11.9-12.4) | 12.4% (12.1-12.7) | 12.3% (12.1-12.5) |
| G3 Alolan Muk in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Alolan Muk in play, own turn 2 | 25.8% (25.4-26.1) | 25.7% (25.4-26.1) | 25.7% (25.5-26.0) |
| G3 Alolan Muk in play, own turn 3 | 38.5% (38.1-38.9) | 38.6% (38.1-39.0) | 38.5% (38.2-38.8) |
| G3 Alolan Muk in play, own turn 4 | 49.8% (49.4-50.2) | 49.7% (49.2-50.1) | 49.7% (49.4-50.1) |
| G3 Alolan Muk in play, own turn 5 | 58.7% (58.2-59.1) | 58.6% (58.2-59.1) | 58.7% (58.3-59.0) |
| G3 Glimmet in play, own turn 1 | 81.4% (81.0-81.7) | 81.5% (81.2-81.9) | 81.5% (81.2-81.7) |
| G3 Glimmet in play, own turn 2 | 49.7% (49.3-50.2) | 49.7% (49.3-50.2) | 49.7% (49.4-50.0) |
| G3 Glimmet in play, own turn 3 | 39.1% (38.6-39.5) | 39.0% (38.6-39.5) | 39.1% (38.8-39.4) |
| G3 Glimmet in play, own turn 4 | 27.9% (27.5-28.3) | 27.7% (27.3-28.1) | 27.8% (27.5-28.1) |
| G3 Glimmet in play, own turn 5 | 17.3% (17.0-17.6) | 17.4% (17.1-17.8) | 17.4% (17.1-17.6) |
| G3 Glimmora in play, own turn 1 | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) | 0.0% (0.0-0.0) |
| G3 Glimmora in play, own turn 2 | 61.2% (60.8-61.6) | 61.3% (60.9-61.7) | 61.3% (61.0-61.6) |
| G3 Glimmora in play, own turn 3 | 77.6% (77.3-78.0) | 77.9% (77.5-78.3) | 77.8% (77.5-78.0) |
| G3 Glimmora in play, own turn 4 | 88.2% (88.0-88.5) | 88.2% (87.9-88.5) | 88.2% (88.0-88.4) |
| G3 Glimmora in play, own turn 5 | 94.5% (94.3-94.7) | 94.3% (94.1-94.5) | 94.4% (94.3-94.6) |
| G3 Regigigas in play, own turn 1 | 54.3% (53.9-54.8) | 54.1% (53.7-54.5) | 54.2% (53.9-54.5) |
| G3 Regigigas in play, own turn 2 | 64.7% (64.2-65.1) | 64.3% (63.9-64.7) | 64.5% (64.2-64.8) |
| G3 Regigigas in play, own turn 3 | 71.0% (70.6-71.3) | 70.7% (70.3-71.1) | 70.8% (70.6-71.1) |
| G3 Regigigas in play, own turn 4 | 74.7% (74.3-75.0) | 74.5% (74.1-74.9) | 74.6% (74.3-74.9) |
| G3 Regigigas in play, own turn 5 | 76.7% (76.3-77.0) | 76.5% (76.1-76.8) | 76.6% (76.3-76.8) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | 77.0% (76.6-77.3) | 76.9% (76.6-77.3) | 77.0% (76.7-77.2) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 3 | 89.4% (89.2-89.7) | 89.7% (89.4-90.0) | 89.6% (89.4-89.7) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 4 | 95.7% (95.5-95.9) | 95.8% (95.7-96.0) | 95.8% (95.7-95.9) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 5 | 98.6% (98.5-98.7) | 98.6% (98.5-98.7) | 98.6% (98.5-98.7) |
| G4.s2 a Stage 2 in play, own turn 2 | 11.1% (10.8-11.4) | 10.9% (10.6-11.2) | 11.0% (10.8-11.2) |
| G4.s2 a Stage 2 in play, own turn 3 | 22.0% (21.7-22.4) | 21.7% (21.4-22.1) | 21.9% (21.6-22.1) |
| G4.s2 a Stage 2 in play, own turn 4 | 36.1% (35.6-36.5) | 35.5% (35.1-35.9) | 35.8% (35.5-36.1) |
| G4.s2 a Stage 2 in play, own turn 5 | 52.0% (51.6-52.4) | 51.7% (51.2-52.1) | 51.8% (51.5-52.1) |
| G5.any3 an empty own turn among turns 1-3 | 26.2% (25.8-26.5) | 26.3% (25.9-26.7) | 26.2% (26.0-26.5) |
| G6 Kingambit with [DD] attached, own turn 2 | 0.0% (0.0-0.0) | 10.9% (10.6-11.2) | 5.5% (5.3-5.6) |
| G6 Kingambit with [DD] attached, own turn 3 | 22.0% (21.7-22.4) | 21.7% (21.4-22.1) | 21.9% (21.6-22.1) |
| G6 Kingambit with [DD] attached, own turn 4 | 36.1% (35.6-36.5) | 35.5% (35.1-35.9) | 35.8% (35.5-36.1) |
| G6 Kingambit with [DD] attached, own turn 5 | 52.0% (51.6-52.4) | 51.7% (51.2-52.1) | 51.8% (51.5-52.1) |
| G5 mean empty own turns in turns 1-5 | 0.785 | 0.787 | 0.786 |

Clock measures under C-his (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.3% / 10.7% [2-3] | 1.2% / 5.3% [1-1] |
| K3.by3 | 3.4% / 12.0% [2-4] | 3.3% / 11.7% [3-4] | 3.3% / 11.8% [3-4] |
| K3.by4 | 4.3% / 13.0% [3-6] | 10.9% / 19.2% [7-15] | 7.6% / 16.1% [5-10] |
| K3.by5 | 17.4% / 26.0% [10-26] | 13.6% / 27.9% [8-20] | 15.5% / 27.0% [10-22] |
| K3.by6 | 21.4% / 35.4% [12-31] | 18.3% / 40.5% [11-26] | 19.9% / 38.0% [13-28] |
| K3.by7 | 27.9% / 49.8% [16-40] | 19.8% / 60.7% [12-29] | 23.8% / 55.2% [14-34] |
| K3.by8 | 29.4% / 69.0% [17-43] | 25.9% / 69.8% [15-39] | 27.7% / 69.4% [17-38] |
| K3.never | 31.0% / 70.6% [12-52] | 30.2% / 74.1% [13-48] | 30.6% / 72.3% [13-50] |
| K3.k0 | 4.4% / 44.0% [3-6] | 3.1% / 47.0% [2-5] | 3.8% / 45.5% [2-5] |
| K3.k1 | 0.4% / 40.0% [0-1] | 1.0% / 44.8% [1-1] | 0.7% / 42.4% [0-1] |
| K3.k2 | 21.7% / 61.3% [11-33] | 19.3% / 63.1% [9-31] | 20.5% / 62.2% [11-30] |
| K3.k3p | 2.9% / 42.4% [0-7] | 2.5% / 46.4% [0-6] | 2.7% / 44.4% [0-7] |
| K4 | 24.6% / 66.7% [12-38] | 21.8% / 67.8% [11-35] | 23.2% / 67.2% [12-34] |
| K5 | 7.9% / 62.4% [6-10] | 11.1% / 61.2% [8-15] | 9.5% / 61.8% [7-12] |

Flagged differences from the base under C-his (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by6: +1.1 points (+0.1 to +2.1); K3.by7: +1.5 points (+0.6 to +2.4); K3.by8: +1.7 points (+0.9 to +2.5); K3.never: -1.2 points (-1.9 to -0.6); K3.k2: +1.8 points (+1.0 to +2.5); K4: +2.0 points (+1.1 to +3.1).

Clock measures under C-his, seat-matched (20,000 deals, 12 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.8% [3-3] | 1.4% [0-2] |
| K3.by3 | 3.2% / 14.5% [2-4] | 4.2% [4-4] | 3.7% / 9.4% [3-4] |
| K3.by4 | 4.0% / 15.3% [2-6] | 10.7% [5-22] | 7.3% / 13.0% [4-13] |
| K3.by5 | 17.3% / 28.6% [8-27] | 20.6% / 43.8% [6-34] | 18.9% / 36.2% [11-27] |
| K3.by6 | 17.7% / 29.0% [8-27] | 20.8% / 44.0% [6-35] | 19.2% / 36.5% [11-27] |
| K3.by7 | 25.9% / 48.2% [12-40] | 26.9% / 81.4% [6-53] | 26.4% / 64.8% [14-40] |
| K3.by8 | 26.0% / 61.8% [12-40] | 26.9% / 87.4% [6-53] | 26.4% / 74.6% [14-40] |
| K3.never | 38.2% / 74.0% [14-65] | 12.6% / 73.1% [0-29] | 25.4% / 73.6% [12-46] |
| K3.k0 | 3.9% / 39.8% [2-6] | 4.4% / 64.9% [3-6] | 4.2% / 52.3% [3-5] |
| K3.k1 | 0.5% / 36.3% [0-1] | 0.7% / 61.2% [0-1] | 0.6% / 48.7% [0-1] |
| K3.k2 | 19.8% / 55.6% [7-33] | 15.7% / 76.2% [0-30] | 17.8% / 65.9% [9-28] |
| K3.k3p | 1.8% / 37.6% [0-5] | 6.1% / 66.6% [0-18] | 3.9% / 52.1% [0-10] |
| K4 | 21.6% / 59.2% [8-36] | 21.8% / 86.6% [0-49] | 21.7% / 72.9% [9-36] |
| K5 | 8.4% / 54.7% [5-11] | 10.1% / 84.7% [7-12] | 9.2% / 69.7% [7-11] |

Flagged differences from the base under C-his, seat-matched (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by5: +1.5 points (+0.3 to +2.6); K3.by6: +1.5 points (+0.4 to +2.6); K3.by7: +1.7 points (+0.3 to +3.1); K3.by8: +1.6 points (+0.3 to +3.0); K3.k2: +1.6 points (+0.5 to +2.8); K4: +1.7 points (+0.5 to +3.2).

Clock measures under C-bot (20,000 deals, 64 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0] | 2.6% [2-3] | 1.3% [1-1] |
| K3.by3 | 3.8% [3-4] | 4.3% [4-5] | 4.0% [4-4] |
| K3.by4 | 5.9% [5-7] | 9.7% [8-12] | 7.8% [7-9] |
| K3.by5 | 14.2% [11-18] | 19.6% [17-23] | 16.9% [15-19] |
| K3.by6 | 30.5% [26-35] | 30.1% / 33.4% [27-34] | 30.3% / 32.0% [27-34] |
| K3.by7 | 44.2% / 47.3% [39-49] | 32.1% / 39.6% [28-36] | 38.2% / 43.4% [34-42] |
| K3.by8 | 45.8% / 52.5% [41-51] | 34.5% / 42.8% [30-39] | 40.1% / 47.7% [36-44] |
| K3.never | 47.5% / 54.2% [41-54] | 57.2% / 65.5% [50-63] | 52.3% / 59.9% [46-58] |
| K3.k0 | 4.9% / 11.6% [4-6] | 3.4% / 11.8% [3-4] | 4.2% / 11.7% [4-5] |
| K3.k1 | 0.7% / 7.4% [0-1] | 1.1% / 9.5% [1-1] | 0.9% / 8.4% [1-1] |
| K3.k2 | 38.1% / 44.9% [34-43] | 27.5% / 35.9% [24-32] | 32.8% / 40.4% [29-37] |
| K3.k3p | 2.1% / 8.8% [1-3] | 2.4% / 10.8% [1-4] | 2.2% / 9.8% [1-3] |
| K4 | 40.2% / 47.8% [35-45] | 29.9% / 39.0% [26-34] | 35.1% / 43.4% [31-39] |
| K5 | 9.0% / 22.4% [8-10] | 12.8% / 24.3% [12-14] | 10.9% / 23.4% [10-12] |

Flagged differences from the base under C-bot (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by5: +1.4 points (+0.6 to +2.2); K3.by6: +2.8 points (+1.9 to +3.6); K3.by7: +3.4 points (+2.4 to +4.3); K3.by8: +3.3 points (+2.4 to +4.1); K3.never: -2.7 points (-3.6 to -1.8); K3.k2: +3.4 points (+2.6 to +4.2); K4: +3.2 points (+2.3 to +4.1).

Clock measures under C-fixed fast (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 1.9% [2-2, Wilson] | 0.9% [1-1, Wilson] |
| K3.by3 | 1.1% [1-1, Wilson] | 9.8% [9-10, Wilson] | 5.4% [5-6, Wilson] |
| K3.by4 | 19.1% [18-20, Wilson] | 13.3% [13-14, Wilson] | 16.2% [16-17, Wilson] |
| K3.by5 | 27.0% [26-28, Wilson] | 14.0% [13-15, Wilson] | 20.5% [20-21, Wilson] |
| K3.by6 | 29.4% [29-30, Wilson] | 14.0% [13-15, Wilson] | 21.7% [21-22, Wilson] |
| K3.by7 | 29.4% [29-30, Wilson] | 14.0% [13-15, Wilson] | 21.7% [21-22, Wilson] |
| K3.by8 | 29.4% [29-30, Wilson] | 14.0% [13-15, Wilson] | 21.7% [21-22, Wilson] |
| K3.never | 70.6% [70-71, Wilson] | 86.0% [85-87, Wilson] | 78.3% [78-79, Wilson] |
| K3.k0 | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] | 0.0% [0-0, Wilson] |
| K3.k1 | 1.1% [1-1, Wilson] | 1.9% [2-2, Wilson] | 1.5% [1-2, Wilson] |
| K3.k2 | 18.0% [17-19, Wilson] | 7.9% [7-8, Wilson] | 12.9% [12-13, Wilson] |
| K3.k3p | 10.3% [10-11, Wilson] | 4.2% [4-5, Wilson] | 7.3% [7-8, Wilson] |
| K4 | 28.3% [27-29, Wilson] | 12.1% [11-13, Wilson] | 20.2% [20-21, Wilson] |
| K5 | 20.5% [20-21, Wilson] | 29.7% [29-31, Wilson] | 25.1% [25-26, Wilson] |

Flagged differences from the base under C-fixed fast (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by4: +1.6 points (+0.9 to +2.3); K3.by5: +2.6 points (+1.9 to +3.4); K3.by6: +2.9 points (+2.1 to +3.6); K3.by7: +2.9 points (+2.1 to +3.6); K3.by8: +2.9 points (+2.1 to +3.6); K3.never: -2.9 points (-3.6 to -2.1); K3.k2: +1.4 points (+0.8 to +2.1); K3.k3p: +1.6 points (+1.1 to +2.1); K4: +3.0 points (+2.3 to +3.8); K5: -1.5 points (-2.4 to -0.7).

Clock measures under C-fixed medium (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.8% [3-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.3% [4-5, Wilson] | 4.0% [4-4, Wilson] | 4.1% [4-4, Wilson] |
| K3.by4 | 4.9% [4-5, Wilson] | 21.9% [21-23, Wilson] | 13.4% [13-14, Wilson] |
| K3.by5 | 35.4% [34-36, Wilson] | 29.5% [29-30, Wilson] | 32.5% [32-33, Wilson] |
| K3.by6 | 45.3% [44-46, Wilson] | 32.0% [31-33, Wilson] | 38.6% [38-39, Wilson] |
| K3.by7 | 48.1% [47-49, Wilson] | 32.0% [31-33, Wilson] | 40.0% [39-41, Wilson] |
| K3.by8 | 48.1% [47-49, Wilson] | 32.0% [31-33, Wilson] | 40.0% [39-41, Wilson] |
| K3.never | 51.9% [51-53, Wilson] | 68.0% [67-69, Wilson] | 60.0% [59-61, Wilson] |
| K3.k0 | 4.3% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.6% [3-4, Wilson] |
| K3.k1 | 0.6% [0-1, Wilson] | 1.1% [1-1, Wilson] | 0.9% [1-1, Wilson] |
| K3.k2 | 30.5% [30-31, Wilson] | 17.9% [17-19, Wilson] | 24.2% [24-25, Wilson] |
| K3.k3p | 12.7% [12-13, Wilson] | 10.1% [9-11, Wilson] | 11.4% [11-12, Wilson] |
| K4 | 43.2% [42-44, Wilson] | 28.0% [27-29, Wilson] | 35.6% [35-36, Wilson] |
| K5 | 14.5% [14-15, Wilson] | 21.2% [20-22, Wilson] | 17.9% [17-18, Wilson] |

Flagged differences from the base under C-fixed medium (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by4: +1.2 points (+0.6 to +1.8); K3.by5: +3.9 points (+3.0 to +4.8); K3.by6: +4.5 points (+3.6 to +5.4); K3.by7: +4.3 points (+3.4 to +5.3); K3.by8: +4.3 points (+3.4 to +5.3); K3.never: -4.3 points (-5.3 to -3.4); K3.k2: +3.1 points (+2.3 to +3.9); K3.k3p: +1.2 points (+0.7 to +1.8); K4: +4.3 points (+3.4 to +5.2); K5: -1.4 points (-2.2 to -0.7).

Clock measures under C-fixed slow (20,000 deals, 1 recorded game(s) sampled by the deal alone). Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.

| Measure | going first | going second | pooled |
|---|---|---|---|
| K3.by2 | 0.0% [0-0, Wilson] | 2.8% [3-3, Wilson] | 1.4% [1-2, Wilson] |
| K3.by3 | 4.3% [4-5, Wilson] | 4.0% [4-4, Wilson] | 4.1% [4-4, Wilson] |
| K3.by4 | 4.9% [4-5, Wilson] | 4.2% [4-5, Wilson] | 4.6% [4-5, Wilson] |
| K3.by5 | 5.0% [5-5, Wilson] | 33.3% [32-34, Wilson] | 19.2% [19-20, Wilson] |
| K3.by6 | 49.4% [48-50, Wilson] | 33.7% [33-35, Wilson] | 41.5% [41-42, Wilson] |
| K3.by7 | 49.6% [49-51, Wilson] | 50.5% [50-51, Wilson] | 50.0% [49-51, Wilson] |
| K3.by8 | 65.7% [65-67, Wilson] | 50.8% [50-52, Wilson] | 58.3% [58-59, Wilson] |
| K3.never | 34.3% [33-35, Wilson] | 49.2% [48-50, Wilson] | 41.7% [41-42, Wilson] |
| K3.k0 | 4.3% [4-5, Wilson] | 2.8% [3-3, Wilson] | 3.6% [3-4, Wilson] |
| K3.k1 | 0.8% [1-1, Wilson] | 1.4% [1-2, Wilson] | 1.1% [1-1, Wilson] |
| K3.k2 | 44.5% [44-45, Wilson] | 29.5% [29-30, Wilson] | 37.0% [36-38, Wilson] |
| K3.k3p | 16.2% [15-17, Wilson] | 17.1% [16-18, Wilson] | 16.6% [16-17, Wilson] |
| K4 | 60.7% [60-62, Wilson] | 46.6% [46-48, Wilson] | 53.6% [53-54, Wilson] |
| K5 | 10.1% [9-11, Wilson] | 13.6% [13-14, Wilson] | 11.8% [11-12, Wilson] |

Flagged differences from the base under C-fixed slow (pooled; bootstrap range over the recorded games, undecided counted as no): K3.by5: +1.7 points (+1.0 to +2.4); K3.by6: +3.9 points (+2.9 to +4.8); K3.by7: +4.6 points (+3.6 to +5.5); K3.by8: +3.6 points (+2.7 to +4.5); K3.never: -3.6 points (-4.5 to -2.7); K3.k2: +3.9 points (+3.0 to +4.8); K4: +3.7 points (+2.7 to +4.6).

Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); "flag" when the range excludes 0 and the difference is at least 1 point):

| Measure | going first | going second | pooled |
|---|---|---|---|
| K1 Pawniard line in play (end of own turn t), own turn 2 | +1.1 (+0.6 to +1.7) FLAG | +1.1 (+0.5 to +1.7) FLAG | +1.1 (+0.7 to +1.5) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 3 | +1.3 (+0.8 to +1.8) FLAG | +1.0 (+0.5 to +1.6) FLAG | +1.2 (+0.8 to +1.5) FLAG |
| K1 Pawniard line in play (end of own turn t), own turn 4 | +1.0 (+0.6 to +1.5) FLAG | +0.9 (+0.5 to +1.4) | +1.0 (+0.7 to +1.3) |
| K2 Kingambit in play, own turn 3 | +2.3 (+1.8 to +2.8) FLAG | +2.0 (+1.5 to +2.5) FLAG | +2.1 (+1.8 to +2.5) FLAG |
| K2 Kingambit in play, own turn 4 | +4.1 (+3.5 to +4.7) FLAG | +3.3 (+2.7 to +3.9) FLAG | +3.7 (+3.3 to +4.1) FLAG |
| K2 Kingambit in play, own turn 5 | +4.6 (+3.9 to +5.2) FLAG | +4.1 (+3.5 to +4.7) FLAG | +4.3 (+3.9 to +4.8) FLAG |
| K2 Kingambit in play, own turn 6 | +4.4 (+3.8 to +4.9) FLAG | +3.7 (+3.2 to +4.3) FLAG | +4.1 (+3.6 to +4.5) FLAG |
| K6 Muk and Regigigas both in play, own turn 3 | +1.9 (+1.4 to +2.4) FLAG | +1.7 (+1.2 to +2.2) FLAG | +1.8 (+1.4 to +2.2) FLAG |
| K6 Muk and Regigigas both in play, own turn 4 | +2.4 (+1.8 to +3.0) FLAG | +1.9 (+1.3 to +2.4) FLAG | +2.1 (+1.7 to +2.5) FLAG |
| K6 Muk and Regigigas both in play, own turn 5 | +2.0 (+1.4 to +2.6) FLAG | +1.7 (+1.1 to +2.3) FLAG | +1.8 (+1.4 to +2.3) FLAG |
| G3 Pawniard in play, own turn 4 | -3.1 (-3.7 to -2.4) FLAG | -2.4 (-3.0 to -1.8) FLAG | -2.7 (-3.2 to -2.3) FLAG |
| G3 Pawniard in play, own turn 5 | -3.8 (-4.4 to -3.2) FLAG | -3.5 (-4.1 to -2.9) FLAG | -3.7 (-4.1 to -3.2) FLAG |
| G3 Kingambit in play, own turn 3 | +2.3 (+1.8 to +2.8) FLAG | +2.0 (+1.5 to +2.5) FLAG | +2.1 (+1.8 to +2.5) FLAG |
| G3 Kingambit in play, own turn 4 | +4.1 (+3.5 to +4.7) FLAG | +3.3 (+2.7 to +3.9) FLAG | +3.7 (+3.3 to +4.1) FLAG |
| G3 Kingambit in play, own turn 5 | +4.6 (+3.9 to +5.2) FLAG | +4.1 (+3.5 to +4.7) FLAG | +4.3 (+3.9 to +4.8) FLAG |
| G3 Alolan Grimer in play, own turn 3 | -1.3 (-1.8 to -0.7) FLAG | -1.2 (-1.8 to -0.7) FLAG | -1.3 (-1.7 to -0.9) FLAG |
| G3 Alolan Grimer in play, own turn 4 | -2.2 (-2.7 to -1.7) FLAG | -1.6 (-2.1 to -1.1) FLAG | -1.9 (-2.2 to -1.5) FLAG |
| G3 Alolan Grimer in play, own turn 5 | -2.0 (-2.5 to -1.6) FLAG | -1.8 (-2.2 to -1.4) FLAG | -1.9 (-2.2 to -1.6) FLAG |
| G3 Alolan Muk in play, own turn 3 | +1.9 (+1.2 to +2.5) FLAG | +1.8 (+1.2 to +2.4) FLAG | +1.8 (+1.4 to +2.3) FLAG |
| G3 Alolan Muk in play, own turn 4 | +2.5 (+1.9 to +3.1) FLAG | +2.0 (+1.3 to +2.6) FLAG | +2.2 (+1.8 to +2.7) FLAG |
| G3 Alolan Muk in play, own turn 5 | +2.1 (+1.5 to +2.7) FLAG | +1.9 (+1.3 to +2.5) FLAG | +2.0 (+1.6 to +2.5) FLAG |
| G3 Glimmet in play, own turn 3 | -1.8 (-2.4 to -1.2) FLAG | -1.7 (-2.3 to -1.1) FLAG | -1.8 (-2.2 to -1.3) FLAG |
| G3 Glimmet in play, own turn 4 | -3.0 (-3.6 to -2.4) FLAG | -3.2 (-3.8 to -2.6) FLAG | -3.1 (-3.5 to -2.7) FLAG |
| G3 Glimmet in play, own turn 5 | -3.4 (-3.9 to -2.9) FLAG | -3.4 (-3.9 to -3.0) FLAG | -3.4 (-3.8 to -3.1) FLAG |
| G3 Glimmora in play, own turn 2 | +1.5 (+0.9 to +2.2) FLAG | +1.2 (+0.5 to +1.8) FLAG | +1.3 (+0.9 to +1.8) FLAG |
| G3 Glimmora in play, own turn 3 | +2.2 (+1.7 to +2.7) FLAG | +2.2 (+1.7 to +2.7) FLAG | +2.2 (+1.8 to +2.6) FLAG |
| G3 Glimmora in play, own turn 4 | +2.1 (+1.6 to +2.5) FLAG | +2.0 (+1.5 to +2.4) FLAG | +2.0 (+1.7 to +2.3) FLAG |
| G3 Glimmora in play, own turn 5 | +1.5 (+1.2 to +1.8) FLAG | +1.2 (+0.9 to +1.5) FLAG | +1.4 (+1.1 to +1.6) FLAG |
| G3 Regigigas in play, own turn 2 | +1.0 (+0.5 to +1.6) FLAG | +0.7 (+0.1 to +1.3) | +0.9 (+0.5 to +1.3) |
| G3 Regigigas in play, own turn 3 | +1.4 (+0.8 to +2.0) FLAG | +1.1 (+0.5 to +1.6) FLAG | +1.2 (+0.8 to +1.6) FLAG |
| G3 Regigigas in play, own turn 4 | +1.2 (+0.6 to +1.7) FLAG | +0.8 (+0.3 to +1.3) | +1.0 (+0.6 to +1.4) |
| G4.s1 a Stage 1 or Stage 2 in play, own turn 2 | +1.1 (+0.6 to +1.6) FLAG | +0.6 (+0.1 to +1.2) | +0.9 (+0.5 to +1.2) |
| G4.s2 a Stage 2 in play, own turn 3 | +2.3 (+1.8 to +2.8) FLAG | +2.0 (+1.5 to +2.5) FLAG | +2.1 (+1.8 to +2.5) FLAG |
| G4.s2 a Stage 2 in play, own turn 4 | +4.1 (+3.5 to +4.7) FLAG | +3.3 (+2.7 to +3.9) FLAG | +3.7 (+3.3 to +4.1) FLAG |
| G4.s2 a Stage 2 in play, own turn 5 | +4.6 (+3.9 to +5.2) FLAG | +4.1 (+3.5 to +4.7) FLAG | +4.3 (+3.9 to +4.8) FLAG |
| G5.any3 an empty own turn among turns 1-3 | -2.7 (-3.2 to -2.1) FLAG | -2.5 (-3.0 to -1.9) FLAG | -2.6 (-3.0 to -2.2) FLAG |
| G6 Kingambit with [DD] attached, own turn 3 | +2.3 (+1.8 to +2.8) FLAG | +2.0 (+1.5 to +2.5) FLAG | +2.1 (+1.8 to +2.5) FLAG |
| G6 Kingambit with [DD] attached, own turn 4 | +4.1 (+3.5 to +4.7) FLAG | +3.3 (+2.7 to +3.9) FLAG | +3.7 (+3.3 to +4.1) FLAG |
| G6 Kingambit with [DD] attached, own turn 5 | +4.6 (+3.9 to +5.2) FLAG | +4.1 (+3.5 to +4.7) FLAG | +4.3 (+3.9 to +4.8) FLAG |
| G5 mean empty own turns (turns 1-5) | pooled -0.024 (-0.031 to -0.016) | | |

Only flagged rows are shown above; the full differences are in results.json.

**Plain summary, deck01.**

Gains (flagged, pooled): K1 Pawniard line in play (end of own turn t), own turn 2 +1.1 points; K1 Pawniard line in play (end of own turn t), own turn 3 +1.2 points; K2 Kingambit in play, own turn 3 +2.1 points; K2 Kingambit in play, own turn 4 +3.7 points; K2 Kingambit in play, own turn 5 +4.3 points; K2 Kingambit in play, own turn 6 +4.1 points; K6 Muk and Regigigas both in play, own turn 3 +1.8 points; K6 Muk and Regigigas both in play, own turn 4 +2.1 points; K6 Muk and Regigigas both in play, own turn 5 +1.8 points; G3 Kingambit in play, own turn 3 +2.1 points.
Gives up (flagged, pooled): G3 Pawniard in play, own turn 4 -2.7 points; G3 Pawniard in play, own turn 5 -3.7 points; G3 Alolan Grimer in play, own turn 3 -1.3 points; G3 Alolan Grimer in play, own turn 4 -1.9 points; G3 Alolan Grimer in play, own turn 5 -1.9 points; G3 Glimmet in play, own turn 3 -1.8 points; G3 Glimmet in play, own turn 4 -3.1 points; G3 Glimmet in play, own turn 5 -3.4 points.
Not valued here (changed cards the script never plays: they count as blanks): Lucky Ice Pop.
Clocks used: C-his, C-his, seat-matched, C-bot, C-fixed fast, C-fixed medium, C-fixed slow (Copycat draws 4 under every clock).

## Against lib/consistency.py on deck 01 (SPEC test 6)

Kingambit in play by own turn t, going first, deck 01, no clock. Gaps are explained by named differences in the script; a gap is not a failure.

| Own turn | this tester | lib/consistency.py solitaire | gap | named difference |
|---|---|---|---|---|
| 2 | 11.1% | 8.1% | +3.0 | +1.6 points of the +3.0 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +1.4 is Copycat and Supporter policy: the script plays Copycat when the hand holds no Kingambit or Rare Candy and is smaller than the opponent's, the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -0.6 from it) |
| 3 | 22.4% | 15.0% | +7.4 | +4.5 points of the +7.4 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +2.9 is Copycat and Supporter policy: the script plays Copycat when the hand holds no Kingambit or Rare Candy and is smaller than the opponent's, the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -2.0 from it) |
| 4 | 36.5% | 23.4% | +13.2 | +8.8 points of the +13.2 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +4.3 is Copycat and Supporter policy: the script plays Copycat when the hand holds no Kingambit or Rare Candy and is smaller than the opponent's, the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -3.5 from it) |
| 5 | 52.5% | 33.7% | +18.8 | +14.0 points of the +18.8 gap is Mesagoza: lib/consistency.py's note on it is 'ignored: not a draw, search, evolution or Energy effect', so the solitaire model never uses it, while this script plays it and flips each turn (measured by forcing the coin to tails); the remaining +4.7 is Copycat and Supporter policy: the script plays Copycat when the hand holds no Kingambit or Rare Candy and is smaller than the opponent's, the solitaire model only when it holds no card the plan needs (with Copycat never played the script is -5.2 from it) |

## Against the bots (SPEC test 7)

Deck 01, C-bot clock, 20,000 deals: the share of deals whose first Overlord's Blade is on own turn t, beside the first Overlord's Blade turn in the 64 recorded games (km3 and kx3 against km3 on the 8 panel lists, replay_b). A gap is printed, not a failure: the tester plays a fixed script and the bots do not.

| First Blade on own turn | this tester | the 64 bot games |
|---|---|---|
| 2 | 1.3% | 0 of 64 (0%) |
| 3 | 2.7% | 0 of 64 (0%) |
| 4 | 3.8% | 1 of 64 (2%) |
| 5 | 9.1% | 3 of 64 (5%) |
| 6 | 13.4% | 8 of 64 (12%) |
| 7 | 7.9% | 6 of 64 (9%) |
| 8 | 2.1% | 0 of 64 (0%) |
| 9 | 0.0% | 3 of 64 (5%) |
| 11 | 0.0% | 1 of 64 (2%) |
| never in the horizon | 59.7% | 42 of 64 (66%) |

## How much each confirmable choice matters (on the base list)

One alternative of each value Dustin confirms, run once on the base list on the same deals. Pooled, paired differences from the default (percentage points; the range is +-1.96 sd/sqrt(n); a "*" marks a range that excludes 0 and a difference of at least 1 point). Only measures a choice can touch are listed.

| Alternative | K1.t1 | K1.t3 | K2.t2 | K2.t3 | K2.t4 | K2.t5 | K6.t4 | G5.any3 | G6.t3 | G6.t5 |
|---|---|---|---|---|---|---|---|---|---|---|
| lead order: Pawniard first | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | -2.0* | -0.1 | +0.0 | +0.0 |
| promote order: Regigigas first | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Copycat whenever no Kingambit or Rare Candy is in hand | +0.2 | +0.4 | +0.1 | +0.2 | +0.5 | +0.7 | +0.4 | -1.0* | +0.2 | +0.7 |
| Blade target 3 (the 180 line) | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 | +0.0 |
| Poke Ball over names, not cards | +1.2* | +0.9 | +0.2 | +0.3 | +0.2 | -0.0 | +0.8 | +0.0 | +0.3 | -0.0 |
| opponent hand 2 (Copycat) | -1.3* | -1.9* | -1.1* | -2.8* | -4.3* | -5.5* | -2.7* | +3.2* | -2.8* | -5.5* |
| opponent hand 6 (Copycat) | +0.9 | +1.5* | +1.7* | +4.2* | +5.5* | +5.5* | +2.2* | -1.7* | +4.2* | +5.5* |

Clock measures under C-his, difference from the default (pooled points, undecided as no):

| Alternative | K3.by3 | K3.by5 | K3.never | K4 | K5 |
|---|---|---|---|---|---|
| lead order: Pawniard first | +2.6* | +0.8 | +1.3* | -4.8* | +10.4* |
| promote order: Regigigas first | +0.0 | +0.0 | +0.6 | -0.3 | +0.0 |
| Copycat whenever no Kingambit or Rare Candy is in hand | +0.1 | +0.1 | -0.2 | +0.3 | -0.1 |
| Blade target 3 (the 180 line) | +0.0 | -8.5* | +9.7* | -16.3* | +0.0 |
| Poke Ball over names, not cards | -0.0 | -0.0 | -0.1 | +0.1 | +0.2 |
| opponent hand 2 (Copycat) | -0.2 | -1.5* | +1.8* | -2.5* | +0.7 |
| opponent hand 6 (Copycat) | +0.3 | +2.4* | -1.6* | +2.6* | -0.5 |

Clock measures under C-bot, difference from the default (pooled points, undecided as no):

| Alternative | K3.by3 | K3.by5 | K3.never | K4 | K5 |
|---|---|---|---|---|---|
| lead order: Pawniard first | +2.9* | +1.1* | +2.7* | -6.7* | +11.0* |
| promote order: Regigigas first | +0.0 | -0.0 | +0.4 | -0.2 | +0.0 |
| Copycat whenever no Kingambit or Rare Candy is in hand | +0.1 | +0.2 | -0.5 | +0.5 | -0.3 |
| Blade target 3 (the 180 line) | -0.1 | -8.7* | +19.6* | -24.3* | +0.0 |
| Poke Ball over names, not cards | +0.0 | +0.2 | -0.3 | +0.1 | +0.1 |
| opponent hand 2 (Copycat) | -0.3 | -1.8* | +3.6* | -3.7* | +1.0* |
| opponent hand 6 (Copycat) | +0.5 | +2.5* | -3.6* | +3.8* | -0.7 |

Clock measures under C-fixed fast, difference from the default (pooled points, undecided as no):

| Alternative | K3.by3 | K3.by5 | K3.never | K4 | K5 |
|---|---|---|---|---|---|
| lead order: Pawniard first | -1.5* | -4.6* | +4.8* | -4.3* | +10.1* |
| promote order: Regigigas first | +0.0 | -0.4 | +0.4 | -0.4 | +0.1 |
| Copycat whenever no Kingambit or Rare Candy is in hand | +0.0 | +0.2 | -0.2 | +0.2 | -0.2 |
| Blade target 3 (the 180 line) | -1.9* | -4.2* | +4.2* | -7.6* | +0.0 |
| Poke Ball over names, not cards | +0.1 | +0.4 | -0.3 | +0.1 | +0.3 |
| opponent hand 2 (Copycat) | -0.4 | -2.6* | +2.8* | -2.9* | +2.2* |
| opponent hand 6 (Copycat) | +0.7 | +3.7* | -3.8* | +3.8* | -1.3* |

## The run record

- **code sha256**: d67307200c3c6d723a76697756d9e8a5160dfc34d31dc56d84c60c58565b86dc
- **engine commit**: pinned rules-switch-2 engine, main 70319c3d (engine unchanged since c045ede); no engine program is run
- **seeds**: 24,700,000,000 + deal index i (deal i is the same in every version and under every clock); 100,000 deals with no knock-outs, 20,000 deals per clock
- **clock sources**: C-his: rl/results/pause_games_new_2026-10-13/v2/positions_all.json (12 Kingambit games); C-bot: rl/results/kx3_on_rules2_2026-10/replay_b/games.jsonl (64 deck-01 rows); C-fixed: fast, medium, slow (SPEC)
- **base list**: rl/results/pause_games_new_2026-10-13/decks/KW261012_203719000.txt (card-list id 73dfed58d1d6)
- **plan config**: /home/dacz8976/credit_work/tools/rl/setup_tester/plans/kingambit.json
- **plan overrides**: none
- **wall time**: 382 s, 1 process(es) (comparisons and the choice runs included)
- **speed**: 5,843 deals per second per process (440,000 deals in 75 s of version time)

