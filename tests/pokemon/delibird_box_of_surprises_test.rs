use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Delibird (B2 032) "Box of Surprises": flip a coin; heads → 70 damage to the opponent's Active,
/// tails → heal 30 damage FROM the opponent's Active.
fn delibird() -> PlayedCard {
    PlayedCard::from_id(CardId::B2032Delibird)
        .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])
}

/// Opponent starts damaged so the tails-heal is observable: Mega Latios ex at 130/180.
fn run(seed: u64, force_heads: bool) -> u32 {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![delibird()],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_damage(50)],
    );
    if force_heads {
        let will = match get_card_by_enum(CardId::A4156Will) {
            Card::Trainer(trainer_card) => trainer_card,
            _ => panic!("Will should be a Trainer card"),
        };
        let mut state = game.get_state_clone();
        state.hands[0].push(Card::Trainer(will.clone()));
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play { trainer_card: will },
            is_stack: false,
        });
    }
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2032Delibird, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

#[test]
fn test_box_of_surprises_heads_does_70() {
    for seed in 0..10 {
        assert_eq!(
            run(seed, true),
            60,
            "seed {seed}: forced heads must deal 70 (130 -> 60)"
        );
    }
}

#[test]
fn test_box_of_surprises_tails_heals_opponent_30() {
    let (mut saw_damage, mut saw_heal) = (false, false);
    for seed in 0..60 {
        match run(seed, false) {
            60 => saw_damage = true,  // heads: 130 - 70
            160 => saw_heal = true,   // tails: 130 + 30 healed
            other => panic!("seed {seed}: unexpected opponent HP {other}, expected 60 or 160"),
        }
        if saw_damage && saw_heal {
            break;
        }
    }
    assert!(saw_damage, "heads branch must occur");
    assert!(saw_heal, "tails branch must heal the opponent's Active by 30");
}

/// The tails-heal cannot overheal: an opponent with only 10 damage is healed back to full, not
/// beyond it.
#[test]
fn test_box_of_surprises_heal_caps_at_full_hp() {
    let mut saw_heal_to_full = false;
    for seed in 0..60 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![delibird()],
            vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_damage(10)],
        );
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B2032Delibird, 0),
            is_stack: false,
        });
        let hp = game.get_state_clone().get_active(1).get_remaining_hp();
        assert!(
            hp == 100 || hp == 180,
            "seed {seed}: HP must be 100 (heads) or 180 (tails, capped heal), got {hp}"
        );
        saw_heal_to_full |= hp == 180;
    }
    assert!(saw_heal_to_full, "the capped heal branch must occur");
}
