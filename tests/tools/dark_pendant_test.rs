use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

/// Dark Pendant (A4 154): "If the [D] Pokémon this card is attached to is in the Active Spot and
/// is damaged by an attack from your opponent's Pokémon, your opponent reveals a random card from
/// their hand and shuffles it into their deck."
///
/// Player 0 is the attacker; player 1 holds the Dark Pendant, so it is player 0's hand that gets
/// disrupted.
fn game_with_pendant_on(
    holder: CardId,
    holder_is_active: bool,
    attacker_hand: usize,
) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    let pendant = PlayedCard::from_id(holder).with_tool(get_card_by_enum(CardId::A4154DarkPendant));
    let defender_board = if holder_is_active {
        vec![pendant, PlayedCard::from_id(CardId::A1001Bulbasaur)]
    } else {
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), pendant]
    };
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        defender_board,
    );
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::A1225Sabrina); attacker_hand];
    state.decks[0].cards = vec![get_card_by_enum(CardId::PA005PokeBall); 10];
    game.set_state(state);
    game
}

fn attack_target(game: &mut Game<'static>, target_in_play_idx: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(30, 1, target_in_play_idx)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
}

fn take_shuffle_action(game: &mut Game<'static>) -> bool {
    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let Some(shuffle) = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::ShuffleRandomOpponentHandCard))
        .cloned()
    else {
        return false;
    };
    game.apply_action(&shuffle);
    true
}

#[test]
fn test_dark_pendant_shuffles_a_random_attacker_hand_card_into_their_deck() {
    // Guzzlord (B2 109) is a [D] Pokémon with 150 HP, so it survives the hit.
    let mut game = game_with_pendant_on(CardId::B2109Guzzlord, true, 3);

    attack_target(&mut game, 0);
    assert!(
        take_shuffle_action(&mut game),
        "Dark Pendant should fire when a [D] holder in the Active Spot is damaged"
    );

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[0].len(),
        2,
        "one card should have left the hand"
    );
    assert_eq!(
        state.decks[0].cards.len(),
        11,
        "and it should be back in the deck"
    );
    assert!(
        state.decks[0]
            .cards
            .iter()
            .any(|card| matches!(card, Card::Trainer(t) if t.name == "Sabrina")),
        "the shuffled card should be the one taken from the hand"
    );
}

/// NEGATIVE: the tool only works on a [D] holder.
#[test]
fn test_dark_pendant_does_nothing_on_a_non_darkness_holder() {
    // Bulbasaur is [G].
    let mut game = game_with_pendant_on(CardId::A1001Bulbasaur, true, 3);

    attack_target(&mut game, 0);
    assert!(
        !take_shuffle_action(&mut game),
        "Dark Pendant must not fire for a non-[D] holder"
    );
    assert_eq!(game.get_state_clone().hands[0].len(), 3);
}

/// NEGATIVE: the tool only works while the holder is in the Active Spot.
#[test]
fn test_dark_pendant_does_nothing_while_benched() {
    let mut game = game_with_pendant_on(CardId::B2109Guzzlord, false, 3);

    attack_target(&mut game, 1);
    assert!(
        !take_shuffle_action(&mut game),
        "Dark Pendant must not fire from the Bench"
    );
    assert_eq!(game.get_state_clone().hands[0].len(), 3);
}

/// NEGATIVE: nothing to reveal when the attacker's hand is empty.
#[test]
fn test_dark_pendant_does_nothing_against_an_empty_hand() {
    let mut game = game_with_pendant_on(CardId::B2109Guzzlord, true, 0);

    attack_target(&mut game, 0);
    assert!(!take_shuffle_action(&mut game));
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.decks[0].cards.len(), 10);
}
