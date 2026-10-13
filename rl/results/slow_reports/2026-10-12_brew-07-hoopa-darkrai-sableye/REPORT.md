# Strength report: slow_report_brew-07-hoopa-darkrai-sableye

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `1536d72073d7573d` (matches the pre-registration); registered 2026-10-12T20:49:33Z.

> kx3 (d513e37b, on main-c045ede) on brew-07-hoopa-darkrai-sableye v km3 on the public panel. A slow report on one deck, not development: how does brew-07-hoopa-darkrai-sableye do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-12T20:49:33Z; first game started 2026-10-12T20:49:47Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 240; complete pairs 120 (= 240 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 120 paired games: +14.6 ± 7.0 points** (arm X 79.2% vs arm ref 64.6% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| brew-07-hoopa-darkrai-sableye | 120 | 79.2% | 64.6% | +14.6 ± 7.0 | +11.0 ± 10.1 | +18.0 ± 9.7 |

Overall by who went first (identical in both arms): deck first +11.0 ± 10.1 (n=59); deck second +18.0 ± 9.7 (n=61).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| brew-07-hoopa-darkrai-sableye | t-altaria | 20 | 80.0% | 80.0% | +0.0 ± 12.3 |
| brew-07-hoopa-darkrai-sableye | t-blaziken | 20 | 90.0% | 55.0% | +35.0 ± 21.4 |
| brew-07-hoopa-darkrai-sableye | t-hydreigon | 20 | 85.0% | 72.5% | +12.5 ± 14.0 |
| brew-07-hoopa-darkrai-sableye | t-lucario | 20 | 80.0% | 80.0% | +0.0 ± 14.2 |
| brew-07-hoopa-darkrai-sableye | t-sceptile | 20 | 55.0% | 35.0% | +20.0 ± 18.0 |
| brew-07-hoopa-darkrai-sableye | t-suicune | 20 | 85.0% | 65.0% | +20.0 ± 18.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 120 | 610.44 / 530.53 / 1404.95 / 1977.07 s | 0.00 | 26.3 | 23211.0 / 20571.0 / 52710.8 / 103933.5 | 10 min |
| X | opponent seat | `km3` | 120 |  |  | 25.4 | 14.1 / 6.6 / 53.9 / 363.3 | 0.36 s |
| ref | deck seat | `km3` | 120 | 0.60 / 0.51 / 1.34 / 1.73 s | 1.67 | 25.4 | 11.7 / 5.3 / 43.6 / 255.0 | 0.30 s |
| ref | opponent seat | `km3` | 120 |  |  | 24.9 | 11.5 / 5.4 / 42.6 / 257.8 | 0.29 s |

One paired game (both arms) took 10 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 120 | 39.1 | +14.6 ± 7.0 | 235 / 115, 4.9 h | 653 / 533, 22.6 h |
| brew-07-hoopa-darkrai-sableye | 120 | 39.1 | +14.6 ± 7.0 | 235 / 115, 4.9 h | 653 / 533, 22.6 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
