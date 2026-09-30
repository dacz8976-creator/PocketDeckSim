# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Draft the coin-flip damage prevention repairs: rules/09_engine_repairs_2026-09-22.md lines 85-114, "Open engine bugs". Set by the Fable coordinator via Dustin, Sept 30 (approved by Dustin). It has two parts, in order.
   - **Part 1, read-only:** a check of the seven attack helpers at rules/09:104-109. For each: does it skip the defender's coin, which cards use it, and is any of them in a list under decks/. The findings are committed before any code, in rl/results/coin_prevention_repair_2026-09-30/HELPERS.md.
   - **Part 2, the repair draft:**
     - (a) partial coin cuts (Bastiodon's Guarded Grill, Hisuian Goodra's Securely Sheltered) apply after Weakness and Bounded Field;
     - (b) direct damage through a queued ApplyDamage choice triggers the coin, extended only to helpers Part 1 confirms.
     - The two pinning fixtures in hooks/core.rs are flipped and committed failing first, in their own commit; then the gated fix with instrumentation; then the full unit suite after the last commit.
   - **Limits:** no kd one-line changes and no players/ change (both listed for the laptop instead). No table games, no identity replay, no pin build, no merge to main.
2. **What is running now, and when it ends.** Nothing is running. The coin-flip prevention repair draft is done, and the fix is commit **5942d1a**. Folder: rl/results/coin_prevention_repair_2026-09-30/.
   - **Commits:**
     - Part 1 (HELPERS.md): 7fa2f85.
     - The two hooks/core.rs fixtures flipped and failing, in their own commit: 0785365.
     - More failing tests: d21511a.
     - The fix: 5942d1a.
     - README, suite log and smoke check: 391a010.
   - **Unit suite, on 5942d1a's engine:** 2,003 passed, 0 failed (1,994 plus 9 new tests). The last engine commit is 5942d1a; the later commits touch only rl/results/.
   - **Which games could change:** none between two lists under decks/. Both repairs need a coin-Ability Pokemon in play (Bastiodon A2 114, Togekiss A4 080, Meowth B2 124 or B2 204, Hisuian Goodra B3b 050), and no list has one.
     - Heatmor (in t-blaziken and Dustin's 06) and six other attackers in lists are changed. Their play changes only against one of those five.
     - The README lists them, with the replay for the laptop: expected 0 changed table games.
   - **Not done, as asked:**
     - No kd one-line changes and nothing in players/. The README gives both kd changes for the laptop.
     - No table games, identity replay, pin build or merge to main.
   - **Files.** The fix used only the three permitted files (attack_outcome.rs, hooks/core.rs, apply_attack_action.rs), plus two test files.
     - For (a) it uses a scoped per-thread value to carry the heads cut into modify_damage. The alternatives each needed a file outside the three; the README's design note says so.
   - **Games.** Besides the tests, I played a smoke check on two scratch decks: 120 games (40 on each of three scans), seeds 20,950,000,000 + i, no table deck. There was also a Part 1 probe on seeds 20,940,000,000 + i.
3. **Files I expect to change.** None until the next job.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin** (from Part 1; not changed in this draft):
   - **Chase Order (Vespiquen ex, in 4 lists under decks/).** It skips the coin both with and without the discard. The discard choice's damage is queued in engine/src/actions/apply_action.rs, outside the three files allowed, so I have not changed it. Should Part 2 cover it, adding apply_action.rs?
   - **The own-Bench form of also_choice_bench_damage (Zapdos's Raging Thunder, Emolga, Luxray's Flash Impact; in no list).** Its hit on the opponent's Active skips the coin. Its one queued choice also damages your own Benched Pokemon, and the coin-flipping path would drop a Guts coin there, so I have not changed it. Leave it, or fix it with a split choice?
   - **Six more sites outside the seven, all confirmed to skip the coin (none in a list):** Wellspring Mask Ogerpon, Rapid Strike Urshifu, Blastoise and Mega Blastoise ex, Mega Kangaskhan ex's second punch, Hoopa's Mischievous Ring, and Slowking's Litter (whose damage is queued in apply_action.rs). Not changed. Should a later round cover them?

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
