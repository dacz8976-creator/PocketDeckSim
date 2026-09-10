use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Purugly (A2 140) — Interrupt: "Your opponent reveals their hand. Choose a card you find there
/// and shuffle it into your opponent's deck." Unlike the random-discard attacks, the attacking
/// player picks which card leaves the hand.
fn interrupt_game(opponent_hand: &[CardId]) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A2140Purugly).with_energy(vec![EnergyType::Colorless; 3])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[1] = opponent_hand
        .iter()
        .copied()
        .map(get_card_by_enum)
        .collect();
    state.discard_piles[1] = vec![];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2140Purugly, 0),
        is_stack: false,
    });
    game
}

#[test]
fn test_interrupt_lets_the_attacker_pick_the_card_to_shuffle_away() {
    let mut game = interrupt_game(&[
        CardId::A1219Erika,
        CardId::A2b111PokeBall,
        CardId::A2147GiantCape,
    ]);
    let opponent_deck_before = game.get_state_clone().decks[1].cards.len();

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "the attacking player chooses the card");
    let choices: Vec<String> = actions
        .iter()
        .filter_map(|action| match &action.action {
            SimpleAction::ShuffleOpponentHandCard { card } => Some(card.get_name()),
            _ => None,
        })
        .collect();
    assert_eq!(
        choices.len(),
        3,
        "every card in the opponent's hand must be a legal choice, not only Supporters"
    );
    assert!(choices.contains(&"Giant Cape".to_string()));
    assert!(choices.contains(&"Poké Ball".to_string()));
    assert!(choices.contains(&"Erika".to_string()));

    let chosen = actions
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::ShuffleOpponentHandCard { card }
                if card.get_name() == "Poké Ball")
        })
        .expect("Poké Ball should be a choice");
    game.apply_action(&chosen);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 2);
    assert!(
        !state.hands[1]
            .iter()
            .any(|card| card.get_name() == "Poké Ball"),
        "the chosen card must leave the opponent's hand"
    );
    assert_eq!(state.decks[1].cards.len(), opponent_deck_before + 1);
    assert!(state.discard_piles[1].is_empty());
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);
}

#[test]
fn test_interrupt_does_nothing_extra_with_an_empty_opponent_hand() {
    let mut game = interrupt_game(&[]);
    let opponent_deck_before = game.get_state_clone().decks[1].cards.len();

    let (_, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        !actions
            .iter()
            .any(|action| matches!(action.action, SimpleAction::ShuffleOpponentHandCard { .. })),
        "no card can be chosen from an empty hand"
    );

    game.play_until_stable();
    let state = game.get_state_clone();
    assert!(state.hands[1].is_empty());
    assert_eq!(state.decks[1].cards.len(), opponent_deck_before);
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);
}
