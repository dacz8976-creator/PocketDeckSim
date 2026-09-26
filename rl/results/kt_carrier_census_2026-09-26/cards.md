# kt carrier census, step 1: the cards the kt candidate prices (settled)

Written Sept 26, 2026 by the census subagent; settled the same day after the skeptic pass (`cards_skeptic.md`), see the section 'Disputed points and how they were settled' at the end. This file REPORTS; it decides nothing and changes no rule. Engine read at main 4924008 (working tree, Sept 26, 2026). Every card text below was printed by `python lib/card.py` (`--exact "<name>"` in the first pass, `"<name>"` in the adjudication; lib/deckgym-database.json); nothing is from memory. Deck carriers were found by matching the printing id in `decks/dustin/*.txt` (15 files) and `decks/brews/*.txt` (13 files), lines `<count> <Name> <SET> <NUM>`. Companion file: `cards.json` (same content, machine-readable; this file is generated from it).

## What the candidate prices, in plain words

The kt draft (Fable's proposed registration in `rl/results/fable_reviews_2026-09-26/kt_spec_review.md`) prices a defender's temporary damage cuts through one engine hook. The engine has three kinds of finite cut that hook reads, and the reserve route's clause (d) needs a non-Dustin Limitless top-30 archetype that carries at least one card from groups 1 to 3. One more temporary defensive effect goes through the same attack route, Steelix's Metal Defender (`CardEffect::NoWeakness`): it removes the Weakness stage instead of subtracting an amount, the hook cannot see it, and it sits in group 4.

1. **Trainer turn effects** (5 cards, 9 printings): Jasmine, Cheren, Blue, Beast Wall (`TurnEffect::ReducedDamageForTarget`) and Adaman (`TurnEffect::ReducedDamageForType`). All are registered for this turn and the opponent's next turn only.
2. **Tools that cut damage** (3 cards, 4 printings): Heavy Helmet and Steel Apron (permanent, in `persistent_defender_damage`) and Metal Core Barrier (temporary: the engine discards it at the end of the opponent's turn whether or not it was hit).
3. **Pokémon whose own attack cuts damage to itself next turn** (25 cards, 42 printings): every attack text the engine maps to `CardEffect::ReducedDamage` or `ReducedDamageFromEx` on the attacker. No Ability maps to either effect, so the 'ability self-reduction' list is empty; the Abilities that come closest (Samurott's Stance, Garchomp's Mach Stealth) are full preventions and sit in group 4.
4. **Considered and left out** of the switch-1 set: Protective Poncho (kt prices it at 0); the three inputs of `get_counterattack_damage` that kt switch 3 prices (Rocky Helmet, the five `CardEffect::Counterattack` attacks, the six `CounterattackDamage` Abilities: damage back, not a cut); Steelix's Metal Defender (`NoWeakness`); Poison Barb (dropped); Clear Veil; Hala; the coin-flip and threshold full preventions; the persistent Ability reductions; and the Growl-type cuts stored on the opponent's attacker.

**Dustin's decks that carry a group 1 to 3 card** (by printing id): deck 07 (Jasmine, Steel Apron, Metal Core Barrier, Skarmory ex), deck 05 (Cheren), decks 01 and 03 (Heavy Helmet), deck 11 (Archaludon B4a 056, Protect Charge). No brew carries one. Group 4 carriers: deck 05 and brew-06b (Protective Poncho); decks 06, brew-03a, brew-06, brew-06b (Rocky Helmet); brew-07 and brew-09 (Mega Sableye ex B3b 041, Cursed Jewel: switch 3, not switch 1); deck 10 and brew-03a (Poison Barb); deck 08 (Garchomp B4a 054, Mach Stealth); deck 15 (Oricorio A3 066, Safeguard). No Dustin file carries Steelix.

## Group 1: Trainer turn effects (kind `trainer_turn_effect`)

Shared mechanics: engine/src/state/mod.rs:1063-1078 add_turn_effect(effect, duration=1) registers the effect for turns t and t+1 (this turn and the opponent's next); engine/src/hooks/core.rs:1189-1227 get_turn_effect_damage_reduction sums ReducedDamageForType / ReducedDamageForTarget for the defending player (scope at 1230-1236, only_from_ex at 1219); summed into the finite reductions at core.rs:1370-1377 and subtracted after Weakness at core.rs:1883-1885; not in persistent_defender_damage (doc at core.rs:1577-1580).

### Jasmine  [A4 160, A4 200]  (Supporter)
- Text (card.py): During your opponent's next turn, all of your Steelix and Skarmory ex take -50 damage from attacks from your opponent's Pokémon.
- Engine: TurnEffect::ReducedDamageForTarget{amount:50, scope:NamedPokemon[Steelix, Skarmory ex], only_from_ex:false}
- Evidence: engine/src/actions/apply_trainer_action.rs:177 (dispatch), 1055-1060 jasmine_effect -> 1021-1037 add_damage_reduction_for_next_turn (add_turn_effect(ReducedDamageForTarget, 1)); playable via move_generation_trainer.rs:163; engine/src/state/mod.rs:1063-1078 add_turn_effect(effect, duration=1) registers the effect for turns t and t+1 (this turn and the opponent's next); engine/src/hooks/core.rs:1189-1227 get_turn_effect_damage_reduction sums ReducedDamageForType / ReducedDamageForTarget for the defending player (scope at 1230-1236, only_from_ex at 1219); summed into the finite reductions at core.rs:1370-1377 and subtracted after Weakness at core.rs:1883-1885; not in persistent_defender_damage (doc at core.rs:1577-1580)
- In Dustin's files: decks/dustin/07-skarmory-stall.txt (2 Jasmine A4 160)

### Cheren  [B3 151, B3 192]  (Supporter)
- Text (card.py): During your opponent's next turn, all of your Watchog and Stoutland take -100 damage from attacks from your opponent's Pokémon ex.
- Engine: TurnEffect::ReducedDamageForTarget{amount:100, scope:NamedPokemon[Watchog, Stoutland], only_from_ex:true}
- Evidence: engine/src/actions/apply_trainer_action.rs:178 (dispatch), 1062-1067 cheren_effect (only_from_ex = true) -> 1021-1037; move_generation_trainer.rs:164; engine/src/state/mod.rs:1063-1078 add_turn_effect(effect, duration=1) registers the effect for turns t and t+1 (this turn and the opponent's next); engine/src/hooks/core.rs:1189-1227 get_turn_effect_damage_reduction sums ReducedDamageForType / ReducedDamageForTarget for the defending player (scope at 1230-1236, only_from_ex at 1219); summed into the finite reductions at core.rs:1370-1377 and subtracted after Weakness at core.rs:1883-1885; not in persistent_defender_damage (doc at core.rs:1577-1580)
- In Dustin's files: decks/dustin/05-indeedee-stoutland.txt (1 Cheren B3 151)

### Blue  [A1a 067, A1a 081]  (Supporter)
- Text (card.py): During your opponent's next turn, all of your Pokémon take -10 damage from attacks from your opponent's Pokémon.
- Engine: TurnEffect::ReducedDamageForTarget{amount:10, scope:AllPokemon, only_from_ex:false}
- Evidence: engine/src/actions/apply_trainer_action.rs:176 (dispatch), 1043-1053 blue_effect -> 1021-1037; move_generation_trainer.rs:162; engine/src/state/mod.rs:1063-1078 add_turn_effect(effect, duration=1) registers the effect for turns t and t+1 (this turn and the opponent's next); engine/src/hooks/core.rs:1189-1227 get_turn_effect_damage_reduction sums ReducedDamageForType / ReducedDamageForTarget for the defending player (scope at 1230-1236, only_from_ex at 1219); summed into the finite reductions at core.rs:1370-1377 and subtracted after Weakness at core.rs:1883-1885; not in persistent_defender_damage (doc at core.rs:1577-1580)
- In Dustin's files: none

### Beast Wall  [A3a 063]  (Item)
- Text (card.py): You can use this card only if your opponent hasn't gotten any points.During your opponent's next turn, all of your Ultra Beasts take -20 damage from attacks from your opponent's Pokémon.
- Engine: TurnEffect::ReducedDamageForTarget{amount:20, scope:UltraBeasts, only_from_ex:false}
- Evidence: engine/src/actions/apply_trainer_action.rs:179 (dispatch), 1069-1078 beast_wall_effect -> 1021-1037; play gate can_play_beast_wall at move_generation_trainer.rs:165; scope via is_ultra_beast at core.rs:1234; engine/src/state/mod.rs:1063-1078 add_turn_effect(effect, duration=1) registers the effect for turns t and t+1 (this turn and the opponent's next); engine/src/hooks/core.rs:1189-1227 get_turn_effect_damage_reduction sums ReducedDamageForType / ReducedDamageForTarget for the defending player (scope at 1230-1236, only_from_ex at 1219); summed into the finite reductions at core.rs:1370-1377 and subtracted after Weakness at core.rs:1883-1885; not in persistent_defender_damage (doc at core.rs:1577-1580)
- In Dustin's files: none

### Adaman  [A2a 075, A2a 090]  (Supporter)
- Text (card.py): During your opponent's next turn, all of your [M] Pokémon take -20 damage from attacks from your opponent's Pokémon.
- Engine: TurnEffect::ReducedDamageForType{amount:20, energy_type:Metal, player}
- Evidence: engine/src/actions/apply_trainer_action.rs:251 (dispatch), 934-944 adaman_effect (add_turn_effect(ReducedDamageForType, 1)); read at core.rs:1206-1212 (target's energy types contain Metal); engine/src/state/mod.rs:1063-1078 add_turn_effect(effect, duration=1) registers the effect for turns t and t+1 (this turn and the opponent's next); engine/src/hooks/core.rs:1189-1227 get_turn_effect_damage_reduction sums ReducedDamageForType / ReducedDamageForTarget for the defending player (scope at 1230-1236, only_from_ex at 1219); summed into the finite reductions at core.rs:1370-1377 and subtracted after Weakness at core.rs:1883-1885; not in persistent_defender_damage (doc at core.rs:1577-1580)
- In Dustin's files: none

## Group 2: Tools that reduce damage taken (kind `tool_reduction`)

### Heavy Helmet  [B1 219]  (Tool)
- Text (card.py): If the Pokémon this card is attached to has a Retreat Cost of 3 or more, it takes -20 damage from attacks from your opponent's Pokémon.
- Engine: heavy_helmet_reduction: 20 x tool_count when the holder's PRINTED retreat_cost.len() >= 3 (rules/09 has the current-cost fix queued); active attacks from the opponent only; permanent (in persistent_defender_damage)
- Evidence: engine/src/hooks/core.rs:687-713 (get_heavy_helmet_reduction / heavy_helmet_reduction), summed at 1331-1336, subtracted after Weakness at 1883-1885; persistent_defender_damage 1614; identity text engine/src/tools.rs:53-54
- In Dustin's files: decks/dustin/01-muk-glimmora-kingambit-regigigas.txt (1 Heavy Helmet B1 219); decks/dustin/03-wailord-indeedee-wall.txt (2 Heavy Helmet B1 219)

### Steel Apron  [A4 153]  (Tool)
- Text (card.py): The [M] Pokémon this card is attached to takes -10 damage from attacks from your opponent's Pokémon, recovers from all Special Conditions, and can't be affected by any Special Conditions.
- Engine: steel_apron_reduction: 10 x tool_count when the holder is a [M] Pokémon (state.pokemon_is_type Metal); opponent's active attacks only; permanent (in persistent_defender_damage)
- Evidence: engine/src/hooks/core.rs:737-762 (get_steel_apron_reduction / steel_apron_reduction), summed at 1342-1347; persistent_defender_damage 1615; tools.rs:51-52
- In Dustin's files: decks/dustin/07-skarmory-stall.txt (1 Steel Apron A4 153)

### Metal Core Barrier  [B2 148, B2b 117]  (Tool)
- Text (card.py): If this card is attached to 1 of your Pokémon, discard it at the end of your opponent's turn.The [M] Pokémon this card is attached to takes -50 damage from attacks from your opponent's Pokémon.
- Engine: get_metal_core_barrier_reduction: 50 x tool_count when the holder is [M]; active attacks only; TEMPORARY: discarded at the end of the opponent's turn whether hit or not; deliberately left out of persistent_defender_damage
- Evidence: engine/src/hooks/core.rs:715-735 (reduction), summed at 1337-1341; discard at core.rs:504-519 (end of the tool owner's opponent's turn); excluded from persistent_defender_damage by its doc at 1577-1580; tools.rs:57-58
- In Dustin's files: decks/dustin/07-skarmory-stall.txt (2 Metal Core Barrier B2 148)

## Group 3: Pokémon whose own attack registers a cut on itself for the opponent's next turn (kind `attack_self_reduction`)

Shared mechanics: engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580). Standard entries: engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)).

Found by matching, in lib/deckgym-database.json, the exact attack texts that effect_mechanic_map.rs maps to ReducedDamage/ReducedDamageFromEx (lines 146-153, 602-628, 2456-2466, 2554-2562, 2604-2612, 3387-3394); a wider regex scan of every attack text for 'takes -N damage' found no unmapped card, so this list is the engine's whole set: 25 cards, 42 printings (re-counted in the adjudication).

### Mr. Mime  [A1 126]  (Pokémon)
- Attack: [PC] Barrier Attack 30; card: Psychic Basic HP 80
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Drifloon  [A2 073, A2 165]  (Pokémon)
- Attack: [P] Expand 10; card: Psychic Basic HP 50
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Bronzong  [A2 117]  (Pokémon)
- Attack: [MMC] Guard Press 60; card: Metal Stage 1 HP 120
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Probopass ex  [A2a 057, A2a 085, A2a 094, A4b 253]  (Pokémon)
- Attack: [MMC] Defensive Unit 90; card: Metal Stage 1 HP 160
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Cloyster  [A3 043, B1a 093]  (Pokémon)
- Attack: [WW] Guard Press 50; card: Water Stage 1 HP 110 (not the A1 067 Shell Armor printing)
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Stakataka  [A3a 053, P-A 080]  (Pokémon)
- Attack: [MC] Brass Rock 40; card: Metal Basic HP 110 (Ultra Beast)
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Skarmory ex  [A4 124, A4 194, A4 209, A4b 252]  (Pokémon)
- Attack: [MM] Steel Wing 70; card: Metal Basic HP 140
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: decks/dustin/07-skarmory-stall.txt (2 Skarmory ex A4 124)

### Avalugg  [B1 075]  (Pokémon)
- Attack: [WWC] Frost Barrier 70; card: Water Stage 1 HP 140
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Swirlix  [B1 117]  (Pokémon)
- Attack: [P] Cotton Guard 10; card: Psychic Basic HP 60
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Ferrothorn  [B1 167]  (Pokémon)
- Attack: [MM] Guard Press 50; card: Metal Stage 1 HP 110
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Porygon  [B1a 056, B3 222]  (Pokémon)
- Attack: [C] Stiffen; card: Colorless Basic HP 60
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Shuckle  [B2 003]  (Pokémon)
- Attack: [GG] Guard Press 40; card: Grass Basic HP 80
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Wigglytuff  [B3b 052]  (Pokémon)
- Attack: [CC] Expand 50; card: Colorless Stage 1 HP 100
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Frigibax  [P-B 037]  (Pokémon)
- Attack: [W] Stiffen; card: Water Basic HP 60 (the Suicune table deck's Stiffen)
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks.
- Engine: ReducedDamage 20
- Evidence: CardEffect::ReducedDamage{amount:20}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 602-610); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Golem  [A1a 045, B1 309]  (Pokémon)
- Attack: [FFFC] Guard Press 120; card: Fighting Stage 2 HP 160
- Text (card.py): During your opponent's next turn, this Pokémon takes -30 damage from attacks.
- Engine: ReducedDamage 30
- Evidence: CardEffect::ReducedDamage{amount:30}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 611-619); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Pupitar  [A4 104]  (Pokémon)
- Attack: [CC] Guard Press 20; card: Fighting Stage 1 HP 80
- Text (card.py): During your opponent's next turn, this Pokémon takes -30 damage from attacks.
- Engine: ReducedDamage 30
- Evidence: CardEffect::ReducedDamage{amount:30}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 611-619); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Carbink  [B1 119]  (Pokémon)
- Attack: [P] Guard Press 30; card: Psychic Basic HP 50 (not the B3b 031 Glittering Gift printing)
- Text (card.py): During your opponent's next turn, this Pokémon takes -30 damage from attacks.
- Engine: ReducedDamage 30
- Evidence: CardEffect::ReducedDamage{amount:30}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 611-619); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none
- Same name, other printing (not this card): decks/brews/brew-10-diancie-giratina.txt (2 Carbink B3b 031: same name, a different printing, not this card)

### Registeel  [B3 116]  (Pokémon)
- Attack: [MCC] Protect Charge 60; card: Metal Basic HP 110
- Text (card.py): During your opponent's next turn, this Pokémon takes -30 damage from attacks.
- Engine: ReducedDamage 30
- Evidence: CardEffect::ReducedDamage{amount:30}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 611-619); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Archaludon  [B4a 056]  (Pokémon)
- Attack: [FMCC] Protect Charge 110; card: Dragon Stage 1 HP 140 (not the B4 113 Raging Blade printing)
- Text (card.py): During your opponent's next turn, this Pokémon takes -30 damage from attacks.
- Engine: ReducedDamage 30
- Evidence: CardEffect::ReducedDamage{amount:30}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 611-619); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: decks/dustin/11-archaludon-haxorus-dragonair.txt (1 Archaludon B4a 056)

### Cosmoem  [A3 086, A4b 182, A4b 183]  (Pokémon)
- Attack: [CC] Stiffen; card: Psychic Stage 1 HP 100
- Text (card.py): During your opponent's next turn, this Pokémon takes -50 damage from attacks.
- Engine: ReducedDamage 50
- Evidence: CardEffect::ReducedDamage{amount:50}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 620-628); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Corviknight  [B1 175, B1 246]  (Pokémon)
- Attack: [MMC] Iron Wings 100; card: Metal Stage 2 HP 140 (not the B3a 048 Metal Claw printing)
- Text (card.py): Discard 2 [M] Energy from this Pokémon. During your opponent's next turn, this Pokémon takes -50 damage from attacks.
- Engine: ReducedDamage 50 after discarding 2 [M]
- Evidence: Mechanic::SelfDiscardEnergyAndCardEffect{effect: ReducedDamage 50, duration 1} (effect_mechanic_map.rs:146-153); dispatched at apply_attack_action.rs:636-645 to self_discard_energy_and_card_effect (2909-2921), add_effect on own Active; engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Gouging Fire  [B3a 054]  (Pokémon)
- Attack: [RLC] Scorching Interruption 100; card: Dragon Basic HP 110
- Text (card.py): Discard 2 Energy from this Pokémon. During your opponent's next turn, this Pokémon takes -30 damage from attacks.
- Engine: ReducedDamage 30 after discarding 2 chosen Energy
- Evidence: Mechanic::SelfDiscardChosenEnergyAndCardEffect{count 2, effect: ReducedDamage 30, duration 1} (effect_mechanic_map.rs:3387-3394); dispatched at apply_attack_action.rs:646-655 to self_discard_chosen_energy_and_card_effect (3706-3723), the effect rides on ChooseAttackEnergyDiscard{defensive_effect}; engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Mega Steelix ex  [B1a 052, B1a 080, B1a 086, B3 232]  (Pokémon)
- Attack: [MMCC] Adamantine Rolling 120; card: Metal Stage 1 (from Onix) HP 220
- Text (card.py): During your opponent's next turn, this Pokémon takes -20 damage from attacks and has no Weakness.
- Engine: ReducedDamage 20 + NoWeakness
- Evidence: Mechanic::DamageAndMultipleCardEffects{opponent:false, [ReducedDamage 20, NoWeakness], duration 1} (effect_mechanic_map.rs:2456-2466); dispatched at apply_attack_action.rs:1239-1248 to damage_and_multiple_card_effects_attack (5832-5852); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Aegislash  [B2 120]  (Pokémon)
- Attack: [MMM] Superb Shield 80; card: Metal Stage 2 HP 140 (not the B1 172 / B1a 102 Cursed Metal printings)
- Text (card.py): During your opponent's next turn, this Pokémon takes -80 damage from attacks from your opponent's Pokémon ex.
- Engine: ReducedDamageFromEx 80 (counts only when the attacker is an ex)
- Evidence: CardEffect::ReducedDamageFromEx{amount:80}, duration 1, on self; engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 2554-2562); read at core.rs:1163 gated on attacker_is_ex; engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Cornerstone Mask Ogerpon  [B2 093]  (Pokémon)
- Attack: [FC] Cornerstone Dance 40; card: Fighting Basic HP 80
- Text (card.py): Flip a coin. If heads, during your opponent's next turn, this Pokémon takes -100 damage from attacks.
- Engine: ReducedDamage 100 on heads only (coin_flip: true)
- Evidence: CardEffect::ReducedDamage{amount:100}, duration 1, on self, coin_flip:true -> AttackOutcomes::binary_coin (apply_attack_action.rs:3492-3496); engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (map 2604-2612); engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)(effect, duration=1) = 'during opponent's next turn'; engine/src/hooks/core.rs:1147-1167 get_reduced_card_effect_modifiers reads CardEffect::ReducedDamage and ReducedDamageFromEx (ex attacker only) on the defending Active, active-to-active hits only; subtracted after Weakness at core.rs:1883-1885; left out of persistent_defender_damage (core.rs:1577-1580)
- In Dustin's files: none

### Ability self-reductions (kind `ability_self_reduction`)

None. `card_effect_from_ability_mechanic` (effect_ability_mechanic_map.rs:993-1011) maps Abilities to the persistent `ReduceDamageFromAttacks` family and the coin/prevention effects, never to `ReducedDamage` or `ReducedDamageFromEx`. See group 4 for the two Abilities that add a temporary full prevention to their holder.

## Group 4: considered, with the reason for each

### Tools and Trainers

### Protective Poncho  [B2 147, B2 234]  (Tool)
- Text (card.py): As long as the Pokémon this card is attached to is on your Bench, prevent all damage done to that Pokémon by your opponent's attacks and Abilities.
- Engine: Full prevention (return 0) for a Benched holder hit by the opponent; not a finite cut
- Evidence: engine/src/hooks/core.rs:1707-1715 (modify_damage returns 0 when target_idx != 0 and the holder has Poncho); tools.rs:55-56
- Decision: considered, listed under kt switch 2 at a price of 0 (spec: Bench-hit pricing is a later candidate); NOT a switch-1 relevant card
- Reason: It prevents Bench damage outright instead of reducing an Active hit, and kp's clock prices hits on the Active only; the proposed registration sets it to 0 on both sides.
- In Dustin's files: decks/dustin/05-indeedee-stoutland.txt (1 Protective Poncho B2 147); decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt (1 Protective Poncho B2 147)

### Rocky Helmet  [A2 148, A4b 322, A4b 323]  (Tool)
- Text (card.py): If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: Damage back to the attacker, not a reduction of the hit
- Evidence: engine/src/hooks/counterattack.rs:13-36 get_counterattack_damage (Rocky Helmet 20 x tool_count at 15-17, plus CardEffect::Counterattack at 19-27, plus AbilityMechanic::CounterattackDamage at 29-33); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; tools.rs:41-42
- Decision: considered, priced by kt switch 3 (counter damage in the holder's own KO clock); NOT a switch-1 relevant card
- Reason: The kt candidate prices it (switch 3), so it is listed for the carrier census, but it is damage back, not a cut: the holder takes the full hit. The other two inputs of the same hook are listed below it, under 'counterattack_inputs'.
- In Dustin's files: decks/dustin/06-mega-blaziken-tournament-list.txt (1 Rocky Helmet A2 148); decks/brews/brew-03a-arceus-nihilego-toxapex.txt (1 Rocky Helmet A4b 322); decks/brews/brew-06-pyukumuku-silvally-payback.txt (1 Rocky Helmet A2 148); decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt (1 Rocky Helmet A2 148)

### Poison Barb  [A3 146]  (Tool)
- Text (card.py): If the Pokémon this card is attached to is your Active Pokémon and is damaged by an attack from your opponent's Pokémon, the Attacking Pokémon is now Poisoned.
- Engine: Poisons the attacker; no damage arithmetic on the hit
- Evidence: engine/src/hooks/counterattack.rs:117-124 should_poison_attacker; tools.rs:43-44
- Decision: excluded: the review drops it from kt (needs the Special Conditions model, deferred)
- Reason: Not a damage cut; the proposed registration says should_poison_attacker is not called.
- In Dustin's files: decks/dustin/10-xatu-oricorio-tr-weezing.txt (2 Poison Barb A3 146); decks/brews/brew-03a-arceus-nihilego-toxapex.txt (1 Poison Barb A3 146)

### Clear Veil  [B4 149]  (Tool)
- Text (card.py): Prevent all effects of attacks used by your opponent's Pokémon done to the Pokémon this card is attached to. (Existing effects are not removed.)
- Engine: Blocks attack effects (State::prevents_attack_effects), never damage
- Evidence: engine/src/tools.rs:87-91 (doc: resolved in State::prevents_attack_effects)
- Decision: excluded
- Reason: Damage passes through untouched; only the rider effects are stopped.
- In Dustin's files: none

### Hala  [B1 222, B1 267]  (Supporter)
- Text (card.py): During your opponent's next turn, if your Hariyama or Crabominable would be Knocked Out by damage from an attack, it is not Knocked Out and its remaining HP becomes 10.
- Engine: TurnEffect::SurviveKnockoutForSpecificPokemon{remaining_hp:10, [Hariyama, Crabominable]}, duration 1
- Evidence: engine/src/actions/apply_trainer_action.rs:1699-1710 hala_effect; dispatch 180
- Decision: excluded
- Reason: A knockout-survival turn effect, not a damage reduction; the kt hook reads ReducedDamageForTarget/ForType only.
- In Dustin's files: none

### Attack effect that removes the holder's Weakness next turn (excluded from switch 1; same route as group 3)

Added in the adjudication (skeptic point 3). It is the one temporary next-turn defensive effect the engine registers through the group-3 route that is not a `ReducedDamage`; the database holds it on Steelix only (the same words ride on Mega Steelix ex's Adamantine Rolling, group 3).

### Steelix  [B1a 051, B3 219]  (Pokémon)
- Attack: [MMCC] Metal Defender 100; card: Metal Stage 1 (from Onix) HP 150 (not the A4 122 Heavy Impact printing)
- Text (card.py): During your opponent's next turn, this Pokémon has no Weakness.
- Engine: CardEffect::NoWeakness, duration 1, on self: the Weakness stage (+20, or Bounded Field's x2) is skipped for hits the holder takes on the opponent's next turn; no amount is subtracted
- Evidence: effect_mechanic_map.rs:367-375 (map entry: DamageAndCardEffect{opponent:false, effect: CardEffect::NoWeakness, duration:1, coin_flip:false}); engine/src/actions/effect_mechanic_map.rs -> Mechanic::DamageAndCardEffect{opponent:false, ..., duration:1}; dispatched at engine/src/actions/apply_attack_action.rs:722-733 to damage_and_card_effect_attack (3467-3500), which add_effect()s on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)); read at hooks/core.rs:1468-1484 weakness_application_against (returns WeaknessApplication::None when the receiver holds NoWeakness, else printed_weakness_application); persistent_defender_damage's doc names NoWeakness among the temporary effects it leaves out (core.rs:1577-1578); the same rider on Mega Steelix ex is at effect_mechanic_map.rs:2456-2466 (group 3)
- Decision: considered, EXCLUDED from the switch-1 set: not a ReducedDamage / ReducedDamageFromEx, and the proposed hook temporary_defender_reduction sums finite amounts only, so the kt candidate as drafted does not see it
- Reason: Same attack route and duration as every group-3 card, but it removes the Weakness stage instead of subtracting a fixed amount. Lists-phase note: Steelix is one of Jasmine's two named targets and the engine's scope test is an exact name match (core.rs:1233 names.contains(&pokemon.get_name())), so every card named 'Steelix' (A4 122 Heavy Impact; B1a 051 / B3 219 Metal Defender) is covered by Jasmine in the engine and 'Mega Steelix ex' [B1a 052, B1a 080, B1a 086, B3 232] is not. That is an engine reading, not a rules claim.
- In Dustin's files: none

### Counter damage priced by kt switch 3 beside Rocky Helmet (not switch 1)

The three inputs of get_counterattack_damage (hooks/counterattack.rs:13-36), which the proposed registration names for switch 3 (kt_spec_review.md lines 175-176). Rocky Helmet is the first (tools_and_trainers); these are the other two. None is a switch-1 card. Added in the adjudication (skeptic point 4).

#### Attacks that register `CardEffect::Counterattack` on the user for the opponent's next turn

### Turtonator  [B1 047]  (Pokémon)
- Attack: [RR] Shell Trap 40; card: Fire Basic HP 110 (not the A3 037 / A3 161 Fire Spin or B4 123 Searing Flame printings)
- Text (card.py): During your opponent's next turn, if this Pokémon is damaged by an attack, do 20 damage to the Attacking Pokémon.
- Engine: CardEffect::Counterattack{amount:20}, duration 1, on self: damage back to the attacker, the holder takes the full hit
- Evidence: effect_mechanic_map.rs:525-533; dispatched at apply_attack_action.rs:722-733 (DamageAndCardEffect{opponent:false}) to damage_and_card_effect_attack (3467-3500), add_effect on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)); read at hooks/counterattack.rs:19-27 get_counterattack_damage (sums every CardEffect::Counterattack on the damaged card); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation (attacker.apply_damage(counter_damage) for each damaged Active)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (counter damage in the holder's own side's KO clock; kt_spec_review.md lines 175-176 name 'CardEffect::Counterattack such as Spike Armor'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut.
- In Dustin's files: none

### Togedemaru  [A3b 048, P-A 090]  (Pokémon)
- Attack: [MM] Bristling Spikes 30; card: Metal Basic HP 80 (not the A3 067 Electrosmash or B4a 045 Tumbling Attack printings)
- Text (card.py): During your opponent's next turn, if this Pokémon is damaged by an attack, do 30 damage to the Attacking Pokémon.
- Engine: CardEffect::Counterattack{amount:30}, duration 1, on self: damage back to the attacker, the holder takes the full hit
- Evidence: effect_mechanic_map.rs:534-542; dispatched at apply_attack_action.rs:722-733 (DamageAndCardEffect{opponent:false}) to damage_and_card_effect_attack (3467-3500), add_effect on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)); read at hooks/counterattack.rs:19-27 get_counterattack_damage (sums every CardEffect::Counterattack on the damaged card); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation (attacker.apply_damage(counter_damage) for each damaged Active)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (counter damage in the holder's own side's KO clock; kt_spec_review.md lines 175-176 name 'CardEffect::Counterattack such as Spike Armor'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut.
- In Dustin's files: none

### Alolan Sandslash  [A3 039]  (Pokémon)
- Attack: [W] Spike Armor 20; card: Water Stage 1 HP 100
- Text (card.py): During your opponent's next turn, if this Pokémon is damaged by an attack, do 40 damage to the Attacking Pokémon.
- Engine: CardEffect::Counterattack{amount:40}, duration 1, on self: damage back to the attacker, the holder takes the full hit
- Evidence: effect_mechanic_map.rs:543-551; dispatched at apply_attack_action.rs:722-733 (DamageAndCardEffect{opponent:false}) to damage_and_card_effect_attack (3467-3500), add_effect on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)); read at hooks/counterattack.rs:19-27 get_counterattack_damage (sums every CardEffect::Counterattack on the damaged card); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation (attacker.apply_damage(counter_damage) for each damaged Active)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (counter damage in the holder's own side's KO clock; kt_spec_review.md lines 175-176 name 'CardEffect::Counterattack such as Spike Armor'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut: the spec's own example.
- In Dustin's files: none

### Mega Sableye ex  [B3b 041, B3b 081, B3b 088]  (Pokémon)
- Attack: [DC] Cursed Jewel 80; card: Darkness Basic HP 170
- Text (card.py): During your opponent's next turn, if this Pokémon is damaged by an attack, do 40 damage to the Attacking Pokémon.
- Engine: CardEffect::Counterattack{amount:40}, duration 1, on self: damage back to the attacker, the holder takes the full hit
- Evidence: effect_mechanic_map.rs:543-551; dispatched at apply_attack_action.rs:722-733 (DamageAndCardEffect{opponent:false}) to damage_and_card_effect_attack (3467-3500), add_effect on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)); read at hooks/counterattack.rs:19-27 get_counterattack_damage (sums every CardEffect::Counterattack on the damaged card); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation (attacker.apply_damage(counter_damage) for each damaged Active)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (counter damage in the holder's own side's KO clock; kt_spec_review.md lines 175-176 name 'CardEffect::Counterattack such as Spike Armor'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut: in two of Dustin's brews, so switch 3 touches those two files.
- In Dustin's files: decks/brews/brew-07-hoopa-darkrai-sableye.txt (1 Mega Sableye ex B3b 041); decks/brews/brew-09-sableye-obstagoon.txt (2 Mega Sableye ex B3b 041)

### Chesnaught  [B2 010]  (Pokémon)
- Attack: [GGCC] Needle Lariat 80; card: Grass Stage 2 HP 160
- Text (card.py): During your opponent's next turn, if this Pokémon is damaged by an attack, do 80 damage to the Attacking Pokémon.
- Engine: CardEffect::Counterattack{amount:80}, duration 1, on self: damage back to the attacker, the holder takes the full hit
- Evidence: effect_mechanic_map.rs:2536-2544; dispatched at apply_attack_action.rs:722-733 (DamageAndCardEffect{opponent:false}) to damage_and_card_effect_attack (3467-3500), add_effect on the attacker's own Active (engine/src/state/played_card.rs:344-346 add_effect (doc comment 340-343)); read at hooks/counterattack.rs:19-27 get_counterattack_damage (sums every CardEffect::Counterattack on the damaged card); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation (attacker.apply_damage(counter_damage) for each damaged Active)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (counter damage in the holder's own side's KO clock; kt_spec_review.md lines 175-176 name 'CardEffect::Counterattack such as Spike Armor'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut.
- In Dustin's files: none

#### Abilities mapped to `AbilityMechanic::CounterattackDamage{20}`

### Poliwrath  [A1 061, B1 297]  (Pokémon)
- Ability: Counterattack; card: Water Stage 2 HP 150 (not Poliwrath ex A4a 042 / A4a 082 / A4a 089, another name)
- Text (card.py): If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: AbilityMechanic::CounterattackDamage{amount:20}: persistent while the Ability is in play and not suppressed; damage back to the attacker
- Evidence: effect_ability_mechanic_map.rs:219-222 (map entry: AbilityMechanic::CounterattackDamage{amount:20}); read at hooks/counterattack.rs:29-33 get_counterattack_damage via get_in_play_ability_mechanic (suppression-aware); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; passive, never activated (apply_abilities_action.rs:327-328 panics if invoked; move_generation_abilities.rs:229 offers it never)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (kt_spec_review.md lines 175-176 name 'CounterattackDamage abilities; none of the latter in the eight lists'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut; the holder takes the full hit.
- In Dustin's files: none

### Druddigon  [A1a 056]  (Pokémon)
- Ability: Rough Skin; card: Dragon Basic HP 100 (not the B1 176 Giga Claw or B2b 057 Clutch printings)
- Text (card.py): If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: AbilityMechanic::CounterattackDamage{amount:20}: persistent while the Ability is in play and not suppressed; damage back to the attacker
- Evidence: effect_ability_mechanic_map.rs:219-222 (map entry: AbilityMechanic::CounterattackDamage{amount:20}); read at hooks/counterattack.rs:29-33 get_counterattack_damage via get_in_play_ability_mechanic (suppression-aware); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; passive, never activated (apply_abilities_action.rs:327-328 panics if invoked; move_generation_abilities.rs:229 offers it never)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (kt_spec_review.md lines 175-176 name 'CounterattackDamage abilities; none of the latter in the eight lists'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut; the holder takes the full hit.
- In Dustin's files: none

### Pawmot  [A2b 028, P-A 054]  (Pokémon)
- Ability: Counterattack; card: Lightning Stage 2 HP 140 (not the B2a 040 / B2a 121 Thunder Blast or B3a 016 Volt Wave printings)
- Text (card.py): If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: AbilityMechanic::CounterattackDamage{amount:20}: persistent while the Ability is in play and not suppressed; damage back to the attacker
- Evidence: effect_ability_mechanic_map.rs:219-222 (map entry: AbilityMechanic::CounterattackDamage{amount:20}); read at hooks/counterattack.rs:29-33 get_counterattack_damage via get_in_play_ability_mechanic (suppression-aware); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; passive, never activated (apply_abilities_action.rs:327-328 panics if invoked; move_generation_abilities.rs:229 offers it never)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (kt_spec_review.md lines 175-176 name 'CounterattackDamage abilities; none of the latter in the eight lists'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut; the holder takes the full hit.
- In Dustin's files: none

### Ferrothorn  [A3a 052]  (Pokémon)
- Ability: Steel Spikes; card: Metal Stage 1 HP 110 (not the B1 167 Guard Press printing, which is in group 3, nor B2 116 Pummel)
- Text (card.py): If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: AbilityMechanic::CounterattackDamage{amount:20}: persistent while the Ability is in play and not suppressed; damage back to the attacker
- Evidence: effect_ability_mechanic_map.rs:219-222 (map entry: AbilityMechanic::CounterattackDamage{amount:20}); read at hooks/counterattack.rs:29-33 get_counterattack_damage via get_in_play_ability_mechanic (suppression-aware); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; passive, never activated (apply_abilities_action.rs:327-328 panics if invoked; move_generation_abilities.rs:229 offers it never)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (kt_spec_review.md lines 175-176 name 'CounterattackDamage abilities; none of the latter in the eight lists'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut; the holder takes the full hit.
- In Dustin's files: none

### Zangoose  [A4a 065]  (Pokémon)
- Ability: Counterattack; card: Colorless Basic HP 80
- Text (card.py): If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: AbilityMechanic::CounterattackDamage{amount:20}: persistent while the Ability is in play and not suppressed; damage back to the attacker
- Evidence: effect_ability_mechanic_map.rs:219-222 (map entry: AbilityMechanic::CounterattackDamage{amount:20}); read at hooks/counterattack.rs:29-33 get_counterattack_damage via get_in_play_ability_mechanic (suppression-aware); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; passive, never activated (apply_abilities_action.rs:327-328 panics if invoked; move_generation_abilities.rs:229 offers it never)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (kt_spec_review.md lines 175-176 name 'CounterattackDamage abilities; none of the latter in the eight lists'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut; the holder takes the full hit.
- In Dustin's files: none

### Iron Jugulis  [B3a 046]  (Pokémon)
- Ability: Automated Combat; card: Darkness Basic HP 100
- Text (card.py): If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.
- Engine: AbilityMechanic::CounterattackDamage{amount:20}: persistent while the Ability is in play and not suppressed; damage back to the attacker
- Evidence: effect_ability_mechanic_map.rs:219-222 (map entry: AbilityMechanic::CounterattackDamage{amount:20}); read at hooks/counterattack.rs:29-33 get_counterattack_damage via get_in_play_ability_mechanic (suppression-aware); applied at actions/apply_action_helpers.rs:593-612 handle_attack_retaliation; passive, never activated (apply_abilities_action.rs:327-328 panics if invoked; move_generation_abilities.rs:229 offers it never)
- Decision: considered, priced by kt switch 3 with Rocky Helmet (kt_spec_review.md lines 175-176 name 'CounterattackDamage abilities; none of the latter in the eight lists'); NOT a switch-1 relevant card
- Reason: Damage back, not a cut; the holder takes the full hit.
- In Dustin's files: none

#### Not inputs of `get_counterattack_damage` (listed so nobody adds them to switch 3 by mistake)

- **AbilityMechanic::DamageOnKnockoutInActive{amount, target: Attacker} (NOT an input of get_counterattack_damage)**
  - Text (card.py, the 50 version): If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 50 damage to the Attacking Pokémon.
  - Evidence: effect_ability_mechanic_map.rs:195-208 (70 and 50); applied on the holder's knockout at hooks/core.rs:2192-2212, a different path from handle_attack_retaliation; the spec's switch 3 is declared 'through get_counterattack_damage', so these are not priced by kt as drafted
  - Cards: Pyukumuku [A3 054 / A3 163 / A4a 097] Innards Out (50); Team Rocket's Electrode [B4a 020] Destiny Burst (70)
  - In Dustin's files: Pyukumuku: decks/brews/brew-06-pyukumuku-silvally-payback.txt (2 Pyukumuku A3 054), decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt (2 Pyukumuku A3 054)

### Attack effects that prevent all damage to the user next turn (excluded)

Excluded from the switch-1 set. They are all-or-nothing (`modify_damage` returns 0; core.rs:1717-1734 and 1888-1894), most sit behind a coin, and the proposed hook `temporary_defender_reduction` sums finite `ReducedDamage`/`ReducedDamageFromEx` amounts only. Listed so the spec can say so explicitly. None is in Dustin's decks (Bombirdier B3 115 in deck 04 is the Villainous Delivery printing, not Fly).

- **CardEffect::PreventDamageIfLessOrEqual{threshold:40}, duration 1, on self**
  - Text (card.py): During your opponent's next turn, prevent all damage done to this Pokémon by attacks if that damage is 40 or less.
  - Evidence: effect_mechanic_map.rs:552-560; read at core.rs:1888-1894 (returns 0 when final damage <= threshold)
  - Cards: Silcoon [B1 004] Harden; Cascoon [B1 006] Harden
  - In Dustin's files: none
- **CardEffect::PreventAllDamageAndEffects, duration 1, on self, on heads**
  - Text (card.py): Flip a coin. If heads, during your opponent's next turn, prevent all damage done to this Pokémon by attacks.
  - Evidence: effect_mechanic_map.rs:970-978 (coin_flip:true); read at core.rs:1717-1724 (returns 0)
  - Cards: Chansey [A4 131] Scrunch; Nosepass [P-A 045] Iron Defense
  - In Dustin's files: none
- **CardEffect::PreventAllDamageAndEffects, duration 1, on self, on heads**
  - Text (card.py): Flip a coin. If heads, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon.
  - Evidence: effect_mechanic_map.rs:979-984 (coin_flip:true); read at core.rs:1717-1724
  - Cards: Dugtrio [A1 140] Dig; Cramorant [A1a 024] Dive; Finneon [A2 042] Elegant Swim; Shinx [A2 058 / A2 163] Hide; Gimmighoul [A2b 036] Chest-ouflage; Revavroom [A2b 056 / A2b 106] Spinning Drift; Mr. Mime [A3 069] Barrier Shove; Carbink [A3b 042] Hard Roll; Magikarp [A4 044] Splashing Dodge; Mantine [A4 058] Dive; Onix [B1a 038 / B3 211] Dig; Sinistea [B2 074 / B4a 100] Hide; Quaxly [B2a 022 / P-B 033] Splashing Dodge; Swadloon [B3 016] Protect; Cyclizar [B4 128 / B4 177] Acceleration Drive; Team Rocket's Kecleon [B4a 062 / B4a 076] Hit and Hide; Charcadet [P-B 064] Protect; Feebas [P-B 072] Hide
  - In Dustin's files: none
- **CardEffect::PreventAllDamageAndEffects, duration 1, on self, on heads; tails does nothing**
  - Text (card.py): Flip a coin. If tails, this attack does nothing. If heads, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon.
  - Evidence: effect_mechanic_map.rs:1126-1130 Mechanic::CoinFlipNoDamageOrDamageAndCardEffect; apply_attack_action.rs:734-743 -> 3502-3523
  - Cards: Noctowl [A4 141] Fly; Bombirdier [B2a 071] Fly; Altaria [B3a 052] Fly; Unfezant [B4 139] Fly
  - In Dustin's files: none
- **CardEffect::PreventDamageFromBasic, duration 1, on self**
  - Text (card.py): Prevent all damage done to this Pokémon by attacks from Basic Pokémon during your opponent's next turn.
  - Evidence: effect_mechanic_map.rs:1637-1645; read at core.rs:1726-1734 (returns 0 when the attacker is a Basic)
  - Cards: Carracosta [B1 067] Blocking Shell
  - In Dustin's files: none

### Abilities that give their holder a full prevention for the opponent's next turn (excluded, flagged)

Excluded for the same reason (full prevention, `CardEffect::PreventAllDamageAndEffects`, not a finite cut). Flag for the spec: Dustin's deck 08 (Garchomp toolbox) carries Garchomp B4a 054, whose Mach Stealth the kt hook as written cannot see.

- **AbilityMechanic::PreventAllDamageAndEffectsOnEvolve{duration:1} -> add_effect(PreventAllDamageAndEffects, 1) on self**
  - Text (card.py): Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may prevent all damage from—and effects of—attacks from your opponent's Pokémon done to this Pokémon until the end of your opponent's next turn.
  - Evidence: effect_ability_mechanic_map.rs:849-853; apply_abilities_action.rs:411-421; offered at hooks/core.rs:241-245
  - Cards: Samurott [B4 044 / B4 163] Stance
  - In Dustin's files: none
- **AbilityMechanic::ProtectSelfNextTurnAfterAttackKnockout -> add_effect(PreventAllDamageAndEffects, 1) on the attacker when its active attack knocks out an opponent's Pokémon**
  - Text (card.py): If your opponent's Pokémon is Knocked Out by damage from this Pokémon's attacks, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon.
  - Evidence: effect_ability_mechanic_map.rs:279-282; hooks/core.rs:2436-2462 on_attack_knockout
  - Cards: Garchomp [B4a 054] Mach Stealth; Zoroark [A4a 050 / P-A 106] Illusive Trickery
  - In Dustin's files: Garchomp: decks/dustin/08-garchomp-toolbox.txt (2 Garchomp B4a 054)

### Persistent Ability reductions and preventions (excluded)

Excluded: not temporary and not Tool-based. They are already in `persistent_defender_damage` (core.rs:1583-1644: the ReduceDamageFromAttacks family at 1609-1616, conditional abilities at 1617-1624, Coordinated Unit at 1625, Ice Face first-hit at 1630-1639; Safeguard at 1596-1598) or in `modify_damage`'s prevention stages, and the kt registration takes over the Tool stages only. Dustin carriers noted for completeness.

- **ReduceDamageFromAttacks 10**: This Pokémon takes -10 damage from attacks.  (evidence: effect_ability_mechanic_map.rs:603-606)
  - Cards: Cloyster [A1 067] Shell Armor; Dwebble [P-B 059] Shell Armor
  - In Dustin's files: none
- **ReduceDamageFromAttacks 20**: This Pokémon takes -20 damage from attacks.  (evidence: effect_ability_mechanic_map.rs:614-617)
  - Cards: Melmetal [A1 182] Hard Coat; Regirock [A2 087] Exoskeleton; Alolan Persian [A3 109] Fur Coat; Shuckle ex [A4 021 / A4 186 / A4 202 / A4b 023] Solid Shell; Donphan [A4a 044] Exoskeleton; Furfrou [B1 206 / B1 207 / B1 208 / B1a 065 / B2 141 / B2b 064 / B3 144 / B3b 061 / B4 142 / B4a 064] Fur Coat
  - In Dustin's files: none
- **ReduceDamageFromAttacks 30**: This Pokémon takes -30 damage from attacks.  (evidence: effect_ability_mechanic_map.rs:728-731)
  - Cards: Armarouge ex [B2a 020 / B2a 101 / B2a 111 / B3a 105] Armor
  - In Dustin's files: none
- **ReduceDamageFromTypedAttackers 20 (R/W)**: This Pokémon takes -20 damage from attacks from [R] or [W] Pokémon.  (evidence: effect_ability_mechanic_map.rs:607-613)
  - Cards: Piloswine [A2 032] Thick Fat
  - In Dustin's files: none
- **ReduceDamageFromTypedAttackers 30 (R/W)**: This Pokémon takes -30 damage from attacks from [R] or [W] Pokémon.  (evidence: effect_ability_mechanic_map.rs:625-631)
  - Cards: Mamoswine [A2 033 / A2 160] Thick Fat; Azumarill [A4 050] Thick Fat
  - In Dustin's files: none
- **ReduceDamageFromTypedAttackers 30 (F)**: This Pokémon takes -30 damage from attacks from [F] Pokémon.  (evidence: effect_ability_mechanic_map.rs:618-624)
  - Cards: Staraptor [P-A 047] Defensive Whirlwind
  - In Dustin's files: none
- **ReduceDamageIfArceusInPlay 30**: If you have Arceus or Arceus ex in play, this Pokémon takes -30 damage from attacks.  (evidence: effect_ability_mechanic_map.rs:261-264)
  - Cards: Raichu [A2a 026 / P-A 044] Resilience Link; Magnezone [A2a 055] Resilience Link
  - In Dustin's files: none
- **ReduceDamageAtFullHp 40 (first hit only)**: If this Pokémon has full HP, it takes -40 damage from attacks from your opponent's Pokémon.  (evidence: effect_ability_mechanic_map.rs:184-187; core.rs:1630-1639)
  - Cards: Eiscue [B1 080 / B1 236] Ice Face
  - In Dustin's files: none
- **UnownGuard 10 (all your Pokémon)**: This Ability works if you have any Unown in play with an Ability other than GUARD. All of your Pokémon take -10 damage from attacks from your opponent's Pokémon.  (evidence: effect_ability_mechanic_map.rs:563-566)
  - Cards: Unown [A4 084] GUARD
  - In Dustin's files: none
- **CoordinatedUnit -20 (with another Falinks)**: If you have another Falinks in play, this Pokémon's attacks do +20 damage to your opponent's Active Pokémon, and this Pokémon takes -20 damage from attacks from your opponent's Pokémon.  (evidence: effect_ability_mechanic_map.rs:255-260; core.rs:1357-1363)
  - Cards: Falinks [B2 092 / B2 172 / B4 215] Coordinated Unit
  - In Dustin's files: none
- **ReduceOpponentActiveDamage 20 (attacker-side stage, before Weakness)**: As long as this Pokémon is in the Active Spot, attacks used by your opponent's Active Pokémon do -20 damage.  (evidence: effect_ability_mechanic_map.rs:32-35; core.rs:764-790, 1741-1753)
  - Cards: Luxray [A3a 015] Intimidating Fang
  - In Dustin's files: none
- **CoinFlipToReduceDamage 100 / 80**: If any damage is done to this Pokémon by attacks, flip a coin. If heads, this Pokémon takes -100 damage from that attack.  (evidence: effect_ability_mechanic_map.rs:164-171)
  - Cards: Bastiodon [A2 114] Guarded Grill (-100); Hisuian Goodra [B3b 050] Securely Sheltered (-80)
  - In Dustin's files: none
- **CoinFlipToPreventDamage**: If any damage is done to this Pokémon by attacks, flip a coin. If heads, prevent that damage.  (evidence: effect_ability_mechanic_map.rs:160-163)
  - Cards: Togekiss [A4 080] Celestial Blessing; Meowth [B2 124 / B2 204] Carefree Steps
  - In Dustin's files: none
- **PreventAllDamageFromEx**: Prevent all damage done to this Pokémon by attacks from your opponent's Pokémon ex.  (evidence: effect_ability_mechanic_map.rs:551-554; core.rs:1686-1695)
  - Cards: Oricorio [A3 066 / A3 165 / A4b 146 / A4b 147 / B1 303] Safeguard
  - In Dustin's files: Oricorio: decks/dustin/15-jolteon-oricorio-raticate.txt (1 Oricorio A3 066)
- **PreventDamageWhileBenched**: As long as this Pokémon is on your Bench, prevent all damage done to this Pokémon by attacks.  (evidence: effect_ability_mechanic_map.rs:63-66; core.rs:1696-1705)
  - Cards: Wartortle [B1a 018] Shell Shield
  - In Dustin's files: none
- **PreventFirstAttack**: When this Pokémon is first damaged by an attack after coming into play, prevent that damage.  (evidence: effect_ability_mechanic_map.rs:639-642)
  - Cards: Mimikyu ex [B2 073 / B2 186 / B2 199 / B4a 107] Disguise
  - In Dustin's files: none
- **CoinFlipToSurviveKnockOut (survival, not a cut)**: If this Pokémon would be Knocked Out by damage from an attack, flip a coin. If heads, this Pokémon is not Knocked Out, and its remaining HP becomes 10.  (evidence: effect_ability_mechanic_map.rs:237-240)
  - Cards: Conkeldurr [A3 096] Guts; Ursaluna [B3b 058] Guts
  - In Dustin's files: none

### Cuts stored on the opponent's attacker (excluded)

Excluded: the effect lives on the opponent's Defending Pokémon and is applied as an attacker-side reduction before Weakness (core.rs:1862-1875), so it is not a cut registered on the player's own Pokémon; kp's threat clock already reads `ReducedAttackDamage` and `CoinFlipToBlockAttack` at value_functions.rs:1050-1051.

- **CardEffect::ReducedAttackDamage{20} on the Defending Pokémon, duration 1 (Growl family)**
  - Text (card.py): During your opponent's next turn, attacks used by the Defending Pokémon do -20 damage.
  - Evidence: effect_mechanic_map.rs:498-506 (opponent:true); applied as carried_attack_reduction before Weakness at core.rs:1862-1875; kp's threat clock already reads it at players/value_functions.rs:1050
  - Cards: Cubone [A1 151 / A1 239 / A3 226 / A4b 194 / A4b 195] Growl; Suicune [A4 059] Cure Stream; Togepi [A4 078 / A4 173] Charm; Slowpoke [B3b 026] Growl; Teddiursa [B3b 056] Charm; Pikachu [B4 049 / P-B 082] Growl; Skitty [B4 134] Charm; Eevee [P-A 030] Growl
  - In Dustin's files: none
- **CardEffect::ReducedAttackDamage{30} on the Defending Pokémon, duration 1**
  - Text (card.py): During your opponent's next turn, attacks used by the Defending Pokémon do -30 damage.
  - Evidence: effect_mechanic_map.rs:507-515; core.rs:1862-1875; value_functions.rs:1050
  - Cards: Clefable [A2a 030] Moonblast; Bonsly [B3 078 / B3 168] Teary Attack
  - In Dustin's files: none
- **CardEffect::CoinFlipToBlockAttack on the Defending Pokémon, until it leaves the Active Spot**
  - Text (card.py): During your opponent's next turn, if the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that attack doesn't happen.
  - Evidence: effect_mechanic_map.rs:1244-1249; apply_attack_action.rs:6803-6814; value_functions.rs:1051
  - Cards: Magnezone [B1a 026] Mirror Shot
  - In Dustin's files: none

## Notes for the Lists phase

- decks/dustin/10-xatu-oricorio-tr-weezing.txt carries 2 Oricorio B4 078 (Supernatural Feather), not the Safeguard printing; the Safeguard carrier is decks/dustin/15-jolteon-oricorio-raticate.txt (1 Oricorio A3 066).
- decks/dustin/05-indeedee-stoutland.txt carries 2 Stoutland A3a 056 (Guard Dog Visage) beside its 1 Cheren B3 151; Cheren's scope is NamedPokemon[Watchog, Stoutland] matched by exact name (core.rs:1233), so this printing is a Cheren target in the engine.
- Jasmine's scope is NamedPokemon[Steelix, Skarmory ex] by exact name (core.rs:1233): every card named 'Steelix' (A4 122 Heavy Impact; B1a 051 / B3 219 Metal Defender) and 'Skarmory ex' (A4 124 / A4 194 / A4 209 / A4b 252) is covered; 'Mega Steelix ex' is not.
- Mega Sableye ex B3b 041 (Cursed Jewel, a switch-3 counterattack card) is in decks/brews/brew-07-hoopa-darkrai-sableye.txt (1) and decks/brews/brew-09-sableye-obstagoon.txt (2); Pyukumuku A3 054 (Innards Out, not a switch-3 input) is in brew-06 (2) and brew-06b (2).

## Disputed points and how they were settled

The skeptic (`cards_skeptic.md`) raised five points against the first pass. Each was re-checked against the engine working tree and `python lib/card.py` before ruling; the scan scripts and raw output are in the session scratchpad (`kt_census/adjudicate_scan.py`, `adjudicate_scan.out`, `cardpy_adjudicate.out`, `adjudicate_build.py`). Bottom line: all five upheld; none moves a card into or out of groups 1 to 3, so the set clause (d) reads is unchanged (33 cards, 55 printings); group 4 gains Steelix's Metal Defender and the eleven other counterattack cards; two counts and one line number in the prose are corrected.

1. **Point.** cards.md line 3 and cards.json sources.decks said 'decks/brews/*.txt (11 files)'.
   - Checked: Glob and the deck parser over decks/brews/*.txt: 13 files (brew-01, 02, 03a, 03b, 04, 05, 05b, 06, 06b, 07, 08, 09, 10); build_cards.py's own scan read all 13 (its placements match a fresh scan id for id), so the '11' was a typo in the prose, not a skipped file.
   - Ruling: Skeptic upheld. Both files now say 13. No placement changes.
2. **Point.** cards.md line 11 said group 3 is '25 cards, 46 printings'.
   - Checked: Summed the ids in cards.json group 3: 1+2+1+4+2+2+4+1+1+1+2+1+1+1+2+1+1+1+1+3+2+1+4+1+1 = 42; adjudicate_scan.py: 25 cards, 42 printings; cards.json's summary already said 55 = 9 (group 1) + 4 (group 2) + 42 (group 3).
   - Ruling: Skeptic upheld. The prose now says 42. Nothing in the set changes.
3. **Point.** Steelix [B1a 051, B3 219] Metal Defender (CardEffect::NoWeakness) was missing from group 4, while the census said the engine has 'exactly three kinds of such cut' and listed the same rider on Mega Steelix ex.
   - Checked: card.py: 'During your opponent's next turn, this Pokémon has no Weakness.' effect_mechanic_map.rs:367-375 maps that text to DamageAndCardEffect{opponent:false, CardEffect::NoWeakness, duration:1} (same route and duration as group 3); core.rs:1468-1484 weakness_application_against returns None under it; core.rs:1578 lists NoWeakness among what persistent_defender_damage leaves out; core.rs:1233 scope by exact name. Database exact-text scan: only Steelix B1a 051 / B3 219 carry the text; the only other 'no Weakness' text is Mega Steelix ex's (group 3). Not in any of the 28 deck files.
   - Ruling: Skeptic upheld. Added to group 4 as considered and excluded from switch 1 (not a ReducedDamage, the hook cannot see it), with the Jasmine scope note for the Lists phase; the 'exactly three kinds' sentence now says three kinds of finite cut plus this one Weakness-removing effect. Groups 1 to 3 unchanged; clause (d) unchanged.
4. **Point.** Group 4 listed Rocky Helmet 'because kt prices it' (switch 3) but not the other two inputs of get_counterattack_damage.
   - Checked: counterattack.rs:13-36 sums Rocky Helmet, CardEffect::Counterattack and AbilityMechanic::CounterattackDamage; kt_spec_review.md lines 175-176 declare switch 3 'through get_counterattack_damage (Rocky Helmet, CardEffect::Counterattack such as Spike Armor, and CounterattackDamage abilities)'. effect_mechanic_map.rs:525-551 and 2536-2544 map the four Counterattack texts (20/30/40/80); effect_ability_mechanic_map.rs:219-222 maps the Ability text. card.py and the database exact-text scan give Turtonator B1 047 (20), Togedemaru A3b 048 / P-A 090 (30), Alolan Sandslash A3 039 (40), Mega Sableye ex B3b 041 / 081 / 088 (40), Chesnaught B2 010 (80); Poliwrath A1 061 / B1 297, Druddigon A1a 056, Pawmot A2b 028 / P-A 054, Ferrothorn A3a 052, Zangoose A4a 065, Iron Jugulis B3a 046 (Ability, 20). Deck scan: Mega Sableye ex B3b 041 in brew-07 (1) and brew-09 (2); none of the others. The scan also turned up two knockout-triggered damage-back Abilities (Pyukumuku's Innards Out, Team Rocket's Electrode's Destiny Burst) that go through DamageOnKnockoutInActive (core.rs:2192-2212), not get_counterattack_damage; recorded as not inputs.
   - Ruling: Skeptic upheld: the inclusion rule is kept and the eleven cards are added to group 4 under 'counterattack_inputs' with the same decision as Rocky Helmet (kt switch 3, not switch 1). Groups 1 to 3 unchanged; clause (d) unchanged. Note for the spec: switch 3 now visibly touches two of Dustin's brews (Mega Sableye ex).
5. **Point.** Minor: played_card.rs add_effect cited as 340-346 (it is 344-346); deck 10's 2 Oricorio B4 078 and deck 05's 2 Stoutland A3a 056 were not flagged.
   - Checked: played_card.rs: doc comment 340-343, `pub fn add_effect` 344-346. card.py: Oricorio B4 078 is Supernatural Feather (the Safeguard printings are A3 066 / A3 165 / A4b 146 / A4b 147 / B1 303); Stoutland A3a 056 is Guard Dog Visage. Deck scan confirms both placements.
   - Ruling: Skeptic upheld. Every evidence string now cites 344-346 (doc 340-343); the two placements are recorded under lists_phase_notes. No set change.

## Provenance and limits

- Scratch scripts and raw card.py output: session scratchpad `kt_census/` (first pass: find_cards.py, scan2.py, scan3.py, build_cards.py, cardpy_main.out, cardpy_considered.out; skeptic: skeptic_check.py, skeptic_check2.py, cardpy_skeptic.out; adjudication: adjudicate_scan.py, adjudicate_scan.out, cardpy_adjudicate.out, adjudicate_build.py).
- Engine line numbers are from the working tree at main 4924008 on Sept 26 (re-confirmed with git rev-parse during the adjudication; this results folder is untracked); the kt review quotes some lines from the cloud branch, which differ by a few lines.
- The deck match is by printing id. Where a deck holds the same name at another printing (Carbink B3b 031 in brew-10, Oricorio B4 078 in deck 10, Cloyster, Corviknight, Archaludon B4 113 and so on) the file says so and does not count it.
- Not run: any engine game. Not read: any Limitless standings file (that is the Lists phase). Not changed: any rule, spec or deck file.
