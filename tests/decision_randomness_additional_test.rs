use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    data_exporter::{DataExporter, ExportedDataPoint},
    database::get_card_by_enum,
    models::PlayedCard,
    players::{expectiminimax_player::ExpectiMiniMaxPlayer, Player},
    simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler},
    test_support::load_test_decks,
    Deck, Game, State,
};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::{fs, path::PathBuf, sync::{Arc, Mutex}};
use uuid::Uuid;

#[derive(Debug)]
struct ScriptedSearch {
    deck: Deck,
    samples: Arc<Mutex<Vec<u64>>>,
}

impl Player for ScriptedSearch {
    fn get_deck(&self) -> Deck { self.deck.clone() }

    fn decide_omniscient(&mut self, rng: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        self.samples.lock().unwrap().push(rng.next_u64());
        actions.iter().find(|a| a.action == SimpleAction::EndTurn)
            .unwrap_or(&actions[0]).clone()
    }
}

fn fixture() -> State {
    let (a, b) = load_test_decks();
    let mut state = State::new(&a, &b);
    state.set_board(vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
                    vec![PlayedCard::from_id(CardId::A1033Charmander)]);
    state.turn_count = 3;
    state.hands[0] = vec![get_card_by_enum(CardId::PA006RedCard)];
    state.hands[1] = b.cards[..5].to_vec();
    state.decks[1].cards = b.cards[5..].to_vec();
    state
}

fn players_with_samples(
    state: &State,
    samples: [Arc<Mutex<Vec<u64>>>; 2],
) -> Vec<Box<dyn Player>> {
    (0..2).map(|p| Box::new(ScriptedSearch {
        deck: state.decks[p].clone(), samples: samples[p].clone(),
    }) as Box<dyn Player>).collect()
}

#[test]
fn each_player_keeps_an_independent_decision_stream() {
    let state = fixture();
    let control_samples = [Arc::default(), Arc::default()];
    let reordered_samples = [Arc::default(), Arc::default()];

    let mut control = Game::from_state(
        state.clone(), players_with_samples(&state, control_samples.clone()), 42,
    );
    control.play_tick();

    let mut reordered = Game::from_state(
        state.clone(), players_with_samples(&state, reordered_samples.clone()), 42,
    );
    let mut player_one_first = state.clone();
    player_one_first.current_player = 1;
    reordered.set_state(player_one_first);
    reordered.play_tick();
    reordered.set_state(state);
    reordered.play_tick();

    assert_eq!(
        *control_samples[0].lock().unwrap(), *reordered_samples[0].lock().unwrap(),
        "player 1's decision must not advance player 0's search stream",
    );
    assert_ne!(
        control_samples[0].lock().unwrap()[0], reordered_samples[1].lock().unwrap()[0],
        "players should receive distinct search streams for the same game seed",
    );
}

#[test]
fn forced_ticks_do_not_create_or_reuse_decision_randomness() {
    let (a, b) = load_test_decks();
    let mut setup = State::new(&a, &b);
    setup.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    let samples = [Arc::default(), Arc::default()];
    let mut game = Game::from_state(setup.clone(), players_with_samples(&setup, samples.clone()), 91);
    let mut expected_rng = StdRng::seed_from_u64(game.randomness().decision(0, 0).search_seed);
    let expected = expected_rng.next_u64();

    // With exactly one legal setup action, this tick is forced and must not consume a search seed.
    game.play_tick();
    game.set_state(fixture());
    game.play_tick();

    assert_eq!(samples[0].lock().unwrap().len(), 1);
    assert_eq!(samples[0].lock().unwrap()[0], expected);
}

#[test]
fn expectiminimax_selection_is_applied_with_the_real_action_rng() {
    let state = fixture();
    let seed = 173;
    let game_probe = Game::from_state(state.clone(), vec![
        Box::new(ScriptedSearch { deck: state.decks[0].clone(), samples: Arc::default() }),
        Box::new(ScriptedSearch { deck: state.decks[1].clone(), samples: Arc::default() }),
    ], seed);
    let search_seed = game_probe.randomness().decision(0, 0).search_seed;
    let (_, mut actions) = state.generate_possible_actions();
    deckgym::observation::canonical_actions(&mut actions);
    assert!(actions.len() > 1, "fixture must exercise a real search decision");

    let mut search_player = ExpectiMiniMaxPlayer {
        deck: state.decks[0].clone(),
        max_depth: 2,
        write_debug_trees: false,
        value_function: Box::new(|state: &State, myself| state.points[myself] as f64),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    };
    let expected_action = search_player.decision_fn(
        &mut StdRng::seed_from_u64(search_seed), &game_probe.observation(0), &actions,
    );

    let actual_players: Vec<Box<dyn Player>> = vec![
        Box::new(ExpectiMiniMaxPlayer {
            deck: state.decks[0].clone(), max_depth: 2, write_debug_trees: false,
            value_function: Box::new(|state: &State, myself| state.points[myself] as f64),
            opponent_ply: 0, consistent_horizon: false, soft_opponent: false,
        }),
        Box::new(ScriptedSearch { deck: state.decks[1].clone(), samples: Arc::default() }),
    ];
    let mut game = Game::from_state(state.clone(), actual_players, seed);
    let chosen_action = game.play_tick();
    assert_eq!(chosen_action, expected_action, "the game's player must return the search selection");

    let manual_players = vec![
        Box::new(ScriptedSearch { deck: state.decks[0].clone(), samples: Arc::default() }) as Box<dyn Player>,
        Box::new(ScriptedSearch { deck: state.decks[1].clone(), samples: Arc::default() }),
    ];
    let mut manually_applied = Game::from_state(state.clone(), manual_players, seed);
    manually_applied.apply_action(&chosen_action);
    assert_eq!(game.get_state_clone(), manually_applied.get_state_clone(),
        "search evaluation must not replace the selected action's real state transition");
}

#[test]
fn exporter_records_game_metadata_on_every_ply_and_none_for_forced_ticks() {
    let output = std::env::temp_dir().join(format!("pdl-randomness-{}", Uuid::new_v4()));
    let game_id = Uuid::new_v4();
    let mut handlers = CompositeSimulationEventHandler::new(vec![
        Box::new(DataExporter::new(output.clone())),
    ]);
    handlers.on_game_start(game_id);

    let (a, b) = load_test_decks();
    let mut setup = State::new(&a, &b);
    setup.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    let players = players_with_samples(&setup, [Arc::default(), Arc::default()]);
    {
        let mut game = Game::new_with_event_handlers(game_id, players, 211, &mut handlers);
        game.set_state(setup.clone());
        game.play_tick(); // forced setup placement: decision_randomness = None
        game.set_state(fixture());
        game.play_tick(); // player decision: decision_randomness = Some(...)
        game.set_state(setup);
        game.play_tick(); // another forced tick must not inherit the prior decision
    }

    let folder = output.join(game_id.to_string());
    let points: Vec<ExportedDataPoint> = (0..3).map(|ply| {
        let path: PathBuf = folder.join(format!("ply_{ply:04}.json"));
        serde_json::from_str(&fs::read_to_string(path).unwrap()).unwrap()
    }).collect();
    assert!(points.iter().all(|point| point.game_id == game_id.to_string()));
    assert!(points.iter().all(|point| point.randomness.as_ref().is_some_and(|r| r.game_seed == 211)));
    assert_eq!(points[0].decision_randomness, None);
    assert_eq!(points[1].decision_randomness.as_ref().map(|d| (d.actor, d.decision_index)), Some((0, 0)));
    assert_eq!(points[2].decision_randomness, None);

    fs::remove_dir_all(output).unwrap();
}
