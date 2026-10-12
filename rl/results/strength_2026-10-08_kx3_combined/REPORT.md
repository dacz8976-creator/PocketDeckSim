# Strength report: kx3_combined_v_frozen

Pilot **kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64** against reference **km3**, stage `dev`. Manifest sha256 `16fe75ad9e7c30a7` (matches the pre-registration); registered 2026-10-08T03:27:37Z.

> THE COMBINED CANDIDATE against the frozen kx3 (coordinator, Oct 7; Dustin chose the full run, Oct 7; rl/RUN5.md). Does kx3 with `_tools _zs3 _m64` together play Dustin's 7 development decks better or worse than the frozen kx3 (d513e37b, the development run's pilot)? `_tools`: the Tool rule in the play-outs and the within-noise Tool tie-break at kx3's own decision (gate 3: +0.2 +- 1.5 against the rule off). `_zs3`: a switch away from km3's attack to a line that attacks this turn in fewer than half of its play-outs needs a lead of 3 standard errors, not 2. `_m64`: where the best moves are within the bar the decision will use after 16 play-outs, the best, the close moves and km3's move play on to 64 on the same worlds, and the decision is made once, at the end (claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219; README rl/results/playout_close_calls_2026-10-07/README.md, the fix round). km3 is untouched. The manifest lists the seven development decks in the development run's order with its seed_base, so every deal is that run's (strength_2026-10-03_kx3_dev) and the frozen arm is that run's X arm, already played; this run plays the candidate (arm X) and km3 (arm ref) on all 7 decks: 1120 games = 560 kx3 games + 560 km3 games. Build check: every reference game here must replay the development run's game for game, or the pairing is void. PRIMARY: candidate - frozen in game score (win 1, tie 1/2, loss 0) on the same (deck, opponent, deal, seat), mean +- 1.96 sd/sqrt(n) over the 560 pairs, read by pair_combined.py in this folder; also every deck weighted equally, per group (fast 09, 06, 10; setup 03, 01, 05; draft A in the middle) and per deck, with pace (turns per game, first-attack own turn). READING, fixed now: if the pooled interval is entirely above zero, the candidate is recommended as the next frozen candidate (Dustin's word), and the held-out exam re-run decides; otherwise the frozen kx3 stays. A deck whose interval is entirely below zero is REPORTED, not a veto. Also reported, per arm: km3-attack skip turns per game (the deck's own turns where km3 proposed an attack, kx3 played something else and no attack followed that turn; trainer_habits scripted --attack-scan on the candidate arm, the existing scan for the frozen arm), the share of games with one or more, and the win rate of games with v without. Time is quoted for kx3 games only. A halfway look (the first 280 kx3 games' pairs, whatever decks they are) is shown to Dustin for information only; nothing is decided on it.

Pre-registration order: registered 2026-10-08T03:27:37Z; first game started 2026-10-08T05:54:47Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`; `selfcheck pilot=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64 games=12 seat0_wins=9 seat1_wins=3 ties=0 turns=132 digest=724e581a9c51711f`

- Planned 1120 games; finished 1120; complete pairs 560 (= 1120 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 560 paired games: +20.5 ± 3.9 points** (arm X 61.5% vs arm ref 41.0% score).
Decks weighted equally (7 decks): +20.5 ± 7.1 (sd across deck means 9.6).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 09-mega-manectric-heliolisk | 80 | 83.8% | 60.0% | +23.8 ± 10.0 | +22.0 ± 14.5 | +25.6 ± 13.9 |
| 06-mega-blaziken-tournament-list | 80 | 65.0% | 50.0% | +15.0 ± 9.3 | +18.4 ± 12.5 | +11.9 ± 13.7 |
| 10-xatu-oricorio-tr-weezing | 80 | 31.2% | 18.8% | +12.5 ± 8.8 | +15.8 ± 13.9 | +9.5 ± 11.2 |
| 03-wailord-indeedee-wall | 80 | 80.6% | 74.4% | +6.2 ± 9.9 | +10.3 ± 15.8 | +2.4 ± 12.3 |
| 01-muk-glimmora-kingambit-regigigas | 80 | 47.5% | 15.0% | +32.5 ± 10.9 | +40.0 ± 14.5 | +22.9 ± 16.2 |
| 05-indeedee-stoutland | 80 | 51.2% | 21.2% | +30.0 ± 10.7 | +31.7 ± 14.4 | +28.2 ± 16.0 |
| draft-A-shark-tempo | 80 | 71.2% | 47.5% | +23.8 ± 11.7 | +10.3 ± 17.3 | +36.6 ± 14.9 |

Overall by who went first (identical in both arms): deck first +21.7 ± 5.7 (n=281); deck second +19.4 ± 5.4 (n=279).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 01-muk-glimmora-kingambit-regigigas | t-altaria | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 01-muk-glimmora-kingambit-regigigas | t-blaziken | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 01-muk-glimmora-kingambit-regigigas | t-hydreigon | 10 | 40.0% | 30.0% | +10.0 ± 35.2 |
| 01-muk-glimmora-kingambit-regigigas | t-lucario | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 01-muk-glimmora-kingambit-regigigas | t-sceptile | 10 | 40.0% | 20.0% | +20.0 ± 26.1 |
| 01-muk-glimmora-kingambit-regigigas | t-suicune | 10 | 80.0% | 10.0% | +70.0 ± 29.9 |
| 01-muk-glimmora-kingambit-regigigas | t-vespiquen | 10 | 30.0% | 10.0% | +20.0 ± 26.1 |
| 01-muk-glimmora-kingambit-regigigas | t-weezing | 10 | 50.0% | 20.0% | +30.0 ± 29.9 |
| 03-wailord-indeedee-wall | t-altaria | 10 | 80.0% | 100.0% | -20.0 ± 26.1 |
| 03-wailord-indeedee-wall | t-blaziken | 10 | 70.0% | 70.0% | +0.0 ± 0.0 |
| 03-wailord-indeedee-wall | t-hydreigon | 10 | 80.0% | 70.0% | +10.0 ± 19.6 |
| 03-wailord-indeedee-wall | t-lucario | 10 | 80.0% | 70.0% | +10.0 ± 35.2 |
| 03-wailord-indeedee-wall | t-sceptile | 10 | 70.0% | 60.0% | +10.0 ± 35.2 |
| 03-wailord-indeedee-wall | t-suicune | 10 | 85.0% | 75.0% | +10.0 ± 32.0 |
| 03-wailord-indeedee-wall | t-vespiquen | 10 | 80.0% | 80.0% | +0.0 ± 29.2 |
| 03-wailord-indeedee-wall | t-weezing | 10 | 100.0% | 70.0% | +30.0 ± 29.9 |
| 05-indeedee-stoutland | t-altaria | 10 | 60.0% | 30.0% | +30.0 ± 29.9 |
| 05-indeedee-stoutland | t-blaziken | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 05-indeedee-stoutland | t-hydreigon | 10 | 60.0% | 30.0% | +30.0 ± 29.9 |
| 05-indeedee-stoutland | t-lucario | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 05-indeedee-stoutland | t-sceptile | 10 | 20.0% | 10.0% | +10.0 ± 19.6 |
| 05-indeedee-stoutland | t-suicune | 10 | 90.0% | 40.0% | +50.0 ± 32.7 |
| 05-indeedee-stoutland | t-vespiquen | 10 | 40.0% | 20.0% | +20.0 ± 39.2 |
| 05-indeedee-stoutland | t-weezing | 10 | 50.0% | 20.0% | +30.0 ± 29.9 |
| 06-mega-blaziken-tournament-list | t-altaria | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 06-mega-blaziken-tournament-list | t-blaziken | 10 | 80.0% | 50.0% | +30.0 ± 29.9 |
| 06-mega-blaziken-tournament-list | t-hydreigon | 10 | 70.0% | 40.0% | +30.0 ± 29.9 |
| 06-mega-blaziken-tournament-list | t-lucario | 10 | 70.0% | 70.0% | +0.0 ± 29.2 |
| 06-mega-blaziken-tournament-list | t-sceptile | 10 | 60.0% | 50.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-suicune | 10 | 60.0% | 50.0% | +10.0 ± 35.2 |
| 06-mega-blaziken-tournament-list | t-vespiquen | 10 | 90.0% | 90.0% | +0.0 ± 0.0 |
| 06-mega-blaziken-tournament-list | t-weezing | 10 | 50.0% | 40.0% | +10.0 ± 19.6 |
| 09-mega-manectric-heliolisk | t-altaria | 10 | 80.0% | 60.0% | +20.0 ± 26.1 |
| 09-mega-manectric-heliolisk | t-blaziken | 10 | 90.0% | 50.0% | +40.0 ± 32.0 |
| 09-mega-manectric-heliolisk | t-hydreigon | 10 | 90.0% | 70.0% | +20.0 ± 26.1 |
| 09-mega-manectric-heliolisk | t-lucario | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| 09-mega-manectric-heliolisk | t-sceptile | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 09-mega-manectric-heliolisk | t-suicune | 10 | 100.0% | 60.0% | +40.0 ± 32.0 |
| 09-mega-manectric-heliolisk | t-vespiquen | 10 | 100.0% | 60.0% | +40.0 ± 32.0 |
| 09-mega-manectric-heliolisk | t-weezing | 10 | 80.0% | 70.0% | +10.0 ± 35.2 |
| 10-xatu-oricorio-tr-weezing | t-altaria | 10 | 50.0% | 40.0% | +10.0 ± 19.6 |
| 10-xatu-oricorio-tr-weezing | t-blaziken | 10 | 40.0% | 30.0% | +10.0 ± 45.7 |
| 10-xatu-oricorio-tr-weezing | t-hydreigon | 10 | 30.0% | 20.0% | +10.0 ± 19.6 |
| 10-xatu-oricorio-tr-weezing | t-lucario | 10 | 50.0% | 30.0% | +20.0 ± 26.1 |
| 10-xatu-oricorio-tr-weezing | t-sceptile | 10 | 40.0% | 20.0% | +20.0 ± 26.1 |
| 10-xatu-oricorio-tr-weezing | t-suicune | 10 | 0.0% | 0.0% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-vespiquen | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 10-xatu-oricorio-tr-weezing | t-weezing | 10 | 0.0% | 0.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-altaria | 10 | 50.0% | 40.0% | +10.0 ± 35.2 |
| draft-A-shark-tempo | t-blaziken | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| draft-A-shark-tempo | t-hydreigon | 10 | 90.0% | 70.0% | +20.0 ± 26.1 |
| draft-A-shark-tempo | t-lucario | 10 | 60.0% | 40.0% | +20.0 ± 48.9 |
| draft-A-shark-tempo | t-sceptile | 10 | 50.0% | 30.0% | +20.0 ± 26.1 |
| draft-A-shark-tempo | t-suicune | 10 | 90.0% | 40.0% | +50.0 ± 43.8 |
| draft-A-shark-tempo | t-vespiquen | 10 | 90.0% | 50.0% | +40.0 ± 32.0 |
| draft-A-shark-tempo | t-weezing | 10 | 70.0% | 60.0% | +10.0 ± 19.6 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` | 560 | 769.32 / 450.38 / 2639.27 / 7327.16 s | 0.00 | 28.3 | 27206.0 / 17092.7 / 90629.8 / 410481.5 | 13 min |
| X | opponent seat | `km3` | 560 |  |  | 26.8 | 18.3 / 7.3 / 70.6 / 686.8 | 0.49 s |
| ref | deck seat | `km3` | 560 | 1.02 / 0.80 / 2.79 / 6.13 s | 0.98 | 27.4 | 17.1 / 7.0 / 66.7 / 526.9 | 0.47 s |
| ref | opponent seat | `km3` | 560 |  |  | 26.1 | 20.5 / 8.4 / 79.8 / 643.8 | 0.54 s |

One paired game (both arms) took 13 min on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 560 | 47.3 | +20.5 ± 3.9 | 344 / 0, 0.00 s | 954 / 394, 42.2 h |
| 09-mega-manectric-heliolisk | 80 | 45.7 | +23.8 ± 10.0 | 321 / 241, 10.5 h | 891 / 811, 35.4 h |
| 06-mega-blaziken-tournament-list | 80 | 42.4 | +15.0 ± 9.3 | 277 / 197, 7.9 h | 768 / 688, 27.5 h |
| 10-xatu-oricorio-tr-weezing | 80 | 40.2 | +12.5 ± 8.8 | 249 / 169, 8.2 h | 689 / 609, 29.6 h |
| 03-wailord-indeedee-wall | 80 | 45.3 | +6.2 ± 9.9 | 315 / 235, 2.9 days | 875 / 795, 9.7 days |
| 01-muk-glimmora-kingambit-regigigas | 80 | 49.7 | +32.5 ± 10.9 | 381 / 301, 41.7 h | 1057 / 977, 5.6 days |
| 05-indeedee-stoutland | 80 | 48.8 | +30.0 ± 10.7 | 366 / 286, 35.3 h | 1016 / 936, 4.8 days |
| draft-A-shark-tempo | 80 | 53.4 | +23.8 ± 11.7 | 438 / 358, 22.5 h | 1216 / 1136, 3.0 days |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 47.5% | 40.0% | +7.5 ± 11.4 |  |  |
