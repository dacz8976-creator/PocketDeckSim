//! Triage check (Oct 6, scratch copy only, not for the repo): Accelgor's Deck and Cover into a Rocky Helmet holder, then the owner promotes
//! a damaged Benched Pokémon. The recorded game (20261004_214731 turn 6, 280-298 s) shows no Rocky Helmet damage to the attacker (it left play
//! first) and none to the promoted Butterfree.
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

fn run(bench_order: &[CardId], promote_name: &str) {
    let mut own = vec![PlayedCard::from_id(CardId::B4014Accelgor).with_energy(vec![EnergyType::Grass, EnergyType::Grass])];
    for (i, id) in bench_order.iter().enumerate() {
        let mut p = PlayedCard::from_id(*id);
        if *id == CardId::B3b003Butterfree {
            p = p.with_remaining_hp(50);
        }
        let _ = i;
        own.push(p);
    }
    let helmet = get_card_by_enum(CardId::A2148RockyHelmet);
    let opp = vec![
        PlayedCard::from_id(CardId::B4120MegaRayquazaEx).with_tool(helmet),
        PlayedCard::from_id(CardId::A1033Charmander),
    ];
    let mut game: Game<'static> = get_test_game_with_board(own, opp);
    let before: Vec<(String, u32)> = game.get_state_clone().in_play_pokemon[0]
        .iter()
        .flatten()
        .map(|p| (p.get_name(), p.get_remaining_hp()))
        .collect();
    println!("[{promote_name}] own board before: {before:?}");
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B4014Accelgor, 0), is_stack: false });
    let mut guard = 0;
    loop {
        guard += 1;
        let st = game.get_state_clone();
        let (actor, actions) = st.generate_possible_actions();
        let kinds: Vec<String> = actions.iter().map(|a| format!("{:?}", a.action)).map(|s| s.chars().take(40).collect()).collect();
        println!("  step {guard}: actor {actor}, {} actions: {:?}", actions.len(), kinds);
        let pick = actions.iter().find(|a| match &a.action {
            SimpleAction::Promote { in_play_idx, .. } | SimpleAction::Activate { in_play_idx, .. } => {
                st.in_play_pokemon[0][*in_play_idx].as_ref().map(|p| p.get_name()).as_deref() == Some(promote_name)
            }
            _ => false,
        });
        let pick = pick.or_else(|| if actions.len() == 1 && { let s = format!("{:?}", actions[0].action); s.starts_with("ShuffleInPlay") || s.starts_with("ResolveAttackRetaliation") } { actions.first() } else { None });
        match pick {
            Some(a) => {
                println!("    applying {:?}", a.action);
                game.apply_action(a);
            }
            None => break,
        }
        if guard > 6 {
            break;
        }
    }
    let st = game.get_state_clone();
    let after: Vec<(String, u32)> = st.in_play_pokemon[0].iter().flatten().map(|p| (p.get_name(), p.get_remaining_hp())).collect();
    let opp_after: Vec<(String, u32)> = st.in_play_pokemon[1].iter().flatten().map(|p| (p.get_name(), p.get_remaining_hp())).collect();
    println!("[{promote_name}] own board after: {after:?} | opponent after: {opp_after:?} | accelgor in deck: {}", st.decks[0].cards.iter().any(|c| c.get_name() == "Accelgor"));
    let target = after.iter().find(|(n, _)| n == promote_name).map(|x| x.1);
    println!("[{promote_name}] promoted Pokémon HP now {target:?}");
}

#[test]
fn deck_and_cover_then_promote_butterfree() {
    // Butterfree (damaged to 50) is the first Bench slot, Metapod the second.
    run(&[CardId::B3b003Butterfree, CardId::B3b002Metapod], "Butterfree");
    // The same with the damaged Butterfree in the second slot (a different swap index).
    run(&[CardId::B3b002Metapod, CardId::B3b003Butterfree], "Butterfree");
}
