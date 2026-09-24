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

fn game_with_board(trainer: CardId, board: Vec<PlayedCard>, opponent: PlayedCard) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(board, vec![opponent]);
    state.hands[0] = vec![Card::Trainer(make_trainer_card(trainer))];
    game.set_state(state);
    game
}

fn can_play(game: &Game<'static>, name: &str) -> bool {
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions.iter().any(
        |a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == name),
    )
}

/// Acerola (A3 148): "Choose 1 of your Palossand or Mimikyu that has damage on it, and move 40 of
/// its damage to your opponent's Active Pokémon."
#[test]
fn test_acerola_moves_40_damage_to_opponent_active() {
    // Palossand has 130 HP; put it on 60 (70 damage) so 40 can be moved.
    let mut game = game_with_board(
        CardId::A3148Acerola,
        vec![PlayedCard::from_id(CardId::A3082Palossand).with_remaining_hp(60)],
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: make_trainer_card(CardId::A3148Acerola),
        },
        is_stack: false,
    });

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let move_damage = choices
        .iter()
        .find(|a| matches!(a.action, SimpleAction::MoveDamageToOpponentActive { .. }))
        .expect("Acerola should offer to move damage off Palossand")
        .clone();
    game.apply_action(&move_damage);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_remaining_hp(0, 0),
        100,
        "Palossand should be healed by the 40 damage moved off it"
    );
    assert_eq!(
        state.get_remaining_hp(1, 0),
        30,
        "Bulbasaur (70 HP) should take the 40 moved damage"
    );
}

/// Only part of the 40 is available when the chosen Pokémon has less damage than that.
#[test]
fn test_acerola_moves_only_the_damage_that_is_there() {
    // Mimikyu has 70 HP; put it on 50 so it only carries 20 damage.
    let mut game = game_with_board(
        CardId::A3190Acerola,
        vec![PlayedCard::from_id(CardId::A3083Mimikyu).with_remaining_hp(50)],
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: make_trainer_card(CardId::A3190Acerola),
        },
        is_stack: false,
    });

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let move_damage = choices
        .iter()
        .find(|a| matches!(a.action, SimpleAction::MoveDamageToOpponentActive { .. }))
        .expect("Acerola should offer to move damage off Mimikyu")
        .clone();
    game.apply_action(&move_damage);

    let state = game.get_state_clone();
    assert_eq!(state.get_remaining_hp(0, 0), 70, "Mimikyu is fully healed");
    assert_eq!(
        state.get_remaining_hp(1, 0),
        50,
        "Only the 20 damage that was actually there moves across"
    );
}

/// Negative case: an undamaged Palossand is not a legal choice, so Acerola cannot be played.
#[test]
fn test_acerola_unplayable_without_damage_on_a_named_pokemon() {
    let game = game_with_board(
        CardId::A3148Acerola,
        vec![PlayedCard::from_id(CardId::A3082Palossand)],
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    assert!(
        !can_play(&game, "Acerola"),
        "Acerola needs a Palossand or Mimikyu that has damage on it"
    );
}

/// Negative case: Acerola names only Palossand and Mimikyu.
#[test]
fn test_acerola_unplayable_with_only_unnamed_damaged_pokemon() {
    let game = game_with_board(
        CardId::A3148Acerola,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10)],
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    assert!(
        !can_play(&game, "Acerola"),
        "A damaged Bulbasaur is not an Acerola target"
    );
}
