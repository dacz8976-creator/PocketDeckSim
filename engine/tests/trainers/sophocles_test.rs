use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::get_initialized_game,
};

fn make_trainer_card(card_id: CardId) -> deckgym::models::TrainerCard {
    get_card_by_enum(card_id).as_trainer()
}

/// Plays `supporter` for player 0 on a board where player 0's active is `attacker` (already
/// energized) and player 1's active is `defender`, then attacks. Returns the resulting game state.
fn play_supporter_then_attack(
    supporter: Option<CardId>,
    attacker: PlayedCard,
    defender: PlayedCard,
) -> deckgym::State {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(vec![attacker], vec![defender]);
    state.hands[0] = supporter
        .map(|id| vec![Card::Trainer(make_trainer_card(id))])
        .unwrap_or_default();
    game.set_state(state);

    if let Some(id) = supporter {
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: make_trainer_card(id),
            },
            is_stack: false,
        });
    }

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let attack = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::Attack(_)))
        .expect("Active Pokemon should be able to attack")
        .clone();
    game.apply_action(&attack);
    game.get_state_clone()
}

/// Sophocles (A3 153): "During this turn, attacks used by your Alolan Golem, Vikavolt, or
/// Togedemaru do +30 damage to your opponent's Active Pokémon."
/// Togedemaru's Bristling Spikes is 30 base, so with Sophocles it is 60 and KOs a 60 HP target.
#[test]
fn test_sophocles_boosts_togedemaru_damage_by_30() {
    let state = play_supporter_then_attack(
        Some(CardId::A3153Sophocles),
        PlayedCard::from_id(CardId::A3b048Togedemaru)
            .with_energy(vec![EnergyType::Metal, EnergyType::Metal]),
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(60),
    );

    assert_eq!(
        state.winner,
        Some(GameOutcome::Win(0)),
        "Sophocles should push Bristling Spikes to 60 and KO the 60 HP defender"
    );
}

/// Negative case: without Sophocles the same attack only does its printed 30 damage.
#[test]
fn test_togedemaru_without_sophocles_does_not_ko() {
    let state = play_supporter_then_attack(
        None,
        PlayedCard::from_id(CardId::A3b048Togedemaru)
            .with_energy(vec![EnergyType::Metal, EnergyType::Metal]),
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(60),
    );

    assert!(state.winner.is_none());
    assert_eq!(
        state.get_remaining_hp(1, 0),
        30,
        "Bristling Spikes should do its printed 30 damage without Sophocles"
    );
}

/// Negative case: Sophocles only boosts the three named Pokémon, not any attacker.
#[test]
fn test_sophocles_does_not_boost_unnamed_pokemon() {
    let state = play_supporter_then_attack(
        Some(CardId::A3195Sophocles),
        PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting]),
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(60),
    );

    assert!(state.winner.is_none());
    assert_eq!(
        state.get_remaining_hp(1, 0),
        30,
        "Hitmonlee's Kick should still do 30: Sophocles does not name it"
    );
}
