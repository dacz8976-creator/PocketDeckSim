# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Draft the coin-flip damage prevention repairs: rules/09_engine_repairs_2026-09-22.md lines 85-114, "Open engine bugs". Set by the Fable coordinator via Dustin, Sept 30 (approved by Dustin). It has two parts, in order.
   - **Part 1, read-only:** a check of the seven attack helpers at rules/09:104-109. For each: does it skip the defender's coin, which cards use it, and is any of them in a list under decks/. The findings are committed before any code, in rl/results/coin_prevention_repair_2026-09-30/HELPERS.md.
   - **Part 2, the repair draft:**
     - (a) partial coin cuts (Bastiodon's Guarded Grill, Hisuian Goodra's Securely Sheltered) apply after Weakness and Bounded Field;
     - (b) direct damage through a queued ApplyDamage choice triggers the coin, extended only to helpers Part 1 confirms.
     - The two pinning fixtures in hooks/core.rs are flipped and committed failing first, in their own commit; then the gated fix with instrumentation; then the full unit suite after the last commit.
   - **Limits:** no kd one-line changes and no players/ change (both listed for the laptop instead). No table games, no identity replay, no pin build, no merge to main.
2. **What is running now, and when it ends.** Part 1 is done and committed: 7fa2f85, rl/results/coin_prevention_repair_2026-09-30/HELPERS.md. Working on Part 2 now: code and unit tests, about one to two hours. No long runs.
3. **Files I expect to change.**
   - engine/src/actions/attack_outcome.rs and engine/src/hooks/core.rs;
   - the helpers' own files, only for helpers Part 1 confirms;
   - their tests;
   - the new folder rl/results/coin_prevention_repair_2026-09-30/;
   - this file.
   - If the fix needs any other file, I stop and write the question here.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin** (from Part 1; I am going on with the rest of Part 2 meanwhile):
   - **Chase Order (Vespiquen ex, in 4 lists under decks/).** It skips the coin both with and without the discard. The discard choice's damage is queued in engine/src/actions/apply_action.rs, outside the three files allowed, so I have not changed it. Should Part 2 cover it, adding apply_action.rs?
   - **The own-Bench form of also_choice_bench_damage (Zapdos's Raging Thunder, Emolga, Luxray's Flash Impact; in no list).** Its hit on the opponent's Active skips the coin. Its one queued choice also damages your own Benched Pokemon, and the coin-flipping path would drop a Guts coin there, so I have not changed it. Leave it, or fix it with a split choice?
   - **Six more sites outside the seven, all confirmed to skip the coin (none in a list):** Wellspring Mask Ogerpon, Rapid Strike Urshifu, Blastoise and Mega Blastoise ex, Mega Kangaskhan ex's second punch, Hoopa's Mischievous Ring, and Slowking's Litter (whose damage is queued in apply_action.rs). Not changed. Should a later round cover them?

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
