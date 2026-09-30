//! km diagnosis, Altaria v Suicune (the laptop's Sept 30 request; diagnosis only, nothing gates on it). For each named
//! deal of table pairing 4 (Altaria v Suicune, 72,000,000 + 40,000 + i, even i = Altaria in seat 0), it replays kta3 on
//! both sides exactly as the table played it, and at every decision of each seat also asks km3 what it would choose
//! there: the same observation, the same offered moves (canonical order) and the same search seed
//! (`Game::randomness().decision(actor, n)`, as `Game::play_tick` seeds it). Until one seat's km3 answer differs from
//! kta3's, a game with km3 on that seat is move for move the kta3 game, so the first differing answer is the first
//! differing decision of the km3 game: for km3 on Suicune only (the mixed row "second"), on Altaria only ("first"), and
//! on both (the earlier of the two). The replayed game's move fingerprint (legality_scan's `moves`) is printed, to check
//! against kta3's committed game. At each first difference it prints both moves, the Stadium in play, both Actives, the
//! 8 moves before it, each side's Tools in play, and kta's and km's clocks from the deciding seat's view
//! (`km_diag_clocks`, a scratch-only helper). When km3's move is Field Blower, it also applies that move to a copy of the
//! game (`Game::from_state`) and asks km3 for its next choice there (the target), with the next search seed; that copy
//! has no revealed-card knowledge, so the target is km3's pick from public information, not a replay of the km3 game.
//! Built as an example in a scratch copy of build B's engine/ (1f6319e) with that helper added; B is unchanged.
//!
//!   km_diag_trace --decks ../decks/research --deals 13,38,... > rows.jsonl
use deckgym::models::Card;
use deckgym::observation::canonical_actions;
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game, State};
use rand::rngs::StdRng;
use rand::SeedableRng;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

fn active(state: &State, p: usize) -> serde_json::Value {
    match state.maybe_get_active(p) {
        Some(x) => {
            let stage = match &x.card {
                Card::Pokemon(c) => c.stage as i64,
                _ => -1,
            };
            serde_json::json!({"name": x.get_name(), "hp": x.get_remaining_hp(), "stage": stage})
        }
        None => serde_json::Value::Null,
    }
}

fn tools(state: &State, p: usize) -> Vec<String> {
    state
        .enumerate_in_play_pokemon(p)
        .flat_map(|(slot, x)| {
            x.attached_tools.iter().map(move |t| match t {
                Card::Trainer(t) => format!("{} on {} ({})", t.name, x.get_name(), if slot == 0 { "Active" } else { "Bench" }),
                other => format!("{other:?}"),
            })
        })
        .collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = arg(&args, "--decks").unwrap_or_else(|| "../decks/research".into());
    let deals: Vec<u64> = arg(&args, "--deals").expect("--deals").split(',').map(|x| x.parse().unwrap()).collect();
    let (pairing, names) = (4u64, ["altaria", "suicune"]);
    let decks = names.map(|n| Deck::from_file(&format!("{dir}/{n}.txt")).expect("deck file"));
    for i in deals {
        let seed = 72_000_000 + pairing * 10_000 + i;
        let first_seat = (i % 2) as usize;
        let seat_deck = if first_seat == 0 { [0, 1] } else { [1, 0] };
        let code = |c: &str| parse_player_code(c).unwrap();
        let players = create_players(decks[seat_deck[0]].clone(), decks[seat_deck[1]].clone(), vec![code("kta3"), code("kta3")]);
        let mut shadows =
            create_players(decks[seat_deck[0]].clone(), decks[seat_deck[1]].clone(), vec![code("km3"), code("km3")]);
        let mut game = Game::new(players, seed);
        let mut moves = DefaultHasher::new();
        let mut counts = [0u64; 2];
        let mut first: [Option<serde_json::Value>; 2] = [None, None];
        let mut history: Vec<String> = Vec::new();
        let mut tick = 0usize;
        while !game.is_game_over() {
            let state = game.get_state_clone();
            let (actor, mut actions) = state.generate_possible_actions();
            canonical_actions(&mut actions);
            let mut shadow = None;
            if actions.len() > 1 {
                let decision = game.randomness().decision(actor, counts[actor]);
                counts[actor] += 1;
                if first[actor].is_none() {
                    let observation = game.observation(actor);
                    let mut rng = StdRng::seed_from_u64(decision.search_seed);
                    let km = shadows[actor].decision_fn(&mut rng, &observation, &actions);
                    let clocks = deckgym::players::value_functions::km_diag_clocks(observation.visible_state(), actor);
                    // km3's next choice after its own move, on a copy, when that move is Field Blower (its target).
                    let is_blower = matches!(&km.action, deckgym::actions::SimpleAction::Play { trainer_card } if trainer_card.name == "Field Blower");
                    let target = is_blower.then(|| {
                        let copies = create_players(decks[seat_deck[0]].clone(), decks[seat_deck[1]].clone(), vec![code("km3"), code("km3")]);
                        let mut side = Game::from_state(state.clone(), copies, seed);
                        side.apply_action(&km);
                        let after = side.get_state_clone();
                        let (next_actor, mut next) = after.generate_possible_actions();
                        canonical_actions(&mut next);
                        if next.len() == 1 {
                            format!("{:?} (the only move)", next[0].action)
                        } else if next_actor == actor {
                            let d = game.randomness().decision(actor, counts[actor]);
                            let mut rng = StdRng::seed_from_u64(d.search_seed);
                            let pick = shadows[actor].decision_fn(&mut rng, &side.observation(actor), &next);
                            format!("{:?} (of {} moves)", pick.action, next.len())
                        } else {
                            "the opponent moves next".to_string()
                        }
                    });
                    shadow = Some((km, clocks, target));
                }
            }
            let chosen = game.play_tick();
            format!("{:?}", chosen).hash(&mut moves);
            if let Some((km, ((kta_mine, kta_theirs), (km_mine, km_theirs)), target)) = shadow {
                if format!("{:?}", km.action) != format!("{:?}", chosen.action) {
                    first[actor] = Some(serde_json::json!({
                        "tick": tick, "turn": state.turn_count, "deck": names[seat_deck[actor]],
                        "kta3": format!("{:?}", chosen.action), "km3": format!("{:?}", km.action),
                        "stadium": state.get_active_stadium_name(),
                        "own_active": active(&state, actor), "opp_active": active(&state, 1 - actor),
                        "own_tools": tools(&state, actor), "opp_tools": tools(&state, 1 - actor), "km3_next": target,
                        "clocks": {"kta": {"mine": kta_mine, "theirs": kta_theirs}, "km": {"mine": km_mine, "theirs": km_theirs}},
                        "before": history[history.len().saturating_sub(8)..].to_vec(),
                    }));
                }
            }
            history.push(format!("seat {} turn {}: {:?}", chosen.actor, state.turn_count, chosen.action));
            tick += 1;
        }
        let by_deck = |d: usize| first[seat_deck.iter().position(|&x| x == d).unwrap()].clone();
        println!(
            "{}",
            serde_json::json!({
                "pairing": pairing, "i": i, "seed": seed, "first_seat": first_seat,
                "moves": format!("{:016x}", moves.finish()), "ticks": tick,
                "first_diff_altaria": by_deck(0), "first_diff_suicune": by_deck(1),
            })
        );
    }
}
