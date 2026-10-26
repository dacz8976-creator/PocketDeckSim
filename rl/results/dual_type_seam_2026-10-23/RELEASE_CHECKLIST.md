# Dual Fusion (C1) release checklist

Set C1 goes live Wed Oct 28, 6 pm PDT, which is Oct 29, 01:00Z. This checklist was asked for in coordinator-035, the advisor's code review of the seam branch. Every item has an owner.

The engine work is on branch `laptop/dual-fusion-release-prep-2026-10-24`: the dual-type seam, plus B4b + P-B data, plus scripted id arms. Nothing goes to main without Dustin's word.

**Owners:**
- **L:** the laptop session.
- **C:** the coordinator.
- **D:** Dustin.

## Before the release (by Oct 28)
| # | Item | Owner | State |
|---|---|---|---|
| 1 | **The B4b Trainer reprints:** scripted id arms (coordinator-035 option (b)). A reprint goes into every pattern and list that names its base printing (same name, same effect text), via `tools/add_reprint_arms.py`. Then card_status, the suite and identity replays against main-4d48844, at night. Release night only takes data. | L | done: 9fcffb5c; night check PASS (build, generator, card_status 438/438 Complete, suite 2,228/0, identity 18/18), RELEASE_PREP_RESULT.md |
| 2 | **A clean port of upstream #395** (Trainer logic keyed by effect text), to stay closer to upstream. | L, after the release; C schedules | later |
| 3 | **Protect frozen-7.** `lib/card.py` is in frozen-7's identity list (`rl/ai_judge/freeze_identity.py:20`), and this branch changes it.<br>- The run 3 kit reads ONLY the tag judge-prompt-frozen-7's own worktree.<br>- This branch is merged into no tree the kit or the judge uses until `RESULTS_run3.md` is filed. | L (the kit), C (any merge) | in force |
| 4 | **The generator guard.** When upstream adds a Pokémon field, `card_enum_generator` stops. Then: read the new field; extend `KNOWN_POKEMON_FIELDS`, and `PokemonCardWire` if it is a type field; rerun.<br>The Python readers use a different rule: any field whose name contains "type" is refused (`lib/card.py` `printed_types`), so extend that list too. | L | ready |
| 5 | **The QR catalog: a gated step.** New cards decode as `UNKNOWN pokemon:N` until the community catalog release that holds them is pinned (`lib/s216_card_catalog_v1.json`, built in Pocket Deck Lab; Energy bytes 9-10 are still unverified).<br>Everything downstream of a post-release game waits for this step: exact lists, deck reads, deck-journal versions, predictions and exam points. | L; C tells D | waits for the catalog release |
| 6 | **Any-of is the rule for every printed-type check.** The basis is fan-sourced and unverified: `rules/05_open_questions.md` #32. The shot-list row is added after the release, once D has a dual-type card. | C (shot list) | noted |
| 7 | **The chokepoint's doc** no longer claims that the 12 in-play `has_printed_type` checks go through it (`state/mod.rs`). | L | done |
| 8 | **Tests.** A printed second type together with Double Type is pinned by `double_type_ability_still_replaces_the_printed_set`. The test file now notes that the synthetic cards are mutated in place, so the tests assume every site reads the card itself, never the database again. | L | done |
| 9 | **Energy-zone inference** (`deck.rs`): keep the TODO, don't guess. | L | in force |
| 10 | **UPSTREAM.md:** the #429 comment as posted (coordinator-036). Only database.json is guarded against unknown fields; saved states and positions still ignore them. | L | done (seam f14f37c0) |
| 11 | **The Urshifu gap, which is live.** Both Urshifu are printed [W] / [D] and are [F] only in play, so "+X if the defender is a [F] Pokémon" misses them, on main too. At the release step, route every defender-type check (the 12 in-play `has_printed_type` sites) through the chokepoint, together with the any-of rule and an Urshifu test. | L; C confirms the rule | release step |
| 12 | **The Ultra Beast list (coordinator-054, Dustin's yes: "include the Buzzwole Ultra Beast fix (with a test) in the Dual Fusion release batch; adoption still on my word with the release").** `ULTRA_BEAST_NAMES` (hooks/core.rs) lacked non-ex Buzzwole (B2 014, B2 159), so Lusamine and Ultra Thrusters refused it (run 3's 3 build drops). Fixed with `tests/ultra_beast_list_test.rs`. **Upstream candidate:** upstream's list has the same gap; posting needs D's OK per post. | L; D adopts with the release | code + test committed; suite at night |

## Release night and after (heavy work in the night window only)
| # | Item | Owner |
|---|---|---|
| R1 | **Watch for C1 data:** `git -C ~/upstream_watch fetch && git -C ~/upstream_watch log origin/main -- database.json`. Record the commit. Upstream's set data has landed between 19 h before and 12 h after a launch. | L |
| R2 | **Take upstream's `database.json`** at that commit onto the release branch, with CRLF endings. Regenerate `card_ids.rs` and `database.rs` with our generator; on an unknown field, see item 4. Compare with upstream's generated files (`tools/gencmp.py`). | L |
| R3 | **New card text.** List new texts with `card_enum_generator --incremental-attack-map` / `--incremental-ability-map` (a text with a non-breaking space is a known false positive). Implement each new mechanic with one Game-level test. For C1 Trainer reprints, run `add_reprint_arms.py` again; a new Trainer needs code. | L |
| R4 | **The checks:** build; the suite; `card_status` (no MissingTrainer for a card in scope); identity replays against the current main engine (the table runs, `tools/replay3.py`). | L |
| R5 | **The `lib/` refresh:** the LF copy `lib/deckgym-database.json`; `card_canon` EXPECTED_IDS, SET_ORDER and CANON_MAP; `deck_classifier` SET_ORDER. | L |
| R6 | **The release:**<br>- the release record and manifest, and D's word to switch;<br>- fold in the held tests-only fixes (59fc3054);<br>- the slow-report pin, the kx3 rebuild and the self-check digests (km3's source changed in `fuel_credit.rs` and `value_functions.rs`). | L builds; C reviews; D decides |
| R7 | **The QR catalog refresh** (item 5), before any post-release game is used. | L |
| R8 | **The rules:** the shot-list rows for the dual-type questions (#32 above), and the release-step rule for item 11. | C, D |
