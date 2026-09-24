use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::get_initialized_game,
};

/// Porygon2 (A4 136) Buggy Evolution:
/// "Whenever you attach an Energy from your Energy Zone to this Pokémon, put a random card from
/// your deck that evolves from this Pokémon onto this Pokémon to evolve it."
fn game_with_porygon2(deck: Vec<Card>) -> deckgym::Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A4136Porygon2),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.current_player = 0;
    state.decks[0].cards = deck;
    game.set_state(state);
    game
}

#[test]
fn test_buggy_evolution_evolves_on_energy_zone_attach() {
    let mut game = game_with_porygon2(vec![get_card_by_enum(CardId::A4137PorygonZ)]);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Colorless, 0)],
            is_turn_energy: true,
        },
        is_stack: false,
    });

    let state = game.get_state_clone();
    let active = state.get_active(0);
    assert_eq!(
        active.get_name(),
        "Porygon-Z",
        "Buggy Evolution should evolve Porygon2 when Energy is attached from the Energy Zone"
    );
    assert_eq!(
        active.attached_energy,
        vec![EnergyType::Colorless],
        "The attached Energy should carry over to the evolution"
    );
    assert!(
        state.decks[0].cards.is_empty(),
        "Porygon-Z should have left the deck"
    );
}

/// Negative case: nothing in the deck evolves from Porygon2, so the attach is an ordinary attach.
#[test]
fn test_buggy_evolution_no_op_without_evolution_in_deck() {
    let mut game = game_with_porygon2(vec![get_card_by_enum(CardId::A1001Bulbasaur)]);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Colorless, 0)],
            is_turn_energy: true,
        },
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_name(),
        "Porygon2",
        "Porygon2 should stay unevolved when the deck has no card that evolves from it"
    );
    assert_eq!(state.decks[0].cards.len(), 1);
}

/// Negative case: the trigger is "an Energy from your Energy Zone to *this* Pokémon" — attaching
/// to a different Pokémon must not evolve Porygon2.
#[test]
fn test_buggy_evolution_does_not_trigger_on_attach_to_other_pokemon() {
    let mut game = game_with_porygon2(vec![get_card_by_enum(CardId::A4137PorygonZ)]);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Colorless, 1)],
            is_turn_energy: true,
        },
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_name(),
        "Porygon2",
        "Attaching to the Bench should not trigger Buggy Evolution"
    );
    assert_eq!(state.decks[0].cards.len(), 1);
}
