use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Rescue Scarf (A4 155): "If the Pokémon this card is attached to is Knocked Out by damage from
/// an attack from your opponent's Pokémon, put it into your hand instead of the discard pile."
///
/// The knockout itself still happens and the attacker still scores — only the destination of the
/// card changes.
#[test]
fn test_rescue_scarf_returns_the_knocked_out_pokemon_to_hand() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1095Raichu).with_energy(vec![
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Lightning,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::A1003Venusaur)
                .with_remaining_hp(10)
                .with_tool(get_card_by_enum(CardId::A4155RescueScarf)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let hand_before = game.get_state_clone().hands[1].len();

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1095Raichu, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "Rescue Scarf must not prevent the knockout"
    );
    assert_eq!(
        state.points[0], 1,
        "the attacker still scores the knockout point"
    );
    assert_eq!(
        state.hands[1].len(),
        hand_before + 1,
        "the knocked out Pokémon should be back in its owner's hand"
    );
    assert!(
        state.hands[1]
            .iter()
            .any(|card| card.get_name() == "Venusaur"),
        "specifically Venusaur should be the card returned"
    );
    assert!(
        state.discard_piles[1]
            .iter()
            .any(|card| card.get_name() == "Rescue Scarf"),
        "the scarf itself is still discarded"
    );
    assert!(
        !state.discard_piles[1]
            .iter()
            .any(|card| card.get_name() == "Venusaur"),
        "Venusaur must not also be in the discard pile"
    );
}

/// Beastite (A3a 066): "Attacks used by the Ultra Beast this card is attached to do +10 damage to
/// your opponent's Active Pokémon for each point you have gotten."
///
/// Nihilego is an Ultra Beast. With no points banked the tool is worth nothing; the bonus only
/// appears once the holder's owner is on the board.
fn nihilego_damage_with_points(points: u8) -> u32 {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A3a042Nihilego)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])
                .with_tool(get_card_by_enum(CardId::A3a066Beastite)),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            // 180 HP, no weakness — survives so the damage is readable.
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let mut state = game.get_state_clone();
    state.points[0] = points;
    game.set_state(state);

    let before = game.get_state_clone().in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("target should exist");

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3a042Nihilego, 0),
        is_stack: false,
    });

    before
        - game.get_state_clone().in_play_pokemon[1][0]
            .as_ref()
            .expect("target must survive so the damage is readable")
            .get_remaining_hp()
}

#[test]
fn test_beastite_scales_damage_with_points_scored() {
    let at_zero = nihilego_damage_with_points(0);
    let at_one = nihilego_damage_with_points(1);
    let at_two = nihilego_damage_with_points(2);

    assert_eq!(
        at_one,
        at_zero + 10,
        "Beastite should add +10 damage per point banked"
    );
    assert_eq!(
        at_two,
        at_zero + 20,
        "Beastite should add +20 damage at two points"
    );
}
