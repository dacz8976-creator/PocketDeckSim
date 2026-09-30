# kta's second reader (Sept 29-30)

**Result: every number that gates agrees with the first reader (`READING_numbers.txt`, `--reps 4000`), and so does the verdict: kta3 is ADOPTED as the working pilot, "unconfirmed".** The ΔMSE label is still PENDING between "wholly below zero" and "spans zero", and the 20,000-rep rerun decides which one is recorded. Every gate passes under both labels, so the rerun cannot change the outcome. I found one small disagreement, in a number that is only reported and gates nothing (item 12 below).

## How I worked

- I wrote my own scripts, which sit in this folder: `sr_lib.py`, `sr1_cells.py`, `sr2_score45.py`, `sr3_clause_d.py`, `sr4_coverage.py`, `sr5_ab_jasmine.py` and `sr6_identity.py`. Each script writes its output beside itself (`sr*_*.txt`). `sr2_score45_page.txt` is score45's own page.
- **I never opened `read_kta.py` or `test_read_kta.sh`.** From the first reader's side I read only these:
  - the registration;
  - RUN5's frame;
  - `STATUS.txt`, `footprint.txt`, `coverage_skip.txt`, `identity_check.txt` and the pairs files;
  - `READING_numbers.txt`;
  - the first reader's two score45 mixed-row composites, which I compared with mine after I had built mine.
- **One disclosure.** I read `READING_numbers.txt` at the start, as the task pointed me to it, so I knew its numbers before I computed. Every number below comes from my own code run on the raw `ec7e1a8_fresh_*` files. The comparisons are mechanical, and no parameter was tuned to match.
- **score45.py / score.py** are the registered instrument. I ran them unchanged with `--rules v2 --reps 4000`, giving them my own mixed-row composites.
  - I added one thing: a tap on `score.pct` that records the unrounded percentiles it returns. This is how the near-zero rule can be read beyond one decimal. The page's text is not changed by the tap.
  - My composites use the runner's 500-deal mixed games in the 17 cells with a changed game. In the 28 zero-footprint cells they use kog3's both-sides games, relabelled (registration 5.2 (c), 5.5 last bullet).
  - The first reader's composites equal mine on every field they keep (a, b, files, bots, seed, seat, i, pairing, moves, score): 0 of 45,000 records differ.
  - Mine carry every field of the source games; theirs keep a subset and add `mixed_source`.
- **The saved page changed under me.** `score45_kta3_vs_kog3.txt` on the disk was overwritten during my work by the other reader's 20,000-rep run (its `.reps` now reads 20000). So I compared my 4,000-rep page with `READING_numbers.txt`'s printed figures. Line by line against that 20,000-rep page, mine differs only in the bootstrap lines and the adoption line; the per-cell and deck tables are identical.
- **What I did not re-verify** (all reported only): the Rayquaza traces, the Suicune and Rayquaza real-cell tables (7a, 7b), McNemar p-values, the Tool placement counts, and the second lists' Limitless "figure" column.

## Numbers, beside the first reader's

| # | Item | Mine (second reader) | First reader | |
|---|---|---|---|---|
| 1 | Footprint, 45 cells | 528 of 22,500 = 2.3467%; 113 with a changed result; **reserve route** | 528 = 2.35%, 113; reserve | AGREE |
| 1 | Cells with a changed game | 17 of 45, per-cell counts identical (10, 27, 23, 32, 30, 31, 14, 44, 27, 50, 48, 37, 31, 30, 23, 17, 54); exactly the 17 cells with Suicune or Rayquaza | same | AGREE |
| 2 | ΔMSE (kta3 − kog3), 45 cells | −4.25; 95% **−8.98 to +0.07** (unrounded, score.py at 4,000 reps); by event −8.98 to +0.14 | −4.3; −9.0 to +0.1; by event −9.0 to +0.1 | AGREE |
| 2 | Label | spans zero at 4,000 reps. The upper edge, +0.066, is within 5% of the width (0.452) of 0, so it is PENDING (below or spans) and the 20,000 rerun decides. The lower edge, −8.98, is far from 0, so "wholly above zero" is ruled out. | PENDING below/spans | AGREE |
| 2 | Real error | kog3 13.550 → kta3 13.392 | 13.6 → 13.4 | AGREE |
| 2 | τ̂ margin (kog3 − kta3) | +0.158; 90% **+0.019 to +0.254**; by event +0.016 to +0.246 | +0.16; +0.02 to +0.25; +0.02 to +0.25 | AGREE |
| 2 | Rule-v2 vetoes | none fire: the largest cell-miss growth is +1.40 (limit 6) and the largest deck-gap growth is +0.09 (limit 2). The 44-cell set gives the same label and no veto. | none; 44-cell set the same | AGREE |
| 2 | Detectable size | sd 2.31; MDE50 4.52; MDE80 6.46 | 2.3; 4.5; 6.5 | AGREE |
| 3 | (c), own side pooled per deck | Altaria −0.10 ± 0.20; Alt/Gren +0.10 ± 0.44; Blaziken +0.00 ± 0.28; Hydreigon +0.10 ± 0.20; Lucario +0.30 ± 0.34; Rayquaza +0.78 ± 0.33 (9 cells); Sceptile 0.00 ± 0.00; Suicune +0.13 ± 0.28 (9 cells); Vespiquen −0.10 ± 0.34; Weezing 0.00 ± 0.00. No deck worse. 547 mixed-row games changed. | same, line for line | AGREE |
| 3 | (c) integrity | 0 of the 2,240 i<40 sample games in the 28 zero-footprint cells differ from kog3's. In the 17 run cells, every mixed-row game that differs lies on a deal where the both-sides games differ. | "every mixed-row game ... equals kog3's" | AGREE |
| 4 | (d) seeds and pairing | every game is at 23,003,000,000 + row×10,000 + i, with i < 2,000, in both arms; paired by seed; census list on side a; even i in seat 0; bots kog3/kog3 against kta3/kog3 | same | AGREE |
| 4 | (d) per row | altaria +0.80 ± 0.41, blaziken +0.40 ± 0.27, hydreigon +0.90 ± 0.46, lucario +0.50 ± 0.34, sceptile +0.70 ± 0.54, suicune +1.40 ± 0.57, vespiquen +2.85 ± 0.86, weezing +0.70 ± 0.50. Shares 10/5/11/6/8/17/35/8%, so no row carries more than half. | identical | AGREE |
| 4 | (d) pooled | **+1.031 ± 0.184** (+0.847 to +1.215): PASS. sd 0.094, MDE50 0.18, MDE80 0.26. 862 of 16,000 kta3-arm games differ (198 better, 32 worse). Without Vespiquen it is +0.77. | +1.03 ± 0.18 PASS; 862 | AGREE |
| 5 | Coverage skips (Dustin's condition, deal by deal) | Every group's skip and run sets are identical to those `coverage_skip.txt` names, in both its per-line list and its summary list. The groups: table 21/7, new17 7/10, Scizor 0/8, B2e 84/12, v-lucario_2 6/1, v-suicune_2 7/0, v-weezing_2 6/1, l-charizardy 7/1. Each mixed file holds exactly the pairings that must run, 500 deals each, on the right side. | same | AGREE |
| 5 | B2e held-out own side | Manectric 0.00, Raticate 0.00, Hoopa/Absol 0.00, Garchomp −0.03 ± 0.05, Whimsicott 0.00, Charizard Y Entei 0.00. No held-out veto. 26 own-side mixed games changed (11 held-out, 15 Dustin's). | same | AGREE |
| 5 | Scizor | own side **−0.45 ± 0.65**, 1,007 own-side mixed games changed (1,227 both-sides): no harm. Both sides 31.48 → 31.06. Other direction −0.11 ± 0.28. | same | AGREE |
| 5 | Second lists | v-lucario_2 +0.06 ± 0.08; v-suicune_2 0.00; v-weezing_2 0.00; l-charizardy 0.00: no harm. Averages 55.31→55.43, 52.37→52.37, 56.40→56.34, 40.17→40.15. | same | AGREE |
| 5 | 5.5's count | 21 own-side tests, 17 with a changed game; 1 − 0.975^17 = 0.350 | same | AGREE |
| 6 | Jasmine, deck 07 | kta3 played on 1,738 of 5,544 offered turns = **31.35%**, reaching 20%. The guard: kog3 played on 34 of 8,707 = 0.39%, below 20%. **PASS.** | same | AGREE |
| 6 | A/B, reported | deck 07 +8.12 (+6.22 to +10.03), discordant 259/103, moves differ 83.8%; 05 +2.34; 11 +0.00; 01 +1.04 (+0.05 to +2.03); 03 −0.47 | same | AGREE |
| 7 | Held-out direction | change in miss: Manectric −0.025, Raticate +0.075, Hoopa/Absol −0.050, Garchomp +0.025, Whimsicott −0.025, Charizard Y Entei 0.000. That is **3 closer, 2 further, 1 unchanged, mean +0.00**. Dustin's six: 1 closer, 4 further, 1 unchanged, mean +0.03. | same | AGREE |
| 8 | Integrity line | Every changed game sits where section 2 says switch 1 reaches: the 17 cells; B2e pairings 4, 12, …, 92 (the held decks against Suicune); Scizor's 8 rows; v-lucario_2 row 19; v-weezing_2 row 26; l-charizardy row 44. v-suicune_2 has none. | clean | AGREE |
| 8 | Programs | deckgym 407976…, legality_scan 924751…, tool_census d9799c…, each hashed on the disk now and equal to the registration | equal | AGREE |
| 8 | Inputs and game files | the 75 recorded inputs are all unchanged. The 16 game files that `coverage_skip.txt` and the score45 record name all hash as recorded. | — | AGREE |
| 8 | Identity replays | I re-checked all 7,920 games myself against kt's files, and every one is equal on 15 fields. The A/B tool is 240/240 per arm. | 7,920 equal | AGREE |
| 8 | Timing and scan pages | wall ratio 90.7/79.1 = 1.15 (within 1.25). The 52 legality_scan pages show no finding. | 1.15; 52 pages clean | AGREE |
| 12 | Detectable size as real error (reported only) | 13.55 → **13.38** (MDE50), 13.55 → **13.31** (MDE80) | 13.60 → 13.43, 13.60 → 13.36 | **DISAGREE (reported only)** |

**Item 12, the one disagreement, explained.** The conversion is sqrt(kog3's real error² − δ).
- kog3's real error on the fresh deals is 13.550: score.py's own τ formula, which I recomputed; the page prints it as "13.6".
- The first reader's figures come out exactly if one starts from 13.60. That is the page's rounded value: sqrt(13.60² − 4.5) = 13.43.
- From 13.55 the figures are 13.38 and 13.31. Mine are right; the first reader carried a rounded input.
- It is 0.05 points in a number that gates nothing.
- Also at rounding level: the τ̂ sd is 0.070 from the printed bounds and 0.0715 from the unrounded ones, so "(b) fails half the time near −0.89" is −0.88 at more digits.

**Cross-check, not the instrument.** A delta-method interval on the same games gives ΔMSE −4.25 ± 4.15 (−8.4 to −0.1). Its upper edge also sits right at zero. The label really is on the line, and settling it is the 20,000-rep rerun's job, as 5.4 requires.

## Verdict (registration section 6, RUN5's three outcomes), written from my numbers

- **Identity (item 1): PASS.** The hashes, the 7,920 replays, the timing (1.15) and the 52 finding-free pages all pass. The integrity line is clean.
- **(a): reserve route.** The footprint is 2.35%, under 15%.
- **The ΔMSE label (item 3):** not wholly above zero (the lower edge is −8.98), so outcome 2 is excluded. The upper edge, +0.066, is near zero, so the label is **PENDING between outcome 1 (wholly below) and outcome 3 (spans)**. The 20,000-rep rerun of the same games decides it.
- **(b): PASS.** The τ̂ lower bound is +0.019, well above −1.0. No rule-v2 veto counts, and there is no B2e held-out veto.
- **(c): PASS.** No meta deck's own side is worse beyond paired noise.
- **(d): PASS.** +1.03 ± 0.18, and the whole 95% interval is above zero.
- **Coverage (item 7): PASS.** B2e held-out, Scizor and the four second lists all show no own-side harm.
- **Jasmine (item 8):** it gates only if the label is "spans". It passes: 31.35% against the 20% threshold, with the kog3 guard at 0.39%.
- **So under either open label every gate holds: kta3 is ADOPTED as the working pilot, "unconfirmed".**
  - If the label is "wholly below", accuracy passes, it is reported as "demonstrated on the simulator side; the real side is development data", and Jasmine is reported.
  - If it is "spans", it is the fallback, and all four of its tests pass.
- **What happens next** (5.7, section 4): confirmation is the no-harm re-check at the post-freeze pull, and the lapse clause applies. An engine switch must carry the preset before the screen or the floor use it.
- **The held-out direction, reported beside:** 3 closer, 2 further, 1 unchanged, mean change in miss +0.00.

**For Dustin, in plain words:**
- The fallback's no-harm tests pass because few games changed: 528 of 22,500 on the 45 cells, and 26 own-side coverage games outside Scizor. They say little.
- The informative results are these:
  - Rayquaza's gain, +1.03 ± 0.18. It is not one row: Vespiquen carries 35%, and without it the gain is still +0.77.
  - Jasmine, at 31% against kog3's 0.4%.
  - Deck 07's A/B replicating at +8.1.
- Scizor, the one coverage deck with many changed games, went slightly down (−0.45 ± 0.65). That is within noise, so it is not harm.

**A file I did not produce, observed only.** The 20,000-rep page now on the disk prints the 45-cell ΔMSE as "−8.8 to +0.0 (not below 0)", which would be the "spans" label. That is the other reader's run, not mine, and I read nothing from it into this verdict. Either label gives the same outcome.

## Reconciliation (Sept 29, evening; the reconciler)

**Final verdict: kta3 is ADOPTED as the working pilot, "unconfirmed", through the fallback.** The ΔMSE label is **"spans zero" (inconclusive at this size)**, and the 20,000-rep rerun decided it. The first reader got nothing wrong that gates. The one correction is in a number that is only reported.

**How I worked.**
- I read this report, `OUTCOME_AUDIT.md`, the registration, RUN5's frame and both readings:
  - `READING_numbers.txt` (4,000 reps, 92fc9e0);
  - `READING_numbers_reps20000.txt` (committed at cdd3199, 19:31 CDT, after both reports were written).
- I did not open `read_kta.py`.
- I ran score45.py/score.py unchanged at `--reps 20000` on the second reader's mixed-row composites. Taps recorded the unrounded percentiles and each bot's unrounded real error. The script is `rc_score45.py` and its output `rc_score45_reps20000.txt`, both in this folder.
- My page equals the committed 20,000-rep page on all 157 lines, except the two lines that name temporary input paths.

| Point | Who is right | What the files show | Gates? |
|---|---|---|---|
| Item 12: detectable size as real error (second reader's DISAGREE) | **Second reader** | score.py's own real error for kog3 on the 45 cells is 13.5501 (tapped), printed as "13.6". The first reader converted from 13.60. Corrected at 4,000 reps: 13.55 → 13.38 (MDE50) and 13.31 (MDE80), not 13.43 and 13.36. The same slip is in the 20,000-rep reading: it should be 13.55 → 13.39 and 13.31, not 13.44 and 13.37. | No (reported only) |
| S1: the verdict was recorded before the rerun | **Audit**, on the text (R L243: "The verdict waits for it"; section 6 item 3) | Now settled. The rerun is in (cdd3199). Unrounded 45-cell ΔMSE at 20,000 reps is −8.83 to **+0.031**, so the upper edge is not below zero and the label is **spans**. The lower edge is far from zero (5% of the width is 0.44), so outcome 2 is out. The τ̂ lower bound is +0.020, far from −1.0. The verdict of record is the 20,000-rep reading's. `READING_numbers.txt` L289 is superseded, but its outcome was right. Its 5.8 row "Jasmine PASS (gates)" is correct under "spans". | The label only; the outcome is unchanged |
| S2: the held-out direction is not beside the verdict | **Audit** (RUN5 L554-555) | Both readings print it only in 5a. Beside the verdict it reads: **3 closer, 2 further, 1 unchanged, mean change in miss +0.00** (it gates nothing). | No |
| S3: the Stiffen counter line says "not in yet" | **Audit** (R L175, STATUS L67) | The runner took 4.6's fallback, so no fresh count is coming. The line should read: development-only, kog3 58 of 127 (45.7%), kta3 84 of 152 (55.3%), not run on fresh deals. | No |

**The notes (N1-N8).** None of them gates. I checked N4 myself:
- The 253 B2e games whose both-sides results differ are 117 held-out plus 136 in Dustin's files, all in pairings 4, 12, ..., 92.
- The 26 own-side games are 11 held-out plus 15 in Dustin's files, from the reading's own rows.

N8 is settled by cdd3199: the 4,000-rep page stays in 92fc9e0. At 20,000 reps the 44-cell decision set reads "below" (−9.06 to −0.028). The 45 cells are the registered frame (R L25, RUN5 L520), so that is only a note, as K1 says.

**The verdict (section 6), with the label decided:**
- **Identity:** PASS.
- **(a):** reserve route (footprint 2.35%).
- **ΔMSE:** spans zero, inconclusive at this size (outcome 3), so the fallback applies.
- **(b):** PASS. The τ̂ lower bound is +0.02, and no veto fires, including B2e's held-out veto.
- **(c):** PASS.
- **(d):** PASS, +1.03 ± 0.18.
- **Coverage:** PASS.
- **Jasmine:** PASS, and it gates here: 31.35%, with the kog3 guard at 0.39%.
- **Result: ADOPTED as the working pilot, "unconfirmed".**
- **Held-out direction, beside the verdict:** 3 closer, 2 further, 1 unchanged, mean +0.00.
- **Still to come:** confirmation is the no-harm re-check at the post-freeze pull (5.7), and the lapse clause applies.

**For Dustin:**
- **Nothing to decide for the verdict.** It is the outcome the registration fixed.
- **One optional choice (N1):** the fresh Stiffen count was skipped because the census tool has no `--seed-base` option. You can keep the development-only figure, which is the default, or ask for the tool option later. It gates nothing either way.
- **A heads-up:** score45's own page prints "ADOPTION RULE (v2): do not adopt". That is the ordinary rule's view, which this reading doesn't use (R L237). It is not the verdict.
- **Next, outside this registration:**
  - the commit to the post-freeze list, made before that data is opened (5.7);
  - an engine switch (RUN5's procedure) before the screen or the floor use kta3. It must carry the presets and settle the name clash with the official program's kp-based `kta3`.
