use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Espathra (B3a 022) "Lumina Crash": "During your next turn, the Defending Pokémon takes +50
/// damage from attacks."
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn game_with_espathra() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a022Espathra)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
        // 180 HP, no Weakness.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    )
}

fn lumina_crash(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a022Espathra, 0),
        is_stack: false,
    });
}

#[test]
fn test_espathra_lumina_crash_adds_vulnerability_on_your_next_turn() {
    let mut game = game_with_espathra();

    lumina_crash(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        130,
        "Lumina Crash does its printed 50 damage, with no bonus on the turn it is used"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    lumina_crash(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        30,
        "on the following turn the Defending Pokémon should take 50 + 50 = 100"
    );
}

/// Negative: the vulnerability covers exactly one of your turns.
#[test]
fn test_espathra_lumina_crash_vulnerability_expires() {
    let mut game = game_with_espathra();

    lumina_crash(&mut game);
    // Let the boosted turn go by without attacking.
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    let before = game.get_state_clone().get_active(1).get_remaining_hp();
    lumina_crash(&mut game);
    let damage = before - game.get_state_clone().get_active(1).get_remaining_hp();

    assert_eq!(
        damage, 50,
        "the +50 vulnerability should have expired after your next turn"
    );
}
