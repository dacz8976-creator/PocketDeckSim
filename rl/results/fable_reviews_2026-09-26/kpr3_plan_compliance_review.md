# kpr3 readout: plan-compliance review (Fable, Sept 26, night)

Decision this informs: how the laptop should read the cloud's kpr3 table (`rl/results/kpr_2026-09-25/` on branch
`claude/pensive-ptolemy-spwc0b`, head aa87fa3) under the Sept 25 plan. Lens: was kpr registered with its formula and
census footprint before the table; was the opponent-side spec issue fixed and recorded before the table; do k3, kp3
and kq3 replay identically at the table's build; and what the kpr code copies show. The numbers themselves are
recounted in `kpr_recompute.md` (sibling review) and `score_v2_kpr3_vs_kp3.txt`; this file repeats only what its
findings need. Everything here was read with `git show`/`git log` on the branch; the working tree was not touched.

Raw material: `kpr3_git_check_output.txt`, `kpr3_git_check2_output.txt` (branch history, diffs, commit messages),
`kpr3_numbers_output.txt` (identity by fingerprint, footprint, fit, vetoes), scripts beside them.

## Bottom line, plainly

1. **Registration before the table: yes, by the letter.** The formula is fixed in commit 9a35f54 (Sept 25 20:30 UTC)
   and amended in 0adfeb7 (21:13), 1981bb4 (21:50) and 14c7d9b (22:22), each with its reason in the commit message;
   the table's binary is e09fb46 (23:29) and its first game ran at about 00:05 UTC on Sept 26. But the README that
   calls itself "the registered spec" did not exist until aa87fa3 (00:51 UTC), after the results were known. The only
   pre-table record is the commit messages.
2. **Census footprint: registered in words, never measured.** 9a35f54 item 7 lists where kpr bites and warns it
   "moves more than the discard decks". Nobody reported the number the plan's routes key on. I measured it:
   **13,117 of 14,000 paired games (93.7%) differ in moves from kp3**, 4,052 (28.9%) in result. The reserve route
   (footprint under 15%) is closed; only the ordinary adoption rule applies. The census's "mainly Hydreigon" was wrong:
   Weezing (-4.7 +/- 1.7) and Blaziken (+4.3 +/- 1.7) move almost as much as Hydreigon (+5.8 +/- 1.9).
3. **Opponent-side spec issue: fixed and recorded before the table, checks rerun.** 1981bb4 carries the finding with
   its measured size (a clock step 10 to 2, about 800 in the evaluator) and the fix; the test at
   `value_functions.rs` 3371-3419 pins it; mutations were rerun at e09fb46 (63 of 64). The order section 8 asked for
   ("fix it, record the reason before any table, rerun the checks, then the table") holds. One asserted fact is not on
   the record: "Dustin's go-ahead" (1981bb4's title; README line 29) is not quoted anywhere.
4. **Identity at the table's own build: 8% by replay, the rest by reading the diff.** k3, kp3, kq3 replay 1,120 of
   1,120 games each at e09fb46 (i < 40 of every pairing; verified field by field, move fingerprint included). The full
   14,000-of-14,000 replays are at 53638a7, whose bot code is 1981bb4's, one amendment behind the table's. The
   53638a7 to e09fb46 engine diff is 106 lines in one file and touches only code reached through `EvalFeatures::KPR`
   (details below), so the claim "changed only inside kpr" is true; it is just not what the README's first sentence
   sounds like. The binary's SHA-256 on the README's line 1 cannot be checked from the branch.
5. **Every number in the README reproduces exactly** (the Hyper Ray table, the twelve cells, the deck averages and their
   paired ranges, 176.1 / 112.2 / 159.3 / 147.3 / 124.5). The table was not restarted (c002d2f's 5,000-line partial
   equals the final file's first 5,000 lines). No branch commit after e09fb46 touches `engine/`.
6. **On the plan's scoreboard kpr3 fails the metric itself.** v2, 27 cells: dMSE +74.7 (95% +27.9 to +123.2, my
   bootstrap; score.py +28.4 to +123.1), real error 8.6 to 12.2. The whole interval is above zero, so "do not adopt"
   does not depend on the mixed rows or any veto. The README reports only the Sept 23 fit (176.1 against 112.2) and
   names only two possible deck vetoes (Vespiquen, Hydreigon); on the Sept 23 cells Altaria's gap also grows +3.0, and
   on v2 five decks (Altaria +3.5, Blaziken +3.6, Hydreigon +5.8, Vespiquen +2.9, Weezing +2.8) and eight cells cross
   the veto lines, three of the cells excluded by the +/-15 band rule.

## Findings, each with its evidence

### F1. Registration is in commit messages only; the README post-dates the table (medium)

- `git log -- rl/results/kpr_2026-09-25/README.md` on the branch returns one commit: aa87fa3, 2026-09-26 00:51:23 UTC
  (`kpr3_git_check_output.txt` lines 123-133: "no README at 9a35f54 / 0adfeb7 / 1981bb4 / 14c7d9b / 53638a7 /
  e09fb46 / c002d2f").
- The table: d141623 (00:15:19) holds 3,500 lines of `kpr3_500.jsonl`, 8f16338 (00:42:52) all 14,000; `timing.txt`
  line 6 says 2,252 s of wall time, so the first game ran at about 00:05, right after the identity replay finished
  (b9a7a21, 00:04:39). The spec commits are 9a35f54 (20:30:43), 0adfeb7 (21:13:32), 1981bb4 (21:50:05), 14c7d9b
  (22:22:32); the table's binary e09fb46 (23:29:41). All before the first game. The plan's wording ("registered before
  their table with formulas fixed in the commit", RUN5 line 380-388 area and section 8 line 115) is met.
- What is not met in spirit: the README's section "Known limits (kept as registered)" (README lines 110-118) and the
  phrase "the registered spec" (line 27) were written after the table. e09fb46's message (23:29) says of the review's
  two limits "written into the kpr README", which did not exist; the two limits (the end-of-turn knockout leaving the
  promotion pending; the self-knockout guard reading the HP now) appear pre-table only inside the raw review output
  `review_1981bb4_workflow_output.json` (df46e0a, 23:30:17; the strings "end-of-turn knockout", "promotion pending",
  "self-knockout" are in it). So the limits were recorded before the table, but as raw review text, not as a
  registered limit.
- Also: the branch's `rl/RUN5.md` is the Sept 24 version (last commit 4ea7601, Sept 24), so the branch does not carry
  the Sept 25 rules it says the laptop will apply; the cloud cites main's docs in 9a35f54's message.

What to do: nothing to rerun. When the laptop writes the reading, cite the commit messages as the registration, not
the README, and say the README was written after the table.

### F2. The footprint was registered in words but never measured; it is 93.7%, so the reserve route is closed (medium)

- 9a35f54's message, item 7 "Footprint (census, rl/results/discard_attack_census_2026-09-25 on main)", lists the
  discard attacks and Energy sources and says "k3 declines only Hyper Ray's chip (19% ...)" and "Broader, and stated
  here so the table isn't misread: because the turn's attach is projected, every Active one attach short now reads as
  ready in both places, on both sides, in every deck" (`kpr3_git_check_output.txt` lines 188-198).
- The plan's reserve route (section 8, line 130, (a)) keys on "the share of the table's paired games in which the new
  bot's play differs from kp3's at least once", threshold 15%. Neither the README nor `deck_averages.py` reports it;
  `analyze_tables.py` prints an "identical" count per cell, but that output is not in the folder.
- Measured (`kpr3_numbers_output.txt`, "footprint"): 13,117 of 14,000 games differ in move fingerprint (93.7%);
  least-changed cell Blaziken v Sceptile 413 of 500, most-changed Altaria v Vespiquen 492 of 500; results differ in
  4,052 games (28.9%). For scale, kd3 differed from kp3 in 69.1% of games and kq3 in 82.8%.
- The census reading (`discard_attack_census_2026-09-25/READING.md` line 28: "would, on this table, mainly change
  Hydreigon") and section 8 line 116 ("kpr's footprint on this table is essentially Hydreigon") were wrong about the
  breadth; 9a35f54's item 7 was right. The README's line 101 ("The discard-attack census predicted exactly this")
  overstates: the census predicted Hydreigon's direction and the deck veto, not a whole-table move.

What to do: the reading should state the footprint (93.7%) and say the reserve route does not apply. For the next
candidate (kt), register the footprint as a number to be measured from the paired games, not a list.

### F3. The opponent-side issue: fixed, recorded, checks rerun, all before the table (verified; one gap)

- The finding and fix are in 1981bb4's message (`kpr3_git_check_output.txt` lines 304-364): under 0adfeb7 the
  opponent's Active was read through its next turn, so at the opponent's turn start its Energy Abilities counted
  twice; on the Suicune board (Chien-Pao ex with no Energy, a Baxcalibur benched, [W] next, against Mega Lucario ex)
  the clock went 10 to 2, about 800 in kpr's value on every line that ended the searcher's turn. Amendment 5 reads the
  opponent's Active at its very next attack (`Horizon::NextAttack`).
- Code: `value_functions.rs` 2036-2049 (`Horizon`), 2125-2139 (the timing rule), and the wiring at 513 (own Active
  score, ThroughNextTurn), 533-534 and 548-549 (own threat ThroughNextTurn, opponent's NextAttack). Test
  `the_opponents_reading_is_the_same_either_side_of_its_turn_start` (3371-3419): clock 10 before and after the
  rotation with NextAttack, 2 if read ThroughNextTurn; kpr minus k equal on both sides of the boundary.
- Checks rerun after the fix: mutations at 1981bb4 (4558464, 53 of 54), the adversarial review of 1981bb4 (df46e0a),
  amendment 6 from that review (14c7d9b), tests (e09fb46, 25 kpr tests), mutations at e09fb46 (580e004, 63 of 64;
  `mutation_results_e09fb46.txt` line 1 shows the baseline at e09fb46), the identity replay at 53638a7 (b9a7a21).
  The order in section 8 line 130 holds.
- Gaps: (a) "Dustin's go-ahead" for amendment 5 is asserted in the commit title and README line 29 but not quoted;
  (b) amendment 6 (14c7d9b) had no review of its own: the 36-agent review read 1981bb4, and 14c7d9b's guard is one
  test plus three mutations (`mutation_results_e09fb46.txt` lines 21-23); (c) the identity replay was built one
  amendment before the table (see F4).

### F4. Identity at the table's own build is 8% by replay; the rest rests on a 106-line diff that I read (low-medium)

- Verified by my own field-by-field comparison (`kpr3_numbers_output.txt`, "identity replays"): at 53638a7, k3
  14,000 of 14,000, kp3 14,000 of 14,000, kq3 14,000 of 14,000, kd3 1,120 of 1,120; at e09fb46, k3, kp3 and kq3
  1,120 of 1,120 each (i < 40 of all 28 pairings); the stopped 9a35f54 replay 10,000 of 10,000. All fields agree
  (a, b, seed, first_seat, moves, winner_seat, points, turns, first_deck_score).
- The gap between the full replay's code and the table's: `git diff 53638a7 e09fb46 -- engine/src` is one file,
  `value_functions.rs`, 106 lines (`kpr3_git_check_output.txt` lines 64-99; the patch is
  `diff_53638a7_e09fb46_engine_src.patch` in the scratchpad). Outside tests it is: the `Action` import (line 10 of the
  patch), the new `end_turn_scored_before_it` (patch lines 18-25; file 2081-2084), and one guard added to
  `projected_active_energy` (patch lines 40-43; file 2130-2132). `projected_active_energy` is reached only through
  `at_next_attack` (2052-2056), which runs only when a `Horizon` is `Some` (2029-2031 for the score, 890-896 for the
  clock, 850-853 for the min), and a `Horizon` is `Some` only when `features.projected_readiness` is true (513,
  533-534, 548-549), which only `EvalFeatures::KPR` sets (291-296; OFF, KQ, KD at 273-290 are false). So k, kp, kq and
  kd cannot reach the changed lines. The claim holds by reading, and by 8% of the table by replay.
- Not verifiable from the branch: the binary's SHA-256 (README line 1) and "the full suite passes at e09fb46: 1,919
  passed" (README line 36; asserted in b9a7a21's message). The laptop's `kpr_mixed_rows_2026-09-26/build_kpr_scan.sh`
  records its own sha and `run_kpr_mixed.sh` replays kp3 on pairings 0-2 (1,500 games) and kpr3 on pairing 1 against
  the cloud's file, which is the right check and adds to the 1,120.

What to do: nothing blocking for a candidate that is not adopted. If the README's line 1 is quoted in the readings
index, say "full replay at 53638a7, 40-deal subset at e09fb46, diff read".

### F5. The decision: kpr3 fails the adoption metric on the plan's scoreboard, before any veto (high, for the reading)

- Plan rule (RUN5 lines 383-387): paired dMSE bootstrap with the whole 95% interval below zero; vetoes decide only
  when that holds. Scoreboard: v2, 27 cells (Altaria v Sceptile quarantined).
- Measured (`kpr3_numbers_output.txt`; `score_v2_kpr3_vs_kp3.txt` lines 46-51 agree): mean squared miss kp3 131.7,
  kpr3 206.4; real error 8.6 to 12.2; dMSE +74.7 with 95% (+27.9, +123.2); real-error margin kp3 minus kpr3 -3.60
  (90% -4.37 to -1.45). On the Sept 23 cells (27): dMSE +66.3 (+31.3, +101.1). k3's 27-cell v2 MSE is 177.5, so kpr3
  is also worse than the k3 reference.
- The README (lines 44-52) reports the Sept 23 fit only, which is not the decision scoreboard, and line 108 leaves
  the verdict to the laptop. Fine as far as it goes, but the reading should say plainly: the mixed rows cannot change
  "do not adopt"; they serve attribution (is Hydreigon better piloted on its own side?) and the investigation list.
- Vetoes as investigation items (`score_v2_kpr3_vs_kp3.txt` lines 52-66; my recount agrees): cells Altaria v
  Hydreigon +7.8, Altaria v Suicune +6.6, Blaziken v Lucario +10.9, Lucario v Suicune +9.2, Suicune v Vespiquen +6.6
  (await mixed rows); Blaziken v Weezing +11.7, Hydreigon v Suicune +9.4, Hydreigon v Vespiquen +15.8 (never count,
  band over 15); decks Altaria +3.5, Blaziken +3.6, Hydreigon +5.8, Vespiquen +2.9, Weezing +2.8. Altaria v Blaziken
  grows exactly +6.0 (58.6 to 52.6 against 76.5), which is "not more than 6"; note it so nobody re-derives it.
- README line 107 names only Vespiquen and Hydreigon as vetoes that "may fire". Altaria's gap grows +3.0 on the very
  cells the README uses (49.7 to 46.7 against 54.0), so the list is incomplete even on its own terms.

### F6. The README's "read the same way" is partial (low)

RUN5 lines 367-368 ask that kpr be "read the same way" as the Altaria network (attack and ability use rates against
kp3 on the same deals, benching, the knockout audit). The README gives Hyper Ray use with and without a knockout
(lines 82-96; all counts reproduce from `kpr3_500.txt` and `identity_kp3_500.txt`) but no Roar in Unison use rate, no
benching counts and no knockout audit of the network readout's form. The `legality_scan` output has only the Hyper
Ray and Chase Order counters, so this needs the laptop's counting scripts if anyone wants it; for a rejected candidate
it is optional.

### F7. Code copies: no hidden-information read, card-agnostic keys, wiring matches the spec (verified)

- Sources read by the projection (`value_functions.rs` 2125-2208): `energy_zone[owner].current/next`,
  `get_turn_effects(turn)`, in-play Pokemon's `ability_used` and `AbilityMechanic` (keyed on the mechanic variants at
  2166-2198, never on a card name), `discard_energies[owner]`, the Active's remaining HP. All public. The one search
  hook, `end_turn_scored_before_it` (2081-2084), asks `observation::hidden_continuation_reason`, which checks whether
  the next player's deck holds `Card::Unknown` (observation.rs 373-381 at e09fb46), the searcher's own knowledge
  state. Test `kpr_reads_no_hidden_card` (3781-3806) swaps hidden hand and deck cards and checks the value does not
  move.
- Wiring: own Active score and own threat over `ThroughNextTurn`, the opponent's over `NextAttack` (513, 533-534,
  548-549); the clock takes `clock(None).min(clock(Some(horizon)))` (851), so the projection can only speed a clock,
  on both sides, as 0adfeb7's amendment 2(b) says. Only slot 0 is projected (891). `get_player`'s KPR arm builds the
  same `PublicPricingPlayer` as KP with the kpr value function (players/mod.rs 549-560); `kpr` parses before `kp`
  (216-221) and the parse test covers `kp3` unchanged (667-672).
- The mutation survivor "Blessing key: total only" (`mutation_results_e09fb46.txt` line 62) is a tie-break that no
  card in the database distinguishes, as stated; fine.
- Known limits that matter for Dustin's decks, not the table: two-type decks (08 and 11) where a `next` drawn inside
  the search is a guess (README line 116); an attach that puts the Active to sleep still counts (line 115). Neither
  affects the eight table lists.

## Answers to the three questions in the task

| question | answer | evidence |
|---|---|---|
| registered with its formula before the table? | yes, in 9a35f54 + 0adfeb7 + 1981bb4 + 14c7d9b (20:30 to 22:22 UTC), table from ~00:05 UTC; the README is post-table | F1 |
| with its census footprint? | in words (9a35f54 item 7); no number; measured now: 93.7% of paired games differ, reserve route closed | F2 |
| opponent-side issue fixed and recorded before the table? | yes: 1981bb4 (21:50), reason and size in the message, test 3371-3419; checks rerun at e09fb46 | F3 |
| k3, kp3, kq3 identical at the table build? | 1,120 of 1,120 each at e09fb46 (8%); 14,000 of 14,000 each at 53638a7; the diff between them is kpr-only (read) | F4 |

## Files in this folder from this review

- `kpr3_plan_compliance_review.md` (this file).
- `kpr3_git_check.sh`, `kpr3_git_check_output.txt`, `kpr3_git_check2.sh`, `kpr3_git_check2_output.txt`: the branch
  reads (commit dates, diffs, commit messages, file first appearances, the c002d2f partial check).
- `kpr3_numbers.py`, `kpr3_numbers_output.txt`: identity by fingerprint, footprint, fit on both scoreboards, paired
  dMSE bootstrap, veto candidates, deck changes.
