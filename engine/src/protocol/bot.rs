//! `protocol_bot --bot <code>`: answers the bot protocol with one of our engine bots.
use crate::{
    actions::Action,
    observation::PlayerObservation,
    players::{create_players, parse_player_code, Player, PlayerCode},
    Deck,
};
use rand::{rngs::StdRng, SeedableRng};
use serde_json::{json, Value};
use std::io::{BufRead, Write};

fn die(msg: &str) -> ! {
    eprintln!("protocol_bot: {msg}");
    std::process::exit(2);
}

fn send(value: &Value) {
    let mut out = std::io::stdout().lock();
    let _ = writeln!(out, "{value}");
    let _ = out.flush();
}

pub fn run() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let code = match args.as_slice() {
        [flag, code] if flag == "--bot" => code.clone(),
        _ => die("usage: protocol_bot --bot <code>"),
    };
    let parsed = parse_player_code(&code).unwrap_or_else(|e| die(&e));
    let mut player: Option<Box<dyn Player>> = None;
    for line in std::io::stdin().lock().lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => break,
        };
        if line.trim().is_empty() {
            continue;
        }
        let msg: Value =
            serde_json::from_str(&line).unwrap_or_else(|e| die(&format!("invalid JSON: {e}")));
        match msg.get("type").and_then(Value::as_str) {
            Some("hello") => send(
                &json!({"type": "hello", "name": format!("pdl-{code}"), "pdl_observation": true}),
            ),
            Some("new_game") => {
                let def = msg
                    .get("deck_definition")
                    .filter(|v| !v.is_null())
                    .unwrap_or_else(|| die("new_game lacks deck_definition"));
                let deck: Deck = serde_json::from_value(def.clone())
                    .unwrap_or_else(|e| die(&format!("bad deck_definition: {e}")));
                let mut players =
                    create_players(deck.clone(), deck, vec![parsed.clone(), PlayerCode::R]);
                player = Some(players.remove(0));
            }
            Some("decide") => {
                let player = player
                    .as_mut()
                    .unwrap_or_else(|| die("decide before new_game"));
                let obs: PlayerObservation = serde_json::from_value(
                    msg.get("pdl_observation")
                        .filter(|v| !v.is_null())
                        .unwrap_or_else(|| die("decide lacks pdl_observation"))
                        .clone(),
                )
                .unwrap_or_else(|e| die(&format!("bad pdl_observation: {e}")));
                let legal: Vec<Action> = serde_json::from_value(
                    msg.get("legal_actions")
                        .filter(|v| !v.is_null())
                        .unwrap_or_else(|| die("decide lacks legal_actions"))
                        .clone(),
                )
                .unwrap_or_else(|e| die(&format!("bad legal_actions: {e}")));
                let seed = msg
                    .get("pdl_search_seed")
                    .and_then(Value::as_u64)
                    .unwrap_or_else(|| die("decide lacks a non-null pdl_search_seed"));
                let mut rng = StdRng::seed_from_u64(seed);
                let chosen = player.decision_fn(&mut rng, &obs, &legal);
                let k = legal
                    .iter()
                    .position(|a| *a == chosen)
                    .unwrap_or_else(|| die("chosen action is not legal"));
                send(&json!({"i": k}));
            }
            other => die(&format!("unknown message type {other:?}")),
        }
    }
}
