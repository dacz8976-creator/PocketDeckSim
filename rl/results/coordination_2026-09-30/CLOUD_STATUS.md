# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** None. The last one is done: build switch N1 as kn<N> (the Fable coordinator via Dustin, Sept 30), rl/results/kn_build_2026-09-30/README.md.
   - **The build:** commit 71877f6, engine/src/players/ only. kn = km + N1: the opponent's Active Retreat Cost counts in the score as the bot's own does, same board cost, same weight, same place in the sum.
   - **Tests:** 11 new tests, all passing; the full suite is 2,022 passed, 0 failed. kn3 with N1 off equals km3 move for move on 200 scratch deals. Three planted faults were each caught.
   - **Smoke** (scratch decks, d363ba8's engine/ with 71877f6's players/, 4,800 games):
     - Goo-zooka goes from 0.1% of chances to 86% (plain deck), and from 18% to 88% (a Grass Knot deck).
     - Plaza stays at 96% where it helps only its own side, and falls from 100% to 29% against a Psychic deck.
     - A control deck with no N1 card: 2 of 600 games differ.
   - **One point for the registration.** kn3 plays Goo-zooka at its first chance (median turn 2), because under N1 the play ties with not playing and the move order breaks the tie.
     - In the Grass Knot deck km3's plays came before a Grass Knot in 359 of 360, kn3's in 120 of 677.
     - That deck won fewer of the same deals with kn3 (23 to 3 and 17 to 3 in two matchups). Scratch decks, not a strength result.
   - **README:** the carrier suggestion (Whimsicott ex Ariados) and the footprint expected: large on lists with Goo-zooka or Plaza, small on the 45 cells.
   - No registration text, no table games, no identity replay, no merge.
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
- 2026-09-30: build switch N1 as kn<N> (km + the opponent's Active Retreat Cost in the clock; Fable via Dustin): code, unit tests (kn3 with N1 off = km3 on 200 scratch deals), smoke on scratch decks with Goo-zooka and Peculiar Plaza, README. No registration text, no table games, no identity replay, no merge.
