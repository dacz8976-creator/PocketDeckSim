use crate::{actions::SimpleAction, models::EnergyType, State};

pub(crate) fn collect_in_play_indices_by_type(
    state: &State,
    player: usize,
    energy_type: EnergyType,
) -> Vec<usize> {
    state
        .enumerate_in_play_pokemon(player)
        .filter_map(|(in_play_idx, pokemon)| {
            if state.pokemon_is_type(pokemon, energy_type) {
                Some(in_play_idx)
            } else {
                None
            }
        })
        .collect()
}

pub(crate) fn energy_any_way_choices(
    target_indices: &[usize],
    energy_type: EnergyType,
    count: usize,
) -> Vec<SimpleAction> {
    if target_indices.is_empty() || count == 0 {
        return Vec::new();
    }

    let mut distributions = Vec::new();
    generate_distributions(
        target_indices,
        count,
        0,
        &mut vec![0; target_indices.len()],
        &mut distributions,
    );

    let mut choices = Vec::new();
    for dist in distributions {
        let mut attachments = Vec::new();
        for (i, &pokemon_idx) in target_indices.iter().enumerate() {
            if dist[i] > 0 {
                attachments.push((dist[i] as u32, energy_type, pokemon_idx));
            }
        }
        if !attachments.is_empty() {
            choices.push(SimpleAction::Attach {
                attachments,
                is_turn_energy: false,
            });
        }
    }

    choices
}

// Helper function to generate all possible distributions of 'count' energy
// across the available Pokémon
pub(crate) fn generate_distributions(
    target_indices: &[usize],
    remaining: usize,
    start_idx: usize,
    current: &mut Vec<usize>,
    result: &mut Vec<Vec<usize>>,
) {
    if remaining == 0 {
        result.push(current.clone());
        return;
    }

    if start_idx >= target_indices.len() {
        return;
    }

    // Try different amounts for the current Pokémon
    for amount in 0..=remaining {
        current[start_idx] = amount;
        generate_distributions(
            target_indices,
            remaining - amount,
            start_idx + 1,
            current,
            result,
        );
    }
    current[start_idx] = 0;
}

/// Lunala's Wings of the Moone (C1 066, C1 198, P-C 008): "Move all Energy from this Pokémon to your
/// Benched Pokémon in any way you like." The choices of one step, one Energy per choice, in a FIXED
/// order (coordinator-088 Q2): the lowest `EnergyType` still on the Active Pokémon moves next, and
/// within one type the destinations never decrease (`last_move` is the step before: the type moved
/// and the Benched Pokémon it went to), while a new type starts again from the first Benched
/// Pokémon. So each final board is reached by exactly one path. Upstream's
/// `active_energy_to_bench_choices` offers every type on the Active Pokémon to every Benched Pokémon
/// at every step, which reaches the same boards by many paths (81 paths to the 15 boards of four [P]
/// on three Benched Pokémon). Empty once the Active Pokémon has no Energy, or with no Benched
/// Pokémon: there is no early stop.
pub(crate) fn ordered_active_energy_to_bench_choices(
    state: &State,
    player: usize,
    last_move: Option<(EnergyType, usize)>,
) -> Vec<SimpleAction> {
    let Some(active) = state.in_play_pokemon[player][0].as_ref() else {
        return Vec::new();
    };
    let Some(energy_type) = active.attached_energy.iter().copied().min() else {
        return Vec::new();
    };
    let floor = match last_move {
        Some((moved_type, moved_to)) if moved_type == energy_type => moved_to,
        _ => 0,
    };
    state
        .enumerate_bench_pokemon(player)
        .filter(|(in_play_idx, _)| *in_play_idx >= floor)
        .map(|(to_in_play_idx, _)| SimpleAction::MoveActiveEnergyToBenchAndReoffer {
            to_in_play_idx,
            energy_type,
        })
        .collect()
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_energy_any_way_choices_empty_or_zero() {
        let choices = energy_any_way_choices(&[], EnergyType::Psychic, 3);
        assert!(choices.is_empty());

        let choices = energy_any_way_choices(&[0, 2], EnergyType::Psychic, 0);
        assert!(choices.is_empty());
    }

    #[test]
    fn test_energy_any_way_choices_two_targets_three_energy() {
        let choices = energy_any_way_choices(&[0, 2], EnergyType::Psychic, 3);
        assert_eq!(choices.len(), 4);

        let expected = [
            vec![(3, EnergyType::Psychic, 2)],
            vec![(1, EnergyType::Psychic, 0), (2, EnergyType::Psychic, 2)],
            vec![(2, EnergyType::Psychic, 0), (1, EnergyType::Psychic, 2)],
            vec![(3, EnergyType::Psychic, 0)],
        ];

        for (i, choice) in choices.iter().enumerate() {
            if let SimpleAction::Attach { attachments, .. } = choice {
                assert_eq!(attachments, &expected[i]);
            } else {
                panic!("Expected SimpleAction::Attach");
            }
        }
    }

    #[test]
    fn test_energy_any_way_choices_three_targets_two_energy() {
        let choices = energy_any_way_choices(&[0, 1, 3], EnergyType::Psychic, 2);
        assert_eq!(choices.len(), 6);

        let expected = [
            vec![(2, EnergyType::Psychic, 3)],
            vec![(1, EnergyType::Psychic, 1), (1, EnergyType::Psychic, 3)],
            vec![(2, EnergyType::Psychic, 1)],
            vec![(1, EnergyType::Psychic, 0), (1, EnergyType::Psychic, 3)],
            vec![(1, EnergyType::Psychic, 0), (1, EnergyType::Psychic, 1)],
            vec![(2, EnergyType::Psychic, 0)],
        ];

        for (i, choice) in choices.iter().enumerate() {
            if let SimpleAction::Attach { attachments, .. } = choice {
                assert_eq!(attachments, &expected[i]);
            } else {
                panic!("Expected SimpleAction::Attach");
            }
        }
    }

    /// Player 0's Lunala (C1 066) holding `energy`, with a Bulbasaur in each Bench slot of `bench`.
    fn lunala_board(energy: Vec<EnergyType>, bench: &[usize]) -> State {
        use crate::{card_ids::CardId, models::PlayedCard};
        let mut state = State::default();
        state.set_board(
            vec![PlayedCard::from_id(CardId::C1066Lunala).with_energy(energy)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        for &in_play_idx in bench {
            state.in_play_pokemon[0][in_play_idx] =
                Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
        }
        state
    }

    /// The (Energy type, Benched Pokémon) of each Wings of the Moone choice.
    fn moves(choices: Vec<SimpleAction>) -> Vec<(EnergyType, usize)> {
        choices
            .into_iter()
            .map(|choice| match choice {
                SimpleAction::MoveActiveEnergyToBenchAndReoffer {
                    to_in_play_idx,
                    energy_type,
                } => (energy_type, to_in_play_idx),
                other => panic!("Expected MoveActiveEnergyToBenchAndReoffer, got {other:?}"),
            })
            .collect()
    }

    #[test]
    fn test_ordered_active_energy_to_bench_choices_lowest_type_from_the_last_destination_on() {
        use EnergyType::{Psychic, Water};
        // [W] comes before [P] in `EnergyType`'s order, whatever the order of attachment, and the
        // empty slot 2 is skipped.
        let state = lunala_board(vec![Psychic, Water, Psychic], &[1, 3]);
        assert_eq!(
            moves(ordered_active_energy_to_bench_choices(&state, 0, None)),
            vec![(Water, 1), (Water, 3)]
        );

        let state = lunala_board(vec![Psychic, Psychic], &[1, 2, 3]);
        // A new type starts again from slot 1, wherever the last [W] went.
        assert_eq!(
            moves(ordered_active_energy_to_bench_choices(&state, 0, Some((Water, 3)))),
            vec![(Psychic, 1), (Psychic, 2), (Psychic, 3)]
        );
        // Within [P], never below the last [P]'s Benched Pokémon.
        assert_eq!(
            moves(ordered_active_energy_to_bench_choices(&state, 0, Some((Psychic, 2)))),
            vec![(Psychic, 2), (Psychic, 3)]
        );
        assert_eq!(
            moves(ordered_active_energy_to_bench_choices(&state, 0, Some((Psychic, 3)))),
            vec![(Psychic, 3)]
        );
    }

    /// Nothing is offered with no Energy on the Active Pokémon (not reachable in play: the attack
    /// costs [P][P]), with no Benched Pokémon, or with no Active Pokémon.
    #[test]
    fn test_ordered_active_energy_to_bench_choices_empty_without_energy_bench_or_active() {
        let no_energy = lunala_board(vec![], &[1, 2]);
        assert!(ordered_active_energy_to_bench_choices(&no_energy, 0, None).is_empty());
        let no_bench = lunala_board(vec![EnergyType::Psychic; 2], &[]);
        assert!(ordered_active_energy_to_bench_choices(&no_bench, 0, None).is_empty());
        let mut no_active = lunala_board(vec![EnergyType::Psychic; 2], &[1, 2]);
        no_active.in_play_pokemon[0][0] = None;
        assert!(ordered_active_energy_to_bench_choices(&no_active, 0, None).is_empty());
    }
}
