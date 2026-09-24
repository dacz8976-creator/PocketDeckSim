use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    State,
};

/// Builds an evolved Pokémon with a real evolution chain underneath it, the way one would look
/// after actually evolving in play.
fn evolved(card_id: CardId, behind: &[CardId], damage: u32) -> PlayedCard {
    let mut played = PlayedCard::from_id(card_id).with_damage(damage);
    played.cards_behind = behind.iter().copied().map(get_card_by_enum).collect();
    played
}

/// Celebi (A4a 006) "Temporal Leaves": 40 damage, then "If your opponent's Active Pokémon is an
/// evolved Pokémon, devolve it by putting the highest Stage Evolution card on it into your
/// opponent's hand."
fn temporal_leaves(defender: PlayedCard, opponent_bench: Option<CardId>) -> State {
    let mut opponent_board = vec![defender];
    opponent_board.extend(opponent_bench.map(PlayedCard::from_id));

    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a006Celebi)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
        opponent_board,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a006Celebi, 0),
        is_stack: false,
    });

    // Devolving into a lower-HP Pokémon can knock it out, which leaves a promotion to make.
    while !game.get_state_clone().move_generation_stack.is_empty() {
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        game.apply_action(&choices[0].clone());
    }

    game.get_state_clone()
}

#[test]
fn test_temporal_leaves_devolves_and_returns_the_top_card_to_hand() {
    let state = temporal_leaves(
        evolved(CardId::A1002Ivysaur, &[CardId::A1001Bulbasaur], 0),
        None,
    );

    assert_eq!(
        state.get_active(1).get_name(),
        "Bulbasaur",
        "Ivysaur should have devolved back into Bulbasaur"
    );
    assert!(
        state.hands[1]
            .iter()
            .any(|card| card.get_name() == "Ivysaur"),
        "the Ivysaur card should be in its owner's hand"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        30,
        "Bulbasaur has 70 HP and is carrying Ivysaur's 40 damage"
    );
}

/// Only the *highest* Stage card comes off: a Stage 2 devolves to Stage 1, not all the way down.
#[test]
fn test_temporal_leaves_removes_only_one_stage() {
    let state = temporal_leaves(
        evolved(
            CardId::A1003Venusaur,
            &[CardId::A1001Bulbasaur, CardId::A1002Ivysaur],
            0,
        ),
        None,
    );

    assert_eq!(state.get_active(1).get_name(), "Ivysaur");
    assert_eq!(
        state.in_play_pokemon[1][0]
            .as_ref()
            .unwrap()
            .cards_behind
            .len(),
        1,
        "Bulbasaur should still be underneath the Ivysaur"
    );
    assert!(state.hands[1]
        .iter()
        .any(|card| card.get_name() == "Venusaur"));
}

/// Devolving onto a lower-HP Pokémon can finish it off: Ivysaur is left with 80 damage, which is
/// more than Bulbasaur's 70 HP.
#[test]
fn test_temporal_leaves_can_knock_out_by_devolving() {
    let state = temporal_leaves(
        evolved(CardId::A1002Ivysaur, &[CardId::A1001Bulbasaur], 40),
        Some(CardId::A1033Charmander),
    );

    assert_eq!(
        state.get_active(1).get_name(),
        "Charmander",
        "the devolved Bulbasaur should have been knocked out and replaced"
    );
    assert_eq!(state.points[0], 1);
    assert!(state.hands[1]
        .iter()
        .any(|card| card.get_name() == "Ivysaur"));
}

/// Negative case: a Basic Pokémon is not an evolved Pokémon, so nothing but the damage happens.
#[test]
fn test_temporal_leaves_does_nothing_extra_against_a_basic_pokemon() {
    let state = temporal_leaves(PlayedCard::from_id(CardId::PB024MegaLatiosEx), None);

    assert_eq!(state.get_active(1).get_name(), "Mega Latios ex");
    assert_eq!(state.get_active(1).get_remaining_hp(), 140);
    assert!(
        state.hands[1].is_empty()
            || !state.hands[1]
                .iter()
                .any(|c| c.get_name() == "Mega Latios ex"),
        "nothing should be put into the opponent's hand"
    );
}
