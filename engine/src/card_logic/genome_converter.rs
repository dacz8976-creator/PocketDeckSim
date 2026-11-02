use crate::{models::EnergyType, State};

/// Genome Converter Y (P-C 009): "Move all [P] Energy from 1 of your Benched [P] Pokémon to your
/// Mega Mewtwo Y ex in the Active Spot." The sources, as `(bench index, [P] Energy count)`: each
/// Benched Pokémon that is [P] in play (`State::pokemon_is_type`, so a [P]/[F] Mega Mewtwo X ex
/// counts) and holds at least one [P] Energy. Empty unless `player`'s Active Pokémon is a Mega
/// Mewtwo Y ex.
pub fn genome_converter_y_sources(state: &State, player: usize) -> Vec<(usize, u32)> {
    let active_is_mega_mewtwo_y = state
        .maybe_get_active(player)
        .is_some_and(|active| active.get_name() == "Mega Mewtwo Y ex");
    if !active_is_mega_mewtwo_y {
        return vec![];
    }
    state
        .enumerate_bench_pokemon(player)
        .filter(|(_, pokemon)| state.pokemon_is_type(pokemon, EnergyType::Psychic))
        .map(|(in_play_idx, pokemon)| {
            let count = pokemon
                .attached_energy
                .iter()
                .filter(|e| **e == EnergyType::Psychic)
                .count() as u32;
            (in_play_idx, count)
        })
        .filter(|(_, count)| *count > 0)
        .collect()
}
