# Bot-protocol adapter prototype: night run results

**Stage A / diagnostic.** Development games only (4 pairs of the panel lists in `decks/screen/opponents/`); no held-out or exam material. These numbers check the plumbing, not playing strength.

**Purpose:** one interface through which an outside planner and our own km3 can play in our engine; this run decides whether the next step can be built on it. **Owner:** the laptop session. **Cost:** at most $10 of API credits plus one laptop run (Dustin's yes, Oct 27).

**Two known limits:**
1. As a protocol bot, km3 needs `pdl_observation` and `pdl_search_seed`, so it cannot play inside upstream's engine, which sends neither.
2. Upstream's MCTS searches the full `State` (the opponent's hand and deck order); it is not a fair opponent until masked or determinized, and is not used here.

## Build job
```
2026-10-29T16:31:11Z BASE=1ff305ab9e69b965aab8c97a1dac6bac4532e01e ENGINE_TREE=c8c79c635b92c9f95c5bf1db7f77d7774f8813ca
2026-10-29T16:48:54Z job end rc=143 after 798 s (stopped: C: free 15985037312 bytes, under the 15 GiB floor)
result: none (no result event)
2026-10-29T20:24:21Z part 2 job end rc=0 after 480 s
2026-10-29T21:32:18Z fix job end rc=0 after 781 s
```

## Results
- **N3 identity (branch v BASE, km3 v km3, 200 games per build):** PASS. 200 finished.
- **N4 parity through protocol_bot (CLI, one seat and both seats, 400 games):** PASS. Seconds per decision through the pipe (decide round trip): {'n': 13993, 'median': 0.004827, 'p95': 0.031939, 'max': 0.200046}; the bot's start-up per game (spawn, hello, new_game): {'n': 599, 'median': 0.002702, 'p95': 0.00474, 'max': 0.021486}.
- **N5 dummy bots:** PASS.

| Bot | Games | Finished | Fallbacks (illegal) | Timeouts | Hangs | Ignored optional keys | Decisions per game (median) | Seconds per decision (decide round trip) | Start-up per game (seconds) |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| first_legal | 200/200 | 200 | 0 | 0 | 0 | 0 | 3.0 | median 0.000324, p95 0.000851, max 0.003222 | median 0.020394, max 0.056477 |
| seeded_random | 200/200 | 200 | 0 | 0 | 0 | 0 | 9.0 | median 0.0002, p95 0.000531, max 0.002454 | median 0.044271, max 0.073846 |
| upstream_random | 200/200 | 200 | 0 | 0 | 0 | 0 | 16.0 | median 0.000202, p95 0.000551, max 0.002682 | median 0.022157, max 0.135387 |
| plan_follower | 200/200 | 200 | 0 | 0 | 0 | 0 | 15.0 | median 0.000277, p95 0.000715, max 0.002246 | median 0.045439, max 0.102383 |
| random_v_first | 50/50 | 50 | 0 | 0 | 0 | 0 | 20.5 | median 0.000178, p95 0.00036, max 0.00185 | median 0.039759, max 0.057538 |

N4's parity tests (T4/T5, 25 seeds per pair and order): seat-games in which a protocol seat was asked no choice (every action it had was the only option): PARITY_ZERO_DECISION_SEAT_GAMES mode=one count=0 of 200; PARITY_ZERO_DECISION_SEAT_GAMES mode=both count=1 of 400.

Earlier attempts, kept beside this one and not part of these results: out.prev.20261029T204657, out.prev.20261029T213623. The first stopped in N1 (git archive in the blob:none clone); the second stopped in N4 on a per-game guard in T5 that was too strict (fixed in the fix job, coordinator-093).

Plan follower re-asks per reason: {'none': 1195, 'opponent_choice': 728, 'stale': 662, 'chance': 490, 'draw_mine': 182}; played from a saved plan 987 times (3257 decisions).

## Files
- `n2_suite_results.txt`, `n2_python.txt`: N2 (the full suite and the Python tests).
- `n3_summary.json`, `n4_summary.json`, `n5_summary.json`: every check per pair and order.
- `n4_timing.tsv`, `n5_timing.tsv`: one row per bot decision.
- `logs.tar.gz`: bot logs, plan-follower logs, and the CLI's stdout and stderr.
- `night.log`: the run's own log.
