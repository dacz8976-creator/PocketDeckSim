use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    data_exporter::{DataExporter, ExportedDataPoint},
    database::get_card_by_enum,
    game::LuxuryCoinResolutionRecord,
    models::{Card, EnergyType, PlayedCard},
    observation::{PlayerObservation, RevealedKnowledge},
    players::Player,
    simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler},
    state::LuxuryCoinDecision,
    test_support::load_test_decks,
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};
use std::{fs, path::PathBuf};
use uuid::Uuid;

#[derive(Debug)]
struct CoinScript {
    deck: Deck,
    reroll: bool,
}
impl Player for CoinScript {
    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        actions
            .iter()
            .find(|action| match &action.action {
                SimpleAction::Play { trainer_card } => {
                    matches!(trainer_card.id.as_str(), "B1 215" | "A3b 069")
                }
                SimpleAction::KeepTrainerCoinResults => !self.reroll,
                SimpleAction::RerollTrainerCoins { .. } => self.reroll,
                _ => false,
            })
            .or_else(|| {
                actions
                    .iter()
                    .find(|action| action.action == SimpleAction::EndTurn)
            })
            .expect("script requires its Trainer, coin decision or EndTurn")
            .clone()
    }
}

fn fixture() -> State {
    let (a, b) = load_test_decks();
    let mut state = State::new(&a, &b);
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B4a051Gholdengo),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.turn_count = 3;
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::B1215HittingHammer)];
    state.hands[1].clear();
    state.in_play_pokemon[1][0]
        .as_mut()
        .unwrap()
        .attached_energy = vec![EnergyType::Fire, EnergyType::Fire];
    state
}

fn players(reroll: bool) -> Vec<Box<dyn Player>> {
    let (a, b) = load_test_decks();
    vec![
        Box::new(CoinScript { deck: a, reroll }),
        Box::new(CoinScript { deck: b, reroll }),
    ]
}

struct Output(PathBuf);
impl Output {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!("pdl-luxury-export-{}", Uuid::new_v4()));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
}
impl Drop for Output {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn read_point(output: &Output, game_id: Uuid, ply: u32) -> ExportedDataPoint {
    let path = output
        .0
        .join(game_id.to_string())
        .join(format!("ply_{ply:04}.json"));
    assert!(
        path.is_file(),
        "resolved ply must be written before the next tick or GameEnd"
    );
    serde_json::from_slice(&fs::read(path).unwrap()).unwrap()
}

fn export_run(seed: u64, reroll: bool) -> LuxuryCoinResolutionRecord {
    let output = Output::new();
    let game_id = Uuid::new_v4();
    let mut handlers =
        CompositeSimulationEventHandler::new(vec![Box::new(DataExporter::new(output.0.clone()))]);
    handlers.on_game_start(game_id);
    let mut game = Game::new_with_event_handlers(game_id, players(reroll), seed, &mut handlers);
    game.set_state(fixture());

    let initial_action = game.play_tick();
    assert!(matches!(initial_action.action, SimpleAction::Play { .. }));
    let pending_state = game.get_state_clone();
    let pending = pending_state.pending_trainer_coin_choice.as_ref().unwrap();
    assert_eq!(pending.flips.len(), 2);
    let initial_faces = pending.flips.clone();
    assert!(read_point(&output, game_id, 0)
        .luxury_coin_resolutions
        .is_empty());
    assert!(game.luxury_coin_resolution_history().is_empty());

    let choice = game.play_tick();
    assert!(matches!(
        (&choice.action, reroll),
        (SimpleAction::KeepTrainerCoinResults, false)
            | (SimpleAction::RerollTrainerCoins { .. }, true)
    ));
    let resolved = game.get_state_clone();
    assert!(resolved.pending_trainer_coin_choice.is_none());
    let point = read_point(&output, game_id, 1);
    assert_eq!(point.game_id, game_id.to_string());
    assert_eq!(point.actor, 0);
    assert_eq!(point.chosen_action, choice);
    assert_eq!(
        point
            .state
            .pending_trainer_coin_choice
            .as_ref()
            .unwrap()
            .flips,
        initial_faces
    );
    assert_eq!(point.luxury_coin_resolutions.len(), 1);
    assert_eq!(
        point.luxury_coin_resolutions,
        game.luxury_coin_resolution_history()
    );
    let record = point.luxury_coin_resolutions[0].clone();
    assert_eq!(record.actor, 0);
    assert_eq!(record.initial_faces, initial_faces);
    assert_eq!(
        record.decision,
        if reroll {
            LuxuryCoinDecision::Reroll
        } else {
            LuxuryCoinDecision::Keep
        }
    );
    let committed_faces = if reroll {
        let faces = record
            .replacement_faces
            .as_ref()
            .expect("a reroll must retain the replacement batch");
        assert_eq!(faces.len(), 2);
        faces
    } else {
        assert!(record.replacement_faces.is_none());
        &record.initial_faces
    };
    let removed = usize::from(committed_faces.iter().all(|face| *face));
    assert_eq!(
        resolved.get_active(1).attached_energy.len(),
        2 - removed,
        "the exported committed faces must explain the real Hitting Hammer result"
    );
    assert_eq!(resolved.discard_energies[1].len(), removed);
    let encoded = serde_json::to_value(&record).unwrap();
    let keys = encoded.as_object().unwrap();
    assert_eq!(
        keys.len(),
        4,
        "public coin evidence must contain only actor, decision and two batches"
    );
    assert!(!keys.contains_key("route"));
    assert!(!keys.contains_key("copied"));

    // A legacy ply omitting the new vector remains readable without fabricating a coin event.
    let mut legacy = serde_json::to_value(&point).unwrap();
    legacy
        .as_object_mut()
        .unwrap()
        .remove("luxury_coin_resolutions");
    let legacy: ExportedDataPoint = serde_json::from_value(legacy).unwrap();
    assert!(legacy.luxury_coin_resolutions.is_empty());

    assert_eq!(game.play_tick().action, SimpleAction::EndTurn);
    assert!(read_point(&output, game_id, 2)
        .luxury_coin_resolutions
        .is_empty());
    assert_eq!(
        game.luxury_coin_resolution_history(),
        &[record.clone()],
        "a later ply must not replay the event"
    );
    game.set_state(resolved);
    assert!(game.luxury_coin_resolution_history().is_empty());
    game.play_tick();
    assert!(read_point(&output, game_id, 3)
        .luxury_coin_resolutions
        .is_empty());
    assert!(game.luxury_coin_resolution_history().is_empty());
    record
}

#[test]
fn keep_exports_the_observed_batch_on_its_own_resolved_ply() {
    export_run(17, false);
}

#[test]
fn reroll_exports_replacement_faces_and_never_repeats_them_on_later_plies() {
    let mut saw_changed_batch = false;
    let mut saw_changed_effect_class = false;
    let mut saw_removal = false;
    let mut saw_no_removal = false;
    for seed in 0..16 {
        let record = export_run(seed, true);
        let replacement = record.replacement_faces.unwrap();
        saw_changed_batch |= replacement != record.initial_faces;
        saw_changed_effect_class |=
            replacement.iter().all(|face| *face) != record.initial_faces.iter().all(|face| *face);
        saw_removal |= replacement.iter().all(|face| *face);
        saw_no_removal |= replacement.iter().any(|face| !*face);
    }
    assert!(
        saw_changed_batch,
        "fixture must reject an exporter that copies the initial batch as the reroll"
    );
    assert!(
        saw_changed_effect_class,
        "at least one reroll must change the actual Hammer effect, not just face order"
    );
    assert!(
        saw_removal && saw_no_removal,
        "recorded faces must explain both real effect outcomes"
    );
}

#[test]
fn raw_coin_events_are_not_serialized_observed_or_replayed_when_a_game_adopts_state() {
    // Apply a concrete branch through the public forecast seam. Unlike Game::apply_action,
    // this deliberately leaves the transient event queued so adoption can be tested.
    fn raw_branch(rng: &mut StdRng, state: &mut State, action: &Action) {
        let (_, mut mutations) = try_forecast_action(state, action).unwrap().into_branches();
        mutations.remove(0)(rng, state, action);
    }
    let mut state = fixture();
    let Card::Trainer(hammer) = get_card_by_enum(CardId::B1215HittingHammer) else {
        panic!()
    };
    let mut rng = StdRng::seed_from_u64(71);
    raw_branch(
        &mut rng,
        &mut state,
        &Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: hammer,
            },
            is_stack: false,
        },
    );
    assert!(state.pending_trainer_coin_choice.is_some());
    raw_branch(
        &mut rng,
        &mut state,
        &Action {
            actor: 0,
            action: SimpleAction::KeepTrainerCoinResults,
            is_stack: true,
        },
    );
    assert!(state.pending_trainer_coin_choice.is_none());
    let serialized = serde_json::to_value(&state).unwrap();
    assert!(!serialized
        .as_object()
        .unwrap()
        .contains_key("luxury_coin_resolution_events"));
    for actor in 0..2 {
        let observation =
            PlayerObservation::from_state(&state, actor, &RevealedKnowledge::default());
        let value = serde_json::to_value(observation).unwrap();
        assert!(!value["template"]
            .as_object()
            .unwrap()
            .contains_key("luxury_coin_resolution_events"));
    }
    let noop = Action {
        actor: 0,
        action: SimpleAction::Noop,
        is_stack: false,
    };
    let mut adopted = Game::from_state(state.clone(), players(false), 71);
    adopted.apply_action(&noop);
    assert!(adopted.luxury_coin_resolution_history().is_empty());
    adopted.set_state(state);
    adopted.apply_action(&noop);
    assert!(adopted.luxury_coin_resolution_history().is_empty());
}

#[test]
fn penny_copied_source_is_private_while_actual_coin_record_stays_public() {
    for reroll in [false, true] {
        let output = Output::new();
        let game_id = Uuid::new_v4();
        let mut handlers = CompositeSimulationEventHandler::new(vec![Box::new(DataExporter::new(
            output.0.clone(),
        ))]);
        handlers.on_game_start(game_id);
        let mut game = Game::new_with_event_handlers(game_id, players(reroll), 29, &mut handlers);
        let mut state = fixture();
        state.hands[0] = vec![get_card_by_enum(CardId::A3b069Penny)];
        // A single physical source makes the copy deterministic without exposing it
        // in the opponent observation or the public resolution event.
        state.decks[1].cards = vec![get_card_by_enum(CardId::B4a070TeamRocketsMasterPlan)];
        game.set_state(state);
        let action = game.play_tick();
        assert!(
            matches!(action.action, SimpleAction::Play { ref trainer_card }
            if trainer_card.id == "A3b 069")
        );
        let actor = game.observation(0);
        let opponent = game.observation(1);
        let actor_pending = actor
            .visible_state()
            .pending_trainer_coin_choice
            .as_ref()
            .unwrap();
        let opponent_pending = opponent
            .visible_state()
            .pending_trainer_coin_choice
            .as_ref()
            .unwrap();
        assert!(matches!(actor_pending.route.as_ref(),
            Some(deckgym::state::TrainerCoinEffectRoute::Penny { copied, .. })
            if copied.id == "B4a 070"));
        assert!(opponent_pending.route.is_none());
        assert_eq!(actor_pending.flips, opponent_pending.flips);
        assert!(opponent
            .visible_state()
            .move_generation_stack
            .last()
            .unwrap()
            .1
            .is_empty());
        // The opponent legitimately knows their own deck composition; only the
        // selected pending route and its copied identity must be redacted.
        let pending_json = serde_json::to_value(opponent_pending).unwrap();
        assert!(pending_json["route"].is_null());
        assert!(!pending_json.to_string().contains("B4a 070"));

        let chosen = game.play_tick();
        let point = read_point(&output, game_id, 1);
        assert_eq!(point.chosen_action, chosen);
        assert_eq!(point.luxury_coin_resolutions.len(), 1);
        assert_eq!(
            point.luxury_coin_resolutions,
            game.luxury_coin_resolution_history()
        );
        let event = &point.luxury_coin_resolutions[0];
        assert_eq!(event.actor, 0);
        assert_eq!(event.initial_faces, actor_pending.flips);
        assert_eq!(
            event.decision,
            if reroll {
                LuxuryCoinDecision::Reroll
            } else {
                LuxuryCoinDecision::Keep
            }
        );
        assert_eq!(event.replacement_faces.is_some(), reroll);
        let public_json = serde_json::to_value(&point.luxury_coin_resolutions).unwrap();
        let fields = public_json[0].as_object().unwrap();
        assert_eq!(fields.len(), 4);
        assert!(
            fields.contains_key("actor")
                && fields.contains_key("decision")
                && fields.contains_key("initial_faces")
                && fields.contains_key("replacement_faces")
        );
        assert!(!public_json.to_string().contains("B4a 070"));
    }
}
