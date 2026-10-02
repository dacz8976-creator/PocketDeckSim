# Strength report: resume_test

Pilot **kog3** against reference **km3**, stage `dev`. Manifest sha256 `b7ae49c126dababe` (matches the pre-registration); registered 2026-10-02T19:52:41Z.

> Harness smoke test: kog3 against km3 on a handful of deals. Not a measurement.

Pre-registration order: registered 2026-10-02T19:52:41Z; first game started 2026-10-02T19:52:53Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`; `selfcheck pilot=kog3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=126 digest=63f520e3318376ae`

- Planned 180 games; finished 180; complete pairs 90 (= 180 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 90 paired games: +1.1 ± 2.2 points** (arm X 57.8% vs arm ref 56.7% score).
Decks weighted equally (3 decks): +1.1 ± 2.2 (sd across deck means 1.9).

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| t-altaria | 30 | 60.0% | 56.7% | +3.3 ± 6.5 | +6.2 ± 12.2 | +0.0 ± 0.0 |
| t-hydreigon | 30 | 56.7% | 56.7% | +0.0 ± 0.0 | +0.0 ± 0.0 | +0.0 ± 0.0 |
| draft-A-shark-tempo | 30 | 56.7% | 56.7% | +0.0 ± 0.0 | +0.0 ± 0.0 | +0.0 ± 0.0 |

Overall by who went first (identical in both arms): deck first +2.2 ± 4.4 (n=45); deck second +0.0 ± 0.0 (n=45).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| draft-A-shark-tempo | t-blaziken | 10 | 100.0% | 100.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-lucario | 10 | 40.0% | 40.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-suicune | 10 | 30.0% | 30.0% | +0.0 ± 0.0 |
| t-altaria | t-blaziken | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| t-altaria | t-lucario | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| t-altaria | t-suicune | 10 | 60.0% | 50.0% | +10.0 ± 19.6 |
| t-hydreigon | t-blaziken | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| t-hydreigon | t-lucario | 10 | 40.0% | 40.0% | +0.0 ± 0.0 |
| t-hydreigon | t-suicune | 10 | 70.0% | 70.0% | +0.0 ± 0.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `kog3` | 90 | 0.36 / 0.29 / 1.07 / 1.28 s | 2.76 | 24.3 | 8.1 / 3.5 / 29.8 / 164.9 | 0.20 s |
| X | opponent seat | `km3` | 90 |  |  | 24.7 | 6.5 / 3.0 / 24.0 / 83.8 | 0.16 s |
| ref | deck seat | `km3` | 90 | 0.35 / 0.29 / 0.80 / 1.29 s | 2.86 | 24.3 | 7.8 / 3.4 / 28.7 / 151.4 | 0.19 s |
| ref | opponent seat | `km3` | 90 |  |  | 24.6 | 6.2 / 2.9 / 23.4 / 80.2 | 0.15 s |

One paired game (both arms) took 0.71 s on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 90 | 10.5 | +1.1 ± 2.2 | 18 / 0, 0.00 s | 48 / 0, 0.00 s |
| t-altaria | 30 | 18.3 | +3.3 ± 6.5 | 52 / 22, 9.50 s | 143 / 113, 49 s |
| t-hydreigon | 30 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |
| draft-A-shark-tempo | 30 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| t-altaria | Eevee is the Active Pokémon on own turn 1 (Boosted Evolution is passive: an Active Eevee may evolve at once) | 40.0% | 40.0% | +0.0 ± 0.0 |  |  |
| t-hydreigon | Hyper Ray used without a knockout (no point gained before the player's next decision) | 0.0% | 0.0% | +0.0 ± 0.0 | 0.0% of 28 uses [0.0%, 12.1%] | 0.0% of 28 uses [0.0%, 12.1%] |
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 30.0% | 30.0% | +0.0 ± 0.0 |  |  |
