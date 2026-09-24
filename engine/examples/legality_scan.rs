//! Legality scan (rl/RUN5.md plan item 3): replay k3-vs-k3 games on the Limitless table's own deals and
//! check every OFFERED move, and every resulting state, against RULES_FOR_AGENTS.md. The checks are written
//! from the rules page, not from move generation, so a move-generation bug (like run 4's turn-1 Mega Altaria
//! via Eevee) shows up even when every card's text is right.
//!
//!   cargo run --release --example legality_scan -- --decks ../decks/research --games 1000
//!       [--pairings 13,23] [--bot b3o3]
//!
//! `--bot` pilots both sides with any player code (default k3), so the same run also gives that bot's
//! table cells on the exact Sept 23 deals.
//!
//! Seeds are the table's: 72,000,000 + pairing x 10,000 + i, pairings in alphabetical order, even i = the
//! first-named deck in seat 0. The scan also prints each pairing's first-deck score, which must equal the
//! Sept 23 table exactly (same engine, same deals).
//!
//! Findings come in two kinds. "RULE" means the rules page says the move or state is impossible. "CHECK" means
//! it is unusual and needs a look (a card effect may allow it).

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

struct GameResult {
    first_deck_score: f64,
    /// Fingerprint of every chosen move in order: distinct games have distinct fingerprints.
    fingerprint: u64,
    findings: Findings,
}

fn play_one(decks: &[Deck; 8], pairing: usize, i: u64, bot: &str) -> GameResult {
    let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();
    let (a, b) = pairs[pairing];
    let seed = SEED_BASE + pairing as u64 * 10_000 + i;
    let first_seat = if i % 2 == 0 { 0 } else { 1 };
    let (d0, d1) = if first_seat == 0 { (a, b) } else { (b, a) };
    let code = parse_player_code(bot).unwrap();
    let players = create_players(decks[d0].clone(), decks[d1].clone(), vec![code.clone(), code]);
    let mut game = Game::new(players, seed);

    let mut findings = Findings::default();
    let mut seen: BTreeMap<String, bool> = BTreeMap::new();
    let mut turn = Turn::default();
    let mut moves = DefaultHasher::new();
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
                        NAMES[d0], NAMES[d1], state.turn_count, detail.chars().take(160).collect::<String>()
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
        let after = game.get_state_clone();
        update_turn(&mut turn, &before, &after, chosen.actor, &chosen);
        let state_findings: Vec<(String, String)> = check_state(&after, start_cards, game.is_game_over())
            .into_iter()
            .map(|(code, detail)| (code, format!("{detail}; after {:?}", chosen.action)))
            .collect();
        record(&mut findings, state_findings, &after);
    }
    let first_deck_score = match game.get_state_clone().winner {
        Some(GameOutcome::Win(w)) => f64::from(u8::from(w == first_seat)),
        _ => 0.5,
    };
    GameResult { first_deck_score, fingerprint: moves.finish(), findings }
}

fn arg(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let games: u64 = arg(&args, "--games").map(|x| x.parse().unwrap()).unwrap_or(1000);
    let only: Option<Vec<usize>> =
        arg(&args, "--pairings").map(|x| x.split(',').map(|p| p.trim().parse().unwrap()).collect());
    let bot = arg(&args, "--bot").unwrap_or_else(|| "k3".into());
    parse_player_code(&bot).expect("player code");
    // The jev bot calls a paid outside service; no scan or table run may use it (Dustin, Sept 24).
    assert!(!bot.eq_ignore_ascii_case("jev"), "the jev bot calls a paid API and is not allowed here");
    let decks: [Deck; 8] = NAMES.map(|n| Deck::from_file(&format!("{dir}/{n}.txt")).expect("deck file"));
    let pairs: Vec<(usize, usize)> = (0..8).flat_map(|a| (a + 1..8).map(move |b| (a, b))).collect();

    println!("bot {bot}, {games} table deals per pairing, rules checked against {RULES_SOURCE}");
    let mut all = Findings::default();
    for (p, (a, b)) in pairs.iter().enumerate() {
        if only.as_ref().is_some_and(|o| !o.contains(&p)) {
            continue;
        }
        let results: Vec<GameResult> = (0..games).into_par_iter().map(|i| play_one(&decks, p, i, &bot)).collect();
        let score: f64 = results.iter().map(|r| r.first_deck_score).sum::<f64>() / games as f64;
        let flagged = results.iter().filter(|r| !r.findings.count.is_empty()).count();
        let distinct = results.iter().map(|r| r.fingerprint).collect::<HashSet<_>>().len();
        println!(
            "{:>9} v {:<9} first deck {:5.1}%   distinct games {distinct} of {games}   games with findings: {flagged}",
            NAMES[*a], NAMES[*b], 100.0 * score
        );
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
