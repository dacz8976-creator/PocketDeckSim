# Strength report: slow_report_smoke-held

Pilot **km3** against reference **km3**, stage `use`. Manifest sha256 `af361717b158cdd3` (matches the pre-registration); registered 2026-10-07T23:09:22Z.

> km3 (smoke, not kx3) on smoke-held v km3 on the public panel. A slow report on one deck, not development: how does smoke-held do when the strong, slow pilot km3 plays it against the eight public panel lists played by km3, 2 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better km3 plays this deck than km3 on the same deals. Realistic knowledge: km3 plays the deck knowing its own cards; the deck is never one of the lists km3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-07T23:09:22Z; first game started 2026-10-07T23:09:22Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (given in the config (copied from the pin; the program sha256 is the one named there))

- Planned 64 games; finished 64; complete pairs 32 (= 64 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 32 paired games: +0.0 ± 0.0 points** (arm X 59.4% vs arm ref 59.4% score).


**Every paired difference is exactly 0** (32 of 32 paired games identical in winner, points and turns): the two arms played the same games.

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| smoke-held | 32 | 59.4% | 59.4% | +0.0 ± 0.0 | +0.0 ± 0.0 | +0.0 ± 0.0 |

Overall by who went first (identical in both arms): deck first +0.0 ± 0.0 (n=17); deck second +0.0 ± 0.0 (n=15).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| smoke-held | t-altaria | 4 | 50.0% | 50.0% | +0.0 ± 0.0 |
| smoke-held | t-blaziken | 4 | 25.0% | 25.0% | +0.0 ± 0.0 |
| smoke-held | t-hydreigon | 4 | 50.0% | 50.0% | +0.0 ± 0.0 |
| smoke-held | t-lucario | 4 | 50.0% | 50.0% | +0.0 ± 0.0 |
| smoke-held | t-sceptile | 4 | 50.0% | 50.0% | +0.0 ± 0.0 |
| smoke-held | t-suicune | 4 | 100.0% | 100.0% | +0.0 ± 0.0 |
| smoke-held | t-vespiquen | 4 | 50.0% | 50.0% | +0.0 ± 0.0 |
| smoke-held | t-weezing | 4 | 100.0% | 100.0% | +0.0 ± 0.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `km3` | 32 | 0.81 / 0.68 / 2.03 / 2.12 s | 1.23 | 28.1 | 12.4 / 5.2 / 53.0 / 143.9 | 0.35 s |
| X | opponent seat | `km3` | 32 |  |  | 31.4 | 14.4 / 6.3 / 60.6 / 211.4 | 0.45 s |
| ref | deck seat | `km3` | 32 | 0.80 / 0.69 / 2.08 / 2.13 s | 1.25 | 28.1 | 12.1 / 4.9 / 51.5 / 230.6 | 0.34 s |
| ref | opponent seat | `km3` | 32 |  |  | 31.4 | 14.3 / 6.2 / 55.9 / 437.2 | 0.45 s |

One paired game (both arms) took 1.61 s on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 32 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |
| smoke-held | 32 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
