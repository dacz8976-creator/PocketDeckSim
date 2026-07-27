use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

/// Tyrantrum's Tyrannical Fang: 100, +80 if you have fewer Pokémon in play than the
/// opponent. With the bonus it KOs the 180 HP Mega Latios ex outright.
#[test]
fn test_tyrannical_fang_extra_damage_when_outnumbered() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2090Tyrantrum).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Fighting,
            ]),
        ],
        vec![sponge(), PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2090Tyrantrum, 0),
        is_stack: false,
    });
    // 100 + 80 = 180 exactly KOs Mega Latios ex (a Mega ex: 3 points).
    let state = game.get_state_clone();
    assert_eq!(
        state.points[0], 3,
        "Tyrannical Fang should deal 180 while outnumbered, KO'ing the 180 HP ex"
    );
}

/// Negative: equal board sizes → base 100 only.
#[test]
fn test_tyrannical_fang_base_damage_with_equal_boards() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2090Tyrantrum).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Fighting,
            ]),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
        vec![sponge(), PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2090Tyrantrum, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 80,
        "Tyrannical Fang should deal 100 with equally sized boards"
    );
}

/// Buzzwole's Ground Beat: 40, +40 if the opponent has gotten exactly 1 point.
#[test]
fn test_ground_beat_extra_damage_at_exactly_one_opponent_point() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2014Buzzwole)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.points[1] = 1;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2014Buzzwole, 0),
        is_stack: false,
    });
    // 180 - 80 = 100.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 100,
        "Ground Beat should deal 80 when the opponent has exactly 1 point"
    );
}

/// Negative: at 0 (or 2) opponent points, Ground Beat deals only its base 40.
#[test]
fn test_ground_beat_base_damage_at_other_point_totals() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2014Buzzwole)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.points[1] = 2;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2014Buzzwole, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 140,
        "Ground Beat should deal 40 when the opponent does not have exactly 1 point"
    );
}

/// Drampa's Berserk: 20, +50 if any of your BENCHED Pokémon have damage on them.
#[test]
fn test_berserk_extra_damage_with_damaged_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3124Drampa)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A1211Snorlax).with_damage(30),
        ],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3124Drampa, 0),
        is_stack: false,
    });
    // 180 - 70 = 110.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 110,
        "Berserk should deal 70 with a damaged benched Pokémon"
    );
}

/// Negative: damage on Drampa itself (the Active) does not count — only the Bench does.
#[test]
fn test_berserk_base_damage_with_healthy_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3124Drampa)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])
                .with_damage(30),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3124Drampa, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 160,
        "Berserk should deal 20 when only the Active (not the Bench) is damaged"
    );
}
