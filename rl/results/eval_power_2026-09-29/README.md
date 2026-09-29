# How much improvement can the 45-cell scoreboard detect? (Sept 29, read-only)

**Why:** Dustin asked (Sept 28, about 11:50 pm Central) whether an article on eval design and hill-climbing could improve the workflow. Its first lesson: an eval has to be quiet enough to detect the improvements you're chasing. This checks that for scoreboard v3's 45 cells.

**How:** one Sonnet agent did the analysis, and a second independently recomputed the key numbers with its own script. Everything agrees within Monte-Carlo error; the verifier's small differences are listed at the end of `ANALYSIS_AND_VERIFY.md`.
- No game or engine was run, and nothing but this folder was written.
- No kt result file and no holdout file was opened.
- Every past point estimate reproduces exactly: koh −45.1, kpf −84.2, kpr −84.7, kpg −43.2, kog3 v kp3 −43.1, kog3 v kpg3 +0.1.
- Scripts and outputs are in `analyst/` and `verifier/`.

## In plain words

1. **koh's "not below zero" was mostly a power problem.**
   - For a candidate that moves cells as much as koh, the ΔMSE interval is about ±55 wide. 79% of that width comes from how few real Limitless matches the moved cells have, mostly the nine Rayquaza cells. The simulator's 500 deals account for the rest.
   - A koh-sized true gain (real error 14.0 → 12.3) would clear zero only about a third of the time. To clear half the time, a big-footprint candidate needs real error down to about 11.9, and to about 10.9 to clear 80% of the time.
   - koh's Altaria veto is a different matter: it's inside the simulator (own side −1.8 ± 1.4 over 4,500 deals), not a power problem.
2. **Small-footprint candidates are limited by the simulator's deals, not by the real data.**
   - For candidates like kog3 v kp3 (6% of games differ), the simulator side is about 65% of the variance.
   - They can be confirmed at about −18 ΔMSE (real error −0.7) half the time.
   - Quadrupling the deals (2,000 per cell) cuts what they need by 29-48%, at about 3 laptop hours per candidate.
3. **What the 14.0 is made of.**
   - About 73% of the raw squared miss is real simulator bias, 25% is Limitless sampling noise, and 2% is the simulator's own noise.
   - A perfect simulator would still show a raw miss of about 8.2 from Limitless noise alone. On the scoreboard's own scale (τ̂, which subtracts the noise), a perfect simulator reads 0.9-1.1 at the median and 6.2 at the 95th percentile. So **the 5.5 target sits inside the scoreboard's own noise**.
4. **Where the bias is.**
   - 76% of it sits in the 17 new cells (Rayquaza and Altaria/Greninja), which also have the thinnest real data (606 matches).
   - The top three cells are Rayquaza v Lucario (sim 34.8 v real 73.3), Rayquaza v Vespiquen (25.2 v 61.1) and Altaria/Greninja v Sceptile (31.0 v 66.7). Then Sceptile v Vespiquen (64.2 v 35.7), the known open cause.
   - The top ten cells hold 69% of the squared miss, and noise is only 12% of theirs, so those misses are real.
5. **What doesn't help:** pooling to 10 deck averages gives nothing, and down-weighting thin cells gives about 8-10%. A post-freeze read on its own is weaker than today (about half the data). It helps only when added to the development data.

## For the hill-climb

- **Print the power beside every ΔMSE reading:** its sd, and the gain it could detect half the time (MDE50) and 80% of the time (MDE80), from the same games. This is reporting only and changes no rule. The laptop can add it to kt's reading as "reported beside".
- **kt:**
  - kt3 moves 65% of games, so it will behave like koh: a big gain would be needed to clear zero at these sizes.
  - kta3 (2.5%) is read on the reserve route, whose no-harm test is simulator-internal; more deals, not more real data, would sharpen it.
- **Decisions for Dustin** (rule changes; nothing is changed here):
  1. **Fold the spent Sept 25 Limitless holdout into the development data?** Real matches would go from 2,214 to 4,712 (×2.13), and the chance of confirming a koh-sized gain from about 36% to 57%. It ends the rule that the holdout is never opened.
  2. **Run candidate tables at 2,000 deals per cell** (×4) when a candidate's footprint is small? It helps small-footprint candidates most (the needed gain falls 29-48%). It costs about 3 laptop hours per candidate, or the cloud's spare cores.
  3. **The 5.5 target:** keep it as "as good as the data allows"? It is inside the scoreboard's own noise, so reaching it can't be told apart from a perfect simulator.
