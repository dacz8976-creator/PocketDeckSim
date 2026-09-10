use std::collections::BTreeSet;

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};
use rand::{rngs::StdRng, SeedableRng};

fn quagsire() -> PlayedCard {
    PlayedCard::from_id(CardId::B3b037Quagsire).with_energy(vec![
        EnergyType::Fighting,
        EnergyType::Fighting,
        EnergyType::Colorless,
    ])
}

fn two_attack_defender(protected: bool) -> PlayedCard {
    let decidueye = PlayedCard::from_id(CardId::A3012DecidueyeEx)
        .with_energy(vec![EnergyType::Grass, EnergyType::Grass]);
    if protected {
        decidueye.with_tool(get_card_by_enum(CardId::B4149ClearVeil))
    } else {
        decidueye
    }
}

fn single_attack_defender() -> PlayedCard {
    // Printed 70 HP survives Amnesia's 60 damage without an inflated test HP value.
    PlayedCard::from_id(CardId::A1001Bulbasaur)
        .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])
}

fn zero_attack_defender() -> PlayedCard {
    // A synthetic attack-list boundary; the card retains its printed HP and other properties.
    let mut defender = PlayedCard::from_id(CardId::A1001Bulbasaur);
    let Card::Pokemon(pokemon) = &mut defender.card else {
        panic!("Bulbasaur must be a Pokemon")
    };
    pokemon.attacks.clear();
    defender
}

fn fixture(defender: PlayedCard) -> State {
    get_initialized_game_with_board(7, 0, 3, vec![quagsire()], vec![defender])
        .get_state_clone()
}

fn amnesia_action() -> Action {
    Action {
        actor: 0,
        action: attack_action(CardId::B3b037Quagsire, 0),
        is_stack: false,
    }
}

fn apply_branch(initial: &State, branch_index: usize, mutation_seed: u64) -> State {
    let action = amnesia_action();
    let (_, mut mutations) = try_forecast_action(initial, &action)
        .expect("Amnesia forecast should be exactly priced")
        .into_branches();
    let mutation = mutations.remove(branch_index);
    let mut next = initial.clone();
    mutation(
        &mut StdRng::seed_from_u64(mutation_seed),
        &mut next,
        &action,
    );
    next
}

fn offered_attacks_on_defender_turn(state: State) -> Vec<String> {
    let mut game = get_initialized_game_with_board(
        99,
        0,
        3,
        vec![quagsire()],
        vec![single_attack_defender()],
    );
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "it should be the defending player's turn");
    choices
        .into_iter()
        .filter_map(|choice| match choice.action {
            SimpleAction::Attack(attack) => Some(attack.title),
            _ => None,
        })
        .collect()
}

#[test]
fn amnesia_forecast_has_uniform_explicit_successors_for_each_attack() {
    let initial = fixture(two_attack_defender(false));
    let action = amnesia_action();
    let (probabilities, mutations) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();

    assert_eq!(probabilities, vec![0.5, 0.5]);
    assert_eq!(mutations.len(), 2);

    let remaining: BTreeSet<Vec<String>> = (0..2)
        .map(|branch| offered_attacks_on_defender_turn(apply_branch(&initial, branch, 41)))
        .collect();
    assert_eq!(
        remaining,
        BTreeSet::from([
            vec!["Pierce the Pain".to_string()],
            vec!["Razor Leaf".to_string()],
        ]),
        "each branch should lock one distinct printed attack"
    );
}

#[test]
fn amnesia_branch_identity_does_not_depend_on_mutation_rng() {
    let initial = fixture(two_attack_defender(false));

    for branch in 0..2 {
        let with_seed_1 =
            offered_attacks_on_defender_turn(apply_branch(&initial, branch, 1));
        let with_seed_2 =
            offered_attacks_on_defender_turn(apply_branch(&initial, branch, 9_999));
        assert_eq!(
            with_seed_1, with_seed_2,
            "forecast branch {branch} sampled a new lock during mutation"
        );
    }
}

#[test]
fn amnesia_single_attack_defender_stays_deterministic() {
    let initial = fixture(single_attack_defender());
    let action = amnesia_action();
    let (probabilities, _) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);

    let next = apply_branch(&initial, 0, 123);
    assert_eq!(next.get_active(1).get_remaining_hp(), 10);
    assert!(
        offered_attacks_on_defender_turn(next).is_empty(),
        "the defender's only attack should be locked"
    );
}

#[test]
fn amnesia_zero_attack_defender_adds_no_random_branch() {
    let initial = fixture(zero_attack_defender());
    let action = amnesia_action();
    let (probabilities, _) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);

    let next = apply_branch(&initial, 0, 321);
    assert_eq!(next.get_active(1).get_remaining_hp(), 10);
    assert!(offered_attacks_on_defender_turn(next).is_empty());
}

#[test]
fn clear_veil_prevents_the_lock_without_preventing_damage_or_adding_chance() {
    let initial = fixture(two_attack_defender(true));
    let action = amnesia_action();
    let (probabilities, _) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);

    let next = apply_branch(&initial, 0, 777);
    assert_eq!(
        next.get_active(1).get_remaining_hp(),
        110,
        "Clear Veil prevents the attack effect, not Amnesia's 60 damage"
    );
    assert_eq!(
        offered_attacks_on_defender_turn(next),
        vec!["Pierce the Pain".to_string(), "Razor Leaf".to_string()],
        "Clear Veil should leave both attacks available"
    );
}
