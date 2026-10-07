//! Gate 2 of the Tool-placement rule (Oct 6; rl/results/playout_tool_rule_2026-10-06/README.md): at each position, every
//! move kx3 would consider (its candidates, cap included) played out `--rounds` times from the same sampled worlds and
//! seeds as kx3's `evaluate`, with the rule off and on (`PlayoutPlayer::tool_rule_study`, LAB). Per move: both means, the
//! paired difference (on - off) with its 95% interval, and the rounds the rule acted in; per position: kx3's choice
//! both ways (its own rule: the best mean, km3's move kept unless the lead exceeds z standard errors).
//!   playout_tool_rule --positions <positions.json> --rounds 128 --out results.jsonl [--resume]
//! positions.json: [{"id", "state": <state file>, "deck": <the pilot's list>, "opponent": <the opponent's list>, "seed"}];
//! the pilot is the side to move. `--resume` skips positions already in `--out`.
//!   playout_tool_rule --tie-break --positions <positions.json> --rounds 64 --out results.jsonl [--resume]
//! Gate 2 of the tie-break at kx3's own decision (Oct 6, the amended follow-up). A position with a "tool" is first advanced
//! by playing that Tool (km3's move there), so the decision studied is its placement. There: kx3's pool with `_tools` off
//! and on (the same: nothing leaves it), every placement played out `--rounds` times with the play-out rule off and on (as
//! above), and kx3's choice three ways: `_tools` off (the rule off), the play-out rule alone, and `_tools` on (the rule on,
//! then the tie-break: when nothing clears the bar and km3's placement has no effect now while another has one, km3's
//! preferred placement with an effect, unless km3's leads it beyond the noise); the paired difference of `_tools` on's
//! choice over off's, round by round. A position without a "tool" is not a placement: only its pool and decision rule are
//! compared, on and off.
//!   playout_tool_rule --no-effect --positions <positions.json> --rounds 64 --out results.jsonl [--resume]
//! Gate 2 of the no-effect tie-break (Oct 6, quiz 4, item 2) at the same positions, each as stored (the decision before
//! any Tool is played): whether km3's move and each candidate can do anything now by its printed text (`effect_now`), and
//! kx3's decision with `_noeffect` off and on (one round shows where the tie-break points; nothing else differs, since the
//! rule changes no play-out). Where km3's move can do nothing, every candidate is played out `--rounds` times (km3's
//! continuation, the same worlds and seeds as `evaluate`) and both choices are compared round by round.
//!   playout_tool_rule --extension --positions <positions.json> --seeds 4 --max-rounds 64 [--combined] --out results.jsonl [--resume]
//! (Oct 7) The close-call extension's cost and effect: at each position as stored, and (with a "tool") advanced to its
//! placement, for each of `--seeds` decision seeds (the position's seed + 10,000 s), kx3 decides with R = 16 (LAB, cap 12,
//! z 2) and with `_m<max-rounds>`; with `--combined`, both with the Tool rule and the skip bar 3 (`_tools_zs3`). Per
//! decision: both codes, choices and reasons, the time each took, and the rounds each candidate played with the extension.
//!   playout_tool_rule --list-tools
//! prints every Tool of the card database (one per distinct text) with the conditions the rule reads from its text.
//!   playout_tool_rule --list-effects
//! (Oct 6, quiz 4, item 2) prints every Item, Supporter and Stadium text and every Ability text of the card database
//! (one per distinct text; Abilities named "X's T") with what the no-effect reader needs before it can do anything:
//! "always", the needs (any one of them is enough), or why it isn't read; and whether the text can be a move.
use std::collections::BTreeSet;
use std::io::Write;

use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::Card;
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::actions::SimpleAction;
use deckgym::players::playout_player::{
    action_card, effect_needs, effect_now, kept_by_playouts, placements_with_effect, tool_conditions, Knowledge, Plan, PlayoutParams,
    PlayoutPlayer, Reading,
};
use deckgym::players::{create_players, PlayerCode};
use deckgym::Game;
use strum::IntoEnumIterator;
use deckgym::{Deck, State};
use rand::{rngs::StdRng, SeedableRng};
use serde_json::{json, Value};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn stats(xs: &[f64]) -> (f64, f64) {
    let n = xs.len() as f64;
    let m = xs.iter().sum::<f64>() / n;
    let se = if xs.len() < 2 { f64::INFINITY } else { (xs.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (n - 1.0)).sqrt() / n.sqrt() };
    (m, se)
}

/// kx3's choice from per-round scores (candidate 0 is km3's move): the best mean (km3's first on a tie, then the order
/// offered) replaces km3's only if its paired lead exceeds z standard errors.
fn choice(scores: &[Vec<f64>], z: f64) -> usize {
    let means: Vec<f64> = scores.iter().map(|s| s.iter().sum::<f64>() / s.len() as f64).collect();
    let best = (0..means.len()).fold(0, |b, c| if means[c] > means[b] { c } else { b });
    if best == 0 {
        return 0;
    }
    let diffs: Vec<f64> = scores[best].iter().zip(&scores[0]).map(|(a, b)| a - b).collect();
    let (d, se) = stats(&diffs);
    if d > 0.0 && d > z * se { best } else { 0 }
}

/// Gate 2 of the tie-break (see the header).
fn tie_break_gate(args: &[String]) {
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(args, "--positions").unwrap()).unwrap()).unwrap();
    let rounds: usize = arg(args, "--rounds").map_or(64, |r| r.parse().unwrap());
    let out_path = arg(args, "--out").unwrap();
    let done: BTreeSet<String> = if args.iter().any(|a| a == "--resume") {
        std::fs::read_to_string(&out_path)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter_map(|v| v["id"].as_str().map(String::from))
            .collect()
    } else {
        BTreeSet::new()
    };
    let mut out = std::fs::OpenOptions::new().create(true).append(true).open(&out_path).unwrap();
    for p in &positions {
        let id = p["id"].as_str().unwrap().to_string();
        if done.contains(&id) {
            continue;
        }
        let mut state: State = serde_json::from_str(&std::fs::read_to_string(p["state"].as_str().unwrap()).unwrap()).unwrap();
        let deck = Deck::from_file(p["deck"].as_str().unwrap()).unwrap();
        let opponent = Deck::from_file(p["opponent"].as_str().unwrap()).unwrap();
        let seed = p["seed"].as_u64().unwrap();
        let tool = p["tool"].as_str();
        if let Some(name) = tool {
            // Play the Tool (km3's move at the position), so the decision is its placement.
            let (me, legal) = state.generate_possible_actions();
            let play = legal
                .iter()
                .find(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == name))
                .unwrap_or_else(|| panic!("{id}: {name} can't be played"))
                .clone();
            let (d0, d1) = if me == 0 { (deck.clone(), opponent.clone()) } else { (opponent.clone(), deck.clone()) };
            let km = PlayerCode::KM { max_depth: 3 };
            let mut game = Game::from_state(state, create_players(d0, d1, vec![km.clone(), km]), seed);
            game.apply_action(&play);
            state = game.get_state_clone();
        }
        let (me, actions) = state.generate_possible_actions();
        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
        let pilot = |tools: bool| {
            let params = PlayoutParams { rollouts: 1, cap: 12, z: 2.0, knowledge: Knowledge::Lab, tools, ..PlayoutParams::new(3) };
            PlayoutPlayer::with_extra_lists(deck.clone(), opponent.clone(), params, Vec::new())
        };
        let pool_off = pilot(false).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let pool_on = pilot(true).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let off_moves: Vec<_> = pool_off.candidates.iter().map(|c| c.action.clone()).collect();
        let on_moves: Vec<_> = pool_on.candidates.iter().map(|c| c.action.clone()).collect();
        let effective = placements_with_effect(&state, &actions);
        // With one round nothing clears the bar, so `_tools` on shows the tie-break's placement, if it applies.
        let tie_target = pool_on
            .reason
            .starts_with("tie-break")
            .then(|| off_moves.iter().position(|a| *a == pool_on.candidates[pool_on.chosen].action).unwrap());
        let base = json!({"id": id, "seed": seed, "placement": tool.is_some(), "tool": tool, "turn": state.turn_count,
                          "pool": off_moves.iter().map(|a| format!("{:?}", a.action)).collect::<Vec<_>>(),
                          "pool_unchanged": off_moves == on_moves && pool_on.dropped.len() == pool_off.dropped.len(),
                          "km_proposal_has_effect": effective.contains(&off_moves[0]), "placements_with_effect": effective.len(),
                          "tie_break_applies": tie_target.is_some(), "tie_break_target": tie_target.map(|t| format!("{:?}", off_moves[t].action))});
        if tool.is_none() {
            writeln!(out, "{base}").unwrap();
            println!("{id}: not a placement; pool with _tools on {}, tie-break {}", if base["pool_unchanged"] == json!(true) { "unchanged" } else { "CHANGED" },
                     if tie_target.is_some() { "APPLIES" } else { "doesn't apply" });
            continue;
        }
        let study = pilot(true).tool_rule_study(&mut StdRng::seed_from_u64(seed), &observation, &off_moves, rounds);
        let off: Vec<Vec<f64>> = study.moves.iter().map(|m| m.off.iter().map(|o| o.score).collect()).collect();
        let on: Vec<Vec<f64>> = study.moves.iter().map(|m| m.on.iter().map(|o| o.score).collect()).collect();
        let c_off = choice(&off, 2.0);
        let c_rule = choice(&on, 2.0);
        // `_tools` on: the play-out rule's choice; if it is km3's move and the tie-break applies, the placement with an effect
        // km3 prefers, unless km3's leads it beyond the noise (as `evaluate` decides).
        let km_lead = tie_target.map(|t| {
            let d: Vec<f64> = on[0].iter().zip(&on[t]).map(|(k, e)| k - e).collect();
            stats(&d)
        });
        let kept = km_lead.is_some_and(|(m, se)| kept_by_playouts(-m, se, 2.0));
        let c_on = match tie_target {
            Some(t) if c_rule == 0 && !kept => t,
            _ => c_rule,
        };
        let paired = |a: &[f64], b: &[f64]| {
            let d: Vec<f64> = a.iter().zip(b).map(|(x, y)| x - y).collect();
            let (m, se) = stats(&d);
            json!({"mean": m, "lo": m - 1.96 * se, "hi": m + 1.96 * se})
        };
        let mut line = base.clone();
        line["rounds"] = json!(study.rounds);
        line["failed_rounds"] = json!(study.failed_rounds);
        line["ms"] = json!(study.millis.round());
        line["moves"] = json!(study
            .moves
            .iter()
            .enumerate()
            .map(|(i, m)| json!({"move": m.label, "has_effect": effective.contains(&m.action),
                                 "off": stats(&off[i]).0, "on": stats(&on[i]).0, "rounds_acted": m.interventions.iter().filter(|&&n| n > 0).count()}))
            .collect::<Vec<_>>());
        line["choice_tools_off"] = json!(study.moves[c_off].label);
        line["choice_rule_only"] = json!(study.moves[c_rule].label);
        line["choice_tools_on"] = json!(study.moves[c_on].label);
        line["tie_break"] = json!(if tie_target.is_none() { "doesn't apply" } else if c_rule != 0 { "a move cleared the bar" } else if kept { "km3's placement kept by its play-outs" } else { "applied" });
        line["km_lead_over_target"] = json!(km_lead.map(|(m, se)| json!({"mean": m, "se": se})));
        line["on_has_effect"] = json!(effective.contains(&study.moves[c_on].action));
        line["off_has_effect"] = json!(effective.contains(&study.moves[c_off].action));
        line["tools_on_minus_off"] = paired(&on[c_on], &off[c_off]);
        line["tie_break_over_rule_only"] = paired(&on[c_on], &on[c_rule]);
        writeln!(out, "{line}").unwrap();
        out.flush().unwrap();
        println!(
            "{id}: {} placements ({} with effect); km3 proposes {} ({}); kx3 with _tools off -> {} | rule only -> {} | on -> {} (tie-break: {}); on - off {:+.3} [{:+.3}, {:+.3}]",
            off_moves.len(), effective.len(), study.moves[0].label, if line["km_proposal_has_effect"] == json!(true) { "has an effect" } else { "no effect" },
            study.moves[c_off].label, study.moves[c_rule].label, study.moves[c_on].label, line["tie_break"].as_str().unwrap(),
            line["tools_on_minus_off"]["mean"].as_f64().unwrap(), line["tools_on_minus_off"]["lo"].as_f64().unwrap(), line["tools_on_minus_off"]["hi"].as_f64().unwrap()
        );
    }
}

/// Gate 2 of the no-effect tie-break (see the header).
fn no_effect_gate(args: &[String]) {
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(args, "--positions").unwrap()).unwrap()).unwrap();
    let rounds: usize = arg(args, "--rounds").map_or(64, |r| r.parse().unwrap());
    let out_path = arg(args, "--out").unwrap();
    let done: BTreeSet<String> = if args.iter().any(|a| a == "--resume") {
        std::fs::read_to_string(&out_path)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter_map(|v| v["id"].as_str().map(String::from))
            .collect()
    } else {
        BTreeSet::new()
    };
    let mut out = std::fs::OpenOptions::new().create(true).append(true).open(&out_path).unwrap();
    for p in &positions {
        let id = p["id"].as_str().unwrap().to_string();
        if done.contains(&id) {
            continue;
        }
        let state: State = serde_json::from_str(&std::fs::read_to_string(p["state"].as_str().unwrap()).unwrap()).unwrap();
        let deck = Deck::from_file(p["deck"].as_str().unwrap()).unwrap();
        let opponent = Deck::from_file(p["opponent"].as_str().unwrap()).unwrap();
        let seed = p["seed"].as_u64().unwrap();
        let (me, actions) = state.generate_possible_actions();
        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
        let pilot = |noeffect: bool, rollouts: usize| {
            let params = PlayoutParams { rollouts, cap: 12, z: 2.0, knowledge: Knowledge::Lab, noeffect, ..PlayoutParams::new(3) };
            PlayoutPlayer::with_extra_lists(deck.clone(), opponent.clone(), params, Vec::new())
        };
        // One round: the pool, km3's move, and where the tie-break points (nothing clears the bar with one round).
        let pool_off = pilot(false, 1).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let pool_on = pilot(true, 1).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let moves: Vec<_> = pool_off.candidates.iter().map(|c| c.action.clone()).collect();
        let effect = |a: &deckgym::actions::Action| match effect_now(&state, a, &observation.known_own_deck) {
            Some(b) => json!(b),
            None => Value::Null,
        };
        let km_effect = effect_now(&state, &moves[0], &observation.known_own_deck);
        let tie_target = pool_on
            .reason
            .starts_with("tie-break: no effect now")
            .then(|| moves.iter().position(|a| *a == pool_on.candidates[pool_on.chosen].action).unwrap());
        let mut line = json!({"id": id, "seed": seed, "turn": state.turn_count,
            "pool": pool_off.candidates.iter().map(|c| json!({"move": c.label, "card": action_card(&state, &c.action), "does_something": effect(&c.action)})).collect::<Vec<_>>(),
            "pool_unchanged": pool_on.candidates.iter().map(|c| &c.action).eq(moves.iter()) && pool_on.dropped.len() == pool_off.dropped.len(),
            "km_move_does_something": effect(&moves[0]), "tie_break_applies": tie_target.is_some(),
            "tie_break_target": tie_target.map(|t| pool_off.candidates[t].label.clone()), "reason_on_one_round": pool_on.reason});
        if km_effect != Some(false) {
            writeln!(out, "{line}").unwrap();
            println!("{id}: km3's move {} does something now ({}); pool with _noeffect on {}, tie-break {}", pool_off.candidates[0].label,
                     action_card(&state, &moves[0]).unwrap_or_else(|| "no card text".into()),
                     if line["pool_unchanged"] == json!(true) { "unchanged" } else { "CHANGED" }, if tie_target.is_some() { "APPLIES" } else { "doesn't apply" });
            continue;
        }
        // km3's move does nothing now: every candidate played out, and kx3's two decisions from the same rounds.
        let off = pilot(false, rounds).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let on = pilot(true, rounds).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let study = pilot(false, rounds).continuation_study(&mut StdRng::seed_from_u64(seed), &observation, &moves, &Plan::default(), 0, rounds);
        let scores: Vec<Vec<f64>> = study.moves.iter().map(|m| m.km.iter().map(|o| o.score).collect()).collect();
        let index = |a: &deckgym::actions::Action| moves.iter().position(|m| m == a).unwrap();
        let (c_off, c_on) = (index(&off.candidates[off.chosen].action), index(&on.candidates[on.chosen].action));
        let d: Vec<f64> = scores[c_on].iter().zip(&scores[c_off]).map(|(a, b)| a - b).collect();
        let (m, se) = stats(&d);
        line["rounds"] = json!(study.rounds);
        line["failed_rounds"] = json!(study.failed_rounds);
        line["moves"] = json!(study.moves.iter().enumerate().map(|(i, mv)| json!({"move": mv.label, "does_something": effect(&mv.action),
            "score": stats(&scores[i]).0, "kx3_score": off.candidates.iter().find(|c| c.action == mv.action).map(|c| c.score)}))
            .collect::<Vec<_>>());
        line["choice_off"] = json!(off.candidates[off.chosen].label);
        line["choice_on"] = json!(on.candidates[on.chosen].label);
        line["reason_off"] = json!(off.reason);
        line["reason_on"] = json!(on.reason);
        line["on_minus_off"] = json!({"mean": m, "lo": m - 1.96 * se, "hi": m + 1.96 * se});
        writeln!(out, "{line}").unwrap();
        out.flush().unwrap();
        println!("{id}: km3's move {} does nothing now; kx3 off -> {} | on -> {} ({}); on - off {:+.3} [{:+.3}, {:+.3}]", pool_off.candidates[0].label,
                 line["choice_off"].as_str().unwrap(), line["choice_on"].as_str().unwrap(), on.reason, m, m - 1.96 * se, m + 1.96 * se);
    }
}

/// The close-call extension's cost and effect (see the header).
fn extension_gate(args: &[String]) {
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(args, "--positions").unwrap()).unwrap()).unwrap();
    let seeds: u64 = arg(args, "--seeds").map_or(4, |r| r.parse().unwrap());
    let max_rounds: usize = arg(args, "--max-rounds").map_or(64, |r| r.parse().unwrap());
    let combined = args.iter().any(|a| a == "--combined");
    let out_path = arg(args, "--out").unwrap();
    let done: BTreeSet<String> = if args.iter().any(|a| a == "--resume") {
        std::fs::read_to_string(&out_path)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter_map(|v| v["decision"].as_str().map(String::from))
            .collect()
    } else {
        BTreeSet::new()
    };
    let mut out = std::fs::OpenOptions::new().create(true).append(true).open(&out_path).unwrap();
    for p in &positions {
        let id = p["id"].as_str().unwrap().to_string();
        let stored: State = serde_json::from_str(&std::fs::read_to_string(p["state"].as_str().unwrap()).unwrap()).unwrap();
        let deck = Deck::from_file(p["deck"].as_str().unwrap()).unwrap();
        let opponent = Deck::from_file(p["opponent"].as_str().unwrap()).unwrap();
        let seed0 = p["seed"].as_u64().unwrap();
        // The position as stored, and (with a "tool") advanced by playing it, so the decision is its placement.
        let mut points = vec![("as stored", stored.clone())];
        if let Some(name) = p["tool"].as_str() {
            let (me, legal) = stored.generate_possible_actions();
            let play = legal
                .iter()
                .find(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == name))
                .unwrap_or_else(|| panic!("{id}: {name} can't be played"))
                .clone();
            let (d0, d1) = if me == 0 { (deck.clone(), opponent.clone()) } else { (opponent.clone(), deck.clone()) };
            let km = PlayerCode::KM { max_depth: 3 };
            let mut game = Game::from_state(stored.clone(), create_players(d0, d1, vec![km.clone(), km]), seed0);
            game.apply_action(&play);
            points.push(("placement", game.get_state_clone()));
        }
        for (at, state) in &points {
            let (me, actions) = state.generate_possible_actions();
            let observation = PlayerObservation::from_state(state, me, &RevealedKnowledge::default());
            for s in 0..seeds {
                let seed = seed0 + 10_000 * s;
                let decision = format!("{id} | {at} | {seed}");
                if done.contains(&decision) {
                    continue;
                }
                let params = |max: Option<usize>| PlayoutParams {
                    rollouts: 16,
                    cap: 12,
                    z: 2.0,
                    knowledge: Knowledge::Lab,
                    tools: combined,
                    z_skip: combined.then_some(3.0),
                    max_rounds: max,
                    ..PlayoutParams::new(3)
                };
                let decide = |max: Option<usize>| {
                    PlayoutPlayer::with_extra_lists(deck.clone(), opponent.clone(), params(max), Vec::new())
                        .evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions)
                };
                let plain = decide(None);
                let ext = decide(Some(max_rounds));
                let cands = |r: &deckgym::players::playout_player::DecisionReport| {
                    r.candidates.iter().map(|c| json!({"move": c.label, "score": c.score, "diff": c.diff, "se": c.se, "rounds": c.rounds})).collect::<Vec<_>>()
                };
                let line = json!({
                    "decision": decision, "id": id, "at": at, "seed": seed, "turn": state.turn_count,
                    "code_r16": params(None).code(), "code_ext": params(Some(max_rounds)).code(),
                    "candidates": plain.candidates.len(), "km_move": plain.candidates[plain.km3].label,
                    "chosen_r16": plain.candidates[plain.chosen].label, "chosen_ext": ext.candidates[ext.chosen].label,
                    "changed": plain.candidates[plain.chosen].action != ext.candidates[ext.chosen].action,
                    "ms_r16": plain.millis.round(), "ms_ext": ext.millis.round(), "rounds_ext": ext.rounds,
                    "extended": ext.candidates.iter().filter(|c| c.rounds > plain.rounds).count(),
                    "failed_rounds": [plain.failed_rounds, ext.failed_rounds],
                    "reason_r16": plain.reason, "reason_ext": ext.reason, "r16": cands(&plain), "ext": cands(&ext),
                });
                writeln!(out, "{line}").unwrap();
                out.flush().unwrap();
                println!(
                    "{decision}: R16 -> {} ({} ms) | m{max_rounds} -> {} ({} ms, {} rounds, {} extended){}",
                    line["chosen_r16"].as_str().unwrap().chars().take(50).collect::<String>(),
                    line["ms_r16"], line["chosen_ext"].as_str().unwrap().chars().take(50).collect::<String>(), line["ms_ext"],
                    ext.rounds, line["extended"], if line["changed"] == json!(true) { " CHANGED" } else { "" }
                );
            }
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a == "--tie-break") {
        tie_break_gate(&args);
        return;
    }
    if args.iter().any(|a| a == "--no-effect") {
        no_effect_gate(&args);
        return;
    }
    if args.iter().any(|a| a == "--extension") {
        extension_gate(&args);
        return;
    }
    if args.iter().any(|a| a == "--list-effects") {
        let mut seen = BTreeSet::new();
        for card in CardId::iter().map(get_card_by_enum) {
            let (name, text, kind) = match &card {
                Card::Trainer(t) if matches!(format!("{:?}", t.trainer_card_type).as_str(), "Item" | "Supporter" | "Stadium") => {
                    (t.name.clone(), t.effect.clone(), format!("{:?}", t.trainer_card_type))
                }
                Card::Pokemon(p) => match &p.ability {
                    Some(a) => (format!("{}'s {}", p.name, a.title), a.effect.clone(), "Ability".to_string()),
                    None => continue,
                },
                _ => continue,
            };
            if !seen.insert(text.clone()) {
                continue;
            }
            // A text is a move if it is played (an Item, a Supporter) or used: a Stadium "once during each player's turn",
            // an Ability "once during your turn" or "as often as you like" (the others work by themselves).
            let t = text.to_lowercase();
            let move_ = match kind.as_str() {
                "Item" | "Supporter" => true,
                "Stadium" => t.contains("once during each player's turn"),
                _ => t.contains("once during your turn") || t.starts_with("as often as you like"),
            };
            let reading = match effect_needs(&text) {
                Ok(Reading::Always) => json!("always"),
                Ok(Reading::Needs(needs)) => json!(needs.iter().map(|n| format!("{n:?}")).collect::<Vec<_>>()),
                Err(why) => json!({"unread": why}),
            };
            println!("{}", json!({"card": name, "kind": kind, "can_be_a_move": move_, "reading": reading, "text": text}));
        }
        return;
    }
    if args.iter().any(|a| a == "--list-tools") {
        let mut seen = BTreeSet::new();
        for card in CardId::iter().map(get_card_by_enum) {
            if let Card::Trainer(t) = &card {
                if format!("{:?}", t.trainer_card_type) == "Tool" && seen.insert(t.effect.clone()) {
                    let c = tool_conditions(&t.effect);
                    println!("{}", json!({"tool": t.name, "text": t.effect, "conditions": format!("{c:?}")}));
                }
            }
        }
        return;
    }
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(&args, "--positions").unwrap()).unwrap()).unwrap();
    let rounds: usize = arg(&args, "--rounds").map_or(128, |r| r.parse().unwrap());
    let out_path = arg(&args, "--out").unwrap();
    let done: BTreeSet<String> = if args.iter().any(|a| a == "--resume") {
        std::fs::read_to_string(&out_path)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter_map(|v| v["id"].as_str().map(String::from))
            .collect()
    } else {
        BTreeSet::new()
    };
    let mut out = std::fs::OpenOptions::new().create(true).append(true).open(&out_path).unwrap();
    for p in &positions {
        let id = p["id"].as_str().unwrap().to_string();
        if done.contains(&id) {
            continue;
        }
        let state: State = serde_json::from_str(&std::fs::read_to_string(p["state"].as_str().unwrap()).unwrap()).unwrap();
        let deck = Deck::from_file(p["deck"].as_str().unwrap()).unwrap();
        let opponent = Deck::from_file(p["opponent"].as_str().unwrap()).unwrap();
        let seed = p["seed"].as_u64().unwrap();
        let (me, actions) = state.generate_possible_actions();
        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
        let params = PlayoutParams { rollouts: 1, cap: 12, z: 2.0, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
        let mut pilot = PlayoutPlayer::with_extra_lists(deck, opponent, params, Vec::new());
        // kx3's candidates (km3's move first, the cap's drops named): they don't depend on the number of play-outs.
        let candidates = pilot.evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let moves: Vec<_> = candidates.candidates.iter().map(|c| c.action.clone()).collect();
        let study = pilot.tool_rule_study(&mut StdRng::seed_from_u64(seed), &observation, &moves, rounds);
        let off: Vec<Vec<f64>> = study.moves.iter().map(|m| m.off.iter().map(|o| o.score).collect()).collect();
        let on: Vec<Vec<f64>> = study.moves.iter().map(|m| m.on.iter().map(|o| o.score).collect()).collect();
        let (c_off, c_on) = (choice(&off, 2.0), choice(&on, 2.0));
        let rows: Vec<Value> = study
            .moves
            .iter()
            .enumerate()
            .map(|(i, m)| {
                let d: Vec<f64> = on[i].iter().zip(&off[i]).map(|(a, b)| a - b).collect();
                let (dm, dse) = stats(&d);
                json!({"move": m.label, "off": stats(&off[i]).0, "on": stats(&on[i]).0, "on_minus_off": dm, "lo": dm - 1.96 * dse, "hi": dm + 1.96 * dse,
                       "rounds_acted": m.interventions.iter().filter(|&&n| n > 0).count(), "interventions": m.interventions.iter().sum::<usize>(),
                       "rounds_detail": {"off": m.off.iter().map(|o| json!([o.score, format!("{:016x}", o.digest), o.turn])).collect::<Vec<_>>(),
                                         "on": m.on.iter().map(|o| json!([o.score, format!("{:016x}", o.digest), o.turn])).collect::<Vec<_>>()}})
            })
            .collect();
        let line = json!({"id": id, "seed": seed, "rounds": study.rounds, "failed_rounds": study.failed_rounds, "knowledge": study.knowledge,
                          "lists": study.lists, "ms": study.millis.round(), "dropped": candidates.dropped.iter().map(|d| d.label.clone()).collect::<Vec<_>>(),
                          "kx3_choice_off": study.moves[c_off].label, "kx3_choice_on": study.moves[c_on].label, "moves": rows});
        writeln!(out, "{line}").unwrap();
        out.flush().unwrap();
        let acted: usize = study.moves.iter().map(|m| m.interventions.iter().filter(|&&n| n > 0).count()).sum();
        let worst = rows.iter().map(|r| r["on_minus_off"].as_f64().unwrap()).fold(f64::INFINITY, f64::min);
        let best = rows.iter().map(|r| r["on_minus_off"].as_f64().unwrap()).fold(f64::NEG_INFINITY, f64::max);
        println!(
            "{id}: {} moves x {} rounds; the rule acted in {acted} play-outs; on - off per move from {worst:+.3} to {best:+.3}; kx3's choice {} -> {}",
            rows.len(), study.rounds, if c_off == c_on { "unchanged" } else { "changed" }, study.moves[c_on].label.chars().take(60).collect::<String>()
        );
    }
}
