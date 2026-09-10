//! Morty, Hiker, Looker, Pokédex, Rotom Dex and Hand Scope are pure *information* cards: they
//! reveal or reorder hidden cards without changing anything a player without that information can
//! act on. deckgym's bots have no hidden-information model, so these are implemented as
//! legal-but-inert plays. These tests pin that down: the card is playable, resolving it does not
//! panic, and the only observable change is the card moving from hand to discard.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

fn make_trainer_card(card_id: CardId) -> deckgym::models::TrainerCard {
    get_card_by_enum(card_id).as_trainer()
}

fn game_with_hidden_zones(trainer: CardId) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![
        Card::Trainer(make_trainer_card(trainer)),
        get_card_by_enum(CardId::A1053Squirtle),
    ];
    state.hands[1] = vec![get_card_by_enum(CardId::A1a025Pikachu)];
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1001Bulbasaur); 6];
    state.decks[1].cards = vec![get_card_by_enum(CardId::A1033Charmander); 6];
    game.set_state(state);
    game
}

/// Plays `trainer` and asserts it was legal and left every observable zone untouched apart from
/// the played card itself moving to the discard pile.
fn assert_playable_and_inert(trainer: CardId, name: &str) {
    let mut game = game_with_hidden_zones(trainer);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        actions.iter().any(|a| matches!(
            &a.action,
            SimpleAction::Play { trainer_card } if trainer_card.name == name
        )),
        "{name} should be playable"
    );

    let before = game.get_state_clone();
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: make_trainer_card(trainer),
        },
        is_stack: false,
    });
    let after = game.get_state_clone();

    assert_eq!(
        after.hands[0],
        vec![get_card_by_enum(CardId::A1053Squirtle)],
        "{name} should only remove itself from hand"
    );
    assert_eq!(
        after.hands[1], before.hands[1],
        "{name} must not move the opponent's hand"
    );
    assert_eq!(
        after.decks[0].cards.len(),
        before.decks[0].cards.len(),
        "{name} must not change the size of your deck"
    );
    assert_eq!(
        after.decks[1].cards.len(),
        before.decks[1].cards.len(),
        "{name} must not change the size of the opponent's deck"
    );
    assert_eq!(
        after.discard_piles[0].len(),
        before.discard_piles[0].len() + 1,
        "{name} itself goes to the discard pile"
    );
    assert_eq!(after.points, before.points);
    assert!(after.winner.is_none());
}

/// Morty (A4a 071): "For each of your [P] Pokémon in play, look at that many cards from the top of
/// your opponent's deck and put them back in any order."
#[test]
fn test_morty_is_a_legal_but_inert_play() {
    assert_playable_and_inert(CardId::A4a071Morty, "Morty");
    assert_playable_and_inert(CardId::A4a085Morty, "Morty");
}

/// Hiker (A4 161): "For each of your [F] Pokémon in play, look at that many cards from the top of
/// your deck and put them back in any order."
#[test]
fn test_hiker_is_a_legal_but_inert_play() {
    assert_playable_and_inert(CardId::A4161Hiker, "Hiker");
    assert_playable_and_inert(CardId::A4201Hiker, "Hiker");
}

/// Looker (A3a 068): "Your opponent reveals all of the Supporter cards in their deck."
#[test]
fn test_looker_is_a_legal_but_inert_play() {
    assert_playable_and_inert(CardId::A3a068Looker, "Looker");
    assert_playable_and_inert(CardId::A3a082Looker, "Looker");
}

/// Pokédex (P-A 004): "Look at the top 3 cards of your deck."
#[test]
fn test_pokedex_is_a_legal_but_inert_play() {
    assert_playable_and_inert(CardId::PA004PokedEx, "Pokédex");
    assert_playable_and_inert(CardId::PA008PokedEx, "Pokédex");
}

/// Rotom Dex (A3 145): "Look at the top card of your deck. Then, you may shuffle your deck."
#[test]
fn test_rotom_dex_is_a_legal_but_inert_play() {
    assert_playable_and_inert(CardId::A3145RotomDEx, "Rotom Dex");
}

/// Hand Scope (P-A 003): "Your opponent reveals their hand."
#[test]
fn test_hand_scope_is_a_legal_but_inert_play() {
    assert_playable_and_inert(CardId::PA003HandScope, "Hand Scope");
}

/// The information Supporters still consume the once-per-turn Supporter slot, so no other
/// Supporter can follow them. (The Items do not, which is what makes the distinction observable.)
#[test]
fn test_information_supporter_still_uses_the_supporter_slot() {
    let mut game = game_with_hidden_zones(CardId::A3a068Looker);
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(make_trainer_card(CardId::A4161Hiker)));
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: make_trainer_card(CardId::A3a068Looker),
        },
        is_stack: false,
    });

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        !actions.iter().any(|a| matches!(
            &a.action,
            SimpleAction::Play { trainer_card } if trainer_card.name == "Hiker"
        )),
        "A second Supporter should not be playable after Looker"
    );
}
