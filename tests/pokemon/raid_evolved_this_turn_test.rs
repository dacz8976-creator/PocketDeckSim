use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

/// Politoed's Raid: 50, +50 if this Pokémon evolved from Poliwhirl during this turn.
#[test]
fn test_politoed_raid_boosted_when_evolved_this_turn() {
    let mut politoed =
        PlayedCard::from_id(CardId::B3035Politoed).with_energy(vec![EnergyType::Water]);
    politoed.played_this_turn = true; // evolved this turn

    let mut game = get_test_game_with_board(vec![politoed], vec![sponge()]);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3035Politoed, 0),
        is_stack: false,
    });
    // 180 - 100 = 80.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 80, "Raid should deal 100 on the turn Politoed evolved");
}

/// Negative: on later turns, Politoed's Raid deals only its base 50.
#[test]
fn test_politoed_raid_base_damage_on_later_turns() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3035Politoed).with_energy(vec![EnergyType::Water])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3035Politoed, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 130,
        "Raid should deal 50 when Politoed did not evolve this turn"
    );
}

/// Weavile's Raid: 40, +20 if this Pokémon evolved from Sneasel during this turn (same
/// mechanic as Politoed with different parameters).
#[test]
fn test_weavile_raid_boosted_when_evolved_this_turn() {
    let mut weavile =
        PlayedCard::from_id(CardId::B3a039Weavile).with_energy(vec![EnergyType::Darkness]);
    weavile.played_this_turn = true; // evolved this turn

    let mut game = get_test_game_with_board(vec![weavile], vec![sponge()]);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a039Weavile, 0),
        is_stack: false,
    });
    // 180 - 60 = 120.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(hp, 120, "Raid should deal 60 on the turn Weavile evolved");
}

/// Negative: on later turns, Weavile's Raid deals only its base 40.
#[test]
fn test_weavile_raid_base_damage_on_later_turns() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a039Weavile).with_energy(vec![EnergyType::Darkness])],
        vec![sponge()],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a039Weavile, 0),
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 140,
        "Raid should deal 40 when Weavile did not evolve this turn"
    );
}
