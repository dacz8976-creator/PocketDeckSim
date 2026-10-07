# Strength report: kx3_tools_gate3

Pilot **kx3_r16_c12_z2_real_t0_poolmeta_tools** against reference **km3**, stage `dev`. Manifest sha256 `23e7919db085a842` (matches the pre-registration); registered 2026-10-06T18:18:06Z.

> GATE 3 of the Tool rule (Fable via Dustin, Oct 5 and Oct 6, amended; rl/results/playout_tool_rule_2026-10-06/README.md): a first paired cut. Does kx3 with the Tool rule play development decks 01, 10, 06, 05 and 03 better or worse than kx3 without it? With `_tools` the rule works in two places: (1) in the play-outs, on both sides, a Tool is attached only where its printed effect can apply (where no placement has an effect, km3's choice stands); (2) at kx3's own decision, a within-noise tie-break: every placement stays in the pool and is played out; only when no move clears the z bar, and km3's proposed placement has no printed effect now while another placement has one, kx3 plays the placement with an effect that km3 prefers (trace: 'tie-break: Tool effect'), unless km3's placement leads it beyond the noise. km3 itself is untouched. The pilot is the development run's kx3 (REALISTIC, the pool's 8 meta lists, 16 play-outs, cap 12, z 2) plus the rule. ONLY DECKS 01, 10, 06, 05 AND 03 ARE PLAYED (--only-deck, 800 games: 400 kx3, 400 km3). The manifest lists the seven development decks in the development run's order, with its seed_base, so every deal is that run's (strength_2026-10-03_kx3_dev) and the rule-off arm is that run's X arm, already played. Build check: every reference game here (km3 v km3) must replay the development run's game for game, or the pairing is void. Primary: rule on - rule off in game score (win 1, tie 1/2, loss 0) on the same (deck, opponent, deal, seat), mean +- 1.96 sd/sqrt(n), per deck and pooled, read by pair_with_dev.py in this folder (byte copy of claude/playout-pilot 11b4836a:rl/results/playout_tool_rule_2026-10-06/gate3/pair_with_dev.py). The harness's own report (kx3 with the rule - km3) is context. Stated in advance: 80 paired games a deck is a first cut; it can show a large harm, not a small gain.

Pre-registration order: registered 2026-10-06T18:18:06Z; first game started 2026-10-06T19:33:04Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`; `selfcheck pilot=kx3_r16_c12_z2_real_t0_poolmeta_tools games=12 seat0_wins=6 seat1_wins=6 ties=0 turns=139 digest=c426e4c860e836ed`

- Planned 1120 games; finished 800; complete pairs 400 (= 800 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 400 paired games: +16.8 ± 4.3 points** (arm X 52.6% vs arm ref 35.9% score).
Decks weighted equally (5 decks): +16.8 ± 9.9 (sd across deck means 11.3).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| 06-mega-blaziken-tournament-list | 80 | 66.2% | 50.0% | +16.2 ± 8.9 | +21.1 ± 13.1 | +11.9 ± 12.0 |
| 10-xatu-oricorio-tr-weezing | 80 | 23.8% | 18.8% | +5.0 ± 7.7 | +7.9 ± 11.4 | +2.4 ± 10.5 |
| 03-wailord-indeedee-wall | 80 | 80.6% | 74.4% | +6.2 ± 8.1 | +10.3 ± 14.0 | +2.4 ± 8.3 |
| 01-muk-glimmora-kingambit-regigigas | 80 | 43.8% | 15.0% | +28.7 ± 11.1 | +40.0 ± 14.5 | +14.3 ± 16.4 |
| 05-indeedee-stoutland | 80 | 48.8% | 21.2% | +27.5 ± 10.4 | +26.8 ± 13.7 | +28.2 ± 16.0 |

Overall by who went first (identical in both arms): deck first +21.9 ± 6.2 (n=201); deck second +11.6 ± 5.8 (n=199).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| 01-muk-glimmora-kingambit-regigigas | t-altaria | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 01-muk-glimmora-kingambit-regigigas | t-blaziken | 10 | 40.0% | 10.0% | +30.0 ± 29.9 |
| 01-muk-glimmora-kingambit-regigigas | t-hydreigon | 10 | 60.0% | 30.0% | +30.0 ± 29.9 |
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
| 05-indeedee-stoutland | t-altaria | 10 | 50.0% | 30.0% | +20.0 ± 26.1 |
| 05-indeedee-stoutland | t-blaziken | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 05-indeedee-stoutland | t-hydreigon | 10 | 50.0% | 30.0% | +20.0 ± 26.1 |
| 05-indeedee-stoutland | t-lucario | 10 | 50.0% | 10.0% | +40.0 ± 32.0 |
| 05-indeedee-stoutland | t-sceptile | 10 | 30.0% | 10.0% | +20.0 ± 26.1 |
| 05-indeedee-stoutland | t-suicune | 10 | 90.0% | 40.0% | +50.0 ± 32.7 |
| 05-indeedee-stoutland | t-vespiquen | 10 | 40.0% | 20.0% | +20.0 ± 39.2 |
| 05-indeedee-stoutland | t-weezing | 10 | 30.0% | 20.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-altaria | 10 | 30.0% | 10.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-blaziken | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-hydreigon | 10 | 70.0% | 40.0% | +30.0 ± 29.9 |
| 06-mega-blaziken-tournament-list | t-lucario | 10 | 80.0% | 70.0% | +10.0 ± 35.2 |
| 06-mega-blaziken-tournament-list | t-sceptile | 10 | 70.0% | 50.0% | +20.0 ± 26.1 |
| 06-mega-blaziken-tournament-list | t-suicune | 10 | 60.0% | 50.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-vespiquen | 10 | 100.0% | 90.0% | +10.0 ± 19.6 |
| 06-mega-blaziken-tournament-list | t-weezing | 10 | 50.0% | 40.0% | +10.0 ± 19.6 |
| 10-xatu-oricorio-tr-weezing | t-altaria | 10 | 40.0% | 40.0% | +0.0 ± 29.2 |
| 10-xatu-oricorio-tr-weezing | t-blaziken | 10 | 40.0% | 30.0% | +10.0 ± 35.2 |
| 10-xatu-oricorio-tr-weezing | t-hydreigon | 10 | 30.0% | 20.0% | +10.0 ± 19.6 |
| 10-xatu-oricorio-tr-weezing | t-lucario | 10 | 30.0% | 30.0% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-sceptile | 10 | 20.0% | 20.0% | +0.0 ± 29.2 |
| 10-xatu-oricorio-tr-weezing | t-suicune | 10 | 0.0% | 0.0% | +0.0 ± 0.0 |
| 10-xatu-oricorio-tr-weezing | t-vespiquen | 10 | 30.0% | 10.0% | +20.0 ± 26.1 |
| 10-xatu-oricorio-tr-weezing | t-weezing | 10 | 0.0% | 0.0% | +0.0 ± 0.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kx3_r16_c12_z2_real_t0_poolmeta_tools` | 400 | 334.38 / 211.53 / 977.45 / 2157.87 s | 0.00 | 30.0 | 11119.8 / 8352.4 / 30416.4 / 480716.2 | 6 min |
| X | opponent seat | `km3` | 400 |  |  | 27.7 | 20.7 / 7.9 / 76.7 / 4649.0 | 0.57 s |
| ref | deck seat | `km3` | 400 | 1.14 / 0.85 / 3.10 / 5.87 s | 0.88 | 29.5 | 17.6 / 6.8 / 69.1 / 730.2 | 0.52 s |
| ref | opponent seat | `km3` | 400 |  |  | 27.3 | 22.2 / 9.0 / 84.3 / 639.1 | 0.61 s |

One paired game (both arms) took 6 min on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 400 | 43.6 | +16.8 ± 4.3 | 292 / 0, 0.00 s | 811 / 411, 19.2 h |
| 06-mega-blaziken-tournament-list | 80 | 40.4 | +16.2 ± 8.9 | 251 / 171, 2.9 h | 697 / 617, 10.6 h |
| 10-xatu-oricorio-tr-weezing | 80 | 35.2 | +5.0 ± 7.7 | 191 / 111, 2.4 h | 530 / 450, 9.6 h |
| 03-wailord-indeedee-wall | 80 | 36.8 | +6.2 ± 8.1 | 208 / 128, 12.9 h | 578 / 498, 2.1 days |
| 01-muk-glimmora-kingambit-regigigas | 80 | 50.8 | +28.7 ± 11.1 | 397 / 317, 13.8 h | 1102 / 1022, 44.5 h |
| 05-indeedee-stoutland | 80 | 47.7 | +27.5 ± 10.4 | 350 / 270, 13.4 h | 970 / 890, 44.3 h |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |
