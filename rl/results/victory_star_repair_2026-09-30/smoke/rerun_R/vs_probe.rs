//! F6 of the rules switch (Oct 1; scratch, diagnosis only): the second half of "in lookahead only". At a game's first
//! differing tick (the two engines see the same board and the same offered moves and choose differently), is the repaired
//! code's gate within the bot's search depth? The probe replays the game on R to that tick (the engines agree up to it), then
//! searches the mover's own consecutive moves from there for a state in which a chosen Attack would build the Confusion-first
//! branch (F5's exact counter `vs_confusion_first_built`: a Confused Active's own attack whose forecast contains a Victory Star
//! pause), and prints the shortest paths it finds.
//!
//! "Depth" here counts plies of the mover's own moves. The bot is kog3, an expectiminimax player of depth 3, so the attack
//! itself is a ply: a gate state found after d earlier moves is inside the search when d + 1 <= 3, i.e. d <= 2. Chance is
//! sampled (SEEDS outcomes per move, from a seeded RNG of the probe's own; the game's RNG is never touched), so a path found
//! is one with positive probability, which is what "within the search" needs; a path not found within the samples is not a
//! proof of absence, and the output says so. It only reads: states are clones, forecasts are the engine's own.
//!   vs_probe --a fire_victini.txt --b psychic_confuse.txt --seed-base 20930000000 --bot kog3 --deal 0 --tick 31
use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game, State};
use rand::{rngs::StdRng, SeedableRng};
use std::collections::BTreeMap;

const SEEDS: u64 = 12;
const MAX_ACTIONS_BEFORE: usize = 2;

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn short(a: &Action) -> String {
    let s = format!("{:?}", a.action);
    if s.chars().count() > 90 { format!("{}...", s.chars().take(87).collect::<String>()) } else { s }
}

/// The titles of the attacks offered to `actor` in `state` that would build the Confusion-first branch if chosen.
fn building_attacks(state: &State, actor: usize) -> Vec<String> {
    let mut out = vec![];
    let Some(active) = state.maybe_get_active(actor) else { return out };
    if !active.is_confused() {
        return out;
    }
    let (mover, actions) = state.generate_possible_actions();
    if mover != actor {
        return out;
    }
    for a in actions.iter().filter(|a| !a.is_stack) {
        let SimpleAction::Attack(attack) = &a.action else { continue };
        let Ok(outcomes) = try_forecast_action(state, a) else { continue };
        let (_, mutations) = outcomes.into_branches();
        let built = mutations.into_iter().any(|mutate| {
            let mut branch = state.clone();
            mutate(&mut StdRng::seed_from_u64(0), &mut branch, a);
            branch.pending_attack_coin_choice.is_some()
        });
        if built {
            out.push(attack.title.clone());
        }
    }
    out
}

/// States reached by `action` from `state`, one per sampled chance outcome (deduplicated by their debug form).
fn successors(state: &State, action: &Action) -> Vec<State> {
    let mut seen = BTreeMap::new();
    for seed in 0..SEEDS {
        let Ok(outcomes) = try_forecast_action(state, action) else { return vec![] };
        let (probabilities, mutations) = outcomes.into_branches();
        for (p, mutate) in probabilities.iter().zip(mutations) {
            if *p <= 0.0 {
                continue;
            }
            let mut next = state.clone();
            mutate(&mut StdRng::seed_from_u64(1000 + seed), &mut next, action);
            seen.entry(serde_json::to_string(&next).unwrap_or_default()).or_insert(next);
        }
    }
    seen.into_values().collect()
}

fn explore(state: &State, actor: usize, path: &mut Vec<String>, before: usize, found: &mut BTreeMap<usize, Vec<(Vec<String>, Vec<String>)>>) {
    let titles = building_attacks(state, actor);
    if !titles.is_empty() {
        let e = found.entry(path.len()).or_default();
        if e.len() < 3 {
            e.push((path.clone(), titles));
        }
        return;
    }
    if before == 0 {
        return;
    }
    let (mover, actions) = state.generate_possible_actions();
    if mover != actor {
        return;
    }
    for a in actions.iter().filter(|a| !matches!(a.action, SimpleAction::EndTurn | SimpleAction::Attack(_))) {
        for next in successors(state, a) {
            if next.current_player != state.current_player || next.turn_count != state.turn_count {
                continue;
            }
            path.push(short(a));
            explore(&next, actor, path, before - 1, found);
            path.pop();
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_a = Deck::from_file(&arg(&args, "--a").expect("--a")).expect("deck a");
    let deck_b = Deck::from_file(&arg(&args, "--b").expect("--b")).expect("deck b");
    let seed_base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let pairing: u64 = arg(&args, "--pairing").map(|x| x.parse().unwrap()).unwrap_or(0);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kog3".into());
    let i: u64 = arg(&args, "--deal").expect("--deal").parse().unwrap();
    let tick: usize = arg(&args, "--tick").expect("--tick").parse().unwrap();
    let seed = seed_base + pairing * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (&deck_a, &deck_b) } else { (&deck_b, &deck_a) };
    let code = || parse_player_code(&bot).unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![code(), code()]), seed);
    for _ in 0..tick {
        assert!(!game.is_game_over(), "the game ended before tick {tick}");
        game.play_tick();
    }
    let state = game.get_state_clone();
    let (actor, offered) = state.generate_possible_actions();
    println!("deal {i}, tick {tick}, turn {}, mover seat {actor}; its Active is {} (Confused: {}); offered {} moves",
        state.turn_count,
        state.maybe_get_active(actor).map_or("-".to_string(), |p| p.get_name()),
        state.maybe_get_active(actor).is_some_and(|p| p.is_confused()), offered.len());
    for a in &offered {
        println!("  offered: {}", short(a));
    }
    let mut found = BTreeMap::new();
    explore(&state, actor, &mut vec![], MAX_ACTIONS_BEFORE, &mut found);
    if found.is_empty() {
        println!("NOT FOUND: no Confusion-first gate state within {MAX_ACTIONS_BEFORE} moves before the attack ({SEEDS} chance samples per move)");
    }
    for (depth, paths) in &found {
        println!("GATE WITHIN THE SEARCH: {depth} move(s) before the attack (attack = ply {}), e.g.:", depth + 1);
        for (path, titles) in paths {
            println!("  after [{}] the attack(s) {:?} would build the Confusion-first branch", path.join(" ; "), titles);
        }
    }
    // For the scripts: the fewest moves before an attack that builds the branch (0 = the branch is built by an attack offered at the
    // tick itself); anything found is inside kog3's three plies, as the search above stops at MAX_ACTIONS_BEFORE moves.
    println!("RESULT built={}", found.keys().next().map_or("none".to_string(), |depth| depth.to_string()));
}
