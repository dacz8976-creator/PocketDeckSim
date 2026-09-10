use deckgym::{
    card_ids::CardId,
    card_validation::{
        get_implementation_status, implementation_limitations, ImplementationStatus,
    },
};

#[test]
fn mapped_cards_with_known_rule_gaps_do_not_report_complete() {
    for id in [
        CardId::B4115Revavroom,
        CardId::B3025Victini,
        CardId::PB049Victini,
    ] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::RulesUnverified
        );
        assert!(!get_implementation_status(id).is_complete());
        assert!(!implementation_limitations(id).is_empty());
    }
}

#[test]
fn ordinary_mapping_coverage_remains_available() {
    assert_eq!(
        get_implementation_status(CardId::A1001Bulbasaur),
        ImplementationStatus::Complete
    );
    assert!(implementation_limitations(CardId::A1001Bulbasaur).is_empty());
}
