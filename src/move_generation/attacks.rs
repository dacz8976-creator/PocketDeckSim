use crate::{
    actions::{
        abilities::AbilityMechanic, get_ability_mechanic, has_ability_mechanic, SimpleAction,
    },
    card_ids::CardId,
    effects::CardEffect,
    hooks::{contains_energy, get_attack_cost},
    models::{Attack, PlayedCard},
    tools::has_tool,
    State,
};

pub(crate) fn generate_attack_actions(state: &State) -> Vec<SimpleAction> {
    let current_player = state.current_player;
    let mut actions = Vec::new();
    if let Some(active_pokemon) = &state.in_play_pokemon[current_player][0] {
        // Fossil cards cannot attack
        if active_pokemon.is_fossil() {
            return actions;
        }

        // Check if the active Pokémon has the CannotAttack effect
        let active_effects = active_pokemon.get_active_effects();
        let cannot_attack = active_effects
            .iter()
            .any(|effect| matches!(effect, CardEffect::CannotAttack));
        if cannot_attack {
            return actions;
        }

        // Regigigas' Seal of Antiquity: the Ability seals its own holder's attacks unless the
        // named Pokémon are all on the Bench.
        if is_sealed_by_bench_requirement(state, current_player, active_pokemon) {
            return actions;
        }

        let restricted_attack_names: Vec<String> = active_effects
            .iter()
            .filter_map(|effect| match effect {
                CardEffect::CannotUseAttack(attack_name) => Some(attack_name.clone()),
                _ => None,
            })
            .collect();

        // The active Pokémon's own attacks, plus any granted by Celebi's Time Recall.
        let mut available_attacks: Vec<Attack> = active_pokemon.get_attacks().clone();
        available_attacks.extend(time_recall_attacks(state, current_player, active_pokemon));

        let mut offered: Vec<Attack> = Vec::new();
        for attack in available_attacks {
            // Avoid offering an identical attack twice (e.g. an attack kept unchanged across an
            // evolution). Dedup on the whole Attack, not just the title: a previous evolution can
            // share an attack's name while differing in cost/damage/effect (e.g. Swirlix's and
            // Slurpuff's "Sweets Relay"), and those are genuinely distinct, usable attacks.
            if offered.contains(&attack) {
                continue;
            }
            if restricted_attack_names.contains(&attack.title) {
                continue;
            }
            let modified_cost = get_attack_cost(&attack.energy_required, state, current_player);
            if contains_energy(active_pokemon, &modified_cost, state, current_player) {
                offered.push(attack.clone());
                actions.push(SimpleAction::Attack(attack));
            }
        }
    }
    actions
}

/// Regigigas' Seal of Antiquity: "If you don't have Regirock, Regice, and Registeel on your Bench,
/// this Pokémon can't attack." True when the Active Pokémon carries such an Ability and its
/// controller's Bench is missing at least one of the required names.
///
/// Only the Bench counts, so a Regi in the Active Spot does not satisfy the requirement — and the
/// restriction is self-scoped, so a Benched holder never seals anyone else's attacks.
fn is_sealed_by_bench_requirement(
    state: &State,
    player: usize,
    active_pokemon: &PlayedCard,
) -> bool {
    let Some(AbilityMechanic::CannotAttackWithoutBenchedNames {
        required_bench_names,
    }) = get_ability_mechanic(&active_pokemon.card)
    else {
        return false;
    };

    let bench_names: Vec<String> = state
        .enumerate_bench_pokemon(player)
        .map(|(_, pokemon)| pokemon.get_name())
        .collect();
    !required_bench_names
        .iter()
        .all(|required| bench_names.iter().any(|name| name == required))
}

/// Celebi's Time Recall: while a Pokémon with the ability is in play, each of your evolved
/// Pokémon can use any attack from its previous Evolutions. We only need the active Pokémon's
/// previous-evolution attacks here, since only the active Pokémon can attack. The previous
/// evolutions are the under-cards recorded on the active when it evolved (`cards_behind`).
fn time_recall_attacks(state: &State, player: usize, active_pokemon: &PlayedCard) -> Vec<Attack> {
    let time_recall_active = state
        .enumerate_in_play_pokemon(player)
        .any(|(_, pokemon)| has_ability_mechanic(&pokemon.card, &AbilityMechanic::TimeRecall));
    // Memory Light (A4a 068) grants the same effect, but scoped to its holder rather than to
    // every evolved Pokémon you control.
    let has_memory_light = has_tool(active_pokemon, CardId::A4a068MemoryLight);
    if !time_recall_active && !has_memory_light {
        return Vec::new();
    }

    active_pokemon
        .cards_behind
        .iter()
        .flat_map(|card| card.get_attacks())
        .collect()
}
