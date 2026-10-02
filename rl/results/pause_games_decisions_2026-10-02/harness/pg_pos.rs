//! Pause-games decisions (scratch, diagnosis only, Oct 2): builds a constructed-board position from a JSON description of one of Dustin's
//! real turns, then asks km3 what it plays there. Built into a scratch copy of the pinned engine (main-8626a35) carrying only the print-only
//! score-dump patch (pgd_patch.py); nothing in the repo's engine/.
//!   pg_pos --positions P.json --deck A=path.txt [--deck B=...] [--seeds 1,2,3] [--bot km3] [--only ID] [--tree]
//! Per position and seed it prints one JSON line per run on stdout:
//!   {"kind":"free", ...}   km3 plays its own turn from the position (actions until its first draw card, or the end of the turn)
//!   {"kind":"forced", ...} the position's "force" line is applied step by step; at every step km3 (on a fresh game from the same state) says what
//!                          it would play, and after the last forced action the next real choice (e.g. Turbo Shark's Bench target) is asked once more
//! and, on stderr, PGSTEP markers followed by the patched search's PGDUMP lines (every root candidate's score).
use deckgym::actions::{Action, SimpleAction};
use deckgym::models::{Card, EnergyType, PlayedCard};
use deckgym::players::expectiminimax_player::pg_label;
use deckgym::players::{create_players, parse_player_code};
use deckgym::state::EnergyZone;
use deckgym::{Deck, Game, State};
use rand::{rngs::StdRng, seq::SliceRandom, SeedableRng};
use serde_json::{json, Value};
use std::collections::HashMap;

fn arg_all(args: &[String], name: &str) -> Vec<String> {
    args.iter().enumerate().filter(|(_, a)| *a == name).filter_map(|(i, _)| args.get(i + 1)).cloned().collect()
}
fn arg(args: &[String], name: &str) -> Option<String> {
    arg_all(args, name).into_iter().next()
}

fn card(s: &str) -> Card {
    Card::from_str_with_count(&format!("1 {s}")).unwrap_or_else(|e| panic!("card {s:?}: {e}")).1
}
fn cards(v: &Value) -> Vec<Card> {
    v.as_array().map(|a| a.iter().map(|x| card(x.as_str().unwrap())).collect()).unwrap_or_default()
}
fn energy(s: &str) -> EnergyType {
    serde_json::from_value(Value::String(s.to_string())).unwrap_or_else(|e| panic!("energy {s}: {e}"))
}
fn energies(v: &Value) -> Vec<EnergyType> {
    v.as_array().map(|a| a.iter().map(|x| energy(x.as_str().unwrap())).collect()).unwrap_or_default()
}

/// One in-play Pokemon from its JSON; also returns every card it carries (for the unseen-deck bookkeeping).
fn pk(v: &Value) -> (PlayedCard, Vec<Card>) {
    let c = card(v["card"].as_str().expect("card"));
    let base_hp = match &c {
        Card::Pokemon(p) => p.hp,
        _ => 40,
    };
    let behind = cards(&v["behind"]);
    let tools = cards(&v["tools"]);
    let mut carried = vec![c.clone()];
    carried.extend(behind.iter().cloned());
    carried.extend(tools.iter().cloned());
    let mut p = PlayedCard::new(c, 0, base_hp, energies(&v["energy"]), v["new"].as_bool().unwrap_or(false), behind);
    p.attached_tools = tools;
    if let Some(h) = v.get("hp").and_then(|h| h.as_u64()) {
        p = p.with_remaining_hp(h as u32);
    }
    (p, carried)
}

fn remove_one(pool: &mut Vec<Card>, c: &Card) -> bool {
    if let Some(i) = pool.iter().position(|x| x.get_id() == c.get_id()) {
        pool.remove(i);
        true
    } else {
        false
    }
}

struct Built {
    state: State,
    summary: Value,
    problems: Vec<String>,
}

fn build(pos: &Value, deck_me: &Deck, deck_filler: &Deck, shuffle_seed: u64) -> Built {
    let mut problems = Vec::new();
    // a random-player game just to get a legal, stable State to overwrite (what test_support does)
    let r = || parse_player_code("r").unwrap();
    let mut g = Game::new(create_players(deck_me.clone(), deck_filler.clone(), vec![r(), r()]), 1);
    g.play_until_stable();
    let mut st = g.get_state_clone();

    let me = &pos["me"];
    let opp = &pos["opp"];
    let hand_me = cards(&me["hand"]);
    let discard_me = cards(&me["discard"]);
    let mut board_me = Vec::new();
    let mut known_me: Vec<Card> = hand_me.iter().cloned().chain(discard_me.iter().cloned()).collect();
    for p in me["board"].as_array().unwrap() {
        let (pc, carried) = pk(p);
        board_me.push(pc);
        known_me.extend(carried);
    }
    let mut board_opp = Vec::new();
    let mut opp_carried = 0usize;
    for p in opp["board"].as_array().unwrap() {
        let (pc, carried) = pk(p);
        board_opp.push(pc);
        opp_carried += carried.len();
    }
    // the opponent's discard is only a count of filler cards unless it is listed
    let discard_opp: Vec<Card> = match opp.get("discard_n").and_then(|x| x.as_u64()) {
        Some(n) => deck_filler.cards.iter().cycle().take(n as usize).cloned().collect(),
        None => cards(&opp["discard"]),
    };
    let stadium = pos.get("stadium").filter(|s| !s.is_null());
    let stadium_owner = stadium.map(|s| s["owner"].as_u64().unwrap() as usize);
    if let Some(s) = stadium {
        if stadium_owner == Some(0) {
            known_me.push(card(s["card"].as_str().unwrap()));
        }
    }

    // the unseen own cards: the deck list minus everything seen
    let mut unseen = deck_me.cards.clone();
    for c in &known_me {
        if !remove_one(&mut unseen, c) {
            problems.push(format!("more copies of {} {} seen than the list holds", c.get_id(), c.get_name()));
        }
    }
    let mut rng = StdRng::seed_from_u64(shuffle_seed);
    unseen.shuffle(&mut rng);
    if let Some(n) = me.get("deck_count").and_then(|x| x.as_u64()) {
        if n as usize != unseen.len() {
            problems.push(format!("deck count: the position says {n}, the list minus seen cards leaves {}", unseen.len()));
        }
    }
    // an optional "top" fixes the first cards of the deck (for forced replays through a draw)
    if let Some(top) = me.get("top") {
        let mut t = cards(top);
        for c in &t {
            if !remove_one(&mut unseen, c) {
                problems.push(format!("top card {} is not in the unseen cards", c.get_name()));
            }
        }
        t.extend(unseen.drain(..));
        unseen = t;
    }

    st.set_board(board_me, board_opp);
    st.hands[0] = hand_me;
    st.decks[0].cards = unseen.clone();
    st.discard_piles[0] = discard_me;
    st.discard_energies[0] = energies(&me["discard_energy"]);

    let opp_hand_n = opp["hand_count"].as_u64().unwrap() as usize;
    let opp_deck_n = match opp.get("deck_count").and_then(|x| x.as_u64()) {
        Some(n) => n as usize,
        None => {
            let used = opp_hand_n + opp_carried + discard_opp.len() + usize::from(stadium_owner == Some(1));
            20usize.saturating_sub(used)
        }
    };
    let filler: Vec<Card> = deck_filler.cards.iter().cycle().take(opp_hand_n + opp_deck_n).cloned().collect();
    st.hands[1] = filler[..opp_hand_n].to_vec();
    st.decks[1].cards = filler[opp_hand_n..].to_vec();
    st.discard_piles[1] = discard_opp;
    st.discard_energies[1] = energies(&opp["discard_energy"]);

    match stadium {
        Some(s) => {
            st.active_stadium = Some(card(s["card"].as_str().unwrap()));
            st.active_stadium_owner = stadium_owner;
        }
        None => {
            st.active_stadium = None;
            st.active_stadium_owner = None;
        }
    }
    st.points = [pos["points"][0].as_u64().unwrap() as u8, pos["points"][1].as_u64().unwrap() as u8];
    st.turn_count = pos["turn_count"].as_u64().unwrap() as u8;
    st.current_player = 0;
    st.move_generation_stack.clear();
    let ez = |v: &Value| EnergyZone {
        current: v.get("energy_now").and_then(|x| x.as_str()).map(energy),
        next: v.get("energy_next").and_then(|x| x.as_str()).map(energy),
    };
    st.energy_zone = [ez(me), ez(opp)];

    // the private fields (turn effects, turn flags) go through the State's own serde form
    let mut val = serde_json::to_value(&st).expect("state to json");
    let mut te = serde_json::Map::new();
    if let Some(list) = pos.get("turn_effects").and_then(|x| x.as_array()) {
        for e in list {
            te.entry(e["turn"].as_u64().unwrap().to_string()).or_insert_with(|| json!([])).as_array_mut().unwrap().push(e["effect"].clone());
        }
    }
    val["turn_effects"] = Value::Object(te);
    if let Some(flags) = pos.get("flags").and_then(|x| x.as_object()) {
        for (k, v) in flags {
            assert!(val.get(k).is_some(), "no such state field {k}");
            val[k] = v.clone();
        }
    }
    let st: State = serde_json::from_value(val).expect("json back to state");

    let describe = |side: usize| -> Value {
        let slots: Vec<Value> = st.in_play_pokemon[side]
            .iter()
            .enumerate()
            .filter_map(|(i, p)| p.as_ref().map(|p| (i, p)))
            .map(|(i, p)| {
                json!({
                    "slot": i, "card": p.card.get_name(), "id": p.card.get_id(), "hp": p.get_remaining_hp(),
                    "energy": p.attached_energy.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
                    "tools": p.attached_tools.iter().map(|t| t.get_name()).collect::<Vec<_>>(),
                    "behind": p.cards_behind.iter().map(|t| t.get_name()).collect::<Vec<_>>(),
                })
            })
            .collect();
        Value::Array(slots)
    };
    let mut hand_names: Vec<String> = st.hands[0].iter().map(|c| c.get_name()).collect();
    hand_names.sort();
    let summary = json!({
        "turn_count": st.turn_count, "points": st.points,
        "me": {"hand": hand_names, "deck": st.decks[0].cards.len(), "discard": st.discard_piles[0].iter().map(|c| c.get_name()).collect::<Vec<_>>(), "board": describe(0),
               "energy_zone": [format!("{:?}", st.energy_zone[0].current), format!("{:?}", st.energy_zone[0].next)]},
        "opp": {"hand": st.hands[1].len(), "deck": st.decks[1].cards.len(), "board": describe(1)},
        "stadium": st.active_stadium.as_ref().map(|c| c.get_name()),
    });
    Built { state: st, summary, problems }
}

fn players(deck_me: &Deck, deck_filler: &Deck, bot: &str) -> Vec<Box<dyn deckgym::players::Player>> {
    let code = || parse_player_code(bot).unwrap();
    create_players(deck_me.clone(), deck_filler.clone(), vec![code(), code()])
}

fn is_draw(label: &str) -> bool {
    label == "Play:Professor's Research" || label == "Play:Copycat" || label.starts_with("Play:Poké Ball") || label.starts_with("Play:Poke Ball")
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let positions: Vec<Value> = serde_json::from_str(&std::fs::read_to_string(arg(&args, "--positions").expect("--positions")).unwrap()).unwrap();
    let mut decks: HashMap<String, Deck> = HashMap::new();
    for d in arg_all(&args, "--deck") {
        let (k, path) = d.split_once('=').expect("--deck KEY=path");
        decks.insert(k.to_string(), Deck::from_file(path).expect("deck file"));
    }
    let seeds: Vec<u64> = arg(&args, "--seeds").unwrap_or_else(|| "1".into()).split(',').map(|x| x.trim().parse().unwrap()).collect();
    let bot = arg(&args, "--bot").unwrap_or_else(|| "km3".into());
    let only = arg(&args, "--only");
    let mode = if args.iter().any(|a| a == "--tree") { "tree" } else { "1" };
    std::env::set_var("PG_DUMP", mode);

    for pos in &positions {
        let id = pos["id"].as_str().unwrap().to_string();
        if only.as_ref().is_some_and(|o| *o != id) {
            continue;
        }
        let deck_me = decks.get(pos["deck"].as_str().unwrap()).expect("deck key").clone();
        let deck_filler = decks.get(pos["filler"].as_str().unwrap_or(pos["deck"].as_str().unwrap())).expect("filler key").clone();
        let first = build(pos, &deck_me, &deck_filler, 1);
        println!("{}", json!({"kind": "position", "id": id, "summary": first.summary, "problems": first.problems}));
        if !first.problems.is_empty() {
            continue;
        }
        let force: Vec<String> = pos.get("force").and_then(|f| f.as_array()).map(|a| a.iter().map(|x| x.as_str().unwrap().to_string()).collect()).unwrap_or_default();

        for &seed in &seeds {
            // ---- free run: km3 plays its own turn
            {
                let built = build(pos, &deck_me, &deck_filler, seed);
                let mut game = Game::from_state(built.state, players(&deck_me, &deck_filler, &bot), seed);
                let mut plan: Vec<String> = Vec::new();
                let mut cut = "end of turn";
                for k in 0..40 {
                    let state = game.get_state_clone();
                    if game.is_game_over() {
                        cut = "game over";
                        break;
                    }
                    let (actor, _) = state.generate_possible_actions();
                    if actor != 0 || (state.current_player != 0 && state.move_generation_stack.is_empty()) {
                        break;
                    }
                    eprintln!("PGSTEP {id} seed {seed} free {k}");
                    let a = game.play_tick();
                    let l = pg_label(&a);
                    plan.push(l.clone());
                    if is_draw(&l) {
                        cut = "first draw";
                        break;
                    }
                }
                println!("{}", json!({"kind": "free", "id": id, "seed": seed, "plan": plan, "cut": cut}));
            }
            // ---- forced run: Dustin's line, with km3's own answer asked at every step
            if !force.is_empty() {
                let built = build(pos, &deck_me, &deck_filler, seed);
                let mut driver = Game::from_state(built.state, players(&deck_me, &deck_filler, &bot), seed);
                let mut steps: Vec<Value> = Vec::new();
                let mut ok = true;
                let mut queue: Vec<Option<String>> = force.iter().cloned().map(Some).collect();
                queue.push(None); // the last ask: the next real choice after the forced line
                for (k, want) in queue.iter().enumerate() {
                    // single-option frames resolve on their own
                    loop {
                        if driver.is_game_over() {
                            break;
                        }
                        let st = driver.get_state_clone();
                        let (actor, acts) = st.generate_possible_actions();
                        if actor == 0 && acts.len() == 1 && want.as_ref().map_or(true, |w| pg_label(&acts[0]) != *w) {
                            let a = acts[0].clone();
                            driver.apply_action(&a);
                            steps.push(json!({"step": k, "auto": pg_label(&a)}));
                            continue;
                        }
                        break;
                    }
                    let st = driver.get_state_clone();
                    if driver.is_game_over() || st.generate_possible_actions().0 != 0 {
                        steps.push(json!({"step": k, "note": "the turn is over or it is the opponent's frame"}));
                        break;
                    }
                    let (_, acts) = st.generate_possible_actions();
                    // km3's own answer here, on a fresh game from the same state
                    eprintln!("PGSTEP {id} seed {seed} forced {k} want={}", want.clone().unwrap_or_else(|| "(next choice)".into()));
                    let km3 = {
                        let mut probe = Game::from_state(st.clone(), players(&deck_me, &deck_filler, &bot), seed);
                        pg_label(&probe.play_tick())
                    };
                    let legal: Vec<String> = acts.iter().map(pg_label).collect();
                    match want {
                        Some(w) => {
                            let found: Vec<&Action> = acts.iter().filter(|a| pg_label(a) == *w).collect();
                            // two copies of one card in hand give two identical actions: that is fine
                            if found.is_empty() || !found.iter().all(|a| **a == *found[0]) {
                                steps.push(json!({"step": k, "forced": w, "km3": km3, "error": format!("{} different legal actions carry that label", found.len()), "legal": legal}));
                                ok = false;
                                break;
                            }
                            steps.push(json!({"step": k, "forced": w, "km3": km3}));
                            let a = found[0].clone();
                            driver.apply_action(&a);
                        }
                        None => {
                            steps.push(json!({"step": k, "next_choice_km3": km3, "legal": legal}));
                        }
                    }
                }
                println!("{}", json!({"kind": "forced", "id": id, "seed": seed, "ok": ok, "steps": steps}));
            }
        }
    }
}

#[allow(dead_code)]
fn unused(_: &SimpleAction) {}
