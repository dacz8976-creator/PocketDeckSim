//! Team Galactic Grunt, Traveling Merchant, Fisher and Fishing Net all move cards out of a hidden
//! zone (deck or discard pile) and into your hand.

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

fn game_with_zones(
    seed: u64,
    trainer: CardId,
    deck: Vec<Card>,
    discard: Vec<Card>,
) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.hands[0] = vec![Card::Trainer(make_trainer_card(trainer))];
    state.decks[0].cards = deck;
    state.discard_piles[0] = discard;
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

fn count_named(cards: &[Card], name: &str) -> usize {
    cards.iter().filter(|card| card.get_name() == name).count()
}

// --- Team Galactic Grunt ---

/// Team Galactic Grunt (A2 151): "Put 1 random Glameow, Stunky, or Croagunk from your deck into
/// your hand."
#[test]
fn test_team_galactic_grunt_fetches_a_named_basic_from_deck() {
    let mut game = game_with_zones(
        0,
        CardId::A2151TeamGalacticGrunt,
        vec![
            get_card_by_enum(CardId::A2139Glameow),
            get_card_by_enum(CardId::A1001Bulbasaur),
        ],
        vec![],
    );
    play_trainer(&mut game, CardId::A2151TeamGalacticGrunt);

    let state = game.get_state_clone();
    assert_eq!(count_named(&state.hands[0], "Glameow"), 1);
    assert_eq!(state.decks[0].cards.len(), 1);
}

/// Hidden deck contents cannot decide whether a search card is playable.
#[test]
fn test_team_galactic_grunt_playable_without_visible_targets_in_deck() {
    let mut game = game_with_zones(
        0,
        CardId::A2191TeamGalacticGrunt,
        vec![get_card_by_enum(CardId::A1001Bulbasaur)],
        vec![],
    );
    assert!(can_play(&game, "Team Galactic Grunt"));
    play_trainer(&mut game, CardId::A2191TeamGalacticGrunt);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0].len(), 0);
    assert_eq!(state.decks[0].cards.len(), 1);
}

// --- Traveling Merchant ---

/// Traveling Merchant (A4a 070): "Look at the top 4 cards of your deck. Put all Pokémon Tool cards
/// you find there into your hand. Shuffle the other cards back into your deck."
#[test]
fn test_traveling_merchant_pulls_tools_from_the_top_of_the_deck() {
    let mut game = game_with_zones(
        0,
        CardId::A4a070TravelingMerchant,
        vec![
            get_card_by_enum(CardId::A2148RockyHelmet),
            get_card_by_enum(CardId::A3b067Leftovers),
            get_card_by_enum(CardId::A1001Bulbasaur),
            get_card_by_enum(CardId::A1033Charmander),
        ],
        vec![],
    );
    play_trainer(&mut game, CardId::A4a070TravelingMerchant);

    let state = game.get_state_clone();
    assert_eq!(count_named(&state.hands[0], "Rocky Helmet"), 1);
    assert_eq!(count_named(&state.hands[0], "Leftovers"), 1);
    assert_eq!(
        state.decks[0].cards.len(),
        2,
        "Only the two non-Tool cards remain in the deck"
    );
}

/// Negative case: no Tool in the top 4 means nothing is taken.
#[test]
fn test_traveling_merchant_takes_nothing_when_no_tools_are_found() {
    let mut game = game_with_zones(
        0,
        CardId::A4a084TravelingMerchant,
        vec![get_card_by_enum(CardId::A1001Bulbasaur); 4],
        vec![],
    );
    play_trainer(&mut game, CardId::A4a084TravelingMerchant);

    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.decks[0].cards.len(), 4);
}

// --- Fisher ---

/// Fisher (A4 159): "Flip 3 coins. For each heads, a [W] Pokémon is chosen at random from your
/// discard pile and put into your hand."
///
/// The coin flips are priced by the search bots via `Outcomes::binomial_by_heads`, so the exact
/// number of heads depends on the seed. This asserts the invariants that must hold for every
/// outcome, and separately that at least one seed actually retrieves something.
#[test]
fn test_fisher_only_ever_retrieves_water_pokemon_from_the_discard() {
    let mut retrieved_somewhere = false;

    for seed in 0..8u64 {
        let mut game = game_with_zones(
            seed,
            CardId::A4159Fisher,
            vec![],
            vec![
                get_card_by_enum(CardId::A1053Squirtle),
                get_card_by_enum(CardId::A1053Squirtle),
                get_card_by_enum(CardId::A1053Squirtle),
                get_card_by_enum(CardId::A1001Bulbasaur),
            ],
        );
        play_trainer(&mut game, CardId::A4159Fisher);

        let state = game.get_state_clone();
        let retrieved = count_named(&state.hands[0], "Squirtle");
        assert!(retrieved <= 3, "At most 3 coins, so at most 3 Pokemon");
        assert_eq!(
            count_named(&state.discard_piles[0], "Squirtle"),
            3 - retrieved,
            "Every retrieved Squirtle left the discard pile"
        );
        assert_eq!(
            count_named(&state.hands[0], "Bulbasaur"),
            0,
            "Fisher only retrieves [W] Pokemon"
        );
        retrieved_somewhere |= retrieved > 0;
    }

    assert!(
        retrieved_somewhere,
        "Fisher should retrieve at least one Pokemon across 8 seeds"
    );
}

/// Negative case: no [W] Pokémon in the discard pile means Fisher is not playable.
#[test]
fn test_fisher_unplayable_without_water_pokemon_in_discard() {
    let game = game_with_zones(
        0,
        CardId::A4199Fisher,
        vec![],
        vec![get_card_by_enum(CardId::A1001Bulbasaur)],
    );
    assert!(
        !can_play(&game, "Fisher"),
        "Fisher has nothing to retrieve without a [W] Pokemon in the discard"
    );
}

// --- Fishing Net ---

/// Fishing Net (A3 143): "Put a random Basic [W] Pokémon from your discard pile into your hand."
#[test]
fn test_fishing_net_retrieves_a_basic_water_pokemon() {
    let mut game = game_with_zones(
        0,
        CardId::A3143FishingNet,
        vec![],
        vec![
            get_card_by_enum(CardId::A1053Squirtle),
            get_card_by_enum(CardId::A1054Wartortle),
            get_card_by_enum(CardId::A1001Bulbasaur),
        ],
    );
    play_trainer(&mut game, CardId::A3143FishingNet);

    let state = game.get_state_clone();
    assert_eq!(
        count_named(&state.hands[0], "Squirtle"),
        1,
        "Squirtle is the only Basic [W] Pokemon in the discard"
    );
    // Two originals remain, plus Fishing Net itself which is discarded when played.
    assert_eq!(state.discard_piles[0].len(), 3);
    assert_eq!(count_named(&state.discard_piles[0], "Squirtle"), 0);
}

/// Negative case: a Stage 1 Water Pokémon is not a Basic, so Fishing Net has no target.
#[test]
fn test_fishing_net_unplayable_without_a_basic_water_in_discard() {
    let game = game_with_zones(
        0,
        CardId::A3143FishingNet,
        vec![],
        vec![
            get_card_by_enum(CardId::A1054Wartortle),
            get_card_by_enum(CardId::A1001Bulbasaur),
        ],
    );
    assert!(
        !can_play(&game, "Fishing Net"),
        "Wartortle is Stage 1, so Fishing Net has no legal target"
    );
}
