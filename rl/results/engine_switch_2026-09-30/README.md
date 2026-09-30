# The kta/km engine switch (Sept 30): main-9b4df9b → main-d363ba8

**Dustin, Sept 30** (verbatim in RUN5, km, "The official engine switch carrying kta and km"): prepare now; "Yes, pin if all pass (Recommended)"; the default pilot "km3 (Recommended)"; the rules items "Keep them out (Recommended)". A mismatch would have stopped the switch with the manifest untouched and gone to him first. The plan he answered: `PLAN.md`.

**What changes in engine/** (`git diff --stat 9b4df9b d363ba8 -- engine`): players only, `players/mod.rs`, `players/public_pricing_player.rs` and `players/value_functions.rs`. `engine/` is B's tree 9c84fef exactly. The rules code is unchanged, so the rules-side steps (the repair mechanic check, the refactor check, new frozen k3 and kp3 tables) don't apply; any rules item comes in a later switch under the full procedure.

## Preparation (`prepare.sh`; `PIN_STATUS.txt`)

- Built `deckgym`, `legality_scan` and `goldfish` from `git archive` of 14c39f4 (main plus 53fc5a1).
- **Identity** (`identity_check.txt`): each replay matched by (pairing, game number), counts asserted.

| pilot | reference | games | result |
|---|---|---:|---|
| kta3 | ec7e1a8's fresh games, `kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl` and `_new17` (the only replay never played at B) | 14,000 + 8,500 | identical |
| kta3 | ec7e1a8's development games, `kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl` and `_new17` | 14,000 + 8,500 | identical |
| km3 | B's games, `km_tables_2026-09-30/1f6319e_km3_table.jsonl` and `_new17` | 14,000 + 8,500 | identical |
| k3, kp3, kog3 | the Sept 28 pin's references | 14,000 each | identical |

- The suggested extras (kq3 on the table, kog3 on the 17 new cells, kd3, kpr3) are reported beside in the same file when run (EXTRAS=1, the default; `PIN_STATUS.txt` says whether they ran). The plan didn't require them, but a difference there would still have stopped the run.
- `deckgym simulate`, 240 games on seed 7,100: k3, kp3 and kog3 repeat Sept 28's lines (150/90/0, 144/96/0, 149/91/0); kta3 and km3 run. goldfish `--coverage` runs.

## The pin (`pin.sh`, run once after PREPARE DONE)

- **Merge:** 53fc5a1 into main as d363ba8, a merge commit with parents main and 53fc5a1 (as a `--no-ff` merge makes one), made off-tree with git merge-tree and commit-tree. Main had moved since the candidate, so `pin.sh` made main's merge commit itself; its `engine/` equals the built candidate 14c39f4's byte for byte. 14c39f4 is kept only on the laptop (`refs/pocketdecksim/engine-switch-candidate`; not a branch, not pushed); elsewhere, build from main's merge commit, the same `engine/`. Nothing outside `rl/results/` and `engine/src/players/` came along, and nothing was deleted (the MERGED line in `PIN_STATUS.txt`).
  - It brings the cloud's build and identity records onto main (`km_build_2026-09-29/`, `-09-30/`, `kt_kog_2026-09-28/`).
  - It also replaces existing records on main with the cloud branch's later versions: 5 files, `rl/results/koh_2026-09-28/BUILD.md`, `rl/results/kph_2026-09-27/BUILD.md`, `rl/results/kt_2026-09-26/BUILD.md`, `rl/results/kt_2026-09-26/README.md`, `rl/results/tool_turn_effect_census_2026-09-25/tool_census.rs`. Checked Sept 30 against main d353621, these were kt's registration (`kt_2026-09-26/README.md`: main's older "RE-ISSUED ON KOG" text gives way to amendment 2 and the withdrawn amendment 3, the text that main's `kta_2026-09-29/REGISTRATION.md` already cites as kt's source), the `BUILD.md` notes of kt, koh and kph, and `tool_turn_effect_census_2026-09-25/tool_census.rs` (the counter tool's extension from km's build round).
- **Programs:** copied to `rl/engine-2026-09-30/` with `SHA256SUMS`, the same hashes as the tested build, committed executable (mode 100755). In the manifest, main-9b4df9b moved to the history as superseded. `current_engine.py` resolves the new program.
- **Screen and floor:** both default to km3 (`run_screen.py`, `floor.py`, together; the calibration reads both and finds km3).
  - `floor.py`'s pricing-pilot pattern now matches every code B builds as a public-pricing player: kp, kq, kd, kpr, koa, kob, kor, kpf, kpg, kog, koh, kph, kpha, kphb, kt, kta, ktb, ktc and km, at any depth, and not k3.
  - Before, it matched only kp, kq, kd and kog, so under kta3 or km3 the floor would have flagged kp's 62 audited cards as unpriced, with no error.
  - `decks/screen/test_floor_pricing_pilot.py` lists those codes and checks them against `players/mod.rs`; `floor.py --self-check` now asserts that the floor's own pilot is a pricing code.
- **The floor's pre-use re-check under km3:** planned in `../floor_recheck_2026-09-30/PLAN.md`, committed with the pin, before any of its games.

**Name change to know about:** in the official program, `kt3`, `kta3`, `ktb3` and `ktc3` are the kog-based presets since this switch (kta3 the adopted one; kt3, ktb3 and ktc3 diagnostic, with no identity claim). The kp-based records (`kt_2026-09-26/identity/43cef0b_*`) replay on `rl/engine-2026-09-28/`, which is kept unchanged.

## After the pin

- **Before Push origin:** Fetch origin in GitHub Desktop. If it then offers Pull origin, origin/main has commits main lacks; ask the laptop session before pulling. `pin.sh` prints whether origin/main, as last fetched, is behind main.
- **After the push:** tell Sonnet's calibration task, and the cloud through Dustin's paste block, that the official engine is main-d363ba8 (`rl/engine-2026-09-30/`) and the working pilot is km3 on both sides of the screen and the floor. Take main before any screen, floor or calibration run, and start a new `--out` rather than resuming a kog3 file: its rows are for another engine and pilot, so they don't carry over.
- **The floor's pre-use re-check:** `bash rl/results/floor_recheck_2026-09-30/run_check.sh` (about 1 hour). If it fails, the floor isn't used until Dustin has seen the pages.
- **Left for a follow-up:** two labels still say kog3, the brew scorecard's header in `decks/screen/panel_ladder_2026-09-26/build_brew_scorecard.py` and `run_calibration.py`'s docstring. They are labels, not checks.

## Next switch backlog (rules items, kept out of this one by Dustin's word; each needs the full procedure)

- **Victory Star / Confusion repair** (`rules/09`). The cloud's drafts are 6415e39 and d4fbc2a on its branch.
- **Coin-flip prevention + Chase Order repair.** The cloud's draft is e52a73b on its branch.
  - Sonnet's independent second read (local branch sonnet/repair-review, 4d45dae, `SECOND_READ_sonnet.md`) found both ready for the laptop's switch review, with no blockers.
  - For that switch's replay: the kd follow-on one-line changes in `persistent_defender_damage` (`rules/09`) must travel with it, and one non-kog3 bot must be run through the cloud's scratch decks.
- **Upstream 09e964f's two knockout-promotion fixes** (`rules/09`, `engine/UPSTREAM.md`). They are not a clean pick: they bring observation and serde changes.
- **PR bcollazo/deckgym-core#383** (Heavy Helmet, Harden, Hide, Blocking Shell), if upstream merges it.
- **B4b card data** (upstream 9044ff6, reprint-only), pinned to Mega Garchomp ex's release.
