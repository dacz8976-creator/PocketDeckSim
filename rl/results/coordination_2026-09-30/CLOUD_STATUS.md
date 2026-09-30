# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** The Chase Order follow-up to the coin-flip prevention repair draft (Fable coordinator via Dustin, Sept 30). Dustin's answers to my three questions:
   - (1) Chase Order: fix it now, with engine/src/actions/apply_action.rs allowed as a fourth file.
   - (2) The own-Bench form of also_choice_bench_damage: leave it open, and keep it listed in the README.
   - (3) The six sites outside the seven: keep them recorded in the README for a later round; don't change them.
   - The order for (1): failing tests first in their own commit (Chase Order without and with the discard into a coin-Ability defender, plus a control that is unchanged); then the gated fix with the same debug line and counter as (b); then the full unit suite after the last engine commit; then the README.
   - Same limits: no players/, no kd changes, no table games, no merge. This approves nothing beyond Chase Order. Release approval waits on the laptop's review (including the per-thread design) and its replay checks.
2. **What is running now, and when it ends.** Starting now: code and unit tests only, about an hour. No long runs. The coin-flip prevention draft before this is done (5942d1a; README 391a010).
3. **Files I expect to change.**
   - engine/src/actions/apply_attack_action.rs (Chase Order's helper) and engine/src/actions/apply_action.rs (its discard branch);
   - their tests, in tests/pokemon/meowth_carefree_steps_test.rs;
   - rl/results/coin_prevention_repair_2026-09-30/ (the README) and this file.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
