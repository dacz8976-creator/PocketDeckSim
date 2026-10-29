//! A `Player` that plays the replies of a subprocess speaking upstream's bot protocol v1
//! (plus the opt-in `pdl_*` extensions, see docs/pdl-protocol-extensions.md).
use super::Player;
use crate::{
    actions::Action,
    game::DecisionRandomness,
    observation::PlayerObservation,
    protocol::{
        view::ViewState, ActionMsg, DecideMsg, DecideReply, HelloMsg, HelloReply, NewGameMsg, PublicEvent, SinceLast,
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
}

fn write_line<T: Serialize>(stdin: &mut ChildStdin, msg: &T) -> Result<(), String> {
    let mut line = serde_json::to_string(msg).map_err(|e| format!("serialize: {e}"))?;
    line.push('\n');
    stdin.write_all(line.as_bytes()).map_err(|e| e.to_string())?;
    stdin.flush().map_err(|e| e.to_string())
}

fn kill_group(pid: u32) {
    let _ = Command::new("kill").args(["-KILL", "--", &format!("-{pid}")]).stderr(Stdio::null()).status();
}

impl ProtocolPlayer {
    pub fn new(deck: Deck, command: String, timeout: Duration, log_dir: Option<PathBuf>) -> Self {
        let instance = NEXT_INSTANCE.fetch_add(1, Ordering::SeqCst);
        let log = log_dir.and_then(|dir| {
            std::fs::create_dir_all(&dir).ok()?;
            File::create(dir.join(format!("protocol_{}_{}.jsonl", std::process::id(), instance))).ok()
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
        }
    }

    pub fn stats(&self) -> Arc<ProtocolStats> {
        self.stats.clone()
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
        let reply = bot.rx.recv_timeout(timeout).map_err(|_| "bot did not reply to hello in time".to_string())?;
        let value: serde_json::Value = serde_json::from_str(&reply).map_err(|e| format!("invalid hello reply: {e}"))?;
        if !value.is_object() {
            return Err("hello reply is not a JSON object".into());
        }
        let hello: HelloReply = serde_json::from_value(value).map_err(|e| format!("bad hello reply: {e}"))?;
        bot.agent_snapshot = hello.agent_snapshot.unwrap_or(false);
        bot.pdl_observation = hello.pdl_observation.unwrap_or(false);
        bot.pdl_events = hello.pdl_events.unwrap_or(false);
        self.bot_name = hello.name;
        let msg = NewGameMsg {
            kind: "new_game".into(),
            game_id: uuid::Uuid::new_v4().to_string(),
            you,
            deck: deck_ids,
            deck_definition: if bot.agent_snapshot || bot.pdl_observation { Some(self.deck.clone()) } else { None },
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
        self.ensure_spawned(observation.actor)?;
        let ply = self.ply;
        let timeout = self.timeout;
        let bot = self.bot.as_mut().ok_or("bot not running")?;
        let full = bot.agent_snapshot || bot.pdl_observation;
        let agent_snapshot = if bot.agent_snapshot {
            let mut snap = observation.visible_state().clone();
            snap.decks[observation.actor].cards = vec![crate::models::Card::Unknown; observation.known_own_deck.len()];
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
                .map(|(i, a)| ActionMsg { i, text: a.action.to_string(), action: a.action.clone() })
                .collect(),
            actor: observation.actor,
            agent_snapshot,
            legal_actions: if full { Some(actions.to_vec()) } else { None },
            pdl_observation: if bot.pdl_observation { Some(observation.clone()) } else { None },
            pdl_search_seed: if bot.pdl_observation { Some(seed) } else { None },
            pdl_since_last: if bot.pdl_events { Some(since) } else { None },
        };
        let stdin = bot.stdin.as_mut().ok_or("no stdin")?;
        write_line(stdin, &msg).map_err(|e| format!("failed writing decide: {e}"))?;
        let reply = bot.rx.recv_timeout(timeout).map_err(|e| match e {
            std::sync::mpsc::RecvTimeoutError::Timeout => "bot timed out".to_string(),
            std::sync::mpsc::RecvTimeoutError::Disconnected => "bot process exited unexpectedly".to_string(),
        })?;
        let parsed: DecideReply = serde_json::from_str(&reply).map_err(|e| format!("invalid decide reply: {e}"))?;
        if parsed.i >= actions.len() {
            return Err(format!("i={} out of range for {} actions", parsed.i, actions.len()));
        }
        Ok(parsed.i)
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

    fn decision_fn(&mut self, _rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
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
        let start = Instant::now();
        let result = if self.failed {
            Err("bot failed earlier in this game".to_string())
        } else {
            self.ask(observation, actions, since, seed)
        };
        let secs = start.elapsed().as_secs_f64();
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
                "i": index, "secs": secs, "fallback": error.is_some(), "error": error, "bot_name": self.bot_name,
            });
            let _ = writeln!(log, "{line}");
        }
        actions[index].clone()
    }

    fn decide_omniscient(&mut self, _rng: &mut StdRng, _state: &State, _actions: &[Action]) -> Action {
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
                "child_pid": if pid == 0 { None } else { Some(pid) },
            });
            let _ = writeln!(log, "{line}");
        }
    }
}
