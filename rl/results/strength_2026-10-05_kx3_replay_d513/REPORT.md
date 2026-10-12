# Strength report: kx3_replay_d513

Pilot **kx3** against reference **k3**, stage `dev`. Manifest sha256 `e6ea8a46d6897a06` (matches the pre-registration); registered 2026-10-05T05:46:09Z.

> The build check the freeze needs (the k3 check pre-registration addendum, item 2). With the d513e37b program, replay 56 of run A's kx3 games (strength_2026-10-04_kx3_v_k3: deal 0, seat 0, every pair, same seeds, k3 the opponent and reference). Every game must equal run A's: winner, points, turns, plies and every logged decision. If any differs: hold the freeze and rerun the k3 check on d513e37b. Compared by compare_with_run_a.py in this folder.

Pre-registration order: registered 2026-10-05T05:46:09Z; first game started 2026-10-05T06:34:25Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=k3 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=121 digest=bd62fa9645b3002d`; `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`

- Planned 112 games; finished 112; complete pairs 56 (= 112 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 56 paired games: +17.9 ± 12.3 points** (arm X 56.2% vs arm ref 38.4% score).
Decks weighted equally (7 decks): +17.9 ± 9.0 (sd across deck means 12.2).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 09-mega-manectric-heliolisk | 8 | 87.5% | 75.0% | +12.5 ± 24.5 | +16.7 ± 32.7 | +0.0 ± 0.0 |
| 06-mega-blaziken-tournament-list | 8 | 75.0% | 50.0% | +25.0 ± 32.1 | +20.0 ± 39.2 | +33.3 ± 65.3 |
| 10-xatu-oricorio-tr-weezing | 8 | 12.5% | 0.0% | +12.5 ± 24.5 | +0.0 ± 0.0 | +50.0 ± 98.0 |
| 03-wailord-indeedee-wall | 8 | 75.0% | 62.5% | +12.5 ± 44.4 | +0.0 ± 62.0 | +33.3 ± 65.3 |
| 01-muk-glimmora-kingambit-regigigas | 8 | 31.2% | 6.2% | +25.0 ± 32.1 | +40.0 ± 48.0 | +0.0 ± 0.0 |
| 05-indeedee-stoutland | 8 | 50.0% | 12.5% | +37.5 ± 35.9 | +40.0 ± 48.0 | +33.3 ± 65.3 |
| draft-A-shark-tempo | 8 | 62.5% | 62.5% | +0.0 ± 37.0 | +0.0 ± 0.0 | +0.0 ± 62.0 |

Overall by who went first (identical in both arms): deck first +17.1 ± 15.0 (n=35); deck second +19.0 ± 21.9 (n=21).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 01-muk-glimmora-kingambit-regigigas | t-altaria | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-blaziken | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-hydreigon | 1 | 50.0% | 50.0% | +0.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-lucario | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-sceptile | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-suicune | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-vespiquen | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 01-muk-glimmora-kingambit-regigigas | t-weezing | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 03-wailord-indeedee-wall | t-altaria | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 03-wailord-indeedee-wall | t-blaziken | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 03-wailord-indeedee-wall | t-hydreigon | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 03-wailord-indeedee-wall | t-lucario | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 03-wailord-indeedee-wall | t-sceptile | 1 | 0.0% | 100.0% | -100.0 (n=1) |
| 03-wailord-indeedee-wall | t-suicune | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 03-wailord-indeedee-wall | t-vespiquen | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 03-wailord-indeedee-wall | t-weezing | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 05-indeedee-stoutland | t-altaria | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 05-indeedee-stoutland | t-blaziken | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 05-indeedee-stoutland | t-hydreigon | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 05-indeedee-stoutland | t-lucario | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 05-indeedee-stoutland | t-sceptile | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 05-indeedee-stoutland | t-suicune | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 05-indeedee-stoutland | t-vespiquen | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 05-indeedee-stoutland | t-weezing | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-altaria | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-blaziken | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-hydreigon | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-lucario | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-sceptile | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-suicune | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-vespiquen | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 06-mega-blaziken-tournament-list | t-weezing | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-altaria | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-blaziken | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-hydreigon | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-lucario | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-sceptile | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-suicune | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 09-mega-manectric-heliolisk | t-vespiquen | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 09-mega-manectric-heliolisk | t-weezing | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-altaria | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-blaziken | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-hydreigon | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-lucario | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-sceptile | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-suicune | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-vespiquen | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| 10-xatu-oricorio-tr-weezing | t-weezing | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| draft-A-shark-tempo | t-altaria | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| draft-A-shark-tempo | t-blaziken | 1 | 100.0% | 0.0% | +100.0 (n=1) |
| draft-A-shark-tempo | t-hydreigon | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| draft-A-shark-tempo | t-lucario | 1 | 0.0% | 100.0% | -100.0 (n=1) |
| draft-A-shark-tempo | t-sceptile | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| draft-A-shark-tempo | t-suicune | 1 | 0.0% | 0.0% | +0.0 (n=1) |
| draft-A-shark-tempo | t-vespiquen | 1 | 100.0% | 100.0% | +0.0 (n=1) |
| draft-A-shark-tempo | t-weezing | 1 | 0.0% | 0.0% | +0.0 (n=1) |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 56 | 302.16 / 146.95 / 1040.23 / 1627.50 s | 0.00 | 28.2 | 10696.2 / 7681.8 / 32339.9 / 60659.1 | 5 min |
| X | opponent seat | `k3` | 56 |  |  | 27.0 | 13.2 / 5.3 / 54.7 / 267.3 | 0.36 s |
| ref | deck seat | `k3` | 56 | 0.83 / 0.62 / 2.30 / 2.80 s | 1.20 | 25.6 | 14.5 / 5.8 / 55.0 / 574.3 | 0.37 s |
| ref | opponent seat | `k3` | 56 |  |  | 25.0 | 17.9 / 6.9 / 71.3 / 359.1 | 0.45 s |

One paired game (both arms) took 5 min on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 56 | 47.1 | +17.9 ± 12.3 | 342 / 286, 12.0 h | 948 / 892, 37.5 h |
| 09-mega-manectric-heliolisk | 8 | 35.4 | +12.5 ± 24.5 | 193 / 185, 3.0 h | 534 / 526, 8.6 h |
| 06-mega-blaziken-tournament-list | 8 | 46.3 | +25.0 ± 32.1 | 330 / 322, 5.0 h | 915 / 907, 14.1 h |
| 10-xatu-oricorio-tr-weezing | 8 | 35.4 | +12.5 ± 24.5 | 193 / 185, 2.9 h | 534 / 526, 8.3 h |
| 03-wailord-indeedee-wall | 8 | 64.1 | +12.5 ± 44.4 | 632 / 624, 2.9 days | 1754 / 1746, 8.0 days |
| 01-muk-glimmora-kingambit-regigigas | 8 | 46.3 | +25.0 ± 32.1 | 330 / 322, 17.4 h | 915 / 907, 2.0 days |
| 05-indeedee-stoutland | 8 | 51.8 | +37.5 ± 35.9 | 412 / 404, 24.2 h | 1144 / 1136, 2.8 days |
| draft-A-shark-tempo | 8 | 53.5 | +0.0 ± 37.0 | 440 / 432, 9.7 h | 1220 / 1212, 27.3 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 37.5% | 37.5% | +0.0 ± 0.0 |  |  |
