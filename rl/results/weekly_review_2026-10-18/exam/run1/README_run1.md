# Exam run 1: the first scored run (prepared Oct 19-20; run live Oct 20, 00:59-01:05Z)

**The results are in `RESULTS_run1.md`, and the outputs are in `live-20261020T0059Z/`.** They wait for Astra's checkpoint-3 review.

This is PLAN step 3 for the unseen-positions exam (v1.6, `5518fd60`). The live run starts on the coordinator's go. Astra passed the frozen tag
`judge-prompt-frozen-4` (commit 72eea776, Sonnet's final review round on top of the dry runs' eb19c7af; the prompt is unchanged) and this kit at a2db950c. The formal comparison is the judge against km3. kx3 can't run on the frozen tree, and the
non-formal kx3 side run is skipped (3-hour rule). Both are recorded in `PREREG_DEVIATION.md`.

## What runs
`MODE=live bash run_exam.sh`, inside WSL tmux. It does the following:
1. **Clone and check.**
   - It makes a clean sparse clone of the judge tag and checks out the tag.
   - It runs `python3 freeze_identity.py --check`, which must pass: sources, prompt fingerprint, settings, engine tree, and both executables.
   - It then runs `test_budget.py`, the spend bound's tests. These use mocks and old fixtures only: no key, no API call, nothing from the exam.
2. **Inputs** (`prep_inputs.py`), taken from the exam commit only.
   - **Candidate view:** each point's `position` and nothing else. Any answer-key field in it stops the run.
   - **References:** `references.json`, verbatim. Its sha256 must start 12e0e997, and `references_meta.json`'s must start 6adca41e, the files Astra checked.
   - **Eligibility:** `eligibility.json` in the harness's `ai_judge_eligibility_v1` format. It has 49 primary points, 19 full-scope points, each point's
     game, and the 2 diagnostic points with their dated exclusion reason.
   - **Decks:** the three lists, from the tag's tree.
3. **Plan lists and cost estimate.** No plan list may be capped. The estimate uses the assumed $3 / $15 per Mtok and about 1.5k output tokens a call. It
   must be at most $12 per judge run, or the script stops before any call.
4. **km3 rows**, from the frozen baseline executable, played afresh. Seeds are 25,100,000,001 to 25,100,000,003, registered in START_HERE at main
   `111ca123` before any run.
5. **The judge, primary:** ONE live call per decision, through `budget_judge.py` (see "Spend bound"). Model and settings are frozen, and it uses the
   API-credit key.
6. **The formal comparison, primary:** `judge.py compare --on-problem fail`, km3 against the judge.
   - **Prefix agreement** on the 49 primary points. This block carries the pass condition (below).
   - **Full-plan agreement** on the 19 full-scope points, as a separate block.
   - The game-clustered bootstrap with analysis.py's verdict rule.
   - The 2 diagnostic points in a separate block.
   - Any problem fails the batch.
7. **The judge, repeat:** a SEPARATE run for sensitivity only, under the same spend bound.
   - judge.py stamps every invocation's rows `repeat: 0`, so `relabel_repeat.py` sets them to 1. That field is set after the call and is in no hash.
   - Its own comparison, `--judge-repeats 2`, gives the sensitivity estimate. It never replaces the primary.
8. **Wrap-up.**
   - `categories.py`: a DESCRIPTIVE breakdown of the primary prefix agreement by deck kind, answer kind and deck. It has no interval or verdict.
   - `judge.py spend` totals the cost.
   - `run_manifest.json` records the sha256 of every output written before it, the judge ref, the seeds and the exit codes. Its `judge_ref_commit` is
     the annotated tag object, f7d5f4e5 for frozen-4, which points to commit 72eea776; run.log line 2 names the commit. run.log's final "done" line
     and STATUS come after the manifest.

## The pass condition (fixed before any live call)
Run 1 passes only if the formal PRIMARY PREFIX verdict is **"judge higher"**: `analysis.prefix.contrasts[0]` in `report_primary.json` (a = judge,
b = km3), on 49 primary points from 26 games.
- That verdict needs the 95% game-clustered interval of judge minus km3 to lie above zero AND the sign-flip test over games to support it
  (p < 0.05), with at least 10 games. This is analysis.py's existing `verdict()` rule.
- With 26 games the sign-flip test is analysis.py's fixed-seed Monte Carlo version: 100,000 draws, seeded with SEED + 1 = 20261020. The bootstrap uses
  20261019, and the exact enumeration is used only up to 16 games. The seed number was corrected after the run; the method is unchanged.
- "Inconclusive" or "km3 higher" is not a pass. It sends the coming week to maintenance and upstream work with no kx3 port. That is a resource choice,
  not evidence that the AI approach can't help.
- The 19-point full-scope block, the repeat, the diagnostic block and the categories are reported separately and don't enter the pass condition.

The details are in `PREREG_DEVIATION.md`.

## Spend bound (Astra's pre-run correction, Oct 20)
**The $25 of API credits is a hard bound** for both judge runs together, with $12 as each run's own hard cap.
- **How it works.** `budget_judge.py` runs the judge calls in place of judge.py's own loop. judge.py is frozen and isn't edited.
  - Before a call is sent, its worst case is reserved: the prompt's UTF-8 bytes plus 2,000 at the input price, plus 8,000 output tokens (max_tokens)
    at the output price, at judge.PRICES.
  - A call is sent only if what was spent plus everything reserved plus this worst case stays within both $25 and the run's $12.
  - When a call returns, its reservation is replaced by its actual cost.
  - A failed call is charged its whole worst case, and no further call is sent.
  - One ledger file (`spend_ledger.json`) carries the spend from the primary run into the repeat run.
- **Why it holds.** With 4 calls in flight, spent plus reserved never passes the total.
- **Rows are unchanged.** Each call is `judge.judge_one` with the FROZEN settings. `test_budget.py` checks that the rows equal judge.py's own loop's,
  field for field.
- **Tests** (`test_budget.py`, 21 checks; mocks and old fixtures only). They all passed on eb19c7af, and the live run repeats them on the frozen tag before
  any call:
  - 32 threads with random costs never pass the bound;
  - calls that each cost their full worst case stop exactly at the bound;
  - a failed call is charged its worst case and stops sending;
  - the run cap, the shared ledger and the lock behave as described;
  - a mocked orchestrator run matches judge.py's loop;
  - a tight total sends some calls, refuses the rest and stays within the total.
- **Size on the exam's prompts** (mock check, Oct 20):
  - a call's worst case is $0.14-0.56 (median $0.18), and all 51 at worst case come to $10.27 per run;
  - the bound therefore can't cut a run short at these prompt sizes;
  - the mocked primary and repeat runs went through with 0 refusals.

## Dry runs (Oct 19), judge mocked
`MODE=dry REF=eb19c7af`: the frozen-4 candidate. On Oct 19, `mock_judge.py` replaced the API call with a fixed "PLAN: 1" reply tagged MOCK; since Oct 20
the mock is `budget_judge.py --mock`. No key was read and no API call was made.

**Results:**
- `freeze_identity --check` passed.
- The inputs and both hashes matched.
- No plan list was capped.
- 153 km3 rows, on the dry-run seeds 25,100,900,001-003.
- 51 mock judge rows.
- The primary comparison exited 0 (`formal: true`, 0 problems). The relabel and the sensitivity comparison also exited 0.
- The category breakdown and the manifest were written.

The first attempt stopped because `compare` wasn't given `--positions/--decks`; that is fixed. The dry-run outputs stay on the laptop
(`~/exam_run1/dry-*`). They aren't results: the judge is mocked, and the km3 rows use dry-run seeds.

### Exposure record (written Oct 20, before any live call)
**These dry runs played the REAL, frozen km3 on the exam positions**: 153 rows each, on dry seeds. So "no bot ran on the exam" is not accurate.
- **What was produced.** Run 2 wrote the km3 and mock agreement figures to `report_primary.json`, `report_sensitivity.json` and `by_category.json`.
- **Who saw what.** Only the laptop session saw figures, and only the console's category breakdown (km3's and the mock's prefix agreement by deck kind,
  answer kind and deck), with counts. The overall contrasts were never opened. No figure went to anyone else.
- **What changed afterwards.**
  - Unchanged: the prompt, the keys, the eligibility, prefix agreement and the decision rule.
  - The frozen tag (72eea776) changed the separate full-plan comparison and some label reading on top of the dry runs' eb19c7af, as listed in
    `PREREG_DEVIATION.md`. Sonnet made that change without any dry-run figure.
  - In the kit: only records, README text, the unrun `kx3_side.py`, the written-out pass condition (analysis.py's existing rule) and the spend bound
    (no row field changes).
- **Baseline exposure, not judge exposure.** km3 is a frozen, untuned baseline. Nothing is known about the judge on the exam.
- **The live run regenerates km3** on the registered seeds 25,100,000,001-003. No dry-run row is reused.

The full record is in `PREREG_DEVIATION.md`.
