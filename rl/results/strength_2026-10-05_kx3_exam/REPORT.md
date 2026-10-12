# Strength report: kx3_exam

Pilot **kx3** against reference **km3**, stage `heldout`. Manifest sha256 `8a8397678cdb5a5d` (matches the pre-registration); registered 2026-10-05T08:58:37Z.

> THE FINAL EXAM of the frozen play-out pilot (kx3 as in claude/playout-pilot d513e37b, 'a promising experimental baseline, not the finished planning bot'). Does kx3 play Dustin's held-out decks (the 11 never used in development) better than km3 does, on fresh deals against the 8 panel lists, REALISTIC knowledge? Primary: the pooled paired difference in game score (win 1, tie 1/2, loss 0) with its 95% interval, over 528 paired comparisons (1,056 games); a second figure weights every deck equally. It measures overall improvement across player decks the pilot was not developed on. Six comparisons per matchup (3 deals x 2 seats) don't support ranking individual matchups; the per-pair rows are printed for completeness only. The panel lists are in the pilot's guessing pool, so this answers 'against the public meta lists', not 'against unknown decks'. Time per game reported as a fact. Approved by Dustin Oct 4 ('yes approved'), conditional on the k3 check's pre-recorded rule and the d513e37b replay check (strength_2026-10-04_kx3_v_k3/PREREGISTRATION.md, addendum).

Pre-registration order: registered 2026-10-05T08:58:37Z; first game started 2026-10-05T09:46:53Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`; `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`

- Planned 1056 games; finished 1056; complete pairs 528 (= 1056 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 528 paired games: +21.3 ± 4.0 points** (arm X 53.0% vs arm ref 31.7% score).
Decks weighted equally (11 decks): +21.3 ± 5.1 (sd across deck means 8.7).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 02-arceus-crobat | 48 | 58.3% | 43.8% | +14.6 ± 11.7 | +4.2 ± 14.3 | +25.0 ± 17.7 |
| 04-absol-hoopa-darkrai | 48 | 58.3% | 33.3% | +25.0 ± 13.7 | +26.9 ± 20.5 | +22.7 ± 17.9 |
| 07-skarmory-stall | 48 | 75.0% | 54.2% | +20.8 ± 11.6 | +22.7 ± 17.9 | +19.2 ± 15.4 |
| 08-garchomp-toolbox | 48 | 39.6% | 17.7% | +21.9 ± 13.0 | +22.0 ± 16.1 | +21.7 ± 21.2 |
| 11-archaludon-haxorus-dragonair | 48 | 35.4% | 16.7% | +18.8 ± 11.2 | +29.2 ± 18.6 | +8.3 ± 11.3 |
| 12-ariados-whimsicott-ogerpon | 48 | 62.5% | 27.1% | +35.4 ± 16.0 | +31.0 ± 19.7 | +42.1 ± 27.3 |
| 13-a-ninetales-raticate | 48 | 72.9% | 54.2% | +18.8 ± 13.9 | +13.0 ± 18.7 | +24.0 ± 20.5 |
| 14-comfey-raticate-hypno | 48 | 35.4% | 10.4% | +25.0 ± 13.7 | +37.5 ± 19.8 | +12.5 ± 17.9 |
| 15-jolteon-oricorio-raticate | 48 | 66.7% | 35.4% | +31.2 ± 13.3 | +31.8 ± 19.9 | +30.8 ± 18.1 |
| draft-C-meowstic-hatterene-v2 | 48 | 33.3% | 12.5% | +20.8 ± 11.6 | +23.1 ± 16.5 | +18.2 ± 16.5 |
| draft-D-entei-grimhound | 48 | 45.8% | 43.8% | +2.1 ± 13.7 | +8.3 ± 23.3 | -4.2 ± 14.3 |

Overall by who went first (identical in both arms): deck first +22.9 ± 5.7 (n=269); deck second +19.7 ± 5.5 (n=259).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 02-arceus-crobat | t-altaria | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 02-arceus-crobat | t-blaziken | 6 | 83.3% | 50.0% | +33.3 ± 41.3 |
| 02-arceus-crobat | t-hydreigon | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 02-arceus-crobat | t-lucario | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 02-arceus-crobat | t-sceptile | 6 | 33.3% | 50.0% | -16.7 ± 32.7 |
| 02-arceus-crobat | t-suicune | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 02-arceus-crobat | t-vespiquen | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 02-arceus-crobat | t-weezing | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 04-absol-hoopa-darkrai | t-altaria | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 04-absol-hoopa-darkrai | t-blaziken | 6 | 66.7% | 66.7% | +0.0 ± 50.6 |
| 04-absol-hoopa-darkrai | t-hydreigon | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 04-absol-hoopa-darkrai | t-lucario | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 04-absol-hoopa-darkrai | t-sceptile | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 04-absol-hoopa-darkrai | t-suicune | 6 | 33.3% | 33.3% | +0.0 ± 0.0 |
| 04-absol-hoopa-darkrai | t-vespiquen | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 04-absol-hoopa-darkrai | t-weezing | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 07-skarmory-stall | t-altaria | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 07-skarmory-stall | t-blaziken | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 07-skarmory-stall | t-hydreigon | 6 | 100.0% | 50.0% | +50.0 ± 43.8 |
| 07-skarmory-stall | t-lucario | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 07-skarmory-stall | t-sceptile | 6 | 100.0% | 50.0% | +50.0 ± 43.8 |
| 07-skarmory-stall | t-suicune | 6 | 100.0% | 100.0% | +0.0 ± 0.0 |
| 07-skarmory-stall | t-vespiquen | 6 | 100.0% | 100.0% | +0.0 ± 0.0 |
| 07-skarmory-stall | t-weezing | 6 | 66.7% | 66.7% | +0.0 ± 0.0 |
| 08-garchomp-toolbox | t-altaria | 6 | 33.3% | 0.0% | +33.3 ± 41.3 |
| 08-garchomp-toolbox | t-blaziken | 6 | 33.3% | 33.3% | +0.0 ± 50.6 |
| 08-garchomp-toolbox | t-hydreigon | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 08-garchomp-toolbox | t-lucario | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 08-garchomp-toolbox | t-sceptile | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 08-garchomp-toolbox | t-suicune | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 08-garchomp-toolbox | t-vespiquen | 6 | 33.3% | 0.0% | +33.3 ± 41.3 |
| 08-garchomp-toolbox | t-weezing | 6 | 50.0% | 41.7% | +8.3 ± 16.3 |
| 11-archaludon-haxorus-dragonair | t-altaria | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 11-archaludon-haxorus-dragonair | t-blaziken | 6 | 33.3% | 0.0% | +33.3 ± 41.3 |
| 11-archaludon-haxorus-dragonair | t-hydreigon | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 11-archaludon-haxorus-dragonair | t-lucario | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 11-archaludon-haxorus-dragonair | t-sceptile | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 11-archaludon-haxorus-dragonair | t-suicune | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 11-archaludon-haxorus-dragonair | t-vespiquen | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 11-archaludon-haxorus-dragonair | t-weezing | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 12-ariados-whimsicott-ogerpon | t-altaria | 6 | 66.7% | 33.3% | +33.3 ± 41.3 |
| 12-ariados-whimsicott-ogerpon | t-blaziken | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 12-ariados-whimsicott-ogerpon | t-hydreigon | 6 | 66.7% | 33.3% | +33.3 ± 65.3 |
| 12-ariados-whimsicott-ogerpon | t-lucario | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 12-ariados-whimsicott-ogerpon | t-sceptile | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 12-ariados-whimsicott-ogerpon | t-suicune | 6 | 66.7% | 33.3% | +33.3 ± 65.3 |
| 12-ariados-whimsicott-ogerpon | t-vespiquen | 6 | 83.3% | 16.7% | +66.7 ± 41.3 |
| 12-ariados-whimsicott-ogerpon | t-weezing | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 13-a-ninetales-raticate | t-altaria | 6 | 66.7% | 66.7% | +0.0 ± 0.0 |
| 13-a-ninetales-raticate | t-blaziken | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 13-a-ninetales-raticate | t-hydreigon | 6 | 50.0% | 50.0% | +0.0 ± 50.6 |
| 13-a-ninetales-raticate | t-lucario | 6 | 100.0% | 83.3% | +16.7 ± 32.7 |
| 13-a-ninetales-raticate | t-sceptile | 6 | 83.3% | 16.7% | +66.7 ± 41.3 |
| 13-a-ninetales-raticate | t-suicune | 6 | 83.3% | 66.7% | +16.7 ± 32.7 |
| 13-a-ninetales-raticate | t-vespiquen | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 13-a-ninetales-raticate | t-weezing | 6 | 66.7% | 33.3% | +33.3 ± 65.3 |
| 14-comfey-raticate-hypno | t-altaria | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 14-comfey-raticate-hypno | t-blaziken | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 14-comfey-raticate-hypno | t-hydreigon | 6 | 33.3% | 0.0% | +33.3 ± 41.3 |
| 14-comfey-raticate-hypno | t-lucario | 6 | 50.0% | 33.3% | +16.7 ± 60.2 |
| 14-comfey-raticate-hypno | t-sceptile | 6 | 33.3% | 0.0% | +33.3 ± 41.3 |
| 14-comfey-raticate-hypno | t-suicune | 6 | 0.0% | 0.0% | +0.0 ± 0.0 |
| 14-comfey-raticate-hypno | t-vespiquen | 6 | 66.7% | 0.0% | +66.7 ± 41.3 |
| 14-comfey-raticate-hypno | t-weezing | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 15-jolteon-oricorio-raticate | t-altaria | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| 15-jolteon-oricorio-raticate | t-blaziken | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 15-jolteon-oricorio-raticate | t-hydreigon | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 15-jolteon-oricorio-raticate | t-lucario | 6 | 83.3% | 50.0% | +33.3 ± 41.3 |
| 15-jolteon-oricorio-raticate | t-sceptile | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 15-jolteon-oricorio-raticate | t-suicune | 6 | 83.3% | 50.0% | +33.3 ± 41.3 |
| 15-jolteon-oricorio-raticate | t-vespiquen | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 15-jolteon-oricorio-raticate | t-weezing | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| draft-C-meowstic-hatterene-v2 | t-altaria | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| draft-C-meowstic-hatterene-v2 | t-blaziken | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| draft-C-meowstic-hatterene-v2 | t-hydreigon | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| draft-C-meowstic-hatterene-v2 | t-lucario | 6 | 66.7% | 16.7% | +50.0 ± 43.8 |
| draft-C-meowstic-hatterene-v2 | t-sceptile | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| draft-C-meowstic-hatterene-v2 | t-suicune | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| draft-C-meowstic-hatterene-v2 | t-vespiquen | 6 | 50.0% | 0.0% | +50.0 ± 43.8 |
| draft-C-meowstic-hatterene-v2 | t-weezing | 6 | 33.3% | 33.3% | +0.0 ± 0.0 |
| draft-D-entei-grimhound | t-altaria | 6 | 66.7% | 66.7% | +0.0 ± 50.6 |
| draft-D-entei-grimhound | t-blaziken | 6 | 0.0% | 16.7% | -16.7 ± 32.7 |
| draft-D-entei-grimhound | t-hydreigon | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| draft-D-entei-grimhound | t-lucario | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| draft-D-entei-grimhound | t-sceptile | 6 | 50.0% | 66.7% | -16.7 ± 60.2 |
| draft-D-entei-grimhound | t-suicune | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| draft-D-entei-grimhound | t-vespiquen | 6 | 83.3% | 66.7% | +16.7 ± 60.2 |
| draft-D-entei-grimhound | t-weezing | 6 | 33.3% | 33.3% | +0.0 ± 0.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 528 | 207.43 / 189.11 / 465.37 / 768.10 s | 0.00 | 24.9 | 8313.4 / 7022.6 / 21024.1 / 53413.7 | 3 min |
| X | opponent seat | `km3` | 528 |  |  | 24.7 | 15.0 / 6.0 / 60.3 / 348.2 | 0.37 s |
| ref | deck seat | `km3` | 528 | 0.99 / 0.87 / 2.29 / 4.97 s | 1.01 | 24.7 | 20.9 / 8.1 / 82.0 / 971.5 | 0.52 s |
| ref | opponent seat | `km3` | 528 |  |  | 24.7 | 18.8 / 8.0 / 73.7 / 407.6 | 0.46 s |

One paired game (both arms) took 3 min on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 528 | 46.6 | +21.3 ± 4.0 | 334 / 0, 0.00 s | 926 / 398, 11.5 h |
| 02-arceus-crobat | 48 | 41.2 | +14.6 ± 11.7 | 261 / 213, 8.0 h | 725 / 677, 25.5 h |
| 04-absol-hoopa-darkrai | 48 | 48.4 | +25.0 ± 13.7 | 360 / 312, 8.7 h | 999 / 951, 26.4 h |
| 07-skarmory-stall | 48 | 41.0 | +20.8 ± 11.6 | 259 / 211, 7.0 h | 719 / 671, 22.4 h |
| 08-garchomp-toolbox | 48 | 46.0 | +21.9 ± 13.0 | 326 / 278, 9.7 h | 904 / 856, 29.9 h |
| 11-archaludon-haxorus-dragonair | 48 | 39.4 | +18.8 ± 11.2 | 240 / 192, 5.1 h | 665 / 617, 16.5 h |
| 12-ariados-whimsicott-ogerpon | 48 | 56.5 | +35.4 ± 16.0 | 490 / 442, 13.4 h | 1361 / 1313, 39.7 h |
| 13-a-ninetales-raticate | 48 | 49.1 | +18.8 ± 13.9 | 370 / 322, 4.8 h | 1028 / 980, 14.7 h |
| 14-comfey-raticate-hypno | 48 | 48.4 | +25.0 ± 13.7 | 360 / 312, 7.4 h | 999 / 951, 22.6 h |
| 15-jolteon-oricorio-raticate | 48 | 46.8 | +31.2 ± 13.3 | 338 / 290, 7.8 h | 937 / 889, 24.1 h |
| draft-C-meowstic-hatterene-v2 | 48 | 41.0 | +20.8 ± 11.6 | 259 / 211, 6.6 h | 719 / 671, 21.1 h |
| draft-D-entei-grimhound | 48 | 48.3 | +2.1 ± 13.7 | 359 / 311, 9.4 h | 998 / 950, 28.9 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| 13-a-ninetales-raticate | Thieving Incisors used (an ability choice when evolving into Raticate ex) | 68.8% | 70.8% | -2.1 ± 10.9 |  |  |
| 14-comfey-raticate-hypno | Thieving Incisors used (an ability choice when evolving into Raticate ex) | 75.0% | 72.9% | +2.1 ± 4.1 |  |  |
| 15-jolteon-oricorio-raticate | Thieving Incisors used (an ability choice when evolving into Raticate ex) | 85.4% | 79.2% | +6.2 ± 6.9 |  |  |
