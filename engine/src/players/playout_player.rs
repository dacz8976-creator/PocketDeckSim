//! The play-out chooser (`kx<N>`; branch claude/playout-pilot, Oct 2; rl/results/planning_pilot_design_2026-10-02/DESIGN.md
//! sections 5 and 9). At each of its decisions with two or more distinct moves, the pilot plays every distinct legal move
//! (up to a cap) out to the end of the game `rollouts` times, with km<N> on both sides, and keeps the move whose play-outs
//! score best; when that move's lead over km<N>'s own move is within the noise, it keeps km<N>'s move.
//!
//! What it may see: only its `PlayerObservation` (its hand and board, the public board, discards, points, counts; its own
//! deck as an unordered multiset). Every play-out starts from a state sampled from that: its own deck order, the
//! opponent's hand and deck and every coin are drawn afresh per play-out. The opponent's hidden cards come from a list:
//! - LAB (a laboratory condition, labelled in every output): the opponent's exact 20-card list, only when that list is
//!   one of the pool's lists below; the meta side is never handed a brew's exact list, so LAB falls back to REALISTIC
//!   then, and says so;
//! - REALISTIC: per play-out, a list drawn from the candidate pool among those consistent with the opponent's cards seen
//!   so far (by name) and with the Energy types its Energy Zone shows; with none consistent, one of the closest (fewest
//!   seen cards missing, then fewest zone types missing), at random among the equally close. The unseen cards come from
//!   the list. REALISTIC never reads the opponent's real list.
//! The pool (`playout_pool.rs`): the lists of decks/screen/opponents and decks/research, duplicates removed (8 lists), plus
//! any added at run time through `KX_EXTRA_LISTS` (`name=path;...`; never a path under decks/brews), each recorded with a
//! hash of its file in `KX_PARAMS`, every `KX_TRACE` line and the knowledge label.
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
pub use super::playout_pool::{parse_extra_lists, under_brews, ExtraList};
use crate::actions::Action;
use crate::models::{Card, EnergyType};
use crate::observation::PlayerObservation;
use crate::state::GameOutcome;
use crate::{Deck, Game, State};

/// Pocket's deck size. The setup rule below reads this, never the opponent's real list, so REALISTIC reads no list.
const DECK_SIZE: usize = 20;

/// With a time budget, a move replaces km<N>'s only after at least this many completed rounds (two equal rounds give a
/// standard error of 0).
const MIN_ROUNDS_WITH_BUDGET: usize = 8;

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
    /// The time budget per decision in milliseconds (0: none). Play-outs stop after the rounds finished in time (at least
    /// 2); no move replaces km<N>'s with fewer than 8 rounds.
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
    /// The opponent lists the rounds drew, with how many rounds drew each (REALISTIC; LAB: the exact list).
    pub lists: BTreeMap<String, usize>,
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
    /// Calls of the diagnostic entry `decide_omniscient` (never made by `Game`): km's move, no play-outs, named in the trace.
    pub omniscient: usize,
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

/// A list's identity for the pool: its card-id multiset and its Energy types.
fn list_key(deck: &Deck) -> (Vec<String>, Vec<EnergyType>) {
    let mut energy = deck.energy_types.clone();
    energy.sort();
    energy.dedup();
    (id_multiset(deck), energy)
}

/// What the play-outs need, shared by the parallel rounds.
struct Core {
    deck: Deck,
    opponent_list: Deck,
    /// The candidate lists, duplicates removed: the meta lists, then any extra lists.
    pool: Vec<(String, Deck)>,
    /// How many of `pool` are meta lists (the rest are extra lists).
    meta: usize,
    /// The extra lists as read (name, path, hash), each with the pool name it went under.
    extras: Vec<(ExtraList, String)>,
    /// LAB is in force: requested, and the opponent's list is one of the pool's; with the pool name it matched.
    lab: Option<String>,
    depth: usize,
}

impl PlayoutPlayer {
    /// The pilot, with any lists from `KX_EXTRA_LISTS` (read once per process). Panics if that variable is refused (a
    /// path under decks/brews, an unreadable list): the run stops rather than play with it.
    pub fn new(deck: Deck, opponent_list: Deck, params: PlayoutParams) -> Self {
        let extras = super::playout_pool::extra_lists().clone().unwrap_or_else(|e| panic!("{e}"));
        Self::with_extra_lists(deck, opponent_list, params, extras)
    }

    /// The pilot with these extra lists (tests; `new` passes those of `KX_EXTRA_LISTS`).
    pub fn with_extra_lists(deck: Deck, opponent_list: Deck, params: PlayoutParams, extra_lists: Vec<ExtraList>) -> Self {
        let km = get_player(deck.clone(), &opponent_list, &PlayerCode::KM { max_depth: params.depth });
        // The pool, duplicates (same cards, same Energy types) removed at load: each research/X equals t-X.
        let mut pool: Vec<(String, Deck)> = Vec::new();
        for (name, path, _, text) in super::playout_pool::POOL.iter() {
            let list = Deck::from_string(text).unwrap_or_else(|e| panic!("the pool's {path}: {e}"));
            if !pool.iter().any(|(_, d)| list_key(d) == list_key(&list)) {
                pool.push((name.to_string(), list));
            }
        }
        let meta = pool.len();
        let mut extras = Vec::new();
        for extra in extra_lists {
            let under = match pool.iter().find(|(_, d)| list_key(d) == list_key(&extra.deck)) {
                Some((name, _)) => name.clone(),
                None => {
                    let name = format!("extra:{}", extra.name);
                    pool.push((name.clone(), extra.deck.clone()));
                    name
                }
            };
            extras.push((extra, under));
        }
        // LAB only: is the opponent's list one of the pool's? (REALISTIC never looks at it. km<N> is handed it as every
        // bot is, and ignores it: get_player's km arm builds its search from the own deck alone.)
        let lab = (params.knowledge == Knowledge::Lab)
            .then(|| {
                let target = id_multiset(&opponent_list);
                pool.iter().find(|(_, d)| id_multiset(d) == target).map(|(name, _)| name.clone())
            })
            .flatten();
        let core = Core { deck, opponent_list, pool, meta, extras, lab, depth: params.depth };
        PlayoutPlayer { params, km, core, printed: false, decisions: 0, millis: 0.0, omniscient: 0 }
    }

    pub fn params(&self) -> &PlayoutParams {
        &self.params
    }

    /// The pool as the labels describe it: "8 meta lists" plus any extra lists by name.
    fn pool_description(&self) -> String {
        let extra = self.core.pool.len() - self.core.meta;
        let mut text = format!("{} meta lists", self.core.meta);
        if !self.core.extras.is_empty() {
            let names: Vec<String> = self.core.extras.iter().map(|(e, under)| {
                if under.starts_with("extra:") { e.name.clone() } else { format!("{} (the same cards as {under})", e.name) }
            }).collect();
            text += &format!(" and {extra} extra list{} from KX_EXTRA_LISTS: {}", if extra == 1 { "" } else { "s" }, names.join(", "));
        }
        text
    }

    /// The knowledge mode in force, as every output labels it.
    pub fn knowledge_label(&self) -> String {
        match (self.params.knowledge, &self.core.lab) {
            (Knowledge::Lab, Some(name)) => format!(
                "LAB (laboratory condition: the opponent's exact 20-card list is known: {name}, one of the pool's {})",
                self.pool_description()
            ),
            (Knowledge::Lab, None) => format!(
                "REALISTIC (LAB asked, but the opponent's list is not one of the pool's {}, so it is never handed over)",
                self.pool_description()
            ),
            _ => format!(
                "REALISTIC (the opponent's list is drawn per play-out from the pool's {}, among those consistent with the cards seen and the Energy Zone)",
                self.pool_description()
            ),
        }
    }

    /// The extra lists as `KX_PARAMS` and every `KX_TRACE` line record them.
    fn extras_json(&self) -> serde_json::Value {
        serde_json::Value::Array(self.core.extras.iter().map(|(e, under)| serde_json::json!({
            "name": e.name, "path": e.path, "fnv1a64": e.fnv1a64, "pool_name": under,
        })).collect())
    }
}

impl Core {
    /// The opponent's cards seen so far: in play (with the cards under an evolution and Tools), discarded, their Stadium,
    /// any revealed from their hand, their known deck-top cards, and any other known to be in their deck.
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
        // The known deck-top cards, then the deck's other known cards (a top card also listed as in the deck counts once).
        let top = &observation.revealed.deck_top[opponent];
        seen.extend(top.iter().cloned());
        let mut membership = observation.revealed.opponent_deck_membership.clone();
        for card in top {
            if let Some(i) = membership.iter().position(|c| c == card) {
                membership.swap_remove(i);
            }
        }
        seen.extend(membership);
        seen.retain(|c| !c.is_unknown());
        seen
    }

    /// The Energy types the opponent's Energy Zone shows (current and next), public from the first decision.
    fn zone_types(observation: &PlayerObservation) -> Vec<EnergyType> {
        let zone = &observation.visible_state().energy_zone[1 - observation.actor];
        let mut types: Vec<EnergyType> = zone.current.iter().chain(zone.next.iter()).cloned().collect();
        types.sort();
        types.dedup();
        types
    }

    /// Makes `list` hold the seen printings: for each seen card (as a multiset) the list's own copy of that printing if
    /// it has one left, else one of its unmatched cards of the same name, replaced by the seen printing. So the sampler's
    /// removal of the seen cards takes them all out, and two seen copies of one printing against a list holding two
    /// printings of that card leave no third copy. Used by both modes.
    fn adopt_seen_printings(list: &mut Deck, seen: &[Card]) {
        let mut matched = vec![false; list.cards.len()];
        let mut pending = Vec::new();
        for card in seen {
            match (0..list.cards.len()).find(|&i| !matched[i] && list.cards[i] == *card) {
                Some(i) => matched[i] = true,
                None => pending.push(card),
            }
        }
        for card in pending {
            if let Some(i) = (0..list.cards.len()).find(|&i| !matched[i] && list.cards[i].get_name() == card.get_name()) {
                list.cards[i] = card.clone();
                matched[i] = true;
            }
        }
    }

    /// REALISTIC: a pool list consistent with the seen cards (every name seen no more often than the list holds it) and
    /// with the Energy Zone (its Energy types include every type the zone shows), uniformly. With none consistent, one of
    /// the closest: fewest seen cards it can't account for, then fewest zone types it lacks; at random among the equally
    /// close (with the world's own rng, so still deterministic). Then the seen printings are adopted.
    fn sample_list(&self, seen: &[Card], zone: &[EnergyType], rng: &mut StdRng) -> (Deck, String) {
        let mut seen_names: BTreeMap<String, usize> = BTreeMap::new();
        for c in seen {
            *seen_names.entry(c.get_name()).or_default() += 1;
        }
        let distance = |deck: &Deck| -> (usize, usize) {
            let missing = seen_names
                .iter()
                .map(|(name, n)| n.saturating_sub(deck.cards.iter().filter(|c| c.get_name() == *name).count()))
                .sum();
            let energy = zone.iter().filter(|t| !deck.energy_types.contains(t)).count();
            (missing, energy)
        };
        let distances: Vec<(usize, usize)> = self.pool.iter().map(|(_, d)| distance(d)).collect();
        let best = *distances.iter().min().expect("a non-empty pool");
        let nearest: Vec<usize> = (0..self.pool.len()).filter(|&i| distances[i] == best).collect();
        let i = nearest[rng.gen_range(0..nearest.len())];
        let label = if best == (0, 0) {
            format!("{} (1 of {} consistent)", self.pool[i].0, nearest.len())
        } else {
            format!("{} (closest, 1 of {} tied; no list consistent)", self.pool[i].0, nearest.len())
        };
        let mut deck = self.pool[i].1.clone();
        Self::adopt_seen_printings(&mut deck, seen);
        (deck, label)
    }

    /// One sampled world: a full state consistent with the observation, the list its opponent's hidden cards came from,
    /// and that list's name.
    fn sample_state(&self, observation: &PlayerObservation, rng: &mut StdRng) -> (State, Deck, String) {
        let seen = Self::seen_opponent_cards(observation);
        let (list, name) = if self.lab.is_some() {
            let mut list = self.opponent_list.clone();
            Self::adopt_seen_printings(&mut list, &seen);
            (list, "the exact list (LAB)".to_string())
        } else {
            self.sample_list(&seen, &Self::zone_types(observation), rng)
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
            lists: BTreeMap::new(),
            millis: 0.0,
        };
        let opponent = 1 - me;
        // Every list is 20 cards: the rule reads the constant, never the opponent's real list.
        let opponent_has_set_up = state.hands[opponent].len() + state.decks[opponent].cards.len() < DECK_SIZE;
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
        // The cap: km's move, then the others by km's score after the move on the first sampled world. The ranking runs
        // inside catch_unwind: a move whose ranking panics (an engine panic in the sampled world or the move) scores
        // NEG_INFINITY and is always a named drop, so a panic here never stops the game.
        let mut candidates: Vec<Action> = distinct.clone();
        if candidates.len() > self.params.cap {
            let code = PlayerCode::KM { max_depth: self.params.depth };
            let world0 = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| sample(0))).ok();
            let mut scored: Vec<(f64, Action)> = candidates[1..]
                .iter()
                .map(|a| {
                    let value = world0.as_ref().and_then(|(world, list, _, seed)| {
                        std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                            let (d0, d1) = if me == 0 { (core.deck.clone(), list.clone()) } else { (list.clone(), core.deck.clone()) };
                            let mut game = Game::from_state(world.clone(), create_players(d0, d1, vec![code.clone(), code.clone()]), *seed);
                            game.apply_action(a);
                            value_functions::public_clock_effect_km_value_function(&game.get_state_clone(), me)
                        }))
                        .ok()
                    });
                    (value.unwrap_or(f64::NEG_INFINITY), a.clone())
                })
                .collect();
            scored.sort_by(|x, y| y.0.partial_cmp(&x.0).unwrap_or(std::cmp::Ordering::Equal));
            let keep = (self.params.cap - 1).min(scored.iter().filter(|(v, _)| *v > f64::NEG_INFINITY).count());
            for (value, a) in &scored[keep..] {
                report.dropped.push(Dropped {
                    label: label(a),
                    reason: if *value == f64::NEG_INFINITY {
                        "panicked: its ranking for the cap failed (an engine panic), so it is dropped".to_string()
                    } else {
                        format!(
                            "beyond the cap of {}: km's score after the move on one sampled world, {value:.0}, is below the {keep} kept",
                            self.params.cap
                        )
                    },
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
            let batch: Vec<Option<(Vec<f64>, String)>> = (from..to)
                .into_par_iter()
                .map(|j| {
                    std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                        let (world, list, name, seed) = sample(j);
                        (candidates.iter().map(|a| core.playout(&world, &list, me, a, seed)).collect::<Vec<f64>>(), name)
                    }))
                    .ok()
                })
                .collect();
            report.failed_rounds += batch.iter().filter(|r| r.is_none()).count();
            for (round, name) in batch.into_iter().flatten() {
                *report.lists.entry(name).or_default() += 1;
                results.push(round);
            }
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
        } else if self.params.budget_ms > 0 && report.rounds < MIN_ROUNDS_WITH_BUDGET {
            report.reason = format!(
                "the time budget ended after {} rounds, fewer than the {MIN_ROUNDS_WITH_BUDGET} a switch needs: km's move kept (the best move led by {:+.3})",
                report.rounds, lead.diff
            );
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
            "extra_lists": self.extras_json(),
            "turn": report.turn,
            "seat": report.actor,
            "rounds": report.rounds,
            "failed_rounds": report.failed_rounds,
            "lists": report.lists,
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
                    "extra_lists": self.extras_json(),
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

    /// The diagnostic entry point with a full state (`Game` never calls it in play): km's move, no play-outs, since play-outs
    /// from a full state would see the hidden cards. Counted, and named in the trace.
    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        let action = self.km.decide_omniscient(rng, state, possible_actions);
        self.omniscient += 1;
        if self.params.trace {
            eprintln!(
                "KX_TRACE {}",
                serde_json::json!({
                    "code": self.params.code(),
                    "knowledge": self.knowledge_label(),
                    "extra_lists": self.extras_json(),
                    "turn": state.turn_count,
                    "seat": state.current_player,
                    "omniscient": true,
                    "km_move": format!("{:?}", action.action),
                    "chosen": format!("{:?}", action.action),
                    "changed": false,
                    "reason": "an omniscient call (the diagnostic entry with the full state, never made by Game): km's move, no play-outs",
                })
            );
        }
        action
    }

    fn get_deck(&self) -> Deck {
        self.core.deck.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;

    fn pilot() -> PlayoutPlayer {
        let (deck_a, deck_b) = crate::test_support::load_test_decks();
        PlayoutPlayer::with_extra_lists(deck_a, deck_b, PlayoutParams::new(3), Vec::new())
    }

    /// The pool loads 8 lists: each research/X holds the same cards and Energy as t-X.
    #[test]
    fn the_pool_holds_8_lists_once_duplicates_are_removed() {
        let p = pilot();
        assert_eq!((p.core.pool.len(), p.core.meta), (8, 8));
        assert!(p.core.pool.iter().all(|(name, _)| name.starts_with("t-")));
        assert!(p.knowledge_label().contains("8 meta lists"), "{}", p.knowledge_label());
    }

    /// The Energy Zone rules: with Water showing, only Water lists are consistent (t-suicune alone), every draw.
    #[test]
    fn a_list_must_hold_the_energy_its_zone_shows() {
        let p = pilot();
        for seed in 0..40 {
            let (deck, label) = p.core.sample_list(&[], &[EnergyType::Water], &mut StdRng::seed_from_u64(seed));
            assert!(deck.energy_types.contains(&EnergyType::Water), "seed {seed}: {label}");
            assert_eq!(label, "t-suicune (1 of 1 consistent)");
        }
        // Grass shows: t-sceptile and t-vespiquen, both drawn.
        let names: BTreeSet<String> = (0..40)
            .map(|seed| p.core.sample_list(&[], &[EnergyType::Grass], &mut StdRng::seed_from_u64(seed)).1)
            .collect();
        assert_eq!(names, BTreeSet::from(["t-sceptile (1 of 2 consistent)".to_string(), "t-vespiquen (1 of 2 consistent)".to_string()]));
    }

    /// With no list consistent, the closest are tied and drawn at random (not always the pool's first): a Metal zone and
    /// a seen Bulbasaur fit none of the 8, and all 8 are equally close.
    #[test]
    fn the_closest_tie_is_broken_at_random() {
        let p = pilot();
        let seen = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
        let names: BTreeSet<String> = (0..80)
            .map(|seed| p.core.sample_list(&seen, &[EnergyType::Metal], &mut StdRng::seed_from_u64(seed)).1)
            .collect();
        assert_eq!(names.len(), 8, "{names:?}");
        assert!(names.iter().all(|n| n.ends_with("(closest, 1 of 8 tied; no list consistent)")), "{names:?}");
        // Missing seen cards count first, then zone types: Psychic showing and a seen Swablu leave t-altaria alone.
        let swablu = vec![get_card_by_enum(CardId::B1196Swablu)];
        let (_, label) = p.core.sample_list(&swablu, &[EnergyType::Metal], &mut StdRng::seed_from_u64(1));
        assert_eq!(label, "t-altaria (closest, 1 of 1 tied; no list consistent)");
    }

    /// The printing swap counts copies: two seen copies of one Sabrina printing against a list holding two different
    /// printings take both slots, leaving no third Sabrina; an exact printing is matched in place.
    #[test]
    fn the_seen_printings_are_adopted_copy_for_copy() {
        let a = get_card_by_enum(CardId::A1225Sabrina);
        let b = get_card_by_enum(CardId::A1272Sabrina);
        let other = get_card_by_enum(CardId::A1001Bulbasaur);
        let mut list = Deck { cards: vec![a.clone(), b.clone(), other.clone()], energy_types: vec![EnergyType::Grass] };
        Core::adopt_seen_printings(&mut list, &[a.clone(), a.clone()]);
        assert_eq!(list.cards, vec![a.clone(), a.clone(), other.clone()]);
        let mut list = Deck { cards: vec![a.clone(), b.clone(), other.clone()], energy_types: vec![EnergyType::Grass] };
        Core::adopt_seen_printings(&mut list, &[b.clone()]);
        assert_eq!(list.cards, vec![a, b, other]);
    }
}
