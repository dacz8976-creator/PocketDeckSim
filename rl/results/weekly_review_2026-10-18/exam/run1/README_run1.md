# Exam run 1: the first scored run (prepared Oct 19, NOT run)

This is PLAN step 3 for the unseen-positions exam (v1.6, `5518fd60`). It is prepared and dry-run only. The live run starts on the coordinator's go, after
Astra passes the frozen tag `judge-prompt-frozen-4`.

## What runs
`MODE=live bash run_exam.sh`, inside WSL tmux. It does the following:
1. **Clone and check.** It makes a clean sparse clone of the judge tag, checks out the tag, and runs `python3 freeze_identity.py --check`. The check must
   pass: sources, prompt fingerprint, settings, engine tree, and both executables.
2. **Inputs** (`prep_inputs.py`), taken from the exam commit only.
   - **Candidate view:** each point's `position` and nothing else. Any answer-key field in it stops the run.
   - **References:** `references.json`, verbatim. Its sha256 must start 12e0e997, and `references_meta.json`'s must start 6adca41e, the files Astra checked.
   - **Eligibility:** `eligibility.json` in the harness's `ai_judge_eligibility_v1` format. It has 49 primary points, 19 full-scope points, each point's
     game, and the 2 diagnostic points with their dated exclusion reason.
   - **Decks:** the three lists, from the tag's tree.
3. **Plan lists and cost estimate.** No plan list may be capped. The estimate uses the assumed $3 / $15 per Mtok and about 1.5k output tokens a call. It
   must be at most $12 per judge run, or the script stops before any call.
4. **km3 rows**, from the frozen baseline executable. Seeds are 25,100,000,001 to 25,100,000,003, registered in START_HERE at main `111ca123` before any run.
5. **The judge, primary:** ONE live call per decision. Model and settings are frozen; it uses the API-credit key, and it stops starting calls at $12.
6. **The formal comparison, primary:** `judge.py compare --on-problem fail`, km3 against the judge.
   - **Prefix agreement** on the 49 primary points.
   - **Full-plan agreement** on the 19 full-scope points.
   - The game-clustered bootstrap, with "inconclusive" when the interval includes 0.
   - The 2 diagnostic points in a separate block.
   - Any problem fails the batch.
7. **The judge, repeat:** a SEPARATE run for sensitivity only, also stopping at $12.
   - judge.py stamps every invocation's rows `repeat: 0`, so `relabel_repeat.py` sets them to 1. That field is set after the call and is in no hash.
   - Its own comparison, `--judge-repeats 2`, gives the sensitivity estimate. It never replaces the primary.
8. **Wrap-up.**
   - `categories.py`: a DESCRIPTIVE breakdown of the primary prefix agreement by deck kind, answer kind and deck. It has no interval or verdict.
   - `judge.py spend` totals the cost.
   - `run_manifest.json` records every file's sha256, the judge commit, the seeds and the exit codes.

**Budget:** the cap is $25 of API credits for both judge runs. The estimate from the dry run is about $3.2 per run at the assumed prices, so about $6.5
in all.

## Dry run (Oct 19, 23:59Z), judge mocked
`MODE=dry REF=eb19c7af`: the frozen-4 candidate, with `mock_judge.py` replacing the API call by a fixed "PLAN: 1" reply tagged MOCK. No key was read and
no API call was made.

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

## Open before the live run
**kx3 isn't played.** The frozen baseline executable plays only the minimax bots coded `k<number>`/`km<number>`; judge.py refuses kx3. PLAN's rule ("it
helps only if it beats kx3 by more than its own wobble") needs kx3 rows. The coordinator's options:
- (a) Sonnet adds kx3 to the frozen baseline, which needs a new freeze;
- (b) a separate, non-formal kx3 run through another pg_pos, reported descriptively next to the formal km3/judge result;
- (c) km3 only for this run.

The script as committed runs km3 and the judge.
