//! Blue, Jasmine, Cheren and Beast Wall all read "During your opponent's next turn, <some of>
//! your Pokémon take -N damage from attacks from your opponent's Pokémon", so they are covered
//! together here: each has a positive case (the protected Pokémon survives an attack that would
//! otherwise KO it) and a negative case (an unprotected Pokémon, or an unmet play condition).

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::get_initialized_game,
    Game,
};

fn make_trainer_card(card_id: CardId) -> deckgym::models::TrainerCard {
    get_card_by_enum(card_id).as_trainer()
}

/// Board where player 0 (about to play a defensive trainer) has `defender` as their active and
/// player 1 has `attacker`. Player 0's hand holds only `trainer`.
fn game_with_defender(
    trainer: CardId,
    defender: PlayedCard,
    attacker: PlayedCard,
) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(vec![defender], vec![attacker]);
    state.hands[0] = vec![Card::Trainer(make_trainer_card(trainer))];
    game.set_state(state);
    game
}

fn play_trainer(game: &mut Game<'static>, trainer: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: make_trainer_card(trainer),
        },
        is_stack: false,
    });
}

fn end_turn_and_attack(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    // Resolve the forced start-of-turn draw before the opponent gets a free choice.
    game.play_until_stable();

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "It should be the opponent's turn");
    let attack = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::Attack(_)))
        .unwrap_or_else(|| panic!("Opponent should be able to attack, got {actions:?}"))
        .clone();
    game.apply_action(&attack);
}

// --- Blue ---

/// Blue (A1a 067): "During your opponent's next turn, all of your Pokémon take -10 damage from
/// attacks from your opponent's Pokémon."
/// Hitmonlee's Kick is 30, so a 30 HP Bulbasaur survives on 10 HP behind Blue.
#[test]
fn test_blue_reduces_damage_to_all_your_pokemon_by_10() {
    let mut game = game_with_defender(
        CardId::A1a067Blue,
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(30),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    play_trainer(&mut game, CardId::A1a067Blue);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert!(
        state.winner.is_none(),
        "Bulbasaur should survive behind Blue"
    );
    assert_eq!(state.get_remaining_hp(0, 0), 10);
}

/// Negative case: the reduction lasts only for the opponent's next turn, so a Bulbasaur that is
/// not protected takes the full 30 and is Knocked Out.
#[test]
fn test_without_blue_the_same_attack_knocks_out() {
    let mut game = game_with_defender(
        CardId::A1a067Blue,
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(30),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    // Deliberately do NOT play Blue.
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[0][0].is_none() || state.winner.is_some(),
        "Bulbasaur should be Knocked Out without Blue"
    );
}

// --- Jasmine ---

/// Jasmine (A4 160): "During your opponent's next turn, all of your Steelix and Skarmory ex take
/// -50 damage from attacks from your opponent's Pokémon."
/// Hitmonlee's 30-damage Kick is fully absorbed by the -50.
#[test]
fn test_jasmine_protects_steelix() {
    let mut game = game_with_defender(
        CardId::A4160Jasmine,
        PlayedCard::from_id(CardId::A4122Steelix).with_remaining_hp(30),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    play_trainer(&mut game, CardId::A4160Jasmine);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_remaining_hp(0, 0),
        30,
        "Jasmine's -50 should fully absorb a 30 damage Kick on Steelix"
    );
}

/// Negative case: Jasmine names only Steelix and Skarmory ex, so an unnamed Pokémon on the same
/// board takes full damage.
#[test]
fn test_jasmine_does_not_protect_unnamed_pokemon() {
    let mut game = game_with_defender(
        CardId::A4200Jasmine,
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(60),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    play_trainer(&mut game, CardId::A4200Jasmine);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_remaining_hp(0, 0),
        30,
        "Bulbasaur is not named by Jasmine, so it takes the full 30"
    );
}

// --- Cheren ---

/// Cheren (B3 151): "During your opponent's next turn, all of your Watchog and Stoutland take
/// -100 damage from attacks from your opponent's Pokémon ex."
/// Mewtwo ex's Psychic Sphere is 50, fully absorbed by the -100.
#[test]
fn test_cheren_protects_watchog_from_ex_attacker() {
    let mut game = game_with_defender(
        CardId::B3151Cheren,
        PlayedCard::from_id(CardId::B1200Watchog),
        PlayedCard::from_id(CardId::A1129MewtwoEx)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic]),
    );
    play_trainer(&mut game, CardId::B3151Cheren);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_remaining_hp(0, 0),
        100,
        "Cheren's -100 should fully absorb Psychic Sphere from a Pokémon ex"
    );
}

/// Negative case: Cheren only reduces damage from the opponent's Pokémon **ex**. A non-ex
/// attacker gets through for full damage.
#[test]
fn test_cheren_does_not_protect_against_non_ex_attacker() {
    let mut game = game_with_defender(
        CardId::B3192Cheren,
        PlayedCard::from_id(CardId::B1200Watchog),
        PlayedCard::from_id(CardId::A3b048Togedemaru)
            .with_energy(vec![EnergyType::Metal, EnergyType::Metal]),
    );
    play_trainer(&mut game, CardId::B3192Cheren);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_remaining_hp(0, 0),
        70,
        "Togedemaru is not a Pokémon ex, so Cheren does not apply"
    );
}

// --- Beast Wall ---

/// Beast Wall (A3a 063): "You can use this card only if your opponent hasn't gotten any points.
/// During your opponent's next turn, all of your Ultra Beasts take -20 damage from attacks from
/// your opponent's Pokémon."
#[test]
fn test_beast_wall_protects_ultra_beasts() {
    let mut game = game_with_defender(
        CardId::A3a063BeastWall,
        PlayedCard::from_id(CardId::A3a008Kartana).with_remaining_hp(30),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    play_trainer(&mut game, CardId::A3a063BeastWall);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert!(state.winner.is_none());
    assert_eq!(
        state.get_remaining_hp(0, 0),
        20,
        "Beast Wall's -20 should let a 30 HP Kartana survive a 30 damage Kick"
    );
}

/// Negative case: Beast Wall can't be played once the opponent has scored a point.
#[test]
fn test_beast_wall_unplayable_when_opponent_has_points() {
    let mut game = game_with_defender(
        CardId::A3a063BeastWall,
        PlayedCard::from_id(CardId::A3a008Kartana),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    let mut state = game.get_state_clone();
    state.points[1] = 1;
    game.set_state(state);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        !actions.iter().any(|a| matches!(
            &a.action,
            SimpleAction::Play { trainer_card } if trainer_card.name == "Beast Wall"
        )),
        "Beast Wall should not be playable once the opponent has a point"
    );
}

/// Negative case: Beast Wall only protects Ultra Beasts, not every Pokémon you control.
#[test]
fn test_beast_wall_does_not_protect_non_ultra_beasts() {
    let mut game = game_with_defender(
        CardId::A3a063BeastWall,
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(60),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
    );
    play_trainer(&mut game, CardId::A3a063BeastWall);
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_remaining_hp(0, 0),
        30,
        "Bulbasaur is not an Ultra Beast, so Beast Wall does not apply"
    );
}
