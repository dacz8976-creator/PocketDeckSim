//! Coin-flip damage prevention, Part 1 (Sept 30; scratch-only, read-only): for each attack that delivers damage
//! through a queued choice, does the defender's coin (Togekiss's Celestial Blessing: heads prevents the damage) flip?
//! 100 seeds per case (20,940,000,000 + i); the queued choice is steered at Togekiss. "prevented" counts the runs where
//! Togekiss took no damage from it, "hit" where it did. A coin shows as both; a skipped coin as "prevented 0".
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};

fn mon(id: CardId, energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(energy)
}

/// Togekiss's remaining HP, or None once it is Knocked Out (counted as a hit).
fn togekiss_hp(state: &State) -> Option<u32> {
    state.in_play_pokemon[1].iter().flatten().find(|p| p.get_name() == "Togekiss").map(|p| p.get_remaining_hp())
}

fn togekiss_idx(state: &State) -> Option<usize> {
    state.enumerate_in_play_pokemon(1).find(|(_, p)| p.get_name() == "Togekiss").map(|(i, _)| i)
}

/// Pick the queued choice aimed at Togekiss (or the discard variant for Chase Order when asked).
fn pick(state: &State, choices: &[Action], discard: bool) -> Action {
    let t = togekiss_idx(state);
    let aims = |a: &SimpleAction| match a {
        SimpleAction::ApplyDamage { targets, .. } => targets.iter().any(|(d, p, i)| *d > 0 && *p == 1 && Some(*i) == t),
        SimpleAction::ApplyQueuedAttackDamage { targets, .. } => targets.iter().any(|(d, opp, i)| *d > 0 && *opp && Some(*i) == t),
        SimpleAction::Activate { player: 1, in_play_idx } => Some(*in_play_idx) == t,
        _ => false,
    };
    if let Some(a) = choices.iter().find(|a| discard && matches!(a.action, SimpleAction::DiscardOwnBenchedThenDamage { .. })) {
        return a.clone();
    }
    choices.iter().find(|a| aims(&a.action)).cloned().unwrap_or_else(|| choices[0].clone())
}

fn is_queued_damage(a: &SimpleAction) -> bool {
    matches!(a, SimpleAction::ApplyDamage { .. } | SimpleAction::ApplyQueuedAttackDamage { .. } | SimpleAction::DiscardOwnBenchedThenDamage { .. })
}

struct Case {
    name: &'static str,
    attacker: Vec<PlayedCard>,
    defender: Vec<PlayedCard>,
    attack: (CardId, usize),
    discard: bool,
}

fn run(case: &Case) {
    let (mut prevented, mut hit, mut no_queue) = (0, 0, 0);
    let mut seen = std::collections::BTreeSet::new();
    let mut kinds = std::collections::BTreeSet::new();
    for i in 0..100u64 {
        let mut game = get_initialized_game_with_board(20_940_000_000 + i, 0, 5, case.attacker.clone(), case.defender.clone());
        let before = togekiss_hp(&game.get_state_clone()).unwrap();
        game.apply_action(&Action { actor: 0, action: attack_action(case.attack.0, case.attack.1), is_stack: false });
        let mut queued = false;
        for _ in 0..20 {
            let state = game.get_state_clone();
            if state.move_generation_stack.is_empty() { break; }
            let (actor, choices) = state.generate_possible_actions();
            if actor != 0 || choices.is_empty() { break; }
            let choice = pick(&state, &choices, case.discard);
            if is_queued_damage(&choice.action) {
                queued = true;
                let k = format!("{:?}", choice.action);
                kinds.insert(k.split([' ', '(', '{']).next().unwrap_or("").to_string());
            }
            game.apply_action(&choice);
        }
        let after = togekiss_hp(&game.get_state_clone());
        let dealt = after.map(|a| before - a);
        if !queued { no_queue += 1; continue; }
        seen.insert(dealt.map_or("KO".to_string(), |d| d.to_string()));
        if dealt == Some(0) { prevented += 1 } else { hit += 1 }
    }
    println!("PROBE | {:58} | queued {:3} | prevented {:3} | hit {:3} | damage seen {:?} | via {:?}{}",
        case.name, 100 - no_queue, prevented, hit, seen, kinds,
        if no_queue > 0 { format!(" | no queued choice in {no_queue}") } else { String::new() });
}

#[test]
fn probe() {
    use CardId::*;
    use EnergyType::*;
    let bulba = || PlayedCard::from_id(A1001Bulbasaur);
    let toge = || PlayedCard::from_id(A4080Togekiss);
    let cases = vec![
        Case { name: "also_choice_bench_damage, opponent (Pikachu Spark), Bench", attacker: vec![mon(A2a025Pikachu, vec![Lightning])], defender: vec![bulba(), toge()], attack: (A2a025Pikachu, 0), discard: false },
        Case { name: "also_choice_bench_damage, own Bench (Zapdos Raging Thunder), Active", attacker: vec![mon(A1103Zapdos, vec![Lightning; 3]), bulba()], defender: vec![toge()], attack: (A1103Zapdos, 0), discard: false },
        Case { name: "optional_discard_benched_basic (Chase Order), no discard", attacker: vec![mon(B4011VespiquenEx, vec![Grass; 2]), PlayedCard::from_id(B4010Combee)], defender: vec![toge()], attack: (B4011VespiquenEx, 0), discard: false },
        Case { name: "optional_discard_benched_basic (Chase Order), discard", attacker: vec![mon(B4011VespiquenEx, vec![Grass; 2]), PlayedCard::from_id(B4010Combee)], defender: vec![toge()], attack: (B4011VespiquenEx, 0), discard: true },
        Case { name: "discard_all_energy_of_type (Chien-Pao ex Diving Icicles)", attacker: vec![mon(B2a037ChienPaoEx, vec![Water; 3])], defender: vec![bulba(), toge()], attack: (B2a037ChienPaoEx, 1), discard: false },
        Case { name: "damage_to_any_opponent_per_target_energy (Tapu Lele)", attacker: vec![mon(A3084TapuLele, vec![Psychic])], defender: vec![bulba(), toge().with_energy(vec![Psychic; 2])], attack: (A3084TapuLele, 0), discard: false },
        Case { name: "self_discard_energy_then_damage_any (Volcarona Volcanic Ash)", attacker: vec![mon(A1a014Volcarona, vec![Fire; 3])], defender: vec![bulba(), toge()], attack: (A1a014Volcarona, 0), discard: false },
        Case { name: "switch_in_opponent_benched_then_damage (Sandy Shocks)", attacker: vec![mon(B3a035SandyShocks, vec![Fighting; 3])], defender: vec![bulba(), toge()], attack: (B3a035SandyShocks, 0), discard: false },
        Case { name: "direct_damage_if_damaged (Decidueye ex Pierce the Pain)", attacker: vec![mon(A3012DecidueyeEx, vec![Grass; 2])], defender: vec![bulba(), toge().with_remaining_hp(130)], attack: (A3012DecidueyeEx, 0), discard: false },
        Case { name: "direct_damage (Heatmor Tongue Whip), rules/09's example", attacker: vec![mon(B1044Heatmor, vec![Fire])], defender: vec![bulba(), toge()], attack: (B1044Heatmor, 0), discard: false },
        Case { name: "extra: coin_flip_also_choice_bench_damage (Ogerpon), Active", attacker: vec![mon(B2048WellspringMaskOgerpon, vec![Water; 2])], defender: vec![toge(), bulba()], attack: (B2048WellspringMaskOgerpon, 0), discard: false },
        Case { name: "extra: self_discard_energy_and_choice_bench (Urshifu), Active", attacker: vec![mon(B3051RapidStrikeUrshifu, vec![Water; 2])], defender: vec![toge(), bulba()], attack: (B3051RapidStrikeUrshifu, 0), discard: false },
        Case { name: "extra: conditional_bench_damage (Blastoise Double Splash), Bench", attacker: vec![mon(B1a019Blastoise, vec![Water; 5])], defender: vec![bulba(), toge()], attack: (B1a019Blastoise, 0), discard: false },
        Case { name: "extra: Mega Kangaskhan ex (second punch), Active", attacker: vec![mon(B2127MegaKangaskhanEx, vec![Colorless; 3])], defender: vec![toge()], attack: (B2127MegaKangaskhanEx, 0), discard: false },
        Case { name: "extra: shuffle_opponent_tools_before_damage (Hoopa), Active", attacker: vec![mon(B4077Hoopa, vec![Psychic])], defender: vec![toge()], attack: (B4077Hoopa, 0), discard: false },
    ];
    for case in &cases {
        run(case);
    }
}
