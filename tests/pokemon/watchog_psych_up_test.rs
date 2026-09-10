use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Watchog (B3 136) "Psych Up": "During your next turn, this Pokémon's Psych Up attack does +30
/// damage."
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn game_with_watchog() -> Game<'static> {
    get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3136Watchog).with_energy(vec![EnergyType::Colorless])],
        // 180 HP, no Weakness.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    )
}

fn psych_up(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3136Watchog, 0),
        is_stack: false,
    });
}

#[test]
fn test_watchog_psych_up_boosts_the_next_psych_up() {
    let mut game = game_with_watchog();

    psych_up(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        150,
        "the first Psych Up does its printed 30 damage"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    psych_up(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        90,
        "the follow-up Psych Up should do 30 + 30 = 60 damage"
    );
}

/// Negative: the boost only covers your very next turn.
#[test]
fn test_watchog_psych_up_boost_expires_if_unused() {
    let mut game = game_with_watchog();

    psych_up(&mut game);
    // Skip the boosted turn.
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    let before = game.get_state_clone().get_active(1).get_remaining_hp();
    psych_up(&mut game);
    let damage = before - game.get_state_clone().get_active(1).get_remaining_hp();

    assert_eq!(damage, 30, "the +30 should have expired after one turn");
}
