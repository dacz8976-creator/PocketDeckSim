use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard, TrainerCard},
    test_support::get_initialized_game,
    Game,
};

/// Indeedee ex starts damaged by this much; the tests compare remaining HP against it.
const DAMAGE: u32 = 40;

/// Indeedee ex's printed HP, so the tests can talk in remaining HP.
fn undamaged_hp() -> u32 {
    PlayedCard::from_id(CardId::B1121IndeedeeEx).get_remaining_hp()
}

fn potion() -> TrainerCard {
    match get_card_by_enum(CardId::PA001Potion) {
        Card::Trainer(trainer_card) => trainer_card,
        _ => panic!("Potion should be a Trainer card"),
    }
}

/// A damaged Indeedee ex (its Watch Over Ability heals 20 from your Active Pokémon) with a Potion
/// in hand, against a Bulbasaur. `own_bench` / `opponent_bench` decide where — if anywhere — a
/// Claydol (A3a 031, Heal Block) sits.
fn game_with_claydol(own_bench: Option<CardId>, opponent_bench: Option<CardId>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();

    let mut own_board = vec![PlayedCard::from_id(CardId::B1121IndeedeeEx).with_damage(DAMAGE)];
    own_board.extend(own_bench.map(PlayedCard::from_id));
    let mut opponent_board = vec![PlayedCard::from_id(CardId::A1001Bulbasaur)];
    opponent_board.extend(opponent_bench.map(PlayedCard::from_id));

    state.set_board(own_board, opponent_board);
    state.current_player = 0;
    state.turn_count = 3;
    state.hands[0] = vec![Card::Trainer(potion())];
    game.set_state(state);
    game
}

/// Uses Indeedee ex's Watch Over ("heal 20 damage from your Active Pokémon") and returns the
/// remaining HP of the Active Pokémon.
fn heal_with_ability(game: &mut Game<'static>) -> u32 {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 0 },
        is_stack: false,
    });
    game.get_state_clone().get_active(0).get_remaining_hp()
}

/// Plays Potion ("heal 20 damage from 1 of your Pokémon") on the Active Pokémon and returns the
/// remaining HP of it.
fn heal_with_potion(game: &mut Game<'static>) -> u32 {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: potion(),
        },
        is_stack: false,
    });
    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    let heal_active = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Heal { in_play_idx: 0, .. }))
        .expect("Potion should offer to heal the Active Pokémon")
        .clone();
    game.apply_action(&heal_active);
    game.get_state_clone().get_active(0).get_remaining_hp()
}

/// Heal Block: "Pokémon (both yours and your opponent's) can't be healed." An Ability heal is
/// suppressed while Claydol is on your own Bench.
#[test]
fn test_heal_block_stops_an_ability_heal() {
    let mut game = game_with_claydol(Some(CardId::A3a031Claydol), None);

    assert_eq!(
        heal_with_ability(&mut game),
        undamaged_hp() - DAMAGE,
        "Watch Over must not remove any damage while Heal Block is in play"
    );
}

/// A second, unrelated healing source: a Trainer card. Both must go through the same gate.
#[test]
fn test_heal_block_stops_a_trainer_heal() {
    let mut game = game_with_claydol(Some(CardId::A3a031Claydol), None);

    assert_eq!(
        heal_with_potion(&mut game),
        undamaged_hp() - DAMAGE,
        "Potion must not remove any damage while Heal Block is in play"
    );
}

/// "Both yours and your opponent's": the opponent's Claydol blocks your healing too.
#[test]
fn test_heal_block_from_the_opponents_board_stops_your_heal() {
    let mut game = game_with_claydol(None, Some(CardId::A3a031Claydol));

    assert_eq!(
        heal_with_ability(&mut game),
        undamaged_hp() - DAMAGE,
        "Heal Block is symmetric, so the opponent's Claydol blocks your Ability heal"
    );
}

/// NEGATIVE: with no Claydol anywhere, the Ability heal works normally.
#[test]
fn test_ability_heal_works_without_claydol_in_play() {
    let mut game = game_with_claydol(Some(CardId::A1001Bulbasaur), None);

    assert_eq!(
        heal_with_ability(&mut game),
        undamaged_hp() - DAMAGE + 20,
        "Watch Over should heal 20 when Heal Block is not in play"
    );
}

/// NEGATIVE: and so does the Trainer heal.
#[test]
fn test_trainer_heal_works_without_claydol_in_play() {
    let mut game = game_with_claydol(Some(CardId::A1001Bulbasaur), None);

    assert_eq!(
        heal_with_potion(&mut game),
        undamaged_hp() - DAMAGE + 20,
        "Potion should heal 20 when Heal Block is not in play"
    );
}
