//! Lt. Surge and Juggler both gather Energy from the Bench onto the Active Pokémon; they differ
//! in which Energy moves and in what makes them legal to play.

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

fn energy(game: &Game<'static>, idx: usize) -> Vec<EnergyType> {
    game.get_state_clone().in_play_pokemon[0][idx]
        .as_ref()
        .map(|p| p.attached_energy.clone())
        .unwrap_or_default()
}

// --- Lt. Surge ---

/// Lt. Surge (A1 226): "Move all [L] Energy from your Benched Pokémon to your Raichu, Electrode,
/// or Electabuzz in the Active Spot." Only Lightning moves; other Energy stays on the Bench.
#[test]
fn test_lt_surge_gathers_only_lightning_energy_onto_the_active() {
    let mut game = game_with_board(
        CardId::A1226LtSurge,
        vec![
            PlayedCard::from_id(CardId::A1100Electrode).with_energy(vec![EnergyType::Lightning]),
            PlayedCard::from_id(CardId::A1a025Pikachu).with_energy(vec![
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Water,
            ]),
            PlayedCard::from_id(CardId::A1a025Pikachu).with_energy(vec![EnergyType::Lightning]),
        ],
    );
    play_trainer(&mut game, CardId::A1226LtSurge);

    assert_eq!(
        energy(&game, 0),
        vec![EnergyType::Lightning; 4],
        "Electrode should end up with its own Lightning plus the three from the Bench"
    );
    assert_eq!(
        energy(&game, 1),
        vec![EnergyType::Water],
        "Non-Lightning Energy stays on the Bench"
    );
    assert!(energy(&game, 2).is_empty());
}

/// Negative case: the Active Spot must hold Raichu, Electrode or Electabuzz.
#[test]
fn test_lt_surge_unplayable_with_a_different_active() {
    let game = game_with_board(
        CardId::A1273LtSurge,
        vec![
            PlayedCard::from_id(CardId::A1a025Pikachu),
            PlayedCard::from_id(CardId::A1a025Pikachu).with_energy(vec![EnergyType::Lightning]),
        ],
    );
    assert!(
        !can_play(&game, "Lt. Surge"),
        "Pikachu is not one of the three named Active Pokemon"
    );
}

/// Negative case: nothing to move means nothing to do.
#[test]
fn test_lt_surge_unplayable_without_lightning_on_the_bench() {
    let game = game_with_board(
        CardId::A1273LtSurge,
        vec![
            PlayedCard::from_id(CardId::A1100Electrode).with_energy(vec![EnergyType::Lightning]),
            PlayedCard::from_id(CardId::A1a025Pikachu).with_energy(vec![EnergyType::Water]),
        ],
    );
    assert!(
        !can_play(&game, "Lt. Surge"),
        "There is no Lightning Energy on the Bench to move"
    );
}

// --- Juggler ---

/// Juggler (B2 151): "You can use this card only if your Pokémon in play have 3 or more different
/// types of Energy attached. Move all Energy from each of your Benched Pokémon to your Active
/// Pokémon."
#[test]
fn test_juggler_gathers_all_bench_energy_onto_the_active() {
    let mut game = game_with_board(
        CardId::B2151Juggler,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1a025Pikachu).with_energy(vec![EnergyType::Lightning]),
            PlayedCard::from_id(CardId::A1053Squirtle)
                .with_energy(vec![EnergyType::Water, EnergyType::Water]),
        ],
    );
    play_trainer(&mut game, CardId::B2151Juggler);

    let active = energy(&game, 0);
    assert_eq!(active.len(), 4, "All bench Energy joins the active's own");
    assert_eq!(
        active.iter().filter(|e| **e == EnergyType::Water).count(),
        2
    );
    assert!(energy(&game, 1).is_empty());
    assert!(energy(&game, 2).is_empty());
}

/// Negative case: only two different Energy types in play, so Juggler cannot be used.
#[test]
fn test_juggler_unplayable_with_fewer_than_three_energy_types() {
    let game = game_with_board(
        CardId::B2192Juggler,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1053Squirtle)
                .with_energy(vec![EnergyType::Water, EnergyType::Water]),
        ],
    );
    assert!(
        !can_play(&game, "Juggler"),
        "Grass + Water is only 2 different Energy types"
    );
}
