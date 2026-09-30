# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Draft the coin-flip damage prevention repairs: rules/09_engine_repairs_2026-09-22.md lines 85-114, "Open engine bugs". Set by the Fable coordinator via Dustin, Sept 30 (approved by Dustin). It has two parts, in order.
   - **Part 1, read-only:** a check of the seven attack helpers at rules/09:104-109. For each: does it skip the defender's coin, which cards use it, and is any of them in a list under decks/. The findings are committed before any code, in rl/results/coin_prevention_repair_2026-09-30/HELPERS.md.
   - **Part 2, the repair draft:**
     - (a) partial coin cuts (Bastiodon's Guarded Grill, Hisuian Goodra's Securely Sheltered) apply after Weakness and Bounded Field;
     - (b) direct damage through a queued ApplyDamage choice triggers the coin, extended only to helpers Part 1 confirms.
     - The two pinning fixtures in hooks/core.rs are flipped and committed failing first, in their own commit; then the gated fix with instrumentation; then the full unit suite after the last commit.
   - **Limits:** no kd one-line changes and no players/ change (both listed for the laptop instead). No table games, no identity replay, no pin build, no merge to main.
2. **What is running now, and when it ends.** Starting Part 1 now: reading code only, well under an hour. Then Part 2: code and unit tests, about an hour or two. No long runs. The Victory Star draft is done and accepted (6415e39, d4fbc2a).
3. **Files I expect to change.**
   - engine/src/actions/attack_outcome.rs and engine/src/hooks/core.rs;
   - the helpers' own files, only for helpers Part 1 confirms;
   - their tests;
   - the new folder rl/results/coin_prevention_repair_2026-09-30/;
   - this file.
   - If the fix needs any other file, I stop and write the question here.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None yet.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
