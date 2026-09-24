use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_test_game_with_board,
    Game,
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

/// Builds a game with Ambipom active and player 0's deck replaced by `deck_cards`.
fn game_with_deck(deck_cards: Vec<Card>) -> Game<'static> {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3b059Ambipom)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards = deck_cards;
    game.set_state(state);
    game
}

/// Ambipom's Catching Tail: "Once during your turn, you may put a random Pokémon Tool card from
/// your deck into your hand."
#[test]
fn test_catching_tail_puts_a_tool_from_the_deck_into_hand() {
    let giant_cape = get_card_by_enum(CardId::A2147GiantCape);
    let bulbasaur = get_card_by_enum(CardId::A1001Bulbasaur);
    let mut game = game_with_deck(vec![giant_cape.clone(), bulbasaur.clone()]);

    let hand_before = game.get_state_clone().hands[0].len();

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Catching Tail should be available");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[0].len(),
        hand_before + 1,
        "exactly one card should move from the deck to the hand"
    );
    assert!(
        state.hands[0].contains(&giant_cape),
        "the Pokémon Tool should be the card that moved to the hand"
    );
    assert!(
        !state.decks[0].cards.contains(&giant_cape),
        "the tool should have left the deck"
    );
    assert!(
        state.decks[0].cards.contains(&bulbasaur),
        "non-Tool cards must stay in the deck"
    );
}

/// Only Tool cards are eligible: Items and Supporters are Trainer cards too, but Catching Tail
/// must skip them.
#[test]
fn test_catching_tail_picks_a_tool_over_other_trainer_cards() {
    let rocky_helmet = get_card_by_enum(CardId::A2148RockyHelmet);
    let poke_ball = get_card_by_enum(CardId::PA005PokeBall);
    let mut game = game_with_deck(vec![poke_ball.clone(), rocky_helmet.clone()]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Catching Tail should be available");
    game.apply_action(&ability_action);

    let state = game.get_state_clone();
    assert!(
        state.hands[0].contains(&rocky_helmet),
        "the Tool should have been drawn"
    );
    assert!(
        state.decks[0].cards.contains(&poke_ball),
        "the Item card must stay in the deck"
    );
}

/// Deck contents are hidden, so a nonempty deck permits the search attempt even when it has
/// no Tool. The attempt finds nothing, shuffles the deck and consumes the once-per-turn Ability.
#[test]
fn test_catching_tail_is_offered_when_hidden_deck_has_no_tool() {
    let mut game = game_with_deck(vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::PA005PokeBall),
    ]);
    let state_before = game.get_state_clone();
    let hand_len_before = state_before.hands[0].len();
    let mut deck_ids_before = state_before.decks[0]
        .cards
        .iter()
        .map(Card::get_id)
        .collect::<Vec<_>>();
    deck_ids_before.sort();

    let (_actor, actions) = state_before.generate_possible_actions();
    let ability = use_ability_action(&actions, 0)
        .expect("a nonempty hidden deck must permit the search attempt");
    game.apply_action(&ability);

    let state = game.get_state_clone();
    let mut deck_ids_after = state.decks[0]
        .cards
        .iter()
        .map(Card::get_id)
        .collect::<Vec<_>>();
    deck_ids_after.sort();
    assert_eq!(state.hands[0].len(), hand_len_before);
    assert_eq!(deck_ids_after, deck_ids_before);
    assert!(state.get_active(0).ability_used);
    assert!(use_ability_action(&state.generate_possible_actions().1, 0).is_none());
}

/// NEGATIVE: an empty deck is also handled cleanly.
#[test]
fn test_catching_tail_not_offered_with_empty_deck() {
    let game = game_with_deck(vec![]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Catching Tail should not be offered with an empty deck"
    );
}

/// NEGATIVE: "Once during your turn".
#[test]
fn test_catching_tail_is_once_per_turn() {
    let mut game = game_with_deck(vec![
        get_card_by_enum(CardId::A2147GiantCape),
        get_card_by_enum(CardId::A2148RockyHelmet),
    ]);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Catching Tail should be available");
    game.apply_action(&ability_action);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Catching Tail should not be usable twice in the same turn"
    );
}
