//! §189 — sealed public-state / hidden-zone eligibility fixtures.
//!
//! Expectations were committed in `s189_E1_HIDDEN_ZONE_RULE_BIND_AND_SCOPE.txt` at a8cc48f
//! before this file existed and before the relevant implementation was read.
//! These are deterministic state transitions, not simulation cells.

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
    let mut ids: Vec<String> = choices
        .iter()
        .filter_map(|a| match &a.action {
            SimpleAction::Play { trainer_card } => Some(trainer_card.id.clone()),
            _ => None,
        })
        .collect();
    ids.sort();
    ids.dedup();
    ids
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

fn discard_has(state: &deckgym::State, player: usize, id: &str) -> bool {
    state.discard_piles[player]
        .iter()
        .any(|card| card.get_id() == id)
}

#[test]
fn p1_poke_ball_nonempty_deck_with_basic_fetches_one_basic() {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA005PokeBall)];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    game.set_state(state);

    let action = offered_play(&game, POKE_BALL).expect("Poké Ball should be offered");
    game.apply_action(&action);
    let after = game.get_state_clone();
    println!(
        "[P1] offered=true hand={:?} deck={} discarded={}",
        ids(&after.hands[0]),
        after.decks[0].cards.len(),
        discard_has(&after, 0, POKE_BALL)
    );
    assert_eq!(ids(&after.hands[0]), vec!["A1 001".to_string()]);
    assert_eq!(after.decks[0].cards.len(), 2);
    assert!(discard_has(&after, 0, POKE_BALL));
}

#[test]
fn p2_poke_ball_nonempty_deck_without_basic_is_playable_noop_search() {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA005PokeBall)];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    game.set_state(state);

    let action = offered_play(&game, POKE_BALL)
        .expect("hidden-zone search may be played even when no Basic is found");
    game.apply_action(&action);
    let after = game.get_state_clone();
    println!(
        "[P2] offered=true hand={} deck={} discarded={}",
        after.hands[0].len(),
        after.decks[0].cards.len(),
        discard_has(&after, 0, POKE_BALL)
    );
    assert!(after.hands[0].is_empty());
    assert_eq!(after.decks[0].cards.len(), 2);
    assert!(discard_has(&after, 0, POKE_BALL));
}

#[test]
fn p3_poke_ball_empty_deck_is_not_offered() {
    let mut game = base_game();
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA005PokeBall)];
    state.decks[0].cards.clear();
    game.set_state(state);

    let offered = offered_play_ids(&game);
    println!("[P3] empty deck -> offered Play ids {offered:?}");
    assert!(
        !offered.iter().any(|id| id == POKE_BALL),
        "a visibly empty deck makes Poké Ball unplayable"
    );
}

#[test]
fn c1_copycat_is_offered_when_opponent_hand_is_empty() {
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
    println!("[C1] opponent hand 0 -> offered Play ids {offered:?}");
    assert!(offered.iter().any(|id| id == COPYCAT));
}

#[test]
fn c2_copycat_empty_deck_recycles_four_remaining_hand_cards() {
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

    let action = offered_play(&game, COPYCAT).expect("Copycat should be offered");
    game.apply_action(&action);
    let after = game.get_state_clone();
    println!(
        "[C2] deck0+four hand -> hand={:?} deck={} discarded={}",
        ids(&after.hands[0]),
        after.decks[0].cards.len(),
        discard_has(&after, 0, COPYCAT)
    );
    assert_eq!(ids(&after.hands[0]), ids(&expected));
    assert!(after.decks[0].cards.is_empty());
    assert!(discard_has(&after, 0, COPYCAT));
}

#[test]
fn c3_copycat_draw_is_capped_by_post_shuffle_cards_available() {
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

    let action = offered_play(&game, COPYCAT).expect("Copycat should remain offered");
    game.apply_action(&action);
    let after = game.get_state_clone();
    println!(
        "[C3] two deck+two hand, opponent6 -> hand={} deck={} discarded={}",
        after.hands[0].len(),
        after.decks[0].cards.len(),
        discard_has(&after, 0, COPYCAT)
    );
    assert_eq!(after.hands[0].len(), 4);
    assert!(after.decks[0].cards.is_empty());
    assert!(discard_has(&after, 0, COPYCAT));
}
