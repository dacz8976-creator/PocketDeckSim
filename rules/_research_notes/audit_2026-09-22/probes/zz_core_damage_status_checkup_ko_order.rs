use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{PlayedCard, StatusCondition},
    test_support::get_test_game_with_board,
};

/// Probe: does a Pokémon Knocked Out by Poison during the Checkup get removed from play
/// (points/discard/promotion) BEFORE the same Checkup's Garganacl "Blessed Salt" heal (10 to
/// each of your Pokémon) has a chance to save it? Per rules/03: "KOs only at the end of the
/// Checkup (a Checkup heal like Garganacl's can save a Pokémon Poison took to 0)."
#[test]
fn probe_poison_ko_vs_blessed_salt_heal_same_checkup() {
    let poisoned_active = PlayedCard::from_id(CardId::A1001Bulbasaur)
        .with_status_condition(StatusCondition::Poisoned)
        .with_remaining_hp(10); // Poison 10 would bring this to exactly 0.
    let garganacl_bench = PlayedCard::from_id(CardId::B3a033Garganacl); // Blessed Salt: heal 10 from each of your Pokemon during Checkup.

    let mut game = get_test_game_with_board(
        vec![poisoned_active, garganacl_bench],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let before = game.get_state_clone();
    println!(
        "BEFORE: p0 active remaining_hp={:?}, points={:?}",
        before.in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp()),
        before.points
    );

    let end_turn_action = Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    };
    game.apply_action(&end_turn_action);

    let mut state = game.get_state_clone();
    // Drain any pending forced choices (e.g. a promotion) so we see the final settled state.
    for _ in 0..5 {
        if state.winner.is_some() {
            break;
        }
        let (actor, actions) = state.generate_possible_actions();
        if actions.len() == 1 {
            let a = Action { actor, action: actions[0].action.clone(), is_stack: actions[0].is_stack };
            game.apply_action(&a);
            state = game.get_state_clone();
        } else {
            break;
        }
    }

    println!(
        "AFTER: p0 slot0={:?} slot1={:?}, points={:?}, current_player={}",
        state.in_play_pokemon[0][0].as_ref().map(|p| (p.get_name(), p.get_remaining_hp())),
        state.in_play_pokemon[0][1].as_ref().map(|p| (p.get_name(), p.get_remaining_hp())),
        state.points,
        state.current_player,
    );

    let bulbasaur_survived_at_10 = state
        .in_play_pokemon[0]
        .iter()
        .flatten()
        .any(|p| p.get_name() == "Bulbasaur" && p.get_remaining_hp() == 10);

    if bulbasaur_survived_at_10 {
        println!("RESULT: Bulbasaur SURVIVED at 10 HP -- Blessed Salt saved it (matches rules).");
    } else {
        println!("RESULT: Bulbasaur did NOT survive at 10 HP in play -- Checkup KO'd it before Blessed Salt could heal (bug per rules/03 item 4), OR something else happened -- see AFTER line above.");
    }
}
