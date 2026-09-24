# Run 5 build notes: step 0 and stage 1

Written 2026-09-23 by Claude (Opus, builder). The lead reviews this note, then Astra does one review pass, then Dustin launches.
Nothing was launched on the laptop. RUN5.md, train_v4.py, the engine, the add-on, the old wheels, the old run folders and the historical results were not changed. FEASIBILITY.md was not read.

## The short version

- **Both modes work end to end in the cloud**: train, crash, resume, finish, confirmations, audit, held-out test (step 0) and REPORT.txt. **16 of 16 practice checks passed** (`checks.txt`).
- **One surprise: `train_v4.py` cannot run on add-on 0.7.2.** The 0.7.2 wheel installs as a single file (`pdl_rl_env.abi3.so`). Earlier wheels installed as a folder. `train_v4.py` looks for the folder layout to record the add-on's hash, and it crashes before any game is played (reproduced). `audit_v4.py`, `transfer_v4.py` and `report_v4.py` all import `train_v4` and call the same function, so they crash too. As instructed, I didn't edit `train_v4.py`. **Step 0 runs on `train_v5.py`** (the differences are listed below), and the three report steps have v5 copies.
- **Three things need the lead's decision.** Details are under "For the lead and Astra".
  1. Step 0 reuses run 4's pilot seeds. That follows from "pilot unchanged".
  2. Stage 1 has no held-out row.
  3. With the specified formula, the averaged copy's early checkpoints are mostly the untrained network.

## Files (SHA-256)

All are in `Boss Folder/rl-feasibility-2026-09-18/`. All are new, and no existing file was changed.

| File | SHA-256 |
|---|---|
| `run_training_v5.sh` | `f5828a63c951f3cb4dcb54359afab9aceb570d039fc40393b48877e9787e1e29` |
| `train_v5.py` | `0c0470b93d2a75d1ee31531f4a75c487fbdd54ab2ef6c8f40ae4381000e00c8e` |
| `audit_v5.py` | `6f92178366d0f575e91619625f14168148af556cf95a69e63b0c2c3ee32063d2` |
| `transfer_v5.py` | `613fe446f6ae86b47102932c65c8c033a24ba3982f25979da9459fea99c3e5f5` |
| `report_v5.py` | `65986328a5e6e378bcea2abb64fde6d0cd57906637ca19dc08a2ca909aed2944` |
| `stage1_v5_settings.json` | `b0ccef6af5797088b00557d6c394c752f746688f48f474e1d8ca7f76ad7add10` |

This folder (`results/run5_build/`) also holds:
- `*_v4_to_v5.diff`, one per file, for Astra;
- `checks.txt` and `step0_equivalence.txt`;
- `practice/`: every launcher output, the check script, the tiny settings files, memory logs, and the practice runs' STATUS/REPORT files. No checkpoints are included.

## What changed from train_v4.py

`train_v5.py` is `train_v4.py` (memory fix included) plus the items below. **Items 2–4 are off unless the settings turn them on**, so step 0 plays and trains the way run 4's pilot did.

1. **Add-on lookup** (`addon_path`): finds either layout. This is the one change step 0 needs.
2. **Seeds come from the settings** (`"seeds"`). The default is run 4's seeds, unchanged. Stage 1 sets its own ranges.
3. **The averaged copy** (`"avg_half_life_games"`, 100,000 in stage 1):
   - **Where it lives:** one float64 copy per network, in the main process only.
   - **When it updates:** every time that network's live weights are published, which happens per network every 50 of its own training steps, plus all networks at each checkpoint. The update is `avg = decay × avg + (1 − decay) × live`, with `decay = 0.5 ** (games since that network's last update / 100,000)`.
   - **Where it starts:** as the starting network, at game 0.
   - **Where it never goes:**
     - The workers' shared weights are written in one place, from the live network.
     - Past opponents come from `pool.json`, which lists only live checkpoints. The code now asserts this.
     - The training loss uses only the live networks.
   - **Saved** at every checkpoint beside the live network as `ckpt_400k_avg_weezing.npz`. That's the brief's example with the order changed. Run 4's `<checkpoint>_<deck>.npz` pattern is kept, so the confirmation, the audit and resume cleanup all treat it as a checkpoint called `ckpt_400k_avg`.
   - **Kept in every resume save**, with its hash recorded in `state.json`. A resume that doesn't restore it byte for byte refuses to continue.
   - **Evaluated** at every checkpoint on exactly the live evaluation's game list: 1,000 paired games per network against k3 (500 per seat), plus 200 against random moves, on the same seeds and seats.
   - **Recorded** in `settings.json` and described in STATUS.txt.
4. **Smaller changes:**
   - `"eval_random_per_matchup"`: stage 1 needs 200 random-move games per network. Run 4's `eval_random // 4` was sized for four matchups per network and would give 50.
   - `"criteria": null` means no pass/fail rule in code. The run ends as FINISHED, and the verdict lists each network's best confirmed checkpoint.
   - **Confirmation candidates** include the averaged checkpoints. For each network, the best by k3 margin (live or averaged, whichever is higher) is confirmed, plus the runner-up if it's within 2 points. Weezing is confirmed first and Lucario second. Each candidate is confirmed on 2,000 fresh paired seeds (1,000 per seat), then gets the existing audit.
   - **Level-off and stopping** use the live weights only. The rule is run 4's, word for word, moved into a function so it could be tested (`leveled_off_at`).
   - **Refuses checkpoints that aren't whole thousands of games** (found in practice). Two checkpoints under 1,000 games apart got the same name (`ckpt_0k`), and the second overwrote the first. Real settings never do this, but a practice file did.
   - STATUS/REPORT headings say "Run 5".

**The report-step copies:**
- `audit_v5.py`: only the import, its own name and its output file prefix (`v5_`) changed.
- `transfer_v5.py`: the same, plus the seed base comes from the settings, and it skips itself when the settings name no held-out deck.
- `report_v5.py`: the same, plus:
  - the averaging verdict;
  - RUN5.md's accepted rules limits for Weezing vs Lucario, which RUN5.md says go with every result;
  - wording without pass/fail when there are no criteria.

**The launcher, `run_training_v5.sh --step0 | --stage1`:**
- **Setup:**
  - works out every path from its own location, so it works from any folder;
  - refuses to run unless the add-on README lists the wheel's SHA-256 and the wheel's actual SHA-256 matches it;
  - installs the wheel into `~/.cache/pocket-deck-lab/run5-venv`;
  - then checks that the installed version is 0.7.2, that the installed library's SHA-256 matches the one in the README, and that encoding v2.2 loads.
- **Running:**
  - uses `set -euo pipefail`;
  - runs training, then the audit, the held-out test and REPORT.txt, as run 4's launcher did;
  - after step 0, adds RUN5.md's +5 go line to REPORT.txt. The unchanged pilot settings still carry run 4's +10 "PASS" rule, and that word would otherwise mislead.
- **Practice runs** need `RUN=runs/practice-...` and are refused in the two real folders.

## Step 0 on train_v5.py: exactly what differs from run 4's pilot

This is checked in `step0_equivalence.txt` without playing games.
- **Game lists:** with the unchanged `pilot_v4_settings.json`, the bar, checkpoint, random-move and confirmation lists are identical to `train_v4.py`'s.
- **Training seed base:** the same, 3,000,000,000.
- **Code:** these functions are byte-identical in both files: the actor, game play, evaluation, pairing statistics and weights loading/saving.
- **Settings:** no value differs. `settings.json` gains three keys, each set to run 4's behaviour.

**What is different:**
- the add-on lookup;
- the whole-thousands check (the pilot's checkpoints are multiples of 50,000, so it has no effect);
- the "Run 5" headings;
- the report steps are the v5 copies;
- the +5 line added to REPORT.txt.

The rules (rules4) and the add-on (0.7.2) differ by design.

## Seeds

### Stage 1

**Corrected after Astra's review** (second addendum): the first ranges here were also used by my cloud practice runs. They are replaced by the ranges below, which no earlier run and no practice run has used; this is checked from the practice runs' own records (`practice/seed_overlap_check.txt`). They are set in `stage1_v5_settings.json`.

| Use | Range |
|---|---|
| Training | 6,000,000,000 + attempt × 100,000,000 + game number. The first attempt is 6,000,000,000–6,001,999,999, and each resume moves up 100M. Thirty attempts would still end below the practice block. |
| Checkpoint evaluation vs k3 (live and averaged, the same list at every checkpoint) | 83,000,000–83,000,999 (Weezing's network) and 83,050,000–83,050,999 (Lucario's) |
| Random-move games | 83,500,000–83,500,199 and 83,505,000–83,505,199 |
| Bars + every confirmation (paired) | 89,000,000–89,001,999 (even: Weezing in seat 0; odd: seat 1) |
| Held-out | 89,500,000–89,999,999 reserved, unused (no held-out row in stage 1) |
| **Reserved for stage 2's final 2,000-game evaluation** | **88,000,000–88,999,999** (recorded in the settings as `seeds_reserved_stage2_final_eval`; nothing uses it) |

The audit replays recorded games. Its four chance streams per option come from the engine's audit mode, as in run 4, and it adds no game seeds. [That the audit adds no seed range is my reading of `audit_v4.py`; I didn't check the engine side.]

### Ranges already used

Read from the code, not from memory:

- **Run 1** (`train.py`):
  - training: 1,000,000,000 + (attempt × 64 + worker) × 10,000,000 + game
  - k3 20M; random 21M; previous-checkpoint games 22M; confirmation 30M
- **Run 2** (`train_v2.py`):
  - training: the same scheme from 2,000,000,000
  - k3 60M; random 61M; previous-checkpoint games 62M; confirmation 70M
- **Runs 3–4** (`train_v3/v4`):
  - training: 3,000,000,000 + attempt × 100M + game. The highest attempt in any run folder is 1, so the top is about 3.106 billion.
  - k3 80,000,000–80,951,000
  - random 81.0–81.1M
  - previous-checkpoint games 82M (run 3)
  - bars/confirmation 90.0–90.91M
  - held-out 95M+
- **Other scripts from that period:**
  - matchup tests 40M and 41M; knockout audit v2 43M
  - k3 screen 50M; speed tests 50M and 60M
  - step-1 checks 18M and 18.5M; step-3 checks 70M, 1M, 2M, 8M and 9M
  - v2.2 checks 5M and 6M
- **Astra's rules4 recheck:**
  - pool benchmark 90M; mirror 18.9M; screen 50M
  - interface checks 18.5M and 28.5M
  - v2.2 checks 6M; add-on/CLI parity 96,092,200–96,092,201
- **Crossplay:** 97,000,000–97,999,999 (a 1M block by its own code).

**No overlap:**
- Stage 1 uses 83.0–83.51M, 88.0–89.999M, and 6.0 billion and up. (Corrected; see the second addendum.)
- A search of every `.py` in `Boss Folder/`, `lib/` and the project root found no use of 83M, 88M, 89M, 6,000,000,000 or 9,000,000,000, and no earlier run folder names its own seeds.
- Every new range is under 97M, so it's clear of crossplay under either reading of "97,000,000+".

### Step 0

Step 0 uses **exactly run 4's pilot seeds**, by construction. See "For the lead and Astra", point 1.

## Practice tests (cloud, tiny budgets; they test the program, not the bot)

**Where:**
- the 0.7.2 wheel installed as-is in the cloud (glibc 2.39, Python 3.11), so no build from source was needed;
- 2 workers;
- tiny settings: 3,000–21,000 games, 4–20 evaluation games per matchup.

**End to end through the launcher:**
- **Step 0:**
  - train → confirmations → audit → held-out → REPORT.txt (`practice/step0-final.out`, `practice/runs/practice-step0-final_REPORT.txt`).
- **Stage 1, run 1** (`stage1-a.attempt1/2/3.out`):
  - a crash at 1,500 games: the launcher exited with code 3 and ran no report steps;
  - resumed;
  - a `kill -9` of the whole process group partway between two checkpoints;
  - resumed again and finished;
  - the confirmations, audit and REPORT.txt all completed.
- **Stage 1, final code:**
  - repeated on the final code with a crash and a resume (`stage1-final.*`).

**Results by check** (full detail in `checks.txt`):

| Check | Result |
|---|---|
| (1) Averaging math on synthetic weights | Exact: decay 0.5 after one half-life; a chain of updates matches the closed form (difference 7e-16); step-by-step with changing weights matches exactly. |
| (2) Live weights untouched; workers and past opponents get live weights only | **Unit test:** the live array is byte-identical after an update. **Code:** the workers' code has no reference to the averaged copy, and the shared weights are written in one line, from the live network. **Traced 21,000-game run** (a wrapper that only watches; the trainer is unchanged): the workers received 90 distinct weight sets and 0 averaged ones; 105 past-opponent loads, 0 averaged; `pool.json` has no averaged names. |
| (3) Same seeds and seats, live vs averaged | Identical lists at every checkpoint, for both the k3 and the random-move games, in two runs. |
| (4) Resume restores the averaged weights byte for byte | **Positive:** three resumes printed matching hashes. **Negative:** I moved one value in a saved averaged file by the smallest possible step, and the resume refused with the two hashes (`corrupt_resume.out`). |
| Averaged checkpoint through confirmation and audit | In two practice runs an averaged checkpoint was a confirmation candidate. In one it was Weezing's best (`ckpt_5k_avg`), and it went through confirmation, audit and REPORT.txt. |
| Weights published per network | Each network has its own publish counter and averaged-copy update count (45 and 45 in the traced run). |
| Level-off on the newest checkpoint only | Five constructed cases, all right. Example: older checkpoints at 90% "vs previous" with the newest at 50% counts as leveled; the newest at 60% doesn't. |
| Launcher from any folder | Run from `/` with a relative path, and from `/tmp` with an absolute one. |
| Memory flat with cached past networks | **At the real cache cap (40):** training workers grew about 2 MB per cached past network (105 → 151 MB over 44 past networks); the evaluation and main processes stayed flat. **With the cap set to 6** (wrapper only, 12 checkpoints): training workers held at 88 → 88 MB once the cache was full. Stage 1 has at most 24 past networks (12 checkpoints × 2), so it never reaches the cap; expect ~50 MB of growth per worker at most [estimate]. |
| Practice checkpoints can't overwrite each other | The launcher refuses practice settings, `--smoke` or `--stop-after` in the real folders; practice folders are separate; the whole-thousands refusal is new. |
| No failure hidden behind a pipe | **Trainer crash:** launcher exit code 3, no report steps. **Deck file changed after a finished run:** both "stopped" messages appeared and REPORT.txt listed every out-of-date step (`report_step_failure.out`). |
| Wrong wheel | I appended one byte to the wheel, and the launcher refused with both hashes before installing anything (`wrong_wheel.out`). |

## Commands for Dustin

Run these in WSL Ubuntu, from any folder, with the laptop plugged in and sleep off. The same line resumes after any interruption. Progress is in plain words in `runs/<run folder>/STATUS.txt`.

**Step 0.** The run folder is `runs/run5-step0-blaziken-lucario`:

    bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v5.sh" --step0

**Stage 1.** Run this only after the lead reads step 0 as a GO. The run folder is `runs/run5-stage1-weezing-lucario`:

    bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v5.sh" --stage1

The first launch creates `~/.cache/pocket-deck-lab/run5-venv` and installs numpy from the internet, as run 4's first launch did.

## Expected durations (laptop, 8 workers)

**Step 0: about 1.3–1.5 h in total.**
- Training: about 1.2 h. Run 4's pilot with the same settings took 1.2 h of training and 0.1 h of evaluation.
- Report steps: about 10 min.
  - Audit: about 5 min. Run 4's audits ran at about 8,000 replayed games per 7 minutes (file timestamps).
  - Held-out test: about a minute.
- Rules4 may change game length a little. [estimate]

**Stage 1: about 9–9.5 h in total; it always runs the full 2M games** (see the addendum) [estimate].
- **Training:** about 8 h for the full 2,000,000 games, at run 4's ~69 games/sec. In the cloud, Weezing vs Lucario trained at the same pace as Blaziken vs Lucario (20 games/sec each), which is why I expect run 4's laptop rate to hold. [inference]
- **Evaluation inside the run:** about 58,000 games, 30–60 min.
  - 2,000 bar games;
  - 11 checkpoints × (4,000 k3 games + 400 random-move games);
  - up to 4 confirmations × 2,000 games.
- **Audit afterwards:** up to 4 × 4,000 replays, about 15 min.

## For the lead and Astra

1. **Step 0 reuses run 4's pilot seeds.** The seeds are:
   - training 3,000,000,000+
   - k3 80M; random 81M
   - bars/confirmation 90,000,000–90,000,999
   - held-out 95M+

   That follows from "pilot settings unchanged". For a regression check, identical seeds with only the rules changed is arguably what you want, but these games are not a fresh sample, and they overlap run 4 and Astra's rules4 pool benchmark (also 90M). [Unverified] If the benchmark lists Blaziken–Lucario as its first pairing, step 0's k3-vs-k3 bar games are the same games as Astra's rules4 baseline for that pair, which would make them a free cross-check. If you want fresh seeds instead, give step 0 a copy of the pilot settings with a `"seeds"` entry; no code change is needed.
2. **Stage 1 has no held-out Ninetales row.** The brief keeps it only if the existing held-out step runs unchanged, and it can't:
   - it crashes on 0.7.2;
   - unchanged, it would reuse run 4's 95M seed numbers.

   `transfer_v5.py` would run it on 87M seeds if you add `"held_out"` and `"transfer_per_row"` to the stage 1 settings.
3. **Early averaged checkpoints are mostly the untrained network** [computed from the formula]. The average starts at the starting weights, so with a 100,000-game half-life the untrained start still carries:

   | Checkpoint | Weight of the untrained start |
   |---|---|
   | 100k | 50% |
   | 200k | 25% |
   | 400k | 6% |
   | 800k | 0.4% |

   The averaged copy will look bad at 100k–200k by construction, and the "averaged scored higher at N of M checkpoints" count is tilted toward live. I suggest reading the averaging verdict from 400k on. I didn't change it, because the brief fixes the formula. The alternative is to start the average at the first checkpoint.
4. **Level-off with uneven early spacing.** The rule needs three checkpoints within 3 points, so with checkpoints at 100k, 200k and 400k the earliest stop is 400k, judged on those three. That's run 4's rule applied as written; noted only because the gaps are 100k then 200k.
5. **The confirmed best might be an averaged checkpoint.** Stage 2's scorer data comes from "stage 1's confirmed networks". If that's an averaged copy, stage 2 would play a weights file that never played a training game. That seems fine, but it's a choice to make knowingly.
6. **Small things:**
   - The audit's headings still say "(run 4)", copied unchanged.
   - STATUS.txt's "Best checkpoint per network" line is live only; averaged candidates show in the confirmations.
   - The new environment may install a newer numpy than run 4's 2.5.3. `identity.json` records it.

## Addendum, 2026-09-23: stage 1 runs to its 2M cap (lead's review)

The lead approved the build with one change: level-off must not stop stage 1.

**What changed:**
- **New setting `"stop_on_level_off"`:**
  - The default is `true`, which is run 4's behaviour, so step 0 and `pilot_v4_settings.json` are unaffected.
  - `stage1_v5_settings.json` sets it to `false`.
- **With `false`:**
  - Level-off is still computed at every checkpoint, on the live networks, with run 4's rule.
  - The run ends only at the budget; the confirmations, audit and REPORT.txt follow as before.
  - The draw gate, crash handling and resume are unchanged.
- **The stop decision:**
  - It is now one small function, `stop_reason`, and replaces the line in the checkpoint loop.
  - With `true` it gives exactly run 4's answer.
- **Level-off is recorded at every checkpoint** (`"leveled"` in state.json):
  - STATUS.txt adds a line, "Leveled off, by checkpoint: …", and says whether this run stops on level-off.
  - REPORT.txt adds a "Level-off" section, one line per checkpoint.
- **Nothing else changed.** Only `train_v5.py`, `report_v5.py` and `stage1_v5_settings.json` were edited, and the SHA-256 table above is updated. The launcher, audit and held-out files are unchanged.

**Tests** (in `practice/`):
1. **With `false`, a run whose networks level off early keeps going to the budget.**
   - Unit test (`stop_rule_checks.txt`): 48 cases, 0 wrong. The cases cover:
     - the setting false, true or missing;
     - no network, one network or both leveled;
     - checkpoints before and at the budget.
   - Tiny practice run (`nostop.out`, `runs/practice-stage1-nostop_*.txt`):
     - both networks leveled off at 3,000 games;
     - the run kept going to its 4,000 budget;
     - it then ran the confirmations, audit and REPORT.txt.
2. **With `true`, it stops exactly as before.**
   - The same unit test compares the decision with train_v4.py's rule in every case.
   - The same tiny run with `true` (`stop.out`, `runs/practice-stage1-stop_*.txt`) stopped at 3,000 games, "every network leveled off", as before.
3. **`step0_equivalence.txt` still holds** (rerun):
   - the same game lists and the same training seed base;
   - no settings value differs; the one new key is set to `true`;
   - the stop decision matches train_v4 at every pilot checkpoint for none, one or both networks leveled.

**Stage 1 duration:** it always runs the full 2,000,000 games. That's about 8 h of training plus 30–60 min of evaluation inside the run and about 15 min of audit afterwards, **about 9–9.5 h in total** [estimate]. Point 4 under "For the lead and Astra" (the earliest stop at 400k) no longer applies to stage 1.

One stale comment is left as is, because the instruction was to touch nothing else: the header of `run_training_v5.sh` still says stage 1 "can stop earlier". It's a comment only, and it doesn't change what runs.

## Second addendum, 2026-09-23: stage 1 seeds moved off the ones practice used (Astra's review)

**What Astra found, and it was right:** the tiny practice settings were copied from the real stage 1 settings, seeds included. So my cloud practice runs used stage 1's intended seeds:
- training: 5,000,000,000 up to 5,200,003,999 (resumes included);
- evaluation: 84M and 85M;
- confirmation: 86,000,000–86,000,019.

The earlier claim that the stage 1 ranges were "all new" was wrong. Step 0's approved reuse of run 4's pilot seeds is unchanged.

**What changed:**
- **`stage1_v5_settings.json`:** new seed bases.
  - training 6,000,000,000
  - checkpoint games vs k3 83,000,000
  - random-move games 83,500,000
  - bars and confirmations 89,000,000
  - held-out (reserved, unused) 89,500,000

  Stage 2's reserved 88,000,000–88,999,999 stays: no practice run touched it. The corrected table is under "Seeds".
- **`run_training_v5.sh`:** a practice run must give its own seeds, with every base at 9,000,000,000 or above (the practice block), or it is refused before anything is installed or written. This covers a different settings file, `--smoke` and `--stop-after`, for both step 0 and stage 1. Real runs are unaffected.
- **Nothing else changed.** `train_v5.py`, the report steps and step 0's settings are untouched; the SHA-256 table above is updated for the two changed files. The header comment Astra accepted is left as it was.

**Checks** (in `practice/`):
1. **The new stage 1 ranges are unused.** `seed_overlap_check.txt` reads every practice run's own records:
   - its settings, and every training attempt from its state, whole budget as the upper bound;
   - every evaluation, bar and confirmation seed, exactly, from `eval_games.jsonl`, including interrupted attempts;
   - held-out ranges from the held-out step's own formula.

   It then compares them, and the earlier runs' blocks, with the stage 1 ranges generated by `train_v5.py`'s own game lists from the real settings. Result: **no overlap**, and no two stage 1 ranges overlap each other.
2. **The check can fail.** The same check run against the old stage 1 seeds reports 3,331 overlaps with practice (`seed_overlap_negative_control.txt`), which is Astra's finding.
3. **The practice-seed rule works.** Three refusals are in `seed_refusals.out`: the old stage 1 practice file (real seeds), the old step 0 practice file (no seeds of its own), and `--smoke` with the real settings.
4. **Practice still works on the practice block.**
   - Step 0 ran end to end.
   - Stage 1 crashed at 1,500 games, resumed with the averaged weights restored byte for byte, and ran to its budget with confirmations, audit and REPORT.txt (`step0-pseeds.out`, `stage1-pseeds.attempt1/2.out`).
   - Every seed they used was 9,000,000,000 or above.

The old practice settings files stay in `practice/` as the record of what those runs used; the launcher now refuses them. New practice files: `step0_tiny_practiceseeds.json`, `stage1_tiny_practiceseeds.json`.

## Third addendum, 2026-09-23: closing two gaps in the practice guard (Astra's second review)

**What Astra found:**
1. A run given only a different folder (for example `RUN=runs/practice-check`), with the real settings and no test option, wasn't treated as practice, so it ran on the real seeds.
2. Extra arguments were passed to the trainer after the checked settings, so another `--override` or `--run` could replace the checked settings or run folder.

**What changed in `run_training_v5.sh`** (the only file changed; its SHA-256 is updated above):
- **Any non-standard run folder is a practice run**, as are a different settings file and the test options. Practice runs must use practice-block seeds (9,000,000,000 and up).
- **Real folders are recognised however they're spelled.** The folder is resolved the way the trainer resolves it, relative to the script's folder, so a trailing slash, an absolute path, or `./` and `..` still count as the real folder. A practice run is refused in either real folder, from either mode.
- **Only `--workers N`, `--smoke` and `--stop-after N` are passed on.** Every other option is refused before anything is installed or written. That includes `--override`, `--run`, their `=` forms and the trainer's accepted abbreviations such as `--ov` and `--ru`. The numbers must be whole numbers.

**Tests** (`practice/guard_tests.out`):
- **How they ran:** the table was run on a copy of the launcher identical except for its training line, which printed what it would run and stopped. That way a wrongly accepted configuration couldn't train. The copy was deleted afterwards.
- **Results:** 22 of 22 cases behaved as intended.
  - Refused: both of Astra's gaps, the abbreviations, a missing or non-number `--workers`, and four other spellings of the real folders, including practice seeds sent into the other mode's real folder.
  - Still accepted: real stage 1 (with and without `--workers 6`), real step 0, and practice runs on practice seeds in both modes.
  - No folder was created by any refused or dry case.
- **The real launcher, end to end:** a tiny stage 1 practice run on practice seeds trained, confirmed, audited and reported (`stage1-guardfix.out`). The lowest seed it used was 9,000,000,000.

## Fourth addendum, 2026-09-23: settings read once, and the raw practice records (Astra's third review, `ASTRA_LAUNCHER_REVIEW_20260923.md`)

**What Astra found:** a relative settings file name was checked from the caller's folder, then read again after the launcher moved to the project folder. With files of the same name in both places, a practice-seeds file passed the check while the trainer received the real stage 1 seeds.

**What changed in `run_training_v5.sh`** (the only code change; its SHA-256 is updated above):
- The settings path is resolved once, from the caller's folder, before any check.
- The file is read once into memory. That same text is what the practice-seed check reads and what the trainer receives, so a second read can't differ from what was checked.
- The default settings path is resolved the same way, so a real run is still recognised however its path is written.

**Tests** (`practice/guard_tests2.out`): 27 of 27 cases right. They ran on a dry copy of the launcher whose training line printed the exact seeds it would pass on and stopped; the copy was deleted afterwards.
- **Astra's case:** the same relative file name in the caller's folder (practice seeds) and the project folder (real seeds). The trainer gets the caller's practice seeds.
- **The reverse:** real seeds in the caller's folder and practice seeds in the project folder. Refused.
- **Also covered:**
  - a `./` path;
  - the real settings named by another path, both as practice (refused) and as the real run (accepted, with the real seeds);
  - every earlier case.
- **The real launcher, end to end:** Astra's setup, a tiny practice run from a folder holding `same-settings.json` while the project folder held a same-named file with the real stage 1 settings (`stage1-relsettings.out`). It trained, confirmed, audited and reported on the practice seeds (all 9,000,000,000 and up).

**The raw practice records are now on the laptop:** `practice/records/`. They were built by `practice/make_records.py`.
- **What was exported:** all 15 cloud practice run folders, with their names and subfolders kept. That includes:
  - the discarded trace/draw-gate attempt;
  - the copy of the corrupted run from before its refused resume;
  - the newest guard-fix and relative-settings runs.
- **What each folder holds:** settings, state, game logs (`eval_games.jsonl`, `selfplay_samples.jsonl`), STATUS/REPORT, identity and pool files, plus the 10 launcher logs. Checkpoints are left out.
- **`inventory.json` / `INVENTORY.txt`:**
  - every file in every folder, 477 in all, with its size, SHA-256 and whether it was copied (131 copied);
  - each run's expected records;
  - the refused and dry-run folder names that were never created.
- **Interrupted attempts:** none exist. Every resumed run shows "absent: never created" for them, because the trainer only makes that folder when a log grew past the last save. [That reason is my reading of the trainer's resume code.]
- **Not logged, by design:** held-out games, and step 0 practice's random-move games. The inventory says so.

**The overlap checker now works from those records** (`practice/seed_overlap_check.py`, which replaces the earlier version that read cloud paths).
- **Paths:** it finds everything from its own location.
- **Records check first:** every copied file must be present with the SHA-256 the inventory lists, and every run folder and file must be listed. Any missing, altered or unlisted record gives "INCOMPLETE" and no overlap verdict.
- **Training bounds:** recorded training seeds must fall inside the computed training bounds (all do).
- **Without the add-on:** it runs where the add-on isn't installed (it only needs numpy), using a stand-in for the game-environment wrapper, which the seed lists don't use.

**Results:**
- **Real stage 1 seeds** (`seed_overlap_check.txt`): records complete, 0 problems; no overlap with earlier runs or with any practice range or game (5,820 exact practice game seeds).
- **Old seeds, as a negative control** (`seed_overlap_negative_control.txt`): 3,480 overlaps. That's more than before because the newer practice runs are now included.
- **Missing-record tests** (`seed_overlap_missing_record_tests.txt`): each of these gave INCOMPLETE:
  - a deleted game log;
  - an altered game log;
  - an unlisted run folder;
  - a missing inventory;
  - a whole run's records missing.

  The checker also ran without the add-on.

To reproduce: `python "results/run5_build/practice/seed_overlap_check.py"` from any folder, with any Python that has numpy.

