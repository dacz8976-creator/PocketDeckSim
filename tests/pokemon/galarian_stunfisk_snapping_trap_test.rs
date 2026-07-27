use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Galarian Stunfisk (B2 117) "Snapping Trap": "During your opponent's next turn, if this Pokémon
/// is in the Active Spot when your opponent's Active Pokémon retreats, this attack does 40 damage
/// to the new Active Pokémon."
fn game_with_stunfisk() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B2117GalarianStunfisk)
            .with_energy(vec![EnergyType::Metal, EnergyType::Colorless])],
        vec![
            // 300 HP so it survives Snapping Trap and can keep retreating.
            PlayedCard::new(
                get_card_by_enum(CardId::A1001Bulbasaur),
                0,
                300,
                vec![EnergyType::Grass, EnergyType::Grass],
                false,
                vec![],
            ),
            // 60 HP, weak to [W]; Stunfisk is [M], so the trap damage is a flat 40.
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    )
}

fn snapping_trap(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2117GalarianStunfisk, 0),
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

fn opponent_retreats(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });
    game.play_until_stable();
}

#[test]
fn test_snapping_trap_damages_the_pokemon_promoted_by_a_retreat() {
    let mut game = game_with_stunfisk();

    snapping_trap(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        260,
        "Snapping Trap does its printed 40 damage"
    );

    end_turn(&mut game, 0);
    opponent_retreats(&mut game);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Charmander");
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        20,
        "the newly promoted Charmander should take the trap's 40 damage (60 - 40)"
    );
}

/// Negative: the trap covers exactly the opponent's next turn.
#[test]
fn test_snapping_trap_expires_after_the_opponents_next_turn() {
    let mut game = game_with_stunfisk();

    snapping_trap(&mut game);
    end_turn(&mut game, 0);
    // Opponent lets the trapped turn pass without retreating.
    end_turn(&mut game, 1);
    end_turn(&mut game, 0);

    opponent_retreats(&mut game);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Charmander");
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        60,
        "the trap should have expired, leaving Charmander undamaged"
    );
}

/// Negative: retreating is harmless when Snapping Trap was never used.
#[test]
fn test_retreat_is_safe_without_snapping_trap() {
    let mut game = game_with_stunfisk();

    end_turn(&mut game, 0);
    opponent_retreats(&mut game);

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        60,
        "with no trap in play the promoted Pokémon should take no damage"
    );
}
