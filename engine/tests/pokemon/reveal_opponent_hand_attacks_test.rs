use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// "Your opponent reveals their hand." has no mechanical consequence in this engine (both players
/// already see the full state), so these attacks must resolve as plain damage and leave both
/// hands untouched. Mew (A1 283 / A1a 031) Psy Report and Noctowl (A2a 065) Silent Wing.
#[test]
fn test_reveal_opponent_hand_only_deals_damage() {
    let printings = [
        (CardId::A1283Mew, vec![EnergyType::Psychic], 20),
        (CardId::A1a031Mew, vec![EnergyType::Psychic], 20),
        (CardId::A2a065Noctowl, vec![EnergyType::Colorless; 2], 50),
    ];

    for (card_id, energy, damage) in printings {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![PlayedCard::from_id(card_id).with_energy(energy)],
            vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
        );
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A1219Erika)];
        state.hands[1] = vec![
            get_card_by_enum(CardId::A2b111PokeBall),
            get_card_by_enum(CardId::A2147GiantCape),
        ];
        state.discard_piles[1] = vec![];
        let deck_len_before = state.decks[1].cards.len();
        game.set_state(state);

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(card_id, 0),
            is_stack: false,
        });
        game.play_until_stable();

        let state = game.get_state_clone();
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            180 - damage,
            "{card_id:?} should deal its printed damage"
        );
        assert_eq!(
            state.hands[1].len(),
            2,
            "{card_id:?}: revealing a hand must not move any cards"
        );
        assert_eq!(state.hands[0].len(), 1);
        assert!(state.discard_piles[1].is_empty());
        assert_eq!(state.decks[1].cards.len(), deck_len_before);
    }
}
