# Run 1: a recorded deviation from PLAN step 3, written before any run

Written Oct 19-20, 2026 by the laptop session, on the coordinator's decision. It was written before any live judge call and before any formal row (registered seeds) or kx3 row on the exam. The mocked dry runs of Oct 19 did play the real km3 on the exam positions on dry seeds; that exposure is recorded below.

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
- analysis.py's verdict rule (below): a direction only when the interval excludes 0 AND the sign-flip test over games supports it, otherwise "inconclusive";
- the 2 points of the excluded game in a separate diagnostic block;
- the judge's repeat as a sensitivity estimate only.

The kit is in `run1/` (README_run1.md, run_exam.sh).

## The run-1 pass condition (fixed before any live call; written out Oct 20)
Run 1 **passes** only if the formal PRIMARY PREFIX verdict is **"judge higher"**. That verdict is `analysis.prefix.contrasts[0]` in `report_primary.json`
(a = judge, b = km3), on the 49 primary points from 26 games, from a comparison with `formal: true` and exit 0. analysis.py's existing `verdict()` gives
"judge higher" only when ALL of these hold:
- the 95% game-clustered percentile bootstrap interval of the judge-minus-km3 prefix agreement lies above zero (`ci_low > 0`);
- the sign-flip test over games supports that direction (`sign_flip_p < 0.05`). With 26 games this is analysis.py's fixed-seed Monte Carlo
  sign-flip test (100,000 draws, seed 20261019), not the exact one: analysis.py enumerates every sign pattern only up to 16 games. (Wording
  corrected Oct 20 before the live run, at Astra's note; the method is unchanged.)
- there are at least 10 games with data (MIN_GAMES).

Anything else is **not a pass**: "inconclusive" (the interval includes 0, or the sign-flip test doesn't support the direction) or "km3 higher".
- The full-plan block on the 19 full-scope points is reported separately. It doesn't enter the pass condition, and neither do the repeat (sensitivity),
  the diagnostic block, the category breakdown or any kx3 run.
- This restates analysis.py's rule, which hasn't changed. It's written out because this file's earlier version said it two ways: the method list
  had both parts, but the staged decision said only "interval not above zero".

## The expansion decision is staged (fixed now, before results)
1. **If run 1 does NOT pass** (verdict "inconclusive" or "km3 higher"), the coming week goes to maintenance and upstream work, and no kx3 port is made.
   - That is a **resource choice**, not evidence that the AI approach can't help.
   - An inconclusive result on 49 points from 26 games has low power for small gaps (analysis.py's own note). It also says nothing about other prompts,
     models or uses of the judge.
   - "km3 higher" would be a result about this frozen judge on these points only.
2. **If run 1 passes** (verdict "judge higher"), that is not yet a claim that the judge beats our best bot. kx3 must first be tested formally against the
   judge, on one tree, under a later freeze, before anyone says so.

## kx3 side run: SKIPPED (Oct 20)
- **Why skipped.** The timing probe (below) put the full side run at about 4.4 hours on 3 seeds. That's over the pre-set ~3-hour rule, so it is skipped
  per that rule.
- **No variant.** No 1-seed variant is run (the coordinator's decision). `run1/kx3_side.py` stays in the kit, unrun.
- **For the record only.** The plan and caveats below were written before the probe. With the run skipped, they no longer apply to run 1.

### The side run as planned (not run)
- **When:** only after the formal run, and only if it fit in about 3 hours with no build.
- **Binary:** stage A's existing `~/stageA/bin/pg_pos_blade` (sha256 bbc05e1f8972fccddeee08fbe438414be5d60c464e9114be04c0f8dc5af5b790; built from
  sonnet/ky3-blade 0f5f234d with pgd_patch.py and main's pg_pos.rs, the same source the exam positions were built and checked with).
- **Bot:** code `kx3_r16_c12_z2_real_t0_poolmeta`, on the same seeds 25,100,000,001-003.
- **Labelled plainly:**
  - It isn't verified equal to the frozen pilot. Its kx3 re-scores km candidates by play-outs; its self-check printed F's digest in stage A, but that
    doesn't verify play on these positions.
  - Its engine differs from the formal rows'.
  - Its printer gives bare action names. Rows the harness can't map to exactly one listed plan (for example the 2 Field Blower points) would count as
    unscored, never as a miss and never dropped silently.
- **How it would have been reported:** descriptively, beside the formal result, with no interval or verdict against the judge.

### The side run's two caveats (recorded before any run; the coordinator chose this binary, option 1)
1. **Bare-name labels.** pg_pos_blade's printer writes action names without their target arguments, unlike the frozen baseline's
   `Name#JSON` labels.
   - So a kx3 line can fit more than one listed plan, or none. The 2 Field Blower points (LAD-20261014_234728000_iOS-t5 and
     LAD-20261014_233402000_iOS-t7) may well come out unmapped.
   - Every such row would be UNSCORED: counted and shown, never scored as a miss, never dropped.
2. **A different engine and rules version.**
   - pg_pos_blade is built from sonnet/ky3-blade 0f5f234d, while the formal km3 and judge rows run on the frozen baseline's engine tree 70652fff.
   - Its kx3 is the F pilot's code path, but it isn't verified to play these positions as the frozen F pilot does.
   - So the side run's numbers wouldn't be comparable to the formal judge-vs-km3 result, and they'd support no claim about the judge against our best bot.

**The timing probe** ran on 2 OLD stage A positions, never on the exam, with dry seeds 25,100,900,101-103:
- 37 plans took 92 s and 271 plans took 688 s, about linear in plans.
- The exam lists 6,310 plans in all, so the full side run would take about 4.4 h.

## Dry-run exposure record (written Oct 20, 2026, before any live call)
"No bot ran on the exam" is NOT accurate. The mocked dry runs of Oct 19 played the real, frozen km3 on the exam positions:

**Dry run 1** (started 23:58Z Oct 19)
- It produced 153 km3 rows (51 points × the dry seeds 25,100,900,001-003) and 51 mock judge rows.
- It stopped at the comparison, before any agreement figure was computed (`compare` wasn't given `--positions/--decks`).
- Its console showed row counts only.

**Dry run 2** (started 23:59Z Oct 19, ended 00:00:26Z Oct 20; the kit was committed at 00:01Z as b1caf527)
- It produced 153 real km3 rows on the same dry seeds and 51 + 51 mock judge rows. The mock always answers plan 1 and calls no API.
- It also wrote `report_primary.json` and `report_sensitivity.json` (km3's and the mock's agreement, intervals and verdicts), `by_category.json`, the
  spend and the manifest.
- Its outputs stay on the laptop in `~/exam_run1/dry-20261019T2359Z/`.

**Who saw what**
- Only the laptop session saw any figure, and only what the script printed to the console:
  - the category breakdown: km3's and the mock judge's prefix agreement on the primary points by deck kind, answer kind and deck, with counts;
  - row counts, exit codes, the cost estimate and the mock spend.
- The overall primary and full-scope contrasts in the report files (estimate, interval, sign-flip p, verdict) were never opened. On Oct 20 only their
  field names were read, to write the pass condition. (Those reports' full-scope blocks used the pre-frozen-4 full-plan comparison; see below.)
- No figure went to the coordinator, Astra, Sonnet or Dustin. The mailbox and the session's messages were checked.
- The mock judge's figures are meaningless.

**What changed afterwards: nothing in the judge's prompt or the pass rule.** (Corrected Oct 20 before the live run: an earlier version of this
record, written before the tag, said the harness hadn't moved since the dry run.)
- **Unchanged:**
  - the prompt and its settings (the frozen tag's commit message and FROZEN.json: prompt unchanged);
  - judge.py's call, cost and run-loop code (`judge_one`, `call_claude`, `cost_of`, FROZEN);
  - the exam and its keys: 5518fd60, `references.json` 12e0e997…, `references_meta.json` 6adca41e…;
  - the eligibility (`prep_inputs.py` is unchanged);
  - prefix agreement (plan identity) and the decision rule (analysis.py's `verdict()`, its constants and the bootstrap).
- **Changed in the judge tag after the dry run.** `judge-prompt-frozen-4` is commit 72eea776 (00:51Z Oct 20), Sonnet's final review round on top of
  eb19c7af, the commit the dry runs used. No dry-run figure had been shared with Sonnet, Astra or the coordinator. It changed:
  - **the full-plan comparison** (formal.py `full_plan_agreement`, judge.py `full_match`): a complete turn now agrees when it reaches the same listed plan
    as an accepted move list, and whatever follows a chance event matches label by label. Before, the whole sequence was compared label by label, in
    order. This is the separate 19-point block, not the pass condition;
  - **label reading:** Energy lists are sorted when labels are compared, a malformed label escape is refused, and an ambiguity message is reworded;
  - **compare's bookkeeping:** the "did not finish" stub is written earlier, a warning was added for full-scope points with an incomplete recorded plan,
    and problem counts are grouped by kind;
  - **docstrings and tests,** and FROZEN.json's source hashes.
- **Changed in the kit after the figures:**
  - this deviation record: 2d2a201e, b75b4ee5, a2db950c and this version;
  - `kx3_side.py` (4324945a, never run, now skipped);
  - README text;
  - the written-out pass condition, which restates analysis.py's existing rule;
  - the spend bound, `budget_judge.py`. It changes how calls are scheduled and capped, not a call, prompt or row field. `test_budget.py` checks that
    its rows equal judge.py's own loop's, field for field.

**Why this is baseline exposure, not judge exposure**
- km3 is a frozen, untuned baseline. No km3 or judge code, setting or seed was chosen or changed after the figures. The live seeds were registered at
  main 111ca123 at 23:56Z Oct 19, before either dry run.
- What the laptop session learned is roughly how often km3 agrees with Dustin's recorded moves on these points, on other seeds.
- Nothing about the judge's own behaviour on the exam is known: there has been no live call.

**The live run regenerates km3.**
- `MODE=live` plays km3 afresh on the registered seeds 25,100,000,001-003 into a new folder.
- No dry-run row is reused.
- The dry seeds (25,100,900,000 and up) are never used for a formal row.
