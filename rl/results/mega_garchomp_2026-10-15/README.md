# Mega Garchomp ex into the engine (the cloud, Oct 15)

Asked by the coordinator (direct route, Oct 15): RUN5's B6, "Mega Garchomp ex is its own refresh".
- Branch `claude/mega-garchomp`, from main 36f4dd62.
- Not pinned, not on main: the laptop or the coordinator reviews it first.

## The card

**Source:** Dustin's in-game screenshot, Oct 15 (released that day).

**Mega Garchomp ex**, P-B 099:
- Stage 2, evolves from Gabite. Dragon. 220 HP. No Weakness. Retreat 2.
- **Falling Edge** [W][F][C], 190: "Discard 2 random Energy from this Pokémon."
- Mega Evolution ex: its knockout gives the opponent 3 points.
- Illus. PLANETA CG Works. Promo B, Double Rare (◊◊◊◊).

**The number:**
- A web search finds the official listing on pokemon-zone.com: "Mega Garchomp ex Double Rare - Promo B (PROMO-B) #99", in Promo Pack B
  Series Vol. 13. This matches our Sept 26 prep's P-B 099 (`../b4b_prep_2026-09-26/`).
- That page couldn't be opened from the cloud (the host doesn't resolve here), so only the number is confirmed from it. The stats and
  text are from Dustin's screenshot.
- The prep flagged a damage conflict: 180 on one Sept 26 card box, 190 on the spoiler. Dustin's screenshot says 190.

## How it was added

**No new mechanic.**
- The effect text is already mapped: `effect_mechanic_map.rs:178`, `SelfDiscardRandomEnergy { count: 2 }`. Giratina A2a 061 and
  Rayquaza B4 119 use it, and `damage_and_discard_random_energy` resolves it.
- **3 points:** the engine gives 3 to any Pokémon whose name starts with "Mega " (`models/card.rs`, `is_mega`, `get_knockout_points`).
- **Evolution:** follows the `evolves_from` name, so all three Gabite printings evolve into it.
- **Rare Candy:** its table is built from the database (`card_logic::can_rare_candy_evolve`), so Gible to Mega Garchomp ex needs
  nothing extra.

**Files changed:**
- `engine/database.json` and `lib/deckgym-database.json`: one entry each, after P-B 094, the last promo. The two hold the same text;
  the engine copy keeps its CRLF line endings (RUN5 B1).
- `engine/src/card_ids.rs` (+2 lines) and `engine/src/database.rs` (+26): regenerated with `card_enum_generator` (engine README,
  "Generating database.rs"), formatted, and stored with CRLF like the originals.
  - Before the change, the generator reproduced both files exactly from the old `database.json` (apart from line endings). So the
    diff is only the new card.
- `engine/tests/pokemon/mega_garchomp_ex_test.rs` (new) and its line in `engine/tests/pokemon.rs`.

## Tests

`engine/tests/pokemon/mega_garchomp_ex_test.rs`: 8 Game-level tests. They look the card up by its id, so before the card existed they
failed with "P-B 099 Mega Garchomp ex is not in the card database" instead of failing to compile (`tests_before.log`: 0 of 8).
After: 8 of 8 pass.

| Test | What it checks |
|---|---|
| `the_card_is_a_stage_2_dragon_mega_ex_with_220_hp` | name, stage 2, Dragon, 220 HP, no Ability, one attack |
| `falling_edge_costs_water_fighting_colorless` | the cost [W][F][C], the title, the effect text |
| `falling_edge_does_190` | 300 − 190 on a 300-HP defender |
| `falling_edge_discards_exactly_2_random_energy_from_itself` | over 64 seeds with 4 different Energy attached: always 2 stay and 2 go to the attacker's discard pile; nothing leaves the defender; each of the 4 types is discarded in some seed (it is random) |
| `with_fewer_than_2_energy_attached_it_discards_what_is_there` | 1 attached: it is discarded, the damage is still 190, nothing fails. In play the cost (3 Energy) makes this unreachable; it pins the effect's edge. |
| `its_knockout_gives_the_opponent_3_points` | a Mega Garchomp ex at 20 HP knocked out by Falling Edge gives 3 points |
| `retreat_costs_2_and_it_has_no_weakness` | 2 Colorless, Weakness none |
| `it_evolves_from_gabite_and_from_gible_with_rare_candy` | each Gabite (A2 122, A2a 046, B4a 053) evolves into it; Gible doesn't without Rare Candy; Rare Candy takes each Gible (A2 121, A2a 045, B4a 052) to it |

**The card in the tools:**
- `python3 lib/card.py garchomp` lists it:
  `Mega Garchomp ex  [P-B 099]  Dragon  Stage 2 (from Gabite)  HP 220  weak -  retreat 2` /
  `[WFC] Falling Edge 190 — Discard 2 random Energy from this Pokémon.`
- `lib/deck_check.py files`:
  - accepts a 20-card list with 2 copies: Dustin's `decks/dustin/08-garchomp-toolbox.txt` with its 2 Garchomp (B4a 054) replaced
    by 2 Mega Garchomp ex. The list is kept in scratch only.
  - refuses 3 copies ("3 copies of printed name Mega Garchomp ex").

## Identity

- **km3's self-check is unchanged:** `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1`.
  - The strength harness was built against this branch's engine with `rl/strength/build.sh`. The program sha256 is 00ed6594…, from
    the cloud build; the harness source is unchanged.
  - The run was the usual t-altaria v t-suicune, 12 games.
- **The engine's full suite:** see below.
- No existing deck carries the card, so no recorded game can change: the new entry only adds a card id, and nothing reads it unless a
  list names it.

**The full engine suite: running** (`cargo test --release --features test-utils`); the result will be added here.

## What a pin would need (RUN5's switch rules)

This branch is a candidate engine. The rules for a data refresh are RUN5's A5 and the B4b release notes (B1-B9); B6 makes this its
own refresh. Before the screen, the floor or any table could use it:
1. **Review** of this branch by the laptop or the coordinator: the card fields against the screenshot, the tests, the generated diff.
2. **A card pass** against a published card page (Limitless or the official site), field by field, when one can be read. Here only
   the number could be checked from outside the screenshot.
3. **The refresh's identity replays on the laptop:** bit-for-bit reproduction, on the new program, of:
   - the k3, kp3 and kog3 tables (14,000 games each);
   - kta3's and km3's recorded games (the Sept 30 switch's references);
   - the current pinned references of `rl/engine-2026-10-12/`;
   - and km3's self-check, as here.
   The full suite passes. Any mismatch stops and goes to Dustin.
4. **The release:**
   - a new `rl/engine-<date>/` folder with the program and its README;
   - hashes in `project_manifest.json`, with the 2026-10-12 program listed under the historical releases, hashes unchanged;
   - the engine line in `START_HERE.md` and `CLAUDE.md`.
   Then Dustin's word to switch, as for every pin so far.
5. **Out of scope until then:** no table or screen game uses the card, and no pilot preset is changed for it.
