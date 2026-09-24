use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Machop (B2 079) "Shatter": "Discard a Stadium in play."
fn game_with_machop() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2079Machop).with_energy(vec![EnergyType::Colorless])],
        // 180 HP, no Weakness.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    )
}

fn shatter(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2079Machop, 0),
        is_stack: false,
    });
}

#[test]
fn test_machop_shatter_discards_the_stadium_to_its_owners_discard_pile() {
    let mut game = game_with_machop();
    let mut state = game.get_state_clone();
    let training_area = get_card_by_enum(CardId::B2153TrainingArea);
    state.active_stadium = Some(training_area.clone());
    state.active_stadium_owner = Some(1);
    game.set_state(state);

    shatter(&mut game);

    let state = game.get_state_clone();
    assert!(
        state.active_stadium.is_none(),
        "Shatter should remove the Stadium from play"
    );
    assert!(
        state.discard_piles[1].contains(&training_area),
        "the Stadium should go to the discard pile of the player who played it"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        170,
        "Shatter still does its printed 10 damage"
    );
}

/// Negative: with no Stadium in play the attack is just its printed damage.
#[test]
fn test_machop_shatter_with_no_stadium_in_play() {
    let mut game = game_with_machop();
    let mut state = game.get_state_clone();
    state.active_stadium = None;
    state.active_stadium_owner = None;
    game.set_state(state);

    shatter(&mut game);

    let state = game.get_state_clone();
    assert!(state.active_stadium.is_none());
    assert!(
        state.discard_piles[0].is_empty() && state.discard_piles[1].is_empty(),
        "nothing should be discarded when there is no Stadium in play"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 170);
}
