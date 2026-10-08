# Strength report: slow_report_draft-A-wallace

Pilot **kx3** against reference **km3**, stage `use`. Manifest sha256 `4c833f24ec9b58e7` (matches the pre-registration); registered 2026-10-08T15:40:39Z.

> kx3 (d513e37b) on draft-A-wallace v km3 on the public panel. A slow report on one deck, not development: how does draft-A-wallace do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.

Pre-registration order: registered 2026-10-08T15:40:39Z; first game started 2026-10-08T15:42:25Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (replayed by slow_report.py on the registering machine just before registration (equal to the committed pin)); `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (replayed by slow_report.py on the registering machine just before registration (equal to the committed pin))

- Planned 320 games; finished 200; complete pairs 100 (= 200 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 100 paired games: +13.0 ± 8.7 points** (arm X 64.0% vs arm ref 51.0% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| draft-A-wallace | 100 | 64.0% | 51.0% | +13.0 ± 8.7 | +14.3 ± 12.8 | +11.8 ± 11.8 |

Overall by who went first (identical in both arms): deck first +14.3 ± 12.8 (n=49); deck second +11.8 ± 11.8 (n=51).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| draft-A-wallace | t-altaria | 20 | 40.0% | 40.0% | +0.0 ± 20.1 |
| draft-A-wallace | t-blaziken | 20 | 65.0% | 60.0% | +5.0 ± 9.8 |
| draft-A-wallace | t-hydreigon | 20 | 80.0% | 65.0% | +15.0 ± 21.4 |
| draft-A-wallace | t-lucario | 20 | 80.0% | 50.0% | +30.0 ± 20.6 |
| draft-A-wallace | t-sceptile | 20 | 55.0% | 40.0% | +15.0 ± 21.4 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 100 | 403.58 / 368.17 / 847.65 / 1006.29 s | 0.00 | 24.9 | 16197.2 / 15541.3 / 32313.5 / 67331.8 | 7 min |
| X | opponent seat | `km3` | 100 |  |  | 25.4 | 10.1 / 4.7 / 38.8 / 242.2 | 0.26 s |
| ref | deck seat | `km3` | 100 | 0.40 / 0.38 / 0.94 / 1.13 s | 2.51 | 24.4 | 8.0 / 3.7 / 29.2 / 155.8 | 0.19 s |
| ref | opponent seat | `km3` | 100 |  |  | 25.3 | 7.7 / 3.6 / 27.1 / 128.6 | 0.19 s |

One paired game (both arms) took 7 min on average; the run used 4 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 100 | 44.2 | +13.0 ± 8.7 | 300 / 200, 5.6 h | 833 / 733, 20.6 h |
| draft-A-wallace | 100 | 44.2 | +13.0 ± 8.7 | 300 / 200, 5.6 h | 833 / 733, 20.6 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
