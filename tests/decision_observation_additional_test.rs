use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::Card,
    observation::{PlayerObservation, RevealedKnowledge},
    players::{EndTurnPlayer, Player},
    test_support::load_test_decks,
    Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

fn players(state: &State) -> Vec<Box<dyn Player>> {
    vec![
        Box::new(EndTurnPlayer { deck: state.decks[0].clone() }),
        Box::new(EndTurnPlayer { deck: state.decks[1].clone() }),
    ]
}

fn play_trainer(actor: usize, card: Card) -> Action {
    let Card::Trainer(trainer_card) = card else { panic!("expected trainer card") };
    Action { actor, action: SimpleAction::Play { trainer_card }, is_stack: false }
}

#[test]
fn default_observation_redacts_opponent_zones_but_keeps_own_deck_multiset() {
    let (a, b) = load_test_decks();
    let mut state = State::new(&a, &b);
    state.hands[0] = vec![get_card_by_enum(CardId::PA006RedCard)];
    state.hands[1] = b.cards[..4].to_vec();

    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let visible = observation.visible_state();
    assert_eq!(visible.hands[0], state.hands[0]);
    assert_eq!(visible.hands[1].len(), state.hands[1].len());
    assert!(visible.hands[1].iter().all(|card| *card == Card::Unknown));
    assert_eq!(visible.decks[1].cards.len(), state.decks[1].cards.len());
    assert!(visible.decks[1].cards.iter().all(|card| *card == Card::Unknown));
    assert!(visible.decks[0].cards.is_empty(), "own deck ordering is supplied by search_state");

    let mut search_state = observation.search_state(&mut StdRng::seed_from_u64(7));
    let mut expected = state.decks[0].cards.clone();
    let mut actual = std::mem::take(&mut search_state.decks[0].cards);
    expected.sort_by_key(Card::get_id);
    actual.sort_by_key(Card::get_id);
    assert_eq!(actual, expected, "search gets the own deck as an unordered multiset");
    assert!(search_state.decks[1].cards.iter().all(|card| *card == Card::Unknown));
}

#[test]
fn pending_private_choice_is_cleared_for_non_chooser_and_reveal_is_limited_to_chooser() {
    let (a, b) = load_test_decks();
    let mut state = State::new(&a, &b);
    let revealed_card = a.cards[0].clone();
    state.hands[0] = a.cards[..2].to_vec();
    state.hands[1] = b.cards[..3].to_vec();
    let pending = SimpleAction::ShuffleOpponentHandCard { card: revealed_card.clone() };
    state.move_generation_stack = vec![(1, vec![pending.clone()])];

    let observer_zero = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    assert!(observer_zero.visible_state().move_generation_stack[0].1.is_empty());
    assert!(observer_zero.visible_state().hands[1].iter().all(|card| *card == Card::Unknown));

    let observer_one = PlayerObservation::from_state(&state, 1, &RevealedKnowledge::default());
    assert_eq!(observer_one.visible_state().move_generation_stack[0].1, vec![pending]);
    let visible_hand = &observer_one.visible_state().hands[0];
    assert!(visible_hand.contains(&revealed_card));
    assert_eq!(visible_hand.iter().filter(|card| **card != Card::Unknown).count(), 1);
}

#[test]
fn hand_scope_reveals_only_to_actor_and_pokedex_knowledge_clears_after_shuffle() {
    let (a, b) = load_test_decks();

    let mut hand_state = State::new(&a, &b);
    hand_state.hands[0] = vec![get_card_by_enum(CardId::PA003HandScope)];
    hand_state.hands[1] = b.cards[..3].to_vec();
    let mut expected_hand = hand_state.hands[1].clone();
    expected_hand.sort_by_key(Card::get_id);
    let mut hand_game = Game::from_state(hand_state, players(&State::new(&a, &b)), 11);
    hand_game.apply_action(&play_trainer(0, get_card_by_enum(CardId::PA003HandScope)));

    let actor_view = hand_game.observation(0);
    assert_eq!(actor_view.visible_state().hands[1], expected_hand);
    assert_eq!(actor_view.revealed.opponent_hand, expected_hand);
    let other_view = hand_game.observation(1);
    assert!(other_view.visible_state().hands[0].iter().all(|card| *card == Card::Unknown));
    assert!(other_view.revealed.opponent_hand.is_empty());

    let mut deck_state = State::new(&a, &b);
    deck_state.hands[0] = vec![
        get_card_by_enum(CardId::PA004PokedEx),
        get_card_by_enum(CardId::PA006RedCard),
    ];
    let mut deck_game = Game::from_state(deck_state.clone(), players(&deck_state), 12);
    let original_top = deck_state.decks[0].cards[..3].to_vec();
    deck_game.apply_action(&play_trainer(0, get_card_by_enum(CardId::PA004PokedEx)));
    assert_eq!(deck_game.observation(0).revealed.deck_top[0], original_top);

    deck_game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ShuffleOwnCardsIntoDeck { cards: vec![get_card_by_enum(CardId::PA006RedCard)] },
        is_stack: false,
    });
    assert!(deck_game.observation(0).revealed.deck_top[0].is_empty(),
        "an ambiguous shuffle must invalidate previously known top cards");
}

