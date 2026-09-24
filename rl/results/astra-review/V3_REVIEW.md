# Astra audit of Run 3, September 19, 2026

Audit only. No project source edits, training, full game audit, or optional laptop smoke run was performed. Three actionable P2 findings are below. The pass rule, ordinary crash/resume handling, pairing draw, and requested strict/winnable split passed the focused checks. This is an add-on/training/report review, not an engine-rules audit.

## 1. P2: worker seed blocks can overlap before the 20M cap

`train_v3.py:810` spaces workers by 10,000,000 seeds, while line 242 adds each worker's uncapped local game index. Run 3 raises the total cap to 20,000,000 and still allows `--workers` to change.

Concrete collision within one resume epoch:

- Worker 0, local game index 10,000,000: seed **3,010,000,000**.
- Worker 1, local game index 0: seed **3,010,000,000**.

For example, a two-worker run can reach that point if worker 0 completes more than half of the 20M games. The shared claim counter limits total games, not each worker's range. This is an arithmetic/code-path counterexample, not an observed duplicate in an executed training run. It is unlikely in the intended eight-worker run if the run levels off early, but the claimed guarantee that seeds never overlap is not true under the supported cap and worker settings. Reuse can repeat a seeded start when the deck placement also matches.

Fix: allocate gameplay seeds from the unique claimed game ID, or reserve a per-worker range at least as large as the maximum number of games any one worker can play and reject unsupported worker/epoch combinations. Verify the end of a permitted worker range against the next range. The existing resume-epoch reservation avoids reusing an epoch after an ordinary restart for the default worker count.

The evaluation domains themselves are separate, and do not overlap training:

| Purpose | Actual seed bounds | Game specifications |
|---|---:|---:|
| Checkpoint vs k3 | 80,000,000 to 80,950,999 | 20,000 |
| Random | 81,000,000 to 81,000,499 | 500 |
| Previous checkpoint | 82,000,000 to 82,001,999 | 2,000 |
| Bars / confirmation | 90,000,000 to 90,900,999 | 10,000 bar, 20,000 confirmation |
| Held-out | 95,000,000 to 95,900,999 | 10,000 bar, 20,000 network |

These are bounds over separated blocks, not continuous use of every seed between them. Bar/confirmation seed reuse is intentional: each bar serves both directed matchups. All 20,000 confirmation specifications matched their bar's seed and deck placement, with 500 games per seat per direction. Held-out pairing passed the same checks.

## 2. P2: failed replays are included in a completed, cached audit

`audit_v3.py:162` counts `ok == false`, but line 163 still tallies every replay. Lines 184-185 write a normal result, and the next invocation skips that result at lines 155-158. `report_v3.py:43-44` includes its summary without rejecting it.

A synthetic probe executed the real audit main with one failed confirmation replay and one successful bar replay. It wrote `replay_problems: 1`, included the result in the statistics, and skipped the unchanged file on the next call. The summary DOES expose the problem count; the issue is accepting and caching invalid statistics as a completed step, not hiding the count.

Fix: refuse to mark the audit complete while any replay fails, or exclude invalid games and label the output incomplete so the launcher/report cannot treat it as finished. Add a failed-replay case to the skip/resume checks. This affects audit credibility; the audit is not one of the four training pass conditions.

## 3. P2: report resume reuses results without validating their inputs

`transfer_v3.py:52-55` skips solely because a filename exists. `audit_v3.py:155-158` does the same. The output identity omits the deck/checkpoint/evaluation/report-code hashes needed to check whether that cached result still applies, and `report_v3.py:43-48` trusts those filenames. The trainer also returns immediately for an ended run at `train_v3.py:684-686`, before its identity comparison; `input_identity()` at 667-673 does not hash the held-out decks.

A synthetic probe created an existing transfer result, changed the temporary held-out deck's bytes, and called the real transfer main. It printed `exists; skipped`, left the old result unchanged, and returned before even loading the current decks. Thus an interrupted report chain can reuse old steps and run missing ones against newer input bytes. This matters when deck lists or scripts are updated between the long run and resumed reports, as happened with shared inputs earlier in this project.

Fix: bind each report artifact to its actual deck bytes, source checkpoint, evaluation records, relevant settings and report-code identity. Validate before skipping or including it. On a mismatch, refuse reuse or explicitly regenerate the affected report. Preserve the existing output as prior evidence. No mixed-input result was observed in the supplied cloud smoke output; this probe establishes the missing protection.

## Requested checks that passed

- **judge():** extracted and executed the actual nested function. Blaziken/Lucario +10.0 points passes and +9.9 fails; either lift matchup below zero fails; the global -5.0 floor passes and -5.1 fails. Tested below-floor values in each of all 20 directions. Confirmation requires every condition to pass within one checkpoint; it does not assemble a pass from different checkpoints.
- **Shared event boundaries:** executed the actual event block with smoke-sized scheduling, mocked evaluations and temporary disk files. Interruptions after the draw gate but before checkpoint creation, and after checkpoint creation but before the shared commit, leave both events pending on resume. A successful boundary saves them once and counts the draw window once; a failed gate saves STOPPED without continuing into checkpoint evaluation.
- **Resume-file deletion:** used real save/load methods and a tiny untrained network. Interrupted before state replacement: old state still references loadable old weights. Interrupted after replacement but before cleanup: new state references loadable new weights. Normal commit leaves one resume file and preserves checkpoint files. These cover process interruption, not sudden power-loss durability.
- **Pairing and seats:** default weights sum to 1. Blaziken pairings total 0.5, distributed 18.932% Lucario, 9.201% Weezing, 11.275% Altaria, and 10.591% Suicune across all games; each other pair is 8.333%. Executing the actual selection block for 100,000 draws gave 19,952 past-checkpoint games, with latest-network seats 9,999 / 9,953. Both self-play and past games followed the same weights and approximately even deck placement.
- **Strict and still winnable:** synthetic calls to the real tally confirmed chosen Q = -0.5 is excluded; -0.499 is included; a high score on a different move does not qualify the chosen move; a retreat offered only on a previous turn does not make this turn strict. The denominator is player-turns with at least one multi-option decision, consistent with this audit's implementation.
- **Runtime identity:** the 0.5.0 wheel matches the one reviewed for v2.1. This review did not change the engine or encoding.

## Evidence and limits

Exact input hashes, helper scripts and probe results are in `v3-review-evidence/`, also packaged as `v3-review-evidence.zip`. The cloud smoke status/report files were inspected as supplied evidence, not rerun. Their recorded audits report zero replay problems. Synthetic report tests replace game replay/pool execution with test fixtures; no gameplay or learning is performed by them. No performance or playing-strength claim is made here.

Suggested disposition: return these three bounded issues to Opus. No defect was found in the specified pass thresholds, the default pairing proportions, shared-boundary saving, or the strict score threshold.
