use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Board where the opponent could ordinarily retreat: their Mega Latios ex Active has plenty of
/// energy and a Benched Pokémon to retreat into.
fn game_with_attacker(seed: u64, attacker: PlayedCard) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![attacker],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    )
}

fn end_turn(game: &mut Game<'static>) {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    let end = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::EndTurn))
        .unwrap_or_else(|| panic!("EndTurn should be available for player {actor}"))
        .clone();
    game.apply_action(&end);
    game.play_until_stable();
}

fn opponent_can_retreat(game: &Game<'static>) -> bool {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "should be the opponent's turn");
    choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Retreat(_)))
}

/// Roserade (B2 005) "Poison Ring": 50 damage, Poisoned, and during your opponent's next turn the
/// Defending Pokémon can't retreat.
#[test]
fn test_roserade_poison_ring_poisons_and_blocks_retreat() {
    let roserade = PlayedCard::from_id(CardId::B2005Roserade)
        .with_energy(vec![EnergyType::Grass, EnergyType::Grass]);
    let mut game = game_with_attacker(0, roserade);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2005Roserade, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(180 - defender.get_remaining_hp(), 50, "Poison Ring does 50");
    assert!(defender.is_poisoned(), "defender must be Poisoned");

    // Move into the opponent's turn (Checkup ticks 10 normal poison on the way).
    end_turn(&mut game);
    let state = game.get_state_clone();
    assert_eq!(
        180 - state.get_active(1).get_remaining_hp(),
        60,
        "Poison Ring's poison is ordinary: 50 attack + 10 poison tick"
    );
    assert!(
        !opponent_can_retreat(&game),
        "the Defending Pokémon must not be able to retreat during the opponent's next turn"
    );
}

/// Negative control: an attack that merely Poisons (Salazzle's Heated Poison) must NOT block the
/// defender's retreat.
#[test]
fn test_plain_poison_attack_does_not_block_retreat() {
    let salazzle = PlayedCard::from_id(CardId::A3036Salazzle)
        .with_energy(vec![EnergyType::Fire, EnergyType::Fire]);
    let mut game = game_with_attacker(0, salazzle);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3036Salazzle, 0),
        is_stack: false,
    });
    end_turn(&mut game);
    assert!(
        opponent_can_retreat(&game),
        "a plain status attack must leave retreat available"
    );
}
