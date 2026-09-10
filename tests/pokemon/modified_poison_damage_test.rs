use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Apply the pending EndTurn (triggering Pokémon Checkup) and resolve forced actions.
fn end_turn(game: &mut Game<'static>) {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    let end = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::EndTurn))
        .unwrap_or_else(|| panic!("EndTurn should be available for player {actor}"))
        .clone();
    game.apply_action(&end);
    game.play_until_stable();
}

fn poison_tick_after_attack(attacker: PlayedCard, attacker_id: CardId, attack_damage: u32) -> u32 {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![attacker],
        // Mega Latios ex: 180 HP, no weakness.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert!(defender.is_poisoned(), "defender must be Poisoned");
    assert_eq!(180 - defender.get_remaining_hp(), attack_damage);

    // End player 0's turn: Pokémon Checkup applies the poison damage.
    end_turn(&mut game);
    let state = game.get_state_clone();
    let defender = state.get_active(1);
    180 - attack_damage - defender.get_remaining_hp()
}

/// Toxicroak (A2a 052) "Toxic": Poisoned, but the Checkup damage is 20 instead of the usual 10.
#[test]
fn test_toxicroak_toxic_poison_ticks_for_20() {
    let toxicroak =
        PlayedCard::from_id(CardId::A2a052Toxicroak).with_energy(vec![EnergyType::Darkness]);
    assert_eq!(
        poison_tick_after_attack(toxicroak, CardId::A2a052Toxicroak, 0),
        20,
        "Toxic's poison must deal 20 at Checkup instead of the usual 10"
    );
}

/// Toxapex (B3b 047) "Severe Poison": same template at 40.
#[test]
fn test_toxapex_severe_poison_ticks_for_40() {
    let toxapex = PlayedCard::from_id(CardId::B3b047ToxapEx)
        .with_energy(vec![EnergyType::Darkness, EnergyType::Colorless]);
    assert_eq!(
        poison_tick_after_attack(toxapex, CardId::B3b047ToxapEx, 0),
        40,
        "Severe Poison's poison must deal 40 at Checkup instead of the usual 10"
    );
}

/// Negative control: ordinary poison (Salazzle's Heated Poison, which also Burns) still ticks for
/// the usual 10 poison damage — the override must only apply to the modified-poison attacks.
/// Burn adds its own 20, so the combined tick is 30.
#[test]
fn test_ordinary_poison_still_ticks_for_10() {
    let salazzle = PlayedCard::from_id(CardId::A3036Salazzle)
        .with_energy(vec![EnergyType::Fire, EnergyType::Fire]);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![salazzle],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3036Salazzle, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert_eq!(180 - state.get_active(1).get_remaining_hp(), 30);

    end_turn(&mut game);
    let state = game.get_state_clone();
    let defender = state.get_active(1);
    // 30 (attack) + 10 (poison) + 20 (burn) = 60 total.
    assert_eq!(
        180 - defender.get_remaining_hp(),
        60,
        "ordinary poison must tick for 10 (plus 20 burn), not a modified amount"
    );
}
