use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Gothitelle (B1 114) "Stellar Cradle": "During your opponent's next turn, if they attach Energy
/// from their Energy Zone to the Defending Pokémon, that Pokémon will be Asleep."
fn game_with_gothitelle() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1114Gothitelle)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
        vec![
            // 180 HP, no Weakness: survives Stellar Cradle's 70 damage.
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    )
}

fn stellar_cradle(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1114Gothitelle, 0),
        is_stack: false,
    });
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

/// Finds the opponent's Energy-Zone attachment onto `in_play_idx` and plays it.
fn attach_energy_to(game: &mut Game<'static>, in_play_idx: usize) {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "it should be the opponent's turn");
    let attach = choices
        .iter()
        .find(|choice| match &choice.action {
            SimpleAction::Attach {
                attachments,
                is_turn_energy,
            } => *is_turn_energy && attachments.iter().all(|(_, _, idx)| *idx == in_play_idx),
            _ => false,
        })
        .unwrap_or_else(|| panic!("expected an Energy Zone attachment onto slot {in_play_idx}"))
        .clone();
    game.apply_action(&attach);
}

#[test]
fn test_gothitelle_stellar_cradle_puts_the_defender_to_sleep_on_energy_attach() {
    let mut game = game_with_gothitelle();
    stellar_cradle(&mut game);

    assert!(
        !game.get_state_clone().get_active(1).is_asleep(),
        "the Defending Pokémon should still be awake before any Energy is attached"
    );

    attach_energy_to(&mut game, 0);

    assert!(
        game.get_state_clone().get_active(1).is_asleep(),
        "attaching Energy from the Energy Zone to the Defending Pokémon should put it to Sleep"
    );
}

/// Negative: only the Defending Pokémon carries the effect. Attaching to the Bench is safe.
#[test]
fn test_gothitelle_stellar_cradle_ignores_attachments_to_other_pokemon() {
    let mut game = game_with_gothitelle();
    stellar_cradle(&mut game);

    attach_energy_to(&mut game, 1);

    let state = game.get_state_clone();
    assert!(
        !state.get_active(1).is_asleep(),
        "the Defending Pokémon should stay awake when the Energy went to the Bench"
    );
    assert!(
        !state.in_play_pokemon[1][1]
            .as_ref()
            .expect("benched Charmander")
            .is_asleep(),
        "the Benched Pokémon never had the effect, so it should not fall asleep either"
    );
}

/// Negative: with no Stellar Cradle in play, attaching Energy is harmless.
#[test]
fn test_energy_attach_does_not_cause_sleep_without_stellar_cradle() {
    let mut game = game_with_gothitelle();
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();

    attach_energy_to(&mut game, 0);

    assert!(
        !game.get_state_clone().get_active(1).is_asleep(),
        "attaching Energy should not cause Sleep on its own"
    );
}
