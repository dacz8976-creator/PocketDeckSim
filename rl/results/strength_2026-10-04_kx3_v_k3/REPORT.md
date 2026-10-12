# Strength report: kx3_v_k3

Pilot **kx3** against reference **k3**, stage `dev`. Manifest sha256 `b1bd74601de31995` (matches the pre-registration); registered 2026-10-04T14:19:30Z.

> Run A (kx3 on the deck, k3 the opponent and the reference). The exploit check of the kx3 development result (+16.6 +- 3.5 against km3, rl/results/strength_2026-10-03_kx3_dev). kx3 plays its play-outs with km3 on both sides, so against a km3 opponent its model of the opponent is exact. Here the opponent is k3, a different pilot, on the first 3 of the same deals (same seeds, both seats). Two paired runs share their reference arm (k3 v k3): run A has kx3 on the deck, run B has km3 on the deck. The pre-registered reading is the per-deal difference between the two runs' X arms, kx3 minus km3 against k3, pooled with mean +- 1.96 sd/sqrt(n) and printed per deck; each run's own report is read too. If the gain against k3 is near the gain against km3, kx3's edge is not just exploiting km3; if it is much smaller, part of it was. REALISTIC mode; development decks only; held-out decks locked out.

Pre-registration order: registered 2026-10-04T14:19:30Z; first game started 2026-10-04T15:19:04Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=k3 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=121 digest=bd62fa9645b3002d`; `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`

- Planned 672 games; finished 672; complete pairs 336 (= 672 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 336 paired games: +16.5 ± 4.9 points** (arm X 59.8% vs arm ref 43.3% score).
Decks weighted equally (7 decks): +16.5 ± 6.3 (sd across deck means 8.5).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 09-mega-manectric-heliolisk | 48 | 72.9% | 64.6% | +8.3 ± 11.4 | +4.2 ± 14.3 | +12.5 ± 17.9 |
| 06-mega-blaziken-tournament-list | 48 | 72.9% | 55.2% | +17.7 ± 12.9 | +9.1 ± 17.8 | +25.0 ± 18.2 |
| 10-xatu-oricorio-tr-weezing | 48 | 22.9% | 18.8% | +4.2 ± 11.6 | +4.2 ± 14.3 | +4.2 ± 18.6 |
| 03-wailord-indeedee-wall | 48 | 78.1% | 63.5% | +14.6 ± 11.7 | +13.0 ± 18.7 | +16.0 ± 14.7 |
| 01-muk-glimmora-kingambit-regigigas | 48 | 53.1% | 24.0% | +29.2 ± 15.4 | +36.7 ± 19.9 | +16.7 ± 23.8 |
| 05-indeedee-stoutland | 48 | 47.9% | 25.0% | +22.9 ± 14.6 | +20.0 ± 22.6 | +26.1 ± 18.3 |
| draft-A-shark-tempo | 48 | 70.8% | 52.1% | +18.8 ± 12.6 | +20.8 ± 16.6 | +16.7 ± 19.3 |

Overall by who went first (identical in both arms): deck first +16.3 ± 7.0 (n=172); deck second +16.8 ± 7.0 (n=164).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 01-muk-glimmora-kingambit-regigigas | t-altaria | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 01-muk-glimmora-kingambit-regigigas | t-blaziken | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 01-muk-glimmora-kingambit-regigigas | t-hydreigon | 6 | 75.0% | 75.0% | +0.0 ± 0.0 |
| 01-muk-glimmora-kingambit-regigigas | t-lucario | 6 | 66.7% | 0.0% | +66.7 ± 41.3 |
| 01-muk-glimmora-kingambit-regigigas | t-sceptile | 6 | 33.3% | 33.3% | +0.0 ± 50.6 |
| 01-muk-glimmora-kingambit-regigigas | t-suicune | 6 | 66.7% | 0.0% | +66.7 ± 41.3 |
| 01-muk-glimmora-kingambit-regigigas | t-vespiquen | 6 | 50.0% | 16.7% | +33.3 ± 65.3 |
| 01-muk-glimmora-kingambit-regigigas | t-weezing | 6 | 50.0% | 0.0% | +50.0 ± 43.8 |
| 03-wailord-indeedee-wall | t-altaria | 6 | 100.0% | 100.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-blaziken | 6 | 66.7% | 33.3% | +33.3 ± 41.3 |
| 03-wailord-indeedee-wall | t-hydreigon | 6 | 83.3% | 66.7% | +16.7 ± 32.7 |
| 03-wailord-indeedee-wall | t-lucario | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-sceptile | 6 | 66.7% | 50.0% | +16.7 ± 60.2 |
| 03-wailord-indeedee-wall | t-suicune | 6 | 75.0% | 75.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-vespiquen | 6 | 83.3% | 50.0% | +33.3 ± 41.3 |
| 03-wailord-indeedee-wall | t-weezing | 6 | 100.0% | 83.3% | +16.7 ± 32.7 |
| 05-indeedee-stoutland | t-altaria | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 05-indeedee-stoutland | t-blaziken | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 05-indeedee-stoutland | t-hydreigon | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 05-indeedee-stoutland | t-lucario | 6 | 50.0% | 33.3% | +16.7 ± 60.2 |
| 05-indeedee-stoutland | t-sceptile | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 05-indeedee-stoutland | t-suicune | 6 | 83.3% | 0.0% | +83.3 ± 32.7 |
| 05-indeedee-stoutland | t-vespiquen | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 05-indeedee-stoutland | t-weezing | 6 | 16.7% | 33.3% | -16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-altaria | 6 | 66.7% | 33.3% | +33.3 ± 41.3 |
| 06-mega-blaziken-tournament-list | t-blaziken | 6 | 83.3% | 66.7% | +16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-hydreigon | 6 | 83.3% | 91.7% | -8.3 ± 16.3 |
| 06-mega-blaziken-tournament-list | t-lucario | 6 | 100.0% | 33.3% | +66.7 ± 41.3 |
| 06-mega-blaziken-tournament-list | t-sceptile | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-suicune | 6 | 66.7% | 50.0% | +16.7 ± 60.2 |
| 06-mega-blaziken-tournament-list | t-vespiquen | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 06-mega-blaziken-tournament-list | t-weezing | 6 | 33.3% | 33.3% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-altaria | 6 | 66.7% | 66.7% | +0.0 ± 50.6 |
| 09-mega-manectric-heliolisk | t-blaziken | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 09-mega-manectric-heliolisk | t-hydreigon | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-lucario | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| 09-mega-manectric-heliolisk | t-sceptile | 6 | 66.7% | 66.7% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-suicune | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-vespiquen | 6 | 66.7% | 66.7% | +0.0 ± 50.6 |
| 09-mega-manectric-heliolisk | t-weezing | 6 | 100.0% | 66.7% | +33.3 ± 41.3 |
| 10-xatu-oricorio-tr-weezing | t-altaria | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-blaziken | 6 | 33.3% | 16.7% | +16.7 ± 60.2 |
| 10-xatu-oricorio-tr-weezing | t-hydreigon | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 10-xatu-oricorio-tr-weezing | t-lucario | 6 | 33.3% | 50.0% | -16.7 ± 32.7 |
| 10-xatu-oricorio-tr-weezing | t-sceptile | 6 | 16.7% | 16.7% | +0.0 ± 50.6 |
| 10-xatu-oricorio-tr-weezing | t-suicune | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 10-xatu-oricorio-tr-weezing | t-vespiquen | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-weezing | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-altaria | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| draft-A-shark-tempo | t-blaziken | 6 | 100.0% | 66.7% | +33.3 ± 41.3 |
| draft-A-shark-tempo | t-hydreigon | 6 | 100.0% | 83.3% | +16.7 ± 32.7 |
| draft-A-shark-tempo | t-lucario | 6 | 33.3% | 33.3% | +0.0 ± 50.6 |
| draft-A-shark-tempo | t-sceptile | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-suicune | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-vespiquen | 6 | 100.0% | 50.0% | +50.0 ± 43.8 |
| draft-A-shark-tempo | t-weezing | 6 | 66.7% | 33.3% | +33.3 ± 41.3 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3` | 336 | 304.61 / 176.88 / 1001.10 / 1966.02 s | 0.00 | 29.1 | 10436.9 / 7434.1 / 30155.9 / 81358.1 | 5 min |
| X | opponent seat | `k3` | 336 |  |  | 26.6 | 15.2 / 5.4 / 60.1 / 1030.3 | 0.40 s |
| ref | deck seat | `k3` | 336 | 0.82 / 0.61 / 2.63 / 5.27 s | 1.22 | 26.2 | 15.1 / 5.9 / 61.0 / 408.5 | 0.40 s |
| ref | opponent seat | `k3` | 336 |  |  | 24.8 | 16.5 / 6.7 / 63.1 / 4057.4 | 0.41 s |

One paired game (both arms) took 5 min on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 336 | 46.1 | +16.5 ± 4.9 | 327 / 0, 0.00 s | 906 / 570, 24.2 h |
| 09-mega-manectric-heliolisk | 48 | 40.4 | +8.3 ± 11.4 | 251 / 203, 3.2 h | 697 / 649, 10.3 h |
| 06-mega-blaziken-tournament-list | 48 | 45.5 | +17.7 ± 12.9 | 319 / 271, 3.8 h | 886 / 838, 11.8 h |
| 10-xatu-oricorio-tr-weezing | 48 | 41.0 | +4.2 ± 11.6 | 259 / 211, 3.8 h | 719 / 671, 12.1 h |
| 03-wailord-indeedee-wall | 48 | 41.2 | +14.6 ± 11.7 | 261 / 213, 23.5 h | 725 / 677, 3.1 days |
| 01-muk-glimmora-kingambit-regigigas | 48 | 54.4 | +29.2 ± 15.4 | 455 / 407, 25.6 h | 1264 / 1216, 3.2 days |
| 05-indeedee-stoutland | 48 | 51.5 | +22.9 ± 14.6 | 408 / 360, 18.0 h | 1134 / 1086, 2.3 days |
| draft-A-shark-tempo | 48 | 44.5 | +18.8 ± 12.6 | 305 / 257, 6.7 h | 846 / 798, 20.7 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 41.7% | 45.8% | -4.2 ± 10.0 |  |  |
