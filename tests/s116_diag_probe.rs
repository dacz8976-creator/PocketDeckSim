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

/// Census: every attack in every configured pool9 deck whose value is misrepresented by
/// `fixed_damage` — i.e., it has an effect, mapped to a mechanic. Decides which mechanic
/// classes the s116 `estimated_attack_damage` must cover; the rest stay fixed_damage.
///
/// Set `DECKGYM_POOL9_DIR` to the pool directory and `DECKGYM_POOL9_EXPECTED_DECKS` to a
/// comma-separated exact roster of its `.txt` filenames. With no pool configured this
/// diagnostic is deliberately skipped; the fixture gate below still exercises the census.
fn pool9_effect_attack_census(
    dir: &std::path::Path,
    expected_decks: &std::collections::BTreeSet<String>,
) -> Result<std::collections::BTreeMap<String, Vec<String>>, String> {
    use deckgym::actions::EFFECT_MECHANIC_MAP;
    use deckgym::models::Card;
    let mut by_mechanic: std::collections::BTreeMap<String, Vec<String>> =
        std::collections::BTreeMap::new();
    let mut found_decks = std::collections::BTreeSet::new();
    let entries = std::fs::read_dir(dir)
        .map_err(|err| format!("cannot read configured pool {}: {err}", dir.display()))?;

    for entry in entries {
        let path = entry
            .map_err(|err| format!("cannot read an entry in configured pool {}: {err}", dir.display()))?
            .path();
        if path.extension().and_then(|extension| extension.to_str()) != Some("txt") {
            continue;
        }
        let deck_file = path
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or_else(|| format!("configured pool has a non-UTF-8 deck filename: {}", path.display()))?
            .to_string();
        found_decks.insert(deck_file);
        let deck = deckgym::Deck::from_file(
            path.to_str()
                .ok_or_else(|| format!("configured pool has a non-UTF-8 deck path: {}", path.display()))?,
        )
        .map_err(|err| format!("malformed configured deck {}: {err}", path.display()))?;
        let deck_name = path
            .file_stem()
            .and_then(|name| name.to_str())
            .ok_or_else(|| format!("configured pool has a non-UTF-8 deck stem: {}", path.display()))?;
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

    if found_decks != *expected_decks {
        return Err(format!(
            "configured pool roster is incomplete or unexpected: expected {:?}, found {:?}",
            expected_decks, found_decks
        ));
    }
    if by_mechanic.is_empty() {
        return Err(format!(
            "configured pool {} has no effect attacks; census fixture is incomplete",
            dir.display()
        ));
    }
    Ok(by_mechanic)
}

fn parse_pool9_expected_decks(configured: &str) -> Result<std::collections::BTreeSet<String>, String> {
    if configured.is_empty() {
        return Err("DECKGYM_POOL9_EXPECTED_DECKS must be a non-empty comma-separated .txt filename roster".to_string());
    }
    let mut expected = std::collections::BTreeSet::new();
    for token in configured.split(',') {
        let name = token.trim();
        if name.is_empty() {
            return Err("DECKGYM_POOL9_EXPECTED_DECKS contains an empty filename token".to_string());
        }
        if !name.ends_with(".txt") {
            return Err(format!("DECKGYM_POOL9_EXPECTED_DECKS contains non-.txt filename {name:?}"));
        }
        if name.contains(['/', '\\']) {
            return Err(format!("DECKGYM_POOL9_EXPECTED_DECKS contains path separator in {name:?}"));
        }
        if !expected.insert(name.to_string()) {
            return Err(format!("DECKGYM_POOL9_EXPECTED_DECKS contains duplicate filename {name:?}"));
        }
    }
    Ok(expected)
}

fn configured_pool9_expected_decks() -> Result<std::collections::BTreeSet<String>, String> {
    let configured = std::env::var("DECKGYM_POOL9_EXPECTED_DECKS").map_err(|_| {
        "DECKGYM_POOL9_EXPECTED_DECKS must name the exact comma-separated .txt roster when DECKGYM_POOL9_DIR is set".to_string()
    })?;
    parse_pool9_expected_decks(&configured)
}

fn print_pool9_effect_attack_census(by_mechanic: &std::collections::BTreeMap<String, Vec<String>>) {
    for (mech, cases) in by_mechanic {
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
fn test_pool9_effect_attack_census() {
    let dir = match std::env::var("DECKGYM_POOL9_DIR") {
        Ok(dir) => dir,
        Err(std::env::VarError::NotPresent) => {
            println!("SKIP test_pool9_effect_attack_census: DECKGYM_POOL9_DIR is unset; fixture gate still executes the census");
            return;
        }
        Err(err) => panic!("DECKGYM_POOL9_DIR is invalid: {err}"),
    };
    let expected_decks = configured_pool9_expected_decks()
        .unwrap_or_else(|err| panic!("configured pool census refused: {err}"));
    let census = pool9_effect_attack_census(std::path::Path::new(&dir), &expected_decks)
        .unwrap_or_else(|err| panic!("configured pool census refused: {err}"));
    println!("CENSUS EXECUTED: {} configured decks, {} mechanic classes", expected_decks.len(), census.len());
    print_pool9_effect_attack_census(&census);
}

fn f016_fixture_dir(name: &str) -> std::path::PathBuf {
    use std::sync::atomic::{AtomicUsize, Ordering};
    static NEXT: AtomicUsize = AtomicUsize::new(0);
    let path = std::env::temp_dir().join(format!(
        "deckgym-f016-{name}-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    ));
    std::fs::create_dir(&path).expect("create F016 fixture directory");
    path
}

#[test]
fn test_pool9_effect_attack_census_fixture_gate() {
    let dir = f016_fixture_dir("valid");
    let file = dir.join("fixture.txt");
    std::fs::write(&file, "Energy: Grass\n1 Caterpie A1 005\n").expect("write valid F016 fixture");
    let expected = std::collections::BTreeSet::from(["fixture.txt".to_string()]);
    let census = pool9_effect_attack_census(&dir, &expected).expect("valid configured fixture must census");
    assert_eq!(census.len(), 1, "fixture must produce one mapped mechanic");
    assert!(
        census.iter().any(|(mechanic, sites)| {
            mechanic != "UNMAPPED"
                && sites == &vec!["fixture: Caterpie \"Find a Friend\" fixed=0".to_string()]
        }),
        "fixture census must retain Caterpie Find a Friend under a mapped mechanic: {census:?}"
    );
    std::fs::remove_dir_all(dir).expect("remove valid F016 fixture");
}

#[test]
fn test_pool9_effect_attack_census_refuses_missing_malformed_and_incomplete_fixtures() {
    let missing = std::env::temp_dir().join(format!("deckgym-f016-missing-{}", std::process::id()));
    let empty_expected = std::collections::BTreeSet::new();
    assert!(
        pool9_effect_attack_census(&missing, &empty_expected)
            .expect_err("missing configured pool must fail closed")
            .contains("cannot read configured pool")
    );

    let malformed = f016_fixture_dir("malformed");
    std::fs::write(malformed.join("bad.txt"), "this is not a deck\n").expect("write malformed F016 fixture");
    let malformed_expected = std::collections::BTreeSet::from(["bad.txt".to_string()]);
    assert!(
        pool9_effect_attack_census(&malformed, &malformed_expected)
            .expect_err("malformed configured pool must fail closed")
            .contains("malformed configured deck")
    );
    std::fs::remove_dir_all(malformed).expect("remove malformed F016 fixture");

    let incomplete = f016_fixture_dir("incomplete");
    std::fs::write(incomplete.join("present.txt"), "Energy: Grass\n1 Caterpie A1 005\n")
        .expect("write incomplete F016 fixture");
    let complete_expected = std::collections::BTreeSet::from([
        "present.txt".to_string(),
        "missing.txt".to_string(),
    ]);
    assert!(
        pool9_effect_attack_census(&incomplete, &complete_expected)
            .expect_err("incomplete configured pool must fail closed")
            .contains("roster is incomplete or unexpected")
    );
    std::fs::remove_dir_all(incomplete).expect("remove incomplete F016 fixture");
}

#[test]
fn test_pool9_expected_roster_parser_refuses_malformed_tokens() {
    assert_eq!(
        parse_pool9_expected_decks("fixture.txt, control.txt").expect("valid roster"),
        std::collections::BTreeSet::from(["control.txt".to_string(), "fixture.txt".to_string()])
    );
    for (roster, reason) in [
        ("", "non-empty"),
        ("fixture.txt,", "empty filename token"),
        ("fixture.txt,,control.txt", "empty filename token"),
        ("fixture.txt,fixture.txt", "duplicate filename"),
        ("fixture", "non-.txt filename"),
        ("folder/fixture.txt", "path separator"),
        ("folder\\fixture.txt", "path separator"),
    ] {
        assert!(
            parse_pool9_expected_decks(roster)
                .expect_err("malformed roster must fail closed")
                .contains(reason),
            "{roster:?} must be refused as {reason}"
        );
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
