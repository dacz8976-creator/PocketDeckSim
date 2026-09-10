use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};
use rand::{rngs::StdRng, SeedableRng};

const BASIC_ENERGY_TYPES: [EnergyType; 8] = [
    EnergyType::Grass,
    EnergyType::Fire,
    EnergyType::Water,
    EnergyType::Lightning,
    EnergyType::Psychic,
    EnergyType::Fighting,
    EnergyType::Darkness,
    EnergyType::Metal,
];

fn state_with_boards(ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> State {
    get_initialized_game_with_board(7, 0, 3, ours, theirs).get_state_clone()
}

fn attack(card_id: CardId) -> Action {
    Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    }
}

fn apply_branch(
    initial: &State,
    action: &Action,
    branch_index: usize,
    mutation_seed: u64,
) -> State {
    let (_, mut mutations) = try_forecast_action(initial, action)
        .expect("the attack forecast should be exactly priced")
        .into_branches();
    let mutation = mutations.remove(branch_index);
    let mut next = initial.clone();
    mutation(
        &mut StdRng::seed_from_u64(mutation_seed),
        &mut next,
        action,
    );
    next
}

fn assert_uniform(probabilities: &[f64], branch_count: usize) {
    assert_eq!(probabilities.len(), branch_count);
    let expected = 1.0 / branch_count as f64;
    assert!(
        probabilities.iter().all(|probability| *probability == expected),
        "expected {branch_count} uniform branches, got {probabilities:?}"
    );
    assert_eq!(probabilities.iter().sum::<f64>(), 1.0);
}

fn sableye_state(with_bench: bool) -> State {
    let mut ours = vec![
        PlayedCard::from_id(CardId::B3a040Sableye).with_energy(vec![EnergyType::Colorless]),
    ];
    if with_bench {
        ours.push(PlayedCard::from_id(CardId::A1001Bulbasaur));
        ours.push(PlayedCard::from_id(CardId::A1033Charmander));
    }
    state_with_boards(ours, vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)])
}

fn queued_attachment_choices(state: &State) -> Vec<(EnergyType, usize)> {
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0, "Jeweled Gift's target belongs to its attacker");
    choices
        .into_iter()
        .map(|choice| match choice.action {
            SimpleAction::Attach {
                attachments,
                is_turn_energy,
            } => {
                assert!(!is_turn_energy);
                assert_eq!(attachments.len(), 1);
                let (amount, energy_type, in_play_idx) = attachments[0];
                assert_eq!(amount, 1);
                (energy_type, in_play_idx)
            }
            other => panic!("expected only Jeweled Gift Attach choices, got {other:?}"),
        })
        .collect()
}

#[test]
fn sableye_forecast_exposes_each_type_before_the_existing_target_choice() {
    let initial = sableye_state(true);
    let action = attack(CardId::B3a040Sableye);
    let (probabilities, mutations) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_uniform(&probabilities, 8);
    assert_eq!(mutations.len(), 8);

    let mut observed_types = Vec::new();
    for branch in 0..8 {
        let seed_1 = apply_branch(&initial, &action, branch, 1);
        let seed_2 = apply_branch(&initial, &action, branch, 9_999);
        let choices_1 = queued_attachment_choices(&seed_1);
        let choices_2 = queued_attachment_choices(&seed_2);
        assert_eq!(choices_1, choices_2, "branch {branch} resampled its type");
        assert_eq!(choices_1.len(), 2);
        assert_eq!(choices_1[0].1, 1);
        assert_eq!(choices_1[1].1, 2);
        assert_eq!(choices_1[0].0, choices_1[1].0);
        assert_eq!(seed_1.get_active(1).get_remaining_hp(), 180);

        let energy_type = choices_1[0].0;
        assert!(!observed_types.contains(&energy_type));
        observed_types.push(energy_type);

        // Commit each advertised target choice: the type is already fixed, one Bench receives
        // one Energy, and this attack attachment does not consume or replace the turn zone.
        let target_actions = seed_1.generate_possible_actions().1;
        for (target_index, target_action) in target_actions.iter().enumerate() {
            let committed = apply_branch(&seed_1, target_action, 0, 53);
            for bench_slot in [1, 2] {
                let expected = if bench_slot == target_index + 1 {
                    vec![energy_type]
                } else {
                    vec![]
                };
                assert_eq!(
                    committed.in_play_pokemon[0][bench_slot].as_ref().unwrap().attached_energy,
                    expected,
                );
            }
            assert_eq!(committed.get_active(0).attached_energy, seed_1.get_active(0).attached_energy);
            assert_eq!(committed.energy_zone[0].current, seed_1.energy_zone[0].current);
            assert_eq!(committed.energy_zone[0].next, seed_1.energy_zone[0].next);
        }
    }
    assert!(
        BASIC_ENERGY_TYPES
            .iter()
            .all(|energy_type| observed_types.contains(energy_type)),
        "forecast omitted a printed Jeweled Gift type: {observed_types:?}"
    );
}

#[test]
fn sableye_without_a_bench_adds_no_chance_or_target_choice() {
    let initial = sableye_state(false);
    let action = attack(CardId::B3a040Sableye);
    let (probabilities, mutations) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);

    let next = apply_branch(&initial, &action, 0, 123);
    let (_, choices) = next.generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|choice| !matches!(choice.action, SimpleAction::Attach { .. }))
    );
    assert_eq!(next.get_active(1).get_remaining_hp(), 180);
}

fn smeargle_state(defender_energy: Vec<EnergyType>, protected: bool) -> State {
    let mut defender = PlayedCard::from_id(CardId::PB024MegaLatiosEx)
        .with_energy(defender_energy);
    if protected {
        defender = defender.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
    }
    state_with_boards(
        vec![PlayedCard::from_id(CardId::A4148Smeargle)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![defender],
    )
}

#[test]
fn smeargle_forecast_exposes_the_full_two_energy_index_type_product() {
    let initial = smeargle_state(
        vec![EnergyType::Colorless, EnergyType::Colorless],
        false,
    );
    let action = attack(CardId::A4148Smeargle);
    let (probabilities, mutations) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_uniform(&probabilities, 16);
    assert_eq!(mutations.len(), 16);

    let mut observed = Vec::new();
    for branch in 0..16 {
        let seed_1 = apply_branch(&initial, &action, branch, 1);
        let seed_2 = apply_branch(&initial, &action, branch, 9_999);
        let energies = seed_1.get_active(1).attached_energy.clone();
        assert_eq!(energies, seed_2.get_active(1).attached_energy);
        assert_eq!(seed_1.get_active(1).get_remaining_hp(), 130);
        assert_eq!(seed_2.get_active(1).get_remaining_hp(), 130);
        assert!(!observed.contains(&energies), "duplicate branch state {energies:?}");
        observed.push(energies);
    }

    for energy_type in BASIC_ENERGY_TYPES {
        assert!(observed.contains(&vec![energy_type, EnergyType::Colorless]));
        assert!(observed.contains(&vec![EnergyType::Colorless, energy_type]));
    }
}

#[test]
fn smeargle_convergent_routes_preserve_their_combined_probability() {
    let initial = smeargle_state(vec![EnergyType::Grass, EnergyType::Grass], false);
    let action = attack(CardId::A4148Smeargle);
    let (probabilities, _) = try_forecast_action(&initial, &action).unwrap().into_branches();
    assert_uniform(&probabilities, 16);
    let mut combined: Vec<(Vec<EnergyType>, f64)> = vec![];
    for branch in 0..probabilities.len() {
        let next = apply_branch(&initial, &action, branch, 71);
        let energies = next.get_active(1).attached_energy.clone();
        assert_eq!(energies.len(), 2);
        assert_eq!(next.get_active(1).get_remaining_hp(), 130);
        if let Some((_, mass)) = combined.iter_mut().find(|(state, _)| *state == energies) {
            *mass += probabilities[branch];
        } else {
            combined.push((energies, probabilities[branch]));
        }
    }
    assert_eq!(combined.len(), 15);
    assert_eq!(combined.iter().map(|(_, mass)| *mass).sum::<f64>(), 1.0);
    for (energies, mass) in combined {
        assert_eq!(mass, if energies == vec![EnergyType::Grass, EnergyType::Grass] {
            0.125 // Either Grass slot can be selected and replaced with Grass.
        } else {
            0.0625
        });
    }
}

#[test]
fn smeargle_no_energy_and_effect_prevention_are_damage_only() {
    let action = attack(CardId::A4148Smeargle);

    let no_energy = smeargle_state(vec![], false);
    let (probabilities, mutations) = try_forecast_action(&no_energy, &action)
        .unwrap()
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    let after_no_energy = apply_branch(&no_energy, &action, 0, 11);
    assert_eq!(after_no_energy.get_active(1).get_remaining_hp(), 130);
    assert!(after_no_energy.get_active(1).attached_energy.is_empty());

    let protected = smeargle_state(
        vec![EnergyType::Colorless, EnergyType::Colorless],
        true,
    );
    let (probabilities, mutations) = try_forecast_action(&protected, &action)
        .unwrap()
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    let after_protected = apply_branch(&protected, &action, 0, 22);
    assert_eq!(after_protected.get_active(1).get_remaining_hp(), 130);
    assert_eq!(
        after_protected.get_active(1).attached_energy,
        vec![EnergyType::Colorless, EnergyType::Colorless]
    );
}

#[test]
fn porygon_z_forecast_exposes_all_next_energy_types_without_mutation_rng() {
    let mut initial = state_with_boards(
        vec![PlayedCard::from_id(CardId::A2129PorygonZ).with_energy(vec![
            EnergyType::Colorless,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    initial.energy_zone[1].next = Some(EnergyType::Colorless);
    let action = attack(CardId::A2129PorygonZ);
    let (probabilities, mutations) = try_forecast_action(&initial, &action)
        .unwrap()
        .into_branches();
    assert_uniform(&probabilities, 8);
    assert_eq!(mutations.len(), 8);

    let mut observed_types = Vec::new();
    for branch in 0..8 {
        let seed_1 = apply_branch(&initial, &action, branch, 1);
        let seed_2 = apply_branch(&initial, &action, branch, 9_999);
        let energy_type = seed_1.energy_zone[1].next.unwrap();
        assert_eq!(Some(energy_type), seed_2.energy_zone[1].next);
        assert_eq!(seed_1.get_active(1).get_remaining_hp(), 100);
        assert_eq!(seed_2.get_active(1).get_remaining_hp(), 100);
        assert!(!observed_types.contains(&energy_type));
        observed_types.push(energy_type);
    }
    assert!(
        BASIC_ENERGY_TYPES
            .iter()
            .all(|energy_type| observed_types.contains(energy_type)),
        "forecast omitted a printed Buggy Beam type: {observed_types:?}"
    );
}
