use std::collections::BTreeMap;

use deckgym::{
    actions::{
        try_forecast_action, Action, CoinPaths, SimpleAction, UnpricedForecastKind,
    },
    card_ids::CardId,
    card_validation::{get_implementation_status, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, PlayedCard, TrainerCard},
    test_support::get_initialized_game,
    Game,
};
use rand::{rngs::StdRng, SeedableRng};

fn trainer(id: CardId) -> TrainerCard {
    get_card_by_enum(id).as_trainer()
}

fn action(id: CardId) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: trainer(id),
        },
        is_stack: false,
    }
}

fn setup(seed: u64) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

fn magmar() -> Card {
    get_card_by_enum(CardId::B4a006TeamRocketsMagmar)
}

fn lapras() -> Card {
    get_card_by_enum(CardId::B4a013TeamRocketsLapras)
}

#[test]
fn both_printings_are_legal_and_explicitly_rules_unverified() {
    for id in [
        CardId::B4a069TeamRocketsResearcher,
        CardId::B4a085TeamRocketsResearcher,
    ] {
        let mut game = setup(1);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(id)];
        game.set_state(state);
        assert!(game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|candidate| {
                matches!(&candidate.action, SimpleAction::Play { trainer_card }
                    if trainer_card.id == get_card_by_enum(id).get_id())
            }));
        assert_eq!(get_implementation_status(id), ImplementationStatus::RulesUnverified);
    }
}

#[test]
fn exact_forecast_merges_identical_copies_with_physical_weights() {
    let mut game = setup(2);
    let mut state = game.get_state_clone();
    let researcher = get_card_by_enum(CardId::B4a069TeamRocketsResearcher);
    state.hands[0] = vec![researcher];
    state.decks[0].cards = vec![
        magmar(),
        magmar(),
        lapras(),
        get_card_by_enum(CardId::A1001Bulbasaur),
    ];
    game.set_state(state.clone());
    let play = action(CardId::B4a069TeamRocketsResearcher);
    let branches = try_forecast_action(&state, &play)
        .expect("three eligible cards are priceable")
        .into_branches_with_coin_paths();
    assert_eq!(branches.len(), 6);

    let mut by_counts: BTreeMap<(usize, usize), f64> = BTreeMap::new();
    for (probability, mutation, _coin_paths) in branches {
        let mut next = state.clone();
        mutation(&mut StdRng::seed_from_u64(7), &mut next, &play);
        let counts = (
            next.hands[0].iter().filter(|card| **card == magmar()).count(),
            next.hands[0].iter().filter(|card| **card == lapras()).count(),
        );
        *by_counts.entry(counts).or_default() += probability;
    }
    let expected = [
        ((0, 0), 1.0 / 2.0),
        ((1, 0), 1.0 / 6.0),
        ((0, 1), 1.0 / 12.0),
        ((2, 0), 1.0 / 24.0),
        ((1, 1), 1.0 / 12.0),
        ((2, 1), 1.0 / 8.0),
    ];
    for (key, probability) in expected {
        assert!((by_counts[&key] - probability).abs() < 1e-12, "{key:?}");
    }
}

#[test]
fn actual_and_exact_full_selection_append_the_same_canonical_hand_order() {
    let game = setup(15);
    let mut state = game.get_state_clone();
    let prefix = get_card_by_enum(CardId::A1001Bulbasaur);
    state.hands[0] = vec![
        prefix.clone(),
        get_card_by_enum(CardId::B4a069TeamRocketsResearcher),
    ];
    // Reverse the eligible cards relative to their stable CardId order. This catches accidental
    // dependence on physical deck index in actual resolution.
    let mut canonical = vec![magmar(), lapras()];
    canonical.sort_by_key(Card::get_id);
    state.decks[0].cards = canonical.iter().cloned().rev().collect();
    let play = action(CardId::B4a069TeamRocketsResearcher);

    let (_, exact_mutation, _) = try_forecast_action(&state, &play)
        .unwrap()
        .into_branches_with_coin_paths()
        .into_iter()
        .find(|(_, _, paths)| matches!(paths, CoinPaths::UntilTailsAtLeast { min_heads: 2 }))
        .expect("full-selection exact branch");
    let mut exact = state.clone();
    exact_mutation(&mut StdRng::seed_from_u64(1), &mut exact, &play);

    let actual_hand = (0..256)
        .find_map(|seed| {
            let mut attempt = setup(seed);
            let mut actual_start = attempt.get_state_clone();
            actual_start.hands[0] = vec![
                prefix.clone(),
                get_card_by_enum(CardId::B4a069TeamRocketsResearcher),
            ];
            actual_start.decks[0].cards = canonical.iter().cloned().rev().collect();
            attempt.set_state(actual_start);
            attempt.apply_action(&play);
            let hand = attempt.get_state_clone().hands[0].clone();
            (hand.len() == 3).then_some(hand)
        })
        .expect("a full-selection actual sample");

    assert_eq!(actual_hand, exact.hands[0]);
    assert_eq!(actual_hand[0], prefix);
    assert_eq!(&actual_hand[1..], canonical.as_slice());
}

#[test]
fn symbolic_terminal_branch_can_exceed_the_inherited_hand_limit() {
    let game = setup(3);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur); 9];
    state.hands[0].push(get_card_by_enum(CardId::B4a069TeamRocketsResearcher));
    state.decks[0].cards = vec![magmar(), lapras()];
    let play = action(CardId::B4a069TeamRocketsResearcher);
    let terminal = try_forecast_action(&state, &play)
        .unwrap()
        .into_branches_with_coin_paths()
        .into_iter()
        .find(|(_, _, paths)| matches!(paths, CoinPaths::UntilTailsAtLeast { min_heads: 2 }))
        .expect("K=2 terminal branch");
    let mut next = state;
    terminal.1(&mut StdRng::seed_from_u64(8), &mut next, &play);
    assert_eq!(next.hands[0].len(), 11);
    assert!(next.decks[0].cards.is_empty());
}

#[test]
fn actual_resolution_moves_only_eligible_physical_cards_and_conserves_them() {
    for seed in 0..40 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::B4a085TeamRocketsResearcher)];
        state.decks[0].cards = vec![
            magmar(),
            magmar(),
            lapras(),
            get_card_by_enum(CardId::A1001Bulbasaur),
        ];
        game.set_state(state);
        game.apply_action(&action(CardId::B4a085TeamRocketsResearcher));
        let state = game.get_state_clone();
        assert!(state.hands[0]
            .iter()
            .all(|card| card == &magmar() || card == &lapras()));
        assert_eq!(state.hands[0].len() + state.decks[0].cards.len(), 4);
        assert_eq!(
            state.hands[0]
                .iter()
                .chain(&state.decks[0].cards)
                .filter(|card| **card == magmar())
                .count(),
            2
        );
        assert!(state.discard_piles[0]
            .iter()
            .any(|card| card.get_name() == "Team Rocket's Researcher"));
    }
}

#[test]
fn will_forces_at_least_one_researcher_pick() {
    for seed in 0..20 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![
            get_card_by_enum(CardId::A4156Will),
            get_card_by_enum(CardId::B4a069TeamRocketsResearcher),
        ];
        state.decks[0].cards = vec![magmar()];
        game.set_state(state);
        game.apply_action(&action(CardId::A4156Will));
        game.apply_action(&action(CardId::B4a069TeamRocketsResearcher));
        assert_eq!(game.get_state_clone().hands[0], vec![magmar()]);
    }
}

fn thirteen_distinct_eligible() -> Vec<Card> {
    [
        CardId::B4a006TeamRocketsMagmar,
        CardId::B4a007TeamRocketsMoltresEx,
        CardId::B4a008TeamRocketsHoundour,
        CardId::B4a009TeamRocketsHoundoom,
        CardId::B4a013TeamRocketsLapras,
        CardId::B4a019TeamRocketsVoltorb,
        CardId::B4a024TeamRocketsPincurchin,
        CardId::B4a025TeamRocketsSlowpoke,
        CardId::B4a027TeamRocketsDrowzee,
        CardId::B4a029TeamRocketsMrMime,
        CardId::B4a030TeamRocketsMewtwo,
        CardId::B4a038TeamRocketsEkans,
        CardId::B4a040TeamRocketsGrimer,
    ]
    .into_iter()
    .map(get_card_by_enum)
    .collect()
}

fn twelve_distinct_eligible() -> Vec<Card> {
    thirteen_distinct_eligible().into_iter().take(12).collect()
}

#[test]
fn oversized_exact_forecast_is_explicit_but_actual_play_still_resolves() {
    let mut game = setup(9);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::B4a069TeamRocketsResearcher)];
    state.decks[0].cards = thirteen_distinct_eligible();
    let play = action(CardId::B4a069TeamRocketsResearcher);
    let error = match try_forecast_action(&state, &play) {
        Err(error) => error,
        Ok(_) => panic!("2^13 exceeds 4096"),
    };
    assert!(matches!(
        error.kind,
        UnpricedForecastKind::ResearcherTooManyExactSuccessors {
            required_at_least: 4097,
            limit: 4096
        }
    ));
    game.set_state(state);
    game.apply_action(&play);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0].len() + state.decks[0].cards.len(), 13);
}

#[test]
fn copied_researcher_uses_copiers_deck_and_keeps_source_card() {
    let mut game = setup(10);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::A4156Will),
        get_card_by_enum(CardId::A3b069Penny),
    ];
    state.decks[0].cards = vec![magmar()];
    state.decks[1].cards = vec![get_card_by_enum(CardId::B4a085TeamRocketsResearcher)];
    game.set_state(state);
    game.apply_action(&action(CardId::A4156Will));
    game.apply_action(&action(CardId::A3b069Penny));
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![magmar()]);
    assert_eq!(state.decks[1].cards, vec![get_card_by_enum(CardId::B4a085TeamRocketsResearcher)]);
}

#[test]
fn portrait_can_copy_penny_then_researcher_with_innermost_will() {
    let mut game = setup(16);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2130Smeargle)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::A4156Will)];
    state.hands[1] = vec![get_card_by_enum(CardId::A3b069Penny)];
    state.decks[0].cards = vec![magmar()];
    state.decks[1].cards = vec![get_card_by_enum(CardId::B4a085TeamRocketsResearcher)];
    game.set_state(state);
    game.apply_action(&action(CardId::A4156Will));
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![magmar()]);
    assert_eq!(state.hands[1], vec![get_card_by_enum(CardId::A3b069Penny)]);
    assert_eq!(
        state.decks[1].cards,
        vec![get_card_by_enum(CardId::B4a085TeamRocketsResearcher)]
    );
}

#[test]
fn copied_root_budget_counts_the_nonresearcher_source_branch() {
    let game = setup(13);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2130Smeargle)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[1] = vec![
        get_card_by_enum(CardId::B4a069TeamRocketsResearcher),
        get_card_by_enum(CardId::A2152Cynthia),
    ];
    state.decks[0].cards = twelve_distinct_eligible();
    let portrait = Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    };
    let error = match try_forecast_action(&state, &portrait) {
        Err(error) => error,
        Ok(_) => panic!("4096 Researcher branches plus Cynthia must exceed the root budget"),
    };
    assert!(matches!(
        error.kind,
        UnpricedForecastKind::ResearcherTooManyExactSuccessors {
            required_at_least: 4097,
            limit: 4096
        }
    ));
}

#[test]
fn portrait_does_not_preflight_unreachable_researcher_in_opponent_deck() {
    let game = setup(14);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2130Smeargle)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[1] = vec![get_card_by_enum(CardId::PA007ProfessorsResearch)];
    state.decks[0].cards = thirteen_distinct_eligible();
    state.decks[1].cards = vec![get_card_by_enum(CardId::B4a069TeamRocketsResearcher)];
    let portrait = Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    };
    let branches = try_forecast_action(&state, &portrait)
        .expect("Researcher in the deck is unreachable when Portrait can only copy the hand")
        .into_branches_with_coin_paths();
    assert_eq!(branches.len(), 1);
}

#[test]
fn copied_will_conditioning_preserves_supporter_source_probability() {
    let mut game = setup(11);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2130Smeargle)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::A4156Will)];
    state.hands[1] = vec![
        get_card_by_enum(CardId::B4a069TeamRocketsResearcher),
        get_card_by_enum(CardId::A2152Cynthia),
    ];
    state.decks[0].cards = vec![magmar()];
    game.set_state(state);
    game.apply_action(&action(CardId::A4156Will));
    let state = game.get_state_clone();
    let portrait = Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    };
    let mut researcher_mass = 0.0;
    for (probability, mutation, _) in try_forecast_action(&state, &portrait)
        .unwrap()
        .into_branches_with_coin_paths()
    {
        let mut next = state.clone();
        mutation(&mut StdRng::seed_from_u64(12), &mut next, &portrait);
        if next.hands[0].contains(&magmar()) {
            researcher_mass += probability;
        }
    }
    assert!((researcher_mass - 0.5).abs() < 1e-12);
}
