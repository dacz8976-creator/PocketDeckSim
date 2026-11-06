# ISMCTS sprint (the Opus cloud, Nov 2026): running notes

## Final result (wrap-up, Nov 6): a failed swing

- **The best setting** was `im100`: 100 iterations, km1 play-outs through the opponent's next turn, scored by km's evaluator.
- **Read against km3, paired game by game on the same seeds:**
  - **development decks:** 24.0% wins v km3's 30.7%, −6.8 ± 8.1 points over 192 games;
  - **check decks, new seeds:** 18.8% v 39.5%, −20.7 ± 6.5 points over 256 games. Every check deck is below km3.
- **It lost to km3, and it is far slower:** about 15 s of CPU a game against km3's 0.3 s.
- **What I'd do next:** stop this track as built. If anyone reopens it, the one idea worth a small test is to start the tree from
  km3's own move ordering (a prior), instead of from an even spread over the moves. Otherwise kx3 remains the better use of
  search time.

## Summary (Nov 6): ISMCTS lost to km3

**It does not beat km3.** It is clearly worse on the check decks, and it was not run against kx3.

**What was built:** single-observer ISMCTS (`im<sims>...`, `engine/src/players/ismcts_player.rs`).
- It plans only on worlds sampled from its own observation, with kx's sampler.
- The tree covers its own actions for the turn, with km1 play-outs through the opponent's next turn, scored by km's evaluator.
- A test shows the same observation and seed give the same decision in two different hidden worlds.
- km3 and kx3 play identical games on this branch (km3 30 of 30, kx3 2 of 2, against K8 b5f15351).

**The numbers.** All runs are paired game by game against km3 v km3 on the same seeds; the difference is in win-share points,
±1.96 SE.

| Set | Setting | Games | ISMCTS wins | km3 wins | Difference |
|---|---|---:|---:|---:|---:|
| Development: decks 01-as-played, 05, 06, 09, 10, 11 v the 8 opponents, 4 games each, seeds 20,102,000,000 + 1000 k | im100 | 192 | 24.0% | 30.7% | −6.8 ± 8.1 |
| the same | im60_pk2 (km2 play-outs) | 192 | 16.9% | 30.7% | **−13.8 ± 7.1** |
| Check: decks 02, 04, 07, 08, 12, 13-a, 14, 15 v the 8 opponents, 4 games each, new seeds 20,103,000,000 + 1000 k | im100 | 256 | 18.8% | 39.5% | **−20.7 ± 6.5** |

- **By group, development, im100:**
  - fast (06, 09, 10): −13.5 ± 11.8 (31.2% v 44.8%, 96 games);
  - setup (01, 05, 11): +0.0 ± 10.9 (16.7% v 16.7%, 96 games).
  - Deck 01-kingambit-as-played came out +21.9 ± 19.1 (32 games). That is one deck where km3 itself wins 6%, and it didn't hold
    on the other setup decks.
- **Check set:** every one of the 8 decks is below km3, from −6.2 (deck 15) to −37.5 (deck 07, Skarmory stall).
- **Time:** im100 takes about 13-17 s of CPU per game on this 4-core cloud machine, against about 0.3 s for km3 v km3. kx3 takes
  6-7 minutes a game here.

**What failed:**
1. **No setting beat km3 in tuning.** Thirteen settings, 48 paired games each on decks 06, 10 and 01 v 4 opponents (tables
   below): more iterations (300), the exploration constant and squash, a km3 anchor, km2 and km3 play-outs, full-game play-outs,
   and full-turn expansion.
2. **It passes up attacks.** In a lost game read at `-vv` (deck 09 v t-suicune, seed 20,104,000,004):
   - on one turn it evolved a second Mega Manectric ex and attached its second Lightning Energy, then ended the turn without using
     Lightning Accelerator, which those Energy pay for;
   - two later turns also ended with no attack.
   It attacks on most turns (3-6 attacking turns a game in the six games read), but it gives away tempo km3 keeps. That fits the
   fast decks losing most.
3. **The likely reason:**
   - **The tree is shallow.** A turn has 5-8 decisions. With 100-300 iterations, the tree rarely gets past the first action or
     two. Each root move is effectively judged as "this move, then km1 to the end of the opponent's reply", scored by km's
     evaluator, over sampled worlds.
   - **The signal is noisier than km3's.** km3 searches 3 actions exactly with the same evaluator, so its signal per decision is
     cleaner than 100 noisy one-world samples.
   - **kx3 is the contrast.** It keeps km3's move unless full-game km3 play-outs disagree beyond the noise. It plays out to the
     end of the game with km3, which this pilot can't afford here.

**ISMCTS against kx3:** not run. ISMCTS is below km3, and kx3 beat km3 53.0% v 31.7% on the 11 held-out decks (the coordinator's
figure, a different set), so the order is kx3 > km3 > ISMCTS as built.

**For the laptop, only if someone wants a second look:** the gap on the check set is 20 points with a ±6.5 interval, so more games
won't change the answer. The cheapest further idea is in "Ideas not tried" below. A larger development run would be:

```
rl/results/sprint_ismcts_2026-11/run_pairs.sh <deckgym> <out> im100 16 <seed> <threads> decks/dustin/01-kingambit-as-played.txt decks/dustin/05-indeedee-stoutland.txt decks/dustin/06-mega-blaziken-tournament-list.txt decks/dustin/09-mega-manectric-heliolisk.txt decks/dustin/10-xatu-oricorio-tr-weezing.txt decks/dustin/11-archaludon-haxorus-dragonair.txt -- decks/screen/opponents/*.txt
python3 rl/results/sprint_ismcts_2026-11/read_pairs.py <out> im100
```

**Ideas not tried:**
- **Use km3 as the in-tree prior** (progressive bias toward km3's ordering of the moves), so the tree starts from km3's plan
  instead of uniform. That is closer to how AlphaZero-style search stays at least as good as its prior.
- **Pick the move on lower-bound value,** not visits.
- **Spend the budget on fewer, deeper iterations:** km3 play-outs only on the most visited branches.

**Tests:** `cargo test --features test-utils --lib -- ismcts playout_player`, 7 of 7 pass. These are the ISMCTS parse test, the
information-boundary test and kx's five sampler tests. The engine's full suite was not run on this branch.

---


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

## Milestone 3: more tuning (Nov 5-6)

The same 48 paired games as above. Times are for 48 games; these ran on 4 threads.

| Setting | Wins | Difference | Fast 06+10 | Setup 01 | Time |
|---|---:|---:|---:|---:|---:|
| im100_k0.05 (km3 anchor, margin 0.05) | 8 of 48 | −6.2 ± 12.2 | −6.2 | −6.2 | 198 s |
| im100_k0.1 (km3 anchor, margin 0.1) | 9 | −4.2 ± 11.6 | −6.2 | +0.0 | 193 s |
| im60_pk2 (km2 play-outs) | 10 | −2.1 ± 14.9 | +3.1 | −12.5 | 588 s |
| im100_d30 (km1 play-outs to the end of the game) | 4 | −14.6 ± 14.3 | −12.5 | −18.8 | 882 s |
| im40_pk3 (km3 play-outs) | 8 | −6.2 ± 13.6 | −15.6 | +12.5 | 1568 s |
| im100_f (full-turn expansion) | 6 | −10.4 ± 13.4 | −9.4 | −12.5 | 168 s |
| im200_f | 7 | −8.3 ± 14.1 | −9.4 | −6.2 | 309 s |

**What this says:**
- **Still no setting beats km3 on these games.** The best are km2 play-outs (−2.1) and the default (−4.2), both inside the noise.
- **The km3 anchor didn't help.** Even keeping km3's move unless the tree's mean beats it by 0.1 loses a little. So the tree's
  means for the alternatives are noisy enough to switch on noise, on the decisions where they do switch.
- **Full-turn expansion is no better than stopping at the first new node.** With 100-200 iterations, a whole-turn tree is too wide
  for the iterations to concentrate on good sequences.
- **Stronger play-outs cost a lot and gained nothing clear here:** km3 play-outs took about 2 minutes a game on 4 threads.
- **Next:** the full development set (6 decks x 8 opponents, 4 games each, 192 paired games) for `im100` and `im60_pk2`.

## Milestone 4: the development and check sets (Nov 6)

**Development set,** `im100`: 192 paired games, 832 s on 4 threads.

| Rows | Games | im100 wins % | km3 wins % | Difference |
|---|---:|---:|---:|---:|
| all | 192 | 24.0 | 30.7 | −6.8 ± 8.1 |
| fast group (06, 09, 10) | 96 | 31.2 | 44.8 | −13.5 ± 11.8 |
| setup group (01, 05, 11) | 96 | 16.7 | 16.7 | +0.0 ± 10.9 |
| deck 01-kingambit-as-played | 32 | 28.1 | 6.2 | +21.9 ± 19.1 |
| deck 05-indeedee-stoutland | 32 | 6.2 | 28.1 | −21.9 ± 17.0 |
| deck 06-mega-blaziken-tournament-list | 32 | 40.6 | 53.1 | −12.5 ± 26.0 |
| deck 09-mega-manectric-heliolisk | 32 | 40.6 | 59.4 | −18.8 ± 20.5 |
| deck 10-xatu-oricorio-tr-weezing | 32 | 12.5 | 21.9 | −9.4 ± 13.5 |
| deck 11-archaludon-haxorus-dragonair | 32 | 15.6 | 15.6 | +0.0 ± 17.6 |

**Development set,** `im60_pk2`: 192 paired games, 2231 s on 4 threads. All −13.8 ± 7.1; fast −23.4 ± 10.7; setup −4.2 ± 9.1.

**Check set,** `im100`, new seeds: 256 paired games, 1218 s on 3 threads.

| Rows | Games | im100 wins % | km3 wins % | Difference |
|---|---:|---:|---:|---:|
| all | 256 | 18.8 | 39.5 | −20.7 ± 6.5 |
| deck 02-arceus-crobat | 32 | 6.2 | 37.5 | −31.2 ± 16.3 |
| deck 04-absol-hoopa-darkrai | 32 | 12.5 | 28.1 | −15.6 ± 15.5 |
| deck 07-skarmory-stall | 32 | 28.1 | 65.6 | −37.5 ± 17.0 |
| deck 08-garchomp-toolbox | 32 | 12.5 | 28.1 | −15.6 ± 19.9 |
| deck 12-ariados-whimsicott-ogerpon | 32 | 15.6 | 34.4 | −18.8 ± 18.5 |
| deck 13-a-ninetales-raticate | 32 | 40.6 | 62.5 | −21.9 ± 22.8 |
| deck 14-comfey-raticate-hypno | 32 | 9.4 | 28.1 | −18.8 ± 16.3 |
| deck 15-jolteon-oricorio-raticate | 32 | 25.0 | 31.2 | −6.2 ± 19.6 |

**Ties** count a half: some cells end in .x because of them.

**Reading games at `-vv`:** six games of deck 09 v t-suicune, im100 v km3, seeds 20,104,000,001-006. The pilot attacked on 3-6
of its turns per game and won 3 of 6. In seed 004 (lost) it ended three turns without an attack, one of them with an attack paid
for (see the summary).
