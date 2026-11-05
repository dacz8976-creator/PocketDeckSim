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

## Milestone 2: identity, and the first tuning (Nov 5)

**km3 and kx3 play the same games on this branch as on K8:**
- **km3:** 30 games are identical in outcome, plies, final turn, points and action counts. Deck 05 v t-altaria, t-suicune and
  t-lucario, 10 games each, seeds 20,100,900,000 and up.
- **kx3:** 2 games are identical. Deck 06 v t-altaria, seeds 20,100,910,000 and up. They took 6-7 minutes a game on this
  4-core machine, under load.

**Tuning subset:**
- **The decks:** development decks 06 and 10 (fast) and 01-kingambit-as-played (setup), against t-altaria, t-suicune, t-lucario
  and t-blaziken.
- **The games:** 4 games per pairing, 48 paired games per setting, seeds 20,101,000,000 + 1000 k.
- **The reference:** km3 v km3 wins 22.9% of these 48 (11 of 48): hard matchups, so there is little room to show a gain.
- **The rows:** the difference is the candidate's win share minus km3's on the same seeds, in points, ±1.96 SE.
- **The time** is per setting for 48 games, on 2 threads while kx3 ran.
- **This is a screen for broken settings, not a measurement:** each row has an interval of about ±12 points.

| Setting | Wins | Difference | Fast 06+10 | Setup 01 | Time |
|---|---:|---:|---:|---:|---:|
| im100 (d1, km1 play-outs, c0.4, s5000) | 9 of 48 | −4.2 ± 13.0 | −6.2 | +0.0 | 310 s |
| im100_d0 (stop at the end of my turn) | 4 | −14.6 ± 11.7 | −15.6 | −12.5 | 58 s |
| im100_pw (weighted-random play-outs) | 6 | −10.4 ± 12.0 | −12.5 | −6.2 | 68 s |
| im100_pstop (no play-out) | 5 | −12.5 ± 11.1 | −9.4 | −18.8 | 17 s |
| im100_c0.1 | 7 | −8.3 ± 12.8 | −9.4 | −6.2 | 349 s |
| im100_s1500 | 5 | −12.5 ± 11.1 | −12.5 | −12.5 | 298 s |
| im100_c0.1_s1500 | 8 | −6.2 ± 13.6 | +0.0 | −18.8 | 289 s |
| im300_c0.1_s1500 | 6 | −10.4 ± 15.7 | −6.2 | −18.8 | 846 s |

**What this says so far:**
- No setting beats km3.
- Seeing the opponent's reply matters: the cut-off at the end of my own turn (`d0`) and no play-out (`pstop`) are the worst.
- **More iterations don't help** (300 is no better than 100). So the limit looks like the signal at the leaves, a km1 play-out
  scored by km's evaluator, not the tree budget. km3's 3-action exact search with the same evaluator is already better informed
  per decision than 100-300 noisy one-world samples.

**Next:**
- the km3 anchor (`_k<margin>`): play km3's move unless the tree's mean for another move beats it by the margin;
- km2 play-outs.
