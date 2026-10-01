# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** None. The last one is done: C2 built as kr<N>, with kro<N> as its one-sided diagnostic (the Fable coordinator via Dustin, Sept 30). See rl/results/kr_build_2026-09-30/README.md.
   - **Commits:** 6a5f225 (tests first, on a scaffold with C2's charge at 0, failing as expected), 7c882b5 (the rule), 639c55b (README, smoke, probe). Only engine/src/players/ and one new test file, engine/tests/kr_judged_turns_test.rs.
   - **Names:** kr<N> (C2 both sides) and kro<N> (the opponent's clock only). No existing code starts with "kr".
   - **Tests:** all pass.
     - The retreat pin against the engine's arithmetic (Goo-zooka, Plaza, Trap Territory, Balloon, Boat, Bombirdier).
     - kr3 with C2 off equals km3 move for move on 200 scratch deals.
     - Four planted faults, each caught.
     - Full suite: 2,031 passed on this branch's engine; 2,011 passed on d363ba8's engine/ with these players/.
   - **The judged turns:** kr3 plays Goo-zooka on 11602 t4 only, not the 6 TIMING.md predicted; none of the 3 "no" turns; km3 on none.
     - TIMING.md's reading was wrong for 5 turns, and the reasons are in km's clock: it picks the readiest attacker as the threat, so an Active that can attack at all is their threat; it doesn't see Ability Energy or the opponent's evolutions; and it doesn't price a stranded damaged Active.
     - The test pins the measured outcome, with each reason. The criterion "play on the 6" is not met, and the README says so.
   - **Smoke** (kn's decks and seeds; the km3 arm equals kn's smoke in 2,400 of 2,400 deals):
     - The tie is gone: Goo-zooka's median first play is turn 7 (kn3: 2), and 364 of 388 Grass Knot-deck plays come before a Grass Knot (km3 359 of 360, kn3 120 of 677).
     - But plays are rare: 1.6% of chances in the plain deck.
     - Plaza falls from 97% to 83%.
   - **Footprint:** large. The control deck with no N1 card differs in 297 of 600 games under kr3 and 117 under kro3, so it is mostly the bot's own half.
   - **Carrier:** Whimsicott ex Ariados, decks 14 and 15. A carrier read would mostly measure C2's general clock change.
   - No table games, no identity replay, no merge. Registration is the laptop's and Dustin's, after the rules switch pins.
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** Whether C2 (kr or kro) is worth a registration given the two findings: 1 of the 6 judged turns, and a large footprint mostly from the bot's own half. A rule that met the judged turns would have to change how the clock picks its threat.

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
