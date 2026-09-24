# Run 4 memory-fix review
September 21, 2026. Audit only. The submitted trainer's cache change passes review. The complete restart procedure needs the helper and practice-test corrections below before approval. No patch was installed and no training or identity amendment was run.

## Reviewed identity
- Original/live trainer: e05c1e3aed33437832e6c16dfecd0952318b267dfe5e4a6bb79494f660aaa339.
- Patched trainer approved for its memory change: 74d54db888a830fe296cc107131829019c039e624917370667d4faab0420e80f.
- Supplied helper: ea3a895920d53d66aebd8acef8716e7346c5dd21ecac4dceb12d98f3559aa298.
- Downloaded zip: 85aa54b8bd2c2769ad811ad4d30de88cff24a8767f0ae4014761b72b6daf1741.

The packaged original matches the live file exactly. AST comparison confirms only actor, _eval_init and _net changed among existing functions; load_scorer, NetCache and cache constants were added. Opponent draws, full pool eligibility, seeds, learner update logic, stopping/pass rules and resume behavior are unchanged by this trainer patch. Current actor networks still allocate optimizer arrays; the past/evaluation caches drop them. load_scorer also creates optimizer arrays transiently before releasing them. These are bounded overheads, not blockers for this fix.

## Independent checks passed
Using the installed Run 4 add-on and actual saved checkpoints:
- 80 loads across all 40 checkpoint files, with a three-entry cache and repeated eviction, produced bit-identical parameters and scores. Scorers retained no optimizer arrays.
- 300 fixed games spanning all five decks, both seats, random/k3 opponents and checkpoints 1M/2M/3M were run through each of original, patched cap 10, and patched cap 1. All 900 executions matched the same 300 reference outcomes, points, turns and full recorded moves exactly. Result SHA-256: 7db83524e6aed5f908d45e9dd09e7896b24c74bf595e1240651e42824b270e02.
- Fresh-process memory checks loaded 80 distinct cache entries using the 40 existing files twice. Past cache held at 40 and about 120.4 MiB added RSS; evaluation held at 10 and about 43.8 MiB. Memory flattened after filling, with no growing tail. These are single-cache measurements, not an eight-worker production guarantee.

## Required corrections before using the restart procedure
### P2: acquire the lock before reading the run
accept_trainer_change.py:40-63 reads/validates identity, state and settings before obtaining run.lock at :65-69. It writes those snapshots back at :75-80. A concurrent process can finish a commit in between, leaving a stale snapshot to overwrite the newer state.

Reproduced with the exact helper main() and disposable JSON fixtures: during input-identity checking a simulated second writer successfully took the run lock and advanced the fixture to games=3,500,000/resume_epoch=1. The helper later accepted the change and wrote games=3,000,000/resume_epoch=0 over it. This is a test injection, not something observed in the real run. Resolve run_dir, acquire its lock, then read and validate mutable run files while holding it.

### P2: make amendment retries recover incomplete writes
accept_trainer_change.py:75-80 writes history, then identity, then the state flag. Interruption after replacing identity leaves a valid new identity but no flag; original-argument retry refuses, and new/new reports nothing to do.

Reproduced by injecting an exception immediately after the real atomic identity replacement in a disposable fixture. The new hash and one history record survived, but flags remained empty. Provenance is not entirely lost because history was written first; the incomplete update nevertheless cannot repair itself through the documented retry.

Minimal correction: write history and state flag idempotently, then make identity.json the final commit marker, with retries reconciling a partially recorded same change. Test interruption after each write and ensure no duplicated records/flags or missing record. No broad identity-guard bypass is needed.

### P2: repeat the practice chain without colliding checkpoints or hidden failures
The practice script schedules checkpoints every 500 games, while the trainer names them with at // 1000. Its 24 checkpoints produce only 13 distinct event names; ckpt_1k through ckpt_11k each occur twice. Files get overwritten while caches may still hold the earlier weights under the same path. Consequently the supplied full-chain results do not establish clean checkpoint/audit/report behavior.

Use distinct checkpoint names through a test schedule such as 1,000-game intervals; no production naming change is needed. Run long enough to exceed cache capacity. Also assert command exit status and expected refusal text: test3_chain.sh lacks pipefail and pipes critical commands through grep/tail, so CHAIN DONE is not a success guarantee. Expected abrupt-exit tests must explicitly accept only their intended exit codes. The REPORT grep | head check also cannot detect the missing note as written.

## Reporting decision
Yes, include the trainer-change and resume notes in REPORT.txt. The submitted report lacks them, as Opus disclosed. STATUS and identity_changes retain useful evidence, but the final report should stand alone. This is reporting scope; it need not alter the trainer hash. Correct the helper's claim that the final report already shows the flag.

## What remains approved and unchanged
The cache implementation can be retained exactly at the reviewed patched hash. The helper's checks for all other recorded inputs, Python/NumPy and an already-held lock passed isolated refusal tests. The fixes needed are in amendment handling and practice evidence, plus the requested report note. Do not rerun the whole scientific training experiment to test them.

At review end, the live trainer and recorded identity were still the original hash; the real run remained at 3M, resume_epoch 0. Preserve the original source/identity history and interrupted 3.5M files when a corrected procedure is later used. This report does not authorize starting training.

Evidence and submitted source snapshots: memfix_review_20260921/evidence.json and memfix_review_20260921/submission/. Local test harnesses and all three evaluation result files are retained alongside them. The cloud full-chain practice was inspected, not rerun locally; its corrected rerun remains outstanding.
