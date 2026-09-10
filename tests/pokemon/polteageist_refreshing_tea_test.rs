use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    test_support::get_initialized_game,
    Game,
};

/// Sinistea active for player 0 with Polteageist (B2 075) in hand, and player 1 holding
/// `opponent_hand` cards on `opponent_points` points.
fn game_ready_to_evolve(opponent_hand: usize, opponent_points: u8) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2074Sinistea)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.hands[0].clear();
    state.hands[0].push(get_card_by_enum(CardId::B2075Polteageist));
    state.hands[1] = vec![get_card_by_enum(CardId::A1225Sabrina); opponent_hand];
    state.decks[1].cards = vec![get_card_by_enum(CardId::PA005PokeBall); 20];
    state.points[1] = opponent_points;
    game.set_state(state);
    game
}

fn evolve_into_polteageist(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Evolve {
            evolution: get_card_by_enum(CardId::B2075Polteageist),
            in_play_idx: 0,
            from_deck: false,
        },
        is_stack: false,
    });
}

/// Refreshing Tea: "Once during your turn, when you play this Pokémon from your hand to evolve 1
/// of your Pokémon, you may have your opponent shuffle their hand into their deck. For each
/// remaining point that your opponent needs to win, they draw a card."
#[test]
fn test_refreshing_tea_shuffles_opponent_hand_and_redraws_remaining_points() {
    let mut game = game_ready_to_evolve(5, 1);

    evolve_into_polteageist(&mut game);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Noop)),
        "Refreshing Tea says 'you may', so declining must be an option"
    );
    let use_tea = choices
        .iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::OpponentShuffleHandAndDrawRemainingPoints
            )
        })
        .expect("Refreshing Tea should be offered on evolve")
        .clone();

    game.apply_action(&use_tea);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_name(),
        "Polteageist",
        "the evolution itself should still have happened"
    );
    assert_eq!(
        state.hands[1].len(),
        2,
        "opponent on 1 point needs 2 more, so they redraw 2 cards"
    );
    assert!(
        state.hands[1]
            .iter()
            .all(|card| card.get_name() == "Poké Ball"),
        "the redrawn cards must come from the deck, not the shuffled-away hand"
    );
    assert_eq!(
        state.decks[1].cards.len(),
        23,
        "20 deck cards + 5 shuffled-in hand cards - 2 drawn"
    );
}

/// The draw count tracks the opponent's score: on 2 points they need 1 more, so they draw 1.
#[test]
fn test_refreshing_tea_draw_count_tracks_opponent_points() {
    let mut game = game_ready_to_evolve(4, 2);

    evolve_into_polteageist(&mut game);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let use_tea = choices
        .iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::OpponentShuffleHandAndDrawRemainingPoints
            )
        })
        .expect("Refreshing Tea should be offered on evolve")
        .clone();

    game.apply_action(&use_tea);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 1);
}

/// NEGATIVE: it is a "may" — declining leaves the opponent's hand exactly as it was.
#[test]
fn test_refreshing_tea_declined_leaves_opponent_hand_alone() {
    let mut game = game_ready_to_evolve(5, 1);
    let hand_before = game.get_state_clone().hands[1].clone();

    evolve_into_polteageist(&mut game);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let decline = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Noop))
        .expect("declining must be an option")
        .clone();

    game.apply_action(&decline);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1], hand_before);
    assert_eq!(state.decks[1].cards.len(), 20);
    assert_eq!(state.get_active(0).get_name(), "Polteageist");
}

/// NEGATIVE: the Ability triggers on evolving *from hand* only, so a Polteageist already in play
/// never offers it.
#[test]
fn test_refreshing_tea_does_not_trigger_without_evolving() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2075Polteageist)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    game.set_state(state);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    assert!(
        choices.iter().all(|choice| !matches!(
            choice.action,
            SimpleAction::OpponentShuffleHandAndDrawRemainingPoints
        )),
        "Refreshing Tea is an on-evolve trigger, not an activated Ability"
    );
}
