//! The continuation experiment (Oct 5; Fable via Dustin; rl/results/playout_continuation_2026-10-05/README.md): does km3's
//! continuation of the play-outs hide good first moves? Per position (a built state and a plan from `--plans`), the plan's
//! first move and a rival (kx3's move) are each played out `--rounds` times from the same sampled worlds and seeds as kx3's
//! own play-outs, continued by km3 and by the plan for its K own turns (`PlayoutPlayer::continuation_study`). Printed per
//! position: each move's mean score both ways, the paired differences with standard errors and 95% intervals, how often
//! each scripted step was played, skipped or never reached, and a verdict by the rule the README states. With `--kx3`,
//! kx3's own decision at the position too (`evaluate`, the same rounds and decision randomness, LAB), as a trace line.
//!   playout_continuation --plans <plans.json> --states <dir> --deck <pilot's list> --opponent <opponent's list>
//!     [--rounds 64] [--seed-base 24200001000] [--only <id>] [--kx3 | --kx3-only] [--out results.jsonl] [--resume]
//! Position i (in the plans file's order) uses the decision randomness StdRng(seed-base + i). `--kx3-only` runs kx3's
//! decision alone (its line matches the study's by the same seed and rounds). `--resume` skips positions already in
//! `--out` (by their study line, or kx3 line with `--kx3-only`). Every plan's names are checked against the pilot's list
//! before anything runs.
use std::collections::BTreeSet;
use std::io::Write;

use deckgym::actions::{Action, SimpleAction};
use deckgym::models::Card;
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{
    ContinuationMove, ContinuationReport, Knowledge, Plan, PlayoutParams, PlayoutPlayer, Step,
};
use deckgym::{Deck, State};
use rand::{rngs::StdRng, SeedableRng};
use serde::Deserialize;
use serde_json::{json, Value};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Entry {
    id: String,
    /// The plan's own turns to play (at most its turns).
    k: usize,
    first_move: Step,
    rival: Step,
    /// Who chose the rival, for the report.
    rival_is: String,
    #[serde(default)]
    note: String,
    plan: Plan,
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// Mean, standard error, and the 95% interval (mean ± 1.96 SE) of per-round values.
fn stats(values: &[f64]) -> Value {
    let n = values.len() as f64;
    let mean = values.iter().sum::<f64>() / n;
    let se = if values.len() < 2 { f64::NAN } else { (values.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / (n - 1.0)).sqrt() / n.sqrt() };
    json!({"mean": mean, "se": se, "lo": mean - 1.96 * se, "hi": mean + 1.96 * se})
}

fn scores(o: &[deckgym::players::playout_player::Outcome]) -> Vec<f64> {
    o.iter().map(|x| x.score).collect()
}

fn paired(a: &[f64], b: &[f64]) -> Vec<f64> {
    a.iter().zip(b).map(|(x, y)| x - y).collect()
}

/// Every name and attack a plan uses must be in the pilot's list: a misspelt name would never match and would only show
/// up as a skipped step.
fn check_names(entry: &Entry, deck: &Deck) -> Result<(), String> {
    let mut pokemon = BTreeSet::new();
    let mut trainers = BTreeSet::new();
    let mut attacks = BTreeSet::new();
    for card in &deck.cards {
        match card {
            Card::Pokemon(p) => {
                pokemon.insert(p.name.clone());
                attacks.extend(p.attacks.iter().map(|a| a.title.clone()));
            }
            Card::Trainer(t) => {
                trainers.insert(t.name.clone());
            }
            _ => {}
        }
    }
    let check = |set: &BTreeSet<String>, name: &str, what: &str| -> Result<(), String> {
        if set.contains(name) { Ok(()) } else { Err(format!("{}: {what} \"{name}\" is not in the pilot's list", entry.id)) }
    };
    let check_step = |step: &Step| -> Result<(), String> {
        match step {
            Step::Energy { to, .. } | Step::ExtraEnergy { to, .. } | Step::Target { to, .. } | Step::RetreatTo { to } => {
                to.iter().try_for_each(|n| check(&pokemon, n, "Pokémon"))
            }
            Step::Evolve { into, from, .. } => {
                check(&pokemon, into, "Pokémon")?;
                from.iter().try_for_each(|n| check(&pokemon, n, "Pokémon"))
            }
            Step::Bench { card } => check(&pokemon, card, "Pokémon"),
            Step::Play { card } => check(&trainers, card, "Trainer"),
            Step::Attack { title } => check(&attacks, title, "attack"),
        }
    };
    check_step(&entry.first_move)?;
    check_step(&entry.rival)?;
    for turn in &entry.plan.turns {
        turn.steps.iter().try_for_each(check_step)?;
        turn.avoid.iter().try_for_each(|n| check(&trainers, n, "Trainer"))?;
    }
    entry.plan.promote.iter().try_for_each(|n| check(&pokemon, n, "Pokémon"))
}

/// The one legal move a step names at the position (identical copies, two of a card in hand, count once; benching a card
/// in one empty Bench slot or another is one move, and the first slot is taken).
fn the_move(state: &State, me: usize, step: &Step, what: &str, id: &str) -> Action {
    let legal = state.generate_possible_actions().1;
    let mut found: Vec<Action> = legal.iter().filter(|a| step.matches(state, me, a)).cloned().collect();
    found.dedup();
    let one_card_placed = |a: &Action| match (&a.action, &found[0].action) {
        (SimpleAction::Place(c, _), SimpleAction::Place(first, _)) => c == first,
        _ => false,
    };
    assert!(
        found.len() == 1 || (!found.is_empty() && found.iter().all(one_card_placed)),
        "{id}: the {what} {step:?} names {} legal moves: {found:?}",
        found.len()
    );
    found.remove(0)
}

fn move_json(m: &ContinuationMove, plan: &Plan, start: u8) -> Value {
    let km = scores(&m.km);
    let planned = scores(&m.plan);
    let steps: Vec<Value> = (0..m.counts.fired.len())
        .flat_map(|t| {
            (0..m.counts.fired[t].len()).map(move |s| (t, s))
        })
        .map(|(t, s)| {
            json!({
                "own_turn": t, "game_turn": start as usize + 2 * t, "step": plan.turns[t].steps[s],
                "played": m.counts.fired[t][s], "skipped": m.counts.skipped[t][s], "unreached": m.counts.unreached[t][s],
            })
        })
        .collect();
    json!({
        "move": m.label,
        "km3_continuation": stats(&km),
        "plan_continuation": stats(&planned),
        "plan_minus_km3": stats(&paired(&planned, &km)),
        "same_final_state": m.km.iter().zip(&m.plan).filter(|(a, b)| a.digest == b.digest).count(),
        "steps": steps,
        "plan_moves": m.counts.plan_moves, "promotions": m.counts.promotions, "km3_fills": m.counts.km_fills,
        "plan_attack_replaced_km3s_end": m.counts.substituted,
        "round_0_plan_trace": m.plan_trace, "round_0_km3_trace": m.km3_trace, "round_0_km3_trace_is_km3s_play_out": m.km3_trace_is_km3,
        "rounds_detail": {
            "km3": m.km.iter().map(|o| json!([o.score, format!("{:016x}", o.digest), o.turn])).collect::<Vec<_>>(),
            "plan": m.plan.iter().map(|o| json!([o.score, format!("{:016x}", o.digest), o.turn])).collect::<Vec<_>>(),
        },
    })
}

/// The verdict, by the rule stated in the README, from the paired leads of the plan's first move over the rival.
fn verdict(lead_km: &Value, lead_plan: &Value, change: &Value) -> String {
    let f = |v: &Value, k: &str| v[k].as_f64().unwrap_or(f64::NAN);
    if f(lead_plan, "lo") > 0.0 && f(lead_km, "mean") <= 0.0 {
        "hidden: the plan's first move leads beyond noise under the plan's continuation, and not under km3's".into()
    } else if f(change, "lo") > 0.0 {
        if f(lead_plan, "lo") > 0.0 {
            "lifted: the plan's continuation widens the plan's first move's lead beyond noise (it leads under both)".into()
        } else {
            "lifted, not ahead: the plan's continuation raises the plan's first move's lead beyond noise, but it doesn't lead beyond noise".into()
        }
    } else if f(lead_plan, "hi") < 0.0 {
        "worse: the plan's first move trails beyond noise even under the plan's continuation".into()
    } else if f(lead_km, "lo") > 0.0 || f(lead_plan, "lo") > 0.0 {
        "ahead either way: the plan's first move leads beyond noise without the plan's continuation changing the lead beyond noise".into()
    } else {
        "no difference: within the noise under both continuations; the plan isn't better in these worlds".into()
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let entries: Vec<Entry> =
        serde_json::from_str(&std::fs::read_to_string(arg(&args, "--plans").expect("--plans")).unwrap()).expect("the plans file");
    let states = arg(&args, "--states").expect("--states");
    let deck = Deck::from_file(&arg(&args, "--deck").expect("--deck")).unwrap();
    let opponent = Deck::from_file(&arg(&args, "--opponent").expect("--opponent")).unwrap();
    let rounds: usize = arg(&args, "--rounds").map_or(64, |r| r.parse().unwrap());
    let seed_base: u64 = arg(&args, "--seed-base").map_or(24_200_001_000, |s| s.parse().unwrap());
    let only = arg(&args, "--only");
    let kx3_only = args.iter().any(|a| a == "--kx3-only");
    let with_kx3 = kx3_only || args.iter().any(|a| a == "--kx3");
    let out_path = arg(&args, "--out");
    let resume = args.iter().any(|a| a == "--resume");
    for entry in &entries {
        check_names(entry, &deck).unwrap_or_else(|e| panic!("{e}"));
    }
    let done: BTreeSet<String> = match (&out_path, resume) {
        (Some(p), true) => std::fs::read_to_string(p)
            .unwrap_or_default()
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter(|v| v["kind"] == if kx3_only { "kx3" } else { "study" })
            .filter_map(|v| v["id"].as_str().map(String::from))
            .collect(),
        _ => BTreeSet::new(),
    };
    let mut out = out_path.map(|p| std::fs::OpenOptions::new().create(true).append(true).open(p).unwrap());
    for (i, entry) in entries.iter().enumerate() {
        if only.as_ref().is_some_and(|o| *o != entry.id) || done.contains(&entry.id) {
            continue;
        }
        let state: State = serde_json::from_str(&std::fs::read_to_string(format!("{states}/{}.json", entry.id)).unwrap()).unwrap();
        let me = state.generate_possible_actions().0;
        let first = the_move(&state, me, &entry.first_move, "first move", &entry.id);
        let rival = the_move(&state, me, &entry.rival, "rival", &entry.id);
        assert!(first != rival, "{}: the first move and the rival are the same move", entry.id);
        let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
        let seed = seed_base + i as u64;
        let params = PlayoutParams { rollouts: rounds, cap: 12, z: 2.0, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
        let mut pilot = PlayoutPlayer::with_extra_lists(deck.clone(), opponent.clone(), params, Vec::new());
        let mut lines: Vec<Value> = Vec::new();
        if with_kx3 {
            let actions = state.generate_possible_actions().1;
            let report = pilot.evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
            lines.push(json!({
                "kind": "kx3", "id": entry.id, "seed": seed, "code": pilot.params().code(), "knowledge": report.knowledge,
                "rounds": report.rounds, "failed_rounds": report.failed_rounds, "lists": report.lists, "ms": report.millis.round(),
                "km_move": report.candidates[report.km3].label, "chosen": report.candidates[report.chosen].label, "reason": report.reason,
                "candidates": report.candidates.iter().map(|c| json!({
                    "move": c.label, "score": c.score, "diff": c.diff, "se": if c.se.is_finite() { c.se } else { -1.0 }
                })).collect::<Vec<_>>(),
                "dropped": report.dropped.iter().map(|d| d.label.clone()).collect::<Vec<_>>(),
            }));
        }
        if kx3_only {
            if let Some(out) = &mut out {
                for line in &lines {
                    writeln!(out, "{line}").unwrap();
                }
                out.flush().unwrap();
            }
            println!("{} kx3: {}", entry.id, lines[0]["chosen"]);
            continue;
        }
        let report: ContinuationReport =
            pilot.continuation_study(&mut StdRng::seed_from_u64(seed), &observation, &[first, rival], &entry.plan, entry.k, rounds);
        let (p1, r1) = (&report.moves[0], &report.moves[1]);
        let lead_km = stats(&paired(&scores(&p1.km), &scores(&r1.km)));
        let lead_plan = stats(&paired(&scores(&p1.plan), &scores(&r1.plan)));
        let change: Vec<f64> = (0..report.rounds)
            .map(|j| (p1.plan[j].score - r1.plan[j].score) - (p1.km[j].score - r1.km[j].score))
            .collect();
        let change = stats(&change);
        let verdict = verdict(&lead_km, &lead_plan, &change);
        lines.push(json!({
            "kind": "study", "id": entry.id, "seed": seed, "k": report.k, "rounds": report.rounds, "failed_rounds": report.failed_rounds,
            "knowledge": report.knowledge, "lists": report.lists, "ms": report.millis.round(), "note": entry.note,
            "plans_first_move": move_json(p1, &entry.plan, state.turn_count),
            "rival": move_json(r1, &entry.plan, state.turn_count), "rival_is": entry.rival_is,
            "lead_under_km3": lead_km, "lead_under_plan": lead_plan, "lead_change": change, "verdict": verdict,
        }));
        // kx3's report and the study share their worlds: the two moves' km3 scores are their kx3 scores.
        if let Some(kx3) = lines.iter().find(|l| l["kind"] == "kx3") {
            for (m, key) in [(p1, "plans_first_move"), (r1, "rival")] {
                let from_kx3 = kx3["candidates"].as_array().unwrap().iter().find(|c| c["move"] == m.label.as_str()).map(|c| c["score"].clone());
                let study = lines.last().unwrap()[key]["km3_continuation"]["mean"].clone();
                eprintln!("{}: {key} km3 score {study} in the study, {} in kx3's report", entry.id, from_kx3.unwrap_or(Value::Null));
            }
        }
        let f = |v: &Value| format!("{:+.3} ± {:.3}", v["mean"].as_f64().unwrap(), 1.96 * v["se"].as_f64().unwrap_or(f64::NAN));
        let g = |v: &Value| format!("{:.3}", v["mean"].as_f64().unwrap());
        let study = lines.last().unwrap();
        println!(
            "{} K={} R={} | first move {}: km3 {} plan {} | rival ({}) {}: km3 {} plan {} | lead km3 {} plan {} change {} | {}",
            entry.id, report.k, report.rounds, p1.label.chars().take(60).collect::<String>(),
            g(&study["plans_first_move"]["km3_continuation"]), g(&study["plans_first_move"]["plan_continuation"]), entry.rival_is,
            r1.label.chars().take(60).collect::<String>(), g(&study["rival"]["km3_continuation"]), g(&study["rival"]["plan_continuation"]),
            f(&study["lead_under_km3"]), f(&study["lead_under_plan"]), f(&study["lead_change"]), verdict
        );
        if let Some(out) = &mut out {
            for line in &lines {
                writeln!(out, "{line}").unwrap();
            }
            out.flush().unwrap();
        }
    }
}
