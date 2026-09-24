# Run 4 memory fix — the three corrections, and the report history (Opus, September 21)

Your review of `V4_MEMFIX_REVIEW_20260921.md`, point by point. **The reviewed trainer is unchanged**
(`74d54db888a830fe…`). Nothing live has been swapped: the folder's `train_v4.py`, `report_v4.py` and the run
itself are as you left them. Everything below is review copies in `results/run4_memfix/`, plus the three
files that go live after your confirmation, at the package root.

## 1. Lock before reading the save — fixed

`accept_trainer_change.py` now takes `run.lock` first. It reads `identity.json`, `state.json`,
`settings.json` and `identity_changes.json` under the lock, and holds it through the last write.

**Reproduced, then fixed** (`helper_checks/test_helper.py`, check 1). The test stands in for a trainer
saving at 3,500 in the gap between the helper starting and locking. The reviewed helper wrote back its
3,000 snapshot and lost the trainer's flag. The corrected one keeps 3,500 and the flag.

## 2. An interrupted approval is recoverable — fixed

The rule is now: **if it's interrupted, run the same command again.** Three writes, in this order, each
skipped if already done:
1. the record in `identity_changes.json`;
2. the flag in `state.json` (its text is built from the record, so a re-run produces the identical flag);
3. the new trainer hash in `identity.json` — last, because it's what lets the run resume.

If `identity.json` already shows the new trainer, the helper carries on only when a matching approval is on
record. Otherwise it refuses. Writes are temp file, then fsync, then `os.replace`.

**Reproduced, then fixed** (checks 2–4). The helper is killed after each write in turn, then the same
command is run again:

| killed after write | reviewed helper, same command again | corrected helper, same command again |
|---|---|---|
| 1 | completes, but **records the change twice** | completes: 1 record, 1 flag, new trainer |
| 2 | **refused**; trainer accepted, flag missing (your case) | completes |
| 3 | refused | "Already accepted", nothing changed |

Running a completed approval again is a byte-for-byte no-op. Refusals all hold: wrong `--from`, wrong
`--to`, a finished run, any other changed input, and the new trainer already recorded with no approval on
file. Totals: reviewed helper 5 of 10, corrected helper 10 of 10 (`on_reviewed_helper.out`,
`on_corrected_helper.out`, `helper.diff`).

## 3. The practice chain, redone — all 22 checks pass

`practice2/practice2.py` is a Python driver with no pipelines. Every step's exit code and outcome is
asserted, and it stops at the first failure. Full output is in `practice2.log`. Checkpoints are 1,000
games apart, 20 of them to a 20,000 cap, so there are no duplicate names.

- **A.** The original trainer (`e05c1e3a…`) crashes at 3,200: exit 3, last save 3,000, still RUNNING.
- **B.** The patched trainer's plain resume is refused, and the save is untouched.
- **C.** The helper refuses a wrong `--from` and a wrong `--to`, and neither writes anything.
- **D.** With the right hashes, it's accepted: one record, one flag. The same command again changes nothing.
- **E.** Resumed on the patched build, then crashed again at 11,300: last save 11,000, resume flagged.
- **F.** Resumed again and finished at 20,000 (exit 0, FINISHED), with the second resume flagged.
- **G.** The report steps ran: 10 audits, all complete, and the held-out test. REPORT.txt has no problems
  line and carries the trainer change (both full hashes) and both resumes.
- **H.** 21 checkpoints with 21 distinct names, and all 105 weight files present.

**Memory, trainer plus all workers, sampled every 10 s (MB at each save):**
- Segment E: 3k 720, 4k 781, 5k 810, 6k 836, 7k 865, then **873 at every save from 8k to 11k**.
- Segment F: 11k 835, 12k 865, then **869–875 from 13k to 19k**, with up to 105 distinct networks in
  the opponent pool.

**Two corrections to my earlier note.** Because of the name collision, its practice run had 12 distinct
checkpoints, not 24, so the opponent pool reached 60 (checkpoint, deck) pairs, not the 120 I claimed. Its
"flat from the 7,000 save" also came from a pool that stopped growing, which proves less than it seemed.
The run above replaces that evidence. The name collision affects the practice settings only: run 4's
checkpoints are 500,000 apart (`ckpt_500k`, `ckpt_1000k`, …), all distinct.

## REPORT.txt carries the history — done, as you asked

`report_v4.py` gains a "Run history" block near the top: every flag the run recorded, in order, then each
entry in `identity_changes.json` with both full hashes and the reason (`report_history.diff`). A run with
none says so in one line. `report_v4.py` isn't among the run's recorded inputs, so changing it can't affect
the resume, and the audit and held-out fingerprints don't include it.

## After your confirmation

1. **Opus** saves `train_v4.py` (`74d54db888a830fe…`), `accept_trainer_change.py` (`c8b1e376e3ecba58…`) and
   `report_v4.py` (`d9b73968496dda28…`) into the folder, keeps the original trainer as
   `results/run4_memfix/train_v4.run4_original_0-3M.py`, and verifies all four on the laptop by hash.
2. **Dustin**, in WSL, runs one line. If it's interrupted, he runs the same line again:
   `~/.cache/pocket-deck-lab/run4-venv/bin/python "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/accept_trainer_change.py" --run runs/pool5-v22-perdeck-01 --from e05c1e3aed334378 --to 74d54db888a830fe --reason "memory fix: capped weights-only network caches (Astra/Fable, Sept 21)"`
3. **Dustin** runs the usual launcher line. It resumes from 3,000,000 under the run's unchanged rules.
