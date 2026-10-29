# Release notes: Dual Fusion (C1), a partial compatibility update, merged into main Oct 28

**Adopted Oct 28, 2026, as a partial compatibility update.** The coordinator asked Dustin: "Adopt the Dual Fusion engine update into main?" At about 22:50Z, he answered by sending Astra's review, whose lead line is: "My recommendation is yes: adopt it as a partial compatibility update." He confirmed it in the laptop session's chat at about 23:00Z: "Yes". The review's three qualifications are written into this file: the unconfirmed rulings stay visible, no claim that old cards play exactly as before, and item 11 is deferred.

## What the merge brings
Branch `laptop/dual-fusion-release-prep-2026-10-24` at d0792568, 16 commits, merged into main:
- **The dual-type seam.** A printed type set for Pokémon cards, behaviour-neutral (2057fa7b). deck_classifier leaves dual-type candidates out of its suggestions (e57d8678). UPSTREAM.md notes (8fe5f9e5, f14f37c0). The step 1 night record (5f5d22dc).
- **The B4b and P-B data.** The data (eb767768), the 82 B4b Trainer reprint arms (9be42ddf), the checklist and small fixes (9fcffb5c), and the night record (cc5d6e04).
- **The Ultra Beast list.** Non-ex Buzzwole (99ecccaa), then Blacephalon ex, Guzzlord and Ultra Necrozma ex, with every tagged printing tested (248e3152), plus the lane record (fc820fe7).
- **Release night.**
  - **A (b290e223):** upstream #430's Dual Fusion data on our seam, our generator, and test updates. `engine/database.json` equals upstream 20d1857's apart from line endings; ours keeps CRLF.
  - **B (63cbb6ab):** #431, the 18 Dual Fusion ex designs. Moltres ex is untouched.
  - **C (d0792568):** #432, the 6 Dual Fusion Supporters, with both printings of each.
- **Checklist item 14** (fad6757b): only the checklist row is added. The Drive copy itself is still to do.

Main's own commits since the merge base (b78c8997) touch no file under `engine/`, so main's `engine/` after the merge is d0792568's tree, and the build and suite below hold for it. One file changed on both sides, `lib/card_canon.py`: main's temp-file cleanup and the branch's dual-type reading. Git merged it without a conflict.

## What it does not switch: the official engine programs
START_HERE's official-engine line, `project_manifest.json` and `current_engine.py` still name `rl/engine-2026-10-21/` (main-4d48844).
- That engine's 3,879 cards include none of the 429 B4b printings, the 9 newer P-B printings (P-B 095-103), or the C1, SP1 and P-C printings.
- The manifest's statement that main's `engine/` equals its built commit stops being true until R6.
- The switch is checklist R6, which was part of the adoption question Dustin answered:
  - the release record and manifest;
  - the held tests-only fixes (59fc3054);
  - the slow-report pin, the kx3 rebuild and the self-check digests.
- Until R6, the screen, the floor and the slow report play on main-4d48844.
- A deck with any of those printings can only be played by a program built from main's source.
- QR codes for new cards decode as `UNKNOWN` until R7 (the catalog refresh).

## A partial compatibility update: 205 of the 260 new printings
| Set | Printings | Complete | Missing attack | Missing ability | Missing Trainer | Missing Tool |
|---|---|---|---|---|---|---|
| C1 | 217 | 166 | 28 | 15 | 6 | 2 |
| SP1 | 30 | 30 | 0 | 0 | 0 | 0 |
| P-C | 13 | 9 | 3 | 0 | 1 | 0 |
| **All** | **260** | **205** | **31** | **15** | **7** | **2** |

- **"Complete" means the card's effects are implemented.** It does not mean every ruling is settled (next section).
- **The other 55 printings are blocked by the card-support preflight of `deckgym simulate` and `deckgym optimize`** (`engine/src/cli_preflight.rs`), which refuses a deck that holds any one of them. The floor and the screen (`decks/screen/floor.py`, `run_screen.py`) call `deckgym simulate`, so they do not start with them.
- **Not every program has that check.**
  - `goldfish` (the brew pages) has no preflight: it records each card's engine status in its coverage file, and counts and skips any game that panics.
  - The slow report (`rl/strength`) has no preflight either. Today its pinned build does not know the new cards; after R6 it would.
  - So R6 adds the same refusal to the slow report before the switch.
- **R6 adds the shared refusal to goldfish and the slow report** (branch `laptop/r6-preflight-2026-10-29`; not built yet, it is built and tested at night with R6).
  - **One check.** The blocking logic moved out of `cli_preflight.rs` into the engine library, `deckgym::card_support`. `deckgym simulate`, `deckgym optimize`, `goldfish` and the slow report's program (`strength run` and `strength selfcheck`) all refuse through it, so there is one list of blocked cards.
  - **simulate and optimize are unchanged:** the same messages and exit codes, and their tests are untouched.
  - **The refusal.** Before any game, and before goldfish writes its coverage file or `strength run` writes in its run folder, a deck that holds a card with status CardNotFound or Missing* stops the program with exit 2. The message has the same form as `deckgym simulate`'s ("Card-support preflight failed; goldfish did not start.", then each card's id, name, reason and deck). The check reads only the card database and uses no RNG, so it should not change any game on a supported deck; R6's replays and self-checks will confirm it.
  - **The opt-out:** `--allow-unsupported-cards` (goldfish, `strength run`, `strength selfcheck`). The program first lists each unsupported card on stderr (id, name, reason, which deck), then runs. `slow_report.py` never passes it, so a slow report of such a deck stops with the program's message.
  - **The tests** use C1 019 Volcanion (MissingAttack):
    - `engine/tests/goldfish_card_support_test.rs`, in the suite;
    - `rl/strength/test_strength_card_support.py`, which runs a real program: `STRENGTH_PROGRAM=<the R6 kx3 rebuild> python3 -B -m unittest -v test_strength_card_support` from `rl/strength`. It is skipped without that variable.
  - **One test is red until the re-pin.** `rl/strength/src/main.rs` is part of the harness source the pin hashes (`src/*.rs` and `Cargo.toml`). On this branch that hash is `c4f7da21…`; the committed pin's `harness_source_sha256` is `bf9c5d68…`. So `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` in `test_slow_report_registration.py` fails (1 of 244), and the cloud route (`--program`) refuses a rebuild from this checkout. Both last until R6's re-pin, after its own gate, records `c4f7da21…` in `slow_report_pin.json` (never edit the hash by hand). The branch lands in the same merge as the re-pin, and `test_slow_report_registration.py` is run after it.
  - **A refused slow report keeps its seed slot.** `slow_report.py` registers before the program first runs, so a refused deck leaves a registered folder with no games, and that folder holds its seed slot in the pin's block until it is removed. With `--register-only`, the refusal shows only at the first sitting.
  - **Two goldfish callers hide the message.** `lib/brew_pages.py` and the coverage step of `decks/screen/floor.py` (it runs before `deckgym simulate`) run goldfish with `check=True` and capture its output. On a refused list they stop with Python's "returned non-zero exit status 2" and do not show the card list; run goldfish by hand to see it. Making them print it is a follow-up: both files' sha256 are recorded inputs of the floor replays.
- **Older printings:** all 4,577 cards were checked, and no older printing is anything other than Complete or RulesUnverified. B4b Trainer reprints keep the same status as their other printings.

## Unconfirmed rulings (still OPEN in `rules/05_open_questions.md`)
- **#33, Rising Star.** The engine counts both printed types of a dual-type Pokémon in play, and both types that Urshifu's Double Type gives. It counts through the chokepoint that Weakness uses. This is the plain reading, not seen in a game. If the game counts one type per Pokémon, the engine allows Rising Star in some boards where the game would not.
- **#34, Serena's Choice with a full hand.** The engine leaves the card in the deck and still shuffles; upstream allows an 11-card hand. Not seen in a game. The question for the upstream maintainer is in `engine/UPSTREAM.md`.
- **#32, any-of for printed-type checks** (checklist item 6). The source is fan-sourced and unverified.

## Not "old cards play exactly as before"
- **The replays matched.** The 17 replays of earlier runs that play games gave the same games on d0792568 as on main-4d48844 ("v f: SAME"). The 18th, goldfish, plays no games, and its page is SAME.
- **The Ultra Beast fix is a deliberate change.** It corrects previously incorrect behavior: non-ex Buzzwole, Blacephalon ex, Guzzlord and Ultra Necrozma ex now count as Ultra Beasts everywhere the engine reads its list (`ULTRA_BEAST_NAMES`).
  - Lusamine and Ultra Thrusters accept them; before, both refused them. The refusal of non-ex Buzzwole cost run 3 three builds.
  - Beast Wall's damage cut and Beastite's damage bonus now apply to them; before, both skipped them.
  - The bots' Lusamine pricing (`players/fuel_credit.rs`) counts them too.
  - The replayed decks don't reach this.
- **Other changes the replays don't reach.**
  - The B4b reprint arms and the new cards add printings. The replays cover the listed decks only.
  - Poke Mart Guy (C1 129/169) is Complete but for now only shuffles the deck. The three Items it fetches (C1 120-122) are MissingTrainer, so the preflight refuses any deck that holds them.

## Deferred: checklist item 11 / R8, the Urshifu gap (NOT done)
- **The gap:** both Urshifu are printed Water (B3 051) and Darkness (B3 113), and are Fighting only in play, through their Ability Double Type. Twelve in-play checks read the printed type with `PlayedCard::has_printed_type`, so they do not see a type that Double Type gives.
  - 2 are on the opponent's side: the "+X if the defender is a [X] Pokémon" and "if the opponent has a [X] Pokémon in play" bonuses.
  - 10 are on the player's own Pokémon: Leaf Cape, Jungle Totem, Deceptive Needle, the Chase Order bench filter, Forest Breath, Wash Out and Psychic Connect.
  - So "+X if the defender is a [F] Pokémon" misses Urshifu.
- **Status:** the checklist assigned the fix to this release step, and it was not done in A, B or C. It was already live on main before this merge, so it is not a regression.
- **The repair goes on a separate branch:** the 12 checks are routed through the chokepoint with the any-of rule, with an Urshifu test and the suite. It goes into main only on Dustin's word.
- **R8's rule rows** (the shot-list rows for #32) stay with the coordinator and Dustin.

## INFORMATION_MODEL v8: a pooling boundary
Commit C raises the information model to v8 (`engine/src/observation.rs`; what Serena's Choice reveals).
- Run 3, K21 and the exam rows are v7.
- They stay frozen and unchanged, and v7 and v8 rows are not pooled.
- The run 3 kit and the AI judge read only their own tag worktrees. RESULTS_run3.md was filed on Oct 26, before this merge (checklist item 3).

## Compatibility only
This release establishes that the engine reads the new cards and has implementations for 205 of them (card_status Complete). The lane played no game with a new card: the 18 replays use earlier decks only. It does not measure or improve the bots' play, and it is not deck advice.

The bots' code changed only so that they read the new cards:
- their type checks read the printed type set (`fuel_credit.rs`, `value_functions.rs`);
- C1 012 Amoonguss's Astonish joins the audited public-pricing texts (`public_pricing_player.rs`, J0);
- the random player gives the new `TakeTopDeckCardAndShuffle` action weight 5, as upstream does.

Their play on the new cards has not been measured. km3's source changed, so R6 rebuilds kx3 and its self-check digests.

## The release lane (Oct 28, laptop; `release_lane_2026-10-28/`)
The lane ran twice: on A alone (b290e223), then on A+B+C together (d0792568, the merged tip). B was not checked on its own. Each run was: a build; the generator compared with upstream's generated files (gencmp); card_status for all cards; the suite; 18 identity replays. The replays compare against main-4d48844 (v f) and against the 08a9b3a references.

| | A b290e223 | A+B+C d0792568 |
|---|---|---|
| build | OK, 341 s | OK, 330 s |
| gencmp (`card_ids.rs`, `database.rs`) | SAME, SAME | SAME, SAME |
| new printings Complete | 167 of 260 (predicted 167) | 205 of 260 (predicted 205) |
| older cards neither Complete nor RulesUnverified | 0 | 0 |
| Trainer printings with the same name and text but a different status | 0 | 0 |
| suite | 2,236 passed, 0 failed, 0 ignored (predicted 2,236) | 2,275 passed, 0 failed, 0 ignored (predicted 2,275) |
| replays | 18 of 18: PASS | 18 of 18: PASS |

**The replay verdict, the same in both phases:**
- 17 rows say "v f: SAME". 11 of them say "v f: SAME (0 deals)", and the 5 cli rows and run_screen give no deal count. Goldfish plays no games, so it has no v f comparison. No v f comparison DIFFERS, and no row ERRORs.
- Against the 08a9b3a references, every row is SAME except the 3 known Growl-rule differences (see the main-4d48844 notes). They have the same counts as main-4d48844: new17_k3 8 of 8,500, dev_km3_new17 7 of 8,500, 8_new_km3 1 of 16,000.
- Every rules page says "no RULE finding", and run_screen has 20 of 20 lines equal.

A+B (63cbb6ab) was not run as a phase of its own: the plan ran it only if A+B+C failed.

## Still to do (checklist)
- **R5:** the `lib/` refresh (the LF copy `lib/deckgym-database.json`; card_canon's EXPECTED_IDS, SET_ORDER and CANON_MAP; deck_classifier's SET_ORDER).
- **R6:** the switch. It adds the shared card-support refusal to goldfish and the slow report first (above); the cargo build runs at night hours.
- **R7:** the QR catalog refresh. It waits for the community catalog release that holds the new cards.
- **Item 14:** the release files to Drive.
- **Item 11:** the separate branch.
- **Item 2:** the #395 port.
- **Separate follow-ups, each on Dustin's word:** upstream 20d1857's later fixes (#433, #435, #438), and Serena's Choice through Penny/Portrait.
