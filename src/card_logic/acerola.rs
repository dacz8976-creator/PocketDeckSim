use crate::State;

/// The Pokémon Acerola can move damage off.
const ACEROLA_TARGET_NAMES: [&str; 2] = ["Palossand", "Mimikyu"];

/// Acerola (A3 148): "Choose 1 of your Palossand or Mimikyu that has damage on it, and move 40 of
/// its damage to your opponent's Active Pokémon."
///
/// Only Pokémon that actually carry damage are offered, matching "that has damage on it".
pub fn acerola_targets(state: &State, player: usize) -> Vec<usize> {
    state
        .enumerate_in_play_pokemon(player)
        .filter(|(_, pokemon)| ACEROLA_TARGET_NAMES.contains(&pokemon.get_name().as_str()))
        .filter(|(_, pokemon)| pokemon.is_damaged())
        .map(|(in_play_idx, _)| in_play_idx)
        .collect()
}
