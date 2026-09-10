use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

fn tinkaton_board() -> deckgym::Game<'static> {
    get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B2a074Tinkaton).with_energy(vec![
                EnergyType::Metal,
                EnergyType::Metal,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            // Mega Latios ex: 180 HP, no weakness — survives 140 so the damage is readable and
            // Tinkaton stays in the Active Spot for the follow-up turn.
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    )
}

/// Tinkaton (B2a 074 / P-B 038) "Gigaton Hammer": 140 damage, and during your next turn this
/// Pokémon can't use Gigaton Hammer.
#[test]
fn test_tinkaton_gigaton_hammer_does_full_damage() {
    let mut game = tinkaton_board();

    let before = game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("opponent active should exist");

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a074Tinkaton, 0),
        is_stack: false,
    });

    let after = game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .expect("target must survive so the damage is readable, not truncated by a knockout")
        .get_remaining_hp();

    assert_eq!(before - after, 140, "Gigaton Hammer does 140 damage");
}

/// The self-lockout is the whole point of the card: after swinging, Gigaton Hammer must not be
/// offered again on the following turn, while other actions stay available.
#[test]
fn test_tinkaton_cannot_reuse_gigaton_hammer_next_turn() {
    let mut game = tinkaton_board();

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a074Tinkaton, 0),
        is_stack: false,
    });

    // Hand the turn back to player 0 with Tinkaton still Active and still fully charged.
    let mut state = game.get_state_clone();
    state.current_player = 0;
    game.set_state(state);

    let gigaton_hammer = attack_action(CardId::B2a074Tinkaton, 0);
    let (_, choices) = game.get_state_clone().generate_possible_actions();

    assert!(
        !choices
            .iter()
            .any(|choice| matches!(&choice.action, SimpleAction::Attack(attack) if
                matches!(&gigaton_hammer, SimpleAction::Attack(expected) if attack.title == expected.title))),
        "Gigaton Hammer must not be usable on the turn after it was used"
    );
}
