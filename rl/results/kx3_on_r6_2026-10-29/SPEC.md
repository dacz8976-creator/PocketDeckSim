# The slow report's R6 re-pin check: kx3 on R6's engine (the spec; written Oct 29, before any game)

Dustin, Oct 21 (verbatim, to the coordinator): "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine." His Oct 28 "Yes" to the Dual Fusion adoption covers R6 as listed, including "the slow-report pin, the kx3 rebuild and the self-check digests" (`rl/results/dual_type_seam_2026-10-23/RELEASE_CHECKLIST.md`, R6; `RELEASE_NOTES.md:3`). This is the check for R6. It repeats the Oct 21-22 check (`../kx3_on_engine_2026-10-21/`: 202 of 202 kx3 and 202 of 202 km3 games identical) on the new program. Runbook steps 13-14. Written by the laptop session on the coordinator's instruction of Oct 29.

## 1. The program
- **Path and hash.** `/home/dacz8976/kx_r4/strength`, sha256 `23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378`.
- **Built from K.** K is `e3ddc0149bb9d35fda1becbb17ab5f71d9461609` (local branch `laptop/kx3-on-r6-2026-10-29`, made by `mk_ks.sh`):
  - **S's tree.** S is `affe56e88985e2997a66beb85efaca0c487617bd`, the R6 release commit on `laptop/r6-release-2026-10-29`. It is main ffe97adb plus the card-support refusal (c0290e37, merged as 6e1ff1d0) plus the tests-only fold (3a9413cf, 59fc3054).
  - **Plus kx3's six engine files:** `examples/playout_smoke.rs`, `src/players/mod.rs`, `src/players/playout_player.rs`, `src/players/playout_pool.rs` and `tests/playout_pilot_{test,extra_lists_test}.rs`.
  - **The six files are unchanged.** Each blob in K equals 87a7f340's (the pinned kx3 on main-4d48844) and d513e37b's (`git rev-parse`, checked Oct 29).
  - **Nothing else differs.** `git diff --name-status S K` lists exactly those six files.
  - **The two bases differ in the same way.** `git diff --stat 87a7f340 K -- engine/src engine/examples engine/Cargo.*` equals `git diff --stat 4d488449 S` over the same paths: 38 files, +21,560 / −272.
- **Engine tree as archived:** `cd970db60aa5df7e9db9d7479e88f87190dab2c3`. It must equal `git rev-parse K:engine` = `cd970db60aa5df7e9db9d7479e88f87190dab2c3`.
- **The build.** `rl/strength/build.sh` ran from a clean checkout at S (`/home/dacz8976/r6s_w`):
  - harness source `c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149` (`bf9c5d68…` at the current pin; it changed only by the card-support refusal in `rl/strength/src/main.rs`, +24/−4);
  - STRENGTH_JOBS=2, build folder `/home/dacz8976/kx_r4_build`, target `/home/dacz8976/dual_target` (shared, not fresh as on Oct 21);
  - built `2026-10-29T04:13:47Z`;
  - build record `/home/dacz8976/kx_r4/strength.build.json`, sha256 `0b0b07fa8e4e621ae0c736f0b622d02b563608633becfa27f57ccd3d5b09cdd1`.
- **Its self-checks were measured on this program in the R6 night job** (`~/pincand_work/r6night/`, night_r6.sh step 4). They equal the slow-report pin's texts:
  - km3: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`
  - kx3: `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (4738 s)
  - Each registration below replays both again.
- **The pilot label** (coordinator-072) is "kx3 (d513e37b's files, on main-affe56e)". The pinned one stays "kx3 (d513e37b, on main-4d48844)" until the re-pin.
- **Why "d513e37b's files" and not "d513e37b's players".** R6 changed four km3 player files on purpose: `fuel_credit.rs`, `value_functions.rs`, `public_pricing_player.rs` and `weighted_random_player.rs`. `opening_class.rs` changed only in a test comment. kx3's own files are byte for byte d513e37b's.

## 2. The games (the same as Oct 12 and Oct 21)
Three registrations of the development run's games (`../strength_2026-10-03_kx3_dev/`). They use the development run's own seeds (`make_replay_configs.py` asserts every key's seed), this program, and `--repo` this branch's worktree.
- **The branch.** It is `laptop/kx3-replay-r6-2026-10-29`, cut from `b9ba4a9a709f116880d53eac1d301b2ae58ff045` (main b9ba4a9a (the R6 adoption 220b9844, then R7 870542e7 and two docs commits; engine/ = S)).
- **The base's engine tree** is `c8c79c635b92c9f95c5bf1db7f77d7774f8813ca`, equal to `git rev-parse affe56e8:engine` = `c8c79c635b92c9f95c5bf1db7f77d7774f8813ca` (checked by prepare.sh).
- **The worktree** is `/home/dacz8976/r5_w`, reused (coordinator-076).
- **K is on origin** before the registrations name it.

| registration | decks v opponents | deals | games (kx3 + km3) |
|---|---|---|---|
| replay_a | 09, 06, 10 v the 8 panel lists | 0-1 | 96 + 96 |
| replay_b | 01, 05, draft A v the 8 panel lists | 0-1 | 96 + 96 |
| replay_c | 10 v t-weezing (Will's row) | 0-4 | 10 + 10 |

- **Wailord is left out** (Dustin, Oct 10), as on Oct 12 and Oct 21.
- **The 14 files are unchanged.** At S, each deck and list file has the sha256 the development run's `manifest.json` records (checked Oct 29). The lane checks the same in each new manifest.
- **How the laptop plays them:**
  - after the R6 night job, nice 19, ionice -c3;
  - the program's environment scrubbed of KX_*, PDL_*, DECKGYM_*, JEV_* and PG_* (KX_EXTRA_LISTS unset, as in the development run);
  - TMPDIR on disk;
  - replay_b at 3 threads with replay_a at 2, then replay_c at 2.
- **Threads change nothing about the results:** every game is seeded.
- **No time window.** Dustin released the laptop for all of Oct 29 (via the coordinator). The lane takes an optional cutoff, `KXR_UNTIL_EPOCH`, which is unset by default.

## 3. Where R6 can change these games (fixed before any game)
**What "reached" means here.**
- A change **can act** in a row when that row's cards (either seat), km3's search or kx3's play-outs can bring the changed code to a different result.
- A change is **reached** when its changed code runs in the row but, by reading, returns what the old code returned.
- Only rows where a change can act would be named in `rows.json`.

**Sources.**
- The read-only check (git grep, git show and git diff over main-4d48844 4d488449 → S) and its results are in `REACH.json`.
- `git diff --stat 4d488449 S -- engine/src` lists 38 files. Every one of them belongs to one of the changes below, or is used by no game: the generator, `card_ids.rs`/`database.rs` data, `python_bindings.rs`, `tui/`, `temp_deck.rs`, `cli_preflight.rs`, goldfish.
- `engine/Cargo.lock` and `Cargo.toml` are unchanged.

| # | R6 change (main-4d48844 → S) | what a game must hold for it to act | in the 6 decks, the 8 lists, kx3's pool | verdict |
|---|---|---|---|---|
| 1 | The dual-type seam: a printed type set. The chokepoint `State::pokemon_energy_types` reads `card.get_types()`. 26 type reads now use `has_printed_type` / `is_type`; they include the 12 in-play checks and km3's two (row 5). | A card with a second printed type. | None: no card id of the lists or the pool has `secondary_energy_type`. Their `database.json` entries are unchanged. | **Reached in every row** (Weakness, type bonuses and cuts; see below). **Cannot change a result:** for a single-type card, `printed_types()` = `[energy_type]` and `has_printed_type(t)` ⇔ `energy_type == t` (`models/card.rs`). |
| 2 | B4b and P-B 095-103 data; the 82 B4b Trainer reprint arms. | A B4b or P-B 095-103 printing. | None (git grep). The only P-B card is Frigibax P-B 037 in t-suicune. | **Reached:** the arms of Copycat (all 14 lists), Field Blower, Lucky Ice Pop, Flame Patch, Clemont, Quick-Grow Extract, Korrina and Mesagoza only *gain* B4b ids. The old ids reach the same functions. |
| 3 | C1/SP1/P-C data; #431 (18 ex designs); #432 (6 Supporters). Adds 9 mechanic-map texts and new mechanics: Mew ex's Secret Guidance, Lycanroc ex's counterattack, Lorelei's turn effect, Serena's Choice's new action, Rika, Lana, Blue's Provocation and Rising Star. | A C1/SP1/P-C printing, or an old card with one of the 9 added texts. | None. No list or pool card carries an added text. | **Cannot act.** |
| 4 | The Ultra Beast list. Adds Buzzwole, Blacephalon ex and Guzzlord, and "Ultra Necrozma" becomes "Ultra Necrozma ex". The readers are Lusamine, Ultra Thrusters, Beast Wall, Beastite and km3's Lusamine pricing. | One of those names and one of the readers. | None (git grep: no Ultra Beast name, Lusamine, Ultra Thrusters, Beast Wall or Beastite). | **Cannot act.** |
| 5 | km3's type-set reads: `fuel_credit.rs:110` (Flame Patch's [R] target) and `value_functions.rs:1604` (the "+X if the defender is [X]" bonus). | A dual-type card. | Flame Patch is in 06 and t-blaziken. No list card has an ExtraDamageIfDefenderType text. | **Reached** in the rows of 06 and v t-blaziken. Same value for single-type cards. |
| 6 | Astonish's audited text, C1 012 only (`AUDITED_TEXTS` 62 → 63, sorted, binary-searched). | C1 012 Amoonguss. | None. | **Cannot act.** Every other text's lookup is unchanged. |
| 7 | The random player's weight 5 for `TakeTopDeckCardAndShuffle`. | The random player (code `w`) and that action, which only Serena's Choice makes. | Neither km3 nor kx3 uses that player. No Serena's Choice. | **Cannot act.** |
| 8 | INFORMATION_MODEL v8 (`observation.rs`): the constant, and Serena's Choice joins Pokédex's top-3 reveal. | Serena's Choice. | None. The constant is not written to a game record, and neither the harness nor kx3's files read it. | **Cannot act.** |
| 9 | The card-support refusal (`deckgym::card_support`; `strength run` and `strength selfcheck`, before any game, reading only the card database, no RNG). | A CardNotFound or Missing* card. | None. All 101 card ids are old printings, and every older card is Complete or RulesUnverified (the R6 lane's card_status check). | **Cannot act.** It would stop a run before any game, not change a game. |
| 10 | The tests-only fold: `#[cfg(test)]` modules of `hooks/core.rs` and two `engine/tests` files. | — | — | Not in the program. |

**Two incidental paths the check found (reached, no decision changes by reading):**
- **rare_candy's name tables.** They are built once by iterating every `CardId` (`card_logic/rare_candy.rs`).
  - The new printings that share names with list cards make the tables longer. `get_highest_evolutions` then returns each available Stage 2 card more often for these Basics:
    - Torchic: 2 → 4 (06, t-blaziken);
    - Treecko: 2 → 5 (t-sceptile);
    - Caterpie: 3 → 5 (t-sceptile);
    - Frigibax: 1 → 3 (t-suicune).
  - As sets, the tables are unchanged. The Rare Candy pair table only gains 6 pairs, none with a Basic of the lists.
  - The bots' uses are insensitive to repeats:
    - a fold to the maximum (`evolution_potential`);
    - the first element (the online score);
    - `any` (`is_attacker`);
    - `is_empty` (`opening_class`);
    - `min_by_key`, which returns the first of equal threat candidates, and a form index that is looked up again in the same list (`threat_candidates`, `kd_attacker`, `threat_attacker_stage_and_types`).
  - The Oct 28 ABC lane's km3 replays on the same engine were "v f: SAME (0 deals)". Tonight's lane on S repeats them.
- **New enum variants.** `SimpleAction` gains its first variant, and `Mechanic` and `TurnEffect` gain one each. `CardId` gains 698 variants, which shifts the discriminants of P-A and P-B ids.
  - No source orders by them: `CardId` has no `Ord`, and derived orders keep the old variants' relative order.
  - No source hashes them with a fixed hasher: there is no DefaultHasher, Fx or AHash in `engine/src` or `rl/strength/src`, and the maps use RandomState, whose order already varies by process.

**Where the bots look.**
- km3's search uses the real opponent list or Unknown cards (`observation.rs`).
- kx3's play-outs draw from `playout_pool.rs` (d513e37b's, unchanged): 16 lists, which are the 8 t-lists and their research twins. That is 66 card ids, all among the lists' 101, with no new printing. KX_EXTRA_LISTS stays unset.
- So no new card enters any position a bot considers.

**Result: no row is named.** `rows.json` is `{}`, and every one of the 202 kx3 and 202 km3 games is expected to replay exactly.
- **The rows the seam's changed reads run in.** Every row runs them (Weakness), and some cards run more:
  - Leaf Cape: t-sceptile, t-vespiquen;
  - Deceptive Needle: t-hydreigon, t-weezing;
  - Chase Order's bench filter: t-vespiquen;
  - Quick-Grow Extract, Fragrant Forest, Erika: t-sceptile;
  - Misty, Turbo Shark: draft A;
  - Flame Patch: 06, t-blaziken;
  - Fighting Coach, Korrina, Arena of Antiquity: t-lucario;
  - Inflatable Boat, Ice Maker: t-suicune;
  - Bombirdier: t-hydreigon.
- **What a pass also shows.** It is evidence for RUN5's refactor rule ("games that reach the touched paths replay identically") on these rows, as far as their games actually play those cards. The logs do not trace which sites ran.

## 4. The reading (fixed now)
`compare_dev.py` compares each game with the development run's game on the same key. It compares content without timing (`split_collect.py`'s `content`), per arm and per row. With `rows.json` empty, any changed game is printed as "NOT A NAMED ROW: a stop", with its first differing logged decision.
- **Pass.** All of these hold:
  - every one of the 202 kx3 and 202 km3 games equals the development run's;
  - every seed equals the development run's, and no game is missing, unreadable or outside the development run;
  - `compare_dev.py` exits 0 ("RESULT: every changed game is in a named row", which with no named row means no game changed);
  - each registration's two self-checks equal the pin's texts;
  - each registration's 14 deck and list files have the development run's sha256.
- **Stop.** Any one of these:
  - any changed game (no row is named, so no change is explained in advance);
  - any missing or unreadable game;
  - a self-check of any registration that differs from the pin's;
  - a deck or list file whose sha256 differs;
  - the program's sha256 not being `23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378`.

  A stop goes to the coordinator and Dustin as it is (coordinator-076). The lane only writes it clearly: a "STOP" line in its log, `STOP.txt` in its state folder, and the first line of `LANE_RECORD.txt`. The session tells them. Nothing is activated. No attribution build is planned in advance: if games change, the cause is outside section 3, and what to build to find it is decided after the stop. The first suspect for rows with Torchic, Treecko, Caterpie or Frigibax is the rare_candy path above.
- **What a pass allows (runbook step 15).** The re-pin: the slow report's program moves to `/home/dacz8976/kx_r4/strength`, and its pin and docs are regenerated on main by an adapted `slowpin_main.py`, then the pin tests run. The pin's new fields are:
  - `program_sha256` and `selfcheck_measured_on_sha256`, both `23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378`;
  - `engine_ref` K and `engine_tree` `cd970db60aa5df7e9db9d7479e88f87190dab2c3`;
  - `harness_source_sha256` `c4f7da21…`;
  - `pilot_label` "kx3 (d513e37b's files, on main-affe56e)";
  - the `engine` and provenance texts;
  - the self-check texts, unchanged.

  This happens after the coordinator's review and only once main carries S's engine. Dustin's words of Oct 21 and his Oct 28 "Yes" cover it.

## 5. Order
1. **Before the lane** (`prepare.sh`): it runs after the R6 night job ended with strength_K, sc_km3 and sc_kx3 done, and after K reached origin.
   - The worktree `/home/dacz8976/r5_w` is reused: it must be clean, and its branch and commit are recorded before it switches to the new branch.
   - This spec, `rows.json`, `REACH.json`, `make_replay_configs.py`, the configs it writes, `compare_dev.py`, `lane_kxr_r6.sh` and `prepare.sh` are committed on `laptop/kx3-replay-r6-2026-10-29`.
   - Guardrail A runs, then they are pushed. The coordinator reviews them.
2. **The lane** (`lane_kxr_r6.sh`):
   1. The three registrations, each replaying both self-checks. They are committed, checked by Guardrail A and pushed, and the push is verified, before any game.
   2. The games: replay_b at 3 threads with replay_a at 2, then replay_c at 2.
   3. `compare_dev.py` writes `COMPARE_DEV.txt`.
   4. The games, `COMPARE_DEV.txt` and `LANE_RECORD.txt` are committed, checked by Guardrail A and pushed.
   - **Guardrail A** (coordinator-076, public repository): before each push, no path of a commit to be pushed may contain "exam", "judge" or "transcript", in any case. "examples" is allowed.
3. **The reading** (`READING.md`, with "**Verdict: pass.**" only on a pass), then the re-pin on main, or the stop.
