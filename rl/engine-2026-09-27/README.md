# The official engine from Sept 27, 2026: main-83e17ae (the repaired engine)

**What changed:**
- These three programs are now the project's official engine (`project_manifest.json`, `available_release`). `current_engine.py`, `decks/screen/run_screen.py` and `decks/screen/floor.py` resolve to them.
- They replace `rl/engine-2026-09-25/` (main-7fc6ccb), which is kept unchanged as history.

**What's different in play:** the ten rules/09 repairs of Sept 26. Only two change table games:
- **Legendary Pulse** draws at once, before Hiking Trail tops the hand up.
- **After an end-of-turn or Checkup Knock Out,** the knocked-out player promotes before the next turn begins.

The other eight change no table game:
- Poké Ball A2b 111 with an empty deck;
- Rare Candy against Primeval Law;
- Heavy Helmet's current Retreat Cost;
- discard-all-Energy attacks filling the discard pile;
- random-Energy effects;
- Disguise, Bad Dreams, Clemont's Backpack, Roar in Unison and Clemont's hand cap.

Three of the ten were confirmed by Dustin's own in-game tests and one by his footage (`rules/09_engine_repairs_2026-09-22.md`). The version string is unchanged at `0.1.0-pdl.rules4`.

| file | sha256 |
|---|---|
| `deckgym` (the command-line engine; `deckgym simulate`) | `27626eb520d4056f734aaa7325ddd10aa8d861d92a19644f9ed80fdc35bf7931` |
| `legality_scan` (the table tool; `--games-out`, `--pairs`/`--seed-base`/`--root`, openings and decisions) | `e6ab9a9d486064142dfedd7ed536896ccba5a45c1a36b056436b358672e0d7b7` |
| `goldfish` (A1's goldfish and card-coverage tool; the floor check needs this hash) | `f851058e0303cf8f3072eb4e69d6297ca7f881571faba24e781c02b7e0ca0800` |

**Why, and the checks** (Dustin, Sept 26-27: "Go … Merge, pin the hashes, point the screen at it"):
- **Replays:** every repair was replayed on the table, k3 and kp3 at 14,000 games each (`rl/results/rules09_fixes_2026-09-26/`). The laptop covered four repairs and the cloud the rest.
- **The mechanic check** (`rl/results/engine_switch_2026-09-26/README.md`):
  - Every changed game reaches its repair's mechanic, on the board or in the bots' lookahead.
  - The lookahead case counts under the rule Dustin restated on Sept 27 (RUN5 "Rules", "Engine repairs"): a code path gated on the mechanic's condition, plus a trace to the first divergence. The promotion fix's 24 lookahead games are the worked example.
- **Identity** (`rl/results/engine_switch_2026-09-26/pin_identity.txt`):
  - k3 and kp3 over the table's 14,000 deals equal the repaired engine's references (the cloud's `af8489f_{k3,kp3}_500.jsonl`: moves, decisions and result), 14,000 of 14,000 each.
  - They also equal kpf's build's table runs, 14,000 of 14,000 each.
  - `deckgym simulate` runs k3 and kp3 on seed 7100 (`--seed-stream`), and `goldfish --coverage` runs.

**Source and build:**
- git commit `83e17ae` on main: the merge of `claude/pensive-ptolemy-spwc0b`.
- `engine/` there is identical to 9bffbda, the kpf build.
- Built in WSL on Sept 27 from `git archive`: `cargo build --release`, plus `--example legality_scan` and `--example goldfish` (`rl/results/engine_switch_2026-09-26/pin_official.sh`).
- Players: k, kp, kq, kd, kpr, koa (with kob and kor), kpf and kpg.

**Baselines moved with it:** the frozen table is scoreboard v3 (`rl/results/scoreboard_v3_2026-09-27/`): k3 and kp3 on all 45 cells at this engine.

**Unchanged:** the 0.7.2 RL add-on wheel and every run identity bound to it; the rules4 program `rl/addon-0.7.2/deckgym`; the Sept 25 release (`rl/engine-2026-09-25/`, now in the manifest's historical releases).
