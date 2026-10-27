# K21: unchanged kx3 on the frozen exam v2, the result (Oct 27)

**Label: EXPERIMENT.** This is frozen-7's own label for a compare run with `--allow-other-binaries` (report `formal: false`). K21 makes it the registered kx3 result (PREREG_RUN3.md, K21 section 6, and K21a). Results go to the coordinator only.

## The registered primary (K21 section 5; 95%)

| | decisions (games) | Gemini (saved run 3 rows) | kx3 (mean of 3 seeds) | Gemini minus kx3 | sign-flip p | verdict |
|---|---|---|---|---|---|---|
| **PRIMARY** | 258 (76) | 0.624 [0.571, 0.677] | 0.426 [0.364, 0.489] | **+0.198 [+0.120, +0.273]** | 1e-05 | **judge higher** |

- **Verdict rule (frozen-7's analysis.py, as registered):** the game-clustered 95% interval lies above 0 AND the sign-flip p < 0.05, with at least 10 games. Here: the interval excludes 0 and the sign-flip test over games agrees; 0 pairs dropped.
- **What it means (K21 section 6):** on these 258 decisions of exam v2, Gemini's first plan segment matches Dustin's accepted moves more often than unchanged kx3's does. This is the comparison section 8 required before anyone says Gemini beats our best bot.
- **Its limits:** the measure is prefix agreement (v1.6's scoring, R1's lister segments), not plan quality. It says nothing about finished games or win rates.
- **Unchanged:** run 3's filed verdict (Gemini v km3, RESULTS_run3.md) stands. **The adapter is not started.**

## Descriptive only (K21 section 5: no verdict is drawn from these)

| | decisions (games) | first bot | second bot | difference | sign-flip p |
|---|---|---|---|---|---|
| kx3 minus km3, same seeds and decisions | 258 (76) | kx3 0.426 [0.364, 0.489] | km3 0.451 [0.388, 0.515] | -0.025 [-0.040, -0.009] | 0.00441 |
| Full-scope block, Gemini minus kx3 | 86 of 90 (46) | Gemini 0.581 (matched) | kx3 0.353 (matched) | +0.229 [+0.097, +0.362] | 0.00223 |
| Full-scope block, kx3 minus km3 | 87 (47) | kx3 0.349 | km3 0.368 | -0.019 [-0.057, +0.019] | 0.433946 |
| Chance-ending stratum (run 3's 168 points), Gemini minus kx3 | 168 (74) | Gemini 0.649 [0.582, 0.713] | kx3 0.462 [0.397, 0.528] | +0.187 [+0.101, +0.271] | 9e-05 |

- **kx3 minus km3:** frozen-7's analysis prints "km3 higher" for this line; K21 registered it as descriptive, so no verdict is drawn. The independent check (below) traced it to kx3's own overrides of km3's move: kx3 chose a different listed plan on 89 of 774 (decision, seed) pairs, on 59 of the 258 positions. kx3 matched the answer on 6 of them, km3 on 25, and neither on 58: a net of -19 of 774 pairs, which is the -0.024548. The difference covers 25 decisions (21 lower, 4 higher) in 20 games. On all 685 pairs where both picked the same plan, they scored the same.
- **kx3's time:** median 9.9 s per decision and seed (95th percentile 47.2 s, longest 154.6 s); 3.31 h for all 774 rows (the registered estimate was 1.4-6 h per seed).
- **Full scope:** 4 of the 90 full-scope points were not comparable for both bots and were dropped, not scored (kx3's plan stops at a chance event: 20261020_000857000_SR-t1, 20261023_122720000_SR-t1, 20261024_175606000_SR-t1; Gemini's: 20261023_122720000_SR-t1, 20261023_215109000_SR-t3). kx3 minus km3 dropped 3.
- **By category:** `run/out/by_category_k21.json` and `categories_k21.txt` (descriptive; a point counts in each of its kinds).

## K21a: what replaced each freeze check the switch skips

- **S1, the plan lister's sha256** (judge.py line 1002): checked in `freeze_checks.json` before the rows and again before the compare; lister bd4eeb6e4579f88c… = FROZEN.json's.
- **S2, `freeze_identity.check`** (line 1007): item by item, 31/31 pass at night start and before the compare; frozen-7 tag 712593a1, its own check: pass.
- **S3, each row's executable** (line 1000): every kx3 row carries the launch line's binary b0df8e0e119a2339… and every km3 row f35a1a99 (f35a1a99188806c7…).
- **Each report** carries exactly the one experiment switch, the frozen fingerprint, the frozen lister and the frozen judge settings (compare_k21.py checks this).
- **No Gemini call:** gemini_calls 0; Gemini's saved run 3 rows are reused byte for byte (judge_primary.jsonl 762b6aed, pass 1 335c438b).

## How it ran (night 1 of 4; the other three are not needed)

- 2026-10-27T02:00:00Z: start; kit d4877c97; freeze checks 31/31 pass.
- 2026-10-27T02:04:00Z: build OK, binary sha256 b0df8e0e119a233906c2b8cdcce01ccab557a7a54e150b78de5ab993fdcdce51.
- Gates (a)-(d) on development positions only: {"a": true, "b": true, "c": true, "d": true}; all pass. The launch line was written at 2026-10-27T02:05:17Z with 0 kx3 exam rows so far.
- 2026-10-27T02:05:20Z: launch line `89578355` committed and pushed, before any kx3 exam row.
- 2026-10-27T05:24:18Z: 3 seeds complete (25101000001, 25101000002, 25101000003), 774 rows; the compare ran at 2026-10-27T05:25:06Z.
- Later nights (Oct 28, 30, 31 UTC) find `DONE` and run nothing.

## The independent check before this report (workflow wf_6bdd9503-5a0; 5 Opus agents, no Sonnet; no API or network call)

- **Frozen code, own driver** (not compare_k21.py): every estimate, n, interval end, p and verdict above reproduced to the printed digits; the judge and km3 rates equal run 3's own report; the kx3 rows fed to the compare equal the runner's raw rows.
- **From scratch** (frozen code read as a spec only): every point estimate and n exact; its own random draws land within 0.0017 of every interval end; with the registered seeds the method reproduces every digit.
- **Line level:** the kx3 minus km3 accounting above; on identical plans the scores are identical.
- **Provenance:** binary sha on disk and in every row; the kit equals d4877c97's; the inputs equal the frozen exam files (6e5fab0c) and run 3's live rows (e159551d); the launch commit is on origin and precedes every row file.
- **Critic:** no discrepancy. Limits: the binary was not rebuilt (its source was checked: frozen tree 70652fff plus kx3's insertions only, the card data unchanged); the order "record, launch, rows" rests on the laptop's clocks and git times.
- **What the checkers ran beyond reading files** (disclosed; nothing new is scored from them): the frozen lister on the 258 exam positions (to rebuild the plan lists, as the compare does); the K21 binary as km3 on all 774 exam pairs (identical to the baseline rows byte for byte); kx3 replays on 8 sampled exam pairs and 2 gate (b) development pairs (identical lines). One checker also computed a label-only reading, which is not the registered definition and is not a result.
- **No answer content was printed** by any checker. Their scripts and outputs stay on the laptop (`~/k21_verify`, scratchpad `exam2/k21/verify/`).

## Records

- `run/`: the night's rows (`rows/`), the compare's outputs (`out/`, including SUMMARY_K21.json and both reports), the gates' outputs on development positions (`gates/`) and the logs. `launch/` and `kit/` were committed before the rows.
