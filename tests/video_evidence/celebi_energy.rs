//! Source-qualified regression candidate for the SweetGameBuddy turn-14 Celebi position.
//!
//! Source: `Boss Folder/direct-video-benchmark-2026-09-06/{SOURCE,CASES}.json`, case
//! `sweetgamebuddy-turn14-energy-before-attack`. The recording establishes the public fields
//! needed by these assertions, but not complete hands, decks, deck order, or prior turn history.
//! These are independent constructed states, not a replay or a claim of globally optimal play.

use deckgym::{
    actions::{try_forecast_action, Action, CoinPaths, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    observation::{PlayerObservation, RevealedKnowledge},
    players::{
        public_clock_effect_value_function, EndTurnPlayer, ExpectiMiniMaxPlayer, Player,
    },
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

const SEED: u64 = 47;
const EPSILON: f64 = 1e-12;

#[derive(Debug, PartialEq)]
struct ForecastRow {
    heads: usize,
    probability: f64,
    rampardos_hp: Option<u32>,
    actor_zero_wins: bool,
}

fn benchmark_state(with_dawn: bool) -> State {
    // The one-card remaining decks and opponent hand are count-preserving initialization
    // scaffolds. Their identities and counts are not claims about the recording.
    let own_deck = Deck::from_string("Energy: Grass\n1 Pinsir A1 026").unwrap();
    let opponent_deck =
        Deck::from_string("Energy: Fighting\n1 Sudowoodo A2a 036").unwrap();
    let mut state = State::new(&own_deck, &opponent_deck);
    state.current_player = 0;
    state.turn_count = 7; // Synthetic engine clock; the video UI says turn 14.
    state.points = [2, 2];
    state.energy_zone[0].current = Some(EnergyType::Grass);
    state.energy_zone[0].next = Some(EnergyType::Grass);
    state.energy_zone[1].current = Some(EnergyType::Fighting);
    state.energy_zone[1].next = Some(EnergyType::Fighting);
    state.hands[0] = vec![get_card_by_enum(CardId::A1031Skiddo)];
    if with_dawn {
        state.hands[0].push(get_card_by_enum(CardId::A2154Dawn));
    }
    state.hands[1] = vec![get_card_by_enum(CardId::PA001Potion)];

    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1a003CelebiEx)
                .with_energy(vec![EnergyType::Grass; 3]),
            PlayedCard::from_id(CardId::A1026Pinsir),
        ],
        vec![
            PlayedCard::from_id(CardId::A2089Rampardos)
                .with_energy(vec![EnergyType::Fighting])
                .with_damage(50),
            PlayedCard::from_id(CardId::A2a036Sudowoodo)
                .with_energy(vec![EnergyType::Fighting]),
            PlayedCard::from_id(CardId::A2092Lucario)
                .with_energy(vec![EnergyType::Fighting]),
            PlayedCard::from_id(CardId::A2144SkullFossil),
        ],
    );
    state
}

fn players(state: &State) -> Vec<Box<dyn Player>> {
    vec![
        Box::new(EndTurnPlayer {
            deck: state.decks[0].clone(),
        }),
        Box::new(EndTurnPlayer {
            deck: state.decks[1].clone(),
        }),
    ]
}

fn generated_action(
    state: &State,
    description: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) -> Action {
    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, 0, "{description} must belong to the recorded actor");
    let matches: Vec<_> = actions
        .into_iter()
        .filter(|action| predicate(&action.action))
        .collect();
    assert_eq!(
        matches.len(),
        1,
        "expected exactly one legal {description}, found {matches:?}"
    );
    matches.into_iter().next().unwrap()
}

fn powerful_bloom(state: &State) -> Action {
    generated_action(state, "Powerful Bloom attack", |action| {
        matches!(action, SimpleAction::Attack(attack) if attack.title == "Powerful Bloom")
    })
}

fn forecast_rows(state: &State) -> Vec<ForecastRow> {
    let action = powerful_bloom(state);
    let branches = try_forecast_action(state, &action)
        .expect("Powerful Bloom must be exactly forecastable")
        .into_branches_with_coin_paths();
    let mut rows = Vec::new();

    for (probability, mutation, paths) in branches {
        let heads = match paths {
            CoinPaths::Exact(sequences) => {
                assert!(!sequences.is_empty(), "each forecast branch needs a coin path");
                let heads = sequences[0].0.iter().filter(|face| **face).count();
                assert!(
                    sequences
                        .iter()
                        .all(|sequence| sequence.0.iter().filter(|face| **face).count() == heads),
                    "one forecast branch must not combine different head counts"
                );
                heads
            }
            other => panic!("Powerful Bloom should have finite exact coin paths, got {other:?}"),
        };
        let mut after = state.clone();
        let mut rng = StdRng::seed_from_u64(SEED);
        mutation(&mut rng, &mut after, &action);
        rows.push(ForecastRow {
            heads,
            probability,
            rampardos_hp: after.in_play_pokemon[1][0]
                .as_ref()
                .map(PlayedCard::get_remaining_hp),
            actor_zero_wins: after.winner == Some(deckgym::state::GameOutcome::Win(0)),
        });
    }
    rows.sort_by_key(|row| row.heads);
    rows
}

fn assert_forecast(
    state: &State,
    expected: &[(usize, f64, Option<u32>, bool)],
    expected_ko_probability: f64,
) {
    let rows = forecast_rows(state);
    assert_eq!(rows.len(), expected.len());
    for (actual, expected) in rows.iter().zip(expected) {
        assert_eq!(actual.heads, expected.0);
        assert!(
            (actual.probability - expected.1).abs() <= EPSILON,
            "heads={}: expected probability {}, got {}",
            actual.heads,
            expected.1,
            actual.probability
        );
        assert_eq!(actual.rampardos_hp, expected.2, "heads={}", actual.heads);
        assert_eq!(actual.actor_zero_wins, expected.3, "heads={}", actual.heads);
    }
    let total_probability: f64 = rows.iter().map(|row| row.probability).sum();
    let ko_probability: f64 = rows
        .iter()
        .filter(|row| row.actor_zero_wins)
        .map(|row| row.probability)
        .sum();
    assert!((total_probability - 1.0).abs() <= EPSILON);
    assert!((ko_probability - expected_ko_probability).abs() <= EPSILON);
}

fn apply_generated(
    game: &mut Game<'_>,
    description: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) {
    let action = generated_action(&game.get_state_clone(), description, predicate);
    game.apply_action(&action);
}

#[test]
fn celebi_three_and_four_energy_forecasts_match_the_video_bound_physical_oracle() {
    let before = benchmark_state(false);
    assert_eq!(before.get_active(0).attached_energy.len(), 3);
    assert_eq!(before.get_active(1).get_remaining_hp(), 100);
    assert_eq!(before.points, [2, 2]);

    assert_forecast(
        &before,
        &[
            (0, 0.125, Some(100), false),
            (1, 0.375, Some(30), false),
            (2, 0.375, None, true),
            (3, 0.125, None, true),
        ],
        0.5,
    );

    let mut direct = Game::from_state(before.clone(), players(&before), SEED);
    apply_generated(&mut direct, "turn Energy attachment to Celebi", |action| {
        matches!(action, SimpleAction::Attach { attachments, is_turn_energy: true }
            if attachments == &vec![(1, EnergyType::Grass, 0)])
    });
    let after_attach = direct.get_state_clone();
    assert_eq!(after_attach.get_active(0).attached_energy.len(), 4);
    assert_forecast(
        &after_attach,
        &[
            (0, 0.0625, Some(100), false),
            (1, 0.25, Some(30), false),
            (2, 0.375, None, true),
            (3, 0.25, None, true),
            (4, 0.0625, None, true),
        ],
        0.6875,
    );
}

#[test]
fn direct_and_dawn_routes_both_reach_an_actionable_four_coin_attack() {
    let direct_state = benchmark_state(true);
    let mut direct = Game::from_state(direct_state.clone(), players(&direct_state), SEED);
    apply_generated(&mut direct, "turn Energy attachment to Celebi", |action| {
        matches!(action, SimpleAction::Attach { attachments, is_turn_energy: true }
            if attachments == &vec![(1, EnergyType::Grass, 0)])
    });
    let direct_attack_state = direct.get_state_clone();
    assert_eq!(direct_attack_state.get_active(0).attached_energy.len(), 4);
    let _direct_attack = powerful_bloom(&direct_attack_state);

    let dawn_state = benchmark_state(true);
    let mut dawn = Game::from_state(dawn_state.clone(), players(&dawn_state), SEED);
    apply_generated(&mut dawn, "turn Energy attachment to Pinsir", |action| {
        matches!(action, SimpleAction::Attach { attachments, is_turn_energy: true }
            if attachments == &vec![(1, EnergyType::Grass, 1)])
    });
    apply_generated(&mut dawn, "Dawn play", |action| {
        matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == "Dawn")
    });
    apply_generated(&mut dawn, "Dawn transfer from Pinsir to Celebi", |action| {
        matches!(action, SimpleAction::MoveEnergy {
            from_in_play_idx: 1,
            to_in_play_idx: 0,
            energy_type: EnergyType::Grass,
            amount: 1,
        })
    });
    let dawn_attack_state = dawn.get_state_clone();
    assert_eq!(dawn_attack_state.get_active(0).attached_energy.len(), 4);
    assert_eq!(dawn_attack_state.in_play_pokemon[0][1]
        .as_ref()
        .unwrap()
        .attached_energy
        .len(), 0);
    let _dawn_attack = powerful_bloom(&dawn_attack_state);

    // Both complete legal routes finish at the same physical forecast. This does not claim
    // Dawn is strategically preferable to the cheaper direct attachment.
    assert_eq!(forecast_rows(&direct_attack_state), forecast_rows(&dawn_attack_state));
}

fn assert_k3_reaches_four_energy_before_attacking(state: State) {
    let k3: Box<dyn Player> = Box::new(ExpectiMiniMaxPlayer {
        deck: state.decks[0].clone(),
        max_depth: 3,
        write_debug_trees: false,
        value_function: Box::new(public_clock_effect_value_function),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    });
    let opponent: Box<dyn Player> = Box::new(EndTurnPlayer {
        deck: state.decks[1].clone(),
    });
    let mut game = Game::from_state(state, vec![k3, opponent], SEED);

    for _ in 0..8 {
        let before = game.get_state_clone();
        if before.current_player != 0 {
            break;
        }
        let chosen = game.play_tick();
        if let SimpleAction::Attack(attack) = &chosen.action {
            assert_eq!(attack.title, "Powerful Bloom");
            assert_eq!(
                before.get_active(0).attached_energy.len(),
                4,
                "k3 must not take the lower-probability three-coin attack"
            );
            return;
        }
    }
    panic!("k3 did not reach an actionable four-Energy Powerful Bloom in the same turn");
}

#[test]
fn k3_reaches_the_supported_four_energy_attack_without_pinning_incidental_setup_order() {
    let state = benchmark_state(true);

    // The opponent fillers exist only to preserve unknown counts. Prove this benchmark's policy
    // boundary redacts their identities, then check the semantic line under both substitutions.
    let original_view = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    assert!(original_view.visible_state().hands[1]
        .iter()
        .all(|card| *card == Card::Unknown));
    assert!(original_view.visible_state().decks[1].cards
        .iter()
        .all(|card| *card == Card::Unknown));

    let mut substituted = state.clone();
    substituted.hands[1].fill(get_card_by_enum(CardId::PA002XSpeed));
    substituted.decks[1]
        .cards
        .fill(get_card_by_enum(CardId::A1003Venusaur));
    let substituted_view =
        PlayerObservation::from_state(&substituted, 0, &RevealedKnowledge::default());
    assert_eq!(original_view, substituted_view);

    // Do not assert that Skiddo placement is first. Any same-turn setup order is acceptable if
    // the complete line reaches four Energy before Powerful Bloom.
    assert_k3_reaches_four_energy_before_attacking(state);
    assert_k3_reaches_four_energy_before_attacking(substituted);
}
