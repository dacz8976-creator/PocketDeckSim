# Draft A v the Fire list, the Wallace addendum: results

Written by `analyze_wallace.py report` from `wallace/games/*.jsonl`, `wallace/coverage/wallace_coverage.json` and the main test's recorded `games/*.jsonl` (draft A and deck 13, the same deals). Every definition is the README's (sections 6 and 7) or ADDENDUM_WALLACE.md's. **Not a ranking and not a ladder forecast**: one list against one saved opponent list, both sides played by the km3 bot.

**Readings (ADDENDUM_WALLACE.md section 7):**
- Against draft A: the Wallace version beat the Fire list more often than draft A did on the same deals, by more than the paired interval. Paired difference, the Wallace version minus draft A: +6.8 points (95% interval +4.2 to +9.4).
- Against deck 13: deck 13 beat the Fire list more often than the Wallace version did on the same deals, by more than the paired interval. Paired difference, the Wallace version minus deck 13: -4.1 points (95% interval -8.1 to -0.1). The point difference is under 5 points, the size START_HERE calls noise for two versions of one shell (for scale only; the reading is the registered one).

Secondary, descriptive: the Wallace version's win rate against this list is above 50% (58.5%, 55.4-61.5%).

Beside the readings (descriptive; the tables below):
- Wallace was played in 435 = 43.5% of the Wallace version's games; a Wallace made Mega Sharpedo ex by own turn 2 in 296 = 29.6% (by own turn 1: 177 = 17.7%).
- Mega Sharpedo ex in play by own turn 2, by an Evolve or Wallace (L1w): Wallace version 643 = 64.3%; draft A 498 = 49.8%.
- Turbo Shark as the attack of own turn 2 (L2): Wallace version 242 = 24.2%; draft A 189 = 18.9%. The plan's line: Wallace version 19 = 1.9%; draft A 17 = 1.7%.

## Win rates (draws are not wins)

| list | games | wins | draws | win rate | 95% interval (Wilson) |
|---|---|---|---|---|---|
| the Wallace version of draft A (1 Misty -> 1 Wallace) | 1000 | 585 | 8 | 58.5% | 55.4-61.5% |
| draft A (Shark Tempo) | 1000 | 517 | 5 | 51.7% | 48.6-54.8% |
| deck 13 (Alolan Ninetales / Raticate) | 1000 | 626 | 0 | 62.6% | 59.6-65.5% |

Draft A's and deck 13's rows are the main test's recorded games (its RESULTS.md), not new games.

## Paired difference: the Wallace version minus draft A (per deal: same seed, same seat)

- Deals played by both: 1000. Difference per deal = (the Wallace version won) - (draft A won), each 1 or 0.
- Mean: +6.80 points; standard deviation of the per-deal differences 0.4118; 95% interval +4.25 to +9.35 points (mean +- 1.96 x sd / sqrt(n)).
- Both won: 464. The Wallace version won and draft A did not: 121. draft A won and the Wallace version did not: 53. Neither won: 362.
- Seat 0 only (500 deals, descriptive): +5.8 points (+2.4 to +9.2).
- Seat 1 only (500 deals, descriptive): +7.8 points (+4.0 to +11.6).
- Deals on which the two lists did not both go first or both go second: 0 of 1000.

## Paired difference: the Wallace version minus deck 13 (per deal: same seed, same seat)

- Deals played by both: 1000. Difference per deal = (the Wallace version won) - (deck 13 won), each 1 or 0.
- Mean: -4.10 points; standard deviation of the per-deal differences 0.6432; 95% interval -8.09 to -0.11 points (mean +- 1.96 x sd / sqrt(n)).
- Both won: 398. The Wallace version won and deck 13 did not: 187. deck 13 won and the Wallace version did not: 228. Neither won: 187.
- Seat 0 only (500 deals, descriptive): -2.6 points (-8.5 to +3.3).
- Seat 1 only (500 deals, descriptive): -5.6 points (-11.0 to -0.2).
- Deals on which the two lists did not both go first or both go second: 64 of 1000.

## Went first / went second, and seat

| list | went first | went second | seat 0 | seat 1 |
|---|---|---|---|---|
| the Wallace version of draft A (1 Misty -> 1 Wallace) | 275/488 = 56.4% (51.9-60.7%) | 310/512 = 60.5% (56.2-64.7%) | 287/500 = 57.4% (53.0-61.7%) | 298/500 = 59.6% (55.2-63.8%) |
| draft A (Shark Tempo) | 246/488 = 50.4% (46.0-54.8%) | 271/512 = 52.9% (48.6-57.2%) | 258/500 = 51.6% (47.2-56.0%) | 259/500 = 51.8% (47.4-56.1%) |
| deck 13 (Alolan Ninetales / Raticate) | 325/488 = 66.6% (62.3-70.6%) | 301/512 = 58.8% (54.5-63.0%) | 300/500 = 60.0% (55.6-64.2%) | 326/500 = 65.2% (60.9-69.2%) |

Each cell: wins/games = win rate (95% Wilson interval).

## Wallace's own counts (ADDENDUM_WALLACE.md section 6.W)

| | all (1000) | went first (488) | went second (512) |
|---|---|---|---|
| games in which Wallace was played | 435 = 43.5% | 230 = 47.1% | 205 = 40.0% |
| W1: a Wallace on own turn 1 made Mega Sharpedo ex | 177 = 17.7% | 91 = 18.6% | 86 = 16.8% |
| W2: a Wallace on own turn 2 or earlier made Mega Sharpedo ex | 296 = 29.6% | 148 = 30.3% | 148 = 28.9% |
| L1 (README 6.5): an Evolve into Mega Sharpedo ex by own turn 2 | 382 = 38.2% | 203 = 41.6% | 179 = 35.0% |
| L1w: Mega Sharpedo ex by own turn 2, by an Evolve or Wallace (L1 or W2) | 643 = 64.3% | 332 = 68.0% | 311 = 60.7% |
| draft A's L1 on the same deals (it has no Wallace, so its L1w = L1) | 498 = 49.8% | 267 = 54.7% | 231 = 45.1% |

Wallaces played: 435 in 435 games (0 games with more than one). By own turn: turn 1: 177, turn 2: 119, turn 3: 51, turn 4: 53, turn 5: 19, turn 6: 14, turn 7+: 2.
By target (the Pokemon on the chosen spot): Carvanha (Bench): 338, Carvanha (Active): 97. By result: evolved into Mega Sharpedo ex: 435.
A Wallace evolution is not an Evolve the list chose, so README 6.5's L1 and an arm's `evolved` do not count it; W1, W2 and L1w do.
Win rate when a Wallace made Mega Sharpedo ex by own turn 2: 197/296 = 66.6% (61.0-71.7%); otherwise: 388/704 = 55.1% (51.4-58.8%). Descriptive only, not cause and effect.

## Sharpedo's line (README section 6.5): the Wallace version beside draft A, on the same deals

| step | Wallace version, all (1000) | Wallace version, went first (488) | Wallace version, went second (512) | draft A, all (1000) | draft A, went first (488) | draft A, went second (512) |
|---|---|---|---|---|---|---|
| L1: Mega Sharpedo ex evolved by own turn 2 (an Evolve) | 382 = 38.2% | 203 = 41.6% | 179 = 35.0% | 498 = 49.8% | 267 = 54.7% | 231 = 45.1% |
| L1w: Mega Sharpedo ex by own turn 2, by an Evolve or Wallace | 643 = 64.3% | 332 = 68.0% | 311 = 60.7% | 498 = 49.8% | 267 = 54.7% | 231 = 45.1% |
| L2: Turbo Shark was the attack of own turn 2 | 242 = 24.2% | 86 = 17.6% | 156 = 30.5% | 189 = 18.9% | 81 = 16.6% | 108 = 21.1% |
| L3: that Turbo Shark armed a Benched Pokemon (any Water Pokemon) | 220 = 22.0% | 79 = 16.2% | 141 = 27.5% | 173 = 17.3% | 76 = 15.6% | 97 = 18.9% |
| L3v: that Turbo Shark armed a Benched Alolan Vulpix | 59 = 5.9% | 14 = 2.9% | 45 = 8.8% | 44 = 4.4% | 14 = 2.9% | 30 = 5.9% |
| L4: Alolan Ninetales ex evolved by own turn 3 (any Vulpix) | 554 = 55.4% | 269 = 55.1% | 285 = 55.7% | 593 = 59.3% | 292 = 59.8% | 301 = 58.8% |
| L4v: that armed Alolan Vulpix evolved into Alolan Ninetales ex by own turn 3 | 19 = 1.9% | 6 = 1.2% | 13 = 2.5% | 17 = 1.7% | 8 = 1.6% | 9 = 1.8% |
| L5: own turn 3's attack was Binding Snow or Turbo Shark | 638 = 63.8% | 302 = 61.9% | 336 = 65.6% | 579 = 57.9% | 282 = 57.8% | 297 = 58.0% |
| line2: the line through turn 2 (L2 and L3) | 220 = 22.0% | 79 = 16.2% | 141 = 27.5% | 173 = 17.3% | 76 = 15.6% | 97 = 18.9% |
| line3: the line through turn 3 (L2 to L5) | 108 = 10.8% | 45 = 9.2% | 63 = 12.3% | 90 = 9.0% | 47 = 9.6% | 43 = 8.4% |
| plan: the plan's line (L2, L4v and L5) | 19 = 1.9% | 6 = 1.2% | 13 = 2.5% | 17 = 1.7% | 8 = 1.6% | 9 = 1.8% |
| games that reached own turn 2 / 3 | 975 / 942 | 481 / 469 | 494 / 473 | 977 / 942 | 481 / 469 | 496 / 473 |

**Own turn 2's Turbo Shark, by where its Energy went** (games).

| own turn 2 | Wallace version, all (1000) | Wallace version, went first (488) | Wallace version, went second (512) | draft A, all (1000) | draft A, went first (488) | draft A, went second (512) |
|---|---|---|---|---|---|---|
| armed: Alolan Ninetales ex | 67 | 26 | 41 | 57 | 29 | 28 |
| armed: Lapras | 64 | 23 | 41 | 54 | 27 | 27 |
| armed: Alolan Vulpix | 59 | 14 | 45 | 44 | 14 | 30 |
| armed: Mega Sharpedo ex | 23 | 14 | 9 | 9 | 4 | 5 |
| armed: Carvanha | 7 | 2 | 5 | 9 | 2 | 7 |
| not armed: no Benched Water Pokemon | 22 | 7 | 15 | 16 | 5 | 11 |
| no Turbo Shark on own turn 2 | 758 | 402 | 356 | 811 | 407 | 404 |

**First Turbo Shark, by own turn** (games).

| games | turn 1 | turn 2 | turn 3 | turn 4 | turn 5 | turn 6+ | never |
|---|---|---|---|---|---|---|---|
| Wallace version, all (1000) | 29 (2.9%) | 219 (21.9%) | 182 (18.2%) | 167 (16.7%) | 58 (5.8%) | 42 (4.2%) | 303 (30.3%) |
| Wallace version, went first (488) | 0 (0.0%) | 86 (17.6%) | 80 (16.4%) | 114 (23.4%) | 39 (8.0%) | 37 (7.6%) | 132 (27.0%) |
| Wallace version, went second (512) | 29 (5.7%) | 133 (26.0%) | 102 (19.9%) | 53 (10.4%) | 19 (3.7%) | 5 (1.0%) | 171 (33.4%) |
| draft A, all (1000) | 0 (0.0%) | 189 (18.9%) | 152 (15.2%) | 153 (15.3%) | 59 (5.9%) | 54 (5.4%) | 393 (39.3%) |
| draft A, went first (488) | 0 (0.0%) | 81 (16.6%) | 68 (13.9%) | 94 (19.3%) | 36 (7.4%) | 44 (9.0%) | 165 (33.8%) |
| draft A, went second (512) | 0 (0.0%) | 108 (21.1%) | 84 (16.4%) | 59 (11.5%) | 23 (4.5%) | 10 (2.0%) | 228 (44.5%) |

The Wallace version's win rate when the line through turn 2 happened: 189/220 = 85.9% (80.7-89.9%); when it did not: 396/780 = 50.8% (47.3-54.3%). Descriptive only, not cause and effect.

**The Wallace version's Turbo Sharks and the Bench-arming count.** Turbo Sharks: 1139 (1.14 a game; 697 games with at least one). Outcome of each: armed: 1071, no Benched Water Pokemon: 68.
Arms: 1071 (94.0% of Turbo Sharks). By target: Alolan Ninetales ex: 386, Lapras: 287, Alolan Vulpix: 218, Mega Sharpedo ex: 132, Carvanha: 48. The armed Pokemon later attacked from the Active Spot in 598 cases (first attack: Alolan Ninetales ex Binding Snow: 318, Lapras Surf: 180, Mega Sharpedo ex Turbo Shark: 84, Alolan Vulpix Gnaw: 10, Carvanha Sharp Fang: 6); left play first in 0; tracking lost in 0 (expected 0).

## Attacks by own turn, attacker and attack (the Wallace version's own attacks)

1000 games. Each cell: number of attacks (one at most per turn, so also games). Draft A's and deck 13's tables are in the main test's RESULTS.md.

| attacker | attack | turn 1 | turn 2 | turn 3 | turn 4 | turn 5 | turn 6 | turn 7+ | total |
|---|---|---|---|---|---|---|---|---|---|
| Alolan Ninetales ex | Binding Snow | 0 | 81 | 337 | 403 | 409 | 266 | 175 | 1671 |
| Mega Sharpedo ex | Turbo Shark | 29 | 242 | 301 | 270 | 171 | 86 | 40 | 1139 |
| Alolan Vulpix | Gnaw | 198 | 39 | 11 | 5 | 11 | 5 | 2 | 271 |
| Lapras | Surf | 0 | 0 | 65 | 109 | 52 | 24 | 12 | 262 |
| Carvanha | Sharp Fang | 112 | 63 | 19 | 5 | 9 | 6 | 1 | 215 |
| games that reached this own turn | | 1000 | 975 | 942 | 841 | 660 | 388 | 160 | |

## Did Mega Sharpedo ex, Alolan Ninetales ex and Lapras attack at all? (README section 6.7)

| list | Pokemon | games in which it attacked at least once | its attacks, all games |
|---|---|---|---|
| the Wallace version of draft A (1 Misty -> 1 Wallace) | Mega Sharpedo ex | 697 of 1000 (69.7%) | 1139 |
| the Wallace version of draft A (1 Misty -> 1 Wallace) | Alolan Ninetales ex | 636 of 1000 (63.6%) | 1671 |
| the Wallace version of draft A (1 Misty -> 1 Wallace) | Lapras | 200 of 1000 (20.0%) | 262 |
| draft A (Shark Tempo) | Mega Sharpedo ex | 607 of 1000 (60.7%) | 955 |
| draft A (Shark Tempo) | Alolan Ninetales ex | 632 of 1000 (63.2%) | 1636 |
| draft A (Shark Tempo) | Lapras | 209 of 1000 (20.9%) | 274 |

## Coverage flags (official goldfish `--coverage`, read as floor.py reads them, pilot km3)

- the Wallace version of draft A (1 Misty -> 1 Wallace) (`decks/brews/drafts_2026-10-01/draft-A-wallace.txt`): Alolan Ninetales ex (B2 029): attack Binding Snow: pays off during the opponent's turn, which the search doesn't play out.
  - In these games, as the floor counts them: Alolan Ninetales ex as attacker: used on 1671 of 1724 opportunities (96.9%).
- Draft A, deck 13 and the Fire list: the main test's RESULTS.md.

## For a second reader

- Wallace games read: 1000; every game completed, its seed, lists and pilots checked against the registration, and the engine's printed wins checked against the result files, at extraction (analyze.py's checks; `wallace/run.log`). Recorded games read for the pairing: draft A 1000, deck 13 1000 (the registered 2,000, checked).
- Wallace games with lifecycle errors: 0. Arm-tracking mismatches: 0. Own turns with two attacks: 0. Smoke records: 0. Wallaces with no target choice or an unreadable result: 0. All five are expected to be 0.
- Engine, programs and lists: sha256 in `wallace/provenance.txt` (written by run_wallace.sh before the first game).
- Per-game records: `wallace/games/*.jsonl` (analyze.py's fields plus `wallace`: each Wallace played, [own turn, game turn, target, spot, result, became]).
