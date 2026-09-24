use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    players::{EndTurnPlayer, Player},
    test_support::load_test_decks,
    Deck, Game, State,
};
use rand::rngs::StdRng;
use std::sync::{Arc, Mutex};

#[derive(Debug)]
struct CaptureActions {
    deck: Deck,
    seen: Arc<Mutex<Vec<Action>>>,
}

impl Player for CaptureActions {
    fn get_deck(&self) -> Deck { self.deck.clone() }

    fn decide_omniscient(
        &mut self,
        _: &mut StdRng,
        _: &State,
        actions: &[Action],
    ) -> Action {
        *self.seen.lock().unwrap() = actions.to_vec();
        actions.iter()
            .find(|a| matches!(a.action, SimpleAction::EndTurn))
            .unwrap()
            .clone()
    }
}

fn observed_root_actions(state: State) -> Vec<Action> {
    let seen = Arc::new(Mutex::new(Vec::new()));
    let players: Vec<Box<dyn Player>> = vec![
        Box::new(CaptureActions {
            deck: state.decks[0].clone(),
            seen: Arc::clone(&seen),
        }),
        Box::new(EndTurnPlayer { deck: state.decks[1].clone() }),
    ];
    let mut game = Game::from_state(state, players, 7);
    game.play_tick();
    let result = seen.lock().unwrap().clone();
    result
}

fn base_state() -> State {
    let (a, b) = load_test_decks();
    let mut state = State::new(&a, &b);
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    // This public extra placement keeps the decision non-forced in both hidden worlds.
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state
}

#[test]
fn penny_root_actions_reveal_whether_opponent_deck_contains_supporter() {
    let mut with_supporter = base_state();
    with_supporter.hands[0].push(get_card_by_enum(CardId::A3b069Penny));
    with_supporter.decks[1].cards = vec![
        get_card_by_enum(CardId::PA007ProfessorsResearch),
        get_card_by_enum(CardId::A1033Charmander),
    ];
    let mut without_supporter = with_supporter.clone();
    without_supporter.decks[1].cards = vec![
        get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::A1033Charmander),
    ];

    assert_eq!(
        deckgym::observation::PlayerObservation::from_state(&with_supporter, 0, &Default::default()),
        deckgym::observation::PlayerObservation::from_state(&without_supporter, 0, &Default::default()),
        "sanitized observations must match before comparing root actions"
    );
    let yes = observed_root_actions(with_supporter);
    let no = observed_root_actions(without_supporter);
    let has_penny = |actions: &[Action]| actions.iter().any(|a| {
        matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Penny")
    });
    assert_eq!(has_penny(&yes), has_penny(&no),
        "policy-visible root actions must not disclose hidden opponent deck identities");
}

#[test]
fn portrait_root_actions_reveal_whether_opponent_hand_contains_supporter() {
    let mut with_supporter = base_state();
    with_supporter.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::B2130Smeargle));
    with_supporter.hands[1] = vec![get_card_by_enum(CardId::PA007ProfessorsResearch)];
    let mut without_supporter = with_supporter.clone();
    without_supporter.hands[1] = vec![get_card_by_enum(CardId::PA001Potion)];

    assert_eq!(
        deckgym::observation::PlayerObservation::from_state(&with_supporter, 0, &Default::default()),
        deckgym::observation::PlayerObservation::from_state(&without_supporter, 0, &Default::default()),
        "sanitized observations must match before comparing root actions"
    );
    let yes = observed_root_actions(with_supporter);
    let no = observed_root_actions(without_supporter);
    let has_portrait = |actions: &[Action]| actions.iter().any(|a| {
        matches!(a.action, SimpleAction::UseAbility { in_play_idx: 0 })
    });
    assert_eq!(has_portrait(&yes), has_portrait(&no),
        "policy-visible root actions must not disclose hidden opponent hand identities");
}

fn card_action(state: &State, portrait: bool) -> Option<Action> {
    state.generate_possible_actions().1.into_iter().find(|a| if portrait {
        matches!(a.action, SimpleAction::UseAbility { in_play_idx: 0 })
    } else {
        matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Penny")
    })
}

#[test]
fn no_target_attempts_consume_penny_and_portrait_but_leave_hidden_zones_unchanged() {
    for actor in 0..2 {
        for portrait in [false,true] {
            let mut s = base_state();
            s.current_player = actor;
            s.hands[actor] = vec![get_card_by_enum(CardId::A3b069Penny),get_card_by_enum(CardId::PA007ProfessorsResearch)];
            if portrait { s.in_play_pokemon[actor][0] = Some(PlayedCard::from_id(CardId::B2130Smeargle)); }
            s.decks[1-actor].cards = vec![get_card_by_enum(CardId::PA001Potion)];
            s.hands[1-actor] = vec![get_card_by_enum(CardId::PA001Potion)];
            let action = card_action(&s,portrait).expect("hidden target absence cannot block an attempt");
            let mut game = Game::from_state(s.clone(), vec![
                Box::new(EndTurnPlayer {deck:s.decks[0].clone()}),
                Box::new(EndTurnPlayer {deck:s.decks[1].clone()})],71);
            game.apply_action(&action);
            let after = game.get_state_clone();
            assert_eq!(after.decks[1-actor],s.decks[1-actor]);
            assert_eq!(after.hands[1-actor],s.hands[1-actor]);
            assert!(after.move_generation_stack.is_empty());
            assert_eq!(after.turn_count,s.turn_count);
            assert!(card_action(&after,portrait).is_none(),"attempt must consume the once-per-turn use");
            if portrait {
                assert!(after.in_play_pokemon[actor][0].as_ref().unwrap().ability_used);
                assert_eq!(after.hands[actor],s.hands[actor]);
            } else {
                assert!(after.discard_piles[actor].iter().any(|c| c.get_name()=="Penny"));
                assert!(!after.generate_possible_actions().1.iter().any(|a| matches!(&a.action,
                    SimpleAction::Play {trainer_card} if trainer_card.name=="Professor's Research")));
            }
        }
    }
}

#[test]
fn publicly_empty_target_zones_block_attempts_for_both_seats() {
    for actor in 0..2 {
        let mut s = base_state();
        s.current_player = actor;
        s.hands[actor] = vec![get_card_by_enum(CardId::A3b069Penny)];
        s.in_play_pokemon[actor][0] = Some(PlayedCard::from_id(CardId::B2130Smeargle));
        s.decks[1-actor].cards.clear();
        s.hands[1-actor].clear();
        assert!(card_action(&s,false).is_none());
        assert!(card_action(&s,true).is_none());
    }
}

#[test]
fn entire_offered_input_matches_across_hidden_supporter_identity_and_order_for_both_seats() {
    use deckgym::observation::{canonical_actions,PlayerObservation};
    for actor in 0..2 {
        let mut s = base_state();
        s.current_player = actor;
        s.hands[actor] = vec![get_card_by_enum(CardId::A3b069Penny)];
        s.in_play_pokemon[actor][0] = Some(PlayedCard::from_id(CardId::B2130Smeargle));
        let input = |s: &State| {
            let mut actions=s.generate_possible_actions().1;
            canonical_actions(&mut actions);
            (PlayerObservation::from_state(s,actor,&Default::default()), actions)
        };
        let mut expected = None;
        for cards in [vec![CardId::PA001Potion,CardId::A1033Charmander],
            vec![CardId::PA007ProfessorsResearch,CardId::PA001Potion],
            vec![CardId::PA001Potion,CardId::PA007ProfessorsResearch],
            vec![CardId::A3b069Penny,CardId::A3b086Penny]] {
            s.hands[1-actor]=cards.iter().map(|c|get_card_by_enum(*c)).collect();
            s.decks[1-actor].cards=s.hands[1-actor].clone();
            let observed=input(&s);
            if let Some(ref expected)=expected { assert_eq!(expected,&observed); }
            else { expected=Some(observed); }
        }
    }
}
