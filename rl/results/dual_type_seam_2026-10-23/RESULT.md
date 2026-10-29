# Dual Fusion step 1: the printed-type-set seam, night check (Oct 23-24, 2026)

**What was checked:** branch `laptop/dual-type-seam-2026-10-23` at `e57d8678` (engine tree `b1daf33d`), against main-4d48844 (main `b78c8997`, the adopted engine). The coordinator gave the GO on Oct 23 (option (c) step 1: rule-independent and behaviour-neutral, branch only). The run started early, at 19:09Z, because Dustin released the laptop for the day ("Okay I'm done with the laptop for the day and you are free to get started with tonight's work whenever"). Settings: CARGO_BUILD_JOBS 2, nice 19.

| Check | Result |
|---|---|
| Build (deckgym, legality_scan, goldfish) | **PASS**: 314 s. sha256 `7122ec5c…`, `f13d6d21…`, `f73beb86…`. The same 5 warnings as main-4d48844's build, all pre-existing. |
| Generator reproduces `card_ids.rs` and `database.rs` | **PASS**, layout aside: `tools/gencmp.py` gives SAME for both. The lane's first comparison, which only removed whitespace, reported DIFFERS. All 63,906 differing lines are rustfmt layout: trailing commas, `use` order and line breaks. rustfmt is not installed on this laptop. The control (one HP changed by one) gives DIFFERS. With the new field dropped, the generator's output is also SAME as main's files. |
| Full suite (`cargo test --release --features test-utils --no-fail-fast`) | **PASS**: 2,223 passed, 0 failed, 0 ignored (main 2,150). The 73 new tests: `dual_type_seam_test` 23, `dual_type_inplay_test` 28, `dual_type_offboard_test` 20, plus one fuel_credit and one kd unit test. |
| Identity replays v main-4d48844 (side f), game for game | **PASS**: 18 of 18 runs SAME, 156,520 games, 0 differing deals (table below). |
| Python (`lib/test_dual_type_readers.py`; card_canon and deck_check selftests; setup_tester tests) | **PASS**: 28/28; both selftests pass; setup_tester's tests pass on both the branch and main. |

**The identity replays** were run by `tools/replay3.py` (replay2.py of Oct 21 plus side d). Each run replays one recorded reference with the seam's programs and compares every game with main-4d48844's own run (side f). "v ref" compares with the old 08a9b3a-era reference. Where v ref says DIFFERS, side f differs from that reference on exactly the same games: these are main-4d48844's known Growl and #401 changes.

| Run | Games | v ref | v main-4d48844 |
|---|---|---|---|
| 10_cli_k3, kp3, kog3, kta3, km3 (5 runs) | 5 × 240 | SAME | SAME |
| 10_goldfish | page and coverage | SAME | (= ref, as f) |
| table_k3, table_kp3, table_kog3, dev_km3_table, dev_kta3_table (5 runs) | 5 × 14,000 | SAME | SAME (0 deals) |
| 10_run_screen | 3,840 | SAME | SAME |
| new17_k3 | 8,500 | 8 deals | SAME (0 deals) |
| dev_km3_new17 | 8,500 | 7 deals | SAME (0 deals) |
| 8b_cloud_new_k3, 8b_cloud_new_km3 | 2 × 240 | SAME | SAME |
| 8_new_km3 | 16,000 | 1 deal | SAME (0 deals) |
| cov_b2e_km3 | 48,000 | SAME | SAME (0 deals) |

Side f had no run of the kp3, kog3 and kta3 tables yet, so main-4d48844's own games for them were played first, the same night (`ref_F`).

**Not checked here:** rustfmt and clippy, which are not installed in WSL. The two getters left with only the Python binding as caller carry `#[cfg_attr(not(feature = "python"), allow(dead_code))]` so that clippy `-D warnings` stays clean. That fix is inferred, not run.

**Tools** (`tools/`):
- `lane_d.sh`: the night lane.
- `replay3.py`.
- `gencmp.py`.
- `fix_endings.py`: restores each line's original ending after an edit.
- `insert_secondary.py`: the 3,566 `secondary_energy_type: None,` lines in database.rs.

Records are on the laptop in `/home/dacz8976/pincand_work/dual/` and `games/{d,f}/`.
