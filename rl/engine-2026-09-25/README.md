# The official engine from Sept 25, 2026: main-7fc6ccb

**What changed:** these two programs are now the project's official engine (`project_manifest.json`, `available_release`). `current_engine.py` and `decks/screen/run_screen.py` resolve to them.

**Why:**
- Dustin approved switching to a build from the merged main, on the condition that it pass an identity replay first. The conditions were met at 10:49 on Sept 25.
- The switch was needed because the plan makes kp3 the screen's pilot, and the previous official program (rules4, `rl/addon-0.7.2/deckgym`) has no kp3.

| file | sha256 |
|---|---|
| `deckgym` (the command-line engine; `deckgym simulate`) | `f4d235e596cdd713546c17450fd66bd9d5eefe4baf53e93d66d8bbe1628e1034` |
| `legality_scan` (the table tool; per-game output with `--games-out`) | `d5c0a9528e076299875ac603667f7076951de885ea8465f3be0d1089b5afbbfb` |

**Source and build:**
- git commit `7fc6ccbcecbfeadf19962be2e11b6c570aa7b88d` on main. `engine/` there is identical to 6a38b40, the tip right after PR #1 and the laptop branch were merged.
- Built in WSL on Sept 25 from `git archive` of that commit: `cargo build --release`, and `cargo build --release --example legality_scan`.
- The version string is unchanged at `0.1.0-pdl.rules4`. The game rules are rules4's. What is new is the kp, kd and kq players and legality_scan's per-game output and counters.

**Identity, checked before the switch** (`rl/results/engine_identity_2026-09-25/`):
- **k3:** the new legality_scan replays the table's reference per-game file (`rl/results/per_game_table_2026-09-25/k3_500.jsonl`, 28 pairings × 500 deals) on 14,000 of 14,000 games. Every field matches: decks, seed, first seat, the hash of every move, winner, points, turns, score.
- **kp3:** the same against `rl/results/public_pricing_2026-09-25/kp3_500_*.jsonl`, 14,000 of 14,000.
- **The command-line program against rules4:** the new `deckgym` and the previous official one print identical win and draw counts for k3 on both sides, on the screen's seed 7100 with `--seed-stream`, in four matchups of 30 games (brew-07 against Altaria, Blaziken, Hydreigon and Lucario).
- **kp3 smoke test:** the new `deckgym` runs kp3 on both sides.

**Unchanged:**
- The 0.7.2 RL add-on wheel and every run identity bound to it.
- The rules4 program `rl/addon-0.7.2/deckgym`, preserved with its hash and listed in the manifest's historical releases.
