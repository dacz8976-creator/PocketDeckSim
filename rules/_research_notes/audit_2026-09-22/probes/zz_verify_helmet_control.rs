use deckgym::{actions::{Action, SimpleAction}, card_ids::CardId, database::get_card_by_enum,
    models::{PlayedCard, StatusCondition}, test_support::get_test_game_with_board};
fn run(helmet: bool) -> u32 {
    let mut p = PlayedCard::from_id(CardId::A1055Blastoise).with_status_condition(StatusCondition::Poisoned);
    if helmet { p = p.with_tool(get_card_by_enum(CardId::B1219HeavyHelmet)); }
    let mut game = get_test_game_with_board(vec![p], vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    game.apply_action(&Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
    game.get_state_clone().in_play_pokemon[0][0].as_ref().unwrap().get_remaining_hp()
}
#[test]
fn control() { println!("VERIFY no_helmet_hp={} helmet_hp={}", run(false), run(true)); }
