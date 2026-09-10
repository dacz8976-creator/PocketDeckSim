use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

/// Galarian Meowth active with Galarian Perrserker (B2 111) in hand, and player 0's discard pile
/// seeded with `own_discard`.
fn game_ready_to_evolve(own_discard: Vec<CardId>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2110GalarianMeowth)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.hands[0].clear();
    state.hands[0].push(get_card_by_enum(CardId::B2111GalarianPerrserker));
    state.discard_piles[0] = own_discard.into_iter().map(get_card_by_enum).collect();
    game.set_state(state);
    game
}

fn evolve_into_perrserker(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Evolve {
            evolution: get_card_by_enum(CardId::B2111GalarianPerrserker),
            in_play_idx: 0,
            from_deck: false,
        },
        is_stack: false,
    });
}

fn dig_up_action(actions: &[Action]) -> Option<Action> {
    actions
        .iter()
        .find(|action| {
            matches!(
                action.action,
                SimpleAction::PutRandomCardsFromDiscardToHand { .. }
            )
        })
        .cloned()
}

fn count_in(cards: &[Card], card: &Card) -> usize {
    cards.iter().filter(|c| *c == card).count()
}

/// Dig Up: "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your
/// Pokémon, you may put 2 random Pokémon Tool cards from your discard pile into your hand."
#[test]
fn test_dig_up_puts_two_tools_from_the_discard_into_hand() {
    let poke_ball = get_card_by_enum(CardId::PA005PokeBall);
    let mut game = game_ready_to_evolve(vec![
        CardId::A2147GiantCape,
        CardId::A2148RockyHelmet,
        CardId::A3146PoisonBarb,
        CardId::PA005PokeBall,
    ]);

    evolve_into_perrserker(&mut game);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Noop)),
        "Dig Up says 'you may', so declining must be an option"
    );
    let dig_up = dig_up_action(&choices).expect("Dig Up should be offered");

    let hand_before = game.get_state_clone().hands[0].len();
    let discard_before = game.get_state_clone().discard_piles[0].len();
    game.apply_action(&dig_up);

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[0].len(),
        hand_before + 2,
        "exactly 2 cards should move from the discard pile to the hand"
    );
    assert_eq!(
        state.discard_piles[0].len(),
        discard_before - 2,
        "the same 2 cards should have left the discard pile"
    );
    assert!(
        state.hands[0].iter().all(
            |card| matches!(card, Card::Trainer(t) if t.trainer_card_type
                == deckgym::models::TrainerType::Tool)
        ),
        "only Pokémon Tool cards may be picked up"
    );
    assert_eq!(
        count_in(&state.discard_piles[0], &poke_ball),
        1,
        "the Item card must stay in the discard pile"
    );
}

/// Fewer Tools than asked for: "2 random Pokémon Tool cards" degrades to whatever is available.
#[test]
fn test_dig_up_takes_the_only_tool_when_the_discard_has_one() {
    let giant_cape = get_card_by_enum(CardId::A2147GiantCape);
    let mut game = game_ready_to_evolve(vec![
        CardId::A2147GiantCape,
        CardId::PA005PokeBall,
        CardId::A1001Bulbasaur,
    ]);

    evolve_into_perrserker(&mut game);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let dig_up = dig_up_action(&choices).expect("Dig Up should be offered for a single Tool");
    let hand_before = game.get_state_clone().hands[0].len();
    game.apply_action(&dig_up);

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[0].len(),
        hand_before + 1,
        "only the one available Tool should be picked up"
    );
    assert!(state.hands[0].contains(&giant_cape));
    assert!(!state.discard_piles[0].contains(&giant_cape));
}

/// NEGATIVE: no Pokémon Tool in the discard pile, so the player is not asked anything.
#[test]
fn test_dig_up_not_offered_without_a_tool_in_the_discard() {
    let mut game = game_ready_to_evolve(vec![
        CardId::PA005PokeBall,
        CardId::A1219Erika,
        CardId::A1001Bulbasaur,
    ]);

    evolve_into_perrserker(&mut game);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    assert!(
        dig_up_action(&choices).is_none(),
        "Dig Up must not be offered when the discard pile holds no Pokémon Tool"
    );
    assert_eq!(
        game.get_state_clone().get_active(0).get_name(),
        "Galarian Perrserker",
        "the evolution itself should still have happened"
    );
}

/// NEGATIVE: it is an on-evolve trigger, not an activated Ability.
#[test]
fn test_dig_up_does_not_trigger_without_evolving() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2111GalarianPerrserker)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.discard_piles[0] = vec![
        get_card_by_enum(CardId::A2147GiantCape),
        get_card_by_enum(CardId::A2148RockyHelmet),
    ];
    game.set_state(state);

    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    assert!(
        dig_up_action(&choices).is_none(),
        "Dig Up is an on-evolve trigger, not an activated Ability"
    );
}
