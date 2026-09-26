# 04 - Skeptic's pass on the B4b refresh procedure (2026-09-26)

Scope: try to refute `README.md` (and the three notes it rests on) on five heads: a step that would change a B4a game, a
file the refresh touches that the procedure omits, an acceptance check that could pass while the set is wrong, a claim
about B4b or upstream that is unverified, an estimate off by more than 2x. Method: files and read-only git only (the
GitHub Desktop git at `C:\Users\dacz8\AppData\Local\GitHubDesktop\app-3.6.6\resources\app\git\cmd\git.exe`, `rev-parse`,
`log -1`, `diff --stat`, `status`), PowerShell JSON parses of `lib/deckgym-database.json`, line counts of the reference
jsonl files, and WebFetch of the pages named below. **No `cargo`, no engine binary, no game, no background process.**
The engine was not modified. Paths are relative to `C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\`. Every
change marked "applied" was written into `README.md` with a "(skeptic: ...)" tag; the rest are recommendations.

## Verdict in one paragraph

The procedure holds on its main claim: no step in it moves a B4a table game, and the identity replay is the right
proof. But (1) its acceptance for the *set itself* is weaker than it reads: every check in sections 2 and 3 passes with
a B4b whose numbers are assigned to the wrong cards, whose count is short, or whose foil reprints point at the wrong
printing, because the step-0 script only asks "does this entry equal *some* existing printing"; (2) step 2's "both
commands print nothing" cannot detect a genuinely new card whose text already exists, and Mega Garchomp ex is exactly
such a card; (3) the Trainer-arm job is about seven times larger than "at least Copycat and Elesa" by the fork's own
A4b precedent, which with the README's one-test-plus-one-test-per-arm rule puts the "half a cloud day" estimate off by
2x or more unless the tests are table-driven; (4) a pure data append does reach k3's evaluation through a path
`03_fork.md` did not look at (name-duplicate evolution lookups), and is harmless today only because every consumer
takes a max, a first or an any, which is an invariant to state and second-read, not a structural guarantee; (5) the
evidence for "B4a excluded" and for Mega Garchomp ex's damage is thinner than the notes say. Several "unverified" items
are now verified and the README is updated accordingly.

## Findings

### F1. The set-level acceptance passes while the set is wrong (acceptance; applied)

**Claim under test.** README section 3 step 5: for B4b "the step-0 script over the whole set (0 texts differ from the
base printing) is the pass"; section 2 step 0: "all fields except id, rarity, booster_pack must equal some existing
printing"; step 1: `card_status_cli_test.rs` line 23 "updated from 3879 to the new total".

**Refutation.** The identity replay (section 3 step 3) says nothing about any B4b entry: the eight decks carry no B4b
id (`03_fork.md` bottom line 8, re-read: `decks/research/*.txt` list only A/B/P-A ids). The step-0 script compares each
B4b entry to the *set of all existing entries*; it passes when
- B4b 0NN is assigned the wrong card (the entry equals some existing printing, just not the one that carries that
  number in the game),
- a card is missing (the count is whatever the cloud writes into `engine/tests/card_status_cli_test.rs` line 23; nothing
  pins it to an outside source),
- a foil reprint is built from the wrong printing where the name has several B-series texts (Charmeleon B1a 012 vs
  B2b 008, Dragonair B2b 052 vs B4 117, Raichu B2b 023 / B3b 022 / B4 050, Bombirdier B2a 071 vs B3 115, Aegislash
  B1 172 vs B2 120; `01_set.md` table B marks all five "unverified"). Each wrong choice equals an existing printing, so
  the script prints 0 novel texts.
The A4b precedent I re-ran (379 A4b entries, 0 with no identical non-A4b printing on all fields but id, rarity,
booster_pack; PowerShell over `lib/deckgym-database.json`) confirms what the script *can* see, not what it cannot.

**What to change (applied to README steps 0 and 3.5).** Add a per-number check of every B4b id against the Limitless
B4b set page (number, name, rarity; the A4b page at https://pocket.limitlesstcg.com/cards/A4b lists all 379 that way, so
it is scriptable): names equal per number, count equal, and the Limitless count written into the PR beside the
`card_status_cli_test.rs` number. For the 23 cards whose printing choice is ambiguous or new-art (the 10 new-art cards
and the 13 foils in `01_set.md` tables A and B), a per-card text check against the Limitless card page with
`python lib/card.py "<B4b id>"`, because the step-0 script cannot tell printings of one name apart.

### F2. Step 2 proves "no new text", not "no new card" (acceptance; applied)

**Claim under test.** Step 2: "Both commands print nothing. Any printed line = a genuinely new text"; the paste-ready
block: "The set is reprint-only".

**Refutation.** `card_enum_generator -- --incremental-attack-map` prints effect texts absent from the map (generator
lines 320-349, `03_fork.md` section 2 step 4). A new card whose text is already mapped prints nothing. Mega Garchomp ex
is that case: its text `"Discard 2 random Energy from this Pokémon."` is at `engine/src/actions/effect_mechanic_map.rs`
line 178 (`02_upstream.md` section 4). And GameWith's B4b pack page lists メガガブリアスex among its eleven 新カード
(verbatim fetch of https://gamewith.jp/pokemon-tcg-pocket/578648 on 2026-09-26: モノマネむすめ, カミツレ,
メガリザードンXex, メガルカリオex, メガサーナイトex, メガチルタリスex, メガフシギバナex, メロエッタ, イーブイ,
パピモッチ, メガガブリアスex), so the set page itself does not separate it from the pack. If a card like it were in the
set, step 2 passes, step 4's audited-texts test passes (its text does not mention the opponent), and only step 0's
whole-entry comparison catches it (no existing printing named "Mega Garchomp ex").

**What to change (applied).** Step 2's pin now says it proves no new *text*; the reprint-only premise is proven by step
0's script (0 entries without an identical existing printing), whose output is a required PR artefact. The paste-ready
block says "expected reprint-only; step 0 proves it".

### F3. The Trainer-arm count is about seven times "Copycat and Elesa", and the test rule makes the estimate off by 2x (estimate; applied)

**Claim under test.** Section 1: "add the new card numbers to the handful of places that list Trainer cards by number
... (at least Copycat and Elesa)"; "roughly half a cloud day for the data files, the Trainer arms and their tests ...
the Trainer-arm change is two source files plus a test per card". Step 3: "One Game-level test per new Trainer arm ...
plus one 'same as base' test per arm".

**Evidence.** The fork's own A4b (the A-series Deluxe Pack, the precedent `01_set.md` uses for the count): 50 Trainer
entries, of which 40 Supporter/Item printings over 19 distinct names (Eevee Bag, Elemental Switch, Rare Candy, Pokémon
Communication, Cyrus, Erika, Irida, Lyra, Giovanni, Silver, Sabrina, Iono, Dawn, Mars, Leaf, Lillie, Lusamine, Red,
Professor's Research), 8 Tools, 2 Fossils; out of 60 Supporter/Item names in A1-A4a (32%). The B1-B4 pool has 81
Supporter/Item printings over 44 names. At the A4b ratio B4b brings about **14 Supporter/Item names, about 30
printings**, each needing arms in `apply_trainer_action.rs` and `move_generation_trainer.rs`. The fork's A4b arms are
there (e.g. `apply_trainer_action.rs` lines 103-240: Erika, Irida, Lillie, Giovanni, Red, Sabrina, Leaf, Cyrus, Mars,
Rare Candy, Pokémon Communication, Dawn, Elemental Switch, Lusamine, Lyra, Silver, Eevee Bag, Iono, Professor's
Research), and **no per-printing Game-level test came with them**: `A4b` appears in `engine/tests/` only in the two
migration tables and a few fixtures (47 hits in 10 files, none a Trainer play test). So the README's per-arm test rule
is new and unbudgeted: 14 arms x 2 tests = 28 tests, 30 printings x 2 = 60 if per printing. Half a cloud day for data,
arms and 28-60 Game-level tests is off by 2x or more.

**What to change (applied).** Keep the rule's substance but make it table-driven: one test function over every B4b
Supporter/Item id that plays the B4b id and its base id from identical states and asserts identical states (the
printed-id table shape of `engine/tests/attack_id_migration_test.rs` lines 6-60 and 150-190), plus one Game-level test
only where an id-keyed helper beyond the two match arms exists (`trainer_coin_plan.rs` 46-101,
`team_rockets_researcher.rs` 129, `state/mod.rs` 365). Budget one cloud day for arms and tests, not half.

### F4. `card_status_cli_test.rs` line 44 catches a missing move-generation arm only (acceptance; applied)

**Claim under test.** Step 3: "Line 44 of `card_status_cli_test.rs` (every card Complete or RulesUnverified) is what
catches a forgotten Trainer arm."

**Evidence.** `engine/src/card_validation.rs` lines 70-74: `MissingTrainer` is reported only when
`trainer_move_generation_implementation(&State::default(), &trainer_card)` returns `None`. An id added to
`move_generation_trainer.rs` but forgotten in `apply_trainer_action.rs` reports `Complete`, is offered in games, and
panics at play (`_ => panic!("Unsupported Trainer Card")`, `apply_trainer_action.rs` line 329; confirmed by grep).

**What to change (applied).** Step 3's pin says which arm line 44 covers; the apply arm is pinned only by a test that
plays the card (the same-as-base test of F3 does).

### F5. A pure data append does reach k3's evaluation; it is neutral today because every consumer takes max/first/any (step that could change a B4a game; applied as reasoning and a second-read item)

**Claim under test.** `03_fork.md` bottom line 8 and README section 3 step 3: nothing orders or hashes by `CardId`
position, so a data-only append cannot move a game; step 3: the different-helper arm "is the one code change that could
move an identity-replay game".

**Evidence.** `engine/src/card_logic/rare_candy.rs` builds `STAGE1_LOOKUP` and `STAGE2_LOOKUP` by pushing one *name per
printing* (lines 17-29 and 38-49: `lookup.entry(evolves_from).or_default().push(name)` over `CardId::iter()`).
`get_highest_evolutions` (lines 121-186) then, for a Basic, loops `for stage1_name in stage1_names` and inside it over
every available card, so each matching Stage 2 card in deck + hand is returned once **per Stage-1 printing of that name
in the whole database**. A B4b Combusken or Grovyle reprint lengthens the Vec for a Torchic or Treecko deck. Two table
decks are on that path: `decks/research/blaziken.txt` (B1 033 Torchic, B1 036 Mega Blaziken ex, A3 144 Rare Candy) and
`decks/research/sceptile.txt` (a Stage 2 line). A4b, the precedent, reprinted 100 Stage 1 and 39 Stage 2 Pokémon
(PowerShell census), so B4b will hit this. The consumers, all in `engine/src/players/value_functions.rs`:
`evolution_potential` folds with `f64::max` (line 1612); `pokemon_online_score` takes `highest_evolutions[0]` (1692);
`best_benched_attacker_online_score` uses `.any` (1766); the threat scan collects candidates per form and takes
`min_by_key` (835), which returns the first minimum, so a later duplicate never displaces the pick, and `[form]` at 854
resolves to the same card either way. Order is also safe: B4b entries sit after every A/B entry and before P-A/P-B in
`CardId::iter()`, and every B4b card has a B-series base printing, so the first entry of every name list is unchanged.
No deterministic hasher is in game code (`indexmap` is used only by the generator, `engine/Cargo.toml` line 18 and
`src/bin/card_enum_generator.rs`; std `HashMap` order is per-process random, so nothing reproducible depends on it).

**So the claim survives, but for a reason the notes do not state.** The invariant that keeps a data refresh
game-neutral is "no consumer of `get_highest_evolutions` counts, sums or averages over forms". Any future value-function
change that does (the promotion-timing repair, kt, B3's features) would turn the next data refresh into a pilot change.

**What to change (applied).** Section 3 step 3's reasoning names the path; step 6 (second read) checks that no new
consumer of `get_highest_evolutions` / `evolution_targets` counts or sums; step 3 of section 2 no longer calls the
helper mismatch "the one" thing that could move a game.

### F6. The "B4a excluded" sentence on GameWith is a stale template about last year's pack (unverified claim; applied)

**Claim under test.** `01_set.md` bottom line: "B4a Team Rocket's Ambition is excluded (GameWith: 「ロケット団の野望」
カードは排出なし)"; README section 1 relies on it for the ex pool and the Trainer list.

**Evidence.** Verbatim fetch of https://gamewith.jp/pokemon-tcg-pocket/578648 (2026-09-26):
「ハイクラスパックexは『ロケット団の野望』のカードは排出されません。」 The subject is ハイクラスパックex, which is A4b's
Japanese name, on a page titled 【ポケポケ】ハイクラスパックMEGAの収録カード一覧. The sentence was carried over from
last year's article. The exclusion is still supported by the official page's range ("from Mega Rising to Ruler of the
Skies", i.e. B1-B4; verbatim at https://www.pokemon.com/us/news/pokemon-tcg-pocket-deluxe-pack-mega-coming-soon), but
that is the evidence, not GameWith. If B4a cards do appear, the six Team Rocket ◊◊◊◊ ex and the B4a Trainers with
id-keyed helpers (Researcher, Arcade in `trainer_coin_plan.rs`) join the arm list; the step-3 grep already covers that.

### F7. Mega Garchomp ex: damage is 180 on GameWith's card box, 190 only on a spoiler image I could not reach (unverified claim; applied)

**Evidence.** Verbatim fetch of https://gamewith.jp/pokemon-tcg-pocket/578652 (2026-09-26): 2進化, ドラゴン,
メガシンカex, HP 220, ワザ Falling Edge, コスト 3エネ, ダメージ **180**, テキスト
「このポケモンからエネルギーをランダムに2個トラッシュ。」, 弱点 and にげる absent, 「PROMO-B 第13弾で入手」. The
sentence `01_set.md` line 34 quotes from the same page (収録カードではなく…完全新規カード) was not returned by the
verbatim fetch (summariser variance; see F8). pokemon-zone (the 190 source, the spoiler image) returned HTTP 403 to me.
The official page says only "B Series vol. 13 promo packs during the Mega Garchomp ex Drop Event". So: promo status is
supported by the official page plus GameWith's 「PROMO-B 第13弾で入手」; the damage is a live 180-vs-190 conflict; cost
colours, weakness and retreat are unpublished.

**What to change (applied).** Step 11 no longer hardcodes 190: damage joins cost, weakness and retreat as "from the
Limitless page, never guessed". Section 1's "not in B4b" states its evidence.

### F8. Summarised web reads are not evidence; one verbatim re-read fixed a list, another confirmed one (method; applied as a note)

My first WebFetch of GameWith 578648 returned mirror cards "Charmeleon, Cleffa, Seadra, Toedschinelle" and new-art
cards "Monotype Girl, Pawmi". A second fetch asking for verbatim Japanese returned the 13 mirror names リザード,
リーシャン, ハクリュー, トドロクツキ, いにしえの闘技場, ブーストエナジー古代, セレビィ, ビクティニ, セグレイブ, ライチュウ,
オトシドリ, ギルガルド, オノノクス, which match `01_set.md` table B name for name (Charmeleon, Chingling, Dragonair,
Roaring Moon, Arena of Antiquity, Ancient Booster Energy Capsule, Celebi, Victini, Baxcalibur, Raichu, Bombirdier,
Aegislash, Haxorus). `02_upstream.md` recorded the same failure mode for `card_ids.rs`. Table B's membership is now
verified verbatim; the printing each foil uses is still not (F1).

### F9. Files and pins the procedure omits or under-states (omission; applied)

- **`lib/s216_card_catalog_v1.json` provenance goes stale by step 9 itself.** Its `sources` block pins `lib/card_canon.py`
  sha `f5cc6496…` and `results/CANON_MAP.tsv` sha `5cd54a2c…` (`03_fork.md` section 5). Step 9 edits `card_canon.py`
  (`EXPECTED_IDS`, `SET_ORDER`) and rebuilds `CANON_MAP.tsv`, so the catalog's recorded sources no longer describe the
  files beside it even though the catalog is untouched. Nothing in the repo verifies those two shas (grep for
  `f5cc6496`, `5cd54a2c`, `source_sha256` over `*.py`: only `card_canon.py`'s own header and `candidate_run.py`, which
  hashes the catalog file itself), so nothing breaks; but the README treated the catalog as wholly separate (open
  question 8). Record it in the step-9 handover.
- **A base_id pin for the canon rebuild.** `card_canon.py` `build` picks `min(members, key=_sort_key)` (line 228) and
  `_sort_key` raises on a set outside `SET_ORDER` (190-195). Inserting `'B4b'` before `'P-A'` cannot flip an existing
  base_id (every B4b class also has a B1-B4 member sorting earlier), but the check costs nothing: diff the old and new
  `CANON_MAP.tsv` on the 3,879 existing ids, base_id column, expect 0 changes. Added to step 9's pin.
- `lib/card.py` (lines 47-51) and `lib/deck_check.py` (lines 24-44) look ids up by string with no set-code list, so
  "B4b 001" works as soon as the LF copy is refreshed. Verified; step 9's smoke test stands.

### F10. Verified this pass (upgrade from "unverified")

| README item | Now | Evidence |
|---|---|---|
| "14,000-game size ... not recounted from the jsonl files" | 14,000 lines in `rl/results/per_game_table_2026-09-25/k3_500.jsonl`; 2,500 + 11,500 = 14,000 in `rl/results/public_pricing_2026-09-25/kp3_500_worst5.jsonl` + `kp3_500_rest.jsonl` | PowerShell `Measure-Object -Line` |
| HEAD `4924008`; `engine/` identical to `7fc6ccb` | `git rev-parse --short HEAD` = 4924008 (2026-09-26 00:53 -0500); `git diff --stat 7fc6ccb HEAD -- engine/src engine/tests engine/examples engine/Cargo.toml engine/Cargo.lock engine/database.json` empty; `git status --short` shows only untracked result folders (now also `rl/results/kt_carrier_census_2026-09-26/`) | GitHub Desktop git, read-only |
| Upstream head `f01e695` (2026-09-17), no B4b data | https://api.github.com/repos/bcollazo/deckgym-core/commits?sha=main : f01e695… 2026-09-17T21:10:12Z is newest; `...&path=database.json` : newest is eb71f845… "b4a" 2026-08-27T12:18:29Z | API, 2026-09-26 |
| Upstream 104 ahead / 0 behind the merge base | https://api.github.com/repos/bcollazo/deckgym-core/compare/8b40f55d889b89634467cca7da153114789ffdf4...main : status ahead, ahead_by 104, behind_by 0 | API |
| Limitless B4b page | still HTTP 404; the set index https://pocket.limitlesstcg.com/cards lists B4a (27 Aug 26, 110) as newest | fetch |
| Release date and "every ♦♦♦♦" | "Tuesday, September 29, 2026, at 6:00 p.m. PDT"; "including reissues of every ♦♦♦♦ card from those expansions" | official page, verbatim |
| Upstream import timing "within about a day of release (dates unverified)" | B4: Limitless 30 Jul 26, upstream "B4" commit 2026-07-29T05:59:23Z, i.e. about 19 hours **before** the 6 pm PDT launch; B4a: Limitless 27 Aug 26, "b4a" 2026-08-27T12:18:29Z, about 11 hours after. Upstream's source precedes the app launch, so the watch can start Sept 28 | Limitless index + API |
| Serebii B4b | count "?? (?? Normal, ?? Secret)", table empty, 13 preview cards; still says "some new cards" | fetch |
| Replay cost | k3 table 1,792 s and kp3 table 1,561 s wall in the cloud (`rl/results/per_game_table_2026-09-25/timing.txt` line 1; `rl/results/public_pricing_2026-09-25/README.md` line 64): both identity replays about 1 hour at cloud speed, consistent with B2e's 1.7 h per 48,000 games. The "quarter to half a WSL day" estimate is not off by 2x unless the laptop is more than 4x slower than the cloud, which is unrecorded | files |
| A4b precedent "0 of 379 differ" | reproduced: 379 entries, 0 without an identical non-A4b printing on all fields but id, rarity, booster_pack; A4b Pokémon by stage: 190 Basic, 100 Stage 1, 39 Stage 2 | PowerShell |
| `card_ids.rs` lines 3677-3678 (`B4a110TeamRocketsGoozooka`, `PA001Potion`); `deck.rs` line 174; `apply_trainer_action.rs` 329; `move_generation_trainer.rs` 345; `apply_action_helpers.rs` 638; `trainer_coin_plan.rs` 101; `public_reply.rs` 624-625; `card_validation.rs` 91-113; nine `engine/tests/b4a_*.rs` files incl. `b4a_trainer_batch2_test.rs` | all as cited | reads and greps |

### F11. Still unverified after this pass

- That the fork's three data files equal upstream's after CRLF normalisation (`02_upstream.md` section 5): not re-done
  here (it needs the 2 MB upstream files; not downloaded).
- Mega Garchomp ex's damage (180 GameWith box vs 190 spoiler image), cost colours, weakness, retreat, Promo-B number;
  whether it is truly outside the B4b set list (F2, F7).
- The B4b count, numbers, membership of the ◊◊◊◊ pool, and which printing each foil uses (F1).
- Main's test count at `7fc6ccb`; that the suite is green; that the replay passes: no build allowed tonight.
- The laptop-to-cloud speed ratio for the replay; the merge-trial budget (2-4 cloud days) has no comparable on record.
- C1 on October 28 (pokemon-zone schedule; pokemon-zone returned 403 to me today).

## What was applied to README.md

Each edit carries a "(skeptic: ...)" tag: section 1 (evidence for "not in B4b", stale GameWith sentence, the Trainer-arm
scale and its effect on the estimate, the replay-cost figures); section 2 step 0 (per-number Limitless check, count
pin, watch from Sept 28), step 2 (no new text, not no new card), step 3 (scale, table-driven test, what line 44
covers), step 6 (consumer check), step 9 (base_id pin, catalog provenance note), step 11 (damage unverified); section 3
step 3 (the rare_candy path and the invariant) and step 5 (per-number and per-card checks); the "Unverified (collected)"
list (items moved to verified with evidence); the paste-ready block.
