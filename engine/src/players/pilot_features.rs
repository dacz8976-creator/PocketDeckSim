//! The planning pilot's data (branch claude/planning-pilot-data, Oct 2; rl/results/planning_pilot_data_2026-10-02/README.md):
//! the features of a position from one side's view, for fitting an evaluation. Read-only: nothing here changes an
//! evaluation and no player calls it; only `engine/examples/pilot_data.rs` does. It is a child module of `value_functions.rs`
//! (declared there by one `#[path]` line) so that it reads km's terms from the same private functions km's evaluation
//! calls, with km's flags ([`EvalFeatures::KM`]) and weights ([`ValueFunctionParams::baseline`]).
//!
//! [`pilot_features`] returns named values in a fixed order: km's terms for each side, km's clock in parts, and the
//! candidates (Bench and Active Energy and readiness, by evolution too, points at risk, context). [`km_total`] adds km's
//! terms up as `parametric_value_function_ex6` does for km, so a caller can check it against
//! [`public_clock_effect_km_value_function`].
use super::*;
use crate::card_ids::CardId;
use std::cell::RefCell;
use std::collections::HashMap;
use std::sync::OnceLock;
use strum::IntoEnumIterator;

/// km's call of `parametric_value_function_ex6`: public_eval, value_aware, clock_aware, effect_aware, reserve_aware.
const KM_CALL: (bool, bool, bool, bool, bool) = (true, false, true, true, false);
const SIDES: [&str; 2] = ["my", "opp"];

/// One row's named features, in a fixed order (the same names for every state).
pub type Row = Vec<(String, f64)>;

/// km's value for `myself` term by term, the way `parametric_value_function_ex6` adds it up for km, pushed into `out`, and
/// the total. A finished game is not a decision point; it is given km's outcome utility and no terms.
fn km_terms(state: &State, myself: usize, out: &mut Row) -> f64 {
    let params = ValueFunctionParams::baseline();
    let features = EvalFeatures::KM;
    let (public_eval, value_aware, clock_aware, effect_aware, reserve_aware) = KM_CALL;
    let opponent = (myself + 1) % 2;
    let mut push = |name: &str, v: f64| out.push((name.to_string(), v));
    let names = [
        "points", "pokemon_value", "hand_size", "deck_size", "active_retreat_cost", "online_pokemon_count",
        "energy_distance_to_online", "active_online_score", "active_safety", "active_has_tool", "is_winner",
        "turns_until_opponent_wins", "discard_size", "fuel_credit",
    ];
    let clock_names = ["lead", "active_hp", "first_hit", "later_hit", "rest", "threat_slot"];
    if state.setup_opponent_hidden {
        // The setup evaluation: own development terms only, and the opening-Active term (koa's switch A).
        let pokemon_value = calculate_pokemon_value(state, myself, 1.0);
        let (online, distance) = calculate_online_metrics(state, myself, 1.0);
        let hand = state.hands[myself].len() as f64;
        let deck = state.decks[myself].cards.len() as f64;
        let retreat = get_active_retreat_cost(state, myself, public_eval) as f64;
        let active_online = calculate_active_pokemon_online_score_ex(state, myself, false, false, false, None, false);
        let safety = calculate_active_safety(state, myself);
        let setup_score = pokemon_value * params.pokemon_value + hand * params.hand_size - deck * params.deck_size
            - retreat * params.active_retreat_cost
            + active_online * params.active_pokemon_online_score
            + safety * params.active_safety
            + online * params.online_pokemon_count
            + distance * params.energy_distance_to_online;
        let opening = crate::players::opening_class::opening_active_term(
            state,
            myself,
            features.opening_first_turn_active,
            features.opening_bench_working,
            features.opening_readiness,
        );
        let mine = [
            state.points[myself] as f64, pokemon_value, hand, deck, retreat, online, distance, active_online, safety,
            0.0, 0.0, 0.0, state.discard_piles[myself].len() as f64, 0.0,
        ];
        for (side, values) in SIDES.iter().zip([mine, [0.0; 14]]) {
            for (name, v) in names.iter().zip(values) {
                push(&format!("{side}_{name}"), v);
            }
        }
        push("opening_term", opening);
        for side in SIDES {
            for name in clock_names {
                push(&format!("{side}_clock_{name}"), 0.0);
            }
        }
        return setup_score + opening;
    }
    // kt's clocks with km's flags (switch 1 and N2; no counter cut), as `kt_clocks` gives them for km.
    let (cuts, n2) = (features.defender_cuts, features.stadium_bonus_in_clock);
    let mine_clock = kt_clock_stadium(state, myself, false, effect_aware, reserve_aware, public_eval, cuts, n2);
    let theirs_clock = kt_clock_stadium(state, opponent, public_eval, effect_aware, reserve_aware, public_eval, cuts, n2);
    debug_assert!(!features.counter_damage);
    let clocks = (mine_clock.total(0.0), theirs_clock.total(0.0));
    let (my, opp) = (
        extract_features(
            state, myself, 1.0, false, value_aware, clock_aware, effect_aware, reserve_aware, public_eval,
            features.next_attack_reduction, features.defender_modifiers, None, None, Some(clocks.0),
            features.evolution_steps, features.zone_to_bench,
        ),
        extract_features(
            state, opponent, 1.0, public_eval, value_aware, clock_aware, effect_aware, reserve_aware, public_eval,
            features.next_attack_reduction, features.defender_modifiers, None, None, Some(clocks.1),
            features.evolution_steps, features.zone_to_bench,
        ),
    );
    let active_has_tool_weight = if features.tool_by_holder { 0.0 } else { params.active_has_tool };
    let score = (my.points - opp.points) * params.points
        + (my.pokemon_value - opp.pokemon_value) * params.pokemon_value
        + (my.hand_size - opp.hand_size) * params.hand_size
        + (opp.deck_size - my.deck_size) * params.deck_size
        + (-my.active_retreat_cost) * params.active_retreat_cost
        + (my.active_pokemon_online_score - opp.active_pokemon_online_score) * params.active_pokemon_online_score
        + (my.active_safety - opp.active_safety) * params.active_safety
        + (my.active_has_tool - opp.active_has_tool) * active_has_tool_weight
        + (my.is_winner - opp.is_winner) * params.is_winner
        + (my.turns_until_opponent_wins - opp.turns_until_opponent_wins) * params.turns_until_opponent_wins
        + (my.online_pokemon_count - opp.online_pokemon_count) * params.online_pokemon_count
        + (my.energy_distance_to_online - opp.energy_distance_to_online) * params.energy_distance_to_online
        + opp.discard_size * params.opponent_discard_size;
    // Part F (kog's): km's projection is off, so each side's whole discard pile.
    let (my_fuel, opp_fuel) = if features.fuel_credit {
        (
            crate::players::fuel_credit::fuel_credit(state, myself, true, &state.discard_energies[myself].clone()),
            crate::players::fuel_credit::fuel_credit(state, opponent, false, &state.discard_energies[opponent].clone()),
        )
    } else {
        (0.0, 0.0)
    };
    let score = score + (my_fuel - opp_fuel) * params.pokemon_value;
    debug_assert!(features.bench_attacker_weight == 0.0);
    for (side, f, fuel) in [("my", &my, my_fuel), ("opp", &opp, opp_fuel)] {
        let values = [
            f.points, f.pokemon_value, f.hand_size, f.deck_size, f.active_retreat_cost, f.online_pokemon_count,
            f.energy_distance_to_online, f.active_pokemon_online_score, f.active_safety, f.active_has_tool,
            f.is_winner, f.turns_until_opponent_wins, f.discard_size, fuel,
        ];
        for (name, v) in names.iter().zip(values) {
            push(&format!("{side}_{name}"), v);
        }
    }
    push("opening_term", 0.0);
    for (side, clock) in [("my", &mine_clock), ("opp", &theirs_clock)] {
        let (hp, first, later) = clock.active.unwrap_or((0.0, 0.0, 0.0));
        let values = [clock.lead, hp, first, later, clock.rest, clock.threat_slot.map_or(-1.0, |s| s as f64)];
        for (name, v) in clock_names.iter().zip(values) {
            push(&format!("{side}_clock_{name}"), if v.is_finite() { v } else { 30.0 });
        }
    }
    score
}

/// km's value for `myself`, added up from its terms (see [`km_terms`]); equal to
/// [`public_clock_effect_km_value_function`] on any state that is not a finished game.
pub fn km_total(state: &State, myself: usize) -> f64 {
    km_terms(state, myself, &mut Vec::new())
}

/// Every card in the pool, for the opponent's evolutions (their deck is hidden; the card pool is public).
fn card_pool() -> &'static Vec<Card> {
    static POOL: OnceLock<Vec<Card>> = OnceLock::new();
    POOL.get_or_init(|| CardId::iter().map(crate::database::get_card_by_enum).collect())
}

thread_local! {
    static POOL_EVOLUTIONS: RefCell<HashMap<String, Vec<Card>>> = RefCell::new(HashMap::new());
}

/// What `pokemon` can still evolve into (the highest evolutions, not the card itself): for the mover, from its deck and
/// hand, as km's clock reads them; for the opponent, from the card pool.
fn evolution_forms(state: &State, owner: usize, mover: usize, pokemon: &PlayedCard) -> Vec<Card> {
    let forms = if owner == mover {
        evolution_targets(state, owner, pokemon)
    } else {
        let id = pokemon.card.get_id();
        POOL_EVOLUTIONS.with(|cache| {
            cache.borrow_mut().entry(id).or_insert_with(|| get_highest_evolutions(&pokemon.card, card_pool())).clone()
        })
    };
    forms.into_iter().filter(|form| form.get_id() != pokemon.card.get_id()).collect()
}

/// The Energy `pokemon` (or `pokemon` evolved into `form`, with its Energy) still misses for each attack, with the attack's
/// printed damage: (missing, damage, cost).
fn attack_needs(state: &State, owner: usize, pokemon: &PlayedCard, form: Option<&Card>) -> Vec<(usize, u32, usize)> {
    let mut slot = pokemon.clone();
    if let Some(form) = form {
        slot.card = form.clone();
    }
    slot.card
        .get_attacks()
        .iter()
        .map(|atk| (energy_missing(&slot, &atk.energy_required, state, owner).len(), atk.fixed_damage, atk.energy_required.len()))
        .collect()
}

/// (missing to the cheapest attack, missing to the priciest, best damage), over `needs`; -1, -1, 0 without an attack.
fn summary(needs: &[(usize, u32, usize)]) -> (f64, f64, f64) {
    let cheapest = needs.iter().min_by_key(|(_, _, cost)| *cost);
    let priciest = needs.iter().max_by_key(|(_, _, cost)| *cost);
    let best = needs.iter().map(|(_, dmg, _)| *dmg).max().unwrap_or(0);
    (
        cheapest.map_or(-1.0, |(m, _, _)| *m as f64),
        priciest.map_or(-1.0, |(m, _, _)| *m as f64),
        best as f64,
    )
}

/// One in-play Pokemon's candidate features: (Energy, missing to cheapest, missing to priciest, evolution forms (0/1),
/// evolution's missing to cheapest, to priciest (min over forms; -1 without), best damage own or by evolution, and the
/// missing Energy to the attack that does it).
fn slot_features(state: &State, owner: usize, mover: usize, pokemon: &PlayedCard) -> [f64; 8] {
    let own = attack_needs(state, owner, pokemon, None);
    let (cheap, pricey, own_best) = summary(&own);
    let forms = evolution_forms(state, owner, mover, pokemon);
    let (mut evo_cheap, mut evo_pricey, mut best, mut best_missing) = (-1.0f64, -1.0f64, own_best, -1.0f64);
    if own_best > 0.0 {
        best_missing = own.iter().filter(|(_, d, _)| *d as f64 == own_best).map(|(m, _, _)| *m).min().unwrap() as f64;
    }
    for form in &forms {
        let needs = attack_needs(state, owner, pokemon, Some(form));
        let (c, p, b) = summary(&needs);
        evo_cheap = if evo_cheap < 0.0 { c } else { evo_cheap.min(c) };
        evo_pricey = if evo_pricey < 0.0 { p } else { evo_pricey.min(p) };
        if b > best {
            best = b;
            best_missing = needs.iter().filter(|(_, d, _)| *d as f64 == b).map(|(m, _, _)| *m).min().unwrap() as f64;
        }
    }
    [
        pokemon.attached_energy.len() as f64,
        cheap,
        pricey,
        (!forms.is_empty()) as u8 as f64,
        evo_cheap,
        evo_pricey,
        best,
        best_missing,
    ]
}

/// The candidates for one side (`owner`) from the mover's view (`mover`), pushed into `out` with the side's prefix.
fn candidates(state: &State, owner: usize, mover: usize, out: &mut Row) {
    let side = if owner == mover { "my" } else { "opp" };
    let mut push = |name: &str, v: f64| out.push((format!("{side}_{name}"), v));
    // The Bench, slot by slot, and over all of it.
    let (mut count, mut energy_total, mut min_missing, mut ready) = (0.0, 0.0, -1.0f64, 0.0);
    let mut attacker: Option<(f64, f64, f64)> = None; // (damage, Energy, missing)
    for slot in 1..4 {
        let pokemon = state.in_play_pokemon[owner][slot].as_ref();
        let f = pokemon.map(|p| slot_features(state, owner, mover, p));
        push(&format!("bench{slot}_present"), pokemon.is_some() as u8 as f64);
        push(&format!("bench{slot}_hp"), pokemon.map_or(0.0, |p| p.get_remaining_hp() as f64));
        let names = ["energy", "missing_cheapest", "missing_priciest", "has_evolution", "evo_missing_cheapest",
                     "evo_missing_priciest", "best_damage"];
        for (k, name) in names.iter().enumerate() {
            push(&format!("bench{slot}_{name}"), f.map_or(if k == 0 || k == 3 || k == 6 { 0.0 } else { -1.0 }, |f| f[k]));
        }
        if let (Some(p), Some(f)) = (pokemon, f) {
            count += 1.0;
            energy_total += f[0];
            let own_ready = attack_needs(state, owner, p, None).iter().any(|(m, d, _)| *m == 0 && *d > 0);
            ready += own_ready as u8 as f64;
            for m in [f[1], f[4]] {
                if m >= 0.0 && (min_missing < 0.0 || m < min_missing) {
                    min_missing = m;
                }
            }
            if attacker.map_or(true, |(d, _, _)| f[6] > d) {
                attacker = Some((f[6], f[0], f[7]));
            }
        }
    }
    push("bench_count", count);
    push("bench_energy_total", energy_total);
    push("bench_min_missing", min_missing);
    push("bench_ready", ready);
    let (damage, energy, missing) = attacker.unwrap_or((0.0, 0.0, -1.0));
    push("bench_attacker_energy", energy);
    push("bench_attacker_missing", missing);
    push("bench_attacker_damage", damage);
    // The Active.
    let active = state.in_play_pokemon[owner][0].as_ref();
    let f = active.map(|p| slot_features(state, owner, mover, p));
    let names = ["active_energy", "active_missing_cheapest", "active_missing_priciest", "active_has_evolution",
                 "active_evo_missing_cheapest", "active_evo_missing_priciest", "active_best_damage"];
    for (k, name) in names.iter().enumerate() {
        push(name, f.map_or(if k == 0 || k == 3 || k == 6 { 0.0 } else { -1.0 }, |f| f[k]));
    }
    push("active_hp", active.map_or(0.0, |p| p.get_remaining_hp() as f64));
    // Whether the Active can attack on the side's next attacking turn (this one, if the side is to move and hasn't
    // attacked) and on the one after: its fewest missing Energy for a damaging attack against the Energy attachable by then
    // (km's own turn arithmetic, `owner_next_turn`), and no Special Condition stopping it. The Zone Energy's type is not read.
    let (_, attach_next) = owner_next_turn(state, owner);
    let (turn0, turn1) = match active {
        Some(p) => {
            let fewest = attack_needs(state, owner, p, None).iter().filter(|(_, d, _)| *d > 0).map(|(m, _, _)| *m).min();
            let free = !special_condition_blocks_attack_or_retreat(p);
            match fewest {
                Some(m) => ((free && m <= attach_next) as u8 as f64, (m <= attach_next + 1) as u8 as f64),
                None => (0.0, 0.0),
            }
        }
        None => (0.0, 0.0),
    };
    push("active_can_attack_turn0", turn0);
    push("active_can_attack_turn1", turn1);
    let risk = active.map_or(0.0, |p| p.card.get_knockout_points() as f64);
    push("active_points_at_risk", risk);
    let other = (owner + 1) % 2;
    push("active_ko_ends_game", (risk > 0.0 && state.points[other] as f64 + risk >= 3.0) as u8 as f64);
    push("attach_now", (owner_to_move_now(state, owner) && state.energy_zone[owner].current.is_some()) as u8 as f64);
}

/// The features of `state` from `mover`'s view, in a fixed order: `state` must be what the mover sees (the caller builds
/// it with `PlayerObservation::search_state`, as km's own decision does). `went_first` is the caller's (the game's first
/// turn is not in the state).
pub fn pilot_features(state: &State, mover: usize, went_first: bool) -> Row {
    let mut out: Row = Vec::with_capacity(160);
    out.push(("turn".to_string(), state.turn_count as f64));
    out.push(("went_first".to_string(), went_first as u8 as f64));
    out.push(("setup".to_string(), state.setup_opponent_hidden as u8 as f64));
    let total = km_terms(state, mover, &mut out);
    out.push(("km_value".to_string(), total));
    candidates(state, mover, mover, &mut out);
    candidates(state, (mover + 1) % 2, mover, &mut out);
    out
}
