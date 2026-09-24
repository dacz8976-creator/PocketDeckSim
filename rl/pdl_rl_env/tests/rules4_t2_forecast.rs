#[path = "../src/v2.rs"]
mod v2;

use deckgym::actions::Action;
use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::test_support::attack_action;
use deckgym::{Deck, State};

#[test]
fn observed_t2_is_priced_as_points_for_both_seats_but_no_win_or_loss() {
    for actor in 0..2 {
        let own = vec![PlayedCard::from_id(CardId::A4124SkarmoryEx)
            .with_remaining_hp(10)
            .with_energy(vec![EnergyType::Metal, EnergyType::Metal])];
        let other = vec![
            PlayedCard::from_id(CardId::B4a020TeamRocketsElectrode),
            PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx),
            PlayedCard::from_id(CardId::B4a019TeamRocketsVoltorb),
        ];
        let (p0, p1) = if actor == 0 { (own, other) } else { (other, own) };
        let mut state = State::new(&Deck::default(), &Deck::default());
        state.turn_count = 5;
        state.current_player = actor;
        state.set_board(p0, p1);
        state.points[actor] = 2;
        let action = Action {
            actor,
            action: attack_action(CardId::A4124SkarmoryEx, 0),
            is_stack: false,
        };
        assert!(state.generate_possible_actions().1.contains(&action));
        let obs = PlayerObservation::from_state(&state, actor, &RevealedKnowledge::default());
        let (_, rows, seen) = v2::features(&obs, &[action.clone()], true);
        let diag: serde_json::Value =
            serde_json::from_str(&v2::diagnostics(&obs, &[action], seen)[0]).unwrap();
        let row = rows[0];
        println!("actor={actor}, row={:?}, diag={diag}", &row[..5]);
        assert_eq!(diag["status"], "priced");
        assert_eq!(row[0], 1.0);
        assert!((row[1] - 1.0 / 3.0).abs() < 1e-6);
        assert!((row[2] - 2.0 / 3.0).abs() < 1e-6);
        assert_eq!(row[3], 0.0);
        assert_eq!(row[4], 0.0);
    }
}
