# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Build C2 as TIMING.md states it (the Fable coordinator via Dustin, Sept 30; Dustin approves building C2 as the next candidate, build only).
   - C2: on the km base with N1's static term off, in km's clock, both sides, a benched threat candidate adds max(0, its Active's board Retreat Cost with effects live on that turn − Energy attached to the Active) to its missing Energy. NoRetreat is left as today, and stated.
   - A preset name free of clashes, plus a one-sided diagnostic code (the opponent's clock only).
   - Tests first:
     - the unit pin against the engine's retreat arithmetic (Goo-zooka, Plaza, Trap Territory, Balloon, Boat, Bombirdier);
     - the new code with the term off equal to km3 move for move on 200 scratch deals;
     - the diagnosis's 10 judged turns (play on the 6, not on the 3).
   - Then the same scratch smoke as kn's.
   - Built on d363ba8's engine/ with this branch's players/; only players/ and tests are touched. No table games, no identity replay, no merge.
   - README with the expected footprint and carrier (Whimsicott ex Ariados; decks 14 and 15). Registration is the laptop's and Dustin's, after the rules switch pins.
   - TIMING.md (2f56033) was read and accepted; kn as built will not be registered.
2. **What is running now, and when it ends.** Starting now: the preset name and the tests, then the code, the suite and the smoke. Within the two days given.
3. **Files I expect to change.** engine/src/players/ (value_functions.rs, mod.rs, public_pricing_player.rs), possibly one new file under engine/tests/, a new folder rl/results/kr_build_2026-09-30/, and this file.
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
- 2026-09-30: carrier lists for the rules switch (Fable via Dustin; PLAN.md step 3): four development lists from the committed Limitless archive (Garchomp Meowth, Togekiss Meowth, Hisuian Goodra, Mega Houndoom ex Victini), card-checked, with provenance; rl/results/engine_switch_rules_2026-10/carriers/. No games beyond the legality scan, no engine change.
- 2026-09-30: N1 timing assessment (Fable via Dustin): rl/results/kn_build_2026-09-30/TIMING.md, why kn3 plays Goo-zooka on a tie, which simplification causes it, up to three list-free candidate rules with footprint, carrier and smoke, and a recommendation. No new build, no table games.
- 2026-09-30: build C2 (TIMING.md; Fable via Dustin): a benched threat pays its Active's missing retreat Energy in km's clock, both sides, N1 off, plus a one-sided diagnostic code; tests first (the retreat pin, 200 scratch deals with the term off = km3, the 10 judged turns), then the scratch smoke and README. players/ and tests only; no table games, no identity replay, no merge.
