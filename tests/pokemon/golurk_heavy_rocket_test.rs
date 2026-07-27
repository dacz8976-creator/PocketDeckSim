use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Golurk (B1 136) — Heavy Rocket: "Reveal the top 3 cards of your deck. This attack does 60
/// damage for each Pokémon with a Retreat Cost of 3 or more you find there. Shuffle the revealed
/// cards back into your deck."
fn heavy_rocket_remaining_hp(top_three: &[CardId]) -> (u32, usize, usize) {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B1136Golurk)
            .with_energy(vec![EnergyType::Fighting, EnergyType::Fighting])],
        // 400 HP sponge so three heavy Pokémon (180 damage) never knock the defender out.
        vec![PlayedCard::new(
            get_card_by_enum(CardId::PB024MegaLatiosEx),
            0,
            400,
            vec![],
            false,
            vec![],
        )],
    );
    let mut state = game.get_state_clone();
    for (offset, card_id) in top_three.iter().enumerate() {
        state.decks[0]
            .cards
            .insert(offset, get_card_by_enum(*card_id));
    }
    state.discard_piles[0] = vec![];
    let deck_len_before = state.decks[0].cards.len();
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1136Golurk, 0),
        is_stack: false,
    });
    game.play_until_stable();

    let state = game.get_state_clone();
    (
        state.get_active(1).get_remaining_hp(),
        state.decks[0].cards.len(),
        deck_len_before,
    )
}

#[test]
fn test_heavy_rocket_counts_pokemon_with_retreat_cost_three_or_more() {
    // Venusaur (A1 003) and Exeggutor (A1 022) both have Retreat Cost 3; Starmie (A1 075) has 0.
    let (remaining_hp, deck_after, deck_before) = heavy_rocket_remaining_hp(&[
        CardId::A1003Venusaur,
        CardId::A1022Exeggutor,
        CardId::A1075Starmie,
    ]);
    assert_eq!(remaining_hp, 400 - 120, "2 heavy Pokémon → 2 × 60 damage");
    assert_eq!(
        deck_after, deck_before,
        "revealed cards are shuffled back, so the deck keeps its size"
    );
}

#[test]
fn test_heavy_rocket_does_nothing_when_no_heavy_pokemon_are_revealed() {
    // Starmie has Retreat Cost 0 and Erika is a Trainer (no Retreat Cost at all).
    let (remaining_hp, deck_after, deck_before) = heavy_rocket_remaining_hp(&[
        CardId::A1075Starmie,
        CardId::A1219Erika,
        CardId::A1075Starmie,
    ]);
    assert_eq!(
        remaining_hp, 400,
        "no Pokémon with Retreat Cost >= 3 → the attack does no damage"
    );
    assert_eq!(deck_after, deck_before);
}

#[test]
fn test_heavy_rocket_scales_to_three_heavy_pokemon() {
    let (remaining_hp, _, _) = heavy_rocket_remaining_hp(&[
        CardId::A1003Venusaur,
        CardId::A1003Venusaur,
        CardId::A1022Exeggutor,
    ]);
    assert_eq!(remaining_hp, 400 - 180, "3 heavy Pokémon → 3 × 60 damage");
}
