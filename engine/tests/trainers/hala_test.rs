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

/// Player 0 has `defender` (already damaged) as their active plus a spare bench Pokémon so the
/// game does not end on a knockout; player 1 has a Hitmonlee ready to Kick for 30.
fn game_with_defender(defender: PlayedCard, hala: Option<CardId>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![defender, PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A2b040Hitmonlee).with_energy(vec![EnergyType::Fighting])],
    );
    state.hands[0] = hala
        .map(|id| vec![Card::Trainer(make_trainer_card(id))])
        .unwrap_or_default();
    game.set_state(state);

    if let Some(id) = hala {
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: make_trainer_card(id),
            },
            is_stack: false,
        });
    }
    game
}

fn end_turn_and_attack(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
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

/// Hala (B1 222): "During your opponent's next turn, if your Hariyama or Crabominable would be
/// Knocked Out by damage from an attack, it is not Knocked Out and its remaining HP becomes 10."
#[test]
fn test_hala_leaves_hariyama_at_10_hp_instead_of_knocking_it_out() {
    let mut game = game_with_defender(
        PlayedCard::from_id(CardId::B1127Hariyama).with_remaining_hp(30),
        Some(CardId::B1222Hala),
    );
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    let hariyama = state.in_play_pokemon[0][0]
        .as_ref()
        .expect("Hariyama should still be in play behind Hala");
    assert_eq!(hariyama.get_name(), "Hariyama");
    assert_eq!(hariyama.get_remaining_hp(), 10);
    assert_eq!(
        state.points[1], 0,
        "No knockout happened, so the opponent scores nothing"
    );
}

/// Negative case: the same board without Hala loses the Hariyama and gives up a point.
#[test]
fn test_hariyama_without_hala_is_knocked_out() {
    let mut game = game_with_defender(
        PlayedCard::from_id(CardId::B1127Hariyama).with_remaining_hp(30),
        None,
    );
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(state.points[1], 1, "Hariyama should have been Knocked Out");
    assert!(state.in_play_pokemon[0]
        .iter()
        .flatten()
        .all(|p| p.get_name() != "Hariyama"));
}

/// Negative case: Hala only names Hariyama and Crabominable — anything else still dies.
#[test]
fn test_hala_does_not_save_unnamed_pokemon() {
    let mut game = game_with_defender(
        PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(30),
        Some(CardId::B1267Hala),
    );
    end_turn_and_attack(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.points[1], 1,
        "Charmander is not named by Hala, so it is Knocked Out normally"
    );
}
