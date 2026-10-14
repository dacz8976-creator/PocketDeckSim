# Strength report: slow_report_brew-10-diancie-giratina

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `07cd3a3c7099988d` (matches the pre-registration); registered 2026-10-13T19:07:56Z.

> kx3 (d513e37b, on main-c045ede) on brew-10-diancie-giratina v km3 on the public panel. A slow report on one deck, not development: how does brew-10-diancie-giratina do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-13T19:07:56Z; first game started 2026-10-13T19:07:59Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 284; complete pairs 142 (= 284 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 142 paired games: +32.0 ± 8.8 points** (arm X 72.5% vs arm ref 40.5% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| brew-10-diancie-giratina | 142 | 72.5% | 40.5% | +32.0 ± 8.8 | +33.6 ± 12.4 | +30.3 ± 12.7 |

Overall by who went first (identical in both arms): deck first +33.6 ± 12.4 (n=76); deck second +30.3 ± 12.7 (n=66).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| brew-10-diancie-giratina | t-altaria | 20 | 80.0% | 47.5% | +32.5 ± 24.9 |
| brew-10-diancie-giratina | t-blaziken | 20 | 60.0% | 30.0% | +30.0 ± 25.0 |
| brew-10-diancie-giratina | t-hydreigon | 20 | 75.0% | 50.0% | +25.0 ± 28.0 |
| brew-10-diancie-giratina | t-lucario | 20 | 60.0% | 50.0% | +10.0 ± 19.6 |
| brew-10-diancie-giratina | t-sceptile | 20 | 70.0% | 55.0% | +15.0 ± 16.1 |
| brew-10-diancie-giratina | t-suicune | 20 | 75.0% | 15.0% | +60.0 ± 22.0 |
| brew-10-diancie-giratina | t-vespiquen | 20 | 90.0% | 40.0% | +50.0 ± 22.5 |
| brew-10-diancie-giratina | t-weezing | 2 | 50.0% | 0.0% | +50.0 ± 98.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 142 | 1681.88 / 1468.45 / 3288.99 / 4590.79 s | 0.00 | 26.9 | 62412.5 / 57399.1 / 127026.2 / 222383.7 | 28 min |
| X | opponent seat | `km3` | 142 |  |  | 24.9 | 27.1 / 10.7 / 105.9 / 552.1 | 0.68 s |
| ref | deck seat | `km3` | 142 | 1.23 / 1.07 / 2.52 / 3.64 s | 0.81 | 26.3 | 26.6 / 11.2 / 99.3 / 434.9 | 0.70 s |
| ref | opponent seat | `km3` | 142 |  |  | 24.1 | 21.3 / 8.9 / 82.5 / 296.9 | 0.51 s |

One paired game (both arms) took 28 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 142 | 53.7 | +32.0 ± 8.8 | 444 / 302, 35.3 h | 1232 / 1090, 5.3 days |
| brew-10-diancie-giratina | 142 | 53.7 | +32.0 ± 8.8 | 444 / 302, 35.3 h | 1232 / 1090, 5.3 days |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
