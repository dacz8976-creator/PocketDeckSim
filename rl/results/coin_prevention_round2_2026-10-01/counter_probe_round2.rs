//! The later round of coin-flip prevention (Oct 1; scratch): do the coin counters of
//! `../coin_prevention_repair_2026-09-30/instrument_scan.py` see the seven repaired sites? Like Sonnet's F5 probe
//! (`../coin_prevention_repair_2026-09-30/smoke/rerun_R/counter_probe.rs`, whose detection functions are copied here
//! unchanged), it applies the counters' detection logic to boards built with `test_support` and asserts what each must
//! read. For each site:
//! - the attack's mechanic name, as the scan prints it, is in the script's HELPERS (the off-gate counter
//!   `offgate_helper_choice` keys on it); Wild Swing's is counted instead by `offgate_discard_then_damage`;
//! - with Meowth (Carefree Steps) where the queued damage lands, the queued coin-path choice is offered
//!   (`coin_queued_offered`), and choosing it runs the coin split for Meowth (`coin_full_prevention`); for Mega
//!   Kangaskhan ex's second punch, Togekiss (Celestial Blessing) stands in, since the first punch would Knock Out a Meowth;
//! - with Bulbasaur there instead (Mega Latios ex for the punch), no queued coin-path choice is offered, only plain
//!   ApplyDamage ones.
//! It plays no game and needs the `test-utils` feature.
//!   cargo run --release --features test-utils --example counter_probe_round2
use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::State;

const FINITE: [&str; 2] = ["A2 114", "B3b 050"];
const FULL: [&str; 3] = ["A4 080", "B2 124", "B2 204"];
/// The HELPERS list of `instrument_scan.py`, as of the later round (its run checks each name is in the script).
const HELPERS: [&str; 14] = ["DirectDamage", "DirectDamageAndSelfCardEffect", "DirectDamageIfDamaged",
    "SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon", "SelfDiscardEnergyThenDamageAnyOpponentPokemon",
    "DamageToAnyOpponentPerTargetEnergy", "SwitchInOpponentBenchedThenDamage",
    "OptionalDiscardBenchedBasicForExtraDamage",
    "CoinFlipAlsoChoiceBenchDamage", "SelfDiscardEnergyAndChoiceBenchDamage", "ConditionalBenchDamage",
    "ShuffleOpponentToolsIntoDeckBeforeDamage", "DiscardToolsFromHandForDamage",
    "MegaKangaskhanExDoublePunchingFamily"];

/// The coin split detection of `instrument_scan.py`: slots of the mover's opponent whose coin split ran in the chosen move's
/// forecast, (finite-cut slots, full-prevention slots).
fn split_slots(before: &State, chosen: &Action) -> (Vec<usize>, Vec<usize>) {
    let opp = 1 - chosen.actor;
    let branches = |s: &State| try_forecast_action(s, chosen).ok().map(|o| o.into_branches().0.len());
    let (mut finite, mut full) = (vec![], vec![]);
    if let Some(n_real) = branches(before) {
        for i in 0..before.in_play_pokemon[opp].len() {
            let Some(id) = before.in_play_pokemon[opp].get(i).and_then(|p| p.as_ref()).map(|p| p.card.get_id()) else { continue };
            let (is_finite, is_full) = (FINITE.contains(&id.as_str()), FULL.contains(&id.as_str()));
            if !is_finite && !is_full {
                continue;
            }
            let mut without = before.clone();
            without.in_play_pokemon[opp][i] = Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
            if branches(&without).is_some_and(|n| n < n_real) {
                if is_finite { finite.push(i) } else { full.push(i) }
            }
        }
    }
    (finite, full)
}

fn mechanic_of(attack: &deckgym::models::Attack) -> String {
    attack.effect.as_deref().and_then(|e| deckgym::actions::EFFECT_MECHANIC_MAP.get(e))
        .map(|m| format!("{m:?}").chars().take_while(|c| c.is_alphanumeric()).collect::<String>())
        .unwrap_or_default()
}

/// The queued coin-path choices offered at a coin Pokemon (the counter `coin_queued_offered`).
fn queued_offered(state: &State, actor: usize) -> usize {
    let opp = 1 - actor;
    let is_coin = |i: usize| {
        state.in_play_pokemon[opp].get(i).and_then(|p| p.as_ref())
            .is_some_and(|p| FINITE.contains(&p.card.get_id().as_str()) || FULL.contains(&p.card.get_id().as_str()))
    };
    state.generate_possible_actions().1.iter().filter(|a| match &a.action {
        SimpleAction::ApplyQueuedAttackDamage { attack, targets } => {
            !mechanic_of(attack).starts_with("AlsoChoiceBenchDamage") && targets.iter().any(|(_, is_opp, i)| *is_opp && is_coin(*i))
        }
        _ => false,
    }).count()
}

/// The off-gate ApplyDamage choices offered to `actor` (the counter `offgate_helper_choice`, without the mechanic test).
fn plain_damage_offered(state: &State, actor: usize) -> usize {
    state.generate_possible_actions().1.iter().filter(|a| matches!(&a.action,
        SimpleAction::ApplyDamage { is_from_active_attack: true, targets, .. } if targets.iter().any(|(_, p, _)| *p == 1 - actor))).count()
}

fn attack_named(state: &State, title: &str) -> Action {
    state.generate_possible_actions().1.into_iter()
        .find(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == title))
        .unwrap_or_else(|| panic!("{title} is not offered"))
}

/// Player 1 uses `title` from `attacker` into `defenders` (with `hand` as its hand), taking the largest discard offered,
/// until a frame of damage choices is offered to it; seeds are tried until one offers it (Wellspring Dance's heads).
/// Returns that state and the attack's mechanic name.
fn damage_frame(attacker: &[PlayedCard], defenders: &[PlayedCard], hand: &[CardId], title: &str) -> (State, String) {
    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(seed, 1, 5, defenders.to_vec(), attacker.to_vec());
        let mut state = game.get_state_clone();
        state.current_player = 1;
        state.hands[1] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        game.set_state(state.clone());
        let attack = attack_named(&state, title);
        let SimpleAction::Attack(a) = &attack.action else { unreachable!() };
        let name = mechanic_of(a);
        game.apply_action(&attack);
        for _ in 0..5 {
            let state = game.get_state_clone();
            let (actor, choices) = state.generate_possible_actions();
            if actor != 1 || state.move_generation_stack.is_empty() {
                break;
            }
            if choices.iter().any(|a| matches!(a.action, SimpleAction::ApplyDamage { .. } | SimpleAction::ApplyQueuedAttackDamage { .. })) {
                return (state, name);
            }
            let discard = choices.iter().max_by_key(|a| match &a.action {
                SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } => in_play_idxs.len(),
                SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. } => cards.len(),
                _ => 0,
            }).expect("a choice is offered").clone();
            game.apply_action(&discard);
        }
    }
    panic!("{title}: no damage choices offered in 40 seeds");
}

fn main() {
    let mon = |id| PlayedCard::from_id(id);
    let with = |id, energy: Vec<EnergyType>| PlayedCard::from_id(id).with_energy(energy);
    let (meowth, bulbasaur) = (CardId::B2124Meowth, CardId::A1001Bulbasaur);
    let mut report = vec![];
    let mut check = |name: &str, got: String, want: &str| {
        let ok = got == want;
        report.push(format!("{} {name}: {got}{}", if ok { "ok  " } else { "FAIL" }, if ok { String::new() } else { format!(" (wanted {want})") }));
    };
    let show = |(f, u): (Vec<usize>, Vec<usize>)| format!("finite {f:?}, full {u:?}");

    // (site, attacker board, attack, hand, Meowth's slot, defenders with Meowth there, the same with Bulbasaur,
    //  wanted "queued / plain" with Meowth, wanted "queued / plain" without, the counter that keys on the mechanic)
    let sites: Vec<(&str, Vec<PlayedCard>, &str, Vec<CardId>, usize, Vec<PlayedCard>, Vec<PlayedCard>, &str, &str, &str)> = vec![
        ("Wild Swing (Gyarados A4 045), with the discard",
            vec![with(CardId::A4045Gyarados, vec![EnergyType::Water; 2]), mon(CardId::A1053Squirtle)], "Wild Swing", vec![], 0,
            vec![mon(meowth)], vec![mon(bulbasaur)], "1 / 0", "0 / 1", "offgate_discard_then_damage"),
        ("Wellspring Dance (Wellspring Mask Ogerpon B2 048), on its heads",
            vec![with(CardId::B2048WellspringMaskOgerpon, vec![EnergyType::Water; 2])], "Wellspring Dance", vec![], 1,
            vec![mon(bulbasaur), mon(meowth)], vec![mon(bulbasaur), mon(bulbasaur)], "1 / 0", "0 / 1", "offgate_helper_choice"),
        ("Tornado Shot (Rapid Strike Urshifu B3 051)",
            vec![with(CardId::B3051RapidStrikeUrshifu, vec![EnergyType::Water; 2])], "Tornado Shot", vec![], 1,
            vec![mon(bulbasaur), mon(meowth)], vec![mon(bulbasaur), mon(bulbasaur)], "1 / 0", "0 / 1", "offgate_helper_choice"),
        ("Double Splash (Blastoise B1a 019)",
            vec![with(CardId::B1a019Blastoise, vec![EnergyType::Water; 5])], "Double Splash", vec![], 1,
            vec![mon(bulbasaur), mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur), mon(bulbasaur)],
            "1 / 1", "0 / 2", "offgate_helper_choice"),
        ("Triple Bombardment (Mega Blastoise ex B1a 020)",
            vec![with(CardId::B1a020MegaBlastoiseEx, vec![EnergyType::Water; 6])], "Triple Bombardment", vec![], 1,
            vec![mon(bulbasaur), mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur), mon(bulbasaur)],
            "1 / 0", "0 / 1", "offgate_helper_choice"),
        ("Mischievous Ring (Hoopa B4 077)",
            vec![with(CardId::B4077Hoopa, vec![EnergyType::Psychic])], "Mischievous Ring", vec![], 0,
            vec![mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur)], "1 / 0", "0 / 1", "offgate_helper_choice"),
        ("Litter (Slowking A4a 018), 2 Tools discarded",
            vec![with(CardId::A4a018Slowking, vec![EnergyType::Water])], "Litter",
            vec![CardId::A2147GiantCape, CardId::A2148RockyHelmet], 0,
            vec![mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur)], "1 / 0", "0 / 1", "offgate_helper_choice"),
        ("Double-Punching Family's second punch (Mega Kangaskhan ex B2 127), into Togekiss",
            vec![with(CardId::B2127MegaKangaskhanEx, vec![EnergyType::Colorless; 3])], "Double-Punching Family", vec![], 0,
            vec![mon(CardId::A4080Togekiss), mon(bulbasaur)], vec![mon(CardId::PB024MegaLatiosEx), mon(bulbasaur)],
            "1 / 0", "0 / 1", "offgate_helper_choice"),
    ];
    for (site, attacker, title, hand, slot, on, off, want_on, want_off, counter) in sites {
        let (state, name) = damage_frame(&attacker, &on, &hand, title);
        let keyed = if HELPERS.contains(&name.as_str()) { "offgate_helper_choice" } else { "offgate_discard_then_damage" };
        check(&format!("{site}: mechanic {name}, off-gate counter"), keyed.to_string(), counter);
        check(&format!("{site}, the coin Pokemon in slot {slot}: queued offered / plain offered"),
            format!("{} / {}", queued_offered(&state, 1), plain_damage_offered(&state, 1)), want_on);
        let queued = state.generate_possible_actions().1.into_iter()
            .find(|a| matches!(a.action, SimpleAction::ApplyQueuedAttackDamage { .. }));
        let split = queued.map(|q| show(split_slots(&state, &q))).unwrap_or_else(|| "no queued choice".to_string());
        check(&format!("{site}: choosing it runs the coin split there"), split, &format!("finite [], full [{slot}]"));
        let (state, _) = damage_frame(&attacker, &off, &hand, title);
        check(&format!("{site}, no coin Pokemon there: queued offered / plain offered"),
            format!("{} / {}", queued_offered(&state, 1), plain_damage_offered(&state, 1)), want_off);
    }

    let failures = report.iter().filter(|l| l.starts_with("FAIL")).count();
    for line in &report {
        println!("{line}");
    }
    println!("{} checks, {failures} failures", report.len());
    assert_eq!(failures, 0);
}
