use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};

/// Xatu (A4 082 / A4 174) "Life Drain": "Flip a coin. If heads, your opponent's Active Pokémon's
/// remaining HP is now 10."
fn life_drain(seed: u64, card_id: CardId, defender_hp: u32) -> State {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(card_id)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_remaining_hp(defender_hp),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });

    game.get_state_clone()
}

#[test]
fn test_life_drain_sets_remaining_hp_to_ten_on_heads() {
    let mut heads = 0;
    let mut tails = 0;

    for seed in 0..40 {
        let state = life_drain(seed, CardId::A4082Xatu, 180);
        match state.get_active(1).get_remaining_hp() {
            10 => heads += 1,
            180 => tails += 1,
            other => panic!("seed {seed}: unexpected remaining HP {other}"),
        }
    }

    assert!(heads > 0, "Life Drain never came up heads in 40 seeds");
    assert!(
        tails > 0,
        "Life Drain always came up heads in 40 seeds — the coin is not being flipped"
    );
}

/// Negative case: the effect only ever lowers the remaining HP. A Pokémon already below 10 HP must
/// not be topped back up to 10 by an attack from the opponent.
#[test]
fn test_life_drain_never_raises_remaining_hp() {
    for seed in 0..40 {
        let state = life_drain(seed, CardId::A4174Xatu, 5);
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            5,
            "seed {seed}: Life Drain must not heal a defender that is already below 10 HP"
        );
    }
}
