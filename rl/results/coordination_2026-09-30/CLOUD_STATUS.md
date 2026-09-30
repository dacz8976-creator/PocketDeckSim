# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Build switch N1, as parked in rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md ("Appendix. Parked: N1"). Set by the Fable coordinator via Dustin, Sept 30, approved by Dustin for the next two days.
   - N1: the opponent's Active Retreat Cost counted in the clock, on the km base, as a new preset kn<N> (km + N1), with N1 off reproducing km exactly.
   - Same pattern as km's build B: the code; unit tests, including kn3 with N1 off equal to km3 move for move on 200 scratch deals; a smoke on scratch decks with Goo-zooka and Peculiar Plaza showing the play rate moves; a short README with the carrier suggestion (Whimsicott ex, Ariados) and the footprint expected.
   - Limits: no registration text (the laptop's and Dustin's), no table games, no identity replay, no merge.
   - The previous job, the km3 unplayed-Trainer diagnosis (3c5221e), was read and accepted.
2. **What is running now, and when it ends.** Starting now: reading the parked N1 text, km's build B and the score code, then the code and tests. Probably most of a day.
3. **Files I expect to change.** engine/src/players/ (the new preset and its score), engine tests, and a new folder rl/results/kn_build_2026-09-30/; this file.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None yet.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
- 2026-09-30: build switch N1 as kn<N> (km + the opponent's Active Retreat Cost in the clock; Fable via Dustin): code, unit tests (kn3 with N1 off = km3 on 200 scratch deals), smoke on scratch decks with Goo-zooka and Peculiar Plaza, README. No registration text, no table games, no identity replay, no merge.
