//! §189 standalone reproducibility probe: same six sealed cases, no panic metadata.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

const COPYCAT: &str = "B1 225";
const POKE_BALL: &str = "P-A 005";

fn base_game() -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.current_player = 0;
    game.set_state(state);
    game
}

fn offered_play_ids(game: &Game<'static>) -> Vec<String> {
    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let mut out: Vec<String> = choices
        .iter()
        .filter_map(|a| match &a.action {
            SimpleAction::Play { trainer_card } => Some(trainer_card.id.clone()),
            _ => None,
        })
        .collect();
    out.sort();
    out.dedup();
    out
}

fn offered_play(game: &Game<'static>, id: &str) -> Option<Action> {
    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    choices.into_iter().find(|a| {
        matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.id == id)
    })
}

fn ids(cards: &[Card]) -> Vec<String> {
    let mut out: Vec<String> = cards.iter().map(Card::get_id).collect();
    out.sort();
    out
}

fn discarded(game: &Game<'static>, id: &str) -> bool {
    game.get_state_clone().discard_piles[0]
        .iter()
        .any(|card| card.get_id() == id)
}

fn p1() -> (bool, String) {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA005PokeBall)];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    game.set_state(state);
    let Some(action) = offered_play(&game, POKE_BALL) else {
        return (false, "offered=false".into());
    };
    game.apply_action(&action);
    let after = game.get_state_clone();
    let hand = ids(&after.hands[0]);
    let ok = hand == vec!["A1 001".to_string()]
        && after.decks[0].cards.len() == 2
        && discarded(&game, POKE_BALL);
    (ok, format!("offered=true hand={hand:?} deck={} discarded={}", after.decks[0].cards.len(), discarded(&game, POKE_BALL)))
}

fn p2() -> (bool, String) {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA005PokeBall)];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    game.set_state(state);
    let Some(action) = offered_play(&game, POKE_BALL) else {
        return (false, "offered=false".into());
    };
    game.apply_action(&action);
    let after = game.get_state_clone();
    let ok = after.hands[0].is_empty()
        && after.decks[0].cards.len() == 2
        && discarded(&game, POKE_BALL);
    (ok, format!("offered=true hand={} deck={} discarded={}", after.hands[0].len(), after.decks[0].cards.len(), discarded(&game, POKE_BALL)))
}

fn p3() -> (bool, String) {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA005PokeBall)];
    state.decks[0].cards.clear();
    game.set_state(state);
    let offered = offered_play_ids(&game);
    (!offered.iter().any(|id| id == POKE_BALL), format!("empty-deck offered={offered:?}"))
}

fn c1() -> (bool, String) {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::B1225Copycat),
        get_card_by_enum(CardId::PA001Potion),
    ];
    state.hands[1].clear();
    state.decks[0].cards = vec![get_card_by_enum(CardId::PA006RedCard)];
    game.set_state(state);
    let offered = offered_play_ids(&game);
    (offered.iter().any(|id| id == COPYCAT), format!("opponent-hand=0 offered={offered:?}"))
}

fn c2() -> (bool, String) {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    let expected = vec![
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::PA002XSpeed),
        get_card_by_enum(CardId::PA005PokeBall),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    state.hands[0] = std::iter::once(get_card_by_enum(CardId::B1225Copycat))
        .chain(expected.clone())
        .collect();
    state.decks[0].cards.clear();
    state.hands[1] = vec![get_card_by_enum(CardId::PA001Potion); 6];
    game.set_state(state);
    let Some(action) = offered_play(&game, COPYCAT) else {
        return (false, "offered=false".into());
    };
    game.apply_action(&action);
    let after = game.get_state_clone();
    let hand = ids(&after.hands[0]);
    let ok = hand == ids(&expected)
        && after.decks[0].cards.is_empty()
        && discarded(&game, COPYCAT);
    (ok, format!("offered=true hand={hand:?} deck={} discarded={}", after.decks[0].cards.len(), discarded(&game, COPYCAT)))
}

fn c3() -> (bool, String) {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::B1225Copycat),
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::PA002XSpeed),
    ];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::PA005PokeBall),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    state.hands[1] = vec![get_card_by_enum(CardId::PA001Potion); 6];
    game.set_state(state);
    let Some(action) = offered_play(&game, COPYCAT) else {
        return (false, "offered=false".into());
    };
    game.apply_action(&action);
    let after = game.get_state_clone();
    let ok = after.hands[0].len() == 4
        && after.decks[0].cards.is_empty()
        && discarded(&game, COPYCAT);
    (ok, format!("offered=true hand={} deck={} discarded={}", after.hands[0].len(), after.decks[0].cards.len(), discarded(&game, COPYCAT)))
}

fn main() {
    let cases: [(&str, fn() -> (bool, String)); 6] = [
        ("P1", p1), ("P2", p2), ("P3", p3),
        ("C1", c1), ("C2", c2), ("C3", c3),
    ];
    let mut passed = 0;
    for (name, run) in cases {
        let (ok, detail) = run();
        if ok { passed += 1; }
        println!("CASE {name} {} {detail}", if ok { "PASS" } else { "FAIL" });
    }
    let failed = 6 - passed;
    println!("SUMMARY {passed} passed {failed} failed 6 total");
    if failed != 0 { std::process::exit(1); }
}
