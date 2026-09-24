use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

/// Skitty active with Delcatty (B1 194) in hand, and player 0's discard pile seeded with
/// `own_discard` (player 1's with `opponent_discard`).
fn game_ready_to_evolve(own_discard: Vec<CardId>, opponent_discard: Vec<CardId>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B1193Skitty)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.hands[0].clear();
    state.hands[0].push(get_card_by_enum(CardId::B1194Delcatty));
    state.discard_piles[0] = own_discard.into_iter().map(get_card_by_enum).collect();
    state.discard_piles[1] = opponent_discard.into_iter().map(get_card_by_enum).collect();
    game.set_state(state);
    game
}

fn evolve_into_delcatty(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Evolve {
            evolution: get_card_by_enum(CardId::B1194Delcatty),
            in_play_idx: 0,
            from_deck: false,
        },
        is_stack: false,
    });
}

fn retrieved_card(action: &Action) -> Option<&Card> {
    match &action.action {
        SimpleAction::PutCardFromDiscardToHand { card } => Some(card),
        _ => None,
    }
}

/// Search for Friends: "Once during your turn, when you play this Pokémon from your hand to evolve
/// 1 of your Pokémon, you may put a Supporter card from your discard pile into your hand."
#[test]
fn test_search_for_friends_puts_a_supporter_from_the_discard_into_hand() {
    let erika = get_card_by_enum(CardId::A1219Erika);
    let poke_ball = get_card_by_enum(CardId::PA005PokeBall);
    let mut game = game_ready_to_evolve(
        vec![CardId::PA005PokeBall, CardId::A1219Erika],
        vec![CardId::A1225Sabrina],
    );

    evolve_into_delcatty(&mut game);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Noop)),
        "Search for Friends says 'you may', so declining must be an option"
    );
    let take_erika = choices
        .iter()
        .find(|choice| retrieved_card(choice) == Some(&erika))
        .expect("Erika should be offered from the discard pile")
        .clone();
    assert!(
        choices
            .iter()
            .all(|choice| retrieved_card(choice).is_none_or(|card| card == &erika)),
        "only Supporter cards are eligible, so the Item in the discard must not be offered"
    );

    game.apply_action(&take_erika);

    let state = game.get_state_clone();
    assert!(
        state.hands[0].contains(&erika),
        "the chosen Supporter should be in hand"
    );
    assert!(
        !state.discard_piles[0].contains(&erika),
        "the chosen Supporter should have left the discard pile"
    );
    assert!(
        state.discard_piles[0].contains(&poke_ball),
        "non-Supporter cards must stay in the discard pile"
    );
}

/// Every Supporter in the discard pile is a candidate — the player picks which one.
#[test]
fn test_search_for_friends_offers_every_supporter_in_the_discard() {
    let erika = get_card_by_enum(CardId::A1219Erika);
    let sabrina = get_card_by_enum(CardId::A1225Sabrina);
    let mut game = game_ready_to_evolve(
        vec![
            CardId::A1219Erika,
            CardId::A1225Sabrina,
            CardId::PA005PokeBall,
        ],
        vec![],
    );

    evolve_into_delcatty(&mut game);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let offered: Vec<&Card> = choices.iter().filter_map(retrieved_card).collect();
    assert!(offered.contains(&&erika), "Erika should be offered");
    assert!(offered.contains(&&sabrina), "Sabrina should be offered");
    assert_eq!(
        offered.len(),
        2,
        "exactly the two Supporters in the discard pile should be offered"
    );
}

/// NEGATIVE: no Supporter in the discard pile, so the Ability has nothing to fetch and the evolve
/// resolves without asking the player anything.
#[test]
fn test_search_for_friends_not_offered_without_a_supporter_in_the_discard() {
    let mut game = game_ready_to_evolve(
        vec![CardId::PA005PokeBall, CardId::A1001Bulbasaur],
        // A Supporter in the *opponent's* discard pile is not "your discard pile".
        vec![CardId::A1219Erika],
    );

    evolve_into_delcatty(&mut game);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|choice| retrieved_card(choice).is_none()),
        "Search for Friends must not offer anything when your discard pile holds no Supporter"
    );
    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_name(),
        "Delcatty",
        "the evolution itself should still have happened"
    );
}

/// NEGATIVE: the Ability triggers on evolving *from hand* only, so a Delcatty put into play any
/// other way (here: already in play at the start of the turn) never offers the search.
#[test]
fn test_search_for_friends_does_not_trigger_without_evolving() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B1194Delcatty)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.discard_piles[0] = vec![get_card_by_enum(CardId::A1219Erika)];
    game.set_state(state);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|choice| retrieved_card(choice).is_none()),
        "Search for Friends is an on-evolve trigger, not an activated Ability"
    );
}
