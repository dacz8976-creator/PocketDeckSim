# Strength report: slow_report_draft-A-wallace

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `34add72c2823d74c` (matches the pre-registration); registered 2026-10-15T02:39:55Z.

> kx3 (d513e37b, on main-c045ede) on draft-A-wallace v km3 on the public panel. A slow report on one deck, not development: how does draft-A-wallace do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-15T02:39:55Z; first game started 2026-10-15T02:39:58Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit b89b7ebea31d): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit b89b7ebea31d): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 320; complete pairs 160 (= 320 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 160 paired games: +15.6 ± 6.9 points** (arm X 66.9% vs arm ref 51.2% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| draft-A-wallace | 160 | 66.9% | 51.2% | +15.6 ± 6.9 | +17.9 ± 8.9 | +13.2 ± 10.6 |

Overall by who went first (identical in both arms): deck first +17.9 ± 8.9 (n=84); deck second +13.2 ± 10.6 (n=76).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| draft-A-wallace | t-altaria | 20 | 60.0% | 35.0% | +25.0 ± 19.5 |
| draft-A-wallace | t-blaziken | 20 | 80.0% | 70.0% | +10.0 ± 13.5 |
| draft-A-wallace | t-hydreigon | 20 | 65.0% | 65.0% | +0.0 ± 14.2 |
| draft-A-wallace | t-lucario | 20 | 70.0% | 50.0% | +20.0 ± 27.0 |
| draft-A-wallace | t-sceptile | 20 | 45.0% | 20.0% | +25.0 ± 19.5 |
| draft-A-wallace | t-suicune | 20 | 70.0% | 55.0% | +15.0 ± 16.1 |
| draft-A-wallace | t-vespiquen | 20 | 80.0% | 70.0% | +10.0 ± 19.6 |
| draft-A-wallace | t-weezing | 20 | 65.0% | 45.0% | +20.0 ± 22.9 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 160 | 887.91 / 647.91 / 2419.65 / 3164.75 s | 0.00 | 25.4 | 34876.8 / 29441.1 / 82055.7 / 185748.3 | 15 min |
| X | opponent seat | `km3` | 160 |  |  | 26.8 | 18.5 / 8.1 / 71.2 / 283.6 | 0.50 s |
| ref | deck seat | `km3` | 160 | 0.78 / 0.67 / 2.18 / 2.86 s | 1.28 | 25.1 | 14.2 / 6.3 / 53.8 / 265.4 | 0.36 s |
| ref | opponent seat | `km3` | 160 |  |  | 26.9 | 15.2 / 7.1 / 60.0 / 339.2 | 0.41 s |

One paired game (both arms) took 15 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 160 | 44.2 | +15.6 ± 6.9 | 301 / 141, 8.7 h | 835 / 675, 41.7 h |
| draft-A-wallace | 160 | 44.2 | +15.6 ± 6.9 | 301 / 141, 8.7 h | 835 / 675, 41.7 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
