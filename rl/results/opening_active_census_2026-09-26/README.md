Decision this informs: what the B5 candidate "opening Active choice" should flag, which decks it would move, and which adoption route its footprint puts it on (docs/REVIEW_2026-09-24_direction.md, section 8, the Altaria follow-up; `../altaria_network_divergence_2026-09-26/RESULT.md`).

# Opening Active census (Sept 26)

Code reading and list arithmetic only. No engine game, no build, no engine seed. The two scripts here are plain Python; the checker used about 3 CPU-minutes while B2e's legality scan was running.

## In plain words

- **How the bot picks its first Active today.** kp3 scores each Basic in the opening hand by how the board looks right after setup, and nothing later.
  - A Basic whose attack is free always wins (Igglybuff, Bonsly, Happiny, Munchlax...).
  - Otherwise the Basic with the most HP per point it gives up wins, minus a little for its Retreat Cost.
  - It never looks at Abilities (except through the Retreat Cost or HP they change, such as Bombirdier's from the Bench), attack costs, or what the Pokémon evolves into.
  - That is why Darkrai (100 HP) beats Eevee and Swablu (50 HP each) in Altaria. k3, kq3 and kd3 choose exactly the same way.
  - Checked against the network study's records: this rule fits kp3's choice in all 235 Altaria games, with no contradiction in the 220 where another Basic in the hand is known (215 if kp3's own later setup picks are not counted as known). Predicted counts match: Darkrai 103.4 predicted against 103 seen.
- **The engine already names both properties.** They are mechanic flags, not cards.
  - "Works only from the Active Spot, and pays on the first turn": exactly one flag, `CanEvolveOnFirstTurnIfActive` (Eevee's Boosted Evolution; its text also covers "the turn you play it", which the opening doesn't need).
  - "Keeps working from the Bench": 8 Bench-only flags plus 44 flags that act on other Pokémon from anywhere in play. Bad Dreams is `BadDreamsEndOfTurn`, which the engine reads from every Pokémon in play.
- **Who carries them** (42 lists: the 8 table decks, Dustin's 15, the 13 brews, the 6 B2e lists):
  - The first-turn flag (switch A): Altaria (it would change the opening in 24% of its games) and Dustin's deck 15 (10%). Nothing else.
  - The Bench flags (switch B): Altaria 24%, Hydreigon 13%, Vespiquen 16%, Weezing 7%.
  - B would also change the opening in 4 of Dustin's decks, 6 brews and 1 B2e list. Three more of Dustin's decks (03, 04, 07) carry a B flag, but the switch never changes their opening.
  - The two lists the proposed ladder panel adds (`decks/screen/panel_ladder_2026-09-26/l-charizardy.txt`, `l-sharpedo.txt`) carry neither flag, and no switch changes their opening (second read; the screen's eight opponents are the table lists card for card).
- **How much of the table this touches: 6% of games with switch A alone, 15% with B alone, 17% with both.**
  - The plan's 15% line decides the route. A alone is well under it, so it goes the reserve route. Both together are just over it, so they go the ordinary rule.
  - Section 8 assumed "the choice is made in every game, so the footprint is above the trigger". That is not so. Only hands with a flagged Basic next to another Basic change.
- **What the network studies add.**
  - Altaria: pricing the rule's changes with B2c's own play-outs gives about **+5.5 points per Altaria game against Lucario with switch A, +7.2 with both**.
  - The network's openings follow the rule's order (Igglybuff, then Eevee, then Swablu, then Darkrai) in 220 of 235 games. The exceptions are 12 Eevee-over-Igglybuff openings, worth 0.0 ± 12.8, and 3 Swablu openings with an Eevee in the hand.
  - It does not matter who goes first: +19.4 either way.
  - The network's other setup differences (mostly ending setup with Basics still in hand) are worth +0.9 ± 3.9, indistinguishable from zero.
  - Lucario network: it opens the same Pokémon as k3 in 103 of 105 games. The 2 differences were never played out.
  - Hydreigon network: its records store only move numbers, so its openings can't be read without replaying the games (not done today).
- **What stays uncertain.** B2c can't tell *why* Darkrai should stay on the Bench.
  - It could be Bad Dreams working from there (switch B).
  - Or it could be that Darkrai's attack costs 3 Energy against Swablu's 1 (a "readiness" rule that needs no Ability flags).
  - On the table the two readings agree on Altaria, Vespiquen and Weezing. They differ only on Hydreigon (B moves it, readiness doesn't) and Suicune (readiness moves it, B doesn't).
- **Recommendation in the draft** (`REGISTRATION_DRAFT.md`, not registered):
  - Register switch A alone first, by the reserve route, in the players' code only (tier 2).
  - Run B and the readiness rule as diagnostics, to name the Darkrai half.
  - The route is Dustin's call, and Fable reviews first.

## 1. Files

- `census.py`: the census. It prints `census_output.txt` and writes `census.json`.
  - For every list: each Basic, its mechanic flag and class, its HP, Retreat, knockout points, attack costs and evolution.
  - The exact chance that an opening choice exists, from the list counts under the engine's deal.
  - Which Basic k3/kp3 open today.
  - How often each switch changes that opening, and to what.
  - Also: the table footprint, the B2c-based value for Altaria, and the check against the two network studies' records.
- `check_census.py`: the independent check. Its outputs are `check_census_output.txt` and `check_census.json` (section 7).
- `REGISTRATION_DRAFT.md`: the draft registration.

## 2. How k3 and kp3 choose the setup Active today

**The path, file:line (engine at the working copy's main):**
- **What is offered.** At turn 0 the only moves are placing a Basic from the hand: first into the empty Active Spot, then onto the Bench, or ending setup.
  - `engine/src/move_generation/mod.rs` 30-42 and 140-167.
  - No Trainer can be played at setup (`move_generation_trainer.rs` 52-54).
  - The moves are sorted by their JSON text before the bot sees them (`game.rs` 199-201, `observation.rs` 37-39). For two Place moves, the first difference in that text is the card id.
- **Who places first.** The player chosen by the coin flip (`state/mod.rs` 766) places first. The setup EndTurn hands over to the other player. Turn 1 starts only when both Actives are down, and it belongs to the player who placed first (`actions/apply_action_helpers.rs` 47-80).
- **What the bot can see.** Until both setups are done, the opponent's board is masked (`observation.rs` 48-53, `setup_opponent_hidden`).
- **The kp3 decision.** kp3 is the k search inside the public-pricing wrapper (`players/mod.rs` 502-512; `public_pricing_player.rs` 113-121).
  - The search scores each root move at depth `max_depth − 1` = 2 (`expectiminimax_player.rs` 310-331). So it sees the placement plus two more of its own setup moves.
  - Ending setup is cut off as unpriced: "setup handoff or reveal requires the concealed opponent board" (`observation.rs` 365-367, applied at `expectiminimax_player.rs` 441-454). The search therefore never reaches its own first turn.
  - Every root move at setup is also recorded unpriced: "opponent setup is hidden; only own setup development is scored" (`expectiminimax_player.rs` 313-318).
  - Ties go to the **last** best move in the sorted list, because `Iterator::max_by` returns the last maximum (`expectiminimax_player.rs` 340-350).
- **What the evaluation sees there.** It is the static setup branch of `parametric_value_function_ex6` (`players/value_functions.rs` 459-478). It holds own-board terms only, and nothing about the opponent:
  - Pokémon value: HP × (Energy + 1) summed over the own board (1137-1150). With no Energy that is just HP.
  - Hand size minus deck size. This is the same for every opening.
  - The Active's Retreat Cost, −1 per Energy (640-664, with Bench reducers from `hooks/retreat.rs` 165-194).
  - **500 × the Active's "online score"** (1647-1735, called with `effect_aware = false`).
    - The score is the Energy on the Active over the cost of the lexicographically largest attack of its highest evolution in deck and hand.
    - With no Energy at setup it is 0 for every Basic whose attacks cost something.
    - It is 1.0 when every attack of that form is free (1724-1726).
  - **The Active's "safety"**: HP ÷ knockout points (1633-1642; points from `models/card.rs` 204-216).
  - The online-count and distance terms have weight 0 in the baseline parameters.
- **So kp3's opening is**: the Basic with the largest 500 × [all attacks free] + HP ÷ knockout points − Retreat.
  - Ties go to the Basic with the larger card id.
  - With four or more Basics in hand, the two-move horizon benches the two highest-HP ones left. In the 42 lists here that never reverses this order: the second read's literal search over every deal gives the same opening as the short rule, and `check_census.py`'s sampled literal search agrees within noise. It is not a general law: a Basic outside the hand's three highest-HP Basics loses the HP it keeps off the Bench (for example a non-ex 80 HP Basic against three 150 HP ex, equal Retreat: 80 + 380 against 75 + 450, so the ex opens), so a new list needs the literal search, not the short rule.
  - k3 (`players/mod.rs` 424-432) and kq3/kd3 (514-536) reach the same setup branch before their extra features run (`value_functions.rs` 459 comes before 525-533), so all four open identically.
  - kpr's code is on the cloud branch and was not read.
- **Why Darkrai.** The Altaria list's Basics score:

  | Basic | score |
  |---|---:|
  | Igglybuff (Sleepy Lullaby is free) | 500 + 30 − 0 = **530** |
  | Darkrai | 100 − 2 = **98** |
  | Swablu | 50 − 1 = **49** |
  | Eevee | 50 − 1 = **49** |

  - Eevee and Swablu tie, and Swablu (B1 196) sorts after Eevee (B1 184), so Swablu wins the tie.
  - Nothing in the score sees Boosted Evolution, Bad Dreams, Dark Slumber's 3-Energy cost, or that Swablu and Eevee evolve.
- **Checked against the records** (`census.json` → `validation`; one opening decision per game with two or more Place moves offered, duplicates included):

  | probe | opening decisions | Darkrai | Igglybuff | Swablu | Eevee |
  |---|---|---|---|---|---|
  | Altaria, kp3 probe | 235 seen, 237.7 predicted | 103 / 103.4 | 73 / 81.6 | 56 / 45.3 | 3 / 7.4 |

  | probe | opening decisions | Bonsly | Hitmonlee | Riolu |
  |---|---|---|---|---|
  | Lucario, k3 probe | 105 seen, 99.5 predicted | 52 / 53.0 | 39 / 32.0 | 14 / 14.4 |

  - A sharper test, from the Altaria records: take every Basic known to be in the hand (the network's Active, the Basics it benched at setup, kp3's Active).
    - In none of the 215 informative games does a known Basic outrank kp3's pick under Igglybuff > Darkrai > Swablu > Eevee.
    - Counting also the Basics kp3's probes placed at the later setup decisions of the same games (each is a Basic in that hand), 220 games are informative, still with none.
  - The deal model is exact. It follows `deck.rs` 129-149: five random cards, and a hand with no Basic has one card swapped for a random Basic. Such a hand holds exactly one Basic, so there is no choice.

## 3. The mechanic flags

Each Ability maps from its printed text to one `AbilityMechanic` value (`actions/effect_ability_mechanic_map.rs`: 156 entries, 124 variants; the enum is in `actions/abilities/mechanic.rs`). Where it works is decided in two places:
- the activation gate in `can_use_ability_by_mechanic` (`move_generation/move_generation_abilities.rs` 55-288: `is_active`, `!is_active`, `_in_play_index == 0`, `require_active`), for activated Abilities;
- the hook, for passive ones.

`census.py`'s `VARIANT_CLASS` classifies every mapped variant by where it works. It is keyed on variants and their own fields, never on card names; a new variant stops the script until it is classified. The classes over the 156 map entries, counted as flag settings (a variant whose own fields change its class counts once per setting):

**(a) Works only from the Active Spot**
- **On the owner's first turn: 1 flag.** `CanEvolveOnFirstTurnIfActive` (`mechanic.rs` 549).
  - Its only effect is the evolution-timing exception in `move_generation/mod.rs` 198-212, which checks `i == 0`, the Active Spot.
  - Precisely, the text is "during your first turn or the turn you play it", and the engine lifts both rules (`mod.rs` 209-210: the first-turn rule and `played_this_turn`). For the opening only the first-turn half matters, so the class is "Active-only, pays on the first turn", not "useless after it".
  - It is passive (`move_generation_abilities.rs` 228).
  - Carried by Eevee B1 184 only. The other Eevee-line flag, `CanEvolveIntoEeveeEvolution`, forbids first-turn evolution and is not this.
- **At any time: 26 flags.**
  - Activated with an Active gate: `AttachEnergyFromZoneToYourTypedPokemon` (115-117), `ConfuseOpponentActive` and `PoisonOpponentActive` (174-175), `CopyRandomOpponentHandSupporter` (274-280), `SwitchDamagedOpponentBenchToActive` (90-92), `VictreebelFragranceTrap` (64-66), and `HealOneYourPokemon`, `SwitchOutOpponentActiveToBench` and `DrawCardsOncePerTurn` when `require_active: true`.
  - Passive with a printed Active condition: `EndTurnDrawCardIfActive` and `EndTurnHealSelfIfActive` (`hooks/core.rs` 381-399 read only the Active); `RandomEvolutionFromDeck { EndOfOpponentTurnIfActive }` (`apply_action.rs` 585-593); `CheckupDamageToOpponentActive`; `CheckupDamageToAllOpponentPokemon`; `StartTurnRandomPokemonToHand`; `IncreaseAttackCostForOpponentActive`; `ReduceOpponentActiveDamage`; `ElectromagneticWall`; `NoOpponentSupportInActive`; `NoOpponentStadiumInActive`.
  - The on-damage and on-knockout triggers that print "if this Pokémon is in the Active Spot": `CounterattackDamage`, `PoisonAttackerOnDamaged`, `AttachEnergyFromZoneToBenchOnDamaged`, `DamageOnKnockoutInActive` (`hooks/core.rs` 2192), `CoinFlipToKnockOutAttackerOnKnockout`, `MoveAllTypedEnergyToBenchOnKnockout`.
- **Drawbacks while Active: 2 flags.**
  - `CannotAttackWithoutBenchedNames` (Regigigas: `move_generation/attacks.rs` 155-174).
  - `SleepOnZoneAttachToSelfWhileActive`.

**(b) Keeps working from the Bench**
- **Bench-only: 8 flags.**
  - Gate `!is_active` or its helper: `SwitchThisBenchWithActive` (96), `AttachEnergyFromDiscardToActiveTypedFromBench` (265-273), `MoveFixedDamageFromActiveToThisBenched` (242-244 and 290-301), `DiscardOpponentActiveToolsAndDiscardSelf` (379-387).
  - Printed "on your Bench": `IncreaseDamageForEvolutionsFromBench`, `PreventDamageWhileBenched`, `ReduceRetreatCostOfYourActiveBasicFromBench` and `ReduceRetreatCostOfYourActiveTypedFromBench` (`hooks/retreat.rs` 165-194, which reads the Bench).
- **From anywhere in play, acting on other Pokémon, the opponent or the owner's draws: 44 flags.**
  - `BadDreamsEndOfTurn` is here. `hooks/core.rs` 618-631 collects every in-play holder, Bench included.
  - So are `DamageOpponentActiveOnZoneAttachToSelf` (Darkrai ex's Nightmare Aura; `state/energy.rs` 149-170, any slot), `IncreasePoisonDamage` (`apply_action_helpers.rs` 226-240 counts every in-play Nihilego), `SoothingWind`, `TimeRecall`, `HealActiveYourPokemon`, and the ungated activated Abilities (the gate is only `!card.ability_used`).
- **Not "Bench-working" for switch B**:
  - The 31 self-scoped flags that act only on the holder: its own damage cuts, status immunity, self-charging, own Retreat (for example Shuckle ex's Solid Shell, Arceus ex's Fabled Luster, Giratina ex's self-attach, Oricorio's Safeguard).
  - The 12 on-evolve triggers.
  - The 4 on-Bench-entry triggers (from the hand onto the Bench).
- **Also first-turn, but from anywhere and self-scoped: 2 flags.** `NoRetreatCost { YourFirstTurn }` and `EndFirstTurnAttachEnergyToSelf`. No list in scope carries either.
  - The setup score already reads the first one: `is_users_first_turn()` is `turn_count <= 2` (`state/mod.rs` 1227-1229), true at turn 0, so such a Basic (Wimpod A3 021) is scored with Retreat 0 at setup (`hooks/retreat.rs` 94).

**(c) Anything else the opening choice could read**, and what the bot can see at setup:
- **HP, knockout points and Retreat** are the only things kp3's setup score reads now. HP ÷ points makes it avoid opening an ex or a Mega ex (Mega Absol ex scores 170 ÷ 3 − 1 = 55.7 against Deino's 59).
- **A free attack** is worth 500 and decides every hand that has one: Igglybuff, Bonsly, Happiny, Mantyke, Cleffa, Munchlax. That agrees with the network, which opens Igglybuff when it can.
- **Attack cost.** At setup the online score is 0 for every costed attack, so 1 Energy and 3 Energy look the same. This is the flag-free alternative for the Darkrai half (switch R in `census.json`: −100 per Energy of the Active's cheapest attack).
- **"A Basic that evolves this game."** The highest evolution in deck and hand is looked up (`card_logic/rare_candy.rs` 121-165), but only to pick a cost yardstick, which is 0 at setup. `census.json` records each Basic's evolution in the list.
- **Weakness to the opponent is unknowable at setup for kp3.** The opponent's board is masked (`observation.rs` 48-53), and kp3 has no opponent list. Only the list-sampling tier (b) could guess it, and even b sees no board at setup.
- **Who goes first.**
  - The engine fixes it before setup: the first to place goes first (`state/mod.rs` 766, `apply_action_helpers.rs` 63-77). But the setup observation carries no field for it.
  - It could be inferred from the opponent's hand count. `observation.rs` 56 masks the opponent's hand card by card but keeps its length, so a player placing second sees 5 minus the Pokémon the opponent placed.
  - The setup evaluation doesn't read that, and no new term should. Whether real Pocket shows that count during setup is an open rules question (tier 1, not checked here).
  - B2c says it doesn't matter for this candidate: the differing openings are worth +19.4 ± 6.6 going first and +19.4 ± 6.4 going second.
- **On-Bench-entry triggers** (`LegendaryDrive`, `AncientRoar`, `HealActiveTypedOnBenchFromHand`, `InfiltratingInspection`).
  - `apply_place_card` fires them for setup placements too (`apply_action.rs` 1111-1120 → `hooks/core.rs` 322-354). But move generation ignores the pending stack at turn 0 (`move_generation/mod.rs` 31-42).
  - Whether they may fire at setup at all is an engine rules question (tier 1). No list in scope carries one.
- **Drawbacks.** kp3 opens Regigigas in 16.2% of deck 01's deals: it has the most HP, but it can't attack unless the Regi trio is benched (deck 01 relies on Alolan Muk switching the Ability off). Switch D in `census.json` records it; it is not proposed.

## 4. The census

The table below comes from `census.json`.
- "Opening choice": the chance that the opening hand holds two or more different Basics (by card id).
- "kp3 opens": the chance of a choice *and* that kp3 opens that Basic, both in % of all deals.
- A, B and A+B: the chance that the switch changes kp3's opening, in % of all deals. Both weights are the pre-set 250.
- **A** marks a switch-A carrier and **B** a switch-B carrier.

| list | flagged Basics (mechanic flag; class) | opening choice | kp3 opens, with a choice (% of deals) | A | B | A+B | opening changes under A+B (% of deals) |
|---|---|---:|---|---:|---:|---:|---|
| altaria | 2 Eevee (CanEvolveOnFirstTurnIfActive; Active, first turn) **A**; 2 Darkrai (BadDreamsEndOfTurn; anywhere, board) **B** | 53.9% | Darkrai 24.0, Igglybuff 20.4, Swablu 9.5 | 24.0% | 24.0% | 33.5% | Darkrai → Eevee 14.5; Darkrai → Swablu 9.5; Swablu → Eevee 9.5 |
| blaziken | - | 21.3% | Heatmor 13.3, Castform Sunny Form 8.0 | 0 | 0 | 0 | - |
| hydreigon | 1 Bombirdier (ReduceRetreatCostOfYourActiveTypedFromBench; Bench) **B** | 21.3% | Bombirdier 13.3, Deino 8.0 | 0 | 13.3% | 13.3% | Bombirdier → Deino 9.7; → Mega Absol ex 3.6 |
| lucario | - | 21.3% | Bonsly 13.3, Hitmonlee 8.0 | 0 | 0 | 0 | - |
| sceptile | 2 Caterpie (RandomEvolutionFromDeck EndOfOpponentTurnIfActive; Active, any turn) | 9.7% | Treecko 9.7 | 0 | 0 | 0 | - |
| suicune | 2 Suicune ex (EndTurnDrawCardIfActive; Active, any turn) | 33.7% | Suicune ex 24.2, Chien-Pao ex 6.6, Frigibax 2.9 | 0 | 0 | 0 | - |
| vespiquen | 2 Shuckle ex (ReduceDamageFromAttacks; self); 1 Teal Mask Ogerpon ex (SoothingWind; anywhere, board) **B** | 30.7% | Ogerpon ex 16.2, Shuckle ex 14.5 | 0 | 16.2% | 16.2% | Ogerpon ex → Shuckle ex 9.7; → Combee 6.6 |
| weezing | 1 Darkrai ex (DamageOpponentActiveOnZoneAttachToSelf; anywhere, board) **B** | 30.7% | Hoopa ex 24.2, Darkrai ex 6.6 | 0 | 6.6% | 6.6% | Darkrai ex → Team Rocket's Koffing 6.6 |
| 01 Muk Glimmora Kingambit Regigigas | 1 Regigigas (CannotAttackWithoutBenchedNames; Active drawback) | 33.7% | Regigigas 16.2, Alolan Grimer 10.9, Glimmet 6.6 | 0 | 0 | 0 | - |
| 02 Arceus Crobat | 2 Arceus ex (ImmuneToStatusConditions; self) | 43.6% | Munchlax 18.5, Absol 13.3, Arceus ex 11.8 | 0 | 0 | 0 | - |
| 03 Wailord Indeedee | 2 Indeedee ex (HealActiveYourPokemon; anywhere, board) **B** | 17.6% | Wailmer 17.6 | 0 | 0 | 0 | - (Wailmer already opens) |
| 04 Absol Hoopa Darkrai | 1 Darkrai ex **B**; 1 Bombirdier **B** | 55.7% | Hoopa ex 24.0, Happiny 20.4, Absol 9.5, Bombirdier 1.8 | 0 | 0 | 0 | - (both B carriers penalised alike) |
| 05 Indeedee Stoutland | 2 Indeedee ex (HealActiveYourPokemon) **B** | 17.6% | Indeedee ex 17.6 | 0 | 17.6% | 17.6% | Indeedee ex → Lillipup 17.6 |
| 06 Mega Blaziken | - | 21.3% | Heatmor 13.3, Castform 8.0 | 0 | 0 | 0 | - |
| 07 Skarmory stall | 1 Indeedee ex **B** | 9.7% | Skarmory ex 9.7 | 0 | 0 | 0 | - |
| 08 Garchomp toolbox | 1 Celebi (TimeRecall; anywhere, board) **B** | 21.3% | Munchlax 13.3, Celebi 8.0 | 0 | 8.0% | 8.0% | Celebi → Gible 8.0 |
| 09 Mega Manectric | - | 17.6% | Electrike 17.6 | 0 | 0 | 0 | - |
| 10 Xatu Oricorio TR Weezing | - | 30.7% | Oricorio 24.2, TR Koffing 6.6 | 0 | 0 | 0 | - |
| 11 Archaludon Haxorus Dragonair | - | 30.7% | Duraludon 16.2, Axew 14.5 | 0 | 0 | 0 | - |
| 12 Ariados Whimsicott Ogerpon | 1 Teal Mask Ogerpon ex **B** | 30.7% | Ogerpon ex 16.2, Spinarak 14.5 | 0 | 16.2% | 16.2% | Ogerpon ex → Spinarak 9.7; → Cottonee 6.6 |
| 13 A-Ninetales Raticate | - | 17.6% | Alolan Vulpix 17.6 | 0 | 0 | 0 | - |
| 14 Comfey Raticate Hypno | 1 Comfey (SoothingWind) **B** | 30.7% | Comfey 16.2, TR Drowzee 14.5 | 0 | 16.2% | 16.2% | Comfey → TR Drowzee 9.7; → TR Rattata 6.6 |
| 15 Jolteon Oricorio Raticate | 2 Eevee B1 184 **A**; 1 Oricorio (PreventAllDamageFromEx; self) | 30.7% | Oricorio 16.2, Eevee 14.5 | 9.7% | 0 | 9.7% | Oricorio → Eevee 9.7 |
| brew-01 Arceus Crobat Xatu | 2 Arceus ex (self) | 41.3% | Arceus ex 29.5, Natu 11.8 | 0 | 0 | 0 | - |
| brew-02 Arceus Tandemaus Persian | 2 Arceus ex (self) | 41.3% | Arceus ex 29.5, TR Meowth 11.8 | 0 | 0 | 0 | - |
| brew-03a Arceus Nihilego Toxapex | 2 Arceus ex (self); 2 Nihilego (IncreasePoisonDamage) **B** | 41.3% | Nihilego 29.5, Arceus ex 11.8 | 0 | 29.5% | 29.5% | Nihilego → Arceus ex 17.6; → Mareanie 11.8 |
| brew-03b Arceus Crobat Nihilego Toxapex | 2 Arceus ex (self); 1 Nihilego **B** | 53.9% | Arceus ex 24.0, Nihilego 20.4, Mareanie 9.5 | 0 | 20.4% | 20.4% | Nihilego → Arceus ex 9.7; → Mareanie 6.6; → Zubat 4.2 |
| brew-04 Xatu Slowking | - | 30.7% | TR Slowpoke 24.2, TR Koffing 6.6 | 0 | 0 | 0 | - |
| brew-05 Meowstic Hatterene | - | 17.6% | Hatenna 17.6 | 0 | 0 | 0 | - |
| brew-05b Meowstic Hatterene Comfey | 1 Comfey **B** | 30.7% | Comfey 16.2, Hatenna 14.5 | 0 | 16.2% | 16.2% | Comfey → Hatenna 9.7; → Espurr 6.6 |
| brew-06 Pyukumuku Silvally Payback | 2 Pyukumuku (DamageOnKnockoutInActive; Active, any turn); 1 Comfey **B** | 53.9% | TR Mewtwo 33.7, Type: Null 16.0, Comfey 4.2 | 0 | 4.2% | 4.2% | Comfey → Pyukumuku 4.2 |
| brew-06b Pyukumuku Silvally Scyther | 2 Pyukumuku (Active, any turn); 1 Ogerpon ex **B** | 53.9% | Type: Null 33.7, Ogerpon ex 10.7, TR Scyther 9.5 | 0 | 10.7% | 10.7% | Ogerpon ex → TR Scyther 6.6; → Pyukumuku 4.2 |
| brew-07 Hoopa Darkrai Sableye | 1 Darkrai ex **B** | 21.3% | Hoopa ex 17.6, Darkrai ex 3.6 | 0 | 3.6% | 3.6% | Darkrai ex → Mega Sableye ex 3.6 |
| brew-08 Entei Rainbow Cave | 2 Entei ex (EndTurnDrawCardIfActive; Active, any turn) | 0 (Entei ex is the only Basic) | - | 0 | 0 | 0 | - |
| brew-09 Sableye Obstagoon | - | 17.6% | Galarian Zigzagoon 17.6 | 0 | 0 | 0 | - |
| brew-10 Diancie Giratina | 2 Giratina ex (AttachEnergyFromZoneToSelfAndEndTurn; self) | 41.3% | Giratina ex 29.5, Mega Diancie ex 11.8 | 0 | 0 | 0 | - |
| h-charizardy_entei | 2 Entei ex (Active, any turn) | 17.6% | Charmander 17.6 | 0 | 0 | 0 | - |
| h-garchomp | - | 36.6% | Happiny 16.2, Mantyke 10.9, Cleffa 6.6, Gible 2.9 | 0 | 0 | 0 | - |
| h-hoopa_absol | 1 Darkrai ex **B** | 21.3% | Hoopa ex 17.6, Darkrai ex 3.6 | 0 | 3.6% | 3.6% | Darkrai ex → Mega Absol ex 3.6 |
| h-manectric | - | 9.7% | Electrike 9.7 | 0 | 0 | 0 | - |
| h-raticate | - | 17.6% | Alolan Vulpix 17.6 | 0 | 0 | 0 | - |
| h-whimsicott | - | 30.7% | Pheromosa 16.2, Spinarak 14.5 | 0 | 0 | 0 | - |

**How to read it.** An opening choice exists in 10% (Sceptile, Skarmory, h-manectric) to 56% (deck 04) of deals, and in 54% for Altaria. With two or more Basic *cards* (duplicates included) it is 59% for Altaria; that is the count the network study's records use.

**The predictions, made before any table**:
- **Switch A** touches Altaria and Dustin's deck 15 only.
- **Switch B** touches Altaria, Hydreigon, Vespiquen and Weezing on the table; Dustin's decks 05, 08, 12 and 14; brews 03a, 03b, 05b, 06, 06b and 07; and h-hoopa_absol.
- **Carriers of an Active-only Ability that is not first-turn**: Sceptile's Caterpie, Suicune ex, Entei ex (in the B2e Charizard-Entei list) and brew-06/06b's Pyukumuku. They are **not** moved by A or B.
  - kp3 opens Suicune ex anyway. It opens Treecko over Caterpie, Charmander over Entei ex, and TR Mewtwo or Type: Null over Pyukumuku.
  - A broader switch C (every non-drawback Active-only flag, +250) would change those: Sceptile 9.7%, h-charizardy_entei 17.6%, brews 06/06b 33.7%. That is reported only (`census.json`, key C). It is not proposed, because nothing measured supports it yet.

**The table footprint** (`census.json` → `table_footprint`). The switches act only in the setup evaluation (`value_functions.rs` 459-478 runs only while `setup_opponent_hidden`). Once the Active is down, every bench placement and the end of setup score the same as under kp3. So a game's play differs from kp3's exactly when either deck's opening Active changes: 1 − (1 − p₁)(1 − p₂) per pairing, averaged over the 28 pairings.

| switches | share of table games whose play differs from kp3's | against the 15% trigger |
|---|---:|---|
| A | **6.0%** (Altaria's 7 pairings only) | under: reserve route |
| B | 14.6% | just under (sampling ±0.6 at 14,000 games) |
| A+B | **16.8%** | over: ordinary rule |
| R (readiness alternative) | 17.1% | over |
| A+R | 19.3% | over |

## 5. The network studies

**Altaria (B2c, `../altaria_network_divergence_2026-09-26/decisions.jsonl`).**
- **What the rule's changes are worth.** B2c's values per changed opening: Eevee over Darkrai +27.0 ± 7.8, Eevee over Swablu +16.1 ± 8.5, Swablu over Darkrai +18.6 ± 8.0. Weighted by the census's transition shares, the switches would be worth, per Altaria game against kp3's Lucario (kp3 continuing on both decks, as in B2c):
  - **A: +5.5 (± 1.4 from the play-outs alone)**;
  - B: +5.3 (± 1.4);
  - **A+B: +7.2 (± 1.6)**.
  - `census.json` → `b2c_expected_altaria_v_lucario`. B2c measured nothing for other opponents.
- **The network's own openings.**
  - 220 of 235 fit the order Igglybuff > Eevee > Swablu > Darkrai, the order A+B produces. The rest: 12 Eevee over Igglybuff (+0.0 ± 12.8, not worth copying) and 3 Swablu openings with an Eevee in the hand (game 169, where the network benched the Eevee; games 138 and 180, where kp3's probe at a later setup decision placed an Eevee the network kept in hand). Counting only the Basics the network placed, as the first draft did, gives 222 and 1.
  - A+B changes 33.5% of Altaria's openings; the network differed from kp3 in 39.5% (158 of 400), or 36.5% without the Igglybuff cases.
- **Does the Eevee gain run through Boosted Evolution?** (second read, descriptive, from the same records.) Of the network's 120 Eevee openings, its Active Eevee evolved on its own first turn in 72.
  - Where it did: Eevee over Darkrai +33.7 ± 9.9 (33 games), Eevee over Swablu +27.9 ± 9.2 (30).
  - Where it didn't: +17.4 ± 12.0 (23) and −2.6 ± 12.9 (19).
  - So the Eevee-over-Swablu value, which only switch A can produce, sits in the games where the first-turn evolution happened. This splits on something after the opening (mostly whether the evolution card was in hand), so it is support for A's mechanism, not a test.
- **Going first or second.** All differing openings: +19.4 ± 6.6 going first (69) and +19.4 ± 6.4 going second (89). Eevee over Darkrai: +28.7 and +25.4. Eevee over Swablu: +18.1 and +14.9. So Boosted Evolution pays either way, and the rule doesn't need to know who goes first.
- **The other setup decisions** (316 bench-or-end decisions at turn 0):
  - 85 differ, 13 of them only in order.
  - The 72 played out are worth **+0.9 ± 3.9** together. The biggest group is kp3 benching Swablu where the network ends setup: −1.0 ± 6.0, 37 positions.
  - In 136 setup decisions both benched Darkrai. The difference is which Pokémon goes Active, not what goes on the Bench.

**Lucario (the Sept 25 B2c, k3 probe, `../lucario_network_divergence_2026-09-25/decisions.jsonl`).**
- 105 games had two or more Place moves at the opening.
- The network opened the same Pokémon as k3 in 103: Bonsly 52, Hitmonlee 37, Riolu 14.
- In 2 (deals 106 and 394) it opened Riolu where k3 opened Hitmonlee. The Lucario tool read both as "order only", because its labels didn't mark the Active slot and the network benched Hitmonlee later. So they were never played out and have no value.
- The Lucario list carries no flagged Basic. No opening blind spot shows there.

**Hydreigon (`../hydreigon_network_readout/`).**
- `readout_nvn_games.jsonl` and `kp3_rows_games.jsonl` store each game's move numbers only, and the readout has no decision-level study. So the network's openings can't be named without replaying the deals in the engine; this census plays no games.
- A replay-only pass would answer it in seconds of CPU: no probes, no play-outs, reading `Place(_, 0)` at turn 0.
- What the census predicts there: kp3 opens Bombirdier in 13.3% of Hydreigon's deals (70 HP beats Deino's 60 and Mega Absol ex's 170 ÷ 3). Bombirdier's Villainous Delivery works only from the Bench. So a Hydreigon network that learned the same lesson would open Deino or Mega Absol ex in those hands.

## 6. Design options (card-agnostic)

1. **Setup-evaluation flag terms (tier 2; recommended).**
   - **Where:** the setup branch of `value_functions.rs` (459-478), behind new `EvalFeatures` switches. It reads `get_in_play_ability_mechanic` (suppression-aware) for the own Active only.
   - **Switch A:** +250 when the Active's flag is in the first-turn Active-only class and `get_highest_evolutions` finds an evolution in own deck and hand.
   - **Switch B:** −250 when the flag is Bench-only or board-scoped from anywhere.
   - The classes live in one players-side function: an exhaustive `match` over `AbilityMechanic` with no wildcard arm, so a new variant fails to compile until it is classified. Its test checks every map entry against the printed-condition phrases (section 7).
   - **What stays untouched:** the engine's setup path (what is offered, the handoff, the setup mask).
   - **Weights:** pre-set, the kq precedent. The predictions above hold for any A weight from 50 to about 460 and any B weight of 50 or more.
     - Checked by re-running the census at 51/51, 51/2000, 480/51, 49/250, 482/250 and 250/49. Only the runs with A at 480 or more, or either weight at 49, change anything, and only in Altaria.
     - Above about 460, Eevee starts to beat Igglybuff in hands with four or more Basics.
   - **Risks:**
     - B's mechanism is not identified (section 5), and B moves Hydreigon, Vespiquen and Weezing with no evidence at all.
     - The class table is hand-written over 124 variants. It is a mechanic list, not a card list, but it can still be wrong; the checker agrees on all but one reading.
     - A fixed weight is a guess until B3 fits it.
2. **Setup readiness term, no Ability flags (tier 2; the alternative for the Darkrai half).**
   - **Where:** the same branch. −100 per Energy of the Active's cheapest attack.
   - **What it reproduces:** A+R gives the same Altaria transitions as A+B.
   - **Where it differs from B:** Hydreigon is untouched, and Suicune ex → Chien-Pao ex or Frigibax in 24.2% of Suicune's deals. It also reaches 8 of Dustin's lists and brews that B doesn't touch: decks 01, 02, 03, 11 and 15, and brews 01, 02 and 10 (key R).
   - **Risks:** a broader footprint (17.1%), and it cannot explain Eevee over Swablu (equal cost), so it needs switch A anyway.
   - Its best use: a diagnostic beside B, to name the Darkrai half.
3. **Engine-side classification or a first-turn lookahead (tier 1 for the engine part, and separate).**
   - **(a)** Move the classes into the engine as `AbilityMechanic` methods (`works_from()`, `first_turn_only()`, `scope()` in `actions/abilities/mechanic.rs`), tested against every map entry, and have option 1 read them.
     - One source of truth beside the mechanics, but it is engine code: tier 1, second reader.
   - **(b)** Let setup search into its own first turn.
     - The cutoff that stops it is in `observation.rs` 365-367, shared by every player, so changing it is tier 1. A players-only version would have to invent an opponent Active, because `forecast_end_turn` needs both Actives (`apply_action_helpers.rs` 50-61).
     - Even then, depth 3 would see Boosted Evolution only when the evolution is in hand, and would never reach a Sleep turn where Bad Dreams pays.
     - Highest cost, least likely to capture the gain. Not proposed.

## 7. The independent check (`check_census.py`, outputs `check_census_output.txt`, `check_census.json`)

Written without calling `census.py`'s code.

**Flags.**
- The checker classifies each carried Ability from its printed text alone (phrases: "is in the Active Spot", "is on your Bench", "first turn", "from your hand onto your Bench", "to evolve", "can't attack"; plus a crude self/board word list).
- It agrees with the variant table on the position and first-turn class of all 156 map entries but one.
  - The one: `CanEvolveIntoEeveeEvolution`, whose text mentions "first turn" only to *forbid* evolving then. The variant table is right.
- On the 42 lists' carriers it disagrees on two self/board scopes, both from its crude word rule:
  - Caterpie's Quick Growth evolves only itself ("from your deck" tripped the rule);
  - Oricorio's Safeguard protects only itself ("your opponent's Pokémon ex" tripped it).
  - The engine's effects act on the holder only in both, so the census's "self" stands.

**Openings.**
- The checker plays the engine's deal literally, 40,000 deals per list. It picks the opening by a literal depth-3 search over its own setup moves, scoring leaves term by term as in `value_functions.rs` 459-478, with Bench retreat reducers applied only when actually benched.
- The opening-choice rate, kp3's opening shares and the A, B and A+B change rates all match `census.json` within Monte Carlo noise: worst |z| 1.29 over 41 lists.
- The 42nd, deck 15, matches on A. It differs on B only because of the checker's Oricorio scope reading above.
- The check covered A, B and A+B; switches C, D and R come from the same code and were not re-derived.

## 8. Limits

- **Where the value numbers come from.** Only Altaria v Lucario has play-out values (B2c, kp3 continuing), so "+5.5 / +7.2" is for that matchup only. Other cells' signs and sizes are untested.
- **What the census assumes.** kp3 as the base pilot, the lists as they are in the repo today, and the engine at the working copy.
  - kpr's cloud code was not read.
  - The six B2e lists were read from `../b2e_card_check_2026-09-26/decks/`.
- **Retreat reducers.** The census's own scorer applies a Bench retreat reducer whenever it is in the hand. The checker applies it only when benched, and they agree on every list.
- **The Hydreigon network's openings are unread** (section 5).
- **An open engine repair touches Bad Dreams:** "Bad Dreams stopped by by-attacks protections" is on the tier 1 repair list (`docs/REVIEW_2026-09-24_direction.md`, section 8, the cloud's paste). It can change what Bad Dreams is worth against some decks, not where it works from, so switch B's class stands; B2c's Darkrai values were measured on the engine as it is.
- **Not counted here:** how often Limitless "Mega Altaria ex Espeon" lists carry Eevee B1 184. The reserve route's clause (d) needs it (`REGISTRATION_DRAFT.md`).
  - Partial pointer only: the two archetype variant lists already on file (`decks/variants-2026-09-23/altaria_jlng_pmpt44_2026-08-29.txt`, `altaria_lanora_blockdragon_2026-09-10.txt`) both carry 2 Eevee B1 184. Switch A would change 24.0% and 16.0% of their openings. This is not the development-half count.
- **Nothing is committed.** Files were written only under this folder.

## 9. Second read (Sept 26, same day)

A second session re-traced section 2 line by line in the engine source, re-derived the flag of every Basic in the 42 lists from `engine/src/database.rs` and the mechanic map (not from `lib/deckgym-database.json` or `census.py`), and recounted every list exactly with its own literal search over the own setup moves (bench choices enumerated, Bench reducers only when benched). No game, no build.
- **Agrees:** the setup path and its line numbers; the 18 flagged Basics and their classes; every list's choice rate, kp3 openings and the A, B, A+B, C, D, R and A+R change rates and transitions; the footprints (A 6.0%, B 14.55%, A+B 16.8%, R 17.1%); the weight ranges (A 50 to 460, B 50 or more); the B2c figures (+19.4 ± 4.6, going first and second, +0.9 ± 3.9, −1.0 ± 6.0 over 37, 136 both-Darkrai); the Lucario records; the scoreboard v2 misses.
- **Corrected here:**
  - `census.json` and `census_output.txt`: Suicune's R and A+R transition "Suicune ex → Frigibax" was 6.6%; it is 14.5%. The list has two Frigibax printings (B2a 034, P-B 037), and `census.py` keyed the transitions by name, so the second printing overwrote the first (8.0% was dropped). `census.py` now sums by name; nothing else in `census.json` changed. `REGISTRATION_DRAFT.md` section 5 is corrected to match.
  - Section 2: the horizon "never reverses" the order only in these 42 lists, not in general.
  - Sections 2, 3 and 5: 220 games are informative for kp3's rule (0 contradictions either way); Boosted Evolution's exact scope; the network's order fits 220 games, not 222.
  - The plain-words summary: the setup score does read Abilities that change a Retreat Cost or HP.
- **Added:** the ladder panel's two lists (plain words), the Wimpod note (section 3), the first-turn-evolution split of B2c's Eevee openings (section 5), the Altaria variant lists and the Bad Dreams repair item (section 8), and in `REGISTRATION_DRAFT.md` the parse order of `ko` after `koa`/`kob`/`kor` and per-deck caps for the diagnostics.
