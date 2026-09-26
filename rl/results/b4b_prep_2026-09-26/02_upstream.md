# 02 - What upstream deckgym-core already has for B4b (checked 2026-09-26)

Scope: plan item A5 (B4b as a data refresh plus a few card implementations; upstream code-merge trial before the C1 series). This file only reports what upstream has and how it adds a set. Nothing in `engine/` was modified. Every git command run locally was read-only (git is not on PATH; the GitHub Desktop copy at `C:\Users\dacz8\AppData\Local\GitHubDesktop\app-3.6.6\resources\app\git\cmd\git.exe` was used).

## Short answer

| Question | Answer | Evidence |
|---|---|---|
| Does upstream have B4b card data? | **No.** `database.json`, `src/card_ids.rs` and `src/database.rs` on `main` contain zero "B4b" strings. Newest set in all three is B4a (110 cards). | Exact fetch and search of the raw files, see section 2 |
| Does upstream implement B4b's new mechanics? | **There are none to implement.** The set is reprint-only (official page and GameWith, section 4). Every reprinted effect text is already implemented upstream and in the fork. The two Supporter reprints (Copycat, Elesa) will still need new `CardId` match arms because Trainer dispatch is by card id, not by text. | Section 4 |
| Any upstream PR or commit mentioning B4b? | **None.** 0 pull requests match "B4b"; no commit on `main` mentions B4b, Deluxe or Mega Garchomp. | Section 3 |
| Upstream head right now | `f01e695186843b5ef9ab0eec91749bfc6e528fc3`, 2026-09-17, "Merge pull request #368 from rook-productions/pr/01-attacks-d" | https://api.github.com/repos/bcollazo/deckgym-core/commits?sha=main and https://github.com/bcollazo/deckgym-core/commits/main |
| Last upstream set-import commit | `eb71f845439872e26ce38d4988b5127381465fa1`, 2026-08-27, message "b4a" | https://github.com/bcollazo/deckgym-core/commit/eb71f845439872e26ce38d4988b5127381465fa1 |
| Fork data files vs upstream | The fork's `engine/database.json`, `engine/src/card_ids.rs` and `engine/src/database.rs` are **identical to upstream main** once CRLF is normalised (the fork copies use CRLF). So a B4b data refresh is a straight copy of upstream's three files once its "b4b" commit lands, or a regeneration from `database.json`. | Section 5 |

A caution about method: my first look at upstream `src/card_ids.rs` went through WebFetch's summariser, which reported variants `B4b001Scyther` .. `B4b110MegaCharizardXEx`. That was invented. An exact download of the same file into memory and a regex count found **0** lines matching `^\s*B4b\d`. Everything below is from exact string searches, not summaries, unless marked.

## 1. Upstream commits on `main`

Source: https://api.github.com/repos/bcollazo/deckgym-core/commits?sha=main (JSON) and https://github.com/bcollazo/deckgym-core/commits/main (HTML). Both agree; the HTML page's newest commit is dated Sep 17, 2026.

| Date (UTC) | SHA | First line |
|---|---|---|
| 2026-09-17 | f01e695186843b5ef9ab0eec91749bfc6e528fc3 | Merge pull request #368 from rook-productions/pr/01-attacks-d (36 attack effects across 59 printings, batch D) |
| 2026-09-04 | b9d5905c5467a612bc2e6f05e89270f974496a2d | Merge cov/attacks-d into pocket-lab |
| 2026-09-04 | b939472b6b5c021ebbc39064db11bfb386f26e8d | Do not run attacker-sourced follow-up effects after the attacker is KO'd |
| 2026-09-04 | 296d95035c90593cd6417e68179f21f09e63f471 | Implement Budew's Prickly Powder |
| 2026-09-04 | 3935cf186ec6bdd6b3db87d90c62fd5c730c71eb | Implement Delcatty's Energy Blender |
| 2026-09-04 | 35f4b9a766179997de95f03c7aa5b36c408c1495 | Implement 5 attack effects needing new engine state |
| 2026-09-04 | 980c2ab926b82a42080df4c64effde80a159a330 | Implement 15 new attack mechanics |
| 2026-09-04 | e4b8761678f8dbba100572e43fc6529bdd8342af | Implement 11 attack effects reusing existing mechanics |
| 2026-08-30 | fda48391a4747c7d9085e6a95520b731cee0b546 | Merge pull request #364 (Gouging Fire / Walking Wake / Raging Bolt / Drampa) - this is the sha `engine/UPSTREAM.md` calls "Fetched main" |
| 2026-08-29 | a2ae90f07d... | Merge PR #363 Oricorio / Happiny next-turn damage |
| 2026-08-28 | 9f210a296e... | Merge PR #362 Serperior and Tinkaton |
| 2026-08-27 | 7e6317941... / b7b4cee786... | Merge PR #360 (B4a ex cards + Regidrago) and PR #361 (B4a Trainer cards) |
| 2026-08-27 | eb71f845439872e26ce38d4988b5127381465fa1 | **b4a** (the B4a data import) |

Upstream has moved by 8 commits (one merged PR, #368) since the sha recorded in `engine/UPSTREAM.md`. None of them is a data import.

## 2. Exact search of the upstream data files (fetched 2026-09-26 from `main`)

| File | Size | "B4b" hits | "B4a" hits | Notes |
|---|---|---|---|---|
| https://raw.githubusercontent.com/bcollazo/deckgym-core/main/database.json | 2,244,950 bytes, 87,484 lines | **0** | 220 (110 `"id": "B4a ..."` entries) | first entry A1 001 Bulbasaur |
| https://raw.githubusercontent.com/bcollazo/deckgym-core/main/src/card_ids.rs | 272,894 bytes, 7,780 lines | **0** enum variants, 0 mentions | 110 variants, last `B4a110TeamRocketsGoozooka` | header: "This is code generated from the database.json by card_enum_generator.rs. Do not edit manually." |
| https://raw.githubusercontent.com/bcollazo/deckgym-core/main/src/database.rs | 3,455,047 bytes, 86,366 lines | **0** | 330 | generated file |

Variant counts per set prefix in upstream `card_ids.rs`: A1=286 A1a=86 A2=207 A2a=96 A2b=111 A3=239 A3a=103 A3b=107 A4=241 A4a=105 A4b=379 B1=331 B1a=103 B2=234 B2a=131 B2b=117 B3=234 B3a=109 B3b=106 B4=233 B4a=110. Promo-B runs to `PB094Meowstic` (fork copy `engine/src/card_ids.rs` line 3888; the fork file is identical to upstream's, section 5). There is no Mega Garchomp ex anywhere in the database (no `"name": "Mega Garchomp ex"` in the fork's identical `engine/database.json`).

## 3. Pull requests

- https://github.com/bcollazo/deckgym-core/pulls?q=is%3Apr+B4b shows "No pull requests matched your search" (0 open, 0 closed). The API search https://api.github.com/search/issues?q=repo:bcollazo/deckgym-core+B4b returns `total_count: 0`.
- Search for Garchomp / Deluxe / Meloetta / Fidough / reprint (https://api.github.com/search/issues?q=repo:bcollazo/deckgym-core+Garchomp+OR+Deluxe+OR+Meloetta+OR+Fidough+OR+reprint): 13 hits, none about B4b. The Meloetta hit is PR #160 "B2 Implementations" (Feb 2026, the original B2 070 implementation); the Garchomp hits are Cynthia (#294) and the A2 Garchomp ability (#221).
- Open PRs on 2026-09-26 (https://api.github.com/repos/bcollazo/deckgym-core/pulls?state=open): #381 Team Rocket's Magmar/Slowpoke (DoctorFun7), #380 Team Rocket's Electrode Destiny Burst (bcollazo), #379 Special Condition and win-condition rules vs the in-app Battle Guide (rook-productions, 35 tests), #378 damaged-bench bonus attack fix, #376 Regice Crystal Body / Alolan Muk Power of Alchemy. PR #372 (36 discard/mill/coin-flip attack effects, batch A) also reports `state: open` at https://api.github.com/repos/bcollazo/deckgym-core/pulls/372 although the summarised open-PR list did not show it (unverified which listing is right; it does not matter for B4b). None of these touch card data.
- Worth knowing for the merge trial: #379 changes Special Condition and win-condition rules; the fork has its own status-restriction work (`engine/UPSTREAM.md` lines 5, 12). That PR, if merged, lands in exactly the conflict areas UPSTREAM.md lists.

## 4. B4b content and whether the mechanics exist

Set facts (given by the task, checked against the two cited pages):
- https://www.pokemon.com/us/news/pokemon-tcg-pocket-deluxe-pack-mega-coming-soon : "Deluxe Pack: Mega", releases Tuesday September 29, 2026 at 6:00 p.m. PDT; the page says it "features many cards introduced in previous expansions, from Mega Rising to Ruler of the Skies, including reissues of every four-diamond card".
- https://gamewith.jp/pokemon-tcg-pocket/578648 : "High Class Pack MEGA", September 30, 2026 10:00 JST; states 新規性能のカードはなし (no cards with new performance) and that everything is a reprint or a same-text alternate art. New-artwork list on that page: Copycat, Elesa, Mega Charizard X ex, Mega Lucario ex, Mega Gardevoir ex, Mega Altaria ex, Mega Venusaur ex, Meloetta, Eevee, Fidough, plus 13 mirror-foil variants. (The task named the five non-Mega ones; GameWith adds the five Mega ex.)

Every one of those texts already exists in the databases and is dispatched:

| Reprint of | Text | Upstream implementation | Fork implementation |
|---|---|---|---|
| Meloetta B2 070, ability Strange Singing | "At the beginning of your turn, if this Pokémon is in the Active Spot, put a random [P] Pokémon from your deck into your hand." | `src/actions/effect_ability_mechanic_map.rs` (1 hit) | `engine/src/actions/effect_ability_mechanic_map.rs:82` |
| Eevee B1 184, ability Boosted Evolution | "As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it." | `src/actions/effect_ability_mechanic_map.rs` (1 hit) | `engine/src/actions/effect_ability_mechanic_map.rs:37`; timing check via `AbilityMechanic::CanEvolveOnFirstTurnIfActive` at `engine/src/move_generation/mod.rs:199-203` |
| Fidough B3b 034, attack Puppy Pile | "Reveal all of your Pokémon in play and in your hand that have the Puppy Pile attack, and this attack does 20 damage for each..." | `src/actions/effect_mechanic_map.rs` (2 hits) | `engine/src/actions/effect_mechanic_map.rs:3330-3332` |
| Copycat B1 225 (Supporter) | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | `src/actions/apply_trainer_action.rs` (Copycat 3 hits), `src/move_generation/move_generation_trainer.rs` (2 hits) | `engine/src/actions/apply_trainer_action.rs:236` (`CardId::B1225Copycat \| CardId::B1270Copycat => ...`), `engine/src/move_generation/move_generation_trainer.rs:239` |
| Elesa B3b 066 (Supporter) | "Return all Pokémon Tools attached to each Pokémon (both yours and your opponent's) to their owner's hand." | `src/actions/apply_trainer_action.rs` (Elesa 2 hits) | `engine/src/actions/apply_trainer_action.rs:304`, `engine/src/move_generation/move_generation_trainer.rs:321` |
| Mega ex cards (B1 102 Mega Altaria ex, B1a 004 Mega Venusaur ex, B2 066 Mega Gardevoir ex, B2b 009 Mega Charizard X ex, B3 081 Mega Lucario ex) | same text as originals | attack/ability dispatch is by effect text, so new printings need no code | same |

The one code consequence: Pokémon attacks and abilities are matched by effect text (`effect_mechanic_map.rs`, `effect_ability_mechanic_map.rs`), so new printings of Meloetta, Eevee, Fidough and the five Mega ex work as soon as the data is in. Trainers are matched by `CardId`, with fallbacks `_ => panic!("Unsupported Trainer Card")` at `engine/src/actions/apply_trainer_action.rs:329` and `_ => None` at `engine/src/move_generation/move_generation_trainer.rs:345`. A B4b Copycat or Elesa played in a game would hit those fallbacks until the new ids are added to the two match arms (that is the "few new card implementations" of plan item A5, and it is the same edit upstream will make; upstream's PR #361 is the pattern, section 6).

Mega Garchomp ex (Promo-B, not in this set; task states Falling Edge 190, "Discard 2 random Energy from this Pokémon."): not in either database. The attack text is already mapped: upstream `src/actions/effect_mechanic_map.rs` has exactly one `"Discard 2 random Energy from this Pokémon."` entry (plus two longer variants), and the fork has it at `engine/src/actions/effect_mechanic_map.rs:178`. The text is on Giratina A2a 061 (Crisis Dive, 120) and Rayquaza B4 119 (Dragon Impact, 140) in upstream `database.json`. So when that promo is imported, no new mechanic is needed; only data. Whether the engine treats a Stage 2 Mega ex differently from the existing Stage 2 ex and Mega ex cards was not checked.

## 5. Fork state versus upstream (read-only checks)

- Repo root is `C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim` (the engine is a subdirectory, not its own repo). Branch `main`, HEAD `8845ac6c85b6cf3525a6f1ebb7ce03138e2acfdd` (2026-09-26).
- Remotes: only `origin` = https://github.com/dacz8976-creator/PocketDeckSim.git. **There is no `upstream` remote on this machine**, so the `git fetch upstream` / `git diff upstream/main` steps in `engine/UPSTREAM.md` line 14 cannot be run here as written; they were done in a cloud session. The sha UPSTREAM.md calls "Fetched main" (`fda4839`) is not in the local object store (`git cat-file -t` returns nothing). The cloud merge trial should add the remote itself.
- Merge base: `engine/UPSTREAM.md` line 3 says `8b40f55d889b89634467cca7da153114789ffdf4` (2026-07-30). Confirmed: `git merge-base --is-ancestor 8b40f55... HEAD` exits 0; upstream's compare API https://api.github.com/repos/bcollazo/deckgym-core/compare/8b40f55d889b89634467cca7da153114789ffdf4...main reports upstream `main` is **104 commits ahead, 0 behind** that base. The base commit is "Merge pull request #342 from bcollazo/claude/b4-card-implementations-b3b03c - Implement B4 cards: Raichu, Dustox, Cradily". The fork has 242 commits after the base (whole repo, not only engine).
- The B4a data reached the fork by its own import, not by merging upstream: pickaxe `git log --all -S'"B4a 001"' -- '*database.json'` finds `12938ca` (2026-09-09, "Preserve accumulated Pocket engine work through B4a before consolidation") and `012f3bc` (2026-09-24, "Upload existing project"); `engine/` itself was added by `02a5b24` (2026-09-24). Matches UPSTREAM.md line 3.
- File comparison (UTF-8 read, CRLF normalised, against upstream `main`):

| File | Upstream lines | Fork lines | Identical after CRLF normalise |
|---|---|---|---|
| `database.json` | 87,484 | 87,484 (87,483 CRLF) | **yes** |
| `src/card_ids.rs` | 7,780 | 7,780 (7,779 CRLF) | **yes** |
| `src/database.rs` | 86,366 | 86,366 (86,365 CRLF) | **yes** |
| `src/actions/effect_mechanic_map.rs` | 2,880 | 3,699 (LF) | no: 244 lines only upstream, 1,063 only fork |
| `src/actions/effect_ability_mechanic_map.rs` | 639 | 1,012 (CRLF) | no: 61 lines only upstream, 434 only fork |

So the three generated/data files are exactly upstream's (the fork's B4a data was upstream's B4a data). The mechanic maps are where the fork diverges, which is what UPSTREAM.md line 11 says ("merge new upstream entries instead of replacing either map"). Note the mixed CRLF/LF state across these files; a copy-in of upstream files should keep whatever line-ending policy the identity replay was built with, or the diff noise UPSTREAM.md mentions ("preserved CRLF churn") returns.

## 6. How upstream adds a set

Upstream's set imports are single commits by Bryan Collazo touching only generated data files, followed days later by separate implementation PRs.

Data-import history for `database.json` (https://api.github.com/repos/bcollazo/deckgym-core/commits?sha=main&path=database.json): eb71f845 "b4a" 2026-08-27; edf22f2f "B4" 2026-07-29; 24e7ab90 "Everyday Wonders" (B3b) 2026-06-30; 0f0a6ba3 "B3a Cards" 2026-05-28; 3180e59f "Fix Database" 2026-05-26; d0eafdac "B3 Cards" 2026-04-27; d924c6db "B2b Cards" 2026-03-26; 1c3094a3 "Add Promo-B" 2026-03-06; 91be4d25 "B2a" 2026-02-26; af457b72 "B2 Cards" 2026-01-28; ... The same commits appear in the histories of `src/card_ids.rs` and `src/database.rs` (path-filtered API calls), so all three always change together.

**Example (B4a-era): `eb71f845439872e26ce38d4988b5127381465fa1`, "b4a", 2026-08-27T12:18:29Z, parent `a0a39124...`** (https://api.github.com/repos/bcollazo/deckgym-core/commits/eb71f845439872e26ce38d4988b5127381465fa1). Stats: +5,481 / -6.
- `database.json` +2,685 / -0
- `src/card_ids.rs` +236 / -0
- `src/database.rs` about +2,560 / -6 (the summariser listed only the first two files; the third is derived from the commit's total stats and confirmed by the `path=src/database.rs` history, which lists this commit)

Second example for the same shape, `edf22f2f8014b6631784933986f631a1750a5952` "B4" 2026-07-29 (https://api.github.com/repos/bcollazo/deckgym-core/commits/edf22f2f8014b6631784933986f631a1750a5952): `database.json` +5,435, `src/card_ids.rs` +482, `src/database.rs` +5,376 / -6; total +11,293 / -6 matches exactly (233 B4 ids plus 8 Promo-B).

Timing pattern: B4 imported 2026-07-29, B4a imported 2026-08-27, both within about a day of the in-game release (release dates not independently verified here). If the pattern holds, a "b4b" commit should appear around Sept 29 to Oct 1.

The generation recipe is in upstream's README (https://raw.githubusercontent.com/bcollazo/deckgym-core/main/README.md, section "Generating database.rs"), and the fork's copy is word-for-word the same at `engine/README.md` lines 204-234:
1. update `database.json`
2. `cargo run --bin card_enum_generator > tmp.rs && mv tmp.rs src/card_ids.rs && cargo fmt`
3. `cargo run --bin card_enum_generator -- --database > tmp.rs && mv tmp.rs src/database.rs && cargo fmt` (with a temporary `_ =>` arm so it compiles mid-way)
4. `cargo run --bin card_enum_generator -- --incremental-attack-map` and `-- --incremental-ability-map`, pasted by hand into the two mechanic maps (only needed when a set brings new effect text; B4b brings none)
The generator lives at `src/bin/card_enum_generator.rs` (463 lines upstream; fork copy at `engine/src/bin/card_enum_generator.rs`).

Implementation PRs that followed the b4a import, both merged 2026-08-27, show which files a "few new card implementations" touch:
- PR #361 "Implement B4a Trainer cards" (https://api.github.com/repos/bcollazo/deckgym-core/pulls/361/files), 18 files: `src/actions/apply_trainer_action.rs` (+131), `src/move_generation/move_generation_trainer.rs` (+36), `src/actions/apply_stadium_action.rs`, `src/actions/apply_action.rs`, `src/actions/types.rs`, `src/effects.rs`, `src/hooks/retreat.rs`, `src/move_generation/mod.rs`, `src/players/weighted_random_player.rs`, `src/stadiums.rs`, `tests/trainers.rs`, `tests/stadiums.rs`, and five new `tests/trainers/*_test.rs` plus `tests/stadiums/arcade_test.rs`. This is the shape a B4b Copycat/Elesa id-arm change takes (two source files plus a test).
- PR #360 "Implement B4a ex cards + Regidrago" (https://api.github.com/repos/bcollazo/deckgym-core/pulls/360/files), 19 files: `src/actions/effect_mechanic_map.rs` (+31/-1), `src/actions/effect_ability_mechanic_map.rs` (+12), `src/actions/attacks/mechanic.rs`, `src/actions/abilities/mechanic.rs`, `src/actions/apply_attack_action.rs` (+108), `src/actions/apply_abilities_action.rs`, `src/actions/apply_action.rs`, `src/actions/types.rs`, `src/hooks/core.rs`, `src/move_generation/move_generation_abilities.rs`, `src/players/weighted_random_player.rs`, `tests/pokemon.rs` and seven new `tests/pokemon/*_test.rs`. Not needed for B4b (no new Pokémon text).

## 7. What this means for the A5 refresh (no action taken)

1. Wait for upstream's "b4b" data commit (watch https://github.com/bcollazo/deckgym-core/commits/main/database.json). Until then there is nothing to pull; the fork's data is already equal to upstream's.
2. When it lands: copy upstream's `database.json`, `src/card_ids.rs`, `src/database.rs` into `engine/` (they are currently identical, so the only diff will be B4b), or regenerate from `database.json` with the README recipe. Decide the CRLF policy first (section 5).
3. Add the B4b Copycat and Elesa ids to the two `CardId` match arms (`engine/src/actions/apply_trainer_action.rs:236,304`, `engine/src/move_generation/move_generation_trainer.rs:239,321`) with a small test each, following PR #361. Nothing else should need code.
4. Acceptance as planned: replay `rl/results/engine_identity_2026-09-25/` (contains `COMMIT`, `identity.txt`, `compare.py`, `k3_500.jsonl`, `kp3_500.jsonl` and their `.txt` summaries) game for game; then the card-effect pass on the reprints (which is really a check that the new ids resolve to the old behaviour).
5. The code-merge trial is a separate, bigger job: upstream is 104 commits past the merge base, the fork's mechanic maps carry about 1,000 fork-only lines, and open PR #379 (status/win rules) sits in the fork's conflict areas. Do it in the cloud with an `upstream` remote, as UPSTREAM.md line 14 says, and not around an A/B.

## 8. Unverified or not checked

- The B4b set code itself. Upstream will use whatever prefix its data source uses; "B4b" follows the B3b precedent but is an assumption until the commit exists.
- Exact in-game release dates for B4 and B4a (used only for the "import lands near release" pattern).
- The task's Mega Garchomp ex stats (Stage 2, HP 220, Falling Edge 190, Promo-B Vol. 13, mid-to-late October drop event) and whether the engine needs anything for a Stage 2 Mega ex. Only the attack text was checked.
- Whether PR #372 is open (API says open; the summarised open-PR list omitted it).
- The third file of commit eb71f845 (`src/database.rs`, about +2,560) is derived from the commit's totals plus the file's path history, not from a file-by-file listing.
- The "14,000-game" size of the identity replay; I only listed the directory's files.
- The pokemon.com and GameWith pages were read through WebFetch summaries (the Japanese quote is as the summariser reported it). The set being reprint-only was taken from those two pages and the task; no third source was checked.
