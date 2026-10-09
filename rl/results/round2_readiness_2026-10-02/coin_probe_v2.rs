//! coin_probe v2 (the cloud, Oct 2; round-2 readiness, job 3). v1 is `../engine_switch_rules_2026-10/coin_probe.rs`, unchanged.
//! v2 counts plies as km3's and k3's own search does (`expectiminimax_player.rs` on the official engine, main-8626a35):
//!   - the root move costs a ply, whatever its frame (the root scores each move with max_depth - 1 more plies, 257-275);
//!   - a forced continuation costs none, whoever is to move (631-655): the top frame is exactly one EndTurn,
//!     ResolveKnockoutPoints, ResolveAttackRetaliation, ResolvePokemonCheckup, FinishPokemonCheckup or ResolveEndTurnEvolution,
//!     or the stack is empty with end_turn_pending; so the search crosses the forced end of the opponent's turn;
//!   - a free frame costs none (659-704): a pending Victory Star, Misty-target or Trainer coin choice, or a frame of only
//!     ApplyQueuedAttackDamage and ChooseRandomEvolutionTarget choices; nor does a promotion frame (707-748);
//!   - then the search stops where the bots stop: when the current player is not the mover (the hidden-hand guard, 750-774,
//!     where the k-tiers stop at the turn boundary) and when 3 plies are spent (depth 0);
//!   - every other move costs a ply, the opponent's forced choices during the mover's turn included (960-1010), and a voluntary
//!     EndTurn too (it is searched last).
//! A finite cut recorded by a move in a free frame is reported at the ply already spent (the move costs none). Everything else is
//! v1's: the conditions, the 12 chance samples per move, the node limit (60,000; `--node-limit N` sets another, for a search
//! that stops there) and the output format.
//! Built from this file and the counters' lines it includes (since Oct 9; the P2 paragraph below), in a scratch copy of the
//! engine: python3 ../coin_prevention_repair_2026-09-30/instrument_scan.py --emit-fns engine/examples/r2_counter_fns.rs &&
//! cp coin_probe_v2.rs engine/examples/ && (cd engine && cargo build --release --locked --features test-utils --example
//! coin_probe_v2). Oct 2's runs used the official engine (main-8626a35), before the include.
//!   coin_probe_v2 --a <list> --b <list> --seed-base <n> --pairing <n> --bot km3 --deal <i> --tick <t> [--node-limit <n>]
//!
//! P2's check (the cloud, Oct 9; claude/coin-prevention-round2): a third condition, RETURN, for rules switch 2's P2 (return
//! damage left by an attack takes Weakness). The probe must then be built on the candidate engine (the P2 head or later): on
//! main-8626a35 RETURN can never fire. QUEUED and CUT are unchanged.
//!   RETURN: a move the search applies runs the hit back of an attack's return damage (CardEffect::Counterattack: Cursed Jewel,
//!     Spike Armor, Bristling Spikes, Needle Lariat, Shell Trap) on a damaged opposing Active, and its forecast leaves a different
//!     board with the Attacking Pokemon's printed Weakness taken away. That is the exact counter "attack_return_weakness": the
//!     counter's own lines (`r2_tick` and its helpers, written out by `../coin_prevention_repair_2026-09-30/instrument_scan.py
//!     --emit-fns`, the text the script puts into legality_scan.rs) are included below, so the trace proves the condition the
//!     counter counts. It is asked of every move the search applies, at the ply the move is charged (the root's move 1, an
//!     ordinary move plies + 1, a forced or free move none: Psy Turbo's held-back hit back, resolved by the forced
//!     ResolveAttackRetaliation after the Attach chosen at ply 2, reads 2), and of the moves of a QUEUED frame (which is not
//!     expanded) at the ply they would be chosen. Only moves that can run the hit back are asked (Attack,
//!     ApplyQueuedAttackDamage, KeepAttackCoinResults, RerollAttackCoins, ApplyDamage from an attack,
//!     ResolveAttackRetaliation), and only while some Pokemon in play carries an attack's return damage. An attack never applied
//!     is never asked, so there is no leaf case.
//!   The code gate (the other half), read in the P2 engine (5543a4ba; line numbers at 35e6acfd): `handle_attack_retaliation`
//!     (actions/apply_action_helpers.rs:649-677) adds `attack_return_weakness_extra` (hooks/core.rs:1535, 20 when the
//!     Attacking Pokemon's printed Weakness is one of the holder's types) to the hit back when the switch is on, the Attacking
//!     Pokemon is Active (`attacking_ref.1 == 0`) and the target carries an attack's return damage
//!     (`attack_counterattack_damage`, hooks/counterattack.rs:34) (:658-663); a Tool's and an Ability's stay flat. It is
//!     reached from `handle_damage` (apply_action_helpers.rs:531; a queued or plain ApplyDamage, coin cut or not, through
//!     apply_action.rs:908), ResolveAttackRetaliation (apply_action.rs:627), forecast_apply_damage_after_coins' Guts / Perish
//!     Body coin branch (apply_action.rs:948) and an attack's immediate outcome (attack_outcome.rs:281); the bots' public reply
//!     (players/public_reply.rs:564) prices the opponent's attack, beyond this search.
//!   Output: a RETURN block as the others, and a last line `RESULT_P2 ret=<n|none>`. The RESULT line is unchanged (scripts read it with an end
//!     anchor: validate_v2.py and the switch-2 classify_8b.py for v2; coin_lookahead.py and classify_8c.py for v1's).
//!   Built on the candidate, in a scratch copy (git archive) of its engine:
//!     python3 ../coin_prevention_repair_2026-09-30/instrument_scan.py --emit-fns engine/examples/r2_counter_fns.rs
//!     cp coin_probe_v2.rs engine/examples/ && (cd engine && cargo build --release --locked --features test-utils --example coin_probe_v2)
//!   The self-test adds boards H-N; with P2 off (DECKGYM_FLAT_RETURN_DAMAGE=1) exactly the four with a return ply fail.
//!
//! v1's notes follow.
//! Step 8c of the rules switch, the coin repair's side (Oct 1; scratch, diagnosis only; no change in engine/). The counterpart of
//! `vs_probe.rs` (victory_star_repair_2026-09-30/smoke/rerun_R/): "in lookahead only" counts as an explanation of a changed game only
//! if both halves hold, the code gate (read in the code) and a trace showing the gate's condition inside the bot's search depth at
//! the game's first differing tick. This is the second half for repair B.
//!
//! Given a game, a deal and the first differing tick, it replays the game on R (the two engines agree up to that tick), then searches
//! the mover's own consecutive moves from there, up to kog3's depth of 3 plies, for repair B's conditions:
//!   QUEUED: a queued coin-path choice is offered: an ApplyQueuedAttackDamage at one of the five coin-Ability Pokemon (Bastiodon
//!     A2 114, Hisuian Goodra B3b 050, Togekiss A4 080, Meowth B2 124 / B2 204) whose attack's mechanic is not
//!     AlsoChoiceBenchDamage[Filtered] (which queued it on the old engine too). This is F5's `coin_queued_offered`.
//!   CUT: a finite heads cut is recorded: applying an Attack or a queued choice whose forecast has more branches than the same move
//!     with the Bastiodon or Goodra replaced by a Bulbasaur (the coin split ran for it). This is F5's `coin_cut_recorded`.
//! It prints, for each condition, the shortest path to it (as plies of the mover's own moves, the first move being ply 1) and says
//! whether that is inside the search: a state reached after p applied moves is in the tree if p <= 3; a move chosen at ply p is in
//! it if p <= 3. At p = 3 for QUEUED the state is the tree's last node, and whether the offered choice is priced there depends on
//! its frame. A frame made only of ApplyQueuedAttackDamage choices is a "pure" frame: the bots resolve it at once without
//! spending a ply ("a queued attack-damage target [is] part of the attack already being priced", expectiminimax_player.rs:659-673
//! and value_function_player.rs:93-110), so the choice is inside the search even at ply 3. A mixed frame (some plain ApplyDamage
//! beside the queued choice) is an ordinary move: at ply 3 it is offered at the leaf and never applied, the leaf's value does not
//! read it, and the output says "AT THE LEAF": the verdict then needs a judgment (PLAN.md: anything that does is Dustin's).
//! Chance is sampled (12 outcomes per move, from the probe's own seeded RNG; the game's is never touched), so a path found has
//! positive probability; one not found is not a proof of absence, and the output says so.
//!   coin_probe --a fire_heatmor.txt --b meowth_carefree.txt --seed-base 20950000000 --bot kog3 --deal 2 --tick 27
//!   coin_probe --selftest        (constructed boards with known answers; needs the test-utils feature)
//! Built as an example in a scratch copy of R's engine (git archive, never in the repository's tree), run from that copy's engine/:
//!   cp coin_probe.rs engine/examples/ && (cd engine && cargo build --release --locked --features test-utils --example coin_probe)
//! `coin_lookahead.py` (this folder) drives it over every changed game of a smoke and checks it against S3's hand-traced ticks.
use deckgym::actions::{try_forecast_action, Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::effects::CardEffect;
use deckgym::database::get_card_by_enum;
use deckgym::models::{Attack, Card, EnergyType, PlayedCard, StatusCondition, TrainerType};
use deckgym::players::{create_players, parse_player_code};
use deckgym::test_support::{get_initialized_game_with_board, get_test_game_with_board};
use deckgym::{Deck, Game, State};
use rand::{rngs::StdRng, SeedableRng};
use std::collections::BTreeMap;

// The exact counters' lines (P2's RETURN uses "attack_return_weakness"); every name in it starts with r2_.
include!("r2_counter_fns.rs");

const FINITE: [&str; 2] = ["A2 114", "B3b 050"];
const FULL: [&str; 3] = ["A4 080", "B2 124", "B2 204"];
const SEEDS: u64 = 12;
const SEARCH_PLIES: usize = 3;
const NODE_LIMIT: usize = 60_000;
/// The node limit in force: NODE_LIMIT (v1's), unless `--node-limit N` sets another.
static LIMIT: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(NODE_LIMIT);

fn limit() -> usize {
    LIMIT.load(std::sync::atomic::Ordering::Relaxed)
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn short(a: &Action) -> String {
    let s = format!("{:?}", a.action);
    if s.chars().count() > 90 { format!("{}...", s.chars().take(87).collect::<String>()) } else { s }
}

fn mechanic_of(attack: &deckgym::models::Attack) -> String {
    attack.effect.as_deref().and_then(|e| deckgym::actions::EFFECT_MECHANIC_MAP.get(e))
        .map(|m| format!("{m:?}").chars().take_while(|c| c.is_alphanumeric()).collect::<String>())
        .unwrap_or_default()
}

fn is_coin(state: &State, player: usize, idx: usize) -> bool {
    state.in_play_pokemon[player].get(idx).and_then(|p| p.as_ref())
        .is_some_and(|p| FINITE.contains(&p.card.get_id().as_str()) || FULL.contains(&p.card.get_id().as_str()))
}

/// Whether `a` is a queued coin-path choice at a coin Pokemon of `actor`'s opponent (F5's coin_queued_offered).
fn is_queued_coin(state: &State, actor: usize, a: &Action) -> bool {
    match &a.action {
        SimpleAction::ApplyQueuedAttackDamage { attack, targets } => {
            !mechanic_of(attack).starts_with("AlsoChoiceBenchDamage")
                && targets.iter().any(|(_, is_opp, i)| *is_opp && is_coin(state, 1 - actor, *i))
        }
        _ => false,
    }
}

/// The slots of `actor`'s opponent whose finite coin cut is recorded when `action` is chosen (F5's coin_cut_recorded).
fn finite_cut_slots(state: &State, action: &Action) -> Vec<usize> {
    let opp = 1 - action.actor;
    let branches = |s: &State| try_forecast_action(s, action).ok().map(|o| o.into_branches().0.len());
    let mut out = vec![];
    let Some(n_real) = branches(state) else { return out };
    for i in 0..state.in_play_pokemon[opp].len() {
        let Some(id) = state.in_play_pokemon[opp].get(i).and_then(|p| p.as_ref()).map(|p| p.card.get_id()) else { continue };
        if !FINITE.contains(&id.as_str()) {
            continue;
        }
        let mut without = state.clone();
        without.in_play_pokemon[opp][i] = Some(PlayedCard::from_id(CardId::A1001Bulbasaur));
        if branches(&without).is_some_and(|n| n < n_real) {
            out.push(i);
        }
    }
    out
}

/// P2's RETURN: applying `a` at `state` runs the hit back of an attack's return damage, and the Attacking Pokemon's printed
/// Weakness changes what it leaves (the exact counter "attack_return_weakness"). `actions` are the moves `state` offers.
fn hit_back_takes_weakness(state: &State, actions: &[Action], a: &Action) -> bool {
    matches!(a.action, SimpleAction::Attack(_)
        | SimpleAction::ApplyQueuedAttackDamage { .. }
        | SimpleAction::KeepAttackCoinResults
        | SimpleAction::RerollAttackCoins { .. }
        | SimpleAction::ApplyDamage { is_from_active_attack: true, .. }
        | SimpleAction::ResolveAttackRetaliation { .. })
        && state.in_play_pokemon.iter().flatten().flatten().any(|p| r2_attack_return(p) > 0)
        && r2_tick(state, actions, a, None).iter().any(|(name, _)| *name == "attack_return_weakness")
}

const RETURN_DETAIL: &str = "the hit back of an attack's return damage takes the Attacking Pokemon's Weakness";

/// States reached by `action` from `state`, one per sampled chance outcome, deduplicated by their serialised form.
fn successors(state: &State, action: &Action) -> Vec<State> {
    let mut seen = BTreeMap::new();
    for seed in 0..SEEDS {
        let Ok(outcomes) = try_forecast_action(state, action) else { return vec![] };
        let (probabilities, mutations) = outcomes.into_branches();
        for (p, mutate) in probabilities.iter().zip(mutations) {
            if *p <= 0.0 {
                continue;
            }
            let mut next = state.clone();
            mutate(&mut StdRng::seed_from_u64(1000 + seed), &mut next, action);
            seen.entry(serde_json::to_string(&next).unwrap_or_default()).or_insert(next);
        }
    }
    seen.into_values().collect()
}

type Example = (Vec<String>, String);
#[derive(Default)]
struct Found {
    /// kind -> ply -> up to three examples; the ply is the number of the mover's moves applied (QUEUED, the offered state's depth)
    /// or the move's own number (CUT, the move chosen at that ply).
    by_kind: BTreeMap<&'static str, BTreeMap<usize, Vec<Example>>>,
    /// The plies at which a QUEUED state was found whose frame is pure (every offered move is an ApplyQueuedAttackDamage or a
    /// ChooseRandomEvolutionTarget), which the bots resolve at once, without spending a ply.
    pure_plies: std::collections::BTreeSet<usize>,
    /// The least depth of a leaf (a node where the search stops) whose mover's Active faces two or more opposing Ariados.
    trapleaf: Option<usize>,
    nodes: usize,
    truncated: bool,
}

/// The bots' own test (expectiminimax_player.rs:663-673): the offered moves are all stack choices of these two kinds.
fn pure_queued_frame(actions: &[Action]) -> bool {
    !actions.is_empty()
        && actions.iter().all(|a| a.is_stack && matches!(a.action, SimpleAction::ApplyQueuedAttackDamage { .. } | SimpleAction::ChooseRandomEvolutionTarget { .. }))
}

/// The result of a probe: the shortest ply of each condition, and whether the shortest QUEUED frame is one the bots resolve at once.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Least {
    queued: Option<usize>,
    cut: Option<usize>,
    queued_free: bool,
    /// P2's condition (Oct 9): the ply of the first move found whose hit back takes Weakness.
    ret: Option<usize>,
    /// Round 2's conditions (Oct 9), in R2_KINDS' order: the least ply each was recorded at (4: just beyond the search).
    r2: [Option<usize>; 7],
    /// The least depth of a leaf of the search where the mover's Active faces two or more opposing Ariados.
    trapleaf: Option<usize>,
}

/// Round 2's kinds, in the RESULT_R2 line's order, with the field name each gets there.
const R2_KINDS: [(&str, &str); 7] =
    [("WILL", "will"), ("VS", "vs"), ("TRAP", "trap"), ("OWN", "own"), ("GUTS", "guts"), ("PLAIN", "plain"), ("PERISH", "perish")];

/// The attack each seat chose last, with the turn it chose it in (r2_tick's `last_attack`, read only in that turn).
type Last = [Option<(u8, Attack)>; 2];

impl Found {
    fn add(&mut self, kind: &'static str, ply: usize, path: &[String], detail: String) {
        let e = self.by_kind.entry(kind).or_default().entry(ply).or_default();
        if e.len() < 3 {
            e.push((path.to_vec(), detail));
        }
    }
}

/// The bots' forced-continuation test (expectiminimax_player.rs 631-645), read from the state (end_turn_pending through its
/// serialised form, the field being crate-private).
fn forced_continuation(state: &State) -> bool {
    state.turn_count > 0
        && match state.move_generation_stack.last() {
            Some((_, choices)) => matches!(choices.as_slice(), [SimpleAction::EndTurn
                | SimpleAction::ResolveKnockoutPoints { .. }
                | SimpleAction::ResolveAttackRetaliation { .. }
                | SimpleAction::ResolvePokemonCheckup
                | SimpleAction::FinishPokemonCheckup
                | SimpleAction::ResolveEndTurnEvolution { .. }]),
            None => serde_json::to_value(state).ok().and_then(|v| v.get("end_turn_pending").and_then(|b| b.as_bool()))
                .expect("State serialises end_turn_pending"),
        }
}

/// The bots' free frames (659-704): a pending coin choice, or a frame of only queued attack damage and random evolution targets.
fn free_frame(state: &State, actions: &[Action]) -> bool {
    state.pending_attack_coin_choice.is_some()
        || state.pending_misty_target_choice.is_some()
        || state.pending_trainer_coin_choice.is_some()
        || pure_queued_frame(actions)
}

/// The bots' promotion frame (`is_current_promotion_frame`, 204-235): the frame's player has an empty Active and every choice is
/// that player's Promote.
fn promotion_frame(state: &State, mover: usize, actions: &[Action]) -> bool {
    state.turn_count > 0
        && !state.setup_opponent_hidden
        && !actions.is_empty()
        && state.in_play_pokemon[mover][0].is_none()
        && actions.iter().all(|a| a.is_stack && matches!(a.action, SimpleAction::Promote { player, .. } if player == mover))
}

/// The actor's attacks chosen now whose own damage records a finite cut, at ply `ply`.
fn attack_cuts(state: &State, actions: &[Action], ply: usize, path: &[String], found: &mut Found) {
    if ply > SEARCH_PLIES {
        return;
    }
    for a in actions.iter().filter(|a| matches!(a.action, SimpleAction::Attack(_)) && !a.is_stack) {
        let slots = finite_cut_slots(state, a);
        if !slots.is_empty() {
            let mut p = path.to_vec();
            p.push(short(a));
            found.add("CUT", ply, &p, format!("the attack's own damage, finite cut at slot(s) {slots:?}"));
        }
    }
}

/// Every action, EndTurn last (a voluntary pass is searched, but after everything else, as v1 left it out).
fn ordered(actions: &[Action]) -> Vec<&Action> {
    let mut out: Vec<&Action> = actions.iter().filter(|a| !matches!(a.action, SimpleAction::EndTurn)).collect();
    out.extend(actions.iter().filter(|a| matches!(a.action, SimpleAction::EndTurn)));
    out
}

/// `plies`: the plies the bots have spent to reach `state`; `root`: the probed state itself (its every move costs a ply).
fn explore(state: &State, actor: usize, plies: usize, root: bool, path: &mut Vec<String>, found: &mut Found) {
    found.nodes += 1;
    if found.nodes > limit() {
        found.truncated = true;
        return;
    }
    if state.winner.is_some() {
        return;
    }
    let (mover, actions) = state.generate_possible_actions();
    if actions.is_empty() {
        return;
    }
    let pure = pure_queued_frame(&actions);
    // QUEUED: the actor's frame offers a queued coin-path choice, after `plies` plies.
    if mover == actor {
        let queued: Vec<&Action> = actions.iter().filter(|a| is_queued_coin(state, actor, a)).collect();
        if !queued.is_empty() {
            if pure {
                found.pure_plies.insert(plies);
            }
            found.add("QUEUED", plies, path, format!("offers {} ({})", queued.iter().map(|a| short(a)).collect::<Vec<_>>().join(" | "),
                if pure { "a pure frame: the bots resolve it without spending a ply" } else { "a mixed frame: an ordinary move" }));
            let cost = if pure && !root { 0 } else { 1 };
            if plies + cost <= SEARCH_PLIES {
                for a in &queued {
                    let slots = finite_cut_slots(state, a);
                    if !slots.is_empty() {
                        let mut p = path.clone();
                        p.push(short(a));
                        found.add("CUT", plies + cost, &p, format!("the queued choice's finite cut at slot(s) {slots:?}"));
                    }
                }
                // P2: the frame is not expanded, so its moves are asked here, at the ply they would be chosen.
                for a in ordered(&actions) {
                    if hit_back_takes_weakness(state, &actions, a) {
                        let mut p = path.clone();
                        p.push(if cost == 0 { format!("(free) {}", short(a)) } else { short(a) });
                        found.add("RETURN", plies + cost, &p, RETURN_DETAIL.to_string());
                    }
                }
            }
            return;
        }
    }
    let step = |a: &Action, next_plies: usize, label: String, path: &mut Vec<String>, found: &mut Found| {
        // P2: every move applied is asked, at the ply it is charged.
        if hit_back_takes_weakness(state, &actions, a) {
            path.push(label.clone());
            found.add("RETURN", next_plies, path, RETURN_DETAIL.to_string());
            path.pop();
        }
        for next in successors(state, a) {
            path.push(label.clone());
            explore(&next, actor, next_plies, false, path, found);
            path.pop();
        }
    };
    if root {
        if mover == actor {
            attack_cuts(state, &actions, plies + 1, path, found);
        }
        for a in ordered(&actions) {
            step(a, plies + 1, short(a), path, found);
        }
        return;
    }
    if forced_continuation(state) && actions.len() == 1 {
        if path.iter().filter(|m| m.starts_with("(free)")).count() < 16 {
            step(&actions[0], plies, format!("(free) {}", short(&actions[0])), path, found);
        }
        return;
    }
    if free_frame(state, &actions) || promotion_frame(state, mover, &actions) {
        if path.iter().filter(|m| m.starts_with("(free)")).count() < 16 {
            for a in ordered(&actions) {
                step(a, plies, format!("(free) {}", short(a)), path, found);
            }
        }
        return;
    }
    if state.current_player != actor || plies >= SEARCH_PLIES {
        return;
    }
    if mover == actor {
        attack_cuts(state, &actions, plies + 1, path, found);
    }
    for a in ordered(&actions) {
        step(a, plies + 1, short(a), path, found);
    }
}

/// Prints the result and returns the shortest ply of each condition, if any.
fn report(found: &Found, label: &str) -> Least {
    let mut least = Least { queued: None, cut: None, queued_free: false, ret: None, r2: [None; 7], trapleaf: found.trapleaf };
    for (kind, by_ply) in &found.by_kind {
        let ply = *by_ply.keys().next().unwrap();
        let r2 = R2_KINDS.iter().position(|(k, _)| k == kind);
        match (*kind, r2) {
            ("QUEUED", _) => {
                least.queued = Some(ply);
                least.queued_free = found.pure_plies.contains(&ply);
            }
            ("CUT", _) => least.cut = Some(ply),
            ("RETURN", _) => least.ret = Some(ply),
            (_, Some(i)) => least.r2[i] = Some(ply),
            (other, None) => unreachable!("{other}"),
        }
        let inside = if *kind == "QUEUED" && ply == SEARCH_PLIES && !found.pure_plies.contains(&ply) {
            "inside the tree but AT THE LEAF (a mixed frame: offered, never applied: a judgment)"
        } else if *kind == "QUEUED" && ply == SEARCH_PLIES {
            "INSIDE THE SEARCH (at the leaf, but a pure frame: resolved without a ply)"
        } else if ply <= SEARCH_PLIES { "INSIDE THE SEARCH" } else if r2.is_some() {
            "beyond the search (offered at a leaf, never applied)"
        } else { "beyond the search" };
        let what = match *kind {
            "QUEUED" => format!("a queued coin-path choice is offered after {ply} move(s)"),
            "CUT" => format!("a finite heads cut is recorded by the move chosen at ply {ply}"),
            "RETURN" => format!("the hit back of an attack's return damage takes Weakness (P2) in the move chosen at ply {ply}"),
            "WILL" => format!("Will's heads reaches a Confused attacker's or a block coin's attack (round 2) in the move chosen at ply {ply}"),
            "VS" => format!("Victory Star pauses after a block coin (round 2) in the move chosen at ply {ply}"),
            "TRAP" => format!("two Ariados' Trap Territory changes the moves offered or a move's outcome (round 2) in the move chosen at ply {ply}"),
            "OWN" => format!("a coin Ability on the attacker's own side splits its attack (round 2) in the move chosen at ply {ply}"),
            "GUTS" => format!("Guts on the attacker's own side splits its attack (round 2) in the move chosen at ply {ply}"),
            "PLAIN" => format!("a coin Ability splits an attack's plain damage choice (round 2) in the move chosen at ply {ply}"),
            _ => format!("Perish Body's coin is built by an attack's plain damage choice (round 2) in the move chosen at ply {ply}"),
        };
        println!("{label}{kind}: {what}: {inside}");
        for (path, detail) in by_ply.values().next().unwrap() {
            println!("    after [{}] {detail}", path.join(" ; "));
        }
    }
    if let Some(d) = found.trapleaf {
        println!("{label}TRAPLEAF: a leaf of the search at depth {d} scores the mover's Active facing two or more Ariados (its Retreat \
            Cost, read by the leaf's value, is one more than before; no counter sees it: a judgment)");
    }
    if found.by_kind.is_empty() {
        println!("{label}NOT FOUND: no queued coin-path choice, finite heads cut, hit back taking Weakness or round-2 condition (Will, \
            Victory Star, Trap Territory, own-side coin or Guts, plain-hit coin or Perish Body) within {SEARCH_PLIES} plies ({SEEDS} chance \
            samples per move; not a proof of absence)");
    }
    if found.truncated {
        println!("{label}(the search stopped at {} nodes)", limit());
    }
    least
}

/// The RESULT_R2 line's fields.
fn r2_fields(least: &Least) -> String {
    let show = |p: Option<usize>| p.map_or("none".to_string(), |p| p.to_string());
    let mut out: Vec<String> = R2_KINDS.iter().zip(least.r2).map(|((_, f), p)| format!("{f}={}", show(p))).collect();
    out.push(format!("trapleaf={}", show(least.trapleaf)));
    out.join(" ")
}

/// `last`: the attack each seat chose last (r2_tick's key), for a probe started inside a turn.
fn probe_state(state: &State, label: &str, last: &Last) -> Least {
    let (actor, offered) = state.generate_possible_actions();
    println!("{label}mover seat {actor}, turn {}; Active {}; {} offered moves", state.turn_count,
        state.maybe_get_active(actor).map_or("-".to_string(), |p| p.get_name()), offered.len());
    let mut found = Found::default();
    let _ = last; // (tests first: no round-2 detection yet)
    explore(state, actor, 0, true, &mut vec![], &mut found);
    report(&found, label)
}

/// No attack chosen yet in the probed turn.
const NO_LAST: Last = [None, None];

// The self-test's round-2 boards (Oct 9): these helpers are counter_probe_readiness.rs's (:34-45, :52-96, :123-157), copied.
fn attack_named(state: &State, title: &str) -> Action {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == title))
        .unwrap_or_else(|| panic!("{title} is not offered"))
}

fn offered(state: &State, pick: impl Fn(&SimpleAction) -> bool) -> Option<Action> {
    state.generate_possible_actions().1.into_iter().find(|a| pick(&a.action))
}

/// Player 1 uses `title` from `attacker` into `defenders` (with `hand` as its hand), choosing the copied attack `copy` when
/// one is offered and the largest discard whenever one is offered, until a frame of damage choices is offered to it with no
/// discard beside it; seeds are tried until one offers it. Returns that state and the last attack player 1 chose.
fn damage_frame(
    attacker: &[PlayedCard],
    defenders: &[PlayedCard],
    hand: &[CardId],
    title: &str,
    copy: Option<&str>,
) -> (State, Attack) {
    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(seed, 1, 5, defenders.to_vec(), attacker.to_vec());
        let mut state = game.get_state_clone();
        state.current_player = 1;
        state.hands[1] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        game.set_state(state.clone());
        let attack = attack_named(&state, title);
        let SimpleAction::Attack(mut last) = attack.action.clone() else { unreachable!() };
        game.apply_action(&attack);
        for _ in 0..5 {
            let state = game.get_state_clone();
            let (actor, choices) = state.generate_possible_actions();
            if actor != 1 || state.move_generation_stack.is_empty() {
                break;
            }
            if let Some(copied) = choices.iter().find(|a| matches!(&a.action, SimpleAction::Attack(x) if Some(x.title.as_str()) == copy)) {
                let SimpleAction::Attack(x) = &copied.action else { unreachable!() };
                last = x.clone();
                game.apply_action(&copied.clone());
                continue;
            }
            let size = |a: &&Action| match &a.action {
                SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } => in_play_idxs.len(),
                SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. } => cards.len(),
                _ => 0,
            };
            if let Some(discard) = choices.iter().filter(|a| size(a) > 0).max_by_key(size) {
                game.apply_action(&discard.clone());
                continue;
            }
            if choices.iter().any(|a| matches!(a.action, SimpleAction::ApplyDamage { .. } | SimpleAction::ApplyQueuedAttackDamage { .. })) {
                return (state, last);
            }
            game.apply_action(&choices[0].clone());
        }
    }
    panic!("{title}: no damage choices offered in 40 seeds");
}

fn mon(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id)
}

/// A Pokemon with `hp` HP and no damage.
fn sturdy(id: CardId, hp: u32) -> PlayedCard {
    PlayedCard::new(get_card_by_enum(id), 0, hp, vec![], false, vec![])
}

/// Player 0 plays Will (A4 156) from its hand.
fn play_will(game: &mut Game) {
    let will = get_card_by_enum(CardId::A4156Will);
    let Card::Trainer(trainer_card) = will.clone() else { unreachable!() };
    let mut state = game.get_state_clone();
    state.hands[0].push(will);
    game.set_state(state);
    game.apply_action(&Action { actor: 0, action: SimpleAction::Play { trainer_card }, is_stack: false });
}

/// Team Rocket's Moltres ex (Heat Charged: flip 3 coins) for player 0 against a 400-HP Mega Latios ex, with the gates asked.
fn moltres_game(seed: u64, confused: bool, block: bool, will: bool, victini: bool) -> Game<'static> {
    let mut attacker = PlayedCard::from_id(CardId::B4a007TeamRocketsMoltresEx).with_energy(vec![EnergyType::Fire]);
    if confused {
        attacker = attacker.with_status_condition(StatusCondition::Confused);
    }
    if block {
        attacker.add_effect(CardEffect::CoinFlipToBlockAttack, 1);
    }
    let bench = mon(if victini { CardId::B3025Victini } else { CardId::A1001Bulbasaur });
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![attacker, bench], vec![sturdy(CardId::PB024MegaLatiosEx, 400)]);
    if will {
        play_will(&mut game);
    }
    game
}

fn moltres_board(seed: u64, confused: bool, block: bool, will: bool, victini: bool) -> State {
    moltres_game(seed, confused, block, will, victini).get_state_clone()
}

fn selftest() {
    let mon = PlayedCard::from_id;
    // Every check runs and prints; the failures are counted and asserted at the end (so a failing run lists them all).
    let (checks, failures) = (std::cell::Cell::new(0), std::cell::Cell::new(0));
    let tally = |ok: bool| {
        checks.set(checks.get() + 1);
        failures.set(failures.get() + usize::from(!ok));
        if ok { "ok  " } else { "FAIL" }
    };
    // (queued, cut, return), and round 2's fields (Oct 9): the (kind, ply) of each that must be found and the trapleaf depth;
    // every other round-2 field must read none.
    let check_r2 = |name: &str, got: Least, want: (Option<usize>, Option<usize>, Option<usize>), r2: &[(&str, usize)], trapleaf: Option<usize>| {
        let mut wanted = Least { queued: want.0, cut: want.1, queued_free: false, ret: want.2, r2: [None; 7], trapleaf };
        for (kind, ply) in r2 {
            wanted.r2[R2_KINDS.iter().position(|(k, _)| k == kind).expect("a round-2 kind")] = Some(*ply);
        }
        let ok = (got.queued, got.cut, got.ret) == want && got.r2 == wanted.r2 && got.trapleaf == trapleaf;
        let mark = tally(ok);
        println!("{mark} {name}: queued {:?} (free {}), cut {:?}, return {:?}; {}{}", got.queued, got.queued_free, got.cut, got.ret,
            r2_fields(&got), if ok { String::new() } else { format!(" (wanted queued {:?}, cut {:?}, return {:?}; {})", want.0, want.1, want.2, r2_fields(&wanted)) });
    };
    // Boards A-N: every round-2 field none.
    let check = |name: &str, got: Least, want: (Option<usize>, Option<usize>, Option<usize>)| check_r2(name, got, want, &[], None);
    let frame = |name: &str, ok: bool| println!("{} {name}", tally(ok));
    let board = |attacker: PlayedCard, defenders: Vec<PlayedCard>| {
        let mut game = get_initialized_game_with_board(5, 1, 5, defenders, vec![attacker]);
        let mut state = game.get_state_clone();
        state.current_player = 1;
        game.set_state(state);
        game.get_state_clone()
    };
    // A: Fire Claws into Bastiodon's Active: the attack itself records the finite cut, chosen at ply 1; nothing is queued.
    let claws = PlayedCard::from_id(CardId::A1034Charmeleon).with_energy(vec![EnergyType::Fire; 3]);
    check("Fire Claws into Bastiodon", probe_state(&board(claws.clone(), vec![mon(CardId::A2114Bastiodon)]), "  A ", &NO_LAST), (None, Some(1), None));
    // B: Tongue Whip with Bastiodon on the Bench: the attack (ply 1) offers the queued choice at a state of depth 1, and choosing it
    // (ply 2) records the cut. A Togekiss on the Bench queues the same way and records no finite cut.
    let whip = || PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire]);
    let b = probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A2114Bastiodon)]), "  B ", &NO_LAST);
    check("Tongue Whip, Bastiodon on the Bench", b, (Some(1), Some(2), None));
    frame("B: the frame has a plain ApplyDamage beside the queued choice: a mixed frame", !b.queued_free);
    check("Tongue Whip, Togekiss on the Bench",
        probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A4080Togekiss)]), "  C ", &NO_LAST), (Some(1), None, None));
    // F: a lone Togekiss on the Bench: every choice of the frame is queued, a pure frame the bots resolve without a ply.
    let f = probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A4080Togekiss)]), "  F ", &NO_LAST);
    check("Tongue Whip, a lone Togekiss on the Bench (a pure frame)", f, (Some(1), None, None));
    frame("F: every choice is a queued one: a pure frame", f.queued_free);
    // G (v2): a lone Bastiodon on the Bench: a pure frame, whose queued choice costs no ply, so its finite cut is at ply 1 (v1: 2).
    let g = probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A2114Bastiodon)]), "  G ", &NO_LAST);
    check("Tongue Whip, a lone Bastiodon on the Bench (a pure frame: the cut costs no ply)", g, (Some(1), Some(1), None));
    frame("G: every choice is a queued one: a pure frame", g.queued_free);
    // D: nothing to find without a coin Pokemon.
    check("Tongue Whip, no coin Pokemon",
        probe_state(&board(whip(), vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur)]), "  D ", &NO_LAST), (None, None, None));
    // E: the queued choice already offered at the tick (the state after the attack): depth 0, the S3 pattern.
    let mut game = get_initialized_game_with_board(5, 1, 5,
        vec![mon(CardId::A1001Bulbasaur), mon(CardId::A1001Bulbasaur), mon(CardId::A4080Togekiss)], vec![whip()]);
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state.clone());
    let attack = state.generate_possible_actions().1.into_iter()
        .find(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == "Tongue Whip")).expect("Tongue Whip");
    game.apply_action(&attack);
    check("the state after Tongue Whip (the choice is on the table)", probe_state(&game.get_state_clone(), "  E ", &NO_LAST), (Some(0), None, None));

    // P2 (Oct 9): RETURN, the hit back of an attack's return damage taking Weakness, found in the search. Player 0 attacks from
    // its Active into player 1's Mega Sableye ex (Darkness) armed as Cursed Jewel leaves it (40 back), as
    // counter_probe_readiness.rs's boards. With P2 off (DECKGYM_FLAT_RETURN_DAMAGE=1) the four with a return ply fail.
    let with = |id: CardId, n: usize, energy: EnergyType| PlayedCard::from_id(id).with_energy(vec![energy; n]);
    let armed = |amount: u32| {
        let mut p = mon(CardId::B3b041MegaSableyeEx);
        p.add_effect(CardEffect::Counterattack { amount }, 1);
        p
    };
    let duel = |attacker: Vec<PlayedCard>, defender: PlayedCard| {
        get_initialized_game_with_board(0, 0, 5, attacker, vec![defender]).get_state_clone()
    };
    let houndstone = || with(CardId::B3a024Houndstone, 3, EnergyType::Psychic);
    // H: Spooky Shot (70) from Houndstone (Psychic, weak Darkness): the attack itself, chosen at ply 1, runs the hit back.
    check("Spooky Shot into an armed Mega Sableye ex (Houndstone weak to it)",
        probe_state(&duel(vec![houndstone()], armed(40)), "  H ", &NO_LAST), (None, None, Some(1)));
    // I: Espeon's Hypnoblast (40), one Energy.
    check("Hypnoblast into an armed Mega Sableye ex (Espeon weak to it)",
        probe_state(&duel(vec![with(CardId::B3a020Espeon, 1, EnergyType::Psychic)], armed(40)), "  I ", &NO_LAST), (None, None, Some(1)));
    // J: Psy Turbo holds the hit back until its Attach is chosen (ply 2); the ResolveAttackRetaliation after it is forced (free).
    check("Psy Turbo into an armed Mega Sableye ex, Ralts on the Bench (the held-back hit back)",
        probe_state(&duel(vec![with(CardId::B2065Gardevoir, 2, EnergyType::Psychic), mon(CardId::A1130Ralts)], armed(40)), "  J ", &NO_LAST),
        (None, None, Some(2)));
    // K: Snorlax (weak Fighting): the hit back lands flat, as before P2.
    check("Rollout into an armed Mega Sableye ex (Snorlax not weak to it)",
        probe_state(&duel(vec![with(CardId::A1211Snorlax, 4, EnergyType::Colorless)], armed(40)), "  K ", &NO_LAST), (None, None, None));
    // L: Houndstone at 30 HP is Knocked Out by the 40 either way: the same board.
    check("Spooky Shot into an armed Mega Sableye ex, Houndstone at 30 HP (Knocked Out either way)",
        probe_state(&duel(vec![houndstone().with_remaining_hp(30)], armed(40)), "  L ", &NO_LAST), (None, None, None));
    // M: at 50 HP the 40 leaves it 10 and the 60 Knocks it Out.
    check("Spooky Shot into an armed Mega Sableye ex, Houndstone at 50 HP",
        probe_state(&duel(vec![houndstone().with_remaining_hp(50)], armed(40)), "  M ", &NO_LAST), (None, None, Some(1)));
    // N: nothing armed: no hit back.
    check("Spooky Shot into an unarmed Mega Sableye ex",
        probe_state(&duel(vec![houndstone()], mon(CardId::B3b041MegaSableyeEx)), "  N ", &NO_LAST), (None, None, None));
    // Round 2 (Oct 9): the round-2 package's conditions, on counter_probe_readiness.rs's boards (its line numbers cited; helpers
    // copied from it). Each lists only the round-2 fields it must find; every other one, QUEUED, CUT and RETURN included, none.
    let none = (None, None, None);
    // The gate coins: Team Rocket's Moltres ex's Heat Charged (3 coins) for player 0 against a 400-HP Mega Latios ex (:270-285). The
    // probe's root move is the Attack CPR verified, so the chosen counters read ply 1.
    for (label, confused, block, will, victini, want) in [
        ("Confused, Will pending", true, false, true, false, vec![("WILL", 1)]),
        ("Confused, Will pending, Victini (WILL, not VS: no block coin)", true, false, true, true, vec![("WILL", 1)]),
        ("Confused, no Will", true, false, false, false, vec![]),
        ("Confused, no Will, Victini", true, false, false, true, vec![]),
        ("a block coin, Will pending", false, true, true, false, vec![("WILL", 1)]),
        ("a block coin, Will pending, Confused", true, true, true, false, vec![("WILL", 1)]),
        ("a block coin, no Will", false, true, false, false, vec![]),
        ("a block coin, no Will, Victini", false, true, false, true, vec![("VS", 1)]),
        ("a block coin, Will pending, Victini", false, true, true, true, vec![("WILL", 1), ("VS", 1)]),
        ("no gate coin, Victini", false, false, false, true, vec![]),
        ("no gate coin, Will pending", false, false, true, false, vec![]),
    ] {
        check_r2(&format!("Heat Charged, {label}"), probe_state(&moltres_board(0, confused, block, will, victini), "  O ", &NO_LAST),
            none, &want, None);
    }
    // The Victory Star pause after a block coin's heads (:287-294), probed at the pause: Keep or Reroll offered at the root.
    let paused = (0..40u64).find_map(|seed| {
        let mut game = moltres_game(seed, false, true, false, true);
        let attack = attack_named(&game.get_state_clone(), "Heat Charged");
        game.apply_action(&attack);
        let after = game.get_state_clone();
        after.pending_attack_coin_choice.is_some().then_some(after)
    }).expect("a block coin heads in 40 seeds");
    check_r2("the Victory Star choice after a block coin's heads", probe_state(&paused, "  P ", &NO_LAST), none, &[("VS", 1)], None);
    // Trap Territory, the moves offered (:297-311): player 0's Active Bulbasaur against player 1's Ariados. With two, the root's
    // offer changes (2 Energy: Retreat is offered only on the old count) or Retreat's outcome does (4 Energy: 3 Grass discarded,
    // not 2; brief pitfall 3); either way the leaf at the turn boundary (depth 1) scores the Active facing them. One: nothing.
    for (label, energy, ariados, want, leaf) in [
        ("2 Energy, two Ariados", 2, 2, vec![("TRAP", 1)], Some(1)),
        ("4 Energy, two Ariados", 4, 2, vec![("TRAP", 1)], Some(1)),
        ("2 Energy, one Ariados", 2, 1, vec![], None),
    ] {
        let mut opponent = vec![mon(CardId::A1001Bulbasaur)];
        opponent.extend((0..ariados).map(|_| mon(CardId::B1a006Ariados)));
        let state = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass; energy]), mon(CardId::A1053Squirtle)], opponent)
            .get_state_clone();
        check_r2(&format!("Bulbasaur against Ariados, {label}"), probe_state(&state, "  T ", &NO_LAST), none, &want, leaf);
    }
    // The outcome (:312-317): Whimsicott ex's Grass Knot (160 with two Ariados, 130 with one) into Charizard ex. The holder's own
    // leaves don't read Trap Territory (its Active faces none): no trapleaf.
    for (ariados, want) in [(2, vec![("TRAP", 1)]), (1, vec![])] {
        let mut attacker = vec![PlayedCard::from_id(CardId::B1016WhimsicottEx).with_energy(vec![EnergyType::Grass; 2])];
        attacker.extend((0..ariados).map(|_| mon(CardId::B1a006Ariados)));
        let state = get_test_game_with_board(attacker, vec![mon(CardId::A1036CharizardEx)]).get_state_clone();
        check_r2(&format!("Grass Knot into Charizard ex, {ariados} Ariados"), probe_state(&state, "  K ", &NO_LAST), none, &want, None);
    }
    // An attack's own outcome (:249-265): Whiscash's Earthquake (10 to each of its own Benched Pokemon).
    let whiscash = || PlayedCard::from_id(CardId::A3b039Whiscash).with_energy(vec![EnergyType::Fighting; 4]);
    for (label, bench, defender, want) in [
        ("its own Benched Meowth", mon(CardId::B2124Meowth), mon(CardId::A1036CharizardEx), vec![("OWN", 1)]),
        ("its own Benched Bulbasaur", mon(CardId::A1001Bulbasaur), mon(CardId::A1036CharizardEx), vec![]),
        ("its own Benched Ursaluna at 10 HP", mon(CardId::B3b058Ursaluna).with_remaining_hp(10), mon(CardId::A1036CharizardEx),
            vec![("GUTS", 1)]),
        ("its own Benched Ursaluna at 160 HP", mon(CardId::B3b058Ursaluna), mon(CardId::A1036CharizardEx), vec![]),
        ("into the opponent's Active Ursaluna at 10 HP (off the gate)", mon(CardId::A1001Bulbasaur),
            mon(CardId::B3b058Ursaluna).with_remaining_hp(10), vec![]),
    ] {
        let state = get_initialized_game_with_board(0, 0, 3, vec![whiscash(), bench], vec![defender]).get_state_clone();
        check_r2(&format!("Earthquake, {label}"), probe_state(&state, "  Q ", &NO_LAST), none, &want, None);
    }
    // The plain-hit coins, the frame state (the damage choice on the table; r2_tick's key, the attack chosen last, passed in):
    // Zapdos's Raging Thunder (:214-223), Ditto's copied Chase Order (:224-233), Vespiquen ex's Chase Order with the discard into
    // an 80-HP Galarian Cursola, which it Knocks Out (:235-247).
    let at_frame = |(state, last): (State, Attack), label: &str| {
        let turn = state.turn_count;
        probe_state(&state, label, &[None, Some((turn, last))])
    };
    let bulbasaur = || mon(CardId::A1001Bulbasaur);
    let zapdos = vec![PlayedCard::from_id(CardId::A1103Zapdos).with_energy(vec![EnergyType::Lightning; 3]), bulbasaur()];
    for (defender, want) in [(CardId::B2124Meowth, vec![("PLAIN", 1)]), (CardId::A1001Bulbasaur, vec![])] {
        check_r2(&format!("Raging Thunder into an Active {defender:?}, the frame state"),
            at_frame(damage_frame(&zapdos, &[mon(defender)], &[], "Raging Thunder", None), "  Z "), none, &want, None);
    }
    let ditto = vec![PlayedCard::from_id(CardId::A1205Ditto).with_energy(vec![EnergyType::Grass; 2]), bulbasaur()];
    for (defender, want) in [(CardId::B2124Meowth, vec![("PLAIN", 1)]), (CardId::A1001Bulbasaur, vec![])] {
        check_r2(&format!("a copied Chase Order (Copy Anything) into an Active {defender:?}, the frame state"),
            at_frame(damage_frame(&ditto, &[mon(defender), mon(CardId::B4011VespiquenEx)], &[], "Copy Anything", Some("Chase Order")), "  Y "),
            none, &want, None);
    }
    let vespiquen = vec![PlayedCard::from_id(CardId::B4011VespiquenEx).with_energy(vec![EnergyType::Grass; 2]), bulbasaur(), bulbasaur()];
    for (cursola, want) in [(mon(CardId::A4a035GalarianCursola), vec![("PERISH", 1)]), (sturdy(CardId::A4a035GalarianCursola, 400), vec![])] {
        let hp = cursola.get_remaining_hp();
        check_r2(&format!("Chase Order with the discard into an Active Galarian Cursola, {hp} HP, the frame state"),
            at_frame(damage_frame(&vespiquen, &[cursola, mon(CardId::A1033Charmander)], &[], "Chase Order", None), "  V "), none, &want, None);
    }
    // One or more plies deep (the brief's predictions). Before the attack, as damage_frame builds it (player 1, an empty hand):
    // Raging Thunder is ply 1 and its single damage choice, an ordinary costed frame, ply 2.
    let before_attack = |attacker: &[PlayedCard], defenders: &[PlayedCard]| {
        let mut state = get_initialized_game_with_board(0, 1, 5, defenders.to_vec(), attacker.to_vec()).get_state_clone();
        state.current_player = 1;
        state.hands[1] = vec![];
        state
    };
    check_r2("Raging Thunder into an Active Meowth, before the attack",
        probe_state(&before_attack(&zapdos, &[mon(CardId::B2124Meowth)]), "  Z2 ", &NO_LAST), none, &[("PLAIN", 2)], None);
    // Chase Order: the Attack 1; the frame {ApplyDamage 70, discard, discard}: the discard 2 (the 70 doesn't Knock Out the 80-HP
    // Cursola); the 140 ApplyDamage 3.
    check_r2("Chase Order into an Active 80-HP Galarian Cursola, before the attack",
        probe_state(&before_attack(&vespiquen, &[mon(CardId::A4a035GalarianCursola), mon(CardId::A1033Charmander)]), "  V2 ", &NO_LAST),
        none, &[("PERISH", 3)], None);
    // Will in hand, not played (Play Will 1, Heat Charged 2), on the Confused Moltres; Victini in hand (Place 1, the attack 2) with
    // the block coin. Without the card in hand they are the boards "Confused, no Will" and "a block coin, no Will" above.
    let mut state = moltres_board(0, true, false, false, false);
    state.hands[0].push(get_card_by_enum(CardId::A4156Will));
    check_r2("Heat Charged, Confused, Will in hand", probe_state(&state, "  W2 ", &NO_LAST), none, &[("WILL", 2)], None);
    let mut state = moltres_board(0, false, true, false, false);
    state.hands[0].push(get_card_by_enum(CardId::B3025Victini));
    check_r2("Heat Charged, a block coin, Victini in hand", probe_state(&state, "  S2 ", &NO_LAST), none, &[("VS", 2)], None);
    println!("selftest: {} checks and {} frame checks, {} failures", checks.get() - 3, 3, failures.get());
    assert_eq!(failures.get(), 0, "selftest failures");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a == "--selftest") {
        return selftest();
    }
    let deck_a = Deck::from_file(&arg(&args, "--a").expect("--a")).expect("deck a");
    let deck_b = Deck::from_file(&arg(&args, "--b").expect("--b")).expect("deck b");
    let seed_base: u64 = arg(&args, "--seed-base").expect("--seed-base").parse().unwrap();
    let pairing: u64 = arg(&args, "--pairing").map(|x| x.parse().unwrap()).unwrap_or(0);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kog3".into());
    let i: u64 = arg(&args, "--deal").expect("--deal").parse().unwrap();
    let tick: usize = arg(&args, "--tick").expect("--tick").parse().unwrap();
    if let Some(n) = arg(&args, "--node-limit") {
        LIMIT.store(n.parse().unwrap(), std::sync::atomic::Ordering::Relaxed);
    }
    let seed = seed_base + pairing * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (&deck_a, &deck_b) } else { (&deck_b, &deck_a) };
    let code = || parse_player_code(&bot).unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![code(), code()]), seed);
    // The attack each seat chose last, with its turn (the scan's r2_last: any chosen Attack, a copied one included).
    let mut last: Last = [None, None];
    for _ in 0..tick {
        assert!(!game.is_game_over(), "the game ended before tick {tick}");
        let turn = game.get_state_clone().turn_count;
        let chosen = game.play_tick();
        if let SimpleAction::Attack(x) = &chosen.action {
            last[chosen.actor] = Some((turn, x.clone()));
        }
    }
    println!("deal {i}, tick {tick}:");
    let least = probe_state(&game.get_state_clone(), "  ", &last);
    let show = |p: Option<usize>| p.map_or("none".to_string(), |p| p.to_string());
    println!("RESULT queued={} cut={} free={}", show(least.queued), show(least.cut), least.queued_free);
    println!("RESULT_P2 ret={}", show(least.ret));
    println!("RESULT_R2 {}", r2_fields(&least));
}
