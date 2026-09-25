//! Brew goldfish (A1): a list piloted by a bot against a panel of decks, with consistency numbers per game.
//!
//!   cargo run --release --example goldfish -- --deck ../decks/brews/x.txt [--panel ../decks/research]
//!       [--bot k3] [--opp-bot aa] [--games 40] [--attackers "Xatu,Arceus ex"] [--seed 22200000000]
//!       [--games-out games.jsonl] [--coverage coverage.json]
//!
//! Per opponent deck, game i uses seed `seed + opponent x 10,000 + i`; the list sits in seat 0 for even i.
//! "Turn k" is the list's own k-th turn. Per game it records: who went first; the turn of the list's first
//! attack and of its first attack by a named main attacker; the opponent's points at that moment (points
//! conceded before the first real attack); whether a Stage 2 was in play by turn 3; and dead cards at the
//! end of each turn (hand cards that no offered move could use when the list ended its turn). A game that
//! panics (a card the engine doesn't support) is counted and skipped, not fatal.
//!
//! `--coverage` writes, per card in the list, what k3 prices with a fallback: the unpriced text rule
//! (opponent's hand or deck), attacks whose damage effect falls back to printed damage in the estimator,
//! and effects that pay off during the opponent's turn (k3 never searches it). The bot's numbers for a
//! list with flagged cards are marked untrusted on its page.

use deckgym::actions::{Action, SimpleAction, EFFECT_MECHANIC_MAP};
use deckgym::card_validation::{get_implementation_status, implementation_limitations};
use deckgym::models::{Card, TrainerType};
use deckgym::players::{create_players, parse_player_code};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rayon::prelude::*;
use std::collections::BTreeMap;
use std::panic::{catch_unwind, AssertUnwindSafe};

/// The attack mechanics `estimated_attack_damage_ex` (players/value_functions.rs) prices; any other
/// damage-changing effect is estimated at its printed damage. Kept in step with that match by hand.
const ESTIMATOR_PRICED: [&str; 30] = [
    "AlsoBenchDamage", "AlsoChoiceBenchDamage", "AlsoChoiceBenchDamageFiltered", "AlsoRandomBenchDamage",
    "BenchCountDamage", "CoinFlipExtraDamage", "CoinFlipExtraDamageOrSelfDamage", "DelayedSpotDamage",
    "DirectDamage", "DirectDamageAndSelfCardEffect", "DiscardSelfEnergyPerHeadsExtraDamage",
    "EvolutionBenchCountDamage", "ExtraDamageForEachHeads", "ExtraDamageIfCombinedActiveEnergyAtLeast",
    "ExtraDamageIfExtraEnergy", "ExtraDamagePerEnergy", "ExtraDamagePerOpponentPointDuringOwnLastTurn",
    "ExtraDamagePerOpponentSpecialCondition", "ExtraDamagePerOwnPoint", "ExtraDamagePerSpecificEnergy",
    "ExtraDamagePerSpecificEnergyAllYours", "ExtraDamagePerTrainerTypeInDiscard", "FlipUntilTailsBonusDamage",
    "FlipUntilTailsDamage", "RandomDamageToOpponentPokemonPerSelfEnergy", "RandomSpreadDamage",
    "RevealTopDeckDamagePerPokemonName", "SelfDiscardAllEnergyKnockOutOpponentActive",
    "SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon", "SelfDiscardAllTypesEnergyDamagePerDiscarded",
];
const MAX_TURNS: usize = 8;

#[derive(Default, Clone, serde::Serialize)]
struct GameRecord {
    opponent: String,
    i: u64,
    seed: u64,
    list_seat: usize,
    went_first: bool,
    crashed: Option<String>,
    first_attack_turn: Option<usize>,
    first_main_attack_turn: Option<usize>,
    /// First own turn a named main attacker in the Active Spot had an attack offered (it could attack).
    first_main_attack_offered_turn: Option<usize>,
    points_conceded_before_main_attack: u8,
    stage2_by_turn3: bool,
    /// Dead cards when the list ended its k-th turn (index k-1).
    dead_at_end_of_turn: Vec<Option<usize>>,
    list_won: Option<bool>,
    points: [u8; 2],
    turns: u8,
}

fn card_of(action: &SimpleAction) -> Option<Card> {
    match action {
        SimpleAction::Play { trainer_card } => Some(Card::Trainer(trainer_card.clone())),
        SimpleAction::Place(card, _) => Some(card.clone()),
        SimpleAction::Evolve { evolution, .. } => Some(evolution.clone()),
        SimpleAction::AttachTool { tool_card, .. } => Some(tool_card.clone()),
        _ => None,
    }
}

fn play(list: &Deck, opp: &Deck, opp_name: &str, i: u64, seed: u64, bot: &str, opp_bot: &str,
        attackers: &[String]) -> GameRecord {
    let list_seat = (i % 2) as usize;
    let (d0, d1, c0, c1) = if list_seat == 0 {
        (list.clone(), opp.clone(), bot, opp_bot)
    } else {
        (opp.clone(), list.clone(), opp_bot, bot)
    };
    let players = create_players(d0, d1, vec![parse_player_code(c0).unwrap(), parse_player_code(c1).unwrap()]);
    let mut game = Game::new(players, seed);
    let mut r = GameRecord {
        opponent: opp_name.into(), i, seed, list_seat, dead_at_end_of_turn: vec![None; MAX_TURNS],
        ..Default::default()
    };
    let (mut turn_seen, mut own_turn, mut supporter_played, mut main_phase_closed) = (0u8, 0usize, false, false);
    while !game.is_game_over() {
        let before: State = game.get_state_clone();
        if before.turn_count != turn_seen && before.turn_count >= 1 {
            turn_seen = before.turn_count;
            supporter_played = false;
            main_phase_closed = false;
            if before.current_player == list_seat {
                own_turn += 1;
            }
            if before.turn_count == 1 {
                r.went_first = before.current_player == list_seat;
            }
        }
        let (actor, actions) = before.generate_possible_actions();
        let chosen: Action = game.play_tick();
        if std::env::var("GOLDFISH_TRACE").is_ok_and(|v| v == format!("{opp_name}:{i}")) && actor == list_seat {
            let hand: Vec<String> = before.hands[list_seat].iter().map(|c| c.get_name()).collect();
            let field: Vec<String> = before.in_play_pokemon[list_seat].iter().flatten()
                .map(|p| format!("{}{:?}", p.get_name(), p.attached_energy)).collect();
            eprintln!("t{own_turn} {:?} | hand {hand:?} | field {field:?}", chosen.action);
        }
        if actor != list_seat || own_turn == 0 {
            continue;
        }
        let active = before.in_play_pokemon[list_seat][0].as_ref().map(|p| p.get_name()).unwrap_or_default();
        let is_main = attackers.iter().any(|a| *a == active);
        if is_main && actions.iter().any(|a| matches!(a.action, SimpleAction::Attack(_))) {
            r.first_main_attack_offered_turn.get_or_insert(own_turn);
        }
        if own_turn <= 3
            && before.in_play_pokemon[list_seat].iter().flatten().any(|p| matches!(&p.card, Card::Pokemon(pc) if pc.stage == 2))
        {
            r.stage2_by_turn3 = true;
        }
        // Dead cards are counted where the list closes its main phase (attacks or ends its turn), from the
        // moves offered at that decision; after an attack no card can be played, so later decisions don't count.
        let closes = matches!(chosen.action, SimpleAction::Attack(_) | SimpleAction::EndTurn);
        if closes && !main_phase_closed && own_turn <= MAX_TURNS {
            main_phase_closed = true;
            let offered: Vec<Card> = actions.iter().filter_map(|a| card_of(&a.action)).collect();
            // A Supporter held only because one was already played this turn is not dead.
            let held = |c: &Card| supporter_played && matches!(c, Card::Trainer(t) if t.trainer_card_type == TrainerType::Supporter);
            let dead = before.hands[list_seat].iter().filter(|c| !offered.contains(c) && !held(c)).count();
            r.dead_at_end_of_turn[own_turn - 1] = Some(dead);
        }
        match &chosen.action {
            SimpleAction::Play { trainer_card } if trainer_card.trainer_card_type == TrainerType::Supporter => {
                supporter_played = true;
            }
            SimpleAction::Attack(_) => {
                r.first_attack_turn.get_or_insert(own_turn);
                if r.first_main_attack_turn.is_none() && is_main {
                    r.first_main_attack_turn = Some(own_turn);
                    r.points_conceded_before_main_attack = before.points[1 - list_seat];
                }
            }
            _ => {}
        }
    }
    let end = game.get_state_clone();
    if r.first_main_attack_turn.is_none() {
        r.points_conceded_before_main_attack = end.points[1 - list_seat];
    }
    r.list_won = match end.winner {
        Some(GameOutcome::Win(w)) => Some(w == list_seat),
        _ => None,
    };
    r.points = [end.points[list_seat], end.points[1 - list_seat]];
    r.turns = end.turn_count;
    r
}

fn coverage(list: &Deck) -> serde_json::Value {
    let lower = |s: &str| s.to_lowercase();
    let reply_markers = ["opponent's next turn", "during your opponent's", "is damaged by an attack",
        "knocked out by damage from an attack", "at the end of your opponent's turn"];
    let mut cards: BTreeMap<String, serde_json::Value> = BTreeMap::new();
    for card in &list.cards {
        let id = card.get_id();
        if cards.contains_key(&id) {
            continue;
        }
        let mut texts: Vec<(String, String)> = Vec::new();
        let mut estimator = Vec::new();
        match card {
            Card::Pokemon(p) => {
                if let Some(a) = &p.ability {
                    texts.push((format!("ability {}", a.title), a.effect.clone()));
                }
                for atk in &p.attacks {
                    let Some(effect) = &atk.effect else { continue };
                    texts.push((format!("attack {}", atk.title), effect.clone()));
                    let mechanic = EFFECT_MECHANIC_MAP.get(effect.as_str()).map(|m| {
                        let s = format!("{m:?}");
                        s.split(|c: char| !c.is_alphanumeric()).next().unwrap_or("").to_string()
                    });
                    let e = lower(effect);
                    // Effects on the damage this attack deals (not damage this Pokémon takes, or heals).
                    let changes_damage = !e.contains("takes") && !e.contains("prevent")
                        && (e.contains("more damage") || e.contains("less damage") || e.contains("remaining hp")
                            || e.contains("damage for") || (e.contains("for each") && e.contains("damage"))
                            || (e.contains("damage to") && e.contains("opponent")) || e.contains("knock out"));
                    match mechanic {
                        None => estimator.push(format!("{}: effect not mapped to a mechanic", atk.title)),
                        Some(m) if changes_damage && !ESTIMATOR_PRICED.contains(&m.as_str()) => {
                            estimator.push(format!("{}: {m} estimated at printed damage", atk.title))
                        }
                        _ => {}
                    }
                }
            }
            Card::Trainer(t) => texts.push(("its effect".into(), t.effect.clone())),
            _ => {}
        }
        let unpriced: Vec<&String> = texts.iter().filter(|(_, t)| {
            let t = lower(t);
            t.contains("opponent") && (t.contains("hand") || t.contains("deck"))
        }).map(|(l, _)| l).collect();
        let reply: Vec<&String> = texts.iter().filter(|(_, t)| reply_markers.iter().any(|m| lower(t).contains(m)))
            .map(|(l, _)| l).collect();
        let status = get_implementation_status(card.get_card_id());
        cards.insert(id.clone(), serde_json::json!({
            "name": card.get_name(), "engine_status": status.description(), "engine_complete": status.is_complete(),
            "limitations": implementation_limitations(card.get_card_id()),
            "unpriced_text_rule": unpriced, "estimator_printed_damage": estimator, "pays_off_on_opponent_turn": reply,
        }));
    }
    serde_json::json!(cards)
}

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

fn mean(v: &[f64]) -> f64 {
    if v.is_empty() { f64::NAN } else { v.iter().sum::<f64>() / v.len() as f64 }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let deck_path = arg(&args, "--deck").expect("--deck <list.txt>");
    let panel = arg(&args, "--panel").unwrap_or_else(|| "../decks/research".into());
    let bot = arg(&args, "--bot").unwrap_or_else(|| "k3".into());
    let opp_bot = arg(&args, "--opp-bot").unwrap_or_else(|| "aa".into());
    for code in [&bot, &opp_bot] {
        parse_player_code(code).expect("player code");
        assert!(!code.eq_ignore_ascii_case("jev"), "the jev bot calls a paid API and is not allowed here");
    }
    let games: u64 = arg(&args, "--games").map(|x| x.parse().unwrap()).unwrap_or(40);
    let seed: u64 = arg(&args, "--seed").map(|x| x.parse().unwrap()).unwrap_or(22_200_000_000);
    let attackers: Vec<String> = arg(&args, "--attackers").unwrap_or_default().split(',')
        .map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect();
    let list = Deck::from_file(&deck_path).expect("list file");
    if let Some(path) = arg(&args, "--coverage") {
        std::fs::write(&path, serde_json::to_string_pretty(&coverage(&list)).unwrap()).expect("coverage file");
    }
    let mut panel_files: Vec<_> = std::fs::read_dir(&panel).expect("panel dir").flatten()
        .map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "txt")).collect();
    panel_files.sort();
    std::panic::set_hook(Box::new(|_| {})); // crashes are recorded per game, not printed
    let mut all: Vec<GameRecord> = Vec::new();
    for (o, path) in panel_files.iter().enumerate() {
        let name = path.file_stem().unwrap().to_string_lossy().to_string();
        let opp = Deck::from_file(path.to_str().unwrap()).expect("panel deck");
        let recs: Vec<GameRecord> = (0..games).into_par_iter().map(|i| {
            let s = seed + o as u64 * 10_000 + i;
            catch_unwind(AssertUnwindSafe(|| play(&list, &opp, &name, i, s, &bot, &opp_bot, &attackers)))
                .unwrap_or_else(|e| GameRecord {
                    opponent: name.clone(), i, seed: s, list_seat: (i % 2) as usize,
                    crashed: Some(e.downcast_ref::<String>().cloned()
                        .or_else(|| e.downcast_ref::<&str>().map(|s| s.to_string())).unwrap_or_default()),
                    ..Default::default()
                })
        }).collect();
        all.extend(recs);
    }
    let _ = std::panic::take_hook();
    if let Some(path) = arg(&args, "--games-out") {
        let lines: Vec<String> = all.iter().map(|r| serde_json::to_string(r).unwrap()).collect();
        std::fs::write(&path, lines.join("\n") + "\n").expect("games-out file");
    }
    let ok: Vec<&GameRecord> = all.iter().filter(|r| r.crashed.is_none()).collect();
    println!("{deck_path}: bot {bot} v {opp_bot}, {} games ({} crashed), attackers {:?}", all.len(), all.len() - ok.len(), attackers);
    for first in [true, false] {
        let g: Vec<&&GameRecord> = ok.iter().filter(|r| r.went_first == first).collect();
        let by = |t: usize| g.iter().filter(|r| r.first_main_attack_turn.is_some_and(|x| x <= t)).count() as f64 / g.len().max(1) as f64;
        let could = |t: usize| g.iter().filter(|r| r.first_main_attack_offered_turn.is_some_and(|x| x <= t)).count() as f64 / g.len().max(1) as f64;
        let conceded: Vec<f64> = g.iter().map(|r| r.points_conceded_before_main_attack as f64).collect();
        let dead: Vec<f64> = g.iter().flat_map(|r| r.dead_at_end_of_turn[1..4].iter().flatten().map(|d| *d as f64)).collect();
        let won = g.iter().filter(|r| r.list_won == Some(true)).count() as f64 / g.len().max(1) as f64;
        println!("  going {}: {} games | main attacker could attack by turn 2 {:.0}%, 3 {:.0}%, 4 {:.0}%; did {:.0}%, {:.0}%, {:.0}% | points conceded before it {:.2} | Stage 2 by turn 3 {:.0}% | dead cards per end of turn 2-4 {:.2} | won {:.0}%",
            if first { "first" } else { "second" }, g.len(), 100.0 * could(2), 100.0 * could(3), 100.0 * could(4), 100.0 * by(2), 100.0 * by(3), 100.0 * by(4), mean(&conceded),
            100.0 * g.iter().filter(|r| r.stage2_by_turn3).count() as f64 / g.len().max(1) as f64, mean(&dead), 100.0 * won);
    }
}
