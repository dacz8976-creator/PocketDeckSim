//! Integration tests for the passive "no Retreat Cost" ability family:
//! Speed Link (Heatran / Rotom), Fluffy Flight (Jumpluff), Fantastical Floating (Latios),
//! Retreat Directive (Tatsugiri), Surge Surfer (Alolan Raichu) and Wimp Out (Wimpod).
//!
//! Every one of these is conditional, so each ability gets a positive test (the condition holds,
//! so the Active Pokemon can retreat with no Energy attached) and a negative test (the condition
//! is absent, so retreating is impossible without Energy).

use deckgym::{
    actions::SimpleAction,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::{get_initialized_game_with_board, get_test_game_with_board},
    Game,
};

/// True if the current player is offered a free retreat to bench slot 1. The boards below never
/// attach Energy to the Active Pokemon, so a retreat is only ever generated when the retreat cost
/// has been reduced to nothing.
fn can_retreat_for_free(game: &Game) -> bool {
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "Player 0 should be the one to act");
    actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(1)))
}

fn game_with_stadium(
    player_board: Vec<PlayedCard>,
    opponent_board: Vec<PlayedCard>,
    stadium: Option<Card>,
) -> Game<'static> {
    let mut game = get_test_game_with_board(player_board, opponent_board);
    if let Some(stadium) = stadium {
        let mut state = game.get_state_clone();
        state.set_active_stadium(stadium);
        game.set_state(state);
    }
    game
}

// ---------------------------------------------------------------------------
// Speed Link: "If you have Arceus or Arceus ex in play, this Pokémon has no Retreat Cost."
// ---------------------------------------------------------------------------

#[test]
fn test_heatran_speed_link_frees_retreat_with_arceus_in_play() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2a013Heatran),
            PlayedCard::from_id(CardId::A2a070Arceus),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "Speed Link should let Heatran retreat for free while Arceus is in play"
    );
}

#[test]
fn test_heatran_speed_link_does_nothing_without_arceus() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2a013Heatran),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_retreat_for_free(&game),
        "Without Arceus in play Heatran should still owe its 3 Colorless Retreat Cost"
    );
}

#[test]
fn test_rotom_speed_link_frees_retreat_with_arceus_ex_in_play() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2a035Rotom),
            PlayedCard::from_id(CardId::A2a071ArceusEx),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "Arceus ex should also satisfy Speed Link"
    );
}

// ---------------------------------------------------------------------------
// Fluffy Flight: "Your Active Pokémon has no Retreat Cost."
// ---------------------------------------------------------------------------

#[test]
fn test_jumpluff_fluffy_flight_frees_active_from_bench() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1055Blastoise),
            PlayedCard::from_id(CardId::A4015Jumpluff),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "A Benched Jumpluff should remove the Active Pokemon's Retreat Cost"
    );
}

#[test]
fn test_jumpluff_fluffy_flight_frees_itself_while_active() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4b018Jumpluff),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "Jumpluff is itself an Active Pokemon, so Fluffy Flight applies to it too"
    );
}

#[test]
fn test_active_still_pays_retreat_without_jumpluff() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1055Blastoise),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_retreat_for_free(&game),
        "Without Jumpluff in play Blastoise should still owe its Retreat Cost"
    );
}

// ---------------------------------------------------------------------------
// Fantastical Floating: "If you have Latias in play, this Pokémon has no Retreat Cost."
// ---------------------------------------------------------------------------

#[test]
fn test_latios_fantastical_floating_frees_retreat_with_latias_in_play() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4a037Latios),
            PlayedCard::from_id(CardId::A4a036Latias),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "Fantastical Floating should free Latios while Latias is in play"
    );
}

#[test]
fn test_latios_fantastical_floating_does_nothing_without_latias() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2217Latios),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_retreat_for_free(&game),
        "Without Latias in play Latios should still owe its 2 Colorless Retreat Cost"
    );
}

// ---------------------------------------------------------------------------
// Retreat Directive: "Your Active Dondozo has no Retreat Cost."
// ---------------------------------------------------------------------------

#[test]
fn test_tatsugiri_retreat_directive_frees_active_dondozo() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2b020Dondozo),
            PlayedCard::from_id(CardId::A2b021Tatsugiri),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "Retreat Directive should free an Active Dondozo"
    );
}

#[test]
fn test_tatsugiri_retreat_directive_does_not_free_other_active() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1055Blastoise),
            PlayedCard::from_id(CardId::A2b075Tatsugiri),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_retreat_for_free(&game),
        "Retreat Directive only names Dondozo, so Blastoise still owes its Retreat Cost"
    );
}

// ---------------------------------------------------------------------------
// Surge Surfer: "If a Stadium is in play, this Pokémon has no Retreat Cost."
// ---------------------------------------------------------------------------

#[test]
fn test_alolan_raichu_surge_surfer_frees_retreat_with_stadium_in_play() {
    let game = game_with_stadium(
        vec![
            PlayedCard::from_id(CardId::B2050AlolanRaichu),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        Some(get_card_by_enum(CardId::B2153TrainingArea)),
    );

    assert!(
        can_retreat_for_free(&game),
        "Surge Surfer should free Alolan Raichu while a Stadium is in play"
    );
}

#[test]
fn test_alolan_raichu_surge_surfer_does_nothing_without_stadium() {
    let game = game_with_stadium(
        vec![
            PlayedCard::from_id(CardId::B2050AlolanRaichu),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        None,
    );

    assert!(
        !can_retreat_for_free(&game),
        "With no Stadium in play Alolan Raichu should still owe its Retreat Cost"
    );
}

// ---------------------------------------------------------------------------
// Wimp Out: "During your first turn, this Pokémon has no Retreat Cost."
// ---------------------------------------------------------------------------

#[test]
fn test_wimpod_wimp_out_frees_retreat_on_first_turn() {
    let game = get_initialized_game_with_board(
        0,
        0,
        1,
        vec![
            PlayedCard::from_id(CardId::A3021Wimpod),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_retreat_for_free(&game),
        "Wimp Out should free Wimpod during its owner's first turn"
    );
}

#[test]
fn test_wimpod_wimp_out_does_nothing_after_first_turn() {
    let game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A3021Wimpod),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_retreat_for_free(&game),
        "After the first turn Wimpod should owe its 3 Colorless Retreat Cost again"
    );
}
