//! The plan continuation for the play-outs (Oct 5; Fable via Dustin; rl/results/playout_continuation_2026-10-05). Written
//! before the option: with K = 0 the plan's continuation is km3's play-outs, final state for final state; the study's
//! km3 continuation is kx3's own play-outs (the same sampled worlds and seeds as `evaluate`); with K > 0 the plan's steps
//! are played when legal and the rest are counted as skipped; the study is deterministic; a plan with a misspelt field
//! is refused; `keep_active_if` forbids km3's retreat only while the Pokémon it names is the Active. The position is the
//! experiment's first: draft A v the computer deck, B-214254-t06, as the position runner built it (seed 1).
use deckgym::actions::Action;
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{ContinuationReport, Knowledge, Plan, PlanTurn, PlayoutParams, PlayoutPlayer, Step};
use deckgym::{Deck, State};
use rand::{rngs::StdRng, SeedableRng};

const POSITIONS: &str = "../rl/results/playout_continuation_2026-10-05/states";

/// Position 1's plan, as rl/results/kx3_examples_2026-10-04/CONTINUATION_POSITIONS.md writes it: the turn's Water on the
/// Benched Vulpix, Turbo Shark with its extra Water to the Vulpix; turn 8 evolve Carvanha and give it the turn's Water;
/// turns 8 and 10 Turbo Shark to the Vulpix (or its Ninetales ex, if km3 has evolved it); turn 12 evolve the Vulpix,
/// retreat into it, Binding Snow. The same as plans.json's.
const PLAN_T06: &str = r#"{
  "promote": ["Alolan Ninetales ex", "Mega Sharpedo ex"],
  "turns": [
    {"keep_active_if": ["Mega Sharpedo ex"], "steps": [
      {"do": "energy", "to": ["Alolan Vulpix"], "at": "bench"},
      {"do": "attack", "title": "Turbo Shark"},
      {"do": "extra_energy", "to": ["Alolan Vulpix", "Alolan Ninetales ex"]}]},
    {"keep_active_if": ["Mega Sharpedo ex"], "steps": [
      {"do": "evolve", "into": "Mega Sharpedo ex", "from": "Carvanha", "at": "bench"},
      {"do": "energy", "to": ["Mega Sharpedo ex"], "at": "bench"},
      {"do": "attack", "title": "Turbo Shark"},
      {"do": "extra_energy", "to": ["Alolan Vulpix", "Alolan Ninetales ex"]}]},
    {"keep_active_if": ["Mega Sharpedo ex"], "steps": [
      {"do": "attack", "title": "Turbo Shark"},
      {"do": "extra_energy", "to": ["Alolan Vulpix", "Alolan Ninetales ex"]}]},
    {"steps": [
      {"do": "evolve", "into": "Alolan Ninetales ex", "from": "Alolan Vulpix"},
      {"do": "retreat_to", "to": ["Alolan Ninetales ex"]},
      {"do": "bench", "card": "Alolan Vulpix"},
      {"do": "attack", "title": "Binding Snow"}]}
  ]
}"#;

fn deck(path: &str) -> Deck {
    Deck::from_file(path).unwrap()
}

fn position(id: &str) -> State {
    serde_json::from_str(&std::fs::read_to_string(format!("{POSITIONS}/{id}.json")).unwrap()).unwrap()
}

/// kx3 at draft A's seat, LAB: the computer deck is in the wide pool, so its exact list is used (as the laptop's
/// REALISTIC run had it, the one consistent list).
fn pilot(rollouts: usize, cap: usize) -> PlayoutPlayer {
    let params = PlayoutParams { rollouts, cap, z: 50.0, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(
        deck("../decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt"),
        deck("../decks/computer/blastoise-wailord-deluxe.txt"),
        params,
        Vec::new(),
    )
}

fn plan() -> Plan {
    serde_json::from_str(PLAN_T06).unwrap()
}

fn step(json: &str) -> Step {
    serde_json::from_str(json).unwrap()
}

/// The legal action a step names at the state (exactly one).
fn the_action(state: &State, json: &str) -> Action {
    let found: Vec<Action> = state.generate_possible_actions().1.into_iter().filter(|a| step(json).matches(state, 0, a)).collect();
    assert_eq!(found.len(), 1, "{json}: {found:?}");
    found[0].clone()
}

/// t06's two first moves: the plan's (the turn's Water on the Benched Vulpix) and kx3's (Turbo Shark).
fn t06() -> (State, PlayerObservation, Vec<Action>) {
    let state = position("B-214254-t06");
    let water = the_action(&state, r#"{"do": "energy", "to": ["Alolan Vulpix"], "at": "bench"}"#);
    let shark = the_action(&state, r#"{"do": "attack", "title": "Turbo Shark"}"#);
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    (state, observation, vec![water, shark])
}

fn study(k: usize, plan: &Plan, rounds: usize, seed: u64) -> ContinuationReport {
    let (_, observation, moves) = t06();
    pilot(rounds, 12).continuation_study(&mut StdRng::seed_from_u64(seed), &observation, &moves, plan, k, rounds)
}

/// With K = 0 the plan's continuation is km3's, final state for final state (its digest, turn and score), for a full
/// plan and for an empty one; and with no turns in the plan, any K is km3's too.
#[test]
fn with_k_0_the_plan_continuation_is_km3s_play_outs() {
    for (k, plan) in [(0, plan()), (0, Plan::default()), (4, Plan::default())] {
        let report = study(k, &plan, 6, 20_000_000_101);
        assert_eq!(report.failed_rounds, 0);
        assert_eq!(report.rounds, 6);
        for m in &report.moves {
            assert_eq!(m.km.len(), 6);
            assert_eq!(m.km, m.plan, "K = {k}, {}: the plan's play-outs differ from km3's", m.label);
            assert!(m.counts.plan_moves == 0 && m.counts.substituted == 0, "K = {k}: {:?}", m.counts);
        }
        // Round 0's km3 log comes from a plan of K empty turns, which plays as km3 does.
        assert!(report.moves.iter().all(|m| m.km3_trace_is_km3), "K = {k}");
        // The two first moves don't lead to the same game every time (the pairing is real).
        assert!(report.moves[0].km.iter().zip(&report.moves[1].km).any(|(a, b)| a.digest != b.digest));
    }
}

/// The study's km3 continuation is kx3's own play-outs: the same sampled worlds and seeds as `evaluate`, so the two first
/// moves' km3 scores are their scores in kx3's report at the same decision randomness.
#[test]
fn the_studys_km3_continuation_is_kx3s_play_outs() {
    let (state, observation, _) = t06();
    let actions = state.generate_possible_actions().1;
    let mut kx3 = pilot(6, 12);
    let report = kx3.evaluate(&mut StdRng::seed_from_u64(20_000_000_102), &observation, &actions);
    assert_eq!(report.rounds, 6, "{}", report.reason);
    let study = study(1, &plan(), 6, 20_000_000_102);
    for m in &study.moves {
        let candidate = report.candidates.iter().find(|c| c.action == m.action).expect("a candidate");
        let mean = m.km.iter().map(|o| o.score).sum::<f64>() / m.km.len() as f64;
        assert_eq!(mean, candidate.score, "{}", m.label);
    }
}

/// With K = 4 the plan is played: after its own first move, every round attacks with Turbo Shark at once and gives the
/// extra Water to the Vulpix; after kx3's move (Turbo Shark, which ends the turn) the plan's first step is skipped in every
/// round, its attack is the first move itself, and the extra Water is the plan's. Steps of turns the game never reached
/// are counted apart from the skipped ones.
#[test]
fn a_plan_is_played_when_legal_and_its_skips_are_counted() {
    let report = study(4, &plan(), 6, 20_000_000_103);
    assert_eq!(report.failed_rounds, 0);
    let (water, shark) = (&report.moves[0], &report.moves[1]);
    assert_eq!(water.counts.fired[0], vec![6, 6, 6], "{:?}", water.counts);
    assert_eq!(shark.counts.fired[0], vec![0, 6, 6], "{:?}", shark.counts);
    assert_eq!(shark.counts.skipped[0], vec![6, 0, 0], "{:?}", shark.counts);
    for m in [water, shark] {
        assert_eq!(m.counts.fired.len(), 4);
        for t in 0..4 {
            for s in 0..m.counts.fired[t].len() {
                assert_eq!(m.counts.fired[t][s] + m.counts.skipped[t][s] + m.counts.unreached[t][s], 6, "{:?}", m.counts);
            }
        }
        assert!(m.counts.plan_moves > 0, "{:?}", m.counts);
        assert!(m.km3_trace_is_km3);
        assert!(m.plan_trace[0].starts_with("t6 first move: "), "{:?}", m.plan_trace);
    }
    assert!(water.plan_trace.iter().any(|l| l == "t6 plan: attack Turbo Shark"), "{:?}", water.plan_trace);
    // The plan changes play: some round ends differently from km3's continuation.
    assert!(report.moves.iter().any(|m| m.km.iter().zip(&m.plan).any(|(a, b)| a.digest != b.digest)));
}

/// The same study twice is the same, round for round.
#[test]
fn the_study_is_deterministic() {
    let a = study(4, &plan(), 4, 20_000_000_104);
    let b = study(4, &plan(), 4, 20_000_000_104);
    for (x, y) in a.moves.iter().zip(&b.moves) {
        assert_eq!(x.km, y.km);
        assert_eq!(x.plan, y.plan);
        assert_eq!(x.counts, y.counts);
    }
}

/// A plan with a misspelt field or an unknown step is refused, not read as an empty rule.
#[test]
fn a_misspelt_plan_is_refused() {
    assert!(serde_json::from_str::<Plan>(r#"{"turns": [{"keep_actve": true}]}"#).is_err());
    assert!(serde_json::from_str::<Step>(r#"{"do": "energy", "too": ["Alolan Vulpix"]}"#).is_err());
    assert!(serde_json::from_str::<Step>(r#"{"do": "charge", "to": ["Alolan Vulpix"]}"#).is_err());
}

/// The keep rules bind km3's fill-ins only as written: `keep_active` forbids any retreat, `keep_active_if` only while the
/// Pokémon it names is the Active (at t06 the Caped Mega Sharpedo ex), and `avoid` forbids the Trainers it names (at t10).
#[test]
fn the_keep_rules_forbid_a_retreat_only_while_they_hold() {
    let state = position("B-214254-t06");
    let retreat = the_action(&state, r#"{"do": "retreat_to", "to": ["Alolan Vulpix"]}"#);
    // Irida is legal at t10 (the Caped Mega is damaged), not at t06.
    let damaged = position("B-214254-t10");
    let irida = the_action(&damaged, r#"{"do": "play", "card": "Irida"}"#);
    let turn = |json: &str| serde_json::from_str::<PlanTurn>(json).unwrap();
    assert!(turn("{}").allows(&state, 0, &retreat));
    assert!(!turn(r#"{"keep_active": true}"#).allows(&state, 0, &retreat));
    assert!(!turn(r#"{"keep_active_if": ["Mega Sharpedo ex"]}"#).allows(&state, 0, &retreat));
    assert!(turn(r#"{"keep_active_if": ["Alolan Ninetales ex"]}"#).allows(&state, 0, &retreat));
    assert!(!turn(r#"{"avoid": ["Irida"]}"#).allows(&damaged, 0, &irida));
    assert!(turn(r#"{"avoid": ["Copycat"]}"#).allows(&damaged, 0, &irida));
}
