//! §47 — Bounded candidate generation for "move Energy around your own board" effects.
//!
//! # Why this module exists
//!
//! Two cards let a player redistribute Energy without a printed limit:
//!
//! * **Vaporeon (A1a 019) — Wash Out**: *"As often as you like during your turn, you may move a
//!   [W] Energy from 1 of your Benched [W] Pokémon to your Active [W] Pokémon."*
//! * **Delcatty (B4 135) — Energy Blender**: *"You may move any amount of Energy from your Pokémon
//!   in play to your other Pokémon in any way you like."*
//!
//! Taken literally, both describe the full lattice of Energy redistributions. Wash Out reaches it
//! by repetition — it has no `ability_used` gate by design, so it re-enters the legal action list
//! after every single use and multiplies the branching factor at *every* node of the search.
//!
//! **§43-D measured the cost of that: `milotic-vaporeon` ran 5–13× slower than every other deck in
//! the pool at the same settings — turn ratio 1.00×, so it was pure branching factor, not longer
//! games — and it had to be dropped from the §43-C gauntlet mid-run.** The card was not merely
//! expensive; it was unusable, and dropping it removed a real archetype from the field.
//!
//! # ⚠ THIS MODULE DELIBERATELY DEVIATES FROM THE PRINTED CARD TEXT
//!
//! Rather than enumerate every legal redistribution, it enumerates only the ones with a *purpose*:
//!
//! 1. **ENABLE** — for each attack on the destination Pokémon, the cheapest transfer that makes
//!    that attack payable this turn. This is the overwhelmingly common real-game use: feed the
//!    Active exactly enough to swing.
//! 2. **RESCUE** — evacuate every eligible Energy off one source Pokémon. This is the play a pure
//!    "enables an attack" filter would silently delete: pulling Energy off a Pokémon that is about
//!    to be knocked out, so it is not discarded along with it.
//!
//! Arbitrary partial shuffles with no immediate payoff are **not** offered. A human can make one;
//! the bot no longer can.
//!
//! **This is a heuristic over the candidate list, not a change to the rules.** Nothing illegal
//! becomes legal. What changes is that some legal-but-pointless plays are no longer searched, which
//! makes the two cards playable at all. §42 is the cautionary precedent here — the value function's
//! `is_public_information_action` filter deleted 44–51% of real actions *silently*, and that is
//! still the surviving explanation for the `x3` regression. The lesson taken from it was not "never
//! prune" but **"never prune silently"**, hence this file's length.
//!
//! # Escape hatch
//!
//! Set `DECKGYM_UNBOUNDED_ENERGY_MOVES=1` to restore the literal, unbounded behaviour for Wash Out.
//! It is slow by construction — that is the point of having it — but it makes the deviation
//! measurable rather than merely asserted.

use std::sync::LazyLock;

use crate::{
    hooks::{energy_missing, get_attack_cost},
    models::EnergyType,
    State,
};

use super::SimpleAction;

/// Whether to fall back to the literal, unbounded enumeration (see module docs).
pub(crate) static UNBOUNDED_ENERGY_MOVES: LazyLock<bool> = LazyLock::new(|| {
    std::env::var("DECKGYM_UNBOUNDED_ENERGY_MOVES")
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false)
});

/// Which Energy may move, from where, to where.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum EnergyMoveScope {
    /// Vaporeon's Wash Out: only `energy_type` Energy, only from Benched Pokémon of that type,
    /// only onto the Active Spot (which must also be that type — the caller checks that).
    TypedBenchToActive(EnergyType),
    /// Delcatty's Energy Blender: any Energy, from any of your Pokémon, onto any *other* one.
    AnyToAny,
}

/// The purposeful redistributions available to `player` under `scope`.
///
/// Returns at most a couple of dozen candidates regardless of board state — bounded by
/// (destinations × attacks) + sources, not by the number of ways Energy can be partitioned.
pub(crate) fn bounded_energy_move_candidates(
    state: &State,
    player: usize,
    scope: EnergyMoveScope,
) -> Vec<SimpleAction> {
    let destinations: Vec<usize> = match scope {
        EnergyMoveScope::TypedBenchToActive(_) => vec![0],
        EnergyMoveScope::AnyToAny => state
            .enumerate_in_play_pokemon(player)
            .map(|(idx, _)| idx)
            .collect(),
    };

    let mut candidates: Vec<SimpleAction> = Vec::new();
    for to_idx in destinations {
        let sources = eligible_sources(state, player, scope, to_idx);
        if sources.is_empty() {
            continue;
        }

        // ---- Intent 1: ENABLE. The cheapest transfer that turns on one of this Pokémon's attacks.
        if let Some(destination) = state.in_play_pokemon[player][to_idx].as_ref() {
            for attack in destination.card.get_attacks() {
                let cost = get_attack_cost(&attack.energy_required, state, player);
                let missing = energy_missing(destination, &cost, state, player);
                if missing.is_empty() {
                    continue; // already payable — moving Energy here buys nothing
                }
                if let Some(transfers) = plan_transfers(&missing, &sources) {
                    push_unique(
                        &mut candidates,
                        SimpleAction::ConsolidateEnergyToPokemon {
                            to_in_play_idx: to_idx,
                            transfers,
                        },
                    );
                }
            }
        }

        // ---- Intent 2: RESCUE. Evacuate one source completely.
        //
        // Not covered by intent 1: pulling Energy off a Pokémon that is about to be knocked out
        // has no attack-enabling payoff this turn, but it is a real and common play.
        for (from_idx, available) in &sources {
            if available.is_empty() {
                continue;
            }
            push_unique(
                &mut candidates,
                SimpleAction::ConsolidateEnergyToPokemon {
                    to_in_play_idx: to_idx,
                    transfers: vec![(*from_idx, available.clone())],
                },
            );
        }
    }

    candidates
}

/// `(in_play_idx, movable Energy on it)` for every legal source, in ascending index order so the
/// candidate list is deterministic.
fn eligible_sources(
    state: &State,
    player: usize,
    scope: EnergyMoveScope,
    to_idx: usize,
) -> Vec<(usize, Vec<EnergyType>)> {
    state
        .enumerate_in_play_pokemon(player)
        .filter(|(idx, _)| *idx != to_idx)
        .filter_map(|(idx, pokemon)| match scope {
            EnergyMoveScope::TypedBenchToActive(energy_type) => {
                // Bench only, and the source itself must be of that type.
                if idx == 0 || pokemon.card.get_type() != Some(energy_type) {
                    return None;
                }
                let movable: Vec<EnergyType> = pokemon
                    .attached_energy
                    .iter()
                    .copied()
                    .filter(|e| *e == energy_type)
                    .collect();
                (!movable.is_empty()).then_some((idx, movable))
            }
            EnergyMoveScope::AnyToAny => {
                let movable: Vec<EnergyType> = pokemon.attached_energy.to_vec();
                (!movable.is_empty()).then_some((idx, movable))
            }
        })
        .collect()
}

/// Pull `missing` out of `sources`, or return `None` if the board cannot cover it.
///
/// Specific Energy types are matched first, then any `Colorless` shortfall is paid with whatever is
/// left over — the same order [`crate::hooks::energy_missing`] uses when it decides what is
/// missing in the first place, so the two agree. Sources are consumed in index order, which makes
/// the resulting plan deterministic (two identical boards always produce the identical action, so
/// the candidate list is stable across runs and across bots).
fn plan_transfers(
    missing: &[EnergyType],
    sources: &[(usize, Vec<EnergyType>)],
) -> Option<Vec<(usize, Vec<EnergyType>)>> {
    let mut pools: Vec<(usize, Vec<EnergyType>)> = sources.to_vec();
    let mut taken: Vec<(usize, Vec<EnergyType>)> = Vec::new();

    let mut take = |pools: &mut Vec<(usize, Vec<EnergyType>)>,
                    taken: &mut Vec<(usize, Vec<EnergyType>)>,
                    wanted: Option<EnergyType>|
     -> bool {
        for (idx, pool) in pools.iter_mut() {
            let position = match wanted {
                Some(energy_type) => pool.iter().position(|e| *e == energy_type),
                None => (!pool.is_empty()).then_some(0),
            };
            if let Some(position) = position {
                let energy = pool.remove(position);
                match taken.iter_mut().find(|(existing, _)| existing == idx) {
                    Some((_, bucket)) => bucket.push(energy),
                    None => taken.push((*idx, vec![energy])),
                }
                return true;
            }
        }
        false
    };

    for energy_type in missing.iter().filter(|e| **e != EnergyType::Colorless) {
        if !take(&mut pools, &mut taken, Some(*energy_type)) {
            return None;
        }
    }
    for _ in missing.iter().filter(|e| **e == EnergyType::Colorless) {
        if !take(&mut pools, &mut taken, None) {
            return None;
        }
    }

    if taken.is_empty() {
        return None;
    }
    taken.sort_by_key(|(idx, _)| *idx);
    for (_, bucket) in taken.iter_mut() {
        bucket.sort_by_key(|e| format!("{e:?}"));
    }
    Some(taken)
}

/// Candidate lists are short, so a linear duplicate check is cheaper than hashing — and it keeps
/// the list in generation order, which keeps the search deterministic.
fn push_unique(candidates: &mut Vec<SimpleAction>, candidate: SimpleAction) {
    if !candidates.contains(&candidate) {
        candidates.push(candidate);
    }
}
