//! KR: replays a shadow log through a fresh in-engine kx3 and compares each chosen index.
use deckgym::{
    actions::Action,
    observation::PlayerObservation,
    players::{create_players, parse_player_code, PlayerCode},
    Deck,
};
use rand::{rngs::StdRng, seq::SliceRandom, SeedableRng};
use serde_json::{json, Value};
use std::io::BufRead;

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let (mut log, mut opp, mut sample, mut sseed) = (String::new(), String::new(), None::<usize>, 1u64);
    let mut i = 0;
    while i < a.len() {
        let v = a.get(i + 1).cloned().unwrap_or_default();
        match a[i].as_str() {
            "--shadow-log" => log = v,
            "--opp-deck" => opp = v,
            "--sample" => sample = Some(v.parse().unwrap()),
            "--sample-seed" => sseed = v.parse().unwrap(),
            other => { eprintln!("unknown argument {other}"); std::process::exit(2) }
        }
        i += 2;
    }
    if log.is_empty() || opp.is_empty() {
        eprintln!("usage: kx3_replay --shadow-log F --opp-deck B [--sample N --sample-seed S]");
        std::process::exit(2);
    }
    let opp_deck = Deck::from_file(&opp).unwrap();
    let f = std::fs::File::open(&log).unwrap();
    let mut recs: Vec<Value> = std::io::BufReader::new(f)
        .lines()
        .map(|l| l.unwrap())
        .filter(|l| !l.trim().is_empty())
        .map(|l| serde_json::from_str(&l).unwrap())
        .collect();
    if let Some(n) = sample {
        recs.shuffle(&mut StdRng::seed_from_u64(sseed));
        recs.truncate(n);
    }
    let (mut checked, mut equal) = (0u64, 0u64);
    for r in &recs {
        let ng: Value = serde_json::from_str(r["new_game"].as_str().unwrap()).unwrap();
        let dc: Value = serde_json::from_str(r["decide"].as_str().unwrap()).unwrap();
        let deck: Deck = serde_json::from_value(ng["deck_definition"].clone()).unwrap();
        let obs: PlayerObservation = serde_json::from_value(dc["pdl_observation"].clone()).unwrap();
        let legal: Vec<Action> = serde_json::from_value(dc["legal_actions"].clone()).unwrap();
        let seed = dc["pdl_search_seed"].as_u64().unwrap();
        let mut p = create_players(deck, opp_deck.clone(), vec![parse_player_code("kx3").unwrap(), PlayerCode::R]).remove(0);
        let chosen = p.decision_fn(&mut StdRng::seed_from_u64(seed), &obs, &legal);
        let k = legal.iter().position(|x| *x == chosen);
        let want = r["shadow_i"].as_u64();
        checked += 1;
        let ok = k.map(|k| k as u64) == want;
        if ok { equal += 1; }
        println!("{}", json!({"deal_tag": r["deal_tag"], "ply": r["ply"], "shadow_i": want, "replay_i": k, "equal": ok}));
    }
    println!("{}", json!({"summary": true, "checked": checked, "equal": equal, "mismatches": checked - equal}));
    std::process::exit(if checked == equal { 0 } else { 1 });
}
