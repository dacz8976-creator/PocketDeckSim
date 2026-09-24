//! Training interface over the Pocket Deck Lab engine (deckgym-unified1).
//!
//! Hidden-information rule: every number handed to a learner comes from
//! `Game::observation(player)` (a `PlayerObservation`) or from the legal-action list the
//! engine already hands its own bots. The raw `State` is used only to (a) ask the engine
//! which actions are legal and whose turn it is, exactly as `Game::play_tick` does, and
//! (b) the clearly named `label_immediate_wins`, which exists for measuring the step-3
//! test and must never feed training.
use std::collections::HashMap;

use deckgym::actions::Action;
use deckgym::models::{Card, EnergyType};
use deckgym::observation::{canonical_actions, PlayerObservation};
use deckgym::players::{create_players, parse_player_code, Player, PlayerCode};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use pyo3::exceptions::{PyIndexError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rand::rngs::StdRng;
use rand::seq::SliceRandom;
use rand::{Rng, SeedableRng};
use serde_json::Value;

mod v2;
use std::cell::RefCell;

const HASH_BUCKETS: usize = 128;
const SLOT_FEATURES: usize = 26;
const N_ENERGY: usize = 10;
const N_SCALARS: usize = 16;
const N_CARD_BLOCKS: usize = 10;

fn energy_index(e: &EnergyType) -> usize {
    match e {
        EnergyType::Grass => 0,
        EnergyType::Fire => 1,
        EnergyType::Water => 2,
        EnergyType::Lightning => 3,
        EnergyType::Psychic => 4,
        EnergyType::Fighting => 5,
        EnergyType::Darkness => 6,
        EnergyType::Metal => 7,
        EnergyType::Dragon => 8,
        EnergyType::Colorless => 9,
    }
}

fn fnv1a(s: &str) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for b in s.as_bytes() {
        h ^= *b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

/// Walks an action's serde form. Card objects (anything with string `id` and `name`)
/// become card ids; every other leaf becomes a short token that is hashed into buckets.
fn walk(v: &Value, key: &str, toks: &mut Vec<String>, cards: &mut Vec<String>) {
    match v {
        Value::Object(m) => {
            if let (Some(Value::String(id)), Some(Value::String(_))) = (m.get("id"), m.get("name")) {
                cards.push(id.clone());
                toks.push(format!("{key}:card"));
                return;
            }
            for (k, vv) in m {
                walk(vv, k, toks, cards);
            }
        }
        Value::Array(a) => {
            toks.push(format!("{key}:len={}", a.len().min(6)));
            for x in a {
                walk(x, key, toks, cards);
            }
        }
        Value::String(s) => toks.push(format!("{key}={s}")),
        Value::Number(n) => toks.push(format!("{key}={}", n.as_i64().unwrap_or(0).clamp(-1, 400))),
        Value::Bool(b) => toks.push(format!("{key}={b}")),
        Value::Null => {}
    }
}

fn action_tokens(action: &Action) -> (Vec<String>, Vec<String>) {
    let mut toks = Vec::new();
    let mut cards = Vec::new();
    let v = serde_json::to_value(&action.action).expect("actions are serializable");
    match &v {
        Value::String(s) => toks.push(format!("V:{s}")),
        Value::Object(m) => {
            for (k, vv) in m {
                toks.push(format!("V:{k}"));
                walk(vv, k, &mut toks, &mut cards);
            }
        }
        other => toks.push(format!("V:{other}")),
    }
    if action.is_stack {
        toks.push("is_stack".into());
    }
    (toks, cards)
}

fn outcome_reward(winner: &Option<GameOutcome>, player: usize) -> Option<f32> {
    match winner {
        Some(GameOutcome::Win(p)) => Some(if *p == player { 1.0 } else { -1.0 }),
        Some(GameOutcome::Tie) => Some(0.0),
        None => None,
    }
}

/// What `player` can see, as readable JSON, built only from PlayerObservation (transcripts).
fn describe_view(game: &Game<'static>, player: usize) -> String {
    let obs = game.observation(player);
    let s = obs.visible_state();
    let names = |cards: &[Card]| -> Vec<String> {
        cards.iter().map(|c| if c.is_unknown() { "?".to_string() } else { c.get_name() }).collect()
    };
    let side = |p: usize| -> Value {
        let slots: Vec<Value> = s.in_play_pokemon[p]
            .iter()
            .map(|slot| match slot {
                None => Value::Null,
                Some(pc) => {
                    let (printed, ex) = match &pc.card {
                        Card::Pokemon(pk) => (pk.hp, pk.name.ends_with(" ex")),
                        _ => (0, false),
                    };
                    let mut status = Vec::new();
                    for (on, label) in [(pc.is_poisoned(), "Poisoned"), (pc.is_asleep(), "Asleep"),
                                        (pc.is_paralyzed(), "Paralyzed"), (pc.is_burned(), "Burned"),
                                        (pc.is_confused(), "Confused")] {
                        if on {
                            status.push(label);
                        }
                    }
                    serde_json::json!({
                        "name": pc.card.get_name(), "hp_left": pc.get_remaining_hp(), "hp_card": printed,
                        "ex": ex,
                        "energy": pc.attached_energy.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
                        "tools": names(&pc.attached_tools), "status": status,
                        "played_this_turn": pc.played_this_turn, "ability_used": pc.ability_used,
                    })
                }
            })
            .collect();
        let deck: Value = if p == player {
            let mut d = names(&obs.known_own_deck);
            d.sort();
            serde_json::json!({"size": d.len(), "contents_unordered": d})
        } else {
            serde_json::json!({"size": s.decks[p].cards.len()})
        };
        serde_json::json!({
            "points": s.points[p], "hand": names(&s.hands[p]), "deck": deck,
            "discard": names(&s.discard_piles[p]), "board": slots,
            "energy_now": s.energy_zone[p].current.map(|e| format!("{e:?}")),
            "energy_next": s.energy_zone[p].next.map(|e| format!("{e:?}")),
        })
    };
    let v = serde_json::json!({
        "viewer": player, "turn": s.turn_count, "current_player": s.current_player,
        "opponent_setup_hidden": s.setup_opponent_hidden,
        "stadium": s.active_stadium.as_ref().map(|c| c.get_name()),
        "me": side(player), "them": side(1 - player),
    });
    v.to_string()
}

/// ANALYSIS ONLY (knockout audit), never a training input: applies each action to copies of
/// the true state under `k` chance seeds and reports, per action, the fewest / most points the
/// actor gains, the fewest / most the opponent gains, and in how many seeds the actor wins.
fn action_outcomes(base: &State, decks: &[Deck; 2], actor: usize, actions: &[Action], k: u64)
    -> Vec<(u8, u8, u8, u8, u64)> {
    let before = base.points;
    actions
        .iter()
        .map(|a| {
            let (mut min_me, mut max_me, mut min_op, mut max_op, mut wins) = (u8::MAX, 0u8, u8::MAX, 0u8, 0u64);
            for s in 0..k {
                let players = create_players(decks[0].clone(), decks[1].clone(), vec![PlayerCode::R, PlayerCode::R]);
                let mut g = Game::from_state(base.clone(), players, 0x5eed_0000 + s);
                g.apply_action(a);
                let after = g.get_state_clone();
                let me = after.points[actor].saturating_sub(before[actor]);
                let op = after.points[1 - actor].saturating_sub(before[1 - actor]);
                min_me = min_me.min(me);
                max_me = max_me.max(me);
                min_op = min_op.min(op);
                max_op = max_op.max(op);
                if matches!(after.winner, Some(GameOutcome::Win(p)) if p == actor) {
                    wins += 1;
                }
            }
            (min_me, max_me, min_op, max_op, wins)
        })
        .collect()
}

#[pyclass]
#[derive(Clone)]
struct Snapshot {
    state: State,
}

#[pyclass(unsendable)]
struct RawEnv {
    vocab: HashMap<String, usize>,
    vocab_list: Vec<String>,
    deck_cache: HashMap<String, Deck>,
    decks: Option<[Deck; 2]>,
    game: Option<Game<'static>>,
    bots: [bool; 2],
    actor: Option<usize>,
    actions: Vec<Action>,
    winner: Option<GameOutcome>,
    agent_decisions: u64,
    forced_moves: u64,
    bot_moves: u64,
    // Transcript support: every applied move, when recording is on (off by default).
    record: bool,
    history: Vec<(usize, &'static str, String, String)>,
    // Knockout audit: engine-bot decisions with each option's outcome (off by default).
    audit: bool,
    audit_k: u64,
    bot_decisions: Vec<String>,
    // Encoding v2 (consequence + threat features); false = v1, byte-identical to 0.1.0.
    v2: bool,
    // v2.2: the two "losing the Active" numbers in place of the threat "certain" flag (v2.1 unchanged).
    v22: bool,
    serial: u64,
    cache: RefCell<Option<(u64, usize, Vec<f32>, Option<Vec<f32>>, bool)>>,
}

impl RawEnv {
    fn card_index(&self, card: &Card) -> usize {
        if card.is_unknown() {
            return 0;
        }
        *self.vocab.get(&card.get_id()).unwrap_or(&1)
    }

    fn n_cards(&self) -> usize {
        self.vocab_list.len() + 2
    }

    fn load_deck(&mut self, path: &str) -> PyResult<Deck> {
        if let Some(d) = self.deck_cache.get(path) {
            return Ok(d.clone());
        }
        let d = Deck::from_file(path).map_err(|e| PyValueError::new_err(format!("deck {path}: {e}")))?;
        self.deck_cache.insert(path.to_string(), d.clone());
        Ok(d)
    }

    fn game(&self) -> PyResult<&Game<'static>> {
        self.game.as_ref().ok_or_else(|| PyRuntimeError::new_err("call reset() first"))
    }

    fn carrier_players(&self) -> Vec<Box<dyn Player>> {
        let d = self.decks.as_ref().expect("decks set");
        create_players(d[0].clone(), d[1].clone(), vec![PlayerCode::R, PlayerCode::R])
    }

    /// Plays forced single-option moves and engine-bot seats until an agent seat has a real
    /// choice (2+ legal actions) or the game ends. Mirrors `Game::play_tick`.
    fn advance(&mut self) {
        self.serial += 1;
        let game = self.game.as_mut().expect("game");
        loop {
            let state = game.get_state_clone();
            if state.winner.is_some() {
                self.winner = state.winner.clone();
                self.actor = None;
                self.actions.clear();
                return;
            }
            let (actor, mut actions) = state.generate_possible_actions();
            if self.bots[actor] {
                let view = if self.record { describe_view(game, actor) } else { String::new() };
                let audit_info = if self.audit {
                    let mut acts = actions.clone();
                    canonical_actions(&mut acts);
                    let decks = self.decks.as_ref().expect("decks set");
                    let outs = action_outcomes(&state, decks, actor, &acts, self.audit_k);
                    Some((acts, outs))
                } else {
                    None
                };
                let done = game.play_tick();
                if let Some((acts, outs)) = audit_info {
                    let chosen = acts.iter().position(|a| *a == done).map(|i| i as i64).unwrap_or(-1);
                    let kinds: Vec<String> = acts.iter().map(|a| {
                        let (t, c) = action_tokens(a);
                        format!("{} {}", t.first().cloned().unwrap_or_default(), c.join(","))
                    }).collect();
                    self.bot_decisions.push(serde_json::json!({
                        "actor": actor, "turn": state.turn_count, "points": state.points,
                        "moves": kinds, "outcomes": outs, "chosen": chosen,
                    }).to_string());
                }
                if self.record {
                    self.history.push((actor, "bot", serde_json::to_string(&done.action).unwrap(), view));
                }
                self.bot_moves += 1;
                continue;
            }
            canonical_actions(&mut actions);
            if actions.len() == 1 {
                game.apply_action(&actions[0]);
                if self.record {
                    self.history.push((actor, "forced", serde_json::to_string(&actions[0].action).unwrap(), String::new()));
                }
                self.forced_moves += 1;
                continue;
            }
            self.actor = Some(actor);
            self.actions = actions;
            return;
        }
    }

    fn encode_obs(&self, obs: &PlayerObservation) -> Vec<f32> {
        let s = obs.visible_state();
        let me = obs.actor;
        let op = 1 - me;
        let c = self.n_cards();
        let mut out = vec![0f32; N_SCALARS + N_CARD_BLOCKS * c + 8 * SLOT_FEATURES + 4 * (N_ENERGY + 1)];
        // Scalars
        let known_opp_hand = s.hands[op].iter().filter(|x| !x.is_unknown()).count();
        let sc = [
            s.turn_count as f32 / 30.0,
            (s.current_player == me) as u8 as f32,
            s.points[me] as f32 / 3.0,
            s.points[op] as f32 / 3.0,
            s.hands[me].len() as f32 / 10.0,
            s.hands[op].len() as f32 / 10.0,
            obs.known_own_deck.len() as f32 / 20.0,
            s.decks[op].cards.len() as f32 / 20.0,
            s.discard_piles[me].len() as f32 / 20.0,
            s.discard_piles[op].len() as f32 / 20.0,
            s.setup_opponent_hidden as u8 as f32,
            (!s.move_generation_stack.is_empty()) as u8 as f32,
            (s.pending_attack_coin_choice.is_some()
                || s.pending_trainer_coin_choice.is_some()
                || s.pending_misty_target_choice.is_some()) as u8 as f32,
            (s.active_stadium_owner == Some(me)) as u8 as f32,
            (s.active_stadium_owner == Some(op)) as u8 as f32,
            known_opp_hand as f32 / 10.0,
        ];
        out[..N_SCALARS].copy_from_slice(&sc);
        let mut o = N_SCALARS;
        // Card-count blocks over the vocabulary
        let mut block = |cards: &mut dyn Iterator<Item = &Card>, out: &mut Vec<f32>, o: usize| {
            for card in cards {
                out[o + self.card_index(card)] += 1.0;
            }
        };
        block(&mut s.hands[me].iter(), &mut out, o);
        o += c;
        block(&mut obs.known_own_deck.iter(), &mut out, o);
        o += c;
        block(&mut s.discard_piles[me].iter(), &mut out, o);
        o += c;
        block(&mut s.discard_piles[op].iter(), &mut out, o);
        o += c;
        block(&mut s.hands[op].iter().filter(|x| !x.is_unknown()), &mut out, o);
        o += c;
        for p in [me, op] {
            block(&mut s.in_play_pokemon[p].iter().flatten().map(|pc| &pc.card), &mut out, o);
            o += c;
        }
        for p in [me, op] {
            if let Some(pc) = &s.in_play_pokemon[p][0] {
                out[o + self.card_index(&pc.card)] = 1.0;
            }
            o += c;
        }
        if let Some(st) = &s.active_stadium {
            out[o + self.card_index(st)] = 1.0;
        }
        o += c;
        // Board slots: mine 0..3 then opponent's 0..3
        for p in [me, op] {
            for slot in 0..4 {
                if let Some(pc) = &s.in_play_pokemon[p][slot] {
                    let (base_hp, is_ex, stage) = match &pc.card {
                        Card::Pokemon(pk) => (pk.hp as f32, pk.name.ends_with(" ex") as u8 as f32, pk.stage as f32),
                        _ => (0.0, 0.0, 0.0),
                    };
                    out[o] = 1.0;
                    out[o + 1] = pc.get_remaining_hp() as f32 / 250.0;
                    out[o + 2] = base_hp / 250.0;
                    for e in &pc.attached_energy {
                        out[o + 3 + energy_index(e)] += 1.0 / 3.0;
                    }
                    out[o + 13] = pc.attached_energy.len() as f32 / 5.0;
                    out[o + 14] = pc.attached_tools.len() as f32;
                    out[o + 15] = pc.is_poisoned() as u8 as f32;
                    out[o + 16] = pc.is_asleep() as u8 as f32;
                    out[o + 17] = pc.is_paralyzed() as u8 as f32;
                    out[o + 18] = pc.is_burned() as u8 as f32;
                    out[o + 19] = pc.is_confused() as u8 as f32;
                    out[o + 20] = is_ex;
                    out[o + 21] = stage / 2.0;
                    out[o + 22] = pc.card.get_retreat_cost().map(|r| r.len()).unwrap_or(0) as f32 / 4.0;
                    out[o + 23] = pc.played_this_turn as u8 as f32;
                    out[o + 24] = pc.ability_used as u8 as f32;
                    out[o + 25] = pc.has_attacked_since_play as u8 as f32;
                }
                o += SLOT_FEATURES;
            }
        }
        // Energy zones as the observation exposes them
        for p in [me, op] {
            for e in [&s.energy_zone[p].current, &s.energy_zone[p].next] {
                let idx = e.as_ref().map(|x| 1 + energy_index(x)).unwrap_or(0);
                out[o + idx] = 1.0;
                o += N_ENERGY + 1;
            }
        }
        debug_assert_eq!(o, out.len());
        out
    }

    fn encode_action(&self, action: &Action, out: &mut [f32]) {
        let (toks, cards) = action_tokens(action);
        for t in &toks {
            out[(fnv1a(t) % HASH_BUCKETS as u64) as usize] = 1.0;
        }
        for id in &cards {
            let idx = if id.is_empty() { 0 } else { *self.vocab.get(id).unwrap_or(&1) };
            out[HASH_BUCKETS + idx] += 1.0;
        }
    }

    fn obs_len(&self) -> usize {
        N_SCALARS + N_CARD_BLOCKS * self.n_cards() + 8 * SLOT_FEATURES + 4 * (N_ENERGY + 1)
            + if self.v2 { v2::O2 + 2 * self.n_cards() } else { 0 }
    }

    fn act_len(&self) -> usize {
        HASH_BUCKETS + self.n_cards() + if self.v22 { v2::A2_V22 } else if self.v2 { v2::A2 } else { 0 }
    }

    /// Observation vector and (when `actions` is given) the action-feature matrix, in the
    /// configured encoding. Built only from the PlayerObservation and the offered move list.
    fn full_features(&self, obs: &PlayerObservation, actions: Option<&[Action]>) -> (Vec<f32>, Option<Vec<f32>>, bool) {
        let mut o = self.encode_obs(obs);
        let al = self.act_len();
        let mut acts = actions.map(|list| {
            let mut out = vec![0f32; al * list.len()];
            for (i, a) in list.iter().enumerate() {
                self.encode_action(a, &mut out[i * al..(i + 1) * al]);
            }
            out
        });
        let mut lookahead_new_rule_frame_seen = false;
        if self.v2 {
            let (extra, rows, seen) = v2::features(obs, actions.unwrap_or(&[]), self.v22);
            lookahead_new_rule_frame_seen = seen;
            o.extend_from_slice(&extra);
            let c = self.n_cards();
            let s = obs.visible_state();
            for p in [obs.actor, 1 - obs.actor] {
                let base = o.len();
                o.resize(base + c, 0.0);
                for pc in s.in_play_pokemon[p].iter().flatten() {
                    for t in &pc.attached_tools {
                        o[base + self.card_index(t)] += 1.0;
                    }
                }
            }
            if let Some(m) = acts.as_mut() {
                let v1 = HASH_BUCKETS + c;
                let n = if self.v22 { v2::A2_V22 } else { v2::A2 };  // v2.1 rows stop before the v2.2 slots
                for (i, r) in rows.iter().enumerate() {
                    m[i * al + v1..(i + 1) * al].copy_from_slice(&r[..n]);
                }
            }
        }
        debug_assert_eq!(o.len(), self.obs_len());
        (o, acts, lookahead_new_rule_frame_seen)
    }

    /// Cached per decision so observe() + action_features() run the v2 lookahead once.
    fn cached(&self, player: usize, want_actions: bool) -> PyResult<(Vec<f32>, Option<Vec<f32>>, bool)> {
        if let Some((serial, p, o, a, seen)) = self.cache.borrow().as_ref() {
            if *serial == self.serial && *p == player && (!want_actions || a.is_some()) {
                return Ok((o.clone(), a.clone(), *seen));
            }
        }
        let obs = self.game()?.observation(player);
        let acts = if self.actor == Some(player) { Some(&self.actions[..]) } else { None };
        let (o, a, seen) = self.full_features(&obs, acts);
        *self.cache.borrow_mut() = Some((self.serial, player, o.clone(), a.clone(), seen));
        Ok((o, a, seen))
    }
}

fn f32_bytes<'py>(py: Python<'py>, v: &[f32]) -> Bound<'py, PyBytes> {
    let bytes: Vec<u8> = v.iter().flat_map(|x| x.to_le_bytes()).collect();
    PyBytes::new_bound(py, &bytes)
}

#[pymethods]
impl RawEnv {
    /// `vocab_ids`: card ids that get their own feature slot; anything else maps to "other".
    #[new]
    #[pyo3(signature = (vocab_ids, features="v1"))]
    fn new(vocab_ids: Vec<String>, features: &str) -> PyResult<Self> {
        let (v2, v22) = match features {
            "v1" => (false, false),
            "v2.1" => (true, false),
            "v2.2" => (true, true),
            "v2" => return Err(PyValueError::new_err(
                "feature set \"v2\" is the September 18 cloud pilot's encoding (add-on 0.4.0, wheels/run2/pdl_rl_env-0.4.0); \
                 this add-on (0.7.2) has the corrected \"v2.1\" (Astra's review fixes) and \"v2.2\". Install 0.4.0 to use pilot checkpoints.")),
            other => return Err(PyValueError::new_err(format!("unknown feature set {other:?} (v1, v2.1 or v2.2)"))),
        };
        let mut vocab_list = vocab_ids;
        vocab_list.sort();
        vocab_list.dedup();
        let vocab = vocab_list.iter().enumerate().map(|(i, id)| (id.clone(), i + 2)).collect();
        Ok(RawEnv {
            vocab,
            vocab_list,
            deck_cache: HashMap::new(),
            decks: None,
            game: None,
            bots: [false, false],
            actor: None,
            actions: Vec::new(),
            winner: None,
            agent_decisions: 0,
            forced_moves: 0,
            bot_moves: 0,
            record: false,
            history: Vec::new(),
            audit: false,
            audit_k: 4,
            bot_decisions: Vec::new(),
            v2,
            v22,
            serial: 0,
            cache: RefCell::new(None),
        })
    }

    /// "v1", "v2.1" or "v2.2".
    #[getter]
    fn features(&self) -> &'static str {
        if self.v22 { "v2.2" } else if self.v2 { "v2.1" } else { "v1" }
    }

    /// v2 lookahead counters in this process: (forecasts run, refused as hidden/unpriceable, panics caught).
    #[staticmethod]
    fn v2_stats() -> (u64, u64, u64) {
        v2::STATS.with(|s| s.get())
    }

    /// ANALYSIS ONLY: per-action public forecast status and a decision-wide trace showing
    /// whether any nested lookahead encountered a new rules3 continuation frame.
    fn forecast_diagnostics(&self) -> PyResult<Vec<String>> {
        if !self.v2 {
            return Err(PyValueError::new_err("forecast diagnostics require v2.1 or v2.2"));
        }
        let actor = self.actor.ok_or_else(|| PyRuntimeError::new_err("no pending decision"))?;
        let (_, _, seen) = self.cached(actor, true)?;
        let obs = self.game()?.observation(actor);
        Ok(v2::diagnostics(&obs, &self.actions, seen))
    }

    /// Card ids listed in a deck file (for building a vocabulary).
    #[staticmethod]
    fn deck_card_ids(path: &str) -> PyResult<Vec<String>> {
        let d = Deck::from_file(path).map_err(|e| PyValueError::new_err(format!("deck {path}: {e}")))?;
        let mut ids: Vec<String> = d.cards.iter().map(|c| c.get_id()).collect();
        ids.sort();
        ids.dedup();
        Ok(ids)
    }

    #[getter]
    fn vocab(&self) -> Vec<String> {
        self.vocab_list.clone()
    }
    #[getter]
    fn obs_dim(&self) -> usize {
        self.obs_len()
    }
    #[getter]
    fn action_dim(&self) -> usize {
        self.act_len()
    }

    /// New game. `bots[i]` = engine player code (e.g. "k3", "r") to let the engine drive
    /// seat i, or None for a seat the caller drives through `step`.
    #[pyo3(signature = (deck_a_path, deck_b_path, seed, bots=None))]
    fn reset(&mut self, deck_a_path: &str, deck_b_path: &str, seed: u64, bots: Option<Vec<Option<String>>>) -> PyResult<()> {
        let da = self.load_deck(deck_a_path)?;
        let db = self.load_deck(deck_b_path)?;
        let bots = bots.unwrap_or_else(|| vec![None, None]);
        if bots.len() != 2 {
            return Err(PyValueError::new_err("bots must have two entries"));
        }
        let mut codes = Vec::new();
        for b in &bots {
            codes.push(match b {
                Some(code) => parse_player_code(code).map_err(PyValueError::new_err)?,
                None => PlayerCode::R,
            });
        }
        self.bots = [bots[0].is_some(), bots[1].is_some()];
        let players = create_players(da.clone(), db.clone(), codes);
        self.decks = Some([da, db]);
        self.game = Some(Game::new(players, seed));
        self.winner = None;
        self.agent_decisions = 0;
        self.forced_moves = 0;
        self.bot_moves = 0;
        self.history.clear();
        self.bot_decisions.clear();
        self.advance();
        Ok(())
    }

    /// Whose decision is pending (None when the game is over).
    #[getter]
    fn current_player(&self) -> Option<usize> {
        self.actor
    }
    #[getter]
    fn done(&self) -> bool {
        self.winner.is_some()
    }
    #[getter]
    fn counters(&self) -> (u64, u64, u64) {
        (self.agent_decisions, self.forced_moves, self.bot_moves)
    }

    /// Fixed-length f32 vector (little-endian bytes) built only from PlayerObservation.
    fn observe<'py>(&self, py: Python<'py>, player: usize) -> PyResult<Bound<'py, PyBytes>> {
        if player > 1 {
            return Err(PyIndexError::new_err("player must be 0 or 1"));
        }
        if !self.v2 {
            let obs = self.game()?.observation(player);
            return Ok(f32_bytes(py, &self.encode_obs(&obs)));
        }
        Ok(f32_bytes(py, &self.cached(player, false)?.0))
    }

    fn num_actions(&self) -> usize {
        self.actions.len()
    }

    /// Short readable form of each legal action, in the engine's canonical order.
    fn legal_actions(&self) -> Vec<String> {
        self.actions
            .iter()
            .map(|a| {
                let (toks, cards) = action_tokens(a);
                let names: Vec<String> = cards;
                format!("{} {}", toks.first().cloned().unwrap_or_default(), names.join(","))
            })
            .collect()
    }

    /// (n_actions x action_dim) f32 matrix, little-endian bytes, rows in legal_actions order.
    fn action_features<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        if self.v2 {
            if let Some(actor) = self.actor {
                if let Ok((_, Some(m), _)) = self.cached(actor, true) {
                    return f32_bytes(py, &m);
                }
            }
            return f32_bytes(py, &[]);
        }
        let a = self.action_dim();
        let mut out = vec![0f32; a * self.actions.len()];
        for (i, act) in self.actions.iter().enumerate() {
            self.encode_action(act, &mut out[i * a..(i + 1) * a]);
        }
        f32_bytes(py, &out)
    }

    /// Apply legal action `index` for the current player. Raises on an illegal index or a
    /// finished game; never silently passes.
    fn step(&mut self, index: i64) -> PyResult<bool> {
        if self.game.is_none() {
            return Err(PyRuntimeError::new_err("call reset() first"));
        }
        if self.winner.is_some() {
            return Err(PyRuntimeError::new_err("game is over"));
        }
        if index < 0 || index as usize >= self.actions.len() {
            return Err(PyIndexError::new_err(format!(
                "illegal action index {index}: {} legal actions",
                self.actions.len()
            )));
        }
        let action = self.actions[index as usize].clone();
        self.game.as_mut().unwrap().apply_action(&action);
        if self.record {
            self.history.push((action.actor, "agent", serde_json::to_string(&action.action).unwrap(), String::new()));
        }
        self.agent_decisions += 1;
        self.advance();
        Ok(self.winner.is_some())
    }

    /// Terminal reward for `player`: +1 win, -1 loss, 0 draw. Raises if the game is not over.
    fn reward(&self, player: usize) -> PyResult<f32> {
        outcome_reward(&self.winner, player).ok_or_else(|| PyRuntimeError::new_err("game not over"))
    }

    /// Engine's own record of the result: (winner seat or -1 for a draw, points).
    fn result(&self) -> PyResult<(i64, [u8; 2], u8)> {
        let s = self.game()?.get_state_clone();
        let w = match &s.winner {
            Some(GameOutcome::Win(p)) => *p as i64,
            Some(GameOutcome::Tie) => -1,
            None => return Err(PyRuntimeError::new_err("game not over")),
        };
        Ok((w, s.points, s.turn_count))
    }

    /// Fingerprint of the pending decision exactly as the network is offered it: the
    /// add-on's own legal-move list, the game state, and the PlayerObservation.
    fn decision_fingerprint(&self) -> PyResult<(u64, u64, u64)> {
        let actor = self.actor.ok_or_else(|| PyRuntimeError::new_err("no pending decision"))?;
        Ok(decision_fingerprint(self.game()?, actor, &self.actions))
    }

    /// Hash of the full final game state (for exact-match tests between two paths).
    fn final_state_hash(&self) -> PyResult<u64> {
        Ok(state_hash(&self.game()?.get_state_clone()))
    }

    /// Both seats pick uniformly at random (Rust-side, fast) until the game ends.
    fn rollout_random(&mut self, seed: u64) -> PyResult<()> {
        let mut rng = StdRng::seed_from_u64(seed);
        while self.winner.is_none() {
            let i = rng.gen_range(0..self.actions.len());
            self.step(i as i64)?;
        }
        Ok(())
    }

    fn snapshot(&self) -> PyResult<Snapshot> {
        Ok(Snapshot { state: self.game()?.get_state_clone() })
    }

    /// Continue from a snapshot with a fresh chance stream `seed`. Revealed-card memory
    /// restarts empty (Game::from_state), so observations can only know less, never more.
    fn restore(&mut self, snap: &Snapshot, seed: u64) -> PyResult<()> {
        let players = self.carrier_players();
        self.game = Some(Game::from_state(snap.state.clone(), players, seed));
        self.bots = [false, false];
        self.winner = None;
        self.advance();
        Ok(())
    }

    /// Boundary test hook: rebuild the current position with the opponent's hidden cards
    /// (hand + deck) reshuffled among themselves and our own deck reordered. Our encoded
    /// observation must come out identical. Returns true when it does.
    /// `control=true` instead reshuffles OUR OWN hand with our deck (visible to us), which
    /// should change the observation whenever the hand actually changes: a positive control
    /// showing the probe can detect a difference.
    #[pyo3(signature = (seed, control=false))]
    fn hidden_info_probe(&self, seed: u64, control: bool) -> PyResult<Option<bool>> {
        let actor = match self.actor {
            Some(a) => a,
            None => return Ok(None),
        };
        let base = self.game()?.get_state_clone();
        let op = 1 - actor;
        let who = if control { actor } else { op };
        let mut alt = base.clone();
        let mut rng = StdRng::seed_from_u64(seed);
        let hn = alt.hands[who].len();
        let mut pool: Vec<Card> = alt.hands[who].drain(..).collect();
        pool.extend(alt.decks[who].cards.drain(..));
        pool.shuffle(&mut rng);
        alt.hands[who] = pool[..hn].to_vec();
        alt.decks[who].cards = pool[hn..].to_vec();
        if !control {
            alt.decks[actor].cards.shuffle(&mut rng);
        } else {
            let mut a: Vec<String> = base.hands[actor].iter().map(|c| c.get_id()).collect();
            let mut b: Vec<String> = alt.hands[actor].iter().map(|c| c.get_id()).collect();
            a.sort();
            b.sort();
            if a == b {
                return Ok(None); // same multiset: nothing to detect
            }
        }
        let g1 = Game::from_state(base, self.carrier_players(), 1);
        let g2 = Game::from_state(alt, self.carrier_players(), 1);
        // Observation and (v2) every action's consequence features, for the same offered moves.
        let f1 = self.full_features(&g1.observation(actor), Some(&self.actions));
        let f2 = self.full_features(&g2.observation(actor), Some(&self.actions));
        Ok(Some(f1.0 == f2.0 && f1.1 == f2.1))
    }

    /// Move-list leak test: rebuild the position with the opponent's hidden cards (hand +
    /// deck) reshuffled among themselves and our own deck reordered, then ask the engine for
    /// the legal moves again. The list must be identical: if it changes, which moves we are
    /// offered depends on something we can't see. Returns None when there is no decision.
    /// `control=true` reshuffles OUR OWN hand with our deck instead (visible to us), which
    /// should change the list whenever the hand's contents change.
    #[pyo3(signature = (seed, control=false))]
    fn hidden_move_probe(&self, seed: u64, control: bool) -> PyResult<Option<bool>> {
        let actor = match self.actor {
            Some(a) => a,
            None => return Ok(None),
        };
        let base = self.game()?.get_state_clone();
        let who = if control { actor } else { 1 - actor };
        let mut alt = base.clone();
        let mut rng = StdRng::seed_from_u64(seed);
        let hn = alt.hands[who].len();
        let mut pool: Vec<Card> = alt.hands[who].drain(..).collect();
        pool.extend(alt.decks[who].cards.drain(..));
        pool.shuffle(&mut rng);
        alt.hands[who] = pool[..hn].to_vec();
        alt.decks[who].cards = pool[hn..].to_vec();
        if !control {
            alt.decks[actor].cards.shuffle(&mut rng);
        }
        let list = |s: &State| {
            let (who, mut acts) = s.generate_possible_actions();
            canonical_actions(&mut acts);
            (who, acts.iter().map(|a| serde_json::to_string(a).unwrap()).collect::<Vec<_>>())
        };
        Ok(Some(list(&base) == list(&alt)))
    }

    // ---------------------------------------------------------------- transcript support
    // Read-only helpers for printing games a person can read. None of this feeds training.

    /// Knockout audit on/off (off by default). When on, every engine-bot decision is saved with
    /// each legal option's outcome under `k` chance seeds (see bot_decisions).
    #[pyo3(signature = (on, k=4))]
    fn set_audit(&mut self, on: bool, k: u64) {
        self.audit = on;
        self.audit_k = k.max(1);
    }

    /// Engine-bot decisions since the last reset (JSON strings), when the audit is on.
    fn bot_decisions(&self) -> Vec<String> {
        self.bot_decisions.clone()
    }

    /// ANALYSIS ONLY: for the pending decision, each legal option's
    /// (fewest, most points the mover gains, fewest, most points the opponent gains, wins of k).
    fn outcome_labels(&self, k: u64) -> PyResult<Vec<(u8, u8, u8, u8, u64)>> {
        let actor = self.actor.ok_or_else(|| PyRuntimeError::new_err("no pending decision"))?;
        let base = self.game()?.get_state_clone();
        let decks = self.decks.as_ref().ok_or_else(|| PyRuntimeError::new_err("call reset() first"))?;
        Ok(action_outcomes(&base, decks, actor, &self.actions, k.max(1)))
    }

    /// ANALYSIS ONLY (v2 regression checks), never a training input: for the pending decision,
    /// each legal option applied to copies of the TRUE game under `k` chance seeds, reporting
    /// (fewest, most HP lost on the opponent's side, fewest, most HP lost on the mover's side),
    /// measured the way v2 measures it (total HP remaining on that side, before minus after, floored at 0).
    fn outcome_damage(&self, k: u64) -> PyResult<Vec<(i64, i64, i64, i64)>> {
        let actor = self.actor.ok_or_else(|| PyRuntimeError::new_err("no pending decision"))?;
        let base = self.game()?.get_state_clone();
        let decks = self.decks.as_ref().ok_or_else(|| PyRuntimeError::new_err("call reset() first"))?;
        let side = |s: &State, p: usize| -> i64 {
            s.in_play_pokemon[p].iter().flatten().map(|pc| pc.get_remaining_hp() as i64).sum()
        };
        let (me0, op0) = (side(&base, actor), side(&base, 1 - actor));
        Ok(self.actions.iter().map(|a| {
            let (mut lo_op, mut hi_op, mut lo_me, mut hi_me) = (i64::MAX, i64::MIN, i64::MAX, i64::MIN);
            for sd in 0..k.max(1) {
                let players = create_players(decks[0].clone(), decks[1].clone(), vec![PlayerCode::R, PlayerCode::R]);
                let mut g = Game::from_state(base.clone(), players, 0x5eed_0000 + sd);
                g.apply_action(a);
                let after = g.get_state_clone();
                let d_op = (op0 - side(&after, 1 - actor)).max(0);
                let d_me = (me0 - side(&after, actor)).max(0);
                lo_op = lo_op.min(d_op);
                hi_op = hi_op.max(d_op);
                lo_me = lo_me.min(d_me);
                hi_me = hi_me.max(d_me);
            }
            (lo_op, hi_op, lo_me, hi_me)
        }).collect())
    }

    /// Turn move recording on or off (off by default; takes effect from the next reset).
    fn set_recording(&mut self, on: bool) {
        self.record = on;
    }

    /// Every move applied since the last reset, when recording is on:
    /// (player, "agent" | "bot" | "forced", move as JSON).
    /// (player, "agent" | "bot" | "forced", move as JSON, that player's view before an
    /// engine-bot move as JSON or "").
    fn history(&self) -> Vec<(usize, String, String, String)> {
        self.history.iter().map(|(p, k, a, v)| (*p, k.to_string(), a.clone(), v.clone())).collect()
    }

    /// The current legal moves as JSON, in the same order as legal_actions / action_features.
    fn legal_actions_json(&self) -> Vec<String> {
        self.actions.iter().map(|a| serde_json::to_string(&a.action).unwrap()).collect()
    }

    /// What `player` can see, as readable JSON, built only from PlayerObservation.
    fn describe(&self, player: usize) -> PyResult<String> {
        if player > 1 {
            return Err(PyIndexError::new_err("player must be 0 or 1"));
        }
        Ok(describe_view(self.game()?, player))
    }

    /// REFEREE VIEW, never shown to a player or used in training: both real hands and the
    /// top of both decks, for checking rules in transcripts.
    fn referee(&self) -> PyResult<String> {
        let s = self.game()?.get_state_clone();
        let names = |cards: &[Card]| -> Vec<String> { cards.iter().map(|c| c.get_name()).collect() };
        let v = serde_json::json!({
            "hands": [names(&s.hands[0]), names(&s.hands[1])],
            "deck_top5": [names(&s.decks[0].cards.iter().take(5).cloned().collect::<Vec<_>>()),
                          names(&s.decks[1].cards.iter().take(5).cloned().collect::<Vec<_>>())],
        });
        Ok(v.to_string())
    }

    /// MEASUREMENT ONLY — never a training input. For each legal action, applies it to
    /// copies of the true state under `k` chance seeds: 1 = the acting player wins in every
    /// copy, 0 = never wins, -1 = depends on chance.
    fn label_immediate_wins(&self, k: u64) -> PyResult<Vec<i8>> {
        let actor = self.actor.ok_or_else(|| PyRuntimeError::new_err("no pending decision"))?;
        let base = self.game()?.get_state_clone();
        let mut labels = Vec::new();
        for a in &self.actions {
            let mut wins = 0;
            for s in 0..k {
                let mut g = Game::from_state(base.clone(), self.carrier_players(), 0x5eed_0000 + s);
                g.apply_action(a);
                if matches!(g.get_state_clone().winner, Some(GameOutcome::Win(p)) if p == actor) {
                    wins += 1;
                }
            }
            labels.push(if wins == k { 1 } else if wins == 0 { 0 } else { -1 });
        }
        Ok(labels)
    }
}

/// Reference path: the engine's own loop (`Game::play`) with engine players on both seats.
/// Used to cross-check that the wrapper's step/advance path matches the engine exactly.
#[pyfunction]
fn engine_play(deck_a_path: &str, deck_b_path: &str, seed: u64, codes: (String, String)) -> PyResult<(i64, [u8; 2], u8)> {
    let da = Deck::from_file(deck_a_path).map_err(PyValueError::new_err)?;
    let db = Deck::from_file(deck_b_path).map_err(PyValueError::new_err)?;
    let c = vec![
        parse_player_code(&codes.0).map_err(PyValueError::new_err)?,
        parse_player_code(&codes.1).map_err(PyValueError::new_err)?,
    ];
    let mut g = Game::new(create_players(da, db, c), seed);
    g.play();
    let s = g.get_state_clone();
    let w = match &s.winner {
        Some(GameOutcome::Win(p)) => *p as i64,
        Some(GameOutcome::Tie) => -1,
        None => -2,
    };
    Ok((w, s.points, s.turn_count))
}

fn state_hash(s: &State) -> u64 {
    use std::hash::{Hash, Hasher};
    let mut h = std::collections::hash_map::DefaultHasher::new();
    s.hash(&mut h);
    h.finish()
}

fn str_hash(parts: &[String]) -> u64 {
    use std::hash::{Hash, Hasher};
    let mut h = std::collections::hash_map::DefaultHasher::new();
    parts.hash(&mut h);
    h.finish()
}

/// (legal-move list, full game state, PlayerObservation) fingerprints for one decision.
/// The move list is compared in canonical order as full serialized moves, so a missing,
/// extra or reordered option changes the first number.
fn decision_fingerprint(game: &Game<'static>, actor: usize, canonical: &[Action]) -> (u64, u64, u64) {
    let acts: Vec<String> = canonical.iter().map(|a| serde_json::to_string(a).unwrap()).collect();
    let obs = serde_json::to_string(&game.observation(actor)).unwrap();
    (str_hash(&acts), state_hash(&game.get_state_clone()), str_hash(&[obs]))
}

/// Reference game through the engine's own loop (`play_tick` for every move), recording the
/// canonical index of every real choice made by `record_seat`. Returns (indices, final-state
/// hash, (winner, points, turns)). Used to replay that seat through the add-on's `step`.
#[pyfunction]
fn engine_play_record(
    deck_a_path: &str,
    deck_b_path: &str,
    seed: u64,
    codes: (String, String),
    record_seat: usize,
) -> PyResult<(Vec<usize>, Vec<(u64, u64, u64)>, u64, (i64, [u8; 2], u8))> {
    let da = Deck::from_file(deck_a_path).map_err(PyValueError::new_err)?;
    let db = Deck::from_file(deck_b_path).map_err(PyValueError::new_err)?;
    let c = vec![
        parse_player_code(&codes.0).map_err(PyValueError::new_err)?,
        parse_player_code(&codes.1).map_err(PyValueError::new_err)?,
    ];
    let mut g = Game::new(create_players(da, db, c), seed);
    let mut rec = Vec::new();
    let mut prints = Vec::new();
    loop {
        let s = g.get_state_clone();
        if s.winner.is_some() {
            break;
        }
        let (actor, mut acts) = s.generate_possible_actions();
        canonical_actions(&mut acts);
        let fp = if actor == record_seat && acts.len() > 1 {
            Some(decision_fingerprint(&g, actor, &acts))
        } else {
            None
        };
        let chosen = g.play_tick();
        if let Some(fp) = fp {
            rec.push(acts.iter().position(|a| *a == chosen).expect("chosen action is legal"));
            prints.push(fp);
        }
    }
    let s = g.get_state_clone();
    let w = match &s.winner {
        Some(GameOutcome::Win(p)) => *p as i64,
        Some(GameOutcome::Tie) => -1,
        None => -2,
    };
    Ok((rec, prints, state_hash(&s), (w, s.points, s.turn_count)))
}

#[pymodule]
fn pdl_rl_env(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RawEnv>()?;
    m.add_class::<Snapshot>()?;
    m.add_function(wrap_pyfunction!(engine_play, m)?)?;
    m.add_function(wrap_pyfunction!(engine_play_record, m)?)?;
    Ok(())
}

#[cfg(test)]
mod rules3_action_encoding_tests;
