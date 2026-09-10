use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Dugtrio (A4a 041) — Cliff Crumbler: "Discard the top card of your deck. If that card is a
/// [F] Pokémon, this attack does 60 more damage." Base damage is 40.
fn cliff_crumbler_remaining_hp(top_card: CardId) -> (u32, String) {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A4a041Dugtrio).with_energy(vec![EnergyType::Fighting])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards.insert(0, get_card_by_enum(top_card));
    state.discard_piles[0] = vec![];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a041Dugtrio, 0),
        is_stack: false,
    });
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(
        state.discard_piles[0].len(),
        1,
        "the top card of the deck is always discarded"
    );
    (
        state.get_active(1).get_remaining_hp(),
        state.discard_piles[0][0].get_name(),
    )
}

#[test]
fn test_cliff_crumbler_adds_damage_when_top_card_is_a_fighting_pokemon() {
    // Sandshrew (A1 137) is a [F] Pokémon → 40 + 60 = 100 damage.
    let (remaining_hp, discarded) = cliff_crumbler_remaining_hp(CardId::A1137Sandshrew);
    assert_eq!(discarded, "Sandshrew");
    assert_eq!(remaining_hp, 180 - 100);
}

#[test]
fn test_cliff_crumbler_does_not_add_damage_for_other_pokemon() {
    // Bulbasaur (A1 001) is a [G] Pokémon → only the printed 40 damage.
    let (remaining_hp, discarded) = cliff_crumbler_remaining_hp(CardId::A1001Bulbasaur);
    assert_eq!(discarded, "Bulbasaur");
    assert_eq!(remaining_hp, 180 - 40);
}

#[test]
fn test_cliff_crumbler_does_not_add_damage_for_trainer_cards() {
    let (remaining_hp, discarded) = cliff_crumbler_remaining_hp(CardId::A1219Erika);
    assert_eq!(discarded, "Erika");
    assert_eq!(remaining_hp, 180 - 40);
}

#[test]
fn test_cliff_crumbler_with_empty_deck_deals_base_damage() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A4a041Dugtrio).with_energy(vec![EnergyType::Fighting])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards.clear();
    state.discard_piles[0] = vec![];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a041Dugtrio, 0),
        is_stack: false,
    });
    game.play_until_stable();

    let state = game.get_state_clone();
    assert!(state.discard_piles[0].is_empty());
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 40);
}
