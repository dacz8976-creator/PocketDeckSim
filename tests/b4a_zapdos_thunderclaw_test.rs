use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
};

const ZAPDOS_PRINTINGS: [CardId; 3] = [
    CardId::B4a021TeamRocketsZapdosEx,
    CardId::B4a081TeamRocketsZapdosEx,
    CardId::B4a090TeamRocketsZapdosEx,
];

fn zapdos(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(vec![
        EnergyType::Lightning,
        EnergyType::Lightning,
        EnergyType::Colorless,
    ])
}

fn use_thunderclaw(game: &mut deckgym::Game<'static>, id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(id, 1),
        is_stack: false,
    });
}

fn bench_target_choice(game: &deckgym::Game<'static>, target_idx: usize) -> Action {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .all(|choice| matches!(choice.action, SimpleAction::ApplyQueuedAttackDamage { .. })),
        "Thunderclaw's mandatory follow-up must contain only attack-damage target choices"
    );
    choices
        .iter()
        .find(|choice| {
            matches!(
                &choice.action,
                SimpleAction::ApplyQueuedAttackDamage { targets, .. }
                    if targets.contains(&(50, true, target_idx))
            )
        })
        .expect("requested damaged Bench target should be offered")
        .clone()
}

#[test]
fn all_reprints_offer_only_damaged_opponent_bench_slots() {
    for id in ZAPDOS_PRINTINGS {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![zapdos(id)],
            vec![
                PlayedCard::from_id(CardId::A1004VenusaurEx),
                PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
                PlayedCard::from_id(CardId::A1056BlastoiseEx),
                PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(160),
            ],
        );

        use_thunderclaw(&mut game, id);
        let before_choice = game.get_state_clone();
        assert_eq!(before_choice.get_active(1).get_remaining_hp(), 190);

        let (_, choices) = before_choice.generate_possible_actions();
        assert_eq!(choices.len(), 2, "{id:?}");
        let mut slots = choices
            .iter()
            .map(|choice| match &choice.action {
                SimpleAction::ApplyQueuedAttackDamage { targets, .. } => targets
                    .iter()
                    .find_map(|(damage, opponent, idx)| {
                        (*damage == 50 && *opponent).then_some(*idx)
                    })
                    .unwrap(),
                other => panic!("unexpected target choice: {other:?}"),
            })
            .collect::<Vec<_>>();
        slots.sort_unstable();
        assert_eq!(slots, vec![1, 3], "{id:?}");
        assert!(!choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Noop)));
    }
}

#[test]
fn no_eligible_bench_still_deals_printed_active_damage() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![zapdos(id)],
        vec![
            PlayedCard::from_id(CardId::A1004VenusaurEx),
            PlayedCard::from_id(CardId::A1056BlastoiseEx),
        ],
    );

    use_thunderclaw(&mut game, id);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 100);
    assert!(state.move_generation_stack.is_empty());
}

#[test]
fn existing_unfiltered_choice_attack_still_offers_an_undamaged_bench() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B2a028Palafin)
            .with_energy(vec![EnergyType::Water, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::A1004VenusaurEx),
            PlayedCard::from_id(CardId::A1056BlastoiseEx),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2a028Palafin, 0),
        is_stack: false,
    });

    let choice = bench_target_choice(&game, 1);
    game.apply_action(&choice);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 140);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        130
    );
}

#[test]
fn legacy_self_bench_choice_keeps_its_own_side_guts_forecast() {
    let mut saw_guts_survive = false;
    let mut saw_knockout = false;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::A1103Zapdos).with_energy(vec![
                    EnergyType::Lightning,
                    EnergyType::Lightning,
                    EnergyType::Colorless,
                ]),
                PlayedCard::from_id(CardId::B3b058Ursaluna).with_remaining_hp(30),
            ],
            vec![PlayedCard::from_id(CardId::A1004VenusaurEx)],
        );
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::A1103Zapdos, 0),
            is_stack: false,
        });
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        let choice = choices
            .iter()
            .find(|action| {
                matches!(
                    &action.action,
                    SimpleAction::ApplyDamage { targets, .. }
                        if targets.contains(&(30, 0, 1))
                )
            })
            .expect("Raging Thunder should retain its own-Bench ApplyDamage choice")
            .clone();
        game.apply_action(&choice);

        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_remaining_hp(), 90, "seed {seed}");
        if let Some(ursaluna) = state.in_play_pokemon[0][1].as_ref() {
            saw_guts_survive = true;
            assert_eq!(ursaluna.get_remaining_hp(), 10, "seed {seed}");
        } else {
            saw_knockout = true;
            assert_eq!(state.points[1], 1, "seed {seed}");
        }
    }
    assert!(saw_guts_survive && saw_knockout);
}

#[test]
fn chosen_bench_damage_is_atomic_and_does_not_apply_bench_weakness() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![zapdos(id)],
        vec![
            PlayedCard::from_id(CardId::A1004VenusaurEx),
            // Blastoise ex is weak to Lightning, but Bench damage does not apply Weakness.
            PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
            PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(160),
        ],
    );

    use_thunderclaw(&mut game, id);
    let choice = bench_target_choice(&game, 1);
    game.apply_action(&choice);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 100);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        120
    );
    assert_eq!(
        state.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        160
    );
}

#[test]
fn protective_poncho_prevents_only_the_selected_bench_damage() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![zapdos(id)],
        vec![
            PlayedCard::from_id(CardId::A1004VenusaurEx),
            PlayedCard::from_id(CardId::A1056BlastoiseEx)
                .with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho))
                .with_remaining_hp(170),
        ],
    );

    use_thunderclaw(&mut game, id);
    let choice = bench_target_choice(&game, 1);
    game.apply_action(&choice);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 100);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        170
    );
}

#[test]
fn active_and_bench_knockouts_score_together_and_keep_attack_attribution() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![zapdos(id)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(50),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );

    use_thunderclaw(&mut game, id);
    let choice = bench_target_choice(&game, 1);
    game.apply_action(&choice);

    let state = game.get_state_clone();
    assert_eq!(state.points[0], 2);
    assert_eq!(state.points_gained_this_turn[0], 2);
    assert!(state.in_play_pokemon[1][0].is_none());
    assert!(state.in_play_pokemon[1][1].is_none());
    let (actor, promotion) = state.generate_possible_actions();
    assert_eq!(actor, 1);
    assert!(promotion
        .iter()
        .all(|action| matches!(action.action, SimpleAction::Promote { player: 1, .. })));
}

#[test]
fn defender_coin_reduction_is_forecast_on_the_selected_bench_target() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut saw_reduced = false;
    let mut saw_full = false;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![zapdos(id)],
            vec![
                PlayedCard::from_id(CardId::A1004VenusaurEx),
                PlayedCard::from_id(CardId::B3b050HisuianGoodra).with_remaining_hp(140),
            ],
        );
        use_thunderclaw(&mut game, id);
        let choice = bench_target_choice(&game, 1);
        game.apply_action(&choice);

        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_remaining_hp(), 100, "seed {seed}");
        match state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp()
        {
            140 => saw_reduced = true,
            90 => saw_full = true,
            hp => panic!("seed {seed}: unexpected Goodra HP {hp}"),
        }
    }
    assert!(saw_reduced && saw_full);
}

#[test]
fn bench_point_denial_coin_is_forecast_after_target_selection() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut saw_denied = false;
    let mut saw_scored = false;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![zapdos(id)],
            vec![
                PlayedCard::from_id(CardId::A1004VenusaurEx),
                PlayedCard::from_id(CardId::B3a045Glimmora).with_remaining_hp(50),
            ],
        );
        use_thunderclaw(&mut game, id);
        let choice = bench_target_choice(&game, 1);
        game.apply_action(&choice);

        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[1][1].is_none(), "seed {seed}");
        match state.points[0] {
            0 => saw_denied = true,
            1 => saw_scored = true,
            points => panic!("seed {seed}: unexpected point total {points}"),
        }
    }
    assert!(saw_denied && saw_scored);
}

#[test]
fn active_perish_body_coin_is_forecast_after_target_selection() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut saw_attacker_knocked_out = false;
    let mut saw_attacker_survive = false;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![zapdos(id), PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![
                PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(90),
                PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
            ],
        );
        use_thunderclaw(&mut game, id);
        let choice = bench_target_choice(&game, 1);
        game.apply_action(&choice);

        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[1][0].is_none(), "seed {seed}");
        assert_eq!(state.points[0], 1, "seed {seed}");
        if state.in_play_pokemon[0][0].is_none() {
            saw_attacker_knocked_out = true;
            assert_eq!(state.points[1], 2, "seed {seed}");
        } else {
            saw_attacker_survive = true;
            assert_eq!(state.points[1], 0, "seed {seed}");
        }
    }
    assert!(saw_attacker_knocked_out && saw_attacker_survive);
}

#[test]
fn genome_hacking_preserves_copied_thunderclaw_context_through_choice() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx),
            PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1a032MewEx, 1),
        is_stack: false,
    });
    let (_, copied_choices) = game.get_state_clone().generate_possible_actions();
    let copied = copied_choices
        .iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Thunderclaw")
        })
        .expect("Genome Hacking should offer Thunderclaw")
        .clone();
    assert!(copied.is_stack);
    game.apply_action(&copied);

    let choice = bench_target_choice(&game, 1);
    game.apply_action(&choice);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 30);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        120
    );
}

#[test]
fn target_choice_is_serializable_and_retained_in_the_choosers_observation() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![zapdos(id)],
        vec![
            PlayedCard::from_id(CardId::A1004VenusaurEx),
            PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
        ],
    );
    use_thunderclaw(&mut game, id);

    let observation = game.observation(0);
    let choices = &observation
        .visible_state()
        .move_generation_stack
        .last()
        .unwrap()
        .1;
    assert_eq!(choices.len(), 1);
    let action = Action {
        actor: 0,
        action: choices[0].clone(),
        is_stack: true,
    };
    let encoded = serde_json::to_string(&action).unwrap();
    let decoded: Action = serde_json::from_str(&encoded).unwrap();
    assert_eq!(decoded, action);
}

#[test]
fn queued_damage_uses_the_carried_attack_name_for_active_modifiers() {
    let id = ZAPDOS_PRINTINGS[0];
    let mut boosted = zapdos(id);
    boosted.add_effect(
        CardEffect::IncreasedDamageForAttack {
            attack_name: "Thunderclaw".to_string(),
            amount: 30,
        },
        1,
    );
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![boosted],
        vec![
            PlayedCard::from_id(CardId::A1004VenusaurEx),
            PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
        ],
    );

    use_thunderclaw(&mut game, id);
    let choice = bench_target_choice(&game, 1);
    game.apply_action(&choice);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        70,
        "the carried Thunderclaw name must apply the +30 named-attack bonus to the Active"
    );
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        120,
        "an Active-only named-attack bonus must not increase Bench damage"
    );
}

#[test]
fn a_successful_confusion_gate_is_not_flipped_again_when_the_target_commits() {
    let id = ZAPDOS_PRINTINGS[0];
    let staged = (0..40)
        .find_map(|seed| {
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                3,
                vec![zapdos(id).with_status_condition(StatusCondition::Confused)],
                vec![
                    PlayedCard::from_id(CardId::A1004VenusaurEx),
                    PlayedCard::from_id(CardId::A1056BlastoiseEx).with_remaining_hp(170),
                ],
            );
            use_thunderclaw(&mut game, id);
            (!game.get_state_clone().move_generation_stack.is_empty())
                .then(|| game.get_state_clone())
        })
        .expect("some initial confusion flip should allow Thunderclaw to stage its choice");
    let choice = {
        let (_, choices) = staged.generate_possible_actions();
        choices
            .into_iter()
            .find(|action| {
                matches!(
                    &action.action,
                    SimpleAction::ApplyQueuedAttackDamage { targets, .. }
                        if targets.contains(&(50, true, 1))
                )
            })
            .unwrap()
    };

    for seed in 0..24 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![zapdos(id)],
            vec![PlayedCard::from_id(CardId::A1004VenusaurEx)],
        );
        game.set_state(staged.clone());
        game.apply_action(&choice);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_remaining_hp(), 100, "seed {seed}");
        assert_eq!(
            state.in_play_pokemon[1][1]
                .as_ref()
                .unwrap()
                .get_remaining_hp(),
            120,
            "seed {seed}: target commit must not rerun confusion"
        );
    }
}
