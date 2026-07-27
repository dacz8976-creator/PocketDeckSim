use crate::{
    actions::{
        abilities::{AbilityMechanic, NoRetreatCostCondition, NoRetreatCostTarget},
        get_in_play_ability_mechanic,
    },
    card_ids::CardId,
    effects::{CardEffect, TurnEffect},
    hooks::core::has_named_pokemon_in_play,
    models::{Card, EnergyType, PlayedCard},
    stadiums::get_peculiar_plaza_retreat_reduction,
    tools::has_tool,
    State,
};

pub(crate) fn can_retreat(state: &State) -> bool {
    let active = state.get_active(state.current_player);

    // Check if active card has CardEffect::NoRetreat
    let has_no_retreat_effect = active.get_active_effects().contains(&CardEffect::NoRetreat);

    // Check if active card is a Fossil (Fossils can never retreat)
    let is_fossil = active.is_fossil();

    !state.has_retreated && !has_no_retreat_effect && !is_fossil
}

/// Resolves the passive `AbilityMechanic::NoRetreatCost` family (Speed Link, Fluffy Flight,
/// Fantastical Floating, Retreat Directive, Surge Surfer, Wimp Out) for the Pokémon that is about
/// to retreat.
///
/// Two shapes are folded together here: abilities that only free their own holder
/// ([`NoRetreatCostTarget::ThisPokemon`], read straight off `card`), and abilities that free your
/// Active Pokémon from anywhere in play ([`NoRetreatCostTarget::YourActive`] and
/// [`NoRetreatCostTarget::YourActiveNamed`], which need a scan of your board for the granting
/// Pokémon). Like the other owner-scoped retreat modifiers in this file, "your" means
/// `state.current_player`.
fn has_no_retreat_cost_ability(state: &State, card: &PlayedCard) -> bool {
    let player = state.current_player;
    if let Some(AbilityMechanic::NoRetreatCost {
        target: NoRetreatCostTarget::ThisPokemon,
        condition,
    }) = get_in_play_ability_mechanic(state, card)
    {
        if no_retreat_cost_condition_holds(state, player, condition) {
            return true;
        }
    }
    state
        .enumerate_in_play_pokemon(player)
        .any(|(_, source)| grants_active_no_retreat_cost(state, player, source, card))
}

/// True if `source` (one of `player`'s in-play Pokémon) has an ability that removes the Retreat
/// Cost of `active`, their Active Pokémon.
fn grants_active_no_retreat_cost(
    state: &State,
    player: usize,
    source: &PlayedCard,
    active: &PlayedCard,
) -> bool {
    let Some(AbilityMechanic::NoRetreatCost { target, condition }) =
        get_in_play_ability_mechanic(state, source)
    else {
        return false;
    };
    let targets_active = match target {
        // Handled by reading the retreating Pokémon's own ability, not by this board scan.
        NoRetreatCostTarget::ThisPokemon => false,
        NoRetreatCostTarget::YourActive => true,
        NoRetreatCostTarget::YourActiveNamed(name) => active.get_name() == *name,
    };
    targets_active && no_retreat_cost_condition_holds(state, player, condition)
}

fn no_retreat_cost_condition_holds(
    state: &State,
    player: usize,
    condition: &NoRetreatCostCondition,
) -> bool {
    match condition {
        NoRetreatCostCondition::Always => true,
        NoRetreatCostCondition::NamedPokemonInPlay(names) => {
            has_named_pokemon_in_play(state, player, names)
        }
        NoRetreatCostCondition::StadiumInPlay => state.active_stadium.is_some(),
        NoRetreatCostCondition::YourFirstTurn => state.is_users_first_turn(),
    }
}

pub(crate) fn get_retreat_cost(state: &State, card: &PlayedCard) -> Vec<EnergyType> {
    if let Card::Pokemon(pokemon_card) = &card.card {
        if matches!(
            get_in_play_ability_mechanic(state, card),
            Some(AbilityMechanic::NoRetreatIfHasEnergy)
        ) && !card.attached_energy.is_empty()
        {
            return vec![];
        }
        if has_no_retreat_cost_ability(state, card) {
            return vec![];
        }
        let mut normal_cost = pokemon_card.retreat_cost.clone();
        if has_tool(card, CardId::A4a067InflatableBoat)
            && state.pokemon_is_type(card, EnergyType::Water)
        {
            normal_cost.pop();
        }
        if has_tool(card, CardId::B2a087BigAirBalloon) && pokemon_card.stage == 2 {
            return vec![];
        }
        if has_tool(card, CardId::B3b064SmallBalloon) && pokemon_card.stage == 0 {
            normal_cost.pop();
        }
        // Implement Retreat Cost Modifiers here
        let mut to_subtract = state
            .get_current_turn_effects()
            .iter()
            .filter(|x| matches!(x, TurnEffect::ReducedRetreatCost { .. }))
            .map(|x| match x {
                TurnEffect::ReducedRetreatCost { amount } => *amount,
                _ => 0,
            })
            .sum::<u8>();

        // Shaymin's Sky Support: As long as this Pokémon is on your Bench, your Active Basic Pokémon's Retreat Cost is 1 less.
        if pokemon_card.stage == 0 {
            // Only affects Basic Pokemon
            let current_player = state.current_player;
            for (_idx, benched_pokemon) in state.enumerate_bench_pokemon(current_player) {
                if matches!(
                    get_in_play_ability_mechanic(state, benched_pokemon),
                    Some(
                        AbilityMechanic::ReduceRetreatCostOfYourActiveBasicFromBench { amount: 1 }
                    )
                ) {
                    to_subtract += 1;
                }
            }
        }
        {
            let active_energy_types = state.pokemon_energy_types(card);
            let current_player = state.current_player;
            for (_idx, benched_pokemon) in state.enumerate_bench_pokemon(current_player) {
                if let Some(AbilityMechanic::ReduceRetreatCostOfYourActiveTypedFromBench {
                    energy_type,
                    amount,
                }) = get_in_play_ability_mechanic(state, benched_pokemon)
                {
                    if active_energy_types.contains(energy_type) {
                        to_subtract += *amount as u8;
                    }
                }
            }
        }

        // Peculiar Plaza: Psychic Pokemon retreat cost is 2 less
        to_subtract += state
            .pokemon_energy_types(card)
            .into_iter()
            .map(|energy_type| get_peculiar_plaza_retreat_reduction(state, energy_type))
            .max()
            .unwrap_or(0);

        // Retreat Effects accumulate so we add them.
        for _ in 0..to_subtract {
            normal_cost.pop(); // Remove one colorless energy from retreat cost
        }

        // Oranguru's Primate's Trap: "its Retreat Cost is 1 [C] more", stored on the Pokémon
        // itself. Added after the reductions so it can't be cancelled out of existence by a pop.
        let extra_retreat_cost: u8 = card
            .get_active_effects()
            .iter()
            .filter_map(|effect| match effect {
                CardEffect::IncreasedRetreatCost { amount } => Some(*amount),
                _ => None,
            })
            .sum();
        for _ in 0..extra_retreat_cost {
            normal_cost.push(EnergyType::Colorless);
        }

        // Ariados Trap Territory: Your opponent's Active Pokémon's Retreat Cost is 1 more.
        // This check needs to look at if the OPPONENT has Ariados in play
        let opponent = (state.current_player + 1) % 2;
        for (_idx, pokemon) in state.enumerate_in_play_pokemon(opponent) {
            if matches!(
                get_in_play_ability_mechanic(state, pokemon),
                Some(AbilityMechanic::IncreaseRetreatCostForOpponentActive { amount: 1 })
            ) {
                normal_cost.push(EnergyType::Colorless);
                break;
            }
        }

        normal_cost
    } else {
        vec![]
    }
}

// Test Colorless is wildcard when counting energy
#[cfg(test)]
mod tests {
    use crate::{
        card_ids::CardId, database::get_card_by_enum, effects::TurnEffect,
        hooks::core::to_playable_card,
    };

    use super::*;

    #[test]
    fn test_retreat_costs() {
        let state = State::default();
        let card = get_card_by_enum(CardId::A1055Blastoise);
        let playable_card = to_playable_card(&card, false);
        let retreat_cost = get_retreat_cost(&state, &playable_card);
        assert_eq!(
            retreat_cost,
            vec![
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless
            ]
        );
    }

    #[test]
    fn test_retreat_costs_with_xspeed() {
        let mut state = State::default();
        state.add_turn_effect(TurnEffect::ReducedRetreatCost { amount: 1 }, 0);
        let card = get_card_by_enum(CardId::A1055Blastoise);
        let playable_card = to_playable_card(&card, false);
        let retreat_cost = get_retreat_cost(&state, &playable_card);
        assert_eq!(
            retreat_cost,
            vec![EnergyType::Colorless, EnergyType::Colorless]
        );
    }

    #[test]
    fn test_retreat_costs_with_two_xspeed_and_two_leafs() {
        let mut state = State::default();
        state.add_turn_effect(TurnEffect::ReducedRetreatCost { amount: 1 }, 0);
        state.add_turn_effect(TurnEffect::ReducedRetreatCost { amount: 1 }, 0);
        state.add_turn_effect(TurnEffect::ReducedRetreatCost { amount: 2 }, 0);
        let card = get_card_by_enum(CardId::A1211Snorlax);
        let playable_card = to_playable_card(&card, false);
        let retreat_cost = get_retreat_cost(&state, &playable_card);
        assert_eq!(retreat_cost, vec![]);
    }

    #[test]
    fn test_retreat_costs_with_inflatable_boat() {
        let state = State::default();
        let card = get_card_by_enum(CardId::A1055Blastoise);
        let mut playable_card = to_playable_card(&card, false);
        playable_card.attached_tool = Some(crate::database::get_card_by_enum(
            CardId::A4a067InflatableBoat,
        ));
        let retreat_cost = get_retreat_cost(&state, &playable_card);
        assert_eq!(
            retreat_cost,
            vec![EnergyType::Colorless, EnergyType::Colorless]
        );
    }
}
