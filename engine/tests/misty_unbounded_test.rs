use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction, UnpricedForecastKind},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{PlayedCard, TrainerCard},
    test_support::get_initialized_game,
    Game,
};
use rand::{rngs::StdRng, SeedableRng};

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

fn portrait() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    }
}

fn setup(seed: u64, portrait_active: bool) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    let own = if portrait_active {
        vec![
            PlayedCard::from_id(CardId::B2130Smeargle),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ]
    } else {
        vec![PlayedCard::from_id(CardId::A1053Squirtle)]
    };
    state.set_board(own, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    state.hands = [vec![], vec![]];
    state.decks[0].cards.clear();
    state.decks[1].cards.clear();
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

fn choose_misty_target(game: &mut Game<'static>) -> usize {
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let choices = actions
        .into_iter()
        .filter(|action| matches!(action.action, SimpleAction::ChooseMistyTarget { .. }))
        .collect::<Vec<_>>();
    assert_eq!(choices.len(), 1, "the scaffold must offer one Water target");
    let SimpleAction::ChooseMistyTarget { in_play_idx } = choices[0].action else {
        unreachable!()
    };
    game.apply_action(&choices[0]);
    in_play_idx
}

fn resolve_misty_heads(game: &mut Game<'static>) -> u32 {
    let before = game.get_state_clone();
    let target = choose_misty_target(game);
    let after = game.get_state_clone();
    let before_count = before.in_play_pokemon[0][target]
        .as_ref()
        .unwrap()
        .attached_energy
        .len();
    let after_count = after.in_play_pokemon[0][target]
        .as_ref()
        .unwrap()
        .attached_energy
        .len();
    (after_count - before_count) as u32
}

fn has_misty_target(game: &Game<'static>) -> bool {
    game.get_state_clone().pending_misty_target_choice.is_some()
}

fn forecast_after_target_is_unpriced(
    state: &deckgym::State,
    initial: &Action,
) -> UnpricedForecastKind {
    let outcomes = try_forecast_action(state, initial)
        .expect("the finite target phase must be forecast exactly");
    let (_, mutations) = outcomes.into_branches();
    let mut staged = mutations
        .into_iter()
        .find_map(|mutation| {
            let mut candidate = state.clone();
            let mut rng = StdRng::seed_from_u64(1);
            mutation(&mut rng, &mut candidate, initial);
            candidate
                .pending_misty_target_choice
                .is_some()
                .then_some(candidate)
        })
        .expect("one exact source branch must stage Misty's target");
    let (_, actions) = staged.generate_possible_actions();
    let target = actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::ChooseMistyTarget { .. }))
        .expect("target action");
    try_forecast_action(&staged, &target)
        .err()
        .expect("the post-target public geometric batch is unpriced")
        .kind
}

fn assert_will_consumed(game: &Game<'static>) {
    let serialized = serde_json::to_string(&game.get_state_clone()).unwrap();
    assert!(
        !serialized.contains("ForceFirstHeads"),
        "the selected Misty batch must consume Will exactly once"
    );
}

fn direct_heads(seed: u64) -> u32 {
    let mut game = setup(seed, false);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
    game.set_state(state);
    game.apply_action(&play(CardId::A1220Misty));
    resolve_misty_heads(&mut game)
}

fn penny_heads(seed: u64) -> u32 {
    let mut game = setup(seed, false);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
    game.set_state(state);
    game.apply_action(&play(CardId::A3b069Penny));
    resolve_misty_heads(&mut game)
}

fn portrait_heads(seed: u64) -> u32 {
    let mut game = setup(seed, true);
    let mut state = game.get_state_clone();
    state.hands[1] = vec![get_card_by_enum(CardId::A1220Misty)];
    game.set_state(state);
    game.apply_action(&portrait());
    resolve_misty_heads(&mut game)
}

#[test]
fn physical_misty_is_not_capped_for_direct_penny_or_portrait_routes() {
    let mut maxima = [0; 3];
    for seed in 0..1024 {
        maxima[0] = maxima[0].max(direct_heads(seed));
        maxima[1] = maxima[1].max(penny_heads(seed));
        maxima[2] = maxima[2].max(portrait_heads(seed));
    }
    assert!(
        maxima.iter().all(|heads| *heads > 5),
        "every physical route must exceed the removed five-head cap; maxima={maxima:?}"
    );
}

#[test]
fn exact_forecasts_price_target_then_refuse_infinite_public_batches() {
    let direct = setup(7, false);
    let mut state = direct.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
    assert!(matches!(
        forecast_after_target_is_unpriced(&state, &play(CardId::A1220Misty)),
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));

    state.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
    assert!(matches!(
        forecast_after_target_is_unpriced(&state, &play(CardId::A3b069Penny)),
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));

    let portrait_game = setup(9, true);
    let mut state = portrait_game.get_state_clone();
    state.hands[1] = vec![get_card_by_enum(CardId::A1220Misty)];
    assert!(matches!(
        forecast_after_target_is_unpriced(&state, &portrait()),
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));

    state.hands[1] = vec![get_card_by_enum(CardId::A3b069Penny)];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
    assert!(matches!(
        forecast_after_target_is_unpriced(&state, &portrait()),
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));
}

#[test]
fn will_forces_only_mistys_first_flip_on_the_uncapped_physical_path() {
    // Mechanics fixture only: direct calls intentionally bypass the one-Supporter-per-turn gate.
    // Legal generated-action Will routes are covered in misty_precoin_target_test.
    let mut saw_more_than_one = false;
    for seed in 0..128 {
        let mut game = setup(seed, false);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![
            get_card_by_enum(CardId::A4156Will),
            get_card_by_enum(CardId::A1220Misty),
        ];
        game.set_state(state);
        game.apply_action(&play(CardId::A4156Will));
        game.apply_action(&play(CardId::A1220Misty));
        assert!(has_misty_target(&game));
        let heads = resolve_misty_heads(&mut game);
        assert!(heads >= 1, "Will must force the first Misty coin to heads");
        assert_will_consumed(&game);
        saw_more_than_one |= heads > 1;
    }
    assert!(saw_more_than_one, "later Misty flips must remain random");
}

#[test]
fn physical_penny_source_selection_retains_duplicate_card_weight() {
    let mut selected_misty = 0;
    let trials = 2048;
    for seed in 0..trials {
        let mut game = setup(seed, false);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
        state.decks[1].cards = vec![
            get_card_by_enum(CardId::A1220Misty),
            get_card_by_enum(CardId::A1220Misty),
            // With no opposing Bench, copied Sabrina is a legal source selection whose effect
            // is a no-op. It makes the source selected by Penny observable in this scaffold.
            get_card_by_enum(CardId::A1225Sabrina),
        ];
        game.set_state(state);
        game.apply_action(&play(CardId::A3b069Penny));
        selected_misty += usize::from(has_misty_target(&game));
    }
    let share = selected_misty as f64 / trials as f64;
    assert!(
        (0.62..0.71).contains(&share),
        "two copies of Misty among three physical cards should retain about 2/3 source mass; got {share}"
    );
}

#[test]
fn unusable_copied_misty_is_noop_and_does_not_consume_will() {
    for seed in 0..64 {
        let mut game = setup(seed, false);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        state.hands[0] = vec![
            get_card_by_enum(CardId::A4156Will),
            get_card_by_enum(CardId::A3b069Penny),
        ];
        state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
        state.active_stadium = Some(get_card_by_enum(CardId::B2a093Mesagoza));
        state.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander)];
        game.set_state(state);

        // This direct-action scaffold isolates Will across copied-source resolution; normal move
        // generation enforces the one-Supporter-per-turn rule.
        game.apply_action(&play(CardId::A4156Will));
        game.apply_action(&play(CardId::A3b069Penny));
        assert!(!has_misty_target(&game));
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseStadium,
            is_stack: false,
        });
        assert!(
            game.get_state_clone().hands[0].contains(&get_card_by_enum(CardId::A1033Charmander))
        );
    }
}

#[test]
fn will_reaches_misty_through_penny_portrait_and_nested_portrait_penny() {
    for seed in 0..128 {
        let mut penny = setup(seed, false);
        let mut state = penny.get_state_clone();
        state.hands[0] = vec![
            get_card_by_enum(CardId::A4156Will),
            get_card_by_enum(CardId::A3b069Penny),
        ];
        state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
        penny.set_state(state);
        penny.apply_action(&play(CardId::A4156Will));
        penny.apply_action(&play(CardId::A3b069Penny));
        assert!(resolve_misty_heads(&mut penny) >= 1);
        assert_will_consumed(&penny);

        let mut portrait_game = setup(seed, true);
        let mut state = portrait_game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A4156Will)];
        state.hands[1] = vec![get_card_by_enum(CardId::A1220Misty)];
        portrait_game.set_state(state);
        portrait_game.apply_action(&play(CardId::A4156Will));
        portrait_game.apply_action(&portrait());
        assert!(resolve_misty_heads(&mut portrait_game) >= 1);
        assert_will_consumed(&portrait_game);

        let mut nested = setup(seed, true);
        let mut state = nested.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A4156Will)];
        state.hands[1] = vec![get_card_by_enum(CardId::A3b069Penny)];
        state.decks[1].cards = vec![get_card_by_enum(CardId::A1220Misty)];
        nested.set_state(state);
        nested.apply_action(&play(CardId::A4156Will));
        nested.apply_action(&portrait());
        assert!(resolve_misty_heads(&mut nested) >= 1);
        assert_will_consumed(&nested);
    }
}

#[test]
fn spent_luxury_coin_falls_back_to_the_same_uncapped_physical_misty_path() {
    let mut maximum = 0;
    for seed in 0..1024 {
        let mut game = setup(seed, false);
        let mut state = game.get_state_clone();
        state.in_play_pokemon[0][1] = Some(PlayedCard::from_id(CardId::B4a051Gholdengo));
        state.luxury_coin_used_this_turn[0] = true;
        state.hands[0] = vec![get_card_by_enum(CardId::A1220Misty)];
        game.set_state(state);
        game.apply_action(&play(CardId::A1220Misty));
        assert!(game.get_state_clone().pending_trainer_coin_choice.is_none());
        maximum = maximum.max(resolve_misty_heads(&mut game));
    }
    assert!(
        maximum > 5,
        "spent Luxury Coin must not restore the old cap"
    );
}

#[test]
fn mixed_source_forecast_is_unpriced_only_when_usable_misty_is_reachable() {
    let mut water = setup(41, false).get_state_clone();
    water.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
    water.decks[1].cards = vec![
        get_card_by_enum(CardId::A1220Misty),
        get_card_by_enum(CardId::PA007ProfessorsResearch),
    ];
    assert!(matches!(
        forecast_after_target_is_unpriced(&water, &play(CardId::A3b069Penny)),
        UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
    ));

    let mut grass = setup(43, false).get_state_clone();
    grass.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    grass.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
    grass.decks[1].cards = vec![
        get_card_by_enum(CardId::A1220Misty),
        get_card_by_enum(CardId::PA007ProfessorsResearch),
    ];
    assert!(
        try_forecast_action(&grass, &play(CardId::A3b069Penny)).is_ok(),
        "an unusable copied Misty branch is a finite no-op rather than an infinite coin batch"
    );
}
