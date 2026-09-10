//! §187 — F017 acceptance: Professor's Research needs a card it can actually draw.
//!
//! The expectations here are NOT new: they are the acceptance line written into OPEN_FIXES.tsv
//! row F017 at §186, before this fix existed, and they are reproduced unchanged.
//!
//! Rule (DUSTIN-RULE-SENSOR): an action card needs a valid thing to act on. Professor's Research
//! has NO target — its precondition is a resource one: at least one card must be drawable.
//!
//! ⚠ Different shape from F014 (a missing per-target filter on a targeted card). The third test
//! is what keeps the fix honest: another Supporter must stay playable in the SAME empty-deck
//! state, so this can never be satisfied by a blanket supporter block.
//!
//! Results are the behaviour of the source that builds them, never automatically of any binary.

use deckgym::{
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

const RESEARCH: &str = "P-A 007";
const COPYCAT: &str = "B1 225";

/// Build a game where the actor holds Professor's Research and a Copycat, with `deck_len` cards
/// left in the actor's deck.
fn game_with_deck_len(deck_len: usize) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.hands[0] = vec![
        get_card_by_enum(CardId::PA007ProfessorsResearch),
        get_card_by_enum(CardId::B1225Copycat),
    ];
    state.decks[0].cards.truncate(deck_len);
    game.set_state(state);
    game
}

/// Ids of the trainer cards offered as `Play` actions to the current player.
fn offered_play_ids(game: &Game<'static>) -> Vec<String> {
    let state = game.get_state_clone();
    let (_actor, choices) = state.generate_possible_actions();
    let mut ids: Vec<String> = choices
        .iter()
        .filter_map(|a| match &a.action {
            deckgym::actions::SimpleAction::Play { trainer_card } => Some(trainer_card.id.clone()),
            _ => None,
        })
        .collect();
    ids.sort();
    ids.dedup();
    ids
}

#[test]
fn f017_empty_deck_does_not_offer_professors_research() {
    let game = game_with_deck_len(0);
    let ids = offered_play_ids(&game);
    println!("[F017-A] deck 0 cards -> offered Play ids {ids:?}");
    assert!(
        !ids.iter().any(|i| i == RESEARCH),
        "with an empty deck nothing can be drawn, so the card must not be offered"
    );
}

#[test]
fn f017_one_card_left_still_offers_professors_research() {
    let game = game_with_deck_len(1);
    let ids = offered_play_ids(&game);
    println!("[F017-B] deck 1 card -> offered Play ids {ids:?}");
    assert!(
        ids.iter().any(|i| i == RESEARCH),
        "one drawable card is enough — the fix must not over-restrict"
    );
}

#[test]
fn f017_full_deck_still_offers_professors_research() {
    let game = game_with_deck_len(14);
    let ids = offered_play_ids(&game);
    println!("[F017-C] deck 14 cards -> offered Play ids {ids:?}");
    assert!(ids.iter().any(|i| i == RESEARCH));
}

#[test]
fn f017_other_supporters_survive_the_same_empty_deck_state() {
    // The anti-blanket-block control: in the SAME empty-deck state, a different Supporter that
    // this fix has no business touching must still be playable.
    let game = game_with_deck_len(0);
    let ids = offered_play_ids(&game);
    println!("[F017-D] deck 0 cards -> other Supporters still offered? {ids:?}");
    assert!(
        ids.iter().any(|i| i == COPYCAT),
        "the fix must be card-specific, not a blanket supporter block"
    );
}
