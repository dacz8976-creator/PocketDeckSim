//! B2c step 2: where does the Lucario network choose differently from k3, and which choice wins more?
//!
//!   zcat games.jsonl.gz | cargo run --release --example net_divergence -- --decks ../decks/research
//!       [--probes 3] [--rollouts 16] [--out decisions.jsonl]
//!
//! Input: the games from rl/results/lucario_network_divergence_2026-09-25/play_network_games.py (the network
//! piloting Lucario through add-on 0.7.2, k3 piloting Weezing), one JSON line each with every move.
//! Each game is replayed here from its seed by applying the recorded moves, and each move must be one this
//! engine offers (the network's own move must sit at the same index in the canonical list the add-on showed
//! it); the final score and turn must match the recording. At each network decision k3 is asked for its move
//! from the same observation, under `--probes` search seeds. Where k3's first-probe move differs from the
//! network's (by card names: a Basic onto either empty Bench slot is the same move) and the network doesn't
//! play k3's move later in the same turn (an order-only difference), both moves are played out from that position `--rollouts` times with k3 piloting both decks
//! afterwards, the two moves sharing each chance seed: the win-rate difference says which move k3 itself
//! would do better with.
//!
//! Seeds: k3 probes 22,500,000,000 + i x 100,000 + decision x 10 + probe; rollouts 22,400,000,000 +
//! i x 100,000 + decision x 100 + r (game i < 1,000, decision < 1,000, probe < 10, r < 100).

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::canonical_actions;
use deckgym::players::{create_players, PlayerCode};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;
use std::io::BufRead;

const K3: PlayerCode = PlayerCode::K { max_depth: 3 };

#[derive(serde::Deserialize)]
struct NetMove {
    chosen: usize,
    q: Vec<f64>,
}

#[derive(serde::Deserialize)]
struct Recorded {
    i: u64,
    seed: u64,
    lucario_seat: usize,
    winner: i64,
    points: [u8; 2],
    turns: u8,
    moves: Vec<(usize, String, String)>,
    net: Vec<NetMove>,
}

struct Position {
    i: u64,
    j: usize,
    state: State,
    net: Action,
    k3: Action,
}

fn label(state: &State, action: &Action) -> String {
    let name = |idx: usize| {
        state.in_play_pokemon[action.actor][idx].as_ref().map(|p| p.get_name()).unwrap_or_else(|| format!("slot {idx}"))
    };
    match &action.action {
        SimpleAction::Play { trainer_card } => format!("play {}", trainer_card.name),
        SimpleAction::Attack(atk) => format!("attack {} ({})", atk.title, name(0)),
        SimpleAction::UseAbility { in_play_idx } => format!("ability of {}", name(*in_play_idx)),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("evolve {} into {}", name(*in_play_idx), evolution.get_name()),
        SimpleAction::Place(card, _) => format!("place {}", card.get_name()),
        SimpleAction::AttachTool { tool_card, in_play_idx } => format!("attach {} to {}", tool_card.get_name(), name(*in_play_idx)),
        SimpleAction::Attach { attachments, .. } => {
            let to: Vec<String> = attachments.iter().map(|(n, e, idx)| format!("{n} {e:?} to {}", name(*idx))).collect();
            format!("attach {}", to.join(", "))
        }
        SimpleAction::Retreat(idx) => format!("retreat to {}", name(*idx)),
        SimpleAction::EndTurn => "end turn".into(),
        other => format!("{other:?}").chars().take(80).collect(),
    }
}

fn lucario_score(state: &State, lucario_seat: usize) -> f64 {
    match state.winner {
        Some(GameOutcome::Win(w)) => f64::from(u8::from(w == lucario_seat)),
        _ => 0.5,
    }
}

fn replay(g: &Recorded, decks: &[Deck; 2], probes: u64) -> (Vec<serde_json::Value>, Vec<Position>, Option<String>) {
    // decks[0] = Lucario, decks[1] = Weezing
    let seat_deck = |s: usize| if s == g.lucario_seat { &decks[0] } else { &decks[1] };
    let players = create_players(seat_deck(0).clone(), seat_deck(1).clone(), vec![K3, K3]);
    let mut game = Game::new(players, g.seed);
    let (mut out, mut positions) = (Vec::new(), Vec::new());
    let mut j = 0usize;
    for (n, (p, kind, js)) in g.moves.iter().enumerate() {
        let state = game.get_state_clone();
        let (actor, mut actions) = state.generate_possible_actions();
        canonical_actions(&mut actions);
        let simple: SimpleAction = match serde_json::from_str(js) {
            Ok(s) => s,
            Err(e) => return (out, positions, Some(format!("move {n}: unreadable ({e})"))),
        };
        let Some(idx) = actions.iter().position(|a| a.action == simple && a.actor == *p) else {
            return (out, positions, Some(format!("move {n} ({kind}) is not offered here: {js}")));
        };
        if kind == "agent" {
            let net = &g.net[j];
            if net.chosen != idx || net.q.len() != actions.len() {
                return (out, positions, Some(format!("decision {j}: index {idx} of {} here, add-on {} of {}",
                    actions.len(), net.chosen, net.q.len())));
            }
            let observation = game.observation(actor);
            let k3_moves: Vec<usize> = (0..probes)
                .map(|s| {
                    let mut seats = create_players(seat_deck(0).clone(), seat_deck(1).clone(), vec![K3, K3]);
                    let k3 = &mut seats[actor];
                    let mut rng = StdRng::seed_from_u64(22_500_000_000 + g.i * 100_000 + j as u64 * 10 + s);
                    let c = k3.decision_fn(&mut rng, &observation, &actions);
                    actions.iter().position(|a| *a == c).expect("k3 picks an offered move")
                })
                .collect();
            let k3i = k3_moves[0];
            let own_turn = (state.turn_count as usize + usize::from(g.lucario_seat == 0)) / 2;
            // Moves that read the same by card name (a Basic onto either empty Bench slot, Energy onto either of
            // two identical Pokémon) count as the same move.
            let same = label(&state, &actions[k3i]) == label(&state, &actions[idx]);
            let record = serde_json::json!({
                "i": g.i, "decision": j, "turn": state.turn_count, "own_turn": own_turn, "legal": actions.len(),
                "points": [state.points[g.lucario_seat], state.points[1 - g.lucario_seat]],
                "net": idx, "net_move": label(&state, &actions[idx]), "net_q": net.q[idx],
                "k3": k3_moves, "k3_move": label(&state, &actions[k3i]), "net_q_of_k3_move": net.q[k3i],
                "k3_agrees_with_itself": k3_moves.iter().all(|m| *m == k3i),
                "differs": !same, "game_won": g.winner == g.lucario_seat as i64,
            });
            if !same {
                positions.push(Position { i: g.i, j, state: state.clone(), net: actions[idx].clone(), k3: actions[k3i].clone() });
            }
            out.push(record);
            j += 1;
        }
        game.apply_action(&actions[idx]);
    }
    // A difference is "order only" when the network plays k3's move later in the same turn.
    let order_only: Vec<bool> = (0..out.len()).map(|a| {
        out[a]["differs"].as_bool() == Some(true) && (a + 1..out.len()).any(|b| {
            out[b]["turn"] == out[a]["turn"] && out[b]["net_move"] == out[a]["k3_move"]
        })
    }).collect();
    for (r, o) in out.iter_mut().zip(&order_only) {
        r["order_only"] = serde_json::json!(o);
    }
    positions.retain(|p| !order_only[p.j]);
    let end = game.get_state_clone();
    let winner = match end.winner {
        Some(GameOutcome::Win(w)) => w as i64,
        Some(_) => -1,
        None => return (out, positions, Some("game not over after the recorded moves".into())),
    };
    if winner != g.winner || end.points != g.points || end.turn_count != g.turns {
        return (out, positions, Some(format!("result {winner} {:?} turn {} here, recorded {} {:?} turn {}",
            end.points, end.turn_count, g.winner, g.points, g.turns)));
    }
    (out, positions, None)
}

fn rollout(pos: &Position, first: &Action, decks: &[Deck; 2], lucario_seat: usize, seed: u64) -> f64 {
    let seat_deck = |s: usize| if s == lucario_seat { decks[0].clone() } else { decks[1].clone() };
    let players = create_players(seat_deck(0), seat_deck(1), vec![K3, K3]);
    let mut game = Game::from_state(pos.state.clone(), players, seed);
    game.apply_action(first);
    while !game.is_game_over() {
        game.play_tick();
    }
    lucario_score(&game.get_state_clone(), lucario_seat)
}

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let probes: u64 = arg(&args, "--probes").map(|x| x.parse().unwrap()).unwrap_or(3);
    let rollouts: u64 = arg(&args, "--rollouts").map(|x| x.parse().unwrap()).unwrap_or(16);
    let decks = [
        Deck::from_file(&format!("{dir}/lucario.txt")).expect("lucario"),
        Deck::from_file(&format!("{dir}/weezing.txt")).expect("weezing"),
    ];
    let games: Vec<Recorded> = std::io::stdin().lock().lines()
        .map(|l| serde_json::from_str(&l.unwrap()).expect("game line")).collect();
    let replays: Vec<_> = games.par_iter().map(|g| replay(g, &decks, probes)).collect();
    let mut problems = 0;
    for (g, (_, _, problem)) in games.iter().zip(&replays) {
        if let Some(p) = problem {
            problems += 1;
            eprintln!("game {}: {p}", g.i);
        }
    }
    let seat_of: std::collections::HashMap<u64, usize> = games.iter().map(|g| (g.i, g.lucario_seat)).collect();
    let (mut records, mut positions) = (Vec::new(), Vec::new());
    for (r, p, problem) in replays {
        if problem.is_none() {
            records.extend(r);
            positions.extend(p);
        }
    }
    eprintln!("{} games, {problems} out of sync; {} network decisions, {} where k3 differs beyond move order; \
        rolling out", games.len(), records.len(), positions.len());
    let results: Vec<(Vec<f64>, Vec<f64>)> = positions.par_iter().map(|pos| {
        let seat = seat_of[&pos.i];
        let seed = |r: u64| 22_400_000_000 + pos.i * 100_000 + pos.j as u64 * 100 + r;
        let net: Vec<f64> = (0..rollouts).map(|r| rollout(pos, &pos.net, &decks, seat, seed(r))).collect();
        let k3: Vec<f64> = (0..rollouts).map(|r| rollout(pos, &pos.k3, &decks, seat, seed(r))).collect();
        (net, k3)
    }).collect();
    let mut rolled: std::collections::HashMap<(u64, usize), (Vec<f64>, Vec<f64>)> = std::collections::HashMap::new();
    for (pos, res) in positions.iter().zip(results) {
        rolled.insert((pos.i, pos.j), res);
    }
    let mut lines = Vec::new();
    let (mut sum_diff, mut n) = (0.0, 0);
    for mut r in records {
        let key = (r["i"].as_u64().unwrap(), r["decision"].as_u64().unwrap() as usize);
        if let Some((net, k3)) = rolled.get(&key) {
            let m = |v: &Vec<f64>| v.iter().sum::<f64>() / v.len().max(1) as f64;
            r["rollouts_net"] = serde_json::json!(net);
            r["rollouts_k3"] = serde_json::json!(k3);
            r["net_minus_k3"] = serde_json::json!(m(net) - m(k3));
            sum_diff += m(net) - m(k3);
            n += 1;
        }
        lines.push(r.to_string());
    }
    println!("{} games ({problems} out of sync), {} network decisions, {n} where k3's move differs beyond move order; average \
        (network move - k3 move) Lucario score when k3 plays on: {:+.3}", games.len(), lines.len(), sum_diff / n.max(1) as f64);
    if let Some(path) = arg(&args, "--out") {
        std::fs::write(&path, lines.join("\n") + "\n").expect("out file");
    }
}
