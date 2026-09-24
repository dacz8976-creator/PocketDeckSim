use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    observation::UnpricedBranch,
    players::{create_players, parse_player_code},
    simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler},
    test_support::load_test_decks,
    State, Game,
};
use std::sync::{Arc, Mutex};
use uuid::Uuid;

#[derive(Clone, Default)]
struct DecisionCapture {
    branches: Arc<Mutex<Vec<UnpricedBranch>>>,
    chosen: Arc<Mutex<Option<Action>>>,
}

impl SimulationEventHandler for DecisionCapture {
    fn merge(&mut self, _other: &dyn SimulationEventHandler) {}

    fn on_decision_information(
        &mut self,
        _game_id: Uuid,
        _model: &str,
        branches: &[UnpricedBranch],
    ) {
        *self.branches.lock().unwrap() = branches.to_vec();
    }

    fn on_action(
        &mut self,
        _game_id: Uuid,
        _state_before_action: &State,
        _actor: usize,
        _playable_actions: &[Action],
        action: &Action,
    ) {
        *self.chosen.lock().unwrap() = Some(action.clone());
    }
}

fn fixture_with_two_hidden_root_candidates() -> State {
    let (a, b) = load_test_decks();
    let mut state = State::new(&a, &b);
    state.turn_count = 3;
    state.set_board(
        vec![deckgym::models::PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![deckgym::models::PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![
        get_card_by_enum(CardId::PA006RedCard),
        get_card_by_enum(CardId::B1225Copycat),
    ];
    state.hands[1] = b.cards[..5].to_vec();
    state.decks[1].cards = b.cards[5..].to_vec();
    state
}

#[test]
fn two_root_candidates_at_same_cutoff_keep_root_and_selection_attribution() {
    let state = fixture_with_two_hidden_root_candidates();
    let branches = Arc::new(Mutex::new(Vec::new()));
    let chosen = Arc::new(Mutex::new(None));
    let capture = DecisionCapture { branches: branches.clone(), chosen: chosen.clone() };
    let (deck_a, deck_b) = load_test_decks();
    let players = create_players(
        deck_a,
        deck_b,
        vec![parse_player_code("k3").unwrap(), parse_player_code("k3").unwrap()],
    );
    let game_id = Uuid::new_v4();
    let mut handler = CompositeSimulationEventHandler::new(vec![Box::new(capture)]);
    let mut game = Game::new_with_event_handlers(game_id, players, 23, &mut handler);
    game.set_state(state);
    let selected = game.play_tick();

    let branches = branches.lock().unwrap();
    let serialized: Vec<serde_json::Value> = branches.iter().map(|branch| serde_json::to_value(branch).unwrap()).collect();
    let red_card = Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: get_card_by_enum(CardId::PA006RedCard).as_trainer() },
        is_stack: false,
    };
    let copycat = Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: get_card_by_enum(CardId::B1225Copycat).as_trainer() },
        is_stack: false,
    };
    let red_json = serde_json::to_value(&red_card).unwrap();
    let copycat_json = serde_json::to_value(&copycat).unwrap();
    assert!(serialized.iter().any(|branch| branch.get("root_action") == Some(&red_json)),
        "Red Card must retain root-candidate attribution");
    assert!(serialized.iter().any(|branch| branch.get("root_action") == Some(&copycat_json)),
        "Copycat must retain root-candidate attribution");
    assert!(serialized.iter().all(|branch| branch.get("occurrences").and_then(serde_json::Value::as_u64).unwrap_or(0) >= 1));
    assert!(serialized.iter().any(|branch| branch.get("selected").and_then(serde_json::Value::as_bool) == Some(true)
        && branch.get("root_action") == Some(&serde_json::to_value(&selected).unwrap())),
        "the selected root action must be linked to its unpriced branches");
    assert_eq!(*chosen.lock().unwrap(), Some(selected));
}

