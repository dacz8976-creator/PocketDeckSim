use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

fn houndoom() -> PlayedCard {
    PlayedCard::from_id(CardId::PB080MegaHoundoomEx).with_energy(vec![
        EnergyType::Fire,
        EnergyType::Fire,
        EnergyType::Colorless,
    ])
}

fn sponge() -> PlayedCard {
    let card = get_card_by_enum(CardId::PB024MegaLatiosEx);
    PlayedCard::new(card, 0, 400, vec![], false, vec![])
}

fn attack_damage(game: &mut Game<'static>) -> u32 {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::PB080MegaHoundoomEx, 0),
        is_stack: false,
    });
    400 - game.get_state_clone().get_active(1).get_remaining_hp()
}

#[test]
fn grimhound_flare_all_tails_replaces_printed_damage_with_zero() {
    let mut saw_zero = false;
    for seed in 0..120 {
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![houndoom()], vec![sponge()]);
        let damage = attack_damage(&mut game);
        saw_zero |= damage == 0;
    }
    assert!(
        saw_zero,
        "an all-tails result must deal 0 rather than the printed 80"
    );
}

#[test]
fn grimhound_flare_reaches_240_and_never_adds_printed_damage() {
    let mut saw_three_heads = false;
    for seed in 0..120 {
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![houndoom()], vec![sponge()]);
        let damage = attack_damage(&mut game);
        assert!(
            damage <= 240 && damage % 80 == 0,
            "seed {seed}: Grimhound Flare dealt {damage}, expected 0/80/160/240"
        );
        saw_three_heads |= damage == 240;
    }
    assert!(
        saw_three_heads,
        "a three-heads result must reach 240 damage across the seed sweep"
    );
}
