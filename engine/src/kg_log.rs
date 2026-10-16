//! ky3 item 7's logger (print-only: it plays a game tick by tick and records, it never chooses). `play_logged` takes a built `Game`
//! and the seat that holds the deck under study, and returns one JSON record: for every real decision (more than one legal move) both
//! boards, both hands, the full legal list, the move played, the own-knockout counts and, for a play-out pilot, the switch note
//! (km's move, the move played and whether the pilot changed it); and every knockout with its cause, the points it paid and the
//! Glimmora-style coin. The own-knockout count is read through the state's serde JSON, as the pause-games harness does, because the
//! field itself is crate-private.
//!
//! A knockout is read off two states one tick apart: a slot that held a Pokémon and is empty, on a seat whose count went up. Ilima's
//! return, a retreat or a Gust leave a slot empty or change it with the count unchanged, so they are never knockouts.
use serde_json::{json, Value};

use crate::actions::abilities::AbilityMechanic;
use crate::actions::get_in_play_ability_mechanic;
use crate::actions::{Action, SimpleAction};
use crate::models::Card;
use crate::players::playout_player::take_switch_note;
use crate::state::PlayedCard;
use crate::{Game, State};

/// A compact name for an action (the same spelling as the strength harness's labels).
pub fn label(a: &Action) -> String {
    let nm = |c: &Card| c.get_name();
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play:{}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Place:{}@{}", nm(card), idx),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve:{}@{}", nm(evolution), in_play_idx),
        SimpleAction::UseAbility { in_play_idx } => format!("Ability@{}", in_play_idx),
        SimpleAction::Attack(at) => format!("Attack:{}", at.title),
        SimpleAction::Retreat(i) => format!("Retreat:{}", i),
        SimpleAction::Attach { attachments, is_turn_energy } => format!(
            "Attach:{}{}",
            attachments.iter().map(|(n, e, i)| format!("{}{:?}@{}", n, e, i)).collect::<Vec<_>>().join("+"),
            if *is_turn_energy { " zone" } else { " fx" }
        ),
        SimpleAction::AttachTool { in_play_idx, tool_card } => format!("Tool:{}@{}", nm(tool_card), in_play_idx),
        SimpleAction::Heal { in_play_idx, amount, .. } => format!("Heal:{}@{}", amount, in_play_idx),
        SimpleAction::Activate { player, in_play_idx } => format!("Activate:{}@{}", player, in_play_idx),
        SimpleAction::Promote { player, in_play_idx } => format!("Promote:{}@{}", player, in_play_idx),
        SimpleAction::ChooseMistyTarget { in_play_idx } => format!("MistyTarget@{}", in_play_idx),
        SimpleAction::ChooseRetreatEnergy { to_in_play_idx, .. } => format!("RetreatPay:{}", to_in_play_idx),
        SimpleAction::EndTurn => "EndTurn".to_string(),
        other => format!("{:?}", other).split(|c: char| c == ' ' || c == '{' || c == '(').next().unwrap_or("?").to_string(),
    }
}

/// Each player's own-knockout count (indexed by the player who LOST the Pokémon), read through the state's JSON.
pub fn own_knockouts(state: &State) -> [u32; 2] {
    let v = serde_json::to_value(state).expect("a state serializes");
    let at = |i: usize| v["own_knockouts_this_game"][i].as_u64().unwrap_or(0) as u32;
    [at(0), at(1)]
}

fn slot_json(p: &Option<PlayedCard>) -> Value {
    match p {
        None => Value::Null,
        Some(p) => json!({
            "n": p.card.get_name(),
            "hp": p.get_remaining_hp(),
            "e": p.attached_energy.iter().map(|e| format!("{:?}", e)).collect::<Vec<_>>(),
            "tools": p.attached_tools.iter().map(|t| t.get_name()).collect::<Vec<_>>(),
        }),
    }
}

fn board_json(state: &State, seat: usize) -> Value {
    Value::Array(state.in_play_pokemon[seat].iter().map(slot_json).collect())
}

fn hand_json(state: &State, seat: usize) -> Value {
    Value::Array(state.hands[seat].iter().map(|c| Value::String(c.get_name())).collect())
}

/// The knockouts between two states one tick apart. `cause` is the label of the action that was applied; `actor` the seat that applied
/// it. `points_gained` is what the other side's score rose by in the tick (shared when two Pokémon of a seat fall together), and
/// `denied` is true when a victim whose live ability flips the point-denial coin was paid less than its knockout points.
pub fn ko_events(before: &State, after: &State, actor: usize, cause: &str) -> Vec<Value> {
    let (kb, ka) = (own_knockouts(before), own_knockouts(after));
    let mut out = Vec::new();
    for seat in 0..2 {
        if ka[seat] <= kb[seat] {
            continue;
        }
        let victims: Vec<usize> = (0..4).filter(|&i| before.in_play_pokemon[seat][i].is_some() && after.in_play_pokemon[seat][i].is_none()).collect();
        let total_points: u32 = victims.iter().map(|&i| before.in_play_pokemon[seat][i].as_ref().unwrap().card.get_knockout_points() as u32).sum();
        let gained = after.points[1 - seat].saturating_sub(before.points[1 - seat]) as u32;
        let any_coin = victims.iter().any(|&i| coin_ability(before, before.in_play_pokemon[seat][i].as_ref().unwrap()));
        for &i in &victims {
            let p = before.in_play_pokemon[seat][i].as_ref().unwrap();
            let coin = coin_ability(before, p);
            out.push(json!({
                "victim_seat": seat,
                "victim": p.card.get_name(),
                "slot": i,
                "ko_points": p.card.get_knockout_points(),
                "coin_ability": coin,
                "points_gained": gained,
                "denied": coin && any_coin && gained < total_points,
                "cause": cause,
                "actor": actor,
                "turn": before.turn_count,
                "count_after": ka[seat],
            }));
        }
    }
    out
}

fn coin_ability(state: &State, p: &PlayedCard) -> bool {
    matches!(get_in_play_ability_mechanic(state, p), Some(AbilityMechanic::CoinFlipToDenyKnockoutPoints))
}

/// Plays `game` to its end, logging every decision. `deck_seat` is the seat of the deck under study (deck 01); the record carries it so
/// the analysis indexes the counts by that seat and never assumes seat 0.
pub fn play_logged(game: &mut Game, deck_seat: usize) -> Value {
    let first = game.get_state_clone().current_player;
    let mut decisions: Vec<Value> = Vec::new();
    let mut kos: Vec<Value> = Vec::new();
    let mut own_turn = [0u32; 2];
    let mut last_turn = 0u8;
    let _ = take_switch_note();
    while !game.is_game_over() {
        let before = game.get_state_clone();
        let (actor, mut legal) = before.generate_possible_actions();
        crate::observation::canonical_actions(&mut legal);
        if before.turn_count != last_turn {
            last_turn = before.turn_count;
            own_turn[before.current_player] += 1;
        }
        let _ = take_switch_note();
        let played = game.play_tick();
        let after = game.get_state_clone();
        let cause = label(&played);
        if legal.len() > 1 {
            let note = take_switch_note();
            decisions.push(json!({
                "turn": before.turn_count,
                "own_turn": own_turn[actor],
                "actor": actor,
                "legal": legal.iter().map(label).collect::<Vec<_>>(),
                "chosen": cause,
                "switch": note.map(|n| json!({"km": n.km, "chosen": n.chosen, "changed": n.changed, "by": if n.changed { "playout" } else { "km" }})),
                "boards": [board_json(&before, 0), board_json(&before, 1)],
                "hands": [hand_json(&before, 0), hand_json(&before, 1)],
                "points": before.points,
                "own_kos": own_knockouts(&before),
            }));
        }
        kos.extend(ko_events(&before, &after, actor, &cause));
    }
    let end = game.get_state_clone();
    let winner = match end.winner {
        Some(crate::state::GameOutcome::Win(s)) => s as i64,
        _ => -1,
    };
    json!({
        "deck_seat": deck_seat,
        "first": first,
        "winner": winner,
        "turns": end.turn_count,
        "points": end.points,
        "own_kos_final": own_knockouts(&end),
        "decisions": decisions,
        "kos": kos,
    })
}
