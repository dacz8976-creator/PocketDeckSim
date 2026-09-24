use crate::{
    actions::{
        abilities::AbilityMechanic, attacks::Mechanic, get_in_play_ability_mechanic,
        has_in_play_ability_mechanic, SimpleAction, EFFECT_MECHANIC_MAP,
    },
    card_ids::CardId,
    effects::CardEffect,
    hooks::{contains_energy, get_attack_cost, special_condition_blocks_attack_or_retreat},
    models::{Attack, EnergyType, PlayedCard},
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

        if special_condition_blocks_attack_or_retreat(active_pokemon) {
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
            // "You can use this attack only if ..." conditions (e.g. Mesprit's Supreme Blast).
            if !attack_usage_condition_met(state, current_player, &attack) {
                continue;
            }
            let modified_cost = get_attack_cost(&attack.energy_required, state, current_player);
            if contains_energy(active_pokemon, &modified_cost, state, current_player)
                || alternative_cost_payable(state, current_player, active_pokemon, &attack)
            {
                offered.push(attack.clone());
                actions.push(SimpleAction::Attack(attack));
            }
        }
    }
    actions
}

/// Look up the `Mechanic` for an attack's effect text, if any.
fn attack_mechanic(attack: &Attack) -> Option<&'static Mechanic> {
    attack
        .effect
        .as_deref()
        .and_then(|effect_text| EFFECT_MECHANIC_MAP.get(effect_text))
}

/// "You can use this attack only if ..." conditions gate the attack at move generation
/// (e.g. Mesprit's Supreme Blast requires Uxie and Azelf on the attacker's Bench).
fn attack_usage_condition_met(state: &State, player: usize, attack: &Attack) -> bool {
    match attack_mechanic(attack) {
        Some(Mechanic::RequiresBenchedNamesSelfDiscardAllEnergy {
            required_bench_names,
        }) => {
            let bench_names: Vec<String> = state
                .enumerate_bench_pokemon(player)
                .map(|(_, pokemon)| pokemon.get_name())
                .collect();
            required_bench_names
                .iter()
                .all(|required| bench_names.iter().any(|name| name == required))
        }
        _ => true,
    }
}

/// "If <condition>, this attack can be used for <cost>" effects (e.g. Boltund's Defiant Spark,
/// Veluza's Shedding Spiral): when the condition holds, the attack is offered if the attacker
/// can pay the alternative cost (run through the usual cost modifiers) even though it cannot
/// pay the printed cost.
fn alternative_cost_payable(
    state: &State,
    player: usize,
    active_pokemon: &PlayedCard,
    attack: &Attack,
) -> bool {
    let Some(alternative_cost) = alternative_attack_cost(state, player, active_pokemon, attack)
    else {
        return false;
    };
    let modified_cost = get_attack_cost(&alternative_cost, state, player);
    contains_energy(active_pokemon, &modified_cost, state, player)
}

/// The alternative cost of `attack` if its condition currently holds for `player`.
fn alternative_attack_cost(
    state: &State,
    player: usize,
    active_pokemon: &PlayedCard,
    attack: &Attack,
) -> Option<Vec<EnergyType>> {
    match attack_mechanic(attack) {
        Some(Mechanic::AlternativeCostIfDamaged { cost }) => {
            active_pokemon.is_damaged().then(|| cost.clone())
        }
        Some(Mechanic::AlternativeCostIfDeckEmpty { cost }) => {
            state.decks[player].cards.is_empty().then(|| cost.clone())
        }
        _ => None,
    }
}

/// Regigigas' Seal of Antiquity: "If you don't have Regirock, Regice, and Registeel on your Bench,
/// this Pokémon can't attack." True when the Active Pokémon carries such an Ability and its
/// controller's Bench is missing at least one of the required names.
///
/// Only the Bench counts, so a Regi in the Active Spot does not satisfy the requirement — and the
/// restriction is self-scoped, so a Benched holder never seals anyone else's attacks.
///
/// Seal of Antiquity is a drawback Ability, so switching it off *helps* its holder: read it through
/// the suppression-aware accessor, and Alolan Muk's Power of Alchemy (or a `NoAbilities` effect)
/// frees Regigigas — a Basic — to attack with no Regis benched at all.
fn is_sealed_by_bench_requirement(
    state: &State,
    player: usize,
    active_pokemon: &PlayedCard,
) -> bool {
    let Some(AbilityMechanic::CannotAttackWithoutBenchedNames {
        required_bench_names,
    }) = get_in_play_ability_mechanic(state, active_pokemon)
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
    let time_recall_active = state.enumerate_in_play_pokemon(player).any(|(_, pokemon)| {
        has_in_play_ability_mechanic(state, pokemon, &AbilityMechanic::TimeRecall)
    });
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
