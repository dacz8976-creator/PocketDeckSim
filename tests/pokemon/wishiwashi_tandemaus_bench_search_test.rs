use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};

/// Runs `card_id`'s first attack with a deck stacked to exactly `deck`, and `own_bench` already in
/// play alongside the attacker.
fn call_from_deck(
    seed: u64,
    card_id: CardId,
    energy: Vec<EnergyType>,
    own_bench: Vec<CardId>,
    deck: Vec<CardId>,
) -> State {
    let mut own_board = vec![PlayedCard::from_id(card_id).with_energy(energy)];
    own_board.extend(own_bench.into_iter().map(PlayedCard::from_id));

    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        own_board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards = deck.into_iter().map(get_card_by_enum).collect();
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

fn bench_names(state: &State) -> Vec<String> {
    (1..4)
        .filter_map(|idx| {
            state.in_play_pokemon[0][idx]
                .as_ref()
                .map(|pokemon| pokemon.get_name())
        })
        .collect()
}

fn deck_names(state: &State) -> Vec<String> {
    state.decks[0].cards.iter().map(Card::get_name).collect()
}

// =================================================================================================
// Wishiwashi (A3 050 / A4b 122 / A4b 123) "Call for Family": "Put 1 random Wishiwashi or Wishiwashi
// ex from your deck onto your Bench."
// =================================================================================================

#[test]
fn test_call_for_family_benches_one_wishiwashi_from_the_deck() {
    let mut saw_plain = false;
    let mut saw_ex = false;

    for seed in 0..20 {
        let state = call_from_deck(
            seed,
            CardId::A3050Wishiwashi,
            vec![EnergyType::Water],
            vec![],
            vec![
                CardId::A3050Wishiwashi,
                CardId::A3051WishiwashiEx,
                CardId::A1001Bulbasaur,
            ],
        );

        let bench = bench_names(&state);
        assert_eq!(
            bench.len(),
            1,
            "seed {seed}: exactly one card should be benched"
        );
        match bench[0].as_str() {
            "Wishiwashi" => saw_plain = true,
            "Wishiwashi ex" => saw_ex = true,
            other => panic!("seed {seed}: unexpected benched Pokémon {other}"),
        }
        assert_eq!(
            deck_names(&state).len(),
            2,
            "seed {seed}: the benched card should have left the deck"
        );
        assert!(
            !deck_names(&state).contains(&bench[0]),
            "seed {seed}: the benched card should no longer be in the deck"
        );
    }

    assert!(
        saw_plain && saw_ex,
        "both Wishiwashi and Wishiwashi ex should be reachable"
    );
}

/// Negative case: with no Wishiwashi in the deck, nothing is put onto the Bench.
#[test]
fn test_call_for_family_does_nothing_without_a_wishiwashi_in_the_deck() {
    let state = call_from_deck(
        0,
        CardId::A4b122Wishiwashi,
        vec![EnergyType::Water],
        vec![],
        vec![CardId::A1001Bulbasaur, CardId::A1033Charmander],
    );

    assert!(bench_names(&state).is_empty());
    assert_eq!(deck_names(&state).len(), 2, "the deck should be untouched");
}

/// The name filter is exact: a Pokémon that merely evolves from Wishiwashi-adjacent lines does not
/// count.
#[test]
fn test_call_for_family_ignores_other_pokemon() {
    let state = call_from_deck(
        0,
        CardId::A4b123Wishiwashi,
        vec![EnergyType::Water],
        vec![],
        vec![CardId::A1053Squirtle, CardId::A3051WishiwashiEx],
    );

    assert_eq!(bench_names(&state), vec!["Wishiwashi ex".to_string()]);
}

// =================================================================================================
// Tandemaus (B2 142) "Flock": "Put 3 random cards from among Tandemaus and Maushold from your deck
// onto your Bench."
// =================================================================================================

#[test]
fn test_flock_benches_three_cards_from_the_deck() {
    let state = call_from_deck(
        0,
        CardId::B2142Tandemaus,
        vec![EnergyType::Colorless],
        vec![],
        vec![
            CardId::B2142Tandemaus,
            CardId::B2142Tandemaus,
            CardId::B2143Maushold,
            CardId::A1001Bulbasaur,
        ],
    );

    let bench = bench_names(&state);
    assert_eq!(bench.len(), 3, "all three Bench slots should be filled");
    assert!(bench
        .iter()
        .all(|name| name == "Tandemaus" || name == "Maushold"));
    assert_eq!(
        deck_names(&state),
        vec!["Bulbasaur".to_string()],
        "only the three benched cards should have left the deck"
    );
}

/// Only as many as there is room for: with one Bench slot already taken, Flock benches 2.
#[test]
fn test_flock_stops_when_the_bench_fills_up() {
    let state = call_from_deck(
        0,
        CardId::B2142Tandemaus,
        vec![EnergyType::Colorless],
        vec![CardId::A1001Bulbasaur],
        vec![
            CardId::B2142Tandemaus,
            CardId::B2142Tandemaus,
            CardId::B2143Maushold,
        ],
    );

    let bench = bench_names(&state);
    assert_eq!(bench.len(), 3, "the Bench holds 3 Pokémon in total");
    assert_eq!(
        bench.iter().filter(|name| *name == "Bulbasaur").count(),
        1,
        "the Pokémon that was already benched should stay"
    );
}

/// Fewer copies in the deck than the attack asks for: it takes what it can.
#[test]
fn test_flock_takes_fewer_when_the_deck_holds_fewer() {
    let state = call_from_deck(
        0,
        CardId::B2142Tandemaus,
        vec![EnergyType::Colorless],
        vec![],
        vec![CardId::B2143Maushold, CardId::A1001Bulbasaur],
    );

    assert_eq!(bench_names(&state), vec!["Maushold".to_string()]);
}
