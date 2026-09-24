use std::collections::HashMap;

use log::debug;
use rand::rngs::StdRng;

use crate::{
    actions::{
        abilities::{AbilityMechanic, RandomEvolutionTrigger},
        effect_ability_mechanic_map::{
            basic_abilities_suppressed, get_in_play_ability_mechanic,
        },
        shared_mutations, SimpleAction,
    },
    card_ids::CardId,
    effects::{CardEffect, TurnEffect},
    hooks::{
        get_counterattack_damage, maybe_attach_energy_on_damaged,
        maybe_shuffle_attacker_hand_card_on_damaged, modify_damage, on_attack_knockout,
        on_end_turn, on_knockout, should_poison_attacker, DamageModifierContext,
    },
    models::{Card, StatusCondition, TrainerType},
    state::GameOutcome,
    tools::has_tool,
    State,
};

use super::Action;

pub(crate) type Probabilities = Vec<f64>;

// Mutations should be deterministic. They take StdRng because we simplify some states spaces
//  like "shuffling a deck" (which would otherwise yield a huge state space) to a single
//  mutation/state ("shuffled deck"). Bots should not use deck order information when forecasting.
pub(crate) type FnMutation = Box<dyn Fn(&mut StdRng, &mut State, &Action)>;
pub(crate) type Mutation = Box<dyn FnOnce(&mut StdRng, &mut State, &Action)>;
pub(crate) type Mutations = Vec<Mutation>;

#[derive(Clone)]
struct CheckupTargets {
    sleeps: Vec<(usize, usize)>,
    paralyzed: Vec<(usize, usize)>,
    poisoned: Vec<(usize, usize)>,
    burned: Vec<(usize, usize)>,
}

/// Advance state to the next turn (i.e. maintain current_player and turn_count)
pub(crate) fn forecast_end_turn(state: &State) -> (Probabilities, Mutations) {
    let in_setup_phase = state.turn_count == 0;
    if in_setup_phase {
        let both_players_initiated =
            state.in_play_pokemon[0][0].is_some() && state.in_play_pokemon[1][0].is_some();
        if !both_players_initiated {
            // Just advance the setup phase to the next player
            return (
                vec![1.0],
                vec![Box::new(|_, state, _| {
                    state.end_turn_pending = false;
                    state.current_player = (state.current_player + 1) % 2;
                })],
            );
        }

        let next_player = (state.current_player + 1) % 2;
        let (start_probs, start_mutations) = start_turn_ability_outcomes(state, next_player);

        let mut outcomes: Mutations = Vec::with_capacity(start_mutations.len());
        for start_mutation in start_mutations {
            outcomes.push(Box::new(move |rng, state, action| {
                state.end_turn_pending = false;
                state.current_player = (state.current_player + 1) % 2;

                // Actually start game (no energy generation)
                state.turn_count = 1;
                state.end_turn_maintenance();
                start_mutation(rng, state, action);
                state.queue_draw_action(state.current_player, 1);
            }));
        }

        (start_probs, outcomes)
    } else {
        forecast_pokemon_checkup(state)
    }
}

/// Handle Status Effects
fn forecast_pokemon_checkup(state: &State) -> (Probabilities, Mutations) {
    let mut preview = state.clone();
    on_end_turn(state.current_player, &mut preview);
    let next = 1 - state.current_player;
    let end_evolution = preview.maybe_get_active(next).is_some_and(|active|
        matches!(get_in_play_ability_mechanic(&preview, active),
            Some(AbilityMechanic::RandomEvolutionFromDeck {
                trigger: RandomEvolutionTrigger::EndOfOpponentTurnIfActive
            })));
    if pending_point_denial(&preview) || end_evolution {
        return (vec![1.0], vec![Box::new(move |_, state, action| {
            let stack_base = state.move_generation_stack.len();
            on_end_turn(action.actor, state);
            if state.is_game_over() { return; }
            state.move_generation_stack.insert(stack_base,
                (action.actor, vec![SimpleAction::ResolvePokemonCheckup]));
            if end_evolution {
                state.move_generation_stack.insert(stack_base + 1,
                    (next, vec![SimpleAction::ResolveEndTurnEvolution { player: next }]));
            }
        })]);
    }
    let (probabilities, phases) = forecast_checkup_phase(&preview);
    let mutations = phases.into_iter().map(|phase| -> Mutation {
        Box::new(move |rng, state, action| {
            on_end_turn(action.actor, state);
            if !state.is_game_over() { phase(rng, state, action); }
        })
    }).collect();
    (probabilities, mutations)
}

pub(crate) fn forecast_checkup_phase(state: &State) -> (Probabilities, Mutations) {
    let next_player = 1 - state.current_player;
    let preview_state = state.clone();
    let checkup_targets = collect_checkup_targets(&preview_state);

    // Get all binary vectors representing the possible outcomes.
    // These are the "outcome_ids" for sleep and burn coin flips
    // (e.g. outcome [true, false] might represent waking up one pokemon and not healing another's burn).
    let total_coin_flips = checkup_targets.sleeps.len() + checkup_targets.burned.len();
    let outcome_ids = generate_boolean_vectors(total_coin_flips);
    let base_probability = 1.0 / outcome_ids.len() as f64;

    let mut probabilities = Vec::with_capacity(outcome_ids.len());
    let mut outcomes: Mutations = Vec::with_capacity(outcome_ids.len());
    for outcome in outcome_ids {
        let mut preview_after_checkup = preview_state.clone();
        if !preview_after_checkup.is_game_over() {
            apply_pokemon_checkup(&mut preview_after_checkup, &checkup_targets, &outcome);
        }
        let (start_probs, start_mutations) = if pending_point_denial(&preview_after_checkup) {
            (vec![1.0], vec![noop_mutation()])
        } else {
            start_turn_ability_outcomes(&preview_after_checkup, next_player)
        };
        for (start_prob, start_mutation) in start_probs.into_iter().zip(start_mutations) {
            let outcome = outcome.clone();
            probabilities.push(base_probability * start_prob);
            outcomes.push(Box::new(move |rng, state, action| {
                if state.is_game_over() {
                    return;
                }
                let stack_base = state.move_generation_stack.len();
                let live_checkup_targets = collect_checkup_targets(state);
                apply_pokemon_checkup(state, &live_checkup_targets, &outcome);
                if pending_point_denial(state) {
                    state.move_generation_stack.insert(stack_base,
                        (state.current_player, vec![SimpleAction::FinishPokemonCheckup]));
                    return;
                }
                // A Checkup result ends the game before another turn or its abilities.
                // In particular, advancing past turn 30 must not replace that result with Tie.
                if state.is_game_over() {
                    return;
                }
                finish_turn_after_checkup(state, rng);
                if !state.is_game_over() {
                    start_mutation(rng, state, action);
                }
            }));
        }
    }
    (probabilities, outcomes)
}

pub(crate) fn forecast_finish_checkup(state: &State) -> (Probabilities, Mutations) {
    let (probabilities, starts) = start_turn_ability_outcomes(state, 1 - state.current_player);
    let mutations = starts.into_iter().map(|start| -> Mutation {
        Box::new(move |rng, state, action| {
            if state.is_game_over() { return; }
            finish_turn_after_checkup(state, rng);
            if !state.is_game_over() { start(rng, state, action); }
        })
    }).collect();
    (probabilities, mutations)
}

fn pending_point_denial(state: &State) -> bool {
    state.move_generation_stack.iter().any(|(_, choices)| choices.iter().any(|action|
        matches!(action, SimpleAction::ResolveKnockoutPoints { .. })))
}

fn start_turn_ability_outcomes(state: &State, player: usize) -> (Probabilities, Mutations) {
    if state.is_game_over() {
        return (vec![1.0], vec![noop_mutation()]);
    }
    let Some(active) = state.maybe_get_active(player) else {
        return (vec![1.0], vec![noop_mutation()]);
    };
    let Some(mechanic) = get_in_play_ability_mechanic(state, active) else {
        return (vec![1.0], vec![noop_mutation()]);
    };

    match mechanic {
        AbilityMechanic::StartTurnRandomPokemonToHand { energy_type } => {
            shared_mutations::pokemon_search_outcomes_by_type_for_player(
                player,
                state,
                false,
                *energy_type,
            )
            .into_branches()
        }
        _ => (vec![1.0], vec![noop_mutation()]),
    }
}

/// Calculate poison damage based on base damage (usually 10, but attacks like Toxicroak's Toxic
/// override it per-Pokémon) plus +10 for each opponent's Nihilego with More Poison ability.
/// Only applies the bonus if the poisoned Pokemon is in the active spot (index 0)
fn get_poison_damage(state: &State, player: usize, in_play_idx: usize) -> u32 {
    use crate::actions::{abilities::AbilityMechanic, get_in_play_ability_mechanic};

    let base_damage = state.in_play_pokemon[player][in_play_idx]
        .as_ref()
        .and_then(|pokemon| pokemon.poison_checkup_damage())
        .unwrap_or(10);

    // Nihilego's More Poison ability only affects the active Pokemon
    if in_play_idx != 0 {
        return base_damage;
    }

    let opponent = (player + 1) % 2;
    let nihilego_count = state
        .enumerate_in_play_pokemon(opponent)
        .filter(|(_, pokemon)| {
            matches!(
                get_in_play_ability_mechanic(state, pokemon),
                Some(AbilityMechanic::IncreasePoisonDamage { amount: 10 })
            )
        })
        .count();

    let total_damage = base_damage + (nihilego_count as u32 * 10);

    if nihilego_count > 0 {
        debug!(
            "Nihilego's More Poison: {} Nihilego in play, poison damage is {}",
            nihilego_count, total_damage
        );
    }

    total_damage
}

fn collect_checkup_targets(state: &State) -> CheckupTargets {
    let mut targets = CheckupTargets {
        sleeps: vec![],
        paralyzed: vec![],
        poisoned: vec![],
        burned: vec![],
    };

    for player in [state.current_player, 1 - state.current_player] {
        for (i, pokemon) in state.enumerate_in_play_pokemon(player) {
            if pokemon.is_asleep() {
                targets.sleeps.push((player, i));
            }
            // `current_player` is still the player whose turn is ending until `advance_turn`.
            // Paralysis recovers after its owner's turn, not at every player's Checkup.
            if pokemon.is_paralyzed() && player == state.current_player {
                targets.paralyzed.push((player, i));
            }
            if pokemon.is_poisoned() {
                targets.poisoned.push((player, i));
                debug!("{player}'s Pokemon {i} is poisoned");
            }
            if pokemon.is_burned() {
                targets.burned.push((player, i));
                debug!("{player}'s Pokemon {i} is burned");
            }
        }
    }

    targets
}

fn apply_pokemon_checkup(
    mutated_state: &mut State,
    checkup_targets: &CheckupTargets,
    outcome: &[bool],
) {
    // First half of outcomes are for sleep, second half for burns
    let num_sleeps = checkup_targets.sleeps.len();
    debug_assert!(outcome.len() >= num_sleeps + checkup_targets.burned.len());

    for player in [mutated_state.current_player, 1 - mutated_state.current_player] {
        for &(_, idx) in checkup_targets.poisoned.iter().filter(|(p, _)| *p == player) {
            let damage = get_poison_damage(mutated_state, player, idx);
            handle_damage_only(mutated_state, (player, idx), &[(damage, player, idx)],
                false, DamageModifierContext::default());
        }
        for (i, &(_, idx)) in checkup_targets.burned.iter().enumerate().filter(|(_, (p, _))| *p == player) {
            handle_damage_only(mutated_state, (player, idx), &[(20, player, idx)],
                false, DamageModifierContext::default());
            if outcome[num_sleeps + i] {
                if let Some(pokemon) = mutated_state.in_play_pokemon[player][idx].as_mut() {
                    pokemon.clear_status_condition(StatusCondition::Burned);
                }
            }
        }
        for (i, &(_, idx)) in checkup_targets.sleeps.iter().enumerate().filter(|(_, (p, _))| *p == player) {
            if outcome[i] {
                if let Some(pokemon) = mutated_state.in_play_pokemon[player][idx].as_mut() {
                    pokemon.clear_status_condition(StatusCondition::Asleep);
                }
            }
        }
        for &(_, idx) in checkup_targets.paralyzed.iter().filter(|(p, _)| *p == player) {
            if let Some(pokemon) = mutated_state.in_play_pokemon[player][idx].as_mut() {
                pokemon.clear_status_condition(StatusCondition::Paralyzed);
            }
        }
    }

    apply_snowy_terrain_checkup_damage(mutated_state);
    apply_blessed_salt_checkup_healing(mutated_state);
    handle_knockouts(mutated_state, (mutated_state.current_player, 0), false);

    // Shift the per-turn KO flag. Turn advancement (including energy rotation) is performed
    // separately by `finish_turn_after_checkup` so it can consume the shared rng.
    mutated_state.knocked_out_by_opponent_attack_last_turn =
        mutated_state.knocked_out_by_opponent_attack_this_turn;
    mutated_state.knocked_out_by_opponent_attack_this_turn = false;
    mutated_state.knocked_out_types_by_opponent_attack_last_turn =
        std::mem::take(&mut mutated_state.knocked_out_types_by_opponent_attack_this_turn);
}

fn finish_turn_after_checkup(state: &mut State, rng: &mut StdRng) {
    state.advance_turn(rng);
}

/// Garganacl's Blessed Salt: "During Pokémon Checkup, heal 10 damage from each of your Pokémon."
///
/// Unlike the checkup *damage* abilities above, this one carries no Active Spot requirement, so
/// the whole board is scanned rather than just each player's Active. It runs after the checkup
/// damage, while every Pokémon remains in play. Knockouts are checked only after all
/// Checkup effects have finished. The relative damage/healing order remains source-qualified.
fn apply_blessed_salt_checkup_healing(state: &mut State) {
    for player in 0..2 {
        let total_heal: u32 = state
            .enumerate_in_play_pokemon(player)
            .filter_map(|(_, pokemon)| match get_in_play_ability_mechanic(state, pokemon) {
                Some(AbilityMechanic::CheckupHealAllYourPokemon { amount }) => Some(*amount),
                _ => None,
            })
            .sum();
        if total_heal == 0 {
            continue;
        }
        debug!("Blessed Salt: healing {total_heal} from each of player {player}'s Pokémon");
        // Routed through `heal_each_pokemon` so Claydol's Heal Block suppresses it.
        state.heal_each_pokemon(player, total_heal, |_| true);
    }
}

fn apply_snowy_terrain_checkup_damage(state: &mut State) {
    let mut active_only_damage: Vec<(usize, u32)> = vec![];
    let mut all_opponent_damage: Vec<(usize, u32)> = vec![];

    for player in [state.current_player, 1 - state.current_player] {
        let Some(active) = state.in_play_pokemon[player][0].as_ref() else {
            continue;
        };
        match get_in_play_ability_mechanic(state, active) {
            Some(AbilityMechanic::CheckupDamageToOpponentActive { amount }) => {
                active_only_damage.push((player, *amount));
            }
            Some(AbilityMechanic::CheckupDamageToAllOpponentPokemon { amount }) => {
                all_opponent_damage.push((player, *amount));
            }
            _ => {}
        }
    }

    for (source_player, checkup_damage) in active_only_damage {
        let target_player = (source_player + 1) % 2;
        if state.in_play_pokemon[target_player][0].is_some() {
            debug!(
                "Snowy Terrain: Player {} active Pokémon deals {} checkup damage to opponent active",
                source_player, checkup_damage
            );
            handle_damage_only(
                state,
                (source_player, 0),
                &[(checkup_damage, target_player, 0)],
                false,
                DamageModifierContext::default(),
            );
        }
    }

    for (source_player, checkup_damage) in all_opponent_damage {
        let target_player = (source_player + 1) % 2;
        let targets: Vec<(u32, usize, usize)> = state
            .enumerate_in_play_pokemon(target_player)
            .map(|(idx, _)| (checkup_damage, target_player, idx))
            .collect();
        if !targets.is_empty() {
            debug!(
                "Sand Slammer: Player {} active Pokémon deals {} checkup damage to all opponent Pokémon",
                source_player, checkup_damage
            );
            handle_damage_only(state, (source_player, 0), &targets, false, DamageModifierContext::default());
        }
    }
}

fn generate_boolean_vectors(n: usize) -> Vec<Vec<bool>> {
    // The total number of combinations is 2^n
    let total_combinations = 1 << n; // 2^n

    // Generate all combinations
    (0..total_combinations)
        .map(|i| {
            // Convert the number `i` to its binary representation as a vector of booleans
            (0..n).map(|bit| (i & (1 << bit)) != 0).collect()
        })
        .collect()
}

fn checkapply_prevent_first_attack(
    state: &mut State,
    target_player: usize,
    target_pokemon_idx: usize,
    is_from_active_attack: bool,
) -> bool {
    if !is_from_active_attack {
        return false;
    }

    // Resolved before the mutable borrow, since the suppression check reads the board.
    let prevents = state.in_play_pokemon[target_player][target_pokemon_idx]
        .as_ref()
        .is_some_and(|target_pokemon| {
            !target_pokemon.prevent_first_attack_damage_used
                && get_in_play_ability_mechanic(state, target_pokemon)
                    == Some(&AbilityMechanic::PreventFirstAttack)
        });
    if !prevents {
        return false;
    }
    if let Some(target_pokemon) = state.in_play_pokemon[target_player][target_pokemon_idx].as_mut()
    {
        debug!("PreventFirstAttackDamageAfterEnteringPlay: Preventing first attack damage");
        target_pokemon.prevent_first_attack_damage_used = true;
        return true;
    }
    false
}

/// True if the Pokémon at `target` has the Guts ability and `raw_damage` (after modifiers)
/// would knock it out — i.e. it should flip a Guts survival coin for this damage.
pub(crate) fn guts_would_flip(
    state: &State,
    attacking_ref: (usize, usize),
    raw_damage: u32,
    target: (usize, usize),
    is_from_active_attack: bool,
    context: DamageModifierContext<'_>,
) -> bool {
    if raw_damage == 0 {
        return false;
    }
    let Some(pokemon) = state.in_play_pokemon[target.0][target.1].as_ref() else {
        return false;
    };
    if !matches!(
        get_in_play_ability_mechanic(state, pokemon),
        Some(AbilityMechanic::CoinFlipToSurviveKnockOut)
    ) {
        return false;
    }
    let modified = modify_damage(
        state,
        attacking_ref,
        (raw_damage, target.0, target.1),
        is_from_active_attack,
        context,
    );
    let remaining = pokemon.get_remaining_hp();
    remaining > 0 && modified >= remaining
}

/// This function applies damage (with modifiers and counterattacks) and handles K.O.s
/// and promotions.
pub(crate) fn handle_damage(
    state: &mut State,
    attacking_ref: (usize, usize), // (attacking_player, attacking_pokemon_idx)
    targets: &[(u32, usize, usize)], // damage, target_player, in_play_idx
    is_from_active_attack: bool,
    attack_name: Option<&str>,
) {
    let damaged_actives = handle_damage_only(
        state,
        attacking_ref,
        targets,
        is_from_active_attack,
        DamageModifierContext {
            attack_name,
            attack_effect: None,
        },
    );
    handle_attack_retaliation(state, attacking_ref, &damaged_actives);
    handle_knockouts(state, attacking_ref, is_from_active_attack);
}

// This function handles Attack Modifiers and Attack Modifiers, but doesn't handle K.O.s or
// queues up promotion decisions. Use carefully, probably just in a few places
pub(crate) fn handle_damage_only(
    state: &mut State,
    attacking_ref: (usize, usize), // (attacking_player, attacking_pokemon_idx)
    targets: &[(u32, usize, usize)], // damage, target_player, in_play_idx
    is_from_active_attack: bool,
    context: DamageModifierContext<'_>,
) -> Vec<(usize, usize)> {
    let mut damaged_actives = Vec::new();
    let attacking_player = attacking_ref.0;

    // Reduce and sum damage for duplicate targets
    let mut damage_map: HashMap<(usize, usize), u32> = HashMap::new();
    for (damage, player, idx) in targets {
        *damage_map.entry((*player, *idx)).or_insert(0) += damage;
    }
    let targets: Vec<(u32, usize, usize)> = damage_map
        .into_iter()
        .map(|((player, idx), damage)| (damage, player, idx))
        .collect();

    // Modify to apply any multipliers (e.g. Oricorio, Giovanni, etc...)
    let modified_targets = targets
        .iter()
        .map(|target_ref| {
            let modified_damage = modify_damage(
                state,
                attacking_ref,
                *target_ref,
                is_from_active_attack,
                context,
            );
            (modified_damage, target_ref.1, target_ref.2)
        })
        .collect::<Vec<(u32, usize, usize)>>();

    // Handle each target individually
    for (damage, target_player, target_pokemon_idx) in modified_targets {
        let applied = checkapply_prevent_first_attack(
            state,
            target_player,
            target_pokemon_idx,
            is_from_active_attack,
        );
        if applied || damage == 0 {
            continue;
        }

        // Apply damage
        {
            let target_pokemon = state.in_play_pokemon[target_player][target_pokemon_idx]
                .as_mut()
                .expect("Pokemon should be there if taking damage");
            target_pokemon.apply_damage(damage); // Applies without surpassing 0 HP
            if is_from_active_attack && target_player != attacking_player && target_pokemon_idx == 0
            {
                // Wobbuffet's Reply Strongly: remember the Active Spot was damaged by an
                // opponent's attack this turn.
                target_pokemon.damaged_by_attack_while_active_this_turn = true;
            }
            debug!(
                "Dealt {} damage to opponent's {} Pokemon. Remaining HP: {}",
                damage,
                target_pokemon_idx,
                target_pokemon.get_remaining_hp()
            );
        }

        if is_from_active_attack && target_player != attacking_player && target_pokemon_idx == 0 {
            damaged_actives.push((target_player, target_pokemon_idx));
        }
    }
    damaged_actives
}

/// Resolve reactions only after the attack's own effects, using the current Ability state.
pub(crate) fn handle_attack_retaliation(
    state: &mut State,
    attacking_ref: (usize, usize),
    damaged_actives: &[(usize, usize)],
) {
    let attacking_player = attacking_ref.0;
    for &(target_player, target_idx) in damaged_actives {
        let Some(target) = state.in_play_pokemon[target_player][target_idx].as_ref() else { continue; };
        let counter_damage = get_counterattack_damage(state, target);
        let should_poison = should_poison_attacker(state, target);
        if let Some(attacker) = state.in_play_pokemon[attacking_player][attacking_ref.1].as_mut() {
            attacker.apply_damage(counter_damage);
        }
        if should_poison && attacking_ref.1 == 0 {
            state.apply_status_condition(attacking_player, attacking_ref.1, StatusCondition::Poisoned);
        }
        maybe_attach_energy_on_damaged(state, target_player, target_idx);
        maybe_shuffle_attacker_hand_card_on_damaged(state, target_player, target_idx, attacking_player);
    }
}

fn is_iris_bonus_active(
    state: &State,
    attacking_ref: (usize, usize),
    is_from_active_attack: bool,
) -> bool {
    if !is_from_active_attack {
        return false;
    }
    let has_iris_effect = state
        .get_current_turn_effects()
        .iter()
        .any(|e| matches!(e, TurnEffect::BonusPointForHaxorusActiveKO));
    if !has_iris_effect {
        return false;
    }
    state.in_play_pokemon[attacking_ref.0][attacking_ref.1]
        .as_ref()
        .map(|attacker| {
            matches!(
                CardId::from_card_id(match &attacker.card {
                    Card::Pokemon(p) => p.id.as_str(),
                    Card::Trainer(t) => t.id.as_str(),
                    Card::Unknown => return false,
                }),
                Some(CardId::B2b056Haxorus | CardId::B2b110Haxorus | CardId::PB045Haxorus)
            )
        })
        .unwrap_or(false)
}

pub(crate) fn handle_knockouts(
    state: &mut State,
    attacking_ref: (usize, usize), // (attacking_player, attacking_pokemon_idx)
    is_from_active_attack: bool,
) {
    handle_knockouts_with_prior(state, attacking_ref, is_from_active_attack, Vec::new());
}

pub(crate) fn handle_knockouts_with_prior(
    state: &mut State,
    attacking_ref: (usize, usize),
    is_from_active_attack: bool,
    mut knockouts: Vec<(usize, usize)>,
) {
    // An attack's target choices and reactions must settle before its KO wave.
    if state.move_generation_stack.iter().any(|(_, choices)| choices.iter().any(|a|
        matches!(a, SimpleAction::ResolveAttackRetaliation { .. }))) { return; }
    // Hala: rescue the named Pokémon at 10 HP *before* anything counts as a knockout, so no points
    // are awarded, nothing is discarded, and no promotion is queued for them.
    if is_from_active_attack {
        apply_survive_knockout_turn_effects(state);
    }

    let iris_bonus_active = is_iris_bonus_active(state, attacking_ref, is_from_active_attack);

    // Handle knockouts: Discard cards and award points (to potentially short-circuit promotions).
    //
    // Resolved in waves rather than in a single pass because losing a Pokémon can shrink the
    // effective HP of the ones left behind — Lilligant's Toughness Aroma ("Each of your [G]
    // Pokémon gets +20 HP") is removed as soon as Lilligant leaves play — which can knock those
    // Pokémon out in turn. Each wave discards at least one Pokémon, so this always terminates.
    loop {
        let wave = get_knocked_out(state);
        if wave.is_empty() {
            break;
        }
        // Finish all required coins before discarding any member of this simultaneous wave.
        // This also preserves suppression while a suppressor is in the same KO wave.
        if pending_point_denial(state) { return; }
        for &(player, idx) in &wave {
            let pokemon = state.in_play_pokemon[player][idx].as_ref().unwrap();
            let coin_resolved = pokemon.get_active_effects().iter().any(|effect|
                matches!(effect, CardEffect::KnockoutPointsCoinResolved));
            if !coin_resolved && matches!(get_in_play_ability_mechanic(state, pokemon),
                Some(AbilityMechanic::CoinFlipToDenyKnockoutPoints)) {
                state.move_generation_stack.push((player, vec![SimpleAction::ResolveKnockoutPoints {
                    player, in_play_idx: idx, attacking_ref, is_from_active_attack,
                    prior_knockouts: knockouts.clone(),
                }]));
                return;
            }
        }
        // Run every knockout hook while the full simultaneous wave is still in play. An on-KO
        // Ability may target another member of the wave: Destiny Burst, for example, must still
        // find an attacker that Rocky Helmet has already reduced to 0 HP. Discarding the attacker
        // before the defender's hook runs made that legal double-KO sequence panic.
        for (ko_receiver, ko_pokemon_idx) in wave.iter().copied() {
            on_knockout(
                state,
                ko_receiver,
                ko_pokemon_idx,
                attacking_ref,
                is_from_active_attack,
            );
            on_attack_knockout(state, attacking_ref, ko_receiver, is_from_active_attack);
        }

        for (ko_receiver, ko_pokemon_idx) in wave.iter().copied() {
            // Award points
            {
                let ko_initiator = (ko_receiver + 1) % 2;
                // Dusknoir "Fade into Darkness" / Glimmora "Shattering Crystal": the coin was already
                // flipped at forecast time, and a heads branch tagged this Pokémon with
                // DenyKnockoutPoints. The knockout itself still stands — only the score is denied.
                let (points_denied, points_won) = {
                    let ko_pokemon = state.in_play_pokemon[ko_receiver][ko_pokemon_idx]
                        .as_ref()
                        .expect("Pokemon should be there if knocked out");
                    let points_denied = ko_pokemon
                        .get_effective_card_effects(state)
                        .iter()
                        .any(|effect| matches!(effect, CardEffect::DenyKnockoutPoints));
                    let points_won = if points_denied {
                        0
                    } else {
                        ko_pokemon.card.get_knockout_points()
                    };
                    (points_denied, points_won)
                };
                state.award_points(ko_initiator, points_won);
                let ko_pokemon = state.in_play_pokemon[ko_receiver][ko_pokemon_idx]
                    .as_ref()
                    .expect("Pokemon should still be present while logging its knockout");
                debug!(
                    "Pokemon {:?} fainted. Player {} won {} points for a total of {}{}",
                    ko_pokemon,
                    ko_initiator,
                    points_won,
                    state.points[ko_initiator],
                    if points_denied {
                        " (point-denial coin flip came up heads)"
                    } else {
                        ""
                    }
                );
                // Iris bonus: 1 extra point if Haxorus KOs opponent's Active Pokemon
                if !points_denied
                    && iris_bonus_active
                    && ko_pokemon_idx == 0
                    && ko_receiver != attacking_ref.0
                {
                    state.award_points(ko_initiator, 1);
                    debug!(
                        "Iris: Player {} gets 1 bonus point for Haxorus KO",
                        ko_initiator
                    );
                }
            }

            // Game-long tally of each player's own losses (Kingambit's Overlord's Blade). Counted for
            // every knockout regardless of cause — self-damage and recoil KOs are still your Pokémon
            // being Knocked Out.
            state.own_knockouts_this_game[ko_receiver] += 1;

            // Type-filtered vengeance attacks (Zarude's Dark Vengeance): record the energy type
            // of each Pokémon Knocked Out by damage from an opponent's attack this turn. Must be
            // captured here, while the card is still in play. Fossils have no energy type and are
            // covered only by the untyped flag below.
            if is_from_active_attack && ko_receiver != attacking_ref.0 {
                let ko_types = state.in_play_pokemon[ko_receiver][ko_pokemon_idx]
                    .as_ref()
                    .map(|pokemon| state.pokemon_energy_types(pokemon))
                    .unwrap_or_default();
                for energy_type in ko_types {
                    state
                        .knocked_out_types_by_opponent_attack_this_turn
                        .push(energy_type);
                }
            }

            // Rescue Scarf (A4 155): if an opponent's attack knocked this Pokémon out, its card goes
            // back to its owner's hand instead of the discard pile. The knockout still stands and the
            // points are still awarded above — only the destination of the card changes.
            let rescued = is_from_active_attack
                && attacking_ref.0 != ko_receiver
                && state.in_play_pokemon[ko_receiver][ko_pokemon_idx]
                    .as_ref()
                    .is_some_and(|pokemon| has_tool(pokemon, CardId::A4155RescueScarf));
            if rescued {
                state.rescue_from_play(ko_receiver, ko_pokemon_idx);
            } else {
                state.discard_from_play(ko_receiver, ko_pokemon_idx);
            }
        }
        knockouts.extend(wave);
    }

    // Set knocked_out_by_opponent_attack_this_turn flag
    // Check if any of the current player's Pokémon were knocked out by an opponent's active attack
    if is_from_active_attack {
        // Only care about KOs from active attacks
        for (ko_receiver, _) in knockouts.clone() {
            let ko_initiator_of_this_damage = attacking_ref.0; // The player who caused the damage
                                                               // If the receiver is NOT the initiator, it's an opponent KO
            if ko_receiver != ko_initiator_of_this_damage {
                state.knocked_out_by_opponent_attack_this_turn = true;
                break; // Only need to set once
            }
        }
    }

    // On-knockout retaliation abilities (Pyukumuku's Innards Out, Spiritomb's Final Scream) deal
    // their damage from the `on_knockout` hook above, which can leave Pokémon at 0 HP that were
    // not in the `knockouts` snapshot taken at the top of this function. Resolve them in a nested
    // pass *before* the win checks below, so a mutual knockout banks both players' points and can
    // end in a tie. The nested pass runs with `is_from_active_attack: false`, which no on-knockout
    // retaliation ability triggers on — so the recursion is at most one level deep.
    if !get_knocked_out(state).is_empty() {
        handle_knockouts(state, attacking_ref, false);
        if state.winner.is_some() {
            return;
        }
    }

    // If game ends because of knockouts, set winner and return so as to short-circuit promotion logic.
    // T2: a last attacking Pokemon can take its third point while a same-attack
    // retaliation knocks it out. The point win and no-Pokemon loss cancel to a tie
    // when the opponent still has Pokemon and has not also reached three points.
    let p0_remaining = state.enumerate_in_play_pokemon(0).count();
    let p1_remaining = state.enumerate_in_play_pokemon(1).count();
    if ((state.points[0] >= 3 && state.points[1] < 3)
        && p0_remaining == 0 && p1_remaining > 0)
        || ((state.points[1] >= 3 && state.points[0] < 3)
            && p1_remaining == 0 && p0_remaining > 0)
    {
        debug!("Third point and last Pokemon knocked out in the same exchange, tie");
        state.winner = Some(GameOutcome::Tie);
        return;
    }

    // Note even the attacking player can lose by counterattack K.O.
    if state.points[0] >= 3 && state.points[1] >= 3 {
        debug!("Both players have 3 points, it's a tie");
        state.winner = Some(GameOutcome::Tie);
        return;
    } else if state.points[0] >= 3 {
        state.winner = Some(GameOutcome::Win(0));
        return;
    } else if state.points[1] >= 3 {
        state.winner = Some(GameOutcome::Win(1));
        return;
    }

    // If a player has no Pokemon left in play, they immediately lose (even if points < 3).
    if p0_remaining == 0 && p1_remaining == 0 {
        debug!("Both players have no Pokemon left in play, it's a tie");
        state.winner = Some(GameOutcome::Tie);
        return;
    } else if p0_remaining == 0 {
        state.winner = Some(GameOutcome::Win(1));
        return;
    } else if p1_remaining == 0 {
        state.winner = Some(GameOutcome::Win(0));
        return;
    }

    if !knockouts.is_empty() {
        prune_stale_bench_activate_choices(state);
    }

    // Promotion frames are inserted below earlier frames; enqueue the attacker first
    // so the attacker is offered the first replacement in either seat.
    if is_from_active_attack {
        knockouts.sort_by_key(|(player, _)| *player != attacking_ref.0);
    }
    // Checkup double-KO promotion order remains an open rule question.
    for (ko_receiver, ko_pokemon_idx) in knockouts {
        if ko_pokemon_idx != 0 {
            continue; // Only promote if K.O. was on Active
        }
        // If K.O. was Active, trigger promotion or declare winner
        state.trigger_promotion_or_declare_winner(ko_receiver);
    }
}

/// Hala (B1 222): "During your opponent's next turn, if your Hariyama or Crabominable would be
/// Knocked Out by damage from an attack, it is not Knocked Out and its remaining HP becomes 10."
///
/// Runs before knockouts are collected, so a rescued Pokémon never appears in a knockout wave: it
/// stays in play, awards no points, and does not trigger a promotion. Only invoked for damage from
/// an attack, matching the card's wording.
pub(crate) fn apply_survive_knockout_turn_effects(state: &mut State) {
    let rescues: Vec<(usize, Vec<String>, u32)> = state
        .get_current_turn_effects()
        .into_iter()
        .filter_map(|effect| match effect {
            TurnEffect::SurviveKnockoutForSpecificPokemon {
                remaining_hp,
                pokemon_names,
                player,
            } => Some((player, pokemon_names, remaining_hp)),
            _ => None,
        })
        .collect();

    for (player, pokemon_names, remaining_hp) in rescues {
        for pokemon in state.in_play_pokemon[player].iter_mut().flatten() {
            if pokemon.is_knocked_out() && pokemon_names.contains(&pokemon.get_name()) {
                debug!(
                    "Hala: {} survives with {remaining_hp} HP instead of being Knocked Out",
                    pokemon.get_name()
                );
                pokemon.set_remaining_hp(remaining_hp);
            }
        }
    }
}

fn get_knocked_out(state: &State) -> Vec<(usize, usize)> {
    let mut knockouts: Vec<(usize, usize)> = vec![];
    for (idx, card) in state.enumerate_in_play_pokemon(0) {
        if card.is_knocked_out() {
            knockouts.push((0, idx));
        }
    }
    for (idx, card) in state.enumerate_in_play_pokemon(1) {
        if card.is_knocked_out() {
            knockouts.push((1, idx));
        }
    }
    knockouts
}

/// Swap a bench pokemon into the active spot, clearing status/effects and setting turn flags.
/// This is the swap portion of retreat without energy payment.
pub(crate) fn apply_activate(player: usize, state: &mut State, bench_idx: usize) {
    // Attack reactions refer to the Pokémon which actually attacked/took damage, even
    // when that attack's effect moves either Pokémon before the reaction resolves.
    for (_, choices) in &mut state.move_generation_stack {
        for choice in choices {
            if let SimpleAction::ResolveAttackRetaliation { attacking_ref, damaged_refs, point_denial_flips, .. } = choice {
                let remap = |target: &mut (usize, usize)| {
                    if target.0 == player {
                        if target.1 == 0 { target.1 = bench_idx; }
                        else if target.1 == bench_idx { target.1 = 0; }
                    }
                };
                remap(attacking_ref);
                for target in damaged_refs { remap(target); }
                for (target, _) in point_denial_flips { remap(target); }
            }
        }
    }
    state.in_play_pokemon[player].swap(0, bench_idx);

    if let Some(pokemon) = state.in_play_pokemon[player][bench_idx].as_mut() {
        pokemon.clear_status_and_effects();
    }

    if let Some(pokemon) = state.in_play_pokemon[player][0].as_mut() {
        pokemon.moved_to_active_this_turn = true;
    }
}

/// Apply costs and one-time bookkeeping that belong to starting an action.  A paused coin effect
/// uses this before exposing its result so the played card and Supporter slot already match the
/// public game state while the player decides whether to replace the batch.
pub(crate) fn apply_common_action_prefix(state: &mut State, action: &Action) {
    if action.is_stack {
        state.move_generation_stack.pop();
    }
    if let SimpleAction::Play { trainer_card } = &action.action {
        let card = Card::Trainer(trainer_card.clone());
        if trainer_card.trainer_card_type == TrainerType::Stadium {
            state.has_played_stadium = true;
            // Replaced Stadium cards go to the discard pile of the player who played them.
            if let Some((old_stadium, old_owner)) =
                state.set_active_stadium_for_player(action.actor, card.clone())
            {
                state.discard_piles[old_owner.unwrap_or(action.actor)].push(old_stadium);
            }
            state.remove_card_from_hand(action.actor, &card);
            state.refresh_hp_bonuses_all();
            handle_knockouts(state, (action.actor, 0), false);
        } else if trainer_card.trainer_card_type == TrainerType::Tool {
            state.remove_card_from_hand(action.actor, &card);
        } else {
            state.discard_card_from_hand(action.actor, &card);
        }
        if card.is_support() {
            state.has_played_support = true;
        }
    }
    if let SimpleAction::UseAbility { in_play_idx } = &action.action {
        let pokemon = state.in_play_pokemon[action.actor][*in_play_idx]
            .as_mut()
            .expect("Pokemon should be there if using ability");
        pokemon.ability_used = true;
    }
    if let SimpleAction::Attack(attack) = &action.action {
        state.record_attack_used(action.actor, attack.title.clone());
    }
}

/// Remove only publicly impossible Bench choices from an ordinary switch frame after every
/// knockout wave has settled. The existing frame remains the eligibility upper bound: this does
/// not add targets or reconsider card-specific switch restrictions.
fn prune_stale_bench_activate_choices(state: &mut State) {
    let in_play_pokemon = &state.in_play_pokemon;
    state.move_generation_stack.retain_mut(|(_, choices)| {
        if choices.is_empty() {
            return true;
        }

        let mut target_player = None;
        let mut has_activate = false;
        for choice in choices.iter() {
            match choice {
                SimpleAction::Noop => {}
                SimpleAction::Activate {
                    player,
                    in_play_idx,
                } => {
                    let Some(board) = in_play_pokemon.get(*player) else {
                        return true;
                    };
                    if *in_play_idx == 0 || *in_play_idx >= board.len() {
                        return true;
                    }
                    if target_player.is_some_and(|prior| prior != *player) {
                        return true;
                    }
                    target_player = Some(*player);
                    has_activate = true;
                }
                _ => return true,
            }
        }

        if !has_activate {
            return true;
        }
        let player = target_player.expect("an Activate choice supplied the target player");
        if in_play_pokemon[player][0].is_none() {
            return true;
        }

        choices.retain(|choice| match choice {
            SimpleAction::Noop => true,
            SimpleAction::Activate {
                player,
                in_play_idx,
            } => in_play_pokemon[*player][*in_play_idx].is_some(),
            _ => unreachable!("the frame was validated before pruning"),
        });
        !choices.is_empty()
    });
}

/// Apply the shared state repair that follows an action's effect.  This is separate from the
/// prefix so a paused Trainer coin effect can commit without paying its Play cost twice.
pub(crate) fn apply_common_action_suffix(state: &mut State, action: &Action) {
    // Energy movement can change per-Energy HP abilities (including effective Energy altered
    // by Jungle Totem), and board changes can change team-wide bonuses.
    state.refresh_hp_bonuses_all();

    // Catch-all knockout check: any action could have reduced a Pokemon's
    // effective HP below its damage taken (e.g. Field Blower discarding a
    // Giant Cape). This way individual mutations don't need to remember to
    // check for knockouts themselves. Damage-dealing mutations already call
    // handle_knockouts with the proper attacking context, so this is a no-op
    // for them.
    // Skipped during the initial setup phase, where players place their boards
    // one at a time and "0 Pokemon in play" doesn't mean a loss.
    if state.turn_count > 0 {
        handle_knockouts(state, (action.actor, 0), false);
    }

    if let SimpleAction::Attack(_) = &action.action {
        // We use a flag instead of .move_generation_stack to reduce
        // stack surgery to make sure things happen in order.
        // This ensures move_generation_stack (effects and promotions)
        // has priority over ending the turn.
        state.end_turn_pending = true;
    }
}

// Apply common logic in outcomes
pub(crate) fn wrap_with_common_logic(mutation: Mutation) -> Mutation {
    Box::new(move |rng, state, action| {
        let basic_abilities_were_suppressed = basic_abilities_suppressed(state);
        apply_common_action_prefix(state, action);
        mutation(rng, state, action); // in the case of attacks, have this be damage + effect.
                                      // Misty has a public target phase before its coins. Its one-time suffix belongs to the
                                      // eventual target/coin commit, not the initial Play/Ability that created the prompt.
        if state.pending_misty_target_choice.is_none() {
            apply_common_action_suffix(state, action);
            // Reconcile only after the suffix completes its catch-all knockout pass. This
            // prevents a 0-HP Comfey or Ogerpon from curing before the same wave removes it.
            if basic_abilities_were_suppressed && !basic_abilities_suppressed(state) {
                state.apply_effective_soothing_wind_for_all_players();
            }
        }
    })
}

fn noop_mutation() -> Mutation {
    Box::new(|_, _, _| {})
}

#[cfg(test)]
#[path = "bench_switch_target_tests.rs"]
mod bench_switch_target_tests;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{card_ids::CardId, database::get_card_by_enum, hooks::to_playable_card};

    #[test]
    fn test_poison_damage_no_nihilego() {
        let state = State::default();
        // Poison damage should be 10 with no Nihilego in play
        assert_eq!(get_poison_damage(&state, 0, 0), 10);
    }

    #[test]
    fn test_poison_damage_with_nihilego() {
        let mut state = State::default();

        // Add 2 Nihilego to opponent's field (player 1)
        let nihilego = get_card_by_enum(CardId::A3a042Nihilego);
        state.in_play_pokemon[1][0] = Some(to_playable_card(&nihilego, false));
        state.in_play_pokemon[1][1] = Some(to_playable_card(&nihilego, false));

        // Player 0's active pokemon should take 30 damage (10 base + 10 per Nihilego)
        assert_eq!(get_poison_damage(&state, 0, 0), 30);
    }

    #[test]
    fn test_mimikyu_ex_disguise_prevents_first_attack_only() {
        let mut state = State::default();

        let attacker = get_card_by_enum(CardId::A1001Bulbasaur);
        let mimikyu_ex = get_card_by_enum(CardId::B2073MimikyuEx);

        state.in_play_pokemon[0][0] = Some(to_playable_card(&attacker, false));
        state.in_play_pokemon[1][0] = Some(to_playable_card(&mimikyu_ex, false));

        let starting_hp = state.get_active(1).get_remaining_hp();

        // First attack damage should be prevented
        handle_damage(&mut state, (0, 0), &[(30, 1, 0)], true, None);
        assert_eq!(state.get_active(1).get_remaining_hp(), starting_hp);

        // Second attack should deal damage normally
        handle_damage(&mut state, (0, 0), &[(30, 1, 0)], true, None);
        assert_eq!(state.get_active(1).get_remaining_hp(), starting_hp - 30);
    }
}
