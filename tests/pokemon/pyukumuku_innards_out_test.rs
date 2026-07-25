use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Pyukumuku (A3 054 / A3 163 / A4a 097) "Innards Out": "If this Pokémon is in the Active Spot
/// and is Knocked Out by damage from an attack from your opponent's Pokémon, do 50 damage to the
/// Attacking Pokémon."
///
/// Mega Latios ex (180 HP, no weakness) is used as the attacker so the retaliation is visible as
/// a plain HP delta — a smaller attacker would be Knocked Out and `hp_before - hp_after` would
/// silently cap at its remaining HP.
#[test]
fn test_innards_out_damages_the_attacking_pokemon() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A3054Pyukumuku),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "Pyukumuku should be Knocked Out by the attack"
    );
    assert_eq!(state.points[0], 1, "the attacker still scores the knockout");

    let attacker = state.in_play_pokemon[0][0]
        .as_ref()
        .expect("Mega Latios ex survives 50 retaliation damage");
    assert_eq!(
        attacker.get_remaining_hp(),
        180 - 50,
        "Innards Out should do 50 damage to the Attacking Pokémon"
    );
}

/// Innards Out is a knockout trigger: damage that leaves Pyukumuku alive must not retaliate.
#[test]
fn test_innards_out_does_not_trigger_without_a_knockout() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::A3054Pyukumuku),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        60 - 40,
        "Vine Whip should leave Pyukumuku alive"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        70,
        "Innards Out must not fire when Pyukumuku survives"
    );
}

/// Innards Out only triggers from the Active Spot: a benched Pyukumuku Knocked Out by spread
/// damage must not damage the attacker.
#[test]
fn test_innards_out_does_not_trigger_from_the_bench() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A2104Spiritomb).with_energy(vec![EnergyType::Darkness])],
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            // 10 HP left, so Swirling Disaster's 10 spread damage Knocks it out on the bench.
            PlayedCard::from_id(CardId::A3054Pyukumuku).with_remaining_hp(10),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2104Spiritomb, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][1].is_none(),
        "the benched Pyukumuku should be Knocked Out"
    );
    assert_eq!(state.points[0], 1);
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        80,
        "Innards Out must not fire from the bench"
    );
}

/// A knockout that finishes the attacker: Innards Out's 50 damage is enough to Knock Out a
/// Charmander that attacked with only 30 HP left, which scores a point for Pyukumuku's owner and
/// forces the attacker to promote.
#[test]
fn test_innards_out_can_knock_out_the_attacker() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])
                .with_remaining_hp(30),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A3054Pyukumuku).with_remaining_hp(30),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "Pyukumuku should be Knocked Out"
    );
    assert!(
        state.in_play_pokemon[0][0].is_none(),
        "Innards Out should Knock Out the 30 HP attacker"
    );
    assert_eq!(state.points, [1, 1], "both knockouts should score");

    // Both players still have a Pokémon on the bench, so both are asked to promote.
    let (_, choices) = state.generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|choice| matches!(choice.action, SimpleAction::Activate { .. })),
        "a promotion is pending after the mutual knockout"
    );
}
