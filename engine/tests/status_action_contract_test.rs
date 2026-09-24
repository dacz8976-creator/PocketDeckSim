use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::get_test_game_with_board,
};

fn offered_actions(condition: StatusCondition) -> Vec<Action> {
    let active = PlayedCard::from_id(CardId::B3024CastformSunnyForm)
        .with_energy(vec![EnergyType::Fire, EnergyType::Colorless])
        .with_status_condition(condition);
    let game = get_test_game_with_board(
        vec![active, PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    game.get_state_clone().generate_possible_actions().1
}

#[test]
fn asleep_and_paralyzed_active_offer_neither_attack_nor_retreat() {
    for condition in [StatusCondition::Asleep, StatusCondition::Paralyzed] {
        let actions = offered_actions(condition);
        assert!(
            !actions.iter().any(|action| matches!(action.action, SimpleAction::Attack(_))),
            "{condition:?} Active was offered Attack"
        );
        assert!(
            !actions.iter().any(|action| matches!(action.action, SimpleAction::Retreat(_))),
            "{condition:?} Active was offered Retreat"
        );
    }
}
