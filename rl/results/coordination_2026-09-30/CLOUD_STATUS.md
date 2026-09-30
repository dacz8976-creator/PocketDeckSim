# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Sonnet's four follow-ups to the two drafts (Fable coordinator via Dustin, Sept 30). Sonnet's independent read found both drafts "ready for the laptop's switch review", no blockers. The follow-ups are tests and comments only, no rules change:
   - S1: unit-test `with_heads_coin_cuts` and harden it, so an empty call nested inside a non-empty one no longer inherits the outer cuts;
   - S2: a test pinning today's behaviour for Gyarados's Wild Swing into a coin-Ability defender (no coin);
   - S3: rerun the smoke check on e52a73b, and trace the 4 changed games without a redirected snipe (i = 16, 23, 29, 32) to their first differing decision;
   - S4: a test pinning rules/09's requirement that damage from an Ability, a Tool or the Checkup never flips the coin.
   - Limits: scratch decks and seeds outside START_HERE's ranges only; no table games, no players/, no merge. Full suite after the last engine commit; README tests table updated.
2. **What is running now, and when it ends.** Starting now: tests, one small hardening, and a scratch smoke rerun with a trace. About one to two hours. The Chase Order follow-up is done (e52a73b).
3. **Files I expect to change.**
   - engine/src/actions/attack_outcome.rs (S1: the hardening and its unit test);
   - engine/tests/pokemon/meowth_carefree_steps_test.rs (S2, S4);
   - rl/results/coin_prevention_repair_2026-09-30/ (the S3 rerun and trace, the README);
   - this file.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
