use std::panic::{catch_unwind, AssertUnwindSafe};

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_test_game_with_board},
    State,
};
use serde::Deserialize;

#[derive(Deserialize)]
struct ReplayDecisionFixture {
    state: State,
    playable_actions: Vec<Action>,
    chosen_action: Action,
}

fn actions_for(active: PlayedCard) -> (deckgym::Game<'static>, Vec<Action>) {
    let game = get_test_game_with_board(
        vec![active, PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    (game, actions)
}

fn has_attack(actions: &[Action]) -> bool {
    actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Attack(_)))
}

fn has_retreat(actions: &[Action]) -> bool {
    actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::Retreat(_)))
}

#[test]
fn asleep_and_paralyzed_remove_attack_and_paid_or_free_retreat() {
    let cases = [
        (
            PlayedCard::from_id(CardId::B3024CastformSunnyForm)
                .with_energy(vec![EnergyType::Fire, EnergyType::Colorless])
                .with_status_condition(StatusCondition::Asleep),
            "asleep Castform replay regression",
        ),
        (
            PlayedCard::from_id(CardId::B1044Heatmor)
                .with_energy(vec![EnergyType::Fire, EnergyType::Colorless])
                .with_status_condition(StatusCondition::Paralyzed),
            "paralyzed Heatmor paid-retreat regression",
        ),
        (
            PlayedCard::from_id(CardId::A4a059Igglybuff)
                .with_status_condition(StatusCondition::Asleep),
            "asleep Igglybuff zero-retreat-cost regression",
        ),
    ];

    for (active, label) in cases {
        let (_, actions) = actions_for(active);
        assert!(!has_attack(&actions), "{label} still offered Attack");
        assert!(!has_retreat(&actions), "{label} still offered Retreat");
    }
}

#[test]
fn other_special_conditions_keep_normal_attack_and_retreat_controls() {
    for condition in [
        StatusCondition::Confused,
        StatusCondition::Poisoned,
        StatusCondition::Burned,
    ] {
        let active = PlayedCard::from_id(CardId::B3024CastformSunnyForm)
            .with_energy(vec![EnergyType::Fire, EnergyType::Colorless])
            .with_status_condition(condition);
        let (_, actions) = actions_for(active);
        assert!(has_attack(&actions), "{condition:?} incorrectly removed Attack");
        assert!(
            has_retreat(&actions),
            "{condition:?} incorrectly removed Retreat"
        );
    }
}

#[test]
fn direct_normal_actions_are_rejected_without_state_mutation() {
    let (mut attack_game, _) = actions_for(
        PlayedCard::from_id(CardId::B3024CastformSunnyForm)
            .with_energy(vec![EnergyType::Fire])
            .with_status_condition(StatusCondition::Asleep),
    );
    let attack_before = attack_game.get_state_clone();
    let attack_result = catch_unwind(AssertUnwindSafe(|| {
        attack_game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B3024CastformSunnyForm, 0),
            is_stack: false,
        });
    }));
    assert!(attack_result.is_err(), "direct asleep Attack was accepted");
    assert_eq!(attack_game.get_state_clone(), attack_before);

    let (mut retreat_game, _) = actions_for(
        PlayedCard::from_id(CardId::B1044Heatmor)
            .with_energy(vec![EnergyType::Colorless])
            .with_status_condition(StatusCondition::Paralyzed),
    );
    let before = retreat_game.get_state_clone();
    let retreat_result = catch_unwind(AssertUnwindSafe(|| {
        retreat_game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Retreat(1),
            is_stack: false,
        });
    }));
    assert!(retreat_result.is_err(), "direct paralyzed Retreat was accepted");
    assert_eq!(retreat_game.get_state_clone(), before);
}

#[test]
fn saved_castform_and_heatmor_replay_choices_are_no_longer_offered() {
    let fixtures = [
        include_str!("fixtures/status_castform_asleep_ply_0059.json"),
        include_str!("fixtures/status_heatmor_asleep_ply_0037.json"),
    ];

    for fixture_json in fixtures {
        let fixture: ReplayDecisionFixture = serde_json::from_str(fixture_json).unwrap();
        assert!(
            fixture.playable_actions.contains(&fixture.chosen_action),
            "the preserved eval18 trace must record its chosen action in the old menu"
        );
        assert!(matches!(
            fixture.chosen_action.action,
            SimpleAction::Attack(_) | SimpleAction::Retreat(_)
        ));
        assert!(fixture.state.get_active(fixture.chosen_action.actor).is_asleep());

        let (_, corrected_actions) = fixture.state.generate_possible_actions();
        assert!(
            !corrected_actions.contains(&fixture.chosen_action),
            "the forbidden saved replay choice remained in the corrected menu"
        );
    }
}

#[test]
fn status_keeps_ability_cure_evolution_and_effect_switch_escapes_legal() {
    let (mut ability_game, _) = actions_for(
        PlayedCard::from_id(CardId::A1053Squirtle)
            .with_status_condition(StatusCondition::Asleep),
    );
    let mut ability_state = ability_game.get_state_clone();
    ability_state.in_play_pokemon[0][1] =
        Some(PlayedCard::from_id(CardId::B2a036Baxcalibur));
    ability_game.set_state(ability_state);
    let (_, ability_actions) = ability_game.get_state_clone().generate_possible_actions();
    let ability = ability_actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 1 }))
        .expect("Ice Maker should remain usable while the Active is Asleep");
    ability_game.apply_action(&ability);
    assert_eq!(
        ability_game
            .get_state_clone()
            .get_active(0)
            .attached_energy,
        vec![EnergyType::Water]
    );
    let (mut cure_game, _) = actions_for(
        PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_status_condition(StatusCondition::Paralyzed),
    );
    let mut cure_state = cure_game.get_state_clone();
    cure_state.hands[0] = vec![get_card_by_enum(CardId::A2b070PokemonCenterLady)];
    cure_game.set_state(cure_state);
    let (_, offered) = cure_game.get_state_clone().generate_possible_actions();
    let play = offered
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::Play { trainer_card }
                if trainer_card.id == "A2b 070")
        })
        .expect("Pokemon Center Lady should remain playable");
    cure_game.apply_action(&play);
    let (_, offered) = cure_game.get_state_clone().generate_possible_actions();
    let heal = offered
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::Heal { in_play_idx: 0, .. }))
        .expect("Pokemon Center Lady should offer the conditioned Active");
    cure_game.apply_action(&heal);
    assert!(!cure_game.get_state_clone().get_active(0).is_paralyzed());

    let (mut evolve_game, _) = actions_for(
        PlayedCard::from_id(CardId::B1184Eevee)
            .with_status_condition(StatusCondition::Asleep),
    );
    let mut evolve_state = evolve_game.get_state_clone();
    evolve_state.hands[0].push(get_card_by_enum(CardId::B3a020Espeon));
    evolve_game.set_state(evolve_state);
    let (_, offered) = evolve_game.get_state_clone().generate_possible_actions();
    let evolve = offered
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::Evolve { in_play_idx: 0, .. }))
        .expect("an Asleep Active should still be able to evolve");
    evolve_game.apply_action(&evolve);
    assert_eq!(evolve_game.get_state_clone().get_active(0).get_name(), "Espeon");
    assert!(!evolve_game.get_state_clone().get_active(0).is_asleep());

    let (mut switch_game, _) = actions_for(
        PlayedCard::from_id(CardId::B1044Heatmor)
            .with_status_condition(StatusCondition::Paralyzed),
    );
    switch_game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Activate {
            player: 0,
            in_play_idx: 1,
        },
        is_stack: true,
    });
    let switched = switch_game.get_state_clone();
    assert_eq!(switched.get_active(0).get_name(), "Bulbasaur");
    assert!(!switched.in_play_pokemon[0][1]
        .as_ref()
        .expect("Heatmor should be on the Bench")
        .is_paralyzed());
}
