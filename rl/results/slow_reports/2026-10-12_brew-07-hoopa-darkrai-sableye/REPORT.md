# Strength report: slow_report_brew-07-hoopa-darkrai-sableye

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `1536d72073d7573d` (matches the pre-registration); registered 2026-10-12T20:49:33Z.

> kx3 (d513e37b, on main-c045ede) on brew-07-hoopa-darkrai-sableye v km3 on the public panel. A slow report on one deck, not development: how does brew-07-hoopa-darkrai-sableye do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-12T20:49:33Z; first game started 2026-10-12T20:49:47Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 320; complete pairs 160 (= 320 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 160 paired games: +15.9 ± 6.1 points** (arm X 79.1% vs arm ref 63.1% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| brew-07-hoopa-darkrai-sableye | 160 | 79.1% | 63.1% | +15.9 ± 6.1 | +15.4 ± 9.1 | +16.5 ± 8.2 |

Overall by who went first (identical in both arms): deck first +15.4 ± 9.1 (n=81); deck second +16.5 ± 8.2 (n=79).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| brew-07-hoopa-darkrai-sableye | t-altaria | 20 | 80.0% | 80.0% | +0.0 ± 12.3 |
| brew-07-hoopa-darkrai-sableye | t-blaziken | 20 | 90.0% | 55.0% | +35.0 ± 21.4 |
| brew-07-hoopa-darkrai-sableye | t-hydreigon | 20 | 85.0% | 72.5% | +12.5 ± 14.0 |
| brew-07-hoopa-darkrai-sableye | t-lucario | 20 | 80.0% | 80.0% | +0.0 ± 14.2 |
| brew-07-hoopa-darkrai-sableye | t-sceptile | 20 | 55.0% | 35.0% | +20.0 ± 18.0 |
| brew-07-hoopa-darkrai-sableye | t-suicune | 20 | 85.0% | 65.0% | +20.0 ± 18.0 |
| brew-07-hoopa-darkrai-sableye | t-vespiquen | 20 | 67.5% | 52.5% | +15.0 ± 16.1 |
| brew-07-hoopa-darkrai-sableye | t-weezing | 20 | 90.0% | 65.0% | +25.0 ± 19.5 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 160 | 698.11 / 645.57 / 1558.68 / 2205.31 s | 0.00 | 27.2 | 25679.5 / 22553.5 / 58613.7 / 121206.7 | 12 min |
| X | opponent seat | `km3` | 160 |  |  | 26.6 | 15.6 / 7.0 / 59.7 / 363.3 | 0.41 s |
| ref | deck seat | `km3` | 160 | 0.68 / 0.58 / 1.50 / 2.77 s | 1.47 | 26.7 | 12.6 / 5.7 / 47.2 / 255.0 | 0.34 s |
| ref | opponent seat | `km3` | 160 |  |  | 26.3 | 12.6 / 5.8 / 48.6 / 257.8 | 0.33 s |

One paired game (both arms) took 12 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 160 | 39.4 | +15.9 ± 6.1 | 239 / 79, 3.8 h | 663 / 503, 24.4 h |
| brew-07-hoopa-darkrai-sableye | 160 | 39.4 | +15.9 ± 6.1 | 239 / 79, 3.8 h | 663 / 503, 24.4 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
