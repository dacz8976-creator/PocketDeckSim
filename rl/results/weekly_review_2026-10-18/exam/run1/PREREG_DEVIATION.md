# Run 1: a recorded deviation from PLAN step 3, written before any run

Written Oct 19-20, 2026 by the laptop session, on the coordinator's decision, before any live judge call and before any formal or kx3 row on the exam.

## What PLAN said
PLAN.md (rl/results/weekly_review_2026-10-18/PLAN.md, step 3) says to score km3, kx3 and the judge on the same exam positions. It says to report
**the judge-minus-kx3 difference** with a game-clustered interval: the judge "helps" only if that interval sits above zero, and an interval that
straddles zero is inconclusive.

## Why kx3 can't be in run 1's formal comparison
- **No kx player on the official tree.** The official engine tree has no kx player. The frozen judge harness's baseline executable is built from
  engine tree 70652fff and plays only the minimax bots `k<number>` / `km<number>`.
- **The frozen kx3 is on an older tree.** The frozen kx3 is the F pilot (players d513e37b, engine cd20a97a).
- **A port is large.** Playing kx3 under the same frozen identity needs a large port (Sonnet's assessment, Oct 19). It isn't done for run 1.

## What run 1 does instead
**The formal comparison is the judge against km3**, under the same rules PLAN set for kx3:
- one primary judge call per decision, compared paired by decision with km3 (seeds 25,100,000,001-003);
- prefix agreement on the 49 primary points, with full-plan agreement on the 19 full-scope points as a separate block;
- a game-clustered bootstrap over the 26 primary games;
- "inconclusive" whenever the interval includes 0, or the sign-flip test doesn't support a direction;
- the 2 points of the excluded game in a separate diagnostic block;
- the judge's repeat as a sensitivity estimate only.

The kit is in `run1/` (README_run1.md, run_exam.sh).

## The expansion decision is staged (fixed now, before results)
1. **If the judge does NOT beat km3** (interval not above zero), the week's answer is maintenance and upstream work, and no kx3 port is made.
2. **If the judge DOES beat km3**, that is not yet a claim that it beats our best bot. kx3 must first be tested formally against the judge, on one tree,
   under a later freeze, before anyone says so.

## Optional kx3 side run (NOT formal)
- **When:** only after the formal run, and only if it fits in about 3 hours with no build.
- **Binary:** stage A's existing `~/stageA/bin/pg_pos_blade` (sha256 bbc05e1f8972fccddeee08fbe438414be5d60c464e9114be04c0f8dc5af5b790; built from
  sonnet/ky3-blade 0f5f234d with pgd_patch.py and main's pg_pos.rs, the same source the exam positions were built and checked with).
- **Bot:** code `kx3_r16_c12_z2_real_t0_poolmeta`, on the same seeds 25,100,000,001-003.
- **Labelled plainly:**
  - It isn't verified equal to the frozen pilot. Its kx3 re-scores km candidates by play-outs; its self-check printed F's digest in stage A, but that
    doesn't verify play on these positions.
  - Its engine differs from the formal rows'.
  - Its printer gives bare action names. Rows the harness can't map to exactly one listed plan (for example the 2 Field Blower points) count as
    unscored, never as a miss and never dropped silently.
- **How it's reported:** descriptively, beside the formal result, with no interval or verdict against the judge.
