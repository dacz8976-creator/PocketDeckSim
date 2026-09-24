use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerCard},
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
