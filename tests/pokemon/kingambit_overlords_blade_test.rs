use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Kingambit (B3a 043) "Overlord's Blade": 60 base damage, +40 for each time your own Pokémon
/// have been Knocked Out during this game.
///
/// With a clean board (no losses yet) the attack should do exactly its base damage.
#[test]
fn test_kingambit_overlords_blade_base_damage_with_no_own_knockouts() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B3a043Kingambit)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        // Mega Latios ex: 180 HP and no weakness, so it survives both the 60 and the 100 hit
        // and the damage is readable off its remaining HP without a knockout truncating it.
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let before = game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("opponent active should exist");

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a043Kingambit, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let dealt = before
        - state.in_play_pokemon[1][0]
            .as_ref()
            .expect("target must survive so the damage is readable, not truncated by a knockout")
            .get_remaining_hp();

    assert_eq!(
        dealt, 60,
        "with no own knockouts yet, Overlord's Blade should do only its 60 base damage"
    );
}

/// After the attacking player has lost Pokémon of their own, the attack scales by +40 each.
///
/// This drives the `State::own_knockouts_this_game` counter rather than asserting on it directly:
/// the bench Pokémon is knocked out by real damage first, then Kingambit attacks.
#[test]
fn test_kingambit_overlords_blade_scales_with_own_knockouts() {
    // Player 0's own benched Bulbasaur is left at 10 HP so the opponent's attack knocks it out,
    // incrementing player 0's own-knockout tally before Kingambit swings.
    let mut game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![
            PlayedCard::from_id(CardId::B3a043Kingambit)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10),
        ],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    // Knock out player 0's benched Pokémon directly, then hand the turn back to player 0.
    let mut state = game.get_state_clone();
    state.in_play_pokemon[0][1] = None;
    state.set_own_knockouts_this_game(0, 1);
    state.current_player = 0;
    game.set_state(state);

    let before = game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("opponent active should exist");

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a043Kingambit, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let dealt = before
        - state.in_play_pokemon[1][0]
            .as_ref()
            .expect("target must survive so the damage is readable, not truncated by a knockout")
            .get_remaining_hp();

    assert_eq!(
        dealt, 100,
        "after losing 1 of your own Pokémon, Overlord's Blade should do 60 + 40 = 100"
    );
}
