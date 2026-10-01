# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** None: idle, as the coordinator asked (Oct 1, via Dustin: "Then idle; nothing else is queued"). The two Oct 1 jobs are done:
   - **Job 1, F8** (5a929c0): accepted. F8's wording goes into rules/09 and PLAN.md at the pin.
   - **Job 2, the later round of coin-flip prevention**, all seven sites, on `claude/coin-prevention-round2` (from Sonnet's R, 1abdbe8; README `rl/results/coin_prevention_round2_2026-10-01/README.md`, 78af4e8). The six sites were accepted (76b87cd). Round 2 stays out of the current switch and goes in the next one.
     - Mega Kangaskhan ex's second punch, after the fifth file was approved:
       - 9145eb3: the tests, the knockout-then-promotion case and the non-knockout case, both failing;
       - 29e126a: the fix;
       - bfe8aeb: the counters;
       - 78af4e8: the README.
     - `engine/src/state/mod.rs`: only the pending-hit check changed. It now also recognises an `ApplyQueuedAttackDamage` aimed at the empty Active, from the other player's frame.
       - The `ApplyDamage` arm's attacker clause is not mirrored. A Mega Kangaskhan ex Knocked Out on its own turn gives 3 points and ends the game (checked in a scratch copy), and mirroring it would have reordered the first round's choices.
     - Full suite at 29e126a: 2,027 passed, 0 failed (R's 2,018 plus the 9 new tests). The counter probe: 32 checks, 0 failures.
     - The scratch smoke, rerun on the final engine, gives byte-identical game files to its first run (80 of 80 for each scan).
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None. Job 2 changed these on its branch:
   - engine: `engine/src/actions/apply_attack_action.rs`, `engine/src/actions/apply_action.rs`, `engine/src/state/mod.rs` (the approved fifth file), `engine/tests/pokemon/meowth_carefree_steps_test.rs`;
   - results: `rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py` (the counters) and `rl/results/coin_prevention_round2_2026-10-01/`.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None. The fifth-file question was answered yes (Oct 1), for the pending-hit check only.

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
- 2026-10-01: F8 (Fable via Dustin): upstream 09e964f's hp_aura_promotion_test.rs ported as a scratch test under rl/results/engine_switch_rules_2026-10/f8/, run against d363ba8's engine; F8.md on fix 1. No engine change.
- 2026-10-01: coin-flip prevention, the later round (Fable via Dustin): the seven recorded sites, failing tests first, then the gated fix; on a new branch claude/coin-prevention-round2 cut from Sonnet's R (1abdbe8). Own-Bench form left open. No players/ change, no table games, no merge.
- 2026-10-01: coin-flip prevention, the later round's seventh site (Fable via Dustin): Mega Kangaskhan ex's second punch on claude/coin-prevention-round2, with engine/src/state/mod.rs's pending-hit check as the approved fifth file; tests first (the knockout-then-promotion case and the non-knockout case), then the fix, the full suite and the README. Then idle. Round 2 goes in the next switch, not the current one.
