use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Chatot (A1a 062) — Mimic: "Shuffle your hand into your deck. Draw a card for each card in your
/// opponent's hand."
struct MimicResult {
    hand_after: usize,
    deck_after: usize,
    deck_before: usize,
    discard_after: usize,
}

fn mimic(own_hand: usize, opponent_hand: usize) -> MimicResult {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1a062Chatot).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1219Erika); own_hand];
    state.hands[1] = vec![get_card_by_enum(CardId::A2b111PokeBall); opponent_hand];
    state.discard_piles[0] = vec![];
    let deck_before = state.decks[0].cards.len();
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1a062Chatot, 0),
        is_stack: false,
    });
    game.play_until_stable();

    let state = game.get_state_clone();
    MimicResult {
        hand_after: state.hands[0].len(),
        deck_after: state.decks[0].cards.len(),
        deck_before,
        discard_after: state.discard_piles[0].len(),
    }
}

#[test]
fn test_mimic_shuffles_hand_back_and_draws_opponent_hand_size() {
    let result = mimic(4, 2);
    assert_eq!(
        result.hand_after, 2,
        "draws exactly 1 card per opponent hand card"
    );
    assert_eq!(
        result.deck_after,
        result.deck_before + 4 - 2,
        "4 cards go back into the deck, then 2 are drawn"
    );
    assert_eq!(
        result.deck_after + result.hand_after,
        result.deck_before + 4,
        "no card may be lost: the hand is shuffled in, not discarded"
    );
    assert_eq!(
        result.discard_after, 0,
        "Mimic shuffles the hand into the deck, it never discards it"
    );
}

#[test]
fn test_mimic_with_empty_opponent_hand_draws_nothing() {
    let result = mimic(3, 0);
    assert_eq!(
        result.hand_after, 0,
        "an empty opponent hand means no cards are drawn back"
    );
    assert_eq!(result.deck_after, result.deck_before + 3);
    assert_eq!(result.discard_after, 0);
}
