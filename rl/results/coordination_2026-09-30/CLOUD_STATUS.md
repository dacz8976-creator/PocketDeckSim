# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** A bounded design assessment of N1's timing (the Fable coordinator via Dustin, Sept 30): rl/results/kn_build_2026-09-30/TIMING.md. No new build, no table games; registration stays the laptop's and Dustin's.
   - The questions:
     - (1) why the tie exists: what exactly the N1 term adds and why it is equal on every chance turn;
     - (2) which of the parked text's simplifications causes it;
     - (3) at most three list-free, constant-free candidate rules that would make the play land on the turn it pays, each with its expected footprint, carrier and smoke;
     - (4) a recommendation.
   - Received with it:
     - kn (71877f6, README 52dd2ef) is accepted as a build. The smoke's timing problem (359 of 360 Goo-zooka plays before Grass Knot under km3, 120 of 677 under kn3) was also Astra's reading.
     - For the rules switch, the coordinator chose the three real alternates as carriers (e0d149a), with the made lists for the scratch rows only.
2. **What is running now, and when it ends.** Starting now: reading the score, search and clock code, and the smoke's and the diagnosis's data. A few hours at most.
3. **Files I expect to change.** rl/results/kn_build_2026-09-30/TIMING.md (new) and this file. No engine file.
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
