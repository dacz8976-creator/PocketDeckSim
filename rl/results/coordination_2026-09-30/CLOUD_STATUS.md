# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

## STOP (step 8c, Oct 2 01:51 UTC): UNEXPLAINED games found

The cloud's step 8c traces (`rl/results/engine_switch_rules_2026-10/trace_8c_cloud/`) have so far found 2 changed games that `tightened_rule.py` cannot explain. PLAN.md: this stops the switch until they are resolved.
- **step 8, k3, pairing 4 (garchomp_meowth v t-sceptile), deal 7:** a lookahead difference at tick 95 (turn 13); no reach counter in its window or later in the turn; neither probe finds a repair's gate within 3 plies.
- **step 8, km3, pairing 1 (garchomp_meowth v t-blaziken), deal 399:** a lookahead difference at tick 81 (turn 13); the same.
- Both traces reproduce their hand-off rows (move fingerprints equal). The run continues over every remaining game, so the full list is known; this section is updated as more are found. Next: a by-hand look at each (what differs at the tick, and why the probes find nothing).

1. **Current task, and the instruction that set it.** Step 8c of the rules switch (Fable via Dustin, Oct 1 evening; see the last log line). The card-text job (Will, the audit, Trap Territory) waits until it is done. The Oct 1 jobs before it are done:
   - **PLAN step 8b's early-warning rows** (3a107f4, `rl/results/engine_switch_rules_2026-10/early_warning_8b/README.md`), on a scratch build of R (f8cfa9c, engine tree 38af8b0, the laptop's candidate's):
     - 960 games, pairings 32-35 × 40 × km3 and k3 × old, new and watch, every program built from `git archive` in a fresh target folder.
     - The checks:
       - watch = new 160/160 per bot;
       - the pinned old `legality_scan` = the old built from source, 160/160 per bot;
       - no rule findings;
       - the laptop's `sitting2_check.py touched` and `stepsum` pass both bots.
     - **63 of 320 deals change.** By `tightened_rule.py`:
       - 50 on the board;
       - 13 lookahead only, with both halves found by `coin_probe` or `vs_probe`;
       - 0 needing a judgment, 0 unexplained.
     - CONDITION 3: 1 game (km3 34/35). It is one of the 13 lookahead games, explained under the Oct 1 ruling.
     - Rows 13/22: pairing 35 met (15 games). Pairing 34 is NOT met: no unchanged game fired the off-gate discard counter. That is a report line, not a stop.
     - **The trace load:**
       - changed games with no exact counter: 13/320, about 1,050 for step 8 by the plan's arithmetic, all of them the automated check's;
       - needing a hand trace: 0 on this sample (by the rule of three, up to about 240);
       - which number goes on TRACE LOAD is the coordinator's call.
     - CLOUD8B lines, if wanted:
       - `CLOUD8B 3a107f4 km3 rl/results/engine_switch_rules_2026-10/early_warning_8b/8b_new_km3.jsonl`
       - `CLOUD8B 3a107f4 k3 rl/results/engine_switch_rules_2026-10/early_warning_8b/8b_new_k3.jsonl`
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
2. **What is running now, and when it ends.** Step 8c's traces: starting now. Partial results are pushed to `trace_8c_cloud/` as pairings finish.
3. **Files I expect to change.** None. The 8b rows are in `rl/results/engine_switch_rules_2026-10/early_warning_8b/` (this branch). The coin round-2 job changed these on its branch:
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
- 2026-10-01: PLAN.md step 8b's early-warning rows (Fable via Dustin): on a scratch build of R (f8cfa9c; engine = ab56bf4, fresh target dir), pairings 32-35 of the 23.1B block (fire_victini v psychic_confuse, fire_heatmor v meowth_carefree, t-vespiquen v meowth_carefree, l-sharpedo v meowth_carefree), 40 games each, km3 and k3, on the old engine (rl/engine-2026-09-30's source), the new, and the watch build; every changed game classified with tightened_rule.py; rows to rl/results/engine_switch_rules_2026-10/early_warning_8b/. Then idle.
- 2026-10-02: step 8c of the rules switch (Fable via Dustin, Oct 1 evening; first, before the card-text job): every changed game of step 8's hand-off (main 1ba07d9, handoff_8c.tsv: 3,750 changed deals, 306 with no reach counter, CONDITION 3 = 296) traced on old (rl/engine-2026-09-30's source) and new (R f8cfa9c) to the first differing tick, fingerprint-checked against the row, classified with tightened_rule.py, both probes on every lookahead-only game; output rl/results/engine_switch_rules_2026-10/trace_8c_cloud/, pushed as pairings finish. An unexplained game is a stop, written at the top of this file at once.
