//! Penny copies a Supporter out of the opponent's deck, so its tests check that the copied card's
//! effect really resolves for the Penny player, and that the copied card stays in the opponent's
//! deck afterwards.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

fn make_trainer_card(card_id: CardId) -> deckgym::models::TrainerCard {
    get_card_by_enum(card_id).as_trainer()
}

fn game_with_opponent_deck(penny: CardId, opponent_deck: Vec<Card>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.hands[0] = vec![Card::Trainer(make_trainer_card(penny))];
    state.hands[1] = vec![];
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1a025Pikachu); 6];
    state.decks[1].cards = opponent_deck;
    game.set_state(state);
    game
}

fn play_trainer(game: &mut Game<'static>, trainer: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: make_trainer_card(trainer),
        },
        is_stack: false,
    });
}

fn can_play(game: &Game<'static>, name: &str) -> bool {
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions.iter().any(
        |a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == name),
    )
}

/// Penny (A3b 069): "Look at a random Supporter card that's not Penny from your opponent's deck and
/// shuffle it back into their deck. Use the effect of that card as the effect of this card."
///
/// With Professor's Research ("Draw 2 cards.") as the only Supporter in the opponent's deck, Penny
/// must draw 2 cards for *its own* controller, and leave the copied card in the opponent's deck.
#[test]
fn test_penny_copies_the_only_supporter_in_the_opponent_deck() {
    let mut game = game_with_opponent_deck(
        CardId::A3b069Penny,
        vec![
            get_card_by_enum(CardId::PA007ProfessorsResearch),
            get_card_by_enum(CardId::A1001Bulbasaur),
        ],
    );
    play_trainer(&mut game, CardId::A3b069Penny);

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[0].len(),
        2,
        "Penny should have drawn 2 cards, copying Professor's Research"
    );
    assert!(state.hands[1].is_empty(), "The opponent draws nothing");
    assert_eq!(
        state.decks[1].cards.len(),
        2,
        "The copied Supporter is shuffled back into the opponent's deck"
    );
    assert!(state.decks[1]
        .cards
        .iter()
        .any(|card| card.get_name() == "Professor's Research"));
}

/// Copying a turn-effect Supporter must apply that effect to the Penny player's own attacks:
/// Giovanni gives +10, so Hitmonlee's 30-damage Kick becomes 40 and KOs a 40 HP defender.
#[test]
fn test_penny_copies_a_turn_effect_supporter() {
    let mut game = game_with_opponent_deck(
        CardId::B2a092Penny,
        vec![get_card_by_enum(CardId::A1223Giovanni)],
    );
    let mut state = game.get_state_clone();
    state.in_play_pokemon[1][0] =
        Some(PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(40));
    game.set_state(state);

    play_trainer(&mut game, CardId::B2a092Penny);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let attack = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::Attack(_)))
        .expect("Hitmonlee should be able to attack")
        .clone();
    game.apply_action(&attack);

    let state = game.get_state_clone();
    assert_eq!(
        state.points[0], 1,
        "Giovanni's +10 (copied by Penny) should turn a 30 damage Kick into a KO"
    );
}

/// Negative case: no Supporter at all in the opponent's deck.
#[test]
fn test_penny_unplayable_without_a_supporter_in_the_opponent_deck() {
    let game = game_with_opponent_deck(
        CardId::A3b086Penny,
        vec![
            get_card_by_enum(CardId::A1001Bulbasaur),
            get_card_by_enum(CardId::PA005PokeBall),
        ],
    );
    assert!(
        !can_play(&game, "Penny"),
        "Penny needs a Supporter in the opponent's deck to copy"
    );
}

/// Negative case: the only Supporter in the opponent's deck is Penny itself, which the card
/// explicitly excludes.
#[test]
fn test_penny_cannot_copy_another_penny() {
    let game = game_with_opponent_deck(
        CardId::B2a109Penny,
        vec![
            get_card_by_enum(CardId::A3b069Penny),
            get_card_by_enum(CardId::A1001Bulbasaur),
        ],
    );
    assert!(
        !can_play(&game, "Penny"),
        "\"a Supporter card that's not Penny\" excludes every Penny printing"
    );
}
