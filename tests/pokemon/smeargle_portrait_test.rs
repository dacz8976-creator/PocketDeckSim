//! Smeargle's Portrait copies a Supporter out of the opponent's *hand*, so its tests check that
//! the copied card's effect resolves for Smeargle's controller and that the copied card stays in
//! the opponent's hand.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

/// Smeargle (B2 130) Portrait: "Once during your turn, if this Pokémon is in the Active Spot, you
/// may look at a random Supporter card from your opponent's hand. Use the effect of that card as
/// the effect of this Ability."
fn game_with_opponent_hand(smeargle_active: bool, opponent_hand: Vec<Card>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    let smeargle = PlayedCard::from_id(CardId::B2130Smeargle);
    let filler = PlayedCard::from_id(CardId::A1001Bulbasaur);
    state.set_board(
        if smeargle_active {
            vec![smeargle, filler]
        } else {
            vec![filler, smeargle]
        },
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![];
    state.hands[1] = opponent_hand;
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1a025Pikachu); 6];
    game.set_state(state);
    game
}

fn portrait_action(smeargle_idx: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::UseAbility {
            in_play_idx: smeargle_idx,
        },
        is_stack: false,
    }
}

fn can_use_portrait(game: &Game<'static>, smeargle_idx: usize) -> bool {
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions.iter().any(|a| {
        matches!(
            a.action,
            SimpleAction::UseAbility { in_play_idx } if in_play_idx == smeargle_idx
        )
    })
}

/// With Professor's Research ("Draw 2 cards.") as the only Supporter in the opponent's hand,
/// Portrait must draw 2 cards for *Smeargle's* controller and leave the card in the opponent's
/// hand.
#[test]
fn test_portrait_copies_the_only_supporter_in_the_opponent_hand() {
    let professors_research = get_card_by_enum(CardId::PA007ProfessorsResearch);
    let mut game = game_with_opponent_hand(true, vec![professors_research.clone()]);

    assert!(can_use_portrait(&game, 0));
    game.apply_action(&portrait_action(0));

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[0].len(),
        2,
        "Portrait should resolve Professor's Research for Smeargle's controller"
    );
    assert_eq!(state.decks[0].cards.len(), 4);
    assert_eq!(
        state.hands[1],
        vec![professors_research],
        "the card is only looked at, so it stays in the opponent's hand"
    );
}

/// Portrait is once per turn.
#[test]
fn test_portrait_cannot_be_used_twice_in_a_turn() {
    let mut game = game_with_opponent_hand(
        true,
        vec![get_card_by_enum(CardId::PA007ProfessorsResearch)],
    );

    game.apply_action(&portrait_action(0));
    assert!(
        !can_use_portrait(&game, 0),
        "Portrait is 'once during your turn'"
    );
}

/// Hidden target absence does not disable an attempt.
#[test]
fn test_portrait_offered_without_a_supporter_in_the_opponent_hand() {
    let game = game_with_opponent_hand(
        true,
        // A Pokémon and an Item are not Supporters.
        vec![
            get_card_by_enum(CardId::A1001Bulbasaur),
            get_card_by_enum(CardId::PA005PokeBall),
        ],
    );

    assert!(
        can_use_portrait(&game, 0),
        "Hidden Supporter absence must not disable Portrait"
    );
}

/// NEGATIVE: Portrait only works from the Active Spot.
#[test]
fn test_portrait_not_offered_from_the_bench() {
    let game = game_with_opponent_hand(
        false,
        vec![get_card_by_enum(CardId::PA007ProfessorsResearch)],
    );

    assert!(
        !can_use_portrait(&game, 1),
        "Portrait requires Smeargle to be in the Active Spot"
    );
}
