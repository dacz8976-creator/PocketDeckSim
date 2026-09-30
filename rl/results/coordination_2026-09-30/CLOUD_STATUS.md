# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** A bounded diagnosis of two cards km3 almost never plays in the floor run (rl/results/floor_dustin_2026-09-30/). Set by the Fable coordinator via Dustin, Sept 30. Nothing gates on it.
   - The cards: Iris in Dustin's deck 11 (233 of 3,068 chances played, 7.6%), and Team Rocket's Goo-zooka in decks 14 and 15 (4.1% and 3.8%).
   - The questions:
     - (1) where the card was offered and not played, what km3 played instead, and what its clock or pricing said the card was worth;
     - (2) whether the score reads the card's effect at all, per the Trainer census in rl/results/trainer_audit_2026-09-25/;
     - (3) in 20 hand-picked turns, whether a competent player would have played it.
   - Limits: from the per-game files and traces, with at most 40 replayed deals per card at the official engine (rl/engine-2026-09-30/, km3). No engine change, no players/ change, no table games, no candidate proposed.
   - Output: rl/results/trainer_unplayed_diag_2026-09-30/README.md plus rows.
2. **What is running now, and when it ends.** Starting now: reading the floor pages and the census, then short replays (at most 80 deals), about one to two hours. origin/main is merged (8151f77).
3. **Files I expect to change.** Only the new folder rl/results/trainer_unplayed_diag_2026-09-30/ and this file.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
