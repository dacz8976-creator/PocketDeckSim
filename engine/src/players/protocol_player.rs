//! A `Player` that plays the replies of a subprocess speaking upstream's bot protocol v1
//! (plus the opt-in `pdl_*` extensions, see docs/pdl-protocol-extensions.md).
use super::Player;
use crate::{
    actions::Action,
    game::DecisionRandomness,
    observation::PlayerObservation,
    protocol::{
        view::ViewState, ActionMsg, DecideMsg, HelloMsg, NewGameMsg, PublicEvent, SinceLast,
    },
    Deck, State,
};
use rand::rngs::StdRng;
use serde::Serialize;
use std::{
    fs::File,
    io::{BufRead, BufReader, Write},
    os::unix::process::CommandExt,
    path::PathBuf,
    process::{Child, ChildStdin, Command, Stdio},
    sync::{
        atomic::{AtomicU32, AtomicU64, Ordering},
        mpsc::{channel, Receiver},
        Arc,
    },
    time::{Duration, Instant},
};

static NEXT_INSTANCE: AtomicU64 = AtomicU64::new(0);

#[derive(Debug, Default)]
pub struct ProtocolStats {
    pub decisions: AtomicU64,
    pub fallbacks: AtomicU64,
    /// 0 = never spawned.
    pub child_pid: AtomicU32,
}

#[derive(Debug)]
struct Spawned {
    child: Child,
    stdin: Option<ChildStdin>,
    rx: Receiver<String>,
    agent_snapshot: bool,
    pdl_observation: bool,
    pdl_events: bool,
}

#[derive(Debug)]
pub struct ProtocolPlayer {
    deck: Deck,
    command: String,
    timeout: Duration,
    stats: Arc<ProtocolStats>,
    bot: Option<Spawned>,
    spawn_attempted: bool,
    failed: bool,
    killed: bool,
    ply: u64,
    search_seed: Option<u64>,
    choices_by_seat: [u64; 2],
    chance: u64,
    cards_left: [usize; 2],
    instance: u64,
    log: Option<File>,
    errors: u64,
    bot_name: Option<String>,
    ignored_optional_keys: u64,
    first_ignored: Option<String>,
    /// Spawn + hello + new_game time of the first decision (taken when logged).
    startup_secs: Option<f64>,
    /// Round trip of the decide just asked (None when no decide was written).
    roundtrip_secs: Option<f64>,
}

fn write_line<T: Serialize>(stdin: &mut ChildStdin, msg: &T) -> Result<(), String> {
    let mut line = serde_json::to_string(msg).map_err(|e| format!("serialize: {e}"))?;
    line.push('\n');
    stdin
        .write_all(line.as_bytes())
        .map_err(|e| e.to_string())?;
    stdin.flush().map_err(|e| e.to_string())
}

fn kill_group(pid: u32) {
    let _ = Command::new("kill")
        .args(["-KILL", "--", &format!("-{pid}")])
        .stderr(Stdio::null())
        .status();
}

impl ProtocolPlayer {
    pub fn new(deck: Deck, command: String, timeout: Duration, log_dir: Option<PathBuf>) -> Self {
        let instance = NEXT_INSTANCE.fetch_add(1, Ordering::SeqCst);
        let log = log_dir.and_then(|dir| {
            std::fs::create_dir_all(&dir).ok()?;
            File::create(dir.join(format!(
                "protocol_{}_{}.jsonl",
                std::process::id(),
                instance
            )))
            .ok()
        });
        ProtocolPlayer {
            deck,
            command,
            timeout,
            stats: Arc::new(ProtocolStats::default()),
            bot: None,
            spawn_attempted: false,
            failed: false,
            killed: false,
            ply: 0,
            search_seed: None,
            choices_by_seat: [0; 2],
            chance: 0,
            cards_left: [0; 2],
            instance,
            log,
            errors: 0,
            bot_name: None,
            ignored_optional_keys: 0,
            first_ignored: None,
            startup_secs: None,
            roundtrip_secs: None,
        }
    }

    pub fn stats(&self) -> Arc<ProtocolStats> {
        self.stats.clone()
    }

    fn note_ignored(&mut self, what: String) {
        self.ignored_optional_keys += 1;
        if self.first_ignored.is_none() {
            self.first_ignored = Some(what);
        }
    }

    fn ensure_spawned(&mut self, you: usize) -> Result<(), String> {
        if self.spawn_attempted {
            return Ok(());
        }
        self.spawn_attempted = true;
        let mut child = Command::new("sh")
            .arg("-c")
            .arg(&self.command)
            .process_group(0)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .map_err(|e| format!("spawn failed: {e}"))?;
        self.stats.child_pid.store(child.id(), Ordering::SeqCst);
        let stdin = child.stdin.take();
        let stdout = child.stdout.take();
        let (tx, rx) = channel::<String>();
        if let Some(stdout) = stdout {
            std::thread::spawn(move || {
                let mut reader = BufReader::new(stdout);
                loop {
                    let mut line = String::new();
                    match reader.read_line(&mut line) {
                        Ok(0) | Err(_) => break,
                        Ok(_) => {
                            if tx.send(line).is_err() {
                                break;
                            }
                        }
                    }
                }
            });
        }
        // Registered before the handshake so a failure there still reaps the child.
        self.bot = Some(Spawned {
            child,
            stdin,
            rx,
            agent_snapshot: false,
            pdl_observation: false,
            pdl_events: false,
        });
        let timeout = self.timeout;
        let deck_ids: Vec<String> = self.deck.cards.iter().map(|c| c.get_id()).collect();
        let bot = self.bot.as_mut().unwrap();
        let stdin = bot.stdin.as_mut().ok_or("no stdin")?;
        write_line(stdin, &HelloMsg::new()).map_err(|e| format!("failed writing hello: {e}"))?;
        let reply = bot
            .rx
            .recv_timeout(timeout)
            .map_err(|_| "bot did not reply to hello in time".to_string())?;
        let value: serde_json::Value =
            serde_json::from_str(&reply).map_err(|e| format!("invalid hello reply: {e}"))?;
        if !value.is_object() {
            return Err("hello reply is not a JSON object".into());
        }
        let mut ignored: Vec<String> = Vec::new();
        let mut flag = |key: &str| -> bool {
            match value.get(key) {
                None => false,
                Some(serde_json::Value::Bool(b)) => *b,
                Some(other) => {
                    ignored.push(format!("hello.{key} wrong type: {other}"));
                    false
                }
            }
        };
        bot.agent_snapshot = flag("agent_snapshot");
        bot.pdl_observation = flag("pdl_observation");
        bot.pdl_events = flag("pdl_events");
        let name = match value.get("name") {
            None => None,
            Some(serde_json::Value::String(n)) => Some(n.clone()),
            Some(other) => {
                ignored.push(format!("hello.name wrong type: {other}"));
                None
            }
        };
        self.bot_name = name;
        for w in ignored {
            self.note_ignored(w);
        }
        let bot = self.bot.as_mut().unwrap();
        let msg = NewGameMsg {
            kind: "new_game".into(),
            game_id: uuid::Uuid::new_v4().to_string(),
            you,
            deck: deck_ids,
            deck_definition: if bot.agent_snapshot || bot.pdl_observation {
                Some(self.deck.clone())
            } else {
                None
            },
        };
        let stdin = bot.stdin.as_mut().ok_or("no stdin")?;
        write_line(stdin, &msg).map_err(|e| format!("failed writing new_game: {e}"))
    }

    fn ask(
        &mut self,
        observation: &PlayerObservation,
        actions: &[Action],
        since: SinceLast,
        seed: Option<u64>,
    ) -> Result<usize, String> {
        let first_spawn = !self.spawn_attempted;
        let t0 = Instant::now();
        let spawned = self.ensure_spawned(observation.actor);
        if first_spawn {
            self.startup_secs = Some(t0.elapsed().as_secs_f64());
        }
        spawned?;
        let ply = self.ply;
        let timeout = self.timeout;
        let bot = self.bot.as_mut().ok_or("bot not running")?;
        let full = bot.agent_snapshot || bot.pdl_observation;
        let agent_snapshot = if bot.agent_snapshot {
            let mut snap = observation.visible_state().clone();
            snap.decks[observation.actor].cards =
                vec![crate::models::Card::Unknown; observation.known_own_deck.len()];
            Some(snap)
        } else {
            None
        };
        let msg = DecideMsg {
            kind: "decide".into(),
            ply,
            state: ViewState::for_observation(observation),
            actions: actions
                .iter()
                .enumerate()
                .map(|(i, a)| ActionMsg {
                    i,
                    text: a.action.to_string(),
                    action: a.action.clone(),
                })
                .collect(),
            actor: observation.actor,
            agent_snapshot,
            legal_actions: if full { Some(actions.to_vec()) } else { None },
            pdl_observation: if bot.pdl_observation {
                Some(observation.clone())
            } else {
                None
            },
            pdl_search_seed: if bot.pdl_observation {
                Some(seed)
            } else {
                None
            },
            pdl_since_last: if bot.pdl_events { Some(since) } else { None },
        };
        let stdin = bot.stdin.as_mut().ok_or("no stdin")?;
        let t1 = Instant::now();
        write_line(stdin, &msg).map_err(|e| format!("failed writing decide: {e}"))?;
        let received = bot.rx.recv_timeout(timeout);
        self.roundtrip_secs = Some(t1.elapsed().as_secs_f64());
        let reply = received.map_err(|e| match e {
            std::sync::mpsc::RecvTimeoutError::Timeout => "bot timed out".to_string(),
            std::sync::mpsc::RecvTimeoutError::Disconnected => {
                "bot process exited unexpectedly".to_string()
            }
        })?;
        let value: serde_json::Value =
            serde_json::from_str(&reply).map_err(|e| format!("invalid decide reply: {e}"))?;
        let obj = value
            .as_object()
            .ok_or_else(|| "decide reply is not a JSON object".to_string())?;
        let i = obj
            .get("i")
            .ok_or_else(|| "decide reply has no i".to_string())?
            .as_u64()
            .ok_or_else(|| "decide reply i is not a non-negative integer".to_string())?;
        if i >= actions.len() as u64 {
            return Err(format!(
                "i={} out of range for {} actions",
                i,
                actions.len()
            ));
        }
        let mut ignored: Vec<String> = Vec::new();
        match obj.get("note") {
            None | Some(serde_json::Value::String(_)) => {}
            Some(other) => ignored.push(format!("decide.note wrong type: {other}")),
        }
        if let Some(sc) = obj.get("scores") {
            let ok = sc.as_array().is_some_and(|a| {
                a.len() == actions.len()
                    && a.iter().all(|x| x.as_f64().is_some_and(|f| f.is_finite()))
            });
            if !ok {
                ignored.push(format!("decide.scores malformed: {sc}"));
            }
        }
        for w in ignored {
            self.note_ignored(w);
        }
        Ok(i as usize)
    }

    fn kill_bot(&mut self) {
        if let Some(mut bot) = self.bot.take() {
            bot.stdin = None;
            if !self.killed {
                kill_group(bot.child.id());
            }
            let _ = bot.child.wait();
            self.killed = true;
        }
    }
}

impl Player for ProtocolPlayer {
    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }

    fn before_decision(&mut self, decision: &DecisionRandomness) {
        self.search_seed = Some(decision.search_seed);
    }

    fn on_public_event(&mut self, e: &PublicEvent) {
        self.choices_by_seat[e.actor] += e.was_choice as u64;
        self.chance += e.chance as u64;
        for s in 0..2 {
            self.cards_left[s] += e.cards_left_deck[s];
        }
    }

    fn decision_fn(
        &mut self,
        _rng: &mut StdRng,
        observation: &PlayerObservation,
        actions: &[Action],
    ) -> Action {
        self.ply += 1;
        self.stats.decisions.fetch_add(1, Ordering::SeqCst);
        let me = observation.actor;
        let since = SinceLast {
            opponent_choices: self.choices_by_seat[1 - me],
            chance_events: self.chance,
            cards_left_deck_mine: self.cards_left[me],
            cards_left_deck_opponent: self.cards_left[1 - me],
        };
        self.choices_by_seat = [0; 2];
        self.chance = 0;
        self.cards_left = [0; 2];
        let seed = self.search_seed.take();
        self.roundtrip_secs = None;
        self.startup_secs = None;
        let result = if self.failed {
            Err("bot failed earlier in this game".to_string())
        } else {
            self.ask(observation, actions, since, seed)
        };
        let secs = self.roundtrip_secs.take();
        let startup_secs = self.startup_secs.take();
        let (index, error) = match result {
            Ok(i) => (i, None),
            Err(e) => {
                self.stats.fallbacks.fetch_add(1, Ordering::SeqCst);
                self.errors += 1;
                if !self.failed {
                    self.failed = true;
                    self.kill_bot();
                }
                (0, Some(e))
            }
        };
        if let Some(log) = self.log.as_mut() {
            let line = serde_json::json!({
                "instance": self.instance, "ply": self.ply, "search_seed": seed, "n_actions": actions.len(),
                "i": index, "secs": secs, "startup_secs": startup_secs, "fallback": error.is_some(), "error": error, "bot_name": self.bot_name,
            });
            let _ = writeln!(log, "{line}");
        }
        actions[index].clone()
    }

    fn decide_omniscient(
        &mut self,
        _rng: &mut StdRng,
        _state: &State,
        _actions: &[Action],
    ) -> Action {
        panic!("ProtocolPlayer plays only through decision_fn (PlayerObservation); it has no omniscient entry point");
    }
}

impl Drop for ProtocolPlayer {
    fn drop(&mut self) {
        self.kill_bot();
        let pid = self.stats.child_pid.load(Ordering::SeqCst);
        if let Some(log) = self.log.as_mut() {
            let line = serde_json::json!({
                "summary": true,
                "decisions": self.stats.decisions.load(Ordering::SeqCst),
                "fallbacks": self.stats.fallbacks.load(Ordering::SeqCst),
                "errors": self.errors,
                "ignored_optional_keys": self.ignored_optional_keys,
                "first_ignored": self.first_ignored,
                "child_pid": if pid == 0 { None } else { Some(pid) },
            });
            let _ = writeln!(log, "{line}");
        }
    }
}
