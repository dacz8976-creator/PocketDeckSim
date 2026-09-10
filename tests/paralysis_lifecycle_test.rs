use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
    Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

fn action(actor: usize, action: SimpleAction) -> Action {
    Action {
        actor,
        action,
        is_stack: false,
    }
}

fn galvantula() -> PlayedCard {
    PlayedCard::from_id(CardId::A3b027Galvantula)
        .with_energy(vec![EnergyType::Lightning, EnergyType::Lightning])
}

fn durable_target() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
        EnergyType::Water,
        EnergyType::Water,
        EnergyType::Psychic,
    ])
}

fn game_with_target(attacker: usize, target: PlayedCard, target_bench: PlayedCard) -> Game<'static> {
    let attacker_board = vec![galvantula()];
    let target_board = vec![target, target_bench];
    let (player_0, player_1) = if attacker == 0 {
        (attacker_board, target_board)
    } else {
        (target_board, attacker_board)
    };
    get_initialized_game_with_board(8_091 + attacker as u64, attacker, 3, player_0, player_1)
}

fn attack_and_enter_restricted_turn(attacker: usize, target: PlayedCard) -> Game<'static> {
    let mut game = game_with_target(
        attacker,
        target,
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    game.apply_action(&action(
        attacker,
        attack_action(CardId::A3b027Galvantula, 0),
    ));
    assert!(game
        .get_state_clone()
        .get_active(1 - attacker)
        .is_paralyzed());
    end_turn(&mut game, attacker);
    game
}

fn end_turn(game: &mut Game<'_>, actor: usize) {
    game.apply_action(&action(actor, SimpleAction::EndTurn));
    game.play_until_stable();
}

fn has_attack(actions: &[Action]) -> bool {
    actions
        .iter()
        .any(|candidate| matches!(candidate.action, SimpleAction::Attack(_)))
}

fn has_retreat(actions: &[Action]) -> bool {
    actions
        .iter()
        .any(|candidate| matches!(candidate.action, SimpleAction::Retreat(_)))
}

fn forecast_states(state: &State, action: &Action) -> (Vec<f64>, Vec<State>) {
    let (probabilities, mutations) = try_forecast_action(state, action)
        .expect("checkup forecast should be fully priced")
        .into_branches();
    let states = mutations
        .into_iter()
        .enumerate()
        .map(|(index, mutation)| {
            let mut next = state.clone();
            mutation(
                &mut StdRng::seed_from_u64(44_000 + index as u64),
                &mut next,
                action,
            );
            next
        })
        .collect();
    (probabilities, states)
}

#[test]
fn opponent_paralysis_restricts_one_full_turn_then_recovers_for_both_seats() {
    for attacker in [0, 1] {
        let target = 1 - attacker;
        let mut healthy = game_with_target(
            attacker,
            durable_target(),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        )
        .get_state_clone();
        healthy.current_player = target;
        healthy.energy_zone[target].current = Some(EnergyType::Water);
        let (offered_actor, actions) = healthy.generate_possible_actions();
        assert_eq!(offered_actor, target);
        assert!(has_attack(&actions), "healthy seat {target} lacked Attack");
        assert!(has_retreat(&actions), "healthy seat {target} lacked Retreat");
        assert!(actions.iter().any(|candidate| matches!(
            candidate.action,
            SimpleAction::Attach {
                is_turn_energy: true,
                ..
            }
        )));

        let mut game = attack_and_enter_restricted_turn(attacker, durable_target());
        let mut state = game.get_state_clone();
        state.energy_zone[target].current = Some(EnergyType::Water);
        game.set_state(state.clone());

        assert_eq!(state.current_player, target);
        assert!(state.get_active(target).is_paralyzed());
        let (offered_actor, actions) = state.generate_possible_actions();
        assert_eq!(offered_actor, target);
        assert!(!has_attack(&actions), "seat {target} was offered Attack");
        assert!(!has_retreat(&actions), "seat {target} was offered Retreat");
        assert!(
            actions.iter().any(|candidate| matches!(
                candidate.action,
                SimpleAction::Attach {
                    is_turn_energy: true,
                    ..
                }
            )),
            "seat {target} was not offered its normal turn Energy attachment"
        );

        end_turn(&mut game, target);
        assert!(
            !game.get_state_clone().get_active(target).is_paralyzed(),
            "seat {target} did not recover at the end of its own turn"
        );

        end_turn(&mut game, attacker);
        let restored = game.get_state_clone();
        assert_eq!(restored.current_player, target);
        let (offered_actor, actions) = restored.generate_possible_actions();
        assert_eq!(offered_actor, target);
        assert!(has_attack(&actions), "seat {target} did not regain Attack");
        assert!(has_retreat(&actions), "seat {target} did not regain Retreat");
    }
}

#[test]
fn paralysis_recovery_is_deterministic_at_each_boundary() {
    let attacker = 0;
    let target = 1;
    let mut game = game_with_target(
        attacker,
        durable_target(),
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    game.apply_action(&action(
        attacker,
        attack_action(CardId::A3b027Galvantula, 0),
    ));

    let attacker_end = action(attacker, SimpleAction::EndTurn);
    let (probabilities, next) = forecast_states(&game.get_state_clone(), &attacker_end);
    assert_eq!(probabilities, vec![1.0], "Paralysis must not add a coin");
    assert!(next[0].get_active(target).is_paralyzed());

    end_turn(&mut game, attacker);
    let target_end = action(target, SimpleAction::EndTurn);
    let (probabilities, next) = forecast_states(&game.get_state_clone(), &target_end);
    assert_eq!(probabilities, vec![1.0], "recovery must not add a coin");
    assert!(!next[0].get_active(target).is_paralyzed());
}

#[test]
fn refreshing_paralysis_before_the_target_turn_keeps_the_same_recovery_boundary() {
    let attacker = 0;
    let target = 1;
    let mut game = game_with_target(
        attacker,
        durable_target(),
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    );
    game.apply_action(&action(
        attacker,
        attack_action(CardId::A3b027Galvantula, 0),
    ));
    let mut refreshed = game.get_state_clone();
    refreshed.apply_status_condition(target, 0, StatusCondition::Paralyzed);
    game.set_state(refreshed);

    end_turn(&mut game, attacker);
    assert!(game.get_state_clone().get_active(target).is_paralyzed());
    end_turn(&mut game, target);
    assert!(!game.get_state_clone().get_active(target).is_paralyzed());
}

#[test]
fn sleep_checkup_still_flips_for_the_ending_or_nonending_side() {
    for sleeper in [0, 1] {
        let mut state = get_initialized_game_with_board(
            9_100 + sleeper as u64,
            0,
            3,
            vec![durable_target()],
            vec![durable_target()],
        )
        .get_state_clone();
        state.apply_status_condition(sleeper, 0, StatusCondition::Asleep);
        let end = action(0, SimpleAction::EndTurn);
        let (probabilities, next) = forecast_states(&state, &end);

        assert_eq!(probabilities, vec![0.5, 0.5]);
        let mut asleep_results: Vec<bool> = next
            .iter()
            .map(|candidate| candidate.get_active(sleeper).is_asleep())
            .collect();
        asleep_results.sort_unstable();
        assert_eq!(asleep_results, vec![false, true]);
    }
}

#[test]
fn applied_paralysis_keeps_ability_and_cure_escapes_legal() {
    let target = 1;
    let mut cure_game = attack_and_enter_restricted_turn(0, durable_target());
    let mut cure_state = cure_game.get_state_clone();
    cure_state.hands[target] = vec![get_card_by_enum(CardId::A2b070PokemonCenterLady)];
    cure_game.set_state(cure_state);
    let play = cure_game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|candidate| {
            matches!(&candidate.action, SimpleAction::Play { trainer_card }
                if trainer_card.id == "A2b 070")
        })
        .expect("Pokemon Center Lady should remain playable while Paralyzed");
    cure_game.apply_action(&play);
    let heal = cure_game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|candidate| matches!(candidate.action, SimpleAction::Heal { in_play_idx: 0, .. }))
        .expect("Pokemon Center Lady should offer the damaged Paralyzed Active");
    cure_game.apply_action(&heal);
    assert!(!cure_game.get_state_clone().get_active(target).is_paralyzed());

    let blastoise = PlayedCard::from_id(CardId::A1056BlastoiseEx)
        .with_energy(vec![EnergyType::Water, EnergyType::Water]);
    let mut ability_game = game_with_target(
        0,
        blastoise,
        PlayedCard::from_id(CardId::B2a036Baxcalibur),
    );
    ability_game.apply_action(&action(0, attack_action(CardId::A3b027Galvantula, 0)));
    end_turn(&mut ability_game, 0);
    let mut ability_state = ability_game.get_state_clone();
    ability_state.energy_zone[target].current = Some(EnergyType::Water);
    ability_game.set_state(ability_state);
    assert!(ability_game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|candidate| matches!(candidate.action, SimpleAction::UseAbility { in_play_idx: 1 })));
}

#[test]
fn evolution_and_effect_switch_clear_applied_paralysis_without_reappearing() {
    let target = 1;
    let ivysaur = PlayedCard::from_id(CardId::A1002Ivysaur).with_energy(vec![
        EnergyType::Grass,
        EnergyType::Colorless,
        EnergyType::Colorless,
    ]);
    let mut evolve_game = attack_and_enter_restricted_turn(0, ivysaur);
    let mut evolve_state = evolve_game.get_state_clone();
    evolve_state.hands[target].push(get_card_by_enum(CardId::A1003Venusaur));
    evolve_game.set_state(evolve_state);
    let evolve = evolve_game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|candidate| matches!(candidate.action, SimpleAction::Evolve { in_play_idx: 0, .. }))
        .expect("the Paralyzed Active should still be able to evolve");
    evolve_game.apply_action(&evolve);
    assert!(!evolve_game.get_state_clone().get_active(target).is_paralyzed());
    end_turn(&mut evolve_game, target);
    assert!(!evolve_game.get_state_clone().get_active(target).is_paralyzed());

    let mut switch_game = attack_and_enter_restricted_turn(0, durable_target());
    switch_game.apply_action(&Action {
        actor: target,
        action: SimpleAction::Activate {
            player: target,
            in_play_idx: 1,
        },
        is_stack: true,
    });
    let switched = switch_game.get_state_clone();
    assert!(!switched.get_active(target).is_paralyzed());
    assert!(!switched.in_play_pokemon[target][1]
        .as_ref()
        .expect("the former Active should be on the Bench")
        .is_paralyzed());
    end_turn(&mut switch_game, target);
    assert!(!switch_game.get_state_clone().get_active(target).is_paralyzed());
}
