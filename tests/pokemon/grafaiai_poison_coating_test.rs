use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::PlayedCard,
    test_support::{get_initialized_game_with_board, get_test_game_with_board},
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

/// Grafaiai's Poison Coating: "Once during your turn, you may flip a coin. If heads, your
/// opponent's Active Pokémon is now Poisoned."
///
/// The coin is a real branch in the forecast (`Outcomes::binary_coin`), so sweeping seeds must
/// show both outcomes: on heads the opponent's Active is Poisoned, on tails nothing happens.
#[test]
fn test_poison_coating_poisons_opponent_active_on_heads() {
    let mut saw_poisoned = false;
    let mut saw_no_poison = false;

    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A2b051Grafaiai)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );

        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseAbility { in_play_idx: 0 },
            is_stack: false,
        });

        if game.get_state_clone().get_active(1).is_poisoned() {
            saw_poisoned = true;
        } else {
            saw_no_poison = true;
        }
    }

    assert!(
        saw_poisoned,
        "expected at least one seed where Poison Coating flipped heads and Poisoned the opponent"
    );
    assert!(
        saw_no_poison,
        "expected at least one seed where Poison Coating flipped tails and did nothing"
    );
}

/// A2b 076 is the same card at a different rarity.
#[test]
fn test_poison_coating_full_art_shares_the_ability() {
    let mut saw_poisoned = false;

    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A2b076Grafaiai)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseAbility { in_play_idx: 0 },
            is_stack: false,
        });
        if game.get_state_clone().get_active(1).is_poisoned() {
            saw_poisoned = true;
            break;
        }
    }

    assert!(saw_poisoned, "A2b 076 Grafaiai should share Poison Coating");
}

/// NEGATIVE: "Once during your turn" — the ability is not offered again after it has been used,
/// regardless of how the coin landed.
#[test]
fn test_poison_coating_is_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2b051Grafaiai)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let ability_action =
        use_ability_action(&actions, 0).expect("Poison Coating should be available");
    game.apply_action(&ability_action);

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Poison Coating should not be usable twice in the same turn"
    );
}

/// Poison Coating has no "in the Active Spot" clause, so a benched Grafaiai can use it too.
#[test]
fn test_poison_coating_is_usable_from_the_bench() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A2b051Grafaiai),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 1).is_some(),
        "Poison Coating should be offered from the Bench"
    );
}
