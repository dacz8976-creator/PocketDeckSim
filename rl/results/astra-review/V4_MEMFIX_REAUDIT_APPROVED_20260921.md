# Run 4 memory fix: re-audit approved
September 21, 2026. The corrected package passes review. No remaining blocker was found in the reviewed memory fix, amendment helper or corrected practice/report procedure. This approves the specific files below for the documented continuation from the committed 3,000,000-game save, with the existing eight workers, 6M cap, seeds, opponent pool and pass/stopping rules.

## Exact approved files
- train_v4.py: 74d54db888a830fe296cc107131829019c039e624917370667d4faab0420e80f
- accept_trainer_change.py: c8b1e376e3ecba58bcdd1df50f04960c57c72c1c91856548796d4f0ba5c2e853
- report_v4.py: d9b73968496dda28f01e3a3c1ed8c56dfd1e88b0480e093b400bd4f91386695e
- Original trainer to preserve: e05c1e3aed33437832e6c16dfecd0952318b267dfe5e4a6bb79494f660aaa339
- Reviewed zip: 6ee325c37a703a0ee42bdbe9fe3e837469a989cbf14de65fcb71cd6557ad6a93

## Prior findings closed
1. The helper now acquires run.lock before reading mutable run data. Independent replay of the race test preserves the newer game count, resume epoch and preexisting flags.
2. History and the run flag are now written idempotently before identity.json, the final acceptance marker. I independently injected interruption after each of the three atomic writes, reran identical arguments, and verified exactly one history record and one flag. A further retry changed no JSON bytes. Changed inputs, wrong hashes, finished runs, an occupied lock and an already-updated identity without an approval record were correctly refused. All 21 local checks passed using the real runtime/input identities and disposable run fixtures.
3. The corrected practice driver checks return codes and outcomes directly. Its supplied evidence shows 22 successful assertions, original-to-patched recovery, a second interruption/resume, a 20,000-game completion, ten complete audits, held-out testing and reporting. A 1,000-game schedule produces 21 unique checkpoint names including the initial checkpoint and 105 weight files. The earlier filename collision is gone.
4. The final report now includes the amendment with both full hashes and both resumes. The report diff is confined to history presentation.

The trainer bytes are identical to the cache patch already reviewed. The prior independent tests therefore still apply: exact parameter/score equality across repeated loads, 300 fixed evaluation games per version with full move equality, and bounded memory through 80 cache loads. These costly game tests were not repeated without a trainer change.

The new practice memory traces show separate resumed segments leveling off after cache warmup. They support the remedy, but do not guarantee a particular eight-worker production memory peak. Cloud practice evidence was inspected; its underlying checkpoint files were not in the package, and the full training chain was not repeated locally.

## Actual laptop readiness
At final verification the live trainer and identity were still the ORIGINAL hash. The run remained at 3M, resume_epoch 0; its lock was free. All five resume archives still match the hashes validated after the crash. All other recorded code, add-on, deck and Python/NumPy identities matched during the local helper tests.

Thus the package is approved, but launching the existing folder as-is would still use the unfixed trainer. Complete the documented preparation first:
1. Install the three exact approved files, preserving the original trainer, and verify the installed hashes.
2. Use the corrected helper with the recorded original and approved new trainer hashes to record the amendment. If interrupted, repeat the same command. Do not alter settings or other identity entries.
3. Resume with the usual launcher. Normal recovery returns to 3M and preserves uncommitted 3.5M checkpoint files separately.

No files were installed into the live program, no real identity was amended, and no training was started by this review. Only review artifacts and temporary tests were written. This approval concerns the memory repair and recovery procedure; earlier engine-rules caveats remain separate.

Evidence and submitted source snapshots: memfix_fixes_20260921/reaudit_evidence.json and memfix_fixes_20260921/submission/.
