# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Draft the Victory Star / Confusion engine repair (rules/09_engine_repairs_2026-09-22.md, "Victory Star is never offered while the attacker is Confused"; rule in rules/04 section 9). Set by the Fable coordinator via Dustin, Sept 30 ("Yes, have the cloud draft the Victory Star repair"). The order: a failing test first, committed; then the fix behind a code gate with instrumentation (RUN5's switch template); then the unit suite. Only engine/src/actions/apply_action.rs and apply_attack_action.rs, plus a new folder rl/results/victory_star_repair_2026-09-30/. No table games, no identity replay, no pinning build, no players/ change, no merge to main. The laptop replays it later, under the full procedure.
2. **What is running now, and when it ends.** Starting now: code and unit tests only, about an hour. The Altaria v Suicune diagnosis is done (6bb43cf).
3. **Files I expect to change.** engine/src/actions/apply_action.rs and engine/src/actions/apply_attack_action.rs (and their tests), plus a new folder rl/results/victory_star_repair_2026-09-30/ (README), and this file. If the fix needs more than those two engine files, or touches anything a table deck uses, I stop and write the question here.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None for this task.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
