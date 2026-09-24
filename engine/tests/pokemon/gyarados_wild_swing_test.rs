use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// Gyarados (A4 045 / A4 215) "Wild Swing": 20 damage, and "You may discard any number of your
/// Benched [W] Pokémon. This attack does 40 more damage for each Benched Pokémon you discarded in
/// this way."
fn wild_swing_game(card_id: CardId, own_bench: Vec<CardId>) -> Game<'static> {
    let mut own_board =
        vec![PlayedCard::from_id(card_id).with_energy(vec![EnergyType::Water, EnergyType::Water])];
    own_board.extend(own_bench.into_iter().map(PlayedCard::from_id));

    let mut game = get_test_game_with_board(
        own_board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game
}

fn discard_count(action: &SimpleAction) -> usize {
    match action {
        SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } => in_play_idxs.len(),
        other => panic!("unexpected action {other}"),
    }
}

#[test]
fn test_wild_swing_offers_every_subset_of_your_water_bench() {
    let game = wild_swing_game(
        CardId::A4045Gyarados,
        vec![
            CardId::A1053Squirtle,
            CardId::A1001Bulbasaur,
            CardId::A1057Psyduck,
        ],
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    // Two eligible [W] Pokémon => discard 0, either one, or both.
    assert_eq!(choices.len(), 4);
    let mut sizes: Vec<usize> = choices
        .iter()
        .map(|choice| discard_count(&choice.action))
        .collect();
    sizes.sort_unstable();
    assert_eq!(sizes, vec![0, 1, 1, 2]);
}

#[test]
fn test_wild_swing_discards_the_chosen_pokemon_and_scales_the_damage() {
    let mut game = wild_swing_game(
        CardId::A4045Gyarados,
        vec![
            CardId::A1053Squirtle,
            CardId::A1001Bulbasaur,
            CardId::A1057Psyduck,
        ],
    );

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let discard_both = choices
        .iter()
        .find(|choice| discard_count(&choice.action) == 2)
        .expect("discarding both [W] Pokémon should be an option")
        .clone();
    game.apply_action(&discard_both);

    // The damage is queued as a follow-up so it runs through the normal damage pipeline.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(matches!(
        choices[0].action,
        SimpleAction::ApplyDamage { .. }
    ));
    game.apply_action(&choices[0].clone());

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        80,
        "20 + 2 x 40 = 100 damage to Mega Latios ex (180 HP, no Weakness)"
    );
    assert!(
        state.in_play_pokemon[0][1].is_none() && state.in_play_pokemon[0][3].is_none(),
        "both discarded [W] Pokémon should have left play"
    );
    assert_eq!(
        state.in_play_pokemon[0][2].as_ref().unwrap().get_name(),
        "Bulbasaur",
        "the non-[W] Benched Pokémon should be untouched"
    );
    for name in ["Squirtle", "Psyduck"] {
        assert!(
            state.discard_piles[0]
                .iter()
                .any(|card| card.get_name() == name),
            "{name} should be in the discard pile"
        );
    }
}

/// Choosing to discard nothing leaves the Bench alone and deals only the printed damage.
#[test]
fn test_wild_swing_can_discard_nothing() {
    let mut game = wild_swing_game(CardId::A4215Gyarados, vec![CardId::A1053Squirtle]);

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let discard_none = choices
        .iter()
        .find(|choice| discard_count(&choice.action) == 0)
        .expect("discarding nothing should be an option")
        .clone();
    game.apply_action(&discard_none);
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    game.apply_action(&choices[0].clone());

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        160,
        "20 damage only"
    );
    assert_eq!(
        state.in_play_pokemon[0][1].as_ref().unwrap().get_name(),
        "Squirtle"
    );
}

/// Negative case: with no Benched [W] Pokémon there is nothing to offer, so the attack resolves
/// immediately for its printed damage.
#[test]
fn test_wild_swing_without_a_water_bench_is_just_its_printed_damage() {
    let game = wild_swing_game(CardId::A4215Gyarados, vec![CardId::A1001Bulbasaur]);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 160);
    let (_, choices) = state.generate_possible_actions();
    assert!(!choices.iter().any(|choice| matches!(
        choice.action,
        SimpleAction::DiscardOwnBenchedThenDamage { .. }
    )));
}
