# Setup tester: builder's report (Sonnet credit worker, Oct 15)

Code: `rl/setup_tester/` (`setup_tester.py` command and report, `st_exact.py`, `st_sim.py`, `st_clock.py`, `st_rng.py`,
`plans/kingambit.json`, `test_setup_tester.py`). **The first run, `runs/2026-10-15_kingambit_first_run/`, is superseded** (old defaults;
see its `SUPERSEDED.md`). The amendment-1 run is `runs/2026-10-15_kingambit_amendment1_run/`; it is also before the review fixes
(section "Fix brief 1" below), so it is history too. Both folders stay as they are.
Standard library only; cards through lib/card.py (`consistency.db()`); no engine program; nothing written outside rl/setup_tester/.

## Status
- Tests: 88 (55 before the fix brief, plus 33), all pass at full sizes (8 min 24 s on one process; the 55 passed in 4 min 50 s). `ST_FAST=1` runs smaller sizes.
- Speed: 6,687 deals per second per process (target 2,000). The first run (100,000 deals plus 6 clocks x 20,000, two lists,
  plus the choice runs and comparisons) took about 6.5 minutes on one process, so it was not detached.
- The seed block 24.7B is as START_HERE records it. Run on the card-list ids 73dfed58d1d6 (his list) and 35d98d0dcaf2 (deck 01).

## What the first run shows (reading is the laptop's; plain facts)
- Exact anchors match the SPEC to 5 decimals on both lists.
- Deck 01 against his list, same deals: Kingambit in play is +2.1 / +3.7 / +4.3 points at own turns 3 / 4 / 5 (flagged).
  "Gives up" lists Pawniard/Glimmet/Grimer "in play" falling because they evolve sooner; that is not a loss.
- Test 6: the tester is above lib/consistency.py's solitaire (+3.0 to +18.8 points, turns 2-5). Measured by forcing the
  Mesagoza coin to tails: most of the gap is Mesagoza, which the solitaire model ignores (its own note says so); the rest is
  Copycat/Supporter policy. Both are printed in RESULTS.md.
- Test 7: the tester's first Blade comes earlier than the 64 bot games (never in the horizon 60% against 66%). Printed, not a failure.
- Clock cells with a long "undecided" share (C-his K4, K5) are wide on purpose: the recorded games stop early.

## Where I departed from, or had to interpret, the SPEC
1. **Setup kept a Bench slot free for Pawniard** while Pawniard was still in the deck (first run; the SPEC's step 1 says "up to 3", but test 2, "Pawniard always finds a Bench slot", cannot pass otherwise). **Since amendment 1 that is the T-now trigger only** (a choices row and test 2 run it): under the default first_ko trigger Pawniard is not benched before our first knock-out and no slot is reserved, and the no-knock-out runs (trigger "at_once", fix brief C6) reserve none either.
2. **Sightseer** is played only if a Stage 1 is in the deck (the SPEC names no condition). It adds Stage 1 cards without a hand-limit check (the flagged engine gap). Not in either first-run list.
3. **Professor's Research** "hand has 8 cards or fewer" counts the Professor card itself (`prof_hand_max`).
4. **Energy**: Regigigas takes it "if Muk is in play" with no cap; otherwise the Active (literal).
5. **Empty turns (G5)**: using Mesagoza (even a tails flip) counts as a search played. Evolution by Rare Candy counts as evolved.
6. **K1** counts the whole Pawniard line (Pawniard, Bisharp, Kingambit) so it only rises; G3 "Pawniard in play" is the top card's name, so it falls when it evolves.
7. **Points**: every knock-out is 1 point (no 2-point ex rule); Glimmora heads gives 0.
8. **C-bot extraction**: per opponent turn, k = the larger of the logged empty-Active `Promote` count and the opponent's points at the next logged decision (or the game's final points); a lower bound as the SPEC says. A game won by the deck is cut off (undecided after its last turn); a game the opponent won ends with the third point. **C-his**: a loss without "concession" in its title gets one more knock-out after its last turn, then ends; other games are undecided after their last turn. A rise across a missing turn is undecided only if the rise is above 0.
9. **Undecided** is carried per deal (`und_own`): a measure is yes if decided before, no if the horizon is before it, otherwise undecided (shown as no / as yes).
10. **Bootstrap** (1,000 resamples over recorded games, fixed stream) is used for the clock measures K3-K5 under C-his, C-his seat-matched and C-bot; C-fixed and the setup measures use Wilson / paired intervals. Paired differences on 0/1 measures use exact count formulas equal to `paired()` (copied); `paired()` itself is used for the G5 count.
11. Extra config keys added to the plan file: `prof_hand_max`, `copycat_rule` (`smaller`, `always`, `never`), `poke_ball_over`, `mesagoza_coin`, `glimmora_coin`, `natural_only`, `reshuffle_after_search`.
12. The choices rows ("How much each open choice matters", RESULTS.md) now run in **every** `--versions` run on the base, not only with `--first-run` (fix brief C3). The rows: T-now, T-late, T-pieces, Pawniard-first lead order, Poké Ball over names, Copycat's fallback rule, Copycat never played, the R1 Energy order, the Regigigas-first promotion order, the opponent's hand 2 and 6. Ranges are the per-game bootstrap under the recorded clocks. (The first run's Copycat "always", Blade target 3 and the N x M grid are gone.)

## Not done / not checked
- Dustin has not confirmed any proposed choice or plan line; RESULTS.md says so at the top.
- `swap_pool` and path versions are implemented and the version limit enforced, but only diff versions and the two first-run lists were exercised.
- The engine-rule line citations in `st_sim.py` come from reading `engine/src` today; I did not run the engine.

## Amendment 1 (SPEC_AMENDMENT_1, origin/main 3eea18ee), built Oct 15
Commits: 9789b2de tests first (13 of the 15 new tests fail or error on d0eb22eb; checked in a clean worktree), 8d3514f8 script, 69b0df50 measures and tables.
Run: `runs/2026-10-15_kingambit_amendment1_run/` (RESULTS.md, results.json): his played list 73dfed58d1d6 beside deck 01, 100,000 deals, 20,000 per clock,
C-his, C-his seat-matched, C-bot (inputs `replay_b/games.jsonl` are on this branch), C-fixed fast/medium/slow plus the 190-HP reference. The first run's folder stays as history.
- Script: Regigigas leads; Pawniard held to the bench trigger (T-first-KO default; T-late, T-pieces, T-now run once each on the base); Grimer/Muk benched;
  Glimmora's turn; promotion and Energy orders; Copycat as the N/M rule (grid N 1-3 x M 0-2, headline N=2 M=1, flagged "still to ask Dustin").
- Measures: P1-P5, P4 as two columns (knocks out their strongest; wins outright, a lower bound), the strongest Pokémon per clock, the old G/K lines below "descriptive (speed is not the goal)",
  the not-modelled limits in every summary.
- Not implementable as written / interpreted:
  1. The no-knock-out runs (the 100,000-deal setup tables) have no knock-out to trigger T-first-KO, so they bench Pawniard at once (= T-now) and say so; hence T-now and T-late show +0.0 there, and only T-pieces differs. The real T-first-KO/T-late/T-now comparison is in the clock tables.
  2. C-bot's strongest Pokémon is the panel list's biggest Pokémon (the logs show no HP), flagged, as the amendment allows.
  3. "Ready" under P4 (able this turn) is judged from the simulated hand and board; points we score before the Blade are not modelled, so "wins outright" is a lower bound.
- Nothing is confirmed by Dustin; RESULTS.md says so at the top. Ilima, the Pops and the Helmet are "not valued here".

## Fix brief 1 (TESTER_FIX_BRIEF sections A-C, with INTEGRATION_BRIEF Part A folded into C9), built Oct 15 on the coordinator's addendum
Commits: 9a08e388 tests first (30 of the 40 new or changed tests fail on eeaf54c5, as run in a clean tree), then the code commit that makes them pass.
Run: none. Section D (the A/A1/A2 comparison) is not run here; the laptop runs it after its review.
- **R1** (Glimmora's turn = it attacked at least once): the turn is counted at the attack step. An Active Glimmora with no [D] takes the turn's Energy after Kingambit's (up to [DD]) and before the Pawniard line; `glimmora_energy_first: false` is the choices row.
- **R2**: an Active Alolan Grimer is never evolved into Muk (`no_active_evolve`). P3 is three columns, never pooled: **P3.pawn_lead** (Pawniard starts Active), **P3.pawn_promo** (a Pawniard, Bisharp or Kingambit promoted by the order list, not as "ready to attack"), **P3.grimer_muk** (Grimer or Muk Active, lead or promotion). My reading of "nothing else left": the order list reaches the Pawniard line only after Glimmora, Glimmet and Regigigas, but Bisharp and Kingambit come before Grimer and Muk, so a promoted Bisharp can show with a Grimer still on the Bench. The laptop may want that changed.
- **R3**: slow = knockouts on their turns 3, 5 and 7 against a 180-HP Mega ex. `ref220` is the 220-HP reference with a 10-own-turn horizon and the slow pace carried on over odd opponent turns (3, 5, 7, 9); with only 3, 5, 7 a 10-turn horizon would change nothing. `ref190` stays. A 3-point deal ends at the third non-Glimmora knockout, so k = 3 moments at the fast and slow paces exist only in deals where a Glimmora's coin gave 0 points.
- **Zero by construction** is worked out from the pace (`zero_by_construction`): the P4 and P5 lines (not "no moment") when the pace never delivers the knockouts the Blade needs within the horizon, and the two "wins outright" lines when the strongest Pokémon is worth under 3 points. Printed for every fixed clock, written into results.json. Today it names only medium's two "wins outright" lines.
- **Copycat (B)**: `plans/kingambit.json` holds the value table (`copycat_values`, printed in RESULTS.md); no fitted constants. The decision samples 16 hands per decision from stream `copycat` of the deal. The fallback rule (2 v 8; must-keep = Kingambit, Rare Candy, my reading) runs on the base and every version beside it; RESULTS.md prints how often they disagree and a WARNING if a flagged P-line difference changes between them. The value table, the 16 samples and the must-keep names are mine and open to Dustin's correction.
- **C1-C10**: the summary leads with flagged P-line differences per clock (bootstrap for C-his and C-bot, paired for C-fixed), G and K under "descriptive (no knockouts)" with evolution-only G3 falls dropped; P1 is "Regigigas leads" by `p1_lead`; the choices rows (C3); P4 "given the moment came" and the P5 note (C4); undecided only where the line can still happen, judged from the board, hand and deck when the record stops (C5); no-knockout runs reserve no slot and say so (C6); a knockout gives `points_of(dead card)`, and a version that adds an ex is refused (C7; Alolan Muk ex is not played by the script); Communication never trades a plan card (C8); results.json v2 with timings only in `run_info`, and a test that runs the tester twice under different PYTHONHASHSEED values and compares both files with timings removed (C9); this report and `SUPERSEDED.md` (C10).
- **results.json v2** also keeps `copycat_opp_hand`, `bench_trigger_under_clocks` and `overrides`; `setup_bench_trigger` is `at_once` and `setup_bench_reserved` false (the amended no-knockout rule), not the brief's `now`/true.
- Speed, timed on one process: a small run (his list and one version, 20,000 deals, 5,000 per clock, all 8 clocks, both Copycat rules, plus the 11 choices rows on the base) took 6 min 42 s, 2,479 deals per second per process over the version runs (the amendment-1 figure was 6,687; Copycat by valuation costs about 1.7x per deal, and every version now runs twice). The choices rows are three quarters of that time. At full size (100,000 deals, 20,000 per clock) one version under both rules is about 3.5 minutes and the choices rows about 22 minutes on one process; a 100-version swap_pool is hours and wants `--workers`.
- Not done: section D; swap_pool and path versions are still unexercised.
