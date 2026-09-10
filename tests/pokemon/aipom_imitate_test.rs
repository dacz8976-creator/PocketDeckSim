use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Aipom (A4 142) — Imitate: "Draw cards until you have the same number of cards in your hand as
/// your opponent."
fn imitate_hand_sizes(own_hand: usize, opponent_hand: usize) -> (usize, usize, usize) {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A4142Aipom).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1219Erika); own_hand];
    state.hands[1] = vec![get_card_by_enum(CardId::A2b111PokeBall); opponent_hand];
    let deck_len_before = state.decks[0].cards.len();
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4142Aipom, 0),
        is_stack: false,
    });
    game.play_until_stable();

    let state = game.get_state_clone();
    (
        state.hands[0].len(),
        state.decks[0].cards.len(),
        deck_len_before,
    )
}

#[test]
fn test_imitate_draws_up_to_the_opponents_hand_size() {
    let (hand_after, deck_after, deck_before) = imitate_hand_sizes(2, 6);
    assert_eq!(hand_after, 6, "should draw 4 cards to match the opponent");
    assert_eq!(deck_after, deck_before - 4);
}

#[test]
fn test_imitate_draws_nothing_when_hands_are_already_equal() {
    let (hand_after, deck_after, deck_before) = imitate_hand_sizes(4, 4);
    assert_eq!(hand_after, 4);
    assert_eq!(deck_after, deck_before, "no cards drawn when hands match");
}

#[test]
fn test_imitate_draws_nothing_when_you_have_more_cards() {
    let (hand_after, deck_after, deck_before) = imitate_hand_sizes(7, 3);
    assert_eq!(
        hand_after, 7,
        "Imitate never discards; a bigger hand simply stays as it is"
    );
    assert_eq!(deck_after, deck_before);
}
