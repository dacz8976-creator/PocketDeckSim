use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    test_support::get_test_game_with_board,
    Game,
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

/// Unown (A2a 034 / A2a 078) active, with both players' decks replaced.
fn game_with_decks(own_deck: Vec<CardId>, opponent_deck: Vec<CardId>) -> Game<'static> {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2a034Unown)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards = own_deck.into_iter().map(get_card_by_enum).collect();
    state.decks[1].cards = opponent_deck.into_iter().map(get_card_by_enum).collect();
    game.set_state(state);
    game
}

/// CHECK: "Once during your turn, you may choose either player. Look at the top card of that
/// player's deck."
///
/// Looking at a card is pure information, and deckgym's bots have no hidden-information model, so
/// the only thing the ability may change is its own once-per-turn flag. This asserts exactly that
/// for both decks.
#[test]
fn test_check_is_usable_and_changes_nothing_but_the_ability_flag() {
    let mut game = game_with_decks(
        vec![CardId::A1001Bulbasaur, CardId::A1033Charmander],
        vec![CardId::A1053Squirtle],
    );

    let before = game.get_state_clone();
    let (_actor, actions) = before.clone().generate_possible_actions();
    let ability_action = use_ability_action(&actions, 0).expect("CHECK should be available");
    game.apply_action(&ability_action);

    let after = game.get_state_clone();
    assert!(
        after.get_active(0).ability_used,
        "using CHECK should mark the ability as used"
    );

    let mut expected_board = before.in_play_pokemon.clone();
    expected_board[0][0]
        .as_mut()
        .expect("Unown should be Active")
        .ability_used = true;
    assert_eq!(
        after.in_play_pokemon, expected_board,
        "CHECK must not change anything on the board"
    );

    assert_eq!(after.hands, before.hands, "CHECK must not draw a card");
    assert_eq!(
        after.decks[0].cards, before.decks[0].cards,
        "CHECK must not disturb its controller's deck"
    );
    assert_eq!(
        after.decks[1].cards, before.decks[1].cards,
        "CHECK must not disturb the opponent's deck"
    );
    assert_eq!(after.discard_piles, before.discard_piles);
    assert_eq!(after.points, before.points);
    assert_eq!(after.current_player, before.current_player);
}

/// "Choose either player": the opponent's deck is a legal target, so CHECK is still usable when
/// only the opponent has cards left.
#[test]
fn test_check_is_usable_when_only_the_opponent_has_a_deck() {
    let game = game_with_decks(vec![], vec![CardId::A1053Squirtle]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_some(),
        "CHECK should still be usable while the opponent has a top card to look at"
    );
}

/// NEGATIVE: "Once during your turn".
#[test]
fn test_check_is_once_per_turn() {
    let mut game = game_with_decks(vec![CardId::A1001Bulbasaur], vec![CardId::A1053Squirtle]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action = use_ability_action(&actions, 0).expect("CHECK should be available");
    game.apply_action(&ability_action);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "CHECK should not be usable twice in the same turn"
    );
}

/// NEGATIVE: neither player has a top card left, so there is nothing to look at.
#[test]
fn test_check_not_offered_when_both_decks_are_empty() {
    let game = game_with_decks(vec![], vec![]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "CHECK should not be offered when both decks are empty"
    );
}
