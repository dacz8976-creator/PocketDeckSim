//! ky3 item 7's logger (engine/src/kg_log.rs), written before it: the own-knockout count read through serde JSON and indexed by seat,
//! knockout events (cause, points gained, the Glimmora coin), and a logged game's record (both boards, both hands, the full legal list,
//! the move, the switch note a play-out pilot leaves).
use deckgym::actions::SimpleAction;
use deckgym::card_ids::CardId;
use deckgym::kg_log::{ko_events, own_knockouts, play_logged};
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{take_switch_note, PlayoutParams, PlayoutPlayer};
use deckgym::players::{create_players, parse_player_code, Player};
use deckgym::test_support::{get_initialized_game, get_test_game_with_board, load_test_decks};
use deckgym::Game;
use rand::{rngs::StdRng, SeedableRng};

#[test]
fn own_knockouts_is_read_through_json_and_indexed_by_seat() {
    let mut state = get_test_game_with_board(vec![PlayedCard::from_id(CardId::B3a043Kingambit)], vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]).get_state_clone();
    assert_eq!(own_knockouts(&state), [0, 0]);
    state.set_own_knockouts_this_game(1, 3);
    assert_eq!(own_knockouts(&state), [0, 3]);
    state.set_own_knockouts_this_game(0, 2);
    assert_eq!(own_knockouts(&state), [2, 3]);
}

/// Seat 1 loses its Active; `after` is `before` with the slot empty, the count up by one and the points as given.
fn fall(victim: CardId, gained: u8) -> Vec<serde_json::Value> {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a043Kingambit).with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
        vec![PlayedCard::from_id(victim).with_remaining_hp(10), PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let before = game.get_state_clone();
    let mut after = before.clone();
    after.in_play_pokemon[1][0] = None;
    after.points[0] += gained;
    after.set_own_knockouts_this_game(1, 1);
    ko_events(&before, &after, 0, "Attack:Venomous Hit")
}

#[test]
fn a_denied_glimmora_knockout_is_logged_with_the_coin_and_its_cause() {
    let ev = fall(CardId::B3a045Glimmora, 0);
    assert_eq!(ev.len(), 1);
    let e = &ev[0];
    assert_eq!(e["victim_seat"], 1);
    assert_eq!(e["victim"], "Glimmora");
    assert_eq!(e["coin_ability"], true);
    assert_eq!(e["ko_points"], 1);
    assert_eq!(e["points_gained"], 0);
    assert_eq!(e["denied"], true);
    assert_eq!(e["cause"], "Attack:Venomous Hit");
    assert_eq!(e["count_after"], 1);
}

#[test]
fn a_paid_glimmora_knockout_and_a_plain_one_are_not_denials() {
    let paid = fall(CardId::B3a045Glimmora, 1);
    assert_eq!((paid[0]["coin_ability"].clone(), paid[0]["denied"].clone()), (true.into(), false.into()));
    let plain = fall(CardId::A3110AlolanGrimer, 1);
    assert_eq!((plain[0]["coin_ability"].clone(), plain[0]["denied"].clone()), (false.into(), false.into()));
}

#[test]
fn a_turn_with_no_knockout_logs_no_event() {
    let game = get_test_game_with_board(vec![PlayedCard::from_id(CardId::B3a043Kingambit)], vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    let s = game.get_state_clone();
    assert!(ko_events(&s, &s, 0, "EndTurn").is_empty());
}

#[test]
fn a_logged_game_records_boards_hands_the_legal_list_and_the_move() {
    let (deck_a, deck_b) = load_test_decks();
    let players = create_players(deck_a, deck_b, vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()]);
    let mut game = Game::new(players, 4242);
    let rec = play_logged(&mut game, 1);
    assert_eq!(rec["deck_seat"], 1);
    assert!(rec["turns"].as_u64().unwrap() > 2);
    assert!(matches!(rec["winner"].as_i64(), Some(0) | Some(1) | Some(-1)));
    let decisions = rec["decisions"].as_array().unwrap();
    assert!(!decisions.is_empty());
    for d in decisions {
        let legal: Vec<&str> = d["legal"].as_array().unwrap().iter().map(|x| x.as_str().unwrap()).collect();
        assert!(!legal.is_empty());
        assert!(legal.contains(&d["chosen"].as_str().unwrap()), "{d}");
        for seat in 0..2 {
            assert!(d["boards"][seat].is_array() && d["boards"][seat].as_array().unwrap().len() == 4);
            assert!(d["hands"][seat].is_array());
        }
        assert_eq!(d["own_kos"].as_array().unwrap().len(), 2);
    }
    // the last count seen is the engine's own
    let last = game.get_state_clone();
    assert_eq!(rec["own_kos_final"], serde_json::json!(own_knockouts(&last)));
}

#[test]
fn a_playout_pilot_leaves_a_switch_note_with_km3s_move() {
    let game = get_initialized_game(3);
    let state = game.get_state_clone();
    let (actor, actions) = state.generate_possible_actions();
    let (deck_a, deck_b) = load_test_decks();
    let (deck, opp) = if actor == 0 { (deck_a, deck_b) } else { (deck_b, deck_a) };
    let params = PlayoutParams { rollouts: 4, cap: 4, ..PlayoutParams::new(3) };
    let mut pilot = PlayoutPlayer::with_extra_lists(deck, opp, params, Vec::new());
    let obs = PlayerObservation::from_state(&state, actor, &RevealedKnowledge::default());
    let _ = take_switch_note();
    let chosen = pilot.decision_fn(&mut StdRng::seed_from_u64(1), &obs, &actions);
    let note = take_switch_note().expect("a play-out decision leaves a note");
    assert!(actions.iter().any(|a| deckgym::kg_log::label(a) == note.km));
    assert_eq!(deckgym::kg_log::label(&chosen), note.chosen);
    assert_eq!(note.changed, note.km != note.chosen);
    assert!(take_switch_note().is_none(), "reading the note clears it");
    let _ = SimpleAction::EndTurn;
}
