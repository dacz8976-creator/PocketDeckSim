//! Regression proposed from the accepted Luckycad Xatu recording transitions.
//!
//! This file adds only the coverage gap. Team Rocket's Master Plan is already covered by
//! `b4a_trainer_batch2_test::master_plan_always_confuses_opponent_and_tails_confuses_self`:
//! the fair Heads branch (probability 0.5) confuses the opponent only, while the fair Tails
//! branch (probability 0.5) confuses both Active Pokémon. The recording observed Heads.

use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

#[test]
fn fighting_pulse_ko_still_triggers_defenders_poison_barb() {
    // Recording 02:59-03:10: B1 097 Natu is at 40 HP with A3 146 Poison Barb;
    // B3 081 Mega Lucario ex uses Fighting Pulse, Natu reaches 0 HP, Poison Barb
    // makes Mega Lucario ex Poisoned, and the knockout awards one point.
    //
    // Fighting Pulse is deterministic here: three Fighting Energy select its boosted
    // 140-damage path before weakness, so this transition has no coin branch. The Benched Pokémon are
    // fixture scaffolding that keeps the post-knockout state nonterminal and inspectable.
    let mega_lucario = PlayedCard::from_id(CardId::B3081MegaLucarioEx).with_energy(vec![
        EnergyType::Fighting,
        EnergyType::Fighting,
        EnergyType::Fighting,
    ]);
    let natu = PlayedCard::from_id(CardId::B1097Natu)
        .with_remaining_hp(40)
        .with_tool(get_card_by_enum(CardId::A3146PoisonBarb));

    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            mega_lucario,
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![natu, PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.points = [0, 0];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3081MegaLucarioEx, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.get_active(0).is_poisoned(),
        "Poison Barb must poison the attacker before its Knocked Out holder is removed"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        190,
        "the test stops before Pokémon Checkup; Poison has not dealt damage yet"
    );
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "the lethal damaging attack must remove Natu"
    );
    assert!(
        state.in_play_pokemon[1][1].is_some(),
        "the synthetic Bench keeps the knockout from becoming a terminal no-Pokémon state"
    );
    assert_eq!(state.points, [1, 0]);
    assert_eq!(state.winner, None);
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_id() == get_card_by_enum(CardId::B1097Natu).get_id()));
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_id() == get_card_by_enum(CardId::A3146PoisonBarb).get_id()));
}
