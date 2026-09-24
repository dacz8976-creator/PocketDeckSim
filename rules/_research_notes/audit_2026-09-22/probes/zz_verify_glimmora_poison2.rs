use deckgym::{actions::{Action, SimpleAction}, card_ids::CardId,
    models::{PlayedCard, StatusCondition}, test_support::get_initialized_game_with_board};
#[test]
fn glimmora_poison_ko_points() {
    let (mut scored, mut denied, mut alive) = (0, 0, 0);
    let mut seen = std::collections::BTreeSet::new();
    for seed in 0..60u64 {
        let g = PlayedCard::from_id(CardId::B3a045Glimmora).with_status_condition(StatusCondition::Poisoned).with_remaining_hp(10);
        let mut game = get_initialized_game_with_board(seed, 0, 3,
            vec![g, PlayedCard::from_id(CardId::B3a044Glimmet)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::A1001Bulbasaur)]);
        let mut s = game.get_state_clone(); s.points = [0,0]; game.set_state(s);
        game.apply_action(&Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
        // Resolve forced continuation actions (coin, promotion, finish Checkup) until a normal turn menu appears.
        for _ in 0..8 {
            let (actor, actions) = game.get_state_clone().generate_possible_actions();
            if actions.is_empty() || actions.iter().any(|a| matches!(a.action, SimpleAction::EndTurn)) { break; }
            seen.insert(format!("{}", actions[0].action).chars().take(40).collect::<String>());
            game.apply_action(&Action { actor, ..actions[0].clone() });
        }
        let s = game.get_state_clone();
        let still = s.in_play_pokemon[0][0].as_ref().map(|p| p.get_name()).unwrap_or_default();
        if still.contains("Glimmora") { alive += 1 } else if s.points[1] >= 1 { scored += 1 } else { denied += 1 }
    }
    println!("VERIFY glimmora poison-KO over 60 seeds: opponent_scored={scored} denied={denied} still_alive={alive}; forced actions seen: {seen:?}");
}
