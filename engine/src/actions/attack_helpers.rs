use std::collections::BTreeMap;

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

/// One Wings of the Moone distribution: `(amount, energy_type, to_in_play_idx)` entries, as
/// `Attach`'s tuples.
type WingsMoves = Vec<(u32, EnergyType, usize)>;

/// Lunala's Wings of the Moone (C1 066, C1 198, P-C 008): the most final boards offered as one
/// choice (coordinator-132). Above it, one choice per Energy type.
pub(crate) const WINGS_OF_THE_MOONE_ONE_FRAME_MAX: usize = 256;

/// The ways to split `k` Energy of one type over `b` Benched Pokémon: C(k + b - 1, b - 1),
/// saturating at `usize::MAX`. With no Bench there is no way, unless there is no Energy.
fn wings_of_the_moone_splits(k: usize, b: usize) -> usize {
    if b == 0 {
        return usize::from(k == 0);
    }
    let mut ways: usize = 1;
    for i in 1..b {
        // `ways` is C(k + i - 1, i - 1) here, so `ways * (k + i) / i` is exactly C(k + i, i).
        ways = match ways.checked_mul(k.saturating_add(i)) {
            Some(product) => product / i,
            None => return usize::MAX,
        };
    }
    ways
}

/// The number of final boards of Wings of the Moone: the product over the Energy types on the
/// Active Pokémon of C(k_t + b - 1, b - 1), `per_type` holding the k_t (one per type present) and
/// `bench` = b, the number of Benched Pokémon. Saturates at `usize::MAX`; 0 when there is Energy
/// but no Bench.
pub(crate) fn wings_of_the_moone_board_count(per_type: &[usize], bench: usize) -> usize {
    per_type.iter().fold(1, |count, &k| {
        count.saturating_mul(wings_of_the_moone_splits(k, bench))
    })
}

/// Coordinator-132's switch: every final board in one choice when there are at most 256 of them,
/// otherwise one choice per Energy type.
pub(crate) fn wings_of_the_moone_in_one_frame(board_count: usize) -> bool {
    board_count <= WINGS_OF_THE_MOONE_ONE_FRAME_MAX
}

/// (type, count) of the Energy on `player`'s Active Pokémon, lowest `EnergyType` first; empty with
/// no Active Pokémon.
fn active_energy_by_type(state: &State, player: usize) -> Vec<(EnergyType, usize)> {
    let mut by_type = BTreeMap::<EnergyType, usize>::new();
    if let Some(active) = state.in_play_pokemon[player][0].as_ref() {
        for &energy in &active.attached_energy {
            *by_type.entry(energy).or_insert(0) += 1;
        }
    }
    by_type.into_iter().collect()
}

/// The in-play indices of `player`'s Benched Pokémon, ascending (empty slots skipped).
fn bench_indices(state: &State, player: usize) -> Vec<usize> {
    state
        .enumerate_bench_pokemon(player)
        .map(|(in_play_idx, _)| in_play_idx)
        .collect()
}

/// Every split of `count` Energy of `energy_type` over the Benched Pokémon at `bench`, each as
/// entries in ascending destination with no zero amounts (`generate_distributions` yields each
/// split once).
fn wings_of_the_moone_type_splits(
    energy_type: EnergyType,
    count: usize,
    bench: &[usize],
) -> Vec<WingsMoves> {
    let mut distributions = Vec::new();
    generate_distributions(bench, count, 0, &mut vec![0; bench.len()], &mut distributions);
    distributions
        .into_iter()
        .map(|dist| {
            bench
                .iter()
                .zip(dist)
                .filter(|(_, amount)| *amount > 0)
                .map(|(&to_in_play_idx, amount)| (amount as u32, energy_type, to_in_play_idx))
                .collect()
        })
        .collect()
}

/// Lunala's Wings of the Moone (C1 066, C1 198, P-C 008): "Move all Energy from this Pokémon to
/// your Benched Pokémon in any way you like." The attack's first choice, its shape decided here
/// once (coordinator-132). With at most 256 final boards: every final board of all the Active
/// Pokémon's Energy, one option each (the product of the types' splits, the lowest `EnergyType`
/// first and varying slowest, entries joined type by type). Otherwise: the splits of the lowest
/// type alone (`wings_of_the_moone_next_type_choices`), and each later type follows the same way.
/// So each final board is reached by exactly one path. Upstream (#438) moves one Energy per choice
/// and reaches the same boards by many paths (81 paths to the 15 boards of four [P] on three
/// Benched Pokémon). Empty with no Active Pokémon, no Energy on it or no Benched Pokémon: there is
/// no early stop.
pub(crate) fn wings_of_the_moone_choices(state: &State, player: usize) -> Vec<SimpleAction> {
    let bench = bench_indices(state, player);
    let per_type = active_energy_by_type(state, player);
    if bench.is_empty() || per_type.is_empty() {
        return Vec::new();
    }
    let counts: Vec<usize> = per_type.iter().map(|&(_, count)| count).collect();
    if !wings_of_the_moone_in_one_frame(wings_of_the_moone_board_count(&counts, bench.len())) {
        return wings_of_the_moone_next_type_choices(state, player);
    }
    let mut boards: Vec<WingsMoves> = vec![Vec::new()];
    for (energy_type, count) in per_type {
        let splits = wings_of_the_moone_type_splits(energy_type, count, &bench);
        let mut extended = Vec::with_capacity(boards.len() * splits.len());
        for board in &boards {
            for split in &splits {
                let mut moves = board.clone();
                moves.extend_from_slice(split);
                extended.push(moves);
            }
        }
        boards = extended;
    }
    boards
        .into_iter()
        .map(|moves| SimpleAction::DistributeActiveEnergyToBench { moves })
        .collect()
}

/// A per-type choice of Wings of the Moone: every split of the lowest `EnergyType` still on
/// `player`'s Active Pokémon over its Benched Pokémon. Empty once the Active Pokémon holds no
/// Energy (so after any one-choice distribution), or with no Benched or no Active Pokémon.
pub(crate) fn wings_of_the_moone_next_type_choices(
    state: &State,
    player: usize,
) -> Vec<SimpleAction> {
    let bench = bench_indices(state, player);
    let Some(&(energy_type, count)) = active_energy_by_type(state, player).first() else {
        return Vec::new();
    };
    if bench.is_empty() {
        return Vec::new();
    }
    wings_of_the_moone_type_splits(energy_type, count, &bench)
        .into_iter()
        .map(|moves| SimpleAction::DistributeActiveEnergyToBench { moves })
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

    /// The entries of each Wings of the Moone choice.
    fn moves(choices: Vec<SimpleAction>) -> Vec<WingsMoves> {
        choices
            .into_iter()
            .map(|choice| match choice {
                SimpleAction::DistributeActiveEnergyToBench { moves } => moves,
                other => panic!("Expected DistributeActiveEnergyToBench, got {other:?}"),
            })
            .collect()
    }

    /// Coordinator-132's switch at 255, 256 and 257 final boards (one choice at 256, one per type
    /// at 257), and the count it reads on boards each side of it: the product over the Energy
    /// types of C(k + b - 1, b - 1).
    #[test]
    fn test_wings_of_the_moone_board_count_and_switch_at_255_256_and_257() {
        assert!(wings_of_the_moone_in_one_frame(255));
        assert!(wings_of_the_moone_in_one_frame(256));
        assert!(!wings_of_the_moone_in_one_frame(257));
        for (per_type, bench, count, one_frame) in [
            (vec![16, 4, 2], 2, 255, true),
            (vec![3, 3, 3, 3], 2, 256, true),
            (vec![7, 7, 3], 2, 256, true),
            (vec![15, 15], 2, 256, true),
            (vec![255], 2, 256, true),
            (vec![256], 2, 257, false),
            (vec![6, 1, 1], 3, 252, true),
            (vec![5, 1, 1], 3, 189, true),
            (vec![2, 1, 1], 3, 54, true),
            (vec![4], 3, 15, true),
            (vec![4, 2, 1], 3, 270, false),
            (vec![5, 4], 3, 315, false),
            (vec![3, 2, 2], 3, 360, false),
            (vec![21], 3, 253, true),
            (vec![22], 3, 276, false),
            (vec![30, 30, 30], 1, 1, true),
        ] {
            let boards = wings_of_the_moone_board_count(&per_type, bench);
            assert_eq!(boards, count, "{per_type:?} on {bench} Benched Pokémon");
            assert_eq!(wings_of_the_moone_in_one_frame(boards), one_frame, "{per_type:?} on {bench}");
        }
        // Energy but no Bench: no final board. No Energy: the one board where nothing moves.
        assert_eq!(wings_of_the_moone_board_count(&[2], 0), 0);
        assert_eq!(wings_of_the_moone_board_count(&[], 3), 1);
        // Saturates instead of overflowing.
        assert_eq!(wings_of_the_moone_board_count(&[usize::MAX], 3), usize::MAX);
        assert_eq!(wings_of_the_moone_board_count(&[1_000_000; 8], 3), usize::MAX);
    }

    #[test]
    fn test_wings_of_the_moone_choices_one_frame_and_per_type() {
        use EnergyType::{Lightning, Psychic, Water};
        // 2 x 3 = 6 final boards, all in one choice: [W] before [P] in `EnergyType`'s order,
        // whatever the order of attachment, the first type varying slowest; the empty slot 2 is
        // never named.
        let state = lunala_board(vec![Psychic, Water, Psychic], &[1, 3]);
        assert_eq!(
            moves(wings_of_the_moone_choices(&state, 0)),
            vec![
                vec![(1, Water, 3), (2, Psychic, 3)],
                vec![(1, Water, 3), (1, Psychic, 1), (1, Psychic, 3)],
                vec![(1, Water, 3), (2, Psychic, 1)],
                vec![(1, Water, 1), (2, Psychic, 3)],
                vec![(1, Water, 1), (1, Psychic, 1), (1, Psychic, 3)],
                vec![(1, Water, 1), (2, Psychic, 1)],
            ]
        );
        // [W][W][W][L][L][P][P] on three Benched Pokémon has 10 x 6 x 6 = 360 final boards, so the
        // first choice is the 10 splits of the three [W] alone.
        let state = lunala_board(
            vec![Psychic, Psychic, Lightning, Lightning, Water, Water, Water],
            &[1, 2, 3],
        );
        let first = moves(wings_of_the_moone_choices(&state, 0));
        assert_eq!(first.len(), 10);
        for split in &first {
            assert!(split.iter().all(|&(_, energy_type, _)| energy_type == Water), "{split:?}");
            assert_eq!(split.iter().map(|&(amount, ..)| amount).sum::<u32>(), 3, "{split:?}");
        }
        assert_eq!(moves(wings_of_the_moone_next_type_choices(&state, 0)), first);
        // Each later choice is the lowest type left, alone.
        let state = lunala_board(vec![Psychic, Psychic, Lightning], &[1, 2, 3]);
        assert_eq!(
            moves(wings_of_the_moone_next_type_choices(&state, 0)),
            vec![vec![(1, Lightning, 3)], vec![(1, Lightning, 2)], vec![(1, Lightning, 1)]]
        );
    }

    /// Nothing is offered with no Energy on the Active Pokémon (not reachable in play: the attack
    /// costs [P][P]), with no Benched Pokémon, or with no Active Pokémon.
    #[test]
    fn test_wings_of_the_moone_choices_empty_without_energy_bench_or_active() {
        let no_energy = lunala_board(vec![], &[1, 2]);
        let no_bench = lunala_board(vec![EnergyType::Psychic; 2], &[]);
        let mut no_active = lunala_board(vec![EnergyType::Psychic; 2], &[1, 2]);
        no_active.in_play_pokemon[0][0] = None;
        for state in [no_energy, no_bench, no_active] {
            assert!(wings_of_the_moone_choices(&state, 0).is_empty());
            assert!(wings_of_the_moone_next_type_choices(&state, 0).is_empty());
        }
    }
}
