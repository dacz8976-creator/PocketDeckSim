use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game},
    Game,
};

/// Regice (A2 034) Crystal Body: "Prevent all effects of attacks used by your opponent's Pokémon
/// done to this Pokémon."
///
/// Player 0 attacks; `defender` is player 1's Active Pokémon.
fn attack_defender(
    attacker: CardId,
    attacker_energy: Vec<EnergyType>,
    defender: PlayedCard,
) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(attacker).with_energy(attacker_energy)],
        vec![defender, PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker, 0),
        is_stack: false,
    });
    game
}

/// Oddish's Poison Powder: 10 damage and "Your opponent's Active Pokémon is now Poisoned."
/// The damage is not an effect, so it still lands; the poison is.
#[test]
fn test_crystal_body_prevents_status_but_not_damage() {
    let game = attack_defender(
        CardId::A4001Oddish,
        vec![EnergyType::Grass],
        PlayedCard::from_id(CardId::A2034Regice),
    );

    let state = game.get_state_clone();
    let regice = state.get_active(1);
    assert!(
        !regice.is_poisoned(),
        "Crystal Body should prevent the attack's Poisoned effect"
    );
    assert_eq!(
        regice.get_remaining_hp(),
        100,
        "damage is not an effect, so the 10 damage still lands"
    );
}

/// NEGATIVE: without Crystal Body the same attack poisons normally.
#[test]
fn test_status_lands_on_a_pokemon_without_crystal_body() {
    let game = attack_defender(
        CardId::A4001Oddish,
        vec![EnergyType::Grass],
        // B3 045 Regice has no Ability — same name, same 110 HP, no Crystal Body.
        PlayedCard::from_id(CardId::B3045Regice),
    );

    let state = game.get_state_clone();
    assert!(
        state.get_active(1).is_poisoned(),
        "a Regice printing without Crystal Body is poisoned as usual"
    );
}

/// Beedrill ex's Crushing Spear: "Discard a random Energy from your opponent's Active Pokémon."
#[test]
fn test_crystal_body_prevents_energy_discard() {
    let game = attack_defender(
        CardId::A2b003BeedrillEx,
        vec![EnergyType::Grass, EnergyType::Grass],
        PlayedCard::from_id(CardId::A2034Regice)
            .with_energy(vec![EnergyType::Water, EnergyType::Water]),
    );

    let state = game.get_state_clone();
    let regice = state.get_active(1);
    assert_eq!(
        regice.attached_energy.len(),
        2,
        "Crystal Body should prevent the attack's Energy discard"
    );
    assert_eq!(regice.get_remaining_hp(), 30, "the 80 damage still lands");
}

/// NEGATIVE: without Crystal Body the Energy discard goes through.
#[test]
fn test_energy_discard_lands_on_a_pokemon_without_crystal_body() {
    let game = attack_defender(
        CardId::A2b003BeedrillEx,
        vec![EnergyType::Grass, EnergyType::Grass],
        PlayedCard::from_id(CardId::B3045Regice)
            .with_energy(vec![EnergyType::Water, EnergyType::Water]),
    );

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).attached_energy.len(), 1);
}
