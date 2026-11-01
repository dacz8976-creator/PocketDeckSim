// Ported from upstream deckgym-core #433 (tests/pokemon/charizard_flame_aura_test.rs, as of e7cc5ce), with fork tests added at the end (a multi-Energy attach from the Energy Zone, an attach from the discard pile, and one non-turn Energy Zone attach against both Flame Aura and Darkrai ex's Nightmare Aura).
use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
};
use rand::{rngs::StdRng, SeedableRng};

fn attach(energy: EnergyType, in_play_idx: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, energy, in_play_idx)],
            is_turn_energy: true,
        },
        is_stack: false,
    }
}

#[test]
fn test_charizard_flame_aura_damages_opponent_active_on_fire_attach() {
    // Flame Aura: Whenever you attach a [R] Energy from your Energy Zone to this Pokémon,
    // do 30 damage to your opponent's Active Pokémon.
    for charizard in [CardId::C1018Charizard, CardId::C1136Charizard] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(charizard)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );

        game.apply_action(&attach(EnergyType::Fire, 0));

        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).attached_energy.len(), 1);
        assert_eq!(state.get_active(1).get_remaining_hp(), 40);
    }
}

#[test]
fn test_charizard_flame_aura_works_from_the_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::C1018Charizard),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&attach(EnergyType::Fire, 1));

    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 40);
}

#[test]
fn test_charizard_flame_aura_ignores_non_fire_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1018Charizard)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&attach(EnergyType::Water, 0));

    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 70);
}

// ---------------------------------------------------------------------------------------------
// Fork additions.
// ---------------------------------------------------------------------------------------------

/// One branch of an attack whose effect attaches Energy from the Energy Zone to a Benched Pokémon:
/// the attach it queued (none on a branch that attaches nothing), the Energy the Benched Pokémon
/// ends with, and the remaining HP of the opponent's Active, Wailord ex (250 HP).
struct BenchAttachBranch {
    queued: Option<SimpleAction>,
    benched_energy: Vec<EnergyType>,
    opponent_remaining_hp: u32,
}

/// Plays `attacker`'s first attack over every branch of its forecast, with `benched` as the only
/// Benched Pokémon, and resolves the attach the branch queues.
fn bench_attach_branches(attacker: PlayedCard, benched: CardId) -> Vec<BenchAttachBranch> {
    let attacker_id = CardId::from_card_id(&attacker.get_id()).expect("the attacker's printing");
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![attacker, PlayedCard::from_id(benched)],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    let initial = game.get_state_clone();
    let attack = Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    };
    let (_, branches) = try_forecast_action(&initial, &attack)
        .expect("the attack's forecast should be exactly priced")
        .into_branches();
    branches
        .into_iter()
        .map(|branch| {
            let mut state = initial.clone();
            branch(&mut StdRng::seed_from_u64(0), &mut state, &attack);
            let (_, choices) = state.generate_possible_actions();
            let queued = choices.into_iter().find(|choice| {
                matches!(
                    choice.action,
                    SimpleAction::Attach {
                        is_turn_energy: false,
                        ..
                    }
                )
            });
            game.set_state(state);
            if let Some(queued) = &queued {
                game.apply_action(queued);
            }
            let state = game.get_state_clone();
            BenchAttachBranch {
                queued: queued.map(|choice| choice.action),
                benched_energy: state.in_play_pokemon[0][1]
                    .as_ref()
                    .expect("the Benched Pokémon stays in play")
                    .attached_energy
                    .clone(),
                opponent_remaining_hp: state.get_active(1).get_remaining_hp(),
            }
        })
        .collect()
}

/// Flame Aura fires once for each [R] Energy of a multi-Energy attach from the Energy Zone. Moltres
/// ex's Inferno Dance ("Flip 3 coins. Take an amount of [R] Energy from your Energy Zone equal to the
/// number of heads and attach it to your Benched [R] Pokémon in any way you like.") puts every heads'
/// Energy on the only Benched Charizard in one attach, and each Energy does 30.
#[test]
fn test_charizard_flame_aura_fires_once_per_energy_of_a_multi_energy_zone_attach() {
    let moltres = PlayedCard::from_id(CardId::A1047MoltresEx).with_energy(vec![EnergyType::Fire]);
    let branches = bench_attach_branches(moltres, CardId::C1018Charizard);

    let mut heads: Vec<usize> = branches
        .iter()
        .map(|branch| branch.benched_energy.len())
        .collect();
    heads.sort();
    assert_eq!(heads, [0, 1, 2, 3]);
    for branch in &branches {
        let count = branch.benched_energy.len();
        assert!(branch
            .benched_energy
            .iter()
            .all(|energy| *energy == EnergyType::Fire));
        assert_eq!(
            branch.opponent_remaining_hp,
            250 - 30 * count as u32,
            "{count} [R] Energy attached"
        );
        if count == 3 {
            assert_eq!(
                branch.queued,
                Some(SimpleAction::Attach {
                    attachments: vec![(3, EnergyType::Fire, 1)],
                    is_turn_energy: false,
                }),
                "the three Energy come in a single attach"
            );
        }
    }
}

/// Flame Aura reads "from your Energy Zone": a [R] Energy attached from the discard pile does
/// nothing.
#[test]
fn test_charizard_flame_aura_ignores_an_attach_from_the_discard_pile() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1018Charizard)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut state = game.get_state_clone();
    state.discard_energies[0] = vec![EnergyType::Fire];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::AttachTypedFromDiscard {
            in_play_idx: 0,
            energy_type: EnergyType::Fire,
            count: 1,
        },
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 70);
}

/// The difference the shared hook keeps, on one attach from the Energy Zone that is not the turn's
/// Energy: Sableye's Jeweled Gift ("Take a random Energy from among [G], [R], [W], [L], [P], [F], [D],
/// and [M] Energy from your Energy Zone and attach it to 1 of your Benched Pokémon."). Flame Aura
/// fires on the [R] branch. Darkrai ex's Nightmare Aura, read as the turn's Energy attach only
/// (only_turn_energy), stays silent on every branch, the [D] one included; its turn's-Energy cases
/// are in darkrai_ex_test.rs.
#[test]
fn test_jeweled_gift_fires_flame_aura_but_not_nightmare_aura() {
    let sableye =
        || PlayedCard::from_id(CardId::B3a040Sableye).with_energy(vec![EnergyType::Colorless]);
    let charizard = bench_attach_branches(sableye(), CardId::C1018Charizard);
    let darkrai = bench_attach_branches(sableye(), CardId::A2110DarkraiEx);

    for branches in [&charizard, &darkrai] {
        assert_eq!(branches.len(), 8, "one branch per printed Energy type");
        assert!(branches
            .iter()
            .all(|branch| branch.benched_energy.len() == 1));
    }
    for branch in &charizard {
        let expected = if branch.benched_energy == [EnergyType::Fire] {
            220
        } else {
            250
        };
        assert_eq!(
            branch.opponent_remaining_hp, expected,
            "Charizard given {:?}",
            branch.benched_energy
        );
    }
    assert!(darkrai
        .iter()
        .any(|branch| branch.benched_energy == [EnergyType::Darkness]));
    for branch in &darkrai {
        assert_eq!(
            branch.opponent_remaining_hp, 250,
            "Darkrai ex given {:?}",
            branch.benched_energy
        );
    }
}
