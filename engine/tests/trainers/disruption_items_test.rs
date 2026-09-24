//! Squirt Bottle, Hitting Hammer, Prank Spinner and Pokémon Flute all reach across the table:
//! the first two strip Energy off the opponent's Active, Prank Spinner shuffles a random card out
//! of a hand, and Pokémon Flute puts a Basic back onto the opponent's Bench.

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

fn game_with_boards(
    seed: u64,
    trainer: CardId,
    board: Vec<PlayedCard>,
    opponent_board: Vec<PlayedCard>,
) -> Game<'static> {
    let mut game = get_initialized_game(seed);
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

fn opponent_active_energy(game: &Game<'static>) -> Vec<EnergyType> {
    game.get_state_clone().get_active(1).attached_energy.clone()
}

// --- Squirt Bottle ---

/// Squirt Bottle (A4 152): "Discard a [R] Energy from your opponent's Active Pokémon."
#[test]
fn test_squirt_bottle_discards_one_fire_energy() {
    let mut game = game_with_boards(
        0,
        CardId::A4152SquirtBottle,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![
            PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Fire,
                EnergyType::Water,
            ]),
        ],
    );
    play_trainer(&mut game, CardId::A4152SquirtBottle);

    let energy = opponent_active_energy(&game);
    assert_eq!(energy.len(), 2);
    assert_eq!(
        energy.iter().filter(|e| **e == EnergyType::Fire).count(),
        1,
        "Exactly one Fire Energy should have been discarded"
    );
    assert_eq!(
        energy.iter().filter(|e| **e == EnergyType::Water).count(),
        1,
        "Non-Fire Energy is untouched"
    );
    assert_eq!(game.get_state_clone().discard_energies[1].len(), 1);
}

/// Negative case: no [R] Energy on the opponent's Active means nothing to discard.
#[test]
fn test_squirt_bottle_unplayable_without_fire_energy_on_opponent_active() {
    let game = game_with_boards(
        0,
        CardId::A4152SquirtBottle,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![EnergyType::Water])],
    );
    assert!(
        !can_play(&game, "Squirt Bottle"),
        "Squirt Bottle needs a [R] Energy to discard"
    );
}

// --- Hitting Hammer ---

/// Hitting Hammer (B1 215): "Flip 2 coins. If both of them are heads, discard a random Energy from
/// your opponent's Active Pokémon."
///
/// The coins are priced through `Outcomes::binomial_by_heads`, so the result is seed-dependent:
/// this asserts the only two legal outcomes (0 or exactly 1 Energy gone) and that both occur
/// across a spread of seeds.
#[test]
fn test_hitting_hammer_discards_at_most_one_energy_and_sometimes_none() {
    let mut saw_discard = false;
    let mut saw_no_discard = false;

    for seed in 0..12u64 {
        let mut game = game_with_boards(
            seed,
            CardId::B1215HittingHammer,
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::A1033Charmander)
                .with_energy(vec![EnergyType::Fire, EnergyType::Fire])],
        );
        play_trainer(&mut game, CardId::B1215HittingHammer);

        let remaining = opponent_active_energy(&game).len();
        assert!(
            remaining == 1 || remaining == 2,
            "Hitting Hammer discards either nothing or exactly one Energy, got {remaining} left"
        );
        saw_discard |= remaining == 1;
        saw_no_discard |= remaining == 2;
    }

    assert!(saw_discard, "Two heads should come up across 12 seeds");
    assert!(
        saw_no_discard,
        "Fewer than two heads should come up across 12 seeds"
    );
}

/// Negative case: no Energy at all on the opponent's Active.
#[test]
fn test_hitting_hammer_unplayable_without_energy_on_opponent_active() {
    let game = game_with_boards(
        0,
        CardId::B1215HittingHammer,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    assert!(
        !can_play(&game, "Hitting Hammer"),
        "Hitting Hammer needs Energy to discard"
    );
}

// --- Prank Spinner ---

/// Prank Spinner (B1 213): "A card from among both player's hands is chosen at random, revealed to
/// the other player, and shuffled into its owner's deck."
#[test]
fn test_prank_spinner_shuffles_one_card_from_a_hand_into_its_owners_deck() {
    let mut game = game_with_boards(
        0,
        CardId::B1213PrankSpinner,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.hands[0].push(get_card_by_enum(CardId::A1053Squirtle));
    state.hands[1] = vec![get_card_by_enum(CardId::A1a025Pikachu)];
    state.decks[0].cards = vec![];
    state.decks[1].cards = vec![];
    game.set_state(state);

    play_trainer(&mut game, CardId::B1213PrankSpinner);

    let state = game.get_state_clone();
    // Prank Spinner itself is discarded when played, leaving Squirtle and Pikachu as the pool of
    // two candidates; exactly one of them ends up back in its owner's (previously empty) deck.
    let total_hand = state.hands[0].len() + state.hands[1].len();
    let total_deck = state.decks[0].cards.len() + state.decks[1].cards.len();
    assert_eq!(total_hand, 1, "One of the two hand cards was shuffled away");
    assert_eq!(total_deck, 1, "...and it went into its owner's deck");
    // The card is always returned to its *own* owner, never handed across the table.
    if state.decks[0].cards.len() == 1 {
        assert_eq!(state.decks[0].cards[0].get_name(), "Squirtle");
    } else {
        assert_eq!(state.decks[1].cards[0].get_name(), "Pikachu");
    }
}

/// Negative case: both hands empty (after Prank Spinner itself leaves) means no card to choose.
#[test]
fn test_prank_spinner_unplayable_with_no_other_cards_in_hand() {
    let mut game = game_with_boards(
        0,
        CardId::B1213PrankSpinner,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.hands[1] = vec![];
    game.set_state(state);

    assert!(
        !can_play(&game, "Prank Spinner"),
        "Prank Spinner would have no card to choose"
    );
}

// --- Pokémon Flute ---

/// Pokémon Flute (A1a 064): "Put a Basic Pokémon from your opponent's discard pile onto their
/// Bench."
#[test]
fn test_pokemon_flute_benches_a_basic_from_opponent_discard() {
    let mut game = game_with_boards(
        0,
        CardId::A1a064PokemonFlute,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.discard_piles[1] = vec![
        get_card_by_enum(CardId::A1053Squirtle),
        get_card_by_enum(CardId::A1054Wartortle),
    ];
    game.set_state(state);

    play_trainer(&mut game, CardId::A1a064PokemonFlute);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "The player using Pokemon Flute chooses");
    assert!(
        choices
            .iter()
            .all(|a| matches!(a.action, SimpleAction::BenchOpponentFromDiscard { .. })),
        "Only Wartortle is not Basic, so every choice benches Squirtle"
    );
    game.apply_action(&choices[0].clone());

    let state = game.get_state_clone();
    let benched: Vec<String> = state
        .enumerate_bench_pokemon(1)
        .map(|(_, p)| p.get_name())
        .collect();
    assert_eq!(benched, vec!["Squirtle".to_string()]);
    assert_eq!(
        state.discard_piles[1].len(),
        1,
        "Squirtle left the opponent's discard pile"
    );
}

/// Negative case: the opponent's discard pile holds no Basic Pokémon.
#[test]
fn test_pokemon_flute_unplayable_without_a_basic_in_opponent_discard() {
    let mut game = game_with_boards(
        0,
        CardId::A1a064PokemonFlute,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.discard_piles[1] = vec![get_card_by_enum(CardId::A1054Wartortle)];
    game.set_state(state);

    assert!(
        !can_play(&game, "Pokémon Flute"),
        "Wartortle is Stage 1, so there is nothing to bench"
    );
}

/// Negative case: the opponent's Bench is full.
#[test]
fn test_pokemon_flute_unplayable_when_opponent_bench_is_full() {
    let mut game = game_with_boards(
        0,
        CardId::A1a064PokemonFlute,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    let mut state = game.get_state_clone();
    state.discard_piles[1] = vec![get_card_by_enum(CardId::A1053Squirtle)];
    game.set_state(state);

    assert!(
        !can_play(&game, "Pokémon Flute"),
        "There is no room on the opponent's Bench"
    );
}
