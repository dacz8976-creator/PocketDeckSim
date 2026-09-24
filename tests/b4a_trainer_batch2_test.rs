use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, TrainerCard},
    test_support::get_initialized_game,
    Game, State,
};

fn trainer(id: CardId) -> TrainerCard {
    get_card_by_enum(id).as_trainer()
}

fn play(game: &mut Game<'static>, actor: usize, id: CardId) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::Play {
            trainer_card: trainer(id),
        },
        is_stack: false,
    });
}

fn use_stadium(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::UseStadium,
        is_stack: false,
    });
}

fn has_play(state: &State, id: CardId) -> bool {
    let wanted = get_card_by_enum(id).get_id();
    state.generate_possible_actions().1.iter().any(|action| {
        matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.id == wanted)
    })
}

fn has_use_stadium(state: &State) -> bool {
    state
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium))
}

fn setup(seed: u64) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

fn advance_past_forced_draw(game: &mut Game<'static>) {
    loop {
        let actions = game.get_state_clone().generate_possible_actions().1;
        if let [only] = actions.as_slice() {
            if matches!(only.action, SimpleAction::DrawCard { .. }) {
                game.apply_action(only);
                continue;
            }
        }
        break;
    }
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    advance_past_forced_draw(game);
}

#[test]
fn thieving_machine_moves_the_only_eligible_opponent_item() {
    let mut game = setup(0);
    let potion = get_card_by_enum(CardId::PA001Potion);
    let supporter = get_card_by_enum(CardId::A2152Cynthia);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::B4a067TeamRocketsThievingMachine)];
    state.discard_piles[1] = vec![supporter.clone(), potion.clone()];
    game.set_state(state);

    assert!(has_play(
        &game.get_state_clone(),
        CardId::B4a067TeamRocketsThievingMachine
    ));
    play(&mut game, 0, CardId::B4a067TeamRocketsThievingMachine);

    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![potion.clone()]);
    assert_eq!(state.discard_piles[1], vec![supporter]);
    assert!(state.discard_piles[0]
        .iter()
        .any(|card| card.get_name() == "Team Rocket's Thieving Machine"));
}

#[test]
fn thieving_machine_randomly_selects_only_eligible_items() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let poke_ball = get_card_by_enum(CardId::PA005PokeBall);
    let excluded = get_card_by_enum(CardId::B4a067TeamRocketsThievingMachine);
    let supporter = get_card_by_enum(CardId::A2152Cynthia);
    let mut saw_potion = false;
    let mut saw_poke_ball = false;

    for seed in 0..60 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![excluded.clone()];
        state.discard_piles[1] = vec![
            excluded.clone(),
            supporter.clone(),
            potion.clone(),
            poke_ball.clone(),
        ];
        game.set_state(state);
        play(&mut game, 0, CardId::B4a067TeamRocketsThievingMachine);

        let stolen = game.get_state_clone().hands[0]
            .first()
            .expect("one eligible Item should be stolen")
            .clone();
        assert!(stolen == potion || stolen == poke_ball);
        saw_potion |= stolen == potion;
        saw_poke_ball |= stolen == poke_ball;
    }
    assert!(saw_potion && saw_poke_ball);
}

#[test]
fn thieving_machine_is_unavailable_without_an_eligible_item() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::B4a067TeamRocketsThievingMachine)];
    state.discard_piles[1] = vec![
        get_card_by_enum(CardId::B4a067TeamRocketsThievingMachine),
        get_card_by_enum(CardId::A2152Cynthia),
        get_card_by_enum(CardId::A2147GiantCape),
        get_card_by_enum(CardId::A1001Bulbasaur),
    ];
    game.set_state(state);
    assert!(!has_play(
        &game.get_state_clone(),
        CardId::B4a067TeamRocketsThievingMachine
    ));
}

#[test]
fn goozooka_increases_retreat_cost_for_exactly_the_opponents_next_turn() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![
            PlayedCard::from_id(CardId::A1055Blastoise).with_energy(vec![EnergyType::Colorless; 3]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::B4a068TeamRocketsGoozooka)];
    game.set_state(state);
    play(&mut game, 0, CardId::B4a068TeamRocketsGoozooka);

    end_turn(&mut game, 0);
    assert!(!game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(_))));

    end_turn(&mut game, 1);
    end_turn(&mut game, 0);
    assert!(game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(_))));
}

#[test]
fn both_goozooka_printings_share_the_effect() {
    for id in [
        CardId::B4a068TeamRocketsGoozooka,
        CardId::B4a110TeamRocketsGoozooka,
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![
                PlayedCard::from_id(CardId::A1055Blastoise)
                    .with_energy(vec![EnergyType::Colorless; 3]),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        state.hands[0] = vec![get_card_by_enum(id)];
        game.set_state(state);
        play(&mut game, 0, id);
        end_turn(&mut game, 0);
        assert!(!game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::Retreat(_))));
    }
}

#[test]
fn master_plan_always_confuses_opponent_and_tails_confuses_self() {
    let mut saw_heads = false;
    let mut saw_tails = false;
    for id in [
        CardId::B4a070TeamRocketsMasterPlan,
        CardId::B4a086TeamRocketsMasterPlan,
        CardId::B4a094TeamRocketsMasterPlan,
    ] {
        for seed in 0..40 {
            let mut game = setup(seed);
            let mut state = game.get_state_clone();
            state.hands[0] = vec![get_card_by_enum(id)];
            game.set_state(state);
            play(&mut game, 0, id);
            let state = game.get_state_clone();
            assert!(state.get_active(1).is_confused());
            if state.get_active(0).is_confused() {
                saw_tails = true;
            } else {
                saw_heads = true;
            }
        }
    }
    assert!(saw_heads && saw_tails);
}

#[test]
fn master_plan_respects_status_immunity_on_each_target() {
    for immune_player in 0..=1 {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.in_play_pokemon[immune_player][0] = Some(PlayedCard::from_id(CardId::A2a071ArceusEx));
        state.hands[0] = vec![get_card_by_enum(CardId::B4a070TeamRocketsMasterPlan)];
        game.set_state(state);

        for seed in 0..40 {
            let mut trial = setup(seed);
            trial.set_state(game.get_state_clone());
            play(&mut trial, 0, CardId::B4a070TeamRocketsMasterPlan);
            assert!(!trial
                .get_state_clone()
                .get_active(immune_player)
                .is_confused());
        }
    }
}

#[test]
fn will_forces_master_plans_coin_to_heads() {
    for seed in 0..20 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![
            get_card_by_enum(CardId::A4156Will),
            get_card_by_enum(CardId::B4a070TeamRocketsMasterPlan),
        ];
        game.set_state(state);
        play(&mut game, 0, CardId::A4156Will);
        play(&mut game, 0, CardId::B4a070TeamRocketsMasterPlan);
        let state = game.get_state_clone();
        assert!(state.get_active(1).is_confused());
        assert!(!state.get_active(0).is_confused());
    }
}

#[test]
fn arcade_has_real_three_coin_outcomes_draws_to_seven_and_is_once_per_turn() {
    let deck_cards = vec![get_card_by_enum(CardId::A1001Bulbasaur); 10];
    let hand_cards = vec![get_card_by_enum(CardId::A1033Charmander); 3];
    let mut saw_all_heads = false;
    let mut saw_other = false;
    for seed in 0..60 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.active_stadium = Some(get_card_by_enum(CardId::B4a072Arcade));
        state.decks[0].cards = deck_cards.clone();
        state.hands[0] = hand_cards.clone();
        game.set_state(state);
        assert!(has_use_stadium(&game.get_state_clone()));
        use_stadium(&mut game, 0);
        let state = game.get_state_clone();
        assert!(state.has_used_stadium[0]);
        assert!(!has_use_stadium(&state));
        match state.hands[0].len() {
            7 => saw_all_heads = true,
            3 => saw_other = true,
            count => panic!("unexpected Arcade hand size {count}"),
        }
    }
    assert!(saw_all_heads && saw_other);
}

#[test]
fn arcade_is_blocked_at_the_hand_limit_and_at_deck_exhaustion() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.active_stadium = Some(get_card_by_enum(CardId::B4a072Arcade));
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur); 7];
    state.hands[1] = vec![get_card_by_enum(CardId::A1033Charmander); 6];
    state.decks[1].cards = vec![];
    game.set_state(state);

    assert!(!has_use_stadium(&game.get_state_clone()));
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state);
    assert!(!has_use_stadium(&game.get_state_clone()));
    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 6);
    assert!(!state.has_used_stadium[1]);
    assert!(!state.has_used_stadium[0]);
}
