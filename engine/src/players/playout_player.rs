//! The play-out chooser (`kx<N>`; branch claude/playout-pilot, Oct 2; rl/results/planning_pilot_design_2026-10-02/DESIGN.md
//! sections 5 and 9). At each of its decisions with two or more distinct moves, the pilot plays every distinct legal move
//! (up to a cap) out to the end of the game `rollouts` times, with km<N> on both sides, and keeps the move whose play-outs
//! score best; when that move's lead over km<N>'s own move is within the noise, it keeps km<N>'s move.
//!
//! What it may see: only its `PlayerObservation` (its hand and board, the public board, discards, points, counts; its own
//! deck as an unordered multiset). Every play-out starts from a state sampled from that: its own deck order, the
//! opponent's hand and deck and every coin are drawn afresh per play-out. The opponent's hidden cards come from a list:
//! - LAB (a laboratory condition, labelled in every output): the opponent's exact 20-card list, only when that list is
//!   one of the meta lists of the pool below; the meta side is never handed a brew's exact list, so LAB falls back to
//!   REALISTIC then, and says so;
//! - REALISTIC: per play-out, a list drawn from the candidate pool (`playout_pool.rs`: decks/screen/opponents and
//!   decks/research) among those consistent with the opponent's cards seen so far (by name), the unseen cards from it.
//!
//! Common random numbers: play-out j of every candidate starts from the same sampled state and uses the same game seed (so
//! the same coin stream and the same km<N> decision seeds, as far as the games run alike); the noise rule reads the paired
//! difference from km<N>'s move, mean / standard error > z.
//!
//! Deterministic given seeds: the sampling and the play-out seeds come from the decision's own randomness (the engine's
//! per-decision search seed); play-outs run in parallel but are collected in order. A time budget (`_t<seconds>`, off by
//! default) stops after the rounds finished in time, which makes the result depend on the machine's speed.
//!
//! Not covered: a setup choice made after the opponent's hidden setup (the opponent's placed cards can't be sampled yet)
//! and a decision with a hidden stack frame of the opponent's both keep km<N>'s move, and say so in the trace.
use std::collections::{BTreeMap, BTreeSet};
use std::time::Instant;

use rand::seq::SliceRandom;
use rand::{rngs::StdRng, Rng, RngCore, SeedableRng};
use rayon::prelude::*;

use super::{create_players, get_player, value_functions, Player, PlayerCode};
use crate::actions::Action;
use crate::models::Card;
use crate::observation::PlayerObservation;
use crate::state::GameOutcome;
use crate::{Deck, Game, State};

/// What the pilot knows of the opponent's list.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Knowledge {
    /// The opponent's exact list (a meta list only): a laboratory condition.
    Lab,
    /// A list sampled per play-out from the candidate pool, consistent with the cards seen.
    Realistic,
}

/// The pilot's parameters; every one is part of its code (`kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<s>][_trace]`).
#[derive(Debug, Clone, PartialEq)]
pub struct PlayoutParams {
    /// The search depth of km<depth>: the move it proposes and the bot of both sides in every play-out.
    pub depth: usize,
    /// Play-outs per candidate (R).
    pub rollouts: usize,
    /// At most this many candidates (km<depth>'s move always among them).
    pub cap: usize,
    /// The noise threshold: a move replaces km<depth>'s only if its mean paired difference exceeds z standard errors.
    pub z: f64,
    pub knowledge: Knowledge,
    /// The time budget per decision in milliseconds (0: none). Play-outs stop after the rounds finished in time (at least 2).
    pub budget_ms: u64,
    /// Write one `KX_TRACE` JSON line per decision to stderr.
    pub trace: bool,
}

impl PlayoutParams {
    pub fn new(depth: usize) -> Self {
        PlayoutParams { depth, rollouts: 16, cap: 12, z: 2.0, knowledge: Knowledge::Realistic, budget_ms: 0, trace: false }
    }

    /// Parses the code after the `kx` prefix (lowercase), e.g. `3_r8_c5_z1.5_lab_t30_trace`.
    pub fn parse(rest: &str) -> Result<Self, String> {
        let invalid = |why: &str| {
            format!("Invalid player code: kx{rest} ({why}). Use 'kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<seconds>][_trace]', e.g. 'kx3' or 'kx3_r24_c12_z2_lab'")
        };
        let mut parts = rest.split('_');
        let depth = parts.next().unwrap_or("").parse::<usize>().map_err(|_| invalid("a depth"))?;
        if depth == 0 {
            return Err(invalid("a depth of at least 1"));
        }
        let mut params = PlayoutParams::new(depth);
        for part in parts {
            let number = |p: &str| p.parse::<u64>().map_err(|_| invalid(part));
            match part {
                "lab" => params.knowledge = Knowledge::Lab,
                "real" => params.knowledge = Knowledge::Realistic,
                "trace" => params.trace = true,
                p if p.starts_with('r') => {
                    params.rollouts = number(&p[1..])? as usize;
                    if params.rollouts == 0 {
                        return Err(invalid("at least 1 play-out"));
                    }
                }
                p if p.starts_with('c') => {
                    params.cap = number(&p[1..])? as usize;
                    if params.cap < 2 {
                        return Err(invalid("a cap of at least 2"));
                    }
                }
                p if p.starts_with('z') => {
                    params.z = p[1..].parse::<f64>().ok().filter(|z| z.is_finite() && *z >= 0.0).ok_or_else(|| invalid(part))?;
                }
                p if p.starts_with('t') => params.budget_ms = number(&p[1..])? * 1000,
                _ => return Err(invalid(&format!("unknown part '{part}'"))),
            }
        }
        Ok(params)
    }

    /// The canonical code, every parameter spelled out.
    pub fn code(&self) -> String {
        format!(
            "kx{}_r{}_c{}_z{}_{}_t{}{}",
            self.depth,
            self.rollouts,
            self.cap,
            self.z,
            if self.knowledge == Knowledge::Lab { "lab" } else { "real" },
            self.budget_ms / 1000,
            if self.trace { "_trace" } else { "" }
        )
    }
}

/// One candidate's play-out result.
#[derive(Debug, Clone)]
pub struct CandidateReport {
    pub action: Action,
    pub label: String,
    /// Mean play-out score for the pilot (win 1, tie ½, loss 0).
    pub score: f64,
    /// Mean paired difference from km<N>'s move (0 for km<N>'s move itself).
    pub diff: f64,
    /// The standard error of that difference (sample sd / √n; infinite with fewer than 2 rounds).
    pub se: f64,
}

/// A move left out by the candidate cap, and why.
#[derive(Debug, Clone)]
pub struct Dropped {
    pub label: String,
    pub reason: String,
}

/// One decision: every candidate's play-outs, the drops, km<N>'s move, the choice and why.
#[derive(Debug, Clone)]
pub struct DecisionReport {
    pub knowledge: String,
    pub turn: u8,
    pub actor: usize,
    pub candidates: Vec<CandidateReport>,
    pub dropped: Vec<Dropped>,
    /// The index of km<N>'s move in `candidates`.
    pub km3: usize,
    /// The index of the move played in `candidates`.
    pub chosen: usize,
    pub reason: String,
    /// Play-out rounds run (each candidate played once per round).
    pub rounds: usize,
    /// Rounds dropped because a play-out in them failed (an engine panic); the rest stay paired.
    pub failed_rounds: usize,
    pub millis: f64,
}

pub struct PlayoutPlayer {
    params: PlayoutParams,
    km: Box<dyn Player>,
    core: Core,
    printed: bool,
    /// Decisions asked of the pilot, and the milliseconds they took (for the per-game report).
    pub decisions: usize,
    pub millis: f64,
}

impl std::fmt::Debug for PlayoutPlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PlayoutPlayer({})", self.params.code())
    }
}

/// A list as a multiset of card ids (the order of a list doesn't matter).
fn id_multiset(deck: &Deck) -> Vec<String> {
    let mut ids: Vec<String> = deck.cards.iter().map(|c| c.get_id()).collect();
    ids.sort();
    ids
}

fn splitmix(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9e37_79b9_7f4a_7c15);
    x = (x ^ (x >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    x ^ (x >> 31)
}

/// What the play-outs need, shared by the parallel rounds.
struct Core {
    deck: Deck,
    opponent_list: Deck,
    pool: Vec<(String, Deck)>,
    /// LAB is in force: requested, and the opponent's list is one of the pool's (a meta list).
    lab: bool,
    depth: usize,
}

impl PlayoutPlayer {
    pub fn new(deck: Deck, opponent_list: Deck, params: PlayoutParams) -> Self {
        let km = get_player(deck.clone(), &opponent_list, &PlayerCode::KM { max_depth: params.depth });
        let pool: Vec<(String, Deck)> = super::playout_pool::POOL
            .iter()
            .map(|(name, path, _, text)| {
                (name.to_string(), Deck::from_string(text).unwrap_or_else(|e| panic!("the pool's {path}: {e}")))
            })
            .collect();
        let target = id_multiset(&opponent_list);
        let lab = params.knowledge == Knowledge::Lab && pool.iter().any(|(_, d)| id_multiset(d) == target);
        let core = Core { deck, opponent_list, pool, lab, depth: params.depth };
        PlayoutPlayer { params, km, core, printed: false, decisions: 0, millis: 0.0 }
    }

    pub fn params(&self) -> &PlayoutParams {
        &self.params
    }

    /// The knowledge mode in force, as every output labels it.
    pub fn knowledge_label(&self) -> String {
        match (self.params.knowledge, self.core.lab) {
            (Knowledge::Lab, true) => "LAB (laboratory condition: the opponent's exact 20-card list is known)".into(),
            (Knowledge::Lab, false) => format!(
                "REALISTIC (LAB asked, but the opponent's list is not one of the {} meta lists, so it is never handed over)",
                self.core.pool.len()
            ),
            _ => format!("REALISTIC (the opponent's list is drawn per play-out from the {} meta lists consistent with the cards seen)", self.core.pool.len()),
        }
    }

}

impl Core {
    /// The opponent's cards seen so far, by name: in play (with the cards under an evolution and Tools), discarded, their
    /// Stadium, and any revealed from their hand or known to be in their deck.
    fn seen_opponent_cards(observation: &PlayerObservation) -> Vec<Card> {
        let state = observation.visible_state();
        let opponent = 1 - observation.actor;
        let mut seen: Vec<Card> = Vec::new();
        for pokemon in state.in_play_pokemon[opponent].iter().flatten() {
            seen.push(pokemon.card.clone());
            seen.extend(pokemon.cards_behind.iter().cloned());
            seen.extend(pokemon.attached_tools.iter().cloned());
        }
        seen.extend(state.discard_piles[opponent].iter().cloned());
        if state.active_stadium_owner == Some(opponent) {
            seen.extend(state.active_stadium.iter().cloned());
        }
        seen.extend(observation.revealed.opponent_hand.iter().cloned());
        seen.extend(observation.revealed.opponent_deck_membership.iter().cloned());
        seen.retain(|c| !c.is_unknown());
        seen
    }

    /// REALISTIC: a pool list consistent with the seen cards (every name seen no more often than the list holds it),
    /// uniformly; with none consistent, the closest. The list's printings of the seen cards are replaced by the seen ones,
    /// so the sampler removes them from it.
    fn sample_list(&self, seen: &[Card], rng: &mut StdRng) -> (Deck, String) {
        let mut seen_names: BTreeMap<String, usize> = BTreeMap::new();
        for c in seen {
            *seen_names.entry(c.get_name()).or_default() += 1;
        }
        let excess = |deck: &Deck| -> usize {
            seen_names
                .iter()
                .map(|(name, n)| n.saturating_sub(deck.cards.iter().filter(|c| c.get_name() == *name).count()))
                .sum()
        };
        let consistent: Vec<usize> = (0..self.pool.len()).filter(|&i| excess(&self.pool[i].1) == 0).collect();
        let (index, label) = if consistent.is_empty() {
            let i = (0..self.pool.len()).min_by_key(|&i| excess(&self.pool[i].1)).unwrap();
            (i, format!("{} (closest; no list consistent)", self.pool[i].0))
        } else {
            let i = consistent[rng.gen_range(0..consistent.len())];
            (i, format!("{} (1 of {} consistent)", self.pool[i].0, consistent.len()))
        };
        let mut deck = self.pool[index].1.clone();
        for card in seen {
            if deck.cards.iter().any(|c| c == card) {
                continue;
            }
            if let Some(i) = deck.cards.iter().position(|c| c.get_name() == card.get_name() && !seen.contains(c)) {
                deck.cards[i] = card.clone();
            }
        }
        (deck, label)
    }

    /// One sampled world: a full state consistent with the observation, the list its opponent's hidden cards came from,
    /// and that list's name.
    fn sample_state(&self, observation: &PlayerObservation, rng: &mut StdRng) -> (State, Deck, String) {
        let (list, name) = if self.lab {
            (self.opponent_list.clone(), "the exact list (LAB)".to_string())
        } else {
            self.sample_list(&Self::seen_opponent_cards(observation), rng)
        };
        let mut state = observation.search_state_with_opponent_list(rng, &list);
        let opponent = 1 - observation.actor;
        // Slots the list couldn't fill (a printing it doesn't hold) take random cards of the list, so no Unknown is played.
        let mut slots: Vec<&mut Card> = state.hands[opponent].iter_mut().chain(state.decks[opponent].cards.iter_mut()).collect();
        for slot in slots.iter_mut().filter(|c| c.is_unknown()) {
            **slot = list.cards.choose(rng).cloned().unwrap_or(Card::Unknown);
        }
        // An opponent still to set up holds at least one Basic, as the engine's deal guarantees (a zero-Basic hand is
        // repaired): swap one in from the sampled deck if the sampled hand has none.
        if state.turn_count == 0
            && state.in_play_pokemon[opponent].iter().all(|p| p.is_none())
            && !state.hands[opponent].iter().any(|c| c.is_basic())
        {
            let basics: Vec<usize> = (0..state.decks[opponent].cards.len()).filter(|&i| state.decks[opponent].cards[i].is_basic()).collect();
            if let (Some(&d), false) = (basics.choose(rng), state.hands[opponent].is_empty()) {
                let h = rng.gen_range(0..state.hands[opponent].len());
                std::mem::swap(&mut state.hands[opponent][h], &mut state.decks[opponent].cards[d]);
            }
        }
        state.setup_opponent_hidden = false;
        (state, list, name)
    }

    /// Plays `action` from `state` to the end with km<N> on both sides; the pilot's score (win 1, tie ½, loss 0).
    fn playout(&self, state: &State, opponent_list: &Deck, me: usize, action: &Action, seed: u64) -> f64 {
        let code = PlayerCode::KM { max_depth: self.depth };
        let (d0, d1) = if me == 0 { (self.deck.clone(), opponent_list.clone()) } else { (opponent_list.clone(), self.deck.clone()) };
        let players = create_players(d0, d1, vec![code.clone(), code]);
        let mut game = Game::from_state(state.clone(), players, seed);
        game.apply_action(action);
        let mut ticks = 0;
        while !game.is_game_over() && ticks < 4000 {
            game.play_tick();
            ticks += 1;
        }
        match game.get_state_clone().winner {
            Some(GameOutcome::Win(w)) if w == me => 1.0,
            Some(GameOutcome::Win(_)) => 0.0,
            _ => 0.5,
        }
    }

}

impl PlayoutPlayer {
    /// The decision, with every candidate's play-outs. `rng` is the decision's own randomness (the engine's per-decision
    /// search seed); nothing else is random.
    pub fn evaluate(&mut self, rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> DecisionReport {
        let start = Instant::now();
        let _quiet = QuietDump::new();
        let me = observation.actor;
        let state = observation.visible_state();
        let km_move = self.km.decision_fn(&mut rng.clone(), observation, actions);
        let label = |a: &Action| format!("{:?}", a.action).chars().take(160).collect::<String>();
        let mut seen = BTreeSet::new();
        let mut distinct: Vec<Action> = vec![km_move.clone()];
        seen.insert(format!("{km_move:?}"));
        for a in actions {
            if seen.insert(format!("{a:?}")) {
                distinct.push(a.clone());
            }
        }
        let mut report = DecisionReport {
            knowledge: self.knowledge_label(),
            turn: state.turn_count,
            actor: me,
            candidates: vec![CandidateReport { action: km_move.clone(), label: label(&km_move), score: f64::NAN, diff: 0.0, se: f64::NAN }],
            dropped: vec![],
            km3: 0,
            chosen: 0,
            reason: String::new(),
            rounds: 0,
            failed_rounds: 0,
            millis: 0.0,
        };
        let opponent = 1 - me;
        let opponent_has_set_up =
            state.hands[opponent].len() + state.decks[opponent].cards.len() < self.core.opponent_list.cards.len();
        let skip = if distinct.len() < 2 {
            Some("one distinct move")
        } else if state.turn_count == 0 && opponent_has_set_up {
            Some("a setup choice after the opponent's hidden setup: km's move")
        } else if state.move_generation_stack.iter().any(|(_, choices)| choices.is_empty()) {
            Some("a hidden stack frame of the opponent's: km's move")
        } else {
            None
        };
        if let Some(why) = skip {
            report.reason = why.to_string();
            report.millis = start.elapsed().as_secs_f64() * 1000.0;
            return report;
        }
        let base = rng.clone().next_u64() ^ 0x4b58_504c_4159_4f55;
        let core = &self.core;
        let sample = |j: usize| {
            let mut sample_rng = StdRng::seed_from_u64(splitmix(base.wrapping_add(j as u64)));
            let (state, list, name) = core.sample_state(observation, &mut sample_rng);
            (state, list, name, splitmix(base ^ 0x5eed_0000_0000_0000 ^ j as u64))
        };
        // The cap: km's move, then the others by km's score after the move on the first sampled world.
        let mut candidates: Vec<Action> = distinct.clone();
        if candidates.len() > self.params.cap {
            let (world, list, _, seed) = sample(0);
            let code = PlayerCode::KM { max_depth: self.params.depth };
            let mut scored: Vec<(f64, Action)> = candidates[1..]
                .iter()
                .map(|a| {
                    let (d0, d1) = if me == 0 { (core.deck.clone(), list.clone()) } else { (list.clone(), core.deck.clone()) };
                    let mut game = Game::from_state(world.clone(), create_players(d0, d1, vec![code.clone(), code.clone()]), seed);
                    game.apply_action(a);
                    (value_functions::public_clock_effect_km_value_function(&game.get_state_clone(), me), a.clone())
                })
                .collect();
            scored.sort_by(|x, y| y.0.partial_cmp(&x.0).unwrap_or(std::cmp::Ordering::Equal));
            let keep = self.params.cap - 1;
            for (value, a) in &scored[keep..] {
                report.dropped.push(Dropped {
                    label: label(a),
                    reason: format!(
                        "beyond the cap of {}: km's score after the move on one sampled world, {value:.0}, is below the {keep} kept",
                        self.params.cap
                    ),
                });
            }
            candidates = std::iter::once(km_move.clone()).chain(scored.into_iter().take(keep).map(|(_, a)| a)).collect();
        }
        // The rounds: play-out j of every candidate from the same world and seed.
        let threads = rayon::current_num_threads().max(1);
        let mut results: Vec<Vec<f64>> = Vec::new();
        let total = self.params.rollouts;
        let mut next = 0;
        while next < total {
            let from = next;
            let to = if self.params.budget_ms == 0 { total } else { (from + threads).min(total) };
            next = to;
            // A play-out that panics (an engine bug in a sampled world) drops its whole round, so the rest stay paired.
            let batch: Vec<Option<Vec<f64>>> = (from..to)
                .into_par_iter()
                .map(|j| {
                    std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                        let (world, list, _, seed) = sample(j);
                        candidates.iter().map(|a| core.playout(&world, &list, me, a, seed)).collect::<Vec<f64>>()
                    }))
                    .ok()
                })
                .collect();
            report.failed_rounds += batch.iter().filter(|r| r.is_none()).count();
            results.extend(batch.into_iter().flatten());
            if self.params.budget_ms > 0
                && results.len() >= 2
                && start.elapsed().as_millis() as u64 >= self.params.budget_ms
            {
                break;
            }
        }
        report.rounds = results.len();
        if results.is_empty() {
            report.reason = format!("every play-out round failed ({}): km's move", report.failed_rounds);
            report.millis = start.elapsed().as_secs_f64() * 1000.0;
            return report;
        }
        let n = results.len() as f64;
        report.candidates = candidates
            .iter()
            .enumerate()
            .map(|(c, a)| {
                let score = results.iter().map(|r| r[c]).sum::<f64>() / n;
                let diffs: Vec<f64> = results.iter().map(|r| r[c] - r[0]).collect();
                let diff = diffs.iter().sum::<f64>() / n;
                let se = if results.len() < 2 {
                    f64::INFINITY
                } else {
                    (diffs.iter().map(|d| (d - diff).powi(2)).sum::<f64>() / (n - 1.0)).sqrt() / n.sqrt()
                };
                CandidateReport { action: a.clone(), label: label(a), score, diff, se: if c == 0 { 0.0 } else { se } }
            })
            .collect();
        // The best score (km's move first on a tie, then the offer order); it replaces km's only beyond the noise.
        let best = (0..report.candidates.len())
            .fold(0, |b, c| if report.candidates[c].score > report.candidates[b].score { c } else { b });
        let lead = &report.candidates[best];
        if best == 0 {
            report.reason = "km's move has the best play-out score".to_string();
        } else if lead.diff > 0.0 && lead.diff > self.params.z * lead.se {
            report.chosen = best;
            report.reason = format!(
                "play-outs: {:+.3} over km's move, {:.1} standard errors (threshold {})",
                lead.diff,
                if lead.se > 0.0 { lead.diff / lead.se } else { f64::INFINITY },
                self.params.z
            );
        } else {
            report.reason = format!(
                "within the noise: the best move leads km's by {:+.3} with a standard error of {:.3} (threshold {} SE): km's move kept",
                lead.diff, lead.se, self.params.z
            );
        }
        report.millis = start.elapsed().as_secs_f64() * 1000.0;
        report
    }

    fn trace(&self, report: &DecisionReport) {
        let line = serde_json::json!({
            "code": self.params.code(),
            "knowledge": report.knowledge,
            "turn": report.turn,
            "seat": report.actor,
            "rounds": report.rounds,
            "failed_rounds": report.failed_rounds,
            "ms": (report.millis * 10.0).round() / 10.0,
            "km_move": report.candidates[report.km3].label,
            "chosen": report.candidates[report.chosen].label,
            "changed": report.chosen != report.km3,
            "reason": report.reason,
            "candidates": report.candidates.iter().map(|c| serde_json::json!({
                "move": c.label,
                "score": if c.score.is_finite() { serde_json::json!((c.score * 1000.0).round() / 1000.0) } else { serde_json::Value::Null },
                "diff": (c.diff * 1000.0).round() / 1000.0,
                "se": if c.se.is_finite() { serde_json::json!((c.se * 1000.0).round() / 1000.0) } else { serde_json::Value::Null },
            })).collect::<Vec<_>>(),
            "dropped": report.dropped.iter().map(|d| serde_json::json!({"move": d.label, "reason": d.reason})).collect::<Vec<_>>(),
        });
        eprintln!("KX_TRACE {line}");
    }
}

/// The pause-games position runner (rl/results/pause_games_decisions_2026-10-02/harness/) patches km's search to print its
/// root scores whenever `PG_DUMP` is set, and sets it for the whole process. Inside this pilot every km decision of every
/// play-out would print, so the variable is switched off while the pilot decides and restored after (print-only; no
/// effect on play). The pilot's own table of candidates is its trace (`_trace`).
struct QuietDump(Option<std::ffi::OsString>);

impl QuietDump {
    fn new() -> Self {
        let saved = std::env::var_os("PG_DUMP");
        if saved.is_some() {
            std::env::remove_var("PG_DUMP");
        }
        QuietDump(saved)
    }
}

impl Drop for QuietDump {
    fn drop(&mut self) {
        if let Some(v) = self.0.take() {
            std::env::set_var("PG_DUMP", v);
        }
    }
}

impl Player for PlayoutPlayer {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, possible_actions: &[Action]) -> Action {
        if !self.printed {
            self.printed = true;
            eprintln!(
                "KX_PARAMS {}",
                serde_json::json!({
                    "code": self.params.code(),
                    "depth": self.params.depth,
                    "rollouts": self.params.rollouts,
                    "cap": self.params.cap,
                    "z": self.params.z,
                    "knowledge": self.knowledge_label(),
                    "budget_ms": self.params.budget_ms,
                    "seat": observation.actor,
                })
            );
        }
        let report = self.evaluate(rng, observation, possible_actions);
        self.decisions += 1;
        self.millis += report.millis;
        if self.params.trace {
            self.trace(&report);
        }
        report.candidates[report.chosen].action.clone()
    }

    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        self.km.decide_omniscient(rng, state, possible_actions)
    }

    fn get_deck(&self) -> Deck {
        self.core.deck.clone()
    }
}
