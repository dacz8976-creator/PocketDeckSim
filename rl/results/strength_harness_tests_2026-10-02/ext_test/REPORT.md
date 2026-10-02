# Strength report: ext_test

Pilot **ext:python3 rl/strength/ext_pilot_example.py attack** against reference **km3**, stage `dev`. Manifest sha256 `3ebcee893d5a4793` (matches the pre-registration); registered 2026-10-02T19:53:26Z.

> Protocol test: the example external pilot (prefers an attack) against km3.

Pre-registration order: registered 2026-10-02T19:53:26Z; first game started 2026-10-02T19:53:26Z (after registration).

- Planned 12 games; finished 12; complete pairs 6 (= 12 games); unpaired games 0; errors 0.
- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.

## Result

**Pooled over all 6 paired games: -66.7 ± 41.3 points** (arm X 0.0% vs arm ref 66.7% score).


### Per deck, pooled over its opponents

| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |
|---|---|---|---|---|---|---|
| t-altaria | 6 | 0.0% | 66.7% | -66.7 ± 41.3 | -66.7 ± 65.3 | -66.7 ± 65.3 |

Overall by who went first (identical in both arms): deck first -66.7 ± 65.3 (n=3); deck second -66.7 ± 65.3 (n=3).

### Per (deck, opponent) pair

| deck | opponent | n | arm X | arm ref | paired difference (points) |
|---|---|---|---|---|---|
| t-altaria | t-blaziken | 6 | 0.0% | 66.7% | -66.7 ± 41.3 |

## Runtime and cost

Wall time is per game on this machine with the threads the run used; it includes both seats' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).

| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |
|---|---|---|---|---|---|---|---|---|
| X | deck seat | `ext:python3 rl/strength/ext_pilot_example.py attack` | 6 | 0.19 / 0.15 / 0.51 / 0.51 s | 5.40 | 14.8 | 2.1 / 0.7 / 19.3 / 21.5 | 0.03 s |
| X | opponent seat | `km3` | 6 |  |  | 21.2 | 7.0 / 3.2 / 24.4 / 97.7 | 0.15 s |
| ref | deck seat | `km3` | 6 | 0.30 / 0.31 / 0.42 / 0.42 s | 3.31 | 23.8 | 8.2 / 3.5 / 30.1 / 71.6 | 0.20 s |
| ref | opponent seat | `km3` | 6 |  |  | 21.0 | 4.8 / 2.3 / 17.1 / 47.5 | 0.10 s |

One paired game (both arms) took 0.49 s on average; the run used 2 thread(s).

## What more precision would take

At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.

| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |
|---|---|---|---|---|---|
| all decks pooled | 6 | 51.6 | -66.7 ± 41.3 | 410 / 404, 2 min | 1139 / 1133, 5 min |
| t-altaria | 6 | 51.6 | -66.7 ± 41.3 | 410 / 404, 2 min | 1139 / 1133, 5 min |

## Intended lines

From `rl/strength/intended_lines.json`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).

| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |
|---|---|---|---|---|---|---|
| t-altaria | Eevee is the Active Pokémon on own turn 1 (Boosted Evolution is passive: an Active Eevee may evolve at once) | 66.7% | 66.7% | +0.0 ± 0.0 |  |  |
