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

fn explore(state: &State, actor: usize, path: &mut Vec<String>, found: &mut Found) {
    found.nodes += 1;
    if found.nodes > NODE_LIMIT {
        found.truncated = true;
        return;
    }
    let depth = path.len();
    let (mover, actions) = state.generate_possible_actions();
    if mover != actor {
        return;
    }
    // QUEUED: the state after `depth` moves offers a queued coin-path choice.
    let queued: Vec<&Action> = actions.iter().filter(|a| is_queued_coin(state, actor, a)).collect();
    if !queued.is_empty() {
        let pure = pure_queued_frame(&actions);
        if pure {
            found.pure_plies.insert(depth);
        }
        found.add("QUEUED", depth, path, format!("offers {} ({})", queued.iter().map(|a| short(a)).collect::<Vec<_>>().join(" | "),
            if pure { "a pure frame: the bots resolve it without spending a ply" } else { "a mixed frame: an ordinary move" }));
        if depth + 1 <= SEARCH_PLIES {
            for a in &queued {
                let slots = finite_cut_slots(state, a);
                if !slots.is_empty() {
                    let mut p = path.clone();
                    p.push(short(a));
                    found.add("CUT", depth + 1, &p, format!("the queued choice's finite cut at slot(s) {slots:?}"));
                }
            }
        }
        return;
    }
    // CUT: an Attack chosen now (ply depth + 1) whose own damage splits for a finite-cut Pokemon.
    if depth + 1 <= SEARCH_PLIES {
        for a in actions.iter().filter(|a| matches!(a.action, SimpleAction::Attack(_)) && !a.is_stack) {
            let slots = finite_cut_slots(state, a);
            if !slots.is_empty() {
                let mut p = path.clone();
                p.push(short(a));
                found.add("CUT", depth + 1, &p, format!("the attack's own damage, finite cut at slot(s) {slots:?}"));
            }
        }
    }
    if depth >= SEARCH_PLIES {
        return;
    }
    for a in actions.iter().filter(|a| !matches!(a.action, SimpleAction::EndTurn)) {
        for next in successors(state, a) {
            if next.current_player != state.current_player || next.turn_count != state.turn_count {
                continue;
            }
            path.push(short(a));
            explore(&next, actor, path, found);
            path.pop();
        }
    }
}

/// Prints the result and returns the shortest ply of each condition, if any.
fn report(found: &Found, label: &str) -> Least {
    let mut least = Least { queued: None, cut: None, queued_free: false };
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
        println!("{label}(the search stopped at {NODE_LIMIT} nodes)");
    }
    least
}

fn probe_state(state: &State, label: &str) -> Least {
    let (actor, offered) = state.generate_possible_actions();
    println!("{label}mover seat {actor}, turn {}; Active {}; {} offered moves", state.turn_count,
        state.maybe_get_active(actor).map_or("-".to_string(), |p| p.get_name()), offered.len());
    let mut found = Found::default();
    explore(state, actor, &mut vec![], &mut found);
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
    println!("selftest: 6 checks and 2 frame checks, 0 failures");
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
