# Lane N/I prediction (written before any run)

Coordinator-147 §4 and coordinator-148 (its eight answers are binding). Written and committed before the lane runs; the
night driver is `lane/night_r8.sh`, and every number below is what it must see. **Anything else is a STOP.**

## 0. The lane commit and its trees

- **Lane commit = the commit that adds this file** (and `lane/`). Its parent is cdadc04f (R8 docs 2 fix), which goes with
  55f67837 (R8 docs 2; coordinator-148 §1).
- **engine/ and decks/ equal 63657e0a's except engine/UPSTREAM.md:** `git diff --name-only 63657e0a <lane> -- engine decks`
  prints exactly `engine/UPSTREAM.md`, 55f67837's one-line note that the file is historical (coordinator-147 §3). No build
  reads that file (`git grep UPSTREAM` over engine/src, examples, tests, build.rs and Cargo.toml: no line). So every compiled
  file is 63657e0a's; the preflight checks exactly this, and that the commits since cdadc04f touch only
  `rl/results/r8_catchup_2026-10-29/`.
- `engine/examples/legality_scan.rs` and `decks/` are unchanged since affe56e8 (R6 S).
- **The R6 replay inputs:** ~/pincand is at b78c8997 (main, the commit R6 recorded, `r6_release/RUN_CONTEXT.txt:3`), and its
  tracked files under these paths are clean. `git diff b78c8997 <lane>` is empty for all of them: decks/, the 4 pairs files
  (`rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv`, `rl/results/engine_switch_rules_2026-10/pairs_8.tsv`,
  `rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv`, `rl/results/engine_switch_rules2_2026-10/pairs_8b_cloud.tsv`),
  the SW2 folder `rl/results/engine_switch_rules2_2026-10` (the references, `switch_check.py`), `screen_with.py` and
  `decks/screen/run_screen.py`. Every file the 18 replays read has the same sha256 in ~/pincand and at the tip. So reading
  them from the lane worktree (148 §3, first option; `lane/replay_r8.py`) changes nothing; the predicted effect is none.

## 1. Build, gencmp, card_status

- **build_R:** BUILD OK (plain: deckgym, then the legality_scan and goldfish examples) in the lane's own target folder
  `/home/dacz8976/lane_r8_target` (empty before), so every binary is new: the guard prints `build_R: guard OK (Compiling
  deckgym v0.1.0-pdl.rules4 (/home/dacz8976/lane_r8_w/engine))` and five new hashes. The warning lines are reported, not
  predicted.
- **gencmp:**
  - `gen_R ids: SAME (/home/dacz8976/lane_r8_w/engine/src/card_ids.rs v <OUT>/prep/gen_ids.rs); generated secondary_energy_type None lines: 0`
  - `gen_R database: SAME (/home/dacz8976/lane_r8_w/engine/src/database.rs v <OUT>/prep/gen_database.rs); generated secondary_energy_type None lines: 4154`
  - (`database.json`, `database.rs`, `card_ids.rs`, the generator and Cargo.lock are unchanged since affe56e8, so these are
    R6's numbers, `lane_r.log:10-11`.)
- **card_status** (`<OUT>/prep/status_R.txt`; checked against the built card_status of 63657e0a's engine, the same code):
  - `card_status: all 4577 | new C1/SP1/P-C: 260 {'Complete': 256, 'RulesUnverified': 4}`
  - `   C1 217 {'Complete': 213, 'RulesUnverified': 4}`, `   SP1 30 {'Complete': 30}`, `   P-C 13 {'Complete': 13}`
  - `older cards neither Complete nor RulesUnverified: 0 []`
  - `Trainers with a new or B4b printing (same name and text) whose printings differ in status: 0`
  - `incomplete new ids: [('C1 015', 'RulesUnverified'), ('C1 051', 'RulesUnverified'), ('C1 135', 'RulesUnverified'), ('C1 184', 'RulesUnverified')]`
  - `all by status: {'Complete': 4565, 'RulesUnverified': 12}`; `STATUS_CHECK OK`
  - So 4,577 = 4,565 Complete + 12 RulesUnverified, 0 refused. The 12 are B3 025, B4 115, B4a 018, B4a 051, B4a 069,
    B4a 085, B4a 109, P-B 049, C1 015, C1 051, C1 135, C1 184. Against R6 S's file, no older card changed status; the
    limitation text changed only for Gholdengo B4a 051 and B4a 109, which no replay deck holds.

## 2. Suite and goldfish steps

- **Suite** (`cargo test --release --features test-utils --locked --no-fail-fast`, RUST_TEST_THREADS=2):
  `passed 2633 failed 0 ignored 0 compile_errors 0 failing []` (the last check at 63657e0a, ~/relplan/r8/cc: the same).
- **goldfish_R:**
  - The plain goldfish rebuilt: `goldfish_plain: guard OK`. Its hash differs from the test-utils goldfish the suite left.
  - `strings` lines with TEST_CARD_SUPPORT_MISSING_ATTACK: `programs/deckgym 0, programs/goldfish 0, rebuilt plain goldfish 0`.
  - `cargo test --release --locked --test goldfish_card_support_test`: `test result: ok. 1 passed; 0 failed`.
  - The test-utils goldfish rebuilt: `goldfish_test_utils: guard OK`, with 2 strings lines (report only).

## 3. The 18 replays (deck list and results v the 08a9b3a references)

**Deck list:** the 18 runs of `REPLAYS=` in R6's `lane_s.sh:18`, as R6 ran them (`r6_release/logs/lane_r.log:21-56`).
RULE_ROWS (c)'s "15 + 7 pages" (`RULE_ROWS.md:17`) is a different, older set; these 18 fall under its (e). The deck files
(43, from the .run records, the table's NAMES and the used rows of the pairs files): `decks/research/` (8),
`decks/screen/opponents/` (8), brew-06 and brew-06b (run_screen), and the pairs files' held and panel files.

| row | games | v the reference | the detail line starts |
|---|---|---|---|
| 10_cli_k3 | 240 | SAME | `Player 0 won: 150 (62.50%) \| Player 1 won: 90 (37.50%) \| Draws: 0 (0.00%) \| v S: SAME` |
| 10_cli_kp3 | 240 | SAME | `Player 0 won: 144 (60.00%) \| Player 1 won: 96 (40.00%) \| Draws: 0 (0.00%) \| v S: SAME` |
| 10_cli_kog3 | 240 | SAME | `Player 0 won: 149 (62.08%) \| Player 1 won: 91 (37.92%) \| Draws: 0 (0.00%) \| v S: SAME` |
| 10_cli_kta3 | 240 | SAME | `Player 0 won: 149 (62.08%) \| Player 1 won: 91 (37.92%) \| Draws: 0 (0.00%) \| v S: SAME` |
| 10_cli_km3 | 240 | SAME | `Player 0 won: 149 (62.08%) \| Player 1 won: 91 (37.92%) \| Draws: 0 (0.00%) \| v S: SAME` |
| 10_goldfish | 0 | SAME | `page =, coverage = \| v S: page SAME, coverage sha SAME` |
| table_k3 | 14000 | SAME | `0 differing deals of 14000;` |
| table_kp3 | 14000 | SAME | `0 differing deals of 14000;` |
| table_kog3 | 14000 | SAME | `0 differing deals of 14000;` |
| dev_km3_table | 14000 | SAME | `0 differing deals of 14000;` |
| dev_kta3_table | 14000 | SAME | `0 differing deals of 14000;` |
| 10_run_screen | 3840 | SAME | `run_screen: ... 20 of 20 lines equal (2 decks; the header's engine path aside) \| v S: SAME` |
| new17_k3 | 8500 | DIFFERS | `8 differing deals of 8500;` |
| dev_km3_new17 | 8500 | DIFFERS | `7 differing deals of 8500;` |
| 8b_cloud_new_k3 | 240 | SAME | `0 differing deals of 240;` |
| 8b_cloud_new_km3 | 240 | SAME | `0 differing deals of 240;` |
| 8_new_km3 | 16000 | DIFFERS | `1 differing deals of 16000;` |
| cov_b2e_km3 | 48000 | SAME | `0 differing deals of 48000;` |

- 15 SAME and the 3 known reference differences, with exactly R6 S's deals (`replays_S/*.diff.tsv`, byte-equal):
  - new17_k3: 8 of 8,500, pairing 21 (altaria_greninja v hydreigon), i = 102, 157, 219, 224, 265, 330, 345, 465;
  - dev_km3_new17: 7 of 8,500, pairing 21, i = 102, 157, 206, 219, 265, 345, 465;
  - 8_new_km3: 1 of 16,000, pairing 11 (togekiss_meowth v lucario), i = 484.
- Every one of the 11 legality_scan rows: `rules page: <OUT>/games/r/<row>.txt: no RULE finding`.
- Wall time as R6's (`lane_r.log:21-38`): about 3 h 15 min for the 18.

## 4. Against R6 S (in place of "v f"; S was "v f: SAME" on all 17, `lane_r.log:39-56`)

- The 11 game files have the sums of `replays_S/outputs.sha256:1-11`: every legality row ends `| v S: sha SAME, diff.tsv =`.
  - 28cb2b23… 8_new_km3, 9501a401… 8b_cloud_new_k3, d2f6a03f… 8b_cloud_new_km3, 84247fb4… cov_b2e_km3,
  - 50be2d19… dev_km3_new17, aff167ac… dev_km3_table, 6b90d3cf… dev_kta3_table, b81fab21… new17_k3,
  - 2437ba5b… table_k3, 00e4ddc8… table_kog3, 788e57a6… table_kp3.
  - The game lines hold deck names and the pairs files' relative deck paths, never `--root`, so the lane worktree's path
    cannot reach them (`legality_scan.rs:751-779`).
- The 5 CLI outputs equal `replays_S/08a9b3a_10_cli_*.txt` with the "Ran " lines aside. The first line names the engine
  version, `PDL decision-integrity candidate 0.1.0-pdl.rules4: …`, and the version is unchanged (`engine/Cargo.toml`, affe56e8
  and the tip). No deck of these runs holds a RulesUnverified card, so the card-support preflight prints no limitation line,
  as in S. Predicted: SAME, with no version-only line.
- run_screen: equal to `replays_S/08a9b3a_10_run_screen.txt` (`switch_check.py screen`, the header's engine path aside;
  ours names `../pincand_work/RR_R8_<c>/programs/deckgym`).
- goldfish: the page equals S's once the deck path's folder is mapped (ours names `/home/dacz8976/lane_r8_w/decks/research/
  altaria.txt`, S's `/home/dacz8976/pincand/…`: a known-reason difference, mapped by replay_r8.py, never a STOP). The coverage
  file's sha256 is `outputs.sha256:12`, 1be78554…; it names no path (S's raw sum equals the reference's).
- `replay_r8.py verify` prints `v S as predicted: 18 of 18; clean rules pages: 11 of 11` and `VERIFY PASS`.
- No known-reason difference is expected beyond the goldfish path. No legality_scan, CLI or run_screen output prints a card
  count or a refusal for these decks. R8's new card support changes only cards that none of them holds (§6).

## 5. Digests (coordinator-148 §2.1)

- **(a) Harness source:** `c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149`, unchanged (checked at the
  tip). Since affe56e8 R8 changed `rl/strength/README.md`, `rl/strength/test_strength_card_support.py` and
  `slow_report_pin.json`, none of them hashed (build.sh hashes `src/*.rs` and `Cargo.toml`). The lane strength build's
  record says so too (`harness_source_sha256`), with its engine tree = the lane commit's `engine` tree.
- **(b) sc_km3** on the lane's own strength build (t-altaria v t-suicune, 12 games, as `night_r6.sh:20`), exactly
  `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`. Why: both decks are old
  cards, and neither holds a rule-row card. sc_kx3 is not run (after his yes, 148 §2.2).
- **(c) The hunks:** `lane/digest_hunks.sh` lists 53 hunks: hooks/core.rs 28, players/mod.rs 6, players/opening_class.rs
  15, players/protocol_player.rs 1 (the new file), players/weighted_random_player.rs 3. Each comes with the R8 commit that
  made it. The explanations are written from that list after the run.

## 6. Lane I (the rule rows R8-10a to R8-10e and item 11, all in this tip)

**0 deals change in the 18 runs.** That is the identity result of §3: 15 SAME plus S's 3 known differences, deal for deal.
Names-only grep, before this commit, of the 43 deck files the 18 runs read (each card line's `SET NNN` id):

| cards | files |
|---|---|
| Snover A2 044; Sealeo B4 039 | 0; 0 |
| Urshifu B3 051, B3 113 | 0 |
| Sableye (Jeweled Gift) B3a 040, P-B 070 | 0 |
| Haxorus B4b 176, B4b 348 (and B2b 056, B2b 110, P-B 045) | 0 (0) |
| Machop B2 079; Conkeldurr B4 089 | 0; 0 |
| Palkia C1 038, C1 140; Sweet Honey C1 119, C1 152 | 0; 0 |
| Iris B2b 067, B2b 081, B4b 212, B4b 378, B4b 421 | 0 |
| Mega Blastoise ex B1a 020, B1a 078, B1a 084, B4b 054, B4b 414 | 0 |
| Starting Plains B2 154, B4b 235, B4b 401 | 5: brew-07, brew-08, brew-09, decks/dustin/04, b2e's h-hoopa_absol |
| Darkrai ex A2 110, A2 187, A2 202, A4b 245, A4b 378, P-A 042 | 5: brew-07, decks/dustin/04, decks/research/weezing, t-weezing, b2e's h-hoopa_absol |
| any C1, SP1 or P-C printing | 0 |

The Darkrai ex and Starting Plains holders are expected. What R8-10b and R8-10e need is a Jeweled Gift attach (B3a 040,
P-B 070) or Shatter, Bedrock Breaker or Spacial Rend (B2 079, B4 089, C1 038, C1 140), and no file holds one. Item 11 needs
an Urshifu with Snover or Sealeo, and R8-10c needs a B4b Haxorus: 0 files. R8-10d needs Mega Blastoise ex: 0 files.
R8-10a is tests only.

## 7. K8 and the smoke

- **K8** (`lane/mk_k8.sh`): kx3's six files of e3ddc014 (all six blobs = d513e37b's: checked) on the lane commit, as the
  local branch `laptop/kx3-on-r8-2026-11-04`. **Prediction: the plain 3-way merge of `engine/src/players/mod.rs` conflicts in
  1 hunk.** At the end of `enum PlayerCode`, R8's `Proto { .. }` variant (with its doc line) and kx3's `KX { params }`
  variant (with its 4 doc lines) are both inserted after `KM { max_depth: usize },`. mk_k8.sh exits 3; by 148 §2.4 the kx3
  smoke stops (night/KX3_STOPPED) and the rest of Lane N goes on.
  - If the coordinator allows the union resolution (`K8_UNION_OK=1`), the merge is accepted only as pure additions: R8 adds
    8 lines and kx3 12, and the merge equals the lane's file plus exactly kx3's 12 lines, and e3ddc014's plus exactly R8's 8.
    A dry run on temporary files passed this check.
  - Whether kx3's files then compile on R8 **cannot be predicted exactly.** Reason: R8 adds two default methods to `Player`
    and new variants to `SimpleAction`, `AbilityMechanic`, `CardEffect` and `PlayerCode`. kx3's files name none of the first
    three, and `PlayerCode` 3 times through `create_players`/`get_player`, but no build was made. A compile failure stops the
    kx3 smoke only.
- **Smoke decks** (`lane/smoke/decks/`, `lane/smoke/PRINTINGS.md`): a01-a09 hold all 55 newly supported printings (55 of
  55); b01-b06 are 148 §2.6's. `check_decks.py` against the lane's own card_status: `ALL DECKS OK`.
- **Smoke b (km3 v km3, the lane's strength build):** 40 games (b01-b04 v t-altaria 32, b05 v b06 8; 2 deals x 2 seats x 2
  arms). Both arms are km3, so each deal is played twice, and the two arms are identical game for game. 0 panics, 0
  refusals, every km3 decision ≤ 3 s. A km3 decision over 3 s is re-run once; over 3 s again is a STOP.
- **Smoke a, km3:** 72 games (a01-a09 v t-altaria), as for b.
- **Smoke a, kx3** (K8's build; only if K8 is made and builds): 72 games, 36 of them kx3 on the deck v km3 (arm X). The other
  36 are km3 v km3 (arm ref) and must equal smoke a km3's games of the same keys. 0 panics and 0 refusals. kx3 is report-only:
  mean, median, p95 and max ms per decision, and every decision over 30 s named with its board. One decision over 120 s
  stops the kx3 smoke only.
- km3's slowest decision is expected well under 3 s. R8's own Lunala heavy rows, km3/y3/x3 at the turn root, were at most
  1,342 ms, and no decision went over 3 s in any check (RELEASE_NOTES §6).

## 8. Not predicted (reported only)

- Wall times, warning counts and program sha256 values.
- kx3's ms per decision.
- The smoke games' winners and points. A km3 game is repeated identically within a run, but no result is predicted.

**Anything else is a STOP.**
