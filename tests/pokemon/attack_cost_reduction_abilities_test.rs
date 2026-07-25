//! The conditional "attacks used by this Pokémon cost 1 less [X] Energy" abilities:
//! Vigor Link (Abomasnow A2a 021) and En-fruits-iastic (Cherubi A4 023 / A4b 025 / A4b 026).
//!
//! Both are driven through move generation: each board attaches exactly one Energy short of the
//! printed cost, so an `Attack` action is offered only when the discount actually applied. Each
//! ability gets a negative test for the case where its condition is absent.

use deckgym::{
    actions::SimpleAction,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::get_test_game_with_board,
    Game,
};

fn can_attack(game: &Game) -> bool {
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "Player 0 should be the one to act");
    actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Attack(_)))
}

// ---------------------------------------------------------------------------
// Vigor Link: "If you have Arceus or Arceus ex in play, attacks used by this Pokémon cost 1 less
// [C] Energy." Abomasnow's Mega Punch costs [W][W][C], so two [W] is one short.
// ---------------------------------------------------------------------------

fn abomasnow() -> PlayedCard {
    PlayedCard::from_id(CardId::A2a021Abomasnow)
        .with_energy(vec![EnergyType::Water, EnergyType::Water])
}

#[test]
fn test_vigor_link_discounts_attack_with_arceus_in_play() {
    let game = get_test_game_with_board(
        vec![abomasnow(), PlayedCard::from_id(CardId::A2a070Arceus)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_attack(&game),
        "Vigor Link should drop Mega Punch's [C] so two [W] pays for it"
    );
}

#[test]
fn test_vigor_link_accepts_arceus_ex_as_well() {
    let game = get_test_game_with_board(
        vec![abomasnow(), PlayedCard::from_id(CardId::A2a071ArceusEx)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_attack(&game),
        "Arceus ex should also satisfy Vigor Link"
    );
}

/// NEGATIVE: no Arceus, no discount.
#[test]
fn test_vigor_link_does_nothing_without_arceus() {
    let game = get_test_game_with_board(
        vec![abomasnow(), PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_attack(&game),
        "Without Arceus in play Mega Punch should still cost [W][W][C]"
    );
}

// ---------------------------------------------------------------------------
// En-fruits-iastic: "If this Pokémon has a Pokémon Tool attached, attacks used by this Pokémon
// cost 1 less [G] Energy." Cherubi's Sweets Relay costs a single [G], so a Tool makes it free.
// ---------------------------------------------------------------------------

#[test]
fn test_en_fruits_iastic_discounts_attack_with_a_tool_attached() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4023Cherubi)
            .with_tool(get_card_by_enum(CardId::A2147GiantCape))],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        can_attack(&game),
        "A Tool should remove Sweets Relay's only [G], letting Cherubi attack with no Energy"
    );
}

/// NEGATIVE: no Tool, no discount.
#[test]
fn test_en_fruits_iastic_does_nothing_without_a_tool() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4023Cherubi)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_attack(&game),
        "Without a Tool attached Sweets Relay should still cost [G]"
    );
}

/// The discount is self-scoped: a Tool on a Benched Cherubi does not pay for the Active one.
#[test]
fn test_en_fruits_iastic_does_not_discount_from_the_bench() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4b025Cherubi),
            PlayedCard::from_id(CardId::A4b026Cherubi)
                .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    assert!(
        !can_attack(&game),
        "En-fruits-iastic only discounts attacks used by the Pokémon holding the Tool"
    );
}
