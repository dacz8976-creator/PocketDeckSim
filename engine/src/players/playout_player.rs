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
//! - REALISTIC: per play-out, a list drawn from the candidate pool: first the lists whose Energy types cover the types
//!   the opponent's Energy Zone shows, then among those the lists holding every card seen so far (by name). The unseen
//!   cards come from the list. With none left (an unfamiliar opponent), the list is inferred (round 4): from the pooled
//!   lists covering the zone, the most similar to what the opponent has shown (seen cards by name, zone types) are the
//!   sources, one drawn per play-out as the base, weighted by similarity; the seen cards are kept and the base's cards
//!   fill the rest, so the sampled opponent can play. Labelled "inferred from N lists". REALISTIC never reads the
//!   opponent's real list.
//! The pool (`playout_pool.rs`; `_poolwide`, the default, or `_poolmeta`): the meta pool is the lists of
//! decks/screen/opponents and decks/research, duplicates removed (8 lists); the wide pool adds every other list under
//! decks/ but Dustin's own and the brews and drafts, and the six B2e held-out lists. Plus any added at run time through
//! `KX_EXTRA_LISTS` (`name=path;...`; never a brew's or one of Dustin's), each recorded with a hash of its file in
//! `KX_PARAMS`, every `KX_TRACE` line and the knowledge label.
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
//!
//! A diagnostic beside it (Oct 5, `continuation_study`, playout_plan.rs): first moves played out from the same sampled
//! worlds and seeds as `evaluate`'s, each continued by km<N> and by a scripted plan for the pilot's next K own turns.
//!
//! The Tool-placement rule (Oct 6, `_tools`, off by default; playout_tools.rs): in the play-outs, on both sides, a Tool is
//! attached only where its printed effect can apply; `tool_rule_study` plays the same worlds with the rule off and on.
//! The same `_tools` breaks ties at kx<N>'s own decision (Oct 6, the amended follow-up): every placement is played out, and
//! only when no move clears the z bar and km<N>'s placement has no printed effect while another has one does kx<N> play
//! the placement with an effect ("tie-break: Tool effect").
//!
//! "Attack when you can" (Oct 6, quiz 4; `_za<z>`, off by default): a switch from km<N>'s attack to a move that isn't one
//! needs a lead beyond z_attack standard errors; the reason names both scores, for a switch and for one the bar stops.
use std::cell::{Cell, RefCell};
use std::collections::{BTreeMap, BTreeSet};
use std::rc::Rc;
use std::time::Instant;

use rand::seq::SliceRandom;
use rand::{rngs::StdRng, Rng, RngCore, SeedableRng};
use rayon::prelude::*;

use super::{create_players, get_player, value_functions, Player, PlayerCode};
pub use super::playout_pool::{
    find_repository, parse_extra_lists, parse_extra_lists_against, protected_lists, under_protected, ExtraList, POOL, WIDE,
};

#[path = "playout_plan.rs"]
pub mod playout_plan;
use playout_plan::{PlanPlayer, Progress};
pub use playout_plan::{Plan, PlanTally, PlanTurn, Spot, Step};

#[path = "playout_tools.rs"]
pub mod playout_tools;
#[path = "playout_effects.rs"]
pub mod playout_effects;
pub use playout_effects::{action_card, effect_needs, effect_now, need_met, CardKind, Need, PokemonFilter, Reading, Scope};
pub use playout_tools::{
    conditions_hold, kept_by_playouts, placements_with_effect, tie_break_placements, tool_conditions, ToolConditions,
    ToolRulePlayer, ToolSpot,
};
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

/// How many of the most similar pooled lists an inferred list draws on.
const INFER_LISTS: usize = 3;

/// At most this many evolution cards an inferred list adds for the seen Pokémon's own lines.
const INFER_EVOLUTIONS: usize = 8;

/// Every Pokémon card of the database by the name it evolves from, in card-id order (read once).
fn evolutions_by_name() -> &'static BTreeMap<String, Vec<Card>> {
    use strum::IntoEnumIterator;
    static MAP: std::sync::OnceLock<BTreeMap<String, Vec<Card>>> = std::sync::OnceLock::new();
    MAP.get_or_init(|| {
        let mut map: BTreeMap<String, Vec<Card>> = BTreeMap::new();
        for id in crate::card_ids::CardId::iter() {
            let card = crate::database::get_card_by_enum(id);
            if let Card::Pokemon(p) = &card {
                if let Some(from) = &p.evolves_from {
                    map.entry(from.clone()).or_default().push(card.clone());
                }
            }
        }
        map
    })
}

/// Which lists REALISTIC draws from (and LAB's membership check reads).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PoolSet {
    /// The 8 meta lists of Oct 2 (decks/screen/opponents, decks/research).
    Meta,
    /// The meta lists and every other allowed list (round 4; the default).
    Wide,
}

/// What the pilot knows of the opponent's list.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Knowledge {
    /// The opponent's exact list (a meta list only): a laboratory condition.
    Lab,
    /// A list sampled per play-out from the candidate pool, consistent with the cards seen.
    Realistic,
}

/// The pilot's parameters; every one is part of its code
/// (`kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<s>][_trace][_poolmeta|_poolwide][_tools][_noeffect][_za<z>|_zs<z>][_m<R_max>]`).
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
    /// The candidate pool (`_poolwide`, the default, or `_poolmeta`).
    pub pool: PoolSet,
    /// The Tool-placement rule (`_tools`; off by default): in the play-outs, and as a within-noise tie-break at the pilot's
    /// own decision (playout_tools.rs).
    pub tools: bool,
    /// No-effect actions (`_noeffect`; Oct 6, quiz 4; off by default): a within-noise tie-break at the pilot's own decision
    /// away from a move of km<depth>'s whose printed effect can do nothing now (playout_effects.rs).
    pub noeffect: bool,
    /// "Attack when you can" (`_za<z>`; Oct 6, quiz 4; off by default): when km<depth>'s move is an attack and the best
    /// candidate isn't one, the switch needs a lead beyond this many standard errors instead of z.
    pub z_attack: Option<f64>,
    /// The skip bar (`_zs<z>`; Oct 7, the narrower attack bar; off by default): when km<depth>'s move is an attack and the
    /// best candidate isn't one, the switch needs a lead beyond this many standard errors only if that candidate's own line
    /// leaves the turn without an attack (in more than half of its play-outs). Not with `_za`.
    pub z_skip: Option<f64>,
    /// Close calls (`_m<R_max>`; Oct 7; off by default): when the decision after the R rounds is a close call (`close_call`:
    /// the best leads km<depth>'s move within the bar that decides the switch, or another candidate is within z standard
    /// errors of the best), the best, the candidates close to it and km<depth>'s move play rounds R to R_max, from the same
    /// worlds and seeds a larger R would use, and the decision is made once, at the end, among them on their rounds. Above
    /// R; not with a time budget.
    pub max_rounds: Option<usize>,
}

impl PlayoutParams {
    pub fn new(depth: usize) -> Self {
        PlayoutParams {
            depth,
            rollouts: 16,
            cap: 12,
            z: 2.0,
            knowledge: Knowledge::Realistic,
            budget_ms: 0,
            trace: false,
            pool: PoolSet::Wide,
            tools: false,
            noeffect: false,
            z_attack: None,
            z_skip: None,
            max_rounds: None,
        }
    }

    /// Parses the code after the `kx` prefix (lowercase), e.g. `3_r8_c5_z1.5_lab_t30_trace`.
    pub fn parse(rest: &str) -> Result<Self, String> {
        let invalid = |why: &str| {
            format!("Invalid player code: kx{rest} ({why}). Use 'kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<seconds>][_trace][_poolmeta|_poolwide][_tools][_noeffect][_za<z>|_zs<z>][_m<R_max>]', e.g. 'kx3' or 'kx3_r24_c12_z2_lab'")
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
                "poolmeta" => params.pool = PoolSet::Meta,
                "poolwide" => params.pool = PoolSet::Wide,
                "tools" => params.tools = true,
                "noeffect" => params.noeffect = true,
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
                p if p.starts_with("za") => {
                    params.z_attack =
                        Some(p[2..].parse::<f64>().ok().filter(|z| z.is_finite() && *z >= 0.0).ok_or_else(|| invalid(part))?);
                }
                p if p.starts_with("zs") => {
                    params.z_skip =
                        Some(p[2..].parse::<f64>().ok().filter(|z| z.is_finite() && *z >= 0.0).ok_or_else(|| invalid(part))?);
                }
                p if p.starts_with('z') => {
                    params.z = p[1..].parse::<f64>().ok().filter(|z| z.is_finite() && *z >= 0.0).ok_or_else(|| invalid(part))?;
                }
                p if p.starts_with('t') => params.budget_ms = number(&p[1..])? * 1000,
                p if p.starts_with('m') => params.max_rounds = Some(number(&p[1..])? as usize),
                _ => return Err(invalid(&format!("unknown part '{part}'"))),
            }
        }
        if params.z_attack.is_some() && params.z_skip.is_some() {
            return Err(invalid("the attack bar and the skip bar together"));
        }
        if let Some(m) = params.max_rounds {
            if m <= params.rollouts {
                return Err(invalid("an R_max above R"));
            }
            if params.budget_ms > 0 {
                return Err(invalid("the extension with a time budget"));
            }
        }
        Ok(params)
    }

    /// The canonical code, every parameter spelled out (the Tool rule and the attack bar only when on, so the codes without
    /// them are as before).
    pub fn code(&self) -> String {
        format!(
            "kx{}_r{}_c{}_z{}_{}_t{}{}_pool{}{}{}{}{}{}",
            self.depth,
            self.rollouts,
            self.cap,
            self.z,
            if self.knowledge == Knowledge::Lab { "lab" } else { "real" },
            self.budget_ms / 1000,
            if self.trace { "_trace" } else { "" },
            if self.pool == PoolSet::Meta { "meta" } else { "wide" },
            if self.tools { "_tools" } else { "" },
            if self.noeffect { "_noeffect" } else { "" },
            self.z_attack.map_or(String::new(), |z| format!("_za{z}")),
            self.z_skip.map_or(String::new(), |z| format!("_zs{z}")),
            self.max_rounds.map_or(String::new(), |m| format!("_m{m}"))
        )
    }
}

/// The bar a switch from km<N>'s move `km` to `best` must clear, in standard errors: `z_attack` when `km` is an attack and
/// `best` isn't (`_za<z>`), else `z`.
pub fn switch_bar(km: &Action, best: &Action, z: f64, z_attack: Option<f64>) -> f64 {
    let attack = |a: &Action| matches!(a.action, crate::actions::SimpleAction::Attack(_));
    match z_attack {
        Some(za) if attack(km) && !attack(best) => za,
        _ => z,
    }
}

/// The bar a switch from km<N>'s move `km` to `best` must clear, in standard errors, with the skip bar (`_zs<z>`):
/// `z_skip` when `km` is an attack, `best` isn't, and `best`'s own line leaves the turn without an attack in more than half
/// of its play-outs (it attacked before the turn ended in `attacks` of `rounds`); else `z`.
pub fn skip_bar(km: &Action, best: &Action, attacks: usize, rounds: usize, z: f64, z_skip: Option<f64>) -> f64 {
    let attack = |a: &Action| matches!(a.action, crate::actions::SimpleAction::Attack(_));
    match z_skip {
        Some(zs) if attack(km) && !attack(best) && attacks * 2 < rounds => zs,
        _ => z,
    }
}

/// The bar the decision puts on a switch from km<N>'s move `km` to `best`, whose line attacked this turn in `attacks` of
/// its `rounds` play-outs: the skip bar with `_zs<z>`, the attack bar with `_za<z>`, else z.
fn decision_bar(params: &PlayoutParams, km: &Action, best: &Action, attacks: usize, rounds: usize) -> f64 {
    if params.z_skip.is_some() {
        skip_bar(km, best, attacks, rounds, params.z, params.z_skip)
    } else {
        switch_bar(km, best, params.z, params.z_attack)
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
    /// Play-outs in which the pilot's side attacked before the decision's turn ended (Oct 7; for the skip bar).
    pub attacks_this_turn: usize,
    /// The rounds this candidate was played: R, or more for a close call's candidates (`_m<R_max>`). Its score is over
    /// them, and its difference from km<N>'s move over the same rounds of km<N>'s.
    pub rounds: usize,
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
    /// Set when the cap's ranking world itself panicked: named once here, and the cap kept the moves in the order offered.
    pub cap_note: Option<String>,
    pub millis: f64,
}

/// One play-out's end in the continuation study: the pilot's score, a digest of the final state (FNV-1a 64 of its JSON)
/// and the final turn.
#[derive(Debug, Clone, PartialEq, serde::Serialize)]
pub struct Outcome {
    pub score: f64,
    pub digest: u64,
    pub turn: u8,
}

/// One first move in the continuation study: round j's play-out continued by km<N> (`km[j]`) and by the plan
/// (`plan[j]`), from the same world and seed; and what the plan did over the rounds.
#[derive(Debug, Clone, serde::Serialize)]
pub struct ContinuationMove {
    pub action: Action,
    pub label: String,
    pub km: Vec<Outcome>,
    pub plan: Vec<Outcome>,
    pub counts: PlanTally,
    /// Round 0's pilot moves within the K turns, under the plan and under km<N> (logged by a plan of K empty turns, whose
    /// play-out must end in km[0]'s final state: `km3_trace_is_km3`).
    pub plan_trace: Vec<String>,
    pub km3_trace: Vec<String>,
    pub km3_trace_is_km3: bool,
}

/// One move in the Tool-rule study: round j's play-out with the rule off (`off[j]`) and on (`on[j]`), from the same world
/// and seed, and how many placements the rule changed in it (`interventions[j]`; with none, `on[j]` is `off[j]`).
#[derive(Debug, Clone, serde::Serialize)]
pub struct ToolRuleMove {
    pub action: Action,
    pub label: String,
    pub off: Vec<Outcome>,
    pub on: Vec<Outcome>,
    pub interventions: Vec<usize>,
}

/// The Tool-rule study at one decision.
#[derive(Debug, Clone, serde::Serialize)]
pub struct ToolRuleReport {
    pub knowledge: String,
    pub rounds: usize,
    pub failed_rounds: usize,
    pub lists: BTreeMap<String, usize>,
    pub moves: Vec<ToolRuleMove>,
    pub millis: f64,
}

/// The continuation study at one decision.
#[derive(Debug, Clone, serde::Serialize)]
pub struct ContinuationReport {
    pub knowledge: String,
    /// The plan's own turns played (K, at most the plan's turns).
    pub k: usize,
    pub rounds: usize,
    pub failed_rounds: usize,
    pub lists: BTreeMap<String, usize>,
    pub moves: Vec<ContinuationMove>,
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

/// The pilot's score at a game's end: win 1, tie ½, loss 0.
fn score(end: &State, me: usize) -> f64 {
    match end.winner {
        Some(GameOutcome::Win(w)) if w == me => 1.0,
        Some(GameOutcome::Win(_)) => 0.0,
        _ => 0.5,
    }
}

/// A decision's base for its rounds' worlds and seeds, from the decision's own randomness (which it doesn't advance).
fn round_base(rng: &StdRng) -> u64 {
    rng.clone().next_u64() ^ 0x4b58_504c_4159_4f55
}

/// A paired comparison's mean difference and standard error (`a` minus `b`, round by round), and whether the two are
/// equal in every round.
fn paired(a: &[(f64, bool)], b: &[(f64, bool)]) -> (f64, f64, bool) {
    let d: Vec<f64> = a.iter().zip(b).map(|(x, y)| x.0 - y.0).collect();
    let n = d.len() as f64;
    let m = d.iter().sum::<f64>() / n;
    let se = (d.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (n - 1.0)).sqrt() / n.sqrt();
    (m, se, d.iter().all(|x| *x == 0.0))
}

/// A close call (`_m<R_max>`), from each candidate's R rounds (`per[c]`, km's move first; `candidates[c]` its move). The
/// best is the one with the highest mean (the first on a tie, km's move first). Close to it:
/// - km's move, when the best is another move whose lead over it is within the bar that would decide that switch (the
///   decision's own bar, `decision_bar`: z_skip from km's attack to a line that skips it, z_attack, or z);
/// - another move the best leads by no more than z standard errors (paired), unless the two are equal in every round.
/// If any is close: those, the best and km's move, in order, less any move equal to km's in every round (it can't win: ties
/// go to km's move); else none.
pub fn close_call(per: &[Vec<(f64, bool)>], candidates: &[Action], params: &PlayoutParams) -> Vec<usize> {
    let full = per[0].len();
    if full < 2 {
        return Vec::new();
    }
    let mean = |c: usize| per[c].iter().map(|x| x.0).sum::<f64>() / full as f64;
    let best = (0..per.len()).fold(0, |b, c| if mean(c) > mean(b) { c } else { b });
    let close: Vec<usize> = (0..per.len())
        .filter(|&c| c != best)
        .filter(|&c| {
            let (m, se, equal) = paired(&per[best], &per[c]);
            if c == 0 {
                let attacks = per[best].iter().filter(|x| x.1).count();
                m <= decision_bar(params, &candidates[0], &candidates[best], attacks, full) * se
            } else {
                !equal && m <= params.z * se
            }
        })
        .collect();
    if close.is_empty() {
        return Vec::new();
    }
    let mut set: BTreeSet<usize> = close.into_iter().collect();
    set.insert(best);
    set.insert(0);
    set.into_iter().filter(|&c| c == 0 || !paired(&per[c], &per[0]).2).collect()
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
    /// The candidate lists, duplicates removed: the meta lists, then any extra lists.
    pool: Vec<(String, Deck)>,
    /// How many of `pool` are meta lists, and how many are listed (meta and wide); the rest are extra lists.
    meta: usize,
    listed: usize,
    /// The extra lists as read (name, path, hash), each with the pool name it went under.
    extras: Vec<(ExtraList, String)>,
    /// LAB is in force: requested, and the opponent's list is one of the pool's. The pool name it matched and the
    /// opponent's list itself, which the pilot keeps only then: REALISTIC holds no opponent list, by construction.
    lab: Option<(String, Deck)>,
    depth: usize,
    /// The Tool-placement rule in the play-outs.
    tools: bool,
}

impl PlayoutPlayer {
    /// The pilot, with any lists from `KX_EXTRA_LISTS` (read once per process). Panics if that variable is refused (a
    /// brew's or one of Dustin's lists, by path or by content; an unreadable list; no repository to check against): the
    /// run stops rather than play with it.
    pub fn new(deck: Deck, opponent_list: Deck, params: PlayoutParams) -> Self {
        let extras = super::playout_pool::extra_lists().clone().unwrap_or_else(|e| panic!("{e}"));
        Self::with_extra_lists(deck, opponent_list, params, extras)
    }

    /// The pilot with these extra lists (tests; `new` passes those of `KX_EXTRA_LISTS`).
    pub fn with_extra_lists(deck: Deck, opponent_list: Deck, params: PlayoutParams, extra_lists: Vec<ExtraList>) -> Self {
        let km = get_player(deck.clone(), &opponent_list, &PlayerCode::KM { max_depth: params.depth });
        // The pool, duplicates (same cards, same Energy types) removed at load: each research/X equals t-X. The meta lists,
        // then (the wide pool) the others.
        let mut pool: Vec<(String, Deck)> = Vec::new();
        let mut meta = 0;
        let wide: &[(&str, &str, &str, &str)] = if params.pool == PoolSet::Wide { &WIDE } else { &[] };
        for (k, (name, path, _, text)) in POOL.iter().chain(wide.iter()).enumerate() {
            let list = Deck::from_string(text).unwrap_or_else(|e| panic!("the pool's {path}: {e}"));
            if !pool.iter().any(|(_, d)| list_key(d) == list_key(&list)) {
                pool.push((name.to_string(), list));
            }
            if k + 1 == POOL.len() {
                meta = pool.len();
            }
        }
        let listed = pool.len();
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
        // LAB only: is the opponent's list one of the pool's? Kept only then. (REALISTIC never holds it. km<N> is handed
        // it as `Game` hands every bot, and ignores it: get_player's km arm builds its search from the own deck alone.)
        let lab = (params.knowledge == Knowledge::Lab)
            .then(|| {
                let target = id_multiset(&opponent_list);
                pool.iter().find(|(_, d)| id_multiset(d) == target).map(|(name, _)| (name.clone(), opponent_list.clone()))
            })
            .flatten();
        let core = Core { deck, pool, meta, listed, extras, lab, depth: params.depth, tools: params.tools };
        PlayoutPlayer { params, km, core, printed: false, decisions: 0, millis: 0.0, omniscient: 0 }
    }

    pub fn params(&self) -> &PlayoutParams {
        &self.params
    }

    /// The pool as the labels describe it: "the pool's 8 meta lists", or "the wide pool's 35 lists (8 meta lists and 27
    /// more)", plus any extra lists by name.
    fn pool_description(&self) -> String {
        let extra = self.core.pool.len() - self.core.listed;
        let mut text = if self.params.pool == PoolSet::Wide {
            format!(
                "the wide pool's {} lists ({} meta lists and {} more)",
                self.core.listed,
                self.core.meta,
                self.core.listed - self.core.meta
            )
        } else {
            format!("the pool's {} meta lists", self.core.meta)
        };
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
            (Knowledge::Lab, Some((name, _))) => format!(
                "LAB (laboratory condition: the opponent's exact 20-card list is known: {name}, one of {})",
                self.pool_description()
            ),
            (Knowledge::Lab, None) => format!(
                "REALISTIC (LAB asked, but the opponent's list is not one of {}, so it is never handed over)",
                self.pool_description()
            ),
            _ => format!(
                "REALISTIC (the opponent's list is drawn per play-out from {}, among those consistent with the cards seen and the Energy Zone, else inferred from the most similar)",
                self.pool_description()
            ),
        }
    }

    /// The extra lists as `KX_PARAMS` and every `KX_TRACE` line record them.
    fn extras_json(&self) -> serde_json::Value {
        serde_json::Value::Array(self.core.extras.iter().map(|(e, under)| serde_json::json!({
            "name": e.name, "path": e.path, "fnv1a64": e.fnv1a64, "pool_name": under, "checked_against": e.checked_against,
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

    /// The pool lists consistent with what the opponent has shown: first the lists whose Energy types cover every type
    /// the Energy Zone shows, then among those the lists holding each seen card's name at least as often as it was seen.
    /// It depends on the observation alone, so it is the same in every round of a decision.
    fn consistent_lists(&self, seen: &[Card], zone: &[EnergyType]) -> Vec<usize> {
        let mut seen_names: BTreeMap<String, usize> = BTreeMap::new();
        for c in seen {
            *seen_names.entry(c.get_name()).or_default() += 1;
        }
        (0..self.pool.len())
            .filter(|&i| zone.iter().all(|t| self.pool[i].1.energy_types.contains(t)))
            .filter(|&i| {
                let list = &self.pool[i].1;
                seen_names.iter().all(|(name, n)| list.cards.iter().filter(|c| c.get_name() == *name).count() >= *n)
            })
            .collect()
    }

    /// With no consistent list (an unfamiliar opponent), the list is inferred rather than left to placeholders (round 4).
    /// - The candidates are the lists covering the zone's types (all lists if none does).
    /// - Each is scored by its similarity to what the opponent has shown: the seen cards it holds (by name, at most as
    ///   often as seen) plus the zone types it plays. The most similar (up to 3; pool order on ties) are the sources.
    /// - One source is drawn as the base, weighted by its score. The seen cards are kept as seen, and the base's own
    ///   cards fill the rest; a seen card stands for one of the base's copies of its name. With too little room, the
    ///   base's Trainers go first, so its evolution lines stay whole. Any room left is filled from the other sources.
    ///   Pocket's limit of 2 copies of a name holds throughout.
    /// - The seen Pokémon's own evolution lines come before the base's cards (2 copies a stage, at most 8 cards): a player
    ///   showing Torchic plays its evolutions, which no similar list may hold. See `seen_evolution_lines`.
    /// - The Energy is the zone's types (the base's if the zone shows none), so it never contradicts the zone.
    fn inferred_list(&self, seen: &[Card], zone: &[EnergyType], rng: &mut StdRng) -> (Deck, String) {
        let covers = |d: &Deck| zone.iter().all(|t| d.energy_types.contains(t));
        let mut candidates: Vec<usize> = (0..self.pool.len()).filter(|&i| covers(&self.pool[i].1)).collect();
        if candidates.is_empty() {
            candidates = (0..self.pool.len()).collect();
        }
        let mut seen_names: BTreeMap<String, usize> = BTreeMap::new();
        for c in seen {
            *seen_names.entry(c.get_name()).or_default() += 1;
        }
        let similarity = |d: &Deck| -> usize {
            let shared: usize = seen_names
                .iter()
                .map(|(name, n)| (*n).min(d.cards.iter().filter(|c| c.get_name() == *name).count()))
                .sum();
            shared + zone.iter().filter(|t| d.energy_types.contains(t)).count()
        };
        let mut ranked: Vec<(usize, usize)> = candidates.iter().map(|&i| (similarity(&self.pool[i].1), i)).collect();
        ranked.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
        ranked.truncate(INFER_LISTS);
        let weights: Vec<usize> = ranked.iter().map(|(score, _)| (*score).max(1)).collect();
        let mut pick = rng.gen_range(0..weights.iter().sum::<usize>());
        let base = weights
            .iter()
            .position(|w| {
                if pick < *w {
                    true
                } else {
                    pick -= w;
                    false
                }
            })
            .unwrap_or(0);
        let order: Vec<usize> = std::iter::once(ranked[base].1)
            .chain(ranked.iter().map(|(_, i)| *i).filter(|&i| i != ranked[base].1))
            .collect();
        let mut cards: Vec<Card> = seen.to_vec();
        let mut copies: BTreeMap<String, usize> = seen_names.clone();
        for card in self.seen_evolution_lines(seen) {
            let n = copies.entry(card.get_name()).or_default();
            if *n < 2 && cards.len() < DECK_SIZE {
                *n += 1;
                cards.push(card);
            }
        }
        for (k, &i) in order.iter().enumerate() {
            if cards.len() >= DECK_SIZE {
                break;
            }
            // This source's cards, its copies of a name already in the list (seen, or a seen line's) used up by those.
            let mut used = copies.clone();
            let rest: Vec<Card> = self.pool[i]
                .1
                .cards
                .iter()
                .filter(|c| match used.get_mut(&c.get_name()) {
                    Some(u) if *u > 0 => {
                        *u -= 1;
                        false
                    }
                    _ => true,
                })
                .cloned()
                .collect();
            let room = DECK_SIZE - cards.len();
            let (mut pokemon, mut trainers): (Vec<Card>, Vec<Card>) = rest.into_iter().partition(|c| matches!(c, Card::Pokemon(_)));
            trainers.shuffle(rng);
            if k > 0 {
                pokemon.shuffle(rng);
            }
            while pokemon.len() + trainers.len() > room && !trainers.is_empty() {
                trainers.pop();
            }
            while pokemon.len() > room {
                pokemon.pop();
            }
            for card in pokemon.into_iter().chain(trainers) {
                let n = copies.entry(card.get_name()).or_default();
                if *n < 2 && cards.len() < DECK_SIZE {
                    *n += 1;
                    cards.push(card);
                }
            }
        }
        // Only a pool far smaller than the shipped ones could leave room; such slots stay unknown.
        cards.resize(DECK_SIZE.max(cards.len()), Card::Unknown);
        let energy = if zone.is_empty() { self.pool[ranked[base].1].1.energy_types.clone() } else { zone.to_vec() };
        let label = format!("inferred from {} lists: {}", ranked.len(), self.pool[ranked[base].1].0);
        (Deck { cards, energy_types: energy }, label)
    }

    /// The evolution lines of the seen Pokémon, for an inferred list: for each seen Pokémon, the cards that evolve from it
    /// (the database's), then theirs, 2 copies a stage, at most `INFER_EVOLUTIONS` cards in all. Where several evolve from
    /// one Pokémon, those a pooled list plays are taken (all of them), else the first in card-id order; a name's printing
    /// is one a pooled list plays, else the first. Stages already seen count towards their 2 copies.
    fn seen_evolution_lines(&self, seen: &[Card]) -> Vec<Card> {
        let pooled = |card: &Card| self.pool.iter().any(|(_, d)| d.cards.contains(card));
        let pooled_name = |name: &str| self.pool.iter().any(|(_, d)| d.cards.iter().any(|c| c.get_name() == name));
        let mut queue: Vec<String> = Vec::new();
        for c in seen {
            if let Card::Pokemon(_) = c {
                if !queue.contains(&c.get_name()) {
                    queue.push(c.get_name());
                }
            }
        }
        let mut out: Vec<Card> = Vec::new();
        let mut k = 0;
        while k < queue.len() && out.len() < INFER_EVOLUTIONS {
            let from = queue[k].clone();
            k += 1;
            let Some(evolutions) = evolutions_by_name().get(&from) else { continue };
            let mut names: Vec<String> = Vec::new();
            for e in evolutions {
                if !names.contains(&e.get_name()) {
                    names.push(e.get_name());
                }
            }
            let known: Vec<String> = names.iter().filter(|n| pooled_name(n)).cloned().collect();
            let chosen = if known.is_empty() { names.into_iter().take(1).collect() } else { known };
            for name in chosen {
                let printings: Vec<&Card> = evolutions.iter().filter(|e| e.get_name() == name).collect();
                let printing = printings.iter().find(|e| pooled(e)).or(printings.first()).map(|e| (*e).clone());
                if let Some(card) = printing {
                    let have = seen.iter().chain(out.iter()).filter(|c| c.get_name() == name).count();
                    for _ in have..2 {
                        if out.len() < INFER_EVOLUTIONS {
                            out.push(card.clone());
                        }
                    }
                    if !queue.contains(&name) {
                        queue.push(name);
                    }
                }
            }
        }
        out
    }

    /// REALISTIC: a consistent list, uniformly, with the seen printings adopted; with none, an inferred list.
    fn sample_list(&self, seen: &[Card], zone: &[EnergyType], rng: &mut StdRng) -> (Deck, String) {
        let consistent = self.consistent_lists(seen, zone);
        if consistent.is_empty() {
            return self.inferred_list(seen, zone, rng);
        }
        let i = consistent[rng.gen_range(0..consistent.len())];
        let mut deck = self.pool[i].1.clone();
        Self::adopt_seen_printings(&mut deck, seen);
        (deck, format!("{} (1 of {} consistent)", self.pool[i].0, consistent.len()))
    }

    /// One sampled world: a full state consistent with the observation, the list its opponent's hidden cards came from,
    /// and that list's name.
    fn sample_state(&self, observation: &PlayerObservation, rng: &mut StdRng) -> (State, Deck, String) {
        let seen = Self::seen_opponent_cards(observation);
        let (list, name) = if let Some((_, exact)) = &self.lab {
            let mut list = exact.clone();
            Self::adopt_seen_printings(&mut list, &seen);
            (list, "the exact list (LAB)".to_string())
        } else {
            self.sample_list(&seen, &Self::zone_types(observation), rng)
        };
        let mut state = observation.search_state_with_opponent_list(rng, &list);
        let opponent = 1 - observation.actor;
        // Slots the list couldn't fill (a printing it doesn't hold) take random named cards of the list, so no Unknown is
        // played.
        let named: Vec<Card> = list.cards.iter().filter(|c| !c.is_unknown()).cloned().collect();
        let mut slots: Vec<&mut Card> = state.hands[opponent].iter_mut().chain(state.decks[opponent].cards.iter_mut()).collect();
        for slot in slots.iter_mut().filter(|c| c.is_unknown()) {
            **slot = named.choose(rng).cloned().unwrap_or(Card::Unknown);
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

    /// Round j of a decision: its sampled world, the list the opponent's hidden cards came from and its name, and the game
    /// seed. Play-out j of every candidate starts from it (common random numbers); `base` is `round_base` of the
    /// decision's randomness.
    fn sample_round(&self, observation: &PlayerObservation, base: u64, j: usize) -> (State, Deck, String, u64) {
        let mut sample_rng = StdRng::seed_from_u64(splitmix(base.wrapping_add(j as u64)));
        let (state, list, name) = self.sample_state(observation, &mut sample_rng);
        (state, list, name, splitmix(base ^ 0x5eed_0000_0000_0000 ^ j as u64))
    }

    /// Plays `action` from `state` to the end with km<N> on both sides; the pilot's score (win 1, tie ½, loss 0), and
    /// whether the pilot's side attacked before the decision's turn ended.
    fn playout(&self, state: &State, opponent_list: &Deck, me: usize, action: &Action, seed: u64) -> (f64, bool) {
        let (end, _, _, attacked) = self.play_out(state, opponent_list, me, action, seed, None, self.tools);
        (score(&end, me), attacked)
    }

    /// `playout`'s game, ending in its final state. With a plan, the pilot's side follows it for K own turns from
    /// `state`'s (playout_plan.rs) and km<N> plays the rest, and the plan's tally comes back; without one (or with K = 0)
    /// it is km<N> on both sides. With `tools`, km<N> on both sides places Tools by the Tool-placement rule
    /// (playout_tools.rs), and the rule's interventions are counted. The last value says whether the pilot's side attacked
    /// before `state`'s turn ended (the first move included; Oct 7, the skip bar).
    fn play_out(
        &self,
        state: &State,
        opponent_list: &Deck,
        me: usize,
        action: &Action,
        seed: u64,
        plan: Option<(&Plan, usize)>,
        tools: bool,
    ) -> (State, Option<(PlanTally, Vec<String>)>, usize, bool) {
        let code = PlayerCode::KM { max_depth: self.depth };
        let (d0, d1) = if me == 0 { (self.deck.clone(), opponent_list.clone()) } else { (opponent_list.clone(), self.deck.clone()) };
        let mut players = create_players(d0, d1, vec![code.clone(), code]);
        let interventions = Rc::new(Cell::new(0));
        if tools {
            players = players
                .into_iter()
                .map(|inner| Box::new(ToolRulePlayer { inner, interventions: interventions.clone() }) as Box<dyn Player>)
                .collect();
        }
        let progress = plan.map(|(plan, k)| {
            let progress = Rc::new(RefCell::new(Progress::new(plan, k, me, state.turn_count as usize)));
            let km = players.remove(me);
            players.insert(me, Box::new(PlanPlayer { km, progress: progress.clone() }));
            progress.borrow_mut().observe(state, action);
            progress.borrow_mut().note(state, action, "first move");
            progress
        });
        let mut game = Game::from_state(state.clone(), players, seed);
        let is_attack = |a: &Action| a.actor == me && matches!(a.action, crate::actions::SimpleAction::Attack(_));
        let mut attacked = is_attack(action);
        game.apply_action(action);
        // Watched only while the decision's turn lasts (and no attack yet): it reads the state, it changes nothing.
        let mut in_turn = !attacked && game.get_state_clone().turn_count == state.turn_count;
        let mut ticks = 0;
        while !game.is_game_over() && ticks < 4000 {
            if let Some(progress) = &progress {
                progress.borrow_mut().before_tick(&game.get_state_clone());
            }
            let a = game.play_tick();
            ticks += 1;
            if in_turn {
                attacked = is_attack(&a);
                in_turn = !attacked && game.get_state_clone().turn_count == state.turn_count;
            }
        }
        let end = game.get_state_clone();
        let tally = progress.map(|p| {
            let mut p = p.borrow_mut();
            (p.finish(&end), p.take_log())
        });
        (end, tally, interventions.get(), attacked)
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
        // The Tool rule's tie-break (`_tools`, playout_tools.rs): when km's proposal is a placement without a printed effect
        // now and another has one, the placement with an effect km prefers (its choice among those, the same randomness as
        // in the play-outs). Every move stays in the pool; it decides only within the noise, after the play-outs.
        let tie_break = if self.params.tools {
            tie_break_placements(state, actions, &km_move)
                .map(|(effective, why)| (self.km.decision_fn(&mut rng.clone(), observation, &effective), effective, why))
        } else {
            None
        };
        // The no-effect tie-break (`_noeffect`, playout_effects.rs): when km's move can do nothing now by its card's text, km's
        // choice among the moves that do something (the same randomness). Decided only within the noise, after the play-outs.
        let noeffect_break = if self.params.noeffect && effect_now(state, &km_move, &observation.known_own_deck) == Some(false) {
            let doing: Vec<Action> =
                actions.iter().filter(|a| effect_now(state, a, &observation.known_own_deck) != Some(false)).cloned().collect();
            let why = format!("km's {} can do nothing now by its text", action_card(state, &km_move).unwrap_or_default());
            (!doing.is_empty()).then(|| (self.km.decision_fn(&mut rng.clone(), observation, &doing), doing, why))
        } else {
            None
        };
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
            candidates: vec![CandidateReport {
                action: km_move.clone(),
                label: label(&km_move),
                score: f64::NAN,
                diff: 0.0,
                se: f64::NAN,
                attacks_this_turn: 0,
                rounds: 0,
            }],
            dropped: vec![],
            km3: 0,
            chosen: 0,
            reason: String::new(),
            rounds: 0,
            failed_rounds: 0,
            lists: BTreeMap::new(),
            cap_note: None,
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
        let base = round_base(rng);
        let core = &self.core;
        let sample = |j: usize| core.sample_round(observation, base, j);
        // The cap: km's move, then the others by km's score after the move on the first sampled world. The ranking runs
        // inside catch_unwind: a move whose ranking panics (an engine panic in the sampled world or the move) scores
        // NEG_INFINITY and is always a named drop, so a panic here never stops the game.
        let mut candidates: Vec<Action> = distinct.clone();
        if candidates.len() > self.params.cap {
            let code = PlayerCode::KM { max_depth: self.params.depth };
            let keep = self.params.cap - 1;
            match std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| sample(0))) {
                Err(_) => {
                    // No world to rank in: say so once, and keep the first moves in the order offered.
                    report.cap_note = Some(format!(
                        "the ranking world panicked (an engine panic sampling it): the cap of {} kept the first {keep} moves in the order offered",
                        self.params.cap
                    ));
                    for a in &candidates[1 + keep..] {
                        report.dropped.push(Dropped {
                            label: label(a),
                            reason: format!("beyond the cap of {}, in the order offered (the ranking world panicked)", self.params.cap),
                        });
                    }
                    candidates.truncate(1 + keep);
                }
                Ok((world, list, _, seed)) => {
                    let mut scored: Vec<(f64, Action)> = candidates[1..]
                        .iter()
                        .map(|a| {
                            let value = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                                let (d0, d1) =
                                    if me == 0 { (core.deck.clone(), list.clone()) } else { (list.clone(), core.deck.clone()) };
                                let mut game =
                                    Game::from_state(world.clone(), create_players(d0, d1, vec![code.clone(), code.clone()]), seed);
                                game.apply_action(a);
                                value_functions::public_clock_effect_km_value_function(&game.get_state_clone(), me)
                            }));
                            (value.unwrap_or(f64::NEG_INFINITY), a.clone())
                        })
                        .collect();
                    scored.sort_by(|x, y| y.0.partial_cmp(&x.0).unwrap_or(std::cmp::Ordering::Equal));
                    let keep = keep.min(scored.iter().filter(|(v, _)| *v > f64::NEG_INFINITY).count());
                    for (value, a) in &scored[keep..] {
                        report.dropped.push(Dropped {
                            label: label(a),
                            reason: if *value == f64::NEG_INFINITY {
                                "panicked: applying this move in the ranking world failed (an engine panic), so it is dropped".to_string()
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
            }
        }
        // The rounds: play-out j of every candidate from the same world and seed.
        let threads = rayon::current_num_threads().max(1);
        let mut results: Vec<Vec<(f64, bool)>> = Vec::new();
        let total = self.params.rollouts;
        let mut next = 0;
        while next < total {
            let from = next;
            let to = if self.params.budget_ms == 0 { total } else { (from + threads).min(total) };
            next = to;
            // A play-out that panics (an engine bug in a sampled world) drops its whole round, so the rest stay paired.
            let batch: Vec<Option<(Vec<(f64, bool)>, String)>> = (from..to)
                .into_par_iter()
                .map(|j| {
                    std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                        let (world, list, name, seed) = sample(j);
                        (candidates.iter().map(|a| core.playout(&world, &list, me, a, seed)).collect::<Vec<(f64, bool)>>(), name)
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
        // Each candidate's rounds, in order.
        let mut per: Vec<Vec<(f64, bool)>> = (0..candidates.len()).map(|c| results.iter().map(|r| r[c]).collect()).collect();
        // Close calls (`_m<R_max>`): the close call's candidates and km's move play rounds R to R_max (the same worlds and
        // seeds as a larger R), and the decision is made at the end on their rounds; the others keep their R rounds. A round
        // in which one of them panics is dropped for all of them.
        let mut extension = None;
        if let (Some(max_rounds), 0) = (self.params.max_rounds, self.params.budget_ms) {
            let in_play = close_call(&per, &candidates, &self.params);
            if !in_play.is_empty() && total < max_rounds {
                let from = per[0].len();
                let batch: Vec<Option<(Vec<(f64, bool)>, String)>> = (total..max_rounds)
                    .into_par_iter()
                    .map(|j| {
                        std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                            let (world, list, name, seed) = sample(j);
                            (in_play.iter().map(|&c| core.playout(&world, &list, me, &candidates[c], seed)).collect::<Vec<(f64, bool)>>(), name)
                        }))
                        .ok()
                    })
                    .collect();
                report.failed_rounds += batch.iter().filter(|r| r.is_none()).count();
                for (round, name) in batch.into_iter().flatten() {
                    *report.lists.entry(name).or_default() += 1;
                    for (k, &c) in in_play.iter().enumerate() {
                        per[c].push(round[k]);
                    }
                }
                extension = Some((from, per[0].len()));
            }
        }
        report.rounds = per[0].len();
        report.candidates = candidates
            .iter()
            .enumerate()
            .map(|(c, a)| {
                let rounds = per[c].len();
                let n = rounds as f64;
                let score = per[c].iter().map(|x| x.0).sum::<f64>() / n;
                let diffs: Vec<f64> = per[c].iter().zip(&per[0]).map(|(x, k)| x.0 - k.0).collect();
                let diff = diffs.iter().sum::<f64>() / n;
                let se = if rounds < 2 {
                    f64::INFINITY
                } else {
                    (diffs.iter().map(|d| (d - diff).powi(2)).sum::<f64>() / (n - 1.0)).sqrt() / n.sqrt()
                };
                let attacks_this_turn = per[c].iter().filter(|x| x.1).count();
                CandidateReport { action: a.clone(), label: label(a), score, diff, se: if c == 0 { 0.0 } else { se }, attacks_this_turn, rounds }
            })
            .collect();
        // The best score among the candidates with the most rounds (after a close call the extended ones, else all of them;
        // km's move first on a tie, then the offer order); it replaces km's only beyond the noise.
        let best = (0..report.candidates.len())
            .filter(|&c| report.candidates[c].rounds == report.rounds)
            .fold(0, |b, c| if report.candidates[c].score > report.candidates[b].score { c } else { b });
        let lead = &report.candidates[best];
        // The bar: z; or (`_za<z>`) z_attack for a switch from km's attack to a move that isn't one; or (`_zs<z>`) z_skip for
        // such a switch whose line leaves the turn without an attack.
        let attack = |a: &Action| matches!(a.action, crate::actions::SimpleAction::Attack(_));
        let from_attack = best != 0 && attack(&report.candidates[0].action) && !attack(&lead.action);
        let bar = decision_bar(&self.params, &report.candidates[0].action, &lead.action, lead.attacks_this_turn, lead.rounds);
        let away = (self.params.z_attack.is_some() || self.params.z_skip.is_some()) && from_attack;
        // With the skip bar, what the best move's line does this turn, in its play-outs.
        let line = if self.params.z_skip.is_none() {
            String::new()
        } else if lead.attacks_this_turn * 2 < lead.rounds {
            format!(", and no attack this turn in its line (an attack in {} of {} play-outs)", lead.attacks_this_turn, lead.rounds)
        } else {
            format!(" to a line that attacks this turn in {} of {} play-outs", lead.attacks_this_turn, lead.rounds)
        };
        let scores = format!("km's attack {:.3}, this move {:.3}", report.candidates[0].score, lead.score);
        if best == 0 {
            report.reason = "km's move has the best play-out score".to_string();
        } else if self.params.budget_ms > 0 && report.rounds < MIN_ROUNDS_WITH_BUDGET {
            report.reason = format!(
                "the time budget ended after {} rounds, fewer than the {MIN_ROUNDS_WITH_BUDGET} a switch needs: km's move kept (the best move led by {:+.3})",
                report.rounds, lead.diff
            );
        } else if lead.diff > 0.0 && lead.diff > bar * lead.se {
            report.chosen = best;
            report.reason = format!(
                "play-outs: {:+.3} over km's move, {:.1} standard errors (threshold {})",
                lead.diff,
                if lead.se > 0.0 { lead.diff / lead.se } else { f64::INFINITY },
                bar
            );
            if away {
                report.reason = format!("{}; away from km's attack{line}: {scores}", report.reason);
            }
        } else if away && lead.diff > 0.0 && lead.diff > self.params.z * lead.se {
            report.reason = format!(
                "the {} bar: the best move leads km's attack by {:+.3}, {:.1} standard errors, past z {} but not the {} bar {}{line} ({scores}): km's attack kept",
                if self.params.z_skip.is_some() { "skip" } else { "attack" },
                lead.diff,
                if lead.se > 0.0 { lead.diff / lead.se } else { f64::INFINITY },
                self.params.z,
                if self.params.z_skip.is_some() { "skip" } else { "attack" },
                bar
            );
        } else {
            report.reason = format!(
                "within the noise: the best move leads km's by {:+.3} with a standard error of {:.3} (threshold {} SE): km's move kept",
                lead.diff, lead.se, bar
            );
        }
        // The tie-break: no move cleared the bar, so km's move would stand; if it is a placement without an effect now and
        // a placement with one is in the pool, that one is played, unless km's leads it beyond the noise.
        if let (0, Some((preferred, effective, why))) = (report.chosen, &tie_break) {
            let target = report.candidates.iter().position(|c| c.action == *preferred).or_else(|| {
                (0..report.candidates.len())
                    .filter(|&c| effective.contains(&report.candidates[c].action))
                    .fold(None, |b: Option<usize>, c| match b {
                        Some(b) if report.candidates[b].score >= report.candidates[c].score => Some(b),
                        _ => Some(c),
                    })
            });
            if let Some(t) = target {
                let c = &report.candidates[t];
                let sd = |se: f64| if se > 0.0 { format!("{:.1}", c.diff.abs() / se) } else { "inf".to_string() };
                if kept_by_playouts(c.diff, c.se, self.params.z) {
                    report.reason = format!(
                        "{}; {why}, but its play-outs lead the placement with one, {}, by {:+.3} ({} standard errors): km's move kept",
                        report.reason,
                        c.label,
                        -c.diff,
                        sd(c.se)
                    );
                } else {
                    report.reason = format!(
                        "tie-break: Tool effect: {why}, and no move clears the bar ({}); the placement with an effect km prefers is played, {} ({:+.3} v km's, {} standard errors)",
                        report.reason,
                        c.label,
                        c.diff,
                        sd(c.se)
                    );
                    report.chosen = t;
                }
            }
        }
        // The no-effect tie-break: no move cleared the bar and km's move can do nothing now; km's choice among the moves that
        // do something is played, unless km's move leads it beyond the noise.
        if let (0, Some((preferred, doing, why))) = (report.chosen, &noeffect_break) {
            let target = report.candidates.iter().position(|c| c.action == *preferred).or_else(|| {
                (0..report.candidates.len())
                    .filter(|&c| doing.contains(&report.candidates[c].action))
                    .fold(None, |b: Option<usize>, c| match b {
                        Some(b) if report.candidates[b].score >= report.candidates[c].score => Some(b),
                        _ => Some(c),
                    })
            });
            if let Some(t) = target {
                let c = &report.candidates[t];
                let sd = |se: f64| if se > 0.0 { format!("{:.1}", c.diff.abs() / se) } else { "inf".to_string() };
                if kept_by_playouts(c.diff, c.se, self.params.z) {
                    report.reason = format!(
                        "{}; {why}, but its play-outs lead km's choice among the moves that do something, {}, by {:+.3} ({} standard errors): km's move kept",
                        report.reason,
                        c.label,
                        -c.diff,
                        sd(c.se)
                    );
                } else {
                    report.reason = format!(
                        "tie-break: no effect now: {why}, and no move clears the bar ({}); km's choice among the moves that do something is played, {} ({:+.3} v km's, {} standard errors)",
                        report.reason,
                        c.label,
                        c.diff,
                        sd(c.se)
                    );
                    report.chosen = t;
                }
            }
        }
        if let Some((from, to)) = extension {
            let n = report.candidates.iter().filter(|c| c.rounds > from).count();
            report.reason = format!("{}; close call: play-outs extended from {from} to {to} rounds for {n} candidates", report.reason);
        }
        report.millis = start.elapsed().as_secs_f64() * 1000.0;
        report
    }

    /// The continuation study (Oct 5; a diagnostic, not a decision): each of `moves` is played out `rounds` times from
    /// round j's sampled world and seed, exactly as `evaluate` does at the same decision randomness, and each play-out is
    /// continued twice: by km<N> on both sides (`evaluate`'s play-out itself), and with the pilot's side following `plan`
    /// for its next `k` own turns, then km<N> (playout_plan.rs). A round in which any play-out panics is dropped whole, so
    /// the rest stay paired.
    pub fn continuation_study(
        &self,
        rng: &mut StdRng,
        observation: &PlayerObservation,
        moves: &[Action],
        plan: &Plan,
        k: usize,
        rounds: usize,
    ) -> ContinuationReport {
        let start = Instant::now();
        let _quiet = QuietDump::new();
        let me = observation.actor;
        let base = round_base(rng);
        let core = &self.core;
        let k = k.min(plan.turns.len());
        let outcome = |end: &State| Outcome {
            score: score(end, me),
            digest: super::playout_pool::fnv1a64(serde_json::to_string(end).unwrap_or_default().as_bytes()),
            turn: end.turn_count,
        };
        // A plan of K empty turns: km<N>'s play, logged.
        let km_logged = Plan { turns: vec![PlanTurn::default(); k], promote: Vec::new() };
        type Round = (Outcome, Outcome, PlanTally, Option<(Vec<String>, Vec<String>, bool)>);
        let results: Vec<Option<(Vec<Round>, String)>> = (0..rounds)
            .into_par_iter()
            .map(|j| {
                std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                    let (world, list, name, seed) = core.sample_round(observation, base, j);
                    let per_move = moves
                        .iter()
                        .map(|a| {
                            let (km_end, _, _, _) = core.play_out(&world, &list, me, a, seed, None, core.tools);
                            let (plan_end, logged, _, _) = core.play_out(&world, &list, me, a, seed, Some((plan, k)), core.tools);
                            let (tally, plan_log) = logged.unwrap_or_default();
                            let traces = (j == 0).then(|| {
                                let (end, logged, _, _) = core.play_out(&world, &list, me, a, seed, Some((&km_logged, k)), core.tools);
                                (plan_log, logged.unwrap_or_default().1, outcome(&end) == outcome(&km_end))
                            });
                            (outcome(&km_end), outcome(&plan_end), tally, traces)
                        })
                        .collect();
                    (per_move, name)
                }))
                .ok()
            })
            .collect();
        let label = |a: &Action| format!("{:?}", a.action).chars().take(160).collect::<String>();
        let mut report = ContinuationReport {
            knowledge: self.knowledge_label(),
            k,
            rounds: 0,
            failed_rounds: results.iter().filter(|r| r.is_none()).count(),
            lists: BTreeMap::new(),
            moves: moves
                .iter()
                .map(|a| ContinuationMove {
                    action: a.clone(),
                    label: label(a),
                    km: Vec::new(),
                    plan: Vec::new(),
                    counts: PlanTally::new(plan, k),
                    plan_trace: Vec::new(),
                    km3_trace: Vec::new(),
                    km3_trace_is_km3: false,
                })
                .collect(),
            millis: 0.0,
        };
        for (per_move, name) in results.into_iter().flatten() {
            report.rounds += 1;
            *report.lists.entry(name).or_default() += 1;
            for (m, (km, planned, tally, traces)) in report.moves.iter_mut().zip(per_move) {
                m.km.push(km);
                m.plan.push(planned);
                m.counts.add(&tally);
                if let Some((plan_trace, km3_trace, same)) = traces {
                    (m.plan_trace, m.km3_trace, m.km3_trace_is_km3) = (plan_trace, km3_trace, same);
                }
            }
        }
        report.millis = start.elapsed().as_secs_f64() * 1000.0;
        report
    }

    /// The Tool-rule study (Oct 6): each of `moves` played out `rounds` times from round j's sampled world and seed, as
    /// `evaluate` does at the same decision randomness, once with the Tool-placement rule and once without (whatever the
    /// pilot's own `_tools`). A play-out in which the rule never acts is the same game both ways, so it is played once.
    /// A round in which any play-out panics is dropped whole.
    pub fn tool_rule_study(&self, rng: &mut StdRng, observation: &PlayerObservation, moves: &[Action], rounds: usize) -> ToolRuleReport {
        let start = Instant::now();
        let _quiet = QuietDump::new();
        let me = observation.actor;
        let base = round_base(rng);
        let core = &self.core;
        let outcome = |end: &State| Outcome {
            score: score(end, me),
            digest: super::playout_pool::fnv1a64(serde_json::to_string(end).unwrap_or_default().as_bytes()),
            turn: end.turn_count,
        };
        let results: Vec<Option<(Vec<(Outcome, Outcome, usize)>, String)>> = (0..rounds)
            .into_par_iter()
            .map(|j| {
                std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                    let (world, list, name, seed) = core.sample_round(observation, base, j);
                    let per_move = moves
                        .iter()
                        .map(|a| {
                            let (on_end, _, n, _) = core.play_out(&world, &list, me, a, seed, None, true);
                            let on = outcome(&on_end);
                            let off = if n == 0 { on.clone() } else { outcome(&core.play_out(&world, &list, me, a, seed, None, false).0) };
                            (off, on, n)
                        })
                        .collect();
                    (per_move, name)
                }))
                .ok()
            })
            .collect();
        let label = |a: &Action| format!("{:?}", a.action).chars().take(160).collect::<String>();
        let mut report = ToolRuleReport {
            knowledge: self.knowledge_label(),
            rounds: 0,
            failed_rounds: results.iter().filter(|r| r.is_none()).count(),
            lists: BTreeMap::new(),
            moves: moves
                .iter()
                .map(|a| ToolRuleMove { action: a.clone(), label: label(a), off: Vec::new(), on: Vec::new(), interventions: Vec::new() })
                .collect(),
            millis: 0.0,
        };
        for (per_move, name) in results.into_iter().flatten() {
            report.rounds += 1;
            *report.lists.entry(name).or_default() += 1;
            for (m, (off, on, n)) in report.moves.iter_mut().zip(per_move) {
                m.off.push(off);
                m.on.push(on);
                m.interventions.push(n);
            }
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
            "candidates": report.candidates.iter().map(|c| {
                let mut j = serde_json::json!({
                    "move": c.label,
                    "score": if c.score.is_finite() { serde_json::json!((c.score * 1000.0).round() / 1000.0) } else { serde_json::Value::Null },
                    "diff": (c.diff * 1000.0).round() / 1000.0,
                    "se": if c.se.is_finite() { serde_json::json!((c.se * 1000.0).round() / 1000.0) } else { serde_json::Value::Null },
                });
                // The skip bar's count and the extension's rounds, only with their parameters (the trace is otherwise as
                // before).
                if self.params.z_skip.is_some() {
                    j["attacks_this_turn"] = serde_json::json!(c.attacks_this_turn);
                }
                if self.params.max_rounds.is_some() {
                    j["rounds"] = serde_json::json!(c.rounds);
                }
                j
            }).collect::<Vec<_>>(),
            "dropped": report.dropped.iter().map(|d| serde_json::json!({"move": d.label, "reason": d.reason})).collect::<Vec<_>>(),
            "cap_note": report.cap_note,
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
                    "pool": if self.params.pool == PoolSet::Meta { "meta" } else { "wide" },
                    "pool_lists": self.core.listed,
                    "tool_rule": self.params.tools,
                    "noeffect": self.params.noeffect,
                    "z_attack": self.params.z_attack,
                    "z_skip": self.params.z_skip,
                    "max_rounds": self.params.max_rounds,
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

    /// The pilot with the meta pool of Oct 2 (`_poolmeta`).
    fn meta_pilot() -> PlayoutPlayer {
        let (deck_a, deck_b) = crate::test_support::load_test_decks();
        PlayoutPlayer::with_extra_lists(deck_a, deck_b, PlayoutParams { pool: PoolSet::Meta, ..PlayoutParams::new(3) }, Vec::new())
    }

    /// The meta pool loads 8 lists: each research/X holds the same cards and Energy as t-X.
    #[test]
    fn the_pool_holds_8_lists_once_duplicates_are_removed() {
        let p = meta_pilot();
        assert_eq!((p.core.pool.len(), p.core.meta, p.core.listed), (8, 8, 8));
        assert!(p.core.pool.iter().all(|(name, _)| name.starts_with("t-")));
        assert!(p.knowledge_label().contains("8 meta lists"), "{}", p.knowledge_label());
        // The wide pool (round 4): the same 8 first, then the 27 others, none a duplicate.
        let w = pilot();
        assert_eq!((w.core.meta, w.core.listed, w.core.pool.len()), (8, 35, 35));
        assert!(w.knowledge_label().contains("the wide pool's 35 lists (8 meta lists and 27 more)"), "{}", w.knowledge_label());
    }

    /// The Energy Zone rules (the meta pool): with Water showing, only Water lists are consistent (t-suicune alone).
    #[test]
    fn a_list_must_hold_the_energy_its_zone_shows() {
        let p = meta_pilot();
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

    /// The zone filters first, then the seen cards (round 3, Astra's review). Psychic showing and a seen Swablu leave
    /// t-altaria among the consistent lists. With a Metal zone the wide pool's Mega Scizor ex list is consistent while
    /// nothing is seen; once a card it doesn't hold is seen (Bulbasaur), the list is inferred (round 4), never borrowed
    /// whole with contradictory Energy, and its Energy is Metal only.
    #[test]
    fn the_zone_filters_first_then_the_seen_cards() {
        let p = pilot();
        let swablu = get_card_by_enum(CardId::B1196Swablu);
        let (deck, label) = p.core.sample_list(&[swablu.clone()], &[EnergyType::Psychic], &mut StdRng::seed_from_u64(1));
        assert!(label.contains("consistent)") && deck.energy_types == vec![EnergyType::Psychic], "{label}");
        assert!(deck.cards.contains(&swablu) && deck.cards.iter().all(|c| !c.is_unknown()));
        let (_, label) = p.core.sample_list(&[], &[EnergyType::Metal], &mut StdRng::seed_from_u64(1));
        assert_eq!(label, "g-mega_scizor_revavroom (1 of 1 consistent)");
        let bulbasaur = get_card_by_enum(CardId::A1001Bulbasaur);
        for seed in 0..20 {
            let (deck, label) = p.core.sample_list(&[bulbasaur.clone()], &[EnergyType::Metal], &mut StdRng::seed_from_u64(seed));
            assert!(label.starts_with("inferred from"), "seed {seed}: {label}");
            assert_eq!(deck.energy_types, vec![EnergyType::Metal], "{label}");
            assert!(deck.cards.contains(&bulbasaur) && deck.cards.iter().all(|c| !c.is_unknown()), "{label}: {:?}", deck.cards);
        }
    }

    /// Astra's case, round 4: Swablu seen with a Water Energy Zone. No pooled list holds both (the Swablu lists play
    /// Psychic). The opponent's list is inferred from the most similar lists that cover Water: 20 named cards that can
    /// be played, the seen Swablu among them, its own evolution line, every other card from a Water list, Energy Water
    /// only, never Psychic.
    #[test]
    fn swablu_with_a_water_zone_is_never_modelled_as_a_psychic_list() {
        let p = pilot();
        let swablu = get_card_by_enum(CardId::B1196Swablu);
        let water: Vec<&Deck> = p.core.pool.iter().map(|(_, d)| d).filter(|d| d.energy_types.contains(&EnergyType::Water)).collect();
        assert!(!water.is_empty());
        for seed in 0..20 {
            let (deck, label) = p.core.sample_list(&[swablu.clone()], &[EnergyType::Water], &mut StdRng::seed_from_u64(seed));
            assert!(label.starts_with("inferred from"), "seed {seed}: {label}");
            assert_eq!(deck.energy_types, vec![EnergyType::Water], "seed {seed}: {label}");
            assert_eq!(deck.cards.len(), DECK_SIZE);
            assert!(deck.cards.iter().all(|c| !c.is_unknown()), "seed {seed}: placeholders {:?}", deck.cards);
            assert_eq!(deck.cards.iter().filter(|c| **c == swablu).count(), 1);
            let line = p.core.seen_evolution_lines(&[swablu.clone()]);
            assert!(!line.is_empty() && line.iter().all(|c| deck.cards.contains(c)), "seed {seed}: Swablu's line {line:?}");
            for card in deck.cards.iter().filter(|c| **c != swablu && !line.contains(c)) {
                assert!(water.iter().any(|d| d.cards.contains(card)), "seed {seed}: {card:?} is in no Water list");
            }
        }
    }

    /// The same through a sampled world and the play-outs: the opponent's Swablu in play and Water in their zone. Every
    /// hidden card of theirs is a real card of an inferred Water list (no placeholder), their Energy is Water only, and
    /// the play-outs run on that world without a failure.
    #[test]
    fn an_unfamiliar_opponent_is_inferred_with_playable_cards() {
        use crate::models::PlayedCard;
        use crate::observation::RevealedKnowledge;
        use crate::state::EnergyZone;
        let mut game = crate::test_support::get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::B1196Swablu)],
        );
        let mut state = game.get_state_clone();
        state.move_generation_stack.clear();
        state.energy_zone[1] = EnergyZone { current: Some(EnergyType::Water), next: Some(EnergyType::Water) };
        // Player 0 has a Grass Energy to attach, so the decision has alternatives.
        state.energy_zone[0] = EnergyZone { current: Some(EnergyType::Grass), next: Some(EnergyType::Grass) };
        game.set_state(state);
        let state = game.get_state_clone();
        assert!(!state.hands[1].is_empty() && !state.decks[1].cards.is_empty(), "the opponent holds hidden cards");
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let mut p = PlayoutPlayer::with_extra_lists(
            crate::test_support::load_test_decks().0,
            crate::test_support::load_test_decks().1,
            PlayoutParams { rollouts: 4, cap: 4, ..PlayoutParams::new(3) },
            Vec::new(),
        );
        for seed in 0..5 {
            let (world, _, name) = p.core.sample_state(&observation, &mut StdRng::seed_from_u64(seed));
            assert!(name.starts_with("inferred from"), "{name}");
            assert_eq!(world.decks[1].energy_types, vec![EnergyType::Water]);
            assert!(world.hands[1].iter().chain(world.decks[1].cards.iter()).all(|c| !c.is_unknown()), "{:?}", world.hands[1]);
            assert_eq!(world.hands[1].len(), state.hands[1].len());
        }
        let actions = state.generate_possible_actions().1;
        let distinct: BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
        assert!(distinct.len() >= 2, "the position offers alternatives: {distinct:?}");
        let report = p.evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
        assert_eq!((report.rounds, report.failed_rounds), (4, 0), "{}", report.reason);
        assert!(report.lists.keys().all(|k| k.starts_with("inferred from")), "{:?}", report.lists);
    }

    /// A km3 game from `seed` between two pool lists, stopped at the first battle position (turn 3 or later) where player 0
    /// decides among two or more distinct moves.
    fn pool_midgame(a: &str, b: &str, seed: u64) -> State {
        let deck = |n: &str| Deck::from_file(&format!("../decks/screen/opponents/{n}.txt")).unwrap();
        let km3 = || PlayerCode::KM { max_depth: 3 };
        let mut game = Game::new(create_players(deck(a), deck(b), vec![km3(), km3()]), seed);
        loop {
            assert!(!game.is_game_over(), "seed {seed}: the game ended before a position came");
            let state = game.get_state_clone();
            let (actor, actions) = state.generate_possible_actions();
            let distinct: BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
            if actor == 0 && state.turn_count >= 3 && state.current_player == 0 && distinct.len() >= 2 {
                return state;
            }
            game.play_tick();
        }
    }

    /// One play-out with km3 on both sides, counting the opponent's attacks and evolutions (every card added under one of
    /// their Pokémon, by Evolve or by Rare Candy).
    fn opponent_activity(world: &State, list: &Deck, deck: &Deck, me: usize, action: &Action, seed: u64) -> (usize, usize) {
        let code = PlayerCode::KM { max_depth: 3 };
        let (d0, d1) = if me == 0 { (deck.clone(), list.clone()) } else { (list.clone(), deck.clone()) };
        let mut game = Game::from_state(world.clone(), create_players(d0, d1, vec![code.clone(), code]), seed);
        game.apply_action(action);
        let opponent = 1 - me;
        let behind = |s: &State| s.in_play_pokemon[opponent].iter().flatten().map(|p| p.cards_behind.len()).sum::<usize>();
        let (mut attacks, mut evolutions, mut ticks) = (0, 0, 0);
        while !game.is_game_over() && ticks < 4000 {
            let before = behind(&game.get_state_clone());
            let played = game.play_tick();
            if played.actor == opponent && matches!(played.action, crate::actions::SimpleAction::Attack(_)) {
                attacks += 1;
            }
            evolutions += behind(&game.get_state_clone()).saturating_sub(before);
            ticks += 1;
        }
        (attacks, evolutions)
    }

    /// Round 4's test that an inferred opponent plays. t-suicune (the pilot) against t-blaziken (Torchic, Mega Blaziken ex
    /// by Rare Candy). Over the same 12 sampled worlds and seeds, the opponent's attacks and evolutions in the play-outs:
    /// - pooled: the opponent's list is in the pool (REALISTIC draws the Blaziken lists);
    /// - inferred: every list consistent with the observation removed from the pool, so the list must be inferred from the
    ///   most similar others (the Fire lists);
    /// - filler: round 3's placeholders (the seen cards, the rest unknown cards, the zone's Energy).
    /// The inferred opponent attacks and evolves at least half as often as the pooled one, and evolves; filler doesn't.
    #[test]
    fn an_inferred_opponent_attacks_and_evolves_like_a_pooled_one() {
        use crate::observation::RevealedKnowledge;
        let state = pool_midgame("t-suicune", "t-blaziken", 3);
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let deck = Deck::from_file("../decks/screen/opponents/t-suicune.txt").unwrap();
        let opponent = Deck::from_file("../decks/screen/opponents/t-blaziken.txt").unwrap();
        let pooled = PlayoutPlayer::with_extra_lists(deck.clone(), opponent.clone(), PlayoutParams::new(3), Vec::new());
        let mut inferred = PlayoutPlayer::with_extra_lists(deck.clone(), opponent, PlayoutParams::new(3), Vec::new());
        let (seen, zone) = (Core::seen_opponent_cards(&observation), Core::zone_types(&observation));
        assert!(!seen.is_empty(), "the opponent has shown cards");
        let consistent = pooled.core.consistent_lists(&seen, &zone);
        assert!(!consistent.is_empty(), "the Blaziken lists are consistent");
        let keep: Vec<(String, Deck)> = (0..inferred.core.pool.len())
            .filter(|i| !consistent.contains(i))
            .map(|i| inferred.core.pool[i].clone())
            .collect();
        inferred.core.pool = keep;
        assert!(inferred.core.consistent_lists(&seen, &zone).is_empty());
        let action = state.generate_possible_actions().1[0].clone();
        let mut filler = seen.clone();
        filler.resize(DECK_SIZE, Card::Unknown);
        let filler = Deck { cards: filler, energy_types: zone.clone() };
        let (mut totals, n) = ([(0usize, 0usize); 3], 12u64);
        for j in 0..n {
            let (world, list, name) = pooled.core.sample_state(&observation, &mut StdRng::seed_from_u64(j));
            assert!(name.contains("consistent)"), "{name}");
            let (a, e) = opponent_activity(&world, &list, &deck, 0, &action, 100 + j);
            totals[0] = (totals[0].0 + a, totals[0].1 + e);
            let (world, list, name) = inferred.core.sample_state(&observation, &mut StdRng::seed_from_u64(j));
            assert!(name.starts_with("inferred from"), "{name}");
            let (a, e) = opponent_activity(&world, &list, &deck, 0, &action, 100 + j);
            totals[1] = (totals[1].0 + a, totals[1].1 + e);
            let world = observation.search_state_with_opponent_list(&mut StdRng::seed_from_u64(j), &filler);
            let (a, e) = opponent_activity(&world, &filler, &deck, 0, &action, 100 + j);
            totals[2] = (totals[2].0 + a, totals[2].1 + e);
        }
        let [(pa, pe), (ia, ie), (fa, fe)] = totals;
        eprintln!("opponent attacks / evolutions over {n} play-outs: pooled {pa} / {pe}, inferred {ia} / {ie}, filler {fa} / {fe}");
        assert!(pa > 0 && pe > 0, "the pooled opponent attacks and evolves: {pa} / {pe}");
        assert!(2 * ia >= pa, "inferred attacks {ia} against pooled {pa}");
        assert!(ie > 0 && 2 * ie >= pe, "inferred evolutions {ie} against pooled {pe}");
        assert!(fe < ie, "filler evolves less than an inferred list: {fe} against {ie}");
    }

    /// The opponent's known deck-top cards count as seen, and a top card also listed as somewhere in their deck counts once.
    #[test]
    fn known_deck_top_cards_count_as_seen_once() {
        use crate::models::PlayedCard;
        use crate::observation::RevealedKnowledge;
        let game = crate::test_support::get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::B1196Swablu)],
        );
        let state = game.get_state_clone();
        let sabrina = get_card_by_enum(CardId::A1225Sabrina);
        let bulbasaur = get_card_by_enum(CardId::A1001Bulbasaur);
        let revealed = RevealedKnowledge {
            deck_top: [Vec::new(), vec![sabrina.clone()]],
            opponent_hand: Vec::new(),
            opponent_deck_membership: vec![sabrina.clone(), bulbasaur.clone()],
        };
        let observation = PlayerObservation::from_state(&state, 0, &revealed);
        let seen = Core::seen_opponent_cards(&observation);
        assert_eq!(seen.iter().filter(|c| **c == sabrina).count(), 1, "{seen:?}");
        assert_eq!(seen.iter().filter(|c| **c == bulbasaur).count(), 1, "{seen:?}");
        assert!(seen.iter().any(|c| c.get_name() == "Swablu"), "{seen:?}");
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
