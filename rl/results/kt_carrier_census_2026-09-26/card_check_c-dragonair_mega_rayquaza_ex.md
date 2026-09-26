# Card-text check: c-dragonair_mega_rayquaza_ex.txt (kt carrier census list)

Date: 2026-09-26. Deck file: `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` (Limitless archetype "Dragonair Mega Rayquaza ex"; thefossilman, 1st of 219, Umbreon99's Aura Sphere #4: $15 USD + Oak, 2026-09-11; provenance in `provenance/c-dragonair_mega_rayquaza_ex.json`).

How it was checked, the way the sibling files did it (`card_check_c-mega_lucario_ex_lucario.md`, after B2e's `rl/results/b2e_card_check_2026-09-26/card_check_arch_manectric.md`): for each of the 13 distinct cards, the engine's text came from `python lib/card.py "<SET> <NUMBER>"` (database `lib/deckgym-database.json`; the raw entry read for the Trainer subtype, `trainer_card_type`), and the Limitless text came from `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched with WebFetch on the same day. Compared: HP, type, stage and evolves-from, weakness, retreat cost, each attack's cost, damage and effect, ability name and text, Trainer subtype and text. Spelling and glyph differences (Pokémon/Pokemon, "-30"/"−30") are ignored.

Fetch note: WebFetch returned every page on this run (no refusals), so no page had to be read in the Browser pane. Two pages (Dratini, Mega Rayquaza ex) were fetched a second time with a narrower prompt because the first summary had folded the attack cost into the attack name; the second fetch printed the raw attack strings ("WL Ram 40", "RL Mega Burst 50x"). Every card was read from both sources; none is unverified.

Coverage flags came from `rl/engine-2026-09-25/goldfish --deck <file> --games 0 --panel decks/screen/opponents --coverage rl/results/kt_carrier_census_2026-09-26/coverage_c-dragonair_mega_rayquaza_ex.json` run in WSL (0 games played; goldfish sha256 318c82c8…be997, the hash in `rl/engine-2026-09-25/README.md`). The raw output is in `coverage_c-dragonair_mega_rayquaza_ex.json` next to this file.

## Summary

- Cards checked: 13 of 13 (all verified against Limitless).
- Mismatches: 2, both low severity. (1) Poké Ball wording: engine "a random Basic Pokémon", Limitless "1 random Basic Pokemon"; same meaning; the same item B2e refuted and the four sibling checks carried. (2) Skull Fossil subtype label: the engine database stores `trainer_card_type` "Fossil" (the engine's own category, `TrainerType::Fossil`, `engine/src/hooks/core.rs:28`) where Limitless prints "Trainer - Item"; the card text is the same (the engine's stored text runs the three sentences together without spaces after the periods, formatting only).
- High-severity mismatches: none. Every HP, type, stage, weakness, retreat cost, attack cost, damage figure, effect, ability and Trainer text matches.
- Coverage flags: 2 cards. Copycat is flagged "unpriced text rule" (reads the opponent's hand). Gouging Fire's Scorching Interruption is flagged "pays off on the opponent's turn" (its -30 to itself lasts through the opponent's next turn; this is exactly the group-3 switch-1 effect the census counts). No card is flagged for an engine limitation or as not implemented; all 13 report "Fully implemented".
- Note on Mega Rayquaza ex: Limitless prints the Mega Evolution ex rule box (3 points when Knocked Out) and "50x" for the damage. The database entry has no field for the rule box, but the engine applies it in code for any Pokémon whose name starts with "Mega " (`engine/src/models/card.rs`, `is_mega`; B2e README section 6), and it stores the integer 50 with the "50 damage for each Energy" sentence. Not counted as mismatches. The Limitless page lists it as "Pokémon - Basic" (a Basic in Pocket, not an evolution); the engine has stage 0. Match.
- Note on "Ancient": Professor Sada and Ancient Booster Energy Capsule act on Ancient Pokémon. The database entries carry no Ancient field; the engine keeps a name list (`engine/src/hooks/core.rs:31-47`, `ANCIENT_POKEMON_NAMES`, 11 names) and "Gouging Fire" is on it, so both Trainers can target Gouging Fire in the engine. Mega Rayquaza ex is not on the list. The Limitless pages read here print no Ancient marking for either Pokémon in what WebFetch returned, so this is a note, not a comparison.
- Damage notation: Limitless prints "50x" for Mega Rayquaza ex where the engine stores the integer and the effect sentence; the same convention the sibling checks accepted for "10+" and "90+". Formatting only.
- Dratini A1 183's only attack, Ram, costs [WL]; the list's declared Energy is Fire and Lightning, so in this list Dratini is an evolution base rather than an attacker. Both sources agree on the cost; noted as a fact about the list, not a mismatch.
- Untrusted-prone? The main attacker (Mega Rayquaza ex, Mega Burst) and the energy engine (Dragonair, Dragon's Blessing; Professor Sada; Rainbow Cave) carry no flag. The flags sit on Gouging Fire (the census card itself, whose defensive half k3 never searches) and Copycat, which is on both sides of many panel pairings. Gouging Fire is the list's second attacker (2 copies) and its Scorching Interruption is the attack the kt draft would price for the defender.

## Per-card table

| # | Card (id) | Field | Engine | Limitless | Result |
|---|-----------|-------|--------|-----------|--------|
| 1 | Dratini (A1 183) | Type / stage | Dragon, Basic (Stage 0) | Dragon, Basic | match |
|   |  | HP / weakness / retreat | 70 / none / 1 | 70 / none / 1 | match |
|   |  | Attack: Ram | [WL] 40, no effect | "WL Ram 40", no effect | match |
|   |  | Ability | none | none | match |
| 2 | Dragonair (B4 117) | Type / stage | Dragon, Stage 1 from Dratini | Dragon, Stage 1, evolves from Dratini | match |
|   |  | HP / weakness / retreat | 80 / none / 2 | 80 / none / 2 | match |
|   |  | Ability: Dragon's Blessing | "Once during your turn, if this Pokémon is on your Bench, you may attach an Energy from your discard pile to your Active [N] Pokémon." | "Once during your turn, if this Pokémon is on your Bench, you may attach an Energy from your discard pile to your Active [N] Pokémon." | match |
|   |  | Attack: Draconic Whip | [CC] 40, no effect | [CC] 40, no effect | match |
| 3 | Gouging Fire (B3a 054) | Type / stage | Dragon, Basic (Stage 0) | Dragon, Basic | match |
|   |  | HP / weakness / retreat | 110 / none / 2 | 110 / none / 2 | match |
|   |  | Attack: Scorching Interruption | [RLC] 100. "Discard 2 Energy from this Pokémon. During your opponent's next turn, this Pokémon takes -30 damage from attacks." | [RLC] 100. "Discard 2 Energy from this Pokémon. During your opponent's next turn, this Pokémon takes −30 damage from attacks." | match |
|   |  | Ability | none | none | match |
| 4 | Mega Rayquaza ex (B4 120) | Type / stage | Dragon, Basic (Stage 0) | Dragon, Basic | match |
|   |  | HP / weakness / retreat | 180 / none / 1 | 180 / none / 1 | match |
|   |  | Attack: Mega Burst | [RL] 50. "Discard all [R] and [L] Energy from this Pokémon, and this attack does 50 damage for each Energy you discarded in this way." | [RL] 50x. "Discard all [R] and [L] Energy from this Pokémon, and this attack does 50 damage for each Energy you discarded in this way." | match |
|   |  | Ability | none | none (rule box only: Mega Evolution ex, 3 points when Knocked Out) | match; rule handled by engine code, see note |
| 5 | Professor's Research (P-A 007) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Draw 2 cards." | "Draw 2 cards." | match |
| 6 | Copycat (B1 225) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | match |
| 7 | Cyrus (A2 150) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | match |
| 8 | Professor Sada (B3a 072) | Trainer type | Supporter | Trainer - Supporter | match |
|   |  | Text | "Attach 3 different types of Energy from your discard pile to your Ancient Pokémon in any way you like." | "Attach 3 different types of Energy from your discard pile to your Ancient Pokémon in any way you like." | match |
| 9 | Poké Ball (P-A 005) | Trainer type | Item | Trainer - Item | match |
|   |  | Text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | MISMATCH, low (wording "a" vs "1"; same meaning; B2e refuted the same item) |
| 10 | Skull Fossil (A2 144) | Trainer type | Fossil (engine's own category for fossil Items) | Trainer - Item | MISMATCH, low (label only; the engine plays it as the text says) |
|   |  | Text | "Play this card as if it were a 40-HP Basic [C] Pokémon.At any time during your turn, you may discard this card from play.This card can't retreat." | "Play this card as if it were a 40-HP Basic [C] Pokémon. At any time during your turn, you may discard this card from play. This card can't retreat." | match (missing spaces after periods in the stored text; formatting only) |
| 11 | Ancient Booster Energy Capsule (B3a 069) | Trainer type | Tool | Trainer - Tool | match |
|   |  | Text | "The Ancient Pokémon this card is attached to gets +40 HP." | "The Ancient Pokémon this card is attached to gets +40 HP." | match |
| 12 | Small Balloon (B3b 064) | Trainer type | Tool | Trainer - Tool | match |
|   |  | Text | "The Retreat Cost of the Basic Pokémon this card is attached to is 1 less." | "The Retreat Cost of the Basic Pokémon this card is attached to is 1 less." | match |
| 13 | Rainbow Cave (B4 155) | Trainer type | Stadium | Trainer - Stadium | match |
|   |  | Text | "Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced." | "Once during each player's turn, that player may discard the Energy that has been generated in their Energy Zone. If they do, the next Energy is produced." | match |

## Coverage flags (goldfish --coverage, 0 games)

| Card (id) | Engine status | Limitations | Unpriced text rule | Printed-damage estimator | Pays off on opponent's turn |
|-----------|---------------|-------------|--------------------|--------------------------|-----------------------------|
| Dratini (A1 183) | Fully implemented | none | - | - | - |
| Dragonair (B4 117) | Fully implemented | none | - | - | - |
| Gouging Fire (B3a 054) | Fully implemented | none | - | - | FLAGGED ("attack Scorching Interruption") |
| Mega Rayquaza ex (B4 120) | Fully implemented | none | - | - | - |
| Professor's Research (P-A 007) | Fully implemented | none | - | - | - |
| Copycat (B1 225) | Fully implemented | none | FLAGGED ("its effect": reads the opponent's hand) | - | - |
| Cyrus (A2 150) | Fully implemented | none | - | - | - |
| Professor Sada (B3a 072) | Fully implemented | none | - | - | - |
| Poké Ball (P-A 005) | Fully implemented | none | - | - | - |
| Skull Fossil (A2 144) | Fully implemented | none | - | - | - |
| Ancient Booster Energy Capsule (B3a 069) | Fully implemented | none | - | - | - |
| Small Balloon (B3b 064) | Fully implemented | none | - | - | - |
| Rainbow Cave (B4 155) | Fully implemented | none | - | - | - |

Flag classes used by the tool: unpriced text rule (text mentions the opponent's hand or deck, which k3 does not price), printed-damage estimator (a damage-changing attack effect the estimator prices at printed damage), pays off on the opponent's turn (k3 never searches it), engine limitation (from `implementation_limitations`), not implemented (`engine_complete` false). Two flags fired: Copycat (unpriced), Gouging Fire (opponent's turn). Mega Rayquaza ex's Mega Burst (damage scales with discarded Energy) is not flagged by the estimator class.

Census note: the census card in this list is Gouging Fire B3a 054, 2 copies (group 3 in `cards.md`, "Pokémon whose own attack cuts damage to itself next turn", engine `CardEffect::ReducedDamage` 30 after discarding 2 Energy; switch-1 relevant). This is the first of the census's representative lists to carry a switch-1 (groups 1 to 3) card; the four earlier lists carried only group-4 cards (Protective Poncho or Rocky Helmet). The list carries no Protective Poncho and no Rocky Helmet.

## Unverified

None. All 13 cards were read from both sources.
