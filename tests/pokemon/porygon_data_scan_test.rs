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

/// Porygon (A1 209 / A1 249) active, with player 0's deck replaced by `deck_cards`.
fn game_with_deck(deck_cards: Vec<CardId>) -> Game<'static> {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1209Porygon)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards = deck_cards.into_iter().map(get_card_by_enum).collect();
    game.set_state(state);
    game
}

/// Data Scan: "Once during your turn, you may look at the top card of your deck."
///
/// Looking at a card is pure information, and deckgym's bots have no hidden-information model, so
/// the only thing the ability may change is its own once-per-turn flag. This asserts exactly that:
/// the ability is legal, using it marks it used, and *nothing else* about the game state moves.
#[test]
fn test_data_scan_is_usable_and_changes_nothing_but_the_ability_flag() {
    let mut game = game_with_deck(vec![CardId::A1001Bulbasaur, CardId::A1033Charmander]);

    let before = game.get_state_clone();
    let (_actor, actions) = before.clone().generate_possible_actions();
    let ability_action = use_ability_action(&actions, 0).expect("Data Scan should be available");
    game.apply_action(&ability_action);

    let after = game.get_state_clone();
    assert!(
        after.get_active(0).ability_used,
        "using Data Scan should mark the ability as used"
    );

    // The board is untouched apart from the once-per-turn flag.
    let mut expected_board = before.in_play_pokemon.clone();
    expected_board[0][0]
        .as_mut()
        .expect("Porygon should be Active")
        .ability_used = true;
    assert_eq!(
        after.in_play_pokemon, expected_board,
        "Data Scan must not change anything on the board"
    );

    assert_eq!(after.hands, before.hands, "Data Scan must not draw a card");
    assert_eq!(
        after.decks[0].cards, before.decks[0].cards,
        "Data Scan must not move, remove or shuffle any card of the deck"
    );
    assert_eq!(after.decks[1].cards, before.decks[1].cards);
    assert_eq!(after.discard_piles, before.discard_piles);
    assert_eq!(after.points, before.points);
    assert_eq!(after.current_player, before.current_player);
}

/// NEGATIVE: "Once during your turn".
#[test]
fn test_data_scan_is_once_per_turn() {
    let mut game = game_with_deck(vec![CardId::A1001Bulbasaur, CardId::A1033Charmander]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action = use_ability_action(&actions, 0).expect("Data Scan should be available");
    game.apply_action(&ability_action);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Data Scan should not be usable twice in the same turn"
    );
}

/// NEGATIVE: with an empty deck there is no top card to look at, so the ability is not offered
/// (and does not clutter the bots' move tree with a branch that cannot do anything).
#[test]
fn test_data_scan_not_offered_with_empty_deck() {
    let game = game_with_deck(vec![]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Data Scan should not be offered when the deck is empty"
    );
}
