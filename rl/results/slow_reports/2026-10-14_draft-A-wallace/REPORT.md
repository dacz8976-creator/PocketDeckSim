# Strength report: slow_report_draft-A-wallace

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `34add72c2823d74c` (matches the pre-registration); registered 2026-10-15T02:39:55Z.

> kx3 (d513e37b, on main-c045ede) on draft-A-wallace v km3 on the public panel. A slow report on one deck, not development: how does draft-A-wallace do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-15T02:39:55Z; first game started 2026-10-15T02:39:58Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit b89b7ebea31d): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit b89b7ebea31d): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 200; complete pairs 100 (= 200 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 100 paired games: +16.0 ± 8.7 points** (arm X 64.0% vs arm ref 48.0% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| draft-A-wallace | 100 | 64.0% | 48.0% | +16.0 ± 8.7 | +21.2 ± 12.4 | +10.4 ± 12.0 |

Overall by who went first (identical in both arms): deck first +21.2 ± 12.4 (n=52); deck second +10.4 ± 12.0 (n=48).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| draft-A-wallace | t-altaria | 20 | 60.0% | 35.0% | +25.0 ± 19.5 |
| draft-A-wallace | t-blaziken | 20 | 80.0% | 70.0% | +10.0 ± 13.5 |
| draft-A-wallace | t-hydreigon | 20 | 65.0% | 65.0% | +0.0 ± 14.2 |
| draft-A-wallace | t-lucario | 20 | 70.0% | 50.0% | +20.0 ± 27.0 |
| draft-A-wallace | t-sceptile | 20 | 45.0% | 20.0% | +25.0 ± 19.5 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 100 | 601.78 / 546.37 / 1083.41 / 1461.64 s | 0.00 | 24.2 | 24862.8 / 23636.2 / 48031.8 / 91825.8 | 10 min |
| X | opponent seat | `km3` | 100 |  |  | 24.1 | 13.7 / 6.7 / 52.4 / 200.3 | 0.33 s |
| ref | deck seat | `km3` | 100 | 0.58 / 0.57 / 1.07 / 1.71 s | 1.74 | 23.9 | 12.4 / 5.5 / 48.0 / 265.4 | 0.30 s |
| ref | opponent seat | `km3` | 100 |  |  | 24.2 | 10.9 / 5.8 / 39.7 / 164.1 | 0.26 s |

One paired game (both arms) took 10 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 100 | 44.3 | +16.0 ± 8.7 | 302 / 202, 8.4 h | 839 / 739, 30.9 h |
| draft-A-wallace | 100 | 44.3 | +16.0 ± 8.7 | 302 / 202, 8.4 h | 839 / 739, 30.9 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
