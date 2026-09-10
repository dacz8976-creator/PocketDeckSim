use rand::{distributions::WeightedIndex, prelude::Distribution, rngs::StdRng, Rng};

use crate::{
    actions::{
        abilities::AbilityMechanic,
        apply_action_helpers::{apply_common_action_prefix, apply_common_action_suffix, Mutation},
        apply_stadium_action::{forecast_coin_stadium_effect, forecast_use_stadium},
        apply_trainer_action::{
            choose_supporter_source, copied_supporter_is_usable, forecast_trainer_action_unchecked,
            penny_candidates, try_copied_supporter_outcomes, try_forecast_trainer_action,
        },
        get_in_play_ability_mechanic,
        outcomes::{CoinPaths, CoinSeq, Outcomes},
        team_rockets_researcher::{
            is_researcher_card, ResearcherPlan, SampledResearcherBatch, UnpricedForecast,
        },
        Action, SimpleAction,
    },
    card_ids::CardId,
    models::{Card, EnergyType, StatusCondition, TrainerCard},
    state::{
        LuxuryCoinDecision, LuxuryCoinResolutionEvent, MistySourceRoute, PendingMistyTargetChoice,
        PendingTrainerCoinChoice, TrainerCoinEffectRoute,
    },
    State,
};

fn luxury_coin_source(state: &State, actor: usize) -> Option<usize> {
    if state.luxury_coin_used_this_turn[actor] {
        return None;
    }
    state
        .enumerate_in_play_pokemon(actor)
        .find_map(|(idx, pokemon)| {
            (get_in_play_ability_mechanic(state, pokemon) == Some(&AbilityMechanic::LuxuryCoin))
                .then_some(idx)
        })
}

fn producer_id(route: &TrainerCoinEffectRoute) -> CardId {
    CardId::from_card_id(&route.effect_trainer().id)
        .expect("a resolved Trainer source must have a known CardId")
}

fn is_misty(id: CardId) -> bool {
    matches!(id, CardId::A1220Misty | CardId::A1267Misty)
}

fn is_master_plan(id: CardId) -> bool {
    matches!(
        id,
        CardId::B4a070TeamRocketsMasterPlan
            | CardId::B4a086TeamRocketsMasterPlan
            | CardId::B4a094TeamRocketsMasterPlan
    )
}

fn is_ice_pop(id: CardId) -> bool {
    id == CardId::B2145LuckyIcePop
}

const REGISTERED_DIRECT_PRODUCERS: [CardId; 19] = [
    CardId::A1220Misty,
    CardId::A1267Misty,
    CardId::A2b072TeamRocketGrunt,
    CardId::A2b091TeamRocketGrunt,
    CardId::A4159Fisher,
    CardId::A4199Fisher,
    CardId::B1215HittingHammer,
    CardId::B2145LuckyIcePop,
    CardId::B2a086ElectricGenerator,
    CardId::B2a131ElectricGenerator,
    CardId::B2a091Arven,
    CardId::B2a108Arven,
    CardId::B2a115Arven,
    CardId::B4145OrderPad,
    CardId::B4a069TeamRocketsResearcher,
    CardId::B4a085TeamRocketsResearcher,
    CardId::B4a070TeamRocketsMasterPlan,
    CardId::B4a086TeamRocketsMasterPlan,
    CardId::B4a094TeamRocketsMasterPlan,
];

fn is_registered_direct_producer(id: CardId) -> bool {
    REGISTERED_DIRECT_PRODUCERS.contains(&id)
}

fn direct_route(trainer: &TrainerCard) -> Option<TrainerCoinEffectRoute> {
    let id = CardId::from_card_id(&trainer.id)?;
    is_registered_direct_producer(id).then(|| TrainerCoinEffectRoute::Direct {
        trainer: trainer.clone(),
    })
}

fn stadium_route(state: &State) -> Option<TrainerCoinEffectRoute> {
    let Card::Trainer(stadium) = state.active_stadium.as_ref()? else {
        return None;
    };
    matches!(
        CardId::from_card_id(&stadium.id),
        Some(CardId::B2a093Mesagoza | CardId::B4a072Arcade)
    )
    .then(|| TrainerCoinEffectRoute::Stadium {
        stadium: stadium.clone(),
        played_by: state.active_stadium_owner,
    })
}

fn effect_outcomes(
    route: &TrainerCoinEffectRoute,
    state: &State,
    actor: usize,
) -> Result<Outcomes, UnpricedForecast> {
    let trainer = route.effect_trainer();
    let id = producer_id(route);
    if is_researcher_card(trainer) {
        return ResearcherPlan::from_state(state, actor).forecast_exact(actor);
    }
    if is_misty(id) {
        return Err(UnpricedForecast::observable_geometric(trainer.id.clone()));
    }
    if is_master_plan(id) {
        return Ok(Outcomes::binary_coin(
            Box::new(|_, _, _| {}),
            Box::new(|_, state, action| {
                state.apply_status_condition(action.actor, 0, StatusCondition::Confused);
            }),
        ));
    }
    if is_ice_pop(id) {
        return Ok(Outcomes::binary_coin(
            Box::new(|_, state, action| {
                let card = match &action.action {
                    SimpleAction::Play { trainer_card } => Card::Trainer(trainer_card.clone()),
                    _ => panic!("Lucky Ice Pop must retain its original Play action"),
                };
                let pos = state.discard_piles[action.actor]
                    .iter()
                    .position(|candidate| candidate == &card)
                    .expect("the staged Lucky Ice Pop must already be in the discard pile");
                state.discard_piles[action.actor].remove(pos);
                state.hands[action.actor].push(card);
            }),
            Box::new(|_, _, _| {}),
        ));
    }
    match route {
        TrainerCoinEffectRoute::Stadium { .. } => forecast_coin_stadium_effect(state, actor)
            .ok_or_else(|| UnpricedForecast::unsupported_trainer_coin(trainer.id.clone())),
        TrainerCoinEffectRoute::Direct { .. } | TrainerCoinEffectRoute::Penny { .. } => {
            Ok(forecast_trainer_action_unchecked(actor, state, trainer))
        }
    }
}

fn apply_pre_coin_prefix(
    state: &mut State,
    action: &Action,
    route: &TrainerCoinEffectRoute,
) -> bool {
    let id = producer_id(route);
    if is_master_plan(id) {
        state.apply_status_condition(1 - action.actor, 0, StatusCondition::Confused);
    }
    if is_ice_pop(id) {
        return state.heal_pokemon(action.actor, 0, 20) > 0;
    }
    true
}

fn ice_pop_can_heal(state: &State, actor: usize) -> bool {
    !state.is_healing_blocked()
        && state
            .maybe_get_active(actor)
            .is_some_and(|active| active.get_damage_counters() > 0)
}

fn apply_route_suffix(rng: &mut StdRng, state: &mut State, route: &TrainerCoinEffectRoute) {
    if let TrainerCoinEffectRoute::Penny { shuffle_owner, .. } = route {
        state.decks[*shuffle_owner].shuffle(false, rng);
    }
}

fn start_action(state: &mut State, action: &Action, route: &TrainerCoinEffectRoute) -> bool {
    apply_common_action_prefix(state, action);
    if matches!(route, TrainerCoinEffectRoute::Stadium { .. }) {
        state.has_used_stadium[action.actor] = true;
    }
    apply_pre_coin_prefix(state, action, route)
}

fn pending_for(
    action: &Action,
    route: TrainerCoinEffectRoute,
    flips: Vec<bool>,
    source_idx: usize,
) -> PendingTrainerCoinChoice {
    PendingTrainerCoinChoice {
        actor: action.actor,
        original_action: action.action.clone(),
        original_is_stack: action.is_stack,
        flips,
        luxury_coin_in_play_idx: source_idx,
        misty_target_in_play_idx: None,
        route: Some(route),
    }
}

fn misty_route_for_action(action: &Action, misty: TrainerCard) -> MistySourceRoute {
    match &action.action {
        SimpleAction::Play { trainer_card } if trainer_card.name == "Misty" => {
            MistySourceRoute::Direct { misty }
        }
        SimpleAction::Play { trainer_card } if trainer_card.name == "Penny" => {
            MistySourceRoute::Penny {
                penny: trainer_card.clone(),
                misty,
                shuffle_owner: 1 - action.actor,
            }
        }
        SimpleAction::UseAbility { .. } => MistySourceRoute::Portrait { misty },
        _ => panic!("Misty target staging requires direct Play, Penny, or Portrait"),
    }
}

/// Start the public target phase after the outer Play/Ability prefix has been paid.
pub(crate) fn stage_misty_target(state: &mut State, action: &Action, misty: TrainerCard) {
    let choices = state
        .enumerate_in_play_pokemon(action.actor)
        .filter(|(_, pokemon)| state.pokemon_is_type(pokemon, EnergyType::Water))
        .map(|(in_play_idx, _)| SimpleAction::ChooseMistyTarget { in_play_idx })
        .collect::<Vec<_>>();
    assert!(!choices.is_empty(), "Misty requires a Water Pokemon target");
    state.pending_misty_target_choice = Some(PendingMistyTargetChoice {
        actor: action.actor,
        original_action: action.action.clone(),
        original_is_stack: action.is_stack,
        route: Some(misty_route_for_action(action, misty)),
    });
    state.move_generation_stack.push((action.actor, choices));
}

/// Penny's shuffle belongs to the copied effect's final commit. When the copied effect is Misty,
/// retain that evidence privately and leave the public target frame active.
pub(crate) fn defer_penny_shuffle_for_misty(
    state: &mut State,
    penny: &TrainerCard,
    shuffle_owner: usize,
) -> bool {
    let Some(pending) = state.pending_misty_target_choice.as_mut() else {
        return false;
    };
    let route = pending
        .route
        .take()
        .expect("a referee Misty target state must retain its source route");
    pending.route = Some(match route {
        MistySourceRoute::Portrait { misty } => MistySourceRoute::PortraitPenny {
            penny: penny.clone(),
            misty,
            shuffle_owner,
        },
        route @ MistySourceRoute::Penny { .. } => route,
        other => panic!("Penny cannot wrap this Misty route: {other:?}"),
    });
    true
}

fn original_misty_action(pending: &PendingMistyTargetChoice) -> Action {
    Action {
        actor: pending.actor,
        action: pending.original_action.clone(),
        is_stack: pending.original_is_stack,
    }
}

fn validate_misty_target(
    state: &State,
    action: &Action,
) -> (PendingMistyTargetChoice, MistySourceRoute, usize) {
    let pending = state
        .pending_misty_target_choice
        .clone()
        .expect("Misty target choice requires pending data");
    let SimpleAction::ChooseMistyTarget { in_play_idx } = action.action else {
        panic!("expected a Misty target choice")
    };
    assert!(
        action.is_stack,
        "Misty target choice must be a stack action"
    );
    assert_eq!(action.actor, pending.actor, "Misty target actor mismatch");
    let (frame_actor, choices) = state
        .move_generation_stack
        .last()
        .expect("Misty target stack frame missing");
    assert_eq!(
        *frame_actor, pending.actor,
        "Misty target frame actor mismatch"
    );
    assert!(
        !choices.is_empty()
            && choices
                .iter()
                .all(|choice| matches!(choice, SimpleAction::ChooseMistyTarget { .. })),
        "Misty target frame must contain only target choices"
    );
    assert!(
        choices.contains(&action.action),
        "chosen Misty target was not offered"
    );
    let pokemon = state.in_play_pokemon[action.actor][in_play_idx]
        .as_ref()
        .expect("chosen Misty target is no longer in play");
    assert!(
        state.pokemon_is_type(pokemon, EnergyType::Water),
        "chosen Misty target is no longer Water"
    );
    let route = pending
        .route
        .clone()
        .expect("a referee Misty target state must retain its source route");
    (pending, route, in_play_idx)
}

fn misty_trainer_route(route: &MistySourceRoute) -> TrainerCoinEffectRoute {
    match route {
        MistySourceRoute::Direct { misty } => TrainerCoinEffectRoute::Direct {
            trainer: misty.clone(),
        },
        MistySourceRoute::Penny {
            misty,
            shuffle_owner,
            ..
        } => TrainerCoinEffectRoute::Penny {
            copied: misty.clone(),
            shuffle_owner: *shuffle_owner,
        },
        MistySourceRoute::Portrait { .. } | MistySourceRoute::PortraitPenny { .. } => {
            panic!("Portrait cannot activate Luxury Coin")
        }
    }
}

fn pop_misty_target_frame(state: &mut State, pending: &PendingMistyTargetChoice) {
    assert_eq!(state.pending_misty_target_choice.as_ref(), Some(pending));
    let (_, choices) = state
        .move_generation_stack
        .last()
        .expect("Misty target stack frame missing");
    assert!(
        !choices.is_empty()
            && choices
                .iter()
                .all(|choice| matches!(choice, SimpleAction::ChooseMistyTarget { .. })),
        "Misty target frame must contain only target choices"
    );
    state.move_generation_stack.pop();
    state.pending_misty_target_choice = None;
}

/// Physical target commit. The target is fixed before any coin or Will consumption.
pub(crate) fn sample_misty_target_actual(
    rng: &mut StdRng,
    state: &State,
    action: &Action,
) -> Mutation {
    let (pending, route, target) = validate_misty_target(state, action);
    let force_first = state.has_pending_will_first_heads();
    let batch = sample_until_tails(rng, force_first);
    let ghold = route
        .outer_is_trainer()
        .then(|| luxury_coin_source(state, action.actor))
        .flatten();
    let actor = action.actor;
    Box::new(move |rng, state, _| {
        pop_misty_target_frame(state, &pending);
        if force_first {
            assert!(state.consume_pending_will_first_heads());
        }
        if let Some(source_idx) = ghold {
            let original = original_misty_action(&pending);
            let mut trainer_pending = pending_for(
                &original,
                misty_trainer_route(&route),
                batch.0.clone(),
                source_idx,
            );
            trainer_pending.misty_target_in_play_idx = Some(target);
            install_pending(state, trainer_pending);
            return;
        }
        let heads = u32::try_from(batch.0.iter().filter(|face| **face).count())
            .expect("Misty heads count exceeds the attachment representation");
        if heads > 0 {
            state.attach_energy_from_zone(actor, target, EnergyType::Water, heads, false);
        }
        if let Some(owner) = route.penny_shuffle_owner() {
            state.decks[owner].shuffle(false, rng);
        }
        apply_common_action_suffix(state, &original_misty_action(&pending));
    })
}

/// Search can enumerate the finite target phase, then records the infinite public batch as
/// explicitly unpriced rather than sampling into an exact forecast.
pub(crate) fn forecast_misty_target(
    state: &State,
    action: &Action,
) -> Result<Outcomes, UnpricedForecast> {
    let (_, route, _) = validate_misty_target(state, action);
    Err(UnpricedForecast::observable_geometric(
        route.effect_trainer().id.clone(),
    ))
}

fn install_pending(state: &mut State, pending: PendingTrainerCoinChoice) {
    let actor = pending.actor;
    let source = pending.luxury_coin_in_play_idx;
    state.pending_trainer_coin_choice = Some(pending);
    state.move_generation_stack.push((
        actor,
        vec![
            SimpleAction::KeepTrainerCoinResults,
            SimpleAction::RerollTrainerCoins {
                luxury_coin_in_play_idx: source,
            },
        ],
    ));
}

fn sample_mutation(rng: &mut StdRng, outcomes: Outcomes) -> Mutation {
    let (probabilities, mut mutations) = outcomes.into_branches();
    let selected = if probabilities.len() == 1 {
        0
    } else {
        WeightedIndex::new(&probabilities)
            .expect("Trainer forecast probabilities must be valid")
            .sample(rng)
    };
    mutations.remove(selected)
}

fn sample_batch_from_outcomes(
    rng: &mut StdRng,
    mut outcomes: Outcomes,
    force_first: bool,
) -> Result<Option<CoinSeq>, Mutation> {
    if force_first {
        outcomes = match outcomes.force_first_heads_preserving_noncoin_mass() {
            Ok(forced) => forced,
            Err(original) => original,
        };
    }
    enum MarginalBatch {
        Exact(CoinSeq),
        Symbolic(CoinPaths),
        Completed(Mutation),
    }
    let mut options: Vec<(f64, MarginalBatch)> = Vec::new();
    for (probability, mutation, paths) in outcomes.into_branches_with_coin_paths() {
        match paths {
            CoinPaths::None => options.push((probability, MarginalBatch::Completed(mutation))),
            CoinPaths::Exact(paths) => {
                let each = probability / paths.len() as f64;
                for path in paths {
                    if let Some((weight, _)) = options.iter_mut().find(|(_, option)| {
                        matches!(option, MarginalBatch::Exact(existing) if existing == &path)
                    }) {
                        *weight += each;
                    } else {
                        options.push((each, MarginalBatch::Exact(path)));
                    }
                }
            }
            symbolic @ CoinPaths::UntilTailsAtLeast { .. } => {
                options.push((probability, MarginalBatch::Symbolic(symbolic)));
            }
        }
    }
    let probabilities = options
        .iter()
        .map(|(probability, _)| *probability)
        .collect::<Vec<_>>();
    let selected = if options.len() == 1 {
        0
    } else {
        WeightedIndex::new(&probabilities)
            .expect("Trainer forecast probabilities must be valid")
            .sample(rng)
    };
    match options.swap_remove(selected).1 {
        MarginalBatch::Exact(flips) => Ok(Some(flips)),
        MarginalBatch::Symbolic(paths) => Ok(paths.sample(rng)),
        MarginalBatch::Completed(mutation) => Err(mutation),
    }
}

fn marginal_exact_coin_sequences(
    outcomes: Outcomes,
) -> Result<(Vec<(f64, CoinSeq)>, Vec<(f64, Mutation)>), ()> {
    let mut coin_batches: Vec<(f64, CoinSeq)> = Vec::new();
    let mut completed = Vec::new();
    for (probability, mutation, paths) in outcomes.into_branches_with_coin_paths() {
        match paths {
            CoinPaths::None => completed.push((probability, mutation)),
            CoinPaths::Exact(paths) => {
                let each = probability / paths.len() as f64;
                for path in paths {
                    if let Some((weight, _)) = coin_batches
                        .iter_mut()
                        .find(|(_, existing)| existing == &path)
                    {
                        *weight += each;
                    } else {
                        coin_batches.push((each, path));
                    }
                }
            }
            CoinPaths::UntilTailsAtLeast { .. } => return Err(()),
        }
    }
    Ok((coin_batches, completed))
}

fn sample_until_tails(rng: &mut impl Rng, force_first: bool) -> CoinSeq {
    let mut flips = Vec::new();
    if force_first {
        flips.push(true);
    }
    while rng.gen_bool(0.5) {
        flips.push(true);
    }
    flips.push(false);
    CoinSeq(flips)
}

fn stage_actual_route(
    rng: &mut StdRng,
    state: &State,
    action: &Action,
    route: TrainerCoinEffectRoute,
    source_idx: usize,
) -> Result<Mutation, UnpricedForecast> {
    let force_first = state.has_pending_will_first_heads();
    let id = producer_id(&route);
    if is_misty(id) {
        let misty = route.effect_trainer().clone();
        let route_for_start = route.clone();
        return Ok(Box::new(move |_, state, original| {
            assert!(start_action(state, original, &route_for_start));
            stage_misty_target(state, original, misty.clone());
        }));
    }
    if is_ice_pop(id) && !ice_pop_can_heal(state, action.actor) {
        let original = action.clone();
        return Ok(Box::new(move |_, state, _| {
            apply_common_action_prefix(state, &original);
            state.heal_pokemon(original.actor, 0, 20);
            apply_common_action_suffix(state, &original);
        }));
    }
    let batch = if is_researcher_card(route.effect_trainer()) {
        ResearcherPlan::from_state(state, action.actor)
            .sample_batch(rng, force_first)
            .flips
    } else {
        match sample_batch_from_outcomes(
            rng,
            effect_outcomes(&route, state, action.actor)?,
            force_first,
        ) {
            Ok(Some(batch)) => batch,
            Ok(None) => unreachable!(),
            Err(completed) => {
                let original = action.clone();
                return Ok(Box::new(move |rng, state, _| {
                    apply_common_action_prefix(state, &original);
                    completed(rng, state, &original);
                    apply_route_suffix(rng, state, &route);
                    apply_common_action_suffix(state, &original);
                }));
            }
        }
    };
    let pending = pending_for(action, route.clone(), batch.0, source_idx);
    Ok(Box::new(move |_, state, original| {
        if !start_action(state, original, &route) {
            return;
        }
        if force_first {
            assert!(state.consume_pending_will_first_heads());
        }
        install_pending(state, pending.clone());
    }))
}

/// Physical-game entry. Source selection and the complete batch use only the gameplay RNG.
pub(crate) fn try_sample_entry_actual(
    rng: &mut StdRng,
    state: &State,
    action: &Action,
) -> Option<Mutation> {
    let source_idx = luxury_coin_source(state, action.actor)?;
    let route = match &action.action {
        SimpleAction::Play { trainer_card } if trainer_card.name == "Penny" => {
            let candidates = penny_candidates(state, 1 - action.actor);
            let Some(copied) = choose_supporter_source(rng, &candidates) else {
                let original = action.clone();
                return Some(Box::new(move |_, state, _| {
                    apply_common_action_prefix(state, &original);
                    apply_common_action_suffix(state, &original);
                }));
            };
            TrainerCoinEffectRoute::Penny {
                copied,
                shuffle_owner: 1 - action.actor,
            }
        }
        SimpleAction::Play { trainer_card } => match direct_route(trainer_card) {
            Some(route) => route,
            None => {
                let probe = try_forecast_trainer_action(action.actor, state, trainer_card)
                    .unwrap_or_else(|error| panic!("Trainer forecast refused: {}", error.reason));
                if probe.has_any_coin_paths() {
                    panic!(
                        "{}",
                        UnpricedForecast::unsupported_trainer_coin(trainer_card.id.clone()).reason
                    );
                }
                return None;
            }
        },
        SimpleAction::UseStadium => match stadium_route(state) {
            Some(route) => route,
            None => {
                if forecast_use_stadium(state, action.actor).has_any_coin_paths() {
                    let id = state
                        .active_stadium
                        .as_ref()
                        .map(Card::get_id)
                        .unwrap_or_else(|| "unknown Stadium".into());
                    panic!("{}", UnpricedForecast::unsupported_trainer_coin(id).reason);
                }
                return None;
            }
        },
        _ => return None,
    };

    if matches!(route, TrainerCoinEffectRoute::Penny { .. })
        && !copied_supporter_is_usable(state, route.effect_trainer())
    {
        let original = action.clone();
        return Some(Box::new(move |rng, state, _| {
            apply_common_action_prefix(state, &original);
            apply_route_suffix(rng, state, &route);
            apply_common_action_suffix(state, &original);
        }));
    }

    if matches!(route, TrainerCoinEffectRoute::Penny { .. })
        && !is_registered_direct_producer(producer_id(&route))
    {
        let copied = try_copied_supporter_outcomes(action.actor, state, route.effect_trainer())
            .unwrap_or_else(|error| {
                panic!("exact copied Supporter forecast refused: {}", error.reason)
            });
        if copied.has_any_coin_paths() {
            panic!(
                "{}",
                UnpricedForecast::unsupported_trainer_coin(route.effect_trainer().id.clone())
                    .reason
            );
        }
        let original = action.clone();
        return Some(Box::new(move |rng, state, _| {
            apply_common_action_prefix(state, &original);
            sample_mutation(rng, copied)(rng, state, &original);
            apply_route_suffix(rng, state, &route);
            apply_common_action_suffix(state, &original);
        }));
    }

    Some(
        stage_actual_route(rng, state, action, route, source_idx)
            .unwrap_or_else(|error| panic!("actual Luxury Coin staging failed: {}", error.reason)),
    )
}

fn search_stage_route(
    state: &State,
    action: &Action,
    route: TrainerCoinEffectRoute,
    source_idx: usize,
) -> Result<Outcomes, UnpricedForecast> {
    let id = producer_id(&route);
    if is_misty(id) {
        let misty = route.effect_trainer().clone();
        let route_for_start = route.clone();
        return Ok(Outcomes::single_fn(move |_, state, original| {
            assert!(start_action(state, original, &route_for_start));
            stage_misty_target(state, original, misty.clone());
        }));
    }
    if is_ice_pop(id) && !ice_pop_can_heal(state, action.actor) {
        let original = action.clone();
        return Ok(Outcomes::single_fn(move |_, state, _| {
            apply_common_action_prefix(state, &original);
            state.heal_pokemon(original.actor, 0, 20);
            apply_common_action_suffix(state, &original);
        }));
    }
    if is_researcher_card(route.effect_trainer()) {
        return Err(UnpricedForecast::observable_geometric(
            route.effect_trainer().id.clone(),
        ));
    }
    let mut outcomes = effect_outcomes(&route, state, action.actor)?;
    if outcomes.has_symbolic_coin_paths() {
        return Err(UnpricedForecast::observable_geometric(
            route.effect_trainer().id.clone(),
        ));
    }
    let force_first = state.has_pending_will_first_heads();
    if force_first {
        outcomes = match outcomes.force_first_heads_preserving_noncoin_mass() {
            Ok(forced) => forced,
            Err(original) => original,
        };
    }
    let (coin_batches, completed) = marginal_exact_coin_sequences(outcomes)
        .map_err(|_| UnpricedForecast::observable_geometric(route.effect_trainer().id.clone()))?;
    let mut expanded = Vec::new();
    for (probability, mutation) in completed {
        let original = action.clone();
        let route = route.clone();
        let completed: Mutation = Box::new(move |rng, state, _| {
            apply_common_action_prefix(state, &original);
            mutation(rng, state, &original);
            apply_route_suffix(rng, state, &route);
            apply_common_action_suffix(state, &original);
        });
        expanded.push((probability, completed, CoinPaths::None));
    }
    for (probability, path) in coin_batches {
        let pending = pending_for(action, route.clone(), path.0.clone(), source_idx);
        let route = route.clone();
        let staged_path = path.clone();
        let stage: Mutation = Box::new(move |_, state, original| {
            assert!(start_action(state, original, &route));
            if force_first {
                assert!(state.consume_pending_will_first_heads());
            }
            install_pending(state, pending.clone());
        });
        expanded.push((probability, stage, CoinPaths::Exact(vec![staged_path])));
    }
    Outcomes::from_branches_with_coin_paths(expanded)
        .map_err(|_| UnpricedForecast::unsupported_trainer_coin(route.effect_trainer().id.clone()))
}

fn search_penny_entry(
    state: &State,
    action: &Action,
    source_idx: usize,
    penny: &TrainerCard,
) -> Result<Outcomes, UnpricedForecast> {
    let candidates = penny_candidates(state, 1 - action.actor);
    let total = candidates.iter().map(|(_, count)| *count).sum::<usize>();
    if total == 0 {
        let original = action.clone();
        return Ok(Outcomes::single_fn(move |_, state, _| {
            apply_common_action_prefix(state, &original);
            apply_common_action_suffix(state, &original);
        }));
    }
    let mut combined = Vec::new();
    for (copied, count) in candidates {
        let weight = count as f64 / total as f64;
        let route = TrainerCoinEffectRoute::Penny {
            copied: copied.clone(),
            shuffle_owner: 1 - action.actor,
        };
        if !copied_supporter_is_usable(state, &copied) {
            let original = action.clone();
            let route = route.clone();
            let completed: Mutation = Box::new(move |rng, state, _| {
                apply_common_action_prefix(state, &original);
                apply_route_suffix(rng, state, &route);
                apply_common_action_suffix(state, &original);
            });
            combined.push((weight, completed, CoinPaths::None));
            continue;
        }
        if is_registered_direct_producer(producer_id(&route)) {
            let staged = search_stage_route(state, action, route, source_idx)?;
            for (probability, mutation, paths) in staged.into_branches_with_coin_paths() {
                combined.push((weight * probability, mutation, paths));
            }
        } else {
            let copied_outcomes = try_copied_supporter_outcomes(action.actor, state, &copied)?;
            if copied_outcomes.has_any_coin_paths() {
                return Err(UnpricedForecast::unsupported_trainer_coin(copied.id));
            }
            for (probability, mutation, paths) in copied_outcomes.into_branches_with_coin_paths() {
                let original = action.clone();
                let route = route.clone();
                let completed: Mutation = Box::new(move |rng, state, _| {
                    apply_common_action_prefix(state, &original);
                    mutation(rng, state, &original);
                    apply_route_suffix(rng, state, &route);
                    apply_common_action_suffix(state, &original);
                });
                combined.push((weight * probability, completed, paths));
            }
        }
    }
    let _ = penny;
    Outcomes::from_branches_with_coin_paths(combined)
        .map_err(|_| UnpricedForecast::unsupported_trainer_coin("Penny mixed source distribution"))
}

/// Exact search entry. Finite public batches are enumerated face-for-face; symbolic public
/// geometric batches return a structured unpriced boundary.
pub(crate) fn try_forecast_entry(
    state: &State,
    action: &Action,
) -> Result<Option<Outcomes>, UnpricedForecast> {
    let Some(source_idx) = luxury_coin_source(state, action.actor) else {
        return Ok(None);
    };
    match &action.action {
        SimpleAction::Play { trainer_card } if trainer_card.name == "Penny" => {
            search_penny_entry(state, action, source_idx, trainer_card).map(Some)
        }
        SimpleAction::Play { trainer_card } => {
            let Some(route) = direct_route(trainer_card) else {
                let probe = try_forecast_trainer_action(action.actor, state, trainer_card)?;
                if probe.has_any_coin_paths() {
                    return Err(UnpricedForecast::unsupported_trainer_coin(
                        trainer_card.id.clone(),
                    ));
                }
                return Ok(None);
            };
            search_stage_route(state, action, route, source_idx).map(Some)
        }
        SimpleAction::UseStadium => {
            let Some(route) = stadium_route(state) else {
                if forecast_use_stadium(state, action.actor).has_any_coin_paths() {
                    let id = state
                        .active_stadium
                        .as_ref()
                        .map(Card::get_id)
                        .unwrap_or_else(|| "unknown Stadium".into());
                    return Err(UnpricedForecast::unsupported_trainer_coin(id));
                }
                return Ok(None);
            };
            search_stage_route(state, action, route, source_idx).map(Some)
        }
        _ => Ok(None),
    }
}

fn original_action(pending: &PendingTrainerCoinChoice) -> Action {
    Action {
        actor: pending.actor,
        action: pending.original_action.clone(),
        is_stack: pending.original_is_stack,
    }
}

fn validate_choice(
    state: &State,
    action: &Action,
) -> (PendingTrainerCoinChoice, TrainerCoinEffectRoute) {
    let pending = state
        .pending_trainer_coin_choice
        .clone()
        .expect("Luxury Coin choice requires pending Trainer coin data");
    assert!(action.is_stack, "Luxury Coin choice must be a stack action");
    assert_eq!(
        action.actor, pending.actor,
        "Luxury Coin choice actor mismatch"
    );
    let source = state.in_play_pokemon[pending.actor][pending.luxury_coin_in_play_idx]
        .as_ref()
        .expect("stored Luxury Coin source is no longer in play");
    assert_eq!(
        get_in_play_ability_mechanic(state, source),
        Some(&AbilityMechanic::LuxuryCoin),
        "stored Luxury Coin source is suppressed or no longer has the Ability"
    );
    if matches!(action.action, SimpleAction::RerollTrainerCoins { .. }) {
        assert!(
            !state.luxury_coin_used_this_turn[pending.actor],
            "Luxury Coin was already used this turn"
        );
    }
    let route = pending
        .route
        .clone()
        .expect("a referee Luxury Coin state must retain its resolved Trainer route");
    (pending, route)
}

fn conditioned_keep(
    state: &State,
    pending: &PendingTrainerCoinChoice,
    route: &TrainerCoinEffectRoute,
) -> Result<Outcomes, UnpricedForecast> {
    let id = producer_id(route);
    let heads = pending.flips.iter().filter(|face| **face).count();
    if is_researcher_card(route.effect_trainer()) {
        return ResearcherPlan::from_state(state, pending.actor)
            .forecast_heads(pending.actor, heads);
    }
    if is_misty(id) {
        let heads =
            u32::try_from(heads).expect("Misty heads count exceeds the attachment representation");
        let target = pending
            .misty_target_in_play_idx
            .expect("a staged Misty Luxury Coin choice must retain its fixed target");
        return Ok(Outcomes::single_fn(move |_, state, action| {
            if heads > 0 {
                state.attach_energy_from_zone(
                    action.actor,
                    target,
                    EnergyType::Water,
                    heads,
                    false,
                );
            }
        }));
    }
    effect_outcomes(route, state, pending.actor)?
        .condition_on_coin_sequence(&CoinSeq(pending.flips.clone()))
        .map_err(|_| UnpricedForecast::unsupported_trainer_coin(route.effect_trainer().id.clone()))
}

fn commit_mutation(
    pending: PendingTrainerCoinChoice,
    route: TrainerCoinEffectRoute,
    effect: Mutation,
    decision: LuxuryCoinDecision,
    replacement_faces: Option<Vec<bool>>,
) -> Mutation {
    Box::new(move |rng, state, _choice| {
        assert_eq!(state.pending_trainer_coin_choice.as_ref(), Some(&pending));
        let (_, choices) = state
            .move_generation_stack
            .last()
            .expect("Luxury Coin choice stack frame missing");
        assert_eq!(choices.len(), 2, "Luxury Coin frame must have two actions");
        state.move_generation_stack.pop();
        state.pending_trainer_coin_choice = None;
        if decision == LuxuryCoinDecision::Reroll {
            state.luxury_coin_used_this_turn[pending.actor] = true;
        }
        let original = original_action(&pending);
        effect(rng, state, &original);
        apply_route_suffix(rng, state, &route);
        apply_common_action_suffix(state, &original);
        state
            .luxury_coin_resolution_events
            .push(LuxuryCoinResolutionEvent {
                actor: pending.actor,
                initial_faces: pending.flips.clone(),
                decision,
                replacement_faces: replacement_faces.clone(),
            });
    })
}

pub(crate) fn try_forecast_choice(
    state: &State,
    action: &Action,
) -> Result<Outcomes, UnpricedForecast> {
    let (pending, route) = validate_choice(state, action);
    match &action.action {
        SimpleAction::KeepTrainerCoinResults => {
            let outcomes = conditioned_keep(state, &pending, &route)?;
            Ok(outcomes.map_mutations(|effect| {
                commit_mutation(
                    pending.clone(),
                    route.clone(),
                    effect,
                    LuxuryCoinDecision::Keep,
                    None,
                )
            }))
        }
        SimpleAction::RerollTrainerCoins {
            luxury_coin_in_play_idx,
        } => {
            assert_eq!(*luxury_coin_in_play_idx, pending.luxury_coin_in_play_idx);
            assert!(!state.luxury_coin_used_this_turn[pending.actor]);
            let id = producer_id(&route);
            if is_misty(id) || is_researcher_card(route.effect_trainer()) {
                return Err(UnpricedForecast::observable_geometric(
                    route.effect_trainer().id.clone(),
                ));
            }
            let fresh = effect_outcomes(&route, state, pending.actor)?;
            if fresh.has_symbolic_coin_paths() {
                return Err(UnpricedForecast::observable_geometric(
                    route.effect_trainer().id.clone(),
                ));
            }
            let (replacement_batches, completed) =
                marginal_exact_coin_sequences(fresh).map_err(|_| {
                    UnpricedForecast::observable_geometric(route.effect_trainer().id.clone())
                })?;
            if !completed.is_empty() {
                return Err(UnpricedForecast::unsupported_trainer_coin(
                    route.effect_trainer().id.clone(),
                ));
            }
            let mut branches = Vec::new();
            for (probability, path) in replacement_batches {
                let selected = effect_outcomes(&route, state, pending.actor)?
                    .condition_on_coin_sequence(&path)
                    .map_err(|_| {
                        UnpricedForecast::unsupported_trainer_coin(
                            route.effect_trainer().id.clone(),
                        )
                    })?;
                for (conditional, effect, _) in selected.into_branches_with_coin_paths() {
                    branches.push((
                        probability * conditional,
                        commit_mutation(
                            pending.clone(),
                            route.clone(),
                            effect,
                            LuxuryCoinDecision::Reroll,
                            Some(path.0.clone()),
                        ),
                        CoinPaths::None,
                    ));
                }
            }
            Outcomes::from_branches_with_coin_paths(branches).map_err(|_| {
                UnpricedForecast::unsupported_trainer_coin(route.effect_trainer().id.clone())
            })
        }
        _ => unreachable!("only Luxury Coin choices reach this function"),
    }
}

/// Physical Keep/Reroll path. It never calls an exact whole-distribution API for Misty or
/// Researcher, so an unpriced search boundary cannot block real play.
pub(crate) fn sample_choice_actual(rng: &mut StdRng, state: &State, action: &Action) -> Mutation {
    let (pending, route) = validate_choice(state, action);
    match &action.action {
        SimpleAction::KeepTrainerCoinResults => {
            let effect: Mutation = if is_researcher_card(route.effect_trainer()) {
                let plan = ResearcherPlan::from_state(state, pending.actor);
                let batch = SampledResearcherBatch {
                    flips: CoinSeq(pending.flips.clone()),
                };
                let actor = pending.actor;
                Box::new(move |rng, state, _| plan.apply_sampled(&batch, rng, state, actor))
            } else {
                sample_mutation(
                    rng,
                    conditioned_keep(state, &pending, &route).unwrap_or_else(|error| {
                        panic!("Luxury Coin Keep failed: {}", error.reason)
                    }),
                )
            };
            commit_mutation(pending, route, effect, LuxuryCoinDecision::Keep, None)
        }
        SimpleAction::RerollTrainerCoins {
            luxury_coin_in_play_idx,
        } => {
            assert_eq!(*luxury_coin_in_play_idx, pending.luxury_coin_in_play_idx);
            let id = producer_id(&route);
            let replacement = if is_researcher_card(route.effect_trainer()) {
                ResearcherPlan::from_state(state, pending.actor)
                    .sample_batch(rng, false)
                    .flips
            } else if is_misty(id) {
                sample_until_tails(rng, false)
            } else {
                sample_batch_from_outcomes(
                    rng,
                    effect_outcomes(&route, state, pending.actor).unwrap_or_else(|error| {
                        panic!("Luxury Coin Reroll failed: {}", error.reason)
                    }),
                    false,
                )
                .unwrap_or_else(|_| panic!("registered Luxury Coin producer lost its coin batch"))
                .expect("registered Luxury Coin producer must expose coin paths")
            };
            let effect: Mutation = if is_researcher_card(route.effect_trainer()) {
                let plan = ResearcherPlan::from_state(state, pending.actor);
                let batch = SampledResearcherBatch {
                    flips: replacement.clone(),
                };
                let actor = pending.actor;
                Box::new(move |rng, state, _| plan.apply_sampled(&batch, rng, state, actor))
            } else {
                let replacement_pending = PendingTrainerCoinChoice {
                    flips: replacement.0.clone(),
                    ..pending.clone()
                };
                sample_mutation(
                    rng,
                    conditioned_keep(state, &replacement_pending, &route).unwrap_or_else(|error| {
                        panic!("Luxury Coin replacement failed: {}", error.reason)
                    }),
                )
            };
            commit_mutation(
                pending,
                route,
                effect,
                LuxuryCoinDecision::Reroll,
                Some(replacement.0),
            )
        }
        _ => unreachable!(),
    }
}

#[cfg(test)]
mod tests {
    use rand::{RngCore, SeedableRng};

    use super::*;
    use crate::{database::get_card_by_enum, models::PlayedCard};

    #[test]
    fn registered_producer_census_drives_the_actual_route_guard() {
        assert_eq!(REGISTERED_DIRECT_PRODUCERS.len(), 19);
        for id in REGISTERED_DIRECT_PRODUCERS {
            assert!(is_registered_direct_producer(id), "missing {id:?}");
        }
        assert!(!is_registered_direct_producer(CardId::PA001Potion));
    }

    #[test]
    fn sampling_public_faces_does_not_consume_hidden_suffix_selection() {
        fn no_op() -> Mutation {
            Box::new(|_, _, _| {})
        }

        for seed in 0..128 {
            // Interleaving the two heads branches makes sampling the full effect branch first
            // observably diverge from sampling the marginal public batch.
            let split = Outcomes::from_branches_with_coin_paths(vec![
                (0.25, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
                (0.50, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![false])])),
                (0.25, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
            ])
            .unwrap();
            let collapsed = Outcomes::from_branches_with_coin_paths(vec![
                (0.50, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
                (0.50, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![false])])),
            ])
            .unwrap();
            let mut split_rng = StdRng::seed_from_u64(seed);
            let mut collapsed_rng = split_rng.clone();

            let split_batch = match sample_batch_from_outcomes(&mut split_rng, split, false) {
                Ok(batch) => batch,
                Err(_) => panic!("split fixture must expose a coin batch"),
            };
            let collapsed_batch =
                match sample_batch_from_outcomes(&mut collapsed_rng, collapsed, false) {
                    Ok(batch) => batch,
                    Err(_) => panic!("collapsed fixture must expose a coin batch"),
                };
            assert_eq!(split_batch, collapsed_batch, "seed {seed}");
            assert_eq!(
                split_rng.next_u64(),
                collapsed_rng.next_u64(),
                "seed {seed}"
            );
        }
    }

    #[test]
    fn search_marginalizes_duplicate_faces_before_staging_or_reroll_conditioning() {
        fn no_op() -> Mutation {
            Box::new(|_, _, _| {})
        }

        let outcomes = Outcomes::from_branches_with_coin_paths(vec![
            (0.10, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
            (0.30, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![true])])),
            (0.60, no_op(), CoinPaths::Exact(vec![CoinSeq(vec![false])])),
        ])
        .unwrap();
        let (batches, completed) = marginal_exact_coin_sequences(outcomes).unwrap();
        assert!(completed.is_empty());
        assert_eq!(batches.len(), 2);
        assert_eq!(batches[0].1, CoinSeq(vec![true]));
        assert!((batches[0].0 - 0.40).abs() < 1e-12);
        assert_eq!(batches[1].1, CoinSeq(vec![false]));
        assert!((batches[1].0 - 0.60).abs() < 1e-12);
    }

    #[test]
    fn rejected_misty_target_preserves_rng_and_state() {
        let mut state = State::default();
        state.set_board(
            vec![
                PlayedCard::from_id(CardId::A1053Squirtle),
                PlayedCard::from_id(CardId::A1057Psyduck),
            ],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        let misty = get_card_by_enum(CardId::A1220Misty).as_trainer();
        let original = Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: misty.clone(),
            },
            is_stack: false,
        };
        stage_misty_target(&mut state, &original, misty);
        let before = state.clone();
        let invalid = Action {
            actor: 0,
            action: SimpleAction::ChooseMistyTarget { in_play_idx: 3 },
            is_stack: true,
        };
        let mut actual_rng = StdRng::seed_from_u64(99);
        let mut control_rng = actual_rng.clone();
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _ = sample_misty_target_actual(&mut actual_rng, &state, &invalid);
        }));
        assert!(result.is_err());
        assert_eq!(state, before);
        assert_eq!(actual_rng.next_u64(), control_rng.next_u64());
    }

    #[test]
    fn penny_misty_gholdengo_defers_exactly_one_shuffle_and_keeps_target() {
        for reroll in [false, true] {
            let mut state = State::default();
            state.turn_count = 3;
            state.current_player = 0;
            state.set_board(
                vec![
                    PlayedCard::from_id(CardId::A1053Squirtle),
                    PlayedCard::from_id(CardId::A1057Psyduck),
                    PlayedCard::from_id(CardId::B4a051Gholdengo),
                ],
                vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            );
            let penny = get_card_by_enum(CardId::A3b069Penny);
            state.hands[0] = vec![penny.clone()];
            state.decks[1].cards = vec![
                get_card_by_enum(CardId::A1220Misty),
                get_card_by_enum(CardId::PA001Potion),
                get_card_by_enum(CardId::PA005PokeBall),
            ];
            let original_deck = state.decks[1].clone();
            let mut actual_rng = StdRng::seed_from_u64(417);
            let mut expected_rng = actual_rng.clone();
            let play = Action {
                actor: 0,
                action: SimpleAction::Play {
                    trainer_card: penny.as_trainer(),
                },
                is_stack: false,
            };
            crate::actions::apply_action(&mut actual_rng, &mut state, &play);
            assert_eq!(state.decks[1], original_deck, "shuffle waits for commit");
            assert_eq!(state.discard_piles[0], vec![penny]);

            let _ = choose_supporter_source(
                &mut expected_rng,
                &[(get_card_by_enum(CardId::A1220Misty).as_trainer(), 1)],
            );
            let initial = sample_until_tails(&mut expected_rng, false);
            let choose = Action {
                actor: 0,
                action: SimpleAction::ChooseMistyTarget { in_play_idx: 1 },
                is_stack: true,
            };
            crate::actions::apply_action(&mut actual_rng, &mut state, &choose);
            assert_eq!(
                state.decks[1], original_deck,
                "shuffle waits through coin pause"
            );
            assert_eq!(
                state.pending_trainer_coin_choice.as_ref().unwrap().flips,
                initial.0
            );

            let committed = if reroll {
                let replacement = sample_until_tails(&mut expected_rng, false);
                crate::actions::apply_action(
                    &mut actual_rng,
                    &mut state,
                    &Action {
                        actor: 0,
                        action: SimpleAction::RerollTrainerCoins {
                            luxury_coin_in_play_idx: 2,
                        },
                        is_stack: true,
                    },
                );
                replacement
            } else {
                crate::actions::apply_action(
                    &mut actual_rng,
                    &mut state,
                    &Action {
                        actor: 0,
                        action: SimpleAction::KeepTrainerCoinResults,
                        is_stack: true,
                    },
                );
                initial
            };
            let mut expected_deck = original_deck;
            expected_deck.shuffle(false, &mut expected_rng);
            assert_eq!(state.decks[1], expected_deck);
            assert_eq!(actual_rng.next_u64(), expected_rng.next_u64());
            assert_eq!(state.discard_piles[0].len(), 1, "Play prefix runs once");
            assert!(state.in_play_pokemon[0][0]
                .as_ref()
                .unwrap()
                .attached_energy
                .is_empty());
            assert_eq!(
                state.in_play_pokemon[0][1]
                    .as_ref()
                    .unwrap()
                    .attached_energy
                    .len(),
                committed.0.iter().filter(|face| **face).count()
            );
        }
    }
}
