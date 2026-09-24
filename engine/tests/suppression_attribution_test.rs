use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    test_support::{attack_action, get_test_game_with_board},
};

fn attack_with_budew(game: &mut deckgym::Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3013Budew, 0),
        is_stack: false,
    });
}

#[test]
fn clear_veil_blocks_suppression_and_capacity_discard_but_not_damage() {
    let clear_veil = get_card_by_enum(CardId::B4149ClearVeil);
    let scarf = get_card_by_enum(CardId::A4155RescueScarf);
    let revavroom = PlayedCard::from_id(CardId::B4115Revavroom)
        .with_tools(vec![clear_veil.clone(), scarf.clone()]);
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![revavroom, PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let hp_before = game.get_state_clone().get_active(1).get_remaining_hp();

    attack_with_budew(&mut game);

    let state = game.get_state_clone();
    assert_eq!(hp_before - state.get_active(1).get_remaining_hp(), 10);
    assert_eq!(state.get_active(1).attached_tools, vec![clear_veil, scarf]);
    assert!(state.discard_piles[1].is_empty());
}
