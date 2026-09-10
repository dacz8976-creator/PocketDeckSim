use std::{collections::HashMap, panic};

use log::debug;
use rand::{distributions::WeightedIndex, prelude::Distribution, rngs::StdRng};

use crate::{
    actions::effect_ability_mechanic_map::get_entering_play_ability_mechanic,
    actions::{
        abilities::{AbilityMechanic, RandomEvolutionTrigger},
        apply_abilities_action::{forecast_ability, try_copy_random_opponent_hand_supporter},
        apply_action_helpers::{apply_activate, wrap_with_common_logic, Mutation},
        get_ability_mechanic, get_in_play_ability_mechanic,
    },
    effects::{CardEffect, TurnEffect},
    hooks::{
        get_retreat_cost, on_bench_from_hand, on_evolve, to_playable_card, DamageModifierContext,
    },
    models::{Card, EnergyType, StatusCondition},
    state::{PendingAttackCoinChoice, State},
    tools,
};

use super::{
    apply_action_helpers::{
        forecast_end_turn, guts_would_flip, handle_damage, handle_damage_only, handle_knockouts,
        Mutations,
    },
    apply_attack_action::{self, forecast_attack},
    apply_stadium_action::{self, forecast_use_stadium},
    apply_trainer_action::{
        self, ensure_copied_researcher_budget, forecast_trainer_action, is_misty_card,
        penny_candidates, sample_copied_supporter_effect, sample_misty_effect,
        supporter_candidates_in_hand, try_forecast_trainer_action,
    },
    outcomes::{CoinPaths, Outcomes},
    shared_mutations,
    team_rockets_researcher::{is_researcher_card, ResearcherPlan, UnpricedForecast},
    trainer_coin_plan, Action, SimpleAction,
};

/// Main function to mutate the state based on the action. It forecasts the possible outcomes
/// and then chooses one of them to apply. This is so that bot implementations can re-use the
/// `forecast_action` function.
pub fn apply_action(rng: &mut StdRng, state: &mut State, action: &Action) {
    if matches!(action.action, SimpleAction::ChooseMistyTarget { .. }) {
        let mutation = trainer_coin_plan::sample_misty_target_actual(rng, state, action);
        mutation(rng, state, action);
        return;
    }
    if matches!(
        action.action,
        SimpleAction::KeepTrainerCoinResults | SimpleAction::RerollTrainerCoins { .. }
    ) {
        let mutation = trainer_coin_plan::sample_choice_actual(rng, state, action);
        mutation(rng, state, action);
        return;
    }
    if let Some(mutation) = trainer_coin_plan::try_sample_entry_actual(rng, state, action) {
        mutation(rng, state, action);
        return;
    }
    if let Some(mutation) = sample_researcher_capable_actual(rng, state, action) {
        let wrapped = wrap_with_common_logic(mutation);
        wrapped(rng, state, action);
        return;
    }
    let (probabilities, mut lazy_mutations) = forecast_action(state, action).into_branches();
    if probabilities.len() == 1 {
        lazy_mutations.remove(0)(rng, state, action);
    } else {
        let dist = WeightedIndex::new(&probabilities).unwrap();
        let chosen_index = dist.sample(rng);
        lazy_mutations.remove(chosen_index)(rng, state, action);
    }
}

fn sample_researcher_capable_actual(
    rng: &mut StdRng,
    state: &State,
    action: &Action,
) -> Option<Mutation> {
    match &action.action {
        SimpleAction::Play { trainer_card } if is_misty_card(trainer_card) => {
            Some(sample_misty_effect(rng, state, trainer_card))
        }
        SimpleAction::Play { trainer_card } if is_researcher_card(trainer_card) => {
            let actor = action.actor;
            let plan = ResearcherPlan::from_state(state, actor);
            if let Err(error) = plan.ensure_priced() {
                crate::observation::record_unpriced(action, &error.reason);
            }
            let force_first = state.has_pending_will_first_heads();
            let batch = plan.sample_batch(rng, force_first);
            Some(Box::new(move |rng, state, _action| {
                if force_first {
                    assert!(state.consume_pending_will_first_heads());
                }
                plan.apply_sampled(&batch, rng, state, actor);
            }))
        }
        SimpleAction::Play { trainer_card } if trainer_card.name == "Penny" => {
            let opponent = 1 - action.actor;
            let penny = trainer_card.clone();
            let candidates = penny_candidates(state, opponent);
            if candidates.is_empty() {
                return Some(Box::new(|_, _, _| {}));
            }
            if let Err(error) = ensure_copied_researcher_budget(action.actor, state, &candidates) {
                crate::observation::record_unpriced(action, &error.reason);
            }
            let copied = sample_copied_supporter_effect(rng, action.actor, state, &candidates);
            Some(Box::new(move |rng, state, action| {
                copied(rng, state, action);
                if trainer_coin_plan::defer_penny_shuffle_for_misty(state, &penny, opponent) {
                    return;
                }
                state.decks[opponent].shuffle(false, rng);
            }))
        }
        SimpleAction::UseAbility { .. } if action_uses_portrait(state, action) => {
            let opponent = 1 - action.actor;
            let candidates = supporter_candidates_in_hand(state, opponent);
            if let Err(error) = ensure_copied_researcher_budget(action.actor, state, &candidates) {
                crate::observation::record_unpriced(action, &error.reason);
            }
            Some(sample_copied_supporter_effect(
                rng,
                action.actor,
                state,
                &candidates,
            ))
        }
        _ => None,
    }
}

fn action_uses_portrait(state: &State, action: &Action) -> bool {
    let SimpleAction::UseAbility { in_play_idx } = action.action else {
        return false;
    };
    state.in_play_pokemon[action.actor][in_play_idx]
        .as_ref()
        .is_some_and(|pokemon| {
            get_ability_mechanic(&pokemon.card)
                == Some(&AbilityMechanic::CopyRandomOpponentHandSupporter)
        })
}

fn victory_star_source(state: &State, actor: usize) -> Option<usize> {
    if state.victory_star_used_this_turn[actor] {
        return None;
    }
    let active = state.in_play_pokemon[actor][0].as_ref()?;
    if !state.pokemon_is_type(active, EnergyType::Fire) {
        return None;
    }
    state
        .enumerate_in_play_pokemon(actor)
        .find_map(|(idx, pokemon)| {
            (get_in_play_ability_mechanic(state, pokemon) == Some(&AbilityMechanic::VictoryStar))
                .then_some(idx)
        })
}

/// Build the sample-only half of Victory Star. `None` means the ordinary attack path remains in
/// charge (no eligible Victini, no attack-effect coin batch, or an explicitly unsupported gate).
fn try_forecast_victory_star_attack(state: &State, action: &Action) -> Option<Outcomes> {
    let SimpleAction::Attack(attack) = &action.action else {
        return None;
    };
    assert!(
        state.pending_attack_coin_choice.is_none(),
        "cannot start an attack while a Victory Star coin choice is pending"
    );
    let source_idx = victory_star_source(state, action.actor)?;

    // Pocket evidence is still needed for whether Victory Star can replace confusion and
    // CoinFlipToBlockAttack checks. Resolving the printed attack-effect coin first would reverse
    // their order, so this bounded implementation deliberately keeps legacy resolution there.
    if apply_attack_action::has_unverified_attacker_coin_gate(action.actor, state, action.is_stack)
    {
        debug!("Victory Star attack-effect pause skipped for unverified attacker coin gate");
        return None;
    }

    let base = apply_attack_action::forecast_attack_effect(action.actor, state, attack);
    if !base.all_branches_have_coin_paths() {
        return None;
    }

    let mut sampled = base.into_outcomes();
    let mut will_consumed_on_sample = false;
    if state.has_pending_will_first_heads() {
        sampled = match sampled.force_first_heads() {
            Ok(forced) => {
                will_consumed_on_sample = true;
                forced
            }
            Err(original) => original,
        };
    }

    // Secondary random successors can refine one public coin class into several exact state
    // branches. Stage only the marginal coin class: choosing and discarding one refined branch
    // here would consume hidden RNG before the player decides Keep/Reroll and then choose the
    // secondary result again at commit.
    let mut coin_classes: Vec<(f64, CoinPaths)> = Vec::new();
    for (probability, _uncommitted_attack, coin_paths) in sampled.into_branches_with_coin_paths() {
        if let Some((total, _)) = coin_classes
            .iter_mut()
            .find(|(_, existing)| *existing == coin_paths)
        {
            *total += probability;
        } else {
            coin_classes.push((probability, coin_paths));
        }
    }

    let attack = attack.clone();
    let actor = action.actor;
    let original_is_stack = action.is_stack;
    let branches: Vec<(f64, Mutation, CoinPaths)> = coin_classes
        .into_iter()
        .map(|(probability, coin_paths)| {
            let sampled_class = coin_paths.clone();
            let attack = attack.clone();
            let mutation: Mutation =
                Box::new(move |rng: &mut StdRng, state: &mut State, _: &Action| {
                    let flips = sampled_class
                        .sample(rng)
                        .expect("Victory Star staging requires a nonempty attack coin-path class");
                    if will_consumed_on_sample {
                        assert!(
                            state.consume_pending_will_first_heads(),
                            "Will must still be pending when its first coin batch is sampled"
                        );
                    }
                    state.pending_attack_coin_choice = Some(PendingAttackCoinChoice {
                        actor,
                        attack: attack.clone(),
                        original_is_stack,
                        flips: flips.0,
                        victory_star_in_play_idx: source_idx,
                    });
                    state.move_generation_stack.push((
                        actor,
                        vec![
                            SimpleAction::KeepAttackCoinResults,
                            SimpleAction::RerollAttackCoins {
                                victory_star_in_play_idx: source_idx,
                            },
                        ],
                    ));
                });
            (probability, mutation, coin_paths)
        })
        .collect();

    Some(
        Outcomes::from_branches_with_coin_paths(branches)
            .expect("Victory Star sample branches must remain a valid distribution"),
    )
}

fn forecast_victory_star_choice(state: &State, action: &Action) -> Outcomes {
    let pending = state
        .pending_attack_coin_choice
        .clone()
        .expect("Victory Star choice requires pending attack coin data");
    assert!(
        action.is_stack,
        "Victory Star choice must be a stack action"
    );
    assert_eq!(
        action.actor, pending.actor,
        "Victory Star choice actor mismatch"
    );

    let (base, use_victory_star) = match &action.action {
        SimpleAction::KeepAttackCoinResults => (
            apply_attack_action::forecast_attack_effect(pending.actor, state, &pending.attack)
                .select_coin_path(&pending.flips)
                .unwrap_or_else(|reason| panic!("{reason}")),
            false,
        ),
        SimpleAction::RerollAttackCoins {
            victory_star_in_play_idx,
        } => {
            assert_eq!(
                *victory_star_in_play_idx, pending.victory_star_in_play_idx,
                "Victory Star source mismatch"
            );
            assert!(
                !state.victory_star_used_this_turn[pending.actor],
                "Victory Star was already used this turn"
            );
            let fresh =
                apply_attack_action::forecast_attack_effect(pending.actor, state, &pending.attack);
            assert!(
                fresh.all_branches_have_coin_paths(),
                "replacement must regenerate an attack-effect coin batch"
            );
            (fresh, true)
        }
        _ => panic!("pending Victory Star state accepts only Keep or Reroll"),
    };

    let outcomes = apply_attack_action::finish_attack_from_effect_outcomes(
        pending.actor,
        state,
        &pending.attack,
        pending.original_is_stack,
        base,
    );

    outcomes.map_mutations(move |mutation| {
        let pending = pending.clone();
        let original_action = Action {
            actor: pending.actor,
            action: SimpleAction::Attack(pending.attack.clone()),
            is_stack: pending.original_is_stack,
        };
        let committed_attack = wrap_with_common_logic(mutation);
        Box::new(move |rng, state, _choice_action| {
            assert_eq!(
                state.pending_attack_coin_choice.as_ref(),
                Some(&pending),
                "Victory Star pending state changed before commit"
            );
            let (_, choices) = state
                .move_generation_stack
                .last()
                .expect("Victory Star choice stack frame missing");
            assert_eq!(
                choices.len(),
                2,
                "Victory Star choice stack must have two actions"
            );
            state.move_generation_stack.pop();
            state.pending_attack_coin_choice = None;
            if use_victory_star {
                state.victory_star_used_this_turn[pending.actor] = true;
            }
            // The pause frame is gone before the original wrapper runs. A copied attack can now
            // pop its older selection frame, and any new effect choice pushed during commit stays.
            committed_attack(rng, state, &original_action);
        })
    })
}

/// Exact-only forecast boundary. Researcher expansions that exceed the declared budget are
/// returned as structured unpriced errors before any sampled substitute can enter `Outcomes`.
pub fn try_forecast_action(state: &State, action: &Action) -> Result<Outcomes, UnpricedForecast> {
    if matches!(action.action, SimpleAction::ChooseMistyTarget { .. }) {
        return trainer_coin_plan::forecast_misty_target(state, action);
    }
    if matches!(
        action.action,
        SimpleAction::KeepTrainerCoinResults | SimpleAction::RerollTrainerCoins { .. }
    ) {
        return trainer_coin_plan::try_forecast_choice(state, action);
    }
    if let Some(staged) = trainer_coin_plan::try_forecast_entry(state, action)? {
        return Ok(staged);
    }
    match &action.action {
        SimpleAction::Play { trainer_card } => {
            let outcomes = try_forecast_trainer_action(action.actor, state, trainer_card)?;
            Ok(finish_forecast(state, action, outcomes))
        }
        SimpleAction::UseAbility { .. } if action_uses_portrait(state, action) => {
            let outcomes = try_copy_random_opponent_hand_supporter(state, action.actor)?;
            Ok(finish_forecast(state, action, outcomes))
        }
        _ => Ok(forecast_action_unchecked(state, action)),
    }
}

/// Compatibility exact forecast. Callers that need to handle an unpriced Researcher tree should
/// use `try_forecast_action`; real play should use `apply_action`.
pub fn forecast_action(state: &State, action: &Action) -> Outcomes {
    try_forecast_action(state, action)
        .unwrap_or_else(|error| panic!("exact action forecast refused: {}", error.reason))
}

/// This should be mostly a "router" function that calls the appropriate forecast function
/// based on the action type.
fn forecast_action_unchecked(state: &State, action: &Action) -> Outcomes {
    if matches!(action.action, SimpleAction::Attack(_)) {
        if let Some(staged) = try_forecast_victory_star_attack(state, action) {
            return staged;
        }
    }
    if matches!(
        action.action,
        SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. }
    ) {
        return forecast_victory_star_choice(state, action);
    }

    let outcomes = match &action.action {
        // Deterministic Actions
        SimpleAction::DrawCard { .. } // TODO: DrawCard should return actual deck probabilities.
        | SimpleAction::Place(_, _)
        | SimpleAction::MoveEnergy { .. }
        | SimpleAction::MoveEnergies { .. }
        | SimpleAction::AttachTool { .. }
        | SimpleAction::Evolve { .. }
        | SimpleAction::Activate { .. }
        | SimpleAction::Promote { .. }
        | SimpleAction::Retreat(_)
        | SimpleAction::ScheduleDelayedSpotDamage { .. }
        | SimpleAction::Heal { .. }
        | SimpleAction::HealAndDiscardEnergy { .. }
        | SimpleAction::HealAndCureConditions { .. }
        | SimpleAction::MoveAllDamage { .. }
        | SimpleAction::MoveDamageToOpponentActive { .. }
        | SimpleAction::ApplyEeveeBagDamageBoost
        | SimpleAction::HealAllEeveeEvolutions
        | SimpleAction::DiscardFossil { .. }
        | SimpleAction::ReturnPokemonToHand { .. }
        | SimpleAction::DiscardToolFromPokemon { .. }
        | SimpleAction::DiscardActiveStadium
        | SimpleAction::BenchOpponentFromDiscard { .. }
        | SimpleAction::BenchOpponentHandBasics { .. }
        | SimpleAction::PutCardFromDiscardToHand { .. }
        | SimpleAction::DiscardRandomOpponentActiveEnergy
        | SimpleAction::MoveRandomOpponentEnergyToActive { .. }
        | SimpleAction::ApplyStatusToOpponentActive { .. }
        | SimpleAction::DiscardOwnBenchedThenDamage { .. }
        | SimpleAction::ConsolidateEnergyToPokemon { .. }
        | SimpleAction::Noop => forecast_deterministic_action(),
        SimpleAction::ShuffleInPlayPokemonIntoDeck { in_play_idx } => {
            let in_play_idx = *in_play_idx;
            Outcomes::single_fn(move |rng, state, action| {
                apply_shuffle_in_play_pokemon_into_deck(action.actor, state, in_play_idx);
                state.decks[action.actor].shuffle(false, rng);
            })
        }
        SimpleAction::Attach {
            attachments,
            is_turn_energy,
        } => forecast_attach(state, action.actor, attachments, *is_turn_energy),
        SimpleAction::OpponentShuffleHandAndDrawRemainingPoints => {
            Outcomes::single_fn(apply_trainer_action::mars_effect)
        }
        SimpleAction::ShuffleRandomOpponentHandCard => {
            Outcomes::single_fn(|rng, state, action| {
                let opponent = (action.actor + 1) % 2;
                apply_attack_action::shuffle_random_hand_cards_into_deck(rng, state, opponent, 1);
            })
        }
        SimpleAction::UseAbility { in_play_idx } => forecast_ability(state, action, *in_play_idx),
        SimpleAction::ApplyDamage {
            attacking_ref,
            targets,
            is_from_active_attack,
        } => forecast_apply_damage(state, *attacking_ref, targets, *is_from_active_attack),
        SimpleAction::ApplyQueuedAttackDamage { attack, targets } => {
            apply_attack_action::finish_queued_attack_damage(
                action.actor,
                state,
                attack,
                targets.clone(),
            )
        }
        SimpleAction::Attack(attack) => {
            forecast_attack(action.actor, state, attack, action.is_stack)
        }
        SimpleAction::Play { trainer_card } => {
            forecast_trainer_action(action.actor, state, trainer_card)
        }
        SimpleAction::CommunicatePokemon { hand_pokemon } => {
            forecast_pokemon_communication(action.actor, state, hand_pokemon)
        }
        SimpleAction::ShufflePokemonIntoDeck { hand_pokemon } => {
            forecast_shuffle_pokemon_into_deck(action.actor, hand_pokemon)
        }
        SimpleAction::ShuffleOwnCardsIntoDeck { cards } => {
            forecast_shuffle_own_cards_into_deck(action.actor, cards)
        }
        SimpleAction::SwitchHandCardForRandomTool { hand_card } => {
            apply_stadium_action::forecast_switch_hand_card_for_random_tool(
                state,
                action.actor,
                hand_card,
            )
        }
        SimpleAction::ShuffleOpponentHandCard { card } => {
            forecast_shuffle_opponent_hand_card(action.actor, card)
        }
        SimpleAction::DiscardOpponentSupporter { supporter_card } => {
            forecast_discard_opponent_supporter(action.actor, supporter_card)
        }
        SimpleAction::DiscardOwnCards { cards } => forecast_discard_own_cards(action.actor, cards),
        SimpleAction::DiscardOwnCardsForAttackDamage {
            cards,
            damage_per_card,
        } => forecast_discard_own_cards_for_attack_damage(action.actor, cards, *damage_per_card),
        SimpleAction::AttachFromDiscard {
            in_play_idx,
            num_random_energies,
        } => forecast_attach_from_discard(
            state,
            action.actor,
            *in_play_idx,
            *num_random_energies,
        ),
        SimpleAction::AttachTypedFromDiscard {
            in_play_idx,
            energy_type,
            count,
        } => forecast_attach_typed_from_discard(*in_play_idx, *energy_type, *count),
        SimpleAction::PutRandomCardsFromDiscardToHand { card_kind, amount } => {
            shared_mutations::discard_search_outcomes(action.actor, state, *card_kind, *amount)
        }
        SimpleAction::SadaAttach { assignments } => forecast_sada_attach(assignments),
        SimpleAction::UseStadium => forecast_use_stadium(state, action.actor),
        SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. } => {
            unreachable!("Victory Star choices are routed before the generic action forecast")
        }
        SimpleAction::KeepTrainerCoinResults | SimpleAction::RerollTrainerCoins { .. } => {
            unreachable!("Luxury Coin choices are routed before the generic action forecast")
        }
        SimpleAction::ChooseMistyTarget { .. } => {
            unreachable!("Misty target choices are routed before the generic action forecast")
        }
        // acting_player is not passed here, because there is only 1 turn to end. The current turn.
        SimpleAction::EndTurn => {
            let (probabilities, mutations) = forecast_end_turn(state);
            Outcomes::from_parts(probabilities, mutations)
        }
    };

    finish_forecast(state, action, outcomes)
}

fn finish_forecast(state: &State, action: &Action, mut outcomes: Outcomes) -> Outcomes {
    // Penny and Portrait condition Will inside each selected Supporter source. Applying Will to
    // their flattened outer distribution would reweight which source card was selected and would
    // consume Will on non-coin source branches.
    let copied_supporter_owns_will = matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Penny")
        || action_uses_portrait(state, action);
    if !copied_supporter_owns_will
        && is_will_eligible_action(&action.action)
        && state.has_pending_will_first_heads()
    {
        outcomes = match outcomes.force_first_heads() {
            Ok(forced_outcomes) => forced_outcomes.map_mutations(|mutation| {
                Box::new(move |rng, state, action| {
                    state.consume_pending_will_first_heads();
                    mutation(rng, state, action);
                })
            }),
            Err(original_outcomes) => original_outcomes,
        };
    }

    // Wrap with common logic for mutations
    outcomes.map_mutations(wrap_with_common_logic)
}

fn is_will_eligible_action(action: &SimpleAction) -> bool {
    matches!(
        action,
        SimpleAction::Attack(_)
            | SimpleAction::UseAbility { .. }
            | SimpleAction::Play { .. }
            | SimpleAction::UseStadium
    )
}

fn forecast_deterministic_action() -> Outcomes {
    Outcomes::single_fn(move |_, state, action| {
        apply_deterministic_action(state, action);
    })
}

/// Attaching Energy is deterministic unless the destination is a Pokémon with Porygon2's Buggy
/// Evolution (A4 136): "Whenever you attach an Energy from your Energy Zone to this Pokémon, put a
/// random card from your deck that evolves from this Pokémon onto this Pokémon to evolve it."
///
/// The evolution card is drawn at random, so the attach forecasts one branch per candidate in the
/// deck rather than hiding the draw inside the mutation — the same shape Caterpie's Quick Growth
/// uses at end of turn. The trigger fires at most once per action: after the first Energy the
/// holder is no longer the Pokémon the Ability is printed on.
fn forecast_attach(
    state: &State,
    actor: usize,
    attachments: &[(u32, EnergyType, usize)],
    is_turn_energy: bool,
) -> Outcomes {
    let Some(in_play_idx) = buggy_evolution_target(state, actor, attachments) else {
        return forecast_deterministic_action();
    };
    let attachments = attachments.to_vec();
    shared_mutations::random_evolution_from_deck_outcomes(actor, in_play_idx, state).map_mutations(
        move |evolve| {
            let attachments = attachments.clone();
            Box::new(
                move |rng: &mut StdRng, state: &mut State, action: &Action| {
                    apply_attach_energy(state, actor, &attachments, is_turn_energy);
                    evolve(rng, state, action);
                },
            )
        },
    )
}

/// The in-play index Buggy Evolution would fire on for this attachment list, if any.
fn buggy_evolution_target(
    state: &State,
    actor: usize,
    attachments: &[(u32, EnergyType, usize)],
) -> Option<usize> {
    attachments
        .iter()
        .map(|(_, _, in_play_idx)| *in_play_idx)
        .find(|in_play_idx| {
            state.in_play_pokemon[actor][*in_play_idx]
                .as_ref()
                .is_some_and(|pokemon| {
                    matches!(
                        get_in_play_ability_mechanic(state, pokemon),
                        Some(AbilityMechanic::RandomEvolutionFromDeck {
                            trigger: RandomEvolutionTrigger::OnEnergyZoneAttachToSelf,
                        })
                    )
                })
        })
}

/// ApplyDamage (damage queued through the move-generation stack, e.g. Mega Kangaskhan's second
/// punch or Raikou ex's spot damage) is deterministic unless a target has the Guts ability and
/// would be knocked out: each such target flips its own survival coin, independently of any
/// Guts flip already resolved earlier in the same attack.
fn forecast_apply_damage(
    state: &State,
    attacking_ref: (usize, usize),
    targets: &[(u32, usize, usize)],
    is_from_active_attack: bool,
) -> Outcomes {
    // Sum raw damage per target (mirroring handle_damage_only) to find the Guts coin flips.
    let mut damage_map: HashMap<(usize, usize), u32> = HashMap::new();
    for (damage, player, idx) in targets {
        *damage_map.entry((*player, *idx)).or_insert(0) += damage;
    }
    let flipping: Vec<(usize, usize)> = damage_map
        .into_iter()
        .filter(|(target, raw_total)| {
            guts_would_flip(
                state,
                attacking_ref,
                *raw_total,
                *target,
                is_from_active_attack,
                DamageModifierContext {
                    attack_name: None,
                    attack_effect: None,
                },
            )
        })
        .map(|(target, _)| target)
        .collect();

    if flipping.is_empty() {
        let targets = targets.to_vec();
        return Outcomes::single_fn(move |_, state, _| {
            handle_damage(state, attacking_ref, &targets, is_from_active_attack, None);
        });
    }

    // One branch per heads/tails combination; on heads the damage still applies (so on-damage
    // triggers fire) and the survivor's remaining HP is set to 10 before knockouts resolve.
    let combos = 1usize << flipping.len();
    let probabilities = vec![1.0 / combos as f64; combos];
    let mut mutations: Mutations = vec![];
    for mask in 0..combos {
        let survivors: Vec<(usize, usize)> = flipping
            .iter()
            .enumerate()
            .filter(|(bit, _)| (mask >> bit) & 1 == 1)
            .map(|(_, target)| *target)
            .collect();
        let targets = targets.to_vec();
        mutations.push(Box::new(move |_, state, _| {
            handle_damage_only(
                state,
                attacking_ref,
                &targets,
                is_from_active_attack,
                DamageModifierContext {
                    attack_name: None,
                    attack_effect: None,
                },
            );
            for (player, idx) in &survivors {
                if let Some(pokemon) = state.in_play_pokemon[*player][*idx].as_mut() {
                    pokemon.set_remaining_hp(10);
                }
            }
            handle_knockouts(state, attacking_ref, is_from_active_attack);
        }));
    }
    Outcomes::from_parts(probabilities, mutations)
}

fn apply_deterministic_action(state: &mut State, action: &Action) {
    match &action.action {
        SimpleAction::DrawCard { amount } => {
            for _ in 0..*amount {
                state.maybe_draw_card(action.actor);
            }
        }
        SimpleAction::Attach {
            attachments,
            is_turn_energy,
        } => apply_attach_energy(state, action.actor, attachments, *is_turn_energy),
        SimpleAction::AttachTool {
            in_play_idx,
            tool_card,
        } => apply_attach_tool(state, action.actor, *in_play_idx, tool_card),
        SimpleAction::MoveEnergy {
            from_in_play_idx,
            to_in_play_idx,
            energy_type,
            amount,
        } => apply_move_energy(
            state,
            action.actor,
            *from_in_play_idx,
            *to_in_play_idx,
            *energy_type,
            *amount,
        ),
        SimpleAction::MoveEnergies {
            from_in_play_idx,
            to_in_play_idx,
            energies,
        } => apply_move_energies(
            state,
            action.actor,
            *from_in_play_idx,
            *to_in_play_idx,
            energies,
        ),
        SimpleAction::Place(card, index) => {
            apply_place_card(state, action.actor, card, *index, false)
        }
        SimpleAction::Evolve {
            evolution,
            in_play_idx,
            from_deck,
        } => apply_evolve(action.actor, state, evolution, *in_play_idx, *from_deck),
        SimpleAction::Activate {
            player,
            in_play_idx,
        }
        | SimpleAction::Promote {
            player,
            in_play_idx,
        } => apply_retreat(*player, state, *in_play_idx, true),
        SimpleAction::Retreat(position) => apply_retreat(action.actor, state, *position, false),
        SimpleAction::ScheduleDelayedSpotDamage {
            target_player,
            target_in_play_idx,
            amount,
            knock_out,
        } => apply_schedule_delayed_spot_damage(
            state,
            action.actor,
            *target_player,
            *target_in_play_idx,
            *amount,
            *knock_out,
        ),
        // Trainer-Specific Actions
        SimpleAction::Heal {
            in_play_idx,
            amount,
            cure_status,
        } => apply_healing(action.actor, state, *in_play_idx, *amount, *cure_status),
        SimpleAction::HealAndDiscardEnergy {
            in_play_idx,
            heal_amount,
            discard_energies,
        } => apply_heal_and_discard_energy(
            action.actor,
            state,
            *in_play_idx,
            *heal_amount,
            discard_energies,
        ),
        SimpleAction::HealAndCureConditions {
            in_play_idx,
            amount,
            conditions,
        } => apply_heal_and_cure_conditions(action.actor, state, *in_play_idx, *amount, conditions),
        SimpleAction::BenchOpponentFromDiscard { card, bench_idx } => {
            apply_bench_opponent_from_discard(action.actor, state, card, *bench_idx)
        }
        SimpleAction::BenchOpponentHandBasics { cards } => {
            apply_bench_opponent_hand_basics(action.actor, state, cards)
        }
        SimpleAction::MoveDamageToOpponentActive {
            from_in_play_idx,
            amount,
        } => apply_move_damage_to_opponent_active(action.actor, state, *from_in_play_idx, *amount),
        SimpleAction::MoveAllDamage { from, to } => {
            apply_move_all_damage(action.actor, state, *from, *to)
        }
        SimpleAction::ApplyEeveeBagDamageBoost => apply_eevee_bag_damage_boost(state),
        SimpleAction::HealAllEeveeEvolutions => {
            apply_heal_all_eevee_evolutions(action.actor, state)
        }
        SimpleAction::DiscardFossil { in_play_idx } => {
            apply_discard_fossil(action.actor, state, *in_play_idx)
        }
        SimpleAction::ConsolidateEnergyToPokemon {
            to_in_play_idx,
            transfers,
        } => apply_consolidate_energy_to_pokemon(action.actor, state, *to_in_play_idx, transfers),
        SimpleAction::ReturnPokemonToHand { in_play_idx } => {
            apply_return_pokemon_to_hand(action.actor, state, *in_play_idx)
        }
        SimpleAction::DiscardToolFromPokemon {
            player,
            in_play_idx,
            tool_idx,
        } => {
            state.discard_tool(*player, *in_play_idx, *tool_idx);
        }
        SimpleAction::DiscardActiveStadium => {
            if let Some((stadium, owner)) = state.take_active_stadium() {
                state.discard_piles[owner.unwrap_or(action.actor)].push(stadium);
            }
        }
        SimpleAction::PutCardFromDiscardToHand { card } => {
            state.transfer_card_from_discard_to_hand(action.actor, card)
        }
        SimpleAction::DiscardRandomOpponentActiveEnergy => {
            let opponent = (action.actor + 1) % 2;
            if let Some(energy) = state.get_active(opponent).attached_energy.last().copied() {
                state.discard_from_active(opponent, &[energy]);
            }
        }
        SimpleAction::MoveRandomOpponentEnergyToActive { from_in_play_idx } => {
            let opponent = (action.actor + 1) % 2;
            // NOTE: Using the last energy instead of a random one to avoid expanding the game
            // tree, mirroring DiscardRandomOpponentActiveEnergy and Piers.
            apply_move_last_energy(state, opponent, *from_in_play_idx, 0);
        }
        SimpleAction::ApplyStatusToOpponentActive { condition } => {
            // Only ever queued by an attack (Dustox's Select Powder), so it goes through the
            // attack-effect gate that Regice's Crystal Body sits behind.
            let opponent = (action.actor + 1) % 2;
            state.apply_attack_status_condition(opponent, 0, *condition);
        }
        SimpleAction::DiscardOwnBenchedThenDamage {
            in_play_idxs,
            damage,
        } => apply_discard_own_benched_then_damage(action.actor, state, in_play_idxs, *damage),
        SimpleAction::Noop => {}
        _ => panic!("Deterministic Action expected"),
    }
}

fn apply_attach_energy(
    state: &mut State,
    actor: usize,
    attachments: &[(u32, EnergyType, usize)],
    is_turn_energy: bool,
) {
    for (amount, energy, in_play_idx) in attachments {
        // it can happen that in the first iteration of for loop the pokemon was K.O.ed
        // if so, just skip the rest of the attachments.
        if state.in_play_pokemon[actor][*in_play_idx].is_none() {
            continue;
        }

        state.attach_energy_from_zone(actor, *in_play_idx, *energy, *amount, is_turn_energy);
    }
}

fn apply_attach_tool(state: &mut State, actor: usize, in_play_idx: usize, tool_card: &Card) {
    tools::ensure_tool_card(tool_card);
    let holder = state.in_play_pokemon[actor][in_play_idx]
        .as_ref()
        .expect("Pokemon should be there if attaching tool to it");
    assert!(
        holder.attached_tools.len() < tools::tool_capacity(state, holder),
        "Pokemon has no free Tool slot"
    );
    {
        let pokemon = state.in_play_pokemon[actor][in_play_idx]
            .as_mut()
            .expect("Pokemon should be there if attaching tool to it");
        pokemon.attached_tools.push(tool_card.clone());
    }

    // Steel Apron: "...recovers from all Special Conditions..." only for a [M] holder.
    let pokemon = state.in_play_pokemon[actor][in_play_idx]
        .as_ref()
        .expect("Pokemon should be there if attaching tool to it");
    if tools::has_tool(pokemon, crate::card_ids::CardId::A4153SteelApron)
        && state.pokemon_is_type(pokemon, crate::models::EnergyType::Metal)
    {
        state.in_play_pokemon[actor][in_play_idx]
            .as_mut()
            .expect("Pokemon should be there if attaching tool to it")
            .cure_status_conditions();
    }
}

/// Moves 1 Energy from `from_idx` to `to_idx` within `player`'s own board, without the caller
/// having to know which Energy types are attached.
fn apply_move_last_energy(state: &mut State, player: usize, from_idx: usize, to_idx: usize) {
    let energy = state.in_play_pokemon[player][from_idx]
        .as_ref()
        .and_then(|pokemon| pokemon.attached_energy.last().copied());
    if let Some(energy) = energy {
        apply_move_energy(state, player, from_idx, to_idx, energy, 1);
    }
}

fn apply_move_energy(
    state: &mut State,
    actor: usize,
    from_idx: usize,
    to_idx: usize,
    energy_type: EnergyType,
    amount: u32,
) {
    let actor_board = &mut state.in_play_pokemon[actor];
    let mut removed_energies = Vec::new();

    // Remove the specified amount of energy from source
    if let Some(from_card) = actor_board[from_idx].as_mut() {
        for _ in 0..amount {
            if let Some(pos) = from_card
                .attached_energy
                .iter()
                .position(|e| e == &energy_type)
            {
                from_card.attached_energy.swap_remove(pos);
                removed_energies.push(energy_type);
            } else {
                break; // No more energy of this type to remove
            }
        }
    }

    // Add removed energies to destination
    if !removed_energies.is_empty() {
        let moved_to_destination = if let Some(to_card) = actor_board[to_idx].as_mut() {
            to_card.attached_energy.extend(removed_energies);
            true
        } else if let Some(from_card) = actor_board[from_idx].as_mut() {
            // Put energies back if destination vanished (should not normally happen)
            from_card.attached_energy.extend(removed_energies);
            false
        } else {
            false
        };
        if moved_to_destination {
            state.apply_soothing_wind_to_pokemon(actor, to_idx);
        }
    }
}

/// Move a specific (possibly mixed-type) set of energies between two of the actor's in-play
/// Pokémon. Only energies actually attached to the source are moved (best effort).
fn apply_move_energies(
    state: &mut State,
    actor: usize,
    from_idx: usize,
    to_idx: usize,
    energies: &[EnergyType],
) {
    let actor_board = &mut state.in_play_pokemon[actor];
    let mut removed_energies = Vec::new();

    if let Some(from_card) = actor_board[from_idx].as_mut() {
        for energy in energies {
            if let Some(pos) = from_card.attached_energy.iter().position(|e| e == energy) {
                from_card.attached_energy.swap_remove(pos);
                removed_energies.push(*energy);
            }
        }
    }

    if !removed_energies.is_empty() {
        let moved_to_destination = if let Some(to_card) = actor_board[to_idx].as_mut() {
            to_card.attached_energy.extend(removed_energies);
            true
        } else if let Some(from_card) = actor_board[from_idx].as_mut() {
            // Put energies back if destination vanished (should not normally happen)
            from_card.attached_energy.extend(removed_energies);
            false
        } else {
            false
        };
        if moved_to_destination {
            state.apply_soothing_wind_to_pokemon(actor, to_idx);
        }
    }
}

pub(crate) fn apply_place_card(
    state: &mut State,
    actor: usize,
    card: &Card,
    index: usize,
    from_deck: bool,
) {
    let played_card = to_playable_card(card, true);
    state.in_play_pokemon[actor][index] = Some(played_card);
    state.refresh_hp_bonuses_all();
    // SoothingWind (Ogerpon ex) / Flower Shield (Comfey): cure status conditions on entry.
    if let Some(AbilityMechanic::SoothingWind { energy_type }) =
        get_entering_play_ability_mechanic(state, card)
    {
        debug!("SoothingWind: Pokémon entered play – curing status conditions for player {actor}");
        state.apply_soothing_wind_for_player(actor, energy_type.as_ref());
    }
    if from_deck {
        state.remove_card_from_deck(actor, card);
    } else {
        state.remove_card_from_hand(actor, card);
        let placed_in_bench = index != 0;
        if placed_in_bench
            && get_entering_play_ability_mechanic(state, card)
                == Some(&AbilityMechanic::InfiltratingInspection)
        {
            debug!("Misdreavus's Infiltrating Inspection: Opponent's hand is revealed (no-op in AI context)");
        }
        if placed_in_bench {
            on_bench_from_hand(actor, state, card, index);
        }
    }
}

fn apply_discard_fossil(acting_player: usize, state: &mut State, in_play_idx: usize) {
    // Discard the fossil from play (handles evolution chain and energies)
    state.discard_from_play(acting_player, in_play_idx);

    // If discarding from active spot, trigger promotion or declare winner
    if in_play_idx == 0 {
        state.trigger_promotion_or_declare_winner(acting_player);
    }
}

/// §47 — Move the planned Energy onto `to_in_play_idx` in one step.
///
/// Sources and destination are re-checked here rather than trusted: the action is generated when
/// the choice is offered, and a Pokémon can leave play between then and here.
fn apply_consolidate_energy_to_pokemon(
    acting_player: usize,
    state: &mut State,
    to_in_play_idx: usize,
    transfers: &[(usize, Vec<EnergyType>)],
) {
    if state.in_play_pokemon[acting_player][to_in_play_idx].is_none() {
        return;
    }
    let mut moved: Vec<EnergyType> = Vec::new();
    for (from_in_play_idx, energies) in transfers {
        let Some(source) = state.in_play_pokemon[acting_player][*from_in_play_idx].as_mut() else {
            continue;
        };
        for energy in energies {
            if let Some(position) = source.attached_energy.iter().position(|e| e == energy) {
                source.attached_energy.remove(position);
                moved.push(*energy);
            }
        }
    }
    if moved.is_empty() {
        return;
    }
    debug!(
        "Consolidating {} Energy onto slot {}",
        moved.len(),
        to_in_play_idx
    );
    if let Some(destination) = state.in_play_pokemon[acting_player][to_in_play_idx].as_mut() {
        destination.attached_energy.extend(moved);
        state.apply_soothing_wind_to_pokemon(acting_player, to_in_play_idx);
    }
}

fn apply_return_pokemon_to_hand(acting_player: usize, state: &mut State, in_play_idx: usize) {
    let played_card = state.in_play_pokemon[acting_player][in_play_idx]
        .take()
        .expect("Pokemon should be there if returning to hand");
    let mut cards_to_collect = played_card.cards_behind.clone();
    cards_to_collect.push(played_card.card.clone());
    state.hands[acting_player].extend(cards_to_collect);
    state.discard_piles[acting_player].extend(played_card.attached_tools);
    state.discard_energies[acting_player].extend(played_card.attached_energy);
    state.refresh_hp_bonuses_all();

    // If returning the active, trigger promotion or declare winner.
    if in_play_idx == 0 {
        state.trigger_promotion_or_declare_winner(acting_player);
    }
}

fn apply_shuffle_in_play_pokemon_into_deck(
    acting_player: usize,
    state: &mut State,
    in_play_idx: usize,
) {
    let played_card = state.in_play_pokemon[acting_player][in_play_idx]
        .take()
        .expect("Pokemon should be there if shuffling into deck");
    let mut cards_to_shuffle = played_card.cards_behind.clone();
    cards_to_shuffle.push(played_card.card.clone());
    state.decks[acting_player].cards.extend(cards_to_shuffle);
    state.discard_piles[acting_player].extend(played_card.attached_tools);
    state.discard_energies[acting_player].extend(played_card.attached_energy);
    state.refresh_hp_bonuses_all();

    if in_play_idx == 0 {
        state.trigger_promotion_or_declare_winner(acting_player);
    }
}

/// Gyarados' Wild Swing: discard the chosen Benched Pokémon, then queue the resulting damage.
///
/// The damage is queued as a one-choice `ApplyDamage` rather than applied inline so that it goes
/// through the same pipeline as any other attack damage — weakness and the other modifiers, Rocky
/// Helmet style counterattacks, and the defender's Guts coin flip all still resolve.
fn apply_discard_own_benched_then_damage(
    acting_player: usize,
    state: &mut State,
    in_play_idxs: &[usize],
    damage: u32,
) {
    // Descending, so removing one slot never shifts the meaning of a later one (it does not today,
    // since slots are fixed positions, but it keeps the loop independent of that).
    let mut idxs = in_play_idxs.to_vec();
    idxs.sort_unstable();
    idxs.reverse();
    for in_play_idx in idxs {
        if state.in_play_pokemon[acting_player][in_play_idx].is_some() {
            state.discard_from_play(acting_player, in_play_idx);
        }
    }

    let opponent = (acting_player + 1) % 2;
    if state.in_play_pokemon[opponent][0].is_none() {
        return;
    }
    state.move_generation_stack.push((
        acting_player,
        vec![SimpleAction::ApplyDamage {
            attacking_ref: (acting_player, 0),
            targets: vec![(damage, opponent, 0)],
            is_from_active_attack: true,
        }],
    ));
}

fn apply_healing(
    acting_player: usize,
    state: &mut State,
    position: usize,
    amount: u32,
    cure_status: bool,
) {
    // Heal Block stops the healing, but not the "and remove all Special Conditions" clause that
    // some printings carry: curing a Special Condition is not healing.
    state.heal_pokemon(acting_player, position, amount);
    if cure_status {
        state.in_play_pokemon[acting_player][position]
            .as_mut()
            .expect("Pokemon should be there if healing it")
            .cure_status_conditions();
    }
}

fn apply_schedule_delayed_spot_damage(
    state: &mut State,
    source_player: usize,
    target_player: usize,
    target_in_play_idx: usize,
    amount: u32,
    knock_out: bool,
) {
    state.add_turn_effect(
        TurnEffect::DelayedSpotDamage {
            source_player,
            target_player,
            target_in_play_idx,
            amount,
            knock_out,
        },
        1,
    );
}

fn apply_heal_and_discard_energy(
    acting_player: usize,
    state: &mut State,
    position: usize,
    heal_amount: u32,
    discard_energies: &[EnergyType],
) {
    // "Heal X damage from 1 of your Pokémon ex. If you do, discard an Energy from it": under Heal
    // Block nothing is healed, so the "if you do" clause must not fire either.
    let healed = state.heal_pokemon(acting_player, position, heal_amount);
    if healed == 0 {
        return;
    }
    state.discard_energy_from_in_play(acting_player, position, discard_energies);
}

/// Heal `amount` and clear only the listed Special Conditions (Whitney). Unlike
/// `apply_healing`'s `cure_status`, conditions not listed are left in place.
fn apply_heal_and_cure_conditions(
    acting_player: usize,
    state: &mut State,
    position: usize,
    amount: u32,
    conditions: &[StatusCondition],
) {
    // Healing goes through `State::heal_pokemon` so Claydol's Heal Block suppresses it; the
    // status cure is not healing and still applies.
    state.heal_pokemon(acting_player, position, amount);
    let pokemon = state.in_play_pokemon[acting_player][position]
        .as_mut()
        .expect("Pokemon should be there if healing it");
    for condition in conditions {
        pokemon.clear_status_condition(*condition);
    }
}

/// Pokémon Flute: take a specific Basic Pokémon out of the opponent's discard pile and place it
/// on their Bench. The card belongs to the opponent throughout, so it is removed from *their*
/// discard pile and placed on *their* board.
fn apply_bench_opponent_from_discard(
    actor: usize,
    state: &mut State,
    card: &Card,
    bench_idx: usize,
) {
    let opponent = (actor + 1) % 2;
    let Some(idx) = state.discard_piles[opponent].iter().position(|c| c == card) else {
        return;
    };
    if state.in_play_pokemon[opponent][bench_idx].is_some() {
        return;
    }
    state.discard_piles[opponent].remove(idx);
    let played_card = to_playable_card(card, true);
    state.in_play_pokemon[opponent][bench_idx] = Some(played_card);
    state.refresh_hp_bonuses_all();
}

fn apply_bench_opponent_hand_basics(actor: usize, state: &mut State, cards: &[Card]) {
    let opponent = 1 - actor;
    let free_slots = state.in_play_pokemon[opponent]
        .iter()
        .enumerate()
        .skip(1)
        .filter_map(|(idx, slot)| slot.is_none().then_some(idx))
        .collect::<Vec<_>>();
    if cards.len() > free_slots.len() {
        return;
    }

    let mut remaining = state.hands[opponent].clone();
    for card in cards {
        if !matches!(card, Card::Pokemon(pokemon) if pokemon.stage == 0) {
            return;
        }
        let Some(index) = remaining.iter().position(|candidate| candidate == card) else {
            return;
        };
        remaining.remove(index);
    }
    for (card, bench_idx) in cards.iter().zip(free_slots) {
        apply_place_card(state, opponent, card, bench_idx, false);
    }
}

/// Acerola: move up to `amount` damage from one of `actor`'s Pokémon onto the opponent's Active
/// Pokémon. Like `apply_move_all_damage`, the transferred damage goes through `handle_damage` so
/// knockouts and on-damage effects resolve, but with `is_from_active_attack: false` — moved damage
/// is not an attack.
fn apply_move_damage_to_opponent_active(
    actor: usize,
    state: &mut State,
    from_in_play_idx: usize,
    amount: u32,
) {
    let opponent = (actor + 1) % 2;
    if state.maybe_get_active(opponent).is_none() {
        return;
    }
    let damage_to_move = {
        let from_pokemon = state.in_play_pokemon[actor][from_in_play_idx]
            .as_ref()
            .expect("Pokemon to move damage from should be there");
        amount.min(from_pokemon.get_damage_counters())
    };
    if damage_to_move == 0 {
        return;
    }

    state.in_play_pokemon[actor][from_in_play_idx]
        .as_mut()
        .expect("Pokemon to move damage from should be there")
        // Moving damage counters is not healing, so it deliberately bypasses Heal Block.
        .heal_raw(damage_to_move);
    handle_damage(
        state,
        (actor, from_in_play_idx),
        &[(damage_to_move, opponent, 0)],
        false,
        None,
    );
}

fn apply_move_all_damage(actor: usize, state: &mut State, from: usize, to: usize) {
    let damage_to_move = {
        let from_pokemon = state.in_play_pokemon[actor][from]
            .as_ref()
            .expect("Pokemon to move damage from should be there");
        from_pokemon.get_damage_counters()
    };

    if damage_to_move > 0 {
        let from_pokemon = state.in_play_pokemon[actor][from]
            .as_mut()
            .expect("Pokemon to move damage from should be there");
        // Moving damage counters is not healing, so it deliberately bypasses Heal Block.
        from_pokemon.heal_raw(damage_to_move);

        // Use handle_damage to ensure KO checks and other effects are triggered
        let targets = vec![(damage_to_move, actor, to)];
        // Attacking ref is (actor, from) as the source of the damage move
        handle_damage(state, (actor, from), &targets, false, None);
    }
}

/// is_free is analogous to "via retreat". If false, its because this comes from an Activate.
/// Note: This might be called when a K.O. happens, so can't assume there is an active...
fn apply_retreat(player: usize, state: &mut State, bench_idx: usize, is_free: bool) {
    if !is_free {
        let active = state.in_play_pokemon[player][0]
            .as_ref()
            .expect("Active Pokemon should be there if paid retreating");
        let double_grass = active.has_double_grass(state, player);
        let retreat_cost = get_retreat_cost(state, active).len();
        let attached_energy: &mut Vec<_> = state.in_play_pokemon[player][0]
            .as_mut()
            .expect("Active Pokemon should be there if paid retreating")
            .attached_energy
            .as_mut();

        // TODO: Maybe give option to user to select which energy to discard

        // Some energies are worth more than others... For now decide the ordering
        // that keeps as much Grass energy as possible (since possibly worth more).

        // Re-order energies so that Grass are at the beginning
        attached_energy.sort_by(|a, b| {
            if *a == EnergyType::Grass && *b != EnergyType::Grass {
                std::cmp::Ordering::Less
            } else if *a != EnergyType::Grass && *b == EnergyType::Grass {
                std::cmp::Ordering::Greater
            } else {
                std::cmp::Ordering::Equal
            }
        });

        // Start walking from the back in the attached, removing energies until retreat cost is paid
        let mut remaining_cost = retreat_cost;
        let mut discarded: Vec<EnergyType> = vec![];
        while remaining_cost > 0 && !attached_energy.is_empty() {
            let energy = attached_energy.pop().unwrap();
            discarded.push(energy);
            if energy == EnergyType::Grass && double_grass {
                remaining_cost = remaining_cost.saturating_sub(2);
            } else {
                remaining_cost = remaining_cost.saturating_sub(1);
            }
        }
        if remaining_cost > 0 {
            panic!("Not enough energy to pay retreat cost");
        }

        if !discarded.is_empty() {
            state.discard_energies[player].extend(discarded);
        }

        state.has_retreated = true;
    }

    apply_activate(player, state, bench_idx);

    if !is_free {
        apply_snapping_trap_on_retreat(player, state);
    }
}

/// Galarian Stunfisk's Snapping Trap: "During your opponent's next turn, if this Pokémon is in the
/// Active Spot when your opponent's Active Pokémon retreats, this attack does 40 damage to the new
/// Active Pokémon." Only a genuine retreat triggers it, not a free promotion or a switch card, so
/// this is called from the paid branch of `apply_retreat` after the promotion has happened.
fn apply_snapping_trap_on_retreat(retreating_player: usize, state: &mut State) {
    let trapper = (retreating_player + 1) % 2;
    let damage: u32 = state.in_play_pokemon[trapper][0]
        .as_ref()
        .map(|pokemon| {
            pokemon
                .get_active_effects()
                .iter()
                .filter_map(|effect| match effect {
                    CardEffect::DamageNewActiveOnRetreat { amount } => Some(*amount),
                    _ => None,
                })
                .sum()
        })
        .unwrap_or(0);
    if damage == 0 || state.in_play_pokemon[retreating_player][0].is_none() {
        return;
    }
    handle_damage(
        state,
        (trapper, 0),
        &[(damage, retreating_player, 0)],
        false,
        None,
    );
}

// We will replace the PlayedCard, but taking into account the attached energy
//  and the remaining HP.
pub(crate) fn apply_evolve(
    acting_player: usize,
    state: &mut State,
    to_card: &Card,
    position: usize,
    from_deck: bool,
) {
    // This removes status conditions
    let mut played_card = to_playable_card(to_card, true);

    let from_pokemon = state.in_play_pokemon[acting_player][position]
        .as_ref()
        .expect("Pokemon should be there if evolving it");
    if let Card::Pokemon(to_pokemon) = &played_card.card {
        if to_pokemon.stage == 0 {
            panic!("Basic pokemon do not evolve from others...");
        }

        let damage_taken = from_pokemon.get_damage_counters();
        played_card.apply_damage(damage_taken);
        played_card.attached_energy = from_pokemon.attached_energy.clone();
        played_card.attached_tools = from_pokemon.attached_tools.clone();
        played_card.cards_behind = from_pokemon.cards_behind.clone();
        played_card.cards_behind.push(from_pokemon.card.clone());
        state.in_play_pokemon[acting_player][position] = Some(played_card);
        state.refresh_hp_bonuses_all();
    } else {
        panic!("Only Pokemon cards can be evolved");
    }

    // Remove the evolution card from either hand or deck depending on the source
    if from_deck {
        state.remove_card_from_deck(acting_player, to_card);
    } else {
        state.remove_card_from_hand(acting_player, to_card);
    }

    // Run special logic hooks on evolution
    on_evolve(acting_player, state, to_card, position, !from_deck)
}

fn forecast_pokemon_communication(
    acting_player: usize,
    state: &State,
    hand_pokemon: &Card,
) -> Outcomes {
    let deck_pokemon: Vec<_> = state.iter_deck_pokemon(acting_player).collect();

    let num_deck_pokemon = deck_pokemon.len();
    if num_deck_pokemon == 0 {
        // Should not happen if move generation is correct, but just shuffle deck
        return Outcomes::single_fn(|rng, state, action| {
            state.decks[action.actor].shuffle(false, rng);
        });
    }

    // Create uniform probability for each deck Pokemon (1/N for each)
    let probabilities = vec![1.0 / (num_deck_pokemon as f64); num_deck_pokemon];
    let mut outcomes: Mutations = vec![];
    for i in 0..num_deck_pokemon {
        let hand_pokemon_clone = hand_pokemon.clone();
        outcomes.push(Box::new(move |rng, state, action| {
            // Get the i-th Pokemon from deck
            let deck_pokemon_card = state
                .iter_deck_pokemon(action.actor)
                .nth(i)
                .cloned()
                .expect("Deck Pokemon should exist");

            // Perform the swap
            // 1. Transfer hand Pokemon to deck
            state.transfer_card_from_hand_to_deck(action.actor, &hand_pokemon_clone);
            // 2. Transfer deck Pokemon to hand
            state.transfer_card_from_deck_to_hand(action.actor, &deck_pokemon_card);
            // 5. Shuffle deck
            state.decks[action.actor].shuffle(false, rng);

            debug!(
                "Pokemon Communication: Swapped {:?} from hand with {:?} from deck",
                hand_pokemon_clone, deck_pokemon_card
            );
        }));
    }

    Outcomes::from_parts(probabilities, outcomes)
}

fn forecast_shuffle_pokemon_into_deck(acting_player: usize, hand_pokemon: &[Card]) -> Outcomes {
    let pokemon_list = hand_pokemon.to_vec();
    Outcomes::single_fn(move |rng, state, _action| {
        for pokemon in &pokemon_list {
            state.transfer_card_from_hand_to_deck(acting_player, pokemon);
        }
        state.decks[acting_player].shuffle(false, rng);
        debug!("May: Shuffled {:?} from hand into deck", pokemon_list);
    })
}

fn forecast_shuffle_own_cards_into_deck(acting_player: usize, cards: &[Card]) -> Outcomes {
    let cards_to_shuffle = cards.to_vec();
    Outcomes::single_fn(move |rng, state, _action| {
        for card in &cards_to_shuffle {
            state.transfer_card_from_hand_to_deck(acting_player, card);
        }
        state.decks[acting_player].shuffle(false, rng);
        state.maybe_draw_card(acting_player);
        debug!(
            "Maintenance: Shuffled {:?} from hand into deck, then drew a card",
            cards_to_shuffle
        );
    })
}

fn forecast_shuffle_opponent_hand_card(acting_player: usize, card: &Card) -> Outcomes {
    let card_clone = card.clone();
    Outcomes::single_fn(move |rng, state, _action| {
        let opponent = (acting_player + 1) % 2;
        state.transfer_card_from_hand_to_deck(opponent, &card_clone);
        state.decks[opponent].shuffle(false, rng);
        debug!("Shuffled {card_clone:?} from opponent's hand into their deck");
    })
}

fn forecast_discard_opponent_supporter(acting_player: usize, supporter_card: &Card) -> Outcomes {
    let supporter_clone = supporter_card.clone();
    Outcomes::single_fn(move |_rng, state, _action| {
        let opponent = (acting_player + 1) % 2;
        state.discard_card_from_hand(opponent, &supporter_clone);
        debug!(
            "Mega Absol Ex: Discarded {:?} from opponent's hand",
            supporter_clone
        );
    })
}

fn forecast_discard_own_cards(acting_player: usize, cards: &[Card]) -> Outcomes {
    let cards_clone = cards.to_vec();
    Outcomes::single_fn(move |_rng, state, _action| {
        for card in &cards_clone {
            state.discard_card_from_hand(acting_player, card);
        }
        debug!("Discarded {:?} from hand", cards_clone);
    })
}

/// Slowking's Litter: discard the chosen cards, then queue the attack's damage, which is
/// `damage_per_card` for every card actually discarded. The damage goes through the normal
/// `ApplyDamage` path (same as Bombirdier's Rock Throw) so weakness, damage modifiers and
/// knockouts are handled by the shared pipeline.
fn forecast_discard_own_cards_for_attack_damage(
    acting_player: usize,
    cards: &[Card],
    damage_per_card: u32,
) -> Outcomes {
    let cards_clone = cards.to_vec();
    Outcomes::single_fn(move |_rng, state, _action| {
        for card in &cards_clone {
            state.discard_card_from_hand(acting_player, card);
        }
        let damage = damage_per_card * cards_clone.len() as u32;
        debug!("Discarded {cards_clone:?} from hand for {damage} attack damage");
        if damage > 0 {
            let opponent = (acting_player + 1) % 2;
            state.move_generation_stack.push((
                acting_player,
                vec![SimpleAction::ApplyDamage {
                    attacking_ref: (acting_player, 0),
                    targets: vec![(damage, opponent, 0)],
                    is_from_active_attack: true,
                }],
            ));
        }
    })
}

fn forecast_attach_from_discard(
    state: &State,
    acting_player: usize,
    in_play_idx: usize,
    num_random_energies: usize,
) -> Outcomes {
    let discard_energies = &state.discard_energies[acting_player];
    let actual_num = std::cmp::min(num_random_energies, discard_energies.len());

    if actual_num == 0 {
        return Outcomes::single_fn(|_, _, _| {});
    }
    if actual_num == 1 {
        // Deterministic: just attach the first energy
        let energy = discard_energies[0];
        return Outcomes::single_fn(move |_rng, state, action| {
            state.attach_energy_from_discard(action.actor, in_play_idx, &[energy]);
            debug!(
                "Lusamine: Attached {:?} from discard to Pokemon at index {}",
                energy, in_play_idx
            );
        });
    }

    // For 2 energies, generate all combinations and deduplicate
    let combinations = generate_energy_combinations(discard_energies);
    let total_combinations: usize = combinations.iter().map(|(_, count)| count).sum();

    let mut probabilities = Vec::new();
    let mut mutations: Mutations = Vec::new();
    for (combo, count) in combinations {
        let probability = count as f64 / total_combinations as f64;
        probabilities.push(probability);
        mutations.push(Box::new(move |_rng, state, action| {
            state.attach_energy_from_discard(action.actor, in_play_idx, &combo);
            debug!(
                "Lusamine: Attached {:?} from discard to Pokemon at index {}",
                combo, in_play_idx
            );
        }));
    }

    Outcomes::from_parts(probabilities, mutations)
}

/// Volkner: deterministically attach up to `count` energies of `energy_type` from discard.
fn forecast_attach_typed_from_discard(
    in_play_idx: usize,
    energy_type: EnergyType,
    count: usize,
) -> Outcomes {
    Outcomes::single_fn(move |_rng, state, action| {
        let available = state.discard_energies[action.actor]
            .iter()
            .filter(|e| **e == energy_type)
            .count();
        let energies = vec![energy_type; std::cmp::min(count, available)];
        state.attach_energy_from_discard(action.actor, in_play_idx, &energies);
    })
}

/// Generate all unique 2-energy combinations from a list of energies in discard pile.
/// Returns a vector of (combination, count) tuples where count is how many times
/// this combination appears when considering all possible pairs.
fn generate_energy_combinations(energies: &[EnergyType]) -> Vec<(Vec<EnergyType>, usize)> {
    let mut combination_counts: HashMap<Vec<EnergyType>, usize> = HashMap::new();
    for i in 0..energies.len() {
        for j in (i + 1)..energies.len() {
            let mut combo = vec![energies[i], energies[j]];
            combo.sort(); // Sort to treat [Grass, Fire] same as [Fire, Grass]
            *combination_counts.entry(combo).or_insert(0) += 1;
        }
    }
    combination_counts.into_iter().collect()
}

fn forecast_sada_attach(assignments: &[(crate::models::EnergyType, usize)]) -> Outcomes {
    let assignments = assignments.to_vec();
    Outcomes::single_fn(move |_, state, action| {
        for (energy, in_play_idx) in &assignments {
            state.attach_energy_from_discard(action.actor, *in_play_idx, &[*energy]);
        }
    })
}

fn apply_eevee_bag_damage_boost(state: &mut State) {
    use crate::effects::TurnEffect;
    state.add_turn_effect(
        TurnEffect::IncreasedDamageForEeveeEvolutions { amount: 10 },
        0,
    );
}

fn apply_heal_all_eevee_evolutions(acting_player: usize, state: &mut State) {
    state.heal_each_pokemon(acting_player, 20, |pokemon| pokemon.evolved_from("Eevee"));
}

// Test that when evolving a damanged pokemon, damage stays.
#[cfg(test)]
mod tests {
    use rand::{RngCore, SeedableRng};

    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::{
        models::{Card, EnergyType, PlayedCard},
        Deck,
    };

    #[test]
    fn victory_star_stages_only_vaporeons_coin_marginal() {
        let Card::Pokemon(vaporeon) = get_card_by_enum(CardId::A3b016Vaporeon) else {
            panic!("Vaporeon should be a Pokémon");
        };
        let attack = vaporeon.attacks[0].clone();
        let mut state = State::default();
        state.current_player = 0;
        state.turn_count = 3;
        // Pass Hyper Whirlpool as a copied attack used by the Active Fire-type Victini. This
        // isolates Victory Star's generic staging contract; Vaporeon itself is Water-type.
        state.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::B3025Victini));
        state.in_play_pokemon[1][0] = Some(
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Lightning,
            ]),
        );
        let action = Action {
            actor: 0,
            action: SimpleAction::Attack(attack),
            is_stack: false,
        };

        let branches = try_forecast_victory_star_attack(&state, &action)
            .expect("Victini should pause Hyper Whirlpool")
            .into_branches_with_coin_paths();
        assert_eq!(
            branches
                .iter()
                .map(|(probability, _, _)| *probability)
                .collect::<Vec<_>>(),
            vec![0.5, 0.25, 0.125, 0.125],
            "secondary Energy successors must not duplicate public coin classes"
        );

        for (index, (_, mutation, coin_paths)) in branches.into_iter().enumerate() {
            let mut actual_rng = StdRng::seed_from_u64(90 + index as u64);
            let mut expected_rng = actual_rng.clone();
            let expected_flips = coin_paths.sample(&mut expected_rng).unwrap();
            let mut next = state.clone();
            mutation(&mut actual_rng, &mut next, &action);
            assert_eq!(
                next.pending_attack_coin_choice.as_ref().unwrap().flips,
                expected_flips.0
            );
            assert_eq!(
                actual_rng.next_u64(),
                expected_rng.next_u64(),
                "staging must consume RNG only for the publicly exposed coin batch"
            );
            assert_eq!(
                next.get_active(1).attached_energy,
                state.get_active(1).attached_energy
            );
        }
    }

    #[test]
    fn test_apply_evolve() {
        let mut state = State::new(&Deck::default(), &Deck::default());
        let energy = EnergyType::Colorless;
        let mankey = get_card_by_enum(CardId::PA017Mankey);
        let primeape = get_card_by_enum(CardId::A1142Primeape);
        let mut base_played_card = to_playable_card(&mankey, false);
        base_played_card.apply_damage(30); // 30 damage taken
        base_played_card.attached_energy = vec![energy];
        state.in_play_pokemon[0][0] = Some(base_played_card.clone());
        let mut healthy_bench = base_played_card.clone();
        healthy_bench.heal_raw(30);
        healthy_bench.attached_energy = vec![energy, energy, energy];
        state.in_play_pokemon[0][2] = Some(healthy_bench);
        state.hands[0] = vec![primeape.clone(), primeape.clone()];

        // Evolve Active
        apply_evolve(0, &mut state, &primeape, 0, false);
        assert_eq!(
            state.in_play_pokemon[0][0],
            Some(PlayedCard::new(
                primeape.clone(),
                30, // 30 damage counters
                90,
                vec![energy],
                true,
                vec![mankey.clone()]
            ))
        );

        // Evolve Bench
        apply_evolve(0, &mut state, &primeape, 2, false);
        assert_eq!(
            state.in_play_pokemon[0][0],
            Some(PlayedCard::new(
                primeape.clone(),
                30, // 30 damage counters
                90,
                vec![energy],
                true,
                vec![mankey.clone()]
            ))
        );
        assert_eq!(
            state.in_play_pokemon[0][2],
            Some(PlayedCard::new(
                primeape.clone(),
                0, // 0 damage counters
                90,
                vec![energy, energy, energy],
                true,
                vec![mankey.clone()]
            ))
        );
    }

    #[test]
    fn test_forcefully_retreat() {
        let mut state = State::new(&Deck::default(), &Deck::default());
        // PUT Mankey in Active and Primeape in Bench 2
        let mankey = get_card_by_enum(CardId::A1141Mankey);
        let primeape = get_card_by_enum(CardId::A1142Primeape);
        state.in_play_pokemon[0][0] = Some(to_playable_card(&mankey, false));
        state.in_play_pokemon[0][2] = Some(to_playable_card(&primeape, false));

        // Forcefully Activate Primeape
        let mut rng: StdRng = StdRng::seed_from_u64(rand::random());
        let action = Action {
            actor: 0,
            action: SimpleAction::Activate {
                player: 0,
                in_play_idx: 2,
            },
            is_stack: false,
        };
        apply_action(&mut rng, &mut state, &action);

        let mut expected_primeape = to_playable_card(&primeape, false);
        expected_primeape.moved_to_active_this_turn = true;
        assert_eq!(state.in_play_pokemon[0][0], Some(expected_primeape));
        assert_eq!(
            state.in_play_pokemon[0][2],
            Some(to_playable_card(&mankey, false))
        );
    }

    #[test]
    fn test_generate_energy_combinations_all_same_type() {
        // [Grass, Grass, Grass] -> 1 unique combo [Grass, Grass] with count 3
        let energies = vec![EnergyType::Grass, EnergyType::Grass, EnergyType::Grass];
        let combinations = super::generate_energy_combinations(&energies);

        assert_eq!(combinations.len(), 1);
        let (combo, count) = &combinations[0];
        assert_eq!(combo, &vec![EnergyType::Grass, EnergyType::Grass]);
        assert_eq!(*count, 3);
    }

    #[test]
    fn test_generate_energy_combinations_mixed_types() {
        // [Grass, Grass, Fire] -> 2 unique combos:
        // [Grass, Grass] count 1, [Fire, Grass] or [Grass, Fire] count 2
        let energies = vec![EnergyType::Grass, EnergyType::Grass, EnergyType::Fire];
        let combinations = super::generate_energy_combinations(&energies);

        assert_eq!(combinations.len(), 2);

        // Find the mixed Fire-Grass combo (sorted, so could be either order)
        let fire_grass = combinations
            .iter()
            .find(|(combo, _)| {
                combo.len() == 2
                    && combo.contains(&EnergyType::Fire)
                    && combo.contains(&EnergyType::Grass)
                    && combo[0] != combo[1]
            })
            .expect("Should have Fire-Grass combo");
        assert_eq!(fire_grass.1, 2);

        let grass_grass = combinations
            .iter()
            .find(|(combo, _)| combo == &vec![EnergyType::Grass, EnergyType::Grass])
            .expect("Should have Grass-Grass combo");
        assert_eq!(grass_grass.1, 1);
    }

    #[test]
    fn test_generate_energy_combinations_all_different() {
        // [Grass, Fire, Water] -> 3 unique combos, each count 1
        let energies = vec![EnergyType::Grass, EnergyType::Fire, EnergyType::Water];
        let combinations = super::generate_energy_combinations(&energies);

        assert_eq!(combinations.len(), 3); // C(3,2) = 3
        for (_, count) in &combinations {
            assert_eq!(*count, 1);
        }
    }
}
