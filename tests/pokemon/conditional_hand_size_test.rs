use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

fn hand_of(n: usize) -> Vec<Card> {
    vec![get_card_by_enum(CardId::A1001Bulbasaur); n]
}

/// Ludicolo's Rhythmic Steps: 60, +60 if you have exactly 1, 3, or 5 cards in your hand.
#[test]
fn test_rhythmic_steps_extra_damage_with_odd_hand_size() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1055Ludicolo)
            .with_energy(vec![EnergyType::Water, EnergyType::Water])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand_of(3);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1055Ludicolo, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 60,
        "Rhythmic Steps should deal 120 with 3 cards in hand"
    );
}

/// Negative: a hand size outside {1, 3, 5} leaves Rhythmic Steps at its base 60.
#[test]
fn test_rhythmic_steps_base_damage_with_even_hand_size() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1055Ludicolo)
            .with_energy(vec![EnergyType::Water, EnergyType::Water])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand_of(4);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1055Ludicolo, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 120,
        "Rhythmic Steps should deal 60 with 4 cards in hand"
    );
}

/// Luvdisc's Paired Tackle: 30, +30 if you have exactly 2, 4, or 6 cards in your hand.
#[test]
fn test_paired_tackle_extra_damage_with_even_hand_size() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1060Luvdisc)
            .with_energy(vec![EnergyType::Water, EnergyType::Water])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand_of(2);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1060Luvdisc, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 120, "Paired Tackle should deal 60 with 2 cards in hand");
}

/// Negative: a hand size outside {2, 4, 6} leaves Paired Tackle at its base 30.
#[test]
fn test_paired_tackle_base_damage_with_odd_hand_size() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1060Luvdisc)
            .with_energy(vec![EnergyType::Water, EnergyType::Water])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand_of(3);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1060Luvdisc, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 150, "Paired Tackle should deal 30 with 3 cards in hand");
}

/// Grumpig's Swaying Dance: 40, +40 if your OPPONENT has exactly 2, 4, or 6 cards in
/// their hand. The attacker's own hand size must not matter.
#[test]
fn test_swaying_dance_extra_damage_with_opponent_even_hand() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2b032Grumpig).with_energy(vec![EnergyType::Psychic])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand_of(3); // own odd hand must not block the bonus
    state.hands[1] = hand_of(4);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2b032Grumpig, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 100,
        "Swaying Dance should deal 80 with 4 cards in the opponent's hand"
    );
}

/// Negative: the opponent holding an odd number of cards leaves Swaying Dance at 40, even
/// when the attacker's own hand size is in {2, 4, 6}.
#[test]
fn test_swaying_dance_base_damage_with_opponent_odd_hand() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2b032Grumpig).with_energy(vec![EnergyType::Psychic])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand_of(4);
    state.hands[1] = hand_of(5);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2b032Grumpig, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 140,
        "Swaying Dance should deal 40 with 5 cards in the opponent's hand"
    );
}
