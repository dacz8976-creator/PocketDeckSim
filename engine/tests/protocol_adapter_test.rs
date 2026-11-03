use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    game::DecisionRandomness,
    models::{Card, PlayedCard},
    observation::PlayerObservation,
    observation::RevealedKnowledge,
    players::protocol_player::ProtocolStats,
    players::{create_players, EndTurnPlayer, Player, PlayerCode, ProtocolPlayer},
    protocol::{view::ViewState, PublicEvent, SinceLast},
    test_support::load_test_decks,
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};
use serde_json::Value;
use std::{
    cell::RefCell,
    collections::BTreeSet,
    path::{Path, PathBuf},
    rc::Rc,
    sync::{atomic::Ordering, mpsc, Arc, Mutex, MutexGuard, OnceLock},
    time::{Duration, Instant},
};

type DecisionLog = Rc<RefCell<Vec<(usize, u64, String)>>>;
type EventLog = Rc<RefCell<Vec<(usize, PublicEvent)>>>;
type SinceLog = Rc<RefCell<Vec<SinceLast>>>;

#[derive(Debug)]
struct Rec {
    seat: usize,
    inner: Box<dyn Player>,
    decisions: DecisionLog,
    events: EventLog,
    pending: Option<DecisionRandomness>,
    check_obs: bool,
    first_legal: bool,
    since: Option<SinceLog>,
    chance: u64,
    cards_left: [usize; 2],
}

impl Rec {
    fn new(seat: usize, inner: Box<dyn Player>, decisions: &DecisionLog, events: &EventLog) -> Rec {
        Rec {
            seat,
            inner,
            decisions: decisions.clone(),
            events: events.clone(),
            pending: None,
            check_obs: false,
            first_legal: false,
            since: None,
            chance: 0,
            cards_left: [0; 2],
        }
    }
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
        self.events.borrow_mut().push((self.seat, *e));
        self.chance += e.chance as u64;
        for s in 0..2 {
            self.cards_left[s] += e.cards_left_deck[s];
        }
        self.inner.on_public_event(e)
    }
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        obs: &PlayerObservation,
        actions: &[Action],
    ) -> Action {
        if self.check_obs {
            let json = serde_json::to_string(obs).unwrap();
            let back: PlayerObservation =
                serde_json::from_str(&json).expect("observation deserializes");
            assert!(back == *obs, "observation round trip differs");
            assert!(
                serde_json::to_string(&back).unwrap() == json,
                "observation re-serialization differs"
            );
        }
        if let Some(log) = &self.since {
            let me = obs.actor;
            log.borrow_mut().push(SinceLast {
                chance_events: self.chance,
                cards_left_deck_mine: self.cards_left[me],
                cards_left_deck_opponent: self.cards_left[1 - me],
            });
            self.chance = 0;
            self.cards_left = [0; 2];
        }
        let chosen = self.inner.decision_fn(rng, obs, actions);
        if self.first_legal {
            assert!(
                chosen == actions[0],
                "first_legal bot did not choose actions[0]"
            );
        }
        let d = self
            .pending
            .take()
            .expect("before_decision precedes decision_fn");
        self.decisions.borrow_mut().push((
            d.actor,
            d.decision_index,
            serde_json::to_string(&chosen).unwrap(),
        ));
        chosen
    }
    fn decide_omniscient(&mut self, rng: &mut StdRng, s: &State, a: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, s, a)
    }
}

const PAIRS: [(&str, &str); 4] = [
    ("t-altaria", "t-suicune"),
    ("t-blaziken", "t-lucario"),
    ("t-hydreigon", "t-weezing"),
    ("t-sceptile", "t-vespiquen"),
];

fn load(name: &str) -> Deck {
    Deck::from_file(&format!(
        "{}/../decks/screen/opponents/{}.txt",
        env!("CARGO_MANIFEST_DIR"),
        name
    ))
    .unwrap()
}

fn decks(p: usize, o: usize) -> (Deck, Deck) {
    let (a, b) = PAIRS[p];
    if o == 0 {
        (load(a), load(b))
    } else {
        (load(b), load(a))
    }
}

fn seed(p: usize, o: usize, k: u64) -> u64 {
    25_102_000_000 + 1_000 * p as u64 + 500 * o as u64 + k
}

fn km3_codes() -> Vec<PlayerCode> {
    vec![
        PlayerCode::KM { max_depth: 3 },
        PlayerCode::KM { max_depth: 3 },
    ]
}

fn km3_cmd() -> String {
    format!("{} --bot km3", env!("CARGO_BIN_EXE_protocol_bot"))
}

fn py_cmd(file: &str, args: &str) -> String {
    format!(
        "python3 -I {}/bots/{} {}",
        env!("CARGO_MANIFEST_DIR"),
        file,
        args
    )
}

/// Held for the whole of every test that starts Python, so no two start it at once. The first holder starts the
/// interpreter once with the bots' imports, untimed, so cold imports are paid outside every timed hello.
fn python_lock() -> MutexGuard<'static, ()> {
    static LOCK: Mutex<()> = Mutex::new(());
    static WARM: OnceLock<()> = OnceLock::new();
    let guard = LOCK.lock().unwrap_or_else(|e| e.into_inner());
    WARM.get_or_init(|| {
        let start = Instant::now();
        let _ = std::process::Command::new("python3")
            .args(["-I", "-c", "import argparse, json, random, sys, time"])
            .status();
        note_hello("warm-up (untimed)", start.elapsed().as_secs_f64());
    });
    guard
}

/// Timing record only (no assertion): appends `HELLO <label> <secs>` to `pdl_adapter_hellos.txt` in the temp dir.
fn note_hello(label: &str, secs: f64) {
    use std::io::Write as _;
    eprintln!("HELLO {label} {secs:.3}");
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(std::env::temp_dir().join("pdl_adapter_hellos.txt"))
    {
        let _ = writeln!(f, "HELLO {label} {secs:.3}");
    }
}

/// Records each bot's spawn + hello time (`startup_secs` of its first decision) from the adapter logs in `dir`;
/// a hello that timed out on purpose is not one.
fn note_hellos(label: &str, dir: &Path) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let name = entry.file_name().to_string_lossy().to_string();
        if !(name.starts_with("protocol_") && name.ends_with(".jsonl")) {
            continue;
        }
        let Ok(text) = std::fs::read_to_string(entry.path()) else {
            continue;
        };
        for rec in text.lines().filter_map(|l| serde_json::from_str::<Value>(l).ok()) {
            let hello_failed = rec["error"].as_str().is_some_and(|e| e.contains("hello"));
            if let (Some(secs), false) = (rec["startup_secs"].as_f64(), hello_failed) {
                note_hello(label, secs);
            }
        }
    }
}

fn out_dir(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("pdl_adapter_{}_{}", name, std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

fn cut(s: &str) -> String {
    s.chars().take(300).collect()
}

/// `s` from 100 bytes before byte `common` (where two strings first differ), cut.
fn tail_from(s: &str, common: usize) -> String {
    let mut start = common.saturating_sub(100).min(s.len());
    while !s.is_char_boundary(start) {
        start -= 1;
    }
    cut(&s[start..])
}

/// km3 v km3 with the given seats replaced by protocol bots (command, timeout).
fn seats(
    a: &Deck,
    b: &Deck,
    bots: [Option<(String, Duration)>; 2],
    log_dir: &Path,
) -> (Vec<Box<dyn Player>>, [Option<Arc<ProtocolStats>>; 2]) {
    let mut players = create_players(a.clone(), b.clone(), km3_codes());
    let mut stats: [Option<Arc<ProtocolStats>>; 2] = [None, None];
    for (seat, bot) in bots.into_iter().enumerate() {
        if let Some((cmd, timeout)) = bot {
            let deck = if seat == 0 { a.clone() } else { b.clone() };
            let pp = ProtocolPlayer::new(deck, cmd, timeout, Some(log_dir.to_path_buf()));
            stats[seat] = Some(pp.stats());
            players[seat] = Box::new(pp);
        }
    }
    (players, stats)
}

fn bot10(cmd: String) -> Option<(String, Duration)> {
    Some((cmd, Duration::from_millis(10_000)))
}

struct Run {
    decisions: Vec<(usize, u64, String)>,
    state_json: String,
    over: bool,
}

fn run(players: Vec<Box<dyn Player>>, seed: u64, cfg: impl Fn(usize, &mut Rec)) -> Run {
    let decisions: DecisionLog = Rc::new(RefCell::new(Vec::new()));
    let events: EventLog = Rc::new(RefCell::new(Vec::new()));
    let wrapped: Vec<Box<dyn Player>> = players
        .into_iter()
        .enumerate()
        .map(|(seat, inner)| {
            let mut r = Rec::new(seat, inner, &decisions, &events);
            cfg(seat, &mut r);
            Box::new(r) as Box<dyn Player>
        })
        .collect();
    let mut game = Game::new(wrapped, seed);
    game.play();
    let state_json = serde_json::to_string(&game.get_state_clone()).unwrap();
    let over = game.is_game_over();
    drop(game);
    let d = decisions.borrow().clone();
    Run {
        decisions: d,
        state_json,
        over,
    }
}

fn all_cases(ks: u64, orders: &[usize], pairs: &[usize]) -> Vec<(usize, usize, u64)> {
    let mut v = Vec::new();
    for &p in pairs {
        for &o in orders {
            for k in 0..ks {
                v.push((p, o, k));
            }
        }
    }
    v
}

fn compare_runs(ctx: &str, direct: &Run, other: &Run) {
    let n = direct.decisions.len().min(other.decisions.len());
    for i in 0..n {
        if direct.decisions[i] != other.decisions[i] {
            panic!(
                "{ctx}: first differing decision index {i}: direct {} vs adapter {}",
                cut(&format!("{:?}", direct.decisions[i])),
                cut(&format!("{:?}", other.decisions[i]))
            );
        }
    }
    if direct.decisions.len() != other.decisions.len() {
        panic!(
            "{ctx}: decision counts differ: {} vs {}",
            direct.decisions.len(),
            other.decisions.len()
        );
    }
    if direct.state_json != other.state_json {
        let common = direct
            .state_json
            .bytes()
            .zip(other.state_json.bytes())
            .take_while(|(a, b)| a == b)
            .count();
        panic!(
            "{ctx}: final states differ at byte {common}: {} vs {}",
            tail_from(&direct.state_json, common),
            tail_from(&other.state_json, common)
        );
    }
}

#[test]
fn observation_json_round_trip() {
    let dir = out_dir("t1");
    let _ = dir;
    for (p, o, k) in all_cases(3, &[0, 1], &[0, 1, 2, 3]) {
        let (a, b) = decks(p, o);
        let players = create_players(a, b, km3_codes());
        let r = run(players, seed(p, o, k), |_, r| r.check_obs = true);
        assert!(r.over && !r.decisions.is_empty());
    }
}

fn key_set(v: &Value) -> BTreeSet<String> {
    v.as_object().expect("object").keys().cloned().collect()
}

fn set(keys: &[&str]) -> BTreeSet<String> {
    keys.iter().map(|s| s.to_string()).collect()
}

fn captured(cmd_bot: &str, name: &str) -> Vec<Value> {
    let dir = out_dir(name);
    let file = dir.join("captured.jsonl");
    let (a, b) = decks(0, 0);
    let cmd = format!("tee {} | {}", file.display(), cmd_bot);
    let (players, _) = seats(&a, &b, [bot10(cmd), None], &dir);
    let r = run(players, seed(0, 0, 0), |_, _| {});
    note_hellos(name, &dir);
    assert!(r.over);
    let text = std::fs::read_to_string(&file).unwrap();
    assert!(text.ends_with('\n'));
    text.lines()
        .map(|l| serde_json::from_str::<Value>(l).expect("each line is one JSON object"))
        .collect()
}

/// A live bot that opts in to `pdl_observation` and `pdl_events`, writes every line it receives to `file` and
/// always replies `{"i": 0}`.
fn capture_bot(file: &Path) -> String {
    let prog = r#"
import sys, json
f = open(sys.argv[1], "w")
for line in sys.stdin:
    f.write(line)
    f.flush()
    m = json.loads(line)
    if m["type"] == "hello":
        r = {"name": "cap", "pdl_observation": True, "pdl_events": True}
    elif m["type"] == "new_game":
        continue
    else:
        r = {"i": 0}
    print(json.dumps(r), flush=True)
"#;
    format!("python3 -I -c '{}' {}", prog, file.display())
}

#[test]
fn messages_are_single_json_lines() {
    let _python = python_lock();
    let base_decide = [
        "type",
        "ply",
        "state",
        "actions",
        "actor",
        "agent_snapshot",
        "legal_actions",
    ];
    // No opt-in.
    let msgs = captured(&py_cmd("first_legal_bot.py", ""), "t2a");
    assert!(
        key_set(&msgs[0]) == set(&["type", "protocol"]),
        "hello keys"
    );
    assert!(msgs[0]["protocol"] == 1);
    assert!(
        key_set(&msgs[1]) == set(&["type", "game_id", "you", "deck", "deck_definition"]),
        "new_game keys"
    );
    assert!(msgs[1]["deck_definition"].is_null());
    let mut decides = 0;
    for m in &msgs[2..] {
        assert!(m["type"] == "decide");
        assert!(
            key_set(m) == set(&base_decide),
            "decide keys {:?}",
            key_set(m)
        );
        assert!(m["agent_snapshot"].is_null() && m["legal_actions"].is_null());
        for a in m["actions"].as_array().unwrap() {
            assert!(key_set(a) == set(&["i", "text", "action"]));
        }
        decides += 1;
    }
    assert!(decides > 0);
    // pdl_observation opt-in (km3 bot).
    let msgs = captured(&km3_cmd(), "t2b");
    assert!(key_set(&msgs[1]) == set(&["type", "game_id", "you", "deck", "deck_definition"]));
    assert!(msgs[1]["deck_definition"].is_object());
    for m in &msgs[2..] {
        let mut want = set(&base_decide);
        want.insert("pdl_observation".into());
        want.insert("pdl_search_seed".into());
        assert!(key_set(m) == want, "decide keys {:?}", key_set(m));
        assert!(m["legal_actions"].is_array());
    }
    // pdl_events opt-in (plan follower).
    let log = out_dir("t2c").join("plan.jsonl");
    let msgs = captured(
        &py_cmd(
            "plan_follower_bot.py",
            &format!("--seed 1 --log {}", log.display()),
        ),
        "t2c",
    );
    for m in &msgs[2..] {
        let mut want = set(&base_decide);
        want.insert("pdl_since_last".into());
        assert!(key_set(m) == want, "decide keys {:?}", key_set(m));
        assert!(
            key_set(&m["pdl_since_last"])
                == set(&[
                    "chance_events",
                    "cards_left_deck_mine",
                    "cards_left_deck_opponent"
                ])
        );
    }
    // Both opted in, live: what ProtocolPlayer actually sends.
    {
        let dir = out_dir("t2d");
        let file = std::env::temp_dir().join(format!("pdl_t2d_recv_{}.jsonl", std::process::id()));
        let _ = std::fs::remove_file(&file);
        let cmd = capture_bot(&file);
        let (a, b) = decks(0, 0);
        let (players, _) = seats(&a, &b, [bot10(cmd), None], &dir);
        let r = run(players, seed(0, 0, 0), |_, _| {});
        note_hellos("t2d", &dir);
        assert!(r.over);
        let text = std::fs::read_to_string(&file).unwrap();
        assert!(text.ends_with('\n'));
        let msgs: Vec<Value> = text
            .lines()
            .map(|l| serde_json::from_str::<Value>(l).expect("each received line is one JSON line"))
            .collect();
        assert!(msgs.len() > 2);
        assert!(msgs[0]["type"] == "hello");
        assert!(
            key_set(&msgs[0]) == set(&["type", "protocol"]),
            "live hello keys"
        );
        assert!(msgs[1]["type"] == "new_game");
        assert!(
            key_set(&msgs[1]) == set(&["type", "game_id", "you", "deck", "deck_definition"]),
            "live new_game keys"
        );
        assert!(msgs[1]["deck_definition"].is_object());
        let mut want = set(&base_decide);
        for k in ["pdl_observation", "pdl_search_seed", "pdl_since_last"] {
            want.insert(k.into());
        }
        for m in &msgs[2..] {
            assert!(m["type"] == "decide");
            assert!(key_set(m) == want, "live decide keys {:?}", key_set(m));
            assert!(m["legal_actions"].is_array() && m["pdl_observation"].is_object());
        }
        let _ = std::fs::remove_file(&file);
    }
    // Both opted in, built directly: exactly the three extra keys; one line.
    let (a, b) = decks(0, 0);
    let mut game = Game::new(create_players(a, b, km3_codes()), seed(0, 0, 0));
    for _ in 0..10 {
        game.play_tick();
    }
    let obs = game.observation(game.get_state_clone().generate_possible_actions().0);
    let (_, acts) = game.get_state_clone().generate_possible_actions();
    let msg = deckgym::protocol::DecideMsg {
        kind: "decide".into(),
        ply: 1,
        state: ViewState::for_observation(&obs),
        actions: vec![],
        actor: obs.actor,
        agent_snapshot: None,
        legal_actions: Some(acts),
        pdl_observation: Some(obs.clone()),
        pdl_search_seed: Some(None),
        pdl_since_last: Some(SinceLast::default()),
    };
    let line = serde_json::to_string(&msg).unwrap() + "\n";
    assert!(line.ends_with('\n') && !line[..line.len() - 1].contains('\n'));
    let v: Value = serde_json::from_str(&line).unwrap();
    let mut want = set(&base_decide);
    for k in ["pdl_observation", "pdl_search_seed", "pdl_since_last"] {
        want.insert(k.into());
    }
    assert!(key_set(&v) == want);
    assert!(v["pdl_search_seed"].is_null());
}

#[test]
fn view_state_hides_hidden_information() {
    let (a, b) = decks(0, 0);
    let mut game = Game::new(create_players(a, b, km3_codes()), seed(0, 0, 0));
    while !game.is_game_over() && game.get_state_clone().turn_count < 6 {
        game.play_tick();
    }
    let s = game.get_state_clone();
    for actor in 0..2 {
        let opp = 1 - actor;
        let mut s2 = s.clone();
        for p in 0..2 {
            s2.decks[p].cards.reverse();
        }
        let filler = s.decks[actor].cards[0].clone();
        for c in s2.hands[opp].iter_mut() {
            *c = filler.clone();
        }
        for c in s2.decks[opp].cards.iter_mut() {
            *c = filler.clone();
        }
        let v1 = ViewState::for_observation(&PlayerObservation::from_state(
            &s,
            actor,
            &RevealedKnowledge::default(),
        ));
        let v2 = ViewState::for_observation(&PlayerObservation::from_state(
            &s2,
            actor,
            &RevealedKnowledge::default(),
        ));
        let j1 = serde_json::to_string(&v1).unwrap();
        let j2 = serde_json::to_string(&v2).unwrap();
        assert!(
            j1 == j2,
            "actor {actor}: views differ: {} vs {}",
            cut(&j1),
            cut(&j2)
        );
        let val: Value = serde_json::from_str(&j1).unwrap();
        assert!(val["players"][opp]["hand"].is_null());
        for p in 0..2 {
            assert_eq!(v1.players[p].deck_count, s.decks[p].cards.len());
            assert_eq!(v1.players[p].hand_count, s.hands[p].len());
        }
        assert_eq!(
            v1.players[actor].hand.as_ref().unwrap().len(),
            s.hands[actor].len()
        );
    }
}

fn parity(both: bool) {
    let n: u64 = std::env::var("ADAPTER_PARITY_GAMES")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(3);
    let mut totals = [0u64; 2];
    let (mut zero, mut total_seat_games) = (0u64, 0u64);
    for (p, o, k) in all_cases(n, &[0, 1], &[0, 1, 2, 3]) {
        let (a, b) = decks(p, o);
        let sd = seed(p, o, k);
        let direct = run(
            create_players(a.clone(), b.clone(), km3_codes()),
            sd,
            |_, _| {},
        );
        let dir = out_dir(&format!("parity{}", both as u8));
        let bots = [bot10(km3_cmd()), if both { bot10(km3_cmd()) } else { None }];
        let (players, stats) = seats(&a, &b, bots, &dir);
        let via = run(players, sd, |_, _| {});
        let ctx = format!("pair {p} order {o} seed {sd}");
        compare_runs(&ctx, &direct, &via);
        for (seat, st) in stats.iter().enumerate() {
            if let Some(st) = st {
                assert_eq!(
                    st.fallbacks.load(Ordering::SeqCst),
                    0,
                    "{ctx} seat {seat}: fallbacks"
                );
                let d = st.decisions.load(Ordering::SeqCst);
                totals[seat] += d;
                total_seat_games += 1;
                if d == 0 {
                    zero += 1;
                }
            }
        }
    }
    for (seat, total) in totals.iter().enumerate() {
        let protocol_seat = seat == 0 || both;
        assert!(
            !protocol_seat || *total > 0,
            "all {} games of the run ({}): protocol seat {seat} was asked no decision at all",
            n * 8,
            if both { "both" } else { "one" }
        );
    }
    println!(
        "PARITY_ZERO_DECISION_SEAT_GAMES mode={} count={} of {}",
        if both { "both" } else { "one" },
        zero,
        total_seat_games
    );
}

#[test]
fn parity_km3_one_seat_through_adapter() {
    parity(false);
}

#[test]
fn parity_km3_both_seats_through_adapter() {
    parity(true);
}

#[test]
fn first_legal_bot_finishes() {
    let _python = python_lock();
    for (p, o, k) in all_cases(3, &[0, 1], &[0, 1, 2, 3]) {
        // Each game gets 30 s: it runs on its own thread so a stuck game fails here with a clear message.
        let (tx, rx) = mpsc::channel();
        let game = std::thread::spawn(move || {
            let (a, b) = decks(p, o);
            let dir = out_dir("t6");
            let (players, stats) = seats(
                &a,
                &b,
                [bot10(py_cmd("first_legal_bot.py", "")), None],
                &dir,
            );
            let r = run(players, seed(p, o, k), |seat, r| r.first_legal = seat == 0);
            note_hellos("t6", &dir);
            let _ = tx.send(());
            (r, stats)
        });
        if let Err(mpsc::RecvTimeoutError::Timeout) = rx.recv_timeout(Duration::from_secs(30)) {
            panic!("pair {p} order {o} k {k}: game did not finish in 30 s");
        }
        let (r, stats) = game.join().unwrap_or_else(|e| std::panic::resume_unwind(e));
        assert!(r.over);
        let st = stats[0].as_ref().unwrap();
        assert_eq!(st.fallbacks.load(Ordering::SeqCst), 0);
        assert!(st.decisions.load(Ordering::SeqCst) > 0);
    }
}

#[test]
fn seeded_random_bot_is_reproducible() {
    let _python = python_lock();
    let (a, b) = decks(0, 0);
    let mut runs = Vec::new();
    for _ in 0..2 {
        let dir = out_dir("t7");
        let (players, stats) = seats(
            &a,
            &b,
            [bot10(py_cmd("seeded_random_bot.py", "--seed 7")), None],
            &dir,
        );
        let r = run(players, seed(0, 0, 0), |_, _| {});
        note_hellos("t7", &dir);
        assert!(r.over);
        assert_eq!(
            stats[0].as_ref().unwrap().fallbacks.load(Ordering::SeqCst),
            0
        );
        runs.push(r);
    }
    compare_runs("seeded_random seed 7", &runs[0], &runs[1]);
}

#[test]
fn upstream_random_bot_plays_in_our_engine() {
    let _python = python_lock();
    for p in 0..4 {
        let (a, b) = decks(p, 0);
        let dir = out_dir("t8");
        let (players, stats) = seats(&a, &b, [bot10(py_cmd("random_bot.py", "")), None], &dir);
        let r = run(players, seed(p, 0, 0), |_, _| {});
        note_hellos("t8", &dir);
        assert!(r.over);
        assert_eq!(
            stats[0].as_ref().unwrap().fallbacks.load(Ordering::SeqCst),
            0
        );
    }
}

fn group_alive(pid: u32) -> bool {
    std::process::Command::new("kill")
        .args(["-0", "--", &format!("-{pid}")])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

#[test]
fn bot_failures_fall_back_and_are_counted() {
    let _python = python_lock();
    for mode in ["garbage", "range", "sleep", "exit", "nohello"] {
        let (a, b) = decks(0, 0);
        let dir = out_dir("t9");
        let bot = Some((
            py_cmd("test_bad_bot.py", &format!("--mode {mode}")),
            Duration::from_millis(5000),
        ));
        let (players, stats) = seats(&a, &b, [bot, None], &dir);
        let start = Instant::now();
        let r = run(players, seed(0, 0, 0), |_, _| {});
        note_hellos(&format!("t9 {mode}"), &dir);
        assert!(r.over, "{mode}: game finished");
        if mode == "sleep" {
            assert!(
                start.elapsed() < Duration::from_secs(30),
                "sleep game took too long"
            );
        }
        let st = stats[0].as_ref().unwrap();
        let (d, f) = (
            st.decisions.load(Ordering::SeqCst),
            st.fallbacks.load(Ordering::SeqCst),
        );
        if mode == "nohello" {
            assert_eq!(f, d, "{mode}");
        } else {
            assert!(d >= 3, "{mode}: decisions {d} fallbacks {f}");
            assert_eq!(f, d - 2, "{mode}");
        }
        let pid = st.child_pid.load(Ordering::SeqCst);
        assert!(pid != 0, "{mode}: spawned");
        let deadline = Instant::now() + Duration::from_secs(2);
        while group_alive(pid) && Instant::now() < deadline {
            std::thread::sleep(Duration::from_millis(50));
        }
        assert!(!group_alive(pid), "{mode}: process group still alive");
        assert!(
            !Path::new(&format!("/proc/{pid}")).exists(),
            "{mode}: /proc entry remains"
        );
    }
}

#[test]
fn public_events_are_classified() {
    let mut seen = (false, false, false, false);
    for p in 0..4 {
        let (a, b) = decks(p, 0);
        let decisions: DecisionLog = Rc::new(RefCell::new(Vec::new()));
        let events: EventLog = Rc::new(RefCell::new(Vec::new()));
        let players: Vec<Box<dyn Player>> = create_players(a, b, km3_codes())
            .into_iter()
            .enumerate()
            .map(|(seat, inner)| {
                Box::new(Rec::new(seat, inner, &decisions, &events)) as Box<dyn Player>
            })
            .collect();
        let mut game = Game::new(players, seed(p, 0, 0));
        while !game.is_game_over() {
            let s = game.get_state_clone();
            let (actor, acts) = s.generate_possible_actions();
            let before = events.borrow().len();
            let action = game.play_tick();
            let log = events.borrow();
            assert_eq!(log.len(), before + 2, "pair {p}: two events per tick");
            let (s0, e0) = log[before];
            let (s1, e1) = log[before + 1];
            assert!(
                s0 == 0 && s1 == 1 && e0 == e1,
                "pair {p}: same event to both seats"
            );
            let ev = e0;
            assert_eq!(ev.actor, actor);
            assert_eq!(ev.was_choice, acts.len() > 1);
            if let SimpleAction::DrawCard { amount } = &action.action {
                assert_eq!(
                    ev.cards_left_deck[actor],
                    (*amount as usize).min(s.decks[actor].cards.len()),
                    "pair {p}: draw"
                );
                seen.3 = true;
            }
            if let Ok(o) = deckgym::actions::try_forecast_action(&s, &action) {
                if o.into_branches().0.len() > 1 {
                    assert!(ev.chance, "pair {p}: multi-branch outcome without chance");
                }
            }
            // An EndTurn may hand the turn end to forced steps (Quick Growth -> Checkup), so the Energy roll belongs to the tick on which the turn advances.
            let t = game.get_state_clone();
            if s.turn_count >= 1 && t.turn_count > s.turn_count && !game.is_game_over() {
                assert!(
                    ev.chance,
                    "pair {p}: turn {} advanced without a chance event",
                    s.turn_count
                );
            }
            if ev.was_choice {
                seen.1 = true
            } else {
                seen.0 = true
            }
            if !ev.chance {
                seen.2 = true
            }
        }
    }
    assert!(
        seen.0 && seen.1 && seen.2 && seen.3,
        "missing event kinds: {seen:?}"
    );
}

fn read_jsonl(path: &Path) -> Vec<Value> {
    std::fs::read_to_string(path)
        .unwrap()
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

#[test]
fn pdl_since_last_reaches_the_bot() {
    let _python = python_lock();
    for (p, o, k) in all_cases(3, &[0, 1], &[0]) {
        let (a, b) = decks(p, o);
        let dir = out_dir("t11");
        let log = dir.join("plan.jsonl");
        let cmd = py_cmd(
            "plan_follower_bot.py",
            &format!("--seed 11 --log {}", log.display()),
        );
        let (players, stats) = seats(&a, &b, [bot10(cmd), None], &dir);
        let since: SinceLog = Rc::new(RefCell::new(Vec::new()));
        let s2 = since.clone();
        let r = run(players, seed(p, o, k), move |seat, r| {
            if seat == 0 {
                r.since = Some(s2.clone());
            }
        });
        note_hellos("t11", &dir);
        assert!(r.over);
        assert_eq!(
            stats[0].as_ref().unwrap().fallbacks.load(Ordering::SeqCst),
            0
        );
        let recs = read_jsonl(&log);
        let want = since.borrow();
        assert_eq!(
            recs.len(),
            want.len(),
            "pair {p} order {o} k {k}: record count"
        );
        for (i, (rec, w)) in recs.iter().zip(want.iter()).enumerate() {
            let got: SinceLast = serde_json::from_value(rec["pdl_since_last"].clone()).unwrap();
            assert!(
                got == *w,
                "pair {p} order {o} k {k} index {i}: bot saw {got:?}, forwarded {w:?}"
            );
        }
    }
}

fn take(cards: &mut Vec<Card>, id: CardId) -> Card {
    let card = get_card_by_enum(id);
    cards.remove(cards.iter().position(|c| *c == card).expect("card in deck"))
}

/// Turn 1, seat 1 went first: no Zone Energy, no Energy on its Ekans and no Bench, so ending the turn is its only
/// option unless the `hidden` card in its hand can be played. Everything else is the same for every `hidden`.
fn hidden_option_state(hidden: CardId) -> State {
    let (a, b) = load_test_decks();
    let mut state = State::initialize(&a, &b, &mut StdRng::seed_from_u64(14));
    let (mut own, mut opp) = (a.cards.clone(), b.cards.clone());
    take(&mut own, CardId::A1001Bulbasaur);
    take(&mut opp, CardId::A1164Ekans);
    let arbok = take(&mut opp, CardId::A1165Arbok);
    take(&mut opp, CardId::A1176Koffing);
    take(&mut opp, CardId::A1177Weezing);
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1164Ekans)],
    );
    state.hands[0] = own.drain(..4).collect();
    state.hands[1] = vec![arbok, get_card_by_enum(hidden)];
    state.decks[0].cards = own;
    state.decks[1].cards = opp;
    state.turn_count = 1;
    state.current_player = 1;
    state
}

/// The capture bot (seat 0) against EndTurnPlayer (seat 1) from `hidden_option_state(hidden)` to the end of the
/// game: every action played, and every decide line the bot received. The bot must answer every decision itself
/// (no fallback) and every decide must carry both opt-in blocks, so the comparison covers the whole game and the
/// `pdl_` fields, not only the v1 ones.
fn hidden_option_game(hidden: CardId, name: &str) -> (Vec<Action>, Vec<String>) {
    let dir = out_dir(name);
    let file = dir.join("received.jsonl");
    let (a, b) = load_test_decks();
    let bot = ProtocolPlayer::new(
        a,
        capture_bot(&file),
        Duration::from_millis(10_000),
        Some(dir.clone()),
    );
    let stats = bot.stats();
    let players: Vec<Box<dyn Player>> = vec![Box::new(bot), Box::new(EndTurnPlayer { deck: b })];
    let mut game = Game::from_state(hidden_option_state(hidden), players, 14);
    let mut played = Vec::new();
    while !game.is_game_over() {
        played.push(game.play_tick());
    }
    drop(game);
    note_hellos(name, &dir);
    let decides: Vec<String> = std::fs::read_to_string(&file)
        .unwrap()
        .lines()
        .filter(|l| serde_json::from_str::<Value>(l).unwrap()["type"] == "decide")
        .map(str::to_string)
        .collect();
    assert_eq!(stats.fallbacks.load(Ordering::SeqCst), 0, "{name}: fallbacks");
    assert_eq!(
        stats.decisions.load(Ordering::SeqCst),
        decides.len() as u64,
        "{name}: decisions v decide lines"
    );
    for (i, d) in decides.iter().enumerate() {
        let v: Value = serde_json::from_str(d).unwrap();
        assert!(
            v["pdl_since_last"].is_object() && v["pdl_observation"].is_object(),
            "{name}: decide {i} lacks an opt-in block"
        );
    }
    (played, decides)
}

/// How many legal actions the opponent had depends on its hidden hand, so no decide line may change with it.
#[test]
fn opponent_hidden_options_do_not_reach_the_bot() {
    let _python = python_lock();
    // Weezing cannot be played on turn 1; Koffing can go to any of the three Bench slots.
    let forced = hidden_option_state(CardId::A1177Weezing);
    let open = hidden_option_state(CardId::A1176Koffing);
    assert_eq!(forced.generate_possible_actions().1.len(), 1);
    assert_eq!(open.generate_possible_actions().1.len(), 4);
    let (forced_played, forced_decides) = hidden_option_game(CardId::A1177Weezing, "t14a");
    let (open_played, open_decides) = hidden_option_game(CardId::A1176Koffing, "t14b");
    assert!(
        forced_played == open_played,
        "the two games played different actions"
    );
    assert!(!forced_decides.is_empty());
    assert_eq!(forced_decides.len(), open_decides.len(), "decide count");
    for (i, (f, o)) in forced_decides.iter().zip(&open_decides).enumerate() {
        if f != o {
            let common = f.bytes().zip(o.bytes()).take_while(|(x, y)| x == y).count();
            panic!(
                "decide {i} differs at byte {common}: {} vs {}",
                tail_from(f, common),
                tail_from(o, common)
            );
        }
    }
}

#[test]
fn plan_follower_plays_full_games() {
    let _python = python_lock();
    let mut reasons: std::collections::BTreeMap<String, usize> = Default::default();
    let mut from_saved = 0;
    for (p, o, k) in all_cases(3, &[0, 1], &[0, 1, 2, 3]) {
        let (a, b) = decks(p, o);
        let dir = out_dir("t12");
        let log = dir.join("plan.jsonl");
        let cmd = py_cmd(
            "plan_follower_bot.py",
            &format!("--seed 12 --log {}", log.display()),
        );
        let (players, stats) = seats(&a, &b, [bot10(cmd), None], &dir);
        let r = run(players, seed(p, o, k), |_, _| {});
        note_hellos("t12", &dir);
        assert!(r.over);
        assert_eq!(
            stats[0].as_ref().unwrap().fallbacks.load(Ordering::SeqCst),
            0
        );
        for rec in read_jsonl(&log) {
            if let Some(r) = rec["reask_reason"].as_str() {
                *reasons.entry(r.to_string()).or_default() += 1;
            }
            if rec["played_from_saved_plan"] == true {
                from_saved += 1;
            }
        }
    }
    eprintln!("reask reasons: {reasons:?}; played_from_saved_plan: {from_saved}");
    for want in ["chance", "draw_mine", "stale"] {
        assert!(
            reasons.get(want).copied().unwrap_or(0) >= 1,
            "no reask_reason {want}: {reasons:?}"
        );
    }
    assert!(from_saved >= 1);
}

#[test]
fn cli_proto_seat_plays() {
    let (pa, pb) = PAIRS[0];
    let deck_path = |n: &str| {
        format!(
            "{}/../decks/screen/opponents/{}.txt",
            env!("CARGO_MANIFEST_DIR"),
            n
        )
    };
    let logs = out_dir("t13_logs");
    let results = out_dir("t13_results");
    let out = std::process::Command::new(env!("CARGO_BIN_EXE_deckgym"))
        .args([
            "simulate",
            &deck_path(pa),
            &deck_path(pb),
            "--players",
            "proto,km3",
            "--bot-a",
            &km3_cmd(),
        ])
        .args([
            "--bot-log",
            logs.to_str().unwrap(),
            "--results-output",
            results.to_str().unwrap(),
        ])
        .args(["--num", "2", "--seed", "25102000000", "--seed-stream"])
        .output()
        .unwrap();
    assert!(
        out.status.success(),
        "exit {:?}: {}",
        out.status.code(),
        cut(&String::from_utf8_lossy(&out.stderr))
    );
    let mut summaries = 0;
    for entry in std::fs::read_dir(&logs).unwrap() {
        let path = entry.unwrap().path();
        for rec in read_jsonl(&path) {
            if rec["summary"] == true {
                assert_eq!(rec["fallbacks"], 0);
                summaries += 1;
            }
        }
    }
    assert_eq!(summaries, 2, "summary lines");
    let mut records = 0;
    for entry in std::fs::read_dir(&results).unwrap() {
        let path = entry.unwrap().path();
        if path.extension().is_some_and(|e| e == "json") {
            let _: Value = serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
            records += 1;
        }
    }
    assert_eq!(records, 2, "result records");
    let bad = std::process::Command::new(env!("CARGO_BIN_EXE_deckgym"))
        .args([
            "simulate",
            &deck_path(pa),
            &deck_path(pb),
            "--players",
            "proto,km3",
            "--num",
            "1",
            "--seed",
            "1",
        ])
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(2));
}
