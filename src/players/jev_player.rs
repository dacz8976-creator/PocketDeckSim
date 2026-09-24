//! Jev action scorer. The decision boundary accepts only PlayerObservation.
//! Never reconstruct a State or query hidden zones. Each decision callback makes
//! one request containing one Score per legal action; the engine may apply forced moves directly.
use super::Player;
use crate::{actions::Action, observation::{canonical_actions, PlayerObservation}, Deck, State};
use rand::rngs::StdRng;
use serde_json::{json, Map, Value};
use std::{fs::{File, OpenOptions}, io::{BufRead, BufReader, Write}, path::PathBuf,
    process::{Child, ChildStdin, ChildStdout, Command, Stdio}, sync::atomic::{AtomicU64, Ordering}};

const TRANSPORT: &str = include_str!("jev_transport.py");
const LEVELS: [&str; 5] = [
    "Very poor: likely loses the game or severely harms the acting player's chances of winning.",
    "Poor: wastes resources or exposes an avoidable major disadvantage.",
    "Adequate: a neutral or reasonable move with limited progress toward winning.",
    "Good: meaningfully improves winning chances while respecting the opponent's visible threats.",
    "Excellent: wins now or is a particularly strong move toward winning, accounting for setup and future turns.",
];
static NEXT_INSTANCE: AtomicU64 = AtomicU64::new(0);

#[derive(Debug)]
struct Bridge { child: Child, input: ChildStdin, output: BufReader<ChildStdout> }
impl Drop for Bridge {
    fn drop(&mut self) { let _ = self.child.kill(); let _ = self.child.wait(); }
}

#[derive(Debug)]
pub struct JevPlayer {
    deck: Deck,
    bridge: Option<Bridge>,
    log: Option<File>,
    decision: u64,
    model: String,
}

impl JevPlayer {
    pub fn new(deck: Deck) -> Self {
        Self { deck, bridge: None, log: None, decision: 0,
            model: std::env::var("JEV_MODEL").unwrap_or_else(|_| "jev-latest".into()) }
    }
    fn start(&mut self) -> Result<(), String> {
        if self.bridge.is_some() { return Ok(()); }
        if std::env::var("TYPESAFE_API_KEY").map_or(true, |s| s.trim().is_empty()) {
            return Err("TYPESAFE_API_KEY is missing".into());
        }
        let dir = PathBuf::from(std::env::var("JEV_LOG_DIR").map_err(|_| "JEV_LOG_DIR is required")?);
        std::fs::create_dir_all(&dir).map_err(|e| format!("create Jev log directory: {e}"))?;
        let instance = NEXT_INSTANCE.fetch_add(1, Ordering::Relaxed);
        let path = dir.join(format!("jev-{}-{instance}.jsonl", std::process::id()));
        self.log = Some(OpenOptions::new().write(true).create_new(true).open(path)
            .map_err(|e| format!("create Jev log: {e}"))?);
        let mut child = Command::new(std::env::var("JEV_PYTHON").unwrap_or_else(|_| "python3".into()))
            .args(["-u", "-c", TRANSPORT]).stdin(Stdio::piped()).stdout(Stdio::piped())
            .stderr(Stdio::null()).spawn().map_err(|e| format!("start Jev transport: {e}"))?;
        self.bridge = Some(Bridge { input: child.stdin.take().unwrap(),
            output: BufReader::new(child.stdout.take().unwrap()), child });
        Ok(())
    }
    fn record(&mut self, value: Value) -> Result<(), String> {
        let log = self.log.as_mut().ok_or("Jev log unavailable")?;
        serde_json::to_writer(&mut *log, &value).map_err(|e| e.to_string())?;
        writeln!(log).and_then(|_| log.flush()).map_err(|e| e.to_string())
    }
    fn decide(&mut self, observation: &PlayerObservation, actions: &[Action]) -> Result<Action, String> {
        let (request, ordered) = request(observation, actions, &self.model)?;
        self.start()?;
        self.decision += 1;
        self.record(json!({"kind":"request", "decision":self.decision, "request":request}))?;
        let bridge = self.bridge.as_mut().unwrap();
        serde_json::to_writer(&mut bridge.input, &request).map_err(|e| e.to_string())?;
        writeln!(bridge.input).and_then(|_| bridge.input.flush()).map_err(|e| e.to_string())?;
        let mut line = String::new();
        if bridge.output.read_line(&mut line).map_err(|e| e.to_string())? == 0 {
            return Err("Jev transport closed without a response; request may have been billed".into());
        }
        let envelope: Value = serde_json::from_str(&line).map_err(|e| format!("invalid transport response: {e}"))?;
        if let Some(error) = envelope.get("transport_error") {
            self.record(json!({"kind":"error", "decision":self.decision, "transport":envelope}))?;
            return Err(format!("Jev transport failed: {error}"));
        }
        let response = envelope.get("response").ok_or("missing Jev response")?;
        // Persist raw probabilities and usage even when validation subsequently rejects them.
        self.record(json!({"kind":"response", "decision":self.decision, "response":response, "request_id":envelope.get("request_id"), "http_status":envelope.get("http_status")}))?;
        let selected = select(response, ordered.len())?;
        self.record(json!({"kind":"selected", "decision":self.decision,
            "action_id":action_id(selected), "action":ordered[selected]}))?;
        Ok(ordered[selected].clone())
    }
}

fn action_id(index: usize) -> String { format!("action_{index:06}") }
fn request(observation: &PlayerObservation, actions: &[Action], model: &str) -> Result<(Value, Vec<Action>), String> {
    if actions.is_empty() { return Err("Jev received no legal actions".into()); }
    if actions.iter().any(|a| a.actor != observation.actor) { return Err("legal action actor differs from observation actor".into()); }
    let mut ordered = actions.to_vec();
    canonical_actions(&mut ordered);
    let mut questions = Map::new();
    for (index, action) in ordered.iter().enumerate() {
        questions.insert(action_id(index), json!({"type":"score", "criteria":LEVELS,
            "instructions": {"task":"Rate taking this legal action now for the acting player's eventual chance of winning this Pokemon TCG Pocket game. Use the same rubric for every action. Consider multi-turn setup, resource conservation, point prizes and visible opponent threats. Unknown cards are unknown; do not assume access to the opponent's hand, deck list or future draws. Card effects supplied in the observation are authoritative.",
                "acting_player":observation.actor, "candidate_action":action}}));
    }
    Ok((json!({"model":model, "state":{
        "game":"Pokemon TCG Pocket",
        "rules":"Win at 3 points or when the opponent has no Pokemon in play. Normal Pokemon give 1 point, Pokemon ex 2, Mega Evolution Pokemon ex 3. Bench has 3 slots; board index 0 is Active. No deck-out loss. Energy comes from the Energy Zone, not energy cards. Actions supplied are already legal. Attack ends the turn. Unknown cards must not be inferred as known. known_own_deck is an unordered multiset, not draw order. The observation template is redacted; use only provided information.",
        "observation":observation}, "questions":questions}), ordered))
}

fn select(response: &Value, count: usize) -> Result<usize, String> {
    if count == 0 { return Err("no actions to score".into()); }
    if response.get("model").and_then(Value::as_str).is_none_or(str::is_empty) {
        return Err("missing response model".into());
    }
    for field in ["input_tokens", "output_tokens"] {
        if response.get("usage").and_then(|u| u.get(field)).and_then(Value::as_u64).is_none() {
            return Err(format!("missing or invalid usage.{field}"));
        }
    }
    let answers = response.get("answers").and_then(Value::as_object).ok_or("missing answers")?;
    if answers.len() != count { return Err("answer count differs from legal-action count".into()); }
    let mut best = (0, f64::NEG_INFINITY);
    for index in 0..count {
        let answer = answers.get(&action_id(index)).ok_or("missing action answer")?;
        if answer.get("type").and_then(Value::as_str) != Some("score") { return Err("non-Score answer".into()); }
        let score = answer.get("score").and_then(Value::as_f64).ok_or("missing score")?;
        let confidence = answer.get("confidence").and_then(Value::as_f64).ok_or("missing confidence")?;
        if !score.is_finite() || !(0.0..=4.0).contains(&score) || !(0.0..=1.0).contains(&confidence) {
            return Err("invalid score or confidence".into());
        }
        let probabilities = answer.get("probabilities").and_then(Value::as_object).ok_or("missing probabilities")?;
        let legend = answer.get("legend").and_then(Value::as_object).ok_or("missing legend")?;
        if probabilities.len() != LEVELS.len() || legend.len() != LEVELS.len() { return Err("invalid score levels".into()); }
        let (mut total, mut weighted) = (0.0, 0.0);
        for (level, description) in LEVELS.iter().enumerate() {
            let key = level.to_string();
            if legend.get(&key).and_then(Value::as_str) != Some(*description) { return Err("rubric legend mismatch".into()); }
            let p = probabilities.get(&key).and_then(Value::as_f64).ok_or("missing level probability")?;
            if !(0.0..=1.0).contains(&p) { return Err("invalid level probability".into()); }
            total += p;
            weighted += p * level as f64;
        }
        // API probabilities and score are independently rounded to hundredths.
        // Five probabilities allow 5 * .005 sum error. The weighted sum allows
        // .005 * (0+1+2+3+4), plus .005 score rounding and floating-point epsilon.
        if (total - 1.0).abs() > 0.0250001 || (weighted - score).abs() > 0.0550001 {
            return Err("score/probability distribution mismatch".into());
        }
        // Strict greater-than preserves canonical action order for exact ties.
        if score > best.1 { best = (index, score); }
    }
    Ok(best.0)
}

impl Player for JevPlayer {
    fn get_deck(&self) -> Deck { self.deck.clone() }
    fn decision_fn(&mut self, _: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
        self.decide(observation, actions).unwrap_or_else(|error| panic!("Jev decision failed; no fallback: {error}"))
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, _: &[Action]) -> Action {
        panic!("JevPlayer refuses State; use PlayerObservation through decision_fn")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{actions::SimpleAction, observation::RevealedKnowledge, card_ids::CardId, database::get_card_by_enum};
    use rand::SeedableRng;
    fn response(levels: &[usize]) -> Value {
        let mut answers = Map::new();
        for (index, &selected) in levels.iter().enumerate() {
            let mut probabilities = Map::new(); let mut legend = Map::new();
            for (level, description) in LEVELS.iter().enumerate() {
                probabilities.insert(level.to_string(), json!(if level == selected {1.0} else {0.0}));
                legend.insert(level.to_string(), json!(description));
            }
            answers.insert(action_id(index), json!({"type":"score", "score":selected,
                "confidence":1.0,"legend":legend,"probabilities":probabilities}));
        }
        json!({"model":"jev-test","usage":{"input_tokens":321,"output_tokens":0},"answers":answers})
    }
    #[test]
    fn legal_maximum_and_canonical_tie() {
        assert_eq!(select(&response(&[1,4,2]),3).unwrap(),1);
        assert_eq!(select(&response(&[4,4,2]),3).unwrap(),0);
        assert_eq!(select(&response(&[0]),1).unwrap(),0);
    }
    #[test]
    fn accepts_live_hundredth_rounded_scores_without_changing_rank() {
        let mut live = response(&[3,2]);
        for (index, (probabilities, score, confidence)) in [
            ([0.02,0.07,0.17,0.44,0.30],2.94,0.46),
            ([0.02,0.14,0.39,0.38,0.07],2.35,0.42),
        ].iter().enumerate() {
            let answer = &mut live["answers"][action_id(index)];
            answer["score"] = json!(score);
            answer["confidence"] = json!(confidence);
            for (level,p) in probabilities.iter().enumerate() {
                answer["probabilities"][level.to_string()] = json!(p);
            }
        }
        assert_eq!(select(&live,2).unwrap(),0);
        let mut bad_sum = live.clone();
        bad_sum["answers"]["action_000000"]["probabilities"]["4"] = json!(0.33);
        bad_sum["answers"]["action_000000"]["score"] = json!(3.05);
        assert!(select(&bad_sum,2).is_err());
        let mut bad_score = live.clone();
        bad_score["answers"]["action_000000"]["score"] = json!(2.99);
        assert!(select(&bad_score,2).is_err());
        for invalid in [-0.01,1.01] {
            let mut bad = live.clone();
            bad["answers"]["action_000000"]["probabilities"]["0"] = json!(invalid);
            assert!(select(&bad,2).is_err());
        }
    }
    #[test]
    fn invalid_responses_never_pick_a_fallback() {
        let good = response(&[1,4]);
        for path in ["score","probabilities","legend","confidence","type"] {
            let mut bad = good.clone(); bad["answers"]["action_000000"].as_object_mut().unwrap().remove(path);
            assert!(select(&bad,2).is_err(),"{path}");
        }
        let mut bad = good.clone(); bad["answers"]["action_000000"]["score"]=json!(4);
        assert!(select(&bad,2).is_err());
        assert!(select(&good,3).is_err());
        let mut bad = good; bad.as_object_mut().unwrap().remove("usage"); assert!(select(&bad,2).is_err());
    }
    #[test]
    fn request_is_one_score_per_action_and_private_information_invariant() {
        let mut state = State::new(&Deck::default(), &Deck::default());
        state.turn_count=3;
        state.decks[0].cards=vec![get_card_by_enum(CardId::PA001Potion),get_card_by_enum(CardId::PA002XSpeed)];
        state.hands[1]=vec![get_card_by_enum(CardId::A1003Venusaur)];
        state.decks[1].cards=vec![get_card_by_enum(CardId::A1002Ivysaur)];
        let actions=vec![Action{actor:0,action:SimpleAction::EndTurn,is_stack:false},
            Action{actor:0,action:SimpleAction::Retreat(1),is_stack:false}];
        let original=PlayerObservation::from_state(&state,0,&RevealedKnowledge::default());
        let (first, ordered)=request(&original,&actions,"jev-test").unwrap();
        state.decks[0].cards.reverse();
        state.hands[1][0]=get_card_by_enum(CardId::PA006RedCard);
        state.decks[1].cards[0]=get_card_by_enum(CardId::PA007ProfessorsResearch);
        let changed=PlayerObservation::from_state(&state,0,&RevealedKnowledge::default());
        let mut reversed=actions.clone(); reversed.reverse();
        assert_eq!(first,request(&changed,&reversed,"jev-test").unwrap().0);
        assert_eq!(first["questions"].as_object().unwrap().len(),actions.len());
        for (i,action) in ordered.iter().enumerate() {
            assert_eq!(first["questions"][action_id(i)]["type"],"score");
            assert_eq!(first["questions"][action_id(i)]["instructions"]["candidate_action"],json!(action));
        }
    }
    #[test]
    #[should_panic(expected="JevPlayer refuses State")]
    fn refuses_omniscient_entry() {
        let mut player=JevPlayer::new(Deck::default());
        player.decide_omniscient(&mut StdRng::seed_from_u64(1),&State::new(&Deck::default(),&Deck::default()),&[]);
    }
    #[test]
    fn parses_jev_without_changing_k3() {
        assert_eq!(super::super::parse_player_code("JEV").unwrap(),super::super::PlayerCode::Jev);
        assert_eq!(super::super::parse_player_code("k3").unwrap(),super::super::PlayerCode::K{max_depth:3});
    }
}
