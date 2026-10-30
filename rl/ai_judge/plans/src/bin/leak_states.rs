//! LS: plays km3 v km3 and dumps the actor's observation at every Nth decision (A2). Without --dump-only it also writes two
//! observations of states that differ only in hidden cards (for gate 2).
use deckgym::{
    actions::Action,
    observation::{canonical_actions, PlayerObservation, RevealedKnowledge},
    players::{create_players, parse_player_code},
    Deck, Game, State,
};
use rand::{rngs::StdRng, seq::SliceRandom, SeedableRng};
use serde_json::{json, Value};
use std::io::Write;

fn variants(s: &State, actor: usize, seed: u64, idx: u64, revealed: &RevealedKnowledge) -> (Value, Value) {
    let opp = 1 - actor;
    let mut s2 = s.clone();
    let mut rng = StdRng::seed_from_u64(seed ^ idx ^ 0xD1CE);
    for p in 0..2 {
        s2.decks[p].cards.shuffle(&mut rng);
    }
    let n = s2.hands[opp].len().min(s2.decks[opp].cards.len());
    for i in 0..n {
        let c = s2.hands[opp][i].clone();
        s2.hands[opp][i] = s2.decks[opp].cards[i].clone();
        s2.decks[opp].cards[i] = c;
    }
    let obs_b = serde_json::to_value(PlayerObservation::from_state(&s2, actor, revealed)).unwrap();
    let mut s3 = s.clone();
    for p in 0..2 {
        s3.decks[p].cards.reverse();
    }
    let obs_c = match s3.decks[actor].cards.first().cloned() {
        Some(c) => {
            for h in s3.hands[opp].iter_mut() {
                *h = c.clone();
            }
            for d in s3.decks[opp].cards.iter_mut() {
                *d = c.clone();
            }
            serde_json::to_value(PlayerObservation::from_state(&s3, actor, revealed)).unwrap()
        }
        None => Value::Null,
    };
    (obs_b, obs_c)
}

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let (mut pd, mut od, mut out) = (String::new(), String::new(), String::new());
    let (mut seat, mut every, mut dump_only) = (0usize, 1u64, false);
    let mut seeds: Vec<u64> = Vec::new();
    let mut i = 0;
    while i < a.len() {
        let v = a.get(i + 1).cloned().unwrap_or_default();
        match a[i].as_str() {
            "--pilot-deck" => { pd = v; i += 2 }
            "--opp-deck" => { od = v; i += 2 }
            "--seat" => { seat = v.parse().unwrap(); i += 2 }
            "--seeds" => { seeds = v.split(',').map(|s| s.parse().unwrap()).collect(); i += 2 }
            "--every" => { every = v.parse().unwrap(); i += 2 }
            "--out" => { out = v; i += 2 }
            "--dump-only" => { dump_only = true; i += 1 }
            other => { eprintln!("unknown argument {other}"); std::process::exit(2) }
        }
    }
    if pd.is_empty() || od.is_empty() || out.is_empty() || seeds.is_empty() || seat > 1 || every == 0 {
        eprintln!("usage: leak_states --pilot-deck A --opp-deck B --seat S --seeds s1,.. [--every N] [--dump-only] --out F.jsonl");
        std::process::exit(2);
    }
    let pilot = Deck::from_file(&pd).unwrap();
    let opp = Deck::from_file(&od).unwrap();
    let (da, db) = if seat == 0 { (pilot, opp) } else { (opp, pilot) };
    let paths = if seat == 0 { [pd.clone(), od.clone()] } else { [od.clone(), pd.clone()] };
    let mut f = std::fs::File::create(&out).unwrap();
    let mut written = 0u64;
    for seed in seeds {
        let km3 = || parse_player_code("km3").unwrap();
        let mut game = Game::new(create_players(da.clone(), db.clone(), vec![km3(), km3()]), seed);
        let mut n_dec = 0u64;
        while !game.is_game_over() {
            let s = game.get_state_clone();
            let (actor, mut acts) = s.generate_possible_actions();
            canonical_actions(&mut acts);
            if acts.len() > 1 {
                n_dec += 1;
                if n_dec % every == 0 {
                    let obs_a = game.observation(actor);
                    let mut rec = json!({
                        "id": format!("{seed}-a{actor}-d{n_dec}"), "seed": seed, "actor": actor, "turn_count": s.turn_count,
                        "current_player": s.current_player, "deck_file": paths[actor], "legal_actions": acts, "obs_a": obs_a,
                    });
                    if !dump_only {
                        if obs_a.revealed != RevealedKnowledge::default() {
                            rec["skipped"] = json!("revealed");
                        } else {
                            let (b, c) = variants(&s, actor, seed, n_dec, &obs_a.revealed);
                            rec["obs_b"] = b;
                            rec["obs_c"] = c;
                        }
                    }
                    writeln!(f, "{rec}").unwrap();
                    written += 1;
                }
            }
            game.play_tick();
        }
    }
    f.flush().unwrap();
    eprintln!("leak_states: wrote {written} records");
    let _ = Action::clone; // keep the import used
}
