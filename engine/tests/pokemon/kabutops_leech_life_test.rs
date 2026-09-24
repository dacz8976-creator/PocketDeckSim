use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    State,
};

/// Kabutops (A1 159 / B2 221) "Leech Life": 50 damage, then "Heal from this Pokémon the same
/// amount of damage you did to your opponent's Active Pokémon."
///
/// Kabutops has 140 HP and starts with 100 damage on it, so there is always room for the heal.
fn leech_life(card_id: CardId, defender: PlayedCard, opponent_bench: Option<CardId>) -> State {
    let mut opponent_board = vec![defender];
    opponent_board.extend(opponent_bench.map(PlayedCard::from_id));

    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(card_id)
            .with_energy(vec![EnergyType::Fighting])
            .with_damage(100)],
        opponent_board,
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });

    game.get_state_clone()
}

#[test]
fn test_leech_life_heals_the_damage_it_dealt() {
    let state = leech_life(
        CardId::A1159Kabutops,
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        None,
    );

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        130,
        "Mega Latios ex (180 HP, no Weakness) should take exactly 50"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        90,
        "Kabutops should heal the 50 it dealt: 140 - 100 + 50"
    );
}

/// The heal follows the damage that was actually done, Weakness included: Snorlax is weak to
/// Fighting, so Leech Life does 70 and Kabutops heals 70.
#[test]
fn test_leech_life_heals_the_weakness_boosted_damage() {
    let state = leech_life(
        CardId::B2221Kabutops,
        PlayedCard::from_id(CardId::A1211Snorlax),
        None,
    );

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        80,
        "Snorlax (150 HP, weak to Fighting) should take 50 + 20"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        110,
        "Kabutops should heal all 70 it dealt: 140 - 100 + 70"
    );
}

/// Overkill still heals the full amount: a defender left with 20 HP is knocked out by the 50, and
/// Kabutops heals 50 rather than the 20 that the defender's HP bar happened to have left.
#[test]
fn test_leech_life_heals_the_full_damage_even_when_it_knocks_out() {
    let state = leech_life(
        CardId::A1159Kabutops,
        PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_remaining_hp(20),
        Some(CardId::A1033Charmander),
    );

    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "the defender should be knocked out"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        90,
        "the heal should be the 50 damage dealt, not the 20 HP the defender had left"
    );
}

/// Negative case: Claydol's Heal Block ("Damage cannot be healed") stops the recovery, but not the
/// damage.
#[test]
fn test_leech_life_heal_is_stopped_by_heal_block() {
    let state = leech_life(
        CardId::A1159Kabutops,
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        Some(CardId::A3a031Claydol),
    );

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        130,
        "Heal Block does not stop the damage"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        40,
        "Heal Block should stop Leech Life's heal entirely"
    );
}
