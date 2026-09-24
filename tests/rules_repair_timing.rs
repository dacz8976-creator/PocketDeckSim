use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{PlayedCard, StatusCondition},
    move_generation::generate_possible_actions,
    state::GameOutcome,
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
use rand::{rngs::StdRng, SeedableRng};

fn p(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id)
}
fn game(actor: usize, a: Vec<PlayedCard>, b: Vec<PlayedCard>) -> Game<'static> {
    let mut game = get_initialized_game_with_board(777, actor, 3, a, b);
    let mut state = game.get_state_clone();
    state.points = [0, 0];
    game.set_state(state);
    game
}
fn act(game: &mut Game<'static>, actor: usize, action: SimpleAction) {
    game.apply_action(&Action {
        actor,
        action,
        is_stack: false,
    });
}
fn finish_forced(game: &mut Game<'static>) {
    for _ in 0..32 {
        let state = game.get_state_clone();
        if state.winner.is_some() {
            return;
        }
        let (_, actions) = generate_possible_actions(&state);
        if actions.is_empty() || !actions[0].is_stack {
            return;
        }
        game.apply_action(&actions[0]);
    }
    panic!("forced continuation failed to terminate");
}

#[test]
fn checkup_heals_before_knockout_in_both_seats() {
    for actor in 0..2 {
        let board = vec![
            p(CardId::A1001Bulbasaur)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            p(CardId::B3a033Garganacl),
        ];
        let mut game = game(actor, board.clone(), board);
        act(&mut game, actor, SimpleAction::EndTurn);
        let state = game.get_state_clone();
        assert_eq!(state.points, [0, 0]);
        assert_eq!(state.get_active(0).get_remaining_hp(), 10);
        assert_eq!(state.get_active(1).get_remaining_hp(), 10);
        assert_eq!(state.turn_count, 4);
    }
}

#[test]
fn checkup_healing_respects_lost_ability() {
    let mut salt = p(CardId::B3a033Garganacl);
    salt.add_effect(CardEffect::NoAbilities, 1);
    let mut game = game(
        0,
        vec![
            p(CardId::A1001Bulbasaur)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            salt,
        ],
        vec![p(CardId::A1211Snorlax)],
    );
    act(&mut game, 0, SimpleAction::EndTurn);
    assert_eq!(game.get_state_clone().points, [0, 1]);
}

#[test]
fn both_checkup_knockouts_score_before_winner_in_both_seats() {
    for actor in 0..2 {
        let board = vec![
            p(CardId::A1001Bulbasaur)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            p(CardId::A1001Bulbasaur),
        ];
        let mut game = game(actor, board.clone(), board);
        let mut state = game.get_state_clone();
        state.points = [2, 2];
        game.set_state(state);
        act(&mut game, actor, SimpleAction::EndTurn);
        let state = game.get_state_clone();
        assert_eq!(state.points, [3, 3]);
        assert_eq!(state.winner, Some(GameOutcome::Tie));
        assert!(state.in_play_pokemon[0][0].is_none());
        assert!(state.in_play_pokemon[1][0].is_none());
    }
}

#[test]
fn prickly_powder_disables_rough_skin_before_retaliation_but_not_tool() {
    for helmet in [false, true] {
        let mut defender = p(CardId::A1a056Druddigon);
        if helmet {
            defender = defender.with_tool(get_card_by_enum(CardId::A2148RockyHelmet));
        }
        let mut game = game(0, vec![p(CardId::B3013Budew)], vec![defender]);
        act(&mut game, 0, attack_action(CardId::B3013Budew, 0));
        assert_eq!(
            game.get_state_clone().get_active(0).get_remaining_hp(),
            if helmet { 10 } else { 30 }
        );
    }
}

#[test]
fn rough_skin_respects_muk_and_iron_jugulis_printing_works() {
    for defender in [CardId::A1a056Druddigon, CardId::B3a046IronJugulis] {
        for suppressed in [false, true] {
            let mut board = vec![p(defender)];
            if suppressed {
                board.push(p(CardId::B2097AlolanMuk));
            }
            let mut game = game(0, vec![p(CardId::A1211Snorlax)], board);
            act(
                &mut game,
                0,
                SimpleAction::ApplyDamage {
                    attacking_ref: (0, 0),
                    targets: vec![(10, 1, 0)],
                    is_from_active_attack: true,
                },
            );
            assert_eq!(
                game.get_state_clone().get_active(0).get_remaining_hp(),
                if suppressed { 150 } else { 130 }
            );
        }
    }
}

#[test]
fn fourth_dragalge_printing_poison_point_respects_ability_loss() {
    for suppressed in [false, true] {
        let mut defender = p(CardId::B3231DragalgeEx);
        if suppressed {
            defender.add_effect(CardEffect::NoAbilities, 1);
        }
        let mut game = game(0, vec![p(CardId::A1211Snorlax)], vec![defender]);
        act(
            &mut game,
            0,
            SimpleAction::ApplyDamage {
                attacking_ref: (0, 0),
                targets: vec![(10, 1, 0)],
                is_from_active_attack: true,
            },
        );
        assert_eq!(
            game.get_state_clone().get_active(0).is_poisoned(),
            !suppressed
        );
    }
}

fn assert_denial_branches(game: &Game<'static>, receiver: usize) {
    let state = game.get_state_clone();
    let (_, choices) = generate_possible_actions(&state);
    assert_eq!(choices.len(), 1);
    assert!(matches!(
        choices[0].action,
        SimpleAction::ResolveKnockoutPoints { .. }
    ));
    let outcomes = try_forecast_action(&state, &choices[0]).unwrap();
    let (probabilities, mutations) = outcomes.into_branches();
    assert_eq!(probabilities, vec![0.5, 0.5]);
    let scores: Vec<_> = mutations
        .into_iter()
        .map(|mutation| {
            let mut next = state.clone();
            mutation(&mut StdRng::seed_from_u64(1), &mut next, &choices[0]);
            assert!(next.in_play_pokemon[receiver][0].is_none());
            next.points[1 - receiver]
        })
        .collect();
    assert_eq!(scores, vec![1, 0]);
}

#[test]
fn glimmora_poison_denial_is_exact_chance_before_next_turn() {
    let mut game = game(
        0,
        vec![
            p(CardId::B3a045Glimmora)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            p(CardId::B3a044Glimmet),
        ],
        vec![p(CardId::A1211Snorlax)],
    );
    act(&mut game, 0, SimpleAction::EndTurn);
    assert_eq!(game.get_state_clone().turn_count, 3);
    assert_denial_branches(&game, 0);
    finish_forced(&mut game);
    assert_eq!(game.get_state_clone().turn_count, 4);
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 60);
}

#[test]
fn dusknoir_ability_damage_denial_keeps_turn_owner() {
    let mut game = game(
        0,
        vec![p(CardId::A1211Snorlax)],
        vec![
            p(CardId::B1105Dusknoir).with_remaining_hp(10),
            p(CardId::A1001Bulbasaur),
        ],
    );
    act(
        &mut game,
        0,
        SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(10, 1, 0)],
            is_from_active_attack: false,
        },
    );
    assert_denial_branches(&game, 1);
    finish_forced(&mut game);
    assert_eq!(game.get_state_clone().current_player, 0);
    assert_eq!(game.get_state_clone().turn_count, 3);
}

#[test]
fn suppressed_point_denial_does_not_flip() {
    let mut glimmora = p(CardId::B3a045Glimmora)
        .with_remaining_hp(10)
        .with_status_condition(StatusCondition::Poisoned);
    glimmora.add_effect(CardEffect::NoAbilities, 1);
    let mut game = game(
        0,
        vec![glimmora, p(CardId::B3a044Glimmet)],
        vec![p(CardId::A1211Snorlax)],
    );
    act(&mut game, 0, SimpleAction::EndTurn);
    assert_eq!(game.get_state_clone().points, [0, 1]);
    assert_eq!(game.get_state_clone().turn_count, 4);
}

#[test]
fn double_attack_knockout_promotes_attacker_first_in_both_seats() {
    for actor in 0..2 {
        let attacker = vec![
            p(CardId::A1001Bulbasaur).with_remaining_hp(10),
            p(CardId::A1001Bulbasaur),
            p(CardId::A1211Snorlax),
        ];
        let defender = vec![
            p(CardId::A1a056Druddigon).with_remaining_hp(10),
            p(CardId::A1001Bulbasaur),
            p(CardId::A1211Snorlax),
        ];
        let (a, b) = if actor == 0 {
            (attacker, defender)
        } else {
            (defender, attacker)
        };
        let mut game = game(actor, a, b);
        act(
            &mut game,
            actor,
            SimpleAction::ApplyDamage {
                attacking_ref: (actor, 0),
                targets: vec![(10, 1 - actor, 0)],
                is_from_active_attack: true,
            },
        );
        let state = game.get_state_clone();
        assert_eq!(state.points, [1, 1]);
        let (chooser, actions) = generate_possible_actions(&state);
        assert_eq!(chooser, actor);
        assert!(actions
            .iter()
            .all(|a| matches!(a.action, SimpleAction::Promote { .. })));
    }
}

#[test]
fn caterpie_evolves_and_cures_poison_before_checkup() {
    let mut game = game(
        0,
        vec![p(CardId::A1211Snorlax)],
        vec![p(CardId::B3b001Caterpie)
            .with_remaining_hp(10)
            .with_status_condition(StatusCondition::Poisoned)],
    );
    let mut state = game.get_state_clone();
    state.decks[1].cards = vec![get_card_by_enum(CardId::B3b002Metapod)];
    game.set_state(state);
    act(&mut game, 0, SimpleAction::EndTurn);
    finish_forced(&mut game);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Metapod");
    assert!(!state.get_active(1).is_poisoned());
    assert_eq!(state.points, [0, 0]);
    assert_eq!(state.turn_count, 4);
}

#[test]
fn point_denial_after_retaliation_preserves_both_promotions() {
    for actor in 0..2 {
        let attacker = vec![
            p(CardId::B1105Dusknoir).with_remaining_hp(10),
            p(CardId::A1001Bulbasaur),
            p(CardId::A1211Snorlax),
        ];
        let defender = vec![
            p(CardId::A3054Pyukumuku).with_remaining_hp(10),
            p(CardId::A1001Bulbasaur),
            p(CardId::A1211Snorlax),
        ];
        let (a, b) = if actor == 0 {
            (attacker, defender)
        } else {
            (defender, attacker)
        };
        let mut game = game(actor, a, b);
        act(
            &mut game,
            actor,
            SimpleAction::ApplyDamage {
                attacking_ref: (actor, 0),
                targets: vec![(10, 1 - actor, 0)],
                is_from_active_attack: true,
            },
        );
        let state = game.get_state_clone();
        let (_, choices) = generate_possible_actions(&state);
        assert!(matches!(
            choices[0].action,
            SimpleAction::ResolveKnockoutPoints { .. }
        ));
        game.apply_action(&choices[0]);
        let state = game.get_state_clone();
        let (chooser, choices) = generate_possible_actions(&state);
        assert_eq!(chooser, actor);
        assert!(choices
            .iter()
            .all(|a| matches!(a.action, SimpleAction::Promote { .. })));
        finish_forced(&mut game);
        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[0][0].is_some());
        assert!(state.in_play_pokemon[1][0].is_some());
        assert_eq!(state.points[actor], 1);
        assert!(state.points[1 - actor] <= 1);
    }
}
