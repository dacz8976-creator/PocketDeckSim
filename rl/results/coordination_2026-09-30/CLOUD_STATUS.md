# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** Two jobs (the Fable coordinator via Dustin, Oct 1). Each is tests first; no table games, no players/ change, no merge.
   - **Job 1, F8** (rl/results/engine_switch_rules_2026-10/PLAN.md): port upstream 09e964f's hp_aura_promotion_test.rs (the Lilligant case) as a scratch test under rl/results/engine_switch_rules_2026-10/f8/ (not in engine/), and run it against d363ba8's engine. F8.md answers whether the fork already covers fix 1, with file:line. No engine change. On this branch.
   - **Job 2, the later round of coin-flip prevention:** the seven sites recorded in rl/results/coin_prevention_repair_2026-09-30/README.md:
     - the sites: Wild Swing, Wellspring Dance, Tornado Shot, Double Splash / Triple Bombardment, Mega Kangaskhan ex's second punch, Mischievous Ring, Litter;
     - method: each with a failing test first, then the gated fix through the same queued_attack_damage_choice path and counters;
     - branch: a NEW branch, claude/coin-prevention-round2, cut from Sonnet's R (1abdbe8, origin/sonnet/rules-fixes);
     - unchanged: the own-Bench form of also_choice_bench_damage stays open, as Dustin ruled;
     - full suite after the last engine commit; a README with reach per card and the lists under decks/ that hold them;
     - I will ask here before touching any file beyond the four the first round used.
   - kr/kro (7c882b5, README 639c55b) was accepted as a build and as a finding; kr will not be registered.
2. **What is running now, and when it ends.** Starting now: job 1 (fetching upstream 09e964f read-only, the scratch test, F8.md), then job 2. Within the two days given.
3. **Files I expect to change.**
   - Job 1: rl/results/engine_switch_rules_2026-10/f8/ (new), on this branch.
   - Job 2, on the new branch: the first round's four files (engine/src/actions/apply_attack_action.rs, apply_action.rs, attack_outcome.rs, engine/src/hooks/core.rs), their tests, and rl/results/coin_prevention_round2_2026-10-01/.
   - This file.
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
- 2026-09-30: carrier lists for the rules switch (Fable via Dustin; PLAN.md step 3): four development lists from the committed Limitless archive (Garchomp Meowth, Togekiss Meowth, Hisuian Goodra, Mega Houndoom ex Victini), card-checked, with provenance; rl/results/engine_switch_rules_2026-10/carriers/. No games beyond the legality scan, no engine change.
- 2026-09-30: N1 timing assessment (Fable via Dustin): rl/results/kn_build_2026-09-30/TIMING.md, why kn3 plays Goo-zooka on a tie, which simplification causes it, up to three list-free candidate rules with footprint, carrier and smoke, and a recommendation. No new build, no table games.
- 2026-09-30: build C2 (TIMING.md; Fable via Dustin): a benched threat pays its Active's missing retreat Energy in km's clock, both sides, N1 off, plus a one-sided diagnostic code; tests first (the retreat pin, 200 scratch deals with the term off = km3, the 10 judged turns), then the scratch smoke and README. players/ and tests only; no table games, no identity replay, no merge.
- 2026-10-01: F8 (Fable via Dustin): upstream 09e964f's hp_aura_promotion_test.rs ported as a scratch test under rl/results/engine_switch_rules_2026-10/f8/, run against d363ba8's engine; F8.md on fix 1. No engine change.
- 2026-10-01: coin-flip prevention, the later round (Fable via Dustin): the seven recorded sites, failing tests first, then the gated fix; on a new branch claude/coin-prevention-round2 cut from Sonnet's R (1abdbe8). Own-Bench form left open. No players/ change, no table games, no merge.
