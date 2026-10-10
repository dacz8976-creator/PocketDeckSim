# PLAN item (a)'s open test: the probe's "free" against R's gate (the cloud, Oct 10)

Rules switch 2's PLAN (`../../engine_switch_rules2_2026-10/PLAN.md`, row (a)) left one test open: coin_probe v2 should
read "free" exactly where `revert_check.tsv`'s gate_R > 0, on step 8c's 1,405 lookahead games (1,126 of them have gate_R > 0).
gate_R is the number of times R's own search (the bots' search, instrumented by Sonnet's `dg_patch.py`, "PGGATE") entered a
pure queued attack-damage frame with a coin-Ability Pokemon among its targets
(`../../engine_switch_rules_2026-10/trace_8c_sonnet/`).

## Answer

**As written, the test fails: free is true in 540 of the 1,126 games, and false in the other 586.** It never reads true
where gate_R = 0 (0 of 279). The two measure different things, so this is a mismatch of definitions, not a probe bug:

- The probe's "free" asks only about the **shortest** queued coin-path frame it finds: is that frame pure? Each branch of
  its walk also **stops at the first queued frame** it meets, so a pure frame that comes after a mixed one is never seen.
  It looks only at the mover's own frames, and only at the opponent's coin Pokemon.
- R's gate counts **any** pure queued frame anywhere in the bots' search: after a mixed queued choice too, from either
  player's frame, with a coin Pokemon of either side among the targets.

Checking that this is the whole difference took a scratch copy of the probe with two print lines and one switch:

- Lines printed: every ply where it found a pure queued frame (`PURE_PLIES`), and every ply where it found R's gate frame,
  defined as `dg_patch.py` defines it (`GATE_PLIES`).
- `GATE_WALK`: when set, a branch goes on past a queued frame instead of stopping. Pure frames cost no ply, mixed ones cost
  one, as before.

`coin_probe_v2_open_test.diff` has the change, against the Oct 2 probe (57c6586, the version `v2_summary.txt` ran).

| Run (all 1,405 games, official engine main-8626a35, engine tree 38af8b0) | gate_R > 0 (1,126) | gate_R = 0 (279) |
|---|---|---|
| 1. `free = true` (PLAN's test as written) | 540 | 0 |
| 2. a pure queued frame at any ply, the probe's normal walk | 543 | 0 |
| 3. **R's gate frame found, walking past queued frames** | **1,126** | **0** |

**With the walk continuing and the gate defined as R's instrumentation defines it, the probe matches gate_R exactly: 1,126
of 1,126, and none of the 279.** The first gate frame is at ply 1 in 98 games, ply 2 in 671 and ply 3 in 357. None is
deeper than the search's 3 plies.

Other checks:

- **The walk switch doesn't change what the probe reports.** Its `queued` and `free` results are the same with and
  without it in all 1,405 games.
- **Nothing drifted since Oct 2.** Every game the Oct 2 run probed (1,398) gets today the same `queued` and `free` it got
  then (`v2_verdicts.tsv`). The other 7 read "on the board" on Oct 2 and weren't probed.
- **The node limit, as before.** Two games stopped at 60,000 nodes having found nothing: pairing 12, game 69, both bots,
  the same two as Oct 2. Run again at 600,000, both found the gate at ply 3.
- **Three walks stopped at the limit after finding something.** Their gate result comes from part of the tree:
  - k3 12/96 and k3 12/177 have gate_R = 0 and found no gate frame. That agrees with R, but the walk didn't cover the
    whole tree.
  - km3 12/148 has gate_R = 4 and found the gate at ply 3.

## What this means for PLAN item (a)

PLAN's sentence "free exactly where gate_R > 0" doesn't hold as worded. The probe's `free` reads the shortest path only.
What R's gate counts is "the search reaches a pure coin-target frame somewhere". That **matches exactly** once the probe
walks past queued frames and uses R's own definition of the frame.

Whether the official `coin_probe_v2.rs` should gain this as a third reading, or PLAN's sentence should be reworded, is a
call for the coordinator. **Nothing in the official probe or the engine changed.** The scratch copy was built in a
throwaway copy of the official engine, as the probe always is.

## Files

- `coin_probe_v2_open_test.rs`: the scratch probe, sha256 `042e37f5...`. Built as the probe is:
  `cp coin_probe_v2_open_test.rs engine/examples/coin_probe_v2.rs && (cd engine && cargo build --release --locked
  --features test-utils --example coin_probe_v2)`, in a copy of main-8626a35's engine.
- `coin_probe_v2_open_test.diff`: its difference from the Oct 2 probe (57c6586, sha256 `6605f7f6...`).
- `run_open_test.py`: runs it over the rows of `revert_check.tsv`, with seed base 23,100,000,000 as in step 8c. A probe
  that stops at the limit having found nothing is run again at 600,000 nodes. Set `WALK=1` to turn on `GATE_WALK`.
- `open_test_default.tsv` (normal walk) and `open_test_walk.tsv` (`WALK=1`): one row per game.
- `summarize.py` and its output, `summary.txt`.
