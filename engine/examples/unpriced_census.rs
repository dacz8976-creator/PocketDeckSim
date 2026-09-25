//! Unpriced-branch census (B2a): on the Limitless table's deals, which moves the bot's search leaves
//! unpriced, for which reason, and how often the move it chose was one of them, per deck.
//!
//!   cargo run --release --example unpriced_census -- --decks ../decks/research --games 200 --bot k3
//!       [--pairings 0,13] [--out census.json] [--games-out games.jsonl]
//!
//! Seeds are the table's (72,000,000 + pairing x 10,000 + i, even i = the first-named deck in seat 0), and
//! the game loop matches legality_scan's, so a game's move fingerprint equals the table run's for the same
//! bot and deal: the census watches the table's own games.
//!
//! A decision counts when the bot had more than one move. For each candidate move (the "root"), the search
//! records the branches below it that it could not price, with the reason (players/expectiminimax_player.rs
//! and observation.rs). The reasons fall in three kinds:
//! - hidden: the branch needs the opponent's hidden cards (the text rule for effects that mention the
//!   opponent's hand or deck, setup reveals, draws of unknown cards). It is scored as the position before
//!   it, as if nothing happened. "itself" means the candidate move is that branch (Copycat played now);
//!   "later" means the branch is deeper in the candidate's search tree.
//! - boundary: at the end of the searched turn the public-reply certificate declined, so the position is
//!   scored by the static value function (k3's ordinary leaf). This happens on nearly every move.
//! - other: anything else (the hidden opponent setup, private pending choices).
//! "offered" counts decisions where a candidate had such a branch, "chosen" those where the bot played it.

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::UnpricedBranch;
use deckgym::players::{create_players, parse_player_code};
use deckgym::simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rayon::prelude::*;
use std::collections::hash_map::DefaultHasher;
use std::collections::BTreeMap;
use std::hash::{Hash, Hasher};
use uuid::Uuid;

const NAMES: [&str; 8] = [
    "altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing",
];
const SEED_BASE: u64 = 72_000_000;

/// One decision with more than one move: who chose, the unpriced roots (label, reason), the chosen root.
struct Decision {
    actor: usize,
    /// (candidate label, reason, the candidate is itself the unpriced branch, chosen)
    roots: Vec<(String, String, bool, bool)>,
    branches: Vec<(String, String, usize)>,
}

#[derive(Default)]
struct Census {
    pending: Vec<UnpricedBranch>,
    decisions: Vec<Decision>,
}

impl SimulationEventHandler for Census {
    fn merge(&mut self, _other: &dyn SimulationEventHandler) {}

    fn on_decision_information(&mut self, _: Uuid, _: &str, unpriced: &[UnpricedBranch]) {
        self.pending = unpriced.to_vec();
    }

    fn on_action(&mut self, _: Uuid, before: &State, actor: usize, playable: &[Action], _chosen: &Action) {
        let pending = std::mem::take(&mut self.pending);
        if playable.len() < 2 {
            return;
        }
        let mut roots: BTreeMap<(String, String, bool), bool> = BTreeMap::new();
        let mut branches: BTreeMap<(String, String), usize> = BTreeMap::new();
        for b in &pending {
            let root = b.root_action.as_ref().map(|r| label(Some(before), r)).unwrap_or_else(|| "(no root)".into());
            let itself = b.root_action.as_ref() == Some(&b.action);
            *roots.entry((root, b.reason.clone(), itself)).or_default() |= b.selected;
            *branches.entry((label(None, &b.action), b.reason.clone())).or_default() += b.occurrences;
        }
        self.decisions.push(Decision {
            actor,
            roots: roots.into_iter().map(|((l, r, i), s)| (l, r, i, s)).collect(),
            branches: branches.into_iter().map(|((l, r), n)| (l, r, n)).collect(),
        });
    }
}

/// A move's card: the Trainer played, the attack (and its user, when the real state is known), the ability's
/// user, the evolution, the Pokémon placed, the Tool, or the kind of move.
fn label(state: Option<&State>, action: &Action) -> String {
    let slot_name = |idx: usize| {
        state
            .and_then(|s| s.in_play_pokemon[action.actor][idx].as_ref())
            .map(|p| p.get_name())
            .unwrap_or_else(|| format!("slot {idx}"))
    };
    match &action.action {
        SimpleAction::Play { trainer_card } => trainer_card.name.clone(),
        SimpleAction::Attack(atk) => match state {
            Some(_) => format!("{} ({})", atk.title, slot_name(0)),
            None => atk.title.clone(),
        },
        SimpleAction::UseAbility { in_play_idx } => format!("{}'s ability", slot_name(*in_play_idx)),
        SimpleAction::Evolve { evolution, .. } => format!("evolve into {}", evolution.get_name()),
        SimpleAction::Place(card, _) => format!("place {}", card.get_name()),
        SimpleAction::AttachTool { tool_card, .. } => format!("attach {}", tool_card.get_name()),
        other => format!("{other:?}").split(|c: char| !c.is_alphanumeric()).next().unwrap_or("").to_string(),
    }
}

struct GameOut {
    first_seat: usize,
    winner_seat: i32,
    points: [u8; 2],
    turns: u8,
    fingerprint: u64,
    decisions: Vec<Decision>,
}

fn play_one(decks: &[Deck; 8], pairing: usize, i: u64, bot: &str) -> GameOut {
    let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
    let (a, b) = pairs[pairing];
    let seed = SEED_BASE + pairing as u64 * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (a, b) } else { (b, a) };
    let codes = vec![parse_player_code(bot).unwrap(), parse_player_code(bot).unwrap()];
    let players = create_players(decks[d0].clone(), decks[d1].clone(), codes);
    let mut handler = CompositeSimulationEventHandler::new(vec![Box::new(Census::default())]);
    let mut moves = DefaultHasher::new();
    let end = {
        let mut game = Game::new_with_event_handlers(Uuid::new_v4(), players, seed, &mut handler);
        while !game.is_game_over() {
            let chosen = game.play_tick();
            format!("{:?}", chosen).hash(&mut moves);
        }
        game.get_state_clone()
    };
    let census = handler.get_handler::<Census>().unwrap();
    let decisions = census
        .decisions
        .iter()
        .map(|d| Decision { actor: d.actor, roots: d.roots.clone(), branches: d.branches.clone() })
        .collect();
    let winner_seat = match end.winner {
        Some(GameOutcome::Win(w)) => w as i32,
        _ => -1,
    };
    GameOut { first_seat, winner_seat, points: end.points, turns: end.turn_count, fingerprint: moves.finish(), decisions }
}

fn kind(reason: &str) -> &'static str {
    if reason.starts_with("public reply") || reason.starts_with("no certified public") || reason.starts_with("opponent reply remains") {
        "boundary"
    } else if reason.starts_with("opponent setup is hidden") || reason.starts_with("private pending choice") {
        "other"
    } else {
        "hidden"
    }
}

#[derive(Default)]
struct DeckTally {
    decisions: u64,
    /// kind -> (decisions with a candidate of that kind, decisions where the chosen move was one)
    kinds: BTreeMap<String, (u64, u64)>,
    /// hidden kind, candidate itself unpriced -> (decisions offered, decisions chosen)
    hidden_itself: (u64, u64),
    /// (root label, reason, itself) -> (decisions offered, decisions chosen)
    roots: BTreeMap<(String, String, bool), (u64, u64)>,
    /// (branch label, reason) -> occurrences in the search
    branches: BTreeMap<(String, String), u64>,
}

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let games: u64 = arg(&args, "--games").map(|x| x.parse().unwrap()).unwrap_or(200);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "k3".into());
    assert!(!bot.eq_ignore_ascii_case("jev"), "the jev bot calls a paid API and is not allowed here");
    parse_player_code(&bot).expect("player code");
    let only: Option<Vec<usize>> =
        arg(&args, "--pairings").map(|x| x.split(',').map(|p| p.trim().parse().unwrap()).collect());
    let decks: [Deck; 8] = NAMES.map(|n| Deck::from_file(&format!("{dir}/{n}.txt")).expect("deck file"));
    let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
    let mut tallies: BTreeMap<&str, DeckTally> = BTreeMap::new();
    let mut lines = Vec::new();
    for (p, (a, b)) in pairs.iter().enumerate() {
        if only.as_ref().is_some_and(|o| !o.contains(&p)) {
            continue;
        }
        let results: Vec<GameOut> = (0..games).into_par_iter().map(|i| play_one(&decks, p, i, &bot)).collect();
        for (i, g) in results.iter().enumerate() {
            let seat_deck = |s: usize| if (s == 0) == (g.first_seat == 0) { *a } else { *b };
            lines.push(serde_json::json!({
                "pairing": p, "a": NAMES[*a], "b": NAMES[*b], "i": i, "seed": SEED_BASE + p as u64 * 10_000 + i as u64,
                "bot": bot, "first_seat": g.first_seat, "winner_seat": g.winner_seat, "points": g.points,
                "turns": g.turns, "moves": format!("{:016x}", g.fingerprint),
            }).to_string());
            for d in &g.decisions {
                let t = tallies.entry(NAMES[seat_deck(d.actor)]).or_default();
                t.decisions += 1;
                for k in ["hidden", "boundary", "other"] {
                    let of_kind: Vec<_> = d.roots.iter().filter(|r| kind(&r.1) == k).collect();
                    let e = t.kinds.entry(k.into()).or_default();
                    e.0 += u64::from(!of_kind.is_empty());
                    e.1 += u64::from(of_kind.iter().any(|r| r.3));
                }
                let itself: Vec<_> = d.roots.iter().filter(|r| kind(&r.1) == "hidden" && r.2).collect();
                t.hidden_itself.0 += u64::from(!itself.is_empty());
                t.hidden_itself.1 += u64::from(itself.iter().any(|r| r.3));
                let mut counted = std::collections::BTreeSet::new();
                for (l, r, i, s) in &d.roots {
                    if !counted.insert((l.clone(), r.clone(), *i)) {
                        continue;
                    }
                    let e = t.roots.entry((l.clone(), r.clone(), *i)).or_default();
                    e.0 += 1;
                    e.1 += u64::from(*s);
                }
                for (l, r, n) in &d.branches {
                    *t.branches.entry((l.clone(), r.clone())).or_default() += *n as u64;
                }
            }
        }
        eprintln!("pairing {p} done");
    }
    println!("bot {bot}, table deals i < {games}; a decision counts when the bot had more than one move");
    let pc = |x: u64, n: u64| 100.0 * x as f64 / n.max(1) as f64;
    for (deck, t) in &tallies {
        let n = t.decisions;
        println!("\n{deck}: {n} decisions (% with such a candidate / % where the bot chose one)");
        println!("    hidden, the candidate itself scored as nothing: {:.1}% / {:.1}%", pc(t.hidden_itself.0, n), pc(t.hidden_itself.1, n));
        for (k, (o, c)) in &t.kinds {
            println!("    {k:8} anywhere in the candidate's search: {:.1}% / {:.1}%", pc(*o, n), pc(*c, n));
        }
        let mut roots: Vec<_> = t.roots.iter().filter(|((_, r, i), _)| kind(r) == "hidden" && *i).collect();
        roots.sort_by_key(|(_, (o, c))| std::cmp::Reverse((*o, *c)));
        for ((l, r, _), (o, c)) in roots.iter().take(8) {
            println!("      {l:38} offered {o:6} chosen {c:6}   {r}");
        }
    }
    if let Some(path) = arg(&args, "--out") {
        let json: BTreeMap<&str, serde_json::Value> = tallies.iter().map(|(deck, t)| {
            let roots: Vec<_> = t.roots.iter().map(|((l, r, i), (o, c))| serde_json::json!({
                "root": l, "reason": r, "kind": kind(r), "itself": i, "offered": o, "chosen": c })).collect();
            let branches: Vec<_> = t.branches.iter().map(|((l, r), n)| serde_json::json!({
                "branch": l, "reason": r, "occurrences": n })).collect();
            let kinds: BTreeMap<&String, serde_json::Value> = t.kinds.iter().map(|(k, (o, c))|
                (k, serde_json::json!({ "offered": o, "chosen": c }))).collect();
            (*deck, serde_json::json!({ "decisions": t.decisions, "kinds": kinds,
                "hidden_itself": { "offered": t.hidden_itself.0, "chosen": t.hidden_itself.1 },
                "roots": roots, "branches": branches }))
        }).collect();
        std::fs::write(&path, serde_json::to_string_pretty(&json).unwrap()).expect("out file");
    }
    if let Some(path) = arg(&args, "--games-out") {
        std::fs::write(&path, lines.join("\n") + "\n").expect("games-out file");
    }
}
