use log::{trace, LevelFilter};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::fmt::Debug;
use std::fmt::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::vec;

use crate::actions::{forecast_action, try_forecast_action, Action, SimpleAction};
use crate::{Deck, State};

use super::{
    public_reply::{PublicReplyAssessment, PublicReplyProvenance},
    Player,
};

// Type alias for value functions
// Takes a state and player index, returns a score
// Using Box<dyn Fn> to allow closures with captured variables
pub type ValueFunction = Box<dyn Fn(&State, usize) -> f64>;

struct DebugStateNode {
    acting_player: usize,
    children: Vec<DebugActionNode>,
    proba: f64,
    value: f64,
    win_distance: Option<usize>,
}

struct DebugActionNode {
    action: Action,
    children: Vec<DebugStateNode>,
    value: f64,
    unpriced_reason: Option<String>,
    // Distance in the already represented search tree, not a guarantee over
    // unmodeled randomness or hidden continuations. Used only on exact score ties.
    win_distance: Option<usize>,
}

fn chance_win_distance(children: &[DebugStateNode]) -> Option<usize> {
    let mut worst = None;
    for child in children.iter().filter(|child| child.proba > 0.0) {
        let distance = child.win_distance?;
        worst = Some(worst.map_or(distance, |prior: usize| prior.max(distance)));
    }
    worst.and_then(|distance| distance.checked_add(1))
}

fn choice_win_distance(
    children: &[DebugActionNode], value: f64, actor: usize, myself: usize,
) -> Option<usize> {
    if actor == myself {
        children.iter().filter(|child| child.value == value)
            .filter_map(|child| child.win_distance).min()
    } else {
        // Every represented opponent choice must still win for us. Never select
        // the opponent's helpful reply to certify a shorter line.
        children.iter().try_fold(None, |worst, child| {
            let distance = child.win_distance?;
            Some(Some(worst.map_or(distance, |prior: usize| prior.max(distance))))
        }).flatten()
    }
}

fn prefer_shorter_win(a: Option<usize>, b: Option<usize>) -> std::cmp::Ordering {
    match (a, b) {
        (Some(a), Some(b)) => b.cmp(&a),
        (Some(_), None) => std::cmp::Ordering::Greater,
        (None, Some(_)) => std::cmp::Ordering::Less,
        (None, None) => std::cmp::Ordering::Equal,
    }
}

/// §42. Which experimental modifications to the search are active. Bundled into one `Copy`
/// struct so a new variant costs a field rather than another parameter on five signatures.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct SearchFlags {
    /// See [`ExpectiMiniMaxPlayer::consistent_horizon`].
    pub consistent_horizon: bool,
    /// §42. Score the opponent's turn as an EXPECTATION over their public actions instead of
    /// a hard `min`.
    ///
    /// The `min` is textbook minimax, but it is being taken over a deliberately truncated
    /// action set: [`is_public_information_action`] admits attacking, retreating, using an
    /// Ability, drawing and attaching the turn's Energy, and rejects everything sourced from
    /// the hand. What survives the filter is dominated by "they attack me", so the `min` is
    /// not "the opponent's best reply" but "the opponent's most damaging reply, assumed
    /// always". A bot that charges every one of its own lines with the opponent's best attack
    /// will not race — it will retreat, which is what §42 measured `x3` doing.
    pub soft_opponent: bool,
}

pub struct ExpectiMiniMaxPlayer {
    pub deck: Deck,
    pub max_depth: usize, // max_depth = 1 it should be value function player
    pub write_debug_trees: bool,
    pub value_function: ValueFunction,
    /// §40. How many of the OPPONENT's actions to search once the turn passes to them.
    ///
    /// `0` reproduces the historical behaviour exactly: the search returns the static value
    /// function the instant `state.current_player != myself`, so `max_depth` is an N-action
    /// lookahead over the bot's OWN turn and nothing else. Any card whose payoff lands on the
    /// opponent's turn — a damage-prevention lock, a forced Active switch, a wall — is priced
    /// at zero by construction, which is one cause behind three separate failures to measure
    /// such cards in this lab.
    ///
    /// A nonzero value searches that many opponent actions using PUBLIC INFORMATION ONLY (see
    /// [`is_public_information_action`]). 3 is the useful minimum: draw, attach, attack.
    pub opponent_ply: usize,

    /// §42. Price EVERY leaf through the same opponent reply, instead of only the leaves that
    /// happen to cross the turn boundary with search depth to spare.
    ///
    /// `x<N>` (this flag `false`) has an INCONSISTENT HORIZON. `expectiminimax` checks
    /// `depth == 0` BEFORE it checks the turn boundary, and a line that never ends our turn
    /// bottoms out on our own turn. So:
    ///
    /// * a line that ends our turn EARLY is charged the opponent's best public reply (a hard
    ///   `min`), while
    /// * a line that ends the turn on its last unit of depth, or never ends it at all, is
    ///   scored by the static value function with **no reply priced whatsoever**.
    ///
    /// The own-turn node then takes a `max` over those two kinds of number. Attacking ends the
    /// turn in Pocket, so the aggressive branch is the one that gets punished and the
    /// turn-preserving branch is the one that gets off free. §42 measured the consequence:
    /// among root decisions offering both kinds, `x3` picked the unpriced action about **four
    /// times** as often as its share of the candidate list, and its retreat rate roughly
    /// doubled against `p3`. That is not a deeper search — it is a search that subtracts a
    /// punishment term from aggression and exempts passivity.
    ///
    /// With this flag set the boundary is checked first, and a leaf that runs out of depth on
    /// our own turn passes the turn and is priced too. Every leaf is then "value after the
    /// opponent's best public reply", which is a consistent quantity to take a `max` over.
    pub consistent_horizon: bool,

    /// §42. See [`SearchFlags::soft_opponent`].
    pub soft_opponent: bool,
}

impl ExpectiMiniMaxPlayer {
    fn flags(&self) -> SearchFlags {
        SearchFlags {
            consistent_horizon: self.consistent_horizon,
            soft_opponent: self.soft_opponent,
        }
    }
}

/// §40 instrumentation. Counts how many times the search actually crossed the turn boundary
/// and searched the opponent's turn, and how many opponent branches it considered there.
///
/// This exists because of the §37-R rule: before reading anything into a null result from the
/// opponent ply, prove the ply FIRED. A silent zero here would make "the opponent ply changes
/// nothing" a statement about a dead code path rather than about the game.
pub static OPPONENT_PLY_NODES: AtomicUsize = AtomicUsize::new(0);
pub static OPPONENT_PLY_BRANCHES: AtomicUsize = AtomicUsize::new(0);

/// Read and reset the §40 opponent-ply counters.
pub fn take_opponent_ply_stats() -> (usize, usize) {
    (
        OPPONENT_PLY_NODES.swap(0, Ordering::Relaxed),
        OPPONENT_PLY_BRANCHES.swap(0, Ordering::Relaxed),
    )
}

/// §40. May the searching player consider this opponent action, given they cannot see the
/// opponent's hand or deck?
///
/// Extending the search into the opponent's turn means generating the opponent's legal
/// actions — but `generate_possible_actions` builds those from their actual hand, so using it
/// unfiltered would hand the bot perfect information and make it strictly *more* omniscient
/// than the leak this section set out to remove. This filter is what keeps the ply honest.
///
/// Allowed: attacking with the Active already in play, attaching the turn's Energy (the Energy
/// Zone is public), retreating, using an Ability of a Pokémon in play, drawing, ending the
/// turn. All of these are visible across the table.
///
/// Rejected: anything sourced from the hand or deck — playing a Trainer, placing a Pokémon,
/// evolving, attaching a Tool.
///
/// Stack actions are always allowed: they are forced continuations of a choice already made,
/// so filtering them would strand the search mid-resolution.
fn is_public_information_action(action: &Action) -> bool {
    matches!(
        action.action,
        SimpleAction::Attack(_)
            | SimpleAction::Retreat(_)
            | SimpleAction::UseAbility { .. }
            | SimpleAction::EndTurn
            | SimpleAction::Activate { .. }
            | SimpleAction::Promote { .. }
            | SimpleAction::DrawCard { .. }
            | SimpleAction::Attach {
                is_turn_energy: true,
                ..
            }
    )
}

/// True only for the current, complete compulsory replacement frame.
///
/// The full Bench-set check prevents a stale or forged subset from receiving free search depth.
/// Generic `Activate` frames remain ordinary effect choices even when their shape resembles a
/// promotion.
fn is_current_promotion_frame(
    state: &State,
    frame_actor: usize,
    choices: &[SimpleAction],
) -> bool {
    if state.turn_count == 0
        || state.setup_opponent_hidden
        || choices.is_empty()
        || state.in_play_pokemon.get(frame_actor).is_none()
        || state.in_play_pokemon[frame_actor][0].is_some()
    {
        return false;
    }

    let mut current_bench = state
        .enumerate_bench_pokemon(frame_actor)
        .map(|(idx, _)| idx)
        .collect::<Vec<_>>();
    current_bench.sort_unstable();
    let mut offered = Vec::with_capacity(choices.len());
    for choice in choices {
        match choice {
            SimpleAction::Promote {
                player,
                in_play_idx,
            } if *player == frame_actor
                && state.in_play_pokemon[frame_actor]
                    .get(*in_play_idx)
                    .is_some_and(|slot| slot.is_some()) =>
            {
                offered.push(*in_play_idx);
            }
            _ => return false,
        }
    }
    offered.sort_unstable();
    offered == current_bench
}

impl ExpectiMiniMaxPlayer {
    fn decide_with_public_reply_provenance(
        &mut self,
        rng: &mut StdRng,
        state: &State,
        possible_actions: &[Action],
        public_reply_provenance: PublicReplyProvenance,
    ) -> Action {
        let myself = possible_actions[0].actor;

        // Create a tree for debugging purposes
        let mut root = DebugStateNode {
            acting_player: myself,
            children: vec![],
            proba: 1.0,
            value: 0.0,
            win_distance: None,
        };

        // Get value for each possible action
        let original_level = log::max_level();
        log::set_max_level(LevelFilter::Info); // Temporarily silence debug and trace logs
        let mut scores: Vec<f64> = Vec::with_capacity(possible_actions.len());
        // §42. Per candidate: did evaluating it push the search across the turn boundary, so
        // that the opponent's reply was actually priced? See `s42_probe`.
        let mut priced: Vec<bool> = Vec::with_capacity(possible_actions.len());
        for action in possible_actions.iter() {
            let before = OPPONENT_PLY_NODES.load(Ordering::Relaxed);
            let (score, action_node) = crate::observation::with_root_action(action, || {
                if state.setup_opponent_hidden {
                    crate::observation::record_unpriced(
                        action,
                        "opponent setup is hidden; only own setup development is scored",
                    );
                }
                expected_value_function_with_public_reply(
                    rng,
                    state,
                    action,
                    self.max_depth - 1,
                    self.opponent_ply,
                    false,
                    self.flags(),
                    myself,
                    &self.value_function,
                    public_reply_provenance,
                )
            });
            priced.push(OPPONENT_PLY_NODES.load(Ordering::Relaxed) > before);
            scores.push(score);
            root.children.push(action_node);
        }
        log::set_max_level(original_level); // Restore the original logging level

        trace!("Scores: {scores:?}");
        // Select the one with best score
        let (best_idx, best_score) = scores
            .iter()
            .enumerate()
            .max_by(|(a_idx, a), (b_idx, b)| {
                a.partial_cmp(b).unwrap().then_with(|| prefer_shorter_win(
                    root.children[*a_idx].win_distance,
                    root.children[*b_idx].win_distance,
                ))
            })
            .map(|(idx, score)| (idx, *score))
            .unwrap();
        root.value = best_score;
        root.win_distance = root.children[best_idx].win_distance;
        super::s42_probe::record_decision(
            myself,
            &possible_actions[best_idx].action,
            &priced,
            best_idx,
        );

        // Output Tree in Dot format for visualization if enabled
        if self.write_debug_trees {
            let folder = "expectiminimax_trees";
            std::fs::create_dir_all(folder).unwrap();

            // Find next available filename to avoid overwriting
            let mut counter = 0;
            let filename = loop {
                let candidate = format!(
                    "{}/expectiminimax_tree_turn{}_p{}_{}.dot",
                    folder, state.turn_count, myself, counter
                );
                if !std::path::Path::new(&candidate).exists() {
                    break candidate;
                }
                counter += 1;
            };
            save_tree_as_dot(&root, state, filename).unwrap();
        }

        // You can now use both best_idx and best_score as needed
        possible_actions[best_idx].clone()
    }

}

impl Player for ExpectiMiniMaxPlayer {
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        observation: &crate::observation::PlayerObservation,
        possible_actions: &[Action],
    ) -> Action {
        // Keep the trait's established determinization domain while retaining proof that this
        // search started from a redacted player observation rather than a raw referee State.
        let mut observation_rng =
            StdRng::seed_from_u64(rng.clone().next_u64() ^ 0x50444c5f4f425331);
        let state = observation.search_state(&mut observation_rng);
        self.decide_with_public_reply_provenance(
            rng,
            &state,
            possible_actions,
            PublicReplyProvenance::from_observation(observation),
        )
    }

    fn decide_omniscient(
        &mut self,
        rng: &mut StdRng,
        state: &State,
        possible_actions: &[Action],
    ) -> Action {
        self.decide_with_public_reply_provenance(
            rng,
            state,
            possible_actions,
            PublicReplyProvenance::untrusted(),
        )
    }

    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
}

#[allow(clippy::too_many_arguments)]
fn expected_value_function_with_public_reply(
    rng: &mut StdRng,
    state: &State,
    action: &Action,
    depth: usize,
    opp_budget: usize,
    opp_entered: bool,
    flags: SearchFlags,
    myself: usize,
    value_function: &ValueFunction,
    public_reply_provenance: PublicReplyProvenance,
) -> (f64, DebugActionNode) {
    let indent = "\t".repeat(10 - depth.min(10));
    trace!("{indent}E({myself}) depth left: {depth} action: {action:?}");

    if let Some(reason) = crate::observation::hidden_continuation_reason(state, action) {
        crate::observation::record_unpriced(action, reason);
        let score = value_function(state, myself);
        return (
            score,
            DebugActionNode {
                action: action.clone(),
                children: Vec::new(),
                value: score,
                unpriced_reason: Some(reason.into()),
                win_distance: None,
            },
        );
    }

    let public_reply_provenance = public_reply_provenance.advance(state, action);
    let forecast = match try_forecast_action(state, action) {
        Ok(forecast) => forecast,
        Err(error) => {
            crate::observation::record_unpriced(action, &error.reason);
            let score = value_function(state, myself);
            return (
                score,
                DebugActionNode {
                    action: action.clone(),
                    children: Vec::new(),
                    value: score,
                    unpriced_reason: Some(error.reason),
                    win_distance: None,
                },
            );
        }
    };
    let (probabilities, mutations) = forecast.into_branches();
    let mut outcomes: Vec<State> = vec![];
    for mutation in mutations {
        let mut state_copy = state.clone();
        mutation(rng, &mut state_copy, action);
        outcomes.push(state_copy);
    }

    // Mantain node
    let mut scores = vec![];
    let mut action_node = DebugActionNode {
        action: action.clone(),
        children: vec![],
        value: 0.0,
        unpriced_reason: None,
        win_distance: None,
    };
    for (prob, outcome) in probabilities.iter().zip(outcomes.iter()) {
        let (score, mut state_node) = expectiminimax_with_public_reply(
            rng,
            outcome,
            depth,
            opp_budget,
            opp_entered,
            flags,
            myself,
            value_function,
            public_reply_provenance,
        );
        scores.push(score);
        state_node.proba = *prob;
        action_node.children.push(state_node);
    }

    let score = probabilities
        .iter()
        .zip(scores.iter())
        .map(|(p, s)| p * s)
        .sum::<f64>();

    action_node.value = score;
    action_node.win_distance = chance_win_distance(&action_node.children);
    trace!("{indent}E({myself}) action: {action:?} score: {score}");
    (score, action_node)
}

/// Return the ordinary terminal-loss utility only when the public reply guard supplies a
/// positive certificate. Every other verdict remains unknown: record why and let the caller use
/// the search behavior it already had at that boundary.
fn certified_public_reply_loss_value(
    state: &State,
    myself: usize,
    value_function: &ValueFunction,
    public_reply_provenance: PublicReplyProvenance,
) -> Option<f64> {
    let diagnostic_action = Action {
        actor: state.current_player,
        action: SimpleAction::Noop,
        is_stack: false,
    };
    // `assess` returns the stored invalid provenance reason before inspecting the leaf, so an
    // invalid token remains unable to certify while retaining its precise diagnostic.
    let assessment = public_reply_provenance.assess(state, myself);
    if let PublicReplyAssessment::ProvenImmediateWin {
        action, positive_branches, probability_sum,
    } = &assessment {
        let mut terminal = state.clone();
        terminal.winner = Some(crate::state::GameOutcome::Win(1 - myself));
        let value = value_function(&terminal, myself);
        crate::public_reply_evidence::record_public_reply(
            state, myself, action, *positive_branches, *probability_sum, value,
        );
        return Some(value);
    }

    crate::observation::record_unpriced(
        &diagnostic_action,
        assessment
            .unpriced_reason()
            .unwrap_or("opponent reply remains uncertified; using the existing fallback"),
    );
    None
}

#[allow(clippy::too_many_arguments)]
fn expectiminimax_with_public_reply(
    rng: &mut StdRng,
    state: &State,
    depth: usize,
    opp_budget: usize,
    opp_entered: bool,
    flags: SearchFlags,
    myself: usize,
    value_function: &ValueFunction,
    public_reply_provenance: PublicReplyProvenance,
) -> (f64, DebugStateNode) {
    let static_eval = || {
        let score = value_function(state, myself);
        (
            score,
            DebugStateNode {
                acting_player: state.current_player,
                children: vec![],
                proba: 1.0,
                value: score,
                win_distance: (state.winner == Some(crate::state::GameOutcome::Win(myself)))
                    .then_some(0),
            },
        )
    };

    // A settled outcome needs no private continuation, nor any further turn resolution.
    // In particular, do not run Checkup after an attack has already ended the game.
    if state.is_game_over() {
        super::s42_probe::LEAF_AFTER_OPP_PLY.fetch_add(usize::from(opp_entered), Ordering::Relaxed);
        return static_eval();
    }

    // A redacted observation preserves the public fact that an attack is pending but removes
    // another player's private choice payload. Stop before trying to expand that empty frame.
    if let Some((actor, choices)) = state.move_generation_stack.last() {
        if choices.is_empty() {
            let action = Action {
                actor: *actor,
                action: SimpleAction::Noop,
                is_stack: true,
            };
            crate::observation::record_unpriced(
                &action,
                "private pending choice is unavailable to this observer",
            );
            return static_eval();
        }
    }

    // An attack (or an effect that explicitly ends the turn) commits its mandatory
    // Checkup. Resolve that forced EndTurn without spending another ordinary action ply.
    // A voluntary pass and setup handoff must still consume their normal search depth.
    let forced_end_turn = state.turn_count > 0
        && match state.move_generation_stack.last() {
            Some((_, choices)) => matches!(choices.as_slice(), [SimpleAction::EndTurn]),
            None => state.end_turn_pending,
        };
    if forced_end_turn {
        let (_, actions) = state.generate_possible_actions();
        assert_eq!(actions.len(), 1, "forced turn end must have exactly one continuation");
        let (score, child) = expected_value_function_with_public_reply(
            rng, state, &actions[0], depth, opp_budget, opp_entered, flags, myself,
            value_function, public_reply_provenance,
        );
        return (score, DebugStateNode {
            acting_player: state.current_player,
            win_distance: child.win_distance,
            children: vec![child],
            proba: 1.0,
            value: score,
        });
    }

    // Victory Star and a queued attack-damage target are parts of the attack already being
    // priced. Resolve either public continuation even at depth zero and before the generic
    // unknown-opponent cutoff; charging another normal-action ply would make shallow searches
    // score the uncommitted, zero-damage pause state.
    let queued_attack_damage_choice =
        state
            .move_generation_stack
            .last()
            .is_some_and(|(_, choices)| {
                !choices.is_empty()
                    && choices.iter().all(|choice| {
                        matches!(choice, SimpleAction::ApplyQueuedAttackDamage { .. })
                    })
            });
    if state.pending_attack_coin_choice.is_some()
        || state.pending_misty_target_choice.is_some()
        || state.pending_trainer_coin_choice.is_some()
        || queued_attack_damage_choice
    {
        let (actor, actions) = state.generate_possible_actions();
        assert!(
            !actions.is_empty() && actions.iter().all(|action| action.is_stack),
            "pending attack continuation must expose stack choices"
        );
        let mut scores = Vec::with_capacity(actions.len());
        let mut children = Vec::with_capacity(actions.len());
        for action in &actions {
            let (score, child) = expected_value_function_with_public_reply(
                rng,
                state,
                action,
                depth,
                opp_budget,
                opp_entered,
                flags,
                myself,
                value_function,
                public_reply_provenance,
            );
            scores.push(score);
            children.push(child);
        }
        let value = if actor == myself {
            scores.iter().copied().fold(f64::NEG_INFINITY, f64::max)
        } else {
            scores.iter().copied().fold(f64::INFINITY, f64::min)
        };
        return (
            value,
            DebugStateNode {
                acting_player: actor,
                win_distance: choice_win_distance(&children, value, actor, myself),
                children,
                proba: 0.0,
                value,
            },
        );
    }

    // Replacing an empty Active is a compulsory continuation of the action that caused it, not
    // another ordinary action. Resolve only an explicit, complete top Promote frame at the same
    // depth. In particular, never infer promotion from a generic Activate frame or scan through
    // another pending effect to find a promotion below it.
    let promotion_choice = state
        .move_generation_stack
        .last()
        .is_some_and(|(actor, choices)| is_current_promotion_frame(state, *actor, choices));
    if promotion_choice {
        let (actor, actions) = state.generate_possible_actions();
        assert!(
            !actions.is_empty()
                && actions.iter().all(|action| {
                    action.is_stack
                        && matches!(action.action, SimpleAction::Promote { player, .. }
                            if player == actor)
                }),
            "explicit promotion must expose only stack Promote choices"
        );
        let mut scores = Vec::with_capacity(actions.len());
        let mut children = Vec::with_capacity(actions.len());
        for action in &actions {
            let (score, child) = expected_value_function_with_public_reply(
                rng,
                state,
                action,
                depth,
                opp_budget,
                opp_entered,
                flags,
                myself,
                value_function,
                public_reply_provenance,
            );
            scores.push(score);
            children.push(child);
        }
        let value = if actor == myself {
            scores.iter().copied().fold(f64::NEG_INFINITY, f64::max)
        } else {
            scores.iter().copied().fold(f64::INFINITY, f64::min)
        };
        return (
            value,
            DebugStateNode {
                acting_player: actor,
                win_distance: choice_win_distance(&children, value, actor, myself),
                children,
                proba: 0.0,
                value,
            },
        );
    }

    if state.current_player != myself
        && (state.hands[state.current_player].contains(&crate::models::Card::Unknown)
            || state.decks[state.current_player]
                .cards
                .contains(&crate::models::Card::Unknown)
            || state.decks[state.current_player].energy_types.is_empty())
    {
        if let Some(score) = certified_public_reply_loss_value(
            state,
            myself,
            value_function,
            public_reply_provenance,
        ) {
            return (
                score,
                DebugStateNode {
                    acting_player: state.current_player,
                    children: vec![],
                    proba: 1.0,
                    value: score,
                    win_distance: None,
                },
            );
        }
        return static_eval();
    }

    if depth == 0 {
        // §42 leaf accounting. `opp_entered` marks a leaf whose opponent reply WAS searched;
        // anything else that bottoms out here is a leaf where the reply was never priced.
        // If aggressive lines land in the first bucket and passive lines in the second, the
        // search is not comparing like with like.
        if opp_entered {
            super::s42_probe::LEAF_AFTER_OPP_PLY.fetch_add(1, Ordering::Relaxed);
            return static_eval();
        }
        if state.current_player != myself {
            // Our turn ENDED here, and the opponent budget may still be unspent — but under
            // `x<N>` the depth check fires first, so the reply goes unpriced anyway. This is
            // the inconsistency, counted separately because it is the one that discriminates
            // by WHEN a line ends the turn rather than by whether it ends it at all.
            if opp_budget > 0 {
                super::s42_probe::LEAF_TURN_PASSED_DEPTH0.fetch_add(1, Ordering::Relaxed);
                if flags.consistent_horizon {
                    return opponent_ply_node(
                        rng,
                        state,
                        depth,
                        opp_budget,
                        flags,
                        myself,
                        value_function,
                        public_reply_provenance,
                    );
                }
            } else {
                super::s42_probe::LEAF_BOUNDARY_UNPRICED.fetch_add(1, Ordering::Relaxed);
            }
            return static_eval();
        }
        super::s42_probe::LEAF_OWN_TURN.fetch_add(1, Ordering::Relaxed);
        // §42 — THE CONSISTENCY FIX. We ran out of depth while still on our own turn, so this
        // leaf would be scored with no opponent reply at all while its aggressive siblings
        // were charged the opponent's best punish. Pass the turn and price it the same way.
        // If the turn cannot be passed here (a forced choice is pending, or the opponent is
        // the one to act) fall through to the static evaluation rather than inventing a line.
        if flags.consistent_horizon && opp_budget > 0 {
            let (actor, actions) = state.generate_possible_actions();
            if actor == myself {
                if let Some(end) = actions
                    .iter()
                    .find(|a| !a.is_stack && matches!(a.action, SimpleAction::EndTurn))
                {
                    // Applied INLINE rather than by recursing back through
                    // `expected_value_function`: re-entering this same `depth == 0` branch
                    // could look for EndTurn again on any state where passing does not in
                    // fact hand over the turn, and loop. One pass, then price or fall back.
                    if let Some(reason) = crate::observation::hidden_continuation_reason(state, end)
                    {
                        crate::observation::record_unpriced(end, reason);
                        return static_eval();
                    }
                    let end_turn_provenance = public_reply_provenance.advance(state, end);
                    let (probabilities, mutations) = forecast_action(state, end).into_branches();
                    let mut outcomes: Vec<State> = vec![];
                    for mutation in mutations {
                        let mut state_copy = state.clone();
                        mutation(rng, &mut state_copy, end);
                        outcomes.push(state_copy);
                    }
                    let mut score = 0.0;
                    for (prob, outcome) in probabilities.iter().zip(outcomes.iter()) {
                        let v = if !outcome.is_game_over() && outcome.current_player != myself {
                            certified_public_reply_loss_value(
                                outcome,
                                myself,
                                value_function,
                                end_turn_provenance,
                            )
                            .unwrap_or_else(|| {
                                opponent_ply_node(
                                    rng,
                                    outcome,
                                    depth,
                                    opp_budget,
                                    flags,
                                    myself,
                                    value_function,
                                    end_turn_provenance,
                                )
                                .0
                            })
                        } else {
                            // Either the game ended or ending the turn did not actually pass
                            // it. Nothing to price; score the position as it stands.
                            value_function(outcome, myself)
                        };
                        score += prob * v;
                    }
                    return (
                        score,
                        DebugStateNode {
                            acting_player: state.current_player,
                            children: vec![],
                            proba: 1.0,
                            value: score,
                            win_distance: None,
                        },
                    );
                }
            }
        }
        return static_eval();
    }

    // §40 — THE TURN BOUNDARY.
    //
    // Historically this was `|| state.current_player != myself` in the guard above: the search
    // stopped dead the moment the turn passed, so it never saw the opponent's reply. With
    // `opponent_ply > 0` we instead search a bounded number of the opponent's actions, using
    // public information only.
    if state.current_player != myself {
        if opp_budget == 0 {
            super::s42_probe::LEAF_BOUNDARY_UNPRICED.fetch_add(1, Ordering::Relaxed);
            return static_eval();
        }
        return opponent_ply_node(
            rng,
            state,
            depth,
            opp_budget,
            flags,
            myself,
            value_function,
            public_reply_provenance,
        );
    }

    // Control has come back to us after the opponent's turn was searched. Stop here rather
    // than recursing into another of our own turns: the point is to price the opponent's
    // reply, not to buy extra depth for ourselves, and continuing would multiply cost by the
    // full branching factor of a second own-turn search.
    if opp_entered {
        super::s42_probe::LEAF_AFTER_OPP_PLY.fetch_add(1, Ordering::Relaxed);
        return static_eval();
    }

    let (actor, actions) = state.generate_possible_actions();
    if actor == myself {
        // We are in maximing mode.
        let mut scores: Vec<f64> = Vec::with_capacity(actions.len());
        let mut children = vec![];
        for action in actions.iter() {
            let (score, action_node) = expected_value_function_with_public_reply(
                rng,
                state,
                action,
                depth - 1,
                opp_budget,
                opp_entered,
                flags,
                myself,
                value_function,
                public_reply_provenance,
            );
            scores.push(score);
            children.push(action_node);
        }
        let best_score = scores.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let state_node = DebugStateNode {
            acting_player: actor,
            win_distance: choice_win_distance(&children, best_score, actor, myself),
            children,
            proba: 0.0, // this will get set by parent
            value: best_score,
        };
        (best_score, state_node)
    } else {
        // The opponent has to act during OUR turn (a forced choice we caused).
        //
        // The upstream TODO here reads: "If minimizing, we can't just generate_possible_actions
        // since not everything is public information." §40 supplies that filter — but only for
        // the new tiers. With `opp_budget == 0` the action list is left exactly as it was, so
        // `e<N>` stays bit-for-bit identical to every historical run in this lab.
        let filtered: Vec<Action> = if opp_budget > 0 {
            let public: Vec<Action> = actions
                .iter()
                .filter(|a| is_public_information_action(a))
                .cloned()
                .collect();
            // Never strand the search: if the filter removes everything, fall back to the
            // unfiltered list rather than returning a meaningless infinity.
            if public.is_empty() {
                actions.clone()
            } else {
                public
            }
        } else {
            actions.clone()
        };

        let mut scores: Vec<f64> = Vec::with_capacity(filtered.len());
        let mut children: Vec<DebugActionNode> = Vec::new();
        for action in filtered.iter() {
            let (score, action_node) = expected_value_function_with_public_reply(
                rng,
                state,
                action,
                depth - 1,
                opp_budget,
                opp_entered,
                flags,
                myself,
                value_function,
                public_reply_provenance,
            );
            scores.push(score);
            children.push(action_node);
        }
        let best_score = scores.iter().cloned().fold(f64::INFINITY, f64::min);
        let state_node = DebugStateNode {
            acting_player: actor,
            win_distance: choice_win_distance(&children, best_score, actor, myself),
            children,
            proba: 0.0, // this will get set by parent
            value: best_score,
        };
        (best_score, state_node)
    }
}

/// §40 — search one bounded stretch of the OPPONENT's turn, from public information only.
///
/// This is the node that did not exist before: previously the search returned the static
/// value function here, so nothing the opponent could do on their own turn was ever
/// simulated. The opponent minimizes our value, and every branch is drawn from
/// [`is_public_information_action`], so the bot gains no knowledge of their hand or deck.
///
/// `depth` is deliberately NOT decremented — opponent actions are paid for out of their own
/// `opp_budget`, so this cannot silently eat the own-turn lookahead that `max_depth` buys.
fn opponent_ply_node(
    rng: &mut StdRng,
    state: &State,
    depth: usize,
    opp_budget: usize,
    flags: SearchFlags,
    myself: usize,
    value_function: &ValueFunction,
    public_reply_provenance: PublicReplyProvenance,
) -> (f64, DebugStateNode) {
    OPPONENT_PLY_NODES.fetch_add(1, Ordering::Relaxed);
    let (actor, actions) = state.generate_possible_actions();

    let public: Vec<Action> = actions
        .iter()
        .filter(|a| is_public_information_action(a))
        .cloned()
        .collect();

    // Nothing the opponent could publicly do here — score the position as it stands.
    if public.is_empty() {
        let score = value_function(state, myself);
        return (
            score,
            DebugStateNode {
                acting_player: actor,
                children: vec![],
                proba: 1.0,
                value: score,
                win_distance: None,
            },
        );
    }

    OPPONENT_PLY_BRANCHES.fetch_add(public.len(), Ordering::Relaxed);
    let mut scores: Vec<f64> = Vec::with_capacity(public.len());
    let mut children: Vec<DebugActionNode> = Vec::new();
    for action in public.iter() {
        let (score, action_node) = expected_value_function_with_public_reply(
            rng,
            state,
            action,
            depth,
            opp_budget - 1,
            true,
            flags,
            myself,
            value_function,
            public_reply_provenance,
        );
        scores.push(score);
        children.push(action_node);
    }

    // The opponent picks the reply that is worst for us — or, under `soft_opponent`, we
    // average over their public options instead. See [`SearchFlags::soft_opponent`]: the `min`
    // is taken over a filtered action list that is dominated by attacks, so it does not mean
    // "their best reply", it means "their hardest hit, every time".
    let best_score = if flags.soft_opponent {
        scores.iter().sum::<f64>() / scores.len() as f64
    } else {
        scores.iter().cloned().fold(f64::INFINITY, f64::min)
    };
    (
        best_score,
        DebugStateNode {
            acting_player: actor,
            win_distance: choice_win_distance(&children, best_score, actor, myself),
            children,
            proba: 0.0, // set by parent
            value: best_score,
        },
    )
}

impl Debug for ExpectiMiniMaxPlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ExpectiMiniMaxPlayer")
    }
}

// Unit tests in this module exercise constructed raw states. Keep their compact historical
// helpers while making the production entry provenance explicit.
#[cfg(test)]
#[allow(clippy::too_many_arguments)]
fn expected_value_function(
    rng: &mut StdRng,
    state: &State,
    action: &Action,
    depth: usize,
    opp_budget: usize,
    opp_entered: bool,
    flags: SearchFlags,
    myself: usize,
    value_function: &ValueFunction,
) -> (f64, DebugActionNode) {
    expected_value_function_with_public_reply(
        rng,
        state,
        action,
        depth,
        opp_budget,
        opp_entered,
        flags,
        myself,
        value_function,
        PublicReplyProvenance::untrusted(),
    )
}

#[cfg(test)]
#[allow(clippy::too_many_arguments)]
fn expectiminimax(
    rng: &mut StdRng,
    state: &State,
    depth: usize,
    opp_budget: usize,
    opp_entered: bool,
    flags: SearchFlags,
    myself: usize,
    value_function: &ValueFunction,
) -> (f64, DebugStateNode) {
    expectiminimax_with_public_reply(
        rng,
        state,
        depth,
        opp_budget,
        opp_entered,
        flags,
        myself,
        value_function,
        PublicReplyProvenance::untrusted(),
    )
}

#[cfg(test)]
mod public_information_filter_tests {
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::models::{Attack, Card, EnergyType, TrainerCard};
    use crate::state::PendingAttackCoinChoice;

    fn act(action: SimpleAction) -> Action {
        Action {
            actor: 1,
            action,
            is_stack: false,
        }
    }

    fn a_pokemon() -> Card {
        get_card_by_enum(CardId::A1003Venusaur)
    }

    fn a_trainer() -> TrainerCard {
        match get_card_by_enum(CardId::A1219Erika) {
            Card::Trainer(t) => t,
            other => panic!("expected a Trainer card, got {other:?}"),
        }
    }

    #[test]
    fn test_redacted_victory_star_continuation_is_unpriced_without_panicking() {
        let mut state = State::default();
        state.pending_attack_coin_choice = Some(PendingAttackCoinChoice {
            actor: 0,
            attack: Attack {
                energy_required: Vec::new(),
                title: "Coin Attack".into(),
                fixed_damage: 0,
                effect: Some("Flip a coin.".into()),
            },
            original_is_stack: false,
            flips: vec![true],
            victory_star_in_play_idx: 1,
        });
        state.move_generation_stack.push((0, Vec::new()));
        let evaluator: ValueFunction = Box::new(|_, _| 17.0);
        let mut rng = rand::SeedableRng::seed_from_u64(4);

        let ((score, node), branches) = crate::observation::collect_unpriced(|| {
            expectiminimax(
                &mut rng,
                &state,
                1,
                0,
                false,
                SearchFlags::default(),
                1,
                &evaluator,
            )
        });

        assert_eq!(score, 17.0);
        assert!(node.children.is_empty());
        assert_eq!(branches.len(), 1);
        assert_eq!(
            branches[0].reason,
            "private pending choice is unavailable to this observer"
        );
    }

    fn thunderclaw_search_state() -> (State, Attack) {
        use crate::models::PlayedCard;

        let mut state = State::default();
        state.set_board(
            vec![PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx)],
            vec![
                PlayedCard::from_id(CardId::A1004VenusaurEx),
                PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
            ],
        );
        state.current_player = 0;
        state.turn_count = 3;
        let attack = get_card_by_enum(CardId::B4a021TeamRocketsZapdosEx).get_attacks()[1].clone();
        (state, attack)
    }

    fn negative_opponent_hp(state: &State, _myself: usize) -> f64 {
        -state
            .enumerate_in_play_pokemon(1)
            .map(|(_, pokemon)| pokemon.get_remaining_hp() as f64)
            .sum::<f64>()
    }

    #[test]
    fn depth_zero_prices_mandatory_queued_attack_damage() {
        let (state, attack) = thunderclaw_search_state();
        let action = Action {
            actor: 0,
            action: SimpleAction::Attack(attack),
            is_stack: false,
        };
        let evaluator: ValueFunction = Box::new(negative_opponent_hp);
        let mut rng = rand::SeedableRng::seed_from_u64(11);

        let (score, _) = expected_value_function(
            &mut rng,
            &state,
            &action,
            0,
            0,
            false,
            SearchFlags::default(),
            0,
            &evaluator,
        );

        assert_eq!(
            score, -220.0,
            "depth-zero search must see 90 Active plus 50 chosen-Bench damage"
        );
    }

    #[test]
    fn queued_attack_damage_does_not_consume_an_ordinary_search_ply() {
        let (mut state, attack) = thunderclaw_search_state();
        state.move_generation_stack.push((
            0,
            vec![SimpleAction::ApplyQueuedAttackDamage {
                attack,
                targets: vec![(90, true, 0), (50, true, 1)],
            }],
        ));
        let evaluator: ValueFunction = Box::new(negative_opponent_hp);
        let mut rng = rand::SeedableRng::seed_from_u64(12);

        let (_, node) = expectiminimax(
            &mut rng,
            &state,
            1,
            0,
            false,
            SearchFlags::default(),
            0,
            &evaluator,
        );

        assert_eq!(node.children.len(), 1);
        let after_target = &node.children[0].children[0];
        assert!(
            !after_target.children.is_empty(),
            "the same depth must remain available after the forced target continuation"
        );
    }

    /// §40's PRIMARY CORRECTNESS GATE. The opponent ply may only branch on things visible
    /// across the table. If any of these start passing, the search has become omniscient and
    /// every number produced by `x<N>` is void.
    #[test]
    fn test_hand_sourced_actions_are_rejected() {
        let hidden = [
            act(SimpleAction::Play {
                trainer_card: a_trainer(),
            }),
            act(SimpleAction::Place(a_pokemon(), 1)),
            act(SimpleAction::Evolve {
                evolution: a_pokemon(),
                in_play_idx: 0,
                from_deck: false,
            }),
            act(SimpleAction::Evolve {
                evolution: a_pokemon(),
                in_play_idx: 0,
                from_deck: true,
            }),
            act(SimpleAction::AttachTool {
                in_play_idx: 0,
                tool_card: a_pokemon(),
            }),
        ];
        for action in hidden {
            assert!(
                !is_public_information_action(&action),
                "the opponent ply would branch on a HIDDEN-ZONE action: {:?}",
                action.action
            );
        }
    }

    /// The mirror of the gate: if the filter rejected everything, the ply would collapse to
    /// the static evaluation it was built to replace and would measure nothing. This is the
    /// §37-R "prove a known-nonzero case" assertion for the filter.
    #[test]
    fn test_public_board_actions_are_allowed() {
        let public = [
            act(SimpleAction::EndTurn),
            act(SimpleAction::Retreat(1)),
            act(SimpleAction::Promote {
                player: 1,
                in_play_idx: 1,
            }),
            act(SimpleAction::UseAbility { in_play_idx: 0 }),
            act(SimpleAction::DrawCard { amount: 1 }),
            act(SimpleAction::Attach {
                attachments: vec![(1, EnergyType::Grass, 0)],
                is_turn_energy: true,
            }),
        ];
        for action in public {
            assert!(
                is_public_information_action(&action),
                "the opponent ply would refuse a PUBLIC action: {:?}",
                action.action
            );
        }
    }

    /// Energy moved from somewhere other than the Energy Zone is the product of a card that
    /// was played, so it is not independently observable as a choice.
    #[test]
    fn test_non_zone_energy_attachment_is_rejected() {
        assert!(!is_public_information_action(&act(SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Grass, 0)],
            is_turn_energy: false,
        })));
    }

    /// A forced continuation can still contain an opponent's private card identities.
    #[test]
    fn test_stack_membership_does_not_reveal_private_cards() {
        let mut stacked = act(SimpleAction::Play {
            trainer_card: a_trainer(),
        });
        assert!(!is_public_information_action(&stacked));
        stacked.is_stack = true;
        assert!(
            !is_public_information_action(&stacked),
            "stack membership cannot grant access to opponent hidden cards"
        );
    }
}

fn save_tree_as_dot(
    root: &DebugStateNode,
    root_state: &State,
    filename: String,
) -> std::io::Result<()> {
    let dot_representation = generate_dot(root, root_state);
    std::fs::write(filename, dot_representation)
}

fn generate_dot(root: &DebugStateNode, root_state: &State) -> String {
    let mut dot = String::new();
    writeln!(dot, "digraph GameTree {{").unwrap();
    writeln!(dot, "    rankdir=TB;").unwrap();
    writeln!(dot, "    node [shape=box];").unwrap();

    // Add info node with root state debug string
    let debug_str = root_state
        .debug_string()
        .replace('"', "'")
        .replace('\n', "\\l")
        + "\\l";
    writeln!(
        dot,
        "    info [label=\"{}\", shape=box, style=filled, fillcolor=lightyellow, align=left];",
        debug_str
    )
    .unwrap();

    let mut state_counter = 0;
    let mut action_counter = 0;

    generate_dot_recursive(
        root,
        &mut dot,
        &mut state_counter,
        &mut action_counter,
        0,
        root.acting_player,
    );

    writeln!(dot, "}}").unwrap();
    dot
}

fn generate_dot_recursive(
    state: &DebugStateNode,
    dot: &mut String,
    state_counter: &mut usize,
    action_counter: &mut usize,
    current_state_id: usize,
    myself: usize,
) {
    // Define the state node with color based on acting player
    let color = if state.acting_player == myself {
        "lightgreen"
    } else {
        "lightcoral"
    };
    writeln!(
        dot,
        "    s{} [label=\"State\\nPlayer: {}\\nProba: {:.3}\\nValue: {:.3}\", style=filled, fillcolor={}];",
        current_state_id,
        state.acting_player,
        state.proba,
        state.value,
        color
    ).unwrap();

    // Process each action child
    for action_node in &state.children {
        *action_counter += 1;
        let action_id = *action_counter;

        // An unpriced boundary score must not look like a completed forecast.
        let uncertainty = action_node.unpriced_reason.as_deref().unwrap_or("");
        writeln!(
            dot,
            "    a{} [label=\"P{} {}\\n{:?}\\nValue: {:.3}\\n{}\", shape=ellipse, style=filled, fillcolor=lightgrey];",
            action_id,
            action_node.action.actor,
            action_node.action.is_stack,
            action_node.action.action,
            action_node.value,
            if uncertainty.is_empty() { String::new() } else { format!("UNPRICED: {uncertainty}") }
        ).unwrap();

        // Edge from state to action
        writeln!(dot, "    s{} -> a{};", current_state_id, action_id).unwrap();

        // Process each state child of this action
        for child_state in &action_node.children {
            *state_counter += 1;
            let child_state_id = *state_counter;

            // Edge from action to child state
            writeln!(dot, "    a{} -> s{};", action_id, child_state_id).unwrap();

            // Recursively process the child state
            generate_dot_recursive(
                child_state,
                dot,
                state_counter,
                action_counter,
                child_state_id,
                myself,
            );
        }
    }
}

#[cfg(test)]
mod xatu_forced_end_turn_regressions {
    use super::*;
    use crate::{
        actions::{Action, SimpleAction},
        card_ids::CardId,
        database::get_card_by_enum,
        models::{Card, EnergyType, PlayedCard, StatusCondition},
        observation::{PlayerObservation, RevealedKnowledge},
        state::GameOutcome,
        test_support::nth_attack,
        State,
    };
    use rand::{rngs::StdRng, SeedableRng};

    fn terminal_value(state: &State, myself: usize) -> f64 {
        match state.winner {
            Some(GameOutcome::Win(player)) if player == myself => 1.0,
            Some(GameOutcome::Win(_)) => -1.0,
            _ => 0.0,
        }
    }

    fn xatu_state(actor: usize, poisoned: bool, protected: bool) -> State {
        let xatu = PlayedCard::from_id(CardId::A4082Xatu)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic]);
        let mut target = PlayedCard::from_id(CardId::B3081MegaLucarioEx);
        if poisoned {
            target = target.with_status_condition(StatusCondition::Poisoned);
        }
        if protected {
            target = target.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
        }
        let backup = PlayedCard::from_id(CardId::A1033Charmander);

        let mut state = State::default();
        if actor == 0 {
            state.set_board(vec![xatu], vec![target, backup]);
        } else {
            state.set_board(vec![target, backup], vec![xatu]);
        }
        state.current_player = actor;
        state.turn_count = 3;
        state.points = [0, 0];
        state.hands = [Vec::new(), Vec::new()];
        state.decks[0].cards.clear();
        state.decks[1].cards.clear();
        state.decks[actor].energy_types = vec![EnergyType::Psychic];
        state.decks[1 - actor].energy_types = vec![EnergyType::Fighting];
        state.energy_zone[0].current = None;
        state.energy_zone[1].current = None;
        state
    }

    fn life_drain(actor: usize) -> Action {
        Action {
            actor,
            action: SimpleAction::Attack(nth_attack(CardId::A4082Xatu, 0)),
            is_stack: false,
        }
    }

    fn score_attack(state: &State, actor: usize, depth: usize) -> f64 {
        let evaluator: ValueFunction = Box::new(terminal_value);
        expected_value_function(
            &mut StdRng::seed_from_u64(91),
            state,
            &life_drain(actor),
            depth,
            0,
            false,
            SearchFlags::default(),
            actor,
            &evaluator,
        )
        .0
    }

    #[test]
    fn depth_zero_attack_resolves_forced_checkup_for_both_actors() {
        for actor in [0, 1] {
            let state = xatu_state(actor, true, false);
            assert_eq!(score_attack(&state, actor, 0), 0.5);
        }
    }

    #[test]
    fn will_forces_the_depth_zero_life_drain_terminal_branch() {
        let mut state = xatu_state(0, true, false);
        state.set_pending_will_first_heads();
        assert_eq!(score_attack(&state, 0, 0), 1.0);
    }

    #[test]
    fn no_poison_and_effect_prevention_are_not_false_terminals() {
        assert_eq!(score_attack(&xatu_state(0, false, false), 0, 0), 0.0);
        assert_eq!(score_attack(&xatu_state(0, true, true), 0, 0), 0.0);
    }

    #[test]
    fn playing_will_still_costs_an_ordinary_search_ply() {
        let mut state = xatu_state(0, true, false);
        state.hands[0] = vec![get_card_by_enum(CardId::A4156Will)];
        let Card::Trainer(trainer_card) = get_card_by_enum(CardId::A4156Will) else {
            unreachable!()
        };
        let action = Action {
            actor: 0,
            action: SimpleAction::Play { trainer_card },
            is_stack: false,
        };
        let evaluator: ValueFunction = Box::new(terminal_value);
        let score = expected_value_function(
            &mut StdRng::seed_from_u64(92),
            &state,
            &action,
            0,
            0,
            false,
            SearchFlags::default(),
            0,
            &evaluator,
        )
        .0;
        assert_eq!(score, 0.0, "Will itself must not receive a free attack continuation");
    }

    #[test]
    fn voluntary_end_turn_is_not_auto_applied_at_depth_zero() {
        let state = xatu_state(0, true, false);
        assert!(!state.end_turn_pending);
        let evaluator: ValueFunction = Box::new(|state, myself| {
            usize::from(state.current_player != myself) as f64
        });
        let score = expectiminimax(
            &mut StdRng::seed_from_u64(93),
            &state,
            0,
            0,
            false,
            SearchFlags::default(),
            0,
            &evaluator,
        )
        .0;
        assert_eq!(score, 0.0, "a free-play EndTurn remains an ordinary searched action");
    }

    #[test]
    fn terminal_leaf_precedes_unknown_opponent_cutoff() {
        let mut state = xatu_state(0, true, false);
        state.current_player = 1;
        state.winner = Some(GameOutcome::Win(0));
        state.hands[1] = vec![Card::Unknown];
        state.decks[1].cards = vec![Card::Unknown];
        state.decks[1].energy_types.clear();
        let evaluator: ValueFunction = Box::new(terminal_value);

        let ((score, _), unpriced) = crate::observation::collect_unpriced(|| {
            expectiminimax(
                &mut StdRng::seed_from_u64(94),
                &state,
                0,
                0,
                false,
                SearchFlags::default(),
                0,
                &evaluator,
            )
        });
        assert_eq!(score, 1.0);
        assert!(unpriced.is_empty(), "a terminal state needs no opponent information");
    }

    #[test]
    fn unknown_start_turn_random_draw_keeps_forced_end_turn_unpriced() {
        let mut state = State::default();
        state.set_board(
            vec![PlayedCard::from_id(CardId::A4082Xatu)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
            vec![
                PlayedCard::from_id(CardId::B2070Meloetta)
                    .with_status_condition(StatusCondition::Poisoned),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        state.current_player = 0;
        state.turn_count = 3;
        state.hands[1] = vec![Card::Unknown];
        state.decks[1].cards = vec![Card::Unknown];
        state.decks[0].energy_types = vec![EnergyType::Psychic];
        state.decks[1].energy_types.clear();
        let evaluator: ValueFunction = Box::new(terminal_value);

        let ((score, _), unpriced) = crate::observation::collect_unpriced(|| {
            expected_value_function(
                &mut StdRng::seed_from_u64(96),
                &state,
                &life_drain(0),
                0,
                0,
                false,
                SearchFlags::default(),
                0,
                &evaluator,
            )
        });
        assert_eq!(score, 0.0);
        assert!(
            unpriced.iter().any(|branch| branch.reason == "automatic next-turn ability searches an unknown deck"),
            "bundled EndTurn must not guess an unknown Strange Singing draw"
        );
    }

    #[test]
    fn observed_hidden_zone_substitutions_do_not_change_life_drain_value() {
        for actor in [0, 1] {
            let mut a = xatu_state(actor, true, false);
            let opponent = 1 - actor;
            a.hands[opponent] = vec![get_card_by_enum(CardId::PA001Potion)];
            a.decks[opponent].cards = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
            let mut b = a.clone();
            b.hands[opponent] = vec![get_card_by_enum(CardId::PA006RedCard)];
            b.decks[opponent].cards = vec![get_card_by_enum(CardId::A1003Venusaur)];

            let oa = PlayerObservation::from_state(&a, actor, &RevealedKnowledge::default());
            let ob = PlayerObservation::from_state(&b, actor, &RevealedKnowledge::default());
            assert_eq!(oa, ob);

            let sa = oa.search_state(&mut StdRng::seed_from_u64(95));
            let sb = ob.search_state(&mut StdRng::seed_from_u64(95));
            assert_eq!(score_attack(&sa, actor, 0), 0.5);
            assert_eq!(score_attack(&sb, actor, 0), 0.5);
        }
    }

    #[test]
    fn explicit_turn_ending_stack_resolves_burn_coin_without_an_extra_ply() {
        let mut state = xatu_state(0, false, false);
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::B3081MegaLucarioEx)
            .with_status_condition(StatusCondition::Burned));
        state.move_generation_stack.push((0, vec![SimpleAction::EndTurn]));
        let evaluator: ValueFunction = Box::new(|state, _| {
            usize::from(!state.get_active(1).has_status(StatusCondition::Burned)) as f64
        });
        let (score, _) = expectiminimax(&mut StdRng::seed_from_u64(98), &state, 0,
            0, false, SearchFlags::default(), 0, &evaluator);
        assert_eq!(score, 0.5, "the forced Checkup must average its own fair Burn coin");
    }

    #[test]
    fn terminal_attack_does_not_run_pending_checkup() {
        let mut state = xatu_state(0, false, false);
        state.winner = Some(GameOutcome::Win(0));
        state.end_turn_pending = true;
        state.in_play_pokemon[1].fill(None);
        state.turn_count = 30;
        let evaluator: ValueFunction = Box::new(terminal_value);
        let ((score, node), unpriced) = crate::observation::collect_unpriced(|| {
            expectiminimax(&mut StdRng::seed_from_u64(99), &state, 0,
                0, false, SearchFlags::default(), 0, &evaluator)
        });
        assert_eq!(score, 1.0);
        assert!(node.children.is_empty());
        assert!(unpriced.is_empty());
    }

    #[test]
    fn unknown_automatic_deck_search_guard_is_specific_to_relevant_abilities() {
        for actor in [0, 1] {
            for card in [CardId::B2070Meloetta, CardId::B3b001Caterpie] {
                let mut state = xatu_state(actor, false, false);
                let next = 1 - actor;
                state.in_play_pokemon[next][0] = Some(PlayedCard::from_id(card));
                state.decks[next].cards = vec![Card::Unknown];
                let end = Action { actor, action: SimpleAction::EndTurn, is_stack: false };
                assert_eq!(crate::observation::hidden_continuation_reason(&state, &end),
                    Some("automatic next-turn ability searches an unknown deck"));
                state.decks[next].cards = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
                assert_eq!(crate::observation::hidden_continuation_reason(&state, &end), None);
                state.decks[next].cards = vec![Card::Unknown];
                state.in_play_pokemon[next][0] = Some(PlayedCard::from_id(CardId::B3081MegaLucarioEx));
                assert_eq!(crate::observation::hidden_continuation_reason(&state, &end), None);
            }
        }
    }
#[test]
fn turn_30_checkup_win_precedes_cap_while_non_ko_becomes_tie() {
    let outcome_value: ValueFunction = Box::new(|state, _| match state.winner {
        Some(GameOutcome::Win(player)) => if player == 0 { 10.0 } else { -10.0 },
        Some(GameOutcome::Tie) => 20.0,
        None => 30.0,
    });

    for (poisoned, expected, label) in [
        (true, 10.0, "Poison KO during Checkup must remain a win"),
        (false, 20.0, "non-KO turn end must reach the turn-cap tie"),
    ] {
        let mut state = xatu_state(0, poisoned, false);
        state.turn_count = 30;
        state.set_pending_will_first_heads();

        let score = expected_value_function(
            &mut StdRng::seed_from_u64(100),
            &state,
            &life_drain(0),
            0,
            0,
            false,
            SearchFlags::default(),
            0,
            &outcome_value,
        )
        .0;

        assert_eq!(score, expected, "{label}");
    }
}

#[test]
fn suppressed_printed_automatic_abilities_still_guard_unknown_decks() {
    for automatic_active in [CardId::B2070Meloetta, CardId::B3b001Caterpie] {
        let mut state = State::default();
        state.set_board(
            vec![
                PlayedCard::from_id(CardId::A4082Xatu),
                PlayedCard::from_id(CardId::B2097AlolanMuk),
            ],
            vec![PlayedCard::from_id(automatic_active)],
        );
        state.current_player = 0;
        state.turn_count = 3;
        state.decks[1].cards = vec![Card::Unknown];

        assert!(
            crate::actions::get_in_play_ability_mechanic(&state, state.get_active(1)).is_none(),
            "real Power of Alchemy must suppress the next player's Basic Ability"
        );

        let end = Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        };
        assert_eq!(
            crate::observation::hidden_continuation_reason(&state, &end),
            Some("automatic next-turn ability searches an unknown deck"),
            "suppression must not remove the conservative printed-ability guard for {automatic_active:?}"
        );
    }
}

#[test]
fn terminal_end_turn_does_not_apply_next_turn_deck_search() {
    for checkup_ko in [true, false] {
        let mut state = State::default();
        let mut xatu = PlayedCard::from_id(CardId::A4082Xatu);
        if checkup_ko {
            xatu = xatu.with_remaining_hp(10).with_status_condition(StatusCondition::Poisoned);
        }
        state.set_board(vec![xatu], vec![PlayedCard::from_id(CardId::B2070Meloetta)]);
        state.current_player = 0;
        state.turn_count = if checkup_ko { 3 } else { 30 };
        state.hands = [vec![], vec![]];
        let known_psychic = get_card_by_enum(CardId::A4081Natu);
        state.decks[1].cards = vec![known_psychic.clone()];
        let end = Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false };
        let branches = try_forecast_action(&state, &end).unwrap().into_branches();
        assert_eq!(branches.0, vec![1.0]);
        for mutation in branches.1 {
            let mut after = state.clone();
            mutation(&mut StdRng::seed_from_u64(103), &mut after, &end);
            assert_eq!(after.winner, Some(if checkup_ko { GameOutcome::Win(1) } else { GameOutcome::Tie }));
            assert_eq!(after.decks[1].cards, vec![known_psychic.clone()]);
            assert!(after.hands[1].is_empty(), "a terminal game must not run Strange Singing");
            if checkup_ko {
                assert_eq!(after.turn_count, 3);
                assert_eq!(after.current_player, 0);
            }
        }
    }
}
}

#[cfg(test)]
#[path = "terminal_win_distance_tests.rs"]
mod terminal_win_distance_tests;

#[cfg(test)]
#[path = "promotion_continuation_tests.rs"]
mod promotion_continuation_tests;
