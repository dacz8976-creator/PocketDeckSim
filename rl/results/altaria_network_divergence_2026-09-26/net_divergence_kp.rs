//! B2c for the Altaria detector network (Sept 26): where does the network choose differently from kp3, and which
//! choice wins more when kp3 plays on? The Lucario study's method (engine/examples/net_divergence.rs at 6a9fa90),
//! with kp3 as the pilot everywhere: the probe, and the continuation for both decks.
//!
//!   net_divergence_kp --games-file kp3_rows_games.jsonl --decks <folder with altaria.txt and lucario.txt>
//!       [--first 0] [--games 400] [--probes 3] [--rollouts 8] [--out decisions.jsonl] [--sync-only]
//!
//! Not part of the engine: rl/results/altaria_network_divergence_2026-09-26/build_b2c.sh copies this file into a
//! scratch copy of the engine at 7fc6ccb as engine/examples/net_divergence_kp.rs and builds it there.
//!
//! Input: rl/results/altaria_network_readout/kp3_rows_games.jsonl, the row 'net|kp3' only: the Altaria detector
//! network (ckpt_1800k_avg_altaria) against kp3 piloting Lucario on the run's bar deals, seed 18,200,000,000 + i,
//! bar seats. Each line holds only the network's chosen index at each of its decisions ("moves"); kp3's moves and
//! the forced moves were never recorded, so they are re-played here exactly as the add-on played them
//! (pdl_rl_env's RawEnv::advance): Game::new(seed) with kp3 in Lucario's seat and a never-called placeholder (R) in
//! Altaria's; a Lucario move is Game::play_tick; an Altaria position with one canonical move is applied as forced;
//! an Altaria position with two or more is a network decision, and the recorded index is applied.
//!
//! A game is in sync only if every recorded index is offered (it is below the number of canonical moves), the engine
//! asks for exactly as many network decisions as were recorded, the final winner, points and turn equal the record,
//! and the per-game counts the readout kept (attacking and benching on offered turns, readout.py's "habits", and the
//! bench size at each Mega Harmony) equal the counts recomputed here. A game out of sync is rejected and counted.
//!
//! At each network decision kp3 is asked for its move from the same view (Game::observation of Altaria's seat)
//! under `--probes` search seeds. Where kp3's first-probe move differs from the network's (by card names: a Basic
//! onto either empty Bench slot is the same move) and the network doesn't play kp3's move later in the same turn
//! (an order-only difference), both moves are played out `--rollouts` times from that position with kp3 piloting
//! both decks afterwards, the two moves sharing each chance seed. The value is Altaria's score (win 1, tie 0.5)
//! after the network's move minus after kp3's move: what kp3 itself would gain by making the network's move there.
//!
//! Seeds (game i = seed - 18,200,000,000, network decision j of that game): kp3 probes 21,160,000,000 + i x 100,000
//! + j x 10 + probe; play-outs 21,110,000,000 + i x 100,000 + j x 100 + r (probe < 10, r < 100, j < 1,000).
//! With i < 400 the play-outs stay below 21,150,000,000 and the probes below 21,200,000,000.

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::canonical_actions;
use deckgym::players::{create_players, PlayerCode};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;
use std::collections::{BTreeMap, HashMap};
use std::io::BufRead;
use std::time::Instant;

const KP3: PlayerCode = PlayerCode::KP { max_depth: 3 };
const ROW: &str = "net|kp3";
const DEAL_BASE: u64 = 18_200_000_000;
const ROLLOUT_BASE: u64 = 21_110_000_000;
const PROBE_BASE: u64 = 21_160_000_000;
/// readout.py's bench attack (A["bench_attack"]): the bench size is counted when it is used.
const BENCH_ATTACK: &str = "Mega Harmony";
/// The knockout audit's "sure knockout" (pdl_rl_env action_outcomes): copies of the true game, R players.
const KO_COPIES: u64 = 4;
const KO_SEED: u64 = 0x5eed_0000;

#[derive(serde::Deserialize, Clone, Copy, PartialEq, Eq, Debug, Default)]
struct Habits {
    turns: u32,
    attack_turns: u32,
    attack_made: u32,
    bench_turns: u32,
    bench_made: u32,
}

#[derive(serde::Deserialize)]
struct Count {
    habits: Habits,
    bench_at: [u32; 4],
}

#[derive(serde::Deserialize)]
struct Recorded {
    row: String,
    seed: u64,
    decks: [String; 2],
    winner: i64,
    points: [u8; 2],
    turns: u8,
    moves: Vec<usize>,
    count: Option<Count>,
}

struct Position {
    i: u64,
    j: usize,
    state: State,
    net: Action,
    kp3: Action,
}

struct Replay {
    records: Vec<serde_json::Value>,
    positions: Vec<Position>,
    problem: Option<String>,
}

fn name_at(state: &State, player: usize, idx: usize) -> String {
    state.in_play_pokemon[player].get(idx).and_then(|s| s.as_ref()).map(|p| p.get_name())
        .unwrap_or_else(|| format!("slot {idx}"))
}

fn active_name(state: &State, player: usize) -> Option<String> {
    state.in_play_pokemon[player][0].as_ref().map(|p| p.get_name())
}

/// The move by card names. As the Lucario tool's label, except that a promotion or switch names its Pokemon instead
/// of its slot, and a move into or onto the Active Spot is marked "(active)": a Basic placed there, and (review, Sept
/// 26) Energy, a Tool, an evolution or an ability on the Active. The list has two each of Swablu, Eevee, Espeon and
/// Darkrai, so without the mark Energy onto the Active Swablu and onto a Benched Swablu read as the same move and
/// were never played out, which is habit 4's own question.
fn label(state: &State, action: &Action) -> String {
    let me = action.actor;
    let at = |idx: usize| format!("{}{}", name_at(state, me, idx), if idx == 0 { " (active)" } else { "" });
    match &action.action {
        SimpleAction::Play { trainer_card } => format!("play {}", trainer_card.name),
        SimpleAction::Attack(atk) => format!("attack {} ({})", atk.title, name_at(state, me, 0)),
        SimpleAction::UseAbility { in_play_idx } => format!("ability of {}", at(*in_play_idx)),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => {
            format!("evolve {} into {}", at(*in_play_idx), evolution.get_name())
        }
        SimpleAction::Place(card, idx) => {
            format!("place {}{}", card.get_name(), if *idx == 0 { " (active)" } else { "" })
        }
        SimpleAction::AttachTool { tool_card, in_play_idx } => {
            format!("attach {} to {}", tool_card.get_name(), at(*in_play_idx))
        }
        SimpleAction::Attach { attachments, .. } => {
            let to: Vec<String> = attachments.iter()
                .map(|(n, e, idx)| format!("{n} {e:?} to {}", at(*idx))).collect();
            format!("attach {}", to.join(", "))
        }
        SimpleAction::Retreat(idx) => format!("retreat to {}", name_at(state, me, *idx)),
        SimpleAction::Promote { player, in_play_idx } => format!("promote {}", name_at(state, *player, *in_play_idx)),
        SimpleAction::Activate { player, in_play_idx } => format!("switch to {}", name_at(state, *player, *in_play_idx)),
        SimpleAction::EndTurn => "end turn".into(),
        other => format!("{other:?}").chars().take(80).collect(),
    }
}

/// The knockout audit's rule: in each of KO_COPIES copies of the true game under different chance seeds, the move
/// gains its player at least one point (analysis only; the game is not touched).
fn sure_ko(state: &State, seat_decks: &[Deck; 2], action: &Action) -> bool {
    let before = state.points[action.actor];
    (0..KO_COPIES).all(|s| {
        let players = create_players(seat_decks[0].clone(), seat_decks[1].clone(), vec![PlayerCode::R, PlayerCode::R]);
        let mut g = Game::from_state(state.clone(), players, KO_SEED + s);
        g.apply_action(action);
        g.get_state_clone().points[action.actor].saturating_sub(before) >= 1
    })
}

/// The move's kind as the Lucario tool describes it (kind, Trainer type, Active or Bench target, attack damage and
/// printed knockout), plus names for the pre-set habits: the attack and its attacker, the Pokemon placed or powered,
/// the retreat or promotion target, and which Pokemon is Active after the move.
fn detail(state: &State, action: &Action, seat_decks: &[Deck; 2]) -> serde_json::Value {
    let me = action.actor;
    let role = |idx: usize| if idx == 0 { "active" } else { "bench" };
    let opp_hp = state.in_play_pokemon[1 - me][0].as_ref().map(|p| p.get_remaining_hp());
    let active = active_name(state, me);
    let mut d = match &action.action {
        SimpleAction::Play { trainer_card } => serde_json::json!({ "kind": "play",
            "trainer": format!("{:?}", trainer_card.trainer_card_type).to_lowercase(), "card": trainer_card.name }),
        SimpleAction::Attack(atk) => serde_json::json!({ "kind": "attack", "damage": atk.fixed_damage,
            "has_effect": atk.effect.is_some(), "printed_ko": opp_hp.is_some_and(|h| atk.fixed_damage >= h),
            "sure_ko": sure_ko(state, seat_decks, action), "name": atk.title, "attacker": active }),
        SimpleAction::UseAbility { in_play_idx } => serde_json::json!({ "kind": "ability", "target": role(*in_play_idx),
            "name": name_at(state, me, *in_play_idx) }),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => serde_json::json!({ "kind": "evolve",
            "target": role(*in_play_idx), "name": evolution.get_name(), "from": name_at(state, me, *in_play_idx) }),
        SimpleAction::Place(card, idx) => serde_json::json!({ "kind": "place", "slot": role(*idx),
            "name": card.get_name(), "setup": state.turn_count == 0 }),
        SimpleAction::AttachTool { in_play_idx, tool_card } => serde_json::json!({ "kind": "tool",
            "target": role(*in_play_idx), "card": tool_card.get_name(), "name": name_at(state, me, *in_play_idx) }),
        SimpleAction::Attach { attachments, .. } => serde_json::json!({ "kind": "energy",
            "target": attachments.first().map(|(_, _, idx)| role(*idx)).unwrap_or("none"),
            "name": attachments.first().map(|(_, _, idx)| name_at(state, me, *idx)) }),
        SimpleAction::Retreat(idx) => serde_json::json!({ "kind": "retreat", "name": name_at(state, me, *idx),
            "from": active }),
        SimpleAction::Promote { player, in_play_idx } => serde_json::json!({ "kind": "promote",
            "name": name_at(state, *player, *in_play_idx) }),
        SimpleAction::Activate { player, in_play_idx } => serde_json::json!({ "kind": "activate",
            "name": name_at(state, *player, *in_play_idx) }),
        SimpleAction::EndTurn => serde_json::json!({ "kind": "end turn" }),
        other => serde_json::json!({ "kind": format!("{other:?}").split(|c: char| !c.is_alphanumeric()).next()
            .unwrap_or("").to_lowercase() }),
    };
    // Who is Active once this move is made (a promotion, retreat or switch names its target; a Basic placed into an
    // empty Active Spot at setup names itself; anything else leaves the Active where it is).
    let after = match &action.action {
        SimpleAction::Retreat(idx) => Some(name_at(state, me, *idx)),
        SimpleAction::Promote { player, in_play_idx } | SimpleAction::Activate { player, in_play_idx }
            if *player == me => Some(name_at(state, me, *in_play_idx)),
        SimpleAction::Place(card, 0) => Some(card.get_name()),
        SimpleAction::Evolve { evolution, in_play_idx: 0, .. } => Some(evolution.get_name()),
        _ => active,
    };
    d["active_after"] = serde_json::json!(after);
    d
}

/// The board around a decision, from the mover's side.
fn context(state: &State, me: usize, actions: &[Action]) -> serde_json::Value {
    let hp = |p: usize| state.in_play_pokemon[p][0].as_ref().map(|c| c.get_remaining_hp());
    let bench = |p: usize| state.in_play_pokemon[p][1..].iter().flatten().count();
    let bench_names = |p: usize| state.in_play_pokemon[p][1..].iter().flatten().map(|c| c.get_name()).collect::<Vec<_>>();
    let energy = |p: usize| state.in_play_pokemon[p][0].as_ref().map(|c| c.attached_energy.len());
    serde_json::json!({
        "own_active": active_name(state, me), "opp_active": active_name(state, 1 - me),
        "own_active_hp": hp(me), "opp_active_hp": hp(1 - me), "own_bench": bench(me), "opp_bench": bench(1 - me),
        "own_bench_names": bench_names(me), "opp_bench_names": bench_names(1 - me),
        "own_active_energy": energy(me), "opp_active_energy": energy(1 - me), "hand": state.hands[me].len(),
        "opp_active_asleep": state.in_play_pokemon[1 - me][0].as_ref().is_some_and(|c| c.is_asleep()),
        "attack_offered": actions.iter().any(|a| matches!(a.action, SimpleAction::Attack(_))),
        "bench_offered": actions.iter().any(|a| matches!(a.action, SimpleAction::Place(_, idx) if idx > 0)),
    })
}

fn altaria_score(state: &State, altaria_seat: usize) -> f64 {
    match state.winner {
        Some(GameOutcome::Win(w)) => f64::from(u8::from(w == altaria_seat)),
        _ => 0.5,
    }
}

fn seat_decks(g: &Recorded, decks: &[Deck; 2]) -> [Deck; 2] {
    let of = |s: usize| if g.decks[s] == "altaria" { decks[0].clone() } else { decks[1].clone() };
    [of(0), of(1)]
}

fn replay(g: &Recorded, i: u64, decks: &[Deck; 2], probes: u64) -> Replay {
    let alt = g.decks.iter().position(|d| d == "altaria").expect("checked in main");
    let luc = 1 - alt;
    let seats = seat_decks(g, decks);
    let mut codes = vec![PlayerCode::R, PlayerCode::R]; // the add-on's placeholder in the network's seat, never asked
    codes[luc] = KP3;
    let mut game = Game::new(create_players(seats[0].clone(), seats[1].clone(), codes), g.seed);
    let (mut records, mut positions) = (Vec::new(), Vec::new());
    let fail = |records, positions, why: String| Replay { records, positions, problem: Some(why) };
    // readout.look() per decision: (attack offered, attack chosen, Place offered, Place chosen), grouped by turn
    let mut turns: BTreeMap<u8, [bool; 4]> = BTreeMap::new();
    let mut bench_at = [0u32; 4];
    let mut j = 0usize;
    // Who moved first, read at the first state of turn 1 or later (the turn player then); the records' went_first
    // and own_turn are set from it at the end (review, Sept 26: read per decision, it was wrong at setup, turn 0).
    let mut first_mover: Option<usize> = None;
    loop {
        let state = game.get_state_clone();
        if first_mover.is_none() && state.turn_count >= 1 {
            first_mover = Some(if state.turn_count % 2 == 1 { state.current_player } else { 1 - state.current_player });
        }
        if state.winner.is_some() {
            break;
        }
        let (actor, mut actions) = state.generate_possible_actions();
        if actor == luc {
            game.play_tick(); // kp3, with the game's own decision seeds, exactly as the add-on's bot seat
            continue;
        }
        canonical_actions(&mut actions);
        if actions.len() == 1 {
            game.apply_action(&actions[0]); // forced, as the add-on
            continue;
        }
        let Some(&k) = g.moves.get(j) else {
            return fail(records, positions, format!("the engine asks for network decision {j}; {} recorded", g.moves.len()));
        };
        if k >= actions.len() {
            return fail(records, positions, format!("decision {j}: recorded index {k}, {} moves offered here", actions.len()));
        }
        if j >= 1_000 {
            return fail(records, positions, format!("decision {j}: past the seed scheme's 1,000 decisions per game"));
        }
        let is_attack = |a: &Action| matches!(a.action, SimpleAction::Attack(_));
        let is_place = |a: &Action| matches!(a.action, SimpleAction::Place(..));
        let t = turns.entry(state.turn_count).or_default();
        t[0] |= actions.iter().any(is_attack);
        t[1] |= is_attack(&actions[k]);
        t[2] |= actions.iter().any(is_place);
        t[3] |= is_place(&actions[k]);
        if matches!(&actions[k].action, SimpleAction::Attack(a) if a.title == BENCH_ATTACK) {
            bench_at[state.in_play_pokemon[alt][1..].iter().flatten().count().min(3)] += 1;
        }
        if probes > 0 {
            let observation = game.observation(actor);
            let kp3_moves: Vec<usize> = (0..probes)
                .map(|p| {
                    let mut pilots = create_players(seats[0].clone(), seats[1].clone(), vec![KP3, KP3]);
                    let mut rng = StdRng::seed_from_u64(PROBE_BASE + i * 100_000 + j as u64 * 10 + p);
                    let c = pilots[actor].decision_fn(&mut rng, &observation, &actions);
                    actions.iter().position(|a| *a == c).expect("kp3 picks an offered move")
                })
                .collect();
            let kp = kp3_moves[0];
            let same = label(&state, &actions[kp]) == label(&state, &actions[k]);
            let revealed = [game.observation(0).revealed != Default::default(),
                            game.observation(1).revealed != Default::default()];
            records.push(serde_json::json!({
                "i": i, "seed": g.seed, "altaria_seat": alt, "decision": j, "turn": state.turn_count,
                "on_own_turn": state.current_player == alt,
                "legal": actions.len(), "points": [state.points[alt], state.points[luc]],
                "net": k, "net_move": label(&state, &actions[k]),
                "kp3": kp3_moves, "kp3_move": label(&state, &actions[kp]),
                "kp3_agrees_with_itself": kp3_moves.iter().all(|m| *m == kp),
                "net_detail": detail(&state, &actions[k], &seats), "kp3_detail": detail(&state, &actions[kp], &seats),
                "context": context(&state, actor, &actions), "revealed_memory": revealed,
                "differs": !same, "game_won": g.winner == alt as i64,
            }));
            if !same {
                positions.push(Position { i, j, state: state.clone(), net: actions[k].clone(), kp3: actions[kp].clone() });
            }
        }
        game.apply_action(&actions[k]);
        j += 1;
    }
    if j != g.moves.len() {
        return fail(records, positions, format!("the game ended after {j} network decisions; {} recorded", g.moves.len()));
    }
    let end = game.get_state_clone();
    let winner = match end.winner {
        Some(GameOutcome::Win(w)) => w as i64,
        _ => -1,
    };
    if winner != g.winner || end.points != g.points || end.turn_count != g.turns {
        return fail(records, positions, format!("result {winner} {:?} turn {} here, recorded {} {:?} turn {}",
            end.points, end.turn_count, g.winner, g.points, g.turns));
    }
    let mut habits = Habits::default();
    for (&t, [ao, am, po, pm]) in &turns {
        if t > 0 {
            habits.turns += 1;
            if *ao {
                habits.attack_turns += 1;
                habits.attack_made += u32::from(*am);
            }
            if *po {
                habits.bench_turns += 1;
                habits.bench_made += u32::from(*pm);
            }
        }
    }
    match &g.count {
        Some(c) if c.habits != habits || c.bench_at != bench_at => {
            return fail(records, positions, format!("counts {habits:?} bench_at {bench_at:?} here, recorded {:?} {:?}",
                c.habits, c.bench_at));
        }
        None => return fail(records, positions, "the record has no per-game counts to check".into()),
        _ => {}
    }
    // A difference is "order only" when the network plays kp3's move later in the same turn.
    let order_only: Vec<bool> = (0..records.len()).map(|a| {
        records[a]["differs"].as_bool() == Some(true) && (a + 1..records.len()).any(|b| {
            records[b]["turn"] == records[a]["turn"] && records[b]["net_move"] == records[a]["kp3_move"]
        })
    }).collect();
    let went_first = first_mover == Some(alt);
    for (r, o) in records.iter_mut().zip(&order_only) {
        r["order_only"] = serde_json::json!(o);
        let t = r["turn"].as_u64().unwrap_or(0);
        let own_turn = match t {
            0 => 0,
            t if went_first => (t + 1) / 2,
            t => t / 2,
        };
        r["went_first"] = serde_json::json!(went_first);
        r["own_turn"] = serde_json::json!(own_turn);
    }
    positions.retain(|p| !order_only[p.j]);
    Replay { records, positions, problem: None }
}

fn rollout(pos: &Position, first: &Action, seats: &[Deck; 2], alt: usize, seed: u64) -> f64 {
    let players = create_players(seats[0].clone(), seats[1].clone(), vec![KP3, KP3]);
    let mut game = Game::from_state(pos.state.clone(), players, seed);
    game.apply_action(first);
    while !game.is_game_over() {
        game.play_tick();
    }
    altaria_score(&game.get_state_clone(), alt)
}

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let num = |flag: &str, default: u64| -> u64 {
        arg(&args, flag).map(|x| x.parse().unwrap_or_else(|_| panic!("{flag} takes a number"))).unwrap_or(default)
    };
    let path = arg(&args, "--games-file").expect("--games-file <kp3_rows_games.jsonl>");
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let (first, count) = (num("--first", 0), num("--games", 400));
    let sync_only = args.iter().any(|a| a == "--sync-only");
    let probes = if sync_only { 0 } else { num("--probes", 3) };
    let rollouts = if sync_only { 0 } else { num("--rollouts", 8) };
    assert!(sync_only || (1..=10).contains(&probes), "--probes must be 1 to 10 (the seed scheme)");
    assert!(rollouts <= 100, "--rollouts must be at most 100 (the seed scheme)");
    let decks = [
        Deck::from_file(&format!("{dir}/altaria.txt")).expect("altaria.txt"),
        Deck::from_file(&format!("{dir}/lucario.txt")).expect("lucario.txt"),
    ];
    let t0 = Instant::now();
    let file = std::fs::File::open(&path).unwrap_or_else(|e| panic!("{path}: {e}"));
    let mut games: Vec<(u64, Recorded)> = Vec::new();
    for line in std::io::BufReader::new(file).lines() {
        let g: Recorded = serde_json::from_str(&line.expect("line")).expect("game line");
        if g.row != ROW || g.seed < DEAL_BASE {
            continue;
        }
        let i = g.seed - DEAL_BASE;
        if i < first || i >= first + count {
            continue;
        }
        let mut names = g.decks.clone();
        names.sort();
        assert!(names == ["altaria", "lucario"], "deal {i}: decks {:?}", g.decks);
        games.push((i, g));
    }
    games.sort_by_key(|(i, _)| *i);
    let found: Vec<u64> = games.iter().map(|(i, _)| *i).collect();
    let wanted: Vec<u64> = (first..first + count).collect();
    if found != wanted {
        eprintln!("the file does not hold row {ROW} exactly once for each deal {first} to {}: found {} lines",
            first + count - 1, found.len());
        std::process::exit(2);
    }

    let replays: Vec<Replay> = games.par_iter().map(|(i, g)| replay(g, *i, &decks, probes)).collect();
    let t_replay = t0.elapsed().as_secs_f64();
    let mut rejected = 0;
    for ((i, _), r) in games.iter().zip(&replays) {
        if let Some(p) = &r.problem {
            rejected += 1;
            eprintln!("deal {i}: REJECTED, out of sync: {p}");
        }
    }
    if sync_only {
        let n = games.len();
        println!("{} {} of {n} games in sync (deals {first} to {}; seeds {} to {}; every recorded index offered, \
            decision count, winner, points, turn and the per-game attack/bench counts equal); {rejected} rejected; {:.0} s",
            if rejected == 0 { "SYNC PASS" } else { "SYNC FAIL" }, n - rejected, first + count - 1,
            DEAL_BASE + first, DEAL_BASE + first + count - 1, t_replay);
        std::process::exit(if rejected == 0 { 0 } else { 1 });
    }
    let alt_of: HashMap<u64, usize> = games.iter()
        .map(|(i, g)| (*i, g.decks.iter().position(|d| d == "altaria").unwrap())).collect();
    let seats_of: HashMap<u64, [Deck; 2]> = games.iter().map(|(i, g)| (*i, seat_decks(g, &decks))).collect();
    let (mut records, mut positions) = (Vec::new(), Vec::new());
    for r in replays {
        if r.problem.is_none() {
            records.extend(r.records);
            positions.extend(r.positions);
        }
    }
    eprintln!("{} games, {rejected} rejected (out of sync); {} network decisions, {} where kp3 differs beyond move \
        order; replay and probes {:.0} s; playing out", games.len(), records.len(), positions.len(), t_replay);
    let t1 = Instant::now();
    let results: Vec<(Vec<f64>, Vec<f64>)> = positions.par_iter().map(|pos| {
        let alt = alt_of[&pos.i];
        let seats = &seats_of[&pos.i];
        let seed = |r: u64| ROLLOUT_BASE + pos.i * 100_000 + pos.j as u64 * 100 + r;
        let net: Vec<f64> = (0..rollouts).map(|r| rollout(pos, &pos.net, seats, alt, seed(r))).collect();
        let kp3: Vec<f64> = (0..rollouts).map(|r| rollout(pos, &pos.kp3, seats, alt, seed(r))).collect();
        (net, kp3)
    }).collect();
    let t_roll = t1.elapsed().as_secs_f64();
    let mut rolled: HashMap<(u64, usize), (Vec<f64>, Vec<f64>)> = HashMap::new();
    for (pos, res) in positions.iter().zip(results) {
        rolled.insert((pos.i, pos.j), res);
    }
    let mut lines = Vec::new();
    let (mut sum_diff, mut n) = (0.0, 0);
    for mut r in records {
        let key = (r["i"].as_u64().unwrap(), r["decision"].as_u64().unwrap() as usize);
        if let Some((net, kp3)) = rolled.get(&key) {
            let m = |v: &Vec<f64>| v.iter().sum::<f64>() / v.len().max(1) as f64;
            r["rollouts_net"] = serde_json::json!(net);
            r["rollouts_kp3"] = serde_json::json!(kp3);
            r["net_minus_kp3"] = serde_json::json!(m(net) - m(kp3));
            sum_diff += m(net) - m(kp3);
            n += 1;
        }
        lines.push(r.to_string());
    }
    println!("{} games ({rejected} rejected, out of sync), {} network decisions, {n} where kp3's move differs beyond \
        move order, {rollouts} paired play-outs each; average (network move - kp3 move) Altaria score when kp3 plays \
        on: {:+.3}", games.len(), lines.len(), sum_diff / n.max(1) as f64);
    eprintln!("timing: replay and probes {t_replay:.0} s, play-outs {t_roll:.0} s ({} positions x {} play-outs), \
        threads {}", n, 2 * rollouts, rayon::current_num_threads());
    if let Some(path) = arg(&args, "--out") {
        std::fs::write(&path, lines.join("\n") + "\n").expect("out file");
    }
}
