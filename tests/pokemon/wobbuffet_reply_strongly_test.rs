use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
};

/// Wobbuffet's Reply Strongly: 30, +50 if this Pokémon was damaged by an attack during the
/// opponent's last turn while it was in the Active Spot. Full flow: Snorlax hits the active
/// Wobbuffet for 70, the turn passes, and Wobbuffet strikes back for 80.
#[test]
fn test_reply_strongly_boosted_after_being_hit_while_active() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![PlayedCard::from_id(CardId::A4086Wobbuffet)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax).with_energy(vec![
            EnergyType::Colorless,
            EnergyType::Colorless,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])],
    );

    // Player 1's Snorlax hits Wobbuffet (90 HP) with Rollout for 70 → 20 HP left.
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::A1211Snorlax, 0),
        is_stack: false,
    });
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "player 1 should be ending their turn");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    assert_eq!(state.get_active(0).get_remaining_hp(), 20);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4086Wobbuffet, 0),
        is_stack: false,
    });

    // 30 + 50 = 80. Snorlax: 150 - 80 = 70.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 70,
        "Reply Strongly should deal 80 after being damaged while Active last turn"
    );
}

/// Negative: an undisturbed Wobbuffet (not damaged by an attack last turn) deals only 30,
/// even if it already carries damage from other sources.
#[test]
fn test_reply_strongly_base_damage_without_being_hit() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4086Wobbuffet)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])
            .with_damage(30)],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4086Wobbuffet, 0),
        is_stack: false,
    });

    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 120,
        "Reply Strongly should deal 30 when not damaged by an attack last turn"
    );
}
