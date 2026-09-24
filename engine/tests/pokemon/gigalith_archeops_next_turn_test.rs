use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Plays out end-of-turn actions (preferring `EndTurn` whenever it is offered, so neither player
/// does anything else) until it is player 0's turn again with a settled board.
fn advance_to_own_next_turn(game: &mut Game) {
    let start_turn = game.get_state_clone().turn_count;
    for _ in 0..40 {
        let state = game.get_state_clone();
        if state.current_player == 0
            && state.turn_count > start_turn
            && state.move_generation_stack.is_empty()
        {
            return;
        }
        let (_, choices) = state.generate_possible_actions();
        let action = choices
            .iter()
            .find(|choice| matches!(choice.action, SimpleAction::EndTurn))
            .unwrap_or(&choices[0])
            .clone();
        game.apply_action(&action);
    }
    panic!("did not get back to player 0's turn");
}

fn gigalith_energy() -> Vec<EnergyType> {
    vec![
        EnergyType::Fighting,
        EnergyType::Fighting,
        EnergyType::Fighting,
        EnergyType::Fighting,
    ]
}

fn gigalith_game() -> Game<'static> {
    get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2087GigalithEx).with_energy(gigalith_energy()),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
    )
}

/// Gigalith ex (B2 087 / B2 187 / B2 200) "Megaton Cannon": "This attack does 140 damage to 1 of
/// your opponent's Pokémon. During your next turn, this Pokémon can't attack."
#[test]
fn test_megaton_cannon_lets_you_pick_any_of_the_opponents_pokemon() {
    let mut game = gigalith_game();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2087GigalithEx, 0),
        is_stack: false,
    });

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "the attacking player picks the target");
    assert_eq!(
        choices.len(),
        2,
        "both the opponent's Active and Benched Pokémon are legal targets"
    );

    let bench_choice = choices
        .iter()
        .find(|choice| match &choice.action {
            SimpleAction::ApplyDamage { targets, .. } => targets[0].2 == 1,
            _ => false,
        })
        .expect("the Bench should be a legal target")
        .clone();
    game.apply_action(&bench_choice);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "the Active Pokémon should be untouched when the Bench was chosen"
    );
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .expect("Snorlax should survive at 10 HP")
            .get_remaining_hp(),
        10,
        "Snorlax (150 HP) takes the flat 140 — Weakness never applies to Bench damage"
    );
}

/// End-to-end: after Megaton Cannon, Gigalith ex is offered no attacks at all on its next turn.
#[test]
fn test_megaton_cannon_locks_gigalith_out_of_attacking_next_turn() {
    let mut game = gigalith_game();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2087GigalithEx, 0),
        is_stack: false,
    });
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    game.apply_action(&choices[0].clone());

    advance_to_own_next_turn(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_name(),
        "Gigalith ex",
        "Gigalith ex should still be the Active Pokémon"
    );
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        !choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Attack(_))),
        "Megaton Cannon should leave Gigalith ex unable to attack during its next turn"
    );
}

/// Control for the test above: a Gigalith ex that has *not* used Megaton Cannon can attack
/// normally, so the absence of Attack actions above really is the lockout.
#[test]
fn test_gigalith_can_attack_when_it_has_not_used_megaton_cannon() {
    let game = gigalith_game();
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Attack(_))));
}

// =================================================================================================
// Archeops (B1 134 / B1 242) "Wild Spin": "This attack does 20 damage to each of your opponent's
// Pokémon. During your next turn, this Pokémon's Wild Spin attack does +20 damage to each of your
// opponent's Pokémon."
// =================================================================================================

fn archeops_game(card_id: CardId) -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(card_id).with_energy(vec![EnergyType::Fighting])],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1211Snorlax),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
    )
}

fn wild_spin(game: &mut Game, card_id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
}

#[test]
fn test_wild_spin_hits_every_opponent_pokemon_for_twenty() {
    let mut game = archeops_game(CardId::B1134Archeops);
    wild_spin(&mut game, CardId::B1134Archeops);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 160, "180 - 20");
    for bench_idx in 1..=2 {
        assert_eq!(
            state.in_play_pokemon[1][bench_idx]
                .as_ref()
                .unwrap()
                .get_remaining_hp(),
            130,
            "the Benched Snorlax (150 HP) in slot {bench_idx} should take 20"
        );
    }
}

/// The +20 has to reach the Bench too, not just the Active Spot — the wording is "+20 damage to
/// each of your opponent's Pokémon". The second Wild Spin therefore does 40 everywhere.
#[test]
fn test_wild_spin_boosts_itself_on_the_following_turn_including_the_bench() {
    let mut game = archeops_game(CardId::B1242Archeops);
    wild_spin(&mut game, CardId::B1242Archeops);
    advance_to_own_next_turn(&mut game);
    wild_spin(&mut game, CardId::B1242Archeops);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        120,
        "180 - 20 (first Wild Spin) - 40 (boosted second Wild Spin)"
    );
    for bench_idx in 1..=2 {
        assert_eq!(
            state.in_play_pokemon[1][bench_idx]
                .as_ref()
                .unwrap()
                .get_remaining_hp(),
            90,
            "the Benched Snorlax in slot {bench_idx} should take 20 then a boosted 40"
        );
    }
}

/// Negative case: the boost is gone by the turn after that, so a third Wild Spin is back to 20.
#[test]
fn test_wild_spin_boost_does_not_persist_two_turns_later() {
    let mut game = archeops_game(CardId::B1134Archeops);
    wild_spin(&mut game, CardId::B1134Archeops);
    advance_to_own_next_turn(&mut game);
    let after_first = game.get_state_clone().get_active(1).get_remaining_hp();

    // Skip a turn without attacking, so the +20 expires unused.
    advance_to_own_next_turn(&mut game);
    wild_spin(&mut game, CardId::B1134Archeops);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        after_first - 20,
        "an expired boost should leave Wild Spin back at its printed 20"
    );
}
