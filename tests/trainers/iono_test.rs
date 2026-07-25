use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
};

fn make_trainer_card(card_id: CardId) -> deckgym::models::TrainerCard {
    get_card_by_enum(card_id).as_trainer()
}

/// Iono (B2a 089): "Each player shuffles the cards in their hand into their deck, then draws
/// that many cards." The Paldean Wonders reprint must behave like the A2b original.
#[test]
fn test_iono_b2a_printing_refreshes_both_hands_keeping_sizes() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let iono = make_trainer_card(CardId::B2a089Iono);
    // Player 0 holds Iono plus two Charmander; player 1 holds three Squirtle.
    state.hands[0] = vec![
        Card::Trainer(iono.clone()),
        get_card_by_enum(CardId::A1033Charmander),
        get_card_by_enum(CardId::A1033Charmander),
    ];
    state.hands[1] = vec![
        get_card_by_enum(CardId::A1053Squirtle),
        get_card_by_enum(CardId::A1053Squirtle),
        get_card_by_enum(CardId::A1053Squirtle),
    ];
    // Decks hold only Pikachu, so a refreshed hand is distinguishable from the old one.
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1a025Pikachu); 8];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1a025Pikachu); 8];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: iono },
        is_stack: false,
    });

    let state = game.get_state_clone();
    // Iono itself is discarded before the effect resolves, so player 0 shuffles 2 and draws 2.
    assert_eq!(state.hands[0].len(), 2);
    assert_eq!(state.hands[1].len(), 3);
    assert_eq!(state.decks[0].cards.len(), 8);
    assert_eq!(state.decks[1].cards.len(), 8);

    // Both hands went through the deck, so each side has drawn at least one Pikachu back.
    let charmander_in_hand = count_named(&state.hands[0], "Charmander");
    let squirtle_in_hand = count_named(&state.hands[1], "Squirtle");
    assert!(
        charmander_in_hand < 2,
        "Player 0's hand should have been refreshed from their deck, got {charmander_in_hand} Charmander"
    );
    assert!(
        squirtle_in_hand < 3,
        "Player 1's hand should have been refreshed from their deck, got {squirtle_in_hand} Squirtle"
    );

    // Nothing is created or destroyed: the old hands are now somewhere in the decks.
    assert_eq!(
        charmander_in_hand + count_named(&state.decks[0].cards, "Charmander"),
        2
    );
    assert_eq!(
        squirtle_in_hand + count_named(&state.decks[1].cards, "Squirtle"),
        3
    );
}

fn count_named(cards: &[Card], name: &str) -> usize {
    cards.iter().filter(|card| card.get_name() == name).count()
}

/// Negative case: an empty hand (after Iono itself leaves it) means nothing is drawn back.
#[test]
fn test_iono_b2a_printing_with_empty_hands_draws_nothing() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let iono = make_trainer_card(CardId::B2a106Iono);
    state.hands[0] = vec![Card::Trainer(iono.clone())];
    state.hands[1] = vec![];
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1a025Pikachu); 8];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1a025Pikachu); 8];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: iono },
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert!(state.hands[1].is_empty());
    assert_eq!(state.decks[0].cards.len(), 8);
    assert_eq!(state.decks[1].cards.len(), 8);
}
