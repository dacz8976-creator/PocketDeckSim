//! §115 probe — does the d-tier evaluation actually score evolving as an improvement,
//! in a REAL constructed state (not the whiteboard)?

use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::players::value_functions::{
    parametric_value_function_ex2, public_baseline_value_function, public_damage_value_function,
    ValueFunctionParams,
};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::State;

/// Player 0: Bulbasaur active with 2 Grass, Ivysaur in HAND, Mega Venusaur ex in DECK.
/// Player 1: a beefy board (Snorlax active + bench) — a race Vine Whip alone loses, i.e.
/// a state where a human would set up the line. In a state where grinding with Vine Whip
/// genuinely wins faster (one lone 60 HP opponent), refusing to evolve is CORRECT play and
/// the d tier is entitled to refuse; this test must not punish it for that.
fn before_evolve() -> State {
    let mine = PlayedCard::from_id(CardId::A1001Bulbasaur)
        .with_energy(vec![EnergyType::Grass, EnergyType::Grass]);
    let their_active = PlayedCard::from_id(CardId::A1211Snorlax)
        .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
    let their_bench = PlayedCard::from_id(CardId::A1211Snorlax);
    let mut state =
        get_initialized_game_with_board(0, 0, 3, vec![mine], vec![their_active, their_bench])
            .get_state_clone();
    // Put Ivysaur in hand and Mega Venusaur ex in deck (replace one filler card each).
    state.hands[0].push(get_card_by_enum(CardId::B1a002Ivysaur));
    state.decks[0]
        .cards
        .push(get_card_by_enum(CardId::B1a004MegaVenusaurEx));
    state
}

/// Same board after evolving: Ivysaur active (energy carried over), Ivysaur no longer in
/// hand, Mega Venusaur ex still in deck.
fn after_evolve() -> State {
    let mut state = before_evolve();
    state.hands[0].pop(); // Ivysaur leaves the hand
    let evolved = PlayedCard::from_id(CardId::B1a002Ivysaur)
        .with_energy(vec![EnergyType::Grass, EnergyType::Grass]);
    state.in_play_pokemon[0][0] = Some(evolved);
    state
}

#[test]
fn test_p_tier_scores_evolution_as_a_downgrade_the_s113_defect() {
    let before = public_baseline_value_function(&before_evolve(), 0);
    let after = public_baseline_value_function(&after_evolve(), 0);
    // The §113 defect, pinned: the p evaluation must NOT reward this evolution.
    // (If this ever fails, the historical record's interpretation changes — investigate.)
    assert!(
        after < before,
        "expected p-tier to (wrongly) score evolution as a downgrade: before={before}, after={after}"
    );
}

#[test]
fn test_which_feature_moves() {
    let zero = ValueFunctionParams {
        points: 0.0,
        pokemon_value: 0.0,
        hand_size: 0.0,
        deck_size: 0.0,
        active_retreat_cost: 0.0,
        active_pokemon_online_score: 0.0,
        active_safety: 0.0,
        active_has_tool: 0.0,
        is_winner: 0.0,
        turns_until_opponent_wins: 0.0,
        online_pokemon_count: 0.0,
        energy_distance_to_online: 0.0,
        opponent_discard_size: 0.0,
    };
    let probes: Vec<(&str, ValueFunctionParams)> = vec![
        ("pokemon_value", ValueFunctionParams { pokemon_value: 1.0, ..zero }),
        ("hand_size", ValueFunctionParams { hand_size: 1.0, ..zero }),
        ("online_score", ValueFunctionParams { active_pokemon_online_score: 500.0, ..zero }),
        ("safety", ValueFunctionParams { active_safety: 1.0, ..zero }),
        ("turns", ValueFunctionParams { turns_until_opponent_wins: 100.0, ..zero }),
        ("retreat", ValueFunctionParams { active_retreat_cost: 1.0, ..zero }),
    ];
    for (name, p) in probes {
        let b = parametric_value_function_ex2(&before_evolve(), 0, &p, true, true);
        let a = parametric_value_function_ex2(&after_evolve(), 0, &p, true, true);
        println!("{name}: before={b:.2} after={a:.2} delta={:.2}", a - b);
    }
}

#[test]
fn test_d_tier_scores_evolution_as_an_upgrade() {
    let before = public_damage_value_function(&before_evolve(), 0);
    let after = public_damage_value_function(&after_evolve(), 0);
    assert!(
        after > before,
        "d-tier must score evolution as an upgrade: before={before}, after={after}"
    );
    println!("d-tier: before={before}, after={after}, delta={}", after - before);
}
