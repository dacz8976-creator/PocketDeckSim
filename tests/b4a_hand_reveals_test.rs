use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard, TrainerCard},
    observation::hidden_continuation_reason,
    test_support::get_initialized_game_with_board,
    Game,
};

fn use_ability(in_play_idx: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx },
        is_stack: false,
    }
}

fn trainer(card_id: CardId) -> TrainerCard {
    let Card::Trainer(card) = get_card_by_enum(card_id) else {
        panic!("expected Trainer card");
    };
    card
}

fn play(card: TrainerCard) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: card },
        is_stack: false,
    }
}

fn reveal_game(seed: u64, kecleons: usize, opponent_hand: Vec<Card>) -> Game<'static> {
    let mut own_board = vec![PlayedCard::from_id(CardId::B4a062TeamRocketsKecleon)];
    if kecleons == 2 {
        own_board.push(PlayedCard::from_id(CardId::B4a076TeamRocketsKecleon));
    }
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        own_board,
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.hands[0].clear();
    state.hands[1] = opponent_hand;
    game.set_state(state);
    game
}

#[test]
fn spy_ops_reveals_one_card_only_to_its_actor_and_records_the_actual_result() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let ball = get_card_by_enum(CardId::PA005PokeBall);
    let mut game = reveal_game(4, 1, vec![potion.clone(), ball.clone()]);
    let pre_observation = game.observation(0);
    assert_eq!(
        hidden_continuation_reason(pre_observation.visible_state(), &use_ability(0)),
        Some("effect or choice depends on unrevealed opponent cards")
    );

    game.apply_action(&use_ability(0));
    let actor = game.observation(0);
    assert_eq!(actor.revealed.opponent_hand.len(), 1);
    assert_eq!(
        actor.visible_state().hands[1]
            .iter()
            .filter(|card| **card == Card::Unknown)
            .count(),
        1
    );
    assert_eq!(game.private_reveal_history().len(), 1);
    assert_eq!(game.private_reveal_history()[0].scope, "random_hand_card");
    assert_eq!(game.private_reveal_history()[0].cause, "Spy Ops");
    assert_eq!(
        game.private_reveal_history()[0].cards,
        actor.revealed.opponent_hand
    );

    let other = game.observation(1);
    assert!(other.revealed.opponent_hand.is_empty());
    assert!(other.visible_state().move_generation_stack.is_empty());
}

#[test]
fn repeated_spy_ops_peek_of_same_identity_does_not_infer_a_second_copy() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let mut game = reveal_game(0, 2, vec![potion.clone()]);
    game.apply_action(&use_ability(0));
    game.apply_action(&use_ability(1));
    assert_eq!(game.observation(0).revealed.opponent_hand, vec![potion]);
    assert_eq!(game.private_reveal_history().len(), 2);
}

#[test]
fn spy_ops_does_not_reduce_or_inflate_two_copies_known_from_a_whole_hand_reveal() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let boss = trainer(CardId::B4a071TeamRocketsBoss);
    let mut game = reveal_game(0, 1, vec![potion.clone(), potion.clone()]);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![Card::Trainer(boss.clone())];
    game.set_state(state);
    game.apply_action(&play(boss));
    let zero = boss_choices(&game).into_iter().find(|action| {
        matches!(&action.action, SimpleAction::BenchOpponentHandBasics { cards } if cards.is_empty())
    }).unwrap();
    game.apply_action(&zero);
    assert_eq!(
        game.observation(0).revealed.opponent_hand,
        vec![potion.clone(), potion.clone()]
    );

    game.apply_action(&use_ability(0));
    assert_eq!(
        game.observation(0).revealed.opponent_hand,
        vec![potion.clone(), potion]
    );
}

fn boss_game(card_id: CardId, opponent_hand: Vec<Card>, occupied_bench: usize) -> Game<'static> {
    let mut opponent_board = vec![PlayedCard::from_id(CardId::A1033Charmander)];
    opponent_board.extend((0..occupied_bench).map(|_| PlayedCard::from_id(CardId::A1001Bulbasaur)));
    let boss = trainer(card_id);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
        opponent_board,
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![Card::Trainer(boss)];
    state.hands[1] = opponent_hand;
    game.set_state(state);
    game
}

fn boss_choices(game: &Game<'_>) -> Vec<Action> {
    game.get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .filter(|action| matches!(action.action, SimpleAction::BenchOpponentHandBasics { .. }))
        .collect()
}

#[test]
fn team_rockets_boss_reveals_before_private_choose_zero_for_both_printings() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let basic = get_card_by_enum(CardId::A1001Bulbasaur);
    for card_id in [CardId::B4a071TeamRocketsBoss, CardId::B4a087TeamRocketsBoss] {
        let boss = trainer(card_id);
        let mut game = boss_game(card_id, vec![basic.clone(), potion.clone()], 0);
        game.apply_action(&play(boss));

        assert_eq!(game.observation(0).revealed.opponent_hand.len(), 2);
        let opponent_observation = game.observation(1);
        assert!(opponent_observation.revealed.opponent_hand.is_empty());
        assert_eq!(
            opponent_observation
                .visible_state()
                .move_generation_stack
                .last()
                .unwrap()
                .1,
            Vec::<SimpleAction>::new(),
            "the pending subset must not be serialized into another observer's policy state"
        );
        let serialized = serde_json::to_value(&opponent_observation).unwrap();
        assert!(serialized["template"]["move_generation_stack"][0][1]
            .as_array()
            .unwrap()
            .is_empty());
        assert!(!format!("{opponent_observation:?}").contains("BenchOpponentHandBasics"));
        assert_eq!(game.get_state_clone().enumerate_bench_pokemon(1).count(), 0);

        let zero = boss_choices(&game).into_iter().find(|action| {
            matches!(&action.action, SimpleAction::BenchOpponentHandBasics { cards } if cards.is_empty())
        }).expect("choose zero must be offered");
        game.apply_action(&zero);
        assert_eq!(
            game.get_state_clone().hands[1],
            vec![basic.clone(), potion.clone()]
        );
        assert_eq!(game.private_reveal_history()[0].scope, "whole_hand");
        assert_eq!(game.private_reveal_history()[0].cause, "Team Rocket's Boss");
    }
}

#[test]
fn team_rockets_boss_play_legality_does_not_depend_on_hidden_basics_or_bench_space() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let boss = trainer(CardId::B4a071TeamRocketsBoss);
    let mut game = boss_game(CardId::B4a071TeamRocketsBoss, vec![potion.clone()], 3);
    let play_action = play(boss);
    assert!(game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .contains(&play_action));
    assert_eq!(
        hidden_continuation_reason(game.observation(0).visible_state(), &play_action),
        Some("effect or choice depends on unrevealed opponent cards")
    );

    game.apply_action(&play_action);
    let choices = boss_choices(&game);
    assert_eq!(choices.len(), 1);
    assert!(matches!(
        &choices[0].action,
        SimpleAction::BenchOpponentHandBasics { cards } if cards.is_empty()
    ));
    assert_eq!(game.observation(0).revealed.opponent_hand, vec![potion]);
}

#[test]
fn team_rockets_boss_offers_one_and_multiple_with_capacity_and_conserves_cards() {
    let basics = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1053Squirtle),
        get_card_by_enum(CardId::A1033Charmander),
    ];
    let potion = get_card_by_enum(CardId::PA001Potion);
    for chosen_count in [1, 2] {
        let mut hand = basics.clone();
        hand.push(potion.clone());
        let boss = trainer(CardId::B4a071TeamRocketsBoss);
        let mut game = boss_game(CardId::B4a071TeamRocketsBoss, hand, 1);
        game.apply_action(&play(boss));
        let choices = boss_choices(&game);
        assert!(!choices.iter().any(|action| {
            matches!(&action.action, SimpleAction::BenchOpponentHandBasics { cards } if cards.len() > 2)
        }));
        let selected = choices.into_iter().find(|action| {
            matches!(&action.action, SimpleAction::BenchOpponentHandBasics { cards } if cards.len() == chosen_count)
        }).expect("requested subset size should be offered");
        let selected_cards = match &selected.action {
            SimpleAction::BenchOpponentHandBasics { cards } => cards.clone(),
            _ => unreachable!(),
        };
        game.apply_action(&selected);

        let state = game.get_state_clone();
        assert_eq!(state.hands[1].len(), 4 - chosen_count);
        assert!(state.hands[1].contains(&potion));
        for card in &selected_cards {
            assert!(!state.hands[1].contains(card));
            assert!(state
                .enumerate_bench_pokemon(1)
                .any(|(_, pokemon)| pokemon.card == *card));
        }
        assert_eq!(
            game.observation(0).revealed.opponent_hand.len(),
            4 - chosen_count
        );
    }
}
