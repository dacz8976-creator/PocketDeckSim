//! §116 diagnosis probes — independent verification of the s113-addendum claims
//! (three defects; Dragonair/Rayquaza mechanism) and of what the §115 d tier does
//! and does not already fix. Diagnostic only.

use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::players::value_functions::{
    public_baseline_value_function, public_damage_value_function,
};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::State;

fn dump_attacks(id: CardId) -> Vec<(String, u32, Vec<EnergyType>)> {
    use deckgym::models::Card;
    let card = get_card_by_enum(id);
    match &card {
        Card::Pokemon(p) => p
            .attacks
            .iter()
            .map(|a| (a.title.clone(), a.fixed_damage, a.energy_required.clone()))
            .collect(),
        _ => vec![],
    }
}

/// Claim checks: card facts + the lexicographic .max() choice for Mega Rayquaza ex.
#[test]
fn test_addendum_card_facts() {
    println!("Wurmple B4 001:  {:?}", dump_attacks(CardId::B4001Wurmple));
    println!("Silcoon B4 002:  {:?}", dump_attacks(CardId::B4002Silcoon));
    println!("Cascoon B4 004:  {:?}", dump_attacks(CardId::B4004Cascoon));
    println!("Beautifly B4 003:{:?}", dump_attacks(CardId::B4003Beautifly));
    println!("Dustox B4 005:  {:?}", dump_attacks(CardId::B4005Dustox));
    println!("MegaRay B4 120: {:?}", dump_attacks(CardId::B4120MegaRayquazaEx));
    println!("Dragonair B4 117:{:?}", dump_attacks(CardId::B4117Dragonair));
    let yardstick = dump_attacks(CardId::B4120MegaRayquazaEx)
        .into_iter()
        .map(|(_, _, cost)| cost)
        .max()
        .unwrap();
    println!("lexicographic .max() yardstick for Mega Rayquaza ex: {yardstick:?}");
}

/// Beautifly cliff-size probe: Wurmple (Gnaw 10) evolving into Silcoon.
/// Hypothesis: the §115 cliff exists here too under p, but is SMALL, because a
/// 10-damage attacker's "turns until I win" is already near the 30.0 sentinel.
fn wurmple_board() -> State {
    let mine = PlayedCard::from_id(CardId::B4001Wurmple)
        .with_energy(vec![EnergyType::Grass]);
    let their_active = PlayedCard::from_id(CardId::A1211Snorlax)
        .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
    let their_bench = PlayedCard::from_id(CardId::A1211Snorlax);
    let mut state =
        get_initialized_game_with_board(0, 0, 3, vec![mine], vec![their_active, their_bench])
            .get_state_clone();
    state.hands[0].push(get_card_by_enum(CardId::B4002Silcoon));
    state.decks[0].cards.push(get_card_by_enum(CardId::B4003Beautifly));
    state
}

fn wurmple_after_evolve() -> State {
    let mut state = wurmple_board();
    state.hands[0].pop();
    state.in_play_pokemon[0][0] =
        Some(PlayedCard::from_id(CardId::B4002Silcoon).with_energy(vec![EnergyType::Grass]));
    state
}

#[test]
fn test_beautifly_cliff_size_under_p() {
    let before = public_baseline_value_function(&wurmple_board(), 0);
    let after = public_baseline_value_function(&wurmple_after_evolve(), 0);
    println!("p-tier Wurmple->Silcoon: before={before:.1} after={after:.1} delta={:.1}", after - before);
    let d_before = public_damage_value_function(&wurmple_board(), 0);
    let d_after = public_damage_value_function(&wurmple_after_evolve(), 0);
    println!("d-tier Wurmple->Silcoon: before={d_before:.1} after={d_after:.1} delta={:.1}", d_after - d_before);
}

/// Census: every attack in every pool9 deck whose value is misrepresented by
/// `fixed_damage` — i.e., it has an effect, mapped to a mechanic. Decides which mechanic
/// classes the s116 `estimated_attack_damage` must cover; the rest stay fixed_damage.
#[test]
fn test_pool9_effect_attack_census() {
    use deckgym::actions::EFFECT_MECHANIC_MAP;
    use deckgym::models::Card;
    use std::collections::BTreeMap;
    let dir = "/root/lab/pool9/pool9";
    let mut by_mechanic: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for entry in std::fs::read_dir(dir).unwrap() {
        let path = entry.unwrap().path();
        if path.extension().map(|e| e != "txt").unwrap_or(true) {
            continue;
        }
        let deck = deckgym::Deck::from_file(path.to_str().unwrap()).unwrap();
        let deck_name = path.file_stem().unwrap().to_string_lossy().to_string();
        for card in &deck.cards {
            if let Card::Pokemon(p) = card {
                for a in &p.attacks {
                    if let Some(effect) = &a.effect {
                        let mech = EFFECT_MECHANIC_MAP
                            .get(effect.as_str())
                            .map(|m| {
                                let d = format!("{m:?}");
                                d.split(['{', '(']).next().unwrap().trim().to_string()
                            })
                            .unwrap_or_else(|| "UNMAPPED".to_string());
                        by_mechanic.entry(mech).or_default().push(format!(
                            "{deck_name}: {} \"{}\" fixed={}",
                            p.name, a.title, a.fixed_damage
                        ));
                    }
                }
            }
        }
    }
    for (mech, cases) in &by_mechanic {
        let mut uniq = cases.clone();
        uniq.sort();
        uniq.dedup();
        println!("MECHANIC {mech} ({} sites)", uniq.len());
        for c in uniq {
            println!("   {c}");
        }
    }
}

#[test]
fn test_wurmple_feature_isolation() {
    use deckgym::players::value_functions::{parametric_value_function_ex2, ValueFunctionParams};
    let zero = ValueFunctionParams {
        points: 0.0, pokemon_value: 0.0, hand_size: 0.0, deck_size: 0.0,
        active_retreat_cost: 0.0, active_pokemon_online_score: 0.0, active_safety: 0.0,
        active_has_tool: 0.0, is_winner: 0.0, turns_until_opponent_wins: 0.0,
        online_pokemon_count: 0.0, energy_distance_to_online: 0.0, opponent_discard_size: 0.0,
    };
    let probes = vec![
        ("pokemon_value", ValueFunctionParams { pokemon_value: 1.0, ..zero }),
        ("hand_size", ValueFunctionParams { hand_size: 1.0, ..zero }),
        ("online_score", ValueFunctionParams { active_pokemon_online_score: 500.0, ..zero }),
        ("safety", ValueFunctionParams { active_safety: 1.0, ..zero }),
        ("turns", ValueFunctionParams { turns_until_opponent_wins: 100.0, ..zero }),
        ("retreat", ValueFunctionParams { active_retreat_cost: 1.0, ..zero }),
    ];
    for (name, p) in probes {
        let b = parametric_value_function_ex2(&wurmple_board(), 0, &p, true, false);
        let a = parametric_value_function_ex2(&wurmple_after_evolve(), 0, &p, true, false);
        println!("p-iso {name}: before={b:.1} after={a:.1} delta={:.1}", a - b);
    }
}

/// Rayquaza charging probe: does attaching Fire/Lightning to an ACTIVE Mega Rayquaza ex
/// raise the evaluation? Under p: predicted FLAT (defect 3). Under d: predicted RISING
/// via the pokemon/turns terms, but the 500-weight online score is predicted STILL BLIND
/// (calculate_active_pokemon_online_score was not touched by §115).
fn ray_board(energy: Vec<EnergyType>) -> State {
    let mine = PlayedCard::from_id(CardId::B4120MegaRayquazaEx).with_energy(energy);
    let their_active = PlayedCard::from_id(CardId::A1211Snorlax)
        .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
    let their_bench = PlayedCard::from_id(CardId::A1211Snorlax);
    get_initialized_game_with_board(0, 0, 3, vec![mine], vec![their_active, their_bench])
        .get_state_clone()
}

#[test]
fn test_rayquaza_charging_probe() {
    use EnergyType::{Fire, Lightning};
    let fns: [(&str, fn(&State, usize) -> f64); 2] = [
        ("p", public_baseline_value_function),
        ("d", public_damage_value_function),
    ];
    for (label, f) in fns {
        let e0 = f(&ray_board(vec![]), 0);
        let e1 = f(&ray_board(vec![Fire]), 0);
        let e2 = f(&ray_board(vec![Fire, Lightning]), 0);
        let e3 = f(&ray_board(vec![Fire, Lightning, Fire]), 0);
        println!("{label}-tier MegaRay charge 0/1/2/3 energy: {e0:.1} / {e1:.1} / {e2:.1} / {e3:.1}  (deltas {:.1}, {:.1}, {:.1})", e1 - e0, e2 - e1, e3 - e2);
    }
}
