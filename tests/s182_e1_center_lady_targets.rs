//! §182 — Pokémon Center Lady target legality.
//! Built strictly from the sealed scope `s182_E1_VALID_TARGET_RULE_AND_SCOPE.txt`
//! sha256 0074324de1ddfa66726bc88a362ba1021f9870715cf826410c0907fdd78439be, committed a3f450d
//! BEFORE this file existed.
//!
//! Rule under test (DUSTIN-RULE-SENSOR): an action card needs a valid thing to act on. An
//! undamaged, unconditioned Pokémon is NOT a legal Pokémon Center Lady target, even when some
//! other Pokémon is damaged and makes the card playable.
//!
//! Results are the behaviour of the s120 SOURCE at b6ae00c, NOT of deckgym-bin-3518-s120k.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard, StatusCondition, TrainerCard},
    test_support::get_initialized_game,
    Game,
};

fn center_lady() -> TrainerCard {
    match get_card_by_enum(CardId::A2b070PokemonCenterLady) {
        Card::Trainer(tc) => tc,
        _ => panic!("expected a trainer card"),
    }
}

fn game_with(board: Vec<PlayedCard>) -> Game<'static> {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(board, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::A2b070PokemonCenterLady)];
    game.set_state(state);
    game
}

/// Is a `Play` action for Pokémon Center Lady offered at all?
fn center_lady_playable(game: &Game<'static>) -> bool {
    let state = game.get_state_clone();
    let (_actor, choices) = state.generate_possible_actions();
    choices.iter().any(|a| {
        matches!(&a.action, SimpleAction::Play { trainer_card }
            if trainer_card.id == center_lady().id)
    })
}

/// Play the card and return the in-play indices offered as heal targets, ascending.
fn offered_heal_targets(game: &mut Game<'static>) -> Vec<usize> {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: center_lady(),
        },
        is_stack: false,
    });
    let state = game.get_state_clone();
    let (_actor, choices) = state.generate_possible_actions();
    let mut idx: Vec<usize> = choices
        .iter()
        .filter_map(|a| match a.action {
            SimpleAction::Heal { in_play_idx, .. } => Some(in_play_idx),
            _ => None,
        })
        .collect();
    idx.sort_unstable();
    idx.dedup();
    idx
}

fn bulbasaur() -> PlayedCard {
    PlayedCard::from_id(CardId::A1001Bulbasaur)
}

// T1 — mixed board: only the damaged Active is a legal target.
#[test]
fn t1_mixed_board_offers_only_the_damaged_pokemon() {
    let mut game = game_with(vec![bulbasaur().with_damage(50), bulbasaur()]);
    let targets = offered_heal_targets(&mut game);
    println!("[T1] active damaged 50, bench undamaged+unconditioned -> heal targets {targets:?}");
    assert_eq!(
        targets,
        vec![0],
        "an undamaged, unconditioned Pokemon is not a legal target"
    );
}

// T2 — status-only board: the conditioned Active is legal, the untouched bench is not.
#[test]
fn t2_status_only_board_offers_only_the_conditioned_pokemon() {
    let mut game = game_with(vec![
        bulbasaur().with_status_condition(StatusCondition::Asleep),
        bulbasaur(),
    ]);
    let targets = offered_heal_targets(&mut game);
    println!("[T2] active undamaged+Asleep, bench undamaged+unconditioned -> heal targets {targets:?}");
    assert_eq!(
        targets,
        vec![0],
        "a Special Condition makes an undamaged Pokemon valid; the untouched one stays invalid"
    );
}

// T3 — playability control: with no valid target the card may not be played at all.
#[test]
fn t3_no_valid_target_makes_the_card_unplayable() {
    let game = game_with(vec![bulbasaur(), bulbasaur()]);
    let playable = center_lady_playable(&game);
    println!("[T3] board wholly undamaged and unconditioned -> Center Lady playable: {playable}");
    assert!(
        !playable,
        "an action card with no valid thing to act on must not be playable"
    );
}

// T4 — falsifiability control: two valid targets must both be offered.
#[test]
fn t4_two_damaged_pokemon_offer_two_targets() {
    let mut game = game_with(vec![bulbasaur().with_damage(50), bulbasaur().with_damage(20)]);
    let targets = offered_heal_targets(&mut game);
    println!("[T4] active damaged 50, bench damaged 20 -> heal targets {targets:?}");
    assert_eq!(
        targets,
        vec![0, 1],
        "with two valid targets the fixture must see both, or 'exactly one' means nothing"
    );
}
