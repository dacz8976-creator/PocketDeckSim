# Run 3 fixes: Astra verification

All three original findings are resolved; no new actionable issue found in this verification.

Audit only. No project source changes, learning, actual game evaluation, or laptop smoke run. Compared the corrected trainer with the source preserved in v3-review-evidence.zip; changes are confined to seed allocation, recorded-game selection, independent worker random streams, and report-input tracking. Training settings, pass rules, event batching and resume-file cleanup are unchanged.

## Training seeds: original finding closed

The actual actor claims game_no and increments the shared counter under claim_lock (train_v3.py:266-270), then uses seed_base + game_no for the engine reset (282-293). All workers receive the same base, SEEDS['train'] + resume_epoch * 100,000,000, and separate worker random streams (851-855). This removes the old worker-block collision.

The shared counter starts at the committed game count (839). The startup guard rejects either a budget or checkpoint of 100,000,000 or more (681-682). With the supplied schedule, every claim is below 20,000,000; each resume epoch therefore occupies a disjoint range. Resume increments and saves the epoch before any worker starts (739-744), including if that resumed attempt itself is interrupted. Training remains above the evaluation seed ranges.

Independent probes ran the actual actor with mocked completed games and an inert model, not a copy of the allocator. Seven cases issued 31,000 claims using 2, 3 or 8 workers: initial allocation; both sides of the old 10M overlap boundary; the 20M cap; pre-crash work; resumed work; a second resume; and the highest permitted cap boundary. Each case produced exactly the expected contiguous seed range, no duplicates, matching recorded and reset seeds, and no claim beyond its limit. The interrupted and resumed attempts had disjoint seeds.

The real startup guard accepted the default and 99,999,999 cap, and rejected a 100,000,000 budget, larger budget, and checkpoint at 100,000,000. The real resume branch reserved epochs 1, 2 and 3 on disk before the evaluation pool or actors could start, with worker counts 2, 8 and 3. These tests stopped before actual games or learning.

Evidence: pdl_v3_fixed_seed_probe.py, seed_checks.json, pdl-v3-fixed-seed-check.log. Source identities match the prefixes in the supplied cloud check log. Independent tests support its seed fix; the supplied 9,000-game cloud practice run was reviewed as supplied evidence and was not rerun.

## Replay failures: original finding closed

The audit now passes only successfully reproduced games to tally (audit_v3.py:179-181). Any failed replay sets complete=false, appears in replay_problems/failed_games, and is called INCOMPLETE in the summary. Cached output is skipped only when its inputs match and complete is true (167-175). A replacement preserves the old artifact as superseded. REPORT.txt marks incomplete audit output as a report problem; it does not present that audit as finished.

An independent three-call synthetic probe used the actual audit entry point with mocked replays. A failed confirmation produced replay_problems=1, complete=false and no contribution from its decision to statistics. The second call replayed the records again, retained the incomplete file as superseded, and produced complete output. The third call skipped the unchanged complete result. The report loader identified the incomplete result as a problem.

## Cached inputs: original finding closed

Report fingerprints bind checkpoint name and bytes, the decks and settings the step uses, shared and step code, and the installed add-on (train_v3.py:189-202). Audit also binds its source records. Transfer creates fresh games from fixed specifications, so it has no source-record input. Both held-out decks are included in identity.json (708-715); transfer checks all seven decks before cache use (transfer_v3.py:56-65). report_v3.py:18-28,62-74 independently recomputes the expected fingerprints before including cached output.

A synthetic sensitivity matrix changed checkpoint bytes, pool deck bytes, relevant settings, shared code, step code, add-on bytes, and audit records. Each relevant change altered the fingerprint. Held-out deck changes altered the transfer fingerprint and were refused by the run-identity check. Superseded audit artifacts were preserved in the rerun probe; the corresponding transfer preservation path was inspected.

Wording note, not a remaining defect: the knockout audit checks and fingerprints its five pool decks; the held-out test checks and fingerprints all seven. FEASIBILITY.md:643-645 and the handoff's blanket statement that every report artifact binds seven decks are broader than the implementation. The dependency scope is correct: held-out decks do not enter the knockout audit, and a changed held-out invalidates transfer/report output.

## Launcher and conclusion

The launcher guards audit and transfer failures separately before running report_v3.py (run_training_v3.sh:30-35). Shell syntax passed. A focused shell test using the same pipefail/tee/error-handler control flow made both report steps fail with nonzero exit codes and still reached REPORT_RAN. This is control-flow evidence, not a rerun of the full installer/launcher or its actual game evaluations. The supplied cloud end-to-end launcher evidence in results/v3_fixes_check.txt was reviewed separately.

All three original findings are closed. No new actionable issue was found in this bounded verification. No training was launched. The five reviewed source files were unchanged throughout the audit and matched the code identities reported in the supplied fix-check output. Full independent evidence, helper code and source snapshots are preserved in v3-fix-verification-evidence.zip; input_sha256.json records exact reviewed identities.
