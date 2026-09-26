//! Legality scan (rl/RUN5.md plan item 3): replay k3-vs-k3 games on the Limitless table's own deals and
//! check every OFFERED move, and every resulting state, against RULES_FOR_AGENTS.md. The checks are written
//! from the rules page, not from move generation, so a move-generation bug (like run 4's turn-1 Mega Altaria
//! via Eevee) shows up even when every card's text is right.
//!
//!   cargo run --release --example legality_scan -- --decks ../decks/research --games 1000
//!       [--pairings 13,23] [--bot b3o3 | --bot-a b3n1 --bot-b k3] [--games-out games.jsonl]
//!
//! `--bot` pilots both sides with any player code (default k3), so the same run also gives that bot's
//! table cells on the exact Sept 23 deals. `--bot-a` / `--bot-b` set the bot for the first- and
//! second-named deck of each pairing separately (mixed rows). `--games-out` writes one JSON line per game
//! (pairing, deal, seed, seats, winner, points, turns, first-deck score, a move fingerprint), so two runs
//! can be compared deal by deal.
//!
//! Seeds are the table's: 72,000,000 + pairing x 10,000 + i, pairings in alphabetical order, even i = the
//! first-named deck in seat 0. The scan also prints each pairing's first-deck score, which must equal the
//! Sept 23 table exactly (same engine, same deals).
//!
//! Findings come in two kinds. "RULE" means the rules page says the move or state is impossible. "CHECK" means
//! it is unusual and needs a look (a card effect may allow it).
//!
//! Other pairings (B2e, rl/results/b2e_card_check_2026-09-26/README.md section 4):
//!
//!   legality_scan --pairs <pairings.tsv> --seed-base 21106000000 --games 500 [--root ..] [--pairings 0,48]
//!
//! `--pairs` plays exactly the rows of a tab-separated file whose header names at least pairing, held_key,
//! held_file, opponent and panel_file, instead of the 28 table pairings (`--decks` is then refused). Each row
//! plays held_file (the first-named deck, output `a` = held_key) against panel_file (the second-named deck,
//! `b` = opponent) with the table's seat convention: even i = the held deck in seat 0. Deck paths are read
//! relative to `--root` (default "..", the repo root when the scan runs from engine/ as usual; an absolute path
//! is used as it is). `--seed-base` replaces 72,000,000 (seed = base + pairing x 10,000 + i); `--pairs` needs
//! it, and a seed_first column, if the file has one, must equal base + pairing x 10,000. `--pairs` refuses
//! `--games` above 10,000 (one pairing's sub-block); `--seed-base` and `--root` are refused without `--pairs`.
//! In `--pairs` mode each `--games-out` line also carries a_file and b_file (the file's paths) and, for a game
//! with findings, their codes and counts (findings) and each code's first example in that game
//! (finding_examples). Without `--pairs` and `--seed-base` the scan runs exactly as before.

use deckgym::actions::{Action, SimpleAction};
use deckgym::models::{Card, EnergyType, PlayedCard, TrainerType};
use deckgym::players::{create_players, parse_player_code};
use deckgym::state::GameOutcome;
use deckgym::{Deck, Game, State};
use rayon::prelude::*;
use std::collections::hash_map::DefaultHasher;
use std::collections::{BTreeMap, HashMap, HashSet};
use std::hash::{Hash, Hasher};

const NAMES: [&str; 8] = [
    "altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing",
];
const SEED_BASE: u64 = 72_000_000;
const EXAMPLES_KEPT: usize = 4;
/// The rules page these checks were written from. It describes the rules4 engine.
const RULES_SOURCE: &str = "RULES_FOR_AGENTS.md (updated 2026-09-22, rules4)";

#[derive(Default)]
struct Findings {
    count: BTreeMap<String, u64>,
    games: BTreeMap<String, u64>,
    examples: BTreeMap<String, Vec<String>>,
}

impl Findings {
    fn merge(&mut self, other: Findings) {
        for (k, v) in other.count {
            *self.count.entry(k).or_default() += v;
        }
        for (k, v) in other.games {
            *self.games.entry(k).or_default() += v;
        }
        for (k, v) in other.examples {
            let e = self.examples.entry(k).or_default();
            for x in v {
                if e.len() < EXAMPLES_KEPT {
                    e.push(x);
                }
            }
        }
    }
}

/// What the turn owner has done so far this turn, tracked from the chosen moves alone.
#[derive(Default)]
struct Turn {
    number: u8,
    owner: usize,
    supporters: u32,
    retreats: u32,
    turn_energy: u32,
    stadiums: u32,
    attacked: bool,
    /// Stacks (card ids, bottom first) put into play or evolved this turn. A Pokémon keeps its stack when it
    /// moves between slots, so this follows it through retreats and promotions.
    placed: Vec<Vec<String>>,
    evolved: Vec<Vec<String>>,
}

fn stack(p: &PlayedCard) -> Vec<String> {
    let mut s: Vec<String> = p.cards_behind.iter().map(|c| c.get_id()).collect();
    s.push(p.card.get_id());
    s
}

fn is_boosted_eevee_active(state: &State, player: usize, idx: usize) -> bool {
    idx == 0
        && state.in_play_pokemon[player][0].as_ref().is_some_and(|p| match &p.card {
            Card::Pokemon(pc) => pc.ability.as_ref().is_some_and(|a| a.title == "Boosted Evolution"),
            _ => false,
        })
}

fn energy_covers(attached: &[EnergyType], cost: &[EnergyType]) -> bool {
    let mut pool: HashMap<EnergyType, i32> = HashMap::new();
    for e in attached {
        *pool.entry(*e).or_default() += 1;
    }
    let mut colorless = 0;
    for e in cost {
        if *e == EnergyType::Colorless {
            colorless += 1;
        } else {
            let n = pool.entry(*e).or_default();
            if *n == 0 {
                return false;
            }
            *n -= 1;
        }
    }
    pool.values().sum::<i32>() >= colorless
}

fn unique_on_board(state: &State, player: usize, s: &[String]) -> bool {
    state.in_play_pokemon[player].iter().flatten().filter(|p| stack(p) == s).count() == 1
}

/// Rules about the moves on offer. Returns (code, detail) pairs.
fn check_offered(state: &State, turn: &Turn, actor: usize, actions: &[Action]) -> Vec<(String, String)> {
    let mut out = Vec::new();
    let t = state.turn_count;
    let mut flag = |code: &str, a: &Action| out.push((code.to_string(), format!("{:?}", a.action)));
    for a in actions {
        let own_turn = actor == turn.owner && t >= 1;
        let voluntary = own_turn && !a.is_stack;
        let active = state.in_play_pokemon[actor][0].as_ref();
        match &a.action {
            SimpleAction::Evolve { evolution, in_play_idx, from_deck } => {
                let Some(target) = state.in_play_pokemon[actor][*in_play_idx].as_ref() else {
                    flag("RULE evolve: empty slot", a);
                    continue;
                };
                let eevee = is_boosted_eevee_active(state, actor, *in_play_idx);
                if t <= 2 && !eevee {
                    flag("RULE evolve: on a player's first turn", a);
                }
                let s = stack(target);
                if unique_on_board(state, actor, &s) {
                    if turn.placed.contains(&s) && !eevee {
                        flag("RULE evolve: Pokémon put into play this turn", a);
                    }
                    if turn.evolved.contains(&s) {
                        flag("RULE evolve: second evolution this turn", a);
                    }
                }
                if target.played_this_turn && !eevee && !turn.placed.contains(&s) && !turn.evolved.contains(&s) {
                    flag("CHECK evolve: engine marks target played this turn, scan doesn't", a);
                }
                if !a.is_stack && !from_deck {
                    if let (Card::Pokemon(evo), Card::Pokemon(base)) = (evolution, &target.card) {
                        if evo.evolves_from.as_deref() != Some(base.name.as_str()) {
                            flag("CHECK evolve: evolves_from doesn't name the target", a);
                        }
                    }
                }
            }
            SimpleAction::Attack(attack) => {
                if let Some(p) = active {
                    if p.is_asleep() || p.is_paralyzed() {
                        flag("RULE attack: while Asleep or Paralyzed", a);
                    }
                    if !energy_covers(&p.attached_energy, &attack.energy_required) {
                        flag("CHECK attack: attached Energy doesn't cover the printed cost", a);
                    }
                }
                if own_turn && t == 1 && !attack.energy_required.is_empty() {
                    flag("CHECK attack: costed attack on the first player's first turn", a);
                }
                if voluntary && turn.attacked {
                    flag("RULE attack: second attack this turn", a);
                }
            }
            SimpleAction::Retreat(idx) => {
                if voluntary && turn.retreats >= 1 {
                    flag("RULE retreat: second retreat this turn", a);
                }
                if active.is_some_and(|p| p.is_asleep() || p.is_paralyzed()) {
                    flag("RULE retreat: while Asleep or Paralyzed", a);
                }
                if state.in_play_pokemon[actor][*idx].is_none() || *idx == 0 {
                    flag("RULE retreat: to an empty or Active slot", a);
                }
            }
            SimpleAction::Attach { attachments, is_turn_energy: true } => {
                if turn.turn_energy >= 1 {
                    flag("RULE energy: second Energy Zone attach this turn", a);
                }
                if t == 1 {
                    flag("RULE energy: first player's first turn", a);
                }
                for (_, _, idx) in attachments {
                    if state.in_play_pokemon[actor][*idx].is_none() {
                        flag("RULE energy: attach to an empty slot", a);
                    }
                }
            }
            SimpleAction::Place(card, idx) => {
                if !card.is_basic() && !card.is_fossil() {
                    flag("RULE place: not a Basic Pokémon", a);
                }
                if state.in_play_pokemon[actor][*idx].is_some() {
                    flag("RULE place: slot already occupied", a);
                }
            }
            SimpleAction::AttachTool { in_play_idx, .. } => {
                match state.in_play_pokemon[actor][*in_play_idx].as_ref() {
                    None => flag("RULE tool: attach to an empty slot", a),
                    Some(p) if !p.attached_tools.is_empty() => flag("RULE tool: Pokémon already has a Tool", a),
                    _ => {}
                }
            }
            SimpleAction::Play { trainer_card } => {
                match trainer_card.trainer_card_type {
                    TrainerType::Supporter if voluntary && turn.supporters >= 1 => {
                        flag("RULE supporter: second Supporter this turn", a)
                    }
                    TrainerType::Stadium if voluntary => {
                        if turn.stadiums >= 1 {
                            flag("RULE stadium: second Stadium play this turn", a);
                        }
                        if state.active_stadium.as_ref().is_some_and(|s| s.get_name() == trainer_card.name) {
                            flag("RULE stadium: same name as the Stadium in play", a);
                        }
                    }
                    _ => {}
                }
                if (trainer_card.name == "Rare Candy" || trainer_card.name == "Quick-Grow Extract") && t <= 2 {
                    flag("RULE evolve item: on a player's first turn", a);
                }
            }
            _ => {}
        }
        let turn_ending_or_forced = matches!(
            a.action,
            SimpleAction::EndTurn
                | SimpleAction::ResolvePokemonCheckup
                | SimpleAction::FinishPokemonCheckup
                | SimpleAction::ResolveEndTurnEvolution { .. }
        );
        if voluntary && turn.attacked && !turn_ending_or_forced && !matches!(a.action, SimpleAction::Attack(_)) {
            flag("RULE turn: move offered after the turn's attack", a);
        }
    }
    out
}

fn card_count(state: &State, player: usize) -> usize {
    let in_play: usize = state.in_play_pokemon[player]
        .iter()
        .flatten()
        .map(|p| 1 + p.cards_behind.len() + p.attached_tools.len())
        .sum();
    let stadium = usize::from(state.active_stadium.is_some() && state.active_stadium_owner == Some(player));
    state.decks[player].cards.len() + state.hands[player].len() + state.discard_piles[player].len() + in_play + stadium
}

/// Rules about the state itself.
fn check_state(state: &State, start_cards: [usize; 2], game_over: bool) -> Vec<(String, String)> {
    let mut out = Vec::new();
    // Cards in transit (a Tool played but not yet attached, a Supporter mid-effect) are counted only once
    // nothing is pending.
    let settled = state.move_generation_stack.is_empty();
    for player in 0..2 {
        let n = card_count(state, player);
        if settled && n != start_cards[player] {
            out.push(("CHECK cards: player's card count changed".into(), format!("player {player}: {n} vs {}", start_cards[player])));
        }
        for (idx, slot) in state.in_play_pokemon[player].iter().enumerate() {
            let Some(p) = slot else { continue };
            let exclusive = [p.is_asleep(), p.is_paralyzed(), p.is_confused()].iter().filter(|x| **x).count();
            if exclusive > 1 {
                out.push(("RULE status: two of Asleep/Paralyzed/Confused at once".into(), p.get_name()));
            }
            if idx > 0 && (exclusive > 0 || p.is_poisoned() || p.is_burned()) {
                out.push(("RULE status: Benched Pokémon has a Special Condition".into(), p.get_name()));
            }
        }
        if state.hands[player].len() > 10 {
            out.push(("CHECK hand: more than 10 cards".into(), format!("{} cards", state.hands[player].len())));
        }
        if state.points[player] >= 3 && !game_over {
            out.push(("RULE points: 3 or more points and the game goes on".into(), format!("{:?}", state.points)));
        }
    }
    if state.turn_count > 30 && !game_over {
        out.push(("CHECK turn limit: past turn 30".into(), format!("turn {}", state.turn_count)));
    }
    out
}

fn update_turn(turn: &mut Turn, before: &State, after: &State, actor: usize, action: &Action) {
    if actor != turn.owner {
        return;
    }
    match &action.action {
        SimpleAction::Play { trainer_card } => match trainer_card.trainer_card_type {
            TrainerType::Supporter => turn.supporters += 1,
            TrainerType::Stadium => turn.stadiums += 1,
            _ => {}
        },
        SimpleAction::Retreat(_) => turn.retreats += 1,
        SimpleAction::Attach { is_turn_energy: true, .. } => turn.turn_energy += 1,
        SimpleAction::Attack(_) => turn.attacked = true,
        SimpleAction::Place(_, idx) => {
            if let Some(p) = after.in_play_pokemon[actor][*idx].as_ref() {
                turn.placed.push(stack(p));
            }
        }
        SimpleAction::Evolve { in_play_idx, .. } => {
            if let (Some(old), Some(new)) = (
                before.in_play_pokemon[actor][*in_play_idx].as_ref(),
                after.in_play_pokemon[actor][*in_play_idx].as_ref(),
            ) {
                let (old, new) = (stack(old), stack(new));
                if turn.placed.contains(&old) {
                    turn.placed.push(new.clone());
                }
                turn.evolved.push(new);
            }
        }
        _ => {}
    }
}

/// Hyper Ray use, counted per turn exactly as rl/results/see_everything_2026-09-24.md's hydsum.py does:
/// a turn where Hyper Ray was legal counts as "used" if Hyper Ray was the turn's attack, or "passed" if the
/// player ended the turn at a point where Hyper Ray was on offer. "KO-able" means the opponent's Active had
/// 130 HP or less left at that moment.
#[derive(Default, Clone, Copy)]
struct HyperRay {
    ko_used: u64,
    ko_passed: u64,
    noko_used: u64,
    noko_passed: u64,
}

/// Chase Order-style choices (an attack offering "discard one of your Benched Pokemon for more damage",
/// SimpleAction::DiscardOwnBenchedThenDamage): how often the choice was offered, how often a Pokemon was
/// discarded, and which.
#[derive(Default, Clone)]
struct ChaseOrder {
    offered: u64,
    discarded: u64,
    names: BTreeMap<String, u64>,
}

#[derive(Default)]
struct HyperTurn {
    used_opp_hp: Option<Option<u32>>,
    declined_opp_hp: Option<Option<u32>>,
}

struct GameResult {
    seed: u64,
    first_seat: usize,
    /// Seat that won, or -1 for a tie.
    winner_seat: i32,
    points: [u8; 2],
    turns: u8,
    first_deck_score: f64,
    hyper_ray: HyperRay,
    chase_order: ChaseOrder,
    /// Fingerprint of every chosen move in order: distinct games have distinct fingerprints.
    fingerprint: u64,
    findings: Findings,
}

/// The decks a run can play, by index, with the names its output uses, and its seed base. The table run holds
/// the eight NAMES decks and SEED_BASE; a `--pairs` run holds two decks per row of the pairings file.
struct Lineup {
    decks: Vec<Deck>,
    names: Vec<String>,
    seed_base: u64,
}

/// One pairing: its number (which fixes its seeds), the Lineup indexes of its first- and second-named decks,
/// and, for a `--pairs` row, the two deck paths as the pairings file gives them.
struct Row {
    pairing: usize,
    a: usize,
    b: usize,
    files: Option<(String, String)>,
}

fn play_one(lineup: &Lineup, pairing: usize, (a, b): (usize, usize), i: u64, bot_a: &str, bot_b: &str) -> GameResult {
    let seed = lineup.seed_base + pairing as u64 * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (a, b) } else { (b, a) };
    let (code_a, code_b) = (parse_player_code(bot_a).unwrap(), parse_player_code(bot_b).unwrap());
    let codes = if first_seat == 0 { vec![code_a, code_b] } else { vec![code_b, code_a] };
    let players = create_players(lineup.decks[d0].clone(), lineup.decks[d1].clone(), codes);
    let mut game = Game::new(players, seed);

    let mut findings = Findings::default();
    let mut seen: BTreeMap<String, bool> = BTreeMap::new();
    let mut turn = Turn::default();
    let mut moves = DefaultHasher::new();
    let mut hyper_turns: BTreeMap<(usize, u8), HyperTurn> = BTreeMap::new();
    let mut chase_order = ChaseOrder::default();
    let start = game.get_state_clone();
    let start_cards = [card_count(&start, 0), card_count(&start, 1)];
    let mut record = |findings: &mut Findings, list: Vec<(String, String)>, state: &State| {
        for (code, detail) in list {
            *findings.count.entry(code.clone()).or_default() += 1;
            if !seen.contains_key(&code) {
                seen.insert(code.clone(), true);
                *findings.games.entry(code.clone()).or_default() += 1;
                let e = findings.examples.entry(code).or_default();
                if e.len() < EXAMPLES_KEPT {
                    e.push(format!(
                        "{} v {}, seed {seed}, turn {}: {}",
                        lineup.names[d0], lineup.names[d1], state.turn_count, detail.chars().take(160).collect::<String>()
                    ));
                }
            }
        }
    };

    while !game.is_game_over() {
        let before = game.get_state_clone();
        if before.turn_count != turn.number {
            turn = Turn { number: before.turn_count, owner: before.current_player, ..Default::default() };
        }
        let (actor, actions) = before.generate_possible_actions();
        let offered = check_offered(&before, &turn, actor, &actions);
        record(&mut findings, offered, &before);
        let chosen = game.play_tick();
        format!("{:?}", chosen).hash(&mut moves);
        if actions.iter().any(|a| matches!(a.action, SimpleAction::DiscardOwnBenchedThenDamage { .. })) {
            chase_order.offered += 1;
            if let SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } = &chosen.action {
                chase_order.discarded += 1;
                for idx in in_play_idxs {
                    let name = before.in_play_pokemon[actor][*idx].as_ref().map(|p| p.get_name()).unwrap_or_default();
                    *chase_order.names.entry(name).or_default() += 1;
                }
            }
        }
        let is_hyper = |a: &SimpleAction| matches!(a, SimpleAction::Attack(x) if x.title == "Hyper Ray");
        if before.turn_count > 0 && actions.iter().any(|a| is_hyper(&a.action)) {
            let opp_hp = before.in_play_pokemon[1 - actor][0].as_ref().map(|p| p.get_remaining_hp());
            let record = hyper_turns.entry((actor, before.turn_count)).or_default();
            if is_hyper(&chosen.action) {
                record.used_opp_hp = Some(opp_hp);
            } else if matches!(chosen.action, SimpleAction::EndTurn) {
                record.declined_opp_hp = Some(opp_hp);
            }
        }
        let after = game.get_state_clone();
        update_turn(&mut turn, &before, &after, chosen.actor, &chosen);
        let state_findings: Vec<(String, String)> = check_state(&after, start_cards, game.is_game_over())
            .into_iter()
            .map(|(code, detail)| (code, format!("{detail}; after {:?}", chosen.action)))
            .collect();
        record(&mut findings, state_findings, &after);
    }
    let end = game.get_state_clone();
    let (first_deck_score, winner_seat) = match end.winner {
        Some(GameOutcome::Win(w)) => (f64::from(u8::from(w == first_seat)), w as i32),
        _ => (0.5, -1),
    };
    let mut hyper_ray = HyperRay::default();
    for record in hyper_turns.values() {
        let ko = |hp: &Option<u32>| hp.is_some_and(|h| h <= 130);
        if let Some(hp) = &record.used_opp_hp {
            if ko(hp) { hyper_ray.ko_used += 1 } else { hyper_ray.noko_used += 1 }
        } else if let Some(hp) = &record.declined_opp_hp {
            if ko(hp) { hyper_ray.ko_passed += 1 } else { hyper_ray.noko_passed += 1 }
        }
    }
    GameResult {
        seed,
        first_seat,
        winner_seat,
        points: end.points,
        turns: end.turn_count,
        first_deck_score,
        hyper_ray,
        chase_order,
        fingerprint: moves.finish(),
        findings,
    }
}

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

/// Reads a `--pairs` file (see the header): two decks per row, held first, in the file's row order.
fn read_pairs(path: &str, root: &str, seed_base: u64) -> (Lineup, Vec<Row>) {
    let text = std::fs::read_to_string(path).unwrap_or_else(|e| panic!("pairs file {path}: {e}"));
    let mut lines = text.trim_start_matches('\u{feff}').lines().filter(|l| !l.trim().is_empty());
    let header: Vec<&str> = lines.next().expect("pairs file header").split('\t').map(str::trim).collect();
    let col = |name: &str| header.iter().position(|h| *h == name);
    let need = |name: &str| col(name).unwrap_or_else(|| panic!("pairs file {path} has no {name} column"));
    let (c_pairing, c_held_key, c_held_file) = (need("pairing"), need("held_key"), need("held_file"));
    let (c_opponent, c_panel_file, c_seed_first) = (need("opponent"), need("panel_file"), col("seed_first"));
    let load = |file: &str| {
        let full = std::path::Path::new(root).join(file);
        let full = full.to_str().expect("deck path");
        Deck::from_file(full).unwrap_or_else(|e| panic!("deck file {full}: {e}"))
    };
    let mut lineup = Lineup { decks: Vec::new(), names: Vec::new(), seed_base };
    let mut rows = Vec::new();
    let mut listed = HashSet::new();
    for line in lines {
        let f: Vec<&str> = line.split('\t').map(str::trim).collect();
        assert!(f.len() >= header.len(), "pairs file {path}: short row {line:?}");
        let pairing = f[c_pairing].parse::<usize>().unwrap_or_else(|e| panic!("pairs file {path}: pairing {:?}: {e}", f[c_pairing]));
        assert!(listed.insert(pairing), "pairs file {path}: pairing {pairing} listed twice");
        if let Some(c) = c_seed_first {
            let want = seed_base + pairing as u64 * 10_000;
            assert_eq!(f[c].parse::<u64>().ok(), Some(want), "pairing {pairing}: seed_first doesn't match --seed-base {seed_base}");
        }
        let a = lineup.decks.len();
        lineup.decks.push(load(f[c_held_file]));
        lineup.names.push(f[c_held_key].to_string());
        lineup.decks.push(load(f[c_panel_file]));
        lineup.names.push(f[c_opponent].to_string());
        rows.push(Row { pairing, a, b: a + 1, files: Some((f[c_held_file].to_string(), f[c_panel_file].to_string())) });
    }
    assert!(!rows.is_empty(), "pairs file {path} lists no pairings");
    (lineup, rows)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let games: u64 = arg(&args, "--games").map(|x| x.parse().unwrap()).unwrap_or(1000);
    let only: Option<Vec<usize>> =
        arg(&args, "--pairings").map(|x| x.split(',').map(|p| p.trim().parse().unwrap()).collect());
    let bot = arg(&args, "--bot").unwrap_or_else(|| "k3".into());
    let bot_a = arg(&args, "--bot-a").unwrap_or_else(|| bot.clone());
    let bot_b = arg(&args, "--bot-b").unwrap_or_else(|| bot.clone());
    for code in [&bot_a, &bot_b] {
        parse_player_code(code).expect("player code");
        // The jev bot calls a paid outside service; no scan or table run may use it (Dustin, Sept 24).
        assert!(!code.eq_ignore_ascii_case("jev"), "the jev bot calls a paid API and is not allowed here");
    }
    let pairs_file = arg(&args, "--pairs");
    let seed_base: u64 = arg(&args, "--seed-base").map(|x| x.parse().unwrap()).unwrap_or(SEED_BASE);
    let root = arg(&args, "--root").unwrap_or_else(|| "..".into());
    if pairs_file.is_some() {
        assert!(arg(&args, "--seed-base").is_some(), "--pairs needs --seed-base (72,000,000 is the table's own block)");
        assert!(arg(&args, "--decks").is_none(), "--pairs names its own deck files; --decks is for the table's 28");
        assert!(games <= 10_000, "--pairs: a pairing's sub-block holds 10,000 seeds, so --games {games} is too many");
    } else {
        assert!(arg(&args, "--seed-base").is_none(), "--seed-base is only for --pairs (the table's base is 72,000,000)");
        assert!(arg(&args, "--root").is_none(), "--root is only for --pairs");
    }
    let mut games_out = arg(&args, "--games-out")
        .map(|path| std::io::BufWriter::new(std::fs::File::create(path).expect("games-out file")));
    let (lineup, rows) = match &pairs_file {
        None => {
            let decks: Vec<Deck> = NAMES.iter().map(|n| Deck::from_file(&format!("{dir}/{n}.txt")).expect("deck file")).collect();
            let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
            let rows: Vec<Row> = pairs.into_iter().enumerate().map(|(pairing, (a, b))| Row { pairing, a, b, files: None }).collect();
            (Lineup { decks, names: NAMES.iter().map(|n| n.to_string()).collect(), seed_base }, rows)
        }
        Some(path) => read_pairs(path, &root, seed_base),
    };

    let bots = if bot_a == bot_b { format!("bot {bot_a}") } else { format!("bot {bot_a} (first-named deck) v {bot_b} (second)") };
    println!("{bots}, {games} table deals per pairing, rules checked against {RULES_SOURCE}");
    if let Some(path) = &pairs_file {
        println!("pairings from {path} ({} rows), seed base {seed_base}, deck paths relative to {root}", rows.len());
    }
    let mut all = Findings::default();
    for row in &rows {
        let (p, a, b) = (row.pairing, row.a, row.b);
        if only.as_ref().is_some_and(|o| !o.contains(&p)) {
            continue;
        }
        let results: Vec<GameResult> =
            (0..games).into_par_iter().map(|i| play_one(&lineup, p, (a, b), i, &bot_a, &bot_b)).collect();
        let score: f64 = results.iter().map(|r| r.first_deck_score).sum::<f64>() / games as f64;
        let flagged = results.iter().filter(|r| !r.findings.count.is_empty()).count();
        let distinct = results.iter().map(|r| r.fingerprint).collect::<HashSet<_>>().len();
        println!(
            "{:>9} v {:<9} first deck {:5.1}%   distinct games {distinct} of {games}   games with findings: {flagged}",
            lineup.names[a], lineup.names[b], 100.0 * score
        );
        let h = results.iter().fold(HyperRay::default(), |mut s, r| {
            s.ko_used += r.hyper_ray.ko_used;
            s.ko_passed += r.hyper_ray.ko_passed;
            s.noko_used += r.hyper_ray.noko_used;
            s.noko_passed += r.hyper_ray.noko_passed;
            s
        });
        if h.ko_used + h.ko_passed + h.noko_used + h.noko_passed > 0 {
            let pct = 100.0 * h.noko_used as f64 / (h.noko_used + h.noko_passed).max(1) as f64;
            println!(
                "      Hyper Ray turns: KO-able used {} passed {} | not KO-able used {} passed {} ({pct:.0}% used)",
                h.ko_used, h.ko_passed, h.noko_used, h.noko_passed
            );
        }
        let chase = results.iter().fold(ChaseOrder::default(), |mut s, r| {
            s.offered += r.chase_order.offered;
            s.discarded += r.chase_order.discarded;
            for (name, n) in &r.chase_order.names {
                *s.names.entry(name.clone()).or_default() += n;
            }
            s
        });
        if chase.offered > 0 {
            let names: Vec<String> = chase.names.iter().map(|(name, n)| format!("{name} {n}")).collect();
            println!(
                "      Chase Order choices: discarded {} of {} ({})",
                chase.discarded, chase.offered, names.join(", ")
            );
        }
        if let Some(out) = games_out.as_mut() {
            use std::io::Write;
            for (i, r) in results.iter().enumerate() {
                let h = r.hyper_ray;
                let mut line = serde_json::json!({
                    "pairing": p, "a": lineup.names[a], "b": lineup.names[b], "i": i, "seed": r.seed,
                    "bot_a": bot_a, "bot_b": bot_b, "first_seat": r.first_seat,
                    "winner_seat": r.winner_seat, "points": r.points, "turns": r.turns,
                    "first_deck_score": r.first_deck_score, "moves": format!("{:016x}", r.fingerprint),
                });
                if h.ko_used + h.ko_passed + h.noko_used + h.noko_passed > 0 {
                    line["hyper_ray"] = serde_json::json!([h.ko_used, h.ko_passed, h.noko_used, h.noko_passed]);
                }
                if r.chase_order.offered > 0 {
                    line["chase_order"] = serde_json::json!({ "offered": r.chase_order.offered,
                        "discarded": r.chase_order.discarded, "names": r.chase_order.names });
                }
                if let Some((file_a, file_b)) = &row.files {
                    line["a_file"] = serde_json::json!(file_a);
                    line["b_file"] = serde_json::json!(file_b);
                    if !r.findings.count.is_empty() {
                        line["findings"] = serde_json::json!(r.findings.count);
                        // Each code's first example in this game: the log keeps only four per code for the run.
                        let first: BTreeMap<&String, &String> =
                            r.findings.examples.iter().filter_map(|(code, e)| e.first().map(|x| (code, x))).collect();
                        line["finding_examples"] = serde_json::json!(first);
                    }
                }
                writeln!(out, "{line}").expect("write games-out");
            }
            out.flush().expect("flush games-out");
        }
        for r in results {
            all.merge(r.findings);
        }
    }
    println!("\nFindings (occurrences / games affected):");
    if all.count.is_empty() {
        println!("  none");
    }
    for (code, n) in &all.count {
        println!("  {code}: {n} / {}", all.games[code]);
        for e in &all.examples[code] {
            println!("      e.g. {e}");
        }
    }
}
