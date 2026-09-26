# Card-text check: arch:hoopa_absol (Plan B2e)

Date: Sept 26, 2026. Deck file: `rl/results/b2e_card_check_2026-09-26/decks/h-hoopa_absol.txt` (20 cards, 14 distinct; Energy: Darkness).

**Sources.** Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`). `card.py` prints Trainers as just "Trainer", so the Trainer subtype (Supporter / Item / Tool / Stadium) in the tables below is the `trainer_card_type` field of the same database entry. Limitless: `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>`, fetched Sept 26, 2026. Coverage: `rl/engine-2026-09-25/goldfish --deck <file> --panel decks/screen/opponents --games 0 --coverage <out>` run in WSL from the repo root (goldfish sha256 `318c82c8…`, the official one from `rl/engine-2026-09-25/README.md`); it played 0 games and wrote `coverage_arch_hoopa_absol.json` beside this file.

## Summary

- **14 of 14 cards verified against Limitless.** No high-severity mismatch (HP, type, stage, weakness, retreat, attack costs, damage, ability and effect meaning all agree).
- **1 low-severity (wording) mismatch:** Poké Ball P-A 005 — engine says "Put **a** random Basic Pokémon…", Limitless prints "Put **1** random Basic Pokemon…". Same meaning.
- **Coverage flags (2 cards):** Mega Absol ex B1 151 (attack Darkness Claw) and Copycat B1 225 (its effect) are both **unpriced text rule** flags — their text reads the opponent's hand, which the k3 bot does not search. Every card in the list is "Fully implemented" in the engine; no engine-limitation, not-implemented, printed-damage-estimator or pays-off-on-the-opponent's-turn flags.
- **Unverified:** none.

## Pokémon (3 distinct)

### Hoopa ex — B4 103 (x2)

| Field | Engine (card.py) | Limitless | Match |
|---|---|---|---|
| HP | 150 | 150 | yes |
| Type | Darkness | Darkness | yes |
| Stage / evolves from | Stage 0 (Basic), none | Basic Pokémon | yes |
| Weakness | Grass | Grass | yes |
| Retreat cost | 2 | 2 | yes |
| Ability | none | none | yes |
| Attack 1 | [D] Shadow Bullet 30 — "This attack also does 20 damage to 1 of your opponent's Benched Pokémon." | (D) Shadow Bullet 30 — "This attack also does 20 damage to 1 of your opponent's Benched Pokémon." | yes |
| Attack 2 | [DDC] Dynamite Punch 100 — "This Pokémon also does 20 damage to itself." | (DDC) Dynamite Punch 100 — "This Pokémon also does 20 damage to itself." | yes |
| Rule box | not a database field; the engine gives 2 points for a Pokémon ex (`engine/src/models/card.rs`) | "When your Pokémon ex is Knocked Out, your opponent gets 2 points." | yes |

### Mega Absol ex — B1 151 (x1)

| Field | Engine (card.py) | Limitless | Match |
|---|---|---|---|
| HP | 170 | 170 | yes |
| Type | Darkness | Darkness | yes |
| Stage / evolves from | Stage 0 (Basic), none | Basic Pokémon | yes |
| Weakness | Grass | Grass | yes |
| Retreat cost | 1 | 1 | yes |
| Ability | none | none | yes |
| Attack | [DD] Darkness Claw 80 — "Your opponent reveals their hand. Choose a Supporter card you find there and discard it." | (DD) Darkness Claw 80 — "Your opponent reveals their hand. Choose a Supporter card you find there and discard it." | yes |
| Rule box | not a database field; the engine gives 3 points for a name starting with "Mega " (`engine/src/models/card.rs`, `is_mega`) | "When your Mega Evolution Pokémon ex is Knocked Out, your opponent gets 3 points." | yes |

### Darkrai ex — A2 110 (x1)

| Field | Engine (card.py) | Limitless | Match |
|---|---|---|---|
| HP | 140 | 140 | yes |
| Type | Darkness | Darkness | yes |
| Stage / evolves from | Stage 0 (Basic), none | Basic Pokémon | yes |
| Weakness | Grass | Grass | yes |
| Retreat cost | 2 | 2 | yes |
| Ability | Nightmare Aura: "Whenever you attach a [D] Energy from your Energy Zone to this Pokémon, do 20 damage to your opponent's Active Pokémon." | Nightmare Aura: "Whenever you attach a [D] Energy from your Energy Zone to this Pokémon, do 20 damage to your opponent's Active Pokémon." | yes |
| Attack | [DDC] Dark Prism 80, no effect | (DDC) Dark Prism 80, no effect | yes |
| Rule box | not a database field; engine gives 2 points for a Pokémon ex | "When your Pokémon ex is Knocked Out, your opponent gets 2 points." | yes |

## Trainers (11 distinct)

| Card | Count | Engine type (database `trainer_card_type`) | Limitless type | Engine text | Limitless text | Match |
|---|---|---|---|---|---|---|
| Professor's Research P-A 007 | 2 | Supporter | Trainer - Supporter | "Draw 2 cards." | "Draw 2 cards." | yes |
| Cyrus A2 150 | 2 | Supporter | Trainer - Supporter | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | same | yes |
| Copycat B1 225 | 1 | Supporter | Trainer - Supporter | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same | yes |
| Pokémon Center Lady A2b 070 | 1 | Supporter | Trainer - Supporter | "Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions." | same | yes |
| Poké Ball P-A 005 | 2 | Item | Trainer - Item | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | **low: wording ("a" vs "1"); same meaning** |
| Lucky Ice Pop B2 145 | 2 | Item | Trainer - Item | "Heal 20 damage from your Active Pokémon. If you healed any damage in this way, flip a coin. If heads, put this Lucky Ice Pop into your hand instead of the discard pile." | same | yes |
| X Speed P-A 002 | 1 | Item | Trainer - Item | "During this turn, the Retreat Cost of your Active Pokémon is 1 less." | same | yes |
| Repel A3a 064 | 1 | Item | Trainer - Item | "Switch out your opponent's Active Basic Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | same | yes |
| Field Blower B3 147 | 1 | Item | Trainer - Item | "Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play." | same | yes |
| Deceptive Needle B4 148 | 2 | Tool | Trainer - Tool | "At the end of your turn, if the [D] Pokémon this card is attached to is in the Active Spot, do 10 damage to your opponent's Active Pokémon." | same | yes |
| Starting Plains B2 154 | 1 | Stadium | Trainer - Stadium | "Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP." | same | yes |

"same" means identical apart from spelling and punctuation (Limitless drops the accent in "Pokémon" on some pages).

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball P-A 005 | effect text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | low (wording) |

## Coverage flags (goldfish --coverage, 0 games)

| Card | Flag class | Detail | Engine status |
|---|---|---|---|
| Mega Absol ex B1 151 | unpriced text rule | attack Darkness Claw (reads the opponent's hand) | Fully implemented, no limitations |
| Copycat B1 225 | unpriced text rule | its effect (reads the opponent's hand) | Fully implemented, no limitations |

The other 12 cards have no flag of any class. For all 14: `engine_status` = "Fully implemented", `engine_complete` = true, `limitations` = [], `estimator_printed_damage` = [], `pays_off_on_opponent_turn` = []. Note that Deceptive Needle and Darkrai ex's Nightmare Aura pay off on the list's own turn (end of your turn / your own energy attach), so they correctly carry no "opponent's turn" flag.

## Unverified

None. Every card's Limitless page was fetched by its exact set and number.
