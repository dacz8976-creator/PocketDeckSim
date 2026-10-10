//! F1 evidence (the cloud, Oct 10; scratch, not part of the engine): the F1 test's play body
//! (g2_copied_second_punch_waits_for_the_copiers_promotion_after_rocky_helmet, f601abcb) without its asserts, traced.
//! Each step prints the actor, the kinds of the choices offered and the one taken (Promote { player: 0, in_play_idx: 1 }
//! when offered, as the test does; else the first choice); then the damage to the opponent's Active (180 - its HP).
//! WRAP is replaced by the build: nothing on the official engine, G1 + G2 off at c7a25df4.
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

fn kind(a: &SimpleAction) -> String {
    format!("{a:?}").chars().take_while(|c| c.is_alphanumeric()).collect()
}

fn trace() -> String {
    let mut out = String::new();
    for seed in 0..5u64 {
        out += &format!("seed {seed}\n");
        let r = std::panic::catch_unwind(|| {
            let mut s = String::new();
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                5,
                vec![
                    PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![EnergyType::Psychic; 3]).with_remaining_hp(20),
                    PlayedCard::from_id(CardId::A1001Bulbasaur),
                ],
                vec![
                    PlayedCard::from_id(CardId::B2127MegaKangaskhanEx).with_tool(get_card_by_enum(CardId::A2148RockyHelmet)),
                    PlayedCard::from_id(CardId::B2124Meowth),
                ],
            );
            game.apply_action(&Action { actor: 0, action: attack_action(CardId::A1a032MewEx, 1), is_stack: false });
            s += "  step 0: actor 0 takes Attack (Genome Hacking)\n";
            let (actor, choices) = game.get_state_clone().generate_possible_actions();
            let copy = choices
                .iter()
                .find(|c| matches!(&c.action, SimpleAction::Attack(a) if a.title == "Double-Punching Family"))
                .expect("Genome Hacking offers Double-Punching Family")
                .clone();
            s += &format!("  step 1: actor {actor}, {} choices, takes Attack (Double-Punching Family)\n", choices.len());
            game.apply_action(&copy);
            for step in 2..14 {
                let state = game.get_state_clone();
                if state.move_generation_stack.is_empty() {
                    break;
                }
                let (actor, choices) = state.generate_possible_actions();
                if choices.is_empty() {
                    break;
                }
                let pick = choices
                    .iter()
                    .find(|c| matches!(c.action, SimpleAction::Promote { player: 0, in_play_idx: 1 }))
                    .unwrap_or(&choices[0])
                    .clone();
                let kinds: Vec<String> = choices.iter().map(|c| kind(&c.action)).collect();
                s += &format!("  step {step}: actor {actor}, choices [{}], takes {:?}\n", kinds.join(", "), pick.action);
                game.apply_action(&pick);
            }
            let state = game.get_state_clone();
            s += &format!(
                "  end: player 0's Active {}, damage to player 1's Active {}\n",
                state.maybe_get_active(0).map_or("-".to_string(), |p| p.get_name()),
                180 - state.get_active(1).get_remaining_hp()
            );
            s
        });
        out += &r.unwrap_or_else(|e| {
            format!("  PANIC: {}\n", e.downcast_ref::<String>().cloned().or(e.downcast_ref::<&str>().map(|x| x.to_string())).unwrap_or_default())
        });
    }
    out
}

#[test]
fn f1_trace() {
    let out = WRAP;
    std::fs::write(std::env::var("F1_OUT").unwrap(), out).unwrap();
}
