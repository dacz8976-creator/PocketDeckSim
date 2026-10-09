use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard, StatusCondition, TrainerCard},
    state::State,
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
use rand::{rngs::StdRng, SeedableRng};
use std::collections::BTreeMap;

fn sponge(damage: u32) -> PlayedCard {
    PlayedCard::new(
        get_card_by_enum(CardId::PB024MegaLatiosEx),
        damage,
        400,
        vec![],
        false,
        vec![],
    )
}

fn game(seed: u64, attacker: PlayedCard, defender: PlayedCard) -> Game<'static> {
    get_initialized_game_with_board(seed, 0, 3, vec![attacker], vec![defender])
}

fn attack(card_id: CardId, index: usize) -> Action {
    Action {
        actor: 0,
        action: attack_action(card_id, index),
        is_stack: false,
    }
}

fn keep() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::KeepAttackCoinResults,
        is_stack: true,
    }
}

fn reroll(source: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::RerollAttackCoins {
            victory_star_in_play_idx: source,
        },
        is_stack: true,
    }
}

fn trainer(card_id: CardId) -> TrainerCard {
    match get_card_by_enum(card_id) {
        Card::Trainer(card) => card,
        _ => panic!("expected Trainer card"),
    }
}

fn moltres(card_id: CardId) -> PlayedCard {
    PlayedCard::from_id(card_id).with_energy(vec![EnergyType::Fire])
}

#[test]
fn heat_charged_attaches_one_fire_energy_per_head_for_all_reprints() {
    for card_id in [
        CardId::B4a007TeamRocketsMoltresEx,
        CardId::B4a079TeamRocketsMoltresEx,
        CardId::B4a088TeamRocketsMoltresEx,
    ] {
        let mut observed = [false; 4];
        for seed in 0..120 {
            let mut game = game(seed, moltres(card_id), sponge(0));
            game.apply_action(&attack(card_id, 0));
            let attached = game.get_state_clone().get_active(0).attached_energy.len();
            assert!((1..=4).contains(&attached));
            observed[attached - 1] = true;
        }
        assert!(observed.iter().all(|seen| *seen));
    }
}

#[test]
fn victory_star_pauses_heat_charged_before_energy_and_keep_commits_once() {
    let card_id = CardId::B4a007TeamRocketsMoltresEx;
    for seed in 0..20 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![moltres(card_id), PlayedCard::from_id(CardId::B3025Victini)],
            vec![sponge(0)],
        );
        game.apply_action(&attack(card_id, 0));
        let paused = game.get_state_clone();
        let pending = paused
            .pending_attack_coin_choice
            .as_ref()
            .expect("Heat Charged should pause for Victory Star");
        assert_eq!(pending.flips.len(), 3);
        assert_eq!(paused.get_active(0).attached_energy.len(), 1);
        let expected = 1 + pending.flips.iter().filter(|heads| **heads).count();

        game.apply_action(&keep());
        let committed = game.get_state_clone();
        assert_eq!(committed.get_active(0).attached_energy.len(), expected);
        assert!(committed.pending_attack_coin_choice.is_none());
    }
}

#[test]
fn victory_star_reroll_discards_heat_charged_first_batch_instead_of_double_attaching() {
    let card_id = CardId::B4a007TeamRocketsMoltresEx;
    let mut saw_favorable_first_batch_replaced_by_fewer_heads = false;
    for seed in 0..500 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![moltres(card_id), PlayedCard::from_id(CardId::B3025Victini)],
            vec![sponge(0)],
        );
        game.apply_action(&attack(card_id, 0));
        let pending = game
            .get_state_clone()
            .pending_attack_coin_choice
            .expect("Heat Charged should pause for Victory Star");
        let first_heads = pending.flips.iter().filter(|heads| **heads).count();
        game.apply_action(&reroll(pending.victory_star_in_play_idx));
        let final_attached = game.get_state_clone().get_active(0).attached_energy.len();
        assert!(
            final_attached <= 4,
            "the ignored first batch must never attach"
        );
        if final_attached - 1 < first_heads {
            saw_favorable_first_batch_replaced_by_fewer_heads = true;
            break;
        }
    }
    assert!(saw_favorable_first_batch_replaced_by_fewer_heads);
}

#[test]
fn will_forces_heat_charged_first_flip_and_is_consumed_before_victory_star_choice() {
    let card_id = CardId::B4a007TeamRocketsMoltresEx;
    for seed in 0..20 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![moltres(card_id), PlayedCard::from_id(CardId::PB049Victini)],
            vec![sponge(0)],
        );
        let will = trainer(CardId::A4156Will);
        let mut state = game.get_state_clone();
        state.hands[0].push(Card::Trainer(will.clone()));
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play { trainer_card: will },
            is_stack: false,
        });
        game.apply_action(&attack(card_id, 0));
        let paused = game.get_state_clone();
        let pending = paused.pending_attack_coin_choice.as_ref().unwrap();
        assert_eq!(pending.flips.first(), Some(&true));
        assert_eq!(paused.get_active(0).attached_energy.len(), 1);
        let expected = 1 + pending.flips.iter().filter(|heads| **heads).count();
        game.apply_action(&keep());
        assert_eq!(
            game.get_state_clone().get_active(0).attached_energy.len(),
            expected
        );
    }
}

#[test]
fn effect_only_heat_charged_does_not_consume_the_defenders_first_damage_shield() {
    let card_id = CardId::B4a007TeamRocketsMoltresEx;
    let mut game = game(
        0,
        moltres(card_id),
        PlayedCard::from_id(CardId::B2073MimikyuEx),
    );
    let will = trainer(CardId::A4156Will);
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(will.clone()));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: will },
        is_stack: false,
    });

    game.apply_action(&attack(card_id, 0));
    let after = game.get_state_clone();
    assert!(after.get_active(0).attached_energy.len() >= 2);
    assert!(!after.get_active(1).prevent_first_attack_damage_used);
}

#[test]
fn evil_inspiration_draws_one_from_active_once_per_turn_for_all_reprints() {
    for card_id in [
        CardId::B4a026TeamRocketsSlowkingEx,
        CardId::B4a082TeamRocketsSlowkingEx,
        CardId::B4a091TeamRocketsSlowkingEx,
    ] {
        let mut game = game(0, PlayedCard::from_id(card_id), sponge(0));
        let drawn = get_card_by_enum(CardId::A1001Bulbasaur);
        let mut state = game.get_state_clone();
        state.hands[0].clear();
        state.decks[0].cards = vec![drawn.clone()];
        game.set_state(state);

        let (_, actions) = game.get_state_clone().generate_possible_actions();
        let ability = actions
            .into_iter()
            .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 }))
            .expect("active Evil Inspiration should be offered");
        game.apply_action(&ability);
        game.play_until_stable();
        let after = game.get_state_clone();
        assert_eq!(after.hands[0], vec![drawn]);
        assert!(after.decks[0].cards.is_empty());
        assert!(after.get_active(0).ability_used);
        assert!(!after.generate_possible_actions().1.iter().any(|action| {
            matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 })
        }));
    }
}

#[test]
fn evil_inspiration_requires_active_spot_and_a_card_to_draw() {
    let slowking = CardId::B4a026TeamRocketsSlowkingEx;
    let mut benched_game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(slowking),
        ],
        vec![sponge(0)],
    );
    let mut state = benched_game.get_state_clone();
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander)];
    benched_game.set_state(state);
    assert!(!benched_game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 1 })));

    let mut empty_game = game(0, PlayedCard::from_id(slowking), sponge(0));
    let mut state = empty_game.get_state_clone();
    state.decks[0].cards.clear();
    empty_game.set_state(state);
    assert!(!empty_game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 })));
}

#[test]
fn hand_kinesis_adds_twenty_damage_per_card_in_hand_for_all_reprints() {
    for card_id in [
        CardId::B4a026TeamRocketsSlowkingEx,
        CardId::B4a082TeamRocketsSlowkingEx,
        CardId::B4a091TeamRocketsSlowkingEx,
    ] {
        for hand_size in [0, 3, 10] {
            let attacker = PlayedCard::from_id(card_id)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]);
            let mut game = game(0, attacker, sponge(0));
            let mut state = game.get_state_clone();
            state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur); hand_size];
            game.set_state(state);
            game.apply_action(&attack(card_id, 0));
            assert_eq!(
                400 - game.get_state_clone().get_active(1).get_remaining_hp(),
                hand_size as u32 * 20,
            );
        }
    }
}

#[test]
fn draconic_slam_loses_one_hundred_damage_only_when_regidrago_is_damaged() {
    for (damage_on_attacker, expected) in [(0, 140), (10, 40)] {
        let attacker = PlayedCard::from_id(CardId::B4a057Regidrago)
            .with_damage(damage_on_attacker)
            .with_energy(vec![
                EnergyType::Grass,
                EnergyType::Fire,
                EnergyType::Colorless,
            ]);
        let mut game = game(0, attacker, sponge(0));
        game.apply_action(&attack(CardId::B4a057Regidrago, 0));
        assert_eq!(
            400 - game.get_state_clone().get_active(1).get_remaining_hp(),
            expected,
        );
    }
}

#[test]
fn second_strike_adds_seventy_only_when_the_defender_is_already_damaged() {
    for (defender_damage, expected_attack_damage) in [(0, 20), (10, 90)] {
        let attacker = PlayedCard::from_id(CardId::PB088TeamRocketsScyther)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless]);
        let mut game = game(0, attacker, sponge(defender_damage));
        let before = game.get_state_clone().get_active(1).get_remaining_hp();
        game.apply_action(&attack(CardId::PB088TeamRocketsScyther, 0));
        assert_eq!(
            before - game.get_state_clone().get_active(1).get_remaining_hp(),
            expected_attack_damage,
        );
    }
}

/// Team Rocket's Moltres ex (Heat Charged: flip 3 coins, a [R] Energy for each heads) with one [R] Energy, Confused,
/// with Victini (Victory Star) on the Bench.
fn confused_moltres_with_victini(seed: u64) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![
            moltres(CardId::B4a007TeamRocketsMoltresEx).with_status_condition(StatusCondition::Confused),
            PlayedCard::from_id(CardId::B3025Victini),
        ],
        vec![sponge(0)],
    )
}

fn offers_victory_star(game: &Game) -> bool {
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    choices.iter().any(|choice| {
        matches!(
            choice.action,
            SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. }
        )
    })
}

/// rules/04 §9, observed in-game Sept 29 (Recording_QA 202314 and 203025; rules/09's Victory Star item): with a
/// Confused attacker the Confusion coin comes first and is never offered for a reroll. On tails the attack does
/// nothing and no Victory Star offer appears. On heads the attack's own coins are flipped and Victory Star is offered
/// on them; keeping them resolves the attack, with no second Confusion check.
#[test]
fn confused_heat_charged_flips_confusion_first_then_offers_victory_star_on_its_own_coins() {
    let (mut offered, mut confusion_tails) = (0, 0);
    for seed in 0..200 {
        let mut game = confused_moltres_with_victini(seed);
        game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
        let after = game.get_state_clone();
        match after.pending_attack_coin_choice.clone() {
            None => {
                // Confusion tails: Heat Charged does nothing, and no Victory Star offer appears.
                assert_eq!(after.get_active(0).attached_energy.len(), 1, "seed {seed}: tails attaches nothing");
                assert!(!offers_victory_star(&game), "seed {seed}: no offer on the Confusion coin");
                confusion_tails += 1;
            }
            Some(pending) => {
                // Confusion heads: the offer is on Heat Charged's own three coins, before any Energy is attached.
                assert_eq!(pending.flips.len(), 3, "seed {seed}");
                assert_eq!(after.get_active(0).attached_energy.len(), 1, "seed {seed}");
                assert!(offers_victory_star(&game), "seed {seed}");
                let expected = 1 + pending.flips.iter().filter(|heads| **heads).count();
                game.apply_action(&keep());
                // No second Confusion check: the kept coins always resolve.
                assert_eq!(game.get_state_clone().get_active(0).attached_energy.len(), expected, "seed {seed}");
                offered += 1;
            }
        }
    }
    assert!(offered > 60 && confusion_tails > 60, "{offered} offers, {confusion_tails} Confusion tails");
}

/// The same order with a reroll (203025: Victory Star taken, the three coins rerolled, no second Confusion check).
/// Every reroll resolves its fresh coins: nothing attaches only when all three are tails (1 in 8), where a second
/// Confusion check would make it nearly 1 in 2.
#[test]
fn a_victory_star_reroll_after_confusion_heads_resolves_with_no_second_confusion_check() {
    let (mut rerolls, mut nothing_attached) = (0, 0);
    for seed in 0..400 {
        let mut game = confused_moltres_with_victini(seed);
        game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
        let Some(pending) = game.get_state_clone().pending_attack_coin_choice else {
            continue;
        };
        game.apply_action(&reroll(pending.victory_star_in_play_idx));
        let after = game.get_state_clone();
        assert!(after.pending_attack_coin_choice.is_none());
        assert!(after.victory_star_used_this_turn[0]);
        let attached = after.get_active(0).attached_energy.len();
        assert!((1..=4).contains(&attached), "seed {seed}");
        rerolls += 1;
        nothing_attached += (attached == 1) as usize;
    }
    assert!(rerolls > 120, "{rerolls} rerolls");
    assert!(nothing_attached * 4 < rerolls, "{nothing_attached} of {rerolls} rerolls attached nothing");
}

/// Plays Will (A4 156) from player 0's hand.
fn play_will(game: &mut Game) {
    let will = trainer(CardId::A4156Will);
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(will.clone()));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: will },
        is_stack: false,
    });
}

/// Team Rocket's Moltres ex with one [R] Energy, Confused, with `bench` on the Bench, after Will is played this turn.
fn confused_moltres_after_will(seed: u64, bench: CardId) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![
            moltres(CardId::B4a007TeamRocketsMoltresEx).with_status_condition(StatusCondition::Confused),
            PlayedCard::from_id(bench),
        ],
        vec![sponge(0)],
    );
    play_will(&mut game);
    game
}

/// Will's "the first coin flip will definitely be heads" is still waiting this turn (the state's own turn effects).
fn will_pending(state: &State) -> bool {
    let json = serde_json::to_value(state).expect("State serialises");
    json["turn_effects"][state.turn_count.to_string()]
        .as_array()
        .is_some_and(|effects| effects.iter().any(|effect| effect == "ForceFirstHeads"))
}

/// Will (A4 156) with a Confused attacker, by the card text (Dustin, Oct 1: plain card text is the rule). Will names the
/// coins flipped "for the effect of an attack, Ability, or Trainer card"; the Confusion coin is not one of them, so it
/// does not use Will. On Confusion heads Will makes the attack's first coin heads and Victory Star is still offered on
/// the attack's coins; on Confusion tails the attack flips nothing for its effect and Will is still waiting. A Victory
/// Star reroll is a fresh batch that Will does not touch. Recording_QA 210403, T14, shows the same: Confusion heads at
/// 342 s, Will's guaranteed heads on Heat Charged's coin screen at about 347 s, Victory Star offered at 354 s; 203626,
/// T12, shows a reroll with Will not reapplied. This replaces Sonnet's F4 guard test, which pinned the old resolution
/// (no pause, no offer, Will left on the Confusion path).
#[test]
fn confusion_with_will_pending_forces_the_attacks_first_coin_and_still_offers_victory_star() {
    let card_id = CardId::B4a007TeamRocketsMoltresEx;
    let (mut offered, mut confusion_tails, mut rerolls_all_tails) = (0, 0, 0);
    for seed in 0..200 {
        let mut game = confused_moltres_after_will(seed, CardId::B3025Victini);
        game.apply_action(&attack(card_id, 0));
        let after = game.get_state_clone();
        match after.pending_attack_coin_choice.clone() {
            None => {
                // Confusion tails: Heat Charged does nothing, no Victory Star offer, and Will is not used.
                assert_eq!(after.get_active(0).attached_energy.len(), 1, "seed {seed}: tails attaches nothing");
                assert!(!offers_victory_star(&game), "seed {seed}: no offer on the Confusion coin");
                assert!(will_pending(&after), "seed {seed}: no coin flipped for the attack's effect, Will still waits");
                confusion_tails += 1;
            }
            Some(pending) => {
                // Confusion heads: Will's heads on Heat Charged's first coin, and the offer on its three coins.
                assert_eq!(pending.flips.len(), 3, "seed {seed}");
                assert_eq!(pending.flips.first(), Some(&true), "seed {seed}: Will's heads on the attack's first coin");
                assert!(!will_pending(&after), "seed {seed}: Will is used on Heat Charged's coins");
                assert_eq!(after.get_active(0).attached_energy.len(), 1, "seed {seed}");
                assert!(offers_victory_star(&game), "seed {seed}");
                let expected = 1 + pending.flips.iter().filter(|heads| **heads).count();
                game.apply_action(&keep());
                assert_eq!(game.get_state_clone().get_active(0).attached_energy.len(), expected, "seed {seed}");
                // The same seed again, rerolled: three fresh coins, the first not forced.
                let mut rerolled = confused_moltres_after_will(seed, CardId::B3025Victini);
                rerolled.apply_action(&attack(card_id, 0));
                assert_eq!(rerolled.get_state_clone().pending_attack_coin_choice, Some(pending.clone()), "seed {seed}");
                rerolled.apply_action(&reroll(pending.victory_star_in_play_idx));
                let attached = rerolled.get_state_clone().get_active(0).attached_energy.len();
                assert!((1..=4).contains(&attached), "seed {seed}");
                rerolls_all_tails += (attached == 1) as usize;
                offered += 1;
            }
        }
    }
    assert!(offered > 60 && confusion_tails > 60, "{offered} offers, {confusion_tails} Confusion tails");
    assert!(rerolls_all_tails > 0, "no reroll of {offered} came up all tails: Will forced a reroll's first coin");
}

/// The same with nothing for Victory Star to work on, exactly (the attack's forecast). Confusion tails, 1/2: nothing
/// attaches and Will still waits. Confusion heads: Will makes Heat Charged's first coin heads, so it attaches 1, 2 or 3
/// Energy with 1/4, 1/2 and 1/4 of that half, and Will is used. Before the fix Will found no attack coin behind the
/// Confusion coin: it stayed pending and the three coins were all fair.
#[test]
fn confusion_with_will_pending_forces_the_attacks_first_coin_without_victory_star() {
    let state = confused_moltres_after_will(0, CardId::A1001Bulbasaur).get_state_clone();
    assert!(will_pending(&state));
    let action = attack(CardId::B4a007TeamRocketsMoltresEx, 0);
    let mut by_result: BTreeMap<(usize, bool), f64> = BTreeMap::new();
    for (probability, mutation, _) in try_forecast_action(&state, &action)
        .expect("Heat Charged is exactly priced")
        .into_branches_with_coin_paths()
    {
        let mut next = state.clone();
        mutation(&mut StdRng::seed_from_u64(0), &mut next, &action);
        *by_result
            .entry((next.get_active(0).attached_energy.len(), will_pending(&next)))
            .or_default() += probability;
    }
    let expected = [((1, true), 0.5), ((2, false), 0.125), ((3, false), 0.25), ((4, false), 0.125)];
    assert_eq!(
        by_result.keys().copied().collect::<Vec<_>>(),
        expected.iter().map(|(key, _)| *key).collect::<Vec<_>>(),
        "(attached Energy, Will still pending) -> probability: {by_result:?}"
    );
    for (key, probability) in expected {
        assert!((by_result[&key] - probability).abs() < 1e-9, "{key:?}: {by_result:?}");
    }
}

/// Team Rocket's Moltres ex with one [R] Energy under a block coin (Weezing's Smokescreen and the like: "During your
/// opponent's next turn, if the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that
/// attack doesn't happen."), Confused when `confused`, with `bench` on the Bench; after Will when `will`.
fn blocked_moltres(seed: u64, confused: bool, bench: CardId, will: bool) -> Game<'static> {
    let mut attacker = moltres(CardId::B4a007TeamRocketsMoltresEx);
    if confused {
        attacker = attacker.with_status_condition(StatusCondition::Confused);
    }
    attacker.add_effect(CardEffect::CoinFlipToBlockAttack, 1);
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![attacker, PlayedCard::from_id(bench)],
        vec![sponge(0)],
    );
    if will {
        play_will(&mut game);
    }
    game
}

/// The attack's exact forecast, as (attached Energy, Will still pending, probability), merged by the first two.
fn heat_charged_results(state: &State) -> Vec<(usize, bool, f64)> {
    let action = attack(CardId::B4a007TeamRocketsMoltresEx, 0);
    let mut by_result: BTreeMap<(usize, bool), f64> = BTreeMap::new();
    for (probability, mutation, _) in try_forecast_action(state, &action)
        .expect("Heat Charged is exactly priced")
        .into_branches_with_coin_paths()
    {
        let mut next = state.clone();
        mutation(&mut StdRng::seed_from_u64(0), &mut next, &action);
        *by_result
            .entry((next.get_active(0).attached_energy.len(), will_pending(&next)))
            .or_default() += probability;
    }
    by_result.into_iter().map(|((attached, will), p)| (attached, will, p)).collect()
}

/// Victory Star with a block coin (TEXT_AUDIT.md A1; the card text, Dustin's rule of Oct 1). The block coin is flipped
/// when the Pokémon "tries to use an attack", so it comes first; it is flipped for the effect of the opponent's attack,
/// not "for an attack of 1 of your [R] Pokémon", so Victory Star is never offered on it. On its tails the attack doesn't
/// happen; on its heads Heat Charged's own coins are flipped and Victory Star is offered on them, and neither a kept nor
/// a rerolled batch meets a second block coin. A Confused attacker flips both coins first. These replace the two tests
/// that pinned the old resolution (no offer at all; the result of the path with Victory Star already used).
#[test]
fn a_block_coin_comes_first_then_victory_star_is_offered_on_the_attacks_own_coins() {
    for confused in [false, true] {
        let (mut offered, mut rerolls, mut rerolls_attaching_nothing) = (0, 0, 0);
        for seed in 0..400 {
            let mut game = blocked_moltres(seed, confused, CardId::B3025Victini, false);
            game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
            let after = game.get_state_clone();
            let Some(pending) = after.pending_attack_coin_choice.clone() else {
                // A gate coin's tails: the attack doesn't happen, and no offer appears.
                assert_eq!(after.get_active(0).attached_energy.len(), 1, "confused {confused}, seed {seed}");
                assert!(!offers_victory_star(&game), "confused {confused}, seed {seed}: no offer on a gate coin");
                continue;
            };
            assert_eq!(pending.flips.len(), 3, "confused {confused}, seed {seed}");
            assert_eq!(after.get_active(0).attached_energy.len(), 1, "confused {confused}, seed {seed}");
            assert!(offers_victory_star(&game), "confused {confused}, seed {seed}");
            let expected = 1 + pending.flips.iter().filter(|heads| **heads).count();
            let mut rerolled = blocked_moltres(seed, confused, CardId::B3025Victini, false);
            rerolled.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
            game.apply_action(&keep());
            // No second block coin: the kept coins always resolve.
            assert_eq!(game.get_state_clone().get_active(0).attached_energy.len(), expected, "confused {confused}, seed {seed}");
            rerolled.apply_action(&reroll(pending.victory_star_in_play_idx));
            let attached = rerolled.get_state_clone().get_active(0).attached_energy.len();
            assert!((1..=4).contains(&attached), "confused {confused}, seed {seed}");
            rerolls += 1;
            rerolls_attaching_nothing += (attached == 1) as usize;
            offered += 1;
        }
        // One gate coin pauses half the attacks; with Confusion as well, a quarter.
        let expected = if confused { 100 } else { 200 };
        assert!(
            offered * 4 > expected * 3 && offered * 4 < expected * 5,
            "confused {confused}: {offered} offers of 400, about {expected} expected"
        );
        // A reroll attaches nothing only on three tails (1 in 8); a second block coin would make it nearly 1 in 2.
        assert!(rerolls_attaching_nothing * 4 < rerolls, "confused {confused}: {rerolls_attaching_nothing} of {rerolls}");
    }
}

/// Will with a block coin (TEXT_AUDIT.md A2). The block coin is flipped by the attacking player for the effect of an
/// attack (the opponent's Smokescreen), so it is the next coin Will covers: it comes up heads, the attack happens, Will
/// is used, and Heat Charged's own three coins are fair. A Confusion coin (not for the effect of an attack) stays fair.
/// Before the fix Will found no coin behind the gates and lapsed, and the block coin was fair.
#[test]
fn will_makes_the_block_coin_heads_and_leaves_the_attacks_own_coins_fair() {
    // Heat Charged's three fair coins: 0, 1, 2 or 3 heads with 1/8, 3/8, 3/8, 1/8.
    let fair = [(1, 0.125), (2, 0.375), (3, 0.375), (4, 0.125)];
    for confused in [false, true] {
        let state = blocked_moltres(0, confused, CardId::A1001Bulbasaur, true).get_state_clone();
        assert!(will_pending(&state));
        let results = heat_charged_results(&state);
        for (attached, will, _) in &results {
            if *attached > 1 {
                assert!(!will, "confused {confused}: the attack happened, so Will was used on the block coin: {results:?}");
            }
        }
        for (attached, p) in fair {
            // A Confusion tails (1/2) attaches nothing; otherwise the attack happens (Will's heads on the block coin).
            let expected = if confused { 0.5 * p + if attached == 1 { 0.5 } else { 0.0 } } else { p };
            let got: f64 = results.iter().filter(|(a, _, _)| *a == attached).map(|(_, _, p)| p).sum();
            assert!((got - expected).abs() < 1e-9, "confused {confused}, {attached} Energy: {got} vs {expected}: {results:?}");
        }
    }
}

/// Will, a block coin and Victory Star together (TEXT_AUDIT.md A1 and A2): Will's heads goes on the block coin, so the
/// attack always happens and pauses for Victory Star, Will is already used at the pause, and Heat Charged's own first
/// coin is fair.
#[test]
fn will_on_the_block_coin_then_victory_star_on_the_attacks_fair_coins() {
    let mut first_tails = 0;
    for seed in 0..100 {
        let mut game = blocked_moltres(seed, false, CardId::B3025Victini, true);
        game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
        let after = game.get_state_clone();
        let pending = after
            .pending_attack_coin_choice
            .clone()
            .unwrap_or_else(|| panic!("seed {seed}: Will's heads on the block coin, so the attack happens and pauses"));
        assert!(!will_pending(&after), "seed {seed}: Will was used on the block coin");
        assert!(offers_victory_star(&game), "seed {seed}");
        first_tails += (pending.flips.first() == Some(&false)) as usize;
    }
    assert!(first_tails > 25, "{first_tails} first tails of 100: Will forced the attack's own first coin too");
}

// ---- Revert switches (rules switch 2, PLAN (e); the coordinator's brief of Oct 9) for G4 (Will on the gate coins) and G5
// (Victory Star after a block coin). Each `revert_*` test re-runs a scenario above with the gate's switch off and asserts
// the engine before it (the official engine, main-8626a35), and with the switch on, the current result. Old values:
// `rl/results/coin_prevention_round2_2026-10-01/tests_before_fix_will.log` and `tests_before_fix_text.log`, and the pins
// removed at 8626a358.

/// `heat_charged_results` against `expected`: the same (attached Energy, Will still pending) keys, each probability within
/// 1e-9.
fn assert_heat_charged_results(results: &[(usize, bool, f64)], expected: &[(usize, bool, f64)], label: &str) {
    let keys = |list: &[(usize, bool, f64)]| list.iter().map(|(attached, will, _)| (*attached, *will)).collect::<Vec<_>>();
    assert_eq!(keys(results), keys(expected), "{label}: (attached Energy, Will still pending, probability): {results:?}");
    for ((_, _, got), (_, _, want)) in results.iter().zip(expected) {
        assert!((got - want).abs() < 1e-9, "{label}: {results:?}");
    }
}

/// G4, Will (`with_will_on_gate_coins(false, ..)`): with a Confused attacker Will finds no coin behind the Confusion coin,
/// so it stays pending and Heat Charged's three coins are fair
/// (`confusion_with_will_pending_forces_the_attacks_first_coin_without_victory_star`). Old: {(1, true): 0.5625,
/// (2, true): 0.1875, (3, true): 0.1875, (4, true): 0.0625} (`tests_before_fix_will.log:34`).
#[test]
fn revert_g4_will_skips_the_attack_coins_behind_a_confusion_coin() {
    use deckgym::actions::with_will_on_gate_coins;
    let forecast = || heat_charged_results(&confused_moltres_after_will(0, CardId::A1001Bulbasaur).get_state_clone());
    assert_heat_charged_results(
        &with_will_on_gate_coins(false, forecast),
        &[(1, true, 0.5625), (2, true, 0.1875), (3, true, 0.1875), (4, true, 0.0625)],
        "switch off",
    );
    assert_heat_charged_results(
        &with_will_on_gate_coins(true, forecast),
        &[(1, true, 0.5), (2, false, 0.125), (3, false, 0.25), (4, false, 0.125)],
        "switch on",
    );
}

/// G4 with Victory Star (`confusion_with_will_pending_forces_the_attacks_first_coin_and_still_offers_victory_star`): a
/// Confused attacker with Will pending gets no pause and no offer, Victory Star stays unused, and the result is the same
/// seed's with nothing for Victory Star to work on. The pin removed at 8626a358
/// (`confusion_with_will_pending_keeps_the_legacy_resolution_without_a_victory_star_offer`, b4a_attack_batch2_test.rs:
/// 437-477 there), verbatim inside the switch, plus Will still pending (every branch of `tests_before_fix_will.log:34`).
/// `tests_before_fix_will.log:28-29` shows the missing pause (seed 1 resolved without one).
#[test]
fn revert_g4_confusion_with_will_pending_keeps_the_old_resolution_without_a_victory_star_offer() {
    use deckgym::actions::with_will_on_gate_coins;
    let card_id = CardId::B4a007TeamRocketsMoltresEx;
    let play_will_then_attack = |seed: u64, bench: CardId| {
        let mut game = confused_moltres_after_will(seed, bench);
        game.apply_action(&attack(card_id, 0));
        game
    };
    let resolved = with_will_on_gate_coins(false, || {
        let mut resolved = 0;
        for seed in 0..60 {
            let with_victini = play_will_then_attack(seed, CardId::B3025Victini);
            let without = play_will_then_attack(seed, CardId::A1001Bulbasaur);
            let (a, b) = (with_victini.get_state_clone(), without.get_state_clone());
            assert!(a.pending_attack_coin_choice.is_none(), "seed {seed}: no pause");
            assert!(!offers_victory_star(&with_victini), "seed {seed}: no offer");
            assert!(!a.victory_star_used_this_turn[0], "seed {seed}: Victory Star unused");
            assert!(will_pending(&a), "seed {seed}: Will still pending");
            // The old result: what the same seed gives with nothing for Victory Star to work on.
            assert_eq!(a.get_active(0).attached_energy.len(), b.get_active(0).attached_energy.len(), "seed {seed}");
            assert_eq!(a.get_active(1).get_remaining_hp(), b.get_active(1).get_remaining_hp(), "seed {seed}");
            assert_eq!(a.generate_possible_actions().1.len(), b.generate_possible_actions().1.len(), "seed {seed}");
            resolved += (a.get_active(0).attached_energy.len() > 1) as usize;
        }
        resolved
    });
    assert!(resolved > 10, "the attack resolved (attached Energy) in only {resolved} of 60 seeds");
    let paused = with_will_on_gate_coins(true, || {
        (0..60)
            .filter(|&seed| {
                let game = play_will_then_attack(seed, CardId::B3025Victini);
                game.get_state_clone().pending_attack_coin_choice.is_some()
            })
            .count()
    });
    assert!(paused > 10, "switch on: a Confusion heads pauses for Victory Star, but only {paused} of 60 paused");
}

/// G4 with a block coin (`will_makes_the_block_coin_heads_and_leaves_the_attacks_own_coins_fair`, not Confused): Will
/// doesn't go to the block coin, which stays fair, and Will stays pending. Old: [(1, true, 0.5625), (2, true, 0.1875),
/// (3, true, 0.1875), (4, true, 0.0625)] (`tests_before_fix_text.log:35`). The Confused case has no logged old value (the
/// old run stopped at the first case), so it is left to the existing test with the switch on.
#[test]
fn revert_g4_will_leaves_the_block_coin_fair() {
    use deckgym::actions::with_will_on_gate_coins;
    let forecast = || heat_charged_results(&blocked_moltres(0, false, CardId::A1001Bulbasaur, true).get_state_clone());
    assert_heat_charged_results(
        &with_will_on_gate_coins(false, forecast),
        &[(1, true, 0.5625), (2, true, 0.1875), (3, true, 0.1875), (4, true, 0.0625)],
        "switch off",
    );
    // Switch on: the existing test's result, Will's heads on the block coin and Heat Charged's three coins fair.
    let results = with_will_on_gate_coins(true, forecast);
    for (attached, will, _) in &results {
        assert!(*attached == 1 || !will, "switch on: the attack happened, so Will was used on the block coin: {results:?}");
    }
    for (attached, p) in [(1, 0.125), (2, 0.375), (3, 0.375), (4, 0.125)] {
        let got: f64 = results.iter().filter(|(a, _, _)| *a == attached).map(|(_, _, p)| p).sum();
        assert!((got - p).abs() < 1e-9, "switch on, {attached} Energy: {got} vs {p}: {results:?}");
    }
}

/// G4 + G5, Will with a block coin and Victory Star (`will_on_the_block_coin_then_victory_star_on_the_attacks_fair_coins`).
/// The old engine never paused with a block coin, and Will skipped it: no pause, no offer, Victory Star unused, Will still
/// pending, and the same result as the same seed with Bulbasaur in Victini's place. Old: no pause at seed 0
/// (`tests_before_fix_text.log:40`), Will pending in every branch (`:35`). G4 alone gives it in full; so do G4 and G5
/// together.
#[test]
fn revert_g4_g5_will_with_a_block_coin_gives_no_victory_star_pause() {
    use deckgym::actions::{with_victory_star_after_block_coin, with_will_on_gate_coins};
    let old_path = || {
        let mut resolved = 0;
        for seed in 0..100 {
            let mut game = blocked_moltres(seed, false, CardId::B3025Victini, true);
            game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
            let mut without = blocked_moltres(seed, false, CardId::A1001Bulbasaur, true);
            without.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
            let (a, b) = (game.get_state_clone(), without.get_state_clone());
            assert!(a.pending_attack_coin_choice.is_none(), "seed {seed}: no pause");
            assert!(!offers_victory_star(&game), "seed {seed}: no offer");
            assert!(!a.victory_star_used_this_turn[0], "seed {seed}: Victory Star unused");
            assert!(will_pending(&a), "seed {seed}: Will skipped the block coin");
            assert_eq!(a.get_active(0).attached_energy.len(), b.get_active(0).attached_energy.len(), "seed {seed}");
            resolved += (a.get_active(0).attached_energy.len() > 1) as usize;
        }
        resolved
    };
    let g4 = with_will_on_gate_coins(false, old_path);
    assert!(g4 > 10, "G4 off: the attack resolved in only {g4} of 100 seeds");
    let both = with_will_on_gate_coins(false, || with_victory_star_after_block_coin(false, old_path));
    assert_eq!(both, g4, "G4 and G5 off together give G4's result");
    with_will_on_gate_coins(true, || {
        with_victory_star_after_block_coin(true, || {
            for seed in 0..100 {
                let mut game = blocked_moltres(seed, false, CardId::B3025Victini, true);
                game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
                assert!(game.get_state_clone().pending_attack_coin_choice.is_some(), "switches on, seed {seed}: the pause");
            }
        })
    });
}

/// G5, Victory Star after a block coin (`with_victory_star_after_block_coin(false, ..)`): an attacker carrying
/// CoinFlipToBlockAttack gets no Victory Star offer, Confused or not (`a_block_coin_comes_first_then_victory_star_is_
/// offered_on_the_attacks_own_coins`). The pin removed at 8626a358 (`coin_flip_to_block_attack_keeps_its_resolution_
/// without_a_victory_star_offer`, b4a_attack_batch2_test.rs:410-430 there), verbatim inside the switch.
/// `tests_before_fix_text.log:28-30` shows the old run with no pause (not Confused, seed 1).
#[test]
fn revert_g5_a_block_coin_keeps_its_resolution_without_a_victory_star_offer() {
    use deckgym::actions::with_victory_star_after_block_coin;
    with_victory_star_after_block_coin(false, || {
        for confused in [false, true] {
            for seed in 0..40 {
                let mut game = blocked_moltres(seed, confused, CardId::B3025Victini, false);
                game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
                assert!(game.get_state_clone().pending_attack_coin_choice.is_none(), "confused {confused}, seed {seed}");
                assert!(!offers_victory_star(&game), "confused {confused}, seed {seed}");
            }
        }
    });
    let paused = with_victory_star_after_block_coin(true, || {
        (0..40)
            .filter(|&seed| {
                let mut game = blocked_moltres(seed, false, CardId::B3025Victini, false);
                game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
                game.get_state_clone().pending_attack_coin_choice.is_some()
            })
            .count()
    });
    assert!(paused > 5, "switch on: a block coin's heads pauses for Victory Star, but only {paused} of 40 paused");
}

/// G5: with a block coin the result equals the old path's, which is what the same seed gives with Victory Star already
/// used this turn. The pin removed at 8626a358 (`coin_flip_to_block_attack_result_is_the_old_paths`,
/// b4a_attack_batch2_test.rs:483-518 there), verbatim inside the switch.
#[test]
fn revert_g5_a_block_coin_result_is_the_old_paths() {
    use deckgym::actions::with_victory_star_after_block_coin;
    with_victory_star_after_block_coin(false, || {
        for confused in [false, true] {
            for seed in 0..40 {
                let play = |used: bool| {
                    let mut game = blocked_moltres(seed, confused, CardId::B3025Victini, false);
                    let mut state = game.get_state_clone();
                    state.victory_star_used_this_turn[0] = used;
                    game.set_state(state);
                    game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
                    game.get_state_clone()
                };
                let (open, shut) = (play(false), play(true));
                assert_eq!(
                    open.get_active(0).attached_energy.len(),
                    shut.get_active(0).attached_energy.len(),
                    "confused {confused}, seed {seed}"
                );
                assert_eq!(
                    open.generate_possible_actions().1.len(),
                    shut.generate_possible_actions().1.len(),
                    "confused {confused}, seed {seed}"
                );
            }
        }
    });
}
