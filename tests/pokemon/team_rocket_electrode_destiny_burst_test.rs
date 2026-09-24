use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

fn destiny_burst_double_knockout(attacking_player: usize) {
    let defending_player = (attacking_player + 1) % 2;
    let attacker_board = vec![
        PlayedCard::from_id(CardId::B3024CastformSunnyForm)
            .with_remaining_hp(20)
            .with_energy(vec![EnergyType::Fire]),
        PlayedCard::from_id(CardId::B3226MegaBlazikenEx),
    ];
    let defender_board = vec![
        PlayedCard::from_id(CardId::B4a020TeamRocketsElectrode)
            .with_remaining_hp(20)
            .with_energy(vec![EnergyType::Lightning])
            .with_tools(vec![deckgym::database::get_card_by_enum(
                CardId::A4b322RockyHelmet,
            )]),
        PlayedCard::from_id(CardId::B4a021TeamRocketsZapdosEx),
    ];
    let (player_0_board, player_1_board) = if attacking_player == 0 {
        (attacker_board, defender_board)
    } else {
        (defender_board, attacker_board)
    };
    let mut game = get_initialized_game_with_board(
        0,
        attacking_player,
        5,
        player_0_board,
        player_1_board,
    );
    let mut state = game.get_state_clone();
    state.set_active_stadium(deckgym::database::get_card_by_enum(CardId::B2a093Mesagoza));
    game.set_state(state);

    game.apply_action(&Action {
        actor: attacking_player,
        action: attack_action(CardId::B3024CastformSunnyForm, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.points, [1, 1], "attacking seat {attacking_player}");
    assert!(state.in_play_pokemon[attacking_player][0].is_none());
    assert!(state.in_play_pokemon[defending_player][0].is_none());
    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, attacking_player, "the turn player promotes first after the double knockout");
    assert!(actions.iter().any(|action| matches!(
        action.action,
        SimpleAction::Promote { player, in_play_idx: 1 } if player == attacking_player
    )));
}

#[test]
fn destiny_burst_can_hit_an_attacker_already_knocked_out_by_rocky_helmet() {
    destiny_burst_double_knockout(0);
    destiny_burst_double_knockout(1);
}
