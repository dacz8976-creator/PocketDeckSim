use log::debug;

use crate::{
    actions::{abilities::AbilityMechanic, get_ability_mechanic, SimpleAction},
    card_ids::CardId,
    effects::CardEffect,
    models::{EnergyType, PlayedCard},
    tools::{has_tool, tool_count},
    State,
};

/// Some cards counterattack either because of RockyHelmet or because of their own ability.
pub(crate) fn get_counterattack_damage(card: &PlayedCard) -> u32 {
    let mut total_damage = 0;
    if has_tool(card, CardId::A2148RockyHelmet) {
        total_damage += 20 * tool_count(card, CardId::A2148RockyHelmet);
    }

    // Temporary counterattack effects (e.g. Alolan Sandslash's Spike Armor).
    total_damage += card
        .get_active_effects()
        .iter()
        .filter_map(|effect| match effect {
            CardEffect::Counterattack { amount } => Some(*amount),
            _ => None,
        })
        .sum::<u32>();

    // Some cards have it as an ability
    let card_id = CardId::from_card_id(&card.card.get_id());
    match card_id {
        Some(CardId::A1061Poliwrath)
        | Some(CardId::A1a056Druddigon)
        | Some(CardId::A2b028Pawmot)
        | Some(CardId::A3a052Ferrothorn)
        | Some(CardId::A4a065Zangoose)
        | Some(CardId::B1297Poliwrath)
        | Some(CardId::PA054Pawmot) => {
            total_damage += 20;
        }
        _ => {}
    }

    total_damage
}

/// Jellicent's Bouncy Body: "If this Pokémon is in the Active Spot and is damaged by an attack from
/// your opponent's Pokémon, take a [W] Energy from your Energy Zone and attach it to 1 of your
/// Benched Pokémon."
///
/// Fires from the same on-damaged spot as the counterattack abilities and Poison Barb, so the
/// caller has already checked that this was an opponent's attack landing on `player`'s Active
/// Pokémon. Which Benched Pokémon receives the Energy is the defender's choice, so this pushes a
/// list of `Attach` actions onto the `move_generation_stack` (mirroring Passimian ex's Offload
/// Pass) rather than resolving it here. An empty Bench leaves no legal target, so nothing is
/// pushed and the Energy is simply not taken.
pub(crate) fn maybe_attach_energy_on_damaged(state: &mut State, player: usize) {
    let energy_type = state.in_play_pokemon[player][0]
        .as_ref()
        .and_then(|pokemon| match get_ability_mechanic(&pokemon.card) {
            Some(AbilityMechanic::AttachEnergyFromZoneToBenchOnDamaged { energy_type }) => {
                Some(*energy_type)
            }
            _ => None,
        });
    let Some(energy_type) = energy_type else {
        return;
    };

    let choices = bench_attach_choices(state, player, energy_type);
    if choices.is_empty() {
        return;
    }
    debug!("Bouncy Body: player {player} attaches a {energy_type:?} Energy to their Bench");
    state.move_generation_stack.push((player, choices));
}

fn bench_attach_choices(
    state: &State,
    player: usize,
    energy_type: EnergyType,
) -> Vec<SimpleAction> {
    state
        .enumerate_bench_pokemon(player)
        .map(|(in_play_idx, _)| SimpleAction::Attach {
            attachments: vec![(1, energy_type, in_play_idx)],
            is_turn_energy: false,
        })
        .collect()
}

/// Dark Pendant (A4 154): "If the [D] Pokémon this card is attached to is in the Active Spot and
/// is damaged by an attack from your opponent's Pokémon, your opponent reveals a random card from
/// their hand and shuffles it into their deck."
///
/// Fires from the same on-damaged spot as Poison Barb and Jellicent's Bouncy Body, so the caller
/// has already checked that this was an opponent's attack landing on `player`'s Active Pokémon.
/// Which card is revealed is random and the on-damaged path carries no RNG, so the disruption is
/// queued as a one-option `move_generation_stack` entry and resolved when that action is applied.
/// Nothing is queued when the attacker's hand is empty.
pub(crate) fn maybe_shuffle_attacker_hand_card_on_damaged(
    state: &mut State,
    player: usize,
    attacking_player: usize,
) {
    let count = state.in_play_pokemon[player][0].as_ref().map_or(0, |pokemon| {
        if state.pokemon_is_type(pokemon, EnergyType::Darkness) {
            tool_count(pokemon, CardId::A4154DarkPendant)
        } else { 0 }
    });
    if state.hands[attacking_player].is_empty() { return; }
    for _ in 0..count {
        state.move_generation_stack.push((player, vec![SimpleAction::ShuffleRandomOpponentHandCard]));
    }
}

/// Check if the defending Pokemon should poison the attacker when damaged.
/// Returns true if the attacker should be poisoned.
pub(crate) fn should_poison_attacker(card: &PlayedCard) -> bool {
    if has_tool(card, CardId::A3146PoisonBarb) {
        return true;
    }

    // Some cards have it as an ability (Dragalge ex's Poison Point)
    let card_id = CardId::from_card_id(&card.card.get_id());
    match card_id {
        Some(CardId::B1160DragalgeEx)
        | Some(CardId::B1263DragalgeEx)
        | Some(CardId::B1281DragalgeEx) => {
            return true;
        }
        _ => {}
    }

    false
}
