# Setup tester: builder's report (Sonnet credit worker, Oct 15)

Code: `rl/setup_tester/` (`setup_tester.py` command and report, `st_exact.py`, `st_sim.py`, `st_clock.py`, `st_rng.py`,
`plans/kingambit.json`, `test_setup_tester.py`). First run: `runs/2026-10-15_kingambit_first_run/` (RESULTS.md, results.json).
Standard library only; cards through lib/card.py (`consistency.db()`); no engine program; nothing written outside rl/setup_tester/.

## Status
- Tests: 55 (40 + 15 amendment tests), all pass at full sizes (about 4 min 50 s on one process). `ST_FAST=1` runs smaller sizes.
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
1. **Setup keeps a Bench slot free for Pawniard** while Pawniard is still in the deck, as well as in step 3(c). The SPEC's step 1 says "up to 3", but test 2 ("Pawniard always finds a Bench slot") cannot pass otherwise.
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
12. `--first-run` also runs the SPEC's alternatives of the five confirmable choices once on the base (RESULTS.md "How much each confirmable choice matters"). Alternatives are my picks: Pawniard-first lead order, Regigigas-first promotion, Copycat "always", Blade target 3, Poké Ball over names, opponent hand 2 and 6; "fast" alternatives are the C-fixed medium and slow clocks.

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
