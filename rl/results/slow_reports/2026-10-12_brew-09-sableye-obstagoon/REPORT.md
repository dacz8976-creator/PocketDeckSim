# Strength report: slow_report_brew-09-sableye-obstagoon

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `577a1ac83dd4f50d` (matches the pre-registration); registered 2026-10-13T04:54:49Z.

> kx3 (d513e37b, on main-c045ede) on brew-09-sableye-obstagoon v km3 on the public panel. A slow report on one deck, not development: how does brew-09-sableye-obstagoon do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-13T04:54:49Z; first game started 2026-10-13T04:54:51Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 160; complete pairs 80 (= 160 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 80 paired games: +18.8 ± 9.1 points** (arm X 81.2% vs arm ref 62.5% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| brew-09-sableye-obstagoon | 80 | 81.2% | 62.5% | +18.8 ± 9.1 | +20.0 ± 15.1 | +17.8 ± 11.3 |

Overall by who went first (identical in both arms): deck first +20.0 ± 15.1 (n=35); deck second +17.8 ± 11.3 (n=45).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| brew-09-sableye-obstagoon | t-altaria | 20 | 85.0% | 65.0% | +20.0 ± 18.0 |
| brew-09-sableye-obstagoon | t-blaziken | 20 | 72.5% | 55.0% | +17.5 ± 16.3 |
| brew-09-sableye-obstagoon | t-hydreigon | 20 | 85.0% | 65.0% | +20.0 ± 18.0 |
| brew-09-sableye-obstagoon | t-lucario | 20 | 82.5% | 65.0% | +17.5 ± 21.7 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 80 | 490.53 / 449.55 / 973.57 / 1196.21 s | 0.00 | 23.4 | 20987.1 / 20163.3 / 40571.4 / 89281.5 | 8 min |
| X | opponent seat | `km3` | 80 |  |  | 26.5 | 17.6 / 7.8 / 66.2 / 544.7 | 0.46 s |
| ref | deck seat | `km3` | 80 | 0.51 / 0.48 / 1.07 / 1.21 s | 1.95 | 20.8 | 8.9 / 5.1 / 29.8 / 160.8 | 0.18 s |
| ref | opponent seat | `km3` | 80 |  |  | 24.2 | 13.0 / 6.6 / 48.3 / 245.5 | 0.31 s |

One paired game (both arms) took 8 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 80 | 41.6 | +18.8 ± 9.1 | 267 / 187, 6.4 h | 740 / 660, 22.5 h |
| brew-09-sableye-obstagoon | 80 | 41.6 | +18.8 ± 9.1 | 267 / 187, 6.4 h | 740 / 660, 22.5 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
