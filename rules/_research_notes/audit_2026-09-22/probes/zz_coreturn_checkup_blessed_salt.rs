// Probe: does a Pokemon Poisoned down to exactly 0 HP at Pokemon Checkup get saved by a
// same-side "During Pokemon Checkup, heal 10" Ability (Garganacl's Blessed Salt) that the
// rules doc says should apply before Knock Outs are finalized (KOs happen "at the end of
// Pokemon Checkup"), or does the engine finalize the KO immediately when poison damage is
// applied, before Blessed Salt gets a chance to heal?

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{PlayedCard, StatusCondition},
    test_support::get_test_game_with_board,
};

#[test]
fn test_blessed_salt_vs_poison_checkup_order() {
    // Caterpie: 50 HP. Damage it to 40 (10 remaining). Poison does 10 at Checkup -> would hit 0.
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1005Caterpie).with_damage(40),
            PlayedCard::from_id(CardId::B3a033Garganacl), // Blessed Salt: heal 10 each Checkup
        ],
        vec![PlayedCard::from_id(CardId::A1005Caterpie)],
    );
    let mut state = game.get_state_clone();
    state.apply_status_condition(0, 0, StatusCondition::Poisoned);
    game.set_state(state);

    println!(
        "Before EndTurn: player0 active remaining HP = {}",
        game.get_state_clone().get_active(0).get_remaining_hp()
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    let final_state = game.get_state_clone();
    let still_in_play = final_state.in_play_pokemon[0][0].is_some();
    println!("After Checkup: player0 active still in play = {still_in_play}");
    if still_in_play {
        println!(
            "After Checkup: player0 active remaining HP = {}",
            final_state.get_active(0).get_remaining_hp()
        );
    }
    println!("Points: {:?}", final_state.points);

    // Just report; don't fail the build either way (this is an evidence probe).
}
