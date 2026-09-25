//! Tool / turn-effect census (the laptop's request, Sept 25): on the Limitless table's own deals, how often each Tool,
//! Field Blower and each temporary damage-reduction effect is offered and played by the pilot, and where the Tools
//! go. It only watches: the games are the table's games (the move fingerprints must equal the pilot's table file).
//! Built as an example in a scratch copy of engine/ (the repo's engine is untouched):
//!
//!   cp tool_census.rs <scratch engine>/examples/ && cargo run --release --example tool_census -- \
//!       --decks ../decks/research --games 100 --bot kp3 --games-out census_games.jsonl
//!
//! Seeds: the table's deals only, 72,000,000 + pairing x 10,000 + i, even i = the first-named deck in seat 0.
//! Per deck and card:
//! - offered: the owner's turns on which playing the card (or using the attack) was among the legal moves;
//! - played: the turns on which it was played (used);
//! - for a Tool, where it was attached (Active or Bench) and the holder's name;
//! - for Field Blower, what it discarded (own or opponent's Tool, on the Active or the Bench, or the Stadium).
use deckgym::actions::SimpleAction;
use deckgym::models::{Card, TrainerType};
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};
use rayon::prelude::*;
use std::collections::hash_map::DefaultHasher;
use std::collections::{BTreeMap, BTreeSet};
use std::hash::{Hash, Hasher};

const NAMES: [&str; 8] = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"];
const SEED_BASE: u64 = 72_000_000;
/// Attacks that put a temporary damage reduction on the attacker itself for the opponent's next turn (defender side),
/// found in the eight lists by their text ("During your opponent's next turn, this Pokemon takes -X damage").
const REDUCTION_ATTACKS: [&str; 1] = ["Stiffen"];

#[derive(Default, Clone)]
struct Tally {
    offered: u64,
    played: u64,
    detail: BTreeMap<String, u64>,
}

#[derive(Default)]
struct GameCensus {
    // (deck, card) -> tally
    t: BTreeMap<(String, String), Tally>,
    fingerprint: u64,
    seed: u64,
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// The card a move plays: a Trainer's name, or a listed reduction attack's title.
fn card_of(action: &SimpleAction) -> Option<String> {
    match action {
        SimpleAction::Play { trainer_card } => Some(trainer_card.name.clone()),
        SimpleAction::Attack(attack) if REDUCTION_ATTACKS.contains(&attack.title.as_str()) => {
            Some(format!("attack {}", attack.title))
        }
        _ => None,
    }
}

fn watched(action: &SimpleAction) -> bool {
    match action {
        SimpleAction::Play { trainer_card } => {
            trainer_card.trainer_card_type == TrainerType::Tool || trainer_card.name == "Field Blower"
        }
        SimpleAction::Attack(attack) => REDUCTION_ATTACKS.contains(&attack.title.as_str()),
        _ => false,
    }
}

fn play_one(decks: &[Deck; 8], pairing: usize, i: u64, bot: &str) -> GameCensus {
    let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
    let (a, b) = pairs[pairing];
    let seed = SEED_BASE + pairing as u64 * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (a, b) } else { (b, a) };
    let deck_of = [NAMES[d0].to_string(), NAMES[d1].to_string()];
    let codes = vec![parse_player_code(bot).unwrap(), parse_player_code(bot).unwrap()];
    let players = create_players(decks[d0].clone(), decks[d1].clone(), codes);
    let mut game = Game::new(players, seed);
    let mut moves = DefaultHasher::new();
    let mut census = GameCensus { seed, ..Default::default() };
    // (seat, turn) -> cards offered / played that turn
    let mut offered: BTreeSet<(usize, u8, String)> = BTreeSet::new();
    let mut played: BTreeSet<(usize, u8, String)> = BTreeSet::new();
    let mut pending: Option<(usize, String)> = None; // a Tool or Field Blower whose target choice comes next
    while !game.is_game_over() {
        let before = game.get_state_clone();
        let (actor, actions) = before.generate_possible_actions();
        for a in actions.iter().filter(|a| watched(&a.action)) {
            offered.insert((actor, before.turn_count, card_of(&a.action).unwrap()));
        }
        let chosen = game.play_tick();
        format!("{:?}", chosen).hash(&mut moves);
        if watched(&chosen.action) {
            let card = card_of(&chosen.action).unwrap();
            played.insert((chosen.actor, before.turn_count, card.clone()));
            if matches!(&chosen.action, SimpleAction::Play { .. }) {
                pending = Some((chosen.actor, card));
            }
            continue;
        }
        if let Some((seat, card)) = pending.take() {
            let where_ = match &chosen.action {
                SimpleAction::AttachTool { in_play_idx, .. } => {
                    let holder = before.in_play_pokemon[seat][*in_play_idx].as_ref().map(|p| p.get_name()).unwrap_or_default();
                    Some(format!("{} {holder}", if *in_play_idx == 0 { "Active" } else { "Bench" }))
                }
                SimpleAction::DiscardToolFromPokemon { player, in_play_idx, tool_idx } => {
                    let pokemon = before.in_play_pokemon[*player][*in_play_idx].as_ref();
                    let tool = pokemon.and_then(|p| p.attached_tools.get(*tool_idx)).map(|t| match t {
                        Card::Trainer(t) => t.name.clone(),
                        other => format!("{other:?}"),
                    });
                    Some(format!(
                        "{} Tool on {} ({})",
                        if *player == seat { "own" } else { "opponent's" },
                        if *in_play_idx == 0 { "Active" } else { "Bench" },
                        tool.unwrap_or_default()
                    ))
                }
                SimpleAction::DiscardActiveStadium => Some("Stadium".to_string()),
                _ => None,
            };
            if let Some(w) = where_ {
                let e = census.t.entry((deck_of[seat].clone(), card)).or_default();
                *e.detail.entry(w).or_default() += 1;
            } else {
                pending = None;
            }
        }
    }
    for (seat, _turn, card) in &offered {
        census.t.entry((deck_of[*seat].clone(), card.clone())).or_default().offered += 1;
    }
    for (seat, _turn, card) in &played {
        census.t.entry((deck_of[*seat].clone(), card.clone())).or_default().played += 1;
    }
    census.fingerprint = moves.finish();
    census
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let games: u64 = arg(&args, "--games").map(|x| x.parse().unwrap()).unwrap_or(100);
    let bot = arg(&args, "--bot").unwrap_or_else(|| "kp3".into());
    assert!(!bot.eq_ignore_ascii_case("jev"), "the jev bot calls a paid API and is not allowed here");
    let decks: [Deck; 8] = NAMES.map(|n| Deck::from_file(&format!("{dir}/{n}.txt")).expect("deck file"));
    let mut out = arg(&args, "--games-out").map(|p| std::io::BufWriter::new(std::fs::File::create(p).unwrap()));
    let mut total: BTreeMap<(String, String), Tally> = BTreeMap::new();
    for p in 0..28 {
        let results: Vec<GameCensus> = (0..games).into_par_iter().map(|i| play_one(&decks, p, i, &bot)).collect();
        for (i, r) in results.iter().enumerate() {
            if let Some(o) = out.as_mut() {
                use std::io::Write;
                writeln!(o, "{}", serde_json::json!({"pairing": p, "i": i, "seed": r.seed, "moves": format!("{:016x}", r.fingerprint)})).unwrap();
            }
            for (k, v) in &r.t {
                let e = total.entry(k.clone()).or_default();
                e.offered += v.offered;
                e.played += v.played;
                for (d, n) in &v.detail {
                    *e.detail.entry(d.clone()).or_default() += n;
                }
            }
        }
        eprintln!("pairing {p} done");
    }
    println!("bot {bot}, the table's first {games} deals of each of the 28 pairings (both decks piloted by {bot})");
    println!("deck        card                          turns offered  turns played   (%)   where");
    for ((deck, card), t) in &total {
        let pct = if t.offered > 0 { 100.0 * t.played as f64 / t.offered as f64 } else { 0.0 };
        let detail: Vec<String> = t.detail.iter().map(|(d, n)| format!("{d}: {n}")).collect();
        println!("{deck:<11} {card:<30} {:>13} {:>13} {pct:>6.1}   {}", t.offered, t.played, detail.join("; "));
    }
}
