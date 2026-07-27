use std::collections::HashSet;

use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

fn sponge() -> PlayedCard {
    // Mega Latios ex: 180 HP, no weakness — a safe damage sponge.
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

#[test]
fn test_maushold_triple_gnawing_discards_one_energy_per_heads() {
    let mut seen_discard_counts = HashSet::new();
    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::B2a082Maushold)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
            vec![sponge().with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ])],
        );

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B2a082Maushold, 0),
            is_stack: false,
        });

        let state = game.get_state_clone();
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            180 - 60,
            "Seed {seed}: Triple Gnawing always deals its printed 60 damage"
        );
        let discarded = 3 - state.get_active(1).attached_energy.len();
        assert!(discarded <= 3);
        seen_discard_counts.insert(discarded);
    }
    assert!(
        seen_discard_counts.len() > 1,
        "Across seeds different heads counts should discard different amounts, saw {seen_discard_counts:?}"
    );
}

#[test]
fn test_pidgeot_twister_does_nothing_on_all_tails() {
    let mut saw_nothing = false;
    let mut saw_damage = false;
    for seed in 0..60 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::B1182Pidgeot)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
            vec![sponge().with_energy(vec![EnergyType::Water, EnergyType::Water])],
        );

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B1182Pidgeot, 0),
            is_stack: false,
        });

        let state = game.get_state_clone();
        let hp = state.get_active(1).get_remaining_hp();
        let energy_left = state.get_active(1).attached_energy.len();
        if hp == 180 {
            // All tails: the attack does nothing at all.
            saw_nothing = true;
            assert_eq!(
                energy_left, 2,
                "Seed {seed}: on all tails no Energy may be discarded"
            );
        } else {
            saw_damage = true;
            assert_eq!(hp, 180 - 80, "Seed {seed}: Twister deals 80 on any heads");
            assert!(
                energy_left < 2,
                "Seed {seed}: at least one Energy is discarded on any heads"
            );
        }
    }
    assert!(saw_nothing, "expected at least one all-tails branch");
    assert!(saw_damage, "expected at least one branch with heads");
}

#[test]
fn test_mega_pidgeot_giant_twister_does_nothing_on_all_tails() {
    let mut saw_nothing = false;
    let mut saw_damage = false;
    for seed in 0..60 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::PB006MegaPidgeotEx).with_energy(vec![
                    EnergyType::Colorless,
                    EnergyType::Colorless,
                    EnergyType::Colorless,
                ]),
            ],
            vec![sponge().with_energy(vec![EnergyType::Water, EnergyType::Water])],
        );

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::PB006MegaPidgeotEx, 0),
            is_stack: false,
        });

        let state = game.get_state_clone();
        let hp = state.get_active(1).get_remaining_hp();
        if hp == 180 {
            saw_nothing = true;
            assert_eq!(state.get_active(1).attached_energy.len(), 2);
        } else {
            saw_damage = true;
            assert_eq!(hp, 180 - 100);
            assert!(state.get_active(1).attached_energy.len() < 2);
        }
    }
    assert!(saw_nothing, "expected at least one all-tails branch");
    assert!(saw_damage, "expected at least one branch with heads");
}

#[test]
fn test_entei_strong_flare_discards_two_random_self_energy_on_tails() {
    let mut saw_heads = false;
    let mut saw_tails = false;
    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A4033Entei).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ])],
            vec![sponge()],
        );

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::A4033Entei, 0),
            is_stack: false,
        });

        let state = game.get_state_clone();
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            180 - 110,
            "Seed {seed}: Strong Flare always deals 110"
        );
        match state.get_active(0).attached_energy.len() {
            4 => saw_heads = true,
            2 => saw_tails = true,
            n => panic!("Seed {seed}: unexpected attacker energy count {n}"),
        }
    }
    assert!(saw_heads, "expected at least one heads branch (no discard)");
    assert!(
        saw_tails,
        "expected at least one tails branch (2 discarded)"
    );
}
