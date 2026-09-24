//! Physical Energy payments selected by the acting player.
use std::collections::BTreeMap;

use crate::models::EnergyType;

fn grouped(energies: &[EnergyType]) -> Vec<(EnergyType, usize)> {
    let mut counts = BTreeMap::<EnergyType, usize>::new();
    for energy in energies {
        *counts.entry(*energy).or_default() += 1;
    }
    counts.into_iter().collect()
}

/// Exact, distinct multisets of attached Energy. Identical physical copies are one choice.
pub(crate) fn attack_discard_choices(energies: &[EnergyType], count: usize) -> Vec<Vec<EnergyType>> {
    let count = count.min(energies.len());
    let types = grouped(energies);
    let mut output = Vec::new();
    fn enumerate(
        types: &[(EnergyType, usize)], index: usize, remaining: usize,
        picked: &mut Vec<EnergyType>, output: &mut Vec<Vec<EnergyType>>,
    ) {
        if index == types.len() {
            if remaining == 0 { output.push(picked.clone()); }
            return;
        }
        let (energy, available) = types[index];
        for take in 0..=available.min(remaining) {
            picked.extend(std::iter::repeat_n(energy, take));
            enumerate(types, index + 1, remaining - take, picked, output);
            picked.truncate(picked.len() - take);
        }
    }
    enumerate(&types, 0, count, &mut Vec::new(), &mut output);
    output
}

/// Payments that cover the effective Colorless retreat cost without discarding extra Energy.
/// Jungle Totem makes one physical Grass attachment pay two symbols for a Grass Pokemon.
pub(crate) fn retreat_payment_choices(
    energies: &[EnergyType], cost: usize, double_grass: bool,
) -> Vec<Vec<EnergyType>> {
    let types = grouped(energies);
    let mut output = Vec::new();
    fn value(energy: EnergyType, double_grass: bool) -> usize {
        if double_grass && energy == EnergyType::Grass { 2 } else { 1 }
    }
    fn enumerate(
        types: &[(EnergyType, usize)], index: usize, slots: usize,
        cost: usize, double_grass: bool, picked: &mut Vec<EnergyType>,
        output: &mut Vec<Vec<EnergyType>>,
    ) {
        if index == types.len() {
            let paid: usize = picked.iter().copied().map(|e| value(e, double_grass)).sum();
            if paid >= cost && !picked.iter().any(|e| paid - value(*e, double_grass) >= cost) {
                output.push(picked.clone());
            }
            return;
        }
        let (energy, available) = types[index];
        for take in 0..=available.min(slots) {
            picked.extend(std::iter::repeat_n(energy, take));
            enumerate(types, index + 1, slots - take, cost, double_grass, picked, output);
            picked.truncate(picked.len() - take);
        }
    }
    enumerate(&types, 0, cost.min(energies.len()), cost, double_grass, &mut Vec::new(), &mut output);
    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unique_choices_on_large_attachment_stack() {
        let energies = [vec![EnergyType::Fire; 30], vec![EnergyType::Water; 30]].concat();
        let mut retreat = retreat_payment_choices(&energies, 1, false);
        retreat.sort();
        assert_eq!(retreat, vec![vec![EnergyType::Fire], vec![EnergyType::Water]]);
        let mut attack = attack_discard_choices(&energies, 2);
        attack.sort();
        assert_eq!(attack, vec![vec![EnergyType::Fire, EnergyType::Fire],
                                vec![EnergyType::Fire, EnergyType::Water],
                                vec![EnergyType::Water, EnergyType::Water]]);
    }

    #[test]
    fn doubled_grass_covers_two_with_one_attachment() {
        let energies = [EnergyType::Grass, EnergyType::Fire, EnergyType::Fire];
        let mut payments = retreat_payment_choices(&energies, 2, true);
        payments.sort();
        assert_eq!(payments, vec![vec![EnergyType::Grass], vec![EnergyType::Fire, EnergyType::Fire]]);
    }
}
