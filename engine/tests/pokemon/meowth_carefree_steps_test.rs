use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
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
    let (prevented, hit) = carefree_steps_counts(attacker, attack, defender, discard);
    assert!(prevented > 10 && hit > 10, "{prevented} prevented, {hit} hit: the coin must flip");
}

/// Over 60 seeds, how often Meowth took none of the attack's damage (prevented) and how often it took some (hit).
fn carefree_steps_counts(
    attacker: Vec<PlayedCard>,
    attack: (CardId, usize),
    defender: Vec<PlayedCard>,
    discard: bool,
) -> (usize, usize) {
    let (mut prevented, mut hit) = (0, 0);
    for seed in 0..60u64 {
        match carefree_steps_seed(seed, &attacker, attack, &defender, discard, &[]) {
            (_, true) => prevented += 1,
            (_, false) => hit += 1,
        }
    }
    (prevented, hit)
}

/// One seed of `carefree_steps_counts`, with the Tool cards in `hand` put in player 0's hand first (for Slowking's
/// Litter, whose largest discard is chosen). Returns whether a queued choice aimed at Meowth was offered, and whether
/// Meowth took none of the attack's damage.
fn carefree_steps_seed(
    seed: u64,
    attacker: &[PlayedCard],
    attack: (CardId, usize),
    defender: &[PlayedCard],
    discard: bool,
    hand: &[CardId],
) -> (bool, bool) {
    fn meowth(state: &State) -> Option<(usize, u32)> {
        state
            .enumerate_in_play_pokemon(1)
            .find(|(_, p)| p.get_name() == "Meowth")
            .map(|(idx, p)| (idx, p.get_remaining_hp()))
    }
    let mut game: Game = get_initialized_game_with_board(seed, 0, 5, attacker.to_vec(), defender.to_vec());
    if !hand.is_empty() {
        let mut state = game.get_state_clone();
        state.hands[0] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        game.set_state(state);
    }
    let (_, before) = meowth(&game.get_state_clone()).expect("Meowth is in play");
    game.apply_action(&Action { actor: 0, action: attack_action(attack.0, attack.1), is_stack: false });
    let mut queued = false;
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
        queued |= aimed.is_some();
        let discarding = choices.iter().find(|choice| {
            matches!(&choice.action, SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } if !in_play_idxs.is_empty())
        });
        let litter = choices
            .iter()
            .filter_map(|choice| match &choice.action {
                SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. } => Some((cards.len(), choice)),
                _ => None,
            })
            .max_by_key(|(n, _)| *n)
            .map(|(_, choice)| choice);
        let pick = if discard { discarding.or(aimed) } else { aimed }.or(litter);
        game.apply_action(pick.unwrap_or(&choices[0]));
    }
    let unhurt = matches!(meowth(&game.get_state_clone()), Some((_, after)) if after == before);
    (queued, unhurt)
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

/// Gyarados's Wild Swing (20, and 40 more for each Benched [W] Pokemon discarded) queues its damage through the
/// discard action it shares with Chase Order. Sonnet's S2 (Sept 30) pinned the gap here (no coin, 0 prevented of 60);
/// the later round (Oct 1) repairs it, so the coin flips with and without the discard, as for Chase Order.
#[test]
fn carefree_steps_flips_for_wild_swing() {
    for discard in [false, true] {
        let (prevented, hit) = carefree_steps_counts(
            vec![
                PlayedCard::from_id(CardId::A4045Gyarados).with_energy(vec![EnergyType::Water; 2]),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
            (CardId::A4045Gyarados, 0),
            vec![PlayedCard::from_id(CardId::B2124Meowth)],
            discard,
        );
        assert!(prevented > 10 && hit > 10, "discard {discard}: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

/// The later round of coin-flip prevention (Oct 1; the README's "Recorded for a later round"): six more attacks deliver
/// damage through a queued choice, and the coin now flips for each. Meowth (B2 124) stands where the queued damage
/// lands: on the Bench, or in the Active Spot when the Active's hit is queued too.
fn bulbasaur() -> PlayedCard {
    PlayedCard::from_id(CardId::A1001Bulbasaur)
}

fn meowth() -> PlayedCard {
    PlayedCard::from_id(CardId::B2124Meowth)
}

/// Wellspring Mask Ogerpon's Wellspring Dance (40; heads: also 40 to 1 of the opponent's Benched Pokemon). On heads both
/// hits are queued in one choice, so only the seeds whose attack coin was heads are counted.
#[test]
fn carefree_steps_flips_for_wellspring_dance_on_its_heads() {
    let attacker = vec![PlayedCard::from_id(CardId::B2048WellspringMaskOgerpon).with_energy(vec![EnergyType::Water; 2])];
    for defender in [vec![bulbasaur(), meowth()], vec![meowth(), bulbasaur()]] {
        let (mut prevented, mut hit) = (0, 0);
        for seed in 0..80u64 {
            match carefree_steps_seed(seed, &attacker, (CardId::B2048WellspringMaskOgerpon, 0), &defender, false, &[]) {
                (true, true) => prevented += 1,
                (true, false) => hit += 1,
                (false, _) => {}
            }
        }
        assert!(prevented > 5 && hit > 5, "{prevented} prevented, {hit} hit on the heads: the coin must flip");
    }
}

#[test]
fn carefree_steps_flips_for_tornado_shot() {
    // Rapid Strike Urshifu's Tornado Shot: discard a [W], 40, and 40 to 1 of the opponent's Benched Pokemon (both
    // hits queued in one choice).
    for defender in [vec![bulbasaur(), meowth()], vec![meowth(), bulbasaur()]] {
        queued_damage_flips_carefree_steps(
            PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu).with_energy(vec![EnergyType::Water; 2]),
            (CardId::B3051RapidStrikeUrshifu, 0),
            defender,
        );
    }
}

#[test]
fn carefree_steps_flips_for_double_splash_and_triple_bombardment() {
    // Blastoise's Double Splash (90; with 2 extra [W], also 50 to 1 Benched Pokemon) and Mega Blastoise ex's Triple
    // Bombardment (130; with 3 extra [W], also 50 to 2 Benched Pokemon).
    for defender in [vec![bulbasaur(), meowth(), bulbasaur()], vec![meowth(), bulbasaur(), bulbasaur()]] {
        queued_damage_flips_carefree_steps(
            PlayedCard::from_id(CardId::B1a019Blastoise).with_energy(vec![EnergyType::Water; 5]),
            (CardId::B1a019Blastoise, 0),
            defender.clone(),
        );
        queued_damage_flips_carefree_steps(
            PlayedCard::from_id(CardId::B1a020MegaBlastoiseEx).with_energy(vec![EnergyType::Water; 6]),
            (CardId::B1a020MegaBlastoiseEx, 0),
            defender,
        );
    }
}

#[test]
fn carefree_steps_flips_for_mischievous_ring() {
    // Hoopa's Mischievous Ring: shuffle the opponent's Tools away (here the Benched Bulbasaur's Giant Cape), then 20 to
    // the Active (queued after the shuffle).
    queued_damage_flips_carefree_steps(
        PlayedCard::from_id(CardId::B4077Hoopa).with_energy(vec![EnergyType::Psychic]),
        (CardId::B4077Hoopa, 0),
        vec![meowth(), bulbasaur().with_tool(get_card_by_enum(CardId::A2147GiantCape))],
    );
}

#[test]
fn carefree_steps_flips_for_litter() {
    // Slowking's Litter: discard up to 2 Tools from the hand, 50 for each (queued after the discard; the largest is
    // chosen, 100).
    let attacker = vec![PlayedCard::from_id(CardId::A4a018Slowking).with_energy(vec![EnergyType::Water])];
    let hand = [CardId::A2147GiantCape, CardId::A2148RockyHelmet];
    let (mut prevented, mut hit) = (0, 0);
    for seed in 0..60u64 {
        match carefree_steps_seed(seed, &attacker, (CardId::A4a018Slowking, 0), &[meowth(), bulbasaur()], false, &hand) {
            (true, true) => prevented += 1,
            (true, false) => hit += 1,
            (false, _) => panic!("seed {seed}: Litter's damage is queued at Meowth"),
        }
    }
    assert!(prevented > 10 && hit > 10, "{prevented} prevented, {hit} hit: the coin must flip");
}

/// Mega Kangaskhan ex's Double-Punching Family: "This attack is used twice in a row. The second attack does 40 damage."
/// Each punch is an attack of its own, so Togekiss's Celestial Blessing flips for each: over 60 seeds the damage is 0, 40,
/// 80 or 120, and the second punch is sometimes prevented (0 or 80) and sometimes not (40 or 120).
#[test]
fn celestial_blessing_flips_for_both_punches_of_double_punching_family() {
    let (mut second_prevented, mut second_hit) = (0, 0);
    for seed in 0..60u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            5,
            vec![PlayedCard::from_id(CardId::B2127MegaKangaskhanEx).with_energy(vec![EnergyType::Colorless; 3])],
            vec![PlayedCard::from_id(CardId::A4080Togekiss), bulbasaur()],
        );
        game.apply_action(&Action { actor: 0, action: attack_action(CardId::B2127MegaKangaskhanEx, 0), is_stack: false });
        for _ in 0..10 {
            let state = game.get_state_clone();
            let (actor, choices) = state.generate_possible_actions();
            if state.move_generation_stack.is_empty() || actor != 0 || choices.is_empty() {
                break;
            }
            game.apply_action(&choices[0]);
        }
        let togekiss = game.get_state_clone().in_play_pokemon[1][0].clone().expect("Togekiss survives 120");
        match 140 - togekiss.get_remaining_hp() {
            0 | 80 => second_prevented += 1,
            40 | 120 => second_hit += 1,
            other => panic!("seed {seed}: {other} damage"),
        }
    }
    assert!(
        second_prevented > 10 && second_hit > 10,
        "second punch: {second_prevented} prevented, {second_hit} hit: the coin must flip for it"
    );
}

/// When the first punch Knocks Out the Active (Bulbasaur, 70 HP), the opponent chooses a new Active first and the second
/// punch lands on it ("... used after your opponent chooses a new Active Pokemon"). Promoting Meowth, its coin flips for
/// the second punch.
#[test]
fn carefree_steps_flips_for_the_second_punch_after_a_knock_out() {
    let (mut prevented, mut hit) = (0, 0);
    for seed in 0..60u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            5,
            vec![PlayedCard::from_id(CardId::B2127MegaKangaskhanEx).with_energy(vec![EnergyType::Colorless; 3])],
            vec![bulbasaur(), meowth()],
        );
        game.apply_action(&Action { actor: 0, action: attack_action(CardId::B2127MegaKangaskhanEx, 0), is_stack: false });
        let mut promoted = false;
        for _ in 0..10 {
            let state = game.get_state_clone();
            if state.move_generation_stack.is_empty() {
                break;
            }
            let (actor, choices) = state.generate_possible_actions();
            if choices.is_empty() {
                break;
            }
            if actor == 1 {
                let promote = choices
                    .iter()
                    .find(|choice| matches!(choice.action, SimpleAction::Promote { player: 1, in_play_idx: 1 }))
                    .expect("player 1 promotes Meowth");
                promoted = true;
                game.apply_action(promote);
                continue;
            }
            // The attack's retaliation step comes first; the second punch's damage must wait for the promotion.
            if matches!(choices[0].action, SimpleAction::ApplyDamage { .. } | SimpleAction::ApplyQueuedAttackDamage { .. }) {
                assert!(promoted, "seed {seed}: the second punch waits for the new Active");
            }
            game.apply_action(&choices[0]);
        }
        assert!(promoted, "seed {seed}: the first punch Knocks Out Bulbasaur");
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_name(), "Meowth", "seed {seed}");
        if state.get_active(1).get_remaining_hp() == 50 {
            prevented += 1;
        } else {
            hit += 1;
        }
    }
    assert!(prevented > 10 && hit > 10, "{prevented} prevented, {hit} hit: the coin must flip for the second punch");
}

/// The later round's gate: a choice takes the coin-flipping path (`ApplyQueuedAttackDamage`) only when one of its
/// targets has a coin-flip damage Ability; every other choice is queued exactly as before (`ApplyDamage`). Tornado Shot
/// queues the Active's hit and a Benched hit together, so a coin Ability in the Active Spot sends every choice there.
#[test]
fn only_a_choice_that_hits_a_coin_ability_pokemon_takes_the_coin_path_in_the_later_round() {
    let kinds = |defender: Vec<PlayedCard>| {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            5,
            vec![PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu).with_energy(vec![EnergyType::Water; 2])],
            defender,
        );
        game.apply_action(&Action { actor: 0, action: attack_action(CardId::B3051RapidStrikeUrshifu, 0), is_stack: false });
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        choices
            .iter()
            .filter_map(|choice| match &choice.action {
                SimpleAction::ApplyDamage { targets, .. } => Some(("ApplyDamage", targets[1].2)),
                SimpleAction::ApplyQueuedAttackDamage { targets, .. } => Some(("ApplyQueuedAttackDamage", targets[1].2)),
                _ => None,
            })
            .collect::<Vec<_>>()
    };
    assert_eq!(
        kinds(vec![bulbasaur(), bulbasaur(), meowth()]),
        vec![("ApplyDamage", 1), ("ApplyQueuedAttackDamage", 2)]
    );
    assert_eq!(
        kinds(vec![meowth(), bulbasaur(), bulbasaur()]),
        vec![("ApplyQueuedAttackDamage", 1), ("ApplyQueuedAttackDamage", 2)]
    );
}

/// The later round's control: into Pokemon without a coin-flip damage Ability, every site queues its damage exactly as
/// before, as `ApplyDamage` (never `ApplyQueuedAttackDamage`), over 20 seeds each.
#[test]
fn the_later_rounds_sites_into_pokemon_without_a_coin_ability_are_unchanged() {
    let latios = || PlayedCard::from_id(CardId::PB024MegaLatiosEx);
    let sites: Vec<(Vec<PlayedCard>, CardId, Vec<CardId>)> = vec![
        (
            vec![
                PlayedCard::from_id(CardId::A4045Gyarados).with_energy(vec![EnergyType::Water; 2]),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
            CardId::A4045Gyarados,
            vec![],
        ),
        (
            vec![PlayedCard::from_id(CardId::B2048WellspringMaskOgerpon).with_energy(vec![EnergyType::Water; 2])],
            CardId::B2048WellspringMaskOgerpon,
            vec![],
        ),
        (
            vec![PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu).with_energy(vec![EnergyType::Water; 2])],
            CardId::B3051RapidStrikeUrshifu,
            vec![],
        ),
        (vec![PlayedCard::from_id(CardId::B1a019Blastoise).with_energy(vec![EnergyType::Water; 5])], CardId::B1a019Blastoise, vec![]),
        (
            vec![PlayedCard::from_id(CardId::B1a020MegaBlastoiseEx).with_energy(vec![EnergyType::Water; 6])],
            CardId::B1a020MegaBlastoiseEx,
            vec![],
        ),
        (
            vec![PlayedCard::from_id(CardId::B2127MegaKangaskhanEx).with_energy(vec![EnergyType::Colorless; 3])],
            CardId::B2127MegaKangaskhanEx,
            vec![],
        ),
        (vec![PlayedCard::from_id(CardId::B4077Hoopa).with_energy(vec![EnergyType::Psychic])], CardId::B4077Hoopa, vec![]),
        (
            vec![PlayedCard::from_id(CardId::A4a018Slowking).with_energy(vec![EnergyType::Water])],
            CardId::A4a018Slowking,
            vec![CardId::A2147GiantCape, CardId::A2148RockyHelmet],
        ),
    ];
    for (attacker, card, hand) in sites {
        let mut plain = 0;
        for seed in 0..20u64 {
            let mut game = get_initialized_game_with_board(seed, 0, 5, attacker.clone(), vec![latios(), latios(), latios()]);
            let mut state = game.get_state_clone();
            state.hands[0] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
            game.set_state(state);
            game.apply_action(&Action { actor: 0, action: attack_action(card, 0), is_stack: false });
            for _ in 0..10 {
                let state = game.get_state_clone();
                if state.move_generation_stack.is_empty() {
                    break;
                }
                let (actor, choices) = state.generate_possible_actions();
                if actor != 0 || choices.is_empty() {
                    break;
                }
                for choice in &choices {
                    assert!(
                        !matches!(choice.action, SimpleAction::ApplyQueuedAttackDamage { .. }),
                        "{card:?}, seed {seed}: {:?}",
                        choice.action
                    );
                    plain += usize::from(matches!(choice.action, SimpleAction::ApplyDamage { .. }));
                }
                // The largest discard (Wild Swing, Litter), else the first choice.
                let pick = choices
                    .iter()
                    .max_by_key(|choice| match &choice.action {
                        SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } => in_play_idxs.len(),
                        SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. } => cards.len(),
                        _ => 0,
                    })
                    .filter(|choice| {
                        matches!(
                            choice.action,
                            SimpleAction::DiscardOwnBenchedThenDamage { .. } | SimpleAction::DiscardOwnCardsForAttackDamage { .. }
                        )
                    })
                    .unwrap_or(&choices[0])
                    .clone();
                game.apply_action(&pick);
            }
        }
        assert!(plain > 0, "{card:?}: the site queued no damage choice in 20 seeds");
    }
}

/// rules/09 (Sonnet's S4, Sept 30): only attacks trigger the coin-flip damage Abilities. Damage from an Ability, a Tool
/// or the Checkup never flips them. The engine already honours this (the coin is set up only on an attack's path);
/// these three pin it.
#[test]
fn carefree_steps_never_flips_for_an_abilitys_damage() {
    // Greninja's Water Shuriken: "Once during your turn, you may do 20 damage to 1 of your opponent's Pokemon."
    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            5,
            vec![PlayedCard::from_id(CardId::A1089Greninja)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::B2124Meowth)],
        );
        game.apply_action(&Action { actor: 0, action: SimpleAction::UseAbility { in_play_idx: 0 }, is_stack: false });
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        let at_meowth = choices
            .iter()
            .find(|choice| matches!(&choice.action, SimpleAction::ApplyDamage { targets, .. } if targets[0].2 == 1))
            .expect("Water Shuriken can target the Benched Meowth")
            .clone();
        assert!(matches!(at_meowth.action, SimpleAction::ApplyDamage { is_from_active_attack: false, .. }));
        game.apply_action(&at_meowth);
        let meowth = game.get_state_clone().in_play_pokemon[1][1].clone().expect("Meowth survives 20");
        assert_eq!(meowth.get_remaining_hp(), 30, "seed {seed}: an Ability's damage never flips the coin");
    }
}

#[test]
fn celestial_blessing_never_flips_for_a_tools_damage() {
    // Togekiss (Celestial Blessing) attacks Mega Latios ex holding Rocky Helmet ("... do 20 damage to the Attacking
    // Pokemon"): the Helmet's 20 always lands on Togekiss.
    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            5,
            vec![PlayedCard::from_id(CardId::A4080Togekiss).with_energy(vec![EnergyType::Psychic; 3])],
            vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
        );
        game.apply_action(&Action { actor: 0, action: attack_action(CardId::A4080Togekiss, 0), is_stack: false });
        let togekiss = game.get_state_clone().in_play_pokemon[0][0].clone().expect("Togekiss survives 20");
        assert_eq!(togekiss.get_remaining_hp(), 120, "seed {seed}: a Tool's damage never flips the coin");
    }
}

#[test]
fn carefree_steps_never_flips_for_the_checkups_damage() {
    // A Poisoned Meowth takes 10 in the Checkup when player 0 ends the turn.
    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            5,
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::B2124Meowth).with_status_condition(StatusCondition::Poisoned)],
        );
        game.apply_action(&Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
        let meowth = game.get_state_clone().in_play_pokemon[1][0].clone().expect("Meowth survives 10");
        assert_eq!(meowth.get_remaining_hp(), 40, "seed {seed}: the Checkup's damage never flips the coin");
    }
}
