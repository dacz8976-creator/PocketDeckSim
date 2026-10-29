# Release notes: Dual Fusion (C1), a partial compatibility update, merged into main Oct 28; official programs from Oct 29 (R6, main-affe56e)

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

## What the merge did not switch: the official engine programs (switched at R6, Oct 29: section "R6" below)
Until R6, START_HERE's official-engine line, `project_manifest.json` and `current_engine.py` named `rl/engine-2026-10-21/` (main-4d48844).
- That engine's 3,879 cards include none of the 429 B4b printings, the 9 newer P-B printings (P-B 095-103), or the C1, SP1 and P-C printings.
- The manifest's statement that main's `engine/` equals its built commit stops being true until R6.
- The switch is checklist R6, which was part of the adoption question Dustin answered:
  - the release record and manifest;
  - the held tests-only fixes (59fc3054);
  - the slow-report pin, the kx3 rebuild and the self-check digests.
- Until R6's engine switch (Oct 29), the screen and the floor played on main-4d48844. The slow report still plays on it until its own re-pin, after its kx3 replay check (section "R6").
- Until that switch, a deck with any of those printings could only be played by a program built from main's source.
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
- **Before R6, not every program had that check.**
  - `goldfish` (the brew pages) had no preflight: it recorded each card's engine status in its coverage file, and counted and skipped any game that panicked.
  - The slow report (`rl/strength`) had no preflight either. Its pinned build (kx3 on main-4d48844) does not know the new cards; the build for its re-pin on main-affe56e does.
  - So R6 added the same refusal to both.
- **R6 added the shared refusal to goldfish and the slow report** (branch `laptop/r6-preflight-2026-10-29`, merged into S as 6e1ff1d0; built and tested on Oct 29, section "R6"). The official goldfish refuses from the switch; the slow report refuses from its re-pin.
  - **One check.** The blocking logic moved out of `cli_preflight.rs` into the engine library, `deckgym::card_support`. `deckgym simulate`, `deckgym optimize`, `goldfish` and the slow report's program (`strength run` and `strength selfcheck`) all refuse through it, so there is one list of blocked cards.
  - **simulate and optimize are unchanged:** the same messages and exit codes, and their tests are untouched.
  - **The refusal.** Before any game, and before goldfish writes its coverage file or `strength run` writes in its run folder, a deck that holds a card with status CardNotFound or Missing* stops the program with exit 2. The message has the same form as `deckgym simulate`'s ("Card-support preflight failed; goldfish did not start.", then each card's id, name, reason and deck). The check reads only the card database and uses no RNG, so it should not change any game on a supported deck; R6's replays and self-checks found no change on the decks they played (section "R6").
  - **The opt-out:** `--allow-unsupported-cards` (goldfish, `strength run`, `strength selfcheck`). The program first lists each unsupported card on stderr (id, name, reason, which deck), then runs. `slow_report.py` never passes it, so after the slow report's re-pin a slow report of such a deck stops with the program's message. Until the re-pin, the pinned program has no such check: it stops at the first sitting with a panic, `deck <file>: Card ID not found for id: <id>`, because it cannot load the deck (section "R6").
  - **The tests** use C1 019 Volcanion (MissingAttack):
    - `engine/tests/goldfish_card_support_test.rs`, in the suite;
    - `rl/strength/test_strength_card_support.py`, which runs a real program: `STRENGTH_PROGRAM=<the R6 kx3 rebuild> python3 -B -m unittest -v test_strength_card_support` from `rl/strength`. It is skipped without that variable.
  - **One test is red until the re-pin.** `rl/strength/src/main.rs` is part of the harness source the pin hashes (`src/*.rs` and `Cargo.toml`). On this branch that hash is `c4f7da21…`; the committed pin's `harness_source_sha256` is `bf9c5d68…`. So `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` in `test_slow_report_registration.py` fails (1 of 244), and the cloud route (`--program`) refuses a rebuild from this checkout. Both last until R6's re-pin, after its own gate, records `c4f7da21…` in `slow_report_pin.json` (never edit the hash by hand). Planned to land with the re-pin, the branch landed instead with R6's engine programs: it is part of S, the built commit, and main's `engine/` must be S's tree. So from main's move (Oct 29) until the re-pin this one test fails on main, and the cloud route refuses a rebuild from main's checkout; the laptop's pinned program is unaffected. `test_slow_report_registration.py` is run again after the re-pin.
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

## R6: the official programs switch to main-affe56e (Oct 29)
In plain words:
- The official programs are now this release's. The new cards play, except 55 printings, which `deckgym simulate`, `optimize` and `goldfish` refuse (exit 2, with the list of cards). Poke Mart Guy only shuffles for now, and two rulings on new cards are still open (#33 Rising Star, #34 Serena's Choice).
- So the screen, the floor and the brew pages stop on a deck that holds one of those 55.
- The slow report stays on the old engine (main-4d48844) until its own check on the new engine passes, and its pages say so. Until then, don't start a slow report of a deck that holds any card printed in B4b, P-B 095-103, C1, SP1 or P-C, new-art reprints of old cards included: the old engine cannot load them.
- This is a compatibility update only. On the replayed decks the new programs gave main-4d48844's results, but that does not make every old card play as before: the corrected Ultra Beast list changes some on purpose. Nothing here measures how well the bots play the new cards.

Dustin's words, verbatim, with their sources:
- **The adoption.** Oct 28, in the laptop session's chat at about 23:00Z: "Yes", to adopting d0792568 into main with R5-R7 as follow-through (top of this file; coordinator-069). R6 is this switch (`RELEASE_CHECKLIST.md`, R6: "part of the adoption question D answered on Oct 28"). It is a "partial compatibility update": Astra's qualification, via coordinator-069.
- **The two-step pin.** His Oct 21 words, via coordinator-072: "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine."
- **Baselines as on Oct 21.** His Oct 21 words, via coordinator-072: "Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a future decision relies on them." The old rows are listed below as pre-R6/v7 ("Tied to the old engine"); their files are left as they are, and nothing is recomputed.
- **goldfish's and the slow report's refusal** is coordinator-071's decision. At about 00:05Z on Oct 29 the coordinator told Dustin that two of our own tools, goldfish and the slow report, did not block the 55 unsupported printings, and that both would refuse them, each with a test, before the rebuild. He did not object (coordinator-072). The refusal stops unsupported decks only; it changes no result.

### What the adoption activates
- **The three programs** in `rl/engine-2026-10-29/` (`deckgym` 1dc857ae… blob, sha256 6a2617f4f9e91c9ca4bb4cb3227fdd8e29ff100bbcfd8e0b1fee8273f866f6f8; `legality_scan` d9805aaaa10a2a70a40cffa4858efd5baf15deff183d144981856ac4d5dca702; `goldfish` ea787a4ed5b6bb9771ffefecf2737a76335efd918ad4138befe888df3322f342): S's tested bytes, the same git blobs as `r6_release/programs_final/`, mode 100755, never rebuilt.
- **The current-engine selector.** `project_manifest.json`'s `available_release` names them. `current_engine.py`, `decks/screen/floor.py` and `decks/screen/run_screen.py` read it, so the screen and the floor switch with the manifest. `make_predictions.py`'s `CURRENT_ENGINE` moves with it: floor pages made on `rl/engine-2026-10-29/deckgym` count as current, and no slow report does until the slow report's re-pin.
- **goldfish's refusal.** The brew pages and the floor's coverage step now stop on a deck that holds an unsupported card (exit 2) instead of counting and skipping its panicking games. On the replayed decks nothing changes: goldfish's page and coverage file are byte-equal to the reference.
- **The slow-report program: not moved by this commit.** The pinned program stays kx3 on main-4d48844's engine (`/home/dacz8976/kx_r3/strength`, sha256 7d046b6f…; 87a7f340, engine tree 64de03e2). Every page names it in its headline ("kx3 (d513e37b, on main-4d48844)"; `rl/strength/README.md` says so too), and `make_predictions.py` counts no slow report as current. The re-pin's program is built and checked: kx3's six files on S (K e3ddc014, branch `laptop/kx3-on-r6-2026-10-29` on origin, not main; engine tree cd970db60aa5), built with `rl/strength/build.sh` at STRENGTH_JOBS 2 (`/home/dacz8976/kx_r4/strength`, sha256 23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378, 177 s; harness c4f7da21…; build record OK); both self-checks equal to the pin's texts (km3 81b572198c04d5d1; kx3 31d638dbc818b0fa, 4738 s). Its kx3 replay check comes next; the re-pin follows only if it passes. **Until the re-pin, don't start a slow report of a deck that holds any B4b, P-B 095-103, C1, SP1 or P-C printing** (all of them, not only the 55): `lib/deck_check.py` accepts it, so `slow_report.py` registers the folder, and the pinned program then stops at its first sitting because it cannot load the deck (a panic, `deck <file>: Card ID not found for id: <id>`, not the card-support message); the folder keeps its seed slot until it is removed.
- **The harness source moves with S, so one test is red until the re-pin.** S holds the card-support refusal in `rl/strength/src/main.rs` (harness c4f7da21…; the pin says bf9c5d68…). From main's move until the slow-report re-pin (after its kx3 replay check), `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` in `rl/strength/test_slow_report_registration.py` fails on main (1 of 244); the re-pin turns it green. Until then the cloud `--program` route must not rebuild from main. The laptop's pinned slow report is unaffected. The preflight section above planned this branch to land with the re-pin; it is part of S, so it lands with the engine (accepted, coordinator-076).

### Release identity
- Built from S = affe56e88985e2997a66beb85efaca0c487617bd (2026-10-29, 00:37-00:43 UTC); engine tree c8c79c635b92. main's `engine/` after the adoption is that tree, byte for byte: no exception. The tests-only fixes held back on Oct 21 are folded into S, so no tests-only exception remains.
- Built in the clean worktree at S with the shared target directory `/home/dacz8976/dual_target` (reused), not in a fresh folder as on Oct 21. The committed programs are the bytes the night's checks ran: `r6_release/RAN_SHA256.txt` shows by sha256 that each replay ran `programs/R`'s programs and each floor piece `programs/R/deckgym`, all equal to `programs_final/` (the floor's coverage step ran the then-official goldfish, below), and that the self-checks ran `/home/dacz8976/kx_r4/strength`, equal to its build record.
- The build record is aa8093c9 (branch `laptop/r6-record-2026-10-29`), the commit this one sits on. A first record of the same night, 26ac0da0 (the tip of `laptop/r6-release-2026-10-29`), is superseded: it holds the same programs and logs, but its floor table, record.json's floor rule and its copies of the day scripts had errors that review found before main moved. `r6_release/RUN_CONTEXT.txt` names the checkout the floor and the replays read (`/home/dacz8976/pincand` at b78c8997) and shows their runners byte-equal to S's.
- **Activation checks** (after the merge, in the repository root, on Linux):
  1. `cd rl/engine-2026-10-29 && sha256sum -c SHA256SUMS`: three OK lines.
  2. `git ls-tree HEAD rl/engine-2026-10-29/`: deckgym 1dc857ae…, legality_scan e2cf615d…, goldfish adc79d2d…, each 100755.
  3. `python3 current_engine.py`: prints this repository's `rl/engine-2026-10-29/deckgym` (it refuses a file whose hash is not the manifest's).
  4. The manifest's three sha256 equal `SHA256SUMS`.
  5. `git rev-parse HEAD:engine` prints c8c79c635b92c9f95c5bf1db7f77d7774f8813ca, S's engine tree.

### R6's night on S (`r6_release/`)
| Check | Result |
|---|---|
| Build: deckgym, legality_scan, goldfish | OK in 364 s (2026-10-29, 00:37-00:43 UTC) |
| gencmp (`card_ids.rs`, `database.rs`) | SAME, SAME |
| card_status | all 4,577 cards; 205 of the 260 new C1, SP1 and P-C printings Complete (31 missing an attack, 15 an Ability, 7 a Trainer, 2 a Tool); older cards neither Complete nor RulesUnverified: 0 |
| Suite | 2,277 passed, 0 failed, 0 ignored (794 s) |
| The folded hit-back tests under the switches | 32 of 32 under the default, DECKGYM_FLAT_RETURN_DAMAGE and DECKGYM_ROUND2_OFF each, and core's hit-back module 14 of 14 under DECKGYM_ROUND2_OFF |
| 18 identity replays (side r = S's programs) | 18 of 18 runs, 156,520 games or deals, on the replayed decks (old cards only): the 17 that play games give main-4d48844's results ("v f: SAME"), 11 of them compared deal by deal (0 differing), the 5 cli rows by their whole printed summary and run_screen by its whole 20-line page (2 decks: each deck's total line and its 8 matchup lines; the engine path aside); goldfish plays no games, and its page and coverage file are byte-equal to the 08a9b3a reference; against the 08a9b3a references only the 3 known Growl-rule rows differ (new17_k3 8 of 8,500, dev_km3_new17 7 of 8,500, 8_new_km3 1 of 16,000), as on main-4d48844; every rules page says no RULE finding |
| Floor re-check, 12 pieces, on S's deckgym | 12 of 12 pieces (24,960 games) equal to main-4d48844's final pages: the 11 deck pieces (21,120 games) with games and coverage files byte-equal and pages equal apart from the two lines that name programs, and run_screen (3,840 games; it writes only its 20-line page) equal apart from the engine path; 10 of the 12 also equal the recorded pages apart from those lines, and B_brew-07 (clears the floor, 1,165 of 1,920) and B_brew-09 (clears the floor, 824 of 1,920) differ from the recorded pages exactly as main-4d48844's pages do (its hit-back change) |
| kx3's rebuild on K | `/home/dacz8976/kx_r4/strength`, sha256 23d8a9b5…, build record OK (the engine tree as archived is K's; harness c4f7da21…; jobs 2) |
| Self-checks on it | km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa: equal to the pin's texts |
| Card-support refusal test (`test_strength_card_support`, a real program) | 4 of 4 OK, on kx3's rebuild |
| `rl/strength` Python suite | 1438 tests; 1 failure, the expected one until the re-pin: `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` |

**The replays** (`r6_release/REPLAY_TABLE.md`):

| Run (replayed command) | Games or deals | v the 08a9b3a reference | v main-4d48844 (side f, Oct 21) |
|---|---|---|---|
| `08a9b3a_10_cli_k3` | 240 | SAME: Player 0 won: 150 (62.50%) | SAME |
| `08a9b3a_10_cli_kp3` | 240 | SAME: Player 0 won: 144 (60.00%) | SAME |
| `08a9b3a_10_cli_kog3` | 240 | SAME: Player 0 won: 149 (62.08%) | SAME |
| `08a9b3a_10_cli_kta3` | 240 | SAME: Player 0 won: 149 (62.08%) | SAME |
| `08a9b3a_10_cli_km3` | 240 | SAME: Player 0 won: 149 (62.08%) | SAME |
| `08a9b3a_10_goldfish` | 0 | SAME: page =, coverage = | not compared (plays no games) |
| `08a9b3a_table_k3` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_table_kp3` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_table_kog3` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_dev_km3_table` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_dev_kta3_table` | 14,000 | SAME: 0 differing deals of 14000 | SAME (0 deals) |
| `08a9b3a_10_run_screen` | 3,840 | SAME: run_screen: /home/dacz8976/pincand_work/games/r/08a9b3a_10_run_screen.txt v engine_switch_rules2_2026-10/08a9b3a_10_run_screen.txt: 20 of 20 lines equal (2 decks; the header's engine path aside) | SAME |
| `08a9b3a_new17_k3` | 8,500 | DIFFERS: 8 differing deals of 8500 | SAME (0 deals) |
| `08a9b3a_dev_km3_new17` | 8,500 | DIFFERS: 7 differing deals of 8500 | SAME (0 deals) |
| `08a9b3a_8b_cloud_new_k3` | 240 | SAME: 0 differing deals of 240 | SAME (0 deals) |
| `08a9b3a_8b_cloud_new_km3` | 240 | SAME: 0 differing deals of 240 | SAME (0 deals) |
| `08a9b3a_8_new_km3` | 16,000 | DIFFERS: 1 differing deals of 16000 | SAME (0 deals) |
| `08a9b3a_cov_b2e_km3` | 48,000 | SAME: 0 differing deals of 48000 | SAME (0 deals) |

**The floor re-check pages** (`r6_release/FLOOR_TABLE.md`):

| Piece (1,920 games; run_screen 3,840) | Recorded on main-c045ede | main-4d48844 final build v recorded (floor2F, Oct 21 UTC) | S v recorded, as floor2.py said | S v main-4d48844 final page (floorS_recompare.sh) |
|---|---|---|---|---|
| B_D_victini-passive | clears the floor, 693 of 1,920 | SAME: clears the floor, 693 of 1,920 | DIFFERS (floor2.py): clears the floor, 693 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| A_brew-06 | fail, 125 of 1,920 | SAME: fail, 125 of 1,920 | DIFFERS (floor2.py): fail, 125 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| A_brew-06b | fail, 262 of 1,920 | SAME: fail, 262 of 1,920 | DIFFERS (floor2.py): fail, 262 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| A_control14_k3 | control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | SAME: control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | DIFFERS (floor2.py): control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| A_brew-05b | clears the floor, 577 of 1,920 | SAME: clears the floor, 577 of 1,920 | DIFFERS (floor2.py): clears the floor, 577 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| A_07 | clears the floor, 1,098 of 1,920 | SAME: clears the floor, 1,098 of 1,920 | DIFFERS (floor2.py): clears the floor, 1,098 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| A_run_screen | run_screen, 20 lines | SAME | SAME (floor2.py) | equal (run_screen.txt, 20 of 20 lines apart from the engine path; switch_check.py screen exit 0; this piece writes no games or coverage file): it equals the recorded page as main-4d48844's did |
| B_12 | clears the floor, 635 of 1,920 | SAME: clears the floor, 635 of 1,920 | DIFFERS (floor2.py): clears the floor, 635 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| B_brew-07 | clears the floor, 1,168 of 1,920 | DIFFERS: clears the floor, 1,165 of 1,920 | DIFFERS (floor2.py): clears the floor, 1,165 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it differs from the recorded page as main-4d48844's did |
| B_brew-09 | clears the floor, 837 of 1,920 | DIFFERS: clears the floor, 824 of 1,920 | DIFFERS (floor2.py): clears the floor, 824 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it differs from the recorded page as main-4d48844's did |
| B_D_root | clears the floor, 693 of 1,920 | SAME: clears the floor, 693 of 1,920 | DIFFERS (floor2.py): clears the floor, 693 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |
| B_D_amended | clears the floor, 597 of 1,920 | SAME: clears the floor, 597 of 1,920 | DIFFERS (floor2.py): clears the floor, 597 of 1,920 | equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844's did |

The floor ran from the laptop's main checkout (`/home/dacz8976/pincand` at b78c8997) with S's `deckgym`. floor.py takes coverage from the official release's goldfish, which that night was `rl/engine-2026-10-21/goldfish`, so the re-check itself does not exercise the new goldfish. Its replay row above does, and S's goldfish run on the 11 floor decks the way floor.py runs it (coverage only, no games) gives coverage files byte-equal to these (`r6_release/logs/floor_recheck_S/GOLDFISH_S_COVERAGE.txt`).

**The floor's acceptance rule: rule corrected after the run, games unchanged (not re-run); reviewed by the coordinator (coordinator-080).** floor2.py's comparison against main-4d48844's final pages (its "v floor2F" check) says DIFFERS for 11 of the 12 pieces, for one line only: each page's coverage line names the official goldfish, `rl/engine-2026-10-21/goldfish` (sha256 db52d3de…) that night where main-4d48844's final pages name `rl/engine-2026-10-12/goldfish` (d8cfb779…), because the release moved with the Oct 21 adoption after those pages were made. The coverage files themselves are byte-equal. (Against the recorded pages, floor2.py's main verdict, brew-07 and brew-09 also differ in games, 20 and 64 of 1,920, as they did on main-4d48844; the other 9 deck pieces differ there by the same goldfish line only, and run_screen is SAME.) The night's rule did not allow for that line and marked the step FAILED; the marker is kept (`r6_release/logs/floorS.FAILED.txt`, beside `floorS.done.txt`). The corrected rule: for the 11 deck pieces, games and coverage byte-equal to main-4d48844's final pages and each page equal after normalising only the engine path and that goldfish line; for run_screen, which writes only its 20-line page, that page equal apart from the engine path. All 12 pass (`r6_release/tools/floorS_recompare.sh`; its output is `r6_release/logs/floor_recheck_S/RECOMPARE.txt`). The project's own comparators agree: `sitting1_check.py floor --allow-coverage-program` and `switch_check.py screen`, S against main-4d48844, exit 0.

### Tied to the old engine (pre-R6/v7): not re-run, nothing recomputed
1. **The slow report and kx3's recorded games**, until the re-pin (above). The reports so far and kx3's replay games of Oct 22 stay main-4d48844's, or older.
2. **Scoreboard v3's frozen cells and thresholds, kta3's status, km3's thresholds, the mixed kt/kta clause-(d) tables and RUN5's development real error:** records of their old engines, as on Oct 21.
3. **The ladder predictions** (`rl/results/ladder_validation/predictions/`), never overwritten. `read_ladder.py` prints "NOT the current engine now" for them.
4. **Run 3, K21 and the exam rows:** v7, frozen, not pooled with v8 rows.
5. **The Oct 12 floor re-check pages and their Oct 21 replays:** records beside the new ones above, never replacements.
6. **The deck journal's "current engine" flags** mean "current when added".

What carries over unchanged: every replayed row that came out equal.

### Checks of the adoption commit (a scratch worktree, before main moved; no engine run)
Run before main moved, on the draft d19b51ad, with `r6_release/tools/verify_r6.sh draft`. The baseline is the same checks on main ffe97adb (`verify_r6.sh baseline`). Python checks only: no engine run, no games.
- The commit's shape: one parent, the build record aa8093c9, whose one parent is S; the 15 paths adopt_r6.py writes. PASS.
- The five activation checks, all PASS: `sha256sum -c` in `rl/engine-2026-10-29/` gives 3 OK lines; the three programs are mode 100755 and are the `programs_final/` blobs (deckgym 1dc857ae, legality_scan e2cf615d, goldfish adc79d2d); `current_engine.py` exits 0 and prints `rl/engine-2026-10-29/deckgym`; the manifest's three sha256 values equal `SHA256SUMS`; the commit's `engine/` tree is S's (c8c79c635b92). The manifest names main-affe56e (source affe56e8, `rl/engine-2026-10-29`) as the available release, and its history ends main-c045ede, main-4d48844, marked superseded.
- `make_predictions.py --selftest`: 136 ok, 0 failed. `read_ladder.py --selftest`: passed.
- `floor_recheck_rules2_2026-10/test_runners` 55 OK; `test_calibration_safety` 168 OK; `test_run_screen_weights` 21 OK; `test_floor_pricing_pilot` 5 OK; `read_km.py --selftest` ok; `test_km_thresholds`: every case gives its known answer.
- `test_journal`: 61 tests, 1 failure (`PartB.test_the_first_fill_holds_the_proposals_and_withdrawn_lists`), the same failure as on main ffe97adb before the draft.
- `rl/strength`'s modules, with KX_RUNS_DIR and STRENGTH_PROGRAM unset: test_slow_report 492, test_slow_report_existing 42, test_slow_report_page 201, test_slow_report_paired 69, test_slow_report_process 115, test_slow_report_runloop 78, test_split_collect 54, test_strength_prereg_use 121 and test_strength_report 18, all OK. test_slow_report_registration: 244 tests, 1 failure, the expected one, `CommittedPin.test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on` (the harness source is now c4f7da21; the pin was made on bf9c5d68). It stays red until the slow report's re-pin. test_strength_card_support: 4 tests, skipped here because STRENGTH_PROGRAM is unset; on kx3's rebuild in the night they ran 4 of 4 OK.
- Against the baseline on main ffe97adb: 18 checks equal, the 2 expected differences above (the CommittedPin failure and the new card-support test), 0 other.
- Earlier drafts passed the same checks: 889ad2a0 (on the superseded record 26ac0da0) and f9399ea3 (on record f772884b). Two reviews of their texts found stale pre-R6 lines and claims wider than the checks; this draft corrects them, and its record is redone so that the day scripts it carries are the ones that wrote this commit.

### Left as is on purpose
- `engine/UPSTREAM.md` stays as built: it is part of S's tree.
- `rules/`: no engine-status line changes at R6. The Ultra Beast correction has no status line there, and `rules/05` #32 still names the seam branch.
- `rl/RUN5.md`'s A5 item still names `rl/engine-2026-10-21/`, now as main-4d48844's engine (pinned Oct 21 to Oct 29): the reproduction it asks for ran against that engine (the release lane's "v f").
- `rules/06_sources.md`'s line on the local card database still says 3,879 cards: an R5 follow-up, not an engine-status line.
- The laptop's `pincand_work` (programs/R, the RR archive, the replay games) stays until the slow report's re-pin.

## Still to do (checklist)
- **R5:** done Oct 29 (main ffe97adb): the `lib/` refresh. Its follow-ups are in the checklist's R5 row.
- **R6:** the engine programs switched Oct 29 (section "R6" above); the slow-report re-pin follows its kx3 replay check.
- **R7:** the QR catalog refresh. It waits for the community catalog release that holds the new cards.
- **Item 14:** the release files to Drive.
- **Item 11:** the separate branch.
- **Item 2:** the #395 port.
- **Separate follow-ups, each on Dustin's word:** upstream 20d1857's later fixes (#433, #435, #438), and Serena's Choice through Penny/Portrait.
