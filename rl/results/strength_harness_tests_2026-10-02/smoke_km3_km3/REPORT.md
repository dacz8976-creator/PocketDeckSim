# Strength report: smoke_km3_km3

Pilot **km3** against reference **km3**, stage `dev`. Manifest sha256 `64e02a848bbe6a06` (matches the pre-registration); registered 2026-10-02T19:51:04Z.

> Harness smoke test: km3 against km3 (must give exactly zero) on a handful of deals. Not a measurement.

Pre-registration order: registered 2026-10-02T19:51:04Z; first game started 2026-10-02T19:51:10Z (after registration).

Self-check digests recorded at registration: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`

- Planned 180 games; finished 180; complete pairs 90 (= 180 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 90 paired games: +0.0 ± 0.0 points** (arm X 56.7% vs arm ref 56.7% score).
Decks weighted equally (3 decks): +0.0 ± 0.0 (sd across deck means 0.0).

**Every paired difference is exactly 0** (90 of 90 paired games identical in winner, points and turns): the two arms played the same games.

### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| t-altaria | 30 | 56.7% | 56.7% | +0.0 ± 0.0 | +0.0 ± 0.0 | +0.0 ± 0.0 |
| t-hydreigon | 30 | 56.7% | 56.7% | +0.0 ± 0.0 | +0.0 ± 0.0 | +0.0 ± 0.0 |
| draft-A-shark-tempo | 30 | 56.7% | 56.7% | +0.0 ± 0.0 | +0.0 ± 0.0 | +0.0 ± 0.0 |

Overall by who went first (identical in both arms): deck first +0.0 ± 0.0 (n=45); deck second +0.0 ± 0.0 (n=45).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| draft-A-shark-tempo | t-blaziken | 10 | 100.0% | 100.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-lucario | 10 | 40.0% | 40.0% | +0.0 ± 0.0 |
| draft-A-shark-tempo | t-suicune | 10 | 30.0% | 30.0% | +0.0 ± 0.0 |
| t-altaria | t-blaziken | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| t-altaria | t-lucario | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| t-altaria | t-suicune | 10 | 50.0% | 50.0% | +0.0 ± 0.0 |
| t-hydreigon | t-blaziken | 10 | 60.0% | 60.0% | +0.0 ± 0.0 |
| t-hydreigon | t-lucario | 10 | 40.0% | 40.0% | +0.0 ± 0.0 |
| t-hydreigon | t-suicune | 10 | 70.0% | 70.0% | +0.0 ± 0.0 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `km3` | 90 | 0.35 / 0.28 / 0.77 / 1.30 s | 2.86 | 24.3 | 7.9 / 3.5 / 28.2 / 153.6 | 0.19 s |
| X | opponent seat | `km3` | 90 |  |  | 24.6 | 6.2 / 3.0 / 23.3 / 84.4 | 0.15 s |
| ref | deck seat | `km3` | 90 | 0.35 / 0.29 / 0.80 / 1.33 s | 2.86 | 24.3 | 7.8 / 3.5 / 27.6 / 165.6 | 0.19 s |
| ref | opponent seat | `km3` | 90 |  |  | 24.6 | 6.2 / 3.0 / 22.7 / 85.2 | 0.15 s |

One paired game (both arms) took 0.70 s on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 90 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |
| t-altaria | 30 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |
| t-hydreigon | 30 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |
| draft-A-shark-tempo | 30 | 0.0 | +0.0 ± 0.0 | n/a (sd 0) | n/a (sd 0) |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| t-altaria | Eevee is the Active Pokémon on own turn 1 (Boosted Evolution is passive: an Active Eevee may evolve at once) | 40.0% | 40.0% | +0.0 ± 0.0 |  |  |
| t-hydreigon | Hyper Ray used without a knockout (no point gained before the player's next decision) | 0.0% | 0.0% | +0.0 ± 0.0 | 0.0% of 28 uses [0.0%, 12.1%] | 0.0% of 28 uses [0.0%, 12.1%] |
| draft-A-shark-tempo | Turbo Shark used (arming a Benched Pokémon) by own turn 3 | 30.0% | 30.0% | +0.0 ± 0.0 |  |  |
