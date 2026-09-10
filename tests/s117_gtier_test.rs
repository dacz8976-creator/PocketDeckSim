//! §117 — pins the g-tier additions: spread-damage estimation (Draco Meteor family),
//! the discard-energy credit, and f-tier immutability at the evaluation level.

use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::players::value_functions::{
    public_development_value_function, public_effect_value_function,
};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::State;

fn board(mine: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> State {
    get_initialized_game_with_board(0, 0, 3, mine, theirs).get_state_clone()
}

fn snorlax() -> PlayedCard {
    PlayedCard::from_id(CardId::A1211Snorlax)
        .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])
}

/// A1 185 Dragonite's Draco Meteor prints fixed_damage 0 (real: 4 random hits of 50).
/// Under f it must read as a 0-damage attacker; under g it must not.
#[test]
fn test_draco_meteor_counts_under_g() {
    let dragonite = PlayedCard::from_id(CardId::A1185Dragonite).with_energy(vec![
        EnergyType::Water,
        EnergyType::Lightning,
        EnergyType::Colorless,
        EnergyType::Colorless,
    ]);
    let with = board(vec![dragonite], vec![snorlax(), PlayedCard::from_id(CardId::A1211Snorlax)]);
    let f = public_effect_value_function(&with, 0);
    let g = public_development_value_function(&with, 0);
    println!("fully-charged A1 185 Dragonite: f={f:.1} g={g:.1}");
    // The cleanest observable: under f the side has NO visible damage (turns sentinel);
    // under g the same board must evaluate strictly higher by a wide margin.
    assert!(
        g > f + 200.0,
        "g must see Draco Meteor's spread damage where f sees a 0-damage attacker: f={f}, g={g}"
    );
}

/// Discard-energy credit: with a benched Dragonair (Dragon's Blessing) in play, energy in
/// the discard pile must raise the g evaluation and leave f unchanged.
#[test]
fn test_discard_energy_credit() {
    let ray = PlayedCard::from_id(CardId::B4120MegaRayquazaEx)
        .with_energy(vec![EnergyType::Fire, EnergyType::Lightning]);
    let dragonair = PlayedCard::from_id(CardId::B4117Dragonair);
    let make = |discarded: usize| {
        let mut s = board(vec![ray.clone(), dragonair.clone()], vec![snorlax()]);
        s.discard_energies[0] = (0..discarded)
            .map(|i| if i % 2 == 0 { EnergyType::Fire } else { EnergyType::Lightning })
            .collect();
        s
    };
    let g0 = public_development_value_function(&make(0), 0);
    let g3 = public_development_value_function(&make(3), 0);
    let g6 = public_development_value_function(&make(6), 0);
    let f0 = public_effect_value_function(&make(0), 0);
    let f3 = public_effect_value_function(&make(3), 0);
    println!("g discard 0/3/6: {g0:.1}/{g3:.1}/{g6:.1}   f discard 0/3: {f0:.1}/{f3:.1}");
    assert_eq!(g3 - g0, 45.0, "3 discard energies with a recycler = +45 (15 each)");
    assert_eq!(g6 - g0, 60.0, "credit caps at 4 (= +60)");
    assert_eq!(f3, f0, "f must not see the discard pile");

    // Without the recycler on the bench, the credit must vanish.
    let mut no_recycler = board(vec![ray.clone()], vec![snorlax()]);
    no_recycler.discard_energies[0] = vec![EnergyType::Fire; 3];
    let base = board(vec![ray], vec![snorlax()]);
    let g_no = public_development_value_function(&no_recycler, 0);
    let g_base = public_development_value_function(&base, 0);
    assert_eq!(g_no, g_base, "no recycler in play => discard energy worth 0");
}
