# Strength report: slow_report_13-a-ninetales-raticate

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `f3dacac4e1315d8c` (matches the pre-registration); registered 2026-10-12T20:47:54Z.

> kx3 (d513e37b, on main-c045ede) on 13-a-ninetales-raticate v km3 on the public panel. A slow report on one deck, not development: how does 13-a-ninetales-raticate do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-12T20:47:54Z; first game started 2026-10-12T20:48:18Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json (commit dbe31f48b3da): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json (commit dbe31f48b3da): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 320; complete pairs 160 (= 320 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 160 paired games: +19.4 ± 6.4 points** (arm X 70.6% vs arm ref 51.2% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 13-a-ninetales-raticate | 160 | 70.6% | 51.2% | +19.4 ± 6.4 | +19.5 ± 8.9 | +19.3 ± 9.2 |

Overall by who went first (identical in both arms): deck first +19.5 ± 8.9 (n=77); deck second +19.3 ± 9.2 (n=83).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 13-a-ninetales-raticate | t-altaria | 20 | 40.0% | 20.0% | +20.0 ± 22.9 |
| 13-a-ninetales-raticate | t-blaziken | 20 | 75.0% | 60.0% | +15.0 ± 16.1 |
| 13-a-ninetales-raticate | t-hydreigon | 20 | 80.0% | 55.0% | +25.0 ± 19.5 |
| 13-a-ninetales-raticate | t-lucario | 20 | 65.0% | 40.0% | +25.0 ± 19.5 |
| 13-a-ninetales-raticate | t-sceptile | 20 | 70.0% | 55.0% | +15.0 ± 16.1 |
| 13-a-ninetales-raticate | t-suicune | 20 | 90.0% | 70.0% | +20.0 ± 18.0 |
| 13-a-ninetales-raticate | t-vespiquen | 20 | 80.0% | 70.0% | +10.0 ± 13.5 |
| 13-a-ninetales-raticate | t-weezing | 20 | 65.0% | 40.0% | +25.0 ± 19.5 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 160 | 595.53 / 447.76 / 1632.57 / 2624.01 s | 0.00 | 23.1 | 25801.0 / 20646.7 / 66891.7 / 162309.9 | 10 min |
| X | opponent seat | `km3` | 160 |  |  | 24.0 | 13.2 / 5.8 / 52.4 / 279.3 | 0.32 s |
| ref | deck seat | `km3` | 160 | 0.60 / 0.51 / 1.35 / 2.79 s | 1.65 | 22.0 | 15.0 / 6.8 / 58.1 / 279.2 | 0.33 s |
| ref | opponent seat | `km3` | 160 |  |  | 23.4 | 11.2 / 5.2 / 45.3 / 184.6 | 0.26 s |

One paired game (both arms) took 10 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 160 | 41.2 | +19.4 ± 6.4 | 261 / 101, 4.2 h | 725 / 565, 23.4 h |
| 13-a-ninetales-raticate | 160 | 41.2 | +19.4 ± 6.4 | 261 / 101, 4.2 h | 725 / 565, 23.4 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| 13-a-ninetales-raticate | Thieving Incisors used (an ability choice when evolving into Raticate ex) | 75.6% | 70.0% | +5.6 ± 6.1 |  |  |
