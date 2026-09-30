# km's second reader (Sept 30)

**Result: every number that gates agrees with the first reader (`READING_numbers.txt`, `--reps 4000`), and so does the verdict. km3 is ADOPTED as the working pilot in the tables, replacing kta3, "unconfirmed", through the fallback.** The ΔMSE interval spans zero, and no bound sits near a line, so no 20,000-rep rerun is needed. Clause (d) passes, but only just. Its exact lower edge is **+0.0263909** points (mean 4/9 = +0.444444, half-width 0.418054). I found one disagreement, in a number that is only reported and gates nothing (item 2b below).

## How I worked

- **My own scripts**, all in this folder: `sr_lib.py`, `sr1_cells.py`, `sr2_score45.py`, `sr3_clause_d.py`, `sr4_coverage.py`, `sr5_m1m2.py` and `sr6_integrity.py`. Each one writes its output beside itself (`sr*_*.txt`). `sr2_score45_page.txt` is score45's own page.
- **I never opened or imported `read_km.py`, `footprint_km.py` or `km_check.py`.** What I read:
  - the registration: the top block, Amendments 1 and 2, section 5 and section 6;
  - RUN5's frame;
  - `km_config.json`;
  - `STATUS.txt`, `footprint.txt`, `coverage_skip.txt`, `programs.txt`, the recorded input lists and the pairs files;
  - `read_koh.py`'s `paired()` function, and nothing else in that file;
  - the raw game files.
- **I opened `READING_numbers.txt` only after all six scripts had run.** I compared the first reader's two score45 composites with mine only after I had built mine. The task text itself had given me the headline numbers, so I knew those from the start. No parameter was tuned to match.
- **score45.py and score.py** are the registered instrument. I ran them unchanged with `--rules v2 --reps 4000`, giving them my own mixed-row composites.
  - I added taps on `score.pct` and `score.pass_parts`. They record the unrounded bootstrap bounds and each bot's unrounded real error. They don't change the page.
  - My composites use the runner's 500-deal mixed games in the 17 cells with a changed game. In the 28 zero-footprint cells they use kta3's reference games, relabelled.
- **Clause (d) is computed exactly.** Every score is a multiple of 1/2, so I used Python `Fraction` for all the sums and the square root in 60-digit `Decimal`. Its lower edge is exact to about 15 digits.
- **Not re-verified** (all reported only):
  - M3 and the sentinels (X Speed, Boss, Copycat, Hiking Trail);
  - M1's and M2's paired-change intervals on the gating deals;
  - the M2 contrast;
  - the real Limitless cell tables (7a);
  - the second lists' Limitless "figure" column.

## Numbers, beside the first reader's

| # | Item | Mine (second reader) | First reader | |
|---|---|---|---|---|
| 1 | Footprint, 45 cells | **3,117 of 22,500 = 13.8533%** differ from kta3's moves; 615 with a changed result. Bots, seeds (base + pairing × 10,000 + i), seats (i % 2) and files all checked on 45,000 games | 3,117 = 13.85%; 615 | AGREE |
| 1 | Route from the integers | 100 × 3,117 = 311,700 < 15 × 22,500 = 337,500: **reserve route** | reserve | AGREE |
| 1 | Cells with a changed game | 17 of 45, with per-cell counts equal to `footprint.txt`'s (79, 82, 197, 108, 227, 182, 184, 160, 218, 85, 303, 329, 315, 210, 199, 143, 96). They are exactly the 17 cells that hold the panel Altaria or Lucario list | same | AGREE |
| 2 | Mixed-row composites | Mine equal theirs on every field they keep: 0 of 45,000 records differ. My score45 page equals `score45_km3_vs_kta3.txt` (4,000 reps) on all 159 lines except the 2 that name temporary input paths | — | AGREE |
| 2 | ΔMSE (km3 − kta3), 45 cells | **+1.08; 95% −6.977 to +10.141** (unrounded, score.py, 4,000 reps). By event: −8.108 to +10.276. Delta-method cross-check: sd 4.15 | +1.1; −7.0 to +10.1; by event −8.1 to +10.3 | AGREE |
| 2 | Label and near-zero rule | **Spans zero: outcome 3, the fallback.** The width is 17.118, so 5% of it is 0.856. The edges are 6.98 and 10.14 from zero, so neither is near. No rerun. The 44-cell set also spans (−7.540 to +9.879) | SPANS | AGREE |
| 2 | Real error | kta3 13.836 → km3 13.875 (tapped) | 13.8 → 13.9 | AGREE |
| 2 | τ̂ margin (kta3 − km3), (b) | −0.039; **90% −0.2589 to +0.1808**. By event: −0.264 to +0.205. The lower bound is 0.741 above −1.0, so it is not near the line: **PASS** | −0.04; −0.26 to +0.18 | AGREE |
| 2 | Rule-v2 vetoes | One candidate, not counting. Altaria v Suicune's miss grows by 6.2 (limit 6). It is an investigation item because neither side is worse in the mixed rows: Altaria −0.60 ± 1.80, Suicune +5.00 ± 2.14. The largest deck-gap growth is +0.74 (Altaria; limit 2). The 44-cell set is the same | none count; Altaria v Suicune +6.2 investigation | AGREE |
| 2 | Detectable size | sd 4.367; MDE50 8.56; MDE80 12.23 | 4.4; 8.6; 12.2 | AGREE |
| 2b | Detectable size as real error (reported only) | 13.84 → **13.52** (MDE50), 13.84 → **13.39** (MDE80) | 13.80 → 13.49, 13.80 → 13.35 | **DISAGREE (reported only)** |
| 3 | (c), own side, pooled per deck over its changed cells | Altaria +0.18 ± 0.54; Alt/Gren −0.20 ± 0.39; Blaziken +0.20 ± 0.39; Hydreigon 0.00 ± 0.39; Lucario +0.82 ± 0.83; Rayquaza +0.20 ± 0.83; Sceptile −0.10 ± 0.20; Suicune +2.50 ± 1.24; Vespiquen +1.50 ± 1.02; Weezing +1.05 ± 0.88. **No deck worse: PASS.** 3,634 mixed games changed | same, line for line; 3,634 | AGREE |
| 3 | (c) pooling check | Pooling over all 9 of a deck's cells, zero cells included, divides the mean and the half-width by the same factor, so no deck's result can flip. score45's decision-set pooling agrees | — | AGREE |
| 4 | (d) seeds, seats, pairings | All 36,000 games of both arms are as registered. Table deals: base + pairing × 10,000 + i, i < 500, first_seat = i % 2. Block: 22,900,000,000 + row × 10,000 + j, j < 1,500, Lucario on side a, first_seat = j % 2; seeds 22,900,000,000 to 22,900,081,499. Files follow `d_lucario_block.tsv`. Bots: km3 on Lucario, kta3 on the other deck, against kta3/kta3 | K6: no stop | AGREE |
| 4 | (d) kta3 arm, deals 0-499 | **Replays kta3's references: 0 of 4,500 differ** on moves, decisions, score, winner, points, seed, seat, openings and turns. The km3 arm there equals (c)'s mixed rows (0 of 4,500 differ) | replays | AGREE |
| 4 | (d) per row (points) | Altaria −0.45 ± 0.87; Blaziken +0.05 ± 0.69; Hydreigon +0.25 ± 1.33; Sceptile 0.00 ± 0.24; Suicune +2.65 ± 1.69; Vespiquen −0.45 ± 1.64; Weezing +2.35 ± 1.70; Rayquaza −0.75 ± 1.40; Alt/Gren +0.35 ± 0.84. Arm averages are 37.80→37.35, …, 44.30→44.65. 7,046 of 18,000 km3-arm games differ | identical | AGREE |
| 4 | **(d) pooled, full precision** | Mean **4/9 = +0.444444444**. Σ per-row variances of the mean difference = 73663/19990 = 3.684992496. Half-width = 1.96 × √Σ / 9 = **0.418053502**. **Lower edge = +0.026390942** (upper +0.862497946). **PASS** | +0.44 ± 0.42; lower edge "about +0.02" | AGREE |
| 4 | (d) size | sd 0.2133; MDE50 0.418; MDE80 0.597 | 0.213; 0.42; 0.60 | AGREE |
| 5 | Coverage skips (Dustin's condition) | Every group's skip and run sets equal `coverage_skip.txt`'s, in both its per-line list and its summary. Skipped / run: table 15/13, new17 13/4, B2e 56/40, Scizor 0/8, v-lucario_2 0/7, v-suicune_2 5/2, v-weezing_2 5/2, l-charizardy 6/2. All 100 skipped pairings were checked on all 500 deals and all seven fields. Each mixed file holds exactly the pairings that must run, with km3 on the right side | same | AGREE |
| 5 | B2e held-out own side | Manectric +0.10 ± 0.32; Raticate +0.08 ± 0.42; Hoopa/Absol +0.43 ± 0.34; Garchomp 0.00 ± 0.00; Whimsicott +0.05 ± 0.18; Charizard Y Entei +0.51 ± 0.35. **No harm and no held-out veto.** The largest move further from Limitless is +0.41. 2,710 own-side games changed (1,637 held-out) | same | AGREE |
| 5 | Scizor | Own side **−0.23 ± 0.42** (−0.64 to +0.19): no harm. 846 own-side games changed, out of 1,361 changed on both sides. Average 31.06 → 30.44 | same | AGREE |
| 5 | Second lists | v-lucario_2 +0.51 ± 0.91; v-suicune_2 +0.29 ± 0.19; v-weezing_2 −0.06 ± 0.21; l-charizardy +0.30 ± 0.25. No harm | same | AGREE |
| 5 | Step 5's count | 21 own-side tests, all 21 with a changed game; 1 − 0.975^21 = 0.412 | same | AGREE |
| 6 | Counter rows | 3,400 per arm. The cells, deals, seeds, seats and bots are as registered. Move fingerprints against the both-sides games: 0 differ in either arm | equal | AGREE |
| 6 | **M1**, Arena of Antiquity (Lucario's side, 9 cells) | km3 918 of 2,574 = 51/143 = **35.664%**, which is ≥ T1 = 100263/362752 (27.640%) in an exact Fraction comparison, by 8.02 points. **Guard:** kta3's 734 of 3,279 = 22.385% is below T1. **PASS.** It rises in 9 of 9 cells | 35.7% ≥ T1; guard 22.4%; 9 of 9 | AGREE |
| 6 | **M2**, Training Area (Altaria's side, 5 cells) | km3 533 of 1,579 = **33.756%**, which is ≥ T2 = 24383/75980 (32.091%), exactly, by 1.66 points. **Guard:** kta3's 498 of 1,748 = 249/874 = 28.490% is below T2. **PASS.** It rises in 4 of 5 cells | 33.8% ≥ T2; guard 28.5%; 4 of 5 | AGREE |
| 6 | Amendment 2, re-derived (beside) | From the sample rows (deals 200-299): T1 and T2 equal the amendment's fractions. The frozen bootstrap gives 0.10706821380818238 to 0.14692109105529338 (M1) and 0.03862448982989242 to 0.0782545074154864 (M2), bit for bit | amendment | AGREE |
| 7 | Held-out direction (reported beside the verdict) | Manectric −0.300, Raticate +0.000, Hoopa/Absol +0.412, Garchomp +0.025, Whimsicott +0.400, Charizard Y Entei −0.662. That is **2 closer, 3 further, 1 unchanged; mean change in miss −0.021**. Dustin's six: 4 closer, 2 further, mean +0.229 | 2/3/1, −0.02; Dustin's 4/2, +0.23 | AGREE |
| 8 | Integrity | Every changed game on the 45 cells is in the 17 named cells. No mixed-row game differs from kta3's on a deal where the both-sides games matched: 0 in the 45 cells and 0 in every coverage group. Every changed coverage pairing is one where a list carries Training Area (B2 153) or Arena (B3 154). B2e 24 and 72 are reached but unchanged | integrity lines: none | AGREE |
| 8 | Pins | The three hashes are equal in `programs.txt`, the STATUS 'KM PART B DONE' line, `km_inputs.sha256` and the programs on the disk now: deckgym 119389c5…, legality_scan c1ef78e3…, tool_census 9e7bdc1b… (= Amendment 2's). B and the tool source equal the config's | equal | AGREE |
| 8 | Files | The 8 reference files' sha256 equal the config's. km3's two 45-cell files match the hashes recorded before the reading (aff167ac…, 8623d6f9…). Every file in `km_inputs.sha256` (65), `inputs_I` (69), `inputs_T` (39) and `inputs_R` (69) is unchanged. git shows no tracked change since 18bd89c, and dac7dcf holds `footprint.txt` alone | — | AGREE |
| 8 | Identity replays (my comparison) | 4,120 laptop identity games equal their references. The km3 smoke (120) and 560 km3 identity games equal km3's registered games. The cloud's smoke file is on the cloud branch, not this checkout, so I didn't compare that one pair | 15 lines equal | AGREE |
| 8 | Timing and scan pages | Wall 4.296/4.045 = 1.062 and CPU 39.593/37.915 = 1.044, within 1.25. The 39 scan pages show no finding | 1.062; 39 clean | AGREE |

**Item 2b, the one disagreement, explained.**
- The conversion is sqrt(kta3's real error² − δ).
- score.py's own real error for kta3 on the 45 cells is 13.836 (tapped). The page prints it as "13.8".
- The first reader's figures come out exactly from 13.80: sqrt(13.80² − 8.559) = 13.486 and sqrt(13.80² − 12.227) = 13.350.
- From 13.836 they are 13.52 and 13.39, so the right line reads "13.84 → 13.52 (MDE50), 13.84 → 13.39 (MDE80)".
- kta's first reader made the same slip, which its reconciler corrected. The difference is 0.03 to 0.04 points, in a number that gates nothing.

**Beside (d), reported only.**
- The gain rests on two rows: Suicune supplies 66% of the pooled sum and Weezing 59%.
- Without either row the pooled figure would not clear zero: +0.169 ± 0.420 without Suicune, +0.206 ± 0.419 without Weezing. Three rows are negative (Altaria, Vespiquen, Rayquaza).
- A reading that is not the registered one also passes. Stratifying each row into its 500 table deals and 1,500 block deals, weighted 1/4 and 3/4, gives +0.444 ± 0.418, lower edge +0.0265.
- The registered statistic pools each row's 2,000 deals (step 4 (d): "A row is its 500 table deals and its 1,500 block deals, pooled: N = 2,000"). It is analytic, not a bootstrap, so the near-zero rerun rule doesn't apply. (d) is read once.

## Verdict (section 6, "Outcomes fixed now", and RUN5's three outcomes), written from my numbers

- **Preconditions: PASS.** The pins, the references, the input lists, the identity replays, the timing (1.062) and the finding-free scan pages all hold. The integrity lines are clean.
- **(a): reserve route.** The footprint is 13.85%, under 15% (311,700 < 337,500).
- **The ΔMSE label: spans zero** (−6.98 to +10.14): outcome 3, "undetectable at this size".
  - It is not wholly above zero, so outcome 2's no-fallback failure does not apply.
  - No edge is near zero, so the label is final at 4,000 reps.
- **So the fallback decides, with its four tests:**
  1. **No harm: PASS.** (b): the τ̂ 90% lower bound is −0.259, which is ≥ −1.0, and no rule-v2 veto counts. (c): no meta deck's own side is worse.
  2. **The coverage decks: PASS.** No B2e held-out harm or veto, and no harm for Scizor or any second list.
  3. **(d) on Lucario: PASS.** It is +0.444 ± 0.418, and the whole interval is above zero, with the lower edge at +0.0264.
  4. **The behavioural footprint: PASS.**
     - M1 is 35.66% against T1 = 27.64%, with the guard clear (kta3 22.38%).
     - M2 is 33.76% against T2 = 32.09%, with the guard clear (kta3 28.49%).
- **Result: km3 ADOPTED as the working pilot in the tables, replacing kta3, "unconfirmed".**
  - Its use in the screen and the floor waits for the official engine switch (Amendment 1 (g)).
  - Confirmation is the no-harm re-check at the post-freeze pull (step 7). The lapse clause applies through kta's, kog's, kpg's and koa's rows.
- **Held-out direction, beside the verdict:** 2 closer, 3 further, 1 unchanged, mean change in miss −0.02. It gates nothing.

**For Dustin, in plain words:**
- The verdict is the one the registration fixed, and both readers reach it from their own code.
- **Two margins are thin:**
  - Lucario's gain clears zero by only about 0.03 points (+0.44 ± 0.42). It comes mostly from two matchups, against Suicune and Weezing.
  - Training Area's rate clears its bar by 1.7 points.
- They still pass as registered. Neither one can be rerun or topped up with more games.
- Arena of Antiquity's rise is large and shows in all nine Lucario matchups: 22% → 36%.
- One cell, Altaria v Suicune, moved 6.2 points further from the real result. It doesn't count as a veto, because neither deck played its own side worse in the mixed games.
- score45's own page says "ADOPTION RULE (v2): do not adopt". That is the ordinary rule's line, which this reading doesn't use. It is not the verdict.

## Reconciliation (Sept 30; the reconciler)

**Final verdict: km3 is ADOPTED as the working pilot in the tables, replacing kta3, "unconfirmed", through the fallback.** The first reader got nothing wrong that gates. There is one correction, in a number that is only reported (item 2b). There are also three fixes to what the reading prints (S1, S2, and the (d) row-share sentence), and none of them changes the outcome. Clause (d)'s lower edge is **+0.026390942440085**. Three independent computations agree on it, so the pass is real, but it is thin.

**How I worked.**
- **What I read:** this report, `OUTCOME_AUDIT.md`, `READING_numbers.txt`, the registration (the top block, step 4, step 5b and section 6), RUN5's frame, `GO_km_tables`, STATUS part R and git.
- **What I didn't open:** `read_km.py`, `footprint_km.py` and `km_check.py`. I also didn't open either reader's scripts (`sr*.py`, `spot*.py`).
- **Two scripts of my own,** both in this folder:
  - `rc_clause_d.py` → `rc_clause_d.txt`: clause (d) from the seven raw (d) files. It is written from step 4 (d) and `read_koh.py`'s `paired()` (lines 109-118). It reads each game's row and deal from the seed. The sums are exact fractions, the square root is done in 60-digit Decimal, and a plain-float copy of `paired()` sits beside the exact figure.
  - `rc_score45.py` → `rc_score45.txt`: score45.py/score.py, unchanged, at `--reps 4000` on the first reader's own composites (`score45_inputs/`). Taps record the unrounded percentiles and each bot's unrounded real error. My page equals `score45_km3_vs_kta3.txt` on all 159 lines except the one that names score45's temporary Limitless-cells file.
- **No game was played and nothing was committed.**

| Point | Who is right | What the files show | Gates? |
|---|---|---|---|
| Item 2b: detectable size as real error (the second reader's DISAGREE) | **Second reader** | score.py's own real error for kta3 on the 45 cells is **13.8362** (tapped). The page prints it as "13.8". At 4,000 reps the sd is 4.3669, MDE50 8.5591 and MDE80 12.2273. From 13.8362 the conversion gives **13.84 → 13.52 (MDE50) and 13.84 → 13.39 (MDE80)**. The first reader's 13.49 and 13.35 come exactly from 13.80, the page's rounded figure (13.4863 and 13.3496). This is the same slip kta's first reader made. | No (reported only) |
| S1: the held-out direction is not beside the verdict | **Audit** | R:584 (step 5b item 4) says "beside every verdict", and so does RUN5:567, in Dustin's words. `READING_numbers.txt` prints the direction only in 5a (L180-187), not in the verdict block (L282-299). Beside the verdict it should read: **2 closer, 3 further, 1 unchanged, mean change in miss −0.02.** | No |
| S2: (d) printed to two decimals | **Audit, on the record.** Its citations are by analogy only: R:13 and R:512 are about M1's and M2's T, and R:532 is about τ̂. No registered line fixes how many digits (d) prints. | "+0.44 +/- 0.42" (L143, L287) can't show whether the pass is real, because it turns on the third decimal. The three computations below settle it. The line should print "+0.4444 ± 0.4181 (95% interval +0.0264 to +0.8625)". | No |

**Clause (d): three independent computations.**

| Computation | Mean | Half-width | Lower edge |
|---|---|---|---|
| First reader (L143, L287; printed only) | +0.44 | 0.42 | "about +0.02". The printed digits only place it between +0.010 and +0.030 |
| Second reader (`sr3_clause_d.txt`) | 4/9 | 0.418053502 | **+0.026390942440085** |
| Audit (exact fractions) | 4/9 | 0.4181 | **+0.0264**; exact test 16 > 14.16 |
| Reconciler, exact (`rc_clause_d.txt`) | 4/9 = 0.444444444444444 | 0.418053502004359 | **+0.026390942440085** |
| Reconciler, float copy of `paired()` | 0.4444444444444444 | 0.418053502004359 | 0.02639094244008544 |

- **The exact figures:**
  - The sum of the nine per-row variances of the mean is 73663/19990 = 3.684992496248124.
  - The square-root-free test is (9 × mean)² = 16 > 1.96² × sum = 14.156267. It holds, and z = 2.08.
  - **Mean minus half-width is above zero, by 0.0264 points: PASS.**
- **The games behind it:**
  - Each arm has 18,000 games, exactly rows 0-8 × deals 0-1,999, read from the seeds.
  - Opponents, seats (first_seat = i mod 2, and j mod 2 in the block) and bots (km3 on Lucario with kta3 on the other deck, against kta3 on both) are right on all 36,000.
  - Seeds, seats and decks are equal across the two arms.
  - 7,046 km3-arm games differ from the kta3 arm's.
  - The kta3 arm on deals 0-499 replays kta3's reference files, 4,500 of 4,500, on moves, decisions, score, winner, seed, seat, decks and turns.
  - All nine rows equal L134-142.
- **Nothing reopens it.**
  - (d) is read once (R:23, R:528, R:563).
  - The near-zero rerun rule covers only the two ΔMSE edges and the τ̂ edge (R:24, R:529-533).
  - (d)'s interval is a formula, not a bootstrap, so the same games always give the same interval.
- **How thin it is (reported only; no registered rule reads this):**
  - About 5 km3-arm games going from a win to a loss (4.75, with the variance held fixed) would bring the lower edge to zero.
  - Dropping any one of three rows, not two, takes the 8-row lower edge to zero or below: Suicune (−0.252), Weezing (−0.213) and **Altaria/Greninja (−0.002)**. Both reports named only the first two.
  - The first reader's sentence "one row supplies more than half" (L145, L299) should say that two rows each supply more than half: Suicune 66.2% and Weezing 58.8%.
  - The gate is the nine-row pooled interval (R:561, R:563, R:583), so none of this changes the pass.

**The other gating numbers.** Both reports agree with the first reader on every one, and I checked the arithmetic on the agreed counts exactly:
- **Footprint:** 100 × 3,117 = 311,700 < 337,500, so the reserve route.
- **M1:** 918 × 362,752 = 333,006,336 ≥ 100,263 × 2,574 = 258,076,962. The guard is below T1: 266,259,968 < 328,762,377. km3 clears T1 by 8.02 points.
- **M2:** 533 × 75,980 = 40,497,340 ≥ 24,383 × 1,579 = 38,500,757. The guard is below T2: 37,838,040 < 42,621,484. km3 clears T2 by **1.66 points**.
- **T1 and T2** are the exact midpoints of the sample rates.
- **ΔMSE at 4,000 reps:** −6.9769 to +10.1414, so it **spans** zero. 5% of the width is 0.856, so neither edge is near.
- **τ̂:** the lower bound is −0.2589, far from −1.0.

**The audit's notes (N1-N10).** None of them gates. Where I checked:
- **N1:** confirmed. It is widened above to three rows.
- **N7:** the go-ahead ("The cloud has the message go ahead on the tables", about 02:20 UTC) was recorded at c74d8df, before any km game, together with the laptop's reading that the tables start once the preparation has passed. That order was kept.
  - `GO_km_tables` was written at 09:31:34 UTC (file time). That is 14 s after e308a65 (09:31:20) and 10 s before part R started (09:31:44).
  - Its own text says "about 09:45 UTC", which is a record slip of about 14 minutes and gates nothing.
- **N3:** K7 still reads the ΔMSE lower edge only as printed. This is flagged for the second time and should be fixed before the next reading reuses the code. It doesn't matter here: the lower edge is −6.98.
- **Housekeeping:** `second_reader/__pycache__/` was left by the second reader's scripts. Leave it out of the commit.

**The verdict (section 6, and RUN5's three outcomes):**
- **Preconditions:** PASS.
- **(a):** the reserve route (13.85%).
- **ΔMSE:** spans zero, "undetectable at this size". It is not wholly above zero, so it isn't a fail with no fallback. The fallback decides.
- **(b):** PASS. The τ̂ lower bound is −0.26, and no veto counts. Altaria v Suicune (+6.2) is an investigation item.
- **(c):** PASS. No deck is worse.
- **Coverage:** PASS. There is no harm to a B2e held-out deck, Scizor or a second list.
- **(d):** PASS, +0.4444 ± 0.4181, lower edge +0.0264.
- **M1:** PASS, 35.66% against T1 = 27.64%. The guard (22.38%) is clear.
- **M2:** PASS, 33.76% against T2 = 32.09%. The guard (28.49%) is clear.
- **Result: km3 ADOPTED as the working pilot in the tables, replacing kta3, "unconfirmed".** Its use in the screen and the floor waits for the official engine switch (Amendment 1 (g)).
- **Held-out direction, beside the verdict:** 2 closer, 3 further, 1 unchanged, mean change in miss −0.02. It gates nothing.
- **Still to come:**
  - the commit to the post-freeze list, made before that data is opened (step 7);
  - the no-harm re-check at that pull;
  - the lapse clause, through kta's, kog's, kpg's and koa's rows.

**For Dustin, in plain words:**
- **Nothing to decide for the verdict.** It is the outcome the registration fixed, and three separate checks reach it.
- **One line to confirm (N7):** did "The cloud has the message go ahead on the tables" (about 02:20 UTC) mean "run the tables once the preparation passes"? The laptop read it that way and wrote that reading down before any km game. If you meant something else, the verdict waits for your word. The games and numbers stand either way.
- **Two thin margins, both passing as registered, and neither can be rerun or topped up:**
  - Lucario's gain clears zero by 0.026 points (+0.44 ± 0.42). It rests on the Suicune and Weezing matchups.
  - Training Area's rate clears its bar by 1.7 points. Its prediction that the Stage 1 matchups wouldn't rise did not hold (N2). That is worth writing down, but it doesn't gate.
- **A heads-up:** score45's page says "do not adopt". That is the ordinary rule's line, which this reading doesn't use. It is not the verdict.
