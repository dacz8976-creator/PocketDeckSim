# Gauntlet decks (Sept 26, 2026)

The lists Dustin approved for growing the test gauntlet (`rl/results/gauntlet_proposal_2026-09-26/README.md`):
three new decks (section 1) and the variation check's lists (section 6, Proposal B). Every list is taken from the
proposal's `gauntlet.json` (the **development half** of the Limitless pull only: 63 events, 4,722 decklists,
Aug 26 to Sept 24) and was checked against it card for card by `rl/results/gauntlet_runs_2026-09-26/make_decks.py`,
which wrote these files. The runs and their reading are in `rl/results/gauntlet_runs_2026-09-26/`.

**The accuracy scoreboard is the 45 cells** (the 28 table cells, frozen, plus the 17 new cells of Rayquaza and
Altaria/Greninja). Gauntlet decks past about 10 to 11 are for brew realism and coverage, **not an accuracy claim**.

## The three new decks

| File | Limitless deck (exact name) | Energy | Row | Where the list comes from |
|---|---|---|---|---|
| `g-mega_scizor_revavroom.txt` | Mega Scizor ex Revavroom | Metal | **COVERAGE only**, never a scoreboard row | `gauntlet.json` → `additions[0].representative_list`. The deck has only 9 lists (usage rank 64) and its modal list is a two-way tie at 2 copies, so the proposal used "core plus the most common flex cards". That build equals a real list registered by two different players: lockpick04 (219 players, Sept 11, 3-4) and pattyd (68 players, Sept 23, 25th, 3-4). It is the most-used deck that runs Metal alone, added so the gauntlet has every Energy type. Its real cells against the panel hold 0 to 13 matches each, so nothing real can check it (Dustin, Sept 26): its panel score and misses are reported, and kept out of every accuracy total. |
| `g-dragonair_mega_rayquaza.txt` | Dragonair Mega Rayquaza ex | Fire, Lightning (all 101 lists that state an Energy) | **Scoreboard** | `gauntlet.json` → `variation_growth_candidates` → `Dragonair Mega Rayquaza ex` → `modal_list`: the most common exact list, 19 of 143 lists (13%). Usage rank 7, 15 top-8 finishes. The kt census file `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` stays as the census's own history: it is 4 cards off this list and carries Skull Fossil, which 2% of lists run, so the gauntlet uses the most common list instead. |
| `g-mega_altaria_greninja.txt` | Mega Altaria ex Greninja | Psychic (76 of 76 stating lists) | **Scoreboard** | `gauntlet.json` → `variation_growth_candidates` → `Mega Altaria ex Greninja` → `modal_list`: the most common exact list, 40 of 125 lists (32%). Usage rank 10, 18 top-8 finishes. No list of this deck was in the repo before. |

Rayquaza and Altaria/Greninja are scoreboard additions (Dustin, Sept 26): with their 8 panel cells each and the one
cell between them, the 28-cell scoreboard becomes 45 cells.

**The Scizor list is not run on the current (pre-repair) engine.** The card check found that Mega Scizor ex's Bullet
Slugger gets its +50 in a case where Pocket gives none (after the opponent's end-of-turn Knock Out, through the
promotion-timing bug). That changes games, and all three skeptics upheld it (`card_check.md`, S1). The file stays here
for the re-check after the engine repair.

## The variation check's lists (Proposal B)

Four decks vary the most among the most-used (usage rank 15 or better, most common list under 20% of lists):
Lucario, Suicune, Weezing and Charizard Y. Each gets three versions, played on its main list's own deals.

| File | Main list it varies | What it is | Change from the main list |
|---|---|---|---|
| `v-lucario_2.txt` | `decks/screen/opponents/t-lucario.txt` | Second list: the 2nd most common exact list, 20 of 398 (5%) (`gauntlet.json` → `variation` → `Mega Lucario ex Lucario` → `tests[0].twin`) | 2 Riolu A2 091 and Lucky Ice Pop for 2 Riolu B3 079 and Protective Poncho |
| `v-lucario_swap1.txt` | `t-lucario.txt` | Swap 1 (`proposal_B_sensitivity`) | Lucky Ice Pop (in 57% of lists) for Protective Poncho |
| `v-lucario_swap2.txt` | `t-lucario.txt` | Swap 2 | Sabrina (21%) for Pokémon Center Lady |
| `v-suicune_2.txt` | `decks/screen/opponents/t-suicune.txt` | Second list: the most common exact list, 18 of 200 (9%) | 2nd Giant Cape, Mars and a 2nd Frigibax B2a 034 for Team Rocket's Boss, Field Blower and Frigibax P-B 037 |
| `v-suicune_swap1.txt` | `t-suicune.txt` | Swap 1 | 2nd Giant Cape (72%) for Team Rocket's Boss |
| `v-suicune_swap2.txt` | `t-suicune.txt` | Swap 2 | Mars (31%) for Field Blower |
| `v-weezing_2.txt` | `decks/screen/opponents/t-weezing.txt` | Second list: the most common exact list, 24 of 152 (16%) | Mega Absol ex, Pokémon Center Lady and 2 Lucky Ice Pop for Darkrai ex, Mars, the 2nd Copycat and Field Blower |
| `v-weezing_swap1.txt` | `t-weezing.txt` | Swap 1 | Lucky Ice Pop (73%) for Mars |
| `v-weezing_swap2.txt` | `t-weezing.txt` | Swap 2 | Pokémon Center Lady (60%) for the 2nd Copycat |
| (not in this folder) `decks/screen/panel_ladder_2026-09-26/l-charizardy.txt` | `rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt` | Charizard Y's second list: the existing ladder-panel list, 4 copies (the proposal's section 6 table) | Protective Poncho and a 2nd Rainbow Cave for Pokémon Center Lady and Lucky Ice Pop |
| `v-charizardy_swap1.txt` | `h-charizardy_entei.txt` | Swap 1 | 2nd Rainbow Cave (42%) for the 2nd Copycat |
| `v-charizardy_swap2.txt` | `h-charizardy_entei.txt` | Swap 2 | Sabrina (26%) for Lucky Ice Pop |

Each swap puts in the most common Trainer the main list lacks, in place of its least common Trainer choice (the
proposal's rule; the pairs are the proposal's own).

**One difference inside the proposal, flagged.** For Charizard Y, the proposal's README (section 6) names
`l-charizardy.txt` as the second list, and so did the task; that is what is used. But `gauntlet.json` →
`proposal_B_sensitivity` → Charizard Y → `twin` holds a different list: 5 copies, with Charizard B1a 013 and a 2nd
Rainbow Cave for the 2nd Copycat and Lucky Ice Pop. `make_decks.py` prints both. It is not used.

**How the version files are laid out.** Each version is its main file with the changed lines replaced in place: a
card that comes in sits on the line of the card it replaces. The engine builds the deck in file order and shuffles
positions, so on the same seed the new card is dealt exactly where the old one would have been, which keeps the
paired comparison as tight as it can be. A name can therefore appear on two lines (for example Giant Cape in
`v-suicune_swap1.txt`); the engine and `lib/deck_check.py` add them up. The `t-` files hold the table's
`decks/research` cards in the same order, card for card (checked by `make_decks.py`).

## Checks

- **`python3 lib/deck_check.py files`** on all 14 files here and `l-charizardy.txt`: "decks clean", exit 0
  (`deck_check.txt`). No warnings.
- **`goldfish --coverage` at 0 games** (`rl/engine-2026-09-25/goldfish --deck <file> --games 0 --panel
  decks/screen/opponents --coverage coverage/coverage_<name>.json`, the official binary, sha256 318c82c8…e997, no
  build). Every card in all 14 files reports "Fully implemented", with no engine limitation. The bot's pricing flags
  (reported, as for B2e; they apply to k3 and kp3 alike except the opponent's-hand ones, which kp3 prices):
  - Rayquaza: Gouging Fire's Scorching Interruption (pays off on the opponent's turn); Copycat (unpriced text).
  - Altaria/Greninja: Bonsly's Teary Attack (pays off on the opponent's turn); Copycat.
  - Scizor: Mega Scizor ex's Bullet Slugger (the +50 when it moved from the Bench is priced at printed damage),
    Metal Core Barrier (pays off on the opponent's turn); Copycat.
  - The versions add nothing new beyond cards already flagged in their main lists (Mars, Team Rocket's Boss, Mega
    Absol ex's Darkness Claw, Weezing ex's Boiler Smog: unpriced opponent's-hand text; Frigibax P-B 037's Stiffen:
    opponent's turn; Riolu B3 079's Fighting Fist: printed damage).
- **The card check** (code reading, every clause of every card not checked before): `card_check.md`.
