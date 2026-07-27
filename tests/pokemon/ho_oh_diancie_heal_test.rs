use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    State,
};

/// Ho-Oh (B1 032) "Blessed Burn": 100 damage, then "Heal 30 damage from each of your Benched Basic
/// Pokémon."
fn blessed_burn(opponent_bench: Option<CardId>) -> State {
    let mut opponent_board = vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)];
    opponent_board.extend(opponent_bench.map(PlayedCard::from_id));

    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B1032HoOh)
                .with_energy(vec![
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Colorless,
                    EnergyType::Colorless,
                ])
                .with_damage(50),
            PlayedCard::from_id(CardId::A1053Squirtle).with_damage(40),
            PlayedCard::from_id(CardId::A1002Ivysaur).with_damage(40),
        ],
        opponent_board,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1032HoOh, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn test_blessed_burn_heals_only_benched_basic_pokemon() {
    let state = blessed_burn(None);

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        80,
        "Blessed Burn still does its printed 100"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        70,
        "Ho-Oh (120 HP) is Active, not Benched, so it keeps all 50 damage"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        50,
        "the Benched Basic Squirtle (60 HP) should heal 30 of its 40 damage"
    );
    assert_eq!(
        state.in_play_pokemon[0][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        50,
        "the Benched Stage 1 Ivysaur (90 HP) is not a Basic Pokémon and heals nothing"
    );
}

/// Negative case: Claydol's Heal Block stops the healing but not the damage.
#[test]
fn test_blessed_burn_healing_is_stopped_by_heal_block() {
    let state = blessed_burn(Some(CardId::A3a031Claydol));

    assert_eq!(state.get_active(1).get_remaining_hp(), 80);
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        20,
        "Heal Block should stop Blessed Burn's healing"
    );
}

/// Diancie (B3 067) "Diamond Storm": 50 damage, then "Heal 20 damage from each of your [P]
/// Pokémon" — Active and Bench alike, but only the Psychic ones.
fn diamond_storm(opponent_bench: Option<CardId>) -> State {
    let mut opponent_board = vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)];
    opponent_board.extend(opponent_bench.map(PlayedCard::from_id));

    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3067Diancie)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])
                .with_damage(50),
            PlayedCard::from_id(CardId::A1113Clefairy).with_damage(30),
            PlayedCard::from_id(CardId::A1053Squirtle).with_damage(30),
        ],
        opponent_board,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3067Diancie, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn test_diamond_storm_heals_every_psychic_pokemon_you_have() {
    let state = diamond_storm(None);

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        130,
        "Diamond Storm still does its printed 50"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        60,
        "Diancie (90 HP) is itself a [P] Pokémon and heals 20 of its 50 damage"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        50,
        "the Benched [P] Clefairy (60 HP) heals 20 of its 30 damage"
    );
    assert_eq!(
        state.in_play_pokemon[0][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        30,
        "the Benched [W] Squirtle (60 HP) is not a [P] Pokémon and heals nothing"
    );
}

#[test]
fn test_diamond_storm_healing_is_stopped_by_heal_block() {
    let state = diamond_storm(Some(CardId::A3a031Claydol));

    assert_eq!(state.get_active(1).get_remaining_hp(), 130);
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        40,
        "Heal Block should stop Diamond Storm's healing"
    );
}
