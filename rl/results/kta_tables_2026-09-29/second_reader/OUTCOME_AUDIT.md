**Verdict: the first reading follows the registration. "ADOPTED, unconfirmed" is the outcome section 6 dictates for these numbers, under either label the --reps 20000 rerun can give. No blocker. Three should-fix items (when the verdict is recorded, and two placement or wording fixes). None of them changes the outcome.**

Audited: `rl/results/kta_2026-09-29/REGISTRATION.md` (363b6b7; the top block, then sections 1-7), `rl/RUN5.md` "The frame a candidate is read in" (L519-557), and `READING_numbers.txt` (92fc9e0, --reps 4000), checked against `STATUS.txt`, `footprint.txt`, `coverage_skip.txt`, the score45 page and git. I did not read read_kta.py's logic. I recomputed numbers from the raw game files with my own few lines (section 3). Line numbers are REGISTRATION.md "R L", READING_numbers.txt "RN L", STATUS.txt "S L" and RUN5.md "RUN5 L".

## 1. Findings

### BLOCKER
None.

### SHOULD_FIX

**S1. The verdict is recorded before the rerun the text says it waits for.**
- Text: R L243: "Each is PENDING below `--reps 20000`. ... that run decides the label or the clause. The verdict waits for it." R L314 (section 6 item 3): "A bound near 0 at either edge is PENDING until the 20,000-rep rerun decides".
- Reading: RN L88-89 correctly flags the ΔMSE upper edge as PENDING. It is +0.1, within 5% of the width: 5% of 9.1 is 0.455. RN L289 still records "kta3 is ADOPTED", on the grounds that every gating test holds under both open labels.
- The reasoning is right, so the outcome can't move:
  - The lower edge is −9.0, far from zero, so outcome 2 ("wholly above zero") is out.
  - If the rerun says "below", Jasmine is only reported. If it says "spans", Jasmine gates, and it passes: 31.35% against the 20% threshold, with kog3's guard rate at 0.39%.
  - (b), (c), (d) and coverage pass either way.
- But the text says to wait, and the recorded label still decides what the page must say:
  - Under "below": "demonstrated on the simulator side; the real side is development data" (R L138, L238), with Jasmine reported and gating nothing.
  - Under "spans": "inconclusive at this size", with Jasmine as one of the tests that carried the verdict.
- Fix: word RN L289 as "adopted under either open label; recorded when the --reps 20000 rerun is in", or let the rerun's page be the record. Then set the label sentence and the 5.8 row "Jasmine on deck 07 PASS (gates)" (RN L273) to match the label.

**S2. The held-out direction is not printed beside the verdict.**
- Text: RUN5 L554-555, Dustin: "Report the held-out direction beside every verdict"; "Every verdict prints how B2e's held-out archetypes (pairings 0-47) moved". R L268 says the same.
- Reading: the direction is printed in section 5a (RN L155-162: 3 closer, 2 further, 1 unchanged, mean change in miss +0.00). The verdict block (RN L276-292) puts only deck 07's A/B beside the verdict.
- Fix: add one line after RN L292: "Held-out direction (gates nothing): 3 closer, 2 further, 1 unchanged, mean change in miss +0.00."

**S3. The Stiffen counter line says "not in yet". The text and STATUS say "development-only".**
- Text: R L175 (4.6): without the tool change, "Stiffen's counter stays on the development deals (kog3 58 of 127 offered turns, kta3 84 of 152) and is labelled development-only. It gates nothing either way."
- STATUS S L67 took that route and says so.
- Reading: RN L205-206 prints "not in yet (reported only; holds nothing)". That reads as a pending input, but none is coming.
- Fix: print the development figures, labelled "development-only (4.6); not run on fresh deals". See N1 for how the route was chosen.

### NOTE

**N1. The counter fallback was taken by default, not on Dustin's word.**
- 4.6's fallback applies "If Dustin doesn't want the tool change" (R L175).
- His approval covers "Everything else as drafted" (R L15). Section 10 i lists the `--seed-base` option among the proposed items (R L404), and section 8 row 8 depends on it (R L362).
- S L67 gives the reason as "no --seed-base tool was supplied (KTA_CENSUS unset)".
- Skipping it keeps section 4's "no new build", and the counters gate nothing, so the verdict doesn't change. The Stiffen prediction (R L260) is left unread on fresh deals. Tell Dustin in one line.

**N2. K7 reads the lower edge the lenient way. Nothing depends on it here.**
- K7 (RN L48-50) reads the upper edge from score45's unrounded "below 0", which is the strict way.
- It reads the lower edge "only as printed: '+0.0' is not called". A lower bound printed +0.0 can be a positive number, which is RUN5's outcome 2 (fail, no fallback).
- N9's own pattern for a bound printed right at its line (τ̂ printed −1.00) is to read it at more digits.
- The lower edge here is −9.0. Fix it before km's reading reuses the code.

**N3. K13 gates only two of the three program hashes.**
- K13 (RN L73-74) gates deckgym and legality_scan and only reports tool_census. Section 4 check 1 (R L165) names all three.
- tool_census matched at every check (RN L15; S L2, L93) and played no game here. Nothing depends on it.

**N4. Two rows of the 5.8 table overstate or blur.**
- The B2e held-out row (RN L269) includes Dustin's files in its counts. I recomputed the split:
  - 253 both-sides games = 117 held-out + 136 in Dustin's files;
  - 26 own-side mixed-row games = 11 held-out + 15 in Dustin's files.
- R L252 asks for the games "behind" each no-harm test. Behind the held-out test are 117 and 11.
- "Jasmine on deck 07 PASS (gates)" (RN L273) is only true if the label is "spans" (S1).

**N5. "Replicates" is stronger than the number shows.** RN L86 says kog3's fresh real error "replicates the development 14.0". The text calls this print "a free replication" (R L244), but the fresh figure is 13.6, and no interval is printed. Better: "13.6 on fresh deals (development 14.0)".

**N6. The verdict block is not self-contained.**
- The verdict line (RN L289) doesn't name (e) "for the screen and the table together" (R L320, section 6 item 9).
- The PASS list (RN L278-287) doesn't restate item 1's identity, timing and hash checks. They are in 1b (RN L12-27) and all passed.
- One phrase each would fix it.

**N7. Warn Dustin about score45's "do not adopt" line.** The score45 page (`score45_kta3_vs_kog3.txt` L20) now prints "ADOPTION RULE (v2): do not adopt (dMSE interval not below 0)", the opposite of the development page's "adopt". Both are the ordinary rule's view and are not read here (R L237). The reading correctly keeps the line out (RN L92). Warn him before he sees "do not adopt" next to an ADOPTED reading, as kt's audit did for the other direction.

**N8. Keep the 4000-rep page traceable.** The page the first reading read is committed at 92fc9e0 (sha256 b53e3b62..., and its `.reps` sidecar says 4000). The on-disk copy was still that file when checked. The 20,000-rep rerun should write its own page, or be committed separately, so RN L85-95 keeps its source.

## 2. Clause by clause

**Top block (governs)**

| Item | Text | Reading / record | |
|---|---|---|---|
| 1 (d) | 8 rows × 2,000, both arms, kog3 on the panel, seeds 23,003,000,000 + row × 10,000 + i, read once (R L8) | RN L109-121. Recomputed: 16,000 pairs, seeds and seats 0 mismatches, max i 1,999, bots kta3/kog3 v kog3 | OK |
| 2 Jasmine | ≥ 20%, gates only when ΔMSE spans zero; kog3 guard (R L9-10) | K10, K11; RN L203, L285 | OK |
| 3 Coverage shortcut | skip only if every deal matches on moves, both decks, seed, seats; a committed script names each skip (R L11-14) | coverage_skip.txt (committed with the runs in 92fc9e0) compares moves, a, b, a_file, b_file, seed, first_seat, and says winner_seat is not a criterion. It names every skip. K9 re-checks it. | OK |
| 4 As drafted | reserve route, three outcomes, near-zero rule on both edges, 3.1 and 3.2, ec7e1a8 as-is, A/B reported (R L15-20) | RN L7, L88-89, 1b, L191-204 | OK (timing of the verdict: S1) |
| 5 Order | runner and blind reading script committed before any fresh game (R L21) | 5f4657b at 12:55:25 CDT. First game at 17:59:08Z = 12:59:08 CDT (S L1). read_kta.py has no later commit and no working-tree change. | OK |

**Section 2 (reach).** Every changed game sits where R L87-88 says switch 1 reaches, all recomputed:
- the 17 cells;
- B2e pairings 4, 12, ..., 92 (the Suicune pairings);
- the second lists' rows v-lucario_2 19, v-weezing_2 26 and l-charizardy 44;
- all 8 Scizor rows (its own Barrier).

v-suicune_2 changed no game, as expected. The integrity line is clean (RN L10, L287).

**Section 3.2 (fresh seeds).** Recomputed, with 0 mismatches on seed and seat rule (even i puts the first-named deck in seat 0):
- the 45 cells at 23,000,000,000 and 23,001,000,000 + pairing × 10,000 + i (45,000 games);
- B2e at 23,002,000,000 + ... (96,000 games);
- the Scizor mixed rows: every game on its kog3 baseline's seed (4,000 of 4,000), with the first at 23,001,000,000.

Also as registered:
- The A/B's first seed is 23,004,070,000, which is deck 07, opponent 0, i 0.
- The traces start at 23,005,000,000 and 23,005,001,000 (S L63-66).

**Section 4 (build and identity).**
- Hashes were checked before the first game (S L2), before each phase (S L29, L36, L46, L49, L62, L68) and after the last game (S L93), and restated in the reading (RN L13-15).
- Identity: 20 replays, 7,920 games, all equal on every listed field (S L25). That is 7,440 games for check 2 plus 480 for check 3, as R L171-172 say.
- Timing: 1.15 against the 1.25 limit, with CPU recorded beside (S L28).
- Scan pages: 52 legality_scan pages, 0 findings (recomputed).
- Check 6 (counters): see S3 and N1.

**5.1 (footprint first).**
- 528 of 22,500 games differ = 2.35% (recomputed), in 17 cells, so the reserve route.
- It was committed alone at 2c035d2: footprint.txt only, at 14:13:20 CDT, 54 s after the runner wrote it (S L35).
- That is before the reading and the rest at 92fc9e0 (19:22:46 CDT).

**5.2 (reserve route).**
- **Three outcomes:** the label (RN L88) and K11 match R L199-204.
- **(b):** the τ̂ lower bound is +0.02, far from −1.0 at the 0.10 margin, and no veto counts (score45 L18-19; RN L278-279).
- **(c):** the 17 cells were run in both directions at 500 deals. The other 28 got the i < 40 sample of both directions: 2,240 games, and I found 0 that differ from kog3's (recomputed).
  - The pooled per-deck interval uses the variation check (N10). Checked by hand for Rayquaza: +0.78 ± 0.33 from score45 L131-138.
  - All 10 meta decks are gated, including the two new ones, which is the stricter reading.
- **(d):** recomputed, +1.031 ± 0.184. It passes and gates on this route, as R L216 requires.
- **5.9:** the row shares are printed. Vespiquen's is 35%, under half, so no sentence beside the verdict is owed.

**5.4 (accuracy).** Printed:
- ΔMSE with the by-event interval beside;
- the label;
- the interval's sd (2.3), and MDE50 and MDE80 each also as real error;
- the τ̂ sd (0.070), with −0.89 as the smallest harm the bound can see;
- development figures for scale;
- kog3's real error beside (N5).

The score45 adoption line is not read. The near-zero rule: the upper edge is PENDING, correctly; the lower edge and τ̂ are clear. When to record the verdict: S1.

**5.5 (coverage and footprint).**
- B2e: 12 pairings run, 84 skipped; no held-out veto. K3 and K4 treat own-side harm alone as a veto, the stricter reading.
- Scizor: −0.45 ± 0.65, no harm (recomputed). The four second lists: no harm.
- The test count: 21 own-side tests, 17 of them with a changed game, and 1 − 0.975^17 = 0.350 (checked).
- The Jasmine line and its guard: recomputed, 1,738 of 5,544 and 34 of 8,707.
- Reported:
  - Barrier on a qualifying holder, 81% under both codes (the prediction held);
  - Apron and Helmet;
  - both traces, with the first-divergence tally;
  - Suicune (7a), Rayquaza's real cells (7b) and Hydreigon's gap (7c).
- The held-out direction: S2. Stiffen: S3.

**5.6 (A/B).**
- Deck 07: +8.1 (+6.2 to +10.0), discordant games 259/103, moves differ in 83.8% (all recomputed).
- The gate file was named (S L50), and the A/B ran after "KTA PART A DONE" (S L30).
- It is reported, not gated (RN L292).

**5.7 and 5.8.** Confirmation, the lapse clause and the post-freeze list are at RN L290-291 and L300-301. The 5.8 table is at RN L264-274 (see N4).

**Section 6.**
- Items 2-8 hold on the printed numbers (RN L277-287).
- Item 1 holds from 1b (RN L12-27).
- Item 3 is "not wholly above zero", which is decided by the lower edge (−9.0), not the near-zero upper edge.
- Item 8 passes whether or not it gates.
- Item 9, (e), is not named (N6).
- So "Adopted (as the working pilot, 'unconfirmed')" is the line section 6 dictates. Only when it is recorded departs from 5.4 (S1).

**Section 7.**

| Item | Result |
|---|---|
| 1 | 2.35% against the predicted 2.5% |
| 2 | no changed game outside switch 1's reach |
| 3 | (d) passes |
| 4 | Jasmine reaches 20%; the guard is low |
| 5 | no harm; n = 17 and the chance are printed |
| 6 | not wholly above zero |
| 7 | deck 07 replicated |
| 8 | no Dustin deck hurt beyond noise (deck 03: −0.5, −2.0 to +1.0) |
| 9 | Barrier unchanged; Stiffen unread (S3) |
| 10 | stated, RN L302 |

**Order of the run (section 8).** STATUS follows the registered order: identity, then timing, the 45 cells, the footprint, the mixed rows, (d), the A/B, the traces, the counters (the fallback), Scizor, the second lists, B2e and B2e's mixed rows.

**K1-K14.** Where the text allows two readings, each K note codes the stricter one:
- K3/K4: harm alone is a veto.
- K8: "within" is inclusive, in whole printed units.
- K10: never offered counts as not passed.
- K11: τ̂ and (c) gate on the ordinary route's outcome 1 too.
- K12: integrity lines hold every verdict, NOT ADOPTED included.

K5, K6 and K9 match the text and Dustin's words. The two exceptions are K7's lower edge (N2) and K13's third hash (N3), both moot here. N7, N8, N10 and N12 are not restated as K notes, but they stand as registered (R L186), and the reading follows them.

**Reported but not registered.** All of these gate nothing:
- the 113 games whose result changed (RN L6);
- Scizor's other direction (RN L177; its games are registered in section 8 row 9);
- the census list's Limitless figure beside each (d) row.

**Registered but dropped.** Only the fresh Stiffen counter (S3, N1).

## 3. Spot checks (my own lines, on the raw files)

| Number | Reading | Recomputed |
|---|---|---|
| Footprint (moves, paired by a, b, i) | 528 of 22,500 = 2.35%, 17 cells | 528 of 22,500 = 2.3467%, 17 cells |
| (d) pooled, and Vespiquen's row | +1.03 ± 0.18; +2.85 ± 0.86; 862 differ | +1.0312 ± 0.1842; +2.850 ± 0.862; 862 differ |
| Jasmine, deck 07 | kta3 1,738 of 5,544 (31.35%); kog3 34 of 8,707 (0.39%) | the same |
| Deck 07 A/B | +8.1 (+6.2 to +10.0); 259/103; 83.8% | +8.12 (+6.22 to +10.03); 259/103; 1,608 (83.8%) |
| Scizor own side | −0.45 ± 0.65; 1,007 changed | −0.450 ± 0.651; 1,007 |
| B2e both sides | 253, in 12 pairings | 253, in pairings 4, 12, ..., 92 |
| Integrity sample, 28 zero-footprint cells | none differ | 0 of 2,240 |

The scripts and their output are in the session scratch folder, `wf_kta2/outcome-audit/` (`spot.py`, `spot2.py`, `spot_out.txt`, `spot2_out.txt`). No game was played, and nothing in the repo was changed except this file.
