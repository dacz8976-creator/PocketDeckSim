# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** The Chase Order follow-up to the coin-flip prevention repair draft (Fable coordinator via Dustin, Sept 30). Dustin's answers to my three questions:
   - (1) Chase Order: fix it now, with engine/src/actions/apply_action.rs allowed as a fourth file.
   - (2) The own-Bench form of also_choice_bench_damage: leave it open, and keep it listed in the README.
   - (3) The six sites outside the seven: keep them recorded in the README for a later round; don't change them.
   - The order for (1): failing tests first in their own commit (Chase Order without and with the discard into a coin-Ability defender, plus a control that is unchanged); then the gated fix with the same debug line and counter as (b); then the full unit suite after the last engine commit; then the README.
   - Same limits: no players/, no kd changes, no table games, no merge. This approves nothing beyond Chase Order. Release approval waits on the laptop's review (including the per-thread design) and its replay checks.
2. **What is running now, and when it ends.** Nothing is running. The Chase Order follow-up is done, and the fix is commit **e52a73b**.
   - **Commits:**
     - Failing tests first, in their own commit: c350e70. Chase Order without and with the discard, each into a Carefree Steps Meowth, both failing; plus the control into Mega Latios ex, which passes before and after: same 70 and 140, same ApplyDamage.
     - The gated fix: e52a73b, in apply_attack_action.rs and apply_action.rs (one line there).
     - README: 66f9731.
   - **Unit suite, on e52a73b (the last engine commit):** 2,006 passed, 0 failed, 0 ignored (2,003 plus the 3 Chase Order tests).
   - **Which lists could change:** Vespiquen ex is in 4 lists under decks/. Its play changes only against the five coin-Ability printings, and none is in a list, so still 0 expected changed table games.
   - **Found on the way: Gyarados's Wild Swing (A4 045, in the panel ladder's l-sharpedo) skips the coin too.** It shares Chase Order's discard action. The gate keeps it exactly as before (its four tests pass), and it is recorded in the README for a later round with the six other sites.
   - **Left open, as Dustin said:** the own-Bench form of also_choice_bench_damage.
   - **Not done, as asked:** no players/, no kd changes, no table games, no merge.
   - **Audit:** no independent audit of the patch has been done yet. Release approval waits on the laptop's review (including the per-thread design) and its replay checks.
3. **Files I expect to change.** None until the next job.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
