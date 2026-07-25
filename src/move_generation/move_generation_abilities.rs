use crate::{
    actions::abilities::{AbilityMechanic, DeckSearchKind},
    actions::{ability_mechanic_from_effect, basic_abilities_suppressed, SimpleAction},
    hooks::is_ultra_beast,
    models::{EnergyType, PlayedCard},
    tools::is_tool_card,
    State,
};

// Use the new function in the filter method
pub(crate) fn generate_ability_actions(state: &State) -> Vec<SimpleAction> {
    let current_player = state.current_player;
    let mut actions = vec![];

    for (in_play_idx, card) in state.enumerate_in_play_pokemon(current_player) {
        if card.card.is_fossil() {
            actions.push(SimpleAction::DiscardFossil { in_play_idx });
        } else if can_use_ability(state, (in_play_idx, card)) {
            actions.push(SimpleAction::UseAbility { in_play_idx });
        }
    }

    actions
}

fn can_use_ability(state: &State, (in_play_index, card): (usize, &PlayedCard)) -> bool {
    if card.card.get_ability().is_none() {
        return false;
    }

    // Power of Alchemy (Alolan Muk): a Basic Pokémon in play "has no Abilities", so its activated
    // Ability disappears from move generation entirely. Checked against the shared suppression
    // predicate rather than `get_in_play_ability_mechanic`, so that a suppressed Ability is still
    // distinguishable from an *unimplemented* one — which must keep panicking below.
    if basic_abilities_suppressed(state) && card.card.is_basic() {
        return false;
    }

    let mechanic = card
        .card
        .get_ability()
        .and_then(|a| ability_mechanic_from_effect(&a.effect))
        .unwrap_or_else(|| {
            panic!(
                "Ability seems not implemented for card ID: {}",
                card.card.get_id()
            )
        });

    can_use_ability_by_mechanic(state, mechanic, in_play_index, card)
}

fn can_use_ability_by_mechanic(
    state: &State,
    mechanic: &AbilityMechanic,
    _in_play_index: usize,
    card: &PlayedCard,
) -> bool {
    let is_active = _in_play_index == 0;
    match mechanic {
        AbilityMechanic::VictreebelFragranceTrap => {
            is_active && can_use_victreebel_fragrance_trap(state, card)
        }
        AbilityMechanic::HealAllYourPokemon { .. } => !card.ability_used,
        AbilityMechanic::HealOneYourPokemon {
            require_active,
            require_tool_attached,
            ..
        } => can_use_heal_one_your_pokemon(
            state,
            card,
            is_active,
            *require_active,
            *require_tool_attached,
        ),
        AbilityMechanic::SuppressBasicAbilities => false, // Passive ability
        AbilityMechanic::PreventAllHealing => false,      // Passive ability
        AbilityMechanic::HealOneYourPokemonExAndDiscardRandomEnergy { .. } => {
            can_use_heal_one_your_pokemon_ex_and_discard_random_energy(state, card)
        }
        AbilityMechanic::DamageOneOpponentPokemon { .. } => !card.ability_used,
        AbilityMechanic::IncreaseDamageIfArceusInPlay { .. } => false,
        AbilityMechanic::DamageOpponentActiveIfArceusInPlay { .. } => {
            can_use_crobat_cunning_link(state, card)
        }
        AbilityMechanic::SwitchDamagedOpponentBenchToActive => {
            is_active && can_use_umbreon_dark_chase(state, card)
        }
        AbilityMechanic::CoinFlipSwitchInOpponentBenchToActive => {
            !card.ability_used && opponent_has_benched_pokemon(state)
        }
        AbilityMechanic::SwitchThisBenchWithActive => !is_active && !card.ability_used,
        AbilityMechanic::SwitchActiveTypedWithBench { energy_type } => {
            can_use_switch_active_typed_with_bench(state, card, *energy_type)
        }
        AbilityMechanic::SwitchActiveUltraBeastWithBench => {
            can_use_celesteela_ultra_thrusters(state, card)
        }
        AbilityMechanic::MoveTypedEnergyFromBenchToActive { .. } => {
            can_use_vaporeon_wash_out(state)
        }
        AbilityMechanic::MoveAllTypedEnergyFromBenchToActive { energy_type } => {
            !card.ability_used && has_benched_typed_pokemon_with_typed_energy(state, *energy_type)
        }
        AbilityMechanic::MoveAllTypedEnergyFromYourPokemonToSelf { energy_type } => {
            can_use_move_all_typed_energy_to_self(state, _in_play_index, card, *energy_type)
        }
        AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { energy_type } => {
            can_use_attach_energy_from_zone_to_active_typed(state, card, *energy_type)
        }
        AbilityMechanic::AttachEnergyFromZoneToYourTypedPokemon { .. } => {
            is_active && !card.ability_used
        }
        AbilityMechanic::AttachEnergyFromZoneToSelf { .. } => !card.ability_used,
        AbilityMechanic::AttachEnergyFromZoneToSelfAndEndTurn { .. } => !card.ability_used,
        AbilityMechanic::AttachEnergyFromZoneToSelfAndDamage { .. } => !card.ability_used,
        AbilityMechanic::DamageOpponentActiveOnZoneAttachToSelf { .. } => false,
        AbilityMechanic::AttachEnergyFromDiscardToSelfAndDamage { energy_type, .. } => {
            !card.ability_used && state.discard_energies[state.current_player].contains(energy_type)
        }
        AbilityMechanic::ReduceDamageFromAttacks { .. } => false,
        AbilityMechanic::ReduceOpponentActiveDamage { .. } => false,
        AbilityMechanic::ReduceDamageFromTypedAttackers { .. } => false, // Passive ability
        AbilityMechanic::ReduceDamageIfArceusInPlay { .. } => false,     // Passive ability
        AbilityMechanic::ReduceDamageAtFullHp { .. } => false,           // Passive ability
        AbilityMechanic::UnownGuard { .. } => false,                     // Passive ability
        AbilityMechanic::IncreaseDamageWhenRemainingHpAtMost { .. } => false,
        AbilityMechanic::IncreaseDamageForTypeInPlay { .. } => false,
        AbilityMechanic::IncreaseDamageForTwoTypesInPlay { .. } => false,
        AbilityMechanic::UnownPower { .. } => false, // Passive ability
        AbilityMechanic::IncreaseDamageForEvolutionsFromBench { .. } => false, // Passive ability
        AbilityMechanic::CoordinatedUnit { .. } => false, // Passive ability
        AbilityMechanic::StartTurnRandomPokemonToHand { .. } => false,
        AbilityMechanic::SearchRandomCardFromDeck { card_kind } => {
            !card.ability_used && deck_has_searchable_card(state, *card_kind)
        }
        AbilityMechanic::LookAtTopCardOfDeck { either_player } => {
            can_look_at_top_card(state, card, *either_player)
        }
        AbilityMechanic::MoveDamageFromOneYourPokemonToThisPokemon => {
            can_use_dusknoir_shadow_void(state, _in_play_index)
        }
        AbilityMechanic::DiscardOpponentActiveToolsAndDiscardSelf => {
            can_use_dismantling_keys(state, _in_play_index, card)
        }
        AbilityMechanic::PreventFirstAttack => false,
        AbilityMechanic::ElectromagneticWall => false,
        AbilityMechanic::InfiltratingInspection => false,
        AbilityMechanic::DiscardTopCardOpponentDeck => {
            !card.ability_used && !state.decks[(state.current_player + 1) % 2].cards.is_empty()
        }
        AbilityMechanic::CoinFlipToPreventDamage => false, // Passive ability
        AbilityMechanic::CoinFlipToReduceDamage { .. } => false, // Passive ability
        AbilityMechanic::CoinFlipToSurviveKnockOut => false, // Passive ability
        AbilityMechanic::CoinFlipToDenyKnockoutPoints => false, // Passive (handle_knockouts)
        AbilityMechanic::MoveAllTypedEnergyToBenchOnKnockout { .. } => false, // Passive (on_knockout)
        AbilityMechanic::DamageOnKnockoutInActive { .. } => false, // Passive (on_knockout)
        AbilityMechanic::CheckupDamageToOpponentActive { .. } => false, // Passive ability
        AbilityMechanic::CheckupDamageToAllOpponentPokemon { .. } => false, // Passive ability
        AbilityMechanic::BadDreamsEndOfTurn { .. } => false,       // Passive ability
        AbilityMechanic::CoinFlipStatusOpponentActive { .. } => !card.ability_used,
        AbilityMechanic::DiscardEnergyToIncreaseTypeDamage { discard_energy, .. } => {
            !card.ability_used && card.attached_energy.contains(discard_energy)
        }
        AbilityMechanic::PoisonOpponentActive => _in_play_index == 0 && !card.ability_used,
        AbilityMechanic::ConfuseOpponentActive => _in_play_index == 0 && !card.ability_used,
        AbilityMechanic::BurnOpponentActive => !card.ability_used,
        AbilityMechanic::RemoveRandomSpecialConditionFromActive => {
            can_use_remove_random_special_condition_from_active(state, card)
        }
        AbilityMechanic::HealActiveYourPokemon { .. } => !card.ability_used,
        AbilityMechanic::SwitchOutOpponentActiveToBench {
            require_active,
            require_opponent_active_basic,
        } => {
            !card.ability_used
                && (!require_active || is_active)
                && opponent_has_benched_pokemon(state)
                && (!require_opponent_active_basic || opponent_active_is_basic(state))
        }
        AbilityMechanic::DiscardFromHandToDrawCard => {
            !card.ability_used && !state.hands[state.current_player].is_empty()
        }
        AbilityMechanic::ImmuneToStatusConditions => false, // Passive ability
        AbilityMechanic::SoothingWind { .. } => false,      // Passive ability
        AbilityMechanic::NoOpponentSupportInActive => false,
        AbilityMechanic::NoOpponentStadiumInActive => false, // Passive ability
        AbilityMechanic::DoubleGrassEnergy => false,
        AbilityMechanic::PreventOpponentActiveEvolution => false,
        AbilityMechanic::ReduceRetreatCostOfYourActiveBasicFromBench { .. } => false,
        AbilityMechanic::ReduceRetreatCostOfYourActiveTypedFromBench { .. } => false,
        AbilityMechanic::NoRetreatIfHasEnergy => false,
        AbilityMechanic::NoRetreatCost { .. } => false, // Passive ability
        AbilityMechanic::PreventAllDamageFromEx => false,
        AbilityMechanic::SleepOnZoneAttachToSelfWhileActive => false,
        AbilityMechanic::IncreasePoisonDamage { .. } => false,
        AbilityMechanic::DrawCardsOnEvolve { .. } => false,
        AbilityMechanic::HealTypedPokemonOnEvolve { .. } => false,
        AbilityMechanic::AttachEnergyFromZoneToActiveTypedOnEvolve { .. } => false,
        AbilityMechanic::DamageOpponentActiveOnEvolve { .. } => false,
        AbilityMechanic::DiscardRandomEnergyFromOpponentActiveOnEvolve => false,
        AbilityMechanic::PutCardsFromDiscardToHandOnEvolve { .. } => false,
        AbilityMechanic::CanEvolveIntoEeveeEvolution => false,
        AbilityMechanic::CanEvolveOnFirstTurnIfActive => false,
        AbilityMechanic::CounterattackDamage { .. } => false,
        AbilityMechanic::PoisonAttackerOnDamaged => false,
        AbilityMechanic::IncreaseAttackCostForOpponentActive { .. } => false,
        AbilityMechanic::IncreaseRetreatCostForOpponentActive { .. } => false,
        AbilityMechanic::PreventDamageWhileBenched => false,
        AbilityMechanic::IncreaseHpPerAttachedEnergy { .. } => false,
        AbilityMechanic::IncreaseHpForTypeInPlay { .. } => false, // Passive ability
        AbilityMechanic::HealSelfOnZoneAttach { .. } => false,
        AbilityMechanic::EndFirstTurnAttachEnergyToSelf { .. } => false,
        AbilityMechanic::EndTurnDrawCardIfActive { .. } => false,
        AbilityMechanic::EndTurnHealSelfIfActive { .. } => false,
        AbilityMechanic::ProtectSelfNextTurnAfterAttackKnockout => false,
        AbilityMechanic::MoveFixedDamageFromActiveToThisBenched { amount } => {
            can_use_accept_pain(state, _in_play_index, card, *amount)
        }
        AbilityMechanic::LegendaryDrive => false, // triggered on bench placement, not via UseAbility
        AbilityMechanic::AncientRoar => false, // triggered on bench placement, not via UseAbility
        AbilityMechanic::ReduceAttackCost { .. } => false, // passive ability
        AbilityMechanic::TimeRecall => false,  // passive ability (consumed in attack generation)
        AbilityMechanic::QuickGrowth => false, // triggered at end of opponent's turn
    }
}

fn can_use_accept_pain(
    state: &State,
    in_play_index: usize,
    card: &PlayedCard,
    amount: u32,
) -> bool {
    in_play_index != 0
        && !card.ability_used
        && state
            .maybe_get_active(state.current_player)
            .is_some_and(|active| active.get_damage_counters() >= amount)
}

fn can_use_celesteela_ultra_thrusters(state: &State, card: &PlayedCard) -> bool {
    if card.ability_used {
        return false;
    }
    let active = state.get_active(state.current_player);
    if !is_ultra_beast(&active.get_name()) {
        return false;
    }
    state
        .enumerate_bench_pokemon(state.current_player)
        .any(|(_, pokemon)| is_ultra_beast(&pokemon.get_name()))
}

fn can_use_switch_active_typed_with_bench(
    state: &State,
    card: &PlayedCard,
    energy_type: EnergyType,
) -> bool {
    if card.ability_used {
        return false;
    }
    let active = state.get_active(state.current_player);
    if active.get_energy_type() != Some(energy_type) {
        return false;
    }
    state
        .enumerate_bench_pokemon(state.current_player)
        .next()
        .is_some()
}

fn can_use_remove_random_special_condition_from_active(state: &State, card: &PlayedCard) -> bool {
    !card.ability_used
        && state
            .maybe_get_active(state.current_player)
            .is_some_and(|active| {
                active.is_poisoned()
                    || active.is_paralyzed()
                    || active.is_asleep()
                    || active.is_burned()
                    || active.is_confused()
            })
}

fn can_use_heal_one_your_pokemon_ex_and_discard_random_energy(
    state: &State,
    card: &PlayedCard,
) -> bool {
    if card.ability_used {
        return false;
    }
    state
        .enumerate_in_play_pokemon(state.current_player)
        .any(|(_, pokemon)| {
            pokemon.card.is_ex() && pokemon.is_damaged() && !pokemon.attached_energy.is_empty()
        })
}

fn can_use_attach_energy_from_zone_to_active_typed(
    state: &State,
    card: &PlayedCard,
    energy_type: EnergyType,
) -> bool {
    if card.ability_used || !state.can_attach_energy_from_zone(0) {
        return false;
    }
    let active = state.get_active(state.current_player);
    active.get_energy_type() == Some(energy_type)
}

fn can_use_dusknoir_shadow_void(state: &State, dusknoir_idx: usize) -> bool {
    state
        .enumerate_in_play_pokemon(state.current_player)
        .any(|(i, p)| p.is_damaged() && i != dusknoir_idx)
}

fn can_use_dismantling_keys(state: &State, in_play_idx: usize, card: &PlayedCard) -> bool {
    if in_play_idx == 0 || card.ability_used {
        return false;
    }
    let opponent = (state.current_player + 1) % 2;
    state
        .maybe_get_active(opponent)
        .is_some_and(|active| active.has_tool_attached())
}

fn can_use_crobat_cunning_link(state: &State, card: &PlayedCard) -> bool {
    if card.ability_used {
        return false;
    }
    // Check if player has Arceus or Arceus ex in play
    state
        .enumerate_in_play_pokemon(state.current_player)
        .any(|(_, pokemon)| {
            let name = pokemon.get_name();
            name == "Arceus" || name == "Arceus ex"
        })
}

/// True when the current player's deck still holds a card the search could actually find. Without
/// this, "put a random <kind> card from your deck into your hand" would be offered against a deck
/// with no eligible card and resolve into a bare shuffle, wasting its once-per-turn use.
fn deck_has_searchable_card(state: &State, card_kind: DeckSearchKind) -> bool {
    let player = state.current_player;
    match card_kind {
        DeckSearchKind::Pokemon => state.iter_deck_pokemon(player).next().is_some(),
        DeckSearchKind::Tool => state.decks[player].cards.iter().any(is_tool_card),
    }
}

/// "Look at the top card of <someone's> deck" needs a top card to exist. Data Scan can only look
/// at its controller's deck; CHECK ("choose either player") is satisfied by either deck, so it
/// stays usable when only the opponent has cards left. Beyond that the ability changes nothing, so
/// the only other gate is the printed "Once during your turn".
fn can_look_at_top_card(state: &State, card: &PlayedCard, either_player: bool) -> bool {
    if card.ability_used {
        return false;
    }
    let opponent = (state.current_player + 1) % 2;
    !state.decks[state.current_player].cards.is_empty()
        || (either_player && !state.decks[opponent].cards.is_empty())
}

/// Energy Plunder is only worth its once-per-turn use if some *other* Pokémon of yours is holding
/// the Energy — pulling Energy from the holder to itself does nothing.
fn can_use_move_all_typed_energy_to_self(
    state: &State,
    self_idx: usize,
    card: &PlayedCard,
    energy_type: EnergyType,
) -> bool {
    !card.ability_used
        && state
            .enumerate_in_play_pokemon(state.current_player)
            .any(|(idx, pokemon)| idx != self_idx && pokemon.attached_energy.contains(&energy_type))
}

/// True when the opponent has at least one Benched Pokémon to switch in. Without one, an ability
/// that promotes from the opponent's Bench can only waste its once-per-turn use, so it is not
/// offered at all.
fn opponent_has_benched_pokemon(state: &State) -> bool {
    let opponent = (state.current_player + 1) % 2;
    state.enumerate_bench_pokemon(opponent).next().is_some()
}

/// True when the opponent's Active Pokémon is a Basic — the restriction Swellow's Repelling Wind
/// adds on top of the shared "switch out your opponent's Active Pokémon" template.
fn opponent_active_is_basic(state: &State) -> bool {
    let opponent = (state.current_player + 1) % 2;
    state
        .maybe_get_active(opponent)
        .is_some_and(|active| active.card.is_basic())
}

fn can_use_umbreon_dark_chase(state: &State, card: &PlayedCard) -> bool {
    if card.ability_used {
        return false;
    }
    // Must be in the Active Spot (index 0)
    // Opponent must have a benched Pokémon with damage
    let opponent = (state.current_player + 1) % 2;
    state
        .enumerate_bench_pokemon(opponent)
        .any(|(_, pokemon)| pokemon.is_damaged())
}

fn can_use_vaporeon_wash_out(state: &State) -> bool {
    // Check if active Pokémon is Water type
    let active = state.get_active(state.current_player);
    if active.get_energy_type() != Some(EnergyType::Water) {
        return false;
    }
    // Check if there's a benched Water Pokémon with Water energy
    state
        .enumerate_bench_pokemon(state.current_player)
        .any(|(_, pokemon)| {
            pokemon.card.get_type() == Some(EnergyType::Water)
                && pokemon.attached_energy.contains(&EnergyType::Water)
        })
}

/// True if the current player has a benched Pokémon of `energy_type` that has at least one
/// `energy_type` Energy attached (a valid source for Lunala ex's Psychic Connect).
fn has_benched_typed_pokemon_with_typed_energy(state: &State, energy_type: EnergyType) -> bool {
    state
        .enumerate_bench_pokemon(state.current_player)
        .any(|(_, pokemon)| {
            pokemon.card.get_type() == Some(energy_type)
                && pokemon.attached_energy.contains(&energy_type)
        })
}

fn can_use_victreebel_fragrance_trap(state: &State, card: &PlayedCard) -> bool {
    if card.ability_used {
        return false;
    }
    let opponent = (state.current_player + 1) % 2;
    state
        .enumerate_bench_pokemon(opponent)
        .any(|(_, pokemon)| pokemon.card.is_basic())
}

/// Gating for the "heal 30 damage from 1 of your Pokémon" family. Beyond the once-per-turn flag
/// and the per-printing conditions, there has to be something damaged to heal — otherwise the
/// ability resolves into an empty choice list.
fn can_use_heal_one_your_pokemon(
    state: &State,
    card: &PlayedCard,
    is_active: bool,
    require_active: bool,
    require_tool_attached: bool,
) -> bool {
    !card.ability_used
        && (!require_active || is_active)
        && (!require_tool_attached || card.has_tool_attached())
        && state
            .enumerate_in_play_pokemon(state.current_player)
            .any(|(_, pokemon)| pokemon.is_damaged())
}
