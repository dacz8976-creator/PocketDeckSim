use super::*;

#[test]
fn serenas_choice_offers_each_distinct_top_three_card_and_preserves_the_others() {
    for supporter in [CardId::C1127SerenasChoice, CardId::C1167SerenasChoice] {
        for pick in [
            CardId::PA001Potion,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
        ] {
            let mut g = board(vec![pokemon("A1 001")]);
            let mut s = g.get_state_clone();
            let cards = vec![
                get_card_by_enum(CardId::PA001Potion),
                get_card_by_enum(CardId::A1001Bulbasaur),
                get_card_by_enum(CardId::A1033Charmander),
                get_card_by_enum(CardId::PA005PokeBall),
            ];
            s.decks[0].cards = cards.clone();
            g.set_state(s);
            play(&mut g, supporter);
            let (actor, actions) = g.get_state_clone().generate_possible_actions();
            assert_eq!(actor, 0);
            assert_eq!(actions.len(), 3);
            let chosen = get_card_by_enum(pick);
            let choice = actions
                .into_iter()
                .find(|a| matches!(&a.action, SimpleAction::TakeTopDeckCardAndShuffle { card, .. } if *card == chosen))
                .expect("Player chooses a top-three card");
            g.apply_action(&choice);
            let s = g.get_state_clone();
            assert_eq!(s.hands[0], vec![chosen.clone()]);
            assert_eq!(s.decks[0].cards.len(), 3);
            for card in cards {
                assert_eq!(s.decks[0].cards.contains(&card), card != chosen);
            }
            assert!(!offered(&mut g, CardId::C1125Lorelei));
        }
    }
}
#[test]
fn serenas_choice_handles_short_decks_and_duplicate_cards() {
    // Ours (rules/04 [DUSTIN]): blocked by an empty deck. Upstream plays it on an empty deck.
    let mut g = board(vec![pokemon("A1 001")]);
    let mut s = g.get_state_clone();
    s.decks[0].cards.clear();
    g.set_state(s);
    assert!(!offered(&mut g, CardId::C1127SerenasChoice));
    for count in 1..=2 {
        let mut g = board(vec![pokemon("A1 001")]);
        let mut s = g.get_state_clone();
        s.decks[0].cards = vec![get_card_by_enum(CardId::PA001Potion); count];
        g.set_state(s);
        play(&mut g, CardId::C1127SerenasChoice);
        let (_, a) = g.get_state_clone().generate_possible_actions();
        assert_eq!(a.len(), 1);
        g.apply_action(&a[0]);
        let s = g.get_state_clone();
        assert_eq!(s.hands[0].len(), 1);
        assert_eq!(s.decks[0].cards.len(), count - 1);
    }
}

#[test]
fn serenas_choice_shuffles_the_remaining_deck_after_the_player_picks() {
    let mut orders = std::collections::HashSet::new();
    for seed in 0..30 {
        let mut g = deckgym::test_support::get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![pokemon("A1 001")],
            vec![pokemon("A1 211")],
        );
        let mut s = g.get_state_clone();
        s.decks[0].cards = [
            CardId::PA001Potion,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
            CardId::PA005PokeBall,
        ]
        .into_iter()
        .map(get_card_by_enum)
        .collect();
        g.set_state(s);
        play(&mut g, CardId::C1127SerenasChoice);
        let (_, a) = g.get_state_clone().generate_possible_actions();
        let a = a
            .into_iter()
            .find(|a| matches!(&a.action, SimpleAction::TakeTopDeckCardAndShuffle { card, .. } if card.get_id() == "P-A 001"))
            .unwrap();
        g.apply_action(&a);
        let s = g.get_state_clone();
        assert_eq!(s.hands[0], vec![get_card_by_enum(CardId::PA001Potion)]);
        orders.insert(
            s.decks[0]
                .cards
                .iter()
                .map(|c| c.get_id())
                .collect::<Vec<_>>(),
        );
    }
    assert!(orders.len() > 1);
}

/// Ours only (J4): with 10 cards in hand after playing it, the chosen card stays in the deck, as
/// with a draw (rules/README item 11, rules/09); the deck is still shuffled.
#[test]
fn serenas_choice_leaves_the_card_in_the_deck_when_the_hand_is_full() {
    let mut g = board(vec![pokemon("A1 001")]);
    let mut s = g.get_state_clone();
    s.hands[0] = std::iter::once(get_card_by_enum(CardId::C1127SerenasChoice))
        .chain(std::iter::repeat(get_card_by_enum(CardId::PA001Potion)).take(10))
        .collect();
    s.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander); 4];
    g.set_state(s);
    play_from_hand(&mut g, CardId::C1127SerenasChoice);
    let (_, a) = g.get_state_clone().generate_possible_actions();
    assert_eq!(a.len(), 1);
    g.apply_action(&a[0]);
    let s = g.get_state_clone();
    assert_eq!(s.hands[0].len(), 10);
    assert_eq!(s.decks[0].cards.len(), 4);
}
