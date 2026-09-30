# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** None. The last one is done: the N1 timing assessment (the Fable coordinator via Dustin, Sept 30), commit 2f56033, rl/results/kn_build_2026-09-30/TIMING.md. No build, no games.
   - **(1) Why the tie.** Under kn, Goo-zooka's effect adds exactly +1 wherever the target stays Active, and the card leaving the hand costs exactly 1. The search has no opponent ply, so every leaf shows the +1 and none shows whether it pays. The tie goes to Play by the sorted move order: 492 of 682 and 507 of 677 plays came on the game's first chance turn.
   - **(2) Causes.**
     - N1's term has no condition, and no opponent ply is searched.
     - Grass Knot's damage is not in the clock. This is the carrier's cost: 120 of 677 kn3 plays before a Grass Knot, against 359 of 360 for km3.
     - Underneath: km's clock gives a benched threat a free path to the Active Spot, with no retreat charged.
   - **(3) Candidates:**
     - C1: count N1 only when their Active is damaged or not their clock's threat. Still a tie on the turns it counts.
     - C2: in the clock, a benched threat pays its Active's missing retreat Energy, both sides, N1's static term off. It prices the play by value, about 100 for a turn of their threat against the card's 1. By reading, it covers 6 of the diagnosis's 7 "yes" turns and none of the 3 "no". Its footprint is large.
     - C3: price Grass Knot and Shadow Seeker's retreat-cost damage in the clock. Whimsicott carrier only.
   - **(4) Recommendation:** C2 next as a new code on km, with the full footprint route; C1 the cheap fallback; C3 separate. kn as built should not be registered. Registration stays the laptop's and Dustin's.
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** Which of C1, C2 or C3 (if any) to build next. C2 is recommended.

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
