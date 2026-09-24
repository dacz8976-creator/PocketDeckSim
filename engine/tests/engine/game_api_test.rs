use deckgym::{
    players::{AttachAttackPlayer, EndTurnPlayer, MctsPlayer, Player, RandomPlayer},
    state::GameOutcome,
    test_support::{init_random_players, load_test_decks},
};

#[test]
fn test_game_api() {
    let players = init_random_players();
    let mut game = deckgym::Game::new(players, 0);
    game.play();
}

#[test]
fn test_mcts_player() {
    let (deck_a, deck_b) = load_test_decks();
    let player_a = Box::new(RandomPlayer { deck: deck_a });
    let player_b = Box::new(MctsPlayer::new(deck_b, 5));
    let players: Vec<Box<dyn Player>> = vec![player_a, player_b];
    let mut game = deckgym::Game::new(players, 6);

    // TODO: We segment the ticks like this so that this test can also be helpful
    // to print out the tree to .dot file and inspect it.
    // while game.get_state_clone().turn_count < 40 {
    //     game.play_tick();
    // }
    game.play();
}

#[test]
fn test_retreat_should_cure_poison() {
    let players = init_random_players();
    let mut game = deckgym::Game::new(players, 1406385978241804004);
    game.play();
}

#[test]
fn test_first_ko() {
    let (deck_a, deck_b) = load_test_decks();
    let player_a = Box::new(AttachAttackPlayer { deck: deck_a });
    let player_b = Box::new(EndTurnPlayer { deck: deck_b });
    let players: Vec<Box<dyn Player>> = vec![player_a, player_b];
    let mut game = deckgym::Game::new(players, 3);

    // The opening shuffle is not a fixed board fixture. The passive opponent has
    // no Bench, so the first knockout ends the game regardless of the dealt Basic.
    for _ in 0..256 {
        if game.get_state_clone().winner.is_some() { break; }
        game.play_tick();
    }
    let state = game.get_state_clone();
    assert_eq!(state.winner, Some(GameOutcome::Win(0)));
    assert!(state.turn_count <= 30);
    assert!(state.points[0] >= 1);
    assert!(state.in_play_pokemon[1][0].is_none());
}
