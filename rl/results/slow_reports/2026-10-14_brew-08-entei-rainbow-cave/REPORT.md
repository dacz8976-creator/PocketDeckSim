# Strength report: slow_report_brew-08-entei-rainbow-cave

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `dfb0219986f54ef3` (matches the pre-registration); registered 2026-10-15T02:40:06Z.

> kx3 (d513e37b, on main-c045ede) on brew-08-entei-rainbow-cave v km3 on the public panel. A slow report on one deck, not development: how does brew-08-entei-rainbow-cave do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-15T02:40:06Z; first game started 2026-10-15T02:40:59Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 160; complete pairs 80 (= 160 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 80 paired games: +26.2 ± 10.3 points** (arm X 76.2% vs arm ref 50.0% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| brew-08-entei-rainbow-cave | 80 | 76.2% | 50.0% | +26.2 ± 10.3 | +23.8 ± 13.0 | +28.9 ± 16.4 |

Overall by who went first (identical in both arms): deck first +23.8 ± 13.0 (n=42); deck second +28.9 ± 16.4 (n=38).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| brew-08-entei-rainbow-cave | t-altaria | 20 | 80.0% | 45.0% | +35.0 ± 21.4 |
| brew-08-entei-rainbow-cave | t-blaziken | 20 | 55.0% | 30.0% | +25.0 ± 19.5 |
| brew-08-entei-rainbow-cave | t-hydreigon | 20 | 90.0% | 70.0% | +20.0 ± 22.9 |
| brew-08-entei-rainbow-cave | t-lucario | 20 | 80.0% | 55.0% | +25.0 ± 19.5 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 80 | 844.72 / 825.35 / 1563.13 / 1932.21 s | 0.00 | 24.2 | 34823.5 / 31838.5 / 68440.6 / 118877.8 | 14 min |
| X | opponent seat | `km3` | 80 |  |  | 26.7 | 24.9 / 9.8 / 95.6 / 368.3 | 0.66 s |
| ref | deck seat | `km3` | 80 | 0.93 / 0.85 / 1.73 / 2.61 s | 1.08 | 24.4 | 15.7 / 7.9 / 61.7 / 170.4 | 0.38 s |
| ref | opponent seat | `km3` | 80 |  |  | 27.7 | 19.0 / 8.0 / 71.8 / 441.0 | 0.53 s |

One paired game (both arms) took 14 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 80 | 47.0 | +26.2 ± 10.3 | 341 / 261, 15.3 h | 945 / 865, 2.1 days |
| brew-08-entei-rainbow-cave | 80 | 47.0 | +26.2 ± 10.3 | 341 / 261, 15.3 h | 945 / 865, 2.1 days |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
