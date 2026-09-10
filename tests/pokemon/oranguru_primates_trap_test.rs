use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Oranguru (A3 140) "Primate's Trap": "During your opponent's next turn, attacks used by the
/// Defending Pokémon cost 1 [C] more, and its Retreat Cost is 1 [C] more."
fn game_with_oranguru() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A3140Oranguru)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![
            // 300 HP so it survives Primate's Trap; Vine Whip normally costs [G][C].
            PlayedCard::new(
                get_card_by_enum(CardId::A1001Bulbasaur),
                0,
                300,
                vec![EnergyType::Grass, EnergyType::Colorless],
                false,
                vec![],
            ),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    )
}

fn primates_trap(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3140Oranguru, 0),
        is_stack: false,
    });
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn opponent_can_attack(game: &Game<'static>) -> bool {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "it should be the opponent's turn");
    choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Attack(_)))
}

#[test]
fn test_oranguru_primates_trap_makes_the_defenders_attack_cost_one_more() {
    let mut game = game_with_oranguru();

    primates_trap(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        260,
        "Primate's Trap does its printed 40 damage"
    );
    end_turn(&mut game, 0);

    assert!(
        !opponent_can_attack(&game),
        "Vine Whip should now cost 3 Energy while Bulbasaur only has 2"
    );
}

#[test]
fn test_oranguru_primates_trap_makes_the_defender_pay_one_more_to_retreat() {
    let mut game = game_with_oranguru();

    primates_trap(&mut game);
    end_turn(&mut game, 0);

    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Charmander");
    let benched_bulbasaur = state.in_play_pokemon[1][1]
        .as_ref()
        .expect("Bulbasaur should be on the Bench after retreating");
    assert_eq!(
        benched_bulbasaur.attached_energy.len(),
        0,
        "the Retreat Cost should have been 2, consuming both attached Energy"
    );
}

/// Negative: the same board without Primate's Trap lets the opponent attack, and retreating costs
/// only the printed 1 [C].
#[test]
fn test_defender_is_unhindered_without_primates_trap() {
    let mut game = game_with_oranguru();
    end_turn(&mut game, 0);

    assert!(
        opponent_can_attack(&game),
        "Bulbasaur's 2 Energy should cover the printed [G][C] cost of Vine Whip"
    );

    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let benched_bulbasaur = state.in_play_pokemon[1][1]
        .as_ref()
        .expect("Bulbasaur should be on the Bench after retreating");
    assert_eq!(
        benched_bulbasaur.attached_energy.len(),
        1,
        "the printed Retreat Cost of 1 should leave one Energy attached"
    );
}
