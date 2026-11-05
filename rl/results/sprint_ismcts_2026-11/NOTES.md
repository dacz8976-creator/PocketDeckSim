# ISMCTS sprint (the Opus cloud, Nov 2026): running notes

**Status: in progress.** The summary goes here when the runs are done.

## The job

From the coordinator, on Dustin's word (Nov 5): build an Information-Set MCTS pilot.
- Branch `claude/sprint-ismcts`, from K8 (b5f15351, R8 rules plus kx3; branch `laptop/kx3-on-r8-2026-11-04`).
- Measure it paired against km3, and against kx3 if it looks real. A failed swing is acceptable; a false claim is not.

## What was built (milestone 1)

**`engine/src/players/ismcts_player.rs`, code `im<sims>[_d<turns>][_p<k1|k2|w|stop>][_c<explore>][_s<scale>][_o][_trace]`:**
single-observer ISMCTS (Cowling, Powley, Whitehouse 2012).

**One iteration:**
1. **Sample a world** consistent with the pilot's observation. It uses kx's sampler: own deck order, and the opponent's hand and
   deck from a pool list consistent with the cards seen.
2. **Walk the tree** over the pilot's own actions this turn, keyed by the action sequence (one node = one information set).
   - Only the actions legal in this world are available. They are chosen by UCB with availability counts.
   - With `_o`, the opponent's decisions up to the cut-off are tree nodes too.
3. **Expand** one untried action.
4. **Play on** with a cheap policy on both sides until the cut-off, then score:
   - the policy is `_p`: km1 by default; `k2`, weighted random `w`, or `stop` for none;
   - the cut-off is `_d`: the end of the pilot's turn plus that many turns, 1 by default, i.e. the end of the opponent's next turn;
   - the score is km's evaluator (`public_clock_effect_km_value_function`), squashed as 0.5 + 0.5 tanh(v / scale), with scale
     `_s` 5000 by default; a win scores 1 and a loss 0.
5. **Back up** the score along the path.

The move played is the most visited root action. Iterations are seeded from the engine's per-decision search seed, so a decision
is reproducible.

**Not covered** (km3's move, as kx does): a single distinct move; a setup choice made after the opponent's hidden setup; an
opponent's hidden stack frame.

**Other changes (no change to any existing pilot):**
- the `IM` arm in `players/mod.rs`, under the free prefix `im`;
- `PlayoutPlayer::sample_world`, a crate-internal call into kx's existing sampler;
- `Game::state()`, a crate-internal borrow.
km3's and kx3's code paths are untouched.

**Tests** (`ismcts_player.rs`):
- the code string parses and round-trips;
- **the information boundary:** two games that differ only in hidden cards (the opponent's hand and deck, and the pilot's deck
  order) give the same observation, and with the same seed the same decision, visit for visit.

**Smoke:** `im100` v km3, deck 06 v t-altaria. About 17 s a game, against under 1 s for km3 v km3. In one game read at `-vv`, it
attacks each turn it can and wins.
