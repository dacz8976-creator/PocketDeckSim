use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Slowking (A4a 018) — Litter: "Discard up to 2 Pokémon Tool cards from your hand. This attack
/// does 50 damage for each card you discarded in this way."
fn litter_game(hand: &[CardId]) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A4a018Slowking).with_energy(vec![EnergyType::Water])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = hand.iter().copied().map(get_card_by_enum).collect();
    state.discard_piles[0] = vec![];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a018Slowking, 0),
        is_stack: false,
    });
    game
}

fn discard_choice_sizes(game: &Game<'static>) -> Vec<usize> {
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    actions
        .iter()
        .filter_map(|action| match &action.action {
            SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. } => Some(cards.len()),
            _ => None,
        })
        .collect()
}

fn pick_discard_of_size(game: &Game<'static>, size: usize) -> Action {
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    actions
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. }
                if cards.len() == size)
        })
        .unwrap_or_else(|| panic!("expected a Litter option discarding {size} tool(s)"))
}

#[test]
fn test_litter_deals_fifty_damage_per_discarded_tool() {
    let mut game = litter_game(&[
        CardId::A2147GiantCape,
        CardId::A2148RockyHelmet,
        CardId::A2b111PokeBall,
    ]);

    let mut sizes = discard_choice_sizes(&game);
    sizes.sort_unstable();
    sizes.dedup();
    assert_eq!(
        sizes,
        vec![0, 1, 2],
        "Litter must offer discarding 0, 1 or 2 Pokémon Tool cards"
    );

    let action = pick_discard_of_size(&game, 2);
    game.apply_action(&action);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180 - 100,
        "2 tools discarded → 2 × 50 damage"
    );
    assert_eq!(state.hands[0].len(), 1, "only the Item card should remain");
    assert_eq!(state.hands[0][0].get_name(), "Poké Ball");
    assert_eq!(state.discard_piles[0].len(), 2);
}

#[test]
fn test_litter_deals_no_damage_when_discarding_nothing() {
    let mut game = litter_game(&[CardId::A2147GiantCape, CardId::A2148RockyHelmet]);

    let action = pick_discard_of_size(&game, 0);
    game.apply_action(&action);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "discarding nothing deals no damage"
    );
    assert_eq!(state.hands[0].len(), 2);
    assert!(state.discard_piles[0].is_empty());
}

#[test]
fn test_litter_deals_fifty_damage_for_a_single_tool() {
    let mut game = litter_game(&[CardId::A2147GiantCape, CardId::A2b111PokeBall]);

    let mut sizes = discard_choice_sizes(&game);
    sizes.sort_unstable();
    sizes.dedup();
    assert_eq!(sizes, vec![0, 1], "only 1 Pokémon Tool card is available");

    let action = pick_discard_of_size(&game, 1);
    game.apply_action(&action);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50);
    assert_eq!(state.hands[0].len(), 1);
}

#[test]
fn test_litter_does_nothing_without_tools_in_hand() {
    let mut game = litter_game(&[CardId::A2b111PokeBall, CardId::A1219Erika]);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "no Pokémon Tool cards to discard → no damage"
    );
    assert_eq!(state.hands[0].len(), 2);
    assert!(state.discard_piles[0].is_empty());
}
