# The slow report's R8 re-pin check: kx3 on R8's engine (the spec; written Nov 4, before any game)

Dustin, Oct 21 (verbatim, to the coordinator): "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine." His Nov 4 "Adopt all three" (answering the approval page "R8 Approval Sheet", relayed in coordinator-153) adopts R8 with nothing dropped, and the page's after-yes steps include this check and the re-pin (plan 113 §7-8). It repeats the Oct 21-22 and Oct 29 checks (`../kx3_on_engine_2026-10-21/`, `../kx3_on_r6_2026-10-29/`: each 202 of 202 kx3 and 202 of 202 km3 games identical) on the new program. Written by the laptop session (plan 113 §7, coordinator-155/156).

## 1. The program
- **Path and hash.** `/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength`, sha256 `d4d4e43acebcf7aebad7ba719d32dc2b0a3d347d1a2b53c074788a678ab4e12d`.
- **Built from K8.** K8 is `b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0` (branch `laptop/kx3-on-r8-2026-11-04`, on origin; made by `rl/results/r8_catchup_2026-10-29/lane/mk_k8.sh`):
  - **R8's engine.** Its first parent is the R8 lane commit 48dec4f5, whose engine tree is that of R8's release commit S8, `543dad0007a345128ec95e9c2698699c8b5493ce` (014b4371a3b8); the official programs of main-543dad0 were built from S8 and have Lane N's sha256 (`rl/results/r8_catchup_2026-10-29/r8_release/`).
  - **Plus kx3's six engine files** of e3ddc014 (R6's K): `examples/playout_smoke.rs`, `src/players/mod.rs`, `src/players/playout_player.rs`, `src/players/playout_pool.rs` and `tests/playout_pilot_{test,extra_lists_test}.rs`.
  - **Five of the six are byte for byte d513e37b's** (the frozen kx3). **`src/players/mod.rs` is d513e37b's plus exactly R8's 8 protocol-adapter lines**: a union merge of one conflicting hunk at the end of `enum PlayerCode` (R8's `Proto { .. }` and kx3's `KX { params }`), plus R8's module lines and the `Player` trait's two new methods, `before_decision` and `on_public_event`, with empty default bodies (`K8_RECORD.union.txt`; laptop check Nov 4).
  - **Nothing else differs.** `git diff --name-only 48dec4f5 K8` lists exactly those six files.
- **Engine tree as archived:** `f33d2c49baf432d4bd1e407b96a6c243471fa9b6`. It must equal `git rev-parse K8:engine` (f33d2c49baf4).
- **The build.** `rl/strength/build.sh` from the lane worktree at 48dec4f5 (`/home/dacz8976/lane_r8_w`): harness source `c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149` (the pinned one: unchanged since R6's re-pin), STRENGTH_JOBS=2, its own build and target folders; built `2026-11-04T06:07:16Z`; build record `strength.build.json` beside the program, sha256 `5d8c0cee1db6a29d5c17eb70debc6b02aa41256f77bab10e440f3c30111d826a`.
- **Its self-checks** equal the slow-report pin's texts:
  - kx3, measured on this program in the switch (Nov 4, 5,377 s): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa`
  - km3, measured on R8's km3 build strength_L (the same engine tree, Lane N's night): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`
  - Each registration below replays both again **on this program**.
- **The pilot label** at the re-pin is "kx3 (d513e37b's files, on main-543dad0)". The pinned one stays "kx3 (d513e37b's files, on main-affe56e)" until then.

## 2. The games (the same as Oct 12, Oct 21 and Oct 29)
Three registrations of the development run's games (`../strength_2026-10-03_kx3_dev/`), with the development run's own seeds (`make_replay_configs.py` asserts every key's seed), this program, and `--repo` this branch's worktree.
- **The branch.** `laptop/kx3-replay-r8-2026-11-04`, cut from `e6a20c73bf7ff7dd629c55729f489fd879d5f44a` (the R8 branch after the adoption commit (113 §7.2: main does not carry R8 until the end)). Its engine tree `014b4371a3b809273c01a1809a058de5980cdfd1` equals S8's (checked by prepare.sh).
- **The harness files are R6's check's.** rl/strength/src, Cargo.toml, strength_prereg.py, split_collect.py, decks.json, groups.json, heldout.json, intended_lines.json and the development run equal R6's release affe56e8's at the base (prepare.sh). `compare_dev.py` is Oct 21's (and R6's).
- **The worktree** is `/home/dacz8976/r5_w`, reused as at R6.

| registration | decks v opponents | deals | games (kx3 + km3) |
|---|---|---|---|
| replay_a | 09, 06, 10 v the 8 panel lists | 0-1 | 96 + 96 |
| replay_b | 01, 05, draft A v the 8 panel lists | 0-1 | 96 + 96 |
| replay_c | 10 v t-weezing (Will's row) | 0-4 | 10 + 10 |

- **Wailord is left out** (Dustin, Oct 10), as before.
- **The files are unchanged.** At the base each deck and list file has the sha256 the development run's `manifest.json` records (15 of 15). The lane checks the same in each new manifest.
- **How the laptop plays them** (coordinator-155: every heavy step under nice): nice 19 and ionice -c3 for the registrations, the games and compare_dev.py; the program's environment scrubbed of KX_*, PDL_*, DECKGYM_*, JEV_* and PG_*; TMPDIR on disk; replay_b at 3 threads with replay_a at 2, then replay_c at 2; no new phase while `~/credit_work/PAUSE` exists (Dustin needs the laptop). Threads change nothing about the results: every game is seeded.

## 3. Where R8 can change these games (fixed before any game)
The terms are R6's (`../kx3_on_r6_2026-10-29/SPEC.md` section 3): a change **can act** in a row when that row's cards (either seat), km3's search or kx3's play-outs can bring the changed code to a different result; it is **reached** when its changed code runs in the row but, by reading, returns what the old code returned. Only rows where a change can act would be named in `rows.json`.

**Sources.**
- `git diff affe56e8 543dad00 -- engine/src`: 43 files, +3,907 / -478. engine/Cargo.toml and Cargo.lock unchanged.
- The cards: the 14 deck/list files and kx3's 16 play-out lists hold 101 card ids (kx3's pool: 66 of them). **None of their 101 database.json entries differs between affe56e8 and S8.**
- The read: six code clusters, each read by one agent over its diff and then by one adversarial verifier told to refute every verdict and to find missed hunks (read-only, Nov 4). Every hunk was placed. The verifiers' corrections are applied. All 63 changes, with their evidence and the 14 objections, are in `REACH.json`.
- The rule rows' own predictions for this check (`../r8_catchup_2026-10-29/RULE_ROWS.md`, source (a)): 0 games for every row and item 11 (Misty, R8-10a, proved tests-only).

| cluster | what R8 changed there | verdict in these games |
|---|---|---|
| Trainers (9 files) | Dispatch by canonical printing (upstream #395, `trainer_identity.rs`); the new Trainers (Sweet Honey, Super Potion, Max Repel, Full Heal, Genome Converter Y); Abandoned Station; Eviolite and Light Ball | **Reached, no change.** Every list Trainer is the first printing of its (name, effect) in enum order, or (Poké Ball P-A 005, Professor's Research P-A 007) maps to a printing with the same text whose arm calls the same functions with the same card. The new cards and Stadium are in no list. |
| Attacks (6 files) | #433 and #438 map entries, Flame Aura, Psycho Boost, Spacial Rend, Dual Blizzard, Wings of the Moone, Triple Bombardment; Jumping Coach's extra coins; four in-play type reads | **Cannot act** for the new texts (no list card carries one); **reached, no change** for the coin and type reads (no Raboot; the in-play type equals the printed type without Urshifu). |
| Abilities and actions (8 files) | Honey Gather, Sudden Duplication, Metal Scrum; new SimpleAction and mechanic variants; Darkrai ex's Nightmare Aura now on any [D] from the Energy Zone; the Checkup's sleep-coin count; the per-Knock-Out "not by the attack" flag | **Reached, no change** in the t-weezing rows: no card of the 101 attaches a [D] from the Zone to a Darkrai ex except the turn's attach, which triggered before too (every non-turn Attach generator checked). The rest cannot act. |
| State and hooks (6 files) | item 11 (in-play type checks), Soothing Lullaby's coins, the status refactor, the Eviolite/Metal Scrum/Light Ball terms, the game loop's new player hooks and its RNG-clone probes | **Reached, no change.** No Urshifu; no Jigglypuff C1; the new damage terms are 0 without their cards; the hooks are empty for km3 and kx3, and the probes draw from a clone of the game RNG, never from it. |
| Coin plan (1 file) | `trainer_coin_plan.rs`: the luxury coin source, the Misty and Sweet Honey routes | **Cannot act / not in the program**: every caller sits behind the luxury coin gate, which no list card opens; Misty's draws are unchanged in number and order (its pinned trace test is in the test suite). |
| Outside the games (13 files) | The protocol adapter and its bot, main.rs, the `proto` player code, opening classes for the new Ability variants, the weighted random player, card support, card validation, test support | **Not in the program or reached, no change**: no game uses the protocol player, an outside bot or the weighted random player; km3's opening term reads the new classes only for new Ability variants. |

**Where the bots look.** km3's search uses the real opponent list or Unknown cards; kx3's play-outs draw from `playout_pool.rs` (d513e37b's blob): 16 lists, 66 card ids, all among the 101. KX_EXTRA_LISTS stays unset. No new card enters any position a bot considers.

**Result: no row is named.** `rows.json` is `{}`, and every one of the 202 kx3 and 202 km3 games is expected to replay exactly. Evidence beyond the reading: Lane N's 18 identity replays on R8's programs (the k3, kp3, kog3, kta3 and km3 pilots; 156,520 games or deals) equal R6's S ("v S: SAME"), and the switch's kx3 self-check equals the pin.

## 4. The reading (fixed now; as at R6)
`compare_dev.py` compares each game with the development run's game on the same key, by content without timing (`split_collect.py`'s `content`), per arm and per row. With `rows.json` empty, any changed game is printed as "NOT A NAMED ROW: a stop", with its first differing logged decision.
- **Pass.** All of these hold: every one of the 202 kx3 and 202 km3 games equals the development run's; every seed equals the development run's, and no game is missing, unreadable or outside the development run; `compare_dev.py` exits 0; each registration's two self-checks equal the pin's texts; each registration's 14 deck and list files have the development run's sha256.
- **Stop.** Any one of these: any changed game; any missing or unreadable game; a self-check of any registration that differs from the pin's; a deck or list file whose sha256 differs; the program's sha256 not being `d4d4e43acebcf7aebad7ba719d32dc2b0a3d347d1a2b53c074788a678ab4e12d`; a kx3 decision over 120 s (plan 113 §7; each logged decision in `games.jsonl` carries its time, `"ms"`, and the reading reads the largest).
  A stop goes to the coordinator and Dustin as it is. The lane only writes it clearly: a "STOP" line in its log, `STOP.txt` in its state folder (`~/pincand_work/kxr8/`), and the first line of `LANE_RECORD.txt`. The session tells them. Nothing is activated: no re-pin, nothing moves.
- **What a pass allows (plan step 8).** The re-pin: the slow report's program moves to the K8 program, and its pin and docs are regenerated by an adapted `slowpin_main.py`, then the pin tests run (all modules rc 0 and `make_predictions.py --selftest` PASS). The pin's new fields: `program_sha256` and `selfcheck_measured_on_sha256` `d4d4e43acebcf7aebad7ba719d32dc2b0a3d347d1a2b53c074788a678ab4e12d`; `engine_ref` K8 and `engine_tree` `f33d2c49baf432d4bd1e407b96a6c243471fa9b6`; `harness_source_sha256` `c4f7da21…` (unchanged); `pilot_label` "kx3 (d513e37b's files, on main-543dad0)"; the `engine` and provenance texts; the self-check texts, unchanged. Then the coordinator's final review; main moves once, after it.

## 5. Order
1. **Before the lane** (`prepare.sh`): this spec, `rows.json`, `REACH.json`, `make_replay_configs.py`, the configs it writes, `compare_dev.py`, `lane_kxr_r8.sh` and `prepare.sh` are committed on `laptop/kx3-replay-r8-2026-11-04`; Guardrail A (paths, message, and added content with the never-open exclusion array); pushed. The coordinator sees them before the lane.
2. **The lane** (`lane_kxr_r8.sh`): the three registrations (each replaying both self-checks), committed, Guardrail A, pushed and checked on origin before any game; the games; `compare_dev.py` writes `COMPARE_DEV.txt`; the games, `COMPARE_DEV.txt` and `LANE_RECORD.txt` committed, Guardrail A, pushed.
3. **The reading** (`READING.md`, with "**Verdict: pass.**" only on a pass), then the re-pin, or the stop.
