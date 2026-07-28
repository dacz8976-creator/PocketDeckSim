use log::{trace, LevelFilter};
use rand::rngs::StdRng;
use std::fmt::Debug;
use std::fmt::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::vec;

use crate::actions::{forecast_action, Action, SimpleAction};
use crate::{Deck, State};

use super::Player;

// Type alias for value functions
// Takes a state and player index, returns a score
// Using Box<dyn Fn> to allow closures with captured variables
pub type ValueFunction = Box<dyn Fn(&State, usize) -> f64>;

struct DebugStateNode {
    acting_player: usize,
    children: Vec<DebugActionNode>,
    proba: f64,
    value: f64,
}

struct DebugActionNode {
    action: Action,
    children: Vec<DebugStateNode>,
    value: f64,
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
    if action.is_stack {
        return true;
    }
    matches!(
        action.action,
        SimpleAction::Attack(_)
            | SimpleAction::Retreat(_)
            | SimpleAction::UseAbility { .. }
            | SimpleAction::EndTurn
            | SimpleAction::DrawCard { .. }
            | SimpleAction::Attach {
                is_turn_energy: true,
                ..
            }
    )
}

impl Player for ExpectiMiniMaxPlayer {
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        state: &State,
        possible_actions: &[Action],
    ) -> Action {
        let myself = possible_actions[0].actor;

        // Create a tree for debugging purposes
        let mut root = DebugStateNode {
            acting_player: myself,
            children: vec![],
            proba: 1.0,
            value: 0.0,
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
            let (score, action_node) = expected_value_function(
                rng,
                state,
                action,
                self.max_depth - 1,
                self.opponent_ply,
                false,
                self.flags(),
                myself,
                &self.value_function,
            );
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
            .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
            .map(|(idx, score)| (idx, *score))
            .unwrap();
        root.value = best_score;
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

    fn get_deck(&self) -> Deck {
        self.deck.clone()
    }
}

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
    let indent = "\t".repeat(10 - depth.min(10));
    trace!("{indent}E({myself}) depth left: {depth} action: {action:?}");

    let (probabilities, mutations) = forecast_action(state, action).into_branches();
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
    };
    for (prob, outcome) in probabilities.iter().zip(outcomes.iter()) {
        let (score, mut state_node) = expectiminimax(
            rng,
            outcome,
            depth,
            opp_budget,
            opp_entered,
            flags,
            myself,
            value_function,
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
    trace!("{indent}E({myself}) action: {action:?} score: {score}");
    (score, action_node)
}

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
    let static_eval = || {
        let score = value_function(state, myself);
        (
            score,
            DebugStateNode {
                acting_player: state.current_player,
                children: vec![],
                proba: 1.0,
                value: score,
            },
        )
    };

    if state.is_game_over() {
        super::s42_probe::LEAF_AFTER_OPP_PLY.fetch_add(usize::from(opp_entered), Ordering::Relaxed);
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
                            opponent_ply_node(
                                rng,
                                outcome,
                                depth,
                                opp_budget,
                                flags,
                                myself,
                                value_function,
                            )
                            .0
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
        return opponent_ply_node(rng, state, depth, opp_budget, flags, myself, value_function);
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
            let (score, action_node) = expected_value_function(
                rng,
                state,
                action,
                depth - 1,
                opp_budget,
                opp_entered,
                flags,
                myself,
                value_function,
            );
            scores.push(score);
            children.push(action_node);
        }
        let best_score = scores.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let state_node = DebugStateNode {
            acting_player: actor,
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
            let (score, action_node) = expected_value_function(
                rng,
                state,
                action,
                depth - 1,
                opp_budget,
                opp_entered,
                flags,
                myself,
                value_function,
            );
            scores.push(score);
            children.push(action_node);
        }
        let best_score = scores.iter().cloned().fold(f64::INFINITY, f64::min);
        let state_node = DebugStateNode {
            acting_player: actor,
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
            },
        );
    }

    OPPONENT_PLY_BRANCHES.fetch_add(public.len(), Ordering::Relaxed);
    let mut scores: Vec<f64> = Vec::with_capacity(public.len());
    let mut children: Vec<DebugActionNode> = Vec::new();
    for action in public.iter() {
        let (score, action_node) = expected_value_function(
            rng,
            state,
            action,
            depth,
            opp_budget - 1,
            true,
            flags,
            myself,
            value_function,
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

#[cfg(test)]
mod public_information_filter_tests {
    use super::*;
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::models::{Card, EnergyType, TrainerCard};

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

    /// Forced continuations of an already-made choice must survive the filter, or the search
    /// strands itself mid-resolution and returns an infinity.
    #[test]
    fn test_stack_actions_always_survive() {
        let mut stacked = act(SimpleAction::Play {
            trainer_card: a_trainer(),
        });
        assert!(!is_public_information_action(&stacked));
        stacked.is_stack = true;
        assert!(
            is_public_information_action(&stacked),
            "stack actions are forced continuations and must not be filtered out"
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

        // Define the action node (neutral color)
        writeln!(
            dot,
            "    a{} [label=\"P{} {}\\n{:?}\\nValue: {:.3}\", shape=ellipse, style=filled, fillcolor=lightgrey];",
            action_id,
            action_node.action.actor,
            action_node.action.is_stack,
            action_node.action.action,
            action_node.value
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
