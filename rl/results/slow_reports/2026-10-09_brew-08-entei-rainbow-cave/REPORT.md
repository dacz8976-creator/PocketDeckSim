# Strength report: slow_report_brew-08-entei-rainbow-cave

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `cf90a886ef22e9d4` (matches the pre-registration); registered 2026-10-09T15:29:52Z.

> kx3 (d513e37b) on brew-08-entei-rainbow-cave v km3 on the public panel. A slow report on one deck, not development: how does brew-08-entei-rainbow-cave do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-09T15:29:52Z; first game started 2026-10-09T15:38:31Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (replayed by slow_report.py on the registering machine just before registration (equal to the committed pin)); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (replayed by slow_report.py on the registering machine just before registration (equal to the committed pin))

- Planned 320 games; finished 320; complete pairs 160 (= 320 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 160 paired games: +13.1 ± 7.0 points** (arm X 75.6% vs arm ref 62.5% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| brew-08-entei-rainbow-cave | 160 | 75.6% | 62.5% | +13.1 ± 7.0 | +12.2 ± 10.6 | +14.0 ± 9.3 |

Overall by who went first (identical in both arms): deck first +12.2 ± 10.6 (n=74); deck second +14.0 ± 9.3 (n=86).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| brew-08-entei-rainbow-cave | t-altaria | 20 | 65.0% | 45.0% | +20.0 ± 22.9 |
| brew-08-entei-rainbow-cave | t-blaziken | 20 | 40.0% | 40.0% | +0.0 ± 20.1 |
| brew-08-entei-rainbow-cave | t-hydreigon | 20 | 85.0% | 75.0% | +10.0 ± 19.6 |
| brew-08-entei-rainbow-cave | t-lucario | 20 | 65.0% | 55.0% | +10.0 ± 19.6 |
| brew-08-entei-rainbow-cave | t-sceptile | 20 | 85.0% | 55.0% | +30.0 ± 20.6 |
| brew-08-entei-rainbow-cave | t-suicune | 20 | 85.0% | 65.0% | +20.0 ± 27.0 |
| brew-08-entei-rainbow-cave | t-vespiquen | 20 | 95.0% | 95.0% | +0.0 ± 0.0 |
| brew-08-entei-rainbow-cave | t-weezing | 20 | 85.0% | 70.0% | +15.0 ± 16.1 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 160 | 524.91 / 473.45 / 1021.95 / 1330.14 s | 0.00 | 22.3 | 23501.9 / 21658.6 / 47384.2 / 87389.6 | 9 min |
| X | opponent seat | `km3` | 160 |  |  | 25.2 | 14.2 / 6.2 / 58.4 / 227.0 | 0.36 s |
| ref | deck seat | `km3` | 160 | 0.56 / 0.53 / 1.08 / 1.59 s | 1.79 | 23.3 | 10.4 / 5.6 / 37.3 / 177.5 | 0.24 s |
| ref | opponent seat | `km3` | 160 |  |  | 26.7 | 11.4 / 5.2 / 43.6 / 229.9 | 0.30 s |

One paired game (both arms) took 9 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 160 | 45.0 | +13.1 ± 7.0 | 312 / 152, 5.5 h | 866 / 706, 25.8 h |
| brew-08-entei-rainbow-cave | 160 | 45.0 | +13.1 ± 7.0 | 312 / 152, 5.5 h | 866 / 706, 25.8 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
