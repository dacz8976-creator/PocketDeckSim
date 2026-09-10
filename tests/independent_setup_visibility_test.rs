use deckgym::{
    actions::{Action, SimpleAction}, card_ids::CardId, database::get_card_by_enum,
    models::PlayedCard, observation::PlayerObservation, players::{EndTurnPlayer, Player},
    test_support::load_test_decks, Deck, Game, State,
};
use rand::rngs::StdRng;
use std::sync::{Arc, Mutex};

#[derive(Debug)]
struct CaptureSetup { deck: Deck, views: Arc<Mutex<Vec<PlayerObservation>>> }
impl Player for CaptureSetup {
    fn get_deck(&self) -> Deck { self.deck.clone() }
    fn decision_fn(&mut self, _: &mut StdRng, view: &PlayerObservation, actions: &[Action]) -> Action {
        self.views.lock().unwrap().push(view.clone());
        actions[0].clone()
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, _: &[Action]) -> Action {
        panic!("production decision must use observation")
    }
}

fn second_setup_observation(opponent_active: CardId) -> PlayerObservation {
    let (a,b) = load_test_decks();
    let mut state = State::new(&a,&b);
    state.turn_count = 0;
    state.current_player = 0;
    state.set_board(vec![PlayedCard::from_id(opponent_active)], vec![]);
    state.hands[1] = vec![get_card_by_enum(CardId::A1001Bulbasaur), get_card_by_enum(CardId::A1033Charmander)];
    let views = Arc::new(Mutex::new(Vec::new()));
    let mut game = Game::from_state(state, vec![
        Box::new(EndTurnPlayer{deck:a}),
        Box::new(CaptureSetup{deck:b, views:Arc::clone(&views)})
    ], 312);
    game.apply_action(&Action{actor:0, action:SimpleAction::EndTurn, is_stack:false});
    assert_eq!(game.get_state_clone().turn_count,0);
    assert_eq!(game.get_state_clone().current_player,1);
    let choice = game.play_tick();
    assert!(matches!(choice.action,SimpleAction::Place(_,0)));
    let result = views.lock().unwrap().pop().expect("second player setup decision");
    result
}

#[test]
fn opponent_starting_pokemon_identity_is_hidden_until_both_players_finish_setup() {
    let a = second_setup_observation(CardId::A1001Bulbasaur);
    let b = second_setup_observation(CardId::A1033Charmander);
    eprintln!("view A opponent active: {:?}",a.visible_state().in_play_pokemon[0][0].as_ref().map(|p|p.card.get_id()));
    eprintln!("view B opponent active: {:?}",b.visible_state().in_play_pokemon[0][0].as_ref().map(|p|p.card.get_id()));
    assert!(a==b,"changing a still-hidden opponent starting Pokemon must not change the setup observation");
}
