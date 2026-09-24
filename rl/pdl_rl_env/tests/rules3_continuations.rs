#[path = "../src/v2.rs"]
mod v2;

use deckgym::actions::{Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{PlayedCard, StatusCondition};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::{Deck, State};

fn state(ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> State {
    let mut s = State::new(&Deck::default(), &Deck::default());
    s.current_player = 0;
    s.turn_count = 3;
    s.set_board(ours, theirs);
    s
}

fn end() -> Action {
    Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false }
}

#[test]
fn end_turn_point_denial_is_weighted_after_forced_checkup() {
    let mut s = state(
        vec![PlayedCard::from_id(CardId::B2b040Darkrai), PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![
            PlayedCard::from_id(CardId::B3a045Glimmora).with_remaining_hp(10)
                .with_status_condition(StatusCondition::Asleep),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    s.points[0] = 2;
    let action = end();
    assert!(s.generate_possible_actions().1.contains(&action));
    let obs = PlayerObservation::from_state(&s, 0, &RevealedKnowledge::default());
    let (_, rows, seen) = v2::features(&obs, &[action.clone()], true);
    let diag: serde_json::Value = serde_json::from_str(&v2::diagnostics(&obs, &[action], seen)[0]).unwrap();
    println!("point-denial row={:?} diagnostic={diag}", &rows[0][..8]);
    assert!(seen);
    assert_eq!(diag["new_rule_frame_seen"], true);
    assert_eq!(diag["status"], "priced");
    assert_eq!(rows[0][0], 1.0);
    assert!((rows[0][1] - 1.0 / 6.0).abs() < 1e-6);
    assert!((rows[0][3] - 0.5).abs() < 1e-6);
}

#[test]
fn hidden_end_turn_evolution_is_explicitly_unpriced() {
    let mut s = state(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::B3b001Caterpie)],
    );
    s.decks[1].cards = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    let action = end();
    assert!(s.generate_possible_actions().1.contains(&action));
    let obs = PlayerObservation::from_state(&s, 0, &RevealedKnowledge::default());
    let (_, rows, seen) = v2::features(&obs, &[action.clone()], true);
    let diag: serde_json::Value = serde_json::from_str(&v2::diagnostics(&obs, &[action], seen)[0]).unwrap();
    println!("evolution row={:?} diagnostic={diag}", &rows[0][..8]);
    assert_eq!(rows[0][0], 0.0);
    assert_eq!(diag["status"], "hidden_refusal");
    assert!(diag["reason"].as_str().unwrap().contains("unknown deck"));
}

#[test]
fn known_own_end_turn_evolution_frame_is_priced() {
    use deckgym::actions::try_forecast_action;
    use rand::{rngs::StdRng, SeedableRng};

    let mut s = state(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::B3b001Caterpie)],
    );
    s.decks[1].cards = vec![get_card_by_enum(CardId::B3b002Metapod)];
    let end_action = end();
    let (probabilities, mutations) = try_forecast_action(&s, &end_action).unwrap().into_branches();
    assert_eq!(probabilities, vec![1.0]);
    let mut pending = s.clone();
    mutations.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(5), &mut pending, &end_action);
    let (actor, actions) = pending.generate_possible_actions();
    assert_eq!(actor, 1);
    assert_eq!(actions.len(), 1);
    assert!(matches!(actions[0].action, SimpleAction::ResolveEndTurnEvolution { player: 1 }));
    let obs = PlayerObservation::from_state(&pending, 1, &RevealedKnowledge::default());
    let (_, rows, seen) = v2::features(&obs, &actions, true);
    let diag: serde_json::Value = serde_json::from_str(&v2::diagnostics(&obs, &actions, seen)[0]).unwrap();
    println!("known evolution row={:?} diagnostic={diag}", &rows[0][..8]);
    assert_eq!(rows[0][0], 1.0);
    assert_eq!(diag["status"], "priced");
    assert_eq!(diag["new_rule_frame_seen"], false);
    assert!(!seen, "the evolution action finishes without leaving a new rule frame");
}
