use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    players::Player,
    test_support::load_test_decks,
    Deck, Game, State,
};
use rand::{rngs::StdRng, RngCore};
use std::sync::{Arc, Mutex};

#[derive(Debug)]
struct ScriptedSearch {
    deck: Deck,
    work: usize,
    samples: Arc<Mutex<Vec<u64>>>,
}

impl Player for ScriptedSearch {
    fn get_deck(&self) -> Deck { self.deck.clone() }

    fn decide_omniscient(&mut self, rng: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        self.samples.lock().unwrap().push(rng.next_u64());
        for _ in 0..self.work { let _ = rng.next_u64(); }
        actions.iter().find(|a| matches!(&a.action,
            SimpleAction::Play { trainer_card } if trainer_card.name == "Red Card"))
            .or_else(|| actions.iter().find(|a| a.action == SimpleAction::EndTurn))
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

fn players(state: &State, work: usize, samples: Arc<Mutex<Vec<u64>>>) -> Vec<Box<dyn Player>> {
    (0..2).map(|p| Box::new(ScriptedSearch {
        deck: state.decks[p].clone(), work, samples: samples.clone(),
    }) as Box<dyn Player>).collect()
}

#[test]
fn search_budget_cannot_change_real_shuffle_with_same_action() {
    let state = fixture();
    for seed in 0..16 {
        let mut quiet = Game::from_state(state.clone(), players(&state, 0, Arc::default()), seed);
        let mut busy = Game::from_state(state.clone(), players(&state, 257, Arc::default()), seed);
        let action = quiet.play_tick();
        assert!(matches!(action.action, SimpleAction::Play { .. }));
        assert_eq!(action, busy.play_tick());
        assert_eq!(quiet.get_state_clone(), busy.get_state_clone(),
            "identical Red Card actions must produce identical real shuffles; seed {seed}");
    }
}

#[test]
fn previous_search_work_cannot_change_next_decision_stream() {
    let state = fixture();
    let quiet_samples = Arc::default();
    let busy_samples = Arc::default();
    let mut quiet = Game::from_state(state.clone(), players(&state, 0, Arc::clone(&quiet_samples)), 42);
    let mut busy = Game::from_state(state.clone(), players(&state, 257, Arc::clone(&busy_samples)), 42);
    quiet.play_tick(); busy.play_tick();
    // Restore the same decision position to isolate per-decision streams from real outcomes.
    quiet.set_state(state.clone()); busy.set_state(state);
    quiet.play_tick(); busy.play_tick();
    let a = quiet_samples.lock().unwrap();
    let b = busy_samples.lock().unwrap();
    assert_eq!(a.len(), 2);
    assert_eq!(*a, *b, "each decision needs a separately derived search seed");
    assert_ne!(a[0], a[1], "successive decisions must not reuse their search stream");
}

#[test]
fn game_constructors_share_search_stream_semantics() {
    let state = fixture();
    let new_samples = Arc::default();
    let state_samples = Arc::default();
    let mut fresh = Game::new(players(&state, 0, Arc::clone(&new_samples)), 73);
    fresh.set_state(state.clone());
    let mut restored = Game::from_state(state.clone(), players(&state, 0, Arc::clone(&state_samples)), 73);
    fresh.play_tick(); restored.play_tick();
    assert_eq!(*new_samples.lock().unwrap(), *state_samples.lock().unwrap(),
        "initial dealing must not advance the search seed stream");
}
