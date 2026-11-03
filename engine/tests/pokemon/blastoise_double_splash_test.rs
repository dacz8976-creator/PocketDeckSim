use deckgym::{
    actions::{with_plain_hit_coin, with_queued_site_coin, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game, get_initialized_game_with_board},
    Game,
};

fn played_card_with_base_hp(card_id: CardId, base_hp: u32) -> PlayedCard {
    let card = get_card_by_enum(card_id);
    PlayedCard::new(card, 0, base_hp, vec![], false, vec![])
}

/// Test Blastoise B1a 019 - Double Splash with extra energy
/// Should deal 90 to active and 50 to 1 benched Pokemon when 2+ extra Water energies attached
#[test]
fn test_blastoise_double_splash_with_extra_energy() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;

    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B1a019Blastoise).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
            ]),
        ],
        vec![
            played_card_with_base_hp(CardId::A1001Bulbasaur, 150),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );

    game.set_state(state);

    // Attack with Double Splash
    let action = Action {
        actor: 0,
        action: attack_action(CardId::B1a019Blastoise, 0),
        is_stack: false,
    };

    game.apply_action(&action);
    let state = game.get_state_clone();

    // Check that a stack action is queued with bench target choices
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0, "Actor should be player 0");
    assert!(
        choices
            .iter()
            .any(|a| matches!(a.action, SimpleAction::ApplyDamage { .. })),
        "Expected bench target ApplyDamage choices"
    );

    // Apply the first choice (damage to bench position 1)
    game.apply_action(&choices[0]);
    let state = game.get_state_clone();

    // Verify active took 90 damage (150 - 90 = 60)
    let opponent_active = state.get_active(1);
    assert_eq!(
        opponent_active.get_remaining_hp(),
        60,
        "Opponent active should have 60 HP remaining (150 - 90)"
    );

    // Verify bench took 50 damage (60 - 50 = 10 HP remaining)
    let opponent_bench = state.enumerate_bench_pokemon(1).next();
    assert!(
        opponent_bench.is_some(),
        "Opponent bench Pokemon should still be alive (60 - 50 = 10)"
    );
    assert_eq!(
        opponent_bench.unwrap().1.get_remaining_hp(),
        10,
        "Opponent bench Pokemon should have 10 HP remaining (60 - 50)"
    );
}

/// Test Blastoise B1a 019 - Double Splash without extra energy
/// Should deal only 90 to active when no extra energies
#[test]
fn test_blastoise_double_splash_without_extra_energy() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;

    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B1a019Blastoise).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Fire,
            ]),
        ],
        vec![
            played_card_with_base_hp(CardId::A1001Bulbasaur, 150),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );

    game.set_state(state);

    // Attack with Double Splash
    let action = Action {
        actor: 0,
        action: attack_action(CardId::B1a019Blastoise, 0),
        is_stack: false,
    };

    game.apply_action(&action);
    let state = game.get_state_clone();

    // Check that there are NO stacked ApplyDamage actions (no bench damage)
    let (_actor, actions) = state.generate_possible_actions();
    let has_apply_damage = actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::ApplyDamage { .. }));
    assert!(
        !has_apply_damage,
        "Move generation stack should have no ApplyDamage actions (no extra energy for bench damage)"
    );

    // Verify active took 90 damage (150 - 90 = 60)
    let opponent_active = state.get_active(1);
    assert_eq!(
        opponent_active.get_remaining_hp(),
        60,
        "Opponent active should have 60 HP remaining (150 - 90)"
    );

    // Verify bench took NO damage (still at 60 HP)
    let opponent_bench = state.enumerate_bench_pokemon(1).next();
    assert!(
        opponent_bench.is_some(),
        "Opponent bench Pokemon should still be alive"
    );
    assert_eq!(
        opponent_bench.unwrap().1.get_remaining_hp(),
        60,
        "Opponent bench should still have 60 HP (no bench damage without extra energy)"
    );
}

/// Test Blastoise B1a 019 - Double Splash with extra energy but no bench
/// Should deal 90 to active only (no bench to hit)
#[test]
fn test_blastoise_double_splash_with_extra_energy_no_bench() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;

    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B1a019Blastoise).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Water,
            ]),
        ],
        vec![played_card_with_base_hp(CardId::A1001Bulbasaur, 150)],
    );

    game.set_state(state);

    // Attack with Double Splash
    let action = Action {
        actor: 0,
        action: attack_action(CardId::B1a019Blastoise, 0),
        is_stack: false,
    };

    game.apply_action(&action);
    let state = game.get_state_clone();

    // Check that there are NO stacked ApplyDamage actions (no bench to hit)
    let (_actor, actions) = state.generate_possible_actions();
    let has_apply_damage = actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::ApplyDamage { .. }));
    assert!(
        !has_apply_damage,
        "Move generation stack should have no ApplyDamage actions (no bench Pokemon to hit)"
    );

    // Verify active took 90 damage (150 - 90 = 60)
    let opponent_active = state.get_active(1);
    assert_eq!(
        opponent_active.get_remaining_hp(),
        60,
        "Opponent active should have 60 HP remaining (150 - 90), even with extra energy but no bench"
    );
}

// Fork tests (R8-10d).

/// The 5 Mega Blastoise ex printings. Triple Bombardment ([W][W][C], 130): "If this Pokémon has at
/// least 3 extra [W] Energy attached, this attack also does 50 damage to 2 of your opponent's
/// Benched Pokémon."
const MEGA_BLASTOISE_EX: [CardId; 5] = [
    CardId::B1a020MegaBlastoiseEx,
    CardId::B1a078MegaBlastoiseEx,
    CardId::B1a084MegaBlastoiseEx,
    CardId::B4b054MegaBlastoiseEx,
    CardId::B4b414MegaBlastoiseEx,
];

fn snorlax() -> PlayedCard {
    // 150 HP, no Ability.
    PlayedCard::from_id(CardId::A1211Snorlax)
}

/// Snorlax in the Active Spot and `benched` Bulbasaur (70 HP, no Ability) in slots 1 to `benched`.
fn snorlax_and_benched_bulbasaur(benched: usize) -> Vec<PlayedCard> {
    std::iter::once(snorlax())
        .chain((0..benched).map(|_| PlayedCard::from_id(CardId::A1001Bulbasaur)))
        .collect()
}

/// Player 0's Active `attacker` with `energy` against `defender` (turn 5 of the game of `seed`)
/// takes its one attack from the legal actions. A Bench choice the attack queued is then on the
/// stack.
fn attack_from_the_legal_actions(
    seed: u64,
    attacker: CardId,
    energy: Vec<EnergyType>,
    defender: Vec<PlayedCard>,
) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        5,
        vec![PlayedCard::from_id(attacker).with_energy(energy)],
        defender,
    );
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let attacks: Vec<&Action> = actions
        .iter()
        .filter(|a| matches!(a.action, SimpleAction::Attack(_)))
        .collect();
    assert_eq!(attacks.len(), 1, "{attacker:?}'s attack should be legal");
    game.apply_action(attacks[0]);
    game
}

/// Damage choices: whether each is queued as the attack's own damage (`ApplyQueuedAttackDamage`,
/// the coin path) rather than as `ApplyDamage`, and the damage and in-play index of each of the
/// opponent's Pokémon it hits.
type Picks = Vec<(bool, Vec<(u32, usize)>)>;

/// The damage choices on the stack, sorted. Empty when the attack queued none.
fn queued_picks(game: &Game<'static>) -> Picks {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    let mut picks: Picks = choices
        .iter()
        .filter_map(|choice| match &choice.action {
            SimpleAction::ApplyDamage { targets, .. } => {
                assert!(targets.iter().all(|(_, player, _)| *player == 1));
                Some((false, targets.iter().map(|&(damage, _, idx)| (damage, idx)).collect()))
            }
            SimpleAction::ApplyQueuedAttackDamage { targets, .. } => {
                assert!(targets.iter().all(|(_, opponent, _)| *opponent));
                Some((true, targets.iter().map(|&(damage, _, idx)| (damage, idx)).collect()))
            }
            _ => None,
        })
        .collect();
    if !picks.is_empty() {
        assert_eq!(actor, 0);
        assert_eq!(picks.len(), choices.len(), "only the Bench choices are on the stack");
    }
    picks.sort();
    picks
}

/// The plain `ApplyDamage` choices, sorted as `queued_picks` returns them, of `active` to the
/// Active and `bench` to each Benched Pokémon of one of `bench_sets`.
fn plain_picks(active: u32, bench: u32, bench_sets: &[Vec<usize>]) -> Picks {
    let mut picks: Picks = bench_sets
        .iter()
        .map(|set| {
            let hits = std::iter::once((active, 0)).chain(set.iter().map(|&idx| (bench, idx)));
            (false, hits.collect())
        })
        .collect();
    picks.sort();
    picks
}

/// The remaining HP of the opponent's Active and of its Pokémon in Bench slots 1 to `benched`.
fn remaining(game: &Game<'static>, benched: usize) -> Vec<u32> {
    let state = game.get_state_clone();
    (0..=benched).map(|idx| state.get_remaining_hp(1, idx)).collect()
}

/// Triple Bombardment with 3 extra [W] (6 [W] in all), from the legal actions, against Snorlax and
/// 0 to 3 Benched Bulbasaur, on every printing:
/// - 2 or 3 Benched: a choice for each pair, as before;
/// - none: no choice and only the Active's 130, as before;
/// - exactly 1 (R8-10d; rules/04: "Up to N" / variable effects do as much as they can, as Dual
///   Blizzard does with fewer Pokémon): one choice, the 130 and 50 to that one. The unchanged engine
///   queued no choice and did no Bench damage.
///
/// Each choice does 130 to Snorlax (150 HP) and 50 to each Bulbasaur (70 HP) it names, and nothing
/// to the others.
#[test]
fn test_mega_blastoise_ex_triple_bombardment_hits_as_many_benched_pokemon_as_it_can_up_to_2() {
    let bench_sets: [Vec<Vec<usize>>; 4] = [
        vec![],
        vec![vec![1]],
        vec![vec![1, 2]],
        vec![vec![1, 2], vec![1, 3], vec![2, 3]],
    ];
    for mega in MEGA_BLASTOISE_EX {
        for (benched, sets) in bench_sets.iter().enumerate() {
            let attack = || {
                attack_from_the_legal_actions(
                    0,
                    mega,
                    vec![EnergyType::Water; 6],
                    snorlax_and_benched_bulbasaur(benched),
                )
            };
            let game = attack();
            assert_eq!(
                queued_picks(&game),
                plain_picks(130, 50, sets),
                "{mega:?}, {benched} Benched"
            );
            if sets.is_empty() {
                assert_eq!(remaining(&game, 0), vec![150 - 130], "{mega:?}: the Active's 130 only");
            }
            for pick in 0..sets.len() {
                let mut game = attack();
                let (_, choices) = game.get_state_clone().generate_possible_actions();
                let hit: Vec<usize> = match &choices[pick].action {
                    SimpleAction::ApplyDamage { targets, .. } => {
                        targets.iter().map(|&(_, _, idx)| idx).filter(|&idx| idx != 0).collect()
                    }
                    other => panic!("not a Triple Bombardment choice: {other:?}"),
                };
                game.apply_action(&choices[pick]);
                let expected: Vec<u32> = (0..=benched)
                    .map(|idx| {
                        if idx == 0 {
                            150 - 130
                        } else if hit.contains(&idx) {
                            70 - 50
                        } else {
                            70
                        }
                    })
                    .collect();
                assert_eq!(
                    remaining(&game, benched),
                    expected,
                    "{mega:?}, {benched} Benched, pick {hit:?}"
                );
            }
        }
    }
}

/// The 3-extra-[W] gate is unchanged: with only 2 extra [W] (5 [W] in all) Triple Bombardment
/// queues no choice and does its 130 to the Active and nothing to the Bench, with 0 to 3 Benched
/// Pokémon, on every printing.
#[test]
fn test_mega_blastoise_ex_triple_bombardment_with_2_extra_water_does_no_bench_damage() {
    for mega in MEGA_BLASTOISE_EX {
        for benched in 0..=3 {
            let game = attack_from_the_legal_actions(
                0,
                mega,
                vec![EnergyType::Water; 5],
                snorlax_and_benched_bulbasaur(benched),
            );
            assert_eq!(queued_picks(&game), Picks::new(), "{mega:?}, {benched} Benched");
            let mut expected: Vec<u32> = vec![70; benched + 1];
            expected[0] = 150 - 130;
            assert_eq!(remaining(&game, benched), expected, "{mega:?}, {benched} Benched");
        }
    }
}

/// Blastoise B1a 019's Double Splash, the same mechanic with 1 target ("If this Pokémon has at
/// least 2 extra [W] Energy attached, this attack also does 50 damage to 1 of your opponent's
/// Benched Pokémon."), is unchanged: with 2 extra [W] (5 [W] in all) a choice for each Benched
/// Pokémon (90 to the Active, 50 to that one) and none with no Bench; with 1 extra [W], no choice
/// and the Active's 90 only.
#[test]
fn test_blastoise_double_splash_choices_are_unchanged() {
    let bench_sets: [Vec<Vec<usize>>; 4] = [
        vec![],
        vec![vec![1]],
        vec![vec![1], vec![2]],
        vec![vec![1], vec![2], vec![3]],
    ];
    for (benched, sets) in bench_sets.iter().enumerate() {
        let game = attack_from_the_legal_actions(
            0,
            CardId::B1a019Blastoise,
            vec![EnergyType::Water; 5],
            snorlax_and_benched_bulbasaur(benched),
        );
        assert_eq!(queued_picks(&game), plain_picks(90, 50, sets), "{benched} Benched");

        let game = attack_from_the_legal_actions(
            0,
            CardId::B1a019Blastoise,
            vec![EnergyType::Water; 4],
            snorlax_and_benched_bulbasaur(benched),
        );
        assert_eq!(queued_picks(&game), Picks::new(), "1 extra [W], {benched} Benched");
        let mut expected: Vec<u32> = vec![70; benched + 1];
        expected[0] = 150 - 90;
        assert_eq!(remaining(&game, benched), expected, "1 extra [W], {benched} Benched");
    }
}

/// A coin-flip damage Ability on the lone Benched Pokémon: Togekiss A4 080 (Celestial Blessing,
/// 140 HP) or Meowth B2 124 (Carefree Steps, 50 HP) behind Snorlax, over 60 seeds, on 2 printings.
/// - G2 on (rules switch 2's seven sites): the one choice is queued as the attack's own damage
///   (`ApplyQueuedAttackDamage`), as the 2-Benched choices are, and its coin sometimes prevents the
///   50 and sometimes not.
/// - G2 off: the plain `ApplyDamage` of the same 2 targets, as the 2-Benched choices are queued
///   then; its coin still flips through G1 (the plain-hit coin).
/// - G1 off too: no coin, the 50 lands every time.
///
/// Snorlax takes the 130 every time.
#[test]
fn test_mega_blastoise_ex_triple_bombardment_on_a_lone_benched_coin_pokemon_with_g2_on_and_off() {
    // (G1, G2, whether the choice takes the coin path, whether the coin flips).
    let settings = [
        (true, true, true, true),
        (true, false, false, true),
        (false, false, false, false),
    ];
    for mega in [CardId::B1a020MegaBlastoiseEx, CardId::B4b414MegaBlastoiseEx] {
        for (coin, hp) in [(CardId::A4080Togekiss, 140), (CardId::B2124Meowth, 50)] {
            for (g1, g2, coin_path, flips) in settings {
                let (mut prevented, mut hit) = (0, 0);
                for seed in 0..60u64 {
                    let game = with_plain_hit_coin(g1, || {
                        with_queued_site_coin(g2, || {
                            let mut game = attack_from_the_legal_actions(
                                seed,
                                mega,
                                vec![EnergyType::Water; 6],
                                vec![snorlax(), PlayedCard::from_id(coin)],
                            );
                            assert_eq!(
                                queued_picks(&game),
                                vec![(coin_path, vec![(130, 0), (50, 1)])],
                                "{mega:?}, {coin:?}, G1 {g1}, G2 {g2}, seed {seed}"
                            );
                            let (_, choices) = game.get_state_clone().generate_possible_actions();
                            game.apply_action(&choices[0]);
                            // The attack's reactions settle before its Knock Out wave.
                            game.play_until_stable();
                            game
                        })
                    });
                    let state = game.get_state_clone();
                    assert_eq!(state.get_remaining_hp(1, 0), 150 - 130, "seed {seed}: Snorlax");
                    match state.in_play_pokemon[1][1].as_ref().map(|p| p.get_remaining_hp()) {
                        Some(left) if left == hp => prevented += 1,
                        Some(left) if left + 50 == hp => hit += 1,
                        None if hp <= 50 => hit += 1,
                        other => panic!("{mega:?}, seed {seed}: {coin:?} at {other:?}"),
                    }
                }
                let what =
                    format!("{mega:?}, {coin:?}, G1 {g1}, G2 {g2}: {prevented} prevented, {hit} hit");
                if flips {
                    assert!(prevented > 10 && hit > 10, "{what}: the coin must flip");
                } else {
                    assert_eq!((prevented, hit), (0, 60), "{what}: no coin");
                }
            }
        }
    }
}
