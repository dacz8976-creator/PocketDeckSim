use deckgym::{
    actions::{Action, SimpleAction}, card_ids::CardId, database::get_card_by_enum,
    models::{EnergyType, PlayedCard}, players::{create_players, parse_player_code, Player},
    test_support::load_test_decks, Deck, Game, State,
};
use rand::rngs::StdRng;
use std::sync::{Arc, Mutex};

fn fixture() -> State {
    let (a, b) = load_test_decks();
    let mut s = State::new(&a, &b);
    s.set_board(vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
        .with_energy(vec![EnergyType::Grass, EnergyType::Grass]),
        PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)]);
    s.turn_count = 3;
    s.hands[0] = vec![get_card_by_enum(CardId::PA007ProfessorsResearch),
        get_card_by_enum(CardId::PA001Potion)];
    s.decks[0].cards = vec![get_card_by_enum(CardId::A1002Ivysaur),
        get_card_by_enum(CardId::A1003Venusaur), get_card_by_enum(CardId::PA002XSpeed),
        get_card_by_enum(CardId::PA006RedCard)];
    s.hands[1] = b.cards[..5].to_vec();
    s.decks[1].cards = b.cards[5..].to_vec();
    s
}

#[derive(Debug)]
struct Capture { deck: Deck, states: Arc<Mutex<Vec<State>>> }
impl Player for Capture {
    fn get_deck(&self) -> Deck { self.deck.clone() }
    fn decide_omniscient(&mut self, _: &mut StdRng, state: &State, actions: &[Action]) -> Action {
        self.states.lock().unwrap().push(state.clone());
        actions.iter().find(|a| a.action == SimpleAction::EndTurn).unwrap_or(&actions[0]).clone()
    }
}

fn capture(state: State) -> State {
    let states = Arc::default();
    let players = (0..2).map(|p| Box::new(Capture {
        deck: state.decks[p].clone(), states: Arc::clone(&states),
    }) as Box<dyn Player>).collect();
    let mut game = Game::from_state(state, players, 42);
    game.play_tick();
    let result = states.lock().unwrap()[0].clone();
    result
}

#[test]
fn unknown_own_deck_order_cannot_reach_policy() {
    let s = fixture();
    let base = capture(s.clone());
    for shift in 1..4 {
        let mut changed = s.clone(); changed.decks[0].cards.rotate_left(shift);
        assert_eq!(base, capture(changed), "policy input must not identify unseen deck order");
    }
}

#[test]
fn unknown_opponent_cards_cannot_reach_policy() {
    let s = fixture();
    let base = capture(s.clone());
    let mut changed = s.clone();
    changed.hands[1].fill(get_card_by_enum(CardId::A1003Venusaur));
    changed.decks[1].cards.fill(get_card_by_enum(CardId::PA001Potion));
    assert_eq!(base, capture(changed), "normal-play policies cannot see opponent deck lists or hands");
}

#[test]
fn complete_k3_decision_is_invariant_under_hidden_substitution() {
    let s = fixture();
    let decide = |s: State| {
        let players = create_players(s.decks[0].clone(), s.decks[1].clone(),
            vec![parse_player_code("k3").unwrap(), parse_player_code("k3").unwrap()]);
        let mut game = Game::from_state(s, players, 42);
        game.play_tick()
    };
    let baseline = decide(s.clone());
    for shift in 0..4 {
        let mut changed = s.clone();
        changed.decks[0].cards.rotate_left(shift);
        changed.hands[1].fill(get_card_by_enum(CardId::A1003Venusaur));
        changed.decks[1].cards.reverse();
        assert_eq!(baseline, decide(changed));
    }
}

#[test]
fn public_draw_preserves_the_remainder_of_a_revealed_prefix() {
    let mut s = fixture();
    let pokedex = get_card_by_enum(CardId::PA004PokedEx);
    s.hands[0].push(pokedex.clone());
    let mut game = Game::from_state(s.clone(), create_players(s.decks[0].clone(), s.decks[1].clone(),
        vec![parse_player_code("k3").unwrap(), parse_player_code("k3").unwrap()]), 91);
    game.apply_action(&Action { actor: 0, action: SimpleAction::Play { trainer_card: pokedex.as_trainer() }, is_stack: false });
    assert_eq!(game.observation(0).revealed.deck_top[0], s.decks[0].cards[..3]);
    game.apply_action(&Action { actor: 0, action: SimpleAction::DrawCard { amount: 1 }, is_stack: false });
    assert_eq!(game.observation(0).revealed.deck_top[0], s.decks[0].cards[1..3]);
}

#[test]
fn revealed_hand_choices_remain_known_after_the_selected_card_leaves() {
    let mut s = fixture();
    let cards = vec![get_card_by_enum(CardId::PA007ProfessorsResearch), get_card_by_enum(CardId::PA001Potion)];
    s.hands[1] = cards.clone();
    s.move_generation_stack = vec![(0, cards.iter().map(|card|
        SimpleAction::ShuffleOpponentHandCard { card: card.clone() }).collect())];
    let mut game = Game::from_state(s.clone(), create_players(s.decks[0].clone(), s.decks[1].clone(),
        vec![parse_player_code("k3").unwrap(), parse_player_code("k3").unwrap()]), 91);
    game.apply_action(&Action { actor: 0, action: SimpleAction::ShuffleOpponentHandCard { card: cards[0].clone() }, is_stack: true });
    assert_eq!(game.observation(0).revealed.opponent_hand, vec![cards[1].clone()]);
    assert_eq!(game.observation(0).visible_state().hands[1], vec![cards[1].clone()]);
}

#[test]
fn unknown_dependent_search_branches_are_exported_as_unpriced() {
    use deckgym::observation::{UnpricedBranch, INFORMATION_MODEL};
    use deckgym::simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler};
    use uuid::Uuid;
    struct CaptureInformation(Arc<Mutex<Vec<UnpricedBranch>>>);
    impl SimulationEventHandler for CaptureInformation {
        fn merge(&mut self, _: &dyn SimulationEventHandler) {}
        fn on_decision_information(&mut self, _: Uuid, model: &str, unpriced: &[UnpricedBranch]) {
            assert_eq!(model, INFORMATION_MODEL);
            *self.0.lock().unwrap() = unpriced.to_vec();
        }
    }
    let mut s = fixture();
    s.hands[0] = vec![get_card_by_enum(CardId::PA006RedCard)];
    let branches = Arc::default();
    let mut handler = CompositeSimulationEventHandler::new(vec![Box::new(CaptureInformation(Arc::clone(&branches)))]);
    let (deck_a, deck_b) = load_test_decks();
    let players = create_players(deck_a, deck_b,
        vec![parse_player_code("k3").unwrap(), parse_player_code("k3").unwrap()]);
    let mut game = Game::new_with_event_handlers(Uuid::new_v4(), players, 47, &mut handler);
    game.set_state(s);
    game.play_tick();
    let branches = branches.lock().unwrap();
    assert!(branches.iter().any(|b| matches!(&b.action.action,
        SimpleAction::Play { trainer_card } if trainer_card.name == "Red Card")
        && b.reason.contains("unrevealed opponent")), "Red Card continuation must not be presented as a fully priced forecast");
}
