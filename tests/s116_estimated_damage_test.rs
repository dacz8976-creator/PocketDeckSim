//! §116 — pins `estimated_attack_damage` (via the f-tier value function) to hand-computed
//! values for the pre-registered mechanic classes, using real cards from pool9 decks.
//! The probes compare f-tier evaluations of constructed states where ONLY the quantity the
//! estimator should read differs, so each test isolates one class.

use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::players::value_functions::{
    public_damage_value_function, public_effect_value_function,
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

/// Mega Burst (SelfDiscardAllTypesEnergyDamagePerDiscarded): banking a 3rd/4th Energy must
/// now RAISE the f evaluation, while d (fixed_damage) stays flat past the printed cost.
#[test]
fn test_mega_burst_banking_gradient() {
    use EnergyType::{Fire, Lightning};
    let charge = |n: usize| {
        let energy: Vec<EnergyType> = (0..n)
            .map(|i| if i % 2 == 0 { Fire } else { Lightning })
            .collect();
        board(
            vec![PlayedCard::from_id(CardId::B4120MegaRayquazaEx).with_energy(energy)],
            vec![snorlax(), PlayedCard::from_id(CardId::A1211Snorlax)],
        )
    };
    let d: Vec<f64> = (2..=4).map(|n| public_damage_value_function(&charge(n), 0)).collect();
    let f: Vec<f64> = (2..=4).map(|n| public_effect_value_function(&charge(n), 0)).collect();
    println!("d-tier charge 2/3/4: {d:?}");
    println!("f-tier charge 2/3/4: {f:?}");
    assert!(
        d[2] - d[1] <= 0.0 + 1e-9,
        "d must NOT reward the 4th energy (got {} -> {})",
        d[1],
        d[2]
    );
    assert!(
        f[1] > f[0] && f[2] > f[1],
        "f must reward banking the 3rd and 4th energy: {f:?}"
    );
}

/// Brutal Bash (BenchCountDamage): adding a bench Pokémon must raise Zoroark ex's f value
/// by more than the bench body alone (the attack gains 30 per bench).
#[test]
fn test_brutal_bash_bench_count() {
    let zoroark = |bench: Vec<PlayedCard>| {
        let mut mine = vec![PlayedCard::from_id(CardId::B3106ZoroarkEx)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])];
        mine.extend(bench);
        board(mine, vec![snorlax()])
    };
    // Brutal Bash counts benched [D] Pokémon only ("This attack does 30 damage for each of
    // your Benched [D] Pokémon", include_fixed=false) — so the bench bodies must be Dark.
    let bench_body = || PlayedCard::from_id(CardId::B3106ZoroarkEx);
    let f0 = public_effect_value_function(&zoroark(vec![]), 0);
    let f1 = public_effect_value_function(&zoroark(vec![bench_body()]), 0);
    let f2 = public_effect_value_function(&zoroark(vec![bench_body(), bench_body()]), 0);
    let d0 = public_damage_value_function(&zoroark(vec![]), 0);
    let d1 = public_damage_value_function(&zoroark(vec![bench_body()]), 0);
    let d2 = public_damage_value_function(&zoroark(vec![bench_body(), bench_body()]), 0);
    let f_marginal = (f2 - f1) - (d2 - d1);
    println!("f: {f0:.0}/{f1:.0}/{f2:.0}  d: {d0:.0}/{d1:.0}/{d2:.0}  extra-per-bench under f: {f_marginal:.1}");
    assert!(
        f_marginal > 0.0,
        "f must credit Brutal Bash's per-bench damage beyond the bench body itself"
    );
}
