**Verdict: the first reading follows the registration as amended. "km3 ADOPTED, 'unconfirmed'" is the outcome section 6 dictates for these numbers: the reserve route, a ΔMSE interval that spans zero, and every fallback test passing. Clause (d)'s narrow pass holds under the registered statistic: the lower edge is +0.0264, checked with exact arithmetic, and no registered rule reopens it. No blocker. Two should-fix items, both about what the record prints; neither changes the outcome.**

**What I audited:**
- `R` = `rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md` at e308a65: the top block, sections 1-7, Amendment 1 and Amendment 2.
- `RUN5` = `rl/RUN5.md`, "The frame a candidate is read in" (L532-570).
- `RN` = `rl/results/km_tables_2026-09-30/READING_numbers.txt` at 18bd89c, --reps 4000.

**What I checked it against:**
- `S` = `rl/results/km_tables_2026-09-30/STATUS.txt`;
- `footprint.txt`, `coverage_skip.txt`, `score45_km3_vs_kta3.txt` and `thresholds.json`;
- `km_run/run_km.sh`, for what STATUS does not log;
- git.

I did not read read_km.py. I recomputed numbers from the raw game files with my own few lines (section 4). References are file:line, using the short names above.

## 1. Findings

### BLOCKER
None.

### SHOULD_FIX

**S1. The held-out direction is not printed beside the verdict.**
- **What the text says:**
  - RUN5:567: "Report the held-out direction beside every verdict".
  - RUN5:568: "Every verdict prints how B2e's held-out archetypes (pairings 0-47) moved".
  - R:584 (step 5b item 4) says the same.
- **What the reading does:** it prints the direction only in section 5a (RN:180-187: 2 closer, 3 further, 1 unchanged, mean change in miss −0.02). The verdict block (RN:282-299) puts only (d)'s row share beside the verdict (RN:299).
- **This happened before.** kta's audit found the same thing as its S2 (`kta_tables_2026-09-29/second_reader/OUTCOME_AUDIT.md:24-27`), and the reader was not changed.
- **Fix:** add one line after RN:299: "Held-out direction (gates nothing): 2 closer, 3 further, 1 unchanged, mean change in miss −0.02." I recomputed it from RN:181-186 and it agrees.

**S2. Clause (d) is printed to two decimals, but whether it passes depends on the third.**
- **What the reading prints:** "+0.44 +/- 0.42" (RN:143, RN:287), with no lower edge. A reader subtracts and gets +0.02. From the page alone, they can't tell a real pass from a rounding accident.
- **What the text says:**
  - Comparisons use the unrounded value, and rounding is for display only (R:13, R:512).
  - A bound printed right at its line "is read at more digits" (R:532, written for τ̂).
- **Recomputed with exact fractions** (section 2):
  - mean 4/9 = +0.4444, half-width 0.4181;
  - 95% interval +0.0264 to +0.8625;
  - the exact test 81·M² > 3.8416·Σvar holds: 16 > 14.16.
- **So the pass is real.** Only the record is thin.
- **Fix:** print "+0.4444 ± 0.4181 (95% interval +0.026 to +0.862)" at RN:143 and RN:287.

### NOTE

**N1. (d)'s gain comes from two rows** (reported only; nothing registered turns on it).
- Lucario v Suicune gives +2.65 (RN:138) and Lucario v Weezing +2.35 (RN:140). The other seven rows add up to −1.0.
- If either of those two rows is left out, the pooled interval spans zero (my lines: +0.169 ± 0.420, and +0.206 ± 0.419).
- The reading names only the Suicune row ("more than half", RN:145, RN:299). Step 5b item 3 makes the per-row numbers a column, not a rule (R:583), so the gate is unchanged.
- These are the same two cells where km3's Arena rate jumps most: table:19 33.9% → 64.0%, and table:21 42.3% → 79.8% (RN:218). That is consistent with N2 being the cause.
- One line in the write-up would help.

**N2. M2's stage prediction did not show up.**
- **The prediction:** Training Area "should not rise where [the opponent's attackers] are [Stage 1]" (R:503).
- **What happened:** the four control cells rose by +5.9 points (26.6% → 32.5%). The five gating cells rose by +5.3. The contrast interval is −3.2 to +1.1 (RN:222).
- M2 still passes as registered, because the threshold is on the five cells (R:504). The contrast is reported only (R:505).
- This is worth one sentence as a prediction that failed, not as a gate.

**N3. K7 still reads the ΔMSE lower edge the lenient way.** Nothing depends on it here.
- K7 (RN:68) reads the lower edge "only as printed ('+0.0' is not called)". A bound printed as +0.0 can be positive, and a positive lower edge is outcome 2: fail, no fallback (R:537, R:531).
- kta's audit flagged this as N2 and asked for the fix "before km's reading reuses the code". It was not fixed.
- The lower edge here is −7.0, so the result is unaffected. Fix it before the next reading.

**N4. K4 gives (c) no gate on the ordinary route.** Nothing depends on it here.
- R:602 (section 6 item 3) counts harm through "route (c) or the vetoes". kta's reader gated (c) on the ordinary route's outcome 1, which is the stricter reading.
- km took the reserve route, so this does not apply.

**N5. The near-zero check is not printed.**
- The rule is K8 (RN:70-72; R:529-533).
- The result isn't shown anywhere. Both ΔMSE edges (−7.0 and +10.1) are far outside 5% of the width (0.86), and τ̂'s −0.26 is 0.74 above −1.0. So nothing is PENDING and --reps 4000 decides.
- One line at RN:112 would show it was checked.

**N6. STATUS logs the pin checks only once, in part B** (S:7-8).
- run_km.sh does check the pins at every point the text asks for (R:200, R:211):
  - after the build and at the start of part I, T and R;
  - after the identity games, after the timing pair and after part T;
  - before the mixed rows, before (d) and before coverage;
  - after the last game.
- These are run_km.sh:520, 545, 641, 661, 742, 765, 807, 858, 873, 885 and 914.
- **Why STATUS doesn't show it:** check_pins stops the run on a mismatch and writes nothing when the pins match (run_km.sh:271-281). Each DONE line comes only after the part's last check (run_km.sh:914-917), so the DONE lines at S:33, S:50 and S:97 imply the checks passed.
- RN:17-19 also restates the three hashes on disk at reading time. kta's STATUS wrote a line at each check; km's could too.

**N7. The go-ahead for the tables was given in advance. Dustin should confirm it.**
- R:37 says "Registered tables still require my separate go-ahead." The one recorded is "The cloud has the message go ahead on the tables" (S:53; GO_km_tables; RUN5 at c74d8df).
- It came at about 02:20 UTC. That was seven hours before the preparation passed, and part R started at 09:31:44 UTC.
- The laptop wrote down its reading before any km game ("they start once the preparation has passed, in Amendment 1 (g)'s order", c74d8df). His second message ends "then you authorize the tables" (R:49).
- The order was kept (section 5). Whether he meant an advance go-ahead is his to confirm, in one line.

**N8. Section 8's B2e held-out row also counts Dustin's files.** kta's audit made the same point as its N4.
- RN:274 gives 5,761 both-sides games and 2,710 own-side mixed-row games, over pairings 0-95.
- Behind the held-out test (0-47) there are 3,183 and 1,637 (recomputed). Dustin's files account for 2,578 and 1,073.

**N9. Warn Dustin about score45's "do not adopt" line.**
- The page prints "ADOPTION RULE (v2): do not adopt (dMSE interval not below 0)" (`score45_km3_vs_kta3.txt`:21, :45). That is the ordinary rule's own line.
- The reading is right to ignore it: the reserve route with a spanning interval goes to the fallback (R:552). But he will see "do not adopt" next to ADOPTED.

**N10. Small things that change nothing:**
- **Identity count units.** RN:22-39 counts "4,664 games, rows and files": its lines 7-8 count 2 compared files each. The registered total is 5,240 games (R:209), and all of them were played (S:17-31).
- **Two figures for Lucario's miss.** RN:242 gives it as 6.5 → 6.3, and RN:261 gives the gap as 6.6 → 6.3, for the same nine cells. One is rounded before subtracting, the other after.
- **Wrong citation.** coverage_skip.txt:4 cites kta's "REGISTRATION.md top block, item 3". km's is R:21 (block item 7). The sentence is the same.
- **Beside intervals with no seed.** M1's and M2's paired-change intervals use "2000 replicates" (RN:217, RN:220) and name no seed. The text asks for an interval but fixes no method, and it is reported only.
- **(d) rows 7-8 use a different deck file.** They play `decks/screen/opponents/t-lucario.txt` (d_lucario_block.tsv:9-10), not R:558's `decks/research/lucario.txt`. The two files are the same 20 cards; t-lucario.txt only adds card names. That is also the list new_decks.tsv gives those cells.
- **Sentinels.** RN:224-226 say "expected unchanged within paired noise" but print no interval, so the expectation is not actually tested. They are reported only (R:525).
- **(c) is pooled over the changed cells only.** RN:121-130 pool each deck over its cells with a changed game, so the numbers look bigger than score45's by-deck line (page:151-159). The gate is the same either way: a zero-footprint cell adds zero mean and zero variance, and the mean and the half-width both scale by 1/K.
- **The verdict block doesn't restate section 6 item 1** (the pin, and the cloud's tests). GO_km_build:2 has it: 53fc5a1, tests 1,991/0.

## 2. Clause (d): does anything in the registration apply to a lower edge this close to zero?

No. Each part of the question, against the text:

- **The statistic** (R:561; read_koh.py's `paired()`, whose lines 109-118 I read):
  - The score is Lucario's own-side score from `first_deck_score`, whichever seat Lucario is in, with draws counted as that field counts them.
  - Each row is 2,000 deals: 500 table deals plus 1,500 block deals (R:560).
  - The pooled figure is the equal-weight mean of the nine per-row mean differences.
  - The half-width is 1.96·√(Σ per-row variance of the mean)/9, with the (n−1) sample variance.
- **My recomputation, as exact fractions:**
  - every row equals RN:134-142 to the printed digit;
  - mean exactly 4/9 = +0.4444, half-width 0.41805, sd 0.21329;
  - 95% interval +0.0264 to +0.8625;
  - z = 2.08 against 1.96.
  - Using the population variance instead of (n−1) changes nothing: the lower edge is +0.0265.
- **Rounding:** the "+0.02" is the printed figures subtracted. The exact comparison of M against 1.96·√Σvar/9 passes (81·M² = 16 > 3.8416·Σvar = 14.16). The pass does not come from rounding (S2).
- **The near-line rule does not cover (d):**
  - It is registered for the two ΔMSE edges and the τ̂ edge only (block item 8, R:24; step 4, R:529-533).
  - Its stated reason is bootstrap Monte-Carlo error ("score45's bounds are bootstrap percentiles with Monte-Carlo error", R:529). (d)'s interval is a formula, not a bootstrap, so the same games always give the same interval.
  - So there is no PENDING state and no 20,000-rep rerun for (d).
- **"Read once":** R:23, R:528 and R:563 say "No doubling, no rerun, and no block beyond D2's". The pass stands and can't be reopened, just as a fail couldn't have been rescued. The reading did not rerun (S:71-77: one run of each file).
- **The pass test is "the whole interval is above zero"** (R:563). +0.0264 > 0.
- **How thin the margin is** (for the record; no rule reads it):
  - A single km3-arm game changing from a win to a loss lowers the pooled mean by 100/(2,000·9) = 0.0056 points.
  - So about 5 such games, with the variance held fixed, would put the lower edge at zero.
  - The registration's model predicted a half-width of 0.4 to 0.8 at this size (R:564). The observed 0.418 is at the tight end, and the observed gain (0.444) is just above MDE50 (0.42).
- **The games themselves check out:**
  - (d)'s kta3 arm on deals 0-499 replays kta3's references, 4,500 of 4,500 (moves, decks, seed, seat).
  - (d)'s km3 arm on those deals is game for game the same as (c)'s mixed rows, played separately, 4,500 of 4,500 (moves, decisions, result, seed, seat, bots).
  - The seat rule holds on all 18,000 pairs, and the bots are right on every game.
- **Section 6 then reads:** (d) passes, so no override is needed (R:603, R:623).

## 3. Clause by clause

**Top block, Amendment 1 and Amendment 2**

| Item | Text | Reading / record | |
|---|---|---|---|
| Block 1: exact midpoint, rounding for display, frozen bootstrap | R:13-15 | T1 = (355/1664 + 37/109)/2 = 100263/362752 and T2 = (127/435 + 275/786)/2 = 24383/75980, both recomputed; compared as Fractions (RN:216, RN:219) | OK |
| Block 2: deals 200-299 set T, deals 0-199 test | R:16 | Sample i 200-299 and counters i 0-199, recomputed | OK |
| Block 3-5: record, independent check, amendment, "cannot pass" final | R:17-19 | 1fc9e0b < 80d77cf < e308a65 (section 5); Amendment 2 writes neither line as "cannot pass" (R:255) | OK |
| Block 7: coverage shortcut | R:21 | coverage_skip.txt compares moves, a, b, a_file, b_file, seed and first_seat, and says winner_seat is not a criterion. It names every skip. K9 re-checks it. | OK |
| Block 8: N2 alone, (d) as drafted, guard, three outcomes, near-zero rule, closure | R:23-26 | RN:132-145, RN:216, RN:219, RN:112, K8, RN:266 | OK (N5) |
| A1 (b) 2: km3 against kta3 everywhere | R:67-78 | Every group is paired against item 3's kta3 files (coverage_skip.txt:7-8 and following; score45 page:3); the counters' kta3 arm is checked against the references (S:63) | OK |
| A1 (b) 3-4: one set of files, the one list | R:79-92 | Written before part I's first game (S:14) and checked (S:15); RN:2 checks it again before reading | OK |
| A1 (e): laptop's own identity at B | R:196-211 | 15 checks, every one PASS (S:32); committed before the timing pair (fcb3901; S:37) | OK (N10 units) |
| A1 (g): order | R:223-227 | See section 5 | OK (N7) |
| A2: T1, T2 | R:241-259 | Match thresholds.json and RN:43-44, and my recomputation | OK |

**Section 5, the reading**
- **Step 1, footprint first and committed alone.**
  - 3,117 of 22,500 = 13.8533% (recomputed), in 17 cells. The integer test 311,700 < 337,500 gives the reserve route.
  - footprint.txt was committed alone at dac7dcf (one file, 09:55:06 UTC), 70 s after the runner wrote it (S:60), and before 18bd89c.
- **Step 3, the mechanism.**
  - M1: 918 of 2,574 ≥ T1, with the guard kta3 at 734 of 3,279 < T1. M2: 533 of 1,579 ≥ T2, with the guard at 498 of 1,748 < T2. All recomputed.
  - They gate only because the interval spans zero (R:552; RUN5:560).
  - Everything the text asks for beside is printed: kta3's rate, the paired change, the cells where it rises, the last four cells and the contrast (RN:217-222), M3, the sentinels and the Hiking Trail column (RN:223-227).
  - See N2 and N10.
- **Step 4, the 45 cells.** Printed:
  - ΔMSE km3 minus kta3 (+1.1, −7.0 to +10.1), with the by-event interval and the 44-cell set beside;
  - the sd, MDE50 and MDE80, each also as real error (checked: √(13.80² − 8.6) = 13.49);
  - the expected sign;
  - the label SPANS.
  - **(b):** τ̂ −0.04 (−0.26 to +0.18). −0.26 ≥ −1.0, and no veto counts. The one veto candidate, Altaria v Suicune (+6.2), has neither side worse (recomputed: −0.600 ± 1.797 and +5.000 ± 2.140).
  - **(c):** 10 decks over the 17 changed cells, no deck worse (all recomputed; the lowest upper edge is Sceptile's +0.096).
  - **(d):** section 2.
  - **Closure sentence:** RN:266.
- **Step 5, coverage.**
  - **Mixed rows:** they ran on every pairing that differs, and B2e's garchomp v lucario (24) was skipped only because all 500 deals were equal, which is what the rule allows.
  - **Harm:** no own-side harm on B2e, Scizor (−0.225 ± 0.417, recomputed) or the second lists, and no held-out deck more than 2 points further.
  - **The test count:** 21 tests, 1 − 0.975^21 = 0.412 (checked).
  - **Held-out direction:** it is printed (RN:180-187), but not beside the verdict (S1).
- **Step 5b:** item 1 at RN:113 and RN:144; item 2 at RN:268-280; item 3 at RN:133-145; item 4 is S1.
- **Steps 6-7:** RN:297-298 and RN:309-311. The lapse clause is read as A1 (b) 5 restates it (R:111).

**Section 6 ("Outcomes fixed now", R:614-623).**
- The route is reserve and the interval spans zero.
- (b), (c), step 5, (d), M1 and M2 all pass.
- So the outcome is "km adopted, 'unconfirmed'" (R:617), in the tables with kta3 replaced. The screen and the floor wait for the engine switch (A1 (g), R:228).
- RN:296 says exactly this. Items 2-5 of section 6 (R:601-604) do not fire.

**RUN5's frame.** Each point matches the reading:
- read on the registered 45 cells (RUN5:533);
- coverage rows count for no harm only, with mixed rows every time (RUN5:534-538);
- three accuracy outcomes, with the fallback only on a spanning interval (RUN5:550-559; K4);
- footprint thresholds gate only in the fallback and were written in before the games (RUN5:560; Amendment 2 at e308a65, before part R);
- (d) required on both routes (RUN5:561; K4);
- held-out direction beside the verdict: not done (S1).

**K1-K14, and whether each takes the stricter reading where the text allows two:**
- **K1, K2, K3:** match R:534 and R:486. K3 uses exact integers.
- **K4:** matches R:550-554 on the reserve route. On the ordinary route it is lenient about (c) (N4; moot).
- **K5:** matches R:557. Pooling over only the changed cells doesn't change any gate (N10).
- **K6:** matches R:559-563, recomputed exactly.
- **K7:** strict on the upper edge, lenient on the lower (N3; moot).
- **K8:** "within" is inclusive, the stricter reading.
- **K9:** matches R:21, and codes the doubtful cases as PENDING.
- **K10:** matches R:506 and R:511-512. "Never offered" counts as not passed, the stricter reading.
- **K11:** matches R:497.
- **K12:** integrity lines hold the verdict.
- **K13:** gates all three programs. This fixes kta's audit N3.
- **K14:** matches R:577.

**Reported but not registered** (all gate nothing):
- the 615 changed results (RN:9);
- (d)'s row shares and the "more than half" sentence (RN:133-145, RN:299);
- M2's "rises in 4 of 5" (RN:220);
- the beside intervals at 2,000 replicates (RN:217, RN:220).

**Registered but missing:**
- the held-out direction beside the verdict (S1);
- the near-zero check's result (N5);
- the sentinels' "within paired noise" (N10).

## 4. Spot checks (my own lines, on the raw files)

| Number | Reading | Recomputed |
|---|---|---|
| Footprint (moves, paired by a, b, i) | 3,117 of 22,500 = 13.85%, 17 cells; 615 results changed (RN:6-12) | 3,117 = 13.8533%, 17 cells, 615; seeds and seats 0 mismatches |
| (d) pooled | +0.44 ± 0.42; 7,046 of 18,000 differ (RN:133, RN:143) | +0.4444 ± 0.4181, interval +0.0264 to +0.8625; 7,046; every row equal to RN:134-142 |
| M1, deals 0-199 | km3 918 of 2,574; kta3 734 of 3,279 (RN:216) | the same; km3 ≥ T1, kta3 < T1 (Fraction) |
| M2, deals 0-199 | km3 533 of 1,579; kta3 498 of 1,748 (RN:219) | the same; km3 ≥ T2, kta3 < T2 |
| Sample, deals 200-299 | M1 355/1,664 and 444/1,308; M2 254/870 and 275/786 (R:244-251) | the same; T1 and T2 are their exact midpoints |
| Scizor own side | −0.23 ± 0.42 (RN:200) | −0.225 ± 0.417, 8 rows |
| (c), 10 decks | RN:121-130 | all ten equal; none wholly below zero |
| Veto cell, Altaria v Suicune | −0.6 ± 1.8 and +5.0 ± 2.1 (page:20) | −0.600 ± 1.797 and +5.000 ± 2.140 |
| B2e both sides | 5,761 in 40 pairings (RN:152) | 5,761 in 40 (held-out 3,183, Dustin's 2,578) |

## 5. The run's record (STATUS and git)

- **Part B** (S:1-8):
  - B's diff touches players/ only, with UPSTREAM.md exempt (S:2);
  - the tool's source is 05d7ba41 (S:3);
  - 41 of 41 pairs and deck files are B's (S:5);
  - pins recorded (S:7-8).
- **Part I** (S:9-34):
  - GO_km_build is in place (S:10). It quotes Dustin's approval of the preparation and says the cloud's round at B passed (53fc5a1) and the tier-1 read is done. TIER1_READ_B.md:3 says it was "Read before the laptop built B".
  - The one list is written and checked (S:14-15).
  - All 15 identity checks pass (S:32), then a stop (S:34).
  - Committed at fcb3901 (09:21:35 UTC), before part T.
- **Part T** (S:35-51):
  - Part I is committed and unchanged (S:37).
  - Timing is 1.062, under the 1.25 limit (S:42).
  - km_thresholds.py's sha256 and the Python version are recorded (S:44). The file itself was committed at a14014e, with the runner and read_km.py, before any game.
  - The sample's kta3 arm equals the references (S:46), and the thresholds are written (S:49).
- **The three threshold commits,** confirmed in order with `git log --ancestry-path`:
  - 1fc9e0b at 09:24:57 UTC;
  - 80d77cf at 09:30:48 UTC;
  - e308a65 at 09:31:20 UTC.
  - The runner checked the same order itself (S:54).
- **Part R** (S:52-97):
  - GO_km_tables is in place (S:53; N7).
  - The references are unchanged (S:55), and (d)'s block is written (S:56).
  - km3 was played on the 45 cells, then the footprint was written (S:58-60). It was committed alone at dac7dcf (09:55:06 UTC).
  - After that the runner played the counters (both arms checked, S:63 and S:65), the mixed rows, (d), and coverage in the registered order.
  - DONE at 12:14:36 UTC; the reading was committed at 18bd89c (12:17:13 UTC).
- **Pins:** checked everywhere the text asks, but STATUS logs only the first check (N6).
- **read_km.py** was committed at a14014e and has not changed since (git log; the working tree is clean for km_run/). Its commit message records the review.

My scripts and their output are in the session scratch folder `wf_km2r/outcome-audit/` (`spot.py`, `spot2.py`, `git.sh`, `spot_out.txt`, `spot2_out.txt`). I played no game, and the only change to the repo is this file.
