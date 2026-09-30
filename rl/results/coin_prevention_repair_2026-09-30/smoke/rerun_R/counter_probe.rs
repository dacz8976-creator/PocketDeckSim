//! F5 of the rules switch (Oct 1; scratch): the coin repair's exact counters on constructed boards. The coin smoke's decks hold
//! only Meowth (full prevention), so `coin_cut_recorded` (a heads finite cut on Bastiodon or Hisuian Goodra) had never fired on
//! a real board, and no list under `decks/` holds either. This example applies the counters' detection logic, the same as the
//! Rust that `instrument_scan.py` inserts (forecast of the chosen move with and without the coin Pokemon: more branches means
//! the coin split ran for it; the queued ApplyQueuedAttackDamage offered at a coin target, not AlsoChoiceBenchDamage[Filtered];
//! the off-gate ApplyDamage of a rewritten helper after its Attack), to boards built with `test_support`, and asserts what
//! each must read. It plays no game and needs the `test-utils` feature.
//!   cargo run --release --features test-utils --example counter_probe
use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::State;

const FINITE: [&str; 2] = ["A2 114", "B3b 050"];
const FULL: [&str; 3] = ["A4 080", "B2 124", "B2 204"];

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

fn board(attacker: PlayedCard, defenders: Vec<PlayedCard>) -> State {
    let mut state = get_initialized_game_with_board(1, 1, 5, defenders, vec![attacker]).get_state_clone();
    state.current_player = 1;
    state
}

fn main() {
    let claws = || PlayedCard::from_id(CardId::A1034Charmeleon).with_energy(vec![EnergyType::Fire; 3]);
    let mon = |id| PlayedCard::from_id(id);
    let mut report = vec![];
    let mut check = |name: &str, got: String, want: &str| {
        let ok = got == want;
        report.push(format!("{} {name}: {got}{}", if ok { "ok  " } else { "FAIL" }, if ok { String::new() } else { format!(" (wanted {want})") }));
    };
    let show = |(f, u): (Vec<usize>, Vec<usize>)| format!("finite {f:?}, full {u:?}");

    // 1-4: Fire Claws (60 damage) at the Active: a finite cut on Bastiodon and on Goodra, full prevention on Togekiss, nothing on Bulbasaur.
    for (name, id, want) in [
        ("Fire Claws into Bastiodon (Guarded Grill)", CardId::A2114Bastiodon, "finite [0], full []"),
        ("Fire Claws into Hisuian Goodra (Securely Sheltered)", CardId::B3b050HisuianGoodra, "finite [0], full []"),
        ("Fire Claws into Togekiss (Celestial Blessing)", CardId::A4080Togekiss, "finite [], full [0]"),
        ("Fire Claws into Meowth B2 124 (Carefree Steps)", CardId::B2124Meowth, "finite [], full [0]"),
        ("Fire Claws into Bulbasaur (no coin Ability)", CardId::A1001Bulbasaur, "finite [], full []"),
    ] {
        let state = board(claws(), vec![mon(id)]);
        let chosen = attack_named(&state, "Fire Claws");
        check(name, show(split_slots(&state, &chosen)), want);
    }

    // 5: per-target precision. Bastiodon Active and Togekiss on the Bench; Fire Claws hits only the Active.
    let state = board(claws(), vec![mon(CardId::A2114Bastiodon), mon(CardId::A4080Togekiss)]);
    check("Fire Claws into Bastiodon with Togekiss on the Bench (only the Active takes damage)",
        show(split_slots(&state, &attack_named(&state, "Fire Claws"))), "finite [0], full []");

    // 6: an attack with no damage of its own at a coin Pokemon: no split (the engine splits only a Pokemon that takes damage).
    let moltres = PlayedCard::from_id(CardId::B4a007TeamRocketsMoltresEx).with_energy(vec![EnergyType::Fire]);
    let state = board(moltres, vec![mon(CardId::A2114Bastiodon)]);
    check("Heat Charged (no damage) into Bastiodon", show(split_slots(&state, &attack_named(&state, "Heat Charged"))), "finite [], full []");

    // 7-9: Heatmor's Tongue Whip (30 to a Benched Pokemon, a DirectDamage helper) with Bastiodon and Bulbasaur on the Bench.
    let heatmor = PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire]);
    let mut game = get_initialized_game_with_board(2, 1, 5,
        vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A2114Bastiodon)], vec![heatmor]);
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state.clone());
    let whip = attack_named(&state, "Tongue Whip");
    check("Tongue Whip itself (no own damage) with a coin Pokemon on the Bench", show(split_slots(&state, &whip)), "finite [], full []");
    game.apply_action(&whip);
    let after = game.get_state_clone();
    check("queued choices offered after Tongue Whip at the coin Pokemon (coin_queued_offered)", queued_offered(&after, 1).to_string(), "1");
    check("plain ApplyDamage choices offered after it, for the other Bench slot (offgate_helper_choice's source)",
        plain_damage_offered(&after, 1).to_string(), "1");
    let queued = after.generate_possible_actions().1.into_iter().find(|a| matches!(a.action, SimpleAction::ApplyQueuedAttackDamage { .. })).expect("queued choice");
    check("choosing the queued choice: the finite cut is recorded for the Bench Bastiodon", show(split_slots(&after, &queued)), "finite [2], full []");

    // 10: with no coin Pokemon on the Bench every choice is plain and none is queued.
    let mut game = get_initialized_game_with_board(3, 1, 5,
        vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire])]);
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state.clone());
    game.apply_action(&attack_named(&state, "Tongue Whip"));
    let after = game.get_state_clone();
    check("Tongue Whip with no coin Pokemon: queued offered / plain offered", format!("{} / {}", queued_offered(&after, 1), plain_damage_offered(&after, 1)), "0 / 2");

    let failures = report.iter().filter(|l| l.starts_with("FAIL")).count();
    for line in &report {
        println!("{line}");
    }
    println!("{} checks, {failures} failures", report.len());
    assert_eq!(failures, 0);
}
