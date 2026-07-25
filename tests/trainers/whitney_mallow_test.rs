//! Whitney and Mallow are both "heal one of my named Pokémon" Supporters with a rider:
//! Whitney also cures three specific Special Conditions, Mallow discards all Energy from the
//! Pokémon it fully heals.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    test_support::get_initialized_game,
    Game,
};

fn make_trainer_card(card_id: CardId) -> deckgym::models::TrainerCard {
    get_card_by_enum(card_id).as_trainer()
}

fn game_with_board(trainer: CardId, board: Vec<PlayedCard>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(board, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
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

// --- Whitney ---

/// Whitney (A4a 069): "Heal 60 damage from 1 of your Miltank, and it recovers from being Asleep,
/// Paralyzed, and Confused." Notably it does NOT cure Poisoned or Burned.
#[test]
fn test_whitney_heals_miltank_and_cures_only_the_three_named_conditions() {
    let mut game = game_with_board(
        CardId::A4a069Whitney,
        vec![PlayedCard::from_id(CardId::A4a062Miltank)
            .with_remaining_hp(40)
            .with_status_condition(StatusCondition::Asleep)
            .with_status_condition(StatusCondition::Poisoned)],
    );
    play_trainer(&mut game, CardId::A4a069Whitney);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let heal = choices
        .iter()
        .find(|a| matches!(a.action, SimpleAction::HealAndCureConditions { .. }))
        .expect("Whitney should offer a heal on Miltank")
        .clone();
    game.apply_action(&heal);

    let state = game.get_state_clone();
    let miltank = state.in_play_pokemon[0][0].as_ref().expect("Miltank");
    assert_eq!(miltank.get_remaining_hp(), 100, "40 + 60 healed");
    assert!(!miltank.is_asleep(), "Asleep should be cured");
    assert!(
        miltank.is_poisoned(),
        "Poisoned is not one of the three conditions Whitney cures"
    );
}

/// Negative case: Whitney needs a Miltank that is damaged or has one of those conditions.
#[test]
fn test_whitney_unplayable_without_a_hurt_miltank() {
    let game = game_with_board(
        CardId::A4a083Whitney,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10)],
    );
    assert!(
        !can_play(&game, "Whitney"),
        "Whitney should not be playable with no Miltank in play"
    );

    let game = game_with_board(
        CardId::A4a083Whitney,
        vec![PlayedCard::from_id(CardId::A4a062Miltank)],
    );
    assert!(
        !can_play(&game, "Whitney"),
        "Whitney should not be playable on an undamaged, unafflicted Miltank"
    );
}

// --- Mallow ---

/// Mallow (A3 154): "Heal all damage from 1 of your Shiinotic or Tsareena. If you do, discard all
/// Energy from that Pokémon."
#[test]
fn test_mallow_fully_heals_tsareena_and_discards_its_energy() {
    let mut game = game_with_board(
        CardId::A3154Mallow,
        vec![PlayedCard::from_id(CardId::A3020Tsareena)
            .with_remaining_hp(30)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
    );
    play_trainer(&mut game, CardId::A3154Mallow);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let heal = choices
        .iter()
        .find(|a| matches!(a.action, SimpleAction::HealAndDiscardEnergy { .. }))
        .expect("Mallow should offer a full heal on Tsareena")
        .clone();
    game.apply_action(&heal);

    let state = game.get_state_clone();
    let tsareena = state.in_play_pokemon[0][0].as_ref().expect("Tsareena");
    assert_eq!(tsareena.get_remaining_hp(), 130, "Tsareena is fully healed");
    assert!(
        tsareena.attached_energy.is_empty(),
        "All Energy should have been discarded"
    );
    assert_eq!(state.discard_energies[0].len(), 2);
}

/// Negative case: Mallow needs a damaged Shiinotic or Tsareena; an undamaged one (or another
/// Pokémon entirely) is not a legal target.
#[test]
fn test_mallow_unplayable_without_a_damaged_named_pokemon() {
    let game = game_with_board(
        CardId::A3196Mallow,
        vec![PlayedCard::from_id(CardId::A3020Tsareena).with_energy(vec![EnergyType::Grass])],
    );
    assert!(
        !can_play(&game, "Mallow"),
        "Mallow should not be playable on an undamaged Tsareena"
    );

    let game = game_with_board(
        CardId::A3196Mallow,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10)],
    );
    assert!(
        !can_play(&game, "Mallow"),
        "Mallow should not be playable with no Shiinotic or Tsareena in play"
    );
}
