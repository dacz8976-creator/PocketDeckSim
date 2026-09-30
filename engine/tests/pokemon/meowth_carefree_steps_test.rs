use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game, State,
};

/// Meowth's "Carefree Steps": "If any damage is done to this Pokémon by attacks, flip a coin. If
/// heads, prevent that damage."
///
/// The key behavior (and the bug this fixes): on a heads flip only the *damage* to Meowth is
/// prevented — the rest of the attack (here, the Poison from Grimer's Poison Gas) still happens.
/// Previously the heads branch dropped the whole attack, including its effects.
///
/// We drive the attack across many RNG seeds and assert:
/// - Meowth is ALWAYS poisoned (the secondary effect resolves regardless of the coin), and
/// - Meowth's remaining HP is sometimes full (heads, damage prevented) and sometimes reduced
///   (tails, 10 damage), proving the prevention coin actually fires.
#[test]
fn test_meowth_carefree_steps_prevents_only_damage_not_effects() {
    let mut saw_prevented = false;
    let mut saw_damaged = false;

    for seed in 0..40u64 {
        // Grimer (attacker) vs Meowth with Carefree Steps (defender).
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A1174Grimer).with_energy(vec![EnergyType::Darkness])],
            vec![PlayedCard::from_id(CardId::B2124Meowth)],
        );

        // Poison Gas: 10 damage and the opponent's Active Pokémon is now Poisoned.
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::A1174Grimer, 0),
            is_stack: false,
        });

        let state = game.get_state_clone();
        let meowth = state.get_active(1);

        // The Poison effect must always land, even on the heads (damage-prevented) branch.
        assert!(
            meowth.is_poisoned(),
            "seed {seed}: Meowth should be Poisoned even when its damage is prevented"
        );

        match meowth.get_remaining_hp() {
            50 => saw_prevented = true, // Heads: damage to Meowth prevented.
            40 => saw_damaged = true,   // Tails: 10 damage dealt.
            other => panic!("seed {seed}: unexpected Meowth HP {other}"),
        }
    }

    assert!(
        saw_prevented,
        "expected at least one seed where Carefree Steps prevented the damage"
    );
    assert!(
        saw_damaged,
        "expected at least one seed where the damage went through"
    );
}

/// Carefree Steps applies wherever the Meowth is — including the Bench — and each Meowth flips
/// its own independent coin. Palkia ex's Dimensional Storm does 150 to the Active and 20 to every
/// Benched Pokémon, so against two Benched Meowth there should be two independent coin flips.
///
/// Across seeds we expect to observe every combination — both prevented, both hit, and (crucially)
/// the mixed cases where one Meowth is prevented and the other is not. A single shared coin could
/// never produce a mixed outcome, so seeing one proves the flips are independent and per-Pokémon.
#[test]
fn test_carefree_steps_applies_to_benched_meowth_with_independent_flips() {
    let mut saw_both_prevented = false;
    let mut saw_both_hit = false;
    let mut saw_mixed = false;

    for seed in 0..60u64 {
        // Palkia ex (attacker) vs a tanky Active (survives 150) backed by two Benched Meowth.
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A2049PalkiaEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
            ])],
            vec![
                // 190 HP, survives the 150 so no promotion muddies the bench slots.
                PlayedCard::from_id(CardId::A1004VenusaurEx),
                PlayedCard::from_id(CardId::B2124Meowth),
                PlayedCard::from_id(CardId::B2124Meowth),
            ],
        );

        // Dimensional Storm is Palkia ex's second attack (index 1).
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::A2049PalkiaEx, 1),
            is_stack: false,
        });

        let state = game.get_state_clone();

        // The Active (no Carefree Steps) always takes the full 150.
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            190 - 150,
            "seed {seed}: opponent Active should always take full Dimensional Storm damage"
        );

        // Each Benched Meowth is either untouched (50) or took 20 (30).
        let hp1 = state.in_play_pokemon[1][1]
            .as_ref()
            .expect("first Benched Meowth should still be in play")
            .get_remaining_hp();
        let hp2 = state.in_play_pokemon[1][2]
            .as_ref()
            .expect("second Benched Meowth should still be in play")
            .get_remaining_hp();

        for hp in [hp1, hp2] {
            assert!(
                hp == 50 || hp == 30,
                "seed {seed}: unexpected Benched Meowth HP {hp}"
            );
        }

        match (hp1, hp2) {
            (50, 50) => saw_both_prevented = true,
            (30, 30) => saw_both_hit = true,
            _ => saw_mixed = true,
        }
    }

    assert!(
        saw_both_prevented,
        "expected a seed where both Benched Meowth prevented the damage"
    );
    assert!(
        saw_both_hit,
        "expected a seed where both Benched Meowth took the damage"
    );
    assert!(
        saw_mixed,
        "expected a mixed seed (one Meowth prevented, one not), proving two independent coin flips"
    );
}

/// Carefree Steps flips for damage an attack deals through a queued choice too (rules/09, "Open engine bugs",
/// repaired Sept 30). Player 1 has a Meowth (B2 124) at `meowth_slot`; player 0 uses `attack`, and every queued choice
/// is steered at Meowth (the queued damage, or the switch that brings Meowth in). Over 60 seeds Meowth must sometimes
/// take nothing (heads) and sometimes take the damage (tails, or a Knock Out).
fn queued_damage_flips_carefree_steps(attacker: PlayedCard, attack: (CardId, usize), defender: Vec<PlayedCard>) {
    queued_damage_flips_carefree_steps_from(vec![attacker], attack, defender, false);
}

/// As `queued_damage_flips_carefree_steps`, from a whole attacker board; with `discard`, a Chase Order choice that
/// discards a Benched Pokemon is taken first.
fn queued_damage_flips_carefree_steps_from(
    attacker: Vec<PlayedCard>,
    attack: (CardId, usize),
    defender: Vec<PlayedCard>,
    discard: bool,
) {
    fn meowth(state: &State) -> Option<(usize, u32)> {
        state
            .enumerate_in_play_pokemon(1)
            .find(|(_, p)| p.get_name() == "Meowth")
            .map(|(idx, p)| (idx, p.get_remaining_hp()))
    }
    let (mut prevented, mut hit) = (0, 0);
    for seed in 0..60u64 {
        let mut game: Game = get_initialized_game_with_board(seed, 0, 5, attacker.clone(), defender.clone());
        let (_, before) = meowth(&game.get_state_clone()).expect("Meowth is in play");
        game.apply_action(&Action { actor: 0, action: attack_action(attack.0, attack.1), is_stack: false });
        for _ in 0..10 {
            let state = game.get_state_clone();
            if state.move_generation_stack.is_empty() {
                break;
            }
            let (actor, choices) = state.generate_possible_actions();
            if actor != 0 || choices.is_empty() {
                break;
            }
            let slot = meowth(&state).map(|(idx, _)| idx);
            let aimed = choices.iter().find(|choice| match &choice.action {
                SimpleAction::ApplyDamage { targets, .. } => targets.iter().any(|(_, p, i)| *p == 1 && Some(*i) == slot),
                SimpleAction::ApplyQueuedAttackDamage { targets, .. } => targets.iter().any(|(_, opp, i)| *opp && Some(*i) == slot),
                SimpleAction::Activate { player: 1, in_play_idx } => Some(*in_play_idx) == slot,
                _ => false,
            });
            let discarding = choices.iter().find(|choice| {
                matches!(&choice.action, SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } if !in_play_idxs.is_empty())
            });
            let pick = if discard { discarding.or(aimed) } else { aimed };
            game.apply_action(pick.unwrap_or(&choices[0]));
        }
        match meowth(&game.get_state_clone()) {
            Some((_, after)) if after == before => prevented += 1,
            _ => hit += 1,
        }
    }
    assert!(prevented > 10 && hit > 10, "{prevented} prevented, {hit} hit: the coin must flip");
}

#[test]
fn carefree_steps_flips_for_a_direct_damage_snipe() {
    // Heatmor's Tongue Whip: 30 to 1 of the opponent's Benched Pokemon (DirectDamage).
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire]),
        (CardId::B1044Heatmor, 0),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::B2124Meowth)],
    );
}

#[test]
fn carefree_steps_flips_for_direct_damage_to_a_damaged_pokemon() {
    // Decidueye ex's Pierce the Pain: 100 to 1 of the opponent's Pokemon that have damage on them.
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::A3012DecidueyeEx).with_energy(vec![EnergyType::Grass; 2]),
        (CardId::A3012DecidueyeEx, 0),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::B2124Meowth).with_remaining_hp(40)],
    );
}

#[test]
fn carefree_steps_flips_for_damage_after_discarding_all_energy_of_a_type() {
    // Chien-Pao ex's Diving Icicles: discard all [W], then 130 to 1 of the opponent's Pokemon.
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::B2a037ChienPaoEx).with_energy(vec![EnergyType::Water; 3]),
        (CardId::B2a037ChienPaoEx, 1),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::B2124Meowth)],
    );
}

#[test]
fn carefree_steps_flips_for_damage_per_energy_on_the_target() {
    // Tapu Lele's Energy Arrow: 20 for each Energy on the chosen Pokemon (Meowth has 1).
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::A3084TapuLele).with_energy(vec![EnergyType::Psychic]),
        (CardId::A3084TapuLele, 0),
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B2124Meowth).with_energy(vec![EnergyType::Colorless]),
        ],
    );
}

#[test]
fn carefree_steps_flips_for_damage_after_discarding_energy() {
    // Volcarona's Volcanic Ash: discard 2 [R], then 80 to 1 of the opponent's Pokemon.
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::A1a014Volcarona).with_energy(vec![EnergyType::Fire; 3]),
        (CardId::A1a014Volcarona, 0),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::B2124Meowth)],
    );
}

#[test]
fn carefree_steps_flips_for_damage_to_the_pokemon_switched_in() {
    // Sandy Shocks's Pull In and Pound: switch in 1 of the opponent's Benched Pokemon, then 50 to it.
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::B3a035SandyShocks).with_energy(vec![EnergyType::Fighting; 3]),
        (CardId::B3a035SandyShocks, 0),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::B2124Meowth)],
    );
}

/// The repair's gate: only a snipe at a Pokemon with a coin Ability takes the coin-flipping path
/// (`ApplyQueuedAttackDamage`); a snipe at any other Pokemon is queued exactly as before (`ApplyDamage`).
#[test]
fn only_a_snipe_at_a_coin_ability_pokemon_takes_the_coin_path() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        5,
        vec![PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire])],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B2124Meowth),
        ],
    );
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B1044Heatmor, 0), is_stack: false });
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let target = |choice: &Action| match &choice.action {
        SimpleAction::ApplyDamage { targets, .. } => Some(("ApplyDamage", targets[0].2)),
        SimpleAction::ApplyQueuedAttackDamage { targets, .. } => Some(("ApplyQueuedAttackDamage", targets[0].2)),
        _ => None,
    };
    let kinds: Vec<_> = choices.iter().filter_map(target).collect();
    assert_eq!(kinds, vec![("ApplyDamage", 1), ("ApplyQueuedAttackDamage", 2)]);
}

/// Vespiquen ex's Chase Order (70; 140 if a Benched Basic [G] Pokemon is discarded) into a Meowth with Carefree Steps:
/// the damage is queued after the choice, and the coin flips for it (Dustin, Sept 30: fix Chase Order now).
#[test]
fn carefree_steps_flips_for_chase_order_without_the_discard() {
    queued_damage_flips_carefree_steps_from(
        vec![
            PlayedCard::from_id(CardId::B4011VespiquenEx).with_energy(vec![EnergyType::Grass; 2]),
            PlayedCard::from_id(CardId::B4010Combee),
        ],
        (CardId::B4011VespiquenEx, 0),
        vec![PlayedCard::from_id(CardId::B2124Meowth)],
        false,
    );
}

#[test]
fn carefree_steps_flips_for_chase_order_with_the_discard() {
    queued_damage_flips_carefree_steps_from(
        vec![
            PlayedCard::from_id(CardId::B4011VespiquenEx).with_energy(vec![EnergyType::Grass; 2]),
            PlayedCard::from_id(CardId::B4010Combee),
        ],
        (CardId::B4011VespiquenEx, 0),
        vec![PlayedCard::from_id(CardId::B2124Meowth)],
        true,
    );
}

/// Chase Order's control (the repair's gate): into a Pokemon without a coin Ability (Mega Latios ex, 180 HP, no
/// Weakness), both choices resolve exactly as before: the damage is queued as `ApplyDamage` and does 70 without the
/// discard, 140 with it.
#[test]
fn chase_order_into_a_pokemon_without_a_coin_ability_is_unchanged() {
    for discard in [false, true] {
        for seed in 0..10u64 {
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                5,
                vec![
                    PlayedCard::from_id(CardId::B4011VespiquenEx).with_energy(vec![EnergyType::Grass; 2]),
                    PlayedCard::from_id(CardId::B4010Combee),
                ],
                vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
            );
            game.apply_action(&Action { actor: 0, action: attack_action(CardId::B4011VespiquenEx, 0), is_stack: false });
            let (_, choices) = game.get_state_clone().generate_possible_actions();
            let pick = choices
                .iter()
                .find(|choice| match &choice.action {
                    SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } => discard && !in_play_idxs.is_empty(),
                    SimpleAction::ApplyDamage { .. } | SimpleAction::ApplyQueuedAttackDamage { .. } => !discard,
                    _ => false,
                })
                .expect("Chase Order offers both choices")
                .clone();
            game.apply_action(&pick);
            if discard {
                let (_, queued) = game.get_state_clone().generate_possible_actions();
                assert_eq!(queued.len(), 1, "seed {seed}");
                assert!(matches!(queued[0].action, SimpleAction::ApplyDamage { .. }), "seed {seed}: {:?}", queued[0].action);
                game.apply_action(&queued[0]);
            } else {
                assert!(matches!(pick.action, SimpleAction::ApplyDamage { .. }), "seed {seed}: {:?}", pick.action);
            }
            let dealt = 180 - game.get_state_clone().get_active(1).get_remaining_hp();
            assert_eq!(dealt, if discard { 140 } else { 70 }, "seed {seed}, discard {discard}");
        }
    }
}
