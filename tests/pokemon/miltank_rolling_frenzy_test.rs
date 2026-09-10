use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Miltank (A4a 062 / P-A 107) "Rolling Frenzy": "Until this Pokémon leaves the Active Spot, this
/// Pokémon's Rolling Frenzy attack does +30 damage. This effect stacks."
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn rolling_frenzy(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a062Miltank, 0),
        is_stack: false,
    });
}

#[test]
fn test_miltank_rolling_frenzy_stacks_with_each_use() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a062Miltank).with_energy(vec![EnergyType::Colorless])],
        // 180 HP, no Weakness.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    rolling_frenzy(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        170,
        "the first Rolling Frenzy does its printed 10 damage"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    rolling_frenzy(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        130,
        "the second Rolling Frenzy should do 10 + 30 = 40 damage"
    );

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    rolling_frenzy(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        60,
        "the bonus stacks: the third Rolling Frenzy should do 10 + 60 = 70 damage"
    );
}

/// Negative: the stack is wiped once Miltank leaves the Active Spot.
#[test]
fn test_miltank_rolling_frenzy_bonus_resets_after_leaving_the_active_spot() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4a062Miltank).with_energy(vec![
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless,
                EnergyType::Colorless,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );

    rolling_frenzy(&mut game);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);

    // Miltank retreats (Retreat Cost 3) and comes back a turn later.
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });

    let before = game.get_state_clone().get_active(1).get_remaining_hp();
    rolling_frenzy(&mut game);
    let damage = before - game.get_state_clone().get_active(1).get_remaining_hp();

    assert_eq!(
        damage, 10,
        "the +30 should be gone after Miltank left the Active Spot"
    );
}
