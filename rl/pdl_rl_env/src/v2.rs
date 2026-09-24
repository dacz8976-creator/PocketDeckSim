//! Encoding v2.1 (add-on 0.5.0). v2 in 0.4.0 reused "after" numbers through a shortcut that
//! Astra's review showed could go stale; v2.1 recomputes them. Consequence and threat features,
//! computed the way the engine's own search player (k3) looks ahead. Everything here starts from `PlayerObservation::search_state`
//! (opponent's hand and deck are Unknown cards; our own deck is one sampled ordering of the
//! multiset we know) and only runs the engine's exact forecasts, refusing any action that
//! `hidden_continuation_reason` says would read hidden information. A refused or failed
//! forecast gives zeros with its "priced" flag at 0; nothing is guessed from the real State.
use std::cell::Cell;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Once;

use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::models::Card;
use deckgym::observation::{hidden_continuation_reason, PlayerObservation};
use deckgym::state::GameOutcome;
use deckgym::State;
use rand::rngs::StdRng;
use rand::SeedableRng;

/// Per-action consequence features (v2.1).
pub const A2: usize = 16;
/// Per-action consequence features (v2.2): the "certain" flag is replaced by two numbers about
/// losing the Active — how many Pokemon I'd have in play after the move, and whether losing the
/// Active right then would lose me the game (no bench, or that knockout gives them their third point).
pub const A2_V22: usize = 17;
/// Per-observation threat scalars (tool-identity blocks come on top, 2 x n_cards).
pub const O2: usize = 9;

const CAP_ACTION: usize = 8;
const CAP_ENDTURN: usize = 4;
const CAP_ATTACK: usize = 8;
const CAP_CHOICE: usize = 4;
const SEARCH_SEED: u64 = 0x5044_4c32_7632_0001;
const PROJECT_SEED: u64 = 0x5044_4c32_7632_0002;

thread_local! {
    static QUIET: Cell<bool> = const { Cell::new(false) };
    pub static STATS: Cell<(u64, u64, u64)> = const { Cell::new((0, 0, 0)) }; // forecasts, refused, panics
    static NEW_RULE_FRAME_SEEN: Cell<bool> = const { Cell::new(false) };
}
static HOOK: Once = Once::new();

fn install_quiet_hook() {
    HOOK.call_once(|| {
        let default = std::panic::take_hook();
        std::panic::set_hook(Box::new(move |info| {
            if !QUIET.with(|q| q.get()) || std::env::var_os("PDL_V2_LOUD").is_some() {
                default(info);
            }
        }));
    });
}

fn bump(i: usize) {
    STATS.with(|s| {
        let mut v = s.get();
        match i {
            0 => v.0 += 1,
            1 => v.1 += 1,
            _ => v.2 += 1,
        }
        s.set(v);
    });
}

/// Exact forecast of `a` on `s`, keeping the `cap` most likely branches (renormalized).
/// None = refused (hidden information) or the engine could not forecast it.
fn branches(s: &State, a: &Action, rng: &mut StdRng, cap: usize) -> Option<Vec<(f64, State)>> {
    if hidden_continuation_reason(s, a).is_some() {
        bump(1);
        return None;
    }
    bump(0);
    QUIET.with(|q| q.set(true));
    let r = catch_unwind(AssertUnwindSafe(|| {
        let outcomes = try_forecast_action(s, a).ok()?;
        let (probs, muts) = outcomes.into_branches();
        let mut order: Vec<usize> = (0..probs.len()).collect();
        order.sort_by(|&i, &j| probs[j].partial_cmp(&probs[i]).unwrap_or(std::cmp::Ordering::Equal).then(i.cmp(&j)));
        order.truncate(cap);
        let total: f64 = order.iter().map(|&i| probs[i]).sum();
        if !(total > 0.0) {
            return None;
        }
        let mut muts: Vec<Option<_>> = muts.into_iter().map(Some).collect();
        let mut out = Vec::with_capacity(order.len());
        for &i in &order {
            let mut c = s.clone();
            (muts[i].take().unwrap())(rng, &mut c, a);
            out.push((probs[i] / total, c));
        }
        Some(out)
    }));
    QUIET.with(|q| q.set(false));
    match r {
        Ok(v) => {
            if v.is_none() {
                bump(1);
            }
            v
        }
        Err(_) => {
            bump(2);
            None
        }
    }
}


/// Rules3 can defer points and victory below an attack follow-up or a Checkup frame.
/// Only public singleton continuations are deterministic. Genuine choices are unpriced
/// until the learner sees and makes that choice.
fn pending_new_rule_frame(s: &State) -> bool {
    let found = s.move_generation_stack.iter().any(|(_, choices)| choices.iter().any(|c| matches!(c,
        SimpleAction::ResolveAttackRetaliation { .. }
        | SimpleAction::ResolveKnockoutPoints { .. }
        | SimpleAction::ResolvePokemonCheckup
        | SimpleAction::FinishPokemonCheckup
        | SimpleAction::ResolveEndTurnEvolution { .. }
    )));
    if found {
        NEW_RULE_FRAME_SEEN.with(|seen| seen.set(true));
    }
    found
}

struct ForecastFailure {
    status: &'static str,
    reason: String,
    deferred: bool,
    forced_steps: usize,
}

/// Keep the original one-step result byte-for-byte when no new rule frame follows.
/// Once one does, play only public singleton actions, including a singleton switch
/// choice above the frame. Hidden continuations or a real choice leave the row unpriced.
fn settled_branches_status(
    s: &State, a: &Action, rng: &mut StdRng, cap: usize,
) -> Result<(Vec<(f64, State)>, usize, bool), ForecastFailure> {
    let base = branches(s, a, rng, cap).ok_or_else(|| ForecastFailure {
        status: if hidden_continuation_reason(s, a).is_some() { "hidden_refusal" } else { "forecast_failed" },
        reason: hidden_continuation_reason(s, a).unwrap_or("engine forecast unavailable").into(),
        deferred: false, forced_steps: 0,
    })?;
    if !base.iter().any(|(_, state)| pending_new_rule_frame(state)) {
        return Ok((base, 0, false));
    }
    let mut work: Vec<_> = base.into_iter().map(|(p, state)| (p, state, 0usize)).collect();
    let mut out = Vec::new();
    let mut max_steps = 0;
    while let Some((p, state, steps)) = work.pop() {
        if state.winner.is_some() || !pending_new_rule_frame(&state) {
            max_steps = max_steps.max(steps);
            out.push((p, state));
            continue;
        }
        if steps >= 16 || work.len() + out.len() >= 256 {
            return Err(ForecastFailure {
                status: "continuation_limit", reason: "forced continuation budget reached".into(),
                deferred: true, forced_steps: steps,
            });
        }
        let (_, legal) = state.generate_possible_actions();
        if legal.len() != 1 {
            return Err(ForecastFailure {
                status: "deferred_choice_unpriced",
                reason: format!("{} follow-up choices; a learner decision is required", legal.len()),
                deferred: true, forced_steps: steps,
            });
        }
        let follow = &legal[0];
        let more = branches(&state, follow, rng, cap).ok_or_else(|| ForecastFailure {
            status: if hidden_continuation_reason(&state, follow).is_some() {
                "continuation_hidden_refusal"
            } else {
                "continuation_forecast_failed"
            },
            reason: hidden_continuation_reason(&state, follow)
                .unwrap_or("engine continuation forecast unavailable").into(),
            deferred: true, forced_steps: steps,
        })?;
        for (q, next) in more {
            work.push((p * q, next, steps + 1));
        }
    }
    if out.is_empty() {
        return Err(ForecastFailure {
            status: "continuation_forecast_failed", reason: "no resolved branches".into(),
            deferred: true, forced_steps: max_steps,
        });
    }
    out.sort_by(|(pa, _), (pb, _)| pb.partial_cmp(pa).unwrap_or(std::cmp::Ordering::Equal));
    out.truncate(cap);
    let total: f64 = out.iter().map(|(p, _)| *p).sum();
    if !(total > 0.0) {
        return Err(ForecastFailure {
            status: "continuation_forecast_failed", reason: "zero branch mass".into(),
            deferred: true, forced_steps: max_steps,
        });
    }
    for (p, _) in &mut out { *p /= total; }
    Ok((out, max_steps, true))
}

fn settled_branches(s: &State, a: &Action, rng: &mut StdRng, cap: usize) -> Option<Vec<(f64, State)>> {
    settled_branches_status(s, a, rng, cap).ok().map(|(states, _, _)| states)
}

fn ko_points(card: &Card) -> f32 {
    match card {
        Card::Pokemon(pk) => {
            if pk.name.starts_with("Mega ") {
                3.0
            } else if pk.name.ends_with(" ex") {
                2.0
            } else {
                1.0
            }
        }
        _ => 0.0,
    }
}

fn side_hp(s: &State, p: usize) -> i64 {
    s.in_play_pokemon[p].iter().flatten().map(|pc| pc.get_remaining_hp() as i64).sum()
}

/// How dangerous one attacker's best option is against the defender's Active.
#[derive(Clone, Copy, Default, Debug)]
pub struct Threat {
    pub dmg: f64,
    pub p_ko: f64,
    pub p_win: f64,
    pub known: f64,
}

impl Threat {
    fn worse_than(&self, o: &Threat) -> bool {
        (self.p_win, self.p_ko, self.dmg) > (o.p_win, o.p_ko, o.dmg)
    }
    fn add(&mut self, p: f64, t: &Threat) {
        self.dmg += p * t.dmg;
        self.p_ko += p * t.p_ko;
        self.p_win += p * t.p_win;
        self.known += p * t.known;
    }
}

/// Best attack `attacker` can use right now (free play, their decision) against the
/// defender's Active; with `attach`, also after attaching this turn's zone Energy to the Active.
fn attack_threat(s: &State, attacker: usize, rng: &mut StdRng, attach: bool) -> Threat {
    let def = 1 - attacker;
    let (actor, acts) = s.generate_possible_actions();
    if actor != attacker || !s.move_generation_stack.is_empty() {
        return Threat::default();
    }
    let before = match &s.in_play_pokemon[def][0] {
        Some(pc) => (pc.card.get_id(), pc.get_remaining_hp() as f64),
        None => return Threat { known: 1.0, ..Default::default() },
    };
    let pts_before = s.points[attacker];
    let mut best = Threat { known: 1.0, ..Default::default() };
    let (mut n_att, mut n_priced) = (0, 0);
    for a in acts.iter().filter(|a| !a.is_stack && matches!(a.action, SimpleAction::Attack(_))) {
        n_att += 1;
        let Some(bs) = settled_branches(s, a, rng, CAP_ATTACK) else { continue };
        n_priced += 1;
        let mut t = Threat { known: 1.0, ..Default::default() };
        for (p, s2) in &bs {
            let win = matches!(s2.winner, Some(GameOutcome::Win(w)) if w == attacker);
            let after = s2.in_play_pokemon[def][0].as_ref();
            let ko = win || after.is_none() || s2.points[attacker] > pts_before;
            let dmg = if ko && after.map_or(true, |pc| pc.card.get_id() != before.0) {
                before.1
            } else {
                match after {
                    Some(pc) if pc.card.get_id() == before.0 => (before.1 - pc.get_remaining_hp() as f64).max(0.0),
                    _ => 0.0,
                }
            };
            t.dmg += p * dmg;
            t.p_ko += p * ko as u8 as f64;
            t.p_win += p * win as u8 as f64;
        }
        if t.worse_than(&best) {
            best = Threat { known: 1.0, ..t };
        }
    }
    if n_att > 0 && n_priced < n_att {
        best.known = n_priced as f64 / n_att as f64;
    }
    if attach {
        if let Some(a) = acts.iter().find(|a| {
            matches!(&a.action, SimpleAction::Attach { attachments, is_turn_energy: true }
                if attachments.len() == 1 && attachments[0].2 == 0)
        }) {
            if let Some(bs) = settled_branches(s, a, rng, 1) {
                let t = attack_threat(&bs[0].1, attacker, rng, false);
                if t.worse_than(&best) {
                    best = t;
                }
            }
        }
    }
    best
}

/// Takes a state where the turn has just passed (or a choice is pending) and walks it to the
/// opponent's free play, then measures the opponent's best attack. Pending choices are resolved
/// in the chooser's favour: the opponent picks the most dangerous option, we pick the safest.
/// The opponent's start-of-turn draw is taken count-only (an Unknown card), never forecast.
fn resolve_then_threat(s: &State, me: usize, rng: &mut StdRng, depth: u8) -> Threat {
    let op = 1 - me;
    if let Some(w) = &s.winner {
        return Threat { p_win: matches!(w, GameOutcome::Win(p) if *p == op) as u8 as f64, known: 1.0, ..Default::default() };
    }
    if depth > 3 {
        return Threat::default();
    }
    if let Some((chooser, choices)) = s.move_generation_stack.last() {
        let (chooser, choices) = (*chooser, choices.clone());
        if s.move_generation_stack.len() == 1 && chooser == op && choices == [SimpleAction::DrawCard { amount: 1 }] {
            let mut t = s.clone();
            t.move_generation_stack.pop();
            if t.hands[op].len() < 10 && t.decks[op].cards.pop().is_some() {
                t.hands[op].push(Card::Unknown);
            }
            return resolve_then_threat(&t, me, rng, depth + 1);
        }
        if choices.is_empty() {
            return Threat::default(); // a private choice we can't see
        }
        let mut out: Option<Threat> = None;
        for c in choices.iter().take(CAP_CHOICE) {
            let a = Action { actor: chooser, action: c.clone(), is_stack: true };
            let Some(bs) = settled_branches(s, &a, rng, CAP_ENDTURN) else { continue };
            let mut t = Threat::default();
            for (p, s2) in &bs {
                t.add(*p, &resolve_then_threat(s2, me, rng, depth + 1));
            }
            out = Some(match out {
                None => t,
                Some(o) => {
                    if (chooser == op) == t.worse_than(&o) { t } else { o }
                }
            });
        }
        return out.unwrap_or_default();
    }
    if s.current_player == op {
        return attack_threat(s, op, rng, true);
    }
    // Still our own turn: end it.
    let end = Action { actor: me, action: SimpleAction::EndTurn, is_stack: false };
    let Some(bs) = settled_branches(s, &end, rng, CAP_ENDTURN) else { return Threat::default() };
    let mut t = Threat::default();
    for (p, s2) in &bs {
        t.add(*p, &resolve_then_threat(s2, me, rng, depth + 1));
    }
    t
}

/// For projecting the opponent's turn our own hand and deck are not needed; replacing them with
/// Unknown cards (same counts) makes every later copy of the state much cheaper. It can only
/// remove information, and effects that would read those zones are then refused as unpriced.
fn strip_own(s: &mut State, me: usize) {
    let n = s.decks[me].cards.len();
    s.decks[me].cards = vec![Card::Unknown; n];
    let h = s.hands[me].len();
    s.hands[me] = vec![Card::Unknown; h];
}

fn free_play(s: &State, me: usize) -> bool {
    s.winner.is_none() && s.move_generation_stack.is_empty() && s.current_player == me
        && s.pending_attack_coin_choice.is_none() && s.pending_trainer_coin_choice.is_none()
        && s.pending_misty_target_choice.is_none()
}

fn state_key(s: &State) -> u64 {
    let mut h = std::collections::hash_map::DefaultHasher::new();
    s.hash(&mut h);
    h.finish()
}

/// The "after" numbers for a position, from `me`'s side: (my best attack still available this
/// turn, their best attack on their next turn). `s` must already be stripped (strip_own), and
/// the result is a pure function of it: a fresh fixed-seed RNG per call, memoised by the full
/// state hash (which includes turn effects, the Stadium and every flag), so two moves that
/// lead to the same position get the same numbers and nothing is reused across different ones.
fn project(s: &State, me: usize, memo: &mut HashMap<u64, (Threat, Threat)>) -> (Threat, Threat) {
    project_d(s, me, memo, 0)
}

fn project_d(s: &State, me: usize, memo: &mut HashMap<u64, (Threat, Threat)>, depth: u8) -> (Threat, Threat) {
    let key = state_key(s);
    if let Some(v) = memo.get(&key) {
        return *v;
    }
    let known = Threat { known: 1.0, ..Default::default() };
    let mut rng = StdRng::seed_from_u64(PROJECT_SEED);
    let pending = s.move_generation_stack.last().cloned();
    let v = if s.winner.is_some() {
        (known, known)
    } else if s.turn_count == 0 || depth > 2 {
        (Threat::default(), Threat::default()) // setup (opponent's board face down), or too deep
    } else if free_play(s, me) {
        (attack_threat(s, me, &mut rng, true), resolve_then_threat(s, me, &mut rng, 0))
    } else if pending.as_ref().is_some_and(|(c, _)| *c == me) {
        (Threat::default(), Threat::default()) // our own follow-up choice: not projected
    } else if let Some((c, choices)) = pending.filter(|(_, ch)| s.current_player == me && !ch.is_empty()) {
        // The opponent chooses in the middle of our turn (e.g. which Pokémon Sabrina brings up):
        // they pick the option that leaves our attack weakest; report the threat for that option.
        let mut best: Option<(Threat, Threat)> = None;
        for ch in choices.iter().take(CAP_CHOICE) {
            let a = Action { actor: c, action: ch.clone(), is_stack: true };
            let Some(bs) = settled_branches(s, &a, &mut rng, CAP_ENDTURN) else { continue };
            let (mut pot, mut thr) = (Threat::default(), Threat::default());
            for (p, s2) in &bs {
                let (p2, t2) = project_d(s2, me, memo, depth + 1);
                pot.add(*p, &p2);
                thr.add(*p, &t2);
            }
            best = Some(match best {
                Some((bp, bt)) if !bp.worse_than(&pot) => (bp, bt),
                _ => (pot, thr),
            });
        }
        best.unwrap_or_default()
    } else {
        (known, resolve_then_threat(s, me, &mut rng, 0))
    };
    memo.insert(key, v);
    v
}

/// (obs extra scalars, per-action rows) for `obs.actor`. Action rows are only meaningful when
/// the observer is the one deciding; pass an empty slice otherwise.
pub fn features(obs: &PlayerObservation, actions: &[Action], v22: bool) -> ([f32; O2], Vec<[f32; A2_V22]>, bool) {
    install_quiet_hook();
    NEW_RULE_FRAME_SEEN.with(|seen| seen.set(false));
    let me = obs.actor;
    let op = 1 - me;
    let mut rng = StdRng::seed_from_u64(SEARCH_SEED);
    let s = obs.search_state(&mut rng);
    let vis = obs.visible_state();
    let mut o = [0f32; O2];
    let mut memo = HashMap::new();
    let fp = free_play(&s, me) && s.turn_count > 0;
    let (pot, thr) = {
        let mut light = s.clone();
        strip_own(&mut light, me);
        project(&light, me, &mut memo)
    };
    o[0] = (pot.dmg / 100.0).min(3.0) as f32;
    o[1] = pot.p_ko as f32;
    o[2] = pot.p_win as f32;
    o[3] = (thr.dmg / 100.0).min(3.0) as f32;
    o[4] = thr.p_ko as f32;
    o[5] = thr.p_win as f32;
    o[6] = if fp { thr.known.min(pot.known) as f32 } else { 0.0 };
    o[7] = vis.in_play_pokemon[me][0].as_ref().map_or(0.0, |pc| ko_points(&pc.card) / 3.0);
    o[8] = vis.in_play_pokemon[op][0].as_ref().map_or(0.0, |pc| ko_points(&pc.card) / 3.0);

    let rows = actions
        .iter()
        .map(|a| {
            let mut r = [0f32; A2_V22];
            // v2.1 keeps [.., 13 = "certain", 14 = asleep, 15 = poisoned]; v2.2 uses
            // [.., 13 = my Pokemon in play after this move, 14 = losing the Active now loses, 15/16 = asleep/poisoned].
            let (i_sleep, i_poison) = if v22 { (15, 16) } else { (14, 15) };
            // A fresh fixed-seed RNG per move: each row depends only on the position and that move.
            let mut arng = StdRng::seed_from_u64(SEARCH_SEED ^ 0x0a0a);
            let Some(mut bs) = settled_branches(&s, a, &mut arng, CAP_ACTION) else { return r };
            r[0] = 1.0;
            let (hp_me, hp_op) = (side_hp(&s, me), side_hp(&s, op));
            let mut known = 0.0;
            for (p, s2) in bs.iter_mut() {
                let p = *p;
                let pf = p as f32;
                r[1] += pf * s2.points[me].saturating_sub(s.points[me]) as f32 / 3.0;
                r[2] += pf * s2.points[op].saturating_sub(s.points[op]) as f32 / 3.0;
                r[3] += pf * matches!(s2.winner, Some(GameOutcome::Win(w)) if w == me) as u8 as f32;
                r[4] += pf * matches!(s2.winner, Some(GameOutcome::Win(w)) if w == op) as u8 as f32;
                r[5] += pf * ((hp_op - side_hp(s2, op)).max(0) as f32 / 100.0).min(3.0);
                r[6] += pf * ((hp_me - side_hp(s2, me)).max(0) as f32 / 100.0).min(3.0);
                let next_op = s2.winner.is_none()
                    && s2.move_generation_stack.last().map_or(s2.current_player, |(c, _)| *c) == op;
                r[7] += pf * next_op as u8 as f32;
                if let Some(pc) = &s2.in_play_pokemon[op][0] {
                    r[i_sleep] += pf * (pc.is_asleep() || pc.is_paralyzed()) as u8 as f32;
                    r[i_poison] += pf * (pc.is_poisoned() || pc.is_burned()) as u8 as f32;
                }
                if v22 {
                    // Exact, from what we can see: my Pokemon in play after this move, and whether
                    // losing the Active right then ends the game (nothing to promote, or their third point).
                    let in_play = s2.in_play_pokemon[me].iter().flatten().count();
                    r[13] += pf * in_play as f32 / 4.0;
                    let lost_if_ko = s2.winner.is_none()
                        && match &s2.in_play_pokemon[me][0] {
                            Some(pc) => in_play <= 1 || s2.points[op] as f32 + ko_points(&pc.card) >= 3.0,
                            None => in_play == 0,
                        };
                    r[14] += pf * lost_if_ko as u8 as f32;
                }
                // What the board looks like after this action: our remaining attack this turn,
                // and the opponent's best attack on their next turn (always recomputed).
                strip_own(s2, me);
                let (pot2, thr2) = project(s2, me, &mut memo);
                r[8] += pf * (pot2.dmg / 100.0).min(3.0) as f32;
                r[9] += pf * pot2.p_ko as f32;
                r[10] += pf * (thr2.dmg / 100.0).min(3.0) as f32;
                r[11] += pf * thr2.p_ko as f32;
                r[12] += pf * thr2.p_win as f32;
                known += p * thr2.known;
            }
            if !v22 {
                r[13] = known as f32;
            }
            r
        })
        .collect();
    (o, rows, NEW_RULE_FRAME_SEEN.with(|seen| seen.get()))
}

/// Analysis only: explain why each offered action is priced or left unpriced.
/// Uses the same public search state and fixed per-action seed as the feature rows.
pub fn diagnostics(obs: &PlayerObservation, actions: &[Action], lookahead_seen: bool) -> Vec<String> {
    let mut rng = StdRng::seed_from_u64(SEARCH_SEED);
    let s = obs.search_state(&mut rng);
    actions.iter().map(|a| {
        let mut arng = StdRng::seed_from_u64(SEARCH_SEED ^ 0x0a0a);
        match settled_branches_status(&s, a, &mut arng, CAP_ACTION) {
            Ok((_, steps, deferred)) => serde_json::json!({
                "status": "priced", "reason": "", "new_rule_frame_seen": deferred,
                "forced_steps": steps, "lookahead_new_rule_frame_seen": lookahead_seen,
            }).to_string(),
            Err(e) => serde_json::json!({
                "status": e.status, "reason": e.reason, "new_rule_frame_seen": e.deferred,
                "forced_steps": e.forced_steps, "lookahead_new_rule_frame_seen": lookahead_seen,
            }).to_string(),
        }
    }).collect()
}
