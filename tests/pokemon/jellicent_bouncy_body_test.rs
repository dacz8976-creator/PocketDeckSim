use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Player 0's Pikachu (Gnaw, 20 damage) attacks player 1's Jellicent, which is Active behind
/// `defender_bench`.
fn attack_jellicent(defender_bench: Vec<PlayedCard>) -> Game<'static> {
    let mut defender_board = vec![PlayedCard::from_id(CardId::B1069Jellicent)];
    defender_board.extend(defender_bench);

    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1094Pikachu).with_energy(vec![EnergyType::Lightning])],
        defender_board,
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1094Pikachu, 0),
        is_stack: false,
    });

    game
}

/// Jellicent (B1 069 / B1 234 / B3 210) "Bouncy Body": "If this Pokémon is in the Active Spot and
/// is damaged by an attack from your opponent's Pokémon, take a [W] Energy from your Energy Zone
/// and attach it to 1 of your Benched Pokémon."
///
/// The Benched Pokémon is Jellicent's controller's choice, so the trigger hands player 1 a
/// decision in the middle of player 0's turn.
#[test]
fn test_bouncy_body_attaches_water_energy_to_a_chosen_benched_pokemon() {
    let mut game = attack_jellicent(vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::A1033Charmander),
    ]);

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(
        actor, 1,
        "Bouncy Body's choice belongs to Jellicent's owner"
    );

    let to_bulbasaur = SimpleAction::Attach {
        attachments: vec![(1, EnergyType::Water, 1)],
        is_turn_energy: false,
    };
    let to_charmander = SimpleAction::Attach {
        attachments: vec![(1, EnergyType::Water, 2)],
        is_turn_energy: false,
    };
    assert!(actions.iter().any(|a| a.action == to_charmander));
    let choice = actions
        .into_iter()
        .find(|a| a.action == to_bulbasaur)
        .expect("Bouncy Body should offer each Benched Pokémon as a target");
    game.apply_action(&choice);

    let state = game.get_state_clone();
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .expect("Bulbasaur should still be benched")
            .attached_energy,
        vec![EnergyType::Water],
        "the chosen Benched Pokémon should receive the [W] Energy"
    );
    assert!(
        state.in_play_pokemon[1][0]
            .as_ref()
            .expect("Jellicent survived Gnaw")
            .attached_energy
            .is_empty(),
        "Bouncy Body attaches to the Bench, never to Jellicent itself"
    );
}

/// Negative test: with nothing on the Bench there is no legal target, so the trigger is skipped
/// entirely and play returns to the attacker rather than stalling on an empty choice list.
#[test]
fn test_bouncy_body_does_nothing_with_an_empty_bench() {
    let game = attack_jellicent(vec![]);

    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0]
        .as_ref()
        .expect("Jellicent survived Gnaw")
        .attached_energy
        .is_empty());

    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, 0, "play should return to the attacking player");
    assert!(
        !actions
            .iter()
            .any(|a| matches!(a.action, SimpleAction::Attach { .. })),
        "no Bouncy Body attachment should be pending"
    );
}

/// Negative test: Bouncy Body keys off damage "from an attack", so Poison damage during Pokémon
/// Checkup does not trigger it.
#[test]
fn test_bouncy_body_does_not_trigger_on_non_attack_damage() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1094Pikachu)],
        vec![
            PlayedCard::from_id(CardId::B1069Jellicent),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );

    let mut state = game.get_state_clone();
    state.apply_status_condition(1, 0, StatusCondition::Poisoned);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    let state = game.get_state_clone();
    let jellicent = state.in_play_pokemon[1][0]
        .as_ref()
        .expect("Jellicent should survive one Poison tick");
    assert_eq!(
        jellicent.get_remaining_hp(),
        110,
        "Poison should have dealt its 10 damage"
    );
    assert!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .expect("Bulbasaur should still be benched")
            .attached_energy
            .is_empty(),
        "Poison damage is not an attack, so Bouncy Body must not fire"
    );
}
