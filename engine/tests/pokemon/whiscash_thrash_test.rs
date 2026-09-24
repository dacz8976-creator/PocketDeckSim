use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Whiscash (A2a 017) "Thrash": 80 damage; heads → 60 MORE damage (140 total), tails → Whiscash
/// also does 20 damage to itself.
fn whiscash() -> PlayedCard {
    PlayedCard::from_id(CardId::A2a017Whiscash).with_energy(vec![
        EnergyType::Water,
        EnergyType::Water,
        EnergyType::Colorless,
        EnergyType::Colorless,
    ])
}

fn run(seed: u64, force_heads: bool) -> (u32, u32) {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![whiscash()],
        // Mega Latios ex: 180 HP, no weakness — survives the 140 max.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
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
        action: attack_action(CardId::A2a017Whiscash, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    let dealt = 180 - state.get_active(1).get_remaining_hp();
    let self_damage = 120 - state.get_active(0).get_remaining_hp();
    (dealt, self_damage)
}

#[test]
fn test_thrash_heads_adds_60_and_no_self_damage() {
    for seed in 0..10 {
        let (dealt, self_damage) = run(seed, true);
        assert_eq!(dealt, 140, "seed {seed}: heads must deal 80 + 60 = 140");
        assert_eq!(self_damage, 0, "seed {seed}: heads must not hurt Whiscash");
    }
}

#[test]
fn test_thrash_tails_deals_base_damage_and_20_to_self() {
    let (mut saw_heads, mut saw_tails) = (false, false);
    for seed in 0..60 {
        let (dealt, self_damage) = run(seed, false);
        match (dealt, self_damage) {
            (140, 0) => saw_heads = true,
            (80, 20) => saw_tails = true,
            other => panic!("seed {seed}: unexpected (damage, self damage) {other:?}"),
        }
        if saw_heads && saw_tails {
            break;
        }
    }
    assert!(saw_heads, "heads branch must occur");
    assert!(saw_tails, "tails branch (80 dealt, 20 recoil) must occur");
}
