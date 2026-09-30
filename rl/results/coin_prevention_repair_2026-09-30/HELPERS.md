Decision this informs: which attack helpers the coin-flip prevention repair's part (b) extends to (the Fable coordinator via Dustin, Sept 30: "Extend (b) to a Part 1 helper only where Part 1 confirmed it skips the coin"). This is Part 1, a read-only check: nothing in `engine/` was changed. It is committed before any repair code.

Seeds: the probe below used 20,940,000,000 + i, for i from 0 to 99 (Claude Code's diagnostic block, outside START_HERE's ranges). No table deal was used and no table game was played.

# Part 1: which attack helpers skip the defender's coin

## The question

Four Abilities read "If any damage is done to this Pokémon by attacks, flip a coin":
- Carefree Steps (Meowth B2 124 and B2 204) and Celestial Blessing (Togekiss A4 080): heads prevents the damage;
- Guarded Grill (Bastiodon A2 114): heads, −100;
- Securely Sheltered (Hisuian Goodra B3b 050): heads, −80.

rules/09 (lines 96-114) says the engine flips the coin only for damage carried in the attack's own outcome. So damage an attack deals through a queued `ApplyDamage` choice never flips it. It lists seven helpers in `engine/src/actions/apply_attack_action.rs` that are likely affected.

## How it was checked

1. **The code.** A queued `ApplyDamage` choice is resolved by `forecast_apply_damage` (`apply_action.rs`, about line 768). That flips only a Guts coin, never a prevention coin.
   - The other queued form, `ApplyQueuedAttackDamage`, is resolved by `finish_queued_attack_damage`. That runs the defender's attack modifiers, including the prevention coin.
   - So a helper skips the coin exactly when it queues `ApplyDamage` for damage to an opponent's Pokémon.
2. **A probe** (`probe_coin_helpers.rs`, output in `probe_output.txt`). It ran as a test in a scratch copy of the engine at `31a9dbf`, so nothing in the repository changed.
   - For each helper, a Togekiss sits where the queued damage lands, and the choice is steered at it.
   - Over 100 seeds it counts the runs where Togekiss took none of that damage ("prevented") and where it took some ("hit").
   - A coin that flips shows both. A skipped coin shows "prevented 0".
3. **The cards** (`helpers_census.py`, output in `census_output.txt`). Each helper's Mechanic is traced to the attack texts that map to it (`effect_mechanic_map.rs`), and those to the cards in `engine/database.json`.
   - Then the census checks every deck list under `decks/`: 64 files with card lines, in both line formats ("2 B1 044" and "2 Heatmor B1 044").

## The seven helpers

| helper | skips the coin? | probe (prevented / hit) | cards | in a list under `decks/` |
|---|---|---|---|---|
| `also_choice_bench_damage` | **No** when it damages the opponent's Bench: its choice is `ApplyQueuedAttackDamage`, which flips. **Yes** in the own-Bench form (the attack also damages your own Benched Pokémon): the hit on the opponent's Active is queued as `ApplyDamage` | opponent Bench (Pikachu's Spark): 47 / 53. Own Bench (Zapdos's Raging Thunder), the Active hit: 0 / 100 | Opponent-Bench form: Spark, Aqua Jet, Muddy Water, Jump Kick, Aura Sphere (Lucario ex), Pike, Jump Blues, Piercing Spin, Voltaic Bullet (Raikou ex), Sprinting Flare (Rapidash ex), Jet Punch, Lightning Laser, Aqua Bullet, Shadow Bullet (Hoopa ex), Thunderclaw (Team Rocket's Zapdos ex). Own-Bench form: Raging Thunder (Zapdos A1 103, B1 302; Emolga A4 072), Flash Impact (Luxray B1 088, B1 237, P-B 004) | Opponent-Bench form: Hoopa ex (B4 103), in 7 lists (research/weezing, t-weezing, three gauntlet Weezing variants, brew 07, Dustin's 04). Own-Bench form: none |
| `optional_discard_benched_basic_for_extra_damage` (Chase Order) | **Yes**, both ways: without the discard the choice is `ApplyDamage`, and the discard choice (`DiscardOwnBenchedThenDamage`) queues `ApplyDamage` from `apply_action.rs` (about line 1307) | no discard: 0 / 100. Discard: 0 / 100 (all Knock Outs) | Vespiquen ex (B4 011, B4 180, B4 194) | B4 011 in 4 lists: research/vespiquen, t-vespiquen, two Vespiquen variants (variants-2026-09-23) |
| `discard_all_energy_of_type_then_damage_any_opponent_pokemon` | **Yes** | 0 / 100 | Chien-Pao ex, Diving Icicles (B2a 037, B2a 102, B2a 112, P-B 041); Luxray, Volt Bolt (A2 060) | Chien-Pao ex (B2a 037) in 6 lists: research/suicune, t-suicune, three gauntlet Suicune variants, panel ladder's l-sharpedo |
| `damage_to_any_opponent_per_target_energy` | **Yes** | 0 / 100 | Tapu Lele, Energy Arrow (A3 084, A3 170) | none |
| `self_discard_energy_then_damage_any_opponent_pokemon` | **Yes** | 0 / 100 | Volcarona, Volcanic Ash (A1a 014, P-A 028) | none |
| `switch_in_opponent_benched_then_damage` | **Yes**, for the damage to the Pokémon switched in (queued as `ApplyDamage` before the switch choice). The attack's own damage to the old Active is in the outcome and flips | 0 / 100 | Sandy Shocks, Pull In and Pound (B3a 035); Team Rocket's Hypno, Entrap (B4a 028, B4a 074). Chinchou's Luring Glow (P-A 095) uses it with 0 damage, so nothing is queued | Team Rocket's Hypno (B4a 028) in Dustin's 14 (comfey-raticate-hypno) |
| `direct_damage_if_damaged` | **Yes** | 0 / 100 | Decidueye ex, Pierce the Pain (A3 012, A3 180, A3 198, A4b 042, B1 317); Mandibuzz, Blindside (B3 110) | none |

**rules/09's own example, the `DirectDamage` group** (`direct_damage` and `direct_damage_and_self_card_effect`, both through `push_direct_damage_choices`): **yes, it skips**. Heatmor's Tongue Whip into a Benched Togekiss: 0 / 100.
- Its cards are the 60 printings in `census_output.txt`.
- These are in lists:
  - Heatmor (B1 044): research/blaziken, t-blaziken, Dustin's 06;
  - Hitmonlee (A1 154): research/lucario, t-lucario, three gauntlet Lucario variants;
  - Grovyle (B3 006): research/sceptile, t-sceptile;
  - Absol (A4 120): Dustin's 02;
  - Gabite (B4a 053): Dustin's 08.

## Found outside the seven: the same skip

Every other place an attack queues `ApplyDamage` for damage to the opponent was checked too. Each skips the coin; the probe confirms the first five.

| where | skips | probe | cards | in `decks/` |
|---|---|---|---|---|
| `coin_flip_also_choice_bench_damage` | yes, on the attack's heads (both hits are queued) | 0 / 53 (the other 47 runs were tails, with no queued choice) | Wellspring Mask Ogerpon, Wellspring Dance (B2 048) | none |
| `self_discard_energy_and_choice_bench_damage` | yes (both hits queued) | 0 / 100 | Rapid Strike Urshifu, Tornado Shot (B3 051) | none |
| `conditional_bench_damage_attack` | yes, for the Bench hit | 0 / 100 | Blastoise, Double Splash (B1a 019); Mega Blastoise ex, Triple Bombardment (B1a 020, 078, 084) | none |
| `mega_kangaskhan_ex_double_punching_family` | yes, for the second attack. The card says the attack is used twice, so each is an attack of its own | damage 40 or 120, never 0 or 80: the first punch flips, the second doesn't | Mega Kangaskhan ex (B2 127, 189, 202; B4 231) | none |
| `shuffle_opponent_tools_into_deck_before_damage` | yes | 0 / 100 | Hoopa, Mischievous Ring (B4 077) | none |
| `discard_tools_from_hand_for_damage` (its damage is queued in `apply_action.rs`, `forecast_discard_own_cards_for_attack_damage`) | yes, by the code (not probed) | — | Slowking, Litter (A4a 018) | none |

The rest are left as they are:
- An Ability's damage (`apply_abilities_action.rs`'s `damage_one_opponent`, and `hooks/core.rs`'s `on_evolve` damage) is queued with `is_from_active_attack: false`. It must never flip the coin (rules/09), and it doesn't.
- `also_choice_own_pokemon_damage` damages only the attacker's own Pokémon.

## The defenders

No list under `decks/` holds any of the five coin-Ability printings: Bastiodon A2 114, Togekiss A4 080, Meowth B2 124 and B2 204, and Hisuian Goodra B3b 050.

So in a game between any two of these lists no coin Ability is ever in play. A repair that runs only when a targeted Pokémon has one of these Abilities changes no such game.

## What this means for Part 2 (b)

The permitted files are `attack_outcome.rs`, `hooks/core.rs` and the helpers' own file, `apply_attack_action.rs`.

- **Changed** (confirmed skip, fixable in the helpers' own file):
  - the `DirectDamage` group;
  - `direct_damage_if_damaged`;
  - `discard_all_energy_of_type_then_damage_any_opponent_pokemon`;
  - `damage_to_any_opponent_per_target_energy`;
  - `self_discard_energy_then_damage_any_opponent_pokemon`;
  - `switch_in_opponent_benched_then_damage`.
- **Not changed, because it doesn't skip:** `also_choice_bench_damage` in its opponent-Bench form.
- **Not changed, though it skips: a question for Dustin** (in CLOUD_STATUS.md):
  - **`optional_discard_benched_basic_for_extra_damage` (Chase Order).** Its discard choice queues its damage from `apply_action.rs`, outside the permitted files. Changing only the no-discard choice would leave the two choices disagreeing.
  - **`also_choice_bench_damage` in its own-Bench form.** Its one queued choice carries both hits: the opponent's Active and your own Benched Pokémon. The coin-flipping path handles only the opponent's side, so switching it over would drop a Guts coin (Ursaluna) on your own Bench. The code's own comment keeps it on `ApplyDamage` for that reason.
- **Not changed, outside the seven: a question for Dustin:** the six sites in the table above.
