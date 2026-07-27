use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Aegislash (B2 120) "Superb Shield": "During your opponent's next turn, this Pokémon takes -80
/// damage from attacks from your opponent's Pokémon ex."
fn aegislash() -> PlayedCard {
    PlayedCard::from_id(CardId::B2120Aegislash).with_energy(vec![
        EnergyType::Metal,
        EnergyType::Metal,
        EnergyType::Metal,
    ])
}

fn superb_shield(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2120Aegislash, 0),
        is_stack: false,
    });
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

#[test]
fn test_aegislash_superb_shield_reduces_damage_from_an_ex() {
    let mut game = get_test_game_with_board(
        vec![aegislash()],
        // Mega Latios ex: Sonic Impulse does a flat 160; Aegislash ([M]) is weak to [R], not [N].
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
        ],
    );

    superb_shield(&mut game);

    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        60,
        "Sonic Impulse should be cut from 160 to 80, leaving Aegislash at 140 - 80 = 60"
    );
}

/// Negative: the reduction is scoped to Pokémon ex. A non-ex attacker hits for full.
#[test]
fn test_aegislash_superb_shield_does_not_reduce_damage_from_a_non_ex() {
    let mut game = get_test_game_with_board(
        vec![aegislash()],
        // Melmetal's Heavy Impact does a flat 120 and Melmetal is not a Pokémon ex.
        vec![PlayedCard::from_id(CardId::A1182Melmetal).with_energy(vec![
            EnergyType::Metal,
            EnergyType::Metal,
            EnergyType::Metal,
            EnergyType::Colorless,
        ])],
    );

    superb_shield(&mut game);

    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::A1182Melmetal, 0),
        is_stack: false,
    });

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        20,
        "Heavy Impact should land its full 120 damage (140 - 120 = 20)"
    );
}
