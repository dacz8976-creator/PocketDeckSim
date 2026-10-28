# Dual Fusion release prep: the night check (Oct 24, 2026, 02:10-05:30Z)

**What was checked:** branch `laptop/dual-fusion-release-prep-2026-10-24` at `9fcffb5c`, against main-4d48844 (main `b78c8997`), the adopted engine.
- The branch is the dual-type seam, plus B4b + P-B card data (upstream dfe6ff30, the data-pin dry run's), plus the scripted id arms for the 82 B4b Trainer reprints (coordinator-035, option (b)).
- Settings: CARGO_BUILD_JOBS 2, nice 19.

| Check | Result |
|---|---|
| Build | **PASS**: 323 s, with the same 5 warnings as main-4d48844's build, all pre-existing. |
| The generator reproduces `card_ids.rs` and `database.rs` | **PASS**, layout aside (`tools/gencmp.py`: SAME for both; 3,922 `secondary_energy_type: None` lines). |
| card_status | **PASS**: 4,317 cards. All 438 new ids (B4b, P-B 091-099) are Complete; 0 B4b Trainers have a status other than their base printing's. |
| The full suite | **PASS**: 2,228 passed, 0 failed, 0 ignored. That is the seam's 2,223 plus `b4b_reprint_arms_test.rs`; `card_status_cli_test` pins 4,317 cards. |
| Identity replays v main-4d48844 | **PASS**: 18 of 18 runs, 156,520 games, 0 differing deals. These are the same runs as the seam's check (`RESULT.md`): CLI ×5, goldfish, the five tables, run_screen, new17 ×2, 8b ×2, 8_new_km3 and cov_b2e_km3. Where a run DIFFERS from the old 08a9b3a reference, main-4d48844 differs on the same games. |

**So:** appending B4b + P-B and giving the reprints their arms changes no game of the current decks. Every new card is playable in the engine. Release night only has to take C1's data (`RELEASE_CHECKLIST.md`, R1-R8).

**Not checked here:** rustfmt and clippy (not installed in WSL). The edited match arms are single lines of up to about 150 characters, which `cargo fmt` would reflow.

**The record on the laptop:** `/home/dacz8976/pincand_work/prep/` (lane log, card_status.json, suite log) and `games/r/`.
