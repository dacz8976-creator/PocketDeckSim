use crate::{models::EnergyType, State};

/// The Pokémon Mallow can fully heal.
const MALLOW_TARGET_NAMES: [&str; 2] = ["Shiinotic", "Tsareena"];

/// Mallow (A3 154): "Heal all damage from 1 of your Shiinotic or Tsareena. If you do, discard all
/// Energy from that Pokémon."
///
/// Returns `(in_play_idx, damage_to_heal, energy_to_discard)` for each legal target. Both the heal
/// amount and the Energy list are read off the Pokémon here so the queued choice can stay a plain
/// deterministic `HealAndDiscardEnergy`. Undamaged Pokémon are excluded: there is no "if you do",
/// so they would only lose their Energy for nothing.
pub fn mallow_targets(state: &State, player: usize) -> Vec<(usize, u32, Vec<EnergyType>)> {
    state
        .enumerate_in_play_pokemon(player)
        .filter(|(_, pokemon)| MALLOW_TARGET_NAMES.contains(&pokemon.get_name().as_str()))
        .filter(|(_, pokemon)| pokemon.is_damaged())
        .map(|(in_play_idx, pokemon)| {
            let damage = pokemon
                .get_effective_total_hp()
                .saturating_sub(pokemon.get_remaining_hp());
            (in_play_idx, damage, pokemon.attached_energy.clone())
        })
        .collect()
}
