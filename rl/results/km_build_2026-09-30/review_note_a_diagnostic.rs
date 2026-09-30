#[cfg(test)]
mod km_mine_side_diagnostic {
    //! Diagnostic for the review's note A (not part of B): N2 reaches both of kt_clocks' clocks. Player 0 (myself) has
    //! Mega Lucario ex (190 HP) Active; player 1 threatens with Mega Lucario ex holding [F][F] (Fighting Pulse 90).
    //! Training Area in play. `mine` (turns until player 0's opponent wins) is 3 hits under kta and 2 under km; `theirs`
    //! (player 0's own threat on player 1) likewise gets N2. Each equals kt_clock_stadium on its side.
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;

    #[test]
    fn n2_reaches_both_sides_through_kt_clocks() {
        let mut state = State::default();
        state.set_board(
            vec![PlayedCard::from_id(CardId::B3081MegaLucarioEx).with_energy(vec![EnergyType::Fighting; 2])],
            vec![PlayedCard::from_id(CardId::B3081MegaLucarioEx).with_energy(vec![EnergyType::Fighting; 2])],
        );
        state.turn_count = 5;
        state.current_player = 0;
        state.active_stadium = Some(get_card_by_enum(CardId::B2153TrainingArea));
        let (km_mine, km_theirs) = kt_clocks(&state, 0, true, true, false, EvalFeatures::KM);
        let (kta_mine, kta_theirs) = kt_clocks(&state, 0, true, true, false, EvalFeatures::KTA);
        println!("mine: km {km_mine} kta {kta_mine}; theirs: km {km_theirs} kta {kta_theirs}");
        assert_eq!(km_mine, kt_clock_stadium(&state, 0, false, true, false, true, true, true).total(0.0));
        assert_eq!(km_theirs, kt_clock_stadium(&state, 1, true, true, false, true, true, true).total(0.0));
        assert_eq!(kta_mine, kt_clock_stadium(&state, 0, false, true, false, true, true, false).total(0.0));
        assert_eq!((kta_mine - km_mine, kta_theirs - km_theirs), (1.0, 1.0));
    }
}
