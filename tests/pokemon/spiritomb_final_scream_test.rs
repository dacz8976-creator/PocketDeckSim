use deckgym::{actions::Action, Game};
use deckgym::{
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Spiritomb (B2 103) "Final Scream": "If this Pokémon is in the Active Spot and is Knocked Out by
/// damage from an attack from your opponent's Pokémon, do 10 damage to each of your opponent's
/// Pokémon."
///
/// Mega Latios ex (180 HP, no weakness) attacks so that its own HP after the retaliation is a
/// plain delta rather than a knockout.
fn attack_with_mega_latios(opponent_board: Vec<PlayedCard>) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        opponent_board,
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });
    game
}

#[test]
fn test_final_scream_damages_every_opponent_pokemon() {
    let game = attack_with_mega_latios(vec![
        PlayedCard::from_id(CardId::B2103Spiritomb),
        PlayedCard::from_id(CardId::A1033Charmander),
    ]);

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "Spiritomb should be Knocked Out by the attack"
    );
    assert_eq!(state.points[0], 1);

    // Active and both Benched Pokémon each take 10.
    assert_eq!(state.get_active(0).get_remaining_hp(), 180 - 10);
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("bench slot 1")
            .get_remaining_hp(),
        60 - 10
    );
    assert_eq!(
        state.in_play_pokemon[0][2]
            .as_ref()
            .expect("bench slot 2")
            .get_remaining_hp(),
        70 - 10
    );
}

/// The spread damage can finish off the opponent's Benched Pokémon, which scores for Spiritomb's
/// owner even though the Bench is never promoted from.
#[test]
fn test_final_scream_can_knock_out_a_benched_pokemon() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(10),
        ],
        vec![
            PlayedCard::from_id(CardId::B2103Spiritomb),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[0][1].is_none(),
        "the 10 HP Benched Charmander should be Knocked Out by Final Scream"
    );
    assert_eq!(
        state.points,
        [1, 1],
        "each player scores one knockout: Spiritomb and the Benched Charmander"
    );
}

/// Final Scream is a knockout trigger: damage that leaves Spiritomb alive must not retaliate.
#[test]
fn test_final_scream_does_not_trigger_without_a_knockout() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::B2103Spiritomb),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    // Vine Whip does 40, +20 for Spiritomb's Grass weakness: 60 of its 70 HP.
    assert_eq!(state.get_active(1).get_remaining_hp(), 70 - 60);
    assert_eq!(state.get_active(0).get_remaining_hp(), 70);
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("bench slot 1")
            .get_remaining_hp(),
        60
    );
}

/// Final Scream only triggers from the Active Spot: a benched Spiritomb Knocked Out by spread
/// damage must not retaliate.
#[test]
fn test_final_scream_does_not_trigger_from_the_bench() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A2104Spiritomb).with_energy(vec![EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::B2103Spiritomb).with_remaining_hp(10),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2104Spiritomb, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][1].is_none(),
        "the benched Spiritomb should be Knocked Out"
    );
    assert_eq!(state.points[0], 1);
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        80,
        "Final Scream must not fire from the bench"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .expect("bench slot 1")
            .get_remaining_hp(),
        60
    );
}
