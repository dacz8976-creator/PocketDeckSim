//! The plan continuation for the play-outs (Oct 5; Fable via Dustin; rl/results/playout_continuation_2026-10-05/README.md):
//! a diagnostic option of the play-out pilot, never used by kx<N>'s own decisions. For the pilot's side, the next K own
//! turns follow a scripted plan (a few rules given per position), then km<N> takes over; the opponent is km<N> throughout.
//!
//! A plan's rules, for each own turn k = 0..K-1 (turn 0 is the decision's own turn, and its steps start with the plan's
//! first move):
//! - `steps`, in order, at the level of intent (a named Pokémon, never an action index, since draws and coins differ
//!   between sampled worlds): the turn's Energy to a Pokémon, an effect's extra Energy to one (Turbo Shark's), evolve,
//!   bench, play a Trainer, choose a target (Misty's, a Tool's), retreat to a Pokémon, attack;
//! - at each of the pilot's decisions in the turn, the first pending step that is legal is played. A step not legal yet
//!   stays pending (a draw may bring its card). When none is, km<N> decides, among the moves the turn's `avoid` (Trainers
//!   by name) and `keep_active` (no retreat) leave (all moves if they leave none), so km<N> fills in what the plan doesn't
//!   name (a draw, a heal). The plan's attack is played when km<N> would end the turn (by an attack or End Turn);
//! - a move made without asking the plan (the first move itself; a forced move, the only legal one, which `Game` makes
//!   without asking a player) counts as the first pending step it matches. A step still pending when its turn ends was
//!   skipped (km<N> decided in its place); one whose turn the game never reached is counted apart;
//! - `promote`: within the K turns, when the Active falls, the first Pokémon in play named in the list is promoted (the
//!   one with the most Energy if two share the name).
//! With K = 0 (or a plan with no turns) the pilot's side is km<N> itself, so the play-outs are km<N>'s, state for state.
//! A play-out also keeps a short log of the pilot's moves within the K turns (who made each: the first move, the plan,
//! km<N>, forced); a plan of K empty turns plays exactly as km<N> and so logs km<N>'s own continuation.
use std::cell::RefCell;
use std::rc::Rc;

use rand::rngs::StdRng;
use serde::{Deserialize, Serialize};

use crate::actions::{Action, SimpleAction};
use crate::observation::PlayerObservation;
use crate::players::Player;
use crate::{Deck, State};

/// Where a named Pokémon must be: anywhere, in the Active Spot, or on the Bench.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Spot {
    #[default]
    Any,
    Active,
    Bench,
}

impl Spot {
    fn admits(self, in_play_idx: usize) -> bool {
        match self {
            Spot::Any => true,
            Spot::Active => in_play_idx == 0,
            Spot::Bench => in_play_idx > 0,
        }
    }
}

/// One step of a plan, at the level of intent. Where a step names several Pokémon (`to`), the earlier name is preferred.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "do", rename_all = "snake_case", deny_unknown_fields)]
pub enum Step {
    /// The turn's Energy from the Energy Zone, to a Pokémon named in `to`.
    Energy {
        to: Vec<String>,
        #[serde(default)]
        at: Spot,
    },
    /// An Energy an effect attaches to a Pokémon of the player's choice (Turbo Shark's), not the turn's.
    ExtraEnergy {
        to: Vec<String>,
        #[serde(default)]
        at: Spot,
    },
    /// Evolve into the card named `into`, from a Pokémon named `from` if given.
    Evolve {
        into: String,
        #[serde(default)]
        from: Option<String>,
        #[serde(default)]
        at: Spot,
    },
    /// Put the Basic named `card` on the Bench.
    Bench { card: String },
    /// Play the Trainer named `card` (its target, for a Tool or Misty, is a `target` step).
    Play { card: String },
    /// The target of a card just played: a Tool's Pokémon, Misty's, a switch's.
    Target {
        to: Vec<String>,
        #[serde(default)]
        at: Spot,
    },
    /// Retreat the Active into a Benched Pokémon named in `to`.
    RetreatTo { to: Vec<String> },
    /// The attack named `title`.
    Attack { title: String },
}

impl Step {
    /// How well `action` carries out this step at `state` (0 best: the earlier name in `to`), or None if it doesn't.
    pub fn rank(&self, state: &State, me: usize, action: &Action) -> Option<usize> {
        if action.actor != me {
            return None;
        }
        let name = |idx: usize| state.in_play_pokemon[me].get(idx).and_then(|p| p.as_ref()).map(|p| p.get_name());
        let pick = |names: &[String], idx: usize, at: Spot| -> Option<usize> {
            if !at.admits(idx) {
                return None;
            }
            let n = name(idx)?;
            names.iter().position(|x| *x == n)
        };
        match (self, &action.action) {
            (Step::Energy { to, at }, SimpleAction::Attach { attachments, is_turn_energy: true })
            | (Step::ExtraEnergy { to, at }, SimpleAction::Attach { attachments, is_turn_energy: false })
                if attachments.len() == 1 =>
            {
                pick(to, attachments[0].2, *at)
            }
            (Step::Evolve { into, from, at }, SimpleAction::Evolve { evolution, in_play_idx, .. }) => {
                let from_ok = from.as_ref().map_or(true, |f| name(*in_play_idx).as_deref() == Some(f.as_str()));
                (evolution.get_name() == *into && from_ok && at.admits(*in_play_idx)).then_some(0)
            }
            (Step::Bench { card }, SimpleAction::Place(c, idx)) => (c.get_name() == *card && *idx > 0).then_some(0),
            (Step::Play { card }, SimpleAction::Play { trainer_card }) => (trainer_card.name == *card).then_some(0),
            (Step::Target { to, at }, SimpleAction::AttachTool { in_play_idx, .. })
            | (Step::Target { to, at }, SimpleAction::ChooseMistyTarget { in_play_idx }) => pick(to, *in_play_idx, *at),
            (Step::Target { to, at }, SimpleAction::Activate { player, in_play_idx })
            | (Step::Target { to, at }, SimpleAction::Promote { player, in_play_idx })
                if *player == me =>
            {
                pick(to, *in_play_idx, *at)
            }
            (Step::RetreatTo { to }, SimpleAction::Retreat(idx)) => pick(to, *idx, Spot::Bench),
            (Step::Attack { title }, SimpleAction::Attack(attack)) => (attack.title == *title).then_some(0),
            _ => None,
        }
    }

    /// Whether `action` carries out this step at `state`.
    pub fn matches(&self, state: &State, me: usize, action: &Action) -> bool {
        self.rank(state, me, action).is_some()
    }

    /// The legal action that best carries out this step (the best rank, then the first offered).
    pub fn best(&self, state: &State, me: usize, actions: &[Action]) -> Option<Action> {
        actions
            .iter()
            .filter_map(|a| self.rank(state, me, a).map(|r| (r, a)))
            .min_by_key(|(r, _)| *r)
            .map(|(_, a)| a.clone())
    }

    fn ends_turn(&self) -> bool {
        matches!(self, Step::Attack { .. })
    }
}

/// One own turn of a plan.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlanTurn {
    #[serde(default)]
    pub steps: Vec<Step>,
    /// Trainers (by name) km<N> may not play in this turn when it fills in.
    #[serde(default)]
    pub avoid: Vec<String>,
    /// km<N> may not retreat in this turn (a `retreat_to` step still may).
    #[serde(default)]
    pub keep_active: bool,
}

/// A plan: its own turns from the decision's on, and whom to promote when the Active falls within them.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Plan {
    #[serde(default)]
    pub turns: Vec<PlanTurn>,
    #[serde(default)]
    pub promote: Vec<String>,
}

/// What a plan did over play-outs: per plan turn and step, how many play-outs played it (`fired`), reached its turn
/// without playing it (`skipped`: km<N> decided in its place), or ended before its turn (`unreached`); and the pilot's
/// decisions in the window: made by the plan (steps and promotions), by km<N> filling in, and how often the plan's
/// attack replaced a different turn-ending move of km<N>'s.
#[derive(Debug, Clone, Default, PartialEq, Serialize)]
pub struct PlanTally {
    pub fired: Vec<Vec<usize>>,
    pub skipped: Vec<Vec<usize>>,
    pub unreached: Vec<Vec<usize>>,
    pub plan_moves: usize,
    pub promotions: usize,
    pub km_fills: usize,
    pub substituted: usize,
}

impl PlanTally {
    pub fn new(plan: &Plan, k: usize) -> Self {
        let zeros: Vec<Vec<usize>> = plan.turns.iter().take(k).map(|t| vec![0; t.steps.len()]).collect();
        PlanTally { fired: zeros.clone(), skipped: zeros.clone(), unreached: zeros, ..Default::default() }
    }

    pub fn add(&mut self, other: &PlanTally) {
        for (mine, theirs) in [(&mut self.fired, &other.fired), (&mut self.skipped, &other.skipped), (&mut self.unreached, &other.unreached)] {
            for (a, b) in mine.iter_mut().zip(theirs) {
                for (x, y) in a.iter_mut().zip(b) {
                    *x += y;
                }
            }
        }
        self.plan_moves += other.plan_moves;
        self.promotions += other.promotions;
        self.km_fills += other.km_fills;
        self.substituted += other.substituted;
    }
}

/// One play-out's progress through the plan, shared by the plan's player inside the game and the play-out loop.
#[derive(Debug)]
pub(crate) struct Progress {
    plan: Plan,
    /// The number of own turns the plan covers: K, at most the plan's turns.
    k: usize,
    me: usize,
    start: usize,
    /// Per plan turn, the steps not played yet.
    pending: Vec<Vec<usize>>,
    tally: PlanTally,
    /// The window is over (a state past its last turn was seen): nothing more to match.
    closed: bool,
    /// The pilot's moves within the window, in order: "t<turn> <who>: <move>".
    log: Vec<String>,
}

/// A move in a few words, with the names of the Pokémon it involves (read at `state`, before the move).
pub fn describe(state: &State, me: usize, action: &Action) -> String {
    let named = |player: usize, idx: usize| {
        let whose = if player == me { "" } else { "opponent's " };
        state.in_play_pokemon[player].get(idx).and_then(|p| p.as_ref()).map_or(format!("{whose}slot {idx}"), |p| {
            format!("{whose}{}{}", if idx == 0 { "Active " } else { "Benched " }, p.get_name())
        })
    };
    let name = |idx: usize| named(me, idx);
    match &action.action {
        SimpleAction::Attack(a) => format!("attack {}", a.title),
        SimpleAction::Play { trainer_card } => format!("play {}", trainer_card.name),
        SimpleAction::Attach { attachments, is_turn_energy } if attachments.len() == 1 => {
            let (n, energy, idx) = &attachments[0];
            let what = if *is_turn_energy { "the turn's" } else { "an extra" };
            format!("{what} {energy:?}{} to the {}", if *n > 1 { format!(" x{n}") } else { String::new() }, name(*idx))
        }
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("evolve the {} into {}", name(*in_play_idx), evolution.get_name()),
        SimpleAction::Place(card, _) => format!("bench {}", card.get_name()),
        SimpleAction::Retreat(idx) => format!("retreat into the {}", name(*idx)),
        SimpleAction::Promote { player, in_play_idx } => format!("promote the {}", named(*player, *in_play_idx)),
        SimpleAction::Activate { player, in_play_idx } => format!("switch in the {}", named(*player, *in_play_idx)),
        SimpleAction::AttachTool { in_play_idx, tool_card } => format!("{} on the {}", tool_card.get_name(), name(*in_play_idx)),
        SimpleAction::ChooseMistyTarget { in_play_idx } => format!("Misty's target: the {}", name(*in_play_idx)),
        SimpleAction::EndTurn => "end the turn".to_string(),
        other => format!("{other:?}").chars().take(80).collect(),
    }
}

impl Progress {
    pub(crate) fn new(plan: &Plan, k: usize, me: usize, start: usize) -> Self {
        let k = k.min(plan.turns.len());
        Progress {
            plan: plan.clone(),
            k,
            me,
            start,
            pending: plan.turns.iter().take(k).map(|t| (0..t.steps.len()).collect()).collect(),
            tally: PlanTally::new(plan, k),
            closed: k == 0,
            log: Vec::new(),
        }
    }

    /// Logs a move of the pilot's made within the window.
    pub(crate) fn note(&mut self, state: &State, action: &Action, who: &str) {
        if self.in_window(state) && action.actor == self.me {
            self.log.push(format!("t{} {who}: {}", state.turn_count, describe(state, self.me, action)));
        }
    }

    /// The window's log of the play-out.
    pub(crate) fn take_log(&mut self) -> Vec<String> {
        std::mem::take(&mut self.log)
    }

    fn in_window(&self, state: &State) -> bool {
        let t = state.turn_count as usize;
        self.k > 0 && t >= self.start && t < self.start + 2 * self.k
    }

    /// The plan turn of a state where the pilot is to move in its own turn within the window.
    fn own_turn(&self, state: &State) -> Option<usize> {
        (self.in_window(state) && state.current_player == self.me).then(|| (state.turn_count as usize - self.start) / 2)
    }

    /// A move made without asking the plan: it counts as the first pending step of its turn it matches.
    pub(crate) fn observe(&mut self, state: &State, action: &Action) {
        let Some(k) = self.own_turn(state) else { return };
        let steps = &self.plan.turns[k].steps;
        if let Some(pos) = self.pending[k].iter().position(|&s| steps[s].matches(state, self.me, action)) {
            let s = self.pending[k].remove(pos);
            self.tally.fired[k][s] += 1;
        }
    }

    /// Before a tick of the play-out: a forced move of the pilot's (the only legal one) is matched against the steps.
    pub(crate) fn before_tick(&mut self, state: &State) {
        if self.closed {
            return;
        }
        if state.turn_count as usize >= self.start + 2 * self.k {
            self.closed = true;
            return;
        }
        let (actor, actions) = state.generate_possible_actions();
        if actor == self.me && actions.len() == 1 {
            self.observe(state, &actions[0]);
            // Only a forced choice of the kinds a plan names is logged, not a draw, a coin's resolution or End Turn.
            if matches!(
                actions[0].action,
                SimpleAction::Attack(_)
                    | SimpleAction::Play { .. }
                    | SimpleAction::Attach { .. }
                    | SimpleAction::Evolve { .. }
                    | SimpleAction::Place(..)
                    | SimpleAction::Retreat(_)
                    | SimpleAction::Promote { .. }
                    | SimpleAction::Activate { .. }
                    | SimpleAction::AttachTool { .. }
                    | SimpleAction::ChooseMistyTarget { .. }
            ) {
                self.note(state, &actions[0], "forced");
            }
        }
    }

    /// The play-out's tally, once it has ended at `end`: the steps still pending were skipped if their turn came.
    pub(crate) fn finish(&mut self, end: &State) -> PlanTally {
        for k in 0..self.k {
            let reached = k == 0 || end.turn_count as usize >= self.start + 2 * k;
            for &s in &self.pending[k] {
                if reached {
                    self.tally.skipped[k][s] += 1;
                } else {
                    self.tally.unreached[k][s] += 1;
                }
            }
            self.pending[k].clear();
        }
        self.tally.clone()
    }
}

/// The pilot's side in a plan continuation: the plan within its K turns, km<N> everywhere else (and for K = 0 entirely).
#[derive(Debug)]
pub(crate) struct PlanPlayer {
    pub(crate) km: Box<dyn Player>,
    pub(crate) progress: Rc<RefCell<Progress>>,
}

impl PlanPlayer {
    /// The plan's move at this decision, if it has one; else the moves km<N> may choose among, and the plan turn.
    fn plan_move(&self, state: &State, actions: &[Action]) -> Result<Action, Option<(usize, Vec<Action>)>> {
        let mut p = self.progress.borrow_mut();
        if !p.in_window(state) {
            return Err(None);
        }
        let me = p.me;
        let all_promotions = actions.iter().all(|a| matches!(a.action, SimpleAction::Promote { .. }));
        if all_promotions && !p.plan.promote.is_empty() {
            let named = |a: &Action| match a.action {
                SimpleAction::Promote { player, in_play_idx } if player == me => {
                    let card = state.in_play_pokemon[me][in_play_idx].as_ref()?;
                    let rank = p.plan.promote.iter().position(|n| *n == card.get_name())?;
                    Some((rank, std::cmp::Reverse(card.attached_energy.len())))
                }
                _ => None,
            };
            let pick = actions.iter().filter(|a| named(a).is_some()).min_by_key(|a| named(a)).cloned();
            if let Some(a) = pick {
                p.tally.plan_moves += 1;
                p.tally.promotions += 1;
                return Ok(a);
            }
        }
        let Some(k) = p.own_turn(state) else { return Err(None) };
        for pos in 0..p.pending[k].len() {
            let s = p.pending[k][pos];
            let step = &p.plan.turns[k].steps[s];
            if step.ends_turn() {
                continue;
            }
            let found = step.best(state, me, actions);
            if let Some(a) = found {
                p.pending[k].remove(pos);
                p.tally.fired[k][s] += 1;
                p.tally.plan_moves += 1;
                return Ok(a);
            }
        }
        let rules = &p.plan.turns[k];
        let forbidden = |a: &Action| match &a.action {
            SimpleAction::Play { trainer_card } => rules.avoid.iter().any(|n| *n == trainer_card.name),
            SimpleAction::Retreat(_) => rules.keep_active,
            _ => false,
        };
        let allowed: Vec<Action> = actions.iter().filter(|a| !forbidden(a)).cloned().collect();
        Err(Some((k, if allowed.is_empty() { actions.to_vec() } else { allowed })))
    }

    /// km<N> chose `choice` at plan turn `k`: if it ends the turn and the plan's attack is pending and legal, the plan's
    /// attack instead. The move, and who made it.
    fn after_km(&self, state: &State, actions: &[Action], k: usize, choice: Action) -> (Action, &'static str) {
        let mut p = self.progress.borrow_mut();
        let me = p.me;
        if matches!(choice.action, SimpleAction::Attack(_) | SimpleAction::EndTurn) {
            for pos in 0..p.pending[k].len() {
                let s = p.pending[k][pos];
                let step = &p.plan.turns[k].steps[s];
                if !step.ends_turn() {
                    continue;
                }
                let found = step.best(state, me, actions);
                if let Some(a) = found {
                    p.pending[k].remove(pos);
                    p.tally.fired[k][s] += 1;
                    p.tally.plan_moves += 1;
                    if a != choice {
                        p.tally.substituted += 1;
                        return (a, "plan, for km3's end");
                    }
                    return (a, "plan");
                }
            }
        }
        p.tally.km_fills += 1;
        (choice, "km3")
    }
}

impl Player for PlanPlayer {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, possible_actions: &[Action]) -> Action {
        let state = observation.visible_state();
        let (action, who) = match self.plan_move(state, possible_actions) {
            Ok(a) => (a, "plan"),
            Err(None) => (self.km.decision_fn(rng, observation, possible_actions), "km3"),
            Err(Some((k, allowed))) => {
                let choice = self.km.decision_fn(rng, observation, &allowed);
                self.after_km(state, possible_actions, k, choice)
            }
        };
        self.progress.borrow_mut().note(state, &action, who);
        action
    }

    fn get_deck(&self) -> Deck {
        self.km.get_deck()
    }

    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        self.km.decide_omniscient(rng, state, possible_actions)
    }
}
