use core::panic;
use std::vec;

use log::debug;

use crate::{
    actions::{
        abilities::{
            AbilityMechanic, AttackCostReductionScope, DiscardSearchKind, DiscardSelection,
            KnockoutDamageTarget, ARCEUS_NAMES,
        },
        card_effect_from_ability_mechanic, get_ability_mechanic, get_entering_play_ability_mechanic,
        get_in_play_ability_mechanic, handle_damage_only, has_any_in_play_ability,
        has_in_play_ability_mechanic, SimpleAction,
    },
    card_ids::CardId,
    effects::{CardEffect, DamageReductionScope, TurnEffect},
    models::{Card, EnergyType, PlayedCard, TrainerCard, TrainerType, BASIC_STAGE},
    stadiums::{
        get_arena_of_antiquity_damage_bonus, get_training_area_damage_bonus,
        is_bounded_field_active, is_hiking_trail_active, is_soothing_shore_active,
    },
    tools::{has_tool, tool_count},
    State,
};

fn is_fossil(trainer_card: &TrainerCard) -> bool {
    trainer_card.trainer_card_type == TrainerType::Fossil
}

const ANCIENT_POKEMON_NAMES: [&str; 11] = [
    "Brute Bonnet",
    "Slither Wing",
    "Scream Tail",
    "Flutter Mane ex",
    "Great Tusk",
    "Sandy Shocks",
    "Koraidon ex",
    "Roaring Moon",
    "Walking Wake",
    "Gouging Fire",
    "Raging Bolt",
];

pub fn is_ancient_pokemon(pokemon_name: &str) -> bool {
    ANCIENT_POKEMON_NAMES.contains(&pokemon_name)
}

const FUTURE_POKEMON_NAMES: [&str; 11] = [
    "Iron Moth",
    "Iron Bundle ex",
    "Iron Hands",
    "Iron Thorns",
    "Miraidon ex",
    "Iron Valiant",
    "Iron Leaves",
    "Iron Boulder",
    "Iron Crown",
    "Iron Jugulis",
    "Iron Treads",
];

pub fn is_future_pokemon(pokemon_name: &str) -> bool {
    FUTURE_POKEMON_NAMES.contains(&pokemon_name)
}

// Ultra Beasts
// TODO: Move this to a field in PokemonCard and database in the future
const ULTRA_BEAST_NAMES: [&str; 14] = [
    "Buzzwole ex",
    "Blacephalon",
    "Kartana",
    "Pheromosa",
    "Xurkitree",
    "Nihilego",
    "Guzzlord ex",
    "Poipole",
    "Naganadel",
    "Stakataka",
    "Celesteela",
    "Dawn Wings Necrozma",
    "Dusk Mane Necrozma",
    "Ultra Necrozma",
];

pub fn is_ultra_beast(pokemon_name: &str) -> bool {
    ULTRA_BEAST_NAMES.contains(&pokemon_name)
}

pub fn to_playable_card(card: &crate::models::Card, played_this_turn: bool) -> PlayedCard {
    let base_hp = match card {
        Card::Pokemon(pokemon_card) => pokemon_card.hp,
        Card::Trainer(trainer_card) => {
            if is_fossil(trainer_card) {
                40
            } else {
                panic!("Unplayable Trainer Card: {:?}", trainer_card);
            }
        }
        Card::Unknown => panic!("Unknown card cannot be played"),
    };
    PlayedCard::new(card.clone(), 0, base_hp, vec![], played_this_turn, vec![])
}

pub(crate) fn get_stage(played_card: &PlayedCard) -> u8 {
    match &played_card.card {
        Card::Pokemon(pokemon_card) => pokemon_card.stage,
        Card::Trainer(trainer_card) => {
            if is_fossil(trainer_card) {
                BASIC_STAGE // Fossils are considered basic for stage purposes
            } else {
                panic!("Trainer cards do not have a stage")
            }
        }
        Card::Unknown => panic!("Unknown card cannot be in play"),
    }
}

/// Whether `base_pokemon`, already in play, may be evolved into `evolution_card`.
///
/// On top of the printed rule (`Card::can_evolve_into`) this applies Eevee's Veevee 'volve
/// ("this Pokémon can evolve into any Pokémon that evolves from Eevee"), which is an *Ability* and
/// therefore needs the board: Power of Alchemy (Alolan Muk) switches off Basic Pokémon's
/// Abilities, and every printing of Veevee 'volve is on a Basic.
pub(crate) fn can_evolve_into(
    state: &State,
    evolution_card: &Card,
    base_pokemon: &PlayedCard,
) -> bool {
    if base_pokemon.card.can_evolve_into(evolution_card) {
        return true;
    }
    matches!(
        get_in_play_ability_mechanic(state, base_pokemon),
        Some(AbilityMechanic::CanEvolveIntoEeveeEvolution)
    ) && matches!(evolution_card, Card::Pokemon(p) if p.evolves_from.as_deref() == Some("Eevee"))
}

/// Called when a Pokémon evolves
pub(crate) fn on_evolve(
    actor: usize,
    state: &mut State,
    to_card: &Card,
    in_play_idx: usize,
    from_hand: bool,
) {
    if !from_hand {
        return;
    }

    // Raw lookup: `to_card` is an evolution card being played from hand, so it is never a Basic
    // and Power of Alchemy can never apply to it.
    match get_ability_mechanic(to_card) {
        Some(AbilityMechanic::DrawCardsOnEvolve { amount }) => {
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::DrawCard {
                        amount: *amount as u8,
                    },
                    SimpleAction::Noop,
                ],
            ));
        }
        Some(AbilityMechanic::HealTypedPokemonOnEvolve {
            energy_type,
            amount,
        }) => {
            let possible_moves: Vec<SimpleAction> = state
                .enumerate_in_play_pokemon(actor)
                .filter(|(_, pokemon)| {
                    pokemon.is_damaged() && state.pokemon_is_type(pokemon, *energy_type)
                })
                .map(|(in_play_idx, _)| SimpleAction::Heal {
                    in_play_idx,
                    amount: *amount,
                    cure_status: false,
                })
                .chain(std::iter::once(SimpleAction::Noop))
                .collect();

            if possible_moves.len() > 1 {
                state.move_generation_stack.push((actor, possible_moves));
            }
        }
        Some(AbilityMechanic::AttachEnergyFromZoneToActiveTypedOnEvolve { energy_type }) => {
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::Attach {
                        attachments: vec![(1, *energy_type, 0)],
                        is_turn_energy: false,
                    },
                    SimpleAction::Noop,
                ],
            ));
        }
        Some(AbilityMechanic::DamageOpponentActiveOnEvolve { amount }) => {
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::ApplyDamage {
                        attacking_ref: (actor, 0),
                        targets: vec![(*amount, (actor + 1) % 2, 0)],
                        is_from_active_attack: false,
                    },
                    SimpleAction::Noop,
                ],
            ));
        }
        Some(AbilityMechanic::PutCardsFromDiscardToHandOnEvolve {
            card_kind,
            selection,
        }) => offer_put_cards_from_discard_to_hand(actor, state, *card_kind, *selection),
        Some(AbilityMechanic::OpponentShuffleHandAndDrawOnEvolve) => {
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::OpponentShuffleHandAndDrawRemainingPoints,
                    SimpleAction::Noop,
                ],
            ));
        }
        Some(AbilityMechanic::CoinFlipParalyzeOpponentActiveOnEvolve) => {
            offer_on_evolve_ability(actor, state, in_play_idx);
        }
        Some(AbilityMechanic::PoisonAndBurnOpponentActiveOnEvolve) => {
            if state.maybe_get_active((actor + 1) % 2).is_some() {
                offer_on_evolve_ability(actor, state, in_play_idx);
            }
        }
        Some(AbilityMechanic::MoveRandomEnergyFromOpponentActiveToSelfOnEvolve) => {
            let opponent = (actor + 1) % 2;
            if state
                .maybe_get_active(opponent)
                .is_some_and(|active| !active.attached_energy.is_empty())
            {
                offer_on_evolve_ability(actor, state, in_play_idx);
            }
        }
        // §47 — Samurott's shield is always worth offering; Raticate's peek is only worth
        // offering when there is a deck left to look at.
        Some(AbilityMechanic::PreventAllDamageAndEffectsOnEvolve { .. }) => {
            offer_on_evolve_ability(actor, state, in_play_idx);
        }
        Some(AbilityMechanic::LookAtTopCardsPutTrainerTypeToHandOnEvolve { .. }) => {
            if !state.decks[actor].cards.is_empty() {
                offer_on_evolve_ability(actor, state, in_play_idx);
            }
        }
        Some(AbilityMechanic::DiscardRandomEnergyFromOpponentActiveOnEvolve) => {
            let opponent = (actor + 1) % 2;
            let has_energy = state
                .maybe_get_active(opponent)
                .is_some_and(|active| !active.attached_energy.is_empty());
            if has_energy {
                state.move_generation_stack.push((
                    actor,
                    vec![
                        SimpleAction::DiscardRandomOpponentActiveEnergy,
                        SimpleAction::Noop,
                    ],
                ));
            }
        }
        _ => {}
    }
}

/// "You may put <selection> `card_kind` card(s) from your discard pile into your hand" — Delcatty's
/// Search for Friends and Galarian Perrserker's Dig Up.
///
/// Both are a "may", so the offer always carries a `Noop`; the difference is who picks:
/// `PlayerChoosesOne` turns every distinct eligible card into its own option (duplicate copies of
/// the same card are the same decision, so they collapse), while `RandomCards` offers a single
/// action whose forecast branches over the possible draws. Nothing is pushed when the pile holds no
/// eligible card, so the evolve resolves without stopping to ask an empty question.
fn offer_put_cards_from_discard_to_hand(
    actor: usize,
    state: &mut State,
    card_kind: DiscardSearchKind,
    selection: DiscardSelection,
) {
    let mut seen = std::collections::HashSet::new();
    let eligible = || {
        state.discard_piles[actor]
            .iter()
            .filter(|card| card_kind.matches(card))
    };
    let mut choices: Vec<SimpleAction> = match selection {
        DiscardSelection::PlayerChoosesOne => eligible()
            .filter(|card| seen.insert((*card).clone()))
            .map(|card| SimpleAction::PutCardFromDiscardToHand { card: card.clone() })
            .collect(),
        DiscardSelection::RandomCards(amount) => eligible()
            .next()
            .map(|_| SimpleAction::PutRandomCardsFromDiscardToHand { card_kind, amount })
            .into_iter()
            .collect(),
    };
    if choices.is_empty() {
        return;
    }
    debug!(
        "On-evolve discard search: offering {} option(s)",
        choices.len()
    );
    choices.push(SimpleAction::Noop);
    state.move_generation_stack.push((actor, choices));
}

/// Offers an optional on-evolve ability as a `UseAbility` / `Noop` choice. The ability's own
/// logic (including any coin flip) then runs through the regular `forecast_ability` pathway.
fn offer_on_evolve_ability(actor: usize, state: &mut State, in_play_idx: usize) {
    state.move_generation_stack.push((
        actor,
        vec![SimpleAction::UseAbility { in_play_idx }, SimpleAction::Noop],
    ));
}

/// Called when a basic Pokémon is placed from hand onto the bench (index > 0).
pub(crate) fn on_bench_from_hand(actor: usize, state: &mut State, card: &Card, bench_idx: usize) {
    match get_entering_play_ability_mechanic(state, card) {
        Some(AbilityMechanic::LegendaryDrive) => {
            if state.maybe_get_active(actor).is_none() {
                return;
            }
            debug!("Legendary Drive: offering switch to active");
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::UseAbility {
                        in_play_idx: bench_idx,
                    },
                    SimpleAction::Noop,
                ],
            ));
        }
        Some(AbilityMechanic::AncientRoar) => {
            let opponent = (actor + 1) % 2;
            if state.enumerate_bench_pokemon(opponent).next().is_none() {
                return;
            }
            debug!("Ancient Roar: offering force-switch of opponent's active");
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::UseAbility {
                        in_play_idx: bench_idx,
                    },
                    SimpleAction::Noop,
                ],
            ));
        }
        // §47 — Poltchageist (B4 017): offer the heal only when there is a matching Active with
        // damage on it, so the bot is never asked to price a no-op.
        Some(AbilityMechanic::HealActiveTypedOnBenchFromHand { energy_type, .. }) => {
            let energy_type = *energy_type;
            let worth_offering = state
                .maybe_get_active(actor)
                .is_some_and(|active| active.is_damaged() && state.pokemon_is_type(active, energy_type));
            if !worth_offering || state.is_healing_blocked() {
                return;
            }
            debug!("Poltchageist-style bench heal: offering");
            state.move_generation_stack.push((
                actor,
                vec![
                    SimpleAction::UseAbility {
                        in_play_idx: bench_idx,
                    },
                    SimpleAction::Noop,
                ],
            ));
        }
        _ => {}
    }
}

/// Called when a basic Pokémon is played to the bench from hand
pub(crate) fn on_end_turn(player_ending_turn: usize, state: &mut State) {
    // Check if active Pokémon has an end-of-turn ability
    let active = state.get_active(player_ending_turn);
    if let Some(mechanic) = get_in_play_ability_mechanic(state, active) {
        if matches!(
            mechanic,
            AbilityMechanic::EndTurnDrawCardIfActive { amount: 1 }
        ) {
            debug!("Legendary Pulse: Drawing a card");
            state.move_generation_stack.push((
                player_ending_turn,
                vec![SimpleAction::DrawCard { amount: 1 }],
            ));
        }
        if let AbilityMechanic::EndTurnHealSelfIfActive { amount } = mechanic {
            debug!("Full-Mouth Manner: Healing 20 damage from active");
            state.heal_pokemon(player_ending_turn, 0, *amount);
        }
    }

    // Leftovers (A3b 067): at the end of your turn, heal 10 from the holder if it is Active.
    // Checked outside the ability block above, since a Pokémon can have both an end-of-turn
    // ability and this tool.
    if has_tool(
        state.get_active(player_ending_turn),
        CardId::A3b067Leftovers,
    ) {
        debug!("Leftovers: healing 10 damage from active");
        let amount = 10 * tool_count(state.get_active(player_ending_turn), CardId::A3b067Leftovers);
        state.heal_pokemon(player_ending_turn, 0, amount);
    }

    // End-of-turn effects belonging to the player whose turn is ending resolve first. In
    // particular, their Bad Dreams must resolve before the opponent's Lum Berry can cure Sleep.
    apply_bad_dreams_damage_for_owner(player_ending_turn, state);
    apply_end_of_turn_berries_for_owner(player_ending_turn, state);

    // Process delayed damage effects on active Pokemon
    // Delayed damage triggers at the end of the opponent's turn (when their turn ends, the effect expires)
    let total_delayed_damage: u32 = state
        .get_active(player_ending_turn)
        .get_effects()
        .iter()
        .filter_map(|(effect, _)| {
            if let CardEffect::DelayedDamage { amount } = effect {
                Some(*amount)
            } else {
                None
            }
        })
        .sum();

    if total_delayed_damage > 0 {
        debug!(
            "Delayed damage: Applying {} damage to active Pokemon",
            total_delayed_damage
        );
        // The opponent is the source of the delayed damage (they used the attack that caused it)
        let opponent = (player_ending_turn + 1) % 2;
        crate::actions::handle_damage(
            state,
            (opponent, 0), // Opponent's active Pokemon as the source
            &[(total_delayed_damage, player_ending_turn, 0)], // Target is current player's active
            false,         // Not from an active attack (it's a delayed effect)
            None,          // No attack name
        );
    }

    // Process delayed spot damage effects from turn effects (e.g. Meowscarada ex's Flower Trick).
    // These target a board position, so they hit whichever Pokémon occupies the spot at trigger time.
    let triggered_spot_damages: Vec<(usize, usize, usize, u32, bool)> = state
        .get_current_turn_effects()
        .into_iter()
        .filter_map(|effect| match effect {
            TurnEffect::DelayedSpotDamage {
                source_player,
                target_player,
                target_in_play_idx,
                amount,
                knock_out,
            } if target_player == player_ending_turn => Some((
                source_player,
                target_player,
                target_in_play_idx,
                amount,
                knock_out,
            )),
            _ => None,
        })
        .collect();

    for (source_player, target_player, target_in_play_idx, amount, knock_out) in
        triggered_spot_damages
    {
        // The effect targets a SPOT, so a Pokémon that moved out of it is not hit and an empty
        // spot resolves to nothing.
        let Some(occupant) = state.in_play_pokemon[target_player][target_in_play_idx].as_ref()
        else {
            continue;
        };

        // Armaldo's Abyssal Drop knocks the occupant out rather than dealing a printed number, so
        // the damage is its remaining HP at trigger time — a bigger Pokémon standing in the spot
        // does not survive it.
        let amount = if knock_out {
            occupant.get_remaining_hp()
        } else {
            amount
        };

        debug!(
            "Delayed spot damage: Applying {} damage to player {} slot {} (ko={})",
            amount, target_player, target_in_play_idx, knock_out
        );
        crate::actions::handle_damage(
            state,
            (source_player, 0),
            &[(amount, target_player, target_in_play_idx)],
            false,
            None,
        );
    }

    // Discard Metal Core Barrier from the opponent's Pokémon at the end of this player's turn.
    // ("discard it at the end of your opponent's turn" — the tool owner is the other player)
    let tool_owner = (player_ending_turn + 1) % 2;
    let barrier_indices: Vec<usize> = state.in_play_pokemon[tool_owner]
        .iter()
        .enumerate()
        .filter(|(_, slot)| {
            slot.as_ref()
                .is_some_and(|p| has_tool(p, CardId::B2148MetalCoreBarrier))
        })
        .map(|(i, _)| i)
        .collect();
    for idx in barrier_indices {
        debug!("Metal Core Barrier: Discarding at end of opponent's turn");
        while state.discard_one_matching_tool(tool_owner, idx, CardId::B2148MetalCoreBarrier) {}
    }

    // Check for Zeraora's Thunderclap Flash ability (on first turn only)
    // Turn 1 is player 0's first turn, turn 2 is player 1's first turn
    if state.turn_count == 1 || state.turn_count == 2 {
        // Collect indices first to avoid borrow checker issues
        let zeraora_indices: Vec<usize> = state
            .enumerate_in_play_pokemon(player_ending_turn)
            .filter_map(|(in_play_idx, pokemon)| {
                if matches!(
                    get_in_play_ability_mechanic(state, pokemon),
                    Some(AbilityMechanic::EndFirstTurnAttachEnergyToSelf {
                        energy_type: EnergyType::Lightning
                    })
                ) {
                    return Some(in_play_idx);
                }
                None
            })
            .collect();

        // Now attach energy to all Zeraora pokemon
        for in_play_idx in zeraora_indices {
            // At the end of your first turn, take a Lightning Energy from your Energy Zone and attach it to this Pokémon.
            debug!("Zeraora's Thunderclap Flash: Attaching 1 Lightning Energy");
            state.attach_energy_from_zone(
                player_ending_turn,
                in_play_idx,
                EnergyType::Lightning,
                1,
                false,
            );
        }
    }

    // Hiking Trail: At the end of each player's turn, draw cards until they have 3 in hand.
    if is_hiking_trail_active(state) {
        let hand_size = state.hands[player_ending_turn].len();
        if hand_size < 3 {
            let amount = 3 - hand_size;
            debug!(
                "Hiking Trail: Player {} drawing {} card(s) to reach 3 in hand",
                player_ending_turn, amount
            );
            for _ in 0..amount {
                state.maybe_draw_card(player_ending_turn);
            }
        }
    }

    apply_soothing_shore_healing(player_ending_turn, state);

    apply_deceptive_needle_damage(player_ending_turn, state);

    let other_player = (player_ending_turn + 1) % 2;
    apply_end_of_turn_berries_for_owner(other_player, state);
    apply_bad_dreams_damage_for_owner(other_player, state);
}

/// Deceptive Needle: At the end of your turn, if the [D] Pokémon this card is attached to is in
/// the Active Spot, do 10 damage to your opponent's Active Pokémon.
fn apply_deceptive_needle_damage(player_ending_turn: usize, state: &mut State) {
    let Some(active) = state.maybe_get_active(player_ending_turn) else {
        return;
    };
    if active.is_knocked_out()
        || !has_tool(active, CardId::B4148DeceptiveNeedle)
        || active.get_energy_type() != Some(EnergyType::Darkness)
    {
        return;
    }
    let opponent = (player_ending_turn + 1) % 2;
    if state.in_play_pokemon[opponent][0].is_none() {
        return;
    }
    let damage = 10 * tool_count(active, CardId::B4148DeceptiveNeedle);
    debug!("Deceptive Needle: Doing {damage} damage to opponent's Active Pokémon");
    crate::actions::handle_damage(
        state,
        (player_ending_turn, 0),
        &[(damage, opponent, 0)],
        false,
        None,
    );
}

/// Soothing Shore: At the end of each player's turn, that player heals 20 damage from each of
/// their Pokémon that has any [W] Energy attached.
fn apply_soothing_shore_healing(player_ending_turn: usize, state: &mut State) {
    if !is_soothing_shore_active(state) {
        return;
    }
    debug!("Soothing Shore: Healing 20 from each [W]-Energy Pokémon");
    state.heal_each_pokemon(player_ending_turn, 20, |pokemon| {
        !pokemon.is_knocked_out()
            && pokemon.attached_energy.contains(&EnergyType::Water)
    });
}

/// Apply Bad Dreams damage from one player's Darkrai, preserving end-of-turn owner order.
fn apply_bad_dreams_damage_for_owner(darkrai_owner: usize, state: &mut State) {
    let mut sources: Vec<(usize, usize, u32)> = vec![];
    for (idx, pokemon) in state.enumerate_in_play_pokemon(darkrai_owner) {
        if pokemon.is_knocked_out() {
            continue;
        }
        if let Some(AbilityMechanic::BadDreamsEndOfTurn { amount }) =
            get_in_play_ability_mechanic(state, pokemon)
        {
            sources.push((darkrai_owner, idx, *amount));
        }
    }

    for (darkrai_owner, darkrai_idx, amount) in sources {
        if state.in_play_pokemon[darkrai_owner][darkrai_idx].is_none() {
            continue;
        }
        let opponent = (darkrai_owner + 1) % 2;
        let Some(opponent_active) = state.in_play_pokemon[opponent][0].as_ref() else {
            continue;
        };
        if !opponent_active.is_asleep() {
            continue;
        }
        debug!(
            "Bad Dreams: Player {}'s Darkrai deals {} damage to opponent's Asleep active",
            darkrai_owner, amount
        );
        crate::actions::handle_damage(
            state,
            (darkrai_owner, darkrai_idx),
            &[(amount, opponent, 0)],
            false,
            None,
        );
    }
}

pub(crate) fn can_play_support(state: &State) -> bool {
    let has_modifiers = state
        .get_current_turn_effects()
        .iter()
        .any(|x| matches!(x, TurnEffect::NoSupportCards));

    // Check if opponent has Gengar ex with Shadowy Spellbind in active spot
    let opponent = (state.current_player + 1) % 2;
    let blocked_by_gengar =
        state.in_play_pokemon[opponent][0]
            .as_ref()
            .is_some_and(|opponent_active| {
                matches!(
                    get_in_play_ability_mechanic(state, opponent_active),
                    Some(AbilityMechanic::NoOpponentSupportInActive)
                )
            });

    !state.has_played_support && !has_modifiers && !blocked_by_gengar
}

pub(crate) fn can_play_item(state: &State) -> bool {
    let has_modifiers = state
        .get_current_turn_effects()
        .iter()
        .any(|x| matches!(x, TurnEffect::NoItemCards));

    !has_modifiers
}

fn get_heavy_helmet_reduction(
    state: &State,
    attacking_player: usize,
    (target_player, target_idx): (usize, usize),
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack || attacking_player == target_player {
        return 0;
    }
    let defending_pokemon = &state.in_play_pokemon[target_player][target_idx]
        .as_ref()
        .expect("Defending Pokemon should be there when checking Heavy Helmet");
    heavy_helmet_reduction(defending_pokemon)
}

/// Heavy Helmet on `defending_pokemon`: -20 per Helmet when its printed Retreat Cost is 3 or more.
fn heavy_helmet_reduction(defending_pokemon: &PlayedCard) -> u32 {
    if has_tool(defending_pokemon, CardId::B1219HeavyHelmet) {
        if let Card::Pokemon(pokemon_card) = &defending_pokemon.card {
            if pokemon_card.retreat_cost.len() >= 3 {
                debug!("Heavy Helmet: Reducing damage by 20");
                return 20 * tool_count(defending_pokemon, CardId::B1219HeavyHelmet);
            }
        }
    }
    0
}

fn get_metal_core_barrier_reduction(
    state: &State,
    (target_player, target_idx): (usize, usize),
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack {
        return 0;
    }

    let defending_pokemon = &state.in_play_pokemon[target_player][target_idx]
        .as_ref()
        .expect("Defending Pokemon should be there when checking Metal Core Barrier");
    // Metal Core Barrier: "The [M] Pokémon this card is attached to takes -50 damage..."
    if has_tool(defending_pokemon, CardId::B2148MetalCoreBarrier)
        && state.pokemon_is_type(defending_pokemon, EnergyType::Metal)
    {
        debug!("Metal Core Barrier: Reducing damage by 50");
        return 50 * tool_count(defending_pokemon, CardId::B2148MetalCoreBarrier);
    }
    0
}

fn get_steel_apron_reduction(
    state: &State,
    attacking_player: usize,
    (target_player, target_idx): (usize, usize),
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack || attacking_player == target_player {
        return 0;
    }

    let defending_pokemon = &state.in_play_pokemon[target_player][target_idx]
        .as_ref()
        .expect("Defending Pokemon should be there when checking Steel Apron");
    steel_apron_reduction(state, defending_pokemon)
}

/// Steel Apron on `defending_pokemon`: "The [M] Pokémon this card is attached to takes -10 damage..."
fn steel_apron_reduction(state: &State, defending_pokemon: &PlayedCard) -> u32 {
    if has_tool(defending_pokemon, CardId::A4153SteelApron)
        && state.pokemon_is_type(defending_pokemon, EnergyType::Metal)
    {
        debug!("Steel Apron: Reducing damage by 10");
        return 10 * tool_count(defending_pokemon, CardId::A4153SteelApron);
    }
    0
}

fn get_intimidating_fang_reduction(
    state: &State,
    attacking_ref: (usize, usize),
    target_ref: (u32, usize, usize),
    is_from_active_attack: bool,
) -> u32 {
    let (attacking_player, attacking_idx) = attacking_ref;
    let (_, target_player, _) = target_ref;
    if attacking_player == target_player || attacking_idx != 0 || !is_from_active_attack {
        return 0;
    }

    // Local precondition: callers only ask for this reduction while the opposing Active target
    // is occupied. A compulsory Promote is inserted at the bottom of any pending effect frames,
    // so stack order alone does not guarantee that an empty Active has already been refilled.
    let defenders_active = state.in_play_pokemon[target_player][0]
        .as_ref()
        .expect("Defending Pokemon should be there when checking Intimidating Fang");
    // Reads the unified effect list: Intimidating Fang (a passive ability) presents as a
    // `ReduceOpponentActiveDamage` effect on the Active defender.
    defenders_active
        .get_effective_card_effects(state)
        .iter()
        .filter_map(|effect| match effect {
            CardEffect::ReduceOpponentActiveDamage { amount } => Some(*amount),
            _ => None,
        })
        .sum()
}

fn get_ability_damage_reduction(
    state: &State,
    receiving_pokemon: &crate::models::PlayedCard,
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack {
        return 0;
    }
    // Reads the unified effect list, so Cloyster's Shell Armor (a passive ability) is handled the
    // same way as any stored effect.
    receiving_pokemon
        .get_effective_card_effects(state)
        .iter()
        .filter_map(|effect| match effect {
            CardEffect::ReduceDamageFromAttacks { amount } => Some(*amount),
            _ => None,
        })
        .sum()
}

/// True if `player` has a Pokémon in play whose name is one of `names`. Used by the abilities
/// worded "if you have <Pokémon> in play" (Power Link, Speed Link, Fantastical Floating).
pub(crate) fn has_named_pokemon_in_play(state: &State, player: usize, names: &[&str]) -> bool {
    state
        .enumerate_in_play_pokemon(player)
        .any(|(_, pokemon)| names.contains(&pokemon.get_name().as_str()))
}

/// Whether `player` has Arceus or Arceus ex anywhere in play. Shared by the Arceus-conditional
/// ability mechanics: `IncreaseDamageIfArceusInPlay` (offense), `ReduceDamageIfArceusInPlay`
/// (Resilience Link, defense) and `NoRetreatCost` with `NamedPokemonInPlay(ARCEUS_NAMES)`.
fn has_arceus_in_play(state: &State, player: usize) -> bool {
    has_named_pokemon_in_play(state, player, ARCEUS_NAMES)
}

/// Unown's GUARD works only while its controller has *another* Unown in play whose printed Ability
/// is something other than GUARD (CHECK on A2a 034 / A2a 078, POWER on A4 085). Two GUARD Unown
/// never enable each other.
fn has_non_guard_unown_in_play(state: &State, player: usize) -> bool {
    state.enumerate_in_play_pokemon(player).any(|(_, pokemon)| {
        pokemon.get_name() == "Unown"
            && has_any_in_play_ability(state, pokemon)
            && pokemon
                .card
                .get_ability()
                .is_some_and(|ability| ability.title != "GUARD")
    })
}

/// GUARD (Unown A4 084): "All of your Pokémon take -10 damage from attacks from your opponent's
/// Pokémon", gated on `has_non_guard_unown_in_play`. Board-wide rather than self-scoped, so it is
/// summed over every GUARD Unown the defending player controls instead of being read off the
/// target's own ability.
fn get_unown_guard_reduction(state: &State, target_player: usize) -> u32 {
    if !has_non_guard_unown_in_play(state, target_player) {
        return 0;
    }
    state
        .enumerate_in_play_pokemon(target_player)
        .filter_map(
            |(_, pokemon)| match get_in_play_ability_mechanic(state, pokemon) {
                Some(AbilityMechanic::UnownGuard { amount }) => Some(*amount),
                _ => None,
            },
        )
        .sum()
}

/// Damage reduction printed on the receiving Pokémon itself but conditioned on the attacker or on
/// the board, so it cannot be modelled as a context-free `CardEffect` the way
/// `ReduceDamageFromAttacks` is (see `card_effect_from_ability_mechanic`).
fn get_conditional_self_damage_reduction(
    state: &State,
    attacking_pokemon: &PlayedCard,
    target_player: usize,
    receiving_pokemon: &PlayedCard,
    from_opponent: bool,
) -> u32 {
    match get_in_play_ability_mechanic(state, receiving_pokemon) {
        // Thick Fat / Defensive Whirlwind: gated on the attacker's Energy type.
        Some(AbilityMechanic::ReduceDamageFromTypedAttackers {
            energy_types,
            amount,
        }) if state
            .pokemon_energy_types(attacking_pokemon)
            .iter()
            .any(|attacker_type| energy_types.contains(attacker_type)) =>
        {
            *amount
        }
        // Resilience Link: gated on the receiver's own controller having an Arceus in play.
        Some(AbilityMechanic::ReduceDamageIfArceusInPlay { amount })
            if has_arceus_in_play(state, target_player) =>
        {
            *amount
        }
        // Ice Face: only while undamaged, and only against the opponent's Pokémon.
        Some(AbilityMechanic::ReduceDamageAtFullHp { amount })
            if from_opponent
                && receiving_pokemon.get_remaining_hp()
                    == receiving_pokemon.get_effective_total_hp() =>
        {
            *amount
        }
        _ => 0,
    }
}

/// True if `player` has at least two Pokémon named `pokemon_name` in play — i.e. any one of them
/// has "another <name> in play" (Falinks' Coordinated Unit).
pub(crate) fn has_another_pokemon_named_in_play(state: &State, player: usize, pokemon_name: &str) -> bool {
    state
        .enumerate_in_play_pokemon(player)
        .filter(|(_, pokemon)| pokemon.get_name() == pokemon_name)
        .count()
        >= 2
}

/// Falinks' Coordinated Unit, defensive half: "this Pokémon takes -20 damage from attacks from
/// your opponent's Pokémon". Self-scoped but board-conditional, so unlike the reductions in
/// `get_ability_damage_reduction` it cannot be expressed as a context-free `CardEffect`. It
/// protects Falinks in the Active Spot and on the Bench alike, and only against the opponent.
fn get_coordinated_unit_reduction(
    state: &State,
    attacking_player: usize,
    target_player: usize,
    receiving_pokemon: &PlayedCard,
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack || attacking_player == target_player {
        return 0;
    }
    match get_in_play_ability_mechanic(state, receiving_pokemon) {
        Some(AbilityMechanic::CoordinatedUnit {
            pokemon_name,
            damage_reduction,
            ..
        }) if has_another_pokemon_named_in_play(state, target_player, pokemon_name) => {
            debug!("Coordinated Unit: Reducing damage by {damage_reduction}");
            *damage_reduction
        }
        _ => 0,
    }
}

/// All conditional ability-driven damage reduction protecting the target: the reductions printed on
/// the target itself plus board-wide ones (Unown's GUARD). Returned as a flat amount that the caller
/// folds into the other pre-Weakness reductions, matching how every existing damage-reduction
/// ability is ordered relative to the Weakness bonus.
fn get_conditional_ability_damage_reduction(
    state: &State,
    attacking_player: usize,
    attacking_pokemon: &PlayedCard,
    target_player: usize,
    receiving_pokemon: &PlayedCard,
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack {
        return 0;
    }
    let from_opponent = attacking_player != target_player;
    let self_reduction = get_conditional_self_damage_reduction(
        state,
        attacking_pokemon,
        target_player,
        receiving_pokemon,
        from_opponent,
    );
    // GUARD is board-wide ("All of your Pokémon"), and only against the opponent's Pokémon.
    let guard_reduction = if from_opponent {
        get_unown_guard_reduction(state, target_player)
    } else {
        0
    };

    let total = self_reduction + guard_reduction;
    if total > 0 {
        debug!("Conditional ability damage reduction: -{total}");
    }
    total
}

fn get_ability_damage_increase(
    state: &State,
    attacking_player: usize,
    attacking_pokemon: &crate::models::PlayedCard,
    is_active_to_active: bool,
) -> u32 {
    if !is_active_to_active {
        return 0;
    }

    if let Some(AbilityMechanic::IncreaseDamageWhenRemainingHpAtMost {
        amount,
        hp_threshold,
    }) = get_in_play_ability_mechanic(state, attacking_pokemon)
    {
        if attacking_pokemon.get_remaining_hp() <= *hp_threshold {
            debug!(
                "IncreaseDamageWhenRemainingHpAtMost: Increasing damage by {}",
                amount
            );
            return *amount;
        }
    }

    if let Some(AbilityMechanic::IncreaseDamageIfArceusInPlay { amount }) =
        get_in_play_ability_mechanic(state, attacking_pokemon)
    {
        if has_arceus_in_play(state, attacking_player) {
            debug!(
                "IncreaseDamageIfArceusInPlay: Increasing damage by {}",
                amount
            );
            return *amount;
        }
    }

    // Coordinated Unit (Falinks), offensive half: "this Pokémon's attacks do +20 damage to your
    // opponent's Active Pokémon" while you have another Falinks in play.
    if let Some(AbilityMechanic::CoordinatedUnit {
        pokemon_name,
        damage_bonus,
        ..
    }) = get_in_play_ability_mechanic(state, attacking_pokemon)
    {
        if has_another_pokemon_named_in_play(state, attacking_player, pokemon_name) {
            debug!("Coordinated Unit: Increasing damage by {damage_bonus}");
            return *damage_bonus;
        }
    }

    0
}

fn get_increased_turn_effect_modifiers(
    state: &State,
    is_active_to_active: bool,
    target_is_ex: bool,
    attacker_is_eevee_evolution: bool,
    attacking_pokemon: &crate::models::PlayedCard,
    attacking_player: usize,
) -> u32 {
    let attacker_energy_types = state.pokemon_energy_types(attacking_pokemon);
    state
        .get_current_turn_effects()
        .iter()
        .map(|effect| match effect {
            TurnEffect::IncreasedDamage { amount } if is_active_to_active => *amount,
            // Inspiring Dance (Oricorio / Meloetta). Player-scoped because it lives across the
            // opponent's turn to reach "your next turn"; `energy_type: None` means every Pokémon.
            TurnEffect::IncreasedDamageForPlayer {
                amount,
                player,
                energy_type,
            } if *player == attacking_player
                && is_active_to_active
                && energy_type.is_none_or(|required| attacker_energy_types.contains(&required)) =>
            {
                *amount
            }
            TurnEffect::IncreasedDamageForType {
                amount,
                energy_type,
            } if is_active_to_active && attacker_energy_types.contains(energy_type) => *amount,
            TurnEffect::IncreasedDamageAgainstEx { amount }
                if is_active_to_active && target_is_ex =>
            {
                *amount
            }
            TurnEffect::IncreasedDamageForEeveeEvolutions { amount }
                if is_active_to_active && attacker_is_eevee_evolution =>
            {
                *amount
            }
            TurnEffect::IncreasedDamageForSpecificPokemon {
                amount,
                pokemon_names,
            } => {
                let attacker_name = attacking_pokemon.get_name();
                let is_backpack = *amount == 20
                    && pokemon_names.len() == 2
                    && pokemon_names.iter().any(|name| name == "Magneton")
                    && pokemon_names.iter().any(|name| name == "Heliolisk");
                if (is_active_to_active || is_backpack)
                    && pokemon_names
                    .iter()
                    .any(|name| name.as_str() == attacker_name)
                {
                    *amount
                } else {
                    0
                }
            }
            TurnEffect::IncreasedDamageForSpecificPokemonAgainstEx {
                amount,
                pokemon_names,
            } if is_active_to_active && target_is_ex => {
                let attacker_name = attacking_pokemon.get_name();
                if pokemon_names
                    .iter()
                    .any(|name| name.as_str() == attacker_name)
                {
                    *amount
                } else {
                    0
                }
            }
            TurnEffect::IncreasedDamageForTypeAgainstEx {
                amount,
                energy_type,
            } if is_active_to_active
                && target_is_ex
                && attacker_energy_types.contains(energy_type) =>
            {
                *amount
            }
            _ => 0,
        })
        .sum::<u32>()
}

fn get_increased_attack_specific_modifiers(
    attacking_pokemon: &crate::models::PlayedCard,
    is_active_to_active: bool,
    attack_name: Option<&str>,
) -> u32 {
    if !is_active_to_active {
        return 0;
    }
    attacking_pokemon
        .get_active_effects()
        .iter()
        .filter_map(|effect| match effect {
            CardEffect::IncreasedDamageForAttack {
                attack_name: effect_attack_name,
                amount,
            } => {
                if let Some(current_attack_name) = attack_name {
                    if current_attack_name == effect_attack_name {
                        Some(*amount)
                    } else {
                        None
                    }
                } else {
                    None
                }
            }
            _ => None,
        })
        .sum::<u32>()
}

fn get_reduced_card_effect_modifiers(
    state: &State,
    is_active_to_active: bool,
    target_player: usize,
    attacker_is_ex: bool,
) -> u32 {
    if !is_active_to_active {
        return 0;
    }
    state
        .get_active(target_player)
        .get_active_effects()
        .iter()
        .map(|effect| match effect {
            CardEffect::ReducedDamage { amount } => *amount,
            // Aegislash's Superb Shield: same reduction, but only against the opponent's ex.
            CardEffect::ReducedDamageFromEx { amount } if attacker_is_ex => *amount,
            _ => 0,
        })
        .sum::<u32>()
}

fn get_increased_vulnerability_modifiers(
    state: &State,
    is_active_to_active: bool,
    target_player: usize,
) -> u32 {
    if !is_active_to_active {
        return 0;
    }
    state
        .get_active(target_player)
        .get_active_effects()
        .iter()
        .filter(|effect| matches!(effect, CardEffect::IncreasedVulnerability { .. }))
        .map(|effect| match effect {
            CardEffect::IncreasedVulnerability { amount } => *amount,
            _ => 0,
        })
        .sum::<u32>()
}

fn get_turn_effect_damage_reduction(
    state: &State,
    target_player: usize,
    target_pokemon: &crate::models::PlayedCard,
    attacking_player: usize,
    attacking_pokemon: &PlayedCard,
    is_from_active_attack: bool,
) -> u32 {
    if !is_from_active_attack || attacking_player == target_player {
        return 0;
    }
    let target_energy_types = state.pokemon_energy_types(target_pokemon);
    let attacker_is_ex = attacking_pokemon.card.is_ex();
    state
        .get_current_turn_effects()
        .iter()
        .filter_map(|effect| match effect {
            TurnEffect::ReducedDamageForType {
                amount,
                energy_type,
                player,
            } if *player == target_player && target_energy_types.contains(energy_type) => {
                Some(*amount)
            }
            TurnEffect::ReducedDamageForTarget {
                amount,
                player,
                scope,
                only_from_ex,
            } if *player == target_player
                && (!*only_from_ex || attacker_is_ex)
                && damage_reduction_scope_covers(scope, target_pokemon) =>
            {
                Some(*amount)
            }
            _ => None,
        })
        .sum::<u32>()
}

/// Whether a `ReducedDamageForTarget` scope covers `pokemon` (see `DamageReductionScope`).
fn damage_reduction_scope_covers(scope: &DamageReductionScope, pokemon: &PlayedCard) -> bool {
    match scope {
        DamageReductionScope::AllPokemon => true,
        DamageReductionScope::NamedPokemon(names) => names.contains(&pokemon.get_name()),
        DamageReductionScope::UltraBeasts => is_ultra_beast(&pokemon.get_name()),
    }
}

enum WeaknessApplication {
    None,
    Flat(u32),
    Double,
}

const DAMAGE_UNAFFECTED_BY_WEAKNESS_EFFECT: &str =
    "This attack's damage isn't affected by Weakness.";

/// Ledian's Swift: one clause combining the Weakness bypass with Sawk's opponent-active-effects
/// bypass. Detected as its own exact string because it matches neither single-clause constant.
const DAMAGE_UNAFFECTED_BY_WEAKNESS_OR_OPPONENT_ACTIVE_EFFECTS_EFFECT: &str =
    "This attack's damage isn't affected by Weakness or by any effects on your opponent's Active Pokémon.";

/// Sawk's Brick Break (and any card sharing this clause): the attack's damage ignores every effect
/// on the opponent's Active Pokémon — ability-derived reductions/preventions, stored CardEffects,
/// and damage-reducing Tools alike. See `attack_ignores_opponent_active_effects`.
pub(crate) const DAMAGE_UNAFFECTED_BY_OPPONENT_ACTIVE_EFFECTS_EFFECT: &str =
    "This attack's damage isn't affected by any effects on your opponent's Active Pokémon.";

/// Whether an attack's effect text carries the "isn't affected by any effects on your opponent's
/// Active Pokémon" clause. This is a substring match (not equality) so attacks that combine it with
/// another clause — e.g. Mega Medicham ex's "Chakra Fist" (the [P]-Energy damage bonus plus this
/// clause) — share Sawk's bypass behavior.
pub(crate) fn attack_effect_ignores_opponent_active_effects(effect: Option<&str>) -> bool {
    effect.is_some_and(|e| {
        e.contains(DAMAGE_UNAFFECTED_BY_OPPONENT_ACTIVE_EFFECTS_EFFECT)
            || e.contains(DAMAGE_UNAFFECTED_BY_WEAKNESS_OR_OPPONENT_ACTIVE_EFFECTS_EFFECT)
    })
}

#[derive(Clone, Copy, Default)]
pub(crate) struct DamageModifierContext<'a> {
    pub(crate) attack_name: Option<&'a str>,
    pub(crate) attack_effect: Option<&'a str>,
}

#[derive(Clone, Copy, Default)]
struct FiniteDamageReductions {
    heavy_helmet: u32,
    metal_core_barrier: u32,
    steel_apron: u32,
    ability: u32,
    conditional_ability: u32,
    coordinated_unit: u32,
    card_effect: u32,
    turn_effect: u32,
}

impl FiniteDamageReductions {
    fn total_u64(self) -> u64 {
        [
            self.heavy_helmet,
            self.metal_core_barrier,
            self.steel_apron,
            self.ability,
            self.conditional_ability,
            self.coordinated_unit,
            self.card_effect,
            self.turn_effect,
        ]
        .into_iter()
        .map(u64::from)
        .sum()
    }

    fn total_u32_saturating(self) -> u32 {
        u32::try_from(self.total_u64()).unwrap_or(u32::MAX)
    }
}

fn finite_damage_reductions(
    state: &State,
    attacking_ref: (usize, usize),
    target: (usize, usize),
    is_from_active_attack: bool,
    skip_target_effects: bool,
) -> FiniteDamageReductions {
    if skip_target_effects {
        return FiniteDamageReductions::default();
    }

    let (attacking_player, attacking_idx) = attacking_ref;
    let (target_player, target_idx) = target;
    let attacking_pokemon = state.in_play_pokemon[attacking_player][attacking_idx]
        .as_ref()
        .expect("Attacking Pokemon should be there when calculating damage reduction");
    let receiving_pokemon = state.in_play_pokemon[target_player][target_idx]
        .as_ref()
        .expect("Receiving Pokemon should be there when calculating damage reduction");
    let is_active_to_active = target_idx == 0 && attacking_idx == 0 && is_from_active_attack;

    FiniteDamageReductions {
        heavy_helmet: get_heavy_helmet_reduction(
            state,
            attacking_player,
            target,
            is_from_active_attack,
        ),
        metal_core_barrier: get_metal_core_barrier_reduction(
            state,
            target,
            is_from_active_attack,
        ),
        steel_apron: get_steel_apron_reduction(
            state,
            attacking_player,
            target,
            is_from_active_attack,
        ),
        ability: get_ability_damage_reduction(state, receiving_pokemon, is_from_active_attack),
        conditional_ability: get_conditional_ability_damage_reduction(
            state,
            attacking_player,
            attacking_pokemon,
            target_player,
            receiving_pokemon,
            is_from_active_attack,
        ),
        coordinated_unit: get_coordinated_unit_reduction(
            state,
            attacking_player,
            target_player,
            receiving_pokemon,
            is_from_active_attack,
        ),
        card_effect: get_reduced_card_effect_modifiers(
            state,
            is_active_to_active,
            target_player,
            attacking_pokemon.card.is_ex(),
        ),
        turn_effect: get_turn_effect_damage_reduction(
            state,
            target_player,
            receiving_pokemon,
            attacking_player,
            attacking_pokemon,
            is_from_active_attack,
        ),
    }
}

/// Conservative raw damage at which every larger active-to-active hit has the same lethal or
/// fully-prevented successor. Positive bonuses and Weakness are deliberately ignored; doing so can
/// only raise the boundary. Finite defender coin reduction is included because it is applied
/// before `modify_damage`. A full-prevention coin branch is already identical at every damage.
pub(crate) fn active_attack_damage_saturation_requirement(
    state: &State,
    acting_player: usize,
    context: DamageModifierContext<'_>,
) -> u64 {
    let opponent = (acting_player + 1) % 2;
    let attacking_ref = (acting_player, 0);
    let target = (opponent, 0);
    let receiving = state.in_play_pokemon[opponent][0]
        .as_ref()
        .expect("Defending Active should exist when calculating damage saturation");
    let skip_target_effects = attack_ignores_opponent_active_effects(context);
    let target_effects = if skip_target_effects {
        Vec::new()
    } else {
        receiving.get_effective_card_effects(state)
    };
    let threshold_requirement = target_effects
        .iter()
        .filter_map(|effect| match effect {
            CardEffect::PreventDamageIfLessOrEqual { threshold } => {
                Some(u64::from(*threshold) + 1)
            }
            _ => None,
        })
        .max()
        .unwrap_or(0);
    let finite_coin_reduction = target_effects
        .iter()
        .find_map(|effect| match effect {
            CardEffect::CoinFlipToReduceIncomingDamage { amount } => Some(*amount),
            CardEffect::CoinFlipToPreventIncomingDamage => Some(u32::MAX),
            _ => None,
        })
        .filter(|amount| *amount != u32::MAX)
        .map(u64::from)
        .unwrap_or(0);
    let remaining_hp = receiving.get_remaining_hp();
    assert!(
        remaining_hp > 0,
        "damage saturation requires a living Defending Active"
    );
    let post_reduction_requirement = u64::from(remaining_hp).max(threshold_requirement);
    let intimidating_fang_reduction = if skip_target_effects {
        0
    } else {
        get_intimidating_fang_reduction(state, attacking_ref, (0, opponent, 0), true)
    };
    finite_damage_reductions(state, attacking_ref, target, true, skip_target_effects)
        .total_u64()
        .checked_add(u64::from(intimidating_fang_reduction))
        .and_then(|value| value.checked_add(finite_coin_reduction))
        .and_then(|value| value.checked_add(post_reduction_requirement))
        .expect("active-attack damage saturation requirement overflowed u64")
}

fn attack_effect_ignores_weakness(context: DamageModifierContext<'_>) -> bool {
    // TODO: If more attack text needs to alter damage-modifier stages, replace this
    // effect-string check with a typed attack metadata/damage-modifier capability.
    matches!(
        context.attack_effect,
        Some(DAMAGE_UNAFFECTED_BY_WEAKNESS_EFFECT)
            | Some(DAMAGE_UNAFFECTED_BY_WEAKNESS_OR_OPPONENT_ACTIVE_EFFECTS_EFFECT)
    )
}

fn attack_ignores_opponent_active_effects(context: DamageModifierContext<'_>) -> bool {
    attack_effect_ignores_opponent_active_effects(context.attack_effect)
}

fn get_weakness_application(
    state: &State,
    is_active_to_active: bool,
    target_player: usize,
    attacking_pokemon: &crate::models::PlayedCard,
    context: DamageModifierContext<'_>,
) -> WeaknessApplication {
    if !is_active_to_active || attack_effect_ignores_weakness(context) {
        return WeaknessApplication::None;
    }
    weakness_application_against(state, state.get_active(target_player), attacking_pokemon)
}

/// Weakness of `receiving` to `attacking_pokemon`, both taken as Active: none under a `NoWeakness` effect,
/// else as [`printed_weakness_application`].
fn weakness_application_against(
    state: &State,
    receiving: &PlayedCard,
    attacking_pokemon: &crate::models::PlayedCard,
) -> WeaknessApplication {
    if receiving
        .get_active_effects()
        .iter()
        .any(|effect| matches!(effect, CardEffect::NoWeakness))
    {
        debug!("NoWeakness: Ignoring weakness damage");
        return WeaknessApplication::None;
    }
    printed_weakness_application(state, receiving, attacking_pokemon)
}

/// The printed Weakness rule: +20 when `receiving`'s Weakness is one of the attacker's types, or x2 of the total
/// under Bounded Field for an attacker that isn't a Mega ex.
fn printed_weakness_application(
    state: &State,
    receiving: &PlayedCard,
    attacking_pokemon: &crate::models::PlayedCard,
) -> WeaknessApplication {
    if let Card::Pokemon(pokemon_card) = &receiving.card {
        // Through the type chokepoint: Urshifu's Double Type makes the attacker count as two
        // types, and Weakness triggers if the defender is weak to either of them.
        let attacker_types = state.pokemon_energy_types(attacking_pokemon);
        if pokemon_card
            .weakness
            .is_some_and(|weakness| attacker_types.contains(&weakness))
        {
            debug!("Weakness! {pokemon_card:?} is weak to one of {attacker_types:?}");
            // Bounded Field: ×2 all damage (including other modifiers) for non-Mega-ex attackers
            if is_bounded_field_active(state)
                && !(attacking_pokemon.card.is_mega() && attacking_pokemon.card.is_ex())
            {
                debug!("Bounded Field: Applying weakness as ×2 of total damage");
                return WeaknessApplication::Double;
            }
            return WeaknessApplication::Flat(20);
        }
    }
    WeaknessApplication::None
}

fn get_future_booster_damage_bonus(attacking_pokemon: &PlayedCard) -> u32 {
    if has_tool(attacking_pokemon, CardId::B3a070FutureBoosterEnergyCapsule)
        && is_future_pokemon(&attacking_pokemon.get_name())
    {
        debug!("Future Booster Energy Capsule: Increasing damage by 20");
        return 20 * tool_count(attacking_pokemon, CardId::B3a070FutureBoosterEnergyCapsule);
    }
    0
}

/// Beastite (A3a 066): "Attacks used by the Ultra Beast this card is attached to do +10 damage to
/// your opponent's Active Pokémon for each point you have gotten."
///
/// Scales with points already banked, so it is worth nothing on an empty scoreboard and rises as
/// the holder closes out the game. The caller gates it to active-to-active damage, matching the
/// card's "to your opponent's Active Pokémon" wording.
fn get_beastite_damage_bonus(
    state: &State,
    attacking_player: usize,
    attacking_pokemon: &PlayedCard,
) -> u32 {
    if has_tool(attacking_pokemon, CardId::A3a066Beastite)
        && is_ultra_beast(&attacking_pokemon.get_name())
    {
        let bonus = 10 * state.points[attacking_player] as u32 * tool_count(attacking_pokemon, CardId::A3a066Beastite);
        debug!("Beastite: Increasing damage by {bonus}");
        return bonus;
    }
    0
}

/// Extra times a random-spread attack (e.g. Draco Meteor) chooses a Pokémon this turn, granted
/// by cards like Drayden.
pub(crate) fn get_extra_random_spread_hits(state: &State, attack_name: &str) -> usize {
    state
        .get_current_turn_effects()
        .iter()
        .filter_map(|effect| match effect {
            TurnEffect::ExtraRandomSpreadHits {
                amount,
                attack_name: effect_attack_name,
            } if effect_attack_name == attack_name => Some(*amount),
            _ => None,
        })
        .sum()
}

/// How kd's clock counts a hit on a victim (see [`persistent_defender_damage`]).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum DefenderHit {
    /// An attack that can hit the Active, on the victim as the Active (the clock promotes each victim in turn).
    Active,
    /// An attack that can only damage the Bench, on a victim that is on the Bench: as the engine prices Bench
    /// damage (no Weakness; Protective Poncho and Shell Shield prevent it; Intimidating Fang comes from the
    /// defender's current Active).
    Benched,
}

/// The damage `attacker` does with `base_damage` to `defender` through the defender's persistent public modifiers,
/// the attacker taken as Active and `context` its attack's name and text, the hit counted as `hit` says. For the kd
/// value function's clock, which asks how fast a threat knocks each victim out in turn.
///
/// Returns `(first, later)`: the expected damage of the threat's first hit on this defender, and of every hit after
/// it. They differ for Disguise (`PreventFirstAttack`, while unused: the first hit does 0) and Ice Face
/// (`ReduceDamageAtFullHp`: only while undamaged, so the first hit only, or every hit if the first does 0).
/// Expected, because two Abilities flip a coin: `CoinFlipToPreventIncomingDamage` and
/// `CoinFlipToReduceIncomingDamage` (heads: the damage before modifiers is cut, as `apply_attack_action` does).
///
/// It runs `modify_damage`'s own stages, in its order, restricted to what stays on the board:
/// - `base_damage == 0` does nothing;
/// - the attack's text: "isn't affected by Weakness" drops Weakness, and "isn't affected by any effects on your
///   opponent's Active Pokemon" drops every defender stage below on the Active, as `skip_target_effects` does, and
///   the coin flip (Disguise still applies, as in `handle_damage_only`);
/// - prevention: `PreventAllDamageFromEx` (Safeguard) from the defender's Ability, against an attacker ex; and on
///   the Bench, Protective Poncho and `PreventDamageWhileBenched` (Shell Shield);
/// - before Weakness: `ReduceOpponentActiveDamage` (Intimidating Fang) from the Ability of the defending side's
///   Active: the defender's own when it is the Active, the current Active's for a Benched hit;
/// - Weakness: the printed rule, +20 or Bounded Field's x2 (`printed_weakness_application`), on the Active only;
/// - after Weakness, every finite reduction that isn't temporary: the Tools Heavy Helmet and Steel Apron;
///   `ReduceDamageFromAttacks` from the defender's Ability (Solid Shell, Shell Armor, ...); the conditional
///   Abilities `ReduceDamageFromTypedAttackers`, `ReduceDamageIfArceusInPlay`, `ReduceDamageAtFullHp` and
///   `UnownGuard` (a teammate's Ability); and `CoordinatedUnit`. Board conditions are read on today's board.
///
/// Left out, because they don't last or aren't the defender's: effects stored on the defender by attacks
/// (`ReducedDamage`, `ReducedDamageFromEx`, `NoWeakness`, `PreventDamageFromBasic`, `PreventAllDamageAndEffects`,
/// `PreventDamageIfLessOrEqual`, a stored `ReduceDamageFromAttacks`); Metal Core Barrier (it discards itself at the
/// end of the opponent's turn); turn effects; vulnerability; the attacker's bonuses and carried reductions; and
/// Guts (`CoinFlipToSurviveKnockOut`, which saves a knockout rather than cutting damage). Abilities are read through
/// the engine's suppression-aware lookup.
#[allow(clippy::too_many_arguments)]
pub(crate) fn persistent_defender_damage(
    state: &State,
    attacking_player: usize,
    attacker: &PlayedCard,
    defending_player: usize,
    defender: &PlayedCard,
    base_damage: u32,
    context: DamageModifierContext<'_>,
    hit: DefenderHit,
) -> (f64, f64) {
    let skip_target_effects = hit == DefenderHit::Active && attack_ignores_opponent_active_effects(context);
    let own_ability = get_in_play_ability_mechanic(state, defender);
    let ability_effect = if skip_target_effects {
        None
    } else {
        own_ability.and_then(card_effect_from_ability_mechanic)
    };
    if hit == DefenderHit::Benched
        && (matches!(ability_effect, Some(CardEffect::PreventDamageWhileBenched))
            || (attacking_player != defending_player && has_tool(defender, CardId::B2147ProtectivePoncho)))
    {
        return (0.0, 0.0);
    }
    // Intimidating Fang works from the defending side's Active Spot.
    let fang_holder_effect = if hit == DefenderHit::Benched {
        state
            .maybe_get_active(defending_player)
            .and_then(|active| get_in_play_ability_mechanic(state, active))
            .and_then(card_effect_from_ability_mechanic)
    } else {
        ability_effect.clone()
    };
    let weakness_applies = hit == DefenderHit::Active && !attack_effect_ignores_weakness(context);
    // One hit of `base` raw damage: (first, later) as above, before coins and Disguise.
    let hit = |base: u32| -> (u32, u32) {
        if base == 0 {
            return (0, 0);
        }
        if matches!(ability_effect, Some(CardEffect::PreventAllDamageFromEx)) && attacker.card.is_ex() {
            return (0, 0);
        }
        let intimidating_fang = match fang_holder_effect {
            Some(CardEffect::ReduceOpponentActiveDamage { amount }) => amount,
            _ => 0,
        };
        let pre_weakness = base.saturating_sub(intimidating_fang);
        let weakness = if weakness_applies {
            printed_weakness_application(state, defender, attacker)
        } else {
            WeaknessApplication::None
        };
        let after_weakness = match weakness {
            WeaknessApplication::None => pre_weakness,
            WeaknessApplication::Flat(amount) => pre_weakness + amount,
            WeaknessApplication::Double => pre_weakness * 2,
        };
        if skip_target_effects {
            return (after_weakness, after_weakness);
        }
        let ability = match ability_effect {
            Some(CardEffect::ReduceDamageFromAttacks { amount }) => amount,
            _ => 0,
        };
        let reductions: u64 = [
            heavy_helmet_reduction(defender),
            steel_apron_reduction(state, defender),
            ability,
            get_conditional_ability_damage_reduction(
                state,
                attacking_player,
                attacker,
                defending_player,
                defender,
                true,
            ),
            get_coordinated_unit_reduction(state, attacking_player, defending_player, defender, true),
        ]
        .into_iter()
        .map(u64::from)
        .sum();
        // Ice Face protects only while undamaged: the first hit, and every hit if that one does nothing.
        let full_hp_only = match own_ability {
            Some(AbilityMechanic::ReduceDamageAtFullHp { amount })
                if attacking_player != defending_player
                    && defender.get_remaining_hp() == defender.get_effective_total_hp() =>
            {
                u64::from(*amount)
            }
            _ => 0,
        };
        let after = |reductions: u64| {
            u32::try_from(u64::from(after_weakness).saturating_sub(reductions)).unwrap_or(u32::MAX)
        };
        let first = after(reductions);
        let later = if first == 0 { 0 } else { after(reductions.saturating_sub(full_hp_only)) };
        (first, later)
    };
    let (first, later) = match ability_effect {
        Some(CardEffect::CoinFlipToPreventIncomingDamage) => {
            let (first, later) = hit(base_damage);
            (0.5 * first as f64, 0.5 * later as f64)
        }
        Some(CardEffect::CoinFlipToReduceIncomingDamage { amount }) => {
            let (tails_first, tails_later) = hit(base_damage);
            let (heads_first, heads_later) = hit(base_damage.saturating_sub(amount));
            (
                0.5 * (tails_first + heads_first) as f64,
                0.5 * (tails_later + heads_later) as f64,
            )
        }
        _ => {
            let (first, later) = hit(base_damage);
            (first as f64, later as f64)
        }
    };
    // Disguise: the first attack that damages it after it comes into play is prevented, whatever the attack's text.
    if base_damage > 0
        && own_ability == Some(&AbilityMechanic::PreventFirstAttack)
        && !defender.prevent_first_attack_damage_used
    {
        return (0.0, later);
    }
    (first, later)
}

// TODO: Confirm is_from_attack and goes to enemy active
pub(crate) fn modify_damage(
    state: &State,
    attacking_ref: (usize, usize),
    target_ref: (u32, usize, usize),
    is_from_active_attack: bool,
    context: DamageModifierContext<'_>,
) -> u32 {
    // If attack is 0, not even Giovanni takes it to 10.
    let (attacking_player, attacking_idx) = attacking_ref;
    let (base_damage, target_player, target_idx) = target_ref;
    if base_damage == 0 {
        debug!("Attack is 0, returning 0");
        return base_damage;
    }

    let attacking_pokemon = state.in_play_pokemon[attacking_player][attacking_idx]
        .as_ref()
        .expect("Attacking Pokemon should be there when modifying damage");
    let receiving_pokemon = state.in_play_pokemon[target_player][target_idx]
        .as_ref()
        .expect("Receiving Pokemon should be there when modifying damage");

    // "Effects on the opponent's Active Pokémon" (Sawk's Brick Break) — when this attack ignores
    // them, treat the receiver's effect list as empty for every defensive stage below, and also
    // bypass its damage-reducing Tools. Only the opponent's Active is targeted by such attacks.
    let skip_target_effects = attack_ignores_opponent_active_effects(context)
        && is_from_active_attack
        && target_idx == 0
        && attacking_player != target_player;

    // The unified "effects on this Pokémon" list: stored CardEffects plus any derived from the
    // receiver's passive ability (Cloyster's Shell Armor, Oricorio's Safeguard, Meowth's Carefree
    // Steps, ...). Damage code checks this single list instead of scanning the board for abilities.
    let target_effects: Vec<CardEffect> = if skip_target_effects {
        Vec::new()
    } else {
        receiving_pokemon.get_effective_card_effects(state)
    };

    // Safeguard (Oricorio): prevent all damage from the opponent's Pokémon ex.
    if target_effects
        .iter()
        .any(|e| matches!(e, CardEffect::PreventAllDamageFromEx))
        && is_from_active_attack
        && attacking_pokemon.card.is_ex()
    {
        debug!("Safeguard: Preventing all damage from opponent's Pokémon ex");
        return 0;
    }
    // Shell Shield (Wartortle): prevent all damage while benched.
    if target_effects
        .iter()
        .any(|e| matches!(e, CardEffect::PreventDamageWhileBenched))
        && is_from_active_attack
        && target_idx != 0
    {
        debug!("Shell Shield: Preventing all damage to benched Wartortle");
        return 0;
    }

    // Protective Poncho: prevent all damage to benched Pokémon with this tool attached
    if target_idx != 0
        && !skip_target_effects
        && attacking_player != target_player
        && has_tool(receiving_pokemon, CardId::B2147ProtectivePoncho)
    {
        debug!("Protective Poncho: Preventing all damage to benched Pokémon");
        return 0;
    }

    // Check for PreventAllDamageAndEffects (Shinx's Hide)
    if target_effects
        .iter()
        .any(|effect| matches!(effect, CardEffect::PreventAllDamageAndEffects))
    {
        debug!("PreventAllDamageAndEffects: Preventing all damage and effects");
        return 0;
    }

    // Check for PreventDamageFromBasic (Carracosta's Blocking Shell)
    if attacking_pokemon.card.is_basic()
        && target_effects
            .iter()
            .any(|effect| matches!(effect, CardEffect::PreventDamageFromBasic))
    {
        debug!("PreventDamageFromBasic: Preventing all damage from a Basic Pokémon");
        return 0;
    }

    // Calculate all modifiers
    let is_active_to_active = target_idx == 0 && attacking_idx == 0 && is_from_active_attack;
    let target_is_ex = receiving_pokemon.card.is_ex();
    let attacker_is_eevee_evolution = attacking_pokemon.evolved_from("Eevee");

    // Intimidating Fang changes the damage done by the opponent's Active, so it belongs to the
    // attacker-modifier stage before Weakness. It is still bypassed by attacks that ignore effects
    // on the opponent's Active because the Ability is carried by that Active.
    let intimidating_fang_reduction = if skip_target_effects {
        0
    } else {
        get_intimidating_fang_reduction(
            state,
            attacking_ref,
            (base_damage, target_player, target_idx),
            is_from_active_attack,
        )
    };
    let reductions = finite_damage_reductions(
        state,
        attacking_ref,
        (target_player, target_idx),
        is_from_active_attack,
        skip_target_effects,
    );
    let ability_damage_increase = get_ability_damage_increase(
        state,
        attacking_player,
        attacking_pokemon,
        is_active_to_active,
    );
    let increased_turn_effect_modifiers = get_increased_turn_effect_modifiers(
        state,
        is_active_to_active,
        target_is_ex,
        attacker_is_eevee_evolution,
        attacking_pokemon,
        attacking_player,
    );
    let increased_attack_specific_modifiers = get_increased_attack_specific_modifiers(
        attacking_pokemon,
        is_active_to_active,
        context.attack_name,
    );
    // Reductions and vulnerability are both "effects on the target"; ignore *any* of them (whether
    // they help or hurt the attacker) when the attack bypasses opponent-active effects.
    let increased_vulnerability_modifiers = if skip_target_effects {
        0
    } else {
        get_increased_vulnerability_modifiers(state, is_active_to_active, target_player)
    };
    let weakness_application = get_weakness_application(
        state,
        is_active_to_active,
        target_player,
        attacking_pokemon,
        context,
    );

    // Board-wide damage boost abilities (e.g., Lucario's Fighting Coach, Aegislash's Royal Command,
    // Unown's POWER, Politoed's Lordly Cheering). These check the attacker's board for
    // ability-holders and boost damage done to the opponent's Active Pokémon.
    // Only applies to active-to-active attacks (not damage moves like Dusknoir's Shadow Void)
    let board_ability_bonus = if is_active_to_active {
        get_board_ability_damage_bonus(state, attacking_player, attacking_pokemon)
    } else {
        0
    };

    let future_booster_damage_bonus = if is_active_to_active {
        get_future_booster_damage_bonus(attacking_pokemon)
    } else {
        0
    };

    let beastite_damage_bonus = if is_active_to_active {
        get_beastite_damage_bonus(state, attacking_player, attacking_pokemon)
    } else {
        0
    };

    // Stadium damage bonus (e.g., Training Area for Stage 1 Pokemon)
    // Only applies to attacks against the opponent's Active Pokemon
    let stadium_damage_bonus = if is_active_to_active {
        let training_area = get_training_area_damage_bonus(state, get_stage(attacking_pokemon));
        let arena_of_antiquity = state
            .pokemon_energy_types(attacking_pokemon)
            .into_iter()
            .map(|energy_type| {
                get_arena_of_antiquity_damage_bonus(state, energy_type, target_is_ex)
            })
            .max()
            .unwrap_or(0);
        training_area + arena_of_antiquity
    } else {
        0
    };

    debug!(
        "Attack: {:?}, IncreasedDamage: {}, IncreasedAttackSpecific: {}, IncreasedVulnerability: {}, ReducedDamage: {}, TurnEffectReduction: {}, HeavyHelmet: {}, MetalCoreBarrier: {}, SteelApron: {}, IntimidatingFangAttackerReduction: {}, AbilityReduction: {}, ConditionalAbilityReduction: {}, CoordinatedUnit: {}, AbilityIncrease: {}, BoardAbilityBonus: {}, StadiumBonus: {}, FutureBooster: {}",
        base_damage,
        increased_turn_effect_modifiers,
        increased_attack_specific_modifiers,
        increased_vulnerability_modifiers,
        reductions.card_effect,
        reductions.turn_effect,
        reductions.heavy_helmet,
        reductions.metal_core_barrier,
        reductions.steel_apron,
        intimidating_fang_reduction,
        reductions.ability,
        reductions.conditional_ability,
        reductions.coordinated_unit,
        ability_damage_increase,
        board_ability_bonus,
        stadium_damage_bonus,
        future_booster_damage_bonus
    );
    let pre_weakness = base_damage
        + ability_damage_increase
        + increased_turn_effect_modifiers
        + increased_attack_specific_modifiers
        + board_ability_bonus
        + stadium_damage_bonus
        + future_booster_damage_bonus
        + beastite_damage_bonus;
    // Growl, Moonblast and Teary Attack follow the Pokemon that was hit. Their reduction
    // affects each opposing target of that Pokemon's attack, including Bench damage,
    // even when the original user has switched out. Ability/status damage bypasses it.
    let carried_attack_reduction: u32 = if is_from_active_attack && attacking_player != target_player {
        attacking_pokemon.get_active_effects().iter().filter_map(|effect| match effect {
            CardEffect::ReducedAttackDamage { amount } => Some(*amount),
            _ => None,
        }).sum()
    } else {
        0
    };
    let pre_weakness = pre_weakness
        .saturating_sub(intimidating_fang_reduction)
        .saturating_sub(carried_attack_reduction);
    let after_weakness = match weakness_application {
        WeaknessApplication::None => pre_weakness,
        WeaknessApplication::Flat(amount) => pre_weakness + amount,
        WeaknessApplication::Double => pre_weakness * 2,
    };
    // Effects on the Defending Pokémon are step 4: after Weakness. This includes both
    // vulnerability (+damage) and reductions, with the final result floored at zero.
    let final_damage = after_weakness
        .saturating_add(increased_vulnerability_modifiers)
        .saturating_sub(reductions.total_u32_saturating());

    // Threshold-based prevention (e.g. Cascoon's Harden): prevent all damage if it is low enough.
    let prevented_by_threshold = target_effects
        .iter()
        .any(|effect| matches!(effect, CardEffect::PreventDamageIfLessOrEqual { threshold } if final_damage <= *threshold));
    if prevented_by_threshold {
        debug!("PreventDamageIfLessOrEqual: Preventing {final_damage} damage");
        return 0;
    }

    final_damage
}

/// Calculate type-specific damage boost from abilities like Lucario's Fighting Coach or Aegislash's Royal Command
/// Returns the bonus damage amount based on attacking Pokemon's energy type and abilities in play
/// POWER (Unown A4 085) works only while its controller has an Unown in play whose printed Ability
/// is something other than POWER (CHECK on A2a 034 / A2a 078, GUARD on A4 084). Two POWER Unown
/// never enable each other.
fn has_non_power_unown_in_play(state: &State, player: usize) -> bool {
    state.enumerate_in_play_pokemon(player).any(|(_, pokemon)| {
        pokemon.get_name() == "Unown"
            && has_any_in_play_ability(state, pokemon)
            && pokemon
                .card
                .get_ability()
                .is_some_and(|ability| ability.title != "POWER")
    })
}

/// Every damage bonus the *attacker's board* grants to an active-to-active attack, summed over the
/// attacking player's in-play Pokémon: the type-boost abilities (Lucario's Fighting Coach,
/// Aegislash's Royal Command), Unown's POWER, and Politoed's Lordly Cheering. Each of these is
/// printed on a Pokémon other than (or as well as) the attacker, so none can be read off the
/// attacker's own ability the way `get_ability_damage_increase` does.
fn get_board_ability_damage_bonus(
    state: &State,
    attacking_player: usize,
    attacking_pokemon: &PlayedCard,
) -> u32 {
    let attacker_energy_types = state.pokemon_energy_types(attacking_pokemon);
    if attacker_energy_types.is_empty() {
        return 0;
    }
    let power_unown_enabled = has_non_power_unown_in_play(state, attacking_player);

    let mut bonus = 0;

    // Check each Pokemon in play for board-wide damage-boosting abilities
    for (idx, pokemon) in state.enumerate_in_play_pokemon(attacking_player) {
        if let Some(mechanic) = get_in_play_ability_mechanic(state, pokemon) {
            match mechanic {
                AbilityMechanic::IncreaseDamageForTypeInPlay {
                    energy_type,
                    amount,
                } if attacker_energy_types.contains(energy_type) => {
                    debug!("Type damage bonus: Increasing damage by {}", amount);
                    bonus += amount;
                }
                AbilityMechanic::IncreaseDamageForTwoTypesInPlay {
                    energy_type_a,
                    energy_type_b,
                    amount,
                } if attacker_energy_types.contains(energy_type_a)
                    || attacker_energy_types.contains(energy_type_b) =>
                {
                    debug!("Type damage bonus: Increasing damage by {}", amount);
                    bonus += amount;
                }
                AbilityMechanic::UnownPower { amount } if power_unown_enabled => {
                    debug!("Unown POWER: Increasing damage by {amount}");
                    bonus += amount;
                }
                // "As long as this Pokémon is on your Bench" — idx 0 is the Active Spot.
                AbilityMechanic::IncreaseDamageForEvolutionsFromBench {
                    evolves_from,
                    amount,
                } if idx != 0 && attacking_pokemon.evolved_from(evolves_from) => {
                    debug!("Lordly Cheering: Increasing damage by {amount}");
                    bonus += amount;
                }
                _ => {}
            }
        }
    }

    bonus
}

// Get the attack cost, considering abilities and active card effects that modify attack costs.
pub(crate) fn get_attack_cost(
    base_cost: &[EnergyType],
    state: &State,
    attacking_player: usize,
) -> Vec<EnergyType> {
    let mut modified_cost = base_cost.to_vec();

    // Check if opponent has Goomy with Sticky Membrane in the active spot
    let opponent = (attacking_player + 1) % 2;
    if let Some(opponent_active) = &state.in_play_pokemon[opponent][0] {
        if matches!(
            get_in_play_ability_mechanic(state, opponent_active),
            Some(AbilityMechanic::IncreaseAttackCostForOpponentActive { amount: 1 })
        ) {
            modified_cost.push(EnergyType::Colorless);
        }
    }

    // Check if attacking active has an effect that increases attack cost
    let extra_colorless = state.in_play_pokemon[attacking_player][0]
        .as_ref()
        .map(|active| {
            active
                .get_active_effects()
                .into_iter()
                .map(|effect| match effect {
                    CardEffect::IncreasedAttackCost { amount } => amount as usize,
                    _ => 0,
                })
                .sum::<usize>()
        })
        .unwrap_or_default();
    modified_cost.extend(vec![EnergyType::Colorless; extra_colorless]);

    // Check for Barry-style turn effects that reduce colorless cost for specific pokemon
    if let Some(active) = &state.in_play_pokemon[attacking_player][0] {
        let active_name = active.get_name();
        let reduction: usize = state
            .get_current_turn_effects()
            .iter()
            .filter_map(|e| {
                if let TurnEffect::ReducedAttackCostForSpecificPokemon {
                    amount,
                    pokemon_names,
                } = e
                {
                    if pokemon_names.contains(&active_name) {
                        return Some(*amount as usize);
                    }
                }
                None
            })
            .sum();
        for _ in 0..reduction {
            if let Some(pos) = modified_cost
                .iter()
                .position(|e| *e == EnergyType::Colorless)
            {
                modified_cost.remove(pos);
            }
        }
    }

    modified_cost = reduce_attack_cost_by_abilities(modified_cost, state, attacking_player);

    modified_cost
}

/// The "attacks used by <someone> cost N less [X] Energy" abilities: Future System, Vigor Link
/// (Abomasnow A2a 021) and En-fruits-iastic (Cherubi A4 023 / A4b 025 / A4b 026). All of them
/// discount the attack the *Active* Pokémon is about to use; `AttackCostReductionScope` says where
/// the granting Pokémon sits and what has to hold. Multiple holders stack, one discount each.
fn reduce_attack_cost_by_abilities(
    mut cost: Vec<EnergyType>,
    state: &State,
    player: usize,
) -> Vec<EnergyType> {
    let Some(active) = state.in_play_pokemon[player][0].as_ref() else {
        return cost;
    };
    for (idx, source) in state.enumerate_in_play_pokemon(player) {
        let Some(AbilityMechanic::ReduceAttackCost {
            energy_type,
            amount,
            scope,
        }) = get_in_play_ability_mechanic(state, source)
        else {
            continue;
        };
        if !attack_cost_reduction_applies(state, player, scope, idx, active) {
            continue;
        }
        for _ in 0..*amount {
            if let Some(pos) = cost.iter().position(|e| e == energy_type) {
                debug!("{scope:?}: Reducing attack cost by 1 {energy_type:?}");
                cost.remove(pos);
            }
        }
    }
    cost
}

/// Whether a `ReduceAttackCost` ability held at board slot `source_idx` currently discounts the
/// attack `active` is about to use. Slot 0 is the Active Spot, so `source_idx == 0` is also the
/// test for the self-scoped ("attacks used by this Pokémon") variants.
fn attack_cost_reduction_applies(
    state: &State,
    player: usize,
    scope: &AttackCostReductionScope,
    source_idx: usize,
    active: &PlayedCard,
) -> bool {
    match scope {
        AttackCostReductionScope::YourFuturePokemon => is_future_pokemon(&active.get_name()),
        AttackCostReductionScope::SelfIfArceusInPlay => {
            source_idx == 0 && has_arceus_in_play(state, player)
        }
        AttackCostReductionScope::SelfIfToolAttached => {
            source_idx == 0 && !active.attached_tools.is_empty()
        }
    }
}

// Check if attached satisfies cost (considering Colorless and Serperior's ability)
pub(crate) fn contains_energy(
    pokemon: &PlayedCard,
    cost: &[EnergyType],
    state: &State,
    player: usize,
) -> bool {
    energy_missing(pokemon, cost, state, player).is_empty()
}

pub(crate) fn energy_missing(
    pokemon: &PlayedCard,
    cost: &[EnergyType],
    state: &State,
    player: usize,
) -> Vec<EnergyType> {
    let mut energy_missing = vec![];
    let mut effective_attached = pokemon.get_effective_attached_energy(state, player);

    // First try to match the non-colorless energy
    let non_colorless_cost = cost.iter().filter(|x| **x != EnergyType::Colorless);
    for energy in non_colorless_cost {
        let index = effective_attached.iter().position(|x| *x == *energy);
        if let Some(i) = index {
            effective_attached.remove(i);
        } else {
            energy_missing.push(*energy);
        }
    }
    // If all non-colorless energy is satisfied, check if there are enough colorless energy
    // with what is left
    let colorless_cost = cost.iter().filter(|x| **x == EnergyType::Colorless);
    let colorless_missing = colorless_cost
        .count()
        .saturating_sub(effective_attached.len());
    energy_missing.extend(vec![EnergyType::Colorless; colorless_missing]);
    energy_missing
}

/// Called when a Pokémon is knocked out
/// This is called before the Pokémon is discarded from play
pub(crate) fn on_knockout(
    state: &mut State,
    knocked_out_player: usize,
    knocked_out_idx: usize,
    attacking_ref: (usize, usize),
    is_from_active_attack: bool,
) {
    // A genuine opponent KO: an active attack that knocked out a Pokémon belonging to a
    // different player than the attacker (not a self/recoil KO).
    let is_opponent_attack = is_from_active_attack && attacking_ref.0 != knocked_out_player;
    apply_lucky_egg(
        state,
        knocked_out_player,
        knocked_out_idx,
        is_opponent_attack,
    );
    apply_electrical_cord(
        state,
        knocked_out_player,
        knocked_out_idx,
        is_from_active_attack,
    );
    apply_offload_pass(
        state,
        knocked_out_player,
        knocked_out_idx,
        is_opponent_attack,
    );
    apply_knockout_retaliation(
        state,
        knocked_out_player,
        knocked_out_idx,
        attacking_ref,
        is_opponent_attack,
    );
}

/// Pyukumuku's Innards Out ("do 50 damage to the Attacking Pokémon") and Spiritomb's Final Scream
/// ("do 10 damage to each of your opponent's Pokémon"): both fire only when the holder is Knocked
/// Out in the Active Spot by damage from an opponent's attack.
///
/// This runs while the Knocked Out Pokémon is still in play — `on_knockout` fires before the
/// discard — which is what lets `modify_damage` resolve the damage source. The damage is dealt
/// with `is_from_active_attack: false` because it comes from an Ability rather than an attack: no
/// Weakness, no counterattack in return, and no Rescue Scarf on whatever it Knocks Out. Any
/// Pokémon it does Knock Out is resolved by the follow-up pass at the end of `handle_knockouts`.
fn apply_knockout_retaliation(
    state: &mut State,
    knocked_out_player: usize,
    knocked_out_idx: usize,
    attacking_ref: (usize, usize),
    is_opponent_attack: bool,
) {
    if !is_opponent_attack || knocked_out_idx != 0 {
        return;
    }

    let retaliation = state.in_play_pokemon[knocked_out_player][knocked_out_idx]
        .as_ref()
        .and_then(
            |pokemon| match get_in_play_ability_mechanic(state, pokemon) {
                Some(AbilityMechanic::DamageOnKnockoutInActive { amount, target }) => {
                    Some((*amount, *target))
                }
                _ => None,
            },
        );
    let Some((amount, target)) = retaliation else {
        return;
    };

    let opponent = attacking_ref.0;
    let targets: Vec<(u32, usize, usize)> = match target {
        KnockoutDamageTarget::Attacker => vec![(amount, attacking_ref.0, attacking_ref.1)],
        KnockoutDamageTarget::EachOpponentPokemon => state
            .enumerate_in_play_pokemon(opponent)
            .map(|(idx, _)| (amount, opponent, idx))
            .collect(),
    };
    if targets.is_empty() {
        return;
    }

    debug!("On-knockout retaliation: dealing {amount} damage to {targets:?}");
    handle_damage_only(
        state,
        (knocked_out_player, knocked_out_idx),
        &targets,
        false,
        DamageModifierContext::default(),
    );
}

/// Lucky Egg: when the holder is Knocked Out by an opponent's attack, draw until hand has 5.
/// Position-agnostic — triggers whether the holder was KO'd in the Active Spot or on the Bench.
/// Lum Berry (A2 149) and Sitrus Berry (B1 218). Both trigger "at the end of each turn" — not
/// just their owner's — and both discard themselves only in the turn they actually do something,
/// so a berry attached with nothing to fix stays on for later.
///
/// One owner's whole board is scanned rather than just the Active. Indices are collected before
/// mutating, matching the Metal Core Barrier handling above.
fn apply_end_of_turn_berries_for_owner(player: usize, state: &mut State) {
    let lum_indices: Vec<usize> = state.in_play_pokemon[player]
        .iter()
        .enumerate()
        .filter(|(_, slot)| {
            slot.as_ref().is_some_and(|pokemon| {
                !pokemon.is_knocked_out()
                    && has_tool(pokemon, CardId::A2149LumBerry)
                    && pokemon.has_status_condition()
            })
        })
        .map(|(idx, _)| idx)
        .collect();
    for idx in lum_indices {
        debug!("Lum Berry: curing Special Conditions and discarding");
        if let Some(pokemon) = state.in_play_pokemon[player][idx].as_mut() {
            pokemon.cure_status_conditions();
        }
        state.discard_one_matching_tool(player, idx, CardId::A2149LumBerry);
    }

    for idx in 0..state.in_play_pokemon[player].len() {
        loop {
            let eligible = state.in_play_pokemon[player][idx]
                .as_ref()
                .is_some_and(|pokemon| {
                    !pokemon.is_knocked_out()
                        && has_tool(pokemon, CardId::B1218SitrusBerry)
                        // Recheck after every Berry: a successful heal can move the holder
                        // above half HP, leaving later copies attached.
                        && pokemon.get_remaining_hp() * 2 <= pokemon.get_effective_total_hp()
                });
            if !eligible {
                break;
            }

            debug!("Sitrus Berry: healing 30 and discarding");
            if state.heal_pokemon(player, idx, 30) == 0 {
                // Heal Block makes "If you do" false. Stop without consuming this or any
                // later copy; otherwise the unchanged board would also loop forever.
                break;
            }
            if !state.discard_one_matching_tool(player, idx, CardId::B1218SitrusBerry) {
                break;
            }
        }
    }
}

fn apply_lucky_egg(
    state: &mut State,
    knocked_out_player: usize,
    knocked_out_idx: usize,
    is_opponent_attack: bool,
) {
    let has_lucky_egg = {
        let knocked_out_pokemon = state.in_play_pokemon[knocked_out_player][knocked_out_idx]
            .as_ref()
            .expect("Pokemon should be there if knocked out");
        has_tool(knocked_out_pokemon, CardId::B3148LuckyEgg)
    };
    if !has_lucky_egg || !is_opponent_attack {
        return;
    }

    debug!("Lucky Egg: Drawing cards until hand has 5");
    let draws_needed = 5usize.saturating_sub(state.hands[knocked_out_player].len());
    for _ in 0..draws_needed {
        if state.decks[knocked_out_player].cards.is_empty() {
            break;
        }
        state.maybe_draw_card(knocked_out_player);
    }
}

/// Electrical Cord: "If the [L] Pokémon this card is attached to is in the Active Spot and is
/// Knocked Out by damage from an attack..." move up to 2 of its Lightning Energy to Benched
/// Pokémon (1 each to the two lowest-index Benched Pokémon). Note this uses the raw
/// `is_from_active_attack` flag, so it fires even on a self-KO from one's own active attack.
///
/// The early returns below only exit this helper (not `on_knockout`), letting control fall
/// through to `apply_offload_pass`. That is behavior-preserving because every return path here
/// is gated on the holder being a Lightning Pokémon, and no Lightning Pokémon carries the
/// `MoveAllTypedEnergyToBenchOnKnockout` ability that Offload Pass requires — so Offload Pass
/// would be a no-op in these cases regardless.
fn apply_electrical_cord(
    state: &mut State,
    knocked_out_player: usize,
    knocked_out_idx: usize,
    is_from_active_attack: bool,
) {
    let has_electrical_cord = {
        let knocked_out_pokemon = state.in_play_pokemon[knocked_out_player][knocked_out_idx]
            .as_ref()
            .expect("Pokemon should be there if knocked out");
        has_tool(knocked_out_pokemon, CardId::A3a065ElectricalCord)
            && state.pokemon_is_type(knocked_out_pokemon, EnergyType::Lightning)
    };
    if !has_electrical_cord {
        return;
    }
    // Only triggers if knocked out in active spot from an active attack
    if knocked_out_idx != 0 || !is_from_active_attack {
        return;
    }

    let copies = tool_count(
        state.in_play_pokemon[knocked_out_player][knocked_out_idx]
            .as_ref().expect("Knocked out Pokemon is still present"),
        CardId::A3a065ElectricalCord,
    );
    // Resolve the existing deterministic target policy, but remove Energy only when it has a
    // recipient. With fewer than two Benched Pokemon, the rest must remain for the KO discard.
    let bench_indices: Vec<_> = state.enumerate_bench_pokemon(knocked_out_player)
        .map(|(idx, _)| idx).take(2).collect();
    for _ in 0..copies {
        for &bench_idx in &bench_indices {
            let energy = {
                let holder = state.in_play_pokemon[knocked_out_player][knocked_out_idx]
                    .as_mut().expect("Knocked out Pokemon is still present");
                holder.attached_energy.iter().position(|e| *e == EnergyType::Lightning)
                    .map(|pos| holder.attached_energy.swap_remove(pos))
            };
            let Some(energy) = energy else { return; };
            state.in_play_pokemon[knocked_out_player][bench_idx]
                .as_mut().expect("Collected Bench recipient is still present")
                .attached_energy.push(energy);
        }
    }
}

/// Passimian ex's Offload Pass: if this Pokémon is Knocked Out in the Active Spot by an
/// opponent's attack, move all of its typed Energy to 1 of your Benched Pokémon (your choice).
fn apply_offload_pass(
    state: &mut State,
    knocked_out_player: usize,
    knocked_out_idx: usize,
    is_opponent_attack: bool,
) {
    if !is_opponent_attack || knocked_out_idx != 0 {
        return;
    }

    let offload_energy = state.in_play_pokemon[knocked_out_player][knocked_out_idx]
        .as_ref()
        .and_then(
            |pokemon| match get_in_play_ability_mechanic(state, pokemon) {
                Some(AbilityMechanic::MoveAllTypedEnergyToBenchOnKnockout { energy_type }) => {
                    Some(*energy_type)
                }
                _ => None,
            },
        );
    let Some(energy_type) = offload_energy else {
        return;
    };

    let bench_indices: Vec<usize> = state
        .enumerate_bench_pokemon(knocked_out_player)
        .map(|(idx, _)| idx)
        .collect();
    // With no Benched Pokémon there is nowhere to move the Energy (and the game is about to
    // end), so leave it to be discarded with this Pokémon.
    if bench_indices.is_empty() {
        return;
    }

    // Remove the Energy from the KO'd Pokémon first so it isn't sent to the discard
    // pile; the chosen Attach below re-attaches it to a Benched Pokémon.
    let moved = {
        let ko_pokemon = state.in_play_pokemon[knocked_out_player][knocked_out_idx]
            .as_mut()
            .expect("Pokemon should be there if knocked out");
        let before = ko_pokemon.attached_energy.len();
        ko_pokemon.attached_energy.retain(|&e| e != energy_type);
        (before - ko_pokemon.attached_energy.len()) as u32
    };
    if moved == 0 {
        return;
    }

    // One choice per Benched Pokémon; all of the Energy goes to the chosen one.
    // Pushed here (before promotion, which is inserted at the bottom of the stack)
    // so it resolves while the Bench is still intact.
    let choices = bench_indices
        .into_iter()
        .map(|idx| SimpleAction::Attach {
            attachments: vec![(moved, energy_type, idx)],
            is_turn_energy: false,
        })
        .collect::<Vec<_>>();
    state
        .move_generation_stack
        .push((knocked_out_player, choices));
}

pub(crate) fn on_attack_knockout(
    state: &mut State,
    attacking_ref: (usize, usize),
    knocked_out_player: usize,
    is_from_active_attack: bool,
) {
    if !is_from_active_attack || knocked_out_player == attacking_ref.0 {
        return;
    }

    // Resolved before taking the mutable borrow below, since the suppression check reads the board.
    let protects_self = state.in_play_pokemon[attacking_ref.0][attacking_ref.1]
        .as_ref()
        .is_some_and(|attacker| {
            has_in_play_ability_mechanic(
                state,
                attacker,
                &AbilityMechanic::ProtectSelfNextTurnAfterAttackKnockout,
            )
        });
    let Some(attacking_pokemon) = state.in_play_pokemon[attacking_ref.0][attacking_ref.1].as_mut()
    else {
        return;
    };
    if protects_self {
        attacking_pokemon.add_effect(CardEffect::PreventAllDamageAndEffects, 1);
    }

    // Lucky Mittens (B1 220): draw a card whenever the holder's attack knocks out one of the
    // opponent's Pokémon. The early return above already restricts this to genuine opponent
    // knockouts from an active attack.
    let mittens = tool_count(attacking_pokemon, CardId::B1220LuckyMittens);
    for _ in 0..mittens {
        debug!("Lucky Mittens: drawing a card for the attack knockout");
        state.maybe_draw_card(attacking_ref.0);
    }
}

// Test Colorless is wildcard when counting energy
#[cfg(test)]
mod tests {
    use crate::{card_ids::CardId, database::get_card_by_enum};

    use super::*;

    #[test]
    fn test_contains_energy() {
        let state = State::default();
        let fire_card = get_card_by_enum(CardId::A1033Charmander);
        let mut pokemon = to_playable_card(&fire_card, false);
        pokemon.attached_energy = vec![EnergyType::Fire, EnergyType::Fire, EnergyType::Fire];
        let cost = vec![EnergyType::Colorless, EnergyType::Fire];
        assert!(contains_energy(&pokemon, &cost, &state, 0));
    }

    #[test]
    fn test_get_attack_cost_with_increased_attack_cost_effect() {
        let mut state = State::default();
        let mut attacker = to_playable_card(&get_card_by_enum(CardId::A1001Bulbasaur), false);
        attacker.add_effect(CardEffect::IncreasedAttackCost { amount: 2 }, 1);
        state.in_play_pokemon[0][0] = Some(attacker);
        state.in_play_pokemon[1][0] = Some(to_playable_card(
            &get_card_by_enum(CardId::A1005Caterpie),
            false,
        ));

        let base_cost = vec![EnergyType::Grass];
        let modified = get_attack_cost(&base_cost, &state, 0);
        assert_eq!(
            modified,
            vec![
                EnergyType::Grass,
                EnergyType::Colorless,
                EnergyType::Colorless
            ]
        );
    }

    #[test]
    fn test_contains_energy_colorless() {
        let state = State::default();
        let fire_card = get_card_by_enum(CardId::A1033Charmander);
        let mut pokemon = to_playable_card(&fire_card, false);
        pokemon.attached_energy = vec![EnergyType::Fire, EnergyType::Fire, EnergyType::Water];
        let cost = vec![EnergyType::Colorless, EnergyType::Fire, EnergyType::Fire];
        assert!(contains_energy(&pokemon, &cost, &state, 0));
    }

    #[test]
    fn test_contains_energy_false_missing() {
        let state = State::default();
        let grass_card = get_card_by_enum(CardId::A1001Bulbasaur);
        let mut pokemon = to_playable_card(&grass_card, false);
        pokemon.attached_energy = vec![EnergyType::Grass, EnergyType::Grass, EnergyType::Fire];
        let cost = vec![EnergyType::Colorless, EnergyType::Fire, EnergyType::Water];
        assert!(!contains_energy(&pokemon, &cost, &state, 0));
    }

    #[test]
    fn test_contains_energy_double_colorless() {
        let state = State::default();
        let water_card = get_card_by_enum(CardId::A1053Squirtle);
        let mut pokemon = to_playable_card(&water_card, false);
        pokemon.attached_energy = vec![EnergyType::Water, EnergyType::Water, EnergyType::Fire];
        let cost = vec![EnergyType::Colorless, EnergyType::Colorless];
        assert!(contains_energy(&pokemon, &cost, &state, 0));
    }

    #[test]
    fn test_baby_pokemon_contain_energy() {
        let state = State::default();
        let baby_card = get_card_by_enum(CardId::A4032Magby);
        let mut pokemon = to_playable_card(&baby_card, false);
        pokemon.attached_energy = vec![];
        let cost = vec![];
        assert!(contains_energy(&pokemon, &cost, &state, 0));
    }

    #[test]
    fn test_can_play_support() {
        // Normal state should allow support cards
        let mut state = State::default();
        assert!(can_play_support(&state));

        // After playing a support, it should disallow
        state.has_played_support = true;
        assert!(!can_play_support(&state));

        // Reset state
        state.has_played_support = false;
        assert!(can_play_support(&state));

        // With Psyduck headache effect, it should disallow
        state.add_turn_effect(TurnEffect::NoSupportCards, 1);
        assert!(!can_play_support(&state));
    }

    #[test]
    fn test_giovanni_modifier() {
        // Create a basic state with attacking and defending Pokémon
        let mut state = State::default();

        // Set up attacker with a fixed damage attack
        let attacker = get_card_by_enum(CardId::A1001Bulbasaur);
        let played_attacker = to_playable_card(&attacker, false);
        state.in_play_pokemon[0][0] = Some(played_attacker);

        // Set up defender
        let defender = get_card_by_enum(CardId::A1033Charmander);
        let played_defender = to_playable_card(&defender, false);
        state.in_play_pokemon[1][0] = Some(played_defender);

        // Get base damage without Giovanni effect
        let attack = attacker.get_attacks()[0].clone();
        let base_damage = modify_damage(
            &state,
            (0, 0),
            (attack.fixed_damage, 1, 0),
            true,
            DamageModifierContext::default(),
        );

        // Add Giovanni effect
        state.add_turn_effect(TurnEffect::IncreasedDamage { amount: 10 }, 0);

        // Get damage with Giovanni effect
        let damage_with_giovanni = modify_damage(
            &state,
            (0, 0),
            (attack.fixed_damage, 1, 0),
            true,
            DamageModifierContext::default(),
        );

        // Verify Giovanni adds exactly 10 damage
        assert_eq!(
            damage_with_giovanni,
            base_damage + 10,
            "Giovanni should add exactly 10 damage to attacks"
        );
    }

    #[test]
    fn test_red_modifier_only_affects_ex() {
        let attacker_card = get_card_by_enum(CardId::A1001Bulbasaur);

        // Non-EX opponent should not receive extra damage
        let mut non_ex_state = State::default();
        non_ex_state.in_play_pokemon[0][0] = Some(to_playable_card(&attacker_card, false));
        let non_ex_defender = get_card_by_enum(CardId::A1033Charmander);
        non_ex_state.in_play_pokemon[1][0] = Some(to_playable_card(&non_ex_defender, false));
        let base_damage_non_ex = modify_damage(
            &non_ex_state,
            (0, 0),
            (40, 1, 0),
            true,
            DamageModifierContext::default(),
        );
        non_ex_state.add_turn_effect(TurnEffect::IncreasedDamageAgainstEx { amount: 20 }, 0);
        let damage_with_red_vs_non_ex = modify_damage(
            &non_ex_state,
            (0, 0),
            (40, 1, 0),
            true,
            DamageModifierContext::default(),
        );
        assert_eq!(
            damage_with_red_vs_non_ex, base_damage_non_ex,
            "Red should not increase damage against non-EX Pokémon"
        );

        // EX opponent should receive the bonus damage
        let mut ex_state = State::default();
        ex_state.in_play_pokemon[0][0] = Some(to_playable_card(&attacker_card, false));
        let ex_defender = get_card_by_enum(CardId::A3122SolgaleoEx);
        ex_state.in_play_pokemon[1][0] = Some(to_playable_card(&ex_defender, false));
        let base_damage_ex = modify_damage(
            &ex_state,
            (0, 0),
            (40, 1, 0),
            true,
            DamageModifierContext::default(),
        );
        ex_state.add_turn_effect(TurnEffect::IncreasedDamageAgainstEx { amount: 20 }, 0);
        let damage_with_red_vs_ex = modify_damage(
            &ex_state,
            (0, 0),
            (40, 1, 0),
            true,
            DamageModifierContext::default(),
        );
        assert_eq!(
            damage_with_red_vs_ex,
            base_damage_ex + 20,
            "Red should add 20 damage against Pokémon ex"
        );
    }

    #[test]
    fn test_cosmoem_reduced_damage() {
        // Arrange
        let mut state = State::default();
        let attacker = get_card_by_enum(CardId::A3122SolgaleoEx);
        let played_attacker = to_playable_card(&attacker, false);
        state.in_play_pokemon[0][0] = Some(played_attacker);
        let defender = get_card_by_enum(CardId::A3086Cosmoem);
        let played_defender = to_playable_card(&defender, false);
        state.in_play_pokemon[1][0] = Some(played_defender);
        state.in_play_pokemon[1][0]
            .as_mut()
            .unwrap()
            .add_effect(crate::effects::CardEffect::ReducedDamage { amount: 50 }, 1);

        // Act
        let damage_with_stiffen = modify_damage(
            &state,
            (0, 0),
            (120, 1, 0),
            true,
            DamageModifierContext::default(),
        );

        // Assert
        assert_eq!(
            damage_with_stiffen, 70,
            "Cosmoem's Stiffen should reduce damage by exactly 50"
        );
    }

    #[test]
    fn test_normal_evolution_works() {
        // Ivysaur evolves from Bulbasaur
        let ivysaur = get_card_by_enum(CardId::A1002Ivysaur);
        let bulbasaur = to_playable_card(&get_card_by_enum(CardId::A1001Bulbasaur), false);

        assert!(
            can_evolve_into(&State::default(), &ivysaur, &bulbasaur),
            "Ivysaur should be able to evolve from Bulbasaur"
        );
    }

    #[test]
    fn test_normal_evolution_fails_wrong_pokemon() {
        // Charizard cannot evolve from Bulbasaur
        let charizard = get_card_by_enum(CardId::A1035Charizard);
        let bulbasaur = to_playable_card(&get_card_by_enum(CardId::A1001Bulbasaur), false);

        assert!(
            !can_evolve_into(&State::default(), &charizard, &bulbasaur),
            "Charizard should not be able to evolve from Bulbasaur"
        );
    }

    #[test]
    fn test_normal_eevee_can_evolve_into_vaporeon() {
        // Regular Eevee (not Eevee ex) should only evolve normally
        let vaporeon = get_card_by_enum(CardId::A1080Vaporeon);
        let normal_eevee = to_playable_card(&get_card_by_enum(CardId::A1206Eevee), false);

        // Normal Eevee CAN evolve into Vaporeon (normal evolution)
        assert!(
            can_evolve_into(&State::default(), &vaporeon, &normal_eevee),
            "Normal Eevee should be able to evolve into Vaporeon normally"
        );
    }

    #[test]
    fn test_eevee_ex_can_evolve_into_vaporeon() {
        // Eevee ex should be able to evolve into Vaporeon (which evolves from "Eevee")
        let vaporeon = get_card_by_enum(CardId::A1080Vaporeon);
        let eevee_ex = to_playable_card(&get_card_by_enum(CardId::A3b056EeveeEx), false);

        assert!(
            can_evolve_into(&State::default(), &vaporeon, &eevee_ex),
            "Eevee ex should be able to evolve into Vaporeon via Veevee 'volve ability"
        );
    }

    #[test]
    fn test_eevee_ex_cannot_evolve_into_charizard() {
        // Eevee ex should NOT be able to evolve into Charizard (doesn't evolve from "Eevee")
        let charizard = get_card_by_enum(CardId::A1035Charizard);
        let eevee_ex = to_playable_card(&get_card_by_enum(CardId::A3b056EeveeEx), false);

        assert!(
            !can_evolve_into(&State::default(), &charizard, &eevee_ex),
            "Eevee ex should not be able to evolve into Charizard"
        );
    }

    #[test]
    fn test_aerodactyl_can_evolve_from_old_amber() {
        // Aerodactyl (regular) should be able to evolve from Old Amber fossil
        let aerodactyl = get_card_by_enum(CardId::A1210Aerodactyl);
        let old_amber = to_playable_card(&get_card_by_enum(CardId::A1218OldAmber), false);

        assert!(
            can_evolve_into(&State::default(), &aerodactyl, &old_amber),
            "Aerodactyl should be able to evolve from Old Amber fossil"
        );
    }

    #[test]
    fn test_aerodactyl_ex_can_evolve_from_old_amber() {
        // Aerodactyl ex should be able to evolve from Old Amber fossil
        let aerodactyl_ex = get_card_by_enum(CardId::A1a046AerodactylEx);
        let old_amber = to_playable_card(&get_card_by_enum(CardId::A1218OldAmber), false);

        assert!(
            can_evolve_into(&State::default(), &aerodactyl_ex, &old_amber),
            "Aerodactyl ex should be able to evolve from Old Amber fossil"
        );
    }

    #[test]
    fn test_omanyte_can_evolve_from_helix_fossil() {
        // Omanyte should be able to evolve from Helix Fossil
        let omanyte = get_card_by_enum(CardId::A1081Omanyte);
        let helix_fossil = to_playable_card(&get_card_by_enum(CardId::A1216HelixFossil), false);

        assert!(
            can_evolve_into(&State::default(), &omanyte, &helix_fossil),
            "Omanyte should be able to evolve from Helix Fossil"
        );
    }

    #[test]
    fn test_kabuto_can_evolve_from_dome_fossil() {
        // Kabuto should be able to evolve from Dome Fossil
        let kabuto = get_card_by_enum(CardId::A1158Kabuto);
        let dome_fossil = to_playable_card(&get_card_by_enum(CardId::A1217DomeFossil), false);

        assert!(
            can_evolve_into(&State::default(), &kabuto, &dome_fossil),
            "Kabuto should be able to evolve from Dome Fossil"
        );
    }

    #[test]
    fn test_aerodactyl_cannot_evolve_from_wrong_fossil() {
        // Aerodactyl should NOT be able to evolve from Helix Fossil (only Old Amber)
        let aerodactyl = get_card_by_enum(CardId::A1210Aerodactyl);
        let helix_fossil = to_playable_card(&get_card_by_enum(CardId::A1216HelixFossil), false);

        assert!(
            !can_evolve_into(&State::default(), &aerodactyl, &helix_fossil),
            "Aerodactyl should not be able to evolve from Helix Fossil"
        );
    }
}

#[cfg(test)]
mod persistent_defender_damage_tests {
    //! kd's `persistent_defender_damage`, checked against `modify_damage` on the same board: equal wherever only
    //! persistent modifiers are in play, and different exactly where a temporary one is left out.
    use super::*;
    use crate::database::get_card_by_enum;
    use rand::{rngs::StdRng, SeedableRng};

    fn mon(id: CardId) -> PlayedCard {
        PlayedCard::from_id(id)
    }

    fn duel(defender: Vec<PlayedCard>, attacker: Vec<PlayedCard>) -> State {
        let mut state = State::default();
        state.set_board(defender, attacker);
        state
    }

    /// `persistent_defender_damage` of player 1's Active on player 0's Pokemon in `target` (the Active unless the
    /// attack only hits the Bench), and what `modify_damage` does to it on the same board, for an attack with
    /// `effect`.
    fn both_on(state: &State, base: u32, effect: Option<&str>, target: usize) -> ((f64, f64), f64) {
        let context = DamageModifierContext { attack_name: None, attack_effect: effect };
        let attacker = state.get_active(1);
        let defender = state.in_play_pokemon[0][target].as_ref().unwrap();
        (
            persistent_defender_damage(state, 1, attacker, 0, defender, base, context, hit(target)),
            modify_damage(state, (1, 0), (base, 0, target), true, context) as f64,
        )
    }

    /// An attack on the Active hits it as the Active; one on the Bench is Bench damage.
    fn hit(target: usize) -> DefenderHit {
        if target == 0 {
            DefenderHit::Active
        } else {
            DefenderHit::Benched
        }
    }

    fn both(defender: PlayedCard, attacker: PlayedCard, base: u32) -> ((f64, f64), f64) {
        both_on(&duel(vec![defender], vec![attacker]), base, None, 0)
    }

    #[test]
    fn weakness_adds_20_when_weak_and_nothing_when_not() {
        // Riolu is weak to Psychic: Mewtwo ex's 50 does 70.
        assert_eq!(both(mon(CardId::B3079Riolu), mon(CardId::A1129MewtwoEx), 50), ((70.0, 70.0), 70.0));
        // Treecko is weak to Fire, not Psychic.
        assert_eq!(both(mon(CardId::B3005Treecko), mon(CardId::A1129MewtwoEx), 50), ((50.0, 50.0), 50.0));
        // A Colorless attacker hits no Weakness.
        assert_eq!(both(mon(CardId::B3079Riolu), mon(CardId::B1180Pidgey), 30), ((30.0, 30.0), 30.0));
        // Bonsly has no Weakness.
        assert_eq!(both(mon(CardId::B3078Bonsly), mon(CardId::A1129MewtwoEx), 50), ((50.0, 50.0), 50.0));
        // 0 stays 0, Weakness or not.
        assert_eq!(both(mon(CardId::B3079Riolu), mon(CardId::A1129MewtwoEx), 0), ((0.0, 0.0), 0.0));
        // Double Type: Single Strike Urshifu is [F] and [D]; Espeon is weak to Darkness.
        assert_eq!(both(mon(CardId::B3a020Espeon), mon(CardId::B3113SingleStrikeUrshifu), 110), ((130.0, 130.0), 130.0));
    }

    #[test]
    fn bounded_field_doubles_except_for_a_mega_ex() {
        let bounded = |attacker: CardId| {
            let mut state = duel(vec![mon(CardId::B3079Riolu)], vec![mon(attacker)]);
            state.active_stadium = Some(get_card_by_enum(CardId::B3155BoundedField));
            both_on(&state, 50, None, 0)
        };
        assert_eq!(bounded(CardId::A1129MewtwoEx), ((100.0, 100.0), 100.0));
        // Mega Altaria ex is Psychic too, but a Mega ex: the usual +20.
        assert_eq!(bounded(CardId::B1102MegaAltariaEx), ((70.0, 70.0), 70.0));
    }

    #[test]
    fn solid_shell_takes_20_off_and_can_take_it_to_0() {
        let shuckle = || mon(CardId::A4021ShuckleEx);
        assert_eq!(both(shuckle(), mon(CardId::A1001Bulbasaur), 40), ((20.0, 20.0), 20.0));
        assert_eq!(both(shuckle(), mon(CardId::A1008Weedle), 20), ((0.0, 0.0), 0.0));
    }

    #[test]
    fn persistent_tools_count() {
        // Heavy Helmet on a Retreat Cost 3 Pokemon: -20.
        let snorlax = mon(CardId::B3b055Snorlax).with_tool(get_card_by_enum(CardId::B1219HeavyHelmet));
        assert_eq!(both(snorlax, mon(CardId::A1001Bulbasaur), 40), ((20.0, 20.0), 20.0));
        // Steel Apron on a Metal Pokemon: -10.
        let skarmory = mon(CardId::A2111Skarmory).with_tool(get_card_by_enum(CardId::A4153SteelApron));
        assert_eq!(both(skarmory, mon(CardId::A1001Bulbasaur), 40), ((30.0, 30.0), 30.0));
    }

    #[test]
    fn safeguard_prevents_damage_from_an_ex_only() {
        assert_eq!(both(mon(CardId::A3066Oricorio), mon(CardId::A1129MewtwoEx), 50), ((0.0, 0.0), 0.0));
        assert_eq!(both(mon(CardId::A3066Oricorio), mon(CardId::B1180Pidgey), 30), ((30.0, 30.0), 30.0));
        // A Mega evolution is an ex.
        assert_eq!(both(mon(CardId::A3066Oricorio), mon(CardId::B1102MegaAltariaEx), 40), ((0.0, 0.0), 0.0));
    }

    #[test]
    fn intimidating_fang_comes_off_before_weakness() {
        // Luxray is weak to Fighting: 10 - 20 floors at 0 before Weakness adds 20.
        assert_eq!(both(mon(CardId::A3a015Luxray), mon(CardId::B3079Riolu), 10), ((20.0, 20.0), 20.0));
    }

    #[test]
    fn conditional_abilities_count_on_todays_board() {
        // Thick Fat-style typed reduction: Piloswine takes -20 from [R] or [W] attackers only.
        assert_eq!(both(mon(CardId::A2032Piloswine), mon(CardId::A1033Charmander), 40), ((20.0, 20.0), 20.0));
        assert_eq!(both(mon(CardId::A2032Piloswine), mon(CardId::A1001Bulbasaur), 40), ((40.0, 40.0), 40.0));
        // Resilience Link: Raichu takes -30 while its owner has Arceus in play.
        let raichu = |bench: Vec<PlayedCard>| {
            let mut mine = vec![mon(CardId::A2a026Raichu)];
            mine.extend(bench);
            both_on(&duel(mine, vec![mon(CardId::A1001Bulbasaur)]), 60, None, 0)
        };
        assert_eq!(raichu(vec![mon(CardId::A2a071ArceusEx)]), ((30.0, 30.0), 30.0));
        assert_eq!(raichu(vec![]), ((60.0, 60.0), 60.0));
        // Coordinated Unit: Falinks takes -20 with another Falinks in play.
        let falinks = |pair: bool| {
            let mine = if pair { vec![mon(CardId::B2092Falinks), mon(CardId::B2092Falinks)] } else { vec![mon(CardId::B2092Falinks)] };
            both_on(&duel(mine, vec![mon(CardId::A1001Bulbasaur)]), 40, None, 0)
        };
        assert_eq!(falinks(true), ((20.0, 20.0), 20.0));
        assert_eq!(falinks(false), ((40.0, 40.0), 40.0));
        // GUARD (a teammate's Ability): -10 for every Pokemon while a non-GUARD Unown is in play.
        let guarded = |check: bool| {
            let mut mine = vec![mon(CardId::B3005Treecko), mon(CardId::A4084Unown)];
            if check {
                mine.push(mon(CardId::A2a034Unown));
            }
            both_on(&duel(mine, vec![mon(CardId::A1001Bulbasaur)]), 40, None, 0)
        };
        assert_eq!(guarded(true), ((30.0, 30.0), 30.0));
        assert_eq!(guarded(false), ((40.0, 40.0), 40.0));
    }

    #[test]
    fn ice_face_counts_for_the_first_hit_only() {
        assert_eq!(both(mon(CardId::B1080Eiscue), mon(CardId::A1001Bulbasaur), 60), ((20.0, 60.0), 20.0));
        let damaged = mon(CardId::B1080Eiscue).with_remaining_hp(70);
        assert_eq!(both(damaged, mon(CardId::A1001Bulbasaur), 60), ((60.0, 60.0), 60.0));
        // A first hit that Ice Face absorbs leaves it at full HP, so every hit is absorbed.
        assert_eq!(both(mon(CardId::B1080Eiscue), mon(CardId::A1001Bulbasaur), 40), ((0.0, 0.0), 0.0));
    }

    #[test]
    fn disguise_prevents_the_first_hit_until_used() {
        assert_eq!(both(mon(CardId::B2073MimikyuEx), mon(CardId::A1001Bulbasaur), 40).0, (0.0, 40.0));
        let mut used = mon(CardId::B2073MimikyuEx);
        used.prevent_first_attack_damage_used = true;
        assert_eq!(both(used, mon(CardId::A1001Bulbasaur), 40), ((40.0, 40.0), 40.0));
        // The engine applies Disguise in handle_damage_only: two 40-damage attacks take 0, then 40.
        let mut state = duel(vec![mon(CardId::B2073MimikyuEx)], vec![mon(CardId::A1001Bulbasaur)]);
        let hp = |state: &State| state.get_active(0).get_remaining_hp();
        let full = hp(&state);
        handle_damage_only(&mut state, (1, 0), &[(40, 0, 0)], true, DamageModifierContext::default());
        assert_eq!(full - hp(&state), 0);
        handle_damage_only(&mut state, (1, 0), &[(40, 0, 0)], true, DamageModifierContext::default());
        assert_eq!(full - hp(&state), 40);
    }

    #[test]
    fn coin_flip_abilities_are_priced_in_expectation() {
        // Celestial Blessing: heads prevents the damage.
        assert_eq!(both(mon(CardId::A4080Togekiss), mon(CardId::A1001Bulbasaur), 40).0, (20.0, 20.0));
        // Guarded Grill: heads takes -100 from the damage before modifiers (Bastiodon is weak to Fire).
        assert_eq!(both(mon(CardId::A2114Bastiodon), mon(CardId::A1033Charmander), 40).0, (30.0, 30.0));
    }

    /// PINS THE ENGINE'S CURRENT ORDER, which is a known engine bug (rules/09, "Open engine bugs"): the engine takes
    /// Guarded Grill's -100 off the raw damage, before Weakness; by the rules (rules/02, step 4) it comes after.
    /// kd prices what the engine does, so the bot's clock agrees with the engine it plays in. When the engine is
    /// fixed, this fails on purpose: then make the matching one-line change in `persistent_defender_damage` (take
    /// the heads reduction off the damage after the rest of the pipeline, not off `base_damage`).
    #[test]
    fn guarded_grill_under_bounded_field_pins_the_engines_current_order_coin_cut_before_weakness() {
        // Charmeleon's Fire Claws (60) into Bastiodon (160 HP, weak to Fire) under Bounded Field. The engine today:
        // tails 60 x2 = 120, heads 60 - 100 = 0, so 60 on average. By the rules: tails 120, heads 120 - 100 = 20: 70.
        let charmeleon = mon(CardId::A1034Charmeleon).with_energy(vec![EnergyType::Fire; 3]);
        let mut state = duel(vec![mon(CardId::A2114Bastiodon)], vec![charmeleon]);
        state.active_stadium = Some(get_card_by_enum(CardId::B3155BoundedField));
        state.current_player = 1;
        state.turn_count = 5;
        let fire_claws = state
            .generate_possible_actions()
            .1
            .into_iter()
            .find(|action| matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Fire Claws"))
            .expect("Fire Claws is playable");
        let (probabilities, mutations) = crate::actions::forecast_action(&state, &fire_claws).into_branches();
        let engine: f64 = probabilities
            .iter()
            .zip(mutations)
            .map(|(probability, mutate)| {
                let mut branch = state.clone();
                mutate(&mut StdRng::seed_from_u64(20_000_000_001), &mut branch, &fire_claws);
                probability * (160 - branch.get_active(0).get_remaining_hp()) as f64
            })
            .sum();
        assert_eq!(engine, 60.0, "the engine's Guarded Grill order changed: see this test's doc comment");
        assert_eq!(both_on(&state, 60, None, 0).0, (engine, engine));
    }

    #[test]
    fn the_attacks_own_text_is_honoured() {
        // Quick Straight isn't affected by Weakness: Luxray (weak to Fighting) takes 50 - 20 (Fang).
        let straight = "This attack's damage isn't affected by Weakness.";
        let state = duel(vec![mon(CardId::A3a015Luxray)], vec![mon(CardId::B1124HitmonchanEx)]);
        assert_eq!(both_on(&state, 50, Some(straight), 0), ((30.0, 30.0), 30.0));
        // Chakra Fist ignores effects on the opponent's Active: Safeguard is bypassed, Weakness isn't.
        let chakra = "If this Pokémon has any [P] Energy attached, this attack does 40 more damage. This attack's damage isn't affected by any effects on your opponent's Active Pokémon.";
        let state = duel(vec![mon(CardId::A3066Oricorio)], vec![mon(CardId::PB029MegaMedichamEx)]);
        assert_eq!(both_on(&state, 100, Some(chakra), 0), ((120.0, 120.0), 120.0));
        // Swift ignores both: Solid Shell and the coin flip are bypassed.
        let swift = "This attack's damage isn't affected by Weakness or by any effects on your opponent's Active Pokémon.";
        let state = duel(vec![mon(CardId::A4021ShuckleEx)], vec![mon(CardId::B4032Staryu)]);
        assert_eq!(both_on(&state, 20, Some(swift), 0), ((20.0, 20.0), 20.0));
        let state = duel(vec![mon(CardId::A4080Togekiss)], vec![mon(CardId::B4032Staryu)]);
        assert_eq!(both_on(&state, 20, Some(swift), 0).0, (20.0, 20.0));
    }

    #[test]
    fn bench_damage_is_priced_as_the_engine_prices_it() {
        let heatmor = || vec![mon(CardId::B1044Heatmor)];
        // Heatmor's Tongue Whip (30 to a Benched Pokemon) on a benched Vespiquen ex, weak to Fire: 30, not 50.
        let state = duel(vec![mon(CardId::A1001Bulbasaur), mon(CardId::B4011VespiquenEx)], heatmor());
        assert_eq!(both_on(&state, 30, None, 1), ((30.0, 30.0), 30.0));
        // Protective Poncho and Shell Shield prevent Bench damage.
        let poncho = mon(CardId::B4011VespiquenEx).with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho));
        let state = duel(vec![mon(CardId::A1001Bulbasaur), poncho], heatmor());
        assert_eq!(both_on(&state, 30, None, 1), ((0.0, 0.0), 0.0));
        let state = duel(vec![mon(CardId::A1001Bulbasaur), mon(CardId::B1a018Wartortle)], heatmor());
        assert_eq!(both_on(&state, 30, None, 1), ((0.0, 0.0), 0.0));
        // Intimidating Fang works from the Active Spot: a benched Luxray's does nothing, an Active Luxray's cuts the
        // damage to a benched Pokemon.
        let state = duel(vec![mon(CardId::A1001Bulbasaur), mon(CardId::A3a015Luxray)], heatmor());
        assert_eq!(both_on(&state, 30, None, 1), ((30.0, 30.0), 30.0));
        let state = duel(vec![mon(CardId::A3a015Luxray), mon(CardId::B4011VespiquenEx)], heatmor());
        assert_eq!(both_on(&state, 30, None, 1), ((10.0, 10.0), 10.0));
    }

    #[test]
    fn temporary_effects_are_left_out() {
        // NoWeakness and ReducedDamage from an attack last one turn: modify_damage applies them, kd doesn't.
        let mut riolu = mon(CardId::B3079Riolu);
        riolu.add_effect(CardEffect::NoWeakness, 1);
        riolu.add_effect(CardEffect::ReducedDamage { amount: 20 }, 1);
        assert_eq!(both(riolu, mon(CardId::A1129MewtwoEx), 50), ((70.0, 70.0), 30.0));
        // A stored ReduceDamageFromAttacks (an attack's, not an Ability's) is left out too.
        let mut treecko = mon(CardId::B3005Treecko);
        treecko.add_effect(CardEffect::ReduceDamageFromAttacks { amount: 20 }, 1);
        assert_eq!(both(treecko, mon(CardId::A1129MewtwoEx), 50), ((50.0, 50.0), 30.0));
        // Metal Core Barrier discards itself at the end of the opponent's turn.
        let skarmory =
            mon(CardId::A2111Skarmory).with_tool(get_card_by_enum(CardId::B2148MetalCoreBarrier));
        assert_eq!(both(skarmory, mon(CardId::A1001Bulbasaur), 40), ((40.0, 40.0), 0.0));
    }
}
