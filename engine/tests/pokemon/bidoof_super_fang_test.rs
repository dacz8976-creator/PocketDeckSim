use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    State,
};

/// Bidoof (A2 135 / A2 177 / B1 316) "Super Fang": "Halve your opponent's Active Pokémon's
/// remaining HP, rounded down."
///
/// Mega Latios ex (180 HP, no Weakness) is the damage sponge so nothing is lost to a Weakness
/// bonus or an early knockout.
fn super_fang_against(remaining_hp: u32) -> State {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2135Bidoof)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_remaining_hp(remaining_hp),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2135Bidoof, 0),
        is_stack: false,
    });

    game.get_state_clone()
}

#[test]
fn test_super_fang_halves_an_undamaged_pokemon() {
    let state = super_fang_against(180);
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        90,
        "180 HP should be halved to 90"
    );
}

/// Half of 90 is 45, which is not on the 10s grid every HP and damage value in this game lives on,
/// so "rounded down" takes it to 40.
#[test]
fn test_super_fang_rounds_down_to_the_nearest_ten() {
    let state = super_fang_against(90);
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        40,
        "90 HP halved and rounded down should be 40, not 45"
    );
}

/// Super Fang is an effect rather than damage, so it is unaffected by Weakness: Snorlax is weak to
/// Fighting, but Bidoof is Colorless anyway — the point is that the result is exactly half its
/// remaining HP and not "half plus 20".
#[test]
fn test_super_fang_is_not_damage_and_ignores_damage_modifiers() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2177Bidoof)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2177Bidoof, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        70,
        "Snorlax's 150 HP should be halved to 70 (75 rounded down), with no Weakness bonus"
    );
}

/// A Pokémon down to its last 10 HP is taken to 0 and knocked out, which is worth a point.
#[test]
fn test_super_fang_knocks_out_a_pokemon_left_with_ten_hp() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2135Bidoof)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax).with_remaining_hp(10),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2135Bidoof, 0),
        is_stack: false,
    });

    assert!(
        game.get_state_clone().in_play_pokemon[1][0].is_none(),
        "a Pokémon left with 10 HP should be knocked out by Super Fang"
    );
    assert_eq!(game.get_state_clone().points[0], 1);

    // The opponent still has to promote from their Bench.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1);
    game.apply_action(&choices[0].clone());
    assert_eq!(
        game.get_state_clone().get_active(1).get_name(),
        "Charmander"
    );
}

/// All three printings of Bidoof share the same Super Fang effect text.
#[test]
fn test_all_bidoof_printings_use_super_fang() {
    for card_id in [
        CardId::A2135Bidoof,
        CardId::A2177Bidoof,
        CardId::B1316Bidoof,
    ] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(card_id)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
            vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
        );
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(card_id, 0),
            is_stack: false,
        });
        assert_eq!(
            game.get_state_clone().get_active(1).get_remaining_hp(),
            90,
            "{card_id:?} should halve the defender's remaining HP"
        );
    }
}
