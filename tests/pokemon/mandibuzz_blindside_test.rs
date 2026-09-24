use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Mandibuzz (B3 110) "Blindside": does 60 damage to 1 of your opponent's Pokémon that have
/// damage on them. It has no base damage of its own — the whole attack is the targeted hit, and
/// only already-damaged Pokémon are legal targets.
#[test]
fn test_mandibuzz_blindside_only_targets_damaged_pokemon() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B3110Mandibuzz).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            // Active is untouched; only the benched Charmander carries damage, so it should be
            // the sole legal target even though it is on the bench.
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(50),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3110Mandibuzz, 0),
        is_stack: false,
    });

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .all(|choice| matches!(choice.action, SimpleAction::ApplyDamage { .. })),
        "Blindside should prompt for a damage target"
    );
    assert_eq!(
        choices.len(),
        1,
        "only the damaged benched Charmander is a legal Blindside target"
    );

    game.apply_action(&choices[0].clone());

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let reaction = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::ResolveAttackRetaliation { .. }))
        .expect("Blindside's queued damage should return through attack retaliation")
        .clone();
    game.apply_action(&reaction);

    // 60 damage into 50 remaining HP knocks it out, so the slot is emptied.
    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][1].is_none(),
        "Blindside's 60 damage should knock out the 50-HP benched target"
    );
    assert_eq!(
        state.points[0], 1,
        "player 0 should score the point for that knockout"
    );
}

/// The opponent's undamaged Active must not take collateral damage — Blindside is a pure
/// targeted hit with no base damage.
#[test]
fn test_mandibuzz_blindside_leaves_undamaged_active_alone() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B3110Mandibuzz).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(50),
        ],
    );

    let active_hp_before = game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("opponent active should exist");

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3110Mandibuzz, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.in_play_pokemon[1][0]
            .as_ref()
            .expect("undamaged active should still be in play")
            .get_remaining_hp(),
        active_hp_before,
        "an undamaged Active is not a legal target and must take no damage"
    );
}
