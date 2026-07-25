//! Lana pulls one of the opponent's Benched Pokémon into the Active Spot; Budding Expeditioner
//! puts your own Active Mew ex back into your hand.

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

fn game_with_boards(
    trainer: CardId,
    board: Vec<PlayedCard>,
    opponent_board: Vec<PlayedCard>,
) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(board, opponent_board);
    state.hands[0] = vec![Card::Trainer(make_trainer_card(trainer))];
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

// --- Lana ---

/// Lana (A3 152): "You can use this card only if you have Araquanid in play. Switch in 1 of your
/// opponent's Benched Pokémon to the Active Spot."
#[test]
fn test_lana_switches_in_an_opponent_benched_pokemon() {
    let mut game = game_with_boards(
        CardId::A3152Lana,
        vec![PlayedCard::from_id(CardId::A3053Araquanid)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    play_trainer(&mut game, CardId::A3152Lana);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "Lana lets the player who used it choose");
    let switch = choices
        .iter()
        .find(|a| {
            matches!(
                a.action,
                SimpleAction::Activate {
                    player: 1,
                    in_play_idx: 1
                }
            )
        })
        .expect("Lana should offer to switch in the opponent's Charmander")
        .clone();
    game.apply_action(&switch);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Charmander");
}

/// Negative case: Lana can only be used with an Araquanid in play.
#[test]
fn test_lana_unplayable_without_araquanid() {
    let game = game_with_boards(
        CardId::A3194Lana,
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    assert!(
        !can_play(&game, "Lana"),
        "Lana requires an Araquanid in play"
    );
}

/// Negative case: nothing to switch in when the opponent has an empty Bench.
#[test]
fn test_lana_unplayable_when_opponent_bench_is_empty() {
    let game = game_with_boards(
        CardId::A3194Lana,
        vec![PlayedCard::from_id(CardId::A3053Araquanid)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    assert!(
        !can_play(&game, "Lana"),
        "Lana needs a Benched opponent Pokemon to switch in"
    );
}

// --- Budding Expeditioner ---

/// Budding Expeditioner (A1a 066): "Put your Mew ex in the Active Spot into your hand."
#[test]
fn test_budding_expeditioner_returns_active_mew_ex_to_hand() {
    let mut game = game_with_boards(
        CardId::A1a066BuddingExpeditioner,
        vec![
            PlayedCard::from_id(CardId::A1a032MewEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    play_trainer(&mut game, CardId::A1a066BuddingExpeditioner);

    let state = game.get_state_clone();
    assert!(
        state.hands[0].contains(&get_card_by_enum(CardId::A1a032MewEx)),
        "Mew ex should be back in hand"
    );

    // The Active Spot is now empty, so the player must promote from the Bench.
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|a| matches!(a.action, SimpleAction::Activate { player: 0, .. })));
}

/// Negative case: only a Mew ex in the Active Spot can be picked up.
#[test]
fn test_budding_expeditioner_unplayable_without_active_mew_ex() {
    let game = game_with_boards(
        CardId::A1a080BuddingExpeditioner,
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1a032MewEx),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    assert!(
        !can_play(&game, "Budding Expeditioner"),
        "A Benched Mew ex does not enable Budding Expeditioner"
    );
}
