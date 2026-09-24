# Astra launcher follow-up, September 23, 2026

The two reported gaps are closed in launcher SHA-256 `8719482758d5bed2c922698a270564fd83fa8100c08b31763185a21b64e21a14`. One settings-path gap remains. No production code, settings, environment or run folder was changed, and no training was launched.

## Verified guard coverage

Twenty-three focused guard checks passed: both modes, non-standard folders with real seeds, protected real-folder aliases, trainer overrides and abbreviations, malformed numeric arguments, normal launches and practice settings. This was a fresh table, not the builder's exact 22-case harness.

The temporary launcher was byte-identical. A fake Python environment made installation and module probes inert; the trainer command was captured and exited with code 77 before any trainer execution. This verifies guard decisions and forwarded arguments, not training or installation. [Evidence, including the inert stub and captured arguments](practice/astra_guard_review_20260923.json).

## Finding: relative settings can select two different files

Line 61 keeps `SETTINGS_FILE` relative. Lines 79-88 check the file and its practice seeds in the caller's folder. Line 113 changes to the project root. Line 116 then reads `cat "$SETTINGS"` again for the trainer, relative to the project root.

Reproducer: both folders contain `same-settings.json`. The caller's file uses practice seeds starting at 9,000,000,000. The project-root file uses the real stage 1 settings, including training at 6,000,000,000 and k3 at 83,000,000. With a practice run folder, the guard accepts the caller's file but the intercepted trainer receives the project-root file and its real seeds. No trainer executed. An independent source review confirmed the mismatch.

Fix: resolve the settings path once before validation, retaining its intended caller-relative meaning, then use that same absolute path for the trainer input. Add a regression case with the same relative filename in both folders and different seeds; inspect the exact settings passed on. The production launcher remains unchanged by this review.

## Seed-overlap evidence still needed

The saved overlap results are local, but the raw cloud practice runs are not. The checker also has hard-coded cloud paths that need adapting to the exported evidence root.

Copy every cloud practice run into the existing practice evidence area, preserving names and subfolders:

- each run's `settings.json`, `state.json` and `eval_games.jsonl`;
- each `interrupted_attempt_*/eval_games.jsonl`;
- the discarded trace/draw-gate attempt and latest `practice-stage1-guardfix` run;
- a complete directory/file inventory, explicitly identifying missing or never-created records.

Checkpoints are unnecessary for this seed check. The checker silently skips runs missing settings or state; an incomplete inventory must not be accepted as no-overlap evidence. Training ranges are conservative bounds from settings and resume state. Held-out ranges come from the configured formula rather than logged games. The saved no-overlap result remains builder evidence until the raw records are available for an independent check.
