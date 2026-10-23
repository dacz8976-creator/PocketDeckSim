//! Dual-type seam, the off-board checks (survey G4): a card in the deck or discard pile is an
//! "[X] Pokémon" when X is any of its *printed* types. Each routed site has a test where only the
//! synthetic card's SECOND printed type matches (main's single-type code misses it) and a
//! single-type control that behaves as on main.
//!
//! No printed dual-type card is in the database yet: each one here is a real card cloned from it
//! with `secondary_energy_type` set.
//!
//! Not here: Flame Patch's "[R] Pokémon" target in the bots' fuel credit (`players/fuel_credit.rs`
//! is a private module), tested next to it in that file.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_logic::{quick_grow_extract_candidates, wallace_candidates},
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::get_initialized_game,
    Game, State,
};

/// The real card `card_id` with `secondary` added as its second printed type. Its primary type
/// must differ from `secondary`, so a test built on it isolates the second type.
fn dual_type(card_id: CardId, secondary: EnergyType) -> Card {
    let Card::Pokemon(mut pokemon) = get_card_by_enum(card_id) else {
        panic!("{card_id:?} is not a Pokémon");
    };
    assert_ne!(
        pokemon.energy_type, secondary,
        "{card_id:?}: the primary type must not be the one under test"
    );
    assert_eq!(pokemon.secondary_energy_type, None, "{card_id:?} is single-type today");
    pokemon.secondary_energy_type = Some(secondary);
    Card::Pokemon(pokemon)
}

/// Player 0 to act on turn 3 with `board` against a Charmander; `trainer` is player 0's only card
/// in hand, and player 0's deck and discard pile are `deck` and `discard`.
fn game_with(
    board: Vec<PlayedCard>,
    trainer: CardId,
    deck: Vec<Card>,
    discard: Vec<Card>,
    seed: u64,
) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.set_board(board, vec![PlayedCard::from_id(CardId::A1033Charmander)]);
    state.current_player = 0;
    state.turn_count = 3;
    state.hands = [vec![get_card_by_enum(trainer)], vec![]];
    state.discard_piles = [discard, vec![]];
    state.decks[0].cards = deck;
    game.set_state(state);
    game
}

fn bulbasaur_board() -> Vec<PlayedCard> {
    vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]
}

fn offered_play(state: &State, trainer: CardId) -> Option<Action> {
    let wanted = get_card_by_enum(trainer).get_id();
    state.generate_possible_actions().1.into_iter().find(|action| {
        matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.id == wanted)
    })
}

/// Plays `trainer` as move generation offers it (fails if it isn't offered).
fn play_offered(game: &mut Game<'static>, trainer: CardId) {
    let action = offered_play(&game.get_state_clone(), trainer)
        .unwrap_or_else(|| panic!("{trainer:?} should be offered"));
    game.apply_action(&action);
}

/// Plays `trainer` without asking move generation, to test its effect alone.
fn play_directly(game: &mut Game<'static>, trainer: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: get_card_by_enum(trainer).as_trainer(),
        },
        is_stack: false,
    });
}

fn count_named(cards: &[Card], name: &str) -> usize {
    cards.iter().filter(|card| card.get_name() == name).count()
}

// --- Fishing Net (A3 143): "Put a random Basic [W] Pokémon from your discard pile into your hand."
// Legality: move_generation_trainer.rs `can_play_fishing_net`; effect: apply_trainer_action.rs
// `is_basic_water_pokemon`.

#[test]
fn fishing_net_is_offered_for_a_basic_whose_second_type_is_water() {
    let discard = vec![dual_type(CardId::A1001Bulbasaur, EnergyType::Water)];
    let game = game_with(bulbasaur_board(), CardId::A3143FishingNet, vec![], discard, 0);
    assert!(offered_play(&game.get_state_clone(), CardId::A3143FishingNet).is_some());
}

#[test]
fn fishing_net_is_not_offered_for_a_single_type_grass_basic() {
    let discard = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    let game = game_with(bulbasaur_board(), CardId::A3143FishingNet, vec![], discard, 0);
    assert!(offered_play(&game.get_state_clone(), CardId::A3143FishingNet).is_none());
}

#[test]
fn fishing_net_retrieves_a_basic_whose_second_type_is_water() {
    let discard = vec![dual_type(CardId::A1001Bulbasaur, EnergyType::Water)];
    let mut game = game_with(bulbasaur_board(), CardId::A3143FishingNet, vec![], discard, 0);
    play_directly(&mut game, CardId::A3143FishingNet);
    let state = game.get_state_clone();
    assert_eq!(count_named(&state.hands[0], "Bulbasaur"), 1);
    assert_eq!(count_named(&state.discard_piles[0], "Bulbasaur"), 0);
}

#[test]
fn fishing_net_leaves_a_single_type_grass_basic() {
    let discard = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    let mut game = game_with(bulbasaur_board(), CardId::A3143FishingNet, vec![], discard, 0);
    play_directly(&mut game, CardId::A3143FishingNet);
    let state = game.get_state_clone();
    assert_eq!(count_named(&state.hands[0], "Bulbasaur"), 0);
    assert_eq!(count_named(&state.discard_piles[0], "Bulbasaur"), 1);
}

// --- Fisher (A4 159): "Flip 3 coins. For each heads, a [W] Pokémon is chosen at random from your
// discard pile and put into your hand." Legality: move_generation_trainer.rs `can_play_fisher`;
// effect: apply_trainer_action.rs `is_water_pokemon`. Ivysaur (Stage 1) shows any stage counts.

#[test]
fn fisher_is_offered_for_a_pokemon_whose_second_type_is_water() {
    let discard = vec![dual_type(CardId::A1002Ivysaur, EnergyType::Water)];
    let game = game_with(bulbasaur_board(), CardId::A4159Fisher, vec![], discard, 0);
    assert!(offered_play(&game.get_state_clone(), CardId::A4159Fisher).is_some());
}

#[test]
fn fisher_is_not_offered_for_a_single_type_grass_pokemon() {
    let discard = vec![get_card_by_enum(CardId::A1002Ivysaur)];
    let game = game_with(bulbasaur_board(), CardId::A4159Fisher, vec![], discard, 0);
    assert!(offered_play(&game.get_state_clone(), CardId::A4159Fisher).is_none());
}

#[test]
fn fisher_retrieves_a_pokemon_whose_second_type_is_water() {
    let mut retrieved_somewhere = false;
    for seed in 0..16u64 {
        let discard = vec![dual_type(CardId::A1002Ivysaur, EnergyType::Water)];
        let mut game = game_with(bulbasaur_board(), CardId::A4159Fisher, vec![], discard, seed);
        play_directly(&mut game, CardId::A4159Fisher);
        let state = game.get_state_clone();
        let retrieved = count_named(&state.hands[0], "Ivysaur");
        assert_eq!(
            retrieved + count_named(&state.discard_piles[0], "Ivysaur"),
            1,
            "seed {seed}: the one Ivysaur is in the hand or the discard pile"
        );
        retrieved_somewhere |= retrieved == 1;
    }
    assert!(retrieved_somewhere, "some seed flips heads and retrieves the [G]/[W] Ivysaur");
}

#[test]
fn fisher_never_retrieves_a_single_type_grass_pokemon() {
    for seed in 0..16u64 {
        let discard = vec![get_card_by_enum(CardId::A1002Ivysaur)];
        let mut game = game_with(bulbasaur_board(), CardId::A4159Fisher, vec![], discard, seed);
        play_directly(&mut game, CardId::A4159Fisher);
        let state = game.get_state_clone();
        assert_eq!(count_named(&state.hands[0], "Ivysaur"), 0, "seed {seed}");
        assert_eq!(count_named(&state.discard_piles[0], "Ivysaur"), 1, "seed {seed}");
    }
}

// --- Mythical Slab (A1a 065): "Look at the top card of your deck. If that card is a [P] Pokémon,
// put it into your hand. If it is not a [P] Pokémon, put it on the bottom of your deck."
// apply_trainer_action.rs `mythical_slab_effect`.

#[test]
fn mythical_slab_keeps_a_top_card_whose_second_type_is_psychic() {
    let dual = dual_type(CardId::A1001Bulbasaur, EnergyType::Psychic);
    let charmander = get_card_by_enum(CardId::A1033Charmander);
    let deck = vec![dual.clone(), charmander.clone()];
    let mut game = game_with(bulbasaur_board(), CardId::A1a065MythicalSlab, deck, vec![], 0);
    play_offered(&mut game, CardId::A1a065MythicalSlab);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![dual]);
    assert_eq!(state.decks[0].cards, vec![charmander]);
}

#[test]
fn mythical_slab_bottoms_a_single_type_grass_top_card() {
    let bulbasaur = get_card_by_enum(CardId::A1001Bulbasaur);
    let charmander = get_card_by_enum(CardId::A1033Charmander);
    let deck = vec![bulbasaur.clone(), charmander.clone()];
    let mut game = game_with(bulbasaur_board(), CardId::A1a065MythicalSlab, deck, vec![], 0);
    play_offered(&mut game, CardId::A1a065MythicalSlab);
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.decks[0].cards, vec![charmander, bulbasaur]);
}

// --- Deck search by type, shared_mutations.rs `pokemon_search_outcomes_by_type_for_player`, here
// through Fragrant Forest (B3 153): "Once during each player's turn, that player may put a random
// Basic [G] Pokémon from their deck into their hand." (The same function serves a typed search
// attack and the StartTurnRandomPokemonToHand Ability.)

/// Fragrant Forest in play, `deck` as player 0's deck, and player 0 uses it.
fn use_fragrant_forest(deck: Vec<Card>) -> State {
    let forest = CardId::B3153FragrantForest;
    let mut game = game_with(bulbasaur_board(), forest, deck, vec![], 0);
    let mut state = game.get_state_clone();
    state.hands[0].clear();
    state.set_active_stadium(get_card_by_enum(forest));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseStadium,
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn deck_search_by_type_finds_a_basic_whose_second_type_is_grass() {
    let state = use_fragrant_forest(vec![dual_type(CardId::A1033Charmander, EnergyType::Grass)]);
    assert_eq!(count_named(&state.hands[0], "Charmander"), 1);
    assert!(state.decks[0].cards.is_empty());
}

#[test]
fn deck_search_by_type_skips_a_single_type_fire_basic() {
    let state = use_fragrant_forest(vec![get_card_by_enum(CardId::A1033Charmander)]);
    assert_eq!(count_named(&state.hands[0], "Charmander"), 0);
    assert_eq!(count_named(&state.decks[0].cards, "Charmander"), 1);
}

// --- Typed evolution from the deck: apply_trainer_action.rs `random_typed_evolution_outcomes`
// (the forecast filter and the re-check in its mutation), through Quick-Grow Extract (B1a 067:
// "Choose 1 of your [G] Pokémon in play. Put a random [G] Pokémon from your deck that evolves from
// that Pokémon onto that Pokémon to evolve it.") and Wallace (B3b 068: the same for a [W] Pokémon
// with a maximum HP of 50 or less). Grubbin ([G]) evolves into Charjabug ([L]); Ducklett ([W], 50
// HP) into Swanna ex ([C], B4 141).

/// Plays `trainer`, picks its one offered evolution target and returns the state after it.
fn evolve_with(mut game: Game<'static>, trainer: CardId) -> State {
    play_offered(&mut game, trainer);
    let choices: Vec<Action> = game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .filter(|action| {
            matches!(
                action.action,
                SimpleAction::ChooseRandomEvolutionTarget { in_play_idx: 0, .. }
            )
        })
        .collect();
    assert_eq!(choices.len(), 1, "the Active is the one target");
    game.apply_action(&choices[0]);
    game.get_state_clone()
}

fn grubbin_with_deck(deck: Vec<Card>) -> Game<'static> {
    let board = vec![PlayedCard::from_id(CardId::A3013Grubbin)];
    game_with(board, CardId::B1a067QuickGrowExtract, deck, vec![], 0)
}

fn ducklett_with_deck(deck: Vec<Card>) -> Game<'static> {
    let board = vec![PlayedCard::from_id(CardId::A1085Ducklett)];
    game_with(board, CardId::B3b068Wallace, deck, vec![], 0)
}

#[test]
fn quick_grow_extract_evolves_into_a_card_whose_second_type_is_grass() {
    let deck = vec![dual_type(CardId::A3064Charjabug, EnergyType::Grass)];
    let state = evolve_with(grubbin_with_deck(deck), CardId::B1a067QuickGrowExtract);
    assert_eq!(state.get_active(0).get_name(), "Charjabug");
    assert!(state.decks[0].cards.is_empty());
}

#[test]
fn quick_grow_extract_skips_a_single_type_lightning_evolution() {
    let deck = vec![get_card_by_enum(CardId::A3064Charjabug)];
    let state = evolve_with(grubbin_with_deck(deck), CardId::B1a067QuickGrowExtract);
    assert_eq!(state.get_active(0).get_name(), "Grubbin");
    assert_eq!(count_named(&state.decks[0].cards, "Charjabug"), 1);
}

#[test]
fn wallace_evolves_into_a_card_whose_second_type_is_water() {
    let deck = vec![dual_type(CardId::B4141SwannaEx, EnergyType::Water)];
    let state = evolve_with(ducklett_with_deck(deck), CardId::B3b068Wallace);
    assert_eq!(state.get_active(0).get_name(), "Swanna ex");
    assert!(state.decks[0].cards.is_empty());
}

#[test]
fn wallace_skips_a_single_type_colorless_evolution() {
    let deck = vec![get_card_by_enum(CardId::B4141SwannaEx)];
    let state = evolve_with(ducklett_with_deck(deck), CardId::B3b068Wallace);
    assert_eq!(state.get_active(0).get_name(), "Ducklett");
    assert_eq!(count_named(&state.decks[0].cards, "Swanna ex"), 1);
}

// --- The public candidate lists, card_logic/quick_grow_extract.rs and card_logic/wallace.rs (no
// engine caller today; part of the library's API).

#[test]
fn quick_grow_extract_candidates_include_a_card_whose_second_type_is_grass() {
    let dual = dual_type(CardId::A3064Charjabug, EnergyType::Grass);
    let state = grubbin_with_deck(vec![dual.clone()]).get_state_clone();
    assert_eq!(quick_grow_extract_candidates(&state, 0), vec![(0, dual)]);
}

#[test]
fn quick_grow_extract_candidates_skip_a_single_type_lightning_evolution() {
    let deck = vec![get_card_by_enum(CardId::A3064Charjabug)];
    let state = grubbin_with_deck(deck).get_state_clone();
    assert!(quick_grow_extract_candidates(&state, 0).is_empty());
}

#[test]
fn wallace_candidates_include_a_card_whose_second_type_is_water() {
    let dual = dual_type(CardId::B4141SwannaEx, EnergyType::Water);
    let state = ducklett_with_deck(vec![dual.clone()]).get_state_clone();
    assert_eq!(wallace_candidates(&state, 0), vec![(0, dual)]);
}

#[test]
fn wallace_candidates_skip_a_single_type_colorless_evolution() {
    let deck = vec![get_card_by_enum(CardId::B4141SwannaEx)];
    let state = ducklett_with_deck(deck).get_state_clone();
    assert!(wallace_candidates(&state, 0).is_empty());
}
