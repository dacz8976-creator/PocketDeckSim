use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Malamar (B3 112 / 175) "Evolution Jammer": "During your opponent's next turn, they can't play
/// any Pokémon from their hand to evolve their Pokémon."
fn game_with_evolvable_opponent() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3112Malamar)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    )
}

/// Hands the opponent an Ivysaur (and only that), then reports whether evolving is offered.
fn opponent_can_evolve(game: &mut Game<'static>) -> bool {
    let mut state = game.get_state_clone();
    state.hands[1] = vec![get_card_by_enum(CardId::A1002Ivysaur)];
    game.set_state(state);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "it should be the opponent's turn");
    choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Evolve { .. }))
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

#[test]
fn test_malamar_evolution_jammer_blocks_evolving_next_turn() {
    let mut game = game_with_evolvable_opponent();

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3112Malamar, 0),
        is_stack: false,
    });
    end_turn(&mut game, 0);

    assert!(
        !opponent_can_evolve(&mut game),
        "Evolution Jammer should remove every Evolve action from the opponent's next turn"
    );
}

/// Negative: without Evolution Jammer the very same board offers the evolution.
#[test]
fn test_opponent_can_evolve_without_evolution_jammer() {
    let mut game = game_with_evolvable_opponent();

    end_turn(&mut game, 0);

    assert!(
        opponent_can_evolve(&mut game),
        "with no lock in play the opponent should be able to evolve Bulbasaur into Ivysaur"
    );
}

/// The lock only covers the opponent's *next* turn — it is gone by the turn after that.
#[test]
fn test_malamar_evolution_jammer_expires_after_one_turn() {
    let mut game = game_with_evolvable_opponent();

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3112Malamar, 0),
        is_stack: false,
    });
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    end_turn(&mut game, 0);

    assert!(
        opponent_can_evolve(&mut game),
        "the evolution lock should have expired after the opponent's next turn"
    );
}
