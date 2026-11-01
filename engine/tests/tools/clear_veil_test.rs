//! Clear Veil (B4 149): "Prevent all effects of attacks used by your opponent's Pokémon done to
//! the Pokémon this card is attached to." Discarding Energy from the holder is such an effect; the
//! shield is `State::prevents_attack_effects`, checked where each discard outcome is built.
//!
//! The first two tests are upstream's from #427 (dadf3be); the others cover the remaining discard
//! routes that commit touched: Mawile's Crunch, the typed discards, and Twister, Triple Gnawing and
//! Sudden Drilling, which upstream sends through the one discard #427 shielded. Hyper Whirlpool's
//! case is `clear_veil_blocks_hyper_whirlpool_energy_effect_but_not_damage` in
//! `pokemon/attack_geometric_completion_test.rs`.

use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

fn attack(game: &mut Game<'static>, actor: usize, card_id: CardId, index: usize) {
    game.apply_action(&Action {
        actor,
        action: attack_action(card_id, index),
        is_stack: false,
    });
}

/// Clear Veil also prevents an opponent's attack from discarding Energy from the holder (Beedrill
/// ex's Crushing Spear: "Discard a random Energy from your opponent's Active Pokémon."), while
/// the attack's damage still goes through. Oricorio's Kindle discards from both Active Pokémon:
/// the attacker still loses its own Energy.
#[test]
fn test_clear_veil_prevents_energy_discard_from_an_opponents_attack() {
    let after_attack = |veil: bool, attacker: PlayedCard, attacker_id: CardId| {
        let mut defender = PlayedCard::from_id(CardId::A1202Chansey)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
        if veil {
            defender = defender.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
        }
        let mut game = get_initialized_game_with_board(0, 1, 3, vec![defender], vec![attacker]);
        attack(&mut game, 1, attacker_id, 0);
        game.play_until_stable();
        let state = game.get_state_clone();
        (
            state.get_active(0).attached_energy.len(),
            state.get_active(0).get_remaining_hp(),
            state.get_active(1).attached_energy.len(),
        )
    };
    let beedrill = || {
        PlayedCard::from_id(CardId::A2b003BeedrillEx)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])
    };
    assert_eq!(
        after_attack(false, beedrill(), CardId::A2b003BeedrillEx),
        (1, 40, 2)
    );
    assert_eq!(
        after_attack(true, beedrill(), CardId::A2b003BeedrillEx),
        (2, 40, 2)
    );

    let oricorio = || {
        PlayedCard::from_id(CardId::A3034Oricorio)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire])
    };
    assert_eq!(
        after_attack(false, oricorio(), CardId::A3034Oricorio),
        (1, 80, 1)
    );
    assert_eq!(
        after_attack(true, oricorio(), CardId::A3034Oricorio),
        (2, 80, 1)
    );
}

/// Same for the single coin-flip discard (Drednaw's Crunch: "Flip a coin. If heads, discard a
/// random Energy from your opponent's Active Pokémon."): over many seeds the Energy is discarded on
/// heads without Clear Veil, and never with it.
#[test]
fn test_clear_veil_prevents_coin_flip_energy_discard_from_an_opponents_attack() {
    let energies_after = |seed: u64, veil: bool| {
        let mut defender = PlayedCard::from_id(CardId::A1202Chansey)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
        if veil {
            defender = defender.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
        }
        let drednaw = PlayedCard::from_id(CardId::A1a023Drednaw).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Water,
        ]);
        let mut game = get_initialized_game_with_board(seed, 1, 3, vec![defender], vec![drednaw]);
        attack(&mut game, 1, CardId::A1a023Drednaw, 0);
        game.play_until_stable();
        game.get_state_clone().get_active(0).attached_energy.len()
    };
    let without_veil: Vec<usize> = (0..40).map(|seed| energies_after(seed, false)).collect();
    assert!(
        without_veil.contains(&1) && without_veil.contains(&2),
        "Crunch should discard on heads and not on tails: {without_veil:?}"
    );
    assert!(
        (0..40).all(|seed| energies_after(seed, true) == 2),
        "Clear Veil should keep the Energy on heads too"
    );
}

/// Mawile's Crunch (A1 178) has Drednaw's text, so here it takes the same route
/// (`coin_flip_discard_opponent_active_energy`); upstream sends this text (Drednaw's too) to
/// `mawile_crunch`, which hard-codes 20 damage, and #427 moved that onto the shielded discard. The
/// 20 damage lands on both faces; without Clear Veil a heads sends the Energy to the discard pile,
/// and with it the Energy never moves.
#[test]
fn test_clear_veil_prevents_mawile_crunch_energy_discard() {
    let after_attack = |seed: u64, veil: bool| {
        let mut defender = PlayedCard::from_id(CardId::A1202Chansey)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
        if veil {
            defender = defender.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
        }
        let mawile = PlayedCard::from_id(CardId::A1178Mawile).with_energy(vec![EnergyType::Metal]);
        let mut game = get_initialized_game_with_board(seed, 1, 3, vec![defender], vec![mawile]);
        attack(&mut game, 1, CardId::A1178Mawile, 0);
        game.play_until_stable();
        let state = game.get_state_clone();
        (
            state.get_active(0).attached_energy.len(),
            state.discard_energies[0].len(),
            state.get_active(0).get_remaining_hp(),
        )
    };
    let without_veil: Vec<(usize, usize, u32)> =
        (0..40).map(|seed| after_attack(seed, false)).collect();
    assert!(
        without_veil.contains(&(1, 1, 100)) && without_veil.contains(&(2, 0, 100)),
        "Crunch should discard on heads and not on tails: {without_veil:?}"
    );
    assert!(
        (0..40).all(|seed| after_attack(seed, true) == (2, 0, 100)),
        "Clear Veil should keep the Energy on heads too"
    );
}

/// The typed discards too (Dedenne's Electric Nibbling: "Discard a [L] Energy from your
/// opponent's Active Pokémon."; Surskit's Firefighting, the same with [R]). Upstream's
/// `damage_and_discard_opponent_active_energy_of_type` is our
/// `discard_type_energy_from_opponent_active`.
#[test]
fn test_clear_veil_prevents_typed_energy_discard_from_an_opponents_attack() {
    let after_attack = |veil: bool, attacker_id: CardId, energy_type: EnergyType| {
        let mut defender = PlayedCard::from_id(CardId::A1202Chansey)
            .with_energy(vec![energy_type, EnergyType::Colorless]);
        if veil {
            defender = defender.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
        }
        let attacker = PlayedCard::from_id(attacker_id).with_energy(vec![EnergyType::Colorless]);
        let mut game = get_initialized_game_with_board(0, 1, 3, vec![defender], vec![attacker]);
        attack(&mut game, 1, attacker_id, 0);
        game.play_until_stable();
        let state = game.get_state_clone();
        (
            state.get_active(0).attached_energy.clone(),
            state.get_active(0).get_remaining_hp(),
        )
    };
    assert_eq!(
        after_attack(false, CardId::B1094Dedenne, EnergyType::Lightning),
        (vec![EnergyType::Colorless], 100)
    );
    assert_eq!(
        after_attack(true, CardId::B1094Dedenne, EnergyType::Lightning),
        (vec![EnergyType::Lightning, EnergyType::Colorless], 100)
    );
    assert_eq!(
        after_attack(false, CardId::B3009Surskit, EnergyType::Fire),
        (vec![EnergyType::Colorless], 110)
    );
    assert_eq!(
        after_attack(true, CardId::B3009Surskit, EnergyType::Fire),
        (vec![EnergyType::Fire, EnergyType::Colorless], 110)
    );
}

/// And the per-heads and evolved-this-turn discards (Pidgeot's Twister: "Flip 2 coins. For each
/// heads, discard a random Energy from your opponent's Active Pokémon. If both of them are tails,
/// this attack does nothing."; Maushold's Triple Gnawing, 3 coins and no all-tails clause;
/// Dudunsparce's Sudden Drilling: "If this Pokémon evolved from Dunsparce during this turn, discard
/// 2 random Energy from your opponent's Active Pokémon."). Upstream sends all three through
/// `discard_random_energy_from_opponent_active`; ours are
/// `flip_coins_discard_opponent_energy_per_heads` and
/// `discard_opponent_active_energy_if_evolved_this_turn`.
#[test]
fn test_clear_veil_prevents_per_heads_and_evolved_energy_discards() {
    let after_attack = |seed: u64, veil: bool, attacker: PlayedCard, attacker_id: CardId| {
        let mut defender = PlayedCard::from_id(CardId::A1202Chansey)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
        if veil {
            defender = defender.with_tool(get_card_by_enum(CardId::B4149ClearVeil));
        }
        let mut game = get_initialized_game_with_board(seed, 1, 3, vec![defender], vec![attacker]);
        attack(&mut game, 1, attacker_id, 0);
        game.play_until_stable();
        let state = game.get_state_clone();
        (
            state.get_active(0).attached_energy.len(),
            state.get_active(0).get_remaining_hp(),
        )
    };
    let attacker = |card_id: CardId| {
        PlayedCard::from_id(card_id)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])
    };

    // Twister (80) and Triple Gnawing (60): over many seeds some heads discards without Clear
    // Veil; with it no seed discards, and the damage still lands.
    let coin_attackers = [(CardId::B1182Pidgeot, 40), (CardId::B2a082Maushold, 60)];
    for (attacker_id, hp_after_heads) in coin_attackers {
        let without_veil: Vec<(usize, u32)> = (0..40)
            .map(|seed| after_attack(seed, false, attacker(attacker_id), attacker_id))
            .collect();
        assert!(
            without_veil
                .iter()
                .any(|&(energy, hp)| energy < 2 && hp == hp_after_heads),
            "{attacker_id:?} should discard on heads: {without_veil:?}"
        );
        let with_veil: Vec<(usize, u32)> = (0..40)
            .map(|seed| after_attack(seed, true, attacker(attacker_id), attacker_id))
            .collect();
        assert!(
            with_veil.contains(&(2, hp_after_heads))
                && with_veil.iter().all(|&(energy, _)| energy == 2),
            "Clear Veil should keep the Energy against {attacker_id:?}: {with_veil:?}"
        );
    }

    // Sudden Drilling from a Dudunsparce that evolved this turn: both Energy without Clear Veil,
    // none with it; 60 damage either way.
    let dudunsparce = || {
        let mut dudunsparce = attacker(CardId::B3a060Dudunsparce);
        dudunsparce.played_this_turn = true;
        dudunsparce
    };
    assert_eq!(
        after_attack(0, false, dudunsparce(), CardId::B3a060Dudunsparce),
        (0, 60)
    );
    assert_eq!(
        after_attack(0, true, dudunsparce(), CardId::B3a060Dudunsparce),
        (2, 60)
    );
}
