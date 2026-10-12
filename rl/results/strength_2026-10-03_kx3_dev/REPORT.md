# Strength report: kx3_dev

Pilot **kx3** against reference **km3**, stage `dev`. Manifest sha256 `3c8bac353ca09a23` (matches the pre-registration); registered 2026-10-03T03:18:14Z.

> REALISTIC (the default knowledge mode). Does the play-out chooser kx3 (km3 proposes; every distinct legal move, up to 12, is played out 16 times to the end of the game with km3 on both sides, each play-out from a world sampled from what the pilot may see: the opponent's hidden cards drawn from a pool of 8 meta lists consistent with the cards and Energy types seen so far; it switches only on a paired lead beyond 2 standard errors) play Dustin's development decks better than km3 does, on the same deals against the 8 panel lists? Primary: the pooled paired difference in game score (win 1, tie 1/2, loss 0) with its 95% interval; every deck's and every pair's row printed; time per game reported as a fact. Development only: the held-out decks are locked out. Caveat stated in advance: the 8 panel lists are also the pool's lists, so once a few cards are seen the pilot's guess of the opponent narrows to the right list; against a deck outside the pool it would not. A LAB run (exact list told, labelled) can follow on these same deals.

Pre-registration order: registered 2026-10-03T03:18:14Z; first game started 2026-10-03T04:06:19Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`; `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`

- Planned 1120 games; finished 1120; complete pairs 560 (= 1120 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 560 paired games: +16.6 ± 3.5 points** (arm X 57.6% vs arm ref 41.0% score).
Decks weighted equally (7 decks): +16.6 ± 6.5 (sd across deck means 8.7).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 09-mega-manectric-heliolisk | 80 | 76.2% | 60.0% | +16.2 ± 8.1 | +19.5 ± 12.3 | +12.8 ± 10.6 |
| 06-mega-blaziken-tournament-list | 80 | 65.0% | 50.0% | +15.0 ± 8.6 | +18.4 ± 12.5 | +11.9 ± 12.0 |
| 10-xatu-oricorio-tr-weezing | 80 | 25.0% | 18.8% | +6.2 ± 8.1 | +7.9 ± 11.4 | +4.8 ± 11.5 |
| 03-wailord-indeedee-wall | 80 | 80.6% | 74.4% | +6.2 ± 8.1 | +10.3 ± 14.0 | +2.4 ± 8.3 |
| 01-muk-glimmora-kingambit-regigigas | 80 | 43.8% | 15.0% | +28.7 ± 11.1 | +42.2 ± 14.6 | +11.4 ± 15.6 |
| 05-indeedee-stoutland | 80 | 47.5% | 21.2% | +26.2 ± 10.3 | +26.8 ± 13.7 | +25.6 ± 15.6 |
| draft-A-shark-tempo | 80 | 65.0% | 47.5% | +17.5 ± 9.7 | +12.8 ± 12.8 | +22.0 ± 14.5 |

Overall by who went first (identical in both arms): deck first +20.3 ± 5.1 (n=281); deck second +12.9 ± 4.8 (n=279).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 01-muk-glimmora-kingambit-regigigas | t-altaria | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 01-muk-glimmora-kingambit-regigigas | t-blaziken | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 01-muk-glimmora-kingambit-regigigas | t-hydreigon | 10 | 50.0% | 30.0% | +20.0 ± 26.1 |
| 01-muk-glimmora-kingambit-regigigas | t-lucario | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 01-muk-glimmora-kingambit-regigigas | t-sceptile | 10 | 30.0% | 20.0% | +10.0 ± 19.6 |
| 01-muk-glimmora-kingambit-regigigas | t-suicune | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 01-muk-glimmora-kingambit-regigigas | t-vespiquen | 10 | 50.0% | 10.0% | +40.0 ± 43.3 |
| 01-muk-glimmora-kingambit-regigigas | t-weezing | 10 | 40.0% | 20.0% | +20.0 ± 39.2 |
| 03-wailord-indeedee-wall | t-altaria | 10 | 90.0% | 100.0% | -10.0 ± 19.6 |
| 03-wailord-indeedee-wall | t-blaziken | 10 | 70.0% | 70.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-hydreigon | 10 | 80.0% | 70.0% | +10.0 ± 19.6 |
| 03-wailord-indeedee-wall | t-lucario | 10 | 60.0% | 70.0% | -10.0 ± 19.6 |
| 03-wailord-indeedee-wall | t-sceptile | 10 | 80.0% | 60.0% | +20.0 ± 39.2 |
| 03-wailord-indeedee-wall | t-suicune | 10 | 85.0% | 75.0% | +10.0 ± 19.6 |
| 03-wailord-indeedee-wall | t-vespiquen | 10 | 90.0% | 80.0% | +10.0 ± 19.6 |
| 03-wailord-indeedee-wall | t-weezing | 10 | 90.0% | 70.0% | +20.0 ± 26.1 |
| 05-indeedee-stoutland | t-altaria | 10 | 60.0% | 30.0% | +30.0 ± 29.9 |
| 05-indeedee-stoutland | t-blaziken | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 05-indeedee-stoutland | t-hydreigon | 10 | 50.0% | 30.0% | +20.0 ± 26.1 |
| 05-indeedee-stoutland | t-lucario | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 05-indeedee-stoutland | t-sceptile | 10 | 20.0% | 10.0% | +10.0 ± 19.6 |
| 05-indeedee-stoutland | t-suicune | 10 | 90.0% | 40.0% | +50.0 ± 32.7 |
| 05-indeedee-stoutland | t-vespiquen | 10 | 40.0% | 20.0% | +20.0 ± 39.2 |
| 05-indeedee-stoutland | t-weezing | 10 | 30.0% | 20.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-altaria | 10 | 30.0% | 10.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-blaziken | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-hydreigon | 10 | 60.0% | 40.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-lucario | 10 | 80.0% | 70.0% | +10.0 ± 35.2 |
| 06-mega-blaziken-tournament-list | t-sceptile | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-suicune | 10 | 60.0% | 50.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-vespiquen | 10 | 100.0% | 90.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-weezing | 10 | 50.0% | 40.0% | +10.0 ± 19.6 |
| 09-mega-manectric-heliolisk | t-altaria | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-blaziken | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 09-mega-manectric-heliolisk | t-hydreigon | 10 | 80.0% | 70.0% | +10.0 ± 19.6 |
| 09-mega-manectric-heliolisk | t-lucario | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-sceptile | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 09-mega-manectric-heliolisk | t-suicune | 10 | 90.0% | 60.0% | +30.0 ± 29.9 |
| 09-mega-manectric-heliolisk | t-vespiquen | 10 | 90.0% | 60.0% | +30.0 ± 29.9 |
| 09-mega-manectric-heliolisk | t-weezing | 10 | 90.0% | 70.0% | +20.0 ± 26.1 |
| 10-xatu-oricorio-tr-weezing | t-altaria | 10 | 40.0% | 40.0% | +0.0 ± 29.2 |
| 10-xatu-oricorio-tr-weezing | t-blaziken | 10 | 40.0% | 30.0% | +10.0 ± 35.2 |
| 10-xatu-oricorio-tr-weezing | t-hydreigon | 10 | 30.0% | 20.0% | +10.0 ± 19.6 |
| 10-xatu-oricorio-tr-weezing | t-lucario | 10 | 40.0% | 30.0% | +10.0 ± 19.6 |
| 10-xatu-oricorio-tr-weezing | t-sceptile | 10 | 20.0% | 20.0% | +0.0 ± 29.2 |
| 10-xatu-oricorio-tr-weezing | t-suicune | 10 | 0.0% | 0.0% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-vespiquen | 10 | 30.0% | 10.0% | +20.0 ± 26.1 |
| 10-xatu-oricorio-tr-weezing | t-weezing | 10 | 0.0% | 0.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-altaria | 10 | 60.0% | 40.0% | +20.0 ± 26.1 |
| draft-A-shark-tempo | t-blaziken | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| draft-A-shark-tempo | t-hydreigon | 10 | 90.0% | 70.0% | +20.0 ± 26.1 |
| draft-A-shark-tempo | t-lucario | 10 | 40.0% | 40.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-sceptile | 10 | 60.0% | 30.0% | +30.0 ± 29.9 |
| draft-A-shark-tempo | t-suicune | 10 | 50.0% | 40.0% | +10.0 ± 35.2 |
| draft-A-shark-tempo | t-vespiquen | 10 | 80.0% | 50.0% | +30.0 ± 41.8 |
| draft-A-shark-tempo | t-weezing | 10 | 70.0% | 60.0% | +10.0 ± 19.6 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 560 | 269.09 / 147.27 / 936.41 / 2227.82 s | 0.00 | 27.9 | 9642.1 / 6669.8 / 28491.8 / 91060.7 | 4 min |
| X | opponent seat | `km3` | 560 |  |  | 26.4 | 16.0 / 6.4 / 63.1 / 536.1 | 0.42 s |
| ref | deck seat | `km3` | 560 | 0.96 / 0.69 / 2.98 / 6.17 s | 1.04 | 27.4 | 16.6 / 6.4 / 68.9 / 742.6 | 0.45 s |
| ref | opponent seat | `km3` | 560 |  |  | 26.1 | 18.9 / 7.7 / 73.7 / 602.6 | 0.50 s |

One paired game (both arms) took 5 min on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 560 | 42.6 | +16.6 ± 3.5 | 280 / 0, 0.00 s | 776 / 216, 8.1 h |
| 09-mega-manectric-heliolisk | 80 | 37.1 | +16.2 ± 8.1 | 212 / 132, 1.8 h | 589 / 509, 6.8 h |
| 06-mega-blaziken-tournament-list | 80 | 39.3 | +15.0 ± 8.6 | 238 / 158, 1.9 h | 660 / 580, 7.0 h |
| 10-xatu-oricorio-tr-weezing | 80 | 36.8 | +6.2 ± 8.1 | 208 / 128, 2.2 h | 578 / 498, 8.6 h |
| 03-wailord-indeedee-wall | 80 | 36.8 | +6.2 ± 8.1 | 208 / 128, 13.7 h | 578 / 498, 2.2 days |
| 01-muk-glimmora-kingambit-regigigas | 80 | 50.8 | +28.7 ± 11.1 | 397 / 317, 13.8 h | 1102 / 1022, 44.6 h |
| 05-indeedee-stoutland | 80 | 47.0 | +26.2 ± 10.3 | 341 / 261, 12.2 h | 945 / 865, 40.4 h |
| draft-A-shark-tempo | 80 | 44.4 | +17.5 ± 9.7 | 303 / 223, 5.0 h | 841 / 761, 16.9 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 42.5% | 40.0% | +2.5 ± 7.0 |  |  |
