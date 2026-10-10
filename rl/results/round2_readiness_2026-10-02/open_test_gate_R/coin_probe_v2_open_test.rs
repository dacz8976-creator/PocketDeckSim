//! coin_probe v2 (the cloud, Oct 2; round-2 readiness, job 3). v1 is `../engine_switch_rules_2026-10/coin_probe.rs`, unchanged.
//! v2 counts plies as km3's and k3's own search does (`expectiminimax_player.rs` on the official engine, main-8626a35):
//!   - the root move costs a ply, whatever its frame (the root scores each move with max_depth - 1 more plies, 257-275);
//!   - a forced continuation costs none, whoever is to move (631-655): the top frame is exactly one EndTurn,
//!     ResolveKnockoutPoints, ResolveAttackRetaliation, ResolvePokemonCheckup, FinishPokemonCheckup or ResolveEndTurnEvolution,
//!     or the stack is empty with end_turn_pending; so the search crosses the forced end of the opponent's turn;
//!   - a free frame costs none (659-704): a pending Victory Star, Misty-target or Trainer coin choice, or a frame of only
//!     ApplyQueuedAttackDamage and ChooseRandomEvolutionTarget choices; nor does a promotion frame (707-748);
//!   - then the search stops where the bots stop: when the current player is not the mover (the hidden-hand guard, 750-774,
//!     where the k-tiers stop at the turn boundary) and when 3 plies are spent (depth 0);
//!   - every other move costs a ply, the opponent's forced choices during the mover's turn included (960-1010), and a voluntary
//!     EndTurn too (it is searched last).
//! A finite cut recorded by a move in a free frame is reported at the ply already spent (the move costs none). Everything else is
//! v1's: the conditions, the 12 chance samples per move, the node limit (60,000; `--node-limit N` sets another, for a search
//! that stops there) and the output format.
//! Built as v1 is (below), from this file: cp coin_probe_v2.rs engine/examples/ && (cd engine && cargo build --release --locked
//! --features test-utils --example coin_probe_v2), in a scratch copy of the official engine (main-8626a35).
//!   coin_probe_v2 --a <list> --b <list> --seed-base <n> --pairing <n> --bot km3 --deal <i> --tick <t> [--node-limit <n>]
//!
//! v1's notes follow.
//! Step 8c of the rules switch, the coin repair's side (Oct 1; scratch, diagnosis only; no change in engine/). The counterpart of
//! `vs_probe.rs` (victory_star_repair_2026-09-30/smoke/rerun_R/): "in lookahead only" counts as an explanation of a changed game only
//! if both halves hold, the code gate (read in the code) and a trace showing the gate's condition inside the bot's search depth at
//! the game's first differing tick. This is the second half for repair B.
//!
//! Given a game, a deal and the first differing tick, it replays the game on R (the two engines agree up to that tick), then searches
//! the mover's own consecutive moves from there, up to kog3's depth of 3 plies, for repair B's conditions:
//!   QUEUED: a queued coin-path choice is offered: an ApplyQueuedAttackDamage at one of the five coin-Ability Pokemon (Bastiodon
//!     A2 114, Hisuian Goodra B3b 050, Togekiss A4 080, Meowth B2 124 / B2 204) whose attack's mechanic is not
//!     AlsoChoiceBenchDamage[Filtered] (which queued it on the old engine too). This is F5's `coin_queued_offered`.
//!   CUT: a finite heads cut is recorded: applying an Attack or a queued choice whose forecast has more branches than the same move
//!     with the Bastiodon or Goodra replaced by a Bulbasaur (the coin split ran for it). This is F5's `coin_cut_recorded`.
//! It prints, for each condition, the shortest path to it (as plies of the mover's own moves, the first move being ply 1) and says
//! whether that is inside the search: a state reached after p applied moves is in the tree if p <= 3; a move chosen at ply p is in
//! it if p <= 3. At p = 3 for QUEUED the state is the tree's last node, and whether the offered choice is priced there depends on
//! its frame. A frame made only of ApplyQueuedAttackDamage choices is a "pure" frame: the bots resolve it at once without
//! spending a ply ("a queued attack-damage target [is] part of the attack already being priced", expectiminimax_player.rs:659-673
//! and value_function_player.rs:93-110), so the choice is inside the search even at ply 3. A mixed frame (some plain ApplyDamage
//! beside the queued choice) is an ordinary move: at ply 3 it is offered at the leaf and never applied, the leaf's value does not
//! read it, and the output says "AT THE LEAF": the verdict then needs a judgment (PLAN.md: anything that does is Dustin's).
//! Chance is sampled (12 outcomes per move, from the probe's own seeded RNG; the game's is never touched), so a path found has
//! positive probability; one not found is not a proof of absence, and the output says so.
//!   coin_probe --a fire_heatmor.txt --b meowth_carefree.txt --seed-base 20950000000 --bot kog3 --deal 2 --tick 27
//!   coin_probe --selftest        (constructed boards with known answers; needs the test-utils feature)
//! Built as an example in a scratch copy of R's engine (git archive, never in the repository's tree), run from that copy's engine/:
//!   cp coin_probe.rs engine/examples/ && (cd engine && cargo build --release --locked --features test-utils --example coin_probe)
//! `coin_lookahead.py` (this folder) drives it over every changed game of a smoke and checks it against S3's hand-traced ticks.
use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::players::{create_players, parse_player_code};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::{Deck, Game, State};
use rand::{rngs::StdRng, SeedableRng};
use std::collections::BTreeMap;

const FINITE: [&str; 2] = ["A2 114", "B3b 050"];
const FULL: [&str; 3] = ["A4 080", "B2 124", "B2 204"];
const SEEDS: u64 = 12;
const SEARCH_PLIES: usize = 3;
const NODE_LIMIT: usize = 60_000;
/// The node limit in force: NODE_LIMIT (v1's), unless `--node-limit N` sets another.
static LIMIT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(NODE_LIMIT);

fn limit() -> usize {
    LIMIT.load(std::sync::atomic::Ordering::Relaxed)
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn short(a: &Action) -> String {
    let s = format!("{:?}", a.action);
    if s.chars().count() > 90 { format!("{}...", s.chars().take(87).collect::<String>()) } else { s }
}

fn mechanic_of(attack: &deckgym::models::Attack) -> String {
    attack.effect.as_deref().and_then(|e| deckgym::actions::EFFECT_MECHANIC_MAP.get(e))
        .map(|m| format!("{m:?}").chars().take_while(|c| c.is_alphanumeric()).collect::<String>())
        .unwrap_or_default()
}

fn is_coin(state: &State, player: usize, idx: usize) -> bool {
    state.in_play_pokemon[player].get(idx).and_then(|p| p.as_ref())
        .is_some_and(|p| FINITE.contains(&p.card.get_id().as_str()) || FULL.contains(&p.card.get_id().as_str()))
}

/// Whether `a` is a queued coin-path choice at a coin Pokemon of `actor`'s opponent (F5's coin_queued_offered).
fn is_queued_coin(state: &State, actor: usize, a: &Action) -> bool {
    match &a.action {
        SimpleAction::ApplyQueuedAttackDamage { attack, targets } => {
            !mechanic_of(attack).starts_with("AlsoChoiceBenchDamage")
                && targets.iter().any(|(_, is_opp, i)| *is_opp && is_coin(state, 1 - actor, *i))
        }
        _ => false,
    }
}

/// The slots of `actor`'s opponent whose finite coin cut is recorded when `action` is chosen (F5's coin_cut_recorded).
fn finite_cut_slots(state: &State, action: &Action) -> Vec<usize> {
    let opp = 1 - action.actor;
    let branches = |s: &State| try_forecast_action(s, action).ok().map(|o| o.into_branches().0.len());
    let mut out = vec![];
    let Some(n_real) = branches(state) else { return out };
    for i in 0..state.in_play_pokemon[opp].len() {
        let Some(id) = state.in_play_pokemon[opp].get(i).and_then(|p| p.as_ref()).map(|p| p.card.get_id()) else { continue };
        if !FINITE.contains(&id.as_str()) {
            continue;
        }
        let mut without = state.clone();
        without.in_play_pokemon[opp][i] = Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
        if branches(&without).is_some_and(|n| n < n_real) {
            out.push(i);
        }
    }
    out
}

/// States reached by `action` from `state`, one per sampled chance outcome, deduplicated by their serialised form.
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

type Example = (Vec<String>, String);
#[derive(Default)]
struct Found {
    /// kind -> ply -> up to three examples; the ply is the number of the mover's moves applied (QUEUED, the offered state's depth)
    /// or the move's own number (CUT, the move chosen at that ply).
    by_kind: BTreeMap<&'static str, BTreeMap<usize, Vec<Example>>>,
    /// The plies at which a QUEUED state was found whose frame is pure (every offered move is an ApplyQueuedAttackDamage or a
    /// ChooseRandomEvolutionTarget), which the bots resolve at once, without spending a ply.
    pure_plies: std::collections::BTreeSet<usize>,
    gate_plies: std::collections::BTreeSet<usize>,
    nodes: usize,
    truncated: bool,
}

/// The bots' own test (expectiminimax_player.rs:663-673): the offered moves are all stack choices of these two kinds.
fn pure_queued_frame(actions: &[Action]) -> bool {
    !actions.is_empty()
        && actions.iter().all(|a| a.is_stack && matches!(a.action, SimpleAction::ApplyQueuedAttackDamage { .. } | SimpleAction::ChooseRandomEvolutionTarget { .. }))
}

/// The result of a probe: the shortest ply of each condition, and whether the shortest QUEUED frame is one the bots resolve at once.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Least {
    queued: Option<usize>,
    cut: Option<usize>,
    queued_free: bool,
}

impl Found {
    fn add(&mut self, kind: &'static str, ply: usize, path: &[String], detail: String) {
        let e = self.by_kind.entry(kind).or_default().entry(ply).or_default();
        if e.len() < 3 {
            e.push((path.to_vec(), detail));
        }
    }
}

/// The bots' forced-continuation test (expectiminimax_player.rs 631-645), read from the state (end_turn_pending through its
/// serialised form, the field being crate-private).
fn forced_continuation(state: &State) -> bool {
    state.turn_count > 0
        && match state.move_generation_stack.last() {
            Some((_, choices)) => matches!(choices.as_slice(), [SimpleAction::EndTurn
                | SimpleAction::ResolveKnockoutPoints { .. }
                | SimpleAction::ResolveAttackRetaliation { .. }
                | SimpleAction::ResolvePokemonCheckup
                | SimpleAction::FinishPokemonCheckup
                | SimpleAction::ResolveEndTurnEvolution { .. }]),
            None => serde_json::to_value(state).ok().and_then(|v| v.get("end_turn_pending").and_then(|b| b.as_bool()))
                .expect("State serialises end_turn_pending"),
        }
}

/// The bots' free frames (659-704): a pending coin choice, or a frame of only queued attack damage and random evolution targets.
fn free_frame(state: &State, actions: &[Action]) -> bool {
    state.pending_attack_coin_choice.is_some()
        || state.pending_misty_target_choice.is_some()
        || state.pending_trainer_coin_choice.is_some()
        || pure_queued_frame(actions)
}

/// The bots' promotion frame (`is_current_promotion_frame`, 204-235): the frame's player has an empty Active and every choice is
/// that player's Promote.
fn promotion_frame(state: &State, mover: usize, actions: &[Action]) -> bool {
    state.turn_count > 0
        && !state.setup_opponent_hidden
        && !actions.is_empty()
        && state.in_play_pokemon[mover][0].is_none()
        && actions.iter().all(|a| a.is_stack && matches!(a.action, SimpleAction::Promote { player, .. } if player == mover))
}

/// The actor's attacks chosen now whose own damage records a finite cut, at ply `ply`.
fn attack_cuts(state: &State, actions: &[Action], ply: usize, path: &[String], found: &mut Found) {
    if ply > SEARCH_PLIES {
        return;
    }
    for a in actions.iter().filter(|a| matches!(a.action, SimpleAction::Attack(_)) && !a.is_stack) {
        let slots = finite_cut_slots(state, a);
        if !slots.is_empty() {
            let mut p = path.to_vec();
            p.push(short(a));
            found.add("CUT", ply, &p, format!("the attack's own damage, finite cut at slot(s) {slots:?}"));
        }
    }
}

/// Every action, EndTurn last (a voluntary pass is searched, but after everything else, as v1 left it out).
fn ordered(actions: &[Action]) -> Vec<&Action> {
    let mut out: Vec<&Action> = actions.iter().filter(|a| !matches!(a.action, SimpleAction::EndTurn)).collect();
    out.extend(actions.iter().filter(|a| matches!(a.action, SimpleAction::EndTurn)));
    out
}

/// `plies`: the plies the bots have spent to reach `state`; `root`: the probed state itself (its every move costs a ply).
fn explore(state: &State, actor: usize, plies: usize, root: bool, path: &mut Vec<String>, found: &mut Found) {
    found.nodes += 1;
    if found.nodes > limit() {
        found.truncated = true;
        return;
    }
    if state.winner.is_some() {
        return;
    }
    let (mover, actions) = state.generate_possible_actions();
    if actions.is_empty() {
        return;
    }
    let pure = pure_queued_frame(&actions);
    // Open test (scratch): R's PGGATE, a pure queued frame of any mover with a coin Pokemon of either side among its targets.
    if pure && actions.iter().any(|a| match &a.action {
        SimpleAction::ApplyQueuedAttackDamage { targets, .. } =>
            targets.iter().any(|(_, is_opp, i)| is_coin(state, if *is_opp { 1 - mover } else { mover }, *i)),
        _ => false,
    }) {
        found.gate_plies.insert(plies);
    }
    // QUEUED: the actor's frame offers a queued coin-path choice, after `plies` plies.
    if mover == actor {
        let queued: Vec<&Action> = actions.iter().filter(|a| is_queued_coin(state, actor, a)).collect();
        if !queued.is_empty() {
            if pure {
                found.pure_plies.insert(plies);
            }
            found.add("QUEUED", plies, path, format!("offers {} ({})", queued.iter().map(|a| short(a)).collect::<Vec<_>>().join(" | "),
                if pure { "a pure frame: the bots resolve it without spending a ply" } else { "a mixed frame: an ordinary move" }));
            let cost = if pure && !root { 0 } else { 1 };
            if plies + cost <= SEARCH_PLIES {
                for a in &queued {
                    let slots = finite_cut_slots(state, a);
                    if !slots.is_empty() {
                        let mut p = path.clone();
                        p.push(short(a));
                        found.add("CUT", plies + cost, &p, format!("the queued choice's finite cut at slot(s) {slots:?}"));
                    }
                }
            }
            if std::env::var_os("GATE_WALK").is_none() {
                return;
            }
        }
    }
    let step = |a: &Action, next_plies: usize, label: String, path: &mut Vec<String>, found: &mut Found| {
        for next in successors(state, a) {
            path.push(label.clone());
            explore(&next, actor, next_plies, false, path, found);
            path.pop();
        }
    };
    if root {
        if mover == actor {
            attack_cuts(state, &actions, plies + 1, path, found);
        }
        for a in ordered(&actions) {
            step(a, plies + 1, short(a), path, found);
        }
        return;
    }
    if forced_continuation(state) && actions.len() == 1 {
        if path.iter().filter(|m| m.starts_with("(free)")).count() < 16 {
            step(&actions[0], plies, format!("(free) {}", short(&actions[0])), path, found);
        }
        return;
    }
    if free_frame(state, &actions) || promotion_frame(state, mover, &actions) {
        if path.iter().filter(|m| m.starts_with("(free)")).count() < 16 {
            for a in ordered(&actions) {
                step(a, plies, format!("(free) {}", short(a)), path, found);
            }
        }
        return;
    }
    if state.current_player != actor || plies >= SEARCH_PLIES {
        return;
    }
    if mover == actor {
        attack_cuts(state, &actions, plies + 1, path, found);
    }
    for a in ordered(&actions) {
        step(a, plies + 1, short(a), path, found);
    }
}

/// Prints the result and returns the shortest ply of each condition, if any.
fn report(found: &Found, label: &str) -> Least {
    let mut least = Least { queued: None, cut: None, queued_free: false };
    println!("{label}PURE_PLIES {:?}", found.pure_plies);
    println!("{label}GATE_PLIES {:?}", found.gate_plies);
    for (kind, by_ply) in &found.by_kind {
        let ply = *by_ply.keys().next().unwrap();
        match *kind {
            "QUEUED" => {
                least.queued = Some(ply);
                least.queued_free = found.pure_plies.contains(&ply);
            }
            _ => least.cut = Some(ply),
        }
        let inside = if *kind == "QUEUED" && ply == SEARCH_PLIES && !found.pure_plies.contains(&ply) {
            "inside the tree but AT THE LEAF (a mixed frame: offered, never applied: a judgment)"
        } else if *kind == "QUEUED" && ply == SEARCH_PLIES {
            "INSIDE THE SEARCH (at the leaf, but a pure frame: resolved without a ply)"
        } else if ply <= SEARCH_PLIES { "INSIDE THE SEARCH" } else { "beyond the search" };
        let what = if *kind == "QUEUED" { format!("a queued coin-path choice is offered after {ply} move(s)") }
                   else { format!("a finite heads cut is recorded by the move chosen at ply {ply}") };
        println!("{label}{kind}: {what}: {inside}");
        for (path, detail) in by_ply.values().next().unwrap() {
            println!("    after [{}] {detail}", path.join(" ; "));
        }
    }
    if found.by_kind.is_empty() {
        println!("{label}NOT FOUND: neither a queued coin-path choice nor a finite heads cut within {SEARCH_PLIES} plies ({SEEDS} chance samples per move; not a proof of absence)");
    }
    if found.truncated {
        println!("{label}(the search stopped at {} nodes)", limit());
    }
    least
}

fn probe_state(state: &State, label: &str) -> Least {
    let (actor, offered) = state.generate_possible_actions();
    println!("{label}mover seat {actor}, turn {}; Active {}; {} offered moves", state.turn_count,
        state.maybe_get_active(actor).map_or("-".to_string(), |p| p.get_name()), offered.len());
    let mut found = Found::default();
    explore(state, actor, 0, true, &mut vec![], &mut found);
    report(&found, label)
}

fn selftest() {
    let mon = PlayedCard::from_id;
    let check = |name: &str, got: Least, want: (Option<usize>, Option<usize>)| {
        println!("{} {name}: queued {:?} (free {}), cut {:?}", if (got.queued, got.cut) == want { "ok  " } else { "FAIL" }, got.queued, got.queued_free, got.cut);
        assert_eq!((got.queued, got.cut), want, "{name}");
    };
    let board = |attacker: PlayedCard, defenders: Vec<PlayedCard>| {
        let mut game = get_initialized_game_with_board(5, 1, 5, defenders, vec![attacker]);
        let mut state = game.get_state_clone();
        state.current_player = 1;
        game.set_state(state);
        game.get_state_clone()
    };
    // A: Fire Claws into Bastiodon's Active: the attack itself records the finite cut, chosen at ply 1; nothing is queued.
    let claws = PlayedCard::from_id(CardId::A1034Charmeleon).with_energy(vec![EnergyType::Fire; 3]);
    check("Fire Claws into Bastiodon", probe_state(&board(claws.clone(), vec![mon(CardId::A2114Bastiodon)]), "  A "), (None, Some(1)));
    // B: Tongue Whip with Bastiodon on the Bench: the attack (ply 1) offers the queued choice at a state of depth 1, and choosing it
    // (ply 2) records the cut. A Togekiss on the Bench queues the same way and records no finite cut.
    let whip = || PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire]);
    let b = probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A2114Bastiodon)]), "  B ");
    check("Tongue Whip, Bastiodon on the Bench", b, (Some(1), Some(2)));
    assert!(!b.queued_free, "the frame has a plain ApplyDamage beside the queued choice: a mixed frame");
    check("Tongue Whip, Togekiss on the Bench",
        probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A4080Togekiss)]), "  C "), (Some(1), None));
    // F: a lone Togekiss on the Bench: every choice of the frame is queued, a pure frame the bots resolve without a ply.
    let f = probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A4080Togekiss)]), "  F ");
    check("Tongue Whip, a lone Togekiss on the Bench (a pure frame)", f, (Some(1), None));
    assert!(f.queued_free, "every choice is a queued one: a pure frame");
    // G (v2): a lone Bastiodon on the Bench: a pure frame, whose queued choice costs no ply, so its finite cut is at ply 1 (v1: 2).
    let g = probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A2114Bastiodon)]), "  G ");
    check("Tongue Whip, a lone Bastiodon on the Bench (a pure frame: the cut costs no ply)", g, (Some(1), Some(1)));
    assert!(g.queued_free, "every choice is a queued one: a pure frame");
    // D: nothing to find without a coin Pokemon.
    check("Tongue Whip, no coin Pokemon",
        probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur)]), "  D "), (None, None));
    // E: the queued choice already offered at the tick (the state after the attack): depth 0, the S3 pattern.
    let mut game = get_initialized_game_with_board(5, 1, 5,
        vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A4080Togekiss)], vec![whip()]);
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state.clone());
    let attack = state.generate_possible_actions().1.into_iter()
        .find(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == "Tongue Whip")).expect("Tongue Whip");
    game.apply_action(&attack);
    check("the state after Tongue Whip (the choice is on the table)", probe_state(&game.get_state_clone(), "  E "), (Some(0), None));
    println!("selftest: 7 checks and 3 frame checks, 0 failures");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a == "--selftest") {
        return selftest();
    }
    let deck_a = Deck::from_file(&arg(&args, "--a").expect("--a")).expect("deck a");
    let deck_b = Deck::from_file(&arg(&args, "--b").expect("--b")).expect("deck b");
    let seed_base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let pairing: u64 = arg(&args, "--pairing").map(|x| x.parse().unwrap()).unwrap_or(0);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kog3".into());
    let i: u64 = arg(&args, "--deal").expect("--deal").parse().unwrap();
    let tick: usize = arg(&args, "--tick").expect("--tick").parse().unwrap();
    if let Some(n) = arg(&args, "--node-limit") {
        LIMIT.store(n.parse().unwrap(), std::sync::atomic::Ordering::Relaxed);
    }
    let seed = seed_base + pairing * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (&deck_a, &deck_b) } else { (&deck_b, &deck_a) };
    let code = || parse_player_code(&bot).unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![code(), code()]), seed);
    for _ in 0..tick {
        assert!(!game.is_game_over(), "the game ended before tick {tick}");
        game.play_tick();
    }
    println!("deal {i}, tick {tick}:");
    let least = probe_state(&game.get_state_clone(), "  ");
    let show = |p: Option<usize>| p.map_or("none".to_string(), |p| p.to_string());
    println!("RESULT queued={} cut={} free={}", show(least.queued), show(least.cut), least.queued_free);
}
