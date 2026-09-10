use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Oricorio (B2 022 / 161) "Inspiring Dance": "During your next turn, attacks used by your Pokémon
/// do +20 damage to your opponent's Active Pokémon."
/// Meloetta (B3 089 / 170) prints the same attack scoped to [F] Pokémon, for +30.
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

#[test]
fn test_oricorio_inspiring_dance_boosts_your_attack_next_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2022Oricorio).with_energy(vec![EnergyType::Fire])],
        // 180 HP, no Weakness: damage is readable straight off the remaining HP.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    let dance = Action {
        actor: 0,
        action: attack_action(CardId::B2022Oricorio, 0),
        is_stack: false,
    };
    game.apply_action(&dance);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        170,
        "Inspiring Dance itself does its printed 10 damage, with no bonus on the turn it is used"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    game.apply_action(&dance);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        140,
        "on the following turn the attack should do 10 + 20 = 30 damage"
    );
}

/// Negative: the boost belongs to Oricorio's controller. The opponent's attacks during the turn in
/// between must be untouched.
#[test]
fn test_oricorio_inspiring_dance_does_not_boost_the_opponents_attacks() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2022Oricorio).with_energy(vec![EnergyType::Fire])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2022Oricorio, 0),
        is_stack: false,
    });
    end_turn(&mut game, 0);

    // Bulbasaur's Vine Whip does a flat 40; Oricorio is [R] and is not weak to [G].
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        30,
        "Vine Whip should do its plain 40 damage (70 - 40); the +20 is only for Oricorio's side"
    );
}

#[test]
fn test_meloetta_inspiring_dance_boosts_your_fighting_attacker_next_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3089Meloetta)
            .with_energy(vec![EnergyType::Fighting, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    let dance = Action {
        actor: 0,
        action: attack_action(CardId::B3089Meloetta, 0),
        is_stack: false,
    };
    game.apply_action(&dance);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        150,
        "Meloetta's Inspiring Dance does its printed 30 damage on the turn it is used"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    game.apply_action(&dance);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        90,
        "on the following turn Meloetta (a [F] Pokémon) should do 30 + 30 = 60 damage"
    );
}

/// Negative: Meloetta's version only boosts [F] Pokémon. A Colorless attacker taking over the
/// Active Spot gets nothing.
#[test]
fn test_meloetta_inspiring_dance_does_not_boost_a_non_fighting_attacker() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3089Meloetta).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![EnergyType::Fire]),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3089Meloetta, 0),
        is_stack: false,
    });
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    // Swap in the [R] Charmander and attack with it instead.
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1033Charmander, 0),
        is_stack: false,
    });

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        120,
        "Ember does its plain 30 damage (150 - 30); Charmander is not a [F] Pokémon"
    );
}
