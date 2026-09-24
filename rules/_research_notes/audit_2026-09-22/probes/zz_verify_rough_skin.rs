use deckgym::{actions::Action, card_ids::CardId, models::PlayedCard,
    test_support::{attack_action, get_test_game_with_board}};
fn budew_hp(extra_own_bench: Option<CardId>, twice: bool) -> (u32, u32) {
    let mut me = vec![PlayedCard::from_id(CardId::B3013Budew)];
    if let Some(c) = extra_own_bench { me.push(PlayedCard::from_id(c)); }
    let mut game = get_test_game_with_board(me, vec![PlayedCard::from_id(CardId::A1a056Druddigon), PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    let before = game.get_state_clone().get_active(0).get_remaining_hp();
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B3013Budew, 0), is_stack: false });
    let _ = twice;
    let s = game.get_state_clone();
    (before, s.in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp()).unwrap_or(0))
}
#[test]
fn rough_skin_vs_prickly_powder() {
    let (b, a) = budew_hp(None, false);
    println!("VERIFY Budew Prickly Powder into Druddigon: Budew HP {b} -> {a} (official FAQ: no Rough Skin damage)");
    let (b2, a2) = budew_hp(Some(CardId::B2097AlolanMuk), false);
    println!("VERIFY with Alolan Muk (Basics have no Abilities) on Budew's bench: Budew HP {b2} -> {a2} (expected no Rough Skin)");
}
