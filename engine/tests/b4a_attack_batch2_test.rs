use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard, StatusCondition, TrainerCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

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

/// CoinFlipToBlockAttack's interaction with Victory Star has not been seen in Pocket, so the repair leaves it as it
/// was: an attacker carrying it gets no Victory Star offer, Confused or not.
#[test]
fn coin_flip_to_block_attack_keeps_its_resolution_without_a_victory_star_offer() {
    for confused in [false, true] {
        for seed in 0..40 {
            let mut attacker = moltres(CardId::B4a007TeamRocketsMoltresEx);
            if confused {
                attacker = attacker.with_status_condition(StatusCondition::Confused);
            }
            attacker.add_effect(CardEffect::CoinFlipToBlockAttack, 1);
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                3,
                vec![attacker, PlayedCard::from_id(CardId::B3025Victini)],
                vec![sponge(0)],
            );
            game.apply_action(&attack(CardId::B4a007TeamRocketsMoltresEx, 0));
            assert!(game.get_state_clone().pending_attack_coin_choice.is_none(), "confused {confused}, seed {seed}");
            assert!(!offers_victory_star(&game), "confused {confused}, seed {seed}");
        }
    }
}
