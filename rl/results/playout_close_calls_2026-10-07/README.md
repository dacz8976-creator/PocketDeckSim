# Close calls: more play-outs where the best moves are within the noise (the cloud, Oct 7)

Set by the Fable coordinator via Dustin, Oct 7.
- **Why.** At quiz 4's Q11, kx3 had the right move among its candidates and picked an equal one at R = 16.
- **The ask.** When the best candidates are within the z bar after R rounds, continue in blocks of 16 up to R_max (a
  parameter, e.g. 64), for those candidates only, with the same common random numbers extended, and decide at the end.
  Trace the rounds used. Report the time cost on the development positions and the 8 continuation positions, and how
  many decisions change against R = 16.
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **What doesn't change.** km3, `mod.rs`, the official engine, and kx3's default play (the parameter is off unless the
  code names it).
- **No table games.**

## In short

- **Close calls are common, and the extension changes about 1 decision in 8.**
  - At the gate positions (64 decisions: the 8 continuation positions, and the 12 development positions as stored and at
    their Tool placement, 2 seeds each), 38 had a close call. 8 choices changed.
  - In 7 of the 8, R = 16 had kept km3's move: the best move's lead was within the noise (6), or km3's move was narrowly
    best (1). The extra rounds made a switch clear.
  - In the 8th, R = 16 had switched on a lead of 2.2 standard errors that shrank to +0.031 over 64 rounds, so km3's move
    is kept.
- **The time cost is 2.4x overall:** 1,271 s → 2,994 s for the 64 decisions; the median decision went from 14.5 s to
  32.2 s.
  - Most close calls stay close: 32 of the 38 ran to 64 rounds.
  - By set: the continuation positions x2.0, the development positions as stored x2.8, at the Tool placement x2.5.
- **At quiz 4's 12 positions, kx3 deciding from the game's own randomness changes 4 choices.**
  - **Q11:** now Turbo Shark, Dustin's move. Over 64 rounds it scores 0.438, against 0.391 for Misty and 0.375 for the
    retreat kx3 played.
  - **Q07:** now the retreat into Stoutland, Dustin's move again: 0.625 against 0.594 for the Psychic line.
  - **Q04:** End Turn instead of the Energy.
  - **Q10:** the retreat instead of the Bench Energy.
  - The leads at Q07 and Q11 are still small after 64 rounds, so they lean Dustin's way rather than prove him right.
- **Where the cost goes.** Most of the extra time (1,499 of 1,716 s, 87%) and 7 of the 8 changes come from close calls
  that involve km3's move. That is, whether to switch at all.
  - The third kind (the best clears the bar, but another move is within the noise of it: Q11's kind) is 5 extensions,
    217 s, and 1 change.
  - A cheaper version could stop at the first kind. Not built.
- **Gates.**
  - Gate 1 passed: suite 2,087/0, km3 unchanged, and the self-checks unchanged with the parameter off.
  - Gate 2 is the gate-position run above.

## What was built

- **The parameter.** `_m<R_max>`, e.g. `kx3_r16_c12_z2_real_t0_poolmeta_m64`. R_max must exceed R, and it can't be
  combined with a time budget. Off, nothing changes.
- **What counts as a close call.** After the R rounds, take the best candidate. Every other within z standard errors of
  it (paired, over the same rounds) is a close call.
  - A pair equal in every round so far doesn't count: more rounds wouldn't separate them.
- **What happens on a close call.** Those candidates and km3's move play 16 more rounds.
  - **The same worlds a larger R would use:** round j's world and game seed come from the decision's own randomness and
    j.
  - **Re-checked after each block:** a candidate the best now leads beyond the noise drops out, keeping its rounds. The
    extension stops when no close call is left, or at R_max.
  - **The decision** is made among the candidates still in play, by the usual rule on their rounds.
- **The trace.**
  - Each candidate reports its rounds.
  - The reason ends with "close call: play-outs extended from 16 to 64 rounds for 4 candidates".
  - The `KX_TRACE` line carries each candidate's rounds when the parameter is on.
- **Code.** `close_call` and the extension in `evaluate`, `engine/src/players/playout_player.rs` (22958cd1).
- **Tests.** Three in `engine/tests/playout_close_calls_test.rs`, written first (`tests_before.log`, eea12479), on
  test-deck decisions with R = 4 and R_max = 20 or 68 (seeds 20,000,000,240-247):
  - the code;
  - a decision without a close call is the plain decision, field for field;
  - an extended candidate's play-outs are exactly those of a plain run with as many rounds: scores, differences and
    attack counts alike, which checks that the common random numbers really extend;
  - km3's move and the best are always extended;
  - blocks of 16, and determinism.
  - Of the 8 test decisions, 6 had a close call.

## The gate positions (`gate2/`, `summary.txt`)

**How it was run.** `playout_tool_rule --extension`:
- **The positions** are gate 2's 20: the 8 continuation positions, and the 12 development positions both as stored and
  advanced to their Tool placement. That makes 32 decision points.
- **Two decision seeds each:** the position's seed and that + 10,000, inside the registered block.
- **Each decision runs twice:** kx3 with R = 16 (LAB, cap 12, z 2) and with `_m64`.
- **Times** are wall times on the cloud's 4 cores, one decision at a time, with nothing else running.

| set | decisions | close calls (extended) | choice changed | time, R = 16 | time, `_m64` | ratio |
|---|---|---|---|---|---|---|
| the 8 continuation positions | 16 | 11 | 4 | 603 s | 1,188 s | 1.97 |
| the 12 development positions, as stored | 24 | 17 | 1 | 431 s | 1,207 s | 2.80 |
| the same, at the Tool placement | 24 | 10 | 3 | 237 s | 600 s | 2.53 |
| all | 64 | 38 | 8 | 1,271 s | 2,994 s | 2.36 |

**The extension's shape.**
- **Rounds played:** 32 of the 38 close calls ran to 64 rounds, 5 stopped at 32, and 1 at 48.
- **Candidates extended:** a median of 4 (km3's move included), from 2 to 12.
- **No round failed.**

**The 8 changes** (every one with both reasons is in `summary.txt`):

| position | R = 16 | `_m64` |
|---|---|---|
| B-205731-t10 | km3's retreat kept (+0.125, 1 SE) | the turn's Water to the Active: +0.141 at 2.9 SE over 64 rounds |
| B-210952-t16 | km3's bench of the Vulpix kept (+0.094, 1.9 SE) | the Water to the Active: +0.125 at 3.0 SE |
| B-205731-t02 (both seeds) | km3's Water to Carvanha kept (+0.188, 1.4 SE) | End Turn: +0.219 at 2.5 SE (32 rounds); +0.172 at 2.8 SE (64) |
| dev06, Heavy Helmet placement | a switch to the Bench (+0.250, 2.2 SE) | km3's placement kept: the lead is +0.031 over 64 rounds |
| dev09, Heavy Helmet placement | km3's Benched Indeedee ex kept (+0.062, 1 SE) | the Benched Wailmer (Retreat Cost 3, where the Helmet works): +0.078 at 2.3 SE |
| dev10, as stored | km3's Heavy Helmet kept (+0.062, 0.6 SE) | Copycat: +0.156 at 2.1 SE |
| dev10, Heavy Helmet placement | km3's Benched Indeedee ex (it was best) | the Active Wailord (Retreat Cost 4, where the Helmet works): +0.281 at 3.0 SE (32 rounds) |

**Where the cost goes,** by what the close call was after 16 rounds:

| close call | extended | changed | extra time |
|---|---|---|---|
| the best leads km3's move, but within the noise (R = 16 keeps km3's) | 18 | 6 | 958 s |
| km3's move is the best, another within the noise of it | 15 | 1 | 541 s |
| the best clears the bar, another within the noise of it (Q11's kind) | 5 | 1 | 217 s |

## Quiz 4's positions (`quiz/`)

**How.** kx3 decided again at each of the 12 positions from the game's own observation and randomness
(`trainer_habits positions --kx3`).
- **The code** is the development run's own (`kx3_r16_c12_z2_real_t0_poolmeta`, REALISTIC, the meta pool). It replays
  every logged move, so the R = 16 column is the game itself. Then again with `_m64`.
- **Q09** comes from the exam run and the rest from the development run.

| Q | km3's move | kx3 in the game (R = 16) | kx3 with `_m64` | rounds | time, R = 16 / `_m64` |
|---|---|---|---|---|---|
| Q01 | Darkness to the Active | Darkness to Bench 3 | the same | 48 | 46 s / 97 s |
| Q02 | Lucky Ice Pop | Darkness to Bench 1 | the same | 16 | 59 s / 54 s |
| Q03 | evolve the Active | retreat | the same | 16 | 7 s / 6 s |
| Q04 | Poké Ball | Water to the Active | **End Turn** | 64 | 58 s / 179 s |
| Q05 | Pokémon Center Lady | Water to Bench 2 | the same | 16 | 6 s / 6 s |
| Q06 | Watch Over | Psychic to Bench 2 | the same | 32 | 14 s / 23 s |
| Q07 | Psychic to the Benched Stoutland | Psychic to the Active, then attack | **retreat into Stoutland** (Dustin's) | 64 | 30 s / 70 s |
| Q08 | Watch Over | retreat | the same | 64 | 19 s / 51 s |
| Q09 | Watch Over | Poké Ball | the same | 64 | 27 s / 47 s |
| Q10 | Lightning to the Active | Lightning to Bench 3 | **retreat** | 64 | 14 s / 36 s |
| Q11 | bench the Vulpix | retreat into the Vulpix | **Turbo Shark** (Dustin's) | 64 | 18 s / 55 s |
| Q12 | Supernatural Feather | End Turn | the same | 16 | 10 s / 11 s |

- **Q11:** the four moves still in play after 64 rounds are Turbo Shark 0.438, Misty 0.391, the retreat 0.375, and km3's
  bench of the Vulpix 0.172.
  - Turbo Shark leads km3's move by 4.4 SE but Misty only slightly. That fits the continuation study's verdict that
    these three are about equal.
- **Q07:** the retreat into Stoutland scores 0.625 and the Psychic line 0.594: very close.
- **Q12** isn't helped: End Turn isn't a close call there (km3's attack trails beyond the noise at R = 16). The skip bar
  is what keeps that attack.
- The quiz positions cost x2.1 in all (308 s → 634 s), about like the gate positions.

## Gate 1 (`checks/`, at 461e78ab in a separate worktree)

- **The suite:** 2,087 passed, 0 failed.
- **km3's 240 games** (seed 7100): game for game equal to the official program's, and equal to the pinned record on
  every line but the wall time.
- **The harness self-checks.**
  - km3: 81b572198c04d5d1, unchanged.
  - `kx3_r2_c3_lab`: 3a2eb43bd9053639 twice, unchanged.
  - `kx3_r2_c3_lab_m20`: d0c281641a7db61f. It's a different digest, as it should be: with R = 2 almost every decision
    is a close call, and the extension changes some choices. The same winners and turns, 2 games. It is the reference
    for a build of this version with the parameter on.

## Files

- `tests_before.log`: the tests before the code.
- `gate2/extension.jsonl` and `extension_stdout.txt`: the 64 decisions, both ways.
- `quiz/`
  - `at.json` and `at_exam.json`: the positions.
  - `index_poolmeta.json` and `index_poolmeta_m64.json`: kx3's two decisions at each, with every candidate's rounds.
- `summary.py` and `summary.txt`: the tables, the changes and every decision.
- `checks/`: gate 1.
- `engine/examples/playout_tool_rule.rs`: the `--extension` mode. `engine/examples/trainer_habits.rs`: `positions --kx3`
  keeps the decision's time and each candidate's rounds.
