use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::PlayedCard,
    move_generation::generate_possible_actions,
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

fn apply(game: &mut Game<'static>, actor: usize, action: SimpleAction) {
    game.apply_action(&Action {
        actor,
        action,
        is_stack: false,
    });
}

fn apply_top_matching(game: &mut Game<'static>, predicate: impl Fn(&SimpleAction) -> bool) {
    let state = game.get_state_clone();
    let (_, actions) = generate_possible_actions(&state);
    let action = actions
        .into_iter()
        .find(|action| predicate(&action.action))
        .expect("expected forced attack continuation");
    game.apply_action(&action);
}

#[test]
fn knock_back_resolves_before_original_defender_retaliates() {
    let mut game = get_initialized_game_with_board(
        901,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1163Grapploct)],
        vec![
            PlayedCard::from_id(CardId::A1a056Druddigon),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    let attacker_hp = game.get_state_clone().get_active(0).get_remaining_hp();

    apply(&mut game, 0, attack_action(CardId::A1163Grapploct, 0));
    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        attacker_hp,
        "Rough Skin must wait for the attack's forced switch effect"
    );

    apply_top_matching(&mut game, |action| {
        matches!(
            action,
            SimpleAction::Activate {
                player: 1,
                in_play_idx: 1
            }
        )
    });
    assert_eq!(game.get_state_clone().get_active(1).get_name(), "Bulbasaur");

    apply_top_matching(&mut game, |action| {
        matches!(action, SimpleAction::ResolveAttackRetaliation { .. })
    });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), attacker_hp - 20);
    assert_eq!(
        state.in_play_pokemon[1][1].as_ref().unwrap().get_name(),
        "Druddigon",
        "the damaged defender, not its Active replacement, owns the reaction"
    );
}

#[test]
fn self_switch_counterdamage_follows_original_attacker_to_bench() {
    let mut game = get_initialized_game_with_board(
        902,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A3068TapuKoko),
            PlayedCard::from_id(CardId::B2052Plusle),
        ],
        vec![PlayedCard::from_id(CardId::A1a056Druddigon)],
    );
    let tapu_hp = game.get_state_clone().get_active(0).get_remaining_hp();
    let plusle_hp = game.get_state_clone().in_play_pokemon[0][1]
        .as_ref()
        .unwrap()
        .get_remaining_hp();

    apply(&mut game, 0, attack_action(CardId::A3068TapuKoko, 0));
    apply_top_matching(&mut game, |action| {
        matches!(
            action,
            SimpleAction::Activate {
                player: 0,
                in_play_idx: 1
            }
        )
    });
    apply_top_matching(&mut game, |action| {
        matches!(action, SimpleAction::ResolveAttackRetaliation { .. })
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Plusle");
    assert_eq!(state.get_active(0).get_remaining_hp(), plusle_hp);
    let tapu = state.in_play_pokemon[0][1].as_ref().unwrap();
    assert_eq!(tapu.get_name(), "Tapu Koko");
    assert_eq!(tapu.get_remaining_hp(), tapu_hp - 20);
}

#[test]
fn prickly_powder_suppresses_perish_body_before_its_heads_recheck() {
    for seed in 0..16 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::B3013Budew),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
            vec![
                PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(10),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        apply(&mut game, 0, attack_action(CardId::B3013Budew, 0));
        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[1][0].is_none(), "seed {seed}");
        assert!(state.in_play_pokemon[0][0].is_some(), "seed {seed}");
    }
}

#[test]
fn lethal_knock_back_does_not_trigger_active_only_perish_body_from_bench() {
    let mut attacker_knocked_out = 0;
    let mut attacker_survived = 0;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::A1163Grapploct),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
            vec![
                PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(70),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        apply(&mut game, 0, attack_action(CardId::A1163Grapploct, 0));
        apply_top_matching(&mut game, |action| {
            matches!(
                action,
                SimpleAction::Activate {
                    player: 1,
                    in_play_idx: 1
                }
            )
        });
        apply_top_matching(&mut game, |action| {
            matches!(action, SimpleAction::ResolveAttackRetaliation { .. })
        });

        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_name(), "Charmander", "seed {seed}");
        assert!(
            state.in_play_pokemon[1][1].is_none(),
            "seed {seed}: the 0-HP Cursola moved by Knock Back must still be removed"
        );
        if state.in_play_pokemon[0][0].is_none() {
            attacker_knocked_out += 1;
        } else {
            attacker_survived += 1;
        }
    }

    assert_eq!(
        attacker_knocked_out, 0,
        "Perish Body requires the source to be Active at knockout"
    );
    assert_eq!(attacker_survived, 40);
}

#[test]
fn switched_bench_point_denial_uses_forecast_coin_once() {
    let mut point_awarded = 0;
    let mut point_denied = 0;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A1163Grapploct)],
            vec![
                PlayedCard::from_id(CardId::B3a045Glimmora).with_remaining_hp(70),
                PlayedCard::from_id(CardId::B3a044Glimmet),
            ],
        );
        apply(&mut game, 0, attack_action(CardId::A1163Grapploct, 0));
        apply_top_matching(&mut game, |action| {
            matches!(
                action,
                SimpleAction::Activate {
                    player: 1,
                    in_play_idx: 1
                }
            )
        });
        apply_top_matching(&mut game, |action| {
            matches!(action, SimpleAction::ResolveAttackRetaliation { .. })
        });

        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_name(), "Glimmet", "seed {seed}");
        assert!(state.in_play_pokemon[1][1].is_none(), "seed {seed}");
        assert!(
            state
                .move_generation_stack
                .iter()
                .all(|(_, choices)| choices
                    .iter()
                    .all(|action| !matches!(action, SimpleAction::ResolveKnockoutPoints { .. }))),
            "seed {seed}: forecast point-denial coin must not be offered a second time"
        );
        match state.points[0] {
            0 => point_denied += 1,
            1 => point_awarded += 1,
            points => panic!("seed {seed}: unexpected score {points}"),
        }
    }

    assert!(point_awarded > 0);
    assert!(point_denied > 0);
}
