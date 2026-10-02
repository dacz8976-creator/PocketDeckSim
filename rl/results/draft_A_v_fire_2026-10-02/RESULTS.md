# Draft A v the Fire list: results

Written by `analyze.py report` from `games/*.jsonl` and `coverage/*.json`. Every definition is the README's (sections 6 to 8). **Not a ranking and not a ladder forecast**: one list against one saved opponent list, both sides played by the km3 bot.

**Reading (README section 8): the premise does not hold in this test (reversed): deck 13 beat the Fire list more often than draft A did on the same deals, by more than the paired interval.** Paired difference, draft A minus deck 13: -10.9 points (95% interval -14.8 to -7.0).

Secondary, descriptive (README section 8): draft A's win rate against this list is not distinguishable from 50% (51.7%, 48.6-54.8%).

Sharpedo's line, beside the reading (README section 8, plan's line first; added by hand from the table in "Sharpedo's line" below, at the independent check's note):
- the plan's line (own turn 2's Turbo Shark arms the Benched Alolan Vulpix, which becomes Alolan Ninetales ex by own turn 3, and own turn 3 attacks) happened in 17 of 1000 games (1.7%);
- the looser line through turn 2 happened in 173 (17.3%), and through turn 3 in 90 (9.0%);
- Mega Sharpedo ex attacked at all in 607 games (60.7%).

## Win rates (draws are not wins)

| list | games | wins | draws | win rate | 95% interval (Wilson) |
|---|---|---|---|---|---|
| draft A (Shark Tempo) | 1000 | 517 | 5 | 51.7% | 48.6-54.8% |
| deck 13 (Alolan Ninetales / Raticate) | 1000 | 626 | 0 | 62.6% | 59.6-65.5% |

## Paired difference (per deal: same seed, same seat)

- Deals played by both lists: 1000. Difference per deal = (draft A won) - (deck 13 won), each 1 or 0.
- Mean: -10.90 points; standard deviation of the per-deal differences 0.6368; 95% interval -14.85 to -6.95 points (mean +- 1.96 x sd / sqrt(n)).
- Both won: 363. Draft A won and deck 13 did not: 154. Deck 13 won and draft A did not: 263. Neither won: 220.
- Seat 0 only (500 deals, descriptive): -8.4 points (-14.2 to -2.6).
- Seat 1 only (500 deals, descriptive): -13.4 points (-18.8 to -8.0).
- Deals on which the two lists did not both go first or both go second: 64 of 1000 (the same seed decides the opening coin for both, if the engine draws it the same way).

## Went first / went second, and seat

| list | went first | went second | seat 0 | seat 1 |
|---|---|---|---|---|
| draft A (Shark Tempo) | 246/488 = 50.4% (46.0-54.8%) | 271/512 = 52.9% (48.6-57.2%) | 258/500 = 51.6% (47.2-56.0%) | 259/500 = 51.8% (47.4-56.1%) |
| deck 13 (Alolan Ninetales / Raticate) | 325/488 = 66.6% (62.3-70.6%) | 301/512 = 58.8% (54.5-63.0%) | 300/500 = 60.0% (55.6-64.2%) | 326/500 = 65.2% (60.9-69.2%) |

Each cell: wins/games = win rate (95% Wilson interval).

## Attacks by own turn, attacker and attack (the list's own attacks)

**draft A (Shark Tempo)** (1000 games). Each cell: number of attacks (one attack at most per turn, so also games). Own turn 1 is the list's first turn.

| attacker | attack | turn 1 | turn 2 | turn 3 | turn 4 | turn 5 | turn 6 | turn 7+ | total |
|---|---|---|---|---|---|---|---|---|---|
| Alolan Ninetales ex | Binding Snow | 0 | 91 | 340 | 398 | 397 | 250 | 160 | 1636 |
| Mega Sharpedo ex | Turbo Shark | 0 | 189 | 239 | 243 | 153 | 93 | 38 | 955 |
| Carvanha | Sharp Fang | 141 | 110 | 42 | 15 | 13 | 8 | 0 | 329 |
| Alolan Vulpix | Gnaw | 226 | 47 | 12 | 6 | 7 | 4 | 2 | 304 |
| Lapras | Surf | 0 | 0 | 73 | 110 | 55 | 23 | 13 | 274 |
| games that reached this own turn | | 1000 | 977 | 942 | 847 | 642 | 379 | 149 | |

**deck 13 (Alolan Ninetales / Raticate)** (1000 games). Each cell: number of attacks (one attack at most per turn, so also games). Own turn 1 is the list's first turn.

| attacker | attack | turn 1 | turn 2 | turn 3 | turn 4 | turn 5 | turn 6 | turn 7+ | total |
|---|---|---|---|---|---|---|---|---|---|
| Alolan Ninetales ex | Binding Snow | 0 | 139 | 473 | 594 | 507 | 276 | 141 | 2130 |
| Team Rocket's Raticate ex | Boost Dash | 0 | 295 | 369 | 168 | 100 | 48 | 13 | 993 |
| Alolan Vulpix | Gnaw | 288 | 80 | 20 | 10 | 8 | 1 | 1 | 408 |
| Team Rocket's Rattata | Ambush | 224 | 54 | 22 | 11 | 1 | 0 | 0 | 312 |
| games that reached this own turn | | 1000 | 959 | 927 | 808 | 618 | 326 | 115 | |

## Did Mega Sharpedo ex, Alolan Ninetales ex and Lapras attack at all? (README section 6.7)

Each row is one Pokemon in one list, counted on its own: a game counts in every row whose Pokemon made at least one of the list's attacks in it (any of its attacks).

| list | Pokemon | games in which it attacked at least once | its attacks, all games |
|---|---|---|---|
| draft A (Shark Tempo) | Mega Sharpedo ex | 607 of 1000 (60.7%) | 955 |
| draft A (Shark Tempo) | Alolan Ninetales ex | 632 of 1000 (63.2%) | 1636 |
| draft A (Shark Tempo) | Lapras | 209 of 1000 (20.9%) | 274 |
| deck 13 (Alolan Ninetales / Raticate) | Mega Sharpedo ex | not in the list | not in the list |
| deck 13 (Alolan Ninetales / Raticate) | Alolan Ninetales ex | 737 of 1000 (73.7%) | 2130 |
| deck 13 (Alolan Ninetales / Raticate) | Lapras | not in the list | not in the list |

## Sharpedo's line (draft A; README section 6.5)

| step | all games (1000) | went first (488) | went second (512) |
|---|---|---|---|
| L1: Mega Sharpedo ex evolved by own turn 2 | 498 = 49.8% | 267 = 54.7% | 231 = 45.1% |
| L2: Turbo Shark was the attack of own turn 2 | 189 = 18.9% | 81 = 16.6% | 108 = 21.1% |
| L3: that Turbo Shark armed a Benched Pokemon (any Water Pokemon) | 173 = 17.3% | 76 = 15.6% | 97 = 18.9% |
| L3v: that Turbo Shark armed a Benched Alolan Vulpix | 44 = 4.4% | 14 = 2.9% | 30 = 5.9% |
| L4: Alolan Ninetales ex evolved by own turn 3 (any Vulpix) | 593 = 59.3% | 292 = 59.8% | 301 = 58.8% |
| L4v: that armed Alolan Vulpix evolved into Alolan Ninetales ex by own turn 3 | 17 = 1.7% | 8 = 1.6% | 9 = 1.8% |
| L5: own turn 3's attack was Binding Snow or Turbo Shark | 579 = 57.9% | 282 = 57.8% | 297 = 58.0% |
| line2: the line through turn 2 (L2 and L3) | 173 = 17.3% | 76 = 15.6% | 97 = 18.9% |
| line3: the line through turn 3 (L2 to L5) | 90 = 9.0% | 47 = 9.6% | 43 = 8.4% |
| plan: the plan's line (L2, L4v and L5) | 17 = 1.7% | 8 = 1.6% | 9 = 1.8% |
| games that reached own turn 2 / 3 | 977 / 942 | 481 / 469 | 496 / 473 |

**Own turn 2's Turbo Shark, by where its Energy went** (games): the arm's target (the Pokemon on that Bench spot), or why there was no arm.

| own turn 2 | all games (1000) | went first (488) | went second (512) |
|---|---|---|---|
| armed: Alolan Ninetales ex | 57 | 29 | 28 |
| armed: Lapras | 54 | 27 | 27 |
| armed: Alolan Vulpix | 44 | 14 | 30 |
| armed: Carvanha | 9 | 2 | 7 |
| armed: Mega Sharpedo ex | 9 | 4 | 5 |
| not armed: no Benched Water Pokemon | 16 | 5 | 11 |
| no Turbo Shark on own turn 2 | 811 | 407 | 404 |

**First Turbo Shark, by own turn** (games). README 6.5 reads the plan as own turn 2 going first and going second; turn 3 is shown beside it.

| games | turn 2 | turn 3 | turn 4 | turn 5 | turn 6+ | never |
|---|---|---|---|---|---|---|
| all games (1000) | 189 (18.9%) | 152 (15.2%) | 153 (15.3%) | 59 (5.9%) | 54 (5.4%) | 393 (39.3%) |
| went first (488) | 81 (16.6%) | 68 (13.9%) | 94 (19.3%) | 36 (7.4%) | 44 (9.0%) | 165 (33.8%) |
| went second (512) | 108 (21.1%) | 84 (16.4%) | 59 (11.5%) | 23 (4.5%) | 10 (2.0%) | 228 (44.5%) |

Win rate when the line through turn 2 happened: 147/173 = 85.0% (78.9-89.5%); when it did not: 370/827 = 44.7% (41.4-48.1%). Descriptive only, not cause and effect: games where the bot can play the line are also games with good draws.

**Turbo Shark and the Bench-arming count.** Turbo Sharks: 955 (0.95 a game; 607 games with at least one). Outcome of each: armed: 912, no Benched Water Pokemon: 43.
Bench-arming count (Turbo Shark Energy attached to a Benched Water Pokemon): 912 (0.91 a game; 95.5% of Turbo Sharks). By target at the time: Alolan Ninetales ex: 352, Lapras: 246, Alolan Vulpix: 161, Mega Sharpedo ex: 85, Carvanha: 68. By own turn: turn 1: 0, turn 2: 173, turn 3: 225, turn 4: 234, turn 5: 151, turn 6: 92, turn 7+: 37.
After the arming: the armed Pokemon later attacked from the Active Spot in 454 cases (49.8%; first attack: Alolan Ninetales ex Binding Snow: 258, Lapras Surf: 146, Mega Sharpedo ex Turbo Shark: 42, Carvanha Sharp Fang: 5, Alolan Vulpix Gnaw: 3); left play before attacking in 0; still in play at the end without attacking in 458; tracking lost in 0 (expected 0; README 6.5).
The armed Pokemon evolved after the arming (its first evolution) in 60 cases: into Alolan Ninetales ex: 48, into Mega Sharpedo ex: 12.

## Coverage flags (official goldfish `--coverage`, read as floor.py reads them, pilot km3)

- draft A (Shark Tempo) (`decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt`): Alolan Ninetales ex (B2 029): attack Binding Snow: pays off during the opponent's turn, which the search doesn't play out.
  - In these games, as the floor counts them: Alolan Ninetales ex as attacker: used on 1636 of 1699 opportunities (96.3%).
- deck 13 (Alolan Ninetales / Raticate) (`decks/dustin/13-a-ninetales-raticate.txt`): Alolan Ninetales ex (B2 029): attack Binding Snow: pays off during the opponent's turn, which the search doesn't play out.
  - In these games, as the floor counts them: Alolan Ninetales ex as attacker: used on 2130 of 2151 opportunities (99.0%).
- the Charizard Y / Entei list (h-charizardy_entei) (`rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt`): no flagged card.

## For a second reader

- Games read: 2000 (draft A (Shark Tempo): 1000, deck 13 (Alolan Ninetales / Raticate): 1000); every game completed, its seed, lists and pilots checked against the registration, and the engine's printed wins checked against the result files, at extraction (`run.log`).
- Games with lifecycle errors: 0. Arm-tracking mismatches: 0. Own turns with two attacks: 0. Smoke records: 0. All four are expected to be 0.
- Engine, programs and lists: sha256 in `provenance.txt` (written by run.sh before the first game).
- Per-game records: `games/*.jsonl` (one line per game; README section 5 lists the fields).
