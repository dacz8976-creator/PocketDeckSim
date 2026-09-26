# B4b refresh procedure (plan item A5), written 2026-09-26

**Who wrote this and why.** Fable's overnight B4b prep workflow (session "Deck pilot bot project review"), on Dustin's
Sept 25 night instruction to keep the approved plan moving while he sleeps; the item is A5 in `rl/RUN5.md` lines 357-359
("B4b as a data refresh with bit-for-bit reproduction of the k3 table plus a card-effect pass, and an upstream code-merge
trial in the cloud before C1") and `docs/REVIEW_2026-09-24_direction.md` line 162. It is a procedure for the three working
sessions, not a result: nothing here has been built, run or played. **Hard rule in force (REVIEW line 134, 01:30 Sept 26):
no `cargo`, no engine binary, no game, no background process while the laptop trains; everything below was read from files
and git history, and any claim that would need a build says "unverified (no build allowed tonight)".** The engine was not
modified. Inputs: the three sibling notes in this folder, `01_set.md` (what B4b is), `02_upstream.md` (what upstream has),
`03_fork.md` (how the fork adds a set, every file a refresh touches). Paths are relative to
`C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\` unless absolute. Repo HEAD when written: `4924008` (00:53 Sept 26);
`engine/` at HEAD is identical to the official build's commit `7fc6ccb` (`git diff --stat 7fc6ccb HEAD -- engine/...` empty,
read-only check via GitHub Desktop's git this pass; same as `03_fork.md` section 1).

## 1. Plain-language summary

**What B4b is.** "Deluxe Pack: Mega", the B-series counterpart of last year's A4b "Deluxe Pack: ex". It goes live Tuesday
September 29 at 6:00 pm PDT (September 30, 01:00 UTC / 10:00 JST) and runs about a month; the next series, C1, follows on
October 28 (official: https://www.pokemon.com/us/news/pokemon-tcg-pocket-deluxe-pack-mega-coming-soon ; schedule:
https://www.pokemon-zone.com/sets/b4b/ and https://www.pokemon-zone.com/schedule/upcoming/ ; GameWith
https://gamewith.jp/pokemon-tcg-pocket/578648). **It is a reprint-only set**: every card in it is a card that already exists,
with the same text, sometimes with new artwork or a mirror-foil finish (official page: reissues of every four-diamond B1-B4
card; GameWith: "no cards with new performance"; details and the full source table in `01_set.md`). (skeptic: GameWith's
B4a-exclusion sentence reads verbatim 「ハイクラスパックexは『ロケット団の野望』のカードは排出されません。」, i.e. it names last
year's pack; the B1-B4 range rests on the official page's "from Mega Rising to Ruler of the Skies"; `04_skeptic.md` F6.) The five cards the plan
called "new" (Meloetta, Eevee, Fidough, Copycat, Elesa) are new-art reprints of B2 070, B1 184, B3b 034, B1 225 and B3b 066
(`01_set.md` lines 29-42 and 100-113). **The only genuinely new card in the window is Mega Garchomp ex**, and it is not in
B4b: it is Promo-B Series Vol. 13, from a solo-battle Drop Event in mid-to-late October (`01_set.md` lines 32-35 and 159-163).
Its one attack text already exists on two other cards and is already implemented (`02_upstream.md` section 4). (skeptic: the
promo status rests on the official page's "B Series vol. 13 promo packs during the Mega Garchomp ex Drop Event" and GameWith's
verbatim 「PROMO-B 第13弾で入手」; GameWith's B4b pack page nevertheless lists メガガブリアスex among its eleven 新カード, so
step 0's script, not step 2, is what proves it is absent from the set list; `04_skeptic.md` F2, F7.)

**What that means for the simulator.** No new game mechanic. The job is a data refresh: add the B4b card entries, regenerate
the two generated Rust files, and add the new card numbers to the handful of places that list Trainer cards by number rather
than by text (at least Copycat and Elesa; the full list depends on the published set list; skeptic: by the fork's own A4b
precedent, 40 Supporter/Item printings over 19 names out of 60 A-series names, expect about 14 names and 30 printings from the
44-name B1-B4 pool, `04_skeptic.md` F3). No table game should change,
because none of the eight research decks carries a B4b card and no rule moves (`03_fork.md` bottom line 8). The acceptance
test is therefore an identity replay: the refreshed engine must replay all 14,000 k3 games and all 14,000 kp3 games of the
Sept 25 reference tables move for move, exactly as the Sept 25 engine switch did (`rl/results/engine_identity_2026-09-25/`).

**How big the job is (estimates, not measurements).** About **1 to 1.5 agent-days of work spread over 2 to 3 calendar days**,
which is at the low end of the plan's "one to three days" (REVIEW line 162) because there are no new mechanics: roughly half a
cloud day for the data files, the Trainer arms and their tests (upstream's own B4a data import was one generated commit,
`02_upstream.md` section 6; the Trainer-arm change is two source files plus a test per card, the shape of upstream PR #361);
a quarter laptop day for the second read; a quarter to half a WSL day for the release build, the replays (14,000 games per
pilot; B2e's README puts 48,000 games at about 1.7 hours per pilot at cloud speed, more on the laptop,
`rl/results/b2e_card_check_2026-09-26/README.md`) and the manifest switch; a quarter day for the `lib/` pins and the docs. The
calendar spread comes from waiting for the data (upstream's "b4b" commit or the Limitless list) and from the one-thing-at-a-time
rule on the laptop. Mega Garchomp ex adds about a quarter to half a day when its promo text is published in October. The
upstream code-merge trial (section 6) is a separate job, guessed at 2 to 4 cloud agent-days, unverified. (skeptic: the half
cloud day for arms and tests holds only if the same-as-base test is one table-driven test over all B4b Supporter/Item ids; with
the per-arm rule as written it is 28 to 60 Game-level tests and the figure is off by 2x or more, so budget one cloud day. The
replay cost is measured, not guessed: k3 1,792 s and kp3 1,561 s wall at cloud speed,
`rl/results/per_game_table_2026-09-25/timing.txt` line 1 and `rl/results/public_pricing_2026-09-25/README.md` line 64, about an
hour for both; `04_skeptic.md` F3, F10.)

**What cannot be simulated until it is done.**
- Any deck list written with a B4b card number (for example a B4b-numbered Copycat or Mega Altaria ex): the engine refuses an
  unknown id (`engine/src/deck.rs` line 174, "Card ID not found for id"), and the 0.7.2 add-on wheel will refuse it forever
  because that wheel is never rebuilt (root `CLAUDE.md`; `03_fork.md` section 5). Interim that needs no engine change: rewrite
  the list to the base printings with `lib/card_canon.py`'s `base_id`, since every B4b card has one (`03_fork.md` bottom line 9).
  Gameplay is the same card, so nothing is lost.
- Mega Garchomp ex, in any list: it has no entry in either database (`01_set.md` line 163), and cannot be added correctly until
  Limitless or the in-game card gives its Energy cost, weakness and retreat cost (unverified today; `01_set.md` line 191).
- Nothing else. Every other B4b card's play is already simulable through its base printing, and Season B4b ranked uses the same
  card pool as today plus, later, Mega Garchomp ex (`01_set.md` line 181).

## 2. The steps, in order, with owner and pinning test

Owners follow the plan's Owners line (`rl/RUN5.md` lines 397-399; `PROJECT_INSTRUCTIONS.md` lines 31-32): **the cloud session
builds** (engine items), **the laptop session second-reads** (tier 1) and coordinates, **the WSL session runs** on the laptop,
Dustin decides. Messages for the cloud go to Dustin as paste-ready blocks, since session messages to it do not land reliably
(REVIEW line 130, last sentence). The test convention for every new card behaviour is the engine's own: a Game-level test through
the public `Game` API using `get_test_game_with_board`-style helpers (`engine/CLAUDE.md` lines 4-8;
`engine/.claude/skills/implement-cards/SKILL.md` lines 141-143), the shape of `engine/tests/b4a_trainer_batch2_test.rs`.

**Ground rule for the whole refresh: the B4b commit contains data, generated files, id arms, tests and docs, and nothing else.**
No rules fix rides in it (the queued promotion-after-end-of-turn-KO repair, REVIEW line 132, and the rules/09 fixes are separate
commits with their own replays, section 3 step 3). No mechanic-map edit "while in there".

| # | Step | Files | Who | What pins it |
|---|---|---|---|---|
| 0 | **Wait for the data, then confirm reprint-only.** Watch https://github.com/bcollazo/deckgym-core/commits/main/database.json for a "b4b" commit (upstream's B4 and B4a imports landed within about a day of release, `02_upstream.md` section 6; skeptic: dates now verified against the Limitless set index, B4 30 Jul 26 vs upstream's "B4" commit 2026-07-29T05:59Z, about 19 hours before the 6 pm PDT launch, and B4a 27 Aug 26 vs "b4a" 2026-08-27T12:18Z, so start watching on Sept 28) and https://pocket.limitlesstcg.com/cards/B4b (404 on Sept 26). When either exists: fill the "???" numbers and the card count in `01_set.md`, and run `01_set.md`'s field-by-field script over the new entries (all fields except id, rarity, booster_pack must equal some existing printing; A4b precedent 0 of 379 differ, `01_set.md` lines 44-49). | `01_set.md` (update in place) | laptop (cheap, read-only) | The script prints 0 novel texts. If it prints any, the set is not reprint-only and that card takes the "new mechanic" path in step 2. (skeptic: this script is the reprint-only proof, step 2 is not, `04_skeptic.md` F2. It cannot see a wrong number-to-card assignment, a short count or a foil built from the wrong printing, F1: also check every B4b number's name and rarity against the Limitless B4b set page by script, with the count equal, and write the Limitless count into the PR beside the `card_status_cli_test.rs` number.) |
| 1 | **Data files.** On a branch: either copy upstream's `database.json`, `src/card_ids.rs`, `src/database.rs` into `engine/` (the fork's three are identical to upstream's today after CRLF normalisation, `02_upstream.md` section 5), or append the entries to `engine/database.json` and regenerate with the recipe in `engine/README.md` lines 204-234 (`cargo run --bin card_enum_generator > tmp.rs && mv tmp.rs src/card_ids.rs && cargo fmt`; `-- --database` for `database.rs`, with a temporary `_ =>` arm mid-way). Decide the CRLF policy first (open question 1) and record it. Expect the B4b variants between `B4a110TeamRocketsGoozooka` (`card_ids.rs` line 3677) and `PA001Potion` (3678); placement unverified until upstream's commit exists. | `engine/database.json`, `engine/src/card_ids.rs`, `engine/src/database.rs` | cloud | `cargo build --release` compiles; the regenerated files equal upstream's after `--ignore-space-at-eol` (if upstream's commit exists); `engine/tests/card_status_cli_test.rs` line 23 updated from 3879 to the new total and passing. |
| 2 | **Prove no new text.** `cargo run --bin card_enum_generator -- --incremental-attack-map` and `-- --incremental-ability-map` (README lines 224-234; generator lines 320-349 and 399-426). Save both outputs into the commit message or a file in this folder. | none expected (`effect_mechanic_map.rs`, `effect_ability_mechanic_map.rs` untouched) | cloud | Both commands print nothing. Any printed line = a genuinely new text: implement per `SKILL.md` with one Game-level test per mechanic, and say so in the PR, because that changes the "reprint-only" premise of every later step. (skeptic: empty output proves no new *text*, not no new card; a new card whose text is already mapped, which is exactly Mega Garchomp ex's case, `effect_mechanic_map.rs` line 178, prints nothing here and is caught only by step 0's whole-entry comparison; `04_skeptic.md` F2.) |
| 3 | **Id-keyed places.** Run `rg -n 'CardId::[AB][0-9]' engine/src --glob '!**/database.rs' --glob '!**/card_ids.rs'` (`03_fork.md` section 3) and check every hit against the published B4b list. Known arms: Copycat `engine/src/actions/apply_trainer_action.rs` line 236 and `engine/src/move_generation/move_generation_trainer.rs` line 239; Elesa lines 304 and 321; every other B4b Supporter or Item on the list gets the same treatment (fallbacks: `panic!("Unsupported Trainer Card")` at 329, `_ => None` at 345). **Each B4b arm must call the same `can_play_*` helper and effect function as its base printing**; that is the one code change in this refresh that could move an identity-replay game (`03_fork.md` section 7; skeptic: the data itself also reaches k3's score through `rare_candy.rs`'s per-printing name lists, neutral today because every consumer takes a max, a first or an any, section 3 step 3 and `04_skeptic.md` F5). Also, if the list includes them: coin-flip Trainers and the Mesagoza/Arcade activators in `engine/src/actions/trainer_coin_plan.rs` lines 46-101, Researcher `team_rockets_researcher.rs` 129, Misty `engine/src/state/mod.rs` 365; Victini's RulesUnverified caveat `engine/src/card_validation.rs` lines 96-97 (Victini is on the foil list); Haxorus for Iris, `engine/src/actions/apply_action_helpers.rs` 638; Dragalge ex in the public-reply refusal list, `engine/src/players/public_reply.rs` 617-627. | the files named | cloud | One Game-level test per new Trainer arm (play the B4b id from a set board; assert the public state), plus one "same as base" test per arm: the B4b id and the base id played from identical states give identical states. For the id lists: `card_status_cli_test.rs` lines 28/44/54 and `engine/tests/card_qualification_test.rs` lines 11-13 updated (Victini RulesUnverified); a refusal test for the B4b Dragalge ex in the public-reply certificate if none exists (unverified whether one does). Line 44 of `card_status_cli_test.rs` (every card Complete or RulesUnverified) is what catches a forgotten Trainer arm in `move_generation_trainer.rs` (skeptic: only that one; `card_validation.rs` lines 70-74 report `MissingTrainer` from move generation alone, so an id forgotten in `apply_trainer_action.rs` reports Complete and panics at play, line 329, and only a test that plays the card pins it. Scale, from the A4b precedent: about 14 Supporter/Item names and 30 printings, and the fork's A4b arms shipped with no per-printing play test; so write the same-as-base check as one table-driven test over every B4b Supporter/Item id, in the shape of `engine/tests/attack_id_migration_test.rs`, and a separate Game-level test only where an id-keyed helper beyond the two match arms exists; `04_skeptic.md` F3, F4). |
| 4 | **Engine inventory pins and the suite.** `cargo fmt`; `cargo clippy --all-targets --all-features -- -D warnings` (`SKILL.md` line 198); the full suite (section 3 step 1). `engine/src/players/public_pricing_player.rs` lines 310-335 must pass unchanged: for a reprint-only set the 62 audited texts are still exactly the database's opponent-hand/deck texts (section 5). | `engine/tests/card_status_cli_test.rs`, no other test edits expected | cloud | Suite green; the count recorded in the PR beside the last main-line counts on record (1,826 at rules4, `rl/addon-0.7.2/rules4-repair-README.md` line 18; main's count at `7fc6ccb` unverified, no build allowed tonight). |
| 5 | **Record and hand over.** `engine/UPSTREAM.md`: the B4b import, the upstream sha it came from, the CRLF decision. Open a PR to main; Dustin merges (he merged PR #1 on Sept 25 the same way). | `engine/UPSTREAM.md` | cloud; Dustin merges | The PR text lists: the incremental-map outputs (empty), the id-grep hits and what was done with each, the test count, the files touched (must be a subset of section 6 of `03_fork.md`). |
| 6 | **Second read (tier 1).** Read the diff, not the description: generated files equal upstream's after CRLF normalisation; every B4b arm uses its base printing's helper; no file outside the listed set; both incremental-map outputs empty; no rules or mechanic-map change; the tests exist and test through `Game`; (skeptic) no new consumer of `get_highest_evolutions` or `evolution_targets` in `players/value_functions.rs` that counts, sums or averages over forms, since that is the invariant that keeps a data append game-neutral (`04_skeptic.md` F5); the per-number Limitless check of step 0 is in the PR. | none | laptop | A dated read note in this folder (`04_second_read_<date>.md`) saying pass or listing what to fix; the WSL build waits for it. |
| 7 | **Release build.** From `git archive` of the merge commit, in WSL, as on Sept 25 (`rl/engine-2026-09-25/README.md` lines 21-24): `cargo build --release`, `cargo build --release --example legality_scan`, `cargo build --release --example goldfish`; sha256 of all three. Only after the laptop's queue reports done (REVIEW line 134: one thing at a time on the laptop). | new `rl/engine-<date>/` | WSL | The three hashes in `identity.txt` line 1 style (`rl/results/engine_identity_2026-09-25/identity.txt`); the tree's `engine/src`, `engine/examples`, `Cargo.lock` checked identical to the commit. |
| 8 | **Acceptance checks** (section 3, in that order). | `rl/results/engine_identity_<date>/` | WSL runs, laptop reads | `RESULT: IDENTICAL`, 14,000 of 14,000, for k3 and for kp3; the parity check; the card pass; the coverage flags. |
| 9 | **`lib/` refresh** (only after step 8 passes). `tr -d '\r' < engine/database.json > lib/deckgym-database.json` and `cmp` after stripping (`03_fork.md` bottom line 6); `lib/card_canon.py` line 54 `EXPECTED_IDS` to the new total and `'B4b'` inserted before `'P-A'` in `SET_ORDER` lines 56-57 (the base-id choice depends on that order, line 228); `python lib/card_canon.py build lib/deckgym-database.json` (writes `results/CANON_MAP.tsv` by default, line 229; move it to `lib/CANON_MAP.tsv`); `lib/deck_classifier.py` line 173 add `"B4b"`. The s216 catalog (`lib/s216_card_catalog_v1.json`, `project_manifest.json` lines 342-345) is a Pocket Deck Lab job, open question 8. | the files named | laptop (Python only; no engine) | `python lib/card_canon.py selftest`, `python lib/deck_check.py selftest`, `python lib/card.py "B4b 001"` prints the card. The CANON_MAP header re-pins `source_sha256` and `ids`. (skeptic: also diff old and new `CANON_MAP.tsv` on the 3,879 existing ids, base_id column, expect 0 changes; and record that `lib/s216_card_catalog_v1.json`'s `sources` block still names the old `card_canon.py` and CANON_MAP shas, which this step makes stale even though the catalog is untouched; nothing in the repo verifies them; `04_skeptic.md` F9.) |
| 10 | **Manifest switch** (section 3, last item), then the docs: `START_HERE.md` lines 19-27 (engine line) and 73-74; `rules/06_sources.md` line 13 ("3,879 cards, A1-B4a"); the A5 line of `rl/RUN5.md` (357-359) corrected from "about five new cards" to reprint-only plus the Garchomp promo, with Dustin's OK since RUN5 is a shared instruction file (open question 7). | `project_manifest.json`, `START_HERE.md`, `rules/06_sources.md`, `rl/RUN5.md` | WSL writes the release folder and manifest; laptop second-reads the hashes; Dustin's word to switch | `current_engine.py` (resolves by hash, `03_fork.md` section 5) and `decks/screen/floor.py` lines 8-10 accept the new release; the old one is listed under `historical_releases` with its hashes unchanged. |
| 11 | **Mega Garchomp ex (October, when Promo-B Vol. 13 is on Limitless).** One entry in `engine/database.json` and the LF copy (Stage 2 Dragon Mega ex, HP 220, Falling Edge, "Discard 2 random Energy from this Pokémon."; damage, cost, weakness, retreat from the Limitless page, never guessed, `01_set.md` line 163; skeptic: the damage is a live conflict, 180 on GameWith 578652's card box read verbatim on Sept 26 against 190 on the spoiler image, so it is entered from neither; `04_skeptic.md` F7); regenerate; `-- --incremental-attack-map` prints nothing because the text is mapped at `engine/src/actions/effect_mechanic_map.rs` line 178 (Giratina A2a 061, Rayquaza B4 119). Same acceptance as B4b, same rule that it is its own commit; bundle it into the B4b refresh only if its text is published before step 5 (open question 6). Whether a Stage 2 Mega ex needs anything special (3 points on knockout, evolution from Garchomp) is unverified; the test settles it. | as steps 1-10 | cloud builds, laptop reads, WSL runs | One Game-level card-effect test: Falling Edge does its Limitless-printed damage (skeptic: 180 or 190, unverified) and leaves the attacker with exactly 2 fewer Energy chosen at random; knocking it out is worth 3 points. Card pass against its Limitless page (section 3 step 5). |

## 3. Acceptance checks, in order

Every check is run by the WSL session on the release build from step 7 and read by the laptop session; a fail at any step stops
the sequence and goes back to the cloud with the mismatch named. Pass status of all of them: **unverified (no build allowed
tonight)**; `03_fork.md` section 7 gives the reasoning for why 3 should pass. (skeptic: that reasoning misses one path.
`engine/src/card_logic/rare_candy.rs` lines 17-29 and 38-49 push one name per printing, so `get_highest_evolutions` returns each
reachable Stage 2 card once per Stage-1 printing of that name in the database; a B4b Combusken or Grovyle reprint lengthens the
Vec for `decks/research/blaziken.txt` and `sceptile.txt`. It stays game-neutral because every consumer in
`players/value_functions.rs` takes a max (line 1612), a first (1692), an any (1766) or a first-minimum `min_by_key` (835), and
because B4b entries sit after every A/B entry in `CardId::iter()` with a B-series base before them. That invariant is what the
second read checks, and the replay remains the proof. `04_skeptic.md` F5.)

1. **The full Rust suite.** `cargo test --release --features test-utils` (root `CLAUDE.md`, build/test line) or
   `cargo test --features "tui test-utils"` (`engine/README.md` line 118; the pre-commit hook `engine/.githooks/pre-commit`
   line 20). Pass = zero failures, zero ignored that were not ignored before; record the count. Run it in the cloud at the PR
   (step 4) and again on the WSL release tree, not beside a training run.
2. **The 44 accepted-review replay segments** (441 outcome assertions, 70 scripted actions, plus the replay tool's 48 tests):
   `rules/README.md` lines 9 and 11; `rl/addon-0.7.2/rules4-repair-README.md` lines 18-20. They live in Pocket Deck Lab's
   `Boss Folder/rules4-t2-repair-2026-09-22/replay-evidence/validated-corpus/`, not in this repo (`03_fork.md` section 7); the
   WSL session runs them there against the new binary. Pass = 44 of 44. Whether that harness still runs against the current
   engine is unverified; the Sept 25 switch README does not list them (`rl/engine-2026-09-25/README.md`), so if they cannot run,
   write "not run, harness status" in the release README and let Dustin decide whether the switch waits (open question 5).
3. **The identity replay of k3 and kp3** on the table's 28 x 500 deals against `rl/results/engine_identity_2026-09-25/`:
   `legality_scan --decks decks/research --games 500 --bot k3 --games-out k3_500.jsonl` (seeds 72,000,000 + pairing x 10,000 + i,
   even i = first-named deck in seat 0; `rl/results/per_game_table_2026-09-25/README.md` line 3,
   `rl/results/deep_search_table/deep_table.py` lines 17-23), then
   `python compare.py k3_500.jsonl ../per_game_table_2026-09-25/k3_500.jsonl`; the same with `--bot kp3` against
   `../public_pricing_2026-09-25/kp3_500_worst5.jsonl` and `kp3_500_rest.jsonl`. Pass = `RESULT: IDENTICAL`, 14,000 of 14,000
   for each pilot, on all of `a, b, seed, first_seat, moves, winner_seat, points, turns, first_deck_score` (`compare.py` line 14;
   Sept 25's readout: `identity.txt` lines 3-13). **A B4b refresh must not change any B4a game**; a single `MISMATCH` line is a
   fail, and the pairing and deal it names go back to the cloud. Reference files exist (listed this pass). **Same-rules caveat:**
   if a rules repair lands on main before the B4b build (the promotion-timing repair, REVIEW line 132, is expected to move table
   games; the laptop already plans to regenerate k3's and kp3's reference tables at the rules/09 commit, REVIEW line 134), the
   references are regenerated at that rules commit first and the B4b replay is compared against those, so the two changes are
   never confounded. One change, one replay.
4. **The CLI parity check on seed 7100.** `deckgym simulate` k3,k3 with `--seed-stream` on the screen's seed 7100, four matchups
   of 30 games (brew-07 against Altaria, Blaziken, Hydreigon, Lucario): the new `deckgym` and `rl/engine-2026-09-25/deckgym`
   print identical win and draw counts (`rl/engine-2026-09-25/README.md` line 29); plus the kp3 smoke test (line 30).
5. **Card-effect pass on every new card against its Limitless page.** For B4b, where every card is a reprint: the step-0 script
   over the whole set (0 texts differ from the base printing) is the pass (skeptic: not on its own; it passes a wrong
   number-to-card assignment, a short count and a foil built from the wrong printing. Add the scripted per-number name and
   rarity check against the Limitless B4b set page with the count equal, and for the 23 ambiguous or new-art cards, the 10 in
   `01_set.md` table A and the 13 in table B, a per-card text check against the Limitless card page; `04_skeptic.md` F1), plus for each B4b card whose base printing has a
   coverage or RulesUnverified entry, the check that the entry now names the B4b id too (`card_validation.rs` 89-113). The laptop
   does this with `python lib/card.py "<B4b id>"` beside the Limitless card page, never from memory (`START_HERE.md` line 56).
   For Mega Garchomp ex: HP, type, stage, evolves-from, Energy cost, damage, effect text, weakness and retreat cost checked field
   by field against https://pocket.limitlesstcg.com/cards/P-B (the promo list; its number is unverified), and the Game-level
   test of step 11.
6. **The coverage tool's flags for the new cards.** `goldfish --coverage` (`engine/examples/goldfish.rs` lines 14-17 and 163-215;
   pinned by hash in the manifest, `project_manifest.json` lines 315-317) on a list carrying each new id. It writes, per card:
   the implementation status and `limitations`, `unpriced_text_rule` (the opponent-hand/deck texts kp has not audited),
   `estimator_printed_damage`, `pays_off_on_opponent_turn`. These are the cards the bot cannot price; the floor check marks a
   list carrying one "untrusted"-prone (`decks/screen/floor.py` lines 28-36). Expected: a B4b reprint carries exactly its base
   printing's flags (same text; printings of one card are counted together, `floor.py` line 36), and Mega Garchomp ex has no
   `unpriced_text_rule` flag (its text does not mention the opponent). Record whatever it prints in the release README.
7. **The manifest switch, as done on Sept 25.** A new dated folder `rl/engine-<date>/` with `deckgym`, `legality_scan`, `goldfish`
   and a README in the shape of `rl/engine-2026-09-25/README.md` (what changed, why, the three sha256s, source commit, build line,
   the identity evidence from steps 3-4, what is unchanged); `project_manifest.json` `available_release` (lines 309-324) rewritten
   for the new build with `source_commit`, `identity_evidence` and `approved` (Dustin's word and time); the previous entry
   `main-7fc6ccb` moved to `historical_releases` with its hashes unchanged, as `rules4` was (lines 295-307);
   `latest_source_commit` (line 334) updated. The 0.7.2 wheel and every run identity bound to it stay untouched. Dustin approves
   the switch, conditional on 3 and 4, as on Sept 25 (`project_manifest.json` line 322).

## 4. No A/B straddles the switch

Rule: **every table, screen, mixed-row, floor and calibration result names the engine it ran on by hash**, the `deckgym` and
`legality_scan` sha256 plus the source commit, in its folder's `identity.txt` or README, the way
`rl/results/engine_identity_2026-09-25/identity.txt` line 1 and the B2e spec do (`rl/results/b2e_card_check_2026-09-26/README.md`
lines 246-252: the scan binary's sha256 goes in the run folder's `identity.txt`, and `deckgym`'s hash stays the reference).
A paired comparison (a candidate pilot against its baseline, a fix against its reference table, both arms of a Dustin-deck A/B)
has both arms on one hash. If the switch would fall in the middle of a run, the run finishes on the old hash (the old binary
stays in `historical_releases` for exactly this) or restarts on the new one; arms are never mixed, and a reading that mixes them
is void. The switch is scheduled in a gap: before B2e's 96 pairings start or after they finish, never during; the same for the
kpr mixed rows, the kt A/B and the Altaria detector readout. Why the rule holds even for a refresh designed to change zero
games: "designed to" is shown only on the eight research decks by step 3, and only after the fact; a screen or A/B on other
lists gets no such proof, so it names its hash and stays on one side.

## 5. The 62 audited texts and the coverage flags when new texts arrive

How it works today: under kp, an effect whose text mentions the opponent's hand or deck is priced only if that text is in
`AUDITED_TEXTS` (`engine/src/players/public_pricing_player.rs` lines 32-95, 62 lowercased texts, sorted; `is_audited` line 98;
the rule at `engine/src/observation.rs` lines 478-485). **A text added later stays unpriced under kp, exactly as under k, until
it is audited and added** (module doc, lines 12-15), and the test `the_audited_list_is_the_card_databases_whole_inventory`
(lines 310-335) fails the moment the database holds such a text that is not on the list, naming it. Coverage (section 3 step 6)
flags the card as `unpriced_text_rule` until then, and the floor treats lists carrying it as untrusted-prone.

- **B4b:** no new text, so the list is unchanged, the test passes unchanged, and reprints of Copycat, Elesa, Chingling and the
  rest are priced or flagged exactly as their base printings (same text). Nothing to audit.
- **Mega Garchomp ex:** its text does not mention the opponent's hand or deck, so the rule does not apply; no audit. Its coverage
  entry is whatever `goldfish --coverage` prints (step 6).
- **The audit step, for the next set that does bring such a text (C1, or a promo):** (a) the test names the text; (b) the cloud
  reads the effect's implementation and its pricing under public evaluation for a leak (does resolving it against the opponent's
  Unknown cards read anything hidden?) and for a panic on Unknown cards, the tier-1 read that was done for 858b6fe ("no leak, no
  panic", module doc line 13-14); (c) the lowercased text goes into `AUDITED_TEXTS` in sorted position and the array length is
  bumped; (d) the test passes; (e) because this changes kp's play wherever the card appears, it is a pilot change, not data: its
  own commit, an identity replay of kp3 read for changed games (any table deck carrying the card moves), Dustin's word if table
  games move, never bundled with a data refresh; (f) until (e) is done the card stays flagged and unpriced. Owners: cloud
  implements, laptop second-reads the tier-1 read, Dustin decides adoption.

## 6. Later and separate: the upstream code-merge trial (cloud, before C1)

**Facts.** The fork has never merged upstream code since `abf1be1` (2026-07-30, "Merge upstream deckgym (B4 set ...)", merge
base `8b40f55`, `engine/UPSTREAM.md` line 3; `03_fork.md` section 1). Upstream `main` is 104 commits ahead of that base and 0
behind (https://api.github.com/repos/bcollazo/deckgym-core/compare/8b40f55d889b89634467cca7da153114789ffdf4...main); its head on
Sept 26 was `f01e695` (2026-09-17, PR #368), 8 commits past the sha `UPSTREAM.md` calls "fetched main" (`02_upstream.md` section
1). This repo has no `upstream` remote and does not hold `fda4839` or `79ba7eb` (`02_upstream.md` section 5), so the trial starts
by adding the remote in the cloud. The fork's mechanic maps carry about 1,000 fork-only lines against upstream's
(`effect_mechanic_map.rs` 3,699 vs 2,880; `effect_ability_mechanic_map.rs` 1,012 vs 639; `02_upstream.md` section 5).

**Conflict areas, from `engine/UPSTREAM.md` lines 7-12:** `src/game.rs` (fork decision randomness, forecasts, state adoption,
terminal and turn handling); `src/players/` (fork observations, public reply checking, K search and evaluation, player factory);
`src/observation.rs` (the hidden-information boundary and public effect forecasting, including Boiler Smog); the two mechanic
maps (merge new upstream entries, never replace either map); and, for status-related changes, `src/hooks/{mod,retreat}.rs`,
`src/move_generation/attacks.rs`, `src/actions/{apply_action,apply_action_helpers}.rs` and their regression tests. Open upstream
PR #379 (Special Condition and win-condition rules, 35 tests) lands in exactly those areas if it merges (`02_upstream.md` section
3). Line 14's instruction stands: import upstream card commits with their tests and reconcile; it is not approval to discard fork
behaviour or reimplement cards upstream already has.

**Procedure (cloud, on a branch, never on main).** Add `upstream`; `git fetch upstream`; `git diff --ignore-space-at-eol --stat
upstream/main HEAD -- src tests` and the per-file diffs (`UPSTREAM.md` line 14); decide the CRLF policy before merging (the
"preserved CRLF churn", line 7); merge `upstream/main`; resolve the conflict areas keeping fork behaviour; build; the full suite;
then the identity replay of section 3 step 3 for k3 and kp3 against references generated at the same rules commit, reading every
changed game and attributing it to a named upstream change. Write the result to a dated folder under `rl/results/`. Merging the
branch to main, and any engine switch after it, obey sections 3 and 4 in full.

**Window.** After the B4b switch is done and before C1 (October 28): the trial must not straddle an A/B (section 4), so it sits
in a gap of the readings calendar, proposed as the week of October 12 to 19, after the B2e and kt readings (open question 9).
Budget: 2 to 4 cloud agent-days (estimate).

**Abort rule (stated before the trial starts).** The trial is abandoned, the branch left unmerged and a note written, if any of:
(a) the merged tree does not build green (suite) within the budget; (b) the identity replay shows changed games that cannot be
attributed to a named upstream rules change the project accepts on rules evidence (`rules/`, `RULES_FOR_AGENTS.md`); (c) the
resolution would replace either mechanic map, or any fork file under `src/players/` or `src/observation.rs`, rather than merge
into it; (d) Dustin says stop. On abort the note lists the upstream commits worth cherry-picking one at a time (card
implementations with their tests, the shape of the B4a PRs #360/#361), and the fork keeps its current method, importing data and
implementing cards itself, as it did for B4a (`03_fork.md` section 4). On success the note states the merged-tree replay result
and the per-set cost, and Dustin decides whether the fork stays merged from C1 on. Publishing the prepared Sleep/Paralysis PR
upstream is Dustin's call, separately (REVIEW line 162; `UPSTREAM.md` line 5).

## 7. Open questions for Dustin

1. **Line endings.** The three data files carry CRLF, `lib/deckgym-database.json` is LF, and `.gitattributes` never converts
   (`03_fork.md` section 1). Keep CRLF in `engine/` for this refresh (least diff noise against the Sept 25 build) or go LF
   repo-wide now? Either is fine for the replay; it must just be decided and written in `UPSTREAM.md`.
2. **Version string.** Does a data-only refresh change `engine/Cargo.toml` line 3 (`0.1.0-pdl.rules4`) or stay? Releases are
   named by commit and hash anyway (`rl/engine-2026-09-25/README.md` line 24 kept the string unchanged).
3. **Order against the rules repair.** The promotion-timing repair (REVIEW line 132) moves table games; B4b moves none. Proposal:
   whichever is ready first lands first, each as its own commit with its own replay, and the references are regenerated at the
   rules commit before the other is replayed (section 3 step 3). OK?
4. **Wait for upstream or build from Limitless?** Proposal: wait up to three days for upstream's "b4b" commit (the copy is then
   trivial because the fork's data files are upstream's); build from the Limitless list only if upstream is late.
5. **The 44 replay segments** are in Pocket Deck Lab, not this repo, and the Sept 25 switch README does not list them. Are they
   a condition of this switch, and should the corpus be copied into the repo?
6. **Mega Garchomp ex:** bundle it into the B4b refresh if its promo text is on Limitless before the PR is merged, or keep it as
   its own small refresh in October?
7. **Correcting RUN5's A5 line** (357-359) and REVIEW line 162 from "about five new cards" to "reprint-only; the one new card is
   the Mega Garchomp ex promo" needs your OK, since RUN5 is a shared instruction file.
8. **The QR card catalog** (`lib/s216_card_catalog_v1.json`, 3,879 printings): its builder and third-party inputs are not in this
   repo (`03_fork.md` section 5). Do you want it refreshed for B4b at all? B4b reprints likely decode already if the app keeps the
   same entity numbers (unverified until a B4b card is scanned); Mega Garchomp ex would need a new entity.
9. **The merge trial's window and budget:** week of October 12 to 19 and 2 cloud days, or another slot? And does the
   Sleep/Paralysis PR go out before it?

## Unverified (collected)

- Everything that needs a build: main's test count at `7fc6ccb`, that the suite is green there, that the identity replay passes
  after a data-only append, the coverage flags of any new card (no build allowed tonight).
- The B4b card count (A4b precedent 379), the set numbers, the exact reprint membership, which printing carries each parallel
  foil, the set code "B4b" itself (`01_set.md` "Unverified items"; `02_upstream.md` section 8).
- Mega Garchomp ex's Energy cost, weakness, retreat cost and Promo-B number; 190 damage is from the spoiler image against
  GameWith's 180 (`01_set.md` line 163); whether a Stage 2 Mega ex needs engine work.
- Where upstream will place the B4b entries (before P-A is the assumption) and when its commit lands.
- Whether the 44-segment harness runs on the current engine; whether the s216 catalog builder still exists in Pocket Deck Lab;
  whether the Pocket app gives B4b reprints the same QR entity numbers.
- The agent-day figures in section 1 and the merge-trial budget in section 6 are estimates from the size of the equivalent
  upstream commits and PRs, not measurements.
- (skeptic, verified Sept 26) The "14,000-game" size of each reference replay: `k3_500.jsonl` has 14,000 lines,
  `kp3_500_worst5.jsonl` + `kp3_500_rest.jsonl` 2,500 + 11,500. Also verified this pass: HEAD `4924008` with `engine/` identical
  to `7fc6ccb`; upstream head `f01e695`, no data commit after "b4a", 104 ahead / 0 behind the merge base; Limitless B4b still
  404; the official date and "every ♦♦♦♦" wording; the 13 mirror-card names verbatim on GameWith; the A4b "0 of 379" precedent
  (re-run); the replay cost at cloud speed. `04_skeptic.md` F10.
- (skeptic) Still unverified: that the fork's data files equal upstream's after CRLF (not re-done), Mega Garchomp ex's damage
  (180 vs 190) and whether it is outside the set list, the laptop-to-cloud speed ratio, C1 on Oct 28 (pokemon-zone returned
  403). `04_skeptic.md` F11.

## Paste-ready block for the cloud session (via Dustin)

> B4b refresh, plan item A5. Procedure: `rl/results/b4b_prep_2026-09-26/README.md` (sections 2 and 3; read `04_skeptic.md` too). The set is expected reprint-only, and step 0's script proves it
> (`01_set.md`); upstream has no B4b data yet (`02_upstream.md`). When upstream's "b4b" commit or the Limitless B4b list exists:
> on a branch, data files + regenerate (step 1), both `--incremental-*-map` commands must print nothing (step 2; skeptic: no new text, not no new card), id arms for every
> B4b Supporter/Item using the base printing's helper, plus Victini/Haxorus/Dragalge ex id lists (step 3), one Game-level test per
> arm and a same-as-base test, `card_status_cli_test.rs` count, suite green (step 4), `UPSTREAM.md`, PR (step 5). No rules fix in
> the same commit. Mega Garchomp ex only if its Limitless promo page exists (step 11). The laptop second-reads; the WSL session
> builds the release and runs the identity replay; nothing runs on the laptop beside training.
