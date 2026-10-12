# Strength report: slow_report_13-a-ninetales-raticate

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `f3dacac4e1315d8c` (matches the pre-registration); registered 2026-10-12T20:47:54Z.

> kx3 (d513e37b, on main-c045ede) on 13-a-ninetales-raticate v km3 on the public panel. A slow report on one deck, not development: how does 13-a-ninetales-raticate do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-12T20:47:54Z; first game started 2026-10-12T20:48:18Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json (commit dbe31f48b3da): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json (commit dbe31f48b3da): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 84; complete pairs 42 (= 84 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 42 paired games: +16.7 ± 13.2 points** (arm X 59.5% vs arm ref 42.9% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 13-a-ninetales-raticate | 42 | 59.5% | 42.9% | +16.7 ± 13.2 | +21.1 ± 18.8 | +13.0 ± 18.7 |

Overall by who went first (identical in both arms): deck first +21.1 ± 18.8 (n=19); deck second +13.0 ± 18.7 (n=23).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 13-a-ninetales-raticate | t-altaria | 20 | 40.0% | 20.0% | +20.0 ± 22.9 |
| 13-a-ninetales-raticate | t-blaziken | 20 | 75.0% | 60.0% | +15.0 ± 16.1 |
| 13-a-ninetales-raticate | t-hydreigon | 2 | 100.0% | 100.0% | +0.0 ± 0.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 42 | 470.19 / 398.39 / 1154.38 / 1274.26 s | 0.00 | 21.0 | 22375.6 / 19394.3 / 50991.6 / 104331.5 | 8 min |
| X | opponent seat | `km3` | 42 |  |  | 22.4 | 12.9 / 5.5 / 51.8 / 268.5 | 0.29 s |
| ref | deck seat | `km3` | 42 | 0.55 / 0.53 / 1.15 / 1.21 s | 1.81 | 20.4 | 14.7 / 6.5 / 57.2 / 273.5 | 0.30 s |
| ref | opponent seat | `km3` | 42 |  |  | 22.3 | 10.8 / 5.0 / 40.5 / 184.6 | 0.24 s |

One paired game (both arms) took 8 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 42 | 43.7 | +16.7 ± 13.2 | 294 / 252, 8.2 h | 816 / 774, 25.3 h |
| 13-a-ninetales-raticate | 42 | 43.7 | +16.7 ± 13.2 | 294 / 252, 8.2 h | 816 / 774, 25.3 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| 13-a-ninetales-raticate | Thieving Incisors used (an ability choice when evolving into Raticate ex) | 64.3% | 50.0% | +14.3 ± 12.6 |  |  |
