# Strength report: slow_report_13-a-giant-cape

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `5807af275528b8a8` (matches the pre-registration); registered 2026-10-15T18:29:56Z.

> kx3 (d513e37b, on main-c045ede) on 13-a-giant-cape v km3 on the public panel. A slow report on one deck, not development: how does 13-a-giant-cape do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact. This is a PAIRED VARIANT, paired with rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate, which played 13-a-ninetales-raticate: 13-a-giant-cape differs from it by -1 Ilima A3 149, +1 Giant Cape A2 147 (the replaced card keeps its place in the deck file (card 17 of 20), and so in the shuffle: the deals differ only in that card). It plays the very same deals, with the same program and pin: the same seed base 24606700000 (no new seed slot is taken), seats, opponents and panel lists.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-15T18:29:56Z; first game started 2026-10-15T18:30:06Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration)

- Planned 320 games; finished 280; complete pairs 140 (= 280 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 140 paired games: +15.7 ± 6.4 points** (arm X 72.9% vs arm ref 57.1% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 13-a-giant-cape | 140 | 72.9% | 57.1% | +15.7 ± 6.4 | +13.6 ± 8.3 | +17.6 ± 9.5 |

Overall by who went first (identical in both arms): deck first +13.6 ± 8.3 (n=66); deck second +17.6 ± 9.5 (n=74).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 13-a-giant-cape | t-altaria | 20 | 35.0% | 15.0% | +20.0 ± 18.0 |
| 13-a-giant-cape | t-blaziken | 20 | 85.0% | 75.0% | +10.0 ± 13.5 |
| 13-a-giant-cape | t-hydreigon | 20 | 70.0% | 50.0% | +20.0 ± 18.0 |
| 13-a-giant-cape | t-lucario | 20 | 65.0% | 50.0% | +15.0 ± 16.1 |
| 13-a-giant-cape | t-sceptile | 20 | 75.0% | 65.0% | +10.0 ± 19.6 |
| 13-a-giant-cape | t-suicune | 20 | 100.0% | 75.0% | +25.0 ± 19.5 |
| 13-a-giant-cape | t-vespiquen | 20 | 80.0% | 70.0% | +10.0 ± 13.5 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 140 | 651.35 / 536.11 / 1613.39 / 2144.09 s | 0.00 | 25.2 | 25877.5 / 22335.4 / 59735.9 / 147127.8 | 11 min |
| X | opponent seat | `km3` | 140 |  |  | 24.5 | 13.5 / 6.0 / 55.3 / 290.7 | 0.33 s |
| ref | deck seat | `km3` | 140 | 0.68 / 0.62 / 1.38 / 2.56 s | 1.47 | 23.9 | 16.3 / 7.3 / 63.0 / 532.2 | 0.39 s |
| ref | opponent seat | `km3` | 140 |  |  | 23.8 | 11.5 / 5.3 / 45.7 / 240.2 | 0.27 s |

One paired game (both arms) took 11 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 140 | 38.4 | +15.7 ± 6.4 | 228 / 88, 4.0 h | 631 / 491, 22.2 h |
| 13-a-giant-cape | 140 | 38.4 | +15.7 ± 6.4 | 228 / 88, 4.0 h | 631 / 491, 22.2 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
