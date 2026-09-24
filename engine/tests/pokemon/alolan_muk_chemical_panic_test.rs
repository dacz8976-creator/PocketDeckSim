use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Alolan Muk ex (A3 111 et al.) "Chemical Panic": 80 damage; 1 Special Condition from among
/// Asleep, Burned, Confused, Paralyzed, and Poisoned is chosen at random and applied to the
/// opponent's Active Pokémon. Conditions already affecting that Pokémon are not chosen.
fn muk() -> PlayedCard {
    PlayedCard::from_id(CardId::A3111AlolanMukEx).with_energy(vec![
        EnergyType::Darkness,
        EnergyType::Darkness,
        EnergyType::Colorless,
    ])
}

fn attack(seed: u64, defender: PlayedCard) -> Game<'static> {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![muk()], vec![defender]);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3111AlolanMukEx, 0),
        is_stack: false,
    });
    game
}

fn condition_flags(pokemon: &PlayedCard) -> [bool; 5] {
    [
        pokemon.is_asleep(),
        pokemon.is_burned(),
        pokemon.is_confused(),
        pokemon.is_paralyzed(),
        pokemon.is_poisoned(),
    ]
}

#[test]
fn test_chemical_panic_applies_exactly_one_random_condition() {
    let mut seen = [false; 5];
    for seed in 0..150 {
        // Mega Latios ex: 180 HP, no weakness — survives the 80.
        let game = attack(seed, PlayedCard::from_id(CardId::PB024MegaLatiosEx));
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert_eq!(
            180 - defender.get_remaining_hp(),
            80,
            "seed {seed}: Chemical Panic always does 80"
        );
        let flags = condition_flags(defender);
        assert_eq!(
            flags.iter().filter(|f| **f).count(),
            1,
            "seed {seed}: exactly one Special Condition must be applied"
        );
        for (i, flag) in flags.iter().enumerate() {
            seen[i] |= flag;
        }
    }
    assert_eq!(
        seen,
        [true; 5],
        "across seeds all 5 Special Conditions must be reachable (Asleep, Burned, Confused, Paralyzed, Poisoned)"
    );
}

#[test]
fn test_chemical_panic_never_reselects_existing_compatible_conditions() {
    // Burn, Poison and one of Asleep/Paralyzed/Confused can coexist. With Paralyzed already
    // present, Chemical Panic must choose Asleep or Confused; either one replaces Paralysis.
    let mut saw_asleep = false;
    let mut saw_confused = false;
    for seed in 0..50 {
        let defender = PlayedCard::from_id(CardId::PB024MegaLatiosEx)
            .with_status_condition(StatusCondition::Burned)
            .with_status_condition(StatusCondition::Paralyzed)
            .with_status_condition(StatusCondition::Poisoned);
        let game = attack(seed, defender);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert_eq!(180 - defender.get_remaining_hp(), 80, "seed {seed}");
        assert!(defender.is_burned(), "seed {seed}: Burn must remain");
        assert!(defender.is_poisoned(), "seed {seed}: Poison must remain");
        assert!(!defender.is_paralyzed(), "seed {seed}: the new trio condition replaces Paralysis");
        assert_ne!(
            defender.is_asleep(),
            defender.is_confused(),
            "seed {seed}: exactly one eligible trio condition must be applied"
        );
        saw_asleep |= defender.is_asleep();
        saw_confused |= defender.is_confused();
    }
    assert!(saw_asleep && saw_confused, "both eligible replacement conditions should be reachable");
}

#[test]
fn test_chemical_panic_replaces_the_existing_trio_condition_and_still_does_damage() {
    let defender = PlayedCard::from_id(CardId::PB024MegaLatiosEx)
        .with_status_condition(StatusCondition::Asleep)
        .with_status_condition(StatusCondition::Burned)
        .with_status_condition(StatusCondition::Poisoned);
    let game = attack(0, defender);
    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(180 - defender.get_remaining_hp(), 80);
    assert!(defender.is_burned());
    assert!(defender.is_poisoned());
    assert!(!defender.is_asleep());
    assert_ne!(defender.is_confused(), defender.is_paralyzed());
}
