// Collection of value functions for ExpectiMiniMaxPlayer
//
// Each value function evaluates a game state from a player's perspective
// and returns a score (higher is better for that player)

use log::trace;

use crate::card_logic::get_highest_evolutions;
use crate::hooks::energy_missing;
use crate::models::{Card, EnergyType, PlayedCard};
use crate::state::GameOutcome;
use crate::State;

/// Coefficients for the parametric value function
#[derive(Debug, Clone, Copy)]
pub struct ValueFunctionParams {
    pub points: f64,
    pub pokemon_value: f64,
    pub hand_size: f64,
    pub deck_size: f64,
    pub active_retreat_cost: f64,
    pub active_pokemon_online_score: f64,
    pub active_safety: f64,
    pub active_has_tool: f64,
    pub is_winner: f64,
    pub turns_until_opponent_wins: f64,
    pub online_pokemon_count: f64,
    pub energy_distance_to_online: f64,
    pub opponent_discard_size: f64,
}

impl ValueFunctionParams {
    /// Baseline parameters (same as original baseline function)
    pub const fn baseline() -> Self {
        Self {
            points: 10_000.0,
            pokemon_value: 1.0,
            hand_size: 1.0,
            deck_size: 1.0,
            active_retreat_cost: 1.0,
            active_pokemon_online_score: 500.0,
            active_safety: 1.0,
            active_has_tool: 10.0,
            is_winner: 100_000.0,
            turns_until_opponent_wins: 100.0,
            online_pokemon_count: 0.0,
            energy_distance_to_online: 0.0,
            opponent_discard_size: 0.1,
        }
    }

    /// Variant parameters
    pub const fn variant() -> Self {
        Self {
            points: 10_000.0,
            pokemon_value: 1.0,
            hand_size: 1.0,
            deck_size: 1.0,
            active_retreat_cost: 1.0,
            active_pokemon_online_score: 500.0,
            active_safety: 1.0,
            active_has_tool: 10.0,
            is_winner: 100_000.0,
            turns_until_opponent_wins: 100.0,
            online_pokemon_count: 0.0,
            energy_distance_to_online: 0.0,
            opponent_discard_size: 0.1,
        }
    }
}

pub fn baseline_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function(state, myself, &ValueFunctionParams::baseline())
}

/// Hidden-information-respecting variant of [`baseline_value_function`]. (§40)
///
/// The baseline function computes the OPPONENT's `active_pokemon_online_score` by scanning
/// the opponent's deck and hand for evolutions of their Active. That is information a real
/// player cannot see, it is weighted 500.0, and it is measured at a 125-point evaluation
/// swing on a 116-point baseline with deck size and hand size held constant — see
/// `tests/value_function_hidden_info_test.rs`.
///
/// This version evaluates the opponent's Active as the card actually ON THE BOARD, and is
/// otherwise identical. The player's own zones are still read in full, because a player may
/// legitimately see their own deck and hand.
pub fn public_baseline_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex(state, myself, &ValueFunctionParams::baseline(), true)
}

/// §115 — the `d` tier. [`public_baseline_value_function`] with ONE substitution: the
/// Pokémon term is [`calculate_pokemon_value_damage_aware`] instead of
/// [`calculate_pokemon_value`]. Everything else is identical, so `p<N>` vs `d<N>`
/// isolates the leaf evaluation of the board.
///
/// Motivation (§113): `calculate_pokemon_value` scores a Pokémon as
/// `remaining_HP × (relevant_energy + 1)` and never reads attack damage, so an undamaged
/// Bulbasaur (70 HP, 2-energy attack) outscores the Ivysaur it evolves into (100 HP,
/// 1-energy utility attack) 210 to 200 — evolution is priced as a downgrade and setup
/// decks never assemble (0 evolutions in 240 logged games; p3/p4/p5 identical, so it is
/// the leaf, not the depth).
pub fn public_damage_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function_ex2(state, myself, &ValueFunctionParams::baseline(), true, true)
}

/// A variant of the baseline value function
pub fn variant_value_function(state: &State, myself: usize) -> f64 {
    parametric_value_function(state, myself, &ValueFunctionParams::variant())
}

/// Parametric value function that uses the provided coefficients.
///
/// Preserved bit-for-bit: it reads the opponent's hidden zones, as it always has. Callers
/// that want the hidden-information-respecting behaviour use
/// [`parametric_value_function_ex`] with `public_eval = true`.
pub fn parametric_value_function(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
) -> f64 {
    parametric_value_function_ex(state, myself, params, false)
}

/// [`parametric_value_function`], plus a switch for whether the OPPONENT's hidden zones
/// (deck and hand CONTENTS) may be read when scoring how "online" their Active is. (§40)
///
/// `public_eval = false` reproduces the historical behaviour exactly. `public_eval = true`
/// restricts the opponent's evaluation to public information.
pub fn parametric_value_function_ex(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
) -> f64 {
    parametric_value_function_ex2(state, myself, params, public_eval, false)
}

/// [`parametric_value_function_ex`], plus the §115 `damage_aware` switch. `false`
/// reproduces the historical behaviour bit-for-bit (the branch selects the same
/// [`calculate_pokemon_value`] call); `true` swaps in the damage/development-aware
/// Pokémon term used by the `d` tier.
pub fn parametric_value_function_ex2(
    state: &State,
    myself: usize,
    params: &ValueFunctionParams,
    public_eval: bool,
    damage_aware: bool,
) -> f64 {
    let opponent = (myself + 1) % 2;
    let (my, opp) = (
        extract_features(state, myself, 1.0, false, damage_aware),
        extract_features(state, opponent, 1.0, public_eval, damage_aware),
    );
    let score = (my.points - opp.points) * params.points
        + (my.pokemon_value - opp.pokemon_value) * params.pokemon_value
        + (my.hand_size - opp.hand_size) * params.hand_size
        + (opp.deck_size - my.deck_size) * params.deck_size
        + (-my.active_retreat_cost) * params.active_retreat_cost
        + (my.active_pokemon_online_score - opp.active_pokemon_online_score)
            * params.active_pokemon_online_score
        + (my.active_safety - opp.active_safety) * params.active_safety
        + (my.active_has_tool - opp.active_has_tool) * params.active_has_tool
        + (my.is_winner - opp.is_winner) * params.is_winner
        + (my.turns_until_opponent_wins - opp.turns_until_opponent_wins)
            * params.turns_until_opponent_wins
        + (my.online_pokemon_count - opp.online_pokemon_count) * params.online_pokemon_count
        + (my.energy_distance_to_online - opp.energy_distance_to_online)
            * params.energy_distance_to_online
        + opp.discard_size * params.opponent_discard_size;
    trace!("parametric_value_function: {score} (params: {params:?}, my: {my:?}, opp: {opp:?})");
    score
}

/// Features extracted from a player's game state
#[derive(Debug)]
struct Features {
    points: f64,
    pokemon_value: f64,
    hand_size: f64,
    deck_size: f64,
    active_retreat_cost: f64,
    online_pokemon_count: f64,
    energy_distance_to_online: f64,
    active_pokemon_online_score: f64,
    active_safety: f64,
    active_has_tool: f64,
    is_winner: f64,
    turns_until_opponent_wins: f64,
    discard_size: f64,
}

/// Extract features for a single player.
///
/// `public_only` restricts the extraction to information an opposing player is entitled to
/// see. Today that affects exactly one feature — `active_pokemon_online_score` — because it
/// is the only one that reads deck or hand CONTENTS; `hand_size` and `deck_size` are counts
/// and are public. (§40)
fn extract_features(
    state: &State,
    player: usize,
    active_factor: f64,
    public_only: bool,
    damage_aware: bool,
) -> Features {
    let points = state.points[player] as f64;
    let pokemon_value = if damage_aware {
        calculate_pokemon_value_damage_aware(state, player, active_factor, public_only)
    } else {
        calculate_pokemon_value(state, player, active_factor)
    };
    let hand_size = state.hands[player].len() as f64;
    let deck_size = state.decks[player].cards.len() as f64;
    let active_retreat_cost = get_active_retreat_cost(state, player) as f64;
    let (online_pokemon_count, energy_distance_to_online) =
        calculate_online_metrics(state, player, active_factor);
    let active_pokemon_online_score =
        calculate_active_pokemon_online_score(state, player, public_only);
    let active_safety = calculate_active_safety(state, player);
    let active_has_tool = get_active_has_tool(state, player);
    let is_winner = check_is_winner(state, player);
    // §115: in the d path the threat scan is evolution-aware. `public_only` doubles as the
    // zone-read permission: it is true exactly when `player` is the OPPONENT of the
    // evaluating player, i.e. when the side being SCANNED for threats ((player+1)%2) is the
    // evaluating player themselves — whose deck and hand they may legitimately see.
    let turns_until_opponent_wins = if damage_aware {
        calculate_turns_until_opponent_wins_damage_aware(state, player, public_only)
    } else {
        calculate_turns_until_opponent_wins(state, player)
    };
    let discard_size = state.discard_piles[player].len() as f64;

    Features {
        points,
        pokemon_value,
        hand_size,
        deck_size,
        active_retreat_cost,
        online_pokemon_count,
        energy_distance_to_online,
        active_pokemon_online_score,
        active_safety,
        active_has_tool,
        is_winner,
        turns_until_opponent_wins,
        discard_size,
    }
}

fn get_active_retreat_cost(state: &State, player: usize) -> usize {
    state
        .maybe_get_active(player)
        .map(|card| card.card.get_retreat_cost().map(|rc| rc.len()).unwrap_or(5))
        .unwrap_or(0)
}

/// Check if active pokemon has a tool attached
fn get_active_has_tool(state: &State, player: usize) -> f64 {
    state
        .maybe_get_active(player)
        .map(|card| if card.has_tool_attached() { 1.0 } else { 0.0 })
        .unwrap_or(0.0)
}

/// Check if the player has won the game
fn check_is_winner(state: &State, player: usize) -> f64 {
    match state.winner {
        Some(GameOutcome::Win(winner)) if winner == player => 1.0,
        _ => 0.0,
    }
}

/// Calculate expected turns until opponent wins
/// Uses opponent's active damage and simulates KOs until opponent reaches 3 points
fn calculate_turns_until_opponent_wins(state: &State, player: usize) -> f64 {
    let opponent = (player + 1) % 2;

    // Find the closest pokemon to being able to deal damage (by energy requirements)
    let best_threat = state
        .enumerate_in_play_pokemon(opponent)
        .filter_map(|(_, pokemon)| {
            let best_attack = pokemon
                .card
                .get_attacks()
                .iter()
                .filter(|atk| atk.fixed_damage > 0) // Only consider attacks that deal damage
                .map(|atk| {
                    let missing = energy_missing(pokemon, &atk.energy_required, state, opponent);
                    (atk.fixed_damage, missing.len())
                })
                .min_by_key(|(damage, missing)| (*missing, u32::MAX - damage)); // Prioritize by missing energy, then by damage

            best_attack
        })
        .min_by_key(|(damage, missing)| (*missing, u32::MAX - damage)); // Find pokemon with least missing energy
    let (max_damage, missing_energy) = match best_threat {
        Some((damage, missing)) => (damage as f64, missing),
        None => return 30.0, // No pokemon can deal damage
    };

    let mut total_turns = 0.0;
    let mut opp_points = state.points[opponent];

    // If the best threat still can't attack (missing energy), factor that into the calculation
    total_turns += missing_energy as f64;

    // Calculate turns to KO my active pokemon
    if let Some(my_active) = state.maybe_get_active(player) {
        let turns_to_ko = (my_active.get_remaining_hp() as f64 / max_damage).ceil();
        total_turns += turns_to_ko;
        opp_points += my_active.card.get_knockout_points();
    }

    // Simulate KOing bench pokemon until opponent has 3+ points
    while opp_points < 3 {
        // Find the safest bench pokemon (highest hp / ko_points)
        let safest_bench = state
            .enumerate_bench_pokemon(player)
            .max_by_key(|(_, card)| {
                // if missing 1 point, just do by HP. if missing more than 1 point,
                // do by point yield hp / ko_points
                if opp_points == 2 {
                    card.get_remaining_hp()
                } else {
                    let ko_points = card.card.get_knockout_points().max(1) as u32;
                    card.get_remaining_hp() * 1000 / ko_points
                }
            });

        let Some((_, safest_pokemon)) = safest_bench else {
            break; // No more bench pokemon
        };

        let turns_to_ko = (safest_pokemon.get_remaining_hp() as f64 / max_damage).ceil();
        total_turns += turns_to_ko;
        opp_points += safest_pokemon.card.get_knockout_points();
    }

    total_turns
}

/// §115 — [`calculate_turns_until_opponent_wins`] with the SECOND instance of the §113
/// defect fixed. The original scans only attacks currently on the board and returns a
/// "can never win" sentinel of 30.0 when none deal damage — so evolving into a utility
/// Stage-1 (Ivysaur) zeroes the side's visible threat and the feature swings by thousands
/// of points at coefficient 100. That cliff, not the 10-point Pokémon-term gap, is the
/// bulk of why the pilot refused to evolve.
///
/// Here, when `read_scanned_zones` permits (see the call site: the scanned side is the
/// evaluating player, whose own deck + hand are legitimately visible), each in-play
/// Pokémon also threatens the attacks of its best evolution available in those zones,
/// priced against the energy already on the slot, with each evolution step still to take
/// counted as one more turn — the same unit as missing energy. When the scanned side is
/// the true opponent, the scan stays board-only, preserving §40's leak closure.
fn calculate_turns_until_opponent_wins_damage_aware(
    state: &State,
    player: usize,
    read_scanned_zones: bool,
) -> f64 {
    let opponent = (player + 1) % 2;

    let best_threat = state
        .enumerate_in_play_pokemon(opponent)
        .filter_map(|(_, pokemon)| {
            let mut candidates: Vec<(u32, usize)> = pokemon
                .card
                .get_attacks()
                .iter()
                .filter(|atk| atk.fixed_damage > 0)
                .map(|atk| {
                    let missing = energy_missing(pokemon, &atk.energy_required, state, opponent);
                    (atk.fixed_damage, missing.len())
                })
                .collect();
            if read_scanned_zones {
                if let Card::Pokemon(current) = &pokemon.card {
                    let mut available: Vec<Card> = state.decks[opponent].cards.to_vec();
                    available.extend(state.hands[opponent].iter().cloned());
                    for target in get_highest_evolutions(&pokemon.card, &available) {
                        let Card::Pokemon(t) = &target else { continue };
                        let steps = t.stage.saturating_sub(current.stage) as usize;
                        if steps == 0 {
                            continue;
                        }
                        for atk in target.get_attacks() {
                            if atk.fixed_damage > 0 {
                                let missing =
                                    energy_missing(pokemon, &atk.energy_required, state, opponent);
                                candidates.push((atk.fixed_damage, missing.len() + steps));
                            }
                        }
                    }
                }
            }
            candidates
                .into_iter()
                .min_by_key(|(damage, missing)| (*missing, u32::MAX - damage))
        })
        .min_by_key(|(damage, missing)| (*missing, u32::MAX - damage));
    let (max_damage, missing_energy) = match best_threat {
        Some((damage, missing)) => (damage as f64, missing),
        None => return 30.0, // No pokemon can deal damage, now or via any available evolution
    };

    let mut total_turns = 0.0;
    let mut opp_points = state.points[opponent];

    total_turns += missing_energy as f64;

    if let Some(my_active) = state.maybe_get_active(player) {
        let turns_to_ko = (my_active.get_remaining_hp() as f64 / max_damage).ceil();
        total_turns += turns_to_ko;
        opp_points += my_active.card.get_knockout_points();
    }

    while opp_points < 3 {
        let safest_bench = state
            .enumerate_bench_pokemon(player)
            .max_by_key(|(_, card)| {
                if opp_points == 2 {
                    card.get_remaining_hp()
                } else {
                    let ko_points = card.card.get_knockout_points().max(1) as u32;
                    card.get_remaining_hp() * 1000 / ko_points
                }
            });

        let Some((_, safest_pokemon)) = safest_bench else {
            break;
        };

        let turns_to_ko = (safest_pokemon.get_remaining_hp() as f64 / max_damage).ceil();
        total_turns += turns_to_ko;
        opp_points += safest_pokemon.card.get_knockout_points();
    }

    total_turns
}

/// Calculate online pokemon metrics: (count of online pokemon, total energy distance to online)
/// A pokemon is "online" if it can use at least one attack
/// Applies active_factor bonus to the active pokemon (position 0)
fn calculate_online_metrics(state: &State, player: usize, active_factor: f64) -> (f64, f64) {
    let (online_count, total_distance) = state
        .enumerate_in_play_pokemon(player)
        .map(|(pos, card)| {
            let min_distance = card
                .card
                .get_attacks()
                .iter()
                .map(|atk| {
                    let missing = energy_missing(card, &atk.energy_required, state, player);
                    missing.len()
                })
                .min()
                .unwrap_or(0);

            let position_factor = if pos == 0 { active_factor } else { 1.0 };

            if min_distance == 0 {
                (position_factor, 0.0) // Online pokemon with position bonus
            } else {
                (0.0, min_distance as f64 * position_factor) // Offline pokemon with weighted distance
            }
        })
        .fold((0.0, 0.0), |(count, dist), (c, d)| (count + c, dist + d));

    (online_count, total_distance)
}

/// Calculate total pokemon value (HP * Energy) for a player
fn calculate_pokemon_value(state: &State, player: usize, active_factor: f64) -> f64 {
    state
        .enumerate_in_play_pokemon(player)
        .map(|(pos, card)| {
            let relevant_energy = get_relevant_energy(state, player, card);
            let hp_energy_product = card.get_remaining_hp() as f64 * (relevant_energy + 1.0);
            if pos == 0 {
                hp_energy_product * active_factor
            } else {
                hp_energy_product
            }
        })
        .sum()
}

/// §115 — the `d` tier's Pokémon term. Scores each Pokémon in play as
///
/// ```text
/// remaining_HP + K_DAMAGE × best_damage_now + evolution_potential
/// ```
///
/// - `best_damage_now`: the best of the card's OWN attacks, each valued at
///   `fixed_damage / (1 + missing_energy)` against the slot's currently attached energy —
///   a ready 40 is worth 40, a 120 missing two energy is worth 40. This is the damage term
///   §113 showed was absent entirely, and because the anchor attack is chosen by DAMAGE it
///   also retires `get_relevant_energy`'s lexicographic-`.max()` quirk in this path.
/// - `evolution_potential`: the best evolution of this card available in the player's own
///   deck + hand, valued the same way (HP net of damage carried, plus its discounted best
///   damage against the energy already on the slot), then discounted by
///   `EVOLUTION_STEP_DISCOUNT^steps`. Each evolution step taken moves value out of the
///   discount and onto the board, so assembling a line is monotonically uphill —
///   Bulbasaur 180 < Ivysaur 240 < Mega Venusaur ex 280 on the §113 whiteboard example
///   that scored 210 > 200 under the old term. Reads the player's OWN hidden zones only;
///   under `public_only` (opponent eval) it contributes 0, preserving §40's leak closure.
fn calculate_pokemon_value_damage_aware(
    state: &State,
    player: usize,
    active_factor: f64,
    public_only: bool,
) -> f64 {
    state
        .enumerate_in_play_pokemon(player)
        .map(|(pos, card)| {
            let value = card.get_remaining_hp() as f64
                + K_DAMAGE * best_attack_value(card, &card.card, state, player)
                + evolution_potential(state, player, card, public_only);
            if pos == 0 {
                value * active_factor
            } else {
                value
            }
        })
        .sum()
}

/// §115 constants, fixed in `s115_prereg.txt` BEFORE the first d-tier game was run.
const K_DAMAGE: f64 = 1.0;
const EVOLUTION_STEP_DISCOUNT: f64 = 0.5;

/// Best damage the Pokémon occupying `slot` could throw using `form`'s attacks, discounted
/// by the energy still missing against the slot's CURRENT attached energy:
/// `fixed_damage / (1 + missing)`. `form` is the slot's own card for the in-place term, or
/// a prospective evolution for the potential term (energy survives evolution, so pricing a
/// future form against today's energy is exact).
fn best_attack_value(slot: &PlayedCard, form: &Card, state: &State, player: usize) -> f64 {
    form.get_attacks()
        .iter()
        .filter(|atk| atk.fixed_damage > 0)
        .map(|atk| {
            let missing = energy_missing(slot, &atk.energy_required, state, player).len();
            atk.fixed_damage as f64 / (1.0 + missing as f64)
        })
        .fold(0.0, f64::max)
}

/// §115 — what this slot could become: the best evolution reachable from the player's own
/// deck + hand (via [`get_highest_evolutions`], the same helper the online score already
/// uses), valued like a board Pokémon and discounted per evolution step still to take.
/// Damage counters carry through evolution in Pocket, so they are subtracted from the
/// target's HP.
fn evolution_potential(state: &State, player: usize, slot: &PlayedCard, public_only: bool) -> f64 {
    if public_only {
        return 0.0;
    }
    let Card::Pokemon(current) = &slot.card else {
        return 0.0;
    };
    let mut available: Vec<Card> = state.decks[player].cards.to_vec();
    available.extend(state.hands[player].iter().cloned());
    get_highest_evolutions(&slot.card, &available)
        .iter()
        .filter_map(|target| {
            let Card::Pokemon(t) = target else {
                return None;
            };
            let steps = t.stage.saturating_sub(current.stage);
            if steps == 0 {
                return None;
            }
            let hp = t.hp.saturating_sub(slot.get_damage_counters()) as f64;
            let dmg = best_attack_value(slot, target, state, player);
            Some((hp + K_DAMAGE * dmg) * EVOLUTION_STEP_DISCOUNT.powi(steps as i32))
        })
        .fold(0.0, f64::max)
}

/// Helper function to calculate relevant energy for a Pokemon
fn get_relevant_energy(state: &State, player: usize, card: &PlayedCard) -> f64 {
    let most_expensive_attack_cost: Vec<EnergyType> = card
        .card
        .get_attacks()
        .iter()
        .map(|atk| atk.energy_required.clone())
        .max()
        .unwrap_or_default();

    let missing = energy_missing(card, &most_expensive_attack_cost, state, player);

    let total = most_expensive_attack_cost.len() as f64;
    total - missing.len() as f64
}

/// Calculate active safety
/// Defined as remaining HP divided by knockout points
fn calculate_active_safety(state: &State, player: usize) -> f64 {
    let Some(active_pokemon) = state.maybe_get_active(player) else {
        return 0.0; // No safety if no active pokemon
    };

    let ko_points = active_pokemon.card.get_knockout_points() as f64;
    let hp = active_pokemon.get_remaining_hp() as f64;

    hp / ko_points.max(1.0)
}

/// Calculate online score for active pokemon (0.0 to 1.0)
/// Returns 1.0 if the active pokemon has enough energy to use the highest attack
/// of its highest evolution available in deck+hand
fn calculate_active_pokemon_online_score(state: &State, player: usize, public_only: bool) -> f64 {
    let Some(active_pokemon) = state.maybe_get_active(player) else {
        return 0.0;
    };

    // Get all cards available in deck + hand.
    //
    // §40: these are HIDDEN zones. When scoring an opponent we must not look in them, so
    // `public_only` leaves the list empty and the scan below falls through to the card that
    // is actually on the board — which is what an opposing player can see.
    let available_cards: Vec<Card> = if public_only {
        Vec::new()
    } else {
        let mut cards: Vec<Card> = state.decks[player].cards.to_vec();
        cards.extend(state.hands[player].iter().cloned());
        cards
    };

    // Find the highest evolution available
    let highest_evolutions = get_highest_evolutions(&active_pokemon.card, &available_cards);

    // If no evolutions found, use the current card
    let target_card = if highest_evolutions.is_empty() {
        &active_pokemon.card
    } else {
        // Use the first highest evolution (they should all be same stage)
        &highest_evolutions[0]
    };

    // Get the highest attack energy cost from the target card
    let most_expensive_attack_cost: Vec<EnergyType> = target_card
        .get_attacks()
        .iter()
        .map(|atk| atk.energy_required.clone())
        .max()
        .unwrap_or_default();

    if most_expensive_attack_cost.is_empty() {
        return 1.0; // No attack requirements, fully online
    }

    // Calculate how much energy we have vs need
    let missing = energy_missing(active_pokemon, &most_expensive_attack_cost, state, player);
    let total_needed = most_expensive_attack_cost.len() as f64;
    let have = total_needed - missing.len() as f64;

    // Return ratio (0.0 to 1.0)
    (have / total_needed).clamp(0.0, 1.0)
}
