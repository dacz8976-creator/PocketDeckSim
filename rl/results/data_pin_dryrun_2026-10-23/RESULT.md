# B4b + P-B data pin, DRY RUN (Oct 23-24, 2026): what adopting it would take

This is a dry run, not an adoption. The branch `laptop/data-pin-dryrun-2026-10-23` at `95eedb3d` is never to be merged. It is main `b78c8997` plus upstream `dfe6ff30`'s `database.json`, `src/card_ids.rs` and `src/database.rs`, with this repo's CRLF line endings. The procedure is `rl/results/b4b_prep_2026-09-26/README.md`, and PLAN.md's row "B4b (438), P-B 099 and C1 in one data pin". The coordinator gave the GO on Oct 23. It ran on the laptop after the dual-type seam lane: CARGO_BUILD_JOBS 2, nice 19.

## Results

| Step | Result |
|---|---|
| 0. Data | **438 new ids**: B4b 429, P-B 090-099 9. **0 changed, 0 removed.** The new database.json only appends lines to ours, in two blocks. Every B4b card is a field-for-field reprint, and so are P-B 090-098. **P-B 099 Mega Garchomp ex** is the one new card: Dragon, 220 HP, Falling Edge 190, "Discard 2 random Energy from this Pokémon." That text is already mapped at `effect_mechanic_map.rs:178`. Before B4b, our three files were byte-identical to upstream's apart from line endings. |
| 1. Build | **PASS**: 577 s. |
| 2. Generator | **Reproduces** upstream's `card_ids.rs` and `database.rs`, layout aside (`gencmp.py`: SAME for both). |
| 2. Incremental maps | The attack map lists 0 new texts. The ability map lists 2: Pidgeot's and Swellow's "Once during your turn, you may switch out your opponent's Active [Basic] Pokémon to the Bench…". Both cards are already on main, and both texts are already mapped (`effect_ability_mechanic_map.rs:477`, `:491`). Those map entries write the text's non-breaking space as `\u{a0}`, and the incremental tool compares raw text, so it reports them falsely. The same happens on main. **No new card text.** |
| 3. Card status (`card_status --json`) | **46 of the 438 new ids are MissingTrainer**, across 22 Trainer names. The rest are Complete. See the list below. |
| 4. Suite | **2,150 passed, 2 failed.** Both failures are the procedure's own pins in `card_status_cli_test`: the card count (3,879, now 4,317) and "every card Complete or RulesUnverified" (the 46 above). Nothing else fails. |
| 5. Identity sample v main-4d48844 | **SAME**: the CLI k3/kp3/kog3/kta3/km3 runs (5 × 240) and the k3 table (14,000), 0 differing deals. Appending the data changes no game of the current decks. |

**MissingTrainer: B4b reprints whose card id has no dispatch arm in this fork** (22 names, 46 printings):
- Arven, Calem, Clemont, Copycat, Diantha, Electric Generator, Elesa, Field Blower, Flame Patch, Iris, Juliana;
- Korrina, Lisia, Lucky Ice Pop, May, Order Pad, Puppy-Loving Girl, Quick-Grow Extract, Serena, Skyla, Wallace, Wally.

The other 18 B4b Trainer names (36 printings: Tools, Stadiums, the Booster Energy Capsules and others) are already Complete. Upstream needs no arms at all since #395 (`f4cdba5`, Oct 9: Trainer logic keyed by the first printing of the effect text).

## What adopting the data pin would take
1. **Port #395, or add 46 id arms.** #395 is the fix for the cause and also covers later reprints. PLAN.md already pairs B4b with #395.
2. **Update the test pin** in `card_status_cli_test` (the count, 3,879 → 4,317). Its coverage assertion passes once step 1 is done. No other test fails.
3. **The `lib/` refresh** (procedure step 9):
   - `lib/deckgym-database.json` (an LF copy);
   - `card_canon` EXPECTED_IDS and SET_ORDER (`'B4b'` before `'P-A'`), and CANON_MAP rebuilt;
   - `deck_classifier` SET_ORDER `'B4b'`.

   The s216 QR catalog is refreshed in Pocket Deck Lab.
4. **The full acceptance:** the suite, and identity replays of the k3/kp3/kog3 and km3/kta3 tables. A full set of the k3, kp3, kog3, km3 and kta3 tables takes about 1.2 h at SCAN_THREADS 8.
5. **The release:** a release folder and manifest entry, and Dustin's word.
6. **C1 lands on top of the dual-type seam.** Its generator reads every #429 shape and refuses an unknown Pokémon field.

**Tools:** `lane_p.sh`. The comparisons use `replay3.py` (side p) and `gencmp.py`, both on the seam branch under `rl/results/dual_type_seam_2026-10-23/tools/`. Records are on the laptop in `/home/dacz8976/pincand_work/datapin/` and `games/p/`.
