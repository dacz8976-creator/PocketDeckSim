use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    data_exporter::{DataExporter, ExportedDataPoint},
    database::get_card_by_enum,
    game_result_exporter::{ExportedMatchup, GameResultExporter},
    observation::{PlayerObservation, RevealedKnowledge},
    players::{
        create_players, parse_player_code, public_clock_effect_value_function,
        ExpectiMiniMaxPlayer, Player,
    },
    public_reply_evidence::{
        collect_public_reply_evidence, mark_selected, PublicReplyEvidence,
        PUBLIC_REPLY_EVIDENCE_SCHEMA,
    },
    simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler},
    test_support::load_test_decks,
    Game, State,
};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::{fs, path::PathBuf};
use uuid::Uuid;

fn saved_root() -> (State, u64) {
    let fixture: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/public_reply_observed.json")).unwrap();
    let state = serde_json::from_value(fixture["row"]["state"].clone()).unwrap();
    let seed = fixture["row"]["decision_randomness"]["search_seed"]
        .as_u64()
        .unwrap();
    (state, seed)
}

fn k3(state: &State) -> ExpectiMiniMaxPlayer {
    ExpectiMiniMaxPlayer {
        deck: state.decks[state.current_player].clone(),
        max_depth: 3,
        write_debug_trees: false,
        value_function: Box::new(public_clock_effect_value_function),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    }
}

fn is_x_speed(action: &Action) -> bool {
    matches!(
        &action.action,
        SimpleAction::Play { trainer_card } if trainer_card.name == "X Speed"
    )
}

fn assert_empty_evidence(evidence: &PublicReplyEvidence) {
    assert_eq!(evidence.schema, PUBLIC_REPLY_EVIDENCE_SCHEMA);
    assert!(evidence.records.is_empty());
    assert_eq!(evidence.total_occurrences, 0);
    assert_eq!(evidence.dropped_occurrences, 0);
}

fn observed_decision(
    state: &State,
    seed: u64,
    enabled: bool,
) -> (Action, Option<PublicReplyEvidence>, u64) {
    let observation = PlayerObservation::from_state(
        state,
        state.current_player,
        &RevealedKnowledge::default(),
    );
    let (_, actions) = state.generate_possible_actions();
    let mut bot = k3(state);
    let mut rng = StdRng::seed_from_u64(seed);
    let (chosen, evidence) = collect_public_reply_evidence(enabled, || {
        bot.decision_fn(&mut rng, &observation, &actions)
    });
    let next_rng_value = rng.next_u64();
    (chosen, evidence, next_rng_value)
}

fn assert_natural_witness(evidence: &PublicReplyEvidence) {
    assert!(evidence.total_occurrences > 0);
    assert!(!evidence.records.is_empty());
    assert_eq!(
        evidence.total_occurrences,
        evidence
            .records
            .iter()
            .map(|record| record.occurrences)
            .sum::<usize>()
            + evidence.dropped_occurrences
    );
    for record in &evidence.records {
        assert!(record.root_action.is_some(), "search evidence must be root-bound");
        assert_eq!(record.observer, 0);
        assert!(matches!(
            &record.witness_action.action,
            SimpleAction::Attack(attack) if attack.title == "Hit and Hide"
        ));
        assert_eq!(record.positive_branches, 2);
        assert!((record.probability_sum - 1.0).abs() < 1e-12);
        assert!(record.applied_leaf_value.is_finite());
        assert!(record.occurrences > 0);
    }
}

#[test]
fn observed_policy_emits_root_bound_hit_and_hide_certificates_and_marks_selection() {
    let (state, seed) = saved_root();
    let (chosen, evidence, _) = observed_decision(&state, seed, true);
    assert!(is_x_speed(&chosen), "saved public decision must retain its defense: {chosen:?}");

    let mut evidence = evidence.expect("enabled collection must return a decision scope");
    assert_natural_witness(&evidence);
    assert!(evidence.records.iter().all(|record| !record.selected));
    mark_selected(&mut evidence, &chosen);
    let (_, offered) = state.generate_possible_actions();
    assert!(evidence.records.iter().all(|record| {
        record
            .root_action
            .as_ref()
            .is_some_and(|root| offered.contains(root))
    }));
    assert!(evidence.records.iter().all(|record| {
        record.selected == (record.root_action.as_ref() == Some(&chosen))
    }));

    let threatening_root = evidence.records[0].root_action.clone().unwrap();
    mark_selected(&mut evidence, &threatening_root);
    assert!(evidence.records.iter().any(|record| record.selected));
    assert!(evidence.records.iter().all(|record| {
        record.selected == (record.root_action.as_ref() == Some(&threatening_root))
    }));
}

#[test]
fn collection_is_decision_and_search_rng_neutral() {
    let (state, seed) = saved_root();
    let (without_action, without_evidence, without_next) = observed_decision(&state, seed, false);
    let (with_action, with_evidence, with_next) = observed_decision(&state, seed, true);

    assert_eq!(without_action, with_action);
    assert_eq!(without_next, with_next, "telemetry must not consume search RNG");
    assert!(without_evidence.is_none());
    assert_natural_witness(&with_evidence.unwrap());
}

#[test]
fn hidden_identity_and_deck_order_changes_leave_serialized_evidence_unchanged() {
    let (state, seed) = saved_root();
    let mut alternate = state.clone();
    alternate.decks[0].cards.reverse();
    alternate.decks[1]
        .cards
        .fill(get_card_by_enum(CardId::A1001Bulbasaur));
    alternate.hands[1].fill(get_card_by_enum(CardId::PA001Potion));

    let base_view = PlayerObservation::from_state(&state, 0, &Default::default());
    let alternate_view = PlayerObservation::from_state(&alternate, 0, &Default::default());
    assert_eq!(base_view, alternate_view, "changed identities must remain concealed");

    let (base_action, base_evidence, base_next) = observed_decision(&state, seed, true);
    let (alternate_action, alternate_evidence, alternate_next) =
        observed_decision(&alternate, seed, true);
    assert_eq!(base_action, alternate_action);
    assert_eq!(base_next, alternate_next);
    assert_eq!(
        serde_json::to_value(base_evidence.unwrap()).unwrap(),
        serde_json::to_value(alternate_evidence.unwrap()).unwrap(),
        "serialized evidence must contain only the same public search facts"
    );
}

#[test]
fn untrusted_raw_search_and_unsupported_public_board_emit_no_success() {
    let (state, seed) = saved_root();
    let (_, actions) = state.generate_possible_actions();
    let mut raw_bot = k3(&state);
    let (_, raw_evidence) = collect_public_reply_evidence(true, || {
        raw_bot.decide_omniscient(&mut StdRng::seed_from_u64(seed), &state, &actions)
    });
    assert_empty_evidence(&raw_evidence.unwrap());

    let mut unsupported = state;
    unsupported.in_play_pokemon[0][0]
        .as_mut()
        .unwrap()
        .attached_tools
        .push(get_card_by_enum(CardId::A2148RockyHelmet));
    let (_, unsupported_evidence, _) = observed_decision(&unsupported, seed, true);
    assert_empty_evidence(&unsupported_evidence.unwrap());
}

struct TemporaryOutput(PathBuf);

impl TemporaryOutput {
    fn new(label: &str) -> Self {
        Self(std::env::temp_dir().join(format!(
            "pdl-public-reply-evidence-{label}-{}",
            Uuid::new_v4()
        )))
    }
}

impl Drop for TemporaryOutput {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn game_players() -> Vec<Box<dyn Player>> {
    let (deck_a, deck_b) = load_test_decks();
    create_players(
        deck_a,
        deck_b,
        vec![parse_player_code("k3").unwrap(), parse_player_code("k3").unwrap()],
    )
}

fn read_ply(output: &TemporaryOutput, game_id: Uuid, ply: u32) -> ExportedDataPoint {
    let path = output
        .0
        .join(game_id.to_string())
        .join(format!("ply_{ply:04}.json"));
    serde_json::from_str(&fs::read_to_string(path).unwrap()).unwrap()
}

#[test]
fn real_game_composite_and_data_exporter_bind_evidence_without_stale_singleton_reuse() {
    let output = TemporaryOutput::new("data-exporter");
    let game_id = Uuid::new_v4();
    let mut handlers = CompositeSimulationEventHandler::new(vec![Box::new(DataExporter::new(
        output.0.clone(),
    ))]);
    handlers.on_game_start(game_id);

    let (state, _) = saved_root();
    let first_state = state.clone();
    let (first_action, forced_action) = {
        let mut game = Game::new_with_event_handlers(game_id, game_players(), 211, &mut handlers);
        game.set_state(state.clone());
        let first = game.play_tick();

        let mut forced = state;
        forced.move_generation_stack = vec![(0, vec![SimpleAction::Noop])];
        game.set_state(forced);
        let second = game.play_tick();
        (first, second)
    };

    assert!(is_x_speed(&first_action));
    assert!(matches!(&forced_action.action, SimpleAction::Noop));

    let first = read_ply(&output, game_id, 0);
    assert_eq!(first.ply, 0);
    assert_eq!(first.actor, 0);
    assert_eq!(first.state, first_state);
    assert_eq!(first.chosen_action, first_action);
    assert!(first.playable_actions.contains(&first_action));
    let evidence = first
        .public_reply_evidence
        .expect("DataExporter requested evidence for the multi-action decision");
    assert_natural_witness(&evidence);
    assert!(evidence.records.iter().all(|record| {
        let root = record.root_action.as_ref().unwrap();
        first.playable_actions.contains(root)
            && record.selected == (root == &first.chosen_action)
    }));

    let forced = read_ply(&output, game_id, 1);
    assert_eq!(forced.ply, 1);
    assert_eq!(forced.chosen_action, forced_action);
    assert_eq!(forced.playable_actions, vec![forced_action]);
    assert!(forced.decision_randomness.is_none());
    assert!(
        forced.public_reply_evidence.is_none(),
        "a forced singleton must not inherit the prior decision's evidence"
    );
}

#[test]
fn results_only_handler_does_not_collect_or_leak_into_an_outer_scope() {
    let output = TemporaryOutput::new("results-only");
    let game_id = Uuid::new_v4();
    let (deck_a, deck_b) = load_test_decks();
    let matchup = ExportedMatchup::from_decks(
        &deck_a,
        &deck_b,
        vec!["K { max_depth: 3 }".into(), "K { max_depth: 3 }".into()],
    )
    .unwrap();
    let mut handlers = CompositeSimulationEventHandler::new(vec![Box::new(
        GameResultExporter::new(output.0.clone(), matchup),
    )]);
    assert!(!handlers.wants_public_reply_evidence());
    handlers.on_game_start(game_id);

    let (state, _) = saved_root();
    let (chosen, outer) = collect_public_reply_evidence(true, || {
        let mut game = Game::new_with_event_handlers(game_id, game_players(), 313, &mut handlers);
        game.set_state(state);
        game.play_tick()
    });
    assert!(is_x_speed(&chosen));
    assert_empty_evidence(&outer.unwrap());
}

#[test]
fn old_trace_defaults_to_none_while_an_empty_collected_scope_round_trips_as_some() {
    let fixture: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/public_reply_observed.json")).unwrap();
    let mut old_row = fixture["row"].clone();
    old_row
        .as_object_mut()
        .unwrap()
        .remove("public_reply_evidence");
    let old_point: ExportedDataPoint = serde_json::from_value(old_row.clone()).unwrap();
    assert!(old_point.public_reply_evidence.is_none());
    assert!(
        serde_json::to_value(old_point)
            .unwrap()
            .get("public_reply_evidence")
            .is_none(),
        "None remains omitted for old or non-collected traces"
    );

    let ((), collected) = collect_public_reply_evidence(true, || ());
    let collected = collected.unwrap();
    assert_empty_evidence(&collected);
    old_row["public_reply_evidence"] = serde_json::to_value(&collected).unwrap();
    let collected_point: ExportedDataPoint = serde_json::from_value(old_row).unwrap();
    assert_eq!(collected_point.public_reply_evidence, Some(collected));
}
