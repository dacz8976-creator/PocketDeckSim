// Ported from upstream deckgym-core #436 (tests/pokemon/melmetal_metal_scrum_test.rs, as of 9a3e2dd): both tests, with fork tests added at the end (a real attack; Metal Scrum switched off; two copies of one printing; stacking with Unown's GUARD and Steel Apron; the owner's own attack and the attacker's own Melmetal; an Ability's damage; the printings' status). The hit back is pinned in rules_repair_hit_back_attack_damage.rs, and kd's clock in hooks/core.rs (persistent_defender_damage_tests).
//! Melmetal's Metal Scrum: "As long as this Pokémon is in play, all of your [M] Pokémon take -20
//! damage from attacks from your opponent's Pokémon. This effect doesn't stack."

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    effects::CardEffect,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
};

/// Player 0 has `board` (first is Active); player 1 has a plain Active attacker. Applies `damage`
/// from player 1 to player 0's Pokémon at `target` and returns the HP it lost.
fn damage_taken(board: Vec<PlayedCard>, target: usize, damage: u32) -> u32 {
    let mut game =
        get_test_game_with_board(board, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state);

    let hp_before = game.get_state_clone().get_remaining_hp(0, target);
    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (1, 0),
            targets: vec![(damage, 0, target)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    hp_before - game.get_state_clone().get_remaining_hp(0, target)
}

#[test]
fn test_metal_scrum_cuts_damage_to_all_metal_pokemon() {
    let board = || {
        vec![
            PlayedCard::from_id(CardId::C1097Melmetal),
            PlayedCard::from_id(CardId::C1096Meltan),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ]
    };
    assert_eq!(damage_taken(board(), 0, 50), 30, "Melmetal is [M] itself");
    assert_eq!(
        damage_taken(board(), 1, 50),
        30,
        "Benched [M] Pokémon are covered"
    );
    assert_eq!(
        damage_taken(board(), 2, 50),
        50,
        "Non-[M] Pokémon are not covered"
    );
}

#[test]
fn test_metal_scrum_does_not_stack() {
    let board = vec![
        PlayedCard::from_id(CardId::C1097Melmetal),
        PlayedCard::from_id(CardId::C1150Melmetal),
        PlayedCard::from_id(CardId::C1096Meltan),
    ];
    assert_eq!(damage_taken(board, 2, 50), 30);
}

// Fork tests.

/// A Melmetal whose Ability is switched off: Prickly Powder's `NoAbilities`, as the engine stores it.
fn switched_off_melmetal() -> PlayedCard {
    let mut melmetal = PlayedCard::from_id(CardId::C1097Melmetal);
    melmetal.add_effect(CardEffect::NoAbilities, 1);
    melmetal
}

/// Player 0's Lunatone uses Moon Press (50, a [P] attack, so no Melmetal or Meltan is weak to it)
/// on player 1's Active, with `defender_board` behind it: the HP player 1's Active has left.
fn hp_after_moon_press(attacker_bench: Vec<PlayedCard>, defender_board: Vec<PlayedCard>) -> u32 {
    let mut attacker_board = vec![PlayedCard::from_id(CardId::A3073Lunatone)
        .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])];
    attacker_board.extend(attacker_bench);
    let mut game = get_test_game_with_board(attacker_board, defender_board);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3073Lunatone, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

/// Through a real attack, not only `ApplyDamage`: Moon Press's 50 does 30 to an Active Melmetal (120
/// HP), and 50 once its Ability is switched off.
#[test]
fn test_metal_scrum_cuts_a_real_attack() {
    for melmetal in [CardId::C1097Melmetal, CardId::C1150Melmetal] {
        let hp = hp_after_moon_press(vec![], vec![PlayedCard::from_id(melmetal)]);
        assert_eq!(hp, 90, "{melmetal:?}");
    }
    assert_eq!(hp_after_moon_press(vec![], vec![switched_off_melmetal()]), 70);
}

/// A switched-off Melmetal covers nothing, itself included; another Melmetal in play still covers
/// every [M] Pokémon, the switched-off one too.
#[test]
fn test_metal_scrum_switched_off_gives_no_cut() {
    let board = || vec![switched_off_melmetal(), PlayedCard::from_id(CardId::C1096Meltan)];
    assert_eq!(damage_taken(board(), 0, 50), 50);
    assert_eq!(damage_taken(board(), 1, 50), 50);

    let board = || {
        vec![
            switched_off_melmetal(),
            PlayedCard::from_id(CardId::C1096Meltan),
            PlayedCard::from_id(CardId::C1150Melmetal),
        ]
    };
    assert_eq!(damage_taken(board(), 0, 50), 30);
    assert_eq!(damage_taken(board(), 1, 50), 30);
}

/// Two copies of one printing don't stack either, and two holders cut each [M] Pokémon by 20 only,
/// the holders themselves included.
#[test]
fn test_two_melmetal_cut_20_not_40() {
    for (first, second) in [
        (CardId::C1097Melmetal, CardId::C1097Melmetal),
        (CardId::C1150Melmetal, CardId::C1150Melmetal),
        (CardId::C1097Melmetal, CardId::C1150Melmetal),
    ] {
        let board = || {
            vec![
                PlayedCard::from_id(first),
                PlayedCard::from_id(CardId::C1096Meltan),
                PlayedCard::from_id(second),
            ]
        };
        for target in 0..3 {
            assert_eq!(damage_taken(board(), target, 50), 30, "{first:?} + {second:?}, target {target}");
        }
    }
}

/// Metal Scrum doesn't stack with itself, but it does with every other cut: Unown's GUARD (A4 084,
/// enabled by A2a 034's CHECK) takes 10 more off every Pokémon, and Steel Apron (A4 153) 10 more
/// off the [M] Pokémon it is attached to. The Unown are [P], so they get GUARD's 10 only.
#[test]
fn test_metal_scrum_stacks_with_unown_guard_and_steel_apron() {
    let board = || {
        vec![
            PlayedCard::from_id(CardId::C1097Melmetal),
            PlayedCard::from_id(CardId::A4084Unown),
            PlayedCard::from_id(CardId::A2a034Unown),
            PlayedCard::from_id(CardId::C1096Meltan)
                .with_tool(get_card_by_enum(CardId::A4153SteelApron)),
        ]
    };
    assert_eq!(damage_taken(board(), 0, 50), 20, "Melmetal: 50 - 20 - 10");
    assert_eq!(damage_taken(board(), 1, 50), 40, "GUARD Unown: 50 - 10");
    assert_eq!(damage_taken(board(), 3, 50), 10, "Meltan with Steel Apron: 50 - 20 - 10 - 10");
}

/// Only attacks from the opponent's Pokémon: Diggersby's Earthquake (70, "This attack also does 10
/// damage to each of your Benched Pokémon.") does its full 10 to its owner's Benched Melmetal and
/// Meltan.
#[test]
fn test_metal_scrum_does_not_cut_damage_from_its_owners_own_attack() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2140Diggersby)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::C1097Melmetal),
            PlayedCard::from_id(CardId::C1096Meltan),
        ],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2140Diggersby, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert_eq!(state.get_remaining_hp(0, 1), 110, "Melmetal: the full 10");
    assert_eq!(state.get_remaining_hp(0, 2), 50, "Meltan: the full 10");
    assert_eq!(state.get_active(1).get_remaining_hp(), 80, "Snorlax took Earthquake's 70");
}

/// "all of your [M] Pokémon": the attacker's own Melmetal doesn't cut the damage its attack does to
/// the opponent's [M] Pokémon.
#[test]
fn test_the_attackers_own_metal_scrum_does_not_cut_its_damage() {
    let hp = hp_after_moon_press(
        vec![PlayedCard::from_id(CardId::C1097Melmetal)],
        vec![PlayedCard::from_id(CardId::C1096Meltan)],
    );
    assert_eq!(hp, 10, "Meltan (60 HP) takes Moon Press's full 50");
}

/// "from attacks": Greninja's Water Shuriken (A1 089, "Once during your turn, you may do 20 damage
/// to 1 of your opponent's Pokémon.") is an Ability's damage, so it does its full 20 to an Active
/// Melmetal (120 HP) and to the Benched Meltan (60 HP) beside it.
#[test]
fn test_metal_scrum_does_not_cut_damage_from_an_ability() {
    for (target, hp) in [(0, 100), (1, 40)] {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            5,
            vec![PlayedCard::from_id(CardId::A1089Greninja)],
            vec![
                PlayedCard::from_id(CardId::C1097Melmetal),
                PlayedCard::from_id(CardId::C1096Meltan),
            ],
        );
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseAbility { in_play_idx: 0 },
            is_stack: false,
        });
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        let shuriken = choices
            .into_iter()
            .find(|choice| {
                matches!(&choice.action, SimpleAction::ApplyDamage { targets, .. } if targets[0].2 == target)
            })
            .expect("Water Shuriken can target either Pokémon");
        assert!(matches!(
            &shuriken.action,
            SimpleAction::ApplyDamage { targets, is_from_active_attack: false, .. }
                if targets[..] == [(20, 1, target)]
        ));
        game.apply_action(&shuriken);
        assert_eq!(game.get_state_clone().get_remaining_hp(1, target), hp, "target {target}");
    }
}

/// Both Melmetal printings are Complete, with no known limitation.
#[test]
fn test_melmetal_printings_report_complete() {
    for id in [CardId::C1097Melmetal, CardId::C1150Melmetal] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}
