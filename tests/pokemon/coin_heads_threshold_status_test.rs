use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// High-HP sponge (Mega Latios ex card, inflated base HP) — no weakness, never knocked out.
fn sponge(hp: u32) -> PlayedCard {
    let card = get_card_by_enum(CardId::PB024MegaLatiosEx);
    PlayedCard::new(card, 0, hp, vec![], false, vec![])
}

fn run_attack(seed: u64, attacker: PlayedCard, attacker_id: CardId) -> Game<'static> {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![attacker], vec![sponge(250)]);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    });
    game
}

/// Alolan Marowak (A3 027) "Burning Bonemerang": flip 2 coins, 70 damage per heads; if at least
/// 1 heads, the opponent's Active is Burned.
#[test]
fn test_burning_bonemerang_burns_iff_at_least_one_heads() {
    let marowak = || {
        PlayedCard::from_id(CardId::A3027AlolanMarowak).with_energy(vec![
            EnergyType::Fire,
            EnergyType::Fire,
            EnergyType::Colorless,
        ])
    };
    let (mut saw_burn, mut saw_zero) = (false, false);
    for seed in 0..120 {
        let game = run_attack(seed, marowak(), CardId::A3027AlolanMarowak);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        let damage = 250 - defender.get_remaining_hp();
        assert!(
            damage == 0 || damage == 70 || damage == 140,
            "seed {seed}: damage must be 0/70/140, got {damage}"
        );
        assert_eq!(
            defender.is_burned(),
            damage > 0,
            "seed {seed}: Burned exactly when at least one heads (damage {damage})"
        );
        saw_burn |= damage > 0;
        saw_zero |= damage == 0;
    }
    assert!(saw_burn, "at least one heads must occur");
    assert!(saw_zero, "double tails (no burn, no damage) must occur");
}

/// Drapion (A2 106) "Cross Poison": flip 4 coins, 40 damage per heads; if at least 2 heads, the
/// opponent's Active is Poisoned.
#[test]
fn test_cross_poison_poisons_iff_at_least_two_heads() {
    let drapion = || {
        PlayedCard::from_id(CardId::A2106Drapion).with_energy(vec![
            EnergyType::Darkness,
            EnergyType::Darkness,
            EnergyType::Darkness,
        ])
    };
    let (mut saw_poison, mut saw_low_roll) = (false, false);
    for seed in 0..150 {
        let game = run_attack(seed, drapion(), CardId::A2106Drapion);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        let damage = 250 - defender.get_remaining_hp();
        assert!(
            damage % 40 == 0 && damage <= 160,
            "seed {seed}: damage must be 0/40/80/120/160, got {damage}"
        );
        assert_eq!(
            defender.is_poisoned(),
            damage >= 80,
            "seed {seed}: Poisoned exactly when at least 2 heads (damage {damage})"
        );
        saw_poison |= damage >= 80;
        saw_low_roll |= damage < 80;
    }
    assert!(saw_poison, "2+ heads must occur across seeds");
    assert!(
        saw_low_roll,
        "0-1 heads (no poison) must occur across seeds"
    );
}

/// Bellossom (A4 003) "Petal Dance": flip 3 coins, 60 damage per heads; Bellossom is now Confused
/// regardless of the flips.
#[test]
fn test_petal_dance_always_confuses_self() {
    let bellossom = || {
        PlayedCard::from_id(CardId::A4003Bellossom)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])
    };
    let mut damages_seen = std::collections::HashSet::new();
    for seed in 0..120 {
        let game = run_attack(seed, bellossom(), CardId::A4003Bellossom);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        let damage = 250 - defender.get_remaining_hp();
        assert!(
            damage % 60 == 0 && damage <= 180,
            "seed {seed}: damage must be 0/60/120/180, got {damage}"
        );
        assert!(
            state.get_active(0).is_confused(),
            "seed {seed}: Bellossom must always be Confused after Petal Dance"
        );
        assert!(
            !defender.is_confused(),
            "seed {seed}: the DEFENDER must not be Confused"
        );
        damages_seen.insert(damage);
    }
    assert!(
        damages_seen.len() >= 3,
        "several distinct heads counts must occur, saw {damages_seen:?}"
    );
}
