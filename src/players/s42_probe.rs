//! §42 — pilot telemetry for diagnosing `x3`'s regression.
//!
//! §40 measured that handing the CHALLENGER the opponent-turn ply made it play **6.63 pt worse**
//! (`x3,e3` = 61.71 vs `e3,e3` = 68.34), with the draw rate rising 1.50% -> 7.00% — the `m`
//! bot's stalling signature. §40 could not say why. This module answers two questions with
//! counters rather than argument:
//!
//! 1. **Is `x3` actually more passive?** — a histogram of the actions each pilot CHOOSES.
//!    Attack/EndTurn are turn-ending; Retreat/UseAbility/Attach are not. A racing deck talked
//!    into passivity attacks less and retreats more per decision.
//!
//! 2. **Is the search comparing like with like?** — the structural suspicion. A root action
//!    that ENDS THE TURN (attacking) pushes the search across the turn boundary, where the
//!    opponent ply prices the reply as a hard `min` — the opponent's best punish. A root action
//!    that does NOT end the turn (retreating, using an ability) leaves the search on our own
//!    turn, so it bottoms out at `depth == 0` in the static value function **with no opponent
//!    reply priced at all**. If that is what is happening, `x3` is not a deeper search — it is
//!    a search that applies a punishment term to aggressive lines and exempts passive ones,
//!    which would make it play worse exactly as measured, and the fix is in how the opponent's
//!    turn is VALUED, not how deeply it is searched.
//!
//! The decisive statistic is `mixed_decisions` / `chose_unpriced_when_mixed`: among decisions
//! whose candidate list contained BOTH a priced (boundary-crossing) and an unpriced action,
//! how often did the bot take the unpriced one?

use std::collections::BTreeMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, OnceLock};

use crate::actions::SimpleAction;

/// Leaf accounting. Every terminal evaluation of the search lands in exactly one bucket.
///
/// * `LEAF_OWN_TURN` — depth ran out while it was still OUR turn. No opponent reply priced.
/// * `LEAF_BOUNDARY_UNPRICED` — the turn passed but the opponent budget was spent (or zero),
///   so the reply was again not priced.
/// * `LEAF_AFTER_OPP_PLY` — reached after the opponent ply actually searched a reply.
/// * `LEAF_TURN_PASSED_DEPTH0` — **the sharp one.** Our turn ENDED, opponent budget was still
///   available, and the ply nonetheless did not fire because the depth check is evaluated
///   before the turn-boundary check. A line that ends the turn late in the search is therefore
///   exempt from the punishment a line that ends it early receives.
pub static LEAF_OWN_TURN: AtomicUsize = AtomicUsize::new(0);
pub static LEAF_BOUNDARY_UNPRICED: AtomicUsize = AtomicUsize::new(0);
pub static LEAF_AFTER_OPP_PLY: AtomicUsize = AtomicUsize::new(0);
pub static LEAF_TURN_PASSED_DEPTH0: AtomicUsize = AtomicUsize::new(0);

#[derive(Default, Debug, Clone)]
pub struct PilotStats {
    /// actor -> action kind -> times CHOSEN at the root.
    pub chosen: BTreeMap<usize, BTreeMap<String, usize>>,
    /// actor -> number of root decisions made.
    pub decisions: BTreeMap<usize, usize>,
    /// actor -> decisions where the candidate list held both priced and unpriced actions.
    pub mixed_decisions: BTreeMap<usize, usize>,
    /// actor -> of those, how many times the UNPRICED (turn-preserving) action won.
    pub chose_unpriced_when_mixed: BTreeMap<usize, usize>,
    /// actor -> total candidate actions offered, and how many of them were priced.
    pub candidates: BTreeMap<usize, usize>,
    pub candidates_priced: BTreeMap<usize, usize>,
}

fn stats() -> &'static Mutex<PilotStats> {
    static S: OnceLock<Mutex<PilotStats>> = OnceLock::new();
    S.get_or_init(|| Mutex::new(PilotStats::default()))
}

/// Coarse, stable label for an action. Turn-ending kinds are marked so the reader does not
/// have to know Pocket's rules to interpret the histogram.
pub fn action_kind(action: &SimpleAction) -> &'static str {
    match action {
        SimpleAction::Attack(_) => "Attack*",
        SimpleAction::EndTurn => "EndTurn*",
        SimpleAction::Retreat(_) => "Retreat",
        SimpleAction::UseAbility { .. } => "UseAbility",
        SimpleAction::Attach { .. } => "Attach",
        SimpleAction::Play { .. } => "PlayTrainer",
        SimpleAction::Place(..) => "Place",
        SimpleAction::Evolve { .. } => "Evolve",
        SimpleAction::AttachTool { .. } => "AttachTool",
        SimpleAction::DrawCard { .. } => "DrawCard",
        _ => "Other",
    }
}

/// Record one root decision. `priced` marks, per candidate, whether evaluating it caused the
/// search to cross the turn boundary into the opponent ply at least once.
pub fn record_decision(actor: usize, chosen: &SimpleAction, priced: &[bool], best_idx: usize) {
    let mut s = stats().lock().unwrap();
    *s.decisions.entry(actor).or_default() += 1;
    *s.chosen
        .entry(actor)
        .or_default()
        .entry(action_kind(chosen).to_string())
        .or_default() += 1;

    let n_priced = priced.iter().filter(|p| **p).count();
    *s.candidates.entry(actor).or_default() += priced.len();
    *s.candidates_priced.entry(actor).or_default() += n_priced;

    if n_priced > 0 && n_priced < priced.len() {
        *s.mixed_decisions.entry(actor).or_default() += 1;
        if !priced[best_idx] {
            *s.chose_unpriced_when_mixed.entry(actor).or_default() += 1;
        }
    }
}

/// Read and clear everything, so each tier is measured in isolation.
pub fn take_pilot_stats() -> (PilotStats, [usize; 4]) {
    let mut s = stats().lock().unwrap();
    let out = s.clone();
    *s = PilotStats::default();
    (
        out,
        [
            LEAF_OWN_TURN.swap(0, Ordering::Relaxed),
            LEAF_BOUNDARY_UNPRICED.swap(0, Ordering::Relaxed),
            LEAF_AFTER_OPP_PLY.swap(0, Ordering::Relaxed),
            LEAF_TURN_PASSED_DEPTH0.swap(0, Ordering::Relaxed),
        ],
    )
}
