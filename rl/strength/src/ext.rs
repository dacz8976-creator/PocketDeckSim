//! An external pilot: a child process asked for each decision over JSON lines (see PROTOCOL.md). It sees only what a pilot is allowed to see,
//! the engine's `PlayerObservation` (own hand and deck as a multiset, the public board, the opponent's hidden cards as counts) and the legal
//! actions; it answers with the index of the action it chooses. It may be as slow as it likes; the harness only reports how slow.
use deckgym::actions::Action;
use deckgym::observation::PlayerObservation;
use deckgym::players::Player;
use deckgym::Deck;
use rand::rngs::StdRng;
use serde_json::{json, Value};
use std::fmt;
use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::mpsc::{channel, Receiver};
use std::sync::{Arc, Mutex};
use std::time::Duration;

/// What the pilot reports besides its choices; summed over the game and written to the game record.
#[derive(Default, Clone)]
pub struct ExtMeta {
    pub notes: Vec<String>,
    pub cost_usd: f64,
    pub tokens: u64,
}
pub type Meta = Arc<Mutex<ExtMeta>>;

pub fn new_meta() -> Meta {
    Arc::new(Mutex::new(ExtMeta::default()))
}

pub struct ExtPlayer {
    deck: Deck,
    child: Child,
    stdin: ChildStdin,
    rx: Receiver<String>,
    seat: usize,
    timeout: Option<Duration>,
    meta: Meta,
    cmd: String,
}

impl fmt::Debug for ExtPlayer {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "ExtPlayer({})", self.cmd)
    }
}

impl ExtPlayer {
    pub fn spawn(cmd: &str, deck: Deck, seat: usize, seed: u64, timeout_s: Option<f64>, meta: Meta) -> Self {
        let mut child = Command::new("sh")
            .arg("-c")
            .arg(cmd)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .unwrap_or_else(|e| panic!("cannot start pilot `{cmd}`: {e}"));
        let stdin = child.stdin.take().unwrap();
        let stdout = child.stdout.take().unwrap();
        let (tx, rx) = channel::<String>();
        std::thread::spawn(move || {
            for line in BufReader::new(stdout).lines() {
                match line {
                    Ok(l) => {
                        if tx.send(l).is_err() {
                            break;
                        }
                    }
                    Err(_) => break,
                }
            }
        });
        let mut p = ExtPlayer { deck, child, stdin, rx, seat, timeout: timeout_s.map(Duration::from_secs_f64), meta, cmd: cmd.to_string() };
        let deck_json: Vec<Value> = p.deck.cards.iter().map(|c| json!({"id": c.get_id(), "name": c.get_name()})).collect();
        p.send(&json!({"type": "hello", "protocol": 1, "seat": seat, "seed": seed, "deck": deck_json}));
        p
    }

    fn send(&mut self, v: &Value) {
        let mut s = serde_json::to_string(v).unwrap();
        s.push('\n');
        if self.stdin.write_all(s.as_bytes()).and_then(|_| self.stdin.flush()).is_err() {
            panic!("pilot `{}` closed its input", self.cmd);
        }
    }

    /// One JSON reply line; lines that are not JSON objects are ignored (a pilot may print logs on stdout by mistake).
    fn read_reply(&mut self) -> Value {
        loop {
            let line = match self.timeout {
                Some(t) => self.rx.recv_timeout(t).unwrap_or_else(|_| panic!("pilot `{}` gave no answer within {:?}", self.cmd, t)),
                None => self.rx.recv().unwrap_or_else(|_| panic!("pilot `{}` ended without answering", self.cmd)),
            };
            if line.trim_start().starts_with('{') {
                if let Ok(v) = serde_json::from_str::<Value>(&line) {
                    return v;
                }
            }
        }
    }
}

impl Drop for ExtPlayer {
    fn drop(&mut self) {
        let _ = writeln!(self.stdin, "{}", json!({"type": "end"}));
        let _ = self.stdin.flush();
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

impl Player for ExtPlayer {
    fn decision_fn(&mut self, _rng: &mut StdRng, observation: &PlayerObservation, possible_actions: &[Action]) -> Action {
        let acts: Vec<Value> = possible_actions
            .iter()
            .enumerate()
            .map(|(i, a)| json!({"i": i, "label": crate::label(a, Some(observation)), "action": serde_json::to_value(a).unwrap()}))
            .collect();
        let turn = observation.visible_state().turn_count;
        let msg = json!({"type": "decide", "seat": self.seat, "turn": turn, "observation": serde_json::to_value(observation).unwrap(), "actions": acts});
        self.send(&msg);
        let reply = self.read_reply();
        {
            let mut m = self.meta.lock().unwrap();
            if let Some(n) = reply.get("note").and_then(|x| x.as_str()) {
                if m.notes.len() < 400 {
                    m.notes.push(format!("t{turn}: {n}"));
                }
            }
            m.cost_usd += reply.get("cost_usd").and_then(|x| x.as_f64()).unwrap_or(0.0);
            m.tokens += reply.get("tokens").and_then(|x| x.as_u64()).unwrap_or(0);
        }
        let idx = if let Some(c) = reply.get("choice").and_then(|c| c.as_u64()) {
            c as usize
        } else if let Some(l) = reply.get("label").and_then(|l| l.as_str()) {
            acts.iter().position(|a| a["label"] == l).unwrap_or_else(|| panic!("pilot answered with an unknown label {l:?}"))
        } else {
            panic!("pilot reply has neither `choice` nor `label`: {reply}")
        };
        assert!(idx < possible_actions.len(), "pilot chose action {idx} of {}", possible_actions.len());
        possible_actions[idx].clone()
    }

    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }

    fn decide_omniscient(&mut self, _rng: &mut StdRng, _state: &deckgym::State, _possible_actions: &[Action]) -> Action {
        panic!("an external pilot decides from observations only")
    }
}
