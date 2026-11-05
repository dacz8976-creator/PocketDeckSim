//! Information-Set Monte Carlo Tree Search (`im<sims>...`; sprint, Nov 2026). Single-observer ISMCTS after Cowling, Powley
//! and Whitehouse (2012), with km's evaluator at the leaves.
//!
//! What it may see: only its `PlayerObservation`. Every iteration samples one world consistent with that observation (the
//! same sampler as kx: its own deck order, the opponent's hand and deck from a list drawn from the pool, consistent with the
//! cards seen; `playout_player::PlayoutPlayer::sample_world`). It never reads the real state.
//!
//! One iteration:
//! 1. sample a world;
//! 2. walk the tree over the pilot's own actions this turn (and, with `_o`, the opponent's decisions up to the cut-off),
//!    keyed by the action sequence, so one node is an information set: the actions legal in this world are the available
//!    ones, chosen by UCB with availability counts (each available action counts one availability per visit);
//! 3. expand one untried available action and stop the walk;
//! 4. play on with a cheap policy on both sides (`_p`: km1 by default) until the cut-off (`_d`: the end of the pilot's turn
//!    plus that many more turns), then score with km's evaluator squashed to 0-1 (a win 1, a loss 0);
//! 5. back the score up the path.
//! The move played is the root action with the most visits (ties: the higher mean, then the order offered).
//!
//! Deterministic given the decision's seed: worlds, chance and play-out seeds all come from the engine's per-decision
//! search seed; iterations run in order on one thread.
//!
//! Not covered (km3's move, as kx does): a single distinct move; a setup choice made after the opponent's hidden setup;
//! a decision with a hidden stack frame of the opponent's.
use std::collections::BTreeSet;
use std::time::Instant;

use rand::{rngs::StdRng, Rng, RngCore, SeedableRng};

use super::playout_player::{PlayoutParams, PlayoutPlayer};
use super::{create_players, get_player, value_functions, Player, PlayerCode};
use crate::actions::{apply_action, Action};
use crate::observation::PlayerObservation;
use crate::state::GameOutcome;
use crate::{Deck, Game, State};

/// Pocket's deck size (the same setup rule as kx; it reads the constant, never the opponent's list).
const DECK_SIZE: usize = 20;

/// The play-out policy beyond the tree.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Rollout {
    /// km<N> on both sides.
    Km(usize),
    /// The weighted random player on both sides.
    Weighted,
    /// No play-out: score the leaf at once.
    Stop,
}

/// The pilot's parameters; every one is part of its code
/// (`im<sims>[_d<turns>][_p<k1|k2|w|stop>][_c<explore>][_s<scale>][_o][_trace]`).
#[derive(Debug, Clone, PartialEq)]
pub struct IsmctsParams {
    /// Iterations per decision.
    pub sims: usize,
    /// The cut-off: the play-out stops this many turns after the end of the pilot's current turn (0: at its end).
    pub cutoff_turns: u8,
    pub rollout: Rollout,
    /// The UCB exploration constant (on scores in 0-1).
    pub explore: f64,
    /// The squash: score = 0.5 + 0.5 tanh(value / scale), km's evaluator value from the pilot's side.
    pub scale: f64,
    /// The opponent's decisions up to the cut-off are tree nodes too (they pick by UCB on 1 - score).
    pub opponent_in_tree: bool,
    /// Write one `IM_TRACE` JSON line per decision to stderr.
    pub trace: bool,
    /// The km3 anchor (`_k<margin>`): km3's move is played unless another root action's mean score beats km3's move's by
    /// more than this margin (scores in 0-1). Off (`None`) by default: the most visited root action is played.
    pub anchor: Option<f64>,
    /// Full-turn expansion (`_f`): an iteration keeps expanding new nodes through the rest of the tree's part (the pilot's
    /// turn, and with `_o` up to the cut-off) instead of stopping at the first new node, so the whole turn's action
    /// sequence is in the tree and the play-out policy only plays what lies beyond it.
    pub full_turn: bool,
}

impl IsmctsParams {
    pub fn new(sims: usize) -> Self {
        IsmctsParams {
            sims,
            cutoff_turns: 1,
            rollout: Rollout::Km(1),
            explore: 0.4,
            scale: 5000.0,
            opponent_in_tree: false,
            trace: false,
            anchor: None,
            full_turn: false,
        }
    }

    /// Parses the code after the `im` prefix (lowercase), e.g. `200_d1_pk1_c0.4_s5000`.
    pub fn parse(rest: &str) -> Result<Self, String> {
        let invalid = |why: &str| {
            format!("Invalid player code: im{rest} ({why}). Use 'im<sims>[_d<turns>][_p<k1|k2|w|stop>][_c<explore>][_s<scale>][_o][_trace]', e.g. 'im200' or 'im400_d0_pw'")
        };
        let mut parts = rest.split('_');
        let sims = parts.next().unwrap_or("").parse::<usize>().map_err(|_| invalid("a number of iterations"))?;
        if sims == 0 {
            return Err(invalid("at least 1 iteration"));
        }
        let mut params = IsmctsParams::new(sims);
        for part in parts {
            match part {
                "o" => params.opponent_in_tree = true,
                "f" => params.full_turn = true,
                "trace" => params.trace = true,
                "pw" => params.rollout = Rollout::Weighted,
                "pstop" => params.rollout = Rollout::Stop,
                p if p.starts_with("pk") => {
                    let depth = p[2..].parse::<usize>().ok().filter(|d| *d >= 1).ok_or_else(|| invalid(part))?;
                    params.rollout = Rollout::Km(depth);
                }
                p if p.starts_with('k') => {
                    params.anchor = Some(p[1..].parse::<f64>().ok().filter(|m| m.is_finite() && *m >= 0.0).ok_or_else(|| invalid(part))?);
                }
                p if p.starts_with('d') => {
                    params.cutoff_turns = p[1..].parse::<u8>().map_err(|_| invalid(part))?;
                }
                p if p.starts_with('c') => {
                    params.explore = p[1..].parse::<f64>().ok().filter(|c| c.is_finite() && *c >= 0.0).ok_or_else(|| invalid(part))?;
                }
                p if p.starts_with('s') => {
                    params.scale = p[1..].parse::<f64>().ok().filter(|s| s.is_finite() && *s > 0.0).ok_or_else(|| invalid(part))?;
                }
                _ => return Err(invalid(&format!("unknown part '{part}'"))),
            }
        }
        Ok(params)
    }

    /// The canonical code, every parameter spelled out.
    pub fn code(&self) -> String {
        let policy = match self.rollout {
            Rollout::Km(d) => format!("k{d}"),
            Rollout::Weighted => "w".to_string(),
            Rollout::Stop => "stop".to_string(),
        };
        format!(
            "im{}_d{}_p{}_c{}_s{}{}{}{}{}",
            self.sims,
            self.cutoff_turns,
            policy,
            self.explore,
            self.scale,
            self.anchor.map(|m| format!("_k{m}")).unwrap_or_default(),
            if self.full_turn { "_f" } else { "" },
            if self.opponent_in_tree { "_o" } else { "" },
            if self.trace { "_trace" } else { "" }
        )
    }
}

/// One action out of a node: its statistics over the iterations that walked through it.
#[derive(Debug, Clone)]
struct Edge {
    key: String,
    child: Option<usize>,
    visits: u32,
    /// Sum of the scores backed up through it, from the pilot's side.
    total: f64,
    /// How many visits of the node had this action available.
    avail: u32,
}

#[derive(Debug, Clone, Default)]
struct Node {
    edges: Vec<Edge>,
}

fn splitmix(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9e37_79b9_7f4a_7c15);
    x = (x ^ (x >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    x ^ (x >> 31)
}

fn key(action: &Action) -> String {
    format!("{}|{:?}", action.actor, action.action)
}

/// One decision's result, for the trace and the tests.
#[derive(Debug, Clone)]
pub struct IsmctsReport {
    pub turn: u8,
    pub actor: usize,
    /// (action label, visits, mean score) for every root action that was available at least once.
    pub root: Vec<(String, u32, f64)>,
    pub chosen: String,
    pub reason: String,
    pub iterations: usize,
    pub failed: usize,
    pub nodes: usize,
    pub millis: f64,
}

pub struct IsmctsPlayer {
    params: IsmctsParams,
    deck: Deck,
    /// km3: the move for the decisions not covered.
    km: Box<dyn Player>,
    /// The world sampler (kx's, REALISTIC knowledge, the same pool).
    sampler: PlayoutPlayer,
    printed: bool,
    pub decisions: usize,
    pub millis: f64,
}

impl std::fmt::Debug for IsmctsPlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "IsmctsPlayer({})", self.params.code())
    }
}

impl IsmctsPlayer {
    pub fn new(deck: Deck, opponent_list: Deck, params: IsmctsParams) -> Self {
        let sampler = PlayoutPlayer::with_extra_lists(deck.clone(), opponent_list.clone(), PlayoutParams::new(1), Vec::new());
        let km = get_player(deck.clone(), &opponent_list, &PlayerCode::KM { max_depth: 3 });
        IsmctsPlayer { params, deck, km, sampler, printed: false, decisions: 0, millis: 0.0 }
    }

    pub fn params(&self) -> &IsmctsParams {
        &self.params
    }

    fn squash(&self, state: &State, me: usize) -> f64 {
        match state.winner {
            Some(GameOutcome::Win(w)) if w == me => 1.0,
            Some(GameOutcome::Win(_)) => 0.0,
            Some(_) => 0.5,
            None => {
                let v = value_functions::public_clock_effect_km_value_function(state, me);
                0.5 + 0.5 * (v / self.params.scale).tanh()
            }
        }
    }

    /// Plays on from `state` with the play-out policy until the cut-off turn or the end, and scores the result.
    fn rollout(&self, state: State, list: &Deck, me: usize, stop_turn: u8, seed: u64) -> f64 {
        if state.winner.is_some() || state.turn_count >= stop_turn {
            return self.squash(&state, me);
        }
        let code = match self.params.rollout {
            Rollout::Km(depth) => PlayerCode::KM { max_depth: depth },
            Rollout::Weighted => PlayerCode::W,
            Rollout::Stop => return self.squash(&state, me),
        };
        let (d0, d1) = if me == 0 { (self.deck.clone(), list.clone()) } else { (list.clone(), self.deck.clone()) };
        let mut game = Game::from_state(state, create_players(d0, d1, vec![code.clone(), code]), seed);
        let mut ticks = 0;
        while !game.is_game_over() && game.state().turn_count < stop_turn && ticks < 2000 {
            game.play_tick();
            ticks += 1;
        }
        self.squash(game.state(), me)
    }

    /// The decision: `sims` iterations over sampled worlds. `rng` is the decision's own randomness.
    pub fn evaluate(&mut self, rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> (Action, IsmctsReport) {
        let start = Instant::now();
        let me = observation.actor;
        let visible = observation.visible_state();
        let mut report = IsmctsReport {
            turn: visible.turn_count,
            actor: me,
            root: vec![],
            chosen: String::new(),
            reason: String::new(),
            iterations: 0,
            failed: 0,
            nodes: 0,
            millis: 0.0,
        };
        let mut root_keys: Vec<String> = Vec::new();
        let mut by_key: Vec<Action> = Vec::new();
        let mut seen = BTreeSet::new();
        for a in actions {
            if seen.insert(key(a)) {
                root_keys.push(key(a));
                by_key.push(a.clone());
            }
        }
        let opponent = 1 - me;
        let opponent_has_set_up = visible.hands[opponent].len() + visible.decks[opponent].cards.len() < DECK_SIZE;
        let skip = if root_keys.len() < 2 {
            Some("one distinct move")
        } else if visible.turn_count == 0 && opponent_has_set_up {
            Some("a setup choice after the opponent's hidden setup: km3's move")
        } else if visible.move_generation_stack.iter().any(|(_, choices)| choices.is_empty()) {
            Some("a hidden stack frame of the opponent's: km3's move")
        } else {
            None
        };
        if let Some(why) = skip {
            let action = if root_keys.len() < 2 { actions[0].clone() } else { self.km.decision_fn(&mut rng.clone(), observation, actions) };
            report.reason = why.to_string();
            report.chosen = key(&action);
            report.millis = start.elapsed().as_secs_f64() * 1000.0;
            return (action, report);
        }

        let base = rng.clone().next_u64() ^ 0x4953_4d43_5453_5f31;
        let start_turn = visible.turn_count;
        let stop_turn = start_turn.saturating_add(1).saturating_add(self.params.cutoff_turns);
        let mut nodes: Vec<Node> = vec![Node::default()];
        for i in 0..self.params.sims {
            let mut world_rng = StdRng::seed_from_u64(splitmix(base.wrapping_add(i as u64)));
            let mut chance = StdRng::seed_from_u64(splitmix(base ^ 0x6368_616e_6365_0000 ^ i as u64));
            let rollout_seed = splitmix(base ^ 0x726f_6c6c_0000_0000 ^ i as u64);
            let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                let (mut state, list) = self.sampler.sample_world(observation, &mut world_rng);
                let mut path: Vec<(usize, usize)> = Vec::new();
                let mut node = 0usize;
                let mut expanded = false;
                loop {
                    if state.winner.is_some() || expanded {
                        break;
                    }
                    let (actor, mut legal) = state.generate_possible_actions();
                    crate::observation::canonical_actions(&mut legal);
                    // The pilot's own decisions this turn; with `_o`, every decision up to the cut-off.
                    let in_tree = state.turn_count < stop_turn
                        && ((actor == me && state.turn_count == start_turn) || self.params.opponent_in_tree);
                    if !in_tree {
                        break;
                    }
                    if legal.len() == 1 {
                        apply_action(&mut chance, &mut state, &legal[0]);
                        continue;
                    }
                    // The actions available in this world, once each; at the root only the real legal ones.
                    let mut available: Vec<(String, Action)> = Vec::new();
                    let mut keys = BTreeSet::new();
                    for a in legal {
                        let k = key(&a);
                        if (node != 0 || root_keys.contains(&k)) && keys.insert(k.clone()) {
                            available.push((k, a));
                        }
                    }
                    if available.is_empty() {
                        break;
                    }
                    let mut slots = Vec::with_capacity(available.len());
                    for (k, _) in &available {
                        let edges = &mut nodes[node].edges;
                        let e = match edges.iter().position(|e| e.key == *k) {
                            Some(e) => e,
                            None => {
                                edges.push(Edge { key: k.clone(), child: None, visits: 0, total: 0.0, avail: 0 });
                                edges.len() - 1
                            }
                        };
                        edges[e].avail += 1;
                        slots.push(e);
                    }
                    let untried: Vec<usize> = (0..slots.len()).filter(|&j| nodes[node].edges[slots[j]].visits == 0).collect();
                    let pick = if !untried.is_empty() {
                        expanded = !self.params.full_turn;
                        untried[chance.gen_range(0..untried.len())]
                    } else {
                        let mine = actor == me;
                        let edges = &nodes[node].edges;
                        let score = |j: usize| {
                            let e = &edges[slots[j]];
                            let mean = e.total / e.visits as f64;
                            let exploit = if mine { mean } else { 1.0 - mean };
                            exploit + self.params.explore * ((e.avail as f64).ln() / e.visits as f64).sqrt()
                        };
                        (0..slots.len()).fold(0, |b, j| if score(j) > score(b) { j } else { b })
                    };
                    let e = slots[pick];
                    apply_action(&mut chance, &mut state, &available[pick].1);
                    path.push((node, e));
                    node = match nodes[node].edges[e].child {
                        Some(c) => c,
                        None => {
                            nodes.push(Node::default());
                            let c = nodes.len() - 1;
                            nodes[node].edges[e].child = Some(c);
                            c
                        }
                    };
                }
                let q = self.rollout(state, &list, me, stop_turn, rollout_seed);
                (path, q)
            }));
            match result {
                Ok((path, q)) => {
                    for (n, e) in path {
                        nodes[n].edges[e].visits += 1;
                        nodes[n].edges[e].total += q;
                    }
                    report.iterations += 1;
                }
                Err(_) => report.failed += 1,
            }
        }
        report.nodes = nodes.len();
        // The most visited root action among the real legal ones (ties: higher mean, then the order offered).
        let mut best: Option<(u32, f64, usize)> = None;
        for (i, k) in root_keys.iter().enumerate() {
            if let Some(e) = nodes[0].edges.iter().find(|e| e.key == *k) {
                let mean = if e.visits > 0 { e.total / e.visits as f64 } else { f64::NAN };
                report.root.push((k.chars().take(140).collect(), e.visits, mean));
                let better = match best {
                    None => e.visits > 0,
                    Some((v, m, _)) => e.visits > v || (e.visits == v && mean > m),
                };
                if better {
                    best = Some((e.visits, mean, i));
                }
            }
        }
        // The km3 anchor: km3's move unless another root action's mean beats it by more than the margin.
        if let (Some(margin), Some((_, _, _))) = (self.params.anchor, best) {
            let km_move = self.km.decision_fn(&mut rng.clone(), observation, actions);
            let km_key = key(&km_move);
            let mean_of = |k: &str| nodes[0].edges.iter().find(|e| e.key == k && e.visits > 0).map(|e| e.total / e.visits as f64);
            let km_mean = mean_of(&km_key);
            let mut lead: Option<(f64, usize)> = None;
            for (i, k) in root_keys.iter().enumerate() {
                if let Some(m) = mean_of(k) {
                    if lead.is_none_or(|(b, _)| m > b) {
                        lead = Some((m, i));
                    }
                }
            }
            let action = match (km_mean, lead) {
                (Some(km), Some((m, i))) if m > km + margin => {
                    report.reason = format!("anchor: {:+.3} over km3's move (margin {margin})", m - km);
                    by_key[i].clone()
                }
                _ => {
                    report.reason = format!("anchor: km3's move kept (margin {margin})");
                    km_move
                }
            };
            report.chosen = key(&action);
            report.millis = start.elapsed().as_secs_f64() * 1000.0;
            return (action, report);
        }
        let action = match best {
            Some((_, _, i)) => {
                report.reason = format!("most visited of {} root actions", report.root.len());
                by_key[i].clone()
            }
            None => {
                report.reason = "no iteration completed: km3's move".to_string();
                self.km.decision_fn(&mut rng.clone(), observation, actions)
            }
        };
        report.chosen = key(&action);
        report.millis = start.elapsed().as_secs_f64() * 1000.0;
        (action, report)
    }
}

impl Player for IsmctsPlayer {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, possible_actions: &[Action]) -> Action {
        if !self.printed {
            self.printed = true;
            eprintln!("IM_PARAMS {}", serde_json::json!({"code": self.params.code(), "seat": observation.actor}));
        }
        let (action, report) = self.evaluate(rng, observation, possible_actions);
        self.decisions += 1;
        self.millis += report.millis;
        if self.params.trace {
            eprintln!(
                "IM_TRACE {}",
                serde_json::json!({
                    "code": self.params.code(), "turn": report.turn, "seat": report.actor,
                    "iterations": report.iterations, "failed": report.failed, "nodes": report.nodes,
                    "ms": (report.millis * 10.0).round() / 10.0, "chosen": report.chosen, "reason": report.reason,
                    "root": report.root.iter().map(|(k, v, m)| serde_json::json!({"move": k, "visits": v,
                        "mean": if m.is_finite() { serde_json::json!((m * 1000.0).round() / 1000.0) } else { serde_json::Value::Null }})).collect::<Vec<_>>(),
                })
            );
        }
        action
    }

    /// The diagnostic entry with a full state (`Game` never calls it in play): km3's move, no search, since a search
    /// from a full state would see the hidden cards.
    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        self.km.decide_omniscient(rng, state, possible_actions)
    }

    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::observation::RevealedKnowledge;

    #[test]
    fn the_code_parses_and_round_trips() {
        let f = IsmctsParams::parse("100_f_k0.1").unwrap();
        assert!(f.full_turn && f.anchor == Some(0.1));
        assert_eq!(IsmctsParams::parse(&f.code()[2..]).unwrap(), f);
        let k = IsmctsParams::parse("100_k0.05").unwrap();
        assert_eq!(k.anchor, Some(0.05));
        assert_eq!(IsmctsParams::parse(&k.code()[2..]).unwrap(), k);
        let p = IsmctsParams::parse("200_d0_pw_c0.7_s3000_o_trace").unwrap();
        assert_eq!((p.sims, p.cutoff_turns, p.rollout, p.explore, p.scale, p.opponent_in_tree, p.trace), (200, 0, Rollout::Weighted, 0.7, 3000.0, true, true));
        assert_eq!(IsmctsParams::parse(&p.code()[2..]).unwrap(), p);
        assert_eq!(IsmctsParams::parse("50").unwrap().code(), "im50_d1_pk1_c0.4_s5000");
        assert!(IsmctsParams::parse("0").is_err());
        assert!(IsmctsParams::parse("50_x").is_err());
        assert_eq!(IsmctsParams::parse("50_pk2").unwrap().rollout, Rollout::Km(2));
    }

    /// The information boundary: two games that differ only in what the pilot can't see (the opponent's hand, both
    /// deck orders) give the same observation, and with the same seed the same decision.
    #[test]
    fn two_hidden_worlds_with_the_same_observation_and_seed_give_the_same_decision() {
        let (deck_a, deck_b) = crate::test_support::load_test_decks();
        let mut game = Game::new(create_players(deck_a.clone(), deck_b.clone(), vec![PlayerCode::KM { max_depth: 1 }, PlayerCode::KM { max_depth: 1 }]), 20_000_000_123);
        // Play into the game until the pilot's side has a real choice in the main part of a turn.
        let mut ticks = 0;
        loop {
            let state = game.get_state_clone();
            let (actor, actions) = state.generate_possible_actions();
            let distinct: BTreeSet<String> = actions.iter().map(key).collect();
            if actor == 0 && state.turn_count >= 3 && distinct.len() >= 3 {
                break;
            }
            game.play_tick();
            ticks += 1;
            assert!(ticks < 500 && !game.is_game_over(), "no decision found");
        }
        let real = game.get_state_clone();
        // A second world: the opponent's hand and deck shuffled together and re-dealt, and the pilot's deck reordered.
        let mut other = real.clone();
        let mut hidden: Vec<_> = other.hands[1].drain(..).chain(other.decks[1].cards.drain(..)).collect();
        hidden.reverse();
        let hand_size = real.hands[1].len();
        other.hands[1] = hidden.drain(..hand_size).collect();
        other.decks[1].cards = hidden;
        other.decks[0].cards.reverse();
        assert!(other.hands[1] != real.hands[1] || other.decks[1].cards != real.decks[1].cards || other.decks[0].cards != real.decks[0].cards,
            "the two worlds must differ in hidden cards");
        let revealed = RevealedKnowledge { deck_top: [Vec::new(), Vec::new()], opponent_hand: Vec::new(), opponent_deck_membership: Vec::new() };
        let obs_real = PlayerObservation::from_state(&real, 0, &revealed);
        let obs_other = PlayerObservation::from_state(&other, 0, &revealed);
        assert_eq!(format!("{:?}", obs_real.visible_state()), format!("{:?}", obs_other.visible_state()), "the same observation");
        let (_, actions) = real.generate_possible_actions();
        let mut pilot = IsmctsPlayer::new(deck_a.clone(), deck_b.clone(), IsmctsParams::parse("40_d0").unwrap());
        let (a1, r1) = pilot.evaluate(&mut StdRng::seed_from_u64(7), &obs_real, &actions);
        let (a2, r2) = pilot.evaluate(&mut StdRng::seed_from_u64(7), &obs_other, &actions);
        assert_eq!(a1, a2);
        assert_eq!(format!("{:?}", r1.root), format!("{:?}", r2.root), "the same search, visit for visit");
        assert!(r1.iterations > 0, "{r1:?}");
    }
}
