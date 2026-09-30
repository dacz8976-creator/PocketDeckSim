# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Sonnet's four follow-ups to the two drafts (Fable coordinator via Dustin, Sept 30). Sonnet's independent read found both drafts "ready for the laptop's switch review", no blockers. The follow-ups are tests and comments only, no rules change:
   - S1: unit-test `with_heads_coin_cuts` and harden it, so an empty call nested inside a non-empty one no longer inherits the outer cuts;
   - S2: a test pinning today's behaviour for Gyarados's Wild Swing into a coin-Ability defender (no coin);
   - S3: rerun the smoke check on e52a73b, and trace the 4 changed games without a redirected snipe (i = 16, 23, 29, 32) to their first differing decision;
   - S4: a test pinning rules/09's requirement that damage from an Ability, a Tool or the Checkup never flips the coin.
   - Limits: scratch decks and seeds outside START_HERE's ranges only; no table games, no players/, no merge. Full suite after the last engine commit; README tests table updated.
2. **What is running now, and when it ends.** Nothing is running. Sonnet's S1-S4 are done. The last engine commit is **c9df626**; README and files are at 3a31ce2.
   - **S1:** with_heads_coin_cuts now puts exactly its own cuts in force, so an empty call nested in a non-empty one clears the outer cuts instead of inheriting them.
     - Commits: the test first and failing (52daee6), then the hardening (c9df626).
     - No engine path nests an empty call today, so no game changes.
   - **S2:** Gyarados's Wild Swing into a Carefree Steps Meowth is pinned at today's behaviour: no coin, 0 prevented of 60, with and without the discard. The later round will change it knowingly.
   - **S3:**
     - **The rerun.** On e52a73b the smoke check gives rows identical to the committed ones (40 of 40 on each scan).
     - **The trace.** In all 4 games (i = 16, 23, 29, 32) the first differing decision is Tongue Whip's target choice: same board, same number of targets. On the repaired engine the snipe at Meowth is offered on the coin path. The old bot sniped Meowth; the repaired one sniped Chatot or Bulbasaur, a sure 30.
     - So it is the bot pricing the coin, on a choice the repair changed on the board.
     - The first smoke's counter counted only chosen redirected snipes, which is why those 4 showed 0.
   - **S4:** three tests pin that damage from an Ability (Greninja's Water Shuriken), a Tool (Rocky Helmet) or the Checkup (Poison) never flips the coin. The code already honoured it.
   - **Unit suite, on c9df626:** 2,011 passed, 0 failed, 0 ignored (2,006 plus the 5 new tests). The README's tests table is updated.
   - **Not done, as asked:** scratch decks and seeds 20,950,000,000 + i only; no table games, no players/, no merge.
3. **Files I expect to change.** None until the next job.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
