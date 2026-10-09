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

/// The coin Abilities on the attacker's own Pokémon (TEXT_AUDIT.md A4; the card text, Dustin's rule of Oct 1). "If any
/// damage is done to this Pokémon by attacks" has no "your opponent's", so damage from your own attack to your own
/// coin-Ability Pokémon flips its coin. Over 60 seeds, how often player 0's own Pokémon named `name` took none of its own
/// attack's damage, and how often it took some; every queued choice of player 0 is steered at that Pokémon.
fn own_coin_counts(
    attacker: Vec<PlayedCard>,
    attack: (CardId, usize),
    defender: Vec<PlayedCard>,
    name: &str,
) -> (usize, usize) {
    let own = |state: &State| {
        state
            .enumerate_in_play_pokemon(0)
            .find(|(_, p)| p.get_name() == name)
            .map(|(idx, p)| (idx, p.get_remaining_hp()))
    };
    let (mut prevented, mut hit) = (0, 0);
    for seed in 0..60u64 {
        let mut game: Game = get_initialized_game_with_board(seed, 0, 5, attacker.clone(), defender.clone());
        let (slot, before) = own(&game.get_state_clone()).expect("the attacker's own coin-Ability Pokémon is in play");
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
            let aimed = choices.iter().find(|choice| match &choice.action {
                SimpleAction::ApplyDamage { targets, .. } => targets.iter().any(|(_, p, i)| *p == 0 && *i == slot),
                SimpleAction::ApplyQueuedAttackDamage { targets, .. } => targets.iter().any(|(_, opp, i)| !*opp && *i == slot),
                _ => false,
            });
            game.apply_action(aimed.unwrap_or(&choices[0]));
        }
        match own(&game.get_state_clone()) {
            Some((_, after)) if after == before => prevented += 1,
            _ => hit += 1,
        }
    }
    (prevented, hit)
}

/// TEXT_AUDIT.md A4: your own Meowth on your Bench, hit by your own attack. Zapdos's Raging Thunder ("This attack also
/// does 30 damage to 1 of your Benched Pokémon") and Mimikyu's Shadow Hit ("... 20 damage to 1 of your Pokémon") queue
/// the hit as a choice; Whiscash's Earthquake ("... 10 damage to each of your Benched Pokémon") carries it in the
/// attack's outcome. Before the fix none of them flipped (0 prevented of 60).
#[test]
fn carefree_steps_flips_for_your_own_attacks_damage_to_your_own_meowth() {
    let cases = [
        ("Raging Thunder", PlayedCard::from_id(CardId::A1103Zapdos).with_energy(vec![EnergyType::Lightning; 3]), CardId::A1103Zapdos),
        ("Shadow Hit", PlayedCard::from_id(CardId::A3083Mimikyu).with_energy(vec![EnergyType::Psychic; 2]), CardId::A3083Mimikyu),
        ("Earthquake", PlayedCard::from_id(CardId::A3b039Whiscash).with_energy(vec![EnergyType::Fighting; 4]), CardId::A3b039Whiscash),
    ];
    for (title, attacker, card_id) in cases {
        let (prevented, hit) = own_coin_counts(
            vec![attacker, meowth()],
            (card_id, 0),
            vec![PlayedCard::from_id(CardId::A1036CharizardEx)],
            "Meowth",
        );
        assert!(prevented > 10 && hit > 10, "{title}: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

/// TEXT_AUDIT.md A4: Securely Sheltered's cut on your own Benched Hisuian Goodra, from Great Tusk's Shaking Stomp ("This
/// attack also does 20 damage to each of your Benched Pokémon"): on heads it takes 20 − 80, so nothing.
#[test]
fn securely_sheltered_cuts_your_own_shaking_stomp_on_your_benched_goodra() {
    let (prevented, hit) = own_coin_counts(
        vec![
            PlayedCard::from_id(CardId::B3a034GreatTusk).with_energy(vec![EnergyType::Fighting; 2]),
            PlayedCard::from_id(CardId::B3b050HisuianGoodra),
        ],
        (CardId::B3a034GreatTusk, 0),
        vec![PlayedCard::from_id(CardId::A1036CharizardEx)],
        "Hisuian Goodra",
    );
    assert!(prevented > 10 && hit > 10, "{prevented} prevented, {hit} hit: the coin must flip");
}

/// TEXT_AUDIT.md A4: the opponent's Active Meowth in an own-Bench choice. Raging Thunder's 100 and its 30 to your own
/// Bench are queued as one choice, which the later round's gate left as a plain `ApplyDamage` because it also hits your
/// Bench, so the 100 never flipped Meowth's coin.
#[test]
fn carefree_steps_flips_for_the_active_hit_of_an_own_bench_choice() {
    queued_damage_flips_carefree_steps_from(
        vec![
            PlayedCard::from_id(CardId::A1103Zapdos).with_energy(vec![EnergyType::Lightning; 3]),
            bulbasaur(),
        ],
        (CardId::A1103Zapdos, 0),
        vec![meowth()],
        false,
    );
}

/// A copied discard attack (TEXT_AUDIT.md A5): Ditto's copy is "this attack", so its damage is damage by an attack.
/// Ditto's Copy Anything copies the opponent's Benched Vespiquen ex's Chase Order (discarding Ditto's Benched Bulbasaur),
/// and Copy a Friend copies Ditto's own Benched Gyarados's Wild Swing (discarding a Benched Water Pokémon), each into an
/// Active Meowth. Before the fix the discard's damage looked for the attack among Ditto's printed attacks, found none,
/// and was queued without the coin.
#[test]
fn carefree_steps_flips_for_a_copied_discard_attack() {
    let cases = [
        (
            "Chase Order",
            vec![
                PlayedCard::from_id(CardId::A1205Ditto).with_energy(vec![EnergyType::Grass; 2]),
                bulbasaur(),
            ],
            CardId::A1205Ditto,
            vec![meowth(), PlayedCard::from_id(CardId::B4011VespiquenEx)],
        ),
        (
            "Wild Swing",
            vec![
                PlayedCard::from_id(CardId::B1a055Ditto).with_energy(vec![EnergyType::Water; 2]),
                PlayedCard::from_id(CardId::A4045Gyarados),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
            CardId::B1a055Ditto,
            vec![meowth()],
        ),
    ];
    for (title, attacker, ditto, defender) in cases {
        let (mut prevented, mut hit, mut discarded) = (0, 0, 0);
        for seed in 0..60u64 {
            let mut game: Game = get_initialized_game_with_board(seed, 0, 5, attacker.clone(), defender.clone());
            let before = game.get_state_clone().get_active(1).get_remaining_hp();
            game.apply_action(&Action { actor: 0, action: attack_action(ditto, 0), is_stack: false });
            for _ in 0..10 {
                let state = game.get_state_clone();
                if state.move_generation_stack.is_empty() {
                    break;
                }
                let (actor, choices) = state.generate_possible_actions();
                if actor != 0 || choices.is_empty() {
                    break;
                }
                let copy = choices
                    .iter()
                    .find(|choice| matches!(&choice.action, SimpleAction::Attack(attack) if attack.title == title));
                let discard = choices.iter().find(|choice| {
                    matches!(&choice.action, SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } if !in_play_idxs.is_empty())
                });
                discarded += discard.is_some() as usize;
                game.apply_action(copy.or(discard).unwrap_or(&choices[0]));
            }
            let unhurt = game
                .get_state_clone()
                .enumerate_in_play_pokemon(1)
                .any(|(idx, p)| idx == 0 && p.get_name() == "Meowth" && p.get_remaining_hp() == before);
            if unhurt {
                prevented += 1;
            } else {
                hit += 1;
            }
        }
        assert_eq!(discarded, 60, "{title}: the copied attack's discard was offered on every seed");
        assert!(prevented > 10 && hit > 10, "{title}: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

// ---- Revert switches (rules switch 2, PLAN (e); the coordinator's brief of Oct 9). Each `revert_*` test re-runs a scenario
// above with a gate's switch off and asserts the engine before that gate (the official engine, main-8626a35), and with the
// switch on, the current result. Old values: `rl/results/coin_prevention_round2_2026-10-01/tests_before_fix*.log`.

/// G1 (the plain-hit coin) and G2 (the seven sites) together. The seven sites' old numbers need both: G2 alone restores
/// the plain `ApplyDamage`, and G1 would still flip the coin inside it.
fn seven_sites<R>(on: bool, f: impl FnOnce() -> R) -> R {
    use deckgym::actions::{with_plain_hit_coin, with_queued_site_coin};
    with_plain_hit_coin(on, || with_queued_site_coin(on, f))
}

/// The three cases of `carefree_steps_flips_for_your_own_attacks_damage_to_your_own_meowth` (player 0's own Meowth on the
/// Bench): (title, prevented, hit) over 60 seeds each.
fn own_meowth_counts() -> Vec<(&'static str, usize, usize)> {
    let cases = [
        ("Raging Thunder", PlayedCard::from_id(CardId::A1103Zapdos).with_energy(vec![EnergyType::Lightning; 3]), CardId::A1103Zapdos),
        ("Shadow Hit", PlayedCard::from_id(CardId::A3083Mimikyu).with_energy(vec![EnergyType::Psychic; 2]), CardId::A3083Mimikyu),
        ("Earthquake", PlayedCard::from_id(CardId::A3b039Whiscash).with_energy(vec![EnergyType::Fighting; 4]), CardId::A3b039Whiscash),
    ];
    cases
        .into_iter()
        .map(|(title, attacker, card_id)| {
            let (prevented, hit) = own_coin_counts(
                vec![attacker, meowth()],
                (card_id, 0),
                vec![PlayedCard::from_id(CardId::A1036CharizardEx)],
                "Meowth",
            );
            (title, prevented, hit)
        })
        .collect()
}

/// G1, the plain-hit coin (`with_plain_hit_coin(false, ..)`): a queued plain `ApplyDamage` flips no coin, so the
/// opponent's Active Meowth always takes Raging Thunder's 100 in the own-Bench choice of
/// `carefree_steps_flips_for_the_active_hit_of_an_own_bench_choice`. Old: 0 prevented, 60 hit
/// (`tests_before_fix_text.log:857`).
#[test]
fn revert_g1_plain_hit_coin_gives_the_old_hit_for_an_own_bench_choice() {
    use deckgym::actions::with_plain_hit_coin;
    let counts = || {
        carefree_steps_counts(
            vec![PlayedCard::from_id(CardId::A1103Zapdos).with_energy(vec![EnergyType::Lightning; 3]), bulbasaur()],
            (CardId::A1103Zapdos, 0),
            vec![meowth()],
            false,
        )
    };
    assert_eq!(with_plain_hit_coin(false, counts), (0, 60), "switch off: no coin for the queued plain hit");
    let (prevented, hit) = with_plain_hit_coin(true, counts);
    assert!(prevented > 10 && hit > 10, "switch on: {prevented} prevented, {hit} hit: the coin must flip");
}

/// G1: a copied discard attack's damage is queued as a plain `ApplyDamage` (the attack is not among Ditto's printed
/// attacks), so with the plain-hit coin off neither copy of `carefree_steps_flips_for_a_copied_discard_attack` flips
/// Meowth's coin, and the discard is still offered on every seed. Old: Chase Order 0 prevented, 60 hit
/// (`tests_before_fix_text.log:852`, the first case); README.md:71 gives "0 of 60" for the test, Wild Swing included.
#[test]
fn revert_g1_plain_hit_coin_gives_the_old_hit_for_a_copied_discard_attack() {
    use deckgym::actions::with_plain_hit_coin;
    /// (prevented, hit, discard offered) over 60 seeds, as in `carefree_steps_flips_for_a_copied_discard_attack`.
    fn copied(title: &str) -> (usize, usize, usize) {
        let (attacker, ditto, defender) = match title {
            "Chase Order" => (
                vec![PlayedCard::from_id(CardId::A1205Ditto).with_energy(vec![EnergyType::Grass; 2]), bulbasaur()],
                CardId::A1205Ditto,
                vec![meowth(), PlayedCard::from_id(CardId::B4011VespiquenEx)],
            ),
            _ => (
                vec![
                    PlayedCard::from_id(CardId::B1a055Ditto).with_energy(vec![EnergyType::Water; 2]),
                    PlayedCard::from_id(CardId::A4045Gyarados),
                    PlayedCard::from_id(CardId::A1053Squirtle),
                ],
                CardId::B1a055Ditto,
                vec![meowth()],
            ),
        };
        let (mut prevented, mut hit, mut discarded) = (0, 0, 0);
        for seed in 0..60u64 {
            let mut game: Game = get_initialized_game_with_board(seed, 0, 5, attacker.clone(), defender.clone());
            let before = game.get_state_clone().get_active(1).get_remaining_hp();
            game.apply_action(&Action { actor: 0, action: attack_action(ditto, 0), is_stack: false });
            for _ in 0..10 {
                let state = game.get_state_clone();
                if state.move_generation_stack.is_empty() {
                    break;
                }
                let (actor, choices) = state.generate_possible_actions();
                if actor != 0 || choices.is_empty() {
                    break;
                }
                let copy = choices
                    .iter()
                    .find(|choice| matches!(&choice.action, SimpleAction::Attack(attack) if attack.title == title));
                let discard = choices.iter().find(|choice| {
                    matches!(&choice.action, SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } if !in_play_idxs.is_empty())
                });
                discarded += discard.is_some() as usize;
                game.apply_action(copy.or(discard).unwrap_or(&choices[0]));
            }
            let unhurt = game
                .get_state_clone()
                .enumerate_in_play_pokemon(1)
                .any(|(idx, p)| idx == 0 && p.get_name() == "Meowth" && p.get_remaining_hp() == before);
            if unhurt {
                prevented += 1;
            } else {
                hit += 1;
            }
        }
        (prevented, hit, discarded)
    }
    for title in ["Chase Order", "Wild Swing"] {
        assert_eq!(with_plain_hit_coin(false, || copied(title)), (0, 60, 60), "{title}: switch off, (prevented, hit, discards)");
        let (prevented, hit, discarded) = with_plain_hit_coin(true, || copied(title));
        assert_eq!(discarded, 60, "{title}: switch on");
        assert!(prevented > 10 && hit > 10, "{title}: switch on: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

/// G1 with your own Meowth (`carefree_steps_flips_for_your_own_attacks_damage_to_your_own_meowth`): Raging Thunder and
/// Shadow Hit queue the hit on your own Bench as a plain `ApplyDamage`, so with the plain-hit coin off they flip no coin.
/// Old: 0 prevented, 60 hit (`tests_before_fix_text.log:862` for Raging Thunder, the first case; README.md:68 gives
/// "0 prevented of 60" for the test). Earthquake's hit is in the attack's outcome, G3's place, so G1 alone leaves its coin
/// flipping.
#[test]
fn revert_g1_plain_hit_coin_gives_the_old_hit_on_your_own_meowth_through_a_queued_choice() {
    use deckgym::actions::with_plain_hit_coin;
    for (title, prevented, hit) in with_plain_hit_coin(false, own_meowth_counts) {
        if title == "Earthquake" {
            assert!(prevented > 10 && hit > 10, "switch off, {title}: {prevented} prevented, {hit} hit: not G1's place");
        } else {
            assert_eq!((prevented, hit), (0, 60), "switch off, {title}: no coin for the queued plain hit");
        }
    }
    for (title, prevented, hit) in with_plain_hit_coin(true, own_meowth_counts) {
        assert!(prevented > 10 && hit > 10, "switch on, {title}: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

/// G3, the own side (`with_own_side_coin(false, ..)`): the coin Abilities of the attacker's own Pokémon never flip, in the
/// attack's outcome (Earthquake) or in a queued plain hit (Raging Thunder, Shadow Hit). Old: 0 prevented, 60 hit for each
/// (`tests_before_fix_text.log:862` for Raging Thunder, the first case; README.md:68 gives "0 prevented of 60" for the
/// test).
#[test]
fn revert_g3_own_side_coin_gives_the_old_hit_on_your_own_meowth() {
    use deckgym::actions::with_own_side_coin;
    for (title, prevented, hit) in with_own_side_coin(false, own_meowth_counts) {
        assert_eq!((prevented, hit), (0, 60), "switch off, {title}: no coin on your own Pokémon");
    }
    for (title, prevented, hit) in with_own_side_coin(true, own_meowth_counts) {
        assert!(prevented > 10 && hit > 10, "switch on, {title}: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

/// G3: Securely Sheltered never cuts your own Shaking Stomp on your own Benched Hisuian Goodra
/// (`securely_sheltered_cuts_your_own_shaking_stomp_on_your_benched_goodra`). Old: 0 prevented, 60 hit
/// (`tests_before_fix_text.log:867`).
#[test]
fn revert_g3_own_side_coin_gives_the_old_hit_on_your_own_goodra() {
    use deckgym::actions::with_own_side_coin;
    let counts = || {
        own_coin_counts(
            vec![
                PlayedCard::from_id(CardId::B3a034GreatTusk).with_energy(vec![EnergyType::Fighting; 2]),
                PlayedCard::from_id(CardId::B3b050HisuianGoodra),
            ],
            (CardId::B3a034GreatTusk, 0),
            vec![PlayedCard::from_id(CardId::A1036CharizardEx)],
            "Hisuian Goodra",
        )
    };
    assert_eq!(with_own_side_coin(false, counts), (0, 60), "switch off: no cut on your own Goodra");
    let (prevented, hit) = with_own_side_coin(true, counts);
    assert!(prevented > 10 && hit > 10, "switch on: {prevented} prevented, {hit} hit: the coin must flip");
}

/// G1 + G2, Gyarados's Wild Swing (`carefree_steps_flips_for_wild_swing`), with and without the discard. Old: 0
/// prevented, 60 hit, verbatim from the pin removed at 8626a358 (`wild_swing_into_carefree_steps_pins_todays_behaviour_
/// no_coin`, meowth_carefree_steps_test.rs:390-403 there); `tests_before_fix.log:136` shows the case without the discard.
#[test]
fn revert_g1_g2_wild_swing_gives_the_old_hit() {
    let counts = |discard: bool| {
        carefree_steps_counts(
            vec![
                PlayedCard::from_id(CardId::A4045Gyarados).with_energy(vec![EnergyType::Water; 2]),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
            (CardId::A4045Gyarados, 0),
            vec![PlayedCard::from_id(CardId::B2124Meowth)],
            discard,
        )
    };
    for discard in [false, true] {
        assert_eq!(seven_sites(false, || counts(discard)), (0, 60), "discard {discard}: Wild Swing is not repaired yet");
        let (prevented, hit) = seven_sites(true, || counts(discard));
        assert!(prevented > 10 && hit > 10, "switches on, discard {discard}: {prevented} prevented, {hit} hit");
    }
}

/// G1 + G2, Wellspring Dance on its heads (`carefree_steps_flips_for_wellspring_dance_on_its_heads`). Old, Meowth on the
/// Bench: 0 prevented, 39 hit on the heads (`tests_before_fix.log:147`). With Meowth in the Active Spot the old run had
/// stopped, so only "none prevented" is asserted there (old aaa:5747-5754 at 8626a358 queued a plain `ApplyDamage`).
#[test]
fn revert_g1_g2_wellspring_dance_gives_the_old_hit_on_its_heads() {
    /// (prevented, hit) over the seeds of 0..80 whose attack coin was heads.
    fn heads_counts(defender: Vec<PlayedCard>) -> (usize, usize) {
        let attacker = vec![PlayedCard::from_id(CardId::B2048WellspringMaskOgerpon).with_energy(vec![EnergyType::Water; 2])];
        let (mut prevented, mut hit) = (0, 0);
        for seed in 0..80u64 {
            match carefree_steps_seed(seed, &attacker, (CardId::B2048WellspringMaskOgerpon, 0), &defender, false, &[]) {
                (true, true) => prevented += 1,
                (true, false) => hit += 1,
                (false, _) => {}
            }
        }
        (prevented, hit)
    }
    assert_eq!(seven_sites(false, || heads_counts(vec![bulbasaur(), meowth()])), (0, 39), "switches off, Meowth on the Bench");
    let (prevented, hit) = seven_sites(false, || heads_counts(vec![meowth(), bulbasaur()]));
    assert!(prevented == 0 && hit > 5, "switches off, Meowth Active: {prevented} prevented, {hit} hit on the heads");
    for defender in [vec![bulbasaur(), meowth()], vec![meowth(), bulbasaur()]] {
        let (prevented, hit) = seven_sites(true, || heads_counts(defender));
        assert!(prevented > 5 && hit > 5, "switches on: {prevented} prevented, {hit} hit on the heads");
    }
}

/// G1 + G2, Rapid Strike Urshifu's Tornado Shot (`carefree_steps_flips_for_tornado_shot`). Old: 0 prevented, 60 hit
/// (`tests_before_fix.log:98`, Meowth on the Bench, the first case; with Meowth Active the old code, aaa:3888-3892 at
/// 8626a358, queued the same plain `ApplyDamage`).
#[test]
fn revert_g1_g2_tornado_shot_gives_the_old_hit() {
    let counts = |defender: Vec<PlayedCard>| {
        carefree_steps_counts(
            vec![PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu).with_energy(vec![EnergyType::Water; 2])],
            (CardId::B3051RapidStrikeUrshifu, 0),
            defender,
            false,
        )
    };
    for defender in [vec![bulbasaur(), meowth()], vec![meowth(), bulbasaur()]] {
        assert_eq!(seven_sites(false, || counts(defender.clone())), (0, 60), "switches off: {defender:?}");
        let (prevented, hit) = seven_sites(true, || counts(defender));
        assert!(prevented > 10 && hit > 10, "switches on: {prevented} prevented, {hit} hit");
    }
}

/// G1 + G2, Blastoise's Double Splash and Mega Blastoise ex's Triple Bombardment
/// (`carefree_steps_flips_for_double_splash_and_triple_bombardment`). Old: 0 prevented, 60 hit (`tests_before_fix.log:74`,
/// Double Splash with Meowth on the Bench, the first case; the other three cases queue the same plain `ApplyDamage` in the
/// old code, aaa:6122 at 8626a358).
#[test]
fn revert_g1_g2_double_splash_and_triple_bombardment_give_the_old_hit() {
    let counts = |attacker: PlayedCard, card: CardId, defender: Vec<PlayedCard>| {
        carefree_steps_counts(vec![attacker], (card, 0), defender, false)
    };
    let blastoise = || PlayedCard::from_id(CardId::B1a019Blastoise).with_energy(vec![EnergyType::Water; 5]);
    let mega = || PlayedCard::from_id(CardId::B1a020MegaBlastoiseEx).with_energy(vec![EnergyType::Water; 6]);
    for defender in [vec![bulbasaur(), meowth(), bulbasaur()], vec![meowth(), bulbasaur(), bulbasaur()]] {
        for (attacker, card) in [(blastoise(), CardId::B1a019Blastoise), (mega(), CardId::B1a020MegaBlastoiseEx)] {
            let off = seven_sites(false, || counts(attacker.clone(), card, defender.clone()));
            assert_eq!(off, (0, 60), "switches off, {card:?}");
            let (prevented, hit) = seven_sites(true, || counts(attacker, card, defender.clone()));
            assert!(prevented > 10 && hit > 10, "switches on, {card:?}: {prevented} prevented, {hit} hit");
        }
    }
}

/// G1 + G2, Hoopa's Mischievous Ring (`carefree_steps_flips_for_mischievous_ring`). Old: 0 prevented, 60 hit
/// (`tests_before_fix.log:86`).
#[test]
fn revert_g1_g2_mischievous_ring_gives_the_old_hit() {
    let counts = || {
        carefree_steps_counts(
            vec![PlayedCard::from_id(CardId::B4077Hoopa).with_energy(vec![EnergyType::Psychic])],
            (CardId::B4077Hoopa, 0),
            vec![meowth(), bulbasaur().with_tool(get_card_by_enum(CardId::A2147GiantCape))],
            false,
        )
    };
    assert_eq!(seven_sites(false, counts), (0, 60), "switches off");
    let (prevented, hit) = seven_sites(true, counts);
    assert!(prevented > 10 && hit > 10, "switches on: {prevented} prevented, {hit} hit");
}

/// G1 + G2, Slowking's Litter (`carefree_steps_flips_for_litter`): the damage is still queued at Meowth on every seed.
/// Old: 0 prevented, 60 hit (`tests_before_fix.log:110`).
#[test]
fn revert_g1_g2_litter_gives_the_old_hit() {
    fn counts() -> (usize, usize) {
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
        (prevented, hit)
    }
    assert_eq!(seven_sites(false, counts), (0, 60), "switches off");
    let (prevented, hit) = seven_sites(true, counts);
    assert!(prevented > 10 && hit > 10, "switches on: {prevented} prevented, {hit} hit");
}

/// G1 + G2, Mega Kangaskhan ex's second punch. Togekiss's Celestial Blessing never prevents it
/// (`celestial_blessing_flips_for_both_punches_of_double_punching_family`; old: second punch 0 prevented, 60 hit,
/// `tests_before_fix_kangaskhan.log:87`), and neither does Meowth promoted after the first punch's Knock Out
/// (`carefree_steps_flips_for_the_second_punch_after_a_knock_out`; old: 0 prevented, 60 hit, `:76`).
#[test]
fn revert_g1_g2_second_punch_gives_the_old_hit() {
    /// Over 60 seeds into Togekiss: (second punch prevented, second punch hit).
    fn into_togekiss() -> (usize, usize) {
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
        (second_prevented, second_hit)
    }
    /// Over 60 seeds, Bulbasaur Knocked Out by the first punch and Meowth promoted: (prevented, hit).
    fn after_a_knock_out() -> (usize, usize) {
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
        (prevented, hit)
    }
    assert_eq!(seven_sites(false, into_togekiss), (0, 60), "switches off: the second punch into Togekiss");
    assert_eq!(seven_sites(false, after_a_knock_out), (0, 60), "switches off: the second punch after a Knock Out");
    for (label, (prevented, hit)) in
        [("into Togekiss", seven_sites(true, into_togekiss)), ("after a Knock Out", seven_sites(true, after_a_knock_out))]
    {
        assert!(prevented > 10 && hit > 10, "switches on, {label}: {prevented} prevented, {hit} hit");
    }
}

/// G2 alone (`with_queued_site_coin(false, ..)`) restores the choice kinds of
/// `only_a_choice_that_hits_a_coin_ability_pokemon_takes_the_coin_path_in_the_later_round`: Tornado Shot queues every
/// choice as a plain `ApplyDamage`. Old, Meowth on the Bench: [("ApplyDamage", 1), ("ApplyDamage", 2)]
/// (`tests_before_fix.log:122`); with Meowth Active the old code (aaa:3888-3892 at 8626a358) built the same plain choices.
#[test]
fn revert_g2_queued_site_coin_gives_the_old_choice_kinds() {
    use deckgym::actions::with_queued_site_coin;
    fn kinds(defender: Vec<PlayedCard>) -> Vec<(&'static str, usize)> {
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
            .collect()
    }
    let plain = vec![("ApplyDamage", 1), ("ApplyDamage", 2)];
    let benched = || kinds(vec![bulbasaur(), bulbasaur(), meowth()]);
    let active = || kinds(vec![meowth(), bulbasaur(), bulbasaur()]);
    assert_eq!(with_queued_site_coin(false, benched), plain, "switch off, Meowth Benched");
    assert_eq!(with_queued_site_coin(false, active), plain, "switch off, Meowth Active");
    assert_eq!(
        with_queued_site_coin(true, benched),
        vec![("ApplyDamage", 1), ("ApplyQueuedAttackDamage", 2)],
        "switch on, Meowth Benched"
    );
    assert_eq!(
        with_queued_site_coin(true, active),
        vec![("ApplyQueuedAttackDamage", 1), ("ApplyQueuedAttackDamage", 2)],
        "switch on, Meowth Active"
    );
}
