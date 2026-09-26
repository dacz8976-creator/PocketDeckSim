# kpr3 readout: Fable's overnight review (Sept 26, 00:30)

**Who wrote this and why.** Fable (the "Deck pilot bot project review" session), overnight on Sept 25 to 26, under Dustin's instruction before bed ("Keep us on track for tonight and make progress. Tokens be damned"). It merges three independent review passes and one recompute run, all in this folder (raw material at the end), all read from the branch with `git show` and `git log`; nothing on the branch or in the working tree was touched. It is independent of the cloud session's own reviewers (the two reviews of 9a35f54 and the adversarial review of 1981bb4). It is a proposal for the laptop session, which owns the reading, and for Dustin, who decides. Nothing here adopts or rejects anything on its own.

**What it reviews.** The cloud's `rl/results/kpr_2026-09-25/README.md` and `kpr3_500.jsonl` on `origin/claude/pensive-ptolemy-spwc0b` at aa87fa3 (engine e09fb46), against "The plan, revised Sept 25" at the end of `rl/RUN5.md` and section 8 of `docs/REVIEW_2026-09-24_direction.md`.

## The verdict, plainly

1. **The readout's numbers hold.** Every figure in the README reproduces exactly from the per-game file: the fit table (mean squared miss 159.3 / 112.2 / 147.3 / 124.5 / 176.1 for k3 / kp3 / kq3 / kd3 / kpr3 on the Sept 23 cells), all eight deck rows with their paired ranges, all twelve "cells that changed most", and the Hyper Ray counts (kpr3 1,105 of 1,227 = 90%, kp3 217 of 1,036 = 21%). The table is paired by deal on the right kp3 baseline, was not restarted, and the formulas were fixed in commits before the first game. The code computes what the README says and reads nothing hidden.

2. **"Worse fit" is the right reading, and on the plan's own scoreboard it is worse still.** The README's 176.1 against 112.2 is on the Sept 23 pooled table over 28 cells, which the plan no longer uses for decisions (scoreboard v2 is not on the branch, so the cloud could not have used it). On v2's 27-cell decision set: kp3 131.7 to kpr3 206.4 (k3 177.5); real error 8.6 to 12.2 points. Paired against kp3, kpr3 is worse by +74.7 points squared with a 95% interval of +28.4 to +123.1, entirely above zero.

3. **"Hydreigon further above Limitless" is true, but it is not the explanation.** Hydreigon does gain the most (+5.8 ± 1.9) and is furthest over Limitless (53.2 against 42.2 on v2). But the table's seven Hydreigon cells carry only 42% of the worse fit; the other 21 cells carry 58%. Suicune's cells carry as much as Hydreigon's. Across the Hydreigon cells, how much more Hyper Ray was chipped has no relation to how much Hydreigon's score moved (three of seven cells: same chip jump, opposite sign). The README's one-sentence story (Hyper Ray chip, so Hydreigon lifts, so the fit is worse) is asserted, not shown, and the README itself says the laptop's mixed rows must decide attribution. What the table shows is that the readiness projection moves every deck's play (93.7% of the paired games differ from kp3's), and the census that said "kpr's footprint is essentially Hydreigon" was wrong.

4. **Not adoptable under any rule in the plan.** The adoption rule needs the whole 95% interval below zero; it is entirely above. So the verdict is "do not adopt" on the metric itself, before any veto is consulted; the mixed rows cannot change it. The reserve route for table-invisible changes is closed twice over: the footprint is 93.7% (the trigger is under 15%) and the no-harm bound fails (the real-error margin's 90% lower bound is −4.37; the route needs −1.0 or above). An override by Dustin would be an override of the adoption metric, not of a veto, and Fable advises against it: the change is everywhere and the fit is worse for seven decks out of eight.

5. **What this means for kpr's future.** The plan wants one pilot for the screen and the table together (route clause (e), and RUN5's "adopt for the screen and the table together"), so "kpr on the brew's side only" would be a second pilot by the back door and is not on offer under the plan. On its merits the brew-side case is also weak: among Dustin's fifteen decks only 06 has a discard attack (Mega Burning), which k3 and kp3 already play at 92%; the part of kpr that reaches every deck, the Zone-attach projection, is the part the table says makes the pilot rate decks worse. What survives: the readiness term goes into B3's feature set, as kd's Weakness term did, where a self-play fit sets its weight instead of the hand-set 500; Hydreigon's over-rating under a rule-correct chip stays an investigation item pointing at the other side of its matchups (the reading rule the cloud quotes is right; the conclusion "a change that is right by the rules" is not yet earned, because the change is much broader than the chip); and the mixed rows are still worth running, for attribution only. kp3 stays the pilot.

## Findings, by severity

### High

**1. On the plan's scoreboard kpr3 fails the adoption metric outright, so the vetoes are never consulted; the README does not say so.**
The README gives a point "mean squared miss" with no interval, no paired ΔMSE and no real-error τ̂, which are the plan's adoption quantities (RUN5 lines 381 to 387; `score.py` lines 283 to 311 for the bootstrap, 379 to 380 for "hi ≥ 0 gives do not adopt before vetoes"). Run through the plan's scorer on v2's 27 cells: ΔMSE kpr3 − kp3 = +74.7, 95% +28.4 to +123.1 (binomial) and +29.9 to +123.2 (by event); τ̂ margin kp3 − kpr3 = −3.60, 90% −4.37 to −1.45. Three independent bootstraps in this folder agree within a point (+27.4 to +122.7; +27.9 to +123.2). The same holds on the Sept 23 cells (+66 on 27 cells, about +31 to +101; +64.1, +30.1 to +98.6 on 28). The README's "the deck-gap vetoes may fire" and "the laptop decides" understate that the result is already decided by the plan's own gate; the mixed rows' value is attribution, not adoption.
Evidence: `score_v2_kpr3_vs_kp3.txt` lines 36 to 50; `kpr3_vs_kp3_v2_check.txt` lines 13 to 19 and 36 to 42; `kpr_recompute.md`; `kpr3_numbers_output.txt`.

**2. The causal story is asserted, not shown, and the cell arithmetic points elsewhere.**
The table is kpr3 v kpr3, so both sides of every cell changed; no mixed row exists yet (the laptop's `kpr_mixed_rows_2026-09-26/` holds only its README and two scripts). Three checks against the README's story:
- The worse fit is mostly outside Hydreigon. Of the +64.0 change in mean squared miss (176.1 − 112.2, Sept 23 cells), Hydreigon's seven cells contribute +26.8 and the other 21 cells +37.2. Largest single contributions: Hydreigon v Vespiquen +11.8, Hydreigon v Suicune +11.0, Suicune v Vespiquen +9.1, Altaria v Blaziken +8.0, Altaria v Hydreigon +7.4, Sceptile v Vespiquen +5.1, Blaziken v Lucario +4.5, Blaziken v Weezing +4.4. Of the eight cells whose miss grew by more than 6, five involve no Hydreigon.
- The Hyper Ray change does not explain the Hydreigon cell moves. Across the seven cells, the rise in non-knockout Hyper Ray use and Hydreigon's score change are uncorrelated (r = −0.24): v Sceptile use 6% to 97% and Hydreigon −3.6 ± 4.4; v Blaziken 1% to 68% and −1.6 ± 4.9; v Vespiquen 15% to 84% and +15.8 ± 5.6; v Lucario 1% to 91% and +8.8; v Altaria 5% to 88% and +7.8; v Suicune 40% to 95% and +9.4; v Weezing 34% to 95% and +4.0.
- Suicune is the second deck with a Hyper Ray-shaped attack (Chien-Pao ex's Diving Icicles, discard all [W]) plus a projected Zone-attach ability (Baxcalibur's Ice Maker, counted from each holder at `value_functions.rs` 2166 to 2170). Its five moved cells (Lucario v Suicune −9.2, Suicune v Weezing +8.5, Suicune v Vespiquen +6.6, Altaria v Suicune −6.6, Hydreigon v Suicune +9.4) sum to +26.1 of the +64.0; the readout has no behaviour counter for it at all (`kpr3_500.txt` prints Hyper Ray and Chase Order only).
Evidence: `kpr3_attribution_check_output.txt` sections D to F; README lines 1, 100 to 108.

### Medium

**3. The headline fit is on the Sept 23 table over 28 cells, not the plan's decision table, and the README does not name its table.**
`analyze_tables.py` line 17 reads `limitless_check_2026-09-23.md`; `deck_averages.py` imports the same function. Scoreboard v2's `limitless_v2_dev.json` and `score.py` are absent on the branch (present on main at fbb0559 and 8cbc348). The 28 cells include the quarantined Altaria v Sceptile (`score.py` line 48; RUN5 line 374 "Altaria v Sceptile in"); the cell is unchanged (42.8 to 42.8), so it only dilutes: on the Sept 23 cells the 27-cell figures are kp3 114.9 to kpr3 181.2 (k3 160.5). The direction is the same on v2, but two of the three largest Hydreigon cell moves are band-excluded from cell vetoes there (finding 4), so the Hydreigon question rests on the deck veto and the mixed rows.
Evidence: README lines 44 to 52; `kpr3_numbers_recomputed.txt` "Sept 23 cells on the 27-cell decision set".

**4. Veto accounting is incomplete and partly wrong.**
README line 107 names only Vespiquen and Hydreigon. On the README's own Sept 23 numbers Altaria also trips (49.7 to 46.7 against 54.0: gap 4.3 to 7.3, +3.0 > 2). On v2's decision set five deck vetoes fire (Hydreigon +5.8, Blaziken +3.6, Altaria +3.5, Vespiquen +2.9, Weezing +2.8) and eight cell vetoes (miss grows more than 6): three never count under rule v2's band rule (Blaziken v Weezing +11.7, band ±23.4; Hydreigon v Suicune +9.4, ±15.2; Hydreigon v Vespiquen +15.8, ±15.3) and five await mixed rows (Altaria v Hydreigon +7.8, Altaria v Suicune +6.6, Blaziken v Lucario +10.9, Lucario v Suicune +9.2, Suicune v Vespiquen +6.6; Altaria v Blaziken is +6.0 exactly, not "more than 6"). The README lists no cell vetoes. Two deck sentences flip between tables: "Blaziken gains too (+4.3, past Limitless)" is a no-change on Sept 23 (57.7: gap 2.1 to 2.2) but a +3.6 deck veto on v2 (55.9); "Lucario and Suicune move toward Limitless" holds for Lucario but Suicune moves away on v2 (47.1: 46.5 to 48.9). None of this changes the verdict (finding 1); it changes what the mixed rows are asked.
Evidence: `score.py` lines 312 to 316 and 336 to 342; `kpr3_vs_kp3_v2_check.txt` lines 40 to 82; `kpr3_numbers_recomputed.txt` "deck averages on v2 cells".

**5. The footprint was registered in words, never measured, and the measurement refutes the census.**
The plan registers kpr "with its census footprint" (RUN5 line 367) and the reserve route keys on the number (section 8 line 130 (a), threshold 15%). 9a35f54's item 7 listed the discard attacks and Energy sources and warned the change "moves more than the discard decks"; section 8 line 116 and the census README said the term would "mainly change Hydreigon". No file on the branch reports the number. Measured from the paired files: only 883 of 14,000 kpr3 games (6.3%) have the same move fingerprint as kp3's, so 13,117 (93.7%) differ (least-changed cell Blaziken v Sceptile 413 of 500, most Altaria v Vespiquen 492 of 500); 4,052 games (28.9%) change result. For scale, kp3 against k3 had 1,242 identical games. Seven of eight decks move beyond paired noise, two of them (Blaziken +4.3 ± 1.7, Weezing −4.7 ± 1.7) with no discard attack in play. README line 102 turns this into "as the registration warned" and line 101 into "the census predicted exactly this"; the honest record is a missed prediction. The reserve route is closed for kpr.
Evidence: `kpr3_numbers_recomputed.txt` "footprint"; `kpr3_attribution_check_output.txt` sections D, E and G; `analyze_tables.py` line 85 prints the identical-game count per cell, so the number was available.

**6. The README that calls itself "the registered spec" was written after the results were known.**
Registration is met by the letter: the formula is in 9a35f54 (Sept 25 20:30 UTC), amended in 0adfeb7 (21:13), 1981bb4 (21:50) and 14c7d9b (22:22), each with its reason in the message; the table binary is e09fb46 (23:29, tests only); the first game ran about 00:05 UTC on Sept 26 (d141623 at 00:15 already holds 3,500 lines; complete at 8f16338 00:42). But `git log -- rl/results/kpr_2026-09-25/README.md` returns one commit, aa87fa3 at 00:51, and e09fb46's message says two review limits were "written into the kpr README" when none existed (they appear pre-table only in `review_1981bb4_workflow_output.json`, df46e0a 23:30). So "Known limits (kept as registered)" (lines 110 to 118) is post hoc as a document, even where its content was known before. "Dustin's go-ahead" for amendment 5 (1981bb4's title; README line 29) is asserted and quoted nowhere on the branch. Amendment 6 (14c7d9b) has one test plus mutations as its guard and no review of its own.
Evidence: `kpr3_git_check_output.txt` lines 123 to 133 and 188 to 198; `timeline_kpr_output.txt`.

**7. A second Hydreigon behaviour changed in the cell that drives the lift, and the README says it did not.**
"Knockout turns are used as before" (README line 96) is true pooled (passes 88 of 2,334 to 38 of 2,434) and false in Hydreigon v Vespiquen, the biggest-moving cell (+15.8): knockout-able Hyper Ray passes fell from 79 of 353 (22.4%) to 35 of 352 (9.9%). In every other Hydreigon cell the passes were already 0 to 4, so the pooled figure is that one cell. Both the knockout and the non-knockout use rose there, so the +15.8 mixes two behaviour changes plus whatever Vespiquen's side did.
Evidence: `identity_kp3_500.txt` line 26 and `kpr3_500.txt` line 26 (branch copies in the scratchpad); `kpr3_counters_output.txt`.

**8. Vespiquen's Chase Order play shifted and the README does not mention it.**
Choices reached 3,510 to 3,762; discard rate 67.5% to 73.6%, higher in six of seven cells (Lucario v Vespiquen 57% to 69%, Vespiquen v Weezing 75% to 87%, Altaria v Vespiquen 54% to 63%, Hydreigon v Vespiquen 48% to 55%); Combee discards 460 to 588. Vespiquen is −2.9 ± 1.8 and its gap grows to a veto candidate. Own side or opponents' side is unknown until the mixed rows; the kq reading used exactly this counter to test its Vespiquen hypothesis (section 8 line 123).
Evidence: `kpr3_counters_output.txt`.

### Low

**9. "Lucario and Suicune move toward Limitless" is a deck-average artifact.** Four Suicune cells' misses grew by 6 or more (Altaria v Suicune −3.5 to −10.1; Lucario v Suicune +0.3 to −8.9; Hydreigon v Suicune +11.7 to +21.1; Suicune v Vespiquen +16.0 to +22.6); the deck average moves toward Limitless on Sept 23 only because +9.2, +8.5, +6.6 and +6.6 offset −9.4, −2.6 and −2.0. Lucario's move is one cell (v Suicune, +9.2 in Suicune's favour) against v Blaziken −10.9. Evidence: `kpr3_attribution_check_output.txt` section D.

**10. Identity at the table's own build is 8% by replay and the rest by reading the diff; the README's first sentence reads as more.** k3, kp3 and kq3 replay 14,000 of 14,000 at 53638a7 (one amendment behind the table) and 1,120 of 1,120 (i < 40, all pairings) at e09fb46; the 53638a7 to e09fb46 engine diff is one file, 106 lines, reachable only through `EvalFeatures::KPR` (`projected_active_energy` via `at_next_attack`, called only when a Horizon is Some, which only KPR sets). So "changed only inside kpr" is true; "replayed the whole table unchanged at 53638a7" should not be read as "at the table's build". The binary's SHA-256 and "1,919 passed" cannot be checked from the branch. The laptop's spot replay (pairings 0 to 2 on its own e09fb46 build) closes this for its rows. Evidence: `kpr3_numbers_output.txt` "identity replays"; `kpr_code_diffs.sh` output; `kpr3_plan_compliance_review.md` item 4.

**11. The readout is only partly "read the same way" as the Altaria network, as RUN5 line 367 asks.** Hyper Ray with and without a knockout only; no Roar in Unison use rate, no benching counts, no knockout audit in the network readout's form; no counter for Diving Icicles, Mega Burning or Terminating Tail. Optional for a rejected candidate, but the mixed-rows scan reuses the same counters, so the gap carries over unless it is closed first.

**12. Provenance nits.** The documented command `analyze_tables.py --base <k3_500 or kp3_500_*>` cannot run as written (one `--base` path; kp3's table is two files); every kp3-paired figure nonetheless reproduces. The branch does not carry the Sept 25 plan (its `rl/RUN5.md` is at 4ea7601, Sept 24; main's is c637259), nor `score.py`, nor `limitless_v2_dev.json`. 9a35f54's message cites the direction doc "on main".

**13. Code-scope notes for "what else moved".** (a) The own-side projection counts this turn's unused Zone attach at mid-turn leaves (`value_functions.rs` 2129 to 2139 and 2151 to 2157: `energy_zone.current` is None only once the attach was made), so at a depth-limited leaf inside the turn "attach not yet made" and "attached to the Active" score the same Active readiness; this applies to all eight decks every turn and is invisible in the per-game files. (b) Known limit 1 (an end-of-turn knockout leaves the promotion pending, "in favour of letting the end of turn take the knockout") is a candidate cause for Weezing's −4.7 ± 1.7, the largest deck drop: Hydreigon and Weezing are the two lists with Deceptive Needle, and Weezing's biggest losses are to Blaziken (−11.7) and Suicune (−8.5). (c) Blaziken v Lucario +10.9 and Blaziken v Weezing +11.7 involve no deck with a projected ability beyond the Zone attach, so the Zone projection alone moves cells by 10 points.

### Verified (info)

- **Numbers.** Fit table, deck rows and ranges (flat pooling over 3,500 games equals `score.py`'s stratified pooling because every cell has 500 games), all twelve cell changes with ranges, Hyper Ray per cell, knockout passes. `kpr3_numbers_recomputed.txt`; `recompute_kpr_output.txt`; `kpr3_attribution_check_output.txt` A to C, G, H.
- **Pairing.** 14,000 games, 28 × 500, no duplicate (pairing, i); seed = 72,000,000 + pairing × 10,000 + i on all; first_seat = i mod 2 on all; deck names, seed and seat match kp3's on all 14,000; bot_a = bot_b = kpr3 on every line. The kp3 baseline is the right file: the branch's `identity_kp3_500.jsonl` equals the laptop's `public_pricing_2026-09-25/kp3_500_worst5.jsonl + kp3_500_rest.jsonl` field by field including the move hash, 14,000 of 14,000 (note: not `per_game_table_2026-09-25`, which holds k3 and b3n1). The c002d2f partial (5,000 games) equals the final file's first 5,000 lines (no restart).
- **Engine did not move after the table.** The `engine/` tree hash 942491391a3d is identical from e09fb46 through aa87fa3 (11 commits). The only bot-code change after the full replay at 53638a7 is 14c7d9b: +34/−3 lines in `value_functions.rs`, reachable only through kpr's flag.
- **The code reads no hidden information and is card-agnostic.** Inputs are `energy_zone[owner].current/next` (2152 to 2154), `discard_energies` (2143), in-play abilities keyed on mechanic (2166 to 2198), remaining HP; `end_turn_scored_before_it` reads the searcher's own knowledge. `PlayerObservation::from_state` masks the opponent's hand, deck and energy menu but copies the Energy Zone unchanged, and the state documents `next` as a visible preview, consistent with Pocket. Horizons as registered: own side ThroughNextTurn, opponent NextAttack (513, 533 to 534, 548 to 549); clock = min(without, with) (851); Active only (891). Test `kpr_reads_no_hidden_card` (3781 to 3810) covers hand and deck, not the Zone; no gap given the Zone is public.
- **Opponent-side spec issue** (under 0adfeb7 the opponent's Active was read through its next turn, so its Energy Abilities counted twice at its turn start; clock 10 to 2, about 800 in kpr's value): fixed in 1981bb4 with a pinning test (3371 to 3419), mutations rerun at 1981bb4 (53 of 54) and e09fb46 (63 of 64; the survivor is a tie-break no current card distinguishes), in the order section 8 line 130 required.
- **No gross tempo or seat effect.** Mean turns 9.71 to 9.67; seat-0 score 50.0 to 50.1; ties 16 to 13. Cost: 2,252 s against kp3's 1,561 s (1.44×), consistent with the double clock scan.

## Questions for the cloud

Paste-ready for Dustin (session messages to the cloud do not land reliably):

```
From Fable's overnight review (via Dustin), on rl/results/kpr_2026-09-25 at aa87fa3:

1. Your fit figures (176.1 v 112.2) are on the Sept 23 table over 28 cells, including the quarantined
   Altaria v Sceptile. The plan decides on scoreboard v2's 27-cell development set, which is not on your
   branch (nor score.py, nor the Sept 25 RUN5). Please pull main and either restate the readout on v2 with
   `rl/results/table_readings_2026-09-24/score.py --rules v2`, or say in the README that the laptop's v2
   reading supersedes your figures. On v2: kp3 131.7 -> kpr3 206.4, dMSE +74.7 (95% +28.4 to +123.1),
   tau margin -3.60 (90% -4.37 to -1.45). That is "do not adopt" on the metric before any veto.
2. Please write kpr's footprint into its record: 13,117 of 14,000 paired games (93.7%) differ from kp3's
   moves, 4,052 (28.9%) change result. The plan registers a candidate with its footprint and the reserve
   route keys on 15%. The census's "essentially Hydreigon" should be recorded as a missed prediction, not
   as "as the registration warned".
3. README fixes: name the table on line 44; list all veto candidates (on v2: five decks, eight cells, three
   of them band-excluded); Altaria trips on your own Sept 23 numbers too; "Blaziken past Limitless" is a
   no-change on Sept 23 and a veto on v2; "Suicune toward Limitless" is a deck-average artifact (four
   Suicune cells' misses grew by 6 or more); "knockout turns used as before" is false in Hydreigon v
   Vespiquen (passes 22.4% -> 9.9%); the `--base` command cannot run as written (kp3 is two files);
   "replayed the whole table unchanged at 53638a7" should say the table's build is covered by 1,120 games
   per bot plus the diff.
4. "Dustin's go-ahead" for 1981bb4: is there a chat record the laptop can cite, or should the reading mark
   it as asserted only?
5. For the laptop's mixed rows, which reuse your legality_scan counters: can you add, with one identity
   replay, use-without-knockout counters for Diving Icicles, Mega Burning and Terminating Tail, a Roar in
   Unison / Ice Maker use rate, and per-cell knockout-able passes? Without them the rows cannot attribute
   Suicune's five moved cells.
6. Fable's proposal (Dustin decides): kpr3 is not adopted; the projected-readiness term goes to B3's
   feature set as kd's Weakness term did; no diagnostic split run (score-only, clock-only, Zone-only)
   since no decision hinges on it, the kd precedent; kt is built on kp3.
```

## What the laptop's rule-v2 read must include

Fable's proposal for the reading file (the laptop owns it):

1. **The decision line, on v2's 27-cell decision set, rules-version stamped:** ΔMSE kpr3 − kp3 +74.7 (95% +28.4 to +123.1 binomial; +29.9 to +123.2 by event); τ̂ kp3 8.57, kpr3 12.18; margin −3.60 (90% −4.37 to −1.45). Verdict: do not adopt, on the metric; vetoes not consulted for the decision. Descriptive beside it: Sept 23 cells 27 (+66) and 28 (+64.1); against k3.
2. **The table used, stated in one sentence,** and that the cloud's README figures are the Sept 23 pooled table over 28 cells, so the two are not read as the same claim.
3. **The footprint:** 13,117 of 14,000 (93.7%) games differ, 4,052 (28.9%) results differ; the reserve route is closed (footprint and no-harm bound both fail); the census prediction "essentially Hydreigon" recorded as missed.
4. **Mixed rows, all 28 pairings both directions, as designed,** read as reporting, not as a route to adoption. Pool per deck for all eight decks, not Hydreigon alone. Answer: (a) does kpr3 pilot Hydreigon's own side better (the get_player test's intent)? (b) which side moved Suicune, Blaziken, Weezing, Altaria and Vespiquen (the five deck-veto candidates)? (c) the five awaiting cells (Altaria v Hydreigon, Altaria v Suicune, Blaziken v Lucario, Lucario v Suicune, Suicune v Vespiquen); the three band-excluded cells reported, marked "never counts".
5. **Behaviour counters in the rows,** per cell: Hyper Ray without a knockout, knockout-able passes (the 22.4% to 9.9% in Hydreigon v Vespiquen), Chase Order discard rate, and, if the cloud adds them, Diving Icicles, Mega Burning, Terminating Tail and the attach-ability use rates.
6. **Identity:** the full replays are at 53638a7; the table's build e09fb46 is covered by 1,120 games per bot plus a kpr-only diff; the laptop's own spot replay of pairings 0 to 2 and the kpr3 pairing-1 replay on its build, as `run_kpr_mixed.sh` already requires.
7. **Disposition:** kpr3 not adopted; kp3 stays the pilot for the screen and the table; the readiness term to B3's feature set; the Hydreigon chip (and the Zone-attach projection's 10-point moves in Blaziken v Lucario and Blaziken v Weezing) on the investigation list; kt built on kp3.
8. **Provenance notes:** README post hoc as a document, spec pre-registered in commit messages; "Dustin's go-ahead" asserted only unless the record is found; no branch commit after e09fb46 touches `engine/`.

## Raw material in this folder

`kpr_recompute.md` (+ `recompute_kpr.py`, `recompute_kpr_output.txt`, `recompute_kpr_summary.json`); `score_v2_kpr3_vs_kp3.txt`, `score_sept23_kpr3_vs_kp3.txt` (the plan's scorer); `kpr3_numbers_recomputed.txt`, `kpr3_vs_kp3_v2_check.txt`, `kpr3_vs_kp3_sept23_check.txt`; `kpr3_attribution_check.py` / `_output.txt`, `kpr3_counters.py` / `_output.txt`; `kpr3_numbers.py` / `_output.txt`; `kpr3_git_check.sh`, `kpr3_git_check2.sh` and outputs; `timeline_kpr.sh` / `_output.txt`; `kpr_code_diffs.sh`; `kpr3_plan_compliance_review.md`. Branch copies and helper scripts are in the session scratchpad under `reviews/` (`branch/kpr_README.md`, `branch/kpr3_500.txt`, `branch/identity_kp3_500.txt`, `branch/value_functions.rs`, `numbers_identity_extra.py`, `copy_kp3_table.sh`, `probe_kp3_sources.sh`, `check_rounding.py`).
