use crate::State;

/// Whitney (A4a 069): "Heal 60 damage from 1 of your Miltank, and it recovers from being Asleep,
/// Paralyzed, and Confused."
///
/// A Miltank with no damage and none of those conditions would gain nothing, so it is not offered
/// as a target — this also keeps Whitney out of move generation on a board where it would do
/// nothing at all (mirroring Pokémon Center Lady).
pub fn whitney_targets(state: &State, player: usize) -> Vec<usize> {
    state
        .enumerate_in_play_pokemon(player)
        .filter(|(_, pokemon)| pokemon.get_name() == "Miltank")
        .filter(|(_, pokemon)| {
            pokemon.is_damaged()
                || pokemon.is_asleep()
                || pokemon.is_paralyzed()
                || pokemon.is_confused()
        })
        .map(|(in_play_idx, _)| in_play_idx)
        .collect()
}
