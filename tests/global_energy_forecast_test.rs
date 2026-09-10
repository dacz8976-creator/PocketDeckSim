use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::attack_action,
    Deck, State,
};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::collections::BTreeMap;

fn board(actor: usize, ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> State {
    let mut state = State::new(&Deck::default(), &Deck::default());
    state.turn_count = 10;
    state.current_player = actor;
    if actor == 0 { state.set_board(ours, theirs); } else { state.set_board(theirs, ours); }
    state
}
fn attack(actor: usize, id: CardId, index: usize) -> Action {
    Action { actor, action: attack_action(id, index), is_stack: false }
}
fn energy_total(state: &State, owner: usize) -> usize {
    state.enumerate_in_play_pokemon(owner).map(|(_, p)| p.attached_energy.len()).sum::<usize>()
        + state.discard_energies[owner].len()
}
fn apply(initial: &State, action: &Action, branch: usize, seed: u64) -> State {
    let (_, mutations) = try_forecast_action(initial, action).unwrap().into_branches();
    let mut state = initial.clone();
    mutations.into_iter().nth(branch).unwrap()(&mut StdRng::seed_from_u64(seed), &mut state, action);
    state
}
fn probabilities(initial: &State, action: &Action) -> Vec<f64> {
    let (p, m) = try_forecast_action(initial, action).unwrap().into_branches();
    assert_eq!(p.len(), m.len());
    assert!(!p.is_empty() && p.iter().all(|x| x.is_finite() && *x > 0.0 && *x <= 1.0));
    close(p.iter().sum(), 1.0);
    p
}
fn close(actual: f64, expected: f64) { assert!((actual - expected).abs() < 1e-12, "{actual} != {expected}"); }
fn sponge() -> PlayedCard { PlayedCard::from_id(CardId::PB024MegaLatiosEx) }

#[test]
fn reuniclus_hp_loss_has_both_terminal_and_surviving_branches_in_both_seats() {
    for actor in [0, 1] {
        let mut initial = board(actor,
            vec![PlayedCard::from_id(CardId::A1a018GyaradosEx).with_energy(vec![EnergyType::Water; 4])],
            vec![PlayedCard::from_id(CardId::B1a034Reuniclus).with_energy(vec![EnergyType::Psychic; 3]).with_damage(20)]);
        initial.points[actor] = 2;
        assert_eq!(initial.get_active(1 - actor).get_remaining_hp(), 160);
        let action = attack(actor, CardId::A1a018GyaradosEx, 0);
        assert!(initial.generate_possible_actions().1.contains(&action));
        let p = probabilities(&initial, &action);
        let mut win_mass = 0.0;
        let mut survival_mass = 0.0;
        for (branch, probability) in p.into_iter().enumerate() {
            let outcome = apply(&initial, &action, branch, 0);
            for seed in [1, 91, u64::MAX] {
                assert_eq!(serde_json::to_value(&outcome).unwrap(), serde_json::to_value(apply(&initial, &action, branch, seed)).unwrap(), "one forecast branch must not resample the discarded Energy");
            }
            for owner in [0, 1] { assert_eq!(energy_total(&outcome, owner), energy_total(&initial, owner)); }
            match outcome.winner {
                Some(GameOutcome::Win(winner)) => { assert_eq!(winner, actor); assert_eq!(outcome.points[actor], 3); win_mass += probability; }
                None => { assert_eq!(outcome.get_active(1 - actor).get_remaining_hp(), 20); survival_mass += probability; }
                other => panic!("unexpected outcome {other:?}"),
            }
        }
        close(win_mass, 3.0 / 7.0);
        close(survival_mass, 4.0 / 7.0);
    }
}

#[test]
fn single_discard_is_weighted_by_physical_attachments_and_preserves_ownership() {
    let initial = board(0,
        vec![PlayedCard::from_id(CardId::A1a018GyaradosEx).with_energy(vec![EnergyType::Water; 9])],
        vec![sponge().with_energy(vec![EnergyType::Psychic])]);
    let action = attack(0, CardId::A1a018GyaradosEx, 0);
    let mut mass = [0.0; 2];
    for (i, p) in probabilities(&initial, &action).into_iter().enumerate() {
        let after = apply(&initial, &action, i, 0);
        assert_eq!(after.get_active(1).get_remaining_hp(), 40);
        assert_eq!(after.discard_energies[0].len() + after.discard_energies[1].len(), 1);
        for owner in [0, 1] {
            assert_eq!(energy_total(&after, owner), energy_total(&initial, owner));
            if after.discard_energies[owner].len() == 1 { mass[owner] += p; }
        }
    }
    close(mass[0], 0.9); close(mass[1], 0.1);
}

#[test]
fn two_global_discards_have_without_replacement_multiset_weights() {
    let initial = board(0,
        vec![PlayedCard::from_id(CardId::B2036MegaSwampertEx).with_energy(vec![EnergyType::Water; 3]),
             PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Psychic])],
        vec![sponge().with_energy(vec![EnergyType::Fire; 2])]);
    let action = attack(0, CardId::B2036MegaSwampertEx, 0);
    let mut mass = BTreeMap::new();
    for (i, p) in probabilities(&initial, &action).into_iter().enumerate() {
        let after = apply(&initial, &action, i, 7);
        let key = (3 - after.get_active(0).attached_energy.len(),
                   1 - after.in_play_pokemon[0][1].as_ref().unwrap().attached_energy.len(),
                   2 - after.get_active(1).attached_energy.len());
        *mass.entry(key).or_insert(0.0) += p;
        assert_eq!(after.discard_energies[0].len() + after.discard_energies[1].len(), 2);
        for owner in [0, 1] { assert_eq!(energy_total(&after, owner), energy_total(&initial, owner)); }
    }
    let expected = [((2, 0, 0), 3.0), ((1, 1, 0), 3.0), ((1, 0, 1), 6.0), ((0, 1, 1), 2.0), ((0, 0, 2), 1.0)];
    assert_eq!(mass.len(), expected.len());
    for (key, ways) in expected { close(mass[&key], ways / 15.0); }
}

#[test]
fn own_side_discard_excludes_opponent_in_both_seats() {
    for actor in [0, 1] {
        let initial = board(actor,
            vec![PlayedCard::from_id(CardId::B2b035Groudon).with_energy(vec![EnergyType::Fighting; 4]),
                 PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Water; 2])],
            vec![sponge().with_energy(vec![EnergyType::Psychic; 5])]);
        let action = attack(actor, CardId::B2b035Groudon, 0);
        let mut mass = BTreeMap::new();
        for (i, p) in probabilities(&initial, &action).into_iter().enumerate() {
            let after = apply(&initial, &action, i, 13);
            assert_eq!(after.get_active(1 - actor).attached_energy, vec![EnergyType::Psychic; 5]);
            assert!(after.discard_energies[1 - actor].is_empty());
            assert_eq!(after.discard_energies[actor].len(), 2);
            let key = 4 - after.get_active(actor).attached_energy.len();
            *mass.entry(key).or_insert(0.0) += p;
        }
        assert_eq!(mass.len(), 3); close(mass[&2], 6.0/15.0); close(mass[&1], 8.0/15.0); close(mass[&0], 1.0/15.0);
    }
}

#[test]
fn damage_lethal_target_remains_in_energy_pool_until_discard_resolves() {
    let initial = board(0,
        vec![PlayedCard::from_id(CardId::A1a018GyaradosEx).with_energy(vec![EnergyType::Water; 4])],
        vec![sponge().with_remaining_hp(10).with_energy(vec![EnergyType::Psychic; 3]), PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    let action = attack(0, CardId::A1a018GyaradosEx, 0);
    let mut attacker_unchanged = 0.0;
    for (i, p) in probabilities(&initial, &action).into_iter().enumerate() {
        let after = apply(&initial, &action, i, 1);
        if after.get_active(0).attached_energy.len() == 4 { attacker_unchanged += p; }
        assert!(after.in_play_pokemon[1][0].is_none());
        for owner in [0, 1] { assert_eq!(energy_total(&after, owner), energy_total(&initial, owner)); }
    }
    close(attacker_unchanged, 3.0/7.0);
}

#[test]
fn copied_own_side_discard_uses_mews_board_and_records_resources() {
    let initial = board(0,
        vec![PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![EnergyType::Psychic; 3])],
        vec![PlayedCard::from_id(CardId::B2b035Groudon).with_energy(vec![EnergyType::Fighting; 4]), sponge()]);
    let copy = attack(0, CardId::A1a032MewEx, 1);
    let staged = apply(&initial, &copy, 0, 17);
    let action = staged.generate_possible_actions().1.into_iter().find(|a| matches!(&a.action, SimpleAction::Attack(atk) if atk.title == "Gaia Blast")).unwrap();
    assert!(action.is_stack);
    let p = probabilities(&staged, &action);
    for i in 0..p.len() {
        let after = apply(&staged, &action, i, 99);
        assert_eq!(after.get_active(0).attached_energy, vec![EnergyType::Psychic]);
        assert_eq!(after.discard_energies[0], vec![EnergyType::Psychic; 2]);
        for owner in [0, 1] { assert_eq!(energy_total(&after, owner), energy_total(&initial, owner)); }
    }
}

#[test]
fn deterministic_discard_branch_does_not_consume_mutation_rng() {
    let initial = board(0,
        vec![PlayedCard::from_id(CardId::A1a018GyaradosEx).with_energy(vec![EnergyType::Water; 4])],
        vec![sponge().with_energy(vec![EnergyType::Psychic; 3])]);
    let action = attack(0, CardId::A1a018GyaradosEx, 0);
    let (_, mutations) = try_forecast_action(&initial, &action).unwrap().into_branches();
    for mutation in mutations {
        let mut rng = StdRng::seed_from_u64(123);
        let mut control = rng.clone();
        mutation(&mut rng, &mut initial.clone(), &action);
        assert_eq!(rng.next_u64(), control.next_u64());
    }
}
