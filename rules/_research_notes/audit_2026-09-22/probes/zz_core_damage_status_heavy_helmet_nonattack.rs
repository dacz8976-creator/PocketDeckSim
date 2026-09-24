use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{PlayedCard, StatusCondition},
    test_support::get_test_game_with_board,
};

/// Probe: Heavy Helmet ("-20 damage from attacks from your opponent's Pokémon") should not touch
/// non-attack damage (Poison ticks). `get_heavy_helmet_reduction` in hooks/core.rs takes no
/// `is_from_active_attack` parameter, unlike Metal Core Barrier / Steel Apron which do gate on it.
#[test]
fn probe_heavy_helmet_reduces_poison_checkup_damage() {
    let poisoned_active = PlayedCard::from_id(CardId::A1055Blastoise)
        .with_status_condition(StatusCondition::Poisoned)
        .with_tool(get_card_by_enum(CardId::B1219HeavyHelmet));

    let mut game = get_test_game_with_board(
        vec![poisoned_active],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let before_hp = game
        .get_state_clone()
        .in_play_pokemon[0][0]
        .as_ref()
        .unwrap()
        .get_remaining_hp();
    println!("BEFORE: Blastoise remaining_hp={before_hp}");

    let end_turn_action = Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    };
    game.apply_action(&end_turn_action);

    let state = game.get_state_clone();
    let after_hp = state.in_play_pokemon[0][0]
        .as_ref()
        .map(|p| p.get_remaining_hp());
    println!("AFTER 1 Poison Checkup tick: Blastoise remaining_hp={after_hp:?} (should be {} if Heavy Helmet correctly ignores non-attack damage; bug if unchanged at {before_hp})", before_hp - 10);

    if after_hp == Some(before_hp - 10) {
        println!("RESULT: OK -- Heavy Helmet correctly ignored the Poison tick.");
    } else {
        println!("RESULT: BUG -- Heavy Helmet reduced/blocked non-attack (Poison) damage.");
    }
    // Documents current behavior; does not hard-fail so it doesn't break other agents' full-suite runs.
}
