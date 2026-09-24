# Rules4: third point and last Pokemon Knocked Out

September 22, 2026. Status: rules4 is active. The full engine suite, recorded segments, and normal-launcher smoke checks passed.

T2 showed a simultaneous finish that rules3 scored incorrectly. Dustin's last Skarmory ex takes the third point by Knocking Out Team Rocket's Electrode; Destiny Burst Knocks Out Skarmory ex, and the opponent still has two Benched Pokemon. The video ends in a tie. Rules3 gave the attacker a win in both mirrored engine fixtures.

Rules4 adds a narrow terminal check: if exactly one player reaches three or more points, that same player has no Pokemon left, and the opponent still has Pokemon with fewer than three points, the result is a tie. Knock Out effects and both point awards still finish before this check. Existing Energy-choice, defender-bound attack-reduction, and double-KO ordering repairs remain intact.

## Evidence and limits

The [bounded T2 evidence note](T2-evidence.md) records the source hash and four inspected frames. The video establishes one seat orientation; mirrored engine tests provide both-seat regression coverage. The attacker's three points, empty board, opponent's two Benched Pokemon and Tie overlay are visible. The opponent's final two points follow from the Skarmory ex KO; they are not read from the result overlay.

This does not settle the broader community win-condition-counting model. Both players reaching three points when one side is empty, and both boards becoming empty, retain their previous engine behavior. Tests for these exclusions are compatibility controls, not evidence of the app's rules.

## Validation

- The new focused test file has three tests, each exercising both player seats. The recorded T2 case ties; an attacker with a surviving Bench still wins on points; adjacent unconfirmed terminal combinations retain prior behavior.
- Full engine suite: **1,826 passed, zero failed or ignored**, across 101 result groups including doc tests. [Count receipt](full-engine-test-counts.json), [full log](full-engine-tests.log), [build log](engine-build.log).
- Accepted-review corpus: 44/44 constructed segments passed, with 441 outcome assertions and 70 scripted actions. These are bounded segments, not whole-game replays. [Report](replay-evidence/validated-corpus/REPORT.md).
- Replay tool: 16 Python and 32 Rust tests passed.
- The first replay run returned 42 passes and two gaps because its Checkup adapter pins the entire helper source. The Sleep/Burn branch generation and order were unchanged; the compatibility fingerprint was reviewed and refreshed. The guard remains enforced. [Revalidation receipt](replay-adapter-revalidation.json), [original gap run](replay-evidence/final-corpus/REPORT.md).
- The saved candidate completed two k3 smoke games before activation; the normal project launcher completed two more after activation. Its runtime hash matches the release manifest. [Activation receipt](validation/activation.json), [launcher completion](validation/post-activation-smoke/completion.json).
- Project integration board: **32 passed, two pre-existing fixture failures** (`driver_progress`, `run_records`), zero skipped or missing dependencies. They concern the fixtures' compatibility with the current-engine resolver; `run_records` omits `current_engine.py` from its temporary fixture. The same failures were present in the rules3 run. This is not an all-green project board. [Current log](validation/project-gates.log), [details](validation/project-gates-detail.log).

## Preserved source and release identity

The complete 545-file engine source snapshot is preserved and verified file by file. Relative to rules3, exactly four files differ: the terminal helper, its new test file, and the Cargo package version/lock. The version is `0.1.0-pdl.rules4`; executable SHA-256 is `e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415`. [Final release identity](release-identity.json). [Source identity](source-identity.json), [source hashes](source-sha256.json), [source archive](source-after.tar.gz), [repair patch](repair.patch), [pre-fix reproduction](pre-fix-reproduction.log).

The replay harness separately updates its local dependency lock and the reviewed Checkup compatibility fingerprint. Original files are retained in `before/`. Historical engine binaries, source exports, checkpoints, wheels and measurement packets remain unchanged.

The add-on and benchmark refresh is a separate [rules4 recheck packet](../rl-feasibility-2026-09-18/results/astra-review/rules4-addon-recheck-2026-09-22/README.md). No Run 5 training or model/search integration build is part of this repair.
