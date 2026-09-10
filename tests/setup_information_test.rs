use deckgym::{
    actions::{Action, SimpleAction}, card_ids::CardId, database::get_card_by_enum,
    models::PlayedCard, observation::PlayerObservation,
    players::{create_players, parse_player_code, EndTurnPlayer, ExpectiMiniMaxPlayer, Player},
    test_support::load_test_decks, Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};
use std::sync::{Arc, Mutex};

type Input = (PlayerObservation, Vec<Action>);
#[derive(Debug)]
struct Capture { deck: Deck, inputs: Arc<Mutex<Vec<Input>>> }
impl Player for Capture {
    fn get_deck(&self) -> Deck { self.deck.clone() }
    fn decision_fn(&mut self, _: &mut StdRng, view: &PlayerObservation, actions: &[Action]) -> Action {
        self.inputs.lock().unwrap().push((view.clone(), actions.to_vec()));
        actions.iter().find(|a| matches!(a.action, SimpleAction::EndTurn)).unwrap_or(&actions[0]).clone()
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, _: &[Action]) -> Action { unreachable!() }
}
fn fixture(actor: usize, alternate: bool) -> State {
    let (a,b) = load_test_decks();
    let mut s = State::new(&a,&b);
    s.current_player = actor;
    s.hands[actor] = vec![get_card_by_enum(CardId::A1001Bulbasaur), get_card_by_enum(CardId::A1033Charmander)];
    s.hands[1-actor] = vec![get_card_by_enum(CardId::PA001Potion)];
    let (active, bench) = if alternate { (CardId::A1033Charmander, CardId::A1001Bulbasaur) }
        else { (CardId::A1001Bulbasaur, CardId::A1033Charmander) };
    s.in_play_pokemon[1-actor][0] = Some(PlayedCard::from_id(active));
    s.in_play_pokemon[1-actor][1] = Some(PlayedCard::from_id(bench));
    s
}
fn capture(s: State) -> Input {
    let inputs = Arc::default();
    let players = (0..2).map(|p| Box::new(Capture { deck:s.decks[p].clone(), inputs:Arc::clone(&inputs) }) as Box<dyn Player>).collect();
    let mut game = Game::from_state(s,players,17);
    game.play_tick();
    let input = inputs.lock().unwrap()[0].clone();
    input
}
#[test]
fn both_seats_receive_identical_complete_input_for_hidden_active_and_bench_substitutions() {
    for actor in 0..2 {
        let base = capture(fixture(actor,false));
        assert_eq!(base,capture(fixture(actor,true)));
        assert!(base.0.visible_state().in_play_pokemon[1-actor].iter().all(Option::is_none));
        assert_eq!(serde_json::to_value(&base.0).unwrap()["template"]["setup_opponent_hidden"], true);
        let mut rng = StdRng::seed_from_u64(19);
        assert!(base.0.search_state(&mut rng).in_play_pokemon[1-actor].iter().all(Option::is_none));
    }
}
#[test]
fn reveal_waits_for_second_end_setup_and_referee_preserves_both_boards() {
    for first in 0..2 {
        let (a,b) = load_test_decks();
        let mut s = State::new(&a,&b);
        s.current_player = first;
        s.hands = [vec![get_card_by_enum(CardId::A1001Bulbasaur)], vec![get_card_by_enum(CardId::A1033Charmander)]];
        let mut game = Game::from_state(s,vec![Box::new(EndTurnPlayer{deck:a}),Box::new(EndTurnPlayer{deck:b})],23);
        for actor in [first,1-first] {
            let (_,actions) = game.get_state_clone().generate_possible_actions();
            game.apply_action(&actions[0]);
            assert!(game.observation(1-actor).visible_state().in_play_pokemon[actor].iter().all(Option::is_none));
            let s = game.get_state_clone();
            assert!(s.in_play_pokemon[actor][0].is_some());
            let (_,actions) = s.generate_possible_actions();
            let end = actions.iter().find(|a| matches!(a.action,SimpleAction::EndTurn)).unwrap();
            game.apply_action(end);
            assert_eq!(game.get_state_clone().turn_count, if actor == first {0} else {1});
        }
        for viewer in 0..2 {
            assert_eq!(game.observation(viewer).visible_state().in_play_pokemon, game.get_state_clone().in_play_pokemon);
        }
        assert!(game.get_state_clone().winner.is_none());
        assert_eq!(game.get_state_clone().current_player,first);
    }
}
#[test]
fn search_stops_before_setup_handoff_even_with_consistent_opponent_horizon() {
    for actor in 0..2 {
        for depth in [1,3] {
            let mut s = fixture(actor,false);
            s.in_play_pokemon[actor][0] = Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
            let view = PlayerObservation::from_state(&s,actor,&Default::default());
            let (_,actions) = s.generate_possible_actions();
            let seen = Arc::new(Mutex::new(Vec::new()));
            let record = Arc::clone(&seen);
            let mut bot = ExpectiMiniMaxPlayer { deck:s.decks[actor].clone(), max_depth:depth,
                write_debug_trees:false, opponent_ply:3, consistent_horizon:true, soft_opponent:false,
                value_function:Box::new(move |state,_| { record.lock().unwrap().push(state.clone()); 0.0 }) };
            let chosen = bot.decision_fn(&mut StdRng::seed_from_u64(29),&view,&actions);
            assert!(actions.contains(&chosen));
            let leaves = seen.lock().unwrap();
            assert!(!leaves.is_empty());
            for leaf in leaves.iter() {
                assert_eq!(leaf.turn_count,0,"search must stop before guessing setup completion");
                assert_eq!(leaf.current_player,actor,"opponent setup cannot be simulated as empty board");
                assert!(leaf.winner.is_none());
                assert!(leaf.in_play_pokemon[1-actor].iter().all(Option::is_none));
            }
        }
    }
}
#[test]
fn all_production_bot_families_finish_legal_setup_with_both_boards_revealed() {
    for code in ["aa","et","r","w","er","v","e3","p3","k3","d3","f3","g3","x3","y3","s3","m"] {
        let (a,b) = load_test_decks();
        let mut game = Game::new(create_players(a,b,vec![if code == "et" { deckgym::players::PlayerCode::ET } else { parse_player_code(code).unwrap() };2]),31);
        for _ in 0..12 {
            if game.get_state_clone().turn_count > 0 { break; }
            let (_,legal) = game.get_state_clone().generate_possible_actions();
            assert!(legal.contains(&game.play_tick()),"{code} chose an illegal setup action");
        }
        let s = game.get_state_clone();
        assert_eq!(s.turn_count,1,"{code} setup must terminate");
        assert!(s.winner.is_none());
        assert!(s.in_play_pokemon.iter().all(|b| b[0].is_some()));
        for viewer in 0..2 { assert_eq!(game.observation(viewer).visible_state().in_play_pokemon,s.in_play_pokemon); }
    }
}

#[test]
fn production_search_choices_ignore_hidden_starting_cards_for_both_seats() {
    for actor in 0..2 {
        for code in ["k3","y3","v"] {
            for own_active in [false,true] {
                let decide = |alternate| {
                    let mut s=fixture(actor,alternate);
                    if own_active { s.in_play_pokemon[actor][0]=Some(PlayedCard::from_id(CardId::A1001Bulbasaur)); }
                    let players=create_players(s.decks[0].clone(),s.decks[1].clone(),vec![parse_player_code(code).unwrap();2]);
                    Game::from_state(s,players,37).play_tick()
                };
                assert_eq!(decide(false),decide(true),"{code}, seat {actor}, own active {own_active}");
            }
        }
    }
}
