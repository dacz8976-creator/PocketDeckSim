//! KP: a seat played directly by the engine bot vs the same seat played through protocol_bot.
use deckgym::{
    game::DecisionRandomness,
    observation::PlayerObservation,
    actions::Action,
    players::{create_players, parse_player_code, Player, PlayerCode, ProtocolPlayer},
    protocol::PublicEvent,
    Deck, Game,
};
use rand::rngs::StdRng;
use serde_json::json;
use std::{cell::RefCell, path::PathBuf, rc::Rc, sync::atomic::Ordering, time::{Duration, Instant}};
use deckgym::State;

type Log = Rc<RefCell<Vec<(usize, u64, String)>>>;

#[derive(Debug)]
struct Rec {
    inner: Box<dyn Player>,
    log: Log,
    pending: Option<DecisionRandomness>,
}

impl Player for Rec {
    fn get_deck(&self) -> Deck {
        self.inner.get_deck()
    }
    fn before_decision(&mut self, d: &DecisionRandomness) {
        self.pending = Some(d.clone());
        self.inner.before_decision(d)
    }
    fn on_public_event(&mut self, e: &PublicEvent) {
        self.inner.on_public_event(e)
    }
    fn decision_fn(&mut self, rng: &mut StdRng, obs: &PlayerObservation, actions: &[Action]) -> Action {
        let chosen = self.inner.decision_fn(rng, obs, actions);
        let d = self.pending.take().expect("before_decision precedes decision_fn");
        self.log.borrow_mut().push((d.actor, d.decision_index, serde_json::to_string(&chosen).unwrap()));
        chosen
    }
    fn decide_omniscient(&mut self, rng: &mut StdRng, s: &State, a: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, s, a)
    }
}

fn cut(s: &str) -> String {
    s.chars().take(300).collect()
}

fn proto_cmd(pb: &str, code: &str, threads: Option<u32>) -> String {
    let t = threads.map(|n| format!("RAYON_NUM_THREADS={n} ")).unwrap_or_default();
    format!("env -u VERTEX_API_KEY -u VERTEX_PROJECT {t}{pb} --bot {code}")
}

struct Cfg {
    code: String,
    opp_code: String,
    pilot_deck: String,
    opp_deck: String,
    seat: usize,
    pb: String,
    proto_cmd: Option<String>,
    proto_threads: Option<u32>,
    max_decisions: Option<usize>,
    timeout_ms: u64,
    log_dir: Option<String>,
    protocol_only: bool,
}

struct Out {
    log: Vec<(usize, u64, String)>,
    state: String,
    secs: f64,
    fallbacks: u64,
}

fn play(cfg: &Cfg, seed: u64, protocol: bool) -> Out {
    let pilot = Deck::from_file(&cfg.pilot_deck).unwrap();
    let opp = Deck::from_file(&cfg.opp_deck).unwrap();
    let (da, db) = if cfg.seat == 0 { (pilot.clone(), opp.clone()) } else { (opp.clone(), pilot.clone()) };
    let mut codes: Vec<PlayerCode> = vec![PlayerCode::R, PlayerCode::R];
    codes[cfg.seat] = parse_player_code(&cfg.code).unwrap();
    codes[1 - cfg.seat] = parse_player_code(&cfg.opp_code).unwrap();
    let mut players = create_players(da, db, codes);
    let mut stats = Vec::new();
    if protocol {
        let timeout = Duration::from_millis(cfg.timeout_ms);
        let logd = cfg.log_dir.as_ref().map(PathBuf::from);
        let pcmd = cfg.proto_cmd.clone().unwrap_or_else(|| proto_cmd(&cfg.pb, &cfg.code, cfg.proto_threads));
        let pp = ProtocolPlayer::new(pilot.clone(), pcmd, timeout, logd.clone());
        stats.push(pp.stats());
        players[cfg.seat] = Box::new(pp);
        if cfg.opp_code == "kx3" {
            let ocmd = proto_cmd(&cfg.pb, "kx3", cfg.proto_threads);
            let op = ProtocolPlayer::new(opp.clone(), ocmd, timeout, logd);
            stats.push(op.stats());
            players[1 - cfg.seat] = Box::new(op);
        }
    }
    let log: Log = Rc::new(RefCell::new(Vec::new()));
    let wrapped: Vec<Box<dyn Player>> = players
        .into_iter()
        .map(|inner| Box::new(Rec { inner, log: log.clone(), pending: None }) as Box<dyn Player>)
        .collect();
    let mut game = Game::new(wrapped, seed);
    let t0 = Instant::now();
    while !game.is_game_over() {
        if let Some(m) = cfg.max_decisions {
            if log.borrow().iter().filter(|e| e.0 == cfg.seat).count() >= m {
                break;
            }
        }
        game.play_tick();
    }
    let secs = t0.elapsed().as_secs_f64();
    let state = serde_json::to_string(&game.get_state_clone()).unwrap();
    let fallbacks = stats.iter().map(|s| s.fallbacks.load(Ordering::SeqCst)).sum();
    drop(game);
    let l = log.borrow().clone();
    Out { log: l, state, secs, fallbacks }
}

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let mut cfg = Cfg {
        code: String::new(), opp_code: "km3".into(), pilot_deck: String::new(), opp_deck: String::new(),
        seat: 0, pb: String::new(), proto_cmd: None, proto_threads: None, max_decisions: None,
        timeout_ms: 2_700_000, log_dir: None, protocol_only: false,
    };
    let mut seeds: Vec<u64> = Vec::new();
    let mut i = 0;
    while i < a.len() {
        let v = |i: usize| a.get(i + 1).cloned().unwrap_or_else(|| { eprintln!("missing value for {}", a[i]); std::process::exit(2) });
        match a[i].as_str() {
            "--code" => { cfg.code = v(i); i += 2 }
            "--opp-code" => { cfg.opp_code = v(i); i += 2 }
            "--pilot-deck" => { cfg.pilot_deck = v(i); i += 2 }
            "--opp-deck" => { cfg.opp_deck = v(i); i += 2 }
            "--seat" => { cfg.seat = v(i).parse().unwrap(); i += 2 }
            "--seeds" => { seeds = v(i).split(',').map(|s| s.parse().unwrap()).collect(); i += 2 }
            "--protocol-bot" => { cfg.pb = v(i); i += 2 }
            "--proto-cmd" => { cfg.proto_cmd = Some(v(i)); i += 2 }
            "--proto-threads" => { cfg.proto_threads = Some(v(i).parse().unwrap()); i += 2 }
            "--max-decisions" => { cfg.max_decisions = Some(v(i).parse().unwrap()); i += 2 }
            "--timeout-ms" => { cfg.timeout_ms = v(i).parse().unwrap(); i += 2 }
            "--log-dir" => { cfg.log_dir = Some(v(i)); i += 2 }
            "--protocol-only" => { cfg.protocol_only = true; i += 1 }
            other => { eprintln!("unknown argument {other}"); std::process::exit(2) }
        }
    }
    if cfg.code.is_empty() || cfg.pb.is_empty() || seeds.is_empty() || cfg.seat > 1 {
        eprintln!("usage: kx3_parity --code C --pilot-deck A --opp-deck B --seat S --seeds s1,.. --protocol-bot PB ...");
        std::process::exit(2);
    }
    let mut bad = false;
    for seed in seeds {
        let direct = if cfg.protocol_only { None } else { Some(play(&cfg, seed, false)) };
        let proto = play(&cfg, seed, true);
        let pilot_n = proto.log.iter().filter(|e| e.0 == cfg.seat).count();
        let mut identical = Value0::Null;
        let mut first_diff = serde_json::Value::Null;
        let mut compared = proto.log.len();
        if let Some(d) = &direct {
            let n = d.log.len().max(proto.log.len());
            compared = d.log.len().min(proto.log.len());
            let mut diff = None;
            for k in 0..n {
                if d.log.get(k) != proto.log.get(k) {
                    diff = Some((k, format!("{:?}", d.log.get(k)), format!("{:?}", proto.log.get(k))));
                    break;
                }
            }
            if diff.is_none() && d.state != proto.state {
                diff = Some((n, cut(&d.state), cut(&proto.state)));
            }
            identical = Value0::Bool(diff.is_none());
            if let Some((k, x, y)) = diff {
                first_diff = json!({"index": k, "a": cut(&x), "b": cut(&y)});
            }
        }
        let ident_json = match identical { Value0::Null => serde_json::Value::Null, Value0::Bool(b) => json!(b) };
        if proto.fallbacks > 0 { bad = true; }
        if !cfg.protocol_only && (identical != Value0::Bool(true) || pilot_n == 0) { bad = true; }
        println!("{}", json!({
            "seed": seed, "seat": cfg.seat, "code": cfg.code, "opp_code": cfg.opp_code,
            "decisions_compared": compared, "pilot_decisions_compared": pilot_n,
            "identical": ident_json, "first_diff": first_diff,
            "secs_direct": direct.as_ref().map(|d| d.secs), "secs_protocol": proto.secs,
            "protocol_fallbacks": proto.fallbacks, "proto_threads": cfg.proto_threads,
        }));
    }
    std::process::exit(if bad { 1 } else { 0 });
}

#[derive(PartialEq)]
enum Value0 { Null, Bool(bool) }
