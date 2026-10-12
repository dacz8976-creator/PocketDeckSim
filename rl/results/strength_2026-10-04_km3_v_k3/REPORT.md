# Strength report: km3_v_k3

Pilot **km3** against reference **k3**, stage `dev`. Manifest sha256 `d7b22db0d7e01f4f` (matches the pre-registration); registered 2026-10-04T14:19:19Z.

> Run B (km3 on the deck, k3 the opponent and the reference). The exploit check of the kx3 development result (+16.6 +- 3.5 against km3, rl/results/strength_2026-10-03_kx3_dev). kx3 plays its play-outs with km3 on both sides, so against a km3 opponent its model of the opponent is exact. Here the opponent is k3, a different pilot, on the first 3 of the same deals (same seeds, both seats). Two paired runs share their reference arm (k3 v k3): run A has kx3 on the deck, run B has km3 on the deck. The pre-registered reading is the per-deal difference between the two runs' X arms, kx3 minus km3 against k3, pooled with mean +- 1.96 sd/sqrt(n) and printed per deck; each run's own report is read too. If the gain against k3 is near the gain against km3, kx3's edge is not just exploiting km3; if it is much smaller, part of it was. REALISTIC mode; development decks only; held-out decks locked out.

Pre-registration order: registered 2026-10-04T14:19:19Z; first game started 2026-10-04T15:11:45Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=k3 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=121 digest=bd62fa9645b3002d`; `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`

- Planned 672 games; finished 672; complete pairs 336 (= 672 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 336 paired games: +1.3 ± 4.2 points** (arm X 44.6% vs arm ref 43.3% score).
Decks weighted equally (7 decks): +1.3 ± 2.9 (sd across deck means 3.9).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 09-mega-manectric-heliolisk | 48 | 60.4% | 64.6% | -4.2 ± 11.6 | -16.7 ± 15.2 | +8.3 ± 16.3 |
| 06-mega-blaziken-tournament-list | 48 | 60.4% | 55.2% | +5.2 ± 14.9 | -4.5 ± 20.3 | +13.5 ± 21.4 |
| 10-xatu-oricorio-tr-weezing | 48 | 16.7% | 18.8% | -2.1 ± 7.1 | +0.0 ± 11.8 | -4.2 ± 8.2 |
| 03-wailord-indeedee-wall | 48 | 67.7% | 63.5% | +4.2 ± 8.2 | +4.3 ± 15.0 | +4.0 ± 7.8 |
| 01-muk-glimmora-kingambit-regigigas | 48 | 24.0% | 24.0% | +0.0 ± 11.7 | +6.7 ± 16.1 | -11.1 ± 14.9 |
| 05-indeedee-stoutland | 48 | 31.2% | 25.0% | +6.2 ± 12.2 | +0.0 ± 19.6 | +13.0 ± 14.1 |
| draft-A-shark-tempo | 48 | 52.1% | 52.1% | +0.0 ± 10.1 | +4.2 ± 14.3 | -4.2 ± 14.3 |

Overall by who went first (identical in both arms): deck first -0.6 ± 6.2 (n=172); deck second +3.4 ± 5.6 (n=164).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 01-muk-glimmora-kingambit-regigigas | t-altaria | 6 | 33.3% | 50.0% | -16.7 ± 32.7 |
| 01-muk-glimmora-kingambit-regigigas | t-blaziken | 6 | 0.0% | 16.7% | -16.7 ± 32.7 |
| 01-muk-glimmora-kingambit-regigigas | t-hydreigon | 6 | 75.0% | 75.0% | +0.0 ± 0.0 |
| 01-muk-glimmora-kingambit-regigigas | t-lucario | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 01-muk-glimmora-kingambit-regigigas | t-sceptile | 6 | 33.3% | 33.3% | +0.0 ± 50.6 |
| 01-muk-glimmora-kingambit-regigigas | t-suicune | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 01-muk-glimmora-kingambit-regigigas | t-vespiquen | 6 | 0.0% | 16.7% | -16.7 ± 32.7 |
| 01-muk-glimmora-kingambit-regigigas | t-weezing | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 03-wailord-indeedee-wall | t-altaria | 6 | 100.0% | 100.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-blaziken | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 03-wailord-indeedee-wall | t-hydreigon | 6 | 83.3% | 66.7% | +16.7 ± 32.7 |
| 03-wailord-indeedee-wall | t-lucario | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-sceptile | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| 03-wailord-indeedee-wall | t-suicune | 6 | 75.0% | 75.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-vespiquen | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-weezing | 6 | 66.7% | 83.3% | -16.7 ± 32.7 |
| 05-indeedee-stoutland | t-altaria | 6 | 33.3% | 33.3% | +0.0 ± 0.0 |
| 05-indeedee-stoutland | t-blaziken | 6 | 33.3% | 50.0% | -16.7 ± 32.7 |
| 05-indeedee-stoutland | t-hydreigon | 6 | 50.0% | 16.7% | +33.3 ± 41.3 |
| 05-indeedee-stoutland | t-lucario | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 05-indeedee-stoutland | t-sceptile | 6 | 16.7% | 0.0% | +16.7 ± 32.7 |
| 05-indeedee-stoutland | t-suicune | 6 | 33.3% | 0.0% | +33.3 ± 41.3 |
| 05-indeedee-stoutland | t-vespiquen | 6 | 16.7% | 33.3% | -16.7 ± 32.7 |
| 05-indeedee-stoutland | t-weezing | 6 | 16.7% | 33.3% | -16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-altaria | 6 | 50.0% | 33.3% | +16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-blaziken | 6 | 83.3% | 66.7% | +16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-hydreigon | 6 | 83.3% | 91.7% | -8.3 ± 16.3 |
| 06-mega-blaziken-tournament-list | t-lucario | 6 | 83.3% | 33.3% | +50.0 ± 43.8 |
| 06-mega-blaziken-tournament-list | t-sceptile | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| 06-mega-blaziken-tournament-list | t-suicune | 6 | 50.0% | 50.0% | +0.0 ± 50.6 |
| 06-mega-blaziken-tournament-list | t-vespiquen | 6 | 50.0% | 83.3% | -33.3 ± 41.3 |
| 06-mega-blaziken-tournament-list | t-weezing | 6 | 16.7% | 33.3% | -16.7 ± 60.2 |
| 09-mega-manectric-heliolisk | t-altaria | 6 | 50.0% | 66.7% | -16.7 ± 60.2 |
| 09-mega-manectric-heliolisk | t-blaziken | 6 | 33.3% | 33.3% | +0.0 ± 50.6 |
| 09-mega-manectric-heliolisk | t-hydreigon | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-lucario | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| 09-mega-manectric-heliolisk | t-sceptile | 6 | 50.0% | 66.7% | -16.7 ± 32.7 |
| 09-mega-manectric-heliolisk | t-suicune | 6 | 83.3% | 83.3% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-vespiquen | 6 | 50.0% | 66.7% | -16.7 ± 32.7 |
| 09-mega-manectric-heliolisk | t-weezing | 6 | 66.7% | 66.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-altaria | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-blaziken | 6 | 33.3% | 16.7% | +16.7 ± 32.7 |
| 10-xatu-oricorio-tr-weezing | t-hydreigon | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-lucario | 6 | 16.7% | 50.0% | -33.3 ± 41.3 |
| 10-xatu-oricorio-tr-weezing | t-sceptile | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-suicune | 6 | 0.0% | 0.0% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-vespiquen | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-weezing | 6 | 16.7% | 16.7% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-altaria | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| draft-A-shark-tempo | t-blaziken | 6 | 66.7% | 66.7% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-hydreigon | 6 | 83.3% | 83.3% | +0.0 ± 50.6 |
| draft-A-shark-tempo | t-lucario | 6 | 16.7% | 33.3% | -16.7 ± 32.7 |
| draft-A-shark-tempo | t-sceptile | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-suicune | 6 | 50.0% | 50.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-vespiquen | 6 | 66.7% | 50.0% | +16.7 ± 32.7 |
| draft-A-shark-tempo | t-weezing | 6 | 16.7% | 33.3% | -16.7 ± 32.7 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `km3` | 336 | 0.46 / 0.35 / 1.25 / 2.53 s | 2.15 | 28.4 | 8.4 / 3.6 / 32.5 / 253.2 | 0.24 s |
| X | opponent seat | `k3` | 336 |  |  | 25.8 | 8.4 / 3.4 / 33.2 / 182.7 | 0.22 s |
| ref | deck seat | `k3` | 336 | 0.40 / 0.30 / 1.19 / 1.69 s | 2.49 | 26.2 | 7.4 / 3.1 / 28.6 / 212.3 | 0.20 s |
| ref | opponent seat | `k3` | 336 |  |  | 24.8 | 8.0 / 3.4 / 30.9 / 221.0 | 0.20 s |

One paired game (both arms) took 0.87 s on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 336 | 39.1 | +1.3 ± 4.2 | 235 / 0, 0.00 s | 653 / 317, 2 min |
| 09-mega-manectric-heliolisk | 48 | 41.0 | -4.2 ± 11.6 | 259 / 211, 54 s | 719 / 671, 3 min |
| 06-mega-blaziken-tournament-list | 48 | 52.8 | +5.2 ± 14.9 | 429 / 381, 84 s | 1192 / 1144, 4 min |
| 10-xatu-oricorio-tr-weezing | 48 | 25.2 | -2.1 ± 7.1 | 98 / 50, 14 s | 271 / 223, 62 s |
| 03-wailord-indeedee-wall | 48 | 28.9 | +4.2 ± 8.2 | 129 / 81, 65 s | 356 / 308, 4 min |
| 01-muk-glimmora-kingambit-regigigas | 48 | 41.3 | +0.0 ± 11.7 | 262 / 214, 2 min | 727 / 679, 7 min |
| 05-indeedee-stoutland | 48 | 43.3 | +6.2 ± 12.2 | 289 / 241, 2 min | 801 / 753, 6 min |
| draft-A-shark-tempo | 48 | 35.7 | +0.0 ± 10.1 | 197 / 149, 53 s | 545 / 497, 3 min |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 43.8% | 45.8% | -2.1 ± 7.1 |  |  |
