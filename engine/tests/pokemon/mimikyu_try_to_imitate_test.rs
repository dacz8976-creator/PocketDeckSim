use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Mimikyu (A3b 035 / P-A 113) "Try to Imitate": "Flip a coin. If heads, choose 1 of your
/// opponent's Active Pokémon's attacks and use it as this attack." Try to Imitate has no printed
/// damage, so tails leaves the board untouched.
fn try_to_imitate(seed: u64) -> u32 {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A3b035Mimikyu)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
        // Bulbasaur's only attack is a flat 40-damage Vine Whip, and [P] hits [G] without Weakness.
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3b035Mimikyu, 0),
        is_stack: false,
    });
    // On heads the copied attack is queued as the single remaining choice.
    game.play_until_stable();

    game.get_state_clone().get_active(1).get_remaining_hp()
}

#[test]
fn test_mimikyu_try_to_imitate_copies_on_heads_and_does_nothing_on_tails() {
    let mut copied = 0;
    let mut whiffed = 0;

    for seed in 0..40 {
        match try_to_imitate(seed) {
            30 => copied += 1,  // 70 - 40 from the copied Vine Whip
            70 => whiffed += 1, // tails: Try to Imitate has 0 printed damage
            other => panic!("seed {seed}: unexpected remaining HP {other}"),
        }
    }

    assert!(
        copied > 0,
        "never copied an attack in 40 seeds — the Try to Imitate coin is not firing"
    );
    assert!(
        whiffed > 0,
        "always copied in 40 seeds — the coin flip is being skipped"
    );
}
