use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction, UnpricedForecastKind},
    card_ids::CardId,
    card_validation::{get_implementation_status, ImplementationStatus},
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, TrainerCard},
    observation::{PlayerObservation, RevealedKnowledge},
    state::{LuxuryCoinDecision, TrainerCoinEffectRoute},
    test_support::get_initialized_game,
    Game, State,
};

fn trainer(id: CardId) -> TrainerCard {
    get_card_by_enum(id).as_trainer()
}

fn play(id: CardId) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: trainer(id),
        },
        is_stack: false,
    }
}

fn keep() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::KeepTrainerCoinResults,
        is_stack: true,
    }
}

fn reroll(source: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::RerollTrainerCoins {
            luxury_coin_in_play_idx: source,
        },
        is_stack: true,
    }
}

fn setup(seed: u64, gholdengo: CardId) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(gholdengo),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

#[test]
fn both_printings_map_as_passive_rules_unverified_abilities() {
    for id in [CardId::B4a051Gholdengo, CardId::B4a109Gholdengo] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::RulesUnverified
        );
        let game = setup(1, id);
        assert!(!game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 1 })));
    }
}

#[test]
fn ice_pop_pays_play_cost_and_heals_once_before_public_choice() {
    for seed in 0..24 {
        let mut game = setup(seed, CardId::B4a051Gholdengo);
        let item = get_card_by_enum(CardId::B2145LuckyIcePop);
        let mut state = game.get_state_clone();
        state.in_play_pokemon[0][0] =
            Some(PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(40));
        state.hands[0] = vec![item.clone()];
        game.set_state(state);

        game.apply_action(&play(CardId::B2145LuckyIcePop));
        let paused = game.get_state_clone();
        assert_eq!(paused.get_active(0).get_remaining_hp(), 50);
        assert!(paused.hands[0].is_empty());
        assert_eq!(paused.discard_piles[0], vec![item.clone()]);
        let initial_heads = paused.pending_trainer_coin_choice.as_ref().unwrap().flips[0];

        game.apply_action(&keep());
        let committed = game.get_state_clone();
        assert_eq!(committed.get_active(0).get_remaining_hp(), 50);
        assert_eq!(committed.hands[0].contains(&item), initial_heads);
        assert_eq!(committed.discard_piles[0].contains(&item), !initial_heads);
        assert!(committed.pending_trainer_coin_choice.is_none());
    }
}

#[test]
fn ice_pop_without_real_healing_has_no_batch_and_leaves_will_for_stadium() {
    for seed in 0..20 {
        let mut game = setup(seed, CardId::B4a051Gholdengo);
        let will = get_card_by_enum(CardId::A4156Will);
        let ice = get_card_by_enum(CardId::B2145LuckyIcePop);
        let searched = get_card_by_enum(CardId::A1033Charmander);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![will.clone(), ice];
        state.decks[0].cards = vec![searched.clone()];
        state.active_stadium = Some(get_card_by_enum(CardId::B2a093Mesagoza));
        game.set_state(state);

        game.apply_action(&play(CardId::A4156Will));
        game.apply_action(&play(CardId::B2145LuckyIcePop));
        assert!(game.get_state_clone().pending_trainer_coin_choice.is_none());
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseStadium,
            is_stack: false,
        });
        let pending = game.get_state_clone().pending_trainer_coin_choice.unwrap();
        assert_eq!(pending.flips, vec![true]);
        game.apply_action(&keep());
        assert_eq!(game.get_state_clone().hands[0], vec![searched]);
    }
}

#[test]
fn master_plan_prefix_is_once_only_and_tail_suffix_waits_for_commit() {
    for seed in 0..24 {
        let mut game = setup(seed, CardId::B4a051Gholdengo);
        let master = get_card_by_enum(CardId::B4a070TeamRocketsMasterPlan);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![master.clone()];
        game.set_state(state);

        game.apply_action(&play(CardId::B4a070TeamRocketsMasterPlan));
        let paused = game.get_state_clone();
        assert!(paused
            .get_active(1)
            .has_status(deckgym::models::StatusCondition::Confused));
        assert!(!paused
            .get_active(0)
            .has_status(deckgym::models::StatusCondition::Confused));
        assert!(paused.hands[0].is_empty());
        assert!(paused.discard_piles[0].contains(&master));
        let heads = paused.pending_trainer_coin_choice.as_ref().unwrap().flips[0];

        game.apply_action(&keep());
        let committed = game.get_state_clone();
        assert!(committed
            .get_active(1)
            .has_status(deckgym::models::StatusCondition::Confused));
        assert_eq!(
            committed
                .get_active(0)
                .has_status(deckgym::models::StatusCondition::Confused),
            !heads
        );
        assert_eq!(
            committed.discard_piles[0]
                .iter()
                .filter(|c| **c == master)
                .count(),
            1
        );
    }
}

#[test]
fn activated_stadium_records_placer_but_eligibility_belongs_to_actor() {
    for owner in [None, Some(0), Some(1)] {
        let mut game = setup(7, CardId::B4a109Gholdengo);
        let mut state = game.get_state_clone();
        state.active_stadium = Some(get_card_by_enum(CardId::B4a072Arcade));
        state.active_stadium_owner = owner;
        state.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander); 8];
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseStadium,
            is_stack: false,
        });
        let paused = game.get_state_clone();
        assert!(paused.has_used_stadium[0]);
        let pending = paused.pending_trainer_coin_choice.unwrap();
        assert_eq!(pending.flips.len(), 3);
        assert!(matches!(
            pending.route,
            Some(TrainerCoinEffectRoute::Stadium { played_by, .. }) if played_by == owner
        ));
    }
}

#[test]
fn actor_sees_fixed_route_while_opponent_sees_only_public_faces() {
    let mut game = setup(9, CardId::B4a051Gholdengo);
    let mut state = game.get_state_clone();
    state.active_stadium = Some(get_card_by_enum(CardId::B4a072Arcade));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseStadium,
        is_stack: false,
    });
    let referee = game.get_state_clone();
    let actor = PlayerObservation::from_state(&referee, 0, &RevealedKnowledge::default());
    let opponent = PlayerObservation::from_state(&referee, 1, &RevealedKnowledge::default());
    assert_eq!(
        actor
            .visible_state()
            .pending_trainer_coin_choice
            .as_ref()
            .unwrap()
            .flips,
        opponent
            .visible_state()
            .pending_trainer_coin_choice
            .as_ref()
            .unwrap()
            .flips
    );
    assert!(actor
        .visible_state()
        .pending_trainer_coin_choice
        .as_ref()
        .unwrap()
        .route
        .is_some());
    assert!(opponent
        .visible_state()
        .pending_trainer_coin_choice
        .as_ref()
        .unwrap()
        .route
        .is_none());
    assert!(opponent
        .visible_state()
        .move_generation_stack
        .last()
        .unwrap()
        .1
        .is_empty());
}

#[test]
fn penny_unusable_misty_is_noop_without_prompt_or_will_consumption() {
    let mut game = setup(13, CardId::B4a051Gholdengo);
    let will = get_card_by_enum(CardId::A4156Will);
    let penny = get_card_by_enum(CardId::A3b069Penny);
    let misty = get_card_by_enum(CardId::A1220Misty);
    let searched = get_card_by_enum(CardId::A1033Charmander);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![will, penny.clone()];
    state.decks[1].cards = vec![misty];
    state.active_stadium = Some(get_card_by_enum(CardId::B2a093Mesagoza));
    state.decks[0].cards = vec![searched.clone()];
    game.set_state(state);
    game.apply_action(&play(CardId::A4156Will));
    game.apply_action(&play(CardId::A3b069Penny));
    let after_penny = game.get_state_clone();
    assert!(after_penny.pending_trainer_coin_choice.is_none());
    assert!(after_penny.discard_piles[0].contains(&penny));
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseStadium,
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone()
            .pending_trainer_coin_choice
            .unwrap()
            .flips,
        vec![true]
    );
}

#[test]
fn unbounded_public_entry_is_unpriced_but_actual_researcher_can_keep() {
    let mut game = setup(15, CardId::B4a051Gholdengo);
    let researcher = get_card_by_enum(CardId::B4a069TeamRocketsResearcher);
    let eligible = get_card_by_enum(CardId::B4a006TeamRocketsMagmar);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![researcher.clone()];
    state.decks[0].cards = vec![eligible.clone(), eligible.clone()];
    game.set_state(state.clone());
    let error = try_forecast_action(&state, &play(CardId::B4a069TeamRocketsResearcher))
        .err()
        .expect("public H*T entry cannot be finitely enumerated");
    assert!(matches!(
        error.kind,
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));

    game.apply_action(&play(CardId::B4a069TeamRocketsResearcher));
    let paused = game.get_state_clone();
    assert_eq!(paused.hands[0].len(), 0);
    assert_eq!(paused.decks[0].cards.len(), 2);
    let heads = paused
        .pending_trainer_coin_choice
        .as_ref()
        .unwrap()
        .flips
        .iter()
        .filter(|face| **face)
        .count();
    game.apply_action(&keep());
    assert_eq!(game.get_state_clone().hands[0].len(), heads.min(2));
}

#[test]
fn reroll_is_single_use_and_durably_records_both_batches() {
    let mut game = setup(21, CardId::B4a051Gholdengo);
    let hammer = get_card_by_enum(CardId::B1215HittingHammer);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![hammer];
    state.in_play_pokemon[1][0]
        .as_mut()
        .unwrap()
        .attached_energy = vec![EnergyType::Fire];
    game.set_state(state);
    game.apply_action(&play(CardId::B1215HittingHammer));
    let pending = game.get_state_clone().pending_trainer_coin_choice.unwrap();
    game.apply_action(&reroll(pending.luxury_coin_in_play_idx));
    let committed = game.get_state_clone();
    assert!(committed.luxury_coin_used_this_turn[0]);
    assert!(committed.pending_trainer_coin_choice.is_none());
    let records = game.luxury_coin_resolution_history();
    assert_eq!(records.len(), 1);
    assert_eq!(records[0].actor, 0);
    assert_eq!(records[0].initial_faces, pending.flips);
    assert_eq!(records[0].decision, LuxuryCoinDecision::Reroll);
    assert_eq!(records[0].replacement_faces.as_ref().unwrap().len(), 2);
}

#[test]
fn pending_state_and_actions_round_trip_and_old_state_defaults_new_fields() {
    let mut game = setup(31, CardId::B4a051Gholdengo);
    let mut state = game.get_state_clone();
    state.active_stadium = Some(get_card_by_enum(CardId::B4a072Arcade));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseStadium,
        is_stack: false,
    });
    let pending = game.get_state_clone();
    let json = serde_json::to_string(&pending).unwrap();
    let restored: State = serde_json::from_str(&json).unwrap();
    assert_eq!(restored, pending);

    let mut value = serde_json::to_value(&pending).unwrap();
    let object = value.as_object_mut().unwrap();
    object.remove("pending_trainer_coin_choice");
    object.remove("luxury_coin_used_this_turn");
    let old: State = serde_json::from_value(value).unwrap();
    assert!(old.pending_trainer_coin_choice.is_none());
    assert_eq!(old.luxury_coin_used_this_turn, [false; 2]);
}
